# SPIKE v0.1 Launch Readiness & OPSEC Audit (U1)

Date: 2026-11-18. Audited commit on `origin/main` of `https://github.com/oddlyprovenai/spike`: `260943ea2d1351916978d05e501c7903b55b23be` (`2026-11-14 23:06:39 +0000`).
Method: Read-only verification of repository files, committed JSON records, offline CI validator scripts, test suites, and GitHub CLI metadata (`gh repo view`, `gh run list`, `gh release list`, `gh issue list`). No LLM weights were downloaded or evaluated.

## Executive Summary

| Gate | Requirement | Status | Blocking v0.1 Announcement? |
|---|---|---|---|
| **Gate 1** | Measured numbers on Mac and 16 GB x86 CPU-only | **PASS** | No |
| **Gate 2** | At least one accepted adapter (Medicine) or honest status | **PASS (rescoring pending)** | Partial — `rescored` is still `null` |
| **Gate 3** | Install in <= 3 commands tested on clean macOS, Linux, Windows | **PARTIAL** | Minor — CI runners pass; desktop Windows 11 & macOS real-model native installer pending |
| **Gate 4** | Green CI on GitHub | **PASS (`260943ea`)** | Must re-run on final v0.1.0 tag commit |
| **Gate 5** | README: 30–60 s real demo GIF/video, measured speed table, specialists, 5-line Why SPIKE, honest comparison | **INCOMPLETE** | **Yes** — real demo recording (`L1`) missing |
| **Gate 6** | Adapters and model cards published on Hugging Face | **PENDING** | **Yes** — awaits local data manifest (`M15`) + owner approval (`L3`) |
| **Gate 7** | Release `v0.1.0` with changelog, `good first issue` list, and templates | **PARTIAL** | **Yes** — 0 GitHub Releases and 0 open issues published yet |
| **Gate 8** | Final security, license (`THIRD_PARTY.md`), and OPSEC review | **NEEDS OPSEC SCRUB** | **Yes** — public `main` contains legacy personal identifiers in static docs/JSON |

---

## Detailed Gate Evidence

### Gate 1 — Measured Hardware Benchmarks in `STATUS.md`
- **Verdict:** **PASS**.
- **Apple Silicon evidence:** [STATUS.md](../STATUS.md) (`evals/results/bench-mac-20261017/bench-metal-ngl99.json` and `bench-cpu-ngl0.json`): Apple M4 Max (36 GB RAM, Metal `--gpu-layers 99`), Qwen3.5-4B Q4_K_M, `q8_0` KV cache: `82.4 tok/s` generation (`0.86 s` TTFT, `3,653 MiB` peak RSS) at 1K prompt; `79.8 tok/s` (`7.2 s` TTFT, `3,668 MiB` peak RSS) at 8K prompt.
- **16 GB x86 CPU-only evidence:** `evals/results/bench-x86-16gb-20261018/bench-cpu-ngl0.json`: 4-core Xeon with AVX-512, 15.7 GB RAM, no swap, `llama.cpp` `b11709-62318cd57`: `6.2 tok/s` generation (`52 s` TTFT, `3,654 MiB` anonymous RSS, `6,274 MiB` total RSS) at 1K prompt; `5.1 tok/s` (`773 s` / `13 min` TTFT, `3,656 MiB` anonymous RSS, `6,276 MiB` total RSS) at 8K prompt; `2.1 tok/s` (`5,566 s` TTFT) at 32K prompt (which is why CPU-only machines default to 8K context).
- **Automated check:** `pytest -q tests/test_public_figures_g30.py` passes (`2 passed`).

### Gate 2 — Accepted Specialist Adapter & Honest Status
- **Verdict:** **PASS WITH CAVEAT (rescoring pending before quoting `+35.07` as a headline)**.
- **Accepted adapter receipt:** [medicine.json](../../spike/specialists/acceptance/medicine.json) and `training/runs/medicine/sweep/final/summary.json`: `spike-medicine-it13270-s0.5.gguf` (`42,485,024` bytes, SHA-256 `21caa0a0b24bdd4d5badb5bc1f336d2eb3061a635400a85a15f4cf52f9d40a34`), accepted `2026-11-05`. Pooled medical accuracy `31.9% -> 67.0%` (`+35.07` pts over `2,318` paired questions, `p < 1e-6`), general knowledge `63.7% -> 63.1%` (`-0.62` pts over `800` MMLU-Pro questions, gate limit `1.5` pts).
- **Rejected runs honestly logged:** Medicine round 1 rejected (`-7.62` general drop); Finance round 1 (`768`-token window) and round 2 (`1536`-token window) both rejected for exceeding the `1.5`-pt general drop limit ([STATUS.md](../STATUS.md)). All 12 non-Medicine specialists run as prompt profiles marked beta (`β`).
- **Router figure verified:** Blind holdout (`evals/data/router_holdout.jsonl`) is `116/130 = 0.89` (Wilson 95% CI `0.83–0.93`).
- **Open sub-item (`M16`):** In [specialists.json](../results/specialists.json), `rounds[1].final` still has `"rescored": null`. On the original run, the base model left `409` of `1,000` MedMCQA answers and `241` of `818` MMLU-Pro health answers unparsed (counting as wrong), whereas the adapter left `26` and `16` unparsed. Until `run_eval.py --rescore` with the updated choice extractor (`M14`) is committed to `main`, public copy should state that the Medicine adapter passed its acceptance gate without leading with `+35` as an unqualified headline.

### Gate 3 — Installation in <= 3 Commands Across Clean OSes
- **Verdict:** **PARTIAL (CI runners verified; end-user desktop machines and PyPI pending)**.
- **Source installer scripts:** `git clone https://github.com/oddlyprovenai/spike.git && cd spike` followed by `./scripts/install.sh --yes` (macOS/Linux) or `.\scripts\install.ps1 -Yes` (Windows) + `spike serve --open` = **3 commands total** (`--no-model` / `-NoModel` skips the 2.74 GB download).
- **Verified on clean GitHub Actions runners:**
  - Script installers (`installers.yml`, runs `39160997172` and `39421918616`): passed on Ubuntu 24.04 (with and without Homebrew), macOS 26 arm64, and Windows Server 2025 (PowerShell 5.1 and 7) with real Qwen3.5-4B answering `/v1/chat/completions`.
  - Native desktop installer candidates (`release.yml` run `41409774078` + `installers-real-model.yml` runs `41449693467` and `41502647706`): `.exe` and `.AppImage` passed end-to-end with real Qwen3.5-4B on 16 GB Windows Server 2022 and Ubuntu 24.04 runners; `.dmg` passed with the tiny fixture model (the free 7.0 GiB macOS runner is blocked by the app's 8 GiB RAM guard).
  - Wheel smoke without a model: `python scripts/installer_smoke.py` passes in CI (`G45`).
- **Remaining gaps:** (1) Not yet tested on non-server Windows 11 desktop or physical clean user machines (unsigned Gatekeeper/SmartScreen prompts); (2) `spike-ai` is not yet published on PyPI; (3) `README.md` Quick Start currently lists 7 manual commands before mentioning `scripts/install.sh` (addressed in `gemini/U2` and `gemini/U3`).

### Gate 4 — Green CI on GitHub
- **Verdict:** **PASS on `origin/main` (`260943ea`)**.
- **Command & evidence:** `gh run list --repo oddlyprovenai/spike --limit 5` confirms `CI` workflow run `43651557478` (`2026-11-14T23:06:43Z`) on HEAD `260943ea2d1351916978d05e501c7903b55b23be` completed with `conclusion: "success"` across all 9 jobs (Python 3.11/3.13 Linux, macOS, Windows, MLX CPU, web Vitest+build, wheel package smoke, Playwright E2E smoke, real `llama-server` + LoRA GGUF converter).
- **Housekeeping note:** Older CI run `43098315415` (`2026-11-11T20:49:46Z`) remains stuck in `status: "queued"` and should be cancelled via GitHub Actions UI/CLI. CI must run green again on the final tagged release commit.

### Gate 5 — Trending-Grade `README.md` & Real 30–60 s Demo
- **Verdict:** **INCOMPLETE**.
- **What exists:** [README.md](../../README.md) has the light/dark banner, 13-specialist table, 5-point "Why SPIKE", measured hardware speed table, and sourced comparison table against Ollama, LM Studio, Open WebUI, and Jan.
- **What is missing or needs update:**
  1. **No real demo GIF/video (`L1`):** [DEMO.md](../DEMO.md) and `web/e2e/demo.mjs` exist, but zero real-model `.gif`/`.mp4` capture is committed (`git ls-files "*demo*.gif" "*demo*.mp4"` returns empty).
  2. **Caveat & positioning updates:** Top status banner should lead with acceptance-by-gate and explicitly surface the `409/1,000` MedMCQA base unparsed caveat next to `+35.07`, avoid promoting the unmeasured multi-agent blueprint mode, and put the <= 3-command install path front and center (prepared in branch `gemini/U2`).

### Gate 6 — Hugging Face Adapters & Model Cards
- **Verdict:** **PENDING (`M15` + `L3`)**.
- **What exists:** `training/model_card.py` and brand banners (`brand/specialists/*/hf-banner-*.png`) are built and tested (`pytest -q tests/test_model_card.py`: `17 passed`).
- **What is missing:** `training/data/medicine/manifest.json` and `training/runs/medicine/export.json` are gitignored and live only on the local training machine (`M15`). Neither the Hugging Face organization (`oddlyprovenai`) nor `spike-medicine-it13270-s0.5.gguf` is published yet (requires explicit owner OK, `L3`). Complete standalone model card draft with the `409/1,000` MedMCQA caveat is prepared in `U7`.

### Gate 7 — Release `v0.1.0`, Changelog, Templates & Good First Issues
- **Verdict:** **PARTIAL**.
- **What exists:** `.github/ISSUE_TEMPLATE/` (`bug_report.yml`, `benchmark.yml`, `failure.yml`, `specialist.yml`, `config.yml`), `.github/pull_request_template.md`, [RELEASE-NOTES.md](../../packaging/RELEASE-NOTES.md), and [CHANGELOG.md](../../CHANGELOG.md) (`## [0.1.0] — unreleased`).
- **What is missing / stale:**
  1. `gh release list --repo oddlyprovenai/spike` -> `no releases found` (requires owner OK).
  2. `gh issue list --repo oddlyprovenai/spike` -> `no open issues` (20 scoped `good first issue` drafts prepared in `U6`, not opened without owner OK).
  3. Stale line at the bottom of `CHANGELOG.md` (line 317): `"Not measured yet: Quality of any trained adapter"` contradicts line 8 (`Medicine, passed its acceptance tests`) — Claude should remove that phrase when cutting `0.1.0`.

### Gate 8 — Security, Licenses (`THIRD_PARTY.md`), and OPSEC Review
- **Security & Licenses:** **PASS** for shipped code.
  - [REVIEW-v0.1.md](../release/REVIEW-v0.1.md) and [2026-11-security-review.md](2026-11-security-review.md) document fixes for S1–S4, O4-1, O4-2, and L2–L8 (`L1` cross-port localhost Origin stays open intentionally for Vite dev proxy).
  - [THIRD_PARTY.md](../../THIRD_PARTY.md) and `packaging/collect_licenses.py` cover all 64 Python packages, CPython, 90 production npm packages, bundled skills, 20 design systems, SIL OFL fonts, `llama.cpp` `b11709` vendored notices, and the AppImage `type2-runtime` LGPL-2.1 notice.
  - Dependency check on `2026-11-18`: `cd web && npm audit --omit=dev` reports **`found 0 vulnerabilities`** in the shipped UI bundle. Note: `npm audit` (including devDependencies) reports 6 high-severity entries from a single newly published ReDoS advisory in `picomatch` (`GHSA-fc5q-39xc-vjpf`) pulled in by `vite`/`vitest` (dev-only, never shipped).
- **CRITICAL OPSEC FINDING ON PUBLIC REPO (`https://github.com/oddlyprovenai/spike` is `PUBLIC`):**
  To preserve Oddly Proven's strict anonymity rule before driving launch traffic, Claude should scrub the following legacy personal identifiers still present on `origin/main`:
  1. **Legacy personal GitHub handle URLs** in `site-src/index.en.html`, `site-src/index.es.html`, `site/index.html`, `site/es/index.html`, and `tests/test_site_g31.py` (line 22) — replace with `https://github.com/oddlyprovenai/spike` (fixed in branch `gemini/U5`).
  2. **Local macOS home directory paths** (`/<home-dir>/<owner-handle>/...`) in `AGENTS.md` (line 43), `web/e2e/a11y.mjs` (lines 17–18), `web/e2e/replay.mjs` (line 16), `training/runs/medicine/sweep/summary.json`, and `evals/results/20261020-202442/summary.json`.
  3. **Founder's first name** in `docs/STATUS.md`, `docs/team/PLAN.md`, `docs/team/BOARD.md`, `docs/release/REVIEW-v0.1.md`, `docs/release/LAUNCH.md`, `packaging/RELEASE-NOTES.md`, and `archive/fase0/*` (plus legacy life-OS codename in `docs/team/BOARD.md` line 107).

---

## Verification Commands Executed (`2026-11-18`)

```text
$ .venv/bin/ruff check .
All checks passed!

$ .venv/bin/spike skills validate && .venv/bin/spike connectors validate
Validation passed
Validation passed

$ .venv/bin/python scripts/compat_matrix.py --check
$ .venv/bin/python scripts/cli_reference.py --check
$ .venv/bin/python scripts/api_reference.py --check
$ .venv/bin/python scripts/build_site.py --check
$ .venv/bin/python scripts/results_index.py --check
$ .venv/bin/python scripts/release/readiness.py check --revision 260943ea2d1351916978d05e501c7903b55b23be
Valid / Valido: source coverage and record structure

$ cd web && npm audit --omit=dev
found 0 vulnerabilities

$ .venv/bin/python -m pytest -q tests/test_public_figures_g30.py tests/test_docs_links_g20.py tests/test_site_g31.py tests/test_user_guide_g19.py tests/test_faq_g32.py tests/test_model_card.py tests/test_i18n_audit.py tests/test_security_review.py tests/test_security_review_low.py tests/test_o4_security.py tests/test_collect_licenses.py tests/test_no_network_g29.py tests/test_installer_smoke_g45.py
223 passed in 14.85s
```
