#!/usr/bin/env python3
"""Clean polluted rows from agent_sft.jsonl.

Removes rows where any assistant message contains the canned
generation-pipeline failure string left behind by an earlier dataset-
synthesis bug. Drops about 3% of the corpus (verified: 315 / 10,171).

Usage:
    python training/clean_agent_sft.py
    python training/clean_agent_sft.py --in training/out/agent_sft.jsonl \
                                        --out training/out/agent_sft_v3.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


# Phrases that mark a polluted row. All three were emitted by the same
# upstream failure mode and tend to co-occur; matching any is sufficient.
_POLLUTION_PATTERNS = [
    re.compile(r"request has an edge case", re.IGNORECASE),
    re.compile(r"what I can determine: (script|process|none|the answer)", re.IGNORECASE),
]


def _is_polluted(row: dict) -> bool:
    for msg in row.get("messages") or []:
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content") or ""
        if not content:
            continue
        for pat in _POLLUTION_PATTERNS:
            if pat.search(content):
                return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src",
                    default="training/out/agent_sft.jsonl")
    ap.add_argument("--out", dest="dst",
                    default="training/out/agent_sft_v3.jsonl")
    ap.add_argument("--report", action="store_true",
                    help="Only report counts; do not write output file.")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    src = root / args.src if not Path(args.src).is_absolute() else Path(args.src)
    dst = root / args.dst if not Path(args.dst).is_absolute() else Path(args.dst)

    if not src.exists():
        print(f"ERROR: source not found: {src}", file=sys.stderr)
        return 2

    total = 0
    kept = 0
    dropped = 0

    out_f = None if args.report else dst.open("w", encoding="utf-8")
    try:
        with src.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line:
                    continue
                total += 1
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    dropped += 1
                    continue
                if _is_polluted(row):
                    dropped += 1
                    continue
                kept += 1
                if out_f is not None:
                    out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
    finally:
        if out_f is not None:
            out_f.close()

    pct = (dropped / total * 100.0) if total else 0.0
    print(f"  source : {src}")
    if not args.report:
        print(f"  output : {dst}")
    print(f"  total  : {total}")
    print(f"  kept   : {kept}")
    print(f"  dropped: {dropped}  ({pct:.2f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
