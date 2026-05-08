#!/usr/bin/env python3
"""Quick diagnostic: does the FT model emit tool_calls with training-style prompts?

Run on the pod:
    python evaluation/test_ft_toolcall.py

Tests the model server directly (bypasses the agent) to isolate whether
the model can generate <tool_call> blocks with the prompts it was trained on.
"""
import json
import requests

MODEL_URL = "http://localhost:9000/v1/chat/completions"

# Exactly the system prompt used during training
OBSERVER_SYSTEM = """You are a Slurm HPC cluster assistant with two modes:
- Observer (default): Read-only monitoring, analysis, diagnosis using Slurm tools.
- Operator (via transfer_to_operator): State-changing actions requiring approval.

Rules:
1. If request changes cluster state (submit/cancel/hold/release/requeue/update/drain), call transfer_to_operator immediately.
2. For read-only requests, use the appropriate Slurm tool directly.
3. For knowledge/docs questions, use lookup_slurm_docs.
4. If action target is ambiguous/missing, ask a clarification question.
5. Always provide concise, actionable responses with relevant data from tool outputs."""

# Simplified tool schemas matching training data
TOOLS_TRAINING = [
    {
        "type": "function",
        "function": {
            "name": "squeue",
            "description": "Show the Slurm job queue. Filter by user, partition, state, or job ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user": {"type": "string", "description": "Filter by username"},
                    "partition": {"type": "string", "description": "Filter by partition"},
                    "state": {"type": "string", "description": "Filter by job state (RUNNING, PENDING, FAILED, etc.)"},
                    "job_id": {"type": "string", "description": "Specific job ID to query"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sinfo",
            "description": "Show cluster node and partition status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "partition": {"type": "string", "description": "Filter by partition"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_to_operator",
            "description": "Hand off to the Operator agent for state-changing actions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string", "description": "Why the handoff is needed"},
                },
            },
        },
    },
]

# Test prompts from the training distribution
TEST_CASES = [
    "Show me the current job queue",
    "What jobs are running right now?",
    "Check the cluster status",
    "Cancel job 12345",
    "Which nodes are available?",
]


def test_model(prompt: str, tools: list, system: str):
    """Send a request to the model and check for tool calls."""
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

    try:
        resp = requests.post(MODEL_URL, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return f"ERROR: {e}"

    choice = data["choices"][0]
    msg = choice["message"]
    tool_calls = msg.get("tool_calls")
    content = msg.get("content")
    finish = choice.get("finish_reason")

    return {
        "has_tool_calls": bool(tool_calls),
        "tool_calls": tool_calls,
        "content_preview": (content or "")[:200],
        "finish_reason": finish,
    }


def main():
    print("=" * 70)
    print("  FT Model Tool-Call Diagnostic")
    print("=" * 70)
    print(f"  Model URL: {MODEL_URL}")
    print(f"  System prompt: TRAINING (short, 5 rules)")
    print(f"  Tools: TRAINING schemas (simplified)")
    print("=" * 70)

    # First test: training prompts + training tools
    print("\n[TEST 1] Training system prompt + Training tool schemas:")
    print("-" * 50)
    for prompt in TEST_CASES:
        result = test_model(prompt, TOOLS_TRAINING, OBSERVER_SYSTEM)
        if isinstance(result, str):
            print(f"  '{prompt}' → {result}")
        else:
            tc_names = [tc["function"]["name"] for tc in (result["tool_calls"] or [])]
            status = "✓ TOOL_CALL" if result["has_tool_calls"] else "✗ NO TOOLS"
            print(f"  '{prompt}'")
            print(f"    {status}: {tc_names or result['content_preview'][:80]}")

    # Second test: NO tools (to see if model generates <tool_call> as raw text)
    print("\n\n[TEST 2] Training system prompt + NO tool schemas:")
    print("-" * 50)
    for prompt in TEST_CASES[:2]:
        result = test_model(prompt, None, OBSERVER_SYSTEM)
        if isinstance(result, str):
            print(f"  '{prompt}' → {result}")
        else:
            print(f"  '{prompt}'")
            print(f"    Content: {result['content_preview'][:120]}")

    # Third test: LONG inference prompt + training tools
    # (to confirm the long prompt breaks things)
    LONG_SYSTEM = "You are a Slurm HPC cluster assistant. You monitor, analyze, and diagnose.\n\nRULE 1 — ACTION ROUTING (MANDATORY):\nIf the request changes cluster state (submit/run/cancel/hold/release/requeue/update/reconfigure/account/node/reservation changes),\nyou MUST transfer_to_operator immediately as your first tool call (no prose first). Do not execute mutating actions in Observer."
    print("\n\n[TEST 3] LONG inference prompt (first 300 chars) + Training tools:")
    print("-" * 50)
    for prompt in TEST_CASES[:2]:
        result = test_model(prompt, TOOLS_TRAINING, LONG_SYSTEM)
        if isinstance(result, str):
            print(f"  '{prompt}' → {result}")
        else:
            tc_names = [tc["function"]["name"] for tc in (result["tool_calls"] or [])]
            status = "✓ TOOL_CALL" if result["has_tool_calls"] else "✗ NO TOOLS"
            print(f"  '{prompt}'")
            print(f"    {status}: {tc_names or result['content_preview'][:80]}")

    print("\n" + "=" * 70)
    print("DIAGNOSIS:")
    print("  If TEST 1 shows ✓ but TEST 3 shows ✗ → system prompt mismatch")
    print("  If TEST 1 shows ✗ → model fundamentally not calling tools")
    print("  If TEST 2 shows <tool_call> in text → serve script parsing issue")
    print("=" * 70)


if __name__ == "__main__":
    main()
