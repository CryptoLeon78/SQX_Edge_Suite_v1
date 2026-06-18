# docs/PROJECT_STATE.md - Cross-model routing & live deltas (model-neutral)

> Single source for **cross-model routing/handoff** and recent decisions. **Phase state is NOT here** - it stays authoritative in `PROJECT_GOVERNANCE.md` "## Current State" (test-enforced). Update at the close of each work unit; sign `model + date`. Governed by proposed **G7** (enforcement lands in Phase B); entry point `/AGENTS.md`.

## Phase state -> governance is authoritative
Current phase, governance baseline, commercial/product state and next-phase candidates live in `PROJECT_GOVERNANCE.md` "## Current State" (pinned by `test_dashboard_static.py`). This file does **not** duplicate them.

## Repository / CI reality (decided 2026-06-18; to be reflected in governance Living Contracts Index - Phase B)
- **GitLab = primary** (work + CI): `git@gitlab.com:rafael_cto/sqx_pro.git` (private, SSH). `main` tracks `gitlab/main`. CI = `.gitlab-ci.yml` (Linux); the `e2e` job is `allow_failure` until promoted.
- **GitHub `origin` = mirror/publication**; push 403-blocked for the active account. `.github/workflows/tests.yml` dormant.
- **`institutional`** remote not configured locally -> governance `G4/G5` are historical baselines (text preserved; pinned by the static test).
- Pushes via PowerShell on Windows (SSH key on Windows). Never git over the Cowork mount.

## Decisions / deltas (append-only, signed)
- 2026-06-18 - GitLab migration done: 4 MRs merged to `main`; GitLab CI primary (e2e `allow_failure` until promoted). - Claude
- 2026-06-18 - Remote topology decided: GitLab primary, GitHub mirror, institutional historical. - user / Claude
- 2026-06-18 - Adopting multi-model orchestration (ADR-0002 Proposed + G7 pending). PROJECT_STATE owns routing; governance stays authoritative for phase state (test-locked). - Claude + GPT
- 2026-06-18 - MCP parked: original mandate was MicroStrategy/Strategy One, not SQX. - Claude

## Routing / handoff queue (a model suggests; the user decides owner)
| Task | Status | Suggested | Owner (user) | Notes |
|---|---|---|---|---|
| Phase A (additive): AGENTS.md + ADR-0002 + PROJECT_STATE.md | in-progress | claude | - | 3 new files; `docs/INDEX.md` already exists (MR !4), untouched; -> flip to done on merge |
| Phase B (governance edit): G7 + baseline bump + CI/remote reality | pending | claude | - | edits test-locked docs -> gate = `test_dashboard_static.py` green before push |
| Cross-ref AGENTS.md/PROJECT_STATE.md/ADR-0002 in existing `docs/INDEX.md` | pending | claude | - | Phase B; INDEX already maps verticals well |
| Decide GitHub workflow retention/removal | pending | either | - | mini Gxx/Qxx; `.github` is mirror/history, not casual cleanup |
| Configurable `:5050` port | pending | either | - | server.py + 2 configs + ~6 JS literals + relay + tests |
| Marker tagging `smoke`/`integration` (~280 tests) | pending | either | - | incremental |

## Suggested handoffs (pending the user's routing decision)
- (none)

## Pointers
- Operating model + phase state: `docs/PROJECT_GOVERNANCE.md`
- Entry point: `/AGENTS.md`
- Docs map: `docs/INDEX.md`
- Decisions: `docs/decisions/` (ADR-0001, ADR-0002 proposed)