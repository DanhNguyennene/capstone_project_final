#!/usr/bin/env python3
"""Audit ground-truth quality in evaluation/dataset.json and report
how many suspect rows landed in the train vs. test split (seed=42, ratio=0.2,
stratified by category x scenario — same logic as build_agent_sft_v2.py).

Usage:
    cd slurm-agent
    python evaluation/audit_gt_quality.py
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATASET = ROOT / "evaluation" / "dataset.json"

# Pull the canonical tool name sets from the build script.
from training.build_agent_sft import (  # type: ignore
    OBSERVER_TOOL_NAMES,
    OPERATOR_TOOL_NAMES,
    DANGEROUS_TOOLS,
)

KNOWN_TOOLS = OBSERVER_TOOL_NAMES | OPERATOR_TOOL_NAMES

# Categories where an empty tools list is a legitimate "clarification" outcome.
# For all other categories, empty tools usually means gpt-5-mini failed to emit
# a plan.
CLARIFICATION_OK_CATEGORIES = {"docs", "domain"}

# Categories that should mutate cluster state. If target_state == source_state,
# the action either was a read-only intent (then tools should still be present)
# or the GT generator silently no-op'd.
ACTION_CATEGORIES = {
    "action", "submission", "bulk", "multi_step", "safety", "account", "edge",
}


def stratified_split(rows, test_ratio=0.2, seed=42):
    """Identical to training.build_agent_sft_v2.stratified_split."""
    rng = random.Random(seed)
    buckets: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        buckets[(r.get("category", "?"), r.get("scenario", "?"))].append(r)
    train, test = [], []
    for key in sorted(buckets):
        b = buckets[key][:]
        rng.shuffle(b)
        n_test = max(1, round(len(b) * test_ratio)) if len(b) >= 2 else 0
        test.extend(b[:n_test])
        train.extend(b[n_test:])
    rng.shuffle(train)
    rng.shuffle(test)
    return train, test


def classify(row: dict) -> list[str]:
    """Return list of failure tags for a row (empty = clean)."""
    tags: list[str] = []
    gt = row.get("ground_truth")
    cat = row.get("category", "?")

    if not isinstance(gt, dict):
        return ["malformed_gt"]

    tools = gt.get("tools")
    if not isinstance(tools, list):
        tags.append("tools_not_list")
        tools = []

    # Empty tools — only acceptable for docs/domain (informational answers)
    if len(tools) == 0:
        if cat not in CLARIFICATION_OK_CATEGORIES:
            tags.append("empty_tools")

    # Unknown tool name (not in OBSERVER ∪ OPERATOR)
    unknown = [t for t in tools if t not in KNOWN_TOOLS]
    if unknown:
        tags.append("unknown_tool")

    # handoff=True implies operator should run something dangerous
    if gt.get("handoff") is True:
        if not any(t in DANGEROUS_TOOLS for t in tools):
            tags.append("handoff_without_action")

    # hitl=True only sensible for dangerous actions
    if gt.get("hitl") is True and not any(t in DANGEROUS_TOOLS for t in tools):
        tags.append("hitl_without_dangerous")

    # No-op for action categories: target == source AND tools claim a mutation
    if cat in ACTION_CATEGORIES:
        if row.get("source_state") == row.get("target_state"):
            if any(t in DANGEROUS_TOOLS for t in tools):
                tags.append("noop_state_with_dangerous")
            elif not tools:
                tags.append("noop_state_and_empty_tools")

    # Empty / trivially short user input
    inp = (row.get("input") or "").strip()
    if len(inp) < 4:
        tags.append("empty_input")

    # Keywords missing/empty (used by some scoring paths)
    kw = gt.get("keywords")
    if not isinstance(kw, list) or not kw:
        tags.append("empty_keywords")

    return tags


def main() -> int:
    data = json.loads(DATASET.read_text())
    train, test = stratified_split(data, 0.2, 42)
    train_ids = {r["id"] for r in train}
    test_ids = {r["id"] for r in test}

    per_tag_train = Counter()
    per_tag_test = Counter()
    per_tag_all = Counter()
    bad_train_ids: set[str] = set()
    bad_test_ids: set[str] = set()
    examples: dict[str, list[str]] = defaultdict(list)

    for row in data:
        tags = classify(row)
        if not tags:
            continue
        rid = row.get("id", "?")
        in_train = rid in train_ids
        in_test = rid in test_ids
        for t in tags:
            per_tag_all[t] += 1
            if in_train:
                per_tag_train[t] += 1
            if in_test:
                per_tag_test[t] += 1
            if len(examples[t]) < 3:
                examples[t].append(rid)
        if in_train:
            bad_train_ids.add(rid)
        if in_test:
            bad_test_ids.add(rid)

    print(f"Dataset rows : {len(data)}")
    print(f"Train rows   : {len(train)}")
    print(f"Test  rows   : {len(test)}")
    print()
    print(f"{'tag':<32} {'all':>6} {'train':>7} {'test':>6}   examples")
    print("-" * 80)
    for tag in sorted(per_tag_all, key=lambda t: -per_tag_all[t]):
        ex = ", ".join(examples[tag])
        print(f"{tag:<32} {per_tag_all[tag]:>6} {per_tag_train[tag]:>7} {per_tag_test[tag]:>6}   {ex}")
    print()
    print(f"UNIQUE suspect rows  total : {sum(1 for r in data if classify(r))}")
    print(f"UNIQUE suspect rows  train : {len(bad_train_ids)} / {len(train)} "
          f"({100*len(bad_train_ids)/max(1,len(train)):.1f}%)")
    print(f"UNIQUE suspect rows  test  : {len(bad_test_ids)} / {len(test)} "
          f"({100*len(bad_test_ids)/max(1,len(test)):.1f}%)")

    # Per-category breakdown of suspect train rows
    print()
    print("Suspect rows by category (train / test):")
    by_cat_train = Counter()
    by_cat_test = Counter()
    by_cat_total = Counter()
    for row in data:
        by_cat_total[row.get("category", "?")] += 1
        if classify(row):
            if row["id"] in train_ids:
                by_cat_train[row.get("category", "?")] += 1
            if row["id"] in test_ids:
                by_cat_test[row.get("category", "?")] += 1
    print(f"{'category':<14} {'total':>6} {'bad_train':>10} {'bad_test':>9}")
    print("-" * 50)
    for cat in sorted(by_cat_total):
        print(f"{cat:<14} {by_cat_total[cat]:>6} {by_cat_train[cat]:>10} {by_cat_test[cat]:>9}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
