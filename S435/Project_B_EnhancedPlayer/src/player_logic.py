def should_skip(current_time, learned_segments):
    for s in learned_segments:
        if current_time>=s['start'] and current_time < s['end']:
            return True, s['end']
    return False, current_time

# simple resume store/retrieve functions using a dict
store = {}

def save_progress(user_id, time_s):
    store[user_id] = time_s

def load_progress(user_id):
    return store.get(user_id, 0)
