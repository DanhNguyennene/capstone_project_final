# MPI and Parallel Jobs

**When to use:** User asks about MPI, multi-node jobs, srun, distributed training, or parallel execution.

## Key Concepts
- `--ntasks=N` — total MPI ranks (processes).
- `--ntasks-per-node=N` — MPI ranks per node.
- `--cpus-per-task=N` — threads per MPI rank (for hybrid MPI+OpenMP).
- `srun` inside sbatch script launches MPI tasks across allocated nodes.
- Don't use `mpirun` on most modern clusters — use `srun` instead.

## Steps
1. If MPI job fails, check `scontrol_show(entity="job")` for NodeList and NumTasks.
2. Check stderr for MPI errors (rank failures, timeout, connection refused).
3. Call `sacct(job_id=<id>)` — look at per-step records (job.0, job.1, etc.).

## Common MPI Patterns
```bash
# Pure MPI: 32 ranks across 4 nodes
#SBATCH --nodes=4
#SBATCH --ntasks=32
#SBATCH --ntasks-per-node=8

module load openmpi
srun ./my_mpi_program

# Hybrid MPI+OpenMP: 4 MPI ranks × 8 threads each
#SBATCH --nodes=2
#SBATCH --ntasks=4
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=8

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
srun ./my_hybrid_program
```

## PyTorch Distributed
```bash
#SBATCH --nodes=2
#SBATCH --gpus-per-node=4
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=4

srun torchrun \
    --nnodes=$SLURM_NNODES \
    --nproc_per_node=$SLURM_GPUS_PER_NODE \
    --rdzv_backend=c10d \
    --rdzv_endpoint=$(hostname):29500 \
    train_ddp.py
```

## Troubleshooting
- "All nodes not ready" → nodes still allocating. Add `--wait-all-nodes=1`.
- "Connection refused" → firewall or wrong port. Use Slurm's `srun` instead of manual launch.
- One rank hangs → deadlock or slow node. Check `sstat()` for per-step stats.

## Output Format
Show node allocation, task distribution, and fix advice.
