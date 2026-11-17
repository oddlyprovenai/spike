"""U1 — Automated verification of the v0.1 launch audit claims and referenced evidence."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_MD = ROOT / "docs" / "audits" / "2026-11-18-launch-audit-u1.md"


def test_launch_audit_exists_and_cites_verified_repo_evidence() -> None:
    assert AUDIT_MD.is_file(), "Missing docs/audits/2026-11-18-launch-audit-u1.md"
    text = AUDIT_MD.read_text(encoding="utf-8")

    for gate in (
        "Gate 1",
        "Gate 2",
        "Gate 3",
        "Gate 4",
        "Gate 5",
        "Gate 6",
        "Gate 7",
        "Gate 8",
    ):
        assert gate in text, f"Audit missing {gate}"

    receipt = json.loads((ROOT / "spike" / "specialists" / "acceptance" / "medicine.json").read_text(encoding="utf-8"))
    assert receipt["sha256"] in text
    assert "409" in text and "1,000" in text

    results = json.loads((ROOT / "docs" / "results" / "specialists.json").read_text(encoding="utf-8"))
    med_rounds = results["specialists"]["medicine"]["rounds"]
    round2 = next(r for r in med_rounds if r["round"] == 2)
    assert round2["final"]["rescored"] is None
    assert '"rescored": null' in text

    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "#")):
            continue
        rel = target.split("#", 1)[0].strip()
        if rel:
            assert (AUDIT_MD.parent / rel).resolve().exists(), f"Broken link in U1 audit: {target}"


def test_launch_audit_has_no_personal_data_or_disallowed_figures() -> None:
    text = AUDIT_MD.read_text(encoding="utf-8")
    macos_home_prefix = "/" + "Users" + "/"
    assert macos_home_prefix not in text
    assert "116/130" in text and "0.89" in text
