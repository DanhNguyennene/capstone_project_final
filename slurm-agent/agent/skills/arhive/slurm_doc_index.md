# Slurm Official Documentation Index

**When to use:** User asks documentation, syntax, or best-practice questions for Slurm commands.
**Official source:** https://slurm.schedmd.com/documentation.html
**Refreshed:** 2026-04-19 04:20:42 UTC
**Corpus directory:** /mnt/e/workspace/uni/capstone_project/slurm-agent/agent/skills/slurm_knowledge
**Pages indexed:** 139

## Agent Routing
- Use lookup_slurm_docs first for Slurm documentation questions.
- Use concise topic queries to retrieve high-signal snippets quickly.
- Fall back to web_search only when local corpus misses the topic.

## Suggested Queries
- lookup_slurm_docs(query="sbatch dependency afterok")
- lookup_slurm_docs(query="scancel array parent id")
- lookup_slurm_docs(query="scontrol hold release requeue")
- lookup_slurm_docs(query="job state codes pending running failed")
- lookup_slurm_docs(query="sacct format fields")
- lookup_slurm_docs(query="sinfo node state drained reason")
- lookup_slurm_docs(query="gres gpu syntax")
- lookup_slurm_docs(query="qos maxjobs maxcpus")

## Sample Pages
- Slurm System Configuration Tool (https://slurm.schedmd.com/configurator.easy.html) -> configurator.easy.md
- Slurm System Configuration Tool (https://slurm.schedmd.com/configurator.html) -> configurator.md
- Slurm Workload Manager - (https://slurm.schedmd.com/authentication.html) -> authentication.md
- Slurm Workload Manager - (https://slurm.schedmd.com/configless_slurm.html) -> configless_slurm.md
- Slurm Workload Manager - (https://slurm.schedmd.com/contributor.html) -> contributor.md
- Slurm Workload Manager - (https://slurm.schedmd.com/release_notes.html) -> release_notes.md
- Slurm Workload Manager - (https://slurm.schedmd.com/rest_api.html) -> rest_api.md
- Slurm Workload Manager - (https://slurm.schedmd.com/tls.html) -> tls.md
- Slurm Workload Manager - (https://slurm.schedmd.com/certmgr.html) -> certmgr.md
- Slurm Workload Manager - Accounting and Resource Limits (https://slurm.schedmd.com/accounting.html) -> accounting.md
- Slurm Workload Manager - Adding Files or Plugins to Slurm (https://slurm.schedmd.com/add.html) -> add.md
- Slurm Workload Manager - Advanced Resource Reservation Guide (https://slurm.schedmd.com/reservations.html) -> reservations.md
- Slurm Workload Manager - CPU Management User and Administrator Guide (https://slurm.schedmd.com/cpu_management.html) -> cpu_management.md
- Slurm Workload Manager - Classic Fairshare Algorithm (https://slurm.schedmd.com/classic_fair_share.html) -> classic_fair_share.md
- Slurm Workload Manager - Consumable Resources in Slurm (https://slurm.schedmd.com/cons_tres.html) -> cons_tres.md
- Slurm Workload Manager - Containers Guide (https://slurm.schedmd.com/containers.html) -> containers.md
- Slurm Workload Manager - Control Group in Slurm (https://slurm.schedmd.com/cgroups.html) -> cgroups.md
- Slurm Workload Manager - Control Group v2 plugin (https://slurm.schedmd.com/cgroup_v2.html) -> cgroup_v2.md
- Slurm Workload Manager - Core Specialization (https://slurm.schedmd.com/core_spec.html) -> core_spec.md
- Slurm Workload Manager - Depth-Oblivious Fair-share Factor (https://slurm.schedmd.com/priority_multifactor3.html) -> priority_multifactor3.md

## Web Fallback
- If local corpus misses a topic, use: web_search(query="site:slurm.schedmd.com <topic>")
