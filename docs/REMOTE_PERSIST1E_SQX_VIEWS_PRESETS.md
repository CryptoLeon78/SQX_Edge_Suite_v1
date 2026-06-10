# REMOTE-PERSIST1E - SQX Views Workspace Presets

## Summary

REMOTE-PERSIST1E closes the last browser-only persistence gap in the current
remote pilot state: user-created SQX Views presets now travel with the active
server-derived workspace instead of living only in the browser cache.

SQX Views still keeps `localStorage` as a compatibility cache for local/offline
use, but remote mode treats `<workspace>/config/workspace_state.sqlite` as the
source of truth through `remote-workspace-state-v1`.

## Scope

Persisted key:

- `sqx_view_creator_presets_v1`

Existing keys kept in the same workspace state store:

- `sqx_plan_user_v1`
- `sqx_pipeline_state_v1`
- `sqx_strategies_user_v1`
- `sqx_strategies_deleted_v1`

## Runtime Flow

1. Remote bootstrap calls `GET /api/remote/state/bootstrap`.
2. The backend reads `workspace_state.sqlite` from the authenticated workspace.
3. `app/js/modules/remote-state.js` writes allowed keys into browser
   `localStorage` as a compatibility cache.
4. `app/js/modules/view-creator.js` renders SQX Views presets from
   `sqx_view_creator_presets_v1`.
5. When the user saves, imports or deletes SQX Views presets,
   `setSavedPresets()` writes local cache and triggers a remote save with source
   `sqx-views-presets`.
6. Remote save calls `POST /api/remote/state/save`, which persists the key only
   inside the active workspace.

## Traceability

- Version: `remote-workspace-state-v1`
- Backend owner: `backend/sqx-edge-tool/core/remote_workspace_state.py`
- Frontend owner: `app/js/modules/remote-state.js`
- SQX Views owner: `app/js/modules/view-creator.js`
- SQLite file: `<workspace>/config/workspace_state.sqlite`
- Audit event: `remote_workspace_state_write`
- Save source: `sqx-views-presets`

## Security And Privacy

- Browser payloads cannot select workspace ids or local paths.
- Backend allowlist ignores non-dashboard keys such as license state.
- Public responses do not return raw emails or Windows paths.
- Presets are stored per authenticated workspace, not globally.
- `localStorage` remains a local compatibility cache only.

## Acceptance

- Two remote identities keep separate SQX Views preset lists.
- A saved SQX Views preset is restored after browser reload on the same
  authenticated workspace.
- Control Panel remote backups now include SQX Views presets through the same
  allowed key list.
- Multi-user expansion is no longer blocked by the former SQX Views/user preset
  persistence gap; REMOTE-8C observation and support gates still apply.
