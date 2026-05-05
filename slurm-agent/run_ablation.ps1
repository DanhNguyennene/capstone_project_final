<#
.SYNOPSIS
  Run ablation studies for the capstone project.
  Ablation 1: Single-agent (no Observer/Operator split)
  Ablation 2: No HITL safety gates

.DESCRIPTION
  Starts MCP mock server + Agent API for each ablation variant,
  runs the single-turn eval (scenario_eval.py) on a subset of tests,
  then saves results.

.PARAMETER Variant
  Which ablation to run: "single-agent", "no-hitl", or "both" (default: both)

.PARAMETER Provider
  LLM provider to use (default: openai)

.PARAMETER Model
  Model name (default: gpt-5-mini)

.PARAMETER Workers
  Parallel eval workers (default: 4)

.PARAMETER Subset
  Number of test cases to sample (default: 0 = all 3135)

.EXAMPLE
  .\run_ablation.ps1 -Variant both -Provider openai -Model gpt-5-mini
  .\run_ablation.ps1 -Variant single-agent -Subset 500
#>
param(
    [ValidateSet("single-agent", "no-hitl", "both")]
    [string]$Variant = "both",

    [string]$Provider = "openai",
    [string]$Model = "gpt-5-mini",
    [int]$Workers = 4,
    [int]$Subset = 0,
    [string]$McpPort = "3002",
    [string]$AgentPort = "8000",
    [string]$Scenario = "mixed"
)

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$MCP_DIR = Join-Path $ROOT "mcp-server"
$AGENT_DIR = Join-Path $ROOT "agent"
$EVAL_DIR = Join-Path $ROOT "evaluation"

# Load .env file from project root into current process environment
$envFile = Join-Path (Split-Path $ROOT -Parent) ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$') {
            $name = $matches[1]; $val = $matches[2].Trim()
            if (-not [System.Environment]::GetEnvironmentVariable($name, "Process")) {
                [System.Environment]::SetEnvironmentVariable($name, $val, "Process")
            }
        }
    }
    Write-Host "[ablation] Loaded .env from $envFile" -ForegroundColor DarkGray
}

$MCP_URL = "http://localhost:$McpPort"
$AGENT_URL = "http://localhost:$AgentPort"

function Write-Info($msg) { Write-Host "[ablation] $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "[ablation] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[ablation] $msg" -ForegroundColor Yellow }

function Stop-Services {
    if ($script:mcpProc -and !$script:mcpProc.HasExited) {
        Write-Info "Stopping MCP server (PID $($script:mcpProc.Id))..."
        Stop-Process -Id $script:mcpProc.Id -Force -ErrorAction SilentlyContinue
    }
    if ($script:agentProc -and !$script:agentProc.HasExited) {
        Write-Info "Stopping Agent API (PID $($script:agentProc.Id))..."
        Stop-Process -Id $script:agentProc.Id -Force -ErrorAction SilentlyContinue
    }
}

function Start-Services([hashtable]$EnvVars = @{}) {
    Write-Info "Starting MCP server (scenario=$Scenario, port=$McpPort)..."
    $script:mcpProc = Start-Process -FilePath "python" `
        -ArgumentList "slurm_mcp_sse.py --mock $Scenario --port $McpPort" `
        -WorkingDirectory $MCP_DIR `
        -PassThru -NoNewWindow -RedirectStandardOutput "NUL"

    Start-Sleep -Seconds 3

    Write-Info "Starting Agent API (port=$AgentPort)..."
    $agentEnv = @{
        "MCP_SERVER_URL" = $MCP_URL
        "AUTO_APPROVE" = "true"
    }
    foreach ($k in $EnvVars.Keys) { $agentEnv[$k] = $EnvVars[$k] }

    # Set env vars for the agent process
    foreach ($k in $agentEnv.Keys) {
        [System.Environment]::SetEnvironmentVariable($k, $agentEnv[$k], "Process")
    }

    $script:agentProc = Start-Process -FilePath "python" `
        -ArgumentList "-m uvicorn main:app --host 0.0.0.0 --port $AgentPort" `
        -WorkingDirectory $AGENT_DIR `
        -PassThru -NoNewWindow -RedirectStandardOutput "NUL"

    # Wait for agent to be ready
    Write-Info "Waiting for agent to come online..."
    $ready = $false
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 2
        try {
            $resp = Invoke-WebRequest -Uri "$AGENT_URL/health" -TimeoutSec 3 -ErrorAction SilentlyContinue
            if ($resp.StatusCode -eq 200) { $ready = $true; break }
        } catch {}
    }
    if (-not $ready) {
        Write-Warn "Agent did not come online within 60s!"
        Stop-Services
        exit 1
    }
    Write-Ok "Agent ONLINE"

    # Clean up env vars so they don't leak to next variant
    foreach ($k in $agentEnv.Keys) {
        [System.Environment]::SetEnvironmentVariable($k, $null, "Process")
    }
}

function Run-Eval([string]$Label) {
    Write-Info "Running eval: $Label"
    $evalArgs = @(
        "scenario_eval.py"
        "--auto-approve"
        "--llm-provider", $Provider
        "--main-model", $Model
        "--specialist-model", $Model
        "--workers", $Workers
        "--mcp-url", $MCP_URL
        "--agent-url", $AGENT_URL
    )

    # Run eval
    Push-Location $EVAL_DIR
    try {
        python @evalArgs
        $exitCode = $LASTEXITCODE
    } finally {
        Pop-Location
    }

    if ($exitCode -ne 0) {
        Write-Warn "Eval exited with code $exitCode"
    }

    # Rename latest result file to include ablation label
    $resultsDir = Join-Path $EVAL_DIR "results"
    $latest = Get-ChildItem $resultsDir -Filter "eval_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latest) {
        $newName = $latest.Name -replace "^eval_", "ablation_${Label}_"
        $newPath = Join-Path $resultsDir $newName
        Move-Item $latest.FullName $newPath -Force
        Write-Ok "Results saved: $newPath"
    }
}

# ==============================================================================
# MAIN
# ==============================================================================

Write-Host ""
Write-Host "=======================================================" -ForegroundColor White
Write-Host "  ABLATION STUDY - Slurm Agent System" -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor White
Write-Host "  Variant  : $Variant"
Write-Host "  Provider : $Provider / $Model"
Write-Host "  Workers  : $Workers"
Write-Host "  Scenario : $Scenario"
Write-Host ""

$variants = @()
if ($Variant -eq "both") {
    $variants = @("single-agent", "no-hitl")
} else {
    $variants = @($Variant)
}

foreach ($v in $variants) {
    Write-Host ""
    Write-Host "-------------------------------------------------------" -ForegroundColor Yellow
    Write-Host "  Running ablation: $v" -ForegroundColor Yellow
    Write-Host "-------------------------------------------------------" -ForegroundColor Yellow

    $envVars = @{}
    switch ($v) {
        "single-agent" { $envVars["ABLATION_SINGLE_AGENT"] = "1" }
        "no-hitl"      { $envVars["ABLATION_NO_HITL"] = "1" }
    }

    try {
        Start-Services -EnvVars $envVars
        Run-Eval -Label $v
    } finally {
        Stop-Services
        Start-Sleep -Seconds 3
    }
}

Write-Host ""
Write-Ok "All ablation runs complete!"
Write-Host ""
