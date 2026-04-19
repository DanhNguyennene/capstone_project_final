---
source_url: https://slurm.schedmd.com/authentication.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:20:47 UTC
title: "Slurm Workload Manager -"
---

# Authentication Plugins
## Overview[#Overview](https://slurm.schedmd.com/authentication.html)
It is important for Slurm to know that the Remote Procedure Calls (RPCs)
that it receives are coming from trusted sources. There are a few different
authentication mechanisms available within Slurm to verify the legitimacy and
integrity of the requests.
If you plan to change the authentication type, you will need to drain the
cluster of running jobs and stop all Slurm daemons before making the change.
Otherwise, requests can be made with the new type while the running daemons
still operate with the old type that was present when they started.
## MUNGE[#munge](https://slurm.schedmd.com/authentication.html)
MUNGE can be used to create and validate credentials. It allows Slurm to
authenticate the UID and GID of a request from another host that has matching
users and groups. MUNGE libraries must exist when building Slurm in order for
it to be able to use munge for authentication. All hosts in the cluster must
have a shared cryptographic key.
#### Setup[#munge_setup](https://slurm.schedmd.com/authentication.html)
- MUNGE requires that there be a shared key on the machines running slurmctld, slurmdbd and the nodes. You can create a key file by entering your own text or by generating random data: ```text dd if=/dev/random of=/etc/munge/munge.key bs=1024 count=1 ```
- This key should be owned by the "munge" user and should not be readable or writable by other users: ```text chown munge:munge /etc/munge/munge.key chmod 400 /etc/munge/munge.key ```
- Distribute the key file to the machines on the cluster. It needs to be on the machines running slurmctld, slurmdbd, slurmd and any submit hosts you have configured. Use the distribution method of your choice.
- The "munge" service should be running on any machines that need to use it for authentication. It should be enabled and started on all the machines you distributed a key to: ```text systemctl enable munge systemctl start munge ```
- Changing the authentication mechanism requires a restart of Slurm daemons. The daemons need to be stopped before updating the slurm.conf so that client commands do not use a mechanism other than what the running daemons are expecting.
- Update your slurm.conf and slurmdbd.conf to use MUNGE authentication. slurm.conf: ```text AuthType = auth/munge CredType = cred/munge ```
- slurmdbd.conf: ```text AuthType = auth/munge ```
- Start the Slurm daemons back up with the appropriate method for your cluster.
## Slurm[#slurm](https://slurm.schedmd.com/authentication.html)
Beginning with version 23.11, Slurm has its own plugin that can create and
validate credentials. It validates that the requests come from legitimate UIDs
and GIDs on other hosts with matching users and groups. All hosts in the
cluster must have a shared cryptographic key.
#### Single Key Setup[#single_key_setup](https://slurm.schedmd.com/authentication.html)
- For the authentication to happen correctly you must have a shared key on the machine running slurmctld, slurmdbd and the nodes. You can create a key file by entering your own text or by generating random data: ```text dd if=/dev/random of=/etc/slurm/slurm.key bs=1024 count=1 ```
- The slurm.key or slurm.jwks should be owned by SlurmUser and should not be readable or writable by other users. This example assumes the SlurmUser is 'slurm': ```text chown slurm:slurm /etc/slurm/slurm.key chmod 600 /etc/slurm/slurm.key ```
- Distribute the key file to the machines on the cluster. It needs to be on the machines running slurmctld, slurmdbd, slurmd and sackd.
- Update your slurm.conf and slurmdbd.conf to use the Slurm authentication type. slurm.conf: ```text AuthType = auth/slurm CredType = cred/slurm ```
- slurmdbd.conf: ```text AuthType = auth/slurm ```
- If not using systemd, create the runtime directories. (Systemd takes care of this automatically if you're starting the daemons using the provided service files). ```text mkdir /run/slurmctld /run/slurmdbd chown slurm:slurm /run/slurmctld /run/slurmdbd ```
- Start the daemons back up with the appropriate method for your cluster.
Beginning with version 24.05, you may alternatively create a slurm.jwks file
with multiple keys defined. The slurm.jwks file aids with key rotation, as
the cluster does not need to be restarted at once when a key is rotated.
Instead, an scontrol reconfigure is sufficient. There are no slurm.conf
parameters required to use the slurm.jwks file, instead, the presence of the
slurm.jwks file enables this functionality. If the slurm.jwks is not present or
cannot be read, the cluster defaults to the slurm.key.
#### Multiple Key Setup[#multiple_key_setup](https://slurm.schedmd.com/authentication.html)
Setup for multiple keys is very similar to the single key setup with the
exception of a richer key file. The key file is composed of one jwks-esque
"keys" list, with a number of "key" entries into this list. The key entries
have many different fields. An example file is below.
```text
{ "keys": [ { "alg": "HS256", "kty": "oct", "kid": "key-identifier", "k": "VGhlIGtleSBiZWxvdyBtZSBuZXZlciBsaWVz", "exp": 1718200800 }, { "alg": "HS256", "kty": "oct", "kid": "key-identifier-2", "k": "VGhlIGtleSBhYm92ZSBtZSBhbHdheXMgbGllcw==", "use": "default" } ] }
```
The following fields are used by auth/slurm. (Additional fields can be
present, but will be ignored.)
- alg — The cryptographic algorithm used with the key. This field is required, and the value MUST be HS256.
- kty — The family of cryptographic algorithms used to sign the key. This field is required, and the value MUST be oct.
- kid — The case-sensitive text identifier used for key matching. This field is required, and the text must be unique.
- k — The actual key, represented in a Base64 or Base64url encoded binary blob. This field is required, and must be longer than 16 bytes.
- use — Determines whether this key is the default key. Acceptable values are only "default", which denotes this key as the default key. There can only be one default key. This field is optional.
- exp — The expiration date of the key as a Unix timestamp. This field is optional.
Once the slurm.jwks file has been created, use the same process for setting
up auth/slurm as in the single key setup, except use the slurm.jwks file instead
of the slurm.key file.
If the cluster does not have access to consistent user ids from LDAP or
the operating system, you can use the
[use_client_ids](https://slurm.schedmd.com/slurm.conf.html) option to
allow it to use the Slurm authentication mechanism.
#### SACK[#sack](https://slurm.schedmd.com/authentication.html)
Slurm's internal authentication makes use of a subsystem — the
S lurm A uth and C red K iosk (SACK) —
that is responsible for handling requests from the auth/slurm and
cred/slurm plugins. This subsystem is automatically started and managed
internally by the slurmctld, slurmdbd, and slurmd daemons on each system with no
need to run a separate daemon.
For login nodes not running one of these Slurm daemons, the sackd
daemon should be run to allow the Slurm client commands to authenticate to
the rest of the cluster. This daemon can also manage cached configuration files
for [configless](https://slurm.schedmd.com/configless_slurm.html) environments.
Beginning with version 25.05, it's possible for multiple sackd daemons
to co-exist on the same login node by changing the RuntimeDirectory option in
separate systemd service files. Clients can authenticate against different sackd
daemons on the same login node by managing the SLURM_CONF environment
variable to point at the different cluster configuration files. Refer to the
[sackd(8)](https://slurm.schedmd.com/sackd.html) manual for more information.
## JWT[#jwt](https://slurm.schedmd.com/authentication.html)
Slurm can be configured to use JSON Web Tokens (JWT) for authentication
purposes. This is configured with the AuthAltType parameter and is used only
for client to server communication. You can read more about this authentication
mechanism and how to install it [here](https://slurm.schedmd.com/jwt.html).
