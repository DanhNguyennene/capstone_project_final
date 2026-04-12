"""
Tool guardrails for the Slurm agent.

Applied at the FunctionTool boundary — before / after dangerous tool invocations.
"""
import json
import logging
import re
from typing import Dict, List

from agents.tool_guardrails import (
    ToolGuardrailFunctionOutput,
    ToolInputGuardrail,
    ToolInputGuardrailData,
    ToolOutputGuardrail,
    ToolOutputGuardrailData,
    tool_input_guardrail,
    tool_output_guardrail,
)

logger = logging.getLogger(__name__)


def _safe_parse_args(raw: str) -> dict:
    """Parse tool arguments JSON robustly, handling LLM quirks."""
    raw = (raw or "").strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # LLM sometimes appends extra text after the JSON object.
        # Try to extract the first valid JSON object.
        match = re.search(r'\{[^{}]*\}', raw)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {}


# ── Sbatch danger-pattern list ────────────────────────────────────────────────
_SBATCH_DANGER_PATTERNS = [
    "rm -rf /", ":(){ :|:& };:", "mkfs", "dd if=/dev/",
    "> /dev/sda", "chmod -R 777 /", "wget.*| sh", "curl.*| bash",
]


# ── Guardrail implementations ─────────────────────────────────────────────────

@tool_input_guardrail(name="validate_job_id")
def guard_job_id(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """Reject missing or non-numeric job_id before any job-control tool fires."""
    args = _safe_parse_args(data.context.tool_arguments)
    job_id = str(args.get("job_id", "")).strip().strip("'\"")
    if not job_id:
        # Try to find a job_id in other common param names
        for key in ("id", "jobid", "job"):
            val = str(args.get(key, "")).strip().strip("'\"")
            if val:
                job_id = val
                break
    if not job_id:
        return ToolGuardrailFunctionOutput.reject_content(
            "job_id is required. Run squeue to find the numeric job ID first."
        )
    # Slurm job IDs. Single: 12345, 12345_1, 12345_[1-5], 12345.batch
    # Comma-separated batch: "12345,12346,12347"
    # Each element must be a valid Slurm ID
    _SINGLE_JOB_RE = r'\d+(_(\d+|\[[\d\-,%]+\]))?(\.\w+)?'
    if not re.match(rf'^{_SINGLE_JOB_RE}(,{_SINGLE_JOB_RE})*$', job_id):
        return ToolGuardrailFunctionOutput.reject_content(
            "Invalid job_id '{}': must be a Slurm job ID (e.g. 12345, 12345_1, 12345_[1-5]) "
            "or comma-separated IDs (e.g. 12345,12346).".format(job_id)
        )
    return ToolGuardrailFunctionOutput.allow(output_info={"job_id": job_id})


@tool_input_guardrail(name="validate_sbatch_script")
def guard_sbatch(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """Reject sbatch with missing script or dangerous patterns."""
    args = _safe_parse_args(data.context.tool_arguments)
    script = (args.get("script") or "").strip()
    if not script:
        return ToolGuardrailFunctionOutput.reject_content(
            "sbatch requires a 'script' argument with the file path. "
            "Example: sbatch(script=\"/tmp/slurm_uploads/job.sh\")"
        )
    content = (script + " " + args.get("flags", "")).lower()
    for pattern in _SBATCH_DANGER_PATTERNS:
        if pattern.lower() in content:
            return ToolGuardrailFunctionOutput.reject_content(
                f"Blocked: script contains dangerous pattern '{pattern}'."
            )
    return ToolGuardrailFunctionOutput.allow()


@tool_input_guardrail(name="require_pending_actions")
def guard_pending_exists(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    """Fast-reject confirm_action when nothing is queued."""
    slurm_ctx = data.context.context
    if slurm_ctx is None:
        return ToolGuardrailFunctionOutput.allow()
    pending = slurm_ctx.get_pending_actions()
    if not pending:
        return ToolGuardrailFunctionOutput.reject_content(
            "No pending actions to confirm. Ask the user what they want to do first."
        )
    return ToolGuardrailFunctionOutput.allow(output_info={"pending_count": len(pending)})


@tool_output_guardrail(name="redact_secrets")
def guard_redact_secrets(data: ToolOutputGuardrailData) -> ToolGuardrailFunctionOutput:
    """Strip API keys, bearer tokens, and plaintext passwords from tool output."""
    text = str(data.output or "")
    redacted = re.sub(
        r"(sk-[A-Za-z0-9]{20,}"
        r"|Bearer\s+[A-Za-z0-9\-._~+/]{20,}"
        r"|password\s*[=:]\s*\S+"
        r"|token\s*[=:]\s*[A-Za-z0-9\-._]{16,})",
        "[REDACTED]",
        text,
        flags=re.IGNORECASE,
    )
    if redacted != text:
        logger.warning(f"Redacted sensitive data in output of '{data.context.tool_name}'")
        return ToolGuardrailFunctionOutput.reject_content(redacted)
    return ToolGuardrailFunctionOutput.allow()


# ── Per-tool input guardrail map (used by tool_discovery) ────────────────────

TOOL_INPUT_GUARDRAILS: Dict[str, List[ToolInputGuardrail]] = {
    "scancel":           [guard_job_id],
    "scontrol_hold":     [guard_job_id],
    "scontrol_release":  [guard_job_id],
    "scontrol_requeue":  [guard_job_id],
    "sbatch":            [guard_sbatch],
}

CONFIRM_OUTPUT_GUARDRAILS: List[ToolOutputGuardrail] = [guard_redact_secrets]
