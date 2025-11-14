$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$venv = Join-Path $ROOT ".venv"
if (-not (Test-Path $venv)) {
  python -m venv $venv
}
. "$venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip | Out-Null
pip install -r "$ROOT\requirements.txt" | Out-Null
pip install greenlet==3.1.1 | Out-Null
pip install --no-deps playwright==1.48.0 | Out-Null
python -m playwright install chromium | Out-Null
$env:PYTHONPATH = "$ROOT\src"
pytest "$ROOT/tests/test_post_unit.py" -q
pytest "$ROOT/tests/test_post_e2e.py" -q
