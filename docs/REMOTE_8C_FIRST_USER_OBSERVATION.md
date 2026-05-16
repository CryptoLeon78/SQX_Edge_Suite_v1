# REMOTE-8C - First User Support Observation And Expansion Decision

REMOTE-8C turns the first real user's private support and stability evidence into a redacted decision. It does not create users, send invites, publish links, run checkout automation or change paid access by itself.

The phase exists after REMOTE-8B. REMOTE-8B proves that the private live smoke can be ingested safely. REMOTE-8C asks the next question: did the first real user experience stay clean enough to prepare a tiny controlled cohort?

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

## Possible Decisions

- `GO_REMOTE8C_TINY_COHORT_EXPANSION_READY`: evidence is clean, the operator requested `expand_3_5`, and only a manual next step is allowed.
- `GO_REMOTE8C_STAY_ONE_USER_DECISION_RECORDED`: evidence is valid but the operator chose to keep observing one user.
- `NO_GO_REMOTE8C_FIRST_USER_OBSERVATION_BLOCKED`: a required signal, metric, approval or observation window is not clean enough.

Even on GO, automation remains disabled:

- `decision.automationAllowed = false`
- `decision.manualOperatorStepRequired = true`

## Next Phase

`REMOTE-8D - Tiny Cohort Activation Package` should prepare, but not automatically execute, the safest package for 3-5 users: exact manual checklist, tester/paid entitlement boundaries, support expectations, rollback, pause rule and private communication copy.
