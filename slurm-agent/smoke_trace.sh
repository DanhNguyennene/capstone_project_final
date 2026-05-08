#!/usr/bin/env bash
# smoke_trace.sh — Run 1 test per category to verify traces have raw tool_name/tool_args.
# Usage:
#   export OPENAI_API_KEY="sk-..."
#   bash smoke_trace.sh [--provider openai] [--model gpt-5.4]
#
# Prerequisites: agent on :8000, MCP on :3002

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PROVIDER="${1:-openai}"
MODEL="${2:-gpt-5.4}"
OUTDIR="evaluation/results"
SMOKE_OUT="$OUTDIR/smoke_trace_$(date +%Y%m%d_%H%M%S).json"

CATEGORIES=(read diagnose action submit safety edge account node)

echo "=== Smoke Trace Test ==="
echo "  Provider : $PROVIDER"
echo "  Model    : $MODEL"
echo ""

# Collect one test ID per category from the dataset
TMPIDS=$(mktemp)
python3 -c "
import json, random
from pathlib import Path

ds = json.loads((Path('evaluation/dataset.json')).read_text())
by_cat = {}
for t in ds:
    cat = t.get('category','').split('_')[0]  # e.g. 'read_jobs' -> 'read'
    if cat not in by_cat:
        by_cat[cat] = []
    by_cat[cat].append(t['id'])

# Pick one random test per category prefix
chosen = []
for cat in sorted(by_cat):
    chosen.append(random.choice(by_cat[cat]))

json.dump(chosen, open('$TMPIDS','w'))
print(f'Selected {len(chosen)} tests across {len(by_cat)} categories')
for c in sorted(by_cat):
    print(f'  {c}: {len(by_cat[c])} cases')
"

echo ""
echo "Running eval on smoke sample..."
python3 evaluation/scenario_eval.py \
  --main-provider "$PROVIDER" \
  --main-model "$MODEL" \
  --test-ids-file "$TMPIDS" \
  --workers 4 \
  --auto-approve

# Find the latest result file
LATEST=$(ls -t "$OUTDIR"/eval_all_*.json 2>/dev/null | head -1)
if [ -z "$LATEST" ]; then
  echo "ERROR: No result file produced!"
  rm -f "$TMPIDS"
  exit 1
fi

echo ""
echo "=== Trace Quality Check ==="
python3 -c "
import json, sys

data = json.loads(open('$LATEST').read())
results = data.get('results', [])
total = len(results)
has_history = 0
has_raw_name = 0
has_raw_args = 0
has_output = 0
has_response = 0
missing = []

for r in results:
    h = r.get('tool_call_history', [])
    resp = r.get('agent_response', '')
    if resp:
        has_response += 1
    if not h:
        missing.append((r.get('test_id','?'), 'no tool_call_history'))
        continue
    has_history += 1

    tools = [e for e in h if e.get('type') == 'tool']
    if not tools:
        missing.append((r.get('test_id','?'), 'no tool entries'))
        continue

    got_name = any('tool_name' in e for e in tools)
    got_args = any('tool_args' in e for e in tools)
    got_out  = any('output' in e for e in tools)

    if got_name: has_raw_name += 1
    if got_args: has_raw_args += 1
    if got_out:  has_output += 1

    if not got_name or not got_args:
        missing.append((r.get('test_id','?'), f'name={got_name} args={got_args}'))

print(f'Results:        {total}')
print(f'Has history:    {has_history}/{total}')
print(f'Has tool_name:  {has_raw_name}/{total}  (raw)')
print(f'Has tool_args:  {has_raw_args}/{total}  (raw)')
print(f'Has output:     {has_output}/{total}')
print(f'Has response:   {has_response}/{total}')
print()

if missing:
    print('ISSUES:')
    for tid, reason in missing:
        print(f'  {tid}: {reason}')

if has_raw_name == has_history and has_raw_args == has_history and has_history == total:
    print()
    print('ALL TRACES HAVE RAW tool_name + tool_args — READY FOR TRAINING')
    sys.exit(0)
else:
    print()
    print('WARNING: Some traces missing raw fields — check agent patch')
    sys.exit(1)
"

# Show a sample trace entry
echo ""
echo "=== Sample Trace Entry ==="
python3 -c "
import json
data = json.loads(open('$LATEST').read())
for r in data['results']:
    h = r.get('tool_call_history', [])
    tools = [e for e in h if e.get('type') == 'tool']
    if tools:
        print(f'test_id: {r[\"test_id\"]}')
        print(json.dumps(tools[0], indent=2))
        break
"

rm -f "$TMPIDS"
echo ""
echo "Full results: $LATEST"
