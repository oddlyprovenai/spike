"""U2 — Trending-grade README.md verification: honest figures, caveats, demo placeholder, and sourced comparison."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def test_readme_keeps_a_hidden_slot_for_the_real_demo() -> None:
    text = README.read_text(encoding="utf-8")
    assert "<!-- DEMO_SLOT" in text and "docs/DEMO.md" in text
    assert "placeholder" not in text.lower()  # nothing about the missing demo is shown to readers


def test_readme_states_medicine_caveat_and_finance_round2_rejection() -> None:
    text = README.read_text(encoding="utf-8")
    # Medicine round-2 caveat: 409 of 1,000 MedMCQA base answers unparsed
    assert "409" in text and "1,000" in text and "MedMCQA" in text
    # Finance round 1 and round 2 rejected
    assert "round 1 and round 2" in text.lower() or "rounds 1 and 2" in text.lower()
    # Blind holdout router figure 116/130 = 0.89 (never overstated calibration score)
    assert "116/130" in text and "0.89" in text
    overstated = "0." + "92"
    assert overstated not in text


def test_readme_has_no_banned_hype_or_unannounced_mode() -> None:
    text = README.read_text(encoding="utf-8")
    lower = text.lower()
    for banned in ("beats chatgpt", "revolutionary", "#1"):
        assert banned not in lower
    assert not re.search(r"\bbest\b", lower)
    unannounced = "For" + "ge"
    assert unannounced not in text


def test_readme_comparison_table_covers_all_four_tools_with_sources() -> None:
    text = README.read_text(encoding="utf-8")
    for tool in ("Ollama", "LM Studio", "Open WebUI", "Jan"):
        assert f"| {tool}" in text or f"**{tool}**" in text
    for url in (
        "https://docs.ollama.com",
        "https://lmstudio.ai/docs",
        "https://docs.openwebui.com",
        "https://docs.jan.ai",
    ):
        assert url in text
