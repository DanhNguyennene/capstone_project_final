#!/bin/bash
#SBATCH --job-name=memory_hog
#SBATCH --partition=cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=logs/memhog_%j.out
#SBATCH --error=logs/memhog_%j.err

# This job deliberately allocates too much memory to trigger OOM.
# Useful for testing OOM diagnosis workflows.

mkdir -p logs

echo "=== Memory Hog Job ==="
echo "Job ID:  $SLURM_JOB_ID"
echo "Node:    $SLURMD_NODENAME"
echo "Mem req: ${SLURM_MEM_PER_NODE:-N/A}MB"
echo "Started: $(date)"

echo "Allocating memory beyond limit..."
python3 -c "
# Allocate ~3GB in a 2GB job → should get OOM killed
import sys
data = []
chunk = 100 * 1024 * 1024  # 100MB chunks
for i in range(30):
    data.append(bytearray(chunk))
    print(f'Allocated {(i+1)*100}MB', flush=True)
print('If you see this, OOM was not triggered')
" 2>&1

echo "Finished: $(date)"
