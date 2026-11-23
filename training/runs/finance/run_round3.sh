#!/bin/bash
# Finance round 3 (M3): round 2's recipe with replay.ratio 0.30 -> 0.45 as the one change (commit on mac/m3-round3).
# Same round-2 self-replay file, prepare --self-replay --fit-domain, window 1536, schedule formula, default sweep, gate.
# Round 2 is archived in training/runs/finance/round2/. One heavy job at a time; run again to continue (each step is
# skipped once its output exists).
set -euo pipefail
cd ~/Downloads/Spike-m3
export PATH=~/Downloads/Spike/.venv-train/bin:$PATH
MODEL=$HOME/.spike/models/Qwen3.5-4B-Q4_K_M.gguf; CFG=training/configs/finance.yaml
D=training/data/finance; R=training/runs/finance; mkdir -p $D $R
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $R/pipeline.log; }
[ -s $D/self_replay.summary.json ] || { log "self_replay.jsonl of round 2 missing; stopping"; exit 1; }
if [ ! -f $R/prepare.ok ]; then
  log "round 3: replay 0.45 (commit $(git rev-parse --short HEAD)); prepare --self-replay --fit-domain"
  python training/prepare.py $CFG --self-replay $D/self_replay.jsonl --fit-domain
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
