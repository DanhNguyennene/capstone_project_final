---
source_url: https://slurm.schedmd.com/burst_buffer.conf.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:21:58 UTC
title: "Slurm Workload Manager - burst_buffer.conf"
---

# burst_buffer.conf
Section: Slurm Configuration File (5)
Updated: Slurm Configuration File
[Index](https://slurm.schedmd.com/burst_buffer.conf.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/burst_buffer.conf.html)
burst_buffer.conf - Slurm configuration file for burst buffer management.
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/burst_buffer.conf.html)
burst_buffer.conf is an ASCII file which describes the configuration
of burst buffer resource management.
This file is only required on the head node(s), where the slurmctld daemon
executes.
The file will always be located in the same directory as the slurm.conf .
Parameter names are case insensitive.
Any text following a "#" in the configuration file is treated
as a comment through the end of that line.
Changes to the configuration file take effect upon restart of
Slurm daemons, daemon receipt of the SIGHUP signal, or execution
of the command "scontrol reconfigure".
The configuration parameters available include:
AllowUsers [#OPT_AllowUsers](https://slurm.schedmd.com/burst_buffer.conf.html) Comma separated list of user names and/or IDs permitted to use burst buffers.
The options AllowUsers and DenyUsers can not both be specified.
By default all users are permitted to use burst buffers.
DefaultPool [#OPT_DefaultPool](https://slurm.schedmd.com/burst_buffer.conf.html) Name of the pool used by default for resource allocations.
The default value is the first pool reported by the burst buffer infrastructure.
This option is only used by the burst_buffer/datawarp plugin.
DenyUsers [#OPT_DenyUsers](https://slurm.schedmd.com/burst_buffer.conf.html) Colon delimited list of user names and/or IDs prevented from using burst buffers.
The options AllowUsers and DenyUsers can not both be specified.
By default all users are permitted to use burst buffers.
Directive [#OPT_Directive](https://slurm.schedmd.com/burst_buffer.conf.html) The string that must be used by a job to request a burst buffer. This string
must be immediately preceded by a single '#' character. This is currently only
used by the lua plugin. For the lua plugin, the default value is "BB_LUA".
See burst_buffer.html for more details.
Flags [#OPT_Flags](https://slurm.schedmd.com/burst_buffer.conf.html) String used to control various functions.
Multiple options may be comma separated.
Supported options include:
DisablePersistent [#OPT_DisablePersistent](https://slurm.schedmd.com/burst_buffer.conf.html) Prevents regular users from being able to create and destroy persistent burst buffers.
This is the default behavior, only privileged users (Slurm operators and
administrators) can create or destroy persistent burst buffers.
EmulateCray [#OPT_EmulateCray](https://slurm.schedmd.com/burst_buffer.conf.html) Emulating a Cray DataWarp system using the dw_wlm_cli script in the burst_buffer/datawarp plugin.
This is only used by the datawarp plugin.
EnablePersistent [#OPT_EnablePersistent](https://slurm.schedmd.com/burst_buffer.conf.html) Enables regular users to create and destroy persistent burst buffers.
By default, only privileged users (Slurm operators and administrators) can
create or destroy persistent burst buffers.
This is only used by the datawarp plugin.
PrivateData [#OPT_PrivateData](https://slurm.schedmd.com/burst_buffer.conf.html) If set, then only Slurm operators and the burst buffer owner can see burst
buffer data.
TeardownFailure [#OPT_TeardownFailure](https://slurm.schedmd.com/burst_buffer.conf.html) If set, then teardown a burst buffer after file staging error. Otherwise
preserve the burst buffer for analysis and manual teardown.
GetSysState [#OPT_GetSysState](https://slurm.schedmd.com/burst_buffer.conf.html) Fully qualified path name of a program which will return the current burst
buffer state.
For the DataWarp plugin, this should be the path of the dw_wlm_cli command
and its default value is /opt/cray/dw_wlm/default/bin/dw_wlm_cli.
This is not used by the lua plugin.
GetSysStatus [#OPT_GetSysStatus](https://slurm.schedmd.com/burst_buffer.conf.html) Fully qualified path name of a program which will return the current burst
buffer status.
For the DataWarp plugin, this should be the path of the dwstat command
and its default value is /opt/cray/dws/default/bin/dwstat.
This is not used by the lua plugin.
OtherTimeout [#OPT_OtherTimeout](https://slurm.schedmd.com/burst_buffer.conf.html) If a burst buffer operation (other than job validation, stage in, or stage out)
runs for longer than this number of seconds, the job will be placed in a held
state.
A Slurm administrator will be required to release the job.
By default there is a 300 second (5 minute) timeout for these operations.
Also see StageInTimeout , StageOutTimeout , and ValidateTimeout
options.
For the lua plugin, the maximum timeout value is 2073600 seconds (24 days).
PollInterval [#OPT_PollInterval](https://slurm.schedmd.com/burst_buffer.conf.html) This option only applies to the lua plugin.
If the test_data_{in|out} hooks return success and "BUSY", then they will be
called again after waiting for the specified number of seconds. The default
value is 15 seconds.
PrivateData [#OPT_PrivateData_1](https://slurm.schedmd.com/burst_buffer.conf.html) If set to "true" then users will only be able to view burst buffers they can
use.
Slurm administrators will still be able to view all burst buffers.
By default, users can view all burst buffers.
StageInTimeout [#OPT_StageInTimeout](https://slurm.schedmd.com/burst_buffer.conf.html) If the stage in of files for a job takes more than this number of seconds,
the burst buffer will be released and the job will be placed in a held state.
A Slurm administrator will be required to release the job.
By default there is a one day timeout for the stage in process.
For the lua plugin, the maximum timeout value is 2073600 seconds (24 days).
StageOutTimeout [#OPT_StageOutTimeout](https://slurm.schedmd.com/burst_buffer.conf.html) If the stage out of files for a job takes more than this number of seconds,
the burst buffer will be released and the job will be purged.
By default there is a one day timeout for the stage out process.
For the lua plugin, the maximum timeout value is 2073600 seconds (24 days).
ValidateTimeout [#OPT_ValidateTimeout](https://slurm.schedmd.com/burst_buffer.conf.html) If the validation of a job submission request takes more than this number of
seconds, the submission will be rejected.
The value of ValidateTimeout must be less than the value of
MessageTimeout configured in the slurm.conf file or job submission
requests may fail with a response timeout error.
By default there is a 5 second timeout for the validation operations.
In the lua plugin, because the validation operation cannot be killed, this
option is not used.
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/burst_buffer.conf.html)
Copyright (C) 2014-2022 SchedMD LLC.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/burst_buffer.conf.html)
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5)
## Index
[NAME](https://slurm.schedmd.com/burst_buffer.conf.html)
[DESCRIPTION](https://slurm.schedmd.com/burst_buffer.conf.html)
[COPYING](https://slurm.schedmd.com/burst_buffer.conf.html)
[SEE ALSO](https://slurm.schedmd.com/burst_buffer.conf.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
