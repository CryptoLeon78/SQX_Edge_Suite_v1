# REMOTE-COHORT-EVIDENCE1 - Cohort Download Smoke Passed

## Summary

REMOTE-COHORT-EVIDENCE1 records the first public-safe cohort download
validation after REMOTE-DOWNLOADS2 and REMOTE-8E. The operator reported that
the current tiny cohort can access SQX Edge Suite and complete browser download
smoke checks without exposing server folders or local paths to users.

Acceptance phrase: `cohort download smoke passed`.

## Redacted Cohort Result

| Alias | Role | Access | Download smoke |
| --- | --- | --- | --- |
| CREATOR-IVAN | creator_operator | OK | OK |
| TESTER-DRP | tester_free | OK | OK |
| TESTER-RILIS | tester_free | OK | OK |
| TESTER-BIBI | tester_free | OK | OK |
| TESTER-JL | tester_free | OK | OK |

Totals:

- Participants observed: 5.
- Access OK: 5 of 5.
- Browser download smoke OK: 5 of 5.
- Blockers reported in this mini-evidence: 0.

## Scope

This evidence confirms the browser-download delivery model at cohort level:

- generated `.cfx` files are delivered by explicit browser download actions;
- user-facing exports must land through the browser download flow;
- `Abrir carpeta`, server-folder browsing and local-path wording remain outside
  normal user UI;
- Control Panel/operator-only diagnostics remain separate from user exports.

## Privacy Boundary

Tracked files for this phase use aliases only. Raw emails, raw IPs, protected
URLs, cookies, session tokens, Cloudflare identifiers, local Windows paths and
private support text must not be committed.

Private local evidence is stored only under the ignored path:

`.local/remote_service/remote_cohort_evidence1/remote_cohort_download_smoke.local.json`

## Next Gate

This mini-evidence strengthens REMOTE-8F monitoring, but it does not by itself
authorize new testers, new grants, checkout, emails or a wider public launch.
The next controlled decision remains REMOTE-8F / REMOTE-8G review.
