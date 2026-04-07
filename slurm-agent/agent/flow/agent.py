"""
SlurmAgentSystem — thin orchestrator.

Wires together context, model, instructions, tool_discovery, and tools into
a runnable agent system.  No schemas or business-logic live here.
"""
import json
import logging
import re
from typing import Any, AsyncGenerator, Dict, List, Optional

from agents import Agent, Runner, SQLiteSession, ItemHelpers
from agents.mcp import MCPServerSse, ToolFilterContext

from .context import ChartFilteredSession, SlurmContext
from .guardrails import guard_job_id  # imported so the guardrail registry is populated
from .instructions import (
    ACTION_SUBAGENT_INSTRUCTIONS,
    ANALYSIS_SUBAGENT_INSTRUCTIONS,
    MAIN_AGENT_INSTRUCTIONS,
    brief_output_summary,
    format_tool_call,
)
from .model import (
    REASONING_MODEL_SETTINGS,
    TOOL_MODEL_SETTINGS,
    create_ollama_model,
    extract_subagent_output,
    make_web_search_handler,
)
from .tool_discovery import ToolCatalog, discover_tools
from .tools import (
    make_cancel_tool,
    make_chart_tool,
    make_check_pending_tool,
    make_confirm_tool,
    make_guarded_dangerous_tools,
)

logger = logging.getLogger(__name__)


def _make_mcp_server(mcp_url: str, allowed: set[str]) -> MCPServerSse:
    """Create a filtered MCP-SSE server."""
    async def _filter(ctx: ToolFilterContext, tool) -> bool:
        return tool.name in allowed

    return MCPServerSse(
        params={
            "url": f"{mcp_url.rstrip('/')}/sse",
            "timeout": 60,
            "sse_read_timeout": 600,
        },
        name="slurm-mcp",
        client_session_timeout_seconds=300,
        cache_tools_list=True,
        tool_filter=_filter,
    )


class SlurmAgentSystem:
    """
    Main ReAct agent with two sub-agents (analysis + action) exposed as tools.

    First call to run_streaming / run performs:
      1. discover_tools()  — one HTTP call to MCP, builds ToolCatalog with live schemas
      2. Builds guarded FunctionTools for dangerous tools from discovered schemas
      3. Initialises sub-agents and main agent
    """

    def __init__(
        self,
        reasoning_model: str = "gemma4:e4b",
        tool_model: str = "gemma4:e4b",
        base_url: str = "http://localhost:11434/v1",
        mcp_url: str = "http://localhost:3002",
        session_id: str = "default",
    ):
        self.mcp_url      = mcp_url
        self.session_id   = session_id

        self._reasoning_model = create_ollama_model(reasoning_model, base_url)
        self._tool_model      = create_ollama_model(tool_model, base_url)

        self._session: Optional[ChartFilteredSession] = None
        self._analysis_mcp: Optional[MCPServerSse]    = None
        self._action_mcp: Optional[MCPServerSse]       = None

        self.main_agent      = None
        self._catalog: Optional[ToolCatalog] = None
        self._ready          = False

    # ── Initialisation ─────────────────────────────────────────────────────────

    async def _init(self):
        if self._ready:
            return

        logger.info(f"[SlurmAgentSystem] Initialising (session={self.session_id})")

        # 1. Discover tools — fetch live schemas, classify
        self._catalog = await discover_tools(self.mcp_url)

        # 2. MCP servers with filtered tool lists
        self._analysis_mcp = _make_mcp_server(self.mcp_url, self._catalog.analysis_names)
        # action MCP carries only safe tools; dangerous tools are FunctionTools that queue
        self._action_mcp   = _make_mcp_server(self.mcp_url, self._catalog.safe_names)

        # 3. Guarded dangerous FunctionTools built from live schemas
        dangerous_fns = make_guarded_dangerous_tools(self._catalog.dangerous)

        # 4. Chart tool — discover valid IDs from the MCP-provided schema enum
        viz_tool = self._catalog.by_name("generate_chart")
        if viz_tool:
            chart_id_schema = viz_tool.schema.get("properties", {}).get("chart_id", {})
            valid_chart_ids = set(chart_id_schema.get("enum", []))
        else:
            valid_chart_ids = set()
        if not valid_chart_ids:
            # Fallback if schema has no enum (older server)
            valid_chart_ids = {
                "system_health", "cluster_topology", "pending_analysis",
                "resource_map", "job_lifecycle",
            }
        chart_tool = make_chart_tool(self.mcp_url, valid_chart_ids)

        # 5. Sub-agents
        analysis_agent = Agent(
            name="Analysis Sub-Agent",
            instructions=ANALYSIS_SUBAGENT_INSTRUCTIONS,
            model=self._tool_model,
            model_settings=TOOL_MODEL_SETTINGS,
            mcp_servers=[self._analysis_mcp],
            tool_use_behavior=make_web_search_handler(),
        )

        action_agent = Agent(
            name="Action Sub-Agent",
            instructions=ACTION_SUBAGENT_INSTRUCTIONS,
            model=self._tool_model,
            model_settings=TOOL_MODEL_SETTINGS,
            mcp_servers=[self._action_mcp],
            tools=dangerous_fns,
        )

        # 6. Wrap sub-agents as tools
        analyze_tool = analysis_agent.as_tool(
            tool_name="analyze_cluster",
            tool_description=(
                "Gather raw cluster data: job status, queue info, node status, web search. "
                "Pass a description of what data is needed."
            ),
            custom_output_extractor=extract_subagent_output,
        )
        action_tool = action_agent.as_tool(
            tool_name="manage_jobs",
            tool_description=(
                "Execute job actions: cancel, hold, release, update, submit. "
                "Pass a description of the action."
            ),
            custom_output_extractor=extract_subagent_output,
        )

        # 7. Orchestration tools
        confirm_tool       = make_confirm_tool(self.mcp_url)
        cancel_tool        = make_cancel_tool()
        check_pending_tool = make_check_pending_tool()

        all_tools = [
            analyze_tool, action_tool,
            confirm_tool, cancel_tool, check_pending_tool,
            chart_tool,
        ]

        # 8. Main agent
        self.main_agent = Agent(
            name="Slurm Assistant",
            instructions=MAIN_AGENT_INSTRUCTIONS,
            model=self._reasoning_model,
            model_settings=REASONING_MODEL_SETTINGS,
            tools=all_tools,
        )

        self._ready = True
        logger.info(
            f"[SlurmAgentSystem] Ready — "
            f"analysis={len(self._catalog.analysis)} "
            f"safe={len(self._catalog.safe)} "
            f"dangerous={len(self._catalog.dangerous)} "
            f"tools on main agent={len(all_tools)}"
        )

    # ── Session ───────────────────────────────────────────────────────────────

    def _get_session(self) -> ChartFilteredSession:
        if self._session is None:
            raw = SQLiteSession(self.session_id, "/tmp/slurm_agent_conversations.db")
            self._session = ChartFilteredSession(raw)
        return self._session

    def _new_context(self) -> SlurmContext:
        return SlurmContext(session_id=self.session_id)

    # ── Streaming run ─────────────────────────────────────────────────────────

    async def run_streaming(
        self,
        user_message: str,
        conversation_history: Optional[list] = None,  # API compat, unused
    ) -> AsyncGenerator[Dict[str, Any], None]:
        try:
            await self._init()
            session = self._get_session()
            ctx     = self._new_context()

            async with self._analysis_mcp, self._action_mcp:
                result = Runner.run_streamed(
                    starting_agent=self.main_agent,
                    input=user_message,
                    session=session,
                    context=ctx,
                )

                async for event in result.stream_events():

                    # Real model reasoning tokens
                    # Ollama gemma4: delta.thinking
                    # Other providers: delta.reasoning / delta.reasoning_content
                    if event.type == "raw_response_event":
                        try:
                            d = event.data.choices[0].delta
                            r = (
                                getattr(d, "thinking", None)
                                or getattr(d, "reasoning", None)
                                or getattr(d, "reasoning_content", None)
                            )
                            if r:
                                yield {"type": "thinking", "content": r}
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

                    elif item.type == "tool_call_output_item":
                        out = str(item.output or "")
                        summary = brief_output_summary(out)
                        if summary:
                            yield {"type": "status", "message": summary}
                        if "[WEB_SEARCH]:" in out:
                            urls = re.findall(r"URL:\s*(https?://[^\s\n'\"]+)", out)
                            if urls:
                                yield {"type": "web_results", "urls": urls[:5]}

                    elif item.type == "message_output_item":
                        content = ItemHelpers.text_message_output(item)
                        if content:
                            clean = _strip_hallucinated_calls(content)
                            if clean.strip():
                                full = clean
                                for chart in ctx.chart_artifacts:
                                    full += _wrap_mermaid(chart)
                                yield {"type": "final_answer", "message": full}

            yield {"type": "done", "pending_actions": ctx.get_pending_actions()}

        except Exception as exc:
            logger.error(f"Streaming error: {exc}", exc_info=True)
            msg = str(exc)
            if "invalid tool call arguments" in msg.lower():
                try:
                    await self.clear_session()
                    msg = "Memory cleared due to a hiccup — please retry."
                except Exception:
                    msg = "Encountered an issue. Please start a new conversation."
            elif "Invalid JSON" in msg:
                msg = "Technical issue with the response. Please rephrase."
            yield {"type": "error", "message": msg}

    # ── Non-streaming run ─────────────────────────────────────────────────────

    async def run(self, user_message: str) -> Dict[str, Any]:
        try:
            await self._init()
            session = self._get_session()
            ctx     = self._new_context()

            async with self._analysis_mcp, self._action_mcp:
                result = await Runner.run(
                    starting_agent=self.main_agent,
                    input=user_message,
                    session=session,
                    context=ctx,
                    max_turns=100,
                )
                final = str(result.final_output)
                for chart in ctx.chart_artifacts:
                    final += _wrap_mermaid(chart)
                return {"success": True, "message": final, "pending_actions": ctx.get_pending_actions()}

        except Exception as exc:
            logger.error(f"Run error: {exc}", exc_info=True)
            return {"success": False, "message": str(exc)}

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def clear_session(self):
        if self._session:
            await self._session.clear_session()
            logger.info(f"Session cleared: {self.session_id}")

    async def disconnect(self):
        self._analysis_mcp = None
        self._action_mcp   = None
        self._session      = None
        self._ready        = False

    async def __aenter__(self):
        await self._init()
        return self

    async def __aexit__(self, *_):
        await self.disconnect()


# ── Private helpers ───────────────────────────────────────────────────────────

def _strip_hallucinated_calls(text: str) -> str:
    text = re.sub(r"<function=[^>]*>.*?</tool_call>", "", text, flags=re.DOTALL)
    text = re.sub(r"</?function[^>]*>", "", text)
    text = re.sub(r"</?parameter[^>]*>", "", text)
    text = re.sub(r"</?tool_call>", "", text)
    return text.strip()


def _wrap_mermaid(code: str) -> str:
    return f"\n\n```mermaid\n{code}\n```"
