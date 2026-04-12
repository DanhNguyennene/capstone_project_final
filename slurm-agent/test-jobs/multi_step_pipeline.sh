#!/bin/bash
#SBATCH --job-name=pipeline
#SBATCH --partition=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=512M
#SBATCH --time=00:15:00
#SBATCH --output=/tmp/slurm_test/pipeline_%j.out

mkdir -p /tmp/slurm_test
WORKDIR="/tmp/slurm_test/pipeline_$SLURM_JOB_ID"
mkdir -p "$WORKDIR"

echo "=== Pipeline started at $(date) ==="

# Stage 1: Data generation
echo "[Stage 1] Generating data..."
python3 -c "
import random, json
data = [{'id': i, 'value': random.gauss(0, 1)} for i in range(1000)]
with open('$WORKDIR/data.json', 'w') as f:
    json.dump(data, f)
print(f'Generated {len(data)} records')
"

# Stage 2: Processing
echo "[Stage 2] Processing data..."
python3 -c "
import json, statistics
with open('$WORKDIR/data.json') as f:
    data = json.load(f)
values = [d['value'] for d in data]
results = {
    'count': len(values),
    'mean': statistics.mean(values),
    'stdev': statistics.stdev(values),
    'min': min(values),
    'max': max(values),
}
with open('$WORKDIR/results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f'Results: {results}')
"

# Stage 3: Report
echo "[Stage 3] Generating report..."
cat "$WORKDIR/results.json"

echo ""
echo "=== Pipeline finished at $(date) ==="
