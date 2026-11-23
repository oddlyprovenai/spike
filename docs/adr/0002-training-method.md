# ADR 0002: Specialization by LoRA on mlx-lm, with verified distillation and replay

Status: accepted (2026-10-17).

## Context

Specialists must be really trained, not prompt profiles, on free resources: a 36 GB Apple Silicon Mac.
General ability must not degrade. Every adaptation needs a hypothesis and an acceptance test.

## Options

| Method | Fits 36 GB for 4B? | Notes |
|---|---|---|
| Full fine-tuning | No (Adam needs ~16 bytes/param ≈ 64 GB+ for 4B) | also produces 13 full models: 13 × 2.7 GB on disk and no hot switching |
| QLoRA (4-bit base) | Yes | Unsloth advises against QLoRA for all Qwen3.5 models (larger quantization differences) ([docs](https://unsloth.ai/docs/models/qwen3.5/fine-tune)) |
| **LoRA, bf16 base** | Yes: ~10 GB reported by Unsloth; 11.1 GB peak reported for 4B with mlx-lm on an M1 ([sciences44](https://github.com/sciences44/mlx-lora-finetune)) | adapters of tens of MB, hot-swappable in llama.cpp |
| Distillation from a stronger open teacher | Teacher Qwen3.6-35B-A3B (Apache-2.0) runs locally on the Mac | generates data; combined with LoRA |

## Decision

- **LoRA in bf16 with mlx-lm** (`training/train.sh`), rank 16, scale 2.0 (PEFT alpha 32), dropout 0.05,
  `mask_prompt`, all layers, targets `self_attn.{q,k,v,o}_proj` (the 8 full-attention layers) and
  `mlp.{gate,up,down}_proj` (all 32 layers). Linear-attention projections are excluded: llama.cpp's converter
  reorders those tensors and LoRA on them is not verified.
- **Data per adapter** (`training/prepare.py`): permissive sources only (license re-checked on the Hub at
  download time, `spike_train/licenses.py`), explanation-rich answers, dedupe, 13-gram decontamination
  against every eval set (shared instruction templates excluded), **30–35 % general replay**
  (human-written OpenAssistant oasst2 only, Apache-2.0) against forgetting; smoltalk smol-constraints is
  excluded (no license in the Hub metadata, generator model not named);
  Llama-generated data is excluded because its license would force "Llama" into the adapter names.
- **Verified distillation** (`training/distill.py`): teacher answers kept only if they match the gold label
  (MCQ, yes/no, numeric) or pass a strict rubric review; GPT-4o-generated datasets are excluded by default
  (OpenAI terms on competing models).
- **Acceptance per adapter** (in each `training/configs/*.yaml`): domain gain ≥ 3 points with exact
  McNemar p < 0.05 vs. the same base with the same system prompt, and ≤ 1.5 points drop on the general
  regression suite; open-ended domains use position-debiased pairwise judging (win rate ≥ 0.60, sign test).
  An adapter that fails stays unreleased and the specialist keeps running as a prompt profile (shown as β).
- Export: MLX → PEFT (A' = Aᵀ, B' = Bᵀ, alpha = scale·r, names checked against the base checkpoint) → GGUF
  with llama.cpp's `convert_lora_to_gguf.py` (`training/export_adapter.py`).

## Evidence so far

- Export math verified: an exported adapter applied at runtime gives the same greedy tokens as weights
  merged by hand, and different tokens from the base (`tests/test_export_integration.py`, tiny model).
- Qwen3.5 module names survive the official converter as `qwen35` LoRA tensors (same test file).
- **No real adapter has been trained yet.** Training runs on the Mac (docs/TRAINING.md).

## Amendment 2026-11-23: a GPU backend for Google Colab (M17)

Context: the Mac trains one adapter at a time (≈ 10 h for medicine), and the owner offered Google Colab GPUs.
Decision: a second backend, `training/train_peft.py` (PyTorch + PEFT, LoRA in bf16 on CUDA), that keeps everything
above except the trainer itself: the same prepared files and recipe (`mlx_lora.yaml`), the same targets (PEFT
`target_modules` is a regex over the decoder layers only, so the vision tower and the linear-attention projections stay
untouched), alpha = scale·r, the same checkpoint cadence and file names with mlx-lm's tensor names and shapes, exact
resume, and the same export, sweep and acceptance gate. Base model names in the adapter follow the checkpoint's own
files (`model.language_model.layers.N`, `language_model.model.` in mlx-lm terms), not the modules transformers loads
(`Qwen3_5ForCausalLM` names them `model.layers.N`).

Not the same arithmetic as mlx-lm, by design and stated in every run: torch Adam has bias correction (mlx's Adam has
none by default), the data order is a seeded permutation per epoch, kernels and bf16 rounding differ. So a GPU run and
a Mac run are compared only by their evaluations. Marketing is the first user (its first round, nothing to compare
with); medicine and finance keep mlx so their rounds stay comparable.

Evidence: tests on CPU with a tiny random Qwen3.5 in the Hub's layout (`tests/test_peft_backend.py`,
`tests/test_train_peft.py`), and in the llama.cpp CI job the trained adapter through `export_adapter.py` gives in
llama-server the same greedy tokens as the delta merged into the checkpoint by hand (`tests/test_export_integration.py`).
**Not yet run on a GPU**: a Colab smoke run (`--stop-after`) must report step time and memory before any real run.
