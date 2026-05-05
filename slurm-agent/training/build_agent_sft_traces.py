#!/usr/bin/env python3
"""Build SFT training data from GPT-5-mini traces + synthetic augmentation.

Strategy:
  1. For base train IDs (185/cat) with passing GPT-5-mini traces:
     → Convert real agent traces to chat-format training samples
  2. For augmented variants (swap + paraphrase) without traces:
     → Generate synthetic training data using simulated tool outputs

This ensures the model learns from REAL high-quality agent behavior (GPT-5-mini)
while having enough volume from augmented data for generalization.

Output: training/out/agent_sft.jsonl (chat-format JSONL for QLoRA fine-tuning)
"""

from __future__ import annotations

import argparse
import glob
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# System prompts matching the actual agent
OBSERVER_SYSTEM = """You are a Slurm HPC cluster assistant with two modes:
- Observer (default): Read-only monitoring, analysis, diagnosis using Slurm tools.
- Operator (via transfer_to_operator): State-changing actions requiring approval.

Rules:
1. If request changes cluster state (submit/cancel/hold/release/requeue/update/drain), call transfer_to_operator immediately.
2. For read-only requests, use the appropriate Slurm tool directly.
3. For knowledge/docs questions, use lookup_slurm_docs.
4. If action target is ambiguous/missing, ask a clarification question.
5. Always provide concise, actionable responses with relevant data from tool outputs."""


def load_all_traces(results_dir: Path) -> dict[str, dict]:
    """Load all GPT-5-mini evaluation traces, keeping best score per test_id."""
    all_traces = {}
    for f in sorted(results_dir.glob("eval_all_*.json")):
        try:
            r = json.loads(f.read_text())
            for c in r.get("results", []):
                if c.get("tool_call_history") and c.get("test_id"):
                    tid = c["test_id"]
                    if tid not in all_traces or c.get("overall", 0) > all_traces[tid].get("overall", 0):
                        all_traces[tid] = c
        except Exception:
            pass
    return all_traces


def trace_to_messages(trace: dict) -> list[dict] | None:
    """Convert a GPT-5-mini evaluation trace to chat messages for training.
    
    Returns messages list or None if trace is unsuitable.
    """
    history = trace.get("tool_call_history", [])
    if not history:
        return None

    messages = [{"role": "system", "content": OBSERVER_SYSTEM}]
    messages.append({"role": "user", "content": trace["prompt"]})

    # Parse tool call history into assistant/tool message pairs
    tool_calls_batch = []
    pending_results = []

    i = 0
    while i < len(history):
        entry = history[i]
        entry_type = entry.get("type", "")

        if entry_type == "tool":
            tool_name = entry.get("tool", "")
            cmd = entry.get("cmd", "")
            output = entry.get("output", "")

            # Extract arguments from cmd string like "$ squeue --user alice"
            args = _parse_cmd_args(tool_name, cmd)

            call_id = f"call_{tool_name}_{random.randint(1000, 9999)}"
            tool_calls_batch.append({
                "id": call_id,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(args),
                },
            })

            # Collect the output - might be in this entry or the next "result" entry
            tool_output = output or ""

            # Look ahead for result entries
            j = i + 1
            while j < len(history) and history[j].get("type") == "result":
                result_cmd = history[j].get("cmd", "")
                if result_cmd.startswith("↳ ") or result_cmd.startswith("\u21b3 "):
                    tool_output = result_cmd[2:] if not tool_output else tool_output
                j += 1

            pending_results.append({
                "role": "tool",
                "tool_call_id": call_id,
                "content": tool_output or f"{tool_name} executed.",
            })
            i = j if j > i + 1 else i + 1

        elif entry_type == "handoff":
            # Flush any pending tool calls
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

        elif entry_type == "result":
            # Stray result — skip
            i += 1
        else:
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
    response = trace.get("agent_response", "")
    if response:
        messages.append({"role": "assistant", "content": response})
    else:
        messages.append({"role": "assistant", "content": "Done."})

    # Validate: need at least system + user + assistant
    if len(messages) < 3:
        return None

    return messages


def _parse_cmd_args(tool_name: str, cmd: str) -> dict:
    """Parse command string like '$ squeue --user alice --state PENDING' into args dict."""
    # Remove the "$ tool_name" prefix
    text = cmd.strip()
    if text.startswith("$ "):
        text = text[2:]
    # Remove tool name
    if text.startswith(tool_name):
        text = text[len(tool_name):].strip()

    args = {}

    # Parse --key value pairs
    for m in re.finditer(r"--(\w+)\s+([^\s-]+(?:\s+[^\s-]+)*?)(?=\s+--|$)", text):
        args[m.group(1)] = m.group(2).strip()

    # Parse positional arguments (e.g., "scancel 1001")
    if not args and text.strip():
        # Common patterns
        if tool_name == "scancel":
            job_ids = re.findall(r"\d+", text)
            if job_ids:
                args["job_id"] = ",".join(job_ids)
        elif tool_name in ("scontrol_hold", "scontrol_release", "scontrol_requeue"):
            job_ids = re.findall(r"\d+", text)
            if job_ids:
                args["job_id"] = job_ids[0]
        elif tool_name == "sbatch":
            scripts = re.findall(r"\S+\.sh", text)
            if scripts:
                args["script"] = scripts[0]
        elif tool_name == "lookup_slurm_docs":
            args["query"] = text.strip()

    return args


# ── Synthetic data generation (for augmented variants without traces) ─────────

def _simulate_tool_output(tool_name: str, source_state: dict, row: dict) -> str:
    """Generate simulated tool output from source state."""
    jobs = source_state.get("jobs", {})
    nodes = source_state.get("nodes", {})
    user_input = row.get("input", "")
    job_ids = re.findall(r"\b(\d{4,5})\b", user_input)

    if tool_name in ("squeue", "squeue_steps"):
        lines = ["JOBID    USER      NAME              STATE     PARTITION  NODE"]
        for jid, job in sorted(jobs.items()):
            node = f"{job.get('partition','')}-node-01" if job.get("state") == "RUNNING" else "(None)"
            lines.append(f"{jid:<8} {job.get('user','?'):<9} {job.get('name','?'):<17} "
                        f"{job.get('state','?'):<9} {job.get('partition','?'):<10} {node}")
        return "\n".join(lines) if len(lines) > 1 else "No jobs found."

    if tool_name == "sinfo":
        lines = ["NODELIST        STATE    PARTITION  CPUS  MEMORY"]
        for name, node in sorted(nodes.items()):
            lines.append(f"{name:<15} {node.get('state','?'):<8} {node.get('partition','?'):<10} 32    128G")
        return "\n".join(lines)

    if tool_name == "sacct":
        jid = job_ids[0] if job_ids else ""
        target = {jid: jobs[jid]} if jid and jid in jobs else jobs
        lines = ["JobID      User     State      Elapsed"]
        for j, info in sorted(target.items()):
            lines.append(f"{j:<10} {info.get('user','?'):<8} {info.get('state','?'):<10} 01:23:45")
        return "\n".join(lines)

    if tool_name in ("sacctmgr_list", "sacctmgr_show"):
        return "Account   User      Partition  QOS     MaxCPUs\nresearch  alice     gpu        normal  64\nresearch  bob       cpu        normal  64"

    if tool_name == "lookup_slurm_docs":
        return f"# Slurm Documentation\nRelevant information about: {user_input[:50]}"

    if tool_name == "sbatch":
        return "Submitted batch job 99001"

    if tool_name == "scancel":
        targets = job_ids[:3] if job_ids else list(jobs.keys())[:2]
        return f"Jobs {', '.join(targets)} cancelled successfully."

    if tool_name in ("scontrol_hold", "scontrol_release", "scontrol_requeue"):
        jid = job_ids[0] if job_ids else list(jobs.keys())[0] if jobs else "1001"
        return f"Job {jid} {tool_name.replace('scontrol_', '')} successful."

    if tool_name == "sstat":
        jid = job_ids[0] if job_ids else list(jobs.keys())[0] if jobs else "1001"
        return f"JobID  AveRSS  MaxRSS  AveCPU\n{jid}   2.1G    4.2G    00:45:30"

    if tool_name == "sshare":
        return "Account  User   RawShares  NormShares  FairShare\nresearch alice  100        0.333       0.75"

    if tool_name == "sdiag":
        return "Scheduler Stats:\n  Jobs submitted: 1523\n  Backfill cycles: 450"

    if tool_name == "scontrol_show":
        if job_ids:
            j = jobs.get(job_ids[0], {})
            return f"JobId={job_ids[0]} State={j.get('state','?')} User={j.get('user','?')} Partition={j.get('partition','?')}"
        return "No entity specified."

    if tool_name == "sinfo_reasons":
        reasons = [f"{n}: {nd['state']}" for n, nd in nodes.items() if nd.get("state") in ("down", "drain")]
        return "\n".join(reasons) if reasons else "No down/drain nodes."

    if tool_name == "scontrol_node":
        node = list(nodes.keys())[0] if nodes else "gpu-node-01"
        return f"Node {node} state updated."

    return f"{tool_name} executed successfully."


def _build_tool_args_synthetic(tool_name: str, row: dict) -> dict:
    """Generate tool arguments for synthetic data."""
    user_input = row.get("input", "")
    jobs = row.get("source_state", {}).get("jobs", {})
    job_ids = re.findall(r"\b(\d{4,5})\b", user_input)
    users = [u for u in ["alice", "bob", "charlie"] if u in user_input.lower()]

    if tool_name in ("squeue", "squeue_steps"):
        args = {}
        if job_ids: args["job_id"] = job_ids[0]
        if users: args["user"] = users[0]
        if "pending" in user_input.lower(): args["state"] = "PENDING"
        elif "running" in user_input.lower(): args["state"] = "RUNNING"
        elif "failed" in user_input.lower(): args["state"] = "FAILED"
        if "gpu" in user_input.lower(): args.setdefault("partition", "gpu")
        return args

    if tool_name == "sacct":
        args = {}
        if job_ids: args["job_id"] = job_ids[0]
        if users: args["user"] = users[0]
        return args

    if tool_name == "sbatch":
        script = re.search(r"(\S+\.sh)", user_input)
        return {"script": script.group(1) if script else "train.sh"}

    if tool_name == "scancel":
        if job_ids: return {"job_id": ",".join(job_ids[:3])}
        if users: return {"user": users[0]}
        if "gpu" in user_input.lower(): return {"partition": "gpu"}
        return {}

    if tool_name in ("scontrol_hold", "scontrol_release", "scontrol_requeue"):
        jid = job_ids[0] if job_ids else (list(jobs.keys())[0] if jobs else "1001")
        return {"job_id": jid}

    if tool_name == "lookup_slurm_docs":
        return {"query": user_input[:60]}

    if tool_name == "sstat":
        jid = job_ids[0] if job_ids else (list(jobs.keys())[0] if jobs else "1001")
        return {"job_id": jid}

    return {}


DANGEROUS_TOOLS = {
    "sbatch", "scancel", "srun", "salloc", "scontrol_hold", "scontrol_release",
    "scontrol_update", "scontrol_requeue", "scontrol_node", "scontrol_reconfigure",
    "sacctmgr_add", "sacctmgr_modify", "sacctmgr_delete",
}


def build_synthetic_sample(row: dict) -> dict | None:
    """Build a synthetic training sample for augmented data without real traces."""
    gt = row.get("ground_truth", {})
    tools = gt.get("tools", [])
    source_state = row.get("source_state", {})
    handoff = gt.get("handoff", False)
    keywords = gt.get("keywords", [])

    messages = [{"role": "system", "content": OBSERVER_SYSTEM}]
    messages.append({"role": "user", "content": row["input"]})

    # Edge case: no tools (ambiguous → clarification)
    if not tools:
        messages.append({"role": "assistant", "content": "I need more information. Which specific target would you like me to act on?"})
        return {"messages": messages}

    if handoff:
        # Observer calls transfer_to_operator
        read_tools = [t for t in tools if t not in DANGEROUS_TOOLS]
        action_tools = [t for t in tools if t in DANGEROUS_TOOLS]

        # Optional pre-read
        if read_tools:
            tool_calls = []
            for t in read_tools:
                args = _build_tool_args_synthetic(t, row)
                call_id = f"call_{t}_{random.randint(1000,9999)}"
                tool_calls.append({"id": call_id, "type": "function", "function": {"name": t, "arguments": json.dumps(args)}})
            messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls})
            for tc in tool_calls:
                output = _simulate_tool_output(tc["function"]["name"], source_state, row)
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": output})

        # Transfer
        action_tool = action_tools[0] if action_tools else tools[0]
        transfer_args = {"action_request": row["input"][:80], "required_tool": action_tool, "target_scope": "explicit" if re.findall(r"\d{4,5}", row["input"]) else "discovery"}
        call_id = f"call_transfer_{random.randint(1000,9999)}"
        messages.append({"role": "assistant", "content": None, "tool_calls": [{"id": call_id, "type": "function", "function": {"name": "transfer_to_operator", "arguments": json.dumps(transfer_args)}}]})
        messages.append({"role": "tool", "tool_call_id": call_id, "content": "Transferred to Operator."})

        # Operator executes action
        if action_tools:
            action_calls = []
            for t in action_tools:
                args = _build_tool_args_synthetic(t, row)
                cid = f"call_{t}_{random.randint(1000,9999)}"
                action_calls.append({"id": cid, "type": "function", "function": {"name": t, "arguments": json.dumps(args)}})
            messages.append({"role": "assistant", "content": None, "tool_calls": action_calls})
            for tc in action_calls:
                output = _simulate_tool_output(tc["function"]["name"], source_state, row)
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": output})

        # Response
        kw = ", ".join(keywords[:3]) if keywords else "completed"
        messages.append({"role": "assistant", "content": f"Done. Action completed: {kw}."})

    else:
        # Observer-only: call tools directly
        tool_calls = []
        for t in tools:
            args = _build_tool_args_synthetic(t, row)
            call_id = f"call_{t}_{random.randint(1000,9999)}"
            tool_calls.append({"id": call_id, "type": "function", "function": {"name": t, "arguments": json.dumps(args)}})

        if not tool_calls:
            return None

        messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls})
        for tc in tool_calls:
            output = _simulate_tool_output(tc["function"]["name"], source_state, row)
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": output})

        kw = ", ".join(keywords[:3]) if keywords else "the requested information"
        messages.append({"role": "assistant", "content": f"Based on the cluster data: {kw}."})

    return {"messages": messages}


# ── Main pipeline ─────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Build agent SFT from GPT-5-mini traces + synthetic augmentation")
    p.add_argument("--train-dataset", default="evaluation/dataset_train.json")
    p.add_argument("--results-dir", default="evaluation/results")
    p.add_argument("--out", default="training/out/agent_sft.jsonl")
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def main():
    args = parse_args()
    random.seed(args.seed)

    root = ROOT
    train_data = json.loads((root / args.train_dataset).read_text())
    results_dir = root / args.results_dir
    output_path = root / args.out
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading GPT-5-mini traces from {results_dir}...")
    all_traces = load_all_traces(results_dir)
    passing_traces = {tid: t for tid, t in all_traces.items() if t.get("passed")}
    print(f"  Total traces: {len(all_traces)}, passing: {len(passing_traces)}")

    # Build training samples
    samples = []
    from_traces = 0
    from_synthetic = 0
    skipped = 0

    print(f"\nProcessing {len(train_data)} training cases...")
    for row in train_data:
        test_id = row["id"]

        # Try to use real GPT-5-mini trace
        if test_id in passing_traces:
            messages = trace_to_messages(passing_traces[test_id])
            if messages:
                samples.append({
                    "messages": messages,
                    "metadata": {"id": test_id, "category": row["category"], "scenario": row["scenario"], "source": "gpt5mini_trace"},
                })
                from_traces += 1
                continue

        # Fall back to synthetic
        sample = build_synthetic_sample(row)
        if sample:
            sample["metadata"] = {"id": test_id, "category": row["category"], "scenario": row["scenario"], "source": "synthetic"}
            samples.append(sample)
            from_synthetic += 1
        else:
            skipped += 1

    random.shuffle(samples)

    # Save
    with output_path.open("w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    print(f"\n{'='*60}")
    print(f"  Training Data Summary")
    print(f"{'='*60}")
    print(f"  Total samples:     {len(samples)}")
    print(f"  From GPT-5-mini:   {from_traces} ({100*from_traces/len(samples):.0f}%)")
    print(f"  From synthetic:    {from_synthetic} ({100*from_synthetic/len(samples):.0f}%)")
    print(f"  Skipped:           {skipped}")
    print(f"  Output:            {output_path}")

    cats = Counter(s["metadata"]["category"] for s in samples)
    sources = Counter(s["metadata"]["source"] for s in samples)
    print(f"\n  By category:")
    for cat in sorted(cats):
        trace_n = sum(1 for s in samples if s["metadata"]["category"] == cat and s["metadata"]["source"] == "gpt5mini_trace")
        synth_n = sum(1 for s in samples if s["metadata"]["category"] == cat and s["metadata"]["source"] == "synthetic")
        print(f"    {cat:12}: {cats[cat]:4} (trace={trace_n}, synthetic={synth_n})")


if __name__ == "__main__":
    main()
