---
source_url: https://slurm.schedmd.com/oci.conf.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:03 UTC
title: "Slurm Workload Manager - oci.conf"
---

# oci.conf
Section: Slurm Configuration File (5)
Updated: Slurm Configuration File
[Index](https://slurm.schedmd.com/oci.conf.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/oci.conf.html)
oci.conf - Slurm configuration file for containers.
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/oci.conf.html)
Slurm supports calling OCI compliant runtimes. oci.conf is an ASCII
file which defines parameters used by OCI runtime interface.
The file will always be located in the same directory as the slurm.conf .
Parameter names are case insensitive.
Any text following a "#" in the configuration file is treated
as a comment through the end of that line.
Changes to the configuration file take effect upon restart of Slurm daemons.
## PARAMETERS[#SECTION_PARAMETERS](https://slurm.schedmd.com/oci.conf.html)
The following oci.conf parameters are defined to control the behavior
of the --container argument of salloc , srun , and sbatch
ContainerPath [#OPT_ContainerPath](https://slurm.schedmd.com/oci.conf.html) Specifies an override path pattern for placing the per-step spool directory.
If this option is set, the resulting per-task OCI container bundle path will be
created as a subdirectory of this path. Refer to the OCI Pattern section
for details on pattern substitution.
By default, an uniquely generated subdirectory for each step is created under
SlurmdSpoolDir .
CreateEnvFile=(null|newline|disabled) [#OPT_CreateEnvFile=(null|newline|disabled)](https://slurm.schedmd.com/oci.conf.html) Create environment file for container. File will have one environment variable
per line if value is "newline". File will have each environment
variable terminated by a NUL (aka '\0') if value is "null". If value
is "disabled", then the environment file will not be created.
Value of "true" is treated as "null" for backwards compatibility.
Value of "false" is treated as "disabled" for backwards compatibility.
Note: When CreateEnvFile=newline, any environment variables with a newline will
be dropped before writing to the environment file.
Default is "disabled".
DebugFlags [#OPT_DebugFlags](https://slurm.schedmd.com/oci.conf.html) Override debug flags during container operations. See debugflags in
slurm.conf .
Default: (disabled)
DisableCleanup [#OPT_DisableCleanup](https://slurm.schedmd.com/oci.conf.html) Disable removal of the generated files handed to OCI runtime.
Default: false
DisableHooks [#OPT_DisableHooks](https://slurm.schedmd.com/oci.conf.html) Comma separated list of hook types to disable.
Default: allow all hooks.
EnvExclude [#OPT_EnvExclude](https://slurm.schedmd.com/oci.conf.html) Extended regular expression to filter environment before. This allows for
excluding variables to avoid unwanted environment variables inside of
containers.
Example: EnvExclude ="^(SLURM_CONF|SLURM_CONF_SERVER)="
Default does not exclude any environment variables.
MountSpoolDir [#OPT_MountSpoolDir](https://slurm.schedmd.com/oci.conf.html) Override pattern for path inside of container to mount ContainerPath . See
the section OCI Pattern for details on pattern replacement.
Default: see ContainerPath
RunTimeEnvExclude [#OPT_RunTimeEnvExclude](https://slurm.schedmd.com/oci.conf.html) Extended regular expression to filter environment before calling any
RunTime* commands. This allows for excluding variables to avoid unwanted
inheritance inside of the OCI runtimes.
Example: RunTimeEnvExclude ="^(SLURM_CONF|SLURM_CONF_SERVER)="
Default is not exclude any environment variables.
FileDebug [#OPT_FileDebug](https://slurm.schedmd.com/oci.conf.html) Override default file logging level during container operations. See
SlurmdDebug in slurm.conf .
Default: (disabled)
IgnoreFileConfigJson=(true|false) [#OPT_IgnoreFileConfigJson=(true|false)](https://slurm.schedmd.com/oci.conf.html) Ignore the existence of config.json in OCI bundle path and disable loading
config.json if it is present.
Default is false.
RunTimeCreate [#OPT_RunTimeCreate](https://slurm.schedmd.com/oci.conf.html) Pattern for OCI runtime create operation. See the section OCI Pattern
for details on pattern replacement.
Default: (disabled)
RunTimeDelete [#OPT_RunTimeDelete](https://slurm.schedmd.com/oci.conf.html) Pattern for OCI runtime delete operation. See the section OCI Pattern
for details on pattern replacement.
Default: (disabled)
RunTimeKill [#OPT_RunTimeKill](https://slurm.schedmd.com/oci.conf.html) Pattern for OCI runtime kill operation. See the section OCI Pattern
for details on pattern replacement.
Default: (disabled)
RunTimeQuery [#OPT_RunTimeQuery](https://slurm.schedmd.com/oci.conf.html) Pattern for OCI runtime query operation (also known as state). See the section
OCI Pattern for details on pattern replacement.
Default: (disabled)
RunTimeRun [#OPT_RunTimeRun](https://slurm.schedmd.com/oci.conf.html) Pattern for OCI runtime run operation. This is not provided in the OCI runtime
specification (<=v1.0) but is provided by multiple OCI runtimes to simplify
execution of containers. If provided, it will be used in the place of create
and start operations. It avoids the need to poll state of the container
resulting in less monitoring overhead. See the section OCI Pattern for
details on pattern replacement.
Default: (disabled)
RunTimeStart [#OPT_RunTimeStart](https://slurm.schedmd.com/oci.conf.html) Pattern for OCI runtime start operation. See the section OCI Pattern
for details on pattern replacement.
Default: (disabled)
SrunPath [#OPT_SrunPath](https://slurm.schedmd.com/oci.conf.html) Absolute path to srun executable.
Default: (search PATH)
SrunArgs [#OPT_SrunArgs](https://slurm.schedmd.com/oci.conf.html) Additional arguments to pass to srun. Add one SrunArgs entry per
argument.
Default: (disabled)
StdIODebug [#OPT_StdIODebug](https://slurm.schedmd.com/oci.conf.html) Override default STDIO logging level during container operations. See
SlurmdDebug in slurm.conf .
Default: (disabled)
SyslogDebug [#OPT_SyslogDebug](https://slurm.schedmd.com/oci.conf.html) Override default syslog logging level during container operations. See
SlurmdSyslogDebug in slurm.conf .
Default: (disabled)
## NOTES[#SECTION_NOTES](https://slurm.schedmd.com/oci.conf.html)
OCI container support is disabled if oci.conf does not exist. If disabled, any
user passing --container will be doing so in a purely advisor manner.
## OCI Pattern[#SECTION_OCI-Pattern](https://slurm.schedmd.com/oci.conf.html)
All of the OCI patterns will replace the following characters:
Replacements :
%% [#OPT_%%](https://slurm.schedmd.com/oci.conf.html) Replace as "%".
%@ [#OPT_%@](https://slurm.schedmd.com/oci.conf.html) Replace as the command and arguments. Each argument will be
enclosed with single quotes and escaped.
%b [#OPT_%b](https://slurm.schedmd.com/oci.conf.html) Replace as OCI Bundle Path.
%e [#OPT_%e](https://slurm.schedmd.com/oci.conf.html) Replace as path to file containing environment if
CreateEnvFile=true .
%j [#OPT_%j](https://slurm.schedmd.com/oci.conf.html) Replace as numeric job id.
%m [#OPT_%m](https://slurm.schedmd.com/oci.conf.html) Replace with the per-step spool directory path of the container as patterned by
ContainerPath . If ContainerPath is not set, this is replaced with
a uniquely generated subdirectory under SlurmdSpoolDir as defined in
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5), or defaults to "/var/spool/slurmd".
%n [#OPT_%n](https://slurm.schedmd.com/oci.conf.html) Replace as nodename.
%p [#OPT_%p](https://slurm.schedmd.com/oci.conf.html) Replace as PID of first processes forked off. Only for use in RunTimeKill
or RunTimeDelete .
%r [#OPT_%r](https://slurm.schedmd.com/oci.conf.html) Replace as original path to rootfs.
%s [#OPT_%s](https://slurm.schedmd.com/oci.conf.html) Replace as numeric step id.
%t [#OPT_%t](https://slurm.schedmd.com/oci.conf.html) Replace as numeric step task id.
%u [#OPT_%u](https://slurm.schedmd.com/oci.conf.html) Replace as user name.
%U [#OPT_%U](https://slurm.schedmd.com/oci.conf.html) Replace as numeric user id.
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/oci.conf.html)
Copyright (C) 2021 SchedMD LLC.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/oci.conf.html)
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5)
## Index
[NAME](https://slurm.schedmd.com/oci.conf.html)
[DESCRIPTION](https://slurm.schedmd.com/oci.conf.html)
[PARAMETERS](https://slurm.schedmd.com/oci.conf.html)
[NOTES](https://slurm.schedmd.com/oci.conf.html)
[OCI Pattern](https://slurm.schedmd.com/oci.conf.html)
[COPYING](https://slurm.schedmd.com/oci.conf.html)
[SEE ALSO](https://slurm.schedmd.com/oci.conf.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
