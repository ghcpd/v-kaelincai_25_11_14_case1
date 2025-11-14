# Playback utilities for baseline project (simple helpers)

def clamp_time(t, duration):
    """Ensure time is within 0..duration"""
    if t is None: return 0.0
    if t < 0: return 0.0
    if duration and t > duration: return float(duration)
    return float(t)


def format_time_s(t):
    return f"{t:.1f}s"
