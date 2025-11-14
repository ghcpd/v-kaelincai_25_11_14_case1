#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/4] Running Project A (baseline)..."
pushd "$ROOT/Project_A_BaselinePlayer" >/dev/null
./run_tests.sh
popd >/dev/null

echo "[2/4] Running Project B (enhanced)..."
pushd "$ROOT/Project_B_EnhancedPlayer" >/dev/null
./run_tests.sh
popd >/dev/null

echo "[3/4] Collecting artifacts..."
RESULT_ROOT="$ROOT/results"
mkdir -p "$RESULT_ROOT"
mkdir -p "$RESULT_ROOT/baseline" "$RESULT_ROOT/enhanced"
cp "$ROOT/Project_A_BaselinePlayer/results/results_pre.json" "$RESULT_ROOT/baseline/"
cp "$ROOT/Project_A_BaselinePlayer/results/time_pre.txt" "$RESULT_ROOT/baseline/"
cp "$ROOT/Project_A_BaselinePlayer/logs/log_pre.txt" "$RESULT_ROOT/baseline/"
cp "$ROOT/Project_B_EnhancedPlayer/results/results_post.json" "$RESULT_ROOT/enhanced/"
cp "$ROOT/Project_B_EnhancedPlayer/results/time_post.txt" "$RESULT_ROOT/enhanced/"
cp "$ROOT/Project_B_EnhancedPlayer/logs/log_post.txt" "$RESULT_ROOT/enhanced/"
mkdir -p "$RESULT_ROOT/baseline/screenshots" "$RESULT_ROOT/enhanced/screenshots"
cp -R "$ROOT/Project_A_BaselinePlayer/screenshots/." "$RESULT_ROOT/baseline/screenshots/" 2>/dev/null || true
cp -R "$ROOT/Project_B_EnhancedPlayer/screenshots/." "$RESULT_ROOT/enhanced/screenshots/" 2>/dev/null || true

echo "[4/4] Generating compare report..."
python "$ROOT/scripts/generate_compare.py" \
  --pre "$ROOT/Project_A_BaselinePlayer/results/results_pre.json" \
  --post "$ROOT/Project_B_EnhancedPlayer/results/results_post.json" \
  --out "$ROOT/compare_report.md"

echo "Workflow complete. See compare_report.md and results/ for details."
