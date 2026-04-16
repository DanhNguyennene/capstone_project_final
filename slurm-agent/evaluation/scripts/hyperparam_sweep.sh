#!/bin/bash
#SBATCH --job-name=param_sweep
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --gres=gpu:1
#SBATCH --time=00:15:00
#SBATCH --output=logs/sweep_%A_%a.out
#SBATCH --error=logs/sweep_%A_%a.err
# Submit with: --array=0-11%4

mkdir -p logs

TASK_ID=${SLURM_ARRAY_TASK_ID:-0}

# Hyperparameter grid
LR_VALUES=(0.1 0.01 0.001 0.0001)
BATCH_VALUES=(32 64 128)

LR_IDX=$((TASK_ID / 3))
BATCH_IDX=$((TASK_ID % 3))

LR=${LR_VALUES[$LR_IDX]}
BATCH=${BATCH_VALUES[$BATCH_IDX]}

echo "=== Hyperparameter Sweep ==="
echo "Job ID:     $SLURM_JOB_ID"
echo "Array Task: $TASK_ID"
echo "Node:       $SLURMD_NODENAME"
echo "LR:         $LR"
echo "Batch Size: $BATCH"
echo "Started:    $(date)"

# Simulated training run
python3 -c "
import random, json, os, pathlib
random.seed($TASK_ID)
lr, batch = $LR, $BATCH
acc = min(0.99, 0.5 + random.gauss(0.3, 0.05) - abs(lr - 0.001) * 10)
loss = max(0.01, 1.0 - acc + random.gauss(0, 0.02))
result = {'task_id': $TASK_ID, 'lr': lr, 'batch': batch,
          'accuracy': round(acc, 4), 'loss': round(loss, 4)}
out = pathlib.Path('/tmp/ml_pipeline/sweep_results')
out.mkdir(parents=True, exist_ok=True)
(out / f'task_{$TASK_ID}.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
"

echo "Finished: $(date)"
