#!/usr/bin/env python3
"""Create a deterministic 80/20 stratified train/test split from dataset.json.

Stratifies by (category x scenario) so proportions are preserved.
Outputs:
  evaluation/split_train_ids.json   — list of test_id strings (80%)
  evaluation/split_test_ids.json    — list of test_id strings (20%)

Usage:
    python evaluation/create_split.py [--test-frac 0.2] [--seed 42]
"""
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="evaluation/dataset.json")
    p.add_argument("--test-frac", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    ds = json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    print(f"Loaded {len(ds)} cases from {args.dataset}")

    # Group by (category, scenario)
    buckets: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in ds:
        key = (row["category"], row.get("scenario", "default"))
        buckets[key].append(row["id"])

    rng = random.Random(args.seed)
    train_ids, test_ids = [], []

    for key in sorted(buckets):
        ids = sorted(buckets[key])
        rng.shuffle(ids)
        n_test = max(1, round(len(ids) * args.test_frac))
        test_ids.extend(ids[:n_test])
        train_ids.extend(ids[n_test:])

    train_ids.sort()
    test_ids.sort()

    out_dir = Path("evaluation")
    out_dir.joinpath("split_train_ids.json").write_text(
        json.dumps(train_ids, indent=2), encoding="utf-8"
    )
    out_dir.joinpath("split_test_ids.json").write_text(
        json.dumps(test_ids, indent=2), encoding="utf-8"
    )

    print(f"\nSplit (seed={args.seed}, test_frac={args.test_frac}):")
    print(f"  Train: {len(train_ids)} IDs → evaluation/split_train_ids.json")
    print(f"  Test:  {len(test_ids)} IDs → evaluation/split_test_ids.json")

    # Category breakdown
    cat_train = defaultdict(int)
    cat_test = defaultdict(int)
    id_to_cat = {row["id"]: row["category"] for row in ds}
    for tid in train_ids:
        cat_train[id_to_cat[tid]] += 1
    for tid in test_ids:
        cat_test[id_to_cat[tid]] += 1

    print(f"\n{'Category':<20} {'Train':>6} {'Test':>6} {'Total':>6} {'Test%':>6}")
    for cat in sorted(set(list(cat_train) + list(cat_test))):
        tr = cat_train.get(cat, 0)
        te = cat_test.get(cat, 0)
        tot = tr + te
        print(f"  {cat:<18} {tr:>6} {te:>6} {tot:>6} {te/tot*100:>5.1f}%")

    print(f"  {'TOTAL':<18} {len(train_ids):>6} {len(test_ids):>6} {len(train_ids)+len(test_ids):>6} {len(test_ids)/(len(train_ids)+len(test_ids))*100:>5.1f}%")


if __name__ == "__main__":
    main()
