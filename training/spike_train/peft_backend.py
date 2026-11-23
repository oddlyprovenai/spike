"""The parts of the GPU training backend (training/train_peft.py) that need no torch, so they are tested everywhere.

The backend trains from the same prepared files and recipe as the mlx one (training/lora.py) and writes what the rest
of the pipeline reads (sweep_checkpoints.py, export_adapter.py, the acceptance gate), so nothing downstream changes:

- `<adapter_path>/<iteration:07d>_adapters.safetensors` every `save_every` iterations and `adapters.safetensors` at the
  end, with mlx-lm's tensor names and shapes: `<prefix>layers.N.<module>.lora_a` of shape (in, r) and `.lora_b` of
  shape (r, out), the transposes of PEFT's `lora_A.weight` (r, in) and `lora_B.weight` (out, r);
- `<adapter_path>/adapter_config.json` with mlx-lm's `lora_parameters` (rank, scale, dropout, keys), so
  export_adapter.py writes PEFT `lora_alpha = scale * rank`, exactly as for an mlx run.

Counting follows mlx-lm: `iters` are micro-batches, the optimizer steps once every `grad_accumulation_steps` of them,
and the learning-rate schedule (linear warmup from 0, then cosine decay) is indexed by optimizer updates.
"""

from __future__ import annotations

import math
import re

import numpy as np

# The recipe's keys (mlx-lm module paths under each decoder layer) and the decoder layers of both layouts: a plain
# causal LM (`model.layers.N`) and Qwen3.5's vision-language wrapper (`model.language_model.layers.N`). The vision
# tower (`model.visual...`) never matches, and in Qwen3.5 only the 8 full-attention layers have `self_attn.*`.
LAYER = re.compile(r"^(?P<base>model\.(?:language_model\.)?)layers\.(?P<n>\d+)\.(?P<module>.+)$")


def target_regex(keys: list[str]) -> str:
    """A PEFT `target_modules` regex (matched against whole module names) for the recipe's keys."""
    alts = "|".join(re.escape(k) for k in keys)
    return rf"^model\.(?:language_model\.)?layers\.\d+\.(?:{alts})$"


def mlx_prefix(base_weight_names: set[str] | list[str]) -> str:
    """mlx-lm's name for the decoder of this checkpoint: Qwen3.5's VLM wrapper is `language_model.model.` in mlx-lm
    (and `model.language_model.` on the Hub); a plain causal LM is `model.` in both. export.DEFAULT_PREFIX_MAP maps
    them back."""
    return "language_model.model." if any(n.startswith("model.language_model.") for n in base_weight_names) else "model."


def mlx_key(module: str, prefix: str) -> str:
    """`model.language_model.layers.3.self_attn.q_proj` -> `<prefix>layers.3.self_attn.q_proj`."""
    m = LAYER.match(module)
    if not m:
        raise ValueError(f"'{module}' is not a decoder-layer module")
    return f"{prefix}layers.{m['n']}.{m['module']}"


def peft_module(name: str) -> str | None:
    """The module a PEFT parameter belongs to, without PEFT's wrappers (None for parameters that are not LoRA's):
    `base_model.model.model.layers.0.mlp.up_proj.lora_A.default.weight` -> (`model.layers.0.mlp.up_proj`, `A`)."""
    m = re.match(r"^(?:base_model\.model\.)?(?P<module>.+)\.lora_(?P<ab>[AB])\.(?:[^.]+\.)?weight$", name)
    return (m["module"], m["ab"]) if m else None


def to_mlx(named: dict[str, np.ndarray], prefix: str, rank: int) -> dict[str, np.ndarray]:
    """PEFT LoRA weights (lora_A (r, in), lora_B (out, r)) as mlx-lm adapter tensors (lora_a (in, r), lora_b (r, out))."""
    out: dict[str, np.ndarray] = {}
    for name, value in named.items():
        found = peft_module(name)
        if found is None:
            continue
        module, ab = found
        key = mlx_key(module, prefix) + (".lora_a" if ab == "A" else ".lora_b")
        arr = np.ascontiguousarray(np.asarray(value, dtype=np.float32).T)
        want = (arr.shape[1] == rank) if ab == "A" else (arr.shape[0] == rank)
        if arr.ndim != 2 or not want:
            raise ValueError(f"{name}: shape {value.shape} is not a rank-{rank} LoRA {ab} matrix")
        out[key] = arr
    if not out:
        raise ValueError("no LoRA weights found")
    return out


def from_mlx(tensors: dict[str, np.ndarray]) -> dict[tuple[str, str], np.ndarray]:
    """mlx-lm adapter tensors back to PEFT orientation, keyed by (mlx module path, 'A' | 'B'): for exact resume."""
    out = {}
    for key, value in tensors.items():
        m = re.match(r"^(?P<module>.+)\.lora_(?P<ab>[ab])$", key)
        if not m:
            raise ValueError(f"unexpected adapter tensor {key}")
        out[(m["module"], m["ab"].upper())] = np.ascontiguousarray(np.asarray(value).T)
    return out


def adapter_config(mlx_cfg: dict) -> dict:
    """adapter_config.json as mlx-lm writes it (its merged run arguments), plus which backend wrote the files."""
    keep = ("model", "fine_tune_type", "num_layers", "lora_parameters", "iters", "batch_size", "grad_accumulation_steps",
            "learning_rate", "lr_schedule", "max_seq_length", "mask_prompt", "grad_checkpoint", "seed", "data",
            "adapter_path", "save_every", "steps_per_eval", "steps_per_report", "val_batches")
    cfg = {k: mlx_cfg[k] for k in keep if k in mlx_cfg}
    cfg["backend"] = "peft"
    return cfg


def lr_at(update: int, learning_rate: float, schedule: dict | None) -> float:
    """The learning rate of optimizer update `update` (0-based), as mlx-lm builds it from the recipe: constant without a
    schedule; with one, a linear warmup from 0 over `warmup` updates joined to `cosine_decay(init, decay_steps, end)`."""
    if not schedule:
        return float(learning_rate)
    if schedule.get("name") != "cosine_decay":
        raise ValueError(f"lr_schedule '{schedule.get('name')}' is not supported by the GPU backend (only cosine_decay)")
    init, decay_steps, *rest = schedule["arguments"]
    end = float(rest[0]) if rest else 0.0
    if decay_steps == "auto":
        raise ValueError("lr_schedule still says 'auto': use the mlx_lora.yaml prepare.py wrote")
    warmup = int(schedule.get("warmup", 0))
    if update < warmup:
        return float(init) * update / warmup
    t = min(update - warmup, int(decay_steps)) / int(decay_steps)
    return end + (float(init) - end) * 0.5 * (1.0 + math.cos(math.pi * t))


def is_save_point(it: int, accum: int, save_every: int) -> bool:
    """An optimizer-update boundary on or after a save_every multiple (one lies in (it - accum, it]): the same rule
    as the mlx backend (spike_train/resume.py), so accumulation is never split by a checkpoint."""
    return it % accum == 0 and it // save_every > (it - accum) // save_every


def epoch_order(n: int, seed: int, epoch: int, batch_size: int) -> list[list[int]]:
    """The batches of one epoch: a permutation seeded from (seed, epoch), cut into full batches (a short last one is
    dropped, as mlx-lm does). A function of (seed, epoch) only, so a resumed run skips the batches it already trained."""
    rng = np.random.default_rng(np.random.SeedSequence([seed, epoch]))
    order = rng.permutation(n).tolist()
    return [order[i:i + batch_size] for i in range(0, n - batch_size + 1, batch_size)]


def prompt_mask(prompt_len: int, total: int, max_len: int | None) -> tuple[int, int]:
    """(first trained token, sequence length) for one chat: the loss covers the final assistant message only
    (mask_prompt), and a chat longer than max_seq_length is cut there (prepare.py already drops those)."""
    length = min(total, max_len) if max_len else total
    if prompt_len >= length:
        raise ValueError(f"the prompt ({prompt_len} tokens) leaves no answer tokens within {length}")
    return prompt_len, length
