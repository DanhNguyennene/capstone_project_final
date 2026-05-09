#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  Run FT Qwen2.5-14B Eval on 615 Test Split
#  Downloads adapter from HF → Starts MCP → Model Server → Agent → Eval
#
#  Usage:
#    bash run_ft_eval.sh                    # all 615 test cases
#    bash run_ft_eval.sh --failed-only      # only 167 base-failed cases
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

cd /workspace/capstone_project/slurm-agent

FAILED_ONLY=false
if [[ "${1:-}" == "--failed-only" ]]; then
  FAILED_ONLY=true
fi

echo "Killing any existing processes..."
pkill -9 -f slurm_mcp_sse.py 2>/dev/null || true
pkill -9 -f 'main:app' 2>/dev/null || true
pkill -9 -f serve_ft_model 2>/dev/null || true
sleep 3

# ── 0. Download adapter from HF ──
ADAPTER_DIR="training/out/ft_v4_adapter"
if [ ! -f "$ADAPTER_DIR/adapter_model.safetensors" ]; then
  echo "[0/4] Downloading adapter from HuggingFace..."
  pip install huggingface_hub -q
  huggingface-cli download DanhVuiVe/slurm-agent-qwen14b-lora-v4 \
    --local-dir $ADAPTER_DIR
  echo "  Downloaded to $ADAPTER_DIR"
else
  echo "[0/4] Adapter already present at $ADAPTER_DIR"
fi

# ── 1. MCP Server ──
echo ""
echo "[1/4] Starting MCP server on :3002..."
python mcp-server/slurm_mcp_sse.py > mcp.log 2>&1 &
MCP_PID=$!
echo "  PID: $MCP_PID"
sleep 5

if ss -tlnp | grep -q ':3002'; then
  echo "  MCP: listening on :3002 ✓"
else
  echo "  MCP FAILED. Log:"
  cat mcp.log
  exit 1
fi

# ── 2. FT Model Server ──
echo ""
echo "[2/4] Starting FT Qwen2.5-14B model server on :9000..."
echo "  (This takes ~2-3 min to load weights + adapter)"
export OPENAI_AGENTS_DISABLE_TRACING=1
python evaluation/serve_ft_model.py \
  --adapter $ADAPTER_DIR \
  --port 9000 \
  --no-4bit \
  --max-new-tokens 2048 \
  > serve_ft.log 2>&1 &
MODEL_PID=$!
echo "  PID: $MODEL_PID"

# Wait for model to load
for i in $(seq 1 60); do
  if curl -s http://localhost:9000/health > /dev/null 2>&1; then
    echo "  Model server: READY ✓ (${i}0s)"
    break
  fi
  if ! kill -0 $MODEL_PID 2>/dev/null; then
    echo "  Model server CRASHED. Log:"
    tail -30 serve_ft.log
    exit 1
  fi
  sleep 10
done

if ! curl -s http://localhost:9000/health > /dev/null 2>&1; then
  echo "  Model server did not start in 10 min. Log:"
  tail -30 serve_ft.log
  exit 1
fi

# ── 3. Agent ──
echo ""
echo "[3/4] Starting agent on :8000..."
export OPENAI_BASE_URL=http://localhost:9000/v1
export OPENAI_API_KEY=dummy
export SLURM_AGENT_MODEL=slurm-agent
export STREAM_TIMEOUT=300
export OPENAI_AGENTS_DISABLE_TRACING=1

cd agent
python -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../agent_ft.log 2>&1 &
AGENT_PID=$!
cd ..
echo "  PID: $AGENT_PID"
sleep 10

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
  echo "  Agent: READY ✓"
else
  echo "  Agent FAILED. Log:"
  tail -30 agent_ft.log
  exit 1
fi

# ── 4. Run Eval ──
echo ""
if [ "$FAILED_ONLY" = true ]; then
  TEST_FILE="evaluation/base_failed_ids.json"
  echo "[4/4] Running eval on 167 base-failed cases..."
else
  TEST_FILE="evaluation/split_test_ids.json"
  echo "[4/4] Running eval on 615 test cases..."
fi
echo "  PIDs: MCP=$MCP_PID, Model=$MODEL_PID, Agent=$AGENT_PID"
echo ""

python evaluation/scenario_eval.py \
  --main-provider openai \
  --main-model slurm-agent \
  --test-ids-file $TEST_FILE \
  --workers 2

echo ""
echo "══════════════════════════════════════════"
echo "  FT model eval complete!"
echo "  Results: evaluation/results/"
echo "══════════════════════════════════════════"
