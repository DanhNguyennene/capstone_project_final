---
source_url: https://slurm.schedmd.com/sacctmgr.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:18 UTC
title: "Slurm Workload Manager - sacctmgr"
---

# sacctmgr
Section: Slurm Commands (1)
Updated: Slurm Commands
[Index](https://slurm.schedmd.com/sacctmgr.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/sacctmgr.html)
sacctmgr - Used to view and modify Slurm account information.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/sacctmgr.html)
sacctmgr [ OPTIONS ...] [ COMMAND ...]
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/sacctmgr.html)
sacctmgr is used to view or modify Slurm account information.
The account information is maintained within a database with the interface
being provided by slurmdbd (Slurm Database daemon).
This database can serve as a central storehouse of user and
computer information for multiple computers at a single site.
Slurm account information is recorded based upon four parameters
that form what is referred to as an association .
These parameters are user , cluster , partition , and
account . user is the login name.
cluster is the name of a Slurm managed cluster as specified by
the ClusterName parameter in the slurm.conf configuration file.
partition is the name of a Slurm partition on that cluster.
account is the account for a job.
The intended mode of operation is to initiate the sacctmgr command,
add, delete, modify, and/or list association records then
commit the changes and exit.
NOTE : The contents of Slurm's database are maintained in lower case.
This may result in some sacctmgr output differing from that of other
Slurm commands.
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
-s , --associations [#OPT_associations](https://slurm.schedmd.com/sacctmgr.html) Use with show or list to display associations with the entity.
This is equivalent to the associations command.
-h , --help [#OPT_help](https://slurm.schedmd.com/sacctmgr.html) Print a help message describing the usage of sacctmgr .
This is equivalent to the help command.
-i , --immediate [#OPT_immediate](https://slurm.schedmd.com/sacctmgr.html) Commit changes immediately without asking for confirmation.
--json , --json = list , --json =< data_parser >[#OPT_json](https://slurm.schedmd.com/sacctmgr.html) Dump information as JSON using the default data_parser plugin or explicit
data_parser with parameters. Sorting and formatting arguments will be ignored.
This option is not available for every command.
-n , --noheader [#OPT_noheader](https://slurm.schedmd.com/sacctmgr.html) No header will be added to the beginning of the output.
-p , --parsable [#OPT_parsable](https://slurm.schedmd.com/sacctmgr.html) Output will be '|' delimited with a '|' at the end.
-P , --parsable2 [#OPT_parsable2](https://slurm.schedmd.com/sacctmgr.html) Output will be '|' delimited without a '|' at the end.
-Q , --quiet [#OPT_quiet](https://slurm.schedmd.com/sacctmgr.html) Print no messages other than error messages.
This is equivalent to the quiet command.
-r , --readonly [#OPT_readonly](https://slurm.schedmd.com/sacctmgr.html) Makes it so the running sacctmgr cannot modify accounting information.
The readonly option is for use within interactive mode.
--yaml , --yaml = list , --yaml =< data_parser >[#OPT_yaml](https://slurm.schedmd.com/sacctmgr.html) Dump information as YAML using the default data_parser plugin or explicit
data_parser with parameters. Sorting and formatting arguments will be ignored.
This option is not available for every command.
-v , --verbose [#OPT_verbose](https://slurm.schedmd.com/sacctmgr.html) Enable detailed logging.
This is equivalent to the verbose command.
-V , --version [#OPT_version](https://slurm.schedmd.com/sacctmgr.html) Display version number.
This is equivalent to the version command.
## COMMANDS[#SECTION_COMMANDS](https://slurm.schedmd.com/sacctmgr.html)
add < ENTITY > < SPECS >[#OPT_add](https://slurm.schedmd.com/sacctmgr.html) Add an entity.
Identical to the create command.
archive {dump|load} < SPECS >[#OPT_archive](https://slurm.schedmd.com/sacctmgr.html) Write database information to a flat file or load information that has
previously been written to a file.
clear stats [#OPT_clear-stats](https://slurm.schedmd.com/sacctmgr.html) Clear the server statistics.
create < ENTITY > < SPECS >[#OPT_create](https://slurm.schedmd.com/sacctmgr.html) Add an entity.
Identical to the add command.
delete < ENTITY > where < SPECS >[#OPT_delete](https://slurm.schedmd.com/sacctmgr.html) Delete the specified entities.
Identical to the remove command.
dump < cluster >[#OPT_dump](https://slurm.schedmd.com/sacctmgr.html) Dump cluster data to the specified file. If the filename is not specified
it uses clustername.cfg filename by default.
help [#OPT_help_1](https://slurm.schedmd.com/sacctmgr.html) Display a description of sacctmgr options and commands.
list < ENTITY > [< SPECS >][#OPT_list](https://slurm.schedmd.com/sacctmgr.html) Display information about the specified entity.
By default, all entries are displayed, you can narrow results by
specifying SPECS in your query.
Identical to the show command.
load < FILENAME >[#OPT_load](https://slurm.schedmd.com/sacctmgr.html) Load cluster data from the specified file. This is a configuration file
generated by running the sacctmgr dump command. This command does
not load archive data, see the sacctmgr archive load option instead.
modify < ENTITY > where < SPECS > set < SPECS >[#OPT_modify](https://slurm.schedmd.com/sacctmgr.html) Modify an entity.
ping [#OPT_ping](https://slurm.schedmd.com/sacctmgr.html) Ping slurmdbd.
reconfigure [#OPT_reconfigure](https://slurm.schedmd.com/sacctmgr.html) Reconfigures the SlurmDBD if running with one.
remove < ENTITY > where < SPECS >[#OPT_remove](https://slurm.schedmd.com/sacctmgr.html) Delete the specified entities.
Identical to the delete command.
show < ENTITY > [< SPECS >][#OPT_show](https://slurm.schedmd.com/sacctmgr.html) Display information about the specified entity.
By default, all entries are displayed, you can narrow results by
specifying SPECS in your query.
Identical to the list command.
shutdown [#OPT_shutdown](https://slurm.schedmd.com/sacctmgr.html) Shutdown the server.
version [#OPT_version_1](https://slurm.schedmd.com/sacctmgr.html) Display the version number of sacctmgr.
## INTERACTIVE COMMANDS[#SECTION_INTERACTIVE-COMMANDS](https://slurm.schedmd.com/sacctmgr.html)
NOTE :
All commands listed below can be used in the interactive mode, but NOT
on the initial command line.
exit [#OPT_exit](https://slurm.schedmd.com/sacctmgr.html) Terminate sacctmgr interactive mode.
Identical to the quit command.
quiet [#OPT_quiet_1](https://slurm.schedmd.com/sacctmgr.html) Print no messages other than error messages.
quit [#OPT_quit](https://slurm.schedmd.com/sacctmgr.html) Terminate the execution of sacctmgr interactive mode.
Identical to the exit command.
verbose [#OPT_verbose_1](https://slurm.schedmd.com/sacctmgr.html) Enable detailed logging.
This includes time-stamps on data structures, record counts, etc.
This is an independent command with no options meant for use in
interactive mode.
!! [#OPT_!!](https://slurm.schedmd.com/sacctmgr.html) Repeat the last command.
## ENTITIES[#SECTION_ENTITIES](https://slurm.schedmd.com/sacctmgr.html)
account [#OPT_account](https://slurm.schedmd.com/sacctmgr.html) An account, typically specified at job submit time using the
--account= option.
These may be arranged in a hierarchical fashion, for example
accounts 'chemistry' and 'physics' may be children of
the account 'science'.
The hierarchy may have an arbitrary depth.
association [#OPT_association](https://slurm.schedmd.com/sacctmgr.html) The entity used to group information consisting of four parameters:
account , cluster , partition (optional), and user .
Used only with the list or show command. Add, modify, and
delete should be done to a user, account or cluster entity, which will
in turn update the underlying associations. Modification of attributes like
limits is allowed for an association but not a modification of the four
core attributes of an association. You cannot change the partition setting
(or set one if it has not been set) for an existing association. Instead,
you will need to create a new association with the partition included. You
can either keep the previous association with no partition defined, or delete
it. Note that these newly added associations are unique entities and any
existing usage information will not be carried over to the new association.
cluster [#OPT_cluster](https://slurm.schedmd.com/sacctmgr.html) The ClusterName parameter in the slurm.conf configuration
file, used to differentiate accounts on different machines.
configuration [#OPT_configuration](https://slurm.schedmd.com/sacctmgr.html) Used only with the list or show command to report current
system configuration.
coordinator [#OPT_coordinator](https://slurm.schedmd.com/sacctmgr.html) A special privileged user, usually an account manager, that can
add users or sub-accounts to the account they are coordinator over.
This should be a trusted person since they can change limits on
account and user associations, as well as cancel, requeue or reassign
accounts of jobs inside their realm.
event [#OPT_event](https://slurm.schedmd.com/sacctmgr.html) Events like downed or drained nodes on clusters. Note that this does not
include transitory states like DRAINING.
federation [#OPT_federation](https://slurm.schedmd.com/sacctmgr.html) A group of clusters that work together to schedule jobs.
job [#OPT_job](https://slurm.schedmd.com/sacctmgr.html) Used to modify specific fields of a job: Derived Exit Code, Comment,
AdminComment, Extra, SystemComment, TRES, or WCKey.
problem [#OPT_problem](https://slurm.schedmd.com/sacctmgr.html) Use with show or list to display entity problems.
qos [#OPT_qos](https://slurm.schedmd.com/sacctmgr.html) Quality of Service.
reservation [#OPT_reservation](https://slurm.schedmd.com/sacctmgr.html) A collection of resources set apart for use by a particular account, user
or group of users for a given period of time.
resource [#OPT_resource](https://slurm.schedmd.com/sacctmgr.html) Software resources for the system. Those are software licenses shared
among clusters.
RunawayJobs [#OPT_RunawayJobs](https://slurm.schedmd.com/sacctmgr.html) Used only with the list or show command to report current
jobs that have been orphaned on the local cluster and are now
runaway. If there are jobs in this state it will also give you an
option to "fix" them.
This sets the end time for each job to the latest of the job's start, eligible,
and submit times, and sets the state to completed by default. Once corrected,
this triggers the SlurmDBD to recalculate the usage from before the earliest
submit time of all the runaway jobs. You must have an AdminLevel of at
least Operator to perform this.
NOTE : This operation could take a long time and sreport may not return
data until the recalculation is complete. It is best to run this when the
system is not busy.
stats [#OPT_stats](https://slurm.schedmd.com/sacctmgr.html) Used with list or show command to view server statistics.
Accepts optional argument of ave_time or total_time to sort on those
fields. By default, sorts on increasing RPC count field.
transaction [#OPT_transaction](https://slurm.schedmd.com/sacctmgr.html) List of transactions that have occurred during a given time period.
tres [#OPT_tres](https://slurm.schedmd.com/sacctmgr.html) Used with list or show command to view a list of Trackable
RESources configured on the system.
user [#OPT_user](https://slurm.schedmd.com/sacctmgr.html) The login name. Usernames are case-insensitive (forced to lowercase) unless
the PreserveCaseUser option has been set in the SlurmDBD configuration
file.
wckeys [#OPT_wckeys](https://slurm.schedmd.com/sacctmgr.html) Workload Characterization Key. An arbitrary string for grouping orthogonal accounts.
## GENERAL SPECIFICATIONS FOR ASSOCIATION BASED ENTITIES[#SECTION_GENERAL-SPECIFICATIONS-FOR-ASSOCIATION-BASED-ENTITIES](https://slurm.schedmd.com/sacctmgr.html)
NOTE : The group limits (GrpJobs, GrpTRES, etc.) are tested when a job is
being considered for being allocated resources.
If starting a job would cause any of its group limit to be exceeded,
that job will not be considered for scheduling even if that job might preempt
other jobs which would release sufficient group resources for the pending
job to be initiated.
NOTE : TRES limit modifications of any kind using "+=" or "-=" syntax
will always produce a value between 0 and 18446744073709551600.
Trying to set a negative value using "-=" will set that TRES to 0, even if
there was not a TRES limit present beforehand.
DefaultQOS =< default_qos >[#OPT_DefaultQOS](https://slurm.schedmd.com/sacctmgr.html) The QOS this association and its children will use by default if allowed in the
QosLevel list mentioned below.
This is overridden if set directly on a user.
To clear an existing value, set a new value of -1.
Fairshare ={< fairshare_number >|parent}[#OPT_Fairshare](https://slurm.schedmd.com/sacctmgr.html)
Share ={< fairshare_number >|parent}[#OPT_Share](https://slurm.schedmd.com/sacctmgr.html)
Allocated shares used for fairshare calculation. Can also be the string
parent , which is interpreted differently if set on a user or on an account.
If set on a user, the parent association is used for fairshare.
If set on an account, that account's children will be effectively re-parented
for fairshare calculations to the first parent of their parent that is not
Fairshare=parent. Limits remain the same, only its fairshare value is affected.
To clear an existing value, set a new value of -1.
GrpJobs =< max_jobs >[#OPT_GrpJobs](https://slurm.schedmd.com/sacctmgr.html) Maximum number of running jobs in aggregate for this association and its
children.
To clear an existing value, set a new value of -1.
GrpJobsAccrue =< max_jobs >[#OPT_GrpJobsAccrue](https://slurm.schedmd.com/sacctmgr.html) Maximum number of pending jobs in aggregate able to accrue age priority for this
association and its children.
To clear an existing value, set a new value of -1.
GrpSubmit =< max_jobs >[#OPT_GrpSubmit](https://slurm.schedmd.com/sacctmgr.html)
GrpSubmitJobs =< max_jobs >[#OPT_GrpSubmitJobs](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of jobs in a pending or running state at any time in aggregate
for this association and its children.
To clear an existing value, set a new value of -1.
GrpTRES =TRES[+|-]=< max_TRES >[,TRES[+|-]=< max_TRES >,...][#OPT_GrpTRES](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES able to be allocated by running jobs in aggregate for
this association and its children.
Refer to the TRES information section below for further details.
GrpTRESMins =TRES[+|-]=< minutes >[,TRES[+|-]=< minutes >,...][#OPT_GrpTRESMins](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES minutes that can possibly be used by past, present, and
future jobs in this association and its children.
Refer to the TRES information section below for further details.
NOTE : This limit is not enforced if set on the root
association of a cluster. So even though it may appear in sacctmgr
output, it will not be enforced.
NOTE : This limit only applies when using the Priority Multifactor
plugin. The time is decayed using the value of PriorityDecayHalfLife
or PriorityUsageResetPeriod as set in the slurm.conf. When this limit
is reached all associated jobs running will be killed and all future
jobs submitted with associations in the group will be delayed until
they are able to run inside the limit.
GrpTRESRunMins =TRES[+|-]=< minutes >[,TRES[+|-]=< minutes >,...][#OPT_GrpTRESRunMins](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES minutes able to be allocated by running jobs in this
association and its children. This takes into consideration time limit of
running jobs and consumes it. If the limit is reached no new jobs are started
until other jobs finish to allow time to free up.
Refer to the TRES information section below for further details.
GrpWall =< max_wall >[#OPT_GrpWall](https://slurm.schedmd.com/sacctmgr.html) Maximum wall clock time able to be allocated by running jobs in aggregate in
this association and its children.
GrpWall format is <min> or <min>:<sec> or <hr>:<min>:<sec> or
<days>-<hr>:<min>:<sec> or <days>-<hr>.
The value is recorded in minutes with rounding as needed.
To clear an existing value, set a new value of -1.
NOTE : Although it may appear in sacctmgr output, this limit will not
be enforced if set on the root association of a cluster.
NOTE : This limit only applies when using the Priority Multifactor
plugin. The time is decayed using the value of PriorityDecayHalfLife
or PriorityUsageResetPeriod as set in the slurm.conf. When this limit
is reached all associated jobs running will be killed and all future
jobs submitted with associations in the group will be delayed until
they are able to run inside the limit.
MaxJobs =< max_jobs >[#OPT_MaxJobs](https://slurm.schedmd.com/sacctmgr.html) Maximum number of running jobs per user in this association. This is overridden
if set directly on a user. Default is the cluster's limit.
To clear an existing value, set a new value of -1.
MaxJobsAccrue =< max_jobs >[#OPT_MaxJobsAccrue](https://slurm.schedmd.com/sacctmgr.html) Maximum number of pending jobs able to accrue age priority at any given time in
this association. This is overridden if set directly on a user.
Default is the cluster's limit.
To clear an existing value, set a new value of -1.
MaxSubmit =< max_jobs >[#OPT_MaxSubmit](https://slurm.schedmd.com/sacctmgr.html)
MaxSubmitJobs =< max_jobs >[#OPT_MaxSubmitJobs](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of jobs in a pending or running state at any time in this
association. Default is the cluster's limit.
To clear an existing value, set a new value of -1.
MaxTRES =TRES[+|-]=< max_TRES >[,TRES[+|-]=< max_TRES >,...][#OPT_MaxTRES](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPJ =TRES[+|-]=< max_TRES >[,TRES[+|-]=< max_TRES >,...][#OPT_MaxTRESPJ](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPerJob =TRES[+|-]=< max_TRES >[,TRES[+|-]=< max_TRES >,...][#OPT_MaxTRESPerJob](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES each job can use in this association.
This is overridden if set directly on a user.
Default is the cluster's limit.
Refer to the TRES information section below for further details.
MaxTRESMins =TRES[+|-]=< minutes >[,TRES[+|-]=< minutes >,...][#OPT_MaxTRESMins](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESMinsPJ =TRES[+|-]=< minutes >[,TRES[+|-]=< minutes >,...][#OPT_MaxTRESMinsPJ](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESMinsPerJob =TRES[+|-]=< minutes >[,TRES[+|-]=< minutes >,...][#OPT_MaxTRESMinsPerJob](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES minutes each job can use in this association.
This is overridden if set directly on a user.
Default is the cluster's limit.
Refer to the TRES information section below for further details.
MaxTRESPN =TRES[+|-]=< max_TRES >[,TRES[+|-]=< max_TRES >,...][#OPT_MaxTRESPN](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPerNode =TRES[+|-]=< max_TRES >[,TRES[+|-]=< max_TRES >,...][#OPT_MaxTRESPerNode](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES each node in a job allocation can use in this association.
This is overridden if set directly on a user.
Default is the cluster's limit.
Refer to the TRES information section below for further details.
MaxWall =< max_wall >[#OPT_MaxWall](https://slurm.schedmd.com/sacctmgr.html)
MaxWallDurationPerJob =< max_wall >[#OPT_MaxWallDurationPerJob](https://slurm.schedmd.com/sacctmgr.html)
Maximum wall clock time each job can use in this association.
This is overridden if set directly on a user.
Default is the cluster's limit.
MaxWall format is <min> or <min>:<sec> or <hr>:<min>:<sec> or
<days>-<hr>:<min>:<sec> or <days>-<hr>.
The value is recorded in minutes with rounding as needed.
To clear an existing value, set a new value of -1.
NOTE : Changing this value will have no effect on any running jobs,
but may update the default time limit for pending jobs.
Priority [#OPT_Priority](https://slurm.schedmd.com/sacctmgr.html) Association priority factor to be used by the priority/multifactor plugin.
This is overridden if set directly on a user.
Unset by default, indicating that no extra priority is granted.
To clear an existing value, set a new value of -1.
QosLevel < operator >< comma_separated_list_of_qos_names >[#OPT_QosLevel](https://slurm.schedmd.com/sacctmgr.html) List of QOS names available to jobs running in this association. To get a list
of valid QOSs use 'sacctmgr list qos'.
This value will override its parents value and push down to its
children as the new default. Setting a QosLevel to '' (two single
quotes with nothing between them) restores its default setting. You
can also use the operator += and -= to add or remove certain QOSs
from the QOS list.
Valid <operator> values include:
=
Set QosLevel to the specified value. NOTE : the QOS that can be used
at a given account in the hierarchy are inherited by the children of that account.
By assigning QOS with the = sign only the assigned QOS can be used by the
account and its children.
+=
Add the specified <qos> value to the current QosLevel . The account will
have access to this QOS and any others previously assigned to it.
-=
Remove the specified <qos> value from the current QosLevel .
See the EXAMPLES section below.
## SPECIFICATIONS FOR ACCOUNTS[#SECTION_SPECIFICATIONS-FOR-ACCOUNTS](https://slurm.schedmd.com/sacctmgr.html)
Accounts can be created, modified, and deleted with sacctmgr. These options
allow you to set the corresponding attributes or filter on them when
querying for Accounts.
Cluster =< cluster >[#OPT_Cluster](https://slurm.schedmd.com/sacctmgr.html) Specific cluster to add account to. Default is all in system.
Description =< description >[#OPT_Description](https://slurm.schedmd.com/sacctmgr.html) An arbitrary string describing an account.
Flags =< flag >[,< flag >,...][#OPT_Flags](https://slurm.schedmd.com/sacctmgr.html)
Valid options are:
NoUsersAreCoords [#OPT_NoUsersAreCoords](https://slurm.schedmd.com/sacctmgr.html) Remove the privilege UsersAreCoords sets.
UsersAreCoords [#OPT_UsersAreCoords](https://slurm.schedmd.com/sacctmgr.html) If set, all users in this account will have the coordinator status here and of
any sub-account in it's hierarchy.
Name =< name >[#OPT_Name](https://slurm.schedmd.com/sacctmgr.html) The name of an account.
Note the name must be unique and can not be represent different
accounts at different points in the account hierarchy.
Organization =< org >[#OPT_Organization](https://slurm.schedmd.com/sacctmgr.html) Organization to which the account belongs.
Parent =< parent >[#OPT_Parent](https://slurm.schedmd.com/sacctmgr.html) Parent account of this account. Default is the root account, a top
level account.
RawUsage =< value >[#OPT_RawUsage](https://slurm.schedmd.com/sacctmgr.html) This allows an administrator to reset the raw usage accrued to an
account. The only value currently supported is 0 (zero). This is a
settable specification only - it cannot be used as a filter to list
accounts.
WithAssoc [#OPT_WithAssoc](https://slurm.schedmd.com/sacctmgr.html) Display all associations for this account.
WithCoord [#OPT_WithCoord](https://slurm.schedmd.com/sacctmgr.html) Display all coordinators for this account.
WithDeleted [#OPT_WithDeleted](https://slurm.schedmd.com/sacctmgr.html) Display information with previously deleted data.
Accounts that are deleted within 24 hours of being created and did not have
a job run in the account during that time will be removed from the database.
Otherwise, the account will be marked as deleted and will be viewable with
the WithDeleted flag.
NOTE : If using the WithAssoc option you can also query against
association specific information to view only certain associations
this account may have. These extra options can be found in the
SPECIFICATIONS FOR ASSOCIATIONS section. You can also use the
general specifications list above in the GENERAL SPECIFICATIONS FOR
ASSOCIATION BASED ENTITIES section.
## LIST/SHOW ACCOUNT FORMAT OPTIONS[#SECTION_LIST/SHOW-ACCOUNT-FORMAT-OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
Fields you can display when viewing Account records by using the format=
option. The default format is:
Account,Description,Organization
Account [#OPT_Account](https://slurm.schedmd.com/sacctmgr.html) The name of an account.
Description [#OPT_Description_1](https://slurm.schedmd.com/sacctmgr.html) An arbitrary string describing an account.
Flags [#OPT_Flags_1](https://slurm.schedmd.com/sacctmgr.html) Flags set on the account.
Organization [#OPT_Organization_1](https://slurm.schedmd.com/sacctmgr.html) Organization to which the account belongs.
Coordinators [#OPT_Coordinators](https://slurm.schedmd.com/sacctmgr.html) List of users that are a coordinator of the account. (Only filled in
when using the WithCoordinator option.)
NOTE : If using the WithAssoc option you can also view the information
about the various associations the account may have on all the
clusters in the system. The association information can be filtered.
Note that all the accounts in the database will always be shown as filter only
takes effect over the association data. The Association format fields are
described in the LIST/SHOW ASSOCIATION FORMAT OPTIONS section.
## SPECIFICATIONS FOR ASSOCIATIONS[#SECTION_SPECIFICATIONS-FOR-ASSOCIATIONS](https://slurm.schedmd.com/sacctmgr.html)
Associations can be created, modified, and deleted with sacctmgr. These
options allow you to set the corresponding attributes or filter on them
when querying for Associations.
Clusters =< cluster_name >[,< cluster_name >,...][#OPT_Clusters](https://slurm.schedmd.com/sacctmgr.html) List the associations of the cluster(s).
Accounts =< account_name >[,< account_name >,...][#OPT_Accounts](https://slurm.schedmd.com/sacctmgr.html) List the associations of the account(s).
Users =< user_name >[,< user_name >,...][#OPT_Users](https://slurm.schedmd.com/sacctmgr.html) List the associations of the user(s).
Partitions =< partition_name >[,< partition_name >,...][#OPT_Partitions](https://slurm.schedmd.com/sacctmgr.html) List the associations of the partition(s).
NOTE : Use Partitions="" or Partitions='' with no other names listed
when specifying the case where there is no partition. This can be useful
when using a command with an entity that has associations with and without
partitions. If given in a shell where the quotes will be consumed then
they must be quoted themselves. For example: Partitions=\"\".
NOTE : You can also use the general specifications list above in the
GENERAL SPECIFICATIONS FOR ASSOCIATION BASED ENTITIES section.
Other options unique for listing associations:
OnlyDefaults [#OPT_OnlyDefaults](https://slurm.schedmd.com/sacctmgr.html) Display only associations that are default associations
Tree [#OPT_Tree](https://slurm.schedmd.com/sacctmgr.html) Display account names in a hierarchical fashion.
WithDeleted [#OPT_WithDeleted_1](https://slurm.schedmd.com/sacctmgr.html) Display information with previously deleted data.
Associations that are deleted within 24 hours of being created and did not have
a job run in the association during that time will be removed from the database.
Otherwise, the association will be marked as deleted and will be viewable with
the WithDeleted flag.
WithSubAccounts [#OPT_WithSubAccounts](https://slurm.schedmd.com/sacctmgr.html) Display information with subaccounts. Only really valuable when used
with the account= option. This will display all the subaccount
associations along with the accounts listed in the option.
WOLimits [#OPT_WOLimits](https://slurm.schedmd.com/sacctmgr.html) Display information without limit information. This is for a smaller
default format of "Cluster,Account,User,Partition".
WOPInfo [#OPT_WOPInfo](https://slurm.schedmd.com/sacctmgr.html) Display information without parent information (i.e. parent id, and
parent account name). This option also implicitly sets the WOPLimits
option.
WOPLimits [#OPT_WOPLimits](https://slurm.schedmd.com/sacctmgr.html) Display information without hierarchical parent limits (i.e. will
only display limits where they are set instead of propagating them
from the parent).
## LIST/SHOW ASSOCIATION FORMAT OPTIONS[#SECTION_LIST/SHOW-ASSOCIATION-FORMAT-OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
Fields you can display when viewing Association records by using the
format= option.
Account [#OPT_Account_1](https://slurm.schedmd.com/sacctmgr.html) The name of an account in the association.
Cluster [#OPT_Cluster_1](https://slurm.schedmd.com/sacctmgr.html) The name of a cluster in the association.
DefaultQOS [#OPT_DefaultQOS_1](https://slurm.schedmd.com/sacctmgr.html) The QOS this association and its children will use by default if allowed in the
QosLevel list mentioned below.
Fairshare [#OPT_Fairshare_1](https://slurm.schedmd.com/sacctmgr.html)
Share [#OPT_Share_1](https://slurm.schedmd.com/sacctmgr.html)
Allocated shares used for fairshare calculation. Can also be the string
parent , which is interpreted differently if set on a user or on an account.
If set on a user, the parent association is used for fairshare.
If set on an account, that account's children will be effectively re-parented
for fairshare calculations to the first parent of their parent that is not
Fairshare=parent. Limits remain the same, only its fairshare value is affected.
Flags [#OPT_Flags_2](https://slurm.schedmd.com/sacctmgr.html) Flags set on the association.
GrpJobs [#OPT_GrpJobs_1](https://slurm.schedmd.com/sacctmgr.html) Maximum number of running jobs in aggregate for this association and its
children.
GrpJobsAccrue [#OPT_GrpJobsAccrue_1](https://slurm.schedmd.com/sacctmgr.html) Maximum number of pending jobs in aggregate able to accrue age priority for this
association and its children.
GrpSubmit [#OPT_GrpSubmit_1](https://slurm.schedmd.com/sacctmgr.html)
GrpSubmitJobs [#OPT_GrpSubmitJobs_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of jobs in a pending or running state at any time in aggregate
for this association and its children.
GrpTRES [#OPT_GrpTRES_1](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES able to be allocated by running jobs in aggregate for
this association and its children.
GrpTRESMins [#OPT_GrpTRESMins_1](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES minutes that can possibly be used by past, present, and
future jobs in this association and its children.
GrpTRESRunMins [#OPT_GrpTRESRunMins_1](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES minutes able to be allocated by running jobs in this
association and its children. This takes into consideration time limit of
running jobs and consumes it. If the limit is reached no new jobs are started
until other jobs finish to allow time to free up.
GrpWall [#OPT_GrpWall_1](https://slurm.schedmd.com/sacctmgr.html) Maximum wall clock time able to be allocated by running jobs in aggregate in
this association and its children.
ID [#OPT_ID](https://slurm.schedmd.com/sacctmgr.html) The id of the association.
Lineage [#OPT_Lineage](https://slurm.schedmd.com/sacctmgr.html) Complete path up the hierarchy to the root association.
MaxJobs [#OPT_MaxJobs_1](https://slurm.schedmd.com/sacctmgr.html) Maximum number of running jobs per user.
MaxJobsAccrue [#OPT_MaxJobsAccrue_1](https://slurm.schedmd.com/sacctmgr.html) Maximum number of pending jobs able to accrue age priority at any given time.
MaxSubmit [#OPT_MaxSubmit_1](https://slurm.schedmd.com/sacctmgr.html)
MaxSubmitJobs [#OPT_MaxSubmitJobs_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of jobs in a pending or running state at any time.
MaxTRES [#OPT_MaxTRES_1](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPJ [#OPT_MaxTRESPJ_1](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPerJob [#OPT_MaxTRESPerJob_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES each job can use.
MaxTRESMins [#OPT_MaxTRESMins_1](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESMinsPJ [#OPT_MaxTRESMinsPJ_1](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESMinsPerJob [#OPT_MaxTRESMinsPerJob_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES minutes each job can use.
MaxTRESPN [#OPT_MaxTRESPN_1](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPerNode [#OPT_MaxTRESPerNode_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES each node in a job allocation can use.
MaxWall [#OPT_MaxWall_1](https://slurm.schedmd.com/sacctmgr.html)
MaxWallDurationPerJob [#OPT_MaxWallDurationPerJob_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum wall clock time each job can use.
ParentID [#OPT_ParentID](https://slurm.schedmd.com/sacctmgr.html) The association id of the parent of this association.
ParentName [#OPT_ParentName](https://slurm.schedmd.com/sacctmgr.html) The account name of the parent of this association.
Partition [#OPT_Partition](https://slurm.schedmd.com/sacctmgr.html) The name of a partition in the association.
Priority [#OPT_Priority_1](https://slurm.schedmd.com/sacctmgr.html) Association priority factor to be used by the priority/multifactor plugin.
Qos [#OPT_Qos](https://slurm.schedmd.com/sacctmgr.html) Valid QOSs for this association.
QosRaw [#OPT_QosRaw](https://slurm.schedmd.com/sacctmgr.html) Numeric IDs of valid QOSs for this association.
User [#OPT_User](https://slurm.schedmd.com/sacctmgr.html) The name of a user in the association.
WithRawQOSLevel [#OPT_WithRawQOSLevel](https://slurm.schedmd.com/sacctmgr.html) Display QosLevel in an unevaluated raw format, consisting of a comma-separated
list of QOS names prepended with '' (nothing), '+' or '-' for
the association. QOS names without +/- prepended were assigned (ie,
sacctmgr modify ... set QosLevel=qos_name) for the entity listed or
on one of its parents in the hierarchy. QOS names with +/- prepended
indicate the QOS was added/filtered (ie, sacctmgr modify ... set
QosLevel=[+-]qos_name) for the entity listed or on one of its parents
in the hierarchy. Including WOPLimits will show exactly where each QOS
was assigned, added or filtered in the hierarchy.
## SPECIFICATIONS FOR CLUSTERS[#SECTION_SPECIFICATIONS-FOR-CLUSTERS](https://slurm.schedmd.com/sacctmgr.html)
Clusters can be created, modified, and deleted with sacctmgr. These
options allow you to set the corresponding attributes or filter on them
when querying for Clusters.
Classification =< classification >[#OPT_Classification](https://slurm.schedmd.com/sacctmgr.html) Type of machine, current classifications are capability, capacity and
capapacity.
Features [+|-]=< comma_separated_list_of_feature_names >[#OPT_Features](https://slurm.schedmd.com/sacctmgr.html) Features that are specific to the cluster. Federated jobs can be directed to
clusters that contain the job requested features.
To add or remove individual features, use the += or -= operators.
To clear all existing features, set a new value of '' (two single quotes with
nothing between them).
Federation =< federation >[#OPT_Federation](https://slurm.schedmd.com/sacctmgr.html) The federation that this cluster should be a member of. A cluster can only be a
member of one federation at a time.
FedState =< state >[#OPT_FedState](https://slurm.schedmd.com/sacctmgr.html) The state of the cluster in the federation.
Valid states are:
ACTIVE [#OPT_ACTIVE](https://slurm.schedmd.com/sacctmgr.html) Cluster will actively accept and schedule federated jobs.
INACTIVE [#OPT_INACTIVE](https://slurm.schedmd.com/sacctmgr.html) Cluster will not schedule or accept any jobs.
DRAIN [#OPT_DRAIN](https://slurm.schedmd.com/sacctmgr.html) Cluster will not accept any new jobs and will let existing federated jobs
complete.
DRAIN+REMOVE [#OPT_DRAIN+REMOVE](https://slurm.schedmd.com/sacctmgr.html) Cluster will not accept any new jobs and will remove itself from the federation
once all federated jobs have completed. When removed from the federation, the
cluster will accept jobs as a non-federated cluster.
Name =< name >[#OPT_Name_1](https://slurm.schedmd.com/sacctmgr.html) The name of a cluster.
This should be equal to the ClusterName parameter in the slurm.conf
configuration file for some Slurm-managed cluster.
RPC =< rpc_list >[#OPT_RPC](https://slurm.schedmd.com/sacctmgr.html) Comma-separated list of numeric RPC values.
WithDeleted [#OPT_WithDeleted_2](https://slurm.schedmd.com/sacctmgr.html) Display information with previously deleted data.
Clusters that are deleted within 24 hours of being created and did not have
a job run in the cluster during that time will be removed from the database.
Otherwise, the cluster will be marked as deleted and will be viewable with
the WithDeleted flag.
WithFed [#OPT_WithFed](https://slurm.schedmd.com/sacctmgr.html) Appends federation related columns to default format options
(e.g. Federation,ID,Features,FedState).
WOLimits [#OPT_WOLimits_1](https://slurm.schedmd.com/sacctmgr.html) Display information without limit information. This is for a smaller
default format of Cluster,ControlHost,ControlPort,RPC
NOTE : You can also use the general specifications list above in the
GENERAL SPECIFICATIONS FOR ASSOCIATION BASED ENTITIES section.
## LIST/SHOW CLUSTER FORMAT OPTIONS[#SECTION_LIST/SHOW-CLUSTER-FORMAT-OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
Fields you can display when viewing Cluster records by using the format=
option.
Classification [#OPT_Classification_1](https://slurm.schedmd.com/sacctmgr.html) Type of machine, i.e. capability, capacity or capapacity.
Cluster [#OPT_Cluster_2](https://slurm.schedmd.com/sacctmgr.html) The name of the cluster.
ControlHost [#OPT_ControlHost](https://slurm.schedmd.com/sacctmgr.html) When a slurmctld registers with the database the ip address of the
controller is placed here.
ControlPort [#OPT_ControlPort](https://slurm.schedmd.com/sacctmgr.html) When a slurmctld registers with the database the port the controller
is listening on is placed here.
Features [#OPT_Features_1](https://slurm.schedmd.com/sacctmgr.html) The list of features on the cluster (if any).
Federation [#OPT_Federation_1](https://slurm.schedmd.com/sacctmgr.html) The name of the federation this cluster is a member of (if any).
FedState [#OPT_FedState_1](https://slurm.schedmd.com/sacctmgr.html) The state of the cluster in the federation (if a member of one).
FedStateRaw [#OPT_FedStateRaw](https://slurm.schedmd.com/sacctmgr.html) Numeric value of the name of the FedState.
Flags [#OPT_Flags_3](https://slurm.schedmd.com/sacctmgr.html) Attributes possessed by the cluster. Current flags include Cray, External and
MultipleSlurmd.
External clusters are registration only clusters. A slurmctld can designate an
external slurmdbd with the AccountingStorageExternalHost slurm.conf
option. This allows a slurmctld to register to an external slurmdbd so that
clusters attached to the external slurmdbd can communicate with the external
cluster with Slurm commands.
ID [#OPT_ID_1](https://slurm.schedmd.com/sacctmgr.html) The ID assigned to the cluster when a member of a federation. This ID uniquely
identifies the cluster and its jobs in the federation.
NodeCount [#OPT_NodeCount](https://slurm.schedmd.com/sacctmgr.html) The current count of nodes associated with the cluster.
NodeNames [#OPT_NodeNames](https://slurm.schedmd.com/sacctmgr.html) The current Nodes associated with the cluster.
RPC [#OPT_RPC_1](https://slurm.schedmd.com/sacctmgr.html) When a slurmctld registers with the database the rpc version the controller
is running is placed here.
TRES [#OPT_TRES](https://slurm.schedmd.com/sacctmgr.html) Trackable RESources (Billing, BB (Burst buffer), CPU, Energy, GRES, License,
Memory, and Node) this cluster is accounting for.
NOTE : You can also view the information about the root association for
the cluster. The Association format fields are described
in the LIST/SHOW ASSOCIATION FORMAT OPTIONS section.
## SPECIFICATIONS FOR COORDINATOR[#SECTION_SPECIFICATIONS-FOR-COORDINATOR](https://slurm.schedmd.com/sacctmgr.html)
Coordinators can be created, modified, and deleted with sacctmgr. These
options allow you to set the corresponding attributes or filter on them
when querying for Coordinators.
Account =< account_name >[,< account_name >,...][#OPT_Account_2](https://slurm.schedmd.com/sacctmgr.html) Account name to add this user as a coordinator to.
Names =< user_name >[,< user_name >,...][#OPT_Names](https://slurm.schedmd.com/sacctmgr.html) Names of coordinators.
NOTE : To list coordinators use the WithCoordinator options with list
account or list user.
## SPECIFICATIONS FOR EVENTS[#SECTION_SPECIFICATIONS-FOR-EVENTS](https://slurm.schedmd.com/sacctmgr.html)
Events are automatically generated and sent to slurmdbd to be stored.
These are options you can specify to filter for specific types of events.
All_Clusters [#OPT_All_Clusters](https://slurm.schedmd.com/sacctmgr.html) Shortcut to get information on all clusters.
All_Time [#OPT_All_Time](https://slurm.schedmd.com/sacctmgr.html) Shortcut to get time period for all time.
Clusters =< cluster_name >[,< cluster_name >,...][#OPT_Clusters_1](https://slurm.schedmd.com/sacctmgr.html) List the events of the cluster(s). Default is the cluster where the
command was run.
CondFlags =< flag >[,< flag >,...][#OPT_CondFlags](https://slurm.schedmd.com/sacctmgr.html) Optional list of flags to filter events by.
Valid options are:
Open [#OPT_Open](https://slurm.schedmd.com/sacctmgr.html) If set, only open node events (currently down) will be returned.
End =< OPT >[#OPT_End](https://slurm.schedmd.com/sacctmgr.html) Period ending of events. Default is now.
Valid time formats are:
HH:MM[:SS] [AM|PM]
MMDD[YY] or MM/DD[/YY] or MM.DD[.YY]
MM/DD[/YY]-HH:MM[:SS]
YYYY-MM-DD[THH:MM[:SS]]
now[{+|-} count [seconds(default)|minutes|hours|days|weeks]]
Event =< OPT >[#OPT_Event](https://slurm.schedmd.com/sacctmgr.html) Specific types of events to look for. Valid options are Cluster or Node.
The default is both.
MaxCPUs =< OPT >[#OPT_MaxCPUs](https://slurm.schedmd.com/sacctmgr.html) Max number of CPUs affected by an event.
MinCPUs =< OPT >[#OPT_MinCPUs](https://slurm.schedmd.com/sacctmgr.html) Min number of CPUs affected by an event.
Nodes =< node_name >[,< node_name >,...][#OPT_Nodes](https://slurm.schedmd.com/sacctmgr.html) Node names affected by an event.
Reason =< reason >[,< reason >,...][#OPT_Reason](https://slurm.schedmd.com/sacctmgr.html) Reason associated with a node going down. A reason that contains a space
should be surrounded by quotes.
Start =< OPT >[#OPT_Start](https://slurm.schedmd.com/sacctmgr.html) Period start of events. Default is 00:00:00 of previous day, unless
states are given with the States=<spec> events. If this is the case
the default behavior is to return events currently in
the states specified.
Valid time formats are:
HH:MM[:SS] [AM|PM]
MMDD[YY] or MM/DD[/YY] or MM.DD[.YY]
MM/DD[/YY]-HH:MM[:SS]
YYYY-MM-DD[THH:MM[:SS]]
now[{+|-} count [seconds(default)|minutes|hours|days|weeks]]
States =< state >[,< state >,...][#OPT_States](https://slurm.schedmd.com/sacctmgr.html) State of a node in a node event. If this is set, the event type is
set automatically to Node.
User =< user_name >[,< user_name >,...][#OPT_User_1](https://slurm.schedmd.com/sacctmgr.html) Query against users who set the event. If this is set, the event type is
set automatically to Node since only the slurm user can perform a cluster
event.
## LIST/SHOW EVENT FORMAT OPTIONS[#SECTION_LIST/SHOW-EVENT-FORMAT-OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
Fields you can display when viewing Event records by using the format=
option. The default format is:
Cluster,NodeName,TimeStart,TimeEnd,State,Reason,User
Cluster [#OPT_Cluster_3](https://slurm.schedmd.com/sacctmgr.html) The name of the cluster event happened on.
ClusterNodes [#OPT_ClusterNodes](https://slurm.schedmd.com/sacctmgr.html) The hostlist of nodes on a cluster in a cluster event.
Duration [#OPT_Duration](https://slurm.schedmd.com/sacctmgr.html) Time period the event was around for.
End [#OPT_End_1](https://slurm.schedmd.com/sacctmgr.html) Period when event ended.
Event [#OPT_Event_1](https://slurm.schedmd.com/sacctmgr.html) Name of the event.
EventRaw [#OPT_EventRaw](https://slurm.schedmd.com/sacctmgr.html) Numeric value of the name of the event.
NodeName [#OPT_NodeName](https://slurm.schedmd.com/sacctmgr.html) The node affected by the event. In a cluster event, this is blank.
Reason [#OPT_Reason_1](https://slurm.schedmd.com/sacctmgr.html) The reason an event happened.
Start [#OPT_Start_1](https://slurm.schedmd.com/sacctmgr.html) Period when event started.
State [#OPT_State](https://slurm.schedmd.com/sacctmgr.html) On a node event this is the formatted state of the node during the event.
StateRaw [#OPT_StateRaw](https://slurm.schedmd.com/sacctmgr.html) On a node event this is the numeric value of the state of the node
during the event.
TRES [#OPT_TRES_1](https://slurm.schedmd.com/sacctmgr.html) Number of TRES involved with the event.
User [#OPT_User_2](https://slurm.schedmd.com/sacctmgr.html) On a node event this is the user who caused the event to happen.
## SPECIFICATIONS FOR FEDERATION[#SECTION_SPECIFICATIONS-FOR-FEDERATION](https://slurm.schedmd.com/sacctmgr.html)
Federations can be created, modified, and deleted with sacctmgr. These
options allow you to set the corresponding attributes or filter on them
when querying for Federations.
Clusters [+|-]=< cluster_name >[,< cluster_name >,...][#OPT_Clusters_2](https://slurm.schedmd.com/sacctmgr.html) List of clusters to add/remove to a federation. A blank value (e.g. clusters=)
will remove all federations for the federation. NOTE : A cluster can only
be a member of one federation.
Name =< name >[#OPT_Name_2](https://slurm.schedmd.com/sacctmgr.html) The name of the federation.
Tree [#OPT_Tree_1](https://slurm.schedmd.com/sacctmgr.html) Display federations in a hierarchical fashion.
WithDeleted [#OPT_WithDeleted_3](https://slurm.schedmd.com/sacctmgr.html) Display information with previously deleted data.
Federations that are deleted within 24 hours of being created will be removed
from the database. Federations that were created more than 24 hours prior to
the deletion request are just marked as deleted and will be viewable with
the WithDeleted flag.
## LIST/SHOW FEDERATION FORMAT OPTIONS[#SECTION_LIST/SHOW-FEDERATION-FORMAT-OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
Fields you can display when viewing Federation records by using the
format= option. The default format is:
Federation,Cluster,Features,FedState
Cluster [#OPT_Cluster_4](https://slurm.schedmd.com/sacctmgr.html) Name of the cluster that is a member of the federation.
Features [#OPT_Features_2](https://slurm.schedmd.com/sacctmgr.html) The list of features on the cluster.
Federation [#OPT_Federation_2](https://slurm.schedmd.com/sacctmgr.html) The name of the federation.
FedState [#OPT_FedState_2](https://slurm.schedmd.com/sacctmgr.html) The state of the cluster in the federation.
FedStateRaw [#OPT_FedStateRaw_1](https://slurm.schedmd.com/sacctmgr.html) Numeric value of the name of the FedState.
Index [#OPT_Index](https://slurm.schedmd.com/sacctmgr.html) The index of the cluster in the federation.
## SPECIFICATIONS FOR INSTANCES[#SECTION_SPECIFICATIONS-FOR-INSTANCES](https://slurm.schedmd.com/sacctmgr.html)
Information about cloud node instances is sent to slurmdbd to be stored.
These are options you can specify to filter for specific instances.
Clusters =< cluster_name >[,< cluster_name >,...][#OPT_Clusters_3](https://slurm.schedmd.com/sacctmgr.html) Name of the cluster that the instance ran on. Default is the cluster where the
command was run.
End =< OPT >[#OPT_End_2](https://slurm.schedmd.com/sacctmgr.html) Period ending of instances. Default is now.
Valid time formats are:
HH:MM[:SS] [AM|PM]
MMDD[YY] or MM/DD[/YY] or MM.DD[.YY]
MM/DD[/YY]-HH:MM[:SS]
YYYY-MM-DD[THH:MM[:SS]]
now[{+|-} count [seconds(default)|minutes|hours|days|weeks]]
Extra =< OPT >[#OPT_Extra](https://slurm.schedmd.com/sacctmgr.html) Arbitrary string associated with node during life of the instance.
InstanceId =< OPT >[#OPT_InstanceId](https://slurm.schedmd.com/sacctmgr.html) Cloud instance ID.
InstanceType =< OPT >[#OPT_InstanceType](https://slurm.schedmd.com/sacctmgr.html) Cloud instance type.
Nodes =< node_name >[,< node_name >,...][#OPT_Nodes_1](https://slurm.schedmd.com/sacctmgr.html) The node on which the instance ran.
Start =< OPT >[#OPT_Start_2](https://slurm.schedmd.com/sacctmgr.html) Period start of instances. Default is 00:00:00 of previous day.
Valid time formats are:
HH:MM[:SS] [AM|PM]
MMDD[YY] or MM/DD[/YY] or MM.DD[.YY]
MM/DD[/YY]-HH:MM[:SS]
YYYY-MM-DD[THH:MM[:SS]]
now[{+|-} count [seconds(default)|minutes|hours|days|weeks]]
## LIST/SHOW INSTANCE FORMAT OPTIONS[#SECTION_LIST/SHOW-INSTANCE-FORMAT-OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
Fields you can display when viewing Instance records by using the format=
option. The default format is:
Cluster,NodeName,Start,End,InstanceID,InstanceType,Extra
Cluster [#OPT_Cluster_5](https://slurm.schedmd.com/sacctmgr.html) Name of the cluster that the instance ran on.
End [#OPT_End_3](https://slurm.schedmd.com/sacctmgr.html) Time when instance ended.
Extra [#OPT_Extra_1](https://slurm.schedmd.com/sacctmgr.html) Arbitrary string associated with node during life of the instance.
InstanceId [#OPT_InstanceId_1](https://slurm.schedmd.com/sacctmgr.html) Cloud instance ID.
InstanceType [#OPT_InstanceType_1](https://slurm.schedmd.com/sacctmgr.html) Cloud instance type.
NodeName [#OPT_NodeName_1](https://slurm.schedmd.com/sacctmgr.html) The node on which the instance ran.
Start [#OPT_Start_3](https://slurm.schedmd.com/sacctmgr.html) Time when instance started.
## SPECIFICATIONS FOR JOB[#SECTION_SPECIFICATIONS-FOR-JOB](https://slurm.schedmd.com/sacctmgr.html)
Job information is automatically sent to slurmdbd to be stored.
These are options you can specify to filter for specific jobs. There are also
some attributes you can modify for a job record.
AdminComment =< admin_comment >[#OPT_AdminComment](https://slurm.schedmd.com/sacctmgr.html) Arbitrary descriptive string. Can only be modified by a Slurm administrator.
To clear an existing value, set a new value of '' (two single quotes with
nothing between them).
Comment =< comment >[#OPT_Comment](https://slurm.schedmd.com/sacctmgr.html) The job's comment string when the AccountingStoreFlags parameter
in the slurm.conf file contains 'job_comment'. The user can only
modify the comment string of their own job.
To clear an existing value, set a new value of '' (two single quotes with
nothing between them).
Cluster =< cluster_list >[#OPT_Cluster_6](https://slurm.schedmd.com/sacctmgr.html) List of clusters to alter jobs on, defaults to local cluster.
DerivedExitCode =< derived_exit_code >[#OPT_DerivedExitCode](https://slurm.schedmd.com/sacctmgr.html) The derived exit code can be modified after a job completes based on
the user's judgment of whether the job succeeded or failed. The user
can only modify the derived exit code of their own job.
EndTime [#OPT_EndTime](https://slurm.schedmd.com/sacctmgr.html) Jobs must end before this time to be modified. Format output is,
YYYY-MM-DDTHH:MM:SS, unless changed through the SLURM_TIME_FORMAT environment
variable.
Extra =< extra >[#OPT_Extra_2](https://slurm.schedmd.com/sacctmgr.html) The job's extra string when the AccountingStoreFlags parameter in the slurm.conf
file contains 'job_extra'. The user can only modify the extra string of their
own job.
To clear an existing value, set a new value of '' (two single quotes with
nothing between them).
JobID =< jobid_list >[#OPT_JobID](https://slurm.schedmd.com/sacctmgr.html) The id of the job to change. Not needed if altering multiple jobs using wckey
specification.
NewWCKey =< new_wckey >[#OPT_NewWCKey](https://slurm.schedmd.com/sacctmgr.html) Use to rename a wckey on job(s) in the accounting database
StartTime [#OPT_StartTime](https://slurm.schedmd.com/sacctmgr.html) Jobs must start at or after this time to be modified in the same format as
EndTime .
SystemComment =< system_comment >[#OPT_SystemComment](https://slurm.schedmd.com/sacctmgr.html) Arbitrary descriptive string, usually managed by the BurstBufferPlugin.
Can only be modified by a Slurm administrator.
To clear an existing value, set a new value of '' (two single quotes
with nothing between them).
TRES =< tres_name=value >[#OPT_TRES_2](https://slurm.schedmd.com/sacctmgr.html) Use to set or modify a TRES on job(s) in the accounting database that have
already completed.
WARNING : This is permanent, the original value will be lost afterwards.
User =< user_list >[#OPT_User_3](https://slurm.schedmd.com/sacctmgr.html) Used to specify the jobs of users jobs to alter.
WCKey =< wckey_list >[#OPT_WCKey](https://slurm.schedmd.com/sacctmgr.html) Used to specify the wckeys to alter.
The AdminComment , Comment , DerivedExitCode , Extra ,
SystemComment , and WCKey fields are the only fields of a job record
in the database that can be modified after job completion.
## LIST/SHOW JOB FORMAT OPTIONS[#SECTION_LIST/SHOW-JOB-FORMAT-OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
The sacct command is the exclusive command to display job
records from the Slurm database.
## SPECIFICATIONS FOR QOS[#SECTION_SPECIFICATIONS-FOR-QOS](https://slurm.schedmd.com/sacctmgr.html)
A QOS can be created, modified, and deleted with sacctmgr. These
options allow you to set the corresponding attributes or filter on them
when querying for a QOS.
NOTE : The group limits (GrpJobs, GrpTRES, etc.) are tested when a job is
being considered for being allocated resources.
If starting a job would cause any of its group limit to be exceeded,
that job will not be considered for scheduling even if that job might preempt
other jobs which would release sufficient group resources for the pending
job to be initiated.
NOTE : All TRES options (GrpTRES, MaxTRES, etc.) can also use the same
"[+|-]=" syntax available for association-based entities.
Description [#OPT_Description_2](https://slurm.schedmd.com/sacctmgr.html) An arbitrary string describing a QOS. Can only be modified by a Slurm
administrator.
Flags [#OPT_Flags_4](https://slurm.schedmd.com/sacctmgr.html) Used by the slurmctld to override or enforce certain characteristics.
To add or remove individual flags, use the += or -= operators.
To clear all existing flags, set a new value of -1.
Valid options are
DenyOnLimit [#OPT_DenyOnLimit](https://slurm.schedmd.com/sacctmgr.html) If set, jobs using this QOS will be rejected at submission time if they do
not conform to the QOS 'Max' or 'Min' limits as stand-alone jobs.
Jobs that exceed these limits when other jobs are considered, but conform
to the limits when considered individually will not be rejected. Instead
they will pend until resources are available.
Group limits (e.g. GrpTRES ) will also be treated like 'Max' limits
(e.g. MaxTRESPerNode ) and jobs will be denied if they would violate
the limit as stand-alone jobs.
This currently only applies to QOS and Association limits.
EnforceUsageThreshold [#OPT_EnforceUsageThreshold](https://slurm.schedmd.com/sacctmgr.html) If set, and the QOS also has a UsageThreshold,
any jobs submitted with this QOS that fall below the UsageThreshold
will be held until their Fairshare Usage goes above the Threshold.
NoDecay [#OPT_NoDecay](https://slurm.schedmd.com/sacctmgr.html) If set, this QOS will not have its GrpTRESMins,
GrpWall and UsageRaw decayed by the slurm.conf PriorityDecayHalfLife or
PriorityUsageResetPeriod settings. This allows a QOS to provide aggregate
limits that, once consumed, will not be replenished automatically. Such a
QOS will act as a time-limited quota of resources for an association
that has access to it. Account/user usage will still be decayed for
associations using the QOS. The QOS GrpTRESMins and
GrpWall limits can be increased or the QOS RawUsage value reset to 0
(zero) to again allow jobs submitted with this QOS to be queued (if
DenyOnLimit is set) or run (pending with QOSGrp{TRES}MinutesLimit
or QOSGrpWallLimit reasons, where {TRES} is some type of trackable resource).
NoReserve [#OPT_NoReserve](https://slurm.schedmd.com/sacctmgr.html) If set and backfill scheduling is used, jobs using this QOS will
not reserve resources in the backfill schedule's map of resources allocated
through time. This flag is intended for use with a QOS that may be preempted
by jobs associated with all other QOS (e.g use with a "standby" QOS). If this
flag is used with a QOS which can not be preempted by all other QOS, it could
result in starvation of larger jobs.
OverPartQOS [#OPT_OverPartQOS](https://slurm.schedmd.com/sacctmgr.html) If set, jobs using this QOS will be able to
override any limits used by the requested partition's QOS limits.
PartitionMaxNodes [#OPT_PartitionMaxNodes](https://slurm.schedmd.com/sacctmgr.html) If set, jobs using this QOS will be able to
override the requested partition's MaxNodes limit.
PartitionMinNodes [#OPT_PartitionMinNodes](https://slurm.schedmd.com/sacctmgr.html) If set, jobs using this QOS will be able to
override the requested partition's MinNodes limit.
PartitionTimeLimit [#OPT_PartitionTimeLimit](https://slurm.schedmd.com/sacctmgr.html) If set, jobs using this QOS will be able to
override the requested partition's TimeLimit.
Relative [#OPT_Relative](https://slurm.schedmd.com/sacctmgr.html) If set, the QOS limits will be treated as percentages of the cluster or
partition instead of absolute limits (numbers should be less than 100).
The controller should be restarted or
reconfigured after adding the Relative flag to the QOS.
If this is used as a partition QOS:
1. Limits will be calculated relative to the partition's resources.
2. Only one partition may have this QOS as its partition QOS.
3. Jobs will not be allowed to use it as a normal QOS.
Additional details are in the QOS documentation at
<[https://slurm.schedmd.com/qos.html](https://slurm.schedmd.com/qos.html)>.
RequiresReservation [#OPT_RequiresReservation](https://slurm.schedmd.com/sacctmgr.html) If set, jobs using this QOS must designate a reservation when submitting a job.
This option can be useful in restricting usage of a QOS that may have greater
preemptive capability or additional resources to be allowed only within a
reservation.
UsageFactorSafe [#OPT_UsageFactorSafe](https://slurm.schedmd.com/sacctmgr.html) If set and AccountingStorageEnforce includes Safe , jobs will only
be able to run if the job can run to completion with the UsageFactor
applied.
GraceTime [#OPT_GraceTime](https://slurm.schedmd.com/sacctmgr.html) Preemption grace time in seconds to be extended to a job which has been
selected for preemption. The default value is zero, meaning no preemption grace
time is allowed on this QOS. This value is only applicable for QOS
PreemptMode=CANCEL and PreemptMode=REQUEUE .
GrpJobs [#OPT_GrpJobs_2](https://slurm.schedmd.com/sacctmgr.html) Maximum number of running jobs in aggregate for this QOS.
To clear an existing value, set a new value of -1.
GrpJobsAccrue [#OPT_GrpJobsAccrue_2](https://slurm.schedmd.com/sacctmgr.html) Maximum number of pending jobs in aggregate able to accrue age priority for this
QOS.
This limit only applies to the job's QOS and not the partition's QOS.
To clear an existing value, set a new value of -1.
GrpSubmit [#OPT_GrpSubmit_2](https://slurm.schedmd.com/sacctmgr.html)
GrpSubmitJobs [#OPT_GrpSubmitJobs_2](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of jobs in a pending or running state at any time in aggregate
for this QOS.
To clear an existing value, set a new value of -1.
GrpTRES [#OPT_GrpTRES_2](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES able to be allocated by running jobs in aggregate for
this QOS.
Refer to the TRES information section below for further details.
GrpTRESMins [#OPT_GrpTRESMins_2](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES minutes that can possibly be used by past, present, and
future jobs with this QOS.
Refer to the TRES information section below for further details.
NOTE : This limit only applies when using the Priority Multifactor
plugin. The time is decayed using the value of PriorityDecayHalfLife
or PriorityUsageResetPeriod as set in the slurm.conf. When this limit
is reached all associated jobs running will be killed and all future jobs
submitted with this QOS will be delayed until they are able to run
inside the limit.
GrpTRESRunMins [#OPT_GrpTRESRunMins_2](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES minutes able to be allocated by running jobs with this
QOS. This takes into consideration time limit of running jobs and consumes it.
If the limit is reached no new jobs are started until other jobs finish to allow
time to free up.
Refer to the TRES information section below for further details.
GrpWall [#OPT_GrpWall_2](https://slurm.schedmd.com/sacctmgr.html) Maximum wall clock time able to be allocated by running jobs in aggregate for
this QOS. If this limit is reached, job submissions will be
denied and the running jobs will be killed.
GrpWall format is <min> or <min>:<sec> or <hr>:<min>:<sec> or
<days>-<hr>:<min>:<sec> or <days>-<hr>.
The value is recorded in minutes with rounding as needed.
To clear an existing value, set a new value of -1.
NOTE : This limit only applies when using the Priority Multifactor
plugin. The time is decayed using the value of PriorityDecayHalfLife
or PriorityUsageResetPeriod as set in the slurm.conf. When this limit
is reached all associated jobs running will be killed and all future jobs
submitted with this QOS will be delayed until they are able to run
inside the limit.
LimitFactor [#OPT_LimitFactor](https://slurm.schedmd.com/sacctmgr.html) A float that is factored into an association's [Grp|Max]TRES limits. For
example, if the LimitFactor is 2, then an association with a GrpTRES of
30 CPUs, would be allowed to allocate 60 CPUs when running under this QOS.
To clear an existing value, set a new value of -1.
NOTE : This factor is only applied to associations running in this QOS
and is not applied to any limits in the QOS itself.
MaxJobsAccruePA [#OPT_MaxJobsAccruePA](https://slurm.schedmd.com/sacctmgr.html)
MaxJobsAccruePerAccount [#OPT_MaxJobsAccruePerAccount](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of pending jobs an account (or subacct) can have accruing age
priority at any given time.
This limit only applies to the job's QOS and not the partition's QOS.
To clear an existing value, set a new value of -1.
MaxJobsAccruePU [#OPT_MaxJobsAccruePU](https://slurm.schedmd.com/sacctmgr.html)
MaxJobsAccruePerUser [#OPT_MaxJobsAccruePerUser](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of pending jobs a user can have accruing age priority at any
given time.
This limit only applies to the job's QOS and not the partition's QOS.
To clear an existing value, set a new value of -1.
MaxJobsPA [#OPT_MaxJobsPA](https://slurm.schedmd.com/sacctmgr.html)
MaxJobsPerAccount [#OPT_MaxJobsPerAccount](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of running jobs per account.
To clear an existing value, set a new value of -1.
MaxJobsPU [#OPT_MaxJobsPU](https://slurm.schedmd.com/sacctmgr.html)
MaxJobsPerUser [#OPT_MaxJobsPerUser](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of running jobs per user.
To clear an existing value, set a new value of -1.
MaxSubmitJobsPA [#OPT_MaxSubmitJobsPA](https://slurm.schedmd.com/sacctmgr.html)
MaxSubmitJobsPerAccount [#OPT_MaxSubmitJobsPerAccount](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of jobs in a pending or running state per account.
To clear an existing value, set a new value of -1.
MaxSubmitJobsPU [#OPT_MaxSubmitJobsPU](https://slurm.schedmd.com/sacctmgr.html)
MaxSubmitJobsPerUser [#OPT_MaxSubmitJobsPerUser](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of jobs in a pending or running state per user.
To clear an existing value, set a new value of -1.
MaxTRES [#OPT_MaxTRES_2](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPJ [#OPT_MaxTRESPJ_2](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPerJob [#OPT_MaxTRESPerJob_2](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES each job can use.
Refer to the TRES information section below for further details.
MaxTRESMins [#OPT_MaxTRESMins_2](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESMinsPJ [#OPT_MaxTRESMinsPJ_2](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESMinsPerJob [#OPT_MaxTRESMinsPerJob_2](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES minutes each job can use.
Refer to the TRES information section below for further details.
MaxTRESPA [#OPT_MaxTRESPA](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPerAccount [#OPT_MaxTRESPerAccount](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES each account can use.
Refer to the TRES information section below for further details.
MaxTRESPN [#OPT_MaxTRESPN_2](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPerNode [#OPT_MaxTRESPerNode_2](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES each node in a job allocation can use.
Refer to the TRES information section below for further details.
MaxTRESPU [#OPT_MaxTRESPU](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPerUser [#OPT_MaxTRESPerUser](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES each user can use.
Refer to the TRES information section below for further details.
MaxTRESRunMinsPA [#OPT_MaxTRESRunMinsPA](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESRunMinsPerAccount [#OPT_MaxTRESRunMinsPerAccount](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES minutes each account can use. This takes into
consideration the time limit of running jobs. If the limit is reached, no new
jobs are started until other jobs finish to allow time to free up.
Refer to the TRES information section below for further details.
MaxTRESRunMinsPU [#OPT_MaxTRESRunMinsPU](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESRunMinsPerUser [#OPT_MaxTRESRunMinsPerUser](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES minutes each user can use. This takes into
consideration the time limit of running jobs. If the limit is reached, no new
jobs are started until other jobs finish to allow time to free up.
Refer to the TRES information section below for further details.
MaxWall [#OPT_MaxWall_2](https://slurm.schedmd.com/sacctmgr.html)
MaxWallDurationPerJob [#OPT_MaxWallDurationPerJob_2](https://slurm.schedmd.com/sacctmgr.html)
Maximum wall clock time each job can use. MaxWall format is <min> or
<min>:<sec> or <hr>:<min>:<sec> or <days>-<hr>:<min>:<sec> or <days>-<hr>.
The value is recorded in minutes with rounding as needed.
To clear an existing value, set a new value of -1.
MinPrioThreshold [#OPT_MinPrioThreshold](https://slurm.schedmd.com/sacctmgr.html) Minimum priority required to reserve resources when scheduling.
To clear an existing value, set a new value of -1.
MinTRES [#OPT_MinTRES](https://slurm.schedmd.com/sacctmgr.html)
MinTRESPerJob [#OPT_MinTRESPerJob](https://slurm.schedmd.com/sacctmgr.html)
Minimum number of TRES each job running under this QOS must request.
Otherwise the job will pend until modified.
Refer to the TRES information section below for further details.
Name [#OPT_Name_3](https://slurm.schedmd.com/sacctmgr.html) Name of the QOS. Needed for creation.
Preempt [#OPT_Preempt](https://slurm.schedmd.com/sacctmgr.html) Other QOSs this QOS can preempt.
To clear an existing value, set a new value of '' (two single quotes with
nothing between them).
NOTE : The Priority of a QOS is NOT related to QOS preemption, only
Preempt is used to define which QOS can preempt others.
PreemptExemptTime [#OPT_PreemptExemptTime](https://slurm.schedmd.com/sacctmgr.html) Specifies a minimum run time for jobs in this QOS before they are considered for
preemption. This QOS option takes precedence over the global
PreemptExemptTime . This is only honored for PreemptMode=REQUEUE
and PreemptMode=CANCEL .
Setting to -1 disables the option, allowing another
QOS or the global option to take effect. Setting to 0 indicates no minimum run
time and supersedes the lower priority QOS (see OverPartQOS ) and/or the
global option in slurm.conf.
PreemptMode [#OPT_PreemptMode](https://slurm.schedmd.com/sacctmgr.html) Mechanism used to preempt jobs or enable gang scheduling for this QOS
when the cluster's PreemptType is set to preempt/qos .
This QOS-specific PreemptMode will override the cluster-wide
PreemptMode for this QOS. Unsetting the QOS specific PreemptMode ,
by specifying "OFF", "" or "Cluster", makes it use the default cluster-wide
PreemptMode .
The GANG option is used to enable gang scheduling independent of
whether preemption is enabled (i.e. independent of the PreemptType
setting). It can be specified in addition to a PreemptMode setting with
the two options comma-separated (e.g. PreemptMode=SUSPEND,GANG ).
See <[preempt](https://slurm.schedmd.com/preempt.html)> and
<[gang_scheduling](https://slurm.schedmd.com/gang_scheduling.html)> for more details.
NOTE :
For performance reasons, the backfill scheduler reserves whole nodes for jobs,
not partial nodes. If during backfill scheduling a job preempts one or more
other jobs, the whole nodes for those preempted jobs are reserved for the
preemptor job, even if the preemptor job requested fewer resources than that.
These reserved nodes aren't available to other jobs during that backfill
cycle, even if the other jobs could fit on the nodes. Therefore, jobs may
preempt more resources during a single backfill iteration than they requested.
NOTE :
For heterogeneous job to be considered for preemption all components
must be eligible for preemption. When a heterogeneous job is to be preempted
the first identified component of the job with the highest order PreemptMode
( SUSPEND (highest), REQUEUE , CANCEL (lowest)) will be
used to set the PreemptMode for all components. The GraceTime and user
warning signal for each component of the heterogeneous job remain unique.
Heterogeneous jobs are excluded from GANG scheduling operations.
OFF [#OPT_OFF](https://slurm.schedmd.com/sacctmgr.html) Is the default value and disables job preemption and gang scheduling.
It is only compatible with PreemptType=preempt/none at a global level.
CANCEL [#OPT_CANCEL](https://slurm.schedmd.com/sacctmgr.html) The preempted job will be cancelled.
GANG [#OPT_GANG](https://slurm.schedmd.com/sacctmgr.html) Enables gang scheduling (time slicing) of jobs in the same partition, and
allows the resuming of suspended jobs.
Configure the OverSubscribe setting to FORCE for all partitions
in which time-slicing is to take place.
Gang scheduling is performed independently for each partition, so
if you only want time-slicing by OverSubscribe , without any preemption,
then configuring partitions with overlapping nodes is not recommended.
Time-slicing won't happen between jobs on different partitions.
NOTE :
Heterogeneous jobs are excluded from GANG scheduling operations.
REQUEUE [#OPT_REQUEUE](https://slurm.schedmd.com/sacctmgr.html) Preempts jobs by requeuing them (if possible) or canceling them.
For jobs to be requeued they must have the --requeue sbatch option set
or the cluster wide JobRequeue parameter in slurm.conf must be set to 1 .
SUSPEND [#OPT_SUSPEND](https://slurm.schedmd.com/sacctmgr.html) The preempted jobs will be suspended, and later the Gang scheduler will resume
them. Therefore the SUSPEND preemption mode always needs the GANG
option to be specified at the cluster level. Also, because the suspended jobs
will still use memory on the allocated nodes, Slurm needs to be able to track
memory resources to be able to suspend jobs.
If PreemptType=preempt/qos is configured and if the preempted job(s) and
the preemptor job are on the same partition, then they will share resources with
the Gang scheduler (time-slicing). If not (i.e. if the preemptees and preemptor
are on different partitions) then the preempted jobs will remain suspended until
the preemptor ends.
NOTE : Suspended jobs will not release GRES. Higher priority jobs will not
be able to preempt to gain access to GRES.
WITHIN [#OPT_WITHIN](https://slurm.schedmd.com/sacctmgr.html) Allows for preemption between jobs sharing the same qos. By default,
PreemptType=preempt/qos will only consider jobs to be eligible for
preemption if they do not share the same qos value.
Priority [#OPT_Priority_2](https://slurm.schedmd.com/sacctmgr.html) QOS priority factor to be used by the priority/multifactor plugin.
Unset by default, indicating that no extra priority is granted.
NOTE : The Priority of a QOS is NOT related to QOS preemption, see
Preempt instead.
RawUsage =< value >[#OPT_RawUsage_1](https://slurm.schedmd.com/sacctmgr.html) This allows an administrator to set the raw usage accrued to a QOS. Specifying
a value of 0 (zero) will reset the raw usage. This is a settable specification
only - it cannot be used as a filter to list accounts.
UsageFactor [#OPT_UsageFactor](https://slurm.schedmd.com/sacctmgr.html) A float that is factored into a job's TRES usage (e.g. RawUsage, TRESMins,
TRESRunMins). For example, if the usagefactor was 2, for every TRESBillingUnit
second a job ran it would count for 2. If the usagefactor was .5, every second
would only count for half of the time. A setting of 0 would add no timed usage
from the job.
The usage factor only applies to the job's QOS and not the partition QOS.
If the UsageFactorSafe flag is set and
AccountingStorageEnforce includes Safe , jobs will only be started if
they can run to completion with the UsageFactor applied, and won't be
killed due to limits.
If the UsageFactorSafe flag is not set and
AccountingStorageEnforce includes Safe , jobs will be started if
they can run to completion without the UsageFactor applied,
and won't be killed due to limits.
If the UsageFactorSafe flag is not set and
AccountingStorageEnforce does not include Safe , jobs will be
scheduled as long as the limits are not reached, but could be killed due to
limits.
See AccountingStorageEnforce in slurm.conf man page.
Default is 1. To clear an existing value, set a new value of -1.
UsageThreshold [#OPT_UsageThreshold](https://slurm.schedmd.com/sacctmgr.html) A float representing the lowest fairshare of an association allowed
to run a job. If an association falls below this threshold and has
pending jobs or submits new jobs those jobs will be held until the
usage goes back above the threshold. Use sshare to see current
shares on the system.
To clear an existing value, set a new value of -1.
## LIST/SHOW QOS FORMAT OPTIONS[#SECTION_LIST/SHOW-QOS-FORMAT-OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
Fields you can display when viewing QOS records by using the format=
option.
Description [#OPT_Description_3](https://slurm.schedmd.com/sacctmgr.html) An arbitrary string describing a QOS.
Flags [#OPT_Flags_5](https://slurm.schedmd.com/sacctmgr.html) Used by the slurmctld to override or enforce certain characteristics.
GraceTime [#OPT_GraceTime_1](https://slurm.schedmd.com/sacctmgr.html) Preemption grace time to be extended to a job which has been
selected for preemption in the format of hh:mm:ss.
GrpJobs [#OPT_GrpJobs_3](https://slurm.schedmd.com/sacctmgr.html) Maximum number of running jobs in aggregate for this QOS.
GrpJobsAccrue [#OPT_GrpJobsAccrue_3](https://slurm.schedmd.com/sacctmgr.html) Maximum number of pending jobs in aggregate able to accrue age priority for this
QOS.
This limit only applies to the job's QOS and not the partition's QOS.
GrpSubmit [#OPT_GrpSubmit_3](https://slurm.schedmd.com/sacctmgr.html)
GrpSubmitJobs [#OPT_GrpSubmitJobs_3](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of jobs in a pending or running state at any time in aggregate
for this QOS.
GrpTRES [#OPT_GrpTRES_3](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES able to be allocated by running jobs in aggregate for
this QOS.
GrpTRESMins [#OPT_GrpTRESMins_3](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES minutes that can possibly be used by past, present, and
future jobs with this QOS.
GrpTRESRunMins [#OPT_GrpTRESRunMins_3](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES minutes able to be allocated by running jobs with this
QOS.
GrpWall [#OPT_GrpWall_3](https://slurm.schedmd.com/sacctmgr.html) Maximum wall clock time able to be allocated by running jobs in aggregate for
this QOS.
ID [#OPT_ID_2](https://slurm.schedmd.com/sacctmgr.html) The id of the QOS.
LimitFactor [#OPT_LimitFactor_1](https://slurm.schedmd.com/sacctmgr.html) A float that is factored into an association's [Grp|Max]TRES limits.
MaxJobsAccruePA [#OPT_MaxJobsAccruePA_1](https://slurm.schedmd.com/sacctmgr.html)
MaxJobsAccruePerAccount [#OPT_MaxJobsAccruePerAccount_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of pending jobs an account (or subacct) can have accruing age
priority at any given time. This limit only applies to the job's QOS and not the
partition's QOS.
MaxJobsAccruePU [#OPT_MaxJobsAccruePU_1](https://slurm.schedmd.com/sacctmgr.html)
MaxJobsAccruePerUser [#OPT_MaxJobsAccruePerUser_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of pending jobs a user can have accruing age priority at any
given time. This limit only applies to the job's QOS and not the partition's
QOS.
MaxJobsPA [#OPT_MaxJobsPA_1](https://slurm.schedmd.com/sacctmgr.html)
MaxJobsPerAccount [#OPT_MaxJobsPerAccount_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of running jobs per account.
MaxJobsPU [#OPT_MaxJobsPU_1](https://slurm.schedmd.com/sacctmgr.html)
MaxJobsPerUser [#OPT_MaxJobsPerUser_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of running jobs per user.
MaxSubmitJobsPA [#OPT_MaxSubmitJobsPA_1](https://slurm.schedmd.com/sacctmgr.html)
MaxSubmitJobsPerAccount [#OPT_MaxSubmitJobsPerAccount_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of jobs in a pending or running state per account.
MaxSubmitJobsPU [#OPT_MaxSubmitJobsPU_1](https://slurm.schedmd.com/sacctmgr.html)
MaxSubmitJobsPerUser [#OPT_MaxSubmitJobsPerUser_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of jobs in a pending or running state per user.
MaxTRES [#OPT_MaxTRES_3](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPJ [#OPT_MaxTRESPJ_3](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPerJob [#OPT_MaxTRESPerJob_3](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES each job can use.
MaxTRESMins [#OPT_MaxTRESMins_3](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESMinsPJ [#OPT_MaxTRESMinsPJ_3](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESMinsPerJob [#OPT_MaxTRESMinsPerJob_3](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES minutes each job can use.
MaxTRESPA [#OPT_MaxTRESPA_1](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPerAccount [#OPT_MaxTRESPerAccount_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES each account can use.
MaxTRESPN [#OPT_MaxTRESPN_3](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPerNode [#OPT_MaxTRESPerNode_3](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES each node in a job allocation can use.
MaxTRESPU [#OPT_MaxTRESPU_1](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESPerUser [#OPT_MaxTRESPerUser_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES each user can use.
MaxTRESRunMinsPA [#OPT_MaxTRESRunMinsPA_1](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESRunMinsPerAccount [#OPT_MaxTRESRunMinsPerAccount_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES minutes each account can use.
MaxTRESRunMinsPU [#OPT_MaxTRESRunMinsPU_1](https://slurm.schedmd.com/sacctmgr.html)
MaxTRESRunMinsPerUser [#OPT_MaxTRESRunMinsPerUser_1](https://slurm.schedmd.com/sacctmgr.html)
Maximum number of TRES minutes each user can use.
MaxWall [#OPT_MaxWall_3](https://slurm.schedmd.com/sacctmgr.html)
MaxWallDurationPerJob [#OPT_MaxWallDurationPerJob_3](https://slurm.schedmd.com/sacctmgr.html)
Maximum wall clock time each job can use.
MinPrioThreshold [#OPT_MinPrioThreshold_1](https://slurm.schedmd.com/sacctmgr.html) Minimum priority required to reserve resources when scheduling.
MinTRES [#OPT_MinTRES_1](https://slurm.schedmd.com/sacctmgr.html) Minimum number of TRES each job running under this QOS must request.
Otherwise the job will pend until modified.
Name [#OPT_Name_4](https://slurm.schedmd.com/sacctmgr.html) Name of the QOS.
Preempt [#OPT_Preempt_1](https://slurm.schedmd.com/sacctmgr.html) Other QOSs this QOS can preempt.
PreemptExemptTime [#OPT_PreemptExemptTime_1](https://slurm.schedmd.com/sacctmgr.html) Specifies a minimum run time for jobs in this QOS before they are considered for
preemption.
PreemptMode [#OPT_PreemptMode_1](https://slurm.schedmd.com/sacctmgr.html) Mechanism used to preempt jobs or enable gang scheduling for this QOS
when the cluster's PreemptType is set to preempt/qos .
The default preemption mechanism is specified by the cluster-wide
PreemptMode configuration parameter.
Priority [#OPT_Priority_3](https://slurm.schedmd.com/sacctmgr.html) QOS priority factor to be used by the priority/multifactor plugin.
UsageFactor [#OPT_UsageFactor_1](https://slurm.schedmd.com/sacctmgr.html) A float that is factored into a job's TRES usage (e.g. RawUsage, TRESMins,
TRESRunMins).
UsageThreshold [#OPT_UsageThreshold_1](https://slurm.schedmd.com/sacctmgr.html) A float representing the lowest fairshare of an association allowed
to run a job.
WithDeleted [#OPT_WithDeleted_4](https://slurm.schedmd.com/sacctmgr.html) Display information with previously deleted data.
A QOS that is deleted within 24 hours of being created and did not have
a job run in the QOS during that time will be removed from the database.
Otherwise, the QOS will be marked as deleted and will be viewable with
the WithDeleted flag.
## SPECIFICATIONS FOR RESERVATIONS[#SECTION_SPECIFICATIONS-FOR-RESERVATIONS](https://slurm.schedmd.com/sacctmgr.html)
Reservations are created with the scontrol command and information about the
reservations is sent to slurmdbd to be stored.
These are options you can specify to filter for specific reservations.
Clusters =< cluster_name >[,< cluster_name >,...][#OPT_Clusters_4](https://slurm.schedmd.com/sacctmgr.html) List the reservations of the cluster(s). Default is the cluster where the
command was run.
End =< OPT >[#OPT_End_4](https://slurm.schedmd.com/sacctmgr.html) Period ending of reservations. Default is now.
Valid time formats are:
HH:MM[:SS] [AM|PM]
MMDD[YY] or MM/DD[/YY] or MM.DD[.YY]
MM/DD[/YY]-HH:MM[:SS]
YYYY-MM-DD[THH:MM[:SS]]
now[{+|-} count [seconds(default)|minutes|hours|days|weeks]]
ID =< OPT >[#OPT_ID_3](https://slurm.schedmd.com/sacctmgr.html) Comma-separated list of reservation ids.
Names =< OPT >[#OPT_Names_1](https://slurm.schedmd.com/sacctmgr.html) Comma-separated list of reservation names.
Nodes =< node_name >[,< node_name >,...][#OPT_Nodes_2](https://slurm.schedmd.com/sacctmgr.html) Node names where reservation ran.
Start =< OPT >[#OPT_Start_4](https://slurm.schedmd.com/sacctmgr.html) Period start of reservations. Default is 00:00:00 of previous day.
Valid time formats are:
HH:MM[:SS] [AM|PM]
MMDD[YY] or MM/DD[/YY] or MM.DD[.YY]
MM/DD[/YY]-HH:MM[:SS]
YYYY-MM-DD[THH:MM[:SS]]
now[{+|-} count [seconds(default)|minutes|hours|days|weeks]]
## LIST/SHOW RESERVATION FORMAT OPTIONS[#SECTION_LIST/SHOW-RESERVATION-FORMAT-OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
Fields you can display when viewing Reservation records by using the
format= option. The default format is:
Cluster,Name,TRES,Start,End,UnusedWall
Associations [#OPT_Associations](https://slurm.schedmd.com/sacctmgr.html) The id's of the associations able to run in the reservation.
Cluster [#OPT_Cluster_7](https://slurm.schedmd.com/sacctmgr.html) Name of cluster reservation was on.
End [#OPT_End_5](https://slurm.schedmd.com/sacctmgr.html) End time of reservation.
Flags [#OPT_Flags_6](https://slurm.schedmd.com/sacctmgr.html) Flags set on the reservation.
ID [#OPT_ID_4](https://slurm.schedmd.com/sacctmgr.html) Reservation ID.
Name [#OPT_Name_5](https://slurm.schedmd.com/sacctmgr.html) Name of this reservation.
NodeNames [#OPT_NodeNames_1](https://slurm.schedmd.com/sacctmgr.html) List of nodes in the reservation.
Start [#OPT_Start_5](https://slurm.schedmd.com/sacctmgr.html) Start time of reservation.
TRES [#OPT_TRES_3](https://slurm.schedmd.com/sacctmgr.html) List of TRES in the reservation.
UnusedWall [#OPT_UnusedWall](https://slurm.schedmd.com/sacctmgr.html) Wall clock time in seconds unused by any job. A job's allocated usage is its
run time multiplied by the ratio of its CPUs to the total number of CPUs in the
reservation. For example, a job using all the CPUs in the reservation running
for 1 minute would reduce unused_wall by 1 minute.
## SPECIFICATIONS FOR RESOURCE[#SECTION_SPECIFICATIONS-FOR-RESOURCE](https://slurm.schedmd.com/sacctmgr.html)
Resources can be created, modified, and deleted with sacctmgr. These
options allow you to set the corresponding attributes or filter on them
when querying for Resources.
LastConsumed =< OPT >[#OPT_LastConsumed](https://slurm.schedmd.com/sacctmgr.html) Number of software resources of a specific name consumed out of Count on
the system being controlled by a resource manager.
Clusters =< name_list >[#OPT_Clusters_5](https://slurm.schedmd.com/sacctmgr.html) Comma-separated list of cluster names on which specified resources are to be
available. If no names are designated then the clusters already
allowed to use this resource will be altered.
Count =< OPT >[#OPT_Count](https://slurm.schedmd.com/sacctmgr.html) Number of software resources of a specific name configured on the system being
controlled by a resource manager.
Descriptions =[#OPT_Descriptions](https://slurm.schedmd.com/sacctmgr.html) A brief description of the resource.
Flags [-|+]=< OPT >[#OPT_Flags_7](https://slurm.schedmd.com/sacctmgr.html) Flags that identify specific attributes of the system resource.
Valid options are
Absolute [#OPT_Absolute](https://slurm.schedmd.com/sacctmgr.html) If set the resource will treat the counts for Allowed and Allocated
as absolute counts instead of percentages.
NOTE : If removing this with flags-=absolute there is no effort to convert
the numbers in the database back to percentages. This is required by the user.
Names =< OPT >[#OPT_Names_2](https://slurm.schedmd.com/sacctmgr.html) Comma-separated list of the name of a resource configured on the
system being controlled by a resource manager. If this resource is
seen on the slurmctld its name will be [name@server](mailto:name@server) to distinguish it
from local resources defined in a slurm.conf.
Allowed =< allowed >[#OPT_Allowed](https://slurm.schedmd.com/sacctmgr.html) Percentage/Count of a specific resource that can be used on specified cluster.
Server =< OPT >[#OPT_Server](https://slurm.schedmd.com/sacctmgr.html) Arbitrary string indicating the name of the server serving up the resource.
Default is 'slurmdb' indicating the licenses are being served by the database.
This parameter is only for tagging purposes.
ServerType =< OPT >[#OPT_ServerType](https://slurm.schedmd.com/sacctmgr.html) Arbitrary string used to tag the type of the software resource manager
providing the licenses. For example FlexNext Publisher Flexlm license server
or Reprise License Manager RLM. This does not imply any kind of integration
with license managers.
Type =< OPT >[#OPT_Type](https://slurm.schedmd.com/sacctmgr.html) The type of the resource represented by this record. Currently the only valid
type is License.
WithClusters [#OPT_WithClusters](https://slurm.schedmd.com/sacctmgr.html) Display the clusters percentage/count of resources. If a resource hasn't
been given to a cluster the resource will not be displayed with this flag.
WithDeleted [#OPT_WithDeleted_5](https://slurm.schedmd.com/sacctmgr.html) Display information with previously deleted data.
Resources that are deleted within 24 hours of being created will be removed
from the database. Resources that were created more than 24 hours prior to
the deletion request are just marked as deleted and will be viewable with
the WithDeleted flag.
NOTE : Resource is used to define each resource configured on a system
available for usage by Slurm clusters.
## LIST/SHOW RESOURCE FORMAT OPTIONS[#SECTION_LIST/SHOW-RESOURCE-FORMAT-OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
Fields you can display when viewing Resource records by using the
format= option. The default format is:
Name,Server,Type,Count,LastConsumed,Allocated,ServerType,Flags
Allocated [#OPT_Allocated](https://slurm.schedmd.com/sacctmgr.html) The percent/count of licenses allocated to a cluster.
LastConsumed [#OPT_LastConsumed_1](https://slurm.schedmd.com/sacctmgr.html) The count of a specific resource consumed out of Count on the system
globally.
Cluster [#OPT_Cluster_8](https://slurm.schedmd.com/sacctmgr.html) Name of cluster resource is given to.
Count [#OPT_Count_1](https://slurm.schedmd.com/sacctmgr.html) The count of a specific resource configured on the system globally.
Description [#OPT_Description_4](https://slurm.schedmd.com/sacctmgr.html) Description of the resource.
Name [#OPT_Name_6](https://slurm.schedmd.com/sacctmgr.html) Name of this resource.
Server [#OPT_Server_1](https://slurm.schedmd.com/sacctmgr.html) Server serving up the resource.
ServerType [#OPT_ServerType_1](https://slurm.schedmd.com/sacctmgr.html) The type of the server controlling the licenses.
Type [#OPT_Type_1](https://slurm.schedmd.com/sacctmgr.html) Type of resource this record represents.
## SPECIFICATIONS FOR RUNAWAYJOB[#SECTION_SPECIFICATIONS-FOR-RUNAWAYJOB](https://slurm.schedmd.com/sacctmgr.html)
Under certain circumstances, jobs can complete without having that completion
recorded by slurmdbd. This results in a "runaway job", where slurmdbd is not
going to record a completion time for that job without intervention.
This command will identify jobs that are in this state and offer to have
slurmdbd clean up the job record(s).
This particular variant of the "show" command also permits the use of the
"set" keyword to define the following specifications:
EndState =< state >[#OPT_EndState](https://slurm.schedmd.com/sacctmgr.html) Desired state to use as the end state for fixed jobs. Supported states are:
Completed, Failed.
## LIST/SHOW RUNAWAYJOB FORMAT OPTIONS[#SECTION_LIST/SHOW-RUNAWAYJOB-FORMAT-OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
Fields you can display when viewing runaway job records by using the
format= option. The default format is:
ID,Name,Partition,Cluster,State,TimeSubmit,TimeStart,TimeEnd
Cluster [#OPT_Cluster_9](https://slurm.schedmd.com/sacctmgr.html) Name of cluster job ran on.
ID [#OPT_ID_5](https://slurm.schedmd.com/sacctmgr.html) Id of the job.
Name [#OPT_Name_7](https://slurm.schedmd.com/sacctmgr.html) Name of the job.
Partition [#OPT_Partition_1](https://slurm.schedmd.com/sacctmgr.html) Partition job ran on.
State [#OPT_State_1](https://slurm.schedmd.com/sacctmgr.html) Current State of the job in the database.
TimeEnd [#OPT_TimeEnd](https://slurm.schedmd.com/sacctmgr.html) Current recorded time of the end of the job.
TimeStart [#OPT_TimeStart](https://slurm.schedmd.com/sacctmgr.html) Time job started running.
TimeSubmit [#OPT_TimeSubmit](https://slurm.schedmd.com/sacctmgr.html) Time job was submitted.
## SPECIFICATIONS FOR TRANSACTIONS[#SECTION_SPECIFICATIONS-FOR-TRANSACTIONS](https://slurm.schedmd.com/sacctmgr.html)
Information about changes to clusters, resources, accounts, associations,
etc., are recorded as transactions by slurmdbd.
These are options you can specify to filter for specific transactions.
Accounts =< account_name >[,< account_name >,...][#OPT_Accounts_1](https://slurm.schedmd.com/sacctmgr.html) Only print out the transactions affecting specified accounts.
Action =< Specific_action_the_list_will_display >[#OPT_Action](https://slurm.schedmd.com/sacctmgr.html) Only display transactions of the specified action type.
Actor =< Specific_name_the_list_will_display >[#OPT_Actor](https://slurm.schedmd.com/sacctmgr.html) Only display transactions done by a certain person.
Clusters =< cluster_name >[,< cluster_name >,...][#OPT_Clusters_6](https://slurm.schedmd.com/sacctmgr.html) Only print out the transactions affecting specified clusters.
End =< Date_and_time_of_last_transaction_to_return >[#OPT_End_6](https://slurm.schedmd.com/sacctmgr.html) Return all transactions before this Date and time. Default is now.
Start =< Date_and_time_of_first_transaction_to_return >[#OPT_Start_6](https://slurm.schedmd.com/sacctmgr.html) Return all transactions after this Date and time. Default is epoch.
Valid time formats for End and Start are:
HH:MM[:SS] [AM|PM]
MMDD[YY] or MM/DD[/YY] or MM.DD[.YY]
MM/DD[/YY]-HH:MM[:SS]
YYYY-MM-DD[THH:MM[:SS]]
now[{+|-} count [seconds(default)|minutes|hours|days|weeks]]
Users =< user_name >[,< user_name >,...][#OPT_Users_1](https://slurm.schedmd.com/sacctmgr.html) Only print out the transactions affecting specified users.
WithAssoc [#OPT_WithAssoc_1](https://slurm.schedmd.com/sacctmgr.html) Get information about which associations were affected by the transactions.
## LIST/SHOW TRANSACTIONS FORMAT OPTIONS[#SECTION_LIST/SHOW-TRANSACTIONS-FORMAT-OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
Fields you can display when viewing Transaction records by using the
format= option. The default format is:
Time,Action,Actor,Where,Info
Action [#OPT_Action_1](https://slurm.schedmd.com/sacctmgr.html) Displays the type of Action that took place.
Actor [#OPT_Actor_1](https://slurm.schedmd.com/sacctmgr.html) Displays the Actor to generate a transaction.
Info [#OPT_Info](https://slurm.schedmd.com/sacctmgr.html) Displays details of the transaction.
TimeStamp [#OPT_TimeStamp](https://slurm.schedmd.com/sacctmgr.html) Displays when the transaction occurred.
Where [#OPT_Where](https://slurm.schedmd.com/sacctmgr.html) Displays details of the constraints for the transaction.
NOTE : If using the WithAssoc option you can also view the information
about the various associations the transaction affected. The
Association format fields are described
in the LIST/SHOW ASSOCIATION FORMAT OPTIONS section.
## SPECIFICATIONS FOR USERS[#SECTION_SPECIFICATIONS-FOR-USERS](https://slurm.schedmd.com/sacctmgr.html)
Users can be created, modified, and deleted with sacctmgr. These
options allow you to set the corresponding attributes or filter on them
when querying for Users.
It is important to recognize the difference between a User and an Association.
There is a User entity that exists for each unique username. However, there
can be multiple User Associations for the same User. The combination of a
Cluster, Account, User, and optionally a Partition constitute a User
Association. When adding an existing User to another Account, you are creating
an additional User Association rather than modifying an existing User.
Account =< account >[#OPT_Account_3](https://slurm.schedmd.com/sacctmgr.html) Account name to add this user to.
AdminLevel =< level >[#OPT_AdminLevel](https://slurm.schedmd.com/sacctmgr.html) Admin level of user. Valid levels are None, Operator, and Admin.
Cluster =< cluster >[#OPT_Cluster_10](https://slurm.schedmd.com/sacctmgr.html) Specific cluster to add user to the account on. Default is all in system.
DefaultAccount =< account >[#OPT_DefaultAccount](https://slurm.schedmd.com/sacctmgr.html) Identify the default account name to be used for a job if none is
specified at submission time.
DefaultWCKey =< defaultwckey >[#OPT_DefaultWCKey](https://slurm.schedmd.com/sacctmgr.html) Identify the default Workload Characterization Key.
Name =< name >[#OPT_Name_8](https://slurm.schedmd.com/sacctmgr.html) Name of user.
NewName =< newname >[#OPT_NewName](https://slurm.schedmd.com/sacctmgr.html) Use to rename a user in the accounting database
Partition =< name >[#OPT_Partition_2](https://slurm.schedmd.com/sacctmgr.html) Partition name.
NOTE : See also Partitions listed in the SPECIFICATIONS FOR
ASSOCIATIONS section.
RawUsage =< value >[#OPT_RawUsage_2](https://slurm.schedmd.com/sacctmgr.html) This allows an administrator to reset the raw usage accrued to a user.
The only value currently supported is 0 (zero). This is a settable
specification only - it cannot be used as a filter to list users.
WCKeys =< wckeys >[#OPT_WCKeys](https://slurm.schedmd.com/sacctmgr.html) Workload Characterization Key values.
WithAssoc [#OPT_WithAssoc_2](https://slurm.schedmd.com/sacctmgr.html) Display all associations for this user.
WithCoord [#OPT_WithCoord_1](https://slurm.schedmd.com/sacctmgr.html) Display all accounts a user is coordinator for.
WithDeleted [#OPT_WithDeleted_6](https://slurm.schedmd.com/sacctmgr.html) Display information with previously deleted data.
Users that are deleted within 24 hours of being created and did not have
a job run by the user during that time will be removed from the database.
Otherwise, the user will be marked as deleted and will be viewable with
the WithDeleted flag.
NOTE : If using the WithAssoc option you can also query against
association specific information to view only certain associations
this user may have. These extra options can be found in the
SPECIFICATIONS FOR ASSOCIATIONS section. You can also use the
general specifications list above in the GENERAL SPECIFICATIONS FOR
ASSOCIATION BASED ENTITIES section.
## LIST/SHOW USER FORMAT OPTIONS[#SECTION_LIST/SHOW-USER-FORMAT-OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
Fields you can display when viewing User records by using the
format= option. The default format is:
User,DefaultAccount,DefaultWCKey,AdminLevel
AdminLevel [#OPT_AdminLevel_1](https://slurm.schedmd.com/sacctmgr.html) Admin level of user.
Coordinators [#OPT_Coordinators_1](https://slurm.schedmd.com/sacctmgr.html) List of users that are a coordinator of the account. (Only filled in
when using the WithCoordinator option.)
DefaultAccount [#OPT_DefaultAccount_1](https://slurm.schedmd.com/sacctmgr.html) The user's default account.
DefaultWCKey [#OPT_DefaultWCKey_1](https://slurm.schedmd.com/sacctmgr.html) The user's default wckey.
User [#OPT_User_4](https://slurm.schedmd.com/sacctmgr.html) The name of a user.
NOTE : If using the WithAssoc option you can also view the information
about the various associations the user may have on all the
clusters in the system. The association information can be filtered.
Note that all the users in the database will always be shown as filter only
takes effect over the association data. The Association format fields are
described in the LIST/SHOW ASSOCIATION FORMAT OPTIONS section.
## LIST/SHOW WCKey[#SECTION_LIST/SHOW-WCKey](https://slurm.schedmd.com/sacctmgr.html)
Fields you can display when viewing WCKey records by using the
format= option. The default format is:
WCKey,Cluster,User
Cluster [#OPT_Cluster_11](https://slurm.schedmd.com/sacctmgr.html) Specific cluster for the WCKey.
ID [#OPT_ID_6](https://slurm.schedmd.com/sacctmgr.html) The ID of the WCKey.
User [#OPT_User_5](https://slurm.schedmd.com/sacctmgr.html) The name of a user for the WCKey.
WCKey [#OPT_WCKey_1](https://slurm.schedmd.com/sacctmgr.html) Workload Characterization Key.
WithDeleted [#OPT_WithDeleted_7](https://slurm.schedmd.com/sacctmgr.html) Display information with previously deleted data.
WCKeys that are deleted within 24 hours of being created and did not have
a job run with the WCKey during that time will be removed from the database.
Otherwise, the WCKey will be marked as deleted and will be viewable with
the WithDeleted flag.
## LIST/SHOW TRES[#SECTION_LIST/SHOW-TRES](https://slurm.schedmd.com/sacctmgr.html)
Fields you can display when viewing TRES records by using the
format= option. The default format is:
Type,Name,ID
ID [#OPT_ID_7](https://slurm.schedmd.com/sacctmgr.html) The identification number of the trackable resource as it appears
in the database.
Name [#OPT_Name_9](https://slurm.schedmd.com/sacctmgr.html) The name of the trackable resource. This option is required for
TRES types BB (Burst buffer), GRES, and License. Types CPU, Energy,
Memory, and Node do not have Names. For example if GRES is the
type then name is the denomination of the GRES itself e.g. GPU.
Type [#OPT_Type_2](https://slurm.schedmd.com/sacctmgr.html) The type of the trackable resource. Current types are BB (Burst
buffer), CPU, Energy, GRES, License, Memory, and Node.
## TRES information[#SECTION_TRES-information](https://slurm.schedmd.com/sacctmgr.html)
Trackable RESources (TRES) are used in many QOS or Association limits
(GrpTRES* / MaxTRES*). When setting limits, one or more comma-separated
"TRES=value" assignments can be specified.
Each TRES can be one of the Slurm defaults (e.g., cpu , mem ,
node ), or any defined generic resource. You can see the list of available
resources by running sacctmgr show tres .
Each TRES has a different limit, e.g., "GrpTRES=cpu=16,mem=32G" would
establish 2 different limits: one for 16 CPUs and another for 32 GB of memory.
Setting a new value for a TRES type does not affect any other TRES types that
were previously specified. For example, on the same entity as above, a
subsequent assignment of "GrpTRES=gres/gpu=2" will result in
"GrpTRES=cpu=16,mem=32G,gres/gpu=2" applying to that entity.
To remove a limit, assign -1 to the TRES type whose limit should be removed,
e.g., "GrpTRES=cpu=-1" would remove only the cpu TRES limit, resulting in
"GrpTRES=mem=32G,gres/gpu=2" on that entity.
Starting in Slurm 25.11, a TRES assignment can use a += or -= operator to add
to or remove from the previously set value for that TRES, e.g.,
"GrpTRES=mem-=8G,gres/gpu+=2" would result in "GrpTRES=mem=24G,gres/gpu=4" on
that entity.
NOTE : When dealing with Memory as a TRES the default units are MB. A
suffix of G, T, or P can be added to specify a limit in larger units.
NOTE : The Billing TRES is calculated from a partition's
TRESBillingWeights. It is temporarily calculated during scheduling for each
partition to enforce billing TRES limits. The final Billing TRES value is
calculated after the job has been allocated resources and can be seen in
scontrol show jobs and sacct output.
## GLOBAL FORMAT OPTION[#SECTION_GLOBAL-FORMAT-OPTION](https://slurm.schedmd.com/sacctmgr.html)
When using the format option for listing various fields you can put a
%NUMBER afterwards to specify how many characters should be printed.
e.g. format=name%30 will print 30 characters of field name right
justified. A -30 will print 30 characters left justified.
## FLAT FILE DUMP AND LOAD[#SECTION_FLAT-FILE-DUMP-AND-LOAD](https://slurm.schedmd.com/sacctmgr.html)
sacctmgr has the capability to load and dump Slurm association data to and
from a file. This method can easily add a new cluster or copy an
existing cluster's associations into a new cluster with similar
accounts. Each file contains Slurm association data for a single
cluster. Beginning with version 25.05, QOS information is included in the
dump file. Comments can be put into the file with the # character.
Each line of information must begin with one of the five titles; QOS ,
Cluster , Parent , Account or User . Following the title
is a space, dash, space, entity value, then specifications. Specifications are
colon-separated. If any variable, such as an Organization name, has a space in
it, surround the name with single or double quotes.
sacctmgr dump/load must be run as a Slurm administrator or root. If using
sacctmgr load on a database without any associations, it must be run as root
(because there aren't any users in the database yet).
### dump[#SECTION_dump_1](https://slurm.schedmd.com/sacctmgr.html)
Dump cluster associations from the database into a file. If no file is given
then one will be generated, using the cluster name for the file name. That
file will be created in the current working directory.
To create a file with the association information you can run:
```text
sacctmgr dump tux file=tux.cfg
```
Cluster =[#OPT_Cluster_12](https://slurm.schedmd.com/sacctmgr.html) Specify the cluster to dump the information for.
File =[#OPT_File](https://slurm.schedmd.com/sacctmgr.html) Specify a file to save flat file data to.
If the filename is not specified it uses clustername.cfg filename by default.
### load[#SECTION_load_1](https://slurm.schedmd.com/sacctmgr.html)
Load cluster associations into the database. The imported associations will be
reconciled with existing ones.
To load a previously created file you can run:
```text
sacctmgr load file=tux.cfg
```
clean [#OPT_clean](https://slurm.schedmd.com/sacctmgr.html) Delete what was already there and start from scratch with this information.
With no options this will only remove the cluster along with it's associations.
No accounts, users, or QOS will be removed.
This also accepts a comma-separated list of other options to remove. Those
include 'account', 'qos' and 'user'. If you would like to remove accounts, qos,
and users along with the cluster and associations give the input of
clean=account,qos,user .
Cluster =[#OPT_Cluster_13](https://slurm.schedmd.com/sacctmgr.html) Specify a different name for the cluster than that which is in the file.
File =[#OPT_File_1](https://slurm.schedmd.com/sacctmgr.html) Specify a flat file to load from.
## SPECIFICATIONS FOR FLAT FILE[#SECTION_SPECIFICATIONS-FOR-FLAT-FILE](https://slurm.schedmd.com/sacctmgr.html)
Since the associations in the system follow a hierarchy, so does the
file. Anything that is a parent needs to be defined before any
children. The only exception is the understood 'root' account. This
is always a default for any cluster and does not need to be defined.
To edit/create a file start with a cluster line for the new cluster:
```text
Cluster - cluster_name:MaxTRESPerJob=node=15
```
Anything included on this line will be the default for all
associations on this cluster. The options for the cluster are:
FairShare =[#OPT_FairShare](https://slurm.schedmd.com/sacctmgr.html) Allocated shares used for fairshare calculation.
GrpJobs =[#OPT_GrpJobs_4](https://slurm.schedmd.com/sacctmgr.html) Maximum number of running jobs in aggregate for this association and its
children.
GrpJobsAccrue =[#OPT_GrpJobsAccrue_4](https://slurm.schedmd.com/sacctmgr.html) Maximum number of pending jobs in aggregate able to accrue age priority for this
association and its children.
GrpNodes =[#OPT_GrpNodes](https://slurm.schedmd.com/sacctmgr.html) This option has been deprecated in favor of the more versatile TRES.
Equivalent limit definition is now GrpTRES=node=# .
GrpSubmitJobs =[#OPT_GrpSubmitJobs_4](https://slurm.schedmd.com/sacctmgr.html) Maximum number of jobs in a pending or running state at any time in aggregate
for this association and its children.
GrpTRES =[#OPT_GrpTRES_4](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES able to be allocated by running jobs in aggregate for
this association and its children.
GrpTRESMins =[#OPT_GrpTRESMins_4](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES minutes that can possibly be used by past, present and
future jobs in this association and its children.
GrpTRESRunMins =[#OPT_GrpTRESRunMins_4](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES minutes able to be allocated by running jobs in this
association and its children. This takes into consideration time limit of
running jobs and consumes it. If the limit is reached no new jobs are started
until other jobs finish to allow time to free up.
GrpWall =[#OPT_GrpWall_4](https://slurm.schedmd.com/sacctmgr.html) Maximum wall clock time able to be allocated by running jobs in aggregate in
this association and its children.
MaxJobs =[#OPT_MaxJobs_2](https://slurm.schedmd.com/sacctmgr.html) Maximum number of running jobs per user in this association.
MaxTRESPerJob =[#OPT_MaxTRESPerJob_4](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES each job can use in this association.
MaxWallDurationPerJob =[#OPT_MaxWallDurationPerJob_4](https://slurm.schedmd.com/sacctmgr.html) Maximum wall clock time each job can use in this association.
QOS =[#OPT_QOS](https://slurm.schedmd.com/sacctmgr.html) Comma-separated list of Quality of Service names (Defined in sacctmgr).
After the entry for the root account you will have entries for the other
accounts on the system. The entries will look similar to this example:
```text
Parent - root Account - cs:MaxTRESPerJob=node=5:MaxJobs=4:FairShare=399:MaxWallDurationPerJob=40:Description='Computer Science':Organization='LC' Parent - cs Account - test:MaxTRESPerJob=node=1:MaxJobs=1:FairShare=1:MaxWallDurationPerJob=1:Description='Test Account':Organization='Test'
```
Any of the options after a ':' can be left out and they can be in any order.
If you want to add any sub accounts just list the Parent THAT HAS ALREADY
BEEN CREATED before the account you are adding.
Account options are:
Description =[#OPT_Description_5](https://slurm.schedmd.com/sacctmgr.html) A brief description of the account.
FairShare =[#OPT_FairShare_1](https://slurm.schedmd.com/sacctmgr.html) Number used in conjunction with other associations to determine job priority.
GrpTRES =[#OPT_GrpTRES_5](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES able to be allocated by running jobs in aggregate for
this association and its children.
GrpTRESMins =[#OPT_GrpTRESMins_5](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES minutes that can possibly be used by past, present, and
future jobs in this association and its children.
GrpTRESRunMins =[#OPT_GrpTRESRunMins_5](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES minutes able to be allocated by running jobs in this
association and its children. This takes into consideration time limit of
running jobs and consumes it. If the limit is reached no new jobs are started
until other jobs finish to allow time to free up.
GrpJobs =[#OPT_GrpJobs_5](https://slurm.schedmd.com/sacctmgr.html) Maximum number of running jobs in aggregate for this association and its
children.
GrpJobsAccrue =[#OPT_GrpJobsAccrue_5](https://slurm.schedmd.com/sacctmgr.html) Maximum number of pending jobs in aggregate able to accrue age priority for this
association and its children.
GrpNodes =[#OPT_GrpNodes_1](https://slurm.schedmd.com/sacctmgr.html) This option has been deprecated in favor of the more versatile TRES.
Equivalent limit definition is now GrpTRES=node=# .
GrpSubmitJobs =[#OPT_GrpSubmitJobs_5](https://slurm.schedmd.com/sacctmgr.html) Maximum number of jobs in a pending or running state at any time in aggregate
for this association and its children.
GrpWall =[#OPT_GrpWall_5](https://slurm.schedmd.com/sacctmgr.html) Maximum wall clock time able to be allocated by running jobs in aggregate in
this association and its children.
MaxJobs =[#OPT_MaxJobs_3](https://slurm.schedmd.com/sacctmgr.html) Maximum number of running jobs per user in this association.
MaxNodesPerJob =[#OPT_MaxNodesPerJob](https://slurm.schedmd.com/sacctmgr.html) Maximum number of nodes per job in this association.
MaxWallDurationPerJob =[#OPT_MaxWallDurationPerJob_5](https://slurm.schedmd.com/sacctmgr.html) Maximum wall clock time each job can use in this association.
Organization =[#OPT_Organization_2](https://slurm.schedmd.com/sacctmgr.html) Name of organization that owns this account.
QOS (=,+=,-=)[#OPT_QOS_1](https://slurm.schedmd.com/sacctmgr.html) Comma-separated list of Quality of Service names (Defined in sacctmgr).
To add users to an account add a line after the Parent line, similar to this:
```text
Parent - test User - adam:MaxTRESPerJob=node:2:MaxJobs=3:FairShare=1:MaxWallDurationPerJob=1:AdminLevel=Operator:Coordinator='test'
```
User options are:
AdminLevel =[#OPT_AdminLevel_2](https://slurm.schedmd.com/sacctmgr.html) Type of admin this user is (Administrator, Operator)
Must be defined on the first occurrence of the user.
Coordinator =[#OPT_Coordinator](https://slurm.schedmd.com/sacctmgr.html) Comma-separated list of accounts this user is coordinator over
Must be defined on the first occurrence of the user.
DefaultAccount =[#OPT_DefaultAccount_2](https://slurm.schedmd.com/sacctmgr.html) System wide default account name
Must be defined on the first occurrence of the user.
FairShare =[#OPT_FairShare_2](https://slurm.schedmd.com/sacctmgr.html) Number used in conjunction with other associations to determine job priority.
MaxJobs =[#OPT_MaxJobs_4](https://slurm.schedmd.com/sacctmgr.html) Maximum number of running jobs from this user.
MaxTRESPerJob =[#OPT_MaxTRESPerJob_5](https://slurm.schedmd.com/sacctmgr.html) Maximum number of TRES each job from this user can use.
MaxWallDurationPerJob =[#OPT_MaxWallDurationPerJob_6](https://slurm.schedmd.com/sacctmgr.html) Maximum wall clock time each job from this user can use.
QOS (=,+=,-=)[#OPT_QOS_2](https://slurm.schedmd.com/sacctmgr.html) Comma-separated list of Quality of Service names (Defined in sacctmgr).
## ARCHIVE FUNCTIONALITY[#SECTION_ARCHIVE-FUNCTIONALITY](https://slurm.schedmd.com/sacctmgr.html)
Sacctmgr has the capability to archive to a flatfile and or load that
data if needed later. The archiving is usually done by the slurmdbd
and it is highly recommended you only do it through sacctmgr if you
completely understand what you are doing. For slurmdbd options see
"man slurmdbd" for more information.
Loading data into the database can be done from these files to either
view old data or regenerate rolled up data.
For information about configuring an archive server see
<[https://slurm.schedmd.com/accounting.html#archive](https://slurm.schedmd.com/accounting.html)>.
### archive dump[#SECTION_archive-dump](https://slurm.schedmd.com/sacctmgr.html)
Dump accounting data to file. Data will not be archived unless the
corresponding purge option is included in this command or in slurmdbd.conf.
This operation cannot be rolled back
once executed. If one of the following options is not specified when sacctmgr
is called, the value configured in slurmdbd.conf is used.
Directory =[#OPT_Directory](https://slurm.schedmd.com/sacctmgr.html) Directory to store the archive data.
Events [#OPT_Events](https://slurm.schedmd.com/sacctmgr.html) Archive Events. If not specified and PurgeEventAfter is set
all event data removed will be lost permanently.
Jobs [#OPT_Jobs](https://slurm.schedmd.com/sacctmgr.html) Archive Jobs. If not specified and PurgeJobAfter is set
all job data removed will be lost permanently.
PurgeEventAfter =[#OPT_PurgeEventAfter](https://slurm.schedmd.com/sacctmgr.html) Purge cluster event records older than time stated in months. If you
want to purge on a shorter time period you can include hours, or days
behind the numeric value to get those more frequent purges. (e.g. a
value of '12hours' would purge everything older than 12 hours.)
PurgeJobAfter =[#OPT_PurgeJobAfter](https://slurm.schedmd.com/sacctmgr.html) Purge job records older than time stated in months. If you
want to purge on a shorter time period you can include hours, or days
behind the numeric value to get those more frequent purges. (e.g. a
value of '12hours' would purge everything older than 12 hours.)
PurgeStepAfter =[#OPT_PurgeStepAfter](https://slurm.schedmd.com/sacctmgr.html) Purge step records older than time stated in months. If you
want to purge on a shorter time period you can include hours, or days
behind the numeric value to get those more frequent purges. (e.g. a
value of '12hours' would purge everything older than 12 hours.)
PurgeSuspendAfter =[#OPT_PurgeSuspendAfter](https://slurm.schedmd.com/sacctmgr.html) Purge job suspend records older than time stated in months. If you
want to purge on a shorter time period you can include hours, or days
behind the numeric value to get those more frequent purges. (e.g. a
value of '12hours' would purge everything older than 12 hours.)
Script =[#OPT_Script](https://slurm.schedmd.com/sacctmgr.html) Run this script instead of the generic form of archive to flat files.
Steps [#OPT_Steps](https://slurm.schedmd.com/sacctmgr.html) Archive Steps. If not specified and PurgeStepAfter is set
all step data removed will be lost permanently.
Suspend [#OPT_Suspend](https://slurm.schedmd.com/sacctmgr.html) Archive Suspend Data. If not specified and PurgeSuspendAfter is set
all suspend data removed will be lost permanently.
### archive load[#SECTION_archive-load](https://slurm.schedmd.com/sacctmgr.html)
Load in to the database previously archived data. The archive file will not be
loaded if the records already exist in the database - therefore, trying to load
an archive file more than once will result in an error. When this data is again
archived and purged from the database, if the old archive file is still in the
directory ArchiveDir, a new archive file will be created (see ArchiveDir in the
slurmdbd.conf man page), so the old file will not be overwritten and these files
will have duplicate records.
Archive files from the current or any prior Slurm release may be loaded
through archive load .
File =[#OPT_File_2](https://slurm.schedmd.com/sacctmgr.html) File to load into database. The specified file must exist on the slurmdbd host,
which is not necessarily the machine running the command.
Insert =[#OPT_Insert](https://slurm.schedmd.com/sacctmgr.html) SQL to insert directly into the database. This should be used very
cautiously since this is writing your sql into the database.
## PERFORMANCE[#SECTION_PERFORMANCE](https://slurm.schedmd.com/sacctmgr.html)
Executing sacctmgr sends a remote procedure call to slurmdbd . If
enough calls from sacctmgr or other Slurm client commands that send remote
procedure calls to the slurmdbd daemon come in at once, it can result in a
degradation of performance of the slurmdbd daemon, possibly resulting in a
denial of service.
Do not run sacctmgr or other Slurm client commands that send remote
procedure calls to slurmdbd from loops in shell scripts or other programs.
Ensure that programs limit calls to sacctmgr to the minimum necessary for
the information you are trying to gather.
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/sacctmgr.html)
Some sacctmgr options may be set via environment variables. These
environment variables, along with their corresponding options, are listed below.
(Note: Command line options will always override these settings.)
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/sacctmgr.html) The location of the Slurm configuration file.
SLURM_DEBUG_FLAGS [#OPT_SLURM_DEBUG_FLAGS](https://slurm.schedmd.com/sacctmgr.html) Specify debug flags for sacctmgr to use. See DebugFlags in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for a full list of flags. The environment
variable takes precedence over the setting in the slurm.conf.
SLURM_JSON [#OPT_SLURM_JSON](https://slurm.schedmd.com/sacctmgr.html) Control JSON serialization:
compact [#OPT_compact](https://slurm.schedmd.com/sacctmgr.html) Output JSON as compact as possible.
pretty [#OPT_pretty](https://slurm.schedmd.com/sacctmgr.html) Output JSON in pretty format to make it more readable.
SLURM_YAML [#OPT_SLURM_YAML](https://slurm.schedmd.com/sacctmgr.html) Control YAML serialization:
compact Output YAML as compact as possible.[#OPT_compact_1](https://slurm.schedmd.com/sacctmgr.html)
pretty Output YAML in pretty format to make it more readable.[#OPT_pretty_1](https://slurm.schedmd.com/sacctmgr.html)
## EXAMPLES[#SECTION_EXAMPLES](https://slurm.schedmd.com/sacctmgr.html)
NOTE : There is an order to set up accounting associations.
You must define clusters before you add accounts and you must add accounts
before you can add users.
```text
$ sacctmgr create cluster tux $ sacctmgr create account name=science fairshare=50 $ sacctmgr create account name=chemistry parent=science fairshare=30 $ sacctmgr create account name=physics parent=science fairshare=20 $ sacctmgr create user name=adam cluster=tux account=physics fairshare=10 $ sacctmgr delete user name=adam cluster=tux account=physics $ sacctmgr delete user name=adam cluster=tux account=science partition=\"\" $ sacctmgr delete account name=physics cluster=tux $ sacctmgr modify user where name=adam cluster=tux account=physics set maxjobs=2 maxwall=30:00 $ sacctmgr add user brian account=chemistry $ sacctmgr list associations cluster=tux format=Account,Cluster,User,Fairshare tree withd $ sacctmgr list transactions Action="Add Users" Start=11/03-10:30:00 format=Where,Time $ sacctmgr dump cluster=tux file=tux_data_file $ sacctmgr load tux_data_file
```
A user's account can not be changed directly. A new association needs to be
created for the user with the new account. Then the association with the old
account can be deleted.
When modifying an object placing the key words 'set' and the
optional 'where' is critical to perform correctly below are examples to
produce correct results. As a rule of thumb anything you put in front
of the set will be used as a quantifier. If you want to put a
quantifier after the key word 'set' you should use the key
word 'where'. The following is wrong:
```text
$ sacctmgr modify user name=adam set fairshare=10 cluster=tux
```
This will produce an error as the above line reads modify user adam
set fairshare=10 and cluster=tux. Either of the following is correct:
```text
$ sacctmgr modify user name=adam cluster=tux set fairshare=10 $ sacctmgr modify user name=adam set fairshare=10 where cluster=tux
```
When changing qos for something only use the '=' operator when wanting
to explicitly set the qos to something. In most cases you will want
to use the '+=' or '-=' operator to either add to or remove from the
existing qos already in place.
If a user already has qos of normal,standby for a parent or it was
explicitly set you should use qos+=expedite to add this to the list in
this fashion.
If you are looking to only add the qos expedite to only a certain
account and or cluster you can do that by specifying them in the
sacctmgr line.
```text
$ sacctmgr modify user name=adam set qos+=expedite
```
or
```text
$ sacctmgr modify user name=adam acct=this cluster=tux set qos+=expedite
```
Let's give an example how to add QOS to user accounts.
List all available QOSs in the cluster.
```text
$ sacctmgr show qos format=name Name --------- normal expedite
```
List all the associations in the cluster.
```text
$ sacctmgr show assoc format=cluster,account,qos Cluster Account QOS -------- ---------- -------------------- zebra root normal zebra root normal zebra g normal zebra g1 normal
```
Add the QOS expedite to account G1 and display the result.
Using the operator += the QOS will be added together
with the existing QOS to this account.
```text
$ sacctmgr modify account name=g1 set qos+=expedite $ sacctmgr show assoc format=cluster,account,qos Cluster Account QOS -------- ---------- -------------------- zebra root normal zebra root normal zebra g normal zebra g1 expedite,normal
```
Now set the QOS expedite as the only QOS for the account G and display
the result. Using the operator = that expedite is the only usable
QOS by account G
```text
$ sacctmgr modify account name=G set qos=expedite $ sacctmgr show assoc format=cluster,account,qos Cluster Account QOS -------- ---------- -------------------- zebra root normal zebra root normal zebra g expedite zebra g1 expedite,normal
```
If a new account is added under the account G it will inherit the
QOS expedite and it will not have access to QOS normal.
```text
$ sacctmgr add account banana parent=G $ sacctmgr show assoc format=cluster,account,qos Cluster Account QOS -------- ---------- -------------------- zebra root normal zebra root normal zebra g expedite zebra banana expedite zebra g1 expedite,normal
```
An example of listing trackable resources:
```text
$ sacctmgr show tres Type Name ID ---------- ----------------- -------- cpu 1 mem 2 energy 3 node 4 billing 5 gres gpu:tesla 1001 license vcs 1002 bb cray 1003
```
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/sacctmgr.html)
Copyright (C) 2008-2010 Lawrence Livermore National Security.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/sacctmgr.html)
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5),
[slurmdbd](https://slurm.schedmd.com/slurmdbd.html) (8)
## Index
[NAME](https://slurm.schedmd.com/sacctmgr.html)
[SYNOPSIS](https://slurm.schedmd.com/sacctmgr.html)
[DESCRIPTION](https://slurm.schedmd.com/sacctmgr.html)
[OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
[COMMANDS](https://slurm.schedmd.com/sacctmgr.html)
[INTERACTIVE COMMANDS](https://slurm.schedmd.com/sacctmgr.html)
[ENTITIES](https://slurm.schedmd.com/sacctmgr.html)
[GENERAL SPECIFICATIONS FOR ASSOCIATION BASED ENTITIES](https://slurm.schedmd.com/sacctmgr.html)
[SPECIFICATIONS FOR ACCOUNTS](https://slurm.schedmd.com/sacctmgr.html)
[LIST/SHOW ACCOUNT FORMAT OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
[SPECIFICATIONS FOR ASSOCIATIONS](https://slurm.schedmd.com/sacctmgr.html)
[LIST/SHOW ASSOCIATION FORMAT OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
[SPECIFICATIONS FOR CLUSTERS](https://slurm.schedmd.com/sacctmgr.html)
[LIST/SHOW CLUSTER FORMAT OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
[SPECIFICATIONS FOR COORDINATOR](https://slurm.schedmd.com/sacctmgr.html)
[SPECIFICATIONS FOR EVENTS](https://slurm.schedmd.com/sacctmgr.html)
[LIST/SHOW EVENT FORMAT OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
[SPECIFICATIONS FOR FEDERATION](https://slurm.schedmd.com/sacctmgr.html)
[LIST/SHOW FEDERATION FORMAT OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
[SPECIFICATIONS FOR INSTANCES](https://slurm.schedmd.com/sacctmgr.html)
[LIST/SHOW INSTANCE FORMAT OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
[SPECIFICATIONS FOR JOB](https://slurm.schedmd.com/sacctmgr.html)
[LIST/SHOW JOB FORMAT OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
[SPECIFICATIONS FOR QOS](https://slurm.schedmd.com/sacctmgr.html)
[LIST/SHOW QOS FORMAT OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
[SPECIFICATIONS FOR RESERVATIONS](https://slurm.schedmd.com/sacctmgr.html)
[LIST/SHOW RESERVATION FORMAT OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
[SPECIFICATIONS FOR RESOURCE](https://slurm.schedmd.com/sacctmgr.html)
[LIST/SHOW RESOURCE FORMAT OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
[SPECIFICATIONS FOR RUNAWAYJOB](https://slurm.schedmd.com/sacctmgr.html)
[LIST/SHOW RUNAWAYJOB FORMAT OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
[SPECIFICATIONS FOR TRANSACTIONS](https://slurm.schedmd.com/sacctmgr.html)
[LIST/SHOW TRANSACTIONS FORMAT OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
[SPECIFICATIONS FOR USERS](https://slurm.schedmd.com/sacctmgr.html)
[LIST/SHOW USER FORMAT OPTIONS](https://slurm.schedmd.com/sacctmgr.html)
[LIST/SHOW WCKey](https://slurm.schedmd.com/sacctmgr.html)
[LIST/SHOW TRES](https://slurm.schedmd.com/sacctmgr.html)
[TRES information](https://slurm.schedmd.com/sacctmgr.html)
[GLOBAL FORMAT OPTION](https://slurm.schedmd.com/sacctmgr.html)
[FLAT FILE DUMP AND LOAD](https://slurm.schedmd.com/sacctmgr.html)
[dump](https://slurm.schedmd.com/sacctmgr.html)
[load](https://slurm.schedmd.com/sacctmgr.html)
[SPECIFICATIONS FOR FLAT FILE](https://slurm.schedmd.com/sacctmgr.html)
[ARCHIVE FUNCTIONALITY](https://slurm.schedmd.com/sacctmgr.html)
[archive dump](https://slurm.schedmd.com/sacctmgr.html)
[archive load](https://slurm.schedmd.com/sacctmgr.html)
[PERFORMANCE](https://slurm.schedmd.com/sacctmgr.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/sacctmgr.html)
[EXAMPLES](https://slurm.schedmd.com/sacctmgr.html)
[COPYING](https://slurm.schedmd.com/sacctmgr.html)
[SEE ALSO](https://slurm.schedmd.com/sacctmgr.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
