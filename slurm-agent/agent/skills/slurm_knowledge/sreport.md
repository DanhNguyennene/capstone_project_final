---
source_url: https://slurm.schedmd.com/sreport.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:29 UTC
title: "Slurm Workload Manager - sreport"
---

# sreport
Section: Slurm Commands (1)
Updated: Slurm Commands
[Index](https://slurm.schedmd.com/sreport.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/sreport.html)
sreport - Generate reports from the slurm accounting data.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/sreport.html)
sreport [ OPTIONS ...] [ COMMAND ...]
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/sreport.html)
sreport is used to generate reports of job usage and cluster
utilization for Slurm jobs saved to the Slurm Database,
slurmdbd . Report data comes from hourly, daily, and monthly rollups of
accounting data that occur automatically in the background. Data will be pulled
from the rollup table with the longest interval that can satisfy the requested
report period. For example, a report on the time range "Start=01/01 End=03/01"
will be able to pull from the monthly rollup table, while a report with
"Start=01/01-03:00 End=03/01" will need to use the hourly rollup table.
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/sreport.html)
-a , --all_clusters [#OPT_all_clusters](https://slurm.schedmd.com/sreport.html) Use all clusters instead of only the cluster from which the command was
executed.
-M , --cluster [#OPT_cluster](https://slurm.schedmd.com/sreport.html) The cluster(s) to generate reports for. Default is local cluster, unless the
local cluster is currently part of a federation and in that case generate a
report for all clusters in the current federation. If the clusters included
in a federation vary through time, use this option to identify the clusters
to be included in report. Implies --local.
--federation [#OPT_federation](https://slurm.schedmd.com/sreport.html) Generate a report for the federation if a member of one.
-h , --help [#OPT_help](https://slurm.schedmd.com/sreport.html) Print a help message describing the usage of sreport .
--local [#OPT_local](https://slurm.schedmd.com/sreport.html) Generate a report for the local cluster, even if part of a federation.
Overrides --federation .
-n , --noheader [#OPT_noheader](https://slurm.schedmd.com/sreport.html) Don't display header when listing results.
-p , --parsable [#OPT_parsable](https://slurm.schedmd.com/sreport.html) Output will be '|' delimited with a '|' at the end.
-P , --parsable2 [#OPT_parsable2](https://slurm.schedmd.com/sreport.html) Output will be '|' delimited without a '|' at the end.
-Q , --quiet [#OPT_quiet](https://slurm.schedmd.com/sreport.html) Print no warning or informational messages, only error messages.
-t < time_format >[#OPT_-t](https://slurm.schedmd.com/sreport.html) Specify the output time format. Time format options are case
insensitive and may be abbreviated. The default format is Minutes.
Supported time format options are listed in the time command
section below.
-T , --tres =< tres_names >[#OPT_tres](https://slurm.schedmd.com/sreport.html) Trackable resource (TRES) to report values for.
By default CPU resource use is reported (except for reservation reports. All
TRES types reserved by a reservation will be shown by default unless overridden
with this option).
Multiple TRES names may be separated using a comma separated list for all
reports except the job reports, which can only support a single TRES name, or
"ALL" for all TRES.
The "Reported" Billing TRES is calculated from the largest Billing TRES of each
node multiplied by the time frame. For example, if a node is part of multiple
partitions and each has a different TRESBillingWeights defined the Billing TRES
for the node will be the highest of the partitions. If TRESBillingWeights is
not defined on any partition for a node then the Billing TRES will be equal to
the number of CPUs on the node.
TRES node usage is no longer reported in percent format or in Cluster
Utilization. Please use TRES CPU instead.
The main issue with using node is in most configurations multiple jobs are able
to run on the same node. This makes TRES node accounting count the same node
multiple times in the same period. In exclusive node configurations, CPU
accounting returns the same usage node accounting would.
-v , --verbose [#OPT_verbose](https://slurm.schedmd.com/sreport.html) Print detailed event logging.
-V , --version [#OPT_version](https://slurm.schedmd.com/sreport.html) Print version information and exit.
## COMMANDS[#SECTION_COMMANDS](https://slurm.schedmd.com/sreport.html)
<keyword> may be omitted from the execute line and sreport will
execute in interactive mode. sreport will process commands as entered until
explicitly terminated.
exit [#OPT_exit](https://slurm.schedmd.com/sreport.html) Terminate the execution of sreport.
Identical to the quit command.
help [#OPT_help_1](https://slurm.schedmd.com/sreport.html) Display a description of sreport options and commands.
nonparsable [#OPT_nonparsable](https://slurm.schedmd.com/sreport.html) Return output to normal after parsable or parsable2 has been set.
parsable [#OPT_parsable_1](https://slurm.schedmd.com/sreport.html) Output will be | delimited with an ending '|'.
parsable2 [#OPT_parsable2_1](https://slurm.schedmd.com/sreport.html) Output will be | delimited without an ending '|'.
quiet [#OPT_quiet_1](https://slurm.schedmd.com/sreport.html) Print no warning or informational messages, only fatal error messages.
quit [#OPT_quit](https://slurm.schedmd.com/sreport.html) Terminate the execution of sreport.
Identical to the exit command.
time <time_format> [#OPT_time- ](https://slurm.schedmd.com/sreport.html) Specify the output time format. Time format options are case
insensitive and may be abbreviated. The default format is Minutes.
Supported time format options include:
SecPer [#OPT_SecPer](https://slurm.schedmd.com/sreport.html) Seconds/Percentage of Total
MinPer [#OPT_MinPer](https://slurm.schedmd.com/sreport.html) Minutes/Percentage of Total
HourPer [#OPT_HourPer](https://slurm.schedmd.com/sreport.html) Hours/Percentage of Total
Seconds [#OPT_Seconds](https://slurm.schedmd.com/sreport.html) Seconds
Minutes [#OPT_Minutes](https://slurm.schedmd.com/sreport.html) Minutes
Hours [#OPT_Hours](https://slurm.schedmd.com/sreport.html) Hours
Percent [#OPT_Percent](https://slurm.schedmd.com/sreport.html) Percentage of Total
verbose [#OPT_verbose_1](https://slurm.schedmd.com/sreport.html) Enable detailed event logging.
version [#OPT_version_1](https://slurm.schedmd.com/sreport.html) Display the sreport version number.
!! [#OPT_!!](https://slurm.schedmd.com/sreport.html) Repeat the last command executed.
## REPORT TYPES[#SECTION_REPORT-TYPES](https://slurm.schedmd.com/sreport.html)
Valid report types are:
cluster <REPORT> <OPTIONS>[#OPT_cluster_1](https://slurm.schedmd.com/sreport.html)
job <REPORT> <OPTIONS>[#OPT_job](https://slurm.schedmd.com/sreport.html)
reservation <REPORT> <OPTIONS>[#OPT_reservation](https://slurm.schedmd.com/sreport.html)
user <REPORT> <OPTIONS>[#OPT_user](https://slurm.schedmd.com/sreport.html)
<REPORT> options for each type include:
cluster [#OPT_cluster_2](https://slurm.schedmd.com/sreport.html) AccountUtilizationByUser, AccountUtilizationByQOS, UserUtilizationByAccount,
UserUtilizationByWckey, Utilization, WCKeyUtilizationByUser
job [#OPT_job_1](https://slurm.schedmd.com/sreport.html) SizesByAccount, SizesByAccountAndWcKey, SizesByWckey
reservation [#OPT_reservation_1](https://slurm.schedmd.com/sreport.html) Utilization
user [#OPT_user_1](https://slurm.schedmd.com/sreport.html) TopUsage
NOTE : If OverSubscribe is configured to FORCE or YES
in your slurm.conf and the system is not configured to use preemption
( PreemptMode=OFF ) accounting can easily grow to values greater than
the actual utilization. It may be common on such systems to get error messages
in the slurmdbd log stating: "We have more allocated time than is possible."
## REPORT DESCRIPTION[#SECTION_REPORT-DESCRIPTION](https://slurm.schedmd.com/sreport.html)
cluster AccountUtilizationByUser [#OPT_cluster-AccountUtilizationByUser](https://slurm.schedmd.com/sreport.html)
This report will display account utilization as it appears on the
hierarchical tree. Starting with the specified account or the
root account by default this report will list the underlying
usage with a sum on each level. Use the 'tree' option to span
the tree for better visibility.
NOTE : Idle reservation time will be split evenly among accounts/users
given access to it. When a reservation is assigned to whole accounts, the
time will be counted in the association for the accounts, not the user
associations in the accounts. In this case, the usage of a parent account can
be larger than the sum of its children.
cluster AccountUtilizationByQOS [#OPT_cluster-AccountUtilizationByQOS](https://slurm.schedmd.com/sreport.html)
This report will display account utilization as it appears on the
hierarchical tree. Starting with the root account by default, or with the
specified account, this report will list the underlying usage in each
account, with a sum on each level. Use the 'tree' option to expand
the tree for better visibility. Users are not displayed here, only parent
accounts.
NOTE : Idle reservation time will be split evenly among accounts that have
access to it. Since no QOS is directly connected with the idle time, the
time is counted against the default QOS of the account, or 'normal' when
there is no default.
NOTE : If you reroll data in the database and have changed the default
QOS on an association to something other than what was there at the time
of the original rollup, you can get different data.
cluster UserUtilizationByAccount [#OPT_cluster-UserUtilizationByAccount](https://slurm.schedmd.com/sreport.html)
This report will display users by account in order of utilization without
grouping multiple accounts by user into one, but displaying them
on separate lines.
cluster UserUtilizationByWCKey [#OPT_cluster-UserUtilizationByWCKey](https://slurm.schedmd.com/sreport.html)
This report will display users by wckey in order of utilization without
grouping multiple wckey by user into one, but displaying them
on separate lines.
cluster Utilization [#OPT_cluster-Utilization](https://slurm.schedmd.com/sreport.html)
This report will display total usage divided amongst Allocated, Down,
Planned Down, Idle, and Planned time for selected clusters.
Refer to the later section for descriptions of these fields.
Note: Reservations created with the IGNORE_JOBS flag are not tracked
in the Cluster Utilization report due to the fact that allowing any
current/active jobs to continue to run in the reservation introduces the
possibility for them to be accounted for incorrectly.
The jobs in these reservations will be tracked as normal rather than
being bundled in the reservation time, as they are with reservations that
do not have the IGNORE_JOBS flag.
Note: The default view for the "Cluster Utilization" report includes the
following fields: Cluster, Allocated, Down, PlannedDown, Idle, Planned,
Reported. You can include additional fields like OverCommitted and TresCount
fields with the Format option. The TresName will also be included if
using the -T, --tres <tres_names> option.
cluster WCKeyUtilizationByUser [#OPT_cluster-WCKeyUtilizationByUser](https://slurm.schedmd.com/sreport.html)
This report will display wckey utilization sorted by WCKey name for
each user on each cluster.
job SizesByAccount [#OPT_job-SizesByAccount](https://slurm.schedmd.com/sreport.html)
This report will display the amount of time used for job ranges
specified by the 'grouping=' option. Only a single level in the tree
is displayed defaulting to the root dir. If you specify other
accounts with the 'account=' option sreport will use those accounts as
the root account and you will receive the aggregated totals of each listed
account plus their sub accounts.
job SizesByAccountAndWckey [#OPT_job-SizesByAccountAndWckey](https://slurm.schedmd.com/sreport.html)
This report is very similar to SizesByAccount with the difference being
each account is pair with wckeys so the identifier is account:wckey
instead of just account so there will most likely be multiple accounts
listed depending on the number of wckeys used.
job SizesByWckey [#OPT_job-SizesByWckey](https://slurm.schedmd.com/sreport.html)
This report will display the amount of time for each wckey for job ranges
specified by the 'grouping=' option.
reservation Utilization [#OPT_reservation-Utilization](https://slurm.schedmd.com/sreport.html)
This report will display total usage for reservations on the systems.
Note: Time requests on this report will not truncate the time the reservation
used, only the reservations that ran at any time during the period requested.
user TopUsage [#OPT_user-TopUsage](https://slurm.schedmd.com/sreport.html)
Displays the top users on a cluster, i.e. users with the highest usage.
By default users are sorted by CPUTime, but the -T, --tres option will
sort users by the first TRES specified.
Use the group option to group accounts together.
The default is to have a different line for each user account combination.
Each report type has various options...
OPTIONS FOR ALL REPORT TYPES
All_Clusters [#OPT_All_Clusters](https://slurm.schedmd.com/sreport.html)
Use all monitored clusters. Default is local cluster.
Clusters=<OPT> [#OPT_Clusters= ](https://slurm.schedmd.com/sreport.html)
List of clusters to include in report. Default is local cluster.
End=<OPT> [#OPT_End= ](https://slurm.schedmd.com/sreport.html)
Period ending for report. Default is 23:59:59 of previous day. Note that while
minutes and seconds are recognized, they will be rounded to the previous hour as
reports cannot be generated for a more specific time range.
Valid time formats are...
HH:MM[:SS] [AM|PM]
MMDD[YY] or MM/DD[/YY] or MM.DD[.YY]
MM/DD[/YY]-HH:MM[:SS]
YYYY-MM-DD[THH:MM[:SS]]
now[{+|-} count [seconds(default)|minutes|hours|days|weeks]]
Format=<OPT> [#OPT_Format= ](https://slurm.schedmd.com/sreport.html)
Comma separated list of fields to display in report.
When using the format option for listing various fields you can put a
%NUMBER afterwards to specify how many characters should be printed.
e.g. format=name%30 will print 30 characters of field name right
justified. A -30 will print 30 characters left justified.
Start=<OPT> [#OPT_Start= ](https://slurm.schedmd.com/sreport.html)
Period start for report. Default is 00:00:00 of previous day. Note that while
minutes and seconds are recognized, they will be rounded to the next hour as
reports cannot be generated for a more specific time range.
Valid time formats are...
HH:MM[:SS] [AM|PM]
MMDD[YY] or MM/DD[/YY] or MM.DD[.YY]
MM/DD[/YY]-HH:MM[:SS]
YYYY-MM-DD[THH:MM[:SS]]
now[{+|-} count [seconds(default)|minutes|hours|days|weeks]]
OPTIONS SPECIFICALLY FOR CLUSTER REPORTS
Accounts=<OPT> [#OPT_Accounts= ](https://slurm.schedmd.com/sreport.html)
When used with the UserUtilizationByAccount, or
AccountUtilizationBy[User|QOS], List of accounts to include in report.
Default is all.
Tree [#OPT_Tree](https://slurm.schedmd.com/sreport.html)
When used with the AccountUtilizationBy[User|QOS] report will span the
accounts as they are in the hierarchy.
Users=<OPT> [#OPT_Users= ](https://slurm.schedmd.com/sreport.html)
When used with any report other than Utilization, List of users to
include in report. Default is all.
Wckeys=<OPT> [#OPT_Wckeys= ](https://slurm.schedmd.com/sreport.html)
When used with the UserUtilizationByWckey or WCKeyUtilizationByUser,
List of wckeys to include in report. Default is all.
OPTIONS SPECIFICALLY FOR JOB REPORTS
Accounts=<OPT> [#OPT_Accounts= _1](https://slurm.schedmd.com/sreport.html)
List of accounts to use for the report. Default is all which will show only
one line corresponding to the totals of all accounts in the hierarchy.
This explanation does not apply when ran with the FlatView or AcctAsParent
options.
AcctAsParent [#OPT_AcctAsParent](https://slurm.schedmd.com/sreport.html)
When used with the SizesbyAccount(*) will take specified accounts
as parents and the next layer of accounts under those specified
will be displayed. Default is root if no specific Accounts are requested.
When FlatView is used, this option is ignored.
FlatView [#OPT_FlatView](https://slurm.schedmd.com/sreport.html)
When used with the SizesbyAccount(*) will not group accounts in a
hierarchical level, but print each account where jobs ran on a
separate line without any hierarchy.
GID=<OPT> [#OPT_GID= ](https://slurm.schedmd.com/sreport.html)
List of group ids to include in report. Default is all.
Grouping=<OPT> [#OPT_Grouping= ](https://slurm.schedmd.com/sreport.html)
Comma separated list of size groupings. (e.g. 50,100,150 would group
job cpu count 1-49, 50-99, 100-149, > 150). grouping=individual will
result in a single column for each job size found.
Jobs=<OPT> [#OPT_Jobs= ](https://slurm.schedmd.com/sreport.html)
List of jobs/steps to include in report. Default is all.
Nodes=<OPT> [#OPT_Nodes= ](https://slurm.schedmd.com/sreport.html)
Only show jobs that ran on these nodes. Default is all.
Partitions=<OPT> [#OPT_Partitions= ](https://slurm.schedmd.com/sreport.html)
List of partitions jobs ran on to include in report. Default is all.
PrintJobCount [#OPT_PrintJobCount](https://slurm.schedmd.com/sreport.html)
When used with the Sizes report will print number of jobs ran instead
of time used.
Users=<OPT> [#OPT_Users= _1](https://slurm.schedmd.com/sreport.html)
List of users jobs to include in report. Default is all.
Wckeys=<OPT> [#OPT_Wckeys= _1](https://slurm.schedmd.com/sreport.html)
List of wckeys to use for the report. Default is all. The
SizesbyWckey report all users summed together. If you want only
certain users specify them with the Users= option.
OPTIONS SPECIFICALLY FOR RESERVATION REPORTS
Names=<OPT> [#OPT_Names= ](https://slurm.schedmd.com/sreport.html)
List of reservations to use for the report. Default is all.
Nodes=<OPT> [#OPT_Nodes= _1](https://slurm.schedmd.com/sreport.html)
Only show reservations that used these nodes. Default is all.
OPTIONS SPECIFICALLY FOR USER REPORTS
Accounts=<OPT> [#OPT_Accounts= _2](https://slurm.schedmd.com/sreport.html)
List of accounts to use for the report. Default is all.
Group [#OPT_Group](https://slurm.schedmd.com/sreport.html)
Group all accounts together for each user. Default is a separate
entry for each user and account reference.
TopCount=<OPT> [#OPT_TopCount= ](https://slurm.schedmd.com/sreport.html)
Used in the TopUsage report. Change the number of users displayed.
Default is 10.
Users=<OPT> [#OPT_Users= _2](https://slurm.schedmd.com/sreport.html)
List of users jobs to include in report. Default is all.
## FORMAT OPTIONS FOR EACH REPORT[#SECTION_FORMAT-OPTIONS-FOR-EACH-REPORT](https://slurm.schedmd.com/sreport.html)
FORMAT OPTIONS FOR CLUSTER REPORTS
AccountUtilizationByUser [#OPT_AccountUtilizationByUser](https://slurm.schedmd.com/sreport.html) Accounts, Cluster, Login, QOS, Proper, TresCount, Used
AccountUtilizationByQOS [#OPT_AccountUtilizationByQOS](https://slurm.schedmd.com/sreport.html) Accounts, Cluster, QOS, TresCount, Used
UserUtilizationByAccount [#OPT_UserUtilizationByAccount](https://slurm.schedmd.com/sreport.html) Accounts, Cluster, Login, Proper, TresCount, Used
UserUtilizationByWckey [#OPT_UserUtilizationByWckey](https://slurm.schedmd.com/sreport.html) Cluster, Login, Proper, TresCount, Used, Wckey
Utilization [#OPT_Utilization](https://slurm.schedmd.com/sreport.html) Allocated, Cluster, Down, Idle, OverCommitted, PlannedDown, Reported, Planned,
TresCount, TresName
WCKeyUtilizationByUser [#OPT_WCKeyUtilizationByUser](https://slurm.schedmd.com/sreport.html) Cluster, Login, Proper, TresCount, Used, Wckey
FORMAT OPTIONS FOR JOB REPORTS
SizesByAccount [#OPT_SizesByAccount](https://slurm.schedmd.com/sreport.html) Account, Cluster
SizesByAccountAndWckey [#OPT_SizesByAccountAndWckey](https://slurm.schedmd.com/sreport.html) Account, Cluster
SizesByWckey [#OPT_SizesByWckey](https://slurm.schedmd.com/sreport.html) Wckey, Cluster
FORMAT OPTIONS FOR RESERVATION REPORTS
Utilization [#OPT_Utilization_1](https://slurm.schedmd.com/sreport.html) Allocated, Associations, Cluster, End, Flags, Idle, Name, Nodes, ReservationId, Start, TotalTime, TresCount, TresName, TresTime
FORMAT OPTIONS FOR USER REPORTS
TopUsage [#OPT_TopUsage](https://slurm.schedmd.com/sreport.html) Account, Cluster, Login, Proper, Used
All commands and options are case-insensitive.
## EXPLANATION OF REPORT FIELDS[#SECTION_EXPLANATION-OF-REPORT-FIELDS](https://slurm.schedmd.com/sreport.html)
Account [#OPT_Account](https://slurm.schedmd.com/sreport.html) Account name
Allocated [#OPT_Allocated](https://slurm.schedmd.com/sreport.html) Cluster utilization report: Time that nodes were in use with active jobs or an
active reservation. This does not include reservations created with the MAINT or
IGNORE_JOBS flags.
Reservation reports: Time that nodes were in use with active jobs in this
reservation
Associations [#OPT_Associations](https://slurm.schedmd.com/sreport.html) Associations allowed in the reservation
Cluster [#OPT_Cluster](https://slurm.schedmd.com/sreport.html) Cluster name
Down [#OPT_Down](https://slurm.schedmd.com/sreport.html) Cluster utilization report only: Time that nodes were marked as Down or fully
Drained, or time that slurmctld was not responding (if TrackSlurmctldDown is set
in slurmdbd.conf)
End [#OPT_End](https://slurm.schedmd.com/sreport.html) Reservation reports only: End time
Energy [#OPT_Energy](https://slurm.schedmd.com/sreport.html) Energy use (if tracking energy consumption)
Flags [#OPT_Flags](https://slurm.schedmd.com/sreport.html) Reservation reports only: Flags applied to the reservation
Idle [#OPT_Idle](https://slurm.schedmd.com/sreport.html) Cluster utilization report: Time that nodes were not Allocated, Down,
PlannedDown, or Planned
Reservation reports: Time that nodes were not Allocated
Login [#OPT_Login](https://slurm.schedmd.com/sreport.html) User's login name
Name [#OPT_Name](https://slurm.schedmd.com/sreport.html) Reservation reports only: Reservation name
OverCommitted [#OPT_OverCommitted](https://slurm.schedmd.com/sreport.html) Cluster utilization report only: Time of eligible jobs waiting in the
queue over the Planned time. This contains any overflow of Planned time that
would otherwise exceed the Reported time. It is typically useful to
determine whether your system is overloaded and by how much.
Planned [#OPT_Planned](https://slurm.schedmd.com/sreport.html) Cluster utilization report only: Time that nodes were not Allocated, Down or
PlannedDown with eligible jobs in the queue that were unable to start due to
time or size constraints. If Allocated plus Planned time exceeds the Reported
time, the excess will be reported as OverCommitted. If this value is not of
importance for you then the number can be grouped with idle time.
PlannedDown [#OPT_PlannedDown](https://slurm.schedmd.com/sreport.html) Cluster utilization report only: Time that nodes were in use by a reservation
created with the MAINT flag but not the IGNORE_JOBS flag. Also, time that nodes
were in the FUTURE or POWERED_DOWN state.
Proper Name [#OPT_Proper-Name](https://slurm.schedmd.com/sreport.html) User's proper/real name
Reported [#OPT_Reported](https://slurm.schedmd.com/sreport.html) Cluster utilization report only: Total time that records are available for.
Nodes that were added to or removed from the cluster during the report period
will only contribute usage data for the time they were present in the cluster
and cause percentage calculations to deviate from 100%.
ReservationId [#OPT_ReservationId](https://slurm.schedmd.com/sreport.html) Reservation reports only: Reservation ID
Start [#OPT_Start](https://slurm.schedmd.com/sreport.html) Reservation reports only: Start time
TotalTime [#OPT_TotalTime](https://slurm.schedmd.com/sreport.html) Reservation reports only: Amount of time the reservation was valid
TresCount [#OPT_TresCount](https://slurm.schedmd.com/sreport.html) Number of TRES present
TresName [#OPT_TresName](https://slurm.schedmd.com/sreport.html) Name of TRES reported
TresTime [#OPT_TresTime](https://slurm.schedmd.com/sreport.html) Reservation reports only: Total TRES-time in the reservation
Used [#OPT_Used](https://slurm.schedmd.com/sreport.html) Used TRES-minutes
Wckey [#OPT_Wckey](https://slurm.schedmd.com/sreport.html) Workload Characterization Key
## PERFORMANCE[#SECTION_PERFORMANCE](https://slurm.schedmd.com/sreport.html)
Executing sreport sends a remote procedure call to slurmdbd . If
enough calls from sreport or other Slurm client commands that send remote
procedure calls to the slurmdbd daemon come in at once, it can result in a
degradation of performance of the slurmdbd daemon, possibly resulting in a
denial of service.
Do not run sreport or other Slurm client commands that send remote
procedure calls to slurmdbd from loops in shell scripts or other programs.
Ensure that programs limit calls to sreport to the minimum necessary for
the information you are trying to gather.
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/sreport.html)
Some sreport options may be set via environment variables. These
environment variables, along with their corresponding options, are listed below.
(Note: Command line options will always override these settings.)
SREPORT_CLUSTER [#OPT_SREPORT_CLUSTER](https://slurm.schedmd.com/sreport.html) Same as -M , --cluster
SREPORT_FEDERATION [#OPT_SREPORT_FEDERATION](https://slurm.schedmd.com/sreport.html) Same as --federation
SREPORT_LOCAL [#OPT_SREPORT_LOCAL](https://slurm.schedmd.com/sreport.html) Same as --local
SREPORT_TRES [#OPT_SREPORT_TRES](https://slurm.schedmd.com/sreport.html) Same as -t, --tres
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/sreport.html) The location of the Slurm configuration file.
## EXAMPLES[#SECTION_EXAMPLES](https://slurm.schedmd.com/sreport.html)
Report number of jobs per account according to different job size bins:
```text
$ sreport job sizesbyaccount Start=11:00 -------------------------------------------------------------------------------- Job Sizes 2024-08-19T11:00:00 - 2024-08-19T11:59:59 (3600 secs) Time reported in Minutes -------------------------------------------------------------------------------- Cluster Account 0-49 CPUs 50-249 CPUs 250-499 CPUs 500-999 CPUs >= 1000 CPUs % of cluster --------- --------- ------------- ------------- ------------- ------------- ------------- ------------ minesofm+ root 770 0 0 0 0 100.00%
```
Report cluster utilization:
```text
$ sreport cluster utilization Start=11:00 -------------------------------------------------------------------------------- Cluster Utilization 2024-08-19T11:00:00 - 2024-08-19T11:59:59 Usage reported in CPU Minutes -------------------------------------------------------------------------------- Cluster Allocate Down Planned Idle Planned Reported --------- -------- -------- -------- -------- -------- -------- minesofm+ 770 120 239 3791 239 4920
```
Report top usage:
```text
$ sreport user top Start=11:00 -------------------------------------------------------------------------------- Top 10 Users 2024-08-19T11:00:00 - 2024-08-19T11:59:59 (3600 secs) Usage reported in CPU Minutes -------------------------------------------------------------------------------- Cluster Login Proper Name Account Used Energy --------- --------- --------------- --------------- -------- -------- minesofm+ stephen ,,, main 538 0 minesofm+ phteven ,,, main 145 0 minesofm+ phteven ,,, rivendell 45 0 minesofm+ stephen ,,, rivendell 41 0
```
Report jobs by size from specific user and account:
```text
$ sreport job sizesbyaccount All_Clusters users=stephen account=main PrintJobCount Start=11:00 -------------------------------------------------------------------------------- Job Sizes 2024-08-19T11:00:00 - 2024-08-19T11:59:59 (3600 secs) Units are in number of jobs ran -------------------------------------------------------------------------------- Cluster Account 0-49 CPUs 50-249 CPUs 250-499 CPUs 500-999 CPUs >= 1000 CPUs % of cluster --------- --------- ------------- ------------- ------------- ------------- ------------- ------------ minesofm+ main 12 0 0 0 0 100.00%
```
Report cluster account utilization with the specified fields during the
specified day and by the specified user:
```text
$ sreport cluster AccountUtilizationByUser start=7/10 end=7/11 cluster=minesofmoria user=stephen format=Account,Cluster,TresCount,Login,Proper,Used -------------------------------------------------------------------------------- Cluster/Account/User Utilization 2024-07-10T00:00:00 - 2024-07-10T23:59:59 (86400 secs) Usage reported in CPU Minutes -------------------------------------------------------------------------------- Account Cluster TRES Count Login Proper Name Used --------------- --------- ---------- --------- --------------- -------- main minesofm+ stephen ,,, 38 rivendell minesofm+ stephen ,,, 1 arwen minesofm+ stephen ,,, 1 elrond minesofm+ stephen ,,, 1
```
Report cluster account utilization by user for a specific account during a
1-week period:
```text
$ sreport cluster AccountUtilizationByUser start=7/23 end=7/24 cluster=minesofmoria account=main -------------------------------------------------------------------------------- Cluster/Account/User Utilization 2024-07-23T00:00:00 - 2024-07-23T23:59:59 (86400 secs) Usage reported in CPU Minutes -------------------------------------------------------------------------------- Cluster Account Login Proper Name Used Energy --------- --------------- --------- --------------- -------- -------- minesofm+ main 148 0 minesofm+ main phteven ,,, 2 0 minesofm+ main stephen ,,, 146 0
```
Report top usage in percent for a specific account:
```text
$ sreport user topusage start=11:00 -t percent account=main -------------------------------------------------------------------------------- Top 10 Users 2024-08-19T11:00:00 - 2024-08-19T11:59:59 (3600 secs) Usage reported in Percentage of Total -------------------------------------------------------------------------------- Cluster Login Proper Name Account Used Energy --------- --------- --------------- --------------- -------- -------- minesofm+ stephen ,,, main 10.94% 0.00% minesofm+ phteven ,,, main 2.95% 0.00%
```
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/sreport.html)
Copyright (C) 2009-2010 Lawrence Livermore National Security.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/sreport.html)
[sacct](https://slurm.schedmd.com/sacct.html) (1), [slurmdbd](https://slurm.schedmd.com/slurmdbd.html) (8)
## Index
[NAME](https://slurm.schedmd.com/sreport.html)
[SYNOPSIS](https://slurm.schedmd.com/sreport.html)
[DESCRIPTION](https://slurm.schedmd.com/sreport.html)
[OPTIONS](https://slurm.schedmd.com/sreport.html)
[COMMANDS](https://slurm.schedmd.com/sreport.html)
[REPORT TYPES](https://slurm.schedmd.com/sreport.html)
[REPORT DESCRIPTION](https://slurm.schedmd.com/sreport.html)
[FORMAT OPTIONS FOR EACH REPORT](https://slurm.schedmd.com/sreport.html)
[EXPLANATION OF REPORT FIELDS](https://slurm.schedmd.com/sreport.html)
[PERFORMANCE](https://slurm.schedmd.com/sreport.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/sreport.html)
[EXAMPLES](https://slurm.schedmd.com/sreport.html)
[COPYING](https://slurm.schedmd.com/sreport.html)
[SEE ALSO](https://slurm.schedmd.com/sreport.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
