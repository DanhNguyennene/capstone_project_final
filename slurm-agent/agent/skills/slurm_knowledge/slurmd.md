---
source_url: https://slurm.schedmd.com/slurmd.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:08 UTC
title: "Slurm Workload Manager - slurmd"
---

# slurmd
Section: Slurm Daemon (8)
Updated: Slurm Daemon
[Index](https://slurm.schedmd.com/slurmd.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/slurmd.html)
slurmd - The compute node daemon for Slurm.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/slurmd.html)
slurmd [ OPTIONS ...]
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/slurmd.html)
slurmd is the compute node daemon of Slurm. It monitors all tasks
running on the compute node , accepts work (tasks), launches tasks, and kills
running tasks upon request.
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/slurmd.html)
--authinfo [#OPT_authinfo](https://slurm.schedmd.com/slurmd.html) Used with configless to set an alternate AuthInfo parameter to be used to
establish communication with slurmctld before the configuration file has been
retrieved. (E.g., to specify an alternate MUNGE socket location.)
-b [#OPT_-b](https://slurm.schedmd.com/slurmd.html) Report node rebooted when daemon restarted. Used for testing purposes.
-c [#OPT_-c](https://slurm.schedmd.com/slurmd.html) Clear system locks as needed. This may be required if slurmd terminated
abnormally.
-C [#OPT_-C](https://slurm.schedmd.com/slurmd.html) Print the actual hardware configuration (not the configuration from the
slurm.conf file) and exit.
The format of output is the same as used in slurm.conf to describe a node's
configuration plus its uptime. You may use --parameters to specify
options such as 'l3cache_as_socket' which may alter the reported node topology.
--ca-cert-file <file> [#OPT_ca-cert-file- ](https://slurm.schedmd.com/slurmd.html) Absolute path to CA certificate used for fetching configuration when running
configless in a TLS enabled cluster.
--conf <node parameters> [#OPT_conf- ](https://slurm.schedmd.com/slurmd.html) Used in conjunction with the -Z option. Used to override or define
additional parameters of a dynamic node using the same syntax and parameters
used to define nodes in the slurm.conf. Specifying any of CPUs ,
Boards , SocketsPerBoard , CoresPerSocket or
ThreadsPerCore will override the defaults defined by the -C
option. NodeName and Port are not supported.
This can also be used to specify a cloud node's topology, in which case
the -Z flag should not be used (e.g.,
--conf="topology=topo-switch:s1")
For example if slurmd -C reports
```text
NodeName=node1 CPUs=16 Boards=1 SocketsPerBoard=1 CoresPerSocket=8 ThreadsPerCore=2 RealMemory=31848
```
the following --conf specifications will generate the corresponding node definitions:
```text
--conf "Gres=gpu:2" NodeName=node1 CPUs=16 Boards=1 SocketsPerBoard=1 CoresPerSocket=8 ThreadsPerCore=2 RealMemory=31848 Gres=gpu:2
```
```text
--conf "RealMemory=30000" NodeName=node1 CPUs=16 Boards=1 SocketsPerBoard=1 CoresPerSocket=8 ThreadsPerCore=2 RealMemory=30000
```
```text
--conf "CPUs=16" NodeName=node1 CPUs=16 RealMemory=331848
```
```text
--conf "CPUs=16 RealMemory=30000 Gres=gpu:2" NodeName=node1 CPUs=16 RealMemory=30000 Gres=gpu:2"
```
--conf-server <host|ip address>[:<port>] [#OPT_conf-server- [:
]](https://slurm.schedmd.com/slurmd.html) Comma-separated list of controllers, the first being the primary slurmctld. A
port can (optionally) be specified for each controller. These hosts are where
the slurmd will fetch the configuration from when running in "configless" mode.
NOTE : If specifying an IPv6 address, wrap the <ip address> in [] to
distinguish the address from the port. This is required even if no port is
specified.
-d <file> [#OPT_-d- ](https://slurm.schedmd.com/slurmd.html) Specify the fully qualified pathname to the slurmstepd program to be used
for shepherding user job steps. This can be useful for testing purposes.
-D [#OPT_-D](https://slurm.schedmd.com/slurmd.html) Run slurmd in the foreground with logging copied to stderr.
--extra <arbitrary string> [#OPT_extra- ](https://slurm.schedmd.com/slurmd.html) Set "extra" data on node startup. If this is a json string and
SchedulerParameters=extra_constraints is set in slurm.conf, then jobs may
use the --extra option to filter based on this "extra" data.
-f <file> [#OPT_-f- ](https://slurm.schedmd.com/slurmd.html) Read configuration from the specified file. See NOTES below.
-F[feature] [#OPT_-F[feature]](https://slurm.schedmd.com/slurmd.html) Start this node as a Dynamic Future node. It will try to match a node
definition with a state of FUTURE , optionally using the specified
feature to match the node definition.
-G [#OPT_-G](https://slurm.schedmd.com/slurmd.html) Print Generic RESource (GRES) configuration (based upon slurm.conf GRES merged
with gres.conf contents for this node) and exit.
-h [#OPT_-h](https://slurm.schedmd.com/slurmd.html) Help; print a brief summary of command options.
--instance-id <cloud instance id> [#OPT_instance-id- ](https://slurm.schedmd.com/slurmd.html) Set cloud instance ID on node startup.
--instance-type <cloud instance type> [#OPT_instance-type- ](https://slurm.schedmd.com/slurmd.html) Set cloud instance type on node startup.
-L <file> [#OPT_-L- ](https://slurm.schedmd.com/slurmd.html) Write log messages to the specified file.
-M [#OPT_-M](https://slurm.schedmd.com/slurmd.html) Lock slurmd pages into system memory using mlockall (2) to disable
paging of the slurmd process. This may help in cases where nodes are
marked DOWN during periods of heavy swap activity. If the mlockall (2)
system call is not available, an error will be printed to the log
and slurmd will continue as normal.
It is suggested to set LaunchParameters=slurmstepd_memlock in
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) when setting -M .
-n <value> [#OPT_-n- ](https://slurm.schedmd.com/slurmd.html) Set the daemon's nice value to the specified value, typically a negative number.
Also note the PropagatePrioProcess configuration parameter.
-N <nodename> [#OPT_-N- ](https://slurm.schedmd.com/slurmd.html) Run the daemon with the given nodename. Used to emulate a larger system
with more than one slurmd daemon per node. Requires that Slurm be built using
the --enable-multiple-slurmd configure option.
--parameters <slurmd parameters> [#OPT_parameters- ](https://slurm.schedmd.com/slurmd.html) Allows for temporary node-specific changes to SlurmdParameters. Can be used
alongside -C to specify options such as 'l3cache_as_socket' which may
alter the reported node topology. These parameters are appended to any
node-specific Parameters defined in slurm.conf.
-s [#OPT_-s](https://slurm.schedmd.com/slurmd.html) Change working directory of slurmd to SlurmdLogFile path if possible, or to
SlurmdSpoolDir otherwise. If both of them fail it will fallback to /var/tmp.
--systemd [#OPT_systemd](https://slurm.schedmd.com/slurmd.html) Use when starting the daemon with systemd. This will allow slurmd to notify
systemd of the new PID when using 'scontrol reconfigure'.
-v [#OPT_-v](https://slurm.schedmd.com/slurmd.html) Verbose operation. Multiple -v's increase verbosity.
-V , --version [#OPT_version](https://slurm.schedmd.com/slurmd.html) Print version information and exit.
-Z [#OPT_-Z](https://slurm.schedmd.com/slurmd.html) Start this node as a Dynamic Normal node. If no --conf is specified,
then the slurmd will register with the same hardware configuration (except GRES)
as defined by the -C option.
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/slurmd.html)
The following environment variables can be used to override settings
compiled into slurmd.
ABORT_ON_FATAL [#OPT_ABORT_ON_FATAL](https://slurm.schedmd.com/slurmd.html) When a fatal error is detected, use abort() instead of exit() to terminate the
process. This allows backtraces to be captured without recompiling Slurm.
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/slurmd.html) The location of the Slurm configuration file. This is overridden by
explicitly naming a configuration file on the command line.
SLURM_DEBUG_FLAGS [#OPT_SLURM_DEBUG_FLAGS](https://slurm.schedmd.com/slurmd.html) Specify debug flags for slurmd to use. See DebugFlags in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for a full list of flags. The environment
variable takes precedence over the setting in the slurm.conf.
## HTTP server[#SECTION_HTTP-server](https://slurm.schedmd.com/slurmd.html)
Unless disabled via CommunicationParameters=disable_http in
slurm.conf , slurmd will accept incoming HTTP/1.1 compliant
requests to any socket listening as configured by SlurmdPort in
slurm.conf . Authentication of HTTP requests is not supported. TLS
wrapping optionally supported without requiring TLSType in
slurm.conf . The following endpoints are currently supported:
GET / [#OPT_GET-/](https://slurm.schedmd.com/slurmd.html) Get list of endpoints.
GET /healthz [#OPT_GET-/healthz](https://slurm.schedmd.com/slurmd.html) Test if slurmd loaded successfully.
GET /livez [#OPT_GET-/livez](https://slurm.schedmd.com/slurmd.html) Test if slurmd loaded successfully.
GET /readyz [#OPT_GET-/readyz](https://slurm.schedmd.com/slurmd.html) Test if slurmd is ready to accept incoming RPCs.
## SIGNALS[#SECTION_SIGNALS](https://slurm.schedmd.com/slurmd.html)
SIGTERM SIGINT SIGQUIT [#OPT_SIGTERM-SIGINT-SIGQUIT](https://slurm.schedmd.com/slurmd.html) slurmd will shutdown cleanly.
SIGHUP [#OPT_SIGHUP](https://slurm.schedmd.com/slurmd.html) Reloads the slurm configuration files, similar to 'scontrol reconfigure'.
SIGUSR2 [#OPT_SIGUSR2](https://slurm.schedmd.com/slurmd.html) Reread the log level from the configs, and then reopen the log file. This
should be used when setting up logrotate (8).
SIGPIPE [#OPT_SIGPIPE](https://slurm.schedmd.com/slurmd.html) This signal is explicitly ignored.
## CORE FILE LOCATION[#SECTION_CORE-FILE-LOCATION](https://slurm.schedmd.com/slurmd.html)
If slurmd is started with the -D option then the core file will be
written to the current working directory.
Otherwise if SlurmdLogFile is a fully qualified path name
(starting with a slash), the core file will be written to the same
directory as the log file. Otherwise the core file will be written to
the SlurmdSpoolDir directory, or "/var/tmp/" as a last resort. If
none of the above directories can be written, no core file will be
produced.
## NOTES[#SECTION_NOTES](https://slurm.schedmd.com/slurmd.html)
It may be useful to experiment with different slurmd specific
configuration parameters using a distinct configuration file
(e.g. timeouts). However, this special configuration file will not be
used by the slurmctld daemon or the Slurm programs, unless you
specifically tell each of them to use it. If you desire changing
communication ports, the location of the temporary file system, or
other parameters used by other Slurm components, change the common
configuration file, slurm.conf .
If you are using configless mode with a login node that runs a lot of client
commands, you may consider running slurmd on that machine so it can
manage a cached version of the configuration files. Otherwise, each client
command will use the DNS record to contact the controller and get the
configuration information, which could place additional load on the controller.
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/slurmd.html)
Copyright (C) 2002-2007 The Regents of the University of California.
Copyright (C) 2008-2010 Lawrence Livermore National Security.
Copyright (C) 2010-2022 SchedMD LLC.
Produced at Lawrence Livermore National Laboratory (cf, DISCLAIMER).
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
## FILES[#SECTION_FILES](https://slurm.schedmd.com/slurmd.html)
/etc/slurm.conf
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/slurmd.html)
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5), [slurmctld](https://slurm.schedmd.com/slurmctld.html) (8)
## Index
[NAME](https://slurm.schedmd.com/slurmd.html)
[SYNOPSIS](https://slurm.schedmd.com/slurmd.html)
[DESCRIPTION](https://slurm.schedmd.com/slurmd.html)
[OPTIONS](https://slurm.schedmd.com/slurmd.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/slurmd.html)
[HTTP server](https://slurm.schedmd.com/slurmd.html)
[SIGNALS](https://slurm.schedmd.com/slurmd.html)
[CORE FILE LOCATION](https://slurm.schedmd.com/slurmd.html)
[NOTES](https://slurm.schedmd.com/slurmd.html)
[COPYING](https://slurm.schedmd.com/slurmd.html)
[FILES](https://slurm.schedmd.com/slurmd.html)
[SEE ALSO](https://slurm.schedmd.com/slurmd.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
