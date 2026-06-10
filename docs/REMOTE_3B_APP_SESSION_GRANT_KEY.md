# REMOTE-3B - App Session Grant Key Gate

## Summary

REMOTE-3B adds the first app-owned session layer on top of REMOTE-3A entitlements and Cloudflare Access identity.

The goal is not yet to protect every remote mutation globally. The goal is to create the login/session primitive that later phases can reuse before workspaces, payment webhooks and write-endpoint enforcement are enabled.

## Runtime Contract

- Session version: `remote-session-v1`.
- Cookie name: `__Host-sqx_remote_session`.
- Cookie flags: `HttpOnly`, `Secure`, `SameSite=Lax`, `path=/`.
- Secret environment variable: `SQX_REMOTE_SESSION_SECRET`.
- Minimum secret length: 32 characters.
- Entitlement store: `SQX_REMOTE_ENTITLEMENTS_PATH`, defaulting to `.local/remote_service/remote_entitlements.local.json`.

The secret and entitlement store are private local/server configuration. They must never be committed, packaged or printed in user-facing diagnostics.

## Endpoints

- `POST /api/remote/session/login`
  - Reads trusted identity from Cloudflare Access/app gateway headers.
  - Validates active entitlement.
  - For `tester_free`, creates the app session directly after Cloudflare identity plus active entitlement unless the operator explicitly marks the grant as `requireGrantKey`.
  - Legacy/enforced tester keys still verify against `grantKeyHash` when that flag is enabled.
  - Sets `__Host-sqx_remote_session`.
  - Never returns the signed token or grant key in JSON.

- `GET /api/remote/session/status`
  - Validates the signed cookie.
  - Revalidates entitlement state from the store.
  - Returns redacted identity, session status and access reason.
  - Never returns the signed token.

- `POST /api/remote/session/logout`
  - Clears `__Host-sqx_remote_session`.

- `GET /api/remote/access/status`
  - Merges trusted edge identity status with app-session status.
  - Remains a public-safe diagnostic status endpoint, not a global write gate.

## Tester Free Flow

Approved testers can use full functionality without payment only when all conditions are true:

1. Cloudflare Access or the app gateway provides a trusted email identity.
2. The entitlement store contains an active `tester_free` grant for that identity.
3. A valid `remote-session-v1` cookie is issued.
4. If and only if the grant explicitly sets `requireGrantKey`, the submitted key must hash to the stored `grantKeyHash`.

The response exposes `grant_key_returned: false` and `session_token_returned: false` so tests can verify privacy expectations.

## Paid And Internal Users

`paid_subscription` and `internal_operator` entitlements do not require a tester grant key. They still require trusted identity, active entitlement and a signed app session.

## Revocation Behavior

Sessions are stateless and signed, but every status evaluation revalidates the current entitlement store. If a user is blocked, cancelled, expired or removed from the store, the existing cookie stops allowing access at the next evaluation.

## Not Implemented Yet

REMOTE-3B does not yet:

- implement checkout/payment webhooks;
- enforce app sessions on every write endpoint;
- create server-side user workspaces;
- expose admin UI for entitlements;
- store real tester emails or grant keys in Git.

Those are reserved for REMOTE-3C and REMOTE-4.

## Security Notes

- Do not use real tester emails in fixtures or docs.
- Do not commit `remote_entitlements.local.json`.
- Do not commit `SQX_REMOTE_SESSION_SECRET`.
- Use email hashes in examples.
- Treat tester grant keys like passwords.
- Keep Cloudflare Access as the first edge gate; the app session is the second gate.
