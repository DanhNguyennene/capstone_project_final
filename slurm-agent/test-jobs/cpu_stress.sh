#!/bin/bash
#SBATCH --job-name=cpu_stress
#SBATCH --partition=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=500M
#SBATCH --time=00:10:00
#SBATCH --output=/tmp/slurm_test/cpu_stress_%j.out

mkdir -p /tmp/slurm_test
echo "CPU stress test started at $(date)"
echo "Using $SLURM_CPUS_PER_TASK CPUs"

# Spin up CPU-bound workers
for i in $(seq 1 $SLURM_CPUS_PER_TASK); do
    echo "Starting worker $i"
    ( while true; do :; done ) &
done

sleep 120
kill $(jobs -p)
echo "CPU stress test finished at $(date)"
