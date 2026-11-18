# Installation and First Run

Language: [Español](../es/installation.md) | **English** · [Guide Index](README.md)

![Installation and First Run](../images/installation.png)

## What it does

Installs SPIKE in 3 commands or fewer as an isolated Python application (`pipx`) with the bundled web UI, configures the local `llama-server` (`llama.cpp`) engine, and optionally downloads the `Qwen3.5-4B` (`Q4_K_M`, 2.55 GiB) base model after verifying its Apache-2.0 license and SHA-256 digest. Desktop installer candidates (`.dmg`, `.exe`, `.AppImage`) also provide a first-run setup wizard that checks free disk space (at least 6 GiB) and RAM (at least 8 GiB) before any download begins.

## Step-by-step usage

1. **Three-command clean install (macOS & Linux):**
   ```bash
   git clone https://github.com/oddlyprovenai/spike.git && cd spike
   ./scripts/install.sh --yes               # add --no-model to skip the 2.7 GB weight download, or --dry-run to preview steps
   spike serve --open
   ```
2. **Three-command clean install (Windows PowerShell 5.1 or 7):**
   ```powershell
   git clone https://github.com/oddlyprovenai/spike.git; cd spike
   powershell -ExecutionPolicy Bypass -File scripts\install.ps1 -Yes   # add -NoModel or -DryRun as needed
   spike serve --open
   ```
3. **Preview without modifying anything:** run `./scripts/install.sh --dry-run` (or `scripts\install.ps1 -DryRun`) to inspect the chosen Python 3.11–3.13 interpreter, `pipx` environment, web bundle build, `llama-server` resolution, and `spike doctor --strict` check without writing files or downloading weights.
4. **Manual virtual environment setup (developers):** `python3 -m venv .venv && .venv/bin/pip install -e ".[dev,docs,finance,data,motion,keyring]"` and `cd web && npm ci && npm run build`.
5. Run `spike doctor` at any time to verify Python, `llama-server`, `~/.spike` storage, SHA-256 model manifests, and the secrets backend, then open `http://127.0.0.1:8740`.

## Real limits

- On a 16 GB x86 CPU-only machine (4 cores, AVX-512), `Qwen3.5-4B Q4_K_M` runs at **5.1–6.2 tok/s** up to an 8K prompt (52 s time-to-first-token at 1K; 773 s at 8K) using **3.6 GiB** of anonymous RAM (6.1 GiB peak RSS including the memory-mapped GGUF). A 32K prompt on 4 CPU cores takes ~1.5 h to the first token, so SPIKE starts CPU-only machines at an 8K context.
- On Apple Silicon M4 Max with Metal (`--gpu-layers 99`), generation runs at **80–82 tok/s** (0.86 s TTFT at 1K; 7.2 s at 8K) with 3.6 GiB RSS.
- Desktop installer candidates (`.dmg`, `.exe`, `.AppImage`) are tested on clean GitHub Actions runners (Windows Server 2022 and Ubuntu 24.04 with the real model; macOS runner with the tiny fixture because the free runner has 7.0 GiB RAM below the 8 GiB guard), are not published yet, and do not carry paid code-signing certificates; see [../../STATUS.md](../../STATUS.md).

## How to verify

- Preview the installer plan safely with `./scripts/install.sh --dry-run --no-model`.
- Run `.venv/bin/spike doctor` and confirm that environment checks pass.
- Run the offline installer, first-run wizard, and launcher test suites: `.venv/bin/python -m pytest -q tests/test_installers.py tests/test_install_u3.py tests/test_first_run_g23.py tests/test_launcher_setup.py tests/test_installer_smoke_g45.py`.
- Run the clean-room server smoke test without a model: `python scripts/installer_smoke.py --wheel dist/spike_ai-*.whl` (or `python scripts/installer_smoke.py --use-python .venv/bin/python` against an existing interpreter). It starts SPIKE on a free loopback port with isolated `SPIKE_HOME`, `HOME`, and `SPIKE_API_TOKEN`, checks `/api/health` and `/v1/models` (both authorized 200 and unauthorized 401), stops the server, removes the temp directory, and verifies that `~/.spike` was not touched.

### What the installer smoke test covers and what it does not

- It covers: the wheel contains a working server and static UI, a clean install starts, health and `/v1/models` respond, API token enforcement works, and cleanup leaves zero artifacts behind.
- It does not replace testing native installers on physical end-user desktops, does not test unsigned OS Gatekeeper/SmartScreen dialogs, and does not download or load LLM weights (`--no-local`).
