"""U7 — Verify the Hugging Face Medicine adapter model card draft matches committed evaluation records and caveats."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "docs" / "release" / "HF-MEDICINE-CARD-DRAFT.md"
RECEIPT = ROOT / "spike" / "specialists" / "acceptance" / "medicine.json"
SUMMARY = ROOT / "training" / "runs" / "medicine" / "sweep" / "final" / "summary.json"


def test_hf_medicine_card_frontmatter_and_receipt_integrity() -> None:
    assert CARD.is_file()
    text = CARD.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    meta = yaml.safe_load(text.split("---\n", 2)[1])

    assert meta["license"] == "apache-2.0"
    assert meta["base_model"] == "Qwen/Qwen3.5-4B"
    assert meta["pipeline_tag"] == "text-generation"
    assert "medicine" in meta["tags"] and "lora" in meta["tags"] and "gguf" in meta["tags"]
    assert set(meta["datasets"]) == {"OpenAssistant/oasst2", "openlifescienceai/medmcqa", "qiaojin/PubMedQA"}

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["sha256"] in text
    assert f"{receipt['bytes']:,}" in text
    assert receipt["file"] in text
    assert "`~/.spike/adapters/spike-medicine.gguf`" in text


def test_hf_medicine_card_highlights_medmcqa_409_unparsed_caveat_and_safety() -> None:
    text = CARD.read_text(encoding="utf-8")
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    medmcqa_base = summary["tasks"]["medmcqa-val"]["accuracy"]["base"]
    assert medmcqa_base["unparsed"] == 409 and medmcqa_base["n"] == 1000

    assert "409" in text and "1,000" in text and "MedMCQA" in text
    assert "241" in text and "818" in text
    assert "--rescore" in text
    assert "0.467" in text and "0.660" in text
    assert "not a medical device" in text
    assert "not professional" in text.lower() or "not clinical advice" in text.lower()
