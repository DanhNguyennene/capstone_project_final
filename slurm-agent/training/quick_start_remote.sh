#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
#  ONE-SHOT SETUP FOR RENTED GPU SERVER
#  Copy this entire script to the server and run it.
#
#  Usage:
#    curl -sL <raw_gist_url> | bash
#    # OR just paste this script into terminal
# ═══════════════════════════════════════════════════════════════════
set -e

# ─── CONFIG (edit these) ──────────────────────────────────────────
GH_USER="pnguyen1"
GH_REPO="capstone_project"
GH_PAT="${GH_PAT:?Set GH_PAT env var first: export GH_PAT=ghp_xxxxx}"
HF_TOKEN="${HF_TOKEN:-}"  # optional, for gated models
# ──────────────────────────────────────────────────────────────────

echo "=============================================="
echo "  Quick Start: Slurm Agent 27B Training"
echo "=============================================="

# 1. System deps
echo "[1/6] Installing system packages..."
sudo apt-get update -qq && sudo apt-get install -y -qq python3-pip python3-venv git > /dev/null 2>&1

# 2. Clone repo
echo "[2/6] Cloning repo..."
if [ -d "$GH_REPO" ]; then
    echo "  Repo already exists, pulling latest..."
    cd "$GH_REPO" && git pull && cd ..
else
    git clone --depth 1 "https://${GH_PAT}@github.com/${GH_USER}/${GH_REPO}.git"
fi
cd "${GH_REPO}/slurm-agent"

# 3. Python venv
echo "[3/6] Setting up Python environment..."
python3 -m venv ~/train_env
source ~/train_env/bin/activate
pip install --upgrade pip -q

# 4. Install PyTorch + deps
echo "[4/6] Installing PyTorch + training dependencies..."
pip install torch --index-url https://download.pytorch.org/whl/cu124 -q
pip install -r training/requirements-finetune.txt -q

# 5. HuggingFace login (for gated models)
if [ -n "$HF_TOKEN" ]; then
    echo "[5/6] Logging into HuggingFace..."
    pip install huggingface_hub -q
    huggingface-cli login --token "$HF_TOKEN"
else
    echo "[5/6] Skipping HF login (set HF_TOKEN if model is gated)"
fi

# 6. Verify GPU
echo "[6/6] Verifying GPU..."
nvidia-smi
python3 -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f'VRAM: {vram:.0f} GB')
    if vram < 40:
        print('WARNING: <48GB VRAM. Use --max-length 2048')
"

echo ""
echo "=============================================="
echo "  READY! Run training with:"
echo ""
echo "  source ~/train_env/bin/activate"
echo "  cd ~/$(basename $PWD)"
echo ""
echo "  # Smoke test (2 min):"
echo "  python training/train_agent_qlora.py --smoke"
echo ""
echo "  # Full training (~3-4h on A100 80GB):"
echo "  python training/train_agent_qlora.py"
echo ""
echo "  # If 48GB GPU:"
echo "  python training/train_agent_qlora.py --max-length 2048"
echo "=============================================="
