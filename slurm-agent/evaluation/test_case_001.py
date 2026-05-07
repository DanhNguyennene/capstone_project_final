#!/usr/bin/env python3
"""Test the exact failing case against the model server directly.

Run on pod:
    python evaluation/test_case_001.py
"""
import json
import requests

MODEL_URL = "http://localhost:9000/v1/chat/completions"

OBSERVER_SYSTEM = """You are a Slurm HPC cluster assistant with two modes:
- Observer (default): Read-only monitoring, analysis, diagnosis using Slurm tools.
- Operator (via transfer_to_operator): State-changing actions requiring approval.

Rules:
1. If request changes cluster state (submit/cancel/hold/release/requeue/update/drain), call transfer_to_operator immediately.
2. For read-only requests, use the appropriate Slurm tool directly.
3. For knowledge/docs questions, use lookup_slurm_docs.
4. If action target is ambiguous/missing, ask a clarification question.
5. Always provide concise, actionable responses with relevant data from tool outputs."""

# Observer tools (training schema)
OBSERVER_TOOLS = [
    {"type": "function", "function": {"name": "squeue", "description": "Show the Slurm job queue. Filter by user, partition, state, or job ID.", "parameters": {"type": "object", "properties": {"user": {"type": "string"}, "partition": {"type": "string"}, "state": {"type": "string"}, "job_id": {"type": "string"}}}}},
    {"type": "function", "function": {"name": "sinfo", "description": "Show cluster node and partition status.", "parameters": {"type": "object", "properties": {"partition": {"type": "string"}}}}},
    {"type": "function", "function": {"name": "scontrol_show", "description": "Show detailed job or node configuration.", "parameters": {"type": "object", "properties": {"entity": {"type": "string"}, "id": {"type": "string"}}}}},
    {"type": "function", "function": {"name": "sinfo_reasons", "description": "Show reasons for node states (down, drain, etc.).", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "transfer_to_operator", "description": "Hand off to the Operator agent for state-changing actions that require approval.", "parameters": {"type": "object", "properties": {"action_request": {"type": "string"}, "required_tool": {"type": "string"}, "targets": {"type": "string"}, "target_scope": {"type": "string"}}, "required": ["action_request", "required_tool"]}}},
    {"type": "function", "function": {"name": "lookup_slurm_docs", "description": "Look up Slurm documentation for a command or concept.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
]

def test(prompt, tools, system, label=""):
    payload = {
        "model": "slurm-agent",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "tools": tools,
        "temperature": 0.1,
        "max_tokens": 512,
        "stream": False,
    }
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  Prompt: {prompt}")
    print(f"{'='*60}")
    
    try:
        resp = requests.post(MODEL_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  ERROR: {e}")
        return

    choice = data["choices"][0]
    msg = choice["message"]
    tool_calls = msg.get("tool_calls")
    content = msg.get("content")
    
    print(f"  Finish reason: {choice.get('finish_reason')}")
    print(f"  Tokens: {data.get('usage', {})}")
    if tool_calls:
        print(f"  Tool calls ({len(tool_calls)}):")
        for tc in tool_calls:
            fn = tc["function"]
            print(f"    - {fn['name']}({fn['arguments']})")
    if content:
        print(f"  Content: {content[:300]}")
    if not tool_calls and not content:
        print(f"  [EMPTY RESPONSE]")


# ── THE FAILING TEST CASE ─────────────────────────────────────────────────────
test(
    "Check node gpu-node-01 state, then drain it if hardware errors are present",
    OBSERVER_TOOLS,
    OBSERVER_SYSTEM,
    "CASE 001: multi-step conditional (check then drain)"
)

# ── SIMPLER CASES FOR COMPARISON ──────────────────────────────────────────────
test(
    "Show me all running jobs",
    OBSERVER_TOOLS,
    OBSERVER_SYSTEM,
    "SIMPLE: read-only squeue"
)

test(
    "What is the state of node gpu-node-01?",
    OBSERVER_TOOLS,
    OBSERVER_SYSTEM,
    "SIMPLE: node state check"
)

test(
    "Drain node gpu-node-01 for maintenance",
    OBSERVER_TOOLS,
    OBSERVER_SYSTEM,
    "ACTION: direct drain (should transfer_to_operator)"
)

# ── TEST WHAT AGENT ACTUALLY SENDS (full MCP tools) ──────────────────────────
# Simulate what the agent might be sending (30+ tools with full schemas)
print("\n\n" + "="*60)
print("  Now testing: how many tools does the agent actually send?")
print("="*60)

# Quick check: curl the agent's actual request
import subprocess
result = subprocess.run(
    ["curl", "-s", "http://localhost:8000/health"],
    capture_output=True, text=True
)
print(f"  Agent health: {result.stdout}")
