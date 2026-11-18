"""U4 — Bilingual EN/ES user guides for building a first specialist and workspace governance."""

from __future__ import annotations

import json
import re
import zipfile
from io import BytesIO
from pathlib import Path

import jsonschema
import pytest

from spike.orchestrator.router import LexicalRouter
from spike.packs import export_pack, read_pack
from spike.specialists.catalog import load_catalog

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "guide"
PACK_SCHEMA = json.loads((ROOT / "docs" / "schemas" / "specialist-pack.schema.json").read_text(encoding="utf-8"))

NEW_MODULES = ("first-specialist", "workspace-governance")
ES_SECTIONS = ("## Qué hace", "## Cómo se usa paso a paso", "## Límites reales", "## Cómo comprobarlo")
EN_SECTIONS = ("## What it does", "## Step-by-step usage", "## Real limits", "## How to verify")


@pytest.mark.parametrize("slug", NEW_MODULES)
def test_new_guide_pages_exist_in_es_and_en_and_are_indexed(slug: str) -> None:
    es_page = GUIDE / "es" / f"{slug}.md"
    en_page = GUIDE / "en" / f"{slug}.md"
    assert es_page.is_file(), f"Missing {es_page}"
    assert en_page.is_file(), f"Missing {en_page}"

    es_text = es_page.read_text(encoding="utf-8")
    en_text = en_page.read_text(encoding="utf-8")
    for h in ES_SECTIONS:
        assert h in es_text, f"es/{slug}.md missing {h}"
    for h in EN_SECTIONS:
        assert h in en_text, f"en/{slug}.md missing {h}"

    # Must be linked in root, ES, and EN guide index pages
    assert f"es/{slug}.md" in (GUIDE / "README.md").read_text(encoding="utf-8")
    assert f"en/{slug}.md" in (GUIDE / "README.md").read_text(encoding="utf-8")
    assert f"({slug}.md)" in (GUIDE / "es" / "README.md").read_text(encoding="utf-8")
    assert f"({slug}.md)" in (GUIDE / "en" / "README.md").read_text(encoding="utf-8")

    # Screenshot link must resolve to a valid PNG
    for page, text in ((es_page, es_text), (en_page, en_text)):
        imgs = re.findall(r"!\[[^\]]+\]\(([^)]+)\)", text)
        assert imgs, f"{page.name} must embed at least one PNG screenshot"
        for target in imgs:
            img_path = (page.parent / target.split("#", 1)[0].strip()).resolve()
            assert img_path.is_file() and img_path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


@pytest.mark.parametrize("lang", ("en", "es"))
def test_first_specialist_json_example_loads_routes_and_packs(lang: str, tmp_path: Path) -> None:
    text = (GUIDE / lang / "first-specialist.md").read_text(encoding="utf-8")

    # Must not contain synthetic LLM training datasets/rows
    assert '{"messages":' not in text

    json_blocks = re.findall(r"```json\n(.*?)```", text, flags=re.S)
    assert json_blocks, f"Expected custom specialist JSON block in {lang}/first-specialist.md"
    spec_dict = json.loads(json_blocks[0])

    catalog = load_catalog(extra=[spec_dict])
    spec = catalog.get(spec_dict["id"])
    assert spec.id == "logistics"
    assert spec.adapter_status == "none"

    router = LexicalRouter(catalog)
    en_decision = router.route("Compute safety stock and reorder point for lead time under incoterms FOB.")
    es_decision = router.route("Calcula el punto de pedido y stock de seguridad con incoterms y albarán.")
    assert en_decision.specialists[0] == "logistics"
    assert es_decision.specialists[0] == "logistics"

    # Validate companion SKILL.md block and full specialist pack round-trip against schema
    md_blocks = re.findall(r"```markdown\n(---\nname:.*?)```", text, flags=re.S)
    assert md_blocks, f"Expected SKILL.md example in {lang}/first-specialist.md"
    skill_dir = tmp_path / "src_skills" / "inventory-reorder-audit"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(md_blocks[0], encoding="utf-8")

    blob = export_pack([spec_dict], [], [skill_dir])
    with zipfile.ZipFile(BytesIO(blob)) as zf:
        manifest_raw = json.loads(zf.read("pack.json").decode("utf-8"))
    jsonschema.validate(manifest_raw, PACK_SCHEMA)

    installed_manifest, installed_skills = read_pack(blob, tmp_path / "dst_skills")
    assert installed_manifest["specialists"][0]["id"] == "logistics"
    assert installed_skills == ["inventory-reorder-audit"]
