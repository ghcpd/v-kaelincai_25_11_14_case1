def simulate_delay(bandwidth_mbps, size_kb=150):
    # simple dt calculation
    bandwidth_kbps = max(0.1, bandwidth_mbps * 1000)
    delay = size_kb / bandwidth_kbps
    return max(0.05, delay)
