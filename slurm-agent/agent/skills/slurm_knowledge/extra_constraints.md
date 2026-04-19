---
source_url: https://slurm.schedmd.com/extra_constraints.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:44 UTC
title: "Slurm Workload Manager - Extra Constraints"
---

# Extra Constraints
## Contents
- [Overview](https://slurm.schedmd.com/extra_constraints.html)
- [Configuration](https://slurm.schedmd.com/extra_constraints.html)
- [Node Extra Data](https://slurm.schedmd.com/extra_constraints.html)
- [Job Submission](https://slurm.schedmd.com/extra_constraints.html) [Syntax](https://slurm.schedmd.com/extra_constraints.html)
- [Warnings](https://slurm.schedmd.com/extra_constraints.html)
- [Valid and Invalid Requests](https://slurm.schedmd.com/extra_constraints.html)
- [Examples](https://slurm.schedmd.com/extra_constraints.html)
## Overview [#Overview](https://slurm.schedmd.com/extra_constraints.html)
Extra data may be added to a node, and jobs may request extra constraints
to filter nodes based on their extra data. This is disabled by
default, but may be enabled in slurm.conf. Warning : Slurm's backfill
scheduler cannot accurately plan nodes for jobs whose request extra constraints
are not immediately satisfied. This means that the more often extra data for
nodes is changed, the less accurate the backfill scheduler will be.
## Configuration [#Configuration](https://slurm.schedmd.com/extra_constraints.html)
- In slurm.conf, configure SchedulerParameters=extra_constraints
## Node Extra Data [#Node_Extra_Data](https://slurm.schedmd.com/extra_constraints.html)
A node's extra data is a json formatted string. It may be initialized on
slurmd startup with the --extra flag for slurmd. For example:
```text
slurmd --extra '{ "a": 1.23, "b": true, "c": 0, "foo": "bar", "zed": 23 }'
```
Or, it may be updated with scontrol. For example:
```text
scontrol update nodename=node123 extra='{ "a": 1.23, "b": true, "c": 0, "foo": "bar", "zed": 23 }'
```
This defines the features that may be requested by the --extra option in
salloc, sbatch, and srun. Values may be any string, number, or boolean value.
## Job Submission [#Job_Submission](https://slurm.schedmd.com/extra_constraints.html)
### Syntax [#Syntax](https://slurm.schedmd.com/extra_constraints.html)
The salloc, sbatch, or srun --extra field is an arbitrary string enclosed in
single or double quotes if using spaces or some special characters.
If SchedulerParameters=extra_constraints is enabled, this string is used
for node filtering based on the Extra field in each node.
The most basic request is structured like this:
```text
```
Key and value are arbitrary, non-empty strings that cannot contain any
characters that are part of operators and cannot contain parentheses. Thus,
the following characters are not allowed in a key or value:
```text
,&|<>=!()
```
The following comparison operators are allowed:
- = (equal to)
- != (not equal to)
- > (greater than)
- >= (greater than or equal to)
-
```
The following boolean operators are allowed:
```text
& (AND) , (AND) | (OR)
```
Any number of parentheses may be used to group requests together.
All boolean operators at any given level of parentheses must be identical.
Boolean operators at different levels of parentheses may be different.
For example, this is not allowed:
```text
a=1&b=2|c=foobar
```
But this is allowed:
```text
(a=1&b=2)|c=foobar
```
### Warnings [#Warnings](https://slurm.schedmd.com/extra_constraints.html)
Whitespace characters are not treated specially. Any whitespace characters will
be considered part of a key or value. This means that the following is invalid:
```text
--extra " (a=b)"
```
The space at he beginning is parsed as a key of a request. Then the opening
parenthesis character is recognized as an invalid character for either a key
or a comparison operator. This request would result in the job being rejected.
However, this is valid:
```text
--extra "( a=b)"
```
This has a single request. The key is " a", the comparison operator is "=", and
the value is "b".
This same warning applies to single and double quotes. These are not considered
special characters, and thus are part of a string. Thus, bar and "bar" are not
equal.
### Valid and Invalid Requests [#Valid](https://slurm.schedmd.com/extra_constraints.html)
Here are some examples of valid requests:
```text
a=1.23 a= b a!=1.24 a!=1.23|foo!=blah b=200 b=true foo =0.00000001) ((c =0.1)
```
Here are some examples of invalid requests:
Invalid comparison operator:
```text
a, =0.00000001) ((c =0.1)
```
The following --extra requests are not fulfilled by this node:
```text
a!=1.23 b=0 b=false foo>baz ((c =0.00001)
```
Reminder: in order for two numbers to be considered equal, their difference
must be less than 0.0001. This is why 0.0001 is not considered equal to 0 and
thus the request `c>=0.0001` is not fulfilled,
but 0.00000001 is considered equal to 0 and thus the request
`c>=0.00000001` is fulfilled.
A practical example might be to have a script that looks at the load average
of each node and updates the extra attribute for each node with the current
value. This would allow users to restrict their jobs to nodes whose load
average is below a certain threshold.
In this simple example, the three nodes in a cluster are being monitored and
the extra attribute is being populated with their load average.
```text
$ scontrol show nodes node[01-03] | grep -E 'NodeName|Extra' NodeName=node01 Arch=x86_64 CoresPerSocket=6 Extra={ "load": 0.99 } NodeName=node02 Arch=x86_64 CoresPerSocket=6 Extra={ "load": 0.75 } NodeName=node03 Arch=x86_64 CoresPerSocket=6 Extra={ "load": 0.45 }
```
A job can request to run on a machine with less than half of the CPU time
being utilized.
```text
$ sbatch -n12 --extra "load 0.5)" --wrap='srun sleep 10' Submitted batch job 11207 $ squeue JOBID PARTITION NAME USER ST TIME NODES NODELIST(REASON) 11207 debug wrap ben R 0:01 1 node02
```
