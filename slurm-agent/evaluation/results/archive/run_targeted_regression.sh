#!/usr/bin/env bash
cd /mnt/e/workspace/uni/capstone_project/slurm-agent || exit 1
mkdir -p evaluation/results

python mcp-server/slurm_mcp_sse.py --mock mixed --port 3002 > evaluation/results/targeted_mcp.log 2>&1 &
MCP_PID=$!
echo "Started MCP PID=$MCP_PID"
for i in $(seq 1 90); do
  if curl -fsS --max-time 2 http://localhost:3002/sse >/dev/null 2>&1; then
    echo "MCP_READY"
    break
  fi
  [[ "$i" -eq 90 ]] && { echo "MCP_NOT_READY"; exit 1; }
done

MCP_SERVER_URL=http://localhost:3002 python -m uvicorn agent.main:app --host 127.0.0.1 --port 8000 > evaluation/results/targeted_agent.log 2>&1 &
AGENT_PID=$!
echo "Started AGENT PID=$AGENT_PID"
for i in $(seq 1 90); do
  if curl -fsS --max-time 2 http://127.0.0.1:8000/health >/dev/null 2>&1; then
    echo "AGENT_READY"
    break
  fi
  [[ "$i" -eq 90 ]] && { echo "AGENT_NOT_READY"; exit 1; }
done

TEST_IDS=(read_util_healthy action_release_1004_healthy bulk_cancel_pending_healthy bulk_cancel_gpu_running_healthy safety_cancel_all_healthy)
: > evaluation/results/targeted_summary.txt
for ID in "${TEST_IDS[@]}"; do
  LOG="evaluation/results/targeted_${ID}.log"
  echo "RUNNING $ID"
  python evaluation/scenario_eval.py --test-id "$ID" --auto-approve --delay 0 --agent-url http://127.0.0.1:8000 --mcp-url http://localhost:3002 > "$LOG" 2>&1 || true
  RESULT="UNKNOWN"
  if grep -Eq "\bFAIL\b|❌" "$LOG"; then
    RESULT="FAIL"
  elif grep -Eq "\bPASS\b|✅" "$LOG"; then
    RESULT="PASS"
  fi
  LOOP_SIGNAL=$(grep -Ein "max turn|max_turn|max-turn|loop" "$LOG" | head -n 3 | tr '\n' '; ')
  [[ -z "$LOOP_SIGNAL" ]] && LOOP_SIGNAL="none"
  echo "$ID|$RESULT|$LOOP_SIGNAL" | tee -a evaluation/results/targeted_summary.txt
done

kill "$AGENT_PID" >/dev/null 2>&1 || true
kill "$MCP_PID" >/dev/null 2>&1 || true
wait "$AGENT_PID" >/dev/null 2>&1 || true
wait "$MCP_PID" >/dev/null 2>&1 || true

echo "DONE"
cat evaluation/results/targeted_summary.txt
