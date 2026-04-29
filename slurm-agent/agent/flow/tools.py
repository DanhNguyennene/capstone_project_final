"""
FunctionTool factories for the Slurm agent.

All tools that are NOT delivered directly via MCP (dangerous-action wrappers
with HITL approval, skill lookup, todo tracker) are built here as FunctionTool
objects.
Each factory is a plain function — easy to test, easy to replace.
"""
import json
import logging
import re
from typing import Any, List

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


def _parse_tool_args(args_json: str | dict | None) -> dict[str, Any]:
    """Parse SDK FunctionTool arguments into a dict.

    Some models/providers occasionally pass a JSON string literal where the
    tool schema expects an object, e.g. '"QOS and Account Limits"' instead of
    '{"title":"QOS and Account Limits"}'.  Tool handlers must never assume
    json.loads(...) returned a dict.
    """
    if args_json is None or args_json == "":
        return {}
    if isinstance(args_json, dict):
        return args_json

    try:
        parsed = json.loads(args_json) if isinstance(args_json, str) else args_json
    except Exception:
        return {"value": str(args_json)}

    if isinstance(parsed, dict):
        return parsed
    if isinstance(parsed, str):
        stripped = parsed.strip()
        if not stripped:
            return {}
        # Handle double-encoded objects: '"{\\\"title\\\": ...}"'.
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                reparsed = json.loads(stripped)
                if isinstance(reparsed, dict):
                    return reparsed
            except Exception:
                pass
        return {"value": stripped}
    return {"value": parsed}


def _coerce_single_required_arg(args: dict[str, Any], required_args: set[str]) -> dict[str, Any]:
    """Map a raw scalar fallback to the sole required schema field, if unambiguous."""
    if "value" not in args or len(required_args) != 1:
        return args
    required_name = next(iter(required_args))
    if args.get(required_name):
        return args
    return {**args, required_name: args["value"]}


def _looks_like_job_id(value: str) -> bool:
    text = (value or "").strip()
    return bool(re.fullmatch(r"\d+(?:_\d+|_\[\d+(?:-\d+)?\])?", text))


def _job_id_list_is_valid(value: Any) -> bool:
    parts = [p.strip() for p in str(value or "").split(",") if p.strip()]
    return bool(parts) and all(_looks_like_job_id(p) for p in parts)


def _runtime_threshold_hours(text: str) -> float | None:
    match = re.search(
        r"\b(?:over|more than|longer than|above|exceed(?:ing)?)\s*(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|h)\b",
        text or "",
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _requires_submission_time_evidence(text: str) -> bool:
    lowered = (text or "").lower()
    return "submitted" in lowered and any(token in lowered for token in ("before", "after", "older than", "newer than"))


def _has_submission_time_evidence(text: str) -> bool:
    """Return True only when discovery output contains a real submit/eligible timestamp."""
    haystack = text or ""
    if re.search(
        r"\b(?:SubmitTime|EligibleTime|submit_time|eligible_time)\s*[=:]\s*\d{4}-\d{2}-\d{2}",
        haystack,
        flags=re.IGNORECASE,
    ):
        return True
    if re.search(
        r"\b(?:submitted|eligible)\b[^\n]*(?:\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2}:\d{2})",
        haystack,
        flags=re.IGNORECASE,
    ):
        return True
    return False


def _action_requires_precondition_evidence(text: str) -> bool:
    """Return True when a destructive action is conditional on state/time evidence."""
    return _runtime_threshold_hours(text) is not None or _requires_submission_time_evidence(text)


def _parse_runtime_seconds(value: str) -> int | None:
    text = (value or "").strip()
    if not text:
        return None
    days = 0
    if "-" in text:
        day_text, text = text.split("-", 1)
        if not day_text.isdigit():
            return None
        days = int(day_text)
    parts = text.split(":")
    try:
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
        elif len(parts) == 2:
            hours = 0
            minutes, seconds = map(int, parts)
        else:
            return None
    except ValueError:
        return None
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def _extract_job_runtimes(squeue_output: str) -> dict[str, int]:
    runtimes: dict[str, int] = {}
    for raw_line in (squeue_output or "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("JOBID") or set(line) <= {"-"}:
            continue
        columns = line.split()
        if len(columns) < 5 or not _looks_like_job_id(columns[0]):
            continue
        seconds = _parse_runtime_seconds(columns[4])
        if seconds is not None:
            runtimes[columns[0]] = seconds
    return runtimes


def _block_operator_action(ctx_obj: Any, reason: str) -> str:
    if ctx_obj is not None and hasattr(ctx_obj, "mark_operator_blocked"):
        ctx_obj.mark_operator_blocked(reason)
    return f"❌ Action blocked: {reason}"


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

    # Safety policy: dangerous actions always require HITL approval before execution.
    # We do not bypass approval for malformed arguments.
    def _make_needs_approval(schema: dict):
        _ = schema
        return True

    for dtool in dangerous_tools:
        def _make_invoke(captured_name: str, required_args: set):
            async def _invoke(ctx: ToolContext[SlurmContext], args_json: str) -> str:
                args = _coerce_single_required_arg(_parse_tool_args(args_json), required_args)
                ctx_obj = ctx.context if hasattr(ctx, "context") else None

                blocked_reason = str(getattr(ctx_obj, "operator_blocked_reason", "") or "").strip()
                if blocked_reason:
                    return _block_operator_action(ctx_obj, blocked_reason)

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
                    return _block_operator_action(
                        ctx_obj,
                        f"{captured_name}() is missing required fields: {', '.join(missing)}. "
                        f"Provide: {hint}.{extra}",
                    )

                if "job_id" in args and not _job_id_list_is_valid(args.get("job_id")):
                    return _block_operator_action(
                        ctx_obj,
                        "Job actions require concrete Slurm numeric job IDs; unresolved labels or invalid IDs are not executable.",
                    )

                action_request = str(getattr(ctx_obj, "operator_action_request", "") or "")
                discovery_output = str(getattr(ctx_obj, "operator_last_discovery_output", "") or "")
                if captured_name == "scancel" and _requires_submission_time_evidence(action_request):
                    if not _has_submission_time_evidence(discovery_output):
                        return _block_operator_action(
                            ctx_obj,
                            "Submission-time condition was not proven by discovery results; refusing destructive action.",
                        )

                threshold_h = _runtime_threshold_hours(action_request)
                if captured_name == "scancel" and threshold_h is not None:
                    job_ids = [p.strip() for p in str(args.get("job_id", "")).split(",") if p.strip()]
                    runtimes = _extract_job_runtimes(discovery_output)
                    threshold_s = threshold_h * 3600
                    eligible = [jid for jid in job_ids if runtimes.get(jid, -1) > threshold_s]
                    if not job_ids or len(eligible) != len(job_ids):
                        return _block_operator_action(
                            ctx_obj,
                            "Conditional runtime action was not proven eligible by the latest discovery results.",
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
                    if ctx_obj is not None and hasattr(ctx_obj, 'mark_operator_action'):
                        ctx_obj.mark_operator_action()
                    return f"✅ {description}: {text}"
                except Exception as exc:
                    logger.error(f"Action failed: {description}: {exc}")
                    return f"❌ {description}: {exc}"
            return _invoke

        def _make_is_enabled(captured_name: str):
            def _is_enabled(run_ctx, _agent) -> bool:
                ctx_obj = run_ctx.context if hasattr(run_ctx, "context") else None
                if bool(getattr(ctx_obj, "operator_blocked_reason", "") or ""):
                    return False
                required = str(getattr(ctx_obj, "operator_required_tool", "") or "").strip().lower()
                if not required:
                    return True
                return captured_name.lower() == required
            return _is_enabled

        tool_required = set(dtool.schema.get("required", []))
        guardrails = TOOL_INPUT_GUARDRAILS.get(dtool.name)
        result.append(FunctionTool(
            name=dtool.name,
            description=dtool.description,
            params_json_schema=dtool.schema,
            on_invoke_tool=_make_invoke(dtool.name, tool_required),
            strict_json_schema=False,  # MCP schemas aren't guaranteed strict-compatible
            is_enabled=_make_is_enabled(dtool.name),
            tool_input_guardrails=guardrails,
            tool_output_guardrails=[guard_redact_secrets],
            needs_approval=_make_needs_approval(dtool.schema),
            timeout_seconds=30.0,
            timeout_behavior="error_as_result",
        ))
        logger.info(f"Created HITL-guarded FunctionTool for {dtool.name}")

    return result


def make_operator_read_tools(mcp_url: str, read_tools: List[DiscoveredTool]) -> List[FunctionTool]:
    """
    Build Operator-side read tools with guardrails tied to handoff payload state.

    Policy:
    - If handoff carries explicit targets, discovery reads are disabled. Operator
      should execute the required action tool directly.
    - For broad actions (no explicit targets), allow at most one discovery read
      call per handoff before forcing execute/handback behavior.
    """
    base = mcp_url.rstrip("/")
    result: List[FunctionTool] = []

    for rtool in read_tools:
        if rtool.name not in {"squeue", "scontrol_show"}:
            continue

        def _make_invoke(captured_name: str, required_args: set):
            async def _invoke(ctx: ToolContext[SlurmContext], args_json: str) -> str:
                args = _coerce_single_required_arg(_parse_tool_args(args_json), required_args)

                missing = [k for k in required_args if not args.get(k)]
                if missing:
                    hint = ", ".join(f'{k}="value"' for k in missing)
                    return (
                        f"❌ {captured_name}() — missing required: {', '.join(missing)}. "
                        f"Provide: {hint}."
                    )

                ctx_obj = ctx.context if hasattr(ctx, "context") else None
                blocked_reason = str(getattr(ctx_obj, "operator_blocked_reason", "") or "").strip()
                if blocked_reason:
                    return blocked_reason
                required = str(getattr(ctx_obj, "operator_required_tool", "") or "").strip().lower()
                targets = list(getattr(ctx_obj, "operator_targets", []) or [])
                discovery_calls = int(getattr(ctx_obj, "operator_discovery_calls", 0) or 0)
                action_request = str(getattr(ctx_obj, "operator_action_request", "") or "")
                needs_evidence = _action_requires_precondition_evidence(action_request)

                if required and targets and not needs_evidence:
                    return (
                        "❌ Discovery read tools are disabled for explicit targets. "
                        "Execute the required action tool now."
                    )

                if discovery_calls >= 1:
                    return (
                        "❌ Discovery read limit reached for this handoff. "
                        "Execute the required action tool or hand back with a concise result."
                    )

                try:
                    content = await _mcp_call(base, captured_name, args)
                    text = " ".join(
                        getattr(c, "text", "") for c in content if hasattr(c, "text")
                    ).strip() or "No output"
                    if ctx_obj is not None and hasattr(ctx_obj, "mark_operator_discovery"):
                        ctx_obj.mark_operator_discovery()
                    if ctx_obj is not None and hasattr(ctx_obj, "record_operator_discovery_output"):
                        ctx_obj.record_operator_discovery_output(text)
                    lowered = text.lower()
                    if "no jobs found" in lowered or "no matching jobs" in lowered:
                        if ctx_obj is not None and hasattr(ctx_obj, "mark_no_targets_found"):
                            ctx_obj.mark_no_targets_found()
                    return text
                except Exception as exc:
                    logger.error(f"Read failed: {captured_name}: {exc}")
                    return f"❌ {captured_name} failed: {exc}"
            return _invoke

        def _make_is_enabled():
            def _is_enabled(run_ctx, _agent) -> bool:
                ctx_obj = run_ctx.context if hasattr(run_ctx, "context") else None
                if ctx_obj is None:
                    return True
                if bool(getattr(ctx_obj, "operator_blocked_reason", "") or ""):
                    return False
                required = str(getattr(ctx_obj, "operator_required_tool", "") or "").strip().lower()
                targets = list(getattr(ctx_obj, "operator_targets", []) or [])
                action_request = str(getattr(ctx_obj, "operator_action_request", "") or "")
                if required and targets and not _action_requires_precondition_evidence(action_request):
                    return False
                discovery_calls = int(getattr(ctx_obj, "operator_discovery_calls", 0) or 0)
                return discovery_calls < 1
            return _is_enabled

        read_required = set(rtool.schema.get("required", []))
        result.append(FunctionTool(
            name=rtool.name,
            description=rtool.description,
            params_json_schema=rtool.schema,
            on_invoke_tool=_make_invoke(rtool.name, read_required),
            strict_json_schema=False,
            is_enabled=_make_is_enabled(),
            timeout_seconds=20.0,
            timeout_behavior="error_as_result",
        ))
        logger.info(f"Created Operator read FunctionTool for {rtool.name}")

    return result


# ── Skill lookup tool (lazy knowledge retrieval) ──────────────────────────────

def make_skill_lookup_tool(skills: dict[str, str]) -> FunctionTool:
    """
    Create a lazy skill browser:
      - list/search returns titles only (no content)
      - read loads one selected title on demand
    This keeps runbook content out of context unless explicitly requested.
    """
    import re

    def _canonical(raw: str) -> str:
        """Canonical form for exact title matching."""
        return re.sub(r"[\s\-]+", "_", (raw or "").strip().lower())

    def _search_norm(raw: str) -> str:
        """Light normalization for title/content search."""
        txt = (raw or "").lower()
        txt = re.sub(r"[^a-z0-9_\-\s]", " ", txt)
        return re.sub(r"\s+", " ", txt).strip()

    sorted_names = sorted(skills.keys())
    canonical_to_name = {_canonical(name): name for name in sorted_names}
    search_index = [
        (name, _search_norm(name), _search_norm(skills.get(name, "")))
        for name in sorted_names
    ]

    def _render_skill(name: str) -> str:
        content = (skills.get(name) or "").strip()
        if len(content) > 7000:
            return content[:7000].rstrip() + "\n\n...[truncated for context size]..."
        return content

    def _parse_limit(raw_limit: object, default: int = 12) -> int:
        try:
            n = int(str(raw_limit))
        except Exception:
            n = default
        return max(1, min(50, n))

    def _format_titles(titles: list[str], *, total: int, label: str) -> str:
        if not titles:
            return f"{label}: no results."
        lines = [f"{label} ({len(titles)}/{total}):"]
        lines.extend(f"{i+1}. {title}" for i, title in enumerate(titles))
        lines.append('Use mode="read" with exact title to load one.')
        return "\n".join(lines)

    async def _invoke(ctx: ToolContext[SlurmContext], args_json: str) -> str:
        if not sorted_names:
            return "No local skill guides are loaded."

        args = _parse_tool_args(args_json)

        raw_value = str(args.get("value", "")).strip()
        raw_mode = str(args.get("mode", "")).strip().lower()
        query = str(args.get("query", "")).strip()
        title = str(args.get("title") or args.get("skill_name") or raw_value or "").strip()
        limit = _parse_limit(args.get("limit", 12))

        if raw_mode and raw_mode not in {"list", "search", "read"}:
            return "Invalid mode. Use one of: list, search, read."

        # Backward-compatible mode inference
        mode = raw_mode
        if not mode:
            if title:
                mode = "read"
            elif query:
                mode = "search"
            else:
                mode = "list"

        if mode == "list":
            shown = sorted_names[:limit]
            return _format_titles(shown, total=len(sorted_names), label="Skill titles")

        if mode == "search":
            if not query:
                return 'Provide query for search mode, or use mode="list".'
            qn = _search_norm(query)
            scored: list[tuple[int, str]] = []
            for name, title_norm, content_norm in search_index:
                score = 0
                if qn == title_norm:
                    score = 300
                elif qn and qn in title_norm:
                    score = 200
                elif qn and title_norm in qn:
                    score = 150
                elif qn and qn in content_norm:
                    score = 100
                if score == 0 and qn:
                    # Lightweight token-overlap fallback for queries like "failed job diagnosis"
                    q_tokens = [tok for tok in qn.split(" ") if len(tok) >= 3]
                    title_hits = sum(1 for tok in q_tokens if tok in title_norm)
                    content_hits = sum(1 for tok in q_tokens if tok in content_norm)
                    if title_hits:
                        score = 120 + title_hits
                    elif content_hits >= 2:
                        score = 80 + content_hits
                if score > 0:
                    scored.append((score, name))
            scored.sort(key=lambda x: (-x[0], x[1]))
            titles = [name for _, name in scored[:limit]]
            return _format_titles(titles, total=len(scored), label=f"Skill search: {query}")

        # mode == "read": load exactly one chosen title
        if not title:
            return 'Provide title for read mode. Tip: use mode="search" first.'

        canonical = _canonical(title)
        exact_name = canonical_to_name.get(canonical)
        if exact_name:
            return _render_skill(exact_name)

        # No exact title: return suggestions (titles only), never content.
        suggestions: list[str] = []
        for name in sorted_names:
            c = _canonical(name)
            if canonical in c or c in canonical:
                suggestions.append(name)
        suggestions = suggestions[:limit]
        if suggestions:
            return _format_titles(
                suggestions,
                total=len(suggestions),
                label=f'No exact title for "{title}". Similar titles',
            )
        return f'No skill title matches "{title}". Use mode="search" first.'

    return FunctionTool(
        name="lookup_skill",
        description=(
            "Lazy skill browser for local Slurm runbooks. "
            "mode=list/search returns titles only; mode=read loads one selected title. "
            "Search matches both titles and content, but returns titles only."
        ),
        params_json_schema={
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["list", "search", "read"],
                    "description": (
                        "Operation mode. list=show titles, search=match titles/content, "
                        "read=load one skill content."
                    ),
                },
                "query": {
                    "type": "string",
                    "description": "Search text for mode=search.",
                },
                "title": {
                    "type": "string",
                    "description": "Exact skill title for mode=read.",
                },
                "skill_name": {
                    "type": "string",
                    "description": "Legacy alias of title for backward compatibility.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "description": "Max titles to return for list/search (default: 12).",
                }
            },
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
        args = _parse_tool_args(args_json)

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
