#!/bin/bash
# Run baseline
cd Project_A_BaselinePlayer
./run_tests.sh
RC_A=$?
cd ..
# Run enhanced
cd Project_B_EnhancedPlayer
./run_tests.sh
RC_B=$?
cd ..
# Aggregate results
mkdir -p results
cp Project_A_BaselinePlayer/results/results_pre.json results/results_pre.json || true
cp Project_B_EnhancedPlayer/results/results_post.json results/results_post.json || true
# Generate compare report
python - <<'PY'
import json, sys, os
pre = {}
post = {}
try:
    pre = json.load(open('results/results_pre.json'))
except Exception:
    pre = {"error":"no_pre_results"}
try:
    post = json.load(open('results/results_post.json'))
except Exception:
    post = {"error":"no_post_results"}
with open('compare_report.md','w') as fh:
    fh.write('# Compare Report\n')
    fh.write('## Pre vs Post Results\n')
    fh.write('Pre: \n')
    fh.write(json.dumps(pre, indent=2))
    fh.write('\nPost: \n')
    fh.write(json.dumps(post, indent=2))
print('Compare report generated at compare_report.md')
PY
python scripts/generate_compare.py
exit $((RC_A|RC_B))
