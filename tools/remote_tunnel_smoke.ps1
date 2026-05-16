[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProtectedUrl,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

function Redact-Url {
    param([string]$Url)
    try {
        $uri = [Uri]$Url
        return "$($uri.Scheme)://<protected-hostname>$($uri.AbsolutePath)"
    } catch {
        return "<invalid-url>"
    }
}

function Test-HttpUrl {
    param([string]$Url)
    return $Url -match '^https://'
}

if (-not (Test-HttpUrl $ProtectedUrl)) {
    throw "REMOTE-2 smoke requires an https protected URL. Do not use plain http for the public tunnel target."
}

$statusCode = $null
$headers = @{}
$bodySnippet = ""
$errorText = $null

try {
    $response = Invoke-WebRequest -Uri $ProtectedUrl -Method GET -MaximumRedirection 0 -TimeoutSec 10 -ErrorAction Stop
    $statusCode = [int]$response.StatusCode
    $headers = $response.Headers
    $bodySnippet = ($response.Content | Out-String)
} catch {
    $errorText = $_.Exception.Message
    if ($_.Exception.Response) {
        $statusCode = [int]$_.Exception.Response.StatusCode
        foreach ($key in $_.Exception.Response.Headers.AllKeys) {
            $headers[$key] = $_.Exception.Response.Headers[$key]
        }
    }
}

$headerText = (($headers.GetEnumerator() | ForEach-Object { "$($_.Key): $($_.Value)" }) -join "`n")
$accessSignal = (
    ($statusCode -in @(302, 401, 403)) -or
    ($headerText -match '(?i)cf-access|cloudflare|location') -or
    ($bodySnippet -match '(?i)cloudflare access|sign in')
)
$appBodyVisible = $bodySnippet -match '(?i)SQX Edge|Project Generator|Template Maker|Mining Control'

$result = [ordered]@{
    ok = ($accessSignal -and -not $appBodyVisible)
    phase = "REMOTE-2"
    mode = "cloudflare_access_anonymous_smoke"
    protectedUrl = Redact-Url $ProtectedUrl
    statusCode = $statusCode
    accessSignalDetected = [bool]$accessSignal
    appBodyVisibleToAnonymous = [bool]$appBodyVisible
    error = $errorText
}

if ($Json) {
    $result | ConvertTo-Json -Depth 6
} else {
    Write-Host "REMOTE-2 anonymous Cloudflare Access smoke"
    Write-Host "  URL: $($result.protectedUrl)"
    Write-Host "  OK: $($result.ok)"
    Write-Host "  Status: $statusCode"
    Write-Host "  Access signal: $($result.accessSignalDetected)"
    Write-Host "  App body visible: $($result.appBodyVisibleToAnonymous)"
}

if (-not $result.ok) {
    exit 1
}
