#!/bin/bash
#SBATCH --job-name=long_runner
#SBATCH --partition=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=256M
#SBATCH --time=01:00:00
#SBATCH --output=/tmp/slurm_test/long_%j.out

mkdir -p /tmp/slurm_test
echo "Long running job started at $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $(hostname)"
echo "CPUs: $SLURM_CPUS_PER_TASK"

for i in $(seq 1 60); do
    echo "[$(date +%H:%M:%S)] Iteration $i/60"
    sleep 30
done

echo "Long running job finished at $(date)"
