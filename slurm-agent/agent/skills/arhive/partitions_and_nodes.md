# Partition and Node Management

**When to use:** User asks about partitions, node states, drained/down nodes, or resource availability.

## Node States
| State | Meaning |
|-------|---------|
| `idle` | Available, no jobs running |
| `alloc` / `allocated` | Fully allocated to jobs |
| `mix` / `mixed` | Some CPUs allocated, some free |
| `down` | Not responding or marked down by admin |
| `drain` / `drained` | Marked for maintenance — running jobs finish, new jobs rejected |
| `drng` / `draining` | Drain in progress — still has running jobs |
| `fail` / `failing` | Node detected failure |
| `unk` / `unknown` | Slurm can't contact slurmctld |
| `plnd` / `planned` | Busy but free resources have been reserved for a pending job |
| `comp` / `completing` | Jobs running but about to finish |
| `resv` / `reserved` | Reserved for advanced reservation |
| `pow_dn` / `powered_down` | Powered off (cloud/power-saving) |
| `pow_up` / `powering_up` | Coming online |

## Steps
1. Call `sinfo()` for partition/node overview.
2. For specific node: `scontrol_show(entity="node", id=<nodename>)`.
3. For partition details: `scontrol_show(entity="partition", id=<partition>)`.
4. If node is `drain*`, check the Reason field — admin left a message.
5. If user needs to drain: `scontrol_update(entity="node", id=<node>, params="State=DRAIN Reason='maintenance'")`.
6. To resume: `scontrol_update(entity="node", id=<node>, params="State=RESUME")`.

## Partition Properties
- **Default**: one partition is marked default (`*` suffix in sinfo).
- **MaxTime**: maximum job walltime allowed.
- **MaxNodes**: max nodes per job.
- **AllowGroups**: restrict access to specific Unix groups.
- **PreemptMode**: whether jobs can be preempted.
- **OverSubscribe**: whether node-sharing is allowed.

## CPUS(A/I/O/T) Format
In `sinfo`: Allocated/Idle/Other/Total. Example: `16/48/0/64` = 16 used, 48 free, 64 total.

## Output Format
Node/partition table with state summary and actionable interpretation.
