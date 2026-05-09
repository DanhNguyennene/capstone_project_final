#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  Run Base Qwen2.5-14B Eval on 615 Test Split
#  Starts MCP → Model Server → Agent → Eval (sequential)
#
#  Usage:
#    bash run_base_eval.sh
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

cd /workspace/capstone_project/slurm-agent

echo "Killing any existing processes..."
pkill -9 -f slurm_mcp_sse.py 2>/dev/null || true
pkill -9 -f 'main:app' 2>/dev/null || true
pkill -9 -f serve_ft_model 2>/dev/null || true
sleep 3

# ── 1. MCP Server ──
echo ""
echo "[1/4] Starting MCP server on :3002..."
nohup python mcp-server/slurm_mcp_sse.py > mcp.log 2>&1 &
MCP_PID=$!
echo "  PID: $MCP_PID"
sleep 5

# Verify MCP (it may not have /health, just check port)
if ss -tlnp | grep -q ':3002'; then
  echo "  MCP: listening on :3002 ✓"
else
  echo "  MCP FAILED. Log:"
  cat mcp.log
  exit 1
fi

# ── 2. Base Model Server ──
echo ""
echo "[2/4] Starting base Qwen2.5-14B model server on :9000..."
echo "  (This takes ~2 min to load weights)"
export OPENAI_AGENTS_DISABLE_TRACING=1
nohup python evaluation/serve_ft_model.py \
  --no-adapter \
  --port 9000 \
  --max-new-tokens 2048 \
  > serve_base.log 2>&1 &
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
    tail -30 serve_base.log
    exit 1
  fi
  sleep 10
done

if ! curl -s http://localhost:9000/health > /dev/null 2>&1; then
  echo "  Model server did not start in 10 min. Log:"
  tail -30 serve_base.log
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
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../agent_base.log 2>&1 &
AGENT_PID=$!
cd ..
echo "  PID: $AGENT_PID"
sleep 10

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
  echo "  Agent: READY ✓"
else
  echo "  Agent FAILED. Log:"
  tail -30 agent_base.log
  exit 1
fi

# ── 4. Run Eval ──
echo ""
echo "[4/4] Running eval on 615 test cases (workers=1)..."
echo "  This will take several hours. Output goes to eval results dir."
echo "  PIDs: MCP=$MCP_PID, Model=$MODEL_PID, Agent=$AGENT_PID"
echo ""

python evaluation/scenario_eval.py \
  --main-provider openai \
  --main-model slurm-agent \
  --test-ids-file evaluation/split_test_ids.json \
  --workers 1

echo ""
echo "══════════════════════════════════════════"
echo "  Base model eval complete!"
echo "  Results: evaluation/results/"
echo "══════════════════════════════════════════"
