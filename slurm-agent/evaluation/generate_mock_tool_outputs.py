"""Generate mock_tool_outputs_5x64.json
─────────────────────────────────────
Canonical per-scenario tool outputs for EVERY mock-MCP tool,
with ALL meaningful parameter variants per tool.

Shape: { scenario: { tool_key: output_string } }
  5 scenarios × ~140 key variants = ~700 total entries.

Key naming convention:
  {tool_name}                       bare / no-arg call
  {tool_name}__{param}_{value}      single param variant
  {tool_name}__{p1}_{v1}__{p2}_{v2} multiple param variant

Usage (run from slurm-agent/evaluation/):
    python generate_mock_tool_outputs.py

Output: slurm-agent/evaluation/mock_tool_outputs_5x64.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# ── Make mcp-server importable ────────────────────────────────────────────────
MCP_DIR = Path(__file__).parent.parent / "mcp-server"
sys.path.insert(0, str(MCP_DIR))

import slurm_mcp_sse as m  # noqa: E402  (path must be set first)

SCENARIOS = ["healthy", "failed", "pending", "mixed", "debug_needed"]

# ── Representative job IDs per scenario ──────────────────────────────────────
# One RUNNING job (sstat, suspend, show_step, scancel, …)
_RUNNING = {
    "healthy":      "1001",   # alice RUNNING
    "failed":       "2004",   # alice RUNNING
    "pending":      "3005",   # bob   RUNNING
    "mixed":        "4001",   # alice RUNNING
    "debug_needed": "5008",   # bob   RUNNING
}
# One PENDING job (hold/release)
_PENDING = {
    "healthy":      "1004",   # charlie
    "failed":       None,
    "pending":      "3001",   # alice
    "mixed":        "4003",   # charlie
    "debug_needed": "5004",   # alice
}
# One FAILED/terminal job (requeue)
_FAILED = {
    "healthy":      None,
    "failed":       "2001",   # alice
    "pending":      None,
    "mixed":        "4002",   # bob
    "debug_needed": "5001",   # alice
}
# Charlie's first job (used for user-scoped queries)
_CHARLIE_JOB = {
    "healthy":      "1004",
    "failed":       "2003",
    "pending":      "3003",
    "mixed":        "4006",
    "debug_needed": "5006",
}


def _call(fn, *args, **kwargs) -> str:
    """Invoke a mock tool, returning its string output."""
    try:
        result = fn(*args, **kwargs)
        return str(result) if result is not None else ""
    except Exception as exc:  # noqa: BLE001
        return f"ERROR: {exc}"


def _reset(scenario: str) -> None:
    """Reset cluster state to a clean snapshot for *scenario*."""
    m.SCENARIO = scenario
    m._STATE.reset(scenario)


# ─────────────────────────────────────────────────────────────────────────────

def _collect(scenario: str) -> dict[str, str]:  # noqa: C901 (complexity OK here)
    running  = _RUNNING[scenario]
    pending  = _PENDING[scenario]
    failed   = _FAILED[scenario]
    charlie  = _CHARLIE_JOB[scenario]

    out: dict[str, str] = {}

    # ══════════════════════════════════════════════════════════════════════════
    # READ-ONLY tools — captured from a single clean reset
    # ══════════════════════════════════════════════════════════════════════════
    _reset(scenario)
    nodes = m._nodes()
    first_node = nodes[0]["name"] if nodes else "cpu-node-01"
    gpu_node   = next((n["name"] for n in nodes if "gpu" in n.get("partition","").lower()), first_node)
    cpu_node   = next((n["name"] for n in nodes if "cpu" in n.get("partition","").lower()), first_node)

    # ── squeue ────────────────────────────────────────────────────────────────
    out["squeue"]                           = _call(m.squeue)
    out["squeue__user_alice"]               = _call(m.squeue, user="alice")
    out["squeue__user_bob"]                 = _call(m.squeue, user="bob")
    out["squeue__user_charlie"]             = _call(m.squeue, user="charlie")
    out["squeue__state_RUNNING"]            = _call(m.squeue, state="RUNNING")
    out["squeue__state_PENDING"]            = _call(m.squeue, state="PENDING")
    out["squeue__state_FAILED"]             = _call(m.squeue, state="FAILED")
    out["squeue__state_ALL"]                = _call(m.squeue, state="ALL")
    out["squeue__partition_gpu"]            = _call(m.squeue, partition="gpu")
    out["squeue__partition_cpu"]            = _call(m.squeue, partition="cpu")
    out["squeue__job_id_running"]           = _call(m.squeue, job_id=running)
    out["squeue__job_id_charlie"]           = _call(m.squeue, job_id=charlie)

    # ── sinfo ─────────────────────────────────────────────────────────────────
    out["sinfo"]                            = _call(m.sinfo)
    out["sinfo__partition_gpu"]             = _call(m.sinfo, partition="gpu")
    out["sinfo__partition_cpu"]             = _call(m.sinfo, partition="cpu")
    out["sinfo__node_gpu"]                  = _call(m.sinfo, node=gpu_node)
    out["sinfo__node_cpu"]                  = _call(m.sinfo, node=cpu_node)

    # ── sinfo_node ────────────────────────────────────────────────────────────
    out["sinfo_node"]                       = _call(m.sinfo_node)
    out["sinfo_node__partition_gpu"]        = _call(m.sinfo_node, partition="gpu")
    out["sinfo_node__partition_cpu"]        = _call(m.sinfo_node, partition="cpu")

    # ── sinfo_reasons ─────────────────────────────────────────────────────────
    out["sinfo_reasons"]                    = _call(m.sinfo_reasons)

    # ── sacct ─────────────────────────────────────────────────────────────────
    out["sacct"]                            = _call(m.sacct)
    out["sacct__user_alice"]                = _call(m.sacct, user="alice")
    out["sacct__user_bob"]                  = _call(m.sacct, user="bob")
    out["sacct__user_charlie"]              = _call(m.sacct, user="charlie")
    out["sacct__state_FAILED"]              = _call(m.sacct, state="FAILED")
    out["sacct__state_COMPLETED"]           = _call(m.sacct, state="COMPLETED")
    out["sacct__state_TIMEOUT"]             = _call(m.sacct, state="TIMEOUT")
    out["sacct__state_CANCELLED"]           = _call(m.sacct, state="CANCELLED")

    # ── scontrol show ─────────────────────────────────────────────────────────
    out["scontrol_show__job"]               = _call(m.scontrol_show, entity="job")
    out["scontrol_show__job_running"]       = _call(m.scontrol_show, entity="job", id=running)
    out["scontrol_show__job_charlie"]       = _call(m.scontrol_show, entity="job", id=charlie)
    out["scontrol_show__node"]              = _call(m.scontrol_show, entity="node")
    out["scontrol_show__node_gpu"]          = _call(m.scontrol_show, entity="node", id=gpu_node)
    out["scontrol_show__node_cpu"]          = _call(m.scontrol_show, entity="node", id=cpu_node)
    out["scontrol_show__partition"]         = _call(m.scontrol_show, entity="partition")
    out["scontrol_show__partition_gpu"]     = _call(m.scontrol_show, entity="partition", id="gpu")
    out["scontrol_show__partition_cpu"]     = _call(m.scontrol_show, entity="partition", id="cpu")

    # ── scontrol_show_step ────────────────────────────────────────────────────
    out["scontrol_show_step__running"]      = _call(m.scontrol_show_step, job_id=running)

    # ── scontrol read-only config tools ───────────────────────────────────────
    out["scontrol_show_config"]             = _call(m.scontrol_show_config)
    out["scontrol_show_topology"]           = _call(m.scontrol_show_topology)
    out["scontrol_show_federation"]         = _call(m.scontrol_show_federation)
    out["scontrol_show_burstbuffer"]        = _call(m.scontrol_show_burstbuffer)
    out["scontrol_show_aliases"]            = _call(m.scontrol_show_aliases)
    out["scontrol_license"]                 = _call(m.scontrol_license)
    out["scontrol_ping"]                    = _call(m.scontrol_ping)

    # ── scontrol_reservation_show ─────────────────────────────────────────────
    out["scontrol_reservation_show"]                    = _call(m.scontrol_reservation_show)
    out["scontrol_reservation_show__maintenance"]       = _call(m.scontrol_reservation_show,
                                                                 reservation="maintenance")

    # ── sstat ─────────────────────────────────────────────────────────────────
    out["sstat__running"]                   = _call(m.sstat, job_id=running)

    # ── sprio ─────────────────────────────────────────────────────────────────
    out["sprio"]                            = _call(m.sprio)
    out["sprio__user_alice"]                = _call(m.sprio, user="alice")
    out["sprio__user_charlie"]              = _call(m.sprio, user="charlie")
    out["sprio__partition_gpu"]             = _call(m.sprio, partition="gpu")
    out["sprio__partition_cpu"]             = _call(m.sprio, partition="cpu")

    # ── sprio_weights ─────────────────────────────────────────────────────────
    out["sprio_weights"]                    = _call(m.sprio_weights)

    # ── sshare ────────────────────────────────────────────────────────────────
    out["sshare"]                           = _call(m.sshare)
    out["sshare__user_alice"]               = _call(m.sshare, user="alice")
    out["sshare__user_bob"]                 = _call(m.sshare, user="bob")
    out["sshare__user_charlie"]             = _call(m.sshare, user="charlie")
    out["sshare__account_general"]          = _call(m.sshare, account="general")
    out["sshare__account_research"]         = _call(m.sshare, account="research")

    # ── sreport ───────────────────────────────────────────────────────────────
    out["sreport__cluster"]                 = _call(m.sreport, report_type="cluster")
    out["sreport__user"]                    = _call(m.sreport, report_type="user")
    out["sreport__account"]                 = _call(m.sreport, report_type="account")
    out["sreport__job"]                     = _call(m.sreport, report_type="job")

    # ── sdiag ─────────────────────────────────────────────────────────────────
    out["sdiag"]                            = _call(m.sdiag)

    # ── sacctmgr_list ─────────────────────────────────────────────────────────
    out["sacctmgr_list__user"]              = _call(m.sacctmgr_list, entity="user")
    out["sacctmgr_list__account"]           = _call(m.sacctmgr_list, entity="account")
    out["sacctmgr_list__assoc"]             = _call(m.sacctmgr_list, entity="assoc")
    out["sacctmgr_list__qos"]               = _call(m.sacctmgr_list, entity="qos")
    out["sacctmgr_list__cluster"]           = _call(m.sacctmgr_list, entity="cluster")

    # ── sacctmgr_show_problems ────────────────────────────────────────────────
    out["sacctmgr_show_problems"]           = _call(m.sacctmgr_show_problems)

    # ── squeue_steps ──────────────────────────────────────────────────────────
    out["squeue_steps"]                     = _call(m.squeue_steps)
    out["squeue_steps__user_alice"]         = _call(m.squeue_steps, user="alice")
    out["squeue_steps__user_charlie"]       = _call(m.squeue_steps, user="charlie")
    out["squeue_steps__state_RUNNING"]      = _call(m.squeue_steps, state="RUNNING")
    out["squeue_steps__state_PENDING"]      = _call(m.squeue_steps, state="PENDING")
    out["squeue_steps__job_running"]        = _call(m.squeue_steps, job_id=running)

    # ── squeue_reservation ────────────────────────────────────────────────────
    out["squeue_reservation__maintenance"]  = _call(m.squeue_reservation,
                                                     reservation="maintenance")

    # ── strigger_get ──────────────────────────────────────────────────────────
    out["strigger_get"]                     = _call(m.strigger_get)

    # ── cluster_history / snapshot ────────────────────────────────────────────
    out["cluster_history"]                  = _call(m.cluster_history)
    out["get_mock_state_snapshot"]          = _call(m.get_mock_state_snapshot)

    # ══════════════════════════════════════════════════════════════════════════
    # STATEFUL ACTION tools — each group resets before calling
    # ══════════════════════════════════════════════════════════════════════════

    # ── scontrol_hold / scontrol_release ──────────────────────────────────────
    _reset(scenario)
    if pending:
        out["scontrol_hold__pending"]       = _call(m.scontrol_hold, job_id=pending)
        # release the held job (state is now HOLD from previous call)
        out["scontrol_release__pending"]    = _call(m.scontrol_release, job_id=pending)
    else:
        out["scontrol_hold__pending"]       = f"(no pending job in '{scenario}')"
        out["scontrol_release__pending"]    = f"(no pending job in '{scenario}')"

    # ── scontrol_requeue ──────────────────────────────────────────────────────
    _reset(scenario)
    if failed:
        out["scontrol_requeue__failed"]     = _call(m.scontrol_requeue, job_id=failed)
    else:
        out["scontrol_requeue__failed"]     = f"(no failed/terminal job in '{scenario}')"

    # ── scontrol_suspend / scontrol_resume_job ────────────────────────────────
    _reset(scenario)
    out["scontrol_suspend__running"]        = _call(m.scontrol_suspend, job_id=running)
    # job is now SUSPENDED — resume it
    out["scontrol_resume_job__suspended"]   = _call(m.scontrol_resume_job, job_id=running)

    # ── scontrol_update ───────────────────────────────────────────────────────
    _reset(scenario)
    out["scontrol_update__job_priority"]    = _call(m.scontrol_update, entity="job",
                                                     id=running, params="Priority=5000")
    out["scontrol_update__job_timelimit"]   = _call(m.scontrol_update, entity="job",
                                                     id=running, params="TimeLimit=01:00:00")
    out["scontrol_update__node_reason"]     = _call(m.scontrol_update, entity="node",
                                                     id=first_node, params="Reason=lookup_test")
    out["scontrol_update__partition_state"] = _call(m.scontrol_update, entity="partition",
                                                     id="cpu", params="State=UP")

    # ── scontrol_reconfigure ──────────────────────────────────────────────────
    out["scontrol_reconfigure"]             = _call(m.scontrol_reconfigure)

    # ── scancel ───────────────────────────────────────────────────────────────
    _reset(scenario)
    out["scancel__running"]                 = _call(m.scancel, job_id=running)
    _reset(scenario)
    out["scancel__charlie_job"]             = _call(m.scancel, job_id=charlie)
    _reset(scenario)
    # cancel two jobs at once (running + charlie's job if different)
    two = running if running == charlie else f"{running},{charlie}"
    out["scancel__multi"]                   = _call(m.scancel, job_id=two)

    # ── sbatch ────────────────────────────────────────────────────────────────
    _reset(scenario)
    out["sbatch__inline"]                   = _call(m.sbatch,
        script="#!/bin/bash\n#SBATCH --job-name=test\necho hello")
    out["sbatch__with_gpu_flags"]           = _call(m.sbatch,
        script="#!/bin/bash\n#SBATCH --job-name=gpu_test\necho gpu",
        flags="--partition=gpu --gres=gpu:1")
    out["sbatch__with_dependency"]          = _call(m.sbatch,
        script="#!/bin/bash\n#SBATCH --job-name=dep_test\necho dep",
        flags=f"--dependency=afterok:{running}")

    # ── srun ──────────────────────────────────────────────────────────────────
    _reset(scenario)
    out["srun__hostname"]                   = _call(m.srun, command="hostname")
    out["srun__interactive_gpu"]            = _call(m.srun, flags="--pty --partition=gpu --gres=gpu:1",
                                                     command="/bin/bash")

    # ── salloc ────────────────────────────────────────────────────────────────
    _reset(scenario)
    out["salloc__cpu_1node"]                = _call(m.salloc, flags="--nodes=1 --cpus-per-task=4")
    out["salloc__gpu"]                      = _call(m.salloc,
                                                     flags="--nodes=1 --partition=gpu --gres=gpu:1")

    # ── sattach ───────────────────────────────────────────────────────────────
    _reset(scenario)
    out["sattach__running"]                 = _call(m.sattach, job_step=f"{running}.0")

    # ── sbcast ────────────────────────────────────────────────────────────────
    _reset(scenario)
    out["sbcast__file"]                     = _call(m.sbcast, src_file="/tmp/test.sh",
                                                     dest_path="/tmp/node_file.sh", job_id=running)

    # ── scontrol_node ─────────────────────────────────────────────────────────
    _reset(scenario)
    out["scontrol_node__drain"]             = _call(m.scontrol_node, node=first_node,
                                                     state="DRAIN", reason="maintenance")
    _reset(scenario)
    out["scontrol_node__down"]              = _call(m.scontrol_node, node=first_node,
                                                     state="DOWN", reason="hardware_failure")
    _reset(scenario)
    out["scontrol_node__resume"]            = _call(m.scontrol_node, node=first_node, state="RESUME")

    # ── scontrol_node_power_down / power_up ───────────────────────────────────
    _reset(scenario)
    out["scontrol_node_power_down"]         = _call(m.scontrol_node_power_down, node=first_node)
    out["scontrol_node_power_up"]           = _call(m.scontrol_node_power_up, node=first_node)

    # ── scontrol_node_features / gres / weight ────────────────────────────────
    _reset(scenario)
    out["scontrol_node_features"]           = _call(m.scontrol_node_features,
                                                     node=first_node, features="rack1,highmem")
    out["scontrol_node_gres"]               = _call(m.scontrol_node_gres,
                                                     node=gpu_node, gres="gpu:a100:4")
    out["scontrol_node_weight"]             = _call(m.scontrol_node_weight,
                                                     node=first_node, weight=100)

    # ── scontrol_create_reservation / update / delete ─────────────────────────
    _reset(scenario)
    out["scontrol_create_reservation"]      = _call(m.scontrol_create_reservation,
        params=(
            "ReservationName=test_lookup "
            "StartTime=2026-05-14T20:00:00 EndTime=2026-05-14T22:00:00 "
            "Nodes=cpu-node-01 Flags=MAINT Users=root"
        ))
    # update the reservation we just created
    out["scontrol_update_reservation"]      = _call(m.scontrol_update_reservation,
        reservation="test_lookup", params="EndTime=2026-05-14T23:00:00")
    _reset(scenario)
    out["scontrol_delete_reservation"]      = _call(m.scontrol_delete_reservation,
                                                     reservation="maintenance")

    # ── scontrol_write_config ─────────────────────────────────────────────────
    _reset(scenario)
    out["scontrol_write_config"]            = _call(m.scontrol_write_config)

    # ── scontrol_setdebug ─────────────────────────────────────────────────────
    _reset(scenario)
    out["scontrol_setdebug__debug3"]        = _call(m.scontrol_setdebug, level="debug3")
    _reset(scenario)
    out["scontrol_setdebug__info"]          = _call(m.scontrol_setdebug, level="info")
    _reset(scenario)
    out["scontrol_setdebug__verbose"]       = _call(m.scontrol_setdebug, level="verbose")

    # ── scontrol_token ────────────────────────────────────────────────────────
    _reset(scenario)
    out["scontrol_token__default"]          = _call(m.scontrol_token)
    out["scontrol_token__1day"]             = _call(m.scontrol_token, lifespan="86400")

    # ── scontrol_shutdown ─────────────────────────────────────────────────────
    _reset(scenario)
    out["scontrol_shutdown"]                = _call(m.scontrol_shutdown)
    out["scontrol_shutdown__graceful"]      = _call(m.scontrol_shutdown, mode="graceful")

    # ── sacctmgr_add ──────────────────────────────────────────────────────────
    _reset(scenario)
    out["sacctmgr_add__user"]               = _call(m.sacctmgr_add, entity="user",
                                                     params="name=testuser DefaultAccount=general")
    out["sacctmgr_add__account"]            = _call(m.sacctmgr_add, entity="account",
                                                     params="name=testacct Cluster=mock-cluster")
    out["sacctmgr_add__qos"]                = _call(m.sacctmgr_add, entity="qos",
                                                     params="name=testqos MaxJobs=20")

    # ── sacctmgr_modify ───────────────────────────────────────────────────────
    _reset(scenario)
    out["sacctmgr_modify__user_grpcpumins"] = _call(m.sacctmgr_modify, entity="user",
                                                     where="name=charlie", params="GrpCPUMins=-1")
    out["sacctmgr_modify__qos_maxjobs"]     = _call(m.sacctmgr_modify, entity="qos",
                                                     where="name=normal", params="MaxJobsPerUser=10")
    out["sacctmgr_modify__account_maxcpus"] = _call(m.sacctmgr_modify, entity="account",
                                                     where="name=general", params="MaxCPUs=256")

    # ── sacctmgr_delete ───────────────────────────────────────────────────────
    _reset(scenario)
    out["sacctmgr_delete__user"]            = _call(m.sacctmgr_delete, entity="user",
                                                     params="name=testuser")
    out["sacctmgr_delete__account"]         = _call(m.sacctmgr_delete, entity="account",
                                                     params="name=testacct")

    # ── sacctmgr_recalc ───────────────────────────────────────────────────────
    _reset(scenario)
    out["sacctmgr_recalc"]                  = _call(m.sacctmgr_recalc)

    # ── sacctmgr_archive / dump / load ────────────────────────────────────────
    _reset(scenario)
    out["sacctmgr_archive"]                 = _call(m.sacctmgr_archive)
    out["sacctmgr_dump"]                    = _call(m.sacctmgr_dump)
    out["sacctmgr_load"]                    = _call(m.sacctmgr_load,
                                                     file_path="/tmp/sacctmgr_dump.mock")

    # ── strigger_set ──────────────────────────────────────────────────────────
    _reset(scenario)
    out["strigger_set__node_down"]          = _call(m.strigger_set,
                                                     spec="--node --down --program=/tmp/alert.sh")
    out["strigger_set__job_fail"]           = _call(m.strigger_set,
                                                     spec="--job --fail --program=/tmp/fail_alert.sh")

    # ── strigger_clear ────────────────────────────────────────────────────────
    # set a trigger first so there is something to clear
    _reset(scenario)
    m.strigger_set(spec="--node --down --program=/tmp/t.sh")
    triggers = m._STATE.list_triggers()
    tid = str(triggers[0]["id"]) if triggers else ""
    out["strigger_clear__all"]              = _call(m.strigger_clear)   # clears everything
    _reset(scenario)
    m.strigger_set(spec="--node --down --program=/tmp/t.sh")
    triggers = m._STATE.list_triggers()
    tid = str(triggers[0]["id"]) if triggers else ""
    out["strigger_clear__specific"]         = _call(m.strigger_clear, trigger_id=tid)

    return out


# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    result: dict[str, dict[str, str]] = {}
    for scenario in SCENARIOS:
        print(f"  {scenario:<15}", end=" ", flush=True)
        result[scenario] = _collect(scenario)
        print(f"{len(result[scenario])} variants")

    n_tools = len(result[SCENARIOS[0]])
    print(f"\nShape: {len(result)} scenarios × {n_tools} variants = "
          f"{len(result) * n_tools} total entries")

    out_path = Path(__file__).parent / "mock_tool_outputs_5x64.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    print(f"Written → {out_path}")
    print("\nTool variants per tool:")
    keys = list(result[SCENARIOS[0]].keys())
    from collections import Counter
    tool_counts = Counter(k.split("__")[0] for k in keys)
    for tool, cnt in sorted(tool_counts.items()):
        print(f"  {tool:<40} {cnt}")


if __name__ == "__main__":
    main()
