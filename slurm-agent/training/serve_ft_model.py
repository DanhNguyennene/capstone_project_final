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
import json
import time
import uuid
import logging
from typing import List, Dict, Any, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Globals ───────────────────────────────────────────────────────────────────
model = None
tokenizer = None
MODEL_NAME = "slurm-agent-ft"


def load_model(base_model: str, adapter_path: str, device: str = "auto"):
    """Load base model + LoRA adapter."""
    global model, tokenizer
    logger.info(f"Loading base model: {base_model}")
    tokenizer = AutoTokenizer.from_pretrained(
        adapter_path,  # use adapter's tokenizer (has chat template)
        trust_remote_code=True,
    )
    # Use flash_attention_2 if available, otherwise fall back to sdpa
    try:
        import flash_attn  # noqa: F401
        attn_impl = "flash_attention_2"
    except ImportError:
        attn_impl = "sdpa"
        logger.info("flash-attn not installed, using sdpa attention")

    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.bfloat16,
        device_map=device,
        trust_remote_code=True,
        attn_implementation=attn_impl,
    )
    logger.info(f"Loading LoRA adapter: {adapter_path}")
    model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()
    logger.info("Model loaded and ready.")


# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(title="Slurm Agent FT Model Server")


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

    # Build prompt using chat template
    text = tokenizer.apply_chat_template(
        messages,
        tools=tools,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    input_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature if temperature > 0 else None,
            do_sample=temperature > 0,
            top_p=0.9 if temperature > 0 else None,
            pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
        )

    generated_ids = outputs[0][input_len:]
    response_text = tokenizer.decode(generated_ids, skip_special_tokens=True)

    # Parse tool calls if present
    tool_calls = None
    content = response_text
    if _has_tool_call(response_text):
        tool_calls, content = _parse_tool_calls(response_text)

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
                tool_calls.append({
                    "id": f"call_{uuid.uuid4().hex[:8]}",
                    "type": "function",
                    "function": {
                        "name": call.get("name", ""),
                        "arguments": json.dumps(call.get("arguments", {})),
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
    """Convert a completed response to SSE stream format."""
    choice = result["choices"][0]
    # Send a single chunk with the full content
    chunk = {
        "id": result["id"],
        "object": "chat.completion.chunk",
        "created": result["created"],
        "model": result["model"],
        "choices": [
            {
                "index": 0,
                "delta": choice["message"],
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
    args = parser.parse_args()

    load_model(args.base_model, args.adapter, args.device)
    uvicorn.run(app, host=args.host, port=args.port)
