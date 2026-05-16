# REMOTE-8J - Next Controlled Movement Manual Execution Record

REMOTE-8J records the exact manual execution approved by REMOTE-8I. It is still a record and validation phase, not an automation phase.

The purpose is to prove what the operator actually did by hand, whether it matches the approved package and whether monitoring can start without exposing raw identities, protected URLs, grant details, message bodies or local paths.

## Local Evidence Rule

Raw manual execution evidence must live only under ignored local paths:

- `.local/remote_service/remote8j_next_controlled_movement_manual_execution.local.json`
- `.local/remote_service/remote8j_next_controlled_movement_manual_execution/`

Tracked docs may contain only schema examples, validator contracts and public-safe summaries. Never commit:

- raw executed-user emails;
- protected URLs;
- private message body or invite text;
- grant keys;
- checkout URLs;
- session tokens;
- local workspace paths;
- support transcripts.

## Source Gate

The record requires:

- `sourceGate.remote8iStatus = GO_REMOTE8I_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVED`
- `sourceGate.remote8iSelectedDecision = approve_execution_record`
- a non-empty `sourceGate.remote8iApprovalId`
- `operatorApproval = true`
- `requestedAction = record_next_controlled_movement_manual_execution`

If REMOTE-8I did not approve execution, REMOTE-8J is `NO_GO`.

## Movement Match

For `add_1_2_users`:

- `plannedNewUsers` must be 1 or 2;
- `candidateCount` must match `plannedNewUsers`;
- `executedUsers` must match `plannedNewUsers`;
- each user must be tagged as `paid_subscription`, `tester_free` or `internal_operator`.

For non-user movement types, no executed users should be attached to the record.

## Required Checks

The private execution evidence must confirm:

- `remote8iApprovalConfirmed`
- `remote8hPackageStillMatches`
- `operatorFinalApprovalRecorded`
- `manualExecutionOnly`
- `noAutomationUsed`
- `manualActionRecorded`
- `entitlementsRecordedPrivately`
- `protectedUrlSharedPrivately`
- `supportWindowActive`
- `rollbackPlanStillReady`
- `pauseRuleStillActive`
- `monitoringStarted`
- `privateEvidenceStoredOutsideGit`

## Manual Counts

For `add_1_2_users`, these counters must match the executed user count:

- `invitesSentManually`
- `grantsRecordedManually`
- `privateMessagesSent`
- `protectedUrlsSharedPrivately`

They are proof of human execution, not permission to automate.

## Automation Must Stay Zero

These counters must remain zero in REMOTE-8J:

- `automationJobsStarted`
- `checkoutLinksCreated`
- `publicUrlsShared`
- `automatedEmailsSent`
- `automatedGrantsCreated`
- `trafficExpanded`
- `paidCampaignStarted`

The phase records what the operator already did manually. It must not start jobs, send emails, create checkout links, create grants or publish URLs.

## Tool

Use the local-only execution validator:

```powershell
python backend\sqx-edge-tool\tools\remote_next_controlled_movement_manual_execution.py `
  --evidence .local\remote_service\remote8j_next_controlled_movement_manual_execution.local.json `
  --out-dir .local\remote_service\remote8j_next_controlled_movement_manual_execution
```

The output is:

- `.local/remote_service/remote8j_next_controlled_movement_manual_execution/remote8j_next_controlled_movement_manual_execution.public.json`

The summary uses `remote-next-controlled-movement-manual-execution-v1`, redacts identities and keeps protected URLs/message bodies/private paths out of public output.

## Possible Decisions

- `GO_REMOTE8J_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION_RECORDED`: the manual execution is recorded and ready for monitoring.
- `NO_GO_REMOTE8J_MANUAL_EXECUTION_BLOCKED`: required source gate, checks, package counts or zero-automation counters are not clean.
- `NO_GO_REMOTE8J_MANUAL_EXECUTION_EVIDENCE_MISSING`: private local execution evidence has not been provided yet.

Even on GO:

- `record.automationAllowed = false`
- `postExecutionGate.furtherExpansionAllowedNow = false`
- `postExecutionGate.monitoringRequired = true`
- `postExecutionGate.rollbackAndPauseRemainActive = true`

## Next Phase

`REMOTE-8K - Post Execution Monitoring` should observe this executed movement before any further expansion, traffic increase, pricing campaign or automated onboarding work.
