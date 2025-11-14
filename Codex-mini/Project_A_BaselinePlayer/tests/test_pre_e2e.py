import json
import os
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "test_data.json"
RESULTS_FILE = ROOT / "results" / "results_pre.json"
TIME_FILE = ROOT / "results" / "time_pre.txt"
LOG_FILE = ROOT / "logs" / "log_pre.txt"
SCREENSHOTS_DIR = ROOT / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)


def load_test_data():
    return json.loads(DATA_FILE.read_text())


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2))


def append_log(message):
    timestamp = datetime.utcnow().isoformat()
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {message}\n")


def test_baseline_e2e_flow():
    data = load_test_data()
    metrics = []
    start_time = datetime.utcnow()
    append_log("Starting baseline E2E run")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:5000/", wait_until="domcontentloaded")
        page.wait_for_timeout(500)
        for test_case in data["tests"]:
            append_log(f"Running test case {test_case['id']}")
            result = page.evaluate("(scenario) => window.baselinePlayer.runScenario(scenario)", test_case)
            screenshot_path = SCREENSHOTS_DIR / f"screenshot_pre_{test_case['id']}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            entry = {
                "id": test_case["id"],
                "description": test_case["description"],
                "result": result,
                "pass": False,
            }
            metrics.append(entry)
            append_log(f"Finished {test_case['id']} result={entry['result']}")
        browser.close()

    elapsed = datetime.utcnow() - start_time
    report = {"tests": metrics, "elapsed_s": elapsed.total_seconds()}
    write_json(RESULTS_FILE, report)
    with open(TIME_FILE, "w", encoding="utf-8") as hand:
        hand.write(f"elapsed_s: {report['elapsed_s']:.3f}\n")
        hand.write("metrics captured from scenario playback\n")
    append_log("Baseline E2E run complete")
    assert len(report["tests"]) == len(data["tests"])
