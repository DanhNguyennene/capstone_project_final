# Slurm Official: Job State Codes

**When to use:** User asks for meaning of job states, transitions, or failure semantics.
**Official source:** https://slurm.schedmd.com/job_state_codes.html
**Refreshed:** 2026-04-19 04:03:51 UTC

## Fast Path
- PENDING means eligible but waiting on policy/resources/dependencies.
- RUNNING means actively executing on allocated resources.
- FAILED/CANCELLED/TIMEOUT are terminal outcome states for reporting and follow-up.

## Canonical Examples
```bash
PENDING -> RUNNING -> COMPLETED
PENDING -> CANCELLED
RUNNING -> FAILED
RUNNING -> TIMEOUT
```

## Retrieved Notes
- CANCELLED
- cancelled by user or administrator
- COMPLETED
- completed execution successfully;
- FAILED
- completed execution unsuccessfully;
- PENDING
- RUNNING
- TIMEOUT
- job has finished or been cancelled
- LAUNCH_FAILED
- failed to launch on the chosen

## Agent Usage
- Use these patterns as primary guidance for command selection and flags.
- If needed, run web_search with: site:slurm.schedmd.com <topic>.
