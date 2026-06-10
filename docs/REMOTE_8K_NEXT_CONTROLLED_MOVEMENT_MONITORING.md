# REMOTE-8K - Next Controlled Movement Post Execution Monitoring

REMOTE-8K observes the manual movement recorded in REMOTE-8J before any new user, traffic, checkout, campaign or onboarding movement is allowed.

The purpose is to prove that the last manual execution stayed stable in the real protected environment: access, Cloudflare Access, app session, entitlement, workspace isolation, artifact generation, exports and support loop. It is still a monitoring phase, not an expansion phase.

## Local Evidence Rule

Raw post-execution monitoring evidence must live only under ignored local paths:

- `.local/remote_service/remote8k_next_controlled_movement_monitoring.local.json`
- `.local/remote_service/remote8k_next_controlled_movement_monitoring/`

Tracked docs may contain only schema examples, validator contracts and public-safe summaries. Never commit:

- raw user emails;
- protected URLs;
- support transcripts or private monitoring notes;
- Cloudflare identifiers;
- session tokens;
- grant keys;
- local workspace paths;
- private incident notes.

## Source Gate

The monitor requires:

- `sourceGate.remote8jStatus = GO_REMOTE8J_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION_RECORDED`
- a non-empty `sourceGate.remote8jExecutionId`
- `operatorReview = true`
- `observationHours >= 24`
- for `add_1_2_users`, monitored user count must match `sourceGate.executedUserCount`
- `requestedDecision` in `continue_monitoring`, `fix_blockers`, `rollback_last_movement` or `prepare_next_decision_review`

If REMOTE-8J is not GO, REMOTE-8K is `NO_GO`.

## Required Signals

The private monitoring evidence must confirm:

- `remote8jExecutionGoConfirmed`
- `manualScopeStillMatches`
- `accessStable`
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
- `exportFailures`
- `entitlementErrors`
- `refundRequests`
- `crossUserDataFindings`
- `publicUrlLeaks`
- `automationJobsStarted`
- `trafficExpanded`
- `paidCampaignStarted`
- `checkoutLinksCreated`
- `automatedEmailsSent`
- `automatedGrantsCreated`

## Tool

Use the local-only monitoring validator:

```powershell
python backend\sqx-edge-tool\tools\remote_next_controlled_movement_monitoring.py `
  --evidence .local\remote_service\remote8k_next_controlled_movement_monitoring.local.json `
  --out-dir .local\remote_service\remote8k_next_controlled_movement_monitoring
```

The output is:

- `.local/remote_service/remote8k_next_controlled_movement_monitoring/remote8k_next_controlled_movement_monitoring.public.json`

The summary uses `remote-next-controlled-movement-monitoring-v1`, redacts identities and keeps protected URLs, support notes, local paths and provider identifiers private.

## Possible Decisions

- `GO_REMOTE8K_NEXT_CONTROLLED_MOVEMENT_MONITORING_CLEAN`: the monitoring window is clean and ready for a separate REMOTE-8L operator decision.
- `NO_GO_REMOTE8K_NEXT_CONTROLLED_MOVEMENT_MONITORING_BLOCKED`: source gate, observation hours, required signals, per-user checks or zero-tolerance metrics are not clean.
- `NO_GO_REMOTE8K_MONITORING_EVIDENCE_MISSING`: private local monitoring evidence has not been provided yet.

Even on GO:

- `decision.automationAllowed = false`
- `decision.furtherExpansionAllowedNow = false`
- `decision.requiresOperatorApprovalForNextMovement = true`

## Current Public-Safe Run Log

2026-06-04:

- local-only validator status: `NO_GO_REMOTE8K_NEXT_CONTROLLED_MOVEMENT_MONITORING_BLOCKED`
- source gate: REMOTE-8J GO
- observation window: above the 24h minimum
- zero-tolerance metrics: all zero for incidents, expansion, checkout, emails, grants, campaigns and automation
- missing signals: `artifactGenerationObserved`, `exportsDownloaded`, `supportLoopObserved`
- missing per-user check: `artifactFlowChecked`
- next action: complete the missing private observations and rerun REMOTE-8K before any REMOTE-8L review or next movement

## Next Phase

`REMOTE-8L - Post Monitoring Decision Review` should turn this monitoring evidence into a human decision: keep observing, fix blockers, roll back or prepare one next controlled movement. REMOTE-8K alone never expands traffic or users.
