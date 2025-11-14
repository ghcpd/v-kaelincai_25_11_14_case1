import json
from pathlib import Path

from player_logic import (
    normalize_notes,
    playback_rate,
    sanitize_resume_time,
    should_skip_segment,
)


def test_sanitize_resume_time_clamps_values():
    assert sanitize_resume_time(-5) == 0.0
    assert sanitize_resume_time(50.5) == 50.5
    assert sanitize_resume_time(4000, duration=100.0) == 100.0


def test_playback_rate_baseline_fixed():
    assert playback_rate() == 1.0


def test_should_skip_segment_never_true():
    segments = [(0, 10), (20, 30)]
    assert should_skip_segment(5, segments) is False
    assert should_skip_segment(25, segments) is False


def test_normalize_notes_sorts_and_filters(tmp_path: Path):
    notes = [
        {"t": "10.25", "text": "B"},
        {"t": 3, "text": "A"},
        {"text": "invalid"},
    ]
    normalized = normalize_notes(notes)
    assert [n["text"] for n in normalized] == ["A", "B"]
    assert normalized[0]["t"] == 3.0


def test_test_data_file_present():
    data_file = Path(__file__).resolve().parents[1] / "data" / "test_data.json"
    assert data_file.exists(), "test_data.json missing for baseline project"
    with data_file.open() as fh:
        data = json.load(fh)
    assert len(data) >= 5
