def is_time_in_segment(t, seg):
    s, e = seg
    return s <= t <= e


def should_skip_current_time(t, learned_segments):
    for s,e in learned_segments:
        if s <= t <= e:
            return True
    return False


def clamp_time(t, duration):
    if t is None: return 0
    if t < 0: return 0
    if duration and t > duration: return duration
    return t
