#!/bin/bash
# Setup script for rented GPU server (A100 80GB / H100)
# Run this first on a fresh Ubuntu/CUDA machine to install dependencies and start training.
#
# Usage:
#   chmod +x training/setup_server.sh
#   ./training/setup_server.sh          # install deps + start training
#   ./training/setup_server.sh --smoke   # quick 50-step test first

set -e

echo "=============================================="
echo "  Slurm Agent 27B QLoRA Training Setup"
echo "=============================================="

# Check GPU
nvidia-smi || { echo "ERROR: No GPU detected"; exit 1; }

# Install system deps
apt-get update && apt-get install -y python3-pip python3-venv git

# Create venv
python3 -m venv ~/train_env
source ~/train_env/bin/activate

# Install PyTorch (CUDA 12.x)
pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cu124

# Install training deps
pip install -r training/requirements-finetune.txt

# Download model weights (will cache in ~/.cache/huggingface)
echo ""
echo "Pre-downloading Qwen3-27B weights..."
python3 -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
print('Downloading tokenizer...')
AutoTokenizer.from_pretrained('Qwen/Qwen3-27B', trust_remote_code=True)
print('Downloading model config (weights download on first train)...')
from huggingface_hub import snapshot_download
snapshot_download('Qwen/Qwen3-27B', ignore_patterns=['*.safetensors'])
print('Done. Model weights will stream on first load.')
"

echo ""
echo "=============================================="
echo "  Setup complete. Start training with:"
echo ""
echo "  source ~/train_env/bin/activate"
echo "  cd $(pwd)"
echo "  python training/train_agent_qlora.py"
echo ""
echo "  For smoke test first:"
echo "  python training/train_agent_qlora.py --smoke"
echo ""
echo "  For 48GB GPU (reduce seq len):"
echo "  python training/train_agent_qlora.py --max-length 2048"
echo "=============================================="

# If --smoke flag passed, run smoke test
if [[ "$1" == "--smoke" ]]; then
    echo ""
    echo "Running smoke test..."
    python3 training/train_agent_qlora.py --smoke
fi
