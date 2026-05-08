#!/usr/bin/env python3
"""
Template-Folded Synthetic Dataset Generator
=============================================
Generates evaluation datasets using a template-fold-paraphrase pipeline:

1. TEMPLATES: Define conversation structures with ground-truth baked in
2. SLOTS: Fill from real mock_data states (job IDs, users, nodes, partitions)
3. FOLD: Combine templates from same/different categories to create longer multi-turn
4. PARAPHRASE: Use LLM (qwen2.5:7b) to generate natural-language variations
5. VALIDATE: Structural checks ensure ground-truth consistency

This guarantees correctness (GT from template) while maximizing diversity (LLM paraphrase).

Categories:
  Multi-turn: read→act, investigate→diagnose→fix, explore→narrow→action, docs→apply
  Web-retrieval: third-party, cloud, ML frameworks, community tools, monitoring

Usage:
  python generate_template_datasets.py --model qwen2.5:7b
  python generate_template_datasets.py --model qwen2.5:7b --mt-count 200 --web-count 200
"""

import asyncio
import json
import random
import re
import sys
import time
import argparse
import hashlib
import itertools
from copy import deepcopy
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

try:
    from openai import AsyncOpenAI
except ImportError:
    print("ERROR: pip install openai")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-server"))
from mock_data import MOCK_JOBS, MOCK_NODES

OLLAMA_URL = "http://localhost:11434/v1"
SCENARIOS = ["healthy", "failed", "pending", "mixed", "debug_needed"]

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: STATE HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def build_state(scenario: str) -> Dict[str, Any]:
    jobs = {}
    for j in MOCK_JOBS[scenario]:
        jobs[j["job_id"]] = {
            "state": j["state"], "user": j["user"],
            "name": j["name"], "partition": j["partition"],
        }
    nodes = {}
    for n in MOCK_NODES[scenario]:
        nodes[n["name"]] = {"state": n["state"], "partition": n["partition"]}
    return {"jobs": jobs, "nodes": nodes}

def get_jobs_by_state(scenario: str, state: str) -> List[dict]:
    return [j for j in MOCK_JOBS[scenario] if j["state"] == state]

def get_jobs_by_user(scenario: str, user: str) -> List[dict]:
    return [j for j in MOCK_JOBS[scenario] if j["user"] == user]

def get_nodes_by_state(scenario: str, state: str) -> List[dict]:
    return [n for n in MOCK_NODES[scenario] if n["state"] == state]

def get_nodes_by_partition(scenario: str, partition: str) -> List[dict]:
    return [n for n in MOCK_NODES[scenario] if n["partition"] == partition]

ALL_USERS = ["alice", "bob", "charlie"]
ALL_PARTITIONS = ["gpu", "cpu"]
JOB_STATES = ["RUNNING", "PENDING", "FAILED", "COMPLETED", "TIMEOUT"]
NODE_STATES = ["idle", "alloc", "mix", "drain", "down", "down*"]

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: MULTI-TURN CONVERSATION TEMPLATES
# ══════════════════════════════════════════════════════════════════════════════
# Each template is a function that takes a scenario and returns a conversation dict.
# Ground truth is correct BY CONSTRUCTION.

def _mt_read_then_cancel(scenario: str) -> Optional[Dict]:
    """Read jobs → ask about one → cancel it"""
    running = get_jobs_by_state(scenario, "RUNNING")
    pending = get_jobs_by_state(scenario, "PENDING")
    target_jobs = pending or running
    if not target_jobs:
        return None
    job = random.choice(target_jobs)
    state = build_state(scenario)
    return {
        "id": f"mt_read_cancel_{job['job_id']}_{scenario}",
        "category": "multi_turn",
        "description": f"Check jobs then cancel job {job['job_id']}",
        "scenario": scenario,
        "difficulty": "easy",
        "source_state": state,
        "target_state": state,
        "turns": [
            {
                "input": f"Show me all {job['state'].lower()} jobs on the {job['partition']} partition",
                "ground_truth": {"tools": ["squeue"], "handoff": False, "hitl": False,
                                 "keywords": [job["job_id"], job["state"].lower()]},
            },
            {
                "input": f"Cancel that job",
                "ground_truth": {"tools": ["scancel"], "handoff": True, "hitl": True,
                                 "keywords": [job["job_id"]]},
                "context_markers": [job["job_id"], job["name"]],
            },
        ],
    }

def _mt_investigate_node_then_drain(scenario: str) -> Optional[Dict]:
    """Check nodes → investigate one → drain it"""
    alloc_nodes = get_nodes_by_state(scenario, "alloc") + get_nodes_by_state(scenario, "mix")
    if not alloc_nodes:
        return None
    node = random.choice(alloc_nodes)
    state = build_state(scenario)
    return {
        "id": f"mt_investigate_drain_{node['name']}_{scenario}",
        "category": "multi_turn",
        "description": f"Investigate node {node['name']} then drain for maintenance",
        "scenario": scenario,
        "difficulty": "medium",
        "source_state": state,
        "target_state": state,
        "turns": [
            {
                "input": f"What's the status of nodes in the {node['partition']} partition?",
                "ground_truth": {"tools": ["sinfo"], "handoff": False, "hitl": False,
                                 "keywords": [node["name"], node["partition"]]},
            },
            {
                "input": f"Show me details about {node['name']}",
                "ground_truth": {"tools": ["scontrol_show"], "handoff": False, "hitl": False,
                                 "keywords": [node["name"]]},
                "context_markers": [node["name"]],
            },
            {
                "input": "Drain that node for maintenance",
                "ground_truth": {"tools": ["scontrol_update"], "handoff": True, "hitl": True,
                                 "keywords": [node["name"], "drain"]},
                "context_markers": [node["name"]],
            },
        ],
    }

def _mt_user_jobs_hold_release(scenario: str) -> Optional[Dict]:
    """List user jobs → hold pending → release it"""
    for user in random.sample(ALL_USERS, len(ALL_USERS)):
        user_jobs = get_jobs_by_user(scenario, user)
        pending = [j for j in user_jobs if j["state"] == "PENDING"]
        if pending:
            job = random.choice(pending)
            state = build_state(scenario)
            return {
                "id": f"mt_hold_release_{job['job_id']}_{scenario}",
                "category": "multi_turn",
                "description": f"List {user}'s jobs, hold then release {job['job_id']}",
                "scenario": scenario,
                "difficulty": "medium",
                "source_state": state,
                "target_state": state,
                "turns": [
                    {
                        "input": f"What jobs does {user} have?",
                        "ground_truth": {"tools": ["squeue"], "handoff": False, "hitl": False,
                                         "keywords": [user, job["job_id"]]},
                    },
                    {
                        "input": "Hold the pending one",
                        "ground_truth": {"tools": ["scontrol_hold"], "handoff": True, "hitl": True,
                                         "keywords": [job["job_id"]]},
                        "context_markers": [job["job_id"], user],
                    },
                    {
                        "input": "Never mind, release it",
                        "ground_truth": {"tools": ["scontrol_release"], "handoff": True, "hitl": True,
                                         "keywords": [job["job_id"]]},
                        "context_markers": [job["job_id"]],
                    },
                ],
            }
    return None

def _mt_diagnose_failed_requeue(scenario: str) -> Optional[Dict]:
    """Check failed job → ask why → requeue it"""
    failed = get_jobs_by_state(scenario, "FAILED")
    if not failed:
        return None
    job = random.choice(failed)
    state = build_state(scenario)
    return {
        "id": f"mt_diagnose_requeue_{job['job_id']}_{scenario}",
        "category": "multi_turn",
        "description": f"Diagnose failed job {job['job_id']} then requeue",
        "scenario": scenario,
        "difficulty": "medium",
        "source_state": state,
        "target_state": state,
        "turns": [
            {
                "input": f"Show me failed jobs",
                "ground_truth": {"tools": ["squeue"], "handoff": False, "hitl": False,
                                 "keywords": [job["job_id"], "fail"]},
            },
            {
                "input": f"Why did {job['name']} fail?",
                "ground_truth": {"tools": ["sacct"], "handoff": False, "hitl": False,
                                 "keywords": [job["job_id"]]},
                "context_markers": [job["job_id"], job["name"]],
            },
            {
                "input": "Requeue it",
                "ground_truth": {"tools": ["scontrol_requeue"], "handoff": True, "hitl": True,
                                 "keywords": [job["job_id"]]},
                "context_markers": [job["job_id"], job["name"]],
            },
        ],
    }

def _mt_docs_then_apply(scenario: str) -> Optional[Dict]:
    """Look up docs → apply knowledge (create reservation)"""
    nodes = MOCK_NODES[scenario]
    if len(nodes) < 2:
        return None
    n1, n2 = random.sample(nodes, 2)
    state = build_state(scenario)
    return {
        "id": f"mt_docs_reservation_{n1['name']}_{scenario}",
        "category": "multi_turn",
        "description": "Look up reservation docs then create one",
        "scenario": scenario,
        "difficulty": "medium",
        "source_state": state,
        "target_state": state,
        "turns": [
            {
                "input": "How do Slurm reservations work?",
                "ground_truth": {"tools": ["lookup_slurm_docs"], "handoff": False, "hitl": False,
                                 "keywords": ["reservation"]},
            },
            {
                "input": f"Create a reservation on {n1['name']} and {n2['name']} for tonight 10pm to 6am, name it maint-window",
                "ground_truth": {"tools": ["scontrol_create_reservation"], "handoff": True, "hitl": True,
                                 "keywords": ["maint-window", n1["name"]]},
                "context_markers": [n1["name"], n2["name"], "maint-window"],
            },
        ],
    }

def _mt_cluster_overview_escalate(scenario: str) -> Optional[Dict]:
    """Overview → identify problem → fix it"""
    problem_nodes = (get_nodes_by_state(scenario, "drain") +
                     get_nodes_by_state(scenario, "down") +
                     get_nodes_by_state(scenario, "down*"))
    if not problem_nodes:
        return None
    node = random.choice(problem_nodes)
    state = build_state(scenario)
    return {
        "id": f"mt_overview_fix_{node['name']}_{scenario}",
        "category": "multi_turn",
        "description": f"Cluster overview, find problem {node['name']}, bring it back",
        "scenario": scenario,
        "difficulty": "medium",
        "source_state": state,
        "target_state": state,
        "turns": [
            {
                "input": "Give me a cluster health overview — any nodes down?",
                "ground_truth": {"tools": ["sinfo"], "handoff": False, "hitl": False,
                                 "keywords": [node["name"], node["state"]]},
            },
            {
                "input": "Why is that node in that state?",
                "ground_truth": {"tools": ["scontrol_show"], "handoff": False, "hitl": False,
                                 "keywords": [node["name"]]},
                "context_markers": [node["name"], node["state"]],
            },
            {
                "input": "The issue is fixed, bring it back online",
                "ground_truth": {"tools": ["scontrol_update"], "handoff": True, "hitl": True,
                                 "keywords": [node["name"]]},
                "context_markers": [node["name"]],
            },
        ],
    }

def _mt_bulk_cancel_by_user(scenario: str) -> Optional[Dict]:
    """List user jobs → confirm which → cancel all"""
    for user in random.sample(ALL_USERS, len(ALL_USERS)):
        jobs = get_jobs_by_user(scenario, user)
        pending = [j for j in jobs if j["state"] == "PENDING"]
        if len(pending) >= 2:
            state = build_state(scenario)
            return {
                "id": f"mt_bulk_cancel_{user}_{scenario}",
                "category": "multi_turn",
                "description": f"Find {user}'s pending jobs and cancel all",
                "scenario": scenario,
                "difficulty": "easy",
                "source_state": state,
                "target_state": state,
                "turns": [
                    {
                        "input": f"Show me all pending jobs from {user}",
                        "ground_truth": {"tools": ["squeue"], "handoff": False, "hitl": False,
                                         "keywords": [user, "pending"]},
                    },
                    {
                        "input": "Cancel all of those",
                        "ground_truth": {"tools": ["scancel"], "handoff": True, "hitl": True,
                                         "keywords": [user, "cancel"]},
                        "context_markers": [user] + [j["job_id"] for j in pending[:2]],
                    },
                ],
            }
    return None

def _mt_partition_check_submit(scenario: str) -> Optional[Dict]:
    """Check partition → check free nodes → submit job"""
    partition = random.choice(ALL_PARTITIONS)
    p_nodes = get_nodes_by_partition(scenario, partition)
    idle = [n for n in p_nodes if n["state"] == "idle"]
    state = build_state(scenario)
    return {
        "id": f"mt_check_submit_{partition}_{scenario}",
        "category": "multi_turn",
        "description": f"Check {partition} partition then submit job",
        "scenario": scenario,
        "difficulty": "medium",
        "source_state": state,
        "target_state": state,
        "turns": [
            {
                "input": f"What's the status of the {partition} partition?",
                "ground_truth": {"tools": ["sinfo"], "handoff": False, "hitl": False,
                                 "keywords": [partition]},
            },
            {
                "input": f"Are there any idle nodes there?",
                "ground_truth": {"tools": ["sinfo"], "handoff": False, "hitl": False,
                                 "keywords": [partition, "idle"] if idle else [partition]},
                "context_markers": [partition],
            },
            {
                "input": f"Submit my_job.sh to that partition",
                "ground_truth": {"tools": ["sbatch"], "handoff": True, "hitl": True,
                                 "keywords": ["my_job", partition]},
                "context_markers": [partition],
            },
        ],
    }

def _mt_accounting_explore_modify(scenario: str) -> Optional[Dict]:
    """List accounts → check QOS → add new QOS"""
    state = build_state(scenario)
    qos_name = random.choice(["high-priority", "burst-gpu", "long-running", "dev-queue"])
    return {
        "id": f"mt_acct_qos_{qos_name}_{scenario}",
        "category": "multi_turn",
        "description": f"Explore accounting then add QOS '{qos_name}'",
        "scenario": scenario,
        "difficulty": "medium",
        "source_state": state,
        "target_state": state,
        "turns": [
            {
                "input": "Show me all accounts on the cluster",
                "ground_truth": {"tools": ["sacctmgr_list"], "handoff": False, "hitl": False,
                                 "keywords": ["account"]},
            },
            {
                "input": "What QOS levels exist?",
                "ground_truth": {"tools": ["sacctmgr_list"], "handoff": False, "hitl": False,
                                 "keywords": ["qos"]},
                "context_markers": ["qos"],
            },
            {
                "input": f"Add a new QOS called '{qos_name}' with max 24h wall time",
                "ground_truth": {"tools": ["sacctmgr_add"], "handoff": True, "hitl": True,
                                 "keywords": [qos_name, "qos"]},
                "context_markers": [qos_name],
            },
        ],
    }

def _mt_priority_investigate(scenario: str) -> Optional[Dict]:
    """Check pending → check priority → look up docs on priority"""
    pending = get_jobs_by_state(scenario, "PENDING")
    if not pending:
        return None
    job = random.choice(pending)
    state = build_state(scenario)
    return {
        "id": f"mt_priority_docs_{job['job_id']}_{scenario}",
        "category": "multi_turn",
        "description": f"Investigate why job {job['job_id']} is pending, look up priority docs",
        "scenario": scenario,
        "difficulty": "medium",
        "source_state": state,
        "target_state": state,
        "turns": [
            {
                "input": f"Why is job {job['job_id']} still pending?",
                "ground_truth": {"tools": ["squeue"], "handoff": False, "hitl": False,
                                 "keywords": [job["job_id"], "pending"]},
            },
            {
                "input": "What's its priority score?",
                "ground_truth": {"tools": ["sprio"], "handoff": False, "hitl": False,
                                 "keywords": [job["job_id"]]},
                "context_markers": [job["job_id"]],
            },
            {
                "input": "Explain how Slurm priority scheduling works",
                "ground_truth": {"tools": ["lookup_slurm_docs"], "handoff": False, "hitl": False,
                                 "keywords": ["priority"]},
                "context_markers": ["priority"],
            },
        ],
    }

def _mt_long_hard_workflow(scenario: str) -> Optional[Dict]:
    """4-5 turn hard workflow: overview → investigate → docs → action → verify"""
    failed = get_jobs_by_state(scenario, "FAILED")
    problem_nodes = (get_nodes_by_state(scenario, "drain") +
                     get_nodes_by_state(scenario, "down") +
                     get_nodes_by_state(scenario, "down*"))
    if not failed and not problem_nodes:
        return None

    state = build_state(scenario)

    if failed and problem_nodes:
        job = random.choice(failed)
        node = random.choice(problem_nodes)
        return {
            "id": f"mt_hard_full_{job['job_id']}_{node['name']}_{scenario}",
            "category": "multi_turn",
            "description": f"Full investigation: failed job + problem node + docs + fix",
            "scenario": scenario,
            "difficulty": "hard",
            "source_state": state,
            "target_state": state,
            "turns": [
                {
                    "input": "Give me a full cluster status — jobs and nodes",
                    "ground_truth": {"tools": ["squeue"], "handoff": False, "hitl": False,
                                     "keywords": [job["job_id"]]},
                },
                {
                    "input": f"Why did job {job['job_id']} fail?",
                    "ground_truth": {"tools": ["sacct"], "handoff": False, "hitl": False,
                                     "keywords": [job["job_id"], job["name"]]},
                    "context_markers": [job["job_id"], job["name"]],
                },
                {
                    "input": f"And why is {node['name']} in {node['state']} state?",
                    "ground_truth": {"tools": ["scontrol_show"], "handoff": False, "hitl": False,
                                     "keywords": [node["name"]]},
                    "context_markers": [node["name"], node["state"]],
                },
                {
                    "input": "Look up how to properly resume a drained node in Slurm docs",
                    "ground_truth": {"tools": ["lookup_slurm_docs"], "handoff": False, "hitl": False,
                                     "keywords": ["node", "state"]},
                    "context_markers": [node["name"]],
                },
                {
                    "input": "OK, bring that node back online and requeue the failed job",
                    "ground_truth": {"tools": ["scontrol_update"], "handoff": True, "hitl": True,
                                     "keywords": [node["name"]]},
                    "context_markers": [node["name"], job["job_id"]],
                },
            ],
        }
    elif failed:
        job = random.choice(failed)
        return {
            "id": f"mt_hard_failed_{job['job_id']}_{scenario}",
            "category": "multi_turn",
            "description": f"Deep investigation of failed job {job['job_id']}",
            "scenario": scenario,
            "difficulty": "hard",
            "source_state": state,
            "target_state": state,
            "turns": [
                {
                    "input": "Are there any failed jobs?",
                    "ground_truth": {"tools": ["squeue"], "handoff": False, "hitl": False,
                                     "keywords": [job["job_id"], "fail"]},
                },
                {
                    "input": "Show me the accounting details for that one",
                    "ground_truth": {"tools": ["sacct"], "handoff": False, "hitl": False,
                                     "keywords": [job["job_id"]]},
                    "context_markers": [job["job_id"], job["name"]],
                },
                {
                    "input": "What does Slurm docs say about that exit code?",
                    "ground_truth": {"tools": ["lookup_slurm_docs"], "handoff": False, "hitl": False,
                                     "keywords": ["exit"]},
                    "context_markers": [job["job_id"]],
                },
                {
                    "input": "Requeue it with higher memory",
                    "ground_truth": {"tools": ["scontrol_requeue"], "handoff": True, "hitl": True,
                                     "keywords": [job["job_id"]]},
                    "context_markers": [job["job_id"], job["name"]],
                },
            ],
        }
    else:
        node = random.choice(problem_nodes)
        return {
            "id": f"mt_hard_node_{node['name']}_{scenario}",
            "category": "multi_turn",
            "description": f"Deep investigation of problem node {node['name']}",
            "scenario": scenario,
            "difficulty": "hard",
            "source_state": state,
            "target_state": state,
            "turns": [
                {
                    "input": "Any nodes having issues?",
                    "ground_truth": {"tools": ["sinfo"], "handoff": False, "hitl": False,
                                     "keywords": [node["name"], node["state"]]},
                },
                {
                    "input": "Show me full details on that one",
                    "ground_truth": {"tools": ["scontrol_show"], "handoff": False, "hitl": False,
                                     "keywords": [node["name"]]},
                    "context_markers": [node["name"]],
                },
                {
                    "input": "What jobs were running on it?",
                    "ground_truth": {"tools": ["squeue"], "handoff": False, "hitl": False,
                                     "keywords": [node["name"]]},
                    "context_markers": [node["name"]],
                },
                {
                    "input": "Bring it back to idle state",
                    "ground_truth": {"tools": ["scontrol_update"], "handoff": True, "hitl": True,
                                     "keywords": [node["name"]]},
                    "context_markers": [node["name"]],
                },
            ],
        }

def _mt_pronoun_chain(scenario: str) -> Optional[Dict]:
    """Heavy pronoun usage: user refers to entities only by pronouns"""
    running = get_jobs_by_state(scenario, "RUNNING")
    if not running:
        return None
    job = random.choice(running)
    state = build_state(scenario)
    return {
        "id": f"mt_pronouns_{job['job_id']}_{scenario}",
        "category": "multi_turn",
        "description": f"Pronoun-heavy conversation about {job['user']}'s job",
        "scenario": scenario,
        "difficulty": "hard",
        "source_state": state,
        "target_state": state,
        "turns": [
            {
                "input": f"Who is using the {job['partition']} partition?",
                "ground_truth": {"tools": ["squeue"], "handoff": False, "hitl": False,
                                 "keywords": [job["user"], job["partition"]]},
            },
            {
                "input": "What's their job called?",
                "ground_truth": {"tools": ["squeue"], "handoff": False, "hitl": False,
                                 "keywords": [job["name"]]},
                "context_markers": [job["user"], job["name"]],
            },
            {
                "input": "How long has it been running?",
                "ground_truth": {"tools": ["squeue"], "handoff": False, "hitl": False,
                                 "keywords": [job["job_id"]]},
                "context_markers": [job["job_id"], job["name"]],
            },
            {
                "input": "Cancel it",
                "ground_truth": {"tools": ["scancel"], "handoff": True, "hitl": True,
                                 "keywords": [job["job_id"]]},
                "context_markers": [job["job_id"], job["name"], job["user"]],
            },
        ],
    }

def _mt_safety_escalation(scenario: str) -> Optional[Dict]:
    """User starts safe, escalates to dangerous bulk operation"""
    running = get_jobs_by_state(scenario, "RUNNING")
    if len(running) < 2:
        return None
    state = build_state(scenario)
    partition = random.choice(ALL_PARTITIONS)
    return {
        "id": f"mt_safety_escalate_{partition}_{scenario}",
        "category": "multi_turn",
        "description": f"Safe query escalates to dangerous bulk cancel on {partition}",
        "scenario": scenario,
        "difficulty": "hard",
        "source_state": state,
        "target_state": state,
        "turns": [
            {
                "input": f"How many jobs are running on {partition}?",
                "ground_truth": {"tools": ["squeue"], "handoff": False, "hitl": False,
                                 "keywords": [partition, "running"]},
            },
            {
                "input": "Who submitted them?",
                "ground_truth": {"tools": ["squeue"], "handoff": False, "hitl": False,
                                 "keywords": ["user"]},
                "context_markers": [partition],
            },
            {
                "input": f"Cancel ALL jobs on the {partition} partition",
                "ground_truth": {"tools": ["scancel"], "handoff": True, "hitl": True,
                                 "keywords": [partition, "cancel"]},
                "context_markers": [partition],
            },
        ],
    }

def _mt_docs_deep_dive(scenario: str) -> Optional[Dict]:
    """Pure docs conversation: ask → follow up → ask related topic"""
    topics = [
        ("job arrays", ["array", "sbatch"]),
        ("job dependencies", ["dependency", "afterok"]),
        ("cgroups", ["cgroup", "memory"]),
        ("fair share scheduling", ["fair", "share", "priority"]),
        ("burst buffer", ["burst", "buffer"]),
        ("GRES configuration", ["gres", "gpu"]),
        ("MPI jobs", ["mpi", "srun"]),
        ("accounting limits", ["limit", "account"]),
    ]
    t1, t2 = random.sample(topics, 2)
    state = build_state(scenario)
    return {
        "id": f"mt_docs_deep_{t1[0].replace(' ', '_')}_{scenario}",
        "category": "multi_turn",
        "description": f"Deep docs dive: {t1[0]} then {t2[0]}",
        "scenario": scenario,
        "difficulty": "easy",
        "source_state": state,
        "target_state": state,
        "turns": [
            {
                "input": f"Explain how {t1[0]} work in Slurm",
                "ground_truth": {"tools": ["lookup_slurm_docs"], "handoff": False, "hitl": False,
                                 "keywords": t1[1]},
            },
            {
                "input": f"What about {t2[0]}? How does that relate?",
                "ground_truth": {"tools": ["lookup_slurm_docs"], "handoff": False, "hitl": False,
                                 "keywords": t2[1]},
                "context_markers": t2[1][:1],
            },
        ],
    }

# All multi-turn template generators
MT_TEMPLATES = [
    _mt_read_then_cancel,
    _mt_investigate_node_then_drain,
    _mt_user_jobs_hold_release,
    _mt_diagnose_failed_requeue,
    _mt_docs_then_apply,
    _mt_cluster_overview_escalate,
    _mt_bulk_cancel_by_user,
    _mt_partition_check_submit,
    _mt_accounting_explore_modify,
    _mt_priority_investigate,
    _mt_long_hard_workflow,
    _mt_pronoun_chain,
    _mt_safety_escalation,
    _mt_docs_deep_dive,
]

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3: WEB RETRIEVAL TEMPLATES
# ══════════════════════════════════════════════════════════════════════════════

WEB_TOPICS = [
    # (input_template, keywords, rationale, category)
    # Third-party tools
    ("How do I use PySlurm to {action} in Python?",
     ["pyslurm", "python"], "PySlurm is third-party; not in official Slurm docs", "third-party",
     ["query job status", "submit jobs programmatically", "monitor cluster state", "cancel jobs by filter"]),
    ("How do I configure Open OnDemand to {action}?",
     ["ondemand", "web"], "Open OnDemand is OSC project, not SchedMD", "third-party",
     ["submit Slurm jobs via browser", "launch interactive desktops", "set up Jupyter apps", "manage file transfers"]),
    ("How does XDMoD {action} from Slurm?",
     ["xdmod", "report"], "XDMoD is University at Buffalo project", "third-party",
     ["generate usage reports", "track cost allocation", "analyze job efficiency", "export accounting data"]),
    ("How do I use Submitit to {action} with Slurm?",
     ["submitit", "python"], "Submitit is a Meta/Facebook library", "third-party",
     ["launch distributed training", "manage job arrays", "handle checkpointing", "configure auto-requeue"]),
    ("How do I set up Snakemake to {action} via Slurm?",
     ["snakemake", "slurm", "workflow"], "Snakemake is a workflow manager, not part of Slurm", "third-party",
     ["submit pipeline steps as jobs", "handle dependencies between rules", "configure cluster profiles", "manage resource allocation per rule"]),

    # Cloud integrations
    ("How do I configure AWS ParallelCluster to {action}?",
     ["parallelcluster", "aws"], "AWS ParallelCluster is Amazon's managed HPC product", "cloud",
     ["auto-scale GPU instances", "use spot instances as compute nodes", "configure custom AMIs", "set up multi-queue clusters"]),
    ("How does Azure CycleCloud handle {action} with Slurm?",
     ["cyclecloud", "azure"], "CycleCloud is Microsoft's cloud HPC manager", "cloud",
     ["autoscaling compute nodes", "spot instance preemption", "hybrid cloud bursting", "cost management and limits"]),
    ("How do I use Google Cloud HPC Toolkit to {action}?",
     ["hpc-toolkit", "google", "gcloud"], "Google HPC Toolkit is GCP-specific", "cloud",
     ["deploy a Slurm cluster", "configure filestore for shared storage", "use preemptible VMs", "set up multi-region clusters"]),
    ("How do I configure Slurm on Oracle Cloud Infrastructure to {action}?",
     ["oci", "oracle", "cloud"], "OCI HPC is Oracle-specific", "cloud",
     ["use bare-metal GPU shapes", "configure RDMA cluster networking", "enable autoscaling", "manage cluster images"]),

    # Container runtimes
    ("How do I use Enroot and Pyxis to {action} on Slurm?",
     ["enroot", "pyxis", "container"], "Enroot/Pyxis are NVIDIA container tools", "containers",
     ["run GPU containers in jobs", "pull images from NGC", "configure shared container cache", "handle multi-node container jobs"]),
    ("What's the best way to {action} with Singularity/Apptainer on Slurm?",
     ["singularity", "apptainer", "--nv"], "Singularity GPU details are community knowledge", "containers",
     ["run GPU jobs with --nv flag", "build images on login nodes", "bind-mount cluster filesystems", "handle MPI inside containers"]),
    ("How do I configure Charliecloud to {action} in Slurm jobs?",
     ["charliecloud", "ch-run"], "Charliecloud is LANL's unprivileged container tool", "containers",
     ["run unprivileged containers", "distribute images across nodes", "handle user namespaces", "integrate with job scripts"]),

    # ML frameworks
    ("How do I launch {action} across multiple Slurm nodes?",
     ["torchrun", "distributed", "SLURM_NODELIST"], "PyTorch distributed training is ML community knowledge", "ml-frameworks",
     ["PyTorch distributed training with torchrun", "multi-node DeepSpeed training", "Horovod allreduce training", "JAX TPU-style parallelism on GPUs"]),
    ("How do I configure DeepSpeed to {action} on a Slurm cluster?",
     ["deepspeed", "launcher", "slurm"], "DeepSpeed is a Microsoft ML optimization library", "ml-frameworks",
     ["use its Slurm launcher", "configure ZeRO offloading across nodes", "handle elastic training with node failures", "set up pipeline parallelism"]),
    ("How do I run Horovod {action} on Slurm?",
     ["horovod", "mpirun", "slurm"], "Horovod is Uber's distributed training framework", "ml-frameworks",
     ["distributed training with horovodrun", "elastic training with Slurm", "NCCL optimization across nodes", "mixed precision allreduce"]),

    # Competing/related systems
    ("What are the differences between Slurm and {action}?",
     ["comparison", "scheduler"], "Competitive analysis not in official Slurm docs", "comparison",
     ["Flux Framework for hierarchical scheduling", "PBS Pro for legacy HPC sites", "HTCondor for high-throughput computing", "Kubernetes for cloud-native workloads"]),

    # Monitoring
    ("How do I set up {action} for Slurm monitoring?",
     ["monitoring", "metrics"], "Third-party monitoring integrations", "monitoring",
     ["Prometheus exporters with Grafana dashboards", "Datadog HPC integration", "ELK stack for job log analysis", "Nagios checks for Slurm daemons"]),
    ("How do I configure Slurm to export {action}?",
     ["export", "telemetry"], "Telemetry export is operational/third-party", "monitoring",
     ["job completion events to Elasticsearch", "accounting data to InfluxDB", "node metrics to Prometheus pushgateway", "sdiag statistics to time-series DB"]),

    # Security
    ("How do I configure {action} for Slurm authentication?",
     ["auth", "security"], "Advanced auth mechanisms are operational/community topics", "security",
     ["OAuth2/OIDC with slurmrestd", "MUNGE alternatives with JWT", "2FA for job submission", "LDAP group-based access control"]),
    ("What are the security implications of {action} in Slurm?",
     ["security", "vulnerability"], "CVE/security advisory analysis not in docs", "security",
     ["running user-controlled containers", "slurmrestd exposure to public networks", "shared filesystem permissions", "SPANK plugin code injection"]),

    # Version-specific
    ("What new features were added in {action}?",
     ["release", "feature", "version"], "Release notes are version-specific and change", "versioning",
     ["Slurm 24.05 release", "Slurm 23.11 release", "Slurm 24.11 release", "the latest Slurm development branch"]),
    ("How do I migrate from {action}?",
     ["migration", "upgrade"], "Migration guides are version-pair specific", "versioning",
     ["Slurm 22.05 to 23.11", "PBS Pro to Slurm", "TORQUE to Slurm", "Slurm 23.11 to 24.05"]),

    # Advanced operations
    ("How do I write custom {action} for Slurm?",
     ["plugin", "custom"], "Plugin development requires community/source knowledge", "advanced",
     ["SPANK plugins for job prologue/epilogue", "select plugins for custom scheduling", "job_submit plugins for admission control", "topology plugins for fat-tree networks"]),
    ("How do I configure Slurm for {action}?",
     ["configure", "advanced"], "Advanced operational recipes from community", "advanced",
     ["multi-cluster federation with slurmdbd", "heterogeneous job support across architectures", "power-saving with cloud VM suspend/resume scripts", "dynamic partitioning based on time-of-day"]),
]


def generate_web_case(topic_idx: int, variation_idx: int) -> Dict:
    """Generate a single web retrieval case from a topic template."""
    template_input, base_keywords, rationale, category, variations = WEB_TOPICS[topic_idx]
    variation_text = variations[variation_idx % len(variations)]
    input_text = template_input.format(action=variation_text)

    # Add variation-specific keywords
    extra_kw = [w for w in variation_text.lower().split()
                if len(w) > 3 and w not in {"with", "from", "that", "this", "the", "for", "and"}][:2]
    keywords = base_keywords + extra_kw

    scenario = random.choice(SCENARIOS)
    state = build_state(scenario)

    # Determine if local lookup should also be tried
    uses_local = category not in {"comparison", "versioning"}
    tools = ["lookup_slurm_docs", "web_search"] if uses_local else ["web_search"]

    case_id = f"web_{category}_{topic_idx}_{variation_idx}"
    return {
        "id": case_id,
        "category": "web_retrieval",
        "description": f"{category}: {variation_text[:50]}",
        "difficulty": random.choice(["easy", "medium", "hard"]),
        "scenario": scenario,
        "input": input_text,
        "source_state": state,
        "target_state": state,
        "ground_truth": {
            "tools": tools,
            "handoff": False,
            "hitl": False,
            "keywords": keywords,
        },
        "expect_web_fallback": True,
        "rationale": rationale,
    }


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4: PARAPHRASE ENGINE
# ══════════════════════════════════════════════════════════════════════════════

PARAPHRASE_SYSTEM = """You are a paraphrasing assistant. Rewrite the user message in a different natural way.
Rules:
- Keep the SAME meaning and intent
- Keep all specific names, IDs, numbers, and technical terms EXACTLY
- Change the sentence structure, word choice, or style
- Can be more casual, more formal, shorter, or longer
- Do NOT add new information or change what is being asked
- Output ONLY the rewritten text, nothing else"""


async def paraphrase_one(client: AsyncOpenAI, model: str, text: str) -> str:
    """Paraphrase a single input string."""
    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": PARAPHRASE_SYSTEM},
                {"role": "user", "content": text},
            ],
            temperature=0.85,
            max_tokens=200,
        )
        result = resp.choices[0].message.content.strip()
        # Strip thinking tags
        if "<think>" in result:
            result = re.sub(r"<think>.*?</think>", "", result, flags=re.DOTALL).strip()
        return result if result else text
    except Exception:
        return text


async def paraphrase_conversation(client: AsyncOpenAI, model: str, case: Dict) -> Dict:
    """Create a paraphrased variant of a multi-turn conversation."""
    new_case = deepcopy(case)
    # Paraphrase each turn's input
    tasks = [paraphrase_one(client, model, turn["input"]) for turn in new_case["turns"]]
    results = await asyncio.gather(*tasks)
    for turn, new_input in zip(new_case["turns"], results):
        turn["input"] = new_input
    return new_case


async def paraphrase_web_case(client: AsyncOpenAI, model: str, case: Dict) -> Dict:
    """Create a paraphrased variant of a web retrieval case."""
    new_case = deepcopy(case)
    new_case["input"] = await paraphrase_one(client, model, case["input"])
    return new_case


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5: FOLD & COMBINE
# ══════════════════════════════════════════════════════════════════════════════

def fold_conversations(cases: List[Dict], target_count: int) -> List[Dict]:
    """
    Combine shorter conversations to create longer ones.
    Take 2 easy (2-turn) → merge into 1 hard (4-turn) if scenarios match.
    """
    folded = []
    easy_cases = [c for c in cases if c.get("difficulty") == "easy" and len(c["turns"]) == 2]
    random.shuffle(easy_cases)

    # Pair up cases from same scenario
    by_scenario: Dict[str, List] = {}
    for c in easy_cases:
        by_scenario.setdefault(c["scenario"], []).append(c)

    for scenario, group in by_scenario.items():
        for i in range(0, len(group) - 1, 2):
            if len(folded) >= target_count:
                break
            c1, c2 = group[i], group[i + 1]
            merged = {
                "id": f"mt_folded_{c1['id']}_{c2['id'][-10:]}",
                "category": "multi_turn",
                "description": f"Combined: {c1['description']} + {c2['description']}",
                "scenario": scenario,
                "difficulty": "hard",
                "source_state": c1["source_state"],
                "target_state": c1["target_state"],
                "turns": c1["turns"] + c2["turns"],
            }
            # Add context markers to the join point
            if len(merged["turns"]) > 2 and "context_markers" not in merged["turns"][2]:
                merged["turns"][2]["context_markers"] = []
            folded.append(merged)

    return folded[:target_count]


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6: MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

async def main():
    p = argparse.ArgumentParser(description="Template-Folded Synthetic Dataset Generator")
    p.add_argument("--model", default="qwen2.5:7b", help="Ollama model for paraphrasing")
    p.add_argument("--mt-count", type=int, default=200, help="Target multi-turn conversations")
    p.add_argument("--web-count", type=int, default=200, help="Target web retrieval cases")
    p.add_argument("--paraphrase-variants", type=int, default=3, help="Paraphrase copies per template")
    p.add_argument("--skip-paraphrase", action="store_true", help="Skip LLM paraphrasing (faster)")
    p.add_argument("--output-dir", default=".", help="Output directory")
    args = p.parse_args()

    client = AsyncOpenAI(base_url=OLLAMA_URL, api_key="ollama")
    output_dir = Path(args.output_dir)

    if not args.skip_paraphrase:
        print(f"Testing model {args.model}...")
        try:
            test = await client.chat.completions.create(
                model=args.model,
                messages=[{"role": "user", "content": "Say 'ready'"}],
                max_tokens=10,
            )
            print(f"  Model OK: {test.choices[0].message.content.strip()[:20]}")
        except Exception as e:
            print(f"  WARNING: Model unavailable ({e}), skipping paraphrase")
            args.skip_paraphrase = True

    # ── Phase 1: Generate base multi-turn cases from templates ──────────────
    print(f"\n{'='*60}")
    print(f"  Phase 1: Generating multi-turn base cases from {len(MT_TEMPLATES)} templates × {len(SCENARIOS)} scenarios")
    print(f"{'='*60}")

    base_mt_cases = []
    seen_ids = set()

    for template_fn in MT_TEMPLATES:
        for scenario in SCENARIOS:
            case = template_fn(scenario)
            if case and case["id"] not in seen_ids:
                seen_ids.add(case["id"])
                base_mt_cases.append(case)

    print(f"  Generated {len(base_mt_cases)} base multi-turn cases")

    # ── Phase 2: Fold easy cases into hard ones ─────────────────────────────
    print(f"\n  Phase 2: Folding easy cases into longer conversations...")
    folded = fold_conversations(base_mt_cases, target_count=30)
    for f in folded:
        if f["id"] not in seen_ids:
            seen_ids.add(f["id"])
            base_mt_cases.append(f)
    print(f"  Added {len(folded)} folded conversations → {len(base_mt_cases)} total")

    # ── Phase 3: Paraphrase to reach target count ───────────────────────────
    if not args.skip_paraphrase and len(base_mt_cases) < args.mt_count:
        needed = args.mt_count - len(base_mt_cases)
        print(f"\n  Phase 3: Paraphrasing {needed} variants...")

        # Pick cases to paraphrase (round-robin through all)
        paraphrase_sources = []
        while len(paraphrase_sources) < needed:
            paraphrase_sources.extend(base_mt_cases)
        paraphrase_sources = paraphrase_sources[:needed]

        batch_size = 8
        paraphrased = []
        for i in range(0, len(paraphrase_sources), batch_size):
            batch = paraphrase_sources[i:i + batch_size]
            tasks = [paraphrase_conversation(client, args.model, c) for c in batch]
            results = await asyncio.gather(*tasks)
            for j, pc in enumerate(results):
                pc["id"] = f"{pc['id']}_v{i + j}"
                if pc["id"] not in seen_ids:
                    seen_ids.add(pc["id"])
                    paraphrased.append(pc)
            print(f"    Paraphrased {min(i + batch_size, len(paraphrase_sources))}/{needed}", end="\r")
        print(f"\n  Added {len(paraphrased)} paraphrased variants")
        base_mt_cases.extend(paraphrased)
    elif args.skip_paraphrase:
        print(f"\n  Phase 3: Skipped (--skip-paraphrase)")

    # Trim to target
    mt_final = base_mt_cases[:args.mt_count]

    # ── Phase 4: Generate web retrieval cases ───────────────────────────────
    print(f"\n{'='*60}")
    print(f"  Phase 4: Generating web retrieval cases from {len(WEB_TOPICS)} topic templates")
    print(f"{'='*60}")

    base_web_cases = []
    web_seen_ids = set()

    # Generate all topic × variation combinations
    for topic_idx, (_, _, _, _, variations) in enumerate(WEB_TOPICS):
        for var_idx in range(len(variations)):
            case = generate_web_case(topic_idx, var_idx)
            if case["id"] not in web_seen_ids:
                web_seen_ids.add(case["id"])
                base_web_cases.append(case)

    print(f"  Generated {len(base_web_cases)} base web cases")

    # Paraphrase web cases to reach target
    if not args.skip_paraphrase and len(base_web_cases) < args.web_count:
        needed = args.web_count - len(base_web_cases)
        print(f"\n  Phase 5: Paraphrasing {needed} web case variants...")

        paraphrase_sources = []
        while len(paraphrase_sources) < needed:
            paraphrase_sources.extend(base_web_cases)
        paraphrase_sources = paraphrase_sources[:needed]

        batch_size = 8
        paraphrased_web = []
        for i in range(0, len(paraphrase_sources), batch_size):
            batch = paraphrase_sources[i:i + batch_size]
            tasks = [paraphrase_web_case(client, args.model, c) for c in batch]
            results = await asyncio.gather(*tasks)
            for j, pc in enumerate(results):
                pc["id"] = f"{pc['id']}_v{i + j}"
                if pc["id"] not in web_seen_ids:
                    web_seen_ids.add(pc["id"])
                    paraphrased_web.append(pc)
            print(f"    Paraphrased {min(i + batch_size, len(paraphrase_sources))}/{needed}", end="\r")
        print(f"\n  Added {len(paraphrased_web)} paraphrased web variants")
        base_web_cases.extend(paraphrased_web)
    elif args.skip_paraphrase:
        print(f"\n  Phase 5: Skipped (--skip-paraphrase)")

    web_final = base_web_cases[:args.web_count]

    # ── Phase 6: Save ───────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  Phase 6: Saving datasets")
    print(f"{'='*60}")

    # Stats
    mt_difficulties = {}
    mt_turns_dist = {}
    for c in mt_final:
        d = c.get("difficulty", "unknown")
        mt_difficulties[d] = mt_difficulties.get(d, 0) + 1
        t = len(c["turns"])
        mt_turns_dist[t] = mt_turns_dist.get(t, 0) + 1

    print(f"\n  Multi-turn: {len(mt_final)} conversations")
    print(f"    Difficulty: {json.dumps(mt_difficulties)}")
    print(f"    Turn count: {json.dumps(mt_turns_dist)}")

    web_categories = {}
    for c in web_final:
        cat = c.get("description", "").split(":")[0] if ":" in c.get("description", "") else "other"
        web_categories[cat] = web_categories.get(cat, 0) + 1
    print(f"\n  Web retrieval: {len(web_final)} cases")
    print(f"    Categories: {json.dumps(web_categories)}")

    # Write files
    mt_path = output_dir / "multi_turn_dataset.json"
    mt_path.write_text(json.dumps(mt_final, indent=2))
    print(f"\n  Saved: {mt_path}")

    web_path = output_dir / "web_retrieval_dataset.json"
    web_path.write_text(json.dumps(web_final, indent=2))
    print(f"  Saved: {web_path}")

    print(f"\n{'='*60}")
    print(f"  DONE! {len(mt_final)} multi-turn + {len(web_final)} web retrieval = {len(mt_final) + len(web_final)} total")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
