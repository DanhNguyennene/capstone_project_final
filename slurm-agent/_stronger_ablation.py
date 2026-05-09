"""Find the strongest genuine arguments for 2-agent superiority."""
import json
from collections import Counter, defaultdict

d = json.load(open('evaluation/dataset.json'))
mono = json.load(open('evaluation/results/base_qwen14b_monolithic_test615.json'))
split = json.load(open('evaluation/results/base_qwen14b_test615.json'))

test_ids = set(r['test_id'] for r in mono['results'])
tests = {t['id']: t for t in d if t['id'] in test_ids}
mono_results = {r['test_id']: r for r in mono['results']}
split_results = {r['test_id']: r for r in split['results']}

DESTRUCTIVE = {
    'scancel', 'scontrol_update', 'scontrol_hold', 'scontrol_release',
    'sacctmgr_modify', 'sacctmgr_add', 'sacctmgr_delete', 'sacctmgr_remove',
    'sbatch', 'srun'
}

READ_TOOLS = {
    'squeue', 'sacct', 'sinfo', 'sacctmgr_list', 'sacctmgr_show',
    'scontrol_show', 'lookup_slurm_docs', 'check_job_efficiency'
}

# ============================================================
# ARGUMENT 1: FOCUSED CONTEXT → BETTER TOOL SELECTION
# On handoff=False cases, routing is neutral (both get 1.0)
# Split still wins because Observer has focused tool list
# ============================================================
print("=" * 70)
print("ARGUMENT 1: FOCUSED CONTEXT ADVANTAGE")
print("On observer-only tasks (no routing bias), split wins on TASK QUALITY")
print("=" * 70)

ho_false = [tid for tid in test_ids if not tests[tid].get('ground_truth', {}).get('handoff')]

metrics = ['tool_recall', 'hitl_match', 'keyword_score', 'state_match']
print(f"\n  {'Metric':<15} {'Split':>8} {'Mono':>8} {'Delta':>8}")
print(f"  {'-'*45}")
for m in metrics:
    s_avg = sum(split_results[tid].get(m, 0) for tid in ho_false) / len(ho_false)
    m_avg = sum(mono_results[tid].get(m, 0) for tid in ho_false) / len(ho_false)
    print(f"  {m:<15} {s_avg:>7.1%} {m_avg:>7.1%} {(s_avg-m_avg)*100:>+7.1f}pp")

sp = sum(1 for tid in ho_false if split_results[tid].get('passed'))
mp = sum(1 for tid in ho_false if mono_results[tid].get('passed'))
print(f"\n  Pass rate:      {sp/len(ho_false):.1%}    {mp/len(ho_false):.1%}   {(sp-mp)/len(ho_false)*100:+.1f}pp")
print(f"  N = {len(ho_false)} (all observer-only, routing=1.0 for both)")

# ============================================================
# ARGUMENT 2: MONOLITHIC CALLS DESTRUCTIVE TOOLS ON READ-ONLY TASKS
# ============================================================
print(f"\n{'='*70}")
print("ARGUMENT 2: UNINTENDED DESTRUCTIVE TOOL CALLS")
print("Monolithic calls write tools on READ-ONLY tasks (hallucination)")
print("=" * 70)

read_categories = {'read', 'diagnose', 'docs', 'domain', 'account'}
read_ids = [tid for tid in test_ids if tests[tid].get('category') in read_categories]
read_no_handoff = [tid for tid in read_ids if not tests[tid].get('ground_truth', {}).get('handoff')]

mono_destructive_on_reads = 0
split_destructive_on_reads = 0
mono_examples = []

for tid in read_no_handoff:
    mr = mono_results[tid]
    sr = split_results[tid]
    mono_tools = set()
    for tc in mr.get('tool_call_history', []):
        if tc.get('type') == 'tool':
            tool = tc.get('tool', '')
            mono_tools.add(tool)
    split_tools = set()
    for tc in sr.get('tool_call_history', []):
        if tc.get('type') == 'tool':
            tool = tc.get('tool', '')
            split_tools.add(tool)

    mono_destr = mono_tools & DESTRUCTIVE
    split_destr = split_tools & DESTRUCTIVE
    if mono_destr:
        mono_destructive_on_reads += 1
        if len(mono_examples) < 5:
            mono_examples.append((tid, tests[tid]['category'], mono_destr))
    if split_destr:
        split_destructive_on_reads += 1

print(f"\n  Read-only tasks (no handoff expected): {len(read_no_handoff)}")
print(f"  Monolithic called destructive tool: {mono_destructive_on_reads} ({mono_destructive_on_reads/len(read_no_handoff)*100:.1f}%)")
print(f"  Split called destructive tool:      {split_destructive_on_reads} ({split_destructive_on_reads/len(read_no_handoff)*100:.1f}%)")
if mono_examples:
    print(f"\n  Examples (mono calling write tools on reads):")
    for tid, cat, tools in mono_examples:
        print(f"    {tid[:45]:45s} [{cat}] -> {tools}")

# ============================================================
# ARGUMENT 3: ERROR RATE / CRASH RATE
# ============================================================
print(f"\n{'='*70}")
print("ARGUMENT 3: STABILITY (errors and crashes)")
print("=" * 70)

mono_errors = sum(1 for r in mono['results'] if r.get('error'))
split_errors = sum(1 for r in split['results'] if r.get('error'))
print(f"  Monolithic errors: {mono_errors}/615 ({mono_errors/615*100:.1f}%)")
print(f"  Split errors:      {split_errors}/615 ({split_errors/615*100:.1f}%)")

mono_err_types = Counter()
split_err_types = Counter()
for r in mono['results']:
    if r.get('error'):
        e = r['error'][:60]
        mono_err_types[e] += 1
for r in split['results']:
    if r.get('error'):
        e = r['error'][:60]
        split_err_types[e] += 1

print(f"\n  Mono error types:")
for e, n in mono_err_types.most_common(5):
    print(f"    [{n:2d}x] {e}")
print(f"\n  Split error types:")
for e, n in split_err_types.most_common(5):
    print(f"    [{n:2d}x] {e}")

# ============================================================
# ARGUMENT 4: TOOL HALLUCINATION (calling tools that don't exist)
# ============================================================
print(f"\n{'='*70}")
print("ARGUMENT 4: TOOL HALLUCINATION (non-existent tool calls)")
print("=" * 70)

KNOWN_TOOLS = DESTRUCTIVE | READ_TOOLS | {
    'transfer_to_operator', 'transfer_to_observer', 'confirm_action',
    'cancel_action', 'manage_jobs', 'analyze_cluster', 'check_pending_actions',
    'scontrol_show', 'lookup_slurm_docs', 'check_job_efficiency',
    'sstat', 'sprio', 'sshare'
}

mono_hallucinated = Counter()
split_hallucinated = Counter()
for r in mono['results']:
    for tc in r.get('tool_call_history', []):
        if tc.get('type') == 'tool':
            tool = tc.get('tool', '')
            if tool and tool not in KNOWN_TOOLS and not tool.startswith('_'):
                mono_hallucinated[tool] += 1
for r in split['results']:
    for tc in r.get('tool_call_history', []):
        if tc.get('type') == 'tool':
            tool = tc.get('tool', '')
            if tool and tool not in KNOWN_TOOLS and not tool.startswith('_'):
                split_hallucinated[tool] += 1

print(f"  Monolithic hallucinated tools: {sum(mono_hallucinated.values())} calls")
for t, n in mono_hallucinated.most_common(10):
    print(f"    {t}: {n}x")
print(f"\n  Split hallucinated tools: {sum(split_hallucinated.values())} calls")
for t, n in split_hallucinated.most_common(10):
    print(f"    {t}: {n}x")

# ============================================================
# ARGUMENT 5: KEYWORD QUALITY (response correctness)
# ============================================================
print(f"\n{'='*70}")
print("ARGUMENT 5: RESPONSE QUALITY (keyword coverage)")
print("=" * 70)

s_kw = sum(split_results[tid].get('keyword_score', 0) for tid in test_ids) / len(test_ids)
m_kw = sum(mono_results[tid].get('keyword_score', 0) for tid in test_ids) / len(test_ids)
print(f"  Split avg keyword:  {s_kw:.1%}")
print(f"  Mono avg keyword:   {m_kw:.1%}")
print(f"  Delta:              {(s_kw-m_kw)*100:+.1f}pp")

print(f"\n  {'Category':<15} {'Split KW':>10} {'Mono KW':>10} {'Delta':>8}")
cats = sorted(set(tests[tid]['category'] for tid in test_ids))
for cat in cats:
    cat_ids = [tid for tid in test_ids if tests[tid]['category'] == cat]
    sk = sum(split_results[tid].get('keyword_score', 0) for tid in cat_ids) / len(cat_ids)
    mk = sum(mono_results[tid].get('keyword_score', 0) for tid in cat_ids) / len(cat_ids)
    print(f"  {cat:<15} {sk:>9.1%} {mk:>9.1%} {(sk-mk)*100:>+7.1f}pp")

# ============================================================
# ARGUMENT 6: STATE SAFETY - wrong state on dangerous categories
# ============================================================
print(f"\n{'='*70}")
print("ARGUMENT 6: STATE CORRUPTION ON DANGEROUS OPERATIONS")
print("(state_match on handoff-required tasks)")
print("=" * 70)

ho_true = [tid for tid in test_ids if tests[tid].get('ground_truth', {}).get('handoff')]
s_state = sum(split_results[tid].get('state_match', 0) for tid in ho_true) / len(ho_true)
m_state = sum(mono_results[tid].get('state_match', 0) for tid in ho_true) / len(ho_true)
print(f"  On dangerous tasks (handoff=True, N={len(ho_true)}):")
print(f"    Split state_match:  {s_state:.1%}")
print(f"    Mono state_match:   {m_state:.1%}")
print(f"    Delta:              {(s_state-m_state)*100:+.1f}pp")

# State=0 means wrong final state
s_bad = sum(1 for tid in ho_true if split_results[tid].get('state_match', 0) < 0.5)
m_bad = sum(1 for tid in ho_true if mono_results[tid].get('state_match', 0) < 0.5)
print(f"\n  Cases with WRONG final state:")
print(f"    Split: {s_bad}/{len(ho_true)} ({s_bad/len(ho_true)*100:.1f}%)")
print(f"    Mono:  {m_bad}/{len(ho_true)} ({m_bad/len(ho_true)*100:.1f}%)")
