"""
Slurm MCP Server (SSE transport) — mock or real mode

Usage:
    python slurm_mcp_sse.py                        # mock healthy scenario, port 3002
    python slurm_mcp_sse.py --mock mixed           # mock mixed scenario
    python slurm_mcp_sse.py --real                  # real Slurm commands
    python slurm_mcp_sse.py --real --port 3002

Mock scenarios: healthy | failed | pending | mixed | debug_needed
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
_parser.add_argument("--real", action="store_true", help="Use real Slurm commands instead of mock data")
_parser.add_argument("--port", type=int, default=3002)
_parser.add_argument("--host", default="0.0.0.0")
_known, _ = _parser.parse_known_args()

REAL_MODE: bool = _known.real
SCENARIO: str = _known.mock
PORT: int = _known.port
HOST: str = _known.host

mode_str = "REAL Slurm" if REAL_MODE else f"mock (scenario={SCENARIO})"
logger.info(f"Starting Slurm MCP SSE server — {mode_str}, {HOST}:{PORT}")

mcp = FastMCP("slurm-mcp-mock" if not REAL_MODE else "slurm-mcp-real")


# ── Real-mode helper ──────────────────────────────────────────────────────────

def _run_cmd(cmd: list[str], timeout: int = 30) -> str:
    """Execute a Slurm CLI command and return stdout. Raises on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout.strip()
        if result.returncode != 0:
            err = result.stderr.strip()
            if err:
                return f"Error (exit {result.returncode}): {err}"
            if output:
                return output
            return f"Command failed with exit code {result.returncode}"
        return output or "(no output)"
    except FileNotFoundError:
        return f"Error: '{cmd[0]}' not found. Is Slurm installed?"
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout}s"


# ── Mutable in-memory cluster state (mock mode) ───────────────────────────────
# All tools read/write _STATE so actions have real visible side-effects:
#   scancel  → removes jobs from _STATE.jobs
#   sbatch   → appends new job to _STATE.jobs
#   hold/release → toggles job state between PENDING / HOLD
#   scontrol_update → patches job fields in place

import copy
import time as _time

class _ClusterState:
    """Single shared mutable cluster state for the mock server.
    Initialised once from MOCK_JOBS/MOCK_NODES at startup.
    All tool functions operate on this instance.
    """

    def __init__(self):
        self._jobs: list[dict] = []
        self._nodes: list[dict] = []
        self._next_id: int = 2000
        self._log: list[str] = []    # action history for transparency
        self._initialized = False

    def _ensure_init(self):
        if not self._initialized:
            import copy
            self._jobs  = copy.deepcopy(MOCK_JOBS.get(SCENARIO, []))
            self._nodes = copy.deepcopy(MOCK_NODES.get(SCENARIO, []))
            # Determine next job id from existing max
            existing_ids = [int(j["job_id"]) for j in self._jobs if str(j.get("job_id","")).isdigit()]
            self._next_id = max(existing_ids, default=1000) + 1
            self._initialized = True

    def jobs(self) -> list[dict]:
        self._ensure_init()
        return self._jobs

    def nodes(self) -> list[dict]:
        self._ensure_init()
        return self._nodes

    def cancel(self, ids: list[str]) -> tuple[list[str], list[str]]:
        """Mark jobs as CANCELLED. Returns (cancelled_ids, not_found_ids)."""
        self._ensure_init()
        cancelled, not_found = [], []
        for jid in ids:
            matched = [j for j in self._jobs if str(j.get("job_id","")) == jid
                       or str(j.get("job_id","")).split("_")[0] == jid]
            if matched:
                for j in matched:
                    prev = j["state"]
                    j["state"] = "CANCELLED"
                    j["time"]  = j.get("time", "0:00")
                    cancelled.append(str(j["job_id"]))
                    self._log.append(f"[{_stamp()}] CANCEL job {j['job_id']} ({prev} → CANCELLED)")
            else:
                not_found.append(jid)
        return cancelled, not_found

    def hold(self, jid: str) -> str:
        self._ensure_init()
        jobs = [j for j in self._jobs if str(j.get("job_id","")) == jid]
        if not jobs:
            return f"scontrol: error: Invalid job id specified: {jid}"
        j = jobs[0]
        if j["state"] not in ("PENDING",):
            return f"scontrol: error: Job {jid} cannot be held — state is {j['state']}"
        j["state"] = "HOLD"
        j["reason"] = "JobHeldUser"
        self._log.append(f"[{_stamp()}] HOLD job {jid}")
        return f"Job {jid} held."

    def release(self, jid: str) -> str:
        self._ensure_init()
        jobs = [j for j in self._jobs if str(j.get("job_id","")) == jid]
        if not jobs:
            return f"scontrol: error: Invalid job id specified: {jid}"
        j = jobs[0]
        if j["state"] != "HOLD":
            return f"scontrol: error: Job {jid} is not held — state is {j['state']}"
        j["state"] = "PENDING"
        j.pop("reason", None)
        self._log.append(f"[{_stamp()}] RELEASE job {jid}")
        return f"Job {jid} released."

    def requeue(self, jid: str) -> str:
        self._ensure_init()
        jobs = [j for j in self._jobs if str(j.get("job_id","")) == jid]
        if not jobs:
            return f"scontrol: error: Invalid job id specified: {jid}"
        j = jobs[0]
        prev = j["state"]
        j["state"] = "PENDING"
        j["time"] = "0:00"
        j.pop("exit_code", None)
        self._log.append(f"[{_stamp()}] REQUEUE job {jid} ({prev} → PENDING)")
        return f"Job {jid} requeued."

    def update(self, jid: str, params: str) -> str:
        self._ensure_init()
        jobs = [j for j in self._jobs if str(j.get("job_id","")) == jid]
        if not jobs:
            return f"scontrol: error: Invalid job id specified: {jid}"
        j = jobs[0]
        import re as _re
        changes = []
        for m in _re.finditer(r"([\w]+)=(\S+)", params):
            key, val = m.group(1).lower(), m.group(2)
            if key in ("timelimit", "time"):
                j["time"] = val; changes.append(f"TimeLimit={val}")
            elif key in ("partition",):
                j["partition"] = val; changes.append(f"Partition={val}")
            elif key in ("numcpus", "cpus"):
                j["cpus"] = val; changes.append(f"NumCPUs={val}")
            elif key in ("minmemorynode", "mem"):
                j["mem"] = val; changes.append(f"MinMemory={val}")
            elif key in ("numnodes", "nodes"):
                j["nodes"] = val; changes.append(f"NumNodes={val}")
        self._log.append(f"[{_stamp()}] UPDATE job {jid}: {params}")
        return f"Job {jid} updated: {', '.join(changes) or params}"

    def submit(self, script_name: str, flags: str = "", user: str = "user") -> str:
        self._ensure_init()
        import re as _re
        jid = str(self._next_id)
        self._next_id += 1
        partition = "cpu"
        m = _re.search(r"--partition[= ](\S+)", flags)
        if m: partition = m.group(1)
        cpus = "4"
        m = _re.search(r"--cpus-per-task[= ](\d+)", flags)
        if m: cpus = m.group(1)
        mem = "4G"
        m = _re.search(r"--mem[= ](\S+)", flags)
        if m: mem = m.group(1)
        nodes = "1"
        m = _re.search(r"--nodes[= ](\d+)", flags)
        if m: nodes = m.group(1)
        array_suffix = ""
        m = _re.search(r"--array[= ](\S+)", flags)
        if m: array_suffix = f"_[{m.group(1)}]"; jid = f"{jid}{array_suffix}"
        job = {
            "job_id": jid,
            "name":   os.path.basename(script_name).replace(".sh",""),
            "user":   user,
            "state":  "PENDING",
            "time":   "0:00",
            "nodes":  nodes,
            "cpus":   cpus,
            "mem":    mem,
            "partition": partition,
            "reason": "Priority",
        }
        dep_m = _re.search(r"--dependency[= ](\S+)", flags)
        if dep_m: job["reason"] = f"Dependency:{dep_m.group(1)}"
        self._jobs.append(job)
        self._log.append(f"[{_stamp()}] SUBMIT {script_name} → job {jid} (PENDING, {partition})")
        return f"Submitted batch job {jid}"

    def history(self) -> str:
        return "\n".join(self._log[-50:]) if self._log else "(no actions taken yet)"

    def reset(self, scenario: str, source_state: dict | None = None) -> str:
        """Reset mock state to scenario defaults, optionally overridden by source_state.
        source_state follows evaluation dataset shape: {jobs:{...}, nodes:{...}}.
        """
        global SCENARIO
        SCENARIO = scenario

        # Start from scenario templates
        tmpl_jobs = copy.deepcopy(MOCK_JOBS.get(scenario, []))
        tmpl_nodes = copy.deepcopy(MOCK_NODES.get(scenario, []))

        if source_state:
            src_jobs = source_state.get("jobs", {}) or {}
            src_nodes = source_state.get("nodes", {}) or {}

            # Build index from templates so we keep realistic defaults
            t_jobs_by_id = {str(j.get("job_id")): j for j in tmpl_jobs}
            t_nodes_by_name = {str(n.get("name")): n for n in tmpl_nodes}

            jobs = []
            for jid, spec in src_jobs.items():
                base = copy.deepcopy(t_jobs_by_id.get(str(jid), {
                    "job_id": str(jid),
                    "name": f"job_{jid}",
                    "user": "user",
                    "state": "PENDING",
                    "time": "0:00",
                    "nodes": 1,
                    "cpus": 1,
                    "mem": "1G",
                    "partition": "cpu",
                }))
                base["job_id"] = str(jid)
                for k, v in spec.items():
                    base[k] = v
                jobs.append(base)

            nodes = []
            for name, spec in src_nodes.items():
                base = copy.deepcopy(t_nodes_by_name.get(str(name), {
                    "name": str(name),
                    "state": "idle",
                    "cpus": "0/32",
                    "mem": "0/128G",
                    "partition": "cpu",
                    "gres": "",
                }))
                base["name"] = str(name)
                for k, v in spec.items():
                    base[k] = v
                nodes.append(base)

            self._jobs = jobs
            self._nodes = nodes
        else:
            self._jobs = tmpl_jobs
            self._nodes = tmpl_nodes

        existing_ids = [int(j["job_id"]) for j in self._jobs if str(j.get("job_id", "")).isdigit()]
        self._next_id = max(existing_ids, default=1000) + 1
        self._initialized = True
        self._log.append(f"[{_stamp()}] RESET state to scenario={scenario} jobs={len(self._jobs)} nodes={len(self._nodes)}")
        return f"reset done: scenario={scenario}, jobs={len(self._jobs)}, nodes={len(self._nodes)}"


def _stamp() -> str:
    import datetime
    return datetime.datetime.now().strftime("%H:%M:%S")


# Single shared instance
_STATE = _ClusterState()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _jobs():
    return _STATE.jobs()

def _nodes():
    return _STATE.nodes()


def _real_jobs() -> list[dict]:
    """Parse real squeue output into the same dict format as mock data."""
    raw = _run_cmd(["squeue", "--noheader",
                    "--format=%i|%j|%u|%T|%M|%D|%C|%m|%P|%r|%e"])
    jobs = []
    for line in raw.strip().split("\n"):
        if not line.strip() or "error" in line.lower():
            continue
        parts = line.strip().split("|")
        if len(parts) < 9:
            continue
        jobs.append({
            "job_id": parts[0].strip(),
            "name": parts[1].strip(),
            "user": parts[2].strip(),
            "state": parts[3].strip(),
            "time": parts[4].strip(),
            "nodes": parts[5].strip(),
            "cpus": parts[6].strip(),
            "mem": parts[7].strip(),
            "partition": parts[8].strip(),
            "reason": parts[9].strip() if len(parts) > 9 else "",
            "exit_code": "0:0",
        })
    return jobs


def _real_nodes() -> list[dict]:
    """Parse real sinfo output into the same dict format as mock data.
    Deduplicates nodes that appear once per partition."""
    raw = _run_cmd(["sinfo", "--noheader",
                    "--format=%N|%T|%C|%m|%P|%G|%E"])
    seen = {}  # name → dict (keep first occurrence, merge partitions)
    for line in raw.strip().split("\n"):
        if not line.strip() or "error" in line.lower():
            continue
        parts = line.strip().split("|")
        if len(parts) < 5:
            continue
        name = parts[0].strip()
        if name in seen:
            # Merge partition names
            seen[name]["partition"] += "," + parts[4].strip().rstrip("*")
            continue
        seen[name] = {
            "name": name,
            "state": parts[1].strip(),
            "cpus": parts[2].strip(),  # A/I/O/T format
            "mem": parts[3].strip(),
            "partition": parts[4].strip().rstrip("*"),
            "gres": parts[5].strip() if len(parts) > 5 else "",
            "reason": parts[6].strip() if len(parts) > 6 and parts[6].strip() not in ("(null)", "none") else "",
        }
    return list(seen.values())


def _get_jobs():
    """Return job list — real Slurm data or mock depending on mode."""
    return _real_jobs() if REAL_MODE else _jobs()


def _get_nodes():
    """Return node list — real Slurm data or mock depending on mode."""
    return _real_nodes() if REAL_MODE else _nodes()

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
    """Show current job queue with JOBID, name, user, state, time, resources.
    Filter: user="alice", state="RUNNING|PENDING|FAILED|COMPLETED", partition="gpu".
    Returns pipe-delimited table."""
    if REAL_MODE:
        cmd = [
            "squeue",
            "--format=%i|%j|%u|%T|%M|%D|%C|%m|%P",
            "--noheader",
        ]
        if user: cmd += ["--user", user]
        if state: cmd += ["--state", state]
        if partition: cmd += ["--partition", partition]
        raw = _run_cmd(cmd)
        if not raw or raw == "(no output)":
            return "No jobs in queue."
        # Add a header for clarity
        header = "JOBID|NAME|USER|STATE|TIME|NODES|CPUS|MIN_MEM|PARTITION"
        return header + "\n" + raw
    jobs = _jobs()
    if user:
        jobs = [j for j in jobs if j.get("user", "").lower() == user.lower()]
    if state:
        jobs = [j for j in jobs if j.get("state", "").upper() == state.upper()]
    if partition:
        jobs = [j for j in jobs if j.get("partition", "").lower() == partition.lower()]
    return _fmt_jobs(jobs)


@mcp.tool()
def cluster_resources() -> str:
    """Show a concise summary of ALL cluster resources: partitions, nodes, CPUs, memory, GPUs.

    Use this BEFORE submitting jobs to check what resources are actually available.
    Returns a structured table with per-node details so you can pick correct
    --partition, --gres, --mem, --cpus-per-task values.

    No arguments needed — always returns the full cluster picture."""
    if REAL_MODE:
        import re as _re
        lines = []

        # ── Partition overview ──
        raw = _run_cmd(["sinfo", "--noheader",
                        "--format=%P|%a|%l|%D|%C|%m|%G|%T"])
        lines.append("=== PARTITIONS ===")
        lines.append(f"{'PARTITION':<12} {'AVAIL':<6} {'TIMELIMIT':<12} {'NODES':<6} {'CPUS(A/I/O/T)':<18} {'MEM(MB)':<10} {'GRES':<20} {'STATE'}")
        lines.append("-" * 110)
        for row in raw.strip().splitlines():
            parts = row.split("|")
            if len(parts) >= 8:
                lines.append(
                    f"{parts[0]:<12} {parts[1]:<6} {parts[2]:<12} {parts[3]:<6} "
                    f"{parts[4]:<18} {parts[5]:<10} {parts[6]:<20} {parts[7]}"
                )

        # ── Per-node detail ──
        raw_nodes = _run_cmd(["sinfo", "--Node", "--noheader",
                              "--format=%N|%P|%T|%c|%m|%G|%O"])
        lines.append("")
        lines.append("=== NODES (detailed) ===")
        lines.append(f"{'NODE':<18} {'PARTITION':<12} {'STATE':<12} {'CPUS':<6} {'MEM(MB)':<10} {'GRES':<24} {'CPU_LOAD'}")
        lines.append("-" * 110)
        seen = set()
        for row in raw_nodes.strip().splitlines():
            parts = row.split("|")
            if len(parts) >= 7:
                node_key = parts[0].strip()
                if node_key in seen:
                    continue
                seen.add(node_key)
                lines.append(
                    f"{parts[0]:<18} {parts[1]:<12} {parts[2]:<12} {parts[3]:<6} "
                    f"{parts[4]:<10} {parts[5]:<24} {parts[6]}"
                )

        # ── GRES summary (what the agent really needs) ──
        raw_gres = _run_cmd(["sinfo", "--noheader", "--format=%N|%G"])
        gres_map: dict[str, str] = {}
        for row in raw_gres.strip().splitlines():
            parts = row.split("|", 1)
            if len(parts) == 2 and parts[1].strip() and parts[1].strip() != "(null)":
                gres_map[parts[0].strip()] = parts[1].strip()

        if gres_map:
            lines.append("")
            lines.append("=== GPU SUMMARY ===")
            for node_name, gres in sorted(gres_map.items()):
                # Parse gres string like "gpu:rtx5070ti:1" → type, count
                for g in gres.split(","):
                    g = g.strip()
                    gparts = g.split(":")
                    if len(gparts) >= 3:
                        lines.append(f"  {node_name}: {gparts[1]} x {gparts[2]} (--gres={gparts[0]}:{gparts[2]} max)")
                    elif len(gparts) == 2:
                        lines.append(f"  {node_name}: gpu x {gparts[1]} (--gres=gpu:{gparts[1]} max)")
            lines.append("")
            lines.append("⚠ When submitting jobs, --gres count must NOT exceed the per-node max above.")

        return "\n".join(lines)

    # Mock mode
    nodes = _nodes()
    partitions: dict[str, list] = {}
    for n in nodes:
        p = n.get("partition", "unknown")
        partitions.setdefault(p, []).append(n)

    lines = ["=== CLUSTER RESOURCES ===", ""]
    for pname, pnodes in sorted(partitions.items()):
        lines.append(f"Partition: {pname}")
        for n in pnodes:
            cpus = n.get("cpus", "?")
            mem = n.get("mem", "?")
            gres = n.get("gres", "(null)")
            lines.append(f"  {n['name']}: state={n['state']}  cpus={cpus}  mem={mem}  gres={gres}")
        lines.append("")

    lines.append("⚠ When submitting jobs, --gres count must NOT exceed per-node max.")
    return "\n".join(lines)


@mcp.tool()
def sinfo(partition: str = "", node: str = "") -> str:
    """Show cluster partition and node status (allocated/idle/down counts, per-node CPUs/memory/GPUs).
    Filter: partition="gpu", node="node01"."""
    if REAL_MODE:
        cmd = ["sinfo", "--format=%P|%a|%l|%D|%T|%N|%C|%m|%G"]
        if partition: cmd += ["--partition", partition]
        if node: cmd += ["--nodes", node]
        return _run_cmd(cmd)
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
    """Query historical job accounting records for completed/failed/cancelled/timed-out jobs.
    Filter: user, state="FAILED|COMPLETED|CANCELLED|TIMEOUT", starttime="now-7days" or "2024-01-01".
    Returns pipe-delimited table with ExitCode, elapsed time, resources."""
    if REAL_MODE:
        cmd = ["sacct", f"--format={format}", "--parsable2", "--noheader"]
        if user: cmd += ["--user", user]
        if state: cmd += ["--state", state]
        if starttime: cmd += ["--starttime", starttime]
        if endtime: cmd += ["--endtime", endtime]
        raw = _run_cmd(cmd)
        if not raw or raw == "(no output)":
            return "No accounting records found."
        header = format.replace(",", "|")
        return header + "\n" + raw
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
    """Show detailed Slurm entity info — more fields than squeue/sinfo.
    entity="job"|"node"|"partition", id=job ID or node name.
    Returns key=value pairs: Reason, AllocTRES, StdErr path, etc."""
    if REAL_MODE:
        cmd = ["scontrol", "show", entity]
        if id: cmd.append(id)
        return _run_cmd(cmd)
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
    """Submit a SINGLE batch job script to Slurm.

    script (REQUIRED): path to one .sh file, e.g. "/tmp/slurm_uploads/job.sh".
                       Must be a single file — call sbatch once per script.
    flags  (optional): extra #SBATCH flags for THIS script only.
                       Use --dependency=afterok:<job_id> to chain jobs.
                       Example: "--partition=gpu --gres=gpu:1 --dependency=afterok:1234"

    To submit a pipeline, call sbatch once per stage in order:
      1. sbatch(data_download.sh)          → job_id=1001
      2. sbatch(preprocess.sh, "--dependency=afterok:1001")
      3. sbatch(train.sh,      "--dependency=afterok:1002 --partition=gpu")
      4. sbatch(evaluate.sh,   "--dependency=afterany:1003")

    Returns: "Submitted batch job <job_id>" on success, or an error string."""
    raw = script.strip()
    if not raw:
        return "sbatch: error: 'script' argument is required. Provide a single file path."

    # Reject multi-script comma lists — agent must call once per script
    if "," in raw and "\n" not in raw:
        paths = [s.strip() for s in raw.split(",") if s.strip()]
        if len(paths) > 1:
            return (
                "sbatch: error: Only one script per call is allowed. "
                f"Submit each script separately with its own dependency flag. "
                f"Got {len(paths)} paths: {raw}"
            )

    return _sbatch_single(raw, flags)


def _sanitize_flags(flags: str, script_path: str) -> str:
    """Remove from `flags` any options already present as #SBATCH directives in the script.

    This prevents the agent from overriding (e.g.) --gres=gpu:1 in the script header
    with --gres=gpu:2 in flags, which would cause a submission error.
    Dependency flags (--dependency) are always kept regardless.
    """
    import re as _re

    # Keys that must NOT be overridden by flags when they're in the script
    _SCRIPT_WINS = {"--gres", "--mem", "--partition", "--time", "--cpus-per-task",
                    "--ntasks", "--nodes", "--exclusive", "--mem-per-cpu"}

    # Parse #SBATCH directives from the script
    script_opts: set[str] = set()
    try:
        with open(script_path) as f:
            for line in f:
                line = line.strip()
                if not line.startswith("#SBATCH"):
                    continue
                m = _re.match(r"#SBATCH\s+(--[\w-]+)", line)
                if m:
                    script_opts.add(m.group(1))
    except OSError:
        return flags  # can't read script, leave flags unchanged

    # Tokenise flags and drop any key whose long form is already in the script
    kept = []
    tokens = flags.split()
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        key = tok.split("=")[0]  # e.g. "--gres" from "--gres=gpu:1"
        if key in _SCRIPT_WINS and key in script_opts:
            # Skip this flag (and its detached value if applicable)
            if "=" not in tok and i + 1 < len(tokens):
                i += 2  # skip "key value"
            else:
                i += 1  # skip "key=value"
        else:
            kept.append(tok)
            i += 1

    return " ".join(kept)


def _sbatch_single(script: str, flags: str = "") -> str:
    """Submit a single script to Slurm."""
    stripped = script.strip()

    # ── Sanitise flags: drop any that duplicate #SBATCH directives in the script ──
    is_path = (
        (stripped.startswith("/") or stripped.startswith("~/") or stripped.startswith("./"))
        and "\n" not in stripped
    )
    if flags and is_path:
        flags = _sanitize_flags(flags, os.path.expanduser(stripped))

    if REAL_MODE:
        is_path = (
            (stripped.startswith("/") or stripped.startswith("~/") or stripped.startswith("./"))
            and "\n" not in stripped
        )

        if is_path:
            expanded = os.path.expanduser(stripped)
            if not os.path.isfile(expanded):
                return f"sbatch: error: File not found: {expanded}"
            script_path = expanded
            tmp_path = None
        else:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(stripped)
                script_path = f.name
                tmp_path = f.name

        cmd = ["sbatch"]
        if flags:
            cmd += flags.split()
        cmd.append(script_path)
        result = _run_cmd(cmd)

        if tmp_path:
            os.unlink(tmp_path)
        return result

    # Mock mode: real stateful submission
    return _STATE.submit(stripped, flags)


@mcp.tool()
def scancel(job_id: str, user: str = "") -> str:
    """Cancel one or more Slurm jobs.
    job_id (REQUIRED): a single job ID, array parent ID, or comma-separated IDs.
    Examples: "12345", "12345_[1-5]", "100,101,102".
    For array jobs, pass the parent ID (e.g. "7") to cancel all tasks at once.
    Returns summary of cancelled jobs."""
    # Normalize: split comma-separated into individual IDs
    ids = [i.strip() for i in job_id.split(",") if i.strip()]
    if not ids:
        return "scancel: error: No job IDs specified"

    if REAL_MODE:
        cmd = ["scancel"] + ids
        if user:
            cmd += ["--user", user]
        result = _run_cmd(cmd)
        if "error" not in result.lower():
            return f"Jobs {', '.join(ids)} cancelled successfully."
        return result

    # Mock mode: stateful cancel — jobs are actually marked CANCELLED
    cancelled, not_found = _STATE.cancel(ids)
    parts = []
    if cancelled:
        parts.append(f"Jobs {', '.join(cancelled)} cancelled successfully.")
    if not_found:
        parts.append(f"scancel: error: Invalid job id(s): {', '.join(not_found)}")
    return " ".join(parts) if parts else f"Job {job_id} cancelled successfully."


@mcp.tool()
def scontrol_hold(job_id: str) -> str:
    """Hold a pending job so it won't be scheduled until released.
    job_id (REQUIRED): the numeric job ID. Only works on PENDING jobs."""
    if REAL_MODE:
        result = _run_cmd(["scontrol", "hold", job_id])
        if "error" not in result.lower():
            return f"Job {job_id} held."
        return result
    return _STATE.hold(job_id)


@mcp.tool()
def scontrol_release(job_id: str) -> str:
    """Release a held job so it can be scheduled again.
    job_id (REQUIRED): the numeric job ID of a held job."""
    if REAL_MODE:
        result = _run_cmd(["scontrol", "release", job_id])
        if "error" not in result.lower():
            return f"Job {job_id} released."
        return result
    return _STATE.release(job_id)


@mcp.tool()
def srun(command: str, nodes: int = 1, cpus: int = 1, partition: str = "cpu") -> str:
    """Run a command interactively on the cluster via srun (allocates then executes).
    command (REQUIRED): the shell command. nodes/cpus/partition are optional resource controls."""
    if REAL_MODE:
        cmd = ["srun", "-N", str(nodes), "-c", str(cpus), "-p", partition, "--"] + command.split()
        return _run_cmd(cmd, timeout=60)
    return f"[mock srun] {command} — would run on {nodes} node(s), {cpus} CPU(s), partition={partition}"


@mcp.tool()
def salloc(nodes: int = 1, cpus: int = 1, partition: str = "cpu", time: str = "01:00:00") -> str:
    """Allocate interactive resources on the cluster without running a command.
    Returns a job allocation ID. Use for interactive sessions."""
    if REAL_MODE:
        return _run_cmd(["salloc", "-N", str(nodes), "-c", str(cpus), "-p", partition, "-t", time], timeout=10)
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

    # ── Real mode: compose analysis from actual Slurm commands ──
    if REAL_MODE:
        if sid == "analyze_cluster_status":
            info = _run_cmd(["sinfo", "--format=%P %a %D %T %N", "--noheader"])
            q = _run_cmd(["squeue", "--format=%i %j %u %T %M %D", "--noheader"])
            return f"=== Cluster Status ===\n\nPartitions & Nodes:\n{info}\n\nJob Queue:\n{q}"
        elif sid == "analyze_failed_jobs":
            return _run_cmd(["sacct", "--state=FAILED,TIMEOUT,NODE_FAIL,OUT_OF_MEMORY",
                             "--format=JobID,JobName,User,State,ExitCode,Elapsed,NodeList",
                             "--parsable2", "--starttime=now-7days"])
        elif sid == "analyze_pending_jobs":
            return _run_cmd(["squeue", "--state=PENDING",
                             "--format=%i %j %u %T %r %P %D %C", "--noheader"])
        elif sid == "analyze_gpu_resources":
            info = _run_cmd(["sinfo", "--format=%N %G %C %m %T", "--noheader", "-p", "gpu"])
            q = _run_cmd(["squeue", "-p", "gpu", "--format=%i %j %u %T %b", "--noheader"])
            return f"=== GPU Resources ===\nNodes:\n{info}\n\nGPU Jobs:\n{q}"
        elif sid == "analyze_node_health":
            return _run_cmd(["sinfo", "--format=%N %T %C %m %G %E", "--noheader"])
        elif sid == "analyze_job_efficiency":
            running = _run_cmd(["squeue", "--state=RUNNING", "--format=%i", "--noheader"]).split()
            if not running:
                return "No running jobs to analyze efficiency."
            lines = ["=== Job Efficiency (live sstat) ==="]
            for jid in running[:5]:
                jid = jid.strip()
                if not jid: continue
                stat = _run_cmd(["sstat", "--format=JobID,AveCPU,AveRSS,MaxRSS,AveDiskRead,AveDiskWrite",
                                 "--parsable2", "--noheader", "-j", f"{jid}.batch"])
                lines.append(f"Job {jid}: {stat}")
            return "\n".join(lines)
        elif sid in ("analyze_my_jobs", "analyze_my_usage", "analyze_my_efficiency"):
            user = os.environ.get("USER", os.environ.get("SLURM_USER", ""))
            if not user:
                return "Cannot determine current user. Set USER env var."
            q = _run_cmd(["squeue", "--user", user, "--format=%i %j %T %M %D %C %P", "--noheader"])
            acct = _run_cmd(["sacct", "--user", user, "--starttime=now-7days",
                             "--format=JobID,JobName,State,ExitCode,Elapsed,NCPUs",
                             "--parsable2", "--noheader"])
            return f"=== My Jobs ({user}) ===\n\nRunning/Pending:\n{q}\n\nRecent History:\n{acct}"
        return f"Unknown script_id '{script_id}'."

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
    jobs  = _get_jobs()
    nodes = _get_nodes()
    mode_label = "live" if REAL_MODE else SCENARIO

    # ── shared micro-helpers ────────────────────────────────────────────────
    def _cpu_pair(s: str):
        """Parse CPU string. Supports A/T (mock) and A/I/O/T (real sinfo)."""
        p = s.split("/")
        try:
            if len(p) == 4:  # A/I/O/T from real sinfo
                return int(p[0]), int(p[3])
            return int(p[0]), int(p[-1])
        except: return 0, 0

    def _mem_gb(s: str) -> float:
        """Parse memory string. Handles '64G', '1024M', '63000' (MB from sinfo)."""
        s = (s or "0").strip().upper()
        try:
            if s.endswith("T"): return float(s[:-1]) * 1024
            if s.endswith("G"): return float(s[:-1])
            if s.endswith("M"): return float(s[:-1]) / 1024
            # Plain number — assume MB (real sinfo format)
            val = float(s)
            if val > 1024:
                return val / 1024  # MB → GB
            return val  # Already in GB or small value
        except: pass
        return 0.0

    def _elapsed_min(t: str) -> int:
        """Parse elapsed time to minutes. Handles D-HH:MM:SS, HH:MM:SS, MM:SS, M:SS."""
        t = (t or "0:01").strip()
        try:
            days = 0
            if "-" in t:
                d, t = t.split("-", 1)
                days = int(d)
            p = t.split(":")
            if len(p) >= 3:
                return days * 1440 + int(p[0]) * 60 + int(p[1])
            if len(p) == 2:
                return days * 1440 + int(p[0])  # MM:SS → MM
        except: pass
        return 1

    def _hhmm(m: int) -> str:
        m = max(0, m)
        return f"{m // 60:02d}:{m % 60:02d}"

    # ── system_health: xychart-beta utilization bars ───────────────────────
    if cid == "system_health":
        cpu_a = cpu_t = 0
        mem_t_gb = 0.0
        mem_a_gb = 0.0
        gpu_n = gpu_a = down_n = 0
        for n in nodes:
            ca, ct = _cpu_pair(n.get("cpus", "0/0"))
            cpu_a += ca; cpu_t += ct
            # Total memory from node
            mp = n.get("mem", "0").split("/")
            mem_t_gb += _mem_gb(mp[-1])  # Total is always last part (or only part)
            if len(mp) > 1:
                mem_a_gb += _mem_gb(mp[0])  # Mock format: alloc/total
            st = n.get("state", "")
            if n.get("gres", ""):
                gpu_n += 1
                if "alloc" in st or "mix" in st: gpu_a += 1
            if "down" in st or "drain" in st: down_n += 1

        # In real mode, estimate allocated memory from scontrol AllocTRES
        if REAL_MODE and mem_a_gb == 0.0:
            import re as _re
            alloc_raw = _run_cmd(["squeue", "--state=RUNNING", "--noheader",
                                  "--format=%i"])
            for jid in alloc_raw.strip().split("\n"):
                jid = jid.strip()
                if not jid:
                    continue
                info = _run_cmd(["scontrol", "show", "job", jid])
                m = _re.search(r"AllocTRES=.*?mem=(\d+[A-Z]?)", info)
                if m:
                    mem_a_gb += _mem_gb(m.group(1))

        cpu_pct  = round(cpu_a / cpu_t * 100)  if cpu_t  else 0
        mem_pct  = round(mem_a_gb / mem_t_gb * 100) if mem_t_gb else 0
        gpu_pct  = round(gpu_a / gpu_n * 100)  if gpu_n  else 0
        heal_pct = round((len(nodes) - down_n) / len(nodes) * 100) if nodes else 100

        return (
            f"xychart-beta\n"
            f"    title \"Cluster Utilization — {mode_label}\"\n"
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
            f"    Cluster[\"HPC Cluster — {mode_label}\\n{len(nodes)} nodes total\"]"
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
            "Nodes required for job are DOWN, DRAINED or reserved for jobs in higher priority partitions": "NodesDown",
            "None": "Starting",
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
            f"    title \"CPU Usage by User — {mode_label}\"\n"
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


# ── File Read Tool ────────────────────────────────────────────────────────────

@mcp.tool()
def read_file(file_path: str) -> str:
    """Read a text file from the filesystem (max 1MB).
    file_path (REQUIRED): absolute path like /home/user/job.sh.
    Returns file contents as plain text, or error if not found."""
    import os
    resolved = os.path.realpath(file_path)
    if not os.path.exists(resolved):
        return f"Error: File not found: {file_path}"
    if not os.path.isfile(resolved):
        return f"Error: Not a file: {file_path}"
    try:
        size = os.path.getsize(resolved)
        if size > 1_000_000:  # 1MB limit
            return f"Error: File too large ({size} bytes). Max 1MB."
        with open(resolved, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


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
    """Show Slurm scheduler diagnostics: main/backfill cycle times, queue depth, RPC rates.
    No args. Good for health checks and performance analysis."""
    if REAL_MODE:
        return _run_cmd(["sdiag"])
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
    """Show priority factors for pending jobs (age, fairshare, QOS, job size).
    Higher priority = scheduled sooner. Filter by user or partition."""
    if REAL_MODE:
        cmd = ["sprio", "--format=%i|%u|%P|%Y|%A|%F|%Q|%S|%N", "--noheader"]
        if user: cmd += ["--user", user]
        if partition: cmd += ["--partition", partition]
        raw = _run_cmd(cmd)
        if not raw or raw == "(no output)":
            return "No pending jobs with priority info."
        header = "JOBID|USER|PARTITION|PRIORITY|AGE|FAIRSHARE|QOS|SIZE|NICE"
        return header + "\n" + raw
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
    """Show real-time resource stats for a RUNNING job (CPU%, RSS memory, disk I/O).
    job_id (REQUIRED). Only works on RUNNING jobs; use sacct for completed ones."""
    if REAL_MODE:
        return _run_cmd(["sstat", "--format=JobID,AveCPU,AveRSS,MaxRSS,AveVMSize,AveDiskRead,AveDiskWrite",
                         "--parsable2", "-j", f"{job_id}.batch"])
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
# Format: "exit_code:signal" → explanation + fix
_EXIT_HINTS: dict[str, str] = {
    # Normal
    "0:0":   "COMPLETED normally.",
    # Application errors (exit code > 0, signal 0)
    "1:0":   "Application exit code 1 — generic failure. Check stderr/stdout for Python tracebacks or app errors.",
    "2:0":   "Misuse of shell command (bad syntax, missing argument). Check the job script shebang and commands.",
    "3:0":   "Cannot execute (permission denied or not a script). Check `chmod +x` and shebang line.",
    "126:0": "Command invoked cannot execute — permission problem or not an executable. Check `chmod +x`.",
    "127:0": "Command not found — missing binary or module not loaded. Add `module load` to your script.",
    "128:0": "Invalid exit argument — script used `exit` with non-integer or negative.",
    # Signal-killed jobs (exit 0, signal > 0) — signal = 128 + N convention
    "0:1":   "SIGHUP — terminal hangup. Job lost connection to controlling terminal.",
    "0:2":   "SIGINT — interrupt (Ctrl+C). Job was interrupted, possibly by scancel --signal=INT.",
    "0:3":   "SIGQUIT — quit with core dump. Check for core file.",
    "0:4":   "SIGILL — illegal instruction. Binary incompatible with CPU architecture.",
    "0:6":   "SIGABRT — abort. Application called abort(), often from assertion failure.",
    "0:7":   "SIGBUS — bus error. Memory alignment issue or I/O error on memory-mapped file.",
    "0:8":   "SIGFPE — floating point exception. Division by zero or overflow.",
    "0:9":   "SIGKILL — killed. OOM-killer or admin killed the job. Increase --mem.",
    "0:11":  "SIGSEGV — segfault. Memory corruption, bad pointer, or stack overflow. Check with valgrind.",
    "0:13":  "SIGPIPE — broken pipe. Process wrote to a closed pipe/socket.",
    "0:14":  "SIGALRM — alarm timer expired.",
    "0:15":  "SIGTERM — terminated. Walltime exceeded or scancel. Increase --time or checkpoint.",
    "0:18":  "SIGCONT — continued (informational).",
    "0:24":  "SIGXCPU — CPU time limit exceeded. Increase --time or reduce computation.",
    "0:25":  "SIGXFSZ — file size limit exceeded. Reduce output size or request more disk.",
    "0:31":  "SIGSYS — bad system call. Seccomp/sandbox violation.",
    # Combined patterns (common in practice)
    "137:0": "OOM-killed (SIGKILL=9, 128+9=137). Increase --mem; current allocation: {mem}.",
    "139:0": "Segfault (SIGSEGV=11, 128+11=139). Memory bug. Debug with valgrind/gdb.",
    "140:0": "SIGBUS (128+7+5). Bus error — bad memory access or shared FS issue.",
    "143:0": "Walltime exceeded (SIGTERM=15, 128+15=143). Increase --time or add checkpointing.",
    "134:0": "SIGABRT (128+6=134). Assertion failure or abort() call in application.",
    "130:0": "SIGINT (128+2=130). Job interrupted — user or scancel.",
    # Slurm-specific signals
    "1:53":  "Node failure (Slurm signal 53). Hardware or network issue. Requeue: scontrol_requeue {job_id}.",
    "0:53":  "Node failure during job execution. Requeue the job.",
    "7:0":   "Bus error — often memory corruption or file I/O on shared filesystem. Check lustre/gpfs health.",
}

# Pending-reason hints — comprehensive from Slurm docs
_PENDING_HINTS: dict[str, str] = {
    # Most common
    "Resources":               "Waiting for matching nodes to free up. Reduce --nodes/--cpus/--mem or wait.",
    "Priority":                "Lower priority than other pending jobs. Wait, or ask admin to boost via `sprio`.",
    "Dependency":              "Waiting on parent job. Check dependency chain: `scontrol show job {job_id}`.",
    "DependencyNeverSatisfied":"Dependency can never be met (parent failed/cancelled). Cancel or remove dependency.",
    "None":                    "Job is being evaluated — should move to RUNNING shortly.",
    "BeginTime":               "Job has --begin time that hasn't arrived yet. Wait or update with scontrol_update.",

    # QOS limits
    "QOSMaxCpuPerUserLimit":   "Per-user CPU quota hit. Wait for your running jobs to finish.",
    "QOSMaxJobsPerUserLimit":  "Per-user job limit hit. Wait for a running job to complete.",
    "QOSMaxWallDurationPerJobLimit": "Requested --time exceeds QOS wall limit. Reduce or switch QOS.",
    "QOSMaxCpuPerJobLimit":    "Job requests more CPUs than QOS allows per job. Reduce --cpus-per-task or -n.",
    "QOSMaxMemoryPerJob":      "Job requests more memory than QOS allows. Reduce --mem.",
    "QOSMaxMemoryPerNode":     "Per-node memory exceeds QOS limit. Reduce --mem-per-cpu or spread across more nodes.",
    "QOSMaxNodePerJobLimit":   "Job requests more nodes than QOS allows. Reduce -N.",
    "QOSMaxNodePerUserLimit":  "Per-user node limit hit. Wait for running jobs to free nodes.",
    "QOSMaxGRESPerJob":        "GRES (GPU) request exceeds QOS limit. Reduce --gres.",
    "QOSMaxGRESPerUser":       "Per-user GPU limit hit. Wait for GPU jobs to finish.",
    "QOSMaxSubmitJobPerUserLimit": "Max pending+running jobs per user reached. Wait for completion.",
    "QOSGrpCpuLimit":          "QOS aggregate CPU limit reached. Wait for other jobs in your QOS to finish.",
    "QOSGrpMemLimit":          "QOS aggregate memory limit reached. Wait for other jobs.",
    "QOSGrpNodeLimit":         "QOS aggregate node limit reached.",
    "QOSGrpJobsLimit":         "QOS total running job limit reached.",
    "QOSGrpGRES":              "QOS aggregate GRES limit reached. Wait for GPU jobs.",
    "QOSNotAllowed":           "Requested QOS not permitted for your association. Check with sacctmgr_show.",
    "QOSResourceLimit":        "Generic QOS resource limit. Check `sacctmgr show qos` for limits.",
    "QOSUsageThreshold":       "QOS usage threshold breached. Fairshare penalty.",

    # Association limits
    "AssocGrpCPUMinutesLimit": "Group CPU-minute budget exhausted. Contact PI or admin.",
    "AssocGrpCpuLimit":        "Association aggregate CPU limit. Wait or contact admin.",
    "AssocGrpMemLimit":        "Association aggregate memory limit.",
    "AssocGrpNodeLimit":       "Association aggregate node limit.",
    "AssocGrpJobsLimit":       "Association running job limit. Wait for completion.",
    "AssocGrpGRES":            "Association GRES limit. Wait for GPU jobs to finish.",
    "AssocGrpWallLimit":       "Association walltime budget exhausted.",
    "AssocGrpSubmitJobsLimit": "Max pending+running jobs for association reached.",
    "AssocMaxJobsLimit":       "Account job limit reached. Wait for other jobs to complete.",
    "AssocMaxCpuPerJobLimit":  "Per-job CPU limit for association. Reduce --cpus.",
    "AssocMaxNodePerJobLimit": "Per-job node limit for association. Reduce -N.",
    "AssocMaxMemPerJob":       "Per-job memory limit for association. Reduce --mem.",
    "AssocMaxWallDurationPerJobLimit": "Per-job walltime limit. Reduce --time.",
    "AssocMaxSubmitJobLimit":  "Max pending+running jobs for association reached.",
    "AssociationJobLimit":     "Association has reached its maximum job count.",
    "AssociationResourceLimit":"Association has reached a resource limit.",
    "AssociationTimeLimit":    "Association has reached its time limit.",

    # Node/partition issues
    "ReqNodeNotAvail":         "Requested node(s) unavailable/down/drained. Remove --nodelist or --constraint, or wait.",
    "NodeDown":                "Required node is down. Remove specific node requirement or wait for repair.",
    "PartitionDown":           "Partition is DOWN. Switch to another partition with -p.",
    "PartitionNodeLimit":      "Requested more nodes than partition has. Reduce -N.",
    "PartitionTimeLimit":      "Job --time exceeds partition limit. Reduce or switch partition.",
    "PartitionInactive":       "Partition is inactive. Use a different partition.",
    "PartitionConfig":         "Job violates a partition limit. Check `scontrol show partition`.",
    "BadConstraints":          "Job requirements can never be met. Fix --constraint, --gres, or resource requests.",
    "Constraints":             "Constraints can't be satisfied right now. Wait for resources or relax constraints.",

    # Other
    "Licenses":                "Waiting for a software license. Check `scontrol show license`.",
    "Reservation":             "Job is waiting for its reservation to start.",
    "ReservationDeleted":      "The reservation was deleted. Resubmit without --reservation.",
    "JobArrayTaskLimit":       "Array task concurrency limit (%N) reached. Wait for running tasks to finish.",
    "JobHeldAdmin":            "Admin put a hold on the job. Contact sysadmin.",
    "JobHeldUser":             "You (or coordinator) held the job. Release with scontrol_release.",
    "JobHoldMaxRequeue":       "Max requeue count reached. Job won't run again.",
    "JobLaunchFailure":        "Launch failed — bad script, missing file, or FS issue. Check script path and permissions.",
    "Prolog":                  "Node prolog script still running. Should clear automatically.",
    "Cleaning":                "Job is being requeued and cleaning up. Should clear automatically.",
    "InactiveLimit":           "Job reached InactiveLimit. Resubmit with activity.",
    "InvalidAccount":          "Account is invalid. Check `sacctmgr show account`.",
    "InvalidQOS":              "Requested QOS doesn't exist. Check `sacctmgr show qos`.",
    "DeadLine":                "Job can't meet its --deadline. Extend deadline or reduce --time.",
    "MaxMemPerLimit":          "Memory request violates MaxMemPer{CPU,Node} limit. Reduce --mem or --mem-per-cpu.",
    "SchedDefer":              "Immediate allocation requested but SchedulerParameters=defer set. Use sbatch instead.",
    "SystemFailure":           "System failure (FS, network). Contact admin.",
    "FedJobLock":              "Federated cluster sync in progress. Wait.",
    "AccountNotAllowed":       "Account not allowed in this partition. Switch -A or -p.",
}


@mcp.tool()
def diagnose_job(job_id: str) -> str:
    """
    Full job diagnosis: state, resources, exit code interpretation, stderr output, and fix hints.
    job_id (REQUIRED). Works on running, pending, failed, and completed jobs.
    Exit code meanings: 137=OOM (increase --mem), 143=walltime (increase --time), 1=app error.
    """
    if REAL_MODE:
        info = _run_cmd(["scontrol", "show", "job", job_id])
        if "error" in info.lower() or "Invalid" in info:
            # Try sacct for completed jobs
            acct = _run_cmd(["sacct", "-j", job_id,
                            "--format=JobID,JobName,User,State,ExitCode,Elapsed,NodeList,Reason",
                            "--parsable2", "--noheader"])
            if acct and "error" not in acct.lower():
                parts = acct.split("|") if "|" in acct else acct.split()
                exit_code = parts[4] if len(parts) > 4 else "?"
                hint = _EXIT_HINTS.get(exit_code, f"Exit code {exit_code} — check stderr.")
                return f"=== Job Diagnosis: {job_id} ===\n\nAccounting record:\n{acct}\n\nDIAGNOSIS: {hint}"
            return f"Job {job_id} not found. {info}"
        # Parse state and exit code from scontrol output
        import re as _re
        state_m = _re.search(r"JobState=(\S+)", info)
        exit_m = _re.search(r"ExitCode=(\S+)", info)
        reason_m = _re.search(r"Reason=(\S+)", info)
        state = state_m.group(1) if state_m else "UNKNOWN"
        exit_code = exit_m.group(1) if exit_m else "0:0"
        reason = reason_m.group(1) if reason_m else "None"
        hint = ""
        if state == "PENDING":
            hint = _PENDING_HINTS.get(reason, f"Reason '{reason}' — check scontrol output.")
        elif state in ("FAILED", "TIMEOUT", "OUT_OF_MEMORY"):
            hint = _EXIT_HINTS.get(exit_code, f"Exit code {exit_code} — check stderr.")
        elif state == "RUNNING":
            hint = f"Job is healthy and running. Use sstat({job_id}) for live stats."
        else:
            hint = f"State: {state}."
        return f"=== Job Diagnosis: {job_id} ===\n\n{info}\n\nDIAGNOSIS: {hint}"
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
    """Update a Slurm entity attribute.
    entity="job"|"node"|"partition", id=entity ID, params="key=value key2=value2"."""
    if REAL_MODE:
        cmd = ["scontrol", "update", f"{entity}={id}"] + params.split()
        return _run_cmd(cmd)
    if entity.lower() == "job":
        return _STATE.update(id, params)
    return f"scontrol update {entity} {id}: {params} — applied."

@mcp.tool()
def scontrol_create(entity: str, params: str) -> str:
    """Create a new Slurm entity (partition, reservation). Admin only."""
    if REAL_MODE:
        return _run_cmd(["scontrol", "create", entity] + params.split())
    return f"scontrol create {entity}: {params} — created (mock)."

@mcp.tool()
def scontrol_delete(entity: str, id: str) -> str:
    """Delete a Slurm entity (partition, reservation). Admin only."""
    if REAL_MODE:
        return _run_cmd(["scontrol", "delete", f"{entity}={id}"])
    return f"scontrol delete {entity} {id} — deleted (mock)."

@mcp.tool()
def scontrol_reconfigure() -> str:
    """Force slurmctld to re-read slurm.conf. Admin only, no args."""
    if REAL_MODE:
        return _run_cmd(["scontrol", "reconfigure"])
    return "scontrol reconfigure: daemon reconfigured (mock)."


@mcp.tool()
def scontrol_requeue(job_id: str) -> str:
    """Requeue a failed/cancelled/completed job back to PENDING state.
    job_id (REQUIRED). Cannot requeue RUNNING jobs — cancel first."""
    if REAL_MODE:
        result = _run_cmd(["scontrol", "requeue", job_id])
        if "error" not in result.lower():
            return f"Job {job_id} requeued."
        return result
    return _STATE.requeue(str(job_id))

@mcp.tool()
def sacctmgr_show(entity: str = "user", params: str = "") -> str:
    """Show accounting entities (user, account, qos, association, cluster)."""
    if REAL_MODE:
        cmd = ["sacctmgr", "show", entity]
        if params: cmd += params.split()
        cmd += ["--parsable2"]
        return _run_cmd(cmd)
    if entity.lower() == "user":
        return "alice  1000  general  normal\nbob    1001  general  normal\ncharlie 1002 general normal"
    if entity.lower() == "qos":
        return "normal  priority=0  MaxJobs=50  MaxWall=7-00:00:00\nhigh    priority=10  MaxJobs=5   MaxWall=1-00:00:00"
    return f"sacctmgr show {entity}: (mock result)"

@mcp.tool()
def sacctmgr_add(entity: str, params: str) -> str:
    """Add an accounting entity."""
    if REAL_MODE:
        return _run_cmd(["sacctmgr", "add", entity] + params.split() + ["--immediate"])
    return f"sacctmgr add {entity}: {params} — added (mock)."

@mcp.tool()
def sacctmgr_modify(entity: str, where: str, params: str) -> str:
    """Modify an accounting entity."""
    if REAL_MODE:
        return _run_cmd(["sacctmgr", "modify", entity, "where"] + where.split() + ["set"] + params.split() + ["--immediate"])
    return f"sacctmgr modify {entity} where {where} set {params} — modified (mock)."

@mcp.tool()
def sacctmgr_delete(entity: str, params: str) -> str:
    """Delete an accounting entity."""
    if REAL_MODE:
        return _run_cmd(["sacctmgr", "delete", entity] + params.split() + ["--immediate"])
    return f"sacctmgr delete {entity}: {params} — deleted (mock)."

@mcp.tool()
def cluster_history() -> str:
    """Show the action history log for this session — every scancel, sbatch, hold, release, update, requeue.
    Useful for auditing what the agent has done so far in this conversation."""
    if REAL_MODE:
        return "cluster_history: not available in real mode (use slurmdbd/sacct)."
    return "=== Cluster Action History ===\n" + _STATE.history()


@mcp.tool()
def reset_mock_state(scenario: str = "", source_state_json: str = "") -> str:
    """Reset mock cluster state.
    - scenario: healthy|failed|pending|mixed|debug_needed (defaults to current SCENARIO)
    - source_state_json: optional JSON string matching dataset source_state
      shape: {"jobs": {"1001": {...}}, "nodes": {"node1": {...}}}
    Use this before each evaluation test to keep deterministic baselines.
    """
    if REAL_MODE:
        return "reset_mock_state: unavailable in real mode"

    target = scenario.strip() or SCENARIO
    if target not in MOCK_JOBS:
        return f"reset_mock_state: invalid scenario '{target}'"

    source_state = None
    if source_state_json.strip():
        try:
            source_state = json.loads(source_state_json)
        except Exception as e:
            return f"reset_mock_state: invalid source_state_json: {e}"

    return _STATE.reset(target, source_state)


@mcp.tool()
def sreport(report_type: str = "cluster", params: str = "") -> str:
    """Generate a Slurm usage/utilization report."""
    if REAL_MODE:
        cmd = ["sreport", report_type]
        if params: cmd += params.split()
        return _run_cmd(cmd)
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


# ── Fairshare / Trigger / Attach / Broadcast Tools ───────────────────────────

@mcp.tool()
def sshare(user: str = "", account: str = "") -> str:
    """Show fairshare usage vs allocation for users/accounts."""
    if REAL_MODE:
        cmd = ["sshare", "--parsable2"]
        if user: cmd += ["--users", user]
        if account: cmd += ["--accounts", account]
        return _run_cmd(cmd)
    # Mock
    return (
        "Account|User|RawShares|NormShares|RawUsage|EffectvUsage|FairShare\n"
        "general|alice|100|0.333|50000|0.250|0.750\n"
        "general|bob|100|0.333|80000|0.400|0.600\n"
        "general|charlie|100|0.333|70000|0.350|0.650"
    )


@mcp.tool()
def strigger(action: str = "get", job_id: str = "", event: str = "", program: str = "") -> str:
    """Manage Slurm event triggers (get/set/clear)."""
    if REAL_MODE:
        if action == "get":
            cmd = ["strigger", "--get"]
            if job_id: cmd += ["--jobid", job_id]
            return _run_cmd(cmd)
        elif action == "set":
            if not event or not program:
                return "Error: --set requires event and program. E.g. event='down' program='/path/to/script.sh'"
            cmd = ["strigger", "--set"]
            if job_id: cmd += ["--jobid", job_id]
            cmd += [f"--{event}", f"--program={program}"]
            return _run_cmd(cmd)
        elif action == "clear":
            cmd = ["strigger", "--clear"]
            if job_id: cmd += ["--jobid", job_id]
            return _run_cmd(cmd)
        return f"Unknown strigger action: {action}. Use get/set/clear."
    # Mock
    if action == "get":
        return "TRIGGER_ID TYPE       RES_TYPE   RES_ID     OFFSET     USER       PROGRAM\n1          node       node       *          0          root       /usr/sbin/strigger_notify.sh"
    elif action == "set":
        return f"strigger: trigger set for event={event} program={program} (mock)."
    elif action == "clear":
        return "strigger: trigger(s) cleared (mock)."
    return f"Unknown strigger action: {action}."


@mcp.tool()
def sattach(job_id: str) -> str:
    """View recent stdout/stderr from a running job. job_id REQUIRED."""
    if REAL_MODE:
        # sattach is interactive; just show the job's output file instead
        info = _run_cmd(["scontrol", "show", "job", job_id])
        import re as _re
        stdout_m = _re.search(r"StdOut=(\S+)", info)
        if stdout_m:
            out_file = stdout_m.group(1)
            try:
                with open(out_file, "r") as f:
                    lines = f.readlines()
                tail = lines[-50:] if len(lines) > 50 else lines
                return f"=== Last {len(tail)} lines of {out_file} ===\n" + "".join(tail)
            except Exception as e:
                return f"Cannot read output file {out_file}: {e}"
        return f"No StdOut file found for job {job_id}.\n\n{info}"
    return f"sattach: would attach to job {job_id} stdin/stdout/stderr (mock — not interactive)."


@mcp.tool()
def sbcast(source: str, destination: str, job_id: str = "") -> str:
    """Broadcast a file to allocated nodes' local storage."""
    if REAL_MODE:
        cmd = ["sbcast", source, destination]
        if job_id: cmd += ["--jobid", job_id]
        return _run_cmd(cmd)
    return f"sbcast: would broadcast {source} → {destination} on allocated nodes (mock)."


@mcp.tool()
def scrontab(action: str = "list", user: str = "", content: str = "") -> str:
    """Manage Slurm crontab (recurring scheduled jobs).
    action: "list" (show current crontab), "edit" (set new crontab from content), "remove" (delete crontab).
    user (optional): target user (admin only). content: crontab text for "edit" action.
    Cron syntax: minute hour day_of_month month day_of_week command.
    Use #SCRON for sbatch options before each entry."""
    if REAL_MODE:
        if action == "list":
            cmd = ["scrontab", "-l"]
            if user:
                cmd += ["-u", user]
            return _run_cmd(cmd)
        elif action == "remove":
            cmd = ["scrontab", "-r"]
            if user:
                cmd += ["-u", user]
            return _run_cmd(cmd)
        elif action == "edit" and content:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cron', delete=False) as f:
                f.write(content)
                tmp = f.name
            cmd = ["scrontab"]
            if user:
                cmd += ["-u", user]
            cmd.append(tmp)
            result = _run_cmd(cmd)
            os.unlink(tmp)
            return result or "Crontab updated."
        return "scrontab: specify action='list', 'edit' (with content=), or 'remove'."
    if action == "list":
        return (
            "# Slurm crontab (mock)\n"
            "#SCRON -p cpu\n"
            "#SCRON -t 5:00\n"
            "@daily /home/user/backup.sh\n"
            "\n"
            "#SCRON -p gpu\n"
            "#SCRON --gres=gpu:1\n"
            "0 */6 * * * /home/user/train_checkpoint.sh\n"
        )
    elif action == "remove":
        return "Crontab removed (mock). Running crontab jobs will continue but won't recur."
    elif action == "edit":
        return "Crontab updated (mock)."
    return "Unknown action."


@mcp.tool()
def sjobexitmod(job_id: str, exit_code: str = "", comment: str = "") -> str:
    """View or modify a completed job's derived exit code and comment string.
    job_id (REQUIRED). exit_code (optional): new derived exit code. comment (optional): annotation.
    Useful for annotating jobs that failed but appear successful, or vice versa."""
    if REAL_MODE:
        if not exit_code and not comment:
            return _run_cmd(["sjobexitmod", "-l", job_id])
        cmd = ["sjobexitmod"]
        if exit_code:
            cmd += ["-e", exit_code]
        if comment:
            cmd += ["-r", comment]
        cmd.append(job_id)
        return _run_cmd(cmd)
    if not exit_code and not comment:
        return (
            f"JobID  DerivedExitCode  Comment\n"
            f"-----  ---------------  -------\n"
            f"{job_id}    0:0              (none)\n"
        )
    parts = []
    if exit_code:
        parts.append(f"DerivedExitCode={exit_code}")
    if comment:
        parts.append(f"Comment='{comment}'")
    return f"Job {job_id} updated: {', '.join(parts)} (mock)."


# ── Tool discovery (lazy loading) ────────────────────────────────────────────
# Short docstrings keep the tool schema small. Agents call tool_help(name) for
# full usage details before calling an unfamiliar tool.

_TOOL_HELP: dict[str, str] = {
    "squeue": """\
Show current Slurm job queue.
Args: user (str, optional), state (str, optional: RUNNING|PENDING|COMPLETED|FAILED|CANCELLED|TIMEOUT), partition (str, optional)
Returns: pipe-delimited table JOBID|NAME|USER|STATE|TIME|NODES|CPUS|MIN_MEM|PARTITION
Example: squeue(state="PENDING") → all pending jobs
Example: squeue(user="alice", partition="gpu") → alice's GPU jobs""",

    "sinfo": """\
Show cluster partition and node status.
Args: partition (str, optional), node (str, optional)
Returns: partition summary (Allocated/Idle/Down counts) + node details (hostname, state, CPUs, memory, GPUs)
Example: sinfo() → full cluster overview
Example: sinfo(partition="gpu") → GPU partition only""",

    "sacct": """\
Query historical job accounting records (completed/failed/cancelled jobs).
Args: user (str), state (str: COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY), starttime (str: YYYY-MM-DD or now-7days), endtime (str), format (str: comma-separated fields)
Returns: pipe-delimited accounting table
Example: sacct(state="FAILED", starttime="now-7days") → recent failures
Example: sacct(user="alice") → alice's job history""",

    "scontrol_show": """\
Show detailed Slurm entity info — more fields than squeue/sinfo.
Args: entity (str: job|node|partition, default=job), id (str, optional)
Returns: raw key=value output (ReasonList, AllocTRES, StdErr path, etc.)
Example: scontrol_show(entity="job", id="12345") → full job details""",

    "sbatch": """\
Submit one or more batch job scripts to Slurm.
Args: script (str, REQUIRED: file path or comma-separated paths), flags (str, optional)
For multiple files, pass ALL paths comma-separated in ONE call.
Returns: "Submitted batch job {id}" per script
Example: sbatch(script="/tmp/slurm_uploads/train.sh")
Example: sbatch(script="/tmp/a.sh,/tmp/b.sh,/tmp/c.sh") → submits all 3
Example: sbatch(script="/tmp/job.sh", flags="--partition=gpu --gres=gpu:1")""",

    "scancel": """\
Cancel one or more Slurm jobs.
Args: job_id (str, REQUIRED: single ID, parent array ID, or comma-separated), user (str, optional)
For array jobs, use the parent ID (e.g. "7") to cancel all tasks at once.
For multiple jobs, pass comma-separated IDs (e.g. "5,7,8") in ONE call.
Returns: summary of cancelled jobs or error
Example: scancel(job_id="12345")
Example: scancel(job_id="100,101,102") → cancel 3 jobs in one call
Example: scancel(job_id="7") → cancel all tasks of array job 7""",

    "scontrol_hold": """\
Hold a pending job (prevents scheduling until released).
Args: job_id (str, REQUIRED)
Example: scontrol_hold(job_id="12345")""",

    "scontrol_release": """\
Release a held job so it can be scheduled.
Args: job_id (str, REQUIRED)
Example: scontrol_release(job_id="12345")""",

    "scontrol_requeue": """\
Requeue a failed/cancelled/completed job back to PENDING.
Args: job_id (str, REQUIRED). Cannot requeue RUNNING jobs — cancel first.
Example: scontrol_requeue(job_id="12345")""",

    "srun": """\
Run a command interactively via Slurm (allocate + execute).
Args: command (str, REQUIRED), nodes (int, default=1), cpus (int, default=1), partition (str, default="cpu")
Example: srun(command="hostname", nodes=2)""",

    "salloc": """\
Allocate interactive resources without running a command.
Args: nodes (int), cpus (int), partition (str), time (str: HH:MM:SS)
Example: salloc(partition="gpu", time="02:00:00")""",

    "sdiag": """\
Show scheduler diagnostics: backfill stats, cycle times, RPC rates, queue depth.
No args. Useful for health checks.""",

    "sprio": """\
Show priority factors for pending jobs (age, fairshare, QOS, size).
Args: user (str, optional), partition (str, optional)
Higher priority = scheduled sooner.""",

    "sstat": """\
Show real-time resource stats for a RUNNING job (CPU%, RSS, disk I/O).
Args: job_id (str, REQUIRED). Only works on RUNNING jobs; use sacct for completed.
Example: sstat(job_id="12345")""",

    "diagnose_job": """\
Full job diagnosis: state, resources, exit code interpretation, stderr, fix hints.
Args: job_id (str, REQUIRED). Works on running AND completed/failed jobs.
Exit code meanings: 137=OOM(increase --mem), 143=walltime(increase --time), 1=app error
Example: diagnose_job(job_id="12345")""",

    "read_file": """\
Read a text file from the filesystem (max 1MB).
Args: file_path (str, REQUIRED: absolute path)
Example: read_file(file_path="/home/alice/job.sh")""",

    "web_search": """\
Search the web via DuckDuckGo.
Args: query (str, REQUIRED), search_type (str: general|slurm|error), fetch_content (bool)
Example: web_search(query="slurm OOM killed fix", search_type="error")""",

    "generate_chart": """\
Generate a Mermaid diagram from live cluster data.
Args: chart_id (REQUIRED, one of: system_health, cluster_topology, pending_analysis, resource_map, job_lifecycle, efficiency_report)
Each chart_id produces a different Mermaid chart type (xychart, flowchart, gantt).""",

    "run_analysis": """\
Run a predefined analysis script.
Args: script_id (REQUIRED, one of: analyze_cluster_status, analyze_failed_jobs, analyze_pending_jobs, analyze_gpu_resources, analyze_node_health, analyze_job_efficiency, analyze_my_jobs, analyze_my_usage, analyze_my_efficiency)""",

    "scontrol_update": """\
Update a Slurm entity attribute.
Args: entity (str: job|node|partition), id (str), params (str: "key=value key2=value2")
Example: scontrol_update(entity="job", id="12345", params="TimeLimit=2-00:00:00")""",

    "scontrol_create": "Create a Slurm entity. Args: entity (str), params (str).",
    "scontrol_delete": "Delete a Slurm entity. Args: entity (str), id (str).",
    "scontrol_reconfigure": "Force slurmctld to re-read slurm.conf. No args.",

    "sacctmgr_show": """\
Show accounting entities.
Args: entity (str: user|account|qos|association|cluster|tres|wckey), params (str, optional)
Example: sacctmgr_show(entity="qos")""",

    "sacctmgr_add": "Add accounting entity. Args: entity (str), params (str).",
    "sacctmgr_modify": "Modify accounting entity. Args: entity (str), where (str), params (str).",
    "sacctmgr_delete": "Delete accounting entity. Args: entity (str), params (str).",

    "sreport": "Generate Slurm usage report. Args: report_type (str, default='cluster'), params (str).",
    "sshare": "Show fairshare info. Args: user (str), account (str).",
    "strigger": "Manage event triggers. Args: action (get|set|clear), job_id, event, program.",
    "sattach": "View recent stdout/stderr from a running job. Args: job_id (str, REQUIRED).",
    "sbcast": "Broadcast file to compute nodes. Args: source (str), destination (str), job_id (str).",

    "scrontab": """\
Manage Slurm cron-like scheduled jobs (scrontab).
Args: action (str: list|edit|remove, default=list), user (str, optional), content (str, for edit)
list → show current crontab entries. edit → replace crontab with content. remove → clear crontab.
Example: scrontab(action="list") → show scheduled jobs
Example: scrontab(action="edit", content="0 2 * * * /scripts/backup.sh")""",

    "sjobexitmod": """\
View or modify the derived exit code of a completed job.
Args: job_id (str, REQUIRED), new_exit_code (int, optional)
Without new_exit_code → returns current exit info. With new_exit_code → updates derived exit code.
Example: sjobexitmod(job_id="12345") → view exit details
Example: sjobexitmod(job_id="12345", new_exit_code=0) → override to success""",
}


@mcp.tool()
def list_tools() -> str:
    """List all available Slurm tools grouped by category. Call tool_help(name) for usage details."""
    return """\
=== Query Tools (read-only) ===
squeue        — Show job queue (filter by user/state/partition)
sinfo         — Show partition & node status
sacct         — Job history (completed/failed)
scontrol_show — Detailed entity info (job/node/partition)
sdiag         — Scheduler diagnostics
sprio         — Pending job priority factors
sstat         — Real-time stats for RUNNING jobs
diagnose_job  — Full job diagnosis with fix hints
sjobexitmod   — View/modify derived exit codes
read_file     — Read a text file
web_search    — Web search via DuckDuckGo

=== Action Tools (modify cluster — requires approval) ===
sbatch           — Submit a job script
scancel          — Cancel a job
scontrol_hold    — Hold a pending job
scontrol_release — Release a held job
scontrol_requeue — Requeue a failed/cancelled job
srun             — Run command interactively
salloc           — Allocate interactive resources
scrontab         — Manage scheduled cron jobs (list/edit/remove)

=== Admin Tools ===
scontrol_update/create/delete/reconfigure
sacctmgr_show/add/modify/delete
sreport, sshare, strigger, sattach, sbcast

=== Analysis & Visualization ===
run_analysis   — Predefined analysis scripts
generate_chart — Mermaid diagrams from live data

Call tool_help(name) for detailed args and examples."""


@mcp.tool()
def tool_help(name: str) -> str:
    """Get detailed usage, args, and examples for a specific tool. Call list_tools() first to see names."""
    key = name.strip().lower()
    if key in _TOOL_HELP:
        return f"=== {key} ===\n{_TOOL_HELP[key]}"
    return f"Unknown tool: '{name}'. Call list_tools() to see available tools."


# ── Shell execution tool ──────────────────────────────────────────────────────

@mcp.tool()
def shell_exec(command: str, workdir: str = "", timeout: int = 30) -> str:
    """Execute a shell command on the cluster and return stdout+stderr.

    command  (REQUIRED): the shell command to run.
                         Supports pipes, redirects, and shell builtins.
                         For sudo commands, prefix with "sudo" — the user
                         will be asked for approval before execution.
    workdir  (optional): directory to run in (default: home directory).
    timeout  (optional): max seconds to wait (default: 30, max: 120).

    USE CASES:
      - Debug job failures:   shell_exec("cat /path/to/slurm-12345.out")
      - Check disk space:     shell_exec("df -h /scratch")
      - Inspect environment:  shell_exec("module list 2>&1")
      - Read job scripts:     shell_exec("cat /tmp/slurm_uploads/train.sh")
      - Check GPU status:     shell_exec("nvidia-smi")
      - View system logs:     shell_exec("sudo journalctl -u slurmctld --no-pager -n 50")
      - Network diagnostics:  shell_exec("ss -tlnp | grep 6817")

    ⚠ This tool can run ANY command. Destructive commands (rm, mkfs, dd, etc.)
      require user approval. Always prefer specific Slurm tools (squeue, sbatch)
      for standard operations — use shell_exec for debugging and inspection."""

    if not command or not command.strip():
        return "shell_exec: error: 'command' argument is required."

    command = command.strip()

    # Clamp timeout
    timeout = max(1, min(timeout, 120))

    # ── Safety: tag dangerous patterns so the display shows a clear warning ──
    _DANGEROUS_PATTERNS = (
        "rm -rf", "rm -r /", "mkfs", "dd if=", ":(){ :|:",  # fork bomb
        "> /dev/sd", "shutdown", "reboot", "init 0", "init 6",
        "chmod -R 777 /", "chown -R", "wipefs",
    )
    is_dangerous = any(pat in command for pat in _DANGEROUS_PATTERNS)
    is_sudo = command.strip().startswith("sudo")

    if not REAL_MODE:
        # Mock mode: return simulated output
        prefix = "[sudo] " if is_sudo else ""
        if "nvidia-smi" in command:
            return (
                f"{prefix}Sat Apr 12 12:00:00 2026\n"
                "+-----------------------------------------------------------------------------+\n"
                "| NVIDIA-SMI 550.54   Driver Version: 550.54   CUDA Version: 12.4             |\n"
                "|-------------------------------+----------------------+----------------------+\n"
                "| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |\n"
                "| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |\n"
                "|   0  RTX 5070 Ti      On      | 00000000:01:00.0 Off |                  N/A |\n"
                "|  0%   35C    P8    15W / 300W |    128MiB / 16384MiB |      0%      Default |\n"
                "+-------------------------------+----------------------+----------------------+\n"
            )
        if "df " in command:
            return (
                f"{prefix}Filesystem      Size  Used Avail Use% Mounted on\n"
                "/dev/sda1       500G  120G  380G  24% /\n"
                "/dev/sdb1       2.0T  800G  1.2T  40% /scratch\n"
            )
        if "module list" in command:
            return f"{prefix}Currently loaded modules:\n  1) cuda/12.4   2) python/3.11   3) openmpi/4.1\n"
        if "cat" in command:
            path = command.split("cat")[-1].strip().split()[0] if "cat" in command else ""
            return f"{prefix}(mock) Contents of {path}:\n#!/bin/bash\n#SBATCH --job-name=example\necho 'Hello from Slurm'\n"
        return f"{prefix}(mock) $ {command}\nCommand executed successfully."

    # ── Real mode ──
    import shlex

    env = os.environ.copy()
    cwd = workdir.strip() if workdir.strip() else os.path.expanduser("~")

    if not os.path.isdir(cwd):
        return f"shell_exec: error: workdir '{cwd}' does not exist."

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=env,
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        parts = []
        if stdout:
            parts.append(stdout)
        if stderr:
            parts.append(f"STDERR: {stderr}")
        if result.returncode != 0:
            parts.append(f"(exit code {result.returncode})")

        output = "\n".join(parts) if parts else "(no output)"

        # Truncate very long output
        if len(output) > 8000:
            output = output[:8000] + f"\n... [truncated, {len(output)} chars total]"

        return output

    except subprocess.TimeoutExpired:
        return f"shell_exec: error: Command timed out after {timeout}s. Try increasing timeout or simplifying the command."
    except Exception as e:
        return f"shell_exec: error: {e}"


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
