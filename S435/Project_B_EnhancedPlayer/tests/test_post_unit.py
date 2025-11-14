import requests, subprocess, time, os

BASE='http://localhost:8002'
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def test_progress_endpoints():
    proc = subprocess.Popen(['python','server_post.py'], cwd=ROOT)
    time.sleep(1)
    try:
        r = requests.post(BASE+'/progress', data='{"time":77}')
        assert r.status_code==200
        r2 = requests.get(BASE+'/progress')
        j=r2.json()
        assert abs(j.get('time',0) - 77) < 0.01
    finally:
        proc.terminate(); proc.wait()


def test_should_skip_logic():
    from src.player_logic import should_skip
    segments=[{'start':30,'end':60}]
    skip, newt = should_skip(35,segments)
    assert skip and newt==60
    skip2,newt2 = should_skip(10,segments)
    assert not skip2 and newt2==10

