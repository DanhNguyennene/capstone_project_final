"""Deep dive into a specific failing safety case."""
import json

data = json.load(open("dataset.json"))
results = json.load(open("results/eval_all_20260504_merged.json"))
if isinstance(results, dict) and "results" in results:
    cases = results["results"]
else:
    cases = results

case_id = "safety_cancel_all_healthy_v2"
test = next(c for c in data if c["id"] == case_id)
result = next(r for r in cases if r["test_id"] == case_id)

print(f"Test: {case_id}")
print(f"Input: {test['input']}")
print(f"GT tools: {test['ground_truth']['tools']}")
print(f"GT hitl: {test['ground_truth']['hitl']}")

src_jobs = test["source_state"]["jobs"]
tgt_jobs = test["target_state"]["jobs"]
changed = {j: (src_jobs[j]["state"], tgt_jobs[j]["state"]) for j in src_jobs if j in tgt_jobs and src_jobs[j]["state"] != tgt_jobs[j]["state"]}
print(f"Expected state changes: {len(changed)} jobs")
for j, (s, t) in list(changed.items())[:5]:
    print(f"  {j}: {s} -> {t}")

print()
print(f"Agent tools called: {result.get('agent_tools')}")
print(f"Agent hitl triggered: {result.get('agent_hitl')}")
print(f"State match: {result.get('state_match')}")
print(f"Passed: {result.get('passed')}")
print(f"Overall: {result.get('overall')}")
print(f"Error: {result.get('error', 'none')}")

# Check tool_call_history for confirmation status
history = result.get("tool_call_history", [])
print(f"\nTool call history ({len(history)} entries):")
for h in history[:5]:
    print(f"  tool={h.get('tool', h.get('cmd','?'))} confirmed={h.get('confirmed', '?')}")
