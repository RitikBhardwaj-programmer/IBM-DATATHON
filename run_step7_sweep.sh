#!/usr/bin/env bash
# Part 1: ATTACK {none, labelflip, boost} x defence {fedavg+SecAgg, fedavg no SecAgg, median no SecAgg} x NOISE {0,1,2} x SEED 0..4
#         = 135 runs. Trimmed mean is left out: with 4 hospitals and beta 0.25 it equals the median (test_step7_attacks.py f).
#         Median + SecAgg is impossible by design (step 7 refuses it).
# Part 2: "attacker wins" membership inference: no noise, no SecAgg, no poisoning, LOCAL_EPOCHS {20, 50} x SEED 0..4 = 10 runs.
#         Shows whether the loss-threshold MIA can succeed at all on this 273-parameter model when it is allowed to overfit.
# Appends each RESULT line to results/step7_runs.jsonl. Seeds are the outer loop, so a stopped sweep still has balanced cells.
# RESUME=1 keeps the existing file and skips every configuration that already has a row (for a sweep that was interrupted).
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8
OUT=results/step7_runs.jsonl
if [ "${RESUME:-0}" != 1 ]; then
  rm -f $OUT results/step7_done.flag  # appends below; start clean so a re-run does not double rows
fi
touch $OUT

# has_row SEED NOISE ATTACK AGG SECAGG EPOCHS: exit 0 if that configuration already has a row
has_row() {
  .venv/Scripts/python.exe -c "
import json, sys
s, n, a, g, sa, e = sys.argv[1:]
rows = [json.loads(l) for l in open('$OUT', encoding='utf-8') if l.strip()]
sys.exit(0 if any((r['seed'], r['noise'], r['attack'], r['agg'], r['secagg'], r.get('local_epochs', 5)) == (int(s), float(n), a, g, int(sa), int(e)) for r in rows) else 1)
" "$@"
}

one() {  # one SEED NOISE ATTACK AGG SECAGG EPOCHS
  if [ "${RESUME:-0}" = 1 ] && has_row "$@"; then return; fi
  AGG=$4 SECAGG=$5 ATTACK=$3 NOISE=$2 LOCAL_EPOCHS=$6 SEED=$1 .venv/Scripts/python.exe step7_heart_attacks.py 2>&1 | grep '^RESULT ' | sed 's/^RESULT //' >> $OUT
}

for seed in 0 1 2 3 4; do
  for noise in 0 1 2; do
    for attack in none labelflip boost; do
      for cfg in "fedavg 1" "fedavg 0" "median 0"; do
        set -- $cfg
        one $seed $noise $attack $1 $2 5
      done
    done
  done
done
for seed in 0 1 2 3 4; do
  for epochs in 20 50; do
    one $seed 0 none fedavg 0 $epochs
  done
done
echo done > results/step7_done.flag
