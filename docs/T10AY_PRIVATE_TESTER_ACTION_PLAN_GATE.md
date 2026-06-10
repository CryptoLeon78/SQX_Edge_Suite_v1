# T10ay Private Tester Action Plan Gate

## Objective

T10ay prepares the private tester action plan gate after T10ax, without committing tester URLs, tester emails, passwords, hostnames, account IDs, Access IDs, tokens, screenshots, raw feedback, tester identities, private bug details, private action details or private support-channel details.

This phase does not create tester accounts, does not send invitations, does not publish the tester URL, does not rotate passwords, does not contact testers and does not run a Cloudflare deployment.

## Action Plan Boundary

Tester feedback may only become execution work after all checks below are true:

- T10ax feedback triage returns `GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_READY_NO_GIT_LEAK`.
- The private triage evidence remains outside Git.
- Action candidates are converted privately into prioritized action items.
- P0, P1 and P2 actions are separated before public/core planning.
- Each action has a private owner, acceptance criteria and release-risk note.
- Support responses and commercial objections are mapped privately before any buyer-facing change.
- Public/core output contains only redacted action labels, aggregate counts and safe planning status.
- No URL, hostname, tester email, password, token, API key, Access ID, account ID, deployment ID, screenshot, raw feedback, tester identity, private bug detail or private action detail is committed.

## Private Local Action Plan File

If the operator needs to record action-plan readiness, create this ignored file only:

```text
templates/SQX_Edge_Tester_Portal/tester-action-plan.local.json
```

It may contain public-safe booleans and small counts only. It must not contain:

- Tester emails, names, passwords, reset links or access codes.
- URL, hostname, domain, route or workers.dev address.
- Account IDs, Access IDs, deployment IDs, version IDs or policy IDs.
- Tokens, API keys, private keys, cookies or session values.
- Screenshots, image paths, raw feedback text, private bug text, private action text, tester identities, chat links, support links, distribution links or meeting links.

## Accepted Fields

The evidence file may use only these fields:

- `phase`: `T10ay`.
- Boolean checks: `t10axFeedbackTriageGo`, `privateTriageEvidenceReady`, `triageEvidenceKeptOutsideGit`, `actionPlanDraftedPrivately`, `actionsPrioritizedPrivately`, `p0ActionsEscalatedPrivately`, `p1ActionsScheduledPrivately`, `p2ActionsBacklogPrivately`, `ownerAssignedPrivately`, `acceptanceCriteriaDefinedPrivately`, `releaseRiskReviewedPrivately`, `supportResponsePreparedPrivately`, `commercialObjectionsMappedPrivately`, `publicSafeActionSummaryReady`, `actionPlanApprovedPrivately`, `publicRepoContainsTesterEmails`, `publicRepoContainsTesterUrl`, `publicRepoContainsCredentials`, `publicRepoContainsProviderIds`, `publicRepoContainsScreenshots`, `publicRepoContainsRawFeedback`, `publicRepoContainsFeedbackIdentities`, `publicRepoContainsPrivateBugDetails`, `publicRepoContainsPrivateActionDetails`.
- Count checks: `plannedActionCount`, `p0ActionCount`, `p1ActionCount`, `p2ActionCount`, `supportActionCount`, `commercialActionCount`, `failedCheckCount`.

Counts must be non-negative integers no greater than 50.

## Expected Results

Without the ignored local action-plan file, the expected guarded result is:

```text
NO_GO_PRIVATE_TESTER_ACTION_PLAN_EVIDENCE_MISSING
```

With safe local action-plan evidence and no public leak, the expected result is:

```text
GO_PRIVATE_TESTER_ACTION_PLAN_READY_NO_GIT_LEAK
```

Unsafe evidence must fail closed and stop the phase.

## Operator Meaning

`GO_PRIVATE_TESTER_ACTION_PLAN_READY_NO_GIT_LEAK` means private tester feedback has a prioritized, owner-ready action plan that can be executed in later phases. It does not authorize public release, public URL publication, raw feedback publication, tester outreach, deployment or automatic work assignment.

## Next Gate

```text
T10az_private_tester_action_execution_gate
```
