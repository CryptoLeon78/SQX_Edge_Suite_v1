# REMOTE-8I - Next Controlled Movement Execution Approval

REMOTE-8I approves, rejects or defers execution of the REMOTE-8H package. It still does not execute invites, grants, checkout, emails, traffic expansion, paid campaigns, onboarding or public URL sharing.

The purpose is to make the operator decision explicit after the package is prepared, while keeping the actual manual execution record in a separate phase.

## Local Evidence Rule

Raw approval evidence must live only under ignored local paths:

- `.local/remote_service/remote8i_next_controlled_movement_execution_approval.local.json`
- `.local/remote_service/remote8i_next_controlled_movement_execution_approval/`

Tracked docs may contain only schema examples, validator contracts and public-safe summaries. Never commit:

- raw candidate emails;
- protected URLs;
- communication copy;
- checkout URLs;
- grant keys;
- session tokens;
- local workspace paths;
- private decision notes.

## Source Gate

The approval requires:

- `sourceGate.remote8hStatus = GO_REMOTE8H_NEXT_CONTROLLED_MOVEMENT_PACKAGE_READY`
- a non-empty `sourceGate.remote8hPackageId`
- `operatorApproval = true`
- `requestedAction = approve_or_reject_next_controlled_movement_execution`

If REMOTE-8H did not produce a clean package, REMOTE-8I is `NO_GO`.

## Valid Decisions

Allowed execution decisions:

- `approve_execution_record`
- `reject_execution`
- `defer_execution`

`approve_execution_record` only authorizes creation of the next manual execution record. It does not execute the package.

## Required Checks

The private approval evidence must confirm:

- `remote8hPackageReviewed`
- `packageMatchesPrivateEvidence`
- `operatorDecisionRecorded`
- `decisionRationaleRecorded`
- `executionScopeUnchanged`
- `supportWindowStillReady`
- `rollbackStillReady`
- `pauseRuleStillReady`
- `noAutomationConfirmed`
- `executionRecordRequired`
- `privateEvidenceStoredOutsideGit`

For `approve_execution_record`, the private evidence must also provide an execution owner, at least 24 hours of support window, at least 24 hours of post-execution monitoring and a bounded execution delay window.

## Execution Must Stay Zero

These counters must remain zero in REMOTE-8I:

- `newUsersInvited`
- `grantsCreated`
- `checkoutLinksCreated`
- `emailsSent`
- `publicUrlsShared`
- `automationJobsStarted`
- `trafficExpanded`
- `paidCampaignStarted`

REMOTE-8I records the approval decision only. Actual execution belongs to REMOTE-8J or later.

## Tool

Use the local-only approval validator:

```powershell
python backend\sqx-edge-tool\tools\remote_next_controlled_movement_execution_approval.py `
  --evidence .local\remote_service\remote8i_next_controlled_movement_execution_approval.local.json `
  --out-dir .local\remote_service\remote8i_next_controlled_movement_execution_approval
```

The output is:

- `.local/remote_service/remote8i_next_controlled_movement_execution_approval/remote8i_next_controlled_movement_execution_approval.public.json`

The summary uses `remote-next-controlled-movement-execution-approval-v1`, redacts candidate identities and keeps protected URLs, decision notes, local paths and grant details private.

## Possible Decisions

- `GO_REMOTE8I_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVED`: the package is approved for a separate manual execution record.
- `GO_REMOTE8I_NEXT_CONTROLLED_MOVEMENT_EXECUTION_REJECTED`: the package is rejected and should be replanned.
- `GO_REMOTE8I_NEXT_CONTROLLED_MOVEMENT_EXECUTION_DEFERRED`: execution decision is deferred and should be revisited.
- `NO_GO_REMOTE8I_EXECUTION_APPROVAL_BLOCKED`: source gate, checks, approval readiness or zero-execution metrics are not clean.
- `NO_GO_REMOTE8I_EXECUTION_APPROVAL_EVIDENCE_MISSING`: private local approval evidence has not been provided yet.

Even on approval:

- `approval.automationAllowed = false`
- `approval.executionPerformedNow = false`
- `approval.requiresSeparateExecutionRecord = true`

## Next Phase

`REMOTE-8J - Manual Execution Record` should record the manual execution if REMOTE-8I approves it. It should still require its own evidence, redaction and zero-automation proof.
