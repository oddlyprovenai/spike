<picture>
  <source media="(prefers-color-scheme: dark)" srcset="brand/github/readme-banner-dark.png">
  <img alt="SPIKE" src="brand/github/readme-banner-light.png">
</picture>

<p align="center">
  <b>A family of small specialist models with an orchestrator, built to run on an ordinary 16&nbsp;GB computer.</b><br>
  Local first · Apache-2.0 · OpenAI-compatible <code>/v1</code> and MCP · optional external API providers behind a privacy and spend guard
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
> **Project status: early and measured.** The web workspace, orchestrator, provider guard, `llama.cpp` runtime, and LoRA training/evaluation pipeline are built and verified in CI across Linux, macOS, and Windows. **13 specialists share one Qwen3.5-4B base; 1 specialist adapter (Medicine) has been accepted by its gate so far** (not published on Hugging Face yet). Finance rounds 1 and 2 were rejected for general-knowledge forgetting (`not accepted yet`). Until a specialist's adapter passes its pre-registered gate and is installed, it runs as a prompt profile on the base model and the UI marks it **β**. Evidence and the command behind every figure: [docs/STATUS.md](docs/STATUS.md).

<!-- DEMO_SLOT (task L1): the unedited real-time recording from web/e2e/demo.mjs with real weights goes here; see docs/DEMO.md. -->

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
4. **Local by default, external APIs only when you allow them.** Connect Ollama, LM Studio, OpenAI, Anthropic, Gemini, DeepSeek, Groq, Mistral, OpenRouter, or Together with the same specialists and tools: paid calls default to blocked, API keys stay in the OS keychain, and local file passages are withheld from remote providers unless explicitly permitted (tested against stand-in endpoints, not yet against live services).
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
| **Medicine · Round 1** (trained `2026-10-20`, `oasst2` replay, scale `1.0`) | `32.2% → 64.1%` (`+31.92` pts on `2,318` questions) | **`−7.62` pts** (`63.9% → 56.2%` on `800` MMLU-Pro items) | **REJECTED** — exceeded general-knowledge forgetting limit; lost persona framing in live probes. |
| **Medicine · Round 2** (accepted `2026-11-05`, self-replay 30%, LoRA scale `0.5` in GGUF) | `31.9% → 67.0%` (`+35.07` pts on `2,318` questions, `p < 1e-6`) | **`−0.62` pts** (`63.7% → 63.1%`, McNemar `p = 0.74`) | **ACCEPTED** (`spike-medicine-it13270-s0.5.gguf`, `42,485,024` bytes, SHA-256 `21caa0a0...`). **Scoring caveat (read before quoting `+35.07`):** on the original scorer, the base model left `409` of `1,000` MedMCQA answers and `241` of `818` MMLU-Pro health answers unparsed (counted as wrong vs `26` and `16` for the adapter), which likely inflates the raw delta; the saved answers are being re-scored with the newer answer extractor (`run_eval.py --rescore`) and the result will be published next to this one. Among readable answers only, MedMCQA is `0.467 → 0.660`; on PubMedQA (`0` unparsed base answers) accuracy rose `0.422 → 0.804` (`+38.20` pts). |
| **Finance · Rounds 1 & 2** (rejected `2026-11-09` & `2026-11-11`, 768- and 1536-token windows) | Selection gain cleared `+3.0` pts (`+5.17` in r1; `+7.00` in r2 at scale `0.5`) | **`−3.00` pts** (r1) and **`−2.75` pts** (r2) on `general-select` | **REJECTED** — Finance remains `not accepted yet` (β prompt profile); round 3 tests 45% self-replay. |
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

These tools do different jobs, and SPIKE is new. The table says what each one *is*; it does not rank quality or
speed. Cells about the others come from each project's own repository, docs or site, checked 2026-10-20 (sources
below). **"not checked"** means it was not looked up for this table, not that the feature is missing. The SPIKE column
follows [docs/STATUS.md](docs/STATUS.md).

| | SPIKE | Ollama | LM Studio | Open WebUI | Jan |
|---|---|---|---|---|---|
| Code license | Apache-2.0 | MIT | Proprietary app, free to use at home and at work; its CLI, SDKs and MLX engine are MIT | Own license since v0.6.6: a branding clause on top of BSD-3-style terms (its docs: not OSI-approved); BSD-3 up to v0.6.5 | Apache-2.0 |
| Runs models on your computer | Yes, through llama.cpp | Yes (cloud models are optional) | Yes, llama.cpp; MLX on Apple Silicon | Connects to Ollama and OpenAI-compatible servers that run the models | Yes, llama.cpp |
| Models you get | Downloads one base, Qwen3.5-4B (SHA-256 checked). One specialist adapter (Medicine) accepted, not published yet | A library of many open models from other makers | A catalog of other makers' models (56 listed, 47 local) and Hugging Face search | Whatever its connected servers offer | Downloads models from Hugging Face |
| Routes a request to a specialist by itself | Yes: lexical router plus a planner for multi-domain requests; specialists are prompt profiles for now | not checked | not checked | Not described in its feature docs; you pick a model or a preset | not checked |
| OpenAI-compatible API | Yes: `/v1` with `spike-auto` or one specialist; tested with the official `openai` client | Yes, a subset: chat completions, responses, completions, embeddings, models | Yes: responses, chat completions, completions, embeddings, models | Its own API has an OpenAI-compatible chat completions endpoint | Yes: local server at `127.0.0.1:1337/v1` |
| MCP | Client (stdio, Streamable HTTP) and server; tested with the official MCP SDK, not with Claude Code, Cursor or Codex | Client not checked; its docs offer a web-search MCP server for other clients | MCP host since 0.3.17 | Native since v0.6.31, Streamable HTTP only (stdio via the mcpo proxy) | Supported; needs a model with tool calling |
| GPU backends | CPU and Metal measured; no other GPU backend tested | NVIDIA CUDA, AMD ROCm, Apple Metal, Vulkan | Apple Silicon on macOS; 4 GB+ VRAM recommended on Windows; the rest not checked | Left to the server it connects to | CUDA (NVIDIA), Vulkan (AMD, Intel), Metal |
| Several users | No accounts or roles: built for one person on one computer | not checked | not checked | Yes: roles, groups, per-resource permissions | not checked |

Sources, all checked 2026-10-20:

- **Ollama**: [LICENSE](https://github.com/ollama/ollama/blob/main/LICENSE) (MIT), [quickstart](https://docs.ollama.com/quickstart) and [FAQ](https://docs.ollama.com/faq) (runs locally), [model library](https://ollama.com/library), [OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility), [hardware support](https://docs.ollama.com/gpu), [web search (MCP server)](https://docs.ollama.com/capabilities/web-search), [docs index](https://docs.ollama.com/llms.txt).
- **LM Studio**: [terms](https://lmstudio.ai/terms) (proprietary software), [free for work](https://lmstudio.ai/blog/free-for-work), [GitHub organization](https://github.com/lmstudio-ai) (MIT repositories), [docs home](https://lmstudio.ai/docs/app) (llama.cpp, MLX), [model catalog](https://lmstudio.ai/models), [OpenAI compatibility](https://lmstudio.ai/docs/developer/openai-compat), [MCP](https://lmstudio.ai/docs/app/mcp), [system requirements](https://lmstudio.ai/docs/app/system-requirements).
- **Open WebUI**: [LICENSE](https://github.com/open-webui/open-webui/blob/main/LICENSE), [license page](https://docs.openwebui.com/license/), [README](https://github.com/open-webui/open-webui) (connects to Ollama and OpenAI-compatible APIs, roles and groups), [getting started](https://docs.openwebui.com/getting-started/), [features](https://docs.openwebui.com/features/), [API endpoints](https://docs.openwebui.com/getting-started/api-endpoints), [MCP](https://docs.openwebui.com/features/extensibility/mcp).
- **Jan**: [LICENSE](https://github.com/janhq/jan/blob/main/LICENSE) and [README](https://github.com/janhq/jan) (Apache-2.0, Hugging Face models, local server), [API server](https://docs.jan.ai/desktop/api-server), [MCP](https://www.jan.ai/docs/desktop/mcp), [local engine](https://docs.jan.ai/desktop/llama-cpp) (llama.cpp, CUDA, Vulkan, Metal).

What they do that SPIKE does not:

- **Ollama** offers a library of many models where SPIKE offers one base, documents four GPU backends, and lists many
  integrations. SPIKE can point at an Ollama server as an OpenAI-compatible provider (not tried against the real product).
- **LM Studio** is a desktop app with an in-app model catalog, a CLI, SDKs and a headless mode (`llmster`).
- **Open WebUI** describes itself as multi-user, with roles and groups, document search (RAG) and a model arena.
  SPIKE is one person on one computer.
- **Jan** is a desktop app with installers for Windows, macOS and Linux. SPIKE runs as a local Python server plus
  llama.cpp with script installers (`scripts/`) and unsigned native installer candidates (`.dmg`, `.exe`, `.AppImage`
  in `packaging/`, tested on clean GitHub runners; not published or code-signed yet).
- **SPIKE is new**: it has the measurements in this repository and no track record yet.

Not claimed here: that SPIKE answers better than any of them (only Medicine has an accepted verdict, and it is
measured against its own base model, not against these apps), or that it is faster (the others were not benchmarked). SPIKE's bet is a
router and specialists on one small model that fits a CPU-only 16 GB computer, with numbers published next to the
command that reproduces them.

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
