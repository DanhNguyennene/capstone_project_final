#!/usr/bin/env python3
"""Cross-reference gpt-5-mini eval failures with the 80/20 stratified train/test split."""
from __future__ import annotations
import json, random
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "evaluation" / "dataset.json").read_text())

# Reproduce build_agent_sft_v2.stratified_split(seed=42, ratio=0.2)
rng = random.Random(42)
buckets: dict[tuple[str, str], list[dict]] = defaultdict(list)
for r in data:
    buckets[(r.get("category", "?"), r.get("scenario", "?"))].append(r)
train, test = [], []
for key in sorted(buckets):
    b = buckets[key][:]
    rng.shuffle(b)
    n_test = max(1, round(len(b) * 0.2)) if len(b) >= 2 else 0
    test.extend(b[:n_test])
    train.extend(b[n_test:])
rng.shuffle(train); rng.shuffle(test)
train_ids = {r["id"] for r in train}
test_ids = {r["id"] for r in test}

snap = json.loads((ROOT / "evaluation" / "results" / "eval_all_20260504_rescored.json").read_text(encoding="utf-8"))
results = snap["results"]
by_id = {r["test_id"]: r for r in results}
print(f"snapshot rows: {len(results)}  unique ids: {len(by_id)}")

failed_ids = {r["test_id"] for r in results if not r.get("passed")}
bad = {r["test_id"] for r in results if r.get("bad_test_case")}

failed_in_train = failed_ids & train_ids
failed_in_test = failed_ids & test_ids
bad_in_train = bad & train_ids
bad_in_test = bad & test_ids

print()
print(f"Total failed (gpt-5-mini, full 3135) : {len(failed_ids)}")
print(f"  -> in TRAIN split ({len(train_ids)}): {len(failed_in_train)} "
      f"({100*len(failed_in_train)/max(1,len(train_ids)):.1f}% of train)")
print(f"  -> in TEST  split ({len(test_ids)}) : {len(failed_in_test)} "
      f"({100*len(failed_in_test)/max(1,len(test_ids)):.1f}% of test)")
print()
print(f"Flagged bad_test_case: {len(bad)}")
print(f"  -> in TRAIN: {len(bad_in_train)}   in TEST: {len(bad_in_test)}")

print()
print("Failed-in-train by category:")
cat_train = Counter(by_id[i]["category"] for i in failed_in_train)
for c, n in sorted(cat_train.items(), key=lambda x: -x[1]):
    print(f"  {c:<14} {n}")

print()
print("Failed-in-test by category:")
cat_test = Counter(by_id[i]["category"] for i in failed_in_test)
for c, n in sorted(cat_test.items(), key=lambda x: -x[1]):
    print(f"  {c:<14} {n}")
