# REMOTE-8F - Tiny Cohort Monitoring And Pause/Rollback Watch

REMOTE-8F watches the 3-5 user cohort activated in REMOTE-8E before any further expansion. It does not invite new users, widen traffic, automate onboarding, send emails, change grants or publish private URLs.

The purpose is to prove the tiny cohort is stable enough to move to a separate operator decision phase, while keeping rollback and pause rules active.

## Current Status

REMOTE-8F was started on 2026-05-18 after REMOTE-8E returned
`GO_REMOTE8E_TINY_COHORT_MANUAL_EXECUTION_RECORDED` for a 5-user redacted
`tester_free` cohort.

Current ignored local evidence returns
`NO_GO_REMOTE8F_TINY_COHORT_MONITORING_BLOCKED`. This is expected at the start
of the window: access and entitlement are confirmed, but REMOTE-8F still needs
the 24h observation window, workspace isolation checks, artifact generation and
export/download confirmation before it can be marked clean.

No further expansion, automated onboarding, sales push or new tester movement is
allowed from this status.

## Local Evidence Rule

Raw monitoring evidence must live only under ignored local paths:

- `.local/remote_service/remote8f_tiny_cohort_monitoring.local.json`
- `.local/remote_service/remote8f_tiny_cohort_monitoring/`

Tracked docs may contain only schema examples, validator contracts and public-safe summaries. Never commit:

- raw user emails;
- protected URLs;
- support transcripts;
- Cloudflare identifiers;
- session tokens;
- grant keys;
- local workspace paths;
- private incident notes.

## Source Gate

The monitor requires:

- `sourceGate.remote8eStatus = GO_REMOTE8E_TINY_COHORT_MANUAL_EXECUTION_RECORDED`
- `operatorReview = true`
- `observationHours >= 24`
- monitored user count between 3 and 5
- `requestedDecision` in `stay_tiny_cohort`, `fix_blockers`, `rollback_tiny_cohort` or `prepare_next_controlled_movement`

If REMOTE-8E is not GO, the monitor is `NO_GO`.

## Required Signals

The private monitoring evidence must confirm:

- `remote8eExecutionGoConfirmed`
- `cohortAccessStable`
- `cloudflareAccessStable`
- `appSessionStable`
- `entitlementStable`
- `workspaceIsolationClean`
- `artifactGenerationObserved`
- `exportsDownloaded`
- `supportLoopObserved`
- `noWorkspaceLeakage`
- `noSecurityIncidents`
- `noUnresolvedSupportBlockers`
- `rollbackPlanReady`
- `pauseRuleReady`
- `privateEvidenceStoredOutsideGit`

## Zero-Tolerance Metrics

These counters must remain zero before any next movement can be reviewed:

- `openSupportItems`
- `unresolvedBlockers`
- `tunnelDrops`
- `appSessionFailures`
- `workspaceLeakEvents`
- `securityIncidents`
- `generationFailures`
- `entitlementErrors`
- `refundRequests`
- `crossUserDataFindings`
- `publicUrlLeaks`
- `automationJobsStarted`

## Tool

Use the local-only monitoring validator:

```powershell
python backend\sqx-edge-tool\tools\remote_tiny_cohort_monitoring.py `
  --evidence .local\remote_service\remote8f_tiny_cohort_monitoring.local.json `
  --out-dir .local\remote_service\remote8f_tiny_cohort_monitoring
```

The output is:

- `.local/remote_service/remote8f_tiny_cohort_monitoring/remote8f_tiny_cohort_monitoring.public.json`

The summary uses `remote-tiny-cohort-monitoring-v1`, redacts identities and keeps protected URLs, support logs, local paths and provider identifiers private.

## Possible Decisions

- `GO_REMOTE8F_TINY_COHORT_MONITORING_CLEAN`: the monitoring window is clean and ready for REMOTE-8G operator review.
- `NO_GO_REMOTE8F_TINY_COHORT_MONITORING_BLOCKED`: source gate, observation hours, required signals, per-user checks or zero-tolerance metrics are not clean.
- `NO_GO_REMOTE8F_MONITORING_EVIDENCE_MISSING`: private local monitoring evidence has not been provided yet.

Even on GO:

- `decision.automationAllowed = false`
- `decision.furtherExpansionAllowedNow = false`
- `decision.requiresOperatorApprovalForNextMovement = true`

## Next Phase

`REMOTE-8G - Tiny Cohort Decision Review` should turn this monitoring evidence into a human decision: continue observing, fix blockers, roll back or prepare one next controlled movement.
