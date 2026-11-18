# SPIKE v0.1 — Curated `good first issue` Backlog (20 Drafts, Not Published)

Prepared for launch review; **none of these issues has been opened on GitHub** (requires explicit owner approval). Every item is self-contained, avoids core security/orchestrator internals (`spike/core/`) and training datasets (`training/`), and names exact target modules and verification suites.

| ID | Title | Target Files | Verification |
|---|---|---|---|
| 01 | `cli: add --json output flag to spike doctor for machine-readable diagnostics` | `spike/cli.py`, `spike/runtime/hardware.py`, `tests/test_cli.py` | `pytest tests/test_cli.py tests/test_cli_help.py` |
| 02 | `bench: record optional power-source state (AC vs battery) in spike bench --share allowlist` | `spike/bench.py`, `docs/schemas/bench-share.schema.json`, `tests/test_bench.py` | `pytest tests/test_bench.py tests/test_ecosystem.py` |
| 03 | `analytics: accept .tab extension alongside .tsv in the read-only DuckDB loader` | `spike/analytics/engine.py`, `spike/analytics/rescue.py`, `tests/test_analytics.py` | `pytest tests/test_analytics.py tests/test_analytics_reliability.py` |
| 04 | `glossary: return skipped duplicate count when importing CSV glossaries with case/accent collisions` | `spike/memory/glossary.py`, `web/src/components/Glossary.tsx`, `tests/test_glossary.py` | `pytest tests/test_glossary.py` + `npx vitest run` |
| 05 | `skills: include YAML line number when spike skills validate fails on malformed front matter` | `spike/skills/validation.py`, `spike/skills/engine.py`, `tests/test_skill_validation.py` | `pytest tests/test_skill_validation.py` |
| 06 | `connectors: report entry index and connector id on schema errors in spike connectors validate` | `spike/connectors/validation.py`, `tests/test_skill_validation.py` | `pytest tests/test_skill_validation.py tests/test_connectors.py` |
| 07 | `web(a11y): announce code-block copy confirmation via polite live region in Markdown renderer` | `web/src/components/Markdown.tsx`, `web/src/i18n.ts`, `web/src/a11y.test.ts` | `npx vitest run` + `pytest tests/test_i18n_audit.py` |
| 08 | `web(palette): preserve last-highlighted item when query text is cleared with Backspace` | `web/src/components/CommandPalette.tsx`, `web/src/a11y.test.ts` | `npx vitest run` |
| 09 | `history: reject inverted date filters (from > to) with a clear 400 error in /api/history` | `spike/store/history.py`, `spike/server/history_api.py`, `tests/test_history.py` | `pytest tests/test_history.py tests/test_history_server.py` |
| 10 | `subtitles: detect overlapping cue timestamps in SRT/VTT editor validation` | `spike/subtitles.py`, `web/src/components/SubtitleStudio.tsx`, `tests/test_subtitles.py` | `pytest tests/test_subtitles.py tests/test_subtitles_api.py` |
| 11 | `geo: render an optional deterministic kilometer scale bar in geo_map SVG output` | `spike/geo/render.py`, `spike/geo/measure.py`, `tests/test_geo.py` | `pytest tests/test_geo.py` |
| 12 | `architecture: include per-language module and edge counts in architecture_graph summary` | `spike/architecture/scan.py`, `web/src/components/Explorer.tsx`, `tests/test_architecture.py` | `pytest tests/test_architecture.py` + `npx vitest run src/explorer.test.tsx` |
| 13 | `tutor: add UTF-8 CSV export of SM-2 study topics in Settings -> Memory -> Tutor` | `spike/memory/tutor.py`, `spike/server/memory_api.py`, `tests/test_tutor.py` | `pytest tests/test_tutor.py` + `npx vitest run` |
| 14 | `research: record SPIKE version and export timestamp in Jupyter notebook metadata without host paths` | `spike/research.py`, `tests/test_research.py` | `pytest tests/test_research.py tests/test_research_server.py` |
| 15 | `device-lab: surface offending CSS selector snippet when reporting horizontal overflow elements` | `spike/dev/device_lab.py`, `web/src/components/DeviceLab.tsx`, `tests/test_device_lab.py` | `pytest tests/test_device_lab.py` + `npx vitest run src/deviceLab.test.tsx` |
| 16 | `design: reject unbalanced curly braces or unclosed comments when importing custom tokens.css` | `spike/design/library.py`, `tests/test_design.py` | `pytest tests/test_design.py` |
| 17 | `samples: add cross-platform path and UTF-8 round-trip regression tests for all 6 sample projects` | `spike/samples/__init__.py`, `tests/test_samples.py` | `pytest tests/test_samples.py tests/test_cross_platform_g22.py` |
| 18 | `e2e: compute Playwright cache browser paths dynamically via os.homedir() in a11y.mjs and replay.mjs` | `web/e2e/a11y.mjs`, `web/e2e/replay.mjs` | `node --check web/e2e/a11y.mjs` |
| 19 | `docs(integrations): add offline curl smoke snippet for /v1/models, /v1/chat/completions, and /mcp` | `docs/INTEGRATIONS.md`, `tests/test_openai_api.py`, `tests/test_mcp_server.py` | `pytest tests/test_docs_links_g20.py` |
| 20 | `community-bench: share verified spike bench --share results on 8 GB and 16 GB consumer laptops` | `.github/ISSUE_TEMPLATE/benchmark.yml`, `docs/schemas/bench-share.schema.json`, `tests/test_bench.py` | `pytest tests/test_bench.py tests/test_ecosystem.py` |
