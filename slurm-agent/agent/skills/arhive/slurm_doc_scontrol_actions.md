# Slurm Official: scontrol Actions

**When to use:** User asks to hold, release, requeue, update, or inspect individual jobs.
**Official source:** https://slurm.schedmd.com/scontrol.html
**Refreshed:** 2026-04-19 04:03:51 UTC

## Fast Path
- Use scontrol hold/release/requeue for direct job state control.
- Use scontrol show job <id> for targeted verification and diagnosis.
- Use scontrol update with explicit JobId and key=value fields.

## Canonical Examples
```bash
scontrol hold 1004
scontrol release 1004
scontrol requeue 1004
scontrol show job 1004
scontrol update JobId=1004 Priority=5000
```

## Retrieved Notes
- Slurm Workload Manager - scontrol
- - Release Notes
- scontrol
- Updated: Slurm Commands
- scontrol - view or modify Slurm configuration and state.
- scontrol [ OPTIONS ...] [ COMMAND ...]
- scontrol is used to view or modify Slurm configuration including: job,
- job step, node, partition, reservation, and overall system configuration. Most
- If no command is entered on the execute line, scontrol will operate in an
- execute line, scontrol will execute that command and terminate. All
- a file using the scontrol write config command. The resulting file
- -a , --all When the show command is used, then display all partitions, their jobs

## Agent Usage
- Use these patterns as primary guidance for command selection and flags.
- If needed, run web_search with: site:slurm.schedmd.com <topic>.
