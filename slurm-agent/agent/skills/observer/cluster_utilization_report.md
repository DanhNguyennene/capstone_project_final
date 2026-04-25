# Cluster Utilization Report

**When to use:** User asks for historical utilization over a time period, efficiency trends, idle/down percentages, or explicit accounting reports.

**Important routing:** For real-time questions like "Is the cluster overloaded?" or "How busy is the cluster right now?", use `squeue` + `sinfo` first. Do not use `sreport` as the only tool for "right now" load checks.

## Key Concepts
- `sreport cluster utilization` breaks time into: Allocated, Down, PlannedDown, Idle, Planned (backfill reserved), Reported.
- **Allocated** = nodes running jobs (or in an active non-MAINT reservation).
- **Idle** = nodes available but unused.
- **Down** = nodes DOWN or fully DRAINED.
- **PlannedDown** = nodes in MAINT reservations or FUTURE/POWERED_DOWN state.
- **Planned** = nodes idle but earmarked by backfill for a future job.
- Default time unit is Minutes. Use `-t hours` for cleaner numbers.
- Reports use hourly rollup granularity; periods < 1 hour are rounded.

## Steps

### Real-time overload check (current state, not historical)
```
sinfo()
squeue()
```

Use this path for "overloaded now" or "busy now" prompts.

### Quick utilization (yesterday by default)
```
sreport(report_type="cluster utilization")
```

### Custom date range
```
sreport(report_type="cluster utilization", params="Start=YYYY-MM-DD End=YYYY-MM-DD")
```

### With GRES/GPU breakdown
```
sreport(report_type="cluster utilization", params="Start=YYYY-MM-DD End=YYYY-MM-DD --tres=cpu,gres/gpu")
```

### Per-account usage breakdown
```
sreport(report_type="cluster AccountUtilizationByUser", params="Start=YYYY-MM-DD End=YYYY-MM-DD")
```

### Top users
```
sreport(report_type="user topusage", params="Start=YYYY-MM-DD End=YYYY-MM-DD TopCount=20")
```

## Output Format
| Metric | Value | % of Reported |
|---|---|---|
| Allocated | X min | Y% |
| Idle | X min | Y% |
| Down | X min | Y% |

Add 1-2 lines interpreting efficiency (e.g. "Cluster was 72% allocated; 18% idle suggests moderate underutilization").
