---
source_url: https://slurm.schedmd.com/slurmctld.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:24 UTC
title: "Slurm Workload Manager - slurmctld"
---

# slurmctld
Section: Slurm Daemon (8)
Updated: Slurm Daemon
[Index](https://slurm.schedmd.com/slurmctld.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/slurmctld.html)
slurmctld - The central management daemon of Slurm.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/slurmctld.html)
slurmctld [ OPTIONS ...]
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/slurmctld.html)
slurmctld is the central management daemon of Slurm. It monitors
all other Slurm daemons and resources, accepts work (jobs), and allocates
resources to those jobs. Given the critical functionality of slurmctld ,
there may be a backup server to assume these functions in the event that
the primary server fails.
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/slurmctld.html)
-c [#OPT_-c](https://slurm.schedmd.com/slurmctld.html) Clear all previous slurmctld state from its last checkpoint.
With this option, all jobs, including both running and queued, and all
node states, will be deleted. Without this option, previously running
jobs will be preserved along with node State of DOWN, DRAINED
and DRAINING nodes and the associated Reason field for those nodes.
NOTE : It is rare you would ever want to use this in production as all
jobs will be killed.
-D [#OPT_-D](https://slurm.schedmd.com/slurmctld.html) Run slurmctld in the foreground with logging copied to stderr.
This limits the resilience of 'scontrol reconfigure' and should be
avoided in production.
-f <file> [#OPT_-f- ](https://slurm.schedmd.com/slurmctld.html) Read configuration from the specified file. See NOTES below.
-h [#OPT_-h](https://slurm.schedmd.com/slurmctld.html) Help; print a brief summary of command options.
-i [#OPT_-i](https://slurm.schedmd.com/slurmctld.html) Ignore errors found while reading in state files on startup.
Warning: Use of this option will mean losing the data that wasn't recovered
from the state files.
-L <file> [#OPT_-L- ](https://slurm.schedmd.com/slurmctld.html) Write log messages to the specified file.
-n <value> [#OPT_-n- ](https://slurm.schedmd.com/slurmctld.html) Set the daemon's nice value to the specified value, typically a negative number.
-r [#OPT_-r](https://slurm.schedmd.com/slurmctld.html) Recover partial state from last checkpoint: jobs and node DOWN/DRAIN
state and reason information state. No partition state is recovered.
This is the default action.
-R [#OPT_-R](https://slurm.schedmd.com/slurmctld.html) Recover full state from last checkpoint: jobs, node, partition state, and power
save settings.
Without this option, previously running jobs will be preserved along
with node State of DOWN, DRAINED and DRAINING nodes and the associated
Reason field for those nodes. No other node or partition state will
be preserved.
-s [#OPT_-s](https://slurm.schedmd.com/slurmctld.html) Change working directory of slurmctld to SlurmctldLogFile path if possible, or
to Slurm's StateSaveLocation otherwise. If both of them fail it will fallback to
/var/tmp.
--systemd [#OPT_systemd](https://slurm.schedmd.com/slurmctld.html) Use when starting the daemon with systemd. This will allow slurmctld to notify
systemd of the new PID when using 'scontrol reconfigure'.
NOTE : The User and Group options in the slurmctld's systemd unit file need
to both specify the SlurmUser.
-v [#OPT_-v](https://slurm.schedmd.com/slurmctld.html) Verbose operation. Multiple v 's can be specified, with each ' v '
beyond the first increasing verbosity, up to 6 times (i.e. -vvvvvv).
-V [#OPT_-V](https://slurm.schedmd.com/slurmctld.html) Print version information and exit.
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/slurmctld.html)
The following environment variables can be used to override settings
compiled into slurmctld.
ABORT_ON_FATAL [#OPT_ABORT_ON_FATAL](https://slurm.schedmd.com/slurmctld.html) When a fatal error is detected, use abort() instead of exit() to terminate the
process. This allows backtraces to be captured without recompiling Slurm.
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/slurmctld.html) The location of the Slurm configuration file. This is overridden by
explicitly naming a configuration file on the command line.
SLURM_DEBUG_FLAGS [#OPT_SLURM_DEBUG_FLAGS](https://slurm.schedmd.com/slurmctld.html) Specify debug flags for the scheduler to use. See DebugFlags in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for a full list of flags. The environment
variable takes precedence over the setting in the slurm.conf.
## HTTP server[#SECTION_HTTP-server](https://slurm.schedmd.com/slurmctld.html)
Unless disabled via CommunicationParameters=disable_http in
slurm.conf , slurmctld will accept incoming HTTP/1.1 compliant
requests to any socket listening as configured by SlurmctldPort in
slurm.conf . Authentication of HTTP requests is not supported. TLS
wrapping optionally supported without requiring TLSType in
slurm.conf . The following endpoints are currently supported:
GET / [#OPT_GET-/](https://slurm.schedmd.com/slurmctld.html) Get list of endpoints.
GET /healthz [#OPT_GET-/healthz](https://slurm.schedmd.com/slurmctld.html) Test if slurmctld loaded successfully.
GET /livez [#OPT_GET-/livez](https://slurm.schedmd.com/slurmctld.html) Test if slurmctld loaded successfully.
GET /readyz [#OPT_GET-/readyz](https://slurm.schedmd.com/slurmctld.html) Test if slurmctld is ready to accept incoming RPCs.
GET /metrics/jobs [#OPT_GET-/metrics/jobs](https://slurm.schedmd.com/slurmctld.html) Get job metrics.
GET /metrics/nodes [#OPT_GET-/metrics/nodes](https://slurm.schedmd.com/slurmctld.html) Get node metrics.
GET /metrics/partitions [#OPT_GET-/metrics/partitions](https://slurm.schedmd.com/slurmctld.html) Get partition metrics.
GET /metrics/scheduler [#OPT_GET-/metrics/scheduler](https://slurm.schedmd.com/slurmctld.html) Return scheduler metrics.
GET /metrics/jobs-users-accts [#OPT_GET-/metrics/jobs-users-accts](https://slurm.schedmd.com/slurmctld.html) Return user and account job metrics.
## CORE FILE LOCATION[#SECTION_CORE-FILE-LOCATION](https://slurm.schedmd.com/slurmctld.html)
If slurmctld is started with the -D option then the core file will be
written to the current working directory.
Otherwise if SlurmctldLogFile is a fully qualified path name (starting
with a slash), the core file will be written to the same directory as the
log file, provided SlurmUser has write permission on the directory.
Otherwise the core file will be written to the StateSaveLocation ,
or "/var/tmp/" as a last resort. If none of the above directories have
write permission for SlurmUser, no core file will be produced.
## SIGNALS[#SECTION_SIGNALS](https://slurm.schedmd.com/slurmctld.html)
SIGTERM SIGINT SIGQUIT [#OPT_SIGTERM-SIGINT-SIGQUIT](https://slurm.schedmd.com/slurmctld.html) slurmctld will shutdown cleanly, saving its current state to the state
save directory.
SIGABRT [#OPT_SIGABRT](https://slurm.schedmd.com/slurmctld.html) slurmctld will shutdown cleanly, saving its current state, and perform a
core dump.
SIGHUP [#OPT_SIGHUP](https://slurm.schedmd.com/slurmctld.html) Reloads the slurm configuration files, similar to 'scontrol reconfigure'.
SIGTSTP [#OPT_SIGTSTP](https://slurm.schedmd.com/slurmctld.html) Stop the process from a terminal. This also stops slurmscriptd.
SIGUSR2 [#OPT_SIGUSR2](https://slurm.schedmd.com/slurmctld.html) Reread the log level from the configs, and then reopen the log file. This
should be used when setting up logrotate (8).
SIGPROF [#OPT_SIGPROF](https://slurm.schedmd.com/slurmctld.html) Logs connection manager state when debug level is at least info.
SIGCHLD SIGUSR1 SIGXCPU SIGPIPE SIGALRM [#OPT_SIGCHLD-SIGUSR1-SIGXCPU-SIGPIPE-SIGALRM](https://slurm.schedmd.com/slurmctld.html) These signals are explicitly ignored.
## NOTES[#SECTION_NOTES](https://slurm.schedmd.com/slurmctld.html)
It may be useful to experiment with different slurmctld specific
configuration parameters using a distinct configuration file
(e.g. timeouts). However, this special configuration file will not be
used by the slurmd daemon or the Slurm programs, unless you
specifically tell each of them to use it. If you desire changing
communication ports, the location of the temporary file system, or
other parameters used by other Slurm components, change the common
configuration file, slurm.conf .
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/slurmctld.html)
Copyright (C) 2002-2007 The Regents of the University of California.
Copyright (C) 2008-2010 Lawrence Livermore National Security.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/slurmctld.html)
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5), [slurmd](https://slurm.schedmd.com/slurmd.html) (8)
## Index
[NAME](https://slurm.schedmd.com/slurmctld.html)
[SYNOPSIS](https://slurm.schedmd.com/slurmctld.html)
[DESCRIPTION](https://slurm.schedmd.com/slurmctld.html)
[OPTIONS](https://slurm.schedmd.com/slurmctld.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/slurmctld.html)
[HTTP server](https://slurm.schedmd.com/slurmctld.html)
[CORE FILE LOCATION](https://slurm.schedmd.com/slurmctld.html)
[SIGNALS](https://slurm.schedmd.com/slurmctld.html)
[NOTES](https://slurm.schedmd.com/slurmctld.html)
[COPYING](https://slurm.schedmd.com/slurmctld.html)
[SEE ALSO](https://slurm.schedmd.com/slurmctld.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
