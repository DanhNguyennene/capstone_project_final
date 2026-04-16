#!/usr/bin/env python3
"""
Human vs Agent Evaluation
==========================
Compares what a human Slurm expert would do (ground truth in test_cases.py)
against what the agent system actually does, on each test case.

Scoring dimensions (per test case):
  Tool Recall     (35%) — did the agent call the tools a human would?
  Handoff Match   (25%) — correct Observer→Operator routing decision?
  HITL Match      (25%) — confirmation triggered when expected?
  Keyword Score   (15%) — expected terms present in the response?

Usage:
  # Run all tests (MCP + Agent must be running):
  python evaluate.py

  # Run a specific category:
  python evaluate.py --category action_single

  # Run a single test:
  python evaluate.py --id act_01

  # Auto-approve HITL actions (test the full flow):
  python evaluate.py --auto-approve

  # Point at a non-default agent:
  python evaluate.py --agent-url http://localhost:8000

Output:
  results/eval_<timestamp>.json        — full per-case results
  results/eval_<timestamp>_summary.tex — LaTeX table for the report
"""

import asyncio
import json
import re
import sys
import time
import argparse
import datetime
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    import aiohttp
except ImportError:
    print("ERROR: aiohttp not installed.  pip install aiohttp")
    sys.exit(1)

# Allow running from any cwd
sys.path.insert(0, str(Path(__file__).parent))
from test_cases import TestCase, HumanBaseline, TESTS, CATEGORIES

# ── Constants ─────────────────────────────────────────────────────────────────

AGENT_URL  = "http://localhost:8000"
RESULTS_DIR = Path(__file__).parent / "results"

# MCP tool names that are "routing" calls, not real operations
ROUTING_TOOLS = {"transfer_to_operator", "transfer_to_observer"}

WEIGHTS = {
    "tool_recall":    0.35,
    "handoff_match":  0.25,
    "hitl_match":     0.25,
    "keyword_score":  0.15,
}

# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class AgentTrace:
    """What we observed the agent actually doing."""
    tools_called:     List[str]   # MCP tools called (excluding routing)
    handoff_occurred: bool        # Observer handed off to Operator?
    hitl_triggered:   bool        # Pending-approval prompt appeared?
    response:         str         # Final text shown to the user
    latency_s:        float
    error:            Optional[str] = None


@dataclass
class EvalResult:
    """Per-test-case comparison: human baseline vs agent trace + scores."""
    case_id:   str
    category:  str
    prompt:    str

    # Human ground truth
    h_tools:   List[str]
    h_handoff: bool
    h_hitl:    bool
    h_keywords: List[str]

    # Agent observed
    a_tools:   List[str]
    a_handoff: bool
    a_hitl:    bool
    a_response: str
    a_error:   Optional[str]
    latency_s: float

    # Scores [0, 1]
    tool_recall:   float
    handoff_match: float
    hitl_match:    float
    keyword_score: float
    overall:       float


# ── SSE stream parser ─────────────────────────────────────────────────────────

def _extract_tool_from_status(msg: str) -> Optional[str]:
    """
    Parse a status_update string like '$ squeue --state RUNNING' → 'squeue'.
    Returns None for handoff messages, HITL warnings, or non-tool lines.
    """
    msg = msg.strip()
    if msg.startswith("$ "):
        raw = msg[2:].split()[0]          # first word after "$ "
        if raw not in ROUTING_TOOLS:
            return raw
    return None


def _parse_sse_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse a single SSE 'data: ...' line into a dict, or None."""
    if not line.startswith("data:"):
        return None
    payload = line[5:].strip()
    if payload == "[DONE]":
        return {"_done": True}
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return None


async def run_agent(
    prompt: str,
    session_id: str,
    agent_url: str = AGENT_URL,
    auto_approve: bool = False,
) -> AgentTrace:
    """
    Send `prompt` to the agent SSE endpoint and collect the full trace.
    If HITL triggers and auto_approve=True, automatically approves and
    continues to capture the rest of the response.
    """
    tools_called:     List[str] = []
    handoff_occurred: bool      = False
    hitl_triggered:   bool      = False
    response_parts:   List[str] = []
    start = time.monotonic()

    payload = {
        "model":    "slurm-agent",
        "stream":   True,
        "chat_id":  session_id,
        "messages": [{"role": "user", "content": prompt}],
    }

    async def _stream_once(p: dict) -> bool:
        """
        Stream one request.  Returns True if HITL was encountered
        (caller may want to send an approval follow-up).
        """
        nonlocal handoff_occurred, hitl_triggered
        saw_hitl = False

        async with session.post(f"{agent_url}/v1/chat/completions", json=p) as resp:
            if resp.status != 200:
                raise RuntimeError(f"HTTP {resp.status}: {await resp.text()}")

            async for raw_line in resp.content:
                line = raw_line.decode("utf-8", errors="replace").rstrip("\n\r")
                chunk = _parse_sse_line(line)
                if not chunk or chunk.get("_done"):
                    break

                choices = chunk.get("choices", [])
                if not choices:
                    continue
                delta = choices[0].get("delta", {})

                # ── Tool calls / handoffs via status_update ──
                status = delta.get("status_update", "")
                if status:
                    tool = _extract_tool_from_status(status)
                    if tool:
                        tools_called.append(tool)
                    if "Handing off to Operator" in status:
                        handoff_occurred = True

                # ── Response text ──
                content = delta.get("content", "")
                if content:
                    response_parts.append(content)

                # ── HITL pending actions ──
                pending = delta.get("pending_actions")
                if pending:
                    hitl_triggered = True
                    saw_hitl = True

        return saw_hitl

    try:
        async with aiohttp.ClientSession() as session:
            saw_hitl = await _stream_once(payload)

            # Auto-approve: send a follow-up with hitl_decision=approve
            if saw_hitl and auto_approve:
                approve_payload = {
                    **payload,
                    "messages": payload["messages"] + [
                        {"role": "user", "content": "approve"}
                    ],
                    "hitl_decision": "approve",
                }
                await _stream_once(approve_payload)

    except Exception as exc:
        return AgentTrace(
            tools_called=tools_called,
            handoff_occurred=handoff_occurred,
            hitl_triggered=hitl_triggered,
            response="".join(response_parts),
            latency_s=time.monotonic() - start,
            error=str(exc),
        )

    return AgentTrace(
        tools_called=tools_called,
        handoff_occurred=handoff_occurred,
        hitl_triggered=hitl_triggered,
        response="".join(response_parts),
        latency_s=time.monotonic() - start,
    )


# ── Scorer ────────────────────────────────────────────────────────────────────

def score(trace: AgentTrace, tc: TestCase) -> EvalResult:
    bl = tc.baseline

    # ── Tool Recall ──────────────────────────────────────────────────────────
    # How many of the tools a human would call did the agent also call?
    called  = set(trace.tools_called) - ROUTING_TOOLS
    expected = set(bl.tools)
    rejected = set(bl.reject_tools)

    if expected:
        tp = len(called & expected)
        tool_recall = tp / len(expected)
    else:
        # No tools expected — perfect if nothing called, penalise otherwise
        tool_recall = 1.0 if not called else 0.0

    # Reject penalty: subtract 0.5 × fraction of reject_tools actually called
    if rejected:
        reject_frac = len(called & rejected) / len(rejected)
        tool_recall = max(0.0, tool_recall - 0.5 * reject_frac)

    # ── Handoff Match ────────────────────────────────────────────────────────
    handoff_match = 1.0 if trace.handoff_occurred == bl.handoff else 0.0

    # ── HITL Match ───────────────────────────────────────────────────────────
    hitl_match = 1.0 if trace.hitl_triggered == bl.hitl else 0.0

    # ── Keyword Coverage ─────────────────────────────────────────────────────
    resp_lower = trace.response.lower()
    if bl.keywords:
        found = sum(1 for kw in bl.keywords if kw.lower() in resp_lower)
        keyword_score = found / len(bl.keywords)
    else:
        keyword_score = 1.0

    # Reject keyword penalty
    if bl.reject_keywords:
        bad = sum(1 for kw in bl.reject_keywords if kw.lower() in resp_lower)
        keyword_score = max(0.0, keyword_score - 0.3 * (bad / len(bl.reject_keywords)))

    # ── Overall ──────────────────────────────────────────────────────────────
    overall = (
        WEIGHTS["tool_recall"]   * tool_recall   +
        WEIGHTS["handoff_match"] * handoff_match +
        WEIGHTS["hitl_match"]    * hitl_match    +
        WEIGHTS["keyword_score"] * keyword_score
    )

    return EvalResult(
        case_id=tc.id,
        category=tc.category,
        prompt=tc.prompt,
        # ground truth
        h_tools=bl.tools,
        h_handoff=bl.handoff,
        h_hitl=bl.hitl,
        h_keywords=bl.keywords,
        # observed
        a_tools=list(called),
        a_handoff=trace.handoff_occurred,
        a_hitl=trace.hitl_triggered,
        a_response=trace.response[:400],   # truncate for storage
        a_error=trace.error,
        latency_s=round(trace.latency_s, 2),
        # scores
        tool_recall=round(tool_recall, 3),
        handoff_match=round(handoff_match, 3),
        hitl_match=round(hitl_match, 3),
        keyword_score=round(keyword_score, 3),
        overall=round(overall, 3),
    )


# ── Report helpers ────────────────────────────────────────────────────────────

def _pct(v: float) -> str:
    return f"{v*100:.0f}%"

def _check(match: float) -> str:
    return "✓" if match >= 1.0 else "✗"


def print_report(results: List[EvalResult]) -> None:
    """Print a per-case comparison table and category summary to stdout."""
    # Header
    print("\n" + "="*90)
    print(f"{'ID':<10} {'Category':<14} {'Tools':>6} {'Handoff':>8} {'HITL':>6} {'Keywords':>9} {'Overall':>8}  Human→Agent")
    print("-"*90)

    for r in results:
        # Compact human-vs-agent tool diff
        h_set = set(r.h_tools)
        a_set = set(r.a_tools)
        only_h = h_set - a_set   # missed
        only_a = a_set - h_set   # extra
        diff_parts = []
        if only_h:  diff_parts.append(f"missed={','.join(sorted(only_h))}")
        if only_a:  diff_parts.append(f"extra={','.join(sorted(only_a))}")
        diff = " ".join(diff_parts) or "exact match"

        flag = " [ERR]" if r.a_error else ""
        print(
            f"{r.case_id:<10} {r.category:<14}"
            f" {_pct(r.tool_recall):>6}"
            f" {_check(r.handoff_match):>8}"
            f" {_check(r.hitl_match):>6}"
            f" {_pct(r.keyword_score):>9}"
            f" {_pct(r.overall):>8}"
            f"  {diff}{flag}"
        )

    # Category summary
    print("\n" + "="*90)
    print(f"{'Category':<16} {'N':>4} {'ToolRecall':>12} {'Handoff%':>10} {'HITL%':>8} {'Overall':>9}")
    print("-"*90)

    from collections import defaultdict
    by_cat: Dict[str, List[EvalResult]] = defaultdict(list)
    for r in results:
        by_cat[r.category].append(r)

    all_scores: List[float] = []
    for cat in sorted(by_cat):
        group = by_cat[cat]
        n = len(group)
        tr  = sum(r.tool_recall   for r in group) / n
        hm  = sum(r.handoff_match for r in group) / n
        hm2 = sum(r.hitl_match    for r in group) / n
        ov  = sum(r.overall       for r in group) / n
        all_scores.extend(r.overall for r in group)
        print(
            f"{cat:<16} {n:>4}"
            f" {_pct(tr):>12}"
            f" {_pct(hm):>10}"
            f" {_pct(hm2):>8}"
            f" {_pct(ov):>9}"
        )

    grand = sum(all_scores) / max(1, len(all_scores))
    print("-"*90)
    print(f"{'TOTAL':<16} {len(results):>4}  {'Overall score':>22} {_pct(grand):>18}")
    print("="*90 + "\n")


def save_results(results: List[EvalResult], tag: str = "") -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"eval_{ts}{('_' + tag) if tag else ''}"

    # JSON
    json_path = RESULTS_DIR / f"{name}.json"
    with open(json_path, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    # LaTeX summary table
    tex_path = RESULTS_DIR / f"{name}.tex"
    _write_latex(results, tex_path)

    print(f"Results saved:\n  {json_path}\n  {tex_path}")
    return json_path


def _write_latex(results: List[EvalResult], path: Path) -> None:
    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\caption{Human vs Agent Evaluation Results}",
        r"\label{tab:eval_results}",
        r"\begin{tabular}{llrcccc}",
        r"\toprule",
        r"\textbf{ID} & \textbf{Category} & \textbf{Tools} & \textbf{Handoff} & \textbf{HITL} & \textbf{Keywords} & \textbf{Score} \\",
        r"\midrule",
    ]
    from collections import defaultdict
    by_cat: Dict[str, List[EvalResult]] = defaultdict(list)
    for r in results:
        by_cat[r.category].append(r)

    for cat in sorted(by_cat):
        for r in by_cat[cat]:
            hm  = r"$\checkmark$" if r.handoff_match >= 1.0 else r"$\times$"
            hit = r"$\checkmark$" if r.hitl_match    >= 1.0 else r"$\times$"
            lines.append(
                f"  {r.case_id} & {r.category.replace('_', ' ')} & {_pct(r.tool_recall)}"
                f" & {hm} & {hit} & {_pct(r.keyword_score)} & {_pct(r.overall)} \\\\"
            )
        lines.append(r"\midrule")

    # Grand average row
    n = len(results)
    avg_tr = sum(r.tool_recall   for r in results) / n
    avg_ov = sum(r.overall       for r in results) / n
    lines.extend([
        f"  \\textbf{{Average}} & & {_pct(avg_tr)} & & & & {_pct(avg_ov)} \\\\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ])
    path.write_text("\n".join(lines))


# ── Main runner ───────────────────────────────────────────────────────────────

async def _run_all(
    tests: List[TestCase],
    agent_url: str,
    auto_approve: bool,
    delay: float,
) -> List[EvalResult]:
    results: List[EvalResult] = []
    for i, tc in enumerate(tests, 1):
        print(f"  [{i:02d}/{len(tests):02d}] {tc.id:<10} — {tc.prompt[:55]}…", end=" ", flush=True)
        session_id = f"eval_{tc.id}_{int(time.time())}"
        trace = await run_agent(tc.prompt, session_id, agent_url, auto_approve)
        result = score(trace, tc)
        results.append(result)
        status = "ERR" if trace.error else f"{_pct(result.overall)}"
        print(f"[{status}]  ({result.latency_s:.1f}s)")
        if delay > 0:
            await asyncio.sleep(delay)
    return results


async def _check_agent(agent_url: str) -> bool:
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{agent_url}/health", timeout=aiohttp.ClientTimeout(total=3)) as r:
                return r.status == 200
    except Exception:
        return False


async def main_async(args: argparse.Namespace) -> None:
    # Select tests
    tests = TESTS
    if args.category:
        tests = [tc for tc in tests if tc.category == args.category]
        if not tests:
            print(f"ERROR: no tests for category '{args.category}'. Available: {CATEGORIES}")
            sys.exit(1)
    if args.id:
        tests = [tc for tc in tests if tc.id == args.id]
        if not tests:
            print(f"ERROR: no test with id='{args.id}'.")
            sys.exit(1)
    if args.n:
        from itertools import islice
        tests = list(islice(tests, args.n))

    if args.dry_run:
        print(f"\nDry run — {len(tests)} test(s) selected:\n")
        for tc in tests:
            print(f"  {tc.id:<10} [{tc.category}]  handoff={tc.baseline.handoff}  "
                  f"hitl={tc.baseline.hitl}  tools={tc.baseline.tools}")
        return

    # Pre-flight check
    print(f"\nChecking agent at {args.agent_url}… ", end="")
    reachable = await _check_agent(args.agent_url)
    if not reachable:
        print("UNREACHABLE")
        print("Make sure the agent (uvicorn main:app --port 8000) is running.")
        sys.exit(1)
    print("OK")

    print(f"\nRunning {len(tests)} test(s)   auto-approve={args.auto_approve}\n")
    t0 = time.monotonic()
    results = await _run_all(tests, args.agent_url, args.auto_approve, args.delay)
    elapsed = time.monotonic() - t0

    print_report(results)
    print(f"Total time: {elapsed:.1f}s")
    save_results(results, tag=args.category or args.id or "")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate agent actions against human-expert baselines."
    )
    parser.add_argument("--agent-url",    default=AGENT_URL,
                        help="Agent API base URL (default: %(default)s)")
    parser.add_argument("--category",     default="",
                        help=f"Only run tests in this category. Choices: {CATEGORIES}")
    parser.add_argument("--id",           default="",
                        help="Run a single test by ID, e.g. act_01")
    parser.add_argument("--n",            type=int, default=0,
                        help="Run only the first N tests (0 = all)")
    parser.add_argument("--auto-approve", action="store_true",
                        help="Automatically approve HITL prompts to test the full flow")
    parser.add_argument("--delay",        type=float, default=1.5,
                        help="Seconds to wait between tests (default: 1.5)")
    parser.add_argument("--dry-run",      action="store_true",
                        help="Print selected tests without running them")
    args = parser.parse_args()

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
