# REMOTE-3C - Paid Webhook And Protected Write Pilot

## Decision

REMOTE-3C connects the commercial access model to runtime entitlement state. The phase adds a signed payment webhook that can activate, renew, cancel, expire or block `paid_subscription` grants, and a minimal protected write endpoint that proves app-session enforcement before REMOTE-4 workspace isolation.

This is still a pilot gate. It does not open arbitrary dashboard mutations, does not generate `.cfx` remotely and does not accept browser-selected local paths or workspace ids.

## Runtime Artifacts

- `backend/sqx-edge-tool/core/remote_payments.py`
- `POST /api/remote/payment/webhook`
- `POST /api/remote/protected/write-pilot`
- `remote-payment-webhook-v1`
- `remote-write-pilot-v1`
- private env var `SQX_REMOTE_PAYMENT_WEBHOOK_SECRET`
- ignored audit file `.local/remote_service/remote_payment_webhook_events.local.jsonl`
- ignored audit file `.local/remote_service/remote_write_pilot.local.jsonl`

## Payment Webhook Contract

Endpoint:

```text
POST /api/remote/payment/webhook
```

Accepted signature headers:

- `X-SQX-Webhook-Signature`
- `X-Hub-Signature-256`
- `X-Signature`

The signature value may be plain SHA-256 HMAC hex or `sha256=<hex>`. The HMAC input is the exact raw request body and the private secret is `SQX_REMOTE_PAYMENT_WEBHOOK_SECRET`. The secret must stay outside Git and must be at least 32 characters.

Supported first-party fields:

- `eventId` or `event_id`
- `eventType` or `event_type`
- `email`, `customerEmail` or `customer_email`
- `subscriptionId` or `subscription_id`
- `customerId` or `customer_id`
- `expiresAt` or `expires_at`
- `featureScope` or `feature_scope`

Supported event types:

- Active: `subscription_activated`, `subscription_created`, `subscription_renewed`, `subscription_resumed`, `order_paid`
- Cancelled: `subscription_cancelled`, `subscription_canceled`
- Expired: `subscription_expired`
- Blocked: `subscription_refunded`, `subscription_chargeback`, `subscription_blocked`

Provider-shaped payloads are normalized defensively when they contain equivalent nested fields, but provider-specific verification remains a later provider-adapter phase. REMOTE-3C only establishes the first-party signed intake and entitlement mutation contract.

## Entitlement Mutation

The webhook writes only to the local entitlement store selected by `SQX_REMOTE_ENTITLEMENTS_PATH`, or to the ignored default `.local/remote_service/remote_entitlements.local.json`.

Rules:

- upsert one `paid_subscription` grant by `emailHash`;
- never write raw buyer email into the entitlement grant;
- store only redacted identity in responses and audit events;
- keep `processedWebhookEvents` for idempotency;
- repeated event ids return `idempotent: true` and do not duplicate grants;
- cancellation, expiration or blocked events set the grant status so access fails on the next session/access check.

## Protected Write Pilot

Endpoint:

```text
POST /api/remote/protected/write-pilot
```

This endpoint requires the `__Host-sqx_remote_session` cookie created by REMOTE-3B. It calls `evaluate_remote_session()` and writes only a small audit event to `.local/remote_service/remote_write_pilot.local.jsonl`.

It proves:

- the app session is required for a write;
- active entitlement is revalidated before mutation;
- the JSON response never returns the session token, raw email or private store path;
- server-side audit can record a redacted identity hash and entitlement kind.

It intentionally does not mutate project state. Real user workspaces and generated artifacts start in REMOTE-4.

## Privacy And Security Boundaries

- No raw payment secret is returned.
- No raw buyer email is returned.
- No private provider payload is committed.
- No checkout provider token is stored in Git.
- No direct public backend exposure is introduced; the service remains behind Cloudflare Tunnel and Access.
- No browser payload may choose a local path, workspace id or SQX resource.

## Manual Smoke

Use a private local secret and local entitlement path:

```powershell
$env:SQX_REMOTE_PAYMENT_WEBHOOK_SECRET = "<private 32+ char secret>"
$env:SQX_REMOTE_ENTITLEMENTS_PATH = "<private ignored remote entitlements path>"
```

Generate a signed test body from the same bytes that will be posted. In production, the payment provider adapter must sign the raw body with the private secret before calling the webhook.

Expected result:

- valid active event creates/renews `paid_subscription`;
- repeated event is idempotent;
- cancelled event blocks the paid session on revalidation;
- protected write pilot returns `403` without app session and `200` with a valid session.

## Not Yet Implemented

- Provider-specific Stripe/Lemon signature adapter.
- Paid checkout UI.
- Workspace derivation and per-user file isolation.
- Global protection of every mutating endpoint.
- Remote `.cfx` generation for paid users.

Those move to REMOTE-4+ after this entitlement and session gate is stable.
