"""A tiny random Qwen3.5 in its Hub layout (vision tower + `model.language_model.*`, 3 linear-attention layers and 1
full-attention layer) with a byte-level BPE tokenizer and a chat template, and a prepared training directory in the
format training/prepare.py writes. For the GPU training backend's tests (tests/test_train_peft.py, and with llama.cpp
tests/test_export_integration.py). build() needs torch, transformers and tokenizers; run as a script with the
interpreter that has them:

    python tests/fixtures/tiny_qwen35.py OUT_DIR
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

KEYS = ["self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj", "self_attn.o_proj",
        "mlp.gate_proj", "mlp.up_proj", "mlp.down_proj"]
TEMPLATE = ("{% for m in messages %}<|im_start|>{{ m['role'] }}\n{{ m['content'] }}<|im_end|>\n{% endfor %}"
            "{% if add_generation_prompt %}<|im_start|>assistant\n{% endif %}")
CHATS = [("What is EBITDA?", "Earnings before interest, taxes, depreciation and amortization."),
         ("Define liquidity.", "How fast an asset turns into cash without losing value."),
         ("What is a bond?", "A loan to an issuer that pays interest and returns the principal."),
         ("Qué es el IVA?", "Un impuesto sobre el valor añadido en cada etapa de venta."),
         ("What is equity?", "The owners' share: assets minus liabilities."),
         ("Define margin.", "Profit as a share of revenue."),
         ("What is a dividend?", "Profit a company pays out to its shareholders."),
         ("Qué es un activo?", "Un recurso con valor económico que se controla.")]


def build(out: Path) -> Path:
    """Write the model and tokenizer to `out`. Byte-level BPE like Qwen's own: AutoTokenizer loads a qwen3_5
    checkpoint's tokenizer as Qwen3_5Tokenizer, which rebuilds a BPE from the vocab and merges (a word-level tokenizer
    would turn every word into one id). MRoPE sections fit the 4 rotary dims (head_dim 16, partial factor 0.25), as
    llama.cpp requires; mtp_num_hidden_layers is in the config as in the real one (llama.cpp's converters read it, and
    transformers writes no MTP weights); initializer_range 0.3 lets a few LoRA steps move the logits."""
    import torch
    from tokenizers import Tokenizer, decoders, models, pre_tokenizers, trainers
    from transformers import AutoModelForImageTextToText, PreTrainedTokenizerFast, Qwen3_5Config

    out.mkdir(parents=True, exist_ok=True)
    tok = Tokenizer(models.BPE())
    tok.pre_tokenizer, tok.decoder = pre_tokenizers.ByteLevel(add_prefix_space=False), decoders.ByteLevel()
    tok.train_from_iterator([f"system user assistant {q} {a}" for q, a in CHATS], trainers.BpeTrainer(
        vocab_size=320, special_tokens=["<pad>", "<unk>", "<|im_start|>", "<|im_end|>"],
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet()))
    fast = PreTrainedTokenizerFast(tokenizer_object=tok, unk_token="<unk>", pad_token="<pad>", eos_token="<|im_end|>",
                                   additional_special_tokens=["<|im_start|>"])
    fast.chat_template = TEMPLATE
    fast.save_pretrained(out)
    text = dict(hidden_size=32, intermediate_size=64, num_hidden_layers=4, num_attention_heads=2, num_key_value_heads=1,
                head_dim=16, vocab_size=len(tok.get_vocab()), max_position_embeddings=256,
                layer_types=["linear_attention", "linear_attention", "linear_attention", "full_attention"],
                linear_num_value_heads=2, linear_num_key_heads=1, linear_key_head_dim=16, linear_value_head_dim=16,
                rope_parameters={"rope_type": "default", "rope_theta": 1e7, "partial_rotary_factor": 0.25,
                                 "mrope_section": [1, 1, 0], "mrope_interleaved": True},
                mtp_num_hidden_layers=1, pad_token_id=0, eos_token_id=3, initializer_range=0.3)
    vision = dict(depth=1, hidden_size=16, intermediate_size=32, num_heads=2, out_hidden_size=32, patch_size=14,
                  spatial_merge_size=2, temporal_patch_size=2)
    torch.manual_seed(0)
    AutoModelForImageTextToText.from_config(Qwen3_5Config(text_config=text, vision_config=vision)).save_pretrained(out)
    return out


def prepared(root: Path, model: Path, iters: int = 24, **train) -> Path:
    data = root / "data"
    data.mkdir(parents=True)
    rows = [{"messages": [{"role": "system", "content": "You are Spike Finance."}, {"role": "user", "content": q},
                          {"role": "assistant", "content": a}]} for q, a in CHATS]
    (data / "train.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    (data / "valid.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows[:2]), encoding="utf-8")
    (data / "manifest.json").write_text(json.dumps({"specialist": "finance", "files": {"train.jsonl": "x"},
                                                    "counts": {"train": 8, "valid": 2, "iters": iters}}), encoding="utf-8")
    cfg = {"model": str(model), "train": True, "fine_tune_type": "lora", "data": str(data), "seed": 0,
           "adapter_path": str(root / "run" / "adapter"), "steps_per_report": 4, "steps_per_eval": 8,
           "val_batches": 2, "save_every": 8, "iters": iters, "batch_size": 1, "grad_accumulation_steps": 2,
           "learning_rate": 2e-2, "lr_schedule": {"name": "cosine_decay", "warmup": 2, "arguments": [2e-2, 10, 2e-3]},
           "max_seq_length": 64, "grad_checkpoint": True, "mask_prompt": True, "num_layers": -1,
           "lora_parameters": {"rank": 4, "scale": 2.0, "dropout": 0.05, "keys": KEYS}, **train}
    (data / "mlx_lora.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    return data


if __name__ == "__main__":
    build(Path(sys.argv[1]))
