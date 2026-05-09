#!/usr/bin/env python3
"""
Serve the fine-tuned Qwen2.5-14B LoRA model via OpenAI-compatible API.

This loads the base model + LoRA adapter using transformers + PEFT
and exposes a /v1/chat/completions endpoint compatible with the agent backend.

Usage:
    python serve_ft_model.py --port 8081
    # Then set: OPENAI_BASE_URL=http://localhost:8081/v1
    #           SLURM_AGENT_MODEL=slurm-agent-ft
    #           LLM_PROVIDER=openai
    #           OPENAI_API_KEY=dummy
"""

import argparse
import asyncio
import json
import os
import time
import uuid
import logging
from typing import List, Dict, Any, Optional

# Reduce fragmentation BEFORE importing torch
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Training tool schema override ─────────────────────────────────────────────
# When set, replace incoming (full MCP) tool schemas with simplified training versions.
USE_TRAINING_TOOLS = os.environ.get("USE_TRAINING_TOOLS", "").strip().lower() in ("1", "true", "yes")

# Simplified schemas matching what the model was trained on
TRAINING_TOOL_SCHEMAS = {
    "squeue": {"type": "function", "function": {"name": "squeue", "description": "Show the Slurm job queue. Filter by user, partition, state, or job ID.", "parameters": {"type": "object", "properties": {"user": {"type": "string", "description": "Filter by username"}, "partition": {"type": "string", "description": "Filter by partition"}, "state": {"type": "string", "description": "Filter by job state (RUNNING, PENDING, FAILED, etc.)"}, "job_id": {"type": "string", "description": "Specific job ID to query"}}}}},
    "sinfo": {"type": "function", "function": {"name": "sinfo", "description": "Show cluster node and partition status.", "parameters": {"type": "object", "properties": {"partition": {"type": "string", "description": "Filter by partition"}}}}},
    "sacct": {"type": "function", "function": {"name": "sacct", "description": "Show accounting data for completed/historical jobs.", "parameters": {"type": "object", "properties": {"job_id": {"type": "string", "description": "Job ID to query"}, "user": {"type": "string", "description": "Filter by user"}, "starttime": {"type": "string", "description": "Start time filter"}}}}},
    "scontrol_show": {"type": "function", "function": {"name": "scontrol_show", "description": "Show detailed job or node configuration.", "parameters": {"type": "object", "properties": {"entity": {"type": "string", "description": "job or node"}, "id": {"type": "string", "description": "Job ID or node name"}}}}},
    "sbatch": {"type": "function", "function": {"name": "sbatch", "description": "Submit a batch job script to Slurm.", "parameters": {"type": "object", "properties": {"script": {"type": "string", "description": "Script path or content"}, "options": {"type": "string", "description": "Additional sbatch options"}}, "required": ["script"]}}},
    "scancel": {"type": "function", "function": {"name": "scancel", "description": "Cancel one or more Slurm jobs.", "parameters": {"type": "object", "properties": {"job_id": {"type": "string", "description": "Job ID(s) to cancel"}, "user": {"type": "string", "description": "Cancel all jobs for user"}, "partition": {"type": "string", "description": "Cancel all jobs in partition"}, "state": {"type": "string", "description": "Cancel jobs in state"}}}}},
    "scontrol_hold": {"type": "function", "function": {"name": "scontrol_hold", "description": "Hold a pending job to prevent scheduling.", "parameters": {"type": "object", "properties": {"job_id": {"type": "string", "description": "Job ID to hold"}}, "required": ["job_id"]}}},
    "scontrol_release": {"type": "function", "function": {"name": "scontrol_release", "description": "Release a held job to allow scheduling.", "parameters": {"type": "object", "properties": {"job_id": {"type": "string", "description": "Job ID to release"}}, "required": ["job_id"]}}},
    "scontrol_requeue": {"type": "function", "function": {"name": "scontrol_requeue", "description": "Requeue a failed or completed job.", "parameters": {"type": "object", "properties": {"job_id": {"type": "string", "description": "Job ID to requeue"}}, "required": ["job_id"]}}},
    "scontrol_update": {"type": "function", "function": {"name": "scontrol_update", "description": "Update job properties (timelimit, partition, etc.).", "parameters": {"type": "object", "properties": {"job_id": {"type": "string", "description": "Job ID to update"}, "updates": {"type": "string", "description": "Key=Value pairs to update"}}, "required": ["job_id"]}}},
    "scontrol_node": {"type": "function", "function": {"name": "scontrol_node", "description": "Change node state (drain, resume, down).", "parameters": {"type": "object", "properties": {"node": {"type": "string", "description": "Node name"}, "state": {"type": "string", "description": "Target state (drain, resume, down)"}, "reason": {"type": "string", "description": "Reason for state change"}}, "required": ["node", "state"]}}},
    "sacctmgr_list": {"type": "function", "function": {"name": "sacctmgr_list", "description": "List accounting entities (accounts, users, associations, QOS).", "parameters": {"type": "object", "properties": {"entity": {"type": "string", "description": "What to list: account, user, association, qos"}}}}},
    "sacctmgr_show": {"type": "function", "function": {"name": "sacctmgr_show", "description": "Show accounting entities (accounts, users, associations, QOS). Alias for sacctmgr_list.", "parameters": {"type": "object", "properties": {"entity": {"type": "string", "description": "What to show: account, user, association, qos"}}}}},
    "lookup_slurm_docs": {"type": "function", "function": {"name": "lookup_slurm_docs", "description": "Look up Slurm documentation for a command or concept.", "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "Documentation topic to look up"}}, "required": ["query"]}}},
    "sdiag": {"type": "function", "function": {"name": "sdiag", "description": "Show scheduler diagnostics and statistics.", "parameters": {"type": "object", "properties": {}}}},
    "sprio": {"type": "function", "function": {"name": "sprio", "description": "Show job priority factors.", "parameters": {"type": "object", "properties": {"job_id": {"type": "string", "description": "Job ID"}}}}},
    "sstat": {"type": "function", "function": {"name": "sstat", "description": "Show status of running job steps (memory, CPU usage).", "parameters": {"type": "object", "properties": {"job_id": {"type": "string", "description": "Job ID"}}, "required": ["job_id"]}}},
    "sshare": {"type": "function", "function": {"name": "sshare", "description": "Show fairshare and usage information.", "parameters": {"type": "object", "properties": {"user": {"type": "string", "description": "Filter by user"}}}}},
    "sreport": {"type": "function", "function": {"name": "sreport", "description": "Generate accounting usage reports.", "parameters": {"type": "object", "properties": {"report_type": {"type": "string", "description": "Report type (cluster, user, job)"}}}}},
    "scontrol_license": {"type": "function", "function": {"name": "scontrol_license", "description": "Show license information and allocations.", "parameters": {"type": "object", "properties": {}}}},
    "scontrol_reservation_show": {"type": "function", "function": {"name": "scontrol_reservation_show", "description": "Show reservation details.", "parameters": {"type": "object", "properties": {}}}},
    "scontrol_show_config": {"type": "function", "function": {"name": "scontrol_show_config", "description": "Show Slurm configuration parameters.", "parameters": {"type": "object", "properties": {}}}},
    "scontrol_ping": {"type": "function", "function": {"name": "scontrol_ping", "description": "Ping Slurm controllers to check health.", "parameters": {"type": "object", "properties": {}}}},
    "sinfo_reasons": {"type": "function", "function": {"name": "sinfo_reasons", "description": "Show reasons for node states (down, drain, etc.).", "parameters": {"type": "object", "properties": {}}}},
    "sinfo_node": {"type": "function", "function": {"name": "sinfo_node", "description": "Show detailed per-node information.", "parameters": {"type": "object", "properties": {"node": {"type": "string", "description": "Node name"}}}}},
    "squeue_steps": {"type": "function", "function": {"name": "squeue_steps", "description": "Show job steps in the queue.", "parameters": {"type": "object", "properties": {"job_id": {"type": "string", "description": "Job ID"}}}}},
    "scontrol_show_step": {"type": "function", "function": {"name": "scontrol_show_step", "description": "Show detailed step information for a job.", "parameters": {"type": "object", "properties": {"job_id": {"type": "string", "description": "Job ID"}}, "required": ["job_id"]}}},
    "sprio_weights": {"type": "function", "function": {"name": "sprio_weights", "description": "Show priority weight configuration.", "parameters": {"type": "object", "properties": {}}}},
    "web_search": {"type": "function", "function": {"name": "web_search", "description": "Search the web for Slurm-related information.", "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "Search query"}}, "required": ["query"]}}},
    "fetch_web_content": {"type": "function", "function": {"name": "fetch_web_content", "description": "Fetch content from a web URL.", "parameters": {"type": "object", "properties": {"url": {"type": "string", "description": "URL to fetch"}}, "required": ["url"]}}},
    "read_file": {"type": "function", "function": {"name": "read_file", "description": "Read content of a file.", "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "File path"}}, "required": ["path"]}}},
    "transfer_to_operator": {"type": "function", "function": {"name": "transfer_to_operator", "description": "Hand off to the Operator agent for state-changing actions that require approval.", "parameters": {"type": "object", "properties": {"action_request": {"type": "string", "description": "What action to perform"}, "required_tool": {"type": "string", "description": "The tool the operator should use"}, "targets": {"type": "string", "description": "Comma-separated target IDs"}, "target_scope": {"type": "string", "description": "explicit|discovery|none"}}, "required": ["action_request", "required_tool"]}}},
    "transfer_to_observer": {"type": "function", "function": {"name": "transfer_to_observer", "description": "Hand back to the Observer agent after Operator action(s) complete.", "parameters": {"type": "object", "properties": {"summary": {"type": "string", "description": "Brief summary of the actions performed"}}}}},
}


def _remap_tools(tools: list) -> list:
    """Replace incoming tool schemas with training versions where available."""
    remapped = []
    for t in tools:
        name = (t.get("function") or {}).get("name", "")
        if name in TRAINING_TOOL_SCHEMAS:
            remapped.append(TRAINING_TOOL_SCHEMAS[name])
        else:
            # Keep unknown tools as-is (e.g., handoff tools injected by SDK)
            remapped.append(t)
    if remapped:
        logger.info(f"[REMAP] {len(remapped)} tools remapped to training schemas")
    return remapped

# ── Globals ───────────────────────────────────────────────────────────────────
model = None
tokenizer = None
MODEL_NAME = "slurm-agent-ft"


def load_model(base_model: str, adapter_path: str, device: str = "auto", quantized: bool = False):
    """Load base model + LoRA adapter."""
    global model, tokenizer
    logger.info(f"Loading base model: {base_model} ({'4-bit quantized' if quantized else 'full precision'})")
    tokenizer = AutoTokenizer.from_pretrained(
        adapter_path,  # use adapter's tokenizer (has chat template)
        trust_remote_code=True,
    )
    # Attention implementation:
    #   - flash_attention_2: Ampere+ only, doesn't work on V100 (CC 7.0)
    #   - sdpa: fused kernels reject GQA (Qwen2.5: 40 Q heads vs 8 KV heads)
    #   - eager: pure-PyTorch, handles GQA correctly via repeat_kv. Slower but reliable.
    # Default to eager for safety on V100; allow override via env ATTN_IMPL.
    attn_impl = os.environ.get("ATTN_IMPL", "").strip()
    if not attn_impl:
        try:
            import flash_attn  # noqa: F401
            attn_impl = "flash_attention_2"
        except ImportError:
            attn_impl = "eager"
            logger.info("flash-attn not installed, using eager attention (GQA-safe)")
    else:
        logger.info(f"ATTN_IMPL override: {attn_impl}")

    load_kwargs = dict(
        torch_dtype=torch.bfloat16,
        device_map=device,
        trust_remote_code=True,
        attn_implementation=attn_impl,
    )
    if quantized:
        try:
            import bitsandbytes  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "bitsandbytes is NOT installed! Cannot run in quantized mode. "
                "Install with: pip install bitsandbytes>=0.43.0"
            )
        from transformers import BitsAndBytesConfig
        load_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )

    model = AutoModelForCausalLM.from_pretrained(base_model, **load_kwargs)

    # Verify quantization actually applied
    if quantized:
        param = next(model.parameters())
        mem_gb = torch.cuda.memory_allocated() / 1e9
        logger.info(f"GPU memory after loading: {mem_gb:.1f} GB")
        if mem_gb > 15.0:
            raise RuntimeError(
                f"Quantization FAILED — model using {mem_gb:.1f} GB (expected <12 GB for 4-bit 14B). "
                f"Check bitsandbytes CUDA compatibility."
            )
        logger.info(f"4-bit quantization verified: {mem_gb:.1f} GB on GPU")

    logger.info(f"Loading LoRA adapter: {adapter_path}")
    model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()

    # Configure SDPA backends (only used if attn_impl=='sdpa').
    # Mem-efficient + math both enabled; math is the GQA fallback. Flash off (V100).
    try:
        torch.backends.cuda.enable_flash_sdp(False)
        torch.backends.cuda.enable_mem_efficient_sdp(True)
        torch.backends.cuda.enable_math_sdp(True)
        logger.info("SDPA: mem_efficient=on, math=on, flash=off")
    except Exception as e:
        logger.warning(f"Could not configure SDPA backends: {e}")

    # Final memory check
    mem_gb = torch.cuda.memory_allocated() / 1e9
    logger.info(f"Model loaded and ready. Total GPU memory: {mem_gb:.1f} GB")


# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(title="Slurm Agent FT Model Server")

# Serialize GPU inference — model.generate() is NOT thread-safe.
# Without this, concurrent requests trigger CUDA device-side asserts.
_GENERATE_LOCK = asyncio.Lock()


@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [{"id": MODEL_NAME, "object": "model", "owned_by": "local"}],
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    tools = body.get("tools", None)
    temperature = body.get("temperature", 0.7)
    max_tokens = body.get("max_tokens", 2048)
    stream = body.get("stream", False)

    # If USE_TRAINING_TOOLS is set, replace incoming tool schemas with the
    # simplified versions used during training (prevents schema mismatch).
    if USE_TRAINING_TOOLS and tools:
        tools = _remap_tools(tools)

    # Build prompt using chat template
    text = tokenizer.apply_chat_template(
        messages,
        tools=tools,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    input_len = inputs["input_ids"].shape[1]
    logger.info(f"Prompt tokens: {input_len}")

    # Serialize inference to prevent CUDA device-side asserts from concurrent generate() calls
    async with _GENERATE_LOCK:
        torch.cuda.empty_cache()

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature if temperature > 0 else None,
                do_sample=temperature > 0,
                top_p=0.9 if temperature > 0 else None,
                pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
                use_cache=True,
            )

    generated_ids = outputs[0][input_len:]
    response_text = tokenizer.decode(generated_ids, skip_special_tokens=True)

    # Parse tool calls if present
    tool_calls = None
    content = response_text
    if _has_tool_call(response_text):
        tool_calls, content = _parse_tool_calls(response_text)

    # Filter hallucinated tool calls: drop any tool not in the request's tools list.
    # This protects against the FT model calling tools from a sibling agent (Observer
    # calling Operator-only tools etc.). If everything gets filtered, fall back to text.
    if tool_calls and tools:
        allowed = {
            (t.get("function") or {}).get("name")
            for t in tools
            if isinstance(t, dict)
        }
        allowed.discard(None)
        kept, dropped = [], []
        for tc in tool_calls:
            name = tc.get("function", {}).get("name")
            if name in allowed:
                kept.append(tc)
            else:
                dropped.append(name)
        if dropped:
            logger.warning(
                f"Dropped {len(dropped)} hallucinated tool_call(s): {dropped}. "
                f"Allowed: {sorted(allowed)[:8]}..."
            )
        if kept:
            tool_calls = kept
        else:
            # All tool calls were invalid. Convert to a text response so the agent
            # can re-prompt instead of crashing on ModelBehaviorError.
            tool_calls = None
            content = (
                response_text
                or "I attempted to call a tool that is not available in my current role."
            )

    completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    result = {
        "id": completion_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": MODEL_NAME,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content if not tool_calls else None,
                    "tool_calls": tool_calls,
                },
                "finish_reason": "tool_calls" if tool_calls else "stop",
            }
        ],
        "usage": {
            "prompt_tokens": input_len,
            "completion_tokens": len(generated_ids),
            "total_tokens": input_len + len(generated_ids),
        },
    }

    if stream:
        return StreamingResponse(
            _stream_response(result),
            media_type="text/event-stream",
        )
    return JSONResponse(result)


def _has_tool_call(text: str) -> bool:
    """Check if response contains a tool call (Qwen format)."""
    return "✿FUNCTION✿" in text or "<tool_call>" in text or '"name"' in text and '"arguments"' in text


def _parse_tool_calls(text: str) -> tuple:
    """Parse tool calls from model output. Returns (tool_calls_list, remaining_content)."""
    tool_calls = []
    content = ""

    # Try Qwen3/Qwen2.5 tool_call format: <tool_call>\n{"name": ..., "arguments": ...}\n</tool_call>
    import re
    pattern = r'<tool_call>\s*(\{.*?\})\s*</tool_call>'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        for i, match in enumerate(matches):
            try:
                call = json.loads(match)
                # arguments may be a dict OR a JSON-encoded string. Normalize to JSON string.
                raw_args = call.get("arguments", {})
                if isinstance(raw_args, str):
                    # Validate it's parseable JSON; if not, wrap as empty
                    try:
                        json.loads(raw_args)
                        args_str = raw_args
                    except json.JSONDecodeError:
                        args_str = "{}"
                else:
                    args_str = json.dumps(raw_args)
                tool_calls.append({
                    "id": f"call_{uuid.uuid4().hex[:8]}",
                    "type": "function",
                    "function": {
                        "name": call.get("name", ""),
                        "arguments": args_str,
                    },
                })
            except json.JSONDecodeError:
                continue
        # Content is everything outside tool_call tags
        content = re.sub(pattern, "", text, flags=re.DOTALL).strip()
        return tool_calls if tool_calls else None, content or None

    # Fallback: Qwen ✿FUNCTION✿ format
    if "✿FUNCTION✿" in text:
        parts = text.split("✿FUNCTION✿")
        content = parts[0].strip() or None
        for part in parts[1:]:
            lines = part.strip().split("\n", 1)
            if lines:
                name = lines[0].strip().rstrip("✿").strip()
                args_str = lines[1].strip() if len(lines) > 1 else "{}"
                try:
                    args = json.loads(args_str)
                except json.JSONDecodeError:
                    args = {}
                tool_calls.append({
                    "id": f"call_{uuid.uuid4().hex[:8]}",
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": json.dumps(args),
                    },
                })
        return tool_calls if tool_calls else None, content

    return None, text


async def _stream_response(result: dict):
    """Convert a completed response to SSE stream format.

    OpenAI streaming spec: each tool_call delta MUST carry an `index` field so
    the client can distinguish multiple parallel tool_calls. Without it, the
    OpenAI Python client concatenates the `arguments` strings of consecutive
    function deltas into one corrupt blob.
    """
    choice = result["choices"][0]
    msg = choice["message"]
    tool_calls = msg.get("tool_calls")

    # Build delta WITHOUT mutating the original message
    delta: Dict[str, Any] = {"role": "assistant"}
    if msg.get("content") is not None:
        delta["content"] = msg["content"]
    if tool_calls:
        delta["tool_calls"] = [
            {
                "index": i,
                "id": tc["id"],
                "type": tc.get("type", "function"),
                "function": {
                    "name": tc["function"]["name"],
                    "arguments": tc["function"]["arguments"],
                },
            }
            for i, tc in enumerate(tool_calls)
        ]

    chunk = {
        "id": result["id"],
        "object": "chat.completion.chunk",
        "created": result["created"],
        "model": result["model"],
        "choices": [
            {
                "index": 0,
                "delta": delta,
                "finish_reason": None,
            }
        ],
    }
    yield f"data: {json.dumps(chunk)}\n\n"

    # Send finish
    finish_chunk = {
        "id": result["id"],
        "object": "chat.completion.chunk",
        "created": result["created"],
        "model": result["model"],
        "choices": [{"index": 0, "delta": {}, "finish_reason": choice["finish_reason"]}],
    }
    yield f"data: {json.dumps(finish_chunk)}\n\n"
    yield "data: [DONE]\n\n"


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serve fine-tuned model")
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-14B-Instruct")
    parser.add_argument("--adapter", default="training/out/slurm-agent-14b-lora")
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--quantized", action="store_true", help="Load in 4-bit NF4 quantization")
    args = parser.parse_args()

    load_model(args.base_model, args.adapter, args.device, quantized=args.quantized)
    uvicorn.run(app, host=args.host, port=args.port)
