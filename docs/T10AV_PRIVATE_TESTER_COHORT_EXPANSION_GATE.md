# T10av Private Tester Cohort Expansion Gate

## Objective

T10av prepares the private micro-cohort expansion gate after T10au, without committing tester URLs, tester emails, passwords, hostnames, account IDs, Access IDs, tokens, screenshots, feedback identities or private support-channel details.

This phase does not create tester accounts, does not send invitations, does not publish the tester URL, does not rotate passwords and does not run a Cloudflare deployment.

## Expansion Boundary

The private tester cohort may only expand beyond the first smoke tester after all checks below are true:

- T10au first-tester smoke returns `GO_PRIVATE_FIRST_TESTER_SMOKE_PASSED_NO_GIT_LEAK`.
- The first tester path passed Access, app login, `tester_pro`, admin-block and logout checks.
- The next cohort size is intentionally capped between 2 and 10 testers.
- Every selected tester has a private identity/account path prepared outside Git.
- The protected URL will be shared through private one-to-one channels only.
- Support, revocation and 15-day renewal capacity are ready for the selected cohort.
- Feedback intake is prepared with redacted/public-safe summaries only.
- No URL, hostname, tester email, password, token, API key, Access ID, account ID, deployment ID, screenshot, feedback identity or version ID is committed.

## Private Local Expansion File

If the operator needs to record cohort readiness, create this ignored file only:

```text
templates/SQX_Edge_Tester_Portal/tester-cohort-expansion.local.json
```

It may contain public-safe booleans and small counts only. It must not contain:

- Tester emails, names, passwords, reset links or access codes.
- URL, hostname, domain, route or workers.dev address.
- Account IDs, Access IDs, deployment IDs, version IDs or policy IDs.
- Tokens, API keys, private keys, cookies or session values.
- Screenshots, image paths, feedback identities, chat links, support links, distribution links or meeting links.

## Accepted Fields

The evidence file may use only these fields:

- `phase`: `T10av`.
- Boolean checks: `t10auFirstSmokeGo`, `firstTesterSmokePassedPrivately`, `cohortSizeWithinLimit`, `privateAccountsPreparedForCohort`, `privateOneToOneShareChannelsReady`, `supportCapacityReadyPrivately`, `revocationPathReadyPrivately`, `renewalCadenceScheduled`, `feedbackIntakeReadyPrivately`, `redactedFeedbackPolicyReady`, `cohortExpansionApprovedPrivately`, `testerUrlsSharedPrivately`, `publicRepoContainsTesterEmails`, `publicRepoContainsTesterUrl`, `publicRepoContainsCredentials`, `publicRepoContainsProviderIds`, `publicRepoContainsScreenshots`, `publicRepoContainsFeedbackIdentities`.
- Count checks: `approvedTesterCount`, `targetCohortSize`, `supportOwnerCount`, `failedCheckCount`.

Counts must be non-negative integers no greater than 50. `targetCohortSize` must be between 2 and 10 for GO.

## Expected Results

Without the ignored local expansion file, the expected guarded result is:

```text
NO_GO_PRIVATE_TESTER_COHORT_EXPANSION_EVIDENCE_MISSING
```

With safe local expansion evidence and no public leak, the expected result is:

```text
GO_PRIVATE_TESTER_COHORT_EXPANSION_READY_NO_GIT_LEAK
```

Unsafe evidence must fail closed and stop the phase.

## Operator Meaning

`GO_PRIVATE_TESTER_COHORT_EXPANSION_READY_NO_GIT_LEAK` means the operator can expand from one smoke tester to a private micro-cohort using only private channels. It does not authorize public release, public URL publication, automatic emails or uncontrolled tester growth.

## Next Gate

```text
T10aw_private_tester_feedback_intake_gate
```
