---
source_url: https://slurm.schedmd.com/scancel.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:21 UTC
title: "Slurm Workload Manager - scancel"
---

# scancel
Section: Slurm Commands (1)
Updated: Slurm Commands
[Index](https://slurm.schedmd.com/scancel.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/scancel.html)
scancel - Used to signal jobs or job steps that are under the control of Slurm.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/scancel.html)
scancel [ OPTIONS ...] [ job_id [_ array_id ][. step_id ]] [ job_id [_ array_id ][. step_id ]...]
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/scancel.html)
scancel is used to signal or cancel jobs, job arrays or job steps.
An arbitrary number of jobs or job steps may be signaled using job
specification filters or a space separated list of specific job and/or
job step IDs.
If the job ID of a job array is specified with an array ID value and the job
associated with the array ID value has been split from the array, then only that
job array element will be cancelled.
If the job ID of a job array is specified without an array ID value or the
array ID value corresponds to a job that has not been split from the array,
then all job array elements will be cancelled.
While a heterogeneous job is in a PENDING state, only the entire job can be
cancelled rather than its individual components.
A request to cancel an individual component of a heterogeneous job while in
a PENDING state will return an error.
After the job has begun execution, an individual component can be cancelled
except for component zero. If component zero is cancelled, the whole het job is
cancelled.
A job or job step can only be signaled by the owner of that job or user root.
If an attempt is made by an unauthorized user to signal a job or job step, an
error message will be printed and the job will not be signaled.
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/scancel.html)
-A , --account = account [#OPT_account](https://slurm.schedmd.com/scancel.html) Restrict the scancel operation to jobs under this charge account.
--admin-comment = comment [#OPT_admin-comment](https://slurm.schedmd.com/scancel.html) Set the AdminComment on the job while canceling jobs. User must have
Administrator privileges on the system.
-b , --batch [#OPT_batch](https://slurm.schedmd.com/scancel.html) By default, signals other than SIGKILL are not sent to the batch step (the shell
script). With this option scancel signals only the batch step, but not
any other steps.
This is useful when the shell script has to trap the signal and take some
application defined action.
Most shells cannot handle signals while a command is running (i.e. is a child
process of the batch step), so the shell needs to wait until the command ends to
then handle the signal.
Children of the batch step are not signaled with this option. If this is
desired, use -f , --full instead.
NOTE : If used with -f , --full , this option is ignored.
NOTE : This option is not applicable if step_id is specified.
NOTE : The shell itself may exit upon receipt of many signals.
You may avoid this by explicitly trap signals within the shell
script (e.g. "trap <arg> <signals>"). See the shell documentation
for details.
-M , --clusters =< string >[#OPT_clusters](https://slurm.schedmd.com/scancel.html) Cluster to issue commands to. Implies --ctld .
Note that the slurmdbd must be up for this option to work properly, unless
running in a federation with FederationParameters=fed_display configured.
--ctld [#OPT_ctld](https://slurm.schedmd.com/scancel.html) If this option is not used with --interactive ,
--sibling , federated job ids, or specific step ids, then this issues a
single request to the slurmctld to signal all jobs matching the specified
filters. This greatly improves the performance of slurmctld and scancel.
Otherwise, this option causes scancel to send each job signal request to the
slurmctld daemon rather than directly to the slurmd daemons, which increases
overhead, but offers better fault tolerance. --ctld is the default
behavior on when the --clusters option is used.
-c , --cron [#OPT_cron](https://slurm.schedmd.com/scancel.html) Confirm request to cancel a job submitted by scrontab. This option only has
effect with the "explicit_scancel" option is set in ScronParameters .
-f , --full [#OPT_full](https://slurm.schedmd.com/scancel.html) By default, signals other than SIGKILL are not sent to the batch step (the shell
script). With this option scancel also signals the batch script and its
children processes.
Most shells cannot handle signals while a command is running (i.e. is a child
process of the batch step), so the shell needs to wait until the command ends to
then handle the signal.
Unlike -b , --batch , children of the batch step
are also signaled with this option.
NOTE : srun steps are also children of the batch step, so steps are also
signaled with this option.
--help [#OPT_help](https://slurm.schedmd.com/scancel.html) Print a help message describing all scancel options.
-H , --hurry [#OPT_hurry](https://slurm.schedmd.com/scancel.html) Do not stage out any burst buffer data.
-i , --interactive [#OPT_interactive](https://slurm.schedmd.com/scancel.html) Interactive mode. Confirm each job_id.step_id before performing the cancel operation.
-n , --jobname = job_name , --name = job_name [#OPT_jobname](https://slurm.schedmd.com/scancel.html) Restrict the scancel operation to jobs with this job name.
--me [#OPT_me](https://slurm.schedmd.com/scancel.html) Restrict the scancel operation to jobs owned by the current user.
-w , --nodelist= host1,host2,... [#OPT_nodelist=](https://slurm.schedmd.com/scancel.html) Cancel any jobs using any of the given hosts. The list may be specified as
a comma-separated list of hosts, a range of hosts (host[1-5,7,...] for
example), or a filename. The host list will be assumed to be a filename only
if it contains a "/" character.
-p , --partition = partition_name [#OPT_partition](https://slurm.schedmd.com/scancel.html) Restrict the scancel operation to jobs in this partition.
-q , --qos = qos [#OPT_qos](https://slurm.schedmd.com/scancel.html) Restrict the scancel operation to jobs with this quality of service.
-Q , --quiet [#OPT_quiet](https://slurm.schedmd.com/scancel.html) Do not report an error if the specified job is already completed.
This option is incompatible with the --verbose option.
-R , --reservation = reservation_name [#OPT_reservation](https://slurm.schedmd.com/scancel.html) Restrict the scancel operation to jobs with this reservation name.
--sibling = cluster_name [#OPT_sibling](https://slurm.schedmd.com/scancel.html) Remove an active sibling job from a federated job.
-s , --signal = signal_name [#OPT_signal](https://slurm.schedmd.com/scancel.html) The name or number of the signal to send. If this option is not used
the specified job or step will be terminated.
-t , --state = job_state_name [#OPT_state](https://slurm.schedmd.com/scancel.html) Restrict the scancel operation to jobs in this
state. job_state_name may have a value of either "PENDING",
"RUNNING" or "SUSPENDED".
--usage [#OPT_usage](https://slurm.schedmd.com/scancel.html) Print a brief help message listing the scancel options.
-u , --user = user_name [#OPT_user](https://slurm.schedmd.com/scancel.html) Restrict the scancel operation to jobs owned by the given user.
-v , --verbose [#OPT_verbose](https://slurm.schedmd.com/scancel.html) Print additional logging. Multiple v's increase logging detail.
This option is incompatible with the --quiet option.
-V , --version [#OPT_version](https://slurm.schedmd.com/scancel.html) Print the version number of the scancel command.
--wckey = wckey [#OPT_wckey](https://slurm.schedmd.com/scancel.html) Restrict the scancel operation to jobs using this workload
characterization key.
## ARGUMENTS[#SECTION_ARGUMENTS](https://slurm.schedmd.com/scancel.html)
job_id [#OPT_job_id](https://slurm.schedmd.com/scancel.html) The Slurm job ID to be signaled.
step_id [#OPT_step_id](https://slurm.schedmd.com/scancel.html) The step ID of the job step to be signaled.
If not specified, the operation is performed at the level of a job.
If neither --batch nor --signal are used,
the entire job will be terminated.
When --batch is used, the batch shell processes will be signaled.
The child processes of the shell will not be signaled by Slurm, but
the shell may forward the signal.
When --batch is not used but --signal is used,
then all job steps will be signaled, but the batch script itself
will not be signaled.
## PERFORMANCE[#SECTION_PERFORMANCE](https://slurm.schedmd.com/scancel.html)
When executing scancel without the --ctld option; or with the
--ctld option and --interactive , --sibling , or specific
step ids; a remote procedure call is sent to slurmctld to get all the
jobs. scancel then sends a signal job remote procedure call for each job
that matches the requested filters.
When executing scancel with the --ctld option and without
--interactive , --sibling , or specific step ids, a single
remote procedure call is sent to slurmctld to signal all jobs matching
the requested filters. It is therefore recommended to use the --ctld
option in order to reduce the number of remote procedure calls sent to the
slurmctld .
If enough calls from scancel or other Slurm client commands that send
remote procedure calls to the slurmctld daemon come in at once, it can
result in a degradation of performance of the slurmctld daemon, possibly
resulting in a denial of service.
Do not run scancel or other Slurm client commands that send remote
procedure calls to slurmctld from loops in shell scripts or other
programs. Ensure that programs limit calls to scancel to the minimum
necessary for the information you are trying to gather.
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/scancel.html)
Some scancel options may be set via environment variables. These
environment variables, along with their corresponding options, are listed below.
(Note: Command line options will always override these settings.)
SCANCEL_ACCOUNT [#OPT_SCANCEL_ACCOUNT](https://slurm.schedmd.com/scancel.html) -A , --account = account
SCANCEL_BATCH [#OPT_SCANCEL_BATCH](https://slurm.schedmd.com/scancel.html) -b, --batch
SCANCEL_CTLD [#OPT_SCANCEL_CTLD](https://slurm.schedmd.com/scancel.html) --ctld
SCANCEL_CRON [#OPT_SCANCEL_CRON](https://slurm.schedmd.com/scancel.html) -c, --cron
SCANCEL_FULL [#OPT_SCANCEL_FULL](https://slurm.schedmd.com/scancel.html) -f, --full
SCANCEL_HURRY [#OPT_SCANCEL_HURRY](https://slurm.schedmd.com/scancel.html) -H , --hurry
SCANCEL_INTERACTIVE [#OPT_SCANCEL_INTERACTIVE](https://slurm.schedmd.com/scancel.html) -i , --interactive
SCANCEL_NAME [#OPT_SCANCEL_NAME](https://slurm.schedmd.com/scancel.html) -n , --name = job_name
SCANCEL_PARTITION [#OPT_SCANCEL_PARTITION](https://slurm.schedmd.com/scancel.html) -p , --partition = partition_name
SCANCEL_QOS [#OPT_SCANCEL_QOS](https://slurm.schedmd.com/scancel.html) -q , --qos = qos
SCANCEL_STATE [#OPT_SCANCEL_STATE](https://slurm.schedmd.com/scancel.html) -t , --state = job_state_name
SCANCEL_USER [#OPT_SCANCEL_USER](https://slurm.schedmd.com/scancel.html) -u , --user = user_name
SCANCEL_VERBOSE [#OPT_SCANCEL_VERBOSE](https://slurm.schedmd.com/scancel.html) -v , --verbose
SCANCEL_WCKEY [#OPT_SCANCEL_WCKEY](https://slurm.schedmd.com/scancel.html) --wckey = wckey
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/scancel.html) The location of the Slurm configuration file.
SLURM_CLUSTERS [#OPT_SLURM_CLUSTERS](https://slurm.schedmd.com/scancel.html) -M , --clusters
SLURM_DEBUG_FLAGS [#OPT_SLURM_DEBUG_FLAGS](https://slurm.schedmd.com/scancel.html) Specify debug flags for scancel to use. See DebugFlags in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for a full list of flags. The environment
variable takes precedence over the setting in the slurm.conf.
## NOTES[#SECTION_NOTES](https://slurm.schedmd.com/scancel.html)
If multiple filters are supplied (e.g. --partition and --name )
only the jobs satisfying all of the filtering options will be signaled.
Cancelling a job step will not result in the job being terminated.
The job must be cancelled to release a resource allocation.
To cancel a job, invoke scancel without --signal option. This
will send first a SIGCONT to all steps to eventually wake them up followed by
a SIGTERM, then wait the KillWait duration defined in the slurm.conf file
and finally if they have not terminated send a SIGKILL. This gives
time for the running job/step(s) to clean up.
If a signal value of "KILL" is sent to an entire job, this will cancel
the active job steps but not cancel the job itself.
## AUTHORIZATION[#SECTION_AUTHORIZATION](https://slurm.schedmd.com/scancel.html)
When using SlurmDBD, users who have an AdminLevel defined (Operator
or Admin) and users who are account coordinators are given the
authority to invoke scancel on other users jobs.
## EXAMPLES[#SECTION_EXAMPLES](https://slurm.schedmd.com/scancel.html)
Send SIGTERM to steps 1 and 3 of job 1234:
```text
$ scancel --signal=TERM 1234.1 1234.3
```
Cancel job 1234 along with all of its steps:
```text
$ scancel 1234
```
Send SIGKILL to all steps of job 1235, but do not cancel the job itself:
```text
$ scancel --signal=KILL 1235
```
Send SIGUSR1 to the batch shell processes of job 1236:
```text
$ scancel --signal=USR1 --batch 1236
```
Cancel all pending jobs belonging to user "bob" in partition "debug":
```text
$ scancel --state=PENDING --user=bob --partition=debug
```
Cancel only array ID 4 of job array 1237
```text
$ scancel 1237_4
```
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/scancel.html)
Copyright (C) 2002-2007 The Regents of the University of California.
Produced at Lawrence Livermore National Laboratory (cf, DISCLAIMER).
Copyright (C) 2008-2011 Lawrence Livermore National Security.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/scancel.html)
slurm_kill_job (3), slurm_kill_job_step (3)
## Index
[NAME](https://slurm.schedmd.com/scancel.html)
[SYNOPSIS](https://slurm.schedmd.com/scancel.html)
[DESCRIPTION](https://slurm.schedmd.com/scancel.html)
[OPTIONS](https://slurm.schedmd.com/scancel.html)
[ARGUMENTS](https://slurm.schedmd.com/scancel.html)
[PERFORMANCE](https://slurm.schedmd.com/scancel.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/scancel.html)
[NOTES](https://slurm.schedmd.com/scancel.html)
[AUTHORIZATION](https://slurm.schedmd.com/scancel.html)
[EXAMPLES](https://slurm.schedmd.com/scancel.html)
[COPYING](https://slurm.schedmd.com/scancel.html)
[SEE ALSO](https://slurm.schedmd.com/scancel.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
