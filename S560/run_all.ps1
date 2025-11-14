# PowerShell version of run_all
Write-Host "Running Project A tests..."
Push-Location Project_A_BaselinePlayer
.\run_tests.ps1
Pop-Location

Write-Host "Running Project B tests..."
Push-Location Project_B_EnhancedPlayer
.\run_tests.ps1
Pop-Location

# Copy results
New-Item -ItemType Directory -Force -Path results | Out-Null
Copy-Item -Force -Path Project_A_BaselinePlayer\results\results_pre.json results\results_pre.json -ErrorAction SilentlyContinue
Copy-Item -Force -Path Project_B_EnhancedPlayer\results\results_post.json results\results_post.json -ErrorAction SilentlyContinue

# Generate compare_report
python scripts/generate_compare.py
