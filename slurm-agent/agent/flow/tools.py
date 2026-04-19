"""
FunctionTool factories for the Slurm agent.

All tools that are NOT delivered directly via MCP (dangerous-action wrappers
with HITL approval, skill lookup, todo tracker) are built here as FunctionTool
objects.
Each factory is a plain function — easy to test, easy to replace.
"""
import json
import logging
from typing import List

from mcp import ClientSession
from mcp.client.sse import sse_client

from agents.tool import FunctionTool
from agents.tool_context import ToolContext

from .context import SlurmContext
from .todo import TodoTracker
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
                            ' Example: sbatch(script="train.sh") or '
                            'sbatch(script="/tmp/slurm_uploads/train.sh").'
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


# ── Skill lookup tool (lazy knowledge retrieval) ──────────────────────────────

def make_skill_lookup_tool(skills: dict[str, str]) -> FunctionTool:
    """
    Create a FunctionTool that loads local markdown runbooks on demand.

    This keeps guides out of the system prompt while still allowing the model
    to fetch deterministic, repo-backed instructions when needed.
    """
    def _normalize(raw: str) -> str:
        return raw.strip().lower().replace(" ", "_").replace("-", "_")

    sorted_names = sorted(skills.keys())
    normalized_to_name = {_normalize(name): name for name in sorted_names}

    def _render_skill(name: str) -> str:
        content = (skills.get(name) or "").strip()
        if len(content) > 7000:
            return content[:7000].rstrip() + "\n\n...[truncated for context size]..."
        return content

    def _list_preview(limit: int = 12) -> str:
        if not sorted_names:
            return "No skills are loaded."
        shown = ", ".join(sorted_names[:limit])
        if len(sorted_names) > limit:
            shown += f", +{len(sorted_names) - limit} more"
        return shown

    async def _invoke(ctx: ToolContext[SlurmContext], args_json: str) -> str:
        if not sorted_names:
            return "No local skill guides are loaded."

        try:
            args = json.loads(args_json) if args_json else {}
        except json.JSONDecodeError:
            args = {}

        query = _normalize(args.get("skill_name", ""))
        if not query:
            return "Provide skill_name. Available: " + _list_preview()

        # Exact canonical match
        if query in normalized_to_name:
            return _render_skill(normalized_to_name[query])

        # Fuzzy match on canonical names
        matches = []
        for canonical, original_name in normalized_to_name.items():
            if query in canonical or canonical in query:
                matches.append(original_name)
        matches = sorted(dict.fromkeys(matches))

        if len(matches) == 1:
            return _render_skill(matches[0])
        if len(matches) > 1:
            shown = ", ".join(matches[:12])
            more = f", +{len(matches) - 12} more" if len(matches) > 12 else ""
            return (
                f"Multiple skills match '{query}': {shown}{more}. "
                "Use exact skill_name."
            )

        return (
            f"Skill '{query}' not found. Available: {_list_preview()}."
        )

    return FunctionTool(
        name="lookup_skill",
        description=(
            "Load a local Slurm workflow/runbook markdown guide by name. "
            "Use for how-to guidance only; do NOT use instead of live data tools "
            "(squeue/sinfo/sacct/scontrol_show). "
            f"Available: {_list_preview(limit=20)}"
        ),
        params_json_schema={
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "Skill file name (without .md), e.g. diagnose_failed_job",
                }
            },
            "required": ["skill_name"],
            "additionalProperties": False,
        },
        on_invoke_tool=_invoke,
        timeout_seconds=5.0,
        timeout_behavior="error_as_result",
    )


# ── Task tracker tool (explicit LLM-driven todo management) ──────────────────

def make_manage_todos_tool(todo: TodoTracker) -> FunctionTool:
    """
    FunctionTool that lets agents explicitly manage their task plan —
    identical in schema to Copilot's manage_todo_list.

    The agent passes the COMPLETE todo list every call (create/update/delete
    all happen by replacing the list).  Schemas: each item must have:
      id     — sequential int (1-based)
      title  — 3-7 word action label
      status — "not-started" | "in-progress" | "completed"

    The tool calls TodoTracker.set_from_tool() which streams the new state
    to the frontend automatically on the next get_snapshot() call.
    """

    async def _invoke(ctx, args_json: str) -> str:
        try:
            args = json.loads(args_json) if args_json else {}
        except json.JSONDecodeError:
            args = {}

        todo_list = args.get("todoList", [])
        if not isinstance(todo_list, list):
            return "Error: todoList must be an array."

        todo.set_from_tool(todo_list)
        count = len(todo.items)
        in_prog = sum(1 for i in todo.items if i["status"] == "in-progress")
        done = sum(1 for i in todo.items if i["status"] == "completed")
        return f"Todo updated: {count} items ({done} completed, {in_prog} in-progress)."

    return FunctionTool(
        name="manage_todos",
        description=(
            "Manage the task plan for this conversation. "
            "Pass the COMPLETE updated todoList every call — this replaces the current list. "
            "Use for multi-step tasks: create the plan upfront, then mark items as you work. "
            "Skip for single-step operations."
        ),
        params_json_schema={
            "type": "object",
            "properties": {
                "todoList": {
                    "type": "array",
                    "description": "Complete array of all todo items (create + existing).",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer",
                                "description": "Sequential id starting from 1.",
                            },
                            "title": {
                                "type": "string",
                                "description": "Concise 3-7 word action label.",
                            },
                            "status": {
                                "type": "string",
                                "enum": ["not-started", "in-progress", "completed"],
                                "description": "not-started | in-progress (max 1) | completed.",
                            },
                        },
                        "required": ["id", "title", "status"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["todoList"],
            "additionalProperties": False,
        },
        on_invoke_tool=_invoke,
        timeout_seconds=5.0,
        timeout_behavior="error_as_result",
    )
