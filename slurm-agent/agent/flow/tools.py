"""
FunctionTool factories for the Slurm agent.

All tools that are NOT delivered directly via MCP (confirmation flow, chart
generation, dangerous-action queues) are built here as FunctionTool objects.
Each factory is a plain function that takes the mcp_url and returns a
FunctionTool — easy to test, easy to replace.
"""
import json
import logging
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
    CONFIRM_OUTPUT_GUARDRAILS,
    TOOL_INPUT_GUARDRAILS,
    guard_pending_exists,
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


# ── Confirmation tools ────────────────────────────────────────────────────────

def make_confirm_tool(mcp_url: str) -> FunctionTool:
    """Execute all queued dangerous actions after the user confirms."""
    base = mcp_url.rstrip("/")

    async def _invoke(ctx: ToolContext[SlurmContext], _args: str) -> str:
        pending = ctx.context.get_pending_actions()
        if not pending:
            return "No pending actions to confirm."

        results = []
        for action in pending:
            tool_name   = action["tool"]
            tool_args   = action["args"]
            description = action["description"]
            try:
                content = await _mcp_call(base, tool_name, tool_args)
                text = " ".join(
                    getattr(c, "text", "") for c in content if hasattr(c, "text")
                ).strip() or "done"
                results.append(f"✅ {description}: {text}")
            except Exception as exc:
                logger.error(f"confirm_action error for {tool_name}: {exc}")
                results.append(f"❌ {description}: {exc}")

        ctx.context.clear_pending()
        return "\n".join(results) or "No actions executed."

    def _is_enabled(ctx: RunContextWrapper, _agent) -> bool:
        return bool(ctx.context and ctx.context.get_pending_actions())

    return FunctionTool(
        name="confirm_action",
        description="Execute ALL queued dangerous actions after user confirms (yes/ok/confirm/proceed).",
        params_json_schema={"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        on_invoke_tool=_invoke,
        is_enabled=_is_enabled,
        tool_input_guardrails=[guard_pending_exists],
        tool_output_guardrails=CONFIRM_OUTPUT_GUARDRAILS,
        timeout_seconds=30.0,
        timeout_behavior="error_as_result",
    )


def make_cancel_tool() -> FunctionTool:
    """Discard all queued dangerous actions."""

    async def _invoke(ctx: ToolContext[SlurmContext], _args: str) -> str:
        pending = ctx.context.get_pending_actions()
        if not pending:
            return "No pending actions to cancel."
        descriptions = [p["description"] for p in pending]
        ctx.context.clear_pending()
        return f"❌ Cancelled {len(descriptions)} action(s): {', '.join(descriptions)}"

    def _is_enabled(ctx: RunContextWrapper, _agent) -> bool:
        return bool(ctx.context and ctx.context.get_pending_actions())

    return FunctionTool(
        name="cancel_action",
        description="Cancel ALL queued dangerous actions (user said no/cancel/stop/nevermind).",
        params_json_schema={"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        on_invoke_tool=_invoke,
        is_enabled=_is_enabled,
    )


def make_check_pending_tool() -> FunctionTool:
    """Let the agent inspect what is currently waiting for confirmation."""

    async def _invoke(ctx: ToolContext[SlurmContext], _args: str) -> str:
        pending = ctx.context.get_pending_actions()
        if not pending:
            return "No pending actions."
        lines = [f"- {p['description']}" for p in pending]
        return "Pending actions awaiting confirmation:\n" + "\n".join(lines)

    return FunctionTool(
        name="check_pending_actions",
        description="Check what dangerous actions are pending user confirmation.",
        params_json_schema={"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        on_invoke_tool=_invoke,
    )


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

def make_guarded_dangerous_tools(dangerous_tools: List[DiscoveredTool]) -> List[FunctionTool]:
    """
    Build FunctionTools for every dangerous MCP tool discovered at runtime.
    Instead of executing immediately, each tool queues the call in SlurmContext
    and returns QUEUED: … so the main agent asks the user for confirmation.

    Schemas come from DiscoveredTool.schema (fetched live from MCP), not hardcoded.
    """
    result = []
    for dtool in dangerous_tools:
        def _make_invoke(captured_name: str):
            async def _invoke(ctx: ToolContext[SlurmContext], args_json: str) -> str:
                try:
                    args = json.loads(args_json) if args_json else {}
                except Exception:
                    args = {}
                args_str    = ", ".join(f"{k}={v}" for k, v in args.items()) if args else ""
                description = f"{captured_name}({args_str})"
                ctx.context.add_pending_action(captured_name, args, description)
                total = len(ctx.context.get_pending_actions())
                logger.info(f"Queued: {description} (total={total})")
                return f"QUEUED: {description} ({total} action(s) pending confirmation)"
            return _invoke

        guardrails = TOOL_INPUT_GUARDRAILS.get(dtool.name)
        result.append(FunctionTool(
            name=dtool.name,
            description=dtool.description,
            params_json_schema=dtool.schema,
            on_invoke_tool=_make_invoke(dtool.name),
            strict_json_schema=False,  # MCP schemas aren't guaranteed strict-compatible
            tool_input_guardrails=guardrails,
            tool_output_guardrails=[guard_redact_secrets],
        ))
        logger.debug(f"Registered guarded tool: {dtool.name}")

    return result
