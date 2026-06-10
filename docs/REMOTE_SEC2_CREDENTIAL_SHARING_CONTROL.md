# REMOTE-SEC2 - Credential Sharing Control

## Decision

SQX Edge Suite now treats credential sharing as a first-class remote security risk. Cloudflare Access remains the external identity gate, but the app adds `remote-access-control-v1` as a strict local control for approved device/IP/browser contexts before a remote workspace can be opened.

## Policy

- Mode: strict.
- Default limit: 2 trusted contexts per identity.
- A context is derived from hashed identity, server-issued device cookie `__Host-sqx_device_id`, Cloudflare client IP signal, country and browser fingerprint signal.
- The IP is a security signal, not the only identity proof.
- A third context is held as pending and must be approved by the operator.
- A revoked or blocked context cannot create or use a remote session.
- A session is bound to the context that created it; copied sessions or copied cookies from another context are blocked.
- Recent simultaneous sessions from different contexts are blocked as suspicious.
- `internal_operator` identities use a separate owner context limit through REMOTE-OWNER1; the normal tester/buyer default remains 2.

## Privacy Rules

- Raw emails, raw IPs, raw user agents, cookies, tokens, protected URLs and local paths are never stored in the access-control store.
- The device cookie is server-issued, `HttpOnly`, `Secure`, `SameSite=Lax` and only identifies a browser context. It is not an access token.
- Evidence is local-only under `.local/remote_service/` and ignored by Git.

## Operator Flow

1. User passes Cloudflare Access with an approved email.
2. SQX Edge Suite evaluates the local context.
3. If the context is within the first two trusted contexts, it is trusted automatically.
4. If the context is over the limit, revoked, mismatched or suspicious, the Welcome gate shows a validation message and `Solicitar aprobacion`.
5. The request creates a redacted support case.
6. The operator reviews `tools/remote_access_control_status.ps1` and approves or revokes with `tools/remote_access_control_admin.ps1`.

## Runtime Artifacts

- `backend/sqx-edge-tool/core/remote_access_control.py`
- `GET /api/remote/access-control/status`
- `POST /api/remote/access-control/request-approval`
- `tools/remote_access_control_status.ps1`
- `tools/remote_access_control_admin.ps1`
- `.local/remote_service/remote_access_control.local.json`
- `.local/remote_service/remote_access_events.local.jsonl`
- `docs/REMOTE_OWNER1_OWNER_ACCESS_RECOVERY.md` for owner-only recovery on top of this control.

## Acceptance

- A valid user can enter from up to 2 trusted contexts.
- A third context creates a pending/blocked state and cannot open the dashboard until approved.
- A session copied to another context is rejected by context mismatch.
- A recent concurrent login from a different context is rejected.
- Public responses and tracked files do not leak raw identity, IP, device, tokens or local paths.
