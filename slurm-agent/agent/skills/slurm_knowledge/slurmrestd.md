---
source_url: https://slurm.schedmd.com/slurmrestd.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:25 UTC
title: "Slurm Workload Manager - slurmrestd"
---

# slurmrestd
Section: Slurm REST Daemon (8)
Updated: Slurm REST Daemon
[Index](https://slurm.schedmd.com/slurmrestd.html)
## NAME[#SECTION_NAME](https://slurm.schedmd.com/slurmrestd.html)
slurmrestd - Interface to Slurm via REST API.
## SYNOPSIS[#SECTION_SYNOPSIS](https://slurm.schedmd.com/slurmrestd.html)
slurmrestd [ OPTIONS ...] < [host]:port | unix:/path/to/socket >...
## DESCRIPTION[#SECTION_DESCRIPTION](https://slurm.schedmd.com/slurmrestd.html)
slurmrestd is REST API interface for Slurm. It can be used in two modes:
Inetd Mode : slurmrestd will read and write to STDIO. If STDIN is a socket
file descriptor, then slurmrestd will detect this and use relevant
functionality. This mode is designed to work with piped input, inetd, xinetd or
systemd socket activation.
Listen Mode : slurmrestd will open a listening socket on each requested
host : port pair or UNIX socket.
## OPTIONS[#SECTION_OPTIONS](https://slurm.schedmd.com/slurmrestd.html)
[[https://][host]:port](https://][host]:port) [https://][host]:port](https://][host]:port)" href="#OPT_[ https://][host]:port "> Hostname and port to listen against. host may be an IPv4/IPv6 IP or a
resolvable hostname. Hostnames are only looked up at startup and do not change
for the life of the process. host is optional; if not provided, slurmrestd
will listen on all network interfaces. https:// is optional; if not
provided, slurmrestd will automatically use TLS plugin to encrypt traffic when
possible. If https:// is specified; slurmrestd will require the configured
TLS plugin to encrypt traffic.
[unix:///path/to/socket](unix:///path/to/socket) [unix:///path/to/socket](unix:///path/to/socket)" href="#OPT_ unix:///path/to/socket "> Listen on local UNIX socket. Must have permission to create socket in
filesystem.
-a <plugin> [,plugin]...[#OPT_-a-
](https://slurm.schedmd.com/slurmrestd.html) Comma-delimited list of authentication plugins to load.
By default all available authentication plugins will be loaded.
list [#OPT_list](https://slurm.schedmd.com/slurmrestd.html) Display a list of the possible plugins to load.
rest_auth/local [#OPT_rest_auth/local](https://slurm.schedmd.com/slurmrestd.html) Allows authentication via UNIX sockets when auth/munge is active.
NOTE : slurmrestd and client processes must run under the same UID or the
client requests will be rejected.
rest_auth/jwt [#OPT_rest_auth/jwt](https://slurm.schedmd.com/slurmrestd.html) Allows authentication via TCP and UNIX sockets when AuthAltTypes=auth/jwt
is active. User must specify the following HTTP cookies with each request:
X-SLURM-USER-NAME :<user name>[#OPT_X-SLURM-USER-NAME](https://slurm.schedmd.com/slurmrestd.html)
X-SLURM-USER-TOKEN :<JSON Web Token>[#OPT_X-SLURM-USER-TOKEN](https://slurm.schedmd.com/slurmrestd.html)
NOTE : Tokens are usually generated via calling " scontrol token ".
-d <plugin> [,plugin]...[#OPT_-d-
](https://slurm.schedmd.com/slurmrestd.html) Comma-delimited list of data_parser plugins, which will determine the
output format. May include optional flags denoted by '+' symbol. By default all
available data_parser plugins will be loaded without any optional flags.
See also -s for OpenAPI plugins controlling the available content.
Defaults: all builtin supported data_parser plugins.
list[+flags] [#OPT_list[+flags]](https://slurm.schedmd.com/slurmrestd.html) Display a list of the possible plugins to load.
latest [#OPT_latest](https://slurm.schedmd.com/slurmrestd.html) Automatically replaced with latest plugin version. See relevant plugin for
description and potential flags.
[data_parser/]v0.0.40[+fast] [#OPT_[data_parser/]v0.0.40[+fast]](https://slurm.schedmd.com/slurmrestd.html) Load data_parser/]v0.0.40 plugin to for formatting of data. Only compatible
with openapi/slurmctld and openapi/slurmdbd content plugins.
+fast [#OPT_+fast](https://slurm.schedmd.com/slurmrestd.html) Disable builtin warnings and other logic to strictly validate
incoming requests. Should only ever be used in a production environment with
very well tested clients and potentially malformatted requests will be accepted
as given and no warnings will be generated about ignored or incorrect fields or
values.
[data_parser/]v0.0.41[+fast][+prefer_refs] [#OPT_[data_parser/]v0.0.41[+fast][+prefer_refs]](https://slurm.schedmd.com/slurmrestd.html) Load data_parser/]v0.0.41 plugin to for formatting of data. Only compatible
with openapi/slurmctld and openapi/slurmdbd content plugins.
+fast [#OPT_+fast_1](https://slurm.schedmd.com/slurmrestd.html) Disable builtin warnings and other logic to strictly validate
incoming requests. Should only ever be used in a production environment with
very well tested clients and potentially malformatted requests will be accepted
as given and no warnings will be generated about ignored or incorrect fields or
values.
+prefer_refs [#OPT_+prefer_refs](https://slurm.schedmd.com/slurmrestd.html) Prefer inline expansion of referenced schemas (via $ref ) in generated
OpenAPI specifications if the schema is only referenced once.
[data_parser/]v0.0.42[+fast][+minimize_refs][+inline_enums] [#OPT_[data_parser/]v0.0.42[+fast][+minimize_refs][+inline_enums]](https://slurm.schedmd.com/slurmrestd.html) Load data_parser/]v0.0.42 plugin to for formatting of data. Only compatible
with openapi/slurmctld and openapi/slurmdbd content plugins.
+fast [#OPT_+fast_2](https://slurm.schedmd.com/slurmrestd.html) Disable builtin warnings and other logic to strictly validate
incoming requests. Should only ever be used in a production environment with
very well tested clients and potentially malformatted requests will be accepted
as given and no warnings will be generated about ignored or incorrect fields or
values.
+minimize_refs [#OPT_+minimize_refs](https://slurm.schedmd.com/slurmrestd.html) Avoid inline expansion of referenced schemas (via $ref ) in generated
OpenAPI specifications if the schema is only referenced once.
+inline_enums [#OPT_+inline_enums](https://slurm.schedmd.com/slurmrestd.html) Avoid inline expansion of referenced schemas (via $ref ) in generated
OpenAPI specifications for enum arrays.
[data_parser/]v0.0.43[+fast][+minimize_refs] [#OPT_[data_parser/]v0.0.43[+fast][+minimize_refs]](https://slurm.schedmd.com/slurmrestd.html) Load data_parser/]v0.0.43 plugin to for formatting of data. Only compatible
with openapi/slurmctld and openapi/slurmdbd content plugins.
+fast [#OPT_+fast_3](https://slurm.schedmd.com/slurmrestd.html) Disable builtin warnings and other logic to strictly validate
incoming requests. Should only ever be used in a production environment with
very well tested clients and potentially malformatted requests will be accepted
as given and no warnings will be generated about ignored or incorrect fields or
values.
+minimize_refs [#OPT_+minimize_refs_1](https://slurm.schedmd.com/slurmrestd.html) Avoid inline expansion of referenced schemas (via $ref ) in generated
OpenAPI specifications if the schema is only referenced once.
[data_parser/]v0.0.44[+fast][+minimize_refs] [#OPT_[data_parser/]v0.0.44[+fast][+minimize_refs]](https://slurm.schedmd.com/slurmrestd.html) Load data_parser/]v0.0.44 plugin to for formatting of data. Only compatible
with openapi/slurmctld , openapi/slurmdbd , and openapi/util
content plugins.
+fast [#OPT_+fast_4](https://slurm.schedmd.com/slurmrestd.html) Disable builtin warnings and other logic to strictly validate
incoming requests. Should only ever be used in a production environment with
very well tested clients and potentially malformatted requests will be accepted
as given and no warnings will be generated about ignored or incorrect fields or
values.
+minimize_refs [#OPT_+minimize_refs_2](https://slurm.schedmd.com/slurmrestd.html) Avoid inline expansion of referenced schemas (via $ref ) in generated
OpenAPI specifications if the schema is only referenced once.
-f <file> [#OPT_-f- ](https://slurm.schedmd.com/slurmrestd.html) Read Slurm configuration from the specified file. See NOTES below.
--generate-openapi-spec [#OPT_generate-openapi-spec](https://slurm.schedmd.com/slurmrestd.html) Dump JSON formatted OpenAPI specification to stdout and exit immediately.
Loads minimal plugins required. All "content" fields will only be in JSON
format even if the serializer/yaml plugin is present and loadable.
Loading of [slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) can be disabled by passing additional
arguments -f /dev/null or setting SLURM_CONF =/dev/null in the
environment.
-g <group id> [#OPT_-g- ](https://slurm.schedmd.com/slurmrestd.html) Change group id (and drop supplemental groups) before processing client
request. This should be a unique group with no write access or special
permissions. Do not set this to the group belonging to to SlurmUser or
root or the daemon won't start with the default settings.
-h , --help [#OPT_help](https://slurm.schedmd.com/slurmrestd.html) Help; print a brief summary of command options.
--max-connections <count> [#OPT_max-connections- ](https://slurm.schedmd.com/slurmrestd.html) Set the maximum number of connections to process at any one time. This is
independent of the number of connections that can connect to slurmrestd at any
one time. The kernel allows any number of connections to be pending for
processing at any one time when SYN cookies are active.
Caution :[#OPT_Caution](https://slurm.schedmd.com/slurmrestd.html) Each connection could cause one RPC to the controller daemons, leading to
potential overloading of the controller. Each connection can also hold memory
for the duration of the life of the connection. Having too many connections
processing at once could use considerably more memory. Process limits
( [ulimit](https://slurm.schedmd.com/ulimit.html) (3)) may require adjustment when this value is increased.
Default: 124
-s <plugin> [,plugin]...[#OPT_-s-
](https://slurm.schedmd.com/slurmrestd.html) Comma-delimited list of OpenAPI plugins to load, which will determine the
available content. By default, OpenAPI plugins loaded will be
slurmctld,slurmdbd when
AccountingStorageType = accounting_storage/slurmdbd is configured in
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) or slurmctld for any other configuration.
See also -d for the data_parser plugins controlling the output format.
list [#OPT_list_1](https://slurm.schedmd.com/slurmrestd.html) Display a list of the possible plugins to load.
[openapi/]slurmctld [#OPT_[openapi/]slurmctld](https://slurm.schedmd.com/slurmrestd.html) Provides 'slurm/' endpoints for the loaded data_parser plugins.
[openapi/]slurmdbd [#OPT_[openapi/]slurmdbd](https://slurm.schedmd.com/slurmrestd.html) Provides 'slurmdb/' endpoints for the loaded data_parser plugins. This plugin
will fail if accounting_storage/slurmdbd is not used in the cluster.
[openapi/]util [#OPT_[openapi/]util](https://slurm.schedmd.com/slurmrestd.html) Provides 'util/' endpoints for the loaded data_parser plugins. Util is short for
utility. It provides utilities available directly through slurmrestd.
-t <THREAD COUNT> [#OPT_-t-
](https://slurm.schedmd.com/slurmrestd.html) Specify number of threads to use to process client connections.
Ignored in inetd mode.
-u <user id> [#OPT_-u- ](https://slurm.schedmd.com/slurmrestd.html) Change user id before processing client request. This should be a unique group
with no write access or special permissions. Do not set this user to SlurmUser
or root or the daemon won't start with the default settings.
-v [#OPT_-v](https://slurm.schedmd.com/slurmrestd.html) Verbose operation. Multiple v 's can be specified, with each ' v '
beyond the first increasing verbosity, up to 6 times (i.e. -vvvvvv).
Higher verbosity levels will have significant performance impact. See
SLURMRESTD_DEBUG for description of logging targets.
-V [#OPT_-V](https://slurm.schedmd.com/slurmrestd.html) Print version information and exit.
## TLS[#SECTION_TLS](https://slurm.schedmd.com/slurmrestd.html)
slurmrestd supports TLS encrypion via the TLS plugin interface. For a detailed
description of TLS support in Slurm, see <[https://slurm.schedmd.com/tls.html](https://slurm.schedmd.com/tls.html)>.
slurmrestd supports TLS encryption for incoming HTTPS connections independently
of how TLSType in [slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) is configured. The configuration of
TLSParameters in [slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) is always applied. This allows the
Slurm RPC layer to remain unencrypted via TLS while allowing slurmrestd to
service HTTPS requests via TLS.
slurmrestd includes automatic detection of incoming TLS connections. If TLS
plugin is fully configured and successfully loads at startup, then all new
incoming connections will be fingerprinted for SSLv3 (per RFC#6101) and TLSv1.x
(per RFC#8446) handshakes. Upon a matching fingerprint, each incoming
connections will then be encrypted via the configured TLS plugin for the
duration of the connection. Support for TLS is handled independently of if the
connection is a [ [unix](https://slurm.schedmd.com/unix.html) (2)] [socket](https://slurm.schedmd.com/socket.html) (2) or [pipe](https://slurm.schedmd.com/pipe.html)(2) (in INETD
mode). Listening connections created with https:// will be required to be
encrypted via the TLS plugin. Any incoming connections to these listeners
without TLS encryption will be closed immediately without sending an error
response the client.
TLS support in slurmrestd is dependent on the requirements of the TLS plugin.
slurmrestd will attempt to load the first available TLS plugin (except
tls/none ) automatically at startup. The requirements for each plugin are
listed below:
tls/s2n [#OPT_tls/s2n](https://slurm.schedmd.com/slurmrestd.html) The following files must be present and readable by the invoking user (before
-u <user id> is applied) at startup:
restd_cert_file.pem [#OPT_restd_cert_file.pem](https://slurm.schedmd.com/slurmrestd.html) TLS x509 server public certificate. Must be signed by CA trusted by clients.
The certificate's CN (common name) must match the hostname. slurmrestd
ignores the host in client HTTP requests but most TLS clients will require they
match.
Note: The certificate's file must be placed in the [autoconf](https://slurm.schedmd.com/autoconf.html)(1)
installation directory variable sysconfdir which can be overridden via setting
TLSParameters = restd_cert_file= /path/to/restd_cert_file.pem in
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5).
restd_cert_key_file.pem [#OPT_restd_cert_key_file.pem](https://slurm.schedmd.com/slurmrestd.html) Private key for restd_cert_file.pem . This file must only be
readable by the slurmrestd user.
Note: The certificate's file must be placed in the [autoconf](https://slurm.schedmd.com/autoconf.html)(1)
installation directory variable sysconfdir which can be overridden via setting
TLSParameters = restd_cert_key_file= /path/to/restd_cert_key.pem
in [slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5).
## ENVIRONMENT VARIABLES[#SECTION_ENVIRONMENT-VARIABLES](https://slurm.schedmd.com/slurmrestd.html)
The following environment variables can be used to override settings
compiled into slurmrestd.
ABORT_ON_FATAL [#OPT_ABORT_ON_FATAL](https://slurm.schedmd.com/slurmrestd.html) When a fatal error is detected, use abort() instead of exit() to terminate the
process. This allows backtraces to be captured without recompiling Slurm.
SLURM_CONF [#OPT_SLURM_CONF](https://slurm.schedmd.com/slurmrestd.html) The location of the Slurm configuration file.
SLURM_DEBUG_FLAGS [#OPT_SLURM_DEBUG_FLAGS](https://slurm.schedmd.com/slurmrestd.html) Specify debug flags for slurmrestd to use. See DebugFlags in the
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5) man page for a full list of flags. The environment
variable takes precedence over the setting in the slurm.conf.
SLURM_DEBUG [#OPT_SLURM_DEBUG](https://slurm.schedmd.com/slurmrestd.html) Set debug level explicitly. Valid values are 0-9, or the same string values as
the debug options such as SlurmctldDebug in [slurm.conf](https://slurm.schedmd.com/slurm.conf.html)(5). Increased if
-v passed as argument during invocation. Ignored if
SLURMRESTD_DEBUG or SLURMRESTD_DEBUG_STDERR or
SLURMRESTD_DEBUG_SYSLOG are set in environment. See
SLURMRESTD_DEBUG for description of logging targets.
SLURMRESTD_JSON or SLURM_JSON [#OPT_SLURMRESTD_JSON](https://slurm.schedmd.com/slurmrestd.html) Control JSON serialization:
compact [#OPT_compact](https://slurm.schedmd.com/slurmrestd.html) Output JSON as compact as possible.
pretty [#OPT_pretty](https://slurm.schedmd.com/slurmrestd.html) Output JSON in pretty format to make it more readable.
SLURM_JWT [#OPT_SLURM_JWT](https://slurm.schedmd.com/slurmrestd.html) This variable must be set to use JWT token authentication.
SLURMRESTD_AUTH_TYPES [#OPT_SLURMRESTD_AUTH_TYPES](https://slurm.schedmd.com/slurmrestd.html) Set allowed authentication types. See -a
SLURMRESTD_DEBUG [#OPT_SLURMRESTD_DEBUG](https://slurm.schedmd.com/slurmrestd.html) Set debug level explicitly. Valid values are 0-9, or the same string values as
the debug options such as SlurmctldDebug in [slurm.conf](https://slurm.schedmd.com/slurm.conf.html)(5). If a controlling
TTY is detected, interactive mode will automatically activate to provide
additional logging information to stderr. If a controlling TTY is not detected,
then logs are sent to syslog. Increased if -v passed as argument during
invocation. Ignored if SLURMRESTD_DEBUG_STDERR or
SLURMRESTD_DEBUG_SYSLOG are set in environment.
SLURMRESTD_DEBUG_STDERR [#OPT_SLURMRESTD_DEBUG_STDERR](https://slurm.schedmd.com/slurmrestd.html) Set debug level explicitly for logging to STDERR. Valid values are 0-9, or the
same string values as the debug options such as SlurmctldDebug in
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html)(5). Increased if -v passed as argument during invocation.
SLURMRESTD_DEBUG_SYSLOG [#OPT_SLURMRESTD_DEBUG_SYSLOG](https://slurm.schedmd.com/slurmrestd.html) Set debug level explicitly for logging to syslog. Valid values are 0-9, or the
same string values as the debug options such as SlurmctldDebug in
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html)(5). Increased if -v passed as argument during invocation.
SLURMRESTD_DATA_PARSER_PLUGINS [#OPT_SLURMRESTD_DATA_PARSER_PLUGINS](https://slurm.schedmd.com/slurmrestd.html) Comma-delimited list of data_parser plugins to load. See -d
SLURMRESTD_LISTEN [#OPT_SLURMRESTD_LISTEN](https://slurm.schedmd.com/slurmrestd.html) Comma-delimited list of host:port pairs or unix sockets to listen on.
SLURMRESTD_MAX_CONNECTIONS [#OPT_SLURMRESTD_MAX_CONNECTIONS](https://slurm.schedmd.com/slurmrestd.html) Set the maximum number of connections to process at any one time. See
--max-connections
SLURMRESTD_OPENAPI_PLUGINS [#OPT_SLURMRESTD_OPENAPI_PLUGINS](https://slurm.schedmd.com/slurmrestd.html) Comma-delimited list of OpenAPI plugins to load. See -s
SLURMRESTD_RESPONSE_STATUS_CODES [#OPT_SLURMRESTD_RESPONSE_STATUS_CODES](https://slurm.schedmd.com/slurmrestd.html) Comma-delimited list of OpenAPI method responses to generate in OpenAPI
specification.
Default: 200,default
SLURMRESTD_SECURITY [#OPT_SLURMRESTD_SECURITY](https://slurm.schedmd.com/slurmrestd.html) Control slurmrestd security functionality using the following comma-delimited
values:
become_user [#OPT_become_user](https://slurm.schedmd.com/slurmrestd.html) Allows slurmrestd to be run as root in order to become the requesting
user for all requests. When combined with rest_auth/local, when a user
connects via a named UNIX socket, slurmrestd will setuid()/setgid() into
that user/group and then complete all requests as the given user. This mode is
only intended for inet mode as the user change is permanent for the life of the
process. This mode is incompatible with rest_auth/jwt and it is suggested
to start slurmrestd with "-a rest_auth/local " arguments.
disable_unshare_files [#OPT_disable_unshare_files](https://slurm.schedmd.com/slurmrestd.html) Disables unsharing file descriptors with parent process.
disable_unshare_sysv [#OPT_disable_unshare_sysv](https://slurm.schedmd.com/slurmrestd.html) Disables unsharing the SYSV namespace.
disable_user_check [#OPT_disable_user_check](https://slurm.schedmd.com/slurmrestd.html) Disables check that slurmrestd is not running as root or SlurmUser, or with the
root or SlurmUser's primary group. Disabling this check will allow slurmrestd
to run as root or SlurmUser which will allow anyone who can communicate with
this daemon to run anything as the root user on the cluster.
SLURMRESTD_YAML or SLURM_YAML [#OPT_SLURMRESTD_YAML](https://slurm.schedmd.com/slurmrestd.html) Control YAML serialization:
compact [#OPT_compact_1](https://slurm.schedmd.com/slurmrestd.html) Output YAML as compact as possible.
no_tag [#OPT_no_tag](https://slurm.schedmd.com/slurmrestd.html) Output YAML without datatype !!tags.
pretty [#OPT_pretty_1](https://slurm.schedmd.com/slurmrestd.html) Output YAML in pretty format to make it more readable.
## SIGNALS[#SECTION_SIGNALS](https://slurm.schedmd.com/slurmrestd.html)
SIGINT [#OPT_SIGINT](https://slurm.schedmd.com/slurmrestd.html) slurmrestd will shutdown cleanly.
SIGPIPE [#OPT_SIGPIPE](https://slurm.schedmd.com/slurmrestd.html) This signal is explicitly ignored.
SIGPROF [#OPT_SIGPROF](https://slurm.schedmd.com/slurmrestd.html) Logs connection manager state when debug level is at least info.
## NOTES[#SECTION_NOTES](https://slurm.schedmd.com/slurmrestd.html)
SPANK and clifilter plugins are not supported in slurmrestd
due to their lack of thread safety. Active SPANK plugins and
JobSubmitPlugins in slurmctld are independent of slurmrestd and can
be used to enforce site policy on job submissions.
## EXAMPLES[#SECTION_EXAMPLES](https://slurm.schedmd.com/slurmrestd.html)
Generate OpenAPI schema without configuration
```text
$ slurmrestd -f /dev/null --generate-openapi-spec -s slurmdbd,slurmctld -d v0.0.42 > openapi.json
```
Start slurmrestd with a UNIX socket in listen mode:
```text
$ export SLURMRESTD=/var/spool/slurm/restd/rest $ slurmrestd -s slurmctld,slurmdbd -d v0.0.42 unix:$SLURMRESTD
```
Verify connectivity with slurmctld with a ping, with slurmrestd
running in listen mode:
```text
$ export $(scontrol token) $ curl --unix-socket "${SLURMRESTD}" -H "X-SLURM-USER-TOKEN:${SLURM_JWT}" '[http://ignored_with_unix_sockets/slurm/v0.0.42/ping'](http://ignored_with_unix_sockets/slurm/v0.0.42/ping') | jq '.pings' [ { "hostname": "omicronpersei8", "pinged": "UP", "latency": 314, "mode": "primary" } ]
```
Verify connectivity with slurmdbd with a diag request, with slurmrestd
running in listen mode:
```text
$ export $(scontrol token) $ curl --unix-socket "${SLURMRESTD}" -H "X-SLURM-USER-TOKEN:${SLURM_JWT}" '[http://ignored_with_unix_sockets/slurmdb/v0.0.42/diag'](http://ignored_with_unix_sockets/slurmdb/v0.0.42/diag') | jq '.pings' 1722009793
```
Query the status of a node with slurmrestd running in INETD mode:
```text
$ echo -e "GET [http://ignored/slurm/v0.0.42/node/host1](http://ignored/slurm/v0.0.42/node/host1) HTTP/1.1\r\n" | slurmrestd HTTP/1.1 200 OK Content-Length: 3174 Content-Type: application/json { "nodes": [ { "architecture": "x86_64", "burstbuffer_network_address": "", "boards": 1, "boot_time": { "set": true, "infinite": false, "number": 1720820315 }, "cluster_name": "", "cores": 16, "specialized_cores": 0, "cpu_binding": 0, "cpu_load": 446, "free_mem": { "set": true, "infinite": false, "number": 39871 }, "cpus": 32, "effective_cpus": 32, "specialized_cpus": "", "energy": { "average_watts": 0, "base_consumed_energy": 0, "consumed_energy": 0, "current_watts": { "set": false, "infinite": false, "number": 0 }, "previous_consumed_energy": 0, "last_collected": 0 }, "external_sensors": {}, "extra": "", "power": {}, "features": [], "active_features": [], "gpu_spec": "", "gres": "gpu:fake1:1(S:0),gpu:fake2:1(S:0)", "gres_drained": "N/A", "gres_used": "gpu:fake1:0(IDX:N/A),gpu:fake2:0(IDX:N/A)", "instance_id": "", "instance_type": "", "last_busy": { "set": true, "infinite": false, "number": 1722009794 }, "mcs_label": "", "specialized_memory": 0, "name": "host1", "next_state_after_reboot": [ "INVALID" ], "address": "localhost", "hostname": "omicronpersei8", "state": [ "IDLE" ], "operating_system": "Linux 6.5.0-44-generic #44-Ubuntu SMP PREEMPT_DYNAMIC Fri Jun 7 15:10:09 UTC 2024", "owner": "", "partitions": [ "debug" ], "port": 5015, "real_memory": 127927, "res_cores_per_gpu": 0, "comment": "", "reason": "", "reason_changed_at": { "set": true, "infinite": false, "number": 0 }, "reason_set_by_user": "", "resume_after": { "set": true, "infinite": false, "number": 0 }, "reservation": "", "alloc_memory": 0, "alloc_cpus": 0, "alloc_idle_cpus": 32, "tres_used": "", "tres_weighted": 0.0, "slurmd_start_time": { "set": true, "infinite": false, "number": 1722009794 }, "sockets": 1, "threads": 2, "temporary_disk": 0, "weight": 1, "tres": "cpu=32,mem=127927M,billing=32,gres/gpu=2", "version": "24.11.0-0rc1" } ], "last_update": { "set": true, "infinite": false, "number": 1722010273 }, "meta": { >> }, "errors": [], "warnings": [] }
```
Submit a job to slurmrestd with it running in listen mode:
```text
$ jq . example_job.json { "job": { "script": "#!/bin/bash\nsleep 30", "name": "ExampleJob", "account": "sub1", "environment": [ "PATH=/usr/bin/:/bin/" ], "current_working_directory": "/tmp/", "tasks": 12, "memory_per_cpu": 100, "time_limit": 240 } } $ curl -H "Content-Type: application/json" --data-binary @example_job.json --unix-socket "${SLURMRESTD}" '[http://ignored/slurm/v0.0.42/job/submit'](http://ignored/slurm/v0.0.42/job/submit') { "job_id": 9, "step_id": "batch", "job_submit_user_msg": "", "meta": { >> }, "errors": [], "warnings": [] } $ curl -H "Content-Type: application/json" --data-binary @example_job.json --unix-socket "${SLURMRESTD}" '[http://ignored/slurm/v0.0.42/job/submit'](http://ignored/slurm/v0.0.42/job/submit') { "job_id": 7, "step_id": "batch", "job_submit_user_msg": "", "meta": { }, "errors": [], "warnings": [ { "description": "Expected OpenAPI type=array (Slurm type=list) but got OpenAPI type=object (Slurm type=dictionary): { "source": "#/job/environment/" } ] }
```
## COPYING[#SECTION_COPYING](https://slurm.schedmd.com/slurmrestd.html)
Copyright (C) 2019-2022 SchedMD LLC.
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
## SEE ALSO[#SECTION_SEE-ALSO](https://slurm.schedmd.com/slurmrestd.html)
[slurm.conf](https://slurm.schedmd.com/slurm.conf.html) (5), [slurmctld](https://slurm.schedmd.com/slurmctld.html) (8), [slurmdbd](https://slurm.schedmd.com/slurmdbd.html) (8)
## Index
[NAME](https://slurm.schedmd.com/slurmrestd.html)
[SYNOPSIS](https://slurm.schedmd.com/slurmrestd.html)
[DESCRIPTION](https://slurm.schedmd.com/slurmrestd.html)
[OPTIONS](https://slurm.schedmd.com/slurmrestd.html)
[TLS](https://slurm.schedmd.com/slurmrestd.html)
[ENVIRONMENT VARIABLES](https://slurm.schedmd.com/slurmrestd.html)
[SIGNALS](https://slurm.schedmd.com/slurmrestd.html)
[NOTES](https://slurm.schedmd.com/slurmrestd.html)
[EXAMPLES](https://slurm.schedmd.com/slurmrestd.html)
[COPYING](https://slurm.schedmd.com/slurmrestd.html)
[SEE ALSO](https://slurm.schedmd.com/slurmrestd.html)
This document was created by
man2html using the manual pages.
Time: 21:00:33 GMT, April 14, 2026
