# G10 Agent And Subagent Refresh

Status: `completed_agent_subagent_refresh_sqx144_primary`.
Date: 2026-06-06.
Marker: `g10-agent-subagent-refresh-v1`.

## Scope

This phase refreshes the project and local Codex agent instructions after the
SQX144 Full closeout and disk cleanup.

Current operational assumptions for agents and subagents:

- SQX144 Full / `sqx144_full` is the confirmed primary local host.
- SQX142 Codex/QXPRO is preserved as local diagnostic and methodology material,
  but it is not the active fallback for the current project.
- SQX143 was removed during local cleanup and is historical-only unless a future
  governed phase reinstalls or reopens it.
- SQX144 144.2953 remains under `SQX144-FULL-UPDATE2`; no automatic promotion.

## Updated Surfaces

- Workspace `AGENTS.md` now contains the brain-first policy, active SQX bootstrap
  and agent/subagent permission boundaries.
- The local Codex global `AGENTS.md` is aligned with the same active SQX
  bootstrap.
- Installed local Codex skills are aligned:
  - `sqx-edge-suite-governance`;
  - `sqx142-local-intelligence`;
  - `sqx-docs-curator`;
  - `sqx-test-guardian`.
- SQX144 read-only gate scripts now report SQX142 only as a manual rollback
  exception, not as an active fallback.
- Project docs and agent profile config are aligned:
  - `docs/PROJECT_GOVERNANCE.md`;
  - `docs/ARCHITECTURE.md`;
  - `docs/STATE_CONSISTENCY_GUARD.md`;
  - `docs/LOCAL_AI_AGENT_ROADMAP.md`;
  - `docs/decisions/ADR-0001-specialist-agent-governance.md`;
  - `backend/sqx-edge-tool/config/agent_profiles.json`;
  - `README.md`;
  - `CHANGELOG.md`;
  - `docs/state_consistency_manifest.json`.

## Runtime Contract

- Every non-trivial SQX Edge Suite turn starts from gbrain and tracked
  governance before implementation.
- Specialist skills are selected by task risk, not by habit.
- When the operator explicitly asks for subagents, delegation, G9 or parallel
  work, Codex lazy-loads Multi-agent tools with `tool_search` if needed.
- Subagents are used for bounded independent slices: docs drift, verification,
  local SQX evidence, methodology review, security/privacy or disjoint
  implementation.
- Codex remains orchestrator and owns permission expansion.
- Subagents may read, inspect, propose, run safe static checks and suggest
  dry-runs. They do not receive automatic permission for `--apply`, `--write`,
  `--launch`, destructive cleanup, project/databank mutation, Cloudflare/grants,
  checkout/email/license actions or SQX runtime work.
- Material subagent results get a short ignored handoff under
  `.local/agent_handoffs/`, storing role, scope, result and next action only.

## Privacy

Tracked docs may name state markers and sanitized host labels, but must not
publish raw SQX logs, private paths, license material, tokens, protected URLs,
emails, account evidence or private workspace payloads.
