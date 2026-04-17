"""
FastAPI Server for Slurm Agent with OpenAI SDK
Supports OpenWebUI streaming format for chat integration.
"""
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
import logging
import uuid
import time
import os
import re
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from flow import SlurmMultiAgentSystem
from flow.model import DEFAULT_MODEL, OLLAMA_BASE_URL

# Configuration
MCP_SERVER_URL = "http://localhost:3002"
AUTO_APPROVE = os.environ.get("AUTO_APPROVE", "false").lower() in ("1", "true", "yes")
CHARTS_DIR = "/tmp/slurm_charts"
UPLOADS_DIR = "/tmp/slurm_uploads"

# Ensure directories exist
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
        # Expose as both field names so any frontend variant picks it up
        chunk["choices"][0]["delta"]["reasoning_content"] = reasoning_content
        chunk["choices"][0]["delta"]["reasoning"] = reasoning_content
    return f"data: {json.dumps(chunk)}\n\n"


# ===== Session Management =====
_session_agents: Dict[str, tuple] = {}
SESSION_TIMEOUT = 3600


def get_agent(session_id: str = "default", mcp_url: str | None = None) -> SlurmMultiAgentSystem:
    """Get or create agent for session."""
    global _session_agents
    current_time = time.time()
    effective_mcp = mcp_url or MCP_SERVER_URL
    
    # Clean expired sessions
    expired = [k for k, (_, _, t) in _session_agents.items() if current_time - t > SESSION_TIMEOUT]
    for k in expired:
        del _session_agents[k]
    
    if session_id in _session_agents:
        agent, prev_mcp, _ = _session_agents[session_id]
        if prev_mcp == effective_mcp:
            _session_agents[session_id] = (agent, prev_mcp, current_time)
            return agent
        # MCP URL changed — recreate agent
        logger.info(f"MCP URL changed for session {session_id}: {prev_mcp} -> {effective_mcp}")
    
    logger.info(f"Creating agent for session: {session_id} (mcp={effective_mcp})")
    agent = SlurmMultiAgentSystem(
        reasoning_model=DEFAULT_MODEL,
        tool_model=DEFAULT_MODEL,
        mcp_url=effective_mcp,
        session_id=session_id,
        auto_approve=AUTO_APPROVE,
    )
    _session_agents[session_id] = (agent, effective_mcp, current_time)
    return agent


# ===== App =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Slurm Agent API")
    yield
    for sid, (agent, _, _) in _session_agents.items():
        try:
            await agent.disconnect()
        except Exception as e:
            logger.error(f"Disconnect error {sid}: {e}")


app = FastAPI(title="Slurm Agent API", version="4.0.0", lifespan=lifespan)

# CORS for live dashboard iframe access
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
    chat_id: Optional[str] = None  # OpenWebUI's chat identifier
    user_id: Optional[str] = None
    hitl_decision: Optional[str] = None  # "approve" or "reject" from frontend buttons
    model_config = {"extra": "allow"}


# ===== File Attachment Pre-processing =====
_ATTACH_RE = re.compile(r'\[Attached file:\s*([^\]]+)\]')


def _preprocess_attachments(user_message: str) -> str:
    """
    Extract [Attached file: /path] markers and list them as path references.
    Does NOT read file contents — the agent can use read_file or pass paths
    directly to tools like sbatch. This keeps the message compact.
    """
    matches = _ATTACH_RE.findall(user_message)
    if not matches:
        return user_message

    # Strip all [Attached file: ...] markers from the text
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

    # Detect submit intent: .sh files + action words (or no specific request)
    all_sh = all(p.endswith('.sh') for p in valid_paths) and valid_paths
    action_words = any(w in clean_text.lower() for w in [
        "run", "submit", "execute", "start", "launch", "these", "all",
    ]) if clean_text else False

    if all_sh and (action_words or not clean_text):
        # Make the submit intent explicit for the model
        paths_csv = ",".join(valid_paths)
        directive = (
            f"ACTION REQUIRED: Submit {len(valid_paths)} scripts to Slurm via sbatch.\n"
            f"Paths: {paths_csv}\n"
            f"→ Hand off to Operator immediately."
        )
        if clean_text:
            return f"{file_block}\n\n{directive}\n\nUser message: {clean_text}"
        return f"{file_block}\n\n{directive}"

    if clean_text:
        return f"{file_block}\n\nUser request: {clean_text}"
    else:
        return f"{file_block}\n\nUser request: Process these files."


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
    
    # Debug: log fields to understand what OpenWebUI sends
    logger.info(f"DEBUG raw request: chat_id={raw.get('chat_id')}, user_id={raw.get('user_id')}")
    
    # Extract session ID - chat_id is now forwarded from OpenWebUI metadata
    session_id = raw.get("chat_id") or raw.get("user_id")
    
    # If still no session ID, generate a unique one
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.warning(f"No chat_id in request, generated new session: {session_id}")
    
    mcp_url = raw_request.headers.get("x-mcp-url")
    logger.info(f"Chat request - session_id: {session_id}, mcp_url: {mcp_url or 'default'}")
    agent = get_agent(session_id, mcp_url=mcp_url)
    
    messages = [m.model_dump() for m in request.messages]
    user_message = ""
    task = "chat"
    for msg in reversed(messages):
        if msg.get("role") == "user" and msg.get("content"):
            user_message = msg["content"]
            task = msg.get("task", "chat")
            break
    
    # Pre-process file attachments: read contents and inject into message
    user_message = _preprocess_attachments(user_message)
    logger.info(f"Preprocessed message ({len(user_message)} chars): {user_message[:500]}")
    
    # Non-streaming — use the agent (not raw LLM) for full tool access
    if not request.stream:
        try:
            result = await agent.run(user_message)
            content = result.get("message", "")
            return {
                "id": "chatcmpl-{}".format(uuid.uuid4()),
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "slurm-agent",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}]
            }
        except Exception as e:
            return {"choices": [{"message": {"content": "Error: {}".format(e)}, "finish_reason": "stop"}]}
    
    # Streaming
    async def stream():
        try:
            if not user_message:
                yield create_stream_chunk(content="No message", finish_reason="stop")
                yield "data: [DONE]\n\n"
                return
            
            # Generation tasks use simple LLM (title, tags, follow-up suggestions)
            if task in ["follow_up_generation", "title_generation", "tags_generation"]:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
                response = await client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=messages,
                    temperature=0.2,
                    extra_body={"think": False},
                )
                content = response.choices[0].message.content or ""
                yield create_stream_chunk(content=content, finish_reason="stop")
                yield "data: [DONE]\n\n"
                return
            
            # Agent streaming
            async for event in agent.run_streaming(user_message, hitl_decision=request.hitl_decision):
                t = event.get("type")
                if t == "status":
                    # Status updates go in their own field — NOT reasoning_content
                    sc = {
                        "id": f"slurm-{uuid.uuid4()}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": "slurm-agent",
                        "choices": [{"index": 0, "finish_reason": None,
                                     "delta": {"status_update": event.get("message", "")}}],
                    }
                    yield f"data: {json.dumps(sc)}\n\n"
                elif t == "tool_output":
                    to_chunk = {
                        "id": f"slurm-{uuid.uuid4()}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": "slurm-agent",
                        "choices": [{"index": 0, "finish_reason": None,
                                     "delta": {"tool_output": event.get("output", "")}}],
                    }
                    yield f"data: {json.dumps(to_chunk)}\n\n"
                elif t == "thinking":
                    yield create_stream_chunk(reasoning_content=event.get("content", ""))
                elif t == "token":
                    yield create_stream_chunk(content=event.get("content", ""))
                elif t == "final_answer":
                    yield create_stream_chunk(content=event.get("message", ""))
                elif t == "chart":
                    # Send mermaid code as a separate delta field
                    chart_chunk = {
                        "id": f"slurm-{uuid.uuid4()}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": "slurm-agent",
                        "choices": [{"index": 0, "finish_reason": None,
                                     "delta": {"chart_artifact": event.get("mermaid", "")}}],
                    }
                    yield f"data: {json.dumps(chart_chunk)}\n\n"
                elif t == "todo":
                    # Send todo list update
                    todo_chunk = {
                        "id": f"slurm-{uuid.uuid4()}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": "slurm-agent",
                        "choices": [{"index": 0, "finish_reason": None,
                                     "delta": {"todo_update": event.get("items", [])}}],
                    }
                    yield f"data: {json.dumps(todo_chunk)}\n\n"
                elif t == "error":
                    yield create_stream_chunk(content=f"Error: {event.get('message', '')}", finish_reason="stop")
                    yield "data: [DONE]\n\n"
                    return
                elif t == "done":
                    # Send pending actions (if any) so the frontend can show confirm/cancel buttons
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
    
    # Disconnect all agents
    for sid, (agent, _, _) in list(_session_agents.items()):
        try:
            await agent.disconnect()
        except Exception as e:
            logger.error(f"Disconnect error {sid}: {e}")
    
    _session_agents = {}
    
    # Also clear the SQLite conversation database
    import os
    db_files = [
        "/tmp/slurm_agent_conversations.db",
    ]
    for db in db_files:
        if os.path.exists(db):
            os.remove(db)
            logger.info(f"Removed {db}")
    
    return {"cleared": count, "message": "All sessions and conversation history cleared"}


@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific session — both in-memory agent and SQLite history."""
    global _session_agents
    if session_id in _session_agents:
        agent, _, _ = _session_agents.pop(session_id)
        try:
            await agent.clear_session()
            await agent.disconnect()
        except Exception as e:
            logger.warning(f"Error clearing session {session_id}: {e}")
        return {"cleared": session_id}
    else:
        # Even if the agent isn't in memory, clear the SQLite session
        try:
            from agents import SQLiteSession
            raw = SQLiteSession(session_id, "/tmp/slurm_agent_conversations.db")
            await raw.clear_session()
            logger.info(f"Cleared orphaned SQLite session: {session_id}")
        except Exception as e:
            logger.warning(f"Error clearing orphaned session {session_id}: {e}")
        return {"cleared": session_id}


@app.get("/charts/{chart_filename}")
async def get_chart(chart_filename: str):
    """Serve generated chart images."""
    # Security: only allow .png files and no path traversal
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
    """Upload a job script file. Returns the server-side path."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename")
    # Sanitize filename: keep only safe characters
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid filename")
    dest = os.path.join(UPLOADS_DIR, safe_name)
    content = await file.read()
    if len(content) > 1_000_000:  # 1 MB limit
        raise HTTPException(status_code=400, detail="File too large (max 1 MB)")
    with open(dest, 'wb') as f:
        f.write(content)
    os.chmod(dest, 0o644)
    logger.info(f"Uploaded: {file.filename} -> {dest}")
    return {"path": dest, "filename": safe_name, "size": len(content)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=20000, reload=True)
