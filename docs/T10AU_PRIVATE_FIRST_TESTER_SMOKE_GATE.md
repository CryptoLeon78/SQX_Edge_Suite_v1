# T10au Private First Tester Smoke Gate

## Objective

T10au prepares the private first-tester smoke gate after T10at, without committing the tester URL, tester emails, passwords, hostnames, account IDs, Access IDs, tokens, screenshots or private support-channel details.

This phase does not create tester accounts, does not send invitations, does not publish the tester URL, does not rotate passwords and does not run a Cloudflare deployment.

## Smoke Boundary

The first private tester smoke may only be recorded outside Git after all checks below are true:

- T10at URL-share approval returns `GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_READY_NO_GIT_LEAK`.
- The protected URL was shared through a private one-to-one channel only.
- Cloudflare Access blocks anonymous traffic before the app body is visible.
- Cloudflare Access allows the approved tester identity.
- App login/session protection still applies after Cloudflare Access.
- The tester can reach the portal surface after app login.
- `tester_pro` options are visible for the approved tester.
- Admin/operator-only routes remain blocked for the tester.
- Logout works and clears the app session.
- Support and revocation paths remain ready privately.
- No URL, hostname, tester email, password, token, API key, Access ID, account ID, deployment ID, screenshot or version ID is committed.

## Private Local Smoke File

If the operator needs to record smoke readiness/results, create this ignored file only:

```text
templates/SQX_Edge_Tester_Portal/tester-first-smoke.local.json
```

It may contain public-safe booleans and small counts only. It must not contain:

- Tester emails, names, passwords, reset links or access codes.
- URL, hostname, domain, route or workers.dev address.
- Account IDs, Access IDs, deployment IDs, version IDs or policy IDs.
- Tokens, API keys, private keys, cookies or session values.
- Screenshots, image paths, chat links, support links, distribution links or meeting links.

## Accepted Fields

The evidence file may use only these fields:

- `phase`: `T10au`.
- Boolean checks: `t10atUrlShareApprovalGo`, `privateUrlSharedWithSingleTester`, `accessBlocksAnonymous`, `accessAllowsApprovedTester`, `appLoginRequiredAfterAccess`, `appPortalLoadsForTester`, `testerProEntitlementsVisible`, `adminRoutesBlockedForTester`, `logoutClearsSession`, `supportChannelReadyPrivately`, `revocationPathReadyPrivately`, `testerSmokeCompletedPrivately`, `publicRepoContainsTesterEmails`, `publicRepoContainsTesterUrl`, `publicRepoContainsCredentials`, `publicRepoContainsProviderIds`, `publicRepoContainsScreenshots`.
- Count checks: `smokedTesterCount`, `failedCheckCount`.

Counts must be non-negative integers no greater than 50.

## Expected Results

Without the ignored local smoke file, the expected guarded result is:

```text
NO_GO_PRIVATE_FIRST_TESTER_SMOKE_EVIDENCE_MISSING
```

With safe local smoke evidence and no public leak, the expected result is:

```text
GO_PRIVATE_FIRST_TESTER_SMOKE_PASSED_NO_GIT_LEAK
```

Unsafe evidence must fail closed and stop the phase.

## Operator Meaning

`GO_PRIVATE_FIRST_TESTER_SMOKE_PASSED_NO_GIT_LEAK` means one private tester path was smoke-tested successfully and can be considered for a controlled micro-cohort. It does not authorize public release, public URL publication or automatic tester invitations.

## Next Gate

```text
T10av_private_tester_cohort_expansion_gate
```
