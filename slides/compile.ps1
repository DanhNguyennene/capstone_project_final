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
            throw "$Command failed with exit code $LASTEXITCODE. Check main.log for details."
        }
    }
    finally {
        if ($nativePreference) {
            $PSNativeCommandUseErrorActionPreference = $previousNativePreference
        }
    }
}

foreach ($tool in @("xelatex", "biber")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        throw "Required tool not found: $tool"
    }
}

Write-Host "=== Compiling slides/main.tex ==="

Invoke-CheckedStep -Label "[1/4] Running xelatex (first pass)..." -Command "xelatex" -Arguments @("-interaction=nonstopmode", "main.tex")
Invoke-CheckedStep -Label "[2/4] Running biber..." -Command "biber" -Arguments @("main")
Invoke-CheckedStep -Label "[3/4] Running xelatex (second pass)..." -Command "xelatex" -Arguments @("-interaction=nonstopmode", "main.tex")
Invoke-CheckedStep -Label "[4/4] Running xelatex (final pass)..." -Command "xelatex" -Arguments @("-interaction=nonstopmode", "main.tex")

if (Test-Path -LiteralPath "main.pdf") {
    $outName = "slides_HK252-DATN-417_2252102.pdf"
    Move-Item -Force -LiteralPath "main.pdf" -Destination $outName
    Write-Host "=== Done! Output: $outName ==="
}
else {
    throw "Compilation failed. Check main.log for errors."
}
