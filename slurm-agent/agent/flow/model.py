"""
Model configuration for the Slurm agent.

- DEFAULT_MODEL             — single source of truth for the model name
- OLLAMA_BASE_URL           — Ollama API endpoint
- create_ollama_model()     — OpenAI-compat Ollama client
- create_copilot_model()    — GitHub Copilot API (Claude Sonnet via Copilot)
- resolve_model()           — returns correct model based on LLM_PROVIDER env var
- REASONING_MODEL_SETTINGS  — main agent (high-quality thinking)
- COPILOT_MODEL_SETTINGS    — Copilot/Claude settings (no think/num_ctx extras)
"""
import logging
import os

from agents.model_settings import ModelSettings
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# ── Provider selection ────────────────────────────────────────────────────────
# Set LLM_PROVIDER=copilot + GITHUB_TOKEN=<pat> to route through GitHub Copilot.
# Leave unset to use local Ollama (default).
LLM_PROVIDER: str = os.environ.get("LLM_PROVIDER", "ollama").lower()

# ── Copilot config ────────────────────────────────────────────────────────────
# GitHub Copilot — OpenAI-compat endpoint.
# Requires a token issued by `gh auth token` (NOT a classic PAT).
COPILOT_BASE_URL: str = os.environ.get(
    "COPILOT_BASE_URL", "https://api.githubcopilot.com"
)
COPILOT_MODEL: str = os.environ.get("COPILOT_MODEL", "claude-sonnet-4-6")

# GitHub Models — Azure-backed, OpenAI-compat, works with a regular GitHub PAT
# (needs the 'models: read' scope). Supports claude-sonnet-4-5.
GITHUB_MODELS_BASE_URL: str = os.environ.get(
    "GITHUB_MODELS_BASE_URL", "https://models.inference.ai.azure.com"
)
GITHUB_MODELS_MODEL: str = os.environ.get("GITHUB_MODELS_MODEL", "claude-sonnet-4-5")

GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN", "")

# ── Ollama config ─────────────────────────────────────────────────────────────
# Override via env vars: SLURM_AGENT_MODEL, SLURM_AGENT_BASE_URL
DEFAULT_MODEL: str = os.environ.get("SLURM_AGENT_MODEL", "qwen3.5:9b")
OLLAMA_BASE_URL: str = os.environ.get("SLURM_AGENT_BASE_URL", "http://localhost:11434/v1")


# ── Model factories ───────────────────────────────────────────────────────────

def create_ollama_model(
    model_name: str,
    base_url: str = "http://localhost:11434/v1",
) -> OpenAIChatCompletionsModel:
    """Create an Ollama-backed model using the OpenAI-compat endpoint."""
    client = AsyncOpenAI(base_url=base_url, api_key="ollama")
    return OpenAIChatCompletionsModel(model=model_name, openai_client=client)


def create_copilot_model(
    model_name: str | None = None,
    token: str | None = None,
    base_url: str | None = None,
) -> OpenAIChatCompletionsModel:
    """Create a GitHub Copilot-backed model (Claude Sonnet via Copilot API).

    The Copilot API is OpenAI-compatible — same SDK, different base URL + token.
    Requires a GitHub PAT with the `copilot` scope in GITHUB_TOKEN env var.
    """
    _token = token or GITHUB_TOKEN
    if not _token:
        raise RuntimeError(
            "GITHUB_TOKEN env var is required for LLM_PROVIDER=copilot. "
            "Create a GitHub PAT with 'copilot' scope."
        )
    _model = model_name or COPILOT_MODEL
    _base = base_url or COPILOT_BASE_URL
    client = AsyncOpenAI(base_url=_base, api_key=_token)
    logger.info(f"[model] Copilot backend: {_base} model={_model}")
    return OpenAIChatCompletionsModel(model=_model, openai_client=client)


def create_github_models_model(
    model_name: str | None = None,
    token: str | None = None,
) -> OpenAIChatCompletionsModel:
    """Create a GitHub Models-backed model (Claude Sonnet via Azure-backed endpoint).

    Works with a regular GitHub PAT that has the 'models: read' scope.
    Create one at: https://github.com/settings/tokens
    """
    _token = token or GITHUB_TOKEN
    if not _token:
        raise RuntimeError(
            "GITHUB_TOKEN env var is required for LLM_PROVIDER=github-models. "
            "Create a GitHub PAT with 'models: read' scope."
        )
    _model = model_name or GITHUB_MODELS_MODEL
    client = AsyncOpenAI(base_url=GITHUB_MODELS_BASE_URL, api_key=_token)
    logger.info(f"[model] GitHub Models backend: {GITHUB_MODELS_BASE_URL} model={_model}")
    return OpenAIChatCompletionsModel(model=_model, openai_client=client)


def resolve_model(model_name: str | None = None) -> OpenAIChatCompletionsModel:
    """Return the appropriate model based on LLM_PROVIDER env var.

    LLM_PROVIDER=ollama         (default) → Ollama at SLURM_AGENT_BASE_URL
    LLM_PROVIDER=copilot                  → GitHub Copilot API (needs gh CLI token)
    LLM_PROVIDER=github-models            → GitHub Models API (works with PAT)
    """
    if LLM_PROVIDER == "copilot":
        return create_copilot_model(model_name)
    if LLM_PROVIDER == "github-models":
        return create_github_models_model(model_name)
    return create_ollama_model(model_name or DEFAULT_MODEL, OLLAMA_BASE_URL)


# ── Sampling settings ─────────────────────────────────────────────────────────

# Ollama: thinking enabled, large context window, sequential tool calls
REASONING_MODEL_SETTINGS = ModelSettings(
    temperature=0.3,
    top_p=0.7,
    parallel_tool_calls=False,
    extra_body={"think": True, "options": {"num_ctx": 16384}},
)

# Copilot/Claude: no Ollama-specific extras; Claude handles thinking natively
COPILOT_MODEL_SETTINGS = ModelSettings(
    temperature=0.3,
    top_p=0.7,
    parallel_tool_calls=False,
)

# Active settings — picked at import time based on provider
ACTIVE_MODEL_SETTINGS: ModelSettings = (
    COPILOT_MODEL_SETTINGS
    if LLM_PROVIDER in ("copilot", "github-models")
    else REASONING_MODEL_SETTINGS
)
