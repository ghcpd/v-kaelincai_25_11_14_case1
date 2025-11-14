"""
Helper functions for the baseline player.
They are intentionally simple but unit-tested to provide parity with Project B's richer logic.
"""
from __future__ import annotations
from typing import Iterable, List, Tuple, Dict, Any


def sanitize_resume_time(saved_time: float, duration: float = 3600.0) -> float:
    """Clamp resume target into [0, duration]."""
    if saved_time is None:
        return 0.0
    saved_time = float(saved_time)
    if saved_time < 0:
        return 0.0
    if saved_time > duration:
        return duration
    return saved_time


def playback_rate() -> float:
    """Baseline player always uses 1× speed."""
    return 1.0


def should_skip_segment(current_time: float, learned_segments: Iterable[Tuple[float, float]]) -> bool:
    """Baseline never skips segments even if data exists."""
    _ = current_time, learned_segments
    return False


def normalize_notes(notes: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort notes by timestamp and drop malformed entries."""
    normalized: List[Dict[str, Any]] = []
    for note in notes:
        try:
            t = float(note["t"])
            text = str(note["text"])
        except (KeyError, TypeError, ValueError):
            continue
        normalized.append({"t": round(t, 2), "text": text})
    normalized.sort(key=lambda n: n["t"])
    return normalized
