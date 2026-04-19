---
source_url: https://slurm.schedmd.com/pam_slurm_adopt.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:21:26 UTC
title: "Slurm Workload Manager - pam_slurm_adopt"
---

# pam_slurm_adopt
The purpose of this module is to prevent users from sshing into nodes that
they do not have a running job on, and to track the ssh connection and any
other spawned processes for accounting and to ensure complete job cleanup when
the job is completed. This module does this by determining the job which
originated the ssh connection. The user's connection is "adopted" into the
"external" step of the job. When access is denied, the user will receive a
relevant error message.
## Contents[#contents](https://slurm.schedmd.com/pam_slurm_adopt.html)
- [Installation](https://slurm.schedmd.com/pam_slurm_adopt.html)
- [Slurm Configuration](https://slurm.schedmd.com/pam_slurm_adopt.html)
- [SSH Configuration](https://slurm.schedmd.com/pam_slurm_adopt.html)
- [PAM Configuration](https://slurm.schedmd.com/pam_slurm_adopt.html)
- [Administrative Access Configuration](https://slurm.schedmd.com/pam_slurm_adopt.html)
- [pam_slurm_adopt Module Options](https://slurm.schedmd.com/pam_slurm_adopt.html)
- [Firewalls, IP Addresses, etc.](https://slurm.schedmd.com/pam_slurm_adopt.html)
- [SELinux](https://slurm.schedmd.com/pam_slurm_adopt.html)
- [Limitations](https://slurm.schedmd.com/pam_slurm_adopt.html)
## Installation [#INSTALLATION](https://slurm.schedmd.com/pam_slurm_adopt.html)
### Source:[#source](https://slurm.schedmd.com/pam_slurm_adopt.html)
In your Slurm source directory, navigate to ./contribs/pam_slurm_adopt/
and run the following as root :
```text
make && make install
```
This will place pam_slurm_adopt.a, pam_slurm_adopt.la,
and pam_slurm_adopt.so in /lib/security/ (on Debian systems) or
/lib64/security/ (on RedHat/SUSE systems). This install location
is not affected by configure's --prefix flag; use --with-pam_dir=PATH
to modify the install location if desired.
### RPM:[#rpm](https://slurm.schedmd.com/pam_slurm_adopt.html)
The included slurm.spec will build a slurm-pam_slurm RPM which will install
pam_slurm_adopt. Refer to the
[Quick Start Administrator Guide](https://slurm.schedmd.com/quickstart_admin.html) for instructions on managing an RPM-based install.
### DEB:[#deb](https://slurm.schedmd.com/pam_slurm_adopt.html)
The included debian packaging scripts will build the
slurm-smd-libpam-slurm-adopt package which will install pam_slurm_adopt.
[Quick Start Administrator Guide](https://slurm.schedmd.com/quickstart_admin.html) for instructions on managing an DEB-based install.
## Slurm Configuration [#SLURM_CONFIG](https://slurm.schedmd.com/pam_slurm_adopt.html)
PrologFlags=contain must be set in the slurm.conf. This sets up the
"extern" step into which ssh-launched processes will be adopted. You must also
enable the task/cgroup plugin in slurm.conf. See the
[Slurm cgroups guide.](https://slurm.schedmd.com/cgroups.html)
CAUTION This option must be in place before using this module.
The module bases its checks on local steps that have already been launched. Jobs
launched without this option do not have an extern step, so pam_slurm_adopt will
not have access to those jobs.
LaunchParameters=ulimit_pam_adopt will set RLIMIT_RSS in processes
adopted by the external step, similar to tasks running in regular steps.
The UsePAM option in slurm.conf is not related to pam_slurm_adopt.
## SSH Configuration [#ssh_config](https://slurm.schedmd.com/pam_slurm_adopt.html)
Verify that UsePAM is set to On in /etc/ssh/sshd_config (it
should be on by default).
Ensure that only supported AuthenticationMethods are enabled in
sshd_config (on the compute nodes). At this time, only publickey and
password are supported. In particular keyboard-interactive is
explicitly unsupported and must be removed from AuthenticationMethods .
If this step is not observed process adoption will be broken
and SSH sessions will persist even after the job ends. See
[Limitations](https://slurm.schedmd.com/pam_slurm_adopt.html) for more information.
## PAM Configuration [#PAM_CONFIG](https://slurm.schedmd.com/pam_slurm_adopt.html)
For initial testing (see warning below), add the following line to the
appropriate file in /etc/pam.d, such as system-auth or sshd (you may use either
the "required" or "sufficient" PAM control flag):
```text
account required pam_slurm_adopt.so
```
The order of plugins is very important. pam_slurm_adopt.so should be the
last PAM module in the account stack. Included files such as common-account
should normally be included before pam_slurm_adopt.
You might have the following account stack in sshd:
```text
account required pam_nologin.so account include password-auth ... -account required pam_slurm_adopt.so
```
Note the "-" before the account entry for pam_slurm_adopt. It allows
PAM to fail gracefully if the pam_slurm_adopt.so file is not found. If Slurm
is on a shared filesystem, such as NFS, then this is suggested to avoid being
locked out of a node while the shared filesystem is mounting or down.
pam_slurm_adopt must be used with the task/cgroup task plugin and the
proctrack/cgroup proctrack plugin.
The pam_systemd module will conflict with pam_slurm_adopt, so you need to
disable it in all files that are included in sshd or system-auth (e.g.
password-auth, common-session, etc.).
WARNING : The default configuration for pam_slurm_adopt is meant to
ensure an admin is not locked out of a node during testing. Production
environments should consider setting both
[action_adopt_failure](https://slurm.schedmd.com/pam_slurm_adopt.html) and
[action_generic_failure](https://slurm.schedmd.com/pam_slurm_adopt.html) to deny
after successful testing; otherwise, plugin failures may allow users to log in
unconfined. Future examples on this page will include these flags.
If you need the user management features from pam_systemd, such as
handling user runtime directory /run/user/$UID, you can have the prolog script
run 'loginctl enable-linger $SLURM_JOB_USER' and the epilog script disable
it again (after making sure there are no other jobs from this user on the node)
by running 'loginctl disable-linger $SLURM_JOB_USER'. You will also need to
export the XDG_* environment variables if your software requires them.
You can see an example of prolog and epilog scripts here:
Prolog:
```text
loginctl enable-linger $SLURM_JOB_USER exit 0
```
TaskProlog:
```text
echo "export XDG_RUNTIME_DIR=/run/user/$SLURM_JOB_UID" echo "export XDG_SESSION_ID=$(
action_no_jobs
[#action_no_jobs](https://slurm.schedmd.com/pam_slurm_adopt.html)
The action to perform if the user has no jobs on the node. Configurable
values are:
ignore
[#action_no_jobs_ignore](https://slurm.schedmd.com/pam_slurm_adopt.html)
Do nothing. Fall through to the next pam module.
deny (default)
[#action_no_jobs_deny](https://slurm.schedmd.com/pam_slurm_adopt.html)
Deny the connection.
action_unknown
[#action_unknown](https://slurm.schedmd.com/pam_slurm_adopt.html)
The action to perform when the user has multiple jobs on the node and
the RPC does not locate the source job. If the RPC mechanism works properly in
your environment, this option will likely be relevant only when
connecting from a login node. Configurable values are:
newest (default)
[#action_unknown_newest](https://slurm.schedmd.com/pam_slurm_adopt.html)
On systems with cgroup/v1 pick the newest job on the node.
The "newest" job is chosen based on the mtime of the job's step_extern cgroup;
asking Slurm would require an RPC to the controller. Thus, the memory cgroup
must be in use so that the code can check mtimes of cgroup directories. The user
can ssh in but may be adopted into a job that exits earlier than the
job they intended to check on. The ssh connection will at least be
subject to appropriate limits and the user can be informed of better
ways to accomplish their objectives if this becomes a problem.
NOTE : If the module fails to retrieve the cgroup mtime, then the picked
job may not be the newest one.
On systems with cgroup/v2 the newest is just the job with the greatest
id, and thus this does not ensure that it is really the newest job.
allow
[#action_unknown_allow](https://slurm.schedmd.com/pam_slurm_adopt.html)
Let the connection through without adoption.
deny
[#action_unknown_deny](https://slurm.schedmd.com/pam_slurm_adopt.html)
Deny the connection.
action_adopt_failure
[#action_adopt_failure](https://slurm.schedmd.com/pam_slurm_adopt.html)
The action to perform if the process is unable to be adopted into any
job for whatever reason. If the process cannot be adopted into the job
identified by the callerid RPC, it will fall through to the action_unknown
code and try to adopt there. A failure at that point or if there is only
one job will result in this action being taken. Configurable values are:
allow (default)
[#action_adopt_failure_allow](https://slurm.schedmd.com/pam_slurm_adopt.html)
Let the connection through without adoption.
WARNING : This value allows connections that were not able to be
adopted into a job, which could allow users complete access to a node, not just
to their allocated resources. This value is recommended for testing purposes
only, we recommend using "deny" in production systems.
deny
[#action_adopt_failure_deny](https://slurm.schedmd.com/pam_slurm_adopt.html)
Deny the connection.
action_generic_failure
[#action_generic_failure](https://slurm.schedmd.com/pam_slurm_adopt.html)
The action to perform if there are certain failures such as the
inability to talk to the local slurmd or if the kernel doesn't offer
the correct facilities. Configurable values are:
ignore (default)
[#action_generic_failure_ignore](https://slurm.schedmd.com/pam_slurm_adopt.html)
Do nothing. Fall through to the next PAM module, even if this module is set
as "required" or "requisite".
WARNING : This value does not deny connections pam_slurm_adopt was
unable to handle normally, which could allow users complete access to a node,
not just to their allocated resources. This value is recommended for testing
purposes only, we recommend using "deny" in production systems.
allow
[#action_generic_failure_allow](https://slurm.schedmd.com/pam_slurm_adopt.html)
Let the connection through without adoption.
WARNING : This value explicitly allows connections pam_slurm_adopt was
unable to handle normally, which could allow users complete access to a node,
not just to their allocated resources. This value is recommended for testing
purposes only, we recommend using "deny" in production systems.
deny
[#action_generic_failure_deny](https://slurm.schedmd.com/pam_slurm_adopt.html)
Deny the connection.
disable_x11
[#disable_x11](https://slurm.schedmd.com/pam_slurm_adopt.html)
Turn off Slurm built-in X11 forwarding support. Configurable values are:
0 (default)
[#disable_x11_0](https://slurm.schedmd.com/pam_slurm_adopt.html)
If the job the connection is adopted into has Slurm's X11 forwarding
enabled, the DISPLAY variable will be overwritten with the X11 tunnel
endpoint details.
1
[#disable_x11_1](https://slurm.schedmd.com/pam_slurm_adopt.html)
Do not check for Slurm's X11 forwarding support, and do not alter the
DISPLAY variable.
join_container
[#join_container](https://slurm.schedmd.com/pam_slurm_adopt.html)
Control the interaction with the namespace plugins.
Configurable values are:
true (default)
[#join_container_true](https://slurm.schedmd.com/pam_slurm_adopt.html)
Attempt to join a namespace created by the namespace plugins.
false
[#join_container_false](https://slurm.schedmd.com/pam_slurm_adopt.html)
Do not attempt to join a namespace.
log_level
[#log_level](https://slurm.schedmd.com/pam_slurm_adopt.html)
See [SlurmdDebug](https://slurm.schedmd.com/slurm.conf.html) in slurm.conf for available options.
The default log_level is info .
nodename
[#nodename](https://slurm.schedmd.com/pam_slurm_adopt.html)
If the NodeName defined in slurm.conf is different than this node's
hostname (as reported by hostname -s ), then this must be set to the
NodeName in slurm.conf that this host operates as.
service
[#service](https://slurm.schedmd.com/pam_slurm_adopt.html)
The pam service name for which this module should run. By default
it only runs for sshd for which it was designed for. A
different service name can be specified like "login" or "*" to
allow the module to in any service context. For local pam logins
this module could cause unexpected behavior or even security
issues. Therefore if the service name does not match then this
module will not perform the adoption logic and returns
PAM_IGNORE immediately.
### Firewalls, IP Addresses, etc. [#firewall](https://slurm.schedmd.com/pam_slurm_adopt.html)
slurmd should be accessible on any IP address from which a user might
launch ssh. The RPC to determine the source job must be able to reach the
slurmd port on that particular IP address. If there is no slurmd
on the source node, such as on a [login node](https://slurm.schedmd.com/quickstart_admin.html), it is better to have the RPC be
rejected rather than silently dropped. This will allow better responsiveness to
the RPC initiator.
### SELinux[#selinux](https://slurm.schedmd.com/pam_slurm_adopt.html)
SELinux may conflict with pam_slurm_adopt, but it is generally possible for
them to work side by side. This is an example type enforcement file that was
used on a fairly stock Debian system. It is provided to give some direction
and to show what is required to get this working but may require additional
modification.
```text
module pam_slurm_adopt 1.0; require { type sshd_t; type var_spool_t; type unconfined_t; type initrc_var_run_t; class sock_file write; class dir { read search }; class unix_stream_socket connectto; } #============= sshd_t ============== allow sshd_t initrc_var_run_t:dir search; allow sshd_t initrc_var_run_t:sock_file write; allow sshd_t unconfined_t:unix_stream_socket connectto; allow sshd_t var_spool_t:dir read; allow sshd_t var_spool_t:sock_file write;
```
It is possible for some plugins to require more permissions than this.
Notably, namespace/tmpfs will require something more like this:
```text
module pam_slurm_adopt 1.0; require { type nsfs_t; type var_spool_t; type initrc_var_run_t; type unconfined_t; type sshd_t; class sock_file write; class dir { read search }; class unix_stream_socket connectto; class fd use; class file read; class capability sys_admin; } #============= sshd_t ============== allow sshd_t initrc_var_run_t:dir search; allow sshd_t initrc_var_run_t:sock_file write; allow sshd_t nsfs_t:file read; allow sshd_t unconfined_t:fd use; allow sshd_t unconfined_t:unix_stream_socket connectto; allow sshd_t var_spool_t:dir read; allow sshd_t var_spool_t:sock_file write; allow sshd_t self:capability sys_admin;
```
## Limitations [#LIMITATIONS](https://slurm.schedmd.com/pam_slurm_adopt.html)
Internally, some AuthenticationMethods cause sshd to fork an extra process
during the login flow, which sshd partially offloads the authentication
dialogue to. This can confuse PAM modules, and may break process adoption
with pam_slurm_adopt.
When using SELinux support in Slurm, the session started via pam_slurm_adopt
won't necessarily be in the same context as the job it is associated with.
When using namespace/linux and the user namespace is configured, the
pam_limits module may not be able to set memlock, sigpending, msgqueue, nice, or
rtprio.
