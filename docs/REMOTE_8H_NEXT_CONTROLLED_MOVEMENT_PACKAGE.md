# REMOTE-8H - Next Controlled Movement Package

REMOTE-8H prepares the exact next controlled movement package after REMOTE-8G selects `prepare_next_controlled_movement`. It does not execute invites, grants, checkout, emails, traffic expansion, paid campaigns, onboarding or public URL sharing.

The purpose is to turn a human decision into a small, reversible and auditable package that can be reviewed again before execution.

## Local Evidence Rule

Raw package evidence must live only under ignored local paths:

- `.local/remote_service/remote8h_next_controlled_movement_package.local.json`
- `.local/remote_service/remote8h_next_controlled_movement_package/`

Tracked docs may contain only schema examples, validator contracts and public-safe summaries. Never commit:

- raw candidate emails;
- protected URLs;
- communication copy;
- checkout URLs;
- grant keys;
- session tokens;
- local workspace paths;
- private support notes.

## Source Gate

The package requires:

- `sourceGate.remote8gStatus = GO_REMOTE8G_TINY_COHORT_DECISION_REVIEW_READY`
- `sourceGate.remote8gSelectedDecision = prepare_next_controlled_movement`
- `operatorApproval = true`
- `requestedAction = prepare_next_controlled_movement_package`

If REMOTE-8G selected another decision, REMOTE-8H is `NO_GO`.

## Movement Types

Allowed package types:

- `add_1_2_users`
- `extend_same_cohort_observation`
- `prepare_paid_micro_offer`
- `schedule_demo_batch`

For `add_1_2_users`, planned new users are capped at 2 and the candidate count must match `plannedNewUsers`.

## Required Checks

The private package evidence must confirm:

- `remote8gDecisionReviewed`
- `oneMovementOnly`
- `scopeLimited`
- `recipientListPrivate`
- `entitlementBoundaryDefined`
- `supportOwnerAssigned`
- `supportWindowReady`
- `rollbackPlanReady`
- `pauseRuleReady`
- `noAutomationConfirmed`
- `executionRequiresSeparateApproval`
- `privateEvidenceStoredOutsideGit`

## Execution Must Stay Zero

These counters must remain zero in REMOTE-8H:

- `newUsersInvited`
- `grantsCreated`
- `checkoutLinksCreated`
- `emailsSent`
- `publicUrlsShared`
- `automationJobsStarted`
- `trafficExpanded`
- `paidCampaignStarted`

REMOTE-8H prepares the package only. Actual execution belongs to REMOTE-8I or later.

## Tool

Use the local-only package validator:

```powershell
python backend\sqx-edge-tool\tools\remote_next_controlled_movement_package.py `
  --evidence .local\remote_service\remote8h_next_controlled_movement_package.local.json `
  --out-dir .local\remote_service\remote8h_next_controlled_movement_package
```

The output is:

- `.local/remote_service/remote8h_next_controlled_movement_package/remote8h_next_controlled_movement_package.public.json`

The summary uses `remote-next-controlled-movement-package-v1`, redacts candidate identities and keeps protected URLs, copy, local paths and grant details private.

## Possible Decisions

- `GO_REMOTE8H_NEXT_CONTROLLED_MOVEMENT_PACKAGE_READY`: the package is ready for a separate execution approval phase.
- `NO_GO_REMOTE8H_NEXT_CONTROLLED_MOVEMENT_PACKAGE_BLOCKED`: source gate, movement type, checks, candidate limits or zero-execution metrics are not clean.
- `NO_GO_REMOTE8H_MOVEMENT_PACKAGE_EVIDENCE_MISSING`: private local package evidence has not been provided yet.

Even on GO:

- `movementPackage.automationAllowed = false`
- `movementPackage.executionAllowedNow = false`
- `movementPackage.requiresSeparateExecutionApproval = true`

## Next Phase

`REMOTE-8I - Next Controlled Movement Execution Approval` should approve or reject execution of the prepared package. It should still not execute automatically without its own explicit record.
