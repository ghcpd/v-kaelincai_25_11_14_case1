import os
import sys
import pytest

root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(root, "src"))
import player_logic


def test_resume_accuracy_function():
    assert player_logic.resume_accuracy(200.1, 199.2) == pytest.approx(0.9, rel=1e-3)


def test_auto_skip_finds_learned_segment():
    segments = [
        {"id": "seg3", "start": 50, "end": 85},
        {"id": "seg4", "start": 85, "end": 130},
    ]
    assert player_logic.should_auto_skip(52, segments, ["seg3"]) == 85
    assert player_logic.should_auto_skip(150, segments, ["seg3"]) is None


def test_choose_resolution_picker():
    assert player_logic.choose_resolution(4) == "720p"
    assert player_logic.choose_resolution(2) == "480p"
    assert player_logic.choose_resolution(0.5) == "360p"
