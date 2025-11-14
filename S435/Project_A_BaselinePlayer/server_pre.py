from flask import Flask, send_from_directory, request, jsonify
import base64, time
app = Flask(__name__, static_folder='src')

@app.route('/')
def index():
    return send_from_directory('src', 'index.html')

@app.route('/player.js')
def player_js():
    return send_from_directory('src', 'player.js')

@app.route('/stream/<quality>')
def stream(quality):
    # Simulate different quality latency: '360p' default, '720p' slower
    t = request.args.get('t', '0')
    bandwidth = int(request.args.get('bandwidth_kbps', '1000'))
    latency = int(request.args.get('latency_ms', '50'))
    # simulate processing
    time.sleep(latency/1000.0)
    # build an SVG as an image data URI with timestamp info for clarity
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360'><rect width='100%' height='100%' fill='green'/><text x='20' y='40' font-size='34' fill='white'>Frame t={t} q={quality}</text></svg>"
    b64 = base64.b64encode(svg.encode('utf-8')).decode('ascii')
    data_uri = 'data:image/svg+xml;base64,' + b64
    try:
        tval = float(t)
    except Exception:
        tval = 0.0
    return jsonify({'t': tval, 'data': data_uri})

if __name__ == '__main__':
    app.run(port=8001, debug=True)
