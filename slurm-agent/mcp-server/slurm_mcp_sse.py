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
from typing import Any

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
def run_analysis(script_id: str) -> str:
    """
    Run a predefined cluster analysis script.

    Available script_ids:
      analyze_my_jobs, analyze_failed_jobs, analyze_gpu_resources,
      analyze_my_efficiency, analyze_my_usage, analyze_pending_jobs,
      analyze_cluster_status
    """
    sid = script_id.strip().lower()

    if sid not in _ANALYSIS_SCRIPTS:
        return (
            f"Unknown script_id '{script_id}'. "
            f"Available: {', '.join(_ANALYSIS_SCRIPTS.keys())}"
        )

    jobs  = _jobs()
    nodes = _nodes()

    running  = [j for j in jobs if j.get("state") == "RUNNING"]
    pending  = [j for j in jobs if j.get("state") == "PENDING"]
    failed   = [j for j in jobs if j.get("state") in ("FAILED", "TIMEOUT")]
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

    return f"Analysis '{script_id}' ran successfully (mock)."


# ── Chart Tool ────────────────────────────────────────────────────────────────

_VALID_CHARTS = {
    "system_health", "cluster_topology", "pending_analysis",
    "resource_map", "job_lifecycle",
    # legacy IDs
    "job_distribution", "node_status", "resource_usage",
    "queue_timeline", "live_dashboard",
}

@mcp.tool()
def generate_chart(chart_id: str) -> str:
    """
    Generate a Mermaid diagram for the cluster.

    Available chart_ids:
      system_health, cluster_topology, pending_analysis,
      resource_map, job_lifecycle
    """
    cid = chart_id.strip().lower()

    jobs  = _jobs()
    nodes = _nodes()

    running  = len([j for j in jobs if j.get("state") == "RUNNING"])
    pending  = len([j for j in jobs if j.get("state") == "PENDING"])
    failed   = len([j for j in jobs if j.get("state") in ("FAILED", "TIMEOUT")])
    completed = len([j for j in jobs if j.get("state") == "COMPLETED"])

    idle_nodes  = len([n for n in nodes if "idle" in n.get("state", "")])
    alloc_nodes = len([n for n in nodes if "alloc" in n.get("state", "") or "mix" in n.get("state", "")])
    down_nodes  = len([n for n in nodes if "down" in n.get("state", "") or "drain" in n.get("state", "")])

    if cid in ("system_health", "job_distribution"):
        mermaid = f"""pie title Job Distribution
    "Running" : {max(running, 0)}
    "Pending" : {max(pending, 0)}
    "Failed"  : {max(failed, 0)}
    "Completed" : {max(completed, 0)}"""

    elif cid in ("cluster_topology", "node_status"):
        node_lines = "\n".join(
            f'    {n["name"]}["{n["name"]}\\n{n["state"]}"]'
            for n in nodes[:8]
        )
        mermaid = f"""graph TD
    Cluster["HPC Cluster"]
{node_lines}
    Cluster --> {nodes[0]['name'] if nodes else 'no-nodes'}"""

    elif cid in ("pending_analysis", "queue_timeline"):
        pending_jobs = [j for j in jobs if j.get("state") == "PENDING"]
        lines = "\n".join(
            f'    J{j["job_id"]}["{j["name"]}\\n({j.get("reason","?")})]'
            for j in pending_jobs[:6]
        )
        mermaid = f"""graph LR
    Queue["Job Queue"]
{lines if lines else "    NoJobs[No pending jobs]"}"""

    elif cid in ("resource_map", "resource_usage"):
        mermaid = f"""pie title Node States
    "Idle"      : {max(idle_nodes, 0)}
    "Allocated" : {max(alloc_nodes, 0)}
    "Down"      : {max(down_nodes, 0)}"""

    elif cid in ("job_lifecycle", "live_dashboard"):
        mermaid = """flowchart LR
    Submit["Job Submit\\n(sbatch)"] --> Pending["PENDING\\n(queued)"]
    Pending --> |"Resources available"| Running["RUNNING"]
    Running --> |"Success"| Completed["COMPLETED"]
    Running --> |"Error"| Failed["FAILED"]
    Running --> |"Time limit"| Timeout["TIMEOUT"]"""

    else:
        return f"Unknown chart_id '{chart_id}'. Available: {', '.join(_VALID_CHARTS)}"

    # Return as MCP resource with mermaid mime type
    return f"```mermaid\n{mermaid.strip()}\n```"


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


# ── Admin Tools (mock — all safe, just return confirmation) ───────────────────

@mcp.tool()
def scontrol_update(entity: str, id: str, params: str) -> str:
    """Update a Slurm entity attribute (mock)."""
    return f"scontrol update {entity} {id}: {params} — applied (mock)."

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

    # FastMCP exposes a Starlette app via .sse_app()
    sse_app = mcp.sse_app()

    uvicorn.run(
        sse_app,
        host=HOST,
        port=PORT,
        log_level="info",
    )
