import json
import os
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "test_data.json"
RESULTS_FILE = ROOT / "results" / "results_post.json"
TIME_FILE = ROOT / "results" / "time_post.txt"
LOG_FILE = ROOT / "logs" / "log_post.txt"
SCREENSHOTS_DIR = ROOT / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)


def load_test_data():
    return json.loads(DATA_FILE.read_text())


def append_log(message):
    timestamp = datetime.utcnow().isoformat()
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {message}\n")


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2))


def summarize(results):
    avg_resume = sum(r["result"].get("resume_accuracy", 0) for r in results) / len(results)
    res_switch = [d for r in results for d in r["result"].get("resolution_switch_ms", [])]
    avg_switch = sum(res_switch) / len(res_switch) if res_switch else 0
    return avg_resume, avg_switch


def test_enhanced_e2e_flow():
    data = load_test_data()
    results = []
    append_log("Starting enhanced E2E run")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:6000/", wait_until="domcontentloaded")
        page.wait_for_timeout(500)
        for test_case in data["tests"]:
            append_log(f"Running enhanced scenario {test_case['id']}")
            result = page.evaluate("(scenario) => window.enhancedPlayer.runScenario(scenario)", test_case)
            screenshot_path = SCREENSHOTS_DIR / f"screenshot_post_{test_case['id']}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            success = result["resume_accuracy"] <= data["acceptance_criteria"]["resume_tolerance_sec"]
            entry = {
                "id": test_case["id"],
                "description": test_case["description"],
                "result": result,
                "pass": success,
            }
            results.append(entry)
            append_log(f"Completed {test_case['id']} pass={success}")
        browser.close()
    write_json(RESULTS_FILE, {"tests": results})
    avg_resume, avg_switch = summarize(results)
    with open(TIME_FILE, "w", encoding="utf-8") as handle:
        handle.write(f"avg_resume_accuracy: {avg_resume:.2f}\n")
        handle.write(f"avg_resolution_switch_ms: {avg_switch:.2f}\n")
    append_log("Enhanced E2E run complete")
    assert len(results) == len(data["tests"])
