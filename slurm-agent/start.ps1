[CmdletBinding()]
param(
    [switch] $Rebuild,
    [switch] $NoRebuild,
    [switch] $Real,
    [switch] $Detached,
    [switch] $Status,
    [switch] $Stop,
    [int] $McpPort = 0,
    [int] $AgentPort = 0,
    [int] $FrontendPort = 0,
    [string] $McpScenario = "",
    [string] $Python = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = $PSScriptRoot
. (Join-Path $Root "ps-common.ps1")

$LogDir = Join-Path $Root "logs"
$PidFile = Join-Path $LogDir "ps-stack-pids.json"

if ($Status) {
    Show-RecordedProcessStatus -PidFile $PidFile
    return
}

if ($Stop) {
    Stop-RecordedProcesses -PidFile $PidFile
    return
}

Load-LocalEnv -Root $Root

if ($McpPort -le 0) { $McpPort = if ($env:MCP_PORT) { [int] $env:MCP_PORT } else { 3002 } }
if ($AgentPort -le 0) { $AgentPort = if ($env:AGENT_PORT) { [int] $env:AGENT_PORT } else { 8000 } }
if ($FrontendPort -le 0) { $FrontendPort = if ($env:FRONTEND_PORT) { [int] $env:FRONTEND_PORT } else { 4173 } }
if (-not $McpScenario) { $McpScenario = if ($env:MCP_SCENARIO) { $env:MCP_SCENARIO } else { "healthy" } }
if (-not $Python) { $Python = if ($env:PYTHON) { $env:PYTHON } else { "python" } }

if ($Detached -and (@(Get-LivePidRecords -PidFile $PidFile)).Count -gt 0) {
    throw "PowerShell stack is already running. Use ./start.ps1 -Status or ./start.ps1 -Stop."
}

$FrontendDir = Join-Path $Root "frontend"
$DistDir = Join-Path $FrontendDir "dist"
$PackageJson = Join-Path $FrontendDir "package.json"

if (-not (Test-Path -LiteralPath $PackageJson)) {
        throw @"
Frontend package manifest not found: $PackageJson
This checkout is missing tracked frontend files. From the repository root, run:
    git restore --source=origin/main -- slurm-agent/frontend
Then retry from slurm-agent:
    .\start.ps1
"@
}

function Test-FrontendNeedsBuild {
    if (-not (Test-Path -LiteralPath $DistDir)) { return $true }
    $distIndex = Join-Path $DistDir "index.html"
    if (-not (Test-Path -LiteralPath $distIndex)) { return $true }

    $distTime = (Get-Item -LiteralPath $distIndex).LastWriteTimeUtc
    $inputs = @()
    $srcDir = Join-Path $FrontendDir "src"
    if (Test-Path -LiteralPath $srcDir) {
        $inputs += Get-ChildItem -LiteralPath $srcDir -Recurse -File -ErrorAction SilentlyContinue
    }
    $indexHtml = Join-Path $FrontendDir "index.html"
    if (Test-Path -LiteralPath $indexHtml) { $inputs += Get-Item -LiteralPath $indexHtml }
    $inputs += Get-ChildItem -LiteralPath $FrontendDir -Filter "vite.config*" -File -ErrorAction SilentlyContinue

    return $null -ne ($inputs | Where-Object { $_.LastWriteTimeUtc -gt $distTime } | Select-Object -First 1)
}

function Get-ViteBinPath {
    $binDir = Join-Path $FrontendDir "node_modules/.bin"
    foreach ($name in @("vite", "vite.cmd", "vite.ps1")) {
        $candidate = Join-Path $binDir $name
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }
    return $null
}

$PythonExe = Resolve-Executable -Name $Python
$NpmExe = Resolve-Executable -Name "npm"

Push-Location $FrontendDir
try {
    $viteBin = Get-ViteBinPath
    if (-not $viteBin) {
        Write-Info "node_modules not found; running npm install"
        Invoke-Checked -FilePath $NpmExe -Arguments @("install") -WorkingDirectory $FrontendDir
        Write-Ok "npm install complete"
    }
    elseif ((Get-Item -LiteralPath $PackageJson).LastWriteTimeUtc -gt (Get-Item -LiteralPath $viteBin).LastWriteTimeUtc) {
        Write-Info "package.json changed; running npm install"
        Invoke-Checked -FilePath $NpmExe -Arguments @("install") -WorkingDirectory $FrontendDir
        Write-Ok "npm install complete"
    }
    else {
        Write-Ok "node_modules up-to-date"
    }
}
finally {
    Pop-Location
}

if (-not $NoRebuild) {
    if ($Rebuild -or (Test-FrontendNeedsBuild)) {
        Write-Info "Building frontend"
        Invoke-Checked -FilePath $NpmExe -Arguments @("run", "build") -WorkingDirectory $FrontendDir
        Write-Ok "Frontend built -> $DistDir"
    }
    else {
        Write-Ok "Frontend up-to-date, skipping build"
    }
}

$requirementsCandidates = @(
    (Join-Path $Root "requirements.txt"),
    (Join-Path $Root "agent/requirements.txt")
)
$requirementsPath = $requirementsCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
$directPackageInstall = @("fastapi==0.116.1", "uvicorn==0.35.0", "pydantic==2.11.7", "python-dotenv==1.1.1", "python-multipart", "openai", "openai-agents", "websockets==14.1", "aiohttp==3.12.14", "matplotlib")
$dependencyCheck = Invoke-NativeCapture -FilePath $PythonExe -Arguments @("-c", "import agents, fastapi, uvicorn, httpx") -WorkingDirectory $Root
if ($dependencyCheck.ExitCode -ne 0) {
    Write-Warn "Python dependencies are missing; installing now."
    if ($requirementsPath) {
        $installArgs = @("-m", "pip", "install", "-r", $requirementsPath)
    }
    else {
        $installArgs = @("-m", "pip", "install") + $directPackageInstall
    }

    $installResult = Invoke-NativeCapture -FilePath $PythonExe -Arguments $installArgs -WorkingDirectory $Root
    if ($installResult.ExitCode -ne 0) {
        $detail = $installResult.Output
        $installCommand = "$PythonExe $($installArgs -join ' ')"
        throw @"
Missing Python dependencies for the agent API.
Automatic install failed. Run this manually:
    $installCommand

Original error:
$detail
"@
    }

    $dependencyCheck = Invoke-NativeCapture -FilePath $PythonExe -Arguments @("-c", "import agents, fastapi, uvicorn, httpx") -WorkingDirectory $Root
    if ($dependencyCheck.ExitCode -ne 0) {
        throw @"
Python dependency install completed, but imports still fail.
Original error:
$($dependencyCheck.Output)
"@
    }

    Write-Ok "Python dependencies installed."
}

$records = @()
$previousMcpServerUrl = $env:MCP_SERVER_URL
$env:MCP_SERVER_URL = "http://localhost:$McpPort"

try {
    $mcpArgs = if ($Real) {
        @("slurm_mcp_sse.py", "--real", "--port", [string] $McpPort)
    }
    else {
        @("slurm_mcp_sse.py", "--mock", $McpScenario, "--port", [string] $McpPort)
    }

    $records += Start-ManagedProcess `
        -Name "mcp-server" `
        -FilePath $PythonExe `
        -Arguments $mcpArgs `
        -WorkingDirectory (Join-Path $Root "mcp-server") `
        -LogDir $LogDir `
        -Detached:$Detached

    $records += Start-ManagedProcess `
        -Name "agent-api" `
        -FilePath $PythonExe `
        -Arguments @("-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", [string] $AgentPort, "--reload") `
        -WorkingDirectory (Join-Path $Root "agent") `
        -LogDir $LogDir `
        -Detached:$Detached

    if (Test-Path -LiteralPath $DistDir) {
        $records += Start-ManagedProcess `
            -Name "frontend" `
            -FilePath $NpmExe `
            -Arguments @("run", "preview", "--", "--host", "0.0.0.0", "--port", [string] $FrontendPort) `
            -WorkingDirectory $FrontendDir `
            -LogDir $LogDir `
            -Detached:$Detached
    }

    Start-Sleep -Seconds 1
    Write-Host ""
    Write-Ok "Main stack ready"
    Write-Ok "  MCP server -> http://localhost:$McpPort"
    Write-Ok "  Agent API  -> http://localhost:$AgentPort"
    if (Test-Path -LiteralPath $DistDir) { Write-Ok "  Frontend   -> http://localhost:$FrontendPort" }
    Write-Host ""

    if ($Detached) {
        Save-PidRecords -PidFile $PidFile -Records $records
        Write-Ok "Started detached PowerShell stack."
        Write-Host "  status: ./start.ps1 -Status"
        Write-Host "  stop:   ./start.ps1 -Stop"
        Write-Host "  logs:   $LogDir"
        return
    }

    try {
        Wait-RecordedProcesses -Records $records
    }
    finally {
        foreach ($record in $records) {
            Stop-Process -Id ([int] $record.Id) -Force -ErrorAction SilentlyContinue
        }
    }
}
finally {
    $env:MCP_SERVER_URL = $previousMcpServerUrl
}