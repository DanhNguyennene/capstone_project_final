#!/usr/bin/env python3
"""Debug a single eval case to see per-dimension scores.

Usage:
    python evaluation/debug_single_eval.py
    python evaluation/debug_single_eval.py --case-idx 5
"""
import asyncio
import json
import sys
import argparse

sys.path.insert(0, "evaluation")
from scenario_eval import score_test, run_agent, reset_mock_state_for_test


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case-idx", type=int, default=0)
    p.add_argument("--mcp-url", default="http://localhost:3002")
    p.add_argument("--model-url", default="http://localhost:8000")
    p.add_argument("--model", default="slurm-agent")
    args = p.parse_args()

    with open("evaluation/dataset.json") as f:
        dataset = json.load(f)
    test = dataset[args.case_idx]

    print(f"Test: {test['id']} (idx={args.case_idx})")
    print(f"Input: {test['input'][:150]}")
    print(f"Expected tools: {test['ground_truth']['tools']}")
    print(f"Expected handoff: {test['ground_truth'].get('handoff')}")
    print(f"Expected hitl: {test['ground_truth'].get('hitl')}")
    print(f"Expected keywords: {test['ground_truth'].get('keywords', [])[:5]}")
    print("---")

    reset_ok, _ = await reset_mock_state_for_test(test, args.mcp_url)
    print(f"MCP reset: {reset_ok}")

    session_id = f"debug_{args.case_idx}"
    trace = await run_agent(
        test["input"],
        session_id,
        args.model_url,
        False,
        mcp_url=args.mcp_url,
        llm_provider="openai",
        main_provider="openai",
        specialist_provider="openai",
        main_model=args.model,
        specialist_model=args.model,
    )

    print(f"\nAgent tools called: {trace.tools_called}")
    print(f"Agent handoff: {trace.handoff_triggered}")
    print(f"Agent hitl: {trace.hitl_triggered}")
    print(f"Agent error: {trace.error}")
    print(f"Agent response (first 300): {trace.final_response[:300] if trace.final_response else 'NONE'}")
    print("---")

    result = await score_test(test, trace, use_judge=False)

    print(f"\nSCORES:")
    print(f"  tool_recall:    {result.tool_recall:.2f}")
    print(f"  routing_match:  {result.routing_match:.2f}")
    print(f"  hitl_match:     {result.hitl_match:.2f}")
    print(f"  keyword_score:  {result.keyword_score:.2f}")
    print(f"  state_match:    {result.state_match:.2f}")
    print(f"  overall:        {result.overall:.2f}")
    print(f"  passed:         {result.passed}")


asyncio.run(main())
