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
    """Wraps SQLiteSession so the LLM never sees mermaid artifacts in history."""

    def __init__(self, session: SQLiteSession):
        self._session = session

    @staticmethod
    def _strip_charts(text: str) -> str:
        if not text:
            return text
        return re.sub(r"```mermaid\n.*?```", "", text, flags=re.DOTALL).strip()

    @staticmethod
    def _filter_item(item):
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

    async def get_session_history(self):
        history = await self._session.get_session_history()
        return [self._filter_item(i) for i in history] if history else history

    async def add_items(self, items):
        return await self._session.add_items(items)

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
