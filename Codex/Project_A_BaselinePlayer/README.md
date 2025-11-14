# Project A – Baseline Course Player

This folder contains the **pre-enhancement** reference implementation for the course playback experience. The focus is on reproducing the limitations of the legacy player while still capturing telemetry for comparison with Project B.

## Components

- `server_pre.py` – Flask server hosting the static player, mock video streams, and configurable latency/bandwidth simulation.
- `src/` – HTML/JS frontend (no resume, single playback speed, no skip logic, notes not time-synced).
- `src/player_logic.py` – Deterministic helper functions covered by unit tests.
- `tests/` – `pytest` unit tests + Playwright-based E2E suite that iterates over `data/test_data.json`.
- `data/` – Copy of canonical `test_data.json` plus `sample_user_state.json`.
- `mocks/` – Placeholder MP4 assets and helper JSON.
- `run_tests.sh` / `.ps1` – One-command execution (setup + unit + E2E tests).

## Running Tests

```bash
./setup.sh          # optional – automatically invoked by run_tests.sh
./run_tests.sh
```

or on Windows PowerShell:

```powershell
.\run_tests.ps1
```

Artifacts are written to:

- `results/results_pre.json` – metrics per test case
- `results/time_pre.txt` – timing summary (TTF averages, stall estimates)
- `logs/log_pre.txt` – textual trace of each scenario
- `screenshots/screenshot_pre_<testid>.png`

## Network Simulation

`server_pre.py` exposes `/video/<quality>?bw_kbps=...&latency_ms=...` which throttles chunk streaming via `time.sleep`. When E2E tests run with `use_mock=1`, the frontend bypasses media download and uses deterministic timers derived from the query profile, ensuring stable measurements even without external bandwidth tools.

## Limitations Captured

- No resume-from-last-position (progress only logged to console).
- No playback speed controls (fixed 1×).
- No auto-skip (learned segments ignored).
- Fixed 720p stream with no adaptive buffer heuristics.
- Notes list is static text without hover/jump interactions.

These gaps are highlighted in the logs/results to contrast with the enhanced experience in Project B.
