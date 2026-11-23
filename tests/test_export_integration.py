"""MLX adapter -> SPIKE export -> llama.cpp convert_lora_to_gguf.py -> llama-server, checked numerically.

Reference: the same tiny base model with the LoRA delta merged into its weights by hand
(W + alpha/r * B'A', plus llama.cpp's q/k row permutation for the llama architecture). Runtime LoRA and the
merged model must give the same next-token distribution, and both must differ from the base model.
A second test feeds a Qwen3.5-shaped (hybrid attention) config to the converter to check the module-name
mapping used for the real SPIKE base. A third trains a tiny random Qwen3.5 with the GPU backend
(training/train_peft.py) and runs the exported adapter in llama-server against the same LoRA merged by hand.

Needs SPIKE_LLAMA_CPP (llama.cpp checkout) and SPIKE_CONVERT_PYTHON (a Python with the converter's
requirements: torch, transformers, gguf); the numeric tests also need llama-server, and the GPU backend's test
needs peft and pyyaml in SPIKE_CONVERT_PYTHON (SPIKE_REQUIRE_PEFT=1 turns its skip into a failure). Skipped otherwise.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "training"))

from spike_train.evaluation import free_port  # noqa: E402
from spike_train.export import convert, read_safetensors, write_safetensors  # noqa: E402

from spike.runtime.gguf import read_gguf  # noqa: E402
from spike.runtime.llamacpp_server import LlamaServer, ServerConfig, find_binary  # noqa: E402

pytest.importorskip("gguf", reason="llama.cpp's gguf package builds the tiny test model")
from tests.fixtures import make_tiny_gguf as tiny  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LLAMA_CPP = os.environ.get("SPIKE_LLAMA_CPP")
CONVERT_PY = os.environ.get("SPIKE_CONVERT_PYTHON")
pytestmark = pytest.mark.skipif(not (LLAMA_CPP and CONVERT_PY), reason="SPIKE_LLAMA_CPP / SPIKE_CONVERT_PYTHON not set")

RANK, SCALE = 4, 2.0
HEAD_DIM = tiny.N_EMBD // tiny.N_HEAD
KV_DIM = tiny.N_HEAD_KV * HEAD_DIM
# HF module -> (in, out, GGUF tensor)
MODULES = {
    "self_attn.q_proj": (tiny.N_EMBD, tiny.N_EMBD, "attn_q"),
    "self_attn.k_proj": (tiny.N_EMBD, KV_DIM, "attn_k"),
    "self_attn.v_proj": (tiny.N_EMBD, KV_DIM, "attn_v"),
    "self_attn.o_proj": (tiny.N_EMBD, tiny.N_EMBD, "attn_output"),
    "mlp.gate_proj": (tiny.N_EMBD, tiny.N_FF, "ffn_gate"),
    "mlp.up_proj": (tiny.N_EMBD, tiny.N_FF, "ffn_up"),
    "mlp.down_proj": (tiny.N_FF, tiny.N_EMBD, "ffn_down"),
}


def llama_permute(w: np.ndarray, n_head: int, n_head_kv: int) -> np.ndarray:
    """Same row permutation llama.cpp applies to q/k weights when converting the llama architecture."""
    if n_head != n_head_kv:
        n_head = n_head_kv
    return w.reshape(n_head, 2, w.shape[0] // n_head // 2, *w.shape[1:]).swapaxes(1, 2).reshape(w.shape)


def mlx_adapter(prefix: str, layers: dict[int, list[str]], dims: dict[str, tuple[int, int]], seed: int = 7):
    """An adapter exactly as mlx-lm saves it: lora_a (in, r), lora_b (r, out), float32."""
    rng = np.random.default_rng(seed)
    weights = {}
    for i, modules in layers.items():
        for m in modules:
            d_in, d_out = dims[m]
            weights[f"{prefix}layers.{i}.{m}.lora_a"] = (rng.standard_normal((d_in, RANK)) * 0.3).astype(np.float32)
            weights[f"{prefix}layers.{i}.{m}.lora_b"] = (rng.standard_normal((RANK, d_out)) * 0.3).astype(np.float32)
    config = {"fine_tune_type": "lora", "lora_parameters": {"rank": RANK, "scale": SCALE, "dropout": 0.0,
                                                            "keys": sorted({m for ms in layers.values() for m in ms})}}
    return weights, config


def export_and_convert(tmp: Path, weights, config, base_names, hf_config) -> Path:
    tensors, peft_cfg = convert(weights, config, base_names)
    peft = tmp / "peft"
    peft.mkdir()
    write_safetensors(peft / "adapter_model.safetensors", tensors)
    (peft / "adapter_config.json").write_text(json.dumps(peft_cfg))
    base = tmp / "hf-base"
    base.mkdir()
    (base / "config.json").write_text(json.dumps(hf_config))
    out = tmp / "spike-test.gguf"
    proc = subprocess.run([CONVERT_PY, str(Path(LLAMA_CPP) / "convert_lora_to_gguf.py"), str(peft), "--base", str(base),
                           "--outfile", str(out), "--outtype", "f32"], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr[-3000:]
    return out


def gguf_tensor_names(path: Path) -> set[str]:
    import gguf

    return {t.name for t in gguf.GGUFReader(str(path)).tensors}


async def greedy_tokens(base_url: str, prompt: str, lora: list | None = None) -> list[int]:
    """Greedy continuation as token ids (probabilities are not used: the server withholds them for
    partial UTF-8 byte tokens, which a random tiny model emits often)."""
    import httpx

    body = {"prompt": prompt, "n_predict": 24, "temperature": 0.0, "cache_prompt": False, "return_tokens": True}
    if lora is not None:
        body["lora"] = lora
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{base_url}/completion", json=body)
    r.raise_for_status()
    return r.json()["tokens"]


@pytest.mark.skipif(find_binary() is None, reason="llama-server not installed")
async def test_exported_lora_matches_hand_merged_weights(tmp_path, monkeypatch):
    monkeypatch.setenv("SPIKE_HOME", str(tmp_path))
    dims = {m: (d_in, d_out) for m, (d_in, d_out, _) in MODULES.items()}
    weights, config = mlx_adapter("model.", {i: list(MODULES) for i in range(tiny.N_LAYER)}, dims)
    base_names = {f"model.layers.{i}.{m}.weight" for i in range(tiny.N_LAYER) for m in MODULES}
    lora_gguf = export_and_convert(tmp_path, weights, config, base_names, tiny.hf_config())

    meta = read_gguf(lora_gguf).metadata
    assert meta["general.type"] == "adapter" and meta["adapter.lora.alpha"] == pytest.approx(SCALE * RANK)
    expected = {f"blk.{i}.{g}.weight.lora_{ab}" for i in range(tiny.N_LAYER) for *_, g in MODULES.values() for ab in "ab"}
    assert gguf_tensor_names(lora_gguf) == expected

    base_tensors = tiny.model_tensors(0)
    merged = {k: v.copy() for k, v in base_tensors.items()}
    for i in range(tiny.N_LAYER):
        for m, (_, _, g) in MODULES.items():
            a, b = weights[f"model.layers.{i}.{m}.lora_a"], weights[f"model.layers.{i}.{m}.lora_b"]
            delta = SCALE * (a @ b).T  # (out, in), the HF/GGUF layout
            if m == "self_attn.q_proj":
                delta = llama_permute(delta, tiny.N_HEAD, tiny.N_HEAD)
            elif m == "self_attn.k_proj":
                delta = llama_permute(delta, tiny.N_HEAD, tiny.N_HEAD_KV)
            merged[f"blk.{i}.{g}.weight"] += delta
    tiny.write_model(tmp_path / "base.gguf", tensors=base_tensors)
    tiny.write_model(tmp_path / "merged.gguf", tensors=merged)

    with_lora = LlamaServer(ServerConfig(model=tmp_path / "base.gguf", adapters=[lora_gguf], port=free_port(),
                                         context=512, kv_cache_type="f16"))
    merged_srv = LlamaServer(ServerConfig(model=tmp_path / "merged.gguf", port=free_port(), context=512,
                                          kv_cache_type="f16"))
    await with_lora.start(timeout_s=60)
    await merged_srv.start(timeout_s=60)
    try:
        for prompt in ["hello SPIKE", "the world and a", "of to the SPIKE hello"]:
            base = await greedy_tokens(with_lora.base_url, prompt, [{"id": 0, "scale": 0.0}])
            runtime = await greedy_tokens(with_lora.base_url, prompt, [{"id": 0, "scale": 1.0}])
            reference = await greedy_tokens(merged_srv.base_url, prompt)
            assert runtime == reference, prompt
            assert base != runtime, prompt  # the adapter really changes the model
    finally:
        await with_lora.stop()
        await merged_srv.stop()


def test_qwen35_module_names_survive_the_official_converter(tmp_path):
    """mlx-lm's Qwen3.5 module paths -> HF names -> llama.cpp qwen35 tensors, on a tiny hybrid config."""
    hidden, ff, n_layers = 64, 128, 4
    text = {"model_type": "qwen3_5_text", "hidden_size": hidden, "intermediate_size": ff, "num_hidden_layers": n_layers,
            "num_attention_heads": 4, "num_key_value_heads": 2, "head_dim": 16, "vocab_size": 512,
            "linear_conv_kernel_dim": 4, "linear_key_head_dim": 16, "linear_num_key_heads": 2,
            "linear_num_value_heads": 4, "linear_value_head_dim": 16, "full_attention_interval": 4,
            "layer_types": ["linear_attention"] * 3 + ["full_attention"], "rms_norm_eps": 1e-6, "mtp_num_hidden_layers": 1,
            "max_position_embeddings": 4096, "tie_word_embeddings": True,
            "rope_parameters": {"rope_theta": 1e7, "partial_rotary_factor": 0.25, "rope_type": "default",
                                "mrope_section": [1, 1, 0], "mrope_interleaved": True}}
    hf_config = {"architectures": ["Qwen3_5ForConditionalGeneration"], "model_type": "qwen3_5", "text_config": text,
                 "vision_config": {"depth": 1, "hidden_size": 32, "out_hidden_size": hidden}, "tie_word_embeddings": True}
    q_out = 4 * 16 * 2  # gated attention: q_proj also produces the output gate
    dims = {"self_attn.q_proj": (hidden, q_out), "self_attn.k_proj": (hidden, 32), "self_attn.v_proj": (hidden, 32),
            "self_attn.o_proj": (64, hidden), "mlp.gate_proj": (hidden, ff), "mlp.up_proj": (hidden, ff),
            "mlp.down_proj": (ff, hidden)}
    mlp = ["mlp.gate_proj", "mlp.up_proj", "mlp.down_proj"]
    attn = ["self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj", "self_attn.o_proj"]
    layers = {0: mlp, 1: mlp, 2: mlp, 3: attn + mlp}  # mlx-lm finds self_attn only in full-attention layers
    weights, config = mlx_adapter("language_model.model.", layers, dims)
    base_names = {f"model.language_model.layers.{i}.{m}.weight" for i, ms in layers.items() for m in ms}
    out = export_and_convert(tmp_path, weights, config, base_names, hf_config)

    meta = read_gguf(out).metadata
    assert meta["general.architecture"] == "qwen35" and meta["adapter.type"] == "lora"
    gguf_names = {"self_attn.q_proj": "attn_q", "self_attn.k_proj": "attn_k", "self_attn.v_proj": "attn_v",
                  "self_attn.o_proj": "attn_output", "mlp.gate_proj": "ffn_gate", "mlp.up_proj": "ffn_up",
                  "mlp.down_proj": "ffn_down"}
    expected = {f"blk.{i}.{gguf_names[m]}.weight.lora_{ab}" for i, ms in layers.items() for m in ms for ab in "ab"}
    assert gguf_tensor_names(out) == expected


# llama.cpp's convert_hf_to_gguf.py recognises a BPE tokenizer by the hash of its output on a fixed text; the tiny
# model's own byte-level BPE has no entry there, so this wrapper names its pre-tokenizer qwen35 (Qwen3.5's) and runs
# the official converter unchanged otherwise
CONVERT_HF = """import runpy, sys
sys.path.insert(0, sys.argv.pop(1))
from conversion import base
base.TextModel.get_vocab_base_pre = lambda self, tokenizer: "qwen35"
sys.argv[0] = "convert_hf_to_gguf.py"
runpy.run_path(base.__file__.rsplit("/conversion/", 1)[0] + "/convert_hf_to_gguf.py", run_name="__main__")
"""


def run(*cmd, **kw) -> subprocess.CompletedProcess:
    proc = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    assert proc.returncode == 0, (proc.stdout[-2000:], proc.stderr[-4000:])
    return proc


def hf_to_gguf(tmp: Path, model_dir: Path, out: Path) -> Path:
    shim = tmp / "convert_hf_tiny.py"
    shim.write_text(CONVERT_HF, encoding="utf-8")
    run(CONVERT_PY, shim, LLAMA_CPP, model_dir, "--no-mtp", "--outfile", out, "--outtype", "f32")
    return out


@pytest.mark.skipif(find_binary() is None, reason="llama-server not installed")
async def test_an_adapter_trained_with_the_gpu_backend_runs_in_llama_server(tmp_path, monkeypatch):
    """train_peft.py -> export_adapter.py -> GGUF LoRA at runtime gives the same greedy tokens as the checkpoint with
    the delta merged into its weights (W + scale * (a b)^T, the HF layout) converted by llama.cpp, and different
    tokens from the base: the GPU backend's adapter is the adapter llama.cpp applies, in the qwen35 architecture."""
    if subprocess.run([CONVERT_PY, "-c", "import peft, yaml"], capture_output=True).returncode != 0:
        if os.environ.get("SPIKE_REQUIRE_PEFT") == "1":
            pytest.fail("SPIKE_CONVERT_PYTHON lacks peft or pyyaml (training/requirements-gpu.txt)")
        pytest.skip("SPIKE_CONVERT_PYTHON lacks peft or pyyaml (training/requirements-gpu.txt)")
    from tests.fixtures import tiny_qwen35

    monkeypatch.setenv("SPIKE_HOME", str(tmp_path))
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    env.pop("SPIKE_RESUME", None)
    base = tmp_path / "base"
    run(CONVERT_PY, ROOT / "tests" / "fixtures" / "tiny_qwen35.py", base, env=env)
    data = tiny_qwen35.prepared(tmp_path, base)
    run(CONVERT_PY, ROOT / "training" / "train_peft.py", "finance", "--data", data, "--run", tmp_path / "run",
        "--device", "cpu", env=env)
    adapter = tmp_path / "run" / "adapter"
    run(sys.executable, ROOT / "training" / "export_adapter.py", "finance", "--llama-cpp", LLAMA_CPP, "--adapter", adapter,
        "--base", base, "--out", tmp_path / "out", "--outtype", "f32", "--python", CONVERT_PY, "--work", tmp_path / "work")
    lora_gguf = tmp_path / "out" / "spike-finance.gguf"
    meta = read_gguf(lora_gguf).metadata
    assert meta["general.architecture"] == "qwen35" and meta["adapter.lora.alpha"] == pytest.approx(2.0 * 4)
    names = gguf_tensor_names(lora_gguf)
    assert {n for n in names if ".attn_" in n} == {f"blk.3.{g}.weight.lora_{ab}" for g in ("attn_q", "attn_k", "attn_v",
                                                   "attn_output") for ab in "ab"}
    assert len(names) == 2 * (4 + 3 * 4)

    weights = read_safetensors(adapter / "adapters.safetensors")
    scale = json.loads((adapter / "adapter_config.json").read_text(encoding="utf-8"))["lora_parameters"]["scale"]
    merged = tmp_path / "merged"
    merged.mkdir()
    for f in base.iterdir():
        if f.name != "model.safetensors":
            (merged / f.name).write_bytes(f.read_bytes())
    tensors = read_safetensors(base / "model.safetensors")
    for key in {k.rsplit(".", 1)[0] for k in weights}:
        a, b = weights[key + ".lora_a"], weights[key + ".lora_b"]
        hf = key.replace("language_model.model.", "model.language_model.", 1) + ".weight"
        tensors[hf] = (tensors[hf] + scale * (a @ b).T).astype(tensors[hf].dtype)
    write_safetensors(merged / "model.safetensors", tensors)
    base_gguf = hf_to_gguf(tmp_path, base, tmp_path / "base.gguf")
    merged_gguf = hf_to_gguf(tmp_path, merged, tmp_path / "merged.gguf")

    with_lora = LlamaServer(ServerConfig(model=base_gguf, adapters=[lora_gguf], port=free_port(), context=512,
                                         kv_cache_type="f16"))
    merged_srv = LlamaServer(ServerConfig(model=merged_gguf, port=free_port(), context=512, kv_cache_type="f16"))
    await with_lora.start(timeout_s=60)
    await merged_srv.start(timeout_s=60)
    try:
        for prompt in ["<|im_start|>user\nDefine margin.<|im_end|>\n<|im_start|>assistant\n", "What is a bond?",
                       "Un recurso con valor"]:
            plain = await greedy_tokens(with_lora.base_url, prompt, [{"id": 0, "scale": 0.0}])
            runtime = await greedy_tokens(with_lora.base_url, prompt, [{"id": 0, "scale": 1.0}])
            reference = await greedy_tokens(merged_srv.base_url, prompt)
            assert runtime == reference, prompt
            assert plain != runtime, prompt  # the trained adapter really changes the model
    finally:
        await with_lora.stop()
        await merged_srv.stop()
