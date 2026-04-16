# Reservation Management

**When to use:** User asks about reservations, reserved nodes, maintenance windows, or why jobs can't run due to reservations.

## Key Concepts
- Reservations block nodes/CPUs for specific users, accounts, or time windows.
- `MAINT` flag → maintenance window (shows as PlannedDown in utilization).
- `OVERLAP` flag → reservation can share resources with other reservations.
- `DAILY/WEEKLY` flags → recurring reservations.
- Jobs outside a reservation cannot use reserved resources unless the job requests that reservation with `--reservation=<name>`.

## Steps

### List all reservations
```
scontrol_show(entity="reservation")
```
Columns to highlight: `ReservationName`, `StartTime`, `EndTime`, `Nodes`, `Users`, `Accounts`, `Flags`.

### Show reservation utilization (requires accounting)
```
sacctmgr_show(entity="reservation", params="cluster=<cluster> start=<date> end=<date>")
```

### Check if a job is blocked by a reservation
1. `scontrol_show(entity="job", id=<job_id>)` — check `Reason` field.
   - `ReqNodeNotAvail` or `Reserved` means reserved nodes conflict.
2. `scontrol_show(entity="reservation")` — find which reservation holds those nodes.
3. Check if the user/account is allowed in the reservation's `Users`/`Accounts` field.

### Sreport reservation utilization
```
sreport(report_type="reservation utilization", params="Start=<YYYY-MM-DD> End=<YYYY-MM-DD>")
```

## Output Format
| Reservation | Start | End | Nodes | Users | Flags |
|---|---|---|---|---|---|
| maint_2024 | 2024-01-10T08:00 | 2024-01-10T18:00 | node[01-04] | — | MAINT |

Note any conflict between reservation end time and pending job eligible time.
