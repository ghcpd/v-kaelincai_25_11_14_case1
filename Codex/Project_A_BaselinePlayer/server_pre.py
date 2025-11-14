import json
import os
import time
from pathlib import Path
from typing import Iterator

from flask import Flask, Response, jsonify, request

ROOT = Path(__file__).parent.resolve()
app = Flask(__name__, static_folder=str(ROOT / "src"), static_url_path="/static")


def ensure_mock_assets() -> None:
    mocks_dir = ROOT / "mocks"
    mocks_dir.mkdir(exist_ok=True)
    for quality in ("240p", "720p", "1080p"):
        path = mocks_dir / f"video_{quality}.mp4"
        if not path.exists():
            path.write_bytes(bytes([0]) * 4096)
    notes_path = mocks_dir / "notes.json"
    if not notes_path.exists():
        notes_path.write_text(
            json.dumps(
                [
                    {"t": 5.2, "text": "Baseline intro"},
                    {"t": 22.0, "text": "Important concept"},
                    {"t": 40.5, "text": "Summary note"},
                ],
                indent=2,
            ),
            encoding="utf-8",
        )


ensure_mock_assets()


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/healthz")
def healthz():
    return {"status": "ok", "project": "baseline"}


@app.route("/notes")
def notes():
    notes_path = ROOT / "mocks" / "notes.json"
    return jsonify(json.loads(notes_path.read_text(encoding="utf-8")))


def chunk_generator(path: Path, bw_kbps: int, latency_ms: int) -> Iterator[bytes]:
    # Baseline intentionally streams slowly (small chunks + fixed delay).
    delay = max(0.02, min(0.2, (1000.0 / max(1, bw_kbps)) + latency_ms / 1000.0))
    time.sleep(latency_ms / 1000.0)
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(512)
            if not chunk:
                break
            yield chunk
            time.sleep(delay)


@app.route("/video/<quality>")
def video(quality: str):
    path = ROOT / "mocks" / f"video_{quality}.mp4"
    if not path.exists():
        return ("quality not available", 404)
    bw = int(request.args.get("bw_kbps", 1000))
    latency = int(request.args.get("latency_ms", 50))
    return Response(chunk_generator(path, bw, latency), mimetype="video/mp4")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001, debug=False)
