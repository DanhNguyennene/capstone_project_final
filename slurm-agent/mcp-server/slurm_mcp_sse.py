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
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# ── Add parent dirs to path so mock_data is importable ──
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
def squeue(user: str = "", state: str = "", partition: str = "", job_id: str = "") -> str:
    """Show current job queue with JOBID, name, user, state, time, resources.
    Filter: user="alice", state="RUNNING|PENDING|FAILED|COMPLETED", partition="gpu", job_id="1001".
    Returns pipe-delimited table. job_id returns info for a specific job (or 'No such job' if not found)."""
    if REAL_MODE:
        cmd = [
            "squeue",
            "--format=%i|%j|%u|%T|%M|%D|%C|%m|%P",
            "--noheader",
        ]
        if user: cmd += ["--user", user]
        if state: cmd += ["--state", state]
        if partition: cmd += ["--partition", partition]
        if job_id: cmd += ["--jobs", job_id]
        raw = _run_cmd(cmd)
        if not raw or raw == "(no output)":
            return f"No such job: {job_id}." if job_id else "No jobs in queue."
        header = "JOBID|NAME|USER|STATE|TIME|NODES|CPUS|MIN_MEM|PARTITION"
        return header + "\n" + raw
    jobs = _jobs()
    if user:
        jobs = [j for j in jobs if j.get("user", "").lower() == user.lower()]
    if state:
        jobs = [j for j in jobs if j.get("state", "").upper() == state.upper()]
    if partition:
        jobs = [j for j in jobs if j.get("partition", "").lower() == partition.lower()]
    if job_id:
        jobs = [j for j in jobs if str(j.get("job_id", "")) == str(job_id)]
        if not jobs:
            return f"No such job: {job_id}."
    return _fmt_jobs(jobs)


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
def sacctmgr_list(entity: str = "user", params: str = "") -> str:
    """List accounting entities (user, account, qos, association, cluster)."""
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


# ── Diagnostic / supplementary tools (not write-ops, supplement Slurm data) ──

@mcp.tool()
def sdiag() -> str:
    """Show Slurm scheduler diagnostics: backfill stats, cycle times, queue depth."""
    if REAL_MODE:
        return _run_cmd(["sdiag"])
    return (
        "sdiag — Scheduler Diagnostics\n"
        "Server threads: 3  Agent queue size: 0\n"
        "Jobs submitted: 42  Jobs started: 38  Jobs completed: 35\n"
        "Backfill: last cycle 0.12s  last depth: 4 jobs  last queue length: 5\n"
        "Main sched: last cycle 0.03s\n"
    )


@mcp.tool()
def sprio(user: str = "", partition: str = "") -> str:
    """Show priority factors for pending jobs (fairshare, age, QOS, partition)."""
    if REAL_MODE:
        cmd = ["sprio", "-l"]
        if user:
            cmd += ["--user", user]
        if partition:
            cmd += ["--partition", partition]
        return _run_cmd(cmd)
    jobs = [j for j in _jobs() if j.get("state") == "PENDING"]
    if user:
        jobs = [j for j in jobs if j.get("user") == user]
    if partition:
        jobs = [j for j in jobs if j.get("partition") == partition]
    if not jobs:
        return "No pending jobs match the filter."
    lines = ["JOBID    USER       PRIORITY  FAIRSHARE  AGE  QOS  PARTITION"]
    for j in jobs:
        jid = j.get("job_id", "?")
        u = j.get("user", "?")
        lines.append(f"{jid:<8} {u:<10} 1000      0.50       100  1    1")
    return "\n".join(lines)


@mcp.tool()
def sstat(job_id: str) -> str:
    """Show real-time resource usage for a RUNNING job (CPU%, memory RSS, I/O).
    job_id (REQUIRED). Only works on running jobs; use sacct for completed."""
    if REAL_MODE:
        return _run_cmd(["sstat", "-j", job_id,
                         "--format=JobID,AveCPU,AveRSS,AveVMSize,MaxRSS,NTasks"])
    jobs = _jobs()
    match = next((j for j in jobs if str(j.get("job_id", "")) == str(job_id)), None)
    if not match:
        return f"sstat: error: Job {job_id} not found or not running."
    if match.get("state") != "RUNNING":
        return f"sstat: Job {job_id} is {match.get('state')} — sstat only works on RUNNING jobs. Use sacct for history."
    mem = match.get("mem", "8G")
    return (
        f"JobID    AveCPU   AveRSS    AveVMSize MaxRSS    NTasks\n"
        f"{job_id}    00:12:30 {mem}     {mem}      {mem}      1\n"
    )


@mcp.tool()
def read_file(file_path: str) -> str:
    """Read a text file from the filesystem (job scripts, logs, config files). Max 50KB."""
    if not REAL_MODE:
        return f"read_file: mock mode — cannot read '{file_path}'. Use real mode with --real flag."
    try:
        p = Path(file_path)
        if not p.exists():
            return f"Error: file not found: {file_path}"
        size = p.stat().st_size
        if size > 50 * 1024:
            return f"Error: file too large ({size} bytes). Max 50KB."
        return p.read_text(errors="replace")
    except PermissionError:
        return f"Error: permission denied: {file_path}"
    except Exception as e:
        return f"Error reading {file_path}: {e}"


@mcp.tool()
def web_search(query: str, search_type: str = "general") -> str:
    """Search the web via DuckDuckGo for Slurm error codes, documentation, or general HPC topics.
    search_type: general | slurm | error"""
    try:
        import urllib.request, urllib.parse, html
        q = urllib.parse.quote_plus(query)
        url = f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "slurm-agent/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
        parts = []
        if data.get("AbstractText"):
            parts.append(data["AbstractText"])
        for r in data.get("RelatedTopics", [])[:3]:
            if isinstance(r, dict) and r.get("Text"):
                parts.append(r["Text"])
        if not parts:
            return f"No results found for: {query}"
        return "\n\n".join(parts[:4])
    except Exception as e:
        return f"web_search failed: {e}"


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
