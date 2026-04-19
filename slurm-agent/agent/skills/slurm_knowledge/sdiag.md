---
source_url: https://slurm.schedmd.com/sdiag.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:22 UTC
title: "Slurm Workload Manager - sdiag"
---

# sdiag
Section: Slurm Commands (1)
Updated: Slurm Commands
[Index](https://slurm.schedmd.com/sdiag.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/sdiag.html)
sdiag - Scheduling diagnostic tool for Slurm
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/sdiag.html)
sdiag
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/sdiag.html)
sdiag shows information related to slurmctld execution about: threads, agents,
jobs, and scheduling algorithms. The goal is to obtain data from slurmctld
behavior helping to adjust configuration parameters or queues policies. The
main reason behind is to know Slurm behavior under systems with a high throughput.
It has two execution modes. The default mode --all shows several counters
and statistics explained later, and there is another execution option
--reset for resetting those values.
Values are reset at midnight UTC time by default.
The first block of information is related to global slurmctld execution:
Server thread count [#OPT_Server-thread-count](https://slurm.schedmd.com/sdiag.html) The number of current active slurmctld threads. A high number would mean a high
load processing events like job submissions, jobs dispatching, jobs completing,
etc. If this is often close to MAX_SERVER_THREADS it could point to a potential
bottleneck.
Agent queue size [#OPT_Agent-queue-size](https://slurm.schedmd.com/sdiag.html) Slurm design has scalability in mind and sending messages to thousands of nodes
is not a trivial task. The agent mechanism helps to control communication
between slurmctld and the slurmd daemons for a best effort. This value denotes
the count of enqueued outgoing RPC requests in an internal retry list.
Agent count [#OPT_Agent-count](https://slurm.schedmd.com/sdiag.html) Number of agent threads. Each of these agent threads can create in turn a group
of up to 2 + AGENT_THREAD_COUNT active threads at a time.
Agent thread count [#OPT_Agent-thread-count](https://slurm.schedmd.com/sdiag.html) Total count of active threads created by all the agent threads.
DBD Agent queue size [#OPT_DBD-Agent-queue-size](https://slurm.schedmd.com/sdiag.html) Slurm queues up the messages intended for the SlurmDBD and processes them in a
separate thread. If the SlurmDBD, or database, is down then this number will
increase.
The max queue size is configured in the slurm.conf with MaxDBDMsgs. If this number begins to grow more than half of the max queue size, the slurmdbd
and the database should be investigated immediately.
Jobs submitted [#OPT_Jobs-submitted](https://slurm.schedmd.com/sdiag.html) Number of jobs submitted since last reset
Jobs started [#OPT_Jobs-started](https://slurm.schedmd.com/sdiag.html) Number of jobs started since last reset. This includes backfilled jobs.
Jobs completed [#OPT_Jobs-completed](https://slurm.schedmd.com/sdiag.html) Number of jobs completed since last reset.
Jobs canceled [#OPT_Jobs-canceled](https://slurm.schedmd.com/sdiag.html) Number of jobs canceled since last reset.
Jobs failed [#OPT_Jobs-failed](https://slurm.schedmd.com/sdiag.html) Number of jobs failed due to slurmd or other internal issues since last reset.
Job states ts: [#OPT_Job-states-ts:](https://slurm.schedmd.com/sdiag.html) Lists the timestamp of when the following job state counts were gathered.
Jobs pending: [#OPT_Jobs-pending:](https://slurm.schedmd.com/sdiag.html) Number of jobs pending at the given time of the time stamp above.
Jobs running: [#OPT_Jobs-running:](https://slurm.schedmd.com/sdiag.html) Number of jobs running at the given time of the time stamp above.
The next block of information is related to main scheduling algorithm based
on jobs priorities. A scheduling cycle implies to get the job_write_lock lock,
then trying to get resources for jobs pending, starting from the most priority
one and going in descending order. Once a job can not get the resources the
loop keeps going but just for jobs requesting other partitions. Jobs with
dependencies or affected by accounts limits are not processed.
Last cycle [#OPT_Last-cycle](https://slurm.schedmd.com/sdiag.html) Time in microseconds for last scheduling cycle.
Max cycle [#OPT_Max-cycle](https://slurm.schedmd.com/sdiag.html) Maximum time in microseconds for any scheduling cycle since last reset.
Total cycles [#OPT_Total-cycles](https://slurm.schedmd.com/sdiag.html) Total run time in microseconds for all scheduling cycles since last reset.
Scheduling is performed periodically and (depending upon configuration)
when a job is submitted or a job is completed.
Mean cycle [#OPT_Mean-cycle](https://slurm.schedmd.com/sdiag.html) Mean time in microseconds for all scheduling cycles since last reset.
Mean depth cycle [#OPT_Mean-depth-cycle](https://slurm.schedmd.com/sdiag.html) Mean of cycle depth. Depth means number of jobs processed in a scheduling cycle.
Cycles per minute [#OPT_Cycles-per-minute](https://slurm.schedmd.com/sdiag.html) Counter of scheduling executions per minute.
Last queue length [#OPT_Last-queue-length](https://slurm.schedmd.com/sdiag.html) Length of jobs pending queue.
The next block of information is related to backfilling scheduling algorithm.
A backfilling scheduling cycle implies to get locks for jobs, nodes and
partitions objects then trying to get resources for jobs pending. Jobs are
processed based on priorities. If a job can not get resources the algorithm
calculates when it could get them obtaining a future start time for the job.
Then next job is processed and the algorithm tries to get resources for that
job but avoiding to affect the previous ones , and again it calculates
the future start time if not current resources available. The backfilling
algorithm takes more time for each new job to process since more priority jobs
can not be affected. The algorithm itself takes measures for avoiding a long
execution cycle and for taking all the locks for too long.
Total backfilled jobs (since last slurm start) [#OPT_Total-backfilled-jobs-(since-last-slurm-start)](https://slurm.schedmd.com/sdiag.html) Number of jobs started thanks to backfilling since last slurm start.
Total backfilled jobs (since last stats cycle start) [#OPT_Total-backfilled-jobs-(since-last-stats-cycle-start)](https://slurm.schedmd.com/sdiag.html) Number of jobs started thanks to backfilling since last time stats where reset.
By default these values are reset at midnight UTC time.
Total backfilled heterogeneous job components [#OPT_Total-backfilled-heterogeneous-job-components](https://slurm.schedmd.com/sdiag.html) Number of heterogeneous job components started thanks to backfilling since
last Slurm start.
Total cycles [#OPT_Total-cycles_1](https://slurm.schedmd.com/sdiag.html) Number of backfill scheduling cycles since last reset
Last cycle when [#OPT_Last-cycle-when](https://slurm.schedmd.com/sdiag.html) Time when last backfill scheduling cycle happened in the format
"weekday Month MonthDay hour:minute.seconds year"
Last cycle [#OPT_Last-cycle_1](https://slurm.schedmd.com/sdiag.html) Time in microseconds of last backfill scheduling cycle.
It counts only execution time, removing sleep time inside a scheduling cycle
when it executes for an extended period time.
Note that locks are released during the sleep time so that other work can
proceed.
Max cycle [#OPT_Max-cycle_1](https://slurm.schedmd.com/sdiag.html) Time in microseconds of maximum backfill scheduling cycle execution since last reset.
It counts only execution time, removing sleep time inside a scheduling cycle
when it executes for an extended period time.
Note that locks are released during the sleep time so that other work can
proceed.
Mean cycle [#OPT_Mean-cycle_1](https://slurm.schedmd.com/sdiag.html) Mean time in microseconds of backfilling scheduling cycles since last reset.
Last depth cycle [#OPT_Last-depth-cycle](https://slurm.schedmd.com/sdiag.html) Number of processed jobs during last backfilling scheduling cycle. It counts
every job even if that job can not be started due to dependencies or limits.
Last depth cycle (try sched) [#OPT_Last-depth-cycle-(try-sched)](https://slurm.schedmd.com/sdiag.html) Number of processed jobs during last backfilling scheduling cycle. It counts
only jobs with a chance to start using available resources. These
jobs consume more scheduling time than jobs which are found can not be started
due to dependencies or limits.
Depth Mean [#OPT_Depth-Mean](https://slurm.schedmd.com/sdiag.html) Mean count of jobs processed during all backfilling scheduling cycles since last
reset.
Jobs which are found to be ineligible to run when examined by the backfill
scheduler are not counted (e.g. jobs submitted to multiple partitions and
already started, jobs which have reached a QOS or account limit such as
maximum running jobs for an account, etc).
Depth Mean (try sched) [#OPT_Depth-Mean-(try-sched)](https://slurm.schedmd.com/sdiag.html) The subset of Depth Mean that the backfill scheduler attempted to schedule.
Last queue length [#OPT_Last-queue-length_1](https://slurm.schedmd.com/sdiag.html) Number of jobs pending to be processed by backfilling algorithm.
A job is counted once for each partition it is queued to use.
A pending job array will normally be counted as one job (tasks of a job array
which have already been started/requeued or individually modified will already
have individual job records and are each counted as a separate job).
Queue length Mean [#OPT_Queue-length-Mean](https://slurm.schedmd.com/sdiag.html) Mean count of jobs pending to be processed by backfilling algorithm.
A job is counted once for each partition it requested.
A pending job array will normally be counted as one job (tasks of a job array
which have already been started/requeued or individually modified will already
have individual job records and are each counted as a separate job).
Last table size [#OPT_Last-table-size](https://slurm.schedmd.com/sdiag.html) Count of different time slots tested by the backfill scheduler in its last
iteration.
Mean table size [#OPT_Mean-table-size](https://slurm.schedmd.com/sdiag.html) Mean count of different time slots tested by the backfill scheduler.
Larger counts increase the time required for the backfill operation.
The table size is influenced by many scheduling parameters, including:
bf_min_age_reserve, bf_min_prio_reserve, bf_resolution, and bf_window.
Latency for 1000 calls to gettimeofday() [#OPT_Latency-for-1000-calls-to-gettimeofday()](https://slurm.schedmd.com/sdiag.html) Latency of 1000 calls to the gettimeofday() syscall in microseconds,
as measured at controller startup.
The next blocks of information report the most frequently issued
remote procedure calls (RPCs), calls made for the Slurmctld daemon to perform
some action.
The fourth block reports the RPCs issued by message type.
You will need to look up those RPC codes in the Slurm source code by looking
them up in the file src/common/slurm_protocol_defs.h.
The report includes the number of times each RPC is invoked, the total time
consumed by all of those RPCs plus the average time consumed by each RPC in
microseconds.
The fifth block reports the RPCs issued by user ID, the total number of RPCs
they have issued, the total time consumed by all of those RPCs plus the average
time consumed by each RPC in microseconds.
RPCs statistics are collected for the life of the slurmctld process unless
explicitly --reset .
The sixth block of information, labeled Pending RPC Statistics, shows
information about pending outgoing RPCs on the slurmctld agent queue.
The first section of this block shows types of RPCs on the queue and the
count of each. The second section shows up to the first 25 individual RPCs
pending on the agent queue, including the type and the destination host list.
This information is cached and only refreshed on 30 second intervals.
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/sdiag.html)
-a , --all [#OPT_all](https://slurm.schedmd.com/sdiag.html) Get and report information. This is the default mode of operation.
-M , --cluster =< string >[#OPT_cluster](https://slurm.schedmd.com/sdiag.html) The cluster to issue commands to. Only one cluster name may be specified.
Note that the slurmdbd must be up for this option to work properly, unless
running in a federation with FederationParameters=fed_display configured.
-h , --help [#OPT_help](https://slurm.schedmd.com/sdiag.html) Print description of options and exit.
--json , --json = list , --json =< data_parser >[#OPT_json](https://slurm.schedmd.com/sdiag.html) Dump information as JSON using the default data_parser plugin or explicit
data_parser with parameters. Sorting and formatting arguments will be ignored.
--no-trunc [#OPT_no-trunc](https://slurm.schedmd.com/sdiag.html) Do not truncate long lines to 80 char.
-r , --reset [#OPT_reset](https://slurm.schedmd.com/sdiag.html) Reset scheduler and RPC counters to 0. Only supported for Slurm operators and
administrators.
-i , --sort-by-id [#OPT_sort-by-id](https://slurm.schedmd.com/sdiag.html) Sort Remote Procedure Call (RPC) data by message type ID and user ID.
-t , --sort-by-time [#OPT_sort-by-time](https://slurm.schedmd.com/sdiag.html) Sort Remote Procedure Call (RPC) data by total run time.
-T , --sort-by-time2 [#OPT_sort-by-time2](https://slurm.schedmd.com/sdiag.html) Sort Remote Procedure Call (RPC) data by average run time.
--usage [#OPT_usage](https://slurm.schedmd.com/sdiag.html) Print list of options and exit.
-V , --version [#OPT_version](https://slurm.schedmd.com/sdiag.html) Print current version number and exit.
--yaml , --yaml = list , --yaml =< data_parser >[#OPT_yaml](https://slurm.schedmd.com/sdiag.html) Dump information as YAML using the default data_parser plugin or explicit
data_parser with parameters. Sorting and formatting arguments will be ignored.
## PERFORMANCE[#SECTION_PERFORMANCE](https://slurm.schedmd.com/sdiag.html)
Executing sdiag sends a remote procedure call to slurmctld . If
enough calls from sdiag or other Slurm client commands that send remote
procedure calls to the slurmctld daemon come in at once, it can result in
a degradation of performance of the slurmctld daemon, possibly resulting
in a denial of service.
Do not run sdiag or other Slurm client commands that send remote procedure
calls to slurmctld from loops in shell scripts or other programs. Ensure
that programs limit calls to sdiag to the minimum necessary for the
information you are trying to gather.
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/sdiag.html)
Some sdiag options may be set via environment variables. These
environment variables, along with their corresponding options, are listed below.
(Note: Command line options will always override these settings.)
SLURM_CLUSTERS [#OPT_SLURM_CLUSTERS](https://slurm.schedmd.com/sdiag.html) Same as --cluster
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/sdiag.html) The location of the Slurm configuration file.
SLURM_JSON [#OPT_SLURM_JSON](https://slurm.schedmd.com/sdiag.html) Control JSON serialization:
compact [#OPT_compact](https://slurm.schedmd.com/sdiag.html) Output JSON as compact as possible.
pretty [#OPT_pretty](https://slurm.schedmd.com/sdiag.html) Output JSON in pretty format to make it more readable.
SLURM_YAML [#OPT_SLURM_YAML](https://slurm.schedmd.com/sdiag.html) Control YAML serialization:
compact Output YAML as compact as possible.[#OPT_compact_1](https://slurm.schedmd.com/sdiag.html)
pretty Output YAML in pretty format to make it more readable.[#OPT_pretty_1](https://slurm.schedmd.com/sdiag.html)
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/sdiag.html)
Copyright (C) 2010-2011 Barcelona Supercomputing Center.
Copyright (C) 2010-2022 SchedMD LLC.
Slurm is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation; either version 2 of the License, or (at your option)
any later version.
Slurm is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/sdiag.html)
[sinfo](https://slurm.schedmd.com/sinfo.html)(1), [squeue](https://slurm.schedmd.com/squeue.html)(1), [scontrol](https://slurm.schedmd.com/scontrol.html)(1), [slurm.conf](https://slurm.schedmd.com/slurm.conf.html)(5),
## Index
[NAME](https://slurm.schedmd.com/sdiag.html)
[SYNOPSIS](https://slurm.schedmd.com/sdiag.html)
[DESCRIPTION](https://slurm.schedmd.com/sdiag.html)
[OPTIONS](https://slurm.schedmd.com/sdiag.html)
[PERFORMANCE](https://slurm.schedmd.com/sdiag.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/sdiag.html)
[COPYING](https://slurm.schedmd.com/sdiag.html)
[SEE ALSO](https://slurm.schedmd.com/sdiag.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
