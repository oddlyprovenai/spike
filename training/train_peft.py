"""Train one SPIKE adapter on an NVIDIA GPU (Colab) with PyTorch + PEFT: the GPU twin of training/train.sh (mlx-lm).

    python training/prepare.py training/configs/<id>.yaml        # the same prepared files as on the Mac
    python training/train_peft.py <id> [--model Qwen/Qwen3.5-4B] [--revision <sha>] [--stop-after N]
    SPIKE_RESUME=1 python training/train_peft.py <id>              # continue from the latest complete checkpoint

Reads training/data/<id>/{mlx_lora.yaml, train.jsonl, valid.jsonl, manifest.json} and writes training/runs/<id>/
{adapter/, train.log, run.json} in the same formats as the mlx backend (spike_train/peft_backend.py says which), so
sweep_checkpoints.py, export_adapter.py and the acceptance gate run unchanged. Same recipe: LoRA rank, scale
(PEFT alpha = scale x rank), dropout and target modules, prompt masking, max_seq_length, batch size, gradient
accumulation, learning rate and schedule, iterations, save and validation cadence, seed.

Not the same numbers as mlx-lm, and not claimed to be: kernels and bf16 arithmetic differ, the optimizer is torch Adam
(with bias correction; mlx's Adam has none by default) and the data order is this script's own seeded order. A run
is compared to an mlx run by its evaluation, never by its loss curve.

Exact resume: every checkpoint also writes <adapter>/resume/<iteration>/ with the LoRA weights, the optimizer and
scheduler state, every RNG state and the data position; resume.json (written last) records the hashes of train.jsonl
and the config and the package versions, and a mismatch refuses to resume. Without SPIKE_RESUME a fresh run moves
older checkpoints aside (resume.old), as the mlx backend does. `--stop-after N` ends the run after iteration N as an
interruption would (a smoke run that measures speed and memory, or a resume test): it exits 3 and run.json says so, so
the sweep never takes its adapters.safetensors for the final one.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import shutil
import subprocess
import sys
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "training"))

from spike_train import peft_backend as pb  # noqa: E402

KEEP = 2  # complete resume checkpoints kept, as in spike_train/resume.py
RESUME_FILES = ("adapters.safetensors", "optimizer.pt", "rng.pt")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def v(pkg: str) -> str | None:
    try:
        return version(pkg)
    except PackageNotFoundError:
        return None


def kernels() -> dict[str, str | None]:
    """The optional CUDA kernels transformers uses for Qwen3.5's linear-attention layers when installed (otherwise its
    reference PyTorch code): they change speed and, slightly, the numbers, so a run records them and a resume needs
    the same ones."""
    return {"flash_linear_attention": v("flash-linear-attention"), "causal_conv1d": v("causal-conv1d")}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def token_ids(out) -> list[int]:
    """apply_chat_template's token ids, whether it returns a list or (transformers 5) a BatchEncoding."""
    ids = out["input_ids"] if not isinstance(out, list) else out
    return list(ids[0] if ids and isinstance(ids[0], list) else ids)


def encode(tokenizer, row: dict, max_len: int | None) -> tuple[list[int], int]:
    """(token ids, first trained token): the chat through the model's own template; the loss covers only the last
    message (the assistant's answer), the rest is the prompt, as mlx-lm's mask_prompt does for chat data."""
    messages, tools = row["messages"], row.get("tools")
    if messages[-1].get("role") != "assistant":
        raise ValueError("a training chat must end with the assistant's answer")
    full = token_ids(tokenizer.apply_chat_template(messages, tools=tools, tokenize=True))
    prompt = token_ids(tokenizer.apply_chat_template(messages[:-1], tools=tools, tokenize=True,
                                                     add_generation_prompt=True))
    if full[:len(prompt)] != prompt:  # mlx-lm uses the prompt's length all the same; count it so it is visible
        encode.not_prefix = getattr(encode, "not_prefix", 0) + 1
    start, length = pb.prompt_mask(len(prompt), len(full), max_len)
    return full[:length], start


def checkpoint_names(model_id: str, revision: str | None) -> set[str]:
    """The tensor names of the base checkpoint's own files. They decide the mlx-lm names of the adapter: transformers
    loads Qwen3.5's vision-language checkpoint as a text model whose modules are `model.layers.N`, but its tensors are
    `model.language_model.layers.N`, which mlx-lm calls `language_model.model.layers.N` (and export_adapter.py checks)."""
    from spike_train.export import load_base_weight_names

    if Path(model_id).is_dir():
        return load_base_weight_names(Path(model_id))
    from huggingface_hub import hf_hub_download
    from huggingface_hub.errors import EntryNotFoundError

    try:
        index = hf_hub_download(model_id, "model.safetensors.index.json", revision=revision)
        return set(json.loads(Path(index).read_text(encoding="utf-8"))["weight_map"])
    except EntryNotFoundError:
        return load_base_weight_names(Path(hf_hub_download(model_id, "model.safetensors", revision=revision)).parent)


def hub_commit(model_id: str, revision: str | None) -> str | None:
    """The Hub commit the base weights were read from (the snapshot folder of the cached config.json), None for a local
    folder. transformers 5 no longer sets config._commit_hash, so run.json recorded null without --revision."""
    if Path(model_id).is_dir():
        return None
    from huggingface_hub import hf_hub_download

    snapshot = Path(hf_hub_download(model_id, "config.json", revision=revision)).parent
    return snapshot.name if snapshot.parent.name == "snapshots" else None


class Trainer:
    def __init__(self, args, cfg: dict, data_dir: Path, run_dir: Path):
        import torch

        self.torch, self.args, self.cfg = torch, args, cfg
        self.data_dir, self.run_dir = data_dir, run_dir
        self.adapter_dir = run_dir / "adapter"
        self.lp = cfg["lora_parameters"]
        self.rank = int(self.lp["rank"])
        self.iters = int(cfg["iters"])
        self.stop_after = int(args.stop_after) if args.stop_after else None
        self.batch = int(cfg.get("batch_size", 1))
        self.accum = int(cfg.get("grad_accumulation_steps", 1))
        self.save_every = int(cfg.get("save_every", 100))
        self.eval_every = int(cfg.get("steps_per_eval", 200))
        self.report_every = int(cfg.get("steps_per_report", 10))
        self.val_batches = int(cfg.get("val_batches", 25))
        self.seed = int(cfg.get("seed", 0))
        self.base = {"model": None, "revision": args.revision, "commit": None}
        self.device = torch.device(args.device or ("cuda" if torch.cuda.is_available() else "cpu"))

    # ---------------------------------------------------------------- model
    def load(self) -> None:
        torch = self.torch
        from peft import LoraConfig, get_peft_model
        from transformers import AutoModelForCausalLM, AutoTokenizer

        torch.manual_seed(self.seed)  # the LoRA initialisation is part of the run: seeded by the recipe
        np.random.seed(self.seed)
        random.seed(self.seed)
        model_id = self.args.model or self.cfg["model"]
        kw = {"revision": self.args.revision} if self.args.revision else {}
        dtype = torch.bfloat16 if self.device.type == "cuda" else torch.float32
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, **kw)
        try:
            model = AutoModelForCausalLM.from_pretrained(model_id, dtype=dtype, **kw)
        except ValueError:  # a vision-language checkpoint (Qwen3.5) that AutoModelForCausalLM does not map
            from transformers import AutoModelForImageTextToText

            model = AutoModelForImageTextToText.from_pretrained(model_id, dtype=dtype, **kw)
        self.prefix = pb.mlx_prefix(checkpoint_names(model_id, self.args.revision))
        # the Hub commit the weights came from (None for a local folder): recorded in run.json and resume.json
        self.base.update(model=model_id, commit=hub_commit(model_id, self.args.revision)
                         or getattr(model.config, "_commit_hash", None))
        if self.cfg.get("num_layers", -1) not in (-1, None):
            raise SystemExit("num_layers other than -1 (all layers) is not supported by the GPU backend")
        lcfg = LoraConfig(r=self.rank, lora_alpha=float(self.lp["scale"]) * self.rank,
                          lora_dropout=float(self.lp.get("dropout", 0.0)), bias="none",
                          target_modules=pb.target_regex(self.lp["keys"]), task_type="CAUSAL_LM")
        if self.cfg.get("grad_checkpoint"):
            model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
            model.enable_input_require_grads()
        model.config.use_cache = False
        self.model = get_peft_model(model, lcfg).to(self.device)
        self.lora = {n: p for n, p in self.model.named_parameters() if p.requires_grad}
        modules = {pb.peft_module(n)[0] for n in self.lora}
        if not modules:
            raise SystemExit(f"no module of {model_id} matches the recipe's keys {self.lp['keys']}")
        self.modules = sorted(modules)
        self.optimizer = torch.optim.Adam(self.lora.values(), lr=float(self.cfg["learning_rate"]))
        print(f"spike-peft: {model_id} on {self.device} ({dtype}); LoRA r={self.rank} alpha={lcfg.lora_alpha} "
              f"on {len(self.modules)} modules; mlx names under '{self.prefix}'", flush=True)

    def data(self) -> None:
        max_len = self.cfg.get("max_seq_length")
        self.train = [encode(self.tokenizer, r, max_len) for r in read_jsonl(self.data_dir / "train.jsonl")]
        valid = self.data_dir / "valid.jsonl"
        self.valid = [encode(self.tokenizer, r, max_len) for r in read_jsonl(valid)] if valid.is_file() else []
        self.per_epoch = len(self.train) // self.batch
        if getattr(encode, "not_prefix", 0):
            print(f"spike-peft: warning: in {encode.not_prefix} chats the template renders the prompt differently from "
                  f"the start of the whole chat; the loss starts at the prompt's length, as in mlx-lm", flush=True)
        if self.per_epoch == 0:
            raise SystemExit("fewer training chats than one batch")

    # ---------------------------------------------------------------- steps
    def collate(self, items: list[tuple[list[int], int]]):
        torch = self.torch
        pad = self.tokenizer.pad_token_id if self.tokenizer.pad_token_id is not None else 0
        width = max(len(ids) for ids, _ in items)
        ids = torch.full((len(items), width), pad, dtype=torch.long)
        labels = torch.full((len(items), width), -100, dtype=torch.long)
        mask = torch.zeros((len(items), width), dtype=torch.long)
        for i, (seq, start) in enumerate(items):
            ids[i, :len(seq)] = torch.tensor(seq)
            labels[i, start:len(seq)] = torch.tensor(seq[start:])
            mask[i, :len(seq)] = 1
        return ids.to(self.device), labels.to(self.device), mask.to(self.device)

    def loss(self, items):
        """Mean cross entropy over the answer tokens of the batch (mlx-lm's default_loss), and their count."""
        torch = self.torch
        ids, labels, mask = self.collate(items)
        logits = self.model(input_ids=ids, attention_mask=mask).logits[:, :-1].float()
        target = labels[:, 1:]
        n = int((target != -100).sum())
        loss = torch.nn.functional.cross_entropy(logits.reshape(-1, logits.size(-1)), target.reshape(-1),
                                                 ignore_index=-100, reduction="sum") / max(1, n)
        return loss, n

    def batch_at(self, it: int) -> list[tuple[list[int], int]]:
        """The batch of iteration `it` (1-based): epoch (it-1) // per_epoch, position within it."""
        epoch, pos = divmod(it - 1, self.per_epoch)
        if getattr(self, "_epoch", None) != epoch:
            self._epoch, self._order = epoch, pb.epoch_order(len(self.train), self.seed, epoch, self.batch)
        return [self.train[i] for i in self._order[pos]]

    def validate(self) -> float | None:
        if not self.valid:
            return None
        torch = self.torch
        self.model.eval()
        total, count = 0.0, 0
        with torch.no_grad():
            for k in range(min(self.val_batches, len(self.valid) // self.batch) if self.val_batches > 0 else
                           len(self.valid) // self.batch):
                loss, n = self.loss(self.valid[k * self.batch:(k + 1) * self.batch])
                total, count = total + float(loss) * n, count + n
        self.model.train()
        return total / max(1, count)

    # ---------------------------------------------------------------- files
    def mlx_tensors(self) -> dict[str, np.ndarray]:
        return pb.to_mlx({n: p.detach().float().cpu().numpy() for n, p in self.lora.items()}, self.prefix, self.rank)

    def write_adapter(self, path: Path) -> None:
        from spike_train.export import write_safetensors

        tmp = path.with_name(path.name + ".tmp")
        write_safetensors(tmp, self.mlx_tensors())
        tmp.replace(path)

    def save_resume(self, it: int, tokens: int, identity: dict) -> None:
        torch = self.torch
        root = self.adapter_dir / "resume"
        root.mkdir(parents=True, exist_ok=True)
        final, tmp = root / f"{it:07d}", root / f"{it:07d}.tmp"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir()
        self.write_adapter(tmp / RESUME_FILES[0])
        torch.save({"optimizer": self.optimizer.state_dict()}, tmp / RESUME_FILES[1])
        rng = {"torch": torch.get_rng_state(), "numpy": np.random.get_state(), "python": random.getstate()}
        if torch.cuda.is_available():
            rng["cuda"] = torch.cuda.get_rng_state_all()
        torch.save(rng, tmp / RESUME_FILES[2])
        epoch, position = divmod(it, self.per_epoch)
        meta = {**identity, "format": 1, "backend": "peft", "iteration": it, "optimizer_step": it // self.accum,
                "epoch": epoch, "position": position, "batches_per_epoch": self.per_epoch,
                "data_order": "peft_backend.epoch_order(n, seed, epoch, batch_size)", "trained_tokens": tokens,
                "saved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "files": {n: sha256(tmp / n) for n in RESUME_FILES}}
        (tmp / "resume.json.tmp").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        (tmp / "resume.json.tmp").replace(tmp / "resume.json")
        shutil.rmtree(final, ignore_errors=True)
        tmp.rename(final)
        for old in sorted(p for p in root.glob("*") if p.is_dir() and not p.name.endswith(".tmp"))[:-KEEP]:
            shutil.rmtree(old, ignore_errors=True)

    def latest_resume(self):
        root = self.adapter_dir / "resume"
        for d in sorted((p for p in root.glob("*") if p.is_dir() and not p.name.endswith(".tmp")), reverse=True):
            try:
                meta = json.loads((d / "resume.json").read_text(encoding="utf-8"))
                if set(meta["files"]) == set(RESUME_FILES) and all(sha256(d / n) == h for n, h in meta["files"].items()):
                    return d, meta
            except (OSError, ValueError, KeyError):
                pass
            print(f"spike-peft: ignoring incomplete checkpoint {d}", flush=True)
        return None

    def begin(self, resume: bool, identity: dict) -> tuple[int, int]:
        """(iteration, trained tokens) to continue from: 0 for a fresh run, else the latest complete checkpoint."""
        torch = self.torch
        root = self.adapter_dir / "resume"
        for stale in root.glob("*.tmp"):
            shutil.rmtree(stale, ignore_errors=True)
        if not resume:
            if root.is_dir() and any(root.glob("*")):
                shutil.rmtree(root.with_name("resume.old"), ignore_errors=True)
                root.rename(root.with_name("resume.old"))
                print(f"spike-peft: not resuming; moved the old checkpoints to {root.with_name('resume.old')}", flush=True)
            return 0, 0
        found = self.latest_resume()
        if not found:
            print(f"spike-peft: no complete checkpoint in {root}; starting at iteration 0", flush=True)
            return 0, 0
        d, meta = found
        changed = [f"{k}: {str(meta.get(k))[:16]} -> {str(val)[:16]}" for k, val in identity.items() if meta.get(k) != val]
        if changed:
            raise SystemExit(f"spike-peft: refusing to resume {d}: it was written by a different run "
                             f"({'; '.join(changed)}). Restore the original files, or delete {root} to train from scratch.")
        from spike_train.export import read_safetensors

        saved = pb.from_mlx(read_safetensors(d / RESUME_FILES[0]))
        mine = {}
        for n, p in self.lora.items():
            module, ab = pb.peft_module(n)
            mine[(pb.mlx_key(module, self.prefix), ab)] = p
        if saved.keys() != mine.keys():
            raise SystemExit(f"spike-peft: {d} does not match the model's LoRA parameters")
        with torch.no_grad():
            for key, p in mine.items():
                p.copy_(torch.from_numpy(saved[key]).to(p.dtype))
        self.optimizer.load_state_dict(torch.load(d / RESUME_FILES[1], weights_only=False)["optimizer"])
        rng = torch.load(d / RESUME_FILES[2], weights_only=False)
        torch.set_rng_state(rng["torch"])
        np.random.set_state(rng["numpy"])
        random.setstate(rng["python"])
        if "cuda" in rng and torch.cuda.is_available():
            torch.cuda.set_rng_state_all(rng["cuda"])
        print(f"spike-peft: resumed from {d.name}: iteration {meta['iteration']}, optimizer step "
              f"{meta['optimizer_step']}", flush=True)
        return meta["iteration"], meta["trained_tokens"]

    # ---------------------------------------------------------------- loop
    def run(self, resume: bool) -> bool:
        """Train; False when --stop-after ended the run before its planned iterations."""
        torch = self.torch
        self.adapter_dir.mkdir(parents=True, exist_ok=True)
        (self.adapter_dir / "adapter_config.json").write_text(
            json.dumps(dict(pb.adapter_config(self.cfg), iters=self.iters), indent=4), encoding="utf-8")
        identity = {"train_jsonl_sha256": sha256(self.data_dir / "train.jsonl"),
                    "config_sha256": sha256(self.data_dir / "mlx_lora.yaml"), "torch": v("torch"),
                    "transformers": v("transformers"), "peft": v("peft"), **kernels(), "seed": self.seed,
                    "batch_size": self.batch,
                    "grad_accumulation_steps": self.accum, "iters": self.iters, "base_model": self.base}
        start, tokens = self.begin(resume, identity)
        self.model.train()
        tic, window_loss, window_n = time.time(), 0.0, 0
        sched = self.cfg.get("lr_schedule")
        for group in self.optimizer.param_groups:  # the rate of the next update, so reports before it show the schedule's
            group["lr"] = pb.lr_at(start // self.accum, float(self.cfg["learning_rate"]), sched)
        if start == 0 and (val := self.validate()) is not None:
            print(f"Iter 1: Val loss {val:.3f}", flush=True)
        for it in range(start + 1, self.iters + 1):
            loss, n = self.loss(self.batch_at(it))
            (loss / self.accum).backward()
            window_loss, window_n, tokens = window_loss + float(loss.detach()) * n, window_n + n, tokens + n
            if it % self.accum == 0:
                update = it // self.accum - 1
                for group in self.optimizer.param_groups:
                    group["lr"] = pb.lr_at(update, float(self.cfg["learning_rate"]), sched)
                self.optimizer.step()
                self.optimizer.zero_grad(set_to_none=True)
            if it % self.report_every == 0 or it == self.iters:
                took = max(1e-9, time.time() - tic)
                mem = (f", Peak mem {torch.cuda.max_memory_allocated() / 2**30:.3f} GB"
                       if torch.cuda.is_available() else "")
                print(f"Iter {it}: Train loss {window_loss / max(1, window_n):.3f}, Learning Rate "
                      f"{self.optimizer.param_groups[0]['lr']:.3e}, It/sec {self.report_every / took:.3f}, "
                      f"Tokens/sec {window_n / took:.1f}, Trained Tokens {tokens}{mem}", flush=True)
                tic, window_loss, window_n = time.time(), 0.0, 0
            if (it % self.eval_every == 0 or it == self.iters) and (val := self.validate()) is not None:
                print(f"Iter {it}: Val loss {val:.3f}", flush=True)
            if it % self.save_every == 0:
                self.write_adapter(self.adapter_dir / "adapters.safetensors")
                self.write_adapter(self.adapter_dir / f"{it:07d}_adapters.safetensors")
                print(f"Iter {it}: Saved adapter weights to {self.adapter_dir / 'adapters.safetensors'} and "
                      f"{self.adapter_dir / f'{it:07d}_adapters.safetensors'}.", flush=True)
            if pb.is_save_point(it, self.accum, self.save_every) or it == self.iters:
                self.save_resume(it, tokens, identity)
            if it == self.stop_after and it < self.iters:
                if it % self.accum == 0 and not pb.is_save_point(it, self.accum, self.save_every):
                    self.save_resume(it, tokens, identity)  # resumable from here (an optimizer-update boundary)
                print(f"spike-peft: stopped after iteration {it} of {self.iters} (--stop-after)", flush=True)
                return False
        self.write_adapter(self.adapter_dir / "adapters.safetensors")
        print(f"Saved final weights to {self.adapter_dir / 'adapters.safetensors'}.", flush=True)
        return True


def write_run_json(run_dir: Path, data_dir: Path, started: str, run_started: str | None, status: int,
                   device: str | None, stopped_after: int | None = None, base_model: dict | None = None) -> None:
    """run.json as train.sh writes it, with the GPU and the PyTorch stack in place of the Mac's chip and mlx."""
    def sh(*cmd):
        try:
            return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT).stdout.strip() or None
        except OSError:
            return None

    manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
    gpu, gpu_mem = None, None
    try:
        import torch

        if torch.cuda.is_available():
            gpu, gpu_mem = torch.cuda.get_device_name(0), torch.cuda.get_device_properties(0).total_memory
    except ImportError:
        pass
    record = {"specialist": manifest["specialist"], "started_utc": started, "run_started_utc": run_started,
              "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "exit_code": status,
              "spike_resume": os.environ.get("SPIKE_RESUME") or None, "stopped_after": stopped_after,
              "data_files_sha256": manifest["files"], "counts": manifest["counts"],
              "git_commit": sh("git", "rev-parse", "HEAD"), "base_model": base_model, "backend": "peft", "device": device,
              "gpu": gpu,
              "gpu_memory_bytes": gpu_mem, "os": platform.platform(), "python": platform.python_version(),
              "torch": v("torch"), "transformers": v("transformers"), "peft": v("peft"), **kernels()}
    (run_dir / "run.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"wrote {run_dir / 'run.json'} (exit {status})", flush=True)


class Tee:
    def __init__(self, path: Path, append: bool):
        self.file = open(path, "a" if append else "w", encoding="utf-8")  # noqa: SIM115 (open for the whole run)
        self.out = sys.stdout

    def write(self, s):
        self.out.write(s)
        self.file.write(s)

    def flush(self):
        self.out.flush()
        self.file.flush()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("specialist")
    ap.add_argument("--data", type=Path, help="prepared data folder (default training/data/<id>)")
    ap.add_argument("--run", type=Path, help="run folder (default training/runs/<id>)")
    ap.add_argument("--model", help="base model: a Hub id or a local folder (default: mlx_lora.yaml's model)")
    ap.add_argument("--revision", help="the Hub revision (commit) of the base model")
    ap.add_argument("--stop-after", type=int, help="end after iteration N as an interruption would (exit 3)")
    ap.add_argument("--device", help="cuda or cpu (default: cuda when available)")
    args = ap.parse_args(argv)
    data_dir = args.data or ROOT / "training" / "data" / args.specialist
    run_dir = args.run or ROOT / "training" / "runs" / args.specialist
    cfg_path = data_dir / "mlx_lora.yaml"
    if not cfg_path.is_file():
        raise SystemExit(f"missing {cfg_path}; run: python training/prepare.py training/configs/{args.specialist}.yaml")
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    if cfg.get("fine_tune_type", "lora") != "lora":
        raise SystemExit("only fine_tune_type lora is supported")
    resume = os.environ.get("SPIKE_RESUME", "").lower() in ("1", "true", "yes")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "adapter").mkdir(exist_ok=True)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    marker = run_dir / "adapter" / "run_started_utc"
    if not resume or not any((run_dir / "adapter" / "resume").glob("*/resume.json")):
        marker.write_text(started + "\n", encoding="utf-8")
    run_started = marker.read_text(encoding="utf-8").strip() if marker.is_file() else None
    log = Tee(run_dir / "train.log", append=resume)
    sys.stdout = log
    if resume:
        print(f"--- {started} SPIKE_RESUME={os.environ.get('SPIKE_RESUME')} ---", flush=True)
    trainer = Trainer(args, cfg, data_dir, run_dir)
    status, stopped = 1, None
    try:
        trainer.load()
        trainer.data()
        finished = trainer.run(resume)
        status, stopped = (0, None) if finished else (3, trainer.stop_after)
    finally:
        sys.stdout = log.out
        log.file.close()
        write_run_json(run_dir, data_dir, started, run_started, status, str(trainer.device), stopped, trainer.base)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
