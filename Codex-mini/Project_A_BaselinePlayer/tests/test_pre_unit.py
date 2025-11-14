import os
import sys

root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(root, "src"))
import pytest
import player_logic


def test_resume_accuracy_baseline():
    assert player_logic.resume_accuracy(125.7, 124.9) == pytest.approx(0.8, rel=1e-3)


def test_skip_detects_learned_segment():
    assert player_logic.should_skip_segment("seg1", ["seg1", "seg2"])
    assert not player_logic.should_skip_segment("seg3", ["seg1"])


def test_clamp_playback_rate():
    assert player_logic.clamp_playback_rate(3.0) == 2.0
    assert player_logic.clamp_playback_rate(0.1) == 0.5
    assert player_logic.clamp_playback_rate(1.25) == 1.25
