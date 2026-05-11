# T10bc Private Tester Next Iteration Gate

## Objective

T10bc prepares the private next-iteration gate after T10bb, without committing tester URLs, tester emails, passwords, hostnames, account IDs, Access IDs, tokens, screenshots, raw feedback, tester identities, private bug details, private action details, private execution notes, private result notes, private decision notes, private iteration plans or private support-channel details.

This phase does not create tester accounts, does not send invitations, does not publish the tester URL, does not rotate passwords, does not contact testers, does not execute provider mutations and does not run a Cloudflare deployment.

## Next Iteration Boundary

Private tester decisions may only become a next-iteration plan after all checks below are true:

- T10bb iteration decision returns `GO_PRIVATE_TESTER_ITERATION_DECISION_READY_NO_GIT_LEAK`.
- Private iteration-decision evidence remains outside Git.
- Next iteration scope is approved privately before choosing the operating mode.
- The iteration mode is one of: repeat validation, execute fixes, expand micro-cohort, pause tester access, prepare next tester cycle or escalate commercial readiness.
- Target cohort, access window, support owner and risk controls are reviewed privately before any tester movement.
- The selected next iteration has private scope, success criteria, rollback criteria, owner and support readiness.
- Public/core output contains only a redacted iteration label, aggregate counts and safe iteration status.
- No URL, hostname, tester email, password, token, API key, Access ID, account ID, deployment ID, screenshot, raw feedback, tester identity, private bug detail, private action detail, private execution note, private result note, private decision note, private iteration plan or private support note is committed.

## Private Local Next Iteration File

If the operator needs to record next-iteration readiness, create this ignored file only:

```text
templates/SQX_Edge_Tester_Portal/tester-next-iteration.local.json
```

It may contain public-safe booleans, one safe enum and small counts only. It must not contain:

- Tester emails, names, passwords, reset links or access codes.
- URL, hostname, domain, route or workers.dev address.
- Account IDs, Access IDs, deployment IDs, version IDs or policy IDs.
- Tokens, API keys, private keys, cookies or session values.
- Screenshots, image paths, raw feedback text, private bug text, private action text, private execution text, private result text, private decision text, private iteration plan text, private support notes, tester identities, chat links, support links, distribution links or meeting links.

## Accepted Fields

The evidence file may use only these fields:

- `phase`: `T10bc`.
- `iterationMode`: one of `repeat_validation`, `execute_fixes`, `expand_micro_cohort`, `pause_tester_access`, `prepare_next_tester_cycle`, `escalate_commercial_readiness`.
- Boolean checks: `t10bbIterationDecisionGo`, `privateDecisionEvidenceReady`, `decisionEvidenceKeptOutsideGit`, `nextIterationScopeApprovedPrivately`, `iterationModeSelectedPrivately`, `targetCohortSelectedPrivately`, `accessWindowReviewedPrivately`, `supportOwnerAssignedPrivately`, `riskControlsReviewedPrivately`, `successCriteriaDefinedPrivately`, `rollbackCriteriaDefinedPrivately`, `publicSafeIterationSummaryReady`, `nextIterationApprovedPrivately`, `publicRepoContainsTesterEmails`, `publicRepoContainsTesterUrl`, `publicRepoContainsCredentials`, `publicRepoContainsProviderIds`, `publicRepoContainsScreenshots`, `publicRepoContainsRawFeedback`, `publicRepoContainsFeedbackIdentities`, `publicRepoContainsPrivateBugDetails`, `publicRepoContainsPrivateActionDetails`, `publicRepoContainsPrivateExecutionNotes`, `publicRepoContainsPrivateResultNotes`, `publicRepoContainsPrivateDecisionNotes`, `publicRepoContainsPrivateIterationPlan`, `publicRepoContainsPrivateSupportNotes`.
- Count checks: `decisionEvidenceCount`, `iterationCandidateCount`, `selectedIterationCount`, `targetCohortCount`, `actionItemCount`, `blockerCount`, `failedCheckCount`.

Counts must be non-negative integers no greater than 50.

## Expected Results

Without the ignored local next-iteration file, the expected guarded result is:

```text
NO_GO_PRIVATE_TESTER_NEXT_ITERATION_EVIDENCE_MISSING
```

With safe local next-iteration evidence and no public leak, the expected result is:

```text
GO_PRIVATE_TESTER_NEXT_ITERATION_READY_NO_GIT_LEAK
```

Unsafe evidence must fail closed and stop the phase.

## Operator Meaning

`GO_PRIVATE_TESTER_NEXT_ITERATION_READY_NO_GIT_LEAK` means the private tester program has a safe next-iteration plan. It does not authorize public release, public URL publication, raw feedback publication, tester outreach, deployment, provider mutation, account creation or automatic execution.

## Next Gate

```text
T10bd_private_tester_next_iteration_execution_gate
```
