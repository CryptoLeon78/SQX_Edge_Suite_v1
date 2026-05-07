# SQX Edge Project Governance

Documento vivo para coordinar agentes especializados, ownership por area y reglas de fase antes de continuar con M46.

## Current State

- Current phase completed: M62 - Template Pack 2 Post-Purchase Handoff.
- Current product/commercial state: `template_pack_2_handoff_ready`.
- Next implementation phase: M63 - Template Pack 2 Sales Register.
- Governance baseline: G2 - Governance Lookup Before Work.
- Previous governance baseline: G1 - Specialist Agent Operating Model.

## Specialist Agents

| Agent | Scope | Primary Ownership | Required Checks |
| --- | --- | --- | --- |
| Frontend/UI | Dashboard, responsive UI, tabs, JS modules, visual state. | `app/SQX_Dashboard_v6.html`, `app/css`, `app/js`, `tests/js`, `tests/ui_e2e`. | JS contracts, Python static tests, E2E screenshots when UI changes. |
| Backend/API | Local Flask API, core business logic, manifests, local persistence. | `backend/sqx-edge-tool/api`, `backend/sqx-edge-tool/core`, `backend/sqx-edge-tool/config`, backend tests. | Backend pytest suite, API tests, manifest/static tests when contracts change. |
| QA/Release | Portable ZIP, release checklist, audit, START/STOP, SHA256 evidence. | `backend/sqx-edge-tool/tools/package_portable.ps1`, `audit_distribution.ps1`, `release_checklist.ps1`, launchers, `dist` evidence. | Full pytest, JS contracts, `git diff --check`, release checklist for ZIP phases. |
| Monetization/Product | Pro offer, pricing, support, renewal, buyer journey, safe claims. | `docs/MONETIZATION_ROADMAP.md`, `docs/MONETIZATION_M*.md`, `docs/sales`, product manifest, README. | Commercial docs tests, safe-claims review, roadmap/status alignment. |
| Security/Distribution | Secrets, license material, relay exposure, packaging exclusions. | `.gitignore`, product manifest security, packaging/audit scripts, relay settings, license manager. | Packaging tests, audit rules, sensitive-file staged review. |
| Architecture/Docs | Load order, module contracts, ADRs, ownership matrix, roadmap hygiene. | `docs/ARCHITECTURE.md`, `docs/PROJECT_GOVERNANCE.md`, `docs/decisions`, roadmap docs, module contracts. | Static docs tests, load-order contracts, roadmap consistency checks. |

## Phase Namespaces

Use clear prefixes so technical, commercial and release phases do not collide:

Use prefixed phase IDs for new work.

- `Mxx`: monetization and commercial product phases.
- `Axx`: architecture, modularization and technical structure phases.
- `Rxx`: release, packaging and distribution phases.
- `Sxx`: security and distribution hardening phases.
- `Qxx`: test, QA and observability hardening phases.
- `Gxx`: governance, ownership and decision-process phases.

Legacy references such as "Phase 46" in the modularization track remain historical. New work should use the prefix in titles and commits when practical.

## Operational Rule

G2 - Governance Lookup Before Work:

- Before every work phase/message, consult `docs/PROJECT_GOVERNANCE.md` or the Specialist Agents ownership matrix.
- Declare active ownership, expected touched areas and required checks before implementation when work is more than a direct answer.
- If specialized agents are available and the user asks for agent consultation, use them for bounded review or execution tasks that match the ownership matrix.
- If no specialized agent is needed, explicitly use Project Governance as the source of ownership and verification discipline.

## Phase Workflow

Every implementation phase must follow this loop:

1. Consult Project Governance or the Specialist Agents ownership matrix before every work phase/message.
2. Confirm working tree state.
3. Create a backup before changing files.
4. Define active agent ownership and expected touched areas.
5. Implement narrowly against the phase objective.
6. Update docs, manifests and tests in the same phase when contracts move.
7. Run required checks for touched areas.
8. Run E2E screenshots when frontend behavior or `manifest-data.js` changes.
9. Clean temporary Playwright/npm artifacts.
10. Commit once per phase after verification.
11. Push only when explicitly requested.

## M46 Entry Criteria

M46 is accepted when these criteria are true:

- Customer cockpit source of truth: local `customer_success_renewal` evidence plus `customer_cockpit.json` metadata.
- Data privacy boundary: no license payloads, private keys, raw checkout events or relay secrets in the UI.
- Ownership: Product defines fields, Backend owns persistence/API, Frontend owns cockpit UI, Security owns redaction/exclusions, QA owns tests.
- GO/NO-GO criteria: customers listed, renewal window visible, activation/support state visible, expansion opportunity visible, safe claims preserved.
- Test plan: JS contracts, backend pytest, static tests, E2E screenshots if cockpit UI is added.

## Living Contracts Index

- Frontend load order: `docs/ARCHITECTURE.md` and `backend/sqx-edge-tool/test_dashboard_static.py`.
- Manifest mirror: `backend/sqx-edge-tool/tools/build_frontend_manifest.py` and `app/js/manifest-data.js`.
- Product/commercial state: `backend/sqx-edge-tool/config/product_manifest.json`.
- Portable distribution: `package_portable.ps1`, `audit_distribution.ps1`, `release_checklist.ps1`.
- Commercial gates: `backend/sqx-edge-tool/tools/*` and `docs/sales/*`.
- Roadmap state: `docs/MODULARIZATION_NEXT_STEPS.md` and `docs/MONETIZATION_ROADMAP.md`.

## Security Notes

- Never commit `backend/sqx-edge-tool/config/license.json`.
- Never package private keys, signed customer licenses, fulfillment events, relay data, `.env` files, backups or internal release tools.
- Any new internal M46+ tool must be added to product manifest exclusions, packaging exclusions, audit deny-lists, release checklist assertions and tests.
