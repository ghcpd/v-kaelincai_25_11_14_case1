def resume_accuracy(stored, target):
    return abs(stored - target)

def should_auto_skip(current_time, segments, learned, tolerance=0.2):
    for segment in segments:
        if segment["id"] in learned and segment["start"] - tolerance <= current_time < segment["end"]:
            return segment["end"]
    return None

def choose_resolution(bandwidth_mbps):
    if bandwidth_mbps >= 3:
        return "720p"
    if bandwidth_mbps >= 1.5:
        return "480p"
    return "360p"
