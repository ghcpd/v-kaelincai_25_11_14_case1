def resume_accuracy(stored_time, target_time):
    return abs(stored_time - target_time)

def should_skip_segment(segment_id, learned_segments):
    return segment_id in learned_segments

def clamp_playback_rate(rate, min_rate=0.5, max_rate=2.0):
    return max(min_rate, min(max_rate, rate))
