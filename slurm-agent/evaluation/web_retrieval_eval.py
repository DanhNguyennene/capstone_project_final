#!/usr/bin/env python3
"""
Web-Grounded Retrieval Evaluation
====================================
Evaluates the agent's ability to escalate from local RAG to web search
when the local corpus cannot answer the question.

Tests the lookup_slurm_docs → web_search escalation path.
Uses the standard scenario_eval scoring but with additional metrics:
  - Web escalation rate: did the agent correctly call web_search?
  - Retrieval path correctness: local-first → web fallback ordering
  - Answer grounding: keywords in response demonstrate real web content

Usage:
  python web_retrieval_eval.py --auto-approve --llm-provider openai
  python web_retrieval_eval.py --auto-approve --judge --judge-model gpt-oss:20b --llm-provider openai
"""

import asyncio
import json
import time
import argparse
import sys
import os
import datetime
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    import aiohttp
except ImportError:
    print("ERROR: pip install aiohttp")
    sys.exit(1)

from scenario_eval import (
    run_agent, clear_agent_session, score_test, reset_mock_state_for_test,
    AgentTrace, TestResult, ROUTING_TOOLS,
    AGENT_URL, MCP_URL, JUDGE_MODEL, JUDGE_PROVIDER, PASS_THRESHOLD,
    CHAT_LLM_PROVIDER, MAIN_MODEL, SPECIALIST_MODEL,
    _normalize_eval_provider, _judge_provider_for, _pct,
)

DATASET_PATH = Path(__file__).parent / "web_retrieval_dataset.json"
RESULTS_DIR = Path(__file__).parent / "results"


@dataclass
class WebRetrievalResult:
    test_id: str
    description: str
    base_result: TestResult
    # Web-specific metrics
    called_lookup_docs: bool
    called_web_search: bool
    escalation_correct: bool  # True if agent tried local first, then web
    web_content_grounded: bool  # True if response contains web-specific indicators
    retrieval_path: List[str]  # Ordered list of retrieval tools called


def _analyze_retrieval_path(trace: AgentTrace) -> tuple[bool, bool, bool, List[str]]:
    """
    Analyze the tool call sequence to determine retrieval behavior.
    Returns: (called_lookup_docs, called_web_search, escalation_correct, path)
    """
    retrieval_tools_order: List[str] = []
    called_lookup = False
    called_web = False

    for entry in trace.tool_call_history:
        if entry.get("type") != "tool":
            continue
        tool = entry.get("tool", "")
        if tool == "lookup_slurm_docs":
            called_lookup = True
            retrieval_tools_order.append("lookup_slurm_docs")
        elif tool == "web_search":
            called_web = True
            retrieval_tools_order.append("web_search")
        elif tool == "fetch_web_content":
            retrieval_tools_order.append("fetch_web_content")

    # Escalation is correct if: local was tried BEFORE web (or web-only for pure web topics)
    escalation_correct = False
    if called_lookup and called_web:
        # Ideal path: local first, then web
        first_local = next((i for i, t in enumerate(retrieval_tools_order) if t == "lookup_slurm_docs"), None)
        first_web = next((i for i, t in enumerate(retrieval_tools_order) if t == "web_search"), None)
        escalation_correct = first_local is not None and first_web is not None and first_local < first_web
    elif called_web and not called_lookup:
        # Some topics are clearly not in local docs (e.g., product comparisons)
        # Directly going to web is acceptable for those
        escalation_correct = True
    elif called_lookup and not called_web:
        # Agent stayed local — might be OK if it found enough, but for these
        # test cases we expect web escalation, so this is incorrect
        escalation_correct = False

    return called_lookup, called_web, escalation_correct, retrieval_tools_order


def _check_web_grounding(trace: AgentTrace) -> bool:
    """
    Check if the response shows signs of being grounded in web content
    (URLs, specific product names, version numbers, code snippets).
    """
    response = (trace.response or "").lower()
    indicators = [
        "http", "url:", "source:", "according to",
        "documentation", "github", "stackoverflow",
        "```", "example:", "install",
    ]
    # Also check tool outputs for web content markers
    for entry in trace.tool_call_history:
        output = (entry.get("output") or "").lower()
        if "[web_search]" in output or "[web_fetch]" in output:
            return True

    return sum(1 for ind in indicators if ind in response) >= 2


async def run_web_eval(args):
    dataset_path = Path(args.dataset) if args.dataset else DATASET_PATH
    if not dataset_path.exists():
        print(f"Web retrieval dataset not found: {dataset_path}")
        sys.exit(1)

    dataset = json.loads(dataset_path.read_text())
    if args.test_id:
        dataset = [t for t in dataset if t["id"] == args.test_id]

    if not dataset:
        print("No test cases match the filters.")
        sys.exit(1)

    main_provider = _normalize_eval_provider(args.main_provider or args.llm_provider, CHAT_LLM_PROVIDER)
    specialist_provider = _normalize_eval_provider(args.specialist_provider or main_provider, main_provider)
    judge_provider = _judge_provider_for(args.judge_model, args.judge_provider)

    print(f"\nWeb-Grounded Retrieval Evaluation")
    print(f"  Agent URL    : {args.agent_url}")
    print(f"  Test cases   : {len(dataset)}")
    print(f"  Auto-approve : {args.auto_approve}")
    print(f"  Main LLM     : {main_provider} / {args.main_model}")
    print(f"  LLM Judge    : {'ON (' + judge_provider + ' / ' + args.judge_model + ')' if args.judge else 'OFF'}")

    # Health check
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{args.agent_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as r:
                assert r.status == 200
        print(f"  Agent        : ONLINE ✓")
    except Exception:
        print(f"\n  Cannot reach agent at {args.agent_url}")
        sys.exit(1)

    results: List[WebRetrievalResult] = []

    for i, test in enumerate(dataset, 1):
        tid = test["id"][:45]
        print(f"  [{i:02d}/{len(dataset):02d}] {tid:<47} ", end="", flush=True)

        await reset_mock_state_for_test(test, args.mcp_url)

        session_id = f"web_eval_{test['id']}_{int(time.time())}"
        try:
            trace = await run_agent(
                test["input"], session_id, args.agent_url, args.auto_approve,
                mcp_url=args.mcp_url,
                llm_provider=args.llm_provider,
                main_provider=main_provider,
                specialist_provider=specialist_provider,
                main_model=args.main_model,
                specialist_model=args.specialist_model,
                openai_parallel=args.openai_parallel,
            )
        except Exception as e:
            trace = AgentTrace([], False, False, "", 0.0, str(e))
        finally:
            await clear_agent_session(args.agent_url, session_id)

        base_result = await score_test(
            test, trace,
            use_judge=args.judge,
            judge_model=args.judge_model,
            judge_provider=judge_provider,
        )

        called_lookup, called_web, escalation_correct, path = _analyze_retrieval_path(trace)
        web_grounded = _check_web_grounding(trace)

        wr = WebRetrievalResult(
            test_id=test["id"],
            description=test.get("description", ""),
            base_result=base_result,
            called_lookup_docs=called_lookup,
            called_web_search=called_web,
            escalation_correct=escalation_correct,
            web_content_grounded=web_grounded,
            retrieval_path=path,
        )
        results.append(wr)

        # Status line
        esc_flag = "↑" if escalation_correct else "—"
        web_flag = "W" if called_web else "L"
        status = "✓" if base_result.passed else "✗"
        print(f"[{_pct(base_result.overall)} {status}] [{web_flag}{esc_flag}] ({base_result.latency_s:.1f}s)")

        if args.delay > 0:
            await asyncio.sleep(args.delay)

    # Report
    print_web_report(results)
    save_web_results(results)


def print_web_report(results: List[WebRetrievalResult]):
    n = len(results)
    if not n:
        return

    passed = sum(1 for r in results if r.base_result.passed)
    web_called = sum(1 for r in results if r.called_web_search)
    escalation_ok = sum(1 for r in results if r.escalation_correct)
    grounded = sum(1 for r in results if r.web_content_grounded)
    local_called = sum(1 for r in results if r.called_lookup_docs)

    print(f"\n{'='*60}")
    print(f"  Web-Grounded Retrieval Results")
    print(f"{'='*60}")
    print(f"  Total cases          : {n}")
    print(f"  Base pass rate       : {passed}/{n} ({passed/n*100:.1f}%)")
    print(f"  Web search called    : {web_called}/{n} ({web_called/n*100:.1f}%)")
    print(f"  Local lookup called  : {local_called}/{n} ({local_called/n*100:.1f}%)")
    print(f"  Escalation correct   : {escalation_ok}/{n} ({escalation_ok/n*100:.1f}%)")
    print(f"  Web-content grounded : {grounded}/{n} ({grounded/n*100:.1f}%)")
    print(f"{'='*60}")

    print(f"\n  Per-case breakdown:")
    for r in results:
        status = "✓" if r.base_result.passed else "✗"
        esc = "✓" if r.escalation_correct else "✗"
        path_str = " → ".join(r.retrieval_path) if r.retrieval_path else "(none)"
        print(f"    [{status}] {r.test_id[:40]:<42} esc={esc} path=[{path_str}]")


def save_web_results(results: List[WebRetrievalResult]):
    RESULTS_DIR.mkdir(exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = RESULTS_DIR / f"web_retrieval_{ts}.json"

    n = len(results)
    output = {
        "timestamp": ts,
        "total_cases": n,
        "pass_rate": sum(1 for r in results if r.base_result.passed) / n if n else 0,
        "web_search_rate": sum(1 for r in results if r.called_web_search) / n if n else 0,
        "escalation_correct_rate": sum(1 for r in results if r.escalation_correct) / n if n else 0,
        "web_grounded_rate": sum(1 for r in results if r.web_content_grounded) / n if n else 0,
        "results": [
            {
                "test_id": r.test_id,
                "description": r.description,
                "passed": r.base_result.passed,
                "overall": r.base_result.overall,
                "called_lookup_docs": r.called_lookup_docs,
                "called_web_search": r.called_web_search,
                "escalation_correct": r.escalation_correct,
                "web_content_grounded": r.web_content_grounded,
                "retrieval_path": r.retrieval_path,
                "agent_response": r.base_result.agent_response[:500],
                "latency_s": r.base_result.latency_s,
            }
            for r in results
        ],
    }

    path.write_text(json.dumps(output, indent=2))
    print(f"\n  Results saved: {path}")


def main():
    p = argparse.ArgumentParser(description="Web-Grounded Retrieval Evaluation")
    p.add_argument("--dataset", default="", help="Path to web retrieval dataset JSON")
    p.add_argument("--test-id", default="", help="Run a single test by ID")
    p.add_argument("--agent-url", default=AGENT_URL)
    p.add_argument("--mcp-url", default=MCP_URL)
    p.add_argument("--llm-provider", default=CHAT_LLM_PROVIDER)
    p.add_argument("--main-provider", default="")
    p.add_argument("--specialist-provider", default="")
    p.add_argument("--main-model", default=MAIN_MODEL)
    p.add_argument("--specialist-model", default=SPECIALIST_MODEL)
    p.add_argument("--auto-approve", action="store_true")
    p.add_argument("--judge", action="store_true")
    p.add_argument("--judge-model", default=JUDGE_MODEL)
    p.add_argument("--judge-provider", default=JUDGE_PROVIDER)
    p.add_argument("--openai-parallel", action="store_true")
    p.add_argument("--delay", type=float, default=2.0)
    args = p.parse_args()
    asyncio.run(run_web_eval(args))


if __name__ == "__main__":
    main()
