#!/usr/bin/env python3
"""
Evaluation Web Server
======================
Serves the evaluation UI and runs tests against the live agent,
streaming real-time progress to the browser via SSE.

Usage:
  cd evaluation/
  python eval_server.py                     # default: port 8080
  python eval_server.py --port 9000         # custom port
  python eval_server.py --judge             # enable LLM judge
"""

import asyncio
import hashlib
import json
import logging
import shlex
import time
import argparse
import uuid
import os
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from fastapi import FastAPI, UploadFile, File, Query, Body
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from scenario_eval import (
    load_dataset, filter_dataset, run_agent, score_test, judge_flow,
    compute_metrics, compute_pass_k, save_results,
    AgentTrace, TestResult,
    AGENT_URL, JUDGE_MODEL, PASS_THRESHOLD, WEIGHTS, WEIGHTS_WITH_JUDGE,
    DATASET_PATH, RESULTS_DIR,
    _judge_uses_openai,
)

# ── State ─────────────────────────────────────────────────────────────────────

class EvalState:
    dataset: list = []
    dataset_id: str = ""    # hash of test IDs — changes only when dataset content changes
    results: dict = {}       # test_id → TestResult dict
    running: bool = False
    current_test: str = ""
    progress: int = 0
    total: int = 0
    metrics: dict = {}
    agent_url: str = AGENT_URL
    use_judge: bool = False
    judge_model: str = JUDGE_MODEL
    auto_approve: bool = True
    mcp_url: str = os.getenv("MCP_SERVER_URL", "http://localhost:3002")
    run_task: Optional[asyncio.Task] = None
    run_id: str = ""
    event_seq: int = 0
    event_log: list = []   # append-only in-memory SSE history for re-attach
    judge_running: bool = False
    judge_progress: int = 0
    judge_total: int = 0
    terminal_histories: dict = {}  # test_id -> terminal transcript entries
    terminal_snapshots: dict = {}  # test_id -> latest mock-state snapshot
    terminal_seq: int = 0

state = EvalState()
# Serialize access to mutable mock-Slurm state between eval runs and admin terminal.
_mcp_state_lock = asyncio.Lock()


def _normalize_judge_model(requested_model: str) -> str:
    """Ensure judge model/provider combination is executable in current env."""
    model = (requested_model or "").strip() or JUDGE_MODEL
    if _judge_uses_openai(model):
        openai_key = (os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_AI_KEY") or "").strip()
        if not openai_key and not _judge_uses_openai(JUDGE_MODEL):
            logger.warning(
                "Requested OpenAI judge model '%s' but no OPENAI_API_KEY found; falling back to '%s'.",
                model,
                JUDGE_MODEL,
            )
            return JUDGE_MODEL
    return model


def _heal_run_state() -> None:
    """Clear stale running flags when background task is no longer active."""
    if state.running and (state.run_task is None or state.run_task.done()):
        state.running = False
        state.current_test = ""
        state.run_task = None
        state.judge_running = False


@asynccontextmanager
async def _mcp_session(mcp_url: str):
    """Create one initialized MCP client session."""
    from mcp import ClientSession as MCPClientSession
    from mcp.client.sse import sse_client

    async with sse_client(f"{mcp_url.rstrip('/')}/sse") as (read, write):
        async with MCPClientSession(read, write) as session:
            await session.initialize()
            yield session


def _mcp_content_to_text(result: Any) -> str:
    """Convert MCP call_tool result payload into plain text."""
    content = getattr(result, "content", None)
    if content is None:
        return str(result)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            txt = None
            if isinstance(item, dict):
                txt = item.get("text") or item.get("content")
            else:
                txt = getattr(item, "text", None) or getattr(item, "content", None)
            if isinstance(txt, str) and txt:
                parts.append(txt)
        if parts:
            return "\n".join(parts)
    return str(content)


async def _call_mcp_tool(
    mcp_url: str,
    tool_name: str,
    args: dict,
    session: Any = None,
) -> str:
    """Call one MCP tool and return textual output."""
    if session is not None:
        result = await session.call_tool(tool_name, args or {})
        return _mcp_content_to_text(result)

    async with _mcp_session(mcp_url) as mcp:
        result = await mcp.call_tool(tool_name, args or {})
        return _mcp_content_to_text(result)


async def _reset_state_for_test(
    mcp_url: str,
    test: dict,
    session: Any = None,
    source_state_override: Optional[dict] = None,
) -> tuple[bool, str]:
    """Reset stateful mock MCP to this test's source_state baseline."""
    scenario = str(test.get("scenario", "") or "")
    source_state = source_state_override if source_state_override is not None else (test.get("source_state") or {})
    try:
        out = await _call_mcp_tool(
            mcp_url,
            "reset_mock_state",
            {
                "scenario": scenario,
                "source_state_json": json.dumps(source_state),
            },
            session=session,
        )
        text = str(out or "")
        low = text.lower()
        if low.startswith("reset_mock_state:"):
            return False, text[:400]
        return True, text[:400]
    except Exception as e:
        return False, f"mcp-sdk reset failed: {e}"


async def _get_terminal_state_snapshot(mcp_url: str, session: Any = None) -> Optional[dict]:
    """Capture current mock-state snapshot from MCP server."""
    try:
        raw = await _call_mcp_tool(mcp_url, "get_mock_state_snapshot", {}, session=session)
        payload = json.loads(raw)
        if isinstance(payload, dict):
            return payload
    except Exception:
        return None
    return None


async def _restore_terminal_state_snapshot(
    mcp_url: str,
    test: dict,
    snapshot: dict,
    session: Any = None,
) -> tuple[bool, str]:
    """Restore terminal state from a previously captured snapshot."""
    source_state = snapshot.get("source_state") if isinstance(snapshot, dict) else None
    if not isinstance(source_state, dict):
        source_state = snapshot if isinstance(snapshot, dict) else {}
    if not isinstance(source_state, dict):
        return False, "invalid snapshot payload"
    restored_test = {
        "scenario": str(snapshot.get("scenario") or test.get("scenario") or ""),
        "source_state": source_state,
    }
    return await _reset_state_for_test(
        mcp_url,
        restored_test,
        session=session,
        source_state_override=source_state,
    )


def _split_long_opts(tokens: List[str], short_map: Optional[Dict[str, str]] = None) -> Tuple[List[str], Dict[str, str]]:
    """Parse --key value / --key=value and mapped short flags (-u alice)."""
    positional: List[str] = []
    opts: Dict[str, str] = {}
    short_map = short_map or {}
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith("--") and len(tok) > 2:
            raw = tok[2:]
            if "=" in raw:
                k, v = raw.split("=", 1)
            else:
                k = raw
                if i + 1 < len(tokens) and not tokens[i + 1].startswith("--"):
                    v = tokens[i + 1]
                    i += 1
                else:
                    v = "true"
            opts[k.replace("-", "_").lower()] = v
        elif tok.startswith("-") and not tok.startswith("--") and len(tok) == 2:
            mapped = short_map.get(tok[1], "")
            if not mapped:
                positional.append(tok)
                i += 1
                continue
            if i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
                v = tokens[i + 1]
                i += 1
            else:
                v = "true"
            opts[mapped.replace("-", "_").lower()] = v
        else:
            positional.append(tok)
        i += 1
    return positional, opts


def _opt(opts: Dict[str, str], *keys: str, default: str = "") -> str:
    """Fetch first matching normalized option key."""
    for key in keys:
        k = key.replace("-", "_").lower()
        if k in opts:
            return opts[k]
    return default


_KNOWN_JOB_STATES = {
    "running", "pending", "failed", "completed", "cancelled", "timeout",
    "suspended", "held", "completing", "configuring",
}


def _clean_opt_value(value: str) -> str:
    """Normalize CLI option values (accept leading '-'/'--' forms)."""
    return str(value or "").strip().lstrip("-")


def _parse_squeue_args(rest: List[str]) -> Dict[str, str]:
    """Robust squeue CLI parser supporting common short/long flag forms."""
    args = {"user": "", "state": "", "partition": "", "job_id": ""}
    positional: List[str] = []
    i = 0
    while i < len(rest):
        tok = rest[i]
        low = tok.lower()

        # --key=value forms
        if low.startswith("--user="):
            args["user"] = _clean_opt_value(tok.split("=", 1)[1])
            i += 1
            continue
        if low.startswith("--state=") or low.startswith("--states="):
            args["state"] = _clean_opt_value(tok.split("=", 1)[1]).upper()
            i += 1
            continue
        if low.startswith("--partition="):
            args["partition"] = _clean_opt_value(tok.split("=", 1)[1])
            i += 1
            continue
        if any(low.startswith(prefix) for prefix in ("--job=", "--jobs=", "--job_id=", "--jobid=")):
            args["job_id"] = _clean_opt_value(tok.split("=", 1)[1])
            i += 1
            continue

        # --key value / -k value forms
        if low in {"-u", "--user"}:
            if i + 1 >= len(rest):
                raise ValueError("squeue: --user requires a value")
            args["user"] = _clean_opt_value(rest[i + 1])
            i += 2
            continue
        if low in {"-t", "--state", "--states"}:
            if i + 1 >= len(rest):
                raise ValueError("squeue: --state requires a value")
            args["state"] = _clean_opt_value(rest[i + 1]).upper()
            i += 2
            continue
        if low in {"-p", "--partition"}:
            if i + 1 >= len(rest):
                raise ValueError("squeue: --partition requires a value")
            args["partition"] = _clean_opt_value(rest[i + 1])
            i += 2
            continue
        if low in {"-j", "--job", "--jobs", "--job_id", "--jobid"}:
            if i + 1 >= len(rest):
                raise ValueError("squeue: --job requires a value")
            args["job_id"] = _clean_opt_value(rest[i + 1])
            i += 2
            continue

        # Accept `squeue --RUNNING` / `squeue --PENDING` as state shorthand.
        if low.startswith("--") and low[2:] in _KNOWN_JOB_STATES:
            args["state"] = low[2:].upper()
            i += 1
            continue

        # Reject unknown options explicitly.
        if low.startswith("-"):
            raise ValueError(f"squeue: unsupported option '{tok}'")

        positional.append(tok)
        i += 1

    # Optional positional shorthand: `squeue 1001`
    if positional:
        if len(positional) == 1:
            args["job_id"] = positional[0]
        else:
            raise ValueError("squeue: unexpected positional args")

    return args


def _dispatch_terminal_command(command: str) -> Tuple[str, Dict[str, str]]:
    """Map terminal CLI text to an MCP tool call."""
    try:
        tokens = shlex.split(command)
    except ValueError as exc:
        raise ValueError(f"shell parse error: {exc}") from exc
    if not tokens:
        raise ValueError("empty command")

    cmd = tokens[0].lower()
    rest = tokens[1:]

    if cmd == "squeue":
        return "squeue", _parse_squeue_args(rest)

    if cmd == "sinfo":
        pos, opts = _split_long_opts(rest, short_map={"p": "partition", "n": "node", "N": "node"})
        if pos:
            raise ValueError("sinfo: unexpected positional args")
        return "sinfo", {
            "partition": _opt(opts, "partition"),
            "node": _opt(opts, "node", "nodes"),
        }

    if cmd == "sacct":
        pos, opts = _split_long_opts(
            rest,
            short_map={"u": "user", "s": "state", "S": "starttime", "E": "endtime", "o": "format"},
        )
        if pos:
            raise ValueError("sacct: unexpected positional args")
        return "sacct", {
            "user": _opt(opts, "user"),
            "state": _opt(opts, "state"),
            "starttime": _opt(opts, "starttime", "start_time"),
            "endtime": _opt(opts, "endtime", "end_time"),
            "format": _opt(opts, "format", default="JobID,JobName,User,State,ExitCode,Elapsed,NCPUs,ReqMem"),
        }

    if cmd == "scontrol":
        if not rest:
            raise ValueError("Usage: scontrol show|hold|release|update|requeue|reconfigure ...")
        sub = rest[0].lower()
        args = rest[1:]

        if sub == "show":
            entity = "job"
            sid = ""
            if args:
                if "=" in args[0]:
                    entity, sid = args[0].split("=", 1)
                else:
                    entity = args[0]
                    sid = args[1] if len(args) > 1 else ""
            return "scontrol_show", {"entity": entity, "id": sid}

        if sub == "hold":
            if not args:
                raise ValueError("Usage: scontrol hold <job_id>")
            return "scontrol_hold", {"job_id": args[0]}

        if sub == "release":
            if not args:
                raise ValueError("Usage: scontrol release <job_id>")
            return "scontrol_release", {"job_id": args[0]}

        if sub == "requeue":
            if not args:
                raise ValueError("Usage: scontrol requeue <job_id>")
            return "scontrol_requeue", {"job_id": args[0]}

        if sub == "reconfigure":
            if args:
                raise ValueError("Usage: scontrol reconfigure")
            return "scontrol_reconfigure", {}

        if sub == "update":
            if not args:
                raise ValueError("Usage: scontrol update <entity>=<id> <key=value ...>")
            entity = ""
            sid = ""
            params_tokens: List[str] = []
            first = args[0]
            if "=" in first:
                k, v = first.split("=", 1)
                if k.lower() in {"job", "node", "partition"} and v:
                    entity = k.lower()
                    sid = v
                    params_tokens = args[1:]
            if not entity:
                if len(args) < 3:
                    raise ValueError("Usage: scontrol update <entity> <id> <key=value ...>")
                entity = args[0].lower()
                sid = args[1]
                params_tokens = args[2:]
            if entity not in {"job", "node", "partition"}:
                raise ValueError(f"scontrol update: unsupported entity '{entity}'")
            if not params_tokens:
                raise ValueError("scontrol update: missing params")
            return "scontrol_update", {"entity": entity, "id": sid, "params": " ".join(params_tokens)}

        raise ValueError(f"scontrol: unsupported subcommand '{sub}'")

    if cmd == "sbatch":
        if not rest:
            raise ValueError("Usage: sbatch <script> [flags...]")
        return "sbatch", {"script": rest[0], "flags": " ".join(rest[1:])}

    if cmd == "scancel":
        pos, opts = _split_long_opts(rest, short_map={"u": "user"})
        if not pos:
            raise ValueError("Usage: scancel <job_id[,job_id...]> [--user <user>]")
        return "scancel", {
            "job_id": ",".join(pos),
            "user": _opt(opts, "user"),
        }

    if cmd == "sacctmgr":
        if not rest:
            raise ValueError("Usage: sacctmgr show|list|add|modify|delete ...")
        sub = rest[0].lower()
        if sub in {"show", "list"}:
            entity = rest[1] if len(rest) > 1 else "user"
            params = " ".join(rest[2:]) if len(rest) > 2 else ""
            return "sacctmgr_list", {"entity": entity, "params": params}
        if sub == "add":
            if len(rest) < 2:
                raise ValueError("Usage: sacctmgr add <entity> <params>")
            return "sacctmgr_add", {"entity": rest[1], "params": " ".join(rest[2:])}
        if sub == "modify":
            if len(rest) < 5:
                raise ValueError("Usage: sacctmgr modify <entity> where <...> set <...>")
            entity = rest[1]
            tail = rest[2:]
            lower = [t.lower() for t in tail]
            if "where" not in lower or "set" not in lower:
                raise ValueError("sacctmgr modify: expected 'where ... set ...'")
            wi = lower.index("where")
            si = lower.index("set")
            if si <= wi + 1:
                raise ValueError("sacctmgr modify: missing where clause")
            where = " ".join(tail[wi + 1:si]).strip()
            params = " ".join(tail[si + 1:]).strip()
            if not params:
                raise ValueError("sacctmgr modify: missing set params")
            return "sacctmgr_modify", {"entity": entity, "where": where, "params": params}
        if sub == "delete":
            if len(rest) < 2:
                raise ValueError("Usage: sacctmgr delete <entity> <params>")
            return "sacctmgr_delete", {"entity": rest[1], "params": " ".join(rest[2:])}
        raise ValueError(f"sacctmgr: unsupported subcommand '{sub}'")

    if cmd == "sdiag":
        if rest:
            raise ValueError("Usage: sdiag")
        return "sdiag", {}

    if cmd == "sprio":
        pos, opts = _split_long_opts(rest, short_map={"u": "user", "p": "partition"})
        if pos:
            raise ValueError("sprio: unexpected positional args")
        return "sprio", {"user": _opt(opts, "user"), "partition": _opt(opts, "partition")}

    if cmd == "sstat":
        if not rest:
            raise ValueError("Usage: sstat <job_id>")
        return "sstat", {"job_id": rest[0]}

    if cmd == "cluster_history":
        if rest:
            raise ValueError("Usage: cluster_history")
        return "cluster_history", {}

    if cmd == "reset_mock_state":
        raise ValueError(
            "reset_mock_state is not allowed in the admin terminal. "
            "Terminal isolation is managed automatically per test."
        )

    if cmd == "read_file":
        if not rest:
            raise ValueError("Usage: read_file <path>")
        return "read_file", {"file_path": rest[0]}

    if cmd == "web_search":
        pos, opts = _split_long_opts(rest)
        query = " ".join(pos).strip()
        if not query:
            raise ValueError("Usage: web_search <query> [--search_type general|slurm|error]")
        return "web_search", {"query": query, "search_type": _opt(opts, "search_type", default="general")}

    if cmd == "fetch_web_content":
        pos, opts = _split_long_opts(rest)
        if not pos:
            raise ValueError("Usage: fetch_web_content <url> [--max_chars N]")
        max_chars_raw = _opt(opts, "max_chars", default="4000")
        try:
            max_chars = int(max_chars_raw)
        except Exception:
            max_chars = 4000
        return "fetch_web_content", {"url": pos[0], "max_chars": str(max_chars)}

    supported = (
        "squeue, sinfo, sacct, scontrol, sbatch, scancel, sacctmgr, "
        "sdiag, sprio, sstat, cluster_history, read_file, web_search, fetch_web_content"
    )
    raise ValueError(f"Unsupported command '{cmd}'. Supported: {supported}")


def _terminal_key(test_id: str) -> str:
    return (test_id or "").strip() or "__global__"


def _terminal_history(test_id: str) -> List[dict]:
    return list(state.terminal_histories.get(_terminal_key(test_id), []))


def _append_terminal_entry(
    test_id: str,
    command: str,
    output: str,
    ok: bool,
    tool_name: str,
    tool_args: Dict[str, str],
    state_snapshot: Optional[dict] = None,
) -> dict:
    key = _terminal_key(test_id)
    state.terminal_seq += 1
    text = str(output or "")
    if len(text) > 60000:
        text = text[:60000] + f"\n...[truncated {len(text) - 60000} chars]"
    entry = {
        "id": state.terminal_seq,
        "test_id": key if key != "__global__" else "",
        "ts": time.time(),
        "prompt": "slurm@hpc:~$ ",
        "command": command,
        "output": text,
        "ok": bool(ok),
        "_tool": tool_name,
        "_args": tool_args,
    }
    if isinstance(state_snapshot, dict):
        entry["_state_snapshot"] = state_snapshot
    hist = state.terminal_histories.setdefault(key, [])
    hist.append(entry)
    if len(hist) > 500:
        state.terminal_histories[key] = hist[-300:]
        hist = state.terminal_histories[key]
    return hist[-1]


async def _prepare_terminal_state_for_test(test_id: str, session: Any = None) -> tuple[bool, str]:
    """Restore terminal state from snapshot; fallback to deterministic baseline reset."""
    key = _terminal_key(test_id)
    if key == "__global__":
        return True, ""

    test = next((t for t in state.dataset if t.get("id") == key), None)
    if not test:
        return False, f"Unknown test_id '{key}'. Select a valid test first."

    hist = state.terminal_histories.get(key, [])
    snapshot = state.terminal_snapshots.get(key)
    if not isinstance(snapshot, dict) and hist:
        legacy_snapshot = hist[-1].get("_state_snapshot")
        if isinstance(legacy_snapshot, dict):
            snapshot = legacy_snapshot

    setup_note = ""
    if isinstance(snapshot, dict):
        ok, msg = await _restore_terminal_state_snapshot(state.mcp_url, test, snapshot, session=session)
        if ok:
            state.terminal_snapshots[key] = snapshot
            return True, ""
        state.terminal_snapshots.pop(key, None)
        setup_note = f"snapshot restore failed ({msg}). Reset to test baseline."
    elif hist:
        setup_note = "legacy terminal history has no snapshot. Reset to test baseline."

    ok, msg = await _reset_state_for_test(state.mcp_url, test, session=session)
    if not ok:
        return False, msg

    baseline_snapshot = await _get_terminal_state_snapshot(state.mcp_url, session=session)
    if isinstance(baseline_snapshot, dict):
        state.terminal_snapshots[key] = baseline_snapshot
    return True, setup_note


def _push_event(event: str, data: Dict[str, Any], run_id: Optional[str] = None) -> None:
    """Store run events so clients can re-attach after disconnect.
    Keeps only a bounded tail to avoid unbounded memory growth.
    """
    state.event_seq += 1
    state.event_log.append({
        "seq": state.event_seq,
        "event": event,
        "data": data,
        "run_id": run_id or state.run_id,
        "ts": time.time(),
    })
    # Keep a rolling tail
    if len(state.event_log) > 5000:
        state.event_log = state.event_log[-3000:]


def _sse_line(ev: dict) -> str:
    return f"event: {ev['event']}\ndata: {json.dumps(ev['data'])}\n\n"


async def _run_judge_background(
    queue: "asyncio.Queue[Optional[tuple[dict, AgentTrace, int]]]",
    run_id: str,
    total_to_judge: int,
) -> None:
    """Judge completed traces independently from agent execution."""
    state.judge_running = total_to_judge > 0
    state.judge_total = total_to_judge
    state.judge_progress = 0
    _push_event("judge_start", {
        "run_id": run_id,
        "total": total_to_judge,
        "done": 0,
    }, run_id)

    judged = 0
    while True:
        item = await queue.get()
        if item is None:
            break
        test, trace, scope_pos = item
        test_id = test["id"]
        _push_event("judge_test_start", {
            "run_id": run_id,
            "id": test_id,
            # Stable index within filtered scope (independent of resume gaps)
            "index": scope_pos,
            "done": judged,
            "total": total_to_judge,
        }, run_id)

        try:
            judged_result = await score_test(
                test,
                trace,
                use_judge=True,
                judge_model=state.judge_model,
            )
            rd = asdict(judged_result)
        except Exception as exc:
            # Keep structural result, mark judge failure explicitly.
            fallback = await score_test(
                test,
                trace,
                use_judge=False,
                judge_model=state.judge_model,
            )
            rd = asdict(fallback)
            rd["judge_score"] = 0.0
            rd["judge_reason"] = f"judge error: {exc}"
            rd["judge_ran"] = True

        rd["judge_pending"] = False
        state.results[test_id] = rd
        judged += 1
        state.judge_progress = judged
        _persist_state()
        _push_event("judge_done", {
            "run_id": run_id,
            "id": test_id,
            "index": scope_pos,
            "done": judged,
            "total": total_to_judge,
            "result": rd,
        }, run_id)

    state.judge_running = False
    state.judge_progress = judged
    if judged != state.judge_total:
        state.judge_total = judged
    _persist_state()
    _push_event("judge_complete", {
        "run_id": run_id,
        "done": judged,
        "total": state.judge_total,
    }, run_id)


async def _run_eval_background(
    ds_to_run: list,
    scope_ds: list,
    pending_judge_items: list,
    agent_url: str,
    mcp_url: str,
    auto_approve: bool,
    use_judge: bool,
    run_id: str,
    scenario_label: str,
) -> None:
    """Execute evaluation independently from client connection lifecycle."""
    pending_judge_items = pending_judge_items or []
    scope_index = {t["id"]: i for i, t in enumerate(scope_ds)}
    judge_total = len(ds_to_run) + len(pending_judge_items) if use_judge else 0
    state.running = True
    state.total = len(scope_ds)
    state.progress = max(0, len(scope_ds) - len(ds_to_run))
    state.judge_running = False
    state.judge_progress = 0
    state.judge_total = judge_total
    already_done = state.progress
    state.current_test = ""
    _push_event(
        "start",
        {
            "total": len(scope_ds),
            "remaining": len(ds_to_run),
            "already_done": already_done,
            "judge": use_judge,
            "judge_total": judge_total,
            "judge_resume_pending": len(pending_judge_items),
            "run_id": run_id,
        },
        run_id,
    )

    judge_queue: Optional[asyncio.Queue] = None
    judge_task: Optional[asyncio.Task] = None
    if use_judge and judge_total:
        judge_queue = asyncio.Queue()
        judge_task = asyncio.create_task(
            _run_judge_background(judge_queue, run_id, judge_total)
        )
        for test, trace, scope_pos in pending_judge_items:
            await judge_queue.put((test, trace, scope_pos))

    try:
        for i, test in enumerate(ds_to_run):
            # Stable absolute position in filtered scope (for UI row mapping/logging).
            scope_pos = scope_index.get(test["id"], i)
            # Monotonic resume-progress counter (for progress bar semantics).
            completed_before = already_done + i
            state.current_test = test["id"]
            state.progress = completed_before

            ok = False
            msg = ""
            run_error: Optional[str] = None
            trace: Optional[AgentTrace] = None
            session_id = f"eval_{test['id']}_{int(time.time())}"

            # Lock around reset + agent execution to prevent terminal/eval
            # interleaving from corrupting shared mock state.
            async with _mcp_state_lock:
                # Deterministic baseline: restore test source_state before each case.
                ok, msg = await _reset_state_for_test(mcp_url, test)
                _push_event("state_reset", {
                    "index": scope_pos,
                    "completed": completed_before,
                    "id": test["id"],
                    "ok": ok,
                    "details": msg[:600],
                    "run_id": run_id,
                }, run_id)

                if ok:
                    _push_event("test_start", {
                        "index": scope_pos,
                        "completed": completed_before,
                        "id": test["id"],
                        "category": test["category"],
                        "scenario": test["scenario"],
                        "input": test["input"],
                        "run_id": run_id,
                    }, run_id)
                    try:
                        trace = await run_agent(
                            test["input"], session_id, agent_url, auto_approve,
                        )
                    except Exception as e:
                        run_error = str(e)

            if not ok:
                gt = test.get("ground_truth", {})
                reset_err = f"state reset failed: {msg}"
                failed = TestResult(
                    test_id=test["id"],
                    scenario=test.get("scenario", ""),
                    category=test.get("category", ""),
                    prompt=test.get("input", ""),
                    gt_tools=gt.get("tools", []),
                    gt_handoff=bool(gt.get("handoff", False)),
                    gt_hitl=bool(gt.get("hitl", False)),
                    gt_keywords=gt.get("keywords", []),
                    agent_tools=[],
                    agent_handoff=False,
                    agent_hitl=False,
                    agent_response="",
                    agent_thinking="",
                    tool_recall=0.0,
                    routing_match=0.0,
                    hitl_match=0.0,
                    keyword_score=0.0,
                    state_match=0.0,
                    judge_score=0.0,
                    judge_reason=reset_err,
                    judge_ran=bool(use_judge),
                    overall=0.0,
                    passed=False,
                    latency_s=0.0,
                    is_variant=bool(test.get("variant_of")),
                    error=reset_err,
                    tool_call_history=[],
                )
                rd = asdict(failed)
                rd["judge_pending"] = False
                state.results[test["id"]] = rd
                _persist_state()
                _push_event("test_done", {
                    "index": scope_pos,
                    "completed": completed_before + 1,
                    "id": test["id"],
                    "result": rd,
                    "run_id": run_id,
                }, run_id)
                continue

            if trace is None:
                trace = AgentTrace([], False, False, "", 0.0, run_error or "agent execution failed")
            result = await score_test(test, trace, use_judge=False)

            rd = asdict(result)
            if use_judge:
                rd["judge_pending"] = True
                rd["judge_ran"] = False
                rd["judge_score"] = 0.0
                rd["judge_reason"] = "LLM judge pending"
                rd["_pending_trace"] = asdict(trace)
            else:
                rd["judge_pending"] = False
            state.results[test["id"]] = rd
            _persist_state()   # write after every test so a mid-run crash loses nothing

            _push_event("test_done", {
                "index": scope_pos,
                "completed": completed_before + 1,
                "id": test["id"],
                "result": rd,
                "run_id": run_id,
            }, run_id)

            if use_judge and judge_queue is not None:
                await judge_queue.put((test, trace, scope_pos))

            await asyncio.sleep(0.5)

        # Finish independent judging queue before final aggregate.
        if judge_queue is not None and judge_task is not None:
            await judge_queue.put(None)
            await judge_task

        # Compute final metrics over the full selected scope, including any
        # already-completed tests from a resumed run.
        scoped_results = []
        for test in scope_ds:
            rd = state.results.get(test["id"])
            if not rd:
                continue
            parsed = _to_test_result(rd, test["id"])
            if parsed is not None:
                scoped_results.append(parsed)

        metrics = compute_metrics(scoped_results)
        state.metrics = metrics

        # Save to disk (timestamped copy + rolling snapshot)
        if scoped_results:
            save_results(scoped_results, metrics, scenario_label)
        _persist_state()
        state.progress = len(scope_ds)

        _push_event("complete", {
            "metrics": metrics,
            "count": len(scoped_results),
            "judge_total": state.judge_total,
            "judge_done": state.judge_progress,
            "run_id": run_id,
        }, run_id)

    except asyncio.CancelledError:
        if judge_task and not judge_task.done():
            judge_task.cancel()
            try:
                await judge_task
            except Exception:
                pass
        _push_event("stopped", {"run_id": run_id, "reason": "cancelled"}, run_id)
        raise
    except Exception as e:
        _push_event("error", {"run_id": run_id, "error": str(e)}, run_id)
    finally:
        if judge_task and not judge_task.done():
            judge_task.cancel()
            try:
                await judge_task
            except Exception:
                pass
        state.running = False
        state.current_test = ""
        state.run_task = None
        state.judge_running = False


async def _stream_events(run_id: str, from_seq: int) -> Any:
    """SSE stream that tails the in-memory event log for a specific run."""
    cursor = from_seq

    while True:
        # Emit all unseen events for this run
        emitted = False
        for ev in state.event_log:
            if ev["seq"] <= cursor:
                continue
            if ev.get("run_id") != run_id:
                continue
            cursor = ev["seq"]
            emitted = True
            yield _sse_line(ev)

        if not emitted:
            # If this run is no longer active and there is nothing new, close stream.
            if not state.running and state.run_id == run_id:
                break
            # If another run is active, this old run will not get new events.
            if state.run_id and state.run_id != run_id:
                break
            await asyncio.sleep(0.2)


def _dataset_fingerprint(ds: list) -> str:
    """Stable hash of dataset test IDs — changes only if tests added/removed."""
    ids = ",".join(sorted(t["id"] for t in ds))
    return hashlib.md5(ids.encode()).hexdigest()[:12]


def _restore_latest() -> None:
    """On startup, load dataset + results from the most recent saved JSON."""
    try:
        jsons = sorted(RESULTS_DIR.glob("eval_*.json"))
        if not jsons:
            return
        latest = jsons[-1]
        data = json.loads(latest.read_text())
        raw_results = data.get("results", [])
        raw_terminal = data.get("terminal_histories", {})
        raw_snapshots = data.get("terminal_snapshots", {})
        if not raw_results and not raw_terminal and not raw_snapshots:
            return

        # Rebuild the results dict
        for r in raw_results:
            state.results[r["test_id"]] = r
        state.terminal_histories = raw_terminal if isinstance(raw_terminal, dict) else {}
        state.terminal_snapshots = raw_snapshots if isinstance(raw_snapshots, dict) else {}
        state.terminal_seq = int(data.get("terminal_seq", 0) or 0)
        if state.terminal_seq <= 0 and state.terminal_histories:
            max_id = 0
            for hist in state.terminal_histories.values():
                if not isinstance(hist, list):
                    continue
                for entry in hist:
                    try:
                        max_id = max(max_id, int(entry.get("id", 0)))
                    except Exception:
                        continue
            state.terminal_seq = max_id

        state.metrics = data.get("metrics", {})
        state.dataset_id = data.get("dataset_id", "")

        # Load the default dataset so list navigation works immediately
        ds = load_dataset(DATASET_PATH)
        if ds:
            state.dataset = ds
            fp = _dataset_fingerprint(ds)
            # If dataset changed since last run, clear stale results
            if state.dataset_id and state.dataset_id != fp:
                print(f"[startup] Dataset changed ({state.dataset_id} → {fp}), clearing old results")
                state.results = {}
                state.metrics = {}
                state.terminal_histories = {}
                state.terminal_snapshots = {}
                state.terminal_seq = 0
            state.dataset_id = fp

        print(
            f"[startup] Restored {len(state.results)} results, "
            f"{sum(len(v) for v in state.terminal_histories.values())} terminal entries "
            f"from {latest.name}"
        )
    except Exception as exc:
        print(f"[startup] Could not restore results: {exc}")


def _persist_state() -> None:
    """Write current in-memory results to a fixed snapshot file so the next
    server restart can reload them instantly."""
    if not state.results and not state.terminal_histories and not state.terminal_snapshots:
        return
    try:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "timestamp": time.strftime("%Y%m%d_%H%M%S"),
            "scenario": "all",
            "dataset_id": state.dataset_id,
            "metrics": state.metrics,
            "pass_k": {},
            "weights": WEIGHTS,
            "results": list(state.results.values()),
            "terminal_histories": state.terminal_histories,
            "terminal_snapshots": state.terminal_snapshots,
            "terminal_seq": state.terminal_seq,
        }
        snap = RESULTS_DIR / "eval_latest_snapshot.json"
        snap.write_text(json.dumps(data, default=str))
        print(
            f"[persist] Saved {len(state.results)} results, "
            f"{sum(len(v) for v in state.terminal_histories.values())} terminal entries → {snap}"
        )
    except Exception as exc:
        import traceback
        print(f"[persist] ERROR saving snapshot: {exc}")
        traceback.print_exc()


def _to_test_result(raw: dict, test_id_hint: str = "") -> Optional[TestResult]:
    """Convert stored result dicts to TestResult while ignoring UI-only keys."""
    try:
        allowed = set(TestResult.__dataclass_fields__.keys())
        cleaned = {k: v for k, v in raw.items() if k in allowed}
        if "error" not in cleaned:
            cleaned["error"] = None
        return TestResult(**cleaned)
    except Exception as exc:
        hint = test_id_hint or str(raw.get("test_id", "unknown"))
        logger.warning(f"Skipping malformed saved result for {hint}: {exc}")
        return None


def _trace_from_dict(raw: dict, test_id_hint: str = "") -> Optional[AgentTrace]:
    """Rebuild AgentTrace from persisted dict payload."""
    try:
        return AgentTrace(
            tools_called=list(raw.get("tools_called") or []),
            handoff_occurred=bool(raw.get("handoff_occurred")),
            hitl_triggered=bool(raw.get("hitl_triggered")),
            response=str(raw.get("response") or ""),
            latency_s=float(raw.get("latency_s") or 0.0),
            error=raw.get("error"),
            thinking=str(raw.get("thinking") or ""),
            tool_call_history=list(raw.get("tool_call_history") or []),
        )
    except Exception as exc:
        hint = test_id_hint or "unknown"
        logger.warning(f"Skipping malformed pending trace for {hint}: {exc}")
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    _restore_latest()
    yield


app = FastAPI(title="Slurm Agent Evaluation", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── API ───────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = Path(__file__).parent / "eval_ui.html"
    return html_path.read_text()


@app.post("/api/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    raw = await file.read()
    new_ds = json.loads(raw)
    new_fp = _dataset_fingerprint(new_ds)
    state.dataset = new_ds
    if new_fp != state.dataset_id:
        state.results = {}
        state.metrics = {}
        state.terminal_histories = {}
        state.terminal_snapshots = {}
        state.terminal_seq = 0
    state.dataset_id = new_fp
    state.progress = 0
    return {"ok": True, "count": len(state.dataset), "dataset_id": new_fp}


@app.post("/api/load-default-dataset")
async def load_default():
    new_ds = load_dataset(DATASET_PATH)
    new_fp = _dataset_fingerprint(new_ds)
    state.dataset = new_ds
    if new_fp != state.dataset_id:
        # Different dataset — wipe stale results
        state.results = {}
        state.metrics = {}
        state.terminal_histories = {}
        state.terminal_snapshots = {}
        state.terminal_seq = 0
    else:
        # Same dataset — restore results from snapshot so UI shows them
        _restore_latest()
    state.dataset_id = new_fp
    state.progress = 0
    return {"ok": True, "count": len(state.dataset), "dataset_id": new_fp}


@app.post("/api/clear-results")
async def clear_results():
    state.results = {}
    state.metrics = {}
    state.progress = 0
    state.judge_running = False
    state.judge_progress = 0
    state.judge_total = 0
    return {"ok": True}


@app.get("/api/dataset")
async def get_dataset(
    scenario: str = "",
    category: str = "",
    no_variants: bool = False,
):
    _heal_run_state()
    ds = filter_dataset(state.dataset, scenario=scenario, category=category, no_variants=no_variants)
    tests = []
    for t in ds:
        status = "untested"
        if t["id"] in state.results:
            r = state.results[t["id"]]
            if r.get("judge_pending"):
                status = "judging"
            else:
                status = "passed" if r["passed"] else "failed"
        if state.running and state.current_test == t["id"]:
            status = "running"
        tests.append({
            "id": t["id"],
            "category": t["category"],
            "scenario": t["scenario"],
            "input": t["input"],
            "is_variant": bool(t.get("variant_of")),
            "status": status,
        })
    return {"tests": tests, "total": len(tests)}


@app.get("/api/test/{test_id}")
async def get_test(test_id: str):
    test = next((t for t in state.dataset if t["id"] == test_id), None)
    if not test:
        return JSONResponse({"error": "not found"}, 404)
    result = state.results.get(test_id)
    return {"test": test, "result": result}


@app.post("/api/test/{test_id}/mark-bad")
async def mark_bad_test_case(test_id: str, reason: str = Body("", embed=True)):
    test = next((t for t in state.dataset if t["id"] == test_id), None)
    if not test:
        return JSONResponse({"error": "not found"}, 404)

    reason_txt = (reason or "").strip() or "Manually flagged by admin terminal."
    existing = state.results.get(test_id)
    if existing:
        rd = dict(existing)
    else:
        gt = test.get("ground_truth", {})
        tr = TestResult(
            test_id=test["id"],
            scenario=test.get("scenario", ""),
            category=test.get("category", ""),
            prompt=test.get("input", ""),
            gt_tools=gt.get("tools", []),
            gt_handoff=bool(gt.get("handoff", False)),
            gt_hitl=bool(gt.get("hitl", False)),
            gt_keywords=gt.get("keywords", []),
            agent_tools=[],
            agent_handoff=False,
            agent_hitl=False,
            agent_response="",
            agent_thinking="",
            tool_recall=0.0,
            routing_match=0.0,
            hitl_match=0.0,
            keyword_score=0.0,
            state_match=0.0,
            judge_score=0.0,
            judge_reason="",
            judge_ran=False,
            overall=0.0,
            passed=False,
            latency_s=0.0,
            is_variant=bool(test.get("variant_of")),
            error=None,
            tool_call_history=[],
        )
        rd = asdict(tr)
        rd["judge_pending"] = False

    rd["bad_test_case"] = True
    rd["bad_test_case_reason"] = reason_txt
    rd["judge_pending"] = False
    state.results[test_id] = rd

    all_results = []
    for t in state.dataset:
        raw = state.results.get(t["id"])
        if not raw:
            continue
        parsed = _to_test_result(raw, t["id"])
        if parsed is not None:
            all_results.append(parsed)
    state.metrics = compute_metrics(all_results) if all_results else {}
    _persist_state()
    return {"ok": True, "result": rd, "metrics": state.metrics}


@app.get("/api/results")
async def get_results():
    return {
        "results": list(state.results.values()),
        "metrics": state.metrics,
        "count": len(state.results),
        "total": len(state.dataset),
    }


@app.get("/api/status")
async def get_status():
    _heal_run_state()
    return {
        "running": state.running,
        "current_test": state.current_test,
        "progress": state.progress,
        "total": state.total,
        "judge_running": state.judge_running,
        "judge_progress": state.judge_progress,
        "judge_total": state.judge_total,
        "dataset_loaded": len(state.dataset) > 0,
        "results_count": len(state.results),
        "terminal_count": sum(len(v) for v in state.terminal_histories.values() if isinstance(v, list)),
    }


@app.get("/api/terminal/history")
async def get_terminal_history(test_id: str = ""):
    key = _terminal_key(test_id)
    hist = _terminal_history(key)
    return {
        "test_id": "" if key == "__global__" else key,
        "history": hist,
        "count": len(hist),
    }


@app.post("/api/terminal/clear")
async def clear_terminal_history(test_id: str = Body("", embed=True)):
    key = _terminal_key(test_id)
    if key == "__global__":
        state.terminal_histories = {}
        state.terminal_snapshots = {}
    else:
        state.terminal_histories.pop(key, None)
        state.terminal_snapshots.pop(key, None)
    _persist_state()
    return {"ok": True}


@app.post("/api/terminal/run")
async def run_terminal_command(
    command: str = Body(..., embed=True),
    test_id: str = Body("", embed=True),
    mcp_url: str = Body("", embed=True),
):
    cmd = (command or "").strip()
    key = _terminal_key(test_id)
    if not cmd:
        return JSONResponse({"ok": False, "error": "command is required"}, 400)
    if key == "__global__":
        return JSONResponse({
            "ok": False,
            "error": "test_id is required. Select a test to run an isolated terminal command.",
        }, 400)
    if mcp_url:
        state.mcp_url = mcp_url

    prep_ok = True
    prep_msg = ""
    tool_name = ""
    tool_args: Dict[str, str] = {}
    ok = True
    output = ""
    state_snapshot: Optional[dict] = None
    async with _mcp_state_lock:
        try:
            async with _mcp_session(state.mcp_url) as mcp:
                prep_ok, prep_msg = await _prepare_terminal_state_for_test(key, session=mcp)
                if prep_ok:
                    try:
                        tool_name, tool_args = _dispatch_terminal_command(cmd)
                        output = await _call_mcp_tool(state.mcp_url, tool_name, tool_args, session=mcp)
                        low = output.strip().lower()
                        if low.startswith("error") or ": error:" in low:
                            ok = False
                        state_snapshot = await _get_terminal_state_snapshot(state.mcp_url, session=mcp)
                    except Exception as exc:
                        ok = False
                        output = str(exc)
        except Exception as exc:
            prep_ok = False
            prep_msg = f"terminal connection error: {exc}"
    if not prep_ok:
        ok = False
        output = f"terminal setup error: {prep_msg}"
    if not output:
        output = "(no output)"
    if not prep_ok:
        tool_name = ""
        tool_args = {}
    elif not tool_name and ok:
        # Should not happen, but keep transcript explicit.
        ok = False
        output = "terminal error: command dispatch produced no tool"

    if prep_ok:
        low = output.strip().lower()
        if low.startswith("error") or ": error:" in low:
            ok = False
        if prep_msg:
            output = f"[setup] {prep_msg}\n\n{output}"

    if prep_ok and isinstance(state_snapshot, dict):
        state.terminal_snapshots[key] = state_snapshot

    entry = _append_terminal_entry(
        key,
        cmd,
        output,
        ok,
        tool_name,
        tool_args,
        state_snapshot=None,
    )
    _persist_state()
    hist = _terminal_history(key)
    return {"ok": ok, "entry": entry, "history": hist, "test_id": entry.get("test_id", "")}


@app.post("/api/run")
async def run_eval(
    scenario: str = "",
    category: str = "",
    no_variants: bool = False,
    agent_url: str = AGENT_URL,
    mcp_url: str = "",
    auto_approve: bool = True,
    use_judge: bool = False,
    judge_model: str = JUDGE_MODEL,
    resume: bool = True,
    force: bool = False,
):
    """Start evaluation, returns SSE stream of progress.
    Runs execute in a background task so they continue after client disconnect.
    """
    _heal_run_state()
    # If already running and caller did not force restart, attach to live stream.
    if state.running and state.run_task and state.run_id and not force:
        from_seq = max(0, state.event_seq - 1000)
        return StreamingResponse(
            _stream_events(state.run_id, from_seq),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # force=true: stop prior run task cleanly first
    if state.running and force and state.run_task:
        state.run_task.cancel()
        try:
            await state.run_task
        except asyncio.CancelledError:
            pass
        except Exception:
            pass
        state.running = False
        state.current_test = ""
    if not state.dataset:
        return JSONResponse({"error": "no dataset loaded"}, 400)

    state.agent_url = agent_url
    if mcp_url:
        state.mcp_url = mcp_url
    state.use_judge = use_judge
    state.judge_model = _normalize_judge_model(judge_model)
    state.auto_approve = auto_approve

    scope_ds = filter_dataset(state.dataset, scenario=scenario, category=category, no_variants=no_variants)
    if not scope_ds:
        return JSONResponse({"error": "no tests match filters"}, 400)

    scope_index = {t["id"]: i for i, t in enumerate(scope_ds)}
    pending_judge_items: list = []

    # Resume mode (default): only run tests that don't already have results.
    # This lets "Run All" continue from where it stopped.
    if resume and not force:
        ds_to_run = []
        for t in scope_ds:
            r = state.results.get(t["id"])
            if not r:
                ds_to_run.append(t)
                continue

            if use_judge and r.get("judge_pending"):
                restored = _trace_from_dict(r.get("_pending_trace") or {}, t["id"])
                if restored is not None:
                    pending_judge_items.append((t, restored, scope_index[t["id"]]))
                else:
                    # Trace unavailable/corrupt: re-run this test to recreate judge input.
                    ds_to_run.append(t)
                continue
    else:
        ds_to_run = scope_ds

    judge_total = len(ds_to_run) + len(pending_judge_items) if use_judge else 0

    # Start a new background run
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    state.run_id = run_id
    state.total = len(scope_ds)
    state.progress = 0
    state.judge_running = False
    state.judge_progress = 0
    state.judge_total = judge_total
    scenario_label = scenario or "all"
    state.run_task = asyncio.create_task(
        _run_eval_background(
            ds_to_run=ds_to_run,
            scope_ds=scope_ds,
            pending_judge_items=pending_judge_items,
            agent_url=agent_url,
            mcp_url=state.mcp_url,
            auto_approve=auto_approve,
            use_judge=use_judge,
            run_id=run_id,
            scenario_label=scenario_label,
        )
    )

    return StreamingResponse(
        _stream_events(run_id, max(0, state.event_seq - 1)),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/stop")
async def stop_run():
    """Force-reset the running state (e.g. after client disconnects mid-run)."""
    if state.run_task:
        state.run_task.cancel()
        try:
            await state.run_task
        except asyncio.CancelledError:
            pass
        except Exception:
            pass
        state.run_task = None
    state.running = False
    state.current_test = ""
    if state.run_id:
        _push_event("stopped", {"run_id": state.run_id, "reason": "api_stop"}, state.run_id)
    state.judge_running = False
    state.judge_progress = 0
    state.judge_total = 0
    return {"ok": True}


@app.post("/api/run-single/{test_id}")
async def run_single(
    test_id: str,
    agent_url: str = AGENT_URL,
    mcp_url: str = "",
    auto_approve: bool = True,
    use_judge: bool = False,
    judge_model: str = "",
):
    """Run a single test case."""
    test = next((t for t in state.dataset if t["id"] == test_id), None)
    if not test:
        return JSONResponse({"error": "not found"}, 404)

    if mcp_url:
        state.mcp_url = mcp_url
    if judge_model:
        state.judge_model = _normalize_judge_model(judge_model)
    else:
        state.judge_model = _normalize_judge_model(state.judge_model)

    # Reset to this test's declared baseline before single-run evaluation.
    await _reset_state_for_test(state.mcp_url, test)

    session_id = f"eval_{test_id}_{int(time.time())}"
    try:
        trace = await run_agent(test["input"], session_id, agent_url, auto_approve)
    except Exception as e:
        trace = AgentTrace([], False, False, "", 0.0, str(e))
    result = await score_test(
        test,
        trace,
        use_judge=use_judge,
        judge_model=state.judge_model,
    )
    rd = asdict(result)
    rd["judge_pending"] = False
    state.results[test_id] = rd

    # Recompute metrics
    all_results = []
    for t in state.dataset:
        if t["id"] in state.results:
            parsed = _to_test_result(state.results[t["id"]], t["id"])
            if parsed is not None:
                all_results.append(parsed)
    if all_results:
        state.metrics = compute_metrics(all_results)
    _persist_state()

    return {"result": rd, "metrics": state.metrics}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--host", default="0.0.0.0")
    args = p.parse_args()
    print(f"\n  Evaluation UI: http://localhost:{args.port}\n")
    uvicorn.run(app, host=args.host, port=args.port)
