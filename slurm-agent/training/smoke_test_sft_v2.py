#!/usr/bin/env python3
"""Smoke-test the v2 training data:

Validates each sample renders cleanly through Qwen's chat template AND that
the model server produces sane tool calls when given the same system prompt
+ tools as a sample's first turn.

Usage (on pod, with model server up on port 9000):
    cd slurm-agent
    python training/smoke_test_sft_v2.py --jsonl training/out/agent_sft_v2.jsonl --n 5
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def render_with_qwen(messages, tools):
    """Render via Qwen tokenizer chat template (no GPU needed)."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-14B-Instruct", trust_remote_code=True)
    text = tok.apply_chat_template(messages, tools=tools, tokenize=False, add_generation_prompt=False)
    return text


def quick_model_check(messages_first_two, tools, model_url):
    """Send first system+user to live model and see if it would produce tool_calls."""
    payload = {
        "model": "slurm-agent",
        "messages": messages_first_two,
        "tools": tools,
        "temperature": 0.1,
        "max_tokens": 256,
        "stream": False,
    }
    try:
        r = requests.post(f"{model_url}/v1/chat/completions", json=payload, timeout=60)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"
        data = r.json()
        msg = data["choices"][0]["message"]
        return msg, None
    except Exception as e:
        return None, str(e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl", default="training/out/agent_sft_v2.jsonl")
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--check-model", action="store_true",
                        help="Also call the live model server (port 9000) for each sample")
    parser.add_argument("--model-url", default="http://localhost:9000")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    path = (ROOT / args.jsonl).resolve()
    if not path.exists():
        print(f"ERROR: {path} not found")
        sys.exit(1)

    samples = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            samples.append(json.loads(line))
            if len(samples) >= args.n:
                break

    print(f"Loaded {len(samples)} samples from {path}")

    # Render all through Qwen template
    from transformers import AutoTokenizer
    print("Loading Qwen tokenizer...")
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-14B-Instruct", trust_remote_code=True)

    all_pass = True
    for i, s in enumerate(samples, 1):
        print(f"\n{'─'*70}")
        print(f"Sample {i}: id={s['metadata'].get('id')} role={s['metadata'].get('role')}")
        try:
            text = tok.apply_chat_template(s["messages"], tools=s["tools"],
                                            tokenize=False, add_generation_prompt=False)
            n_tokens = len(tok(text)["input_ids"])
            print(f"  ✓ Renders cleanly | {n_tokens} tokens")
            if args.verbose:
                print("  --- prompt preview (first 800 chars) ---")
                print(text[:800])
                print("  --- end preview ---")
        except Exception as e:
            print(f"  ✗ TEMPLATE ERROR: {e}")
            all_pass = False
            continue

        # Verify first 2 messages are system+user, and tool list non-empty
        if len(s["messages"]) < 2:
            print(f"  ✗ Too few messages: {len(s['messages'])}")
            all_pass = False
            continue
        if s["messages"][0]["role"] != "system":
            print(f"  ✗ First message not system: {s['messages'][0]['role']}")
            all_pass = False
        if not s["tools"]:
            print(f"  ✗ Empty tools list")
            all_pass = False

        # Optional: ping model server with first 2 messages
        if args.check_model:
            first_two = s["messages"][:2]
            tool_names_expected = []
            for m in s["messages"]:
                for tc in m.get("tool_calls", []) or []:
                    tool_names_expected.append(tc["function"]["name"])
            msg, err = quick_model_check(first_two, s["tools"], args.model_url)
            if err:
                print(f"  ✗ Model error: {err}")
                continue
            tcs = msg.get("tool_calls") or []
            tc_names = [t["function"]["name"] for t in tcs]
            if tcs:
                print(f"  ✓ Model emitted tool calls: {tc_names}")
            else:
                print(f"  ⚠ Model emitted text instead of tool_calls")
                print(f"    Expected: {tool_names_expected[:3]}")
                content = msg.get("content", "")
                print(f"    Content: {(content or '')[:200]}")

    print(f"\n{'─'*70}")
    print("ALL PASS" if all_pass else "FAILURES DETECTED")


if __name__ == "__main__":
    main()
