# QOS and Account Limits

**When to use:** User hits QOS limits, asks about quotas, fairshare, or account management.

## Key Concepts
- **QOS** (Quality of Service): defines resource limits and priority for groups of jobs.
- **Association**: links a user to an account with specific limits.
- **Fairshare**: adjusts priority based on historical usage — heavy users get lower priority.
- Limits apply at: per-job, per-user, per-account, per-QOS, and aggregate levels.

## Steps
1. If job pending with `QOS*` reason, call `sacctmgr_list(entity="qos")` to see limits.
2. Call `sshare(user=<username>)` to check fairshare standing.
3. Call `sacctmgr_list(entity="association", params="user=<username>")` to see account limits.
4. For `AssocGrp*` reasons, the entire account/group is at a limit — not just this user.

## Common QOS Limits
| Limit | Meaning | Fix |
|-------|---------|-----|
| MaxCpuPerUser | Max CPUs per user across all jobs | Wait for jobs to finish |
| MaxJobsPerUser | Max concurrent running jobs | Wait for completion |
| MaxWallDurationPerJob | Max --time per job | Reduce --time |
| MaxGRESPerUser | Max GPUs per user | Wait for GPU jobs |
| MaxSubmitJobPerUser | Max pending+running | Wait or cancel queued jobs |
| GrpCPUMinutes | Total CPU-minutes for group | Wait for next billing cycle |

## Checking Limits
```
sacctmgr show qos format=Name,MaxWall,MaxCPUs,MaxNodes,MaxGRES,MaxJobsPU,MaxSubmitPU
sacctmgr show association user=alice format=User,Account,QOS,MaxJobs,MaxWall,Fairshare
sshare -u alice  # shows fairshare standing
```

## Output Format
Show the user's current limits and usage as a table.
