# GPU and GRES Resource Management

**When to use:** User asks about GPU jobs, GRES allocation, GPU utilization, or GPU-related errors.

## Key Concepts
- Request GPUs: `#SBATCH --gres=gpu:1` (1 GPU), `--gres=gpu:a100:2` (2 A100s specifically).
- Check available GPUs: `sinfo --Format=NodeList,Partition,Gres,GresUsed,StateCompact`.
- Inside script: `$CUDA_VISIBLE_DEVICES` is auto-set by Slurm. Do NOT set it manually.
- `--gpus-per-task=1` assigns GPUs per task (for multi-task jobs).
- `--gpus-per-node=2` requests 2 GPUs on each allocated node.
- `--gpu-bind=closest` binds GPUs to nearest CPU (NUMA-aware, reduces latency).

## Steps
1. If user asks about GPU availability, call `sinfo(partition="gpu")` and check Gres column.
2. If GPU job is pending, check if reason is `Resources` or `QOSMaxGRESPerUser`.
3. If GPU job fails, check `diagnose_job()` — common issue is requesting more GPUs than exist.
4. For GPU utilization, call `sstat(job_id=<id>)` for running jobs, or `sacct()` for history.

## Common sbatch GPU Patterns
```bash
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-gpu=4        # 4 CPUs per GPU (for data loading)
#SBATCH --mem-per-gpu=16G       # Memory per GPU

module load cuda/12.0
python train.py --gpus 1
```

## Multi-GPU / Multi-Node
```bash
#SBATCH --nodes=2
#SBATCH --gpus-per-node=4       # 4 GPUs per node = 8 total
#SBATCH --ntasks-per-node=4     # 1 task per GPU
#SBATCH --cpus-per-task=8

srun torchrun --nproc_per_node=4 --nnodes=2 train_ddp.py
```

## Troubleshooting
- "CUDA out of memory" → app-level, not Slurm. Reduce batch size or use gradient checkpointing.
- "no CUDA-capable device" → missing `--gres=gpu` or wrong module loaded.
- "Resources" pending → not enough free GPUs. Wait or reduce `--gres`.

## Output Format
Show GPU availability table and specific fix advice.
