"""
Regenerate evaluation report figures from the rescored results.
Produces: metrics_radar.png, pass_rate_by_category.png, dimension_heatmap.png, latency_by_category.png
"""
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict

# Load rescored results
results_path = Path(__file__).parent / "results" / "eval_all_20260504_rescored.json"
raw = json.loads(results_path.read_text(encoding="utf-8"))
cases = raw.get("results", raw) if isinstance(raw, dict) else raw

output_dir = Path(__file__).parent.parent / "report" / "images" / "evaluation"
output_dir.mkdir(parents=True, exist_ok=True)

# Aggregate metrics
n = len(cases)
metrics = {
    "pass_rate": sum(1 for r in cases if r["passed"]) / n,
    "avg_tool_recall": sum(r["tool_recall"] for r in cases) / n,
    "avg_routing_match": sum(r["routing_match"] for r in cases) / n,
    "avg_hitl_match": sum(r["hitl_match"] for r in cases) / n,
    "avg_keyword_score": sum(r["keyword_score"] for r in cases) / n,
    "avg_state_match": sum(r["state_match"] for r in cases) / n,
    "avg_overall": sum(r["overall"] for r in cases) / n,
    "avg_judge_score": sum(r.get("judge_score", 0) for r in cases) / n,
    "avg_latency": sum(r.get("latency_s", 0) for r in cases) / n,
}

print("=== Aggregate Metrics (Rescored) ===")
for k, v in metrics.items():
    if "latency" in k:
        print(f"  {k}: {v:.1f}s")
    else:
        print(f"  {k}: {v*100:.1f}%")

# Per-category stats
by_cat = defaultdict(list)
for r in cases:
    by_cat[r["category"]].append(r)

categories = sorted(by_cat.keys())
cat_pass_rates = {c: sum(1 for r in by_cat[c] if r["passed"])/len(by_cat[c]) for c in categories}
cat_avg_scores = {c: sum(r["overall"] for r in by_cat[c])/len(by_cat[c]) for c in categories}

print("\n=== Per-Category Pass Rates ===")
for c in categories:
    print(f"  {c}: {cat_pass_rates[c]*100:.1f}%")

# --- Figure 1: Radar Chart ---
dims = ["tool_recall", "routing_match", "hitl_match", "keyword_score", "state_match"]
dim_labels = ["Tool Recall", "Routing", "HITL", "Keywords", "State Match"]
values = [sum(r[d] for r in cases)/n for d in dims]
values.append(values[0])  # close the polygon

angles = np.linspace(0, 2*np.pi, len(dims), endpoint=False).tolist()
angles.append(angles[0])

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.fill(angles, values, alpha=0.25, color='steelblue')
ax.plot(angles, values, color='steelblue', linewidth=2)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(dim_labels, size=11)
ax.set_ylim(0, 1.05)
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], size=8)
ax.set_title("Aggregate Scoring Dimensions", pad=20, size=13)
plt.tight_layout()
plt.savefig(output_dir / "metrics_radar.png", dpi=150, bbox_inches='tight')
plt.close()
print("\nSaved: metrics_radar.png")

# --- Figure 2: Pass Rate by Category ---
fig, ax = plt.subplots(figsize=(12, 5))
x = np.arange(len(categories))
width = 0.35
bars1 = ax.bar(x - width/2, [cat_pass_rates[c]*100 for c in categories], width, label='Pass Rate %', color='steelblue')
bars2 = ax.bar(x + width/2, [cat_avg_scores[c]*100 for c in categories], width, label='Avg Score %', color='coral')
ax.set_xlabel('Category')
ax.set_ylabel('Percentage')
ax.set_title('Pass Rate and Average Score by Category')
ax.set_xticks(x)
ax.set_xticklabels(categories, rotation=45, ha='right')
ax.set_ylim(0, 105)
ax.legend()
ax.axhline(y=70, color='gray', linestyle='--', alpha=0.5, label='Pass threshold')
for bar in bars1:
    h = bar.get_height()
    ax.annotate(f'{h:.0f}', xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 3),
                textcoords="offset points", ha='center', va='bottom', fontsize=8)
plt.tight_layout()
plt.savefig(output_dir / "pass_rate_by_category.png", dpi=150, bbox_inches='tight')
plt.close()
print("Saved: pass_rate_by_category.png")

# --- Figure 3: Dimension Heatmap ---
dim_by_cat = {}
for c in categories:
    dim_by_cat[c] = {d: sum(r[d] for r in by_cat[c])/len(by_cat[c]) for d in dims}

heatmap_data = np.array([[dim_by_cat[c][d] for d in dims] for c in categories])
fig, ax = plt.subplots(figsize=(8, 7))
im = ax.imshow(heatmap_data, cmap='RdYlGn', vmin=0.5, vmax=1.0, aspect='auto')
ax.set_xticks(range(len(dims)))
ax.set_xticklabels(dim_labels, rotation=45, ha='right')
ax.set_yticks(range(len(categories)))
ax.set_yticklabels(categories)
for i in range(len(categories)):
    for j in range(len(dims)):
        val = heatmap_data[i, j]
        ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=8,
                color='white' if val < 0.7 else 'black')
ax.set_title('Scoring Dimensions by Category')
plt.colorbar(im, ax=ax, shrink=0.8)
plt.tight_layout()
plt.savefig(output_dir / "dimension_heatmap.png", dpi=150, bbox_inches='tight')
plt.close()
print("Saved: dimension_heatmap.png")

# --- Figure 4: Latency by Category ---
cat_latencies = {c: [r.get("latency_s", 0) for r in by_cat[c]] for c in categories}
fig, ax = plt.subplots(figsize=(10, 5))
bp = ax.boxplot([cat_latencies[c] for c in categories], labels=categories, patch_artist=True)
for patch in bp['boxes']:
    patch.set_facecolor('lightsteelblue')
ax.set_xlabel('Category')
ax.set_ylabel('Latency (seconds)')
ax.set_title('Response Latency by Category')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(output_dir / "latency_by_category.png", dpi=150, bbox_inches='tight')
plt.close()
print("Saved: latency_by_category.png")

print("\nAll figures regenerated from rescored results.")
