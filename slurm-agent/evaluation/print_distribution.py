#!/usr/bin/env python3
"""Print and plot test distribution from dataset.json."""

import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.transforms import Bbox
import numpy as np

DATASET_PATH = Path(__file__).parent / "dataset.json"
RESULTS_DIR  = Path(__file__).parent / "results"
IMAGE_PATH   = RESULTS_DIR / "dataset_distribution.png"
SEPARATE_IMAGE_PATHS = {
    "category": RESULTS_DIR / "dataset_distribution_category.png",
    "scenario": RESULTS_DIR / "dataset_distribution_scenario.png",
    "heatmap": RESULTS_DIR / "dataset_distribution_heatmap.png",
    "tools": RESULTS_DIR / "dataset_distribution_top_tools.png",
    "flags": RESULTS_DIR / "dataset_distribution_flags.png",
}


def bar(n, total, width=30):
    filled = int(width * n / total) if total else 0
    return "█" * filled + "░" * (width - filled)


def save_axes_image(fig, renderer, axes, path, pad_inches=0.08):
    bbox = Bbox.union([ax.get_tightbbox(renderer) for ax in axes])
    bbox_inches = bbox.transformed(fig.dpi_scale_trans.inverted())
    x0, y0, x1, y1 = bbox_inches.extents
    clamped_bbox = Bbox.from_extents(
        max(0.0, x0 - pad_inches),
        max(0.0, y0 - pad_inches),
        min(fig.get_figwidth(), x1 + pad_inches),
        min(fig.get_figheight(), y1 + pad_inches),
    )
    fig.savefig(path, dpi=150, bbox_inches=clamped_bbox)


# ── Console print ─────────────────────────────────────────────────────────────

def print_distribution(data):
    total    = len(data)
    base     = [t for t in data if not t.get("variant_of")]
    variants = [t for t in data if t.get("variant_of")]

    print(f"\n{'='*60}")
    print(f"  DATASET: {DATASET_PATH.name}")
    print(f"{'='*60}")
    print(f"  Total tests : {total}")
    print(f"  Base tests  : {len(base)}")
    print(f"  Variants    : {len(variants)}")

    cat_counts = Counter(t["category"] for t in data)
    print(f"\n{'─'*60}\n  BY CATEGORY\n{'─'*60}")
    for cat, n in sorted(cat_counts.items(), key=lambda x: -x[1]):
        hitl = sum(1 for t in data if t["category"] == cat and t["ground_truth"].get("hitl"))
        print(f"  {cat:<12} {n:>4}  {bar(n, total)}  HITL:{hitl}")

    sc_counts = Counter(t["scenario"] for t in data)
    print(f"\n{'─'*60}\n  BY SCENARIO\n{'─'*60}")
    for sc, n in sorted(sc_counts.items(), key=lambda x: -x[1]):
        print(f"  {sc:<14} {n:>4}  {bar(n, total)}")

    hitl_n    = sum(1 for t in data if t["ground_truth"].get("hitl"))
    handoff_n = sum(1 for t in data if t["ground_truth"].get("handoff"))
    print(f"\n{'─'*60}\n  BY GROUND TRUTH FLAGS\n{'─'*60}")
    print(f"  hitl=True    {hitl_n:>4}  {bar(hitl_n, total)}")
    print(f"  handoff=True {handoff_n:>4}  {bar(handoff_n, total)}")

    tool_counts: Counter = Counter()
    for t in data:
        for tool in t["ground_truth"].get("tools", []):
            tool_counts[tool] += 1
    print(f"\n{'─'*60}\n  TOOLS EXERCISED\n{'─'*60}")
    for tool, n in sorted(tool_counts.items(), key=lambda x: -x[1]):
        print(f"  {tool:<35} {n:>4}  {bar(n, total, width=20)}")

    cats = sorted(cat_counts.keys())
    scs  = sorted(sc_counts.keys())
    grid = defaultdict(Counter)
    for t in data:
        grid[t["category"]][t["scenario"]] += 1
    print(f"\n{'─'*60}\n  CATEGORY × SCENARIO MATRIX\n{'─'*60}")
    print(f"  {'':12}" + "".join(f"{s[:7]:>8}" for s in scs))
    for cat in cats:
        print(f"  {cat:<12}" + "".join(f"{grid[cat].get(sc,0):>8}" for sc in scs))

    print(f"\n{'='*60}\n")
    return cat_counts, sc_counts, tool_counts, grid, hitl_n, handoff_n, total


# ── Plot ──────────────────────────────────────────────────────────────────────

def plot_distribution(data, cat_counts, sc_counts, tool_counts, grid,
                      hitl_n, handoff_n, total):

    BLUE   = "#4C72B0"
    GREEN  = "#55A868"
    ORANGE = "#DD8452"
    RED    = "#C44E52"
    PURPLE = "#8172B2"

    cats = sorted(cat_counts.keys())
    scs  = sorted(sc_counts.keys())

    fig = plt.figure(figsize=(20, 24), facecolor="#F8F9FA")
    fig.suptitle(
        f"Evaluation Dataset Distribution  —  {total} tests  "
        f"({sum(1 for t in data if not t.get('variant_of'))} base + "
        f"{sum(1 for t in data if t.get('variant_of'))} variants)",
        fontsize=16, fontweight="bold", y=0.98,
    )

    gs = gridspec.GridSpec(
        3, 2,
        figure=fig,
        hspace=0.45, wspace=0.35,
        top=0.94, bottom=0.04,
        left=0.08, right=0.97,
    )

    # ── 1. Category bar chart ─────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    sorted_cats = sorted(cat_counts.items(), key=lambda x: -x[1])
    labels1, vals1 = zip(*sorted_cats)
    hitl_vals = [
        sum(1 for t in data if t["category"] == c and t["ground_truth"].get("hitl"))
        for c in labels1
    ]
    non_hitl = [v - h for v, h in zip(vals1, hitl_vals)]
    x1 = np.arange(len(labels1))
    ax1.bar(x1, non_hitl, color=BLUE, label="non-HITL")
    ax1.bar(x1, hitl_vals, bottom=non_hitl, color=RED, label="HITL")
    ax1.set_xticks(x1)
    ax1.set_xticklabels(labels1, rotation=30, ha="right", fontsize=9)
    ax1.set_title("Tests by Category", fontweight="bold")
    ax1.set_ylabel("Count")
    ax1.legend(fontsize=8)
    for i, v in enumerate(vals1):
        ax1.text(i, v + 1, str(v), ha="center", va="bottom", fontsize=8)

    # ── 2. Scenario pie chart ─────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    sorted_scs = sorted(sc_counts.items(), key=lambda x: -x[1])
    sc_labels, sc_vals = zip(*sorted_scs)
    colors2 = [BLUE, GREEN, ORANGE, PURPLE, RED]
    wedges, texts, autotexts = ax2.pie(
        sc_vals, labels=sc_labels, autopct="%1.1f%%",
        colors=colors2[:len(sc_vals)], startangle=140,
        textprops={"fontsize": 9},
    )
    ax2.set_title("Tests by Scenario", fontweight="bold")

    # ── 3. Category × Scenario heatmap ───────────────────────────
    ax3 = fig.add_subplot(gs[1, :])
    matrix = np.array([[grid[c].get(s, 0) for s in scs] for c in cats])
    im = ax3.imshow(matrix, cmap="Blues", aspect="auto")
    ax3.set_xticks(range(len(scs)))
    ax3.set_xticklabels(scs, fontsize=10)
    ax3.set_yticks(range(len(cats)))
    ax3.set_yticklabels(cats, fontsize=10)
    ax3.set_title("Category × Scenario Heatmap", fontweight="bold")
    cbar = plt.colorbar(im, ax=ax3, shrink=0.6, label="Count")
    for i in range(len(cats)):
        for j in range(len(scs)):
            v = matrix[i, j]
            ax3.text(j, i, str(v), ha="center", va="center",
                     fontsize=9, color="white" if v > matrix.max() * 0.6 else "black")

    # ── 4. Top tools bar chart ────────────────────────────────────
    ax4 = fig.add_subplot(gs[2, 0])
    top_tools = tool_counts.most_common(15)
    t_labels, t_vals = zip(*top_tools)
    # colour: red if tool not in MCP, blue if implemented
    MCP_TOOLS = {
        "squeue","sinfo","sacct","scontrol_show","sbatch","scancel",
        "scontrol_hold","scontrol_release","scontrol_update","scontrol_requeue",
        "scontrol_reconfigure","scontrol_node","scontrol_create_reservation",
        "scontrol_delete_reservation","scontrol_reservation_show","scontrol_license",
        "sacctmgr_list","sacctmgr_add","sacctmgr_modify","sacctmgr_delete",
        "sreport","sdiag","sprio","sstat","read_file","web_search","fetch_web_content",
        "cluster_history","reset_mock_state",
    }
    colors4 = [GREEN if t in MCP_TOOLS else RED for t in t_labels]
    y4 = np.arange(len(t_labels))
    ax4.barh(y4, t_vals, color=colors4)
    ax4.set_yticks(y4)
    ax4.set_yticklabels(t_labels, fontsize=8)
    ax4.invert_yaxis()
    ax4.set_title("Top 15 Tools in Ground Truth\n(green=implemented, red=missing)", fontweight="bold")
    ax4.set_xlabel("Test count")
    for i, v in enumerate(t_vals):
        ax4.text(v + 0.5, i, str(v), va="center", fontsize=8)

    # ── 5. HITL / handoff / flags ─────────────────────────────────
    ax5 = fig.add_subplot(gs[2, 1])
    flag_labels = ["hitl=True", "hitl=False", "handoff=True", "handoff=False"]
    flag_vals   = [hitl_n, total - hitl_n, handoff_n, total - handoff_n]
    flag_colors = [RED, BLUE, ORANGE, BLUE]
    y5 = np.arange(len(flag_labels))
    ax5.barh(y5, flag_vals, color=flag_colors)
    ax5.set_yticks(y5)
    ax5.set_yticklabels(flag_labels, fontsize=9)
    ax5.invert_yaxis()
    ax5.set_title("HITL & Handoff Flags", fontweight="bold")
    ax5.set_xlabel("Test count")
    for i, v in enumerate(flag_vals):
        ax5.text(v + 1, i, str(v), va="center", fontsize=9)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(IMAGE_PATH, dpi=150, bbox_inches="tight")
    print(f"  Saved → {IMAGE_PATH}")

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    panel_exports = [
        ("category", [ax1]),
        ("scenario", [ax2]),
        ("heatmap", [ax3, cbar.ax]),
        ("tools", [ax4]),
        ("flags", [ax5]),
    ]
    for key, axes in panel_exports:
        panel_path = SEPARATE_IMAGE_PATHS[key]
        save_axes_image(fig, renderer, axes, panel_path)
        print(f"  Saved → {panel_path}")

    plt.close(fig)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    data = json.loads(DATASET_PATH.read_text())
    cat_counts, sc_counts, tool_counts, grid, hitl_n, handoff_n, total = \
        print_distribution(data)
    plot_distribution(data, cat_counts, sc_counts, tool_counts, grid,
                      hitl_n, handoff_n, total)


if __name__ == "__main__":
    main()
