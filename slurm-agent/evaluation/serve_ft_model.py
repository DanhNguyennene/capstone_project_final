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
import os
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

# ── Training tool schema override ─────────────────────────────────────────────
USE_TRAINING_TOOLS = os.environ.get("USE_TRAINING_TOOLS", "").strip().lower() in ("1", "true", "yes")

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
    "sprio_weights": {"type": "function", "function": {"name": "sprio_weights", "description": "Show priority weight configuration.", "parameters": {"type": "object", "properties": {}}}},
    "transfer_to_operator": {"type": "function", "function": {"name": "transfer_to_operator", "description": "Hand off to the Operator agent for state-changing actions that require approval.", "parameters": {"type": "object", "properties": {"action_request": {"type": "string", "description": "What action to perform"}, "required_tool": {"type": "string", "description": "The tool the operator should use"}, "targets": {"type": "string", "description": "Comma-separated target IDs"}, "target_scope": {"type": "string", "description": "explicit|discovery|none"}}, "required": ["action_request", "required_tool"]}}},
    "transfer_to_observer": {"type": "function", "function": {"name": "transfer_to_observer", "description": "Hand back to the Observer agent after Operator action(s) complete.", "parameters": {"type": "object", "properties": {"summary": {"type": "string", "description": "Brief summary of the actions performed"}}}}},
}


def _remap_tools(tools):
    """Replace incoming tool schemas with training versions where available."""
    remapped = []
    for t in tools:
        name = (t.get("function") or {}).get("name", "")
        if name in TRAINING_TOOL_SCHEMAS:
            remapped.append(TRAINING_TOOL_SCHEMAS[name])
        else:
            remapped.append(t)
    return remapped

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
            tools = req.tools
            if USE_TRAINING_TOOLS:
                tools = _remap_tools(tools)
            kwargs["tools"] = tools

        try:
            prompt = tokenizer.apply_chat_template(req.messages, **kwargs)
        except Exception:
            # Fallback without tools
            prompt = tokenizer.apply_chat_template(req.messages, tokenize=False, add_generation_prompt=True)

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        input_len = inputs["input_ids"].shape[1]

        # Try sampling first; on NaN/inf error, retry with greedy decoding
        with torch.no_grad():
            try:
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=max(req.temperature, 0.01),
                    do_sample=req.temperature > 0,
                    pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
                )
            except RuntimeError as gen_err:
                if "probability tensor" in str(gen_err):
                    # Fallback to greedy decoding (no sampling = no NaN issue)
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        do_sample=False,
                        pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
                    )
                else:
                    raise
    except Exception as e:
        print(f"ERROR in generation: {e}\n{tb.format_exc()}")
        return JSONResponse(status_code=500, content={"error": {"message": str(e)}})

    # Decode only the new tokens
    new_tokens = outputs[0][input_len:]
    response_text = tokenizer.decode(new_tokens, skip_special_tokens=True)

    # Parse tool calls from Qwen's format
    tool_calls = None
    content = response_text

    import re

    if "<tool_call>" in response_text:
        tool_calls = []
        content = None
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

    # Fallback: model outputs tool call as raw JSON in text (no <tool_call> tags)
    # Detect {"name": "...", "arguments": {...}} pattern in content
    if not tool_calls and content:
        try:
            # Find JSON objects that look like tool calls (handle nested braces)
            _extracted = []
            for m in re.finditer(r'\{\s*"name"\s*:', content):
                start = m.start()
                # Walk forward to find balanced closing brace
                depth = 0
                end = start
                for idx in range(start, len(content)):
                    if content[idx] == '{':
                        depth += 1
                    elif content[idx] == '}':
                        depth -= 1
                        if depth == 0:
                            end = idx + 1
                            break
                if end > start:
                    try:
                        tc_data = json.loads(content[start:end])
                        if "name" in tc_data and "arguments" in tc_data:
                            _extracted.append(tc_data)
                    except json.JSONDecodeError:
                        pass
            if _extracted:
                tool_calls = []
                for tc_data in _extracted:
                    args = tc_data.get("arguments", {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except json.JSONDecodeError:
                            args = {}
                    tool_calls.append({
                        "id": f"call_{uuid.uuid4().hex[:8]}",
                        "type": "function",
                        "function": {
                            "name": tc_data["name"],
                            "arguments": json.dumps(args),
                        },
                    })
                content = None
        except Exception:
            pass  # Keep content as-is if parsing fails

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
        load_kwargs["device_map"] = "auto"
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
