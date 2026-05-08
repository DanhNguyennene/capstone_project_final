#!/usr/bin/env python3
"""Fine-tune Qwen3-27B for the Slurm agent using QLoRA.

Designed for A100 80GB / H100 VRAM. Uses 4-bit NF4 quantization + LoRA adapters.
Trains on multi-turn tool-calling conversations from build_agent_sft.py output.

Usage:
    python training/train_agent_qlora.py                           # full training
    python training/train_agent_qlora.py --max-steps 50 --smoke    # quick smoke test
    python training/train_agent_qlora.py --export-gguf             # train + export for Ollama
    python training/train_agent_qlora.py --max-length 2048         # for 48GB VRAM
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, PeftModel
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForSeq2Seq,
    Trainer,
    TrainingArguments,
)


DEFAULT_BASE_MODEL = "Qwen/Qwen3.6-27B"
DEFAULT_DATA = "training/out/agent_sft.jsonl"
DEFAULT_OUTPUT = "training/out/slurm-agent-27b-lora"

# LoRA targets for Qwen3 — all linear layers
TARGET_MODULES = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="QLoRA fine-tune Qwen3-27B for Slurm agent")
    p.add_argument("--base-model", default=DEFAULT_BASE_MODEL)
    p.add_argument("--data", default=DEFAULT_DATA)
    p.add_argument("--out", default=DEFAULT_OUTPUT)
    p.add_argument("--max-length", type=int, default=4096,
                   help="Max sequence length (4096 for 80GB VRAM, use 2048 for 48GB)")
    p.add_argument("--epochs", type=float, default=3.0)
    p.add_argument("--max-steps", type=int, default=0,
                   help="Override epochs with fixed step count (for smoke tests)")
    p.add_argument("--batch-size", type=int, default=1)
    p.add_argument("--grad-accum", type=int, default=16,
                   help="Effective batch = batch_size × grad_accum = 16")
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--lora-r", type=int, default=64,
                   help="LoRA rank (64 for 27B model)")
    p.add_argument("--lora-alpha", type=int, default=128)
    p.add_argument("--lora-dropout", type=float, default=0.05)
    p.add_argument("--warmup-ratio", type=float, default=0.05)
    p.add_argument("--no-4bit", action="store_true")
    p.add_argument("--smoke", action="store_true",
                   help="Smoke test: 50 steps, small subset")
    p.add_argument("--export-gguf", action="store_true",
                   help="After training, merge adapter and export GGUF for Ollama")
    p.add_argument("--sample-count", type=int, default=0)
    p.add_argument("--init-adapter", default="",
                   help="Warm-start LoRA from an existing adapter dir "
                        "(continued fine-tuning). Reuses its lora_r/alpha.")
    p.add_argument("--resume-from-checkpoint", default="",
                   help="Resume Trainer state (optimizer, scheduler, step) "
                        "from a checkpoint dir produced by a previous run.")
    return p.parse_args()


def render_messages_qwen(tokenizer, messages: list[dict], tools: list[dict] | None = None) -> str:
    """Render messages using Qwen2.5's native chat template with tool support.

    `tools` is the role-scoped JSON-schema tool list emitted by
    build_agent_sft.py / build_agent_sft_traces.py. Passing it through the
    chat template is what teaches the model the per-sample tool boundary —
    without this the model learns that all tools are always available and
    hallucinates cross-role calls at inference time.
    """
    # Qwen2.5-Instruct has native tool_call support in its chat template.
    # We need to handle tool_calls and tool results properly.
    try:
        kwargs = dict(tokenize=False, add_generation_prompt=False)
        if tools:
            kwargs["tools"] = tools
        return tokenizer.apply_chat_template(messages, **kwargs)
    except Exception:
        # Fallback: manual rendering for tool messages
        rendered_msgs = []
        for msg in messages:
            if msg.get("tool_calls"):
                # Convert tool_calls to content format Qwen understands
                tc_text = json.dumps(msg["tool_calls"], ensure_ascii=False)
                rendered_msgs.append({
                    "role": "assistant",
                    "content": f"<tool_call>\n{tc_text}\n</tool_call>",
                })
            elif msg["role"] == "tool":
                rendered_msgs.append({
                    "role": "user",
                    "content": f"<tool_response>\n{msg.get('content', '')}\n</tool_response>",
                })
            else:
                rendered_msgs.append({
                    "role": msg["role"],
                    "content": msg.get("content") or "",
                })

        return tokenizer.apply_chat_template(
            rendered_msgs,
            tokenize=False,
            add_generation_prompt=False,
        )


def main():
    args = parse_args()

    if args.smoke:
        args.max_steps = args.max_steps or 50
        args.sample_count = args.sample_count or 200

    root = Path(__file__).resolve().parents[1]
    data_path = root / args.data
    output_dir = root / args.out
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"{'='*60}")
    print(f"  Slurm Agent QLoRA Fine-Tuning")
    print(f"{'='*60}")
    print(f"  Base model:  {args.base_model}")
    print(f"  Data:        {data_path}")
    print(f"  Output:      {output_dir}")
    print(f"  Max length:  {args.max_length}")
    print(f"  Epochs:      {args.epochs}")
    print(f"  Batch:       {args.batch_size} × {args.grad_accum} = {args.batch_size * args.grad_accum}")
    print(f"  LoRA:        r={args.lora_r}, α={args.lora_alpha}")
    print(f"  4-bit:       {not args.no_4bit}")
    print(f"  CUDA:        {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  GPU:         {torch.cuda.get_device_name(0)}")
        print(f"  VRAM:        {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    print(f"{'='*60}\n")

    # Load tokenizer
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Quantization config
    quant_config = None
    if not args.no_4bit:
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
            bnb_4bit_use_double_quant=True,
        )

    # Load model
    print("Loading model (4-bit quantized)...")
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        device_map="auto",
        torch_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
        quantization_config=quant_config,
        trust_remote_code=True,
        attn_implementation="flash_attention_2",
    )

    if quant_config:
        # Don't let prepare_model_for_kbit_training enable gradient
        # checkpointing — it uses use_reentrant=True which disables
        # flash-attn's fast path. We enable grad-ckpt below in
        # TrainingArguments with use_reentrant=False instead.
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=False)
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.enable_input_require_grads()

    if args.init_adapter:
        init_path = Path(args.init_adapter)
        if not init_path.is_absolute():
            init_path = root / init_path
        print(f"\nWarm-starting LoRA from existing adapter: {init_path}")
        model = PeftModel.from_pretrained(model, str(init_path), is_trainable=True)
    else:
        # LoRA config
        peft_config = LoraConfig(
            r=args.lora_r,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=TARGET_MODULES,
            layers_to_transform=list(range(36, 48)),
        )
        model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # Load and tokenize dataset
    print(f"\nLoading dataset from {data_path}...")
    dataset = load_dataset("json", data_files=str(data_path), split="train")
    if args.sample_count and args.sample_count > 0:
        dataset = dataset.select(range(min(args.sample_count, len(dataset))))

    # Filter: remove edge-case samples with no tool calls (just clarification questions)
    # These dilute tool-calling signal. Keep only samples with ≥4 messages or tool_calls.
    pre_filter = len(dataset)
    dataset = dataset.filter(
        lambda ex: len(ex["messages"]) > 3 or any(
            m.get("tool_calls") for m in ex["messages"]
        )
    )
    print(f"  Loaded: {pre_filter} → filtered to {len(dataset)} (removed {pre_filter - len(dataset)} edge-only samples)")
    print(f"  Training samples: {len(dataset)}")

    def tokenize(example):
        messages = example["messages"]
        tools = example.get("tools") or None
        text = render_messages_qwen(tokenizer, messages, tools=tools)
        # LEFT-truncate: keep the END of the sequence so assistant tool_calls
        # (the actual training labels) are preserved. The system prompt at the
        # start gets clipped instead — model has the full prompt at inference.
        tokenizer.truncation_side = "left"
        tokenized = tokenizer(
            text,
            truncation=True,
            max_length=args.max_length,
            padding=False,
        )
        tokenized["labels"] = list(tokenized["input_ids"])
        return tokenized

    print("Tokenizing...")
    tokenized_dataset = dataset.map(
        tokenize,
        remove_columns=dataset.column_names,
        num_proc=4,
    )

    # Filter out samples that are too short
    tokenized_dataset = tokenized_dataset.filter(lambda x: len(x["input_ids"]) > 10)
    print(f"  After filtering: {len(tokenized_dataset)} samples")

    # Data collator: pads input_ids with pad_token_id and labels with -100
    # so cross-entropy ignores padding. Required for batch_size > 1 with
    # variable-length sequences.
    collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        padding=True,
        label_pad_token_id=-100,
        return_tensors="pt",
    )

    # Training args
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        max_steps=args.max_steps if args.max_steps > 0 else -1,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        warmup_ratio=args.warmup_ratio,
        lr_scheduler_type="cosine",
        logging_steps=5,
        save_steps=100,
        save_total_limit=2,
        bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
        fp16=torch.cuda.is_available() and not torch.cuda.is_bf16_supported(),
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        optim="paged_adamw_8bit",
        report_to="wandb",
        remove_unused_columns=False,
        dataloader_pin_memory=True,
        dataloader_num_workers=2,
    )

    # Train
    print("\nStarting training...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=collator,
    )
    resume = args.resume_from_checkpoint or None
    if resume:
        resume_path = Path(resume)
        if not resume_path.is_absolute():
            resume_path = root / resume_path
        print(f"Resuming Trainer state from: {resume_path}")
        trainer.train(resume_from_checkpoint=str(resume_path))
    else:
        trainer.train()

    # Save adapter
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    # Save metadata
    metadata = {
        "base_model": args.base_model,
        "data": str(data_path),
        "samples": len(tokenized_dataset),
        "adapter_dir": str(output_dir),
        "lora_r": args.lora_r,
        "lora_alpha": args.lora_alpha,
        "epochs": args.epochs,
        "max_steps": args.max_steps,
        "max_length": args.max_length,
    }
    (output_dir / "training_metadata.json").write_text(json.dumps(metadata, indent=2))
    print(f"\n✓ Saved adapter → {output_dir}")

    # Optional GGUF export
    if args.export_gguf:
        export_gguf(args.base_model, output_dir)


def export_gguf(base_model: str, adapter_dir: Path):
    """Merge adapter into base model and export as GGUF for Ollama."""
    merged_dir = adapter_dir / "merged"
    gguf_path = adapter_dir / "slurm-agent-q4_k_m.gguf"

    print(f"\nMerging adapter with base model...")

    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    base = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.float16,
        device_map="cpu",
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base, str(adapter_dir))
    model = model.merge_and_unload()

    model.save_pretrained(str(merged_dir))
    tokenizer.save_pretrained(str(merged_dir))
    print(f"  Merged model → {merged_dir}")

    # Create Ollama Modelfile
    modelfile = adapter_dir / "Modelfile"
    modelfile.write_text(f"""FROM {gguf_path}

SYSTEM "You are a Slurm HPC cluster assistant. You monitor, analyze, diagnose, and execute actions on Slurm clusters using appropriate tools."

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
""")
    print(f"  Modelfile → {modelfile}")
    print(f"\n  To convert to GGUF, run:")
    print(f"    python llama.cpp/convert_hf_to_gguf.py {merged_dir} --outfile {gguf_path} --outtype q4_k_m")
    print(f"\n  Then load in Ollama:")
    print(f"    ollama create slurm-agent-ft -f {modelfile}")


if __name__ == "__main__":
    main()
