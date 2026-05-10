# T10ajc Cloudflare Shell Evidence Ingest

## Objective

T10ajc ingests the Cloudflare shell evidence route prepared by T10ajb and decides whether the project shell is verified enough to unlock T10ak. This phase remains no-deploy, no-Access-policy, no-tester-URL and no-tester-account.

## Inputs Checked

```text
templates/SQX_Edge_Tester_Portal/cloudflare-shell-evidence.local.json
result=missing

npm exec --yes wrangler@latest -- whoami
result=not_authenticated
```

The tracked example exists and remains public-safe:

```text
templates/SQX_Edge_Tester_Portal/cloudflare-shell-evidence.example.json
```

## Official Sources Checked

- Wrangler Workers commands: https://developers.cloudflare.com/workers/wrangler/commands/workers/
- Wrangler command index: https://developers.cloudflare.com/workers/wrangler/commands/
- Cloudflare Access policies: https://developers.cloudflare.com/cloudflare-one/policies/access/
- Cloudflare Access self-hosted applications: https://developers.cloudflare.com/cloudflare-one/applications/configure-apps/self-hosted-apps/

## Required Evidence For GO

T10ak can be unlocked only when the ignored local evidence or authenticated provider evidence proves:

- `projectShellName` is `sqx-edge-tester-portal-preview`.
- `shellVerified` is `true`.
- `deploymentCreated` is `false`.
- `accessApplicationCreated` is `false`.
- `accessPolicyCreated` is `false`.
- `customDomainAttached` is `false`.
- `testerUrlPublished` is `false`.
- `testerAccountsCreated` is `false`.
- `testerEmailsIncluded` is `false`.

## Result

```text
NO_GO_CLOUDFLARE_SHELL_EVIDENCE_MISSING_T10AK_BLOCKED
```

The result is a safe NO-GO because no ignored local evidence file exists and Wrangler remains unauthenticated. T10ak must not begin until real shell evidence is captured and ingested.

## Security Boundary Preserved

- No Cloudflare project was created.
- No Cloudflare deployment was created.
- No Cloudflare Access application was created.
- No Cloudflare Access policy was created.
- No GitHub repository was connected to Cloudflare.
- No Cloudflare token or account ID was committed.
- No tester URL was published.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.

## Next Gate

```text
T10ajd_capture_real_cloudflare_shell_evidence_no_deploy
```

T10ajd is not a deployment phase. It is the manual/authenticated evidence capture needed before T10ak can be considered.

## Verification

T10ajc is accepted when:

- this document exists
- `scripts/cloudflare-shell-evidence-ingest-proof.mjs` exists
- `package.json` exposes `proof:cloudflare-shell-evidence-ingest`
- the proof returns `NO_GO_CLOUDFLARE_SHELL_EVIDENCE_MISSING_T10AK_BLOCKED`
- `cloudflare-shell-evidence.local.json` remains ignored
- no deploy script is added
- no provider token, account ID, tester email or tester URL appears in tracked files
- static tests and full pytest pass
- `git diff --check` passes
