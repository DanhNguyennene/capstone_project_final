#!/bin/bash
#SBATCH --job-name=array_test
#SBATCH --partition=debug
#SBATCH --array=1-5
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=100M
#SBATCH --time=00:05:00
#SBATCH --output=/tmp/slurm_test/array_%A_%a.out

mkdir -p /tmp/slurm_test
echo "Array task $SLURM_ARRAY_TASK_ID of job $SLURM_ARRAY_JOB_ID"
echo "Running on node: $(hostname)"
echo "Started at $(date)"

# Each task does different work based on its index
SLEEP_TIME=$((SLURM_ARRAY_TASK_ID * 10))
echo "Sleeping for $SLEEP_TIME seconds"
sleep $SLEEP_TIME

echo "Array task $SLURM_ARRAY_TASK_ID finished at $(date)"
