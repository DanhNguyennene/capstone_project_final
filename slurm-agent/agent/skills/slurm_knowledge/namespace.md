---
source_url: https://slurm.schedmd.com/namespace.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:21:20 UTC
title: "Slurm Workload Manager - Namespace Plugins"
---

# Namespace Plugins
## Overview[#overview](https://slurm.schedmd.com/namespace.html)
A namespace plugin can be enabled to provide job-specific, private temporary
file system space.
When enabled on the cluster, a filesystem namespace will be created for each
job with a unique, private instance of /tmp and /dev/shm for the job to use.
These directories can be changed with the Dirs= option in the
plugin-specific configuration file. The contents of these directories will be
removed at job termination. Additionally, the namespace/linux plugin can
be configured to create new PID and user namespaces.
## Installation [#installation](https://slurm.schedmd.com/namespace.html)
These plugins are built and installed as part of the default build, no extra
installation steps are required.
## Setup[#setup](https://slurm.schedmd.com/namespace.html)
Slurm must be configured to load the namespace plugin by adding
PrologFlags=contain and setting NamespaceType to the desired
plugin in slurm.conf. Additional configuration must be done in the
plugin-specific configuration file file, which should be placed in the same
directory as slurm.conf.
### namespace/linux plugin [#linux_setup](https://slurm.schedmd.com/namespace.html)
The namespace/linux plugin (added 25.11) uses the configuration file
[namespace.yaml](https://slurm.schedmd.com/namespace.yaml.html). This plugin can be configured
to create user and PID namespaces in addition to a temporary filesystem
namespace. Namespaces can be configured for all nodes or for a subset of nodes.
As an example, if all nodes will be configured the same way, you could put the
following in your namespace.yaml:
```text
defaults: auto_base_path: true base_path: "/var/nvme/storage"
```
Note the following important details with this plugin:
- This plugin requires cgroup/v2 to operate correctly.
- When using user namespaces, bpf token support (added in kernel 6.9) is required to use [ConstrainDevices](https://slurm.schedmd.com/cgroup.conf.html) in cgroup.conf .
### namespace/tmpfs plugin [#tmpfs_setup](https://slurm.schedmd.com/namespace.html)
The namespace/tmpfs plugin (formerly job_container/tmpfs) uses the
configuration file [job_container.conf](https://slurm.schedmd.com/job_container.conf.html).
Namespaces can be configured for all nodes, or for a subset of nodes. As an
example, if all nodes will be configured the same way, you could put the
following in your job_container.conf:
```text
AutoBasePath=true BasePath=/var/nvme/storage
```
## Initial Testing [#initial_testing](https://slurm.schedmd.com/namespace.html)
An easy way to verify that the container is working is to run a job and
ensure that the /tmp directory is empty (since it normally has some other
files) and that "." is owned by the user that submitted the job.
```text
tim@slurm-ctld:~$ srun ls -al /tmp total 8 drwx------ 2 tim root 4096 Feb 10 17:14 . drwxr-xr-x 21 root root 4096 Nov 15 08:46 ..
```
While a job is running, root should be able to confirm that
`/$BasePath/$JobID/_tmp` exists and is empty. This directory is bind
mounted into the job. `/$BasePath/$JobID` should be owned by root,
and is not intended to be accessible to the user.
Additionally, when the Linux plugin is in use, you can confirm that a
PID namespace is in effect by running a job and running "ps". The only visible
PIDs should be related to the job and PID 1 will be named slurmstepd:
[${job_id}.namespace] .
## SPANK[#spank](https://slurm.schedmd.com/namespace.html)
This plugin interfaces with the SPANK api, and automatically joins the job's
namespace in the following functions:
- spank_task_init_privileged()
- spank_task_init()
In addition to the job itself, the TaskProlog will also be executed inside
the container.
