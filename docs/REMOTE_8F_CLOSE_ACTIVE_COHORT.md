# REMOTE-8F-CLOSE - Active Cohort Monitoring Clean

## Summary

REMOTE-8F-CLOSE closes the active tiny-cohort monitoring window with a clean
operator-safe result. The active monitored cohort is `4/4 ready` and the local
REMOTE-8F monitoring evidence returns:

`GO_REMOTE8F_TINY_COHORT_MONITORING_CLEAN`

This phase does not create users, grants, Cloudflare changes, checkout links,
emails, protected URLs or onboarding automation. It only records that the
confirmed active cohort can move to REMOTE-8G decision review.

## Active Cohort

Active aliases included in the clean close:

- `CREATOR-IVAN`
- `TESTER-DRP`
- `TESTER-BIBI`
- `TESTER-JL`

Active matrix status at close:

- Active aliases: `4`
- Ready active aliases: `4`
- Active aliases needing action: `0`
- Open incidents: `0`
- Context recapture required: `0`

## Standby Aliases

Standby aliases remain visible but do not block the active cohort close:

- `TESTER-RILIS` - standby because the operator could not contact the tester to
  confirm context recapture in this close window.
- `TESTER-ESTHER` - standby alias, not part of the active REMOTE-8F close.

If a standby tester returns, the operator must recapture or review the context
through the existing REMOTE-COHORT-FIX2 flow before that alias can become active
again.

## Evidence

Local-only evidence:

- `.local/remote_service/remote8f_tiny_cohort_monitoring.local.json`
- `.local/remote_service/remote8f_tiny_cohort_monitoring/remote8f_tiny_cohort_monitoring.public.json`
- `.local/remote_service/remote_cohort_matrix/remote_cohort_matrix.local.json`
- `.local/remote_service/remote_cohort_matrix/remote_cohort_context_reconcile.local.json`

Tracked evidence is intentionally alias-only. Raw emails, IPs, protected URLs,
cookies, session tokens, Cloudflare identifiers, grant keys and local paths stay
out of Git.

## Close Decision

REMOTE-8F-CLOSE allows only:

- move to REMOTE-8G decision review;
- keep automation disabled;
- keep further expansion disabled until a later explicit decision phase.

It does not allow:

- inviting more testers;
- creating or editing grants;
- sending emails;
- changing Cloudflare Access;
- publishing protected URLs;
- starting checkout or payment automation.

## Next Recommended Phase

`REMOTE-8G` should review this clean monitoring result and choose one explicit
operator decision: continue observing, fix a blocker if one appears, roll back,
or prepare the next controlled movement package.
