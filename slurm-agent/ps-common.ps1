function Write-Info {
    param([Parameter(Mandatory = $true)][string] $Message)
    Write-Host "[start] $Message" -ForegroundColor Cyan
}

function Write-Ok {
    param([Parameter(Mandatory = $true)][string] $Message)
    Write-Host "[start] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([Parameter(Mandatory = $true)][string] $Message)
    Write-Host "[start] $Message" -ForegroundColor Yellow
}

function Initialize-Directory {
    param([Parameter(Mandatory = $true)][string] $Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Load-EnvLikeFile {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string] $Path)

    if (-not (Test-Path -LiteralPath $Path)) { return $false }

    $loaded = $false
    foreach ($raw in Get-Content -LiteralPath $Path) {
        $line = $raw.Trim()
        if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith("#")) { continue }
        if ($line.StartsWith("export ")) { $line = $line.Substring(7).Trim() }

        $equalsIndex = $line.IndexOf("=")
        if ($equalsIndex -ge 0) {
            $key = $line.Substring(0, $equalsIndex).Trim()
            $value = $line.Substring($equalsIndex + 1).Trim()

            if ($value.Length -ge 2) {
                $first = $value.Substring(0, 1)
                $last = $value.Substring($value.Length - 1, 1)
                if (($first -eq '"' -and $last -eq '"') -or ($first -eq "'" -and $last -eq "'")) {
                    $value = $value.Substring(1, $value.Length - 2)
                }
            }

            if ($key -eq "OPEN_AI_KEY") {
                [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $value, "Process")
                $loaded = $true
            }
            elseif ($key -in @("GH_TOKEN", "GH_PAT", "GITHUB_PAT")) {
                [Environment]::SetEnvironmentVariable("GITHUB_TOKEN", $value, "Process")
                $loaded = $true
            }
            elseif ($key -match '^[A-Za-z_][A-Za-z0-9_]*$') {
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
                $loaded = $true
            }
            else {
                Write-Warn "Skipping invalid key name in $(Split-Path -Leaf $Path): $key"
            }
            continue
        }

        if ($line.StartsWith("sk-")) {
            [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $line, "Process")
            $loaded = $true
        }
        elseif ($line.StartsWith("ghp_") -or $line.StartsWith("github_pat_") -or $line.StartsWith("gho_") -or $line.StartsWith("ghu_") -or $line.StartsWith("ghs_")) {
            [Environment]::SetEnvironmentVariable("GITHUB_TOKEN", $line, "Process")
            $loaded = $true
        }
    }

    return $loaded
}

function Load-LocalEnv {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string] $Root)

    $files = @(
        (Join-Path $Root ".key"),
        (Join-Path (Split-Path -Parent $Root) ".key"),
        (Join-Path $Root ".env"),
        (Join-Path (Split-Path -Parent $Root) ".env")
    )

    foreach ($file in $files) {
        if (Load-EnvLikeFile -Path $file) {
            Write-Ok "Loaded local secrets from: $file"
        }
    }

    if (-not $env:OPENAI_API_KEY -and $env:OPEN_AI_KEY) {
        $env:OPENAI_API_KEY = $env:OPEN_AI_KEY
    }
    if (-not $env:GITHUB_TOKEN -and $env:GH_TOKEN) {
        $env:GITHUB_TOKEN = $env:GH_TOKEN
    }
    if ($env:OPENAI_API_KEY -and -not $env:LLM_PROVIDER) {
        $env:LLM_PROVIDER = "openai"
        if (-not $env:OPENAI_MODEL) { $env:OPENAI_MODEL = "gpt-4o-mini" }
        Write-Ok "Detected OPENAI_API_KEY; defaulting LLM_PROVIDER=openai"
    }
}

function Resolve-Executable {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string] $Name)

    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $command) { throw "Executable not found: $Name" }
    return $command.Source
}

function Invoke-Checked {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string] $FilePath,
        [string[]] $Arguments = @(),
        [string] $WorkingDirectory = $PWD.Path
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

function Invoke-NativeCapture {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string] $FilePath,
        [string[]] $Arguments = @(),
        [string] $WorkingDirectory = $PWD.Path
    )

    Push-Location $WorkingDirectory
    $previousErrorActionPreference = $ErrorActionPreference
    $nativePreference = Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue
    if ($nativePreference) {
        $previousNativePreference = $PSNativeCommandUseErrorActionPreference
        $PSNativeCommandUseErrorActionPreference = $false
    }

    try {
        $ErrorActionPreference = "Continue"
        $output = & $FilePath @Arguments 2>&1
        $exitCode = $LASTEXITCODE
        return [pscustomobject]@{
            ExitCode = $exitCode
            Output = ($output | Out-String).Trim()
        }
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
        if ($nativePreference) {
            $PSNativeCommandUseErrorActionPreference = $previousNativePreference
        }
        Pop-Location
    }
}

function Convert-ToStartProcessCommand {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string] $FilePath,
        [string[]] $Arguments = @()
    )

    $extension = [System.IO.Path]::GetExtension($FilePath).ToLowerInvariant()
    if ($extension -eq ".ps1") {
        return [pscustomobject]@{
            FilePath = (Resolve-Executable -Name "powershell")
            Arguments = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $FilePath) + $Arguments
        }
    }
    if ($extension -eq ".cmd" -or $extension -eq ".bat") {
        return [pscustomobject]@{
            FilePath = (Resolve-Executable -Name "cmd")
            Arguments = @("/c", $FilePath) + $Arguments
        }
    }

    return [pscustomobject]@{
        FilePath = $FilePath
        Arguments = $Arguments
    }
}

function Get-PidRecords {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string] $PidFile)

    if (-not (Test-Path -LiteralPath $PidFile)) { return @() }
    try {
        $raw = Get-Content -LiteralPath $PidFile -Raw
        if ([string]::IsNullOrWhiteSpace($raw)) { return @() }
        $data = $raw | ConvertFrom-Json
        if ($data.PSObject.Properties.Name -contains "processes") {
            return @($data.processes)
        }
        return @($data)
    }
    catch {
        Write-Warn "Could not read PID file: $PidFile"
        return @()
    }
}

function Get-LivePidRecords {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string] $PidFile)

    $live = @()
    foreach ($record in @(Get-PidRecords -PidFile $PidFile)) {
        $process = Get-Process -Id ([int] $record.Id) -ErrorAction SilentlyContinue
        if ($process) { $live += $record }
    }
    return $live
}

function Show-RecordedProcessStatus {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string] $PidFile)

    $records = @(Get-PidRecords -PidFile $PidFile)
    if ($records.Count -eq 0) {
        Write-Warn "No PID file found: $PidFile"
        return
    }

    foreach ($record in $records) {
        $process = Get-Process -Id ([int] $record.Id) -ErrorAction SilentlyContinue
        if ($process) {
            Write-Ok "$($record.Name) running (pid=$($record.Id))"
        }
        else {
            Write-Warn "$($record.Name) not running (pid=$($record.Id))"
        }
    }
}

function Stop-RecordedProcesses {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string] $PidFile)

    $records = @(Get-PidRecords -PidFile $PidFile)
    if ($records.Count -eq 0) {
        Write-Warn "No PID file found: $PidFile"
        return
    }

    [array]::Reverse($records)
    foreach ($record in $records) {
        $process = Get-Process -Id ([int] $record.Id) -ErrorAction SilentlyContinue
        if ($process) {
            Write-Info "Stopping $($record.Name) (pid=$($record.Id))"
            Stop-Process -Id ([int] $record.Id) -Force -ErrorAction SilentlyContinue
        }
    }

    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
    Write-Ok "Stopped recorded processes."
}

function Save-PidRecords {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string] $PidFile,
        [Parameter(Mandatory = $true)][object[]] $Records
    )

    Initialize-Directory -Path (Split-Path -Parent $PidFile)
    [pscustomobject]@{
        started = (Get-Date).ToString("o")
        processes = $Records
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $PidFile -Encoding UTF8
}

function Start-ManagedProcess {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string] $Name,
        [Parameter(Mandatory = $true)][string] $FilePath,
        [string[]] $Arguments = @(),
        [Parameter(Mandatory = $true)][string] $WorkingDirectory,
        [Parameter(Mandatory = $true)][string] $LogDir,
        [switch] $Detached
    )

    Initialize-Directory -Path $LogDir
    $command = Convert-ToStartProcessCommand -FilePath $FilePath -Arguments $Arguments
    Write-Info "Starting ${Name}: $($command.FilePath) $($command.Arguments -join ' ')"

    $startParams = @{
        FilePath = $command.FilePath
        ArgumentList = $command.Arguments
        WorkingDirectory = $WorkingDirectory
        PassThru = $true
    }

    $stdout = Join-Path $LogDir "$Name.out.log"
    $stderr = Join-Path $LogDir "$Name.err.log"
    if ($Detached) {
        $startParams["RedirectStandardOutput"] = $stdout
        $startParams["RedirectStandardError"] = $stderr
    }
    else {
        $startParams["NoNewWindow"] = $true
    }

    $process = Start-Process @startParams
    return [pscustomobject]@{
        Name = $Name
        Id = $process.Id
        Command = "$($command.FilePath) $($command.Arguments -join ' ')"
        WorkingDirectory = $WorkingDirectory
        Stdout = $stdout
        Stderr = $stderr
    }
}

function Wait-RecordedProcesses {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][object[]] $Records)

    while ($true) {
        $live = @()
        foreach ($record in $Records) {
            $process = Get-Process -Id ([int] $record.Id) -ErrorAction SilentlyContinue
            if ($process) { $live += $record }
        }
        if ($live.Count -eq 0) { break }
        Start-Sleep -Seconds 1
    }
}