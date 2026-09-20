#!/usr/bin/env bash
# Runs FedAvg and FedProx (mu=0.1, mu=1.0) over 5 seeds; appends each RESULT line to results/step2_runs.jsonl
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
for seed in 0 1 2 3 4; do
  for cfg in "fedavg 0" "fedprox 0.1" "fedprox 1.0"; do
    set -- $cfg
    STRATEGY=$1 MU=$2 SEED=$seed .venv/Scripts/python.exe step2_heart_fedavg_fedprox.py 2>&1 | grep '^RESULT ' | sed 's/^RESULT //' >> results/step2_runs.jsonl
  done
done
echo done > results/step2_done.flag
