#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$ROOT/setup.sh"
source "$ROOT/.venv/bin/activate"
export PYTHONPATH="$ROOT/src"
pytest "$ROOT/tests/test_pre_unit.py" -q
pytest "$ROOT/tests/test_pre_e2e.py" -q
