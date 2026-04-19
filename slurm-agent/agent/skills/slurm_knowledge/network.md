---
source_url: https://slurm.schedmd.com/network.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:21:21 UTC
title: "Slurm Workload Manager - Network Configuration Guide"
---

# Network Configuration Guide
## Contents[#contents](https://slurm.schedmd.com/network.html)
- [Overview](https://slurm.schedmd.com/network.html)
- [Communication for slurmctld](https://slurm.schedmd.com/network.html)
- [Communication for slurmdbd](https://slurm.schedmd.com/network.html)
- [Communication for slurmd](https://slurm.schedmd.com/network.html)
- [Communication for client commands](https://slurm.schedmd.com/network.html)
- [Communication for multiple controllers](https://slurm.schedmd.com/network.html)
- [Communication with multiple clusters](https://slurm.schedmd.com/network.html)
- [Communication in a federation](https://slurm.schedmd.com/network.html)
- [Communication with IPv6](https://slurm.schedmd.com/network.html)
## Overview[#overview](https://slurm.schedmd.com/network.html)
There are a lot of components in a Slurm cluster that need to be able
to communicate with each other. Some sites have security requirements that
prevent them from opening all communications between the machines and will
need to be able to selectively open just the ports that are necessary.
This document will go over what is needed for different components to be
able to talk to each other.
Slurm requires IP connectivity bidirectionally between all hosts in each
cluster and from any hosts where srun may be run (such as login nodes). The
ports listed below must be opened in any firewalls. If IP communications are
blocked then Slurm will not be able to fully function, potentially resulting
in failed jobs, node problems, command timeouts or other problems.
Below is a diagram of a fairly typical cluster, with slurmctld
and slurmdbd on separate machines. In smaller clusters, MySQL can run
on the same machine as the slurmdbd , but in most cases it is preferable
to have it run on a dedicated machine. slurmd runs on the
compute nodes and the client commands can be installed and run from machines
of your choosing.
Typical configuration
## Communication for slurmctld [#slurmctld](https://slurm.schedmd.com/network.html)
The default port used by slurmctld to listen for incoming requests
is 6817 . This port can be changed with the
[SlurmctldPort](https://slurm.schedmd.com/slurm.conf.html) slurm.conf
parameter. Slurmctld listens for incoming requests on that port and responds
back on the same connection opened by the requester.
The machine running slurmctld needs to be able to establish
outbound connections as well. It needs to communicate with slurmdbd
on port 6819 by default (see the [slurmdbd](https://slurm.schedmd.com/network.html)
section for information on how to change this). It also needs to communicate
with slurmd on the compute nodes on port 6818 by default (see the
[slurmd](https://slurm.schedmd.com/network.html) section for information on how to change
this).
By default, the slurmctld will listen for IPv4 traffic. IPv6
communication can be enabled by adding EnableIPv6 to the
[CommunicationParameters](https://slurm.schedmd.com/slurm.conf.html) in your slurm.conf. With IPv6 enabled, you can
disable IPv4 by adding DisableIPv4 to the
[CommunicationParameters](https://slurm.schedmd.com/slurm.conf.html). These settings must match in both slurmdbd.conf
and slurm.conf (see the [slurmdbd](https://slurm.schedmd.com/network.html) section).
## Communication for slurmdbd [#slurmdbd](https://slurm.schedmd.com/network.html)
The default port used by slurmdbd to listen for incoming requests
is 6819 . This port can be changed with the
[DbdPort](https://slurm.schedmd.com/slurmdbd.conf.html) slurmdbd.conf parameter.
Slurmdbd listens for incoming requests on that port and responds back
on the same connection opened by the requester.
The machine running slurmdbd needs to be able to reach the
MySQL or MariaDB server on port 3306 by default (the port is
configurable on the database side).
This port can be changed with the
[StoragePort](https://slurm.schedmd.com/slurmdbd.conf.html) slurmdbd.conf
parameter. It also needs to be able to initiate
a connection to slurmctld on port 6819 by default (see the
[slurmctld](https://slurm.schedmd.com/network.html) section for information on how to
change this).
By default, the slurmdbd will listen for IPv4 traffic. IPv6
communication can be enabled by adding EnableIPv6 to the
[CommunicationParameters](https://slurm.schedmd.com/slurmdbd.conf.html) in your slurmdbd.conf. With IPv6 enabled, you can
disable IPv4 by adding DisableIPv4 to the
[CommunicationParameters](https://slurm.schedmd.com/slurmdbd.conf.html). These settings must match in both slurmdbd.conf
and slurm.conf (see the [slurmctld](https://slurm.schedmd.com/network.html) section).
## Communication for slurmd [#slurmd](https://slurm.schedmd.com/network.html)
The default port used by slurmd to listen for incoming requests
from slurmctld is 6818 . This port can be changed with the
[SlurmdPort](https://slurm.schedmd.com/slurm.conf.html) slurm.conf
parameter.
The machines running srun also use a range of ports to be able
to communicate with slurmstepd . By default these ports are chosen
at random from the ephemeral port range, but you can use the
[SrunPortRange](https://slurm.schedmd.com/slurm.conf.html) to specify
a range of ports from which they can be chosen. This is necessary
for login nodes that are behind a firewall.
The machines running slurmd need to be able to establish
connections with slurmctld on port 6817 by default (see
the [slurmctld](https://slurm.schedmd.com/network.html) section for information on how to
change this).
By default, the slurmd communicates over IPv4. Please see the
[slurmctld](https://slurm.schedmd.com/network.html) section for details on how to change this
as the slurm.conf parameter affects slurmd daemons as well.
## Communication for client commands [#client](https://slurm.schedmd.com/network.html)
The majority of the client commands will communicate with slurmctld
on port 6817 by default (see the [slurmctld](https://slurm.schedmd.com/network.html)
section for information on how to change this) to get the information they
need. This includes the following commands:
salloc
sacctmgr
sbatch
sbcast
scancel
scontrol
sdiag
sinfo
sprio
squeue
sshare
sstat
strigger
sview
There are also commands that communicate directly with slurmdbd on
port 6819 by default (see the [slurmdbd](https://slurm.schedmd.com/network.html) section
for information on how to change this). The following commands get information
from slurmdbd :
sacct
sacctmgr
sreport
When a user starts a job using srun there has to be a communication
path from the machine where srun is called to the node(s) the job is
allocated. Communication follows the sequence outlined below:
1a. srun sends job allocation request to slurmctld
1b. slurmctld grants allocation and returns details
2a. srun sends step create request to slurmctld
2b. slurmctld responds with step credential
3. srun opens sockets for I/O
4. srun forwards credential with task info to slurmd
5. slurmd forwards request as needed (per fanout)
6. slurmd forks/execs slurmstepd
7. slurmstepd connects I/O and launches tasks
8. On task termination, slurmstepd notifies srun
9. srun notifies slurmctld of job termination
10. slurmctld verifies termination of all processes via slurmd and
releases resources for next job
srun communication
## Communication with multiple controllers [#failover](https://slurm.schedmd.com/network.html)
You can configure a secondary slurmctld and/or slurmdbd to
serve as a fallback if the primary should go down. The ports involved don't
change, but there are additional communication paths that need to be taken
into consideration. The client commands need to be able to reach both
machines running slurmctld as well as both machines running
slurmdbd . Both instances of slurmctld need to be able to
reach both instances of slurmdbd and each slurmdbd needs
to be able to reach the MySQL server.
Fallback slurmctld and slurmdbd
## Communication with multiple clusters [#multi](https://slurm.schedmd.com/network.html)
In environments where multiple slurmctld instances share the same
slurmdbd you can configure each cluster to stand on their own and allow
users to specify a cluster to submit their jobs to. Ports
used by the different daemons don't change, but all instances of
slurmctld need to be able to communicate with the same instance of
slurmdbd . You can read more about multi cluster configurations in the
[Multi-Cluster Operation](https://slurm.schedmd.com/multi_cluster.html)
documentation.
Multi-Cluster configuration
## Communication in a federation [#federation](https://slurm.schedmd.com/network.html)
Slurm also provides the ability to schedule jobs in a peer-to-peer fashion
between multiple clusters, allowing jobs to run on the cluster that has
available resources first. The difference in communication needs between this
and a multi-cluster configuration is that the two instances of slurmctld
need to be able to communicate with each other. There are more details about
using a
[Federation](https://slurm.schedmd.com/federation.html) in the
documentation.
Federation configuration
## Communication with IPv6 [#ipv6](https://slurm.schedmd.com/network.html)
The slurmctld , slurmdbd , and slurmd daemons will,
by default, communicate using IPv4, but they can be configured to use IPv6.
This is handled by setting CommunicationParameters=EnableIPv6
in your slurm.conf and slurmdbd.conf, then restarting all of the daemons.
The slurmd may operate over IPv4 OR IPv6 in this mode. IPv4 can be
disabled by setting CommunicationParameters=EnableIPv6,DisableIPv4 .
In is mode, everything must have a valid IPv6 address or the connection will
fail.
The slurmctld expects a node to map to a single IP address (which
will be the first address returned when looking up the IP of the node with
getaddrinfo() ). If you enable IPv6 on an existing cluster and the
nodes have IPv6 addresses, you must restart the slurmd daemons for
communication over IPv6 to be established.
The presence of precedence ::ffff:0:0/96 100 in /etc/gai.conf
will cause IPv4 addresses to be returned BEFORE an IPv6 address. This might
cause a situation where you have enabled IPv6 for Slurm, but are still seeing nodes
communicate with IPv4. If there is confusion as to which address is being used
you can call scontrol setdebugflags +NET to enable network related
debug logging in your slurmctld.log.
If IPv4 and IPv6 are enabled, the loopback interface may still resolve to
127.0.0.1. This is not necessarily an indication of a problem.
