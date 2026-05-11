# T10ax Private Tester Feedback Triage Gate

## Objective

T10ax prepares the private tester feedback triage gate after T10aw, without committing tester URLs, tester emails, passwords, hostnames, account IDs, Access IDs, tokens, screenshots, raw feedback, tester identities, private bug details or private support-channel details.

This phase does not create tester accounts, does not send invitations, does not publish the tester URL, does not rotate passwords and does not run a Cloudflare deployment.

## Triage Boundary

Tester feedback may only become project actions after all checks below are true:

- T10aw feedback intake returns `GO_PRIVATE_TESTER_FEEDBACK_INTAKE_READY_NO_GIT_LEAK`.
- Raw feedback remains outside Git.
- Feedback is grouped privately into public-safe themes.
- Each theme has a private severity/priority assigned.
- Blocking bugs, support issues, onboarding friction, UI confusion, performance notes and commercial objections are separated before action planning.
- Action candidates are created privately before any public/core summary.
- Public/core output contains only redacted themes, aggregate counts and safe action labels.
- No URL, hostname, tester email, password, token, API key, Access ID, account ID, deployment ID, screenshot, raw feedback, private bug detail or tester identity is committed.

## Private Local Triage File

If the operator needs to record triage readiness, create this ignored file only:

```text
templates/SQX_Edge_Tester_Portal/tester-feedback-triage.local.json
```

It may contain public-safe booleans and small counts only. It must not contain:

- Tester emails, names, passwords, reset links or access codes.
- URL, hostname, domain, route or workers.dev address.
- Account IDs, Access IDs, deployment IDs, version IDs or policy IDs.
- Tokens, API keys, private keys, cookies or session values.
- Screenshots, image paths, raw feedback text, private bug text, tester identities, chat links, support links, distribution links or meeting links.

## Accepted Fields

The evidence file may use only these fields:

- `phase`: `T10ax`.
- Boolean checks: `t10awFeedbackIntakeGo`, `privateFeedbackEvidenceReady`, `rawFeedbackKeptOutsideGit`, `triageBucketsReviewed`, `severityAssignedPrivately`, `actionCandidatesCreatedPrivately`, `publicSafeActionSummaryReady`, `blockingBugsSeparatedPrivately`, `supportIssuesSeparatedPrivately`, `commercialThemesSeparatedPrivately`, `onboardingThemesSeparatedPrivately`, `uiThemesSeparatedPrivately`, `performanceThemesSeparatedPrivately`, `feedbackTriageApprovedPrivately`, `publicRepoContainsTesterEmails`, `publicRepoContainsTesterUrl`, `publicRepoContainsCredentials`, `publicRepoContainsProviderIds`, `publicRepoContainsScreenshots`, `publicRepoContainsRawFeedback`, `publicRepoContainsFeedbackIdentities`, `publicRepoContainsPrivateBugDetails`.
- Count checks: `triagedThemeCount`, `p0ThemeCount`, `p1ThemeCount`, `p2ThemeCount`, `actionCandidateCount`, `failedCheckCount`.

Counts must be non-negative integers no greater than 50.

## Expected Results

Without the ignored local triage file, the expected guarded result is:

```text
NO_GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_EVIDENCE_MISSING
```

With safe local triage evidence and no public leak, the expected result is:

```text
GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_READY_NO_GIT_LEAK
```

Unsafe evidence must fail closed and stop the phase.

## Operator Meaning

`GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_READY_NO_GIT_LEAK` means private tester feedback has been grouped, prioritized and converted into safe action candidates. It does not authorize public release, public URL publication, raw feedback publication or automatic tester outreach.

## Next Gate

```text
T10ay_private_tester_action_plan_gate
```
