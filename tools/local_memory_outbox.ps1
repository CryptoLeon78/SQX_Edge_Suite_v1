param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'enqueue', 'list', 'mark-synced')]
  [string]$Action = 'status',

  [string]$Title = '',
  [string]$Content = '',
  [string]$Source = 'codex_mem_limit_fallback',
  [string]$Tags = '',
  [string]$FilterStatus = 'pending',
  [int]$Limit = 20,
  [int]$OutboxId = 0,
  [string]$MemNoteId = ''
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$BackendRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'

$argsList = @(
  '-m', 'core.local_memory_outbox',
  $Action,
  '--project-root', $RepoRoot
)

if ($Action -eq 'enqueue') {
  $argsList += @('--title', $Title, '--content', $Content, '--source', $Source, '--tags', $Tags)
}
if ($Action -eq 'list') {
  $argsList += @('--status', $FilterStatus, '--limit', [string]$Limit)
}
if ($Action -eq 'mark-synced') {
  $argsList += @('--outbox-id', [string]$OutboxId, '--mem-note-id', $MemNoteId)
}

Push-Location $BackendRoot
try {
  python @argsList
} finally {
  Pop-Location
}
