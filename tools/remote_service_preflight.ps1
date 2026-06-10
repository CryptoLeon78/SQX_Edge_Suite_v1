[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$ApiUrl = "http://127.0.0.1:5050/api/health",
    [switch]$RequireSqxReady,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Get-ConfigValue {
    param(
        [object]$Config,
        [string]$Name,
        [object]$Default = $null
    )
    if ($null -eq $Config) { return $Default }
    $prop = $Config.PSObject.Properties[$Name]
    if ($null -eq $prop -or $null -eq $prop.Value -or $prop.Value -eq "") { return $Default }
    return $prop.Value
}

function Resolve-ToolPath {
    param(
        [string]$ToolRoot,
        [string]$Value
    )
    if ([string]::IsNullOrWhiteSpace($Value)) { return $null }
    if ([System.IO.Path]::IsPathRooted($Value)) {
        return [System.IO.Path]::GetFullPath($Value)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $ToolRoot $Value))
}

function Test-LocalApiUrl {
    param([string]$Url)
    return $Url -match '^http://(127\.0\.0\.1|localhost)(:\d+)?/'
}

$repo = [System.IO.Path]::GetFullPath($RepoRoot)
$toolRoot = Join-Path $repo "backend\sqx-edge-tool"
$serverPy = Join-Path $toolRoot "api\server.py"
$configPath = Join-Path $toolRoot "config.json"
$embeddedPython = Join-Path $toolRoot "runtime\python\python.exe"
$venvPython = Join-Path $toolRoot "venv\Scripts\python.exe"
$pythonPath = $null
if (Test-Path -LiteralPath $embeddedPython) {
    $pythonPath = $embeddedPython
} elseif (Test-Path -LiteralPath $venvPython) {
    $pythonPath = $venvPython
}

$config = $null
$configError = $null
if (Test-Path -LiteralPath $configPath) {
    try {
        $config = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        $configError = $_.Exception.Message
    }
}

$templateCapa1 = Resolve-ToolPath $toolRoot (Get-ConfigValue $config "template_capa1" "templates/Capa1_Long.cfx")
$templateCapa2 = Resolve-ToolPath $toolRoot (Get-ConfigValue $config "template_capa2" "templates/Capa2_Base.cfx")
$outputDir = Resolve-ToolPath $toolRoot (Get-ConfigValue $config "output_dir" "output")
$sqxDataDb = Get-ConfigValue $config "sqx_data_db" ""
$sqxPath = Get-ConfigValue $config "sqx_path" ""
$sqxProjectsDir = Get-ConfigValue $config "sqx_projects_dir" ""

$health = [ordered]@{
    reachable = $false
    ok = $false
    error = $null
    payload = $null
}

if (Test-LocalApiUrl $ApiUrl) {
    try {
        $payload = Invoke-RestMethod -Uri $ApiUrl -TimeoutSec 2
        $health.reachable = $true
        $health.ok = [bool]$payload.ok
        $health.payload = $payload
    } catch {
        $health.error = $_.Exception.Message
    }
} else {
    $health.error = "Refusing non-local API URL in REMOTE-1 preflight."
}

$checks = [ordered]@{
    repoRootExists = Test-Path -LiteralPath $repo
    toolRootExists = Test-Path -LiteralPath $toolRoot
    serverPyExists = Test-Path -LiteralPath $serverPy
    apiUrlLocalOnly = Test-LocalApiUrl $ApiUrl
    configExists = Test-Path -LiteralPath $configPath
    configReadable = ($null -eq $configError)
    pythonRuntimeExists = [bool]$pythonPath
    templateCapa1Exists = ($templateCapa1 -and (Test-Path -LiteralPath $templateCapa1))
    templateCapa2Exists = ($templateCapa2 -and (Test-Path -LiteralPath $templateCapa2))
    outputDirExists = ($outputDir -and (Test-Path -LiteralPath $outputDir))
    sqxPathSet = -not [string]::IsNullOrWhiteSpace($sqxPath)
    sqxPathExists = (-not [string]::IsNullOrWhiteSpace($sqxPath)) -and (Test-Path -LiteralPath $sqxPath)
    sqxDataDbSet = -not [string]::IsNullOrWhiteSpace($sqxDataDb)
    sqxDataDbExists = (-not [string]::IsNullOrWhiteSpace($sqxDataDb)) -and (Test-Path -LiteralPath $sqxDataDb)
    sqxProjectsDirSet = -not [string]::IsNullOrWhiteSpace($sqxProjectsDir)
    sqxProjectsDirExists = (-not [string]::IsNullOrWhiteSpace($sqxProjectsDir)) -and (Test-Path -LiteralPath $sqxProjectsDir)
    healthReachable = $health.reachable
    healthOk = $health.ok
}

$required = @("repoRootExists", "toolRootExists", "serverPyExists", "apiUrlLocalOnly", "configReadable")
if ($RequireSqxReady) {
    $required += @(
        "pythonRuntimeExists",
        "configExists",
        "templateCapa1Exists",
        "templateCapa2Exists",
        "outputDirExists",
        "sqxPathSet",
        "sqxPathExists",
        "sqxDataDbSet",
        "sqxDataDbExists",
        "sqxProjectsDirSet",
        "sqxProjectsDirExists"
    )
}

$missing = @()
foreach ($name in $required) {
    if (-not [bool]$checks[$name]) {
        $missing += $name
    }
}

$result = [ordered]@{
    ok = ($missing.Count -eq 0)
    phase = "REMOTE-1"
    mode = "laptop_server_baseline"
    repoRoot = $repo
    toolRoot = $toolRoot
    apiUrl = $ApiUrl
    localOnly = [bool]$checks.apiUrlLocalOnly
    requireSqxReady = [bool]$RequireSqxReady
    pythonPath = $pythonPath
    configPath = $configPath
    configError = $configError
    paths = [ordered]@{
        templateCapa1 = $templateCapa1
        templateCapa2 = $templateCapa2
        outputDir = $outputDir
        sqxPath = $sqxPath
        sqxDataDb = $sqxDataDb
        sqxProjectsDir = $sqxProjectsDir
    }
    checks = $checks
    health = $health
    missingRequired = $missing
}

if ($Json) {
    $result | ConvertTo-Json -Depth 8
} else {
    Write-Host "REMOTE-1 laptop server preflight"
    Write-Host "  OK: $($result.ok)"
    Write-Host "  API: $ApiUrl"
    Write-Host "  Python: $pythonPath"
    if ($missing.Count -gt 0) {
        Write-Host "  Missing required checks: $($missing -join ', ')"
    }
    Write-Host "  Use -Json for machine-readable output."
}

if (-not $result.ok) {
    exit 1
}
