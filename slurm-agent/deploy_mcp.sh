#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# deploy_mcp.sh — Rapid-deploy the MCP server to a remote Slurm head node
#
# Usage:
#   ./deploy_mcp.sh user@headnode            # deploy + start (port 3002)
#   ./deploy_mcp.sh user@headnode 3005       # custom port
#   ./deploy_mcp.sh user@headnode 3002 mock  # mock mode (no real Slurm)
#
# What it does:
#   1. rsync the mcp-server/ directory to the remote host
#   2. Install Python dependencies (pip) if needed
#   3. Kill any existing MCP server on that port
#   4. Start the server in a detached tmux session
#
# Prerequisites on the remote:
#   - Python 3.11+
#   - pip
#   - tmux (for background session)
#   - Slurm CLI tools (squeue, sbatch, etc.) if running in --real mode
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Args ─────────────────────────────────────────────────────────────────────
REMOTE="${1:?Usage: $0 user@host [port] [mock|real]}"
PORT="${2:-3002}"
MODE="${3:-real}"   # "real" or "mock"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MCP_DIR="${SCRIPT_DIR}/mcp-server"
REMOTE_DIR="~/slurm-mcp-server"
TMUX_SESSION="slurm-mcp"

# Validate
if [[ ! -f "${MCP_DIR}/slurm_mcp_sse.py" ]]; then
    echo "ERROR: mcp-server/slurm_mcp_sse.py not found at ${MCP_DIR}" >&2
    exit 1
fi

if [[ "${MODE}" == "real" ]]; then
    MODE_FLAG="--real"
elif [[ "${MODE}" == "mock" ]]; then
    MODE_FLAG="--mock healthy"
else
    echo "ERROR: MODE must be 'real' or 'mock', got '${MODE}'" >&2
    exit 1
fi

echo "╔══════════════════════════════════════════════════════╗"
echo "║  MCP Server Deploy                                  ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Remote:  ${REMOTE}"
echo "║  Port:    ${PORT}"
echo "║  Mode:    ${MODE} (${MODE_FLAG})"
echo "║  Dir:     ${REMOTE_DIR}"
echo "╚══════════════════════════════════════════════════════╝"
echo

# ── Step 1: rsync files ─────────────────────────────────────────────────────
echo "[1/4] Syncing mcp-server/ → ${REMOTE}:${REMOTE_DIR}/"
rsync -avz --delete \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    "${MCP_DIR}/" "${REMOTE}:${REMOTE_DIR}/"
echo "  ✓ Files synced"

# ── Step 2: Install dependencies ────────────────────────────────────────────
echo "[2/4] Installing Python dependencies..."
ssh "${REMOTE}" bash -s <<'INSTALL_EOF'
cd ~/slurm-mcp-server
pip install --quiet --upgrade pip
pip install --quiet mcp uvicorn aiohttp matplotlib 2>&1 | tail -3
echo "  ✓ Dependencies installed"
INSTALL_EOF

# ── Step 3: Kill existing server ────────────────────────────────────────────
echo "[3/4] Stopping existing MCP server (if any)..."
ssh "${REMOTE}" bash -s -- "${PORT}" "${TMUX_SESSION}" <<'KILL_EOF'
PORT="$1"
TMUX_SESSION="$2"
# Kill tmux session if it exists
tmux kill-session -t "${TMUX_SESSION}" 2>/dev/null && echo "  ✓ Killed tmux session" || echo "  (no existing session)"
# Also kill anything on the port
PID=$(lsof -ti :"${PORT}" 2>/dev/null || true)
if [[ -n "${PID}" ]]; then
    kill "${PID}" 2>/dev/null
    echo "  ✓ Killed PID ${PID} on port ${PORT}"
fi
sleep 1
KILL_EOF

# ── Step 4: Start server in tmux ────────────────────────────────────────────
echo "[4/4] Starting MCP server in tmux session '${TMUX_SESSION}'..."
ssh "${REMOTE}" bash -s -- "${PORT}" "${TMUX_SESSION}" "${MODE_FLAG}" <<'START_EOF'
PORT="$1"
TMUX_SESSION="$2"
MODE_FLAG="$3"

tmux new-session -d -s "${TMUX_SESSION}" \
    "cd ~/slurm-mcp-server && python3 slurm_mcp_sse.py ${MODE_FLAG} --port ${PORT} --host 0.0.0.0 2>&1 | tee mcp.log"

# Wait briefly and check if it started
sleep 2
if tmux has-session -t "${TMUX_SESSION}" 2>/dev/null; then
    echo "  ✓ Server started on port ${PORT}"
    echo "  ✓ tmux session: ${TMUX_SESSION}"
    echo ""
    echo "  View logs:   ssh ${HOSTNAME} 'tmux attach -t ${TMUX_SESSION}'"
    echo "  Or:          ssh ${HOSTNAME} 'tail -f ~/slurm-mcp-server/mcp.log'"
    echo "  Stop:        ssh ${HOSTNAME} 'tmux kill-session -t ${TMUX_SESSION}'"
else
    echo "  ✗ Server failed to start. Check logs:"
    cat ~/slurm-mcp-server/mcp.log 2>/dev/null | tail -20
    exit 1
fi
START_EOF

echo
echo "═══════════════════════════════════════════════════════"
echo "  MCP server running at http://${REMOTE##*@}:${PORT}"
echo "  Connect your agent with: MCP_URL=http://${REMOTE##*@}:${PORT}"
echo "═══════════════════════════════════════════════════════"
