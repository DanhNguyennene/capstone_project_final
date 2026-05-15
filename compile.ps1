[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Set-Location -LiteralPath $PSScriptRoot

function Invoke-CheckedStep {
    param(
        [Parameter(Mandatory = $true)][string] $Label,
        [Parameter(Mandatory = $true)][string] $Command,
        [string[]] $Arguments = @()
    )

    Write-Host $Label

    $nativePreference = Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue
    if ($nativePreference) {
        $previousNativePreference = $PSNativeCommandUseErrorActionPreference
        $PSNativeCommandUseErrorActionPreference = $false
    }

    try {
        & $Command @Arguments *> $null
        if ($LASTEXITCODE -ne 0) {
            throw "$Command failed with exit code $LASTEXITCODE. Check poster_table.log for details."
        }
    }
    finally {
        if ($nativePreference) {
            $PSNativeCommandUseErrorActionPreference = $previousNativePreference
        }
    }
}

if (-not (Get-Command xelatex -ErrorAction SilentlyContinue)) {
    throw "Required tool not found: xelatex"
}

Write-Host "=== Compiling poster_table.tex ==="

Invoke-CheckedStep -Label "[1/2] Running xelatex (first pass)..." -Command "xelatex" -Arguments @("-interaction=nonstopmode", "poster_table.tex")
Invoke-CheckedStep -Label "[2/2] Running xelatex (final pass)..." -Command "xelatex" -Arguments @("-interaction=nonstopmode", "poster_table.tex")

if (Test-Path -LiteralPath "poster_table.pdf") {
    $outName = "poster_HK252-DATN-417_2252102.pdf"
    Move-Item -Force -LiteralPath "poster_table.pdf" -Destination $outName
    Write-Host "=== Done! Output: $outName ==="
}
else {
    throw "Compilation failed. Check poster_table.log for errors."
}
