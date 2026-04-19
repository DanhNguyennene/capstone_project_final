# GPU Utilization Analysis

**When to use:** User asks about GPU usage, GPU jobs, or GPU availability.

## Steps

1. Call `sinfo(partition="gpu")` to check GPU node states and available GPUs.
2. Call `squeue(partition="gpu")` to see running and pending GPU jobs.
3. For running GPU jobs, call `sstat(job_id=<id>)` to check resource usage.
4. If user wants efficiency, compare allocated GPUs vs actually used.
5. Check if GPU nodes are in `drain` or `down` state.

## Key Metrics
- **GPU allocation**: how many GPUs allocated vs total
- **GPU node state**: idle, mixed, allocated, down
- **Pending GPU jobs**: how many waiting, what resources they need
- **GRES field**: shows GPU type and count (e.g., `gpu:a100:2`)

## Output Format
GPU node status table, running GPU jobs, pending GPU jobs, utilization percentage.
