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
import json
import time
import argparse
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Optional

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

app = FastAPI(title="Slurm Agent Evaluation")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── State ─────────────────────────────────────────────────────────────────────

class EvalState:
    dataset: list = []
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

state = EvalState()

# ── API ───────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = Path(__file__).parent / "eval_ui.html"
    return html_path.read_text()


@app.post("/api/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    raw = await file.read()
    state.dataset = json.loads(raw)
    state.results = {}
    state.metrics = {}
    state.progress = 0
    return {"ok": True, "count": len(state.dataset)}


@app.post("/api/load-default-dataset")
async def load_default():
    state.dataset = load_dataset(DATASET_PATH)
    state.results = {}
    state.metrics = {}
    state.progress = 0
    return {"ok": True, "count": len(state.dataset)}


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
    auto_approve: bool = True,
    use_judge: bool = False,
    judge_model: str = "qwen3.5:9b",
):
    """Start evaluation, returns SSE stream of progress."""
    if state.running:
        return JSONResponse({"error": "already running"}, 409)
    if not state.dataset:
        return JSONResponse({"error": "no dataset loaded"}, 400)

    state.agent_url = agent_url
    state.use_judge = use_judge
    state.judge_model = judge_model
    state.auto_approve = auto_approve

    ds = filter_dataset(state.dataset, scenario=scenario, category=category, no_variants=no_variants)
    if not ds:
        return JSONResponse({"error": "no tests match filters"}, 400)

    async def stream():
        state.running = True
        state.total = len(ds)
        state.progress = 0

        def _ev(event: str, data: dict) -> str:
            return f"event: {event}\ndata: {json.dumps(data)}\n\n"

        yield _ev("start", {"total": len(ds), "judge": use_judge})

        results_list = []
        for i, test in enumerate(ds):
            state.current_test = test["id"]
            state.progress = i

            yield _ev("test_start", {
                "index": i,
                "id": test["id"],
                "category": test["category"],
                "scenario": test["scenario"],
                "input": test["input"],
            })

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

            yield _ev("test_done", {
                "index": i,
                "id": test["id"],
                "result": rd,
            })

            # Small delay to avoid overwhelming agent
            await asyncio.sleep(0.5)

        # Compute final metrics
        metrics = compute_metrics(results_list)
        state.metrics = metrics

        # Save to disk
        scenario_label = scenario or "all"
        save_results(results_list, metrics, scenario_label)

        yield _ev("complete", {"metrics": metrics, "count": len(results_list)})

        state.running = False
        state.current_test = ""

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/run-single/{test_id}")
async def run_single(
    test_id: str,
    agent_url: str = AGENT_URL,
    auto_approve: bool = True,
    use_judge: bool = False,
):
    """Run a single test case."""
    test = next((t for t in state.dataset if t["id"] == test_id), None)
    if not test:
        return JSONResponse({"error": "not found"}, 404)

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

    return {"result": rd, "metrics": state.metrics}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--host", default="0.0.0.0")
    args = p.parse_args()
    print(f"\n  Evaluation UI: http://localhost:{args.port}\n")
    uvicorn.run(app, host=args.host, port=args.port)
