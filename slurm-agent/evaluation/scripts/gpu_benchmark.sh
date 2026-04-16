#!/bin/bash
#SBATCH --job-name=gpu_bench
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --gres=gpu:1
#SBATCH --time=00:10:00
#SBATCH --output=logs/gpu_bench_%j.out
#SBATCH --error=logs/gpu_bench_%j.err

mkdir -p logs
echo "=== GPU Benchmark ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Node:   $SLURMD_NODENAME"
echo "GPUs:   ${CUDA_VISIBLE_DEVICES:-none}"
echo "Started: $(date)"

echo ""
echo "--- nvidia-smi ---"
nvidia-smi 2>/dev/null || echo "(nvidia-smi unavailable)"

echo ""
echo "--- GPU Memory Test ---"
python3 -c "
import subprocess, sys
try:
    import torch
    print(f'PyTorch version: {torch.__version__}')
    print(f'CUDA available:  {torch.cuda.is_available()}')
    if torch.cuda.is_available():
        print(f'GPU name:        {torch.cuda.get_device_name(0)}')
        print(f'GPU memory:      {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB')
        # Quick matrix multiply benchmark
        import time
        x = torch.randn(4096, 4096, device='cuda')
        torch.cuda.synchronize()
        t0 = time.time()
        for _ in range(10):
            y = x @ x
        torch.cuda.synchronize()
        elapsed = time.time() - t0
        print(f'MatMul 4096x4096 x10: {elapsed:.3f}s')
except ImportError:
    print('PyTorch not installed — skipping GPU test')
" 2>&1

echo ""
echo "Finished: $(date)"
