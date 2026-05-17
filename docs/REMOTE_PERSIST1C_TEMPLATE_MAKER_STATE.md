# REMOTE-PERSIST1C - Template Maker Workspace State

## Purpose

REMOTE-PERSIST1C moves Template Maker runtime state into the active
server-derived workspace. A remote user must not depend on browser-only
IndexedDB for loaded CSV/SQX records, certification status, diversity settings
or C2 readiness.

This closes the Template Maker multi-user persistence gap left after
REMOTE-PERSIST1A and REMOTE-PERSIST1B.

## Storage Model

Template Maker state is stored as one normalized snapshot inside the active
workspace:

`<workspace>/config/template_maker.sqlite`

The SQLite database stores a single key:

`template_maker_snapshot`

The public contract version is:

`remote-template-maker-state-v1`

The browser keeps IndexedDB only as a compatibility cache. In remote mode, the
workspace snapshot is the source of truth and replaces stale browser cache on
bootstrap, including an empty workspace snapshot.

## Backend Contract

- `GET /api/remote/template-maker/bootstrap`
  - requires an active remote app session and trusted access context;
  - derives the workspace from the active session identity;
  - returns the Template Maker snapshot and no local filesystem paths;
  - writes a workspace audit event `remote_template_maker_state_read`.
- `POST /api/remote/template-maker/save`
  - requires an active remote app session and trusted access context;
  - accepts `state` plus a source label;
  - writes the normalized snapshot to `template_maker.sqlite`;
  - writes a workspace audit event `remote_template_maker_state_write`.
- `GET /api/remote/template-maker/status`
  - requires an active remote app session;
  - returns record count, public workspace context, storage mode and database
    name only.

Public responses must not include absolute Windows paths, raw email, cookies,
tokens, Cloudflare identifiers, private URLs or local workspace roots.

## Frontend Contract

`app/js/modules/template-maker.js` exposes:

- `buildRemoteSnapshot()`
- `applyRemoteSnapshot(snapshot)`
- `bootstrapRemoteState()`
- `saveRemoteState(source)`
- `getRemotePersistenceStatus()`

The module keeps local/offline behavior unchanged:

- without `fetch`, it stays local-only;
- if remote endpoints return session/access errors, it keeps IndexedDB mode;
- remote save failures are recorded in UI state but do not break the local
  workflow.

When remote bootstrap succeeds:

- the workspace snapshot hydrates strategies and config;
- the hydrated state is mirrored into IndexedDB as cache;
- subsequent strategy/config mutations autosave back to the workspace.

## Snapshot Fields

- `schemaVersion`: `remote-template-maker-state-v1`
- `templateMakerSchemaVersion`: current Template Maker metric contract
- `strategies`: normalized Template Maker records
- `config.currentCapa`
- `config.currentPreset`
- `config.thresholds`
- `config.diversitySettings`
- `metadata.source`
- `metadata.recordCount`
- `metadata.updatedAt`

## Explicit Non-Scope

This phase does not migrate:

- raw uploaded CSV/SQX files as separate server files;
- SQX Views user presets;
- Control Panel backup/restore, later migrated by REMOTE-PERSIST1D;
- cross-device conflict resolution beyond last accepted snapshot.

SQX Views/user presets remain a separate persistence decision before broad
multi-user expansion.

## Acceptance

- Two remote identities must receive separate Template Maker state.
- A second identity must not see the first identity's loaded strategies.
- Remote bootstrap of an empty workspace must clear stale browser cache.
- Remote responses must not return local paths or raw identity values.
- Local Template Maker behavior must remain compatible without remote session.
