---
source_url: https://slurm.schedmd.com/sprio.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:28 UTC
title: "Slurm Workload Manager - sprio"
---

# sprio
Section: Slurm Commands (1)
Updated: Slurm Commands
[Index](https://slurm.schedmd.com/sprio.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/sprio.html)
sprio - view the factors that comprise a job's scheduling priority
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/sprio.html)
sprio [ OPTIONS ...]
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/sprio.html)
sprio is used to view the components of a job's scheduling
priority when the multi-factor priority plugin is installed.
sprio is a read-only utility that extracts information from the
multi-factor priority plugin. By default, sprio returns
information for all pending jobs. Options exist to display specific
jobs by job ID and user name.
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/sprio.html)
-M , --clusters =< string >[#OPT_clusters](https://slurm.schedmd.com/sprio.html) The cluster to issue commands to. Only one cluster name may be specified.
Note that the slurmdbd must be up for this option to work properly, unless
running in a federation with either FederationParameters=fed_display
configured or the --federation option set.
This option implicitly sets the --local option.
--federation [#OPT_federation](https://slurm.schedmd.com/sprio.html) Show jobs in federation if a member of one.
-o , --format =< output_format >[#OPT_format](https://slurm.schedmd.com/sprio.html) Specify the information to be displayed, its size and position (right
or left justified). The default formats when all factors have been
assigned non-zero weights are
default [#OPT_default](https://slurm.schedmd.com/sprio.html) "%.15i %9r %.10Y %.10S %.10A %.10B %.10F %.10J %.10P %.10Q %20T"
-l, --long [#OPT_long](https://slurm.schedmd.com/sprio.html) "%.15i %9r %.8u %.8o %.10Y %.10S %.10A %.10B %.10F %.10J %.10P %.10n %.10Q %.11N %.20T";
The format of each field is "%[.][size]type".
size [#OPT_size](https://slurm.schedmd.com/sprio.html) is the minimum field size.
If no size is specified, whatever is needed to print the information will be used.
. [#OPT_-.](https://slurm.schedmd.com/sprio.html) indicates the output should be left justified.
By default, output is right justified.
Valid type specifications include:
%a [#OPT_%a](https://slurm.schedmd.com/sprio.html) Normalized age priority
%A [#OPT_%A](https://slurm.schedmd.com/sprio.html) Weighted age priority
%b [#OPT_%b](https://slurm.schedmd.com/sprio.html) Normalized association priority
%B [#OPT_%B](https://slurm.schedmd.com/sprio.html) Weighted association priority
%c [#OPT_%c](https://slurm.schedmd.com/sprio.html) Cluster name. Only applicable for federated clusters
%f [#OPT_%f](https://slurm.schedmd.com/sprio.html) Normalized fair-share priority
%F [#OPT_%F](https://slurm.schedmd.com/sprio.html) Weighted fair-share priority
%i [#OPT_%i](https://slurm.schedmd.com/sprio.html) Job ID
%j [#OPT_%j](https://slurm.schedmd.com/sprio.html) Normalized job size priority
%J [#OPT_%J](https://slurm.schedmd.com/sprio.html) Weighted job size priority
%n [#OPT_%n](https://slurm.schedmd.com/sprio.html) QOS name
%N [#OPT_%N](https://slurm.schedmd.com/sprio.html) Nice adjustment
%o [#OPT_%o](https://slurm.schedmd.com/sprio.html) Account name
%p [#OPT_%p](https://slurm.schedmd.com/sprio.html) Normalized partition priority
%P [#OPT_%P](https://slurm.schedmd.com/sprio.html) Weighted partition priority
%q [#OPT_%q](https://slurm.schedmd.com/sprio.html) Normalized quality of service priority
%Q [#OPT_%Q](https://slurm.schedmd.com/sprio.html) Weighted quality of service priority
%r [#OPT_%r](https://slurm.schedmd.com/sprio.html) Partition name
%S [#OPT_%S](https://slurm.schedmd.com/sprio.html) Weighted admin priority.
%t [#OPT_%t](https://slurm.schedmd.com/sprio.html) Normalized TRES priorities
%T [#OPT_%T](https://slurm.schedmd.com/sprio.html) Weighted TRES priorities
%u [#OPT_%u](https://slurm.schedmd.com/sprio.html) User name for a job
%Y [#OPT_%Y](https://slurm.schedmd.com/sprio.html) Job priority
%y [#OPT_%y](https://slurm.schedmd.com/sprio.html) Normalized job priority
--help [#OPT_help](https://slurm.schedmd.com/sprio.html) Print a help message describing all options sprio .
-j , --jobs =< job_id_list >[#OPT_jobs](https://slurm.schedmd.com/sprio.html) Requests a comma separated list of job ids to display. Defaults to
all jobs. Since this option's argument is optional, for proper parsing
the single letter option must be followed immediately with the value
and not include a space between them. For example "-j1008,1009" and
not "-j 1008,1009".
--local [#OPT_local](https://slurm.schedmd.com/sprio.html) Show only jobs local to this cluster. Ignore other clusters in this federation
(if any). Overrides --federation.
-l , --long [#OPT_long_1](https://slurm.schedmd.com/sprio.html) Report more of the available information for the selected jobs.
-h , --noheader [#OPT_noheader](https://slurm.schedmd.com/sprio.html) Do not print a header on the output.
-n , --norm [#OPT_norm](https://slurm.schedmd.com/sprio.html) Display the normalized priority factors for the selected jobs.
-p , --partition =< partition_list >[#OPT_partition](https://slurm.schedmd.com/sprio.html) Requests a comma separated list of partitions to display. Defaults to
all partitions.
--sibling [#OPT_sibling](https://slurm.schedmd.com/sprio.html) Show all sibling jobs on a federated cluster. Without this option in a
federated cluster, each job in each partition will have its priority and its
components reported for only one cluster. Each sibling job on the various
clusters in the federation may have different priority, which will not be
reported without using this option. Implicitly adds "%c" (cluster name) to the
output format.
-S , --sort =< sort_list >[#OPT_sort](https://slurm.schedmd.com/sprio.html) Specification of the order in which jobs should be reported. This uses the same
field specification as <output_format>. Multiple sorts may be performed by
listing multiple sort fields separated by commas. The field specifications may
be preceded by "+" or "-" for ascending (default) or descending respectively.
For example, a <sort_list> of "u,r,-y" will sort the job priority reports by
username, partition name, and descending job priority, in that order. The
default <sort_list> is "i" (ascending job id).
--usage [#OPT_usage](https://slurm.schedmd.com/sprio.html) Print a brief help message listing the sprio options.
-u , --user =< user_list >[#OPT_user](https://slurm.schedmd.com/sprio.html) Request jobs from a comma separated list of users. The list can
consist of user names or user id numbers.
-v , --verbose [#OPT_verbose](https://slurm.schedmd.com/sprio.html) Report details of sprios actions.
-V , --version [#OPT_version](https://slurm.schedmd.com/sprio.html) Print version information and exit.
-w , --weights [#OPT_weights](https://slurm.schedmd.com/sprio.html) Display the configured weights for each factor. This is for information
purposes only. Actual job data is suppressed.
## PERFORMANCE[#SECTION_PERFORMANCE](https://slurm.schedmd.com/sprio.html)
Executing sprio sends a remote procedure call to slurmctld . If
enough calls from sprio or other Slurm client commands that send remote
procedure calls to the slurmctld daemon come in at once, it can result in
a degradation of performance of the slurmctld daemon, possibly resulting
in a denial of service.
Do not run sprio or other Slurm client commands that send remote procedure
calls to slurmctld from loops in shell scripts or other programs. Ensure
that programs limit calls to sprio to the minimum necessary for the
information you are trying to gather.
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/sprio.html)
If no corresponding command line option is specified, sprio will use the
value of the following environment variables.
SLURM_CLUSTERS [#OPT_SLURM_CLUSTERS](https://slurm.schedmd.com/sprio.html) Same as --clusters
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/sprio.html) The location of the Slurm configuration file.
SLURM_DEBUG_FLAGS [#OPT_SLURM_DEBUG_FLAGS](https://slurm.schedmd.com/sprio.html) Specify debug flags for sprio to use. See DebugFlags in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for a full list of flags. The environment
variable takes precedence over the setting in the slurm.conf.
SPRIO_FEDERATION [#OPT_SPRIO_FEDERATION](https://slurm.schedmd.com/sprio.html) Same as --federation
SPRIO_FORMAT [#OPT_SPRIO_FORMAT](https://slurm.schedmd.com/sprio.html) Same as -o <output_format>, --format=<output_format>
SPRIO_LOCAL [#OPT_SPRIO_LOCAL](https://slurm.schedmd.com/sprio.html) Same as --local
SPRIO_SIBLING [#OPT_SPRIO_SIBLING](https://slurm.schedmd.com/sprio.html) Same as --sibling
## EXAMPLES[#SECTION_EXAMPLES](https://slurm.schedmd.com/sprio.html)
Print the list of all pending jobs with their weighted priorities
```text
$ sprio JOBID PRIORITY AGE FAIRSHARE JOBSIZE PARTITION QOS 65539 62664 0 51664 1000 10000 0 65540 62663 0 51663 1000 10000 0 65541 62662 0 51662 1000 10000 0
```
Print the list of all pending jobs with their normalized priorities
```text
$ sprio -n JOBID PRIORITY AGE FAIRSHARE JOBSIZE PARTITION QOS 65539 0.00001459 0.0007180 0.5166470 1.0000000 1.0000000 0.0000000 65540 0.00001459 0.0007180 0.5166370 1.0000000 1.0000000 0.0000000 65541 0.00001458 0.0007180 0.5166270 1.0000000 1.0000000 0.0000000
```
Print the job priorities for specific jobs
```text
$ sprio --jobs=65548,65547 JOBID PRIORITY AGE FAIRSHARE JOBSIZE PARTITION QOS 65547 62078 0 51078 1000 10000 0 65548 62077 0 51077 1000 10000 0
```
Print the job priorities for jobs of specific users
```text
$ sprio --users=fred,sally JOBID USER PRIORITY AGE FAIRSHARE JOBSIZE PARTITION QOS 65548 fred 62079 1 51077 1000 10000 0 65549 sally 62080 1 51078 1000 10000 0
```
Print the configured weights for each priority component
```text
$ sprio -w JOBID PRIORITY AGE FAIRSHARE JOBSIZE PARTITION QOS Weights 1000 100000 1000 10000 1
```
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/sprio.html)
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/sprio.html)
[squeue](https://slurm.schedmd.com/squeue.html) (1), [sshare](https://slurm.schedmd.com/sshare.html) (1)
## Index
[NAME](https://slurm.schedmd.com/sprio.html)
[SYNOPSIS](https://slurm.schedmd.com/sprio.html)
[DESCRIPTION](https://slurm.schedmd.com/sprio.html)
[OPTIONS](https://slurm.schedmd.com/sprio.html)
[PERFORMANCE](https://slurm.schedmd.com/sprio.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/sprio.html)
[EXAMPLES](https://slurm.schedmd.com/sprio.html)
[COPYING](https://slurm.schedmd.com/sprio.html)
[SEE ALSO](https://slurm.schedmd.com/sprio.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
