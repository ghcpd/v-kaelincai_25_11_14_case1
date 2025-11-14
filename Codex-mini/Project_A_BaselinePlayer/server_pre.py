from flask import Flask, send_from_directory, jsonify, request
import time

app = Flask(__name__, static_folder="src", static_url_path="")

@app.route("/")
def index():
    return send_from_directory("src", "index.html")

@app.route("/player.js")
def player_js():
    return send_from_directory("src", "player.js")

@app.route("/api/segments")
def segments():
    resolution = request.args.get("res", "480p")
    bandwidth = float(request.args.get("bandwidth", 1.0))
    latency = float(request.args.get("latency", 0.1))
    simulated_delay = min(0.75, latency + 1.0 / max(0.1, bandwidth))
    time.sleep(simulated_delay)
    return jsonify({
        "resolution": resolution,
        "fetched_at": time.time(),
        "simulated_delay": simulated_delay,
    })

@app.route("/api/notes")
def notes():
    return jsonify([
        {"t": 10, "text": "Introduction"},
        {"t": 45, "text": "Key concept"},
        {"t": 90, "text": "Summary"},
    ])


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("src", path)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Baseline mock video server")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    app.run(host="0.0.0.0", port=args.port)
