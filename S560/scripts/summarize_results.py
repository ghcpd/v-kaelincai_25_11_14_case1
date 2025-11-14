import json, sys

def summarize(path, outpath):
    try:
        data = json.load(open(path))
    except Exception as e:
        print('failed to read', path, e)
        return
    with open(outpath, 'w') as fh:
        fh.write('time_to_first_frame_ms: {}\n'.format(data.get('time_to_first_frame_ms', 'TBD')))
        fh.write('avg_stall_duration_ms: {}\n'.format(data.get('avg_stall_duration_ms', 'TBD')))
        fh.write('resolution_switch_ms: {}\n'.format(data.get('resolution_switch_ms', 'TBD')))

if __name__ == '__main__':
    summarize('Project_A_BaselinePlayer/results/results_pre.json','Project_A_BaselinePlayer/results/time_pre.txt')
    summarize('Project_B_EnhancedPlayer/results/results_post.json','Project_B_EnhancedPlayer/results/time_post.txt')
    print('Summaries written')
