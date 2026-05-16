# REMOTE-6 - Security And Abuse Controls

REMOTE-6 adds the first operational security layer around the remote Pro service. It does not expose new commercial features; it makes the existing remote auth, session and workspace gates harder to abuse before the pilot grows.

## Scope

- Version: `remote-security-v1`.
- Policy file: private local `SQX_REMOTE_SECURITY_POLICY_PATH`, defaulting to ignored `.local/remote_service/remote_security.local.json`.
- Backend owner: `backend/sqx-edge-tool/core/remote_security.py`.
- Protected surface: every `/api/remote/*` endpoint.
- User-facing surface: Home `remote-pro-panel` security item plus low-opacity session watermark.

## Controls

### Rate limits

`check_remote_rate_limit()` applies per-subject, per-action windows before remote endpoints run. The current action map is:

- `remote_status`: read-only remote status endpoints.
- `remote_session_login`: session login.
- `remote_session_logout`: session logout.
- `remote_payment_webhook`: payment webhook.
- `remote_protected_write`: protected remote write endpoints.

Responses never return the raw subject, email, session token or local paths. Rate limited requests return HTTP `429` with `Retry-After`.

### Kill switch

The local security policy can set:

```json
{
  "killSwitch": {
    "active": true,
    "reason": "operator_controlled_pause"
  }
}
```

When active, login and protected writes return HTTP `503` with `remote_kill_switch_active`. Read-only status stays available so the operator can see the incident posture.

### Revocation and blocking

The policy supports:

- `revokedSessionIds`: session ids to invalidate.
- `blockedIdentityHashes`: SHA-256 email hashes to block without storing raw emails.

`evaluate_remote_session()` enforces both before entitlement access is accepted. Runtime code must never hardcode tester emails, paid users, grant keys or raw identities.

### Watermark

The public status endpoint returns a safe watermark model:

- enabled flag;
- short label;
- redacted marker from the app session or workspace id.

The dashboard renders `remote-session-watermark` only when the remote status says it is enabled. This is a deterrent and traceability hint, not a DRM guarantee.

### Redacted audit visibility

`GET /api/remote/security/audit/recent` returns recent workspace audit events for the active remote session. Events are redacted:

- no local workspace paths;
- no raw emails;
- no session tokens;
- identity hash is shortened to a reference only.

## Endpoints

- `GET /api/remote/security/status`: public-safe readiness and current security posture.
- `GET /api/remote/security/audit/recent`: active-session recent audit view, redacted and workspace-bound.

All `/api/remote/*` responses include `X-SQX-Remote-Security-Version: remote-security-v1`.

## Policy Shape

Private local example:

```json
{
  "schemaVersion": "remote-security-v1",
  "killSwitch": { "active": false, "reason": "operator_controlled_pause" },
  "blockedIdentityHashes": [],
  "revokedSessionIds": [],
  "rateLimits": {
    "remote_status": { "limit": 180, "windowSeconds": 60 },
    "remote_session_login": { "limit": 10, "windowSeconds": 60 },
    "remote_session_logout": { "limit": 30, "windowSeconds": 60 },
    "remote_payment_webhook": { "limit": 90, "windowSeconds": 60 },
    "remote_protected_write": { "limit": 30, "windowSeconds": 60 }
  },
  "watermark": { "enabled": true, "label": "SQX REMOTE PRO" },
  "audit": { "recentEventsLimit": 20 }
}
```

Do not commit the real local policy. Store it under `.local/remote_service/` or another ignored private path.

## Abuse Response Runbook

1. Activate `killSwitch.active=true` if a remote incident is suspected.
2. Add compromised session ids to `revokedSessionIds`.
3. Add abusive identity hashes to `blockedIdentityHashes`.
4. Review `GET /api/remote/security/audit/recent` from the affected account and the private workspace logs.
5. Rotate `SQX_REMOTE_SESSION_SECRET` only if session signing is suspected compromised; this invalidates active sessions.
6. Keep Cloudflare Access and Tunnel logs private; never paste provider ids, URLs, tokens or raw emails into Git.
7. Reopen login/protected writes only after the workspace and entitlement state are verified.

## Out Of Scope

- Full migration of every existing dashboard mutation behind remote workspace gates.
- Per-user billing UI.
- Cloudflare WAF automation.
- Advanced anomaly detection.

Those belong to REMOTE-7 and later pilot-hardening phases.
