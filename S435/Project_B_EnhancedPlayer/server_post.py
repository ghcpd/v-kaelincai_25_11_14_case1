from flask import Flask, send_from_directory, request, jsonify
import time

app = Flask(__name__, static_folder='src')
# in-memory store
store={'progress':{}, 'learned':[], 'notes':[{'t':120.5,'text':'Key point'}]}

@app.route('/')
def index():
    return send_from_directory('src','index.html')

@app.route('/player.js')
def player_js():
    return send_from_directory('src','player.js')

@app.route('/progress', methods=['GET','POST'])
def progress():
    if request.method=='POST':
        data=request.get_data().decode('utf-8')
        try:
            import json
            d=json.loads(data)
            store['progress']['time']=d.get('time',0)
        except Exception:
            pass
        return jsonify({'status':'ok'})
    return jsonify(store['progress'])

@app.route('/meta')
def meta():
    return jsonify({'learned': store['learned'], 'notes': store['notes']})

@app.route('/learned', methods=['POST'])
def learned():
    d=request.json
    store['learned'].append(d)
    return jsonify({'status':'ok'})

@app.route('/stream/<quality>')
def stream(quality):
    # similar to pre, but simulate different delays and larger sizes for high quality
    t = request.args.get('t', '0')
    bandwidth = int(request.args.get('bandwidth_kbps', '1000'))
    latency = int(request.args.get('latency_ms', '50'))
    if quality=='720p':
        time.sleep(latency/1000.0 + 0.2)
    else:
        time.sleep(latency/1000.0)
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360'><rect width='100%' height='100%' fill='purple'/><text x='20' y='40' font-size='34' fill='white'>Frame t={t} q={quality}</text></svg>"
    import base64
    b64 = base64.b64encode(svg.encode('utf-8')).decode('ascii')
    data_uri = 'data:image/svg+xml;base64,' + b64
    try:
        tval = float(t)
    except Exception:
        tval = 0.0
    return jsonify({'t': tval, 'data': data_uri})

if __name__=='__main__':
    app.run(port=8002, debug=True)
