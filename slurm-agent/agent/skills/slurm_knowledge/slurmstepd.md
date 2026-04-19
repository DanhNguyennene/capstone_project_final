---
source_url: https://slurm.schedmd.com/slurmstepd.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:26 UTC
title: "Slurm Workload Manager - slurmstepd"
---

# slurmstepd
Section: Slurm Component (8)
Updated: Slurm Component
[Index](https://slurm.schedmd.com/slurmstepd.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/slurmstepd.html)
slurmstepd - The job step manager for Slurm.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/slurmstepd.html)
slurmstepd
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/slurmstepd.html)
slurmstepd is a job step manager for Slurm.
It is spawned by the slurmd daemon when a job step is launched
and terminates when the job step does.
It is responsible for managing input and output (stdin, stdout and stderr)
for the job step along with its accounting and signal processing.
slurmstepd should not be initiated by users or system administrators.
## ENVIRONMENT VARIABLES:[#SECTION_ENVIRONMENT-VARIABLES:](https://slurm.schedmd.com/slurmstepd.html)
The following environment variables can be used to override settings
compiled into slurmstepd.
SLURM_DEBUG_FLAGS [#OPT_SLURM_DEBUG_FLAGS](https://slurm.schedmd.com/slurmstepd.html) Specify debug flags for slurmstepd to use. See DebugFlags in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for a full list of flags. The environment
variable takes precedence over the setting in the slurm.conf.
## SIGNALS[#SECTION_SIGNALS](https://slurm.schedmd.com/slurmstepd.html)
SIGINT SIGTERM SIGQUIT [#OPT_SIGINT-SIGTERM-SIGQUIT](https://slurm.schedmd.com/slurmstepd.html) slurmstepd will shutdown cleanly.
SIGPROF [#OPT_SIGPROF](https://slurm.schedmd.com/slurmstepd.html) Logs connection manager state when debug level is at least info.
SIGTSTP SIGPIPE SIGUSR1 SIGUSR2 SIGALRM SIGHUP [#OPT_SIGTSTP-SIGPIPE-SIGUSR1-SIGUSR2-SIGALRM-SIGHUP](https://slurm.schedmd.com/slurmstepd.html) These signals are explicitly ignored.
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/slurmstepd.html)
Copyright (C) 2006 The Regents of the University of California.
Copyright (C) 2010-2022 SchedMD LLC.
Produced at Lawrence Livermore National Laboratory (cf, DISCLAIMER).
CODE-OCEC-09-009. All rights reserved.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/slurmstepd.html)
[slurmd](https://slurm.schedmd.com/slurmd.html) (8)
## Index
[NAME](https://slurm.schedmd.com/slurmstepd.html)
[SYNOPSIS](https://slurm.schedmd.com/slurmstepd.html)
[DESCRIPTION](https://slurm.schedmd.com/slurmstepd.html)
[ENVIRONMENT VARIABLES:](https://slurm.schedmd.com/slurmstepd.html)
[SIGNALS](https://slurm.schedmd.com/slurmstepd.html)
[COPYING](https://slurm.schedmd.com/slurmstepd.html)
[SEE ALSO](https://slurm.schedmd.com/slurmstepd.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
