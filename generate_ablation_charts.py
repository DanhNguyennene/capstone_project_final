"""Generate ablation comparison charts for the report."""
import json
import matplotlib.pyplot as plt
import numpy as np

# Load data
mono = json.load(open('slurm-agent/evaluation/results/base_qwen14b_monolithic_test615.json'))
split = json.load(open('slurm-agent/evaluation/results/base_qwen14b_test615.json'))
d = json.load(open('slurm-agent/evaluation/dataset.json'))

test_ids = set(r['test_id'] for r in mono['results'])
tests = {t['id']: t for t in d if t['id'] in test_ids}
mono_r = {r['test_id']: r for r in mono['results']}
split_r = {r['test_id']: r for r in split['results']}

# ============================================================
# CHART 1: Per-category pass rate (all 615 cases, 11 categories)
# ============================================================
cats = ['read', 'account', 'diagnose', 'docs', 'domain', 'edge',
        'multi_step', 'action', 'bulk', 'safety', 'submission']

split_rates = []
mono_rates = []
for cat in cats:
    ids = [tid for tid in test_ids if tests[tid]['category'] == cat]
    sp = sum(1 for tid in ids if split_r[tid].get('passed')) / len(ids) * 100
    mp = sum(1 for tid in ids if mono_r[tid].get('passed')) / len(ids) * 100
    split_rates.append(sp)
    mono_rates.append(mp)

x = np.arange(len(cats))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 5.5))
bars1 = ax.bar(x - width/2, split_rates, width, label='Observer/Operator (2-Agent)', color='#2196F3', edgecolor='white', linewidth=0.5)
bars2 = ax.bar(x + width/2, mono_rates, width, label='Monolithic (Single Agent)', color='#FF9800', edgecolor='white', linewidth=0.5)

ax.set_ylabel('Pass Rate (%)', fontsize=11)
ax.set_title('Architecture Ablation: Per-Category Pass Rate (615 Test Cases)', fontsize=12, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([c.replace('_', '\n') for c in cats], fontsize=9)
ax.set_ylim(0, 105)
ax.legend(loc='upper right', fontsize=10)
ax.axhline(y=80, color='gray', linestyle='--', alpha=0.5, label='Pass threshold')
ax.grid(axis='y', alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add value labels on bars
for bar in bars1:
    h = bar.get_height()
    if h > 5:
        ax.text(bar.get_x() + bar.get_width()/2., h + 1, f'{h:.0f}', ha='center', va='bottom', fontsize=8, color='#1565C0')
for bar in bars2:
    h = bar.get_height()
    if h > 5:
        ax.text(bar.get_x() + bar.get_width()/2., h + 1, f'{h:.0f}', ha='center', va='bottom', fontsize=8, color='#E65100')

plt.tight_layout()
plt.savefig('report/images/evaluation/ablation_per_category.png', dpi=200, bbox_inches='tight')
plt.close()
print("Saved: report/images/evaluation/ablation_per_category.png")

# ============================================================
# CHART 2: Observer-only (routing-neutral) comparison
# ============================================================
ho_false = [tid for tid in test_ids if not tests[tid].get('ground_truth', {}).get('handoff')]

# Only categories with enough cases
obs_cats = []
obs_split = []
obs_mono = []
for cat in cats:
    ids = [tid for tid in ho_false if tests[tid]['category'] == cat]
    if len(ids) >= 4:  # need meaningful sample
        obs_cats.append(cat)
        sp = sum(1 for tid in ids if split_r[tid].get('passed')) / len(ids) * 100
        mp = sum(1 for tid in ids if mono_r[tid].get('passed')) / len(ids) * 100
        obs_split.append(sp)
        obs_mono.append(mp)

x2 = np.arange(len(obs_cats))

fig2, ax2 = plt.subplots(figsize=(11, 5))
bars3 = ax2.bar(x2 - width/2, obs_split, width, label='Observer/Operator (2-Agent)', color='#2196F3', edgecolor='white', linewidth=0.5)
bars4 = ax2.bar(x2 + width/2, obs_mono, width, label='Monolithic (Single Agent)', color='#FF9800', edgecolor='white', linewidth=0.5)

ax2.set_ylabel('Pass Rate (%)', fontsize=11)
ax2.set_title('Routing-Neutral Comparison: Observer-Only Tasks (378 Cases, routing=1.0 for both)', fontsize=11, fontweight='bold')
ax2.set_xticks(x2)
ax2.set_xticklabels([c.replace('_', '\n') for c in obs_cats], fontsize=9)
ax2.set_ylim(0, 110)
ax2.legend(loc='upper right', fontsize=10)
ax2.axhline(y=80, color='gray', linestyle='--', alpha=0.5)
ax2.grid(axis='y', alpha=0.3)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Add value labels
for bar in bars3:
    h = bar.get_height()
    if h > 5:
        ax2.text(bar.get_x() + bar.get_width()/2., h + 1, f'{h:.0f}', ha='center', va='bottom', fontsize=8, color='#1565C0')
for bar in bars4:
    h = bar.get_height()
    if h > 5:
        ax2.text(bar.get_x() + bar.get_width()/2., h + 1, f'{h:.0f}', ha='center', va='bottom', fontsize=8, color='#E65100')

# Add annotation for overall
overall_sp = sum(1 for tid in ho_false if split_r[tid].get('passed')) / len(ho_false) * 100
overall_mp = sum(1 for tid in ho_false if mono_r[tid].get('passed')) / len(ho_false) * 100
ax2.annotate(f'Overall: {overall_sp:.1f}% vs {overall_mp:.1f}% (+{overall_sp-overall_mp:.1f}pp)',
             xy=(0.02, 0.95), xycoords='axes fraction', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

plt.tight_layout()
plt.savefig('report/images/evaluation/ablation_observer_only.png', dpi=200, bbox_inches='tight')
plt.close()
print("Saved: report/images/evaluation/ablation_observer_only.png")
