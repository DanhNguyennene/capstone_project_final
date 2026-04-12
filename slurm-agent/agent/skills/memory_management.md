# Memory Management and OOM Debugging

**When to use:** User gets OOM-killed jobs (exit 137), memory errors, or asks about memory allocation.

## Key Concepts
- `--mem=32G` — total memory for entire job.
- `--mem-per-cpu=4G` — memory per CPU (total = cpus × mem-per-cpu). Mutually exclusive with --mem.
- `--mem-per-gpu=16G` — memory per GPU.
- Default memory is set by admin (often small). Always request explicitly.
- Slurm enforces via cgroups — exceeding kills the job with signal 9 (exit 137).

## Steps
1. Call `diagnose_job(job_id=<id>)` — confirms exit code 137:0 or 0:9 (OOM).
2. Call `sacct(job_id=<id>)` with format containing MaxRSS — shows peak memory usage.
3. Calculate: if MaxRSS ≈ requested --mem, job was right at the limit. Recommend 20-50% more.
4. If MaxRSS << requested, the OOM happened in a child process or on a shared node.

## sacct Memory Fields
- **MaxRSS**: Peak resident set size across all steps (actual usage).
- **ReqMem**: Requested memory. Suffix: `c` = per-CPU, `n` = per-node.
- **AveRSS**: Average RSS across all steps.

## Practical Fixes
- `sbatch --mem=64G job.sh` — increase request.
- Use `--mem-per-cpu=8G` for MPI jobs that scale with CPU count.
- Add `ulimit -v unlimited` in script if hitting virtual memory limits.
- For Python: reduce batch size, use `gc.collect()`, move data to disk.
- For multi-GPU training: memory is per-GPU, use `--mem-per-gpu`.

## Output Format
Show peak usage vs allocation, percent used, and specific recommendation.
