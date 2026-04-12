#!/bin/bash
#SBATCH --job-name=oom_test
#SBATCH --partition=debug
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=50M
#SBATCH --time=00:05:00
#SBATCH --output=/tmp/slurm_test/oom_%j.out

mkdir -p /tmp/slurm_test
echo "OOM test started at $(date)"
echo "Memory limit: 50MB"

# Try to allocate way more memory than allowed
python3 -c "
import time
chunks = []
try:
    for i in range(100):
        chunks.append(bytearray(10 * 1024 * 1024))  # 10MB each
        print(f'Allocated {(i+1)*10} MB')
        time.sleep(1)
except MemoryError:
    print('MemoryError caught')
"

echo "OOM test finished at $(date)"
