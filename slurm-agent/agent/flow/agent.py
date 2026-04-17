"""
SlurmAgentSystem — two-agent handoff orchestrator.

Architecture:
  Observer  — entry point, all read-only MCP tools + charts + skills
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
from agents.mcp import MCPServerSse, ToolFilterContext

# ── Monkey-patch: fix malformed tool call arguments from Ollama streaming ─────
# Ollama/gemma4 sometimes streams the same JSON fragment multiple times
# (e.g., '{}{}{}' instead of '{}'), which the SDK concatenates verbatim.
# This causes 400 "invalid tool call arguments" on the next turn and
# "Extra data" parse errors when the SDK invokes MCP tools.
#
# We patch two SDK sites:
# 1. Converter.items_to_messages — fixes history replay to the model
# 2. MCPUtil.invoke_mcp_tool — fixes tool invocation with bad args

def _sanitize_json_args(raw: str) -> str:
    """Extract the first valid JSON object from potentially concatenated duplicates."""
    if not raw or not isinstance(raw, str):
        return raw
    raw = raw.strip()
    if not raw:
        return "{}"
    try:
        json.loads(raw)
        return raw
    except (json.JSONDecodeError, ValueError):
        pass
    if raw.startswith("{"):
        depth = 0
        for i, ch in enumerate(raw):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = raw[: i + 1]
                    try:
                        json.loads(candidate)
                        return candidate
                    except (json.JSONDecodeError, ValueError):
                        break
    return "{}"


def _patch_sdk_for_ollama():
    # Patch 1: Converter — sanitize arguments in history messages
    from agents.models.chatcmpl_converter import Converter
    _orig_items_to_messages = Converter.items_to_messages.__func__

    @classmethod
    def _patched_items_to_messages(cls, *args, **kwargs):
        messages = _orig_items_to_messages(cls, *args, **kwargs)
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            for tc in msg.get("tool_calls", []):
                fn = tc.get("function", {})
                raw = fn.get("arguments", "")
                if raw and isinstance(raw, str):
                    fn["arguments"] = _sanitize_json_args(raw)
        return messages

    Converter.items_to_messages = _patched_items_to_messages

    # Patch 2: MCPUtil.invoke_mcp_tool — sanitize arguments before JSON parse
    from agents.mcp.util import MCPUtil
    _orig_invoke = MCPUtil.invoke_mcp_tool.__func__

    @classmethod
    async def _patched_invoke_mcp_tool(cls, server, tool, context, input_json, **kwargs):
        if input_json and isinstance(input_json, str):
            input_json = _sanitize_json_args(input_json)
        return await _orig_invoke(cls, server, tool, context, input_json, **kwargs)

    MCPUtil.invoke_mcp_tool = _patched_invoke_mcp_tool

_patch_sdk_for_ollama()

from .context import ChartFilteredSession, SlurmContext
from .guardrails import guard_job_id  # imported so the guardrail registry is populated
from .instructions import (
    build_observer_instructions,
    build_operator_instructions,
    brief_output_summary,
    format_tool_call,
)
from .model import (
    ACTIVE_MODEL_SETTINGS,
    DEFAULT_MODEL,
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    resolve_model,
)
from .skills import (
    format_skills_for_instructions,
    load_observer_skills,
    load_operator_skills,
)
from .todo import TodoTracker
from .tool_discovery import ToolCatalog, discover_tools
from .tools import (
    make_chart_tool,
    make_guarded_dangerous_tools,
    make_manage_todos_tool,
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
_OPERATOR_READ_TOOLS = {"scontrol_show", "cluster_resources"}


class SlurmAgentSystem:
    """
    Two-agent handoff system for Slurm HPC clusters.

    Observer (entry point):
        Read-only MCP tools (analysis + safe) + chart FunctionTool + skills.
        Handles monitoring, diagnosis, and analysis. Hands off to Operator
        when an action is required.

    Operator:
        Dangerous FunctionTools with needs_approval=True (HITL).
        Plus squeue / scontrol_show via MCP for pre-action verification.
        Hands off back to Observer for further investigation.

    First call to run_streaming / run performs lazy init:
      1. discover_tools() — one HTTP call to MCP, builds ToolCatalog
      2. Loads skills from agent/skills/*.md
      3. Builds Observer + Operator agents with bidirectional handoffs
    """

    def __init__(
        self,
        reasoning_model: str = DEFAULT_MODEL,
        tool_model: str = DEFAULT_MODEL,
        base_url: str = OLLAMA_BASE_URL,
        mcp_url: str = "http://localhost:3002",
        session_id: str = "default",
        auto_approve: bool = False,
    ):
        self.mcp_url      = mcp_url
        self.session_id   = session_id
        self.auto_approve = auto_approve

        self._reasoning_model = resolve_model(reasoning_model)

        self._session: Optional[ChartFilteredSession] = None
        self._mcp_observer: Optional[MCPServerSse]    = None
        self._mcp_operator: Optional[MCPServerSse]    = None

        self.main_agent      = None   # entry-point agent (Observer)
        self._catalog: Optional[ToolCatalog] = None
        self._ready          = False

        # Session-scoped task plan
        self._todo = TodoTracker()

        # HITL: store RunState + interruptions between requests for approval flow
        self._pending_approvals: Dict[str, dict] = {}

    # ── Initialisation ─────────────────────────────────────────────────────────

    async def _init(self):
        if self._ready:
            return

        logger.info(f"[SlurmAgentSystem] Initialising (session={self.session_id})")

        # 1. Discover tools — fetch live schemas, classify
        self._catalog = await discover_tools(self.mcp_url)

        # 2. Load skills — separate sets per agent for efficiency
        observer_skills = load_observer_skills()
        operator_skills = load_operator_skills()
        observer_instructions = build_observer_instructions(format_skills_for_instructions(observer_skills))
        operator_instructions = build_operator_instructions(format_skills_for_instructions(operator_skills))

        # 3. MCP servers — Observer gets all read-only tools; Operator gets a small read subset
        observer_mcp_names = self._catalog.analysis_names | self._catalog.safe_names
        self._mcp_observer = _make_mcp_server(self.mcp_url, observer_mcp_names, "slurm-observer-mcp")

        operator_read_names = _OPERATOR_READ_TOOLS & (self._catalog.analysis_names | self._catalog.safe_names)
        self._mcp_operator = _make_mcp_server(self.mcp_url, operator_read_names, "slurm-operator-mcp")

        # 4. Guarded dangerous FunctionTools (HITL: needs_approval=True)
        dangerous_fns = make_guarded_dangerous_tools(self.mcp_url, self._catalog.dangerous)

        # 5. Chart tool — discover valid IDs from MCP-provided schema enum
        viz_tool = self._catalog.by_name("generate_chart")
        if viz_tool:
            chart_id_schema = viz_tool.schema.get("properties", {}).get("chart_id", {})
            valid_chart_ids = set(chart_id_schema.get("enum", []))
        else:
            valid_chart_ids = set()
        if not valid_chart_ids:
            valid_chart_ids = {
                "system_health", "cluster_topology", "pending_analysis",
                "resource_map", "job_lifecycle",
            }
        chart_tool = make_chart_tool(self.mcp_url, valid_chart_ids)

        # 5b. Skill lookup tools — per agent, scoped to their own skill set
        skill_lookup_tool = make_skill_lookup_tool(observer_skills)
        operator_skill_lookup_tool = make_skill_lookup_tool(operator_skills) if operator_skills else None

        # 5c. Shared todo management tool (same instance, both agents share the tracker)
        manage_todos_tool = make_manage_todos_tool(self._todo)

        # 6. Build agents with bidirectional handoffs
        #    Create agents first (no handoffs), then wire handoffs after both exist.
        observer = Agent(
            name="Observer",
            instructions=observer_instructions,
            model=self._reasoning_model,
            model_settings=ACTIVE_MODEL_SETTINGS,
            mcp_servers=[self._mcp_observer],
            tools=[chart_tool, skill_lookup_tool, manage_todos_tool],
            handoffs=[],  # filled below
        )

        operator = Agent(
            name="Operator",
            instructions=operator_instructions,
            model=self._reasoning_model,
            model_settings=ACTIVE_MODEL_SETTINGS,
            mcp_servers=[self._mcp_operator],
            tools=dangerous_fns + ([operator_skill_lookup_tool] if operator_skill_lookup_tool else []) + [manage_todos_tool],
            handoffs=[],  # filled below
        )

        # Wire bidirectional handoffs
        observer.handoffs = [
            handoff(
                operator,
                tool_name_override="transfer_to_operator",
                tool_description_override=(
                    "Hand off to the Operator to EXECUTE actions that modify the cluster. "
                    "Your message to the Operator is its instruction — state the action "
                    "and list ALL targets (file paths, job IDs). "
                    "The Operator will call the tools and report results."
                ),
            ),
        ]
        # Guard: Operator can only hand back AFTER executing at least one action.
        # is_enabled hides transfer_to_observer until an action tool has fired,
        # forcing the model to use sbatch/scancel/etc. first.
        def _operator_handoff_enabled(ctx, _agent) -> bool:
            slurm_ctx = ctx.context if hasattr(ctx, 'context') else None
            if slurm_ctx and hasattr(slurm_ctx, 'operator_actions_taken'):
                return slurm_ctx.operator_actions_taken > 0
            return True  # fallback: allow if context is unavailable

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
            ),
        ]

        self.main_agent = observer  # entry point

        self._ready = True
        obs_tools = len(observer_mcp_names) + 2 + 1   # MCP + (chart, skill_lookup) + handoff
        op_tools  = len(dangerous_fns) + len(operator_read_names) + 1 + (1 if operator_skill_lookup_tool else 0)
        logger.info(
            f"[SlurmAgentSystem] Ready — "
            f"Observer tools≈{obs_tools} Operator tools≈{op_tools} "
            f"observer_skills={len(observer_skills)} operator_skills={len(operator_skills)}"
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
            if LLM_PROVIDER == "copilot":
                from .model import GITHUB_TOKEN, COPILOT_BASE_URL, COPILOT_MODEL
                client = AsyncOpenAI(base_url=COPILOT_BASE_URL, api_key=GITHUB_TOKEN)
                _model = COPILOT_MODEL
                _extra: dict = {}
            else:
                client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
                _model = DEFAULT_MODEL
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

    # ── HITL approval helpers ────────────────────────────────────────────────

    @staticmethod
    async def _classify_approval_llm(text: str) -> str:
        """Classify user intent as 'approve', 'reject', or 'new_instruction'.

        'new_instruction' means the user sent a completely different request
        while a HITL prompt was pending — the pending action should be dropped
        and the new message handled as a fresh input.
        """
        from openai import AsyncOpenAI
        try:
            if LLM_PROVIDER == "copilot":
                from .model import GITHUB_TOKEN, COPILOT_BASE_URL, COPILOT_MODEL
                client = AsyncOpenAI(base_url=COPILOT_BASE_URL, api_key=GITHUB_TOKEN)
                _model = COPILOT_MODEL
                _extra2: dict = {}
            else:
                client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
                _model = DEFAULT_MODEL
                _extra2 = {"think": False}
            resp = await client.chat.completions.create(
                model=_model,
                messages=[
                    {"role": "system", "content": (
                        "A Slurm HPC assistant is waiting for the user to approve or reject a pending action. "
                        "Classify the user's message as EXACTLY one of three words:\n"
                        "  approve — the user confirms the action (yes, ok, confirm, do it, go ahead, etc.)\n"
                        "  reject  — the user cancels the action (no, cancel, stop, don't, abort, etc.)\n"
                        "  new_instruction — the user is asking something unrelated or giving a brand-new command "
                        "                    instead of responding to the approval prompt\n"
                        "Output EXACTLY one word. Nothing else."
                    )},
                    {"role": "user", "content": text},
                ],
                temperature=0,
                max_tokens=10,
                **(({"extra_body": _extra2}) if _extra2 else {}),
            )
            answer = (resp.choices[0].message.content or "").strip().lower()
            if "approve" in answer:
                return "approve"
            if "new_instruction" in answer or "new instruction" in answer:
                return "new_instruction"
            return "reject"  # safe default
        except Exception as e:
            logger.warning(f"LLM approval classification failed: {e}")
            return "reject"  # safe default: don't execute without clear confirmation

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
        conversation_history: Optional[list] = None,  # API compat, unused
        hitl_decision: Optional[str] = None,  # "approve" or "reject" from frontend
    ) -> AsyncGenerator[Dict[str, Any], None]:
        try:
            await self._init()
            self._hallucination_retries = 0  # reset per request
            session = self._get_session()
            ctx     = self._new_context()

            # Session-scoped plan tracker
            todo = self._todo

            # Track HITL-approved tools for better error recovery
            hitl_approved_tools: List[str] = []

            async with self._mcp_observer, self._mcp_operator:

                # ── HITL resume: if a previous run paused for approval, resume it ──
                approval_data = self._pending_approvals.pop(self.session_id, None)

                # ── Todo tracking ──
                if approval_data and "todo_items" in approval_data:
                    # Restore plan saved before HITL pause
                    todo.restore(approval_data["todo_items"])
                    snap = todo.get_items()
                    if snap:
                        yield {"type": "todo", "items": snap}
                elif not approval_data and not todo.has_active_plan:
                    # Only generate a new plan if there's no active one in progress
                    await todo.generate_plan(user_message)
                    plan_snapshot = todo.get_snapshot()
                    if plan_snapshot:
                        yield {"type": "todo", "items": plan_snapshot}
                elif not approval_data and todo.has_active_plan:
                    # Existing plan still in progress — send current state to frontend
                    snap = todo.get_items()
                    if snap:
                        yield {"type": "todo", "items": snap}

                if approval_data:
                    run_state     = approval_data["state"]
                    interruptions = approval_data["interruptions"]

                    # Use structured decision from frontend buttons if available;
                    # otherwise fall back to LLM classification of free-text
                    if hitl_decision in ("approve", "reject"):
                        decision = hitl_decision
                    else:
                        decision = await self._classify_approval_llm(user_message)

                    # ── New instruction while HITL was pending ────────────────
                    # User sent a brand-new request instead of approving/rejecting.
                    # Drop the pending action entirely and handle the new message
                    # as a fresh run so the user isn't stuck in the approval loop.
                    if decision == "new_instruction":
                        logger.info("HITL: new instruction detected — discarding pending action, starting fresh")
                        todo.reset()
                        approval_data = None
                        await todo.generate_plan(user_message)
                        plan_snapshot = todo.get_snapshot()
                        if plan_snapshot:
                            yield {"type": "todo", "items": plan_snapshot}
                        plan_text = todo.format_for_llm()
                        augmented_message = f"{user_message}\n\n{plan_text}" if plan_text else user_message
                        result = Runner.run_streamed(
                            starting_agent=self.main_agent,
                            input=augmented_message,
                            session=session,
                            context=ctx,
                            max_turns=30,
                        )
                    else:
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
                    # Inject plan into the message so the LLM follows it
                    plan_text = todo.format_for_llm()
                    augmented_message = f"{user_message}\n\n{plan_text}" if plan_text else user_message

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
                    ):
                        yield ev

                except Exception as stream_exc:
                    exc_msg = str(stream_exc).lower()
                    is_malformed_history = (
                        "invalid tool call arguments" in exc_msg
                        or ("400" in exc_msg and hitl_approved_tools)
                    )
                    is_tool_not_found = "not found in agent" in exc_msg

                    if is_tool_not_found:
                        # Model called a tool on the wrong agent — retry with a nudge
                        logger.warning(f"Tool not found on agent: {stream_exc}")
                        bad_tool = ""
                        bad_agent = ""
                        import re as _re
                        m = _re.search(r"Tool (\S+) not found in agent (\S+)", str(stream_exc))
                        if m:
                            bad_tool = m.group(1)
                            bad_agent = m.group(2)

                        # Determine if the tool exists on a different agent (cross-agent error)
                        observer_tools = {"squeue", "sinfo", "sacct", "sshare", "sprio",
                                          "sstat", "sacctmgr_list", "sdiag", "scontrol_show",
                                          "run_analysis", "generate_chart", "lookup_skill"}
                        is_cross_agent = bad_tool in observer_tools and bad_agent == "Operator"

                        if not hasattr(self, '_hallucination_retries'):
                            self._hallucination_retries = 0

                        if self._hallucination_retries < 1:
                            self._hallucination_retries += 1
                            try:
                                await self.clear_session()
                            except Exception:
                                pass
                            if is_cross_agent:
                                nudge = (
                                    f"[SYSTEM: The Operator tried to call '{bad_tool}' which is an Observer-only tool. "
                                    f"The action has already completed successfully. "
                                    f"Report the results to the user. Do NOT call '{bad_tool}'.]\n\n"
                                )
                            else:
                                nudge = (
                                    f"[SYSTEM: You called '{bad_tool}' which does not exist on {bad_agent}. "
                                    f"Use only the tools listed in your instructions.]\n\n"
                                ) if bad_tool else ""
                            retry_input = nudge + (augmented_message if not approval_data else user_message)
                            logger.info(f"Retrying after tool-not-found: tool={bad_tool} agent={bad_agent} cross_agent={is_cross_agent}")
                            yield {"type": "status", "message": f"Retrying ('{bad_tool}' is not available)…"}

                            ctx = self._new_context()
                            result = Runner.run_streamed(
                                starting_agent=self.main_agent,
                                input=retry_input,
                                session=session,
                                context=ctx,
                                max_turns=30,
                            )
                            state = _StreamState()
                            try:
                                async for ev in self._emit_stream_events(
                                    result, state, todo=todo, ctx=ctx,
                                ):
                                    yield ev
                            except Exception as retry_exc:
                                logger.warning(f"Retry also failed: {retry_exc}")
                                yield {
                                    "type": "final_answer",
                                    "message": "I encountered a technical issue. Please try rephrasing your request.",
                                }
                                try:
                                    await self.clear_session()
                                except Exception:
                                    pass
                                yield {"type": "done", "pending_actions": []}
                                return
                        else:
                            # Already retried once — give up
                            yield {
                                "type": "final_answer",
                                "message": "I couldn't complete the request after retrying. Please try rephrasing.",
                            }
                            try:
                                await self.clear_session()
                            except Exception:
                                pass
                            yield {"type": "done", "pending_actions": []}
                            return
                    elif is_malformed_history:
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
                                    HandoffCallItem, HandoffOutputItem,
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
                    todo.on_done()
                    snap = todo.get_snapshot()
                    if snap:
                        yield {"type": "todo", "items": snap}
                    yield {"type": "done", "pending_actions": []}
                else:
                    # ── Normal HITL: pause and ask user ──
                    self._pending_approvals[self.session_id] = {
                        "state": run_state,
                        "interruptions": list(result.interruptions),
                        "todo_items": todo.get_items(),
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
                    # Don't mark everything done — leave the action step as in-progress
                    # so the spinner shows while the user decides to approve/reject.
                    snap = todo.get_items()
                    if snap:
                        yield {"type": "todo", "items": snap}
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
                todo.on_done()
                snap = todo.get_snapshot()
                if snap:
                    yield {"type": "todo", "items": snap}
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
