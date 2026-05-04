#!/usr/bin/env python3
"""Generate evaluation charts for the report."""

import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

EVAL_FILE = Path(__file__).parent / "results" / "eval_all_20260504_001747.json"
DATASET_FILE = Path(__file__).parent / "dataset.json"
OUT_DIR = Path(__file__).parent.parent / "report" / "images" / "evaluation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load data
with open(EVAL_FILE) as f:
    eval_data = json.load(f)
with open(DATASET_FILE) as f:
    dataset = json.load(f)

results = eval_data["results"]
metrics = eval_data["metrics"]

# ─── 1. Scenario Pie Chart ─────────────────────────────────────────────────────
scenario_counts = Counter(d["scenario"] for d in dataset)
fig, ax = plt.subplots(figsize=(8, 6))
labels = list(scenario_counts.keys())
sizes = list(scenario_counts.values())
colors = ["#4C72B0", "#55A868", "#DD8452", "#C44E52", "#8172B2"]
explode = [0.02] * len(labels)
wedges, texts, autotexts = ax.pie(
    sizes, labels=labels, autopct="%1.1f%%", colors=colors,
    explode=explode, startangle=90, textprops={"fontsize": 12}
)
for t in autotexts:
    t.set_fontsize(11)
    t.set_fontweight("bold")
ax.set_title("Dataset Distribution by Scenario", fontsize=14, fontweight="bold")
fig.tight_layout()
fig.savefig(OUT_DIR / "scenario_pie.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  Saved → {OUT_DIR / 'scenario_pie.png'}")

# ─── 2. Category bar chart (bigger) ────────────────────────────────────────────
cat_counts = Counter(d["category"] for d in dataset)
cats_sorted = sorted(cat_counts.keys())
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(cats_sorted, [cat_counts[c] for c in cats_sorted], color="#4C72B0", edgecolor="white")
ax.set_xlabel("Number of Test Cases", fontsize=12)
ax.set_title("Dataset Distribution by Category (3,135 total)", fontsize=14, fontweight="bold")
for bar in bars:
    ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height()/2,
            f"{int(bar.get_width())}", va="center", fontsize=11)
ax.set_xlim(0, 320)
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig(OUT_DIR / "category_bar_large.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  Saved → {OUT_DIR / 'category_bar_large.png'}")

# ─── 3. Overall metrics radar chart ────────────────────────────────────────────
metric_names = ["Tool Recall", "Routing", "HITL", "Keywords", "State"]
metric_values = [
    metrics["avg_tool_recall"],
    metrics["avg_routing_match"],
    metrics["avg_hitl_match"],
    metrics["avg_keyword_score"],
    metrics["avg_state_match"],
]
angles = np.linspace(0, 2 * np.pi, len(metric_names), endpoint=False).tolist()
angles += angles[:1]
values = metric_values + metric_values[:1]

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
ax.plot(angles, values, "o-", linewidth=2, color="#4C72B0")
ax.fill(angles, values, alpha=0.25, color="#4C72B0")
ax.set_xticks(angles[:-1])
ax.set_xticklabels(metric_names, fontsize=12)
ax.set_ylim(0.8, 1.0)
ax.set_yticks([0.85, 0.90, 0.95, 1.0])
ax.set_yticklabels(["0.85", "0.90", "0.95", "1.00"], fontsize=9)
ax.set_title("Average Scores by Dimension", fontsize=14, fontweight="bold", pad=20)
for angle, val, name in zip(angles[:-1], metric_values, metric_names):
    ax.annotate(f"{val:.3f}", xy=(angle, val), fontsize=10, ha="center",
                xytext=(0, 10), textcoords="offset points")
fig.tight_layout()
fig.savefig(OUT_DIR / "metrics_radar.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  Saved → {OUT_DIR / 'metrics_radar.png'}")

# ─── 4. Pass rate by category ──────────────────────────────────────────────────
cat_pass = defaultdict(list)
cat_overall = defaultdict(list)
for r in results:
    cat_pass[r["category"]].append(r["passed"])
    cat_overall[r["category"]].append(r["overall"])

cats_sorted = sorted(cat_pass.keys())
pass_rates = [sum(cat_pass[c]) / len(cat_pass[c]) * 100 for c in cats_sorted]
avg_scores = [np.mean(cat_overall[c]) for c in cats_sorted]

fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(cats_sorted))
width = 0.4
bars1 = ax.bar(x - width/2, pass_rates, width, label="Pass Rate (%)", color="#55A868", edgecolor="white")
bars2 = ax.bar(x + width/2, [s*100 for s in avg_scores], width, label="Avg Score (%)", color="#4C72B0", edgecolor="white")
ax.set_xticks(x)
ax.set_xticklabels(cats_sorted, rotation=30, ha="right", fontsize=11)
ax.set_ylabel("Percentage", fontsize=12)
ax.set_title("Pass Rate and Average Score by Category", fontsize=14, fontweight="bold")
ax.set_ylim(0, 105)
ax.axhline(y=80, color="red", linestyle="--", alpha=0.5, label="Pass Threshold (80%)")
ax.legend(fontsize=11)
ax.grid(axis="y", alpha=0.3)
for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f"{bar.get_height():.1f}", ha="center", fontsize=9)
fig.tight_layout()
fig.savefig(OUT_DIR / "pass_rate_by_category.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  Saved → {OUT_DIR / 'pass_rate_by_category.png'}")

# ─── 5. Score distribution histogram ───────────────────────────────────────────
all_scores = [r["overall"] for r in results]
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(all_scores, bins=30, color="#4C72B0", edgecolor="white", alpha=0.8)
ax.axvline(x=0.8, color="red", linestyle="--", linewidth=2, label="Pass threshold (0.80)")
ax.set_xlabel("Overall Score", fontsize=12)
ax.set_ylabel("Number of Cases", fontsize=12)
ax.set_title("Distribution of Overall Scores (n=3,135)", fontsize=14, fontweight="bold")
ax.legend(fontsize=12)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(OUT_DIR / "score_distribution.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  Saved → {OUT_DIR / 'score_distribution.png'}")

# ─── 6. Dimension scores by category heatmap ───────────────────────────────────
dims = ["tool_recall", "routing_match", "hitl_match", "keyword_score", "state_match"]
dim_labels = ["Tool Recall", "Routing", "HITL", "Keywords", "State"]
cat_dim_scores = defaultdict(lambda: defaultdict(list))
for r in results:
    for d in dims:
        cat_dim_scores[r["category"]][d].append(r.get(d, 0))

heatmap_data = []
for cat in cats_sorted:
    row = [np.mean(cat_dim_scores[cat][d]) for d in dims]
    heatmap_data.append(row)
heatmap_data = np.array(heatmap_data)

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(heatmap_data, cmap="RdYlGn", aspect="auto", vmin=0.7, vmax=1.0)
ax.set_xticks(range(len(dim_labels)))
ax.set_xticklabels(dim_labels, fontsize=11)
ax.set_yticks(range(len(cats_sorted)))
ax.set_yticklabels(cats_sorted, fontsize=11)
for i in range(len(cats_sorted)):
    for j in range(len(dims)):
        ax.text(j, i, f"{heatmap_data[i, j]:.3f}", ha="center", va="center", fontsize=10,
                color="white" if heatmap_data[i, j] < 0.85 else "black")
cbar = fig.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label("Average Score", fontsize=11)
ax.set_title("Scoring Dimensions by Category", fontsize=14, fontweight="bold")
fig.tight_layout()
fig.savefig(OUT_DIR / "dimension_heatmap.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  Saved → {OUT_DIR / 'dimension_heatmap.png'}")

# ─── 7. SVR and safety analysis ────────────────────────────────────────────────
safety_results = [r for r in results if r["category"] == "safety"]
safety_hitl_correct = sum(1 for r in safety_results if r["hitl_match"] == 1.0)
safety_hitl_wrong = len(safety_results) - safety_hitl_correct

fig, ax = plt.subplots(figsize=(7, 5))
ax.bar(["HITL Correct", "HITL Missed"], [safety_hitl_correct, safety_hitl_wrong],
       color=["#55A868", "#C44E52"], edgecolor="white", width=0.5)
ax.set_ylabel("Number of Cases", fontsize=12)
ax.set_title(f"Safety Category: HITL Compliance (n={len(safety_results)})", fontsize=14, fontweight="bold")
for i, v in enumerate([safety_hitl_correct, safety_hitl_wrong]):
    ax.text(i, v + 2, str(v), ha="center", fontsize=12, fontweight="bold")
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(OUT_DIR / "safety_hitl_compliance.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  Saved → {OUT_DIR / 'safety_hitl_compliance.png'}")

# ─── 8. Latency distribution by category ───────────────────────────────────────
cat_latency = defaultdict(list)
for r in results:
    if r.get("latency_s") and r["latency_s"] > 0:
        cat_latency[r["category"]].append(r["latency_s"])

fig, ax = plt.subplots(figsize=(12, 6))
box_data = [cat_latency[c] for c in cats_sorted]
bp = ax.boxplot(box_data, labels=cats_sorted, patch_artist=True, showfliers=False)
for patch in bp["boxes"]:
    patch.set_facecolor("#4C72B0")
    patch.set_alpha(0.6)
ax.set_xticklabels(cats_sorted, rotation=30, ha="right", fontsize=11)
ax.set_ylabel("Latency (seconds)", fontsize=12)
ax.set_title("Response Latency by Category", fontsize=14, fontweight="bold")
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(OUT_DIR / "latency_by_category.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  Saved → {OUT_DIR / 'latency_by_category.png'}")

# ─── Summary ────────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"  All charts saved to: {OUT_DIR}")
print(f"  Overall: pass_rate={metrics['pass_rate']:.1%}, BAR={metrics['BAR']:.3f}, SVR={metrics['SVR']:.3f}")
print(f"{'='*60}")
