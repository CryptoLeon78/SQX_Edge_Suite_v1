# T10aw Private Tester Feedback Intake Gate

## Objective

T10aw prepares the private tester feedback intake gate after T10av, without committing tester URLs, tester emails, passwords, hostnames, account IDs, Access IDs, tokens, screenshots, raw feedback, tester identities or private support-channel details.

This phase does not create tester accounts, does not send invitations, does not publish the tester URL, does not rotate passwords and does not run a Cloudflare deployment.

## Feedback Boundary

Tester feedback may only be summarized for public/core documentation after all checks below are true:

- T10av cohort expansion returns `GO_PRIVATE_TESTER_COHORT_EXPANSION_READY_NO_GIT_LEAK`.
- The feedback channel is private and access-controlled outside Git.
- Raw tester feedback remains outside Git.
- Tester identities, emails, screenshots, URLs and account/provider IDs remain outside Git.
- The operator has a redaction policy before summarizing feedback.
- Feedback is classified into public-safe buckets such as onboarding friction, UI confusion, missing docs, performance notes, blocking bugs and commercial objections.
- Any public/core summary contains only aggregate counts and redacted themes.
- Support and revocation paths remain ready for testers who report access problems.
- No URL, hostname, tester email, password, token, API key, Access ID, account ID, deployment ID, screenshot, raw feedback or tester identity is committed.

## Private Local Feedback File

If the operator needs to record intake readiness, create this ignored file only:

```text
templates/SQX_Edge_Tester_Portal/tester-feedback-intake.local.json
```

It may contain public-safe booleans and small counts only. It must not contain:

- Tester emails, names, passwords, reset links or access codes.
- URL, hostname, domain, route or workers.dev address.
- Account IDs, Access IDs, deployment IDs, version IDs or policy IDs.
- Tokens, API keys, private keys, cookies or session values.
- Screenshots, image paths, raw feedback text, tester identities, chat links, support links, distribution links or meeting links.

## Accepted Fields

The evidence file may use only these fields:

- `phase`: `T10aw`.
- Boolean checks: `t10avCohortExpansionGo`, `privateFeedbackChannelReady`, `rawFeedbackKeptOutsideGit`, `redactionPolicyReady`, `publicSafeSummaryPolicyReady`, `aggregateCountsOnly`, `onboardingFrictionBucketReady`, `uiConfusionBucketReady`, `missingDocsBucketReady`, `performanceNotesBucketReady`, `blockingBugsBucketReady`, `commercialObjectionsBucketReady`, `supportChannelReadyPrivately`, `revocationPathReadyPrivately`, `feedbackIntakeApprovedPrivately`, `publicRepoContainsTesterEmails`, `publicRepoContainsTesterUrl`, `publicRepoContainsCredentials`, `publicRepoContainsProviderIds`, `publicRepoContainsScreenshots`, `publicRepoContainsRawFeedback`, `publicRepoContainsFeedbackIdentities`.
- Count checks: `feedbackResponderCount`, `redactedThemeCount`, `blockingBugCount`, `failedCheckCount`.

Counts must be non-negative integers no greater than 50.

## Expected Results

Without the ignored local feedback file, the expected guarded result is:

```text
NO_GO_PRIVATE_TESTER_FEEDBACK_INTAKE_EVIDENCE_MISSING
```

With safe local feedback intake evidence and no public leak, the expected result is:

```text
GO_PRIVATE_TESTER_FEEDBACK_INTAKE_READY_NO_GIT_LEAK
```

Unsafe evidence must fail closed and stop the phase.

## Operator Meaning

`GO_PRIVATE_TESTER_FEEDBACK_INTAKE_READY_NO_GIT_LEAK` means the operator can collect tester feedback privately and later publish only redacted aggregate themes. It does not authorize public release, public URL publication, raw feedback publication or automatic tester outreach.

## Next Gate

```text
T10ax_private_tester_feedback_triage_gate
```
