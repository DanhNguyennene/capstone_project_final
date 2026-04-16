#!/bin/bash
#SBATCH --job-name=ml_data_download
#SBATCH --partition=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=logs/data_download_%j.out
#SBATCH --error=logs/data_download_%j.err

set -euo pipefail

DATASET_DIR="${SCRATCH:-/tmp}/ml_pipeline/dataset"
mkdir -p "$DATASET_DIR" logs

echo "=== Stage 1: Data Download ==="
echo "Job ID:  $SLURM_JOB_ID"
echo "Node:    $SLURMD_NODENAME"
echo "Started: $(date)"

# Simulated download (creates sample files locally — no network needed)
echo "Simulating dataset download ..."
for i in $(seq 1 20); do
    echo "sample_${i}" > "$DATASET_DIR/sample_${i}.sample"
done

echo "$SLURM_JOB_ID $(date -Iseconds)" > "$DATASET_DIR/.download_complete"

echo "Done. Files in $DATASET_DIR:"
ls -lh "$DATASET_DIR"
echo "Finished: $(date)"
