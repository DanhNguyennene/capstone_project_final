# Investigate Pending Jobs

**When to use:** User asks why jobs are stuck, pending forever, or not starting.

## Steps

1. Call `squeue(state="PENDING")` to list all pending jobs with reasons.
2. Group jobs by pending reason.
3. For `Resources` — call `sinfo()` to check available nodes vs requested resources.
4. For `Priority` — call `sprio()` to check priority factors. Lower priority jobs wait behind higher ones.
5. For `QOSMaxCpuPerUserLimit` — user hit their CPU quota. Check with `sacctmgr_show(entity="qos")`.
6. For `ReqNodeNotAvail` — the requested node is down. Call `scontrol_show(entity="node", id=<node>)`.
7. For `Dependency` — job depends on another job finishing. Show the dependency chain.

## Common Fixes
- **Priority**: Just wait, or request fewer resources.
- **Resources**: Reduce `--nodes`, `--cpus-per-task`, or `--mem`. Try a different partition.
- **QOS limit**: Wait for other jobs to finish, or ask admin to increase quota.
- **ReqNodeNotAvail**: Remove the `--nodelist` constraint or wait for node repair.

## Output Format
Table of pending jobs grouped by reason, with specific fix for each group.
