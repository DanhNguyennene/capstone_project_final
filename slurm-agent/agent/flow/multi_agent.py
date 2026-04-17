"""
Slurm ReAct Agent with Sub-Agents as Tools

Architecture:
- Main ReAct Agent: Keeps context, orchestrates everything
- Analysis Sub-Agent: Called as a tool for read-only queries  
- Action Sub-Agent: Called as a tool for job management
- SQLiteSession: Automatic conversation history management
- SlurmContext: Custom RunContext for confirmation state

Sub-agents return results to main agent, maintaining context coherence.
"""
import logging
import re
import json
from typing import Optional, AsyncGenerator, Dict, Any, Set, List
from dataclasses import dataclass, field

from agents import Agent, Runner, SQLiteSession, RunContextWrapper, ItemHelpers
from agents.agent import ToolsToFinalOutputResult
from agents.result import RunResult, RunResultStreaming
from agents.mcp import MCPServerSse, ToolFilterContext
from agents.tool import FunctionTool, FunctionToolResult
from agents.tool_context import ToolContext
from agents.tool_guardrails import (
    ToolInputGuardrail, ToolOutputGuardrail,
    tool_input_guardrail, tool_output_guardrail,
    ToolGuardrailFunctionOutput, ToolInputGuardrailData, ToolOutputGuardrailData,
)
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from agents.model_settings import ModelSettings
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


# ============ Custom Output Extractors ============
async def extract_subagent_output(result: RunResult | RunResultStreaming) -> str:
    """
    Extract structured output from sub-agent runs.
    
    This ensures sub-agents return data, not conversational responses.
    If the sub-agent used tools, we format the tool results.
    Otherwise, we return the final output with a prefix indicating it's internal.
    """
    # Get the final output
    if isinstance(result, RunResultStreaming):
        final_output = await result.final_output_async()
    else:
        final_output = result.final_output
    
    # Check if tools were called - if so, include tool outputs
    tool_outputs = []
    if hasattr(result, 'new_items'):
        for item in result.new_items:
            item_type = type(item).__name__
            if item_type == "ToolCallOutputItem":
                tool_name = getattr(item, 'name', '') or getattr(item, 'tool_name', '')
                output = getattr(item, 'output', '')
                if output:
                    tool_outputs.append(f"[{tool_name}]: {output}")
    
    # Build structured response
    if tool_outputs:
        tools_section = "\n".join(tool_outputs)
        return f"TOOL_RESULTS:\n{tools_section}\n\nSUMMARY: {final_output}"
    else:
        # No tools called - just return the output but mark it as internal
        return f"INTERNAL_RESPONSE: {final_output}"


# ============ Chart-Filtering Session Wrapper ============

class ChartFilteredSession:
    """
    Wraps SQLiteSession to filter chart artifacts from conversation history.
    
    The agent never sees chart HTML in history - the framework handles chart display.
    This ensures the LLM isn't confused by HTML artifacts in previous messages.
    """
    
    def __init__(self, session: SQLiteSession):
        self._session = session
    
    @staticmethod
    def _strip_charts(text: str) -> str:
        """Remove chart artifacts (mermaid blocks) from text."""
        if not text:
            return text
        # Remove mermaid code blocks from history to keep context clean
        pattern = r'```mermaid\n.*?```'
        return re.sub(pattern, '', text, flags=re.DOTALL).strip()
    
    @staticmethod
    def _filter_history_item(item):
        """Filter chart artifacts from a single history item."""
        # Handle different item types from the SDK
        if hasattr(item, 'content'):
            # Message-like item
            if isinstance(item.content, str):
                filtered_content = ChartFilteredSession._strip_charts(item.content)
                # Create a copy with filtered content
                if hasattr(item, '_replace'):  # namedtuple
                    return item._replace(content=filtered_content)
                elif hasattr(item, '__dict__'):
                    # Object - create modified copy
                    import copy
                    new_item = copy.copy(item)
                    new_item.content = filtered_content
                    return new_item
        return item
    
    async def get_session_history(self):
        """Get history with chart artifacts filtered out."""
        history = await self._session.get_session_history()
        if not history:
            return history
        
        # Filter each item in history
        filtered = []
        for item in history:
            filtered_item = self._filter_history_item(item)
            filtered.append(filtered_item)
        
        return filtered
    
    async def add_items(self, items):
        """Add items to history (charts included for persistence, filtered on read)."""
        return await self._session.add_items(items)
    
    async def clear_session(self):
        """Clear session history."""
        return await self._session.clear_session()
    
    def __getattr__(self, name):
        """Delegate unknown attributes to wrapped session."""
        return getattr(self._session, name)


# ============ Pending Actions Store ============
import sqlite3
import threading

class PendingActionsStore:
    """
    Persistent store for pending actions that require confirmation.
    Uses SQLite for persistence across runs.
    """
    _lock = threading.Lock()
    
    def __init__(self, db_path: str = "/tmp/slurm_pending_actions.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pending_actions (
                    session_id TEXT PRIMARY KEY,
                    actions TEXT,
                    created_at REAL
                )
            """)
            conn.commit()
            conn.close()
    
    def store_pending(self, session_id: str, actions: List[Dict[str, Any]]):
        """Store pending actions for a session."""
        import time
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "INSERT OR REPLACE INTO pending_actions (session_id, actions, created_at) VALUES (?, ?, ?)",
                (session_id, json.dumps(actions), time.time())
            )
            conn.commit()
            conn.close()
            logger.info(f"Stored {len(actions)} pending actions for session {session_id}")
    
    def get_pending(self, session_id: str) -> List[Dict[str, Any]]:
        """Get pending actions for a session."""
        import time
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "SELECT actions, created_at FROM pending_actions WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                actions_json, created_at = row
                # Only return if less than 1 hour old
                if time.time() - created_at < 3600:
                    return json.loads(actions_json)
            return []
    
    def clear_pending(self, session_id: str):
        """Clear pending actions for a session."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute("DELETE FROM pending_actions WHERE session_id = ?", (session_id,))
            conn.commit()
            conn.close()
            logger.info(f"Cleared pending actions for session {session_id}")


# Global pending actions store
_pending_store = PendingActionsStore()


# ============ Run Context ============
@dataclass
class SlurmContext:
    """
    Custom context passed through the agent run.
    Accessible via RunContextWrapper.context in tools and guardrails.
    
    Note: pending_actions are now stored persistently via PendingActionsStore,
    allowing them to survive across runs for confirmation flow.
    
    Chart artifacts are stored here during the run and appended to response at stream end.
    """
    session_id: str = "default"
    chart_artifacts: List[str] = field(default_factory=list)
    
    def add_chart_artifact(self, mermaid_code: str):
        """Store a chart artifact for later appending to response."""
        self.chart_artifacts.append(mermaid_code)
        logger.debug(f"Stored chart artifact ({len(mermaid_code)} chars), total: {len(self.chart_artifacts)}")
    
    def get_pending_actions(self) -> List[Dict[str, Any]]:
        """Get pending actions from persistent store."""
        return _pending_store.get_pending(self.session_id)
    
    def add_pending_action(self, tool_name: str, args: Dict[str, Any], description: str):
        """Add a pending action to persistent store."""
        actions = self.get_pending_actions()
        actions.append({
            "tool": tool_name,
            "args": args,
            "description": description
        })
        _pending_store.store_pending(self.session_id, actions)
        logger.info(f"Added pending action {tool_name} - {description}")
    
    def clear_pending(self):
        """Clear pending actions from persistent store."""
        _pending_store.clear_pending(self.session_id)


# ============ Tool Sets ============
# Analysis tools: Read-only data gathering + web search for debugging
ANALYSIS_TOOL_NAMES: Set[str] = {"run_analysis","squeue", "sacct", "sinfo", "scontrol_show" , "web_search"}

# Visualization tools: For main agent direct access
VISUALIZATION_TOOLS: Set[str] = {"generate_chart"}

# Safe action tools (no confirmation needed - read-only or low-risk)
SAFE_ACTION_TOOLS: Set[str] = {
    "squeue", "sacct", "sinfo", "scontrol_show",  # Read-only queries
    "srun", "salloc",  # Interactive execution (user's own resources)
    "sacctmgr_show", "sreport",  # Read-only accounting queries
    "web_search"  # Web search for debugging/docs
}

# Dangerous tools (modify cluster state - need confirmation via context)
DANGEROUS_TOOLS: Set[str] = {
    # Job control
    "scancel", "scontrol_hold", "scontrol_release", "scontrol_update", "sbatch",
    # Admin operations (high risk)
    "scontrol_create", "scontrol_delete", "scontrol_reconfigure",
    # Accounting modifications (high risk)
    "sacctmgr_add", "sacctmgr_modify", "sacctmgr_delete"
}

# All action tools (including dangerous ones)
ACTION_TOOL_NAMES: Set[str] = SAFE_ACTION_TOOLS | DANGEROUS_TOOLS


# ============ Dynamic Tool Filter ============
def create_tool_filter_for_agent(allowed_tools: Set[str]):
    """Create a tool filter that only allows specific tools."""
    async def tool_filter(context: ToolFilterContext, tool) -> bool:
        allowed = tool.name in allowed_tools
        logger.debug(f"Tool filter: {tool.name} -> {'ALLOWED' if allowed else 'BLOCKED'}")
        return allowed
    return tool_filter


def create_static_tool_filter(allowed_tools: Set[str]) -> dict:
    """Create a static tool filter (doesn't require run_context)."""
    return {"allowed_tool_names": list(allowed_tools)}


# ============ Hardcoded Dangerous Tool Schemas ============
# Mirrors the MCP server tool signatures exactly, so we don't need an extra
# MCP connection at startup just to fetch schemas.

_DANGEROUS_TOOL_SCHEMAS: Dict[str, Dict] = {
    "sbatch": {
        "description": "Submit a batch job script to Slurm.",
        "schema": {"type": "object", "properties": {
            "script": {"type": "string", "description": "Job script content or path"},
            "flags":  {"type": "string", "description": "Additional sbatch flags (optional)"},
        }, "required": ["script"]},
    },
    "scancel": {
        "description": "Cancel a Slurm job.",
        "schema": {"type": "object", "properties": {
            "job_id": {"type": "string", "description": "Job ID to cancel"},
            "user":   {"type": "string", "description": "Optional user filter"},
        }, "required": ["job_id"]},
    },
    "scontrol_hold": {
        "description": "Place a hold on a pending Slurm job.",
        "schema": {"type": "object", "properties": {
            "job_id": {"type": "string", "description": "Job ID to hold"},
        }, "required": ["job_id"]},
    },
    "scontrol_release": {
        "description": "Release a held Slurm job.",
        "schema": {"type": "object", "properties": {
            "job_id": {"type": "string", "description": "Job ID to release"},
        }, "required": ["job_id"]},
    },
    "scontrol_update": {
        "description": "Update a Slurm entity attribute.",
        "schema": {"type": "object", "properties": {
            "entity": {"type": "string", "description": "Entity type (job, node, partition)"},
            "id":     {"type": "string", "description": "Entity ID"},
            "params": {"type": "string", "description": "Key=value pairs to set"},
        }, "required": ["entity", "id", "params"]},
    },
    "scontrol_create": {
        "description": "Create a new Slurm entity (partition, node reservation).",
        "schema": {"type": "object", "properties": {
            "entity": {"type": "string", "description": "Entity type"},
            "params": {"type": "string", "description": "Entity parameters"},
        }, "required": ["entity", "params"]},
    },
    "scontrol_delete": {
        "description": "Delete a Slurm entity.",
        "schema": {"type": "object", "properties": {
            "entity": {"type": "string", "description": "Entity type"},
            "id":     {"type": "string", "description": "Entity ID"},
        }, "required": ["entity", "id"]},
    },
    "scontrol_reconfigure": {
        "description": "Force slurmctld to re-read its configuration file.",
        "schema": {"type": "object", "properties": {}, "required": []},
    },
    "sacctmgr_add": {
        "description": "Add a Slurm accounting entity (user, account, QOS).",
        "schema": {"type": "object", "properties": {
            "entity": {"type": "string", "description": "Entity type (user, account, qos)"},
            "params": {"type": "string", "description": "Entity parameters"},
        }, "required": ["entity", "params"]},
    },
    "sacctmgr_modify": {
        "description": "Modify a Slurm accounting entity.",
        "schema": {"type": "object", "properties": {
            "entity": {"type": "string", "description": "Entity type"},
            "where":  {"type": "string", "description": "Filter condition (e.g. name=alice)"},
            "params": {"type": "string", "description": "Fields to update"},
        }, "required": ["entity", "where", "params"]},
    },
    "sacctmgr_delete": {
        "description": "Delete a Slurm accounting entity.",
        "schema": {"type": "object", "properties": {
            "entity": {"type": "string", "description": "Entity type"},
            "params": {"type": "string", "description": "Entity identifier"},
        }, "required": ["entity", "params"]},
    },
}


# ============ Tool Guardrails ============
# These run at the tool boundary — before/after each FunctionTool invocation.
# Three behaviors: allow() | reject_content(msg) | raise_exception()

_SBATCH_DANGER_PATTERNS = [
    "rm -rf /", ":(){ :|:& };:", "mkfs", "dd if=/dev/",
    "> /dev/sda", "chmod -R 777 /", "wget.*| sh", "curl.*| bash",
]


@tool_input_guardrail(name="validate_job_id")
def _guard_job_id(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """Reject if job_id is missing or non-numeric. Prevents wildcard/typo cancels."""
    args = json.loads(data.context.tool_arguments or "{}")
    job_id = str(args.get("job_id", "")).strip()
    if not job_id:
        return ToolGuardrailFunctionOutput.reject_content(
            "job_id is required. Use squeue to find the numeric job ID first."
        )
    if not job_id.isdigit():
        return ToolGuardrailFunctionOutput.reject_content(
            f"Invalid job_id '{job_id}': must be a numeric Slurm job ID (e.g. 12345). "
            "Run squeue to look up the correct ID."
        )
    return ToolGuardrailFunctionOutput.allow(output_info={"job_id": job_id})


@tool_input_guardrail(name="validate_sbatch_script")
def _guard_sbatch(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """Reject sbatch calls containing obviously destructive shell commands."""
    args = json.loads(data.context.tool_arguments or "{}")
    content = (args.get("script", "") + " " + args.get("flags", "")).lower()
    for pattern in _SBATCH_DANGER_PATTERNS:
        if pattern.lower() in content:
            return ToolGuardrailFunctionOutput.reject_content(
                f"Blocked: script contains dangerous pattern '{pattern}'. "
                "Review the script carefully before submitting."
            )
    return ToolGuardrailFunctionOutput.allow()


@tool_input_guardrail(name="require_pending_actions")
def _guard_pending_exists(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """Reject confirm_action fast if there's nothing pending — avoids an async round-trip."""
    slurm_ctx = data.context.context  # SlurmContext injected at Runner.run time
    if slurm_ctx is None:
        return ToolGuardrailFunctionOutput.allow()
    pending = slurm_ctx.get_pending_actions()
    if not pending:
        return ToolGuardrailFunctionOutput.reject_content(
            "No pending actions to confirm. "
            "Ask the user what dangerous action they want to execute first."
        )
    return ToolGuardrailFunctionOutput.allow(output_info={"pending_count": len(pending)})


@tool_output_guardrail(name="redact_secrets")
def _guard_redact_secrets(data: ToolOutputGuardrailData) -> ToolGuardrailFunctionOutput:
    """Redact credential-like strings from tool output before they reach the LLM context."""
    text = str(data.output or "")
    redacted = re.sub(
        r'(sk-[A-Za-z0-9]{20,}'
        r'|Bearer\s+[A-Za-z0-9\-._~+/]{20,}'
        r'|password\s*[=:]\s*\S+'
        r'|token\s*[=:]\s*[A-Za-z0-9\-._]{16,})',
        '[REDACTED]',
        text,
        flags=re.IGNORECASE,
    )
    if redacted != text:
        logger.warning(f"Redacted sensitive data in output of '{data.context.tool_name}'")
        return ToolGuardrailFunctionOutput.reject_content(redacted)
    return ToolGuardrailFunctionOutput.allow()


# Map dangerous tool names to their input guardrails
_TOOL_INPUT_GUARDRAILS: Dict[str, List[ToolInputGuardrail]] = {
    "scancel":          [_guard_job_id],
    "scontrol_hold":    [_guard_job_id],
    "scontrol_release": [_guard_job_id],
    "sbatch":           [_guard_sbatch],
}

# Output guardrail applied to confirm_action (runs real MCP calls)
_CONFIRM_OUTPUT_GUARDRAILS: List[ToolOutputGuardrail] = [_guard_redact_secrets]


# ============ Model Configuration ============
def create_ollama_model(model_name: str = None, base_url: str = None) -> OpenAIChatCompletionsModel:
    """Create Ollama-compatible model."""
    from .model import DEFAULT_MODEL, OLLAMA_BASE_URL
    model_name = model_name or DEFAULT_MODEL
    base_url = base_url or OLLAMA_BASE_URL
    client = AsyncOpenAI(base_url=base_url, api_key="ollama")
    return OpenAIChatCompletionsModel(model=model_name, openai_client=client)


# Model settings for reasoning (main agent) - gemma4 thinks before answering
# Google recommends temperature=1.0, top_p=0.95, top_k=64 for best gemma4 quality
# "think": True tells Ollama to activate thinking mode; top_k is Ollama-specific
REASONING_MODEL_SETTINGS = ModelSettings(
    temperature=1.0,
    top_p=0.95,
    extra_body={"think": True, "options": {"top_k": 64}},
)

# Model settings for tool execution (sub-agents) - lower temp for precise tool calls
TOOL_MODEL_SETTINGS = ModelSettings(
    temperature=0.3,
    top_p=0.95,
    tool_choice="required",  # Force tool usage - sub-agents MUST call tools
    extra_body={"options": {"top_k": 64}},
)

# Legacy alias
MODEL_SETTINGS = TOOL_MODEL_SETTINGS


# ============ Streaming Status Helpers ============

def _format_tool_call(tool_name: str, args: dict) -> str:
    """Format a tool call as a one-line terminal-style step."""
    inp = str(args.get("input", args.get("request", ""))).strip()

    if tool_name == "analyze_cluster":
        if inp.lower().startswith("search for"):
            q = inp[inp.lower().index("search for") + 10:].lstrip(": ").strip()[:60]
            return f"Searching: {q}"
        return f"Querying: {inp[:60]}" if inp else "Querying cluster..."

    if tool_name == "manage_jobs":
        return f"Action: {inp[:60]}" if inp else "Executing job operation..."

    if tool_name == "generate_chart":
        return f"Generating chart: {args.get('chart_id', 'system_health')}"

    if tool_name == "run_analysis":
        return f"$ run_analysis {args.get('script_id', '')}"

    if tool_name in ("squeue", "sacct", "sinfo"):
        parts = [tool_name] + [f"--{k} {v}" for k, v in list(args.items())[:3]]
        return "$ " + " ".join(parts)

    if tool_name == "scontrol_show":
        return f"$ scontrol show {args.get('entity','')} {args.get('id', args.get('job_id',''))}".strip()

    if tool_name == "web_search":
        return f"$ web_search \"{args.get('query', '')[:50]}\""

    if tool_name in ("confirm_action", "cancel_action"):
        verb = "✓ Confirming" if "confirm" in tool_name else "✗ Cancelling"
        return f"{verb} pending actions"

    if tool_name == "check_pending_actions":
        return "Checking pending actions..."

    # Generic Slurm command
    parts = [tool_name] + [f"{k}={v}" for k, v in list(args.items())[:2]]
    return "$ " + " ".join(parts)


def _brief_output_summary(output_str: str) -> str | None:
    """Extract a 1-line result summary to display as a completed step."""
    text = output_str.strip()
    if not text or len(text) < 5:
        return None

    if text.startswith("QUEUED:"):
        return f"↳ {text[:100]}"

    if "SUMMARY:" in text:
        m = re.search(r"SUMMARY:\s*(.+?)(?:\n|$)", text)
        if m:
            return f"↳ {m.group(1).strip()[:100]}"

    # Count Slurm job states in output
    running = len(re.findall(r'\bRUNNING\b', text))
    pending = len(re.findall(r'\bPENDING\b', text))
    failed  = len(re.findall(r'\bFAILED\b|\bTIMEOUT\b', text))
    if running + pending + failed > 0:
        parts = []
        if running: parts.append(f"{running} running")
        if pending: parts.append(f"{pending} pending")
        if failed:  parts.append(f"{failed} failed")
        return f"↳ {', '.join(parts)}"

    return None


# ============ Agent Instructions ============

MAIN_AGENT_INSTRUCTIONS = """You are a Slurm HPC cluster assistant. Expert in job scheduling, resource management, and HPC troubleshooting.

## NON-NEGOTIABLE RULES
1. CALL A TOOL FIRST. Never answer without fresh data.
2. `analyze_cluster` for all read-only queries. `manage_jobs` for all mutations.
3. When `manage_jobs` returns "QUEUED:": tell the user what's pending, then wait for confirm/cancel.
4. Never fabricate job IDs, node names, exit codes, or counts.

## CRITICAL: WHEN TO CALL manage_jobs
You MUST call `manage_jobs` for ANY of the following user intents:
- Cancel / kill / terminate / stop job(s) → manage_jobs("cancel job <id>") or manage_jobs("cancel all gpu running jobs")
- Hold or release job(s) → manage_jobs("hold job <id>")
- Submit / schedule / run a script → manage_jobs("submit /path/script.sh --array=0-9")
- Update job parameters (timelimit, nodes, etc.) → manage_jobs("update job <id> timelimit=2:00:00")

**DO NOT**: Call analyze_cluster, gather data, write a report, and stop.
If the user requested an action, you MUST call manage_jobs — even if you also queried first.

**DO NOT**: Try to read/cat the script file before submitting.
Pass the script path directly to manage_jobs: manage_jobs("submit gpu_benchmark.sh as job array of 10 tasks")

## TOOLS
| Tool | Use |
|------|-----|
| `analyze_cluster(request)` | Status, jobs, nodes, failures, efficiency, web search |
| `manage_jobs(request)` | Cancel, hold, release, submit, update |
| `generate_chart(chart_id)` | system_health · cluster_topology · pending_analysis · resource_map · job_lifecycle |
| `confirm_action()` | User confirmed a queued action |
| `cancel_action()` | User declined a queued action |
| `check_pending_actions()` | List what is currently queued |

## WHAT TO PASS TO analyze_cluster
- Full snapshot → `"run_analysis cluster_status"`
- Failed jobs → `"run_analysis failed_jobs"`
- Pending reasons → `"run_analysis pending_jobs"`
- GPU state → `"run_analysis gpu_resources"`
- Specific job → `"scontrol show job 12345"`
- Web lookup → `"search for: OOMKilled exit code 137 fix"`

## DIAGNOSIS CHEAT SHEET
- PENDING Priority → normal queue backlog
- PENDING Resources → no matching free nodes
- PENDING QOSMaxCpuPerUserLimit → user hit CPU quota
- PENDING ReqNodeNotAvail → requested node is down
- FAILED ExitCode=1 → application error (check stderr)
- FAILED ExitCode=137 → OOM-killed (increase --mem)
- FAILED ExitCode=143 → walltime exceeded (increase --time)
- FAILED ExitCode=1:53 → node hardware failure (re-queue)

## OUTPUT FORMAT
Markdown tables and headers. Show exact IDs, codes, counts. One actionable recommendation per issue."""
ANALYSIS_SUBAGENT_INSTRUCTIONS = """You are a data collector. Call ONE tool and return its raw output. Do not explain or summarize.

Available tools:
- `run_analysis(script_id)` — script_id: analyze_cluster_status | analyze_failed_jobs | analyze_gpu_resources | analyze_my_efficiency | analyze_my_usage | analyze_pending_jobs | analyze_my_jobs
- `squeue` — list queued/running jobs
- `sacct` — job accounting history
- `sinfo` — node/partition status
- `scontrol_show` — detailed entity info (entity: job|node|partition)
- `web_search(query, search_type, fetch_content)` — search_type: slurm|error|general

Pick the right tool. Return output exactly as received."""

ANALYSIS_SUBAGENT_INSTRUCTIONS = """You gather data by calling ONE tool, then return.

## TOOLS
- **web_search(query, search_type, fetch_content)** - Search the internet for documentation, tutorials, error solutions
- **run_analysis(script_id)** - Get current cluster status, job info, node info
- **scontrol_show** - Get specific job/node details
- **squeue/sacct/sinfo** - Raw Slurm queries

## WHEN TO USE WEB_SEARCH
Use web_search when the user wants to:
- Find documentation or tutorials
- Look up error messages or solutions
- Learn how to do something (how to, example, guide)
- Find best practices or recommendations
- Search for external information not in the cluster

### web_search parameters:
- query: The search query
- search_type: "error" for debugging, "docs" for documentation, "slurm" for Slurm-specific
- fetch_content: Set to TRUE for detailed answers (reads full web pages), FALSE for quick search

Use fetch_content=true when:
- User needs detailed step-by-step instructions
- Debugging complex errors
- Looking for code examples or configuration

Use fetch_content=false (default) when:
- Quick lookup of what something means
- Finding relevant URLs
- Simple questions

## WHEN TO USE RUN_ANALYSIS
Use run_analysis when the user wants to:
- Check current cluster status
- See running/pending/failed jobs
- Get node information
- Analyze resource usage

## RULES
1. Call ONE tool only, then stop
2. Return raw tool output - do not summarize

"""

ACTION_SUBAGENT_INSTRUCTIONS = """You execute cluster actions by calling tools. You MUST call a tool for EVERY action request.

## CRITICAL RULES
1. NEVER say an action was done without calling the tool first
2. ALWAYS call the appropriate tool - do not make up results
3. If a tool returns "QUEUED", report that it needs user confirmation
4. If you cannot find the right tool, say so - do not fabricate success

## TOOLS
- **Job control**: sbatch, scancel, scontrol_hold, scontrol_release, scontrol_update, scontrol_requeue
- **Interactive**: srun, salloc  
- **Admin**: scontrol_create, scontrol_delete, scontrol_reconfigure
- **Accounting**: sacctmgr_show, sacctmgr_add, sacctmgr_modify, sacctmgr_delete, sreport

## WORKFLOW
1. Identify the correct tool for the action
2. Call the tool with the required parameters
3. Return the EXACT tool response - do not modify or summarize
4. If tool says "QUEUED", user must confirm before execution
"""


# ============ Main System ============
class SlurmMultiAgentSystem:
    """
    Main ReAct agent with sub-agents as tools.
    
    Architecture:
    - Main agent: Orchestrates, keeps context, calls sub-agents
    - Analysis sub-agent: Read-only investigations (as tool)
    - Action sub-agent: Job management (as tool)
    """
    
    def __init__(
        self,
        reasoning_model: str = None,  # Main agent - thinks/reasons
        tool_model: str = None,  # Sub-agents - executes tools
        base_url: str = None,
        mcp_url: str = "http://localhost:3002",
        session_id: str = "default"
    ):
        from .model import DEFAULT_MODEL, OLLAMA_BASE_URL
        reasoning_model = reasoning_model or DEFAULT_MODEL
        tool_model = tool_model or DEFAULT_MODEL
        base_url = base_url or OLLAMA_BASE_URL
        self.reasoning_model_name = reasoning_model
        self.tool_model_name = tool_model
        self.base_url = base_url
        self.mcp_url = mcp_url
        self.session_id = session_id
        
        # Session for conversation history (wrapped to filter chart artifacts)
        self._session: Optional[ChartFilteredSession] = None
        
        # MCP servers (chart tool uses direct HTTP, not MCP SDK)
        self._analysis_mcp: Optional[MCPServerSse] = None
        self._action_mcp: Optional[MCPServerSse] = None
        # Note: dangerous tools are executed via direct HTTP (same as generate_chart)
        
        # Models - separate for reasoning vs tool execution
        self.reasoning_sdk_model = create_ollama_model(reasoning_model, base_url)  # gemma4
        self.tool_sdk_model = create_ollama_model(tool_model, base_url)  # gemma4
        
        # Agents
        self.main_agent = None
        self.analysis_subagent = None
        self.action_subagent = None
        
        self._agents_initialized = False
    
    def _get_session(self) -> ChartFilteredSession:
        """Get or create session for conversation history with chart filtering."""
        if self._session is None:
            # Use persistent SQLite file for conversation history
            sqlite_session = SQLiteSession(
                self.session_id, 
                "/tmp/slurm_agent_conversations.db"
            )
            # Wrap with chart filter so agent never sees HTML artifacts in history
            self._session = ChartFilteredSession(sqlite_session)
            logger.info(f"Created ChartFilteredSession for session_id: {self.session_id}")
        return self._session
    
    def _create_mcp_server(self, tool_filter_func=None) -> MCPServerSse:
        """Create MCP server with optional tool filter."""
        sse_url = f"{self.mcp_url.rstrip('/')}/sse"
        return MCPServerSse(
            params={
                "url": sse_url,
                "timeout": 60,
                "sse_read_timeout": 600,
            },
            name="slurm-mcp",
            client_session_timeout_seconds=300,
            cache_tools_list=True,
            tool_filter=tool_filter_func,
        )
    
    async def _ensure_agents(self):
        """Initialize MCP servers and agents with tool guardrails on dangerous MCP tools."""
        if self._agents_initialized:
            logger.info("Agents already initialized, skipping")
            return
        
        logger.info("Initializing agents for the first time...")
        
        # Create MCP servers with tool filters
        # Analysis: read-only tools
        self._analysis_mcp = self._create_mcp_server(
            create_tool_filter_for_agent(ANALYSIS_TOOL_NAMES)
        )
        # Action: safe tools only via MCP (dangerous tools are guarded FunctionTools → direct HTTP)
        self._action_mcp = self._create_mcp_server(
            create_tool_filter_for_agent(SAFE_ACTION_TOOLS)
        )

        logger.info("Created MCP servers for sub-agents")
        
        # Tool handler to mark web_search results for stream detection
        def analysis_tool_handler(
            context: RunContextWrapper[Any],
            tool_results: List[FunctionToolResult]
        ) -> ToolsToFinalOutputResult:
            """Process tool results - mark web_search with [WEB_SEARCH]: prefix."""
            logger.info(f"[tool_use_behavior] Called with {len(tool_results)} results")
            
            for i, result in enumerate(tool_results):
                # Debug: log all attributes
                result_attrs = [a for a in dir(result) if not a.startswith('_')]
                logger.info(f"[tool_use_behavior] Result {i} attrs: {result_attrs}")
                
                # Try multiple ways to get tool name (FunctionTool vs MCP tool)
                tool_name = ""
                if hasattr(result, 'tool'):
                    tool_obj = result.tool
                    tool_name = getattr(tool_obj, 'name', str(tool_obj))
                    logger.info(f"[tool_use_behavior] Tool from result.tool: {tool_name}")
                if not tool_name and hasattr(result, 'name'):
                    tool_name = result.name
                    logger.info(f"[tool_use_behavior] Tool from result.name: {tool_name}")
                
                output_str = str(result.output) if hasattr(result, 'output') and result.output else ""
                logger.info(f"[tool_use_behavior] Tool: '{tool_name}', output len: {len(output_str)}, preview: {output_str[:200]}")
                
                # Check for web_search by name OR by output content
                is_web_search = (
                    "web_search" in tool_name.lower() or 
                    "[WEB_SEARCH]:" in output_str or
                    ("URL:" in output_str and "http" in output_str)
                )
                
                logger.info(f"[tool_use_behavior] is_web_search={is_web_search}")
                
                if is_web_search and output_str:
                    # Mark the output so streaming can detect it
                    if not output_str.startswith("[WEB_SEARCH]:"):
                        marked_output = f"[WEB_SEARCH]:\n{output_str}"
                    else:
                        marked_output = output_str
                    logger.info(f"[tool_use_behavior] RETURNING web search output ({len(marked_output)} chars)")
                    return ToolsToFinalOutputResult(
                        is_final_output=True,
                        final_output=marked_output
                    )
            
            logger.info("[tool_use_behavior] No web search detected, letting LLM continue")
            # Let LLM continue processing for other tools
            return ToolsToFinalOutputResult(is_final_output=False, final_output=None)
        
        # Create sub-agents with TOOL model (gpt-oss) - precise execution
        self.analysis_subagent = Agent(
            name="Analysis Sub-Agent",
            instructions=ANALYSIS_SUBAGENT_INSTRUCTIONS,
            model=self.tool_sdk_model,  # gpt-oss for tool execution
            model_settings=TOOL_MODEL_SETTINGS,
            mcp_servers=[self._analysis_mcp],
            tool_use_behavior=analysis_tool_handler,  # Mark web_search results
        )
        
        # Create guarded FunctionTools for dangerous actions (static — no MCP connection needed)
        dangerous_function_tools = self._create_guarded_dangerous_tools(mcp_base_url)
        
        # Action sub-agent with safe MCP tools + guarded dangerous tools
        self.action_subagent = Agent(
            name="Action Sub-Agent",
            instructions=ACTION_SUBAGENT_INSTRUCTIONS,
            model=self.tool_sdk_model,  # gpt-oss for tool execution
            model_settings=TOOL_MODEL_SETTINGS,
            mcp_servers=[self._action_mcp],
            tools=dangerous_function_tools,  # Add guarded dangerous tools
        )
        
        # Convert sub-agents to tools for main agent
        # Use custom_output_extractor to get structured data instead of conversational messages
        analyze_tool = self.analysis_subagent.as_tool(
            tool_name="analyze_cluster",
            tool_description="Gather raw cluster data: job status, queue info, node status. Pass a description of what data is needed. Returns structured data, not user-facing messages.",
            custom_output_extractor=extract_subagent_output,
        )
        
        action_tool = self.action_subagent.as_tool(
            tool_name="manage_jobs",
            tool_description="Execute job actions: cancel, hold, release, update, submit. Pass a description of the action. Returns execution results or lists missing required info.",
            custom_output_extractor=extract_subagent_output,
        )
        
        # Create confirm_action tool — executes pending actions via direct HTTP (no extra MCP conn)
        async def confirm_action_fn(ctx: ToolContext[SlurmContext], args: str) -> str:
            """
            Execute all pending dangerous actions after user confirms.
            Call this tool when the user has confirmed they want to proceed with a pending action.
            """
            import httpx
            import uuid as _uuid

            pending_actions = ctx.context.get_pending_actions()
            if not pending_actions:
                return "No pending actions to confirm. The action may have already been executed or cancelled."

            results = []
            for pending in pending_actions:
                tool_name  = pending["tool"]
                tool_args  = pending["args"]
                description = pending["description"]
                try:
                    payload = {
                        "jsonrpc": "2.0",
                        "id": str(_uuid.uuid4()),
                        "method": "tools/call",
                        "params": {"name": tool_name, "arguments": tool_args},
                    }
                    async with httpx.AsyncClient(timeout=30) as client:
                        resp = await client.post(f"{mcp_base_url}/message", json=payload)
                    if resp.status_code == 200:
                        content = resp.json().get("result", {}).get("content", [])
                        text = next(
                            (c.get("text", "") for c in content if c.get("type") == "text"),
                            str(resp.json().get("result", ""))
                        )
                        results.append(f"✅ {description}: {text}")
                    else:
                        results.append(f"❌ {description}: HTTP {resp.status_code}")
                except Exception as e:
                    logger.error(f"confirm_action error for {tool_name}: {e}")
                    results.append(f"❌ {description}: {e}")

            ctx.context.clear_pending()
            return "\n".join(results) if results else "No actions executed"
        
        confirm_tool = FunctionTool(
            name="confirm_action",
            description="Execute ALL queued dangerous actions after user confirms. Call when user says yes/ok/confirm/proceed.",
            params_json_schema={"type": "object", "properties": {}, "required": []},
            on_invoke_tool=confirm_action_fn,
            tool_input_guardrails=[_guard_pending_exists],
            tool_output_guardrails=_CONFIRM_OUTPUT_GUARDRAILS,
        )
        
        # Create cancel_action tool - allows agent to cancel pending actions when user declines
        async def cancel_action_fn(ctx: ToolContext[SlurmContext], args: str) -> str:
            """
            Cancel all pending dangerous actions.
            Call this tool when the user has declined/cancelled a pending action.
            """
            pending_actions = ctx.context.get_pending_actions()
            
            if not pending_actions:
                return "No pending actions to cancel."
            
            descriptions = [p["description"] for p in pending_actions]
            ctx.context.clear_pending()
            return f"❌ Cancelled {len(descriptions)} action(s): {', '.join(descriptions)}"
        
        cancel_tool = FunctionTool(
            name="cancel_action",
            description="Cancel ALL queued dangerous actions. Call when user says no/cancel/stop/nevermind.",
            params_json_schema={"type": "object", "properties": {}, "required": []},
            on_invoke_tool=cancel_action_fn,
        )
        
        # Create check_pending tool - allows agent to see what actions are waiting for confirmation
        async def check_pending_fn(ctx: ToolContext[SlurmContext], args: str) -> str:
            """
            Check what actions are pending confirmation.
            """
            pending = ctx.context.get_pending_actions()
            if not pending:
                return "No pending actions."
            
            descriptions = [f"- {p['description']}" for p in pending]
            return f"Pending actions awaiting confirmation:\n" + "\n".join(descriptions)
        
        check_pending_tool = FunctionTool(
            name="check_pending_actions",
            description="Check what dangerous actions are pending user confirmation.",
            params_json_schema={"type": "object", "properties": {}, "required": []},
            on_invoke_tool=check_pending_fn,
        )
        
        # Create wrapper for generate_chart that hides artifact from LLM
        # This calls MCP via HTTP directly (stateless mode), stores artifact in context, returns only summary
        # Using FunctionTool with ToolContext (not @function_tool - doesn't work inside methods)
        
        # Valid chart IDs - new conceptual charts + legacy charts
        VALID_CHARTS = {
            # New utility-focused charts
            "cluster_topology",   # Hierarchical view: cluster → partitions → nodes
            "job_lifecycle",      # Gantt timeline: job progression over time
            "resource_map",       # Who's using what: user → resources allocation
            "pending_analysis",   # Why waiting: pending jobs with reasons
            "system_health",      # Dashboard: health indicators and alerts
            # Legacy charts (still supported)
            "job_distribution", "node_status", "resource_usage", "queue_timeline", "live_dashboard"
        }
        
        # Need to capture self.mcp_url for use in the function
        mcp_base_url = self.mcp_url.rstrip('/')
        
        async def generate_chart_wrapper(ctx: ToolContext[SlurmContext], args_json: str) -> str:
            """
            Generate a chart visualization. The chart will be displayed to the user automatically.
            """
            import httpx
            import uuid
            
            # Parse chart_id from JSON args
            chart_id = "system_health"
            try:
                if args_json:
                    parsed = json.loads(args_json)
                    if isinstance(parsed, dict):
                        chart_id = parsed.get("chart_id", "system_health")
                    elif isinstance(parsed, str):
                        chart_id = parsed
            except json.JSONDecodeError:
                # Try to extract chart_id from malformed input
                pass
            
            # Normalize and validate chart_id
            chart_id_clean = (chart_id or "system_health").strip().lower().replace(" ", "_").replace("-", "_")
            
            # Map common variations to valid chart IDs
            if chart_id_clean not in VALID_CHARTS:
                # New charts - priority mappings
                if "health" in chart_id_clean or "status" in chart_id_clean or "overview" in chart_id_clean:
                    chart_id_clean = "system_health"
                elif "topology" in chart_id_clean or "structure" in chart_id_clean or "cluster" in chart_id_clean:
                    chart_id_clean = "cluster_topology"
                elif "pending" in chart_id_clean or "waiting" in chart_id_clean or "queue" in chart_id_clean or "why" in chart_id_clean:
                    chart_id_clean = "pending_analysis"
                elif "allocation" in chart_id_clean or "who" in chart_id_clean or "user" in chart_id_clean:
                    chart_id_clean = "resource_map"
                elif "lifecycle" in chart_id_clean or "timeline" in chart_id_clean or "gantt" in chart_id_clean:
                    chart_id_clean = "job_lifecycle"
                # Legacy mappings
                elif "dashboard" in chart_id_clean or "live" in chart_id_clean:
                    chart_id_clean = "live_dashboard"
                elif "distribution" in chart_id_clean or "pie" in chart_id_clean:
                    chart_id_clean = "job_distribution"
                elif "node" in chart_id_clean:
                    chart_id_clean = "node_status"
                elif "resource" in chart_id_clean or "usage" in chart_id_clean or "cpu" in chart_id_clean:
                    chart_id_clean = "resource_usage"
                elif "job" in chart_id_clean:
                    chart_id_clean = "job_lifecycle"
                else:
                    chart_id_clean = "system_health"
                    logger.warning(f"Unknown chart_id '{chart_id}', defaulting to system_health")
            
            logger.info(f"generate_chart: chart_id='{chart_id_clean}' (original: '{chart_id}')")
            
            try:
                # Call MCP server directly via HTTP in STATELESS mode (no session_id)
                message_url = f"{mcp_base_url}/message"
                
                jsonrpc_request = {
                    "jsonrpc": "2.0",
                    "id": str(uuid.uuid4()),
                    "method": "tools/call",
                    "params": {
                        "name": "generate_chart",
                        "arguments": {"chart_id": chart_id_clean}
                    }
                }
                
                async with httpx.AsyncClient(timeout=60) as client:
                    response = await client.post(message_url, json=jsonrpc_request)
                    
                    if response.status_code != 200:
                        logger.warning(f"MCP returned {response.status_code}: {response.text}")
                        return f"❌ MCP error: {response.status_code}"
                    
                    result_data = response.json().get("result", {})
                
                # Parse the response to extract artifact
                summary = f"✅ Chart '{chart_id_clean}' generated"
                artifact = None
                
                content_items = result_data.get("content", [])
                for item in content_items:
                    if item.get("type") == "resource":
                        # Check for resource with mermaid mimetype
                        resource = item.get("resource", {})
                        if resource.get("mimeType") == "text/x-mermaid":
                            artifact = resource.get("text")
                    elif item.get("type") == "text":
                        # Check if text content is mermaid code
                        text = item.get("text", "")
                        # Detect mermaid chart types (case-insensitive check for common patterns)
                        mermaid_markers = [
                            "xychart-beta", "xychart", 
                            "pie", "pie showData",
                            "gantt", 
                            "flowchart", "flowchart TB", "flowchart LR",
                            "graph ", "graph TB", "graph LR",
                            "%%{init:",  # Mermaid config directive
                            "---\nconfig",  # YAML frontmatter for mermaid
                        ]
                        text_lower = text.lower()
                        is_mermaid = any(marker.lower() in text_lower for marker in mermaid_markers)
                        # Also check if starts with --- (YAML frontmatter)
                        if text.strip().startswith("---"):
                            is_mermaid = True
                        
                        if is_mermaid:
                            artifact = text
                        else:
                            summary = text
                
                # Store artifact in context if found
                if artifact:
                    ctx.context.add_chart_artifact(artifact)
                    logger.info(f"Chart artifact stored in context ({len(artifact)} chars)")
                    logger.info(f"Context id: {id(ctx.context)}, artifacts count: {len(ctx.context.chart_artifacts)}")
                else:
                    logger.warning("No mermaid artifact found in MCP response")
                    logger.warning(f"Content items received: {content_items}")
                
                # Return only summary to LLM - artifact is hidden!
                return summary
                    
            except Exception as e:
                logger.error(f"generate_chart error: {e}")
                import traceback
                traceback.print_exc()
                return f"❌ Chart generation failed: {str(e)}"
        
        # Create FunctionTool for generate_chart
        chart_tool = FunctionTool(
            name="generate_chart",
            description="""Generate a visualization chart.

Charts for operations:
- system_health: Dashboard with health indicators and alerts (DEFAULT)
- cluster_topology: Cluster structure (partitions → nodes → states)  
- pending_analysis: Why jobs are waiting (bottleneck diagnosis)
- resource_map: Who's using what resources
- job_lifecycle: Gantt timeline of job progression

Legacy: job_distribution, node_status, resource_usage, queue_timeline, live_dashboard""",
            params_json_schema={
                "type": "object",
                "properties": {
                    "chart_id": {
                        "type": "string",
                        "description": "Chart to generate: system_health, cluster_topology, pending_analysis, resource_map, job_lifecycle"
                    }
                },
                "required": ["chart_id"]
            },
            on_invoke_tool=generate_chart_wrapper,
        )
        
        # Debug: log tool info
        logger.info(f"Chart tool created: {chart_tool.name}")
        
        # Create main agent with REASONING model (qwen3-coder) - thinks before acting
        # Main agent uses wrapper FunctionTool for charts (hides artifact from LLM)
        all_tools = [analyze_tool, action_tool, confirm_tool, cancel_tool, check_pending_tool, chart_tool]
        logger.info(f"Registering {len(all_tools)} tools with main agent: {[getattr(t, 'name', str(t)) for t in all_tools]}")
        
        self.main_agent = Agent(
            name="Slurm Assistant",
            instructions=MAIN_AGENT_INSTRUCTIONS,
            model=self.reasoning_sdk_model,  # qwen3-coder for reasoning
            model_settings=REASONING_MODEL_SETTINGS,
            # NO mcp_servers - charts go through wrapper tool that hides artifacts
            tools=all_tools,
        )
        
        self._agents_initialized = True
        logger.info("Agents initialized with tool guardrails on dangerous MCP tools")
    
    def _create_guarded_dangerous_tools(self, mcp_base_url: str) -> list:
        """
        Build FunctionTools for dangerous MCP tools using hardcoded schemas.
        No MCP connection needed — schemas are static and match the server exactly.
        Each tool queues the call for confirmation instead of executing immediately.
        """
        guarded_tools = []

        for tool_name, meta in _DANGEROUS_TOOL_SCHEMAS.items():
            def make_invoke_fn(captured_name: str):
                async def invoke_dangerous_tool(ctx: ToolContext[SlurmContext], args_json: str) -> str:
                    """Queue dangerous action for user confirmation."""
                    try:
                        args = json.loads(args_json) if args_json else {}
                    except Exception:
                        args = {}

                    args_str = ", ".join(f"{k}={v}" for k, v in args.items()) if args else ""
                    description = f"{captured_name}({args_str})"
                    ctx.context.add_pending_action(captured_name, args, description)
                    total = len(ctx.context.get_pending_actions())
                    logger.info(f"Queued dangerous action: {description} (total: {total})")
                    return f"QUEUED: {description} ({total} action(s) pending confirmation)"
                return invoke_dangerous_tool

            guarded_tools.append(FunctionTool(
                name=tool_name,
                description=meta["description"],
                params_json_schema=meta["schema"],
                on_invoke_tool=make_invoke_fn(tool_name),
                tool_input_guardrails=_TOOL_INPUT_GUARDRAILS.get(tool_name),
            ))
            logger.info(f"Registered guarded FunctionTool: {tool_name}")

        return guarded_tools
    
    def _create_context(self) -> SlurmContext:
        """Create a new SlurmContext for a run."""
        return SlurmContext(session_id=self.session_id)
    
    async def run(self, user_message: str) -> Dict[str, Any]:
        """Run the agent system (non-streaming) with session memory and context."""
        try:
            logger.info(f"Processing: {user_message[:100]}...")
            await self._ensure_agents()
            
            # Get session for conversation history
            session = self._get_session()
            
            # Create context
            ctx = self._create_context()
            
            logger.info("Opening MCP connections...")
            async with self._analysis_mcp, self._action_mcp:
                logger.info("MCP connections opened, running agent...")
                result = await Runner.run(
                    starting_agent=self.main_agent,
                    input=user_message,
                    session=session,
                    context=ctx,  # Pass SlurmContext
                    max_turns=100  # Increased from default 10 for complex multi-agent workflows
                )
                logger.info(f"Agent run completed: {result.last_agent.name}")
                
                # Get chart artifacts from context (stored by wrapper tool)
                chart_artifacts = ctx.chart_artifacts
                logger.info(f"Charts in context: {len(chart_artifacts)}")
                
                # Build response with chart artifacts appended
                final_message = str(result.final_output)
                for chart_code in chart_artifacts:
                    final_message += self._wrap_chart_artifact(chart_code)
                
                return {
                    "success": True,
                    "agent": result.last_agent.name,
                    "type": "response",
                    "message": final_message,
                    "executed": True,
                    "pending_actions": ctx.get_pending_actions()
                }
                
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "type": "error",
                "message": str(e),
                "executed": False
            }
    
    async def run_streaming(
        self,
        user_message: str,
        conversation_history: Optional[list] = None  # Kept for API compatibility
    ) -> AsyncGenerator[Dict[str, Any], None]:
        try:
            await self._ensure_agents()
            session = self._get_session()
            ctx     = self._create_context()

            async with self._analysis_mcp, self._action_mcp:
                result = Runner.run_streamed(
                    starting_agent=self.main_agent,
                    input=user_message,
                    session=session,
                    context=ctx,
                )

                _streamed_parts = []
                _emitted_final = False

                async for event in result.stream_events():

                    # ── Real model reasoning tokens ────────────────────────────
                    # The agents SDK converts Ollama delta.reasoning into
                    # Responses-API events with type "response.reasoning_text.delta"
                    # and OpenAI delta.reasoning_content into
                    # "response.reasoning_summary_text.delta".
                    # Both carry the text in event.data.delta.
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
                                    logger.debug(f"Thinking token: {r[:60]!r}")
                                    yield {"type": "thinking", "content": r}
                            elif event_data_type == "response.output_text.delta":
                                t = getattr(event_data, "delta", None)
                                if t:
                                    _streamed_parts.append(t)
                                    yield {"type": "token", "content": t}
                        except Exception:
                            pass
                        continue

                    # ── Run items (tool calls, outputs, final message) ─────────
                    if event.type != "run_item_stream_event":
                        continue

                    item = event.item

                    if item.type == "tool_call_item":
                        name     = getattr(item.raw_item, "name", "") if hasattr(item, "raw_item") else ""
                        args_raw = getattr(item.raw_item, "arguments", "{}") if hasattr(item, "raw_item") else "{}"
                        try:
                            args = json.loads(args_raw)
                        except Exception:
                            args = {}
                        if name:
                            logger.info(f"Tool call: {name}, args: {json.dumps(args)[:200]}")
                            yield {"type": "status", "message": _format_tool_call(name, args)}

                    elif item.type == "tool_call_output_item":
                        output_str = str(item.output or "")
                        summary = _brief_output_summary(output_str)
                        if summary:
                            logger.info(f"Tool output (first 300): {output_str[:300]}")
                            yield {"type": "status", "message": summary}
                        if output_str.strip():
                            yield {"type": "tool_output", "output": output_str.strip()}
                        if "[WEB_SEARCH]:" in output_str:
                            urls = re.findall(r"URL:\s*(https?://[^\s\n'\"]+)", output_str)
                            if urls:
                                yield {"type": "web_results", "urls": urls[:5]}

                    elif item.type == "message_output_item":
                        content = ItemHelpers.text_message_output(item)
                        if content:
                            clean = self._clean_hallucinated_calls(content)
                            if clean.strip():
                                full = clean
                                for chart in ctx.chart_artifacts:
                                    full += self._wrap_chart_artifact(chart)
                                logger.info(f"Final response length: {len(full)}")
                                yield {"type": "final_answer", "message": full}
                                _streamed_parts.clear()
                                _emitted_final = True

                # Fallback 1: streamed text deltas but no final_answer from message_output_item
                if not _emitted_final and _streamed_parts:
                    full = self._clean_hallucinated_calls("".join(_streamed_parts))
                    if full.strip():
                        for chart in ctx.chart_artifacts:
                            full += self._wrap_chart_artifact(chart)
                        logger.info(f"Fallback final_answer from streamed tokens: {len(full)} chars")
                        yield {"type": "final_answer", "message": full}
                        _emitted_final = True

                # Fallback 2: use SDK's final_output (always populated after streaming ends)
                if not _emitted_final:
                    sdk_output = str(result.final_output or "")
                    if sdk_output.strip():
                        full = self._clean_hallucinated_calls(sdk_output)
                        for chart in ctx.chart_artifacts:
                            full += self._wrap_chart_artifact(chart)
                        logger.info(f"Fallback final_answer from SDK final_output: {len(full)} chars")
                        yield {"type": "final_answer", "message": full}

            yield {"type": "done", "pending_actions": ctx.get_pending_actions()}

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            import traceback
            traceback.print_exc()
            error_msg = str(e)
            if "invalid tool call arguments" in error_msg.lower():
                try:
                    await self.clear_session()
                    error_msg = "Memory cleared due to a hiccup — please retry."
                except Exception:
                    error_msg = "Encountered an issue. Please start a new conversation."
            elif "Invalid JSON" in error_msg:
                error_msg = "Technical issue with the response. Please rephrase."
            yield {"type": "error", "message": error_msg}

    def _clean_hallucinated_calls(self, text: str) -> str:
        """Remove hallucinated XML function calls from model output."""
        import re
        # Remove <function=...>...</tool_call> patterns
        text = re.sub(r'<function=[^>]*>.*?</tool_call>', '', text, flags=re.DOTALL)
        # Remove standalone tags
        text = re.sub(r'</?function[^>]*>', '', text)
        text = re.sub(r'</?parameter[^>]*>', '', text)
        text = re.sub(r'</?tool_call>', '', text)
        return text.strip()
    
    def _wrap_chart_artifact(self, mermaid_code: str) -> str:
        """
        Wrap Mermaid diagram for OpenWebUI native rendering.
        
        OpenWebUI has built-in Mermaid support with pan/zoom capabilities.
        Charts are wrapped in ```mermaid code blocks which OpenWebUI renders
        as interactive SVG diagrams.
        """
        # OpenWebUI renders ```mermaid blocks as interactive SVG with pan/zoom
        # No visible markers - we detect mermaid blocks directly for filtering
        return f"\n\n```mermaid\n{mermaid_code}\n```"
    
    @staticmethod
    def strip_chart_artifacts(text: str) -> str:
        """Remove chart artifacts (mermaid blocks) from text for history filtering."""
        if not text:
            return text
        # Remove mermaid code blocks from history to keep context clean
        pattern = r'```mermaid\n.*?```'
        return re.sub(pattern, '', text, flags=re.DOTALL).strip()
    
    async def clear_session(self):
        """Clear conversation history for this session."""
        if self._session:
            await self._session.clear_session()
            logger.info(f"Cleared session history for: {self.session_id}")
    
    async def disconnect(self):
        """Clean up."""
        self._analysis_mcp = None
        self._action_mcp = None
        self._session = None
        self._agents_initialized = False
    
    async def __aenter__(self):
        await self._ensure_agents()
        return self
    
    async def __aexit__(self, *args):
        await self.disconnect()


# ============ Convenience Functions ============

async def run_multi_agent(message: str, mcp_url: str = "http://localhost:3002") -> Dict[str, Any]:
    """Quick one-shot execution."""
    system = SlurmMultiAgentSystem(mcp_url=mcp_url)
    try:
        return await system.run(message)
    finally:
        await system.disconnect()


async def run_multi_agent_streaming(
    message: str, 
    conversation_history: Optional[list] = None, 
    mcp_url: str = "http://localhost:3002"
) -> AsyncGenerator[Dict[str, Any], None]:
    """Quick one-shot streaming execution."""
    system = SlurmMultiAgentSystem(mcp_url=mcp_url)
    try:
        async for event in system.run_streaming(message, conversation_history):
            yield event
    finally:
        await system.disconnect()
