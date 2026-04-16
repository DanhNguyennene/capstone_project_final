#!/bin/bash
# run_eval.sh — start MCP server + run the evaluation suite
#
# Usage:
#   ./run_eval.sh                      # 100-test real-slurm eval (default)
#   ./run_eval.sh --quick              # 1 test per category (10 total), fast sanity check
#   ./run_eval.sh --filter basic_read  # only tests matching a category or id
#   ./run_eval.sh --suite agent        # evaluate_agent.py (LLM-as-judge, structured scoring)
#   ./run_eval.sh --model qwen3.5:27b  # override model (default: qwen3.5:9b)
#   ./run_eval.sh --no-mock            # real Slurm (skips mock MCP startup)
#
# Models that support tool calling (safe choices):
#   qwen3.5:9b  qwen3.5:27b  qwen2.5:7b  gpt-oss:20b

# cd slurm-agent

# # Full 100-test run (starts mock MCP automatically, uses qwen3.5:9b)
# ./run_eval.sh

# # Quick sanity check — 1 test per category (10 tests)
# ./run_eval.sh --quick

# # Only one category or one test
# ./run_eval.sh --filter basic_read
# ./run_eval.sh --filter read_01

# # Use a bigger model
# ./run_eval.sh --model qwen3.5:27b

# # LLM-as-judge scoring (starts agent server too)
# ./run_eval.sh --suite agent

# # Already have MCP+Slurm running externally
# ./run_eval.sh --no-mock
# Do NOT use: deepseek-r1:*  (no tool support → 400 error)

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
EVAL="$ROOT/evaluation"

# ── colours ───────────────────────────────────────────────────────────────────
GRN='\033[0;32m'; YEL='\033[1;33m'; RED='\033[0;31m'; BLU='\033[0;34m'; NC='\033[0m'
info() { echo -e "${BLU}[eval]${NC} $*"; }
ok()   { echo -e "${GRN}[eval]${NC} $*"; }
warn() { echo -e "${YEL}[eval]${NC} $*"; }
die()  { echo -e "${RED}[eval]${NC} $*" >&2; exit 1; }

# ── defaults ──────────────────────────────────────────────────────────────────
MODEL="${SLURM_AGENT_MODEL:-gpt-oss:20b}"
MCP_PORT="${MCP_PORT:-3002}"
MCP_URL="http://localhost:$MCP_PORT"
AGENT_PORT="${AGENT_PORT:-8000}"
SUITE="real"        # real | agent
MODE="full"         # full | quick
FILTER=""
START_MOCK=1        # 1 = start mock MCP server; 0 = assume real Slurm already running
MCP_PID=""
AGENT_PID=""

# ── parse args ────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --quick)       MODE="quick" ;;
    --filter)      FILTER="$2"; shift ;;
    --model)       MODEL="$2";  shift ;;
    --suite)       SUITE="$2";  shift ;;   # real | agent
    --no-mock)     START_MOCK=0 ;;
    --mcp-url)     MCP_URL="$2"; START_MOCK=0; shift ;;
    -h|--help)
      sed -n '2,20p' "$0" | sed 's/^# \?//'
      exit 0 ;;
    *) die "Unknown argument: $1  (use --help)" ;;
  esac
  shift
done

# ── validate model ─────────────────────────────────────────────────────────────
if echo "$MODEL" | grep -qi "deepseek-r1"; then
  die "deepseek-r1 does not support tool calling — use qwen3.5:9b or qwen3.5:27b instead."
fi
export SLURM_AGENT_MODEL="$MODEL"

# ── cleanup on exit ────────────────────────────────────────────────────────────
cleanup() {
  echo ""
  warn "Shutting down background services…"
  [[ -n "$AGENT_PID" ]] && kill "$AGENT_PID" 2>/dev/null || true
  [[ -n "$MCP_PID"   ]] && kill "$MCP_PID"   2>/dev/null || true
  wait 2>/dev/null
  ok "Done."
}
trap cleanup EXIT INT TERM

# ── start mock MCP server ──────────────────────────────────────────────────────
if [[ $START_MOCK -eq 1 ]]; then
  # Kill anything already on the port
  fuser -k "${MCP_PORT}/tcp" 2>/dev/null || true
  sleep 0.3

  info "Starting mock MCP server on port $MCP_PORT (scenario=mixed)…"
  cd "$ROOT/mcp-server"
  python slurm_mcp_sse.py --mock mixed --port "$MCP_PORT" \
    > "$ROOT/evaluation/results/mcp_server.log" 2>&1 &
  MCP_PID=$!
  cd "$ROOT"

  # Wait up to 8 s for it to be ready
  for i in $(seq 1 16); do
    sleep 0.5
    if curl -sf "$MCP_URL/sse" --max-time 1 -o /dev/null 2>/dev/null; then
      ok "MCP server ready at $MCP_URL"
      break
    fi
    if [[ $i -eq 16 ]]; then
      die "MCP server didn't come up in 8s — check evaluation/results/mcp_server.log"
    fi
  done
fi

# ── optionally start agent server (needed for --suite agent) ──────────────────
if [[ "$SUITE" == "agent" ]]; then
  fuser -k "${AGENT_PORT}/tcp" 2>/dev/null || true
  sleep 0.3

  info "Starting agent server on port $AGENT_PORT…"
  cd "$ROOT/agent"
  MCP_SERVER_URL="$MCP_URL" \
    python -m uvicorn main:app --host 0.0.0.0 --port "$AGENT_PORT" \
    > "$ROOT/evaluation/results/agent_server.log" 2>&1 &
  AGENT_PID=$!
  cd "$ROOT"

  for i in $(seq 1 20); do
    sleep 0.5
    if curl -sf "http://localhost:$AGENT_PORT/health" -o /dev/null 2>/dev/null; then
      ok "Agent server ready at http://localhost:$AGENT_PORT"
      break
    fi
    if [[ $i -eq 20 ]]; then
      warn "Agent server health check timed out — continuing anyway"
    fi
  done
fi

# ── ensure results dir ─────────────────────────────────────────────────────────
mkdir -p "$EVAL/results"

# ── run the selected suite ─────────────────────────────────────────────────────
echo ""
info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
info "  Suite  : $SUITE"
info "  Model  : $MODEL"
info "  MCP    : $MCP_URL"
info "  Mode   : $MODE"
[[ -n "$FILTER" ]] && info "  Filter : $FILTER"
info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$ROOT"

if [[ "$SUITE" == "real" ]]; then
  # ── run_real_slurm_eval.py — 100 complex tests from test_cases_real_slurm.py ──
  ARGS=(
    python evaluation/run_real_slurm_eval.py
    --mcp-url "$MCP_URL"
    --model   "$MODEL"
    --mode    "$MODE"
    --auto-approve
  )
  [[ -n "$FILTER" ]] && ARGS+=(--filter "$FILTER")
  "${ARGS[@]}"

elif [[ "$SUITE" == "agent" ]]; then
  # ── evaluate_agent.py — LLM-as-judge scoring ──────────────────────────────
  EVMODE="normal"
  [[ "$MODE" == "quick" ]] && EVMODE="short"
  ARGS=(
    python evaluation/evaluate_agent.py
    --mcp-url "$MCP_URL"
    --mode    "$EVMODE"
  )
  [[ -n "$FILTER" ]] && ARGS+=(--filter "$FILTER")
  "${ARGS[@]}"

else
  die "Unknown --suite '$SUITE'. Use: real | agent"
fi
