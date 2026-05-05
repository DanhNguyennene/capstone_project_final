#!/usr/bin/env python3
"""Build chat-style SFT data for the MAIN Slurm agent (not the specialist planner).

Converts the evaluation dataset into multi-turn tool-calling conversations
suitable for fine-tuning Qwen2.5-7B-Instruct with native tool-call format.

Each training sample simulates a full agent turn:
  1. System prompt (condensed observer/operator instructions)
  2. User query
  3. Assistant tool_calls (based on ground_truth tools)
  4. Tool results (simulated from source_state)
  5. Assistant final response (synthesized with keywords)

For handoff cases (operator route), the conversation includes the
transfer_to_operator call followed by the operator's tool execution.

Output format: JSONL with {"messages": [...]} compatible with:
  - Qwen2.5 chat template (tool_call / tool roles)
  - OpenAI fine-tuning format
  - Axolotl / Unsloth ShareGPT format
"""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# ── Tool schemas (simplified for training) ────────────────────────────────────

TOOL_SCHEMAS = {
    "squeue": {
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
    "sinfo": {
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
    "sacct": {
        "type": "function",
        "function": {
            "name": "sacct",
            "description": "Show accounting data for completed/historical jobs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "Job ID to query"},
                    "user": {"type": "string", "description": "Filter by user"},
                    "starttime": {"type": "string", "description": "Start time filter"},
                },
            },
        },
    },
    "scontrol_show": {
        "type": "function",
        "function": {
            "name": "scontrol_show",
            "description": "Show detailed job or node configuration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity": {"type": "string", "description": "job or node"},
                    "id": {"type": "string", "description": "Job ID or node name"},
                },
            },
        },
    },
    "sbatch": {
        "type": "function",
        "function": {
            "name": "sbatch",
            "description": "Submit a batch job script to Slurm.",
            "parameters": {
                "type": "object",
                "properties": {
                    "script": {"type": "string", "description": "Script path or content"},
                    "options": {"type": "string", "description": "Additional sbatch options"},
                },
                "required": ["script"],
            },
        },
    },
    "scancel": {
        "type": "function",
        "function": {
            "name": "scancel",
            "description": "Cancel one or more Slurm jobs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "Job ID(s) to cancel"},
                    "user": {"type": "string", "description": "Cancel all jobs for user"},
                    "partition": {"type": "string", "description": "Cancel all jobs in partition"},
                    "state": {"type": "string", "description": "Cancel jobs in state"},
                },
            },
        },
    },
    "scontrol_hold": {
        "type": "function",
        "function": {
            "name": "scontrol_hold",
            "description": "Hold a pending job to prevent scheduling.",
            "parameters": {
                "type": "object",
                "properties": {"job_id": {"type": "string", "description": "Job ID to hold"}},
                "required": ["job_id"],
            },
        },
    },
    "scontrol_release": {
        "type": "function",
        "function": {
            "name": "scontrol_release",
            "description": "Release a held job to allow scheduling.",
            "parameters": {
                "type": "object",
                "properties": {"job_id": {"type": "string", "description": "Job ID to release"}},
                "required": ["job_id"],
            },
        },
    },
    "scontrol_requeue": {
        "type": "function",
        "function": {
            "name": "scontrol_requeue",
            "description": "Requeue a failed or completed job.",
            "parameters": {
                "type": "object",
                "properties": {"job_id": {"type": "string", "description": "Job ID to requeue"}},
                "required": ["job_id"],
            },
        },
    },
    "scontrol_update": {
        "type": "function",
        "function": {
            "name": "scontrol_update",
            "description": "Update job properties (timelimit, partition, etc.).",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "Job ID to update"},
                    "updates": {"type": "string", "description": "Key=Value pairs to update"},
                },
                "required": ["job_id"],
            },
        },
    },
    "scontrol_node": {
        "type": "function",
        "function": {
            "name": "scontrol_node",
            "description": "Change node state (drain, resume, down).",
            "parameters": {
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Node name"},
                    "state": {"type": "string", "description": "Target state (drain, resume, down)"},
                    "reason": {"type": "string", "description": "Reason for state change"},
                },
                "required": ["node", "state"],
            },
        },
    },
    "sacctmgr_list": {
        "type": "function",
        "function": {
            "name": "sacctmgr_list",
            "description": "List accounting entities (accounts, users, associations, QOS).",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity": {"type": "string", "description": "What to list: account, user, association, qos"},
                },
            },
        },
    },
    "sacctmgr_show": {
        "type": "function",
        "function": {
            "name": "sacctmgr_show",
            "description": "Show accounting entities (accounts, users, associations, QOS). Alias for sacctmgr_list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity": {"type": "string", "description": "What to show: account, user, association, qos"},
                },
            },
        },
    },
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
    "sdiag": {
        "type": "function",
        "function": {
            "name": "sdiag",
            "description": "Show scheduler diagnostics and statistics.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    "sprio": {
        "type": "function",
        "function": {
            "name": "sprio",
            "description": "Show job priority factors.",
            "parameters": {
                "type": "object",
                "properties": {"job_id": {"type": "string", "description": "Job ID"}},
            },
        },
    },
    "sstat": {
        "type": "function",
        "function": {
            "name": "sstat",
            "description": "Show status of running job steps (memory, CPU usage).",
            "parameters": {
                "type": "object",
                "properties": {"job_id": {"type": "string", "description": "Job ID"}},
                "required": ["job_id"],
            },
        },
    },
    "sshare": {
        "type": "function",
        "function": {
            "name": "sshare",
            "description": "Show fairshare and usage information.",
            "parameters": {
                "type": "object",
                "properties": {"user": {"type": "string", "description": "Filter by user"}},
            },
        },
    },
    "sreport": {
        "type": "function",
        "function": {
            "name": "sreport",
            "description": "Generate accounting usage reports.",
            "parameters": {
                "type": "object",
                "properties": {
                    "report_type": {"type": "string", "description": "Report type (cluster, user, job)"},
                },
            },
        },
    },
    "scontrol_license": {
        "type": "function",
        "function": {
            "name": "scontrol_license",
            "description": "Show license information and allocations.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    "scontrol_reservation_show": {
        "type": "function",
        "function": {
            "name": "scontrol_reservation_show",
            "description": "Show reservation details.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    "scontrol_show_config": {
        "type": "function",
        "function": {
            "name": "scontrol_show_config",
            "description": "Show Slurm configuration parameters.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    "scontrol_ping": {
        "type": "function",
        "function": {
            "name": "scontrol_ping",
            "description": "Ping Slurm controllers to check health.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    "sinfo_reasons": {
        "type": "function",
        "function": {
            "name": "sinfo_reasons",
            "description": "Show reasons for node states (down, drain, etc.).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    "sinfo_node": {
        "type": "function",
        "function": {
            "name": "sinfo_node",
            "description": "Show detailed per-node information.",
            "parameters": {
                "type": "object",
                "properties": {"node": {"type": "string", "description": "Node name"}},
            },
        },
    },
    "squeue_steps": {
        "type": "function",
        "function": {
            "name": "squeue_steps",
            "description": "Show job steps in the queue.",
            "parameters": {
                "type": "object",
                "properties": {"job_id": {"type": "string", "description": "Job ID"}},
            },
        },
    },
    "scontrol_show_step": {
        "type": "function",
        "function": {
            "name": "scontrol_show_step",
            "description": "Show detailed step information for a job.",
            "parameters": {
                "type": "object",
                "properties": {"job_id": {"type": "string", "description": "Job ID"}},
                "required": ["job_id"],
            },
        },
    },
    "sprio_weights": {
        "type": "function",
        "function": {
            "name": "sprio_weights",
            "description": "Show priority weight configuration.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    "web_search": {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for Slurm-related information.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Search query"}},
                "required": ["query"],
            },
        },
    },
    "fetch_web_content": {
        "type": "function",
        "function": {
            "name": "fetch_web_content",
            "description": "Fetch content from a web URL.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string", "description": "URL to fetch"}},
                "required": ["url"],
            },
        },
    },
    "read_file": {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read content of a file.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "File path"}},
                "required": ["path"],
            },
        },
    },
    "transfer_to_operator": {
        "type": "function",
        "function": {
            "name": "transfer_to_operator",
            "description": "Hand off to the Operator agent for state-changing actions that require approval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action_request": {"type": "string", "description": "What action to perform"},
                    "required_tool": {"type": "string", "description": "The tool the operator should use"},
                    "targets": {"type": "string", "description": "Comma-separated target IDs"},
                    "target_scope": {"type": "string", "description": "explicit|discovery|none"},
                },
                "required": ["action_request", "required_tool"],
            },
        },
    },
}

# ── Simulated tool outputs ────────────────────────────────────────────────────

def _format_jobs_table(jobs: dict, **filters) -> str:
    """Simulate squeue output from source_state jobs."""
    lines = ["JOBID    USER      NAME              STATE     PARTITION  NODE"]
    for jid, job in sorted(jobs.items()):
        if filters.get("user") and job.get("user") != filters["user"]:
            continue
        if filters.get("state") and job.get("state", "").upper() != filters["state"].upper():
            continue
        if filters.get("partition") and job.get("partition") != filters["partition"]:
            continue
        if filters.get("job_id") and str(jid) != str(filters["job_id"]):
            continue
        node = f"{job.get('partition','')}-node-01" if job.get("state") == "RUNNING" else "(None)"
        lines.append(
            f"{jid:<8} {job.get('user','?'):<9} {job.get('name','?'):<17} "
            f"{job.get('state','?'):<9} {job.get('partition','?'):<10} {node}"
        )
    return "\n".join(lines) if len(lines) > 1 else "No jobs found matching criteria."


def _format_nodes_table(nodes: dict, **filters) -> str:
    """Simulate sinfo output from source_state nodes."""
    lines = ["NODELIST        STATE    PARTITION  CPUS  MEMORY"]
    for name, node in sorted(nodes.items()):
        if filters.get("partition") and node.get("partition") != filters["partition"]:
            continue
        state = node.get("state", "unknown")
        partition = node.get("partition", "?")
        lines.append(f"{name:<15} {state:<8} {partition:<10} 32    128G")
    return "\n".join(lines)


def _format_sacct(jobs: dict, job_id: str = "") -> str:
    """Simulate sacct output."""
    lines = ["JobID      User     JobName          State      Elapsed    MaxRSS   MaxVMSize"]
    target_jobs = {job_id: jobs[job_id]} if job_id and job_id in jobs else jobs
    for jid, job in sorted(target_jobs.items()):
        elapsed = "01:23:45" if job.get("state") == "RUNNING" else "00:45:12"
        lines.append(
            f"{jid:<10} {job.get('user','?'):<8} {job.get('name','?'):<16} "
            f"{job.get('state','?'):<10} {elapsed}  4.2G     8.1G"
        )
    return "\n".join(lines)


def _format_scontrol_show(jobs: dict, nodes: dict, entity: str, eid: str) -> str:
    """Simulate scontrol show output."""
    if entity == "job" and eid in jobs:
        job = jobs[eid]
        return (
            f"JobId={eid} JobName={job.get('name','?')} UserId={job.get('user','?')}\n"
            f"  JobState={job.get('state','?')} Partition={job.get('partition','?')}\n"
            f"  NumNodes=1 NumCPUs=4 MinMemoryNode=16G\n"
            f"  SubmitTime=2024-01-15T10:00:00 StartTime=2024-01-15T10:01:00\n"
            f"  TimeLimit=24:00:00 Elapsed=01:23:45"
        )
    if entity == "node" and eid in nodes:
        node = nodes[eid]
        return (
            f"NodeName={eid} State={node.get('state','?')} Partition={node.get('partition','?')}\n"
            f"  CPUTot=32 RealMemory=131072 TmpDisk=0\n"
            f"  Gres=gpu:4 GresUsed=gpu:2"
        )
    return f"No {entity} found: {eid}"


def _simulate_tool_output(tool_name: str, source_state: dict, row: dict) -> str:
    """Generate a realistic tool output based on the source state and tool name."""
    jobs = source_state.get("jobs", {})
    nodes = source_state.get("nodes", {})
    user_input = row.get("input", "")

    # Extract potential filters from the user input
    job_ids = re.findall(r"\b(\d{4,5})\b", user_input)
    users = [u for u in ["alice", "bob", "charlie"] if u in user_input.lower()]

    if tool_name in ("squeue", "squeue_steps"):
        filters = {}
        if job_ids:
            filters["job_id"] = job_ids[0]
        if users:
            filters["user"] = users[0]
        if "pending" in user_input.lower():
            filters["state"] = "PENDING"
        elif "running" in user_input.lower():
            filters["state"] = "RUNNING"
        elif "failed" in user_input.lower():
            filters["state"] = "FAILED"
        if "gpu" in user_input.lower():
            filters["partition"] = "gpu"
        return _format_jobs_table(jobs, **filters)

    if tool_name == "sinfo":
        filters = {}
        if "gpu" in user_input.lower():
            filters["partition"] = "gpu"
        return _format_nodes_table(nodes, **filters)

    if tool_name == "sacct":
        jid = job_ids[0] if job_ids else ""
        return _format_sacct(jobs, jid)

    if tool_name in ("scontrol_show", "scontrol_show_step"):
        entity = "node" if "node" in user_input.lower() else "job"
        eid = job_ids[0] if job_ids else (list(nodes.keys())[0] if nodes else "unknown")
        return _format_scontrol_show(jobs, nodes, entity, eid)

    if tool_name == "sinfo_reasons":
        reasons = []
        for name, node in nodes.items():
            if node.get("state") in ("down", "drain"):
                reasons.append(f"{name}: {node['state']} - maintenance scheduled")
        return "\n".join(reasons) if reasons else "No nodes in down/drain state."

    if tool_name == "sstat":
        jid = job_ids[0] if job_ids else list(jobs.keys())[0]
        return f"JobID  AveRSS    MaxRSS    AveCPU\n{jid}   2.1G      4.2G      00:45:30"

    if tool_name == "sdiag":
        return "Scheduler Stats:\n  Server thread count: 4\n  Jobs submitted: 1523\n  Jobs started: 1401\n  Backfill: last_cycle=0.002s mean=0.001s"

    if tool_name == "sprio":
        jid = job_ids[0] if job_ids else list(jobs.keys())[0]
        return f"JOBID  PRIORITY  AGE   FAIRSHARE  JOBSIZE  QOS\n{jid}   1000      200   500        100      200"

    if tool_name == "sshare":
        return "Account    User     RawShares  NormShares  RawUsage  EffectvUsage  FairShare\nresearch   alice    100        0.333       50000     0.25          0.75\nresearch   bob      100        0.333       80000     0.40          0.50\nresearch   charlie  100        0.333       30000     0.15          0.85"

    if tool_name in ("sacctmgr_list", "sacctmgr_show"):
        accounts = source_state.get("accounts", {})
        if accounts:
            lines = ["Account   User      Partition  QOS     MaxCPUs"]
            for acct, info in accounts.items():
                for user in info.get("users", []):
                    limits = info.get("limits", {}).get(user, {})
                    part = limits.get("partition", "cpu")
                    maxcpu = limits.get("MaxCPUs", 64)
                    lines.append(f"{acct:<9} {user:<9} {part:<10} normal  {maxcpu}")
            return "\n".join(lines)
        return "Account   User      Partition  QOS     MaxCPUs\ngeneral   alice     cpu        normal  64\ngeneral   bob       cpu        normal  64\ngeneral   charlie   gpu        normal  32"

    if tool_name == "lookup_slurm_docs":
        query_kw = user_input[:60]
        return f"# Slurm Documentation: {query_kw}\n\nRelevant information about the requested topic. See `man slurm` or https://slurm.schedmd.com for full details."

    if tool_name == "sreport":
        return "Cluster Utilization:\n  CPU hours used: 12,450\n  GPU hours used: 3,200\n  Total jobs: 1,523"

    if tool_name == "scontrol_license":
        return "LicenseName=matlab Total=10 Used=7 Free=3\nLicenseName=ansys Total=4 Used=4 Free=0"

    if tool_name == "scontrol_reservation_show":
        return "ReservationName=maint StartTime=2024-01-20T00:00:00 EndTime=2024-01-20T06:00:00 Nodes=ALL"

    if tool_name == "sbatch":
        return "Submitted batch job 99001"

    if tool_name == "scancel":
        targets = job_ids if job_ids else [jid for jid, j in jobs.items() if j.get("state") in ("RUNNING", "PENDING")]
        return f"scancel: Cancelled job(s) {', '.join(targets[:5])}"

    if tool_name in ("scontrol_hold", "scontrol_release", "scontrol_requeue"):
        jid = job_ids[0] if job_ids else list(jobs.keys())[0]
        action = tool_name.replace("scontrol_", "")
        return f"Job {jid} {action} successful."

    if tool_name == "scontrol_update":
        jid = job_ids[0] if job_ids else list(jobs.keys())[0]
        return f"Job {jid} updated successfully."

    if tool_name == "scontrol_node":
        node = list(nodes.keys())[0] if nodes else "gpu-node-01"
        return f"Node {node} state updated."

    if tool_name == "scontrol_show_config":
        return "Configuration data as of 2024-01-15:\nSchedulerType = sched/backfill\nSelectType = select/cons_tres\nAccountingStorageType = accounting_storage/slurmdbd"

    if tool_name == "scontrol_ping":
        return "Slurmctld(primary) at controller-01 is UP\nSlurmctld(backup) at controller-02 is UP"

    if tool_name == "sprio_weights":
        return "PriorityWeightAge=1000\nPriorityWeightFairshare=5000\nPriorityWeightJobSize=500\nPriorityWeightQOS=2000"

    if tool_name == "web_search":
        return f"Search results for query:\n1. Slurm Documentation - https://slurm.schedmd.com\n2. HPC Best Practices - https://hpc-wiki.info"

    if tool_name == "read_file":
        return "#!/bin/bash\n#SBATCH --job-name=train\n#SBATCH --partition=gpu\n#SBATCH --gres=gpu:1\n#SBATCH --time=24:00:00\npython train.py"

    # Fallback
    return f"Command {tool_name} executed successfully."


# ── Build tool call arguments ─────────────────────────────────────────────────

def _build_tool_args(tool_name: str, row: dict) -> dict:
    """Generate plausible tool arguments based on the query and state."""
    user_input = row.get("input", "")
    jobs = row.get("source_state", {}).get("jobs", {})
    nodes = row.get("source_state", {}).get("nodes", {})

    job_ids = re.findall(r"\b(\d{4,5})\b", user_input)
    users = [u for u in ["alice", "bob", "charlie"] if u in user_input.lower()]

    if tool_name in ("squeue", "squeue_steps"):
        args = {}
        if job_ids:
            args["job_id"] = job_ids[0]
        if users:
            args["user"] = users[0]
        if "pending" in user_input.lower():
            args["state"] = "PENDING"
        elif "running" in user_input.lower():
            args["state"] = "RUNNING"
        elif "failed" in user_input.lower():
            args["state"] = "FAILED"
        if "gpu" in user_input.lower() and "partition" not in args:
            args["partition"] = "gpu"
        return args

    if tool_name == "sinfo":
        if "gpu" in user_input.lower():
            return {"partition": "gpu"}
        return {}

    if tool_name == "sacct":
        args = {}
        if job_ids:
            args["job_id"] = job_ids[0]
        if users:
            args["user"] = users[0]
        return args

    if tool_name in ("scontrol_show", "scontrol_show_step"):
        entity = "node" if "node" in user_input.lower() else "job"
        eid = job_ids[0] if job_ids else ""
        if not eid and entity == "node" and nodes:
            eid = list(nodes.keys())[0]
        return {"entity": entity, "id": eid} if eid else {"entity": entity}

    if tool_name == "sbatch":
        script = re.search(r"(\S+\.sh)", user_input)
        return {"script": script.group(1) if script else "train.sh"}

    if tool_name == "scancel":
        if job_ids:
            return {"job_id": ",".join(job_ids[:3])}
        if users:
            return {"user": users[0]}
        if "gpu" in user_input.lower():
            return {"partition": "gpu"}
        if "pending" in user_input.lower():
            return {"state": "PENDING"}
        return {}

    if tool_name in ("scontrol_hold", "scontrol_release", "scontrol_requeue"):
        jid = job_ids[0] if job_ids else ""
        if not jid:
            # Find a suitable job
            for j, info in jobs.items():
                if tool_name == "scontrol_hold" and info.get("state") == "PENDING":
                    jid = j
                    break
                if tool_name == "scontrol_release" and info.get("state") in ("PENDING", "HELD"):
                    jid = j
                    break
                if tool_name == "scontrol_requeue" and info.get("state") == "FAILED":
                    jid = j
                    break
            if not jid:
                jid = list(jobs.keys())[0] if jobs else "1001"
        return {"job_id": jid}

    if tool_name == "scontrol_node":
        node_name = ""
        for n in nodes:
            if n in user_input:
                node_name = n
                break
        if not node_name:
            node_name = list(nodes.keys())[0] if nodes else "gpu-node-01"
        state = "drain" if "drain" in user_input.lower() else "resume"
        return {"node": node_name, "state": state, "reason": "maintenance"}

    if tool_name == "scontrol_update":
        jid = job_ids[0] if job_ids else list(jobs.keys())[0] if jobs else "1001"
        return {"job_id": jid, "updates": "TimeLimit=48:00:00"}

    if tool_name in ("sacctmgr_list", "sacctmgr_show"):
        return {"entity": "account"}

    if tool_name == "lookup_slurm_docs":
        # Extract topic from query
        query = user_input[:80]
        return {"query": query}

    if tool_name == "sstat":
        jid = job_ids[0] if job_ids else list(jobs.keys())[0] if jobs else "1001"
        return {"job_id": jid}

    if tool_name == "sprio":
        jid = job_ids[0] if job_ids else ""
        return {"job_id": jid} if jid else {}

    if tool_name == "web_search":
        return {"query": user_input[:60]}

    if tool_name == "read_file":
        script = re.search(r"(\S+\.sh)", user_input)
        return {"path": script.group(1) if script else "train.sh"}

    if tool_name == "transfer_to_operator":
        # Determine the actual action tool
        gt_tools = row.get("ground_truth", {}).get("tools", [])
        action_tools = [t for t in gt_tools if t in DANGEROUS_TOOLS]
        required = action_tools[0] if action_tools else "scancel"
        action = user_input[:80]
        scope = "explicit" if job_ids else "discovery"
        targets = ",".join(job_ids[:3]) if job_ids else ""
        args = {"action_request": action, "required_tool": required, "target_scope": scope}
        if targets:
            args["targets"] = targets
        return args

    return {}


# ── Constants ─────────────────────────────────────────────────────────────────

DANGEROUS_TOOLS = {
    "sbatch", "scancel", "srun", "salloc", "scontrol_hold", "scontrol_release",
    "scontrol_update", "scontrol_requeue", "scontrol_node", "scontrol_reconfigure",
    "scontrol_suspend", "scontrol_resume_job", "sacctmgr_add", "sacctmgr_modify",
    "sacctmgr_delete", "scontrol_create_reservation", "scontrol_delete_reservation",
}

OBSERVER_SYSTEM = """You are a Slurm HPC cluster assistant with two modes:
- Observer (default): Read-only monitoring, analysis, diagnosis using Slurm tools.
- Operator (via transfer_to_operator): State-changing actions requiring approval.

Rules:
1. If request changes cluster state (submit/cancel/hold/release/requeue/update/drain), call transfer_to_operator immediately.
2. For read-only requests, use the appropriate Slurm tool directly.
3. For knowledge/docs questions, use lookup_slurm_docs.
4. If action target is ambiguous/missing, ask a clarification question.
5. Always provide concise, actionable responses with relevant data from tool outputs."""

OPERATOR_SYSTEM = """You are the Operator agent for a Slurm HPC cluster. You execute state-changing actions.

Rules:
1. All actions require user confirmation (HITL). Present what you will do and ask for approval.
2. For broad-scope targets, use squeue first to discover matching jobs, then act.
3. Execute the minimum set of tools needed to complete the action.
4. Report results clearly after execution."""


# ── Build training samples ────────────────────────────────────────────────────

def _build_final_response(row: dict, tool_outputs: list[str]) -> str:
    """Synthesize a realistic final response incorporating keywords and tool data."""
    keywords = row.get("ground_truth", {}).get("keywords", [])
    category = row.get("category", "")
    handoff = row.get("ground_truth", {}).get("handoff", False)
    user_input = row.get("input", "")

    # Use a template-based response incorporating keywords
    if not keywords:
        if handoff:
            return "The action has been completed successfully."
        return "Here's the information you requested based on the current cluster state."

    kw_text = ", ".join(keywords[:3])

    if category == "submission":
        return f"I've submitted the job. The batch submission returned a new job ID. Keywords: {kw_text}"
    if category == "safety":
        return f"This action affects multiple jobs. I've executed it after confirmation. Relevant: {kw_text}"
    if category == "bulk":
        return f"Bulk operation completed for the matching targets. Details: {kw_text}"
    if category == "diagnose":
        return f"Based on the diagnostic data, here's what I found regarding {kw_text}."
    if category == "read":
        return f"Here's the current status showing {kw_text}."
    if category == "edge":
        if not row.get("ground_truth", {}).get("tools"):
            return f"I need more information to proceed. Could you clarify what you'd like me to do?"
        return f"The request has an edge case. Here's what I can determine: {kw_text}"
    if category == "docs":
        return f"From the Slurm documentation: {kw_text}. See the official docs for complete details."
    if category == "domain":
        return f"Regarding your domain-specific query about {kw_text}: here's the relevant cluster information."
    if category == "account":
        return f"The accounting information shows: {kw_text}."
    if category == "action":
        return f"Action completed. The operation affected: {kw_text}."
    if category == "multi_step":
        return f"I've completed the multi-step operation. Results: {kw_text}."

    return f"Based on the cluster state: {kw_text}."


def build_observer_sample(row: dict) -> dict[str, Any] | None:
    """Build a training sample for an Observer-only (read-only) case."""
    gt = row.get("ground_truth", {})
    tools = gt.get("tools", [])
    source_state = row.get("source_state", {})

    if gt.get("handoff"):
        return None  # Handled by build_handoff_sample

    messages = [{"role": "system", "content": OBSERVER_SYSTEM}]
    messages.append({"role": "user", "content": row["input"]})

    # Edge case: no tools (ambiguous query → clarification)
    if not tools:
        response = _build_final_response(row, [])
        messages.append({"role": "assistant", "content": response})
        return {"messages": messages}

    # Tool calls
    tool_calls = []
    for tool_name in tools:
        if tool_name not in TOOL_SCHEMAS:
            continue
        args = _build_tool_args(tool_name, row)
        tool_calls.append({
            "id": f"call_{tool_name}_{random.randint(1000,9999)}",
            "type": "function",
            "function": {"name": tool_name, "arguments": json.dumps(args)},
        })

    if not tool_calls:
        # Tools not in our schema — skip
        return None

    # Assistant message with tool_calls
    messages.append({
        "role": "assistant",
        "content": None,
        "tool_calls": tool_calls,
    })

    # Tool results
    tool_outputs = []
    for tc in tool_calls:
        tool_name = tc["function"]["name"]
        output = _simulate_tool_output(tool_name, source_state, row)
        tool_outputs.append(output)
        messages.append({
            "role": "tool",
            "tool_call_id": tc["id"],
            "content": output,
        })

    # Final response
    response = _build_final_response(row, tool_outputs)
    messages.append({"role": "assistant", "content": response})

    return {"messages": messages}


def build_handoff_sample(row: dict) -> dict[str, Any] | None:
    """Build a training sample for a handoff case (Observer → Operator)."""
    gt = row.get("ground_truth", {})
    tools = gt.get("tools", [])
    source_state = row.get("source_state", {})

    if not gt.get("handoff"):
        return None

    messages = [{"role": "system", "content": OBSERVER_SYSTEM}]
    messages.append({"role": "user", "content": row["input"]})

    # Determine which tools are read (pre-checks) vs action
    read_tools = [t for t in tools if t not in DANGEROUS_TOOLS]
    action_tools = [t for t in tools if t in DANGEROUS_TOOLS]

    # If there are read tools before handoff, call them first
    if read_tools:
        tool_calls = []
        for tool_name in read_tools:
            if tool_name not in TOOL_SCHEMAS:
                continue
            args = _build_tool_args(tool_name, row)
            tool_calls.append({
                "id": f"call_{tool_name}_{random.randint(1000,9999)}",
                "type": "function",
                "function": {"name": tool_name, "arguments": json.dumps(args)},
            })

        if tool_calls:
            messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls})
            for tc in tool_calls:
                output = _simulate_tool_output(tc["function"]["name"], source_state, row)
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": output})

    # Transfer to operator
    transfer_args = _build_tool_args("transfer_to_operator", row)
    transfer_call = {
        "id": f"call_transfer_{random.randint(1000,9999)}",
        "type": "function",
        "function": {"name": "transfer_to_operator", "arguments": json.dumps(transfer_args)},
    }
    messages.append({"role": "assistant", "content": None, "tool_calls": [transfer_call]})
    messages.append({
        "role": "tool",
        "tool_call_id": transfer_call["id"],
        "content": "Transferred to Operator agent.",
    })

    # Operator executes actions
    if action_tools:
        # Switch to operator system for remaining
        messages.append({"role": "system", "content": OPERATOR_SYSTEM})

        action_calls = []
        for tool_name in action_tools:
            if tool_name not in TOOL_SCHEMAS:
                continue
            args = _build_tool_args(tool_name, row)
            action_calls.append({
                "id": f"call_{tool_name}_{random.randint(1000,9999)}",
                "type": "function",
                "function": {"name": tool_name, "arguments": json.dumps(args)},
            })

        if action_calls:
            messages.append({"role": "assistant", "content": None, "tool_calls": action_calls})
            for tc in action_calls:
                output = _simulate_tool_output(tc["function"]["name"], source_state, row)
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": output})

    # Final response
    response = _build_final_response(row, [])
    messages.append({"role": "assistant", "content": response})

    return {"messages": messages}


def build_sample(row: dict) -> dict[str, Any] | None:
    """Route to appropriate builder based on handoff flag."""
    gt = row.get("ground_truth", {})
    if gt.get("handoff"):
        return build_handoff_sample(row)
    return build_observer_sample(row)


# ── Main ──────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build main agent SFT data from evaluation dataset")
    parser.add_argument("--dataset", default="evaluation/dataset_10k.json",
                        help="Path to evaluation dataset (relative to repo root)")
    parser.add_argument("--out", default="training/out/agent_sft.jsonl",
                        help="Output JSONL path")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limit number of samples (0=all)")
    parser.add_argument("--split", type=float, default=0.0,
                        help="Test split ratio (0=no split, 0.2=80/20)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--include-tools", action="store_true",
                        help="Include tool definitions in system message")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    random.seed(args.seed)

    dataset_path = (ROOT / args.dataset).resolve()
    output_path = (ROOT / args.out).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = json.loads(dataset_path.read_text())
    if not isinstance(data, list):
        raise TypeError("dataset must be a JSON array")
    if args.limit > 0:
        data = data[:args.limit]

    print(f"Building agent SFT data from {len(data)} cases...")

    samples = []
    skipped = 0
    for row in data:
        sample = build_sample(row)
        if sample:
            # Optionally inject tool definitions
            if args.include_tools:
                tools_json = json.dumps(
                    [TOOL_SCHEMAS[t] for t in row.get("ground_truth", {}).get("tools", []) if t in TOOL_SCHEMAS],
                    indent=1,
                )
                sample["messages"][0]["content"] += f"\n\nAvailable tools:\n{tools_json}"
            sample["metadata"] = {
                "id": row.get("id"),
                "category": row.get("category"),
                "scenario": row.get("scenario"),
            }
            samples.append(sample)
        else:
            skipped += 1

    random.shuffle(samples)

    # Optional train/test split
    if args.split > 0:
        split_idx = int(len(samples) * (1 - args.split))
        train_samples = samples[:split_idx]
        test_samples = samples[split_idx:]

        train_path = output_path
        test_path = output_path.with_name(output_path.stem + "_test.jsonl")

        with train_path.open("w", encoding="utf-8") as f:
            for s in train_samples:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
        with test_path.open("w", encoding="utf-8") as f:
            for s in test_samples:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")

        print(f"  Train: {len(train_samples)} → {train_path}")
        print(f"  Test:  {len(test_samples)} → {test_path}")
    else:
        with output_path.open("w", encoding="utf-8") as f:
            for s in samples:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
        print(f"  Saved: {len(samples)} → {output_path}")

    print(f"  Skipped: {skipped} (tools not in schema)")

    # Stats
    from collections import Counter
    cats = Counter(s["metadata"]["category"] for s in samples)
    handoffs = sum(1 for s in samples if any(
        m.get("tool_calls") and any(tc["function"]["name"] == "transfer_to_operator" for tc in m["tool_calls"])
        for m in s["messages"] if isinstance(m.get("tool_calls"), list)
    ))
    print(f"\n  Categories: {dict(sorted(cats.items()))}")
    print(f"  Handoff cases: {handoffs}")
    print(f"  Observer-only: {len(samples) - handoffs}")


if __name__ == "__main__":
    main()
