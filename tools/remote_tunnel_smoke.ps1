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

function Read-ResponseBody {
    param([object]$Response)
    if ($null -eq $Response) { return "" }
    try {
        $stream = $Response.GetResponseStream()
        if ($null -eq $stream) { return "" }
        $reader = New-Object System.IO.StreamReader($stream)
        return $reader.ReadToEnd()
    } catch {
        return ""
    }
}

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
        $bodySnippet = Read-ResponseBody $_.Exception.Response
    }
}

$headerText = (($headers.GetEnumerator() | ForEach-Object { "$($_.Key): $($_.Value)" }) -join "`n")
$accessSignal = (
    ($headerText -match '(?i)cf-access-authenticated-user-email|cf-access-jwt-assertion|cf-access-domain|cf-access') -or
    ($headerText -match '(?i)location:.*cloudflareaccess') -or
    ($bodySnippet -match '(?i)cloudflare access|access denied|sign in to.*cloudflare|checking your browser')
)
$appBodyVisible = $bodySnippet -match '(?i)SQX Edge|Project Generator|Template Maker|Mining Control|local_api_only|SQX Edge API'
$backendLocalOnlyVisible = $bodySnippet -match '(?i)local_api_only|SQX Edge API only accepts local browser requests'

$result = [ordered]@{
    ok = ($accessSignal -and -not $appBodyVisible -and -not $backendLocalOnlyVisible)
    phase = "REMOTE-2"
    mode = "cloudflare_access_anonymous_smoke"
    protectedUrl = Redact-Url $ProtectedUrl
    statusCode = $statusCode
    accessSignalDetected = [bool]$accessSignal
    appBodyVisibleToAnonymous = [bool]$appBodyVisible
    backendLocalOnlyVisibleToAnonymous = [bool]$backendLocalOnlyVisible
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
    Write-Host "  Backend local-only body visible: $($result.backendLocalOnlyVisibleToAnonymous)"
}

if (-not $result.ok) {
    exit 1
}
