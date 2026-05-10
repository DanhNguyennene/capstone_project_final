#!/bin/bash
set -euo pipefail

ROOT=/workspace/capstone_project/slurm-agent
cd $ROOT

ADAPTER_DIR="/workspace/adapter_final"
if [[ "${1:-}" == "--adapter" ]]; then
  ADAPTER_DIR="$2"
fi

echo "Killing any existing processes..."
pkill -9 -f slurm_mcp_sse.py 2>/dev/null || true
pkill -9 -f 'main:app' 2>/dev/null || true
pkill -9 -f serve_ft_model 2>/dev/null || true
pkill -9 -f scenario_eval 2>/dev/null || true
sleep 3

# ── 0. Download adapter ──
if [ ! -f "$ADAPTER_DIR/adapter_model.safetensors" ]; then
  echo "[0/4] Downloading adapter from HuggingFace..."
  pip install huggingface_hub -q
  huggingface-cli download DanhVuiVe/slurm-agent-qwen14b-lora-final \
    --local-dir $ADAPTER_DIR
else
  echo "[0/4] Adapter already present at $ADAPTER_DIR"
fi

# ── 1. MCP ──
echo "[1/4] Starting MCP server on :3002..."
nohup python $ROOT/mcp-server/slurm_mcp_sse.py > $ROOT/mcp.log 2>&1 &
sleep 5
ss -tlnp | grep -q ':3002' && echo "  MCP ✓" || { cat $ROOT/mcp.log; exit 1; }

# ── 2. Model server (BF16) ──
echo "[2/4] Starting model server on :9000 (adapter: $ADAPTER_DIR)..."
export OPENAI_AGENTS_DISABLE_TRACING=1
nohup python $ROOT/evaluation/serve_ft_model.py \
  --adapter $ADAPTER_DIR --port 9000 --no-4bit --max-new-tokens 2048 \
  > $ROOT/serve_ft.log 2>&1 &
echo "  Waiting for model..."; until curl -s http://localhost:9000/health > /dev/null 2>&1; do sleep 10; done; echo "  Model ✓"

# ── 3. Agent ──
echo "[3/4] Starting agent on :8000..."
export OPENAI_BASE_URL=http://localhost:9000/v1
export OPENAI_API_KEY=dummy
export SLURM_AGENT_MODEL=slurm-agent
export LLM_PROVIDER=openai
export STREAM_TIMEOUT=300
cd $ROOT/agent
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 > $ROOT/agent_ft.log 2>&1 &
cd $ROOT
sleep 10
curl -s http://localhost:8000/health > /dev/null && echo "  Agent ✓" || { tail -20 $ROOT/agent_ft.log; exit 1; }

# ── 4. Eval (276 passed cases) ──
echo "[4/4] Running eval on 276 base-passed cases..."
nohup python -u $ROOT/evaluation/scenario_eval.py \
  --main-provider openai --main-model slurm-agent \
  --test-ids-file $ROOT/evaluation/base_union_passed_ids.json \
  --workers 1 > $ROOT/eval_ft_passed.log 2>&1 &
echo "  PID: $! — tail -f $ROOT/eval_ft_passed.log"
