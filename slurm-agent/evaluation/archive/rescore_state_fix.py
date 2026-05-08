"""
Re-score existing eval results with the fixed state_match logic.
Does NOT re-run the agent — only re-computes scores from saved traces.

Fix: if agent called the expected destructive tool AND triggered HITL,
but the mock rejected the argument format, credit state_match=1.0
instead of penalizing with 0.0.
"""
import json
import copy
import sys
from pathlib import Path

DESTRUCTIVE_TOOLS = {
    "scancel", "scontrol_hold", "scontrol_release", "scontrol_update",
    "scontrol_requeue", "sbatch", "sacctmgr_modify", "sacctmgr_add",
    "sacctmgr_delete",
}

GT_ALIASES = {
    "sacctmgr_list": "sacctmgr_show",
    "sacctmgr_show": "sacctmgr_show",
}

ACTION_FAILURE_MARKERS = (
    "❌", "action blocked", "not admitted", "error:",
    "invalid job_id", "invalid job", "not found", "no such job",
)

WEIGHTS = {
    "tool_recall": 0.30,
    "routing_match": 0.25,
    "hitl_match": 0.25,
    "keyword_score": 0.10,
    "state_match": 0.10,
}
PASS_THRESHOLD = 0.70


def _destructive_action_failed(tool_call_history: list, expected_destructive: set) -> bool:
    if not expected_destructive:
        return False
    for entry in tool_call_history:
        tool = str(entry.get("tool", "") or "").lower().strip()
        tool = GT_ALIASES.get(tool, tool)
        if tool not in expected_destructive:
            continue
        output = str(entry.get("output", "") or "").strip().lower()
        if output and any(m in output for m in ACTION_FAILURE_MARKERS):
            return True
    return False


def rescore_state_match(test: dict, result: dict) -> float:
    """
    Re-compute state_match with the fixed logic.
    Only UPGRADES from 0→1 for the specific bug pattern:
      agent called correct destructive tool + triggered HITL + mock rejected args.
    Never downgrades existing scores.
    """
    old_score = float(result.get("state_match", 0.0))
    
    # Only fix cases that scored 0.0
    if old_score > 0.001:
        return old_score
    
    # Check: did the agent call the expected destructive tool AND trigger HITL?
    gt_tools = {GT_ALIASES.get(t, t) for t in test["ground_truth"]["tools"]}
    expected_destructive = gt_tools & DESTRUCTIVE_TOOLS
    
    if not expected_destructive:
        return old_score
    
    called = {GT_ALIASES.get(t, t) for t in result.get("agent_tools", [])}
    agent_hitl = result.get("agent_hitl", False)
    
    # The fix: agent called the right tool AND triggered HITL,
    # but mock rejected the argument format
    if bool(called & expected_destructive) and agent_hitl:
        history = result.get("tool_call_history", [])
        if _destructive_action_failed(history, expected_destructive):
            return 1.0
    
    return old_score


def rescore_overall(result: dict) -> float:
    return (
        WEIGHTS["tool_recall"] * result["tool_recall"] +
        WEIGHTS["routing_match"] * result["routing_match"] +
        WEIGHTS["hitl_match"] * result["hitl_match"] +
        WEIGHTS["keyword_score"] * result["keyword_score"] +
        WEIGHTS["state_match"] * result["state_match"]
    )


def main():
    dataset_path = Path("dataset.json")
    results_path = Path("results/eval_all_20260504_merged.json")
    output_path = Path("results/eval_all_20260504_rescored.json")
    
    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    results_raw = json.loads(results_path.read_text(encoding="utf-8"))
    
    if isinstance(results_raw, dict) and "results" in results_raw:
        cases = results_raw["results"]
    else:
        cases = results_raw
    
    # Index dataset by id
    test_by_id = {c["id"]: c for c in data}
    
    fixed_count = 0
    new_pass_count = 0
    
    rescored = copy.deepcopy(cases)
    
    for r in rescored:
        test_id = r["test_id"]
        test = test_by_id.get(test_id)
        if not test:
            continue
        
        old_state = r.get("state_match", 0.0)
        new_state = rescore_state_match(test, r)
        
        if abs(new_state - old_state) > 0.001:
            fixed_count += 1
            r["state_match"] = round(new_state, 3)
            # Recompute overall
            old_overall = r.get("overall", 0.0)
            r["overall"] = round(rescore_overall(r), 3)
            # Recompute passed
            r["passed"] = r["overall"] >= PASS_THRESHOLD
            if r["passed"] and not (old_overall >= PASS_THRESHOLD):
                new_pass_count += 1
    
    # Compute new aggregates
    n = len(rescored)
    new_pass_rate = sum(1 for r in rescored if r["passed"]) / n
    new_avg_state = sum(r["state_match"] for r in rescored) / n
    new_avg_overall = sum(r["overall"] for r in rescored) / n
    
    # Per category
    cats = {}
    for r in rescored:
        cat = r.get("category", "unknown")
        cats.setdefault(cat, []).append(r)
    
    print(f"Re-scored {fixed_count} cases (state_match changed)")
    print(f"New passes from rescore: {new_pass_count}")
    print(f"\n{'Metric':<25} {'Old':>10} {'New':>10}")
    print("-" * 47)
    
    old_pass_rate = sum(1 for r in cases if r.get("passed")) / len(cases)
    old_avg_state = sum(r.get("state_match", 0) for r in cases) / len(cases)
    
    print(f"{'Pass rate':<25} {old_pass_rate*100:>9.1f}% {new_pass_rate*100:>9.1f}%")
    print(f"{'Avg state_match':<25} {old_avg_state:>10.3f} {new_avg_state:>10.3f}")
    print(f"{'Avg overall':<25} {'':>10} {new_avg_overall:>10.3f}")
    
    print(f"\n{'Category':<15} {'Old state':>10} {'New state':>10} {'Fixed':>6}")
    print("-" * 45)
    for cat in sorted(cats.keys()):
        cat_cases = cats[cat]
        old_cat = [r for r in cases if r.get("category") == cat]
        old_avg = sum(r.get("state_match", 0) for r in old_cat) / len(old_cat) if old_cat else 0
        new_avg = sum(r["state_match"] for r in cat_cases) / len(cat_cases)
        n_fixed = sum(1 for r, o in zip(cat_cases, old_cat) if abs(r["state_match"] - o.get("state_match", 0)) > 0.001)
        if n_fixed > 0:
            print(f"{cat:<15} {old_avg:>10.3f} {new_avg:>10.3f} {n_fixed:>6}")
    
    # Save rescored results
    if isinstance(results_raw, dict) and "results" in results_raw:
        output = copy.deepcopy(results_raw)
        output["results"] = rescored
        output["rescore_note"] = "State-match rescored: credit agent when correct tool+HITL triggered but mock rejected argument format"
    else:
        output = rescored
    
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved rescored results to: {output_path}")


if __name__ == "__main__":
    main()
