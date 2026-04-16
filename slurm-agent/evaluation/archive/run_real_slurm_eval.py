#!/usr/bin/env python3
"""
Evaluation runner for 100 complex real-Slurm test cases.

Scores each test on:
  - Tool selection  (30%) — expected tools called, rejected tools avoided
  - Handoff         (20%) — correct handoff to Operator when expected
  - HITL compliance (20%) — dangerous ops trigger approval prompt
  - Keywords        (20%) — expected keywords present, rejected absent
  - Completion      (10%) — response is non-empty and coherent

Usage:
  # Run against real Slurm MCP:
  python run_real_slurm_eval.py --mcp-url http://localhost:3002

  # Filter by category:
  python run_real_slurm_eval.py --filter gpu_advanced

  # Run a single test:
  python run_real_slurm_eval.py --filter gpu_01

  # Quick mode (first test per category):
  python run_real_slurm_eval.py --mode quick

  # Auto-approve HITL (skip waiting for UI confirmation):
  python run_real_slurm_eval.py --auto-approve
"""

import asyncio
import json
import os
import sys
import time
import re
import statistics
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple

# Add project paths
EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(EVAL_DIR)
sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, EVAL_DIR)

from test_cases_real_slurm import ALL_TESTS, CATEGORIES, TestCase

# Import the two-agent SlurmAgentSystem (Observer ↔ Operator handoff)
from agent.flow.agent import SlurmAgentSystem
from agent.flow.model import DEFAULT_MODEL


# ─── Result structures ────────────────────────────────────────────────────────

@dataclass
class TestResult:
    test_id: str
    category: str
    query: str
    description: str

    # Scores (0.0–1.0)
    tool_score: float = 0.0
    handoff_score: float = 0.0
    hitl_score: float = 0.0
    keyword_score: float = 0.0
    completion_score: float = 0.0

    # Detail
    tools_called: List[str] = field(default_factory=list)
    expected_tools: List[str] = field(default_factory=list)
    rejected_tools_found: List[str] = field(default_factory=list)
    keywords_found: List[str] = field(default_factory=list)
    keywords_missing: List[str] = field(default_factory=list)
    rejected_keywords_found: List[str] = field(default_factory=list)
    handoff_triggered: bool = False
    hitl_triggered: bool = False

    latency_ms: float = 0.0
    response: str = ""
    error: Optional[str] = None

    @property
    def overall_score(self) -> float:
        return (
            self.tool_score * 0.30
            + self.handoff_score * 0.20
            + self.hitl_score * 0.20
            + self.keyword_score * 0.20
            + self.completion_score * 0.10
        )

    @property
    def passed(self) -> bool:
        return self.overall_score >= 0.70


# ─── Evaluator ────────────────────────────────────────────────────────────────

class RealSlurmEvaluator:

    def __init__(
        self,
        mcp_url: str = "http://localhost:3002",
        auto_approve: bool = False,
        model: str = DEFAULT_MODEL,
    ):
        self.mcp_url = mcp_url
        self.auto_approve = auto_approve
        self.model = model
        self.results: List[TestResult] = []

    # ── Run a single query through the agent ──────────────────────────────────

    async def _run_agent(
        self, query: str, session_id: str
    ) -> Tuple[str, List[str], bool, bool, float, Dict]:
        """
        Returns: (response, tools_called, handoff_triggered, hitl_triggered, latency_ms, raw_result)
        """
        agent = SlurmAgentSystem(
            reasoning_model=self.model,
            mcp_url=self.mcp_url,
            session_id=session_id,
        )

        tools_called: List[str] = []
        handoff = False
        hitl = False

        start = time.perf_counter()
        try:
            result = await agent.run(query)
            latency = (time.perf_counter() - start) * 1000

            response = result.get("message", "") if result.get("success") else f"ERROR: {result.get('message', '')}"

            # Detect pending HITL actions
            pending = result.get("pending_actions", [])
            if pending:
                hitl = True
                for pa in pending:
                    tool_name = pa.get("tool", "")
                    if tool_name:
                        tools_called.append(tool_name)

                # Auto-approve if configured (for evaluation — we just accept)
                if self.auto_approve and pending:
                    try:
                        approve_result = await agent.approve(self.session_id)
                        if approve_result and approve_result.get("success"):
                            approve_msg = approve_result.get("message", "")
                            response = response + "\n[AUTO-APPROVED]\n" + approve_msg
                            # Re-check for tools in the approval response
                            tools_called.extend(self._infer_tools(approve_msg))
                    except Exception as e:
                        response += f"\n[AUTO-APPROVE ERROR: {e}]"

            # Infer tools from response heuristics
            tools_called.extend(self._infer_tools(response))

            # Detect handoff from response patterns
            handoff = self._detect_handoff(response, result)

            return response, list(set(tools_called)), handoff, hitl, latency, result

        except Exception as e:
            latency = (time.perf_counter() - start) * 1000
            return f"ERROR: {e}", [], False, False, latency, {}
        finally:
            try:
                await agent.disconnect()
            except Exception:
                pass

    # ── Heuristic tool inference ──────────────────────────────────────────────

    @staticmethod
    def _infer_tools(response: str) -> List[str]:
        """Infer tool names from response text patterns."""
        tools = []
        low = response.lower()

        # Direct tool name mentions (from format_tool_call output)
        tool_patterns = {
            "squeue": r"(?:squeue|job queue|job_id.*state|running.*pending)",
            "sinfo": r"(?:sinfo|partition.*nodes|node.*state.*cpu)",
            "sacct": r"(?:sacct|job history|accounting|completed.*failed)",
            "scontrol_show": r"(?:scontrol show|scontrol_show|job detail|node detail)",
            "diagnose_job": r"(?:diagnose_job|diagnosis|exit.code.*interpretation)",
            "sprio": r"(?:sprio|priority.*factor|age.*fairshare)",
            "sstat": r"(?:sstat|real.time.*resource|live.*stats|cpu.*rss)",
            "sdiag": r"(?:sdiag|scheduler.*diagnostic|backfill.*cycle)",
            "sshare": r"(?:sshare|fairshare.*usage)",
            "sreport": r"(?:sreport|utilization.*report|cluster.*report)",
            "generate_chart": r"(?:```mermaid|generate_chart|xychart|flowchart\s+[TL])",
            "sbatch": r"(?:sbatch|submitted.*batch|job.*submitted|submission)",
            "scancel": r"(?:scancel|cancelled.*job|cancel.*job)",
            "scontrol_hold": r"(?:scontrol_hold|job.*held|holding.*job)",
            "scontrol_release": r"(?:scontrol_release|job.*released|releasing.*job)",
            "scontrol_requeue": r"(?:scontrol_requeue|requeued|requeue.*job)",
            "scontrol_update": r"(?:scontrol_update|updated.*job|update.*param|updated.*node)",
            "scontrol_create": r"(?:scontrol_create|created.*partition|created.*reservation)",
            "scontrol_delete": r"(?:scontrol_delete|deleted.*partition|deleted.*reservation)",
            "scontrol_reconfigure": r"(?:scontrol_reconfigure|reconfigur)",
            "sacctmgr_show": r"(?:sacctmgr.*show|sacctmgr_show|qos.*definition|account.*association)",
            "sacctmgr_add": r"(?:sacctmgr.*add|sacctmgr_add|added.*qos|added.*user|added.*account)",
            "sacctmgr_modify": r"(?:sacctmgr.*modify|sacctmgr_modify|modified.*qos|modified.*limit)",
            "sacctmgr_delete": r"(?:sacctmgr.*delete|sacctmgr_delete|deleted.*qos|deleted.*user)",
            "scrontab": r"(?:scrontab|crontab|scheduled.*recurring|cron.*job)",
            "strigger": r"(?:strigger|trigger.*set|trigger.*event|trigger.*list)",
            "sbcast": r"(?:sbcast|broadcast.*file|broadcast.*node)",
            "srun": r"(?:\bsrun\b|interactive.*command|ran.*command.*node)",
            "salloc": r"(?:salloc|interactive.*session|allocated.*resource)",
            "run_analysis": r"(?:run_analysis|analysis.*script|analyze_)",
            "web_search": r"(?:web_search|search.*online|found.*online|according.*to|stackoverflow)",
            "read_file": r"(?:read_file|file.*content|reading.*file)",
            "sjobexitmod": r"(?:sjobexitmod|exit.*code.*modif)",
            "sattach": r"(?:sattach|attach.*job|stdout.*running|stderr.*running)",
            "lookup_skill": r"(?:lookup_skill|skill.*lookup)",
        }

        for tool, pattern in tool_patterns.items():
            if re.search(pattern, low):
                tools.append(tool)

        return tools

    @staticmethod
    def _detect_handoff(response: str, result: Dict) -> bool:
        """Detect if handoff to Operator occurred."""
        low = response.lower()
        # Handoff signals:
        # 1. pending_actions exist (Operator triggered HITL)
        if result.get("pending_actions"):
            return True
        # 2. Operator agent name in result
        if result.get("agent") == "Operator":
            return True
        # 3. Action result keywords (Operator did something)
        action_signals = [
            "submitted", "cancelled", "held", "released", "requeued",
            "updated", "created", "deleted", "reconfigured"
        ]
        if any(s in low for s in action_signals):
            return True
        return False

    # ── Scoring ───────────────────────────────────────────────────────────────

    @staticmethod
    def score_tools(tools_called: List[str], expect: List[str], reject: List[str]) -> Tuple[float, List[str]]:
        """Score tool selection. Returns (score, rejected_tools_found)."""
        if not expect and not reject:
            return 1.0, []

        called = set(tools_called)
        score = 1.0

        # Reward: each expected tool found
        if expect:
            found = called & set(expect)
            recall = len(found) / len(expect)
            score *= recall

        # Penalty: each rejected tool found
        rejected_found = []
        if reject:
            for r in reject:
                if r in called:
                    rejected_found.append(r)
                    score *= 0.5  # halve score per violation

        return min(score, 1.0), rejected_found

    @staticmethod
    def score_handoff(handoff_triggered: bool, expect_handoff: bool) -> float:
        if expect_handoff:
            return 1.0 if handoff_triggered else 0.0
        else:
            return 1.0  # no expectation → pass

    @staticmethod
    def score_hitl(hitl_triggered: bool, expect_hitl: bool) -> float:
        if expect_hitl:
            return 1.0 if hitl_triggered else 0.0
        else:
            return 1.0  # no expectation → pass

    @staticmethod
    def score_keywords(
        response: str, expect_kw: List[str], reject_kw: List[str]
    ) -> Tuple[float, List[str], List[str], List[str]]:
        """Returns (score, found, missing, rejected_found)."""
        low = response.lower()
        found, missing, rejected_found = [], [], []

        for kw in expect_kw:
            if kw.lower() in low:
                found.append(kw)
            else:
                missing.append(kw)

        for kw in reject_kw:
            if kw.lower() in low:
                rejected_found.append(kw)

        if not expect_kw and not reject_kw:
            return 1.0, found, missing, rejected_found

        score = 1.0
        if expect_kw:
            score *= len(found) / len(expect_kw) if expect_kw else 1.0
        if rejected_found:
            score *= max(0.0, 1.0 - 0.3 * len(rejected_found))

        return min(score, 1.0), found, missing, rejected_found

    @staticmethod
    def score_completion(response: str) -> float:
        if not response or "ERROR" in response:
            return 0.0
        length = len(response.strip())
        if length < 20:
            return 0.3
        if length < 100:
            return 0.6
        # Check for markdown (structured) output
        has_table = "|" in response and "---" in response
        has_code = "```" in response
        has_structure = has_table or has_code or response.count("\n") > 3
        return 1.0 if has_structure else 0.8

    # ── Evaluate one test case ────────────────────────────────────────────────

    async def evaluate(self, tc: TestCase) -> TestResult:
        session_id = f"eval_{tc.id}_{int(time.time())}"
        print(f"  [{tc.id}] {tc.description}")

        try:
            response, tools, handoff, hitl, latency, raw = await self._run_agent(
                tc.input, session_id
            )

            tool_score, rej_tools = self.score_tools(tools, tc.expect_tools, tc.reject_tools)
            ho_score = self.score_handoff(handoff, tc.expect_handoff)
            hitl_score = self.score_hitl(hitl, tc.expect_hitl)
            kw_score, kw_found, kw_miss, kw_rej = self.score_keywords(
                response, tc.expect_keywords, tc.reject_keywords
            )
            comp_score = self.score_completion(response)

            result = TestResult(
                test_id=tc.id,
                category=tc.category,
                query=tc.input,
                description=tc.description,
                tool_score=tool_score,
                handoff_score=ho_score,
                hitl_score=hitl_score,
                keyword_score=kw_score,
                completion_score=comp_score,
                tools_called=tools,
                expected_tools=tc.expect_tools,
                rejected_tools_found=rej_tools,
                keywords_found=kw_found,
                keywords_missing=kw_miss,
                rejected_keywords_found=kw_rej,
                handoff_triggered=handoff,
                hitl_triggered=hitl,
                latency_ms=latency,
                response=response,
            )

            mark = "✓" if result.passed else "✗"
            print(
                f"    {mark} {result.overall_score:.2f} "
                f"(tool:{tool_score:.1f} handoff:{ho_score:.1f} hitl:{hitl_score:.1f} "
                f"kw:{kw_score:.1f} comp:{comp_score:.1f}) "
                f"[{latency:.0f}ms]"
            )
            if kw_miss:
                print(f"      └─ missing keywords: {kw_miss}")
            if rej_tools:
                print(f"      └─ rejected tools used: {rej_tools}")

            return result

        except Exception as e:
            print(f"    ✗ ERROR: {e}")
            return TestResult(
                test_id=tc.id,
                category=tc.category,
                query=tc.input,
                description=tc.description,
                error=str(e),
            )

    # ── Run all ───────────────────────────────────────────────────────────────

    async def run_all(self, tests: List[TestCase]) -> List[TestResult]:
        print("=" * 70)
        print("Real Slurm Agent Evaluation — 100 Complex Maneuvers")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"MCP URL: {self.mcp_url}")
        print(f"Model: {self.model}")
        print(f"Tests: {len(tests)}")
        print(f"Auto-approve: {self.auto_approve}")
        print("=" * 70 + "\n")

        for tc in tests:
            result = await self.evaluate(tc)
            self.results.append(result)
            await asyncio.sleep(0.3)

        return self.results

    # ── Summary ───────────────────────────────────────────────────────────────

    def summary(self) -> Dict[str, Any]:
        if not self.results:
            return {}

        passed = sum(1 for r in self.results if r.passed)

        cats: Dict[str, Dict] = {}
        for r in self.results:
            c = cats.setdefault(r.category, {"passed": 0, "total": 0, "scores": []})
            c["total"] += 1
            if r.passed:
                c["passed"] += 1
            c["scores"].append(r.overall_score)

        for data in cats.values():
            data["pass_rate"] = round(data["passed"] / data["total"] * 100, 1) if data["total"] else 0
            data["avg_score"] = round(statistics.mean(data["scores"]), 3) if data["scores"] else 0
            del data["scores"]

        all_scores = [r.overall_score for r in self.results]

        return {
            "total_tests": len(self.results),
            "passed": passed,
            "failed": len(self.results) - passed,
            "pass_rate": round(passed / len(self.results) * 100, 1),
            "avg_overall": round(statistics.mean(all_scores), 3),
            "avg_tool": round(statistics.mean([r.tool_score for r in self.results]), 3),
            "avg_handoff": round(statistics.mean([r.handoff_score for r in self.results]), 3),
            "avg_hitl": round(statistics.mean([r.hitl_score for r in self.results]), 3),
            "avg_keyword": round(statistics.mean([r.keyword_score for r in self.results]), 3),
            "avg_completion": round(statistics.mean([r.completion_score for r in self.results]), 3),
            "by_category": cats,
        }

    # ── LaTeX tables ──────────────────────────────────────────────────────────

    def generate_latex_tables(self) -> str:
        s = self.summary()
        lines = [
            "% Auto-generated by run_real_slurm_eval.py",
            "",
            r"\begin{table}[H]",
            r"    \centering",
            r"    \caption{Complex Real-Slurm Evaluation — Results by Category}",
            r"    \label{tab:real-slurm-eval}",
            r"    \begin{tabular}{|l|c|c|c|c|}",
            r"        \hline",
            r"        \textbf{Category} & \textbf{Tests} & \textbf{Passed} & \textbf{Rate} & \textbf{Avg Score} \\",
            r"        \hline",
        ]
        for cat, data in sorted(s.get("by_category", {}).items()):
            name = cat.replace("_", " ").title()
            lines.append(
                f"        {name} & {data['total']} & {data['passed']} "
                f"& {data['pass_rate']}\\% & {data['avg_score']:.2f} \\\\"
            )
        lines.extend([
            r"        \hline",
            f"        \\textbf{{Total}} & {s['total_tests']} & {s['passed']} "
            f"& {s['pass_rate']}\\% & {s['avg_overall']:.2f} \\\\",
            r"        \hline",
            r"    \end{tabular}",
            r"\end{table}",
            "",
            r"\begin{table}[H]",
            r"    \centering",
            r"    \caption{Complex Real-Slurm Evaluation — Score Breakdown}",
            r"    \label{tab:real-slurm-scores}",
            r"    \begin{tabular}{|l|c|c|l|}",
            r"        \hline",
            r"        \textbf{Metric} & \textbf{Weight} & \textbf{Score} & \textbf{Description} \\",
            r"        \hline",
            f"        Tool Selection & 30\\% & {s['avg_tool']:.2f} & Expected tools called, rejected avoided \\\\",
            f"        Handoff & 20\\% & {s['avg_handoff']:.2f} & Observer→Operator transfer when needed \\\\",
            f"        HITL Compliance & 20\\% & {s['avg_hitl']:.2f} & Dangerous ops trigger approval \\\\",
            f"        Keywords & 20\\% & {s['avg_keyword']:.2f} & Required facts present, forbidden absent \\\\",
            f"        Completion & 10\\% & {s['avg_completion']:.2f} & Structured, non-empty response \\\\",
            r"        \hline",
            f"        \\textbf{{Overall}} & 100\\% & {s['avg_overall']:.2f} & Weighted average \\\\",
            r"        \hline",
            r"    \end{tabular}",
            r"\end{table}",
        ])
        return "\n".join(lines)


# ─── CLI ──────────────────────────────────────────────────────────────────────

async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run 100 complex real-Slurm evaluation tests")
    parser.add_argument(
        "--mcp-url", default="http://localhost:3002",
        help="MCP server URL (default: http://localhost:3002)",
    )
    parser.add_argument(
        "--filter", type=str, default=None,
        help="Filter tests by category or test ID substring (e.g. 'gpu_advanced', 'dep_03')",
    )
    parser.add_argument(
        "--mode", choices=["full", "quick"], default="full",
        help="full=all 100, quick=first test per category",
    )
    parser.add_argument(
        "--auto-approve", action="store_true",
        help="Auto-approve HITL confirmations (for automated runs)",
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Model name for Ollama (default: {DEFAULT_MODEL})",
    )
    args = parser.parse_args()

    tests = list(ALL_TESTS)

    if args.mode == "quick":
        seen_cats = set()
        quick = []
        for t in tests:
            if t.category not in seen_cats:
                seen_cats.add(t.category)
                quick.append(t)
        tests = quick

    if args.filter:
        filt = args.filter.lower()
        tests = [t for t in tests if filt in t.id.lower() or filt in t.category.lower()]
        print(f"Filtered to {len(tests)} tests matching '{args.filter}'")

    if not tests:
        print("No tests matched the filter.")
        return

    evaluator = RealSlurmEvaluator(
        mcp_url=args.mcp_url,
        auto_approve=args.auto_approve,
        model=args.model,
    )

    results = await evaluator.run_all(tests)

    # Summary
    s = evaluator.summary()
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total: {s['total_tests']} tests")
    print(f"Passed: {s['passed']} ({s['pass_rate']}%)")
    print(f"\nScore Breakdown:")
    print(f"  Tool Selection:    {s['avg_tool']:.3f}")
    print(f"  Handoff:           {s['avg_handoff']:.3f}")
    print(f"  HITL Compliance:   {s['avg_hitl']:.3f}")
    print(f"  Keywords:          {s['avg_keyword']:.3f}")
    print(f"  Completion:        {s['avg_completion']:.3f}")
    print(f"  ─────────────────────────")
    print(f"  Overall:           {s['avg_overall']:.3f}")
    print(f"\nBy Category:")
    for cat, data in sorted(s.get("by_category", {}).items()):
        print(f"  {cat:25s} {data['passed']:>2}/{data['total']:<2} ({data['pass_rate']:>5.1f}%) avg={data['avg_score']:.2f}")

    # Save results
    results_dir = os.path.join(EVAL_DIR, "results")
    os.makedirs(results_dir, exist_ok=True)

    suffix = ""
    if args.mode == "quick":
        suffix = "_quick"
    if args.filter:
        suffix = f"_{args.filter}"

    json_path = os.path.join(results_dir, f"real_slurm_eval{suffix}.json")
    with open(json_path, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "mode": args.mode,
                "model": args.model,
                "mcp_url": args.mcp_url,
                "auto_approve": args.auto_approve,
                "summary": s,
                "results": [asdict(r) for r in results],
            },
            f,
            indent=2,
        )
    print(f"\nSaved: {json_path}")

    latex_path = os.path.join(results_dir, f"real_slurm_eval_tables{suffix}.tex")
    with open(latex_path, "w") as f:
        f.write(evaluator.generate_latex_tables())
    print(f"Saved: {latex_path}")

    # Append to score history
    history_path = os.path.join(results_dir, "real_slurm_score_history.jsonl")
    with open(history_path, "a") as f:
        f.write(
            json.dumps(
                {
                    "timestamp": datetime.now().isoformat(),
                    "mode": args.mode,
                    "total": s["total_tests"],
                    "passed": s["passed"],
                    "pass_rate": s["pass_rate"],
                    "scores": {
                        "tool": s["avg_tool"],
                        "handoff": s["avg_handoff"],
                        "hitl": s["avg_hitl"],
                        "keyword": s["avg_keyword"],
                        "completion": s["avg_completion"],
                        "overall": s["avg_overall"],
                    },
                    "by_category": s["by_category"],
                }
            )
            + "\n"
        )
    print(f"Appended: {history_path}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
