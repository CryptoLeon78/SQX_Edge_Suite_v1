# Modularization Next Steps

Persistent planning note for the next SQX Edge phases.

## Current Status

- Last updated: 2026-05-10.
- Current completed phase: T10al - Controlled Real App Deploy Gate.
- Current product/commercial state: `next_controlled_commercial_movement_from_m98_decision_ready`.
- Governance baseline: G6 - Institutional Dashboard Quick Actions Gate.
- Last synced base commit before S2/M-pre: `cc8dbf0`.
- Latest verified portable ZIP: `dist/SQX_Edge_Tool_Portable_20260509_102131.zip`.
- Latest ZIP SHA256: `18EC98981D8B52535E1FE26EA47876588FA2EB8321DD2A9706CBD30B6A0B7E5D`.
- Next recommended phase: T10am - execute one controlled real app deploy only with exact approval, immediate Access smoke and rollback on mismatch, M100 - execute exactly the M99-approved controlled commercial movement, R46 - publish the verified GitHub Release only with explicit approval, V10 - SQX Views pack comparison, or SB18 - Strategy Builder buyer evidence export polish.

## Historical State Anchors

- Current completed phase: T10l - Vercel Route Investigation. Historical anchor only; superseded by T10m.
- Next recommended phase: T10m - manual/API Vercel correction or alternative no-deploy route proof before any further deployment. Historical anchor only; superseded by T10n.
- Current completed phase: T10m - Vercel Config Hardening. Historical anchor only; superseded by T10n.
- Next recommended phase: T10n - no-deploy preview target proof or Vercel route replacement before any further deployment. Historical anchor only; superseded by T10o.
- Current completed phase: T10n - Vercel Route Decision. Historical anchor only; superseded by T10o.
- Next recommended phase: T10o - replacement route or provider-level no-deploy proof before any deployment. Historical anchor only; superseded by T10p.
- Current completed phase: T10o - Replacement Route Contract. Historical anchor only; superseded by T10p.
- Next recommended phase: T10p - create or verify a fresh staging route only after explicit approval and before any deployment. Historical anchor only; superseded by T10q.
- Current completed phase: T10p - Fresh Staging Route Preflight. Historical anchor only; superseded by T10q.
- Next recommended phase: T10q - request exact approval to create or verify a fresh protected staging route without deployment. Historical anchor only; superseded by T10r.
- Current completed phase: T10q - Fresh Staging Route Access Check. Historical anchor only; superseded by T10r.
- Next recommended phase: T10r - authenticate Vercel CLI or provide local `VERCEL_TOKEN`, then create or verify `sqx-edge-tester-staging` without deployment. Historical anchor only; superseded by T10s.
- Current completed phase: T10r - Fresh Staging Project Created. Historical anchor only; superseded by T10s.
- Next recommended phase: T10s - verify or enable protection/settings for `sqx-edge-tester-staging` before any Git link or deployment. Historical anchor only; superseded by T10t.
- Current completed phase: T10s - Staging Protection Verified. Historical anchor only; superseded by T10t.
- Next recommended phase: T10t - link or configure staging without deployment and without publishing a URL. Historical anchor only; superseded by T10u.
- Current completed phase: T10t - Staging Local Link Configured. Historical anchor only; superseded by T10u.
- Next recommended phase: T10u - prepare a no-deploy staging deployment readiness gate before any deployment. Historical anchor only; superseded by T10v.
- Current completed phase: T10u - Staging Deployment Readiness Gate. Historical anchor only; superseded by T10v.
- Next recommended phase: T10v - execute one controlled staging deployment attempt with immediate target/alias inspection and rollback on mismatch. Historical anchor only; superseded by T10w.
- Current completed phase: T10v - Controlled Staging Deploy Rollback. Historical anchor only; superseded by T10w.
- Next recommended phase: T10w - investigate/correct provider-level target mapping without another deployment attempt or replace the staging route. Historical anchor only; superseded by T10x.
- Current completed phase: T10w - Provider Target Mapping Investigation. Historical anchor only; superseded by T10x.
- Next recommended phase: T10x - execute one explicit preview-target deployment attempt with immediate target/alias inspection and rollback on mismatch. Historical anchor only; superseded by T10y.
- Current completed phase: T10x - Explicit Preview Target Rollback. Historical anchor only; superseded by T10y.
- Next recommended phase: T10y - stop retrying Vercel CLI deployment and choose a no-deploy route replacement or provider/dashboard correction decision. Historical anchor only; superseded by T10z.
- Current completed phase: T10y - No-Deploy Provider Dashboard Decision. Historical anchor only; superseded by T10z.
- Next recommended phase: T10z - prepare the no-deploy provider/dashboard correction package before any deployment attempt. Historical anchor only; superseded by T10aa.
- Current completed phase: T10z - Provider Dashboard Correction Package. Historical anchor only; superseded by T10aa.
- Next recommended phase: T10aa - record no-deploy provider/dashboard correction evidence before any deployment attempt. Historical anchor only; superseded by T10ab.
- Current completed phase: T10aa - Provider Dashboard Evidence Record. Historical anchor only; superseded by T10ab.
- Next recommended phase: T10ab - ingest manual dashboard evidence or replace the Vercel tester route before any deployment attempt. Historical anchor only; superseded by T10ac.
- Current completed phase: T10ab - Manual Dashboard Evidence Ingest. Historical anchor only; superseded by T10ac.
- Next recommended phase: T10ac - compare and select a protected non-Vercel tester route or local/private-network pilot without deployment. Historical anchor only; superseded by T10ad.
- Current completed phase: T10ac - Replacement Tester Route Options. Historical anchor only; superseded by T10ad.
- Next recommended phase: T10ad - prepare a no-deploy Cloudflare Access preflight package before any provider project, deployment or tester URL. Historical anchor only; superseded by T10ae.
- Current completed phase: T10ad - Cloudflare Access Preflight. Historical anchor only; superseded by T10ae.
- Next recommended phase: T10ae - decide and test Cloudflare runtime compatibility locally before any provider project, deployment or tester URL. Historical anchor only; superseded by T10af.
- Current completed phase: T10ae - Cloudflare Runtime Compatibility. Historical anchor only; superseded by T10af.
- Next recommended phase: T10af - prepare the local OpenNext/Cloudflare Workers adapter package without deployment or provider action. Historical anchor only; superseded by T10ag.
- Current completed phase: T10af - OpenNext Cloudflare Adapter Package. Historical anchor only; superseded by T10ag.
- Next recommended phase: T10ag - run the local OpenNext build/preview smoke without provider action. Historical anchor only; superseded by T10ah.
- Current completed phase: T10ag - OpenNext Local Smoke. Historical anchor only; superseded by T10ah.
- Next recommended phase: T10ah - evaluate and block the Next.js middleware-to-proxy migration for the current Cloudflare route. Historical anchor only; superseded by T10ai.
- Current completed phase: T10ah - Next Proxy Migration Gate. Historical anchor only; superseded by T10ai.
- Next recommended phase: T10ai - prepare the Cloudflare provider-project preflight without deployment or tester URL. Historical anchor only; superseded by T10aj.
- Current completed phase: T10ai - Cloudflare Provider Project Preflight. Historical anchor only; superseded by T10aj.
- Next recommended phase: T10aj - create or verify a Cloudflare project shell only with exact approval, otherwise keep the route local. Historical anchor only; superseded by T10ak.
- Current completed phase: T10aj - Cloudflare Project Shell Gate. Historical anchor only; superseded by T10ajb.
- Next recommended phase: T10ajb - resolve Cloudflare authentication or manually verify/create the provider shell without deployment. Historical anchor only; superseded by T10ajc.
- Current completed phase: T10ajb - Cloudflare Auth Handoff. Historical anchor only; superseded by T10ajc.
- Next recommended phase: T10ajc - ingest authenticated or manual Cloudflare shell evidence without deployment before T10ak. Historical anchor only; superseded by T10ajd.
- Current completed phase: T10ajc - Cloudflare Shell Evidence Ingest. Historical anchor only; superseded by T10ajd.
- Next recommended phase: T10ajd - capture real Cloudflare shell evidence manually/authenticated before T10ak. Historical anchor only; superseded by T10aje.
- Current completed phase: T10ajd - Cloudflare Shell Evidence Capture Checklist. Historical anchor only; superseded by T10aje.
- Next recommended phase: T10aje - execute manual Cloudflare login/dashboard evidence capture outside git, then rerun T10ajc ingest. Historical anchor only; superseded by T10ajf.
- Current completed phase: T10aje - Cloudflare Read-Only Shell Capture. Historical anchor only; superseded by T10ajf.
- Next recommended phase: T10ajf - choose exact no-deploy Cloudflare shell creation path or authorize one controlled deploy later. Historical anchor only; superseded by T10ajg.
- Current completed phase: T10ajf - Cloudflare Shell Creation Decision. Historical anchor only; superseded by T10ajg.
- Next recommended phase: T10ajg - prepare exact approval gate for the first Cloudflare Worker deploy/shell creation without tester URL sharing. Historical anchor only; superseded by T10ajh.
- Current completed phase: T10ajg - Cloudflare First Deploy Approval Gate. Historical anchor only; superseded by T10ajh.
- Next recommended phase: T10ajh - verify first Cloudflare Worker deploy readiness without deploy while waiting for exact approval. Historical anchor only; superseded by T10aji.
- Current completed phase: T10ajh - Cloudflare First Deploy Readiness. Historical anchor only; superseded by T10aji.
- Next recommended phase: T10aji - execute the first Cloudflare Worker deploy/shell creation only after approval and rollback if unsafe. Historical anchor only; superseded by T10ajj.
- Current completed phase: T10aji - Cloudflare First Deploy Rollback. Historical anchor only; superseded by T10ajj.
- Next recommended phase: T10ajj - decide/register the Cloudflare route or workers.dev onboarding path before any new deploy attempt. Historical anchor only; superseded by T10ajk.
- Current completed phase: T10ajj - Cloudflare Route Onboarding Decision. Historical anchor only; superseded by T10ajk.
- Next recommended phase: T10ajk - configure a protected Cloudflare custom route/domain or complete dashboard workers.dev onboarding with immediate Access precreate before any new deploy attempt. Historical anchor only; superseded by T10ajl.
- Current completed phase: T10ajk - Cloudflare Route Access Precreate. Historical anchor only; superseded by T10ajl.
- Next recommended phase: T10ajl - select private Cloudflare hostname/zone or complete workers.dev onboarding evidence before T10ak Access creation. Historical anchor only; superseded by T10ak.
- Current completed phase: T10ajl - Cloudflare Hostname Zone Selection. Historical anchor only; superseded by T10ajl2.
- Next recommended phase: T10ajl2 - prepare the local operator unlock kit for private Cloudflare hostname/zone evidence before T10ak. Historical anchor only; superseded by T10ajm.
- Current completed phase: T10ajl2 - Cloudflare Operator Unlock Kit. Historical anchor only; superseded by T10ajm.
- Next recommended phase: T10ajm - prepare the workers.dev shell gate because no custom domain and no Worker target exist yet. Historical anchor only; superseded by T10ajn.
- Current completed phase: T10ajm - Workers.dev Shell Gate. Historical anchor only; superseded by T10ajn.
- Next recommended phase: T10ajn - deploy the harmless workers.dev shell only with exact approval, then enable/verify Cloudflare Access before any tester URL. Historical anchor only; superseded by T10ajo.
- Current completed phase: T10ajn - Controlled Workers.dev Shell Deploy. Historical anchor only; superseded by T10ajo.
- Next recommended phase: T10ajo - enable or verify Cloudflare Access on the existing workers.dev shell via dashboard or Access API token before any real app deploy. Historical anchor only; superseded by T10ak.
- Current completed phase: T10ajo - Workers.dev Access Verified. Historical anchor only; superseded by T10ak.
- Next recommended phase: T10ak - record or verify the Cloudflare Access application/policy boundary for the protected workers.dev shell before any real app deploy. Historical anchor only; superseded by T10al.
- Current completed phase: T10ak - Access Policy Boundary. Historical anchor only; superseded by T10al.
- Next recommended phase: T10al - prepare the exact controlled real app deploy gate after Access app/policy boundary verification. Historical anchor only; superseded by T10am.
- Current completed phase: T10al - Controlled Real App Deploy Gate. Historical anchor only; superseded by T10am.

## Recommended Order

1. Phase 36: harden Project Generator module boundaries. Done.
2. Phase 37: split the remaining `main.js` orchestration into focused files. Done.
3. Phase 38: add more granular contracts per frontend submodule. Done.
4. Phase 39: regenerate and test the portable ZIP after modularization. Done.
5. Phase 40: document the final architecture map and load order. Done.
6. Phase 41: guard architecture load-order documentation with a living contract. Done.
7. Phase 42: reduce Project Generator legacy bridge with a focused DOM helper module. Done.
8. Phase 43: add a release checklist script for tests, portable packaging and ZIP validation. Done.
9. Phase 44: polish release flow with one-click strict release, summary output and package guardrails. Done.
10. Phase 45: extract Project Generator event bindings and polling from the legacy bridge. Done.
11. Phase 46: apply operational visual polish for Project Generator, Strategies and responsive dense views. Done.

## Project Generator Track

1. Phase PG1: add Custom Libre generation outside the plan mining while preserving plan-based bulk generation. Done.
2. Phase PG2: add reusable local custom presets for frequent buyer assets/timeframes. Done.
3. Phase PG3: add portable export/import JSON packs for custom preset portability between installations. Done.
4. Phase PG4: add starter custom preset examples by asset/timeframe profile with load/save/export flow. Done.
5. Phase PG5: add richer custom profile families or buyer-specific `.cfx` starter guidance if Project Generator continues. Done.
6. Phase PG6: add buyer-specific `.cfx` handoff notes or Project Generator pack import preview if this track continues. Done.
7. Phase PG7: add buyer-specific `.cfx` handoff notes with copy/download Markdown flow. Done; see `docs/PG7_PROJECT_GENERATOR_BUYER_CFX_HANDOFF.md`.

## Working Discipline

- Before every work phase/message, consult `docs/PROJECT_GOVERNANCE.md` or the Specialist Agents ownership matrix and state the active ownership/checks.
- Create a backup before changing files.
- Verify with JS contracts, Python tests, and E2E screenshots when frontend behavior is touched.
- Remove temporary Playwright dependencies after E2E.
- Use one commit per phase.
- Push immediately after every successful commit unless the user explicitly asks to hold the push or the remote is unavailable.
- Treat `https://github.com/CryptoLeon78/SQX_Institutional_Core.git` as first-class/original via local remote `institutional`; push it separately only when histories are aligned or after an explicit institutional sync phase.
- Never force-push `institutional/main` and never delete institutional-only files, workflows, analyzer assets or operating docs through a blind mirror push.
- Declare active specialist ownership before broad phases.
- Use prefixed phase IDs for new work: `Mxx`, `Axx`, `Rxx`, `Sxx`, `Qxx`, `Gxx`, `SBxx`, `Txx`.
- Use `Vxx` for SQX view/template generation and StrategyQuant operator tools.
- Follow `docs/PROJECT_GOVERNANCE.md` for phase workflow and M46 entry criteria.
- Apply G3 before adding internal automation: classify risk level, ownership, output path, privacy boundary and required checks.
- Keep external commercial actions manual unless the user approves the exact traffic, checkout, email, license, public release or buyer-contact action.
- Treat tester portal actions as external/security-sensitive: no Vercel deploy, tester account, password rotation, renewal email or public/protected URL publication without explicit approval for that exact action.

## Cloud Tester Access Track

1. Phase T1: define the Vercel-hosted tester architecture contract, repo boundaries, Access/Security Gatekeeper, 15-day renewal model and threat model. Done; see `docs/T1_CLOUD_TESTER_ARCHITECTURE_CONTRACT.md`.
2. Phase T2: create/private-bootstrap `SQX_Edge_Tester_Portal` with Next.js/Vercel structure, README, `.gitignore`, env placeholders and no real tester data. Done as public-safe template; see `docs/T2_TESTER_PORTAL_BOOTSTRAP.md` and `templates/SQX_Edge_Tester_Portal/`.
3. Phase T3: define tester auth data contract: statuses, password hash policy, sessions, renewal tokens, audit events and secret boundaries. Done; see `docs/T3_TESTER_AUTH_DATA_CONTRACT.md` and `templates/SQX_Edge_Tester_Portal/src/lib/auth-data-contract.ts`.
4. Phase T4: implement login/session prototype with blocked unauthenticated routes. Done; see `docs/T4_LOGIN_SESSION_PROTOTYPE.md` and `templates/SQX_Edge_Tester_Portal/src/lib/session-prototype.ts`.
5. Phase T5: add `tester_pro` entitlements and feature gates for paid options. Done; see `docs/T5_TESTER_PRO_ENTITLEMENT_GATES.md` and `templates/SQX_Edge_Tester_Portal/src/lib/entitlement-gates.ts`.
6. Phase T6: add 15-day expiry, renewal state and manual approve/deny flow. Done; see `docs/T6_15_DAY_EXPIRY_RENEWAL_FLOW.md` and `templates/SQX_Edge_Tester_Portal/src/lib/renewal-flow.ts`.
7. Phase T7: add admin tester console for create, renew, deny, block and audit review. Done; see `docs/T7_ADMIN_TESTER_CONSOLE.md` and `templates/SQX_Edge_Tester_Portal/src/lib/admin-console.ts`.
8. Phase T8: harden rate limiting, security headers, watermark, kill switch and deployment-protection checklist. Done; see `docs/T8_TESTER_PORTAL_SECURITY_HARDENING.md`, `templates/SQX_Edge_Tester_Portal/src/lib/security-hardening.ts` and `templates/SQX_Edge_Tester_Portal/src/lib/deployment-protection.ts`.
9. Phase T9: run Vercel preview staging behind protection with no public indexing, only with explicit approval for the exact external action. Preflight attempted; blocked safely by invalid local Vercel token; see `docs/T9_PROTECTED_VERCEL_PREVIEW_PREFLIGHT.md` and `templates/SQX_Edge_Tester_Portal/scripts/vercel-preview-preflight.mjs`.
10. Phase T9b: authenticate Vercel, verify Deployment Protection and execute protected preview deploy. Attempted; rolled back because CLI created production aliases; see `docs/T9B_VERCEL_PREVIEW_DEPLOY_ROLLBACK.md`.
11. Phase T9c: verify Vercel Deployment Protection before retrying preview deploy. Done as safe NO-GO gate; see `docs/T9C_VERCEL_DEPLOYMENT_PROTECTION_GATE.md` and `templates/SQX_Edge_Tester_Portal/scripts/vercel-protection-audit.mjs`.
12. Phase T9d: enable or verify Vercel Authentication/Password Protection privately, then retry preview only after `GO_PROTECTION_VERIFIED`. Done; see `docs/T9D_VERCEL_AUTH_PROTECTION_VERIFIED.md`.
13. Phase T9e: retry preview-only deploy with target and alias inspection before sharing any URL; rollback immediately if target or aliases are production. Attempted and rolled back; see `docs/T9E_PROTECTED_PREVIEW_DEPLOY_ROLLBACK.md`.
14. Phase T9f: prepare Git/PR-based preview or API deployment proof that cannot auto-alias production before any URL is shared. Done as a local no-deploy proof gate; see `docs/T9F_PREVIEW_PATH_PROOF.md` and `templates/SQX_Edge_Tester_Portal/scripts/vercel-preview-path-proof.mjs`.
15. Phase T9g: connect private Git/PR preview source before any tester URL is shared. Done; see `docs/T9G_PRIVATE_GIT_PREVIEW_SOURCE.md`.
16. Phase T10: run one internal tester pilot before inviting external testers. Attempted and rolled back because Vercel reported `target=production` from `tester-preview`; see `docs/T10_INTERNAL_PREVIEW_ROLLBACK.md`.
17. Phase T10b: fix Vercel preview target mapping before any tester URL is shared. Contained with a build-time guard; see `docs/T10B_VERCEL_TARGET_GUARD.md`.
18. Phase T10c: correct Vercel Git/preview mapping or define an explicit API preview path before any tester URL is shared. Done as no-deploy explicit API preview proof; see `docs/T10C_EXPLICIT_API_PREVIEW_PATH.md`.
19. Phase T10d: execute one explicit API preview deployment with target inspection before any tester URL is shared. Attempted and rolled back because Vercel returned `target = production`; see `docs/T10D_EXPLICIT_API_PREVIEW_ROLLBACK.md`.
20. Phase T10e: attempted an omitted-target API preview deployment and rolled it back because Vercel still returned `target = production`; see `docs/T10E_OMITTED_TARGET_PREVIEW_ROLLBACK.md`.
21. Phase T10f: recreate or separate the Vercel preview project before any tester URL is shared. Done as separated, undeployed preview project; see `docs/T10F_SEPARATED_PREVIEW_PROJECT.md`.
22. Phase T10g: link the private tester portal repository to the separated preview project and prove Git/protection settings without deploying. Done as linked no-deploy proof; see `docs/T10G_LINKED_PREVIEW_PROJECT_PROOF.md`.
23. Phase T10h: execute exactly one protected preview deployment from the separated project with immediate target inspection before any tester URL is shared. Attempted and rolled back because Vercel returned `target = production`; see `docs/T10H_PROTECTED_PREVIEW_DEPLOY_ROLLBACK.md`.
24. Phase T10i: correct or replace the Vercel preview deployment route before another deployment attempt. Done as CLI default preview route proof; see `docs/T10I_CLI_DEFAULT_PREVIEW_ROUTE.md`.
25. Phase T10j: execute exactly one CLI default preview deployment with immediate target inspection and rollback on mismatch. Attempted command was rejected before deployment because `--skip-domain` is production-only; see `docs/T10J_CLI_DEFAULT_PREVIEW_COMMAND_ROLLBACK.md`.
26. Phase T10k: execute exactly one CLI default preview deployment without `--skip-domain`, with immediate target inspection and rollback on mismatch. Attempted and rolled back because Vercel still returned `target = production`; see `docs/T10K_CLI_DEFAULT_PREVIEW_ROLLBACK.md`.
27. Phase T10l: investigate or replace the Vercel route without another deployment attempt. Done as no-deploy investigation with NO-GO route status; see `docs/T10L_VERCEL_ROUTE_INVESTIGATION.md`.
28. Phase T10m: manual/API Vercel correction or alternative no-deploy route proof before any further deployment. Done as Vercel Project API hardening without deployment; see `docs/T10M_VERCEL_CONFIG_HARDENING.md`.
29. Phase T10n: no-deploy preview target proof or Vercel route replacement before any further deployment. Done as route decision NO-GO for the current Vercel route; see `docs/T10N_VERCEL_ROUTE_DECISION.md`.
30. Phase T10o: replacement route or provider-level no-deploy proof before any deployment. Done as no-deploy replacement-route contract; see `docs/T10O_REPLACEMENT_ROUTE_CONTRACT.md`.
31. Phase T10p: create or verify a fresh staging route only after explicit approval, with no-deploy preflight before any deployment. Done as local no-external-action preflight; see `docs/T10P_FRESH_STAGING_ROUTE_PREFLIGHT.md`.
32. Phase T10q: request exact approval to create or verify a fresh protected staging route without deployment. Done as access check; write path blocked by CLI/token authentication; see `docs/T10Q_FRESH_STAGING_ROUTE_ACCESS_CHECK.md`.
33. Phase T10r: authenticate Vercel CLI or provide local `VERCEL_TOKEN`, then create or verify `sqx-edge-tester-staging` without deployment. Done; see `docs/T10R_FRESH_STAGING_PROJECT_CREATED.md`.
34. Phase T10s: verify or enable protection/settings for `sqx-edge-tester-staging` before any Git link or deployment. Done; see `docs/T10S_STAGING_PROTECTION_VERIFIED.md`.
35. Phase T10t: link or configure staging without deployment and without publishing a URL. Done; see `docs/T10T_STAGING_LOCAL_LINK_CONFIGURED.md`.
36. Phase T10u: prepare a no-deploy staging deployment readiness gate before any deployment. Done; see `docs/T10U_STAGING_DEPLOYMENT_READINESS_GATE.md`.
37. Phase T10v: execute one controlled staging deployment attempt with immediate target/alias inspection and rollback on mismatch. Done as clean rollback; see `docs/T10V_CONTROLLED_STAGING_DEPLOY_ROLLBACK.md`.
38. Phase T10w: investigate/correct provider-level target mapping without another deployment attempt or replace the staging route. Done as no-deploy route investigation; see `docs/T10W_PROVIDER_TARGET_MAPPING_INVESTIGATION.md`.
39. Phase T10x: execute one explicit preview-target deployment attempt with immediate target/alias inspection and rollback on mismatch. Done as clean rollback; see `docs/T10X_EXPLICIT_PREVIEW_TARGET_ROLLBACK.md`.
40. Phase T10y: stop retrying Vercel CLI deployment and choose a no-deploy route replacement or provider/dashboard correction decision. Done as provider-dashboard correction decision; see `docs/T10Y_NO_DEPLOY_PROVIDER_DASHBOARD_DECISION.md`.
41. Phase T10z: prepare the no-deploy provider/dashboard correction package before any deployment attempt. Done as correction package; see `docs/T10Z_PROVIDER_DASHBOARD_CORRECTION_PACKAGE.md`.
42. Phase T10aa: record no-deploy provider/dashboard correction evidence before any deployment attempt. Done as read-only evidence record with manual dashboard gap; see `docs/T10AA_PROVIDER_DASHBOARD_EVIDENCE_RECORD.md`.
43. Phase T10ab: ingest manual dashboard evidence or replace the Vercel tester route before any deployment attempt. Done as `NO_GO_REPLACE_VERCEL_TESTER_ROUTE`; see `docs/T10AB_MANUAL_DASHBOARD_EVIDENCE_INGEST.md`.
44. Phase T10ac: compare and select a protected non-Vercel tester route or local/private-network pilot without deployment. Done as Cloudflare Pages preview + Cloudflare Access email OTP candidate; see `docs/T10AC_REPLACEMENT_TESTER_ROUTE_OPTIONS.md`.
45. Phase T10ad: prepare a no-deploy Cloudflare Access preflight package before any provider project, deployment or tester URL. Done; see `docs/T10AD_CLOUDFLARE_ACCESS_PREFLIGHT.md`.
46. Phase T10ae: decide and test Cloudflare runtime compatibility locally before any provider project, deployment or tester URL. Done as Workers/OpenNext runtime selection; see `docs/T10AE_CLOUDFLARE_RUNTIME_COMPATIBILITY.md`.
47. Phase T10af: prepare the local OpenNext/Cloudflare Workers adapter package without deployment or provider action. Done; see `docs/T10AF_OPENNEXT_CLOUDFLARE_ADAPTER_PACKAGE.md`.
48. Phase T10ag: run the local OpenNext build/preview smoke without provider action. Done as WSL/Linux local smoke GO and native Windows preview NO-GO; see `docs/T10AG_OPENNEXT_LOCAL_SMOKE.md`.
49. Phase T10ah: evaluate and block the Next.js middleware-to-proxy migration for the current Cloudflare route. Done; see `docs/T10AH_NEXT_PROXY_MIGRATION.md`.
50. Phase T10ai: prepare the Cloudflare provider-project preflight without deployment or tester URL. Done; see `docs/T10AI_CLOUDFLARE_PROVIDER_PROJECT_PREFLIGHT.md`.
51. Phase T10aj: create or verify a Cloudflare project shell only with exact approval, otherwise keep the route local. Done as a guarded NO-GO because Wrangler is not authenticated locally and the no-deploy CLI path configures files rather than creating a provider shell; see `docs/T10AJ_CLOUDFLARE_PROJECT_SHELL.md`.
52. Phase T10ajb: resolve Cloudflare authentication or manually verify/create the provider shell without deployment. Done as auth/manual evidence handoff; local Wrangler is still unauthenticated and no provider resource was created; see `docs/T10AJB_CLOUDFLARE_AUTH_HANDOFF.md`.
53. Phase T10ajc: ingest authenticated or manual Cloudflare shell evidence without deployment and decide whether T10ak can be unlocked. Done as guarded NO-GO because no ignored local evidence exists and Wrangler remains unauthenticated; see `docs/T10AJC_CLOUDFLARE_SHELL_EVIDENCE_INGEST.md`.
54. Phase T10ajd: capture real Cloudflare shell evidence manually/authenticated before T10ak. Done as capture checklist/proof because Wrangler remains unauthenticated in Codex; see `docs/T10AJD_CLOUDFLARE_SHELL_EVIDENCE_CAPTURE.md`.
55. Phase T10aje: execute manual Cloudflare login/dashboard evidence capture outside git, then rerun T10ajc ingest. Done as read-only Wrangler capture; authenticated read confirms `sqx-edge-tester-portal-preview` does not exist, so T10ak stays blocked; see `docs/T10AJE_CLOUDFLARE_READONLY_SHELL_CAPTURE.md`.
56. Phase T10ajf: choose exact no-deploy Cloudflare shell creation path or authorize one controlled deploy later. Done as decision gate: no pure invisible shell path is accepted; first Worker creation must use an explicit `wrangler deploy`/C3 class external action because `wrangler versions upload` fails on first upload; see `docs/T10AJF_CLOUDFLARE_SHELL_CREATION_DECISION.md`.
57. Phase T10ajg: prepare exact approval gate for the first Cloudflare Worker deploy/shell creation without tester URL sharing. Done as approval gate only: exact command, manual approval phrase, pre-checks, post-checks and cleanup criteria are documented; see `docs/T10AJG_CLOUDFLARE_FIRST_DEPLOY_APPROVAL_GATE.md`.
58. Phase T10ajh: verify first Cloudflare Worker deploy readiness without deploy while waiting for exact approval. Done; see `docs/T10AJH_CLOUDFLARE_FIRST_DEPLOY_READINESS.md`.
59. Phase T10aji: execute the first Cloudflare Worker deploy/shell creation only after approval, then immediately inspect or clean up before any tester URL is shared. Done as rollback: Cloudflare requires workers.dev subdomain or route, versions/deployments briefly appeared, and the Worker was deleted; see `docs/T10AJI_CLOUDFLARE_FIRST_DEPLOY_ROLLBACK.md`.
60. Phase T10ajj: decide/register the Cloudflare route or workers.dev onboarding path before any new deploy attempt. Done as no-deploy route decision: prefer protected custom route/domain, disable `workers_dev` and `preview_urls`, and require T10ajk before any redeploy; see `docs/T10AJJ_CLOUDFLARE_ROUTE_ONBOARDING_DECISION.md`.
61. Phase T10ajk: configure a protected Cloudflare custom route/domain or complete dashboard `workers.dev` onboarding with immediate Access precreate before any new deploy attempt. Done as guarded NO-GO: Wrangler auth and Worker-not-found were verified, but no hostname/zone is selected, so Access precreate stays blocked; see `docs/T10AJK_CLOUDFLARE_ROUTE_ACCESS_PRECREATE.md`.
62. Phase T10ajl: select private Cloudflare hostname/zone or complete dashboard `workers.dev` onboarding evidence before T10ak Access creation. Done as public-safe evidence gate; T10ak remains blocked until ignored local evidence returns GO; see `docs/T10AJL_CLOUDFLARE_HOSTNAME_ZONE_SELECTION.md`.
62.1. Phase T10ajl2: add `prepare:cloudflare-hostname-zone-selection` and `docs/T10AJL_OPERATOR_UNLOCK_KIT.md` so the operator can create the ignored local evidence file and prove it contains no hostname, zone ID, tester URL, tester emails or tokens before T10ak.
63. Phase T10ak: create Cloudflare Access application and policy only with exact approval after the provider shell is verified. Blocked until ignored T10ajl evidence proves a private hostname/zone or protected workers.dev onboarding.
64. Phase T10al: execute one controlled Cloudflare Workers deployment only after shell + Access policy are verified, then inspect target, Access coverage and no custom/public domain before any tester URL.
65. Phase T10am: run protected-route E2E smoke: anonymous blocked by Cloudflare Access, app session required, expired/denied/blocked tester states, logout, watermark, health and noindex.
66. Phase T10an: prepare private tester onboarding packet without committing tester emails or URL.
67. Phase T11: roll out to up to 10 testers with monitored access and manual renewal.
68. Phase T12: monitor abuse, failed logins, access patterns and continue/stop decision.

## Governance Track

1. Phase G1: define specialist agent ownership, phase namespaces, workflow and M46 entry criteria. Done.
2. Phase G2: require governance/ownership lookup before each work phase/message. Done.
3. Phase G3: define internal automation risk levels, specialist-agent escalation rules, command matrix and local tooling notes. Done.
4. Phase G4: add Institutional Core as first-class repository discipline with separate non-destructive push rules. Done.
5. Phase G5: reconcile `institutional/main` with current `main` while preserving institutional-only assets before routine dual pushes. Done.
6. Phase G6: selectively integrate `institutional/feat/dashboard-quick-actions` as native quick actions, health panel and visual funnel without Top Picks/Matrix. Done.
7. Next governance option: keep dual-repo pushes aligned while choosing the next buyer-facing or commercial execution phase.

## Architecture / External Comparison Track

1. Phase A47: compare Jose Livan's `sqx-edge-pipeline` repo and integrate a first-party Plan Quality Advisor. Done.
2. Phase A48: recover valuable HTML-side capabilities as native UI: local state backup/restore, dynamic Plan v2 summary and a locked Priority multi-TF placeholder, explicitly excluding Top Picks and Matrix. Done.
3. Phase A49: convert multi-timeframe analytical scoring into a controlled, dependency-isolated backend tool that consumes supplied metric JSON files and emits TF scores plus weighted consensus. Done.
4. Phase A50: connect multi-timeframe consensus to plan review without changing the dashboard UI until real metrics are available. Done.
5. Phase A51: add a multi-timeframe metric gate for supplied `asset_metrics[_TF].json` folders before exposing or using them as first-party evidence. Done.
6. Phase A52: implement a first-party H1 metric source from existing dashboard scores, write provenance and validate it through the A51 gate without synthetic lower/higher TFs. Done.
7. Phase A53: add a controlled intake gate for real H1/M30/M15/H4 metric folders, with first-party H1 support and strict blocking for missing synthetic lower/higher TFs. Done.
8. Phase A54: connect a validated full multi-timeframe source to Plan Quality Advisor artifacts only after A53 returns GO, otherwise write a blocked NO-GO report. Done.
9. Phase A55: add an OHLC CSV metric builder that converts reviewable market CSVs into `asset_metrics[_TF].json` without synthetic timeframes. Done.
10. Phase A56: add an end-to-end real-data pipeline runner for OHLC CSV -> metrics -> intake -> guarded plan artifacts, returning GO only when every stage passes. Done.
11. Phase A57: expose read-only MTF evidence in dashboard only after A56 returns GO with real data. Done.
12. Phase A58: add an internal MT5/Dukascopy OHLC download gate that writes real CSVs for A55/A56 and stays excluded from buyer portable builds. Done.
13. Phase A59: run the first local A58 smoke against Dukascopy MT5 and record NO-GO if terminal/API readiness blocks real data. Done; see `docs/A59_REAL_DATA_VALIDATION.md`.
14. Phase A60: add active-terminal MT5 initialization mode, retry the smoke against the already-open terminal and record NO-GO if IPC still times out. Done; see `docs/A60_MT5_ACTIVE_TERMINAL_MODE.md`.
15. Phase A61: add a repeatable MT5 IPC diagnostic that records environment, process state and init variants before any full OHLC download. Done; see `docs/A61_MT5_IPC_DIAGNOSTIC.md`.
16. Phase A62: add controlled recent-bars download mode, align the MT5 symbol map to the product manifest universe, produce `EURUSD_H1.csv`, download the full configured OHLC universe and validate A56 GO. Done; see `docs/A62_RECENT_BARS_REAL_MTF_GO.md`.
17. Phase A63/R44: refresh the portable/release story after real A56 GO while keeping OHLC data, `analysis_output/` evidence and internal MT5 tools out of buyer builds. Done; see `docs/R44_A63_PORTABLE_AFTER_REAL_MTF_GO.md`.

## Champion vs Challenger Track

1. Phase J1: document the Champion vs Challenger integration contract from Jose's latest HTML work, including input schemas, aliases, parsing, scoring, OOS evidence, security boundaries and tests. Done; see `docs/J1_CHAMPION_CHALLENGER_CONTRACT.md`.
2. Phase J2: implement the pure parser, alias resolver and formal comparison core with contracts, without dashboard UI. Done; see `docs/J2_CHAMPION_CHALLENGER_CORE.md`.
3. Phase J3: add OOS block parsing and stability scoring with contracts. Done; see `docs/J3_CHAMPION_CHALLENGER_OOS.md`.
4. Phase J4: add native dashboard UI using the current SQX module architecture and visual system, without restoring removed Top Picks or Matrix surfaces. Done; see `docs/J4_CHAMPION_CHALLENGER_UI.md`.
5. Phase J5: add regime/EGT evidence through first-party historical-data adapters. Done; see `docs/J5_CHAMPION_CHALLENGER_REGIME_EGT.md`.
6. Phase J6: add export and future Strategy Builder handoff. Done; see `docs/J6_CHAMPION_CHALLENGER_EXPORT_HANDOFF.md`.
7. Phase J7: document the Temporal Health and EGT v2 contract from JoseLivan commit `06767d8`, preserving SQX architecture and excluding Top Picks/Matrix surfaces. Done; see `docs/J7_TEMPORAL_HEALTH_EGT_V2_CONTRACT.md`.
8. Phase J8: implement pure Temporal Health and EGT v2 helpers with JS contracts before UI changes. Done; see `docs/J8_TEMPORAL_HEALTH_EGT_V2_HELPERS.md`.
9. Phase J9: add compact dashboard chips and optional filters for Temporal Health and EGT v2. Done; see `docs/J9_TEMPORAL_HEALTH_EGT_V2_UI.md`.
10. Phase J10: extend redacted review export and Strategy Builder handoff with reduced Temporal Health and EGT v2 evidence. Done; see `docs/J10_TEMPORAL_HEALTH_EGT_V2_HANDOFF.md`.
11. Phase J11: add native direction detection, directional coherence, Score Pro and imported CVC evidence display inside Strategy Builder UI without changing generation gates. Done; see `docs/J11_DIRECTIONAL_COHERENCE_SCORE.md`.

## Strategy Builder / Only One Platform Track

1. Phase SB1: discover the minimum viable Strategy Builder scope as a commercial "only one platform" hook, starting from existing SQX indicators, project presets and strategy cleaner outputs. Done; see `docs/SB1_STRATEGY_BUILDER_DISCOVERY.md`.
2. Phase SB2: design a controlled Builder flow that creates a strategy idea/package without bypassing StrategyQuant validation. Done; see `docs/SB2_STRATEGY_BUILDER_WORKFLOW.md`.
3. Phase SB3: prototype read-only previews and export handoff artifacts before any live generation feature is offered to buyers. Done; see `docs/SB3_STRATEGY_BUILDER_PROTOTYPE.md`.
4. Phase SB4: harden Strategy Builder handoff import/export and decide whether it remains a tab or becomes a compact workflow panel. Done; see `docs/SB4_STRATEGY_BUILDER_IMPORT_EXPORT.md`.
5. Phase SB5: add Strategy Builder to Project Generator prefill bridge without auto-running generation. Done; see `docs/SB5_STRATEGY_BUILDER_PROJECT_GENERATOR_PREFILL.md`.
6. Phase SB6: add Strategy Builder review checklist and Project Generator save-as-preset handoff without auto-saving. Done; see `docs/SB6_STRATEGY_BUILDER_PRESET_HANDOFF.md`.
7. Phase SB7: add Strategy Builder SQX Views validation-pack handoff without auto-saving templates. Done; see `docs/SB7_STRATEGY_BUILDER_VIEWS_HANDOFF.md`.
8. Phase SB8: add Strategy Builder handoff audit trail and buyer workflow polish. Done; see `docs/SB8_STRATEGY_BUILDER_AUDIT_WORKFLOW.md`.
9. Phase SB9: add Strategy Builder Strategy Cleaner draft handoff. Done; see `docs/SB9_STRATEGY_BUILDER_CLEANER_HANDOFF.md`.
10. Phase SB10: add Strategy Builder unified buyer handoff pack. Done; see `docs/SB10_STRATEGY_BUILDER_BUYER_HANDOFF_PACK.md`.
11. Phase SB11: add Strategy Builder buyer handoff pack import and review. Done; see `docs/SB11_STRATEGY_BUILDER_BUYER_PACK_IMPORT_REVIEW.md`.
12. Phase SB12: add Strategy Builder guided buyer session checklist. Done; see `docs/SB12_STRATEGY_BUILDER_BUYER_SESSION_CHECKLIST.md`.
13. Phase SB13: add Strategy Builder buyer session handoff summary export. Done; see `docs/SB13_STRATEGY_BUILDER_BUYER_SESSION_SUMMARY_EXPORT.md`.
14. Phase SB14: add Strategy Builder buyer session printable operator notes. Done; see `docs/SB14_STRATEGY_BUILDER_BUYER_SESSION_PRINTABLE_NOTES.md`.
15. Phase SB15: add Strategy Builder buyer session support case bundle. Done; see `docs/SB15_STRATEGY_BUILDER_BUYER_SESSION_SUPPORT_CASE_BUNDLE.md`.
16. Phase SB16: add Strategy Builder buyer session support resolution checklist. Done; see `docs/SB16_STRATEGY_BUILDER_BUYER_SESSION_SUPPORT_RESOLUTION_CHECKLIST.md`.
17. Phase SB17: add Strategy Builder buyer session evidence handoff index. Done; see `docs/SB17_STRATEGY_BUILDER_EVIDENCE_HANDOFF_INDEX.md`.
18. Phase SB18: add Strategy Builder buyer evidence export polish if this track continues.

## QA / Security Track

1. Phase Q1: add GitHub Actions baseline plus root development requirements for Python tests and JS contracts. Done.
2. Phase S1: define private commercial repository boundary, manifest and ignored local staging paths. Done.
3. Phase S2/M-pre: prepare private commercial docs split with export tool, SHA256 migration index and public traceability plan. Done.
4. Phase S3/M-pre: initialize the ignored private commercial export as a local git repository with publication and security instructions. Done.
5. Phase S4/M-pre: create the private GitHub repository and push private export commit `ed79719`. Done.
6. Phase S5/M-pre: replace public sensitive commercial docs and Pro resource packs with traceability pointers. Done.

## Monetization Track

1. Phase M1: define monetization model for SQX Edge Pro subscription, services and templates. Done.
2. Phase M2: design licensing and access model. Done.
3. Phase M3: define distribution channels and paid delivery flow. Done.
4. Phase M4: separate Free/Pro/internal product packaging. Done.
5. Phase M5: prepare branding and go-to-market assets. Done.
6. Phase M6: run security and distribution audit. Done.
7. Phase M7: design support and diagnostics flow. Done.
8. Phase M8: implement offline signed license activation. Done.
9. Phase M9: prepare production license key management and release guardrails. Done.
10. Phase M10: add manual Pro license issuer for first paid sales. Done.
11. Phase M11: prepare checkout wiring and manual sales fulfillment. Done.
12. Phase M12: prepare local webhook-to-fulfillment automation bridge. Done.
13. Phase M13: add private receiver with persistent queue and deduplication. Done.
14. Phase M14: add operator states, retries and dashboard queue cockpit. Done.
15. Phase M15: add trusted relay ingest for remote webhook forwarding. Done.
16. Phase M16: add deployable remote relay service with queue and dispatch. Done.
17. Phase M17: harden relay deployment with config checks, operator token and worker. Done.
18. Phase M18: add relay observability, snapshots and simulated purchase flow. Done.
19. Phase M19: prepare production relay deployment package and provider runbook. Done.
20. Phase M20: add relay staging validation kit and go/no-go checklist. Done.
21. Phase M21: choose Render staging path and add evidence go/no-go collector. Done.
22. Phase M22: add Render API preflight for key, owner and blueprint validation. Done.
23. Phase M23: add Render credential handshake and no-password guardrail. Done.
24. Phase M24: add Render staging go/no-go gate before live deployment. Done.
25. Phase M25: add Render staging launch pack for audited manual deployment. Done.
26. Phase M26: add Render staging secrets kit for safe provider setup. Done.
27. Phase M27: add local ingest tunnel readiness check before Render staging. Done.
28. Phase M28: add local ingest tunnel launcher and provider detection. Done.
29. Phase M29: add local ingest staging session orchestrator. Done.
30. Phase M30: add local ingest Render handoff pack. Done.
31. Phase M31: add Render staging apply gate for handoff confirmation and remote gate evidence. Done.
32. Phase M32: add Render staging purchase drill for webhook, queue and dispatch evidence. Done.
33. Phase M33: add checkout live readiness gate for Lemon Squeezy URLs, variants and rollback. Done.
34. Phase M34: add commercial release candidate gate for ZIP, readiness, pilot purchase and rollback evidence. Done.
35. Phase M35: add pilot purchase kit for private checkout, license issue, delivery and import evidence. Done.
36. Phase M36: add limited public launch gate for first sale cap, support, checkout and rollback evidence. Done.
37. Phase M37: add post-launch control for sales, activations, support, refunds and scale decision evidence. Done.
38. Phase M38: add commercial feedback loop for issue classification, pricing, copy and version decisions. Done.
39. Phase M39: add public offer pack for controlled offer copy, FAQ, release notes and buyer steps. Done.
40. Phase M40: add launch assets kit for screenshots, copy, release draft and publication checklist. Done.
41. Phase M41: add public release gate for tag, GitHub Release, ZIP, SHA256, support and rollback. Done.
42. Phase M42: add release publication record for published tag, release, ZIP, SHA256 and rollback evidence. Done.
43. Phase M43: add post-release monitor for incidents, activation errors, support, refunds and scale decision. Done.
44. Phase M44: add hotfix/rollback release kit for action owner, notes, comms, verification and closure evidence. Done.
45. Phase M45: add customer success and renewal loop for Pro onboarding, support outcomes, retention decisions and upsell evidence. Done.
46. Phase M46: add a lightweight commercial customer cockpit for renewals, support state, template opportunities and customer success decisions. Done.
47. Phase M47: prepare real Pro buyer data and templates with safe CSV import, asset universe, activation, support and first-value material. Done.
48. Phase M48: add a basic buyer onboarding and support gate for purchase, install, license activation, FAQ, support macro and refund/pause criteria. Done.
49. Phase M49: package Template Pack 1 as a controlled add-on with sample profiles, safe claims, delivery checklist and support boundaries. Done.
50. Phase M50: prepare public add-on offer, checkout variant wiring and delivery macro for Template Pack 1. Done.
51. Phase M51: connect real checkout URL, variant ID and support email through a controlled publication gate. Done.
52. Phase M52: run a controlled Template Pack 1 purchase drill and validate delivery/support evidence. Done.
53. Phase M53: execute post-purchase handoff, support follow-up and scale/pause decision. Done.
54. Phase M54: consolidate a lightweight add-on sales register before wider public traffic. Done.
55. Phase M55: review the add-on buyer cohort and real feedback before expanding traffic or building Template Pack 2. Done.
56. Phase M56: turn feedback into an offer iteration or Template Pack 2 action plan. Done.
57. Phase M57: execute the selected action plan as Template Pack 2 initial specs with scope, assets, support, delivery and next phase. Done.
58. Phase M58: create Template Pack 2 initial assets from the specs gate. Done.
59. Phase M59: prepare Template Pack 2 offer pack with public copy, FAQ, checkout draft, delivery macro and support macro. Done.
60. Phase M60: prepare controlled Template Pack 2 publication with live checkout URL, support, rollback and purchase drill. Done.
61. Phase M61: execute Template Pack 2 controlled purchase drill with redacted payment, delivery, support and refund/pause evidence. Done.
62. Phase M62: prepare Template Pack 2 post-purchase handoff, first-value support and scale/pause decision. Done.
63. Phase M63: consolidate Template Pack 2 sales register and early cohort tracking before more traffic. Done.
64. Phase M64: review Template Pack 2 early buyer feedback, support signals, refunds and scale decision. Done.
65. Phase M65: close buyer-ready checkout, release, support and delivery readiness for controlled first sales. Done.
66. Phase M66: prepare public buyer page checklist and a calm first-sale operating cadence. Done.
67. Phase M67: prepare first controlled buyer operating log and lightweight post-sale review. Done.
68. Phase M68: prepare a small post-sale improvement loop for onboarding, support macros and public copy. Done.
69. Phase M69: apply approved buyer-facing micro-updates and prepare the next controlled buyer readiness check. Done.
70. Phase M70: run the next controlled buyer readiness check before sharing another private checkout link. Done.
71. Phase M71: record the next controlled buyer outcome and decide repeat, pause or carefully widen. Done.
72. Phase M72: execute the selected outcome decision with a tiny, reversible distribution step. Done.
73. Phase M73: review controlled distribution evidence and choose repeat, hold, pause or prepare the next buyer-facing asset. Done.
74. Phase M74: prepare the next buyer-facing asset if M73 selects it, or route to repeat/hold/pause. Done.
75. Phase M75: privately review the prepared buyer-facing asset before publication or traffic. Done.
76. Phase M76: prepare a controlled publication gate only if M75 selects it. Done.
77. Phase M77: prepare a limited publication draft only if M76 selects it. Done.
78. Phase M78: review the limited publication draft before any manual publication. Done.
79. Phase M79: record a manual limited publication only if M78 approves. Done.
80. Phase M80: monitor the manual limited publication before any traffic expansion. Done.
81. Phase M81: review controlled traffic expansion only if M80 selects it. Done.
82. Phase M82: execute one tiny reversible traffic expansion step only if M81 approves it. Done.
83. Phase M83: monitor the tiny controlled traffic expansion step before repeating, pausing or widening again. Done.
84. Phase M84: decide repeat, hold, pause or prepare the next private review from M83 evidence. Done.
85. Phase M85: execute only the approved M84 operator decision. Done.
86. Phase M86: monitor the M85 execution result before any further movement. Done.
87. Phase M87: decide next controlled commercial movement from M86 evidence. Done.
88. Phase M88: execute only the approved controlled commercial next movement. Done.
89. Phase M89: monitor the M88 execution result before any broader commercial movement. Done.
90. Phase M90: decide the next controlled commercial movement from M89 evidence. Done.
91. Phase M91: execute only the M90-approved controlled commercial movement. Done.
92. Phase M92: monitor the M91 execution result before any additional movement. Done.
93. Phase M93: decide the next controlled commercial movement from M92 evidence. Done.
94. Phase M94: execute only the M93-approved controlled commercial movement. Done.
95. Phase M95: monitor the M94 execution result before any additional movement. Done.
96. Phase M96: decide the next controlled commercial movement from M95 monitor evidence. Done.
97. Phase M97: execute exactly the M96-approved controlled commercial movement. Done; see `docs/MONETIZATION_M97.md`.
98. Phase M98: monitor the M97 execution result before any additional commercial movement. Done; see `docs/MONETIZATION_M98.md`.
99. Phase M99: decide the next controlled commercial movement from M98 monitor evidence. Done; see `docs/MONETIZATION_M99.md`.
100. Phase M100: execute exactly the M99-approved controlled commercial movement.

## Active Cloudflare Tester Route

1. Phase T10ajl: select private Cloudflare hostname/zone or complete dashboard `workers.dev` onboarding evidence before T10ak Access creation. Done as public-safe evidence gate.
2. Phase T10ajl2: add `prepare:cloudflare-hostname-zone-selection` to create the ignored local evidence file. Done.
3. Phase T10ajm: prepare a controlled workers.dev shell gate because there is no custom domain and no Worker target to protect yet. Done.
4. Phase T10ajn: deploy only the harmless workers.dev shell with exact approval, then enable/verify Cloudflare Access before any tester URL. Done as shell-created, Access-permission blocked.
5. Phase T10ajo: enable or verify Cloudflare Access on the existing workers.dev shell via dashboard or Access API token. Done as Access-protected shell verification.
6. Phase T10ak: record/verify the Cloudflare Access application and policy boundary only after the shell target exists and Access coverage is verified. Done as private boundary evidence with no real app deploy.
7. Phase T10al: prepare the exact controlled real app deploy gate after Access app/policy boundary verification. Done as exact-approval gate, no deploy.
8. Phase T10am: execute one controlled real app deploy only with exact approval, immediate Access smoke and rollback on mismatch. Next.

## SQX View Creator Track

1. Phase V1: integrate the annual SQX `.vw` creator as a native dashboard tab with EGT Core preset, XML preview and portable download. Done.
2. Phase V2: add saved view presets and reusable operator templates in localStorage. Done.
3. Phase V3: add JSON export/import packs for saved SQX Views presets. Done.
4. Phase V4: add optional handoff links from Workflow/Estrategias and richer saved-template guidance. Done.
5. Phase V5: close the native SQX View Creator integration, archive the staging prototype in backup and remove the local staging folder. Done.
6. Phase V6: add buyer-ready SQX View template examples for first review, robustness, risk and full audit, with load/save/export flow. Done.
7. Phase V7: expand SQX Views packs by buyer profile, asset family or validation workflow if the View Creator track continues. Done.
8. Phase V8: add asset-family or validation-workflow packs if SQX Views continues. Done.
9. Phase V9: add SQX Views import preview or pack comparison if this track continues. Done.
10. Phase V10: add SQX Views pack comparison if this track continues.

## Release Track

1. Phase R40: regenerate and test the portable ZIP after V6/PG3 because frontend behavior and dev tooling changed. Done.
2. Phase R41: regenerate and test the portable ZIP after PG4 because frontend behavior changed. Done.
3. Phase R42: regenerate and validate a fresh portable release candidate after V9. Done.
4. Phase R43: prepare a public GitHub Release record only when we decide to publish the verified ZIP.
5. Phase R44: regenerate and validate the portable ZIP after real A56 GO, with broad generated-evidence exclusions. Done; see `docs/R44_A63_PORTABLE_AFTER_REAL_MTF_GO.md`.
6. Phase R45: prepare a controlled GitHub Release/publication plan for the verified ZIP without publishing it. Done; see `docs/R45_CONTROLLED_PUBLICATION_PLAN.md`.
7. Phase R46: publish the verified GitHub Release only with explicit approval, then run `release_publication_record.py`.
8. Phase R47: regenerate and validate a controlled commercial release candidate after Strategy Builder buyer-session support phases. Done; see `docs/R47_CONTROLLED_COMMERCIAL_RELEASE.md`.
