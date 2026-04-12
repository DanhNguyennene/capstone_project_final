#!/bin/bash
#SBATCH --job-name=test_sleep
#SBATCH --partition=debug
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=100M
#SBATCH --time=00:05:00
#SBATCH --output=/tmp/slurm_test/sleep_%j.out

mkdir -p /tmp/slurm_test
echo "Sleep job started at $(date)"
echo "Running on node: $(hostname)"
echo "Job ID: $SLURM_JOB_ID"
sleep 60
echo "Sleep job finished at $(date)"
