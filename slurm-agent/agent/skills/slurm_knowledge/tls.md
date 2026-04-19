---
source_url: https://slurm.schedmd.com/tls.html
source_host: slurm.schedmd.com
fetched_at_utc: 2026-04-19 04:22:36 UTC
title: "Slurm Workload Manager -"
---

# TLS
## Overview[#Overview](https://slurm.schedmd.com/tls.html)
TLS can be enabled for internal Slurm cluster communications in environments
via the `tls` plugin interface.
## s2n[#s2n](https://slurm.schedmd.com/tls.html)
The `tls/s2n` plugin uses Amazon's TLS implementation
[s2n-tls](https://github.com/aws/s2n-tls), which is a C99
implementation of the TLS/SSL protocols that is designed to be simple, small,
fast, and with security as a priority.
### Install[#s2n_install](https://slurm.schedmd.com/tls.html)
Build s2n-tls from their public GitHub repository:
```text
git clone https://github.com/aws/s2n-tls.git cd s2n-tls/ cmake . -B build/ -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON cmake --build build/ -j $(nproc) cmake --install build/
```
Note that the cmake `-DBUILD_SHARED_LIBS=ON` flag
is required in order to build the `libs2n.so`
shared object that is used by Slurm.
Follow s2n-tls build documentation for further guidance on different possible
settings.
### Setup[#s2n_setup](https://slurm.schedmd.com/tls.html)
To enable TLS for internal Slurm cluster communications, configure the
[TLSType](https://slurm.schedmd.com/slurm.conf.html) option in slurm.conf and
slurmdbd.conf to use the `tls/s2n` plugin.
All Slurm components are required to have access to a common CA certificate.
slurmctld, slurmdbd, and slurmrestd are required to have their own unique
certificate/key pair. These certificates must chain to the specified CA
certificate. Note that these certificate/key pairs only needs to be accessible
by their respective daemons. Only the CA certificate file needs to be
accessible by Slurm components.
slurmd and sackd can also have static predefined certificate/key pairs, or they
can optionally use the `certmgr` plugin interface to dynamically
retrieve and renew their certificate/key pairs. If the `certmgr`
plugin interface is not configured, they are required to have a static
predefined certificate/key pair. See the
[TLS Certificate Management](https://slurm.schedmd.com/certmgr.html) page for more info.
Here's a list of the default certificate/key PEM file names which are expected
to be in Slurm's default etc directory. Different absolute file paths can be
set for each of these files via `TLSParameters`.
- ca_cert.pem
- ctld_cert.pem
- ctld_cert_key.pem
- dbd_cert.pem
- dbd_cert_key.pem
- restd_cert.pem
- restd_cert_key.pem
- sackd_cert.pem
- sackd_cert_key.pem
- slurmd_cert.pem
- slurmd_cert_key.pem
In some cases (e.g. step IO, waiting for step allocation, etc.) some client
commands need to create listening socket servers. In order for other Slurm
components to connect to these listening sockets, they need a TLS certificate
they can trust. Client commands achieve this by ephemerally generating
self-signed certificates via the `certgen` plugin interface and
securely sharing these certificates in pre-established TLS connections.
By default, the `certgen` plugin requires no configuration and will
use the openssl cli to generate a self-signed certificate/key pair. It can
optionally be configured to use different scripts to generate this pair via
[CertgenParameters](https://slurm.schedmd.com/slurm.conf.html).
After configuring the `tls/s2n` plugin and certificates, the
following debug log can be seen in the daemon logs:
```text
debug: tls/s2n: init: tls/s2n loaded
```
Note that when tls/s2n is not configured, this line will always be seen:
```text
debug: tls/none: init: tls/none loaded
```
With [DebugFlags=TLS](https://slurm.schedmd.com/slurm.conf.html) configured, an extremely verbose view of RPC connections can be seen in the logs. For example, here's what appears for a connection between slurmctld and slurmdbd:
```text
slurmctld: tls/s2n: tls_p_create_conn: TLS: tls/s2n: cipher suite:TLS_AES_128_GCM_SHA256, {0x13,0x01}. fd:17. slurmctld: tls/s2n: tls_p_create_conn: TLS: tls/s2n: connection successfully created. fd:17. tls mode:client
```
```text
slurmdbd: tls/s2n: tls_p_create_conn: TLS: tls/s2n: cipher suite:TLS_AES_128_GCM_SHA256, {0x13,0x01}. fd:13. slurmdbd: tls/s2n: tls_p_create_conn: TLS: tls/s2n: connection successfully created. fd:13. tls mode:server
```
### OpenSSL Example[#s2n_openssl_example](https://slurm.schedmd.com/tls.html)
Here are some examples of how to generate the certificate key/pairs needed for
the `tls/s2n` plugin. These examples are not intended to be used in
a production environment.
Generate a self-signed CA certificate key pair:
```text
openssl ecparam -out ca_key.pem -name prime256v1 -genkey chmod 0400 ca_key.pem openssl req -x509 -key ca_key.pem -out ca_cert.pem -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=my_slurm_ca" chmod 0444 ca_cert.pem
```
Generate a signed certificate from CA certificate:
```text
openssl ecparam -out ctld_key.pem -name prime256v1 -genkey chmod 0400 ctld_key.pem # ensure that ownership of key matches user running daemon openssl req -new -key ctld_key.pem -out ctld_csr.pem -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=ctld" openssl x509 -req -in ctld_csr.pem -CA ca_cert.pem -CAkey ca_key.pem -out ctld_cert.pem -sha384 chmod 0444 ctld_cert.pem
```
