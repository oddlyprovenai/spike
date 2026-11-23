<picture>
  <source media="(prefers-color-scheme: dark)" srcset="brand/github/readme-banner-dark.png">
  <img alt="SPIKE" src="brand/github/readme-banner-light.png">
</picture>

<p align="center">
  <b>13 domain specialists sharing one 4B base model and a zero-cost router, built to run on an ordinary 16&nbsp;GB computer.</b><br>
  Local-first · Apache-2.0 · OpenAI-compatible <code>/v1</code> &amp; MCP · Optional external API providers behind a strict privacy &amp; spend guard
</p>

<p align="center">
  <a href="#install-in-3-commands">Quick Install</a> ·
  <a href="#why-spike">Why SPIKE</a> ·
  <a href="#thirteen-specialists-one-base-model">Specialists</a> ·
  <a href="#measured-hardware--adapter-receipts">Lab Receipts</a> ·
  <a href="#spike-next-to-ollama-lm-studio-open-webui-and-jan">Comparison</a> ·
  <a href="docs/guide/README.md">User Guide (EN/ES)</a> ·
  <a href="docs/STATUS.md">Full Status Log</a>
</p>

---

> [!IMPORTANT]
> **Project status: early, measured, and radically honest.** The web workspace, orchestrator, provider guard, `llama.cpp` runtime, and LoRA training/evaluation pipeline are built and verified in CI across Linux, macOS, and Windows. **13 specialists share one Qwen3.5-4B base; 1 specialist adapter (Medicine) has been accepted by its gate so far** (not published on Hugging Face yet). Finance rounds 1 and 2 were rejected for general-knowledge forgetting (`not accepted yet`). Until a specialist's adapter passes its pre-registered gate and is installed, it runs as a prompt profile on the base model and the UI marks it **β**. Every figure below links to the record and command that produced it: [docs/STATUS.md](docs/STATUS.md).

<!-- CLAUDE_DEMO_PLACEHOLDER_START: replace this block with the real-time 30-60s recording produced by `node web/e2e/demo.mjs` against real Qwen3.5-4B weights (task L1, see docs/DEMO.md). Never substitute a scripted/fake capture. -->
> **Demo recording (`v0.1` capture slot — pending real-weight run `L1`):**
> _Placeholder for Claude:_ insert `docs/assets/demo-v0.1.gif` (and `<video>` MP4 link) recorded unedited in real time via [`web/e2e/demo.mjs`](docs/DEMO.md) with `Qwen3.5-4B-Q4_K_M.gguf`, captioned from `demo.json` with exact hardware, time to router chip, time to first token, and streaming tok/s.
<!-- CLAUDE_DEMO_PLACEHOLDER_END -->

## Install in 3 commands

Requirements: Python 3.11+, Node.js 18+ (when building from source), ~3 GB disk for the default quantized model (`Qwen3.5-4B` `Q4_K_M`), 16 GB RAM recommended (`--no-model` skips the 2.74 GB download if you only want external API providers or a dry-run check).

```bash
git clone https://github.com/oddlyprovenai/spike.git && cd spike
./scripts/install.sh --yes               # Windows PowerShell: .\scripts\install.ps1 -Yes  (add --no-model / -NoModel to skip weights)
spike serve --open                       # opens http://127.0.0.1:8740
```

Prefer running each step manually?

```bash
git clone https://github.com/oddlyprovenai/spike.git && cd spike
(cd web && npm ci && npm run build) && pipx install ".[docs,finance,data,motion]"  # builds UI and installs isolated CLI
brew install llama.cpp                   # macOS / Linux with Homebrew; Linux without brew: ./scripts/install.sh fetches pinned b11709
spike doctor                             # inspects RAM, CPU/GPU, context budget, and verified model manifests
spike models pull qwen3.5-4b             # Q4_K_M by default; Hub license and SHA-256 verified before saving
spike serve --open                       # app at http://127.0.0.1:8740
```

Unsigned one-click desktop installer candidates (`.dmg` for macOS Apple Silicon, `.exe` for Windows x64, `.AppImage` for Linux x86_64) are built in CI ([`packaging/README.md`](packaging/README.md)) and tested on clean GitHub runners; public release artifacts wait for `v0.1.0`.

---

## Why SPIKE

1. **Fits an ordinary 16 GB computer without a GPU.** One `Qwen3.5-4B` (`Q4_K_M`) base model ran on a 4-core 16 GB CPU-only x86 VM at `5.1–6.2 tok/s` up to an 8K prompt in `3.6 GiB` of anonymous memory (`6.1 GiB` peak RSS including the memory-mapped model file) — and we publish the slow 32K numbers too.
2. **13 specialists, zero model-reload penalty.** Core, Code, Finance, Medicine, Law, Marketing, Science, Data, Math, Education, Writing, Business, and Security share one base model in memory and hot-swap `~42 MB` LoRA adapters (computed at rank 16) per request.
3. **Zero-cost routing before spending tokens.** A ~1 ms lexical router (`~3,850` EN/ES domain terms) dispatches clear single-domain prompts without an LLM call (`116/130 = 0.89`, Wilson 95% CI `0.83–0.93`, on a blind holdout written without seeing the keywords); only multi-domain or ambiguous requests invoke a schema-validated DAG plan.
4. **Local by default, external APIs only behind a firewall you control.** Connect Ollama, LM Studio, OpenAI, Anthropic, Gemini, DeepSeek, Groq, Mistral, OpenRouter, or Together with the same specialists and tools: paid calls default to blocked, API keys stay in the OS keychain, and local file passages are withheld from remote providers unless explicitly permitted.
5. **Lab receipts, including our own rejections.** Every adapter has pre-written acceptance gates (`>= +3.0 pts` domain gain at `p <= 0.05` AND `<= 1.5 pts` general-knowledge drop): we rejected our own Medicine v1 (`−7.62 pts` general drop) and Finance rounds 1 and 2, fixed Medicine in round 2, and publish every verdict in [`docs/results/specialists.json`](docs/results/specialists.json).

---

## Thirteen specialists, one base model

<table>
  <tr>
    <td align="center"><img src="brand/specialists/core/avatar-core-128.png" width="56" alt="Spike Core avatar"><br><b>Core</b><br><sub>Base</sub></td>
    <td align="center"><img src="brand/specialists/medicine/avatar-medicine-128.png" width="56" alt="Spike Medicine avatar"><br><b>Medicine</b><br><sub>Accepted</sub></td>
    <td align="center"><img src="brand/specialists/code/avatar-code-128.png" width="56" alt="Spike Code avatar"><br><b>Code</b><br><sub>β profile</sub></td>
    <td align="center"><img src="brand/specialists/finance/avatar-finance-128.png" width="56" alt="Spike Finance avatar"><br><b>Finance</b><br><sub>β profile</sub></td>
    <td align="center"><img src="brand/specialists/law/avatar-law-128.png" width="56" alt="Spike Law avatar"><br><b>Law</b><br><sub>β profile</sub></td>
    <td align="center"><img src="brand/specialists/marketing/avatar-marketing-128.png" width="56" alt="Spike Marketing avatar"><br><b>Marketing</b><br><sub>β profile</sub></td>
    <td align="center"><img src="brand/specialists/science/avatar-science-128.png" width="56" alt="Spike Science avatar"><br><b>Science</b><br><sub>β profile</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="brand/specialists/data/avatar-data-128.png" width="56" alt="Spike Data avatar"><br><b>Data</b><br><sub>β profile</sub></td>
    <td align="center"><img src="brand/specialists/math/avatar-math-128.png" width="56" alt="Spike Math avatar"><br><b>Math</b><br><sub>β profile</sub></td>
    <td align="center"><img src="brand/specialists/education/avatar-education-128.png" width="56" alt="Spike Education avatar"><br><b>Education</b><br><sub>β profile</sub></td>
    <td align="center"><img src="brand/specialists/writing/avatar-writing-128.png" width="56" alt="Spike Writing avatar"><br><b>Writing</b><br><sub>β profile</sub></td>
    <td align="center"><img src="brand/specialists/business/avatar-business-128.png" width="56" alt="Spike Business avatar"><br><b>Business</b><br><sub>β profile</sub></td>
    <td align="center"><img src="brand/specialists/security/avatar-security-128.png" width="56" alt="Spike Security avatar"><br><b>Security</b><br><sub>β profile</sub></td>
    <td align="center"><sub>13 roles<br>1 accepted<br>12 β profiles</sub></td>
  </tr>
</table>

Scope, audited training sources, decontamination rules, and evaluation suites for each specialist: [docs/SPECIALISTS.md](docs/SPECIALISTS.md). Settings → Specialists verifies any installed `.gguf` adapter by SHA-256 against [`spike/specialists/acceptance/`](spike/specialists/acceptance/) so an unverified file is never presented as accepted.

---

## Measured hardware & adapter receipts

### 1. Speed and memory (`spike bench`, real `Qwen3.5-4B` `Q4_K_M` weights)

`llama.cpp`, `q8_0` KV cache, 128 generated tokens, median of 3 runs ([raw JSON records](docs/STATUS.md#measured-with-real-weights)):

| Machine | Prompt | Time to first word | Generation | Memory footprint |
|---|---|---|---|---|
| **16 GB x86, 4 cores, CPU only** (`b11709-62318cd57`) | 1K tokens | 52 s | 6.2 tok/s | 3.6 GiB anonymous, 6.1 GiB RSS with the mapped model file |
| | 8K tokens | 13 min | 5.1 tok/s | 3.6 GiB anonymous, 6.1 GiB RSS |
| **Apple M4 Max (36 GB), Metal** (`--gpu-layers 99`) | 1K tokens | 0.9 s | 82 tok/s | 3.6 GiB RSS |
| | 8K tokens | 7.2 s | 80 tok/s | 3.6 GiB RSS |

_Why CPU-only defaults to an 8K context:_ at 32K tokens on the 4-core CPU VM, anonymous RAM stayed flat (`3.6 GiB`), but prompt prefill took ~1.5 hours (`5,566 s`) at `2.1 tok/s`. `spike tune` benchmarks thread counts and `f16` vs `q8_0` KV cache on your own machine and saves the faster setting.

### 2. Specialist training & gate verdicts ("We rejected our own medical AI. Then we fixed it.")

| Specialist & Round | Domain Result | General-Knowledge Drift (limit `−1.50` pts) | Gate Verdict & Caveats |
|---|---|---|---|
| **Medicine · Round 1** (`2026-10-20`, `oasst2` replay, scale `1.0`) | `32.2% → 64.1%` (`+31.92` pts on `2,318` questions) | **`−7.62` pts** (`63.9% → 56.2%` on `800` MMLU-Pro items) | **REJECTED** — exceeded general-knowledge forgetting limit; lost persona framing in live probes. |
| **Medicine · Round 2** (`2026-11-05`, self-replay 30%, LoRA scale `0.5` in GGUF) | `31.9% → 67.0%` (`+35.07` pts on `2,318` questions, `p < 1e-6`) | **`−0.62` pts** (`63.7% → 63.1%`, McNemar `p = 0.74`) | **ACCEPTED** (`spike-medicine-it13270-s0.5.gguf`, `42,485,024` bytes, SHA-256 `21caa0a0...`). **Scoring caveat (read before quoting `+35.07`):** on the original scorer, the base model left `409` of `1,000` MedMCQA answers and `241` of `818` MMLU-Pro health answers unparsed (counted as wrong vs `26` and `16` for the adapter), which inflates the raw delta until `run_eval.py --rescore` is committed on `main`. Among readable answers only, MedMCQA is `0.467 → 0.660`; on PubMedQA (`0` unparsed base answers) accuracy rose `0.422 → 0.804` (`+38.20` pts). |
| **Finance · Rounds 1 & 2** (`2026-11-09` & `2026-11-11`, 768 & 1536 window) | Selection gain cleared `+3.0` pts (`+5.17` in r1; `+7.00` in r2 at scale `0.5`) | **`−3.00` pts** (r1) and **`−2.75` pts** (r2) on `general-select` | **REJECTED** — Finance remains `not accepted yet` (β prompt profile); round 3 tests 45% self-replay. |
| **Lexical Router (`M9`)** | `116/130 = 0.89` (Wilson 95% CI `0.83–0.93`) | ~1 ms per route, zero model calls | **MEASURED** on `evals/data/router_holdout.jsonl` (130 EN/ES prompts written blind without keyword access; `48/50 = 0.96` on original test split). Real-user traffic not measured yet. |

---

## What ships in the workspace

- **Chat, Projects & Isolated Artifacts:** Per-project instructions, default specialist, scoped files, project branches with diff review, temporary zero-disk chats, HTML/SVG sandboxed previews (`connect-src 'none'`), and Word/Excel/PowerPoint/PDF generation with one-click undo (`$SPIKE_HOME/checkpoints`).
- **Local Neural Memory:** SQLite hybrid recall (FTS5 BM25 + embeddings via reciprocal rank fusion), opt-in local folder indexing (symlinks escaping the folder refused), bilingual glossary, Education spaced-repetition tutor (SM-2), and deterministic entity graphs.
- **Data, Finance & Media Studios:**
  - **Spike Data:** Read-only locked DuckDB (`SUMMARIZE`, `data_sql`, `SQL Guardian`), CSV rescue, data contracts, baseline backtested forecasts, and offline Vega-Lite charts exported to HTML/Word/PDF.
  - **Spike Finance:** Public market history (`ccxt`), fee/slippage backtester vs buy-and-hold, historical VaR/drawdown, and paper trading. Live exchange orders are **locked off by default** and never exposed to `/v1` or MCP callers.
  - **Spike Design & Motion:** 21 bundled `DESIGN.md` + `tokens.css` systems (zero third-party company look-alikes) and deterministic virtual-clock HTML/SVG-to-MP4/WebM/GIF rendering (`spike render`).
- **Terminal & In-App Coding Agent (`spike dev`):** Read-only `/plan` mode and approval-gated `/act` mode (`edit_file`, `search`, `find_files`, `run_command`, `/undo`, `--sessions`, `--resume`), isolated with `sandbox-exec` (macOS) or `bwrap` (Linux) for model-written Python ([guide](docs/DEV-WORKFLOW.md)).
- **Agent Skills, MCP Apps & Ecosystem:** 30 validated `SKILL.md` packages, MCP client (stdio + Streamable HTTP) supporting isolated `ui://` MCP Apps (`SEP-1865`), MCP server (`spike mcp`), OpenAI-compatible `/v1` server ([integrations](docs/INTEGRATIONS.md)), Trustworthy Answers citation verifier, and local Evolution (`spike evolve`).

---

## SPIKE next to Ollama, LM Studio, Open WebUI and Jan

These tools solve different slices of the local-AI stack, and SPIKE is the newcomer. The table describes documented architecture and licensing — it does **not** claim quality or speed wins (we have not benchmarked the other four tools). External columns were verified against each project's official repository and documentation on `2026-11-18`; `"not checked"` means not audited for this table, not absent.

| Dimension | SPIKE | Ollama | LM Studio | Open WebUI | Jan |
|---|---|---|---|---|---|
| **License** | **Apache-2.0** | **MIT** | **Proprietary desktop app** (free for personal & workplace use without forms); CLI (`lms`), SDKs & MLX engine are **MIT** | **Custom license since `v0.6.6`** (BSD-3 base + branding preservation clause above 50 active monthly users; not OSI-approved; `<= v0.6.5` BSD-3) | **Apache-2.0** |
| **Local inference engine** | Yes (`llama.cpp` `llama-server`) | Yes (native Go/GGML daemon + optional cloud models) | Yes (`llama.cpp` + Apple `MLX` on Apple Silicon) | Frontend/orchestrator that connects to Ollama or OpenAI-compatible servers | Yes (bundled `llama.cpp` + Apple Silicon support; external endpoints optional) |
| **Model strategy** | One SHA-256-verified `Qwen3.5-4B` base + hot-swapped specialist LoRA adapters (1 accepted so far, 12 β profiles) + external APIs | Broad library of open-weight models (`ollama pull`) | Curated catalog + direct Hugging Face GGUF/MLX search | Uses models exposed by connected local or cloud backends | Downloads GGUF models from Hugging Face + cloud API keys |
| **Built-in domain routing** | Yes: ~1 ms lexical router (`0.89` blind holdout) + multi-specialist DAG planner | Not built into daemon; single model per API call | Manual/SDK model selection | User selects model, preset, or pipe | Manual/assistant model selection |
| **OpenAI-compatible API** | Yes: `127.0.0.1:8740/v1` (`spike-auto` or `spike-<specialist>`, tested with `openai` Python SDK) | Yes: `localhost:11434/v1` (chat completions, responses, completions, embeddings, models) | Yes: local server with chat completions, responses, completions, embeddings, models | Yes: OpenAI-compatible chat completions proxy endpoint | Yes: local API server (`127.0.0.1:1337/v1`) with trusted-host checks |
| **MCP support** | **Client** (stdio + Streamable HTTP + `SEP-1865` MCP Apps UI) **and Server** (`spike mcp` / `/mcp`) | Native tool/function calling; MCP via ecosystem clients/bridges + web-search MCP server | **MCP Host** (`mcp.json` since `0.3.17`) | **Native Streamable HTTP MCP** (`v0.6.31+`; stdio via `mcpo` proxy) | **MCP Host** with inline tool approvals |
| **GPU backends** | CPU-only (x86/ARM) and Apple Metal measured; other GPUs not tested yet | NVIDIA CUDA, AMD ROCm, Apple Metal, Vulkan, CPU | Apple Metal/MLX, NVIDIA CUDA, AMD/Vulkan on Windows/Linux | Delegated to connected inference server | NVIDIA CUDA, Vulkan (AMD/Intel), Apple Metal, CPU |
| **Multi-user & RBAC** | Single-user on `127.0.0.1` by design | Local daemon (no user accounts) | Single-user desktop / `llmster` headless server | **Yes:** multi-user accounts, roles, groups, per-resource permissions | Single-user desktop app |

**Sources (verified `2026-11-18`):**
- **Ollama:** [LICENSE](https://github.com/ollama/ollama/blob/main/LICENSE) · [Docs Home](https://docs.ollama.com) · [OpenAI Compatibility](https://docs.ollama.com/api/openai-compatibility) · [GPU Support](https://docs.ollama.com/gpu) · [Model Library](https://ollama.com/library) · [Web Search MCP](https://docs.ollama.com/capabilities/web-search)
- **LM Studio:** [Docs](https://lmstudio.ai/docs/app) · [Free for Work Policy](https://lmstudio.ai/blog/free-for-work) · [Terms](https://lmstudio.ai/terms) · [OpenAI Compatibility](https://lmstudio.ai/docs/developer/openai-compat) · [MCP Host](https://lmstudio.ai/docs/app/mcp) · [GitHub (MIT SDKs/CLI)](https://github.com/lmstudio-ai)
- **Open WebUI:** [Docs](https://docs.openwebui.com) · [License & Branding FAQ](https://docs.openwebui.com/license/) · [Repository LICENSE](https://github.com/open-webui/open-webui/blob/main/LICENSE) · [Features](https://docs.openwebui.com/features/) · [MCP Documentation](https://docs.openwebui.com/features/extensibility/mcp)
- **Jan:** [Docs](https://docs.jan.ai) · [Repository & Apache-2.0 LICENSE](https://github.com/janhq/jan/blob/main/LICENSE) · [Local API Server](https://docs.jan.ai/desktop/api-server) · [llama.cpp Engine](https://docs.jan.ai/desktop/llama-cpp) · [MCP Integration](https://www.jan.ai/docs/desktop/mcp)

**Where those projects are ahead of SPIKE today:**
- **Ollama** supports dozens of model families and tested CUDA/ROCm/Vulkan GPU backends out of the box (and SPIKE can use an Ollama daemon as a local provider).
- **LM Studio** ships a mature signed desktop app, native Apple `MLX` runtime, `lms` CLI, Python/TS SDKs, and `llmster` headless mode.
- **Open WebUI** provides multi-user RBAC, admin governance, and team deployments; SPIKE is intentionally built for one person on one machine.
- **Jan** distributes signed cross-platform desktop installers with a bundled engine; SPIKE's native installers (`.dmg`, `.exe`, `.AppImage`) are unsigned release candidates today.

---

## Documentation

| Document | Contents |
|---|---|
| [User Guide (EN / ES)](docs/guide/README.md) | Step-by-step guides for every module, CLI reference, FAQ & `spike doctor` troubleshooting |
| [API Reference (EN / ES)](docs/api/README.md) | Every HTTP & SSE endpoint with parameters, error codes, and `curl` examples |
| [Architecture](docs/ARCHITECTURE.md) | Orchestrator, router, providers, Neural Memory, sandbox, and Trustworthy Answers |
| [Specialists](docs/SPECIALISTS.md) | Domain scope, audited datasets, decontamination, evaluation gates, and risks |
| [Training](docs/TRAINING.md) | Train, sweep against forgetting, export to GGUF, and evaluate on Apple Silicon |
| [Integrations](docs/INTEGRATIONS.md) | Connect Aider, Continue, OpenCode, Claude Code, Cursor, or OpenAI SDKs |
| [Compatibility](docs/COMPATIBILITY.md) | CI-verified OS/Python matrix and measured hardware table |
| [Status Log](docs/STATUS.md) | Complete ledger of verified features, real-weight benchmarks, rejections, and blockers |
| [Architecture Decisions](docs/adr/) | ADRs covering base model choice, bf16 LoRA, orchestration, and per-request LoRA serving |

---

## Development & Verification

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev,docs,finance,data,motion,keyring]"
ruff check .
pytest -q
cd web && npm ci && npx vitest run && npm run build
```

Contributions follow a strict **test-first, evidence-first** workflow (`no new claim without a reproducing command`): [CONTRIBUTING.md](CONTRIBUTING.md). Security policy and vulnerability reporting: [SECURITY.md](SECURITY.md).

## License & Disclaimers

Code: [Apache-2.0](LICENSE). Base model (`Qwen/Qwen3.5-4B`): Apache-2.0. Datasets, fonts, bundled skills, and third-party libraries retain their upstream licenses documented in [THIRD_PARTY.md](THIRD_PARTY.md) and [NOTICE](NOTICE). The SPIKE name and cactus mark are the project's identity ([brand/](brand/)).

SPIKE's sensitive specialists (**Medicine, Finance, Law, Security**) provide general technical information only — they are **not professional medical, financial, legal, or security advice**, and SPIKE is **not a medical device**.
