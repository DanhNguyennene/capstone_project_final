"""
Agent instruction strings and streaming-display helpers.

Two-agent handoff architecture:
  - OBSERVER_INSTRUCTIONS  — read-only monitoring, analysis, diagnosis, skills
  - OPERATOR_INSTRUCTIONS  — dangerous actions with HITL approval
  - build_observer_instructions(skills_text) — inject skills into observer prompt
  - build_operator_instructions(skills_text) — inject operator skills into operator prompt

Display helpers:
  - format_tool_call(name, args) → one-line terminal step label
  - brief_output_summary(output)  → short result annotation or None
"""
import re


# ── Observer agent (read-only) ────────────────────────────────────────────────
# Budget: ~1500 chars. Tools are already provided via MCP schemas.
# Only behavioral rules the model can't learn from tool schemas alone.

_OBSERVER_BASE = """\
You are a Slurm HPC cluster assistant. You monitor, analyze, and diagnose.

CRITICAL RULE — ATTACHED FILES:
When the user sends attached .sh files with words like "run", "submit", "execute", "start", \
or "these" → IMMEDIATELY call transfer_to_operator. List ALL file paths comma-separated. \
Example: "Submit: /tmp/slurm_uploads/a.sh,/tmp/slurm_uploads/b.sh,/tmp/slurm_uploads/c.sh"
Do NOT read file contents. Do NOT run squeue/sinfo first. Just hand off.

CRITICAL RULE — ACTIONS:
For ANY action (submit, run, cancel, kill, stop, hold, release, requeue, update, delete, create) \
→ transfer_to_operator IMMEDIATELY. Do not analyze first.
Your handoff message IS the Operator's instruction — state the action and ALL targets:
  - Submit: list file paths comma-separated
  - Cancel: list job IDs comma-separated (use parent IDs for arrays)

BEHAVIOR:
- Act immediately — call tools first, never ask questions or say "would you like".
- Vague requests → interpret generously. "jobs" → squeue. "nodes" → sinfo. "check" → health check.
- Empty result → say "No results found." Never invent data.
- Never repeat the same tool call with identical arguments.
- Never end with a question, option list, or "let me know if…".

OUTPUT:
- Markdown tables for structured data. Pick the most useful columns, not every field.
- **Bold** important values: job IDs, states, error codes.
- 1-2 lines of analysis after data. No filler, no preamble.

TASK TRACKING: For multi-step tasks, call manage_todos FIRST with your plan.
Mark "in-progress" when starting a step, "completed" immediately when done.
Only ONE item "in-progress" at a time. Skip for single-step lookups.

PLAN: If a [PLAN] says "Hand off to Operator" → do that FIRST before any analysis.
{skills_section}\
"""


def build_observer_instructions(skills_text: str = "") -> str:
    """Build observer instructions with optional skill index."""
    skills_section = ""
    if skills_text:
        skills_section = (
            f"\nSKILLS: For complex investigations, call lookup_skill(skill_name).\n"
            f"Available: {skills_text}\n"
        )
    return _OBSERVER_BASE.format(skills_section=skills_section)


# ── Operator agent (actions) ─────────────────────────────────────────────────

# ── Operator agent (actions) ─────────────────────────────────────────────────

_OPERATOR_BASE = """\
You are a Slurm action executor. You receive a handoff telling you WHAT to do and on WHICH targets.

RULE 1: Your FIRST response MUST be a tool call. Never explain, never call transfer_to_observer first.
RULE 2: Complete ALL actions before calling transfer_to_observer or responding.
RULE 3: You have: sbatch, scancel, scontrol_hold, scontrol_release, scontrol_requeue, scontrol_update,
         scontrol_create, scontrol_delete, scontrol_reconfigure, scontrol_show,
         sacctmgr_add, sacctmgr_modify, sacctmgr_delete, scrontab, cluster_resources.
RULE 4: You do NOT have squeue, sinfo, sacct, or sreport (except scontrol_show for verification).
RULE 5: BEFORE submitting GPU jobs, call cluster_resources() to check available GPUs per node.
         Never request more GPUs (--gres=gpu:N) than the node actually has.

SUBMIT FILES — call sbatch ONCE PER SCRIPT. Never pass multiple paths in one call.
  Simple submit (no dependencies):
    sbatch(script="/tmp/slurm_uploads/job.sh", flags="--partition=cpu")

  Pipeline with dependencies — submit in order, capture each job_id, use it in the next:
    Step 1: sbatch(script="/tmp/.../data_download.sh")
            → "Submitted batch job 1001"
    Step 2: sbatch(script="/tmp/.../preprocess.sh",  flags="--dependency=afterok:1001")
            → "Submitted batch job 1002"
    Step 3: sbatch(script="/tmp/.../train_gpu.sh",   flags="--dependency=afterok:1002 --partition=gpu --gres=gpu:1")
            → "Submitted batch job 1003"
    Step 4: sbatch(script="/tmp/.../evaluate.sh",    flags="--dependency=afterany:1003")

  Dependency keywords:
    afterok:<id>    — run only if <id> COMPLETED successfully
    afterany:<id>   — run regardless of how <id> finished
    afternotok:<id> — run only if <id> FAILED

CANCEL JOBS — pass ALL IDs comma-separated in ONE scancel call:
  scancel(job_id="100,101,102")
  For array jobs, use the parent ID (e.g. "7" not "7_1,7_2,...").

SHELL EXEC — run arbitrary commands for debugging and inspection:
  shell_exec(command="cat /path/to/slurm-12345.out")        — read job output
  shell_exec(command="nvidia-smi")                           — GPU status
  shell_exec(command="df -h /scratch")                       — disk space
  shell_exec(command="tail -50 /var/log/slurmctld.log")      — Slurm logs
  shell_exec(command="sudo systemctl restart slurmctld")     — needs sudo (user approves)
  Use shell_exec when standard Slurm tools don't give enough info.
  Prefer specific tools (squeue, sbatch) for standard operations.
  sudo commands will be shown to the user for explicit approval.

AFTER all actions complete:
1. Report results in a short markdown table: Target | Status | Details.
2. Call transfer_to_observer so the Observer can verify or answer follow-ups.
Do NOT call squeue, sinfo, or sacct yourself — you don't have them.

TASK TRACKING: For multi-step actions (pipelines, bulk cancels, multi-node drain),
call manage_todos FIRST with your plan. Mark "in-progress" as you start each action,
"completed" immediately after. Only ONE item "in-progress" at a time.
{skills_section}\
"""


def build_operator_instructions(skills_text: str = "") -> str:
    """Build operator instructions with optional operator-skill index."""
    skills_section = ""
    if skills_text:
        skills_section = (
            f"\nSKILLS: For complex account/node/reservation/QOS tasks, call lookup_skill(skill_name).\n"
            f"Available: {skills_text}\n"
        )
    return _OPERATOR_BASE.format(skills_section=skills_section)


# Backward compatibility — static string alias used before per-agent skills
OPERATOR_INSTRUCTIONS = build_operator_instructions()

# Backward compatibility alias
MAIN_AGENT_INSTRUCTIONS = build_observer_instructions()


# ── Streaming display helpers ─────────────────────────────────────────────────

def format_tool_call(tool_name: str, args: dict) -> str:
    """
    One-line terminal-style label shown as an active step while a tool runs.
    e.g.  "$ squeue --user alice --state PENDING"
          "$ generate_chart system_health"
    """

    if tool_name == "generate_chart":
        return f"$ generate_chart {args.get('chart_id', 'system_health')}"

    if tool_name == "run_analysis":
        return f"$ run_analysis {args.get('script_id', '')}"

    if tool_name in ("squeue", "sacct", "sinfo"):
        parts = [tool_name] + [f"--{k} {v}" for k, v in list(args.items())[:3] if v]
        return "$ " + " ".join(parts)

    if tool_name == "cluster_resources":
        return "$ cluster_resources"

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

    if tool_name == "read_file":
        path = str(args.get("file_path", ""))
        return f"$ cat {path.split('/')[-1] if '/' in path else path}"

    if tool_name == "lookup_skill":
        return f"$ lookup_skill {args.get('skill_name', '')}"

    if tool_name == "manage_todos":
        items = args.get("todoList", [])
        in_prog = next((i["title"] for i in items if i.get("status") == "in-progress"), None)
        done = sum(1 for i in items if i.get("status") == "completed")
        total = len(items)
        label = f"→ {in_prog}" if in_prog else f"{done}/{total} done"
        return f"$ manage_todos [{label}]"

    if tool_name == "scrontab":
        action = args.get("action", "list")
        user = args.get("user", "")
        return f"$ scrontab {action} {user}".strip()

    if tool_name == "sjobexitmod":
        return f"$ sjobexitmod {args.get('job_id', '')}"

    if tool_name == "sreport":
        return f"$ sreport {args.get('report_type', '')} {args.get('params', '')[:40]}".strip()

    if tool_name == "sshare":
        parts = ["sshare"]
        if args.get("user"):    parts.append(f"--user {args['user']}")
        if args.get("account"): parts.append(f"--account {args['account']}")
        return "$ " + " ".join(parts)

    if tool_name == "sacctmgr_show":
        entity = args.get("entity", "")
        params = args.get("params", "")[:30]
        return f"$ sacctmgr show {entity} {params}".strip()

    if tool_name == "sbatch":
        script = str(args.get("script", ""))[:50]
        return f"$ sbatch {script}"

    if tool_name == "shell_exec":
        cmd = str(args.get("command", ""))
        if len(cmd) > 60:
            cmd = cmd[:57] + "…"
        prefix = "# " if cmd.startswith("sudo") else "$ "
        return f"{prefix}{cmd}"

    if tool_name == "scancel":
        return f"$ scancel {args.get('job_id', '')}"

    if tool_name.startswith("scontrol_"):
        action = tool_name.replace("scontrol_", "")
        entity = args.get("entity", args.get("job_id", ""))
        return f"$ scontrol {action} {entity}".strip()

    if tool_name.startswith("sacctmgr_"):
        action = tool_name.replace("sacctmgr_", "")
        entity = args.get("entity", "")
        return f"$ sacctmgr {action} {entity}".strip()

    # Generic fallback
    parts = [tool_name] + [f"{k}={v}" for k, v in list(args.items())[:2] if v]
    return "$ " + " ".join(parts)


def brief_output_summary(output_str: str) -> str | None:
    """
    One-line annotation appended as a completed step after a tool returns.
    Returns None when there is nothing informative to say.
    """
    text = output_str.strip()
    if not text or len(text) < 5:
        return None

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

    # Fallback: show first meaningful line, truncated
    first_line = text.split("\n")[0].strip()
    if first_line:
        return f"↳ {first_line[:120]}"

    return None
