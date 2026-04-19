---
source_url: https://slurm.schedmd.com/man_index.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:21:17 UTC
title: "Slurm Workload Manager - Man Pages"
---

# Man Pages
NOTE: This documentation is for Slurm version 25.11.
Documentation for other versions of Slurm is distributed with the code
Refer to [this page](https://slurm.schedmd.com/slurm.html) for an overview of Slurm.
## Commands [#commands](https://slurm.schedmd.com/man_index.html)
[sacct](https://slurm.schedmd.com/sacct.html)
Displays accounting data for all jobs and job steps in the Slurm job
accounting log or Slurm database.
[sacctmgr](https://slurm.schedmd.com/sacctmgr.html)
Used to view and modify Slurm account information.
[salloc](https://slurm.schedmd.com/salloc.html)
Obtain a Slurm job allocation (a set of nodes), execute a command,
and then release the allocation when the command is finished.
[sattach](https://slurm.schedmd.com/sattach.html)
Attach to a Slurm job step.
[sbatch](https://slurm.schedmd.com/sbatch.html)
Submit a batch script to Slurm.
[sbcast](https://slurm.schedmd.com/sbcast.html)
Transmit a file to the nodes allocated to a Slurm job.
[scancel](https://slurm.schedmd.com/scancel.html)
Used to signal jobs or job steps that are under the control of Slurm.
[scontrol](https://slurm.schedmd.com/scontrol.html)
View or modify Slurm configuration and state.
[scrontab](https://slurm.schedmd.com/scrontab.html)
Manage Slurm crontab files.
[scrun](https://slurm.schedmd.com/scrun.html)
An OCI runtime proxy for slurm.
[sdiag](https://slurm.schedmd.com/sdiag.html)
Scheduling diagnostic tool.
[sh5util](https://slurm.schedmd.com/sh5util.html)
Merge utility for acct_gather_profile plugin.
[sinfo](https://slurm.schedmd.com/sinfo.html)
View information about Slurm nodes and partitions.
[sprio](https://slurm.schedmd.com/sprio.html)
View the factors that comprise a job's scheduling priority.
[squeue](https://slurm.schedmd.com/squeue.html)
View information about jobs located in the Slurm scheduling queue.
[sreport](https://slurm.schedmd.com/sreport.html)
Generate reports from the slurm accounting data.
[srun](https://slurm.schedmd.com/srun.html)
Run parallel jobs.
[sshare](https://slurm.schedmd.com/sshare.html)
Tool for listing the shares of associations to a cluster.
[sstat](https://slurm.schedmd.com/sstat.html)
Display the status information of a running job/step.
[strigger](https://slurm.schedmd.com/strigger.html)
Used to set, get or clear Slurm trigger information.
[sview](https://slurm.schedmd.com/sview.html)
Graphical user interface to view and modify Slurm state.
## Configuration Files [#configuration_files](https://slurm.schedmd.com/man_index.html)
[acct_gather.conf](https://slurm.schedmd.com/acct_gather.conf.html)
Slurm configuration file for the acct_gather plugins.
[burst_buffer.conf](https://slurm.schedmd.com/burst_buffer.conf.html)
Slurm burst buffer configuration.
[cgroup.conf](https://slurm.schedmd.com/cgroup.conf.html)
Slurm configuration file for the cgroup support.
[gres.conf](https://slurm.schedmd.com/gres.conf.html)
Slurm configuration file for generic resource management.
[helpers.conf](https://slurm.schedmd.com/helpers.conf.html)
Slurm configuration file for the node_features/helpers plugin.
[job_container.conf](https://slurm.schedmd.com/job_container.conf.html)
Slurm configuration file for configuring the namespace/tmpfs
plugin.
[mpi.conf](https://slurm.schedmd.com/mpi.conf.html)
Slurm configuration file to allow the configuration of MPI plugins.
[namespace.yaml](https://slurm.schedmd.com/namespace.yaml.html)
Slurm configuration file for the namespace/linux plugin.
[oci.conf](https://slurm.schedmd.com/oci.conf.html)
Slurm configuration file for OCI Containers.
[plugstack.conf](https://slurm.schedmd.com/spank.html)
Slurm configuration file for SPANK plug-in stack.
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html)
Slurm configuration file.
[slurmdbd.conf](https://slurm.schedmd.com/slurmdbd.conf.html)
Slurm Database Daemon (SlurmDBD) configuration file.
[topology.conf](https://slurm.schedmd.com/topology.conf.html)
Slurm configuration file for defining the network topology.
[topology.yaml](https://slurm.schedmd.com/topology.yaml.html)
Slurm configuration file for defining multiple network topologies.
## Daemons and Other [#daemons](https://slurm.schedmd.com/man_index.html)
[sackd](https://slurm.schedmd.com/sackd.html)
Slurm Auth and Cred Kiosk Daemon.
[slurmctld](https://slurm.schedmd.com/slurmctld.html)
The central management daemon of Slurm.
[slurmd](https://slurm.schedmd.com/slurmd.html)
The compute node daemon for Slurm.
[slurmdbd](https://slurm.schedmd.com/slurmdbd.html)
Slurm Database Daemon.
[slurmrestd](https://slurm.schedmd.com/slurmrestd.html)
The Slurm REST API daemon.
[slurmstepd](https://slurm.schedmd.com/slurmstepd.html)
The job step manager for Slurm.
[SPANK](https://slurm.schedmd.com/spank.html)
Slurm Plug-in Architecture for Node and job (K)control.
