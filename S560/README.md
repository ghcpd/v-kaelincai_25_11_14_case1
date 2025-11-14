# Enhanced Course Playback Experience — Baseline vs Enhanced

This repository contains two demo projects implementing a simple course video player: Project_A_BaselinePlayer (baseline) and Project_B_EnhancedPlayer (enhanced). Each includes unit tests and E2E tests using Playwright for Python.

Quick start (Windows PowerShell):
- cd Project_A_BaselinePlayer; .\run_tests.ps1
- cd ..\Project_B_EnhancedPlayer; .\run_tests.ps1
- From root: .\run_all.sh (on WSL/macOS/Linux) or run the two projects sequentially manually.

Outputs are saved at `Project_A_BaselinePlayer/results` and `Project_B_EnhancedPlayer/results` and aggregated to `results/`.

The tests validate resume, playback speed, auto-skip, adaptive buffering, and note sync using a mock video behavior for controlled timing.

## Test Scenarios (canonical)
- Resume-from-last-position: tests for resuming close to saved progress within ±1s.
- Playback-speed: apply rates 0.75×, 1.5×, 2× and check audio/video sync within 200ms.
- Auto-skip learned segments: toggling skips learned segments and does not skip unlearned content.
- Adaptive buffering and resolution switching: change network profile (bandwidth/latency) and validate TTF and switch times.
- Notes sync and quick-jump: verify hover-to-highlight note and click-to-jump behavior within ±1s tolerance.

Acceptance criteria (defaults):
- Resume accuracy within ±1s of stored time
- Playback-rate control applies and persists per session
- Skip logic does not skip unlearned content
- Time-to-first-frame ≤ 800ms on typical network (e.g., 1.5 Mbps)
- Resolution switch completes without stalls >300ms

To change thresholds and simulation parameters, edit `test_data.json` or `shared/test_data.json` and re-run `run_all.sh`.

Limitations & pitfalls:
- Network simulation performed by server is an approximation. Real CDNs and codec-level behavior vary.
- Browser-level autoplay restrictions require that the video element is muted for automatic playback used in tests.
- A/V drift may still occur at extreme rates (2x); browser decoding may throttle audio or skip frames.

Recommendations for rollout:
- Use server-side alignment for stored progress to keyframe boundaries to prevent resume jitter.
- Conservative adaptive quality switching heuristics reduce stalls: increase buffer threshold before switching to higher quality.
- Validate note timestamps against video timeline using automated tools during note submission.

