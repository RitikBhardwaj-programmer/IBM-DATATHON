#!/usr/bin/env bash
# Part 1: SECAGG=1 x NOISE {0,1,2} x {fedavg, fedprox MU=0.1} x SEED 0..4 = 30 runs.
# Part 2: SECAGG=0 timing reference, seed 0 only (6 runs): gives sec/round without SecAgg on the same code path.
# Appends each RESULT line to results/step4_runs.jsonl (the "secagg" field tells them apart).
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
rm -f results/step4_runs.jsonl results/step4_done.flag  # appends below; start clean so a re-run does not double rows
for seed in 0 1 2 3 4; do
  for noise in 0 1 2; do
    for cfg in "fedavg 0" "fedprox 0.1"; do
      set -- $cfg
      SECAGG=1 STRATEGY=$1 MU=$2 NOISE=$noise SEED=$seed .venv/Scripts/python.exe step4_heart_secagg.py 2>&1 | grep '^RESULT ' | sed 's/^RESULT //' >> results/step4_runs.jsonl
    done
  done
done
for noise in 0 1 2; do
  for cfg in "fedavg 0" "fedprox 0.1"; do
    set -- $cfg
    SECAGG=0 STRATEGY=$1 MU=$2 NOISE=$noise SEED=0 .venv/Scripts/python.exe step4_heart_secagg.py 2>&1 | grep '^RESULT ' | sed 's/^RESULT //' >> results/step4_runs.jsonl
  done
done
echo done > results/step4_done.flag
