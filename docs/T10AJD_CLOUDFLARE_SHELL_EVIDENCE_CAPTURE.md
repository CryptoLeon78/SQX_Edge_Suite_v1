# T10ajd Cloudflare Shell Evidence Capture Checklist

## Objective

T10ajd prepares the exact manual/authenticated capture needed to unblock T10ajc without letting Codex create Cloudflare resources. This is still a no-deploy, no-Access-policy, no-tester-URL and no-tester-account phase.

## Current Probe

```text
npm exec --yes wrangler@latest -- whoami
result=not_authenticated
```

Because Wrangler is not authenticated in this workspace, Codex cannot capture real provider evidence directly.

## Official Sources Checked

- Wrangler command index: https://developers.cloudflare.com/workers/wrangler/commands/
- Wrangler Workers commands: https://developers.cloudflare.com/workers/wrangler/commands/workers/
- Cloudflare Access self-hosted applications: https://developers.cloudflare.com/cloudflare-one/applications/configure-apps/self-hosted-apps/
- Cloudflare Access policies: https://developers.cloudflare.com/cloudflare-one/policies/access/

## Manual Capture Checklist

Run outside Codex, in a normal terminal/browser session:

```powershell
cd <private repo root>\templates\SQX_Edge_Tester_Portal
npm exec --yes wrangler@latest -- login
npm exec --yes wrangler@latest -- whoami
Copy-Item cloudflare-shell-evidence.example.json cloudflare-shell-evidence.local.json
```

Then fill only this ignored local file:

```text
templates/SQX_Edge_Tester_Portal/cloudflare-shell-evidence.local.json
```

Allowed fields:

```json
{
  "projectShellName": "sqx-edge-tester-portal-preview",
  "shellVerified": true,
  "deploymentCreated": false,
  "accessApplicationCreated": false,
  "accessPolicyCreated": false,
  "customDomainAttached": false,
  "testerUrlPublished": false,
  "testerAccountsCreated": false,
  "testerEmailsIncluded": false
}
```

Forbidden in local evidence:

- tokens
- account IDs
- zone IDs
- tester emails
- tester URLs
- screenshots or copied account details

## Result

```text
NO_GO_CLOUDFLARE_CAPTURE_PENDING_MANUAL_AUTH_OR_DASHBOARD_EVIDENCE
```

T10ajd does not unlock T10ak. It makes the manual action exact enough that T10ajc can validate it mechanically afterward.

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
T10aje_manual_cloudflare_evidence_capture_then_t10ajc_ingest
```

After the ignored local evidence exists, rerun:

```powershell
npm run proof:cloudflare-shell-evidence-ingest
```

If it returns `GO_CLOUDFLARE_SHELL_EVIDENCE_VERIFIED_T10AK_READY_FOR_EXACT_APPROVAL`, then T10ak can be proposed. It still requires exact approval before creating any Access application or policy.

## Verification

T10ajd is accepted when:

- this document exists
- `scripts/cloudflare-shell-evidence-capture-proof.mjs` exists
- `package.json` exposes `proof:cloudflare-shell-evidence-capture`
- the proof returns `NO_GO_CLOUDFLARE_CAPTURE_PENDING_MANUAL_AUTH_OR_DASHBOARD_EVIDENCE`
- no deploy script is added
- no provider token, account ID, tester email or tester URL appears in tracked files
- static tests and full pytest pass
- `git diff --check` passes
