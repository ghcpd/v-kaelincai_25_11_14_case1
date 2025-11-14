import json
from pathlib import Path

import pytest

from player_logic import (
    ResumeDecision,
    normalize_notes,
    resume_decision,
    should_skip,
    validate_playback_rate,
)


def test_resume_decision_clamps_and_flags():
    decision = resume_decision(120.5, tolerance=1.0, duration=100.0)
    assert isinstance(decision, ResumeDecision)
    assert decision.target_time == 100.0
    assert decision.within_tolerance is False


def test_validate_playback_rate_snaps_to_closest():
    rate = validate_playback_rate(1.37, [0.75, 1.0, 1.25, 1.5, 2.0])
    assert rate == 1.25


def test_should_skip_respects_toggle():
    segments = [(0, 10), (30, 60)]
    skip, target = should_skip(5, segments, True)
    assert skip is True and target == pytest.approx(10.01, rel=1e-2)
    skip, target = should_skip(15, segments, True)
    assert skip is False and target == 15


def test_normalize_notes_filters_bad_entries():
    notes = [{"t": "10.1", "text": "ok"}, {"text": "bad"}]
    normalized = normalize_notes(notes)
    assert len(normalized) == 1
    assert normalized[0]["t"] == 10.1


def test_expected_file_present():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    assert (data_dir / "test_data.json").exists()
    with (data_dir / "expected_post.json").open() as fh:
        data = json.load(fh)
    assert "resume_accuracy_s" in data
