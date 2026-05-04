#!/usr/bin/env python3
"""Load a specialist LoRA adapter and generate one planning response."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


ROOT = Path(__file__).resolve().parents[1]


def render(tokenizer, messages):
    if getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return "\n".join(f"<{msg['role']}>\n{msg['content']}\n</{msg['role']}>" for msg in messages)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test a specialist LoRA adapter")
    parser.add_argument("--adapter", default="training/out/slurm-specialist-qwen05b-lora-quick")
    parser.add_argument("--sample-file", default="training/out/specialist_sft_smoke.jsonl")
    parser.add_argument("--sample-index", type=int, default=0)
    parser.add_argument("--max-new-tokens", type=int, default=160)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    adapter_dir = (ROOT / args.adapter).resolve()
    config = json.loads((adapter_dir / "adapter_config.json").read_text())
    base_model = config["base_model_name_or_path"]

    tokenizer = AutoTokenizer.from_pretrained(adapter_dir, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        device_map="auto",
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
    )
    model = PeftModel.from_pretrained(model, adapter_dir)
    model.eval()

    sample_path = (ROOT / args.sample_file).resolve()
    sample_line = sample_path.read_text().splitlines()[args.sample_index]
    sample = json.loads(sample_line)
    prompt_messages = sample["messages"][:-1]
    expected = sample["messages"][-1]["content"]

    prompt = render(tokenizer, prompt_messages)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        generated = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_tokens = generated[0][inputs["input_ids"].shape[1] :]
    output = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    print("EXPECTED:")
    print(expected)
    print("\nGENERATED:")
    print(output)


if __name__ == "__main__":
    main()