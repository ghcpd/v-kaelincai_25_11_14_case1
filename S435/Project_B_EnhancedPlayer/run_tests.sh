#!/usr/bin/env bash
set -e
ROOT=$(pwd)
. venv/bin/activate
pytest -q tests/test_post_unit.py -q
python server_post.py > logs/server.log 2>&1 &
PID=$!
sleep 1
pytest -q tests/test_post_e2e.py -q
kill $PID || true
