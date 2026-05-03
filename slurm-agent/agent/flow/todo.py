"""
TodoTracker — LLM-generated task planning for the Slurm agent.

The agent generates its own plan via a lightweight LLM call, then tracks
progress as tool calls execute. Plan snapshots stream to the frontend as
session-level state (not per-message).
"""
import json
import logging
import re
from typing import Optional

from .model import (
    DEFAULT_MODEL,
    LLM_PROVIDER,
    SPECIALIST_MODEL,
    OLLAMA_BASE_URL,
    GITHUB_TOKEN,
    COPILOT_BASE_URL,
    COPILOT_MODEL,
    GITHUB_MODELS_BASE_URL,
    GITHUB_MODELS_MODEL,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_MODEL,
    OPENAI_BASE_URL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    cloud_client_kwargs,
    normalize_provider,
)

logger = logging.getLogger(__name__)

_PLAN_SYSTEM_PROMPT = """\
You are a task planner for a Slurm HPC assistant with two agents:
- Observer: read-only tools (squeue, sinfo, sacct, etc.)
- Operator: action tools (sbatch, scancel, scontrol_hold, etc.)

Given a user request, output a short task plan as a JSON array of strings.

Rules:
- Output ONLY a JSON array of strings. No markdown, no explanation.
- 3-5 steps max. Be specific to the request.
- Do NOT name tool names.
- For actions (submit, cancel, hold, release): say "Hand off to Operator to ...".
- For read-only tasks: just describe what to check.
- Last step is always the deliverable.

Examples:
User: "check cluster health"
["Check partition and node states","Review job queue","Check scheduler metrics","Summarize cluster health"]

User: "cancel jobs 12345 12346 12347"
["Verify jobs exist","Hand off to Operator to cancel all 3 jobs","Report results"]

User: "submit these scripts: sleep.sh, gpu_test.sh"
["Hand off to Operator to submit all scripts","Verify jobs are queued","Report submission results"]

User: "why is job 5555 pending"
["Check job status and pending reason","Check node availability","Report root cause and fix"]

User: "run all these" (with 3 attached files)
["Hand off to Operator to submit all 3 scripts","Verify jobs are queued","Report results"]
"""


class TodoTracker:
    """Session-scoped task tracker with LLM-generated plans."""

    def __init__(
        self,
        llm_provider: str = LLM_PROVIDER,
        main_model: str = DEFAULT_MODEL,
        specialist_provider: Optional[str] = None,
        specialist_model: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ):
        self.items: list[dict] = []  # [{id, title, status}]
        self._active_step: Optional[int] = None
        self._changed = False
        self.llm_provider = normalize_provider(llm_provider or LLM_PROVIDER)
        self.main_model = (main_model or DEFAULT_MODEL).strip()
        self.specialist_provider = normalize_provider(specialist_provider or self.llm_provider)
        if self.specialist_provider == "azure-openai":
            default_specialist = AZURE_OPENAI_MODEL
        elif self.specialist_provider == "openai":
            default_specialist = OPENAI_MODEL
        elif self.specialist_provider == "copilot":
            default_specialist = COPILOT_MODEL
        elif self.specialist_provider == "github-models":
            default_specialist = GITHUB_MODELS_MODEL
        else:
            default_specialist = SPECIALIST_MODEL
        self.specialist_model = (specialist_model or default_specialist).strip()
        self.openai_api_key = openai_api_key or OPENAI_API_KEY

    @property
    def has_plan(self) -> bool:
        return len(self.items) > 0

    @property
    def has_active_plan(self) -> bool:
        """True if there's a plan with uncompleted steps."""
        return any(item["status"] != "completed" for item in self.items)

    def reset(self) -> None:
        """Clear all plan items (e.g. when a new instruction arrives mid-HITL)."""
        self.items = []
        self._active_step = None
        self._changed = True

    def set_from_tool(self, items: list[dict]) -> None:
        """Apply an explicit LLM-provided todo list (called by the manage_todos tool).

        Accepts the same schema as Copilot's manage_todo_list:
          [{id, title, status}] where status ∈ {not-started, in-progress, completed}
        """
        _valid = {"not-started", "in-progress", "completed"}
        self.items = [
            {
                "id": int(item.get("id", i + 1)),
                "title": str(item.get("title", ""))[:100],
                "status": item["status"] if item.get("status") in _valid else "not-started",
            }
            for i, item in enumerate(items)
            if isinstance(item, dict) and str(item.get("title", "")).strip()
        ]
        self._active_step = None
        for i, item in enumerate(self.items):
            if item["status"] == "in-progress":
                self._active_step = i
                break
        self._changed = True

    async def generate_plan(self, user_message: str) -> bool:
        """Generate a plan via lightweight LLM call. Returns True if successful."""
        try:
            from openai import AsyncOpenAI
            try:
                from openai import AsyncAzureOpenAI
            except ImportError:
                AsyncAzureOpenAI = None
            provider = self.specialist_provider
            if provider == "copilot":
                if not GITHUB_TOKEN:
                    raise RuntimeError("GITHUB_TOKEN missing for copilot provider")
                client = AsyncOpenAI(base_url=COPILOT_BASE_URL, api_key=GITHUB_TOKEN, **cloud_client_kwargs())
                _model = self.specialist_model or COPILOT_MODEL
                _create_kwargs: dict = {}
            elif provider == "github-models":
                if not GITHUB_TOKEN:
                    raise RuntimeError("GITHUB_TOKEN missing for github-models provider")
                client = AsyncOpenAI(base_url=GITHUB_MODELS_BASE_URL, api_key=GITHUB_TOKEN, **cloud_client_kwargs())
                _model = self.specialist_model or GITHUB_MODELS_MODEL
                _create_kwargs = {}
            elif provider == "openai":
                if not self.openai_api_key:
                    raise RuntimeError("OPENAI_API_KEY missing for openai provider")
                client = AsyncOpenAI(base_url=OPENAI_BASE_URL, api_key=self.openai_api_key, **cloud_client_kwargs())
                _model = self.specialist_model or OPENAI_MODEL
                _create_kwargs = {}
            elif provider == "azure-openai":
                if AsyncAzureOpenAI is None:
                    raise RuntimeError("Installed openai package does not provide AsyncAzureOpenAI")
                if not AZURE_OPENAI_ENDPOINT:
                    raise RuntimeError("AZURE_OPENAI_ENDPOINT missing for azure-openai provider")
                if not AZURE_OPENAI_API_KEY:
                    raise RuntimeError("AZURE_OPENAI_API_KEY or AZURE_OPENAI_KEY missing for azure-openai provider")
                client = AsyncAzureOpenAI(
                    azure_endpoint=AZURE_OPENAI_ENDPOINT,
                    api_key=AZURE_OPENAI_API_KEY,
                    api_version=AZURE_OPENAI_API_VERSION,
                    **cloud_client_kwargs(),
                )
                _model = self.specialist_model or AZURE_OPENAI_MODEL
                _create_kwargs = {}
            else:
                client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
                _model = self.specialist_model or SPECIALIST_MODEL
                _create_kwargs = {"extra_body": {"think": False}}
            resp = await client.chat.completions.create(
                model=_model,
                messages=[
                    {"role": "system", "content": _PLAN_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.1,
                max_tokens=300,
                **_create_kwargs,
            )
            raw = (resp.choices[0].message.content or "").strip()
            logger.info(f"Plan LLM raw output: {raw[:300]}")
            steps = self._parse_plan(raw)
            if steps:
                self._set_plan(steps)
                logger.info(f"Generated plan ({len(steps)} steps): {steps}")
                return True
            else:
                logger.warning(f"Plan parse returned empty from raw: {raw[:300]}")
        except Exception as e:
            logger.warning(f"Plan generation failed: {e}", exc_info=True)
        return False

    @staticmethod
    def _parse_plan(raw: str) -> list[str]:
        """Parse LLM output into list of step titles."""
        # Strip thinking tags (qwen3, gemma4, etc.)
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
        # Strip markdown code fences
        raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        raw = re.sub(r"\s*```$", "", raw.strip())
        # Try to extract JSON array from anywhere in the text
        m = re.search(r"\[.*\]", raw, flags=re.DOTALL)
        if m:
            try:
                parsed = json.loads(m.group())
                if isinstance(parsed, list) and all(isinstance(s, str) for s in parsed):
                    return [s.strip() for s in parsed if s.strip()][:6]
            except json.JSONDecodeError:
                pass
        # Direct JSON parse
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list) and all(isinstance(s, str) for s in parsed):
                return [s.strip() for s in parsed if s.strip()][:6]
        except json.JSONDecodeError:
            pass
        # Fallback: numbered/bulleted list
        lines = []
        for line in raw.split("\n"):
            line = re.sub(r"^\s*\d+[\.\)]\s*", "", line).strip()
            line = re.sub(r"^[-*]\s*", "", line).strip()
            if line and len(line) > 3:
                lines.append(line)
        return lines[:6] if lines else []

    def _set_plan(self, step_titles: list[str]):
        self.items = [
            {"id": i + 1, "title": t, "status": "not-started"}
            for i, t in enumerate(step_titles)
        ]
        self._active_step = None
        self._changed = True

    def on_tool_start(self, tool_name: str):
        """Advance: complete current step, start next not-started one."""
        if tool_name == "manage_todos":
            return  # plan is set explicitly by the tool; skip auto-advance
        if not self.items:
            return
        if self._active_step is not None:
            cur = self.items[self._active_step]
            if cur["status"] == "in-progress":
                cur["status"] = "completed"
        for i, item in enumerate(self.items):
            if item["status"] == "not-started":
                item["status"] = "in-progress"
                self._active_step = i
                self._changed = True
                return

    def on_tool_complete(self, tool_name: str):
        """Mark current active step completed."""
        if self._active_step is not None and self._active_step < len(self.items):
            cur = self.items[self._active_step]
            if cur["status"] == "in-progress":
                cur["status"] = "completed"
                self._changed = True

    def on_response_start(self):
        """When text generation starts, advance to the final step."""
        if not self.items:
            return
        if self._active_step is not None:
            cur = self.items[self._active_step]
            if cur["status"] == "in-progress":
                cur["status"] = "completed"
        for item in self.items:
            if item["status"] == "not-started":
                item["status"] = "in-progress"
                self._changed = True
                break

    def on_done(self):
        """Mark all remaining as completed."""
        for item in self.items:
            if item["status"] != "completed":
                item["status"] = "completed"
                self._changed = True

    def format_for_llm(self) -> str:
        """Format plan for injection into agent context."""
        if not self.items:
            return ""
        lines = ["[PLAN] You MUST follow these steps in order:"]
        for item in self.items:
            marker = "✓" if item["status"] == "completed" else "→" if item["status"] == "in-progress" else " "
            lines.append(f"  [{marker}] {item['id']}. {item['title']}")

        # Only inject the operator-handoff urgency when the FIRST non-completed step
        # explicitly requires it — avoids triggering on later operator steps.
        first_pending = next(
            (item for item in self.items if item["status"] != "completed"), None
        )
        first_needs_handoff = first_pending and (
            "hand off" in first_pending["title"].lower()
            or ("operator" in first_pending["title"].lower() and "hand off" in first_pending["title"].lower())
        )
        if first_needs_handoff:
            lines.append("IMPORTANT: The next step requires transfer_to_operator. Do it NOW. Do NOT run read-only tools first.")
        else:
            lines.append("Execute each step by calling tools. Do NOT skip steps. Do NOT repeat completed steps.")
        return "\n".join(lines)

    def get_snapshot(self) -> Optional[list[dict]]:
        """Return items if changed, else None."""
        if not self._changed or not self.items:
            return None
        self._changed = False
        return [dict(item) for item in self.items]

    def get_items(self) -> list[dict]:
        return [dict(item) for item in self.items]

    def restore(self, items: list[dict]):
        """Restore from saved state (HITL resume)."""
        self.items = [dict(item) for item in items]
        self._changed = True
        self._active_step = None
        for i, item in enumerate(self.items):
            if item["status"] == "in-progress":
                self._active_step = i
                break
