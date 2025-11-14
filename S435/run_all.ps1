# PowerShell version of run_all
$ROOT = Get-Location
cd "$ROOT\Project_A_BaselinePlayer"
./setup.ps1
./run_tests.ps1
cd "$ROOT\Project_B_EnhancedPlayer"
./setup.ps1
./run_tests.ps1
cd $ROOT
python - <<'PY'
import json, os
pa='Project_A_BaselinePlayer/results'
pb='Project_B_EnhancedPlayer/results'
resA=json.load(open(os.path.join(pa,'results_pre.json')))
resB=json.load(open(os.path.join(pb,'results_post.json')))
lines=['# Compare Report\n','\n','## Per-test comparisons\n','\n','|Test|Pre|Post|Improvement|\n','|----|---|----|-----------|\n']
for k,a in resA['tests'].items():
    b = resB['tests'].get(k,{})
    pre_str=str(a)
    post_str=str(b)
    imp='n/a'
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
