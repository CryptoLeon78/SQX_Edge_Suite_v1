# T10at Private Tester URL Share Approval Gate

## Objective

T10at prepares the private approval gate for sharing the protected tester URL after T10as, without committing the tester URL, tester emails, passwords, hostnames, account IDs, Access IDs, tokens or private support-channel details.

This phase does not create tester accounts, does not send invitations, does not publish the tester URL, does not rotate passwords and does not run a Cloudflare deployment.

## Approval Boundary

The tester URL may only be shared outside Git after all checks below are true:

- T10as evidence ingest is safe and returns `GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_SAFE_NO_GIT_LEAK`.
- Cloudflare Access still blocks anonymous traffic before the app body is visible.
- App login/session protection still applies after Cloudflare Access.
- Tester accounts are already activated privately.
- Password delivery, support and revocation paths are prepared privately.
- The 15-day renewal cadence is ready before access is shared.
- The URL will be sent through a private one-to-one channel only.
- No URL, hostname, tester email, password, token, API key, Access ID, account ID, deployment ID or version ID is committed.

## Private Local Approval File

If the operator needs to record readiness, create this ignored file only:

```text
templates/SQX_Edge_Tester_Portal/tester-url-share-approval.local.json
```

It may contain public-safe booleans and small counts only. It must not contain:

- Tester emails, names, passwords, reset links or access codes.
- URL, hostname, domain, route or workers.dev address.
- Account IDs, Access IDs, deployment IDs, version IDs or policy IDs.
- Tokens, API keys, private keys, cookies or session values.
- Chat, support, distribution or meeting links.

## Accepted Fields

The evidence file may use only these fields:

- `phase`: `T10at`.
- Boolean checks: `t10asActivationEvidenceGo`, `accessStillInterceptsAnonymous`, `appSessionStillRequiredAfterAccess`, `privateTesterAccountsActivated`, `passwordDeliveryChannelPrivate`, `supportChannelReadyPrivately`, `revocationPathReadyPrivately`, `renewalCadenceScheduled`, `privateOneToOneShareChannelReady`, `testerUrlSharedPrivately`, `publicRepoContainsTesterEmails`, `publicRepoContainsTesterUrl`, `publicRepoContainsCredentials`, `publicRepoContainsProviderIds`.
- Count checks: `approvedTesterCount`, `pendingTesterCount`, `urlRecipientsCount`.

Counts must be non-negative integers no greater than 50.

## Expected Results

Without the ignored local approval file, the expected guarded result is:

```text
NO_GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_MISSING
```

With safe local approval evidence and no public leak, the expected result is:

```text
GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_READY_NO_GIT_LEAK
```

Unsafe evidence must fail closed and stop the phase.

## Operator Meaning

`GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_READY_NO_GIT_LEAK` means the operator can share the protected tester URL privately. It does not publish the URL, does not email testers automatically and does not authorize public release.

## Next Gate

```text
T10au_private_first_tester_smoke_gate
```
