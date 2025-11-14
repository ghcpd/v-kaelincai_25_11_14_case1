import os, subprocess, time, json
import pytest
from playwright.sync_api import sync_playwright

SERVER_PORT=8002
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@pytest.mark.e2e
def test_enhanced_playback():
    proc = subprocess.Popen(['python', 'server_post.py'], cwd=ROOT)
    time.sleep(1)
    results={'tests':{}}
    try:
        import requests
        # add a learned segment for tests
        requests.post(f'http://localhost:{SERVER_PORT}/learned', json={'start':30,'end':60})
        td = json.load(open(os.path.join(ROOT,'..','test_data.json')))
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            for tcase in td['tests']:
                page.goto(f'http://localhost:{SERVER_PORT}/')
                net = tcase.get('network',{})
                page.evaluate(f'window.networkProfile = {{bandwidth_kbps: {net.get("bandwidth_kbps",1000)}, latency_ms: {net.get("latency_ms",50)}}}')
                if tcase['id']=='t1':
                    # resume
                    requests.post(f'http://localhost:{SERVER_PORT}/progress', data=json.dumps({'time':tcase['initial']['saved_time']}))
                    page.reload()
                    page.wait_for_timeout(500)
                    state = page.evaluate('window.player.getState()')
                    resumed = abs(state['currentTime']-tcase['initial']['saved_time']) < tcase['expect'].get('tolerance_s',1.0)
                    results['tests'][tcase['id']]={'resumed':resumed}
                elif tcase['id']=='t2':
                    for rate in [0.75,1.5,2]:
                        page.select_option('#rate',str(rate))
                        page.click('#play'); page.wait_for_timeout(200)
                        state = page.evaluate('window.player.getState()')
                        if abs(state['playbackRate']-rate) > 0.01:
                            results['tests'][tcase['id']]={'rate_applied':False}
                            break
                    else:
                        results['tests'][tcase['id']]={'rate_applied':True}
                elif tcase['id']=='t3':
                    page.check('#auto-skip')
                    # simulate seeking to start=30
                    page.evaluate('window.player.addLearned({start:30,end:60}); window.player.getState().currentTime = 30;')
                    page.wait_for_timeout(1200)
                    final_time = page.evaluate('window.player.getState().currentTime')
                    results['tests'][tcase['id']]={'skipped': final_time >= 60}
                elif tcase['id']=='t4':
                    # network constraints are simulated by setting networkProfile earlier
                    page.click('#play')
                    start=time.time()
                    ttf=None
                    for i in range(50):
                        page.wait_for_timeout(100)
                        ss=page.locator('#canvas').screenshot()
                        if ss:
                            ttf=(time.time()-start)*1000
                            break
                    # after a few frames quality may adapt
                    page.wait_for_timeout(1000)
                    state = page.evaluate('window.player.getState()')
                    results['tests'][tcase['id']]={'time_to_first_frame_ms':ttf,'quality':state.get('quality'),'rebufferCount': state.get('rebufferCount')}
                elif tcase['id']=='t5':
                    # add note and hover to jump
                    page.locator('.note').first.hover()
                    page.wait_for_timeout(100)
                    note_time = page.evaluate('window.player.getState().currentTime')
                    results['tests'][tcase['id']]={'note_time': note_time}
                # screenshot per case
                ss_path=os.path.join(ROOT,'screenshots',f'screenshot_post_{tcase['id']}.png')
                page.locator('#canvas').screenshot(path=ss_path)
            with open(os.path.join(ROOT,'results','results_post.json'),'w') as f:
                json.dump(results,f)
            with open(os.path.join(ROOT,'results','time_post.txt'),'w') as f:
                f.write(str(results))
            with open(os.path.join(ROOT,'logs','log_post.txt'),'w') as f:
                f.write('Enhanced playback tests completed')
            browser.close()
    finally:
        proc.terminate(); proc.wait()
