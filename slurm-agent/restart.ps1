$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = $PSScriptRoot
$StartWindows = Join-Path $Root "start_windows.ps1"

& $StartWindows -Stop
& $StartWindows @args