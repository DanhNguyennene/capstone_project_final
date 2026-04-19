# Account and User Usage Report

**When to use:** User asks about who is using the cluster, usage by account/group/user, billing, or wants to audit accounting data.

## Key Concepts
- Slurm accounting uses a hierarchy: `cluster → account → user`.
- `sacctmgr_list` reads current configuration (limits, QOS allocations).
- `sreport` reads historical usage from the accounting database.
- Associations = (cluster, account, user, partition) tuples that define who can run what.

## Steps

### Show all users and their default accounts
```
sacctmgr_list(entity="user", params="format=User,DefaultAccount,AdminLevel WithAssoc")
```

### Show account hierarchy
```
sacctmgr_list(entity="account", params="format=Account,Description,Organization WithAssoc Tree")
```

### Show all associations (limits per user/account)
```
sacctmgr_list(entity="assoc", params="format=Cluster,Account,User,Partition,QOS,MaxTRESPJ,MaxWall,FairShare")
```

### Show QOS list with limits
```
sacctmgr_list(entity="qos", params="format=Name,Priority,MaxTRESPJ,MaxWall,GrpTRES,GrpJobs,UsageFactor")
```

### Historical usage by account (last 7 days)
```
sreport(report_type="cluster AccountUtilizationByUser", params="Start=now-7days End=now")
```

### Top 10 users by CPU usage
```
sreport(report_type="user topusage", params="Start=now-7days End=now TopCount=10")
```

### Usage for a specific user or account
```
sreport(report_type="cluster AccountUtilizationByUser", params="Start=now-30days End=now users=<user>")
sreport(report_type="cluster AccountUtilizationByUser", params="Start=now-30days End=now account=<account>")
```

### Check TRES usage (CPU, GPU separately)
```
sreport(report_type="user topusage", params="Start=now-7days --tres=cpu,gres/gpu")
```

## Output Format
Show a table of Account | User | CPU-Minutes Used | % of Cluster, sorted by usage descending.
If limits are involved, note associations where users are near or over `MaxTRESPJ` or `GrpTRES`.
