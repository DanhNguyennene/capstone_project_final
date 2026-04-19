---
source_url: https://slurm.schedmd.com/strigger.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:30 UTC
title: "Slurm Workload Manager - strigger"
---

# strigger
Section: Slurm Commands (1)
Updated: Slurm Commands
[Index](https://slurm.schedmd.com/strigger.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/strigger.html)
strigger - Used to set, get or clear Slurm trigger information.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/strigger.html)
strigger --set [ OPTIONS ...]
strigger --get [ OPTIONS ...]
strigger --clear [ OPTIONS ...]
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/strigger.html)
strigger is used to set, get or clear Slurm trigger information.
Triggers include events such as a node failing, a job reaching its
time limit or a job terminating.
These events can cause actions such as the execution of an arbitrary
script.
Typical uses include notifying system administrators of node failures
and gracefully terminating a job when its time limit is approaching.
A hostlist expression for the nodelist or job ID is passed as an argument
to the program.
Trigger events are not processed instantly, but a check is performed for
trigger events on a periodic basis (currently every 15 seconds).
Any trigger events which occur within that interval will be compared
against the trigger programs set at the end of the time interval.
The trigger program will be executed once for any event occurring in
that interval.
The record of those events (e.g. nodes which went DOWN in the previous
15 seconds) will then be cleared.
The trigger program must set a new trigger before the end of the next
interval to ensure that no trigger events are missed OR the trigger must be
created with an argument of "--flags=PERM".
If desired, multiple trigger programs can be set for the same event.
NOTE : This command can only set triggers if run by the
user SlurmUser unless SlurmUser is configured as user root.
This is required for the slurmctld daemon to set the appropriate
user and group IDs for the executed program.
Also note that the trigger program is executed on the same node that the
slurmctld daemon uses rather than some allocated compute node.
To check the value of SlurmUser , run the command:
```text
scontrol show config | grep SlurmUser
```
## ARGUMENTS[#SECTION_ARGUMENTS](https://slurm.schedmd.com/strigger.html)
-C , --backup_slurmctld_assumed_control [#OPT_backup_slurmctld_assumed_control](https://slurm.schedmd.com/strigger.html) Trigger event when backup slurmctld assumes control.
-B , --backup_slurmctld_failure [#OPT_backup_slurmctld_failure](https://slurm.schedmd.com/strigger.html) Trigger an event when the backup slurmctld fails.
-c , --backup_slurmctld_resumed_operation [#OPT_backup_slurmctld_resumed_operation](https://slurm.schedmd.com/strigger.html) Trigger an event when the backup slurmctld resumes operation after failure.
--burst_buffer [#OPT_burst_buffer](https://slurm.schedmd.com/strigger.html) Trigger event when burst buffer error occurs.
--clear [#OPT_clear](https://slurm.schedmd.com/strigger.html) Clear or delete a previously defined event trigger.
The --id , --jobid or --user
option must be specified to identify the trigger(s) to
be cleared.
Only user root or the trigger's creator can delete a trigger.
-M , --clusters =< string >[#OPT_clusters](https://slurm.schedmd.com/strigger.html) Clusters to issue commands to.
Note that the slurmdbd must be up for this option to work properly, unless
running in a federation with FederationParameters=fed_display configured.
-d , --down [#OPT_down](https://slurm.schedmd.com/strigger.html) Trigger an event if the specified node goes into a DOWN state.
-D , --drained [#OPT_drained](https://slurm.schedmd.com/strigger.html) Trigger an event if the specified node goes into a DRAINED state.
--draining [#OPT_draining](https://slurm.schedmd.com/strigger.html) Trigger an event if the specified node goes into a DRAINING state,
before it is DRAINED.
-F , --fail [#OPT_fail](https://slurm.schedmd.com/strigger.html) Trigger an event if the specified node goes into a FAILING state.
-f , --fini [#OPT_fini](https://slurm.schedmd.com/strigger.html) Trigger an event when the specified job completes execution.
--flags =< flag >[#OPT_flags](https://slurm.schedmd.com/strigger.html) Associate flags with the reservation. Multiple flags should be comma separated.
Valid flags include:
PERM [#OPT_PERM](https://slurm.schedmd.com/strigger.html) Make the trigger permanent. Do not purge it after the event occurs.
--get [#OPT_get](https://slurm.schedmd.com/strigger.html) Show registered event triggers.
Options can be used for filtering purposes.
-i , --id =< id >[#OPT_id](https://slurm.schedmd.com/strigger.html) Trigger ID number.
-I , --idle [#OPT_idle](https://slurm.schedmd.com/strigger.html) Trigger an event if the specified node remains in an IDLE state
for at least the time period specified by the --offset
option. This can be useful to hibernate a node that remains idle,
thus reducing power consumption.
-j , --jobid =< id >[#OPT_jobid](https://slurm.schedmd.com/strigger.html) Job ID of interest.
NOTE : The --jobid option can not be used in conjunction
with the --node option. When the --jobid option is
used in conjunction with the --up or --down option,
all nodes allocated to that job will considered the nodes used as a
trigger event.
-n , --node [= host ][#OPT_node](https://slurm.schedmd.com/strigger.html) Host name(s) of interest.
By default, all nodes associated with the job (if --jobid
is specified) or on the system are considered for event triggers.
NOTE : The --node option can not be used in conjunction
with the --jobid option. When the --jobid option is
used in conjunction with the --up , --down or
--drained option,
all nodes allocated to that job will considered the nodes used as a
trigger event. Since this option's argument is optional, for proper
parsing the single letter option must be followed immediately with
the value and not include a space between them. For example "-ntux"
and not "-n tux".
-N , --noheader [#OPT_noheader](https://slurm.schedmd.com/strigger.html) Do not print the header when displaying a list of triggers.
-o , --offset =< seconds >[#OPT_offset](https://slurm.schedmd.com/strigger.html) The specified action should follow the event by this time interval.
Specify a negative value if action should preceded the event.
The default value is zero if no --offset option is specified.
The resolution of this time is about 20 seconds, so to execute
a script not less than five minutes prior to a job reaching its
time limit, specify --offset=320 (5 minutes plus 20 seconds).
-h , --primary_database_failure [#OPT_primary_database_failure](https://slurm.schedmd.com/strigger.html) Trigger an event when the primary database fails. This event is triggered when
the accounting plugin tries to open a connection with mysql and it fails and
the slurmctld needs the database for some operations.
-H , --primary_database_resumed_operation [#OPT_primary_database_resumed_operation](https://slurm.schedmd.com/strigger.html) Trigger an event when the primary database resumes operation after failure.
It happens when the connection to mysql from the accounting plugin is restored.
-g , --primary_slurmdbd_failure [#OPT_primary_slurmdbd_failure](https://slurm.schedmd.com/strigger.html) Trigger an event when the primary slurmdbd fails. The trigger is launched by
slurmctld in the occasions it tries to connect to slurmdbd, but receives no
response on the socket.
-G , --primary_slurmdbd_resumed_operation [#OPT_primary_slurmdbd_resumed_operation](https://slurm.schedmd.com/strigger.html) Trigger an event when the primary slurmdbd resumes operation after failure.
This event is triggered when opening the connection from slurmctld to slurmdbd
results in a response. It can happen also in different situations, periodically
every 15 seconds when checking the connection status, when saving state,
when agent queue is filling, and so on.
-e , --primary_slurmctld_acct_buffer_full [#OPT_primary_slurmctld_acct_buffer_full](https://slurm.schedmd.com/strigger.html) Trigger an event when primary slurmctld accounting buffer is full.
-a , --primary_slurmctld_failure [#OPT_primary_slurmctld_failure](https://slurm.schedmd.com/strigger.html) Trigger an event when the primary slurmctld fails.
-b , --primary_slurmctld_resumed_control [#OPT_primary_slurmctld_resumed_control](https://slurm.schedmd.com/strigger.html) Trigger an event when primary slurmctld resumes control.
-A , --primary_slurmctld_resumed_operation [#OPT_primary_slurmctld_resumed_operation](https://slurm.schedmd.com/strigger.html) Trigger an event when the primary slurmctld resuming operation after failure.
-p , --program =< path >[#OPT_program](https://slurm.schedmd.com/strigger.html) Execute the program at the specified fully qualified pathname
when the event occurs.
You may quote the path and include extra program arguments if desired.
The program will be executed as the user who sets the trigger.
If the program fails to terminate within 5 minutes, it will
be killed along with any spawned processes.
-Q , --quiet [#OPT_quiet](https://slurm.schedmd.com/strigger.html) Do not report non-fatal errors.
This can be useful to clear triggers which may have already been purged.
-r , --reconfig [#OPT_reconfig](https://slurm.schedmd.com/strigger.html) Trigger an event when the system configuration changes.
This is triggered when the slurmctld daemon reads its configuration file or
when a node state changes.
-R , --resume [#OPT_resume](https://slurm.schedmd.com/strigger.html) Trigger an event if the specified node is set to the RESUME state.
--set [#OPT_set](https://slurm.schedmd.com/strigger.html) Register an event trigger based upon the supplied options.
NOTE : An event is only triggered once. A new event trigger
must be set established for future events of the same type
to be processed.
Triggers can only be set if the command is run by the user
SlurmUser unless SlurmUser is configured as user root.
-t , --time [#OPT_time](https://slurm.schedmd.com/strigger.html) Trigger an event when the specified job's time limit is reached.
This must be used in conjunction with the --jobid option.
-u , --up [#OPT_up](https://slurm.schedmd.com/strigger.html) Trigger an event if the specified node is returned to service
from a DOWN state.
--user =< user_name_or_id >[#OPT_user](https://slurm.schedmd.com/strigger.html) Clear or get triggers created by the specified user.
For example, a trigger created by user root for a job created by user
adam could be cleared with an option --user=root .
Specify either a user name or user ID.
-v , --verbose [#OPT_verbose](https://slurm.schedmd.com/strigger.html) Print detailed event logging. This includes time-stamps on data structures,
record counts, etc.
-V , --version [#OPT_version](https://slurm.schedmd.com/strigger.html) Print version information and exit.
## OUTPUT FIELD DESCRIPTIONS[#SECTION_OUTPUT-FIELD-DESCRIPTIONS](https://slurm.schedmd.com/strigger.html)
TRIG_ID [#OPT_TRIG_ID](https://slurm.schedmd.com/strigger.html) Trigger ID number.
RES_TYPE [#OPT_RES_TYPE](https://slurm.schedmd.com/strigger.html) Resource type: job or node
RES_ID [#OPT_RES_ID](https://slurm.schedmd.com/strigger.html) Resource ID: job ID or host names or "*" for any host
TYPE [#OPT_TYPE](https://slurm.schedmd.com/strigger.html) Trigger type: time or fini (for jobs only),
down or up (for jobs or nodes), or
drained , idle or reconfig (for nodes only)
OFFSET [#OPT_OFFSET](https://slurm.schedmd.com/strigger.html) Time offset in seconds. Negative numbers indicated the action should
occur before the event (if possible)
USER [#OPT_USER](https://slurm.schedmd.com/strigger.html) Name of the user requesting the action
PROGRAM [#OPT_PROGRAM](https://slurm.schedmd.com/strigger.html) Pathname of the program to execute when the event occurs
## PERFORMANCE[#SECTION_PERFORMANCE](https://slurm.schedmd.com/strigger.html)
Executing strigger sends a remote procedure call to slurmctld . If
enough calls from strigger or other Slurm client commands that send remote
procedure calls to the slurmctld daemon come in at once, it can result in
a degradation of performance of the slurmctld daemon, possibly resulting
in a denial of service.
Do not run strigger or other Slurm client commands that send remote
procedure calls to slurmctld from loops in shell scripts or other
programs. Ensure that programs limit calls to strigger to the minimum
necessary for the information you are trying to gather.
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/strigger.html)
Some strigger options may be set via environment variables. These
environment variables, along with their corresponding options, are listed below.
(Note: Command line options will always override these settings.)
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/strigger.html) The location of the Slurm configuration file.
SLURM_DEBUG_FLAGS [#OPT_SLURM_DEBUG_FLAGS](https://slurm.schedmd.com/strigger.html) Specify debug flags for strigger to use. See DebugFlags in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for a full list of flags. The environment
variable takes precedence over the setting in the slurm.conf.
## EXAMPLES[#SECTION_EXAMPLES](https://slurm.schedmd.com/strigger.html)
Execute the program "/usr/sbin/primary_slurmctld_failure" whenever the primary slurmctld fails.
```text
$ cat /usr/sbin/primary_slurmctld_failure #!/bin/bash # Submit trigger for next primary slurmctld failure event strigger --set --primary_slurmctld_failure \ --program=/usr/sbin/primary_slurmctld_failure # Notify the administrator of the failure using e-mail /bin/mail [slurm_admin@site.com](mailto:slurm_admin@site.com) -s Primary_SLURMCTLD_FAILURE $ strigger --set --primary_slurmctld_failure \ --program=/usr/sbin/primary_slurmctld_failure
```
Execute the program "/usr/sbin/slurm_admin_notify" whenever any node in the cluster goes down. The subject line will include the node names which have entered the down state (passed as an argument to the script by Slurm).
```text
$ cat /usr/sbin/slurm_admin_notify #!/bin/bash # Submit trigger for next event strigger --set --node --down \ --program=/usr/sbin/slurm_admin_notify # Notify administrator using by e-mail /bin/mail [slurm_admin@site.com](mailto:slurm_admin@site.com) -s NodesDown:$* $ strigger --set --node --down \ --program=/usr/sbin/slurm_admin_notify
```
Execute the program "/usr/sbin/slurm_suspend_node" whenever any node in the cluster remains in the idle state for at least 600 seconds.
```text
$ strigger --set --node --idle --offset=600 \ --program=/usr/sbin/slurm_suspend_node
```
Execute the program "/home/joe/clean_up" when job 1234 is within 10 minutes of reaching its time limit.
```text
$ strigger --set --jobid=1234 --time --offset=-600 \ --program=/home/joe/clean_up
```
Execute the program "/home/joe/node_died" when any node allocated to job 1234 enters the DOWN state.
```text
$ strigger --set --jobid=1234 --down \ --program=/home/joe/node_died
```
Show all triggers associated with job 1235.
```text
$ strigger --get --jobid=1235 TRIG_ID RES_TYPE RES_ID TYPE OFFSET USER PROGRAM 123 job 1235 time -600 joe /home/bob/clean_up 125 job 1235 down 0 joe /home/bob/node_died
```
Delete event trigger 125.
```text
$ strigger --clear --id=125
```
Execute /home/joe/job_fini upon completion of job 1237.
```text
$ strigger --set --jobid=1237 --fini --program=/home/joe/job_fini
```
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/strigger.html)
Copyright (C) 2007 The Regents of the University of California.
Produced at Lawrence Livermore National Laboratory (cf, DISCLAIMER).
Copyright (C) 2008-2010 Lawrence Livermore National Security.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/strigger.html)
[scontrol](https://slurm.schedmd.com/scontrol.html) (1), [sinfo](https://slurm.schedmd.com/sinfo.html) (1), [squeue](https://slurm.schedmd.com/squeue.html) (1)
## Index
[NAME](https://slurm.schedmd.com/strigger.html)
[SYNOPSIS](https://slurm.schedmd.com/strigger.html)
[DESCRIPTION](https://slurm.schedmd.com/strigger.html)
[ARGUMENTS](https://slurm.schedmd.com/strigger.html)
[OUTPUT FIELD DESCRIPTIONS](https://slurm.schedmd.com/strigger.html)
[PERFORMANCE](https://slurm.schedmd.com/strigger.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/strigger.html)
[EXAMPLES](https://slurm.schedmd.com/strigger.html)
[COPYING](https://slurm.schedmd.com/strigger.html)
[SEE ALSO](https://slurm.schedmd.com/strigger.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
