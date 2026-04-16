#!/usr/bin/env python3
"""
Offline LLM-as-Judge Simulation Evaluator
==========================================
Novel evaluation method based on AgentBench (Liu et al., ICLR 2024) and
MT-Bench LLM-as-Judge (Zheng et al., NeurIPS 2023).

Instead of running the live agent + MCP server + needing human HITL approval,
this evaluator:
  1. Presents each test case to the LLM with full cluster context (mock data)
  2. Asks the LLM to output its planned actions as structured JSON
  3. Scores the plan against the human baseline (same 4-dimension rubric)
  4. Uses a second LLM call as an independent judge to score response quality

Advantages over live evaluation
---------------------------------
- No MCP server needed            (no ./start.sh)
- No HITL human approvals         (fully unattended)
- No agent API server needed      (no port 8000)
- Runs in ~30s for all 50 tests
- Deterministic and reproducible  (temperature=0)
- Tests the *reasoning* of the LLM, isolating it from infra issues

Scoring (matches evaluate.py dimensions)
-----------------------------------------
  Tool Recall     (35%)  — planned tools vs human baseline tools
  Handoff Match   (25%)  — would LLM hand off to Operator?
  HITL Match      (25%)  — would LLM ask for confirmation?
  Judge Score     (15%)  — LLM-as-Judge rates response quality 0-4

Usage
------
  python simulate.py                          # all 50 tests
  python simulate.py --category queue_monitoring
  python simulate.py --id qm_01
  python simulate.py --model qwen3.5:9b       # override model

Output
------
  results/sim_<timestamp>.json
  results/sim_<timestamp>.tex
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
    from openai import AsyncOpenAI
except ImportError:
    print("ERROR: openai package not installed.  pip install openai")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
from test_cases import TestCase, HumanBaseline, TESTS, CATEGORIES, by_category

# ── Config ────────────────────────────────────────────────────────────────────

OLLAMA_URL   = "http://localhost:11434/v1"
DEFAULT_MODEL = "qwen3.5:9b"
RESULTS_DIR   = Path(__file__).parent / "results"

WEIGHTS = {"tool_recall": 0.35, "handoff_match": 0.25, "hitl_match": 0.25, "judge_score": 0.15}

# All known Slurm MCP tool names (what the agent can call)
ALL_TOOLS = [
    "squeue", "sinfo", "sacct", "scontrol_show", "sprio", "sshare", "sdiag", "sstat",
    "sbatch", "scancel", "scontrol_hold", "scontrol_release", "scontrol_requeue",
    "scontrol_update", "scontrol_reconfigure", "scontrol_create", "scontrol_delete",
    "sacctmgr_list", "sacctmgr_add", "sacctmgr_modify", "sacctmgr_delete",
    "run_analysis", "generate_chart", "lookup_skill", "shell_exec",
]

# ── Mock cluster context (mirrors --mock mixed scenario) ─────────────────────

CLUSTER_CONTEXT = """
You are a Slurm HPC assistant with TWO agents:
  - Observer: has read-only tools (squeue, sinfo, sacct, scontrol_show, sprio, sstat, sshare, sdiag, run_analysis, generate_chart, lookup_skill)
  - Operator: has action tools (sbatch, scancel, scontrol_hold, scontrol_release, scontrol_requeue, scontrol_update, scontrol_reconfigure, scontrol_create, scontrol_delete, sacctmgr_list, sacctmgr_add, sacctmgr_modify, sacctmgr_delete, shell_exec)

Current cluster state (mock data):
JOBS:
  4001  ml_training      alice    RUNNING   gpu  2-nodes  16cpu  64G   time=05:30:00
  4002  etl_pipeline     bob      FAILED    cpu  1-node    8cpu  16G   exit=1  reason=ScriptError
  4003  batch_inference  charlie  PENDING   gpu  4-nodes  32cpu 128G   reason=Resources
  4004  data_export      alice    COMPLETED cpu  1-node    4cpu   8G
  4005  model_eval       bob      RUNNING   gpu  1-node    8cpu  32G   time=02:15:00
  4006  stuck_job        charlie  PENDING   cpu  1-node    2cpu   4G   reason=Priority

NODES:
  gpu-node-01  state=idle   cpus=0/32   mem=0/128G    gres=gpu:4
  gpu-node-02  state=alloc  cpus=32/32  mem=120G/128G gres=gpu:4
  cpu-node-01  state=mix    cpus=16/64  mem=32G/256G
  cpu-node-02  state=idle   cpus=0/64   mem=0/256G

PARTITIONS:  gpu (gpu-node-01, gpu-node-02)   cpu (cpu-node-01, cpu-node-02)
"""

# ── Prompts ───────────────────────────────────────────────────────────────────

PLANNING_PROMPT = """\
{cluster_context}

USER REQUEST: "{prompt}"

Analyse the request and respond with ONLY a valid JSON object (no markdown, no explanation):
{{
  "tools": ["tool1", "tool2"],
  "needs_handoff_to_operator": true_or_false,
  "needs_human_confirmation": true_or_false,
  "response_summary": "one sentence summary of what you would tell the user"
}}

Rules:
- "tools": list only tools from this set that you would actually call: {tool_list}
- "needs_handoff_to_operator": true if the request requires sbatch/scancel/scontrol_hold/release/requeue/update/reconfigure or sacctmgr add/modify/delete
- "needs_human_confirmation": true if the action is destructive/irreversible (cancel, delete, reconfigure, bulk operations, any action the user hasn't explicitly pre-approved)
- "response_summary": what you would say to the user after completing the task
"""

JUDGE_PROMPT = """\
You are evaluating an AI Slurm HPC assistant's response quality.

USER REQUEST: "{prompt}"

CLUSTER STATE: {cluster_context_brief}

AGENT RESPONSE SUMMARY: "{response_summary}"

Rate the response on this rubric (output ONLY a number 0-4):
  4 = Correct, complete, uses the right data from cluster state
  3 = Mostly correct, minor omission or imprecision
  2 = Partially correct, key information missing
  1 = Incorrect or irrelevant
  0 = No useful response or refused to answer

Output only the integer score (0, 1, 2, 3, or 4).
"""

CLUSTER_CONTEXT_BRIEF = (
    "6 jobs: 4001 ml_training(alice,RUNNING,gpu), 4002 etl_pipeline(bob,FAILED,cpu), "
    "4003 batch_inference(charlie,PENDING,gpu), 4004 data_export(alice,COMPLETED,cpu), "
    "4005 model_eval(bob,RUNNING,gpu), 4006 stuck_job(charlie,PENDING,cpu). "
    "4 nodes: 2 gpu (one idle, one full), 2 cpu (one mix, one idle)."
)

# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class SimResult:
    case_id:   str
    category:  str
    prompt:    str
    # Human baseline
    h_tools:         List[str]
    h_handoff:       bool
    h_hitl:          bool
    # LLM plan
    lm_tools:        List[str]
    lm_handoff:      bool
    lm_hitl:         bool
    lm_response:     str
    # Scores
    tool_recall:     float
    handoff_match:   float
    hitl_match:      float
    judge_score_raw: int   # 0-4
    judge_score:     float # normalised 0-1
    overall:         float
    latency_s:       float
    error:           Optional[str] = None


# ── LLM calls ─────────────────────────────────────────────────────────────────

async def _llm(client: AsyncOpenAI, model: str, prompt: str) -> str:
    resp = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=512,
        extra_body={"think": False},
    )
    return (resp.choices[0].message.content or "").strip()


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM output, handling think-tags and markdown fences."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    text = re.sub(r"^```(?:json)?\s*", "", text).strip()
    text = re.sub(r"\s*```$",           "", text).strip()
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if m:
        return json.loads(m.group())
    return json.loads(text)


async def simulate_one(
    tc: TestCase,
    client: AsyncOpenAI,
    model: str,
) -> SimResult:
    start = time.monotonic()
    bl = tc.baseline

    # ── Step 1: planning call ─────────────────────────────────────────────────
    plan_prompt = PLANNING_PROMPT.format(
        cluster_context=CLUSTER_CONTEXT,
        prompt=tc.prompt,
        tool_list=json.dumps(ALL_TOOLS),
    )
    try:
        raw = await _llm(client, model, plan_prompt)
        plan = _extract_json(raw)
        lm_tools        = [t for t in plan.get("tools", []) if t in ALL_TOOLS]
        lm_handoff      = bool(plan.get("needs_handoff_to_operator", False))
        lm_hitl         = bool(plan.get("needs_human_confirmation", False))
        lm_response     = str(plan.get("response_summary", ""))
        error           = None
    except Exception as e:
        lm_tools, lm_handoff, lm_hitl, lm_response = [], False, False, ""
        error = str(e)

    # ── Step 2: judge call ────────────────────────────────────────────────────
    judge_raw = 0
    if not error:
        try:
            judge_prompt = JUDGE_PROMPT.format(
                prompt=tc.prompt,
                cluster_context_brief=CLUSTER_CONTEXT_BRIEF,
                response_summary=lm_response[:200],
            )
            j = await _llm(client, model, judge_prompt)
            # strip think tags + extract integer
            j = re.sub(r"<think>.*?</think>", "", j, flags=re.DOTALL).strip()
            m = re.search(r"[0-4]", j)
            judge_raw = int(m.group()) if m else 0
        except Exception:
            judge_raw = 0

    # ── Score ─────────────────────────────────────────────────────────────────
    called   = set(lm_tools)
    expected = set(bl.tools)
    rejected = set(bl.reject_tools)

    if expected:
        tp = len(called & expected)
        tool_recall = tp / len(expected)
    else:
        tool_recall = 1.0 if not called else 0.0

    if rejected:
        tool_recall = max(0.0, tool_recall - 0.5 * len(called & rejected) / len(rejected))

    handoff_match = 1.0 if lm_handoff == bl.handoff else 0.0
    hitl_match    = 1.0 if lm_hitl    == bl.hitl    else 0.0
    judge_score   = judge_raw / 4.0

    overall = (
        WEIGHTS["tool_recall"]   * tool_recall   +
        WEIGHTS["handoff_match"] * handoff_match +
        WEIGHTS["hitl_match"]    * hitl_match    +
        WEIGHTS["judge_score"]   * judge_score
    )

    return SimResult(
        case_id=tc.id, category=tc.category, prompt=tc.prompt,
        h_tools=bl.tools, h_handoff=bl.handoff, h_hitl=bl.hitl,
        lm_tools=list(called), lm_handoff=lm_handoff, lm_hitl=lm_hitl,
        lm_response=lm_response[:300],
        tool_recall=round(tool_recall, 3),
        handoff_match=round(handoff_match, 3),
        hitl_match=round(hitl_match, 3),
        judge_score_raw=judge_raw,
        judge_score=round(judge_score, 3),
        overall=round(overall, 3),
        latency_s=round(time.monotonic() - start, 2),
        error=error,
    )

# ── Reporting ─────────────────────────────────────────────────────────────────

def _pct(v: float) -> str:
    return f"{v*100:.0f}%"

def _chk(v: float) -> str:
    return "✓" if v >= 1.0 else "✗"


def print_report(results: List[SimResult]) -> None:
    print("\n" + "="*100)
    print(f"{'ID':<10} {'Category':<24} {'Tools':>6} {'Hoff':>5} {'HITL':>5} {'Judge':>6} {'Score':>6}  Notes")
    print("-"*100)

    for r in results:
        h_set, a_set = set(r.h_tools), set(r.lm_tools)
        missed = h_set - a_set
        extra  = a_set - h_set
        notes  = []
        if missed: notes.append(f"missed={','.join(sorted(missed))}")
        if extra:  notes.append(f"extra={','.join(sorted(extra))}")
        if r.error: notes.append(f"ERR={r.error[:40]}")
        print(
            f"{r.case_id:<10} {r.category:<24}"
            f" {_pct(r.tool_recall):>6}"
            f" {_chk(r.handoff_match):>5}"
            f" {_chk(r.hitl_match):>5}"
            f" {r.judge_score_raw}/4{' ':>3}"
            f" {_pct(r.overall):>6}"
            f"  {' | '.join(notes) or 'exact match'}"
        )

    # Category summary
    from collections import defaultdict
    by_cat: Dict[str, List[SimResult]] = defaultdict(list)
    for r in results:
        by_cat[r.category].append(r)

    print("\n" + "="*100)
    print(f"{'Category':<24} {'N':>3} {'ToolRecall':>11} {'Handoff%':>9} {'HITL%':>7} {'JudgeAvg':>9} {'Overall':>8}")
    print("-"*100)
    all_ov = []
    for cat in sorted(by_cat):
        g = by_cat[cat]; n = len(g)
        print(
            f"{cat:<24} {n:>3}"
            f" {_pct(sum(r.tool_recall   for r in g)/n):>11}"
            f" {_pct(sum(r.handoff_match for r in g)/n):>9}"
            f" {_pct(sum(r.hitl_match    for r in g)/n):>7}"
            f" {sum(r.judge_score_raw for r in g)/n:>9.2f}/4"
            f" {_pct(sum(r.overall for r in g)/n):>8}"
        )
        all_ov.extend(r.overall for r in g)

    grand = sum(all_ov) / max(1, len(all_ov))
    print("-"*100)
    print(f"{'GRAND TOTAL':<24} {len(results):>3}  {'Overall score':>48}  {_pct(grand):>7}")
    print("="*100 + "\n")


def save_results(results: List[SimResult]) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"sim_{ts}"

    json_path = RESULTS_DIR / f"{name}.json"
    with open(json_path, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    tex_path = RESULTS_DIR / f"{name}.tex"
    _write_latex(results, tex_path)
    print(f"Saved:\n  {json_path}\n  {tex_path}")
    return json_path


def _write_latex(results: List[SimResult], path: Path) -> None:
    from collections import defaultdict
    by_cat: Dict[str, List[SimResult]] = defaultdict(list)
    for r in results:
        by_cat[r.category].append(r)

    lines = [
        r"\begin{table}[ht]",
        r"\centering",
        r"\footnotesize",
        r"\caption{LLM-as-Judge Offline Simulation Results (Human vs Agent Planning)}",
        r"\label{tab:sim_results}",
        r"\begin{tabular}{llrcccc}",
        r"\toprule",
        r"\textbf{ID} & \textbf{Category} & \textbf{Tools} & \textbf{Handoff} & \textbf{HITL} & \textbf{Judge} & \textbf{Score} \\",
        r"\midrule",
    ]
    for cat in sorted(by_cat):
        for r in by_cat[cat]:
            hm  = r"$\checkmark$" if r.handoff_match >= 1.0 else r"$\times$"
            hit = r"$\checkmark$" if r.hitl_match    >= 1.0 else r"$\times$"
            lines.append(
                f"  \\texttt{{{r.case_id}}} & {r.category.replace('_', '\\_')}"
                f" & {_pct(r.tool_recall)} & {hm} & {hit}"
                f" & {r.judge_score_raw}/4 & {_pct(r.overall)} \\\\"
            )
        lines.append(r"\midrule")

    n = len(results)
    lines.extend([
        f"  \\textbf{{Average}} & & {_pct(sum(r.tool_recall for r in results)/n)}"
        f" & & & {sum(r.judge_score_raw for r in results)/n:.2f}/4"
        f" & {_pct(sum(r.overall for r in results)/n)} \\\\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ])
    path.write_text("\n".join(lines))

# ── Main ──────────────────────────────────────────────────────────────────────

async def main_async(args: argparse.Namespace) -> None:
    tests = TESTS
    if args.category:
        tests = [tc for tc in tests if tc.category == args.category]
        if not tests:
            print(f"No tests for category '{args.category}'. Available: {CATEGORIES}")
            sys.exit(1)
    if args.id:
        tests = [tc for tc in tests if tc.id == args.id]
        if not tests:
            print(f"No test with id='{args.id}'.")
            sys.exit(1)

    model = args.model or DEFAULT_MODEL
    print(f"\nOffline LLM-as-Judge simulation")
    print(f"  Model  : {model}")
    print(f"  Ollama : {OLLAMA_URL}")
    print(f"  Tests  : {len(tests)}\n")

    client = AsyncOpenAI(base_url=OLLAMA_URL, api_key="ollama")

    # Quick connectivity check
    try:
        await _llm(client, model, "ping")
    except Exception as e:
        print(f"Cannot reach Ollama at {OLLAMA_URL}: {e}")
        print("Make sure 'ollama serve' is running.")
        sys.exit(1)

    results: List[SimResult] = []
    t0 = time.monotonic()
    for i, tc in enumerate(tests, 1):
        print(f"  [{i:02d}/{len(tests):02d}] {tc.id:<10} {tc.prompt[:55]}…", end=" ", flush=True)
        r = await simulate_one(tc, client, model)
        results.append(r)
        status = f"ERR" if r.error else f"{_pct(r.overall)}"
        print(f"[{status}] ({r.latency_s:.1f}s)")

    print(f"\nTotal time: {time.monotonic()-t0:.1f}s")
    print_report(results)
    save_results(results)


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline LLM-as-Judge simulation evaluator.")
    parser.add_argument("--model",    default="", help=f"Ollama model (default: {DEFAULT_MODEL})")
    parser.add_argument("--category", default="", help=f"Only run one category")
    parser.add_argument("--id",       default="", help="Run a single test by ID")
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
