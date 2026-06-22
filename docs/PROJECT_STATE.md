# docs/PROJECT_STATE.md - Cross-model routing & live deltas (model-neutral)

> Single source for **cross-model routing/handoff** and recent decisions. **Phase state is NOT here** - it stays authoritative in `PROJECT_GOVERNANCE.md` "## Current State" (test-enforced). Update at the close of each work unit; sign `model + date`. Governed by proposed **G7** (enforcement lands in Phase B); entry point `/AGENTS.md`.

## Phase state -> governance is authoritative
Current phase, governance baseline, commercial/product state and next-phase candidates live in `PROJECT_GOVERNANCE.md` "## Current State" (pinned by `test_dashboard_static.py`). This file does **not** duplicate them.

## Repository / CI reality (decided 2026-06-18; reflected in governance Living Contracts Index by Phase B / `docs/G7-phase-b`)
- **GitLab = primary** (work + CI): `git@gitlab.com:rafael_cto/sqx_pro.git` (private, SSH). `main` tracks `gitlab/main`. CI = `.gitlab-ci.yml` (Linux); the `e2e` job is `allow_failure` until promoted.
- **GitHub `origin` = mirror/publication** (passive); push works via the permitted GCM account — the 403 was a wrong cached account, fixed 2026-06-18; mirror synced to `main` (latest `eb473c5`). `.github/workflows/*` archived (`workflow_dispatch` + `if:false`), dormant.
- **`institutional`** remote not configured locally -> governance `G4/G5` are historical baselines (text preserved; pinned by the static test).
- Pushes via PowerShell on Windows (SSH key on Windows). Never git over the Cowork mount.

## Decisions / deltas (append-only, signed)
- 2026-06-21 - CF deploy token rotated: leaked `CLOUDFLARE_API_TOKEN` revoked, replaced with a fresh account-scoped token (GitLab CI var, masked+protected); deploy re-verified green with the old token revoked. GitHub mirror re-synced to `main` (`eb473c5`). - Claude
- 2026-06-21 - Portal hardened: `wrangler.jsonc` gets `workers_dev=true` + `preview_urls=false`; Cloudflare Access now enforced on `trading@`; per-version preview URL bypass closed (`fix/portal-preview-urls`, MR merged). - Claude
- 2026-06-19 - CI Cloudflare deploy circuit landed (bootstrap §11, previously unapplied): `deploy-portal` job (manual, on `main`) + `cf:deploy` npm script + `test_gitlab_ci_portal_deploy.py` smoke gate; OpenNext build-validate job added same day (`portal-build`, scoped to portal path). - Claude
- 2026-06-18 - GitLab migration done: 4 MRs merged to `main`; GitLab CI primary (e2e `allow_failure` until promoted). - Claude
- 2026-06-18 - Remote topology decided: GitLab primary, GitHub mirror, institutional historical. - user / Claude
- 2026-06-18 - Adopting multi-model orchestration (ADR-0002 Proposed + G7 pending). PROJECT_STATE owns routing; governance stays authoritative for phase state (test-locked). - Claude + GPT
- 2026-06-18 - MCP parked: original mandate was MicroStrategy/Strategy One, not SQX. - Claude
- 2026-06-18 - Phase B applied: `G7 - Multi-Model Orchestration Gate` baselined in `PROJECT_GOVERNANCE.md` (Current State + Operational Rule + Living Contracts CI/remotes) with MODULARIZATION baseline and the paired `test_dashboard_static.py` assert; full suite green (290 passed, 3 skipped); on `docs/G7-phase-b` (MR open). - Claude

## Routing / handoff queue (a model suggests; the user decides owner)
| Task | Status | Suggested | Owner (user) | Notes |
|---|---|---|---|---|
| Phase A (additive): AGENTS.md + ADR-0002 + PROJECT_STATE.md | done (MR !5) | claude | user | merged to main; `docs/INDEX.md` already exists (MR !4), untouched |
| Phase B (governance edit): G7 + baseline bump + CI/remote reality | done (MR open) | claude | user | applied on `docs/G7-phase-b`; gate + full suite green; user merges |
| Cross-ref AGENTS.md/PROJECT_STATE.md/ADR-0002 in existing `docs/INDEX.md` | pending | claude | - | Phase B; INDEX already maps verticals well |
| Decide GitHub workflow retention/removal | pending | either | - | mini Gxx/Qxx; `.github` is mirror/history, not casual cleanup |
| Configurable `:5050` port | pending | either | - | server.py + 2 configs + ~6 JS literals + relay + tests |
| Marker tagging `smoke`/`integration` (~280 tests) | pending | either | - | incremental |
| Flip `deploy-portal` to auto-on-main | pending | claude | - | remove `when: manual`; user decided auto-on-main |
| Author T10ai provider/preflight proof | pending | claude | - | `proof:cloudflare-provider-project-preflight` (current preflight is Vercel-era) |

## Suggested handoffs (pending the user's routing decision)
- (none)

## Pointers
- Operating model + phase state: `docs/PROJECT_GOVERNANCE.md`
- Entry point: `/AGENTS.md`
- Docs map: `docs/INDEX.md`
- Decisions: `docs/decisions/` (ADR-0001, ADR-0002 proposed)