#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT"
mkdir -p logs results

python server_pre.py --port 5000 > logs/server_pre.log 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" >/dev/null 2>&1' EXIT
sleep 1
pytest tests/test_pre_unit.py tests/test_pre_e2e.py
wait "$SERVER_PID" || true
