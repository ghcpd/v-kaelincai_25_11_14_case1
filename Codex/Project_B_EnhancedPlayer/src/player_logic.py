"""
Enhanced player helper logic shared with unit tests.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple


@dataclass
class ResumeDecision:
    target_time: float
    within_tolerance: bool


def resume_decision(saved_time: float, tolerance: float = 1.0, duration: float = 3600.0) -> ResumeDecision:
    """Clamp resume target and compute tolerance flag."""
    if saved_time is None:
        return ResumeDecision(0.0, True)
    target = max(0.0, min(float(saved_time), duration))
    within = abs(target - float(saved_time)) <= tolerance
    return ResumeDecision(target, within)


def validate_playback_rate(requested: float, allowed: Sequence[float]) -> float:
    """Return the closest supported playback rate."""
    if not allowed:
        raise ValueError("allowed rates required")
    closest = min(allowed, key=lambda x: abs(x - requested))
    return closest


def should_skip(current_time: float, segments: Iterable[Tuple[float, float]], enabled: bool) -> Tuple[bool, float]:
    """Determine whether the current time falls into a learned segment."""
    if not enabled:
        return False, current_time
    for start, end in segments:
        if start <= current_time <= end:
            return True, float(end) + 0.01
    return False, current_time


def normalize_notes(notes: Iterable[dict]) -> List[dict]:
    """Validate, sort, and clamp note data."""
    valid: List[dict] = []
    for note in notes:
        try:
            t = float(note["t"])
            text = str(note["text"])
        except (KeyError, TypeError, ValueError):
            continue
        valid.append({"t": round(t, 2), "text": text})
    valid.sort(key=lambda n: n["t"])
    return valid
