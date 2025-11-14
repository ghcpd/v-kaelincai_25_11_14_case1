import pytest
from src.playback_utils import clamp_time


def test_clamp_time_basic():
    assert clamp_time(None, 100) == 0.0
    assert clamp_time(-5, 100) == 0.0
    assert clamp_time(30, 100) == 30.0
    assert clamp_time(120, 100) == 100.0
