#!/usr/bin/env python3
"""Deterministically regenerate the 627 holdout test ids matching
training/build_agent_sft_v2.stratified_split(seed=42, ratio=0.2).

Use when training/out/agent_sft_v2_ids.json is missing on the pod
(the HF adapter repo only hosts model weights).

Output: evaluation/v2_test_ids.json (flat list, scenario_eval --test-ids-file format).
"""
from __future__ import annotations
import json, random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    data = json.loads((ROOT / "evaluation" / "dataset.json").read_text())
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
    test_ids = [r["id"] for r in test]
    train_ids = [r["id"] for r in train]

    out_flat = ROOT / "evaluation" / "v2_test_ids.json"
    out_flat.write_text(json.dumps(test_ids, indent=2))

    out_full = ROOT / "training" / "out" / "agent_sft_v2_ids.json"
    out_full.parent.mkdir(parents=True, exist_ok=True)
    out_full.write_text(json.dumps({"train_ids": train_ids, "test_ids": test_ids}, indent=2))

    print(f"train={len(train_ids)} test={len(test_ids)}")
    print(f"wrote {out_flat}")
    print(f"wrote {out_full}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
