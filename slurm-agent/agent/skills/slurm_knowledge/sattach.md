---
source_url: https://slurm.schedmd.com/sattach.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:19 UTC
title: "Slurm Workload Manager - sattach"
---

# sattach
Section: Slurm Commands (1)
Updated: Slurm Commands
[Index](https://slurm.schedmd.com/sattach.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/sattach.html)
sattach - Attach to a Slurm job step.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/sattach.html)
sattach [ options ] <jobid.stepid>
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/sattach.html)
sattach attaches to a running Slurm job step. By attaching, it makes available
the IO streams of all of the tasks of a running Slurm job step. It is also
suitable for use with a parallel debugger like TotalView. It cannot be used to
attach directly to extern or batch steps since the IO channels of these steps
are not set or directly forwarded to a file.
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/sattach.html)
--error-filter [=]< task number >[#OPT_error-filter](https://slurm.schedmd.com/sattach.html)
Only transmit standard input to a single task, or print the standard output
or standard error from a single task. The filtering is performed locally in
sattach.
-h , --help [#OPT_help](https://slurm.schedmd.com/sattach.html) Display help information and exit.
--input-filter [=]< task number >[#OPT_input-filter](https://slurm.schedmd.com/sattach.html)
Only transmit standard input to a single task, or print the standard output
or standard error from a single task. The filtering is performed locally in
sattach.
-l , --label [#OPT_label](https://slurm.schedmd.com/sattach.html) Prepend each line of task standard output or standard error with the task
number of its origin.
--layout [#OPT_layout](https://slurm.schedmd.com/sattach.html) Contacts the slurmctld to obtain the task layout information for the job step,
prints the task layout information, and then exits without attaching to the
job step.
--output-filter [=]< task number >[#OPT_output-filter](https://slurm.schedmd.com/sattach.html)
Only transmit standard input to a single task, or print the standard output
or standard error from a single task. The filtering is performed locally in
sattach.
--pty [#OPT_pty](https://slurm.schedmd.com/sattach.html) Execute task zero in pseudo terminal.
Not compatible with the --input-filter , --output-filter , or
--error-filter options.
Notes: The terminal size and resize events are ignored by sattach.
Proper operation requires that the job step be initiated by srun using the
--pty option.
-Q , --quiet [#OPT_quiet](https://slurm.schedmd.com/sattach.html) Suppress informational messages from sattach. Errors will still be displayed.
-u , --usage [#OPT_usage](https://slurm.schedmd.com/sattach.html) Display brief usage message and exit.
-V , --version [#OPT_version](https://slurm.schedmd.com/sattach.html) Display Slurm version number and exit.
-v , --verbose [#OPT_verbose](https://slurm.schedmd.com/sattach.html) Increase the verbosity of sattach's informational messages. Multiple
-v 's will further increase sattach's verbosity.
## PERFORMANCE[#SECTION_PERFORMANCE](https://slurm.schedmd.com/sattach.html)
Executing sattach sends a remote procedure call to slurmctld . If
enough calls from sattach or other Slurm client commands that send remote
procedure calls to the slurmctld daemon come in at once, it can result in
a degradation of performance of the slurmctld daemon, possibly resulting
in a denial of service.
Do not run sattach or other Slurm client commands that send remote
procedure calls to slurmctld from loops in shell scripts or other
programs. Ensure that programs limit calls to sattach to the minimum
necessary for the information you are trying to gather.
## INPUT ENVIRONMENT VARIABLES[#SECTION_INPUT-ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/sattach.html)
Upon startup, salloc will read and handle the options set in the following
environment variables. Note: Command line options always override environment
variables settings.
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/sattach.html) The location of the Slurm configuration file.
SLURM_DEBUG_FLAGS [#OPT_SLURM_DEBUG_FLAGS](https://slurm.schedmd.com/sattach.html) Specify debug flags for sattach to use. See DebugFlags in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for a full list of flags. The environment
variable takes precedence over the setting in the slurm.conf.
SLURM_EXIT_ERROR [#OPT_SLURM_EXIT_ERROR](https://slurm.schedmd.com/sattach.html) Specifies the exit code generated when a Slurm error occurs
(e.g. invalid options).
This can be used by a script to distinguish application exit codes from
various Slurm error conditions.
## EXAMPLES[#SECTION_EXAMPLES](https://slurm.schedmd.com/sattach.html)
Attach to job 15, step 0:
```text
$ sattach 15.0
```
Limit the output to the 5th task of job 65386, step 15:
```text
$ sattach --output-filter 5 65386.15
```
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/sattach.html)
Copyright (C) 2006-2007 The Regents of the University of California.
Produced at Lawrence Livermore National Laboratory (cf, DISCLAIMER).
Copyright (C) 2008-2009 Lawrence Livermore National Security.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/sattach.html)
[sinfo](https://slurm.schedmd.com/sinfo.html) (1), [salloc](https://slurm.schedmd.com/salloc.html) (1), [sbatch](https://slurm.schedmd.com/sbatch.html) (1), [squeue](https://slurm.schedmd.com/squeue.html) (1),
[scancel](https://slurm.schedmd.com/scancel.html) (1), [scontrol](https://slurm.schedmd.com/scontrol.html) (1),
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5), sched_setaffinity (2), numa (3)
## Index
[NAME](https://slurm.schedmd.com/sattach.html)
[SYNOPSIS](https://slurm.schedmd.com/sattach.html)
[DESCRIPTION](https://slurm.schedmd.com/sattach.html)
[OPTIONS](https://slurm.schedmd.com/sattach.html)
[PERFORMANCE](https://slurm.schedmd.com/sattach.html)
[INPUT ENVIRONMENT VARIABLES](https://slurm.schedmd.com/sattach.html)
[EXAMPLES](https://slurm.schedmd.com/sattach.html)
[COPYING](https://slurm.schedmd.com/sattach.html)
[SEE ALSO](https://slurm.schedmd.com/sattach.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
