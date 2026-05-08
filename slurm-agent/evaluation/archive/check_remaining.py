"""Quick check on remaining safety state_match=0 cases."""
import json

new = json.loads(open("results/eval_all_20260504_rescored.json", encoding="utf-8").read())
nc = new.get("results", new) if isinstance(new, dict) else new
safety_still_0 = [r for r in nc if r.get("category") == "safety" and r["state_match"] < 0.001]
print(f"Safety still state=0: {len(safety_still_0)}")
for r in safety_still_0[:8]:
    tid = r["test_id"]
    hitl = r["agent_hitl"]
    tools = r["agent_tools"][:4]
    print(f"  {tid}: hitl={hitl} tools={tools}")
