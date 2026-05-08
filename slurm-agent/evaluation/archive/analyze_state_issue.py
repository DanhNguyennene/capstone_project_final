"""Analyze safety/bulk cases with state-match issues in the dataset."""
import json

data = json.load(open("dataset.json"))
safety_cases = [c for c in data if c.get("category") == "safety"]
bulk_cases = [c for c in data if c.get("category") == "bulk"]

print(f"Total cases: {len(data)}")
print(f"Safety cases: {len(safety_cases)}")
print(f"Bulk cases: {len(bulk_cases)}")
print()

# Safety analysis
hitl_true = [c for c in safety_cases if c["ground_truth"].get("hitl")]
hitl_false = [c for c in safety_cases if not c["ground_truth"].get("hitl")]
print(f"Safety hitl=True: {len(hitl_true)}")
print(f"Safety hitl=False: {len(hitl_false)}")

hitl_true_no_change = []
hitl_true_with_change = []
for c in hitl_true:
    src = c.get("source_state", {}).get("jobs", {})
    tgt = c.get("target_state", {}).get("jobs", {})
    if src == tgt:
        hitl_true_no_change.append(c)
    else:
        hitl_true_with_change.append(c)

print(f"  hitl=True, no state delta: {len(hitl_true_no_change)}")
print(f"  hitl=True, with state delta: {len(hitl_true_with_change)}")
print()

# The 107 cases with hitl=True but source==target:
# These expect the agent to trigger HITL. The target_state == source_state means
# the scorer expects NO destructive tool to be called (or no state change).
# But if the GT tools include a destructive tool, the scorer checks if it was called.
# This is the conflict!

print("--- hitl=True, no state delta, but has destructive GT tools ---")
DESTRUCTIVE = {"scancel", "scontrol_hold", "scontrol_release", "scontrol_update", "sbatch", "sacctmgr_modify"}
count_problem = 0
for c in hitl_true_no_change:
    gt_tools = set(c["ground_truth"]["tools"])
    if gt_tools & DESTRUCTIVE:
        count_problem += 1
        if count_problem <= 3:
            print(f"  ID: {c['id']}")
            print(f"  Prompt: {c['input'][:100]}")
            print(f"  GT tools: {c['ground_truth']['tools']}")
            print()
print(f"  Total: {count_problem}")
print()

# Bulk analysis  
print("--- Bulk cases ---")
bulk_with_change = [c for c in bulk_cases if c.get("source_state", {}).get("jobs", {}) != c.get("target_state", {}).get("jobs", {})]
print(f"Bulk with state change: {len(bulk_with_change)}")
bulk_hitl = [c for c in bulk_cases if c["ground_truth"].get("hitl")]
print(f"Bulk with hitl=True: {len(bulk_hitl)}")

# Count multi-job state changes in bulk
multi_job_changes = 0
for c in bulk_with_change:
    src = c.get("source_state", {}).get("jobs", {})
    tgt = c.get("target_state", {}).get("jobs", {})
    changed = [j for j in src if j in tgt and src[j].get("state") != tgt[j].get("state")]
    if len(changed) > 1:
        multi_job_changes += 1
print(f"Bulk with multi-job state changes: {multi_job_changes}")
