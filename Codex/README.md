# Enhanced Course Playback Experience Evaluation

This repository hosts two fully reproducible demo projects that simulate an online course player **before** and **after** enhancement. Project A (`Project_A_BaselinePlayer`) captures the legacy experience, while Project B (`Project_B_EnhancedPlayer`) implements resume, playback-speed control, learned-segment skipping, adaptive buffering/resolution, and time-synced notes. Each project ships with a Flask mock backend, HTML/JS frontend, Playwright E2E coverage, pytest unit tests, reproducible environments, and execution scripts. A shared root workflow (`run_all.sh`) orchestrates both projects, captures screenshots, metrics, and logs, and produces `compare_report.md`.

## Repository Layout

- `Project_A_BaselinePlayer/` – baseline implementation + tests/artifacts.
- `Project_B_EnhancedPlayer/` – enhanced implementation + tests/artifacts.
- `test_data.json` – canonical scenario vectors shared by both projects (each project also keeps a copy in `data/`).
- `results/` – aggregated outputs (copied from per-project folders) after running `run_all.sh`.
- `scripts/` – helper utilities (e.g., comparison builder).
- `run_all.sh` / `run_all.ps1` – one-command workflow for Linux/macOS (bash) or Windows PowerShell.
- `compare_report.md` – populated by the workflow with before/after metrics, screenshot thumbnails, and rollout recommendations.

## Canonical Test Scenarios

Each scenario in `test_data.json` follows the JSON action/state schema:

```json
{
  "id": "TC1_resume_normal",
  "description": "Normal resume: reopen course and resume near last timestamp",
  "actions": [
    {"action": "open_course", "course_id": "C101", "user": "u1"},
    {"action": "play"},
    {"action": "wait_seconds", "value": 5}
  ],
  "initial_state": {
    "saved_progress_s": 125.7,
    "playback_rate": 1.25,
    "learned_segments": [[0, 45]],
    "notes": [{"t": 126.5, "text": "Key point"}]
  },
  "network_profile": {
    "bandwidth_kbps": 1500,
    "latency_ms": 50,
    "jitter_ms": 30
  },
  "expected_state": {
    "start_time_s": 125.7,
    "playback_rate": 1.25,
    "current_quality": "720p",
    "notes_synced": true
  },
  "acceptance": {
    "resume_accuracy_s": 1,
    "playback_rate_error": 0.05,
    "max_time_to_first_frame_ms": 800,
    "max_stall_ms": 300
  }
}
```

**Acceptance criteria**

- Resume accuracy: video resumes within ±1 s of stored time.
- Playback rate: UI applies selection immediately and persists for the session.
- Auto-skip: only skips segments explicitly marked as learned; unlearned content must play.
- Adaptive buffering: time-to-first-frame (TTF) ≤ 800 ms on typical network profiles.
- Resolution switch: completes with < 300 ms stall.
- Note sync: hover displays metadata; click jumps to timestamp within ±1 s.

## Running the Projects

### Prerequisites

- Python 3.9+
- Node not required (Playwright for Python installs Chromium automatically)
- Bash (for `run_all.sh`) or PowerShell (for `run_all.ps1`)

> TIP: On Windows, use Git Bash or WSL for the bash scripts; otherwise run the PowerShell variants.

### Project-Level Execution

```powershell
cd Project_A_BaselinePlayer
./run_tests.ps1     # creates venv, installs deps, runs unit + E2E tests

cd ..\Project_B_EnhancedPlayer
./run_tests.ps1
```

Artifacts (screenshots, logs, metrics) are written into each project’s `results/`, `logs/`, and `screenshots/` directories.

### Full Workflow

```bash
./run_all.sh
```

or

```powershell
./run_all.ps1
```

Steps performed:

1. Install/update dependencies for Project A and Project B (idempotent via local venvs).
2. Launch each mock server, execute pytest unit suites, then Playwright E2E runs that loop over `test_data.json`.
3. Collect `results_pre.json`, `time_pre.txt`, `log_pre.txt`, `screenshot_pre_*` (baseline) and analogous `post` artifacts.
4. Copy artifacts into the root `results/` folder (namespaced by project).
5. Run `scripts/generate_compare.py` to produce `compare_report.md` with per-test tables, aggregated KPIs, and screenshot thumbnails/links.

## Network Simulation & Configurability

- Network behavior is simulated by query parameters (`bw_kbps`, `latency_ms`, `jitter_ms`) consumed by the frontend mocks and Flask video-streaming routes.
- Thresholds (TTF, stall duration, resume tolerance, playback-rate tolerances) reside in `data/expected_post.json` (Project B) and inline defaults in the baseline tests. Adjust them by editing the JSON and re-running the tests/workflow.
- Bandwidth shaping for the mock video stream leverages deliberate `time.sleep` delays per chunk in `server_pre.py` / `server_post.py`. For more realistic testing, plug in OS-level shapers (tc/netem) and point the tests to an alternate hostname via environment variable `PLAYER_HOST`.

## Test Importance Summary

| Test Case | Purpose |
|-----------|---------|
| TC1 Resume | Validates persistence of playback position for continuity. |
| TC2 Playback Speed | Ensures speed UI works across 0.75×–2× without A/V drift and persists for the session. |
| TC3 Auto-Skip | Confirms marked segments are skipped only when opt-in toggle is active. |
| TC4 Network Constrained | Measures resilience (TTF, stalls, adaptive quality) under poor bandwidth/high latency. |
| TC5 Notes Sync | Verifies time-synced note hover/click jumps, preventing study-context loss. |

## Pitfalls & Mitigations

- **Clock drift** between stored timestamps and client time → align to nearest keyframe server-side before saving; in demo we clamp via `player_logic.py`.
- **A/V drift at extreme playback rates** → restrict available rates and monitor `video.playbackRate` vs. allowed set; degrade gracefully if mismatch occurs.
- **Adaptive switches causing stalls** → enhanced player waits for sufficient buffered duration before switching and records switch latency for comparison.
- **Malformed note timestamps** → both projects validate note data via Python unit tests and JS guards before rendering.
- **Browser autoplay constraints** → tests mute the video element and rely on mock timers for deterministic playback start.

## Limitations

- Simulated bandwidth/latency/jitter uses simple sleeps; real CDN behavior must be validated in staging.
- Placeholder MP4 assets are 1 KB stubs; codec-level effects (e.g., continuity at 2×) may differ on production streams.
- Playwright headless Chromium was used; other browsers/platforms might require tuning for autoplay and media policies.
- Performance metrics (TTF, stall duration) are based on client timestamps; production deployments should collect telemetry from both client and edge caches for accuracy.

## Next Steps

- Replace mock assets with adaptive bitrate (ABR) manifests to test realistic switching.
- Integrate real analytics ingestion to capture resume accuracy at scale.
- Extend E2E to cover offline resume and error injection (malformed notes, network drops mid-playback).
- Wire run_all output into CI pipelines for regression gating.

Refer to each project’s README for implementation details, endpoints, and troubleshooting tips.
