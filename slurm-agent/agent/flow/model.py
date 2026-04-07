"""
Model configuration for the Slurm agent.

- create_ollama_model()   — OpenAI-compat Ollama client
- REASONING_MODEL_SETTINGS — main agent (high-quality thinking)
- TOOL_MODEL_SETTINGS      — sub-agents (precise, tool_choice=required)
- extract_subagent_output  — custom output extractor for sub-agent tool calls
"""
import logging
from typing import Any

from agents import RunContextWrapper
from agents.agent import ToolsToFinalOutputResult
from agents.model_settings import ModelSettings
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from agents.result import RunResult, RunResultStreaming
from agents.tool import FunctionToolResult
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


def create_ollama_model(
    model_name: str,
    base_url: str = "http://localhost:11434/v1",
) -> OpenAIChatCompletionsModel:
    """Create an Ollama-backed model using the OpenAI-compat endpoint."""
    client = AsyncOpenAI(base_url=base_url, api_key="ollama")
    return OpenAIChatCompletionsModel(model=model_name, openai_client=client)


# Gemma 4 recommended sampling — thinking enabled for main agent
# `think: True` tells Ollama to activate thinking mode (chat template handled internally)
# `top_k` is Ollama-specific and goes in extra_body, not ModelSettings
REASONING_MODEL_SETTINGS = ModelSettings(
    temperature=1.0,
    top_p=0.95,
    extra_body={"think": True, "options": {"top_k": 64}},
)

# Sub-agents must call tools exactly — lower temperature, forced tool use, no thinking
TOOL_MODEL_SETTINGS = ModelSettings(
    temperature=0.3,
    top_p=0.95,
    tool_choice="required",
    extra_body={"options": {"top_k": 64}},
)


async def extract_subagent_output(result: RunResult | RunResultStreaming) -> str:
    """
    Return structured tool results from a sub-agent run so the main agent
    gets raw data rather than a prose summary.
    """
    if isinstance(result, RunResultStreaming):
        final_output = await result.final_output_async()
    else:
        final_output = result.final_output

    tool_outputs = []
    if hasattr(result, "new_items"):
        for item in result.new_items:
            if type(item).__name__ == "ToolCallOutputItem":
                name   = getattr(item, "name", "") or getattr(item, "tool_name", "")
                output = getattr(item, "output", "")
                if output:
                    tool_outputs.append(f"[{name}]: {output}")

    if tool_outputs:
        return "TOOL_RESULTS:\n" + "\n".join(tool_outputs) + f"\n\nSUMMARY: {final_output}"
    return f"INTERNAL_RESPONSE: {final_output}"


def make_web_search_handler():
    """
    Returns a tool_use_behavior handler that short-circuits the analysis sub-agent
    and returns web_search results directly, tagged with [WEB_SEARCH]: so
    the streaming layer can detect URLs.
    """
    def handler(
        context: RunContextWrapper[Any],
        tool_results: list[FunctionToolResult],
    ) -> ToolsToFinalOutputResult:
        for result in tool_results:
            tool_name  = ""
            output_str = str(getattr(result, "output", "") or "")

            if hasattr(result, "tool"):
                tool_name = getattr(result.tool, "name", "")

            is_web = (
                "web_search" in tool_name.lower()
                or "[WEB_SEARCH]:" in output_str
                or ("URL:" in output_str and "http" in output_str)
            )
            if is_web and output_str:
                marked = output_str if output_str.startswith("[WEB_SEARCH]:") else f"[WEB_SEARCH]:\n{output_str}"
                return ToolsToFinalOutputResult(is_final_output=True, final_output=marked)

        return ToolsToFinalOutputResult(is_final_output=False, final_output=None)

    return handler
