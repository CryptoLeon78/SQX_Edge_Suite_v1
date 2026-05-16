# REMOTE-2B - Tester Grants And Repository Privacy

## Summary

REMOTE-2B locks two product/security decisions before REMOTE-3 auth and payment work:

1. Approved testers keep complete app access without payment, but they authenticate through the same remote-service identity path as paid users.
2. The working repositories should be private before commercial rollout because the product is moving from open artifact delivery to paid web access.

This phase is documentation and governance only. It does not create tester accounts, send emails, change GitHub visibility or alter runtime behavior.

## Tester Free Access Decision

The current approved tester cohort remains eligible for full access as `tester_free` users:

- Auth is still required.
- Email validation is still required.
- Access is complete, equivalent to Pro feature access.
- Payment is not required for the tester entitlement.
- Tester access is granted by an operator-controlled key or grant record.
- The model must remain open to adding more testers later.

REMOTE-3 must therefore model entitlement as more than "paid or not paid":

```text
entitlement_kind = paid_subscription | tester_free | internal_operator
entitlement_status = active | pending | expired | denied | blocked
feature_scope = full | restricted
```

The tester list, real emails, grant keys, invitation messages and renewal evidence remain private and ignored by Git. Public docs may describe the model, but not the identities.

## Tester Grant Requirements For REMOTE-3

REMOTE-3 auth/webhook work must include:

- a first-class `tester_free` grant path;
- a way to activate/deactivate a tester without payment webhook;
- audit events for grant creation, login, renewal, denial and block;
- clear separation between `tester_free` and `paid_subscription`;
- no hardcoded tester emails in tracked code or docs;
- no feature downgrade for approved testers unless the operator explicitly changes their grant.

The commercial UI can label testers as "Tester Free" or "Tester Pro Pilot", but they should experience the same core product capabilities as paid users while the grant is active.

## Repository Privacy Decision

Recommended commercial posture:

- Make `CryptoLeon78/SQX_Edge_Suite_v1` private before active sales.
- Make `CryptoLeon78/SQX_Institutional_Core` private before active sales.
- Keep the existing commercial-private repository private.

Rationale:

- The product value is now the hosted methodology, tooling, source manifests, workflows and generated-service operation.
- A public repo no longer supports the distribution model.
- Private repos simplify future security, pricing, anti-copying and buyer positioning.
- Public source visibility can reduce perceived product exclusivity before launch.

Important limitation: making a repository private does not erase anything previously cloned or cached. It reduces future exposure, but it is not a substitute for secret scanning, history review or never committing private evidence.

## Manual Operator Action

The operator may switch repo visibility in GitHub UI:

1. Open the repository settings.
2. Confirm branch/protection expectations.
3. Change visibility to private.
4. Repeat for the institutional repository.
5. Tell Codex after the change so governance, README and tests can be updated from "recommended" to "done".

Codex must not assume the change occurred until verified by the operator or by an authenticated GitHub check.

## GO / NO-GO

GO to REMOTE-3 when:

- Tester-free entitlement is documented as a required auth contract.
- Repo privacy is recorded as recommended before launch or verified as complete.
- No tester identities, grant keys, private URLs or provider IDs are committed.

NO-GO for launch when:

- Auth only supports paid users and cannot grant tester-free access.
- A tester can access without authentication.
- Tester grants are hardcoded in frontend code.
- Public repo visibility remains accepted as final commercial posture without explicit operator decision.

