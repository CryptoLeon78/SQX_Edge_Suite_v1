# REMOTE-3A - Remote Access Foundation

## Summary

REMOTE-3A starts the real REMOTE-3 implementation without turning on global blocking yet. It adds the backend access model that all later login, session and webhook work must use.

The first-class entitlement kinds are:

- `paid_subscription`: paid monthly/annual users activated by future signed payment webhook.
- `tester_free`: approved testers with full feature access, no payment, authenticated and revocable.
- `internal_operator`: operator/admin access for controlled local operations.

## Repository Privacy Evidence

The operator changed both working repositories to private before this phase continued.

Verified locally with GitHub CLI:

```text
CryptoLeon78/SQX_Edge_Suite_v1 -> PRIVATE
CryptoLeon78/SQX_Institutional_Core -> PRIVATE
```

This verification does not weaken secret discipline. Private repos still must not receive tester emails, grant keys, provider IDs, private URLs, tokens or payment payloads.

## Added Runtime Foundation

- `backend/sqx-edge-tool/core/remote_access.py`
- `GET /api/remote/access/status`
- `backend/sqx-edge-tool/test_remote_access.py`
- `docs/examples/remote_entitlements.local.example.json`

The entitlement store is local-only and ignored:

```text
.local/remote_service/remote_entitlements.local.json
```

The public example contains only placeholders. The real file may contain emails or hashes, tester grant hashes and provider references, so it must stay outside Git.

## Access Model

Remote access evaluation now separates:

- identity from Cloudflare Access or future app session headers;
- entitlement kind and status;
- feature scope;
- audit event shape;
- privacy boundaries.

The status response is public-safe:

- returns redacted email references only;
- returns email hashes for traceability;
- never returns grant keys;
- never returns the entitlement store path;
- never returns payment payloads.

## Tester Free Contract

Approved testers are not "free users". They are full-access `tester_free` users:

- same authentication path as paid users;
- same full feature scope while active;
- no payment requirement;
- revocable by operator;
- future grant key supported through `grantKeyHash`;
- no tester identities in tracked files.

## Endpoint Contract

`GET /api/remote/access/status` reads trusted edge/app identity headers and returns:

- `version = remote-access-v1`
- `schemaVersion = remote-entitlements-v1`
- `identity.email_ref`
- `identity.email_hash`
- `auth_layers`
- `entitlement`
- `access`
- `audit_event`
- `privacy`

This endpoint is not the final login session. REMOTE-3B must add app sessions, signed cookies or equivalent session enforcement before mutating endpoints become remote-user-facing.

## Handoff To REMOTE-3B

Next recommended phase:

- add app session login/verification around the access foundation;
- support tester grant key verification without returning the key;
- keep payment webhook activation separate and signed;
- start protecting selected write endpoints only after session and workspace boundaries exist.

