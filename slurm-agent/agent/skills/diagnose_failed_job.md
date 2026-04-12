# Diagnose Failed Job

**When to use:** User asks why a job failed, reports an error, or wants to understand exit codes.

## Steps

1. Call `diagnose_job(job_id=<id>)` to get the full diagnosis with exit code and hints.
2. If exit code is 137 (OOM), call `scontrol_show(entity="job", id=<id>)` to check requested vs allocated memory.
3. If exit code is 143 (timeout), check the `--time` vs actual elapsed time.
4. If exit code is 1 (generic), the application itself errored — suggest checking stderr output.
5. Call `sacct(job_id=<id>)` to get resource usage history (MaxRSS, elapsed, etc.).

## Exit Code Reference
- **0** — Success
- **1** — Application error (bug in user code)
- **2** — Bash misuse (bad script syntax)
- **126** — Permission denied
- **127** — Command not found (missing module/binary)
- **137** — OOM-killed by cgroup (increase `--mem`)
- **143** — SIGTERM from walltime limit (increase `--time`)
- **1:0** — Node failure (requeue the job)

## Output Format
Report: job ID, exit code, root cause, and one specific fix.
