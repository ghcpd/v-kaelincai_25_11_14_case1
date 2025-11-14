import pytest
from src.player_logic import should_skip_current_time, clamp_time


def test_should_skip_true():
    learned = [[0,30],[90,105]]
    assert should_skip_current_time(15, learned) is True
    assert should_skip_current_time(95, learned) is True


def test_should_skip_false():
    learned = [[0,30],[90,105]]
    assert should_skip_current_time(80, learned) is False


def test_clamp_time():
    assert clamp_time(None, 100) == 0
    assert clamp_time(-5, 100) == 0
    assert clamp_time(120, 100) == 100
    assert clamp_time(50, 100) == 50
