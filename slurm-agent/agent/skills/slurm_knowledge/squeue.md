---
source_url: https://slurm.schedmd.com/squeue.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:15 UTC
title: "Slurm Workload Manager - squeue"
---

# squeue
Section: Slurm Commands (1)
Updated: Slurm Commands
[Index](https://slurm.schedmd.com/squeue.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/squeue.html)
squeue - view information about jobs located in the Slurm scheduling queue.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/squeue.html)
squeue [ OPTIONS ...]
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/squeue.html)
squeue is used to view job and job step information for jobs managed by
Slurm.
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/squeue.html)
-A , --account =< account_list >[#OPT_account](https://slurm.schedmd.com/squeue.html) Specify the accounts of the jobs to view. Accepts a comma separated
list of account names. This has no effect when listing job steps.
-a , --all [#OPT_all](https://slurm.schedmd.com/squeue.html) Display information about jobs and job steps in all partitions.
This causes information to be displayed about partitions that are configured as
hidden, partitions that are unavailable to a user's group, and federated jobs
that are in a "revoked" state.
-r , --array [#OPT_array](https://slurm.schedmd.com/squeue.html) Display one job array element per line.
Without this option, the display will be optimized for use with job arrays
(pending job array elements will be combined on one line of output with the
array index values printed using a regular expression).
-M , --clusters =< cluster_name >[#OPT_clusters](https://slurm.schedmd.com/squeue.html) Clusters to issue commands to. Multiple cluster names may be comma separated.
A value of ' all ' will query to run on all clusters.
Note that the slurmdbd must be up for this option to work properly, unless
running in a federation with either FederationParameters=fed_display
configured or the --federation option set.
This option implicitly sets the --local option.
--expand-patterns [#OPT_expand-patterns](https://slurm.schedmd.com/squeue.html) Expand any filename patterns from in StdOut , StdErr and StdIn .
Fields that map to a range of values will use the first value of the range. For
example "%t" for task id will be replaced by "0".
--federation [#OPT_federation](https://slurm.schedmd.com/squeue.html) Show jobs from the federation if a member of one.
-o , --format =< output_format >[#OPT_format](https://slurm.schedmd.com/squeue.html) Specify the information to be displayed, its size and position
(right or left justified).
Also see the -O , --Format =< output_format >
option described below (which supports less flexibility in formatting, but
supports access to all fields).
If the command is executed in a federated cluster environment and information
about more than one cluster is to be displayed and the -h, --noheader
option is used, then the cluster name will be displayed before the default
output formats shown below.
The default formats with various options are:
default [#OPT_default](https://slurm.schedmd.com/squeue.html) "%.18i %.9P %.8j %.8u %.2t %.10M %.6D %R"
-l, --long [#OPT_long](https://slurm.schedmd.com/squeue.html) "%.18i %.9P %.8j %.8u %.8T %.10M %.9l %.6D %R"
-s, --steps [#OPT_steps](https://slurm.schedmd.com/squeue.html) "%.15i %.8j %.9P %.8u %.9M %N"
The format of each field is "%[[.]size]type[suffix]"
size [#OPT_size](https://slurm.schedmd.com/squeue.html) Minimum field size. If no size is specified, whatever is needed to print the
information will be used.
. [#OPT_.](https://slurm.schedmd.com/squeue.html) Indicates the output should be right justified and size must be specified.
By default output is left justified.
suffix [#OPT_suffix](https://slurm.schedmd.com/squeue.html) Arbitrary string to append to the end of the field.
Note that many of these type specifications are valid
only for jobs while others are valid only for job steps.
Valid type specifications include:
%all [#OPT_%all](https://slurm.schedmd.com/squeue.html) Print all fields available for this data type with a vertical bar separating
each field.
%a [#OPT_%a](https://slurm.schedmd.com/squeue.html) Account associated with the job.
(Valid for jobs only)
%A [#OPT_%A](https://slurm.schedmd.com/squeue.html) Number of tasks created by a job step.
This reports the value of the srun --ntasks option.
(Valid for job steps only)
%A [#OPT_%A_1](https://slurm.schedmd.com/squeue.html) Job id.
This will have a unique value for each element of job arrays.
(Valid for jobs only)
%B [#OPT_%B](https://slurm.schedmd.com/squeue.html) Executing (batch) host. For an allocated session, this is the host on which
the session is executing (i.e. the node from which the srun or the
salloc command was executed). For a batch job, this is the node executing
the batch script. In the case of a typical Linux cluster, this would be the
compute node zero of the allocation.
%c [#OPT_%c](https://slurm.schedmd.com/squeue.html) Minimum number of CPUs (processors) per node requested by the job.
This reports the value of the srun --mincpus option with a
default value of zero.
(Valid for jobs only)
%C [#OPT_%C](https://slurm.schedmd.com/squeue.html) Number of CPUs (processors) requested by the job or allocated to
it if already running. As a job is completing this number will
reflect the current number of CPUs allocated.
(Valid for jobs only)
%d [#OPT_%d](https://slurm.schedmd.com/squeue.html) Minimum size of temporary disk space (in MB) requested by the job.
(Valid for jobs only)
%D [#OPT_%D](https://slurm.schedmd.com/squeue.html) Number of nodes allocated to the job or the minimum number of nodes
required by a pending job. The actual number of nodes allocated to a pending
job may exceed this number if the job specified a node range count (e.g.
minimum and maximum node counts) or the job specifies a processor
count instead of a node count. As a job is completing this number will reflect
the current number of nodes allocated.
(Valid for jobs only)
%e [#OPT_%e](https://slurm.schedmd.com/squeue.html) Time at which the job ended or is expected to end (based upon its time limit).
(Valid for jobs only)
%E [#OPT_%E](https://slurm.schedmd.com/squeue.html) Job dependencies remaining. This job will not begin execution until these
dependent jobs complete. In the case of a job that can not run due to job
dependencies never being satisfied, the full original job dependency
specification will be reported. Once a dependency is satisfied, it is
removed from the job. A value of NULL implies this job has no
dependencies.
(Valid for jobs only)
%f [#OPT_%f](https://slurm.schedmd.com/squeue.html) Features required by the job.
(Valid for jobs only)
%F [#OPT_%F](https://slurm.schedmd.com/squeue.html) Job array's job ID. This is the base job ID.
For non-array jobs, this is the job ID.
(Valid for jobs only)
%g [#OPT_%g](https://slurm.schedmd.com/squeue.html) Group name of the job.
(Valid for jobs only)
%G [#OPT_%G](https://slurm.schedmd.com/squeue.html) Group ID of the job.
(Valid for jobs only)
%h [#OPT_%h](https://slurm.schedmd.com/squeue.html) Can the compute resources allocated to the job be over subscribed by other jobs.
The resources to be over subscribed can be nodes, sockets, cores, or
hyperthreads depending upon configuration.
The value will be "YES" if the job was submitted with the oversubscribe option
or the partition is configured with OverSubscribe=Force,
"NO" if the job requires exclusive node access,
"USER" if the allocated compute nodes are dedicated to a single user,
"MCS" if the allocated compute nodes are dedicated to a single security class
(See MCSPlugin and MCSParameters configuration parameters for more information),
"OK" otherwise (typically allocated dedicated CPUs),
(Valid for jobs only)
%H [#OPT_%H](https://slurm.schedmd.com/squeue.html) Number of sockets per node requested by the job.
This reports the value of the srun --sockets-per-node option.
When --sockets-per-node has not been set, "*" is displayed.
(Valid for jobs only)
%i [#OPT_%i](https://slurm.schedmd.com/squeue.html) Job or job step id.
In the case of job arrays, the job ID format will be of the form
"<base_job_id>_<index>".
By default, the job array index field size will be limited to 64 bytes.
Use the environment variable SLURM_BITSTR_LEN to specify larger field sizes.
(Valid for jobs and job steps)
In the case of heterogeneous job allocations, the job ID format will be of the
form "#+#" where the first number is the "heterogeneous job leader" and the
second number the zero origin offset for each component of the job.
%I [#OPT_%I](https://slurm.schedmd.com/squeue.html) Number of cores per socket requested by the job.
This reports the value of the srun --cores-per-socket option.
When --cores-per-socket has not been set, "*" is displayed.
(Valid for jobs only)
%j [#OPT_%j](https://slurm.schedmd.com/squeue.html) Job or job step name.
(Valid for jobs and job steps)
%J [#OPT_%J](https://slurm.schedmd.com/squeue.html) Number of threads per core requested by the job.
This reports the value of the srun --threads-per-core option.
When --threads-per-core has not been set, "*" is displayed.
(Valid for jobs only)
%k [#OPT_%k](https://slurm.schedmd.com/squeue.html) Comment associated with the job.
(Valid for jobs only)
%K [#OPT_%K](https://slurm.schedmd.com/squeue.html) Job array index.
By default, this field size will be limited to 64 bytes.
Use the environment variable SLURM_BITSTR_LEN to specify larger field sizes.
(Valid for jobs only)
%l [#OPT_%l](https://slurm.schedmd.com/squeue.html) Time limit of the job or job step in days-hours:minutes:seconds.
The value may be "NOT_SET" if not yet established or "UNLIMITED" for no limit.
(Valid for jobs and job steps)
%L [#OPT_%L](https://slurm.schedmd.com/squeue.html) Time left for the job to execute in days-hours:minutes:seconds.
This value is calculated by subtracting the job's time used from its time
limit.
The value may be "NOT_SET" if not yet established or "UNLIMITED" for no limit.
(Valid for jobs only)
%m [#OPT_%m](https://slurm.schedmd.com/squeue.html) Minimum size of memory (in MB) requested by the job.
(Valid for jobs only)
If memory was request per CPU, or per GPU the value is shown
with the assumption that at least one CPU, GPU will be allocated
respectively.
%M [#OPT_%M](https://slurm.schedmd.com/squeue.html) Time used by the job or job step in days-hours:minutes:seconds.
The days and hours are printed only as needed.
For job steps this field shows the elapsed time since execution began
and thus will be inaccurate for job steps which have been suspended.
Clock skew between nodes in the cluster will cause the time to be inaccurate.
If the time is obviously wrong (e.g. negative), it displays as "INVALID".
(Valid for jobs and job steps)
%n [#OPT_%n](https://slurm.schedmd.com/squeue.html) List of node names explicitly requested by the job.
(Valid for jobs only)
%N [#OPT_%N](https://slurm.schedmd.com/squeue.html) List of nodes allocated to the job or job step. In the case of a
COMPLETING job, the list of nodes will comprise only those
nodes that have not yet been returned to service.
(Valid for jobs and job steps)
%o [#OPT_%o](https://slurm.schedmd.com/squeue.html) The command to be executed.
%O [#OPT_%O](https://slurm.schedmd.com/squeue.html) Are contiguous nodes requested by the job.
(Valid for jobs only)
%p [#OPT_%p](https://slurm.schedmd.com/squeue.html) Priority of the job (converted to a floating point number between 0.0 and 1.0).
Also see %Q .
(Valid for jobs only)
%P [#OPT_%P](https://slurm.schedmd.com/squeue.html) Partition of the job or job step.
(Valid for jobs and job steps)
%q [#OPT_%q](https://slurm.schedmd.com/squeue.html) Quality of service associated with the job.
(Valid for jobs only)
%Q [#OPT_%Q](https://slurm.schedmd.com/squeue.html) Priority of the job (generally a very large unsigned integer).
Also see %p .
(Valid for jobs only)
%r [#OPT_%r](https://slurm.schedmd.com/squeue.html) The reason a job is in its current state.
See the JOB REASON CODES section below for more information.
(Valid for jobs only)
%R [#OPT_%R](https://slurm.schedmd.com/squeue.html) For pending jobs: the reason a job has not been started by the scheduler
is printed within parenthesis.
For terminated jobs with failure: an explanation as to why the
job failed is printed within parenthesis.
For all other job states: the list of allocate nodes.
See the JOB REASON CODES section below for more information.
(Valid for jobs only)
%s [#OPT_%s](https://slurm.schedmd.com/squeue.html) SLUID
(Valid for jobs only)
%S [#OPT_%S](https://slurm.schedmd.com/squeue.html) Actual or expected start time of the job or job step.
(Valid for jobs and job steps)
%t [#OPT_%t](https://slurm.schedmd.com/squeue.html) Job state in compact form.
See the JOB STATE CODES section below for a list of possible states.
(Valid for jobs only)
%T [#OPT_%T](https://slurm.schedmd.com/squeue.html) Job state in extended form.
See the JOB STATE CODES section below for a list of possible states.
(Valid for jobs only)
%u [#OPT_%u](https://slurm.schedmd.com/squeue.html) User name for a job or job step.
(Valid for jobs and job steps)
%U [#OPT_%U](https://slurm.schedmd.com/squeue.html) User ID for a job or job step.
(Valid for jobs and job steps)
%v [#OPT_%v](https://slurm.schedmd.com/squeue.html) Reservation for the job.
(Valid for jobs only)
%V [#OPT_%V](https://slurm.schedmd.com/squeue.html) The job's submission time.
%w [#OPT_%w](https://slurm.schedmd.com/squeue.html) Workload Characterization Key (wckey).
(Valid for jobs only)
%W [#OPT_%W](https://slurm.schedmd.com/squeue.html) Licenses requested by the job.
(Valid for jobs only)
%x [#OPT_%x](https://slurm.schedmd.com/squeue.html) List of node names explicitly excluded by the job.
(Valid for jobs only)
%X [#OPT_%X](https://slurm.schedmd.com/squeue.html) Count of cores reserved on each node for system use (core specialization).
(Valid for jobs only)
%y [#OPT_%y](https://slurm.schedmd.com/squeue.html) Nice value (adjustment to a job's scheduling priority).
(Valid for jobs only)
%Y [#OPT_%Y](https://slurm.schedmd.com/squeue.html) For pending jobs, a list of the nodes expected to be used when the job is
started.
%z [#OPT_%z](https://slurm.schedmd.com/squeue.html) Number of requested sockets, cores, and threads (S:C:T) per node for the job.
When (S:C:T) has not been set, "*" is displayed.
(Valid for jobs only)
%Z [#OPT_%Z](https://slurm.schedmd.com/squeue.html) The job's working directory.
-O , --Format =< output_format >[#OPT_Format](https://slurm.schedmd.com/squeue.html) Specify the information to be displayed.
Also see the -o , --format =< output_format >
option described above (which supports greater flexibility in formatting, but
does not support access to all fields because we ran out of letters).
Requests a comma separated list of job information to be displayed.
The format of each field is "type[:[.][size][suffix]]"
size [#OPT_size_1](https://slurm.schedmd.com/squeue.html) Minimum field size. If no size is specified, 20 characters will be allocated
to print the information.
. [#OPT_._1](https://slurm.schedmd.com/squeue.html) Indicates the output should be right justified and size must be specified.
By default output is left justified.
suffix [#OPT_suffix_1](https://slurm.schedmd.com/squeue.html) Arbitrary string to append to the end of the field.
Note that many of these type specifications are valid
only for jobs while others are valid only for job steps.
Valid type specifications include:
Account [#OPT_Account](https://slurm.schedmd.com/squeue.html) Print the account associated with the job.
(Valid for jobs only)
AccrueTime [#OPT_AccrueTime](https://slurm.schedmd.com/squeue.html) Print the accrue time associated with the job.
(Valid for jobs only)
admin_comment [#OPT_admin_comment](https://slurm.schedmd.com/squeue.html) Administrator comment associated with the job.
(Valid for jobs only)
AllocNodes [#OPT_AllocNodes](https://slurm.schedmd.com/squeue.html) Print the nodes allocated to the job.
(Valid for jobs only)
AllocSID [#OPT_AllocSID](https://slurm.schedmd.com/squeue.html) Print the session ID used to submit the job.
(Valid for jobs only)
ArrayJobID [#OPT_ArrayJobID](https://slurm.schedmd.com/squeue.html) Prints the job ID of the job array.
(Valid for jobs and job steps)
ArrayTaskID [#OPT_ArrayTaskID](https://slurm.schedmd.com/squeue.html) Prints the task ID of the job array.
(Valid for jobs and job steps)
AssocID [#OPT_AssocID](https://slurm.schedmd.com/squeue.html) Prints the ID of the job association.
(Valid for jobs only)
BatchFlag [#OPT_BatchFlag](https://slurm.schedmd.com/squeue.html) Prints whether the batch flag has been set.
(Valid for jobs only)
BatchHost [#OPT_BatchHost](https://slurm.schedmd.com/squeue.html) Executing (batch) host. For an allocated session, this is the host on which
the session is executing (i.e. the node from which the srun or the
salloc command was executed). For a batch job, this is the node executing
the batch script. In the case of a typical Linux cluster, this would be the
compute node zero of the allocation.
(Valid for jobs only)
BoardsPerNode [#OPT_BoardsPerNode](https://slurm.schedmd.com/squeue.html) Prints the number of boards per node allocated to the job.
(Valid for jobs only)
BurstBuffer [#OPT_BurstBuffer](https://slurm.schedmd.com/squeue.html) Burst Buffer specification
(Valid for jobs only)
BurstBufferState [#OPT_BurstBufferState](https://slurm.schedmd.com/squeue.html) Burst Buffer state
(Valid for jobs only)
Cluster [#OPT_Cluster](https://slurm.schedmd.com/squeue.html) Name of the cluster that is running the job or job step.
ClusterFeature [#OPT_ClusterFeature](https://slurm.schedmd.com/squeue.html) Cluster features required by the job.
(Valid for jobs only)
Command [#OPT_Command](https://slurm.schedmd.com/squeue.html) The command to be executed.
(Valid for jobs only)
Comment [#OPT_Comment](https://slurm.schedmd.com/squeue.html) Comment associated with the job.
(Valid for jobs only)
Contiguous [#OPT_Contiguous](https://slurm.schedmd.com/squeue.html) Are contiguous nodes requested by the job.
(Valid for jobs only)
Container [#OPT_Container](https://slurm.schedmd.com/squeue.html) OCI container bundle path.
ContainerID [#OPT_ContainerID](https://slurm.schedmd.com/squeue.html) OCI container assigned ID.
Cores [#OPT_Cores](https://slurm.schedmd.com/squeue.html) Number of cores per socket requested by the job.
This reports the value of the srun --cores-per-socket option.
When --cores-per-socket has not been set, "*" is displayed.
(Valid for jobs only)
CoreSpec [#OPT_CoreSpec](https://slurm.schedmd.com/squeue.html) Count of cores reserved on each node for system use (core specialization).
(Valid for jobs only)
CPUFreq [#OPT_CPUFreq](https://slurm.schedmd.com/squeue.html) Prints the frequency of the allocated CPUs.
(Valid for job steps only)
cpus-per-task [#OPT_cpus-per-task](https://slurm.schedmd.com/squeue.html) Prints the number of CPUs per tasks allocated to the job.
(Valid for jobs only)
cpus-per-tres [#OPT_cpus-per-tres](https://slurm.schedmd.com/squeue.html) Print the memory required per trackable resources allocated to the job or job step.
CronJob [#OPT_CronJob](https://slurm.schedmd.com/squeue.html) Print Yes/No depending on whether the job has been generated by scrontab or not.
(Valid for jobs only)
Deadline [#OPT_Deadline](https://slurm.schedmd.com/squeue.html) Prints the deadline affected to the job
(Valid for jobs only)
DelayBoot [#OPT_DelayBoot](https://slurm.schedmd.com/squeue.html) Delay boot time.
(Valid for jobs only)
Dependency [#OPT_Dependency](https://slurm.schedmd.com/squeue.html) Job dependencies remaining. This job will not begin execution until these
dependent jobs complete. In the case of a job that can not run due to job
dependencies never being satisfied, the full original job dependency
specification will be reported. Once a dependency is satisfied, it is
removed from the job. A value of NULL implies this job has no
dependencies.
(Valid for jobs only)
DerivedEC [#OPT_DerivedEC](https://slurm.schedmd.com/squeue.html) The highest exit code returned by the job's job steps (srun invocations).
Following the colon is the signal that caused the process to terminate if
it was terminated by a signal.
(Valid for jobs only)
EligibleTime [#OPT_EligibleTime](https://slurm.schedmd.com/squeue.html) Time the job is eligible for running.
(Valid for jobs only)
EndTime [#OPT_EndTime](https://slurm.schedmd.com/squeue.html) The time of job termination, actual or expected.
(Valid for jobs only)
ExcNodes [#OPT_ExcNodes](https://slurm.schedmd.com/squeue.html) The nodes requested to be excluded when allocating this job.
(Valid for jobs only)
exit_code [#OPT_exit_code](https://slurm.schedmd.com/squeue.html) The exit code returned by the job, typically as set by the exit() function.
Following the colon is the signal that caused the process to terminate if it was
terminated by a signal.
(Valid for jobs only)
Feature [#OPT_Feature](https://slurm.schedmd.com/squeue.html) Features required by the job.
(Valid for jobs only)
GroupID [#OPT_GroupID](https://slurm.schedmd.com/squeue.html) Group ID of the job.
(Valid for jobs only)
GroupName [#OPT_GroupName](https://slurm.schedmd.com/squeue.html) Group name of the job.
(Valid for jobs only)
HetJobID [#OPT_HetJobID](https://slurm.schedmd.com/squeue.html) Job ID of the heterogeneous job leader.
HetJobIDSet [#OPT_HetJobIDSet](https://slurm.schedmd.com/squeue.html) Expression identifying all components job IDs within a heterogeneous job.
HetJobOffset [#OPT_HetJobOffset](https://slurm.schedmd.com/squeue.html) Zero origin offset within a collection of heterogeneous job components.
JobArrayID [#OPT_JobArrayID](https://slurm.schedmd.com/squeue.html) Job array's job ID. This is the base job ID.
For non-array jobs, this is the job ID.
(Valid for jobs only)
JobID [#OPT_JobID](https://slurm.schedmd.com/squeue.html) Job ID.
This will have a unique value for each element of job arrays and each
component of heterogeneous jobs.
(Valid for jobs only)
LastSchedEval [#OPT_LastSchedEval](https://slurm.schedmd.com/squeue.html) Prints the last time the job was evaluated for scheduling.
(Valid for jobs only)
Licenses [#OPT_Licenses](https://slurm.schedmd.com/squeue.html) Licenses requested by the job.
(Valid for jobs only)
LicensesAlloc [#OPT_LicensesAlloc](https://slurm.schedmd.com/squeue.html) Licenses allocated to the job.
(Valid for jobs only)
MaxCPUs [#OPT_MaxCPUs](https://slurm.schedmd.com/squeue.html) Prints the max number of CPUs allocated to the job.
(Valid for jobs only)
MaxNodes [#OPT_MaxNodes](https://slurm.schedmd.com/squeue.html) Prints the max number of nodes allocated to the job.
(Valid for jobs only)
MCSLabel [#OPT_MCSLabel](https://slurm.schedmd.com/squeue.html) Prints the MCS_label of the job.
(Valid for jobs only)
mem-per-tres [#OPT_mem-per-tres](https://slurm.schedmd.com/squeue.html) Print the memory (in MB) required per trackable resources allocated to the job
or job step.
MinCpus [#OPT_MinCpus](https://slurm.schedmd.com/squeue.html) Minimum number of CPUs (processors) per node requested by the job.
This reports the value of the srun --mincpus option with a
default value of zero.
(Valid for jobs only)
MinMemory [#OPT_MinMemory](https://slurm.schedmd.com/squeue.html) Minimum size of memory (in MB) requested by the job.
(Valid for jobs only)
MinTime [#OPT_MinTime](https://slurm.schedmd.com/squeue.html) Minimum time limit of the job
(Valid for jobs only)
MinTmpDisk [#OPT_MinTmpDisk](https://slurm.schedmd.com/squeue.html) Minimum size of temporary disk space (in MB) requested by the job.
(Valid for jobs only)
Name [#OPT_Name](https://slurm.schedmd.com/squeue.html) Job or job step name.
(Valid for jobs and job steps)
Network [#OPT_Network](https://slurm.schedmd.com/squeue.html) The network that the job is running on.
(Valid for jobs and job steps)
Nice [#OPT_Nice](https://slurm.schedmd.com/squeue.html) Nice value (adjustment to a job's scheduling priority).
(Valid for jobs only)
NodeList [#OPT_NodeList](https://slurm.schedmd.com/squeue.html) List of nodes allocated to the job or job step. In the case of a
COMPLETING job, the list of nodes will comprise only those
nodes that have not yet been returned to service.
(Valid for jobs only)
Nodes [#OPT_Nodes](https://slurm.schedmd.com/squeue.html) List of nodes allocated to the job or job step. In the case of a
COMPLETING job, the list of nodes will comprise only those
nodes that have not yet been returned to service.
(Valid job steps only)
NTPerBoard [#OPT_NTPerBoard](https://slurm.schedmd.com/squeue.html) The number of tasks per board allocated to the job.
(Valid for jobs only)
NTPerCore [#OPT_NTPerCore](https://slurm.schedmd.com/squeue.html) The number of tasks per core allocated to the job.
(Valid for jobs only)
NTPerNode [#OPT_NTPerNode](https://slurm.schedmd.com/squeue.html) The number of tasks per node allocated to the job.
(Valid for jobs only)
NTPerSocket [#OPT_NTPerSocket](https://slurm.schedmd.com/squeue.html) The number of tasks per socket allocated to the job.
(Valid for jobs only)
NumCPUs [#OPT_NumCPUs](https://slurm.schedmd.com/squeue.html) Number of CPUs (processors) requested by the job or allocated to
it if already running. As a job is completing, this number will
reflect the current number of CPUs allocated.
(Valid for jobs and job steps)
NumNodes [#OPT_NumNodes](https://slurm.schedmd.com/squeue.html) Number of nodes allocated to the job or the minimum number of nodes
required by a pending job. The actual number of nodes allocated to a pending
job may exceed this number if the job specified a node range count (e.g.
minimum and maximum node counts) or the job specifies a processor
count instead of a node count. As a job is completing this number will reflect
the current number of nodes allocated.
(Valid for jobs only)
NumTasks [#OPT_NumTasks](https://slurm.schedmd.com/squeue.html) Number of tasks requested by a job or job step.
This reports the value of the --ntasks option.
(Valid for jobs and job steps)
Origin [#OPT_Origin](https://slurm.schedmd.com/squeue.html) Cluster name where federated job originated from.
(Valid for federated jobs only)
OriginRaw [#OPT_OriginRaw](https://slurm.schedmd.com/squeue.html) Cluster ID where federated job originated from.
(Valid for federated jobs only)
OverSubscribe [#OPT_OverSubscribe](https://slurm.schedmd.com/squeue.html) Can the compute resources allocated to the job be over subscribed by other jobs.
The resources to be over subscribed can be nodes, sockets, cores, or
hyperthreads depending upon configuration.
The value will be "YES" if the job was submitted with the oversubscribe option
or the partition is configured with OverSubscribe=Force,
"NO" if the job requires exclusive node access,
"USER" if the allocated compute nodes are dedicated to a single user,
"MCS" if the allocated compute nodes are dedicated to a single security class
(See MCSPlugin and MCSParameters configuration parameters for more information),
"OK" otherwise (typically allocated dedicated CPUs),
(Valid for jobs only)
Partition [#OPT_Partition](https://slurm.schedmd.com/squeue.html) Partition of the job or job step.
(Valid for jobs and job steps)
PendingTime [#OPT_PendingTime](https://slurm.schedmd.com/squeue.html) The time (in seconds) between start time and submit time of the job.
If the job has not started yet, then the time (in seconds) between
now and the submit time of the job.
(Valid for jobs only)
PreemptTime [#OPT_PreemptTime](https://slurm.schedmd.com/squeue.html) The preempt time for the job.
(Valid for jobs only)
Prefer [#OPT_Prefer](https://slurm.schedmd.com/squeue.html) The preferred features of a pending job.
(Valid for jobs only)
Priority [#OPT_Priority](https://slurm.schedmd.com/squeue.html) Priority of the job (converted to a floating point number between 0.0 and 1.0).
Also see prioritylong .
(Valid for jobs only)
PriorityLong [#OPT_PriorityLong](https://slurm.schedmd.com/squeue.html) Priority of the job (generally a very large unsigned integer).
Also see priority .
(Valid for jobs only)
Profile [#OPT_Profile](https://slurm.schedmd.com/squeue.html) Profile of the job.
(Valid for jobs only)
QOS [#OPT_QOS](https://slurm.schedmd.com/squeue.html) Quality of service associated with the job.
(Valid for jobs only)
Reason [#OPT_Reason](https://slurm.schedmd.com/squeue.html) The reason a job is in its current state.
See the JOB REASON CODES section below for more information.
(Valid for jobs only)
ReasonList [#OPT_ReasonList](https://slurm.schedmd.com/squeue.html) For pending jobs: the reason a job is waiting for execution
is printed within parenthesis.
For terminated jobs with failure: an explanation as to why the
job failed is printed within parenthesis.
For all other job states: the list of allocate nodes.
See the JOB REASON CODES section below for more information.
(Valid for jobs only)
Reboot [#OPT_Reboot](https://slurm.schedmd.com/squeue.html) Indicates if the allocated nodes should be rebooted before starting the job.
(Valid on jobs only)
ReqNodes [#OPT_ReqNodes](https://slurm.schedmd.com/squeue.html) List of node names explicitly requested by the job.
(Valid for jobs only)
ReqSwitch [#OPT_ReqSwitch](https://slurm.schedmd.com/squeue.html) The max number of requested switches by for the job.
(Valid for jobs only)
Requeue [#OPT_Requeue](https://slurm.schedmd.com/squeue.html) Prints whether the job will be requeued on failure.
(Valid for jobs only)
Reservation [#OPT_Reservation](https://slurm.schedmd.com/squeue.html) Reservation for the job.
(Valid for jobs only)
ResizeTime [#OPT_ResizeTime](https://slurm.schedmd.com/squeue.html) The amount of time changed for the job to run.
(Valid for jobs only)
RestartCnt [#OPT_RestartCnt](https://slurm.schedmd.com/squeue.html) The number of restarts for the job.
(Valid for jobs only)
ResvPort [#OPT_ResvPort](https://slurm.schedmd.com/squeue.html) Reserved ports of the job.
(Valid for job steps only)
SchedNodes [#OPT_SchedNodes](https://slurm.schedmd.com/squeue.html) For pending jobs, a list of the nodes expected to be used when the job is
started.
(Valid for jobs only)
SCT [#OPT_SCT](https://slurm.schedmd.com/squeue.html) Number of requested sockets, cores, and threads (S:C:T) per node for the job.
When (S:C:T) has not been set, "*" is displayed.
(Valid for jobs only)
SegmentSize [#OPT_SegmentSize](https://slurm.schedmd.com/squeue.html) Segment size requested by the job.
(Valid for jobs only)
SiblingsActive [#OPT_SiblingsActive](https://slurm.schedmd.com/squeue.html) Cluster names of where federated sibling jobs exist.
(Valid for federated jobs only)
SiblingsActiveRaw [#OPT_SiblingsActiveRaw](https://slurm.schedmd.com/squeue.html) Cluster IDs of where federated sibling jobs exist.
(Valid for federated jobs only)
SiblingsViable [#OPT_SiblingsViable](https://slurm.schedmd.com/squeue.html) Cluster names of where federated sibling jobs are viable to run.
(Valid for federated jobs only)
SiblingsViableRaw [#OPT_SiblingsViableRaw](https://slurm.schedmd.com/squeue.html) Cluster IDs of where federated sibling jobs viable to run.
(Valid for federated jobs only)
Sockets [#OPT_Sockets](https://slurm.schedmd.com/squeue.html) Number of sockets per node requested by the job.
This reports the value of the srun --sockets-per-node option.
When --sockets-per-node has not been set, "*" is displayed.
(Valid for jobs only)
SPerBoard [#OPT_SPerBoard](https://slurm.schedmd.com/squeue.html) Number of sockets per board allocated to the job.
(Valid for jobs only)
StartTime [#OPT_StartTime](https://slurm.schedmd.com/squeue.html) Actual or expected start time of the job or job step.
(Valid for jobs and job steps)
State [#OPT_State](https://slurm.schedmd.com/squeue.html) Job state in extended form.
See the JOB STATE CODES section below for a list of possible states.
(Valid for jobs only)
StateCompact [#OPT_StateCompact](https://slurm.schedmd.com/squeue.html) Job state in compact form.
See the JOB STATE CODES section below for a list of possible states.
(Valid for jobs only)
STDERR [#OPT_STDERR](https://slurm.schedmd.com/squeue.html) The directory for standard error to output to.
(Valid for jobs and steps)
STDIN [#OPT_STDIN](https://slurm.schedmd.com/squeue.html) The directory for standard in.
(Valid for jobs and steps)
STDOUT [#OPT_STDOUT](https://slurm.schedmd.com/squeue.html) The directory for standard out to output to.
(Valid for jobs and steps)
StepID [#OPT_StepID](https://slurm.schedmd.com/squeue.html) Job or job step ID.
In the case of job arrays, the job ID format will be of the form
"<base_job_id>_<index>".
(Valid for job steps only)
StepName [#OPT_StepName](https://slurm.schedmd.com/squeue.html) Job step name.
(Valid for job steps only)
StepState [#OPT_StepState](https://slurm.schedmd.com/squeue.html) The state of the job step.
(Valid for job steps only)
SubmitTime [#OPT_SubmitTime](https://slurm.schedmd.com/squeue.html) The time that the job was submitted at.
(Valid for jobs only)
system_comment [#OPT_system_comment](https://slurm.schedmd.com/squeue.html) System comment associated with the job.
(Valid for jobs only)
Threads [#OPT_Threads](https://slurm.schedmd.com/squeue.html) Number of threads per core requested by the job.
This reports the value of the srun --threads-per-core option.
When --threads-per-core has not been set, "*" is displayed.
(Valid for jobs only)
TimeLeft [#OPT_TimeLeft](https://slurm.schedmd.com/squeue.html) Time left for the job to execute in days-hours:minutes:seconds.
This value is calculated by subtracting the job's time used from its time
limit.
The value may be "NOT_SET" if not yet established or "UNLIMITED" for no limit.
(Valid for jobs only)
TimeLimit [#OPT_TimeLimit](https://slurm.schedmd.com/squeue.html) Timelimit for the job or job step.
(Valid for jobs and job steps)
TimeUsed [#OPT_TimeUsed](https://slurm.schedmd.com/squeue.html) Time used by the job or job step in days-hours:minutes:seconds.
The days and hours are printed only as needed.
For job steps this field shows the elapsed time since execution began
and thus will be inaccurate for job steps which have been suspended.
Clock skew between nodes in the cluster will cause the time to be inaccurate.
If the time is obviously wrong (e.g. negative), it displays as "INVALID".
(Valid for jobs and job steps)
tres-alloc [#OPT_tres-alloc](https://slurm.schedmd.com/squeue.html) Print the trackable resources allocated to the job if running.
If not running, then print the trackable resources requested by the job.
tres-bind [#OPT_tres-bind](https://slurm.schedmd.com/squeue.html) Print the trackable resources task binding requested by the job or job step.
tres-freq [#OPT_tres-freq](https://slurm.schedmd.com/squeue.html) Print the trackable resources frequencies requested by the job or job step.
tres-per-job [#OPT_tres-per-job](https://slurm.schedmd.com/squeue.html) Print the trackable resources requested by the job.
tres-per-node [#OPT_tres-per-node](https://slurm.schedmd.com/squeue.html) Print the trackable resources per node requested by the job or job step.
tres-per-socket [#OPT_tres-per-socket](https://slurm.schedmd.com/squeue.html) Print the trackable resources per socket requested by the job or job step.
tres-per-step [#OPT_tres-per-step](https://slurm.schedmd.com/squeue.html) Print the trackable resources requested by the job step.
tres-per-task [#OPT_tres-per-task](https://slurm.schedmd.com/squeue.html) Print the trackable resources per task requested by the job or job step.
UserID [#OPT_UserID](https://slurm.schedmd.com/squeue.html) User ID for a job or job step.
(Valid for jobs and job steps)
UserName [#OPT_UserName](https://slurm.schedmd.com/squeue.html) User name for a job or job step.
(Valid for jobs and job steps)
Wait4Switch [#OPT_Wait4Switch](https://slurm.schedmd.com/squeue.html) The amount of time to wait for the desired number of switches.
(Valid for jobs only)
WCKey [#OPT_WCKey](https://slurm.schedmd.com/squeue.html) Workload Characterization Key (wckey).
(Valid for jobs only)
WorkDir [#OPT_WorkDir](https://slurm.schedmd.com/squeue.html) The job's working directory.
(Valid for jobs only)
--help [#OPT_help](https://slurm.schedmd.com/squeue.html) Print a help message describing all options squeue .
--hide [#OPT_hide](https://slurm.schedmd.com/squeue.html) Do not display information about jobs and job steps in all partitions. By default,
information about partitions that are configured as hidden or are not available
to the user's group will not be displayed (i.e. this is the default behavior).
-i , --iterate =< seconds >[#OPT_iterate](https://slurm.schedmd.com/squeue.html) Repeatedly gather and report the requested information at the interval
specified (in seconds).
By default, prints a time stamp with the header.
-j , --jobs [=< job_id_list >][#OPT_jobs](https://slurm.schedmd.com/squeue.html) Specify a comma separated list of job IDs to display. Defaults to all jobs.
The --jobs =< job_id_list > option may be used in conjunction with
the --steps option to print step information about specific jobs.
Note: If a list of job IDs is provided, the jobs are displayed even if
they are on hidden partitions. Since this option's argument is optional,
for proper parsing the single letter option must be followed immediately
with the value and not include a space between them. For example "-j1008"
and not "-j 1008".
The job ID format is "job_id[_array_id]".
Performance of the command can be measurably improved for systems with large
numbers of jobs when a single job ID is specified.
By default, this field size will be limited to 64 bytes.
Use the environment variable SLURM_BITSTR_LEN to specify larger field sizes.
--json , --json = list , --json =< data_parser >[#OPT_json](https://slurm.schedmd.com/squeue.html) Dump information as JSON using the default data_parser plugin or explicit
data_parser with parameters. All information is dumped, even if it would
normally not be. Sorting and formatting arguments passed to other options are
ignored; however, most filtering arguments are still used.
-L , --licenses =< license_list >[#OPT_licenses](https://slurm.schedmd.com/squeue.html) Request jobs requesting or using one or more of the named licenses.
The license list consists of a comma separated list of license names.
--local [#OPT_local](https://slurm.schedmd.com/squeue.html) Show only jobs local to this cluster. Ignore other clusters in this federation
(if any). Overrides --federation.
-l , --long [#OPT_long_1](https://slurm.schedmd.com/squeue.html) Report more of the available information for the selected jobs or job steps,
subject to any constraints specified.
--me [#OPT_me](https://slurm.schedmd.com/squeue.html) Equivalent to --user=<my username> .
-n , --name =< name_list >[#OPT_name](https://slurm.schedmd.com/squeue.html) Request jobs or job steps having one of the specified names. The
list consists of a comma separated list of job names.
--noconvert [#OPT_noconvert](https://slurm.schedmd.com/squeue.html) Don't convert units from their original type (e.g. 2048M won't be converted to
2G).
-w , --nodelist =< hostlist >[#OPT_nodelist](https://slurm.schedmd.com/squeue.html) Report only on jobs allocated to the specified node or list of nodes.
This may either be the NodeName or NodeHostname
as defined in [slurm.conf](https://slurm.schedmd.com/slurm.conf.html)(5) in the event that they differ.
A node_name of localhost is mapped to the current host name.
-h , --noheader [#OPT_noheader](https://slurm.schedmd.com/squeue.html) Do not print a header on the output.
--notme [#OPT_notme](https://slurm.schedmd.com/squeue.html) Opposite of --me ; only display jobs that are not from the invoking user.
--only-job-state [#OPT_only-job-state](https://slurm.schedmd.com/squeue.html) Only query for the job state. Query utilizes RPC that only retains JobID
and State information, reducing work required by slurmctld to respond.
-p , --partition =< part_list >[#OPT_partition](https://slurm.schedmd.com/squeue.html) Specify the partitions of the jobs or steps to view. Accepts a comma separated
list of partition names.
-P , --priority [#OPT_priority](https://slurm.schedmd.com/squeue.html) For pending jobs submitted to multiple partitions, list the job once per
partition. In addition, if jobs are sorted by priority, consider both the
partition and job priority. This option can be used to produce a list of
pending jobs in the same order considered for scheduling by Slurm with
appropriate additional options (e.g. "--sort=-p,i --states=PD").
-q , --qos =< qos_list >[#OPT_qos](https://slurm.schedmd.com/squeue.html) Specify the qos(s) of the jobs or steps to view. Accepts a comma
separated list of qos's.
-R , --reservation =< reservation_list >[#OPT_reservation](https://slurm.schedmd.com/squeue.html) Specify the reservations of the jobs to view. Accepts a comma separated
list of reservation names. Jobs matching any reservation will satisfy the
filter (logic works like an OR).
--running-over =< time >[#OPT_running-over](https://slurm.schedmd.com/squeue.html) Display only jobs that have been running over the amount of specified time.
Acceptable time formats include "minutes", "minutes:seconds",
"hours:minutes:seconds", "days-hours", "days-hours:minutes" and
"days-hours:minutes:seconds".
--running-under =< time >[#OPT_running-under](https://slurm.schedmd.com/squeue.html) Display only jobs that have been running under the amount of specified time.
Acceptable time formats include "minutes", "minutes:seconds",
"hours:minutes:seconds", "days-hours", "days-hours:minutes" and
"days-hours:minutes:seconds".
--sibling [#OPT_sibling](https://slurm.schedmd.com/squeue.html) Show all sibling jobs on a federated cluster. Implies --federation.
-S , --sort =< sort_list >[#OPT_sort](https://slurm.schedmd.com/squeue.html) Specification of the order in which records should be reported.
This uses the same field specification as the <output_format>.
The long format option "cluster" can also be used to sort jobs or job steps by
cluster name (e.g. federated jobs).
Multiple sorts may be performed by listing multiple sort fields
separated by commas.
The field specifications may be preceded by "+" or "-" for
ascending (default) and descending order respectively.
For example, a sort value of "P,U" will sort the
records by partition name then by user id.
The default value of sort for jobs is "P,t,-p" (increasing partition
name then within a given partition by increasing job state and then
decreasing priority).
The default value of sort for job steps is "P,i" (increasing partition
name then within a given partition by increasing step id).
--start [#OPT_start](https://slurm.schedmd.com/squeue.html) Report the expected start time and resources to be allocated for pending jobs
in order of increasing start time.
This is equivalent to the following options:
--format="%.18i %.9P %.8j %.8u %.2t %.19S %.6D %20Y %R" ,
--sort=S and --states=PENDING .
Any of these options may be explicitly changed as desired by
combining the --start option with other option values
(e.g. to use a different output format).
The expected start time of pending jobs is only available if the
Slurm is configured to use the backfill scheduling plugin.
-t , --states =< state_list >[#OPT_states](https://slurm.schedmd.com/squeue.html) Specify the states of jobs to view. Accepts a comma separated list of
state names or "all". If "all" is specified then jobs of all states will be
reported. If no state is specified then pending, running, and completing
jobs are reported. See the JOB STATE CODES section below for a list of
valid states. Both extended and compact forms are valid.
Note the <state_list> supplied is case insensitive ("pd" and "PD" are
equivalent).
-s , --steps [=< step_list >][#OPT_steps_1](https://slurm.schedmd.com/squeue.html) Specify the job steps to view. This flag indicates that a comma separated list
of job steps to view follows without an equal sign (see examples).
The job step format is "job_id[_array_id].step_id". Defaults to all job
steps. Since this option's argument is optional, for proper parsing
the single letter option must be followed immediately with the value
and not include a space between them. For example "-s1008.0" and not
"-s 1008.0".
--usage [#OPT_usage](https://slurm.schedmd.com/squeue.html) Print a brief help message listing the squeue options.
-u , --user =< user_list >[#OPT_user](https://slurm.schedmd.com/squeue.html) Request jobs or job steps from a comma separated list of users.
The list can consist of user names or user id numbers.
Performance of the command can be measurably improved for systems with large
numbers of jobs when a single user is specified.
-v , --verbose [#OPT_verbose](https://slurm.schedmd.com/squeue.html) Report details of squeues actions.
-V , --version [#OPT_version](https://slurm.schedmd.com/squeue.html) Print version information and exit.
--yaml , --yaml = list , --yaml =< data_parser >[#OPT_yaml](https://slurm.schedmd.com/squeue.html) Dump information as YAML using the default data_parser plugin or explicit
data_parser with parameters. All information is dumped, even if it would
normally not be. Sorting and formatting arguments passed to other options are
ignored; however, most filtering arguments are still used.
## JOB REASON CODES[#SECTION_JOB-REASON-CODES](https://slurm.schedmd.com/squeue.html)
These codes identify the reason that a job has not been started by the scheduler.
There may be multiple reasons why a job cannot start yet, in which case only the
reason that was encountered by the attempted scheduling method will be displayed.
The Reasons listed below are some of the more common ones you might see.
For a full list of Reason codes refer to this page:
<[https://slurm.schedmd.com/job_reason_codes.html](https://slurm.schedmd.com/job_reason_codes.html)>
AssocGrp*Limit [#OPT_AssocGrp*Limit](https://slurm.schedmd.com/squeue.html) The job's association has reached an aggregate limit on some resource.
AssociationJobLimit [#OPT_AssociationJobLimit](https://slurm.schedmd.com/squeue.html) The job's association has reached its maximum job count.
AssocMax*Limit [#OPT_AssocMax*Limit](https://slurm.schedmd.com/squeue.html) The job requests a resource that violates a per-job limit on the requested
association.
AssociationResourceLimit [#OPT_AssociationResourceLimit](https://slurm.schedmd.com/squeue.html) The job's association has reached some resource limit.
AssociationTimeLimit [#OPT_AssociationTimeLimit](https://slurm.schedmd.com/squeue.html) The job's association has reached its time limit.
BadConstraints [#OPT_BadConstraints](https://slurm.schedmd.com/squeue.html) The job's constraints can not be satisfied.
BeginTime [#OPT_BeginTime](https://slurm.schedmd.com/squeue.html) The job's earliest start time has not yet been reached.
Cleaning [#OPT_Cleaning](https://slurm.schedmd.com/squeue.html) The job is being requeued and still cleaning up from its previous execution.
Dependency [#OPT_Dependency_1](https://slurm.schedmd.com/squeue.html) This job has a dependency on another job that has not been satisfied.
DependencyNeverSatisfied [#OPT_DependencyNeverSatisfied](https://slurm.schedmd.com/squeue.html) This job has a dependency on another job that will never be satisfied.
InactiveLimit [#OPT_InactiveLimit](https://slurm.schedmd.com/squeue.html) The job reached the system InactiveLimit.
InvalidAccount [#OPT_InvalidAccount](https://slurm.schedmd.com/squeue.html) The job's account is invalid.
InvalidQOS [#OPT_InvalidQOS](https://slurm.schedmd.com/squeue.html) The job's QOS is invalid.
JobHeldAdmin [#OPT_JobHeldAdmin](https://slurm.schedmd.com/squeue.html) The job is held by a system administrator.
JobHeldUser [#OPT_JobHeldUser](https://slurm.schedmd.com/squeue.html) The job is held by the user.
JobLaunchFailure [#OPT_JobLaunchFailure](https://slurm.schedmd.com/squeue.html) The job could not be launched.
This may be due to a file system problem, invalid program name, etc.
Licenses [#OPT_Licenses_1](https://slurm.schedmd.com/squeue.html) The job is waiting for a license.
NodeDown [#OPT_NodeDown](https://slurm.schedmd.com/squeue.html) A node required by the job is down.
NonZeroExitCode [#OPT_NonZeroExitCode](https://slurm.schedmd.com/squeue.html) The job terminated with a non-zero exit code.
PartitionDown [#OPT_PartitionDown](https://slurm.schedmd.com/squeue.html) The partition required by this job is in a DOWN state.
PartitionInactive [#OPT_PartitionInactive](https://slurm.schedmd.com/squeue.html) The partition required by this job is in an Inactive state and not able to
start jobs.
PartitionNodeLimit [#OPT_PartitionNodeLimit](https://slurm.schedmd.com/squeue.html) The number of nodes required by this job is outside of its partition's current
limits.
Can also indicate that required nodes are DOWN or DRAINED.
PartitionTimeLimit [#OPT_PartitionTimeLimit](https://slurm.schedmd.com/squeue.html) The job's time limit exceeds its partition's current time limit.
Priority [#OPT_Priority_1](https://slurm.schedmd.com/squeue.html) One or more higher priority jobs exist for this partition or advanced reservation.
Prolog [#OPT_Prolog](https://slurm.schedmd.com/squeue.html) Its Prolog program is still running.
QOSGrp*Limit [#OPT_QOSGrp*Limit](https://slurm.schedmd.com/squeue.html) The job's QOS has reached an aggregate limit on some resource.
QOSJobLimit [#OPT_QOSJobLimit](https://slurm.schedmd.com/squeue.html) The job's QOS has reached its maximum job count.
QOSMax*Limit [#OPT_QOSMax*Limit](https://slurm.schedmd.com/squeue.html) The job requests a resource that violates a per-job limit on the requested
QOS.
QOSResourceLimit [#OPT_QOSResourceLimit](https://slurm.schedmd.com/squeue.html) The job's QOS has reached some resource limit.
QOSTimeLimit [#OPT_QOSTimeLimit](https://slurm.schedmd.com/squeue.html) The job's QOS has reached its time limit.
QOSUsageThreshold [#OPT_QOSUsageThreshold](https://slurm.schedmd.com/squeue.html) Required QOS threshold has been breached.
ReqNodeNotAvail [#OPT_ReqNodeNotAvail](https://slurm.schedmd.com/squeue.html) Some node specifically required by the job is not currently available.
The node may currently be in use, reserved for another job, in an advanced
reservation, DOWN, DRAINED, or not responding.
Nodes which are DOWN, DRAINED, or not responding will be identified as part
of the job's "reason" field as "UnavailableNodes". Such nodes will typically
require the intervention of a system administrator to make available.
Reservation [#OPT_Reservation_1](https://slurm.schedmd.com/squeue.html) The job is waiting its advanced reservation to become available.
Resources [#OPT_Resources](https://slurm.schedmd.com/squeue.html) The job is waiting for resources to become available.
SystemFailure [#OPT_SystemFailure](https://slurm.schedmd.com/squeue.html) Failure of the Slurm system, a file system, the network, etc.
TimeLimit [#OPT_TimeLimit_1](https://slurm.schedmd.com/squeue.html) The job exhausted its time limit.
WaitingForScheduling [#OPT_WaitingForScheduling](https://slurm.schedmd.com/squeue.html) No reason has been set for this job yet.
Waiting for the scheduler to determine the appropriate reason.
## JOB STATE CODES[#SECTION_JOB-STATE-CODES](https://slurm.schedmd.com/squeue.html)
Jobs typically pass through several states in the course of their
execution.
The typical states are PENDING, RUNNING, SUSPENDED, COMPLETING, and COMPLETED.
The following states are recognized by squeue. A full list of possible states
is available at <[https://slurm.schedmd.com/job_state_codes.html](https://slurm.schedmd.com/job_state_codes.html)>.
BF BOOT_FAIL [#OPT_BF--BOOT_FAIL](https://slurm.schedmd.com/squeue.html) Job terminated due to launch failure, typically due to a hardware failure
(e.g. unable to boot the node or block and the job can not be requeued).
CA CANCELLED [#OPT_CA--CANCELLED](https://slurm.schedmd.com/squeue.html) Job was explicitly cancelled by the user or system administrator.
The job may or may not have been initiated.
CD COMPLETED [#OPT_CD--COMPLETED](https://slurm.schedmd.com/squeue.html) Job has terminated all processes on all nodes with an exit code of zero.
CF CONFIGURING [#OPT_CF--CONFIGURING](https://slurm.schedmd.com/squeue.html) Job has been allocated resources, but are waiting for them to become ready for use
(e.g. booting).
CG COMPLETING [#OPT_CG--COMPLETING](https://slurm.schedmd.com/squeue.html) Job is in the process of completing. Some processes on some nodes may still be active.
DL DEADLINE [#OPT_DL--DEADLINE](https://slurm.schedmd.com/squeue.html) Job terminated on deadline.
F FAILED [#OPT_F---FAILED](https://slurm.schedmd.com/squeue.html) Job terminated with non-zero exit code or other failure condition.
NF NODE_FAIL [#OPT_NF--NODE_FAIL](https://slurm.schedmd.com/squeue.html) Job terminated due to failure of one or more allocated nodes.
OOM OUT_OF_MEMORY [#OPT_OOM-OUT_OF_MEMORY](https://slurm.schedmd.com/squeue.html) Job experienced out of memory error.
PD PENDING [#OPT_PD--PENDING](https://slurm.schedmd.com/squeue.html) Job is awaiting resource allocation.
PR PREEMPTED [#OPT_PR--PREEMPTED](https://slurm.schedmd.com/squeue.html) Job terminated due to preemption.
R RUNNING [#OPT_R---RUNNING](https://slurm.schedmd.com/squeue.html) Job currently has an allocation.
RD RESV_DEL_HOLD [#OPT_RD--RESV_DEL_HOLD](https://slurm.schedmd.com/squeue.html) Job is being held after requested reservation was deleted.
RF REQUEUE_FED [#OPT_RF--REQUEUE_FED](https://slurm.schedmd.com/squeue.html) Job is being requeued by a federation.
RH REQUEUE_HOLD [#OPT_RH--REQUEUE_HOLD](https://slurm.schedmd.com/squeue.html) Held job is being requeued.
RQ REQUEUED [#OPT_RQ--REQUEUED](https://slurm.schedmd.com/squeue.html) Completing job is being requeued.
RS RESIZING [#OPT_RS--RESIZING](https://slurm.schedmd.com/squeue.html) Job is about to change size.
RV REVOKED [#OPT_RV--REVOKED](https://slurm.schedmd.com/squeue.html) Sibling was removed from cluster due to other cluster starting the job.
SI SIGNALING [#OPT_SI--SIGNALING](https://slurm.schedmd.com/squeue.html) Job is being signaled.
SE SPECIAL_EXIT [#OPT_SE--SPECIAL_EXIT](https://slurm.schedmd.com/squeue.html) The job was requeued in a special state. This state can be set by
users, typically in EpilogSlurmctld, if the job has terminated with
a particular exit value.
SO STAGE_OUT [#OPT_SO--STAGE_OUT](https://slurm.schedmd.com/squeue.html) Job is staging out files.
ST STOPPED [#OPT_ST--STOPPED](https://slurm.schedmd.com/squeue.html) Job has an allocation, but execution has been stopped with SIGSTOP signal.
CPUS have been retained by this job.
S SUSPENDED [#OPT_S---SUSPENDED](https://slurm.schedmd.com/squeue.html) Job has an allocation, but execution has been suspended and CPUs have been
released for other jobs.
TO TIMEOUT [#OPT_TO--TIMEOUT](https://slurm.schedmd.com/squeue.html) Job terminated upon reaching its time limit.
## PERFORMANCE[#SECTION_PERFORMANCE](https://slurm.schedmd.com/squeue.html)
Executing squeue sends a remote procedure call to slurmctld . If
enough calls from squeue or other Slurm client commands that send remote
procedure calls to the slurmctld daemon come in at once, it can result in
a degradation of performance of the slurmctld daemon, possibly resulting
in a denial of service.
Do not run squeue or other Slurm client commands that send remote
procedure calls to slurmctld from loops in shell scripts or other
programs. Ensure that programs limit calls to squeue to the minimum
necessary for the information you are trying to gather.
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/squeue.html)
Some squeue options may be set via environment variables. These
environment variables, along with their corresponding options, are listed
below. (Note: Command line options will always override these settings.)
SLURM_BITSTR_LEN [#OPT_SLURM_BITSTR_LEN](https://slurm.schedmd.com/squeue.html) Specifies the string length to be used for holding a job array's task ID
expression.
The default value is 64 bytes.
A value of 0 will print the full expression with any length required.
Larger values may adversely impact the application performance.
SLURM_CLUSTERS [#OPT_SLURM_CLUSTERS](https://slurm.schedmd.com/squeue.html) Same as --clusters
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/squeue.html) The location of the Slurm configuration file.
SLURM_DEBUG_FLAGS [#OPT_SLURM_DEBUG_FLAGS](https://slurm.schedmd.com/squeue.html) Specify debug flags for squeue to use. See DebugFlags in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for a full list of flags. The environment
variable takes precedence over the setting in the slurm.conf.
SLURM_JSON [#OPT_SLURM_JSON](https://slurm.schedmd.com/squeue.html) Control JSON serialization:
compact [#OPT_compact](https://slurm.schedmd.com/squeue.html) Output JSON as compact as possible.
pretty [#OPT_pretty](https://slurm.schedmd.com/squeue.html) Output JSON in pretty format to make it more readable.
SLURM_TIME_FORMAT [#OPT_SLURM_TIME_FORMAT](https://slurm.schedmd.com/squeue.html) Specify the format used to report time stamps. A value of standard , the
default value, generates output in the form "year-month-dateThour:minute:second".
A value of relative returns only "hour:minute:second" if the current day.
For other dates in the current year it prints the "hour:minute" preceded by
"Tomorr" (tomorrow), "Ystday" (yesterday), the name of the day for the coming
week (e.g. "Mon", "Tue", etc.), otherwise the date (e.g. "25 Apr").
For other years it returns a date month and year without a time (e.g.
"6 Jun 2012"). All of the time stamps use a 24 hour format.
A valid strftime() format can also be specified. For example, a value of
"%a %T" will report the day of the week and a time stamp (e.g. "Mon 12:34:56").
SLURM_YAML [#OPT_SLURM_YAML](https://slurm.schedmd.com/squeue.html) Control YAML serialization:
compact Output YAML as compact as possible.[#OPT_compact_1](https://slurm.schedmd.com/squeue.html)
pretty Output YAML in pretty format to make it more readable.[#OPT_pretty_1](https://slurm.schedmd.com/squeue.html)
SQUEUE_ACCOUNT [#OPT_SQUEUE_ACCOUNT](https://slurm.schedmd.com/squeue.html) -A <account_list>, --account=<account_list>
SQUEUE_ALL [#OPT_SQUEUE_ALL](https://slurm.schedmd.com/squeue.html) -a, --all
SQUEUE_ARRAY [#OPT_SQUEUE_ARRAY](https://slurm.schedmd.com/squeue.html) -r, --array
SQUEUE_NAMES [#OPT_SQUEUE_NAMES](https://slurm.schedmd.com/squeue.html) --name=<name_list>
SQUEUE_FEDERATION [#OPT_SQUEUE_FEDERATION](https://slurm.schedmd.com/squeue.html) --federation
SQUEUE_FORMAT [#OPT_SQUEUE_FORMAT](https://slurm.schedmd.com/squeue.html) -o <output_format>, --format=<output_format>
SQUEUE_FORMAT2 [#OPT_SQUEUE_FORMAT2](https://slurm.schedmd.com/squeue.html) -O <output_format>, --Format=<output_format>
SQUEUE_LICENSES [#OPT_SQUEUE_LICENSES](https://slurm.schedmd.com/squeue.html) -p-l <license_list>, --license=<license_list>
SQUEUE_LOCAL [#OPT_SQUEUE_LOCAL](https://slurm.schedmd.com/squeue.html) --local
SQUEUE_PARTITION [#OPT_SQUEUE_PARTITION](https://slurm.schedmd.com/squeue.html) -p <part_list>, --partition=<part_list>
SQUEUE_PRIORITY [#OPT_SQUEUE_PRIORITY](https://slurm.schedmd.com/squeue.html) -P , --priority
SQUEUE_QOS [#OPT_SQUEUE_QOS](https://slurm.schedmd.com/squeue.html) -p <qos_list>, --qos=<qos_list>
SQUEUE_SIBLING [#OPT_SQUEUE_SIBLING](https://slurm.schedmd.com/squeue.html) --sibling
SQUEUE_SORT [#OPT_SQUEUE_SORT](https://slurm.schedmd.com/squeue.html) -S <sort_list>, --sort=<sort_list>
SQUEUE_STATES [#OPT_SQUEUE_STATES](https://slurm.schedmd.com/squeue.html) -t <state_list>, --states=<state_list>
SQUEUE_USERS [#OPT_SQUEUE_USERS](https://slurm.schedmd.com/squeue.html) -u <user_list>, --users=<user_list>
## EXAMPLES[#SECTION_EXAMPLES](https://slurm.schedmd.com/squeue.html)
Print the jobs scheduled in the debug partition and in the COMPLETED state in the format with six right justified digits for the job id followed by the priority with an arbitrary fields size:
```text
$ squeue -p debug -t COMPLETED -o "%.6i %p" JOBID PRIORITY 65543 99993 65544 99992 65545 99991
```
Print the job steps in the debug partition sorted by user:
```text
$ squeue -s -p debug -S u STEPID NAME PARTITION USER TIME NODELIST 65552.1 test1 debug alice 0:23 dev[1-4] 65562.2 big_run debug bob 0:18 dev22 65550.1 param1 debug candice 1:43:21 dev[6-12]
```
Print information only about jobs 12345, 12346 and 12348:
```text
$ squeue --jobs 12345,12346,12348 JOBID PARTITION NAME USER ST TIME NODES NODELIST(REASON) 12345 debug job1 dave R 0:21 4 dev[9-12] 12346 debug job2 dave PD 0:00 8 (Resources) 12348 debug job3 ed PD 0:00 4 (Priority)
```
Print information only about job step 65552.1:
```text
$ squeue --steps 65552.1 STEPID NAME PARTITION USER TIME NODELIST 65552.1 test2 debug alice 12:49 dev[1-4]
```
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/squeue.html)
Copyright (C) 2002-2007 The Regents of the University of California.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/squeue.html)
[scancel](https://slurm.schedmd.com/scancel.html) (1), [scontrol](https://slurm.schedmd.com/scontrol.html) (1), [sinfo](https://slurm.schedmd.com/sinfo.html) (1), [srun](https://slurm.schedmd.com/srun.html) (1),
slurm_load_ctl_conf (3), slurm_load_jobs (3),
slurm_load_node (3),
slurm_load_partitions (3)
## Index
[NAME](https://slurm.schedmd.com/squeue.html)
[SYNOPSIS](https://slurm.schedmd.com/squeue.html)
[DESCRIPTION](https://slurm.schedmd.com/squeue.html)
[OPTIONS](https://slurm.schedmd.com/squeue.html)
[JOB REASON CODES](https://slurm.schedmd.com/squeue.html)
[JOB STATE CODES](https://slurm.schedmd.com/squeue.html)
[PERFORMANCE](https://slurm.schedmd.com/squeue.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/squeue.html)
[EXAMPLES](https://slurm.schedmd.com/squeue.html)
[COPYING](https://slurm.schedmd.com/squeue.html)
[SEE ALSO](https://slurm.schedmd.com/squeue.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
