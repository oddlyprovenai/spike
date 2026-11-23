"""Self-distillation: the base model's own answers to gold-answered training questions, kept only when correct. No
network and no model: the server is test_self_replay's fake llama-server, the dataset rows and the Hub are replaced."""

import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "training"))

from spike_train.self_distill import DROP_REASONS, gold_task  # noqa: E402

from spike.specialists.catalog import load_catalog  # noqa: E402
from tests.test_finance_data import CHANGE, COMPARE, GROWTH, MULTI, RATIO, SPAN, finqa_row, step  # noqa: E402
from tests.test_self_replay import BASE, BUILD, FakeServer, count_tokens, read_rows  # noqa: E402
from tests.test_training import TEACHER_LICENSES, prepare_env  # noqa: E402

SYSTEM = load_catalog().get("finance").system_prompt
WRONG_SUM = finqa_row("what was the change in revenue?", "-50", -50.0, [step("minus1-1", "959.2", "991.1", "-50")],
                      {"table_1": "revenue is 959.2 ; the year before it was 991.1 ;"}, row_id="BBB/2009/page_1.pdf-2")
SUJET = [{"user_prompt": "Classify the sentiment of this tweet: Shares of $XYZ jump after record earnings.",
          "answer": "positive", "dataset": "zeroshot/twitter-financial-news-sentiment"},
         {"user_prompt": "Classify the sentiment of this tweet: $ABC to hold its annual meeting on Tuesday.",
          "answer": "neutral", "dataset": "zeroshot/twitter-financial-news-sentiment"}]
ROWS = {"finqa_train": [GROWTH, RATIO, COMPARE, WRONG_SUM], "tatqa": [CHANGE, SPAN, MULTI], "sujet": SUJET}


def answers(server: FakeServer):
    """What the fake base model says, by question: the growth rate is right only on the sampled retry, the span and the
    'neutral' tweet are never right, everything else is right at once."""
    def answer(user: str):
        greedy = server.chats[-1]["temperature"] == 0.0
        for key, text in [
            ("growth rate", "(959.2 - 991.1) / 991.1 = -0.0322\nAnswer: " + ("-5%" if greedy else "-3.2%")),
            ("purchased in november", "1947 / 7018 = 0.2774\nAnswer: 27.74%"),
            ("milestones were achieved", "607 * 18.13 thousand = 11.0 million, more than 3.3 million.\nAnswer: yes"),
            ("percentage change", "(16,284 - 6,509) / 6,509 = 1.5018\nAnswer: 150.18"),
            ("internally developed", "It is capitalised at fair value.\nAnswer: at fair value"),
            ("cheese", "From the table.\nAnswer: 11,459; 11,486"),
            ("record earnings", "positive"),
            ("annual meeting", "negative"),
        ]:
            if key in user:
                return text, "stop", ""
        raise AssertionError(f"unexpected question: {user[:80]}")
    return answer


def config(tmp_path: Path) -> Path:
    cfg = yaml.safe_load((ROOT / "training" / "configs" / "finance.yaml").read_text(encoding="utf-8"))
    cfg["domain_sources"] = []
    cfg["self_distill"] = {"sources": [{"source": "finqa-train"}, {"source": "tatqa-train"},
                                       {"source": "sujet-finance", "max": 8000, "max_per_value": 2000}]}
    path = tmp_path / "finance.yaml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return path


def generate(tmp_path, monkeypatch, server: FakeServer, *flags: str, cfg: Path | None = None,
             base_license: str = "apache-2.0"):
    import self_distill

    prepare_env(tmp_path / "data", monkeypatch)    # fake Hub licenses for the datasets
    monkeypatch.setitem(TEACHER_LICENSES, BASE, base_license)
    monkeypatch.setattr(self_distill, "load_rows", lambda src, offset=0, limit=None, **k: iter(
        ROWS[src["format"]][offset: None if limit is None else offset + limit]))
    monkeypatch.setattr(self_distill, "load_token_counter", lambda base_model: count_tokens)
    monkeypatch.setattr(self_distill, "Teacher", server.teacher)
    out = tmp_path / "self_distilled.jsonl"
    monkeypatch.setattr(sys, "argv", ["self_distill.py", str(cfg or config(tmp_path)), "--base-url",
                                      "http://127.0.0.1:8091/v1", "--out", str(out), *flags])
    return self_distill.main(), out


def test_rows_are_the_base_models_answers_kept_only_when_the_scorer_marks_them_correct(tmp_path, monkeypatch, capsys):
    server = FakeServer()
    server.answer = answers(server)
    code, out = generate(tmp_path, monkeypatch, server)
    assert code == 0
    # the inconsistent FinQA row is never asked (as in training); the 8 others are, wrong ones twice
    asked = [(c["messages"][-1]["content"], c["temperature"]) for c in server.chats]
    assert not any("change in revenue" in q for q, _ in asked)
    assert len(asked) == 8 + 3   # 8 questions, 3 retries (growth rate, the span, the neutral tweet)
    assert sorted(t for q, t in asked if "growth rate" in q) == [0.0, 0.7]
    for body in server.chats:
        assert body["chat_template_kwargs"] == {"enable_thinking": False}
        assert body["messages"][0] == {"role": "system", "content": SYSTEM} and len(body["messages"]) == 2
    rows = read_rows(out)
    kept = {r["meta"]["prompt_source"]: [] for r in rows}
    for r in rows:
        kept[r["meta"]["prompt_source"]].append(r["messages"][2]["content"].rsplit("\n", 1)[-1])
    assert kept == {"finqa-train": ["Answer: -3.2%", "Answer: 27.74%", "Answer: yes"],
                    "tatqa-train": ["Answer: 150.18", "Answer: 11,459; 11,486"], "sujet-finance": ["positive"]}
    growth = rows[0]
    assert [m["role"] for m in growth["messages"]] == ["system", "user", "assistant"]
    meta = growth["meta"]
    assert len(meta.pop("prompt_id")) == 16 and meta.pop("max_tokens") == server.chats[0]["max_tokens"]
    settings = {"specialist": "finance", "temperature": 0.0, "retry_temperature": 0.7, "thinking": False,
                "max_seq_length": 1536}
    assert meta == {
        "source": "self_distill", "teacher": BASE, "teacher_license": "apache-2.0", "self_generated": True,
        "server": {"build": BUILD, "model_file": "Qwen3.5-4B-Q4_K_M.gguf", "adapters_checked": True},
        "settings": settings, "seeding": {"mode": "gold", "source": "finqa-train"}, "prompt_source": "finqa-train",
        "gold": repr(-0.03219), "parsed": "-3.2%", "attempt": 2, "temperature": 0.7,
        "completion_tokens": len(growth["messages"][2]["content"].split())}
    assert [r["meta"]["attempt"] for r in rows] == [2, 1, 1, 1, 1, 1]
    summary = json.loads(capsys.readouterr().out)
    assert summary == json.loads(out.with_suffix(".summary.json").read_text())
    assert summary["questions"] == 8 and summary["kept"] == 6
    assert summary["sources"] == {"finqa-train": {"questions": 3, "kept": 3, "kept_on_retry": 1},
                                  "tatqa-train": {"questions": 3, "kept": 2, "kept_on_retry": 0},
                                  "sujet-finance": {"questions": 2, "kept": 1, "kept_on_retry": 0}}
    assert summary["dropped"] == {**dict.fromkeys(DROP_REASONS, 0), "wrong": 2}
    assert not out.with_name(out.name + ".partial").exists()


def test_prepare_takes_the_file_as_distilled_data_with_the_generator_and_its_license(tmp_path, monkeypatch):
    import prepare

    server = FakeServer()
    server.answer = answers(server)
    code, out = generate(tmp_path, monkeypatch, server)
    assert code == 0
    chats, teachers, made = prepare.load_distilled(out)
    assert len(chats) == 6 and all("meta" not in c for c in chats)
    assert teachers == {BASE: "apache-2.0"}
    assert sorted(m["source"] for m in made) == ["finqa-train", "sujet-finance", "tatqa-train"]
    assert all(m["mode"] == "gold" for m in made)


def test_a_retry_also_follows_an_answer_spike_would_not_give(tmp_path, monkeypatch):
    server = FakeServer()
    right = answers(server)
    server.answer = lambda user: (("Answer: 27.74%", "length", "") if server.chats[-1]["temperature"] == 0.0
                                  else right(user))
    code, out = generate(tmp_path, monkeypatch, server, "--limit", "2")
    assert code == 0
    summary = json.loads(out.with_suffix(".summary.json").read_text())
    # growth rate: cut off, then right on the retry; november: cut off, then right
    assert summary["kept"] == 2 and summary["sources"]["finqa-train"]["kept_on_retry"] == 2


def test_a_question_with_no_room_for_an_answer_is_not_sent(tmp_path, monkeypatch):
    from spike_train.self_replay import TOKEN_MARGIN

    server = FakeServer()
    server.answer = answers(server)
    tweet = count_tokens({"messages": [{"role": "system", "content": SYSTEM},
                                       {"role": "user", "content": SUJET[0]["user_prompt"]},
                                       {"role": "assistant", "content": ""}]})
    cfg = yaml.safe_load(config(tmp_path).read_text())
    cfg["train"]["max_seq_length"] = tweet + TOKEN_MARGIN + 20   # room for a tweet's label, not for a table question
    path = tmp_path / "short.yaml"
    path.write_text(yaml.safe_dump(cfg))
    code, out = generate(tmp_path, monkeypatch, server, cfg=path)
    assert code == 0
    assert [c["messages"][-1]["content"] for c in server.chats if c["temperature"] == 0.0] == [
        s["user_prompt"] for s in SUJET]
    summary = json.loads(out.with_suffix(".summary.json").read_text())
    assert summary["dropped"]["prompt_too_long"] == 6 and summary["kept"] == 1


def test_only_formats_with_gold_scoring_are_accepted(tmp_path, monkeypatch):
    cfg = yaml.safe_load(config(tmp_path).read_text())
    cfg["self_distill"]["sources"] = [{"source": "oasst2"}]
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(cfg))
    server = FakeServer()
    with pytest.raises(SystemExit, match="no gold scoring"):
        generate(tmp_path, monkeypatch, server, cfg=path)
    assert not any(c == "/v1/chat/completions" for c in server.calls)
    with pytest.raises(ValueError, match="no gold scoring"):
        gold_task("x", "messages", 0, {})


def test_the_generator_must_be_the_recipes_base_model_with_an_allowed_license(tmp_path, monkeypatch):
    server = FakeServer()
    with pytest.raises(SystemExit, match="not the recipe's base model"):
        generate(tmp_path, monkeypatch, server, "--base-repo", "Qwen/Qwen3.6-35B-A3B")
    with pytest.raises(SystemExit, match="refusing to generate"):
        generate(tmp_path, monkeypatch, server, base_license="cc-by-nc-4.0")
    assert server.calls == []   # refused before the server is asked anything


def test_a_server_with_an_adapter_applied_is_refused(tmp_path, monkeypatch):
    server = FakeServer(adapters=[{"id": 0, "path": "spike-finance.gguf", "scale": 1.0}])
    with pytest.raises(SystemExit, match="LoRA adapters applied"):
        generate(tmp_path, monkeypatch, server)
    assert "/v1/chat/completions" not in server.calls


def test_resume_continues_an_interrupted_run_without_asking_again(tmp_path, monkeypatch):
    import httpx
    import self_distill

    monkeypatch.setattr(self_distill, "BATCH", 2)
    server = FakeServer()
    server.answer = answers(server)
    server.fail_from = 4   # the first batch (growth rate twice, november once) is saved; the second fails
    with pytest.raises(httpx.HTTPStatusError):
        generate(tmp_path, monkeypatch, server)
    out = tmp_path / "self_distilled.jsonl"
    partial = out.with_name(out.name + ".partial")
    assert partial.exists() and not out.exists()
    with pytest.raises(SystemExit, match="--resume continues it"):
        generate(tmp_path, monkeypatch, server)
    server.fail_from = None
    server.chats.clear()
    code, out = generate(tmp_path, monkeypatch, server, "--resume")
    assert code == 0 and len(read_rows(out)) == 6
    asked = [c["messages"][-1]["content"] for c in server.chats]
    assert not any("growth rate" in q or "november" in q for q in asked) and len(asked) == 8   # 6 questions, 2 retries
    assert json.loads(out.with_suffix(".summary.json").read_text())["kept"] == 6


def test_prepare_without_the_file_says_how_to_make_it(tmp_path, monkeypatch):
    import prepare

    prepare_env(tmp_path, monkeypatch, config="finance")
    with pytest.raises(SystemExit, match="training/self_distill.py"):
        prepare.main()
