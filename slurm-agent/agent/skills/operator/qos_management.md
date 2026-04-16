# QOS Management

**When to use:** You are asked to create, modify, or delete a QOS (Quality of Service); or to set/change QOS limits, priority, or preemption settings.

## Available Tools
- `sacctmgr_add(entity="qos", params=<spec>)` — create new QOS
- `sacctmgr_modify(entity="qos", where="name=<qos>", params=<spec>)` — change QOS limits
- `sacctmgr_delete(entity="qos", params="name=<name>")` — delete QOS
- `scontrol_show(entity="assoc_mgr", id="qos=<name>")` — verify live cache

## Key QOS Parameters
| Parameter | Purpose | Example |
|---|---|---|
| `Priority` | Job priority boost (higher = earlier) | `Priority=1000` |
| `MaxTRESPJ` | Max TRES per job | `MaxTRESPJ=cpu=128,gres/gpu=4` |
| `MaxWall` | Max walltime per job | `MaxWall=48:00:00` |
| `MaxJobsPU` | Max running jobs per user | `MaxJobsPU=10` |
| `MaxSubmitJobsPU` | Max pending+running per user | `MaxSubmitJobsPU=100` |
| `GrpTRES` | Aggregate TRES cap for all jobs in QOS | `GrpTRES=cpu=512,gres/gpu=8` |
| `GrpJobs` | Max running jobs total | `GrpJobs=50` |
| `UsageFactor` | Billing multiplier (1.0=normal, 2.0=double) | `UsageFactor=0.5` |
| `Flags` | Special behaviors | `DenyOnLimit,OverPartQOS` |
| `Preempt` | QOSes this QOS can preempt | `Preempt=standby` |
| `PreemptMode` | How to preempt | `PreemptMode=REQUEUE` |

## Workflows

### Create a new QOS
```
sacctmgr_add(entity="qos", params="name=high Priority=1000 MaxTRESPJ=cpu=128 MaxWall=48:00:00")
```

### Create a low-priority/standby QOS (preemptable by others)
```
sacctmgr_add(entity="qos", params="name=standby Priority=1 UsageFactor=0.0 Flags=NoReserve")
```

### Increase priority of an existing QOS
```
sacctmgr_modify(entity="qos", where="name=high", params="Priority=2000")
```

### Set resource limits on a QOS
```
sacctmgr_modify(entity="qos", where="name=normal", params="MaxTRESPJ=cpu=64,gres/gpu=2 MaxWall=24:00:00 MaxJobsPU=5")
```
Clear a limit: `MaxTRESPJ=cpu=-1`

### Enable preemption
```
sacctmgr_modify(entity="qos", where="name=high", params="Preempt=standby PreemptMode=REQUEUE")
```

### Delete a QOS
```
sacctmgr_delete(entity="qos", params="name=<qos_name>")
```
Warning: users/associations referencing this QOS must have it removed first or jobs will fail with `InvalidQOS`.

### Grant QOS to a user or account
After creating the QOS, assign it to a user:
```
sacctmgr_modify(entity="user", where="name=<user>", params="QosLevel+=<qos_name>")
```
Or to an account:
```
sacctmgr_modify(entity="account", where="name=<acct>", params="QosLevel+=<qos_name>")
```

## Verification
```
scontrol_show(entity="assoc_mgr", id="qos=<name>")
```
Or list all QOS: `sacctmgr_show(entity="qos", params="format=Name,Priority,MaxTRESPJ,MaxWall,GrpTRES")`

## After Actions
Report: QOS | Parameter | Old → New — markdown table.
