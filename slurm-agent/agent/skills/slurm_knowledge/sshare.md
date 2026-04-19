---
source_url: https://slurm.schedmd.com/sshare.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:30 UTC
title: "Slurm Workload Manager - sshare"
---

# sshare
Section: Slurm Commands (1)
Updated: Slurm Commands
[Index](https://slurm.schedmd.com/sshare.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/sshare.html)
sshare - Tool for listing the shares of associations to a cluster.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/sshare.html)
sshare [ OPTIONS ...]
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/sshare.html)
sshare is used to view Slurm share information. This command is
only viable when running with the priority/multifactor plugin.
The sshare information is derived from a database with the interface
being provided by slurmdbd (Slurm Database daemon) which is
read in from the slurmctld and used to process the shares available
to a given association. sshare provides Slurm share information of
Account, User, Raw Shares, Normalized Shares, Raw Usage, Normalized
Usage, Effective Usage, the Fair-share factor, the GrpTRESMins limit,
Partitions and accumulated currently running TRES-minutes for each association.
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/sshare.html)
-A , --accounts =< account >[#OPT_accounts](https://slurm.schedmd.com/sshare.html) Display information for specific accounts (comma separated list).
-a , --all [#OPT_all](https://slurm.schedmd.com/sshare.html) Display information for all users.
-M , --clusters =< string >[#OPT_clusters](https://slurm.schedmd.com/sshare.html) Clusters to issue commands to.
Note that the slurmdbd must be up for this option to work properly, unless
running in a federation with FederationParameters=fed_display configured.
-o , --format =< output_format >[#OPT_format](https://slurm.schedmd.com/sshare.html) Comma separated list of fields (use
"--helpformat" for a list of available fields).
--help [#OPT_help](https://slurm.schedmd.com/sshare.html) Display a description of sshare options and commands.
-l , --long [#OPT_long](https://slurm.schedmd.com/sshare.html) Long listing - includes the normalized usage information.
--json , --json = list , --json =< data_parser >[#OPT_json](https://slurm.schedmd.com/sshare.html) Dump information as JSON using the default data_parser plugin or explicit
data_parser with parameters. Sorting and formatting arguments will be ignored.
-n , --noheader [#OPT_noheader](https://slurm.schedmd.com/sshare.html) No header will be added to the beginning of the output.
-p , --parsable [#OPT_parsable](https://slurm.schedmd.com/sshare.html) Output will be '|' delimited with a '|' at the end.
-P , --parsable2 [#OPT_parsable2](https://slurm.schedmd.com/sshare.html) Output will be '|' delimited without a '|' at the end.
-m , --partition [#OPT_partition](https://slurm.schedmd.com/sshare.html) If there are association based partitions in the system
print their names.
--usage [#OPT_usage](https://slurm.schedmd.com/sshare.html) Display a description of sshare options and commands.
-u , --users =< user_list >[#OPT_users](https://slurm.schedmd.com/sshare.html) Display information for specific users (comma separated list).
-U , --Users [#OPT_Users](https://slurm.schedmd.com/sshare.html) If specified only the users information are printed, the parent
and ancestors are not displayed.
-v , --verbose [#OPT_verbose](https://slurm.schedmd.com/sshare.html) Display more information about the specified options.
-V , --version [#OPT_version](https://slurm.schedmd.com/sshare.html) Display the version number of sshare.
--yaml , --yaml = list , --yaml =< data_parser >[#OPT_yaml](https://slurm.schedmd.com/sshare.html) Dump information as YAML using the default data_parser plugin or explicit
data_parser with parameters. Sorting and formatting arguments will be ignored.
## SSHARE OUTPUT FIELDS[#SECTION_SSHARE-OUTPUT-FIELDS](https://slurm.schedmd.com/sshare.html)
Account [#OPT_Account](https://slurm.schedmd.com/sshare.html) The Account.
User [#OPT_User](https://slurm.schedmd.com/sshare.html) The User.
Raw Shares [#OPT_Raw-Shares](https://slurm.schedmd.com/sshare.html) The raw shares assigned to the user or account.
Norm Shares [#OPT_Norm-Shares](https://slurm.schedmd.com/sshare.html) The shares assigned to the user or account normalized to the total
number of assigned shares.
Raw Usage [#OPT_Raw-Usage](https://slurm.schedmd.com/sshare.html) The number of tres-seconds (cpu-seconds if TRESBillingWeights is not defined)
of all the jobs charged to the account or user. This number will decay over
time when PriorityDecayHalfLife is defined.
Norm Usage (only appears with sshare -l option)[#OPT_Norm-Usage](https://slurm.schedmd.com/sshare.html) The Raw Usage normalized to the total number of tres-seconds of all
jobs run on the cluster, subject to the PriorityDecayHalfLife decay
when defined.
Effectv Usage [#OPT_Effectv-Usage](https://slurm.schedmd.com/sshare.html) The Effective Usage augments the normalized usage to account for usage
from sibling accounts.
FairShare [#OPT_FairShare](https://slurm.schedmd.com/sshare.html) The Fair-Share factor, based on a user's assigned shares and
the effective usage charged to them.
GrpTRESMins [#OPT_GrpTRESMins](https://slurm.schedmd.com/sshare.html) The TRES-minutes limit set on the account. The total number of cpu
minutes that can possibly be used by past, present and future jobs
running from this account and its children.
GrpTRESRaw [#OPT_GrpTRESRaw](https://slurm.schedmd.com/sshare.html) The raw TRES usage that has been used by jobs running from
this account and its children.
TRESRunMins [#OPT_TRESRunMins](https://slurm.schedmd.com/sshare.html) The number of TRES-minutes allocated by jobs currently running against
the account. Used to limit the combined total number of TRES minutes
used by all jobs running with this account and its children.
This takes into consideration time limit of running jobs and consumes it,
if the limit is reached no new jobs are started until other jobs finish
to allow time to free up.
## FAIR_TREE MODIFICATIONS[#SECTION_FAIR_TREE-MODIFICATIONS](https://slurm.schedmd.com/sshare.html)
When PriorityFlags=FAIR_TREE is set (the default, unless NO_FAIR_TREE is set),
calculations are done differently.
As a result, the following fields are added or modified:
Norm Shares [#OPT_Norm-Shares_1](https://slurm.schedmd.com/sshare.html) The shares assigned to the user or account normalized to the total
number of assigned shares within the level.
Effectv Usage [#OPT_Effectv-Usage_1](https://slurm.schedmd.com/sshare.html) Effectv Usage is the association's usage normalized with its parent.
Level FS (only appears with sshare -l option)[#OPT_Level-FS](https://slurm.schedmd.com/sshare.html) This is the association's fairshare value compared to its siblings, calculated
as Norm Shares / Effectv Usage. If an association is over-served, the value is
between 0 and 1. If an association is under-served, the value is greater than 1.
Associations with no usage receive the highest possible value, infinity.
More information about Fair Tree can be found in doc/html/fair_tree.html or
at [https://slurm.schedmd.com/fair_tree.html](https://slurm.schedmd.com/fair_tree.html)
## PERFORMANCE[#SECTION_PERFORMANCE](https://slurm.schedmd.com/sshare.html)
Executing sshare sends a remote procedure call to slurmctld . If
enough calls from sshare or other Slurm client commands that send remote
procedure calls to the slurmctld daemon come in at once, it can result in
a degradation of performance of the slurmctld daemon, possibly resulting
in a denial of service.
Do not run sshare or other Slurm client commands that send remote
procedure calls to slurmctld from loops in shell scripts or other
programs. Ensure that programs limit calls to sshare to the minimum
necessary for the information you are trying to gather.
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/sshare.html)
Some sshare options may be set via environment variables. These
environment variables, along with their corresponding options, are listed below.
(Note: Command line options will always override these settings.)
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/sshare.html) The location of the Slurm configuration file.
SLURM_DEBUG_FLAGS [#OPT_SLURM_DEBUG_FLAGS](https://slurm.schedmd.com/sshare.html) Specify debug flags for sshare to use. See DebugFlags in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for a full list of flags. The environment
variable takes precedence over the setting in the slurm.conf.
SLURM_JSON [#OPT_SLURM_JSON](https://slurm.schedmd.com/sshare.html) Control JSON serialization:
compact [#OPT_compact](https://slurm.schedmd.com/sshare.html) Output JSON as compact as possible.
pretty [#OPT_pretty](https://slurm.schedmd.com/sshare.html) Output JSON in pretty format to make it more readable.
SLURM_YAML [#OPT_SLURM_YAML](https://slurm.schedmd.com/sshare.html) Control YAML serialization:
compact Output YAML as compact as possible.[#OPT_compact_1](https://slurm.schedmd.com/sshare.html)
pretty Output YAML in pretty format to make it more readable.[#OPT_pretty_1](https://slurm.schedmd.com/sshare.html)
## EXAMPLES[#SECTION_EXAMPLES](https://slurm.schedmd.com/sshare.html)
Display information about users in a particular account:
```text
$ sshare -A
```
Display information about a specific user in a parsable format:
```text
$ sshare --parsable --users=
```
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/sshare.html)
Copyright (C) 2008 Lawrence Livermore National Security.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/sshare.html)
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5),
[slurmdbd](https://slurm.schedmd.com/slurmdbd.html) (8)
## Index
[NAME](https://slurm.schedmd.com/sshare.html)
[SYNOPSIS](https://slurm.schedmd.com/sshare.html)
[DESCRIPTION](https://slurm.schedmd.com/sshare.html)
[OPTIONS](https://slurm.schedmd.com/sshare.html)
[SSHARE OUTPUT FIELDS](https://slurm.schedmd.com/sshare.html)
[FAIR_TREE MODIFICATIONS](https://slurm.schedmd.com/sshare.html)
[PERFORMANCE](https://slurm.schedmd.com/sshare.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/sshare.html)
[EXAMPLES](https://slurm.schedmd.com/sshare.html)
[COPYING](https://slurm.schedmd.com/sshare.html)
[SEE ALSO](https://slurm.schedmd.com/sshare.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
