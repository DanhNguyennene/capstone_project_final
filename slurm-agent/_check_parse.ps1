$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile('C:\uni\capstone_project\slurm-agent\run_ablation.ps1', [ref]$tokens, [ref]$errors)
if ($errors.Count -gt 0) {
    foreach ($e in $errors) {
        Write-Host "Line $($e.Extent.StartLineNumber): $($e.Message)"
    }
    exit 1
} else {
    Write-Host "No errors"
}
