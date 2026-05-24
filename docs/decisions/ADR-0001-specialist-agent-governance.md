# ADR-0001 - Specialist Agent Governance

Date: 2026-05-07

Status: Accepted

## Context

SQX Edge has grown from a dashboard into a portable product with backend API, modular frontend, licensing, fulfillment, relay deployment, release gates and commercial support flows.

The project now needs clearer ownership before adding M46, because future work touches product, UI, backend, release, security and documentation at the same time.

## Decision

Adopt a specialist-agent operating model with six persistent roles:

- Frontend/UI
- Backend/API
- QA/Release
- Monetization/Product
- Security/Distribution
- Architecture/Documentation

Use prefixed phase namespaces for new work:

- `Mxx` for monetization/commercial phases.
- `Axx` for architecture/modularization phases.
- `Rxx` for release/packaging phases.
- `Sxx` for security/distribution hardening phases.
- `Qxx` for testing/QA phases.
- `Gxx` for governance/process phases.

The first governance baseline is G1: Specialist Agent Operating Model.

G2 extends the baseline with a mandatory governance lookup: before every work phase/message, consult `docs/PROJECT_GOVERNANCE.md` or the Specialist Agents ownership matrix, then derive active ownership, touched areas and required checks from that source.

G3 extends the baseline with an internal automation and agent gate. Internal automation is allowed when it reduces repeated checks, protects contracts, writes reproducible local evidence or prevents docs/tests/manifest drift. External commercial actions remain manual unless the user explicitly approves the exact action.

G9 extends the baseline with per-message specialist activation and session bootstrap. Each user message triggers a lightweight specialist-fit check across available agents/skills; each new chat/session starts with a concise project-state bootstrap from tracked governance sources before implementation work.

## Consequences

- Future phases should declare active owner areas before implementation.
- Each work phase/message starts from Project Governance or the Specialist Agents ownership matrix.
- Internal automations must declare risk level, output path, privacy boundary and required checks before commit.
- Specialist agents should be used for bounded review or execution slices, not as vague background work.
- Specialist use is proactive but bounded: Codex remains orchestrator, permissions do not expand automatically, and backup/diff/confirmation gates continue to govern all mutations.
- New session bootstrap reports current phase, next exact block, open fronts, gates and immediate verification risks before non-trivial work.
- M46 should start from a defined customer cockpit data model and privacy boundary.
- Roadmap references should avoid ambiguous unprefixed phase numbers where possible.
- Documentation and tests become part of the phase deliverable, not cleanup after the fact.

## Verification

The decision is guarded by:

- `docs/PROJECT_GOVERNANCE.md`
- `backend/sqx-edge-tool/test_dashboard_static.py`
- `backend/sqx-edge-tool/test_packaging.py`
