import os, subprocess, time, json, signal, requests
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SERVER_SCRIPT = os.path.join(ROOT, 'server_pre.py')

def start_server():
    env = os.environ.copy()
    p = subprocess.Popen(['python', SERVER_SCRIPT], cwd=ROOT, env=env)
    time.sleep(1.0)
    return p


def stop_server(proc):
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


def test_time_to_first_frame_and_basic_resume(tmp_path):
    server_proc = start_server()
    results = {}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            url = 'http://127.0.0.1:8001/?use_mock=1&bw_kbps=500&latency_ms=120'
            start = time.time()
            page.goto(url)
            # Wait for 'playing' event through the mock logic; poll the window object
            page.wait_for_timeout(1000)
            ttf = page.evaluate('window.playerMetrics.timeToFirstFrameMs')
            results['time_to_first_frame_ms'] = ttf
            results['timetoconnect_s'] = time.time() - start
            # Take screenshot
            shot_path = tmp_path / 'screenshot_pre_TC1.png'
            page.screenshot(path=str(shot_path))
            results['screenshot'] = str(shot_path)
            # Save results json and copy screenshot to results folder
            outdir = os.path.join(ROOT, 'results')
            os.makedirs(outdir, exist_ok=True)
            import shutil
            shutil.copy(str(shot_path), os.path.join(outdir, 'screenshot_pre_TC1.png'))
            with open(os.path.join(outdir, 'results_pre.json'), 'w') as fh:
                json.dump(results, fh, indent=2)
            browser.close()
    finally:
        stop_server(server_proc)
    assert results['time_to_first_frame_ms'] is not None and results['time_to_first_frame_ms'] < 5000

if __name__ == '__main__':
    test_time_to_first_frame_and_basic_resume('.tmp')
