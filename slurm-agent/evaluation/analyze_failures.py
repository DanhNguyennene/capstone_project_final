#!/usr/bin/env python3
"""
Failure mode taxonomy analysis.

Classifies each failed evaluation case into one of several categories:
  - missing_tool        : gt tool was not invoked
  - extra_tool          : agent invoked tools beyond ground truth (and harmful or off-topic)
  - wrong_routing       : handoff to Operator missed or made spuriously
  - missing_hitl        : dangerous tool call without expected HITL approval gate
  - keyword_miss        : answer omitted required factual keyword(s)
  - state_drift         : multi-step state was not preserved
  - judge_quality       : judge score low while structural metrics are high (semantic quality fail)
  - runtime_error       : agent raised an exception or returned no answer

Outputs:
  failure_taxonomy.json  — per-case classification
  failure_taxonomy.md    — human-readable summary table
  failure_taxonomy.csv   — flat per-case table for further analysis
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).parent
RESULTS_DIR = THIS_DIR / "results"
DEFAULT_INPUT = RESULTS_DIR / "eval_all_20260504_001747.json"


def classify(result: dict[str, Any]) -> tuple[str, str]:
    """Return (primary_label, explanation) for a failed case."""
    err = result.get("error")
    if err:
        err_str = str(err)
        low = err_str.lower()
        if "429" in err_str or "rate limit" in low or "ratelimit" in low:
            return "rate_limit", f"upstream LLM rate limit (429): {err_str[:120]}"
        if "timeout" in low or "timed out" in low:
            return "timeout", f"agent timeout: {err_str[:120]}"
        return "runtime_error", f"agent error: {err_str[:120]}"

    tool_recall = float(result.get("tool_recall", 1.0))
    routing_match = float(result.get("routing_match", 1.0))
    hitl_match = float(result.get("hitl_match", 1.0))
    keyword_score = float(result.get("keyword_score", 1.0))
    state_match = float(result.get("state_match", 1.0))
    judge_score = float(result.get("judge_score", 1.0))

    gt_tools = list(result.get("gt_tools", []) or [])
    agent_tools = list(result.get("agent_tools", []) or [])
    gt_handoff = bool(result.get("gt_handoff", False))
    agent_handoff = bool(result.get("agent_handoff", False))
    gt_hitl = bool(result.get("gt_hitl", False))
    agent_hitl = bool(result.get("agent_hitl", False))

    # Routing
    if gt_handoff != agent_handoff:
        if gt_handoff and not agent_handoff:
            return "wrong_routing", "missed handoff to Operator"
        return "wrong_routing", "spurious handoff to Operator"

    # HITL
    if gt_hitl != agent_hitl:
        if gt_hitl and not agent_hitl:
            return "missing_hitl", "dangerous action executed without HITL approval gate"
        return "missing_hitl", "HITL prompt issued for non-dangerous action"

    # Tool selection
    if tool_recall < 1.0 and gt_tools:
        canonical = set(result.get("gt_tools_canonical", gt_tools) or gt_tools)
        invoked = set(agent_tools)
        missing = canonical - invoked
        if missing:
            return "missing_tool", f"required tool(s) not invoked: {sorted(missing)}"

    # Extra tools — only call this out if structural metrics are otherwise fine
    if (
        agent_tools
        and gt_tools
        and len(agent_tools) > len(gt_tools) + 1
        and judge_score < 0.5
    ):
        canonical = set(result.get("gt_tools_canonical", gt_tools) or gt_tools)
        extra = [t for t in agent_tools if t not in canonical]
        if extra:
            return "extra_tool", f"unnecessary tool calls beyond ground truth: {extra[:3]}"

    # State / multi-turn coherence
    if state_match < 0.7:
        return "state_drift", f"state_match={state_match:.2f}; multi-step coherence degraded"

    # Keyword
    if keyword_score < 0.5:
        return "keyword_miss", f"keyword_score={keyword_score:.2f}; required term(s) absent"

    # Judge / semantic quality
    if judge_score < 0.5:
        reason = (result.get("judge_reason") or "").strip()
        return "judge_quality", f"semantic judge low ({judge_score:.2f}): {reason[:120]}"

    # Fallback — overall below threshold but no single dimension dominates
    return "borderline", (
        f"overall={result.get('overall', 0):.2f} with no single dimension below 0.5"
    )


def main(input_path: Path = DEFAULT_INPUT, out_dir: Path = RESULTS_DIR) -> None:
    data = json.loads(input_path.read_text())
    results = data["results"]
    fails = [r for r in results if not r.get("passed", False)]

    classified: list[dict[str, Any]] = []
    for r in fails:
        label, explanation = classify(r)
        classified.append(
            {
                "test_id": r.get("test_id", ""),
                "category": r.get("category", ""),
                "scenario": r.get("scenario", ""),
                "label": label,
                "explanation": explanation,
                "overall": round(float(r.get("overall", 0.0)), 3),
                "tool_recall": round(float(r.get("tool_recall", 0.0)), 3),
                "routing_match": round(float(r.get("routing_match", 0.0)), 3),
                "hitl_match": round(float(r.get("hitl_match", 0.0)), 3),
                "keyword_score": round(float(r.get("keyword_score", 0.0)), 3),
                "state_match": round(float(r.get("state_match", 0.0)), 3),
                "judge_score": round(float(r.get("judge_score", 0.0)), 3),
                "prompt": (r.get("prompt") or "")[:200],
            }
        )

    label_counts = Counter(c["label"] for c in classified)
    cat_label = defaultdict(Counter)
    for c in classified:
        cat_label[c["category"]][c["label"]] += 1

    n_total = len(results)
    n_fail = len(fails)
    pass_rate = (n_total - n_fail) / n_total if n_total else 0.0

    # JSON
    json_out = {
        "input_file": str(input_path),
        "n_total": n_total,
        "n_fail": n_fail,
        "pass_rate": round(pass_rate, 4),
        "label_distribution": dict(label_counts.most_common()),
        "by_category": {k: dict(v) for k, v in cat_label.items()},
        "cases": classified,
    }
    json_path = out_dir / "failure_taxonomy.json"
    json_path.write_text(json.dumps(json_out, indent=2))

    # CSV
    csv_path = out_dir / "failure_taxonomy.csv"
    with csv_path.open("w", newline="") as f:
        cols = [
            "test_id", "category", "scenario", "label", "explanation",
            "overall", "tool_recall", "routing_match", "hitl_match",
            "keyword_score", "state_match", "judge_score", "prompt",
        ]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for c in classified:
            w.writerow(c)

    # Markdown summary
    md = [
        "# Failure Mode Taxonomy",
        "",
        f"- Source: `{input_path.name}`",
        f"- Total cases: **{n_total}**",
        f"- Failed cases: **{n_fail}**",
        f"- Pass rate: **{pass_rate:.1%}**",
        "",
        "## Failure label distribution",
        "",
        "| Label | Count | % of failures | % of total |",
        "|---|---:|---:|---:|",
    ]
    for label, n in label_counts.most_common():
        md.append(
            f"| `{label}` | {n} | {n / n_fail:.1%} | {n / n_total:.2%} |"
        )
    md.append("")

    md += ["## Failure breakdown by category", ""]
    md.append("| Category | Failures | Top label(s) |")
    md.append("|---|---:|---|")
    for cat in sorted(cat_label.keys(), key=lambda k: -sum(cat_label[k].values())):
        sub = cat_label[cat]
        n_cat = sum(sub.values())
        top = ", ".join(f"`{lbl}`({n})" for lbl, n in sub.most_common(3))
        md.append(f"| {cat} | {n_cat} | {top} |")
    md.append("")

    md += ["## Label definitions", ""]
    defs = [
        ("missing_tool", "Required ground-truth tool(s) were never invoked."),
        ("extra_tool", "Agent invoked tools beyond ground truth and judge marked answer poor."),
        ("wrong_routing", "Observer↔Operator handoff missed or fired spuriously."),
        ("missing_hitl", "HITL approval gate was bypassed or wrongly triggered."),
        ("keyword_miss", "Final answer omitted required factual term(s) (keyword_score<0.5)."),
        ("state_drift", "Multi-step state inconsistent across turns (state_match<0.7)."),
        ("judge_quality", "LLM judge marked answer semantically poor despite passing structural checks."),
        ("runtime_error", "Agent raised exception or produced no answer."),
        ("borderline", "Overall score below threshold with no single dimension dominating."),
    ]
    for k, v in defs:
        md.append(f"- **`{k}`** — {v}")
    md.append("")

    md += ["## Sample failures per label", ""]
    by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in classified:
        by_label[c["label"]].append(c)
    for label in label_counts.keys():
        md.append(f"### `{label}` ({label_counts[label]})")
        md.append("")
        for ex in by_label[label][:3]:
            md.append(f"- **{ex['test_id']}** [{ex['category']}] — {ex['explanation']}")
            md.append(f"  > {ex['prompt']}")
        md.append("")

    md_path = out_dir / "failure_taxonomy.md"
    md_path.write_text("\n".join(md))

    print(f"Wrote: {json_path}")
    print(f"Wrote: {csv_path}")
    print(f"Wrote: {md_path}")
    print()
    print(f"Failures: {n_fail}/{n_total} ({(1 - pass_rate):.1%})")
    print("Top labels:")
    for label, n in label_counts.most_common():
        print(f"  {label:18} {n:>4}  ({n / n_fail:.1%})")


if __name__ == "__main__":
    in_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    main(in_path)
