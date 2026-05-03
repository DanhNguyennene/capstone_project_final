"""Structured admission control for Slurm action tools.

SlurmGuard intentionally does not inspect raw user prompts. It admits or blocks
dangerous calls using only structured handoff fields, discovered tool schemas,
tool arguments, Operator discovery evidence, and optional live Slurm reads.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Mapping, Sequence

from .context import SlurmContext
from .tool_discovery import DiscoveredTool


LiveMcpCall = Callable[[str, dict[str, Any]], Awaitable[list]]

VALID_TARGET_SCOPES = {"explicit", "discovery", "none"}
DISCOVERY_SCOPES = {"broad", "dynamic", "discovery", "discover", "resolve", "resolved", "query"}
EXPLICIT_SCOPES = {"explicit", "ids", "id", "targets", "target", "provided", "concrete"}
NO_TARGET_SCOPES = {"none", "no_target", "not_applicable", "na", "cluster", "global"}

JOB_ID_TOOLS = {
    "scancel",
    "scontrol_hold",
    "scontrol_release",
    "scontrol_requeue",
    "scontrol_suspend",
    "scontrol_resume_job",
}

ACTIVE_JOB_STATE_POLICY = {
    "scancel": {"RUNNING", "PENDING", "SUSPENDED", "CONFIGURING", "COMPLETING", "RESIZING"},
    "scontrol_hold": {"PENDING"},
    "scontrol_release": {"PENDING"},
    "scontrol_suspend": {"RUNNING"},
    "scontrol_resume_job": {"SUSPENDED"},
    "scontrol_update": {"RUNNING", "PENDING", "SUSPENDED", "CONFIGURING", "COMPLETING", "RESIZING"},
}


@dataclass(frozen=True)
class SlurmGuardDecision:
    allowed: bool
    reason: str = ""
    audit: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def allow(cls, **audit: Any) -> "SlurmGuardDecision":
        return cls(True, "", dict(audit))

    @classmethod
    def block(cls, reason: str, **audit: Any) -> "SlurmGuardDecision":
        return cls(False, reason, dict(audit))


def normalize_target_scope(raw_scope: object, *, targets: Sequence[str] | None = None) -> str:
    """Normalize the structured target-scope enum used in handoff payloads."""
    text = re.sub(r"[^a-z0-9_]+", "_", str(raw_scope or "").strip().lower()).strip("_")
    if text in EXPLICIT_SCOPES:
        return "explicit"
    if text in DISCOVERY_SCOPES:
        return "discovery"
    if text in NO_TARGET_SCOPES:
        return "none"
    return "explicit" if targets else "none"


def split_job_ids(value: Any) -> list[str]:
    return [part.strip() for part in str(value or "").split(",") if part.strip()]


def looks_like_job_id(value: str) -> bool:
    text = (value or "").strip()
    return bool(re.fullmatch(r"\d+(?:_\d+|_\[\d+(?:-\d+)?\])?", text))


def tool_accepts_job_ids(tool_name: str, schema: Mapping[str, Any]) -> bool:
    properties = set((schema.get("properties", {}) or {}).keys())
    required = set(schema.get("required", []) or [])
    return tool_name in JOB_ID_TOOLS or "job_id" in properties or "job_id" in required


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return len(value) == 0
    return False


def _content_text(content: list) -> str:
    return " ".join(getattr(item, "text", "") for item in content if hasattr(item, "text")).strip()


def _extract_job_ids_from_discovery(text: str) -> set[str]:
    return set(re.findall(r"(?<![A-Za-z0-9_])\d{2,}(?:_\d+|_\[\d+(?:-\d+)?\])?(?![A-Za-z0-9_])", text or ""))


def _parse_squeue_state(text: str, job_id: str) -> str:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    if not lines or any("no such job" in line.lower() for line in lines):
        return ""
    header = lines[0].split("|")
    try:
        job_index = header.index("JOBID")
        state_index = header.index("STATE")
    except ValueError:
        return "UNKNOWN"
    for line in lines[1:]:
        columns = line.split("|")
        if len(columns) <= max(job_index, state_index):
            continue
        if columns[job_index].strip() == job_id:
            return columns[state_index].strip().upper()
    return ""


class SlurmGuard:
    """Policy engine for structured Slurm action admission."""

    def __init__(self, dangerous_tools: Sequence[DiscoveredTool]):
        self._dangerous_by_name = {tool.name: tool for tool in dangerous_tools}

    def tool(self, tool_name: str) -> DiscoveredTool | None:
        return self._dangerous_by_name.get(tool_name)

    def admit_handoff(
        self,
        *,
        action_request: str,
        required_tool: str,
        targets: Sequence[str],
        target_scope: str,
    ) -> SlurmGuardDecision:
        if not (action_request or "").strip():
            return SlurmGuardDecision.block("No action request was provided to Operator.")
        tool_def = self.tool(required_tool)
        if not required_tool or tool_def is None:
            return SlurmGuardDecision.block("No valid dangerous action tool was resolved for this handoff.")

        schema = tool_def.schema or {}
        normalized_scope = normalize_target_scope(target_scope, targets=targets)
        if normalized_scope not in VALID_TARGET_SCOPES:
            return SlurmGuardDecision.block("Invalid target_scope in Operator handoff.")

        if tool_accepts_job_ids(required_tool, schema):
            if normalized_scope == "discovery":
                return SlurmGuardDecision.allow(target_scope=normalized_scope)
            if not targets:
                return SlurmGuardDecision.block(
                    "Job actions require concrete Slurm job IDs or target_scope='discovery'."
                )
            invalid_targets = [target for target in targets if not looks_like_job_id(target)]
            if invalid_targets:
                return SlurmGuardDecision.block(
                    "Job action targets must be concrete Slurm numeric job IDs.",
                    invalid_targets=invalid_targets,
                )

        return SlurmGuardDecision.allow(target_scope=normalized_scope)

    async def admit_dangerous_call(
        self,
        *,
        tool_name: str,
        args: Mapping[str, Any],
        context: SlurmContext | None,
        live_mcp_call: LiveMcpCall | None = None,
    ) -> SlurmGuardDecision:
        tool_def = self.tool(tool_name)
        if tool_def is None:
            return SlurmGuardDecision.block(f"{tool_name} is not in the discovered dangerous tool catalog.")

        static_decision = self._admit_static_call(tool_def, args, context)
        if not static_decision.allowed:
            return static_decision

        job_ids = self._job_ids_for_call(tool_name, args)
        if job_ids and live_mcp_call and tool_name in ACTIVE_JOB_STATE_POLICY:
            live_decision = await self._admit_live_job_state(tool_name, job_ids, live_mcp_call)
            if not live_decision.allowed:
                return live_decision

        return SlurmGuardDecision.allow(
            tool=tool_name,
            target_scope=getattr(context, "operator_target_scope", "") if context else "",
            job_ids=job_ids,
        )

    def _admit_static_call(
        self,
        tool_def: DiscoveredTool,
        args: Mapping[str, Any],
        context: SlurmContext | None,
    ) -> SlurmGuardDecision:
        tool_name = tool_def.name
        schema = tool_def.schema or {}
        required_fields = set(schema.get("required", []) or [])
        missing = [field_name for field_name in required_fields if _is_blank(args.get(field_name))]
        if missing:
            return SlurmGuardDecision.block(
                f"{tool_name}() is missing required field(s): {', '.join(sorted(missing))}.",
                missing=missing,
            )

        if context is not None:
            required_tool = str(getattr(context, "operator_required_tool", "") or "").strip()
            if not required_tool:
                return SlurmGuardDecision.block("Dangerous tool call is missing structured required_tool context.")
            if required_tool != tool_name:
                return SlurmGuardDecision.block(
                    f"Tool mismatch: handoff required {required_tool}, but Operator called {tool_name}.",
                    required_tool=required_tool,
                    called_tool=tool_name,
                )

        job_ids = self._job_ids_for_call(tool_name, args)
        invalid_job_ids = [job_id for job_id in job_ids if not looks_like_job_id(job_id)]
        if invalid_job_ids:
            return SlurmGuardDecision.block(
                "Job actions require concrete Slurm numeric job IDs.",
                invalid_job_ids=invalid_job_ids,
            )

        if job_ids and context is not None:
            scope = normalize_target_scope(
                getattr(context, "operator_target_scope", ""),
                targets=getattr(context, "operator_targets", []) or [],
            )
            approved_targets = set(getattr(context, "operator_targets", []) or [])
            if scope == "explicit":
                if not approved_targets:
                    return SlurmGuardDecision.block("Explicit action scope has no approved targets.")
                unexpected = [job_id for job_id in job_ids if job_id not in approved_targets]
                if unexpected:
                    return SlurmGuardDecision.block(
                        "Tool job IDs are outside the approved handoff target scope.",
                        unexpected_job_ids=unexpected,
                        approved_targets=sorted(approved_targets),
                    )
            elif scope == "discovery":
                discovery_calls = int(getattr(context, "operator_discovery_calls", 0) or 0)
                discovery_output = str(getattr(context, "operator_last_discovery_output", "") or "")
                if discovery_calls < 1 or not discovery_output.strip():
                    return SlurmGuardDecision.block(
                        "Broad-scope job actions require one Operator discovery read before mutation."
                    )
                discovered_job_ids = _extract_job_ids_from_discovery(discovery_output)
                missing_evidence = [job_id for job_id in job_ids if job_id not in discovered_job_ids]
                if missing_evidence:
                    return SlurmGuardDecision.block(
                        "Tool job IDs were not present in Operator discovery evidence.",
                        missing_evidence=missing_evidence,
                    )
            else:
                return SlurmGuardDecision.block("Job action scope is not executable without explicit targets or discovery.")

        return SlurmGuardDecision.allow(tool=tool_name, job_ids=job_ids)

    async def _admit_live_job_state(
        self,
        tool_name: str,
        job_ids: Sequence[str],
        live_mcp_call: LiveMcpCall,
    ) -> SlurmGuardDecision:
        allowed_states = ACTIVE_JOB_STATE_POLICY[tool_name]
        for job_id in job_ids:
            content = await live_mcp_call("squeue", {"job_id": job_id, "state": "ALL"})
            text = _content_text(content)
            state = _parse_squeue_state(text, job_id)
            if not state:
                return SlurmGuardDecision.block(
                    f"Live Slurm check could not find active job {job_id}; action not admitted.",
                    job_id=job_id,
                )
            if state not in allowed_states:
                allowed = ", ".join(sorted(allowed_states))
                return SlurmGuardDecision.block(
                    f"Live Slurm check found job {job_id} in state {state}; {tool_name} admits only: {allowed}.",
                    job_id=job_id,
                    state=state,
                )
        return SlurmGuardDecision.allow(live_checked=True, job_ids=list(job_ids))

    @staticmethod
    def _job_ids_for_call(tool_name: str, args: Mapping[str, Any]) -> list[str]:
        if "job_id" in args:
            return split_job_ids(args.get("job_id"))
        if tool_name == "scontrol_update" and str(args.get("entity", "")).strip().lower() == "job":
            return split_job_ids(args.get("id"))
        return []