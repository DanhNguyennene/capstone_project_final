#!/usr/bin/env python3
"""Build SFT data for the existing TodoTracker specialist model slot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

TODO_SYSTEM_PROMPT = """\
You are a task planner for a Slurm HPC assistant with two agents:
- Observer: read-only tools (squeue, sinfo, sacct, etc.)
- Operator: action tools (sbatch, scancel, scontrol_hold, etc.)

Given a user request, output a short task plan as a JSON array of strings.

Rules:
- Output ONLY a JSON array of strings. No markdown, no explanation.
- 3-5 steps max. Be specific to the request.
- Do NOT name tool names.
- For actions (submit, cancel, hold, release): say "Hand off to Operator to ...".
- For read-only tasks: just describe what to check.
- Last step is always the deliverable.
"""


def classify_plan(row: dict[str, Any]) -> list[str]:
    text = str(row.get("input") or "").strip()
    lower = text.lower()
    category = str(row.get("category") or "")
    gt = row.get("ground_truth") or {}
    handoff = bool(gt.get("handoff"))
    hitl = bool(gt.get("hitl"))

    if handoff:
        verb = "perform the requested cluster action"
        if any(word in lower for word in ["submit", "sbatch", "run", "launch"]):
            verb = "submit the requested workload"
        elif any(word in lower for word in ["cancel", "kill", "stop"]):
            verb = "cancel the requested job or jobs"
        elif "hold" in lower:
            verb = "hold the requested job or jobs"
        elif "release" in lower:
            verb = "release the requested job or jobs"
        elif "requeue" in lower:
            verb = "requeue the requested job or jobs"
        elif "resume" in lower:
            verb = "resume the requested job or node"
        elif "suspend" in lower:
            verb = "suspend the requested job or node"

        steps = ["Verify the target and requested action"]
        if hitl:
            steps.append("Confirm that the action needs user approval")
        steps.append(f"Hand off to Operator to {verb}")
        steps.append("Verify the action result")
        steps.append("Report results")
        return steps[:5]

    if category == "diagnose":
        return [
            "Check the relevant job and cluster state",
            "Review failure, pending, or resource indicators",
            "Identify the likely cause",
            "Report root cause and recommended fix",
        ]
    if category == "docs":
        return [
            "Review the relevant Slurm reference information",
            "Extract the command or policy detail needed",
            "Answer with concise guidance",
        ]
    if category == "domain":
        return [
            "Check the relevant cluster context",
            "Combine live state with Slurm policy knowledge",
            "Explain the operational implication",
        ]
    if category == "account":
        return [
            "Check the requested account or association information",
            "Review limits, usage, or membership details",
            "Summarize the account findings",
        ]
    if category == "edge":
        return [
            "Check whether the request is valid and specific",
            "Identify missing, conflicting, or unsafe details",
            "Ask for clarification or provide safe guidance",
        ]
    return [
        "Check the requested Slurm state",
        "Review the relevant jobs, nodes, or partitions",
        "Summarize the result for the user",
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build TodoTracker-compatible specialist SFT JSONL")
    parser.add_argument("--dataset", default="evaluation/dataset.json")
    parser.add_argument("--out", default="training/out/todo_specialist_sft.jsonl")
    parser.add_argument("--limit", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset_path = (ROOT / args.dataset).resolve()
    output_path = (ROOT / args.out).resolve()
    rows = json.loads(dataset_path.read_text())
    if args.limit > 0:
        rows = rows[: args.limit]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            sample = {
                "messages": [
                    {"role": "system", "content": TODO_SYSTEM_PROMPT},
                    {"role": "user", "content": row.get("input") or ""},
                    {"role": "assistant", "content": json.dumps(classify_plan(row), ensure_ascii=True)},
                ],
                "metadata": {
                    "id": row.get("id"),
                    "category": row.get("category"),
                    "scenario": row.get("scenario"),
                },
            }
            handle.write(json.dumps(sample, ensure_ascii=True) + "\n")
    print(f"wrote {len(rows)} todo-specialist SFT samples -> {output_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()