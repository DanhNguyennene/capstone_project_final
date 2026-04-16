#!/bin/bash
#SBATCH --job-name=bad_script
#SBATCH --partition=debug
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:05:00
#SBATCH --output=logs/bad_%j.out
#SBATCH --error=logs/bad_%j.err

# This job exits with a non-zero code on purpose.
# Useful for testing failure diagnosis workflows.

mkdir -p logs

echo "=== Deliberately Failing Job ==="
echo "Job ID:  $SLURM_JOB_ID"
echo "Node:    $SLURMD_NODENAME"
echo "Started: $(date)"

echo "Step 1: OK"
echo "Step 2: OK"
echo "Step 3: Simulating critical error..."

# Exit with code 42 (application error)
echo "ERROR: Missing configuration file /etc/app/config.yaml" >&2
echo "ERROR: Cannot proceed without valid config" >&2
exit 42
