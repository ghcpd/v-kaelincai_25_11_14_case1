import json
pre = {}
post = {}
try:
    pre = json.load(open('results/results_pre.json'))
except Exception:
    pre = {"error":"no_pre_results"}
try:
    post = json.load(open('results/results_post.json'))
except Exception:
    post = {"error":"no_post_results"}
with open('compare_report.md','w') as fh:
    fh.write('# Compare Report\n')
    fh.write('\n## Pre vs Post Results\n')
    fh.write('\n### Pre:\n')
    fh.write(json.dumps(pre, indent=2))
    fh.write('\n\n### Post:\n')
    fh.write(json.dumps(post, indent=2))
print('Compare report generated at compare_report.md')
