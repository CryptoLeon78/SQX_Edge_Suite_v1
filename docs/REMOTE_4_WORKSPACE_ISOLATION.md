# REMOTE-4 - Workspace Isolation Foundation

## Decision

REMOTE-4 introduces the first server-derived workspace boundary. A workspace is derived from the signed app session identity hash and active entitlement. The browser cannot choose `workspace_id`, local paths, output folders or SQX internals.

This phase creates the isolation foundation and moves the protected write pilot into a per-workspace audit log. It still does not migrate all existing dashboard mutations or `.cfx` generation; those will be moved behind the same gate in later REMOTE-4 subphases and REMOTE-5.

## Runtime Artifacts

- `backend/sqx-edge-tool/core/remote_workspaces.py`
- `remote-workspace-v1`
- private env var `SQX_REMOTE_WORKSPACES_ROOT`
- `GET /api/remote/workspace/status`
- workspace-aware `POST /api/remote/protected/write-pilot`
- ignored workspace root `.local/remote_service/workspaces/`
- ignored per-workspace audit file `logs/audit.local.jsonl`

## Workspace Derivation

Workspace id:

```text
ws_<first 24 chars of sha256(normalized email)>
```

Rules:

- source of truth is the already validated `__Host-sqx_remote_session` cookie;
- `email_hash` must be a 64-character SHA-256 hex string;
- workspace root defaults to `.local/remote_service/workspaces/`;
- `SQX_REMOTE_WORKSPACES_ROOT` may redirect the root privately for operations/tests;
- every resolved path must stay inside the configured workspace root;
- public JSON never returns local paths.

## Workspace Layout

Every workspace receives this server-managed layout:

```text
workspace/
  config/
  uploads/
  outputs/
  exports/
  logs/
  tmp/
  workspace_manifest.local.json
```

The manifest stores only redacted identity and hashes:

- `workspaceId`
- `ownerHash`
- `ownerRef`
- `entitlementKind`
- `featureScope`
- `layout`
- `createdAt`
- `updatedAt`
- privacy flags

Raw buyer emails, local absolute paths, secrets and checkout payloads are not written to the manifest.

## API Contract

### `GET /api/remote/workspace/status`

Requires an active app session and entitlement. It creates the workspace if missing and returns only:

- workspace id;
- owner hash/ref;
- entitlement kind;
- feature scope;
- logical layout;
- `paths.mode = server_managed`;
- `local_paths_returned = false`.

Without a valid session, it returns `403` with redacted session/access status.

### `POST /api/remote/protected/write-pilot`

The REMOTE-3C write pilot now runs through REMOTE-4 workspace derivation:

- validates app session;
- derives workspace server-side;
- ignores browser-supplied `workspace_id`, `workspaceId` or `path`;
- writes audit into the active workspace `logs/audit.local.jsonl`;
- returns workspace id and audit metadata without returning local paths.

## Not Yet Migrated

These remain future work:

- `/api/generate`
- `/api/generate-custom`
- `/api/generate-all`
- uploads/imports/exports from dashboard tabs;
- user-visible workspace selector/status in the frontend;
- cleanup/backup/restore per workspace;
- rate limits and kill switch per workspace.

## Acceptance Criteria

- Two different session identities produce different workspace ids.
- A missing or invalid session cannot create a workspace.
- Browser-supplied workspace ids and paths are ignored.
- Per-workspace audit exists after a protected write pilot.
- Public API responses never include absolute local paths or raw buyer emails.

## Manual Smoke

```powershell
$env:SQX_REMOTE_SESSION_SECRET = "<private 32+ char secret>"
$env:SQX_REMOTE_ENTITLEMENTS_PATH = "<private ignored remote entitlements path>"
$env:SQX_REMOTE_WORKSPACES_ROOT = "<private ignored remote workspaces root>"
```

Then:

1. Create an app session through REMOTE-3B login.
2. Call `GET /api/remote/workspace/status`.
3. Call `POST /api/remote/protected/write-pilot` with any browser `workspace_id` value.
4. Confirm the response returns the server-derived workspace id only.
5. Confirm the audit line exists under that workspace.

## Security Notes

- The workspace id is not a password or token; it is a stable server-side routing key.
- The entitlement check still controls access.
- The workspace root is ignored by Git and must be included in private backup/restore operations before expanding testers.
