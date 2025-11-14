from flask import Flask, request, jsonify, send_from_directory
import time

app = Flask(__name__, static_folder="src", static_url_path="")
progress_store = {}
learned_segments = {}
notes_store = [
    {"t": 30, "text": "Introduction"},
    {"t": 90, "text": "Deep dive"},
    {"t": 150, "text": "Summary"},
]
resolutions = {
    "360p": {"bandwidth": 0.5},
    "480p": {"bandwidth": 1.5},
    "720p": {"bandwidth": 3.0},
}

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/player.js")
def player_js():
    return app.send_static_file("player.js")

@app.route("/api/notes")
def notes():
    return jsonify(notes_store)

@app.route("/api/segments")
def segments():
    resolution = request.args.get("res", "360p")
    bandwidth = float(request.args.get("bandwidth", 2.0))
    latency = float(request.args.get("latency", 0.05))
    simulated = min(1.0, 0.05 + latency + 1.0 / max(0.1, bandwidth))
    time.sleep(simulated)
    return jsonify({
        "resolution": resolution,
        "bandwidth": bandwidth,
        "latency": latency,
        "simulated_delay": simulated,
    })

@app.route("/api/progress", methods=["GET", "POST"])
def progress():
    user = request.args.get("user", "anonymous")
    if request.method == "POST":
        payload = request.json or {}
        position = payload.get("position", 0)
        progress_store[user] = position
        return jsonify({"user": user, "saved": position})
    saved = progress_store.get(user, 0)
    return jsonify({"user": user, "position": saved})

@app.route("/api/learned", methods=["POST"])
def learned_route():
    payload = request.json or {}
    user = payload.get("user", "anonymous")
    segments = payload.get("segments", [])
    learned_segments[user] = segments
    return jsonify({"user": user, "learned": segments})

@app.route("/api/learned", methods=["GET"])
def learned_get():
    user = request.args.get("user", "anonymous")
    return jsonify({"user": user, "learned": learned_segments.get(user, [])})


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("src", path)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Post-enhancement mock server")
    parser.add_argument("--port", type=int, default=6000)
    args = parser.parse_args()
    app.run(host="0.0.0.0", port=args.port)
