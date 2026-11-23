"""Training with the GPU backend (training/train_peft.py) on the CPU: a tiny random Qwen3.5 in its Hub layout (vision
tower + `model.language_model.*`) trained with the recipe's files, checked against what the rest of the pipeline reads.
Needs torch, transformers and peft (training/requirements-gpu.txt): CI's "GPU training backend" job installs them and
sets SPIKE_REQUIRE_PEFT=1, so a missing package fails there instead of skipping."""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "training"))

from spike_train.export import convert, load_base_weight_names, read_safetensors  # noqa: E402

from tests.fixtures import tiny_qwen35 as tiny  # noqa: E402
from tests.fixtures.tiny_qwen35 import KEYS, prepared  # noqa: E402

if os.environ.get("SPIKE_REQUIRE_PEFT") == "1":
    import peft  # noqa: F401
    import torch
    import transformers  # noqa: F401
else:
    torch = pytest.importorskip("torch", reason="needs training/requirements-gpu.txt (CI's GPU training backend job)")
    pytest.importorskip("transformers")
    pytest.importorskip("peft")

@pytest.fixture(scope="module")
def tiny_model(tmp_path_factory) -> Path:
    return tiny.build(tmp_path_factory.mktemp("tiny-qwen35"))


def train(tmp: Path, model: Path, *extra: str, run: str = "run") -> int:
    import train_peft

    return train_peft.main(["finance", "--data", str(tmp / "data"), "--run", str(tmp / run), "--device", "cpu", *extra])


def test_trains_writes_mlx_format_checkpoints_and_exports(tmp_path, tiny_model, monkeypatch):
    monkeypatch.delenv("SPIKE_RESUME", raising=False)
    prepared(tmp_path, tiny_model)
    assert train(tmp_path, tiny_model) == 0
    adapter = tmp_path / "run" / "adapter"
    assert sorted(p.name for p in adapter.glob("*_adapters.safetensors")) == [
        "0000008_adapters.safetensors", "0000016_adapters.safetensors", "0000024_adapters.safetensors"]
    final = read_safetensors(adapter / "adapters.safetensors")
    np.testing.assert_array_equal(final["language_model.model.layers.3.self_attn.q_proj.lora_a"],
                                  read_safetensors(adapter / "0000024_adapters.safetensors")[
                                      "language_model.model.layers.3.self_attn.q_proj.lora_a"])
    modules = {k.rsplit(".", 1)[0] for k in final}
    assert {m.split("layers.", 1)[1] for m in modules if "self_attn" in m} == {f"3.{k}" for k in KEYS[:4]}
    assert len([m for m in modules if ".mlp." in m]) == 4 * 3               # every layer's MLP, none of the vision tower
    cfg = json.loads((adapter / "adapter_config.json").read_text(encoding="utf-8"))
    assert cfg["backend"] == "peft" and cfg["lora_parameters"]["scale"] == 2.0
    # export_adapter.py's conversion accepts it against the base checkpoint's own tensor names
    peft, peft_cfg = convert(final, cfg, load_base_weight_names(tiny_model))
    assert peft_cfg["lora_alpha"] == 8.0 and all(k.startswith("base_model.model.model.language_model.") for k in peft)
    # the sweep finds the checkpoints
    import sweep_checkpoints

    assert sorted(sweep_checkpoints.list_checkpoints(adapter)) == [8, 16, 24]
    run = json.loads((tmp_path / "run" / "run.json").read_text(encoding="utf-8"))
    assert run["exit_code"] == 0 and run["backend"] == "peft" and run["torch"] and run["peft"]
    assert run["run_started_utc"] and run["counts"]["iters"] == 24 and run["stopped_after"] is None
    assert run["base_model"] == {"model": str(tiny_model), "revision": None, "commit": None}   # a local folder
    log = (tmp_path / "run" / "train.log").read_text(encoding="utf-8")
    losses = [float(x.split("Train loss ")[1].split(",")[0]) for x in log.splitlines() if "Train loss" in x]
    vals = [float(x.split("Val loss ")[1]) for x in log.splitlines() if "Val loss" in x]
    assert len(losses) == 6 and losses[-1] < losses[0] - 0.3, losses      # it learns
    assert len(vals) == 4 and vals[-1] < vals[0] - 0.3, vals
    assert "Val loss" in log


def test_an_interrupted_run_resumes_to_the_same_weights(tmp_path, tiny_model, monkeypatch):
    monkeypatch.delenv("SPIKE_RESUME", raising=False)
    prepared(tmp_path, tiny_model)
    assert train(tmp_path, tiny_model, run="straight") == 0
    assert train(tmp_path, tiny_model, "--stop-after", "12", run="cut") == 3
    stopped = json.loads((tmp_path / "cut" / "run.json").read_text(encoding="utf-8"))
    assert stopped["exit_code"] == 3 and stopped["stopped_after"] == 12
    assert (tmp_path / "cut" / "adapter" / "resume" / "0000012" / "resume.json").is_file()
    monkeypatch.setenv("SPIKE_RESUME", "1")
    assert train(tmp_path, tiny_model, run="cut") == 0
    a = read_safetensors(tmp_path / "straight" / "adapter" / "adapters.safetensors")
    b = read_safetensors(tmp_path / "cut" / "adapter" / "adapters.safetensors")
    assert a.keys() == b.keys()
    for k in a:
        np.testing.assert_array_equal(a[k], b[k], err_msg=k)
    log = (tmp_path / "cut" / "train.log").read_text(encoding="utf-8")
    assert "SPIKE_RESUME=1" in log and "resumed from 0000012" in log
    assert json.loads((tmp_path / "cut" / "run.json").read_text(encoding="utf-8"))["run_started_utc"] == stopped["run_started_utc"]


def test_resume_refuses_a_checkpoint_of_other_data(tmp_path, tiny_model, monkeypatch):
    monkeypatch.delenv("SPIKE_RESUME", raising=False)
    data = prepared(tmp_path, tiny_model)
    assert train(tmp_path, tiny_model, "--stop-after", "8") == 3
    with (data / "train.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"messages": [{"role": "user", "content": "Define margin."},
                                         {"role": "assistant", "content": "Profit."}]}) + "\n")
    monkeypatch.setenv("SPIKE_RESUME", "1")
    with pytest.raises(SystemExit, match="refusing to resume"):
        train(tmp_path, tiny_model)


def test_the_answer_alone_is_trained(tiny_model):
    import train_peft
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(tiny_model)
    row = {"messages": [{"role": "user", "content": "Define margin."},
                        {"role": "assistant", "content": "Profit as a share of revenue."}]}
    ids, start = train_peft.encode(tok, row, None)
    assert type(tok).__name__ == "Qwen3_5Tokenizer"                       # the class a real run loads
    assert tok.decode(ids[start:]) == "Profit as a share of revenue.<|im_end|>\n"
    assert tok.decode(ids[:start]).endswith("Define margin.<|im_end|>\n<|im_start|>assistant\n")
    assert math.isclose(len(ids[:start]), len(train_peft.token_ids(
        tok.apply_chat_template(row["messages"][:1], tokenize=True, add_generation_prompt=True))))
