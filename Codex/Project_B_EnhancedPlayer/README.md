# Project B – Enhanced Course Player

Project B upgrades the baseline experience with resumable playback, adjustable speeds (0.75×–2×), auto-skip of learned segments, adaptive buffering/resolution, and interactive time-synced notes. The folder mirrors Project A’s structure but implements the enhanced logic and richer tests.

## Components

- `server_post.py` – Flask backend with progress + learned-segment endpoints and adaptive mock streaming.
- `src/index.html` + `src/player.js` – Enhanced UI and logic, instrumented for Playwright automation.
- `src/player_logic.py` – Pure-Python helpers for resume, playback-rate validation, skip heuristics, and note mapping (unit tested).
- `data/test_data.json` – copy of canonical scenarios plus `expected_post.json` that stores acceptance thresholds.
- `tests/` – pytest unit suite + Playwright E2E suite validating functionality & performance vs. expectations.
- `run_tests.sh` / `.ps1` – orchestrate environment setup, unit tests, and E2E flows; artifacts are stored in `results/`, `logs/`, `screenshots/`.

## Running Tests

```bash
./setup.sh
./run_tests.sh
```

or on Windows PowerShell:

```powershell
.\run_tests.ps1
```

Outputs:

- `results/results_post.json` – per-test metrics (resume accuracy, stalls, adaptive switches, note-jump precision)
- `results/time_post.txt` – timing summary: avg TTF, avg stall duration, resolution switch latency
- `logs/log_post.txt` – textual event trace
- `screenshots/screenshot_post_<testid>.png`

## Feature Highlights vs. Baseline

| Capability | Project A | Project B |
|------------|-----------|-----------|
| Resume progress | ✖️ | ✔️ (local & server store) |
| Playback speeds | Fixed 1× | 0.75×–2× persisted per session |
| Learned segments | Ignored | Auto-skip toggle with safety checks |
| Adaptive buffering | Constant chunk delay | Bandwidth-aware source switching & stall tracking |
| Notes | Static text | Hover highlight + click-to-jump |

## Network Simulation & Metrics

- Query parameters `bw_kbps`, `latency_ms`, `jitter_ms` flow from Playwright tests into both the Flask stream (chunk pacing) and the JS mock instrumentation (when `use_mock=1`), enabling deterministic KPIs.
- `window.enhancedMetrics` captures time-to-first-frame, stall durations, adaptive switch events, skip destinations, and note-jump accuracy. Tests persist these metrics into JSON/ TXT artifacts and attach screenshots.

## Acceptance Thresholds

Defined in `data/expected_post.json`:

- Resume accuracy ≤ ±1 s
- Time-to-first-frame ≤ 800 ms (normal) / 1800 ms (constrained)
- Playback rate error ≤ 0.05
- Resolution switch stall ≤ 300 ms
- Note jump accuracy ≤ 1 s

Modify the JSON to reconfigure tolerances without touching code.
