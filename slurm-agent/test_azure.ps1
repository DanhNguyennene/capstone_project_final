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
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request

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

print(f"AZURE_OPENAI_ENDPOINT: {mask(endpoint)}")
print(f"AZURE_OPENAI_API_KEY: {mask(api_key)}")
print(f"AZURE_OPENAI_API_VERSION: {api_version}")
print(f"AZURE_OPENAI_MODEL: {model or 'missing'}")
print(f"HTTPS_PROXY: {mask(https_proxy)}")
print(f"HTTP_PROXY: {mask(http_proxy)}")
print(f"NO_PROXY: {no_proxy or 'missing'}")

if not endpoint or not api_key or not model:
    print("RESULT: missing Azure config. Set endpoint, key, and model/deployment.")
    sys.exit(2)

endpoint_host, endpoint_port = host_port(endpoint, 443)
print(f"Endpoint host: {endpoint_host}")
try:
    endpoint_ips = socket.getaddrinfo(endpoint_host, endpoint_port, type=socket.SOCK_STREAM)
    print("Endpoint DNS: ok")
except OSError as exc:
    print(f"Endpoint DNS: failed: {exc}")

proxy = https_proxy or http_proxy
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
    with httpx.Client(verify=ssl_context, timeout=20, trust_env=True) as client:
        response = client.get(url, headers={"api-key": api_key})
    print(f"HTTPX system cert test: reached endpoint, HTTP {response.status_code}")
except ImportError as exc:
    print(f"HTTPX system cert test: skipped, missing package: {exc.name}")
except Exception as exc:
    print(f"HTTPX system cert test: failed: {type(exc).__name__}: {exc}")

request = urllib.request.Request(url, headers={"api-key": api_key})
try:
    with urllib.request.urlopen(request, timeout=20) as response:
        print(f"Azure API: ok, HTTP {response.status}")
        sys.exit(0)
except urllib.error.HTTPError as exc:
    print(f"Azure API: reached endpoint, HTTP {exc.code}")
    print("RESULT: network path works; check key/API version/deployment if chat still fails.")
    sys.exit(0 if exc.code in (200, 401, 403, 404) else 3)
except Exception as exc:
    print(f"Azure API: connection failed: {type(exc).__name__}: {exc}")
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
