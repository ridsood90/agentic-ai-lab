#!/usr/bin/env bash
# Runs the full eval for each model, validator on and off.
# Usage: bash scripts/run_all.sh            (from the repo root)
#        bash scripts/run_all.sh qwen3:8b   (one model only)
set -u
MODELS=${@:-"qwen3:8b mistral:latest"}

for m in $MODELS; do
  ollama show "$m" >/dev/null 2>&1 || { echo "Unknown model: $m"; exit 1; }
done

mkdir -p logs
for m in $MODELS; do
  for v in true false; do
    echo "== $m validate=$v =="
    AGENT_MODEL=$m VALIDATE_RESULTS=$v PYTHONPATH=src \
      python scripts/run_evals.py > "logs/${m//:/_}-$v.log" 2>&1
  done
  ollama stop "$m"
done