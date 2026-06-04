# SQX Docs Canonical Index

Marker: `sqx-edge.docs-canonical-index-v1`

Phase: `A66 Docs Canonicalization`

Status: `completed_docs_canonical_index`

Last updated: 2026-06-04

## Purpose

A66 defines which SQX documentation is canonical, which documentation is historical/reference, and how to resolve conflicts before any future docs movement. It is an index and policy pass only. No docs moved during A66. No docs deleted during A66. No mass docs rehome during A66.

## Canonical Lookup Order

Use this order when a task depends on project state, phase status, architecture, roadmap or prior decisions:

1. gbrain page `projects/sqx-edge-suite-v1` for durable curated project memory.
2. `docs/PROJECT_GOVERNANCE.md` for live operational state, gates, blockers and current next step.
3. `docs/RESTRUCTURING_GOVERNANCE.md` for A64-A69 restructuring phase state.
4. `docs/DOCS_CANONICAL_INDEX.md` for docs canonicalization and historical/reference policy.
5. `docs/state_consistency_manifest.json` for machine-checked markers that must not drift.
6. `README.md` and `CHANGELOG.md` for public/current operator-facing summaries.
7. Domain docs named by the current governance entry for the specific feature, gate or runbook.

If these sources disagree, the newer live governance entry and state manifest win over older phase closeouts. Preserve the older document as history; update the canonical pointer or manifest in a later small phase.

## Canonical Core Docs

| Doc | Role | A66 decision |
| --- | --- | --- |
| `docs/PROJECT_GOVERNANCE.md` | Live operating state and gates | Canonical current-state source. |
| `docs/RESTRUCTURING_GOVERNANCE.md` | A64-A69 restructuring register | Canonical restructuring source. |
| `docs/DOCS_CANONICAL_INDEX.md` | Docs canonicalization index | Canonical docs-policy source. |
| `docs/TOOLING_OWNERSHIP_MAP.md` | Tooling/wrapper ownership map | Canonical tooling ownership source. |
| `docs/DISCIPLINA_OPERATIVA.md` | Operational discipline and institutional workflow policy | Canonical discipline source after A68; root `DISCIPLINA_OPERATIVA.md` is compatibility shim only. |
| `docs/state_consistency_manifest.json` | Literal state-marker test contract | Canonical drift guard. |
| `README.md` | Public/operator state summary | Canonical summary, not exhaustive source. |
| `CHANGELOG.md` | Phase closeout chronology | Canonical chronology of completed changes. |
| `docs/PUBLIC_ROADMAP.md` | Public-safe roadmap framing | Canonical public roadmap when current governance points to it. |
| `docs/MODULARIZATION_NEXT_STEPS.md` | Architecture/restructuring planning bridge | Canonical planning bridge for A64-A69 until superseded. |
| `docs/ARCHITECTURE.md` | Architecture map/load-order reference | Canonical architecture reference when current governance does not supersede it. |

## Canonical Domain Families

These families remain tracked and public-safe unless a later gate says otherwise. They are canonical only for their current domain when linked from governance, README, changelog or state manifest.

| Family | Examples / patterns | Canonical use |
| --- | --- | --- |
| SQX142/SQX144 compatibility and runbooks | `docs/SQX142_*.md`, `docs/SQX144_*.md`, `docs/maintenance/*.md` | Current when the active governance entry references the doc. |
| Remote/tester/commercial gates | `docs/REMOTE_*.md`, `docs/T*.md`, `docs/TL*.md`, `docs/MONETIZATION_*.md` | Current only for the latest gate named by governance. Older gates are historical. |
| Portfolio/Capa2/methodology | `docs/PHASE30_*.md`, `docs/SQX142_PORTFOLIO_*.md`, correlation/C2 docs | Current when tied to Portfolio Master inputs-pending or active Capa2 state. |
| Product/UX feature tracks | `docs/UI_*.md`, `docs/UX_*.md`, `docs/J*.md`, `docs/SB*.md`, `docs/PG*.md`, `docs/WFCO_*.md` | Current for the latest accepted surface only; older UX experiments are historical anchors. |
| Release/readiness/packaging | `docs/R*.md`, `docs/RELEASE_*.md`, `docs/*READINESS*.md` | Current only for the active release/readiness route named by governance. |

## Historical And Reference Policy

- Historical phase closeouts remain tracked as evidence and should not be rewritten just to match current wording.
- A historical document does not become current simply because it is newer than an older file in the same family; current status must be named in governance, README, changelog or the manifest.
- Long gate series such as `MONETIZATION_M1..M99`, `T10*`, `J*`, `SB*`, `PG*` and older `REMOTE*` entries are reference history unless the live governance entry selects one.
- Historical docs may contain superseded phase names, older routes or retired UI language. Do not use them to override live gates.
- If a historical doc contains unsafe public content, create a small redaction phase; do not hide the issue by moving the file during A66.

## Movement Gate

A66 creates index rules only. Physical docs movement requires a later phase with:

- explicit source and destination list;
- link/reference check;
- state manifest update;
- privacy scan;
- one domain per commit;
- rollback path.

Next restructuring phase: `A67 Tooling Ownership Map`.

## A66 Closeout

A66 Docs Canonicalization completed as `sqx-edge.docs-canonical-index-v1` with a canonical core-doc list, domain family policy and historical/reference conflict rules. No docs moved during A66. No docs deleted during A66. No mass docs rehome during A66.

## A68 Closeout

A68 Low-Risk Physical Moves completed as `completed_low_risk_physical_move` with one docs-domain relocation: `docs/DISCIPLINA_OPERATIVA.md` is the canonical operational discipline document and root `DISCIPLINA_OPERATIVA.md` is a compatibility shim. No tools moved, no wrappers moved, no scripts executed, no import or load-order changes and no runtime behavior changes during A68.

## A69 Closeout

A69 Major Refactor Decision Gate completed as `completed_major_refactor_decision_no_go`. The A64-A69 restructuring cycle closes without approving a major backend/frontend/tests separation because `REMOTE-8K Post Execution Monitoring` and the `SQX142-AW-AI2` install/manual roundtrip remain open. Future restructuring needs a new explicit phase plan after those gates close.
