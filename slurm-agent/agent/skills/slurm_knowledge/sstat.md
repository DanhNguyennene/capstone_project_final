---
source_url: https://slurm.schedmd.com/sstat.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:21:57 UTC
title: "Slurm Workload Manager - sstat"
---

# sstat
Section: Slurm Commands (1)
Updated: Slurm Commands
[Index](https://slurm.schedmd.com/sstat.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/sstat.html)
sstat - Display the status information of a running job/step.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/sstat.html)
sstat [ OPTIONS ...]
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/sstat.html)
Status information for running jobs invoked with Slurm.
The sstat command displays job status information for your analysis.
The sstat command displays information pertaining to CPU, Task, Node,
Resident Set Size (RSS) and Virtual Memory (VM).
You can tailor the output with the use of the --fields=
option to specify the fields to be shown.
For the root user, the sstat command displays job status data for any
job running on the system.
For the non-root user, the sstat output is limited to the user's jobs.
NOTE : The sstat command requires that the jobacct_gather
plugin be installed and operational.
NOTE : Availability of metrics rely on the jobacct_gather plugin
used. For example the jobacct_gather/cgroup in combination with cgroup/v2 does
not provide Virtual Memory metrics due to limitations in the kernel cgroups
interfaces and will show a 0 for the related fields.
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/sstat.html)
-a , --allsteps [#OPT_allsteps](https://slurm.schedmd.com/sstat.html) Print all steps for the given job(s) when no step is specified.
-o , --format , --fields [#OPT_format](https://slurm.schedmd.com/sstat.html) Comma separated list of fields.
(use '--helpformat' for a list of available fields).
NOTE : When using the format option for listing various fields you can put
a %NUMBER afterwards to specify how many characters should be printed.
i.e. format=name%30 will print 30 characters of field name right
justified. A -30 will print 30 characters left justified.
-h , --help [#OPT_help](https://slurm.schedmd.com/sstat.html) Displays a general help message.
-e , --helpformat [#OPT_helpformat](https://slurm.schedmd.com/sstat.html) Print a list of fields that can be specified with the '--format' option.
-j , --jobs [#OPT_jobs](https://slurm.schedmd.com/sstat.html) Format is <job(.step)>. Stat this job step or comma-separated list of
job steps. This option is required. The step portion will default to
the lowest numbered (not batch, extern, etc) step running if not specified,
unless the --allsteps flag is set where not specifying a step will result in
all running steps to be displayed.
NOTE : A step id of 'batch' will display the information about the batch
step.
NOTE : A step id of 'extern' will display the information about the
extern step. This step is only available when using PrologFlags=contain
--noconvert [#OPT_noconvert](https://slurm.schedmd.com/sstat.html) Don't convert units from their original type (e.g. 2048M won't be converted to
2G).
-n , --noheader [#OPT_noheader](https://slurm.schedmd.com/sstat.html) No heading will be added to the output. The default action is to
display a header.
-p , --parsable [#OPT_parsable](https://slurm.schedmd.com/sstat.html) output will be '|' delimited with a '|' at the end
-P , --parsable2 [#OPT_parsable2](https://slurm.schedmd.com/sstat.html) output will be '|' delimited without a '|' at the end
-i , --pidformat [#OPT_pidformat](https://slurm.schedmd.com/sstat.html) Predefined format to list the pids running for each job step.
(JobId,Nodes,Pids)
--usage [#OPT_usage](https://slurm.schedmd.com/sstat.html) Display a command usage summary.
-v , --verbose [#OPT_verbose](https://slurm.schedmd.com/sstat.html) Primarily for debugging purposes, report the state of various
variables during processing.
-V , --version [#OPT_version](https://slurm.schedmd.com/sstat.html) Print version.
### Job Status Fields[#SECTION_Job-Status-Fields](https://slurm.schedmd.com/sstat.html)
Descriptions of each field option can be found below.
Note that the Ave*, Max* and Min* accounting fields look at the values for
all the tasks of each step in a job and return the average, maximum or minimum
values of the task for that job step. For example, for MaxRSS, the returned
value is the maximum memory consumption seen by one of the tasks of the step,
and MaxRSSTask shows which task it is.
AllocTRES [#OPT_AllocTRES](https://slurm.schedmd.com/sstat.html) Allocated TRES of all tasks in job.
AveCPU [#OPT_AveCPU](https://slurm.schedmd.com/sstat.html) Average (system + user) CPU time of all tasks in job.
AveCPUFreq [#OPT_AveCPUFreq](https://slurm.schedmd.com/sstat.html) Average weighted CPU frequency of all tasks in job, in kHz.
AveDiskRead [#OPT_AveDiskRead](https://slurm.schedmd.com/sstat.html) Average number of bytes read by all tasks in job.
AveDiskWrite [#OPT_AveDiskWrite](https://slurm.schedmd.com/sstat.html) Average number of bytes written by all tasks in job.
AvePages [#OPT_AvePages](https://slurm.schedmd.com/sstat.html) Average number of page faults of all tasks in job.
AveRSS [#OPT_AveRSS](https://slurm.schedmd.com/sstat.html) Average resident set size of all tasks in job.
AveVMSize [#OPT_AveVMSize](https://slurm.schedmd.com/sstat.html) Average Virtual Memory size of all tasks in job.
ConsumedEnergy [#OPT_ConsumedEnergy](https://slurm.schedmd.com/sstat.html) Total energy consumed by all tasks in job, in joules.
Note: Only in case of exclusive job allocation this value
reflects the jobs' real energy consumption.
JobID [#OPT_JobID](https://slurm.schedmd.com/sstat.html) The number of the job or job step.
It is in the form:
job.jobstep
MaxDiskRead [#OPT_MaxDiskRead](https://slurm.schedmd.com/sstat.html) Maximum number of bytes read by all tasks in job.
MaxDiskReadNode [#OPT_MaxDiskReadNode](https://slurm.schedmd.com/sstat.html) The node on which the maxdiskread occurred.
MaxDiskReadTask [#OPT_MaxDiskReadTask](https://slurm.schedmd.com/sstat.html) The task ID where the maxdiskread occurred.
MaxDiskWrite [#OPT_MaxDiskWrite](https://slurm.schedmd.com/sstat.html) Maximum number of bytes written by all tasks in job.
MaxDiskWriteNode [#OPT_MaxDiskWriteNode](https://slurm.schedmd.com/sstat.html) The node on which the maxdiskwrite occurred.
MaxDiskWriteTask [#OPT_MaxDiskWriteTask](https://slurm.schedmd.com/sstat.html) The task ID where the maxdiskwrite occurred.
MaxPages [#OPT_MaxPages](https://slurm.schedmd.com/sstat.html) Maximum number of page faults of all tasks in job.
MaxPagesNode [#OPT_MaxPagesNode](https://slurm.schedmd.com/sstat.html) The node on which the maxpages occurred.
MaxPagesTask [#OPT_MaxPagesTask](https://slurm.schedmd.com/sstat.html) The task ID where the maxpages occurred.
MaxRSS [#OPT_MaxRSS](https://slurm.schedmd.com/sstat.html) Maximum resident set size of all tasks in job.
MaxRSSNode [#OPT_MaxRSSNode](https://slurm.schedmd.com/sstat.html) The node on which the maxrss occurred.
MaxRSSTask [#OPT_MaxRSSTask](https://slurm.schedmd.com/sstat.html) The task ID where the maxrss occurred.
MaxVMSize [#OPT_MaxVMSize](https://slurm.schedmd.com/sstat.html) Maximum Virtual Memory size of all tasks in job.
MaxVMSizeNode [#OPT_MaxVMSizeNode](https://slurm.schedmd.com/sstat.html) The node on which the maxvsize occurred.
MaxVMSizeTask [#OPT_MaxVMSizeTask](https://slurm.schedmd.com/sstat.html) The task ID where the maxvsize occurred.
MinCPU [#OPT_MinCPU](https://slurm.schedmd.com/sstat.html) Minimum (system + user) CPU time of all tasks in job.
MinCPUNode [#OPT_MinCPUNode](https://slurm.schedmd.com/sstat.html) The node on which the mincpu occurred.
MinCPUTask [#OPT_MinCPUTask](https://slurm.schedmd.com/sstat.html) The task ID where the mincpu occurred.
NTasks [#OPT_NTasks](https://slurm.schedmd.com/sstat.html) Total number of tasks in a job or step.
ReqCPUFreq [#OPT_ReqCPUFreq](https://slurm.schedmd.com/sstat.html) Requested CPU frequency for the step, in kHz.
TresUsageInAve [#OPT_TresUsageInAve](https://slurm.schedmd.com/sstat.html) Tres average usage in by all tasks in job.
NOTE : If corresponding TresUsageInMaxTask is -1 the metric is node
centric instead of task.
TresUsageInMax [#OPT_TresUsageInMax](https://slurm.schedmd.com/sstat.html) Tres maximum usage in by all tasks in job.
NOTE : If corresponding TresUsageInMaxTask is -1 the metric is node
centric instead of task.
TresUsageInMaxNode [#OPT_TresUsageInMaxNode](https://slurm.schedmd.com/sstat.html) Node for which each maximum TRES usage out occurred.
TresUsageInMaxTask [#OPT_TresUsageInMaxTask](https://slurm.schedmd.com/sstat.html) Task for which each maximum TRES usage out occurred.
TresUsageOutAve [#OPT_TresUsageOutAve](https://slurm.schedmd.com/sstat.html) Tres average usage out by all tasks in job.
NOTE : If corresponding TresUsageOutMaxTask is -1 the metric is node
centric instead of task.
TresUsageOutMax [#OPT_TresUsageOutMax](https://slurm.schedmd.com/sstat.html) Tres maximum usage out by all tasks in job.
NOTE : If corresponding TresUsageOutMaxTask is -1 the metric is node
centric instead of task.
TresUsageOutMaxNode [#OPT_TresUsageOutMaxNode](https://slurm.schedmd.com/sstat.html) Node for which each maximum TRES usage out occurred.
TresUsageOutMaxTask [#OPT_TresUsageOutMaxTask](https://slurm.schedmd.com/sstat.html) Task for which each maximum TRES usage out occurred.
## PERFORMANCE[#SECTION_PERFORMANCE](https://slurm.schedmd.com/sstat.html)
Executing sstat sends a remote procedure call to slurmctld . If
enough calls from sstat or other Slurm client commands that send remote
procedure calls to the slurmctld daemon come in at once, it can result in
a degradation of performance of the slurmctld daemon, possibly resulting
in a denial of service.
Do not run sstat or other Slurm client commands that send remote procedure
calls to slurmctld from loops in shell scripts or other programs. Ensure
that programs limit calls to sstat to the minimum necessary for the
information you are trying to gather.
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/sstat.html)
Some sstat options may be set via environment variables. These
environment variables, along with their corresponding options, are listed below.
(Note: Command line options will always override these settings.)
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/sstat.html) The location of the Slurm configuration file.
SLURM_DEBUG_FLAGS [#OPT_SLURM_DEBUG_FLAGS](https://slurm.schedmd.com/sstat.html) Specify debug flags for sstat to use. See DebugFlags in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for a full list of flags. The environment
variable takes precedence over the setting in the slurm.conf.
## EXAMPLES[#SECTION_EXAMPLES](https://slurm.schedmd.com/sstat.html)
Display job step information for job 11 with the specified fields:
```text
$ sstat --format=AveCPU,AvePages,AveRSS,AveVMSize,JobID -j 11 25:02.000 0K 1.37M 5.93M 9.0
```
Display job step information for job 11 with the specified fields in a parsable format:
```text
$ sstat -p --format=AveCPU,AvePages,AveRSS,AveVMSize,JobID -j 11 25:02.000|0K|1.37M|5.93M|9.0|
```
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/sstat.html)
Copyright (C) 2009 Lawrence Livermore National Security.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/sstat.html)
[sacct](https://slurm.schedmd.com/sacct.html) (1)
## Index
[NAME](https://slurm.schedmd.com/sstat.html)
[SYNOPSIS](https://slurm.schedmd.com/sstat.html)
[DESCRIPTION](https://slurm.schedmd.com/sstat.html)
[OPTIONS](https://slurm.schedmd.com/sstat.html)
[Job Status Fields](https://slurm.schedmd.com/sstat.html)
[PERFORMANCE](https://slurm.schedmd.com/sstat.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/sstat.html)
[EXAMPLES](https://slurm.schedmd.com/sstat.html)
[COPYING](https://slurm.schedmd.com/sstat.html)
[SEE ALSO](https://slurm.schedmd.com/sstat.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
