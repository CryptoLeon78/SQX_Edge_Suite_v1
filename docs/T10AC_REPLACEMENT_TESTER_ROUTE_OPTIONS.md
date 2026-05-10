# T10ac Replacement Tester Route Options

## Objective

T10ac compares replacement tester routes after T10ab rejected the current Vercel path.

This is a no-deploy decision phase. It does not create accounts, does not create projects, does not connect repositories, does not publish URLs and does not invite testers.

## Official Sources Checked

- Cloudflare Pages preview deployments: https://developers.cloudflare.com/pages/configuration/preview-deployments/
- Cloudflare Pages branch deployment controls: https://developers.cloudflare.com/pages/configuration/branch-build-controls/
- Cloudflare Access one-time PIN login: https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/one-time-pin/
- Netlify Password Protection overview: https://docs.netlify.com/manage/security/secure-access-to-sites/password-protection/
- Render Static Sites: https://render.com/docs/static-sites/

## Evaluation

| Route | Fit | Pros | Blocking Concerns |
| --- | --- | --- | --- |
| Cloudflare Pages + Cloudflare Access OTP | High | Preview deployments are separate from production; preview access can be protected with Access; preview indexing is blocked by default; branch controls can limit preview behavior; OTP supports approved email access without a shared password. | Requires Cloudflare account setup and careful Access policy. Preview access policy alone does not automatically protect every production/custom-domain surface, so T10ad must explicitly scope protected surfaces. |
| Netlify deploy previews + Password Protection | Medium-low | Mature deploy previews and built-in password/team login options. | Basic password is shared, which conflicts with per-tester identity. Team login is mainly for team members, not lightweight external testers. |
| Render static site / PR previews | Medium-low | Static sites and PR previews are straightforward, with TLS and DDoS protection. | The reviewed static-site docs do not show an equivalent first-party per-tester access gate. We would rely more heavily on our own app auth or another protection layer. |
| Local/private-network pilot | Medium | Safest for a very small internal pilot, no public cloud URL. | Poor fit for 10 external testers and weak as a commercial distribution rehearsal. |
| Current Vercel staging route | Rejected | Existing project and CLI are available. | Repeated controlled attempts returned `target=production`; T10ab manual evidence did not prove branch-target safety. |

## Decision

```text
GO_CLOUDFLARE_ACCESS_OTP_ROUTE_SELECTED_NO_DEPLOY
```

Selected route:

```text
cloudflare_pages_preview_with_cloudflare_access_email_otp
```

Rationale:

- It best matches the desired tester model: email-based individual access, 15-day renewal decisions and no shared password.
- It gives a second security layer outside our own tester portal auth.
- It offers a clearer preview-versus-production model than the rejected Vercel route.
- It keeps the project in a static/Next-compatible deployment family without forcing a backend rewrite.

## T10ad Entry Gate

```text
T10ad_cloudflare_access_preflight_no_deploy
```

T10ad must be a no-deploy Cloudflare preflight package unless Ivan explicitly approves a specific external action later.

T10ad must define:

- Cloudflare account and project naming without creating a deployment.
- Production branch must be `main`.
- Tester branch must be `tester-preview`.
- Preview branch controls must include only the intended tester branch.
- No custom domain until Access coverage is proven.
- Access policy must use individual approved emails or an equivalent identity provider group.
- OTP or equivalent identity provider must be configured before any tester surface exists.
- Own app auth remains mandatory; Cloudflare Access is an outer gate, not the only gate.
- No production database, real tester accounts, tester emails in git, renewal emails or public URL.

## Security Boundary

- No Cloudflare project was created.
- No Cloudflare deployment was created.
- No Cloudflare Access application or policy was created.
- No Netlify or Render project was created.
- No repository was connected to a new provider.
- No tester URL was shared.
- No tester accounts were created.
- No tester emails were committed.
- No production database was connected.

## Verification

T10ac is accepted when:

- this document exists
- `scripts/replacement-tester-route-options-proof.mjs` exists
- `package.json` exposes `proof:replacement-tester-route-options`
- the proof returns `GO_CLOUDFLARE_ACCESS_OTP_ROUTE_SELECTED_NO_DEPLOY`
- docs and roadmap point to T10ad as a no-deploy Cloudflare preflight package
- static tests assert that Vercel remains rejected and no provider project/deployment was created
- sensitive scan finds no tester emails, secrets or deployment URLs in touched public files
- `git diff --check` passes
