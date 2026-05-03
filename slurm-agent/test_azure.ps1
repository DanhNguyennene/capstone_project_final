[CmdletBinding()]
param([string] $Python = "")

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = $PSScriptRoot

function Write-Step { param([string] $Message) Write-Host "[azure-test] $Message" -ForegroundColor Cyan }
function Write-Ok { param([string] $Message) Write-Host "[azure-test] $Message" -ForegroundColor Green }
function Write-Warn { param([string] $Message) Write-Host "[azure-test] $Message" -ForegroundColor Yellow }

function Load-EnvFile {
    param([Parameter(Mandatory = $true)][string] $Path)
    if (-not (Test-Path -LiteralPath $Path)) { return }

    foreach ($rawLine in Get-Content -LiteralPath $Path) {
        $line = $rawLine.Trim()
        if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith("#")) { continue }
        if ($line.StartsWith("export ")) { $line = $line.Substring(7).Trim() }
        $equalsIndex = $line.IndexOf("=")
        if ($equalsIndex -lt 1) { continue }

        $key = $line.Substring(0, $equalsIndex).Trim()
        $value = $line.Substring($equalsIndex + 1).Trim()
        if ($value.Length -ge 2) {
            $first = $value.Substring(0, 1)
            $last = $value.Substring($value.Length - 1, 1)
            if (($first -eq '"' -and $last -eq '"') -or ($first -eq "'" -and $last -eq "'")) {
                $value = $value.Substring(1, $value.Length - 2)
            }
        }
        if ($key -match '^[A-Za-z_][A-Za-z0-9_]*$') {
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
    Write-Ok "Loaded env: $Path"
}

function Resolve-Tool {
    param([Parameter(Mandatory = $true)][string[]] $Names)
    foreach ($name in $Names) {
        if ($name -and (Test-Path -LiteralPath $name)) { return (Resolve-Path -LiteralPath $name).Path }
        if ($name) {
            $command = Get-Command $name -ErrorAction SilentlyContinue
            if ($command) { return $command.Source }
        }
    }
    throw "Tool not found: $($Names -join ', ')"
}

function Resolve-PythonExe {
    if ($Python) { return Resolve-Tool @($Python) }
    if ($env:PYTHON) { return Resolve-Tool @($env:PYTHON) }

    $candidates = @()
    if ($env:VIRTUAL_ENV) { $candidates += (Join-Path $env:VIRTUAL_ENV "Scripts\python.exe") }
    $candidates += (Join-Path (Split-Path -Parent $Root) ".venv\Scripts\python.exe")
    $candidates += (Join-Path $Root ".venv\Scripts\python.exe")
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) { return (Resolve-Path -LiteralPath $candidate).Path }
    }
    return Resolve-Tool @("python.exe", "python")
}

foreach ($envFile in @(
    (Join-Path $Root ".key"),
    (Join-Path (Split-Path -Parent $Root) ".key"),
    (Join-Path $Root ".env"),
    (Join-Path (Split-Path -Parent $Root) ".env")
)) {
    Load-EnvFile -Path $envFile
}

$PythonExe = Resolve-PythonExe
Write-Step "Using Python: $PythonExe"

$script = @'
import os
import ipaddress
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request

os.environ['NO_PROXY'] = '.cognitiveservices.azure.com,.openai.azure.com,10.0.0.0/8'
os.environ['no_proxy'] = os.environ['NO_PROXY']

endpoint = (os.getenv("AZURE_OPENAI_ENDPOINT") or "").rstrip("/")
api_key = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_KEY") or ""
api_version = os.getenv("AZURE_OPENAI_API_VERSION") or os.getenv("API_VERSION") or "2024-02-15-preview"
model = os.getenv("AZURE_OPENAI_MODEL") or os.getenv("AZURE_OPENAI_DEPLOYMENT") or ""
https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy") or ""
http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy") or ""
no_proxy = os.getenv("NO_PROXY") or os.getenv("no_proxy") or ""

def mask(value):
    return "set" if value else "missing"

def host_port(url, default_port):
    parsed = urllib.parse.urlparse(url)
    return parsed.hostname, parsed.port or default_port

def no_proxy_matches(hostname, no_proxy_value):
    host = (hostname or "").strip().strip("[]").lower()
    for raw_token in no_proxy_value.split(","):
        token = raw_token.strip().lower()
        if not token:
            continue
        if token == "*":
            return True
        if "/" in token:
            try:
                if ipaddress.ip_address(host) in ipaddress.ip_network(token, strict=False):
                    return True
            except ValueError:
                pass
        token_host = token[1:] if token.startswith(".") else token
        if host == token_host or host.endswith(f".{token_host}"):
            return True
    return False

print(f"AZURE_OPENAI_ENDPOINT: {mask(endpoint)}")
print(f"AZURE_OPENAI_API_KEY: {mask(api_key)}")
print(f"AZURE_OPENAI_API_VERSION: {api_version}")
print(f"AZURE_OPENAI_MODEL: {model or 'missing'}")
print(f"HTTPS_PROXY: {mask(https_proxy)}")
print(f"HTTP_PROXY: {mask(http_proxy)}")
print(f"NO_PROXY: {no_proxy or 'missing'}")
if ",," in no_proxy:
    print("NO_PROXY warning: duplicate commas found; clean this env value to avoid inconsistent proxy bypass parsing.")

if not endpoint or not api_key or not model:
    print("RESULT: missing Azure config. Set endpoint, key, and model/deployment.")
    sys.exit(2)

endpoint_host, endpoint_port = host_port(endpoint, 443)
print(f"Endpoint host: {endpoint_host}")
endpoint_dns_ok = False
try:
    endpoint_ips = socket.getaddrinfo(endpoint_host, endpoint_port, type=socket.SOCK_STREAM)
    print("Endpoint DNS: ok")
    endpoint_dns_ok = True
except OSError as exc:
    print(f"Endpoint DNS: failed: {exc}")

proxy = https_proxy or http_proxy
proxy_bypassed = no_proxy_matches(endpoint_host, no_proxy)
if proxy_bypassed:
    print("Proxy bypass: endpoint matches NO_PROXY; Azure test will use direct network path.")
    if not endpoint_dns_ok:
        print("Proxy bypass warning: direct Azure route cannot work until this host resolves on your machine.")
if proxy:
    proxy_host, proxy_port = host_port(proxy, 8080)
    print(f"Proxy host: {proxy_host}:{proxy_port}")
    try:
        socket.getaddrinfo(proxy_host, proxy_port, type=socket.SOCK_STREAM)
        print("Proxy DNS: ok")
    except OSError as exc:
        print(f"Proxy DNS: failed: {exc}")

url = f"{endpoint}/openai/deployments?api-version={urllib.parse.quote(api_version)}"

try:
    import ssl
    import httpx
    import truststore

    ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    mounts = {}
    if http_proxy and not proxy_bypassed:
        mounts["http://"] = httpx.HTTPTransport(proxy=http_proxy, verify=ssl_context)
    if (https_proxy or http_proxy) and not proxy_bypassed:
        mounts["https://"] = httpx.HTTPTransport(proxy=https_proxy or http_proxy, verify=ssl_context)
    client_kwargs = {"verify": ssl_context, "timeout": 20}
    if mounts:
        client_kwargs = {"mounts": mounts, "timeout": 20, "trust_env": False}
    label = "direct/system cert" if proxy_bypassed else ("explicit proxy" if mounts else "system cert")
    with httpx.Client(**client_kwargs) as client:
        response = client.get(url, headers={"api-key": api_key})
    print(f"HTTPX {label} test: network path returned HTTP {response.status_code}")
    if response.status_code in (502, 503, 504):
        body = response.text[:4096]
        if "DNS look up failed" in body or "DNS lookup failed" in body:
            print("HTTPX test: corporate proxy reported DNS lookup failure for the Azure host.")
        print("HTTPX test: proxy/upstream gateway timeout; check corporate proxy/VPN/Azure private DNS route.")
except ImportError as exc:
    print(f"HTTPX test: skipped, missing package: {exc.name}")
except Exception as exc:
    label = "direct/system cert" if proxy_bypassed else "explicit proxy"
    print(f"HTTPX {label} test: failed: {type(exc).__name__}: {exc}")

request = urllib.request.Request(url, headers={"api-key": api_key})
try:
    with urllib.request.urlopen(request, timeout=20) as response:
        print(f"Azure API: ok, HTTP {response.status}")
        sys.exit(0)
except urllib.error.HTTPError as exc:
    print(f"Azure API: network path returned HTTP {exc.code}")
    if exc.code in (502, 503, 504):
        body = exc.read(4096).decode("utf-8", errors="ignore")
        if "DNS look up failed" in body or "DNS lookup failed" in body:
            print("RESULT: corporate proxy reported DNS lookup failure for the Azure host.")
        print("RESULT: proxy/upstream gateway timeout. Python, TLS, and proxy mounting work; the proxy/Azure route is blocked or misconfigured.")
        sys.exit(3)
    print("RESULT: network path works; check key/API version/deployment if chat still fails.")
    sys.exit(0 if exc.code in (200, 401, 403, 404) else 3)
except Exception as exc:
    print(f"Azure API: connection failed: {type(exc).__name__}: {exc}")
    if proxy_bypassed and not endpoint_dns_ok:
        print("RESULT: NO_PROXY is active, but direct DNS failed. Connect to the private DNS/VPN route or remove Azure from NO_PROXY to use the proxy path.")
        sys.exit(1)
    print("RESULT: network/proxy/DNS is blocking the Azure call from Python.")
    sys.exit(1)
'@

$temp = New-TemporaryFile
try {
    Set-Content -LiteralPath $temp -Value $script -Encoding UTF8
    & $PythonExe $temp
    exit $LASTEXITCODE
}
finally {
    Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
}
