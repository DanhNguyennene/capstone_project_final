---
source_url: https://slurm.schedmd.com/cons_tres.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:20:54 UTC
title: "Slurm Workload Manager - Consumable Resources in Slurm"
---

# Consumable Resources in Slurm
Slurm, using the default node allocation plug-in, allocates nodes to jobs in
exclusive mode. This means that even when all the resources within a node are
not utilized by a given job, another job will not have access to these resources.
Nodes possess resources such as processors, memory, swap, local
disk, etc. and jobs consume these resources. The exclusive use default policy
in Slurm can result in inefficient utilization of the cluster and of its nodes
resources.
Slurm's cons_tres plugin is available to
manage resources on a much more fine-grained basis as described below.
## Using the Consumable Trackable Resource Plugin: select/cons_tres [#using_cons_tres](https://slurm.schedmd.com/cons_tres.html)
The Consumable Trackable Resources ( cons_tres ) plugin has been built
to work with several resources. It can track a Board, Socket, Core, CPU, Memory
as well as any combination of the logical processors with Memory:
- CPU ( CR_CPU ): CPU as a consumable resource.
- No notion of sockets, cores, or threads.
- On a multi-core system CPUs will be cores.
- On a multi-core/hyperthread system CPUs will be threads.
- On a single-core system CPUs are CPUs.
- Board ( CR_Board ): Baseboard as a consumable resource.
- Socket ( CR_Socket ): Socket as a consumable resource.
- Core ( CR_Core ): Core as a consumable resource.
- Socket and Memory ( CR_Socket_Memory ): Socket and Memory as consumable resources.
- Core and Memory ( CR_Core_Memory ): Core and Memory as consumable resources.
- CPU and Memory ( CR_CPU_Memory ) CPU and Memory as consumable resources.
All CR_* parameters assume OverSubscribe=No or
OverSubscribe=Force .
The cons_tres plugin also provides functionality specifically
related to GPUs.
Additional parameters available for the cons_tres plugin:
- DefCpuPerGPU : Default number of CPUs allocated per GPU.
- DefMemPerGPU : Default amount of memory allocated per GPU.
Additional job submit options available for the cons_tres plugin:
- --cpus-per-gpu= : Number of CPUs for every GPU.
- --gpus= : Count of GPUs for entire job allocation.
- --gpu-bind= : Bind task to specific GPU(s).
- --gpu-freq= : Request specific GPU/memory frequencies.
- --gpus-per-node= : Number of GPUs per node.
- --gpus-per-socket= : Number of GPUs per socket.
- --gpus-per-task= : Number of GPUs per task.
- --mem-per-gpu= : Amount of memory for each GPU.
srun's -B extension for sockets, cores, and threads is
ignored within the node allocation mechanism when CR_CPU or
CR_CPU_MEMORY is selected. It is used to compute the total
number of tasks when -n is not specified.
In the cases where Memory is a consumable resource, the RealMemory
parameter must be set in the slurm.conf to define a node's amount of real
memory.
The job submission commands (salloc, sbatch and srun) support the options
--mem=MB and --mem-per-cpu=MB , permitting users to specify
the maximum amount of real memory required per node or per allocated CPU.
This option is required in the environments where Memory is a consumable
resource. It is important to specify enough memory since Slurm will not allow
the application to use more than the requested amount of real memory. The
default value for --mem is inherited from DefMemPerNode . See
[srun](https://slurm.schedmd.com/srun.html)(1) for more details.
Using --overcommit or -O is allowed. When the process to
logical processor pinning is enabled by using an appropriate TaskPlugin
configuration parameter, the extra processes will time share the allocated
resources.
The Consumable Trackable Resource plugin is enabled via the SelectType
parameter in the slurm.conf.
```text
# Excerpt from sample slurm.conf file SelectType=select/cons_tres
```
## General Comments[#general](https://slurm.schedmd.com/cons_tres.html)
Slurm's default select/linear plugin is using a best fit algorithm
based on number of consecutive nodes.
The select/cons_tres plugin is enabled or disabled cluster-wide.
In the case where select/linear is enabled, the normal Slurm
behaviors are not disrupted. The major change users see when using the
select/cons_tres plugin is that jobs can be
co-scheduled on nodes when resources permit it. Generic resources (such as GPUs)
can also be tracked individually with this plugin.
The rest of Slurm, such as srun and its options (except srun -s ...), etc. are not
affected by this plugin. Slurm is, from the user's point of view, working the
same way as when using the default node selection scheme.
The --exclusive srun option allows users to request nodes in
exclusive mode even when consumable resources is enabled. See
[srun](https://slurm.schedmd.com/srun.html)(1) for details.
srun's -s or --oversubscribe is incompatible with the consumable
resource environment and will therefore not be honored. Since this
environment's nodes are shared by default, --exclusive allows users to
obtain dedicated nodes.
The --oversubscribe and --exclusive options are mutually
exclusive when used at job submission. If both options are set when submitting
a job, the job submission command used will fatal.
## Examples of CR_Socket_Memory, and CR_CPU_Memory type consumable resources [#example_mem](https://slurm.schedmd.com/cons_tres.html)
```text
# sinfo -lNe NODELIST NODES PARTITION STATE CPUS S:C:T MEMORY hydra[12-16] 5 allNodes* ... 4 2:2:1 2007
```
Using select/cons_tres plug-in with CR_Socket_Memory (2 sockets/node)
```text
Example 1: # srun -N 5 -n 5 --mem=1000 sleep 100 & cons_tres
plugin and CPUs as the consumable resource. The output of squeue shows that we
have 3 out of the 4 jobs allocated and running. This is a 2 running job
increase over the default Slurm approach.
Job 2 is running on nodes linux01
to linux04. Job 2's allocation is the same as for Slurm's default allocation
which is that it uses one CPU on each of the 4 nodes. Once Job 2 is scheduled
and running, nodes linux01, linux02 and linux03 still have one idle CPU each
and node linux04 has 3 idle CPUs. The main difference between this approach and
the exclusive mode approach described above is that idle CPUs within a node
are now allowed to be assigned to other jobs.
It is important to note that
assigned doesn't mean oversubscription . The consumable resource approach
tracks how much of each available resource (in our case CPUs) must be dedicated
to a given job. This allows us to prevent per node oversubscription of
resources (CPUs).
Once Job 2 is running, Job 3 is
scheduled onto node linux01, linux02, and Linux03 (using one CPU on each of the
nodes) and Job 4 is scheduled onto one of the remaining idle CPUs on Linux04.
Job 2, Job 3, and Job 4 are now running concurrently on the cluster.
```text
# squeue JOBID PARTITION NAME USER ST TIME NODES NODELIST(REASON) 5 lsf sleep root PD 0:00 1 (Resources) 2 lsf sleep root R 0:13 4 linux[01-04] 3 lsf sleep root R 0:09 3 linux[01-03] 4 lsf sleep root R 0:05 1 linux04 # sinfo -lNe NODELIST NODES PARTITION STATE CPUS MEMORY TMP_DISK WEIGHT FEATURES REASON linux[01-03] 3 lsf* allocated 2 2981 1 1 (null) none linux04 1 lsf* allocated 4 3813 1 1 (null) none
```
Once Job 2 finishes, Job 5, which was pending, is allocated available resources and is then
running as illustrated below:
```text
# squeue JOBID PARTITION NAME USER ST TIME NODES NODELIST(REASON) 3 lsf sleep root R 1:58 3 linux[01-03] 4 lsf sleep root R 1:54 1 linux04 5 lsf sleep root R 0:02 3 linux[01-03] # sinfo -lNe NODELIST NODES PARTITION STATE CPUS MEMORY TMP_DISK WEIGHT FEATURES REASON linux[01-03] 3 lsf* allocated 2 2981 1 1 (null) none linux04 1 lsf* idle 4 3813 1 1 (null) none
```
Job 3, Job 4, and Job 5 are now running concurrently on the cluster.
```text
# squeue JOBID PARTITION NAME USER ST TIME NODES NODELIST(REASON) 5 lsf sleep root R 1:52 3 linux[01-03]
```
Job 3 and Job 4 have finished and Job 5 is still running on nodes linux[01-03].
The advantage of the consumable resource scheduling policy
is that the job throughput can increase dramatically. The overall job
throughput and productivity of the cluster increases, thereby reducing the
amount of time users have to wait for their job to complete as well as
increasing the overall efficiency of the use of the cluster. The drawback is
that users do not have entire nodes dedicated to their jobs by default.
We have added the --exclusive option to srun (see
[srun](https://slurm.schedmd.com/srun.html)(1) for more details),
which allows users to specify that they would like
their nodes to be allocated in exclusive mode.
This is to accommodate users who might have mpi/threaded/openMP
programs that will take advantage of all the CPUs on a node but only need
one mpi process per node.
