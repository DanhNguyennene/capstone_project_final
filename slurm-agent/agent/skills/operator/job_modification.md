# Job Modification

**When to use:** You are asked to change properties of a running or pending job: time limit, node count, QOS, priority, dependency, partition, account, or to hold/release/requeue jobs.

## Available Tools
- `scontrol_update(entity="job", id=<job_id>, params=<spec>)` — modify job properties
- `scontrol_hold(job_id)` — hold (priority=0) a pending job
- `scontrol_release(job_id)` — release a held job
- `scontrol_requeue(job_id)` — requeue a running/suspended/finished job back to PENDING
- `scontrol_show(entity="job", id=<job_id>)` — verify before/after

## Key Update Parameters
| What | Parameter | Example |
|---|---|---|
| Extend time limit | `TimeLimit=+<minutes>` | `TimeLimit=+60` |
| Set absolute time | `TimeLimit=<HH:MM:SS>` | `TimeLimit=4:00:00` |
| Change partition | `Partition=<name>` | `Partition=gpu` |
| Change QOS | `QOS=<name>` | `QOS=high` |
| Change account | `Account=<name>` | `Account=physics` |
| Modify dependency | `Dependency=afterok:<id>` | `Dependency=afterok:1234` |
| Clear dependency | `Dependency=` | (empty value) |
| Change node count | `NumNodes=<min>[-<max>]` | `NumNodes=2` |
| Change nice/priority | `Nice=<value>` | `Nice=-100` (higher priority) |
| Change reservation | `ReservationName=<name>` | `ReservationName=maint_jan` |

## Workflows

### Extend a running job's time limit
```
scontrol_update(entity="job", id="<job_id>", params="TimeLimit=+120")
```
Only privileged users can extend running jobs.

### Change partition of a pending job
```
scontrol_update(entity="job", id="<job_id>", params="Partition=gpu")
```

### Hold a pending job (prevent it from starting)
```
scontrol_hold(job_id="<job_id>")
```
Or via update: `scontrol_update(entity="job", id="<job_id>", params="Priority=0")`

### Release a held job
```
scontrol_release(job_id="<job_id>")
```

### Requeue a running job (return to PENDING)
```
scontrol_requeue(job_id="<job_id>")
```
Job will restart from the beginning. Useful when a node is suspected faulty.

### Cancel stuck dependency (never-satisfied)
If `DependencyNeverSatisfied`, clear it:
```
scontrol_update(entity="job", id="<job_id>", params="Dependency=")
```

### Bump a job's priority
```
scontrol_update(entity="job", id="<job_id>", params="Priority=99999")
```
Note: this disables automatic priority updates by the priority plugin.

## Verification
```
scontrol_show(entity="job", id="<job_id>")
```
Confirm the changed field matches the requested value.

## After Actions
Report: JobID | Field Changed | Old Value → New Value — markdown table.
