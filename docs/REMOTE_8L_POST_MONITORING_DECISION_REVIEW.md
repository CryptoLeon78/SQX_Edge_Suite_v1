# REMOTE-8L - Post Monitoring Decision Review

REMOTE-8L turns a REMOTE-8K monitoring window into one explicit human decision.
It never invites users, changes grants, sends email, creates checkout links, expands
traffic or publishes protected URLs. It only decides the next controlled route.

## Source Gate

REMOTE-8L reads ignored local evidence from:

`.local/remote_service/remote8l_post_monitoring_decision_review.local.json`

It writes a redacted public-safe summary to:

`.local/remote_service/remote8l_post_monitoring_decision_review/remote8l_post_monitoring_decision_review.public.json`

Required source statuses:

- `GO_REMOTE8K_NEXT_CONTROLLED_MOVEMENT_MONITORING_CLEAN`
- `NO_GO_REMOTE8K_NEXT_CONTROLLED_MOVEMENT_MONITORING_BLOCKED`

Only clean REMOTE-8K monitoring with `remote8kRequestedDecision =
prepare_next_decision_review`, at least 24 observation hours and zero monitoring
blockers can prepare another controlled movement package.

## Valid Decisions

The operator must choose exactly one `selectedDecision`:

- `continue_monitoring`: keep the current observation loop active.
- `fix_blockers`: prepare a blocker fix plan, with no new access movement.
- `rollback_last_movement`: prepare a manual rollback package.
- `prepare_next_controlled_movement`: route back into the controlled package gate.

## Required Checks

All checks must be true:

- `remote8kMonitoringReviewed`
- `operatorDecisionRecorded`
- `decisionRationaleRecorded`
- `sourceStatusReviewed`
- `monitoringWindowReviewed`
- `supportOutcomeReviewed`
- `workspaceIsolationReviewed`
- `securityOutcomeReviewed`
- `entitlementOutcomeReviewed`
- `generationExportOutcomeReviewed`
- `rollbackPlanReady`
- `pauseRuleReady`
- `noAutomationConfirmed`
- `privateEvidenceStoredOutsideGit`

## Reviewed Users

For `add_1_2_users`, reviewed users must match the monitored user count from
REMOTE-8K and stay capped at 1-2 users. Each user requires:

- `accessOutcomeReviewed`
- `entitlementOutcomeReviewed`
- `workspaceOutcomeReviewed`
- `artifactOutcomeReviewed`
- `supportOutcomeReviewed`
- `noNewCriticalIssue`

The public summary returns only redacted identity references and short identity
hashes. Raw emails stay in ignored local evidence.

## Zero Execution Metrics

These must remain zero in REMOTE-8L:

- `newUsersInvited`
- `grantsChanged`
- `checkoutLinksCreated`
- `emailsSent`
- `publicUrlsShared`
- `protectedUrlsShared`
- `automationJobsStarted`
- `trafficExpanded`
- `paidCampaignStarted`
- `automatedEmailsSent`
- `automatedGrantsCreated`
- `entitlementsChanged`

Any non-zero metric blocks the decision review.

## Privacy Rules

The public summary must not return raw emails, protected URLs, local paths,
secrets, session tokens, grant keys, support logs, private notes or private
decision rationale. The summary uses `remote-post-monitoring-decision-review-v1`.

## Statuses

- `GO_REMOTE8L_POST_MONITORING_DECISION_REVIEW_READY`: the operator decision is valid.
- `NO_GO_REMOTE8L_POST_MONITORING_DECISION_REVIEW_BLOCKED`: source gate, checks, user review or zero-execution metrics are not clean.
- `NO_GO_REMOTE8L_DECISION_REVIEW_EVIDENCE_MISSING`: ignored local evidence has not been collected.
- `NO_GO_REMOTE8L_PUBLIC_SUMMARY_PRIVACY_LEAK`: public summary would leak private data.

## Output Meaning

Even on GO:

- `decision.automationAllowed = false`
- `decision.executionAllowedNow = false`
- `decision.furtherExpansionAllowedNow = false`
- `decision.requiresSeparateNextPhase = true`

If the selected decision is `prepare_next_controlled_movement`, REMOTE-8L routes
back to `REMOTE-8H - Next Controlled Movement Package`. That later gate still
prepares only one exact package and does not execute access changes.
