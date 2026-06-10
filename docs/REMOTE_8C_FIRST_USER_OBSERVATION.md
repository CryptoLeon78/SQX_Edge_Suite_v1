# REMOTE-8C - First User Support Observation And Expansion Decision

REMOTE-8C turns the first real user's private support and stability evidence into a redacted decision. It does not create users, send invites, publish links, run checkout automation or change paid access by itself.

The phase exists after REMOTE-8B. REMOTE-8B proves that the private live smoke can be ingested safely. REMOTE-8C asks the next question: did the first real user experience stay clean enough to prepare a tiny controlled cohort?

## Current Observation Baseline

The REMOTE-8C baseline was started locally on 2026-05-17 after REMOTE-8B returned `GO_REMOTE8B_LIVE_PILOT_EVIDENCE_SAFE_NO_GIT_LEAK`. On 2026-05-18, ignored local evidence first returned `GO_REMOTE8C_STAY_ONE_USER_DECISION_RECORDED` with more than 24 clean observation hours, all required signals present, zero open support items and zero unresolved blockers.

The operator then explicitly changed the private decision to `expand_3_5` only to prepare REMOTE-8D. The rerun returned `GO_REMOTE8C_TINY_COHORT_EXPANSION_READY`. This does not invite users, create grants, send emails, publish checkout or share protected URLs; it only permits a manual REMOTE-8D package.

After REMOTE-ACCEPT1 returned `GO_REMOTE_ACCEPT1_BROWSER_ACCEPTANCE_CLEAN`, the local observation evidence marked the guided Welcome/Dashboard flow, app-session/entitlement path and tunnel stability as observed. The support loop was later confirmed through Control Panel support intake; the output-folder case was resolved as safe remote behavior because local server folders are intentionally not exposed to remote users.

Public-safe expansion-prep result:

- Status: `GO_REMOTE8C_TINY_COHORT_EXPANSION_READY`
- Observation window: `38.0` hours in ignored local evidence at the rerun time
- Requested decision: `expand_3_5`
- Missing signals: `0`
- Metric blockers: `0`
- Open support items: `0`
- Unresolved blockers: `0`
- Expansion package allowed: `true`
- Automation allowed: `false`

## Local Evidence Rule

Raw observation evidence must live only under ignored local paths:

- `.local/remote_service/remote8c_first_user_observation.local.json`
- `.local/remote_service/remote8c_first_user_observation/`

Tracked docs may contain only the schema, the validator contract and public-safe summaries. Never commit:

- raw emails;
- protected URLs;
- support transcripts;
- Cloudflare identifiers;
- payment payloads;
- session tokens;
- grant keys;
- local workspace paths;
- SQX local paths.

## Required Signals

The private observation JSON must confirm:

- `remote8bEvidenceGo`
- `firstUserCompletedGuidedFlow`
- `supportLoopObserved`
- `tunnelStable`
- `appSessionStable`
- `entitlementStable`
- `workspaceIsolationClean`
- `artifactGenerated`
- `exportDownloaded`
- `revocationRestoreConfidence`
- `noWorkspaceLeakage`
- `noSecurityIncidents`
- `noUnresolvedSupportBlockers`
- `supportEvidenceRedacted`
- `privateEvidenceStoredOutsideGit`

The observation window must be at least 24 hours.

## Support Intake

REMOTE-SUPPORT1 adds an in-app support intake under `Control Panel > Soporte` while preserving the REMOTE-8C one-user boundary. Cases use `support-incident-v1`, stay in ignored `.local/remote_service/support_cases/` evidence and can be summarized with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_support_status.ps1 -Json
```

Open cases or blocker cases must keep `openSupportItems` / `unresolvedBlockers` non-zero in private REMOTE-8C evidence until the operator resolves them. The support intake does not automatically flip `supportLoopObserved`, does not send email and does not create external tickets.

Operator-only status updates can be done locally without exposing the case to the tester UI:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_support_status.ps1 -SetStatusCase SQX-SUP-YYYYMMDDHHMMSS-xxxxxxxxxx -Status resolved -Note "Resolved after operator review." -Json
```

## Zero Tolerance Metrics

These values must be zero before a tiny cohort expansion can be prepared:

- `openSupportItems`
- `unresolvedBlockers`
- `tunnelDrops`
- `appSessionFailures`
- `workspaceLeakEvents`
- `securityIncidents`
- `generationFailures`
- `entitlementErrors`
- `refundRequests`

## Tool

Use the local-only ingest tool:

```powershell
python backend\sqx-edge-tool\tools\remote_first_user_observation.py `
  --evidence .local\remote_service\remote8c_first_user_observation.local.json `
  --out-dir .local\remote_service\remote8c_first_user_observation
```

The output is:

- `.local/remote_service/remote8c_first_user_observation/remote8c_first_user_observation.public.json`

The summary uses `remote-first-user-observation-v1`, redacts the pilot identity and keeps all support evidence private.

## Operator Status Helper

During the 24-hour observation window, use the local status helper for a short redacted summary:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote8c_observation_status.ps1 -Json
```

The helper wraps the same `remote_first_user_observation.py` ingest tool, writes only the redacted public summary under ignored `.local/remote_service/remote8c_first_user_observation/`, and prints whether REMOTE-8C is still blocked, valid-but-staying-at-one-user, or ready for a manual REMOTE-8D package. It must not print raw emails, protected URLs, grant keys, session tokens, support transcripts or local SQX paths.

## Possible Decisions

- `GO_REMOTE8C_TINY_COHORT_EXPANSION_READY`: evidence is clean, the operator requested `expand_3_5`, and only a manual next step is allowed.
- `GO_REMOTE8C_STAY_ONE_USER_DECISION_RECORDED`: evidence is valid but the operator chose to keep observing one user.
- `NO_GO_REMOTE8C_FIRST_USER_OBSERVATION_BLOCKED`: a required signal, metric, approval or observation window is not clean enough.

Even on GO, automation remains disabled:

- `decision.automationAllowed = false`
- `decision.manualOperatorStepRequired = true`

## Next Phase

`REMOTE-8D - Tiny Cohort Activation Package` should prepare, but not automatically execute, the safest package for 3-5 users: exact manual checklist, tester/paid entitlement boundaries, support expectations, rollback, pause rule and private communication copy.
