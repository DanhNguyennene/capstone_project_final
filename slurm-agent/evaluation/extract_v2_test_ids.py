#!/usr/bin/env python3
"""Extract test_ids from training/out/agent_sft_v2_ids.json into a flat list
JSON file that scenario_eval.py --test-ids-file can consume.

Usage:
    cd slurm-agent
    python evaluation/extract_v2_test_ids.py
    # → evaluation/v2_test_ids.json (a flat list of row ids)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "training" / "out" / "agent_sft_v2_ids.json"
DST = ROOT / "evaluation" / "v2_test_ids.json"


def main() -> int:
    if not SRC.exists():
        print(f"Source not found: {SRC}", file=sys.stderr)
        return 1
    payload = json.loads(SRC.read_text())
    test_ids = payload.get("test_ids", [])
    if not test_ids:
        print("No test_ids found in source.", file=sys.stderr)
        return 1
    # Write as a flat list (the format scenario_eval --test-ids-file expects)
    DST.write_text(json.dumps(test_ids, indent=2))
    print(f"Wrote {len(test_ids)} test ids → {DST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
