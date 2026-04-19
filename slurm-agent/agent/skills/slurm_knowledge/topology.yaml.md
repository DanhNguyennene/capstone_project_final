---
source_url: https://slurm.schedmd.com/topology.yaml.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:32 UTC
title: "Slurm Workload Manager - topology.yaml"
---

# topology.yaml
Section: Slurm Configuration File (5)
Updated: Slurm Configuration File
[Index](https://slurm.schedmd.com/topology.yaml.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/topology.yaml.html)
topology.yaml - Slurm configuration file for the topology plugins
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/topology.yaml.html)
topology.yaml is a YAML-formatted configuration file that defines
multiple network topologies for optimizing job resource allocation in Slurm.
The file must be located in the same directory as slurm.conf . Any text
following a "#" in this file is treated as a comment through the end of that
line.
Additional details are available in [topology.conf](https://slurm.schedmd.com/topology.conf.html) (5) and in the
Topology Guide: <[https://slurm.schedmd.com/topology.html](https://slurm.schedmd.com/topology.html)>
NOTE : Slurm will first check for topology.yaml.
If this file exists, topology.conf will be ignored.
## PARAMETERS[#SECTION_PARAMETERS](https://slurm.schedmd.com/topology.yaml.html)
Each topology contains the following attributes:
topology [#OPT_topology](https://slurm.schedmd.com/topology.yaml.html) Unique name of the topology, will be used to identify it on partition
configurations. Must be the first attribute.
cluster_default [#OPT_cluster_default](https://slurm.schedmd.com/topology.yaml.html) The first topology defined with cluster_default: true will be used for
partitions without an explicitly specified topology and cluster-wide operations
not tied to a partition (e.g., slurmctld-to-slurmd communication). Defaults to
false .
Each topology must also define exactly one of the following topology types:
block [#OPT_block](https://slurm.schedmd.com/topology.yaml.html) This topology will use the topology/block plugin. Must contain additional
fields, see below.
flat [#OPT_flat](https://slurm.schedmd.com/topology.yaml.html) If set to true , this topology will use the topology/flat plugin,
which is the default if no TopologyPlugin or topology.yaml is specified.
tree [#OPT_tree](https://slurm.schedmd.com/topology.yaml.html) This topology will use the topology/tree plugin. Must contain additional
fields, see below.
### Block definitions[#SECTION_Block-definitions](https://slurm.schedmd.com/topology.yaml.html)
Each block topology contains the following attributes:
block_sizes [#OPT_block_sizes](https://slurm.schedmd.com/topology.yaml.html) List of the planning base block size, alongside any
higher-level block sizes that would be enforced.
Successive BlockSizes must be a power of two larger than the prior values.
blocks [#OPT_blocks](https://slurm.schedmd.com/topology.yaml.html) List of blocks available in this topology. Each block contains the following
attributes:
block [#OPT_block_1](https://slurm.schedmd.com/topology.yaml.html) The name of a block. This name is internal to Slurm and arbitrary.
Each block should have a unique name.
This field must be specified.
nodes [#OPT_nodes](https://slurm.schedmd.com/topology.yaml.html) Child nodes of the named block.
### Tree definitions[#SECTION_Tree-definitions](https://slurm.schedmd.com/topology.yaml.html)
Each tree topology contains the following attribute:
switches [#OPT_switches](https://slurm.schedmd.com/topology.yaml.html) List of switches available in this topology. Each switch contains the following
attributes:
switch [#OPT_switch](https://slurm.schedmd.com/topology.yaml.html) The name of a switch. This name is internal to Slurm and arbitrary.
Each switch should have a unique name.
This field must be specified and cannot be longer than 64 characters.
children [#OPT_children](https://slurm.schedmd.com/topology.yaml.html) Child switches of the named switch.
nodes [#OPT_nodes_1](https://slurm.schedmd.com/topology.yaml.html) Child nodes of the named leaf switch.
## EXAMPLE[#SECTION_EXAMPLE](https://slurm.schedmd.com/topology.yaml.html)
```text
--- - topology: topo1 cluster_default: true tree: switches: - switch: sw_root children: s[1-2] - switch: s1 nodes: node[01-02] - switch: s2 nodes: node[03-04] - topology: topo2 cluster_default: false block: block_sizes: - 4 - 16 blocks: - block: b1 nodes: node[01-04] - block: b2 nodes: node[05-08] - block: b3 nodes: node[09-12] - block: b4 nodes: node[13-16] - topology: topo3 cluster_default: false flat: true
```
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/topology.yaml.html)
Copyright (C) 2025 SchedMD LLC.
This file is part of Slurm, a resource management program.
For details, see <[https://slurm.schedmd.com/](https://slurm.schedmd.com/)>.
Slurm is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation; either version 2 of the License, or (at your option)
any later version.
Slurm is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/topology.yaml.html)
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5), [topology.conf](https://slurm.schedmd.com/topology.conf.html) (5)
## Index
[NAME](https://slurm.schedmd.com/topology.yaml.html)
[DESCRIPTION](https://slurm.schedmd.com/topology.yaml.html)
[PARAMETERS](https://slurm.schedmd.com/topology.yaml.html)
[Block definitions](https://slurm.schedmd.com/topology.yaml.html)
[Tree definitions](https://slurm.schedmd.com/topology.yaml.html)
[EXAMPLE](https://slurm.schedmd.com/topology.yaml.html)
[COPYING](https://slurm.schedmd.com/topology.yaml.html)
[SEE ALSO](https://slurm.schedmd.com/topology.yaml.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
