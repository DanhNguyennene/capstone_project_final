[CmdletBinding()]
param(
    [switch] $Stop,
    [switch] $Status,
    [switch] $Real,
    [switch] $SkipInstall,
    [string] $Scenario = "",
    [int] $McpPort = 0,
    [int] $AgentPort = 0,
    [int] $FrontendPort = 0,
    [int] $EvalPort = 0,
    [string] $Python = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = $PSScriptRoot
$LogDir = Join-Path $Root "logs"
$PidFile = Join-Path $LogDir "windows-stack-pids.json"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Step {
    param([Parameter(Mandatory = $true)][string] $Message)
    Write-Host "[windows-start] $Message" -ForegroundColor Cyan
}

function Write-Ok {
    param([Parameter(Mandatory = $true)][string] $Message)
    Write-Host "[windows-start] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([Parameter(Mandatory = $true)][string] $Message)
    Write-Host "[windows-start] $Message" -ForegroundColor Yellow
}

function Quote-PS {
    param([AllowNull()][string] $Value)
    if ($null -eq $Value) { return "''" }
    return "'" + $Value.Replace("'", "''") + "'"
}

function Load-EnvFile {
    param([Parameter(Mandatory = $true)][string] $Path)
    if (-not (Test-Path -LiteralPath $Path)) { return }

    foreach ($rawLine in Get-Content -LiteralPath $Path) {
        $line = $rawLine.Trim()
        if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith("#")) { continue }
        if ($line.StartsWith("export ")) { $line = $line.Substring(7).Trim() }

        $equalsIndex = $line.IndexOf("=")
        if ($equalsIndex -ge 1) {
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
                if ($key -eq "OPEN_AI_KEY") {
                    [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $value, "Process")
                }
            }
            continue
        }

        if ($line.StartsWith("sk-")) {
            [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $line, "Process")
        }
        elseif ($line.StartsWith("ghp_") -or $line.StartsWith("github_pat_") -or $line.StartsWith("gho_") -or $line.StartsWith("ghu_") -or $line.StartsWith("ghs_")) {
            [Environment]::SetEnvironmentVariable("GITHUB_TOKEN", $line, "Process")
        }
    }

    Write-Ok "Loaded env: $Path"
}

function Resolve-Tool {
    param([Parameter(Mandatory = $true)][string[]] $Names)

    foreach ($name in $Names) {
        if (Test-Path -LiteralPath $name) { return (Resolve-Path -LiteralPath $name).Path }
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) { return $command.Source }
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

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)][string] $FilePath,
        [string[]] $Arguments = @(),
        [string] $WorkingDirectory = $Root
    )

    Push-Location $WorkingDirectory
    try {
        & $FilePath @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
        }
    }
    finally {
        Pop-Location
    }
}

function Get-StackState {
    if (-not (Test-Path -LiteralPath $PidFile)) { return $null }
    try {
        return (Get-Content -LiteralPath $PidFile -Raw | ConvertFrom-Json)
    }
    catch {
        return $null
    }
}

function Stop-PortOwner {
    param([Parameter(Mandatory = $true)][int] $Port)

    try {
        $connections = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
        foreach ($connection in $connections) {
            if ($connection.OwningProcess -and $connection.OwningProcess -ne $PID) {
                Stop-Process -Id ([int] $connection.OwningProcess) -Force -ErrorAction SilentlyContinue
            }
        }
    }
    catch {
        # Get-NetTCPConnection is Windows-only; ignore if unavailable.
    }
}

function Stop-Stack {
    param([int[]] $Ports)

    $state = Get-StackState
    if ($state -and ($state.PSObject.Properties.Name -contains "processes")) {
        $records = @($state.processes)
        [array]::Reverse($records)
        foreach ($record in $records) {
            $process = Get-Process -Id ([int] $record.Id) -ErrorAction SilentlyContinue
            if ($process) {
                Write-Step "Stopping $($record.Name) window (pid=$($record.Id))"
                Stop-Process -Id ([int] $record.Id) -Force -ErrorAction SilentlyContinue
            }
        }
    }

    foreach ($port in $Ports) {
        Stop-PortOwner -Port $port
    }

    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
    Write-Ok "Stopped Windows stack."
}

function Show-Status {
    param([int[]] $Ports)

    $state = Get-StackState
    if ($state -and ($state.PSObject.Properties.Name -contains "processes")) {
        foreach ($record in @($state.processes)) {
            $process = Get-Process -Id ([int] $record.Id) -ErrorAction SilentlyContinue
            if ($process) { Write-Ok "$($record.Name) window running (pid=$($record.Id))" }
            else { Write-Warn "$($record.Name) window is not running (pid=$($record.Id))" }
        }
    }
    else {
        Write-Warn "No Windows stack PID file found."
    }

    foreach ($port in $Ports) {
        try {
            $listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($listener) { Write-Ok "Port $port is listening (pid=$($listener.OwningProcess))" }
            else { Write-Warn "Port $port is not listening" }
        }
        catch {
            Write-Warn "Could not inspect port $port"
        }
    }
}

function Test-TcpPort {
    param([Parameter(Mandatory = $true)][int] $Port)

    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $async = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        if (-not $async.AsyncWaitHandle.WaitOne(500)) { return $false }
        $client.EndConnect($async)
        return $true
    }
    catch {
        return $false
    }
    finally {
        $client.Close()
    }
}

function Wait-TcpPort {
    param(
        [Parameter(Mandatory = $true)][string] $Name,
        [Parameter(Mandatory = $true)][int] $Port,
        [int] $TimeoutSeconds = 30
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-TcpPort -Port $Port) {
            Write-Ok "$Name is listening on port $Port"
            return $true
        }
        Start-Sleep -Milliseconds 500
    }
    Write-Warn "$Name did not answer on port $Port yet. Check its window."
    return $false
}

function Wait-HttpUrl {
    param(
        [Parameter(Mandatory = $true)][string] $Name,
        [Parameter(Mandatory = $true)][string] $Url,
        [int] $TimeoutSeconds = 45
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                Write-Ok "$Name is ready: $Url"
                return $true
            }
        }
        catch {
        }
        Start-Sleep -Milliseconds 500
    }
    Write-Warn "$Name did not answer yet: $Url. Check its window."
    return $false
}

function Start-ServiceWindow {
    param(
        [Parameter(Mandatory = $true)][string] $Name,
        [Parameter(Mandatory = $true)][string] $Title,
        [Parameter(Mandatory = $true)][string] $WorkingDirectory,
        [Parameter(Mandatory = $true)][string] $FilePath,
        [string[]] $Arguments = @()
    )

    $argumentText = ($Arguments | ForEach-Object { Quote-PS $_ }) -join " "
    $script = @"
`$ErrorActionPreference = 'Stop'
`$Host.UI.RawUI.WindowTitle = $(Quote-PS $Title)
Set-Location -LiteralPath $(Quote-PS $WorkingDirectory)
Write-Host $(Quote-PS "Starting $Name") -ForegroundColor Green
Write-Host $(Quote-PS "$FilePath $($Arguments -join ' ')") -ForegroundColor DarkGray
& $(Quote-PS $FilePath) $argumentText
if (`$LASTEXITCODE -ne 0) { Write-Host (($(Quote-PS "$Name exited with code ")) + `$LASTEXITCODE) -ForegroundColor Red }
Write-Host ''
Write-Host $(Quote-PS "$Name stopped. You can close this window.") -ForegroundColor Yellow
"@

    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($script))
    $startArgs = @("-NoExit", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $encoded)
    $process = Start-Process -FilePath $PowerShellExe -ArgumentList $startArgs -WorkingDirectory $WorkingDirectory -WindowStyle Normal -PassThru
    return [pscustomobject]@{
        Name = $Name
        Id = $process.Id
        WorkingDirectory = $WorkingDirectory
        Command = "$FilePath $($Arguments -join ' ')"
    }
}

foreach ($envFile in @(
    (Join-Path $Root ".key"),
    (Join-Path (Split-Path -Parent $Root) ".key"),
    (Join-Path $Root ".env"),
    (Join-Path (Split-Path -Parent $Root) ".env")
)) {
    Load-EnvFile -Path $envFile
}

if ($McpPort -le 0) { $McpPort = if ($env:MCP_PORT) { [int] $env:MCP_PORT } else { 3002 } }
if ($AgentPort -le 0) { $AgentPort = if ($env:AGENT_PORT) { [int] $env:AGENT_PORT } else { 8000 } }
if ($FrontendPort -le 0) { $FrontendPort = if ($env:FRONTEND_PORT) { [int] $env:FRONTEND_PORT } else { 4173 } }
if ($EvalPort -le 0) { $EvalPort = if ($env:EVAL_PORT) { [int] $env:EVAL_PORT } else { 8080 } }
if (-not $Scenario) { $Scenario = if ($env:MCP_SCENARIO) { $env:MCP_SCENARIO } else { "healthy" } }

$ports = @($McpPort, $AgentPort, $FrontendPort, $EvalPort)

if ($Stop) {
    Stop-Stack -Ports $ports
    return
}

if ($Status) {
    Show-Status -Ports $ports
    return
}

$PythonExe = Resolve-PythonExe
$pythonScriptsDir = Split-Path -Parent $PythonExe
if ((Split-Path -Leaf $pythonScriptsDir) -ieq "Scripts") {
    $env:VIRTUAL_ENV = Split-Path -Parent $pythonScriptsDir
    $env:PATH = "$pythonScriptsDir;$env:PATH"
}

$NpmExe = Resolve-Tool @("npm.cmd", "npm")
$PowerShellExe = Resolve-Tool @("powershell.exe", "powershell", "pwsh")
$FrontendDir = Join-Path $Root "frontend"
$Requirements = Join-Path $Root "requirements.txt"

Write-Step "Using Python: $PythonExe"
Write-Step "Using npm: $NpmExe"

if (-not $SkipInstall) {
    & $PythonExe -c "import agents, fastapi, uvicorn, httpx" *> $null
    if ($LASTEXITCODE -ne 0) {
        if (-not (Test-Path -LiteralPath $Requirements)) {
            throw "Missing requirements file: $Requirements"
        }

        $uv = Get-Command "uv" -ErrorAction SilentlyContinue
        if ($uv) {
            Write-Step "Installing Python dependencies with uv"
            Invoke-Native -FilePath $uv.Source -Arguments @("pip", "install", "--python", $PythonExe, "-r", $Requirements) -WorkingDirectory $Root
        }
        else {
            Write-Step "Installing Python dependencies with pip"
            Invoke-Native -FilePath $PythonExe -Arguments @("-m", "pip", "install", "-r", $Requirements) -WorkingDirectory $Root
        }
    }
    else {
        Write-Ok "Python dependencies look ready"
    }

    if (-not (Test-Path -LiteralPath (Join-Path $FrontendDir "node_modules"))) {
        Write-Step "Installing frontend dependencies"
        Invoke-Native -FilePath $NpmExe -Arguments @("install") -WorkingDirectory $FrontendDir
    }
    else {
        Write-Ok "Frontend dependencies look ready"
    }
}

Stop-Stack -Ports $ports
$env:MCP_SERVER_URL = "http://127.0.0.1:$McpPort"

$mcpArgs = if ($Real) {
    @("slurm_mcp_sse.py", "--real", "--port", [string] $McpPort)
}
else {
    @("slurm_mcp_sse.py", "--mock", $Scenario, "--port", [string] $McpPort)
}

$records = @()
$records += Start-ServiceWindow -Name "MCP server" -Title "Slurm MCP server" -WorkingDirectory (Join-Path $Root "mcp-server") -FilePath $PythonExe -Arguments $mcpArgs
$records += Start-ServiceWindow -Name "Agent API" -Title "Slurm Agent API" -WorkingDirectory (Join-Path $Root "agent") -FilePath $PythonExe -Arguments @("-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", [string] $AgentPort)
$records += Start-ServiceWindow -Name "Frontend" -Title "Slurm Frontend" -WorkingDirectory $FrontendDir -FilePath $NpmExe -Arguments @("run", "dev", "--", "--host", "0.0.0.0", "--port", [string] $FrontendPort)
$records += Start-ServiceWindow -Name "Eval server" -Title "Slurm Eval server" -WorkingDirectory (Join-Path $Root "evaluation") -FilePath $PythonExe -Arguments @("eval_server.py", "--host", "0.0.0.0", "--port", [string] $EvalPort)

[pscustomobject]@{
    started = (Get-Date).ToString("o")
    ports = [pscustomobject]@{
        mcp = $McpPort
        agent = $AgentPort
        frontend = $FrontendPort
        eval = $EvalPort
    }
    processes = $records
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $PidFile -Encoding UTF8

Write-Step "Waiting for services"
[void](Wait-TcpPort -Name "MCP server" -Port $McpPort -TimeoutSeconds 30)
[void](Wait-HttpUrl -Name "Agent API" -Url "http://127.0.0.1:$AgentPort/health" -TimeoutSeconds 45)
[void](Wait-HttpUrl -Name "Frontend" -Url "http://127.0.0.1:$FrontendPort/" -TimeoutSeconds 45)
[void](Wait-HttpUrl -Name "Eval server" -Url "http://127.0.0.1:$EvalPort/api/status" -TimeoutSeconds 45)

Write-Host ""
Write-Ok "Started all Windows service windows."
Write-Host "  Frontend:   http://127.0.0.1:$FrontendPort/"
Write-Host "  Agent API:  http://127.0.0.1:$AgentPort/health"
Write-Host "  Eval UI:    http://127.0.0.1:$EvalPort/"
Write-Host "  MCP server: http://127.0.0.1:$McpPort/sse"
Write-Host ""
Write-Host "Stop:   .\start_windows.ps1 -Stop"
Write-Host "Status: .\start_windows.ps1 -Status"