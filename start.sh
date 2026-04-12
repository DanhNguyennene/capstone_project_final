#!/usr/bin/env bash
# start.sh — Start MCP server, Agent API, and Frontend in one go
# Usage:
#   ./start.sh                  # default: mixed scenario (mock)
#   ./start.sh --mock failed    # choose scenario: healthy|failed|pending|mixed|debug_needed
#   ./start.sh --real            # use real Slurm commands (requires slurmctld + slurmd)
#   ./start.sh --no-frontend    # skip npm dev server

set -e
SCENARIO="mixed"
FRONTEND=true
REAL_MODE=false

for arg in "$@"; do
  case $arg in
    --mock) shift; SCENARIO="$1"; shift ;;
    --mock=*) SCENARIO="${arg#*=}" ;;
    --real) REAL_MODE=true ;;
    --no-frontend) FRONTEND=false ;;
  esac
done

ROOT="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$ROOT/slurm-agent/agent"
MCP_DIR="$ROOT/slurm-agent/mcp-server"
FRONTEND_DIR="$ROOT/slurm-agent/frontend"

# ── Colours ────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

log()  { echo -e "${CYAN}[start]${NC} $*"; }
ok()   { echo -e "${GREEN}  ✓${NC} $*"; }
warn() { echo -e "${YELLOW}  !${NC} $*"; }
die()  { echo -e "${RED}  ✗ $*${NC}"; exit 1; }

# ── Kill stale processes on our ports ──────────────────────────────
for port in 3002 8000; do
  pid=$(lsof -ti :"$port" -sTCP:LISTEN 2>/dev/null || true)
  if [[ -n "$pid" ]]; then
    warn "Port $port in use (pid $pid) — killing"
    kill "$pid" 2>/dev/null; sleep 0.5
    kill -9 "$pid" 2>/dev/null || true
  fi
done

# ── Trap — kill background children on exit ────────────────────────
PIDS=()
cleanup() {
  echo ""
  log "Shutting down..."
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null && echo "  killed $pid"
  done
}
trap cleanup EXIT INT TERM

# ── Conda env ─────────────────────────────────────────────────────
if command -v conda &>/dev/null; then
  # shellcheck disable=SC1090
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda activate main 2>/dev/null || warn "conda env 'main' not found, using current python"
fi

PYTHON=$(command -v python || command -v python3 || die "python not found")
ok "Python: $($PYTHON --version)"

# ── 1. MCP Server ─────────────────────────────────────────────────
if $REAL_MODE; then
  log "Starting MCP server  (${BOLD}REAL Slurm${NC}, port 3002)..."
  MCP_ARGS="--real --port 3002"
else
  log "Starting MCP server  (scenario=${BOLD}${SCENARIO}${NC}, port 3002)..."
  MCP_ARGS="--mock $SCENARIO --port 3002"
fi
(
  cd "$MCP_DIR"
  $PYTHON slurm_mcp_sse.py $MCP_ARGS 2>&1 \
    | sed 's/^/  [mcp] /'
) &
PIDS+=($!)
sleep 2

# Quick health check
if curl -sf http://localhost:3002/sse -H "Accept: text/event-stream" \
    --max-time 2 -o /dev/null 2>/dev/null; then
  ok "MCP server  →  http://localhost:3002"
else
  warn "MCP server may still be starting..."
fi

# ── 2. Agent API ───────────────────────────────────────────────────
log "Starting Agent API   (port 8000)..."
(
  cd "$AGENT_DIR"
  $PYTHON -m uvicorn main:app --host 0.0.0.0 --port 8000 2>&1 \
    | sed 's/^/  [agent] /'
) &
PIDS+=($!)
sleep 2

if curl -sf http://localhost:8000/health -o /dev/null 2>/dev/null; then
  ok "Agent API   →  http://localhost:8000"
else
  warn "Agent API may still be starting..."
fi

# ── 3. Frontend ────────────────────────────────────────────────────
if $FRONTEND; then
  if ! command -v npm &>/dev/null; then
    warn "npm not found — skipping frontend"
  else
    log "Starting Frontend    (port 5173)..."
    (
      cd "$FRONTEND_DIR"
      npm run dev -- --host 2>&1 | sed 's/^/  [ui]    /'
    ) &
    PIDS+=($!)
    sleep 2
    ok "Frontend    →  http://localhost:5173"
  fi
fi

# ── Summary ────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}  Slurm Agent — running${NC}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
MODE_LABEL=$($REAL_MODE && echo "REAL Slurm" || echo "$SCENARIO")
echo -e "  MCP server  →  ${CYAN}http://localhost:3002${NC}  (${MODE_LABEL})"
echo -e "  Agent API   →  ${CYAN}http://localhost:8000${NC}"
$FRONTEND && echo -e "  Frontend    →  ${CYAN}http://localhost:5173${NC}"
echo ""
echo -e "  Press ${BOLD}Ctrl+C${NC} to stop everything."
echo ""

# ── Wait forever ──────────────────────────────────────────────────
wait
