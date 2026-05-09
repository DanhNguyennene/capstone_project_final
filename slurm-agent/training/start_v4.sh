#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  v4 Training — Qwen2.5-14B QLoRA on A40 (44GB)
#  Distilled from GPT-5.4 traces (3329 samples)
#
#  Usage:
#    export GH_PAT=ghp_xxxxx
#    bash training/start_v4.sh          # full training
#    bash training/start_v4.sh --smoke  # 50-step smoke test
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

SMOKE=0
if [[ "${1:-}" == "--smoke" ]]; then SMOKE=1; fi

export GH_PAT="${GH_PAT:?Set GH_PAT first: export GH_PAT=ghp_xxxxx}"

# ── 1. Clone / pull ──
if [ ! -d "capstone_project" ]; then
  echo "Cloning repo..."
  git clone --depth 1 "https://$GH_PAT@github.com/DanhNguyennene/capstone_project.git"
else
  echo "Pulling latest..."
  cd capstone_project && git pull && cd ..
fi
cd capstone_project/slurm-agent

# ── 2. Venv + deps ──
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q --upgrade pip setuptools wheel

# Core training deps — A40 is Ampere (sm_86), CUDA 12.x
# Pin versions to avoid transformers/torch incompatibility
pip install -q torch --index-url https://download.pytorch.org/whl/cu124
pip install -q transformers==4.46.3 peft==0.13.2 bitsandbytes accelerate==0.34.2 datasets scipy wandb

# Flash Attention 2 — compiles from source, takes 5-10 min
if ! python -c "import flash_attn" 2>/dev/null; then
  echo "Installing flash-attn (this takes ~10 min on first run)..."
  pip install flash-attn --no-build-isolation
fi

# ── 3. Verify GPU ──
python3 -c "
import torch
print(f'PyTorch {torch.__version__}, CUDA {torch.version.cuda}')
print(f'GPU: {torch.cuda.get_device_name(0)}')
print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory/1024**3:.0f} GB')
print(f'bf16: {torch.cuda.is_bf16_supported()}')
import flash_attn; print(f'flash-attn {flash_attn.__version__}')
import bitsandbytes; print('bitsandbytes OK')
"

# ── 4. Verify data exists ──
DATA="out/agent_sft_v3_base.jsonl"
if [ ! -f "$DATA" ]; then
  echo "ERROR: $DATA not found. Check git pull."
  exit 1
fi
ROWS=$(wc -l < "$DATA")
echo "Training data: $DATA ($ROWS rows)"

# ── 5. Train ──
echo ""
echo "════════════════════════════════════════════════"
echo "  v4 Training: Qwen2.5-14B + LoRA (all layers)"
echo "  Data: $ROWS samples, max_length=8192"
echo "  Effective batch: 1 × 16 = 16"
echo "  Epochs: 3, lr: 1e-4, LoRA r=64 α=128"
echo "════════════════════════════════════════════════"
echo ""

export WANDB_PROJECT="slurm-agent-v4"

if [ $SMOKE -eq 1 ]; then
  echo "SMOKE TEST MODE (50 steps)"
  python training/train_agent_qlora.py \
    --base-model Qwen/Qwen2.5-14B-Instruct \
    --data "$DATA" \
    --out training/out/slurm-agent-14b-lora-v4 \
    --max-length 8192 \
    --all-layers \
    --lora-r 64 \
    --lora-alpha 128 \
    --epochs 3 \
    --grad-accum 16 \
    --skip-validation \
    --smoke
else
  python training/train_agent_qlora.py \
    --base-model Qwen/Qwen2.5-14B-Instruct \
    --data "$DATA" \
    --out training/out/slurm-agent-14b-lora-v4 \
    --max-length 8192 \
    --all-layers \
    --lora-r 64 \
    --lora-alpha 128 \
    --epochs 3 \
    --grad-accum 16 \
    --skip-validation
fi

echo ""
echo "════════════════════════════════════════════════"
echo "  Training complete!"
echo "  Adapter: training/out/slurm-agent-14b-lora-v4"
echo "════════════════════════════════════════════════"
