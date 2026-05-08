"""Tolerance patch for FT models that emit handoff arguments as JSON-encoded strings.

Some fine-tuned chat models serialize tool-call `arguments` like:
    "{\"action_request\": \"...\", \"targets\": [\"2001\"]}"
instead of a proper JSON object. The OpenAI Agents SDK calls
`type_adapter.validate_json(args, ...)`; pydantic then sees a *string* and rejects
with `Input should be an object`.

This patch wraps `agents.util._json.validate_json` so that on
`ModelBehaviorError`/`ValidationError`, we try a single round of `json.loads`
and re-validate the resulting object. Idempotent: only installs once.

Importing this module installs the patch as a side effect.
"""
from __future__ import annotations

import json as _json
import logging as _logging

_log = _logging.getLogger(__name__)

_INSTALLED_FLAG = "_slurm_agent_handoff_compat_installed"


def install() -> None:
    try:
        from agents.util import _json as _agents_json
    except Exception as exc:  # pragma: no cover
        _log.warning("agents.util._json not importable; handoff compat skipped: %s", exc)
        return

    if getattr(_agents_json, _INSTALLED_FLAG, False):
        return

    try:
        from agents.exceptions import ModelBehaviorError
    except Exception:  # pragma: no cover
        ModelBehaviorError = Exception  # type: ignore[assignment]

    try:
        from pydantic import ValidationError as _PydValidationError
    except Exception:  # pragma: no cover
        _PydValidationError = Exception  # type: ignore[assignment]

    _orig = _agents_json.validate_json

    def _coerce_payload(d):
        """Best-effort coercion for FT-model handoff payloads.

        Fixes common deviations like targets="" (string) → targets=[],
        targets="2001" → targets=["2001"], required_tool=null → "".
        """
        if not isinstance(d, dict):
            return d
        out = dict(d)
        if "targets" in out:
            t = out["targets"]
            if t in (None, "", "null", "none"):
                out["targets"] = []
            elif isinstance(t, str):
                # Comma-separated single string → list
                parts = [p.strip() for p in t.split(",") if p.strip()]
                out["targets"] = parts if parts else []
            elif not isinstance(t, list):
                out["targets"] = [str(t)]
        for k in ("action_request", "required_tool", "target_scope"):
            if k in out and out[k] is None:
                out[k] = ""
        return out

    def _retry(new_json_str, args, kwargs):
        if args:
            return _orig(new_json_str, *args[1:], **kwargs)
        kwargs2 = dict(kwargs)
        kwargs2["json_str"] = new_json_str
        return _orig(**kwargs2)

    def _tolerant_validate_json(*args, **kwargs):
        try:
            return _orig(*args, **kwargs)
        except (ModelBehaviorError, _PydValidationError):
            json_str = args[0] if args else kwargs.get("json_str")
            if not isinstance(json_str, (str, bytes, bytearray)):
                raise
            # Step 1: try parsing the JSON directly (the original payload may
            # already be a valid JSON object that just has wrong field types).
            try:
                parsed = _json.loads(json_str)
            except Exception:
                raise
            # Step 2: unwrap doubly-encoded JSON-string-of-a-JSON-string.
            if isinstance(parsed, str):
                _log.debug("handoff_compat: doubly-encoded JSON args, unwrapping")
                try:
                    parsed = _json.loads(parsed)
                except Exception:
                    raise
            # Step 3: coerce common type deviations and retry.
            if isinstance(parsed, dict):
                coerced = _coerce_payload(parsed)
                _log.debug("handoff_compat: coerced payload, retrying")
                return _retry(_json.dumps(coerced), args, kwargs)
            raise

    _agents_json.validate_json = _tolerant_validate_json
    setattr(_agents_json, _INSTALLED_FLAG, True)
    _log.info("handoff_compat: tolerant validate_json installed")


install()
