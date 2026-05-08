#!/usr/bin/env python3
"""Pick the N longest samples (by Qwen-rendered token count) and write them to a
worst-case smoke dataset. If `train_agent_qlora.py` survives a few steps on
this dataset at the chosen max_length, full training is unlikely to OOM.

Usage:
    python training/pick_longest_samples.py --top 16 \
        --src training/out/agent_sft_v2.jsonl \
        --out training/out/agent_sft_v2_worst16.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from training.train_agent_qlora import render_messages_qwen  # type: ignore
from transformers import AutoTokenizer  # type: ignore


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="training/out/agent_sft_v2.jsonl")
    ap.add_argument("--out", default="training/out/agent_sft_v2_worst.jsonl")
    ap.add_argument("--top", type=int, default=16)
    ap.add_argument("--base-model", default="Qwen/Qwen2.5-14B-Instruct")
    args = ap.parse_args()

    src = (ROOT / args.src).resolve()
    out = (ROOT / args.out).resolve()

    print(f"Loading tokenizer {args.base_model}...")
    tok = AutoTokenizer.from_pretrained(args.base_model, use_fast=True, trust_remote_code=True)

    print(f"Scanning {src}...")
    sized: list[tuple[int, dict]] = []
    with src.open() as f:
        for i, line in enumerate(f):
            ex = json.loads(line)
            text = render_messages_qwen(tok, ex["messages"], tools=ex.get("tools"))
            n = len(tok(text, add_special_tokens=False).input_ids)
            sized.append((n, ex))
            if (i + 1) % 500 == 0:
                print(f"  scanned {i+1}, max so far: {max(s[0] for s in sized)}")

    sized.sort(key=lambda t: t[0], reverse=True)
    top = sized[: args.top]
    print(f"\nTop {args.top} sizes: {[n for n, _ in top]}")

    with out.open("w") as f:
        for _, ex in top:
            f.write(json.dumps(ex) + "\n")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
