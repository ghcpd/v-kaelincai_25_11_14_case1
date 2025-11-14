#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)

cd "$ROOT"
./Project_A_BaselinePlayer/run_tests.sh
./Project_B_EnhancedPlayer/run_tests.sh

mkdir -p results
cp Project_A_BaselinePlayer/results/results_pre.json results/
cp Project_A_BaselinePlayer/results/time_pre.txt results/
cp Project_B_EnhancedPlayer/results/results_post.json results/
cp Project_B_EnhancedPlayer/results/time_post.txt results/
cp Project_A_BaselinePlayer/logs/log_pre.txt results/log_pre.txt
cp Project_B_EnhancedPlayer/logs/log_post.txt results/log_post.txt
cp Project_A_BaselinePlayer/screenshots/screenshot_pre_*.png results/ 2>/dev/null || true
cp Project_B_EnhancedPlayer/screenshots/screenshot_post_*.png results/ 2>/dev/null || true

python - <<'PY'
import json
from pathlib import Path
root = Path(__file__).resolve().parent
pre = json.loads((root / "results" / "results_pre.json").read_text())
post = json.loads((root / "results" / "results_post.json").read_text())
lines = [
    "# Feature Comparison Report", 
    "", 
    "| Scenario | Baseline | Enhanced | Notes |",
    "| --- | --- | --- | --- |",
]
for p, q in zip(pre.get("tests", []), post.get("tests", [])):
    note = f"Baseline pass={p.get('pass')}, enhanced pass={q.get('pass')}"
    lines.append(f"| {p.get('id')} | {p.get('pass')} | {q.get('pass')} | {note} |")
lines.append("")
lines.append("## Metrics")
lines.append(f"- Baseline time file: `results/time_pre.txt`")
lines.append(f"- Enhanced time file: `results/time_post.txt`")
lines.append("")
lines.append("## Visual proof")
lines.append("- ![Resume](results/screenshot_pre_resume.png)")
lines.append("- ![Improved player](results/screenshot_post_resume.png)")
compare_path = root / "compare_report.md"
compare_path.write_text("\n".join(lines))
PY
