import os, subprocess, time, json
import pytest
from playwright.sync_api import sync_playwright

SERVER_PORT=8001
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@pytest.mark.e2e
def test_playback():
    # Start server
    proc = subprocess.Popen(['python', 'server_pre.py'], cwd=ROOT)
    time.sleep(1)
    results={'tests':{}}
    try:
        # load test vectors
        td = json.load(open(os.path.join(ROOT,'..','test_data.json')))
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            for t in td['tests']:
                start=time.time()
                page.goto(f'http://localhost:{SERVER_PORT}/')
                # set network profile
                net = t.get('network',{})
                page.evaluate(f'window.networkProfile = {{bandwidth_kbps: {net.get("bandwidth_kbps",1000)}, latency_ms: {net.get("latency_ms",50)}}}')
                page.click('#play')
                ttf=None
                for i in range(50):
                    page.wait_for_timeout(100)
                    img_bytes = page.locator('#canvas').screenshot()
                    if img_bytes:
                        ttf=(time.time()-start)*1000
                        break
                ss_path=os.path.join(ROOT,'screenshots',f'screenshot_pre_{t["id"]}.png')
                page.locator('#canvas').screenshot(path=ss_path)
                results['tests'][t['id']]={'time_to_first_frame_ms':ttf, 'pass': ttf is not None}
            with open(os.path.join(ROOT,'results','results_pre.json'),'w') as f:
                json.dump(results,f)
            with open(os.path.join(ROOT,'results','time_pre.txt'),'w') as f:
                f.write(str(results))
            with open(os.path.join(ROOT,'logs','log_pre.txt'),'w') as f:
                f.write('Play started, screenshots saved')
            browser.close()
    finally:
        proc.terminate()
        proc.wait()
