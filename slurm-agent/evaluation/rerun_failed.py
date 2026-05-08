#!/usr/bin/env python3
"""Re-run only the rows in a results JSON whose error matches a transient
infra pattern (TaskGroup / post_writer / ConnectError / etc.).

Usage:
  python evaluation/rerun_failed.py \
      --results evaluation/results/scenario_eval_YYYYMMDD_HHMMSS.json \
      --output  evaluation/results/scenario_eval_YYYYMMDD_HHMMSS_rerun.json \
      [--workers 2] \
      [--main-model slurm-agent] [--llm-provider openai] [--auto-approve]

Steps:
  1. Load the input results JSON.
  2. Identify rows where `error` matches the transient regex.
  3. Write their test_ids to a temp file.
  4. Invoke scenario_eval.py with --test-ids-file to rerun just those.
  5. Merge new results back into the snapshot, replacing transient-failure rows.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TRANSIENT_RE = re.compile(
    r"TaskGroup|post_writer|ConnectError|Connection reset|"
    r"ServerDisconnectedError|ClientConnectorError|Streaming error",
    re.IGNORECASE,
)


def load_results(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_transient_failures(snap: dict) -> list[str]:
    rows = snap.get("results") or snap.get("tests") or []
    ids: list[str] = []
    for r in rows:
        err = (r.get("error") or "").strip()
        if err and TRANSIENT_RE.search(err):
            tid = r.get("id") or r.get("test_id")
            if tid:
                ids.append(tid)
    return ids


def merge(snap: dict, new_rows: list[dict]) -> dict:
    rows = snap.get("results") or snap.get("tests") or []
    by_id = {r.get("id") or r.get("test_id"): r for r in rows}
    for nr in new_rows:
        tid = nr.get("id") or nr.get("test_id")
        if tid and tid in by_id:
            by_id[tid] = nr
    merged_rows = list(by_id.values())
    if "results" in snap:
        snap["results"] = merged_rows
    else:
        snap["tests"] = merged_rows
    return snap


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--main-model", default="slurm-agent")
    ap.add_argument("--llm-provider", default="openai")
    ap.add_argument("--auto-approve", action="store_true")
    ap.add_argument("--judge", action="store_true")
    args = ap.parse_args()

    snap = load_results(args.results)
    ids = find_transient_failures(snap)
    print(f"[rerun] Found {len(ids)} transient-failure rows to retry")
    if not ids:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as f:
            json.dump(snap, f, indent=2)
        return 0

    here = Path(__file__).parent
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
        json.dump(ids, tf)
        tf_path = Path(tf.name)

    try:
        cmd = [
            sys.executable, str(here / "scenario_eval.py"),
            "--test-ids-file", str(tf_path),
            "--workers", str(args.workers),
            "--main-model", args.main_model,
            "--llm-provider", args.llm_provider,
        ]
        if args.auto_approve:
            cmd.append("--auto-approve")
        if args.judge:
            cmd.append("--judge")
        print(f"[rerun] Running: {' '.join(cmd)}")
        proc = subprocess.run(cmd, cwd=str(here.parent))
        if proc.returncode != 0:
            print(f"[rerun] scenario_eval.py exited with {proc.returncode}", file=sys.stderr)
            return proc.returncode
    finally:
        try:
            os.unlink(tf_path)
        except OSError:
            pass

    # Locate the latest results file produced by scenario_eval.py
    results_dir = here / "results"
    candidates = sorted(
        results_dir.glob("scenario_eval_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    candidates = [c for c in candidates if c != args.results.resolve()]
    if not candidates:
        print("[rerun] No new results file found", file=sys.stderr)
        return 1
    new_snap = load_results(candidates[0])
    new_rows = new_snap.get("results") or new_snap.get("tests") or []
    print(f"[rerun] Merging {len(new_rows)} re-run rows from {candidates[0].name}")

    merged = merge(snap, new_rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
    print(f"[rerun] Wrote merged snapshot to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
