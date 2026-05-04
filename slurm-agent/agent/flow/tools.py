"""
FunctionTool factories for the Slurm agent.

All tools that are NOT delivered directly via MCP (dangerous-action wrappers
with HITL approval, skill lookup) are built here as FunctionTool objects.
Each factory is a plain function — easy to test, easy to replace.
"""
import json
import logging
import re
from pathlib import Path
from typing import Any, List

from mcp import ClientSession
from mcp.client.sse import sse_client

from agents.tool import FunctionTool
from agents.tool_context import ToolContext

from .context import SlurmContext
from .guardrails import (
    TOOL_INPUT_GUARDRAILS,
    guard_redact_secrets,
)
# SlurmGuard admission is disabled by request. HITL approval still gates all
# dangerous tools through FunctionTool.needs_approval=True below.
# from .slurm_guard import SlurmGuard
from .tool_discovery import DiscoveredTool

logger = logging.getLogger(__name__)


def _parse_tool_args(args_json: str | dict | None) -> dict[str, Any]:
    """Parse SDK FunctionTool arguments into a dict.

    Some models/providers occasionally pass a JSON string literal where the
    tool schema expects an object, e.g. '"QOS and Account Limits"' instead of
    '{"title":"QOS and Account Limits"}'.  Tool handlers must never assume
    json.loads(...) returned a dict.
    """
    if args_json is None or args_json == "":
        return {}
    if isinstance(args_json, dict):
        return args_json

    try:
        parsed = json.loads(args_json) if isinstance(args_json, str) else args_json
    except Exception:
        return {"value": str(args_json)}

    if isinstance(parsed, dict):
        return parsed
    if isinstance(parsed, str):
        stripped = parsed.strip()
        if not stripped:
            return {}
        # Handle double-encoded objects: '"{\\\"title\\\": ...}"'.
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                reparsed = json.loads(stripped)
                if isinstance(reparsed, dict):
                    return reparsed
            except Exception:
                pass
        return {"value": stripped}
    return {"value": parsed}


def _coerce_single_required_arg(args: dict[str, Any], required_args: set[str]) -> dict[str, Any]:
    """Map a raw scalar fallback to the sole required schema field, if unambiguous."""
    if "value" not in args or len(required_args) != 1:
        return args
    required_name = next(iter(required_args))
    if args.get(required_name):
        return args
    return {**args, required_name: args["value"]}


def _looks_like_job_id(value: str) -> bool:
    text = (value or "").strip()
    return bool(re.fullmatch(r"\d+(?:_\d+|_\[\d+(?:-\d+)?\])?", text))


def _job_id_list_is_valid(value: Any) -> bool:
    parts = [p.strip() for p in str(value or "").split(",") if p.strip()]
    return bool(parts) and all(_looks_like_job_id(p) for p in parts)


def _block_operator_action(ctx_obj: Any, reason: str) -> str:
    if ctx_obj is not None and hasattr(ctx_obj, "mark_operator_blocked"):
        ctx_obj.mark_operator_blocked(reason)
    return f"❌ Action blocked: {reason}"


async def _mcp_call(base: str, tool_name: str, arguments: dict) -> list:
    """Call an MCP tool via SSE transport. Returns content item list."""
    async with sse_client(f"{base}/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content


def _content_text(content: list) -> str:
    return " ".join(
        getattr(c, "text", "") for c in content if hasattr(c, "text")
    ).strip() or "done"


# ── Dangerous-action queuing tools (built from discovered schemas) ────────────

def make_guarded_dangerous_tools(mcp_url: str, dangerous_tools: List[DiscoveredTool]) -> List[FunctionTool]:
    """
    Build FunctionTools for every dangerous MCP tool discovered at runtime.
    Each tool actually executes via MCP, gated by the SDK's needs_approval
    mechanism (Human-in-the-Loop). The Runner will pause with interruptions
    before any dangerous tool runs; the caller must approve/reject and resume.

    Schemas come from DiscoveredTool.schema (fetched live from MCP), not hardcoded.
    """
    base = mcp_url.rstrip("/")
    result = []
    # SlurmGuard admission is disabled by request.
    # slurm_guard = SlurmGuard(dangerous_tools)

    # Safety policy: dangerous actions always require HITL approval before execution.
    # We do not bypass approval for malformed arguments.
    def _make_needs_approval(schema: dict):
        _ = schema
        return True

    for dtool in dangerous_tools:
        def _make_invoke(captured_name: str, required_args: set):
            async def _invoke(ctx: ToolContext[SlurmContext], args_json: str) -> str:
                args = _coerce_single_required_arg(_parse_tool_args(args_json), required_args)
                ctx_obj = ctx.context if hasattr(ctx, "context") else None

                blocked_reason = str(getattr(ctx_obj, "operator_blocked_reason", "") or "").strip()
                if blocked_reason:
                    return _block_operator_action(ctx_obj, blocked_reason)

                # Early validation: reject missing required args with actionable message
                missing = [k for k in required_args if not args.get(k)]
                if missing:
                    hint = ", ".join(f'{k}="value"' for k in missing)
                    extra = ""
                    if captured_name == "sbatch":
                        extra = (
                            ' Example: sbatch(script="train.sh") or '
                            'sbatch(script="/tmp/slurm_uploads/train.sh").'
                        )
                    return _block_operator_action(
                        ctx_obj,
                        f"{captured_name}() is missing required fields: {', '.join(missing)}. "
                        f"Provide: {hint}.{extra}",
                    )

                if "job_id" in args and not _job_id_list_is_valid(args.get("job_id")):
                    return _block_operator_action(
                        ctx_obj,
                        "Job actions require concrete Slurm numeric job IDs; unresolved labels or invalid IDs are not executable.",
                    )

                # SlurmGuard admission is disabled by request.
                # admission = await slurm_guard.admit_dangerous_call(
                #     tool_name=captured_name,
                #     args=args,
                #     context=ctx_obj,
                #     live_mcp_call=lambda tool, tool_args: _mcp_call(base, tool, tool_args),
                # )
                # if not admission.allowed:
                #     return _block_operator_action(ctx_obj, admission.reason)

                args_str    = ", ".join(f"{k}={v}" for k, v in args.items()) if args else ""
                description = f"{captured_name}({args_str})"
                logger.info(f"Executing approved action: {description}")
                try:
                    content = await _mcp_call(base, captured_name, args)
                    text = _content_text(content)
                    # Detect MCP-level errors returned as text
                    is_error = any(w in text.lower() for w in ("error", "failed", "invalid", "not found"))
                    if is_error:
                        return f"❌ {description}: {text}"
                    # Track that the Operator actually executed an action tool
                    if ctx_obj is not None and hasattr(ctx_obj, 'mark_operator_action'):
                        ctx_obj.mark_operator_action()
                    return f"✅ {description}: {text}"
                except Exception as exc:
                    logger.error(f"Action failed: {description}: {exc}")
                    return f"❌ {description}: {exc}"
            return _invoke

        def _make_is_enabled(captured_name: str):
            def _is_enabled(run_ctx, _agent) -> bool:
                ctx_obj = run_ctx.context if hasattr(run_ctx, "context") else None
                if bool(getattr(ctx_obj, "operator_blocked_reason", "") or ""):
                    return False
                required = str(getattr(ctx_obj, "operator_required_tool", "") or "").strip().lower()
                if not required:
                    return True
                return captured_name.lower() == required
            return _is_enabled

        tool_required = set(dtool.schema.get("required", []))
        guardrails = TOOL_INPUT_GUARDRAILS.get(dtool.name)
        result.append(FunctionTool(
            name=dtool.name,
            description=dtool.description,
            params_json_schema=dtool.schema,
            on_invoke_tool=_make_invoke(dtool.name, tool_required),
            strict_json_schema=False,  # MCP schemas aren't guaranteed strict-compatible
            is_enabled=_make_is_enabled(dtool.name),
            tool_input_guardrails=guardrails,
            tool_output_guardrails=[guard_redact_secrets],
            needs_approval=_make_needs_approval(dtool.schema),
            timeout_seconds=30.0,
            timeout_behavior="error_as_result",
        ))
        logger.info(f"Created HITL-guarded FunctionTool for {dtool.name}")

    return result


def make_operator_read_tools(mcp_url: str, read_tools: List[DiscoveredTool]) -> List[FunctionTool]:
    """
    Build Operator-side read tools with guardrails tied to handoff payload state.

    Policy:
    - If handoff carries explicit targets, discovery reads are disabled. Operator
      should execute the required action tool directly.
    - For broad actions (no explicit targets), allow at most one discovery read
      call per handoff before forcing execute/handback behavior.
    """
    base = mcp_url.rstrip("/")
    result: List[FunctionTool] = []

    for rtool in read_tools:
        if rtool.name not in {"squeue", "scontrol_show", "sinfo"}:
            continue

        def _make_invoke(captured_name: str, required_args: set):
            async def _invoke(ctx: ToolContext[SlurmContext], args_json: str) -> str:
                args = _coerce_single_required_arg(_parse_tool_args(args_json), required_args)

                missing = [k for k in required_args if not args.get(k)]
                if missing:
                    hint = ", ".join(f'{k}="value"' for k in missing)
                    return (
                        f"❌ {captured_name}() — missing required: {', '.join(missing)}. "
                        f"Provide: {hint}."
                    )

                ctx_obj = ctx.context if hasattr(ctx, "context") else None
                blocked_reason = str(getattr(ctx_obj, "operator_blocked_reason", "") or "").strip()
                if blocked_reason:
                    return blocked_reason
                required = str(getattr(ctx_obj, "operator_required_tool", "") or "").strip().lower()
                targets = list(getattr(ctx_obj, "operator_targets", []) or [])
                discovery_calls = int(getattr(ctx_obj, "operator_discovery_calls", 0) or 0)

                if required and targets:
                    return (
                        "❌ Discovery read tools are disabled for explicit targets. "
                        "Execute the required action tool now."
                    )

                if discovery_calls >= 1:
                    return (
                        "❌ Discovery read limit reached for this handoff. "
                        "Execute the required action tool or hand back with a concise result."
                    )

                try:
                    content = await _mcp_call(base, captured_name, args)
                    text = " ".join(
                        getattr(c, "text", "") for c in content if hasattr(c, "text")
                    ).strip() or "No output"
                    if ctx_obj is not None and hasattr(ctx_obj, "mark_operator_discovery"):
                        ctx_obj.mark_operator_discovery()
                    if ctx_obj is not None and hasattr(ctx_obj, "record_operator_discovery_output"):
                        ctx_obj.record_operator_discovery_output(text)
                    lowered = text.lower()
                    if "no jobs found" in lowered or "no matching jobs" in lowered:
                        if ctx_obj is not None and hasattr(ctx_obj, "mark_no_targets_found"):
                            ctx_obj.mark_no_targets_found()
                    return text
                except Exception as exc:
                    logger.error(f"Read failed: {captured_name}: {exc}")
                    return f"❌ {captured_name} failed: {exc}"
            return _invoke

        def _make_is_enabled():
            def _is_enabled(run_ctx, _agent) -> bool:
                ctx_obj = run_ctx.context if hasattr(run_ctx, "context") else None
                if ctx_obj is None:
                    return True
                if bool(getattr(ctx_obj, "operator_blocked_reason", "") or ""):
                    return False
                required = str(getattr(ctx_obj, "operator_required_tool", "") or "").strip().lower()
                targets = list(getattr(ctx_obj, "operator_targets", []) or [])
                if required and targets:
                    return False
                discovery_calls = int(getattr(ctx_obj, "operator_discovery_calls", 0) or 0)
                return discovery_calls < 1
            return _is_enabled

        read_required = set(rtool.schema.get("required", []))
        result.append(FunctionTool(
            name=rtool.name,
            description=rtool.description,
            params_json_schema=rtool.schema,
            on_invoke_tool=_make_invoke(rtool.name, read_required),
            strict_json_schema=False,
            is_enabled=_make_is_enabled(),
            timeout_seconds=20.0,
            timeout_behavior="error_as_result",
        ))
        logger.info(f"Created Operator read FunctionTool for {rtool.name}")

    return result


# ── Skill lookup tool (lazy knowledge retrieval) ──────────────────────────────

def make_skill_lookup_tool(skills: dict[str, str]) -> FunctionTool:
    """
    Create a lazy skill browser:
      - list/search returns titles only (no content)
      - read loads one selected title on demand
    This keeps runbook content out of context unless explicitly requested.
    """
    import re

    def _canonical(raw: str) -> str:
        """Canonical form for exact title matching."""
        return re.sub(r"[\s\-]+", "_", (raw or "").strip().lower())

    def _search_norm(raw: str) -> str:
        """Light normalization for title/content search."""
        txt = (raw or "").lower()
        txt = re.sub(r"[^a-z0-9_\-\s]", " ", txt)
        return re.sub(r"\s+", " ", txt).strip()

    sorted_names = sorted(skills.keys())
    canonical_to_name = {_canonical(name): name for name in sorted_names}
    search_index = [
        (name, _search_norm(name), _search_norm(skills.get(name, "")))
        for name in sorted_names
    ]

    def _render_skill(name: str) -> str:
        content = (skills.get(name) or "").strip()
        if len(content) > 7000:
            return content[:7000].rstrip() + "\n\n...[truncated for context size]..."
        return content

    def _parse_limit(raw_limit: object, default: int = 12) -> int:
        try:
            n = int(str(raw_limit))
        except Exception:
            n = default
        return max(1, min(50, n))

    def _format_titles(titles: list[str], *, total: int, label: str) -> str:
        if not titles:
            return f"{label}: no results."
        lines = [f"{label} ({len(titles)}/{total}):"]
        lines.extend(f"{i+1}. {title}" for i, title in enumerate(titles))
        lines.append('Use mode="read" with exact title to load one.')
        return "\n".join(lines)

    async def _invoke(ctx: ToolContext[SlurmContext], args_json: str) -> str:
        if not sorted_names:
            return "No local skill guides are loaded."

        args = _parse_tool_args(args_json)

        raw_value = str(args.get("value", "")).strip()
        raw_mode = str(args.get("mode", "")).strip().lower()
        query = str(args.get("query", "")).strip()
        title = str(args.get("title") or args.get("skill_name") or raw_value or "").strip()
        limit = _parse_limit(args.get("limit", 12))

        if raw_mode and raw_mode not in {"list", "search", "read"}:
            return "Invalid mode. Use one of: list, search, read."

        # Backward-compatible mode inference
        mode = raw_mode
        if not mode:
            if title:
                mode = "read"
            elif query:
                mode = "search"
            else:
                mode = "list"

        if mode == "list":
            shown = sorted_names[:limit]
            return _format_titles(shown, total=len(sorted_names), label="Skill titles")

        if mode == "search":
            if not query:
                return 'Provide query for search mode, or use mode="list".'
            qn = _search_norm(query)
            scored: list[tuple[int, str]] = []
            for name, title_norm, content_norm in search_index:
                score = 0
                if qn == title_norm:
                    score = 300
                elif qn and qn in title_norm:
                    score = 200
                elif qn and title_norm in qn:
                    score = 150
                elif qn and qn in content_norm:
                    score = 100
                if score == 0 and qn:
                    # Lightweight token-overlap fallback for queries like "failed job diagnosis"
                    q_tokens = [tok for tok in qn.split(" ") if len(tok) >= 3]
                    title_hits = sum(1 for tok in q_tokens if tok in title_norm)
                    content_hits = sum(1 for tok in q_tokens if tok in content_norm)
                    if title_hits:
                        score = 120 + title_hits
                    elif content_hits >= 2:
                        score = 80 + content_hits
                if score > 0:
                    scored.append((score, name))
            scored.sort(key=lambda x: (-x[0], x[1]))
            titles = [name for _, name in scored[:limit]]
            return _format_titles(titles, total=len(scored), label=f"Skill search: {query}")

        # mode == "read": load exactly one chosen title
        if not title:
            return 'Provide title for read mode. Tip: use mode="search" first.'

        canonical = _canonical(title)
        exact_name = canonical_to_name.get(canonical)
        if exact_name:
            return _render_skill(exact_name)

        # No exact title: return suggestions (titles only), never content.
        suggestions: list[str] = []
        for name in sorted_names:
            c = _canonical(name)
            if canonical in c or c in canonical:
                suggestions.append(name)
        suggestions = suggestions[:limit]
        if suggestions:
            return _format_titles(
                suggestions,
                total=len(suggestions),
                label=f'No exact title for "{title}". Similar titles',
            )
        return f'No skill title matches "{title}". Use mode="search" first.'

    return FunctionTool(
        name="lookup_skill",
        description=(
            "Lazy skill browser for local Slurm runbooks. "
            "mode=list/search returns titles only; mode=read loads one selected title. "
            "Search matches both titles and content, but returns titles only."
        ),
        params_json_schema={
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["list", "search", "read"],
                    "description": (
                        "Operation mode. list=show titles, search=match titles/content, "
                        "read=load one skill content."
                    ),
                },
                "query": {
                    "type": "string",
                    "description": "Search text for mode=search.",
                },
                "title": {
                    "type": "string",
                    "description": "Exact skill title for mode=read.",
                },
                "skill_name": {
                    "type": "string",
                    "description": "Legacy alias of title for backward compatibility.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "description": "Max titles to return for list/search (default: 12).",
                }
            },
            "additionalProperties": False,
        },
        on_invoke_tool=_invoke,
        timeout_seconds=5.0,
        timeout_behavior="error_as_result",
    )


# ── Slurm documentation retrieval (local RAG) ────────────────────────────────

def make_slurm_docs_lookup_tool(docs: dict[str, str]) -> FunctionTool:
    """Hybrid lexical + semantic retriever over the local Slurm documentation corpus."""
    import re

    import numpy as np

    # --- Lazy-load sentence-transformers embedding model (GPU if available) ---
    _embedder = None
    _chunk_embeddings: np.ndarray | None = None

    # Try to load pre-computed embeddings from .npz (built by build_embeddings.py)
    _precomputed_npz = Path(__file__).parent.parent / "skills" / "slurm_knowledge" / "embeddings.npz"

    def _get_embedder():
        nonlocal _embedder
        if _embedder is None:
            try:
                from sentence_transformers import SentenceTransformer

                _embedder = SentenceTransformer(
                    "sentence-transformers/all-MiniLM-L6-v2",
                    device="cuda",
                )
                logger.info("Loaded semantic embedding model (all-MiniLM-L6-v2) on CUDA")
            except Exception as e:
                logger.warning(f"Semantic embeddings unavailable, falling back to lexical: {e}")
        return _embedder

    def _get_chunk_embeddings(texts: list[str]) -> np.ndarray | None:
        nonlocal _chunk_embeddings
        if _chunk_embeddings is not None:
            return _chunk_embeddings

        # Prefer pre-computed .npz file (instant load, no GPU needed at startup)
        if _precomputed_npz.exists():
            try:
                data = np.load(_precomputed_npz, allow_pickle=False)
                _chunk_embeddings = data["embeddings"]
                # Verify dimension match (npz may be stale if corpus changed)
                if _chunk_embeddings.shape[0] == len(texts):
                    logger.info(f"Loaded pre-computed embeddings from {_precomputed_npz.name}")
                    return _chunk_embeddings
                else:
                    logger.warning(
                        f"Pre-computed embeddings stale ({_chunk_embeddings.shape[0]} vs {len(texts)} chunks). Re-embedding."
                    )
                    _chunk_embeddings = None
            except Exception as e:
                logger.warning(f"Failed to load pre-computed embeddings: {e}")

        # Fallback: compute at runtime
        embedder = _get_embedder()
        if embedder is None:
            return None
        logger.info(f"Embedding {len(texts)} doc chunks (one-time)...")
        _chunk_embeddings = embedder.encode(texts, batch_size=128, show_progress_bar=False, normalize_embeddings=True)
        logger.info("Doc chunk embeddings ready.")
        return _chunk_embeddings

    def _normalize(raw: str) -> str:
        txt = (raw or "").lower()
        txt = re.sub(r"[^a-z0-9_\-\s]", " ", txt)
        return re.sub(r"\s+", " ", txt).strip()

    def _tokens(raw: str) -> list[str]:
        return [tok for tok in _normalize(raw).split(" ") if len(tok) >= 2]

    def _title_for(content: str, fallback: str) -> str:
        frontmatter_title = re.search(r'^title:\s*"?([^"\n]+)"?', content, re.MULTILINE)
        if frontmatter_title:
            return frontmatter_title.group(1).strip()
        heading = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        return heading.group(1).strip() if heading else fallback

    def _source_for(content: str) -> str:
        source = re.search(r"^source_url:\s*(\S+)", content, re.MULTILINE)
        return source.group(1).strip() if source else "local Slurm docs corpus"

    def _clean_content(content: str) -> str:
        if content.startswith("---"):
            end = content.find("---", 3)
            if end >= 0:
                return content[end + 3 :].strip()
        return content.strip()

    def _chunks(content: str) -> list[str]:
        body = _clean_content(content)
        parts = re.split(r"\n(?=#{1,3}\s+)", body)
        chunks = []
        for part in parts:
            compact = re.sub(r"\n{3,}", "\n\n", part).strip()
            if len(compact) < 80:
                continue
            if len(compact) <= 1400:
                chunks.append(compact)
                continue
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n", compact) if p.strip()]
            buffer = ""
            for paragraph in paragraphs:
                candidate = f"{buffer}\n\n{paragraph}".strip() if buffer else paragraph
                if len(candidate) > 1400 and buffer:
                    chunks.append(buffer)
                    buffer = paragraph
                else:
                    buffer = candidate
            if buffer:
                chunks.append(buffer[:1800])
        return chunks

    def _parse_limit(raw_limit: object, default: int = 5) -> int:
        try:
            value = int(str(raw_limit))
        except Exception:
            value = default
        return max(1, min(10, value))

    pages = []
    for doc_path, content in sorted(docs.items()):
        title = _title_for(content, doc_path)
        source = _source_for(content)
        page_norm = _normalize(f"{doc_path} {title}")
        for chunk in _chunks(content):
            pages.append({
                "path": doc_path,
                "title": title,
                "source": source,
                "chunk": chunk,
                "norm": _normalize(f"{doc_path} {title} {chunk}"),
                "page_norm": page_norm,
            })

    # Pre-build text list for embedding (aligned with pages list)
    _chunk_texts = [f"{p['title']}: {p['chunk'][:512]}" for p in pages]

    async def _invoke(ctx: ToolContext[SlurmContext], args_json: str) -> str:
        if not pages:
            return "No local Slurm documentation corpus is loaded."

        args = _parse_tool_args(args_json)
        query = str(args.get("query", "")).strip()
        limit = _parse_limit(args.get("limit", 5))
        if not query:
            return "Provide a concise Slurm documentation query."

        query_norm = _normalize(query)
        query_tokens = _tokens(query)
        if not query_tokens:
            return "Query is too short to search local Slurm docs."

        # --- Lexical scoring ---
        lexical_scores: list[float] = []
        phrase = f" {query_norm} "
        for page in pages:
            score = 0.0
            norm = f" {page['norm']} "
            page_norm = f" {page['page_norm']} "
            if phrase in norm:
                score += 120
            for token in query_tokens:
                token_pattern = f" {token} "
                if token_pattern in page_norm:
                    score += 16
                if token_pattern in norm:
                    score += min(18, norm.count(token_pattern) * 3)
                if token in page["path"].lower():
                    score += 20
            lexical_scores.append(score)

        # --- Semantic scoring ---
        semantic_scores: list[float] = [0.0] * len(pages)
        chunk_embs = _get_chunk_embeddings(_chunk_texts)
        if chunk_embs is not None:
            embedder = _get_embedder()
            if embedder is not None:
                query_emb = embedder.encode([query], normalize_embeddings=True)
                cosine_sims = (chunk_embs @ query_emb.T).flatten()
                # Scale cosine similarity (0-1) to match lexical range (~0-200)
                semantic_scores = (cosine_sims * 200).tolist()

        # --- Reciprocal Rank Fusion ---
        k = 60  # RRF constant
        # Rank by lexical
        lexical_ranked = sorted(range(len(pages)), key=lambda i: -lexical_scores[i])
        # Rank by semantic
        semantic_ranked = sorted(range(len(pages)), key=lambda i: -semantic_scores[i])

        rrf_scores: list[float] = [0.0] * len(pages)
        for rank, idx in enumerate(lexical_ranked):
            if lexical_scores[idx] > 0:
                rrf_scores[idx] += 1.0 / (k + rank + 1)
        for rank, idx in enumerate(semantic_ranked):
            if semantic_scores[idx] > 20:  # Only count if similarity > 0.1
                rrf_scores[idx] += 1.0 / (k + rank + 1)

        # Filter to pages with any signal
        scored = [(rrf_scores[i], i) for i in range(len(pages)) if rrf_scores[i] > 0]
        scored.sort(key=lambda item: (-item[0], pages[item[1]]["path"]))

        if not scored:
            return f'No local Slurm documentation snippets matched "{query}". Try web_search with site:slurm.schedmd.com.'

        seen = set()
        results = []
        for rrf_score, idx in scored:
            page = pages[idx]
            key = (page["path"], page["chunk"][:100])
            if key in seen:
                continue
            seen.add(key)
            snippet = page["chunk"].strip()
            if len(snippet) > 950:
                snippet = snippet[:950].rstrip() + "..."
            results.append((rrf_score, page, snippet))
            if len(results) >= limit:
                break

        lines = [
            f'Local Slurm docs results for "{query}" ({len(results)}/{len(scored)} snippets, hybrid retrieval).',
            "Use these snippets as documentation context; verify live cluster state with Slurm tools.",
        ]
        for index, (rrf_score, page, snippet) in enumerate(results, 1):
            lines.append(
                f"\n[{index}] {page['title']}\n"
                f"Source: {page['source']}\n"
                f"Path: {page['path']}\n"
                f"Snippet:\n{snippet}"
            )
        return "\n".join(lines)

    return FunctionTool(
        name="lookup_slurm_docs",
        description=(
            "Retrieve ranked snippets from the local official Slurm documentation corpus. "
            "Use for Slurm command syntax, reason codes, states, accounting/QOS, resources, and admin reference questions. "
            "Do not use for live cluster state; call Slurm tools for that."
        ),
        params_json_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Concise Slurm documentation query, e.g. 'sbatch dependency afterok'.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Maximum snippets to return (default: 5).",
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        on_invoke_tool=_invoke,
        timeout_seconds=5.0,
        timeout_behavior="error_as_result",
    )
