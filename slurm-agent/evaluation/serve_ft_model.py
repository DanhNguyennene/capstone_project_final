#!/usr/bin/env python3
"""Serve the QLoRA fine-tuned adapter as an OpenAI-compatible API.

Uses transformers + PEFT (same stack as training — no vLLM needed).
Exposes /v1/chat/completions with tool-calling support.

Usage:
    python evaluation/serve_ft_model.py                          # default
    python evaluation/serve_ft_model.py --port 8000              # custom port
    python evaluation/serve_ft_model.py --adapter path/to/lora   # custom adapter path

Then run eval:
    LLM_PROVIDER=openai \\
    OPENAI_BASE_URL=http://localhost:8000/v1 \\
    OPENAI_API_KEY=dummy \\
    SLURM_AGENT_MODEL=slurm-agent \\
    python evaluation/scenario_eval.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path

import torch
from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from peft import PeftModel
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import uvicorn

# ── Args ──────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Serve QLoRA adapter as OpenAI API")
    p.add_argument("--base-model", default="Qwen/Qwen2.5-14B-Instruct")
    p.add_argument("--adapter", default="training/out/slurm-agent-14b-lora")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--max-new-tokens", type=int, default=1024)
    p.add_argument("--no-4bit", action="store_true", help="Load in bf16 instead of 4-bit")
    return p.parse_args()


# ── Pydantic models (OpenAI-compatible subset) ────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str | None = None
    tool_calls: list | None = None
    tool_call_id: str | None = None
    name: str | None = None


class ChatCompletionRequest(BaseModel):
    model: str = "slurm-agent"
    messages: list[dict]
    tools: list[dict] | None = None
    tool_choice: str | dict | None = None
    temperature: float = 0.1
    max_tokens: int | None = None
    stream: bool = False


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="Slurm Agent FT Model Server")

# Global state (loaded in main)
model = None
tokenizer = None
max_new_tokens_default = 1024


@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [{"id": "slurm-agent", "object": "model", "owned_by": "local"}],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/chat/completions")
def chat_completions(req: ChatCompletionRequest):
    """Handle chat completion with optional tool calling."""
    global model, tokenizer, max_new_tokens_default
    import traceback as tb

    try:
        max_tokens = req.max_tokens or max_new_tokens_default

        # Build input using Qwen's native chat template (with tools if provided)
        kwargs = dict(tokenize=False, add_generation_prompt=True)
        if req.tools:
            kwargs["tools"] = req.tools

        try:
            prompt = tokenizer.apply_chat_template(req.messages, **kwargs)
        except Exception:
            # Fallback without tools
            prompt = tokenizer.apply_chat_template(req.messages, tokenize=False, add_generation_prompt=True)

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        input_len = inputs["input_ids"].shape[1]

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=max(req.temperature, 0.01),
                do_sample=req.temperature > 0,
                pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
            )
    except Exception as e:
        print(f"ERROR in generation: {e}\n{tb.format_exc()}")
        return JSONResponse(status_code=500, content={"error": {"message": str(e)}})

    # Decode only the new tokens
    new_tokens = outputs[0][input_len:]
    response_text = tokenizer.decode(new_tokens, skip_special_tokens=True)

    # Parse tool calls from Qwen's format
    tool_calls = None
    content = response_text

    if "<tool_call>" in response_text:
        tool_calls = []
        content = None
        import re
        tc_blocks = re.findall(r"<tool_call>\s*(.*?)\s*</tool_call>", response_text, re.DOTALL)
        for i, block in enumerate(tc_blocks):
            try:
                tc_data = json.loads(block)
                tool_calls.append({
                    "id": f"call_{uuid.uuid4().hex[:8]}",
                    "type": "function",
                    "function": {
                        "name": tc_data.get("name", ""),
                        "arguments": json.dumps(tc_data.get("arguments", {})),
                    },
                })
            except json.JSONDecodeError:
                # If parsing fails, treat as regular content
                content = response_text
                tool_calls = None
                break

    # Build OpenAI-compatible response
    message = {"role": "assistant", "content": content}
    if tool_calls:
        message["tool_calls"] = tool_calls

    completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    finish_reason = "tool_calls" if tool_calls else "stop"

    # Handle streaming mode
    if req.stream:
        def generate_stream():
            # Send the full response as a single SSE chunk (fake streaming)
            chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": req.model,
                "choices": [{
                    "index": 0,
                    "delta": message,
                    "finish_reason": None,
                }],
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            # Send finish
            done_chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": req.model,
                "choices": [{
                    "index": 0,
                    "delta": {},
                    "finish_reason": finish_reason,
                }],
            }
            yield f"data: {json.dumps(done_chunk)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate_stream(), media_type="text/event-stream")

    return {
        "id": completion_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": req.model,
        "choices": [
            {
                "index": 0,
                "message": message,
                "finish_reason": finish_reason,
            }
        ],
        "usage": {
            "prompt_tokens": input_len,
            "completion_tokens": len(new_tokens),
            "total_tokens": input_len + len(new_tokens),
        },
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    global model, tokenizer, max_new_tokens_default
    args = parse_args()
    max_new_tokens_default = args.max_new_tokens

    root = Path(__file__).resolve().parents[1]
    adapter_path = root / args.adapter

    print(f"{'='*60}")
    print(f"  Slurm Agent FT Model Server")
    print(f"{'='*60}")
    print(f"  Base model:  {args.base_model}")
    print(f"  Adapter:     {adapter_path}")
    print(f"  4-bit:       {not args.no_4bit}")
    print(f"  Port:        {args.port}")
    print(f"{'='*60}\n")

    # Load tokenizer (always from base model — training didn't add tokens)
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Quantization config (same as training)
    quant_config = None
    if not args.no_4bit:
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
            bnb_4bit_use_double_quant=True,
        )

    # Load base model
    print("Loading base model...")
    load_kwargs = dict(
        trust_remote_code=True,
    )
    if quant_config:
        load_kwargs["quantization_config"] = quant_config
        # bitsandbytes handles device placement; no device_map needed
    else:
        load_kwargs["device_map"] = "auto"
        load_kwargs["torch_dtype"] = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16

    model = AutoModelForCausalLM.from_pretrained(args.base_model, **load_kwargs)

    # Load LoRA adapter
    print(f"Loading adapter from {adapter_path}...")
    model = PeftModel.from_pretrained(model, str(adapter_path))
    model.eval()

    print(f"\n✓ Model ready — serving on http://{args.host}:{args.port}")
    print(f"  Endpoint: http://{args.host}:{args.port}/v1/chat/completions\n")

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
