#!/usr/bin/env python3
"""Debug vocab size mismatch between tokenizer, config, and adapter."""
import os
import json
from pathlib import Path

from transformers import AutoTokenizer, AutoConfig

root = Path(__file__).resolve().parents[1]
adapter_path = root / "training" / "qlora_output"

print("=" * 60)
print("  Vocab Size Debug")
print("=" * 60)

# 1. Base model config
config = AutoConfig.from_pretrained("Qwen/Qwen2.5-14B-Instruct", trust_remote_code=True)
print(f"\n  Config vocab_size:  {config.vocab_size}")

# 2. Base tokenizer
tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-14B-Instruct", trust_remote_code=True)
print(f"  Tokenizer len():    {len(tok)}")

# 3. Adapter config
cfg = json.load(open(adapter_path / "adapter_config.json"))
print(f"\n  Adapter config:")
print(f"    modules_to_save:  {cfg.get('modules_to_save', None)}")
print(f"    target_modules:   {cfg.get('target_modules', None)}")
print(f"    r:                {cfg.get('r', None)}")
print(f"    lora_alpha:       {cfg.get('lora_alpha', None)}")

# 4. Check safetensors keys
print(f"\n  Adapter safetensors:")
try:
    from safetensors import safe_open
    for f in sorted(os.listdir(adapter_path)):
        if f.endswith(".safetensors"):
            with safe_open(str(adapter_path / f), framework="pt") as sf:
                keys = list(sf.keys())
                embed_keys = [k for k in keys if "embed" in k or "lm_head" in k]
                print(f"    {f}: {len(keys)} tensors")
                if embed_keys:
                    print(f"      EMBED KEYS: {embed_keys}")
                    for ek in embed_keys:
                        t = sf.get_tensor(ek)
                        print(f"        {ek}: shape={t.shape}")
                else:
                    print(f"      (no embed/lm_head keys)")
                # Print first 5 keys as sample
                print(f"      sample keys: {keys[:5]}")
except ImportError:
    print("    safetensors not installed, checking with torch")
    import torch
    for f in sorted(os.listdir(adapter_path)):
        if f.endswith(".safetensors") or f.endswith(".bin"):
            sd = torch.load(str(adapter_path / f), map_location="cpu") if f.endswith(".bin") else None
            if sd:
                embed_keys = [k for k in sd if "embed" in k or "lm_head" in k]
                print(f"    {f}: {len(sd)} tensors, embed keys: {embed_keys}")

print("\n" + "=" * 60)
print("  If embed keys exist with shape[0] != config.vocab_size,")
print("  training resized embeddings and 4-bit inference will fail.")
print("  Use --no-4bit to allow resize_token_embeddings().")
print("=" * 60)
