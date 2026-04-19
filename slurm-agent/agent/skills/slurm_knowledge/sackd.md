---
source_url: https://slurm.schedmd.com/sackd.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:21:58 UTC
title: "Slurm Workload Manager - sackd"
---

# sackd
Section: Slurm Auth and Cred Kiosk Daemon (8)
Updated: Slurm Auth and Cred Kiosk Daemon
[Index](https://slurm.schedmd.com/sackd.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/sackd.html)
sackd - Slurm Auth and Cred Kiosk Daemon.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/sackd.html)
sackd [ OPTIONS ...]
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/sackd.html)
sackd is the Slurm Auth and Cred Kiosk Daemon. It can be used on login
nodes that are not running slurmd daemons to allow authentication to the
cluster. The program will run as the SlurmUser . When running in Slurm's
"configless" mode, in which case configuration files are retrieved and written
under the /run/slurm/conf directory (unless RUNTIME_DIRECTORY is set).
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/sackd.html)
--ca-cert-file <file> [#OPT_ca-cert-file- ](https://slurm.schedmd.com/sackd.html) Absolute path to CA certificate used for fetching configuration when running
configless in a TLS enabled cluster.
--conf-server host[:port] [#OPT_conf-server-host[:port]](https://slurm.schedmd.com/sackd.html) Retrieve configs from slurmctld running at host[:port] .
Requires slurmctld support provided by setting enable_configless in
SlurmctldParameters.
-D [#OPT_-D](https://slurm.schedmd.com/sackd.html) Run sackd in the foreground with logging copied to stderr.
--disable-reconfig [#OPT_disable-reconfig](https://slurm.schedmd.com/sackd.html) Fetch configurations in configless mode once, but do not register with slurmctld
for further reconfiguration updates.
-f config [#OPT_-f-config](https://slurm.schedmd.com/sackd.html) Read configuration from the specified file.
-h [#OPT_-h](https://slurm.schedmd.com/sackd.html) Help; print a brief summary of command options.
--jwks-file <file> [#OPT_jwks-file- ](https://slurm.schedmd.com/sackd.html) Read auth/slurm JWKS information from the specified file. Default value is
slurm.jwks located in the same directory as slurm.conf.
--key-file <file> [#OPT_key-file- ](https://slurm.schedmd.com/sackd.html) Read auth/slurm authentication key from the specified file. Default value is
slurm.key located in the same directory as slurm.conf.
--port number [#OPT_port-number](https://slurm.schedmd.com/sackd.html) Port socket number to listen for reconfiguration updates. This can be useful
when multiple sackds co-exist on the same login node. The default value is
SlurmdPort .
--systemd [#OPT_systemd](https://slurm.schedmd.com/sackd.html) To be used when started from a systemd unit file.
-v [#OPT_-v](https://slurm.schedmd.com/sackd.html) Verbose mode. Multiple -v's increase verbosity.
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/sackd.html)
The following environment variables can be used to override settings
compiled into sackd.
ABORT_ON_FATAL [#OPT_ABORT_ON_FATAL](https://slurm.schedmd.com/sackd.html) When a fatal error is detected, use abort() instead of exit() to terminate the
process. This allows backtraces to be captured without recompiling Slurm.
RUNTIME_DIRECTORY [#OPT_RUNTIME_DIRECTORY](https://slurm.schedmd.com/sackd.html) Absolute path governing the location for both the configuration cache sackd
maintains, and the sack.socket unix socket used to provide authentication
services.
If multiple sackds need to be started on the same login node, the
RuntimeDirectory systemd unit option should be set to
slurm-<clustername> . Systemd v240+ automatically sets
RUNTIME_DIRECTORY to /run/$RuntimeDirectory for each sackd service,
otherwise it requires manual setting (i.e. via EnvironmentFile unit
option).
If this is not set, the default value is /run/slurm/ .
SACKD_DEBUG [#OPT_SACKD_DEBUG](https://slurm.schedmd.com/sackd.html) Set debug level explicitly for syslog and stderr. Valid values are 0-9, or the
same string values as the debug options such as SlurmctldDebug in
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html)(5).
SACKD_DISABLE_RECONFIG [#OPT_SACKD_DISABLE_RECONFIG](https://slurm.schedmd.com/sackd.html) Same as --disable-reconfig .
SACKD_PORT [#OPT_SACKD_PORT](https://slurm.schedmd.com/sackd.html) Same as --port .
SACKD_STDERR_DEBUG [#OPT_SACKD_STDERR_DEBUG](https://slurm.schedmd.com/sackd.html) Set debug level explicitly for stderr. Valid values are 0-9, or the same
string values as the debug options such as SlurmctldDebug in [slurm.conf](https://slurm.schedmd.com/slurm.conf.html)(5).
SACKD_SYSLOG_DEBUG [#OPT_SACKD_SYSLOG_DEBUG](https://slurm.schedmd.com/sackd.html) Set debug level explicitly for syslog. Valid values are 0-9, or the same
string values as the debug options such as SlurmctldDebug in [slurm.conf](https://slurm.schedmd.com/slurm.conf.html)(5).
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/sackd.html) The location of the Slurm configuration file.
SLURM_DEBUG_FLAGS [#OPT_SLURM_DEBUG_FLAGS](https://slurm.schedmd.com/sackd.html) Specify debug flags for sackd to use. See DebugFlags in the [slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5)
man page for a full list of flags. The environment variable takes precedence
over the setting in the slurm.conf.
## SIGNALS[#SECTION_SIGNALS](https://slurm.schedmd.com/sackd.html)
SIGINT [#OPT_SIGINT](https://slurm.schedmd.com/sackd.html) sackd will shutdown cleanly.
SIGHUP [#OPT_SIGHUP](https://slurm.schedmd.com/sackd.html) sackd will reconfigure.
SIGUSR2 SIGPIPE [#OPT_SIGUSR2-SIGPIPE](https://slurm.schedmd.com/sackd.html) This signal is explicitly ignored.
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/sackd.html)
Copyright (C) SchedMD LLC.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/sackd.html)
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5), [slurmctld](https://slurm.schedmd.com/slurmctld.html) (8)
## Index
[NAME](https://slurm.schedmd.com/sackd.html)
[SYNOPSIS](https://slurm.schedmd.com/sackd.html)
[DESCRIPTION](https://slurm.schedmd.com/sackd.html)
[OPTIONS](https://slurm.schedmd.com/sackd.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/sackd.html)
[SIGNALS](https://slurm.schedmd.com/sackd.html)
[COPYING](https://slurm.schedmd.com/sackd.html)
[SEE ALSO](https://slurm.schedmd.com/sackd.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
