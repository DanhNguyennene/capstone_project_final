"""Check if routing metric creates unfair bias against monolithic."""
import json

d = json.load(open('evaluation/dataset.json'))
mono = json.load(open('evaluation/results/base_qwen14b_monolithic_test615.json'))
split = json.load(open('evaluation/results/base_qwen14b_test615.json'))

test_ids = set(r['test_id'] for r in mono['results'])
tests = {t['id']: t for t in d if t['id'] in test_ids}
mono_results = {r['test_id']: r for r in mono['results']}
split_results = {r['test_id']: r for r in split['results']}

print("=" * 60)
print("ROUTING BIAS ANALYSIS")
print("=" * 60)

# How many test cases expect handoff?
ho_true = [tid for tid in test_ids if tests[tid].get('ground_truth', {}).get('handoff')]
ho_false = [tid for tid in test_ids if not tests[tid].get('ground_truth', {}).get('handoff')]
print(f"\nIn 615 test split:")
print(f"  handoff=True (expect Operator):  {len(ho_true)} ({len(ho_true)/615*100:.0f}%)")
print(f"  handoff=False (Observer-only):   {len(ho_false)} ({len(ho_false)/615*100:.0f}%)")
print(f"\nMonolithic NEVER triggers handoff → routing=0 for ALL {len(ho_true)} handoff cases")
print(f"This costs monolithic 0.25 × {len(ho_true)}/615 = {0.25*len(ho_true)/615*100:.1f}% on overall avg")

# Recalculate pass rates WITHOUT routing metric (reweight to sum=1)
# Original: tool=0.30, routing=0.25, hitl=0.25, kw=0.10, state=0.10
# Without routing: renormalize remaining 0.75 → 1.0
# tool=0.40, hitl=0.333, kw=0.133, state=0.133
def calc_no_routing(r):
    tr = r.get('tool_recall', 0)
    hitl = r.get('hitl_match', 0)
    kw = r.get('keyword_score', 0)
    state = r.get('state_match', 0)
    return 0.40 * tr + 0.333 * hitl + 0.133 * kw + 0.133 * state

mono_pass_no_route = sum(1 for r in mono['results'] if calc_no_routing(r) >= 0.80)
split_pass_no_route = sum(1 for r in split['results'] if calc_no_routing(r) >= 0.80)
mono_pass_orig = sum(1 for r in mono['results'] if r.get('passed'))
split_pass_orig = sum(1 for r in split['results'] if r.get('passed'))

print(f"\n{'='*60}")
print("PASS RATES: ORIGINAL vs ROUTING-REMOVED")
print(f"{'='*60}")
print(f"{'Metric':<30} {'Split':>10} {'Monolithic':>12} {'Delta':>8}")
print(f"{'-'*60}")
print(f"{'Original (with routing)':<30} {split_pass_orig/615*100:>9.1f}% {mono_pass_orig/615*100:>11.1f}% {(split_pass_orig-mono_pass_orig)/615*100:>+7.1f}pp")
print(f"{'Routing removed':<30} {split_pass_no_route/615*100:>9.1f}% {mono_pass_no_route/615*100:>11.1f}% {(split_pass_no_route-mono_pass_no_route)/615*100:>+7.1f}pp")

# Now check: HITL metric — does monolithic also lose here?
# In monolithic mode, does the agent still ask for confirmation?
mono_hitl_1 = sum(1 for r in mono['results'] if r.get('hitl_match', 0) >= 0.99)
split_hitl_1 = sum(1 for r in split['results'] if r.get('hitl_match', 0) >= 0.99)
print(f"\n{'='*60}")
print("HITL MATCH (does monolithic still ask for confirmation?)")
print(f"{'='*60}")
print(f"  Split  hitl=1.0: {split_hitl_1}/615 ({split_hitl_1/615*100:.1f}%)")
print(f"  Mono   hitl=1.0: {mono_hitl_1}/615 ({mono_hitl_1/615*100:.1f}%)")

# Tool recall — same tools available in both modes
mono_tool_1 = sum(1 for r in mono['results'] if r.get('tool_recall', 0) >= 0.99)
split_tool_1 = sum(1 for r in split['results'] if r.get('tool_recall', 0) >= 0.99)
print(f"\n{'='*60}")
print("TOOL RECALL (architecture-neutral metric)")
print(f"{'='*60}")
print(f"  Split  tool=1.0: {split_tool_1}/615 ({split_tool_1/615*100:.1f}%)")
print(f"  Mono   tool=1.0: {mono_tool_1}/615 ({mono_tool_1/615*100:.1f}%)")

# Only on handoff=False cases (where routing metric is neutral)
print(f"\n{'='*60}")
print(f"PASS RATE ON handoff=False CASES ONLY ({len(ho_false)} cases)")
print(f"(No routing bias here — both get routing=1.0)")
print(f"{'='*60}")
sp_pass = sum(1 for tid in ho_false if split_results[tid].get('passed'))
mo_pass = sum(1 for tid in ho_false if mono_results[tid].get('passed'))
print(f"  Split:      {sp_pass}/{len(ho_false)} = {sp_pass/len(ho_false)*100:.1f}%")
print(f"  Monolithic: {mo_pass}/{len(ho_false)} = {mo_pass/len(ho_false)*100:.1f}%")
print(f"  Delta:      {(sp_pass-mo_pass)/len(ho_false)*100:+.1f}pp")

# On handoff=True cases (where routing systematically penalizes mono)
print(f"\n{'='*60}")
print(f"PASS RATE ON handoff=True CASES ONLY ({len(ho_true)} cases)")
print(f"(Routing metric gives mono 0.0 here)")
print(f"{'='*60}")
sp_pass = sum(1 for tid in ho_true if split_results[tid].get('passed'))
mo_pass = sum(1 for tid in ho_true if mono_results[tid].get('passed'))
print(f"  Split:      {sp_pass}/{len(ho_true)} = {sp_pass/len(ho_true)*100:.1f}%")
print(f"  Monolithic: {mo_pass}/{len(ho_true)} = {mo_pass/len(ho_true)*100:.1f}%")
print(f"  Delta:      {(sp_pass-mo_pass)/len(ho_true)*100:+.1f}pp")

# Recalculate handoff=True pass rate WITHOUT routing
sp_pass_nr = sum(1 for tid in ho_true if calc_no_routing(split_results[tid]) >= 0.80)
mo_pass_nr = sum(1 for tid in ho_true if calc_no_routing(mono_results[tid]) >= 0.80)
print(f"\n  Without routing metric:")
print(f"  Split:      {sp_pass_nr}/{len(ho_true)} = {sp_pass_nr/len(ho_true)*100:.1f}%")
print(f"  Monolithic: {mo_pass_nr}/{len(ho_true)} = {mo_pass_nr/len(ho_true)*100:.1f}%")
print(f"  Delta:      {(sp_pass_nr-mo_pass_nr)/len(ho_true)*100:+.1f}pp")

print(f"\n{'='*60}")
print("CONCLUSION")
print(f"{'='*60}")
