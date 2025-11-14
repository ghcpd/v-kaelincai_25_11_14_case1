$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "[1/4] Running Project A (baseline)..."
Push-Location "$ROOT\Project_A_BaselinePlayer"
./run_tests.ps1
Pop-Location

Write-Host "[2/4] Running Project B (enhanced)..."
Push-Location "$ROOT\Project_B_EnhancedPlayer"
./run_tests.ps1
Pop-Location

Write-Host "[3/4] Collecting artifacts..."
$resultRoot = Join-Path $ROOT "results"
New-Item -ItemType Directory -Force -Path "$resultRoot\baseline" | Out-Null
New-Item -ItemType Directory -Force -Path "$resultRoot\baseline\screenshots" | Out-Null
New-Item -ItemType Directory -Force -Path "$resultRoot\enhanced" | Out-Null
New-Item -ItemType Directory -Force -Path "$resultRoot\enhanced\screenshots" | Out-Null
Copy-Item "$ROOT\Project_A_BaselinePlayer\results\results_pre.json" "$resultRoot\baseline\" -Force
Copy-Item "$ROOT\Project_A_BaselinePlayer\results\time_pre.txt" "$resultRoot\baseline\" -Force
Copy-Item "$ROOT\Project_A_BaselinePlayer\logs\log_pre.txt" "$resultRoot\baseline\" -Force
Copy-Item "$ROOT\Project_B_EnhancedPlayer\results\results_post.json" "$resultRoot\enhanced\" -Force
Copy-Item "$ROOT\Project_B_EnhancedPlayer\results\time_post.txt" "$resultRoot\enhanced\" -Force
Copy-Item "$ROOT\Project_B_EnhancedPlayer\logs\log_post.txt" "$resultRoot\enhanced\" -Force
$baselineShots = "$ROOT\Project_A_BaselinePlayer\screenshots"
if (Test-Path $baselineShots) {
  Copy-Item "$baselineShots\*" "$resultRoot\baseline\screenshots\" -Recurse -Force -ErrorAction SilentlyContinue
}
$enhancedShots = "$ROOT\Project_B_EnhancedPlayer\screenshots"
if (Test-Path $enhancedShots) {
  Copy-Item "$enhancedShots\*" "$resultRoot\enhanced\screenshots\" -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "[4/4] Generating compare report..."
python "$ROOT\scripts\generate_compare.py" `
  --pre "$ROOT\Project_A_BaselinePlayer\results\results_pre.json" `
  --post "$ROOT\Project_B_EnhancedPlayer\results\results_post.json" `
  --out "$ROOT\compare_report.md"

Write-Host "Workflow complete. See compare_report.md and results/."
