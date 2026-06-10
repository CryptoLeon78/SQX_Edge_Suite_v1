param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'index', 'import-outbox', 'search', 'query', 'get-page', 'save-page')]
  [string]$Action = 'status',

  [string]$Query = '',
  [string]$Slug = '',
  [string]$Title = '',
  [string]$Content = '',
  [string]$Tags = '',
  [string]$FilterStatus = 'pending',
  [int]$Limit = 10
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$BackendRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'

$argsList = @(
  '-m', 'core.local_gbrain',
  $Action,
  '--project-root', $RepoRoot
)

if ($Action -eq 'search' -or $Action -eq 'query') {
  $argsList += @('--query', $Query, '--limit', [string]$Limit)
}
if ($Action -eq 'get-page') {
  $argsList += @('--slug', $Slug)
}
if ($Action -eq 'save-page') {
  $argsList += @('--title', $Title, '--content', $Content, '--slug', $Slug, '--tags', $Tags)
}
if ($Action -eq 'import-outbox') {
  $argsList += @('--status', $FilterStatus, '--limit', [string]$Limit)
}

Push-Location $BackendRoot
try {
  python @argsList
} finally {
  Pop-Location
}
