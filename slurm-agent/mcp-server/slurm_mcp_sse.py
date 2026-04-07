"""
Slurm MCP Server (SSE transport) — mock mode for local development

Usage:
    python slurm_mcp_sse.py                        # healthy scenario, port 3002
    python slurm_mcp_sse.py --mock mixed           # mixed scenario
    python slurm_mcp_sse.py --mock failed --port 3002

Scenarios: healthy | failed | pending | mixed | debug_needed
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Literal

# ── Add parent dirs to path so defined_charts / defined_analysis are importable ──
THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(THIS_DIR))
sys.path.insert(0, str(THIS_DIR.parent))

from mcp.server.fastmcp import FastMCP
from mock_data import MOCK_JOBS, MOCK_NODES

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Parse CLI args early so SCENARIO is set before tool registration ──────────
_parser = argparse.ArgumentParser(add_help=False)
_parser.add_argument("--mock", default="healthy",
                     choices=["healthy", "failed", "pending", "mixed", "debug_needed"])
_parser.add_argument("--port", type=int, default=3002)
_parser.add_argument("--host", default="0.0.0.0")
_known, _ = _parser.parse_known_args()

SCENARIO: str = _known.mock
PORT: int = _known.port
HOST: str = _known.host

logger.info(f"Starting Slurm MCP SSE server — scenario={SCENARIO}, {HOST}:{PORT}")

mcp = FastMCP("slurm-mcp-mock")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _jobs():
    return MOCK_JOBS.get(SCENARIO, [])

def _nodes():
    return MOCK_NODES.get(SCENARIO, [])

def _fmt_jobs(jobs: list) -> str:
    if not jobs:
        return "No jobs found."
    lines = ["JOBID    NAME                USER     STATE     TIME      NODES CPUS MEM  PARTITION"]
    lines.append("-" * 88)
    for j in jobs:
        lines.append(
            f"{j.get('job_id','?'):<8} {j.get('name','?'):<20} {j.get('user','?'):<8} "
            f"{j.get('state','?'):<9} {j.get('time','?'):<9} {j.get('nodes','?'):<5} "
            f"{j.get('cpus','?'):<4} {j.get('mem','?'):<4} {j.get('partition','?')}"
        )
    return "\n".join(lines)

def _fmt_nodes(nodes: list) -> str:
    if not nodes:
        return "No nodes found."
    lines = ["NODENAME       STATE  CPUS(A/T)  MEM(A/T)   PARTITION  GRES"]
    lines.append("-" * 72)
    for n in nodes:
        reason = f"  [{n['reason']}]" if n.get("reason") else ""
        lines.append(
            f"{n.get('name','?'):<14} {n.get('state','?'):<6} {n.get('cpus','?'):<10} "
            f"{n.get('mem','?'):<10} {n.get('partition','?'):<10} {n.get('gres','')}{reason}"
        )
    return "\n".join(lines)


# ── Query Tools ───────────────────────────────────────────────────────────────

@mcp.tool()
def squeue(user: str = "", state: str = "", partition: str = "") -> str:
    """Show current job queue. Filter by user, state, or partition."""
    jobs = _jobs()
    if user:
        jobs = [j for j in jobs if j.get("user", "").lower() == user.lower()]
    if state:
        jobs = [j for j in jobs if j.get("state", "").upper() == state.upper()]
    if partition:
        jobs = [j for j in jobs if j.get("partition", "").lower() == partition.lower()]
    return _fmt_jobs(jobs)


@mcp.tool()
def sinfo(partition: str = "", node: str = "") -> str:
    """Show cluster node and partition information."""
    nodes = _nodes()
    if partition:
        nodes = [n for n in nodes if n.get("partition", "").lower() == partition.lower()]
    if node:
        nodes = [n for n in nodes if n.get("name", "").lower() == node.lower()]

    # Partition summary
    all_nodes = _nodes()
    partitions: dict[str, dict] = {}
    for n in all_nodes:
        p = n.get("partition", "unknown")
        if p not in partitions:
            partitions[p] = {"nodes": 0, "idle": 0, "alloc": 0, "down": 0}
        partitions[p]["nodes"] += 1
        state = n.get("state", "")
        if "idle" in state:
            partitions[p]["idle"] += 1
        elif "alloc" in state or "mix" in state:
            partitions[p]["alloc"] += 1
        elif "down" in state or "drain" in state:
            partitions[p]["down"] += 1

    part_lines = ["PARTITION  AVAIL  TIMELIMIT   NODES(A/I/D)"]
    part_lines.append("-" * 48)
    for pname, counts in partitions.items():
        part_lines.append(
            f"{pname:<10} up     unlimited   "
            f"{counts['alloc']}/{counts['idle']}/{counts['down']}"
        )

    return "\n".join(part_lines) + "\n\n" + _fmt_nodes(nodes)


@mcp.tool()
def sacct(
    user: str = "",
    state: str = "",
    starttime: str = "",
    endtime: str = "",
    format: str = "JobID,JobName,User,State,ExitCode,Elapsed,NCPUs,ReqMem",
) -> str:
    """Query job accounting records from Slurm database."""
    jobs = _jobs()
    # Include completed/failed/timeout jobs from mock data
    history_states = {"FAILED", "COMPLETED", "TIMEOUT", "CANCELLED"}
    history = [j for j in jobs if j.get("state", "").upper() in history_states]

    if not history:
        # Fall back to all jobs if none in history states
        history = jobs

    if user:
        history = [j for j in history if j.get("user", "").lower() == user.lower()]
    if state:
        history = [j for j in history if j.get("state", "").upper() == state.upper()]

    if not history:
        return "No accounting records found for given filters."

    lines = [f"{format.replace(',', '|')}"]
    lines.append("-" * 72)
    for j in history:
        exit_code = j.get("exit_code", "0:0")
        stderr = j.get("stderr", "")
        base = (
            f"{j.get('job_id','?')}|{j.get('name','?')}|{j.get('user','?')}|"
            f"{j.get('state','?')}|{exit_code}|{j.get('time','?')}|"
            f"{j.get('cpus','?')}|{j.get('mem','?')}"
        )
        lines.append(base)
        if stderr:
            lines.append(f"  stderr: {stderr[:120]}")

    return "\n".join(lines)


@mcp.tool()
def scontrol_show(entity: str = "job", id: str = "") -> str:
    """Show detailed information about a Slurm entity (job, node, partition)."""
    if entity.lower() == "job":
        jobs = _jobs()
        if id:
            jobs = [j for j in jobs if str(j.get("job_id", "")) == str(id)]
        if not jobs:
            return f"scontrol: error: Invalid job id specified"
        j = jobs[0]
        return (
            f"JobId={j['job_id']} JobName={j['name']}\n"
            f"   UserId={j.get('user','?')} GroupId={j.get('user','?')}\n"
            f"   JobState={j['state']} Reason={j.get('reason','None')}\n"
            f"   NumNodes={j.get('nodes',1)} NumCPUs={j.get('cpus',1)}\n"
            f"   MinMemoryNode={j.get('mem','0')}\n"
            f"   Partition={j.get('partition','?')}\n"
            f"   RunTime={j.get('time','0:00:00')}\n"
            f"   ExitCode={j.get('exit_code','0:0')}"
        )
    elif entity.lower() == "node":
        nodes = _nodes()
        if id:
            nodes = [n for n in nodes if n.get("name", "").lower() == id.lower()]
        if not nodes:
            return f"scontrol: error: Invalid node name: {id}"
        n = nodes[0]
        return (
            f"NodeName={n['name']} State={n['state']}\n"
            f"   CPUTot={n.get('cpus','?').split('/')[-1] if '/' in n.get('cpus','') else n.get('cpus','?')}\n"
            f"   RealMemory={n.get('mem','?').split('/')[-1] if '/' in n.get('mem','') else n.get('mem','?')}\n"
            f"   Partitions={n.get('partition','?')}\n"
            f"   Gres={n.get('gres','(null)')}\n"
            f"   Reason={n.get('reason','none')}"
        )
    return f"scontrol show {entity}: not supported in mock mode"


# ── Action Tools ──────────────────────────────────────────────────────────────

@mcp.tool()
def sbatch(script: str, flags: str = "") -> str:
    """Submit a batch job script to Slurm."""
    import random
    job_id = random.randint(9000, 9999)
    return f"Submitted batch job {job_id}"


@mcp.tool()
def scancel(job_id: str, user: str = "") -> str:
    """Cancel a Slurm job."""
    jobs = _jobs()
    match = [j for j in jobs if str(j.get("job_id", "")) == str(job_id)]
    if not match:
        return f"scancel: error: Kill job error on job id {job_id}: Invalid job id specified"
    return f"Job {job_id} cancelled successfully."


@mcp.tool()
def scontrol_hold(job_id: str) -> str:
    """Place a hold on a pending Slurm job."""
    return f"Job {job_id} held."


@mcp.tool()
def scontrol_release(job_id: str) -> str:
    """Release a held Slurm job."""
    return f"Job {job_id} released."


@mcp.tool()
def srun(command: str, nodes: int = 1, cpus: int = 1, partition: str = "cpu") -> str:
    """Run a command interactively via srun (mock)."""
    return f"[mock srun] {command} — would run on {nodes} node(s), {cpus} CPU(s), partition={partition}"


@mcp.tool()
def salloc(nodes: int = 1, cpus: int = 1, partition: str = "cpu", time: str = "01:00:00") -> str:
    """Allocate resources interactively (mock)."""
    import random
    job_id = random.randint(9000, 9999)
    return f"salloc: Granted job allocation {job_id} ({nodes} node(s), {cpus} CPUs, {partition})"


# ── Analysis Tool ─────────────────────────────────────────────────────────────

# Map script IDs to human descriptions
_ANALYSIS_SCRIPTS = {
    "analyze_my_jobs":       "analyze_my_jobs",
    "analyze_failed_jobs":   "analyze_failed_jobs",
    "analyze_gpu_resources": "analyze_gpu_resources",
    "analyze_my_efficiency": "analyze_my_efficiency",
    "analyze_my_usage":      "analyze_my_usage",
    "analyze_pending_jobs":  "analyze_pending_jobs",
    "analyze_cluster_status":"analyze_cluster_status",
}

@mcp.tool()
def run_analysis(script_id: Literal[
    "analyze_my_jobs",
    "analyze_failed_jobs",
    "analyze_gpu_resources",
    "analyze_my_efficiency",
    "analyze_my_usage",
    "analyze_pending_jobs",
    "analyze_cluster_status",
    "analyze_node_health",
    "analyze_job_efficiency",
]) -> str:
    """
    Run a predefined cluster analysis script.

    Available script_ids:
      analyze_cluster_status, analyze_failed_jobs, analyze_pending_jobs,
      analyze_gpu_resources, analyze_node_health, analyze_job_efficiency,
      analyze_my_jobs, analyze_my_usage, analyze_my_efficiency
    """
    sid = script_id.strip().lower()

    jobs  = _jobs()
    nodes = _nodes()

    running   = [j for j in jobs if j.get("state") == "RUNNING"]
    pending   = [j for j in jobs if j.get("state") == "PENDING"]
    failed    = [j for j in jobs if j.get("state") in ("FAILED", "TIMEOUT")]
    completed = [j for j in jobs if j.get("state") == "COMPLETED"]

    gpu_nodes  = [n for n in nodes if "gpu" in n.get("gres", "").lower()]
    down_nodes = [n for n in nodes if "down" in n.get("state", "").lower() or "drain" in n.get("state", "").lower()]

    if sid == "analyze_cluster_status":
        return (
            f"=== Cluster Status Analysis (scenario: {SCENARIO}) ===\n"
            f"Total jobs   : {len(jobs)}\n"
            f"  Running    : {len(running)}\n"
            f"  Pending    : {len(pending)}\n"
            f"  Failed     : {len(failed)}\n"
            f"  Completed  : {len(completed)}\n\n"
            f"Total nodes  : {len(nodes)}\n"
            f"  GPU nodes  : {len(gpu_nodes)}\n"
            f"  Down/Drain : {len(down_nodes)}\n"
        )

    elif sid == "analyze_failed_jobs":
        if not failed:
            return "No failed or timed-out jobs in current scenario."
        lines = [f"=== Failed Jobs Analysis (scenario: {SCENARIO}) ==="]
        for j in failed:
            lines.append(
                f"\nJob {j['job_id']} ({j['name']}) — {j['state']}"
                f"\n  User     : {j.get('user','?')}"
                f"\n  ExitCode : {j.get('exit_code','?')}"
                f"\n  Reason   : {j.get('reason','?')}"
            )
            if j.get("stderr"):
                lines.append(f"  Stderr   : {j['stderr'][:200]}")
        return "\n".join(lines)

    elif sid == "analyze_gpu_resources":
        if not gpu_nodes:
            return "No GPU nodes found in current scenario."
        lines = [f"=== GPU Resource Analysis (scenario: {SCENARIO}) ==="]
        for n in gpu_nodes:
            lines.append(
                f"{n['name']}: state={n['state']}, "
                f"GRES={n.get('gres','?')}, CPUs={n.get('cpus','?')}, Mem={n.get('mem','?')}"
            )
        gpu_jobs = [j for j in running if j.get("partition") == "gpu"]
        lines.append(f"\nGPU jobs running: {len(gpu_jobs)}")
        for j in gpu_jobs:
            lines.append(f"  Job {j['job_id']} ({j['name']}) by {j['user']}")
        return "\n".join(lines)

    elif sid == "analyze_pending_jobs":
        if not pending:
            return "No pending jobs found."
        lines = [f"=== Pending Jobs Analysis (scenario: {SCENARIO}) ==="]
        for j in pending:
            lines.append(
                f"Job {j['job_id']} ({j['name']}) — reason: {j.get('reason','?')}, "
                f"partition: {j.get('partition','?')}, nodes: {j.get('nodes','?')}"
            )
        return "\n".join(lines)

    elif sid in ("analyze_my_jobs", "analyze_my_usage", "analyze_my_efficiency"):
        lines = [f"=== My Jobs Summary (scenario: {SCENARIO}) ==="]
        for j in jobs:
            lines.append(
                f"Job {j['job_id']} ({j['name']}): {j['state']}, "
                f"CPUs={j.get('cpus','?')}, Mem={j.get('mem','?')}, "
                f"Time={j.get('time','?')}"
            )
        return "\n".join(lines) if lines[1:] else "No jobs found."

    elif sid == "analyze_node_health":
        lines = [f"=== Node Health Analysis (scenario: {SCENARIO}) ==="]
        for n in nodes:
            state = n.get("state", "?")
            reason = f" [{n['reason']}]" if n.get("reason") else ""
            lines.append(
                f"{n['name']}: {state}{reason}  CPUs={n.get('cpus','?')}  "
                f"Mem={n.get('mem','?')}  GRES={n.get('gres','none')}"
            )
        lines.append(f"\nSummary: {len(nodes)} nodes, "
                     f"{len(down_nodes)} down/drain, "
                     f"{len([n for n in nodes if 'idle' in n.get('state','')])} idle")
        return "\n".join(lines)

    elif sid == "analyze_job_efficiency":
        import hashlib
        targets = running or failed
        if not targets:
            return "No running or recently completed jobs to analyze efficiency."
        lines = [f"=== Job Efficiency Estimate (scenario: {SCENARIO}) ==="]
        lines.append(f"{'JOBID':<8}  {'NAME':<22}  {'USER':<8}  {'CPUS':<5}  {'MEM':<6}  {'CPU_EFF':>7}  {'MEM_EFF':>7}")
        lines.append("-" * 72)
        for j in targets[:10]:
            h = int(hashlib.md5(str(j['job_id']).encode()).hexdigest()[:4], 16)
            cpu_eff = 25 + (h % 65)
            mem_eff = 35 + ((h >> 4) % 60)
            warnings = []
            if cpu_eff < 50: warnings.append("⚠ CPU")
            if mem_eff < 40: warnings.append("⚠ MEM")
            warn = "  " + " ".join(warnings) if warnings else ""
            lines.append(
                f"{j['job_id']:<8}  {j['name'][:22]:<22}  {j.get('user','?'):<8}  "
                f"{j.get('cpus','?'):<5}  {j.get('mem','?'):<6}  "
                f"{cpu_eff:>6}%  {mem_eff:>6}%{warn}"
            )
        lines.append("\nNote: efficiency estimated from step counters (mock data).")
        lines.append("Real: use 'sstat -j <jobid>' for live CPU/mem utilization.")
        return "\n".join(lines)

    return f"Unknown script_id '{script_id}'. Available: {', '.join(['analyze_cluster_status','analyze_failed_jobs','analyze_pending_jobs','analyze_gpu_resources','analyze_node_health','analyze_job_efficiency','analyze_my_jobs'])}"


# ── Chart Tool ────────────────────────────────────────────────────────────────

@mcp.tool()
def generate_chart(chart_id: Literal[
    "system_health",
    "cluster_topology",
    "pending_analysis",
    "resource_map",
    "job_lifecycle",
    "efficiency_report",
]) -> str:
    """
    Generate a Mermaid diagram from live scenario data.

    Each chart_id uses a DIFFERENT Mermaid chart type:
      system_health    → xychart-beta bars: CPU / Memory / GPU / Node-health %
      cluster_topology → flowchart TD: nodes grouped by state with counts
      pending_analysis → xychart-beta bars: jobs blocked per reason
      resource_map     → xychart-beta bars: CPUs in-use per user
      job_lifecycle    → gantt: running jobs with real elapsed times
      efficiency_report → xychart-beta bars: estimated CPU efficiency per job
    """
    cid   = chart_id.strip().lower()
    jobs  = _jobs()
    nodes = _nodes()

    # ── shared micro-helpers ────────────────────────────────────────────────
    def _cpu_pair(s: str):
        p = s.split("/")
        try: return int(p[0]), int(p[-1])
        except: return 0, 0

    def _mem_gb(s: str) -> float:
        s = (s or "0").strip().upper()
        try:
            if s.endswith("T"): return float(s[:-1]) * 1024
            if s.endswith("G"): return float(s[:-1])
            if s.endswith("M"): return float(s[:-1]) / 1024
        except: pass
        return 0.0

    def _elapsed_min(t: str) -> int:
        p = t.split(":")
        try:
            if len(p) >= 3: return int(p[0]) * 60 + int(p[1])
            if len(p) == 2: return int(p[0]) * 60 + int(p[1])
        except: pass
        return 1

    def _hhmm(m: int) -> str:
        m = max(0, m)
        return f"{m // 60:02d}:{m % 60:02d}"

    # ── system_health: xychart-beta utilization bars ───────────────────────
    if cid == "system_health":
        cpu_a = cpu_t = 0
        mem_a = mem_t = 0.0
        gpu_n = gpu_a = down_n = 0
        for n in nodes:
            ca, ct = _cpu_pair(n.get("cpus", "0/0"))
            cpu_a += ca; cpu_t += ct
            mp = n.get("mem", "0/0").split("/")
            mem_a += _mem_gb(mp[0]); mem_t += _mem_gb(mp[-1])
            st = n.get("state", "")
            if n.get("gres", ""):
                gpu_n += 1
                if "alloc" in st or "mix" in st: gpu_a += 1
            if "down" in st or "drain" in st: down_n += 1

        cpu_pct  = round(cpu_a / cpu_t * 100)  if cpu_t  else 0
        mem_pct  = round(mem_a / mem_t * 100)  if mem_t  else 0
        gpu_pct  = round(gpu_a / gpu_n * 100)  if gpu_n  else 0
        heal_pct = round((len(nodes) - down_n) / len(nodes) * 100) if nodes else 100

        return (
            f"xychart-beta\n"
            f"    title \"Cluster Utilization — {SCENARIO}\"\n"
            f"    x-axis [\"CPU\", \"Memory\", \"GPU Nodes\", \"Node Health\"]\n"
            f"    y-axis \"%\" 0 --> 100\n"
            f"    bar [{cpu_pct}, {mem_pct}, {gpu_pct}, {heal_pct}]"
        )

    # ── cluster_topology: flowchart grouped by state ───────────────────────
    elif cid == "cluster_topology":
        from collections import defaultdict
        groups: dict = defaultdict(list)
        for n in nodes:
            st = n.get("state", "unknown").lower().rstrip("*")
            if   "down"  in st: key = "DOWN"
            elif "drain" in st: key = "DRAIN"
            elif "alloc" in st: key = "ALLOC"
            elif "mix"   in st: key = "MIX"
            elif "idle"  in st: key = "IDLE"
            else:               key = st.upper()[:6]
            groups[key].append(n["name"])

        defs   = "".join(
            f'\n    {k}["{k}\\n{len(v)} node(s)\\n{", ".join(v[:3])}{"..." if len(v) > 3 else ""}"]'
            for k, v in sorted(groups.items())
        )
        arrows = "".join(f"\n    Cluster --> {k}" for k in sorted(groups))
        return (
            f"flowchart TD\n"
            f"    Cluster[\"HPC Cluster — {SCENARIO}\\n{len(nodes)} nodes total\"]"
            f"{defs}{arrows}"
        )

    # ── pending_analysis: xychart-beta reason bars ─────────────────────────
    elif cid == "pending_analysis":
        from collections import Counter
        pj = [j for j in jobs if j.get("state") == "PENDING"]
        if not pj:
            return (
                "flowchart LR\n"
                "    OK[\"✅ Queue clear — no pending jobs\"]"
            )
        reasons = Counter(j.get("reason") or "Unknown" for j in pj)
        top = reasons.most_common(5)
        _SHORT = {
            "Resources": "Resources", "Priority": "Priority",
            "Dependency": "Dependency",
            "QOSMaxJobsPerUserLimit": "QOSMaxJobs",
            "QOSMaxCpuPerUserLimit":  "QOSMaxCPU",
            "ReqNodeNotAvail":        "NodeUnavail",
            "AssocGrpCPUMinutesLimit":"CPUBudget",
        }
        labels = json.dumps([_SHORT.get(r, r[:12]) for r, _ in top])
        counts = json.dumps([c for _, c in top])
        max_c  = max(c for _, c in top)
        return (
            f"xychart-beta\n"
            f"    title \"Pending Queue: {len(pj)} jobs blocked\"\n"
            f"    x-axis {labels}\n"
            f"    y-axis \"Jobs\" 0 --> {max_c + 1}\n"
            f"    bar {counts}"
        )

    # ── resource_map: xychart-beta per-user CPU bars ───────────────────────
    elif cid == "resource_map":
        from collections import defaultdict
        user_cpu: dict = defaultdict(int)
        for j in jobs:
            if j.get("state") == "RUNNING":
                user_cpu[j.get("user", "?")] += int(j.get("cpus", 0))
        if not user_cpu:
            return (
                "flowchart LR\n"
                "    EMPTY[\"No running jobs — all resources free\"]"
            )
        users  = sorted(user_cpu)
        mc     = max(user_cpu.values())
        labels = json.dumps(users)
        vals   = json.dumps([user_cpu[u] for u in users])
        return (
            f"xychart-beta\n"
            f"    title \"CPU Usage by User — {SCENARIO}\"\n"
            f"    x-axis {labels}\n"
            f"    y-axis \"CPUs\" 0 --> {mc + 4}\n"
            f"    bar {vals}"
        )

    # ── job_lifecycle: gantt with real running jobs ────────────────────────
    elif cid == "job_lifecycle":
        running = [j for j in jobs if j.get("state") == "RUNNING"]
        if not running:
            return (
                "flowchart LR\n"
                "    A[\"sbatch\"] -->|queue| B[\"PENDING\"]\n"
                "    B -->|free slot| C[\"RUNNING\"]\n"
                "    C -->|success| D[\"COMPLETED\"]\n"
                "    C -->|error| E[\"FAILED\"]\n"
                "    C -->|wall limit| F[\"TIMEOUT\"]"
            )
        from collections import defaultdict
        by_user: dict = defaultdict(list)
        for j in running: by_user[j.get("user", "?")].append(j)

        now = 600  # reference checkpoint = 10:00
        sections = "".join(
            f"\n    section {u}\n" + "".join(
                f"        {j['name'][:18]} [{j['job_id']}] :active, "
                f"{_hhmm(now - _elapsed_min(j.get('time', '0:01')))}, "
                f"{_elapsed_min(j.get('time', '0:01'))}m\n"
                for j in uj
            )
            for u, uj in sorted(by_user.items())
        )
        return (
            f"gantt\n"
            f"    title Running Jobs Timeline (checkpoint 10:00)\n"
            f"    dateFormat HH:mm\n"
            f"    axisFormat %H:%M"
            f"{sections}"
        )

    # ── efficiency_report: xychart-beta estimated efficiency bars ──────────
    elif cid == "efficiency_report":
        import hashlib
        targets = [j for j in jobs if j.get("state") == "RUNNING"] or \
                  [j for j in jobs if j.get("state") in ("FAILED", "COMPLETED")]
        if not targets:
            return "No jobs available for efficiency analysis."
        targets = targets[:6]

        def _eff(job_id: str) -> int:
            h = int(hashlib.md5(job_id.encode()).hexdigest()[:4], 16)
            return 25 + (h % 65)

        labels = json.dumps([f"{j['name'][:10]}/{j['job_id']}" for j in targets])
        effs   = json.dumps([_eff(str(j["job_id"])) for j in targets])
        return (
            f"xychart-beta\n"
            f"    title \"Estimated CPU Efficiency per Job (%)\"\n"
            f"    x-axis {labels}\n"
            f"    y-axis \"Efficiency %\" 0 --> 100\n"
            f"    bar {effs}"
        )

    else:
        return (
            f"Unknown chart_id '{chart_id}'. "
            "Available: system_health, cluster_topology, pending_analysis, "
            "resource_map, job_lifecycle, efficiency_report"
        )


# ── Web Search Tool ───────────────────────────────────────────────────────────

@mcp.tool()
def web_search(
    query: str,
    search_type: str = "general",
    fetch_content: bool = False,
) -> str:
    """
    Search the web for Slurm docs, error messages, or HPC resources.
    Uses DuckDuckGo. search_type: general | slurm | error
    """
    import urllib.request
    import urllib.parse
    import re

    if search_type == "slurm":
        query = f"Slurm workload manager {query}"
    elif search_type == "error":
        query = f"HPC Slurm error {query} fix"

    encoded = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return f"Web search error: {e}"

    # Extract result snippets from DDG HTML
    results = []
    # Match result titles and snippets
    title_pattern = re.compile(r'class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>', re.S)
    snippet_pattern = re.compile(r'class="result__snippet">(.*?)</span>', re.S)

    titles   = title_pattern.findall(html)
    snippets = [re.sub(r"<[^>]+>", "", s) for s in snippet_pattern.findall(html)]

    for i, (href, title) in enumerate(titles[:5]):
        title_clean = re.sub(r"<[^>]+>", "", title).strip()
        snippet = snippets[i].strip() if i < len(snippets) else ""
        results.append(f"[{i+1}] {title_clean}\n    {href}\n    {snippet}")

    if not results:
        return f"No results found for: {query}"

    return f"Search: {query}\n\n" + "\n\n".join(results)


# ── Diagnostic Tools ─────────────────────────────────────────────────────────

@mcp.tool()
def sdiag() -> str:
    """Show Slurm scheduler diagnostics: backfill stats, cycle times, submit/RPC rates."""
    running = len([j for j in _jobs() if j.get("state") == "RUNNING"])
    pending = len([j for j in _jobs() if j.get("state") == "PENDING"])
    return (
        f"=== Slurm Scheduler Diagnostics (scenario: {SCENARIO}) ===\n"
        f"Server Thread      : Alive\n"
        f"Main sched cycles  : 1 (last=8ms, mean=6ms, depth=12)\n"
        f"Backfill cycles    : 89 (last=45ms, mean=40ms, sched%=94.2)\n"
        f"Queue depth        : {running} running, {pending} pending\n"
        f"RPCs/last minute   : 3 submitted, 42 completed\n"
        f"RPC queue latency  : 1.8 ms avg\n"
        f"Last cycle end     : 0.000 sec\n"
        f"Last full cycle    : 0.023 sec\n"
    )


@mcp.tool()
def sprio(user: str = "", partition: str = "") -> str:
    """Show composite job priority factors for pending jobs (age, fairshare, QOS, size)."""
    import hashlib
    pending = [j for j in _jobs() if j.get("state") == "PENDING"]
    if user:
        pending = [j for j in pending if j.get("user", "").lower() == user.lower()]
    if partition:
        pending = [j for j in pending if j.get("partition", "").lower() == partition.lower()]
    if not pending:
        return "No pending jobs match the given filters."

    lines = [
        f"{'JOBID':<8}  {'USER':<8}  {'PARTITION':<10}  {'PRIORITY':>8}  "
        f"{'AGE':>6}  {'FAIRSHARE':>9}  {'QOS':>6}  {'SIZE':>6}  NICE"
    ]
    lines.append("-" * 72)
    for j in pending:
        h = int(hashlib.md5(str(j["job_id"]).encode()).hexdigest()[:6], 16)
        priority  = 1000 + (h % 8000)
        age       = (h >> 2) % 500
        fairshare = (h >> 4) % 700
        qos       = (h >> 6) % 300
        size      = max(1, j.get("cpus", 1)) * 10
        lines.append(
            f"{j['job_id']:<8}  {j.get('user','?'):<8}  {j.get('partition','?'):<10}  "
            f"{priority:>8}  {age:>6}  {fairshare:>9}  {qos:>6}  {size:>6}  0"
        )
    lines.append(
        f"\nNote: Priority = age({lines[1].count('AGE')}) + fairshare + QOS + "
        f"size. Higher = runs sooner."
    )
    return "\n".join(lines)


@mcp.tool()
def sstat(job_id: str) -> str:
    """Show real-time step statistics for a running job: CPU usage, AveRSS, MaxRSS, disk I/O."""
    import hashlib
    jobs = _jobs()
    match = next((j for j in jobs if str(j.get("job_id", "")) == str(job_id)), None)
    if not match:
        return f"sstat: error: Invalid job id: {job_id}"
    if match.get("state") != "RUNNING":
        return (
            f"sstat: Job {job_id} is {match.get('state','?')} — "
            f"sstat only works on RUNNING jobs."
        )

    h = int(hashlib.md5(job_id.encode()).hexdigest()[:5], 16)
    cpus      = int(match.get("cpus", 1))
    cpu_pct   = round((25 + (h % 65)) * cpus / max(cpus, 1), 1)
    ave_rss   = f"{200 + (h % 600)}M"
    max_rss   = f"{400 + (h % 800)}M"
    ave_vss   = f"{1024 + (h % 2048)}M"
    max_disk_r = f"{10 + (h % 200)}G"
    max_disk_w = f"{5 + (h % 100)}G"

    return (
        f"JobID         = {job_id}.batch\n"
        f"JobName       = {match.get('name','?')}\n"
        f"State         = RUNNING\n"
        f"CPUs          = {cpus}\n"
        f"AveCPU        = {cpu_pct}%\n"
        f"AveRSS        = {ave_rss}\n"
        f"MaxRSS        = {max_rss}\n"
        f"AveVMSize     = {ave_vss}\n"
        f"MaxDiskRead   = {max_disk_r}\n"
        f"MaxDiskWrite  = {max_disk_w}\n"
        f"AllocCPUS     = {cpus}\n"
        f"ReqMem        = {match.get('mem','?')}\n"
        f"Elapsed       = {match.get('time','?')}\n"
    )


# Exit-code hints for diagnose_job
_EXIT_HINTS: dict[str, str] = {
    "0:0": "COMPLETED normally.",
    "1:0": "Application returned exit code 1 — check stderr for Python/app error.",
    "2:0": "Misuse of shell command (bad syntax) — check the job script.",
    "137:0": "OOM-killed (SIGKILL). Increase --mem; current: {mem}.",
    "143:0": "Walltime exceeded (SIGTERM). Increase --time or checkpoint more often.",
    "1:53": "Node hardware failure (slurm signal 53). Requeue: scontrol_requeue {job_id}.",
    "7:0": "Bus error — often memory corruption or file I/O on shared FS.",
    "127:0": "Command not found in job script (module not loaded?).",
}

# Pending-reason hints
_PENDING_HINTS: dict[str, str] = {
    "Resources":               "Wait for matching nodes to free up, or reduce --nodes/--cpus.",
    "Priority":                "Lower priority than other jobs — wait or ask admin to boost.",
    "Dependency":              "Waiting on parent job to finish — check with `scontrol show job <id>`.",
    "QOSMaxCpuPerUserLimit":   "You hit your per-user CPU quota. Wait for your other jobs to finish.",
    "QOSMaxJobsPerUserLimit":  "You hit the max-jobs-per-user limit. Wait for a slot.",
    "QOSMaxWallDurationPerJobLimit": "Requested --time exceeds QOS wall limit. Reduce or use a different QOS.",
    "ReqNodeNotAvail":         "Requested node(s) are unavailable/down. Remove node constraint or resubmit.",
    "AssocGrpCPUMinutesLimit": "Group CPU-minute budget exhausted. Contact your PI or HPC admin.",
    "AssocMaxJobsLimit":       "Account job limit reached. Wait for other jobs to complete.",
    "None":                    "Job is probably starting — should move to RUNNING shortly.",
}


@mcp.tool()
def diagnose_job(job_id: str) -> str:
    """
    Full job diagnosis: current state, resources, exit code interpretation,
    captured stderr, and actionable fix hints.
    """
    jobs = _jobs()
    match = next((j for j in jobs if str(j.get("job_id", "")) == str(job_id)), None)
    if not match:
        return (
            f"diagnose_job: Job {job_id} not found in current scenario '{SCENARIO}'.\n"
            f"Tip: use sacct to look up completed / recently failed jobs."
        )

    state     = match.get("state", "UNKNOWN")
    exit_code = match.get("exit_code", "0:0")
    stderr    = match.get("stderr", "")
    reason    = match.get("reason") or "None"
    user      = match.get("user", "?")
    mem       = match.get("mem", "?")
    cpus      = match.get("cpus", "?")
    partition = match.get("partition", "?")
    elapsed   = match.get("time", "?")

    hint = _EXIT_HINTS.get(exit_code, f"Exit code {exit_code} — check Slurm docs or stderr.")
    hint = hint.format(mem=mem, job_id=job_id)

    if state == "PENDING":
        pending_hint = _PENDING_HINTS.get(reason, f"Reason '{reason}' — check `scontrol show job {job_id}`.")
        diagnosis = (
            f"=== Job Diagnosis: {job_id} ===\n"
            f"State     : PENDING\n"
            f"Reason    : {reason}\n"
            f"User      : {user}   Partition: {partition}\n"
            f"Resources : {cpus} CPU(s), {mem} RAM\n\n"
            f"DIAGNOSIS : {pending_hint}\n"
        )
    elif state == "RUNNING":
        diagnosis = (
            f"=== Job Diagnosis: {job_id} ===\n"
            f"State     : RUNNING\n"
            f"User      : {user}   Partition: {partition}\n"
            f"Resources : {cpus} CPU(s), {mem} RAM\n"
            f"Elapsed   : {elapsed}\n\n"
            f"DIAGNOSIS : Job is healthy and running. Use sstat({job_id}) for live step stats.\n"
        )
    else:
        diagnosis = (
            f"=== Job Diagnosis: {job_id} ===\n"
            f"State     : {state}\n"
            f"ExitCode  : {exit_code}\n"
            f"User      : {user}   Partition: {partition}\n"
            f"Resources : {cpus} CPU(s), {mem} RAM\n"
            f"Elapsed   : {elapsed}\n\n"
            f"DIAGNOSIS : {hint}\n"
        )
        if stderr:
            diagnosis += f"\nSTDERR (last 300 chars):\n{stderr[-300:]}\n"

    return diagnosis


# ── Admin Tools (mock — all safe, just return confirmation) ───────────────────

@mcp.tool()
def scontrol_update(entity: str, id: str, params: str) -> str:
    """Update a Slurm entity attribute. params format: 'key=value key2=value2' (e.g. 'TimeLimit=2:00:00 Priority=100')."""
    return f"scontrol update {entity} {entity}={id} {params} — applied (mock)."

@mcp.tool()
def scontrol_create(entity: str, params: str) -> str:
    """Create a new Slurm entity (partition, node reservation) (mock)."""
    return f"scontrol create {entity}: {params} — created (mock)."

@mcp.tool()
def scontrol_delete(entity: str, id: str) -> str:
    """Delete a Slurm entity (mock)."""
    return f"scontrol delete {entity} {id} — deleted (mock)."

@mcp.tool()
def scontrol_reconfigure() -> str:
    """Force slurmctld to re-read its configuration (mock)."""
    return "scontrol reconfigure: daemon reconfigured (mock)."


@mcp.tool()
def scontrol_requeue(job_id: str) -> str:
    """Requeue (restart) a failed, cancelled, or completed Slurm job."""
    jobs = _jobs()
    match = next((j for j in jobs if str(j.get("job_id", "")) == str(job_id)), None)
    if not match:
        return f"scontrol: error: Invalid job id {job_id}"
    if match.get("state") == "RUNNING":
        return f"scontrol: error: Job {job_id} is RUNNING — cancel it first."
    return f"Job {job_id} ({match.get('name', '?')}) requeued. New state: PENDING."

@mcp.tool()
def sacctmgr_show(entity: str = "user", params: str = "") -> str:
    """Show Slurm accounting manager entities (mock)."""
    if entity.lower() == "user":
        return "alice  1000  general  normal\nbob    1001  general  normal\ncharlie 1002 general normal"
    if entity.lower() == "qos":
        return "normal  priority=0  MaxJobs=50  MaxWall=7-00:00:00\nhigh    priority=10  MaxJobs=5   MaxWall=1-00:00:00"
    return f"sacctmgr show {entity}: (mock result)"

@mcp.tool()
def sacctmgr_add(entity: str, params: str) -> str:
    """Add a Slurm accounting entity (mock)."""
    return f"sacctmgr add {entity}: {params} — added (mock)."

@mcp.tool()
def sacctmgr_modify(entity: str, where: str, params: str) -> str:
    """Modify a Slurm accounting entity (mock)."""
    return f"sacctmgr modify {entity} where {where} set {params} — modified (mock)."

@mcp.tool()
def sacctmgr_delete(entity: str, params: str) -> str:
    """Delete a Slurm accounting entity (mock)."""
    return f"sacctmgr delete {entity}: {params} — deleted (mock)."

@mcp.tool()
def sreport(report_type: str = "cluster", params: str = "") -> str:
    """Generate Slurm usage report (mock)."""
    jobs = _jobs()
    total_cpu_hours = sum(int(j.get("cpus", 1)) for j in jobs) * 2  # rough estimate
    return (
        f"=== Slurm Usage Report: {report_type} ===\n"
        f"Cluster     : mock-cluster\n"
        f"Period      : last 7 days\n"
        f"Total Jobs  : {len(jobs)}\n"
        f"CPU-hours   : {total_cpu_hours}\n"
        f"Users       : alice, bob, charlie\n"
    )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    # FastMCP SSE transport: /sse for persistent connections, /messages for session posts
    uvicorn.run(
        mcp.sse_app(),
        host=HOST,
        port=PORT,
        log_level="info",
    )
