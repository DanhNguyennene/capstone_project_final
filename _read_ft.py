import json
d = json.load(open('slurm-agent/evaluation/results/qwen14b_lora_final_test615_tmp.json'))
m = d['metrics']
print('n_tests:', m['n_tests'])
print('pass_rate:', m['pass_rate'])
print('avg_tool_recall:', m['avg_tool_recall'])
print('avg_routing_match:', m['avg_routing_match'])
print('avg_hitl_match:', m['avg_hitl_match'])
print('avg_state_match:', m['avg_state_match'])
print('avg_judge_score:', m['avg_judge_score'])
print('avg_overall:', m['avg_overall'])
print('avg_latency_s:', m['avg_latency_s'])
from collections import defaultdict
cats = defaultdict(lambda: {'pass':0,'total':0})
for r in d['results']:
    cat = r['category']
    cats[cat]['total'] += 1
    if r.get('passed'):
        cats[cat]['pass'] += 1
for cat in sorted(cats):
    c = cats[cat]
    pct = c['pass'] / c['total'] * 100
    print(f"  {cat}: {c['pass']}/{c['total']} = {pct:.1f}%")
