#!/bin/bash
#SBATCH --job-name=will_timeout
#SBATCH --partition=debug
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:01:00
#SBATCH --output=logs/timeout_%j.out
#SBATCH --error=logs/timeout_%j.err

# This job sleeps longer than its time limit (1 min) to trigger TIMEOUT.
# Useful for testing timeout diagnosis workflows.

mkdir -p logs

echo "=== Timeout Test Job ==="
echo "Job ID:  $SLURM_JOB_ID"
echo "Node:    $SLURMD_NODENAME"
echo "Time limit: 1 minute"
echo "Started: $(date)"

echo "Sleeping for 5 minutes (will be killed at 1 min)..."
for i in $(seq 1 300); do
    sleep 1
    if (( i % 15 == 0 )); then
        echo "[$(date +%H:%M:%S)] Still running... ${i}s elapsed"
    fi
done

echo "This should never print"
