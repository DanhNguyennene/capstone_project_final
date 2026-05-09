"""Compare base Qwen (Observer/Operator) vs base Qwen (Monolithic) failures."""
import json
from collections import Counter, defaultdict

# Load both results
split = json.load(open('evaluation/results/base_qwen14b_test615.json', encoding='utf-8'))
mono = json.load(open('evaluation/results/base_qwen14b_monolithic_test615.json', encoding='utf-8'))

split_results = {r['test_id']: r for r in split['results']}
mono_results = {r['test_id']: r for r in mono['results']}

all_ids = set(split_results.keys()) & set(mono_results.keys())
print(f"Common test IDs: {len(all_ids)}")

# Categorize outcomes
both_pass = []
both_fail = []
split_only_pass = []  # split passes, mono fails
mono_only_pass = []   # mono passes, split fails

for tid in all_ids:
    s = split_results[tid]
    m = mono_results[tid]
    sp = s.get('passed', False)
    mp = m.get('passed', False)
    if sp and mp:
        both_pass.append(tid)
    elif not sp and not mp:
        both_fail.append(tid)
    elif sp and not mp:
        split_only_pass.append(tid)
    else:
        mono_only_pass.append(tid)

print(f"\n{'='*60}")
print(f"OUTCOME MATRIX")
print(f"{'='*60}")
print(f"  Both pass:              {len(both_pass)}")
print(f"  Both fail:              {len(both_fail)}")
print(f"  Split passes, Mono fails: {len(split_only_pass)}  (architecture helps)")
print(f"  Mono passes, Split fails: {len(mono_only_pass)}  (architecture hurts)")

print(f"\n{'='*60}")
print(f"CASES WHERE ARCHITECTURE HELPS ({len(split_only_pass)} cases)")
print(f"{'='*60}")
cats = Counter(split_results[tid]['category'] for tid in split_only_pass)
for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {cat:15s} {n}")

print(f"\n{'='*60}")
print(f"CASES WHERE MONOLITHIC IS BETTER ({len(mono_only_pass)} cases)")
print(f"{'='*60}")
cats = Counter(split_results[tid]['category'] for tid in mono_only_pass)
for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {cat:15s} {n}")

# Why does mono pass where split fails?
print(f"\n  Sample mono-only passes (split failed because...):")
for tid in mono_only_pass[:10]:
    s = split_results[tid]
    cat = s['category']
    err = s.get('error', '')[:60] if s.get('error') else 'no error'
    tool_r = s.get('tool_recall', 0)
    route = s.get('routing_match', 0)
    print(f"    {tid[:40]:40s} [{cat:12s}] tool={tool_r:.0%} route={route:.0%} err={err}")

print(f"\n{'='*60}")
print(f"BOTH FAIL ({len(both_fail)} cases) - by category")
print(f"{'='*60}")
cats = Counter(split_results[tid]['category'] for tid in both_fail)
for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {cat:15s} {n}")

# Failure reasons for both-fail
print(f"\n  Failure analysis (both-fail):")
mono_errors = Counter()
for tid in both_fail:
    m = mono_results[tid]
    if m.get('error'):
        mono_errors[m['error'][:50]] += 1
print(f"  Mono errors in both-fail:")
for e, n in mono_errors.most_common(5):
    print(f"    [{n:2d}x] {e}")

# Score comparison on both-fail: which architecture gets closer?
print(f"\n  Avg overall on both-fail cases:")
avg_split = sum(split_results[tid].get('overall', 0) for tid in both_fail) / len(both_fail) if both_fail else 0
avg_mono = sum(mono_results[tid].get('overall', 0) for tid in both_fail) / len(both_fail) if both_fail else 0
print(f"    Split:     {avg_split*100:.1f}%")
print(f"    Monolithic: {avg_mono*100:.1f}%")
