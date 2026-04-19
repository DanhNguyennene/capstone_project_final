---
source_url: https://slurm.schedmd.com/sh5util.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:11 UTC
title: "Slurm Workload Manager - sh5util"
---

# sh5util
Section: Slurm Commands (1)
Updated: Slurm Commands
[Index](https://slurm.schedmd.com/sh5util.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/sh5util.html)
sh5util - Tool for merging HDF5 files from the acct_gather_profile
plugin that gathers detailed data for jobs running under Slurm
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/sh5util.html)
sh5util
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/sh5util.html)
sh5util merges HDF5 files produced on each node for each step of a job into
one HDF5 file for the job. The resulting file can be viewed and manipulated
by common HDF5 tools such as HDF5View, h5dump, h5edit, or h5ls.
sh5util also has two extract modes. The first, writes a limited set of
data for specific nodes, steps, and data series in
"comma separated value" form to a file which can be imported into other
analysis tools such as spreadsheets.
The second, (Item-Extract) extracts one data time from one time series for all
the samples on all the nodes from a jobs HDF5 profile.
- Finds sample with maximum value of the item.
- Write CSV file with min, ave, max, and item totals for each node for each
sample
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/sh5util.html)
-E , --extract [#OPT_extract](https://slurm.schedmd.com/sh5util.html)
Extract data series from a merged job file.
Extract mode options
-i , --input = path [#OPT_input](https://slurm.schedmd.com/sh5util.html) merged file to extract from (default ./job_$jobid.h5)
-N , --node = nodename [#OPT_node](https://slurm.schedmd.com/sh5util.html) Node name to extract (default is all)
-l , --level =[Node:Totals | Node:TimeSeries][#OPT_level](https://slurm.schedmd.com/sh5util.html) Level to which series is attached. (default Node:Totals)
-s , --series =[Energy | Filesystem | Network | Task | Task_#][#OPT_series](https://slurm.schedmd.com/sh5util.html) Task is all tasks, Task_# (# is a task id) (default is everything)
-h , --help [#OPT_help](https://slurm.schedmd.com/sh5util.html) Print this description of use.
-I , --item-extract [#OPT_item-extract](https://slurm.schedmd.com/sh5util.html)
Extract one data item from all samples of one data series from all nodes in a merged job file.
Item-Extract mode options
-s , --series =[Energy | Filesystem | Network | Task][#OPT_series_1](https://slurm.schedmd.com/sh5util.html)
-d , --data [#OPT_data](https://slurm.schedmd.com/sh5util.html) Name of data item in series (See note below).
-j , --jobs =< job [. step ]>[#OPT_jobs](https://slurm.schedmd.com/sh5util.html) Format is < job [. step ]>. Merge this job/step
(or a comma-separated list of job steps). This option is required.
Not specifying a step will result in all steps found to be processed.
-L , --list [#OPT_list](https://slurm.schedmd.com/sh5util.html)
Print the items of a series contained in a job file.
List mode options
-i , --input = path [#OPT_input_1](https://slurm.schedmd.com/sh5util.html) Merged file to extract from (default ./job_$jobid.h5)
-s , --series =[Energy | Filesystem | Network | Task][#OPT_series_2](https://slurm.schedmd.com/sh5util.html)
-o , --output =< path >[#OPT_output](https://slurm.schedmd.com/sh5util.html) Path to a file into which to write.
Default for merge is ./job_$jobid.h5
Default for extract is ./extract_$jobid.csv
-p , --profiledir =< dir >[#OPT_profiledir](https://slurm.schedmd.com/sh5util.html) Directory location where node-step files exist default is set in
acct_gather.conf.
-S , --savefiles [#OPT_savefiles](https://slurm.schedmd.com/sh5util.html) Instead of removing node-step files after merging them into the job file,
keep them around.
--usage [#OPT_usage](https://slurm.schedmd.com/sh5util.html) Display brief usage message.
--user =< user >[#OPT_user](https://slurm.schedmd.com/sh5util.html) User who profiled job.
(Handy for root user, defaults to user running this command.)
## Data Items per Series[#SECTION_Data-Items-per-Series](https://slurm.schedmd.com/sh5util.html)
Energy [#OPT_Energy](https://slurm.schedmd.com/sh5util.html)
Power
CPU_Frequency
Filesystem [#OPT_Filesystem](https://slurm.schedmd.com/sh5util.html)
Reads
Megabytes_Read
Writes
Megabytes_Write
Network [#OPT_Network](https://slurm.schedmd.com/sh5util.html)
Packets_In
Megabytes_In
Packets_Out
Megabytes_Out
Task [#OPT_Task](https://slurm.schedmd.com/sh5util.html)
CPU_Frequency
CPU_Time
CPU_Utilization
RSS
VM_Size
Pages
Read_Megabytes
Write_Megabytes
## PERFORMANCE[#SECTION_PERFORMANCE](https://slurm.schedmd.com/sh5util.html)
Executing sh5util sends a remote procedure call to slurmctld . If
enough calls from sh5util or other Slurm client commands that send remote
procedure calls to the slurmctld daemon come in at once, it can result in
a degradation of performance of the slurmctld daemon, possibly resulting
in a denial of service.
Do not run sh5util or other Slurm client commands that send remote
procedure calls to slurmctld from loops in shell scripts or other
programs. Ensure that programs limit calls to sh5util to the minimum
necessary for the information you are trying to gather.
## EXAMPLES[#SECTION_EXAMPLES](https://slurm.schedmd.com/sh5util.html)
Merge node-step files (as part of a sbatch script):
```text
$ sbatch -n1 -d$SLURM_JOB_ID --wrap="sh5util --savefiles -j $SLURM_JOB_ID"
```
Extract all task data from a node:
```text
$ sh5util -j 42 -N snowflake01 --level=Node:TimeSeries --series=Tasks
```
Extract all energy data:
```text
$ sh5util -j 42 --series=Energy --data=power
```
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/sh5util.html)
Copyright (C) 2013 Bull.
Copyright (C) 2013-2022 SchedMD LLC.
Slurm is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation; either version 2 of the License, or (at your option)
any later version.
Slurm is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/sh5util.html)
## Index
[NAME](https://slurm.schedmd.com/sh5util.html)
[SYNOPSIS](https://slurm.schedmd.com/sh5util.html)
[DESCRIPTION](https://slurm.schedmd.com/sh5util.html)
[OPTIONS](https://slurm.schedmd.com/sh5util.html)
[Data Items per Series](https://slurm.schedmd.com/sh5util.html)
[PERFORMANCE](https://slurm.schedmd.com/sh5util.html)
[EXAMPLES](https://slurm.schedmd.com/sh5util.html)
[COPYING](https://slurm.schedmd.com/sh5util.html)
[SEE ALSO](https://slurm.schedmd.com/sh5util.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
