# REMOTE-8D - Tiny Cohort Activation Package

REMOTE-8D prepares a manual activation package for 3-5 users after a clean REMOTE-8C GO. It is deliberately not an execution tool: it does not send invites, create grants, publish protected URLs, send emails, open checkout links or mutate entitlement stores.

The purpose is to make the next human step exact, reversible and auditable before any cohort expansion happens.

## Current Package Status

On 2026-05-18, after the operator explicitly changed REMOTE-8C to `expand_3_5`, ignored local evidence returned `GO_REMOTE8D_TINY_COHORT_ACTIVATION_PACKAGE_READY`.

Public-safe package summary:

- Candidate count: `3`
- Target cohort size: `3`
- Candidate kind: `tester_free`
- Feature scope: `full`
- Missing checks: `0`
- Automation blockers: `0`
- Invites sent: `0`
- Grants created: `0`
- Checkout links created: `0`
- Emails sent: `0`
- Public URLs shared: `0`

This is only a manual package. REMOTE-8E is still required before recording any real activation, and operator final confirmation is still mandatory.

## Local Evidence Rule

Raw package evidence must live only under ignored local paths:

- `.local/remote_service/remote8d_tiny_cohort_activation.local.json`
- `.local/remote_service/remote8d_tiny_cohort_activation/`

Tracked docs may contain only schema examples, validator contracts and public-safe summaries. Never commit:

- raw candidate emails;
- protected URLs;
- communication copy containing private links;
- grant keys;
- checkout URLs;
- session tokens;
- local workspace paths;
- support transcripts.

## Source Gate

The package requires:

- `sourceGate.remote8cStatus = GO_REMOTE8C_TINY_COHORT_EXPANSION_READY`
- `operatorApproval = true`
- `requestedAction = prepare_manual_activation_package`
- `targetCohortSize` between 3 and 5
- candidate count between 3 and 5

If REMOTE-8C is not GO, the package is `NO_GO`.

## Required Checks

The private package evidence must confirm:

- `remote8cGoConfirmed`
- `candidateListReviewed`
- `cohortSizeWithinLimit`
- `entitlementBoundariesDefined`
- `supportOwnerAssigned`
- `supportWindowReady`
- `rollbackPlanReady`
- `pauseRuleReady`
- `communicationCopyReviewed`
- `protectedUrlPrivateOnly`
- `workspaceIsolationReminder`
- `securityMonitoringReady`
- `noAutomationConfirmed`
- `privateEvidenceStoredOutsideGit`

## Automation Must Stay Zero

These counters must remain zero in REMOTE-8D:

- `invitesSent`
- `grantsCreated`
- `checkoutLinksCreated`
- `emailsSent`
- `publicUrlsShared`
- `automationJobsStarted`

This phase prepares the package only. Execution belongs to a later manual record phase.

## Tool

Use the local-only package validator:

```powershell
python backend\sqx-edge-tool\tools\remote_tiny_cohort_activation.py `
  --evidence .local\remote_service\remote8d_tiny_cohort_activation.local.json `
  --out-dir .local\remote_service\remote8d_tiny_cohort_activation
```

The output is:

- `.local/remote_service/remote8d_tiny_cohort_activation/remote8d_tiny_cohort_activation.public.json`

The summary uses `remote-tiny-cohort-activation-v1`, redacts all candidate identities and keeps protected URLs/communication copy private.

## Possible Decisions

- `GO_REMOTE8D_TINY_COHORT_ACTIVATION_PACKAGE_READY`: the manual package is ready for operator review.
- `NO_GO_REMOTE8D_TINY_COHORT_ACTIVATION_BLOCKED`: required source gate, checks, candidate limits or zero-automation counters are not clean.
- `NO_GO_REMOTE8D_ACTIVATION_PACKAGE_EVIDENCE_MISSING`: private local package evidence has not been provided yet.

Even on GO:

- `executionGate.invitesAllowedNow = false`
- `executionGate.grantMutationAllowedNow = false`
- `executionGate.emailSendingAllowedNow = false`
- `executionGate.checkoutAllowedNow = false`
- `executionGate.protectedUrlSharingAllowedNow = false`

## Next Phase

`REMOTE-8E - Tiny Cohort Manual Execution Record` should record the exact human execution only after the operator has reviewed the package and explicitly approved the controlled 3-5 user activation.
