---
license: apache-2.0
base_model: Qwen/Qwen3.5-4B
language:
- en
- es
pipeline_tag: text-generation
tags:
- spike
- lora
- gguf
- medicine
datasets:
- OpenAssistant/oasst2
- openlifescienceai/medmcqa
- qiaojin/PubMedQA
---

<!-- Draft Hugging Face Model Card for spike-medicine (not published yet; awaits M16 rescore & owner approval L3).
     When staged into the Hugging Face repository folder by `training/model_card.py`, the banner path becomes `banner.png`. -->

![Spike Medicine](../../brand/specialists/medicine/hf-banner-medicine.png)

# Spike Medicine (`spike-medicine-it13270-s0.5.gguf`)

GGUF LoRA adapter for [Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) (`Q4_K_M`, `llama.cpp`) that serves as SPIKE's medical-knowledge specialist across clinical reasoning, pharmacology, physiology, diagnostics, and evidence-based medicine.

**Accepted by its pre-registered acceptance criteria on `2026-11-05`** (criteria written before training; Round 1 was rejected for general-knowledge forgetting and replaced by Round 2).

> **Important Scoring & Rescoring Caveat (Read Before Quoting Headline Deltas):**
> On the acceptance evaluation run (`d41e89a` choice extractor), the base model (`Qwen3.5-4B-Q4_K_M.gguf`) produced **no parseable option letter on `409` of `1,000` MedMCQA validation questions** and **`241` of `818` MMLU-Pro health questions** (often ending with a clinical disclaimer or writing the option's text rather than its letter), whereas this adapter left `26` and `16` unparsed (`650` vs `43` pooled across all `2,318` medical items). Because unparsed answers count as wrong under exact-answer scoring, **part of the raw `+35.07` point pooled gain (`0.319 -> 0.670`) comes from answer-format compliance and is likely inflated** until the saved base and adapter predictions are re-scored side by side with SPIKE's updated `M14` answer extractor (`evals/run_eval.py --rescore`).
>
> - **Accuracy among readable answers only** (computed from the run's counts): MedMCQA validation `0.467` (base) vs `0.660` (adapter); MMLU-Pro health `0.439` (base) vs `0.633` (adapter); pooled medicine `0.444` (base) vs `0.683` (adapter).
> - **PubMedQA labeled (`500` items, `0` unparsed base answers):** base `0.422` -> adapter `0.804` (**`+38.20` pts**, `p < 1e-6`), unaffected by option-letter unparsed rates.

> **Safety Notice:** Spike Medicine provides general educational and technical information only. It is **not professional clinical or medical advice**, has **not** been evaluated for clinical safety or real patient care, and is **not a medical device**.

---

## Artifact Verification

| Field | Value |
|---|---|
| Exported file | `spike-medicine-it13270-s0.5.gguf` |
| Installed path in SPIKE | `~/.spike/adapters/spike-medicine.gguf` |
| Size | `42,485,024` bytes (~40.5 MiB) |
| SHA-256 | `21caa0a0b24bdd4d5badb5bc1f336d2eb3061a635400a85a15f4cf52f9d40a34` |
| Effective LoRA scale | `0.5` baked into GGUF `alpha` (`16.0` at rank `16`), loaded at runtime scale `1.0` |
| Receipt in SPIKE repo | [medicine.json](../../spike/specialists/acceptance/medicine.json) |

---

## Use

### In SPIKE
Save the verified file as `~/.spike/adapters/spike-medicine.gguf`. SPIKE loads it alongside `Qwen3.5-4B-Q4_K_M.gguf` without reloading the base weights, routes medical queries to it automatically, and checks its SHA-256 digest in **Settings → Specialists** against the embedded acceptance receipt.

### With `llama.cpp` directly
```bash
llama-server -m Qwen3.5-4B-Q4_K_M.gguf --lora spike-medicine-it13270-s0.5.gguf
```

---

## Training Recipe & Anti-Forgetting History

- **Method:** bf16 LoRA (`mlx-lm` with SPIKE's chunked differentiable Gated DeltaNet rule), rank `16`, initial `alpha` `32` (`scale 2.0`), exported at checkpoint-sweep scale `0.5` (`alpha 16.0`) on `self_attn.q_proj`, `self_attn.k_proj`, `self_attn.v_proj`, `self_attn.o_proj`, `mlp.gate_proj`, `mlp.up_proj`, `mlp.down_proj`; prompt tokens masked (`mask_prompt: true`).
- **Schedule (Round 2, git commit `00a0090640`):** `13,270` micro-batches (`batch_size: 1`, `grad_accumulation_steps: 16`, effective batch `16`), cosine learning-rate decay from `1e-4` to `1e-5` (`100` warmup steps), `max_seq_length: 768` (longer examples dropped rather than truncated), `seed: 0`.
- **Training mix (`13,270` train / `270` valid chats):**
  - `9,478` medical domain chats sampled (`prepare.py --fit-domain`) from filtered `openlifescienceai/medmcqa` (explanations >= 40 chars, single-answer items) and `qiaojin/PubMedQA` (`pqa_artificial`).
  - `30%` anti-forgetting general replay (`4,062` chats) generated from the **base model's own greedy answers** (`training/self_replay.py`) on human-written `OpenAssistant/oasst2` prompts under the specialist system prompt.
  - Strict 13-gram decontamination against all evaluation sets (`medmcqa` validation, `PubMedQA` `pqa_labeled`, `TIGER-Lab/MMLU-Pro`). Zero outputs from proprietary or competing models (Claude, GPT, Gemini, Llama) were used.
- **Why Round 1 was rejected (`2026-10-20`):** Round 1 (`25,469` steps, human `oasst2` replay without specialist prompt, LoRA scale `1.0`) gained `+31.92` pts on medicine (`0.322 -> 0.641`) but lost **`-7.62` pts** on `general` (`0.639 -> 0.562`, max allowed drop `1.5` pts) and dropped its safety framing in live probes, so it was rejected by its gate. In Round 2, combining self-replay (`30%`) with checkpoint-scale selection on disjoint `*-select` suites (`spike-medicine-it13270-s0.5`: `+33.83` pts on `medicine-select`, `0.00` pts drop on `general-select`) eliminated the general-knowledge regression.

### Datasets & Licenses

| Dataset | License | Role |
|---|---|---|
| [openlifescienceai/medmcqa](https://huggingface.co/datasets/openlifescienceai/medmcqa) | `apache-2.0` | Training (train split with explanations) & evaluation (`validation` split, `n = 1,000`) |
| [qiaojin/PubMedQA](https://huggingface.co/datasets/qiaojin/PubMedQA) | `mit` | Training (`pqa_artificial`) & evaluation (`pqa_labeled`, `n = 500`) |
| [OpenAssistant/oasst2](https://huggingface.co/datasets/OpenAssistant/oasst2) | `apache-2.0` | Human-written prompt trees for base-model self-replay (`30%` of training mix) |
| [TIGER-Lab/MMLU-Pro](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro) | `mit` | Evaluation and decontamination only (`health` `n = 818`; `general` `n = 800`) |

---

## Evaluation (`training/runs/medicine/sweep/final/summary.json`)

Protocol: `Qwen3.5-4B-Q4_K_M.gguf`, `llama.cpp` `b11669-620d2225c`, greedy decoding, `thinking: false`, `max_tokens: 2048`, `kv_cache_type: q8_0`, zero-shot with specialist system prompt, paired Wilson 95% CIs and exact McNemar test.

| Task / Suite | Variant | n | Accuracy | 95% CI | Delta vs base (pts) | McNemar p | Unparsed | Truncated |
|---|---|---:|---:|---|---:|---:|---:|---:|
| `medmcqa-val` | `base` | 1,000 | 0.276 | 0.249–0.304 | — | — | **409** | 24 |
| `medmcqa-val` | `spike-medicine-it13270-s0.5` | 1,000 | 0.643 | 0.613–0.672 | +36.70 | < 1e-6 | 26 | 34 |
| `pubmedqa-labeled` | `base` | 500 | 0.422 | 0.380–0.466 | — | — | 0 | 1 |
| `pubmedqa-labeled` | `spike-medicine-it13270-s0.5` | 500 | 0.804 | 0.767–0.836 | +38.20 | < 1e-6 | 1 | 1 |
| `mmlu-pro-health` | `base` | 818 | 0.309 | 0.279–0.342 | — | — | **241** | 27 |
| `mmlu-pro-health` | `spike-medicine-it13270-s0.5` | 818 | 0.621 | 0.587–0.654 | +31.17 | < 1e-6 | 16 | 31 |
| **`medicine` (pooled)** | `base` | 2,318 | 0.319 | 0.301–0.339 | — | — | **650** | 52 |
| **`medicine` (pooled)** | `spike-medicine-it13270-s0.5` | 2,318 | 0.670 | 0.651–0.689 | **+35.07** | < 1e-6 | 43 | 66 |
| **`general` (pooled)** | `base` | 800 | 0.637 | 0.604–0.670 | — | — | 10 | 37 |
| **`general` (pooled)** | `spike-medicine-it13270-s0.5` | 800 | 0.631 | 0.597–0.664 | **-0.62** | 0.7433 | 1 | 26 |

**Pre-registered gate verdict: ACCEPTED**
- Primary (`medicine`): `+35.07` pts (required `>= +3.0` pts, `p <= 0.05`) — **pass** (and `+38.20` pts on `pubmedqa-labeled` where `0` base answers were unparsed).
- Regression (`general`): `-0.62` pts (max allowed drop `1.5` pts) — **pass**.

---

## Limitations

- **English multiple-choice exam benchmarks only:** MedMCQA reflects Indian postgraduate medical entrance exams, PubMedQA tests abstract yes/no/maybe reasoning, and MMLU-Pro health is multiple choice. Accuracy on exam questions does **not** measure clinical safety, diagnostic reliability, or open-ended medical dialogue.
- **Spanish & live-probe evaluation not measured yet:** although `Qwen3.5-4B` and SPIKE's router support Spanish and English, all three acceptance benchmarks above are in English, and Round 2 live persona/disclaimer probes have not been formally scored yet.
- **Pending rescore (`M16`):** an updated card revision will add the side-by-side `evals/run_eval.py --rescore` table once the saved base and adapter predictions are re-read with SPIKE's `M14` answer extractor.
- **4B model hallucinations:** small language models state incorrect facts, dosages, or mechanisms with high confidence. Always verify against primary clinical literature and licensed healthcare professionals.

## License

Released under `apache-2.0`, matching `Qwen/Qwen3.5-4B`. Upstream datasets retain their respective `apache-2.0` and `mit` licenses listed above. Part of the [SPIKE](https://github.com/oddlyprovenai/spike) open-source project by Oddly Proven Lab.
