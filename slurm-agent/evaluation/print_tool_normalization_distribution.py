#!/usr/bin/env python3
"""Print and plot ground-truth tool normalization from dataset.json."""

import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import numpy as np

from scenario_eval import (
    _GT_ALIASES,
    _accepted_tool_aliases,
    _canonical_tool_name,
)


DATASET_PATH = Path(__file__).parent / "dataset.json"
RESULTS_DIR = Path(__file__).parent / "results"
IMAGE_PATH = RESULTS_DIR / "tool_normalization_distribution.png"
SEPARATE_IMAGE_PATHS = {
    "summary": RESULTS_DIR / "tool_normalization_summary.png",
    "canonical": RESULTS_DIR / "tool_normalization_canonical_tools.png",
    "aliases": RESULTS_DIR / "tool_normalization_alias_remaps.png",
    "category_heatmap": RESULTS_DIR / "tool_normalization_category_heatmap.png",
}


def bar(n, total, width=30):
    filled = int(width * n / total) if total else 0
    return "#" * filled + "." * (width - filled)


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


def accepted_display(canonical_tool):
    return " / ".join(_accepted_tool_aliases(canonical_tool))


def collect_distribution(data):
    raw_counts = Counter()
    canonical_counts = Counter()
    remap_counts = Counter()
    raw_by_canonical = defaultdict(Counter)
    category_canonical = defaultdict(Counter)
    scenario_canonical = defaultdict(Counter)
    tests_with_tools = 0
    tests_with_normalization = 0

    for test in data:
        tools = test.get("ground_truth", {}).get("tools", []) or []
        if tools:
            tests_with_tools += 1
        changed = False
        for raw_tool in tools:
            raw = str(raw_tool or "").strip()
            if not raw:
                continue
            canonical = _canonical_tool_name(raw)
            raw_counts[raw] += 1
            canonical_counts[canonical] += 1
            raw_by_canonical[canonical][raw] += 1
            category_canonical[str(test.get("category", "unknown"))][canonical] += 1
            scenario_canonical[str(test.get("scenario", "unknown"))][canonical] += 1
            if raw != canonical:
                remap_counts[(raw, canonical)] += 1
                changed = True
        if changed:
            tests_with_normalization += 1

    return {
        "raw_counts": raw_counts,
        "canonical_counts": canonical_counts,
        "remap_counts": remap_counts,
        "raw_by_canonical": raw_by_canonical,
        "category_canonical": category_canonical,
        "scenario_canonical": scenario_canonical,
        "tests_with_tools": tests_with_tools,
        "tests_with_normalization": tests_with_normalization,
        "total_tool_entries": sum(raw_counts.values()),
    }


def print_distribution(data, dist):
    total_tests = len(data)
    total_entries = dist["total_tool_entries"]
    normalized_entries = sum(dist["remap_counts"].values())
    direct_entries = total_entries - normalized_entries

    print(f"\n{'=' * 72}")
    print(f"  TOOL NORMALIZATION: {DATASET_PATH.name}")
    print(f"{'=' * 72}")
    print(f"  Total tests                  : {total_tests}")
    print(f"  Tests with expected tools    : {dist['tests_with_tools']}")
    print(f"  Tests touched by aliases     : {dist['tests_with_normalization']}")
    print(f"  Ground-truth tool entries    : {total_entries}")
    print(f"  Direct canonical entries     : {direct_entries}")
    print(f"  Alias-normalized entries     : {normalized_entries}")

    print(f"\n{'-' * 72}\n  NORMALIZATION RULES IN USE\n{'-' * 72}")
    for alias, canonical in sorted(_GT_ALIASES.items()):
        count = dist["remap_counts"].get((alias, canonical), 0)
        print(f"  {alias:<28} -> {canonical:<28} count:{count}")

    print(f"\n{'-' * 72}\n  RAW LABELS COLLAPSED BY CANONICAL TOOL\n{'-' * 72}")
    for canonical, count in dist["canonical_counts"].most_common():
        raw_parts = ", ".join(
            f"{raw}:{n}" for raw, n in dist["raw_by_canonical"][canonical].most_common()
        )
        print(f"  {canonical:<30} {count:>4}  {bar(count, total_entries, 20)}")
        print(f"    accepted: {accepted_display(canonical)}")
        print(f"    raw     : {raw_parts}")

    print(f"\n{'-' * 72}\n  TOP CANONICAL TOOLS BY CATEGORY\n{'-' * 72}")
    for category, counts in sorted(dist["category_canonical"].items()):
        top = ", ".join(f"{tool}:{n}" for tool, n in counts.most_common(5))
        print(f"  {category:<14} {top}")

    print(f"\n{'=' * 72}\n")


def draw_empty(ax, title, message):
    ax.set_title(title, fontweight="bold")
    ax.axis("off")
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=11, color="#555555")


def plot_distribution(data, dist):
    blue = "#4C72B0"
    green = "#55A868"
    orange = "#DD8452"
    red = "#C44E52"

    total_entries = dist["total_tool_entries"]
    normalized_entries = sum(dist["remap_counts"].values())
    direct_entries = total_entries - normalized_entries

    fig = plt.figure(figsize=(20, 18), facecolor="#F8F9FA")
    fig.suptitle(
        f"Tool Normalization Distribution - {len(data)} tests, {total_entries} ground-truth tool entries",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )
    gs = gridspec.GridSpec(
        2, 2,
        figure=fig,
        hspace=0.42,
        wspace=0.32,
        top=0.93,
        bottom=0.06,
        left=0.08,
        right=0.96,
    )

    ax1 = fig.add_subplot(gs[0, 0])
    summary_labels = ["direct labels", "alias-remapped labels", "tests with aliases"]
    summary_vals = [direct_entries, normalized_entries, dist["tests_with_normalization"]]
    summary_colors = [green, orange, red]
    y1 = np.arange(len(summary_labels))
    ax1.barh(y1, summary_vals, color=summary_colors)
    ax1.set_yticks(y1)
    ax1.set_yticklabels(summary_labels, fontsize=10)
    ax1.invert_yaxis()
    ax1.set_title("Normalization Summary", fontweight="bold")
    ax1.set_xlabel("Count")
    for i, value in enumerate(summary_vals):
        ax1.text(value + 0.5, i, str(value), va="center", fontsize=9)

    ax2 = fig.add_subplot(gs[0, 1])
    top_canonical = dist["canonical_counts"].most_common(20)
    if top_canonical:
        labels2, vals2 = zip(*top_canonical)
        y2 = np.arange(len(labels2))
        ax2.barh(y2, vals2, color=blue)
        ax2.set_yticks(y2)
        ax2.set_yticklabels(labels2, fontsize=8)
        ax2.invert_yaxis()
        ax2.set_title("Top Canonical Tools", fontweight="bold")
        ax2.set_xlabel("Ground-truth entries")
        for i, value in enumerate(vals2):
            ax2.text(value + 0.5, i, str(value), va="center", fontsize=8)
    else:
        draw_empty(ax2, "Top Canonical Tools", "No ground-truth tools found")

    ax3 = fig.add_subplot(gs[1, 0])
    remaps = dist["remap_counts"].most_common(20)
    if remaps:
        labels3 = [f"{raw} -> {canonical}" for (raw, canonical), _ in remaps]
        vals3 = [value for _, value in remaps]
        y3 = np.arange(len(labels3))
        ax3.barh(y3, vals3, color=orange)
        ax3.set_yticks(y3)
        ax3.set_yticklabels(labels3, fontsize=8)
        ax3.invert_yaxis()
        ax3.set_title("Alias Remaps Applied", fontweight="bold")
        ax3.set_xlabel("Ground-truth entries")
        for i, value in enumerate(vals3):
            ax3.text(value + 0.5, i, str(value), va="center", fontsize=8)
    else:
        draw_empty(ax3, "Alias Remaps Applied", "No alias remaps applied")

    ax4 = fig.add_subplot(gs[1, 1])
    categories = sorted(dist["category_canonical"].keys())
    heat_tools = [tool for tool, _ in dist["canonical_counts"].most_common(14)]
    if categories and heat_tools:
        matrix = np.array([
            [dist["category_canonical"][category].get(tool, 0) for tool in heat_tools]
            for category in categories
        ])
        im = ax4.imshow(matrix, cmap="Blues", aspect="auto")
        ax4.set_xticks(range(len(heat_tools)))
        ax4.set_xticklabels(heat_tools, rotation=35, ha="right", fontsize=8)
        ax4.set_yticks(range(len(categories)))
        ax4.set_yticklabels(categories, fontsize=9)
        ax4.set_title("Category x Canonical Tool Heatmap", fontweight="bold")
        cbar = plt.colorbar(im, ax=ax4, shrink=0.75, label="Count")
        max_value = matrix.max() if matrix.size else 0
        for i in range(len(categories)):
            for j in range(len(heat_tools)):
                value = matrix[i, j]
                if value:
                    ax4.text(
                        j,
                        i,
                        str(value),
                        ha="center",
                        va="center",
                        fontsize=7,
                        color="white" if max_value and value > max_value * 0.6 else "black",
                    )
    else:
        cbar = None
        draw_empty(ax4, "Category x Canonical Tool Heatmap", "No category/tool data found")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(IMAGE_PATH, dpi=150, bbox_inches="tight")
    print(f"  Saved -> {IMAGE_PATH}")

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    panel_exports = [
        ("summary", [ax1]),
        ("canonical", [ax2]),
        ("aliases", [ax3]),
        ("category_heatmap", [ax4] + ([cbar.ax] if cbar else [])),
    ]
    for key, axes in panel_exports:
        panel_path = SEPARATE_IMAGE_PATHS[key]
        save_axes_image(fig, renderer, axes, panel_path)
        print(f"  Saved -> {panel_path}")

    plt.close(fig)


def main():
    data = json.loads(DATASET_PATH.read_text())
    dist = collect_distribution(data)
    print_distribution(data, dist)
    plot_distribution(data, dist)


if __name__ == "__main__":
    main()