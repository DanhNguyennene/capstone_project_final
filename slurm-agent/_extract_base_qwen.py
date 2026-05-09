import json

d = json.load(open('evaluation/results/eval_all_slurm-agent_test_20260509_080506.json', encoding='utf-8'))
results = d['results']
n = len(results)

passes = sum(1 for r in results if r.get('passed', False))
avg_tool = sum(r.get('tool_recall', 0) for r in results) / n
avg_routing = sum(r.get('routing_match', 0) for r in results) / n
avg_hitl = sum(r.get('hitl_match', 0) for r in results) / n
avg_state = sum(r.get('state_match', 0) for r in results) / n
avg_latency = sum(r.get('latency_s', 0) for r in results) / n
errors = sum(1 for r in results if r.get('error'))

print(f'Base Qwen2.5-14B on 615 test split:')
print(f'  Pass rate: {passes}/{n} = {passes*100/n:.1f}%')
print(f'  Avg tool recall: {avg_tool*100:.1f}%')
print(f'  Avg routing: {avg_routing*100:.1f}%')
print(f'  Avg HITL: {avg_hitl*100:.1f}%')
print(f'  Avg state: {avg_state*100:.1f}%')
print(f'  Avg latency: {avg_latency:.1f}s')
print(f'  Errors: {errors}')
print()
print(f'Model: {d.get("model")}')
print(f'Split: {d.get("split")}')
print(f'Built-in metrics: {json.dumps(d.get("metrics"), indent=2)}')
