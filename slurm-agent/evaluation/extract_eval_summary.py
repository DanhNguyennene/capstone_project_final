#!/usr/bin/env python3
"""Extract detailed eval results from the running/completed eval.

Run on the A40 pod:
    python evaluation/extract_eval_summary.py

Reads the latest eval JSON from evaluation/results/ OR parses eval_ft.log
if the eval is still running.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent / "results"


def parse_log(log_path: Path) -> dict:
    """Parse eval_ft.log for in-progress results."""
    results = []
    pattern = re.compile(
        r"\[(\d+)/(\d+)\]\s+(\S+)\s+\[(\d+)%\s+(✓|✗|ERR)\]\s+\(([\d.]+)s\)"
    )
    with open(log_path) as f:
        for line in f:
            m = pattern.search(line)
            if m:
                idx, total, case_id, score, status, latency = m.groups()
                results.append({
                    "idx": int(idx),
                    "total": int(total),
                    "case_id": case_id,
                    "score": int(score) / 100.0,
                    "passed": status == "✓",
                    "error": status == "ERR",
                    "latency": float(latency),
                })
    return results


def parse_json(json_path: Path) -> dict:
    """Parse saved JSON results file."""
    data = json.loads(json_path.read_text())
    return data


def categorize(case_id: str) -> str:
    """Infer category from case_id prefix."""
    # Common patterns: acct_list_healthy, read_nodes_pending, etc.
    parts = case_id.split("_")
    # Known category prefixes
    categories = [
        "acct", "read", "diagnose", "diag", "action", "bulk", "safety",
        "submission", "sub", "multi", "account", "edge", "docs", "domain",
        "node", "job"
    ]
    for cat in categories:
        if parts[0] == cat:
            return cat
    # Try first two parts
    if len(parts) >= 2:
        combo = f"{parts[0]}_{parts[1]}"
        return combo
    return parts[0]


def scenario_from_id(case_id: str) -> str:
    """Infer scenario from case_id suffix."""
    for s in ["healthy", "failed", "pending", "mixed", "debug_needed"]:
        if case_id.endswith(s):
            return s
    # Check with variant suffix like _123 (v)
    for s in ["healthy", "failed", "pending", "mixed", "debug_needed"]:
        if s in case_id:
            return s
    return "unknown"


def print_summary(results: list, source: str):
    """Print detailed summary."""
    total = len(results)
    if total == 0:
        print("No results found.")
        return

    passed = sum(1 for r in results if r["passed"])
    errors = sum(1 for r in results if r["error"])
    failed = total - passed - errors

    avg_score = sum(r["score"] for r in results) / total
    avg_latency = sum(r["latency"] for r in results) / total

    print("=" * 70)
    print(f"  Fine-Tuned Model Evaluation Summary")
    print(f"  Source: {source}")
    print("=" * 70)
    print(f"\n  Cases evaluated: {total} / {results[0]['total']}")
    print(f"  Pass rate:       {passed}/{total} ({100*passed/total:.1f}%)")
    print(f"  Fail rate:       {failed}/{total} ({100*failed/total:.1f}%)")
    print(f"  Error rate:      {errors}/{total} ({100*errors/total:.1f}%)")
    print(f"  Avg score:       {100*avg_score:.1f}%")
    print(f"  Avg latency:     {avg_latency:.1f}s")
    print(f"  Est. total time: {avg_latency * results[0]['total'] / 3600:.1f}h")

    # By category
    by_cat = defaultdict(list)
    for r in results:
        by_cat[categorize(r["case_id"])].append(r)

    print(f"\n  {'Category':<15} {'N':>4} {'Pass':>5} {'Rate':>6} {'Avg Score':>10} {'Avg Lat':>8}")
    print(f"  {'-'*15} {'-'*4} {'-'*5} {'-'*6} {'-'*10} {'-'*8}")
    for cat in sorted(by_cat.keys()):
        cases = by_cat[cat]
        n = len(cases)
        p = sum(1 for c in cases if c["passed"])
        avg_s = sum(c["score"] for c in cases) / n
        avg_l = sum(c["latency"] for c in cases) / n
        print(f"  {cat:<15} {n:>4} {p:>5} {100*p/n:>5.1f}% {100*avg_s:>9.1f}% {avg_l:>7.1f}s")

    # By scenario
    by_scenario = defaultdict(list)
    for r in results:
        by_scenario[scenario_from_id(r["case_id"])].append(r)

    print(f"\n  {'Scenario':<15} {'N':>4} {'Pass':>5} {'Rate':>6}")
    print(f"  {'-'*15} {'-'*4} {'-'*5} {'-'*6}")
    for scn in sorted(by_scenario.keys()):
        cases = by_scenario[scn]
        n = len(cases)
        p = sum(1 for c in cases if c["passed"])
        print(f"  {scn:<15} {n:>4} {p:>5} {100*p/n:>5.1f}%")

    # Failure details (first 20)
    failures = [r for r in results if not r["passed"] and not r["error"]]
    if failures:
        print(f"\n  First 20 failures:")
        for r in failures[:20]:
            print(f"    [{r['idx']:>4}] {r['case_id']:<45} [{int(r['score']*100)}%] ({r['latency']:.1f}s)")

    # Export summary as JSON
    summary = {
        "total": total,
        "total_possible": results[0]["total"],
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "pass_rate": passed / total,
        "avg_score": avg_score,
        "avg_latency": avg_latency,
        "by_category": {
            cat: {
                "n": len(cases),
                "passed": sum(1 for c in cases if c["passed"]),
                "pass_rate": sum(1 for c in cases if c["passed"]) / len(cases),
                "avg_score": sum(c["score"] for c in cases) / len(cases),
            }
            for cat, cases in by_cat.items()
        },
        "by_scenario": {
            scn: {
                "n": len(cases),
                "passed": sum(1 for c in cases if c["passed"]),
                "pass_rate": sum(1 for c in cases if c["passed"]) / len(cases),
            }
            for scn, cases in by_scenario.items()
        },
    }

    out_path = RESULTS_DIR / "ft_eval_summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\n  Summary saved to: {out_path}")


def main():
    root = Path(__file__).resolve().parents[1]

    # Try to find latest JSON results first
    json_files = sorted(RESULTS_DIR.glob("eval_all_*.json"), reverse=True)
    today_files = [f for f in json_files if "20260507" in f.name]

    if today_files:
        print(f"Found completed results: {today_files[0].name}")
        data = parse_json(today_files[0])
        # Convert JSON format to our simplified format
        results = []
        for r in data.get("results", []):
            results.append({
                "idx": r.get("idx", 0),
                "total": data.get("metrics", {}).get("n_tests", 3135),
                "case_id": r.get("case_id", ""),
                "score": r.get("overall", 0),
                "passed": r.get("overall", 0) >= 0.8,
                "error": r.get("error", False),
                "latency": r.get("latency", 0),
            })
        print_summary(results, str(today_files[0]))
        return

    # Fall back to parsing the log
    log_candidates = [
        root / "eval_ft.log",
        root / "eval_ft_bf16.log",
    ]
    for log_path in log_candidates:
        if log_path.exists():
            print(f"Parsing in-progress log: {log_path}")
            results = parse_log(log_path)
            if results:
                print_summary(results, str(log_path))
                return

    print("No eval results found. Check eval_ft.log or evaluation/results/")
    sys.exit(1)


if __name__ == "__main__":
    main()
