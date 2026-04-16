# Reservation Creation and Management

**When to use:** You are asked to create, modify, or delete a Slurm reservation for maintenance windows, priority access, or license reservations.

## Available Tools
- `scontrol_create(entity="reservation", params=<spec>)` — create new reservation
- `scontrol_update(entity="reservation", id=<name>, params=<spec>)` — modify existing reservation
- `scontrol_delete(entity="reservation", id=<name>)` — delete reservation
- `scontrol_show(entity="reservation")` — verify reservations

## Key Parameters
| Parameter | Purpose | Example |
|---|---|---|
| `ReservationName` | Unique name | `maint_2024` |
| `StartTime` | Start (absolute or relative) | `2024-12-01T08:00:00` or `now+1hour` |
| `EndTime` or `Duration` | When it ends | `2024-12-01T18:00:00` or `10:00:00` |
| `Nodes` | Which nodes | `node[01-04]` or `ALL` |
| `NodeCnt` | How many nodes (auto-select) | `4` |
| `Users` | Who can use it | `alice,bob` |
| `Accounts` | Which accounts | `physics,chemistry` |
| `Flags` | Behavior flags | `MAINT,OVERLAP,DAILY` |

## Workflows

### Create a maintenance reservation
```
scontrol_create(entity="reservation", params="ReservationName=maint_jan Nodes=node[01-04] StartTime=2024-01-15T08:00:00 EndTime=2024-01-15T18:00:00 Flags=MAINT Users=root")
```

### Create a priority reservation for specific users
```
scontrol_create(entity="reservation", params="ReservationName=priority_run Users=alice,bob NodeCnt=2 StartTime=now Duration=04:00:00")
```

### Create a recurring daily reservation
```
scontrol_create(entity="reservation", params="ReservationName=daily_maint Nodes=node01 StartTime=2024-01-01T02:00:00 Duration=01:00:00 Flags=DAILY,MAINT Users=root")
```

### Modify an existing reservation (extend end time)
```
scontrol_update(entity="reservation", id="maint_jan", params="EndTime=2024-01-15T22:00:00")
```

### Add nodes to existing reservation
```
scontrol_update(entity="reservation", id="maint_jan", params="Nodes+=node05")
```

### Delete a reservation
```
scontrol_delete(entity="reservation", id="maint_jan")
```
Warning: all pending jobs requesting this reservation will be held.

## Verification
```
scontrol_show(entity="reservation")
```
Confirm `ReservationName`, `StartTime`, `EndTime`, `Nodes`, `Users`, `State=ACTIVE or INACTIVE`.

## After Actions
Report: Reservation | Action | StartTime | EndTime | Nodes | Users — markdown table.
