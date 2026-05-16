# REMOTE-7 - Web Pro Monetization Rewrite

## Summary

REMOTE-7 locks the commercial story around SQX Edge as a web Pro service, not as a user-installed portable package. Buyers receive authenticated browser access, monthly or annual subscription entitlement, isolated workspace and optional support. The Windows laptop pilot, Cloudflare Tunnel and Cloudflare Access remain the active delivery path until REMOTE-8 proves the controlled pilot end to end.

This phase changes commercial positioning, onboarding, FAQ and support boundaries. It does not change runtime access code, pricing provider configuration or payment execution.

## Offer Model

| Offer | Internal code | Buyer promise | Notes |
| --- | --- | --- | --- |
| SQX Edge Pro Monthly | `web_pro_monthly` | Protected web access with validated email, active subscription and isolated workspace. | Monthly billing and renewal handled by payment webhook in later commercial flow. |
| SQX Edge Pro Annual | `web_pro_annual` | Same Pro access with annual billing. | Annual plan can include a higher-touch onboarding window if approved privately. |
| Support Assist | `support_assist` | Guided onboarding, configuration review, methodology orientation and issue triage. | Support does not include financial advice or trading execution promises. |
| Template Packs | `template_pack_addon` | Curated methodology packs or templates around SQX Edge. | Add-on sales remain behind the private commercial boundary until safe publication is approved. |
| Approved Tester Access | `tester_free` | Full feature access without payment for approved testers. | Same authentication, workspace isolation, audit and revocation path as paid users. |

## Buyer Flow

1. Buyer chooses monthly or annual Pro access.
2. Checkout records the subscription and sends a signed payment event.
3. The webhook grants or updates `paid_subscription` entitlement.
4. Buyer receives the protected access link through the approved private channel.
5. Cloudflare Access validates the email before the app body is visible.
6. SQX Edge app session validates entitlement, status and security policy.
7. The server derives the workspace; the browser never selects local paths.
8. Buyer uses Workflow, Activos, Mining Control, SQX Views, Project Generator, Template Maker, Strategy Control, Champion vs Challenger and BlockSettings Info through the browser.
9. Generated `.cfx`, `.vw`, C2 templates, imports, exports and logs remain in the server-side workspace.
10. Cancellation, expiration, revocation or blocked status removes access without deleting the audit trail.

## No-Install Buyer Promise

Buyer-facing copy must say:

- The user opens a protected web link.
- The user validates email and app access.
- The user does not install Python.
- The user does not download a ZIP as the primary commercial path.
- The user does not run `START_SQX_EDGE.bat`.
- SQX paths, `data.db`, templates, BlockSettings and outputs are managed on the controlled server side.

Avoid saying "zero risk" or "no risk". Use "controlled, audited and isolated environment".

## Tester Flow

Approved testers remain a first-class access class:

- entitlement kind: `tester_free`;
- full feature access while active;
- same login and session path as paid users;
- operator-managed grant or record;
- redacted audit trail;
- revocation path;
- expandable to more testers only by explicit operator approval.

Tester identities, private grant keys, renewal records and private support evidence stay outside Git.

## FAQ Copy

**Do I need to install anything?**  
No. The commercial path is browser access through a protected link. The server handles SQX Edge runtime resources.

**Do I need Python or local configuration?**  
No. Python, SQX Edge backend, SQX resources and output folders are server-side in the controlled pilot.

**What happens when my subscription expires?**  
Access is blocked by entitlement status. Audit history and workspace data remain controlled by the operator policy until retention rules decide otherwise.

**Can a tester use all features without payment?**  
Yes, if the tester has an active `tester_free` grant. It is still authenticated, audited and revocable.

**Does SQX Edge promise profitable strategies?**  
No. SQX Edge sells productivity, methodology, traceability and error reduction around StrategyQuant X workflows. It does not sell financial results.

**Can I still receive a ZIP?**  
Not as the default commercial path. Portable/ZIP remains an internal fallback for rollback, support diagnostics or explicitly approved exceptional delivery.

## Responsible Notice

SQX Edge Pro does not promise profitability or financial results. The commercial promise is better methodology, traceability, productivity and reduced operational error around StrategyQuant X research.

## Support Scope

Support Assist may include:

- account/access triage;
- workspace readiness checks;
- SQX Edge module orientation;
- Project Generator and Template Maker workflow guidance;
- help interpreting app validation messages;
- support-case bundles with redacted evidence.

Support Assist must not include:

- financial advice;
- guarantee of profitability;
- trading execution decisions;
- claims that a strategy is safe to trade live;
- sharing private infrastructure details, tokens, raw emails or local server paths.

## Commercial Boundary

Tracked docs may describe the model, safe claims and public-safe buyer flow. Private docs must hold:

- exact checkout links;
- exact live prices if not approved for tracked docs;
- buyer identities;
- tester identities;
- support logs;
- payment provider payloads;
- entitlement records;
- private grants and grant keys;
- operational URLs and Cloudflare identifiers.

## Product Manifest Contract

`backend/sqx-edge-tool/config/product_manifest.json` may keep legacy offline/license fields for fallback runtime compatibility. REMOTE-7 adds a non-breaking commercial section that declares:

- `primaryChannel = remote_service`;
- `buyerAccessModel = web_pro_subscription`;
- plans `web_pro_monthly` and `web_pro_annual`;
- support add-on `support_assist`;
- tester entitlement `tester_free`;
- portable role `internal_fallback`.

## Acceptance Criteria

- README presents REMOTE-7 as the active commercial state.
- Commercial README no longer instructs the buyer to download a ZIP, double click a launcher or paste an offline license as the primary path.
- Public roadmap shows remote web Pro as the current commercial direction.
- Governance includes `Remote Monetization Rewrite Gate`.
- Remote roadmap points from REMOTE-7 to REMOTE-8 controlled pilot.
- Product manifest contains a remote commercial contract without breaking fallback runtime fields.

## Next REMOTE-8 Scope

REMOTE-8 should prove one controlled user journey:

1. active entitlement exists;
2. login succeeds through Cloudflare Access plus app session;
3. workspace is derived server-side;
4. user generates or exports a real artifact;
5. revocation/cancellation blocks further use;
6. support evidence stays redacted;
7. no workspace leakage appears between users.
