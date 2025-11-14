import json
import os
import time
from pathlib import Path
from typing import Iterator

from flask import Flask, Response, jsonify, request

ROOT = Path(__file__).parent.resolve()
app = Flask(__name__, static_folder=str(ROOT / "src"), static_url_path="/static")

PROGRESS_STORE = {}
LEARNED_STORE = {}


def ensure_assets() -> None:
    mocks = ROOT / "mocks"
    mocks.mkdir(exist_ok=True)
    for quality in ("240p", "480p", "720p", "1080p"):
        path = mocks / f"video_{quality}.mp4"
        if not path.exists():
            path.write_bytes(bytes([0]) * 8192)
    notes_path = mocks / "notes.json"
    if not notes_path.exists():
        notes_path.write_text(
            json.dumps(
                [
                    {"t": 5.2, "text": "Intro context"},
                    {"t": 22.0, "text": "Important concept"},
                    {"t": 40.5, "text": "Summary call-out"},
                    {"t": 65.2, "text": "Deep dive"},
                ],
                indent=2,
            ),
            encoding="utf-8",
        )


ensure_assets()


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/healthz")
def healthz():
    return {"status": "ok", "project": "enhanced"}


@app.route("/notes")
def notes():
    notes_path = ROOT / "mocks" / "notes.json"
    return jsonify(json.loads(notes_path.read_text(encoding="utf-8")))


@app.route("/progress", methods=["POST"])
def save_progress():
    payload = request.get_json(force=True)
    user = payload.get("courseId", "unknown")
    PROGRESS_STORE[user] = payload
    return jsonify({"status": "ok", "received": payload})


@app.route("/learned_segments", methods=["POST"])
def save_learned():
    payload = request.get_json(force=True)
    user = request.remote_addr or "anon"
    LEARNED_STORE[user] = payload
    return jsonify({"status": "ok", "count": len(payload or [])})


def adaptive_chunk_generator(path: Path, bw_kbps: int, latency_ms: int) -> Iterator[bytes]:
    # Simulate jitter-aware adaptive streaming.
    time.sleep(latency_ms / 1000.0)
    chunk_size = max(512, int(2048 * max(0.25, min(2.0, bw_kbps / 1000.0))))
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(chunk_size)
            if not chunk:
                break
            yield chunk
            sleep_time = max(0.005, (1000.0 / max(100.0, bw_kbps)) / 10.0)
            time.sleep(sleep_time)


@app.route("/video/<quality>")
def video(quality: str):
    path = ROOT / "mocks" / f"video_{quality}.mp4"
    if not path.exists():
        return ("quality not available", 404)
    bw = int(request.args.get("bw_kbps", 1200))
    latency = int(request.args.get("latency_ms", 40))
    return Response(adaptive_chunk_generator(path, bw, latency), mimetype="video/mp4")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8002, debug=False)
