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

G9R hardens the runtime behavior for automatic compaction and lazy tools. When the operator explicitly asks for G9, subagents, delegation or parallel agent work, Codex must expose Multi-agent tools through `tool_search` if they are not already available, spawn independent subagent tasks in the same round when they materially help, continue non-overlapping local orchestration work while they run, and store only a short sanitized `.local/agent_handoffs/` summary when their result affects the next action.

G10 refreshes the project and installed Codex agent layer after SQX144 Full was confirmed as the primary host. Agents and subagents must bootstrap with SQX144 Full / `sqx144_full` as confirmed primary, SQX142 Codex/QXPRO as preserved local diagnostic and methodology material but not active fallback, SQX143 as historical-only after local cleanup, and SQX144 144.2953 as a separate `SQX144-FULL-UPDATE2` gate.

## Consequences

- Future phases should declare active owner areas before implementation.
- Each work phase/message starts from Project Governance or the Specialist Agents ownership matrix.
- Internal automations must declare risk level, output path, privacy boundary and required checks before commit.
- Specialist agents should be used for bounded review or execution slices, not as vague background work.
- Specialist use is proactive but bounded: Codex remains orchestrator, permissions do not expand automatically, and backup/diff/confirmation gates continue to govern all mutations.
- New session bootstrap reports current phase, next exact block, open fronts, gates and immediate verification risks before non-trivial work.
- Parallel subagent claims require actual Multi-agent runtime use, not just reading skill text; compaction recovery revalidates G9 from tracked docs/manifest and reloads tools when needed.
- G10 keeps the installed Codex AGENTS/skills and project docs aligned with the active SQX host posture before any subagent work starts.
- Subagent handoffs are local ignored summaries, not memory stores: role, scope, result and next action only.
- M46 should start from a defined customer cockpit data model and privacy boundary.
- Roadmap references should avoid ambiguous unprefixed phase numbers where possible.
- Documentation and tests become part of the phase deliverable, not cleanup after the fact.

## Verification

The decision is guarded by:

- `docs/PROJECT_GOVERNANCE.md`
- `docs/state_consistency_manifest.json`
- `backend/sqx-edge-tool/test_dashboard_static.py`
- `backend/sqx-edge-tool/test_packaging.py`
