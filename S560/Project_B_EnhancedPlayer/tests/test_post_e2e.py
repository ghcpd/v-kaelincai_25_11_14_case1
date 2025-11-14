import os, subprocess, time, json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SERVER_SCRIPT = os.path.join(ROOT, 'server_post.py')

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


def test_enhanced_resume_speed_and_skip(tmp_path):
    server_proc = start_server()
    results = {}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            # Load with a slow network simulation; use mock
            url = 'http://127.0.0.1:8002/?use_mock=1&bw_kbps=600&latency_ms=70'
            page.goto(url)
            # Wait for playing
            page.wait_for_timeout(1000)
            # set speed to 1.5x via UI
            page.locator('#speedSelect').select_option('1.5')
            # mark segment as learned
            page.locator('#markSegmentBtn').click()
            # enable auto skip
            page.locator('#autoSkipToggle').click()
            # measure time to first frame
            ttf = page.evaluate('window.enhancedMetrics.timeToFirstFrameMs')
            results['time_to_first_frame_ms'] = ttf
            # check speed was persisted in sessionStorage
            speed = page.evaluate("sessionStorage.getItem('last_speed')")
            results['last_speed'] = speed
            # test jump by clicking first note
            page.locator('.note').first.click()
            # allow time to reflect in player
            page.wait_for_timeout(500)
            current_time = page.evaluate('document.getElementById("courseVideo").currentTime')
            results['after_jump_time'] = current_time
            # screenshot
            shot_path = tmp_path / 'screenshot_post_TC5.png'
            page.screenshot(path=str(shot_path))
            results['screenshot'] = str(shot_path)
            outdir = os.path.join(ROOT, 'results')
            os.makedirs(outdir, exist_ok=True)
            import shutil
            shutil.copy(str(shot_path), os.path.join(outdir, 'screenshot_post_TC5.png'))
            with open(os.path.join(outdir, 'results_post.json'), 'w') as fh:
                json.dump(results, fh, indent=2)
            browser.close()
    finally:
        stop_server(server_proc)
    assert float(results['time_to_first_frame_ms']) < 5000
    assert float(results['last_speed']) == 1.5
    assert abs(float(results['after_jump_time']) - 5.2) < 2.0

if __name__ == '__main__':
    test_enhanced_resume_speed_and_skip('.tmp')
