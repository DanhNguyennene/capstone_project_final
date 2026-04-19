# Slurm Official: scancel

**When to use:** User needs canonical cancellation behavior, syntax, arrays, or scoped cancellation.
**Official source:** https://slurm.schedmd.com/scancel.html
**Refreshed:** 2026-04-19 04:03:51 UTC

## Fast Path
- Use scancel for cancellation and signal delivery to jobs or steps.
- Prefer exact job IDs for destructive actions; keep target binding strict.
- For job arrays, parent IDs and array selectors are valid targets.

## Canonical Examples
```bash
scancel 1004
scancel 1001,1002,1003
scancel 12345_[1-8]
scancel --user alice
```

## Retrieved Notes
- Slurm Workload Manager - scancel
- scancel
- scancel - Used to signal jobs or job steps that are under the control of Slurm.
- scancel [ OPTIONS ...] [ job_id [_ array_id ][. step_id ]] [ job_id [_ array_id ][. step_id ]...]
- scancel is used to signal or cancel jobs, job arrays or job steps.
- An arbitrary number of jobs or job steps may be signaled using job
- specification filters or a space separated list of specific job and/or
- job step IDs.
- If the job ID of a job array is specified with an array ID value and the job
- associated with the array ID value has been split from the array, then only that
- job array element will be cancelled.
- If the job ID of a job array is specified without an array ID value or the

## Agent Usage
- Use these patterns as primary guidance for command selection and flags.
- If needed, run web_search with: site:slurm.schedmd.com <topic>.
