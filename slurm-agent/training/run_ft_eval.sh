#!/bin/bash
# run_ft_eval.sh — Deploy fine-tuned model + run full eval benchmark
#
# This script:
#   1. Clones repo (or pulls latest) with adapter weights
#   2. Installs deps
#   3. Starts the FT model server (transformers + PEFT, full precision)
#   4. Starts the agent backend pointing at the FT model
#   5. Starts the mock MCP server
#   6. Runs eval against dataset.json (3135 cases)
#
# Usage:
#   bash run_ft_eval.sh                    # full 3135-case eval
#   bash run_ft_eval.sh --quick            # 20-case sample
#   bash run_ft_eval.sh --filter docs      # category filter
#
# Requirements: NVIDIA GPU with >=30GB VRAM (A40/A100), CUDA 12.x

set -e

# ── Config ────────────────────────────────────────────────────────────────────
WORK_DIR="${WORK_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
PROJECT_DIR="$WORK_DIR"
VENV_DIR="$PROJECT_DIR/.venv"

MODEL_PORT=8081
AGENT_PORT=20000
MCP_PORT=3002

BASE_MODEL="Qwen/Qwen2.5-14B-Instruct"
ADAPTER_PATH="$PROJECT_DIR/slurm-agent/training/out/slurm-agent-14b-lora"

# Eval config
EVAL_ARGS=""
MODE="full"
QUANTIZED=0

# ── Parse args ────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --quick)    MODE="quick" ;;
    --quantized) QUANTIZED=1 ;;
    --filter)   EVAL_ARGS="$EVAL_ARGS --filter $2"; shift ;;
    --judge)    EVAL_ARGS="$EVAL_ARGS --judge" ;;
    *)          echo "Unknown arg: $1"; exit 1 ;;
  esac
  shift
done

# ── Colours ───────────────────────────────────────────────────────────────────
GRN='\033[0;32m'; YEL='\033[1;33m'; RED='\033[0;31m'; BLU='\033[0;34m'; NC='\033[0m'
info() { echo -e "${BLU}[ft-eval]${NC} $*"; }
ok()   { echo -e "${GRN}[ft-eval]${NC} $*"; }
warn() { echo -e "${YEL}[ft-eval]${NC} $*"; }
die()  { echo -e "${RED}[ft-eval]${NC} $*" >&2; exit 1; }

# ── Cleanup ───────────────────────────────────────────────────────────────────
MODEL_PID="" ; AGENT_PID="" ; MCP_PID=""
cleanup() {
  warn "Shutting down..."
  [[ -n "$MODEL_PID" ]] && kill "$MODEL_PID" 2>/dev/null || true
  [[ -n "$AGENT_PID" ]] && kill "$AGENT_PID" 2>/dev/null || true
  [[ -n "$MCP_PID"   ]] && kill "$MCP_PID"   2>/dev/null || true
  wait 2>/dev/null
  ok "Done."
}
trap cleanup EXIT INT TERM

# ── 1. Ensure we're in the right place ────────────────────────────────────────
cd "$PROJECT_DIR/slurm-agent"

# ── Kill any stale processes from previous runs ──────────────────────────────
for port in $MODEL_PORT $AGENT_PORT $MCP_PORT; do
  fuser -k "${port}/tcp" 2>/dev/null || true
done
sleep 1

# ── Strip runpod proxy env (forces localhost calls through nginx → 405) ─────
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy
export NO_PROXY="localhost,127.0.0.1,::1,0.0.0.0"
export no_proxy="localhost,127.0.0.1,::1,0.0.0.0"
info "Proxy env after cleanup:"
env | grep -iE 'proxy' || echo "  (none)"

# # ── 2. Setup venv + deps ─────────────────────────────────────────────────────
# if [[ ! -d "$VENV_DIR" ]]; then
#   info "Creating virtualenv..."
#   python3 -m venv "$VENV_DIR"
# fi
# source "$VENV_DIR/bin/activate"

# info "Installing dependencies..."
# pip install -q --upgrade pip
# pip install -q \
#   torch --index-url https://download.pytorch.org/whl/cu124
# pip install -q \
#   transformers>=4.46.0 \
#   peft>=0.13.0 \
#   accelerate>=0.34.0 \
#   bitsandbytes>=0.43.0 \
#   fastapi \
#   uvicorn \
#   httpx \
#   aiohttp

# # Install agent deps
# if [[ -f "$PROJECT_DIR/slurm-agent/agent/requirements.txt" ]]; then
#   pip install -q -r "$PROJECT_DIR/slurm-agent/agent/requirements.txt"
# fi

# Try flash-attention (optional, falls back to sdpa)
pip install -q flash-attn --no-build-isolation 2>/dev/null || warn "flash-attn not installed, using sdpa"

# ── 3. Start FT Model Server ─────────────────────────────────────────────────
QUANT_FLAG=""
if [[ $QUANTIZED -eq 1 ]]; then
  QUANT_FLAG="--quantized"
  info "Starting fine-tuned model server (4-bit quantized) on port $MODEL_PORT..."
else
  info "Starting fine-tuned model server (full precision) on port $MODEL_PORT..."
fi
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
python "$PROJECT_DIR/slurm-agent/training/serve_ft_model.py" \
  --base-model "$BASE_MODEL" \
  --adapter "$ADAPTER_PATH" \
  --port "$MODEL_PORT" \
  $QUANT_FLAG \
  > >(tee "$PROJECT_DIR/slurm-agent/evaluation/results/ft_model_server.log") 2>&1 &
MODEL_PID=$!

# Wait for model to load (can take 2-3 min for 14B)
info "Waiting for model to load (this takes 2-3 min for 14B full precision)..."
for i in $(seq 1 120); do
  sleep 2
  if curl -sf "http://localhost:$MODEL_PORT/v1/models" -o /dev/null 2>/dev/null; then
    ok "FT model server ready at http://localhost:$MODEL_PORT"
    break
  fi
  if [[ $i -eq 120 ]]; then
    die "Model server didn't start in 4 min. Check: evaluation/results/ft_model_server.log"
  fi
done

# ── 4. Start Mock MCP Server ─────────────────────────────────────────────────
info "Starting mock MCP server on port $MCP_PORT..."
fuser -k "${MCP_PORT}/tcp" 2>/dev/null || true
sleep 0.3
cd "$PROJECT_DIR/slurm-agent/mcp-server"
python slurm_mcp_sse.py --mock mixed --port "$MCP_PORT" \
  > >(tee "$PROJECT_DIR/slurm-agent/evaluation/results/mcp_server.log") 2>&1 &
MCP_PID=$!
cd "$PROJECT_DIR/slurm-agent"

for i in $(seq 1 16); do
  sleep 0.5
  if python -c "import socket; s=socket.socket(); s.settimeout(0.5); s.connect(('127.0.0.1',$MCP_PORT)); s.close()" 2>/dev/null; then
    ok "MCP server ready at http://localhost:$MCP_PORT"
    break
  fi
  [[ $i -eq 16 ]] && die "MCP server didn't come up"
done

# ── 5. Start Agent Backend (pointing at FT model) ────────────────────────────
info "Starting agent backend on port $AGENT_PORT..."
export LLM_PROVIDER="openai"
export OPENAI_BASE_URL="http://127.0.0.1:$MODEL_PORT/v1"
export OPENAI_API_KEY="dummy"
export OPENAI_AGENTS_DISABLE_TRACING="1"
export SLURM_AGENT_MODEL="slurm-agent-ft"
export SLURM_AGENT_SPECIALIST_MODEL="slurm-agent-ft"
export MCP_SERVER_URL="http://localhost:$MCP_PORT"
export AUTO_APPROVE="true"

cd "$PROJECT_DIR/slurm-agent/agent"
python main.py \
  > >(tee "$PROJECT_DIR/slurm-agent/evaluation/results/agent_server.log") 2>&1 &
AGENT_PID=$!
cd "$PROJECT_DIR/slurm-agent"

for i in $(seq 1 30); do
  sleep 1
  if curl -sf "http://localhost:$AGENT_PORT/health" -o /dev/null 2>/dev/null; then
    ok "Agent backend ready at http://localhost:$AGENT_PORT"
    break
  fi
  [[ $i -eq 30 ]] && die "Agent didn't come up. Check: evaluation/results/agent_server.log"
done

# ── 6. Run Evaluation ────────────────────────────────────────────────────────
info "Running evaluation (mode=$MODE)..."
cd "$PROJECT_DIR/slurm-agent/evaluation"

export SLURM_AGENT_MODEL="slurm-agent-ft"
export LLM_PROVIDER="openai"

if [[ "$MODE" == "quick" ]]; then
  # 20-case sample
  python scenario_eval.py \
    --agent-url "http://localhost:$AGENT_PORT" \
    --mcp-url "http://localhost:$MCP_PORT" \
    --main-model "slurm-agent-ft" \
    --main-provider openai \
    --specialist-model "slurm-agent-ft" \
    --specialist-provider openai \
    --test-ids-file "$PROJECT_DIR/slurm-agent/evaluation/results/sample_50_ids.json" \
    --auto-approve \
    $EVAL_ARGS \
    2>&1 | tee "$PROJECT_DIR/slurm-agent/evaluation/results/eval_ft_full.log"
else
  # Full 3135-case eval
  python scenario_eval.py \
    --agent-url "http://localhost:$AGENT_PORT" \
    --mcp-url "http://localhost:$MCP_PORT" \
    --main-model "slurm-agent-ft" \
    --main-provider openai \
    --specialist-model "slurm-agent-ft" \
    --specialist-provider openai \
    --auto-approve \
    $EVAL_ARGS \
    2>&1 | tee "$PROJECT_DIR/slurm-agent/evaluation/results/eval_ft_full.log"
fi

ok "Evaluation complete! Results in: evaluation/results/"
ok "Compare vs GPT-5-mini baseline: eval_all_20260504_001747.json (96.1% pass rate)"
