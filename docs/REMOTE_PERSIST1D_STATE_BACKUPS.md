# REMOTE-PERSIST1D - Workspace State Backups And Restore

## Purpose

REMOTE-PERSIST1D makes Control Panel backup/restore safe for multi-user remote
operation. A remote user's snapshots must live inside that user's
server-derived workspace, not in the operator-global `analysis/analysis_output`
folder.

Local operator mode remains compatible with the historical local backup folder.

## Storage Model

Local mode:

`analysis/analysis_output/state_backup_*.json`

Remote mode:

`<workspace>/config/state_backups/state_backup_*.json`

Remote public responses use:

`workspace://state-backups`

No response may expose local Windows paths, workspace roots, raw emails,
cookies, tokens, Cloudflare identifiers or protected URLs.

## Backend Contract

- `remote-state-backup-v1`
- `POST /api/state/backup`
  - local mode: stores in `analysis/analysis_output`;
  - remote mode: requires active app session plus trusted access context;
  - remote mode: stores only in `<workspace>/config/state_backups`;
  - filters payload to allowlisted dashboard keys;
  - writes workspace audit event `remote_state_backup_created`.
- `GET /api/state/backups`
  - local mode: lists local operator snapshots;
  - remote mode: lists only the active workspace snapshots;
  - remote mode without valid app session returns `remote_session_required`.
- `GET /api/state/restore/<filename>`
  - local mode: reads local operator snapshots;
  - remote mode: reads only active workspace snapshots;
  - validates filename and prevents path traversal;
  - writes workspace audit event `remote_state_backup_restored`.

## Allowed State Keys

The backend accepts only the same non-sensitive dashboard state keys used by the
frontend backup module:

- `sqx_priority_progress_v1`
- `sqx_plan_user_v1`
- `sqx_pipeline_state_v1`
- `sqx_strategies_user_v1`
- `sqx_strategies_deleted_v1`
- `sqx_workflow_checklist_v1`
- `sqx_view_creator_presets_v1`
- `sqx_pg_custom_presets_v1`
- `sqx_home_trace_v1`
- `sqx_pg_api_base_v1`

License, fulfillment, payment, entitlement, security, tunnel, workspace path and
private evidence keys are not accepted in snapshots.

## Frontend Contract

`app/js/modules/state-backup.js` now sends `/api/state/*` requests with
credentials included, renders whether a snapshot is local or workspace-scoped,
and after remote restore asks `SQX.remoteState.saveSnapshot(...)` to resync
restored allowed keys back into the active workspace state store.

Restore remains traceable through the shared modal:

- snapshot name;
- scope local/workspace;
- allowed keys;
- automatic pre-restore backup;
- excluded sensitive surfaces.

## Explicit Non-Scope

This phase does not create a full server disaster-recovery archive of every
workspace folder. It also does not migrate SQX Views user presets into a
first-class backend database beyond including the current localStorage key in
the snapshot payload.

SQX Views/user presets were later persisted as workspace-owned state in
REMOTE-PERSIST1E through `remote-workspace-state-v1`; they remain included in
snapshot payloads for restore compatibility.

## Acceptance

- Remote snapshots are stored under the active workspace only.
- Two remote identities cannot list or restore each other's snapshots.
- Remote restore returns no local paths and no raw identity.
- Sensitive keys are filtered by the backend even if the browser submits them.
- Local operator backup/restore remains compatible.
