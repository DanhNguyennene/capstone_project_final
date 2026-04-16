#!/bin/bash
#SBATCH --job-name=long_simulation
#SBATCH --partition=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=logs/sim_%j.out
#SBATCH --error=logs/sim_%j.err

mkdir -p logs

echo "=== Long Running Simulation ==="
echo "Job ID:  $SLURM_JOB_ID"
echo "Node:    $SLURMD_NODENAME"
echo "CPUs:    $SLURM_CPUS_PER_TASK"
echo "Started: $(date)"

# Simulated long computation with periodic checkpoints
CHECKPOINT_DIR="/tmp/sim_checkpoints/$SLURM_JOB_ID"
mkdir -p "$CHECKPOINT_DIR"

for step in $(seq 1 100); do
    # Simulate work (sleep 1s per step)
    sleep 1
    
    # Progress output
    if (( step % 10 == 0 )); then
        echo "[$(date +%H:%M:%S)] Step $step/100 (${step}%)"
        echo "$step" > "$CHECKPOINT_DIR/checkpoint.txt"
    fi
done

echo "Simulation complete."
echo "$SLURM_JOB_ID $(date -Iseconds)" > "$CHECKPOINT_DIR/.sim_complete"
echo "Finished: $(date)"
