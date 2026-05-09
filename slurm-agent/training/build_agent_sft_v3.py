#!/usr/bin/env python3
"""Build SFT training data from GPT-5.4 traces (pure distillation + augmentation).

v3 strategy — uses RAW tool_name + tool_args from patched agent traces:
  1. Load GPT-5.4 evaluation results (passed only, from train split)
  2. Convert tool_call_history → chat-format messages with real args
  3. Role-split: Observer-only or Observer+Operator (via transfer_to_operator)
  4. Augment with entity swaps (users, job IDs, partitions)
  5. Validate with _validate_sft.py checks

NO synthetic data. NO regex arg recovery. Only real traces from GPT-5.4.

Output: training/out/agent_sft_v3.jsonl

Usage:
    python training/build_agent_sft_v3.py \\
        --traces evaluation/results/eval_all_gpt-5.4_train_20260509_043944.json \\
        --augment 2 --seed 42
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.flow.instructions import _OBSERVER_BASE, _OPERATOR_BASE  # type: ignore
from training.build_agent_sft import (  # type: ignore
    OBSERVER_TOOL_NAMES,
    OPERATOR_TOOL_NAMES,
    DANGEROUS_TOOLS,
    TOOL_SCHEMAS,
    _role_tools,
)

OBSERVER_SYSTEM = _OBSERVER_BASE
OPERATOR_SYSTEM = _OPERATOR_BASE


# ── Load traces ──────────────────────────────────────────────────────────────

def load_traces(path: Path, passed_only: bool = True) -> list[dict]:
    """Load evaluation results from a single JSON file."""
    data = json.loads(path.read_text())
    results = data.get("results", [])
    if passed_only:
        results = [r for r in results if r.get("passed")]
    return results


# ── Trace → Messages conversion ─────────────────────────────────────────────

def trace_to_messages(trace: dict) -> list[dict] | None:
    """Convert a GPT-5.4 eval trace to chat messages using raw tool_name/tool_args.

    Returns messages list or None if trace is unsuitable.
    """
    history = trace.get("tool_call_history", [])
    prompt = trace.get("prompt", "")
    response = trace.get("agent_response", "")

    if not prompt:
        return None

    messages: list[dict] = [
        {"role": "system", "content": OBSERVER_SYSTEM},
        {"role": "user", "content": prompt},
    ]

    # No tool calls → pure text response (clarification/edge/docs-only)
    if not history or not any(e.get("type") == "tool" for e in history):
        if response:
            messages.append({"role": "assistant", "content": response})
            return messages
        return None

    # Process tool call history into assistant/tool message pairs
    tool_calls_batch: list[dict] = []
    # All known tools across both roles
    ALL_KNOWN_TOOLS = OBSERVER_TOOL_NAMES | OPERATOR_TOOL_NAMES

    pending_results: list[dict] = []
    call_counter = 0

    i = 0
    while i < len(history):
        entry = history[i]
        entry_type = entry.get("type", "")

        if entry_type == "tool":
            # Prefer raw tool_name/tool_args, fall back to normalized
            tool_name = entry.get("tool_name") or entry.get("tool", "")
            tool_args = entry.get("tool_args")
            if tool_args is None:
                tool_args = {}

            # Skip tools not in our schema (GPT hallucinated tool names)
            if tool_name not in ALL_KNOWN_TOOLS:
                i += 1
                # Skip subsequent result entries for this tool
                while i < len(history) and history[i].get("type") == "result":
                    i += 1
                continue

            call_counter += 1
            call_id = f"call_{tool_name}_{call_counter}"

            tool_calls_batch.append({
                "id": call_id,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(tool_args, ensure_ascii=False),
                },
            })

            # Collect tool output from this entry or subsequent result entries
            tool_output = entry.get("output", "")
            j = i + 1
            while j < len(history) and history[j].get("type") == "result":
                result_cmd = history[j].get("cmd", "")
                # Result entries with "↳" prefix contain tool output
                if result_cmd.startswith("↳ ") or result_cmd.startswith("\u21b3 "):
                    if not tool_output:
                        tool_output = result_cmd[2:]
                j += 1

            pending_results.append({
                "role": "tool",
                "tool_call_id": call_id,
                "content": tool_output or f"{tool_name} executed successfully.",
            })
            i = j if j > i + 1 else i + 1

        elif entry_type == "handoff":
            # Flush pending tool calls before the handoff
            if tool_calls_batch:
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": tool_calls_batch,
                })
                messages.extend(pending_results)
                tool_calls_batch = []
                pending_results = []
            i += 1

        elif entry_type == "approved":
            # HITL approval — skip (approval flow is handled at inference)
            i += 1

        else:
            # result, retry, etc — skip
            i += 1

    # Flush remaining tool calls
    if tool_calls_batch:
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": tool_calls_batch,
        })
        messages.extend(pending_results)

    # Add final response
    if response:
        messages.append({"role": "assistant", "content": response})
    else:
        messages.append({"role": "assistant", "content": "Done."})

    # Need at least system + user + one assistant
    if len(messages) < 3:
        return None

    return messages


# ── Role splitting ───────────────────────────────────────────────────────────

def split_by_role(messages: list[dict]) -> list[tuple[str, list[dict]]]:
    """Split a conversation into Observer and Operator samples.

    If transfer_to_operator is called, everything before (inclusive) becomes
    the Observer sample, and the action tool calls after become the Operator sample.
    """
    # Find transfer_to_operator
    transfer_idx = -1
    transfer_args: dict = {}
    for i, m in enumerate(messages):
        if m.get("role") == "assistant" and m.get("tool_calls"):
            for tc in m["tool_calls"]:
                if tc.get("function", {}).get("name") == "transfer_to_operator":
                    transfer_idx = i
                    try:
                        transfer_args = json.loads(tc["function"].get("arguments", "{}"))
                    except Exception:
                        transfer_args = {}
                    break
            if transfer_idx >= 0:
                break

    if transfer_idx < 0:
        # Pure Observer trace — ensure ends with assistant
        if messages[-1]["role"] != "assistant":
            messages.append({"role": "assistant", "content": "Done."})
        return [("observer", messages)]

    # Observer half: everything up to and including the transfer call + tool results
    obs = list(messages[:transfer_idx + 1])
    # Include tool results that match tool_calls in the transfer message
    transfer_msg = messages[transfer_idx]
    obs_call_ids = set()
    if transfer_msg.get("tool_calls"):
        obs_call_ids = {tc["id"] for tc in transfer_msg["tool_calls"]}
    j = transfer_idx + 1
    while j < len(messages) and messages[j].get("role") == "tool":
        if messages[j].get("tool_call_id") in obs_call_ids:
            obs.append(messages[j])
        j += 1
    # Observer must end with assistant
    if obs[-1]["role"] != "assistant":
        obs.append({"role": "assistant", "content": "Handing off to operator for execution."})

    # Operator half: remaining tool calls and final response
    op_start = j  # skip past transfer message's tool responses

    op_tail = []
    k = op_start
    while k < len(messages):
        m = messages[k]
        # Drop any transfer_to_operator calls (keep other tools)
        if m.get("role") == "assistant" and m.get("tool_calls"):
            kept = [tc for tc in m["tool_calls"]
                    if tc.get("function", {}).get("name") != "transfer_to_operator"]
            dropped_ids = {tc["id"] for tc in m["tool_calls"]
                          if tc.get("function", {}).get("name") == "transfer_to_operator"}
            if kept:
                op_tail.append({**m, "tool_calls": kept})
                kept_ids = {tc["id"] for tc in kept}
                n = k + 1
                while n < len(messages) and messages[n].get("role") == "tool":
                    tcid = messages[n].get("tool_call_id")
                    if tcid in kept_ids:
                        op_tail.append(messages[n])
                    # Skip orphaned transfer_to_operator responses
                    n += 1
                k = n
                continue
            else:
                # All calls were transfer_to_operator — skip this message + its tool responses
                n = k + 1
                while n < len(messages) and messages[n].get("role") == "tool":
                    n += 1
                k = n
                continue
        elif m.get("role") == "tool":
            # Skip orphaned tool responses (from transfer_to_operator calls we already processed)
            k += 1
            continue
        else:
            op_tail.append(m)
        k += 1

    # Did operator actually do anything?
    has_action = any(m.get("role") == "assistant" and m.get("tool_calls") for m in op_tail)
    if not has_action and not any(m.get("role") == "assistant" and m.get("content") for m in op_tail):
        return [("observer", obs)]

    # Build operator user message (mirrors agent._operator_handoff_input_filter)
    user_query = next((m["content"] for m in messages if m.get("role") == "user"), "")
    action_request = transfer_args.get("action_request", user_query[:120])
    target_scope = transfer_args.get("target_scope", "discovery")
    required_tool = transfer_args.get("required_tool", "")
    targets = transfer_args.get("targets", []) or []

    op_user_lines = [
        "Execute this exact cluster-state action now.",
        "Do not substitute a different action type.",
        f"Action request: {action_request}",
        f"Target scope: {target_scope}",
    ]
    if required_tool:
        op_user_lines.append(f"Required tool: {required_tool}")
    if targets:
        op_user_lines.append(f"Targets: {', '.join(str(t) for t in targets)}")
    if target_scope == "discovery":
        op_user_lines.append(
            "IMPORTANT: Your FIRST tool call must be a read tool (squeue/sinfo/scontrol_show) to resolve concrete numeric IDs."
        )
        op_user_lines.append(
            "NEVER call the action tool with placeholder IDs like 0, ALL, or flags."
        )
        if required_tool:
            op_user_lines.append(f"Only after discovery, call {required_tool} with the resolved IDs.")
    elif required_tool:
        op_user_lines.append(f"First action tool call MUST use {required_tool}.")

    op_messages = [
        {"role": "system", "content": OPERATOR_SYSTEM},
        {"role": "user", "content": "\n".join(op_user_lines)},
        *op_tail,
    ]
    # Operator must end with assistant
    if op_messages[-1]["role"] != "assistant":
        op_messages.append({"role": "assistant", "content": "Done."})

    return [("observer", obs), ("operator", op_messages)]


# ── Augmentation ─────────────────────────────────────────────────────────────

SWAP_USERS = ["alice", "bob", "charlie", "dave", "eve", "frank", "grace", "henry"]
SWAP_PARTITIONS = ["gpu", "cpu", "debug", "batch", "high-mem", "short", "long", "a100"]


def augment_messages(messages: list[dict], rng: random.Random) -> list[dict] | None:
    """Create an augmented variant by swapping entity names."""
    full_text = json.dumps(messages).lower()
    found_users = [u for u in SWAP_USERS if u in full_text]
    found_partitions = [p for p in SWAP_PARTITIONS if p in full_text]

    if not found_users and not found_partitions:
        return None

    user_pool = list(SWAP_USERS)
    rng.shuffle(user_pool)
    partition_pool = list(SWAP_PARTITIONS)
    rng.shuffle(partition_pool)

    user_map = {}
    for i, u in enumerate(found_users):
        target = user_pool[(i + 1) % len(user_pool)]
        if target != u:
            user_map[u] = target

    partition_map = {}
    for i, p in enumerate(found_partitions):
        target = partition_pool[(i + 1) % len(partition_pool)]
        if target != p:
            partition_map[p] = target

    job_offset = rng.randint(100, 9000)

    if not user_map and not partition_map:
        return None

    def _swap(text: str) -> str:
        for old, new in user_map.items():
            text = re.sub(re.escape(old), new, text, flags=re.IGNORECASE)
        for old, new in partition_map.items():
            text = re.sub(re.escape(old), new, text, flags=re.IGNORECASE)
        text = re.sub(r'\b(\d{4,5})\b', lambda m: str(int(m.group(1)) + job_offset), text)
        return text

    augmented = []
    for msg in messages:
        new_msg = dict(msg)
        if new_msg.get("content"):
            new_msg["content"] = _swap(new_msg["content"])
        if new_msg.get("tool_calls"):
            new_tcs = []
            for tc in new_msg["tool_calls"]:
                new_tc = dict(tc)
                if "function" in new_tc:
                    func = dict(new_tc["function"])
                    func["arguments"] = _swap(func.get("arguments", "{}"))
                    new_tc["function"] = func
                new_tcs.append(new_tc)
            new_msg["tool_calls"] = new_tcs
        augmented.append(new_msg)

    return augmented


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Build SFT data from GPT-5.4 traces (v3 distillation)")
    p.add_argument("--traces", required=True,
                   help="Path to GPT-5.4 eval result JSON")
    p.add_argument("--out", default="training/out/agent_sft_v3.jsonl")
    p.add_argument("--augment", type=int, default=2,
                   help="Augmented variants per trace (0=none)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--passed-only", action="store_true", default=True,
                   help="Only use passed traces (default: True)")
    args = p.parse_args()

    rng = random.Random(args.seed)
    trace_path = ROOT / args.traces
    output_path = ROOT / args.out
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading traces from {trace_path}...")
    traces = load_traces(trace_path, passed_only=args.passed_only)
    print(f"  Loaded: {len(traces)} traces")

    # Convert traces → samples
    samples: list[dict] = []
    stats = Counter()
    skipped_reasons: Counter = Counter()

    for trace in traces:
        tid = trace.get("test_id", "?")
        messages = trace_to_messages(trace)

        if not messages:
            stats["skipped"] += 1
            skipped_reasons["no_messages"] += 1
            continue

        # Role-split
        for role, role_msgs in split_by_role(messages):
            if not role_msgs or len(role_msgs) < 2:
                continue
            samples.append({
                "messages": role_msgs,
                "tools": _role_tools(role),
                "test_id": f"{tid}_{role}",
                "source": "gpt54_trace",
                "role": role,
                "category": trace.get("category", ""),
            })
            stats[f"base_{role}"] += 1

    base_count = len(samples)
    print(f"  Base samples: {base_count}")
    print(f"    Observer: {stats['base_observer']}")
    print(f"    Operator: {stats['base_operator']}")
    print(f"    Skipped:  {stats['skipped']}")
    if skipped_reasons:
        for reason, count in skipped_reasons.most_common():
            print(f"      {reason}: {count}")

    # Augment
    aug_count = 0
    if args.augment > 0:
        print(f"\nAugmenting ({args.augment}x per sample)...")
        base_samples = list(samples)
        for s in base_samples:
            for i in range(args.augment):
                aug_msgs = augment_messages(s["messages"], rng)
                if aug_msgs:
                    samples.append({
                        "messages": aug_msgs,
                        "tools": s.get("tools", []),
                        "test_id": s["test_id"] + f"_aug{i}",
                        "source": "augmented",
                        "role": s.get("role", "observer"),
                        "category": s.get("category", ""),
                    })
                    aug_count += 1

    rng.shuffle(samples)

    # Save
    with output_path.open("w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    total = len(samples)
    print(f"\n{'='*60}")
    print(f"  SFT v3 Training Data Summary")
    print(f"{'='*60}")
    print(f"  Source:              GPT-5.4 traces")
    print(f"  Base (real traces):  {base_count}")
    print(f"  Augmented:           {aug_count}")
    print(f"  Total samples:       {total}")
    print(f"  Output:              {output_path}")
    print(f"{'='*60}")
    print(f"\nNext: validate with  python training/_validate_sft.py {output_path}")


if __name__ == "__main__":
    main()
