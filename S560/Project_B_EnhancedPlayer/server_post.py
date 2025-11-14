from flask import Flask, send_from_directory, Response, request, jsonify
import os, time, json

app = Flask(__name__, static_folder='src', static_url_path='/static')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'mocks')
PROGRESS_STORE = {}
LEARNED_STORE = {}

os.makedirs(DATA_DIR, exist_ok=True)
# Ensure example video files exist (same placeholder approach)
for q in ('240p','720p','1080p'):
    p = os.path.join(DATA_DIR, f'video_{q}.mp4')
    if not os.path.exists(p):
        with open(p, 'wb') as fh:
            fh.write(b'\x00' * 1024)  # small placeholder

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/progress', methods=['POST'])
def save_progress():
    try:
        data = request.get_json(force=True)
        user = request.remote_addr or 'anon'
        PROGRESS_STORE[user] = data
        # Echo a success
        return jsonify({'status':'ok', 'stored': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/learned_segments', methods=['POST'])
def save_learned():
    try:
        data = request.get_json(force=True)
        user = request.remote_addr or 'anon'
        LEARNED_STORE[user] = data
        return jsonify({'status': 'ok', 'stored': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/video/<quality>')
def video_stream(quality):
    path = os.path.join(DATA_DIR, f'video_{quality}.mp4')
    if not os.path.exists(path):
        return 'not found', 404
    # adjust streaming based on query params
    bw = int(request.args.get('bw_kbps', 1000))
    latency = int(request.args.get('latency_ms', 20))
    def generate():
        time.sleep(latency/1000.0)
        with open(path,'rb') as fh:
            while True:
                chunk = fh.read(2048)
                if not chunk: break
                yield chunk
                # speed up or slow down chunk intervals based on requested bandwidth
                time.sleep(0.01 + max(0.0, (1000.0/(1 + bw/100.0)) / 1000.0))
    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    app.run(port=8002)
