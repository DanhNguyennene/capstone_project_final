$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = $PSScriptRoot

try {
	& (Join-Path $Root "start.ps1") -Stop
	& (Join-Path $Root "start_eval_server.ps1") -Stop
	& (Join-Path $Root "start.ps1") -Detached
	& (Join-Path $Root "start_eval_server.ps1") -Detached
}
catch {
	Write-Host "[restart] Startup failed; stopping any services that were started." -ForegroundColor Yellow
	& (Join-Path $Root "start.ps1") -Stop
	& (Join-Path $Root "start_eval_server.ps1") -Stop
	throw
}