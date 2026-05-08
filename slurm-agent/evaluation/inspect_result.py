"""Inspect a single saved eval result row.

Usage:
    python evaluation/inspect_result.py <test_id> [results_json]

Example:
    python evaluation/inspect_result.py bulk_bal200_006
    python evaluation/inspect_result.py bulk_bal200_006 \
        evaluation/results/eval_all_20260508_132622.json
"""
from __future__ import annotations

import glob
import json
import sys


def _load_rows(src: str):
    data = json.load(open(src))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("results", "rows", "data"):
            v = data.get(key)
            if isinstance(v, list):
                return v
        # Fallback: first list-of-dicts value
        for v in data.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return v
    return []


def _short(v, n: int = 600) -> str:
    if v is None:
        return "None"
    t = v if isinstance(v, str) else json.dumps(v, default=str)
    return t if len(t) <= n else t[:n] + "..."


FIELDS = (
    "prompt",
    "gt_tools",
    "agent_tools",
    "tool_call_history",
    "gt_handoff",
    "agent_handoff",
    "gt_hitl",
    "agent_hitl",
    "gt_keywords",
    "keyword_score",
    "routing_match",
    "hitl_match",
    "state_match",
    "tool_recall",
    "overall",
    "error",
    "agent_response",
)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    tid = sys.argv[1]
    if len(sys.argv) >= 3:
        srcs = [sys.argv[2]]
    else:
        srcs = sorted(
            glob.glob("evaluation/results/eval_all_*.json"), reverse=True
        )

    for src in srcs:
        rows = _load_rows(src)
        match = [
            x for x in rows if isinstance(x, dict) and x.get("test_id") == tid
        ]
        if match:
            r = match[0]
            print(f"# file: {src}")
            print(f"# rows: {len(rows)}")
            for k in FIELDS:
                print(f"{k:18s}: {_short(r.get(k))}")
            return 0

    print(f"NOT FOUND: {tid} in {len(srcs)} result file(s)")
    if srcs:
        first = _load_rows(srcs[0])
        print(
            "first 5 ids in latest:",
            [x.get("test_id") for x in first[:5] if isinstance(x, dict)],
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
