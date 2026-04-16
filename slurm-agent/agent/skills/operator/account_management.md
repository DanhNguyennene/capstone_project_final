# Account and User Management

**When to use:** You are asked to create, modify, or delete Slurm accounts, users, or associations; or to change limits/QOS on an existing account or user.

## Available Tools
- `sacctmgr_add(entity, params)` — create account/user/QOS
- `sacctmgr_modify(entity, where, params)` — update limits/QOS on existing entity
- `sacctmgr_delete(entity, params)` — remove an account/user
- `scontrol_show(entity="assoc_mgr")` — verify live cache after changes

## Important Rules
- Order: create **cluster** → **account** → **user** (cluster must pre-exist).
- A user needs an association to submit jobs; creating the user also creates an association.
- Use `--immediate` flag (already added by the tool) — no interactive confirmation needed.
- Deleting an account removes all its user associations on that account.

## Workflows

### Create a new account
```
sacctmgr_add(entity="account", params="name=<acct> Description='<desc>' Organization='<org>'")
```
Optional: add limits `MaxTRESPJ=cpu=64,gres/gpu=2 MaxWall=24:00:00 FairShare=100`

### Add a user to an account
```
sacctmgr_add(entity="user", params="name=<user> Account=<acct> DefaultAccount=<acct>")
```
Optional: `Partition=<partition> MaxTRESPJ=cpu=16 AdminLevel=Operator`

### Modify limits on an account
```
sacctmgr_modify(entity="account", where="name=<acct>", params="MaxTRESPJ=cpu=128,gres/gpu=4 MaxWall=48:00:00")
```

### Modify limits on a user
```
sacctmgr_modify(entity="user", where="name=<user> account=<acct>", params="MaxTRESPJ=cpu=32 MaxWall=24:00:00")
```
To clear a limit: `MaxTRESPJ=cpu=-1`

### Add QOS to a user/account
```
sacctmgr_modify(entity="user", where="name=<user>", params="QosLevel+=<qos_name>")
```
Remove: `QosLevel-=<qos_name>`. Replace: `QosLevel=<qos_name>`.

### Change user's admin level
```
sacctmgr_modify(entity="user", where="name=<user>", params="AdminLevel=Operator")
```
Levels: `None`, `Operator`, `Administrator`

### Delete a user from an account
```
sacctmgr_delete(entity="user", params="name=<user> account=<acct>")
```

### Delete an account
```
sacctmgr_delete(entity="account", params="name=<acct>")
```
Warning: removes all user associations under the account.

## After Changes
Verify via `scontrol_show(entity="assoc_mgr", id="accounts=<acct>")`.
Report: entity | action | result in a markdown table.
