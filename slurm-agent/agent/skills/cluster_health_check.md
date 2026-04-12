# Cluster Health Check

**When to use:** User asks for overall cluster status, health report, or something seems wrong.

## Steps

1. Call `sinfo()` to get partition and node states.
2. Call `squeue()` to get the job queue overview.
3. If any nodes show `down`, `drain`, or `error` state, call `scontrol_show(entity="node", id=<node_name>)` for details and the `Reason` field.
4. Check job distribution: count RUNNING vs PENDING. High pending-to-running ratio suggests resource pressure.
5. If many jobs are PENDING with reason `Resources`, check if nodes are down or oversubscribed.
6. Optionally call `sdiag()` if the user asks about scheduler performance.

## Warning Signs
- Nodes in `drain` or `down` state
- All jobs PENDING with `Priority` reason (scheduler backlog)
- High `Resources` pending count with idle nodes (possible misconfiguration)
- `ReqNodeNotAvail` on many jobs (specific node outage)

## Output Format
Summary table of partitions + node states, job queue breakdown, any issues flagged with recommendations.
