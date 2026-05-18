# remote_link_preview_smoke.ps1 - verifies the Cloudflare social-preview boundary.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProtectedUrl,
    [string]$PreviewPath = "/link-preview",
    [string]$DashboardPath = "/dashboard",
    [string]$ImagePath = "/assets/brand/sqx-social-preview.png",
    [switch]$Json
)

$ErrorActionPreference = "Stop"

function Test-HttpsUrl {
    param([string]$Url)
    return $Url -match '^https://'
}

function Get-Origin {
    param([string]$Url)
    try {
        $uri = [Uri]$Url
        return "$($uri.Scheme)://$($uri.Authority)"
    } catch {
        throw "Invalid URL. Use the protected Cloudflare https URL."
    }
}

function Join-UrlPath {
    param([string]$Origin, [string]$Path)
    return "$($Origin.TrimEnd('/'))/$($Path.TrimStart('/'))"
}

function Redact-Url {
    param([string]$Url)
    try {
        $uri = [Uri]$Url
        return "$($uri.Scheme)://<protected-hostname>$($uri.AbsolutePath)"
    } catch {
        return "<invalid-url>"
    }
}

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

function Invoke-SmokeRequest {
    param([string]$Url)

    $statusCode = $null
    $headers = @{}
    $body = ""
    $errorText = $null

    try {
        $request = [System.Net.WebRequest]::Create($Url)
        $request.Method = "GET"
        $request.AllowAutoRedirect = $false
        $request.Timeout = 12000
        $request.UserAgent = "sqx-edge-link-preview-smoke/1.0"
        $response = $request.GetResponse()
        $statusCode = [int]$response.StatusCode
        foreach ($key in $response.Headers.AllKeys) {
            $headers[$key] = $response.Headers[$key]
        }
        $body = Read-ResponseBody $response
    } catch [System.Net.WebException] {
        $errorText = $_.Exception.Message
        if ($_.Exception.Response) {
            $response = $_.Exception.Response
            $statusCode = [int]$response.StatusCode
            foreach ($key in $response.Headers.AllKeys) {
                $headers[$key] = $response.Headers[$key]
            }
            $body = Read-ResponseBody $response
        }
    } catch {
        $errorText = $_.Exception.Message
    }

    return [ordered]@{
        url = Redact-Url $Url
        statusCode = $statusCode
        headers = $headers
        body = $body
        error = $errorText
    }
}

if (-not (Test-HttpsUrl $ProtectedUrl)) {
    throw "ROOT-PREVIEW1 smoke requires the protected Cloudflare https URL."
}

$origin = Get-Origin $ProtectedUrl
$rootUrl = Join-UrlPath $origin "/"
$previewUrl = Join-UrlPath $origin $PreviewPath
$dashboardUrl = Join-UrlPath $origin $DashboardPath
$imageUrl = Join-UrlPath $origin $ImagePath

$root = Invoke-SmokeRequest $rootUrl
$preview = Invoke-SmokeRequest $previewUrl
$dashboard = Invoke-SmokeRequest $dashboardUrl
$image = Invoke-SmokeRequest $imageUrl

function Test-AccessSignal {
    param([object]$Response)
    $headerText = (($Response.headers.GetEnumerator() | ForEach-Object { "$($_.Key): $($_.Value)" }) -join "`n")
    return (
        ($headerText -match '(?i)cf-access-authenticated-user-email|cf-access-jwt-assertion|cf-access-domain|cf-access') -or
        ($headerText -match '(?i)location:.*cloudflareaccess') -or
        ($Response.body -match '(?i)cloudflare access|access denied|sign in to.*cloudflare|checking your browser')
    )
}

function Test-AppBodyVisible {
    param([object]$Response)
    return $Response.body -match '(?i)remote-welcome-gate|Project Generator|Template Maker|Mining Control|SQX Edge API|local_api_only'
}

$rootHasMeta = (
    ($root.statusCode -eq 200) -and
    ($root.body -match 'SQX Edge Suite \| Plataforma Pro para SQX Traders') -and
    ($root.body -match 'property="og:image"') -and
    ($root.body -match [regex]::Escape($ImagePath)) -and
    ($root.body -match [regex]::Escape($DashboardPath))
)
$rootAccessSignal = Test-AccessSignal $root
$rootAppBodyVisible = Test-AppBodyVisible $root
$dashboardAccessSignal = Test-AccessSignal $dashboard
$dashboardAppBodyVisible = Test-AppBodyVisible $dashboard

$previewHasMeta = (
    ($preview.statusCode -eq 200) -and
    ($preview.body -match 'SQX Edge Suite \| Plataforma Pro para SQX Traders') -and
    ($preview.body -match 'property="og:image"') -and
    ($preview.body -match [regex]::Escape($ImagePath))
)
$previewLeaksApp = $preview.body -match '(?i)remote-welcome-gate|Cf-Access-Authenticated-User-Email|local_api_only|workspace|session token|grant key'

$imageContentType = ""
if ($image.headers.ContainsKey("Content-Type")) {
    $imageContentType = [string]$image.headers["Content-Type"]
}
$imageOk = ($image.statusCode -eq 200) -and ($imageContentType -match '(?i)image/png')

$result = [ordered]@{
    ok = ([bool]$rootHasMeta -and -not [bool]$rootAccessSignal -and -not [bool]$rootAppBodyVisible -and [bool]$dashboardAccessSignal -and -not [bool]$dashboardAppBodyVisible -and [bool]$previewHasMeta -and -not [bool]$previewLeaksApp -and [bool]$imageOk)
    phase = "ROOT-PREVIEW1"
    mode = "cloudflare_root_preview_dashboard_boundary_smoke"
    rootUrl = Redact-Url $rootUrl
    previewUrl = Redact-Url $previewUrl
    dashboardUrl = Redact-Url $dashboardUrl
    imageUrl = Redact-Url $imageUrl
    rootPreviewPublic = [bool]$rootHasMeta
    rootAccessSignalDetected = [bool]$rootAccessSignal
    rootAppBodyVisibleToAnonymous = [bool]$rootAppBodyVisible
    dashboardProtected = [bool]$dashboardAccessSignal
    dashboardAppBodyVisibleToAnonymous = [bool]$dashboardAppBodyVisible
    previewPublic = [bool]$previewHasMeta
    previewLeaksAppOrPrivateState = [bool]$previewLeaksApp
    imagePublic = [bool]$imageOk
    statusCodes = [ordered]@{
        root = $root.statusCode
        preview = $preview.statusCode
        dashboard = $dashboard.statusCode
        image = $image.statusCode
    }
    errors = [ordered]@{
        root = $root.error
        preview = $preview.error
        dashboard = $dashboard.error
        image = $image.error
    }
}

if ($Json) {
    $result | ConvertTo-Json -Depth 6
} else {
    Write-Host "ROOT-PREVIEW1 Cloudflare root preview/dashboard boundary smoke"
    Write-Host "  Root preview public: $($result.rootPreviewPublic)"
    Write-Host "  Root Access signal: $($result.rootAccessSignalDetected)"
    Write-Host "  Root app body visible: $($result.rootAppBodyVisibleToAnonymous)"
    Write-Host "  Dashboard protected: $($result.dashboardProtected)"
    Write-Host "  Dashboard app body visible: $($result.dashboardAppBodyVisibleToAnonymous)"
    Write-Host "  Preview public: $($result.previewPublic)"
    Write-Host "  Preview leaks app/private state: $($result.previewLeaksAppOrPrivateState)"
    Write-Host "  Social image public: $($result.imagePublic)"
    Write-Host "  OK: $($result.ok)"
}

if (-not $result.ok) {
    exit 1
}
