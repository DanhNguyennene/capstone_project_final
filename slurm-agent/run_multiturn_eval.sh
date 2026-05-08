#!/bin/bash
# run_multiturn_eval.sh — Deploy adapter from HuggingFace & run multi-turn evaluation
#
# Prerequisites:
#   - A40 pod with ~46GB VRAM
#   - Python 3.10+, CUDA available
#   - Port 9000 (model server), 8000 (agent), 3002 (MCP)
#
# Usage:
#   chmod +x run_multiturn_eval.sh
#   ./run_multiturn_eval.sh              # full eval (default)
#   ./run_multiturn_eval.sh --quick      # 10-test sanity check
#   ./run_multiturn_eval.sh --workers 4  # parallel workers

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

GRN='\033[0;32m'; YEL='\033[1;33m'; RED='\033[0;31m'; BLU='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${BLU}[multiturn-eval]${NC} $*"; }
ok()    { echo -e "${GRN}[multiturn-eval]${NC} $*"; }
warn()  { echo -e "${YEL}[multiturn-eval]${NC} $*"; }
die()   { echo -e "${RED}[multiturn-eval]${NC} $*" >&2; exit 1; }

# ── Parse args ────────────────────────────────────────────────────────────────
QUICK=0
WORKERS=2
EXTRA_ARGS=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --quick)   QUICK=1; shift ;;
        --workers) WORKERS="$2"; shift 2 ;;
        *)         EXTRA_ARGS="$EXTRA_ARGS $1"; shift ;;
    esac
done

# ── Step 1: Install dependencies ─────────────────────────────────────────────
info "Installing dependencies..."
pip install -q torch transformers peft accelerate bitsandbytes \
    fastapi uvicorn huggingface_hub aiohttp openai

# ── Step 2: Download adapter from HuggingFace ────────────────────────────────
ADAPTER_DIR="$ROOT/training/out/slurm-agent-14b-lora-v2"
if [[ -d "$ADAPTER_DIR" && -f "$ADAPTER_DIR/adapter_model.safetensors" ]]; then
    ok "Adapter already present at $ADAPTER_DIR"
else
    info "Downloading adapter from HuggingFace..."
    mkdir -p "$ROOT/training/out"
    hf download DanhVuiVe/slurm-agent-14b-lora-v2 \
        --local-dir "$ADAPTER_DIR" \
        --repo-type model
    ok "Adapter downloaded to $ADAPTER_DIR"
fi

# ── Step 3: Start model server (port 9000, bf16 — no 4-bit for eval) ─────────
MODEL_PORT=9000
info "Starting model server on port $MODEL_PORT (bf16, no quantization)..."
python evaluation/serve_ft_model.py \
    --adapter "$ADAPTER_DIR" \
    --port $MODEL_PORT \
    --no-4bit &
MODEL_PID=$!

# Wait for model to be ready
info "Waiting for model server to load (this takes ~60-90s on A40)..."
for i in $(seq 1 120); do
    if curl -s "http://localhost:$MODEL_PORT/health" > /dev/null 2>&1; then
        ok "Model server ready!"
        break
    fi
    if ! kill -0 $MODEL_PID 2>/dev/null; then
        die "Model server crashed. Check logs above."
    fi
    sleep 2
done

if ! curl -s "http://localhost:$MODEL_PORT/health" > /dev/null 2>&1; then
    die "Model server did not become ready in 240s"
fi

# ── Step 4: Start MCP mock server (port 3002) ────────────────────────────────
info "Starting MCP mock server on port 3002..."
cd "$ROOT/mcp-server"
python slurm_mcp_sse.py --mock mixed --port 3002 &
MCP_PID=$!
cd "$ROOT"
sleep 3

for i in $(seq 1 10); do
    if curl -s "http://localhost:3002/health" > /dev/null 2>&1; then
        break
    fi
    sleep 1
done
ok "MCP server started (PID $MCP_PID)"

# ── Step 5: Start agent server (port 8000) ───────────────────────────────────
info "Starting agent server on port 8000..."
export LLM_PROVIDER=openai
export OPENAI_BASE_URL="http://localhost:$MODEL_PORT/v1"
export OPENAI_API_KEY=dummy
export SLURM_AGENT_MODEL=slurm-agent
export USE_TRAINING_TOOLS=1
export AGENT_AUTO_APPROVE=true
export MCP_SERVER_URL="http://localhost:3002"

cd "$ROOT/agent"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
AGENT_PID=$!
cd "$ROOT"
sleep 5

for i in $(seq 1 15); do
    if curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
        break
    fi
    sleep 2
done
ok "Agent server started (PID $AGENT_PID)"

# ── Step 6: Extract test IDs (multi-turn subset from v2 training data) ────────
info "Extracting v2 test IDs..."
if [[ -f "$ROOT/training/out/agent_sft_v2_ids.json" ]]; then
    python evaluation/extract_v2_test_ids.py
    TEST_IDS_ARG="--test-ids-file evaluation/v2_test_ids.json"
    ok "Using v2 test IDs (held-out from training)"
else
    warn "No v2_ids file found — running full dataset"
    TEST_IDS_ARG=""
fi

# ── Step 7: Run evaluation ───────────────────────────────────────────────────
info "Running multi-turn evaluation..."
echo ""
echo "=============================================="
echo "  MULTI-TURN EVAL — slurm-agent-14b-lora-v2"
echo "  Model: bf16 (no quant) on A40"
echo "  Workers: $WORKERS"
echo "=============================================="
echo ""

EVAL_CMD="python evaluation/scenario_eval.py \
    --auto-approve \
    --workers $WORKERS \
    --llm-provider openai \
    --main-model slurm-agent \
    $TEST_IDS_ARG \
    $EXTRA_ARGS"

if [[ $QUICK -eq 1 ]]; then
    info "Quick mode: subset per category"
    $EVAL_CMD --category read --no-variants
else
    $EVAL_CMD
fi

# ── Step 8: Print results summary ────────────────────────────────────────────
echo ""
ok "Evaluation complete!"
echo ""

LATEST_RESULT=$(ls -t evaluation/results/*.json 2>/dev/null | head -1)
if [[ -n "$LATEST_RESULT" ]]; then
    info "Latest results: $LATEST_RESULT"
    python -c "
import json, sys
r = json.load(open('$LATEST_RESULT'))
m = r.get('metrics', {})
print(f\"  BAR  (Behavioral Agreement Rate): {m.get('bar', 'N/A')}\")
print(f\"  SVR  (Safety Violation Rate):     {m.get('svr', 'N/A')}\")
print(f\"  CSR  (Cross-Scenario Robustness): {m.get('csr', 'N/A')}\")
print(f\"  Overall Score:                    {m.get('overall_score', m.get('mean_score', 'N/A'))}\")
print(f\"  Total Tests:                      {m.get('total', len(r.get('results', [])))}\")
print(f\"  Pass Rate:                        {m.get('pass_rate', 'N/A')}\")
"
fi

# ── Cleanup ──────────────────────────────────────────────────────────────────
info "Stopping services..."
kill $AGENT_PID 2>/dev/null || true
kill $MCP_PID 2>/dev/null || true
kill $MODEL_PID 2>/dev/null || true
ok "Done. Results saved to evaluation/results/"
