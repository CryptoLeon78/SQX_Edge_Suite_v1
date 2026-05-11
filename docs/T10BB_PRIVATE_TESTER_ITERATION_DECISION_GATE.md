# T10bb Private Tester Iteration Decision Gate

## Objective

T10bb prepares the private tester iteration decision gate after T10ba, without committing tester URLs, tester emails, passwords, hostnames, account IDs, Access IDs, tokens, screenshots, raw feedback, tester identities, private bug details, private action details, private execution notes, private result notes, private decision notes or private support-channel details.

This phase does not create tester accounts, does not send invitations, does not publish the tester URL, does not rotate passwords, does not contact testers, does not execute provider mutations and does not run a Cloudflare deployment.

## Iteration Decision Boundary

Private tester results may only become an iteration decision after all checks below are true:

- T10ba result validation returns `GO_PRIVATE_TESTER_RESULT_VALIDATION_READY_NO_GIT_LEAK`.
- Private result-validation evidence remains outside Git.
- Decision scope is approved privately before choosing the next move.
- The decision is one of: repeat validation, execute fixes, expand micro-cohort, pause tester access, prepare next tester cycle or escalate to commercial readiness.
- P0/P1 blockers and support/commercial risks are reviewed privately before expansion.
- The selected decision has private owner, acceptance criteria, rollback/risk notes and next gate.
- Public/core output contains only a redacted decision label, aggregate counts and safe iteration status.
- No URL, hostname, tester email, password, token, API key, Access ID, account ID, deployment ID, screenshot, raw feedback, tester identity, private bug detail, private action detail, private execution note, private result note or private decision note is committed.

## Private Local Decision File

If the operator needs to record iteration-decision readiness, create this ignored file only:

```text
templates/SQX_Edge_Tester_Portal/tester-iteration-decision.local.json
```

It may contain public-safe booleans, one safe enum and small counts only. It must not contain:

- Tester emails, names, passwords, reset links or access codes.
- URL, hostname, domain, route or workers.dev address.
- Account IDs, Access IDs, deployment IDs, version IDs or policy IDs.
- Tokens, API keys, private keys, cookies or session values.
- Screenshots, image paths, raw feedback text, private bug text, private action text, private execution text, private result text, private decision text, tester identities, chat links, support links, distribution links or meeting links.

## Accepted Fields

The evidence file may use only these fields:

- `phase`: `T10bb`.
- `decision`: one of `repeat_validation`, `execute_fixes`, `expand_micro_cohort`, `pause_tester_access`, `prepare_next_tester_cycle`, `escalate_commercial_readiness`.
- Boolean checks: `t10baResultValidationGo`, `privateResultEvidenceReady`, `resultEvidenceKeptOutsideGit`, `decisionScopeApprovedPrivately`, `decisionSelectedPrivately`, `p0P1BlockersReviewedPrivately`, `supportRiskReviewedPrivately`, `commercialRiskReviewedPrivately`, `ownerAssignedPrivately`, `acceptanceCriteriaDefinedPrivately`, `rollbackRiskReviewedPrivately`, `nextGateSelectedPrivately`, `publicSafeDecisionSummaryReady`, `iterationDecisionApprovedPrivately`, `publicRepoContainsTesterEmails`, `publicRepoContainsTesterUrl`, `publicRepoContainsCredentials`, `publicRepoContainsProviderIds`, `publicRepoContainsScreenshots`, `publicRepoContainsRawFeedback`, `publicRepoContainsFeedbackIdentities`, `publicRepoContainsPrivateBugDetails`, `publicRepoContainsPrivateActionDetails`, `publicRepoContainsPrivateExecutionNotes`, `publicRepoContainsPrivateResultNotes`, `publicRepoContainsPrivateDecisionNotes`.
- Count checks: `validatedResultCount`, `acceptedActionCount`, `repeatActionCount`, `blockedActionCount`, `decisionCandidateCount`, `selectedDecisionCount`, `failedCheckCount`.

Counts must be non-negative integers no greater than 50.

## Expected Results

Without the ignored local iteration-decision file, the expected guarded result is:

```text
NO_GO_PRIVATE_TESTER_ITERATION_DECISION_EVIDENCE_MISSING
```

With safe local iteration-decision evidence and no public leak, the expected result is:

```text
GO_PRIVATE_TESTER_ITERATION_DECISION_READY_NO_GIT_LEAK
```

Unsafe evidence must fail closed and stop the phase.

## Operator Meaning

`GO_PRIVATE_TESTER_ITERATION_DECISION_READY_NO_GIT_LEAK` means private tester validation has produced a safe next-move decision. It does not authorize public release, public URL publication, raw feedback publication, tester outreach, deployment, provider mutation or automatic execution of the selected decision.

## Next Gate

```text
T10bc_private_tester_next_iteration_gate
```
