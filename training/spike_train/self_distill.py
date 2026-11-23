"""Self-distillation on gold-answered questions: the base model's own reasoned answers, kept only when correct.

A domain dataset's targets can be terse (a label, a span, a FinQA program) and unlike how the base model answers;
training on them teaches the adapter to stop reasoning (M3 rounds 1-3: finance gained, general knowledge fell early in
training). Here the target is what the base model itself answers to the training question, under the specialist's
system prompt and SPIKE's inference settings (greedy, thinking off), kept only when the evaluation scorer
(evaluation.score) marks it correct against the dataset's gold answer; a wrong greedy answer gets one sampled retry.
The rows are training data like distill.py's: they record the generator and its license, and prepare.py --distilled
checks them again. training/self_distill.py is the command line; this module needs no dataset and no Hub.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from spike_train.data import fmt_finqa_train, fmt_sujet
from spike_train.distill import Teacher
from spike_train.evaluation import Item, make_item, score
from spike_train.self_replay import MIN_ANSWER_TOKENS, TOKEN_MARGIN, rejection

FORMATS = ("finqa_train", "tatqa", "sujet")
DROP_REASONS = ("prompt_too_long", "thinking", "hit_length_limit", "unfinished", "empty", "repeated_sentence",
                "repeated_ngrams", "too_long", "wrong")


@dataclass
class GoldTask:
    id: str
    source: str
    item: Item   # item.prompt is the user turn, item.gold what a correct answer must give


def gold_task(source: str, fmt: str, index: int, row: dict[str, Any]) -> GoldTask | None:
    """The question of one training row with its gold answer, scored like the domain's eval items, or None for a row the
    training formatter would drop. FinQA rows whose annotated steps contradict their arithmetic are dropped as in
    training; a Sujet label is scored as a span (the answer's last line or 'Answer:' line, normalized)."""
    if fmt == "finqa_train":
        item = make_item(source, "finqa", index, row) if fmt_finqa_train(row, "") else None
    elif fmt == "tatqa":
        item = make_item(source, "tatqa", index, row)
    elif fmt == "sujet":
        chat = fmt_sujet(row, "")
        item = None if chat is None else Item("", source, chat["messages"][1]["content"], "span",
                                              chat["messages"][2]["content"])
    else:
        raise ValueError(f"self-distillation has no gold scoring for format '{fmt}' (known: {', '.join(FORMATS)})")
    if item is None:
        return None
    # the id names the question, not its position: a resumed run finds it again whatever the order
    item.id = hashlib.sha1(f"{source}\n{item.prompt}".encode()).hexdigest()[:16]
    return GoldTask(item.id, source, item)


async def solve(teacher: Teacher, system: str, task: GoldTask, count_tokens: Callable[[dict], int], max_len: int,
                record: dict[str, Any], retry_temperature: float) -> tuple[dict | None, str | None]:
    """The base model's correct answer to one task as a training chat (with `record` and the task in `meta`), or (None,
    why the last attempt failed). First greedy; if that is wrong or not an answer SPIKE would give, one sample at
    `retry_temperature`. The question and the answer together fit `max_len` tokens as the trainer counts them."""
    chat = [{"role": "system", "content": system}, {"role": "user", "content": task.item.prompt}]
    budget = max_len - count_tokens({"messages": [*chat, {"role": "assistant", "content": ""}]}) - TOKEN_MARGIN
    if budget < MIN_ANSWER_TOKENS:
        return None, "prompt_too_long"
    why: str | None = None
    for attempt, temperature in enumerate((0.0, retry_temperature), 1):
        done = await teacher.complete(chat, temperature=temperature, max_tokens=budget, thinking=False)
        if why := rejection(done):
            continue
        parsed, correct = score(task.item, done["content"])
        if not correct:
            why = "wrong"
            continue
        row: dict[str, Any] = {"messages": [*chat, {"role": "assistant", "content": done["content"]}]}
        if count_tokens(row) > max_len:
            why = "too_long"
            continue
        row["meta"] = {**record, "seeding": {"mode": "gold", "source": task.source}, "prompt_source": task.source,
                       "prompt_id": task.id, "gold": task.item.gold, "parsed": parsed, "attempt": attempt,
                       "temperature": temperature, "max_tokens": budget,
                       "completion_tokens": done["completion_tokens"]}
        return row, None
    return None, why
