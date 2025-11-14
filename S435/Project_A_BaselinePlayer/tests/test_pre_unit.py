import pytest
import requests, subprocess, time, os

BASE='http://localhost:8001'
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def test_stream_response():
    proc = subprocess.Popen(['python','server_pre.py'], cwd=ROOT)
    time.sleep(1)
    try:
        r = requests.get(BASE+'/stream/360p?bandwidth_kbps=1000&latency_ms=10&t=1')
        assert r.status_code==200
        j=r.json()
    assert 'data' in j
    assert float(j['t'])==1.0
    # malformed timestamp
    r2 = requests.get(BASE+'/stream/360p?t=abc')
    assert r2.status_code==200
    finally:
        proc.terminate(); proc.wait()
