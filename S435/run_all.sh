#!/usr/bin/env bash
set -e
# Run baseline then enhanced tests and aggregate results
PROJECT_A="Project_A_BaselinePlayer"
PROJECT_B="Project_B_EnhancedPlayer"
ROOT=$(pwd)

# Setup envs and run tests
echo "Setting up Project A..."
cd "$ROOT/$PROJECT_A"
./setup.sh || echo 'setup.sh failed - try setup.ps1 on Windows'
./run_tests.sh

echo "Setting up Project B..."
cd "$ROOT/$PROJECT_B"
./setup.sh || echo 'setup.sh failed - try setup.ps1 on Windows'
./run_tests.sh

mkdir -p "$ROOT/results"
cp "$ROOT/$PROJECT_A/results"/* "$ROOT/results/" || true
cp "$ROOT/$PROJECT_B/results"/* "$ROOT/results/" || true

# Generate compare report
python - <<'PY'
import json, os
pa='Project_A_BaselinePlayer/results'
pb='Project_B_EnhancedPlayer/results'
resA=json.load(open(os.path.join(pa,'results_pre.json')))
resB=json.load(open(os.path.join(pb,'results_post.json')))
# write a simple markdown table with some metrics
lines=['# Compare Report\n', '\n', '## Per-test comparisons\n', '\n', '|Test|Pre|Post|Improvement|\n', '|----|---|----|-----------|\n']
for k,a in resA['tests'].items():
    b = resB['tests'].get(k,{})
    pre_str=str(a)
    post_str=str(b)
    imp='n/a'
    # if both have ttf
    if 'time_to_first_frame_ms' in a and 'time_to_first_frame_ms' in b:
        try:
            imp = float(a['time_to_first_frame_ms']) - float(b['time_to_first_frame_ms'])
            imp = f"{imp} ms"
        except Exception:
            imp='n/a'
    lines.append(f'|{k}|{pre_str}|{post_str}|{imp}|\n')
open('compare_report.md','w').write(''.join(lines))
print('compare_report.md generated')
PY

echo "All done. Artifacts in ./results and compare_report.md"
