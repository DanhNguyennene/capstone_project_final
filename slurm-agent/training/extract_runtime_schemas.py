#!/usr/bin/env python3
"""Extract real runtime schemas (MCP tools + handoff tools) into a JSON file.

Run this on the pod (with MCP server running on port 3002) BEFORE building
the training data. Output is consumed by build_agent_sft_v2.py.

Usage:
    cd slurm-agent
    python training/extract_runtime_schemas.py --mcp-url http://localhost:3002 \
        --out training/runtime_schemas.json
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.flow.tool_discovery import discover_tools  # type: ignore


# Handoff tool schemas — these match exactly what the OpenAI Agents SDK
# generates from `_OperatorHandoffPayload` dataclass at runtime.
# (See agent/flow/agent.py: _build_transfer_to_operator_handoff)
HANDOFF_TOOL_SCHEMAS = {
    "transfer_to_operator": {
        "type": "function",
        "function": {
            "name": "transfer_to_operator",
            "description": (
                "Hand off to the Operator to EXECUTE actions that modify the cluster. "
                "Call with structured args: action_request (required imperative action) "
                "required_tool (exact action tool name), targets (optional list of concrete IDs/names), "
                "and target_scope ('explicit', 'discovery', or 'none'). "
                "For job actions with concrete IDs, use target_scope='explicit' and targets=['12345','12346']. "
                "For broad job actions that need Operator resolution, use target_scope='discovery' and empty targets. "
                "For cluster-control actions with no target, use target_scope='none'. "
                "The Operator will call the tools and report results."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action_request": {
                        "type": "string",
                        "description": "Imperative action to perform",
                    },
                    "required_tool": {
                        "type": "string",
                        "description": "Exact action tool name (e.g., scancel, scontrol_node)",
                    },
                    "targets": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Concrete target IDs/names",
                    },
                    "target_scope": {
                        "type": "string",
                        "enum": ["explicit", "discovery", "none"],
                        "description": "Target resolution mode",
                    },
                },
                "required": ["action_request", "required_tool"],
            },
        },
    },
    "transfer_to_observer": {
        "type": "function",
        "function": {
            "name": "transfer_to_observer",
            "description": (
                "Hand back to the Observer ONLY for purely read-only requests "
                "(monitoring, analysis, questions). NEVER use this if the handoff "
                "message asks you to submit, cancel, hold, release, or requeue. "
                "You must call the action tools first."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
}


# Lookup tools added by the agent (not from MCP)
LOCAL_TOOL_SCHEMAS = {
    "lookup_slurm_docs": {
        "type": "function",
        "function": {
            "name": "lookup_slurm_docs",
            "description": "Look up Slurm documentation for a command or concept.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Documentation topic to look up"},
                },
                "required": ["query"],
            },
        },
    },
    "lookup_skill": {
        "type": "function",
        "function": {
            "name": "lookup_skill",
            "description": "Look up a local runbook/workflow/skill guide.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["search", "read"]},
                    "query": {"type": "string"},
                    "skill_name": {"type": "string"},
                },
                "required": ["mode"],
            },
        },
    },
}


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mcp-url", default="http://localhost:3002")
    parser.add_argument("--out", default="training/runtime_schemas.json")
    args = parser.parse_args()

    print(f"Discovering tools from {args.mcp_url}...")
    catalog = await discover_tools(args.mcp_url)

    schemas = {}
    for bucket_name in ("analysis", "safe", "dangerous"):
        bucket = getattr(catalog, bucket_name)
        for tool in bucket:
            schemas[tool.name] = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.schema,
                },
                "_category": bucket_name,
            }

    # Add local + handoff tools
    for name, schema in LOCAL_TOOL_SCHEMAS.items():
        schema_copy = json.loads(json.dumps(schema))
        schema_copy["_category"] = "local"
        schemas[name] = schema_copy

    for name, schema in HANDOFF_TOOL_SCHEMAS.items():
        schema_copy = json.loads(json.dumps(schema))
        schema_copy["_category"] = "handoff"
        schemas[name] = schema_copy

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(schemas, indent=2))

    # Stats
    cats = {}
    for tool_name, schema in schemas.items():
        cat = schema.get("_category", "unknown")
        cats[cat] = cats.get(cat, 0) + 1

    print(f"\n✓ Saved {len(schemas)} tool schemas → {out_path}")
    print(f"  Breakdown: {cats}")
    print(f"\n  Tools: {sorted(schemas.keys())}")


if __name__ == "__main__":
    asyncio.run(main())
