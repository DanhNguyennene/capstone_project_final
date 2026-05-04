#!/usr/bin/env python3
"""Build chat-style SFT data for the Slurm specialist planner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

TOOL_ALIASES = {
    "sacctmgr_list": "sacctmgr_show",
    "sacctmgr": "sacctmgr_show",
    "scontrol": "scontrol_show",
}


def stable(value: Any) -> Any:
    if isinstance(value, list):
        return [stable(item) for item in value]
    if isinstance(value, dict):
        return {key: stable(value[key]) for key in sorted(value)}
    return value


def compact_state(state: dict[str, Any] | None) -> dict[str, Any]:
    state = state or {}
    jobs = [
        {
            "id": job_id,
            "state": job.get("state"),
            "user": job.get("user"),
            "name": job.get("name"),
            "partition": job.get("partition"),
        }
        for job_id, job in sorted((state.get("jobs") or {}).items())
    ]
    nodes = [
        {
            "name": name,
            "state": node.get("state"),
            "partition": node.get("partition"),
        }
        for name, node in sorted((state.get("nodes") or {}).items())
    ]
    return stable({"jobs": jobs, "nodes": nodes})


def changed_state(source: dict[str, Any] | None, target: dict[str, Any] | None) -> dict[str, Any]:
    source = source or {}
    target = target or {}
    changed_jobs = []
    source_jobs = source.get("jobs") or {}
    target_jobs = target.get("jobs") or {}
    for job_id in sorted(set(source_jobs) | set(target_jobs)):
        before = source_jobs.get(job_id)
        after = target_jobs.get(job_id)
        if stable(before) != stable(after):
            changed_jobs.append({"id": job_id, "before": before, "after": after})

    changed_nodes = []
    source_nodes = source.get("nodes") or {}
    target_nodes = target.get("nodes") or {}
    for name in sorted(set(source_nodes) | set(target_nodes)):
        before = source_nodes.get(name)
        after = target_nodes.get(name)
        if stable(before) != stable(after):
            changed_nodes.append({"name": name, "before": before, "after": after})

    return stable({"jobs": changed_jobs, "nodes": changed_nodes})


def build_user_message(row: dict[str, Any]) -> str:
    payload = stable(
        {
            "task": "Plan the Slurm-specialist behavior for this user request.",
            "id": row.get("id"),
            "category": row.get("category"),
            "scenario": row.get("scenario"),
            "user_request": row.get("input"),
            "source_state": compact_state(row.get("source_state")),
        }
    )
    return json.dumps(payload, indent=2, ensure_ascii=True)


def build_assistant_message(row: dict[str, Any]) -> str:
    ground_truth = row.get("ground_truth") or {}
    tools = [TOOL_ALIASES.get(str(tool), str(tool)) for tool in ground_truth.get("tools") or []]
    payload = stable(
        {
            "route": "operator" if ground_truth.get("handoff") else "observer",
            "tools": tools,
            "requires_handoff": bool(ground_truth.get("handoff")),
            "requires_confirmation": bool(ground_truth.get("hitl")),
            "response_keywords": ground_truth.get("keywords") or [],
            "expected_state_change": changed_state(row.get("source_state"), row.get("target_state")),
        }
    )
    return json.dumps(payload, ensure_ascii=True)


def build_sample(row: dict[str, Any]) -> dict[str, Any]:
    system = " ".join(
        [
            "You are the Slurm specialist planner inside a tool-grounded HPC assistant.",
            "Return JSON only.",
            "Choose the expected Slurm tools, Observer/Operator route, HITL confirmation requirement, response evidence keywords, and expected state change.",
            "Do not execute commands and do not invent unsupported tools.",
        ]
    )
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": build_user_message(row)},
            {"role": "assistant", "content": build_assistant_message(row)},
        ],
        "metadata": {
            "id": row.get("id"),
            "category": row.get("category"),
            "scenario": row.get("scenario"),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Slurm specialist SFT JSONL")
    parser.add_argument("--dataset", default="evaluation/dataset.json")
    parser.add_argument("--out", default="training/out/specialist_sft.jsonl")
    parser.add_argument("--limit", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset_path = (ROOT / args.dataset).resolve()
    output_path = (ROOT / args.out).resolve()
    data = json.loads(dataset_path.read_text())
    if not isinstance(data, list):
        raise TypeError("dataset must be a JSON array")
    if args.limit > 0:
        data = data[: args.limit]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in data:
            handle.write(json.dumps(build_sample(row), ensure_ascii=True) + "\n")

    print(f"wrote {len(data)} specialist SFT samples -> {output_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()