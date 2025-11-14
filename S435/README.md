# Enhanced Course Playback Experience Evaluation\n\nThis repository contains two reproducible demo projects that compare a baseline course player (Project A) and an enhanced player (Project B) implementing features like resume, playback speed control, auto-skip learned segments, adaptive buffering/resolution, and synced notes with hover-to-jump behavior.\n\nRun the full workflow: ./run_all.sh (or PowerShell: ./run_all.ps1)\n\nEach project has its own run_tests.sh that starts the server, runs unit and E2E tests, captures screenshots, and writes results to results/*.\n\nNetwork simulation: The tests pass a `networkProfile` object into the browser to simulate bandwidth_kbps and latency_ms. The server honors these via delay and approximation.\n\nThresholds and acceptance criteria are in `Project_B_EnhancedPlayer/data/expected_post.json`.

Acceptance criteria summary:\n- Resume accuracy within ±1s\n- Playback-rate applied immediately and persisted per session\n- Auto-skip only skips learned segments and not others\n- Time-to-first-frame under 800ms on normal network (adjustable)\n- Resolution switch completes without stalls longer than 300ms\n\n\nSee compare_report.md for aggregated results after running the workflow.

## Test scenarios and expected formats
Test vectors are in `test_data.json` (root). Each test case uses a JSON structure with initial state, network profile, actions, and expected outcomes. Tests produce `results_pre.json` and `results_post.json`, `time_pre.txt`, `time_post.txt`, and screenshots in each project's `screenshots/` folder.

## Pitfalls & common failure points
- Clock drift and timezone differences when persisting timestamps; use server-aligned time to avoid mismatches.
- A/V drift when playbackRate is set to extreme speeds (>1.75x) in real media; simulated player may not show codec-level issues.
- Browser-specific behavior for media codecs and adaptive bitrate; the demo uses simulated frames.
- Network shaping here is simulated at the server; real CDN behavior is more complex and may vary.
\n