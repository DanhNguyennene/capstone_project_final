"""
FunctionTool factories for the Slurm agent.

All tools that are NOT delivered directly via MCP (chart generation,
dangerous-action wrappers with HITL approval) are built here as
FunctionTool objects.  Each factory is a plain function — easy to test,
easy to replace.
"""
import json
import logging
import re
import uuid
from typing import List

import httpx
from mcp import ClientSession
from mcp.client.sse import sse_client

from agents.tool import FunctionTool
from agents.tool_context import ToolContext
from agents.run_context import RunContextWrapper

from .context import SlurmContext
from .guardrails import (
    TOOL_INPUT_GUARDRAILS,
    guard_redact_secrets,
)
from .tool_discovery import DiscoveredTool

logger = logging.getLogger(__name__)


async def _mcp_call(base: str, tool_name: str, arguments: dict) -> list:
    """Call an MCP tool via SSE transport. Returns content item list."""
    async with sse_client(f"{base}/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content


# ── Chart data extraction ─────────────────────────────────────────────────────

def _extract_chart_data(chart_id: str, mermaid: str) -> str:
    """Extract key data points from Mermaid text so the LLM can report numbers."""
    try:
        if chart_id == "system_health":
            # xychart-beta with bar [cpu%, mem%, gpu%, health%]
            m = re.search(r'bar\s*\[([^\]]+)\]', mermaid)
            if m:
                vals = [v.strip() for v in m.group(1).split(",")]
                labels = ["CPU", "Memory", "GPU Nodes", "Node Health"]
                parts = [f"{l}: {v}%" for l, v in zip(labels, vals)]
                return "Data: " + ", ".join(parts)

        elif chart_id == "cluster_topology":
            # flowchart with "STATE\nN node(s)\nnames"
            nodes_m = re.findall(r'"([A-Z]+)\\n(\d+) node', mermaid)
            if nodes_m:
                parts = [f"{state}: {n}" for state, n in nodes_m]
                return "Nodes by state: " + ", ".join(parts)

        elif chart_id == "pending_analysis":
            if "no pending jobs" in mermaid.lower():
                return "No pending jobs in queue."
            m = re.search(r'title\s+"Pending Queue:\s*(\d+)\s*jobs', mermaid)
            bar_m = re.search(r'bar\s*\[([^\]]+)\]', mermaid)
            axis_m = re.search(r'x-axis\s*\[([^\]]+)\]', mermaid)
            if m and bar_m and axis_m:
                total = m.group(1)
                reasons = [r.strip().strip('"') for r in axis_m.group(1).split(",")]
                counts = [c.strip() for c in bar_m.group(1).split(",")]
                parts = [f"{r}: {c}" for r, c in zip(reasons, counts)]
                return f"{total} pending jobs. Breakdown: " + ", ".join(parts)

        elif chart_id == "resource_map":
            if "no running jobs" in mermaid.lower() or "all resources free" in mermaid.lower():
                return "No running jobs — all resources free."
            bar_m = re.search(r'bar\s*\[([^\]]+)\]', mermaid)
            axis_m = re.search(r'x-axis\s*\[([^\]]+)\]', mermaid)
            if bar_m and axis_m:
                users = [u.strip().strip('"') for u in axis_m.group(1).split(",")]
                cpus = [c.strip() for c in bar_m.group(1).split(",")]
                parts = [f"{u}: {c} CPUs" for u, c in zip(users, cpus)]
                return "CPU usage: " + ", ".join(parts)

        elif chart_id == "job_lifecycle":
            sections = re.findall(r'section\s+(\S+)', mermaid)
            jobs_m = re.findall(r'\[(\d+)\]', mermaid)
            if sections:
                return f"Timeline for {len(jobs_m)} running job(s) across user(s): {', '.join(sections)}"
            if "PENDING" in mermaid:
                return "No running jobs — showing lifecycle template."

        elif chart_id == "efficiency_report":
            bar_m = re.search(r'bar\s*\[([^\]]+)\]', mermaid)
            if bar_m:
                vals = [int(v.strip()) for v in bar_m.group(1).split(",")]
                avg = sum(vals) // len(vals) if vals else 0
                return f"Efficiency for {len(vals)} job(s): avg {avg}%, range {min(vals)}-{max(vals)}%"

    except Exception as e:
        logger.debug(f"Chart data extraction failed for {chart_id}: {e}")

    return ""


# ── Chart tool ────────────────────────────────────────────────────────────────

def make_chart_tool(mcp_url: str, valid_chart_ids: set[str]) -> FunctionTool:
    """
    Wrap the MCP generate_chart tool so that:
      1. The Mermaid artifact is stored in SlurmContext (not returned to the LLM).
      2. The LLM only sees a short summary string.
    """
    base = mcp_url.rstrip("/")

    _MERMAID_MARKERS = [
        "xychart-beta", "xychart", "pie", "gantt",
        "flowchart", "graph ", "%%{init:", "---\nconfig",
    ]

    def _normalize_chart_id(raw: str) -> str:
        cid = (raw or "system_health").strip().lower().replace(" ", "_").replace("-", "_")
        if cid in valid_chart_ids:
            return cid
        # Fuzzy match
        for keyword, target in [
            ("health", "system_health"), ("status", "system_health"), ("overview", "system_health"),
            ("topology", "cluster_topology"), ("structure", "cluster_topology"),
            ("pending", "pending_analysis"), ("waiting", "pending_analysis"), ("queue", "pending_analysis"),
            ("resource_map", "resource_map"), ("allocation", "resource_map"), ("who", "resource_map"),
            ("lifecycle", "job_lifecycle"), ("timeline", "job_lifecycle"), ("gantt", "job_lifecycle"),
        ]:
            if keyword in cid:
                return target
        logger.warning(f"Unknown chart_id '{raw}', defaulting to system_health")
        return "system_health"

    async def _invoke(ctx: ToolContext[SlurmContext], args_json: str) -> str:
        chart_id = "system_health"
        try:
            parsed = json.loads(args_json) if args_json else {}
            chart_id = parsed.get("chart_id", "system_health")
        except json.JSONDecodeError:
            pass

        chart_id = _normalize_chart_id(chart_id)
        logger.info(f"generate_chart: {chart_id}")

        try:
            content = await _mcp_call(base, "generate_chart", {"chart_id": chart_id})
        except Exception as exc:
            return f"❌ Chart generation failed: {exc}"

        summary  = f"✅ Chart '{chart_id}' generated"
        artifact = None

        for item in content:
            text = getattr(item, "text", "") or ""
            if not text:
                continue
            text_low = text.lower()
            is_mermaid = (
                any(m.lower() in text_low for m in _MERMAID_MARKERS)
                or text.strip().startswith("---")
            )
            if is_mermaid:
                artifact = text
            else:
                summary = text

        if artifact:
            ctx.context.add_chart_artifact(artifact)
            # Extract key data points from the Mermaid so the LLM can report them
            data_summary = _extract_chart_data(chart_id, artifact)
            if data_summary:
                summary = f"✅ Chart '{chart_id}' rendered. {data_summary}"
        else:
            logger.warning(f"No mermaid artifact in MCP response for chart '{chart_id}'")

        return summary  # Only summary reaches the LLM

    chart_ids_str = " · ".join(sorted(valid_chart_ids)[:8])
    return FunctionTool(
        name="generate_chart",
        description=f"Generate a Mermaid visualisation.\nAvailable chart IDs: {chart_ids_str}",
        params_json_schema={
            "type": "object",
            "properties": {
                "chart_id": {
                    "type": "string",
                    "description": f"One of: {chart_ids_str}",
                }
            },
            "required": ["chart_id"],
            "additionalProperties": False,
        },
        on_invoke_tool=_invoke,
        tool_output_guardrails=[guard_redact_secrets],
        timeout_seconds=60.0,
        timeout_behavior="error_as_result",
    )


# ── Dangerous-action queuing tools (built from discovered schemas) ────────────

def make_guarded_dangerous_tools(mcp_url: str, dangerous_tools: List[DiscoveredTool]) -> List[FunctionTool]:
    """
    Build FunctionTools for every dangerous MCP tool discovered at runtime.
    Each tool actually executes via MCP, gated by the SDK's needs_approval
    mechanism (Human-in-the-Loop). The Runner will pause with interruptions
    before any dangerous tool runs; the caller must approve/reject and resume.

    Schemas come from DiscoveredTool.schema (fetched live from MCP), not hardcoded.
    """
    base = mcp_url.rstrip("/")
    result = []

    # Schemas with required args — skip HITL for calls missing them
    # so the guardrail rejection goes straight back to the model
    def _make_needs_approval(schema: dict):
        required = set(schema.get("required", []))
        if not required:
            return True  # always need approval if no required args

        def _check_approval(ctx, parsed_args: dict, call_id: str) -> bool:
            # If required args are missing, skip approval so the guardrail
            # rejects immediately and the model can retry without user input
            for key in required:
                val = parsed_args.get(key)
                if val is None or (isinstance(val, str) and not val.strip()):
                    return False
            return True
        return _check_approval

    for dtool in dangerous_tools:
        def _make_invoke(captured_name: str, required_args: set):
            async def _invoke(ctx: ToolContext[SlurmContext], args_json: str) -> str:
                try:
                    args = json.loads(args_json) if args_json else {}
                except Exception:
                    args = {}

                # Early validation: reject missing required args with actionable message
                missing = [k for k in required_args if not args.get(k)]
                if missing:
                    hint = ", ".join(f'{k}="value"' for k in missing)
                    extra = ""
                    if captured_name == "sbatch":
                        extra = (
                            ' Example: sbatch(script="/tmp/slurm_uploads/a.sh,/tmp/slurm_uploads/b.sh")'
                            " — pass file paths from the handoff message."
                        )
                    return (
                        f"❌ {captured_name}() — missing required: {', '.join(missing)}. "
                        f"Provide: {hint}.{extra}"
                    )

                args_str    = ", ".join(f"{k}={v}" for k, v in args.items()) if args else ""
                description = f"{captured_name}({args_str})"
                logger.info(f"Executing approved action: {description}")
                try:
                    content = await _mcp_call(base, captured_name, args)
                    text = " ".join(
                        getattr(c, "text", "") for c in content if hasattr(c, "text")
                    ).strip() or "done"
                    # Detect MCP-level errors returned as text
                    is_error = any(w in text.lower() for w in ("error", "failed", "invalid", "not found"))
                    if is_error:
                        return f"❌ {description}: {text}"
                    # Track that the Operator actually executed an action tool
                    if hasattr(ctx, 'context') and hasattr(ctx.context, 'mark_operator_action'):
                        ctx.context.mark_operator_action()
                    return f"✅ {description}: {text}"
                except Exception as exc:
                    logger.error(f"Action failed: {description}: {exc}")
                    return f"❌ {description}: {exc}"
            return _invoke

        tool_required = set(dtool.schema.get("required", []))
        guardrails = TOOL_INPUT_GUARDRAILS.get(dtool.name)
        result.append(FunctionTool(
            name=dtool.name,
            description=dtool.description,
            params_json_schema=dtool.schema,
            on_invoke_tool=_make_invoke(dtool.name, tool_required),
            strict_json_schema=False,  # MCP schemas aren't guaranteed strict-compatible
            tool_input_guardrails=guardrails,
            tool_output_guardrails=[guard_redact_secrets],
            needs_approval=_make_needs_approval(dtool.schema),
            timeout_seconds=30.0,
            timeout_behavior="error_as_result",
        ))
        logger.info(f"Created HITL-guarded FunctionTool for {dtool.name}")

    return result


# ── Skill lookup tool (lazy knowledge retrieval) ─────────────────────────────

def make_skill_lookup_tool(skills: dict[str, str]) -> FunctionTool:
    """
    Create a FunctionTool that lets the agent load full skill guides on demand.

    Instead of embedding all skill content into the system prompt, only skill
    names appear in the tool description.  The agent calls lookup_skill when
    it encounters a complex task and needs step-by-step guidance.
    """

    async def _invoke(ctx: ToolContext[SlurmContext], args_json: str) -> str:
        try:
            args = json.loads(args_json) if args_json else {}
        except json.JSONDecodeError:
            args = {}

        raw = (args.get("skill_name") or "").strip().lower().replace(" ", "_").replace("-", "_")
        if not raw:
            return "Provide a skill_name. Available: " + ", ".join(sorted(skills.keys()))

        # Exact match
        if raw in skills:
            return skills[raw]

        # Partial / fuzzy match
        for key in skills:
            if raw in key or key in raw:
                return skills[key]

        return f"Skill '{raw}' not found. Available: " + ", ".join(sorted(skills.keys()))

    names = ", ".join(sorted(skills.keys()))
    return FunctionTool(
        name="lookup_skill",
        description=(
            "Load a detailed step-by-step guide for complex Slurm tasks. "
            f"Available: {names}"
        ),
        params_json_schema={
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "Name of the skill guide to load",
                }
            },
            "required": ["skill_name"],
            "additionalProperties": False,
        },
        on_invoke_tool=_invoke,
        timeout_seconds=5.0,
        timeout_behavior="error_as_result",
    )
