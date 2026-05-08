#!/usr/bin/env python3
"""Comprehensive SFT data validator — run BEFORE every training job.

Catches every known class of data-quality issue that degrades model
performance at inference time. Exits non-zero if anything fails so it
can gate a training script.

Usage:
    python training/_validate_sft.py training/out/agent_sft_v2_clean.jsonl
    python training/_validate_sft.py --strict  training/out/agent_sft_v2_clean.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# ── Known-bad patterns (data pollution) ──────────────────────────────────────

_POLLUTION_REGEXES = [
    # Generation-pipeline failure string (v1 bug, 315 rows)
    re.compile(r"request has an edge case", re.I),
    re.compile(r"what I can determine:\s*(script|process|none|the answer)", re.I),
    # Generic refusals that shouldn't be in training data
    re.compile(r"^I('m| am) (sorry|unable|not able),?\s", re.I),
    re.compile(r"^(Sorry|Apologies),?\s.*I can(not|'t)", re.I),
]

# Dangerous tools that must NOT appear in Observer samples
DANGEROUS_TOOLS = {
    "sbatch", "scancel", "srun", "salloc", "sattach", "sbcast",
    "scontrol_hold", "scontrol_release", "scontrol_update",
    "scontrol_reconfigure", "scontrol_requeue", "scontrol_suspend",
    "scontrol_resume_job", "scontrol_node", "scontrol_shutdown",
    "scontrol_create_reservation", "scontrol_delete_reservation",
    "scontrol_update_reservation", "scontrol_write_config",
    "scontrol_setdebug", "scontrol_token",
    "scontrol_node_power_down", "scontrol_node_power_up",
    "scontrol_node_features", "scontrol_node_gres", "scontrol_node_weight",
    "sacctmgr_add", "sacctmgr_modify", "sacctmgr_delete",
    "sacctmgr_recalc", "sacctmgr_archive", "sacctmgr_load", "sacctmgr_dump",
    "strigger_set", "strigger_clear",
    "cluster_history",
}


def _check_tool_args_format(tool_call: dict) -> list[str]:
    """Return list of problems with a tool_call's arguments."""
    issues: list[str] = []
    func = tool_call.get("function", {})
    name = func.get("name", "?")
    raw_args = func.get("arguments", "")

    if not raw_args or raw_args == "{}":
        return issues  # empty args are OK for some tools

    # 1) Must be valid JSON
    try:
        parsed = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
    except json.JSONDecodeError:
        issues.append(f"tool '{name}': arguments not valid JSON: {raw_args[:80]}")
        return issues

    # 2) Must be a dict (not string, list, etc.)
    if not isinstance(parsed, dict):
        issues.append(f"tool '{name}': arguments decoded to {type(parsed).__name__}, not dict")
        return issues

    # 3) No CLI-style flags in values (e.g. "--user charlie")
    for k, v in parsed.items():
        if isinstance(v, str) and re.match(r"^--\w", v.strip()):
            issues.append(f"tool '{name}': arg '{k}' has CLI-style value: {v[:60]}")

    # 4) Check for double-encoded JSON strings
    if isinstance(raw_args, str):
        try:
            inner = json.loads(raw_args)
            if isinstance(inner, str):
                issues.append(f"tool '{name}': arguments are double-encoded JSON string")
        except json.JSONDecodeError:
            pass

    return issues


def _check_message(msg: dict, idx: int, row_idx: int,
                   declared_tools: set[str] | None,
                   role_scope: str) -> list[str]:
    """Validate one message within a conversation."""
    issues: list[str] = []
    msg_role = msg.get("role", "?")
    content = msg.get("content") or ""

    # ── Pollution check on assistant messages ──
    if msg_role == "assistant" and content:
        for pat in _POLLUTION_REGEXES:
            if pat.search(content):
                issues.append(
                    f"row {row_idx} msg {idx}: POLLUTED assistant content "
                    f"matches /{pat.pattern}/"
                )
                break  # one hit per message is enough

    # ── Empty assistant with no tool_calls ──
    if msg_role == "assistant" and not content and not msg.get("tool_calls"):
        issues.append(f"row {row_idx} msg {idx}: assistant has no content AND no tool_calls")

    # ── Tool-call validation ──
    for tc in msg.get("tool_calls") or []:
        func = tc.get("function", {})
        name = func.get("name", "?")

        # Tool declared in schema?
        if declared_tools and name not in declared_tools:
            issues.append(
                f"row {row_idx} msg {idx}: calls '{name}' not in declared tools"
            )

        # Role-scope leaks
        if role_scope == "observer" and name in DANGEROUS_TOOLS:
            issues.append(
                f"row {row_idx} msg {idx}: Observer calls dangerous tool '{name}'"
            )
        if role_scope == "operator" and name == "transfer_to_operator":
            issues.append(
                f"row {row_idx} msg {idx}: Operator calls transfer_to_operator (loop)"
            )

        # Argument format
        issues.extend(_check_tool_args_format(tc))

    # ── Tool response without a corresponding call ──
    if msg_role == "tool" and not msg.get("tool_call_id"):
        issues.append(f"row {row_idx} msg {idx}: tool message has no tool_call_id")

    return issues


def validate(path: str, *, strict: bool = False) -> tuple[list[str], dict]:
    """Run all checks on a JSONL file. Returns (issues_list, stats_dict)."""
    issues: list[str] = []
    stats: dict = {
        "total": 0,
        "no_tools_field": 0,
        "no_tool_calls": 0,
        "short_convos": 0,
        "roles": Counter(),
        "categories": Counter(),
        "tool_names": Counter(),
        "polluted": 0,
        "bad_args": 0,
        "scope_leaks": 0,
    }

    with open(path, encoding="utf-8") as f:
        for row_idx, line in enumerate(f):
            line = line.rstrip("\n")
            if not line:
                continue
            stats["total"] += 1

            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                issues.append(f"row {row_idx}: invalid JSON")
                continue

            msgs = row.get("messages") or []
            tools = row.get("tools")
            meta = row.get("metadata") or {}
            role_scope = meta.get("role", "?")
            category = meta.get("category", "?")
            stats["roles"][role_scope] += 1
            stats["categories"][category] += 1

            # ── Structural checks ──
            if not msgs or len(msgs) < 2:
                issues.append(f"row {row_idx}: fewer than 2 messages")
                stats["short_convos"] += 1
                continue

            if not tools:
                stats["no_tools_field"] += 1
                if strict:
                    issues.append(f"row {row_idx}: no 'tools' field")

            declared = None
            if tools:
                declared = set()
                for t in tools:
                    fn = t.get("function", {})
                    declared.add(fn.get("name", ""))

            has_tool_call = any(m.get("tool_calls") for m in msgs)
            if not has_tool_call:
                stats["no_tool_calls"] += 1

            # ── Per-message checks ──
            for msg_idx, msg in enumerate(msgs):
                msg_issues = _check_message(
                    msg, msg_idx, row_idx,
                    declared_tools=declared,
                    role_scope=role_scope,
                )
                for issue in msg_issues:
                    if "POLLUTED" in issue:
                        stats["polluted"] += 1
                    if "CLI-style" in issue or "double-encoded" in issue or "not dict" in issue:
                        stats["bad_args"] += 1
                    if "dangerous tool" in issue.lower() or "transfer_to_operator" in issue:
                        stats["scope_leaks"] += 1
                issues.extend(msg_issues)

            # ── Conversation coherence ──
            # Check system message exists
            if msgs[0].get("role") != "system":
                if strict:
                    issues.append(f"row {row_idx}: first message is not system")

            # Track tool names used
            for m in msgs:
                for tc in m.get("tool_calls") or []:
                    stats["tool_names"][tc.get("function", {}).get("name", "?")] += 1

    return issues, stats


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate SFT data before training")
    ap.add_argument("path", nargs="?", default="training/out/agent_sft_v2_clean.jsonl")
    ap.add_argument("--strict", action="store_true",
                     help="Also flag warnings (missing tools field, no system msg)")
    ap.add_argument("--max-show", type=int, default=30,
                     help="Max issues to print")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    path = root / args.path if not Path(args.path).is_absolute() else Path(args.path)

    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 2

    print(f"Validating: {path}")
    issues, stats = validate(str(path), strict=args.strict)

    # ── Report ──
    print(f"\n{'='*60}")
    print(f"  Total rows:         {stats['total']}")
    print(f"  Roles:              {dict(stats['roles'])}")
    print(f"  Categories:         {dict(stats['categories'])}")
    print(f"  No tools field:     {stats['no_tools_field']}")
    print(f"  No tool_calls:      {stats['no_tool_calls']}")
    print(f"  Short convos (<2):  {stats['short_convos']}")
    print(f"{'='*60}")

    # Blocking issues (exit 1)
    blocking = {
        "polluted": stats["polluted"],
        "bad_args": stats["bad_args"],
        "scope_leaks": stats["scope_leaks"],
    }
    has_blockers = any(v > 0 for v in blocking.values())

    print(f"\n  BLOCKERS:")
    for k, v in blocking.items():
        status = "✗ FAIL" if v > 0 else "✓ OK"
        print(f"    {k:20s}: {v:5d}  [{status}]")

    top_tools = stats["tool_names"].most_common(15)
    print(f"\n  Top tools used: {[f'{n}({c})' for n,c in top_tools]}")

    if issues:
        print(f"\n  Issues ({len(issues)} total, showing first {args.max_show}):")
        for issue in issues[:args.max_show]:
            print(f"    ⚠  {issue}")
        if len(issues) > args.max_show:
            print(f"    ... and {len(issues) - args.max_show} more")

    print()
    if has_blockers:
        print("✗ VALIDATION FAILED — fix data before training.")
        print("  Run: python training/clean_agent_sft.py --in <file> --out <cleaned>")
        return 1
    elif issues:
        print("⚠ VALIDATION PASSED with warnings. Safe to train.")
        return 0
    else:
        print("✓ VALIDATION PASSED — data is clean. Safe to train.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
