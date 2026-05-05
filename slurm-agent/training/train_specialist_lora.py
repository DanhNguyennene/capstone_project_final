#!/usr/bin/env python3
"""Quick LoRA/QLoRA trainer for the Slurm specialist planner.

The training data is produced by training/build_specialist_sft.mjs as chat-style
JSONL. This script trains a PEFT adapter; it does not replace the main model.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)


DEFAULT_TARGET_MODULES = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]


def render_messages(tokenizer, messages: list[dict[str, str]]) -> str:
    if getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    rendered = []
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        rendered.append(f"<{role}>\n{content}\n</{role}>")
    return "\n".join(rendered)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a Slurm specialist LoRA adapter")
    parser.add_argument("--data", default="training/out/specialist_sft.jsonl")
    parser.add_argument("--base-model", default="google/gemma-2b-it")
    parser.add_argument("--out", default="training/out/slurm-specialist-lora")
    parser.add_argument("--max-length", type=int, default=2048)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--max-steps", type=int, default=0, help="Use a small value such as 20 for smoke tests")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--grad-accum", type=int, default=8)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--no-4bit", action="store_true", help="Disable 4-bit loading")
    parser.add_argument("--sample-count", type=int, default=0, help="Optional small subset for smoke training")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_path = Path(args.data)
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quantization_config = None
    if not args.no_4bit:
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            bnb_4bit_use_double_quant=True,
        )

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        device_map="auto",
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        quantization_config=quantization_config,
    )
    if quantization_config is not None:
        model = prepare_model_for_kbit_training(model)

    peft_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=DEFAULT_TARGET_MODULES,
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    dataset = load_dataset("json", data_files=str(data_path), split="train")
    if args.sample_count and args.sample_count > 0:
        dataset = dataset.select(range(min(args.sample_count, len(dataset))))

    def tokenize(example):
        text = render_messages(tokenizer, example["messages"])
        tokenized = tokenizer(text, truncation=True, max_length=args.max_length)
        tokenized["labels"] = list(tokenized["input_ids"])
        return tokenized

    tokenized_dataset = dataset.map(tokenize, remove_columns=dataset.column_names)
    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        max_steps=args.max_steps if args.max_steps > 0 else -1,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        logging_steps=5,
        save_steps=50,
        save_total_limit=2,
        bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
        fp16=torch.cuda.is_available() and not torch.cuda.is_bf16_supported(),
        report_to="none",
        remove_unused_columns=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=collator,
    )
    trainer.train()
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    metadata = {
        "base_model": args.base_model,
        "data": str(data_path),
        "samples": len(dataset),
        "adapter_dir": str(output_dir),
    }
    (output_dir / "training_metadata.json").write_text(json.dumps(metadata, indent=2))
    print(f"saved specialist LoRA adapter -> {output_dir}")


if __name__ == "__main__":
    main()