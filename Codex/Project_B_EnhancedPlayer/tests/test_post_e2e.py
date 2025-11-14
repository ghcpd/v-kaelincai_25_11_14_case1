import json
import os
import statistics
import subprocess
import time
from pathlib import Path
from typing import Dict, List

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server_post.py"
TEST_DATA = ROOT / "data" / "test_data.json"
EXPECTATIONS = json.loads(
    (ROOT / "data" / "expected_post.json").read_text(encoding="utf-8")
)
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


def configure_storage(context, course_id: str, saved_progress: float):
    script = f"""
        window.localStorage.setItem(
            'course_progress_{course_id}',
            JSON.stringify({{"t": {saved_progress}, "updated_at": Date.now()}})
        );
        window.sessionStorage.clear();
    """
    context.add_init_script(script)


def apply_actions(page, case: Dict):
    for action in case.get("actions", []):
        kind = action["action"]
        if kind == "wait_seconds":
            page.wait_for_timeout(int(action["value"] * 1000))
        elif kind == "set_speed":
            page.locator("#speedSelect").select_option(str(action["value"]))
            page.wait_for_timeout(300)
        elif kind == "reload_course":
            page.reload()
            page.wait_for_timeout(1000)
        elif kind == "enable_auto_skip":
            checkbox = page.locator("#autoSkipToggle")
            checked = checkbox.is_checked()
            if action.get("value", True) and not checked:
                checkbox.click()
            elif not action.get("value", True) and checked:
                checkbox.click()
        elif kind == "play":
            page.evaluate("document.getElementById('courseVideo').play()")
        elif kind == "add_note":
            page.evaluate("window.playerApi.addNote(note)", note={"t": action["t"], "text": action["text"]})
        elif kind == "hover_note":
            page.wait_for_selector(".note", timeout=5000)
            page.locator(".note").nth(action["index"]).hover()
        elif kind == "click_note":
            page.wait_for_selector(".note", timeout=5000)
            page.locator(".note").nth(action["index"]).click()
        elif kind == "simulate_network":
            # handled via query parameters
            pass
        elif kind == "observe_state":
            pass
        # simulate network handled via query parameters


def run_case(browser, case: Dict) -> Dict:
    profile = case["network_profile"]
    course_id = next(
        (a["course_id"] for a in case.get("actions", []) if a["action"] == "open_course"),
        "C101",
    )
    context = browser.new_context()
    configure_storage(context, course_id, case["initial_state"]["saved_progress_s"])
    page = context.new_page()
    url = (
        f"http://127.0.0.1:8002/?use_mock=1&course_id={course_id}"
        f"&test_id={case['id']}&bw_kbps={profile['bandwidth_kbps']}"
        f"&latency_ms={profile['latency_ms']}&jitter_ms={profile.get('jitter_ms', 0)}"
    )
    page.goto(url)
    page.wait_for_function("window.playerApi !== undefined", timeout=15000)
    if case["initial_state"].get("learned_segments"):
        page.evaluate(
            "segments => window.playerApi.setLearnedSegments(segments)",
            case["initial_state"]["learned_segments"],
        )
    apply_actions(page, case)
    metrics = page.evaluate("window.playerApi.getMetrics()")
    metrics["videoCurrentTime"] = page.evaluate(
        "document.getElementById('courseVideo').currentTime"
    )
    metrics["playbackRate"] = page.evaluate(
        "document.getElementById('courseVideo').playbackRate"
    )
    shot = SCREEN_DIR / f"screenshot_post_{case['id']}.png"
    page.screenshot(path=str(shot))
    metrics["screenshot"] = str(shot)
    context.close()
    return metrics


def evaluate_case(case: Dict, metrics: Dict) -> Dict:
    expected = case.get("expected_state", {})
    threshold = EXPECTATIONS["max_time_to_first_frame_ms"]
    if case["id"] == "TC4_network_constrained_performance":
        threshold = EXPECTATIONS["max_time_to_first_frame_ms_constrained"]
    resume_target = expected.get("start_time_s", case["initial_state"]["saved_progress_s"])
    resume_error = abs(metrics["videoCurrentTime"] - resume_target)
    playback_error = abs(metrics["playbackRate"] - expected.get("playback_rate", metrics["playbackRate"]))
    note_diffs = [jump["diff"] for jump in metrics.get("noteJumps", [])]
    note_diff = min(note_diffs) if note_diffs else None
    stall_avg = (
        statistics.mean(metrics["stalls"]) if metrics.get("stalls") else 0.0
    )
    return {
        "id": case["id"],
        "time_to_first_frame_ms": metrics["timeToFirstFrameMs"],
        "resume_error_s": resume_error,
        "playback_rate_error": playback_error,
        "note_jump_diff_s": note_diff,
        "stalls_ms": metrics.get("stalls", []),
        "avg_stall_ms": stall_avg,
        "quality": metrics.get("currentQuality"),
        "skipped_segments": metrics.get("skippedSegments", []),
        "meets_ttf": metrics["timeToFirstFrameMs"] <= threshold,
        "meets_resume": resume_error <= EXPECTATIONS["resume_accuracy_s"],
        "meets_playback_rate": playback_error <= EXPECTATIONS["playback_rate_error"],
        "meets_note_jump": (
            note_diff is None or note_diff <= EXPECTATIONS["note_jump_accuracy_s"]
        ),
        "screenshot": metrics["screenshot"],
    }


def test_enhanced_end_to_end():
    RESULTS_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    SCREEN_DIR.mkdir(exist_ok=True)
    cases = json.loads(TEST_DATA.read_text(encoding="utf-8"))
    server_proc = start_server()
    logs: List[str] = []
    case_results: List[Dict] = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for case in cases:
                metrics = run_case(browser, case)
                evaluated = evaluate_case(case, metrics)
                case_results.append(evaluated)
                logs.append(
                    f"{case['id']}: TTF={evaluated['time_to_first_frame_ms']:.1f}ms "
                    f"resume_error={evaluated['resume_error_s']:.2f}s "
                    f"quality={evaluated['quality']}"
                )
            browser.close()
    finally:
        stop_server(server_proc)

    avg_ttf = statistics.mean(r["time_to_first_frame_ms"] for r in case_results)
    avg_stall = statistics.mean(
        r["avg_stall_ms"] for r in case_results if r["avg_stall_ms"] is not None
    )
    summary = {
        "cases": case_results,
        "avg_time_to_first_frame_ms": round(avg_ttf, 2),
        "avg_stall_ms": round(avg_stall, 2),
        "generated_at": time.time(),
    }
    (RESULTS_DIR / "results_post.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    (RESULTS_DIR / "time_post.txt").write_text(
        f"avg_time_to_first_frame_ms={round(avg_ttf, 2)}\n"
        f"avg_stall_ms={round(avg_stall, 2)}\n",
        encoding="utf-8",
    )
    (LOG_DIR / "log_post.txt").write_text("\n".join(logs), encoding="utf-8")

    assert all(r["meets_ttf"] for r in case_results), "TTF requirement not met"
    for case, result in zip(cases, case_results):
        if "start_time_s" in case.get("expected_state", {}):
            assert result["meets_resume"], f"Resume requirement failed for {case['id']}"
        if case["id"] == "TC2_playback_speed":
            assert (
                result["meets_playback_rate"]
            ), "Playback rate persistence failed"
        if case["id"] == "TC5_notes_sync_and_jump":
            assert (
                result["meets_note_jump"]
            ), "Note jump accuracy failed"
        if case["id"] == "TC3_auto_skip_learned":
            assert result["skipped_segments"], "Auto-skip did not trigger"
        if case["id"] == "TC4_network_constrained_performance":
            assert (
                result["quality"] in ("240p", "480p")
            ), "Adaptive quality did not reduce under constrained network"
