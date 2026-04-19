---
source_url: https://slurm.schedmd.com/sbcast.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:20 UTC
title: "Slurm Workload Manager - sbcast"
---

# sbcast
Section: Slurm Commands (1)
Updated: Slurm Commands
[Index](https://slurm.schedmd.com/sbcast.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/sbcast.html)
sbcast - transmit a file to the nodes allocated to a Slurm job.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/sbcast.html)
sbcast [-CfFjpstvV] SOURCE DEST
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/sbcast.html)
sbcast is used to transmit a file to all nodes allocated
to the currently active Slurm job.
This command should only be executed from within a Slurm batch
job or within the shell spawned after a Slurm job's resource
allocation.
SOURCE is the name of a file on the current node.
DEST should be the fully qualified pathname for the
file copy to be created on each node.
If a fully qualified pathname is not provided, the file will be created in
the directory specified in the BcastParameters parameter in the slurm.conf
file (if available) otherwise it will be created in the current working
directory from which the sbcast command is invoked.
DEST should be on a file system local to that node.
Note that parallel file systems may provide better performance
than sbcast can provide, although performance will vary
by file size, degree of parallelism, and network type.
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/sbcast.html)
-C , --compress [= library ][#OPT_compress](https://slurm.schedmd.com/sbcast.html) Compress the file being transmitted.
The optional argument specifies the data compression library to be used.
Supported values are "lz4" (default) and "none".
Some compression libraries may be unavailable on some systems.
The default compression library (and enabling compression itself) may be
set in the slurm.conf file using the BcastParameters option.
--exclude =< NONE | path1 , ... , pathN >[#OPT_exclude](https://slurm.schedmd.com/sbcast.html) Comma-separated list of absolute directory paths to be excluded when
autodetecting and broadcasting executable shared object dependencies. If the
keyword " NONE " is configured, no directory paths will be excluded. The
default value is that of slurm.conf BcastExclude and this option overrides
it. See also --send-libs .
-f , --force [#OPT_force](https://slurm.schedmd.com/sbcast.html) If the destination file (and the destination library directory when using
--send-libs ) already exists, replace it.
-j , --jobid =< jobID [+ hetjobOffset ].[ stepID ]>[#OPT_jobid](https://slurm.schedmd.com/sbcast.html) Specify the job ID to use with optional hetjob offset and/or step ID. If run
inside an allocation this is unneeded as the job ID will be read from the
environment.
-Z , --no-allocation [#OPT_no-allocation](https://slurm.schedmd.com/sbcast.html) Transmit files to a list of nodes regardless of what jobs they may be running.
This can only be done by SlurmUser/root.
--nodelist must be used with this option.
-w , --nodelist =< node_name_list >[#OPT_nodelist](https://slurm.schedmd.com/sbcast.html) List of hosts to transmit files to. These nodes must be a subset of the
targeted job, or the --no-allocation option must be used.
-p , --preserve [#OPT_preserve](https://slurm.schedmd.com/sbcast.html) Preserves modification times, access times, and modes from the
original file.
--send-libs [= yes | no ][#OPT_send-libs](https://slurm.schedmd.com/sbcast.html) If set to yes (or no argument), autodetect and broadcast the executable's
shared object dependencies to allocated compute nodes. The files are placed in
a directory alongside the executable. This overrides the default behavior
configured in slurm.conf SbcastParameters send_libs . See also
--exclude .
-s , --size =< size >[#OPT_size](https://slurm.schedmd.com/sbcast.html) Specify the block size used for file broadcast.
The size can have a suffix of k or m for kilobytes
or megabytes respectively (defaults to bytes).
This size subject to rounding and range limits to maintain
good performance.
The default value is the file size or 8MB, whichever is smaller.
This value may need to be set on systems with very limited memory.
-t , --timeout =< seconds >[#OPT_timeout](https://slurm.schedmd.com/sbcast.html) Specify the message timeout in seconds.
The default value is MessageTimeout as reported by
"scontrol show config".
Setting a higher value may be necessitated by relatively slow
I/O performance on the compute node disks.
-F , --treewidth =< number >[#OPT_treewidth](https://slurm.schedmd.com/sbcast.html) Specify the treewidth of messages used for file transfer.
Maximum value is currently 64. A value of "off" disables the fanout.
-v , --verbose [#OPT_verbose](https://slurm.schedmd.com/sbcast.html) Provide detailed event logging through program execution.
-V , --version [#OPT_version](https://slurm.schedmd.com/sbcast.html) Print version information and exit.
## PERFORMANCE[#SECTION_PERFORMANCE](https://slurm.schedmd.com/sbcast.html)
Executing sbcast sends a remote procedure call to slurmctld . If
enough calls from sbcast or other Slurm client commands that send remote
procedure calls to the slurmctld daemon come in at once, it can result in
a degradation of performance of the slurmctld daemon, possibly resulting
in a denial of service.
Do not run sbcast or other Slurm client commands that send remote
procedure calls to slurmctld from loops in shell scripts or other
programs. Ensure that programs limit calls to sbcast to the minimum
necessary for the information you are trying to gather.
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/sbcast.html)
Some sbcast options may be set via environment variables.
These environment variables, along with their corresponding options,
are listed below. (Note: Command line options will always override
these settings.)
SBCAST_COMPRESS [#OPT_SBCAST_COMPRESS](https://slurm.schedmd.com/sbcast.html) -C, --compress
SBCAST_EXCLUDE [#OPT_SBCAST_EXCLUDE](https://slurm.schedmd.com/sbcast.html) --exclude =< NONE | path1 , ... , pathN >
SBCAST_FANOUT [#OPT_SBCAST_FANOUT](https://slurm.schedmd.com/sbcast.html) -F number , --fanout = number
SBCAST_FORCE [#OPT_SBCAST_FORCE](https://slurm.schedmd.com/sbcast.html) -f, --force
SBCAST_SEND_LIBS [#OPT_SBCAST_SEND_LIBS](https://slurm.schedmd.com/sbcast.html) --send-libs [= yes|no ]
SBCAST_PRESERVE [#OPT_SBCAST_PRESERVE](https://slurm.schedmd.com/sbcast.html) -p, --preserve
SBCAST_SIZE [#OPT_SBCAST_SIZE](https://slurm.schedmd.com/sbcast.html) -s size , --size = size
SBCAST_TIMEOUT [#OPT_SBCAST_TIMEOUT](https://slurm.schedmd.com/sbcast.html) -t seconds , --timeout = seconds
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/sbcast.html) The location of the Slurm configuration file.
SLURM_DEBUG_FLAGS [#OPT_SLURM_DEBUG_FLAGS](https://slurm.schedmd.com/sbcast.html) Specify debug flags for sbcast to use. See DebugFlags in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for a full list of flags. The environment
variable takes precedence over the setting in the slurm.conf.
## AUTHORIZATION[#SECTION_AUTHORIZATION](https://slurm.schedmd.com/sbcast.html)
When using SlurmDBD, users who have an AdminLevel defined (Operator
or Admin) are given the authority to invoke sbcast on other users jobs.
## EXAMPLES[#SECTION_EXAMPLES](https://slurm.schedmd.com/sbcast.html)
Using a batch script, transmit local file my.prog to
/tmp/my.proc on the local nodes and then execute it.
```text
$ cat my.job #!/bin/bash sbcast my.prog /tmp/my.prog srun /tmp/my.prog $ sbatch --nodes=8 my.job srun: jobid 12345 submitted
```
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/sbcast.html)
Copyright (C) 2006-2010 The Regents of the University of California.
Produced at Lawrence Livermore National Laboratory (cf, DISCLAIMER).
Copyright (C) 2010-2022 SchedMD LLC.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/sbcast.html)
[srun](https://slurm.schedmd.com/srun.html) (1)
## Index
[NAME](https://slurm.schedmd.com/sbcast.html)
[SYNOPSIS](https://slurm.schedmd.com/sbcast.html)
[DESCRIPTION](https://slurm.schedmd.com/sbcast.html)
[OPTIONS](https://slurm.schedmd.com/sbcast.html)
[PERFORMANCE](https://slurm.schedmd.com/sbcast.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/sbcast.html)
[AUTHORIZATION](https://slurm.schedmd.com/sbcast.html)
[EXAMPLES](https://slurm.schedmd.com/sbcast.html)
[COPYING](https://slurm.schedmd.com/sbcast.html)
[SEE ALSO](https://slurm.schedmd.com/sbcast.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
