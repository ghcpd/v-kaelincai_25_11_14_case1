from flask import Flask, send_file, Response, request, jsonify, render_template_string
import os, time, base64

app = Flask(__name__, static_folder='src', static_url_path='/static')

# Write a small minimal mp4 file using base64 data if not present
MP4_B64 = 'AAAAIGZ0eXBtcDQyAAAAAG1wNDEAAAC6bW9vdgAAAGxtdmhkAAAAANr...'  # truncated placeholder

VIDEO_BYTES = base64.b64decode(MP4_B64 + 'A')[:1024] if MP4_B64 else b'0'  # placeholder

VIDEO_DIR = os.path.join(os.path.dirname(__file__), 'mocks')
os.makedirs(VIDEO_DIR, exist_ok=True)
for q in ('240p','720p','1080p'):
    p = os.path.join(VIDEO_DIR, f'video_{q}.mp4')
    if not os.path.exists(p):
        with open(p, 'wb') as f:
            f.write(VIDEO_BYTES)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/video/<quality>')
def video_stream(quality):
    # Simulate a slow server by streaming the file with small delays (baseline behavior={no optimization})
    file_path = os.path.join('mocks', f'video_{quality}.mp4')
    if not os.path.exists(file_path):
        return 'quality not found', 404
    def generate():
        with open(file_path, 'rb') as fh:
            while True:
                chunk = fh.read(512)
                if not chunk:
                    break
                yield chunk
                time.sleep(0.08)  # baseline: slow streaming to simulate bandwidth strain
    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    app.run(port=8001)
