# REMOTE-5 - Remote Pro UX Surface

## Summary

REMOTE-5 makes the remote-service pivot visible inside the dashboard without changing generation behavior yet. The user-facing Home panel now shows Pro access, app session, workspace readiness, server readiness and privacy posture in one place.

The goal is operational clarity for a basic user: they should understand whether their protected link/session is ready, whether their server-managed workspace exists, and whether the SQX server resources are available. They should not see raw Windows paths, secrets, tokens, Cloudflare identifiers, workspace root paths or internal SQX folders.

## Dashboard Surface

The Home tab includes `remote-pro-panel`:

- `remote-pro-access-*`: shows email/session/entitlement status using redacted backend signals.
- `remote-pro-workspace-*`: shows only the server-derived workspace id, shortened for readability.
- `remote-pro-server-*`: shows backend readiness without displaying `sqx_path`, `data.db` path or output directory.
- `remote-pro-privacy-*`: repeats the product promise: no local installation for the user and no public exposure of internal paths or secrets.
- `remote-pro-refresh`: lets the operator/user refresh the status without leaving the dashboard.

## Data Sources

The UI consumes existing public-safe endpoints:

- `GET /api/remote/access/status`
- `GET /api/remote/session/status`
- `GET /api/remote/workspace/status`
- `GET /api/health`

The UI treats failing or unauthenticated calls as expected pending states, not fatal crashes. In local/internal fallback mode the panel says that the remote link will activate email and entitlement validation.

## Redaction Rules

- Do not display `sqx_path`, `output_dir`, `sqx_data_db`, workspace root paths or server local paths.
- Do not display session tokens, grant keys, raw emails, Cloudflare IDs or private URLs.
- Showing a short workspace id such as `ws_abc...` is allowed because it is not a path and helps support traceability.
- Copy must say "controlled, audited and isolated", not "zero risk".

## Implementation

- `app/SQX_Dashboard_v6.html`: adds the `Acceso web Pro` Home panel.
- `app/js/modules/home.js`: owns the remote UX state model, endpoint fetches, redaction-aware rendering and refresh binding.
- `app/js/dashboard.js`: initializes the panel after Home controls are wired.
- `app/css/dashboard.css`: adds the premium status card visual treatment.

## Acceptance

- A user with active session, workspace and backend sees `Remote Pro`.
- A local/internal run sees a calm pending/local state.
- The dashboard never renders raw paths from `/api/health`.
- The panel remains responsive inside the Home side column.

## Next Phase

REMOTE-6 should add abuse/security controls around the now-visible remote service: rate limits, revocation/kill switch, audit views, session-block enforcement, watermark and incident runbooks.
