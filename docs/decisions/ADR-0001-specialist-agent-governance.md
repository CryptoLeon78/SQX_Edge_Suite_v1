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

## Consequences

- Future phases should declare active owner areas before implementation.
- Each work phase/message starts from Project Governance or the Specialist Agents ownership matrix.
- M46 should start from a defined customer cockpit data model and privacy boundary.
- Roadmap references should avoid ambiguous unprefixed phase numbers where possible.
- Documentation and tests become part of the phase deliverable, not cleanup after the fact.

## Verification

The decision is guarded by:

- `docs/PROJECT_GOVERNANCE.md`
- `backend/sqx-edge-tool/test_dashboard_static.py`
- `backend/sqx-edge-tool/test_packaging.py`
