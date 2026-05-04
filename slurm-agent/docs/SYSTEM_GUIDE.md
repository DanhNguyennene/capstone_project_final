# Slurm Agent — System Guide

Quick reference for understanding what the agent does, how it is built, and how every tool fits together.

---

## Overview

The Slurm Agent is a conversational HPC assistant that can read cluster state, diagnose problems, generate charts, and perform controlled write actions (job submission, cancellation, holds, etc.).  
It consists of two specialised AI agents connected by an SDK `handoff()` call and exposed through a streaming HTTP API backed by an Ollama LLM.

```
User (browser)
     │  POST /chat  (SSE stream)
     ▼
FastAPI backend  ─────────────────────────────────────────────
     │                                                        │
     ▼                                                 SQLite session store
  Observer Agent  ──[lookup_skill / analysis tools]──────────┘
     │                                                        │
     │  transfer_to_operator()                                │
     ▼                                                        │
  Operator Agent  ──[write tools, needs_approval=True HITL]──┘
     │
     │  transfer_to_observer()  (after first action)
     ▼
  Observer Agent  (confirms / shows updated state)
```

---

## Two-Agent Design

### Observer (entry-point, read-only + analysis)

| What it can do | Tools used |
|---|---|
| Read queue, nodes, history | `squeue`, `sinfo`, `sacct`, `scontrol_show` |
| Scheduler diagnostics | `sdiag`, `sprio`, `sstat` |
| Analyse / diagnose jobs | `diagnose_job`, `run_analysis` (9 script types) |
| Look up workflow guides | `lookup_skill` (17 `.md` guides, loaded lazily) |
| Manage accounts / QoS | `sacctmgr_show`, `sreport` |
| Web search | `web_search` |

Observer calls `transfer_to_operator` when the request needs a write action.  
It **never** calls write tools directly.

### Operator (write actions, gated by HITL)

| What it can do | Tools used |
|---|---|
| Submit jobs | `sbatch`, `srun`, `salloc` |
| Cancel / modify jobs | `scancel`, `scontrol_update`, scontrol_hold/release/requeue |
| Manage scheduler config | `scontrol_create`, `scontrol_delete`, `scontrol_reconfigure` |
| Account management (write) | `sacctmgr_add`, `sacctmgr_modify`, `sacctmgr_delete` |

Every Operator tool has `needs_approval=True`.  
Before the tool executes the browser receives a HITL prompt → user clicks **Approve** or **Reject**.

Operator returns to Observer via `transfer_to_observer` after its first action, so the Observer can confirm with a fresh `squeue`/`sinfo` call.

---

## HITL (Human-in-the-Loop)

```
Operator tries tool call
         │
         ▼
  RunState.needs_approval → interrupt saved to _pending_approvals[session_id]
         │
         ▼
  Frontend shows Approve / Reject buttons
         │
    ┌────┴───────────────┐
    │ approve            │ reject
    ▼                    ▼
  tool executes    tool skipped, explanation returned
```

The `RunState` object is serialised and stored between HTTP requests so the approval decision arrives in the next POST body (`hitl_decision: "approve"|"reject"`).

---

## Tool Reference

### MCP Tools (read-only)

| Tool | What it does |
|---|---|
| `squeue` | List jobs — filter by user, partition, state, job ID |
| `sinfo` | Node and partition status — state, CPU, memory, GRES |
| `sacct` | Historical job accounting — elapsed time, exit codes, resources |
| `scontrol_show` | Raw Slurm record for any job, node, partition, reservation |
| `sdiag` | Scheduler statistics: backfill cycles, RPC throughput, queue depth |
| `sprio` | Composite and per-factor priority for pending jobs |
| `sstat` | Live resource usage for running jobs (CPU%, RSS, IO) |
| `diagnose_job` | Aggregated diagnosis: state + exit code + histogram + interpretation |
| `sacctmgr_show` | Account, user, QoS, and fairshare records |
| `sreport` | Usage summary reports by user, account, cluster, or time window |

### MCP Tools (write) — require HITL

| Tool | What it does |
|---|---|
| `sbatch` | Submit a batch script |
| `srun` | Run an interactive or batch step |
| `salloc` | Allocate resources interactively |
| `scancel` | Cancel one or more jobs |
| `scontrol_update` | Update job attributes (memory, time, CPUs, etc.) |
| `scontrol_hold` | Hold a job (prevent scheduling) |
| `scontrol_release` | Release a held job |
| `scontrol_requeue` | Requeue a failed or cancelled job |
| `scontrol_create` | Create a reservation or partition |
| `scontrol_delete` | Delete a reservation or partition |
| `scontrol_reconfigure` | Signal slurmctld to re-read config |
| `sacctmgr_add` | Add user / account / QoS |
| `sacctmgr_modify` | Modify account/user limits |
| `sacctmgr_delete` | Remove account/user/QoS |

### FunctionTools (built-in, always available)

| Tool | What it does |
|---|---|
| `lookup_skill` | Load a workflow guide by name (lazy — only fetched when needed) |
| `run_analysis` | Run one of 9 Python analysis scripts and return structured results |
| `transfer_to_operator` | Observer → Operator handoff |
| `transfer_to_observer` | Operator → Observer handoff (auto-called after first action) |

#### Analysis script IDs (`run_analysis`)

| Script ID | Purpose |
|---|---|
| `efficiency_report` | Per-job CPU and memory efficiency vs allocation |
| `wait_time_analysis` | Distribution of queue wait times |
| `failure_analysis` | Exit-code frequency and OOM/walltime breakdown |
| `user_usage_summary` | CPU-hours and job counts per user |
| `partition_utilisation` | Utilisation % per partition over time window |
| `job_duration_distribution` | Elapsed time histogram |
| `memory_usage_analysis` | Actual vs requested memory per job |
| `gpu_utilisation` | GPU allocation and efficiency |
| `fairshare_analysis` | Per-user/account fairshare vs raw usage |

---

## Skills (Workflow Guides)

Skills are Markdown knowledge files loaded lazily into the agent's context when it calls `lookup_skill(name)`. Only the skill **names** live in the system prompt to save tokens.

| Skill name | When it helps |
|---|---|
| `cluster_health_check` | Systematic cluster triage checklist |
| `diagnose_failed_job` | Step-by-step failure investigation |
| `exit_codes_reference` | Slurm/Linux exit code meanings |
| `gpu_resources` | GPU allocation patterns and GRES syntax |
| `gpu_utilisation_analysis` | GPU efficiency measurement workflow |
| `investigate_pending_jobs` | PENDING job diagnose checklist |
| `job_arrays` | Array job submission and monitoring |
| `job_dependencies` | afterok/afterany/afternotok patterns |
| `job_efficiency_audit` | CPU/memory efficiency review workflow |
| `memory_management` | OOM diagnosis and memory tuning |
| `mpi_parallel_jobs` | MPI flag selection and debugging |
| `partitions_and_nodes` | Partition selection guide |
| `qos_and_limits` | QoS policy and limit management |
| `sbatch_best_practices` | Script writing conventions |
| `scheduled_jobs` | Scrontab and recurring job setup |
| `user_job_summary` | Per-user accounting queries |
| `walltime_and_checkpointing` | Walltime estimation and checkpoint patterns |

---

## Session Management

- Sessions are stored in **SQLite** (one row per `session_id`), keyed by cookie.
- Each session holds a list of message items (user, assistant, tool calls, tool results).
- When the item count exceeds **50**, `_compact_session()` runs: the LLM summarises the old items in ≤ 300 words, then the session is replaced with `[summary_item] + 20_most_recent_items`.
- The `TodoTracker` generates a 3–5 step plan at the start of each request (lightweight LLM call) and streams progress as `{"type": "todo", "items": [...]}` SSE events.
- Charts generated during a session are de-duplicated before they are replayed into history to avoid context bloat.

---

## Streaming Protocol (SSE)

The `/chat` endpoint streams newline-delimited JSON events:

| `type` field | Meaning |
|---|---|
| `text` | Incremental assistant text token |
| `todo` | Todo plan update `{items: [{id, title, status}]}` |
| `tool_call` | Tool invocation started `{tool, args}` |
| `tool_result` | Tool result returned `{tool, result}` |
| `chart` | Mermaid diagram `{chart_type, mermaid_code}` |
| `hitl` | HITL prompt `{tool, args, description}` — show Approve/Reject |
| `done` | Stream finished |
| `error` | Unrecoverable error `{message}` |

---

## Running the Evaluation

```bash
# Automated 100-test suite (mocked Slurm tools)
cd slurm-agent/evaluation
python run_eval.py

# Real-cluster 100-test suite (requires live slurm-agent + Slurm)
python run_real_slurm_eval.py --base-url http://localhost:8000

# Verify test definitions load
python test_cases.py     # → "Total tests: 100"
```

---

## Adding a New Tool

1. **MCP tool** — add the tool to the MCP server (`mcp_server/`), then list its name in the Observer or Operator tool-set in `agent.py`. Add `needs_approval=True` if it writes.
2. **FunctionTool** — implement in `agent/flow/` and register in the appropriate agent's `tools=` list.
3. **Skill** — drop a `.md` file in `agent/skills/` named `my_skill_name.md`. The `lookup_skill` tool finds it automatically.
4. **Test** — add a `TestCase` to the matching category list in `evaluation/test_cases.py`.
