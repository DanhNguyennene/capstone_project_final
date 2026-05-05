#!/usr/bin/env python3
"""Serve a specialist LoRA adapter through a tiny OpenAI-compatible API."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from peft import PeftModel
from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer


ROOT = Path(__file__).resolve().parents[1]


class LoadProgress:
    def __init__(self, total_steps: int):
        self.total_steps = total_steps
        self.current_step = 0

    @contextmanager
    def step(self, label: str):
        self.current_step += 1
        stop = threading.Event()
        start = time.time()
        spinner = itertools.cycle("|/-\\")
        width = 24

        def _render(done: bool = False) -> None:
            elapsed = int(time.time() - start)
            filled = width if done else max(1, int(width * (self.current_step - 0.5) / self.total_steps))
            bar = "#" * filled + "." * (width - filled)
            marker = "done" if done else next(spinner)
            sys.stdout.write(
                f"\r[load {self.current_step}/{self.total_steps}] [{bar}] {marker} {label} ({elapsed}s)"
            )
            sys.stdout.flush()

        def _heartbeat() -> None:
            while not stop.wait(0.25):
                _render(False)

        print(f"[load {self.current_step}/{self.total_steps}] {label}...", flush=True)
        worker = threading.Thread(target=_heartbeat, daemon=True)
        worker.start()
        try:
            yield
        finally:
            stop.set()
            worker.join(timeout=1)
            _render(True)
            print(flush=True)


class ChatMessage(BaseModel):
    role: str
    content: str | list[dict[str, Any]] | None = ""


class ChatRequest(BaseModel):
    model: str = "slurm-todo-specialist-qwen05b-lora-quick"
    messages: list[ChatMessage]
    max_tokens: int | None = Field(default=300, alias="max_tokens")
    temperature: float | None = 0.0
    stream: bool | None = False


def normalize_content(content: str | list[dict[str, Any]] | None) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    parts = []
    for item in content:
        if isinstance(item, dict):
            parts.append(str(item.get("text") or item.get("content") or ""))
    return "\n".join(part for part in parts if part)


def render_messages(tokenizer, messages: list[ChatMessage]) -> str:
    normalized = [
        {"role": message.role, "content": normalize_content(message.content)}
        for message in messages
    ]
    if getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(normalized, tokenize=False, add_generation_prompt=True)
    return "\n".join(f"<{msg['role']}>\n{msg['content']}\n</{msg['role']}>" for msg in normalized)


def create_app(adapter_dir: Path, model_id: str) -> FastAPI:
    progress = LoadProgress(total_steps=5)
    with progress.step(f"Reading adapter config from {adapter_dir}"):
        config = json.loads((adapter_dir / "adapter_config.json").read_text())
        base_model = config["base_model_name_or_path"]

    with progress.step("Loading tokenizer"):
        tokenizer = AutoTokenizer.from_pretrained(adapter_dir, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    device_note = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    with progress.step(f"Loading base model {base_model} on {device_note}"):
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            device_map="auto",
            dtype=dtype,
        )
    with progress.step("Attaching LoRA adapter"):
        model = PeftModel.from_pretrained(model, adapter_dir)
    with progress.step("Preparing inference server"):
        model.eval()
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        print(f"[load] Ready: model_id={model_id}", flush=True)

    app = FastAPI(title="Slurm Specialist Adapter API")

    @app.get("/v1/models")
    async def models():
        return {
            "object": "list",
            "data": [{"id": model_id, "object": "model", "created": 0, "owned_by": "local"}],
        }

    @app.post("/v1/chat/completions")
    async def chat_completions(request: ChatRequest):
        if request.stream:
            raise HTTPException(status_code=400, detail="streaming is not implemented for the local specialist adapter")
        prompt = render_messages(tokenizer, request.messages)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            generated = model.generate(
                **inputs,
                max_new_tokens=request.max_tokens or 300,
                do_sample=bool(request.temperature and request.temperature > 0),
                temperature=request.temperature if request.temperature and request.temperature > 0 else None,
                pad_token_id=tokenizer.eos_token_id,
            )
        new_tokens = generated[0][inputs["input_ids"].shape[1] :]
        content = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        completion_tokens = int(new_tokens.shape[0])
        prompt_tokens = int(inputs["input_ids"].shape[1])
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model or model_id,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        }

    return app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve a Slurm specialist LoRA adapter")
    parser.add_argument("--adapter", default="training/out/slurm-todo-specialist-qwen05b-lora-quick")
    parser.add_argument("--model-id", default="slurm-todo-specialist-qwen05b-lora-quick")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8010)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    adapter_dir = (ROOT / args.adapter).resolve()
    print("[serve] Starting Slurm specialist adapter server", flush=True)
    print(f"[serve] Adapter: {adapter_dir}", flush=True)
    print(f"[serve] URL: http://{args.host}:{args.port}/v1", flush=True)
    app = create_app(adapter_dir, args.model_id)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()