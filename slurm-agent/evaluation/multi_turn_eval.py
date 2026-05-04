#!/usr/bin/env python3
"""
Multi-Turn Behavioral Evaluation
==================================
Evaluates the agent across ordered conversation turns within a single session.
Each test case defines a sequence of user messages; the agent must maintain
context, resolve coreferences, and stay consistent across turns.

Reuses run_agent / score_test from scenario_eval.py but preserves session state
between turns (no clear_agent_session until after the final turn).

Dataset format (multi_turn_dataset.json):
[
  {
    "id": "mt_...",
    "category": "multi_turn",
    "description": "...",
    "scenario": "healthy",
    "source_state": {...},
    "target_state": {...},
    "turns": [
      {
        "input": "...",
        "ground_truth": {
          "tools": [...],
          "handoff": false,
          "hitl": false,
          "keywords": [...]
        }
      },
      ...
    ]
  }
]

Metrics:
  Turn-level pass rate     — per-turn scoring (same dimensions as single-turn)
  Conversation pass rate   — entire conversation passes iff ALL turns pass
  Context retention score  — do later turns correctly resolve prior context?

Usage:
  python multi_turn_eval.py --auto-approve --judge --judge-model gpt-oss:20b --llm-provider openai
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
    compute_metrics, save_results, AgentTrace, TestResult,
    AGENT_URL, MCP_URL, JUDGE_MODEL, JUDGE_PROVIDER, PASS_THRESHOLD,
    CHAT_LLM_PROVIDER, MAIN_MODEL, SPECIALIST_MODEL,
    _normalize_eval_provider, _judge_provider_for, _pct,
)
import scenario_eval as _seval

DATASET_PATH = Path(__file__).parent / "multi_turn_dataset.json"
RESULTS_DIR = Path(__file__).parent / "results"


@dataclass
class TurnResult:
    turn_index: int
    input: str
    test_result: TestResult
    context_retention: float  # 1.0 if coreference/context was handled correctly


@dataclass
class ConversationResult:
    test_id: str
    description: str
    scenario: str
    turns: List[TurnResult]
    all_turns_passed: bool
    avg_overall: float
    avg_context_retention: float
    total_latency_s: float


def _check_context_retention(turn_idx: int, turn: dict, trace: AgentTrace) -> float:
    """
    Evaluate whether the agent correctly maintained context from prior turns.
    For the first turn, context retention is trivially 1.0.
    For subsequent turns, check if context_markers (pronouns, references to
    prior entities) were resolved correctly based on keyword evidence.
    """
    if turn_idx == 0:
        return 1.0

    context_markers = turn.get("context_markers", [])
    if not context_markers:
        return 1.0

    # Check if the agent's response demonstrates awareness of context
    evidence = (trace.response or "").lower()
    # Also include tool call history (args/outputs often contain resolved refs)
    for entry in trace.tool_call_history:
        evidence += " " + (entry.get("cmd", "") + " " + entry.get("output", "")).lower()

    hits = sum(1 for marker in context_markers if marker.lower() in evidence)
    return hits / len(context_markers) if context_markers else 1.0


async def run_conversation(
    test: dict,
    agent_url: str,
    mcp_url: str,
    auto_approve: bool,
    use_judge: bool,
    judge_model: str,
    judge_provider: str,
    llm_provider: str,
    main_provider: str,
    specialist_provider: str,
    main_model: str,
    specialist_model: str,
    openai_parallel: bool,
) -> ConversationResult:
    """Run all turns of a multi-turn conversation in a single session."""
    session_id = f"mt_eval_{test['id']}_{int(time.time())}"
    turn_results: List[TurnResult] = []
    total_latency = 0.0

    # Reset mock state once at the start of the conversation
    await reset_mock_state_for_test(test, mcp_url)

    try:
        for turn_idx, turn in enumerate(test["turns"]):
            # Build a synthetic single-turn test dict for score_test
            single_test = {
                "id": f"{test['id']}_turn{turn_idx}",
                "category": "multi_turn",
                "scenario": test["scenario"],
                "input": turn["input"],
                "source_state": test["source_state"],
                "target_state": test.get("target_state", test["source_state"]),
                "ground_truth": turn["ground_truth"],
            }

            trace = await run_agent(
                turn["input"],
                session_id,
                agent_url,
                auto_approve,
                mcp_url=mcp_url,
                llm_provider=llm_provider,
                main_provider=main_provider,
                specialist_provider=specialist_provider,
                main_model=main_model,
                specialist_model=specialist_model,
                openai_parallel=openai_parallel,
            )

            result = await score_test(
                single_test,
                trace,
                use_judge=use_judge,
                judge_model=judge_model,
                judge_provider=judge_provider,
            )

            context_score = _check_context_retention(turn_idx, turn, trace)
            total_latency += trace.latency_s

            turn_results.append(TurnResult(
                turn_index=turn_idx,
                input=turn["input"],
                test_result=result,
                context_retention=round(context_score, 3),
            ))
    finally:
        await clear_agent_session(agent_url, session_id)

    all_passed = all(tr.test_result.passed for tr in turn_results)
    avg_overall = sum(tr.test_result.overall for tr in turn_results) / len(turn_results) if turn_results else 0.0
    avg_ctx = sum(tr.context_retention for tr in turn_results) / len(turn_results) if turn_results else 0.0

    return ConversationResult(
        test_id=test["id"],
        description=test.get("description", ""),
        scenario=test["scenario"],
        turns=turn_results,
        all_turns_passed=all_passed,
        avg_overall=round(avg_overall, 3),
        avg_context_retention=round(avg_ctx, 3),
        total_latency_s=round(total_latency, 2),
    )


def print_report(results: List[ConversationResult]):
    """Print a summary report."""
    n = len(results)
    conv_pass = sum(1 for r in results if r.all_turns_passed)
    total_turns = sum(len(r.turns) for r in results)
    turn_pass = sum(1 for r in results for t in r.turns if t.test_result.passed)
    avg_ctx = sum(r.avg_context_retention for r in results) / n if n else 0

    print(f"\n{'='*60}")
    print(f"  Multi-Turn Behavioral Evaluation Results")
    print(f"{'='*60}")
    print(f"  Conversations       : {n}")
    print(f"  Total turns         : {total_turns}")
    print(f"  Conversation pass   : {conv_pass}/{n} ({conv_pass/n*100:.1f}%)")
    print(f"  Turn-level pass     : {turn_pass}/{total_turns} ({turn_pass/total_turns*100:.1f}%)")
    print(f"  Avg context retain  : {avg_ctx:.3f}")
    print(f"{'='*60}")

    for r in results:
        status = "✓" if r.all_turns_passed else "✗"
        print(f"\n  [{status}] {r.test_id} — {r.description}")
        print(f"      Overall: {r.avg_overall:.3f} | Context: {r.avg_context_retention:.3f} | Latency: {r.total_latency_s:.1f}s")
        for t in r.turns:
            ts = "✓" if t.test_result.passed else "✗"
            ctx_flag = "" if t.context_retention >= 0.99 else f" [ctx:{t.context_retention:.2f}]"
            print(f"      Turn {t.turn_index}: [{_pct(t.test_result.overall)} {ts}]{ctx_flag} — {t.input[:60]}")


def save_multi_turn_results(results: List[ConversationResult]):
    """Save results to JSON."""
    RESULTS_DIR.mkdir(exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = RESULTS_DIR / f"multi_turn_{ts}.json"

    output = {
        "timestamp": ts,
        "conversations": len(results),
        "total_turns": sum(len(r.turns) for r in results),
        "conversation_pass_rate": sum(1 for r in results if r.all_turns_passed) / len(results) if results else 0,
        "turn_pass_rate": (
            sum(1 for r in results for t in r.turns if t.test_result.passed)
            / sum(len(r.turns) for r in results)
        ) if results else 0,
        "avg_context_retention": sum(r.avg_context_retention for r in results) / len(results) if results else 0,
        "results": [
            {
                "test_id": r.test_id,
                "description": r.description,
                "scenario": r.scenario,
                "all_turns_passed": r.all_turns_passed,
                "avg_overall": r.avg_overall,
                "avg_context_retention": r.avg_context_retention,
                "total_latency_s": r.total_latency_s,
                "turns": [
                    {
                        "turn_index": t.turn_index,
                        "input": t.input,
                        "context_retention": t.context_retention,
                        "passed": t.test_result.passed,
                        "overall": t.test_result.overall,
                        "tool_recall": t.test_result.tool_recall,
                        "routing_match": t.test_result.routing_match,
                        "hitl_match": t.test_result.hitl_match,
                        "keyword_score": t.test_result.keyword_score,
                        "agent_tools": t.test_result.agent_tools,
                        "agent_response": t.test_result.agent_response[:500],
                        "latency_s": t.test_result.latency_s,
                    }
                    for t in r.turns
                ],
            }
            for r in results
        ],
    }

    path.write_text(json.dumps(output, indent=2))
    print(f"\n  Results saved: {path}")


async def run_eval(args):
    dataset_path = Path(args.dataset) if args.dataset else DATASET_PATH
    if not dataset_path.exists():
        print(f"Multi-turn dataset not found: {dataset_path}")
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

    print(f"\nMulti-Turn Behavioral Evaluation")
    print(f"  Agent URL    : {args.agent_url}")
    print(f"  Conversations: {len(dataset)}")
    print(f"  Total turns  : {sum(len(t['turns']) for t in dataset)}")
    print(f"  Auto-approve : {args.auto_approve}")
    print(f"  Main LLM     : {main_provider} / {args.main_model}")
    print(f"  Specialist   : {specialist_provider} / {args.specialist_model}")
    judge_workers = getattr(args, 'judge_workers', 0) or 0
    print(f"  LLM Judge    : {'ON (' + judge_provider + ' / ' + args.judge_model + ')' if args.judge else 'OFF'}")
    print(f"  Workers      : {getattr(args, 'workers', 1)}")
    print(f"  Judge Workers: {judge_workers if judge_workers else 'unlimited (same as workers)'}")

    if judge_workers > 0:
        _seval._judge_semaphore = asyncio.Semaphore(judge_workers)

    # Health check
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{args.agent_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as r:
                assert r.status == 200
        print(f"  Agent        : ONLINE ✓")
    except Exception:
        print(f"\n  Cannot reach agent at {args.agent_url}")
        sys.exit(1)

    workers = getattr(args, "workers", 1) or 1
    results: List[ConversationResult] = [None] * len(dataset)
    sem = asyncio.Semaphore(workers)
    counter = {"done": 0}
    total = len(dataset)

    async def _run_one(i: int, test: dict):
        async with sem:
            conv_result = await run_conversation(
                test,
                agent_url=args.agent_url,
                mcp_url=args.mcp_url,
                auto_approve=args.auto_approve,
                use_judge=args.judge,
                judge_model=args.judge_model,
                judge_provider=judge_provider,
                llm_provider=args.llm_provider,
                main_provider=main_provider,
                specialist_provider=specialist_provider,
                main_model=args.main_model,
                specialist_model=args.specialist_model,
                openai_parallel=args.openai_parallel,
            )
            results[i] = conv_result
            counter["done"] += 1
            status = "✓" if conv_result.all_turns_passed else "✗"
            print(f"  [{counter['done']:03d}/{total:03d}] {test['id']} ({len(test['turns'])} turns)"
                  f"  [{status}] avg={conv_result.avg_overall:.3f} ctx={conv_result.avg_context_retention:.3f} ({conv_result.total_latency_s:.1f}s)")

    tasks = [_run_one(i, test) for i, test in enumerate(dataset)]
    await asyncio.gather(*tasks)

    print_report(results)
    save_multi_turn_results(results)


def main():
    p = argparse.ArgumentParser(description="Multi-Turn Behavioral Evaluation")
    p.add_argument("--dataset", default="", help="Path to multi-turn dataset JSON")
    p.add_argument("--test-id", default="", help="Run a single conversation by ID")
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
    p.add_argument("--workers", type=int, default=4, help="Concurrent conversations")
    p.add_argument("--judge-workers", type=int, default=0, help="Concurrent judge calls (0=same as workers)")
    p.add_argument("--delay", type=float, default=1.0)
    args = p.parse_args()
    asyncio.run(run_eval(args))


if __name__ == "__main__":
    main()
