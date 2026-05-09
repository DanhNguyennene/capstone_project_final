#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  COMPLETE Pod Setup — A40 (44GB)
#  Run this ONCE on a fresh pod. Does everything:
#    1. Clones repo
#    2. Installs ALL deps (agent, MCP, model server, eval, training)
#    3. Verifies GPU + all imports
#
#  Usage:
#    export GH_PAT=ghp_xxxxx
#    bash setup_pod.sh
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

export GH_PAT="${GH_PAT:?Set GH_PAT first: export GH_PAT=ghp_xxxxx}"

echo "══════════════════════════════════════════"
echo "  STEP 1: Clone repo"
echo "══════════════════════════════════════════"
cd /workspace
if [ ! -d "capstone_project" ]; then
  git clone --depth 1 "https://$GH_PAT@github.com/DanhNguyennene/capstone_project.git"
else
  cd capstone_project && git pull && cd ..
fi
cd capstone_project/slurm-agent

echo ""
echo "══════════════════════════════════════════"
echo "  STEP 2: Install ALL dependencies"
echo "══════════════════════════════════════════"

# Upgrade pip
pip install --upgrade pip setuptools wheel

# PyTorch (CUDA 12.4, Ampere)
pip install torch --index-url https://download.pytorch.org/whl/cu124

# Training deps (pinned for compat)
pip install transformers==4.46.3 peft==0.13.2 bitsandbytes accelerate==0.34.2 datasets scipy wandb

# Agent deps
pip install fastapi uvicorn pydantic python-dotenv python-multipart \
  openai openai-agents truststore websockets aiohttp httpx httpx-sse

# MCP deps
pip install mcp matplotlib

# Model server deps (serve_ft_model.py)
# (transformers, peft, torch already installed above)

# Eval deps
pip install aiohttp

# Agent's lookup_slurm_docs tool (sentence-transformers for RAG)
pip install sentence-transformers numpy

# Flash Attention 2
if ! python -c "import flash_attn" 2>/dev/null; then
  echo ""
  echo "Installing flash-attn (compiles from source, ~10 min)..."
  pip install flash-attn --no-build-isolation
fi

echo ""
echo "══════════════════════════════════════════"
echo "  STEP 3: Verify everything"
echo "══════════════════════════════════════════"

python3 -c "
import sys
errors = []

# Core
try:
    import torch
    print(f'  torch {torch.__version__}, CUDA {torch.version.cuda}')
    print(f'  GPU: {torch.cuda.get_device_name(0)}')
    print(f'  VRAM: {torch.cuda.get_device_properties(0).total_memory/1024**3:.0f} GB')
    print(f'  bf16: {torch.cuda.is_bf16_supported()}')
except Exception as e: errors.append(f'torch: {e}')

# Training
try:
    import transformers, peft, bitsandbytes, accelerate, datasets
    print(f'  transformers {transformers.__version__}')
    print(f'  peft {peft.__version__}')
    print(f'  bitsandbytes OK')
except Exception as e: errors.append(f'training deps: {e}')

# Flash attention
try:
    import flash_attn
    print(f'  flash-attn {flash_attn.__version__}')
except Exception as e: errors.append(f'flash-attn: {e}')

# Agent
try:
    import fastapi, uvicorn, openai, agents
    print(f'  fastapi OK, openai {openai.__version__}, openai-agents OK')
except Exception as e: errors.append(f'agent deps: {e}')

# MCP
try:
    import mcp
    print(f'  mcp OK')
except Exception as e: errors.append(f'mcp: {e}')

# Sentence transformers (for lookup_slurm_docs RAG)
try:
    import sentence_transformers, numpy
    print(f'  sentence-transformers OK, numpy OK')
except Exception as e: errors.append(f'sentence-transformers: {e}')

# Eval
try:
    import aiohttp
    print(f'  aiohttp OK')
except Exception as e: errors.append(f'aiohttp: {e}')

if errors:
    print(f'\\n  ERRORS:')
    for e in errors:
        print(f'    ✗ {e}')
    sys.exit(1)
else:
    print(f'\\n  ✓ All imports OK')
"

echo ""
echo "══════════════════════════════════════════"
echo "  SETUP COMPLETE"
echo ""
echo "  To run base model eval:"
echo "    bash run_base_eval.sh"
echo ""
echo "  To train v4:"
echo "    bash training/start_v4.sh"
echo ""
echo "  To serve FT model after training:"
echo "    python evaluation/serve_ft_model.py \\"
echo "      --adapter training/out/slurm-agent-14b-lora-v4 \\"
echo "      --merge --port 9000"
echo "══════════════════════════════════════════"
