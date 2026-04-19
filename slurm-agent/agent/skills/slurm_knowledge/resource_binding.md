---
source_url: https://slurm.schedmd.com/resource_binding.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:21:39 UTC
title: "Slurm Workload Manager - Resource Binding"
---

# Resource Binding
- [Overview](https://slurm.schedmd.com/resource_binding.html)
- [Srun --cpu-bind option](https://slurm.schedmd.com/resource_binding.html)
- [Node CpuBind Configuration](https://slurm.schedmd.com/resource_binding.html)
- [Partition CpuBind Configuration](https://slurm.schedmd.com/resource_binding.html)
- [TaskPluginParam Configuration](https://slurm.schedmd.com/resource_binding.html)
## Overview[#overview](https://slurm.schedmd.com/resource_binding.html)
Slurm has a rich set of options to control the default
binding of tasks to resources.
For example, tasks can be bound to individual threads, cores, sockets, NUMA
or boards.
See the slurm.conf and srun man pages for more information about how these
options work.
This document focuses on how default binding configuration can be configured.
Default binding can be configured on a per-node, per-partition or global
basis. The highest priority will be that specified using the srun
[--cpu-bind](https://slurm.schedmd.com/srun.html) option.
The next highest priority binding will be the node-specific binding, if any
node in the job allocation has some [CpuBind](https://slurm.schedmd.com/slurm.conf.html) configuration parameter and all other nodes in the job
allocation either have the same or no CpuBind configuration parameter.
The next highest priority binding will be the partition-specific
[CpuBind](https://slurm.schedmd.com/slurm.conf.html) configuration
parameter (if any).
The lowest priority binding will be that specified by the
[TaskPluginParam](https://slurm.schedmd.com/slurm.conf.html)
configuration parameter.
Summary of the order of enforcement:
- Srun --cpu-bind option
- Node CpuBind configuration parameter (if all nodes match)
- Partition CpuBind configuration parameter
- TaskPluginParam configuration parameter
## Srun --cpu-bind option[#srun](https://slurm.schedmd.com/resource_binding.html)
The srun [--cpu-bind](https://slurm.schedmd.com/srun.html) option will always
be used to control task binding. If the --cpu-bind option only includes
"verbose" rather than identifying the entities to be bound to, then the verbose
option will be used together with the default entity based upon Slurm
configuration parameters as described below.
## Node CpuBind Configuration [#node](https://slurm.schedmd.com/resource_binding.html)
The next possible source of the resource binding information is the node's
configured [CpuBind](https://slurm.schedmd.com/slurm.conf.html) value, but only
if every node has the same CpuBind value (or no configured CpuBind value).
The node's CpuBind value is configured in the slurm.conf file.
Its value may be viewed or modified using the scontrol command.
To clear a node's CpuBind value use the command:
```text
scontrol update NodeName=node01 CpuBind=off
```
## Partition CpuBind Configuration [#partition](https://slurm.schedmd.com/resource_binding.html)
The next possible source of the resource binding information is the
partition's configured [CpuBind](https://slurm.schedmd.com/slurm.conf.html)
value. The partition's CpuBind value is configured in the slurm.conf file.
Its value may be viewed or modified using the scontrol command, similar to how
a node's CpuBind value is changed:
```text
scontrol update PartitionName=debug CpuBind=cores
```
## TaskPluginParam Configuration [#TaskPluginParam](https://slurm.schedmd.com/resource_binding.html)
The last possible source of the resource binding information is the
[TaskPluginParam](https://slurm.schedmd.com/slurm.conf.html)
configuration parameter from the slurm.conf file.
