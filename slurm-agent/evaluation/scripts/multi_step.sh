#!/bin/bash
#SBATCH --job-name=multi_step
#SBATCH --partition=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:15:00
#SBATCH --output=logs/multistep_%j.out
#SBATCH --error=logs/multistep_%j.err

mkdir -p logs

echo "=== Multi-Step Data Processing ==="
echo "Job ID:  $SLURM_JOB_ID"
echo "Node:    $SLURMD_NODENAME"
echo "Started: $(date)"

WORKDIR="/tmp/multistep/$SLURM_JOB_ID"
mkdir -p "$WORKDIR"

# Step 1: Generate data
echo "[Step 1/4] Generating synthetic data..."
python3 -c "
import json, random, pathlib
random.seed(42)
data = [{'id': i, 'x': random.gauss(0,1), 'y': random.gauss(5,2), 'label': random.choice(['A','B','C'])} for i in range(1000)]
pathlib.Path('$WORKDIR/raw.json').write_text(json.dumps(data))
print(f'  Generated {len(data)} records')
"

# Step 2: Filter
echo "[Step 2/4] Filtering outliers..."
python3 -c "
import json, pathlib
data = json.loads(pathlib.Path('$WORKDIR/raw.json').read_text())
filtered = [r for r in data if abs(r['x']) < 2 and abs(r['y'] - 5) < 4]
pathlib.Path('$WORKDIR/filtered.json').write_text(json.dumps(filtered))
print(f'  Kept {len(filtered)}/{len(data)} records')
"

# Step 3: Aggregate
echo "[Step 3/4] Aggregating by label..."
python3 -c "
import json, pathlib
from collections import defaultdict
data = json.loads(pathlib.Path('$WORKDIR/filtered.json').read_text())
agg = defaultdict(lambda: {'count': 0, 'sum_x': 0, 'sum_y': 0})
for r in data:
    a = agg[r['label']]
    a['count'] += 1; a['sum_x'] += r['x']; a['sum_y'] += r['y']
result = {k: {**v, 'mean_x': v['sum_x']/v['count'], 'mean_y': v['sum_y']/v['count']} for k,v in agg.items()}
pathlib.Path('$WORKDIR/aggregated.json').write_text(json.dumps(result, indent=2))
for k,v in result.items():
    print(f'  {k}: n={v[\"count\"]}, mean_x={v[\"mean_x\"]:.3f}, mean_y={v[\"mean_y\"]:.3f}')
"

# Step 4: Summary
echo "[Step 4/4] Writing summary report..."
python3 -c "
import json, pathlib
raw = json.loads(pathlib.Path('$WORKDIR/raw.json').read_text())
filtered = json.loads(pathlib.Path('$WORKDIR/filtered.json').read_text())
agg = json.loads(pathlib.Path('$WORKDIR/aggregated.json').read_text())
report = {'total_raw': len(raw), 'total_filtered': len(filtered), 'labels': list(agg.keys()), 'status': 'SUCCESS'}
pathlib.Path('$WORKDIR/report.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
"

echo "All steps complete. Output: $WORKDIR/"
echo "Finished: $(date)"
