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
import re
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
        self._reservations: list[dict] = []
        self._triggers: list[dict] = []
        self._partition_overrides: dict[str, dict] = {}
        self._config: dict[str, str] = {
            "SchedulerType": "sched/backfill",
            "PriorityType": "priority/multifactor",
            "SelectType": "select/cons_tres",
            "SlurmctldDebug": "info",
            "ClusterName": "mock-cluster",
        }
        self._next_id: int = 2000
        self._log: list[str] = []    # action history for transparency
        self._initialized = False

    @staticmethod
    def _scenario_defaults(scenario: str) -> "tuple[list, dict, list]":
        """Return (reservations, config, triggers) appropriate for *scenario*.
        Called by both _ensure_init and reset() so state is always consistent."""
        _res_node  = {"failed": "cpu-node-01", "debug_needed": "gpu-node-02"}.get(scenario, "cpu-node-01")
        _res_state = "ACTIVE" if scenario in ("failed", "debug_needed") else "INACTIVE"
        reservations = [
            {
                "ReservationName": "maintenance",
                "StartTime":  "2026-05-14T00:00:00",
                "EndTime":    "2026-05-14T08:00:00",
                "Nodes":      _res_node,
                "Flags":      "MAINT",
                "Users":      "root",
                "State":      _res_state,
            }
        ]
        _debug = {"debug_needed": "debug3", "failed": "verbose"}.get(scenario, "info")
        config = {
            "SchedulerType": "sched/backfill",
            "PriorityType":  "priority/multifactor",
            "SelectType":    "select/cons_tres",
            "SlurmctldDebug": _debug,
            "ClusterName":   "mock-cluster",
        }
        # Pre-set node-failure monitoring triggers in broken scenarios
        triggers: list[dict] = []
        if scenario in ("failed", "debug_needed"):
            triggers = [
                {"id": "1", "spec": "--node --down   --program=/usr/local/bin/notify_admin.sh"},
                {"id": "2", "spec": "--node --drain  --program=/usr/local/bin/notify_admin.sh"},
                {"id": "3", "spec": "--node --up     --program=/usr/local/bin/node_recovered.sh"},
            ]
        return reservations, config, triggers

    def _ensure_init(self):
        if not self._initialized:
            import copy
            self._jobs  = copy.deepcopy(MOCK_JOBS.get(SCENARIO, []))
            self._nodes = copy.deepcopy(MOCK_NODES.get(SCENARIO, []))
            self._partition_overrides = {}
            self._reservations, self._config, self._triggers = \
                _ClusterState._scenario_defaults(SCENARIO)
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

    def suspend(self, jid: str) -> str:
        self._ensure_init()
        jobs = [j for j in self._jobs if str(j.get("job_id", "")) == jid]
        if not jobs:
            return f"scontrol: error: Invalid job id specified: {jid}"
        j = jobs[0]
        if j.get("state") != "RUNNING":
            return f"scontrol: error: Job {jid} cannot be suspended — state is {j.get('state')}"
        j["state"] = "SUSPENDED"
        self._log.append(f"[{_stamp()}] SUSPEND job {jid} (RUNNING → SUSPENDED)")
        return f"Job {jid} suspended."

    def resume_job(self, jid: str) -> str:
        self._ensure_init()
        jobs = [j for j in self._jobs if str(j.get("job_id", "")) == jid]
        if not jobs:
            return f"scontrol: error: Invalid job id specified: {jid}"
        j = jobs[0]
        if j.get("state") != "SUSPENDED":
            return f"scontrol: error: Job {jid} is not suspended — state is {j.get('state')}"
        j["state"] = "RUNNING"
        self._log.append(f"[{_stamp()}] RESUME job {jid} (SUSPENDED → RUNNING)")
        return f"Job {jid} resumed."

    def drain_node(self, name: str, reason: str = "admin") -> str:
        self._ensure_init()
        nodes = [n for n in self._nodes if n.get("name") == name]
        if not nodes:
            return f"scontrol: error: Invalid node name: {name}"
        n = nodes[0]
        prev = n.get("state", "idle")
        n["state"] = "drain"
        n["reason"] = reason or "admin"
        self._log.append(f"[{_stamp()}] DRAIN node {name} ({prev} → drain) reason={reason}")
        return f"Node {name} set to DRAIN. Reason: {reason or 'admin'}"

    def set_node_down(self, name: str, reason: str = "admin") -> str:
        self._ensure_init()
        nodes = [n for n in self._nodes if n.get("name") == name]
        if not nodes:
            return f"scontrol: error: Invalid node name: {name}"
        n = nodes[0]
        prev = n.get("state", "idle")
        n["state"] = "down"
        n["reason"] = reason or "admin"
        self._log.append(f"[{_stamp()}] DOWN node {name} ({prev} → down) reason={reason}")
        return f"Node {name} set to DOWN. Reason: {reason or 'admin'}"

    def resume_node(self, name: str) -> str:
        self._ensure_init()
        nodes = [n for n in self._nodes if n.get("name") == name]
        if not nodes:
            return f"scontrol: error: Invalid node name: {name}"
        n = nodes[0]
        prev = n.get("state", "drain")
        n["state"] = "idle"
        n.pop("reason", None)
        self._log.append(f"[{_stamp()}] RESUME node {name} ({prev} → idle)")
        return f"Node {name} resumed to idle."

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

    def update_node(self, node_name: str, params: str) -> str:
        self._ensure_init()
        nodes = [n for n in self._nodes if str(n.get("name", "")).lower() == node_name.lower()]
        if not nodes:
            return f"scontrol: error: Invalid node name: {node_name}"
        n = nodes[0]
        import re as _re
        changes = []
        for m in _re.finditer(r"([\w]+)=(\S+)", params):
            key = m.group(1).lower()
            val = m.group(2)
            if key == "state":
                n["state"] = val.lower()
                changes.append(f"State={val}")
            elif key == "features":
                n["features"] = val
                changes.append(f"Features={val}")
            elif key == "gres":
                n["gres"] = val
                changes.append(f"Gres={val}")
            elif key == "weight":
                n["weight"] = val
                changes.append(f"Weight={val}")
            elif key == "reason":
                n["reason"] = val
                changes.append(f"Reason={val}")
        self._log.append(f"[{_stamp()}] UPDATE node {node_name}: {params}")
        return f"Node {node_name} updated: {', '.join(changes) or params}"

    def update_partition(self, partition_name: str, params: str) -> str:
        self._ensure_init()
        if not partition_name.strip():
            return "scontrol: error: Partition name is required."
        import re as _re
        current = dict(self._partition_overrides.get(partition_name, {}))
        changes = []
        for m in _re.finditer(r"([\w]+)=(\S+)", params):
            key = m.group(1)
            val = m.group(2)
            current[key] = val
            changes.append(f"{key}={val}")
        self._partition_overrides[partition_name] = current
        self._log.append(f"[{_stamp()}] UPDATE partition {partition_name}: {params}")
        return f"Partition {partition_name} updated: {', '.join(changes) or params}"

    def create_reservation(self, params: str) -> str:
        self._ensure_init()
        import re as _re
        if not params.strip():
            return "scontrol: error: Reservation parameters are required."
        fields = {m.group(1): m.group(2) for m in _re.finditer(r"([\w]+)=(\S+)", params)}
        name = fields.get("ReservationName")
        if not name:
            return "scontrol: error: ReservationName is required."
        existing = [r for r in self._reservations if str(r.get("ReservationName", "")).lower() == name.lower()]
        if existing:
            return f"scontrol: error: Reservation {name} already exists."
        reservation = {
            "ReservationName": name,
            "StartTime": fields.get("StartTime", "now"),
            "EndTime": fields.get("EndTime", "now+8hours"),
            "Nodes": fields.get("Nodes", ""),
            "Flags": fields.get("Flags", ""),
            "Users": fields.get("Users", "root"),
            "State": fields.get("State", "INACTIVE"),
        }
        self._reservations.append(reservation)
        self._log.append(f"[{_stamp()}] CREATE reservation {name}")
        return f"Reservation {name} created successfully."

    def update_reservation(self, reservation: str, params: str) -> str:
        self._ensure_init()
        matches = [r for r in self._reservations if str(r.get("ReservationName", "")).lower() == reservation.lower()]
        if not matches:
            return f"scontrol: error: Reservation {reservation} not found."
        import re as _re
        r = matches[0]
        changes = []
        for m in _re.finditer(r"([\w]+)=(\S+)", params):
            key = m.group(1)
            val = m.group(2)
            r[key] = val
            changes.append(f"{key}={val}")
        self._log.append(f"[{_stamp()}] UPDATE reservation {reservation}: {params}")
        return f"Reservation {reservation} updated: {', '.join(changes) or params}"

    def delete_reservation(self, reservation: str) -> str:
        self._ensure_init()
        before = len(self._reservations)
        self._reservations = [
            r for r in self._reservations
            if str(r.get("ReservationName", "")).lower() != reservation.lower()
        ]
        if len(self._reservations) == before:
            return f"scontrol: error: Reservation {reservation} not found."
        self._log.append(f"[{_stamp()}] DELETE reservation {reservation}")
        return f"Reservation {reservation} deleted."

    def list_reservations(self) -> list[dict]:
        self._ensure_init()
        return list(self._reservations)

    def create_trigger(self, spec: str) -> str:
        self._ensure_init()
        trig_id = str(len(self._triggers) + 1)
        self._triggers.append({
            "id": trig_id,
            "spec": spec.strip(),
        })
        self._log.append(f"[{_stamp()}] TRIGGER set id={trig_id} spec={spec}")
        return trig_id

    def list_triggers(self) -> list[dict]:
        self._ensure_init()
        return list(self._triggers)

    def clear_trigger(self, trigger_id: str = "") -> str:
        self._ensure_init()
        if not trigger_id.strip():
            n = len(self._triggers)
            self._triggers = []
            self._log.append(f"[{_stamp()}] TRIGGER clear all ({n})")
            return f"Cleared {n} trigger(s)."
        before = len(self._triggers)
        self._triggers = [t for t in self._triggers if str(t.get("id", "")) != trigger_id]
        if len(self._triggers) == before:
            return f"strigger: error: trigger id {trigger_id} not found."
        self._log.append(f"[{_stamp()}] TRIGGER clear id={trigger_id}")
        return f"Cleared trigger {trigger_id}."

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

    def snapshot(self) -> dict:
        """Serialize full mock state for deterministic restore."""
        self._ensure_init()
        jobs_by_id = {
            str(j.get("job_id")): copy.deepcopy(j)
            for j in self._jobs
            if str(j.get("job_id", "")).strip()
        }
        nodes_by_name = {
            str(n.get("name")): copy.deepcopy(n)
            for n in self._nodes
            if str(n.get("name", "")).strip()
        }
        return {
            "scenario": SCENARIO,
            "source_state": {
                "jobs": jobs_by_id,
                "nodes": nodes_by_name,
                "partition_overrides": copy.deepcopy(self._partition_overrides),
                "reservations": copy.deepcopy(self._reservations),
                "triggers": copy.deepcopy(self._triggers),
                "config": copy.deepcopy(self._config),
                "next_id": self._next_id,
            },
        }

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

        # Reset supplemental mock state (can be overridden by snapshot payload)
        self._partition_overrides = {}
        self._reservations, self._config, self._triggers = \
            _ClusterState._scenario_defaults(scenario)

        if source_state:
            partition_overrides = source_state.get("partition_overrides")
            if isinstance(partition_overrides, dict):
                self._partition_overrides = copy.deepcopy(partition_overrides)

            reservations = source_state.get("reservations")
            if isinstance(reservations, list):
                self._reservations = copy.deepcopy(reservations)

            triggers = source_state.get("triggers")
            if isinstance(triggers, list):
                self._triggers = copy.deepcopy(triggers)

            cfg = source_state.get("config")
            if isinstance(cfg, dict):
                self._config = copy.deepcopy(cfg)

        existing_ids = [int(j["job_id"]) for j in self._jobs if str(j.get("job_id", "")).isdigit()]
        self._next_id = max(existing_ids, default=1000) + 1
        if source_state:
            try:
                next_id = int(source_state.get("next_id", 0) or 0)
                if next_id > 0:
                    self._next_id = next_id
            except Exception:
                pass
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
    has_submit_time = any(j.get("submit_time") or j.get("SubmitTime") for j in jobs)
    suffix = "  SUBMIT_TIME" if has_submit_time else ""
    lines = ["JOBID    NAME                USER     STATE     TIME      NODES CPUS MEM  PARTITION" + suffix]
    lines.append("-" * 88)
    for j in jobs:
        submit_time = j.get("submit_time") or j.get("SubmitTime") or ""
        submit_part = f"  {submit_time}" if has_submit_time else ""
        lines.append(
            f"{j.get('job_id','?'):<8} {j.get('name','?'):<20} {j.get('user','?'):<8} "
            f"{j.get('state','?'):<9} {j.get('time','?'):<9} {j.get('nodes','?'):<5} "
            f"{j.get('cpus','?'):<4} {j.get('mem','?'):<4} {j.get('partition','?')}{submit_part}"
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
    normalized_state = re.sub(r"\s*[|]\s*", ",", str(state or "").strip())
    if REAL_MODE:
        cmd = [
            "squeue",
            "--format=%i|%j|%u|%T|%M|%D|%C|%m|%P",
            "--noheader",
        ]
        if user: cmd += ["--user", user]
        if normalized_state: cmd += ["--state", normalized_state]
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
    if normalized_state:
        wanted_states = {s.strip().upper() for s in normalized_state.split(",") if s.strip()}
        if wanted_states != {"ALL"}:
            jobs = [j for j in jobs if j.get("state", "").upper() in wanted_states]
    else:
        # Match real-world squeue behavior: hide terminal jobs by default.
        terminal_states = {"CANCELLED", "COMPLETED", "FAILED", "TIMEOUT"}
        jobs = [j for j in jobs if j.get("state", "").upper() not in terminal_states]
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
    normalized_state = re.sub(r"\s*[|,]\s*", ",", str(state or "").strip())
    if REAL_MODE:
        cmd = ["sacct", f"--format={format}", "--parsable2", "--noheader"]
        if user: cmd += ["--user", user]
        if normalized_state: cmd += ["--state", normalized_state]
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
    if normalized_state:
        wanted_states = {s.strip().upper() for s in normalized_state.split(",") if s.strip()}
        if wanted_states != {"ALL"}:
            history = [j for j in history if j.get("state", "").upper() in wanted_states]

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
            f"   SubmitTime={j.get('submit_time') or j.get('SubmitTime') or 'Unknown'}\n"
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
    elif entity.lower() == "partition":
        nodes = _nodes()
        partitions = {}
        for n in nodes:
            p = n.get("partition", "unknown")
            info = partitions.setdefault(p, {"nodes": 0, "idle": 0, "alloc": 0, "down": 0})
            info["nodes"] += 1
            state = str(n.get("state", "")).lower()
            if "idle" in state:
                info["idle"] += 1
            elif "alloc" in state or "mix" in state:
                info["alloc"] += 1
            elif "down" in state or "drain" in state:
                info["down"] += 1

        if id:
            part = partitions.get(id)
            if not part:
                return f"scontrol: error: Invalid partition name: {id}"
            return (
                f"PartitionName={id}\n"
                f"   TotalNodes={part['nodes']} AllocNodes={part['alloc']} IdleNodes={part['idle']} DownNodes={part['down']}\n"
                f"   State=UP"
            )
        lines = []
        for pname, part in sorted(partitions.items()):
            lines.append(
                f"PartitionName={pname}\n"
                f"   TotalNodes={part['nodes']} AllocNodes={part['alloc']} IdleNodes={part['idle']} DownNodes={part['down']}\n"
                f"   State=UP"
            )
        return "\n\n".join(lines)
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
def srun(command: str = "", flags: str = "") -> str:
    """Launch an interactive or one-off job step.
    Real command: srun [flags] <command>."""
    if REAL_MODE:
        cmd = ["srun"]
        if flags:
            cmd += flags.split()
        if command:
            cmd += command.split()
        return _run_cmd(cmd)
    payload = f"srun {flags} {command}".strip()
    _STATE._log.append(f"[{_stamp()}] SRUN {payload}")
    return f"srun mock: launched step ({payload or 'no command provided'})."


@mcp.tool()
def salloc(flags: str = "") -> str:
    """Request an interactive allocation.
    Real command: salloc [flags]."""
    if REAL_MODE:
        cmd = ["salloc"]
        if flags:
            cmd += flags.split()
        return _run_cmd(cmd)
    _STATE._log.append(f"[{_stamp()}] SALLOC {flags}")
    return "salloc mock: Granted job allocation 9001."


@mcp.tool()
def sattach(job_step: str) -> str:
    """Attach I/O to a running job step.
    Real command: sattach <jobid.stepid>."""
    if not job_step.strip():
        return "sattach: error: job_step is required (example: 1001.0)."
    if REAL_MODE:
        return _run_cmd(["sattach", job_step.strip()])
    _STATE._log.append(f"[{_stamp()}] SATTACH {job_step.strip()}")
    return f"sattach mock: attached to {job_step.strip()}."


@mcp.tool()
def sbcast(src_file: str, dest_path: str, job_id: str = "") -> str:
    """Broadcast a file to all nodes in an allocation.
    Real command: sbcast <src_file> <dest_path> [--jobid <id>]."""
    if not src_file.strip() or not dest_path.strip():
        return "sbcast: error: src_file and dest_path are required."
    if REAL_MODE:
        cmd = ["sbcast", src_file.strip(), dest_path.strip()]
        if job_id.strip():
            cmd += ["--jobid", job_id.strip()]
        return _run_cmd(cmd)
    _STATE._log.append(
        f"[{_stamp()}] SBCAST src={src_file.strip()} dest={dest_path.strip()} job={job_id.strip() or 'auto'}"
    )
    return f"sbcast mock: copied {src_file.strip()} to {dest_path.strip()}."


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
    if entity.lower() == "node":
        return _STATE.update_node(id, params)
    if entity.lower() == "partition":
        return _STATE.update_partition(id, params)
    if entity.lower() == "reservation":
        return _STATE.update_reservation(id, params)
    return f"scontrol update {entity} {id}: {params} — unsupported entity in mock mode."


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
def scontrol_suspend(job_id: str) -> str:
    """Suspend a RUNNING job without cancelling it.
    Real command: scontrol suspend <job_id>."""
    if REAL_MODE:
        result = _run_cmd(["scontrol", "suspend", job_id])
        if "error" not in result.lower():
            return f"Job {job_id} suspended."
        return result
    return _STATE.suspend(str(job_id))


@mcp.tool()
def scontrol_resume_job(job_id: str) -> str:
    """Resume a SUSPENDED job back to RUNNING.
    Real command: scontrol resume <job_id>."""
    if REAL_MODE:
        result = _run_cmd(["scontrol", "resume", job_id])
        if "error" not in result.lower():
            return f"Job {job_id} resumed."
        return result
    return _STATE.resume_job(str(job_id))


@mcp.tool()
def sacctmgr_list(entity: str = "user", params: str = "") -> str:
    """List accounting entities (user, account, qos, association, cluster)."""
    if REAL_MODE:
        cmd = ["sacctmgr", "show", entity]
        if params: cmd += params.split()
        cmd += ["--parsable2"]
        return _run_cmd(cmd)
    if entity.lower() == "user":
        # In debug_needed charlie has exhausted his GrpCPUMins (job 5004 pending: AssocGrpCPUMinutesLimit)
        charlie_grp = "10000/10000 (exhausted)" if SCENARIO == "debug_needed" else "10000/-"
        return (
            "User      UID   DefaultAccount  Account   Partition  QOS     MaxCPUs  GrpCPUMins\n"
            f"alice     1000  general         general   cpu        normal  64       -\n"
            f"bob       1001  general         general   cpu        normal  64       -\n"
            f"charlie   1002  general         general   gpu        normal  32       {charlie_grp}\n"
            "dave      1003  research        research  gpu        high    32       -"
        )
    if entity.lower() in {"account", "association", "assoc"}:
        # In debug_needed charlie's association has a GrpCPUMins limit that is now exhausted
        charlie_mins = "10000" if SCENARIO == "debug_needed" else "-"
        charlie_used = " (EXHAUSTED)" if SCENARIO == "debug_needed" else ""
        return (
            "Account   User      Partition  QOS     MaxCPUs  MaxGrpCPUMins\n"
            "general   alice     cpu        normal  64       -\n"
            "general   bob       cpu        normal  64       -\n"
            f"general   charlie   gpu        normal  32       {charlie_mins}{charlie_used}\n"
            "research  dave      gpu        high    32       -"
        )
    if entity.lower() == "qos":
        # In pending scenario charlie has hit QOSMaxJobsPerUserLimit — show charlie at cap
        if SCENARIO == "pending":
            return (
                "Name    Priority  MaxJobs  MaxWall       GrpJobs  MaxJobsPerUser\n"
                "normal  0         50       7-00:00:00    -        5   (charlie: 5/5 LIMIT REACHED)\n"
                "high    10        5        1-00:00:00    -        5"
            )
        return (
            "Name    Priority  MaxJobs  MaxWall       GrpJobs  MaxJobsPerUser\n"
            "normal  0         50       7-00:00:00    -        5\n"
            "high    10        5        1-00:00:00    -        5"
        )
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
    """[INTERNAL EVAL] Action history log for this session. Not for agent use."""
    if REAL_MODE:
        return "cluster_history: not available in real mode (use slurmdbd/sacct)."
    return "=== Cluster Action History ===\n" + _STATE.history()


@mcp.tool()
def reset_mock_state(scenario: str = "", source_state_json: str = "") -> str:
    """[INTERNAL EVAL] Reset mock cluster state to a named scenario.
    - scenario: healthy|failed|pending|mixed|debug_needed (defaults to current SCENARIO)
    - source_state_json: optional JSON string matching dataset source_state shape
    Not for agent use — evaluation infrastructure only.
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
def get_mock_state_snapshot() -> str:
    """[INTERNAL EVAL] Return current mock-state snapshot JSON. Not for agent use."""
    if REAL_MODE:
        return "get_mock_state_snapshot: unavailable in real mode"
    return json.dumps(_STATE.snapshot())


# ── Diagnostic / supplementary tools (not write-ops, supplement Slurm data) ──

@mcp.tool()
def sdiag() -> str:
    """Show Slurm scheduler diagnostics: backfill stats, cycle times, queue depth."""
    if REAL_MODE:
        return _run_cmd(["sdiag"])
    return (  # noqa: W503
        "sdiag — Scheduler Diagnostics\n"
        "Server threads: 3  Agent queue size: 0\n"
        + {
            "healthy":      "Jobs submitted: 42  Jobs started: 38  Jobs completed: 35  Jobs failed: 0\n"
                            "Backfill: last cycle 0.12s  last depth: 4 jobs  last queue length: 4\n",
            "failed":       "Jobs submitted: 15  Jobs started: 15  Jobs completed: 0  Jobs failed: 4\n"
                            "Backfill: last cycle 0.08s  last depth: 1 jobs  last queue length: 1\n",
            "pending":      "Jobs submitted: 18  Jobs started: 5  Jobs completed: 4  Jobs failed: 0\n"
                            "Backfill: last cycle 0.31s  last depth: 4 jobs  last queue length: 4  (high backlog)\n",
            "mixed":        "Jobs submitted: 22  Jobs started: 18  Jobs completed: 3  Jobs failed: 1\n"
                            "Backfill: last cycle 0.18s  last depth: 3 jobs  last queue length: 2\n",
            "debug_needed": "Jobs submitted: 20  Jobs started: 20  Jobs completed: 0  Jobs failed: 6\n"
                            "Backfill: last cycle 0.10s  last depth: 1 jobs  last queue length: 1  (high failure rate)\n",
        }.get(SCENARIO, "Jobs submitted: 42  Jobs started: 38  Jobs completed: 35  Jobs failed: 0\n"
                         "Backfill: last cycle 0.12s  last depth: 4 jobs  last queue length: 4\n")
        + "Main sched: last cycle 0.03s\n"
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
    # Priority values reflect actual pending reasons:
    #   Dependency -> 0 (blocked), QOSMaxJobsPerUserLimit -> 0 (blocked),
    #   Priority -> low value, Resources -> moderate
    REASON_PRIO = {
        "Dependency": (0,    "0.00", "blocked"),
        "QOSMaxJobsPerUserLimit": (0, "0.00", "blocked"),
        "Priority":   (420,  "0.35", "low"),
        "Resources":  (750,  "0.62", "normal"),
    }
    lines = ["JOBID    USER       PRIORITY  FAIRSHARE  AGE  QOS  PARTITION  REASON"]
    for j in jobs:
        jid    = j.get("job_id", "?")
        u      = j.get("user", "?")
        reason = j.get("reason", "Resources")
        prio, fs, _ = REASON_PRIO.get(reason, (750, "0.62", "normal"))
        lines.append(f"{jid:<8} {u:<10} {prio:<9} {fs:<10} 100  1    {j.get('partition','?'):<10} {reason}")
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


def _strip_html_text(raw_html: str) -> str:
    """Extract readable text from HTML without external dependencies."""
    import html as _html

    text = re.sub(
        r"(?is)<(script|style|noscript|svg|iframe|header|footer|nav|form).*?>.*?</\\1>",
        " ",
        raw_html,
    )
    text = re.sub(r"(?is)<br\\s*/?>", "\n", text)
    text = re.sub(r"(?is)</p\\s*>", "\n", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = _html.unescape(text)
    text = text.replace("\r", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _duckduckgo_html_search(query: str, limit: int = 5) -> list[tuple[str, str]]:
    """Scrape DuckDuckGo HTML search for real web results."""
    import urllib.parse
    import urllib.request

    q = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={q}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read(200_000).decode("utf-8", errors="replace")
    except Exception:
        return []

    # Parse result links: <a class="result__a" href="...">title</a>
    # and snippets: <a class="result__snippet" ...>text</a>
    results: list[tuple[str, str]] = []
    seen: set[str] = set()

    # Find all result blocks
    link_pattern = re.compile(
        r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        re.DOTALL,
    )
    snippet_pattern = re.compile(
        r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
        re.DOTALL,
    )

    links = link_pattern.findall(body)
    snippets = snippet_pattern.findall(body)

    for i, (href, title_html) in enumerate(links):
        if len(results) >= limit:
            break
        # Decode DDG redirect URL
        if "uddg=" in href:
            m = re.search(r"uddg=([^&]+)", href)
            if m:
                href = urllib.parse.unquote(m.group(1))
        elif href.startswith("//"):
            href = "https:" + href

        if not href.startswith("http") or href in seen:
            continue
        seen.add(href)

        title = _strip_html_text(title_html).strip()
        snippet = _strip_html_text(snippets[i]).strip() if i < len(snippets) else ""
        text = f"{title} — {snippet}" if snippet else title
        results.append((text, href))

    return results


def _collect_duckduckgo_results(payload: dict[str, Any]) -> list[tuple[str, str]]:
    """Collect (text, url) pairs from DuckDuckGo instant-answer payload."""
    items: list[tuple[str, str]] = []
    seen_urls: set[str] = set()

    def _add_item(text: Any, url: Any) -> None:
        txt = str(text or "").strip()
        link = str(url or "").strip()
        if not txt or not link or link in seen_urls:
            return
        seen_urls.add(link)
        items.append((txt, link))

    for row in payload.get("Results", []) or []:
        if isinstance(row, dict):
            _add_item(row.get("Text"), row.get("FirstURL"))

    def _walk(rows: Any) -> None:
        if not isinstance(rows, list):
            return
        for row in rows:
            if not isinstance(row, dict):
                continue
            _add_item(row.get("Text"), row.get("FirstURL"))
            sub_topics = row.get("Topics")
            if isinstance(sub_topics, list):
                _walk(sub_topics)

    _walk(payload.get("RelatedTopics", []))
    return items


def _fetch_url_text(url: str, max_chars: int = 4000) -> str:
    """Fetch URL and return readable text payload."""
    import urllib.parse
    import urllib.request

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return "Error: only http/https URLs are supported."

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "slurm-agent/1.0 (+mcp-web-fetch)"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        content_type = str(resp.headers.get("Content-Type") or "").lower()
        raw = resp.read(400_000)

    charset = "utf-8"
    if "charset=" in content_type:
        charset = content_type.split("charset=", 1)[1].split(";", 1)[0].strip() or "utf-8"

    body = raw.decode(charset, errors="replace")

    title = ""
    title_match = re.search(r"(?is)<title[^>]*>(.*?)</title>", body)
    if title_match:
        title = _strip_html_text(title_match.group(1))

    if "html" in content_type or "<html" in body[:2000].lower():
        text = _strip_html_text(body)
    else:
        text = body.strip()

    try:
        limit = int(max_chars)
    except Exception:
        limit = 4000
    limit = max(500, min(limit, 20000))

    if len(text) > limit:
        text = text[:limit].rstrip() + f"\n...[truncated {len(text) - limit} chars]"

    lines = [f"URL: {url}"]
    if title:
        lines.append(f"Title: {title}")
    if content_type:
        lines.append(f"Content-Type: {content_type}")
    lines.append("Content:")
    lines.append(text or "(empty response body)")
    return "\n".join(lines)


@mcp.tool()
def web_search(query: str, search_type: str = "general", max_results: int = 5) -> str:
    """Search the web and return URL-bearing snippets.

    search_type: general | slurm | error
    max_results: number of link snippets to return (1..10)
    """
    try:
        import urllib.parse
        import urllib.request

        raw_query = str(query or "").strip()
        if not raw_query:
            return "web_search: query is required."

        mode = str(search_type or "general").strip().lower()
        scoped_query = raw_query
        if mode == "slurm":
            scoped_query = f"site:slurm.schedmd.com {raw_query}"
        elif mode == "error":
            scoped_query = f"slurm {raw_query} error"

        try:
            limit = int(max_results)
        except Exception:
            limit = 5
        limit = max(1, min(limit, 10))

        # Primary: DuckDuckGo HTML search (returns real web results)
        hits = _duckduckgo_html_search(scoped_query, limit)

        # Fallback: Instant Answer API (for factual/wiki queries)
        abstract_text = ""
        abstract_url = ""
        if not hits:
            q = urllib.parse.quote_plus(scoped_query)
            api_url = f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1&skip_disambig=1"
            req = urllib.request.Request(api_url, headers={"User-Agent": "slurm-agent/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            abstract_text = str(data.get("AbstractText") or "").strip()
            abstract_url = str(data.get("AbstractURL") or "").strip()
            hits = _collect_duckduckgo_results(data)

        lines = [
            "[WEB_SEARCH]:",
            f"Query: {raw_query}",
            f"Search type: {mode}",
        ]

        if abstract_text:
            lines.append("Top summary:")
            lines.append(abstract_text)
            if abstract_url:
                lines.append(f"URL: {abstract_url}")

        if hits:
            lines.append("Results:")
            for idx, (text, link) in enumerate(hits[:limit], start=1):
                cleaned = " ".join(text.split())
                if len(cleaned) > 220:
                    cleaned = cleaned[:220].rstrip() + "..."
                lines.append(f"{idx}. {cleaned}")
                lines.append(f"URL: {link}")

        if not abstract_text and not hits:
            lines.append("No results found.")

        lines.append("Tip: call fetch_web_content(url=...) to retrieve full page text.")
        return "\n".join(lines)
    except Exception as e:
        return f"web_search failed: {e}"


@mcp.tool()
def fetch_web_content(url: str, max_chars: int = 4000) -> str:
    """Fetch and extract readable text from a web page URL.

    url: http/https URL to fetch
    max_chars: truncate output to this many chars (500..20000)
    """
    target = str(url or "").strip()
    if not target:
        return "fetch_web_content: url is required."
    try:
        body = _fetch_url_text(target, max_chars=max_chars)
        return "[WEB_FETCH]:\n" + body
    except Exception as e:
        return f"fetch_web_content failed: {e}"


# ── Node management tools ─────────────────────────────────────────────────────

@mcp.tool()
def scontrol_node(node: str, state: str, reason: str = "") -> str:
    """Set a node's administrative state (admin action).
    node (REQUIRED): node name, e.g. 'gpu-node-01'.
    state (REQUIRED): DRAIN | DOWN | RESUME | IDLE.
      DRAIN  — stop scheduling new jobs; current jobs finish normally.
      DOWN   — take node offline immediately.
      RESUME — bring a drained/down node back online (alias: IDLE).
    reason: short text shown in sinfo (required in production for DRAIN/DOWN)."""
    state_upper = state.strip().upper()
    if state_upper not in {"DRAIN", "DOWN", "RESUME", "IDLE"}:
        return f"scontrol: error: Invalid state '{state}'. Use DRAIN, DOWN, RESUME, or IDLE."
    if not node.strip():
        return "scontrol: error: Node name is required."

    if REAL_MODE:
        cmd = ["scontrol", "update", f"NodeName={node}", f"State={state_upper}"]
        if reason:
            cmd += [f"Reason={reason}"]
        return _run_cmd(cmd)

    if state_upper == "DRAIN":
        return _STATE.drain_node(node.strip(), reason)
    elif state_upper == "DOWN":
        return _STATE.set_node_down(node.strip(), reason)
    else:
        return _STATE.resume_node(node.strip())


@mcp.tool()
def scontrol_create_reservation(params: str) -> str:
    """Create a Slurm reservation (admin only, requires HITL approval).
    params: space-separated key=value pairs.
    Example: "ReservationName=maint StartTime=2026-04-22T00:00:00 EndTime=2026-04-22T08:00:00 Nodes=cpu-node-01 Flags=MAINT Users=root"
    Returns the name of the created reservation on success."""
    if not params.strip():
        return "scontrol: error: params are required. Include ReservationName, StartTime, EndTime, Nodes."
    if REAL_MODE:
        return _run_cmd(["scontrol", "create", "reservation"] + params.split())
    return _STATE.create_reservation(params)


@mcp.tool()
def scontrol_delete_reservation(reservation: str) -> str:
    """Delete a named Slurm reservation (admin only, requires HITL approval).
    reservation (REQUIRED): exact name of the reservation to delete."""
    if not reservation.strip():
        return "scontrol: error: Reservation name is required."
    if REAL_MODE:
        return _run_cmd(["scontrol", "delete", f"ReservationName={reservation}"])
    return _STATE.delete_reservation(reservation.strip())


# ── Read-only supplementary tools ─────────────────────────────────────────────

@mcp.tool()
def sreport(report_type: str = "cluster", params: str = "") -> str:
    """Generate a Slurm usage report (CPU-hours, GPU-hours) by user, account, or partition.
    report_type: cluster | user | account | job  (default: cluster)
    params: optional filters, e.g. "Start=now-7days End=now TopCount=10"
    Returns a tabular summary of resource consumption for the requested period."""
    if REAL_MODE:
        cmd = ["sreport", report_type, "utilization", "-t", "Hours", "--parsable2", "--noheader"]
        if params:
            cmd += params.split()
        return _run_cmd(cmd)
    # Usage numbers align with sshare EffectvUsage per scenario
    _SREPORT = {
        "healthy":      [("alice","research",420,168,12),("bob","general",280,0,8),("charlie","general",140,0,5)],
        "failed":       [("alice","research",510,204,15),("bob","general",290,0,8),("charlie","general",130,0,4)],
        "pending":      [("alice","research",820,336,24),("bob","general",210,0,6),("charlie","general",80,0,3)],
        "mixed":        [("alice","research",560,210,16),("bob","general",310,0,9),("charlie","general",155,0,5)],
        "debug_needed": [("alice","research",440,180,13),("bob","general",280,0,8),("charlie","general",130,0,4)],
    }
    data = _SREPORT.get(SCENARIO, _SREPORT["healthy"])
    header = (
        "Cluster Usage Report (last 7 days)\n"
        f"{'User':<12} {'Account':<12} {'CPUHours':>10} {'GPUHours':>10} {'Jobs':>6}\n"
        + "-" * 54 + "\n"
    )
    rows = "".join(f"{u:<12} {a:<12} {c:>10}        {g:>4}     {j:>2}\n" for u, a, c, g, j in data)
    total_c = sum(r[2] for r in data)
    total_g = sum(r[3] for r in data)
    total_j = sum(r[4] for r in data)
    return header + rows + "-" * 54 + f"\nTotal                          {total_c}        {total_g:>4}     {total_j}\n"


@mcp.tool()
def scontrol_license() -> str:
    """Show available software licenses tracked by Slurm: name, total, in-use, and free count."""
    if REAL_MODE:
        return _run_cmd(["scontrol", "show", "licenses"])
    return (
        "LicenseName  Total  Used  Free  Remote\n"
        "matlab          20    12     8  no\n"
        "ansys            4     2     2  no\n"
        "comsol           2     0     2  no\n"
        "gaussian         8     5     3  no\n"
    )


@mcp.tool()
def scontrol_reservation_show(reservation: str = "") -> str:
    """List all Slurm reservations or show details of a specific one.
    reservation: optional name to filter. Empty returns all reservations."""
    if REAL_MODE:
        cmd = ["scontrol", "show", "reservation"]
        if reservation.strip():
            cmd.append(reservation.strip())
        return _run_cmd(cmd)
    reservations = _STATE.list_reservations()
    if reservation.strip():
        reservations = [
            r for r in reservations
            if str(r.get("ReservationName", "")).lower() == reservation.strip().lower()
        ]
        if not reservations:
            return f"scontrol: error: Reservation {reservation.strip()} not found."
    if not reservations:
        return "(0 reservations found)"
    lines = []
    for r in reservations:
        lines.append(
            f"ReservationName={r.get('ReservationName','?')} "
            f"StartTime={r.get('StartTime','?')} EndTime={r.get('EndTime','?')}\n"
            f"   Nodes={r.get('Nodes','')} Flags={r.get('Flags','')} Users={r.get('Users','')} "
            f"State={r.get('State','INACTIVE')}"
        )
    lines.append(f"\n({len(reservations)} reservation{'s' if len(reservations) != 1 else ''} found)")
    return "\n\n".join(lines)


@mcp.tool()
def sshare(user: str = "", account: str = "") -> str:
    """Show fairshare usage and effective shares.
    Real command: sshare -l."""
    if REAL_MODE:
        cmd = ["sshare", "-l"]
        if user:
            cmd += ["--users", user]
        if account:
            cmd += ["--accounts", account]
        return _run_cmd(cmd)
    # Fairshare varies by scenario: pending = alice heavy usage, debug_needed = charlie at cap
    _SSHARE = {
        "healthy":      [("root","root",1.0,1.0,0.0),("research","alice",0.6,0.42,1.8),("general","bob",0.3,0.38,0.7),("general","charlie",0.1,0.20,0.4)],
        "failed":       [("root","root",1.0,1.0,0.0),("research","alice",0.6,0.55,2.1),("general","bob",0.3,0.30,0.8),("general","charlie",0.1,0.15,0.3)],
        "pending":      [("root","root",1.0,1.0,0.0),("research","alice",0.6,0.71,3.9),("general","bob",0.3,0.20,0.5),("general","charlie",0.1,0.09,0.2)],
        "mixed":        [("root","root",1.0,1.0,0.0),("research","alice",0.6,0.50,2.4),("general","bob",0.3,0.35,0.9),("general","charlie",0.1,0.15,0.4)],
        "debug_needed": [("root","root",1.0,1.0,0.0),("research","alice",0.6,0.44,2.0),("general","bob",0.3,0.38,0.7),("general","charlie",0.1,0.18,0.3)],
    }
    rows = _SSHARE.get(SCENARIO, _SSHARE["healthy"])
    if user:
        rows = [r for r in rows if r[1].lower() == user.lower()]
    if account:
        rows = [r for r in rows if r[0].lower() == account.lower()]
    if not rows:
        return "No fairshare records found."
    out = ["Account       User       RawShares  NormShares  EffectvUsage"]
    out.append("-" * 60)
    for acct, usr, raw_s, norm_s, usage in rows:
        out.append(f"{acct:<12} {usr:<10} {raw_s:<9.3f} {norm_s:<10.3f} {usage:<12.3f}")
    return "\n".join(out)


@mcp.tool()
def scontrol_show_config() -> str:
    """Show Slurm controller configuration values.
    Real command: scontrol show config."""
    if REAL_MODE:
        return _run_cmd(["scontrol", "show", "config"])
    cfg = _STATE._config
    lines = [f"{k}={v}" for k, v in sorted(cfg.items())]
    return "\n".join(lines)


@mcp.tool()
def scontrol_ping() -> str:
    """Check whether slurmctld is responsive.
    Real command: scontrol ping."""
    if REAL_MODE:
        return _run_cmd(["scontrol", "ping"])
    return "Slurmctld(primary) at mock-cluster is UP"


@mcp.tool()
def scontrol_show_topology() -> str:
    """Show network topology as seen by Slurm.
    Real command: scontrol show topology."""
    if REAL_MODE:
        return _run_cmd(["scontrol", "show", "topology"])
    nodes = _nodes()
    if not nodes:
        return "No topology data available."
    lines = ["SwitchName=switch0 Nodes=" + ",".join(sorted(n.get("name", "?") for n in nodes))]
    return "\n".join(lines)


@mcp.tool()
def scontrol_show_step(job_id: str) -> str:
    """Show step-level information for a job.
    Real command: scontrol show step <jobid>."""
    if not job_id.strip():
        return "scontrol: error: job_id is required for show step."
    if REAL_MODE:
        return _run_cmd(["scontrol", "show", "step", job_id.strip()])
    jobs = _jobs()
    j = next((x for x in jobs if str(x.get("job_id", "")) == job_id.strip()), None)
    if not j:
        return f"scontrol: error: Invalid job id specified: {job_id}"
    return (
        f"StepId={job_id}.0 JobId={job_id} Name={j.get('name','?')}.batch\n"
        f"   State={j.get('state','?')} Nodes={j.get('nodes','1')} CPUs={j.get('cpus','1')} Mem={j.get('mem','?')}"
    )


@mcp.tool()
def scontrol_show_federation() -> str:
    """Show federation status for multi-cluster Slurm.
    Real command: scontrol show federation."""
    if REAL_MODE:
        return _run_cmd(["scontrol", "show", "federation"])
    return "FederationName=mock-federation Clusters=mock-cluster State=ACTIVE"


@mcp.tool()
def scontrol_show_burstbuffer() -> str:
    """Show burst buffer state.
    Real command: scontrol show burst_buffer."""
    if REAL_MODE:
        return _run_cmd(["scontrol", "show", "burst_buffer"])
    return "BurstBufferName=bb0 TotalSpace=100T FreeSpace=78T StageInOps=0 StageOutOps=0"


@mcp.tool()
def sinfo_reasons() -> str:
    """List nodes in down/drain states with reasons.
    Real command: sinfo -R."""
    if REAL_MODE:
        return _run_cmd(["sinfo", "-R"])
    bad = [n for n in _nodes() if any(x in str(n.get("state", "")).lower() for x in ("down", "drain"))]
    if not bad:
        return "No nodes are down or drained."
    lines = ["NODELIST        STATE     REASON"]
    lines.append("-" * 56)
    for n in bad:
        lines.append(f"{n.get('name','?'):<14} {n.get('state','?'):<9} {n.get('reason','none')}")
    return "\n".join(lines)


@mcp.tool()
def sinfo_node(partition: str = "", state: str = "") -> str:
    """Show one row per node.
    Real command: sinfo --Node [--partition ...] [--states ...]."""
    if REAL_MODE:
        cmd = ["sinfo", "--Node"]
        if partition:
            cmd += ["--partition", partition]
        if state:
            cmd += ["--states", state]
        return _run_cmd(cmd)
    nodes = _nodes()
    if partition:
        nodes = [n for n in nodes if str(n.get("partition", "")).lower() == partition.lower()]
    if state:
        wanted = {x.strip().lower() for x in state.split(",") if x.strip()}
        nodes = [n for n in nodes if str(n.get("state", "")).lower() in wanted]
    return _fmt_nodes(nodes)


@mcp.tool()
def squeue_steps(job_id: str = "", user: str = "", state: str = "") -> str:
    """Show job steps (not only top-level jobs).
    Real command: squeue --steps."""
    if REAL_MODE:
        cmd = ["squeue", "--steps"]
        if job_id:
            cmd += ["--jobs", job_id]
        if user:
            cmd += ["--user", user]
        if state:
            cmd += ["--states", state]
        return _run_cmd(cmd)
    jobs = _jobs()
    if job_id:
        jobs = [j for j in jobs if str(j.get("job_id", "")) == str(job_id)]
    if user:
        jobs = [j for j in jobs if str(j.get("user", "")).lower() == user.lower()]
    if state:
        wanted = {x.strip().upper() for x in state.split(",") if x.strip()}
        jobs = [j for j in jobs if str(j.get("state", "")).upper() in wanted]
    if not jobs:
        return "No job steps found."
    lines = ["STEPID         JOBID    USER     STATE     PARTITION"]
    lines.append("-" * 64)
    for j in jobs:
        jid = str(j.get("job_id", "?"))
        lines.append(f"{jid}.0{'':<9} {jid:<8} {j.get('user','?'):<8} {j.get('state','?'):<9} {j.get('partition','?')}")
    return "\n".join(lines)


@mcp.tool()
def squeue_reservation(reservation: str) -> str:
    """Show queue entries tied to a reservation.
    Real command: squeue --reservation=<name>."""
    if not reservation.strip():
        return "squeue: error: reservation name is required."
    if REAL_MODE:
        return _run_cmd(["squeue", f"--reservation={reservation.strip()}"])
    jobs = [j for j in _jobs() if str(j.get("reservation", "")).lower() == reservation.strip().lower()]
    if not jobs:
        return f"No jobs found in reservation {reservation.strip()}."
    return _fmt_jobs(jobs)


@mcp.tool()
def sprio_weights() -> str:
    """Show configured priority weights.
    Real command: sprio --weights."""
    if REAL_MODE:
        return _run_cmd(["sprio", "--weights"])
    return (
        "Priority Weights\n"
        "  PriorityWeightAge=1000\n"
        "  PriorityWeightFairshare=10000\n"
        "  PriorityWeightJobSize=100\n"
        "  PriorityWeightPartition=500\n"
        "  PriorityWeightQOS=1000\n"
    )


@mcp.tool()
def scontrol_node_power_down(node: str, reason: str = "power_save") -> str:
    """Power down a node administratively.
    Real command: scontrol update NodeName=<node> State=POWER_DOWN [Reason=...]."""
    if not node.strip():
        return "scontrol: error: Node name is required."
    if REAL_MODE:
        cmd = ["scontrol", "update", f"NodeName={node.strip()}", "State=POWER_DOWN"]
        if reason:
            cmd.append(f"Reason={reason}")
        return _run_cmd(cmd)
    return _STATE.update_node(node.strip(), f"State=power_down Reason={reason or 'power_save'}")


@mcp.tool()
def scontrol_node_power_up(node: str) -> str:
    """Power up a node administratively.
    Real command: scontrol update NodeName=<node> State=POWER_UP."""
    if not node.strip():
        return "scontrol: error: Node name is required."
    if REAL_MODE:
        return _run_cmd(["scontrol", "update", f"NodeName={node.strip()}", "State=POWER_UP"])
    return _STATE.update_node(node.strip(), "State=idle")


@mcp.tool()
def scontrol_node_features(node: str, features: str) -> str:
    """Set node feature labels.
    Real command: scontrol update NodeName=<node> Features=<features>."""
    if not node.strip() or not features.strip():
        return "scontrol: error: node and features are required."
    if REAL_MODE:
        return _run_cmd(["scontrol", "update", f"NodeName={node.strip()}", f"Features={features.strip()}"])
    return _STATE.update_node(node.strip(), f"Features={features.strip()}")


@mcp.tool()
def scontrol_node_gres(node: str, gres: str) -> str:
    """Set node GRES labels.
    Real command: scontrol update NodeName=<node> Gres=<gres>."""
    if not node.strip() or not gres.strip():
        return "scontrol: error: node and gres are required."
    if REAL_MODE:
        return _run_cmd(["scontrol", "update", f"NodeName={node.strip()}", f"Gres={gres.strip()}"])
    return _STATE.update_node(node.strip(), f"Gres={gres.strip()}")


@mcp.tool()
def scontrol_node_weight(node: str, weight: int) -> str:
    """Set scheduling weight for a node.
    Real command: scontrol update NodeName=<node> Weight=<weight>."""
    if not node.strip():
        return "scontrol: error: node is required."
    if REAL_MODE:
        return _run_cmd(["scontrol", "update", f"NodeName={node.strip()}", f"Weight={int(weight)}"])
    return _STATE.update_node(node.strip(), f"Weight={int(weight)}")


@mcp.tool()
def scontrol_update_reservation(reservation: str, params: str) -> str:
    """Update an existing reservation.
    Real command: scontrol update ReservationName=<reservation> <params>."""
    if not reservation.strip():
        return "scontrol: error: reservation is required."
    if REAL_MODE:
        return _run_cmd(["scontrol", "update", f"ReservationName={reservation.strip()}"] + params.split())
    return _STATE.update_reservation(reservation.strip(), params)


@mcp.tool()
def scontrol_write_config() -> str:
    """Persist current in-memory config.
    Real command: scontrol write config."""
    if REAL_MODE:
        return _run_cmd(["scontrol", "write", "config"])
    _STATE._log.append(f"[{_stamp()}] WRITE_CONFIG")
    return "scontrol write config: configuration persisted (mock)."


@mcp.tool()
def scontrol_setdebug(level: str) -> str:
    """Set slurmctld debug level.
    Real command: scontrol setdebug <level>."""
    if not level.strip():
        return "scontrol: error: debug level is required."
    if REAL_MODE:
        return _run_cmd(["scontrol", "setdebug", level.strip()])
    _STATE._config["SlurmctldDebug"] = level.strip().lower()
    _STATE._log.append(f"[{_stamp()}] SETDEBUG {level.strip().lower()}")
    return f"SlurmctldDebug set to {level.strip().lower()}."


@mcp.tool()
def scontrol_token(lifespan: str = "3600") -> str:
    """Generate an auth token for Slurm REST API.
    Real command: scontrol token lifespan=<seconds>."""
    if REAL_MODE:
        return _run_cmd(["scontrol", "token", f"lifespan={lifespan}"])
    ttl = lifespan.strip() or "3600"
    return f"SLURM_JWT=mock-token-{ttl}-seconds"


@mcp.tool()
def scontrol_shutdown(mode: str = "graceful") -> str:
    """Shutdown Slurm controllers.
    Real command: scontrol shutdown [mode]."""
    if REAL_MODE:
        cmd = ["scontrol", "shutdown"]
        if mode.strip():
            cmd.append(mode.strip())
        return _run_cmd(cmd)
    _STATE._log.append(f"[{_stamp()}] SHUTDOWN mode={mode.strip() or 'graceful'}")
    return f"scontrol shutdown ({mode.strip() or 'graceful'}) accepted (mock)."


@mcp.tool()
def scontrol_show_aliases() -> str:
    """Show configured command aliases.
    Real command: scontrol show aliases."""
    if REAL_MODE:
        return _run_cmd(["scontrol", "show", "aliases"])
    return "alias cancel_gpu='scancel --partition=gpu'\nalias quick_sinfo='sinfo --Node'"


@mcp.tool()
def sacctmgr_show_problems() -> str:
    """Show accounting DB consistency problems.
    Real command: sacctmgr show problems."""
    if REAL_MODE:
        return _run_cmd(["sacctmgr", "show", "problems"])
    if SCENARIO == "debug_needed":
        return (
            "Association charlie/general/gpu — GrpCPUMins limit reached "
            "(used 10000 of 10000). Jobs will remain PENDING until next accounting window.\n"
            "Run: sacctmgr modify user charlie set GrpCPUMins=-1 — to remove limit."
        )
    if SCENARIO == "pending":
        return (
            "QOS normal — user charlie has reached MaxJobsPerUser limit (5/5). "
            "Additional job submissions will be held.\n"
            "Run: sacctmgr modify qos normal set MaxJobsPerUser=0 — to remove limit."
        )
    return "No accounting problems found."


@mcp.tool()
def sacctmgr_recalc(scope: str = "") -> str:
    """Recalculate fairshare/accounting usage.
    Real command: sacctmgr recalc [scope]."""
    if REAL_MODE:
        cmd = ["sacctmgr", "recalc"]
        if scope:
            cmd += scope.split()
        return _run_cmd(cmd)
    _STATE._log.append(f"[{_stamp()}] SACCTMGR RECALC {scope}".rstrip())
    return "sacctmgr recalc completed (mock)."


@mcp.tool()
def sacctmgr_archive(params: str = "") -> str:
    """Archive accounting records.
    Real command: sacctmgr archive <params>."""
    if REAL_MODE:
        cmd = ["sacctmgr", "archive"]
        if params:
            cmd += params.split()
        return _run_cmd(cmd)
    _STATE._log.append(f"[{_stamp()}] SACCTMGR ARCHIVE {params}".rstrip())
    return "sacctmgr archive completed (mock)."


@mcp.tool()
def sacctmgr_load(file_path: str) -> str:
    """Load archived accounting data.
    Real command: sacctmgr load <file>."""
    if not file_path.strip():
        return "sacctmgr load: error: file_path is required."
    if REAL_MODE:
        return _run_cmd(["sacctmgr", "load", file_path.strip()])
    _STATE._log.append(f"[{_stamp()}] SACCTMGR LOAD {file_path.strip()}")
    return f"sacctmgr load completed from {file_path.strip()} (mock)."


@mcp.tool()
def sacctmgr_dump(file_path: str = "") -> str:
    """Dump accounting DB snapshot.
    Real command: sacctmgr dump [file]."""
    if REAL_MODE:
        cmd = ["sacctmgr", "dump"]
        if file_path.strip():
            cmd.append(file_path.strip())
        return _run_cmd(cmd)
    target = file_path.strip() or "/tmp/sacctmgr_dump.mock"
    _STATE._log.append(f"[{_stamp()}] SACCTMGR DUMP {target}")
    return f"sacctmgr dump written to {target} (mock)."


@mcp.tool()
def strigger_set(spec: str) -> str:
    """Create a Slurm trigger.
    Real command: strigger --set <spec>."""
    if not spec.strip():
        return "strigger: error: trigger spec is required."
    if REAL_MODE:
        return _run_cmd(["strigger", "--set"] + spec.split())
    trig_id = _STATE.create_trigger(spec)
    return f"Trigger {trig_id} set: {spec.strip()}"


@mcp.tool()
def strigger_get() -> str:
    """List active triggers.
    Real command: strigger --get."""
    if REAL_MODE:
        return _run_cmd(["strigger", "--get"])
    triggers = _STATE.list_triggers()
    if not triggers:
        return "No active triggers."
    lines = ["TRIGGERID   SPEC"]
    lines.append("-" * 64)
    for t in triggers:
        lines.append(f"{t.get('id','?'):<10} {t.get('spec','')}")
    return "\n".join(lines)


@mcp.tool()
def strigger_clear(trigger_id: str = "") -> str:
    """Clear one trigger or all triggers.
    Real command: strigger --clear [--id=<id>]."""
    if REAL_MODE:
        cmd = ["strigger", "--clear"]
        if trigger_id.strip():
            cmd += [f"--id={trigger_id.strip()}"]
        return _run_cmd(cmd)
    return _STATE.clear_trigger(trigger_id.strip())


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
