---
source_url: https://slurm.schedmd.com/dynamic_nodes.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:20:59 UTC
title: "Slurm Workload Manager - Dynamic Nodes"
---

# Dynamic Nodes
## Overview[#overview](https://slurm.schedmd.com/dynamic_nodes.html)
Starting in Slurm 22.05, nodes can be dynamically added and removed from
Slurm.
## Dynamic Node Communications [#communications](https://slurm.schedmd.com/dynamic_nodes.html)
For regular, non-dynamically created nodes, Slurm knows how to communicate with
nodes by reading in the slurm.conf. This is why it is important for a
non-dynamic setup that the slurm.conf is synchronized across the cluster. For
dynamically created nodes, The controller automatically grabs the node's
NodeAddr and NodeHostname for dynamic slurmd registrations. The
controller then passes the node addresses to the clients so that they
communicate, and even fanout, to other nodes.
## Slurm Configuration [#config](https://slurm.schedmd.com/dynamic_nodes.html)
MaxNodeCount=#
Set to the number of possible nodes that can be active in a system at a time.
See the slurm.conf [man](https://slurm.schedmd.com/slurm.conf.html) page for
more details.
SelectType=select/cons_tres
Dynamic nodes are only supported with cons_tres.
### Partition Assignment [#partitions](https://slurm.schedmd.com/dynamic_nodes.html)
Dynamic nodes can be automatically assigned to partitions at creation by using
the partition's nodes [ALL](https://slurm.schedmd.com/slurm.conf.html) keyword or
[NodeSets](https://slurm.schedmd.com/slurm.conf.html) and
specifying a feature on the nodes.
e.g.
```text
Nodeset=ns1 Feature=f1 Nodeset=ns2 Feature=f2 PartitionName=all Nodes=ALL Default=yes PartitionName=dyn1 Nodes=ns1 PartitionName=dyn2 Nodes=ns2 PartitionName=dyn3 Nodes=ns1,ns2
```
## Creating Nodes [#create](https://slurm.schedmd.com/dynamic_nodes.html)
Nodes can be created two ways:
- Dynamic slurmd registration Using the slurmd [-Z](https://slurm.schedmd.com/slurmd.html) and [--conf](https://slurm.schedmd.com/slurmd.html) options a slurmd will register with the controller and will automatically be added to the system. e.g. ```text slurmd -Z --conf "RealMemory=80000 Gres=gpu:2 Feature=f1" ```
- scontrol create NodeName= ... Create nodes using scontrol by specifying the same NodeName line that you would define in the slurm.conf. See slurm.conf [man](https://slurm.schedmd.com/slurm.conf.html) page for node options. Only State=CLOUD and State=FUTURE are supported. The node configuration should match what the slurmd will register with (e.g. slurmd -C) plus any additional attributes. e.g. ```text scontrol create NodeName=d[1-100] CPUs=16 Boards=1 SocketsPerBoard=1 CoresPerSocket=8 ThreadsPerCore=2 RealMemory=31848 Gres=gpu:2 Feature=f1 State=cloud ```
## Deleting Nodes [#delete](https://slurm.schedmd.com/dynamic_nodes.html)
Nodes can be deleted using scontrol delete nodename=<nodelist> .
Only dynamic nodes that have no running jobs and that are not part of a
reservation can be deleted.
## Topology [#topology](https://slurm.schedmd.com/dynamic_nodes.html)
Nodes can be dynamically added to and removed from topologies as described in
the [Topology Guide](https://slurm.schedmd.com/topology.html).
## Limitations [#limitations](https://slurm.schedmd.com/dynamic_nodes.html)
- Dynamic nodes are not sorted internally and when added to Slurm they will potentially be alphabetically out of order internally — leading to suboptimal job allocations if node names represent topology of the nodes.
