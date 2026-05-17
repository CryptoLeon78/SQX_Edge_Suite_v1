# REMOTE-PERSIST1B - Workspace Outputs For Project Generator

## Purpose

REMOTE-PERSIST1B moves Project Generator `.cfx` artifacts into the active
remote workspace. A remote user must never generate into the shared configured
`output_dir`, and a remote response must not expose the operator laptop path.

This closes the second major multi-user persistence gap after
REMOTE-PERSIST1A.

## Storage Model

Generated files now live under the server-derived workspace:

`<workspace>/outputs/*.cfx`

The physical path is local-only. Browser/API responses use:

`workspace://outputs`

and per-file URIs such as:

`workspace://outputs/Custom_EURUSD_H1_Capa1.cfx`

## Backend Contract

- `remote-workspace-output-v1`
- `GET /api/output`
  - local mode: keeps listing configured `output_dir`;
  - remote mode with valid app session: lists only the active workspace outputs;
  - remote mode without app session: returns `remote_session_required`;
  - public response returns no local filesystem paths.
- `POST /api/generate`
- `POST /api/generate-custom`
- `POST /api/generate-all`
  - local mode: keeps the configured/custom output behavior;
  - remote mode: ignores global config output and writes to workspace outputs;
  - remote body field `output` is blocked with `remote_output_override_blocked`;
  - each generated file writes a workspace audit event.
- `POST /api/open-folder`
  - local mode: keeps opening allowed local folders;
  - remote mode: blocked because users must not open server folders.

## Privacy And Traceability

Remote responses include:

- workspace id/ref only through `public_workspace_context`;
- output scope `remote_workspace`;
- `privacy.local_paths_returned = false`;
- generated filename and `workspace://` URI;
- audit event type `remote_workspace_output_generated`.

Remote responses must not include:

- configured `output_dir`;
- absolute Windows paths;
- raw email;
- cookies, tokens or Cloudflare ids.

## Explicit Non-Scope

This phase did not yet migrate:

- Template Maker IndexedDB (`SQXTemplateMakerDB`), later migrated by
  REMOTE-PERSIST1C;
- SQX Views custom presets;
- Control Panel backup/restore;
- browser-side generated-output reset history beyond the existing compatibility cache.

The remaining persistence gaps remain blockers before expanding beyond the
current controlled pilot.

## Acceptance

- Two remote identities must receive separate output folders.
- One user's `/api/output` must not list another user's `.cfx`.
- A remote `output` override must be rejected.
- Remote Project Generator endpoints must require a valid app session.
- Local Project Generator behavior must remain compatible.
