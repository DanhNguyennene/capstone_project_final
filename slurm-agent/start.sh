#!/bin/bash
# start.sh — build frontend (if needed) then launch all services
# Usage:
#   ./start.sh              — auto-rebuild when src/ is newer than dist/
#   ./start.sh --rebuild    — force a clean rebuild
#   ./start.sh --no-rebuild — skip build check entirely
#   ./start.sh --screen     — run detached in screen session (survives logout)
#   ./start.sh --screen-status | --screen-attach | --screen-stop
#
# Service ports (override via env):
#   MCP_PORT=3002  AGENT_PORT=8000  FRONTEND_PORT=4173
#   MCP_SCENARIO=healthy   (healthy | failed | pending | mixed | debug_needed)
#
#   --real   — connect to the real Slurm daemons instead of mock data

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

# ── Colours ────────────────────────────────────────────────────────────────────
GRN='\033[0;32m'; YEL='\033[1;33m'; RED='\033[0;31m'; BLU='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${BLU}[start]${NC} $*"; }
ok()    { echo -e "${GRN}[start]${NC} $*"; }
warn()  { echo -e "${YEL}[start]${NC} $*"; }
die()   { echo -e "${RED}[start]${NC} $*" >&2; exit 1; }

# ── Config ─────────────────────────────────────────────────────────────────────
MCP_PORT="${MCP_PORT:-3002}"
AGENT_PORT="${AGENT_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-4173}"
MCP_SCENARIO="${MCP_SCENARIO:-healthy}"

FORCE_REBUILD=0
SKIP_REBUILD=0
REAL_SLURM=0
SCREEN_MODE=0
SCREEN_STATUS=0
SCREEN_ATTACH=0
SCREEN_STOP=0
SCREEN_NAME="${SCREEN_NAME:-slurm-agent-stack}"
SCREEN_LOG="${SCREEN_LOG:-$ROOT/logs/screen-stack.log}"
FORWARD_ARGS=()
for arg in "$@"; do
  case "$arg" in
    --rebuild)        FORCE_REBUILD=1; FORWARD_ARGS+=("$arg") ;;
    --no-rebuild)     SKIP_REBUILD=1;  FORWARD_ARGS+=("$arg") ;;
    --real)           REAL_SLURM=1;    FORWARD_ARGS+=("$arg") ;;
    --screen)         SCREEN_MODE=1 ;;
    --screen-status)  SCREEN_STATUS=1 ;;
    --screen-attach)  SCREEN_ATTACH=1 ;;
    --screen-stop)    SCREEN_STOP=1 ;;
    --screen-name=*)  SCREEN_NAME="${arg#*=}" ;;
    --screen-log=*)   SCREEN_LOG="${arg#*=}" ;;
    *)                FORWARD_ARGS+=("$arg") ;;
  esac
done

# ── Detached screen controls ──────────────────────────────────────────────────
if [[ $SCREEN_STATUS -eq 1 || $SCREEN_ATTACH -eq 1 || $SCREEN_STOP -eq 1 || $SCREEN_MODE -eq 1 ]]; then
  command -v screen >/dev/null 2>&1 || die "'screen' is not installed. Install it first (e.g. apt install screen)."
fi

if [[ $SCREEN_STATUS -eq 1 ]]; then
  if screen -list | grep -q "[.]${SCREEN_NAME}[[:space:]]"; then
    ok "screen session '${SCREEN_NAME}' is running"
    [[ -f "$SCREEN_LOG" ]] && tail -n 20 "$SCREEN_LOG"
  else
    warn "screen session '${SCREEN_NAME}' is not running"
  fi
  exit 0
fi

if [[ $SCREEN_ATTACH -eq 1 ]]; then
  exec screen -r "$SCREEN_NAME"
fi

if [[ $SCREEN_STOP -eq 1 ]]; then
  if screen -list | grep -q "[.]${SCREEN_NAME}[[:space:]]"; then
    screen -S "$SCREEN_NAME" -X quit || true
    ok "stopped screen session '${SCREEN_NAME}'"
  else
    warn "screen session '${SCREEN_NAME}' is not running"
  fi
  exit 0
fi

if [[ $SCREEN_MODE -eq 1 ]]; then
  mkdir -p "$(dirname "$SCREEN_LOG")"
  if screen -list | grep -q "[.]${SCREEN_NAME}[[:space:]]"; then
    die "screen session '${SCREEN_NAME}' is already running. Use --screen-status or --screen-stop first."
  fi

  # Relaunch this script in foreground mode inside detached screen.
  cmd=("$ROOT/start.sh" "${FORWARD_ARGS[@]}")
  qcmd=""
  for token in "${cmd[@]}"; do
    qcmd+="$(printf '%q' "$token") "
  done

  info "Starting detached screen session '${SCREEN_NAME}'…"
  screen -dmS "$SCREEN_NAME" bash -lc "cd $(printf '%q' "$ROOT") && ${qcmd} >> $(printf '%q' "$SCREEN_LOG") 2>&1"
  ok "Started in screen."
  echo "  status: ./start.sh --screen-status"
  echo "  attach: ./start.sh --screen-attach"
  echo "  stop:   ./start.sh --screen-stop"
  echo "  logs:   tail -f $SCREEN_LOG"
  exit 0
fi

# ── 1. Frontend build ──────────────────────────────────────────────────────────
FE_DIR="$ROOT/frontend"
DIST_DIR="$FE_DIR/dist"

needs_build() {
  # Rebuild if dist/ missing, or if any src file is newer than dist/index.html
  [[ ! -d "$DIST_DIR" ]] && return 0
  [[ ! -f "$DIST_DIR/index.html" ]] && return 0
  if find "$FE_DIR/src" "$FE_DIR/index.html" "$FE_DIR/vite.config*" \
          -newer "$DIST_DIR/index.html" 2>/dev/null | grep -q .; then
    return 0
  fi
  return 1
}

# ── 1a. Ensure node_modules is always present ─────────────────────────────────
cd "$FE_DIR"
if [[ ! -f node_modules/.bin/vite ]]; then
  info "node_modules not found — running npm install…"
  npm install
  ok "npm install complete"
elif [[ package.json -nt node_modules/.bin/vite ]]; then
  info "package.json changed — running npm install…"
  npm install
  ok "npm install complete"
else
  ok "node_modules up-to-date"
fi
cd "$ROOT"

if [[ $SKIP_REBUILD -eq 0 ]]; then
  if [[ $FORCE_REBUILD -eq 1 ]] || needs_build; then
    info "Building frontend…"
    cd "$FE_DIR"
    npm run build
    ok "Frontend built → $DIST_DIR"
    cd "$ROOT"
  else
    ok "Frontend up-to-date, skipping build  (use --rebuild to force)"
  fi
fi

# ── 2. Verify Python env ───────────────────────────────────────────────────────
PYTHON="${PYTHON:-python}"
$PYTHON -c "import agents, fastapi, uvicorn, httpx" 2>/dev/null \
  || die "Missing Python dependencies. Run: pip install -r agent/requirements.txt"

# ── 3. PIDs for cleanup ────────────────────────────────────────────────────────
PIDS=()
cleanup() {
  echo ""
  warn "Shutting down…"
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null
  ok "All services stopped."
}
trap cleanup EXIT INT TERM

# ── 4. Start MCP server ────────────────────────────────────────────────────────
if [[ $REAL_SLURM -eq 1 ]]; then
  info "Starting MCP server on port $MCP_PORT (REAL Slurm — no mock)…"
  cd "$ROOT/mcp-server"
  $PYTHON slurm_mcp_sse.py --real --port "$MCP_PORT" &
else
  info "Starting MCP server on port $MCP_PORT (scenario=$MCP_SCENARIO)…"
  cd "$ROOT/mcp-server"
  $PYTHON slurm_mcp_sse.py --mock "$MCP_SCENARIO" --port "$MCP_PORT" &
fi
PIDS+=($!)
cd "$ROOT"

# ── 5. Start Agent API ─────────────────────────────────────────────────────────
info "Starting Agent API on port $AGENT_PORT…"
cd "$ROOT/agent"
MCP_SERVER_URL="http://localhost:$MCP_PORT" \
  $PYTHON -m uvicorn main:app --host 0.0.0.0 --port "$AGENT_PORT" --reload &
PIDS+=($!)
cd "$ROOT"

# ── 6. Serve built frontend ────────────────────────────────────────────────────
if [[ -d "$DIST_DIR" ]]; then
  info "Serving frontend on port $FRONTEND_PORT…"
  cd "$FE_DIR"
  # Use npm run preview so vite is resolved from node_modules/.bin, not PATH
  npm run preview -- --host 0.0.0.0 --port "$FRONTEND_PORT" &
  PIDS+=($!)
  cd "$ROOT"
fi

# ── 7. Ready banner ────────────────────────────────────────────────────────────
sleep 1
echo ""
ok "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ok "  MCP server  → http://localhost:${MCP_PORT}"
ok "  Agent API   → http://localhost:${AGENT_PORT}"
[[ -d "$DIST_DIR" ]] && \
ok "  Frontend    → http://localhost:${FRONTEND_PORT}"
ok "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

wait
