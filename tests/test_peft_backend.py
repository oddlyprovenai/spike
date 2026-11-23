"""The parts of the GPU training backend (spike_train/peft_backend.py) that need no torch: the recipe's target modules,
mlx-lm's tensor names and orientation, the learning-rate schedule, the checkpoint and data-order rules. Training itself
is tested in tests/test_train_peft.py."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "training"))

from spike_train import peft_backend as pb  # noqa: E402
from spike_train.export import convert  # noqa: E402

KEYS = ["self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj", "self_attn.o_proj",
        "mlp.gate_proj", "mlp.up_proj", "mlp.down_proj"]


def test_targets_are_the_recipes_modules_of_the_decoder_only():
    import re

    rx = re.compile(pb.target_regex(KEYS))
    assert rx.match("model.language_model.layers.3.self_attn.q_proj")
    assert rx.match("model.layers.0.mlp.down_proj")
    for other in ("model.language_model.layers.0.linear_attn.in_proj_qkv", "model.visual.blocks.0.attn.qkv",
                  "model.visual.blocks.0.mlp.gate_proj", "lm_head", "model.layers.3.self_attn.q_norm"):
        assert not rx.match(other), other


def test_mlx_names_follow_the_checkpoint_not_the_loaded_modules():
    assert pb.mlx_prefix({"model.language_model.layers.0.mlp.up_proj.weight", "model.visual.x"}) == "language_model.model."
    assert pb.mlx_prefix({"model.layers.0.mlp.up_proj.weight"}) == "model."
    assert pb.mlx_key("model.layers.3.self_attn.q_proj", "language_model.model.") == \
        "language_model.model.layers.3.self_attn.q_proj"
    with pytest.raises(ValueError):
        pb.mlx_key("model.visual.blocks.0.attn.qkv", "model.")


def test_peft_weights_become_mlx_tensors_that_export_turns_back_into_the_same_peft_weights():
    rng = np.random.default_rng(0)
    r = 4
    peft = {}
    for layer, module, (fan_in, fan_out) in ((3, "self_attn.q_proj", (32, 64)), (0, "mlp.down_proj", (48, 32))):
        name = f"base_model.model.model.layers.{layer}.{module}"
        peft[f"{name}.lora_A.default.weight"] = rng.normal(size=(r, fan_in)).astype(np.float32)
        peft[f"{name}.lora_B.default.weight"] = rng.normal(size=(fan_out, r)).astype(np.float32)
    peft["base_model.model.model.layers.0.input_layernorm.weight"] = np.ones(32, np.float32)  # not LoRA: ignored
    mlx = pb.to_mlx(peft, "language_model.model.", r)
    assert mlx["language_model.model.layers.3.self_attn.q_proj.lora_a"].shape == (32, r)
    assert mlx["language_model.model.layers.3.self_attn.q_proj.lora_b"].shape == (r, 64)
    base = {"model.language_model.layers.3.self_attn.q_proj.weight", "model.language_model.layers.0.mlp.down_proj.weight"}
    out, config = convert(mlx, {"lora_parameters": {"rank": r, "scale": 2.0, "dropout": 0.05}}, base)
    assert config["lora_alpha"] == 8.0 and config["r"] == r
    for name, value in peft.items():
        if ".lora_" not in name:
            continue
        hf = name.replace("base_model.model.model.layers.", "base_model.model.model.language_model.layers.")
        hf = hf.replace(".default.weight", ".weight")
        np.testing.assert_array_equal(out[hf], value)
    back = pb.from_mlx(mlx)
    np.testing.assert_array_equal(back[("language_model.model.layers.0.mlp.down_proj", "B")],
                                  peft["base_model.model.model.layers.0.mlp.down_proj.lora_B.default.weight"])


def test_the_learning_rate_is_mlx_lms_schedule_in_optimizer_updates():
    sched = {"name": "cosine_decay", "warmup": 60, "arguments": [1e-4, 770, 1e-5]}
    assert pb.lr_at(0, 1e-4, sched) == 0.0
    assert pb.lr_at(30, 1e-4, sched) == pytest.approx(5e-5)
    assert pb.lr_at(60, 1e-4, sched) == pytest.approx(1e-4)
    assert pb.lr_at(60 + 385, 1e-4, sched) == pytest.approx(1e-5 + 0.5 * 9e-5)
    assert pb.lr_at(60 + 770, 1e-4, sched) == pytest.approx(1e-5)
    assert pb.lr_at(5000, 1e-4, sched) == pytest.approx(1e-5)
    assert pb.lr_at(7, 3e-4, None) == 3e-4
    with pytest.raises(ValueError, match="auto"):
        pb.lr_at(0, 1e-4, {"name": "cosine_decay", "arguments": [1e-4, "auto", 1e-5]})


def test_checkpoints_and_data_order_match_the_mlx_rules():
    assert [it for it in range(1, 70) if pb.is_save_point(it, 16, 20)] == [32, 48, 64]
    assert [it for it in range(1, 50) if pb.is_save_point(it, 1, 20)] == [20, 40]
    a = pb.epoch_order(10, seed=0, epoch=1, batch_size=3)
    assert a == pb.epoch_order(10, seed=0, epoch=1, batch_size=3) and len(a) == 3
    assert a != pb.epoch_order(10, seed=0, epoch=2, batch_size=3)
    assert pb.prompt_mask(5, 20, 12) == (5, 12)
    with pytest.raises(ValueError):
        pb.prompt_mask(12, 20, 12)
