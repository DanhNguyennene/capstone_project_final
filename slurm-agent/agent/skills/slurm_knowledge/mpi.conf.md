---
source_url: https://slurm.schedmd.com/mpi.conf.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:16 UTC
title: "Slurm Workload Manager - mpi.conf"
---

# mpi.conf
Section: Slurm Configuration File (5)
Updated: Slurm Configuration File
[Index](https://slurm.schedmd.com/mpi.conf.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/mpi.conf.html)
mpi.conf - Slurm configuration file to allow the configuration of MPI plugins.
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/mpi.conf.html)
mpi.conf is an ASCII file which defines parameters that control the
behavior of MPI plugins. Currently the configuration file can only be used
to configure the PMIx plugin, but it can be extended to support other MPI
plugins as well. The file will always be located in the same directory as
the slurm.conf . This file is optional.
Parameter names are case insensitive. Any text following a "#" in the
configuration file is treated as a comment through the end of that line.
Changes to the configuration file take effect upon restart of Slurm daemons,
daemon receipt of the SIGHUP signal, or execution of the command "scontrol
reconfigure" unless otherwise noted.
Settings from this configuration file can be viewed in the output of
"scontrol show config". This configuration file can be included when using
"configless" mode. Information from mpi.conf is read at startup or upon
reconfigure by slurmctld and slurmd. Instances of slurmstepd for batch steps
will receive information about the plugin requested from slurmd.
## PARAMETERS[#SECTION_PARAMETERS](https://slurm.schedmd.com/mpi.conf.html)
PMIxCliTmpDirBase =< path >[#OPT_PMIxCliTmpDirBase](https://slurm.schedmd.com/mpi.conf.html) Directory to have PMIx use for temporary files.
Defaults to not being set.
PMIxCollFence ={mixed|tree|ring}[#OPT_PMIxCollFence](https://slurm.schedmd.com/mpi.conf.html) Define the type of fence to use for collecting inter-node data.
Defaults to not being set. See also PMIxFenceBarrier .
PMIxDebug ={0|1}[#OPT_PMIxDebug](https://slurm.schedmd.com/mpi.conf.html) Enable debug logging for the PMIx plugin.
Defaults to 0.
PMIxDirectConn ={true|false}[#OPT_PMIxDirectConn](https://slurm.schedmd.com/mpi.conf.html) Disable direct launching of tasks. Default is "true".
PMIxDirectConnEarly ={true|false}[#OPT_PMIxDirectConnEarly](https://slurm.schedmd.com/mpi.conf.html) Allow early connections to a parent node.
Defaults to "false".
PMIxDirectConnUCX ={true|false}[#OPT_PMIxDirectConnUCX](https://slurm.schedmd.com/mpi.conf.html) Allow PMIx to use UCX for communication.
Defaults to "false".
PMIxDirectSameArch ={true|false}[#OPT_PMIxDirectSameArch](https://slurm.schedmd.com/mpi.conf.html) Enable additional communication optimizations when PMIxDirectConn is
set to true, assuming all the job's nodes have the same architecture.
Defaults to "false".
PMIxEnv =< environment variables >[#OPT_PMIxEnv](https://slurm.schedmd.com/mpi.conf.html) Semicolon separated list of environment variables to be set in job environments
to be used by PMIx. Defaults to not being set.
PMIxFenceBarrier ={true|false}[#OPT_PMIxFenceBarrier](https://slurm.schedmd.com/mpi.conf.html) Define whether to fence inter-node communication for data collection.
Default is "false". See also PMIxCollFence .
PMIxNetDevicesUCX =< device type >[#OPT_PMIxNetDevicesUCX](https://slurm.schedmd.com/mpi.conf.html) Type of network device to use for communication. This will set the
UCX_NET_DEVICES environment variable in only the slurmstepd environment.
Defaults to not being set.
PMIxShareServerTopology ={true|false}[#OPT_PMIxShareServerTopology](https://slurm.schedmd.com/mpi.conf.html) Allow the PMIx server to share its copy of the local node topology of the job
with clients. If set to true, the PMIx server will set any necessary key-value
pairs in the job-level information provided to each client. The topology will
not be shared via shared memory.
Defaults to "false".
NOTE : This is only supported by PMIx v4.x+.
PMIxTimeout =< time >[#OPT_PMIxTimeout](https://slurm.schedmd.com/mpi.conf.html) The maximum time (in seconds) allowed for communication between hosts to
take place. Defaults to 300 seconds.
PMIxTlsUCX =< tl1 >[,< tl2 >...][#OPT_PMIxTlsUCX](https://slurm.schedmd.com/mpi.conf.html) Sets the UCX_TLS variable, which restricts the transports to use, in the
slurmstepd environment. The accepted values are defined in the UCX documentation
and may vary between installations. Multiple values can be set and must be
separated by commas. If not set, UCX tries to use all available transports and
selects the best ones according to their performance capabilities and scale.
Defaults to not being set.
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/mpi.conf.html)
Copyright (C) 2022 SchedMD LLC.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/mpi.conf.html)
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5)
## Index
[NAME](https://slurm.schedmd.com/mpi.conf.html)
[DESCRIPTION](https://slurm.schedmd.com/mpi.conf.html)
[PARAMETERS](https://slurm.schedmd.com/mpi.conf.html)
[COPYING](https://slurm.schedmd.com/mpi.conf.html)
[SEE ALSO](https://slurm.schedmd.com/mpi.conf.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
