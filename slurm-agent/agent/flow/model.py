"""
Model configuration for the Slurm agent.

- DEFAULT_MODEL             — model for core agents (Observer/Operator/etc.)
- SPECIALIST_MODEL          — model for agent-as-tool specialists
- OLLAMA_BASE_URL           — Ollama API endpoint
- create_ollama_model()     — OpenAI-compat Ollama client
- create_openai_model()     — Native OpenAI API client
- create_azure_openai_model() — Azure OpenAI API client
- create_copilot_model()    — GitHub Copilot API (Claude Sonnet via Copilot)
- resolve_model()           — returns correct model based on LLM_PROVIDER env var
- REASONING_MODEL_SETTINGS  — main agent (high-quality thinking)
- CLOUD_MODEL_SETTINGS      — cloud provider settings (no Ollama-specific extras)
"""
import logging
import ipaddress
import os
import ssl
import urllib.parse

from agents.model_settings import ModelSettings
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
import httpx
from openai import AsyncOpenAI, DefaultAsyncHttpxClient
try:
    from openai import AsyncAzureOpenAI
except ImportError:  # Older openai packages may not expose Azure helpers.
    AsyncAzureOpenAI = None
try:
    import truststore
except ImportError:
    truststore = None

logger = logging.getLogger(__name__)

os.environ['NO_PROXY'] = '.cognitiveservices.azure.com,.openai.azure.com,10.0.0.0/8'
os.environ['no_proxy'] = os.environ['NO_PROXY']

# ── Provider selection ────────────────────────────────────────────────────────
# Supported providers: ollama (default), openai, azure-openai, copilot, github-models.
LLM_PROVIDER: str = os.environ.get("LLM_PROVIDER", "ollama").lower()

# ── OpenAI config ─────────────────────────────────────────────────────────────
OPENAI_BASE_URL: str = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY: str = (
    os.environ.get("OPENAI_API_KEY", "")
    or os.environ.get("OPEN_AI_KEY", "")
)

# ── Azure OpenAI config ──────────────────────────────────────────────────────
AZURE_OPENAI_ENDPOINT: str = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
AZURE_OPENAI_API_KEY: str = (
    os.environ.get("AZURE_OPENAI_API_KEY", "")
    or os.environ.get("AZURE_OPENAI_KEY", "")
)
AZURE_OPENAI_API_VERSION: str = os.environ.get(
    "AZURE_OPENAI_API_VERSION",
    os.environ.get("API_VERSION", "2024-02-15-preview"),
)
AZURE_OPENAI_MODEL: str = (
    os.environ.get("AZURE_OPENAI_MODEL", "")
    or os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")
    or os.environ.get("OPENAI_MODEL", "gpt-4o")
)

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

GITHUB_TOKEN: str = (
    os.environ.get("GITHUB_TOKEN", "")
    or os.environ.get("GH_TOKEN", "")
    or os.environ.get("GITHUB_PAT", "")
)

# ── Ollama config ─────────────────────────────────────────────────────────────
# Override via env vars: SLURM_AGENT_MODEL, SLURM_AGENT_SPECIALIST_MODEL, SLURM_AGENT_BASE_URL
DEFAULT_MODEL: str = os.environ.get("SLURM_AGENT_MODEL", "qwen3.5:9b")
SPECIALIST_MODEL: str = os.environ.get("SLURM_AGENT_SPECIALIST_MODEL", "qwen2.5:7b")
OLLAMA_BASE_URL: str = os.environ.get("SLURM_AGENT_BASE_URL", "http://localhost:11434/v1")


# ── Model factories ───────────────────────────────────────────────────────────

def _host_matches_no_proxy(hostname: str, no_proxy: str) -> bool:
    host = hostname.strip().strip("[]").lower()
    if not host:
        return False
    for raw_token in no_proxy.split(","):
        token = raw_token.strip().lower()
        if not token:
            continue
        if token == "*":
            return True
        if "/" in token:
            try:
                if ipaddress.ip_address(host) in ipaddress.ip_network(token, strict=False):
                    return True
            except ValueError:
                pass
        token_host = token[1:] if token.startswith(".") else token
        if host == token_host or host.endswith(f".{token_host}"):
            return True
    return False


def _url_matches_no_proxy(url: str | None) -> bool:
    if not url:
        return False
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname or url
    return _host_matches_no_proxy(host, os.environ.get("NO_PROXY") or os.environ.get("no_proxy") or "")


def _cloud_http_client(target_url: str | None = None) -> DefaultAsyncHttpxClient | None:
    """Return an OpenAI SDK HTTP client with system certs and explicit proxy mounts."""
    mode = os.environ.get("SLURM_AGENT_USE_SYSTEM_CERTS", "auto").strip().lower()
    http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    https_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")

    use_system_certs = mode in {"1", "true", "yes", "on"} or (
        mode == "auto" and os.name == "nt"
    )
    verify: ssl.SSLContext | bool = True
    if use_system_certs and truststore is not None:
        verify = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        logger.info("[model] Using system certificate store for cloud LLM HTTP client")
    elif use_system_certs:
        logger.warning(
            "[model] truststore is not installed; cloud LLM calls will use Python's default certs."
        )

    if _url_matches_no_proxy(target_url):
        logger.info("[model] Bypassing proxy for cloud LLM URL matched by NO_PROXY")
        return DefaultAsyncHttpxClient(verify=verify, trust_env=False)

    mounts: dict[str, httpx.AsyncHTTPTransport] = {}
    if http_proxy:
        mounts["http://"] = httpx.AsyncHTTPTransport(proxy=http_proxy, verify=verify)
    if https_proxy or http_proxy:
        mounts["https://"] = httpx.AsyncHTTPTransport(proxy=https_proxy or http_proxy, verify=verify)

    if mounts:
        logger.info("[model] Using explicit proxy mounts for cloud LLM HTTP client")
        return DefaultAsyncHttpxClient(mounts=mounts, verify=verify, trust_env=False)
    if verify is not True:
        return DefaultAsyncHttpxClient(verify=verify, trust_env=False)
    return None


def cloud_client_kwargs(target_url: str | None = None) -> dict[str, DefaultAsyncHttpxClient]:
    http_client = _cloud_http_client(target_url=target_url)
    return {"http_client": http_client} if http_client is not None else {}


def create_ollama_model(
    model_name: str,
    base_url: str = "http://localhost:11434/v1",
) -> OpenAIChatCompletionsModel:
    """Create an Ollama-backed model using the OpenAI-compat endpoint."""
    client = AsyncOpenAI(base_url=base_url, api_key="ollama")
    return OpenAIChatCompletionsModel(model=model_name, openai_client=client)


def create_openai_model(
    model_name: str | None = None,
    token: str | None = None,
    base_url: str | None = None,
) -> OpenAIChatCompletionsModel:
    """Create a native OpenAI model client.

    Requires OPENAI_API_KEY in env or explicit token.
    """
    _token = token or OPENAI_API_KEY
    if not _token:
        raise RuntimeError(
            "OPENAI_API_KEY env var is required for LLM_PROVIDER=openai."
        )
    _model = model_name or OPENAI_MODEL
    _base = base_url or OPENAI_BASE_URL
    client = AsyncOpenAI(base_url=_base, api_key=_token, **cloud_client_kwargs())
    logger.info(f"[model] OpenAI backend: {_base} model={_model}")
    return OpenAIChatCompletionsModel(model=_model, openai_client=client)


def create_azure_openai_model(
    model_name: str | None = None,
    token: str | None = None,
    endpoint: str | None = None,
    api_version: str | None = None,
) -> OpenAIChatCompletionsModel:
    """Create an Azure OpenAI model client.

    The model name is the Azure deployment name.
    """
    _token = token or AZURE_OPENAI_API_KEY
    _endpoint = (endpoint or AZURE_OPENAI_ENDPOINT).rstrip("/")
    if not _endpoint:
        raise RuntimeError(
            "AZURE_OPENAI_ENDPOINT env var is required for LLM_PROVIDER=azure-openai."
        )
    if not _token:
        raise RuntimeError(
            "AZURE_OPENAI_API_KEY or AZURE_OPENAI_KEY env var is required for LLM_PROVIDER=azure-openai."
        )
    if AsyncAzureOpenAI is None:
        raise RuntimeError("Installed openai package does not provide AsyncAzureOpenAI.")
    _model = model_name or AZURE_OPENAI_MODEL
    _api_version = api_version or AZURE_OPENAI_API_VERSION
    client = AsyncAzureOpenAI(
        azure_endpoint=_endpoint,
        api_key=_token,
        api_version=_api_version,
        **cloud_client_kwargs(target_url=_endpoint),
    )
    logger.info(f"[model] Azure OpenAI backend: {_endpoint} deployment={_model}")
    return OpenAIChatCompletionsModel(model=_model, openai_client=client)


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
    client = AsyncOpenAI(base_url=_base, api_key=_token, **cloud_client_kwargs())
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
    client = AsyncOpenAI(
        base_url=GITHUB_MODELS_BASE_URL,
        api_key=_token,
        **cloud_client_kwargs(),
    )
    logger.info(f"[model] GitHub Models backend: {GITHUB_MODELS_BASE_URL} model={_model}")
    return OpenAIChatCompletionsModel(model=_model, openai_client=client)


def normalize_provider(provider: str | None = None) -> str:
    """Normalize provider input, falling back to env default."""
    value = (provider or LLM_PROVIDER or "ollama").strip().lower()
    if value in {"azure", "azure_openai", "azure-openai"}:
        return "azure-openai"
    if value not in {"ollama", "openai", "azure-openai", "copilot", "github-models"}:
        return "ollama"
    return value


def resolve_model(
    model_name: str | None = None,
    *,
    provider: str | None = None,
    openai_api_key: str | None = None,
    openai_base_url: str | None = None,
    github_token: str | None = None,
) -> OpenAIChatCompletionsModel:
    """Return the appropriate model based on LLM_PROVIDER env var.

    LLM_PROVIDER=ollama         (default) → Ollama at SLURM_AGENT_BASE_URL
    LLM_PROVIDER=openai                   → OpenAI API (needs OPENAI_API_KEY)
    LLM_PROVIDER=azure-openai             → Azure OpenAI API (needs AZURE_OPENAI_ENDPOINT + key)
    LLM_PROVIDER=copilot                  → GitHub Copilot API (needs gh CLI token)
    LLM_PROVIDER=github-models            → GitHub Models API (works with PAT)
    """
    active_provider = normalize_provider(provider)
    if active_provider == "openai":
        return create_openai_model(model_name, token=openai_api_key, base_url=openai_base_url)
    if active_provider == "azure-openai":
        return create_azure_openai_model(model_name)
    if active_provider == "copilot":
        return create_copilot_model(model_name, token=github_token)
    if active_provider == "github-models":
        return create_github_models_model(model_name, token=github_token)
    return create_ollama_model(model_name or DEFAULT_MODEL, OLLAMA_BASE_URL)


def resolve_specialist_model(
    model_name: str | None = None,
    *,
    provider: str | None = None,
    openai_api_key: str | None = None,
    openai_base_url: str | None = None,
    github_token: str | None = None,
) -> OpenAIChatCompletionsModel:
    """Return model for agent-as-tool specialists.

    For Ollama, defaults to a smaller model (`qwen2.5:7b`) to keep specialist calls fast/cheap.
    For non-Ollama providers, falls back to the provider default.
    """
    active_provider = normalize_provider(provider)
    if active_provider == "ollama":
        return create_ollama_model(model_name or SPECIALIST_MODEL, OLLAMA_BASE_URL)
    if active_provider == "openai":
        return create_openai_model(
            model_name or OPENAI_MODEL,
            token=openai_api_key,
            base_url=openai_base_url,
        )
    if active_provider == "azure-openai":
        return create_azure_openai_model(model_name or AZURE_OPENAI_MODEL)
    return resolve_model(
        model_name,
        provider=active_provider,
        openai_api_key=openai_api_key,
        openai_base_url=openai_base_url,
        github_token=github_token,
    )


# ── Sampling settings ─────────────────────────────────────────────────────────

# Ollama: deterministic, tool-focused responses (no explicit reasoning stream)
REASONING_MODEL_SETTINGS = ModelSettings(
    temperature=0.0,
    top_p=0.9,
    parallel_tool_calls=False,
    extra_body={"think": False, "options": {"num_ctx": 16384}},
)

# Cloud providers: no Ollama-specific extras.
CLOUD_MODEL_SETTINGS = ModelSettings(
    temperature=0.0,
    top_p=0.7,
    parallel_tool_calls=False,
)


def model_settings_for_provider(
    provider: str | None = None,
    *,
    parallel_tool_calls: bool = False,
) -> ModelSettings:
    """Return model settings that match the selected provider."""
    active_provider = normalize_provider(provider)
    if active_provider in ("openai", "azure-openai", "copilot", "github-models"):
        return CLOUD_MODEL_SETTINGS.resolve(
            ModelSettings(
                parallel_tool_calls=bool(
                    parallel_tool_calls and active_provider == "openai"
                )
            )
        )
    return REASONING_MODEL_SETTINGS

# Active settings — picked at import time based on provider
ACTIVE_MODEL_SETTINGS: ModelSettings = model_settings_for_provider(LLM_PROVIDER)
