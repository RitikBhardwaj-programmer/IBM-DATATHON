#!/usr/bin/env bash
# Runs FedAvg and FedProx (mu=0.1) at NOISE in {0, 0.5, 1.0, 2.0} over 5 seeds; appends each RESULT line to results/step3_runs.jsonl
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
rm -f results/step3_runs.jsonl results/step3_done.flag  # appends below; start clean so a re-run does not double rows
for seed in 0 1 2 3 4; do
  for noise in 0 0.5 1.0 2.0; do
    for cfg in "fedavg 0" "fedprox 0.1"; do
      set -- $cfg
      STRATEGY=$1 MU=$2 NOISE=$noise SEED=$seed .venv/Scripts/python.exe step3_heart_dp.py 2>&1 | grep '^RESULT ' | sed 's/^RESULT //' >> results/step3_runs.jsonl
    done
  done
done
echo done > results/step3_done.flag
