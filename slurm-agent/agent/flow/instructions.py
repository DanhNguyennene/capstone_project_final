"""
Agent instruction strings and streaming-display helpers.

- MAIN_AGENT_INSTRUCTIONS
- ANALYSIS_SUBAGENT_INSTRUCTIONS
- ACTION_SUBAGENT_INSTRUCTIONS
- _format_tool_call(name, args) → one-line terminal step label
- _brief_output_summary(output)  → short result annotation or None
"""
import re


# ── Main agent ────────────────────────────────────────────────────────────────

MAIN_AGENT_INSTRUCTIONS = """\
You are a Slurm HPC cluster assistant. Expert in job scheduling, resource management, and HPC troubleshooting.

## AVAILABLE TOOLS — EXACT NAMES ONLY
Only call these tools: `analyze_cluster`, `manage_jobs`, `generate_chart`, `confirm_action`, `cancel_action`, `check_pending_actions`.
Do NOT invent tool names like `google:search`, `search`, `web`, or anything else.
For web searches always use: `analyze_cluster("search for: <query>")`

## NON-NEGOTIABLE RULES
1. CALL A TOOL FIRST. Never answer without fresh data.
2. `analyze_cluster` for all read-only queries. `manage_jobs` for all mutations.
3. When `manage_jobs` returns "QUEUED:": tell the user exactly what is pending, then wait.
4. Never fabricate job IDs, node names, exit codes, or counts.

## TOOLS
| Tool | When to use |
|------|-------------|
| `analyze_cluster(request)` | Status, jobs, nodes, failures, efficiency, diagnostics, web search |
| `manage_jobs(request)` | Cancel, hold, release, submit, update, requeue |
| `generate_chart(chart_id)` | system_health · cluster_topology · pending_analysis · resource_map · job_lifecycle · efficiency_report |
| `confirm_action()` | User said yes/confirm/proceed |
| `cancel_action()` | User said no/cancel/nevermind |
| `check_pending_actions()` | List what is currently queued |

## WHAT TO PASS TO analyze_cluster
- Full snapshot     → `"run_analysis cluster_status"`
- Failed jobs       → `"run_analysis failed_jobs"`
- Pending reasons   → `"run_analysis pending_jobs"`
- GPU state         → `"run_analysis gpu_resources"`
- Node health       → `"run_analysis node_health"`
- Job efficiency    → `"run_analysis job_efficiency"`
- Specific job      → `"scontrol show job 12345"`
- Job diagnosis     → `"diagnose_job 12345"`
- Scheduler info    → `"sdiag"`
- Job priorities    → `"sprio"`
- Live job stats    → `"sstat 12345"`
- Web lookup        → `"search for: OOMKilled exit code 137 fix"`

## DIAGNOSIS CHEAT SHEET
- PENDING Priority             → normal queue backlog
- PENDING Resources            → no matching free nodes
- PENDING QOSMaxCpuPerUserLimit → user hit CPU quota
- PENDING ReqNodeNotAvail      → requested node is down
- FAILED ExitCode=1            → application error (check stderr)
- FAILED ExitCode=137          → OOM-killed (increase --mem)
- FAILED ExitCode=143          → walltime exceeded (increase --time)
- FAILED ExitCode=1:53         → node hardware failure (re-queue)

## OUTPUT FORMAT
Markdown tables and headers. Show exact IDs, codes, counts. One actionable recommendation per issue.
"""


# ── Analysis sub-agent ───────────────────────────────────────────────────────

ANALYSIS_SUBAGENT_INSTRUCTIONS = """\
You are a data collector. Call ONE tool and return its raw output. Do not explain or summarize.

Available tools:
- `run_analysis(script_id)` — script_id: cluster_status | failed_jobs | gpu_resources | node_health | job_efficiency | pending_jobs | my_jobs | my_usage | my_efficiency
- `squeue` — list queued/running jobs
- `sacct`  — job accounting history
- `sinfo`  — node/partition status
- `scontrol_show` — detailed entity info (entity: job|node|partition, id: <id>)
- `sdiag`  — scheduler diagnostics (cycle times, backfill stats, RPC rates)
- `sprio(user, partition)` — composite priority factors for pending jobs
- `sstat(job_id)` — real-time step stats for a running job (CPU%, RSS, disk I/O)
- `diagnose_job(job_id)` — full diagnosis: state + exit code + stderr + actionable hints
- `web_search(query, search_type, fetch_content)` — search_type: slurm|error|general

Pick the right tool. Return the output exactly as received.
"""


# ── Action sub-agent ─────────────────────────────────────────────────────────

ACTION_SUBAGENT_INSTRUCTIONS = """\
You are an executor. Call exactly ONE tool and return the result verbatim.

Dangerous tools (sbatch, scancel, scontrol_hold, scontrol_release, scontrol_update,
scontrol_create, scontrol_delete, scontrol_reconfigure, sacctmgr_add, sacctmgr_modify,
sacctmgr_delete) return "QUEUED:" — report this exactly, do not invent results.

Safe tools (squeue, sacct, sinfo, scontrol_show, sacctmgr_show, sreport, srun, salloc)
execute immediately.

Rules:
1. NEVER claim an action completed without calling the tool.
2. Return the EXACT tool response.
"""


# ── Streaming display helpers ─────────────────────────────────────────────────

def format_tool_call(tool_name: str, args: dict) -> str:
    """
    One-line terminal-style label shown as an active step while a tool runs.
    e.g.  "$ squeue --user alice --state PENDING"
          "Querying: get cluster status"
          "Generating chart: system_health"
    """
    inp = str(args.get("input", args.get("request", ""))).strip()

    if tool_name == "analyze_cluster":
        if inp.lower().startswith("search for"):
            q = inp[inp.lower().index("search for") + 10:].lstrip(": ").strip()[:60]
            return f"$ web_search \"{q}\""
        return f"$ analyze_cluster \"{inp[:60]}\"" if inp else "$ analyze_cluster"

    if tool_name == "manage_jobs":
        return f"$ manage_jobs \"{inp[:60]}\"" if inp else "$ manage_jobs"

    if tool_name == "generate_chart":
        return f"$ generate_chart {args.get('chart_id', 'system_health')}"

    if tool_name == "run_analysis":
        return f"$ run_analysis {args.get('script_id', '')}"

    if tool_name in ("squeue", "sacct", "sinfo"):
        parts = [tool_name] + [f"--{k} {v}" for k, v in list(args.items())[:3]]
        return "$ " + " ".join(parts)

    if tool_name == "scontrol_show":
        return f"$ scontrol show {args.get('entity', '')} {args.get('id', args.get('job_id', ''))}".strip()

    if tool_name == "web_search":
        return f"$ web_search \"{args.get('query', '')[:50]}\""

    if tool_name == "sdiag":
        return "$ sdiag"

    if tool_name == "sprio":
        parts = ["sprio"]
        if args.get("user"):      parts.append(f"--user {args['user']}")
        if args.get("partition"): parts.append(f"--partition {args['partition']}")
        return "$ " + " ".join(parts)

    if tool_name == "sstat":
        return f"$ sstat -j {args.get('job_id', '')}"

    if tool_name == "diagnose_job":
        return f"$ diagnose_job {args.get('job_id', '')}"

    if tool_name in ("confirm_action", "cancel_action"):
        verb = "✓ Confirming" if "confirm" in tool_name else "✗ Cancelling"
        return f"{verb} queued actions"

    if tool_name == "check_pending_actions":
        return "$ check_pending_actions"

    # Generic
    parts = [tool_name] + [f"{k}={v}" for k, v in list(args.items())[:2]]
    return "$ " + " ".join(parts)


def brief_output_summary(output_str: str) -> str | None:
    """
    One-line annotation appended as a completed step after a tool returns.
    Returns None when there is nothing informative to say.
    """
    text = output_str.strip()
    if not text or len(text) < 5:
        return None

    if text.startswith("QUEUED:"):
        return f"↳ {text[:100]}"

    if "SUMMARY:" in text:
        m = re.search(r"SUMMARY:\s*(.+?)(?:\n|$)", text)
        if m:
            return f"↳ {m.group(1).strip()[:100]}"

    # Count Slurm job-state tokens in output
    running = len(re.findall(r"\bRUNNING\b", text))
    pending = len(re.findall(r"\bPENDING\b", text))
    failed  = len(re.findall(r"\bFAILED\b|\bTIMEOUT\b", text))
    if running + pending + failed > 0:
        parts = []
        if running: parts.append(f"{running} running")
        if pending: parts.append(f"{pending} pending")
        if failed:  parts.append(f"{failed} failed")
        return f"↳ {', '.join(parts)}"

    return None
