#!/usr/bin/env python3
"""Extract GPT-5-mini results for the balanced 20% subset IDs.

Reads the existing GPT-5-mini eval results and filters to only the
test IDs in balanced_20pct_ids.json for fair comparison.

Run: python evaluation/extract_subset_results.py
"""

import json
import glob
import os
from pathlib import Path
from collections import Counter

def main():
    eval_dir = Path(__file__).parent
    ids_path = eval_dir / "balanced_20pct_ids.json"

    if not ids_path.exists():
        print("Run sample_balanced_20pct.py first to generate IDs")
        return

    target_ids = set(json.loads(ids_path.read_text()))
    print(f"Target IDs: {len(target_ids)}")

    # Find GPT-5-mini results (look for multi_turn or gpt5mini files)
    results_dir = eval_dir / "results"
    candidates = []
    for f in sorted(results_dir.glob("*.json")):
        if "gpt5mini" in f.name or "multi_turn" in f.name or "latest" in f.name:
            candidates.append(f)

    if not candidates:
        # Fall back to all eval json files
        candidates = sorted(results_dir.glob("eval_*.json"), key=os.path.getmtime)

    print(f"\nCandidate result files:")
    for f in candidates:
        print(f"  {f.name} ({f.stat().st_size // 1024}KB)")

    # Try each file to find GPT-5-mini results
    best_file = None
    best_matches = 0
    for f in candidates:
        try:
            data = json.loads(f.read_text())
            results = data.get("results", [])
            matches = sum(1 for r in results if r.get("test_id") in target_ids)
            if matches > best_matches:
                best_matches = matches
                best_file = f
                print(f"  → {f.name}: {matches}/{len(target_ids)} matching IDs")
        except Exception as e:
            continue

    if not best_file or best_matches == 0:
        print("\nNo matching results found. Available result files:")
        for f in sorted(results_dir.glob("*.json")):
            print(f"  {f.name}")
        return

    print(f"\nUsing: {best_file.name} ({best_matches} matches)")
    data = json.loads(best_file.read_text())
    results = data.get("results", [])

    # Filter to our subset
    subset_results = [r for r in results if r.get("test_id") in target_ids]
    found_ids = {r["test_id"] for r in subset_results}
    missing_ids = target_ids - found_ids

    if missing_ids:
        print(f"  Warning: {len(missing_ids)} IDs not found in results")

    # Compute metrics
    passed = sum(1 for r in subset_results if r.get("passed"))
    total = len(subset_results)
    avg_overall = sum(r.get("overall", 0) for r in subset_results) / total if total else 0

    print(f"\n{'='*60}")
    print(f"GPT-5-mini on balanced 20% subset ({total} cases)")
    print(f"{'='*60}")
    print(f"  Pass Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"  Avg Score: {avg_overall*100:.1f}%")

    # By category
    by_cat = Counter()
    by_cat_pass = Counter()
    for r in subset_results:
        cat = r.get("category", "unknown")
        by_cat[cat] += 1
        if r.get("passed"):
            by_cat_pass[cat] += 1

    print(f"\n  {'Category':<15} {'N':>4} {'Pass%':>6}")
    print(f"  {'-'*30}")
    for cat in sorted(by_cat.keys()):
        n = by_cat[cat]
        p = by_cat_pass[cat]
        print(f"  {cat:<15} {n:>4} {p/n*100:>5.1f}%")

    # Save subset results
    out_path = eval_dir / "results" / "gpt5mini_balanced_20pct.json"
    out_data = {
        "config": data.get("config", {}),
        "results": subset_results,
        "metrics": {
            "total": total,
            "passed": passed,
            "pass_rate": passed / total if total else 0,
            "avg_overall": avg_overall,
        },
    }
    out_path.write_text(json.dumps(out_data, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
