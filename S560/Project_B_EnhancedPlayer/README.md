# Project B — Enhanced Player

This enhanced player implements: resume-from-last-position, adjustable playback rates, auto-skip learned segments, adaptive resolution switching, and time-synced notes with hover-to-jump.

To run (PowerShell):
- .\run_tests.ps1

Outputs are written to `results/` inside the project directory and include `results_post.json`, `time_post.txt`, and `screenshot_post_TC5.png`.

Notes:
- The player persists last playback speed in session storage and stores progress via localStorage + server beacon.
- The server endpoint `/learned_segments` accepts POST requests for learned segments.
- Tests simulate network shaping using the `bw_kbps` and `latency_ms` query parameters.
