# REMOTE-PERSIST1A - Workspace State Persistence

## Purpose

REMOTE-PERSIST1A is the first real persistence layer for multi-user remote use.
The browser can still use `localStorage`/IndexedDB as a local cache, but the
source of truth for remote users starts moving to the server-derived workspace.

This phase covers the first two critical mutable surfaces:

- Plan Mining: `sqx_plan_user_v1`
- Mining pipeline state: `sqx_pipeline_state_v1`
- Strategy Control imported/hidden strategies:
  - `sqx_strategies_user_v1`
  - `sqx_strategies_deleted_v1`

## Storage Model

Each authenticated user receives a workspace derived from the active app-session
identity hash. The workspace owns a private SQLite database:

`<workspace>/config/workspace_state.sqlite`

The path is never returned to the browser. Public responses may include the
workspace id and the list of persisted keys, but not local paths, raw email,
tokens, cookies or provider identifiers.

## Backend Contract

- `remote-workspace-state-v1`
- `GET /api/remote/state/bootstrap`
  - requires active app session and trusted access context;
  - provisions the workspace;
  - returns the allowed persisted state keys for that workspace.
- `POST /api/remote/state/save`
  - requires active app session and trusted access context;
  - ignores browser-supplied workspace ids/paths;
  - persists only allowed dashboard keys;
  - writes a workspace audit event.
- `GET /api/remote/state/status`
  - reports public-safe persistence readiness.

## Frontend Contract

`app/js/modules/remote-state.js` acts as a compatibility bridge:

- local/offline mode keeps using `localStorage`;
- remote mode bootstraps state from the active workspace;
- allowed `SQX.storage.setJson(...)` writes are queued back to the workspace;
- loaded remote state emits `sqx:remote-state-loaded`, allowing the dashboard to
  refresh Plan Mining, pipeline state and Strategy Control without a manual reload.

## Explicit Non-Scope

This phase does not yet migrate:

- Template Maker IndexedDB (`SQXTemplateMakerDB`) was later migrated by
  REMOTE-PERSIST1C;
- SQX Views custom presets;
- Control Panel state backups, later migrated by REMOTE-PERSIST1D;
- full per-workspace disaster-recovery archive UI.

REMOTE-PERSIST1B later moved Project Generator generated `.cfx` output paths to
workspace outputs. REMOTE-PERSIST1C later moved Template Maker state to
per-workspace `template_maker.sqlite`. REMOTE-PERSIST1D later moved Control
Panel snapshots to per-workspace `state_backups`. The remaining items are still
required before expanding beyond the current controlled pilot.

## Acceptance

- Two identities must receive different workspace ids and different SQLite files.
- A second identity must not see the first identity's Plan Mining or Strategy Control state.
- Remote responses must not include local paths or raw emails.
- Multi-user expansion remains blocked until SQX Views/user presets receive a final remote persistence decision.
