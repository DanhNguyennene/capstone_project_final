"""
SlurmAgentSystem — two-agent handoff orchestrator.

Architecture:
  Observer  — entry point, read-only MCP tools + optional skill lookup
  Operator  — dangerous-action FunctionTools (HITL) + minimal read tools

The Observer handles monitoring / analysis / diagnosis (~80 % of requests).
When an action is needed it hands off to the Operator; the Operator can hand
back for further investigation.  The OpenAI Agents SDK runner follows handoffs
automatically — no manual routing code required.
"""
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Dict, List, Optional

from agents import Agent, Runner, RunState, SQLiteSession, ItemHelpers, handoff, SessionSettings
from agents.extensions.handoff_filters import remove_all_tools
from agents.handoffs import HandoffInputData
from agents.mcp import MCPServerSse, ToolFilterContext
from agents.model_settings import ModelSettings

from .context import ChartFilteredSession, SlurmContext
from .guardrails import guard_job_id  # imported so the guardrail registry is populated
from .instructions import (
    build_observer_instructions,
    build_operator_instructions,
    brief_output_summary,
    format_tool_call,
)
from .model import (
    DEFAULT_MODEL,
    SPECIALIST_MODEL,
    OLLAMA_BASE_URL,
    GITHUB_TOKEN,
    COPILOT_BASE_URL,
    COPILOT_MODEL,
    GITHUB_MODELS_BASE_URL,
    GITHUB_MODELS_MODEL,
    OPENAI_BASE_URL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    LLM_PROVIDER,
    normalize_provider,
    model_settings_for_provider,
    resolve_model,
)
from .skills import (
    load_observer_skills,
)
from .todo import TodoTracker
from .tool_discovery import ToolCatalog, discover_tools
from .tools import (
    make_guarded_dangerous_tools,
    make_operator_read_tools,
    make_skill_lookup_tool,
)

logger = logging.getLogger(__name__)


# ── Mutable state container for stream event processing ──────────────────────

@dataclass
class _StreamState:
    """Tracks state across a single stream event iteration."""
    content_streamed: bool = False
    charts_emitted: int = 0
    hitl_tool_outputs: List[str] = field(default_factory=list)
    _is_first_agent_event: bool = True


@dataclass
class _OperatorHandoffPayload:
    """Structured payload Observer must pass when handing off to Operator."""
    action_request: str
    required_tool: str
    targets: List[str] = field(default_factory=list)


def _make_mcp_server(mcp_url: str, allowed: set[str], name: str = "slurm-mcp") -> MCPServerSse:
    """Create a filtered MCP-SSE server exposing only the named tools."""
    async def _filter(ctx: ToolFilterContext, tool) -> bool:
        return tool.name in allowed

    return MCPServerSse(
        params={
            "url": f"{mcp_url.rstrip('/')}/sse",
            "timeout": 60,
            "sse_read_timeout": 600,
        },
        name=name,
        client_session_timeout_seconds=300,
        cache_tools_list=True,
        tool_filter=_filter,
    )


# ── Tool names given to the Operator for pre-action verification ──────────────
_OPERATOR_READ_TOOLS = {"scontrol_show", "squeue"}
_OBSERVER_HIDDEN_MCP_TOOLS = {"cluster_history", "reset_mock_state"}



class SlurmAgentSystem:
    """
    Two-agent handoff system for Slurm HPC clusters.

    Observer (entry point):
        Read-only MCP tools (analysis + safe) + optional skill lookup tool.
        Handles monitoring, diagnosis, and analysis. Hands off to Operator
        when an action is required.

    Operator:
        Dangerous FunctionTools with needs_approval=True (HITL).
        Plus squeue / scontrol_show via MCP for pre-action verification.
        Hands off back to Observer for further investigation.

    First call to run_streaming / run performs lazy init:
      1. discover_tools() — one HTTP call to MCP, builds ToolCatalog
      2. Loads Observer skill guides from agent/skills/*
      3. Builds Observer + Operator agents with bidirectional handoffs
    """

    def __init__(
        self,
        reasoning_model: str = DEFAULT_MODEL,
        mcp_url: str = "http://localhost:3002",
        session_id: str = "default",
        auto_approve: bool = False,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        specialist_model: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ):
        self.mcp_url      = mcp_url
        self.session_id   = session_id
        self.auto_approve = auto_approve

        self.llm_provider = normalize_provider(llm_provider or LLM_PROVIDER)
        self.llm_model = (llm_model or reasoning_model or DEFAULT_MODEL).strip()
        self.openai_api_key = openai_api_key or OPENAI_API_KEY
        default_specialist = OPENAI_MODEL if self.llm_provider == "openai" else SPECIALIST_MODEL
        self.specialist_model = (specialist_model or default_specialist).strip()

        self._reasoning_model = resolve_model(
            self.llm_model,
            provider=self.llm_provider,
            openai_api_key=self.openai_api_key,
        )
        self._active_model_settings = model_settings_for_provider(self.llm_provider)

        self._session: Optional[ChartFilteredSession] = None
        self._mcp_observer: Optional[MCPServerSse]    = None
        self._mcp_operator: Optional[MCPServerSse]    = None

        self.main_agent      = None   # entry-point agent (Observer)
        self.operator_agent  = None   # direct retry target
        self._catalog: Optional[ToolCatalog] = None
        self._ready          = False

        # Session-scoped task plan
        self._todo = TodoTracker(
            llm_provider=self.llm_provider,
            main_model=self.llm_model,
            specialist_model=self.specialist_model,
            openai_api_key=self.openai_api_key,
        )

        # HITL: store RunState + interruptions between requests for approval flow
        self._pending_approvals: Dict[str, dict] = {}

    # ── Initialisation ─────────────────────────────────────────────────────────

    async def _init(self):
        if self._ready:
            return

        logger.info(f"[SlurmAgentSystem] Initialising (session={self.session_id})")

        # 1. Discover tools — fetch live schemas, classify
        self._catalog = await discover_tools(self.mcp_url)

        # 2. Build instructions
        observer_instructions = build_observer_instructions()
        operator_instructions = build_operator_instructions()

        # 3. Load Observer-only skill lookup tool (local markdown runbooks)
        observer_skills = load_observer_skills()
        skill_lookup_tool = make_skill_lookup_tool(observer_skills) if observer_skills else None

        # 4. MCP servers — Observer gets read-only tools minus internal control tools
        observer_mcp_names = (self._catalog.analysis_names | self._catalog.safe_names) - _OBSERVER_HIDDEN_MCP_TOOLS
        self._mcp_observer = _make_mcp_server(self.mcp_url, observer_mcp_names, "slurm-observer-mcp")

        # Operator reads are exposed as guarded FunctionTools (not raw MCP tools)
        # so we can enforce per-handoff policies.
        self._mcp_operator = _make_mcp_server(self.mcp_url, set(), "slurm-operator-mcp")

        # 5. Guarded dangerous FunctionTools (HITL: needs_approval=True)
        dangerous_fns = make_guarded_dangerous_tools(self.mcp_url, self._catalog.dangerous)
        operator_read_defs = [
            t for t in (self._catalog.analysis + self._catalog.safe)
            if t.name in _OPERATOR_READ_TOOLS
        ]
        operator_read_fns = make_operator_read_tools(self.mcp_url, operator_read_defs)

        # 6. Build agents with bidirectional handoffs
        #    Keep Observer tool surface focused on operational tools.
        _observer_tools: list = []
        if skill_lookup_tool:
            _observer_tools.append(skill_lookup_tool)

        observer = Agent(
            name="Observer",
            instructions=observer_instructions,
            model=self._reasoning_model,
            model_settings=self._active_model_settings.resolve(
                ModelSettings(tool_choice="required")
            ),
            mcp_servers=[self._mcp_observer],
            tools=_observer_tools,
            handoffs=[],  # filled below
        )

        operator = Agent(
            name="Operator",
            instructions=operator_instructions,
            model=self._reasoning_model,
            model_settings=self._active_model_settings.resolve(
                ModelSettings(tool_choice="required")
            ),
            mcp_servers=[self._mcp_operator],
            tools=dangerous_fns + operator_read_fns,
            handoffs=[],  # filled below
        )

        # Wire bidirectional handoffs
        def _capture_operator_handoff(ctx, payload: _OperatorHandoffPayload) -> None:
            # Persist required action tool in run context so non-required dangerous
            # tools are hidden from Operator during this handoff.
            ctx_obj = ctx.context if hasattr(ctx, "context") else None
            if ctx_obj is None:
                return
            required_tool = _normalize_tool_name(getattr(payload, "required_tool", ""))
            raw_targets = getattr(payload, "targets", [])
            if not isinstance(raw_targets, list):
                raw_targets = [raw_targets] if raw_targets else []
            targets = [str(t).strip() for t in raw_targets if str(t).strip()]
            if hasattr(ctx_obj, "reset_operator_handoff_state"):
                ctx_obj.reset_operator_handoff_state()
            if hasattr(ctx_obj, "operator_required_tool"):
                ctx_obj.operator_required_tool = required_tool
            if hasattr(ctx_obj, "operator_targets"):
                ctx_obj.operator_targets = targets

        def _operator_handoff_input_filter(handoff_data: HandoffInputData) -> HandoffInputData:
            """Provide Operator a canonical action request from handoff payload."""
            canonical_text = ""
            for run_item in getattr(handoff_data, "new_items", ()) or ():
                run_item_type = getattr(run_item, "type", "")
                if run_item_type != "handoff_call_item":
                    continue
                raw_item = getattr(run_item, "raw_item", None)
                if getattr(raw_item, "name", "") != "transfer_to_operator":
                    continue
                raw_args = getattr(raw_item, "arguments", "{}") or "{}"
                try:
                    payload = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})
                except Exception:
                    payload = {}
                action_request = str(payload.get("action_request", "")).strip()
                targets = payload.get("targets", [])
                required_tool = _normalize_tool_name(str(payload.get("required_tool", "")).strip())
                if not isinstance(targets, list):
                    targets = [targets] if targets else []
                targets = [str(t).strip() for t in targets if str(t).strip()]
                if action_request:
                    lines = [
                        "Execute this exact cluster-state action now.",
                        "Do not substitute a different action type.",
                        f"Action request: {action_request}",
                    ]
                    if required_tool:
                        lines.append(f"Required tool: {required_tool}")
                    if targets:
                        lines.append(f"Targets: {', '.join(targets)}")
                    if required_tool:
                        lines.append(f"First action tool call MUST use {required_tool}.")
                    canonical_text = "\n".join(lines)
                break

            cleaned = remove_all_tools(handoff_data)
            if canonical_text:
                canonical_input = {
                    "role": "user",
                    "content": [{"type": "input_text", "text": canonical_text}],
                }
                return cleaned.clone(
                    input_history=(canonical_input,),
                    pre_handoff_items=(),
                    input_items=(),
                )
            return cleaned

        def _observer_handoff_input_filter(handoff_data: HandoffInputData) -> HandoffInputData:
            """Give Observer only completion context to avoid action re-handoff loops."""
            snippets: List[str] = []
            for run_item in getattr(handoff_data, "new_items", ()) or ():
                run_item_type = getattr(run_item, "type", "")
                if run_item_type == "tool_call_output_item":
                    out = _extract_tool_output_text(getattr(run_item, "output", None)).strip()
                    if out:
                        snippets.append(out)
                elif run_item_type == "message_output_item":
                    msg = _strip_hallucinated_calls(ItemHelpers.text_message_output(run_item) or "")
                    if msg.strip():
                        snippets.append(msg.strip())

            seen = set()
            compact_snippets: List[str] = []
            for s in snippets:
                norm = " ".join(s.split()).lower()
                if norm in seen:
                    continue
                seen.add(norm)
                compact_snippets.append(s[:500])
                if len(compact_snippets) >= 3:
                    break

            lines = [
                "Action execution phase is complete.",
                "Prepare the final user-facing summary from these results.",
                "Do NOT call transfer_to_operator again unless a NEW user message asks for another action.",
            ]
            if compact_snippets:
                lines.append("Execution results:")
                lines.extend(f"- {s}" for s in compact_snippets)

            cleaned = remove_all_tools(handoff_data)
            canonical_input = {
                "role": "user",
                "content": [{"type": "input_text", "text": "\n".join(lines)}],
            }
            return cleaned.clone(
                input_history=(canonical_input,),
                pre_handoff_items=(),
                input_items=(),
            )

        def _build_transfer_to_operator_handoff():
            return handoff(
                operator,
                tool_name_override="transfer_to_operator",
                tool_description_override=(
                    "Hand off to the Operator to EXECUTE actions that modify the cluster. "
                    "Call with structured args: action_request (required imperative action) "
                    "required_tool (exact action tool name), and targets (optional list of job IDs / node names / user/account). "
                    "Example: action_request='Cancel jobs 1001,1002', required_tool='scancel', targets=['1001','1002']. "
                    "The Operator will call the tools and report results."
                ),
                on_handoff=_capture_operator_handoff,
                input_type=_OperatorHandoffPayload,
                input_filter=_operator_handoff_input_filter,
            )

        observer.handoffs = [_build_transfer_to_operator_handoff()]
        # Guard: Operator can only hand back AFTER executing at least one action.
        # is_enabled hides transfer_to_observer until an action has fired OR
        # discovery has confirmed there are no eligible targets this handoff.
        def _operator_handoff_enabled(ctx, _agent) -> bool:
            slurm_ctx = ctx.context if hasattr(ctx, 'context') else None
            if slurm_ctx and hasattr(slurm_ctx, 'operator_actions_taken'):
                actions_taken = int(getattr(slurm_ctx, 'operator_actions_taken', 0) or 0)
                no_targets = bool(getattr(slurm_ctx, 'operator_no_targets_found', False))
                return actions_taken > 0 or no_targets
            return False  # strict: never allow handback before an action call

        operator.handoffs = [
            handoff(
                observer,
                tool_name_override="transfer_to_observer",
                tool_description_override=(
                    "Hand back to the Observer ONLY for purely read-only requests "
                    "(monitoring, analysis, questions). NEVER use this if the handoff "
                    "message asks you to submit, cancel, hold, release, or requeue. "
                    "You must call the action tools first."
                ),
                is_enabled=_operator_handoff_enabled,
                input_filter=_observer_handoff_input_filter,
            ),
        ]

        self.main_agent    = observer  # default entry point
        self.operator_agent = operator  # direct retry target

        self._ready = True
        obs_tools = len(observer_mcp_names) + len(_observer_tools)   # MCP + function tools
        op_tools  = len(dangerous_fns) + len(operator_read_fns)  # dangerous + guarded read tools
        logger.info(
            f"[SlurmAgentSystem] Ready — "
            f"Observer tools≈{obs_tools} Operator tools≈{op_tools} "
            f"observer_skills={len(observer_skills)}"
        )

    # ── Session ───────────────────────────────────────────────────────────────

    def _get_session(self) -> ChartFilteredSession:
        if self._session is None:
            # Limit serves as a hard cap before compaction kicks in.
            # Compaction (at COMPACT_THRESHOLD=50) replaces old items with a summary,
            # so the limit just guards against a single huge fetch if compaction hasn't run yet.
            raw = SQLiteSession(
                self.session_id,
                "/tmp/slurm_agent_conversations.db",
                session_settings=SessionSettings(limit=self.COMPACT_THRESHOLD),
            )
            self._session = ChartFilteredSession(raw)
        return self._session

    def _new_context(self) -> SlurmContext:
        return SlurmContext(session_id=self.session_id)

    # ── Session compaction ───────────────────────────────────────────────────

    # When session grows beyond COMPACT_THRESHOLD items, the older portion is
    # summarised by a lightweight LLM call and the DB rows replaced with:
    #   [summary_item] + most-recent KEEP_RECENT items
    # This keeps context relevant without unbounded growth.
    COMPACT_THRESHOLD = 50   # items before compaction triggers
    KEEP_RECENT       = 20   # recent items kept verbatim

    @staticmethod
    def _extract_text_from_items(items: list) -> str:
        """Pull human-readable text from SDK session items (dict format)."""
        parts: List[str] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            itype = item.get("type", "")
            role  = item.get("role", "")

            # User / assistant messages
            if itype == "message" or role in ("user", "assistant"):
                content = item.get("content", "")
                if isinstance(content, list):
                    # [{"type": "input_text"/"output_text", "text": "..."}]
                    texts = [
                        p.get("text", "")
                        for p in content
                        if isinstance(p, dict) and p.get("type") in (
                            "input_text", "output_text", "text",
                        )
                    ]
                    text = " ".join(t for t in texts if t)
                elif isinstance(content, str):
                    text = content
                else:
                    continue
                if text.strip():
                    label = role.capitalize() if role else "Msg"
                    parts.append(f"{label}: {text.strip()[:500]}")

            # Tool calls — just the name + short args
            elif itype == "function_call":
                name = item.get("name", "?")
                args = item.get("arguments", "")
                if isinstance(args, str) and len(args) > 120:
                    args = args[:120] + "…"
                parts.append(f"Tool call: {name}({args})")

            # Tool outputs — truncate heavily (these are the biggest items)
            elif itype == "function_call_output":
                output = item.get("output", "")
                if isinstance(output, str) and output.strip():
                    preview = output.strip()[:200]
                    parts.append(f"Tool result: {preview}{'…' if len(output) > 200 else ''}")

        return "\n".join(parts)

    async def _summarize_conversation(self, conversation_text: str) -> str:
        """Use a lightweight LLM call to produce a concise conversation summary."""
        from openai import AsyncOpenAI
        try:
            provider = self.llm_provider
            if provider == "copilot":
                if not GITHUB_TOKEN:
                    raise RuntimeError("GITHUB_TOKEN missing for copilot provider")
                client = AsyncOpenAI(base_url=COPILOT_BASE_URL, api_key=GITHUB_TOKEN)
                _model = self.llm_model or COPILOT_MODEL
                _extra: dict = {}
            elif provider == "github-models":
                if not GITHUB_TOKEN:
                    raise RuntimeError("GITHUB_TOKEN missing for github-models provider")
                client = AsyncOpenAI(base_url=GITHUB_MODELS_BASE_URL, api_key=GITHUB_TOKEN)
                _model = self.llm_model or GITHUB_MODELS_MODEL
                _extra = {}
            elif provider == "openai":
                token = self.openai_api_key or OPENAI_API_KEY
                if not token:
                    raise RuntimeError("OPENAI_API_KEY missing for openai provider")
                client = AsyncOpenAI(base_url=OPENAI_BASE_URL, api_key=token)
                _model = self.llm_model or OPENAI_MODEL
                _extra = {}
            else:
                client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
                _model = self.llm_model or DEFAULT_MODEL
                _extra = {"think": False}
            # Truncate input to avoid overloading the summarisation call itself
            if len(conversation_text) > 6000:
                conversation_text = conversation_text[:6000] + "\n[...truncated]"
            resp = await client.chat.completions.create(
                model=_model,
                messages=[
                    {"role": "system", "content": (
                        "Summarise the following Slurm HPC assistant conversation into a concise "
                        "recap (max 300 words). Preserve: key facts discovered (job IDs, node "
                        "names, error codes, partition states), user goals, and conclusions reached. "
                        "Omit raw tool output details. Use bullet points."
                    )},
                    {"role": "user", "content": conversation_text},
                ],
                temperature=0.1,
                max_tokens=500,
                **(({"extra_body": _extra}) if _extra else {}),
            )
            summary = (resp.choices[0].message.content or "").strip()
            if summary:
                return summary
        except Exception as e:
            logger.warning(f"Conversation summarisation failed: {e}")

        # Fallback: no LLM summary, just keep a text extract
        return conversation_text[:2000]

    async def _compact_session(self):
        """Compact session history if it has grown beyond threshold.

        Replaces old items with an LLM-generated summary to keep context
        relevant without unbounded DB growth.
        """
        session = self._get_session()
        try:
            items = await session.get_items()
        except Exception:
            return

        if not items or len(items) <= self.COMPACT_THRESHOLD:
            return

        old_count = len(items)
        old_items = items[:-self.KEEP_RECENT]
        recent_items = items[-self.KEEP_RECENT:]

        # Extract readable conversation from old items
        conversation_text = self._extract_text_from_items(old_items)
        if not conversation_text.strip():
            # Nothing meaningful to summarise — just drop old items
            await session.clear_session()
            await session.add_items(recent_items)
            logger.info(f"Session compacted (no text): {old_count} → {len(recent_items)} items")
            return

        # Summarise via LLM
        summary = await self._summarize_conversation(conversation_text)

        # Rebuild session: [summary] + recent items
        summary_item = {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": (
                        "[Conversation history summary — earlier messages were compacted]\n\n"
                        f"{summary}"
                    ),
                }
            ],
        }

        await session.clear_session()
        await session.add_items([summary_item] + recent_items)
        new_count = 1 + len(recent_items)
        logger.info(f"Session compacted: {old_count} → {new_count} items (summary: {len(summary)} chars)")

    # ── Reusable stream event processor ──────────────────────────────────────

    async def _emit_stream_events(
        self,
        result,
        state: _StreamState,
        *,
        todo: TodoTracker,
        ctx: "SlurmContext",
        approval_data: dict | None = None,
        hitl_approved_tools: List[str] | None = None,
        augmented_message: str = "",
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process streaming events from a Runner result and yield UI events.

        Updates ``state`` in place so the caller can inspect
        ``content_streamed`` / ``hitl_tool_outputs`` after iteration.
        """
        hitl_tools = hitl_approved_tools or []

        async for event in result.stream_events():
            # ── Agent handoff events ──
            if event.type == "agent_updated_stream_event":
                if state._is_first_agent_event:
                    state._is_first_agent_event = False
                    continue
                new_name = getattr(event.new_agent, "name", "Agent")
                yield {"type": "status", "message": f"↪ Handing off to {new_name}"}
                continue

            if event.type == "raw_response_event":
                try:
                    event_data = event.data
                    event_data_type = getattr(event_data, "type", "")
                    if event_data_type in (
                        "response.reasoning_text.delta",
                        "response.reasoning_summary_text.delta",
                    ):
                        r = getattr(event_data, "delta", None)
                        if r:
                            yield {"type": "thinking", "content": r}
                    elif event_data_type == "response.output_text.delta":
                        r = getattr(event_data, "delta", None)
                        if r:
                            if not state.content_streamed:
                                todo.on_response_start()
                                snap = todo.get_snapshot()
                                if snap:
                                    yield {"type": "todo", "items": snap}
                            yield {"type": "final_answer", "message": r}
                            state.content_streamed = True
                except Exception:
                    pass
                continue

            if event.type != "run_item_stream_event":
                continue

            item = event.item

            if item.type == "tool_call_item":
                name = getattr(item.raw_item, "name", "") if hasattr(item, "raw_item") else ""
                raw_args = getattr(item.raw_item, "arguments", "{}") if hasattr(item, "raw_item") else "{}"
                try:
                    args = json.loads(raw_args)
                except Exception:
                    args = {}
                if name:
                    yield {"type": "status", "message": format_tool_call(name, args)}
                    todo.on_tool_start(name)
                    snap = todo.get_snapshot()
                    if snap:
                        yield {"type": "todo", "items": snap}

            elif item.type == "tool_call_output_item":
                _completed_name = ""
                try:
                    call_id = getattr(item.raw_item, "call_id", None)
                    if call_id:
                        for prev in result.new_items:
                            if (hasattr(prev, "raw_item")
                                and getattr(prev.raw_item, "call_id", None) == call_id
                                and prev.type == "tool_call_item"):
                                _completed_name = getattr(prev.raw_item, "name", "")
                                break
                except Exception:
                    pass
                todo.on_tool_complete(_completed_name or "")
                snap = todo.get_snapshot()
                if snap:
                    yield {"type": "todo", "items": snap}

                out = _extract_tool_output_text(item.output)
                summary = brief_output_summary(out)
                if summary:
                    yield {"type": "status", "message": summary}
                if out.strip():
                    yield {"type": "tool_output", "output": out.strip()}
                # Track HITL-approved tool outputs for fallback display
                if approval_data and _completed_name in hitl_tools and out.strip():
                    state.hitl_tool_outputs.append(out.strip())
                if "[WEB_SEARCH]:" in out:
                    urls = re.findall(r"URL:\s*(https?://[^\s\n'\"]+)", out)
                    if urls:
                        yield {"type": "web_results", "urls": urls[:5]}
                # Emit chart artifacts immediately
                while len(ctx.chart_artifacts) > state.charts_emitted:
                    chart = ctx.chart_artifacts[state.charts_emitted]
                    state.charts_emitted += 1
                    yield {"type": "chart", "mermaid": chart}

            elif item.type == "message_output_item":
                if not state.content_streamed:
                    text_content = ItemHelpers.text_message_output(item)
                    if text_content:
                        clean = _strip_hallucinated_calls(text_content)
                        if clean.strip():
                            yield {"type": "final_answer", "message": clean}
                state.content_streamed = False  # reset for next turn
                while len(ctx.chart_artifacts) > state.charts_emitted:
                    chart = ctx.chart_artifacts[state.charts_emitted]
                    state.charts_emitted += 1
                    yield {"type": "chart", "mermaid": chart}

    # ── Streaming run ─────────────────────────────────────────────────────────

    async def run_streaming(
        self,
        user_message: str,
        hitl_decision: Optional[str] = None,  # "approve" or "reject" from frontend
    ) -> AsyncGenerator[Dict[str, Any], None]:
        try:
            await self._init()
            session = self._get_session()
            ctx     = self._new_context()

            # Session-scoped tracker (kept for explicit /todo commands only)
            todo = self._todo

            # Track HITL-approved tools for fallback display
            hitl_approved_tools: List[str] = []
            augmented_message = user_message

            if self._mcp_observer is None or self._mcp_operator is None:
                raise RuntimeError("MCP servers are not initialized")
            async with self._mcp_observer, self._mcp_operator:

                # ── HITL resume: if a previous run paused for approval, resume it ──
                approval_data = self._pending_approvals.pop(self.session_id, None)

                if approval_data and "todo_items" in approval_data:
                    todo.restore(approval_data["todo_items"])

                if approval_data:
                    run_state     = approval_data["state"]
                    interruptions = approval_data["interruptions"]

                    # Use explicit frontend HITL decision only (SDK-native flow).
                    if hitl_decision not in ("approve", "reject"):
                        self._pending_approvals[self.session_id] = {
                            "state": run_state,
                            "interruptions": list(interruptions),
                        }
                        actions = []
                        for item in interruptions:
                            name = getattr(item, "name", None) or getattr(item, "tool_name", "unknown")
                            raw_args = getattr(item, "arguments", None) or "{}"
                            try:
                                args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                            except Exception:
                                args = {}
                            args_str = ", ".join(f"{k}={v}" for k, v in args.items()) if args else ""
                            actions.append({
                                "tool": name,
                                "args": args,
                                "description": f"{name}({args_str})",
                            })

                        desc_list = ", ".join(a["description"] for a in actions)
                        yield {
                            "type": "final_answer",
                            "message": f"⚠️ **Pending approval:** {desc_list}\n\nPlease confirm or cancel.",
                        }
                        yield {"type": "done", "pending_actions": actions}
                        return

                    decision = hitl_decision
                    for item in interruptions:
                        name = getattr(item, "name", None) or getattr(item, "tool_name", "unknown")
                        if decision == "approve":
                            run_state.approve(item)
                            hitl_approved_tools.append(name)
                            logger.info(f"Approved: {name}")
                        else:
                            run_state.reject(item)
                            logger.info(f"Rejected: {name}")

                    # IMPORTANT: do NOT pass context= here — the RunState already
                    # carries the context with approval records. Passing a new context
                    # would override it and lose the approve/reject decisions.
                    result = Runner.run_streamed(
                        starting_agent=self.main_agent,
                        input=run_state,
                        session=session,
                        max_turns=30,
                    )
                    # Retrieve the context that the resumed run is using
                    ctx = run_state._context.context if run_state._context else ctx
                else:
                    augmented_message = user_message

                    result = Runner.run_streamed(
                        starting_agent=self.main_agent,
                        input=augmented_message,
                        session=session,
                        context=ctx,
                        max_turns=30,
                    )

                # ── Stream events with targeted 400 recovery ──
                stream_interrupted = False
                state = _StreamState()
                try:
                    async for ev in self._emit_stream_events(
                        result, state,
                        todo=todo, ctx=ctx,
                        approval_data=approval_data,
                        hitl_approved_tools=hitl_approved_tools,
                        augmented_message=augmented_message,
                    ):
                        yield ev

                except Exception as stream_exc:
                    exc_msg = str(stream_exc).lower()
                    is_malformed_history = (
                        "invalid tool call arguments" in exc_msg
                        or ("400" in exc_msg and hitl_approved_tools)
                    )
                    if is_malformed_history:
                        logger.warning(
                            f"Streaming interrupted after HITL (approved={hitl_approved_tools}): {stream_exc}"
                        )
                        stream_interrupted = True
                    else:
                        raise  # re-raise non-recoverable errors

                # ── Post-error recovery ──
                # Tool may have executed but Ollama rejected the next turn.
                # Collect outputs from partial run and report them.
                if stream_interrupted:
                    collected = []
                    try:
                        for new_item in result.new_items:
                            out = None
                            if hasattr(new_item, "output") and new_item.output:
                                out = _extract_tool_output_text(new_item.output)
                            elif hasattr(new_item, "raw_item"):
                                raw_out = getattr(new_item.raw_item, "output", None)
                                if raw_out:
                                    out = str(raw_out)
                            if out and out.strip():
                                collected.append(out)
                    except Exception:
                        pass

                    if collected:
                        yield {"type": "final_answer", "message": "\n\n".join(collected)}
                    elif not state.content_streamed:
                        # Nothing was shown to the user yet
                        yield {
                            "type": "final_answer",
                            "message": "⚠️ A technical issue occurred processing the response. Please try again.",
                        }

                    # Clear corrupted history to prevent recurring errors
                    try:
                        await self.clear_session()
                        logger.info("Session cleared after malformed-history recovery")
                    except Exception:
                        pass
                    yield {"type": "done", "pending_actions": []}
                    return

            # ── HITL: check if the run paused awaiting approval ──
            if result.interruptions:
                run_state = result.to_state()

                # Build pending-actions payload (same format the frontend expects)
                actions = []
                for item in result.interruptions:
                    name = getattr(item, "name", None) or getattr(item, "tool_name", "unknown")
                    raw_args = getattr(item, "arguments", None) or "{}"
                    try:
                        args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    except Exception:
                        args = {}
                    args_str = ", ".join(f"{k}={v}" for k, v in args.items()) if args else ""
                    full_desc = f"{name}({args_str})"
                    actions.append({
                        "tool": name,
                        "args": args,
                        "description": full_desc,
                    })

                # ── Auto-approve mode: approve and resume immediately ──
                if self.auto_approve:
                    desc_list_auto = ", ".join(a["description"][:60] for a in actions)
                    logger.info(f"[auto-approve] Approving: {desc_list_auto}")
                    yield {
                        "type": "status",
                        "message": f"✅ Auto-approved: {desc_list_auto[:100]}",
                    }
                    # Approve all interruptions and resume the streamed run
                    for item in result.interruptions:
                        run_state.approve(item)
                    resumed_result = Runner.run_streamed(
                        starting_agent=self.main_agent,
                        input=run_state,
                        session=session,
                        max_turns=100,
                    )
                    # Re-use the context from resumed state
                    ctx = run_state._context.context if run_state._context else ctx

                    # Stream the resumed run's events
                    async for event in resumed_result.stream_events():
                        if hasattr(event, 'type'):
                            if event.type == "raw_response_event":
                                delta = getattr(event.data, "delta", None) or ""
                                if delta:
                                    if not state.content_streamed:
                                        state.content_streamed = True
                                    yield {"type": "token", "content": delta}
                            elif event.type == "run_item_stream_event":
                                item_ev = event.item
                                from agents.types import (
                                    ToolCallItem, ToolCallOutputItem,
                                )
                                if isinstance(item_ev, ToolCallItem):
                                    t_name = getattr(item_ev, "raw_item", {}).get("name", "")
                                    t_args = getattr(item_ev, "raw_item", {}).get("arguments", "{}")
                                    try:
                                        t_parsed = json.loads(t_args) if isinstance(t_args, str) else t_args
                                    except Exception:
                                        t_parsed = {}
                                    yield {"type": "status", "message": format_tool_call(t_name, t_parsed)}
                                elif isinstance(item_ev, ToolCallOutputItem):
                                    out = getattr(item_ev, "output", "")
                                    if out:
                                        state.hitl_tool_outputs.append(out)
                                        summary = brief_output_summary(out)
                                        if summary:
                                            yield {"type": "status", "message": summary}

                    # Check if there are MORE interruptions after resume
                    final_result = resumed_result
                    while final_result.interruptions:
                        chained_state = final_result.to_state()
                        for chained_item in final_result.interruptions:
                            c_name = getattr(chained_item, "name", None) or "unknown"
                            logger.info(f"[auto-approve] Chained: {c_name}")
                            yield {"type": "status", "message": f"✅ Auto-approved: {c_name}"}
                            chained_state.approve(chained_item)
                        final_result = Runner.run_streamed(
                            starting_agent=self.main_agent,
                            input=chained_state,
                            session=session,
                            max_turns=100,
                        )
                        async for event in final_result.stream_events():
                            if hasattr(event, 'type') and event.type == "raw_response_event":
                                delta = getattr(event.data, "delta", None) or ""
                                if delta:
                                    state.content_streamed = True
                                    yield {"type": "token", "content": delta}

                    # Done — show final output
                    if not state.content_streamed and state.hitl_tool_outputs:
                        yield {
                            "type": "final_answer",
                            "message": "\n\n".join(state.hitl_tool_outputs),
                        }
                    try:
                        await self._compact_session()
                    except Exception as e:
                        logger.warning(f"Session compaction failed: {e}")
                    yield {"type": "done", "pending_actions": []}
                else:
                    # ── Normal HITL: pause and ask user ──
                    self._pending_approvals[self.session_id] = {
                        "state": run_state,
                        "interruptions": list(result.interruptions),
                    }

                    # Build a readable summary — truncate long arg lists
                    def _short(desc):
                        if len(desc) <= 80:
                            return desc
                        import re as _re
                        m = _re.match(r'(\w+)\((.+)\)$', desc, _re.DOTALL)
                        if not m:
                            return desc[:77] + "…"
                        tool, args_str = m.group(1), m.group(2)
                        # Split on commas that precede a `word=` (top-level arg boundaries)
                        parts = _re.split(r',\s*(?=\w+=)', args_str)
                        if len(parts) == 1:
                            # Single-arg tool — check if value is a list
                            key_m = _re.match(r'(\w+)=(\[.+\])$', parts[0], _re.DOTALL)
                            if key_m:
                                items = _re.findall(r'\{[^}]+\}', key_m.group(2))
                                if len(items) > 2:
                                    return f"{tool}({key_m.group(1)}: {len(items)} items)"
                            return f"{tool}({parts[0][:70]}…)"
                        # Multi-arg tool — show first 2 args in full, then "…"
                        shown = ", ".join(parts[:2])
                        if len(parts) > 2:
                            shown += ", …"
                        if len(shown) > 77:
                            shown = shown[:74] + "…"
                        return f"{tool}({shown})"

                    desc_list = ", ".join(_short(a["description"]) for a in actions)
                    yield {
                        "type": "final_answer",
                        "message": f"⚠️ **Pending approval:** {desc_list}\n\nPlease confirm or cancel.",
                    }
                    yield {"type": "done", "pending_actions": actions}
            else:
                # ── HITL fallback: if the Operator didn't generate a text
                # response after executing approved tools, show the tool
                # outputs as the main response so the user sees the result.
                if not state.content_streamed and state.hitl_tool_outputs:
                    yield {
                        "type": "final_answer",
                        "message": "\n\n".join(state.hitl_tool_outputs),
                    }

                # Compact session in background (don't block the response)
                try:
                    await self._compact_session()
                except Exception as e:
                    logger.warning(f"Session compaction failed: {e}")
                yield {"type": "done", "pending_actions": []}

        except Exception as exc:
            logger.error(f"Streaming error: {exc}", exc_info=True)
            msg = str(exc)
            if "Invalid JSON" in msg:
                msg = "Technical issue with the response. Please rephrase."
            yield {"type": "error", "message": msg}

    # ── Non-streaming run ─────────────────────────────────────────────────────

    async def run(self, user_message: str) -> Dict[str, Any]:
        try:
            await self._init()
            session = self._get_session()
            ctx     = self._new_context()

            if self._mcp_observer is None or self._mcp_operator is None:
                raise RuntimeError("MCP servers are not initialized")
            async with self._mcp_observer, self._mcp_operator:
                result = await Runner.run(
                    starting_agent=self.main_agent,
                    input=user_message,
                    session=session,
                    context=ctx,
                    max_turns=100,
                )
                final = str(result.final_output)
                charts = [_wrap_mermaid(c) for c in ctx.chart_artifacts]

                pending = []
                if result.interruptions:
                    state = result.to_state()
                    self._pending_approvals[self.session_id] = {
                        "state": state,
                        "interruptions": list(result.interruptions),
                    }
                    for item in result.interruptions:
                        name = getattr(item, "name", None) or getattr(item, "tool_name", "unknown")
                        raw_args = getattr(item, "arguments", None) or "{}"
                        try:
                            args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                        except Exception:
                            args = {}
                        args_str = ", ".join(f"{k}={v}" for k, v in args.items()) if args else ""
                        pending.append({"tool": name, "args": args, "description": f"{name}({args_str})"})

                if not pending:
                    try:
                        await self._compact_session()
                    except Exception as e:
                        logger.warning(f"Session compaction failed: {e}")

                return {"success": True, "message": final, "charts": charts, "pending_actions": pending}

        except Exception as exc:
            logger.error(f"Run error: {exc}", exc_info=True)
            return {"success": False, "message": str(exc)}

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def clear_session(self):
        if self._session:
            await self._session.clear_session()
            logger.info(f"Session cleared: {self.session_id}")

    async def disconnect(self):
        self._mcp_observer = None
        self._mcp_operator = None
        self._session = None
        self._ready = False

    async def __aenter__(self):
        await self._init()
        return self

    async def __aexit__(self, *_):
        await self.disconnect()


# ── Private helpers ───────────────────────────────────────────────────────────


def _normalize_tool_name(name: str) -> str:
    norm = re.sub(r"[^a-z0-9_]+", "_", (name or "").strip().lower()).strip("_")
    norm = norm.replace("scontrol_hold_job", "scontrol_hold")
    norm = norm.replace("scontrol_release_job", "scontrol_release")
    norm = norm.replace("scontrol_requeue_job", "scontrol_requeue")
    return norm


def _extract_tool_output_text(output) -> str:
    """Extract plain text from tool output, which may be str, list of dicts, or other."""
    if output is None:
        return ""
    if isinstance(output, str):
        # SDK may stringify MCP response: "[{'type': 'text', 'text': '...'}]"
        # or "{'type': 'text', 'text': '...'}"  — unwrap to get the actual text.
        return _unwrap_mcp_text(output)
    # MCP tools return list[TextContent | ImageContent | dict]
    if isinstance(output, list):
        parts = []
        for item in output:
            if isinstance(item, dict):
                parts.append(item.get("text", ""))
            elif hasattr(item, "text"):
                parts.append(str(item.text))
            else:
                s = str(item)
                parts.append(_unwrap_mcp_text(s))
        return "\n".join(p for p in parts if p)
    if hasattr(output, "text"):
        return str(output.text)
    return _unwrap_mcp_text(str(output))


# Regex to extract text from stringified MCP response wrappers like:
#   {'type': 'text', 'text': '...'} or {"type": "text", "text": "..."}
_MCP_WRAPPER_RE = re.compile(
    r"""[{\[]\s*['"]type['"]\s*:\s*['"]text['"]\s*,\s*['"]text['"]\s*:\s*['"]""",
)


def _unwrap_mcp_text(s: str) -> str:
    """If s looks like a stringified MCP TextContent wrapper, extract the text."""
    stripped = s.strip()
    if not _MCP_WRAPPER_RE.search(stripped):
        return s
    # Safe parse: try json first, then ast.literal_eval
    try:
        import ast
        parsed = ast.literal_eval(stripped)
        if isinstance(parsed, list):
            texts = [item.get("text", "") for item in parsed if isinstance(item, dict)]
            return "\n".join(t for t in texts if t) or s
        if isinstance(parsed, dict):
            return parsed.get("text", s)
    except Exception:
        pass
    return s


def _strip_hallucinated_calls(text: str) -> str:
    text = re.sub(r"<function=[^>]*>.*?</tool_call>", "", text, flags=re.DOTALL)
    text = re.sub(r"</?function[^>]*>", "", text)
    text = re.sub(r"</?parameter[^>]*>", "", text)
    text = re.sub(r"</?tool_call>", "", text)
    return text.strip()


def _wrap_mermaid(code: str) -> str:
    return f"\n\n```mermaid\n{code}\n```"
