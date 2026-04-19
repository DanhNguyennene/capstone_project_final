---
source_url: https://slurm.schedmd.com/rest_quickstart.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:21:44 UTC
title: "Slurm Workload Manager - REST API Quick Start Guide"
---

# REST API Quick Start Guide
Slurm provides a [REST API](https://restfulapi.net/) through the
slurmrestd daemon, using [JSON Web Tokens](https://slurm.schedmd.com/jwt.html) for
authentication. This daemon is designed to allow clients to communicate with
Slurm via a REST API (in addition to the command line interface (CLI) or C API).
This page provides a brief tutorial for setting up these components.
See also:
- [REST API Details](https://slurm.schedmd.com/rest.html)
- [REST API Methods and Models](https://slurm.schedmd.com/rest_api.html)
- [slurmrestd man page](https://slurm.schedmd.com/slurmrestd.html)
- [OpenAPI Plugin Release Notes](https://slurm.schedmd.com/openapi_release_notes.html)
- [REST API Client Guide](https://slurm.schedmd.com/rest_clients.html)
## Contents[#contents](https://slurm.schedmd.com/rest_quickstart.html)
- [Prerequisites](https://slurm.schedmd.com/rest_quickstart.html)
- [Quick Start](https://slurm.schedmd.com/rest_quickstart.html) [Running with systemd](https://slurm.schedmd.com/rest_quickstart.html)
- [Customizing slurmrestd.service](https://slurm.schedmd.com/rest_quickstart.html)
- [Basic Usage](https://slurm.schedmd.com/rest_quickstart.html) [Token management](https://slurm.schedmd.com/rest_quickstart.html)
- [Advanced Usage](https://slurm.schedmd.com/rest_quickstart.html)
- [Common Issues](https://slurm.schedmd.com/rest_quickstart.html) [Unable to bind socket](https://slurm.schedmd.com/rest_quickstart.html)
- [Connection refused](https://slurm.schedmd.com/rest_quickstart.html)
- [Protocol authentication error (HTTP 500)](https://slurm.schedmd.com/rest_quickstart.html)
- [Unable to find requested URL (HTTP 404)](https://slurm.schedmd.com/rest_quickstart.html)
- [Rejecting thread config token (HTTP 401)](https://slurm.schedmd.com/rest_quickstart.html)
- [Unexpected URL character (HTTP 400)](https://slurm.schedmd.com/rest_quickstart.html)
- [Other Slurm commands not working](https://slurm.schedmd.com/rest_quickstart.html)
## Prerequisites [#prereq](https://slurm.schedmd.com/rest_quickstart.html)
The following development libraries are required at compile time
in order for slurmrestd to be compiled (minimum versions are on the related
software page linked below):
- [HTTP Parser](https://slurm.schedmd.com/related_software.html)
- [JSON-C](https://slurm.schedmd.com/related_software.html)
The following development libraries are optional; if present at compile time
the related functionality will be available:
- [YAML](https://slurm.schedmd.com/related_software.html) (YAML support)
- [JWT](https://slurm.schedmd.com/related_software.html) (authentication for socket-based clients)
- [s2n](https://slurm.schedmd.com/tls.html) (TLS communications)
It is generally recommended that you have
[slurmdbd](https://slurm.schedmd.com/slurmdbd.html) set up for
[accounting](https://slurm.schedmd.com/accounting.html). Without slurmdbd you may need to
start slurmrestd with the [-s](https://slurm.schedmd.com/slurmrestd.html)
flag to tell it not to load the slurmdbd plugin.
## Quick Start [#quick_start](https://slurm.schedmd.com/rest_quickstart.html)
This may be done on a dedicated REST API machine or
your existing 'slurmctld' machine, depending on demand.
If you have multiple clusters, you will need a unique instance of
slurmrestd for each cluster.
- Install components for slurmrestd DEB: slurm-smd slurm-smd-slurmrestd
- RPM: slurm slurm-slurmrestd (requires --with slurmrestd at build time)
- Set up [JSON Web Tokens](https://slurm.schedmd.com/jwt.html) for authentication
- Ensure /etc/slurm/slurm.conf is present and correct for your cluster (see [Quick Start Admin Guide](https://slurm.schedmd.com/quickstart_admin.html) and [slurm.conf man page](https://slurm.schedmd.com/slurm.conf.html))
- Run slurmrestd (see [below](https://slurm.schedmd.com/rest_quickstart.html) for systemd instructions) on your preferred [HOST]:PORT combination (':6820' is the default for production) ```text export SLURM_JWT=daemon export SLURMRESTD_DEBUG=debug slurmrestd : ``` Adjust SLURMRESTD_DEBUG to the desired level of output (as described on the [man page](https://slurm.schedmd.com/slurmrestd.html))
### Running with systemd [#systemd](https://slurm.schedmd.com/rest_quickstart.html)
Slurm ships with a slurmrestd service unit for systemd,
however, it might require some additional setup to run properly.
This section assumes you have either installed slurmrestd using DEB/RPM packages
or built it manually such that the files are in the same places.
Note the versions associated with certain steps in the instructions
below; these steps should be ignored on other versions.
- Create a local service account and group of slurmrestd to run the slurmrestd daemon. To prevent privilege escalation, the user account should be: Not root or SlurmUser
- Not used by real users or for any other functions
- Not granted any special permissions
```text
sudo useradd -M -r -s /usr/sbin/nologin -U slurmrestd
```
- If needed, sites can run systemctl edit slurmrestd to override the default User and Group to the site specific user and group: ```text [Service] User=slurmrestd Group=slurmrestd ```
- (Slurm 24.05 and newer) Optional: Customize the socket for slurmrestd. By default it will listen only on TCP port 6820. You may change this behavior by changing SLURMRESTD_LISTEN (see [Customizing slurmrestd.service](https://slurm.schedmd.com/rest_quickstart.html)).
- (Slurm 23.11 and earlier) Configure the socket for slurmrestd. This may be accomplished by creating/changing permissions on the parent directory and/or changing the path to the socket in the service file. Permissions : The user running the service must have write+execute permissions on the directory that will contain the UNIX socket
- Changing socket : On Slurm 23.11, the way to change or disable the socket is to modify the 'ExecStart' line of the service Run systemctl edit slurmrestd
- Add the following contents to the [Service] section: ```text ExecStart= ExecStart=/usr/sbin/slurmrestd $SLURMRESTD_OPTIONS Environment=SLURMRESTD_LISTEN=:6820 ```
- Adjust the assignment of SLURMRESTD_LISTEN to contain the socket(s) you want the daemon to listen on.
- After a future upgrade to Slurm 24.05+, the 'ExecStart' overrides will be unnecessary but will not conflict with the newer version.
### Customizing slurmrestd.service [#customization](https://slurm.schedmd.com/rest_quickstart.html)
The Slurm 24.05 release changes the operation of
the default service file and may break existing overrides. If you have
overridden `ExecStart=` to contain any TCP/UNIX sockets directly, it
will cause the service to fail if it duplicates any sockets contained in
SLURMRESTD_LISTEN. These overrides will need to be changed after upgrading.
The default `slurmrestd.service` file has two intended ways of
customizing its operation:
- Environment files : The service will read environment variables from two files: /etc/default/slurmrestd and /etc/sysconfig/slurmrestd . You may set any environment variables recognized by [slurmrestd](https://slurm.schedmd.com/slurmrestd.html), but the following are particularly relevant: SLURMRESTD_OPTIONS : CLI options to add to the slurmrestd command (see [slurmrestd](https://slurm.schedmd.com/slurmrestd.html))
- SLURMRESTD_LISTEN : Comma-delimited list of host:port pairs or unix:$SOCKET_PATH sockets to listen on NOTE : If this duplicates what is already set in the 'ExecStart' line in the service file, it will fail. Starting in Slurm 24.05, the default service file contains no sockets in 'ExecStart' and fully relies on this variable to contain the desired sockets.
- Service editing : Systemd has a built in way to edit services by running systemctl edit slurmrestd . This will create an override file in '/etc/systemd/' containing directives that will add to or replace directives in the default unit in '/lib/systemd/'.
- The override file must have the appropriate section declaration(s) for the directives you use (e.g., [Service] ).
- Environment variables may be set with Environment=NAME=value (refer to systemd documentation for more details)
- Changes may be reverted by running systemctl revert slurmrestd
## Basic Usage [#basic_usage](https://slurm.schedmd.com/rest_quickstart.html)
- Find the latest supported API version ```text slurmrestd -d list ```
- Get an authentication token for JWT ```text unset SLURM_JWT; export $(scontrol token) ``` This ensures an old token doesn't prevent a new one from being issued
- By default, tokens will expire after 1800 seconds (30 minutes). Add lifespan=SECONDS to the 'scontrol' command to change this.
- Run a basic curl command to hit the API when listening on a TCP host:port ```text curl -s -o "/tmp/curl.log" -k -vvvv \ -H X-SLURM-USER-TOKEN:$SLURM_JWT \ -X GET 'http:// : /slurm/v0.0. /diag' ``` Replace the server , port , and api-version with the appropriate values.
- Examine the output to ensure the response was 200 OK , and examine /tmp/curl.log for a valid JSON response.
- Try other endpoints described in the [API Methods and Models](https://slurm.schedmd.com/rest_api.html). Change GET to the correct method for the endpoint.
- Alternate command to use the UNIX socket instead ```text curl -s -o "/tmp/curl.log" -k -vvvv \ -H X-SLURM-USER-TOKEN:$SLURM_JWT \ --unix-socket /path/to/slurmrestd.socket \ 'http:// /slurm/v0.0. /diag' ``` Replace the path , server , and api-version with the appropriate values.
- Examine the output to ensure the response was 200 OK , and examine /tmp/curl.log for a valid JSON response.
### Token management [#tokens](https://slurm.schedmd.com/rest_quickstart.html)
This guide provides a simple overview using `scontrol` to
obtain tokens. This is a basic introductory approach that in many cases
should be disabled in favor of more sophisticated token management.
Refer to the [JWT page](https://slurm.schedmd.com/jwt.html) for more details.
## Advanced Usage [#advanced_usage](https://slurm.schedmd.com/rest_quickstart.html)
Information about ways to further customize and configure slurmrestd,
including authentication methods, run modes, plugins, high availability, proxies,
and Python client is found on the [REST API Details](https://slurm.schedmd.com/rest.html) page.
## Common Issues [#common_issues](https://slurm.schedmd.com/rest_quickstart.html)
In general, look out for these things:
- Validity of authentication token in SLURM_JWT
- Hostname and port number
- API version and endpoint
- Log output of slurmrestd
### Unable to bind socket [#bind_socket](https://slurm.schedmd.com/rest_quickstart.html)
This may be due to a permissions issue while attempting to set up the socket.
Check the log output from slurmrestd for the path to the socket.
Ensure that the user running the slurmrestd service has permissions to the
parent directory of the configured socket path, or change/remove the socket path
as [described above](https://slurm.schedmd.com/rest_quickstart.html).
If it says " Address already in use ", check the command being run
and the contents of "SLURMRESTD_LISTEN" for duplicates of the same TCP or UNIX
socket.
### Connection refused [#connection_refused](https://slurm.schedmd.com/rest_quickstart.html)
Verify that slurmrestd is running and listening on the port you are
attempting to connect to.
### Protocol authentication error (HTTP 500) [#authentication_error](https://slurm.schedmd.com/rest_quickstart.html)
One common authentication problem is an expired token. Request a new one:
```text
unset SLURM_JWT; export $(scontrol token)
```
This solution also applies to an HTTP 401 error caused by no authentication
token being sent at all. This may appear in the slurmrestd logs as
"Authentication does not apply to request."
Otherwise, consult the logs on the slurmctld and slurmdbd .
### Unable to find requested URL (HTTP 404) [#invalid_url](https://slurm.schedmd.com/rest_quickstart.html)
Check the [API Methods and Models](https://slurm.schedmd.com/rest_api.html) page to ensure
you're using a valid URL and the correct method for it. Pay attention to the
path as there are different endpoints for slurm and slurmdbd .
### Rejecting thread config token (HTTP 401) [#rejected_token](https://slurm.schedmd.com/rest_quickstart.html)
Check that slurmrestd has loaded the auth/jwt plugin.
You should see a debug message like this:
```text
slurmrestd: debug: auth/jwt: init: JWT authentication plugin loaded
```
If it didn't load jwt, run this in the terminal you're using for slurmrestd:
```text
export SLURM_JWT=daemon
```
### Unexpected URL character (HTTP 400) [#unexpected_character](https://slurm.schedmd.com/rest_quickstart.html)
Check the request URL and slurmrestd logs for characters that may be causing
the URL to be parsed incorrectly. Use the appropriate URL encoding sequence in
place of the problematic character (e.g., / = %2F ).
```text
... -X GET "localhost:8080/slurmdb/v0.0.40/jobs?submit_time=02/28/24" ### 400 BAD REQUEST ... -X GET "localhost:8080/slurmdb/v0.0.40/jobs?submit_time=02%2F28%2F24" ### 200 OK
```
### Other slurm commands not working [#slurm_commands](https://slurm.schedmd.com/rest_quickstart.html)
If SLURM_JWT is set, other slurm commands will attempt to use JWT
authentication, causing failures. This can be fixed by clearing the variable:
```text
unset SLURM_JWT
```
