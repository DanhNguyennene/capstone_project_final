$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = $PSScriptRoot

& (Join-Path $Root "start.ps1") -Stop
& (Join-Path $Root "start_eval_server.ps1") -Stop
& (Join-Path $Root "start.ps1") -Detached
& (Join-Path $Root "start_eval_server.ps1") -Detached