---
source_url: https://slurm.schedmd.com/sinfo.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:23 UTC
title: "Slurm Workload Manager - sinfo"
---

# sinfo
Section: Slurm Commands (1)
Updated: Slurm Commands
[Index](https://slurm.schedmd.com/sinfo.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/sinfo.html)
sinfo - View information about Slurm nodes and partitions.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/sinfo.html)
sinfo [ OPTIONS ...]
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/sinfo.html)
sinfo is used to view partition and node information for a
system running Slurm.
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/sinfo.html)
-a , --all [#OPT_all](https://slurm.schedmd.com/sinfo.html) Display information about all partitions. This causes information to be
displayed about partitions that are configured as hidden and partitions that
are unavailable to the user's group.
-M , --clusters =< string >[#OPT_clusters](https://slurm.schedmd.com/sinfo.html) Clusters to issue commands to. Multiple cluster names may be comma separated.
A value of ' all ' will query all clusters.
Note that the slurmdbd must be up for this option to work properly, unless
running in a federation with either FederationParameters=fed_display
configured or the --federation option set.
This option implicitly sets the --local option.
-d , --dead [#OPT_dead](https://slurm.schedmd.com/sinfo.html) Only show nodes that have unexpectedly stopped responding. This may not show
nodes in a POWERED_DOWN state since they are expected to be down.
-e , --exact [#OPT_exact](https://slurm.schedmd.com/sinfo.html) If set, do not group node information on multiple nodes unless
their configurations to be reported are identical. Otherwise
cpu count, memory size, and disk space for nodes will be listed
with the minimum value followed by a "+" for nodes with the
same partition and state (e.g. "250+").
--federation [#OPT_federation](https://slurm.schedmd.com/sinfo.html) Show all partitions from the federation if a member of one.
-F , --future [#OPT_future](https://slurm.schedmd.com/sinfo.html) Report nodes in FUTURE state.
-o , --format =< output_format >[#OPT_format](https://slurm.schedmd.com/sinfo.html) Specify the information to be displayed using an sinfo
format string.
If the command is executed in a federated cluster environment and information
about more than one cluster is to be displayed and the -h, --noheader
option is used, then the cluster name will be displayed before the default
output formats shown below.
Format strings transparently used by sinfo when running with various
options are:
default [#OPT_default](https://slurm.schedmd.com/sinfo.html)
"%#P %.5a %.10l %.6D %.6t %N"
--summarize [#OPT_summarize](https://slurm.schedmd.com/sinfo.html)
"%#P %.5a %.10l %.16F %N"
--long [#OPT_long](https://slurm.schedmd.com/sinfo.html)
"%#P %.5a %.10l %.10s %.4r %.8h %.10g %.6D %.11T %.11i %N"
--Node [#OPT_Node](https://slurm.schedmd.com/sinfo.html)
"%#N %.6D %#P %6t"
--long --Node [#OPT_long---Node](https://slurm.schedmd.com/sinfo.html)
"%#N %.6D %#P %.11T %.4c %.8z %.6m %.8d %.6w %.8f %20E"
--list-reasons [#OPT_list-reasons](https://slurm.schedmd.com/sinfo.html)
"%20E %9u %19H %N"
--long --list-reasons [#OPT_long---list-reasons](https://slurm.schedmd.com/sinfo.html)
"%20E %12U %19H %6t %N"
In the above format strings, the use of "#" represents the
maximum length of any partition name or node list to be printed.
A pass is made over the records to be printed to establish the size in order
to align the sinfo output, then a second pass is made over the records to
print them.
Note that the literal character "#" itself is not a valid field length
specification, but is only used to document this behavior.
The format of each field is "%[[.]size]type[suffix]"
size [#OPT_size](https://slurm.schedmd.com/sinfo.html) Minimum field size. If no size is specified, whatever is needed to print the
information will be used.
. [#OPT_.](https://slurm.schedmd.com/sinfo.html) Indicates the output should be right justified and size must be specified.
By default output is left justified.
suffix [#OPT_suffix](https://slurm.schedmd.com/sinfo.html) Arbitrary string to append to the end of the field.
Valid type specifications include:
%all [#OPT_%all](https://slurm.schedmd.com/sinfo.html) Print all fields available for this data type with a vertical bar separating
each field.
%a [#OPT_%a](https://slurm.schedmd.com/sinfo.html) State/availability of a partition.
%A [#OPT_%A](https://slurm.schedmd.com/sinfo.html) Number of nodes by state in the format "allocated/idle".
Do not use this with a node state option ("%t" or "%T") or
the different node states will be placed on separate lines.
%b [#OPT_%b](https://slurm.schedmd.com/sinfo.html) Features currently active on the nodes, also see %f .
%B [#OPT_%B](https://slurm.schedmd.com/sinfo.html) The max number of CPUs per node available to jobs in the partition.
%c [#OPT_%c](https://slurm.schedmd.com/sinfo.html) Number of CPUs per node.
%C [#OPT_%C](https://slurm.schedmd.com/sinfo.html) Number of CPUs by state in the format
"allocated/idle/other/total". Do not use this with a node
state option ("%t" or "%T") or the different node states will
be placed on separate lines.
%d [#OPT_%d](https://slurm.schedmd.com/sinfo.html) Size of temporary disk space per node in megabytes.
%D [#OPT_%D](https://slurm.schedmd.com/sinfo.html) Number of nodes.
%e [#OPT_%e](https://slurm.schedmd.com/sinfo.html) The total memory, in MB, currently free on the node as reported by the OS. This
value is for informational use only and is not used for scheduling.
%E [#OPT_%E](https://slurm.schedmd.com/sinfo.html) The reason a node is unavailable (down, drained, or draining states).
%f [#OPT_%f](https://slurm.schedmd.com/sinfo.html) Features available the nodes, also see %b .
%F [#OPT_%F](https://slurm.schedmd.com/sinfo.html) Number of nodes by state in the format
"allocated/idle/other/total". Note the use of this format option with a node
state format option ("%t" or "%T") will result in the different node states
being be reported on separate lines.
%g [#OPT_%g](https://slurm.schedmd.com/sinfo.html) Groups which may use the nodes.
%G [#OPT_%G](https://slurm.schedmd.com/sinfo.html) Generic resources (gres) associated with the nodes.
%h [#OPT_%h](https://slurm.schedmd.com/sinfo.html) Print the OverSubscribe setting for the partition.
%H [#OPT_%H](https://slurm.schedmd.com/sinfo.html) Print the timestamp of the reason a node is unavailable.
%i [#OPT_%i](https://slurm.schedmd.com/sinfo.html) If a node is in an advanced reservation print the name of that reservation.
%I [#OPT_%I](https://slurm.schedmd.com/sinfo.html) Partition job priority weighting factor.
%l [#OPT_%l](https://slurm.schedmd.com/sinfo.html) Maximum time for any job in the format "days-hours:minutes:seconds"
%L [#OPT_%L](https://slurm.schedmd.com/sinfo.html) Default time for any job in the format "days-hours:minutes:seconds"
%m [#OPT_%m](https://slurm.schedmd.com/sinfo.html) Size of memory per node in megabytes.
%M [#OPT_%M](https://slurm.schedmd.com/sinfo.html) PreemptionMode.
%n [#OPT_%n](https://slurm.schedmd.com/sinfo.html) List of node hostnames.
%N [#OPT_%N](https://slurm.schedmd.com/sinfo.html) List of node names.
%o [#OPT_%o](https://slurm.schedmd.com/sinfo.html) List of node communication addresses.
%O [#OPT_%O](https://slurm.schedmd.com/sinfo.html) CPU load of a node as reported by the OS.
%p [#OPT_%p](https://slurm.schedmd.com/sinfo.html) Partition scheduling tier priority.
%P [#OPT_%P](https://slurm.schedmd.com/sinfo.html) Partition name followed by "*" for the default partition, also see %R .
%r [#OPT_%r](https://slurm.schedmd.com/sinfo.html) Only user root may initiate jobs, "yes" or "no".
%R [#OPT_%R](https://slurm.schedmd.com/sinfo.html) Partition name, also see %P .
%s [#OPT_%s](https://slurm.schedmd.com/sinfo.html) Maximum job size in nodes.
%S [#OPT_%S](https://slurm.schedmd.com/sinfo.html) Allowed allocating nodes.
%t [#OPT_%t](https://slurm.schedmd.com/sinfo.html) State of nodes, compact form.
%T [#OPT_%T](https://slurm.schedmd.com/sinfo.html) State of nodes, extended form.
%u [#OPT_%u](https://slurm.schedmd.com/sinfo.html) Print the user name of who set the reason a node is unavailable.
%U [#OPT_%U](https://slurm.schedmd.com/sinfo.html) Print the user name and uid of who set the reason a node is unavailable.
%v [#OPT_%v](https://slurm.schedmd.com/sinfo.html) Print the running slurmd version. If reporting on a node list, print the
version of the first node in the list.
%V [#OPT_%V](https://slurm.schedmd.com/sinfo.html) Print the cluster name if running in a federation.
%w [#OPT_%w](https://slurm.schedmd.com/sinfo.html) Scheduling weight of the nodes.
%X [#OPT_%X](https://slurm.schedmd.com/sinfo.html) Number of sockets per node.
%Y [#OPT_%Y](https://slurm.schedmd.com/sinfo.html) Number of cores per socket.
%Z [#OPT_%Z](https://slurm.schedmd.com/sinfo.html) Number of threads per core.
%z [#OPT_%z](https://slurm.schedmd.com/sinfo.html) Extended processor information: number of sockets, cores, threads (S:C:T) per node.
-O , --Format =< output_format >[#OPT_Format](https://slurm.schedmd.com/sinfo.html) Specify the information to be displayed.
Also see the -o <output_format> , --format=<output_format>
option (which supports greater flexibility in formatting, but
does not support access to all fields because we ran out of letters).
Requests a comma separated list of job information to be displayed.
The format of each field is "type[:[.][size][suffix]]"
size [#OPT_size_1](https://slurm.schedmd.com/sinfo.html) The maximum field size.
If no size is specified, 20 characters will be allocated to print the information.
. [#OPT_._1](https://slurm.schedmd.com/sinfo.html) Indicates the output should be right justified and size must be specified.
By default, output is left justified.
suffix [#OPT_suffix_1](https://slurm.schedmd.com/sinfo.html) Arbitrary string to append to the end of the field.
Valid type specifications include:
All [#OPT_All](https://slurm.schedmd.com/sinfo.html) Print all fields available in the -o format for this data type with a
vertical bar separating each field.
AllocMem [#OPT_AllocMem](https://slurm.schedmd.com/sinfo.html) Prints the amount of allocated memory on a node.
AllocNodes [#OPT_AllocNodes](https://slurm.schedmd.com/sinfo.html) Allowed allocating nodes.
Available [#OPT_Available](https://slurm.schedmd.com/sinfo.html) State/availability of a partition.
Cluster [#OPT_Cluster](https://slurm.schedmd.com/sinfo.html) Print the cluster name if running in a federation.
Comment [#OPT_Comment](https://slurm.schedmd.com/sinfo.html) Comment. (Arbitrary descriptive string)
Cores [#OPT_Cores](https://slurm.schedmd.com/sinfo.html) Number of cores per socket.
CPUs [#OPT_CPUs](https://slurm.schedmd.com/sinfo.html) Number of CPUs per node.
CPUsLoad [#OPT_CPUsLoad](https://slurm.schedmd.com/sinfo.html) CPU load of a node as reported by the OS.
CPUsState [#OPT_CPUsState](https://slurm.schedmd.com/sinfo.html) Number of CPUs by state in the format
"allocated/idle/other/total". Do not use this with a node
state option ("%t" or "%T") or the different node states will
be placed on separate lines.
DefaultTime [#OPT_DefaultTime](https://slurm.schedmd.com/sinfo.html) Default time for any job in the format "days-hours:minutes:seconds".
Disk [#OPT_Disk](https://slurm.schedmd.com/sinfo.html) Size of temporary disk space per node in megabytes.
Extra [#OPT_Extra](https://slurm.schedmd.com/sinfo.html) Arbitrary string on the node.
Features [#OPT_Features](https://slurm.schedmd.com/sinfo.html) Features available on the nodes. Also see features_act .
features_act [#OPT_features_act](https://slurm.schedmd.com/sinfo.html) Features currently active on the nodes. Also see features .
FreeMem [#OPT_FreeMem](https://slurm.schedmd.com/sinfo.html) The total memory, in MB, currently free on the node as reported by the OS. This
value is for informational use only and is not used for scheduling.
Gres [#OPT_Gres](https://slurm.schedmd.com/sinfo.html) Generic resources (gres) associated with the nodes.
GresUsed [#OPT_GresUsed](https://slurm.schedmd.com/sinfo.html) Generic resources (gres) currently in use on the nodes.
Groups [#OPT_Groups](https://slurm.schedmd.com/sinfo.html) Groups which may use the nodes.
MaxCPUsPerNode [#OPT_MaxCPUsPerNode](https://slurm.schedmd.com/sinfo.html) The max number of CPUs per node available to jobs in the partition.
Memory [#OPT_Memory](https://slurm.schedmd.com/sinfo.html) Size of memory per node in megabytes.
NodeAddr [#OPT_NodeAddr](https://slurm.schedmd.com/sinfo.html) List of node communication addresses.
NodeAI [#OPT_NodeAI](https://slurm.schedmd.com/sinfo.html) Number of nodes by state in the format "allocated/idle".
Do not use this with a node state option ("%t" or "%T") or
the different node states will be placed on separate lines.
NodeAIOT [#OPT_NodeAIOT](https://slurm.schedmd.com/sinfo.html) Number of nodes by state in the format
"allocated/idle/other/total". Do not use this with a node
state option ("%t" or "%T") or the different node states will
be placed on separate lines.
NodeHost [#OPT_NodeHost](https://slurm.schedmd.com/sinfo.html) List of node hostnames.
NodeList [#OPT_NodeList](https://slurm.schedmd.com/sinfo.html) List of node names.
Nodes [#OPT_Nodes](https://slurm.schedmd.com/sinfo.html) Number of nodes.
OverSubscribe [#OPT_OverSubscribe](https://slurm.schedmd.com/sinfo.html) Whether jobs may oversubscribe compute resources (e.g. CPUs).
Partition [#OPT_Partition](https://slurm.schedmd.com/sinfo.html) Partition name followed by "*" for the default partition, also see %R .
PartitionName [#OPT_PartitionName](https://slurm.schedmd.com/sinfo.html) Partition name, also see %P .
Port [#OPT_Port](https://slurm.schedmd.com/sinfo.html) Node TCP port.
PreemptMode [#OPT_PreemptMode](https://slurm.schedmd.com/sinfo.html) Preemption mode.
PriorityJobFactor [#OPT_PriorityJobFactor](https://slurm.schedmd.com/sinfo.html) Partition factor used by priority/multifactor plugin in calculating job priority.
PriorityTier or Priority [#OPT_PriorityTier](https://slurm.schedmd.com/sinfo.html) Partition scheduling tier priority.
Reason [#OPT_Reason](https://slurm.schedmd.com/sinfo.html) The reason a node is unavailable (down, drained, or draining states).
Root [#OPT_Root](https://slurm.schedmd.com/sinfo.html) Only user root may initiate jobs, "yes" or "no".
Size [#OPT_Size](https://slurm.schedmd.com/sinfo.html) Maximum job size in nodes.
SocketCoreThread [#OPT_SocketCoreThread](https://slurm.schedmd.com/sinfo.html) Extended processor information: number of sockets, cores, threads (S:C:T) per node.
Sockets [#OPT_Sockets](https://slurm.schedmd.com/sinfo.html) Number of sockets per node.
StateCompact [#OPT_StateCompact](https://slurm.schedmd.com/sinfo.html) State of nodes, compact form.
StateLong [#OPT_StateLong](https://slurm.schedmd.com/sinfo.html) State of nodes, extended form.
StateComplete [#OPT_StateComplete](https://slurm.schedmd.com/sinfo.html) State of nodes, including all node state flags. e.g. "idle+cloud+power"
Threads [#OPT_Threads](https://slurm.schedmd.com/sinfo.html) Number of threads per core.
Time [#OPT_Time](https://slurm.schedmd.com/sinfo.html) Maximum time for any job in the format "days-hours:minutes:seconds".
TimeStamp [#OPT_TimeStamp](https://slurm.schedmd.com/sinfo.html) Print the timestamp of the reason a node is unavailable.
User [#OPT_User](https://slurm.schedmd.com/sinfo.html) Print the user name of who set the reason a node is unavailable.
UserLong [#OPT_UserLong](https://slurm.schedmd.com/sinfo.html) Print the user name and uid of who set the reason a node is unavailable.
Version [#OPT_Version](https://slurm.schedmd.com/sinfo.html) Print the running slurmd version. If reporting on a node list, print the
version of the first node in the list.
Weight [#OPT_Weight](https://slurm.schedmd.com/sinfo.html) Scheduling weight of the nodes.
--help [#OPT_help](https://slurm.schedmd.com/sinfo.html) Print a message describing all sinfo options.
--hide [#OPT_hide](https://slurm.schedmd.com/sinfo.html) Do not display information about hidden partitions. Partitions
that are configured as hidden or are not available to the user's group
will not be displayed. This is the default behavior.
-i , --iterate =< seconds >[#OPT_iterate](https://slurm.schedmd.com/sinfo.html) Print the state on a periodic basis.
Sleep for the indicated number of seconds between reports.
By default prints a time stamp with the header.
--json , --json = list , --json =< data_parser >[#OPT_json](https://slurm.schedmd.com/sinfo.html) Dump information as JSON using the default data_parser plugin or explicit
data_parser with parameters. All information is dumped, even if it would
normally not be. Sorting and formatting arguments passed to other options are
ignored; however, most filtering arguments are still used.
-R , --list-reasons [#OPT_list-reasons_1](https://slurm.schedmd.com/sinfo.html) List reasons nodes are in the down, drained, fail or failing state.
When nodes are in these states Slurm supports the inclusion
of a "reason" string by an administrator.
This option will display the first 20 characters of the reason
field and list of nodes with that reason for all nodes that are,
by default, down, drained, draining or failing.
This option may be used with other node filtering options
(e.g. -r , -d , -t , -n ),
however, combinations of these options that result in a
list of nodes that are not down or drained or failing will
not produce any output.
When used with -l the output additionally includes
the current node state.
--local [#OPT_local](https://slurm.schedmd.com/sinfo.html) Show only jobs local to this cluster. Ignore other clusters in this federation
(if any). Overrides --federation .
-l , --long [#OPT_long_1](https://slurm.schedmd.com/sinfo.html) Print more detailed information.
This is ignored if the --format option is specified.
--noconvert [#OPT_noconvert](https://slurm.schedmd.com/sinfo.html) Don't convert units from their original type (e.g. 2048M won't be converted to
2G).
-N , --Node [#OPT_Node_1](https://slurm.schedmd.com/sinfo.html) Print information in a node-oriented format with one line per node
and partition. That is, if a node belongs to more than one partition, then one
line for each node-partition pair will be shown.
If --partition is also specified, then only one line per node in this
partition is shown.
The default is to print information in a partition-oriented format.
This is ignored if the --format option is specified.
-n , --nodes =< nodes >[#OPT_nodes](https://slurm.schedmd.com/sinfo.html) Print information about the specified node(s).
Multiple nodes may be comma separated or expressed using a
node range expression (e.g. "linux[00-17]")
Limiting the query to just the relevant nodes can measurably improve the
performance of the command for large clusters.
-h , --noheader [#OPT_noheader](https://slurm.schedmd.com/sinfo.html) Do not print a header on the output.
-p , --partition =< partition >[#OPT_partition](https://slurm.schedmd.com/sinfo.html) Print information about the node(s) in the specified partition(s).
Multiple partitions are separated by commas.
-T , --reservation [#OPT_reservation](https://slurm.schedmd.com/sinfo.html) Only display information about Slurm reservations.
NOTE : This option causes sinfo to ignore most other options,
which are focused on partition and node information.
-r , --responding [#OPT_responding](https://slurm.schedmd.com/sinfo.html) Exclude any nodes that have unexpectedly stopped responding. This is the
opposite of --dead .
-S , --sort =< sort_list >[#OPT_sort](https://slurm.schedmd.com/sinfo.html) Specification of the order in which records should be reported.
This uses the same field specification as the <output_format>.
Multiple sorts may be performed by listing multiple sort fields
separated by commas. The field specifications may be preceded
by "+" or "-" for ascending (default) and descending order
respectively. The partition field specification, "P", may be
preceded by a "#" to report partitions in the same order that
they appear in Slurm's configuration file, slurm.conf .
For example, a sort value of "+P,-m" requests that records
be printed in order of increasing partition name and within a
partition by decreasing memory size. The default value of sort
is "#P,-t" (partitions ordered as configured then decreasing
node state). If the --Node option is selected, the
default sort value is "N" (increasing node name).
-t , --states =< states >[#OPT_states](https://slurm.schedmd.com/sinfo.html) List nodes only having the given state(s). Multiple states
may be comma separated and the comparison is case insensitive.
If the states are separated by '+', then the nodes must be in all states.
The state can be prefixed with '~' which will invert the result of match.
Possible values include (case insensitive): ALLOC, ALLOCATED, BLOCKED, CLOUD,
COMP, COMPLETING, DOWN, DRAIN (for node in DRAINING or DRAINED
states), DRAINED, DRAINING, FAIL, FUTURE, FUTR,
IDLE, MAINT, MIX, MIXED, NO_RESPOND, NPC, PERFCTRS, PLANNED,
POWER_DOWN, POWERING_DOWN, POWERED_DOWN, POWERING_UP, REBOOT_ISSUED,
REBOOT_REQUESTED, RESV, RESERVED, UNK, and UNKNOWN.
By default nodes in the specified state are reported whether
they are responding or not.
The --dead and --responding options may be
used to filter nodes by the corresponding flag.
-s , --summarize [#OPT_summarize_1](https://slurm.schedmd.com/sinfo.html) List only a partition state summary with no node state details.
This is ignored if the --format option is specified.
--usage [#OPT_usage](https://slurm.schedmd.com/sinfo.html) Print a brief message listing the sinfo options.
-v , --verbose [#OPT_verbose](https://slurm.schedmd.com/sinfo.html) Provide detailed event logging through program execution.
-V , --version [#OPT_version](https://slurm.schedmd.com/sinfo.html) Print version information and exit.
--yaml , --yaml = list , --yaml =< data_parser >[#OPT_yaml](https://slurm.schedmd.com/sinfo.html) Dump information as YAML using the default data_parser plugin or explicit
data_parser with parameters. All information is dumped, even if it would
normally not be. Sorting and formatting arguments passed to other options are
ignored; however, most filtering arguments are still used.
## OUTPUT FIELD DESCRIPTIONS[#SECTION_OUTPUT-FIELD-DESCRIPTIONS](https://slurm.schedmd.com/sinfo.html)
AVAIL [#OPT_AVAIL](https://slurm.schedmd.com/sinfo.html) Partition state. Can be either up , down , drain , or inact
(for INACTIVE). See the partition definition's State parameter in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for more information.
CPUS [#OPT_CPUS](https://slurm.schedmd.com/sinfo.html) Count of CPUs (processors) on these nodes.
S:C:T [#OPT_S:C:T](https://slurm.schedmd.com/sinfo.html) Count of sockets (S), cores (C), and threads (T) on these nodes.
SOCKETS [#OPT_SOCKETS](https://slurm.schedmd.com/sinfo.html) Count of sockets on these nodes.
CORES [#OPT_CORES](https://slurm.schedmd.com/sinfo.html) Count of cores on these nodes.
THREADS [#OPT_THREADS](https://slurm.schedmd.com/sinfo.html) Count of threads on these nodes.
GROUPS [#OPT_GROUPS](https://slurm.schedmd.com/sinfo.html) Resource allocations in this partition are restricted to the
named groups. all indicates that all groups may use
this partition.
JOB_SIZE [#OPT_JOB_SIZE](https://slurm.schedmd.com/sinfo.html) Minimum and maximum node count that can be allocated to any
user job. A single number indicates the minimum and maximum
node count are the same. infinite is used to identify
partitions without a maximum node count.
TIMELIMIT [#OPT_TIMELIMIT](https://slurm.schedmd.com/sinfo.html) Maximum time limit for any user job in
days-hours:minutes:seconds. infinite is used to identify
partitions without a job time limit.
MEMORY [#OPT_MEMORY](https://slurm.schedmd.com/sinfo.html) Size of real memory in megabytes on these nodes.
NODELIST [#OPT_NODELIST](https://slurm.schedmd.com/sinfo.html) Names of nodes associated with this particular configuration.
NODES [#OPT_NODES](https://slurm.schedmd.com/sinfo.html) Count of nodes with this particular configuration.
NODES(A/I) [#OPT_NODES(A/I)](https://slurm.schedmd.com/sinfo.html) Count of nodes with this particular configuration by node
state in the form "allocated/idle".
NODES(A/I/O/T) [#OPT_NODES(A/I/O/T)](https://slurm.schedmd.com/sinfo.html) Count of nodes with this particular configuration by node
state in the form "allocated/idle/other/total".
PARTITION [#OPT_PARTITION](https://slurm.schedmd.com/sinfo.html) Name of a partition. Note that the suffix "*" identifies the
default partition.
PORT [#OPT_PORT](https://slurm.schedmd.com/sinfo.html) Local TCP port used by slurmd on the node.
ROOT [#OPT_ROOT](https://slurm.schedmd.com/sinfo.html) Is the ability to allocate resources in this partition
restricted to user root, yes or no .
OVERSUBSCRIBE [#OPT_OVERSUBSCRIBE](https://slurm.schedmd.com/sinfo.html) Whether jobs allocated resources in this partition can/will oversubscribe
those compute resources (e.g. CPUs).
NO indicates resources are never oversubscribed.
EXCLUSIVE indicates whole nodes are dedicated to jobs
(equivalent to srun --exclusive option, may be used even
with select/cons_tres managing individual processors).
FORCE indicates resources are always available to be oversubscribed.
YES indicates resource may be oversubscribed, if requested by the job's
resource allocation.
NOTE : If OverSubscribe is set to FORCE or YES,
the OversubScribe value will be appended to the output.
STATE [#OPT_STATE](https://slurm.schedmd.com/sinfo.html) State of the nodes.
Possible states include: allocated, blocked, completing, down,
drained, draining, fail, failing, future, idle, maint, mixed,
perfctrs, planned, power_down, power_up, reserved, and unknown.
Their abbreviated forms are: alloc, block, comp, down, drain, drng,
fail, failg, futr, idle, maint, mix, npc, plnd, pow_dn, pow_up, resv,
and unk respectively.
NOTE : The suffix "*" identifies nodes that are presently
not responding.
TMP_DISK [#OPT_TMP_DISK](https://slurm.schedmd.com/sinfo.html) Size of temporary disk space in megabytes on these nodes.
## NODE STATE CODES[#SECTION_NODE-STATE-CODES](https://slurm.schedmd.com/sinfo.html)
Node state codes are shortened as required for the field size.
These node states may be followed by a special character to identify
state flags associated with the node.
The following node suffixes and states are used:
* [#OPT_*](https://slurm.schedmd.com/sinfo.html) The node is presently not responding and will not be allocated
any new work. If the node remains non-responsive, it will
be placed in the DOWN state (except in the case of
COMPLETING , DRAINED , DRAINING ,
FAIL , FAILING nodes).
~ [#OPT_~](https://slurm.schedmd.com/sinfo.html) The node is presently in powered off.
# [#OPT_#](https://slurm.schedmd.com/sinfo.html) The node is presently being powered up or configured.
! [#OPT_!](https://slurm.schedmd.com/sinfo.html) The node is pending power down.
% [#OPT_%](https://slurm.schedmd.com/sinfo.html) The node is presently being powered down.
$ [#OPT_$](https://slurm.schedmd.com/sinfo.html) The node is currently in a reservation with a flag value of "maintenance".
@ [#OPT_@](https://slurm.schedmd.com/sinfo.html) The node is pending reboot.
^ [#OPT_^](https://slurm.schedmd.com/sinfo.html) The node reboot was issued.
- [#OPT_-](https://slurm.schedmd.com/sinfo.html) The node is planned by the backfill scheduler for a higher priority job.
ALLOCATED [#OPT_ALLOCATED](https://slurm.schedmd.com/sinfo.html) The node has been allocated to one or more jobs.
ALLOCATED+ [#OPT_ALLOCATED+](https://slurm.schedmd.com/sinfo.html) The node is allocated to one or more active jobs plus
one or more jobs are in the process of COMPLETING.
BLOCKED [#OPT_BLOCKED](https://slurm.schedmd.com/sinfo.html) The node has been blocked by exclusive topo job.
COMPLETING [#OPT_COMPLETING](https://slurm.schedmd.com/sinfo.html) All jobs associated with this node are in the process of
COMPLETING. This node state will be removed when
all of the job's processes have terminated and the Slurm
epilog program (if any) has terminated. See the Epilog
parameter description in the [slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for
more information.
DOWN [#OPT_DOWN](https://slurm.schedmd.com/sinfo.html) The node is unavailable for use. Slurm can automatically
place nodes in this state if some failure occurs. System
administrators may also explicitly place nodes in this state. If
a node resumes normal operation, Slurm can automatically
return it to service. See the ReturnToService
and SlurmdTimeout parameter descriptions in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for more information.
DRAINED [#OPT_DRAINED](https://slurm.schedmd.com/sinfo.html) The node is unavailable for use per system administrator
request. See the update node command in the
[scontrol](https://slurm.schedmd.com/scontrol.html) (1) man page or the [slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page
for more information.
DRAINING [#OPT_DRAINING](https://slurm.schedmd.com/sinfo.html) The node is currently allocated a job, but will not be allocated
additional jobs. The node state will be changed to state
DRAINED when the last job on it completes. Nodes enter
this state per system administrator request. See the update
node command in the [scontrol](https://slurm.schedmd.com/scontrol.html) (1) man page or the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for more information.
FAIL [#OPT_FAIL](https://slurm.schedmd.com/sinfo.html) The node is expected to fail soon and is unavailable for
use per system administrator request.
See the update node command in the [scontrol](https://slurm.schedmd.com/scontrol.html) (1)
man page or the [slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for more information.
FAILING [#OPT_FAILING](https://slurm.schedmd.com/sinfo.html) The node is currently executing a job, but is expected to fail
soon and is unavailable for use per system administrator request.
See the update node command in the [scontrol](https://slurm.schedmd.com/scontrol.html) (1)
man page or the [slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for more information.
FUTURE [#OPT_FUTURE](https://slurm.schedmd.com/sinfo.html) The node is currently not fully configured, but expected to be available at
some point in the indefinite future for use.
IDLE [#OPT_IDLE](https://slurm.schedmd.com/sinfo.html) The node is not allocated to any jobs and is available for use.
INVAL [#OPT_INVAL](https://slurm.schedmd.com/sinfo.html) The node did not register correctly with the controller. This happens when
a node registers with less resources than configured in the slurm.conf file.
The node will clear from this state with a valid registration (i.e. a slurmd
restart is required).
MAINT [#OPT_MAINT](https://slurm.schedmd.com/sinfo.html) The node is currently in a reservation with a flag value of "maintenance".
REBOOT_ISSUED [#OPT_REBOOT_ISSUED](https://slurm.schedmd.com/sinfo.html) A reboot request has been sent to the agent configured to handle this request.
REBOOT_REQUESTED [#OPT_REBOOT_REQUESTED](https://slurm.schedmd.com/sinfo.html) A request to reboot this node has been made, but hasn't been handled yet.
MIXED [#OPT_MIXED](https://slurm.schedmd.com/sinfo.html) The node has some of its CPUs ALLOCATED while others are IDLE .
Or the node has a suspended job allocated to some of its TRES (e.g. memory).
PERFCTRS (NPC) [#OPT_PERFCTRS-(NPC)](https://slurm.schedmd.com/sinfo.html) Network Performance Counters associated with this node are in use, rendering
this node as not usable for any other jobs
PLANNED [#OPT_PLANNED](https://slurm.schedmd.com/sinfo.html) The node is planned by the backfill scheduler for a higher priority job.
POWER_DOWN [#OPT_POWER_DOWN](https://slurm.schedmd.com/sinfo.html) The node is pending power down.
POWERED_DOWN [#OPT_POWERED_DOWN](https://slurm.schedmd.com/sinfo.html) The node is currently powered down and not capable of running any jobs.
POWERING_DOWN [#OPT_POWERING_DOWN](https://slurm.schedmd.com/sinfo.html) The node is in the process of powering down and not capable of running any jobs.
POWERING_UP [#OPT_POWERING_UP](https://slurm.schedmd.com/sinfo.html) The node is in the process of being powered up.
RESERVED [#OPT_RESERVED](https://slurm.schedmd.com/sinfo.html) The node is in an advanced reservation and not generally available.
UNKNOWN [#OPT_UNKNOWN](https://slurm.schedmd.com/sinfo.html) The Slurm controller has just started and the node's state
has not yet been determined.
## PERFORMANCE[#SECTION_PERFORMANCE](https://slurm.schedmd.com/sinfo.html)
Executing sinfo sends a remote procedure call to slurmctld . If
enough calls from sinfo or other Slurm client commands that send remote
procedure calls to the slurmctld daemon come in at once, it can result in
a degradation of performance of the slurmctld daemon, possibly resulting
in a denial of service.
Do not run sinfo or other Slurm client commands that send remote procedure
calls to slurmctld from loops in shell scripts or other programs. Ensure
that programs limit calls to sinfo to the minimum necessary for the
information you are trying to gather.
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/sinfo.html)
Some sinfo options may
be set via environment variables. These environment variables,
along with their corresponding options, are listed below.
NOTE : Command line options will always override these settings.
SINFO_ALL [#OPT_SINFO_ALL](https://slurm.schedmd.com/sinfo.html) Same as -a, --all
SINFO_FEDERATION [#OPT_SINFO_FEDERATION](https://slurm.schedmd.com/sinfo.html) Same as --federation
SCONTROL_FUTURE [#OPT_SCONTROL_FUTURE](https://slurm.schedmd.com/sinfo.html) -F, --future
SINFO_FORMAT [#OPT_SINFO_FORMAT](https://slurm.schedmd.com/sinfo.html) Same as -o <output_format>, --format=<output_format>
SINFO_LOCAL [#OPT_SINFO_LOCAL](https://slurm.schedmd.com/sinfo.html) Same as --local
SINFO_PARTITION [#OPT_SINFO_PARTITION](https://slurm.schedmd.com/sinfo.html) Same as -p <partition>, --partition=<partition>
SINFO_SORT [#OPT_SINFO_SORT](https://slurm.schedmd.com/sinfo.html) Same as -S <sort>, --sort=<sort>
SLURM_CLUSTERS [#OPT_SLURM_CLUSTERS](https://slurm.schedmd.com/sinfo.html) Same as --clusters
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/sinfo.html) The location of the Slurm configuration file.
SLURM_DEBUG_FLAGS [#OPT_SLURM_DEBUG_FLAGS](https://slurm.schedmd.com/sinfo.html) Specify debug flags for sinfo to use. See DebugFlags in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for a full list of flags. The environment
variable takes precedence over the setting in the slurm.conf.
SLURM_JSON [#OPT_SLURM_JSON](https://slurm.schedmd.com/sinfo.html) Control JSON serialization:
compact [#OPT_compact](https://slurm.schedmd.com/sinfo.html) Output JSON as compact as possible.
pretty [#OPT_pretty](https://slurm.schedmd.com/sinfo.html) Output JSON in pretty format to make it more readable.
SLURM_TIME_FORMAT [#OPT_SLURM_TIME_FORMAT](https://slurm.schedmd.com/sinfo.html) Specify the format used to report time stamps. A value of standard , the
default value, generates output in the form "year-month-dateThour:minute:second".
A value of relative returns only "hour:minute:second" if the current day.
For other dates in the current year it prints the "hour:minute" preceded by
"Tomorr" (tomorrow), "Ystday" (yesterday), the name of the day for the coming
week (e.g. "Mon", "Tue", etc.), otherwise the date (e.g. "25 Apr").
For other years it returns a date month and year without a time (e.g.
"6 Jun 2012"). All of the time stamps use a 24 hour format.
A valid strftime() format can also be specified. For example, a value of
"%a %T" will report the day of the week and a time stamp (e.g. "Mon 12:34:56").
SLURM_YAML [#OPT_SLURM_YAML](https://slurm.schedmd.com/sinfo.html) Control YAML serialization:
compact Output YAML as compact as possible.[#OPT_compact_1](https://slurm.schedmd.com/sinfo.html)
pretty Output YAML in pretty format to make it more readable.[#OPT_pretty_1](https://slurm.schedmd.com/sinfo.html)
## EXAMPLES[#SECTION_EXAMPLES](https://slurm.schedmd.com/sinfo.html)
Report basic node and partition configurations:
```text
$ sinfo PARTITION AVAIL TIMELIMIT NODES STATE NODELIST batch up infinite 2 alloc adev[8-9] batch up infinite 6 idle adev[10-15] debug* up 30:00 8 idle adev[0-7]
```
Report partition summary information:
```text
$ sinfo -s PARTITION AVAIL TIMELIMIT NODES(A/I/O/T) NODELIST batch up infinite 2/6/0/8 adev[8-15] debug* up 30:00 0/8/0/8 adev[0-7]
```
Report more complete information about the partition debug:
```text
$ sinfo --long --partition=debug PARTITION AVAIL TIMELIMIT JOB_SIZE ROOT OVERSUBS GROUPS NODES STATE NODELIST debug* up 30:00 8 no no all 8 idle dev[0-7]
```
Report only those nodes that are in state DRAINED:
```text
$ sinfo --states=drained PARTITION AVAIL NODES TIMELIMIT STATE NODELIST debug* up 2 30:00 drain adev[6-7]
```
Report node-oriented information with details and exact matches:
```text
$ sinfo -Nel NODELIST NODES PARTITION STATE CPUS MEMORY TMP_DISK WEIGHT FEATURES REASON adev[0-1] 2 debug* idle 2 3448 38536 16 (null) (null) adev[2,4-7] 5 debug* idle 2 3384 38536 16 (null) (null) adev3 1 debug* idle 2 3394 38536 16 (null) (null) adev[8-9] 2 batch allocated 2 246 82306 16 (null) (null) adev[10-15] 6 batch idle 2 246 82306 16 (null) (null)
```
Report only down, drained and draining nodes and their reason field:
```text
$ sinfo -R REASON NODELIST Memory errors dev[0,5] Not Responding dev8
```
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/sinfo.html)
Copyright (C) 2002-2007 The Regents of the University of California.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/sinfo.html)
[scontrol](https://slurm.schedmd.com/scontrol.html) (1), [squeue](https://slurm.schedmd.com/squeue.html) (1),
slurm_load_ctl_conf (3), slurm_load_jobs (3),
slurm_load_node (3),
slurm_load_partitions (3),
slurm_reconfigure (3), slurm_shutdown (3),
slurm_update_job (3), slurm_update_node (3),
slurm_update_partition (3),
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5)
## Index
[NAME](https://slurm.schedmd.com/sinfo.html)
[SYNOPSIS](https://slurm.schedmd.com/sinfo.html)
[DESCRIPTION](https://slurm.schedmd.com/sinfo.html)
[OPTIONS](https://slurm.schedmd.com/sinfo.html)
[OUTPUT FIELD DESCRIPTIONS](https://slurm.schedmd.com/sinfo.html)
[NODE STATE CODES](https://slurm.schedmd.com/sinfo.html)
[PERFORMANCE](https://slurm.schedmd.com/sinfo.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/sinfo.html)
[EXAMPLES](https://slurm.schedmd.com/sinfo.html)
[COPYING](https://slurm.schedmd.com/sinfo.html)
[SEE ALSO](https://slurm.schedmd.com/sinfo.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
