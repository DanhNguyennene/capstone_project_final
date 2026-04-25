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
KEY_FILE="$ROOT/.key"
KEY_FILE_ALT="$ROOT/slurm-agent/.key"
ENV_FILE="$ROOT/.env"
ENV_FILE_ALT="$ROOT/slurm-agent/.env"

# ── Colours ────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

log()  { echo -e "${CYAN}[start]${NC} $*"; }
ok()   { echo -e "${GREEN}  ✓${NC} $*"; }
warn() { echo -e "${YELLOW}  !${NC} $*"; }
die()  { echo -e "${RED}  ✗ $*${NC}"; exit 1; }

# ── Optional local key bootstrap (.key/.env are gitignored) ───────
trim_ws() {
  local s="$1"
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s' "$s"
}

load_env_like_file() {
  local file="$1"
  [[ -f "$file" ]] || return 1

  local raw line key value loaded=0
  while IFS= read -r raw || [[ -n "$raw" ]]; do
    line="$(trim_ws "$raw")"
    [[ -z "$line" || "$line" == \#* ]] && continue

    if [[ "$line" == export\ * ]]; then
      line="${line#export }"
    fi

    if [[ "$line" == *=* ]]; then
      key="$(trim_ws "${line%%=*}")"
      value="$(trim_ws "${line#*=}")"

      if [[ ( "$value" == \"*\" && "$value" == *\" ) || ( "$value" == \'*\' && "$value" == *\' ) ]]; then
        value="${value:1:${#value}-2}"
      fi

      case "$key" in
        OPEN_AI_KEY)
          export OPENAI_API_KEY="$value"
          loaded=1
          ;;
        GH_TOKEN|GH_PAT|GITHUB_PAT)
          export GITHUB_TOKEN="$value"
          loaded=1
          ;;
        *)
          if [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
            export "$key=$value"
            loaded=1
          else
            warn "Skipping invalid key name in $(basename "$file"): $key"
          fi
          ;;
      esac
      continue
    fi

    if [[ "$line" == sk-* ]]; then
      export OPENAI_API_KEY="$line"
      loaded=1
    elif [[ "$line" == ghp_* || "$line" == github_pat_* || "$line" == gho_* || "$line" == ghu_* || "$line" == ghs_* ]]; then
      export GITHUB_TOKEN="$line"
      loaded=1
    fi
  done < "$file"

  [[ $loaded -eq 1 ]] && ok "Loaded local secrets from: $file"
  return 0
}

for f in "$KEY_FILE" "$KEY_FILE_ALT" "$ENV_FILE" "$ENV_FILE_ALT"; do
  load_env_like_file "$f" || true
done

if [[ -z "${OPENAI_API_KEY:-}" && -n "${OPEN_AI_KEY:-}" ]]; then
  export OPENAI_API_KEY="$OPEN_AI_KEY"
fi

if [[ -z "${GITHUB_TOKEN:-}" && -n "${GH_TOKEN:-}" ]]; then
  export GITHUB_TOKEN="$GH_TOKEN"
fi

if [[ -n "${OPENAI_API_KEY:-}" && -z "${LLM_PROVIDER:-}" ]]; then
  export LLM_PROVIDER="openai"
  export OPENAI_MODEL="${OPENAI_MODEL:-gpt-4o-mini}"
  ok "Detected OPENAI_API_KEY; defaulting LLM_PROVIDER=openai"
fi

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
