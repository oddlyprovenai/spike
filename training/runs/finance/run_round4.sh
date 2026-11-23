#!/bin/bash
# Finance round 4 (M3): round 2's recipe (replay 0.30, window 1536, the round-2 self-replay file, --fit-domain) with one
# change: every domain target is the base model's own answer, kept only when correct (training/self_distill.py).
# Archive round 3 first (training/runs/finance/round3/). Run only when no other heavy job is on the Mac; run again to
# continue (each step is skipped once its output exists; self_distill resumes its .partial).
set -euo pipefail
cd ~/Downloads/Spike-m3
export PATH=~/Downloads/Spike/.venv-train/bin:$PATH
MODEL=$HOME/.spike/models/Qwen3.5-4B-Q4_K_M.gguf; CFG=training/configs/finance.yaml
D=training/data/finance; R=training/runs/finance; mkdir -p $D $R
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $R/pipeline.log; }
[ -s $D/self_replay.summary.json ] || { log "self_replay.jsonl of round 2 missing; stopping"; exit 1; }
if [ ! -s $D/self_distilled.summary.json ]; then
  PORT=8091
  log "round 4 (commit $(git rev-parse --short HEAD)): self_distill, llama-server on the base model alone, port $PORT"
  llama-server -m $MODEL --host 127.0.0.1 --port $PORT -c 8192 --parallel 4 --jinja -ngl 99 --flash-attn auto \
    --no-webui --cache-type-k q8_0 --cache-type-v q8_0 > $R/llama-server.log 2>&1 &
  SERVER=$!; trap 'kill $SERVER 2>/dev/null || true' EXIT
  until curl -sf http://127.0.0.1:$PORT/health >/dev/null; do sleep 2; kill -0 $SERVER || { log "llama-server died"; exit 1; }; done
  RES=(); [ -f $D/self_distilled.jsonl.partial ] && RES=(--resume)
  python training/self_distill.py $CFG --base-url http://127.0.0.1:$PORT/v1 --out $D/self_distilled.jsonl "${RES[@]}"
  kill $SERVER; trap - EXIT
  log "self_distill: done $(python -c "import json;s=json.load(open('$D/self_distilled.summary.json'));print(s['kept'], 'of', s['questions'], s['sources'])")"
fi
if [ ! -f $R/prepare.ok ]; then
  log "prepare --distilled self_distilled.jsonl --self-replay --fit-domain"
  python training/prepare.py $CFG --distilled $D/self_distilled.jsonl --self-replay $D/self_replay.jsonl --fit-domain
  python - <<PY
import json, sys
c = json.load(open("$D/manifest.json"))["counts"]
print(c)
if c["replay_ratio_target"] - c["replay_ratio_actual"] > 0.02 or c["domain"] < 0.3 * c.get("domain_before_fit", c["domain"]):
    sys.exit("prepare: replay ratio or domain floor not met; stopping before training")
PY
  touch $R/prepare.ok; log "prepare: done $(python -c "import json;print(json.load(open('$D/manifest.json'))['counts'])")"
fi
if ! python -c "import json,sys;sys.exit(0 if json.load(open('$R/run.json')).get('exit_code')==0 else 1)" 2>/dev/null; then
  log "train: RAM guard"
  RESUME_FREE_GB=15 RESUME_STABLE_MIN=2 SPIKE_MLX_MEMORY_GB=16 SPIKE_MLX_CACHE_GB=2 bash training/scripts/train_supervised.sh finance
  log "train: done"
fi
log "sweep: default candidates (incl. final@0.5) on the selection suites, then the acceptance suites once"
set +e
python training/sweep_checkpoints.py finance --llama-cpp $HOME/src/llama.cpp --model $MODEL
code=$?
log "sweep: exit $code (0 accepted, 2 rejected); evidence $R/sweep/summary.md"
exit $code
