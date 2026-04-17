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
import time
import argparse
import uuid
import os
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from scenario_eval import (
    load_dataset, filter_dataset, run_agent, score_test, judge_flow,
    compute_metrics, compute_pass_k, save_results,
    AgentTrace, TestResult,
    AGENT_URL, PASS_THRESHOLD, WEIGHTS, WEIGHTS_WITH_JUDGE,
    DATASET_PATH, RESULTS_DIR,
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
    judge_model: str = "qwen3.5:9b"
    auto_approve: bool = True
    mcp_url: str = os.getenv("MCP_SERVER_URL", "http://localhost:3002")
    run_task: Optional[asyncio.Task] = None
    run_id: str = ""
    event_seq: int = 0
    event_log: list = []   # append-only in-memory SSE history for re-attach

state = EvalState()


async def _reset_state_for_test(mcp_url: str, test: dict) -> tuple[bool, str]:
    """Reset stateful mock MCP to this test's source_state baseline."""
    scenario = str(test.get("scenario", "") or "")
    source_state = test.get("source_state") or {}
    try:
        from mcp import ClientSession as MCPClientSession
        from mcp.client.sse import sse_client

        async with sse_client(f"{mcp_url.rstrip('/')}/sse") as (read, write):
            async with MCPClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "reset_mock_state",
                    {
                        "scenario": scenario,
                        "source_state_json": json.dumps(source_state),
                    },
                )
                return True, str(getattr(result, "content", result))[:400]
    except Exception as e:
        return False, f"mcp-sdk reset failed: {e}"


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


async def _run_eval_background(
    ds: list,
    agent_url: str,
    mcp_url: str,
    auto_approve: bool,
    use_judge: bool,
    run_id: str,
    scenario_label: str,
) -> None:
    """Execute evaluation independently from client connection lifecycle."""
    state.running = True
    state.total = len(ds)
    state.progress = 0
    state.current_test = ""
    _push_event("start", {"total": len(ds), "judge": use_judge, "run_id": run_id}, run_id)

    try:
        results_list = []
        for i, test in enumerate(ds):
            state.current_test = test["id"]
            state.progress = i

            # Deterministic baseline: restore test source_state before each case.
            ok, msg = await _reset_state_for_test(mcp_url, test)
            _push_event("state_reset", {
                "index": i,
                "id": test["id"],
                "ok": ok,
                "details": msg[:600],
                "run_id": run_id,
            }, run_id)

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
                state.results[test["id"]] = rd
                results_list.append(failed)
                _persist_state()
                _push_event("test_done", {
                    "index": i,
                    "id": test["id"],
                    "result": rd,
                    "run_id": run_id,
                }, run_id)
                continue

            _push_event("test_start", {
                "index": i,
                "id": test["id"],
                "category": test["category"],
                "scenario": test["scenario"],
                "input": test["input"],
                "run_id": run_id,
            }, run_id)

            session_id = f"eval_{test['id']}_{int(time.time())}"
            try:
                trace = await run_agent(
                    test["input"], session_id, agent_url, auto_approve,
                )
                result = await score_test(test, trace, use_judge=use_judge)
            except Exception as e:
                trace = AgentTrace([], False, False, "", 0.0, str(e))
                result = await score_test(test, trace, use_judge=use_judge)

            rd = asdict(result)
            state.results[test["id"]] = rd
            results_list.append(result)
            _persist_state()   # write after every test so a mid-run crash loses nothing

            _push_event("test_done", {
                "index": i,
                "id": test["id"],
                "result": rd,
                "run_id": run_id,
            }, run_id)

            await asyncio.sleep(0.5)

        # Compute final metrics
        metrics = compute_metrics(results_list)
        state.metrics = metrics

        # Save to disk (timestamped copy + rolling snapshot)
        save_results(results_list, metrics, scenario_label)
        _persist_state()

        _push_event("complete", {
            "metrics": metrics,
            "count": len(results_list),
            "run_id": run_id,
        }, run_id)

    except asyncio.CancelledError:
        _push_event("stopped", {"run_id": run_id, "reason": "cancelled"}, run_id)
        raise
    except Exception as e:
        _push_event("error", {"run_id": run_id, "error": str(e)}, run_id)
    finally:
        state.running = False
        state.current_test = ""
        state.run_task = None


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
        if not raw_results:
            return

        # Rebuild the results dict
        for r in raw_results:
            state.results[r["test_id"]] = r

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
            state.dataset_id = fp

        print(f"[startup] Restored {len(state.results)} results from {latest.name}")
    except Exception as exc:
        print(f"[startup] Could not restore results: {exc}")


def _persist_state() -> None:
    """Write current in-memory results to a fixed snapshot file so the next
    server restart can reload them instantly."""
    if not state.results:
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
        }
        snap = RESULTS_DIR / "eval_latest_snapshot.json"
        snap.write_text(json.dumps(data, default=str))
        print(f"[persist] Saved {len(state.results)} results → {snap}")
    except Exception as exc:
        import traceback
        print(f"[persist] ERROR saving snapshot: {exc}")
        traceback.print_exc()


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
    return {"ok": True}


@app.get("/api/dataset")
async def get_dataset(
    scenario: str = "",
    category: str = "",
    no_variants: bool = False,
):
    ds = filter_dataset(state.dataset, scenario=scenario, category=category, no_variants=no_variants)
    tests = []
    for t in ds:
        status = "untested"
        if t["id"] in state.results:
            r = state.results[t["id"]]
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
    return {
        "running": state.running,
        "current_test": state.current_test,
        "progress": state.progress,
        "total": state.total,
        "dataset_loaded": len(state.dataset) > 0,
        "results_count": len(state.results),
    }


@app.post("/api/run")
async def run_eval(
    scenario: str = "",
    category: str = "",
    no_variants: bool = False,
    agent_url: str = AGENT_URL,
    mcp_url: str = "",
    auto_approve: bool = True,
    use_judge: bool = False,
    judge_model: str = "qwen3.5:9b",
    force: bool = False,
):
    """Start evaluation, returns SSE stream of progress.
    Runs execute in a background task so they continue after client disconnect.
    """
    # If already running and caller did not force restart, attach to live stream.
    if state.running and state.run_id and not force:
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
    state.judge_model = judge_model
    state.auto_approve = auto_approve

    ds = filter_dataset(state.dataset, scenario=scenario, category=category, no_variants=no_variants)
    if not ds:
        return JSONResponse({"error": "no tests match filters"}, 400)

    # Start a new background run
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    state.run_id = run_id
    state.total = len(ds)
    state.progress = 0
    scenario_label = scenario or "all"
    state.run_task = asyncio.create_task(
        _run_eval_background(
            ds=ds,
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
        except Exception:
            pass
        state.run_task = None
    state.running = False
    state.current_test = ""
    if state.run_id:
        _push_event("stopped", {"run_id": state.run_id, "reason": "api_stop"}, state.run_id)
    return {"ok": True}


@app.post("/api/run-single/{test_id}")
async def run_single(
    test_id: str,
    agent_url: str = AGENT_URL,
    mcp_url: str = "",
    auto_approve: bool = True,
    use_judge: bool = False,
):
    """Run a single test case."""
    test = next((t for t in state.dataset if t["id"] == test_id), None)
    if not test:
        return JSONResponse({"error": "not found"}, 404)

    if mcp_url:
        state.mcp_url = mcp_url

    # Reset to this test's declared baseline before single-run evaluation.
    await _reset_state_for_test(state.mcp_url, test)

    session_id = f"eval_{test_id}_{int(time.time())}"
    try:
        trace = await run_agent(test["input"], session_id, agent_url, auto_approve)
    except Exception as e:
        trace = AgentTrace([], False, False, "", 0.0, str(e))
    result = await score_test(test, trace, use_judge=use_judge)
    rd = asdict(result)
    state.results[test_id] = rd

    # Recompute metrics
    all_results = []
    for t in state.dataset:
        if t["id"] in state.results:
            r = state.results[t["id"]]
            all_results.append(TestResult(**{k: v for k, v in r.items() if k != "error" or v is not None}))
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
