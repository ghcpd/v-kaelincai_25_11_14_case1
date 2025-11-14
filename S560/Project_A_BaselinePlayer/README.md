# Project A — Baseline Player

This baseline demonstrates a simple video player using a mock streaming endpoint. It lacks resume, playback speed UI, auto-skip, adaptive buffering, and notes sync logic.

To run (PowerShell):
- .\run_tests.ps1

Outputs are written to `results/` inside the project directory.

Important notes:
- Tests use a simulated 'mock' player to ensure timing consistency in constrained CI environments.
- E2E tests will create a screenshot named `screenshot_pre_TC1.png` under `results/`.
