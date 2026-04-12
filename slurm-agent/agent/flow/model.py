"""
Model configuration for the Slurm agent.

- DEFAULT_MODEL             — single source of truth for the model name
- OLLAMA_BASE_URL           — Ollama API endpoint
- create_ollama_model()     — OpenAI-compat Ollama client
- REASONING_MODEL_SETTINGS  — main agent (high-quality thinking)
"""
import logging
import os

from agents.model_settings import ModelSettings
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# ── Central model config ──────────────────────────────────────────────────────
# Change these two values to switch every LLM call in the system at once.
# Override via env vars: SLURM_AGENT_MODEL, SLURM_AGENT_BASE_URL
DEFAULT_MODEL: str = os.environ.get("SLURM_AGENT_MODEL", "qwen3.5:9b")
OLLAMA_BASE_URL: str = os.environ.get("SLURM_AGENT_BASE_URL", "http://localhost:11434/v1")


def create_ollama_model(
    model_name: str,
    base_url: str = "http://localhost:11434/v1",
) -> OpenAIChatCompletionsModel:
    """Create an Ollama-backed model using the OpenAI-compat endpoint."""
    client = AsyncOpenAI(base_url=base_url, api_key="ollama")
    return OpenAIChatCompletionsModel(model=model_name, openai_client=client)


# Sampling settings — thinking enabled
# `think: True` tells Ollama to activate thinking mode (supported by gemma4, qwen3, etc.)
# `num_ctx`: explicitly set context window so Ollama allocates enough for
#   system prompt (~8K chars) + tools (~9K chars) + conversation history
# temp=0.3 + top_p=0.7: low creativity but enough flexibility for multi-step tool calls
# `parallel_tool_calls=False`: Ollama models may generate malformed JSON when
#   attempting multiple tool calls in a single response — force sequential calls
REASONING_MODEL_SETTINGS = ModelSettings(
    temperature=0.3,
    top_p=0.7,
    parallel_tool_calls=False,
    extra_body={"think": True, "options": {"num_ctx": 16384}},
)
