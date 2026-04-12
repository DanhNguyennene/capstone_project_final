#!/bin/bash
#SBATCH --job-name=memory_hog
#SBATCH --partition=debug
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=200M
#SBATCH --time=00:05:00
#SBATCH --output=/tmp/slurm_test/memory_hog_%j.out

mkdir -p /tmp/slurm_test
echo "Memory allocation test started at $(date)"
echo "Allocated memory limit: $SLURM_MEM_PER_NODE MB"

# Allocate ~150MB using python
python3 -c "
import time
data = bytearray(150 * 1024 * 1024)  # 150 MB
print(f'Allocated {len(data) / 1024 / 1024:.0f} MB')
time.sleep(60)
print('Done')
"

echo "Memory test finished at $(date)"
