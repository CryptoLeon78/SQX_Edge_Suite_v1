# REMOTE-8E - Tiny Cohort Manual Execution Record

REMOTE-8E records the exact manual execution of a 3-5 user tiny cohort only after the operator has reviewed and approved the REMOTE-8D activation package. It is still a record and validation phase, not an automation phase.

The purpose is to prove who was activated, which entitlement class was used and whether the private handoff was completed, without committing raw emails, protected URLs, message bodies or local paths.

## Current Status

On 2026-05-18, REMOTE-ASSET1 was verified by the operator in incognito and by
an external tester redacted as `tester-ref-asset1`. The previous
`/dashboard HTML OK but assets not OK` blocker is closed.

Later on 2026-05-18, the operator confirmed 5 users were manually added to
Cloudflare Access, privately guided through first access and observed without
problems. Ignored local evidence returned
`GO_REMOTE8E_TINY_COHORT_MANUAL_EXECUTION_RECORDED` with 5 redacted
`tester_free` users, matching manual counts, zero automation and no public
leak of raw emails, protected URLs or private handoff text.

Next gate: REMOTE-8F must monitor this 5-user cohort before any further
expansion, traffic increase, automated onboarding or sales push.

## Local Evidence Rule

Raw execution evidence must live only under ignored local paths:

- `.local/remote_service/remote8e_tiny_cohort_execution.local.json`
- `.local/remote_service/remote8e_tiny_cohort_execution/`

Tracked docs may contain only schema examples, validator contracts and public-safe summaries. Never commit:

- raw activated-user emails;
- protected URLs;
- private message body or invite text;
- grant keys;
- checkout URLs;
- session tokens;
- local workspace paths;
- support transcripts.

## Source Gate

The record requires:

- `sourceGate.remote8dStatus = GO_REMOTE8D_TINY_COHORT_ACTIVATION_PACKAGE_READY`
- `operatorApproval = true`
- `requestedAction = record_manual_activation_execution`
- activated user count between 3 and 5
- all activated users tagged as `paid_subscription`, `tester_free` or `internal_operator`

If REMOTE-8D is not GO, the execution record is `NO_GO`.

## Required Checks

The private execution evidence must confirm:

- `remote8dPackageGoConfirmed`
- `operatorFinalApprovalRecorded`
- `manualExecutionOnly`
- `noAutomationUsed`
- `privateMessagesSent`
- `entitlementsRecordedPrivately`
- `protectedUrlSharedPrivately`
- `supportWindowActive`
- `rollbackPlanStillReady`
- `pauseRuleStillActive`
- `monitoringStarted`
- `privateEvidenceStoredOutsideGit`

## Manual Counts

These counters must match the activated user count:

- `invitesSentManually`
- `grantsRecordedManually`
- `privateMessagesSent`
- `protectedUrlsSharedPrivately`

They are proof of human execution, not permission to automate.

## Automation Must Stay Zero

These counters must remain zero in REMOTE-8E:

- `automationJobsStarted`
- `checkoutLinksCreated`
- `publicUrlsShared`
- `automatedEmailsSent`
- `automatedGrantsCreated`

The phase records what the operator already did manually. It must not start jobs, send emails, create checkout links or publish URLs.

## Tool

Use the local-only execution validator:

```powershell
python backend\sqx-edge-tool\tools\remote_tiny_cohort_execution.py `
  --evidence .local\remote_service\remote8e_tiny_cohort_execution.local.json `
  --out-dir .local\remote_service\remote8e_tiny_cohort_execution
```

The output is:

- `.local/remote_service/remote8e_tiny_cohort_execution/remote8e_tiny_cohort_execution.public.json`

The summary uses `remote-tiny-cohort-execution-v1`, redacts all identities and keeps protected URLs/message bodies/private paths out of public output.

## Possible Decisions

- `GO_REMOTE8E_TINY_COHORT_MANUAL_EXECUTION_RECORDED`: the manual execution is recorded and ready for monitoring.
- `NO_GO_REMOTE8E_TINY_COHORT_EXECUTION_BLOCKED`: required source gate, checks, cohort limits, manual counts or zero-automation counters are not clean.
- `NO_GO_REMOTE8E_EXECUTION_EVIDENCE_MISSING`: private local execution evidence has not been provided yet.

Even on GO:

- `record.automationAllowed = false`
- `postExecutionGate.furtherExpansionAllowedNow = false`
- `postExecutionGate.monitoringRequired = true`
- `postExecutionGate.rollbackAndPauseRemainActive = true`

## Next Phase

`REMOTE-8F - Tiny Cohort Monitoring And Pause/Rollback Watch` should observe this activated cohort before any further expansion, traffic increase, pricing campaign or automated onboarding work.
