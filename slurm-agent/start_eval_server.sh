#!/bin/bash
# start_eval_server.sh — run evaluation backend standalone
#
# Usage:
#   ./start_eval_server.sh                     # foreground (default)
#   ./start_eval_server.sh --screen            # detached screen mode
#   ./start_eval_server.sh --screen-status     # check detached status
#   ./start_eval_server.sh --screen-attach     # attach to screen session
#   ./start_eval_server.sh --screen-stop       # stop detached screen session
#
# Options:
#   --host 0.0.0.0
#   --port 8080
#   --python python3
#   --screen-name eval-server
#   --screen-log logs/eval_server_screen.log

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
EVAL_DIR="$ROOT/evaluation"

GRN='\033[0;32m'; YEL='\033[1;33m'; RED='\033[0;31m'; BLU='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${BLU}[eval-server]${NC} $*"; }
ok()    { echo -e "${GRN}[eval-server]${NC} $*"; }
warn()  { echo -e "${YEL}[eval-server]${NC} $*"; }
die()   { echo -e "${RED}[eval-server]${NC} $*" >&2; exit 1; }

HOST="0.0.0.0"
PORT="8080"
PYTHON="${PYTHON:-python3}"
SCREEN_MODE=0
SCREEN_STATUS=0
SCREEN_ATTACH=0
SCREEN_STOP=0
SCREEN_NAME="${SCREEN_NAME:-eval-server}"
SCREEN_LOG="${SCREEN_LOG:-$ROOT/logs/eval_server_screen.log}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)
      HOST="$2"; shift 2 ;;
    --port)
      PORT="$2"; shift 2 ;;
    --python)
      PYTHON="$2"; shift 2 ;;
    --screen)
      SCREEN_MODE=1; shift ;;
    --screen-status)
      SCREEN_STATUS=1; shift ;;
    --screen-attach)
      SCREEN_ATTACH=1; shift ;;
    --screen-stop)
      SCREEN_STOP=1; shift ;;
    --screen-name)
      SCREEN_NAME="$2"; shift 2 ;;
    --screen-log)
      SCREEN_LOG="$2"; shift 2 ;;
    -h|--help)
      cat <<'EOF'
start_eval_server.sh — run evaluation backend standalone

Usage:
  ./start_eval_server.sh                     # foreground (default)
  ./start_eval_server.sh --screen            # detached screen mode
  ./start_eval_server.sh --screen-status     # check detached status
  ./start_eval_server.sh --screen-attach     # attach to screen session
  ./start_eval_server.sh --screen-stop       # stop detached screen session

Options:
  --host 0.0.0.0
  --port 8080
  --python python3
  --screen-name eval-server
  --screen-log logs/eval_server_screen.log
EOF
      exit 0 ;;
    *)
      die "Unknown argument: $1" ;;
  esac
done

if [[ $SCREEN_MODE -eq 1 || $SCREEN_STATUS -eq 1 || $SCREEN_ATTACH -eq 1 || $SCREEN_STOP -eq 1 ]]; then
  command -v screen >/dev/null 2>&1 || die "'screen' is not installed."
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

run_eval_server() {
  command -v "$PYTHON" >/dev/null 2>&1 || die "python executable not found: $PYTHON"
  "$PYTHON" -c "import fastapi, uvicorn" >/dev/null 2>&1 \
    || die "Missing deps. Install: pip install fastapi uvicorn"

  cd "$EVAL_DIR"
  info "Starting eval server at http://$HOST:$PORT"
  exec "$PYTHON" eval_server.py --host "$HOST" --port "$PORT"
}

if [[ $SCREEN_MODE -eq 1 ]]; then
  mkdir -p "$(dirname "$SCREEN_LOG")"
  if screen -list | grep -q "[.]${SCREEN_NAME}[[:space:]]"; then
    die "screen session '${SCREEN_NAME}' is already running"
  fi

  info "Starting detached screen session '${SCREEN_NAME}'..."
  screen -dmS "$SCREEN_NAME" bash -lc "cd $(printf '%q' "$ROOT") && $(printf '%q' "$ROOT/start_eval_server.sh") --host $(printf '%q' "$HOST") --port $(printf '%q' "$PORT") --python $(printf '%q' "$PYTHON") >> $(printf '%q' "$SCREEN_LOG") 2>&1"
  ok "Started eval server in detached screen"
  echo "  status: ./start_eval_server.sh --screen-status"
  echo "  attach: ./start_eval_server.sh --screen-attach"
  echo "  stop:   ./start_eval_server.sh --screen-stop"
  echo "  logs:   tail -f $SCREEN_LOG"
  exit 0
fi

run_eval_server
