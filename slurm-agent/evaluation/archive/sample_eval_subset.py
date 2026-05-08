#!/usr/bin/env python3
"""Sample a stratified 20% subset from the full 3.1k eval dataset.

Stratifies by category so each category is proportionally represented.
Uses a fixed seed for reproducibility.

Run: python evaluation/sample_eval_subset.py
Output: evaluation/eval_subset_20pct.json  (test cases)
        evaluation/eval_subset_20pct_ids.json  (just IDs, for --test-ids-file)

Usage with scenario_eval.py:
  python evaluation/scenario_eval.py --dataset evaluation/eval_subset_20pct.json
"""

import json
import random
from collections import defaultdict
from pathlib import Path

SEED = 42
FRACTION = 0.20

def main():
    dataset_path = Path(__file__).parent / "dataset.json"
    if not dataset_path.exists():
        print(f"dataset.json not found at {dataset_path}")
        return

    dataset = json.loads(dataset_path.read_text())
    print(f"Full dataset: {len(dataset)} cases")

    # Group by category
    by_category = defaultdict(list)
    for case in dataset:
        cat = case.get("category", "unknown")
        by_category[cat].append(case)

    # Stratified sample
    random.seed(SEED)
    sampled = []
    for cat, cases in sorted(by_category.items()):
        n = max(1, round(len(cases) * FRACTION))
        picked = random.sample(cases, min(n, len(cases)))
        sampled.extend(picked)
        print(f"  {cat:<15} {len(cases):>4} → {len(picked):>3} sampled")

    random.shuffle(sampled)
    print(f"\nTotal sampled: {len(sampled)} ({len(sampled)/len(dataset)*100:.1f}%)")

    # Save full subset
    out_path = Path(__file__).parent / "eval_subset_20pct.json"
    out_path.write_text(json.dumps(sampled, indent=2))
    print(f"Saved: {out_path}")

    # Save just IDs
    ids_path = Path(__file__).parent / "eval_subset_20pct_ids.json"
    ids_path.write_text(json.dumps([c["id"] for c in sampled], indent=2))
    print(f"Saved: {ids_path}")

    print(f"\nRun eval:")
    print(f"  python evaluation/scenario_eval.py --dataset evaluation/eval_subset_20pct.json")


if __name__ == "__main__":
    main()
