# Enhanced Course Playback Evaluation

## Structure
- `Project_A_BaselinePlayer/`: baseline UI without enhancements, simple Flask server, placeholder tests, and baseline metrics artifacts.
- `Project_B_EnhancedPlayer/`: enhanced UX with resume, speed control, auto-skip, adaptive buffering, and note sync plus a Flask + API backend.
- `results/`: aggregated run outputs, metrics, logs, and screenshots from both projects.
- `test_data.json`: canonical test vectors shared by both projects for scenarios like resume, playback speed, auto-skip, performance under constrained networks, and note sync.
- `run_all.sh`: master workflow that runs both project suites, copies artifacts into `results/`, and regenerates `compare_report.md`.

## Setup
1. Run each project setup script once to install dependencies and Playwright assets:
   ```bash
   cd Project_A_BaselinePlayer
   ./setup.sh
   cd ../Project_B_EnhancedPlayer
   ./setup.sh
   ```
2. Each setup creates the Python environment (using system Python) and installs Flask, PyTest, Playwright, Pillow, and helpers.
3. To refresh Playwright browsers manually: `python -m playwright install` inside each project.

## Running tests
- **Project A (baseline)**
  ```bash
  cd Project_A_BaselinePlayer
  ./run_tests.sh
  ```
  - Starts `server_pre.py` on port 5000, runs unit + Playwright-based E2E flows, stores logs in `logs/`, metrics in `results/`, screenshots in `screenshots/`, and writes summary files (`results_prev.json`, `time_pre.txt`).

- **Project B (enhanced)**
  ```bash
  cd Project_B_EnhancedPlayer
  ./run_tests.sh
  ```
  - Starts `server_post.py` on port 6000, runs the enhanced suite, captures improved metrics, and outputs `results_post.json`, `time_post.txt`, and visual evidence.

- **Full pipeline**
  ```bash
  ./run_all.sh
  ```
  - Executes Project A then Project B suites, copies results/logs/screenshots into `results/`, and rewrites `compare_report.md` with before/after summaries and thumbnails.

## Network simulation & thresholds
- Each test entry in `test_data.json` has `network_profile` attributes (`bandwidth_mbps`, `latency_ms`, `packet_loss`). Playwright E2E flows propagate these into backend calls to simulate delayed chunk responses.
- Adjust profiles there to emulate jitter, constrained bandwidth, or offline retries.
- Acceptance thresholds (documented in `test_data.json` under `acceptance_criteria`):
  - `resume_tolerance_sec`: ¡Ü1s resume accuracy.
  - `playback_rate_range`: 0.75¡Á¨C2¡Á (UI persists selection per scenario).
  - `time_to_first_frame_ms`: ¡Ü800ms target.
  - `max_stall_ms`: ¡Ü300ms per stall.
  - `resolution_switch_ms`: ¡Ü300ms ideally.

## Artifacts
- `results/`: merged `results_pre.json`, `results_post.json`, `time_pre.txt`, `time_post.txt`, `log_pre.txt`, `log_post.txt`, and screenshots for each test (e.g., `screenshot_pre_resume.png`).
- `compare_report.md`: per-scenario comparison table, aggregated metrics, and screenshot thumbnails.
- Each project also retains its own `results/`, `logs/`, and `screenshots/` folders for isolated runs.

## Importance of each test scenario
1. **Resume accuracy**: Users expect to continue within ¡À1s of their last stop; repeated interrupts should not break continuity.
2. **Playback speed**: Studying at 0.75¡Á¨C2¡Á helps pace learning; rate toggles must stay synced with audio/video to prevent drift.
3. **Auto-skip learned segments**: Skipping already-reviewed content improves efficiency but must never skip segments that are not flagged.
4. **Adaptive buffering/performance**: Constrained networks should still reach first frame <800ms, avoid stalls >300ms, and switch resolutions without large stalls.
5. **Note sync & jump**: Notes guide recall; hovering should show jump targets and clicking should place the player at the exact timestamp.

## Pitfalls & mitigations
- **Clock drift** between saved timestamps and client timeline**: Normalize stored time before resuming; add server-side validation of stored positions.
- **A/V drift at extreme rates**: Cap playback rates and monitor audio deviation; re-sync on every keyframe.
- **Chunk availability for adaptive resolution**: Keep fallback tiers and parallel prefetch to avoid missing segments.
- **Invalid note timestamps**: Validate note input and guard hover/click logic; clamp to playback range.
- **Browser codec differences**: Test across Chrome/Firefox and fall back to progressive textures if 2¡Á playback fails.

## Limitations & next steps
- Bandwidth simulation in this repo is a proxy; real CDNs and codec behavior require staging validation.
- Actual video playback is stubbed with simulated timing; real MP4/HLS streams might behave differently, especially across browsers.
- The UI stores progress in localStorage and the mock API; production needs persisted user data and daily cleanup.
- For future work: add telemetry (e.g., rebuffer counts, picture quality metrics), extend tests to real video segments, and integrate with the real course API.
