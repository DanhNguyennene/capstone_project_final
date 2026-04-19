---
source_url: https://slurm.schedmd.com/slurmdbd.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:25 UTC
title: "Slurm Workload Manager - slurmdbd"
---

# slurmdbd
Section: Slurm Daemon (8)
Updated: Slurm Daemon
[Index](https://slurm.schedmd.com/slurmdbd.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/slurmdbd.html)
slurmdbd - Slurm Database Daemon.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/slurmdbd.html)
slurmdbd [ OPTIONS ...]
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/slurmdbd.html)
slurmdbd provides a secure enterprise-wide interface to a database
for Slurm. This is particularly useful for archiving accounting records.
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/slurmdbd.html)
-D [#OPT_-D](https://slurm.schedmd.com/slurmdbd.html) Run slurmdbd in the foreground with logging copied to stdout.
-h [#OPT_-h](https://slurm.schedmd.com/slurmdbd.html) Help; print a brief summary of command options.
-n <value> [#OPT_-n- ](https://slurm.schedmd.com/slurmdbd.html) Set the daemon's nice value to the specified value, typically a negative number.
-s [#OPT_-s](https://slurm.schedmd.com/slurmdbd.html) Change working directory of slurmdbd to LogFile path if possible, or to /var/tmp
otherwise.
-u [#OPT_-u](https://slurm.schedmd.com/slurmdbd.html) Only display the Slurm Database version and if conversion is needed and exit
without taking control. If no conversion is needed 0 is returned, if conversion
is needed 1 is returned.
-v [#OPT_-v](https://slurm.schedmd.com/slurmdbd.html) Verbose operation. Multiple v 's can be specified, with each ' v '
beyond the first increasing verbosity, up to 6 times (i.e. -vvvvvv).
-V [#OPT_-V](https://slurm.schedmd.com/slurmdbd.html) Print version information and exit.
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/slurmdbd.html)
The following environment variables can be used to override settings
compiled into slurmdbd.
ABORT_ON_FATAL [#OPT_ABORT_ON_FATAL](https://slurm.schedmd.com/slurmdbd.html) When a fatal error is detected, use abort() instead of exit() to terminate the
process. This allows backtraces to be captured without recompiling Slurm.
## CORE FILE LOCATION[#SECTION_CORE-FILE-LOCATION](https://slurm.schedmd.com/slurmdbd.html)
If slurmdbd is started with the -D option then the core file will be
written to the current working directory.
Otherwise if LogFile in "slurmdbd.conf" is a fully qualified
path name (starting with a slash), the core file will be written to
the same directory as the log file, provided SlurmUser has write
permission on the directory. Otherwise the core file will be written
to "/var/tmp/" as a last resort. If neither of the above directories
have write permission for SlurmUser, no core file will be produced.
## SIGNALS[#SECTION_SIGNALS](https://slurm.schedmd.com/slurmdbd.html)
SIGTERM SIGINT SIGQUIT [#OPT_SIGTERM-SIGINT-SIGQUIT](https://slurm.schedmd.com/slurmdbd.html) slurmdbd will shutdown cleanly, waiting for in-progress rollups to
finish.
SIGABRT [#OPT_SIGABRT](https://slurm.schedmd.com/slurmdbd.html) slurmdbd will perform a core dump, then exit. In-progress operations
are killed.
SIGHUP [#OPT_SIGHUP](https://slurm.schedmd.com/slurmdbd.html) Reloads the slurm configuration files, similar to 'scontrol reconfigure'.
SIGTSTP [#OPT_SIGTSTP](https://slurm.schedmd.com/slurmdbd.html) Stop the process from a terminal.
SIGUSR2 [#OPT_SIGUSR2](https://slurm.schedmd.com/slurmdbd.html) Reread the log level from the configs, and then reopen the log file. This
should be used when setting up logrotate (8).
SIGCHLD SIGUSR1 SIGXCPU SIGPIPE SIGALRM [#OPT_SIGCHLD-SIGUSR1-SIGXCPU-SIGPIPE-SIGALRM](https://slurm.schedmd.com/slurmdbd.html) These signals are explicitly ignored.
## NOTES[#SECTION_NOTES](https://slurm.schedmd.com/slurmdbd.html)
It may be useful to experiment with different slurmctld specific
configuration parameters using a distinct configuration file
(e.g. timeouts). However, this special configuration file will not be
used by the slurmd daemon or the Slurm programs, unless you
specifically tell each of them to use it. If you desire changing
communication ports, the location of the temporary file system, or
other parameters used by other Slurm components, change the common
configuration file, slurm.conf .
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/slurmdbd.html)
Copyright (C) 2008 Lawrence Livermore National Security.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/slurmdbd.html)
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5), [slurmdbd.conf](https://slurm.schedmd.com/slurmdbd.conf.html) (5), [slurmctld](https://slurm.schedmd.com/slurmctld.html) (8)
## Index
[NAME](https://slurm.schedmd.com/slurmdbd.html)
[SYNOPSIS](https://slurm.schedmd.com/slurmdbd.html)
[DESCRIPTION](https://slurm.schedmd.com/slurmdbd.html)
[OPTIONS](https://slurm.schedmd.com/slurmdbd.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/slurmdbd.html)
[CORE FILE LOCATION](https://slurm.schedmd.com/slurmdbd.html)
[SIGNALS](https://slurm.schedmd.com/slurmdbd.html)
[NOTES](https://slurm.schedmd.com/slurmdbd.html)
[COPYING](https://slurm.schedmd.com/slurmdbd.html)
[SEE ALSO](https://slurm.schedmd.com/slurmdbd.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
