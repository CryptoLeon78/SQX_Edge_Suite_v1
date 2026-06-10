# TL1 Tester Launch Candidate

## Objective

TL1 freezes the fine-grained T10 tester gates and replaces the next movement with one human-sized launch candidate decision: are we ready to let the first private testers use the tool, yes or no?

This phase is intentionally macro-level. It does not add another public URL, does not create tester accounts, does not email testers, does not deploy, does not rotate passwords and does not publish private evidence. It only gives the operator a single safe proof and a short checklist.

## Launch Candidate Boundary

The tester launch candidate is ready only when all checks below are true in private evidence outside Git:

- Protected Cloudflare Access path is verified privately.
- The protected tester URL is known privately and is not committed.
- Tester login, active access and blocked states are smoke-tested privately.
- At least one active tester path is confirmed privately.
- Expired, denied or blocked tester states are confirmed privately.
- Admin/operator review path is ready privately.
- Support channel, rollback plan and launch message are ready privately.
- No tester emails, URL, hostname, credentials, account IDs, Access IDs, screenshots, raw feedback or private notes are committed.

## Private Local Launch File

If the operator wants a single go/no-go answer, create this ignored file only:

```text
templates/SQX_Edge_Tester_Portal/tester-launch-candidate.local.json
```

It may contain booleans, one safe enum and small counts only. It must not contain:

- Tester emails, names, passwords, reset links or access codes.
- URL, hostname, domain, route or workers.dev address.
- Account IDs, Access IDs, deployment IDs, version IDs or policy IDs.
- Tokens, API keys, private keys, cookies or session values.
- Screenshots, image paths, raw feedback text, private bug text, private action text, private execution text, private result text, private decision text, private iteration plan text, private support notes, tester identities, chat links, support links, distribution links or meeting links.

## Accepted Fields

The evidence file may use only these fields:

- `phase`: `TL1`.
- `launchMode`: one of `hold`, `first_private_tester`, `micro_cohort`, `pause`.
- Boolean checks: `protectedAccessVerifiedPrivately`, `protectedTesterUrlKnownPrivately`, `testerUrlKeptOutsideGit`, `testerAuthSmokePassedPrivately`, `activeTesterPathVerifiedPrivately`, `blockedStatesVerifiedPrivately`, `adminReviewReadyPrivately`, `supportChannelReadyPrivately`, `rollbackPlanReadyPrivately`, `launchMessageReadyPrivately`, `operatorApprovalReadyPrivately`, `publicRepoContainsTesterEmails`, `publicRepoContainsTesterUrl`, `publicRepoContainsCredentials`, `publicRepoContainsProviderIds`, `publicRepoContainsScreenshots`, `publicRepoContainsRawFeedback`, `publicRepoContainsPrivateNotes`.
- Count checks: `privateTesterCount`, `activePathSmokeCount`, `blockedStateSmokeCount`, `openP0Count`, `openP1Count`, `failedCheckCount`.

Counts must be non-negative integers no greater than 50.

## Expected Results

Without the ignored local launch-candidate file, the expected guarded result is:

```text
NO_GO_TESTER_LAUNCH_PRIVATE_EVIDENCE_MISSING
```

With safe private launch evidence and no public leak, the expected result is:

```text
GO_TESTER_LAUNCH_CANDIDATE_READY_NO_GIT_LEAK
```

Unsafe evidence must fail closed and stop the launch.

## Operator Meaning

`GO_TESTER_LAUNCH_CANDIDATE_READY_NO_GIT_LEAK` means the product is ready for a controlled private tester launch. It still does not mean public release, public URL publication, public marketing, GitHub Release publication, buyer onboarding or automatic outreach.

## Next Real Action

After TL1 is committed, the next real action is operational, not another microphase:

1. Fill `tester-launch-candidate.local.json` privately.
2. Run `npm run proof:tester-launch-candidate`.
3. If it returns GO, send the protected URL and access instructions manually to the chosen testers outside Git.
4. If it returns NO_GO, fix the private blocker directly and rerun the same proof.
