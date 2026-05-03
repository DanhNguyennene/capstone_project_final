[CmdletBinding()]
param(
    [Alias("Host")]
    [string] $HostName = "0.0.0.0",
    [int] $Port = 0,
    [string] $Python = "",
    [switch] $Detached,
    [switch] $Status,
    [switch] $Stop
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = $PSScriptRoot
. (Join-Path $Root "ps-common.ps1")

$LogDir = Join-Path $Root "logs"
$PidFile = Join-Path $LogDir "ps-eval-server-pids.json"

if ($Status) {
    Show-RecordedProcessStatus -PidFile $PidFile
    return
}

if ($Stop) {
    Stop-RecordedProcesses -PidFile $PidFile
    return
}

Load-LocalEnv -Root $Root

if ($Port -le 0) { $Port = 8080 }
if (-not $Python) { $Python = if ($env:PYTHON) { $env:PYTHON } else { "python3" } }

if ($Detached -and (@(Get-LivePidRecords -PidFile $PidFile)).Count -gt 0) {
    throw "PowerShell eval server is already running. Use ./start_eval_server.ps1 -Status or ./start_eval_server.ps1 -Stop."
}

$PythonExe = Resolve-Executable -Name $Python
$dependencyCheck = & $PythonExe -c "import fastapi, uvicorn" 2>&1
if ($LASTEXITCODE -ne 0) {
        $detail = ($dependencyCheck | Out-String).Trim()
        throw @"
Missing Python dependencies for the eval server.
Install them with:
    $PythonExe -m pip install fastapi uvicorn

Original error:
$detail
"@
}

$record = Start-ManagedProcess `
    -Name "eval-server" `
    -FilePath $PythonExe `
    -Arguments @("eval_server.py", "--host", $HostName, "--port", [string] $Port) `
    -WorkingDirectory (Join-Path $Root "evaluation") `
    -LogDir $LogDir `
    -Detached:$Detached

Start-Sleep -Seconds 1
Write-Ok "Eval server -> http://localhost:$Port"

if ($Detached) {
    Save-PidRecords -PidFile $PidFile -Records @($record)
    Write-Ok "Started detached PowerShell eval server."
    Write-Host "  status: ./start_eval_server.ps1 -Status"
    Write-Host "  stop:   ./start_eval_server.ps1 -Stop"
    Write-Host "  logs:   $LogDir"
    return
}

try {
    Wait-RecordedProcesses -Records @($record)
}
finally {
    Stop-Process -Id ([int] $record.Id) -Force -ErrorAction SilentlyContinue
}