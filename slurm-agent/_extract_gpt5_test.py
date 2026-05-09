import json

test_ids = set(json.load(open('evaluation/split_test_ids.json', encoding='utf-8')))
print(f'Test split: {len(test_ids)}')

data = json.load(open('evaluation/results/eval_all_20260504_rescored.json', encoding='utf-8'))
results = data['results']
print(f'Total results: {len(results)}')

test_results = [r for r in results if r.get('test_id') in test_ids]
print(f'Matched: {len(test_results)}')

n = len(test_results)
passes = sum(1 for r in test_results if r.get('passed', False))
avg_tool = sum(r.get('tool_recall', 0) for r in test_results) / n
avg_routing = sum(r.get('routing_match', 0) for r in test_results) / n
avg_hitl = sum(r.get('hitl_match', 0) for r in test_results) / n
avg_state = sum(r.get('state_match', 0) for r in test_results) / n
avg_latency = sum(r.get('latency_s', 0) for r in test_results) / n

print(f'\nGPT-5-mini on 615 test split:')
print(f'  Pass rate: {passes}/{n} = {passes*100/n:.1f}%')
print(f'  Avg tool recall: {avg_tool*100:.1f}%')
print(f'  Avg routing: {avg_routing*100:.1f}%')
print(f'  Avg HITL: {avg_hitl*100:.1f}%')
print(f'  Avg state: {avg_state*100:.1f}%')
print(f'  Avg latency: {avg_latency:.1f}s')
