# Job Efficiency Audit

**When to use:** User asks about resource waste, efficiency, or wants to optimize their jobs.

## Steps

1. Call `squeue(state="RUNNING")` to find running jobs.
2. For each running job (limit to 5), call `sstat(job_id=<id>)` to get live CPU%, RSS, disk I/O.
3. Call `sacct(user=<user>, start_time="now-7days")` to get recent job history with resource usage.
4. Compare requested resources vs actual usage:
   - If MaxRSS << requested memory → user is over-requesting memory
   - If elapsed << time limit → user is over-requesting walltime
   - If CPUs used << CPUs requested → job isn't parallelized well

## Efficiency Thresholds
- **Good**: >70% CPU utilization, >50% memory utilization
- **Warning**: 30-70% CPU, 20-50% memory
- **Wasteful**: <30% CPU, <20% memory

## Recommendations
- Over-requesting memory → reduce `--mem` to 1.2x actual MaxRSS
- Over-requesting time → reduce `--time` to 1.5x actual elapsed
- Low CPU usage → reduce `--cpus-per-task` or check parallelization

## Output Format
Per-job efficiency table, overall efficiency score, top 3 optimization suggestions.
