# User Job Summary

**When to use:** User asks "what are my jobs", "show my usage", or wants a personal overview.

## Steps

1. Determine the username. If not provided, note that we need it.
2. Call `squeue(user=<username>)` to list their current running and pending jobs.
3. Call `sacct(user=<username>, start_time="now-7days")` to get their recent job history.
4. Count: running, pending, completed, failed jobs.
5. If any jobs failed, briefly note the exit codes.
6. If jobs are pending, note the pending reasons.

## Output Format
- Current jobs table (ID, name, state, partition, runtime)
- Recent history summary (last 7 days: completed, failed, total CPU-hours)
- Any issues flagged (failed jobs, stuck pending jobs)
