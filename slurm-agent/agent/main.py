"""
FastAPI Server for Slurm Agent with OpenAI SDK
Supports OpenWebUI streaming format for chat integration.
"""
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import uvicorn
import json
import logging
import uuid
import time
import os
import re
import base64
import mimetypes
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from flow import SlurmAgentSystem
from flow.model import (
    DEFAULT_MODEL,
    SPECIALIST_MODEL,
    OLLAMA_BASE_URL,
    LLM_PROVIDER,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_MODEL,
    COPILOT_BASE_URL,
    COPILOT_MODEL,
    GITHUB_MODELS_BASE_URL,
    GITHUB_MODELS_MODEL,
    GITHUB_TOKEN,
    normalize_provider,
)
from flow.skills import load_observer_skills

# Configuration
MCP_SERVER_URL = "http://localhost:3002"
AUTO_APPROVE = os.environ.get("AUTO_APPROVE", "false").lower() in ("1", "true", "yes")
# Per-event timeout: if the agent produces no event for this many seconds, abort
STREAM_TIMEOUT = int(os.environ.get("STREAM_TIMEOUT", "75"))
CHARTS_DIR = "/tmp/slurm_charts"
UPLOADS_DIR = "/tmp/slurm_uploads"
VISION_MODEL = os.environ.get("SLURM_AGENT_VISION_MODEL", "").strip()
MAX_IMAGE_BYTES = int(os.environ.get("SLURM_AGENT_MAX_IMAGE_BYTES", "2000000"))
MAX_IMAGE_ATTACHMENTS = int(os.environ.get("SLURM_AGENT_MAX_IMAGE_ATTACHMENTS", "3"))

os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ===== Streaming Helpers =====
def create_stream_chunk(
    content: Optional[str] = None,
    reasoning_content: Optional[str] = None,
    finish_reason: Optional[str] = None,
) -> str:
    """Create OpenWebUI-compatible SSE chunk."""
    chunk = {
        "id": f"slurm-{uuid.uuid4()}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "slurm-agent",
        "choices": [{
            "index": 0,
            "finish_reason": finish_reason,
            "delta": {}
        }]
    }
    if content:
        chunk["choices"][0]["delta"]["content"] = content
    if reasoning_content:
        chunk["choices"][0]["delta"]["reasoning_content"] = reasoning_content
        chunk["choices"][0]["delta"]["reasoning"] = reasoning_content
    return f"data: {json.dumps(chunk)}\n\n"


def create_todo_chunk(items: list[dict]) -> str:
    """Create SSE chunk for todo panel updates."""
    chunk = {
        "id": f"slurm-{uuid.uuid4()}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "slurm-agent",
        "choices": [{
            "index": 0,
            "finish_reason": None,
            "delta": {"todo_update": items},
        }],
    }
    return f"data: {json.dumps(chunk)}\n\n"


def _event_to_sse(event: dict) -> str | None:
    """Convert an agent event dict to an SSE data line, or None to skip."""
    t = event.get("type")
    cid = f"slurm-{uuid.uuid4()}"
    ts = int(time.time())

    def _chunk(delta: dict) -> str:
        return f"data: {json.dumps({'id': cid, 'object': 'chat.completion.chunk', 'created': ts, 'model': 'slurm-agent', 'choices': [{'index': 0, 'finish_reason': None, 'delta': delta}]})}\n\n"

    if t == "status":
        return _chunk({"status_update": event.get("message", "")})
    elif t == "tool_output":
        return _chunk({"tool_output": event.get("output", "")})
    elif t == "thinking":
        c = event.get("content", "")
        return create_stream_chunk(reasoning_content=c) if c else None
    elif t in ("token", "final_answer"):
        c = event.get("content") or event.get("message", "")
        return create_stream_chunk(content=c) if c else None
    elif t == "chart":
        return _chunk({"chart_artifact": event.get("mermaid", "")})
    elif t == "todo":
        return _chunk({"todo_update": event.get("items", [])})
    return None  # web_results, unknown → skip


# ===== Session Management =====
SessionAgentEntry = tuple[SlurmAgentSystem, str, str, str, str, str, bool, float]
_session_agents: Dict[str, SessionAgentEntry] = {}
SESSION_TIMEOUT = 3600


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _default_model_for_provider(provider: str) -> str:
    if provider == "azure-openai":
        return AZURE_OPENAI_MODEL
    if provider == "openai":
        return OPENAI_MODEL
    if provider == "copilot":
        return COPILOT_MODEL
    if provider == "github-models":
        return GITHUB_MODELS_MODEL
    return DEFAULT_MODEL


def _default_specialist_model_for_provider(provider: str) -> str:
    if provider == "azure-openai":
        return AZURE_OPENAI_MODEL
    if provider == "openai":
        return OPENAI_MODEL
    if provider == "copilot":
        return COPILOT_MODEL
    if provider == "github-models":
        return GITHUB_MODELS_MODEL
    return SPECIALIST_MODEL


def _schedule_disconnect(agent: SlurmAgentSystem) -> None:
    """Best-effort cleanup for replaced/expired agents."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(agent.disconnect())
    except Exception:
        pass


def get_agent(
    session_id: str = "default",
    mcp_url: str | None = None,
    llm_provider: str | None = None,
    llm_main_provider: str | None = None,
    llm_specialist_provider: str | None = None,
    llm_model: str | None = None,
    llm_specialist_model: str | None = None,
    openai_api_key: str | None = None,
    openai_parallel: bool = False,
) -> SlurmAgentSystem:
    """Get or create agent for session."""
    global _session_agents
    current_time = time.time()
    effective_mcp = mcp_url or MCP_SERVER_URL
    effective_provider = normalize_provider(llm_main_provider or llm_provider or LLM_PROVIDER)
    effective_specialist_provider = normalize_provider(llm_specialist_provider or effective_provider)
    effective_model = (llm_model or "").strip() or _default_model_for_provider(effective_provider)
    effective_specialist_model = (llm_specialist_model or "").strip() or _default_specialist_model_for_provider(effective_specialist_provider)
    effective_openai_parallel = bool(openai_parallel and effective_provider == "openai")

    expired = [
        k for k, (agent, _, _, _, _, _, _, t) in _session_agents.items()
        if current_time - t > SESSION_TIMEOUT
    ]
    for k in expired:
        _schedule_disconnect(_session_agents[k][0])
        del _session_agents[k]

    if session_id in _session_agents:
        (
            agent,
            prev_mcp,
            prev_provider,
            prev_model,
            prev_specialist_provider,
            prev_specialist_model,
            prev_openai_parallel,
            _,
        ) = _session_agents[session_id]
        key_changed = (
            "openai" in {effective_provider, effective_specialist_provider}
            and bool(openai_api_key)
            and getattr(agent, "openai_api_key", "") != openai_api_key
        )
        if (
            prev_mcp == effective_mcp
            and prev_provider == effective_provider
            and prev_model == effective_model
            and prev_specialist_provider == effective_specialist_provider
            and prev_specialist_model == effective_specialist_model
            and prev_openai_parallel == effective_openai_parallel
            and not key_changed
        ):
            _session_agents[session_id] = (
                agent,
                prev_mcp,
                prev_provider,
                prev_model,
                prev_specialist_provider,
                prev_specialist_model,
                prev_openai_parallel,
                current_time,
            )
            return agent
        logger.info(
            f"Agent config changed for session {session_id}: "
            f"mcp {prev_mcp}->{effective_mcp}, "
            f"main-provider {prev_provider}->{effective_provider}, "
            f"main-model {prev_model}->{effective_model}, "
            f"specialist-provider {prev_specialist_provider}->{effective_specialist_provider}, "
            f"specialist-model {prev_specialist_model}->{effective_specialist_model}, "
            f"openai-parallel {prev_openai_parallel}->{effective_openai_parallel}"
        )
        _schedule_disconnect(agent)

    logger.info(
        f"Creating agent for session: {session_id} "
        f"(mcp={effective_mcp}, main-provider={effective_provider}, "
        f"main-model={effective_model}, specialist-provider={effective_specialist_provider}, "
        f"specialist-model={effective_specialist_model}, "
        f"openai-parallel={effective_openai_parallel})"
    )
    agent = SlurmAgentSystem(
        reasoning_model=effective_model,
        mcp_url=effective_mcp,
        session_id=session_id,
        auto_approve=AUTO_APPROVE,
        llm_provider=effective_provider,
        llm_model=effective_model,
        specialist_provider=effective_specialist_provider,
        specialist_model=effective_specialist_model,
        openai_api_key=openai_api_key,
        openai_parallel=effective_openai_parallel,
    )
    _session_agents[session_id] = (
        agent,
        effective_mcp,
        effective_provider,
        effective_model,
        effective_specialist_provider,
        effective_specialist_model,
        effective_openai_parallel,
        current_time,
    )
    return agent


# ===== App =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Slurm Agent API")
    yield
    for sid, (agent, *_) in _session_agents.items():
        try:
            await agent.disconnect()
        except Exception as e:
            logger.error(f"Disconnect error {sid}: {e}")


app = FastAPI(title="Slurm Agent API", version="4.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Models =====
class ChatMessage(BaseModel):
    role: str
    content: Optional[str] = None
    task: Optional[str] = "chat"


class ChatRequest(BaseModel):
    model: Optional[str] = "slurm-agent"
    messages: List[ChatMessage]
    stream: bool = True
    session_id: Optional[str] = None
    chat_id: Optional[str] = None
    user_id: Optional[str] = None
    hitl_decision: Optional[str] = None
    model_config = {"extra": "allow"}


# ===== File Attachment Pre-processing =====
_ATTACH_RE = re.compile(r'\[Attached file:\s*([^\]]+)\]')
_SKILL_CMD_RE = re.compile(r"^\s*/skill\s+(list|search|use)\b(.*)$", re.IGNORECASE | re.DOTALL)
_TODO_CMD_RE = re.compile(r"^\s*/todo\b(.*)$", re.IGNORECASE | re.DOTALL)
_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}


def _attached_paths(user_message: str) -> list[str]:
    paths: list[str] = []
    for raw in _ATTACH_RE.findall(user_message or ""):
        path = (raw or "").strip()
        if path:
            paths.append(path)
    return paths


def _is_image_path(path: str) -> bool:
    return os.path.splitext(path.lower())[1] in _IMAGE_EXTS


def _preprocess_attachments(user_message: str) -> str:
    matches = _ATTACH_RE.findall(user_message)
    if not matches:
        return user_message

    clean_text = _ATTACH_RE.sub('', user_message).strip()
    valid_paths = []
    parts = []
    for path in matches:
        path = path.strip()
        filename = os.path.basename(path)
        if os.path.isfile(path):
            parts.append(f"📎 **{filename}** (path: {path})")
            valid_paths.append(path)
        else:
            parts.append(f"📎 **{filename}** (path: {path}) ⚠️ not found")

    file_block = "\n".join(parts)

    if clean_text:
        return f"{file_block}\n\nUser request: {clean_text}"
    return f"{file_block}\n\nUser request: Process these files."


def _parse_todo_steps(raw: str) -> list[str]:
    text = (raw or "").strip()
    if not text:
        return []
    parts = [text]
    if ";" in text:
        parts = [p.strip() for p in text.split(";")]
    elif "\n" in text:
        parts = [p.strip() for p in text.splitlines()]
    cleaned: list[str] = []
    for part in parts:
        s = re.sub(r"^\s*[-*]\s*", "", part).strip()
        s = re.sub(r"^\s*\d+[\.)]\s*", "", s).strip()
        if s:
            cleaned.append(s[:100])
    return cleaned[:20]


def _format_todo_text(items: list[dict]) -> str:
    if not items:
        return "Todo list is empty."
    lines = ["Todo list:"]
    for item in items:
        status = str(item.get("status", "not-started"))
        marker = "[x]" if status == "completed" else "[>]" if status == "in-progress" else "[ ]"
        lines.append(f"{marker} {item.get('id', '?')}. {item.get('title', '')}")
    return "\n".join(lines)


def _handle_todo_command(agent: SlurmAgentSystem, user_message: str) -> Optional[Dict[str, Any]]:
    m = _TODO_CMD_RE.match((user_message or "").strip())
    if not m:
        return None

    payload = (m.group(1) or "").strip()
    if not payload:
        payload = "show"
    parts = payload.split(None, 1)
    sub = parts[0].lower()
    rest = parts[1].strip() if len(parts) > 1 else ""

    if sub in {"show", "list"}:
        items = agent._todo.get_items()
        return {"message": _format_todo_text(items), "todo_items": items}

    if sub == "clear":
        agent._todo.reset()
        return {"message": "Cleared todo list.", "todo_items": []}

    if sub == "set":
        steps = _parse_todo_steps(rest)
        if not steps:
            return {
                "message": 'Usage: /todo set step 1; step 2; step 3',
                "todo_items": agent._todo.get_items(),
            }
        items = [{"id": i + 1, "title": title, "status": "not-started"} for i, title in enumerate(steps)]
        agent._todo.set_from_tool(items)
        return {"message": f"Set todo list ({len(items)} items).", "todo_items": agent._todo.get_items()}

    if sub == "add":
        title = rest.strip()
        if not title:
            return {
                "message": "Usage: /todo add <task>",
                "todo_items": agent._todo.get_items(),
            }
        items = agent._todo.get_items()
        next_id = max((int(i.get("id", 0)) for i in items), default=0) + 1
        items.append({"id": next_id, "title": title[:100], "status": "not-started"})
        agent._todo.set_from_tool(items)
        return {"message": f"Added todo #{next_id}.", "todo_items": agent._todo.get_items()}

    return {
        "message": "Todo commands: /todo show | /todo clear | /todo set <a; b; c> | /todo add <task>",
        "todo_items": agent._todo.get_items(),
    }


def _search_skill_titles(skills: dict[str, str], query: str, limit: int = 12) -> list[str]:
    q = (query or "").strip().lower()
    if not q:
        return sorted(skills.keys())[:limit]
    hits: list[str] = []
    for title, content in sorted(skills.items()):
        title_l = title.lower()
        content_l = content.lower()
        if q in title_l or q in content_l:
            hits.append(title)
    return hits[:limit]


def _handle_skill_command(user_message: str) -> Optional[Dict[str, str]]:
    raw = (user_message or "").strip()
    m = _SKILL_CMD_RE.match(raw)
    if not m:
        return None

    mode = (m.group(1) or "").strip().lower()
    payload = (m.group(2) or "").strip()
    skills = load_observer_skills()
    titles = sorted(skills.keys())

    if mode == "list":
        if not titles:
            return {"direct_message": "No local skills found."}
        lines = ["Available skills:"] + [f"- {name}" for name in titles[:50]]
        if len(titles) > 50:
            lines.append(f"...and {len(titles) - 50} more.")
        return {"direct_message": "\n".join(lines)}

    if mode == "search":
        if not payload:
            return {"direct_message": "Usage: /skill search <query>"}
        hits = _search_skill_titles(skills, payload)
        if not hits:
            return {"direct_message": f'No skills matched "{payload}".'}
        lines = [f'Skill matches for "{payload}":'] + [f"- {name}" for name in hits]
        return {"direct_message": "\n".join(lines)}

    # mode == "use"
    if not payload:
        return {"direct_message": "Usage: /skill use <query> :: <task>"}
    query, sep, task = payload.partition("::")
    query = query.strip()
    task = task.strip() if sep else ""
    if not query:
        return {"direct_message": "Usage: /skill use <query> :: <task>"}
    if not task:
        task = f"Apply this skill guidance for: {query}"
    rewritten = (
        "EXPLICIT SKILL EXECUTION REQUEST\n"
        f"Skill query: {query}\n"
        f"Task: {task}\n\n"
        "You MUST do this sequence:\n"
        "1) Call lookup_skill with mode='search' for the skill query.\n"
        "2) Call lookup_skill with mode='read' using one exact title from search results.\n"
        "3) Execute the task by following that skill's steps.\n"
        "4) If no skill matches, report that and list close titles.\n"
    )
    return {"rewritten_message": rewritten}


async def _describe_image(
    path: str,
    llm_provider: Optional[str] = None,
    openai_api_key: Optional[str] = None,
) -> Optional[str]:
    if not VISION_MODEL:
        return None
    if not os.path.isfile(path):
        return None
    try:
        size = os.path.getsize(path)
        if size <= 0 or size > MAX_IMAGE_BYTES:
            return f"Skipped ({os.path.basename(path)}): unsupported size {size} bytes."

        with open(path, "rb") as f:
            raw = f.read()
        mime = mimetypes.guess_type(path)[0] or "image/png"
        data_url = f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"

        provider = normalize_provider(llm_provider or LLM_PROVIDER)
        client, _, extra_kwargs = _build_chat_client(
            provider=provider,
            model_name=VISION_MODEL,
            openai_api_key=openai_api_key,
        )

        resp = await client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are helping an HPC assistant. Describe the image concisely with concrete "
                        "details that could be useful for troubleshooting or operations."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe the attached image for technical ops context."},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            temperature=0.1,
            max_tokens=220,
            **extra_kwargs,
        )
        desc = (resp.choices[0].message.content or "").strip()
        if not desc:
            return "No description returned by vision model."
        return desc[:700]
    except Exception as exc:
        logger.warning(f"Vision parse failed for {path}: {exc}")
        return f"Vision parse failed for {os.path.basename(path)}: {exc}"


def _build_chat_client(
    provider: str,
    model_name: Optional[str],
    openai_api_key: Optional[str] = None,
):
    """Create an OpenAI-compatible client for the active provider."""
    from openai import AsyncOpenAI
    try:
        from openai import AsyncAzureOpenAI
    except ImportError:
        AsyncAzureOpenAI = None

    active_provider = normalize_provider(provider)
    target_model = (model_name or "").strip() or _default_model_for_provider(active_provider)

    if active_provider == "openai":
        token = (openai_api_key or OPENAI_API_KEY).strip()
        if not token:
            raise RuntimeError("OPENAI_API_KEY missing for OpenAI provider")
        return AsyncOpenAI(base_url=OPENAI_BASE_URL, api_key=token), target_model, {}

    if active_provider == "azure-openai":
        if AsyncAzureOpenAI is None:
            raise RuntimeError("Installed openai package does not provide AsyncAzureOpenAI")
        if not AZURE_OPENAI_ENDPOINT:
            raise RuntimeError("AZURE_OPENAI_ENDPOINT missing for Azure OpenAI provider")
        if not AZURE_OPENAI_API_KEY:
            raise RuntimeError("AZURE_OPENAI_API_KEY or AZURE_OPENAI_KEY missing for Azure OpenAI provider")
        client = AsyncAzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
        )
        return client, target_model, {}

    if active_provider == "copilot":
        if not GITHUB_TOKEN:
            raise RuntimeError("GITHUB_TOKEN missing for Copilot provider")
        return AsyncOpenAI(base_url=COPILOT_BASE_URL, api_key=GITHUB_TOKEN), target_model, {}

    if active_provider == "github-models":
        if not GITHUB_TOKEN:
            raise RuntimeError("GITHUB_TOKEN missing for GitHub Models provider")
        return AsyncOpenAI(base_url=GITHUB_MODELS_BASE_URL, api_key=GITHUB_TOKEN), target_model, {}

    return (
        AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama"),
        target_model,
        {"extra_body": {"think": False}},
    )


async def _augment_with_image_descriptions(
    user_message: str,
    llm_provider: Optional[str] = None,
    openai_api_key: Optional[str] = None,
) -> str:
    paths = [p for p in _attached_paths(user_message) if os.path.isfile(p) and _is_image_path(p)]
    if not paths:
        return user_message

    image_paths = paths[:MAX_IMAGE_ATTACHMENTS]
    notes: list[str] = []
    if not VISION_MODEL:
        names = ", ".join(os.path.basename(p) for p in image_paths)
        notes.append(
            f"Image attachments detected ({names}), but no vision model is configured. "
            "Set SLURM_AGENT_VISION_MODEL to enable image understanding."
        )
    else:
        for p in image_paths:
            desc = await _describe_image(p, llm_provider=llm_provider, openai_api_key=openai_api_key)
            if desc:
                notes.append(f"{os.path.basename(p)}: {desc}")
    if not notes:
        return user_message
    joined = "\n".join(f"- {n}" for n in notes)
    return f"{user_message}\n\n[IMAGE_ANALYSIS]\n{joined}"


# ===== Endpoints =====
@app.get("/")
async def root():
    return {"status": "running", "sessions": len(_session_agents)}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/v1/models")
async def list_models():
    return {"object": "list", "data": [{"id": "slurm-agent", "object": "model"}]}


@app.post("/v1/chat/completions")
async def chat(request: ChatRequest, raw_request: Request):
    """OpenWebUI-compatible chat endpoint."""
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages")

    raw = request.model_dump()
    session_id = raw.get("chat_id") or raw.get("user_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.warning(f"No chat_id in request, generated new session: {session_id}")

    mcp_url = raw_request.headers.get("x-mcp-url")
    legacy_provider = raw_request.headers.get("x-llm-provider")
    llm_provider = normalize_provider(
        raw_request.headers.get("x-llm-main-provider")
        or legacy_provider
        or LLM_PROVIDER
    )
    llm_specialist_provider = normalize_provider(
        raw_request.headers.get("x-llm-specialist-provider") or llm_provider
    )
    llm_model = (raw_request.headers.get("x-llm-model") or "").strip() or None
    llm_specialist_model = (raw_request.headers.get("x-llm-specialist-model") or "").strip() or None
    openai_parallel = _truthy(
        raw_request.headers.get("x-llm-parallel-tool-calls")
        or raw_request.headers.get("x-openai-parallel")
    )
    openai_api_key = (raw_request.headers.get("x-openai-api-key") or "").strip() or None
    logger.info(
        f"Chat request - session_id: {session_id}, mcp_url: {mcp_url or 'default'}, "
        f"main-provider: {llm_provider}, main-model: {llm_model or '(default)'}, "
        f"specialist-provider: {llm_specialist_provider}, "
        f"specialist-model: {llm_specialist_model or '(default)'}, "
        f"openai-parallel: {bool(openai_parallel and llm_provider == 'openai')}"
    )
    agent = get_agent(
        session_id,
        mcp_url=mcp_url,
        llm_provider=llm_provider,
        llm_main_provider=llm_provider,
        llm_specialist_provider=llm_specialist_provider,
        llm_model=llm_model,
        llm_specialist_model=llm_specialist_model,
        openai_api_key=openai_api_key,
        openai_parallel=openai_parallel,
    )

    messages = [m.model_dump() for m in request.messages]
    user_message = ""
    task = "chat"
    for msg in reversed(messages):
        if msg.get("role") == "user" and msg.get("content"):
            user_message = msg["content"]
            task = msg.get("task", "chat")
            break

    def _direct_completion(content: str) -> dict:
        return {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "slurm-agent",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
        }

    async def _direct_stream(content: str, todo_items: Optional[list[dict]] = None):
        if todo_items is not None:
            yield create_todo_chunk(todo_items)
        yield create_stream_chunk(content=content, finish_reason="stop")
        yield "data: [DONE]\n\n"

    todo_cmd = _handle_todo_command(agent, user_message)
    if todo_cmd is not None:
        msg = str(todo_cmd.get("message", "")).strip() or "Done."
        todo_items = todo_cmd.get("todo_items", [])
        if request.stream:
            return StreamingResponse(_direct_stream(msg, todo_items), media_type="text/event-stream")
        return _direct_completion(msg)

    skill_cmd = _handle_skill_command(user_message)
    if skill_cmd is not None:
        if skill_cmd.get("direct_message"):
            msg = str(skill_cmd["direct_message"]).strip()
            if request.stream:
                return StreamingResponse(_direct_stream(msg), media_type="text/event-stream")
            return _direct_completion(msg)
        if skill_cmd.get("rewritten_message"):
            user_message = str(skill_cmd["rewritten_message"])

    user_message = _preprocess_attachments(user_message)
    user_message = await _augment_with_image_descriptions(
        user_message,
        llm_provider=agent.llm_provider,
        openai_api_key=agent.openai_api_key,
    )
    logger.info(f"Preprocessed message ({len(user_message)} chars): {user_message[:500]}")

    # Non-streaming
    if not request.stream:
        try:
            result = await agent.run(user_message)
            content = result.get("message", "")
            return {
                "id": f"chatcmpl-{uuid.uuid4()}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "slurm-agent",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}]
            }
        except Exception as e:
            return {"choices": [{"message": {"content": f"Error: {e}"}, "finish_reason": "stop"}]}

    # Streaming with per-event timeout to prevent infinite hangs
    async def stream():
        try:
            if not user_message:
                yield create_stream_chunk(content="No message", finish_reason="stop")
                yield "data: [DONE]\n\n"
                return

            # Generation tasks use simple LLM directly
            if task in ["follow_up_generation", "title_generation", "tags_generation"]:
                client, generation_model, extra_kwargs = _build_chat_client(
                    provider=agent.llm_provider,
                    model_name=agent.llm_model,
                    openai_api_key=agent.openai_api_key,
                )
                response = await client.chat.completions.create(
                    model=generation_model,
                    messages=messages,
                    temperature=0.2,
                    **extra_kwargs,
                )
                content = response.choices[0].message.content or ""
                yield create_stream_chunk(content=content, finish_reason="stop")
                yield "data: [DONE]\n\n"
                return

            # Agent streaming — per-event timeout prevents eval hangs
            async def _gen():
                async for ev in agent.run_streaming(user_message, hitl_decision=request.hitl_decision):
                    yield ev

            gen = _gen()
            while True:
                try:
                    event = await asyncio.wait_for(gen.__anext__(), timeout=STREAM_TIMEOUT)
                except StopAsyncIteration:
                    break
                except asyncio.TimeoutError:
                    logger.warning(f"Stream timeout after {STREAM_TIMEOUT}s (session={session_id})")
                    yield create_stream_chunk(content="⏱️ Request timed out. Please try again.", finish_reason="stop")
                    yield "data: [DONE]\n\n"
                    return

                t = event.get("type")
                if t == "error":
                    yield create_stream_chunk(content=f"Error: {event.get('message', '')}", finish_reason="stop")
                    yield "data: [DONE]\n\n"
                    return
                elif t == "done":
                    pending = event.get("pending_actions") or []
                    if pending:
                        pa_chunk = {
                            "id": f"slurm-{uuid.uuid4()}",
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": "slurm-agent",
                            "choices": [{"index": 0, "finish_reason": None,
                                         "delta": {"pending_actions": pending}}],
                        }
                        yield f"data: {json.dumps(pa_chunk)}\n\n"
                    yield create_stream_chunk(finish_reason="stop")
                    yield "data: [DONE]\n\n"
                    return
                else:
                    line = _event_to_sse(event)
                    if line:
                        yield line

        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield create_stream_chunk(content=f"Error: {e}", finish_reason="stop")
            yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/sessions")
async def list_sessions():
    return {"count": len(_session_agents), "sessions": list(_session_agents.keys())}


@app.delete("/sessions")
async def clear_all_sessions():
    """Clear all sessions and SQLite conversation history."""
    global _session_agents
    count = len(_session_agents)
    for sid, (agent, *_) in list(_session_agents.items()):
        try:
            await agent.disconnect()
        except Exception as e:
            logger.error(f"Disconnect error {sid}: {e}")
    _session_agents = {}
    db = "/tmp/slurm_agent_conversations.db"
    if os.path.exists(db):
        os.remove(db)
        logger.info(f"Removed {db}")
    return {"cleared": count, "message": "All sessions and conversation history cleared"}


@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific session."""
    global _session_agents
    if session_id in _session_agents:
        agent, *_ = _session_agents.pop(session_id)
        try:
            await agent.clear_session()
            await agent.disconnect()
        except Exception as e:
            logger.warning(f"Error clearing session {session_id}: {e}")
        return {"cleared": session_id}
    else:
        try:
            from agents import SQLiteSession
            raw = SQLiteSession(session_id, "/tmp/slurm_agent_conversations.db")
            await raw.clear_session()
        except Exception as e:
            logger.warning(f"Error clearing orphaned session {session_id}: {e}")
        return {"cleared": session_id}


@app.get("/charts/{chart_filename}")
async def get_chart(chart_filename: str):
    if not chart_filename.endswith('.png') or '/' in chart_filename or '\\' in chart_filename:
        raise HTTPException(status_code=400, detail="Invalid chart filename")
    chart_path = os.path.join(CHARTS_DIR, chart_filename)
    if not os.path.exists(chart_path):
        raise HTTPException(status_code=404, detail="Chart not found")
    return FileResponse(chart_path, media_type="image/png")


@app.get("/api/cluster/status")
async def cluster_status():
    """Proxy to MCP server's cluster status endpoint."""
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{MCP_SERVER_URL}/api/cluster/status", timeout=aiohttp.ClientTimeout(total=10)) as resp:
                return await resp.json()
    except Exception as e:
        return {"error": str(e), "available": False}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename")
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid filename")
    dest = os.path.join(UPLOADS_DIR, safe_name)
    content = await file.read()
    if len(content) > 1_000_000:
        raise HTTPException(status_code=400, detail="File too large (max 1 MB)")
    with open(dest, 'wb') as f:
        f.write(content)
    os.chmod(dest, 0o644)
    logger.info(f"Uploaded: {file.filename} -> {dest}")
    return {"path": dest, "filename": safe_name, "size": len(content)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=20000, reload=True)
