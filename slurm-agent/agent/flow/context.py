"""
Session & context primitives for the Slurm agent.

- ChartFilteredSession  — wraps SQLiteSession, strips mermaid blocks from history reads
- PendingActionsStore   — SQLite-backed queue for dangerous actions awaiting confirmation
- SlurmContext          — per-run context injected via RunContextWrapper
"""
import copy
import json
import logging
import re
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

from agents import SQLiteSession

logger = logging.getLogger(__name__)


# ── Chart-filtered session ────────────────────────────────────────────────────

class ChartFilteredSession:
    """Wraps SQLiteSession so the LLM never sees mermaid artifacts in history.
    
    Implements the full Session ABC interface: get_items, add_items, pop_item, clear_session.
    """

    def __init__(self, session: SQLiteSession):
        self._session = session

    # Forward session_settings so the SDK can read them
    @property
    def session_settings(self):
        return getattr(self._session, 'session_settings', None)

    @staticmethod
    def _strip_charts(text: str) -> str:
        if not text:
            return text
        return re.sub(r"```mermaid\n.*?```", "", text, flags=re.DOTALL).strip()

    @staticmethod
    def _sanitize_tool_arguments(args: str) -> str:
        """Fix malformed tool call arguments produced by Ollama streaming.

        Ollama/gemma4 sometimes streams the same JSON object multiple times
        (e.g., '{}{}{}' instead of '{}'), producing invalid JSON that causes
        400 errors when replayed in conversation history.
        """
        if not args or not isinstance(args, str):
            return args
        args = args.strip()
        if not args:
            return "{}"
        # Fast path: already valid JSON
        try:
            json.loads(args)
            return args
        except (json.JSONDecodeError, ValueError):
            pass
        # Try to extract the first valid JSON object from concatenated duplicates
        # e.g., '{}{}{}' → '{}', '{"a":1}{"a":1}' → '{"a":1}'
        if args.startswith("{"):
            depth = 0
            for i, ch in enumerate(args):
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        candidate = args[: i + 1]
                        try:
                            json.loads(candidate)
                            return candidate
                        except (json.JSONDecodeError, ValueError):
                            break
        return "{}"

    @staticmethod
    def _filter_item(item):
        # Sanitize function_call arguments (fixes Ollama streaming duplicates)
        if isinstance(item, dict) and item.get("type") == "function_call":
            raw_args = item.get("arguments", "")
            cleaned_args = ChartFilteredSession._sanitize_tool_arguments(raw_args)
            if cleaned_args != raw_args:
                item = {**item, "arguments": cleaned_args}
            return item

        if hasattr(item, "content"):
            if isinstance(item.content, str):
                cleaned = ChartFilteredSession._strip_charts(item.content)
                if hasattr(item, "_replace"):
                    return item._replace(content=cleaned)
                try:
                    new = copy.copy(item)
                    new.content = cleaned
                    return new
                except Exception:
                    pass
        return item

    async def get_items(self, limit=None):
        """Retrieve session items with mermaid blocks stripped (SDK Session ABC)."""
        items = await self._session.get_items(limit=limit)
        return [self._filter_item(i) for i in items] if items else items

    @staticmethod
    def _is_empty_assistant_message(item) -> bool:
        """Check if an item is an assistant message with no real content."""
        if not isinstance(item, dict):
            return False
        role = item.get("role", "")
        if role != "assistant":
            return False
        content = item.get("content", "")
        if isinstance(content, list):
            return all(
                not (isinstance(p, dict) and p.get("text", "").strip())
                for p in content
            )
        if isinstance(content, str):
            return not content.strip()
        return False

    @classmethod
    def _clean_history(cls, items: list) -> list:
        """Remove empty assistant messages and orphaned trailing user messages.

        Prevents poisoned sessions where the model learns to mimic the pattern of
        empty responses, and prevents duplicate user-user sequences from confusing it.
        """
        if not items:
            return items
        # 1. Remove empty assistant messages
        cleaned = [i for i in items if not cls._is_empty_assistant_message(i)]
        # 2. Remove trailing orphan: if the last item is a user message with no
        #    assistant follow-up it's leftover from a failed run — drop it
        while cleaned and isinstance(cleaned[-1], dict) and cleaned[-1].get("role") == "user":
            cleaned.pop()
        return cleaned

    async def get_items(self, limit=None):
        """Retrieve session items with mermaid blocks stripped and history cleaned."""
        items = await self._session.get_items(limit=limit)
        if items:
            items = [self._filter_item(i) for i in items]
            items = self._clean_history(items)
        return items or []

    async def add_items(self, items):
        return await self._session.add_items(items)

    async def pop_item(self):
        """Remove and return the most recent item (SDK Session ABC)."""
        return await self._session.pop_item()

    async def clear_session(self):
        return await self._session.clear_session()

    def __getattr__(self, name):
        return getattr(self._session, name)


# ── Pending-actions store ─────────────────────────────────────────────────────

class PendingActionsStore:
    """Persistent SQLite queue for dangerous Slurm actions awaiting confirmation."""

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
                    actions    TEXT,
                    created_at REAL
                )
            """)
            conn.commit()
            conn.close()

    def store(self, session_id: str, actions: List[Dict[str, Any]]):
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "INSERT OR REPLACE INTO pending_actions VALUES (?, ?, ?)",
                (session_id, json.dumps(actions), time.time()),
            )
            conn.commit()
            conn.close()
        logger.debug(f"Stored {len(actions)} pending action(s) for {session_id}")

    def get(self, session_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            row = conn.execute(
                "SELECT actions, created_at FROM pending_actions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            conn.close()
        if row:
            actions_json, created_at = row
            if time.time() - created_at < 3600:
                return json.loads(actions_json)
        return []

    def clear(self, session_id: str):
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute("DELETE FROM pending_actions WHERE session_id = ?", (session_id,))
            conn.commit()
            conn.close()
        logger.debug(f"Cleared pending actions for {session_id}")


# Module-level singleton so the same DB is shared within a process
_pending_store = PendingActionsStore()


# ── Run context ───────────────────────────────────────────────────────────────

@dataclass
class SlurmContext:
    """Per-run context passed through RunContextWrapper.context."""

    session_id: str = "default"
    chart_artifacts: List[str] = field(default_factory=list)
    operator_actions_taken: int = 0  # count of dangerous tools executed this run
    operator_required_tool: str = ""  # optional per-handoff required action tool
    operator_targets: List[str] = field(default_factory=list)  # targets captured at latest handoff
    operator_discovery_calls: int = 0  # bounded pre-action discovery reads per handoff
    operator_no_targets_found: bool = False  # set when discovery confirms no eligible targets

    def mark_operator_action(self):
        self.operator_actions_taken += 1

    def mark_operator_discovery(self):
        self.operator_discovery_calls += 1

    def mark_no_targets_found(self):
        self.operator_no_targets_found = True

    def reset_operator_handoff_state(self):
        self.operator_actions_taken = 0
        self.operator_discovery_calls = 0
        self.operator_no_targets_found = False

    # ── chart artifacts ──────────────────────────────────────────────────────
    def add_chart_artifact(self, mermaid_code: str):
        self.chart_artifacts.append(mermaid_code)
        logger.debug(f"Chart stored ({len(mermaid_code)} chars), total={len(self.chart_artifacts)}")

    # ── pending actions ──────────────────────────────────────────────────────
    def get_pending_actions(self) -> List[Dict[str, Any]]:
        return _pending_store.get(self.session_id)

    def add_pending_action(self, tool_name: str, args: Dict[str, Any], description: str):
        actions = self.get_pending_actions()
        actions.append({"tool": tool_name, "args": args, "description": description})
        _pending_store.store(self.session_id, actions)
        logger.info(f"Queued: {description}")

    def clear_pending(self):
        _pending_store.clear(self.session_id)
