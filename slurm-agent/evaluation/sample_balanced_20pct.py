#!/usr/bin/env python3
"""Sample a stratified 20% balanced subset from the 3.1k eval dataset.

Ensures equal representation per category (same N from each).
Uses a fixed seed for reproducibility.

Run: python evaluation/sample_balanced_20pct.py
Output: evaluation/balanced_20pct_dataset.json
"""

import json
import random
from collections import defaultdict
from pathlib import Path

SEED = 42
TARGET_PER_CATEGORY = 57  # ~627 total across 11 categories

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

    # Balanced sample: same N from each category
    random.seed(SEED)
    sampled = []
    for cat in sorted(by_category.keys()):
        cases = by_category[cat]
        n = min(TARGET_PER_CATEGORY, len(cases))
        picked = random.sample(cases, n)
        sampled.extend(picked)
        print(f"  {cat:<15} {len(cases):>4} → {n:>3} sampled")

    random.seed(SEED)
    random.shuffle(sampled)
    print(f"\nTotal sampled: {len(sampled)} ({len(sampled)/len(dataset)*100:.1f}%)")

    # Save dataset
    out_path = Path(__file__).parent / "balanced_20pct_dataset.json"
    out_path.write_text(json.dumps(sampled, indent=2))
    print(f"Saved: {out_path}")

    # Save just IDs (for extracting GPT-5-mini results)
    ids_path = Path(__file__).parent / "balanced_20pct_ids.json"
    ids = [c["id"] for c in sampled]
    ids_path.write_text(json.dumps(ids, indent=2))
    print(f"Saved: {ids_path}")

    print(f"\nRun LoRA eval:")
    print(f"  python evaluation/scenario_eval.py --dataset evaluation/balanced_20pct_dataset.json")
    print(f"\nExtract GPT-5-mini results for same subset:")
    print(f"  python evaluation/extract_subset_results.py")


if __name__ == "__main__":
    main()
