import json
import os
import statistics
import subprocess
import time
from pathlib import Path
from typing import Dict, List

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server_pre.py"
DATA = ROOT / "data" / "test_data.json"
RESULTS_DIR = ROOT / "results"
LOG_DIR = ROOT / "logs"
SCREEN_DIR = ROOT / "screenshots"


def start_server():
    env = os.environ.copy()
    return subprocess.Popen(["python", str(SERVER)], cwd=ROOT, env=env)


def stop_server(proc):
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def run_case(page, case: Dict) -> Dict:
    profile = case["network_profile"]
    params = (
        f"?use_mock=1"
        f"&test_id={case['id']}"
        f"&bw_kbps={profile['bandwidth_kbps']}"
        f"&latency_ms={profile['latency_ms']}"
        f"&jitter_ms={profile.get('jitter_ms', 0)}"
    )
    url = f"http://127.0.0.1:8001/{params}"
    page.goto(url)
    page.wait_for_function(
        "window.playerMetrics && window.playerMetrics.timeToFirstFrameMs !== null",
        timeout=15000,
    )
    metrics = page.evaluate("window.playerMetrics")
    metrics["currentTime"] = page.evaluate(
        "document.getElementById('courseVideo').currentTime"
    )
    metrics["meets_ttf_requirement"] = (
        metrics["timeToFirstFrameMs"]
        <= case["acceptance"]["max_time_to_first_frame_ms"]
    )
    metrics["resume_error_s"] = abs(
        metrics["currentTime"] - case["initial_state"].get("saved_progress_s", 0.0)
    )
    metrics["resume_within_tolerance"] = (
        metrics["resume_error_s"] <= case["acceptance"].get("resume_accuracy_s", 999)
    )
    shot_path = SCREEN_DIR / f"screenshot_pre_{case['id']}.png"
    page.screenshot(path=str(shot_path))
    metrics["screenshot"] = str(shot_path)
    return metrics


def test_baseline_end_to_end():
    RESULTS_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    SCREEN_DIR.mkdir(exist_ok=True)
    with DATA.open() as fh:
        cases = json.load(fh)
    logs: List[str] = []
    case_results: List[Dict] = []
    server_proc = start_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            for case in cases:
                start = time.time()
                metrics = run_case(page, case)
                metrics["elapsed_s"] = round(time.time() - start, 2)
                case_results.append({"id": case["id"], "metrics": metrics})
                logs.append(
                    f"{case['id']}: ttf={metrics['timeToFirstFrameMs']:.1f}ms "
                    f"resume_error={metrics['resume_error_s']:.2f}s"
                )
            browser.close()
    finally:
        stop_server(server_proc)

    avg_ttf = statistics.mean(
        m["metrics"]["timeToFirstFrameMs"] for m in case_results
    )
    summary = {
        "avg_time_to_first_frame_ms": round(avg_ttf, 2),
        "cases": case_results,
        "generated_at": time.time(),
    }
    (RESULTS_DIR / "results_pre.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    (RESULTS_DIR / "time_pre.txt").write_text(
        f"avg_time_to_first_frame_ms={round(avg_ttf, 2)}\n",
        encoding="utf-8",
    )
    (LOG_DIR / "log_pre.txt").write_text("\n".join(logs), encoding="utf-8")

    # Baseline assertions: still ensure mocks produced finite metrics.
    assert all(
        m["metrics"]["timeToFirstFrameMs"] < 6000 for m in case_results
    ), "Baseline player took too long to start in at least one scenario"
