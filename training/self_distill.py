"""Re-write a specialist's gold-answered training questions with the base model's own answers, kept when correct.

    # 1. serve the BASE model alone (no --lora), e.g. on the Mac
    llama-server -m ~/.spike/models/Qwen3.5-4B-Q4_K_M.gguf --port 8091 --jinja -c 4096 --parallel 4
    # 2. generate
    python training/self_distill.py training/configs/finance.yaml --base-url http://127.0.0.1:8091/v1 \
        --base-repo Qwen/Qwen3.5-4B --out training/data/finance/self_distilled.jsonl
    # 3. build the training set from it (the recipe's domain_sources stay empty: these rows replace them)
    python training/prepare.py training/configs/finance.yaml --distilled training/data/finance/self_distilled.jsonl

The questions are the rows of the config's `self_distill.sources` (entries like domain_sources: source, max, offset,
max_per_value), gated for training like any source, in a format with a gold answer the eval scorer can check
(spike_train/self_distill.py: finqa_train, tatqa, sujet). Each is answered by the server under the specialist's system
prompt, greedy, thinking off, within the tokens `train.max_seq_length` leaves; a wrong answer gets one retry at
`self_distill.retry_temperature` (default 0.7); questions never answered correctly are dropped and counted. The checks
before any question is sent and the resume rules are self_replay.py's: the license of --base-repo (the recipe's
base_model) must be on the allowlist and the server must run no adapter. Writes OUT and OUT.summary.json;
an interrupted run leaves OUT.partial, which --resume continues.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections import Counter
from itertools import zip_longest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "training"))
sys.path.insert(0, str(ROOT))

from prepare import gate_source, load_rows, load_token_counter  # noqa: E402
from self_replay import read_partial  # noqa: E402
from spike_train import licenses  # noqa: E402
from spike_train.distill import Teacher  # noqa: E402
from spike_train.self_distill import DROP_REASONS, FORMATS, GoldTask, gold_task, solve  # noqa: E402
from spike_train.self_replay import check_server  # noqa: E402

BATCH = 32   # questions answered, then appended to OUT.partial, at a time


def load_tasks(entries: list[dict], registry: dict) -> list[GoldTask]:
    """Every question of the entries with a gold answer, once per distinct (source, question), the sources taken in
    turn (one question of each, then the next), so --limit samples every source."""
    per_source: list[list[GoldTask]] = []
    seen: set[str] = set()
    for entry in entries:
        name = entry["source"]
        src = registry[name]
        if src["format"] not in FORMATS:
            raise SystemExit(f"self_distill source '{name}' has format '{src['format']}', which has no gold scoring "
                             f"(known: {', '.join(FORMATS)})")
        gate_source(name, src, "train")  # the questions are training data: same gate as prepare.py
        cap = {"per_value": entry["max_per_value"]} if "max_per_value" in entry else {}
        tasks: list[GoldTask] = []
        for i, row in enumerate(load_rows(src, entry.get("offset", 0), entry.get("max"), **cap)):
            task = gold_task(name, src["format"], i, row)
            if task and task.id not in seen:
                seen.add(task.id)
                tasks.append(task)
        per_source.append(tasks)
    return [t for group in zip_longest(*per_source) for t in group if t is not None]


async def run(args: argparse.Namespace) -> int:
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    registry = yaml.safe_load((ROOT / "training" / "datasets.yaml").read_text(encoding="utf-8"))["sources"]
    from spike.specialists.catalog import load_catalog

    spec = load_catalog().get(cfg["specialist"])
    scfg = cfg.get("self_distill") or {}
    max_len = (cfg.get("train") or {}).get("max_seq_length")
    if not scfg.get("sources") or not max_len:
        raise SystemExit("the config needs self_distill.sources (the gold-answered questions) and train.max_seq_length "
                         "(how many tokens a question and its answer may take)")
    retry = float(scfg.get("retry_temperature", 0.7))
    repo = args.base_repo or cfg["base_model"]
    if repo != cfg["base_model"]:
        raise SystemExit(f"--base-repo {repo} is not the recipe's base model ({cfg['base_model']}): self-distillation "
                         "is the model being trained answering for itself")
    try:  # before the server is asked anything: the generator's terms apply to everything it writes
        generator_license = licenses.teacher_license(repo, "generator")
    except ValueError as exc:
        raise SystemExit(f"refusing to generate: {exc} (--base-repo names the Hub repo of the weights)") from exc
    teacher = Teacher(args.base_url, repo, concurrency=args.concurrency)
    try:
        try:
            server = await check_server(teacher)
        except ValueError as exc:
            raise SystemExit(f"refusing to generate: {exc}") from exc
        settings = {"specialist": cfg["specialist"], "temperature": 0.0, "retry_temperature": retry, "thinking": False,
                    "max_seq_length": max_len}
        identity = {"generator": repo, "generator_license": generator_license, "server": server, "settings": settings}
        tasks = load_tasks(scfg["sources"], registry)
        tasks = tasks[: args.limit] if args.limit else tasks
        count_tokens = load_token_counter(cfg["base_model"])
        out = Path(args.out)
        partial = out.with_name(out.name + ".partial")
        done: dict[str, dict] = {}
        if partial.exists():
            if not args.resume:
                raise SystemExit(f"{partial} is left by an interrupted run: --resume continues it; delete it to start over")
            done = read_partial(partial, identity)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            partial.write_text(json.dumps({"run": identity}, ensure_ascii=False) + "\n", encoding="utf-8")
        resumed = sum(t.id in done for t in tasks)
        todo = [t for t in tasks if t.id not in done]
        print(f"{len(tasks)} questions, {resumed} already done", file=sys.stderr)
        # distill.py's row record (prepare.py --distilled reads `teacher`), plus what self_replay.py records
        record = {"source": "self_distill", "teacher": repo, "teacher_license": generator_license, "self_generated": True,
                  "server": server, "settings": settings}
        with partial.open("a", encoding="utf-8") as f:
            for i in range(0, len(todo), BATCH):
                batch = todo[i:i + BATCH]
                answers = await asyncio.gather(*[
                    solve(teacher, spec.system_prompt, t, count_tokens, max_len, record, retry) for t in batch])
                for t, (row, why) in zip(batch, answers, strict=True):
                    done[t.id] = {"prompt_id": t.id, **({"row": row} if row else {"dropped": why})}
                    f.write(json.dumps(done[t.id], ensure_ascii=False) + "\n")
                f.flush()
                kept = sum("row" in done[t.id] for t in tasks if t.id in done)
                print(f"  {resumed + i + len(batch)}/{len(tasks)} processed, {kept} kept", file=sys.stderr)
    finally:
        await teacher.aclose()
    rows = [done[t.id]["row"] for t in tasks if "row" in done[t.id]]
    dropped = Counter(done[t.id]["dropped"] for t in tasks if "dropped" in done[t.id])
    per_source: dict[str, dict[str, int]] = {}
    for t in tasks:
        counts = per_source.setdefault(t.source, {"questions": 0, "kept": 0, "kept_on_retry": 0})
        counts["questions"] += 1
        if row := done[t.id].get("row"):
            counts["kept"] += 1
            counts["kept_on_retry"] += row["meta"]["attempt"] == 2
    summary = {**identity, "questions": len(tasks), "kept": len(rows), "resumed_questions": resumed,
               "sources": per_source, "dropped": {reason: dropped[reason] for reason in DROP_REASONS}, "out": str(out)}
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if not rows:
        raise SystemExit(f"no answer was kept ({dict(dropped)}); nothing written beyond {partial.name}; if 'thinking' or "
                         "'hit_length_limit' dominates, serve the model with --jinja so thinking is switched off")
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    out.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    partial.unlink()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--base-url", required=True, help="OpenAI-compatible endpoint of llama-server serving the base model "
                                                       "alone, e.g. http://127.0.0.1:8091/v1")
    ap.add_argument("--base-repo", help="Hugging Face repo of the served weights, whose license governs the answers "
                                        "(default and only allowed value: the config's base_model)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, help="only the first N questions (a speed test, too few rows to train on)")
    ap.add_argument("--concurrency", type=int, default=4, help="requests in flight; llama-server needs --parallel >= this")
    ap.add_argument("--resume", action="store_true", help="continue the OUT.partial of an interrupted run")
    return asyncio.run(run(ap.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
