[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments = @(),
    [string]$RepoRoot = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

$repo = [System.IO.Path]::GetFullPath($RepoRoot)
$tool = Join-Path $repo "backend\sqx-edge-tool\tools\sqx142_compatibility.py"
$pythonCandidates = @(
    (Join-Path $repo "backend\sqx-edge-tool\runtime\python\python.exe"),
    "python"
)

$python = $null
foreach ($candidate in $pythonCandidates) {
    if ($candidate -eq "python") {
        $python = $candidate
        break
    }
    if (Test-Path -LiteralPath $candidate) {
        $python = $candidate
        break
    }
}

if (-not (Test-Path -LiteralPath $tool)) {
    throw "SQX compatibility tool not found: $tool"
}

& $python $tool @Arguments
exit $LASTEXITCODE
