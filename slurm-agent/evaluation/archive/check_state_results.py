"""Check actual eval results for state_match failures in safety/bulk."""
import json

results = json.load(open("results/eval_all_20260504_merged.json"))
if isinstance(results, dict) and "results" in results:
    cases = results["results"]
else:
    cases = results

print(f"Total results: {len(cases)}")

for cat in ["safety", "bulk"]:
    cat_results = [r for r in cases if r.get("category") == cat]
    if not cat_results:
        print(f"\n{cat}: no results")
        continue
    low_state = [r for r in cat_results if float(r.get("state_match", 1.0)) < 1.0]
    avg_state = sum(float(r.get("state_match", 0)) for r in cat_results) / len(cat_results)
    print(f"\n{cat}: {len(cat_results)} results")
    print(f"  state_match < 1.0: {len(low_state)}")
    print(f"  avg state_match: {avg_state:.3f}")
    
    # Show some failing ones
    for r in low_state[:3]:
        print(f"  FAIL: {r['test_id']} state={r.get('state_match')} hitl={r.get('agent_hitl')} tools={r.get('agent_tools', [])[:3]}")
