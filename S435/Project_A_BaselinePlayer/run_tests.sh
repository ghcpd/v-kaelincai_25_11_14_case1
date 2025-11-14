#!/usr/bin/env bash
set -e
ROOT=$(pwd)
. venv/bin/activate
# run unit tests
pytest -q tests/test_pre_unit.py -q
# start server for e2e
python server_pre.py > logs/server.log 2>&1 &
PID=$!
sleep 1
pytest -q tests/test_pre_e2e.py -q
kill $PID || true
