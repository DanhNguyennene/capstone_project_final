#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  A40 (48GB) Quick Start — Qwen2.5-14B QLoRA Fine-Tuning
#  Copy-paste this entire block on the rented server.
# ═══════════════════════════════════════════════════════════════
set -e

export GH_PAT="${GH_PAT:?Set GH_PAT first: export GH_PAT=ghp_xxxxx}"

# Clone
if [ ! -d "capstone_project" ]; then
  git clone --depth 1 https://$GH_PAT@github.com/DanhNguyennene/capstone_project.git
fi
cd capstone_project/slurm-agent

# Venv
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -q uv setuptools

# Install (A40 = Ampere, CUDA 12.4 compatible)
uv pip install torch --index-url https://download.pytorch.org/whl/cu124
uv pip install transformers==4.46.3 peft==0.13.2 bitsandbytes accelerate==0.34.2 datasets scipy

# Verify
python -c "
import torch, bitsandbytes
print(f'PyTorch {torch.__version__}, CUDA {torch.version.cuda}')
print(f'GPU: {torch.cuda.get_device_name(0)}')
print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory/1024**3:.0f} GB')
print(f'bf16: {torch.cuda.is_bf16_supported()}')
print('bitsandbytes OK')
"

# Train
echo ""
echo "Starting training..."
python training/train_agent_qlora.py \
  --base-model Qwen/Qwen2.5-14B-Instruct \
  --max-length 2048 \
  --lora-r 64 \
  --lora-alpha 128 \
  --epochs 3 \
  --grad-accum 16 \
  --out training/out/slurm-agent-14b-lora
