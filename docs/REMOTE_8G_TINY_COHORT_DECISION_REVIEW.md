# REMOTE-8G - Tiny Cohort Decision Review

REMOTE-8G turns the REMOTE-8F monitoring summary into a human decision. It does not execute traffic, checkout, grants, emails, onboarding, public URL sharing or campaign actions.

The purpose is to decide what should happen next without letting a clean monitoring window automatically expand the pilot.

## Local Evidence Rule

Raw decision evidence must live only under ignored local paths:

- `.local/remote_service/remote8g_tiny_cohort_decision_review.local.json`
- `.local/remote_service/remote8g_tiny_cohort_decision_review/`

Tracked docs may contain only schema examples, validator contracts and public-safe summaries. Never commit:

- raw user emails;
- protected URLs;
- decision rationale text containing private support details;
- support transcripts;
- Cloudflare identifiers;
- session tokens;
- grant keys;
- local workspace paths;
- private incident notes.

## Source Gate

The review accepts either a clean or blocked REMOTE-8F source:

- `GO_REMOTE8F_TINY_COHORT_MONITORING_CLEAN`
- `NO_GO_REMOTE8F_TINY_COHORT_MONITORING_BLOCKED`

Only `GO_REMOTE8F_TINY_COHORT_MONITORING_CLEAN` may support `selectedDecision = prepare_next_controlled_movement`.

## Allowed Decisions

The operator can select:

- `continue_observing`
- `fix_blockers`
- `rollback_tiny_cohort`
- `prepare_next_controlled_movement`

If the monitoring source is blocked or has recorded blockers, the next controlled movement cannot be prepared.

## Required Checks

The private decision evidence must confirm:

- `remote8fMonitoringReviewed`
- `operatorDecisionRecorded`
- `decisionRationaleRecorded`
- `cohortSizeReviewed`
- `supportOwnerConfirmed`
- `rollbackPlanReady`
- `pauseRuleReady`
- `entitlementBoundaryReviewed`
- `workspaceIsolationReviewed`
- `securityReviewCompleted`
- `noAutomationConfirmed`
- `privateEvidenceStoredOutsideGit`

## Execution Must Stay Zero

These counters must remain zero in REMOTE-8G:

- `newUsersInvited`
- `grantsChanged`
- `checkoutLinksCreated`
- `emailsSent`
- `publicUrlsShared`
- `automationJobsStarted`
- `trafficExpanded`
- `paidCampaignStarted`

REMOTE-8G may prepare a next package only as a decision artifact. Actual execution belongs to a separate later gate.

## Tool

Use the local-only decision validator:

```powershell
python backend\sqx-edge-tool\tools\remote_tiny_cohort_decision_review.py `
  --evidence .local\remote_service\remote8g_tiny_cohort_decision_review.local.json `
  --out-dir .local\remote_service\remote8g_tiny_cohort_decision_review
```

The output is:

- `.local/remote_service/remote8g_tiny_cohort_decision_review/remote8g_tiny_cohort_decision_review.public.json`

The summary uses `remote-tiny-cohort-decision-review-v1`, redacts identities and keeps protected URLs, support logs, local paths, provider identifiers and rationale text private.

## Possible Decisions

- `GO_REMOTE8G_TINY_COHORT_DECISION_REVIEW_READY`: the reviewed decision is ready for its next separate gate.
- `NO_GO_REMOTE8G_TINY_COHORT_DECISION_REVIEW_BLOCKED`: source gate, selected decision, checks, reviewed users or zero-execution metrics are not clean.
- `NO_GO_REMOTE8G_DECISION_REVIEW_EVIDENCE_MISSING`: private local decision evidence has not been provided yet.

Even on GO:

- `decision.automationAllowed = false`
- `decision.executionAllowedNow = false`
- `decision.requiresSeparateNextPhase = true`

## Next Phase

`REMOTE-8H - Next Controlled Movement Package` should prepare the exact next package only if REMOTE-8G selected `prepare_next_controlled_movement`. Other decisions should continue monitoring, fix blockers or prepare rollback.
