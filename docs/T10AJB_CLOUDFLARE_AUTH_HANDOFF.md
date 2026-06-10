# T10ajb Cloudflare Auth Handoff

## Objective

T10ajb turns the blocked T10aj shell gate into a repeatable, safe handoff for Cloudflare authentication or manual shell evidence, without deploying, without creating Cloudflare Access, without publishing a tester URL and without creating testers.

## Current Probe

```text
npm exec --yes wrangler@latest -- whoami
result=not_authenticated
```

No Cloudflare authentication is available to Codex in this workspace, and no `CLOUDFLARE_API_TOKEN` or `CLOUDFLARE_ACCOUNT_ID` value is committed or requested.

## Official Sources Checked

- Wrangler command index: https://developers.cloudflare.com/workers/wrangler/commands/
- Wrangler Workers commands: https://developers.cloudflare.com/workers/wrangler/commands/workers/
- Cloudflare API token management: https://developers.cloudflare.com/fundamentals/api/get-started/create-token/
- Cloudflare Access application configuration: https://developers.cloudflare.com/cloudflare-one/applications/configure-apps/

## Safe Operator Choices

Option A: browser login, run locally by Ivan:

```powershell
cd <private repo root>\templates\SQX_Edge_Tester_Portal
npm exec --yes wrangler@latest -- login
npm exec --yes wrangler@latest -- whoami
```

Option B: temporary local API token, never committed:

```powershell
[Environment]::SetEnvironmentVariable("CLOUDFLARE_API_TOKEN", "paste-token-only-in-your-local-terminal", "Process")
npm exec --yes wrangler@latest -- whoami
Remove-Item Env:\CLOUDFLARE_API_TOKEN
```

Option C: manual dashboard evidence without CLI auth:

1. Verify whether a Cloudflare Workers shell named `sqx-edge-tester-portal-preview` exists.
2. Confirm it has no deployment/version serving tester traffic.
3. Confirm no Access application or policy exists yet.
4. Confirm no custom domain or tester URL has been shared.
5. Copy `cloudflare-shell-evidence.example.json` to `cloudflare-shell-evidence.local.json` and fill only booleans and non-sensitive labels.

## Local Evidence Boundary

Tracked example:

```text
templates/SQX_Edge_Tester_Portal/cloudflare-shell-evidence.example.json
```

Ignored local evidence:

```text
templates/SQX_Edge_Tester_Portal/cloudflare-shell-evidence.local.json
```

The local evidence file must not contain:

- Cloudflare tokens
- account IDs
- zone IDs
- tester emails
- tester URLs
- screenshots with private account details

## Result

```text
NO_GO_CLOUDFLARE_AUTH_HANDOFF_PENDING_MANUAL_LOGIN_OR_EVIDENCE
```

T10ajb is a real operational step because it removes ambiguity and defines exactly how to unblock the shell verification without weakening the no-deploy/no-tester boundary.

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
T10ajc_ingest_cloudflare_shell_evidence_no_deploy
```

T10ajc may ingest either authenticated `wrangler whoami` confirmation plus shell evidence or the ignored local manual evidence file. T10ak remains blocked until T10ajc verifies the real provider shell.

## Verification

T10ajb is accepted when:

- this document exists
- `cloudflare-shell-evidence.example.json` exists
- `cloudflare-shell-evidence.local.json` is ignored
- `scripts/cloudflare-auth-handoff-proof.mjs` exists
- `package.json` exposes `proof:cloudflare-auth-handoff`
- the proof returns `NO_GO_CLOUDFLARE_AUTH_HANDOFF_PENDING_MANUAL_LOGIN_OR_EVIDENCE`
- no deploy script is added
- no provider token, account ID, tester email or tester URL appears in tracked files
- static tests and full pytest pass
- `git diff --check` passes
