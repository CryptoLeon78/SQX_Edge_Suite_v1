# ADR-0002 - Multi-Model Orchestration

Date: 2026-06-18
Status: Proposed
Extends: ADR-0001 (adds multi-model coordination; records the 7th specialist role)

## Context
SQX Edge is operated by interchangeable LLM orchestrators (Claude, OpenAI Codex/GPT, and future models), routed by the user. ADR-0001 defined specialist-agent roles and phase namespaces for a single implementing agent consulting governance. It does not cover coordination *between* models: two orchestrators can drift, repeat work, or both edit state. Separately, since ADR-0001 governance grew from 6 to 7 specialist roles (added `Access/Security Gatekeeper`) without a recording decision.

## Decision
1. Operate with multiple interchangeable model-orchestrators. Model identity is **orthogonal** to specialist-agent ownership: any model may act as any specialist role; ADR-0001 ownership and required checks still apply.
2. The **user is the router**. A model may *suggest* a handoff to another model but never self-assigns; the user decides the owner.
3. **Single source per concern, no duplication.** Cross-model routing/handoff lives in `docs/PROJECT_STATE.md`. Phase state stays authoritative in `PROJECT_GOVERNANCE.md` "Current State" (test-enforced by `test_dashboard_static.py`); `PROJECT_STATE.md` points to it rather than copying it.
4. `AGENTS.md` (repo root) is the model-neutral entry point: it routes any agent to read `PROJECT_GOVERNANCE.md`, `docs/PROJECT_STATE.md` and `docs/INDEX.md` before work. It restates nothing.
5. **Session ritual:** at start read governance + PROJECT_STATE + INDEX; at the close of a work unit, the model proposes the `PROJECT_STATE.md` diff (routing/handoff + decisions), signed `model + date`; the user approves routing/state changes before they are committed (and only the user merges to `main`). Implementation commits/pushes of working branches still follow the governance phase workflow.
6. To be enforced by governance baseline **G7 - Multi-Model Orchestration Gate** in `PROJECT_GOVERNANCE.md` (added in Phase B).
7. **Roster of record:** the specialist roles are the **7** in `PROJECT_GOVERNANCE.md` (ADR-0001's six + `Access/Security Gatekeeper`). ADR-0001 remains the historical baseline; this ADR records the 7th role rather than editing ADR-0001 (ADRs are immutable point-in-time records).

## Consequences
- New work still declares specialist ownership (G2) regardless of which model executes.
- A small `PROJECT_STATE.md` (routing/handoff) plus the existing governance Current State replace ad-hoc bootstrap pastes; context load drops without duplicating phase state.
- Handoffs are explicit and user-decided; no silent cross-model reassignment.
- Each model's private memory (if any) only points to repo docs; it never holds a parallel source of truth.
- Governance edits are test-locked (`test_dashboard_static.py`) and are applied as a separate, test-gated phase (Phase B), not bundled with the additive new files (Phase A).

## Verification
- `AGENTS.md` exists and points to governance + PROJECT_STATE + INDEX.
- `PROJECT_GOVERNANCE.md` contains G7 and references `docs/PROJECT_STATE.md` only for cross-model routing/handoff, while retaining phase state in Current State.
- `docs/PROJECT_STATE.md` exists with the routing/handoff queue (no duplicated phase state).
- Phase B verification: `test_dashboard_static.py` stays green (baseline G7 reflected in MODULARIZATION + the matching test assertion updated together).