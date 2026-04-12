#!/bin/bash
#SBATCH --job-name=will_fail
#SBATCH --partition=debug
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=100M
#SBATCH --time=00:02:00
#SBATCH --output=/tmp/slurm_test/fail_%j.out

mkdir -p /tmp/slurm_test
echo "This job will fail at $(date)"
echo "Running on node: $(hostname)"

# Simulate work then exit with error
sleep 5
echo "Encountering a fatal error..."
exit 1
