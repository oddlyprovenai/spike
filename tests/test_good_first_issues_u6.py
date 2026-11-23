"""U6 — Verify the 20 curated good-first-issue specs reference real repository modules and tests."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs" / "release" / "GOOD-FIRST-ISSUES.md"


def test_twenty_good_first_issues_reference_real_files() -> None:
    assert CATALOG.is_file()
    text = CATALOG.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if re.match(r"^\|\s*\d{2}\s*\|", line)]
    assert len(rows) == 20, f"Expected 20 issue rows, found {len(rows)}"

    # Every backticked repo path in the Target Files column must exist in the checkout
    for row in rows:
        cols = [c.strip() for c in row.strip("|").split("|")]
        assert len(cols) == 4, row
        paths = re.findall(r"`([^`]+)`", cols[2])
        assert paths, f"Row missing target file paths: {row}"
        for rel in paths:
            assert (ROOT / rel).exists(), f"Missing target path {rel!r} in row: {row}"
