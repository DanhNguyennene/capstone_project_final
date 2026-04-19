---
source_url: https://slurm.schedmd.com/topology.conf.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:32 UTC
title: "Slurm Workload Manager - topology.conf"
---

# topology.conf
Section: Slurm Configuration File (5)
Updated: Slurm Configuration File
[Index](https://slurm.schedmd.com/topology.conf.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/topology.conf.html)
topology.conf - Slurm configuration file for the topology plugins
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/topology.conf.html)
topology.conf is an ASCII file which describes the
cluster's network topology for optimized job resource allocation.
The file will always be located in the same directory as the slurm.conf .
NOTE : This file is ignored if [topology.yaml](https://slurm.schedmd.com/topology.yaml.html) (5) exists.
Parameter names are case insensitive.
Any text following a "#" in the configuration file is treated
as a comment through the end of that line.
Changes to the configuration file take effect upon restart of
Slurm daemons, daemon receipt of the SIGHUP signal, or execution
of the command "scontrol reconfigure" unless otherwise noted.
Refer to the topology guide for more details:
<[https://slurm.schedmd.com/topology.html](https://slurm.schedmd.com/topology.html)>
## topology/tree[#SECTION_topology/tree](https://slurm.schedmd.com/topology.conf.html)
This plugin requires you to use the select/cons_tres plugin.
The network topology configuration, each line defining a switch name and
its children, either node names or switch names.
Slurm's hostlist expression parser is used, so the node and switch
names need not be consecutive (e.g. "Nodes=tux[0-3,12,18-20]"
and "Switches=s[0-2,4-8,12]" will parse fine).
An optional link speed may also be specified.
All nodes in the
network must be connected to at least one switch. The network must be fully
connected to use TopologyParam=RouteTree . Jobs can only span nodes
connected by the same switch fabric, even if there are available idle nodes
in other areas of the cluster.
The topology.conf file for an Infiniband switch can be
automatically generated using the slurmibtopology tool found here:
<[https://github.com/OleHolmNielsen/Slurm_tools/tree/master/slurmibtopology](https://github.com/OleHolmNielsen/Slurm_tools/tree/master/slurmibtopology)>.
The overall configuration parameters available for topology/tree include:
SwitchName [#OPT_SwitchName](https://slurm.schedmd.com/topology.conf.html) The name of a switch. This name is internal to Slurm and arbitrary.
Each switch should have a unique name.
This field must be specified and cannot be longer than 64 characters.
Switches [#OPT_Switches](https://slurm.schedmd.com/topology.conf.html) Child switches of the named switch.
Nodes [#OPT_Nodes](https://slurm.schedmd.com/topology.conf.html) Child nodes of the named leaf switch.
LinkSpeed [#OPT_LinkSpeed](https://slurm.schedmd.com/topology.conf.html) An optional value specifying the performance of this communication link.
The units used are arbitrary and this information is currently not used.
It may be used in the future to optimize resource allocations.
## topology/block[#SECTION_topology/block](https://slurm.schedmd.com/topology.conf.html)
The network topology configuration, each line defining a block name and
its children node names.
Slurm's hostlist expression parser is used, so the node
names need not be consecutive (e.g. "Nodes=tux[0-3,12,18-20]").
This topology plugin places emphasis on reducing fragmentation of the
cluster, allowing jobs to take advantage of lower-latency connections
between smaller "blocks" of nodes, rather than starting jobs as quickly
as possible on the first available resources.
Defined blocks of nodes are paired with other contiguous blocks, to create
a higher level block of nodes. These larger blocks can then be paired with
other blocks at the same level for bigger and bigger blocks of contiguous
nodes with optimized communication between them. The enforced block sizes
are defined by BlockSizes .
The overall configuration parameters available for topology/block include:
BlockName [#OPT_BlockName](https://slurm.schedmd.com/topology.conf.html) The name of a block. This name is internal to Slurm and arbitrary.
Each block should have a unique name.
This field must be specified.
Nodes [#OPT_Nodes_1](https://slurm.schedmd.com/topology.conf.html) Child nodes of the named block.
BlockSizes [#OPT_BlockSizes](https://slurm.schedmd.com/topology.conf.html) List of the planning base block size, alongside any
higher-level block sizes that would be enforced.
Each block must have at least the planning base block size count of nodes.
Successive BlockSizes must be a power of two larger than the prior values.
## EXAMPLE[#SECTION_EXAMPLE](https://slurm.schedmd.com/topology.conf.html)
```text
################################################################## # Slurm's network topology configuration file for use with the # topology/tree plugin ################################################################## SwitchName=s0 Nodes=dev[0-5] SwitchName=s1 Nodes=dev[6-11] SwitchName=s2 Nodes=dev[12-17] SwitchName=s3 Switches=s[0-2]
```
```text
################################################################## # Slurm's network topology configuration file for use with the # topology/block plugin ################################################################## BlockName=block1 Nodes=node[1-32] BlockName=block2 Nodes=node[33-64] BlockName=block3 Nodes=node[65-96] BlockName=block4 Nodes=node[97-128] BlockSizes=30,120
```
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/topology.conf.html)
Copyright (C) 2009 Lawrence Livermore National Security.
Produced at Lawrence Livermore National Laboratory (cf, DISCLAIMER).
Copyright (C) 2010-2023 SchedMD LLC.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/topology.conf.html)
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5), [topology.yaml](https://slurm.schedmd.com/topology.yaml.html) (5)
## Index
[NAME](https://slurm.schedmd.com/topology.conf.html)
[DESCRIPTION](https://slurm.schedmd.com/topology.conf.html)
[topology/tree](https://slurm.schedmd.com/topology.conf.html)
[topology/block](https://slurm.schedmd.com/topology.conf.html)
[EXAMPLE](https://slurm.schedmd.com/topology.conf.html)
[COPYING](https://slurm.schedmd.com/topology.conf.html)
[SEE ALSO](https://slurm.schedmd.com/topology.conf.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
