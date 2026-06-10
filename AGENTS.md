Brain-first policy for this workspace:

Always consult gbrain before answering whenever the request may depend on:

- prior project knowledge;
- previous decisions;
- notes, docs, or research already created;
- people, companies, entities, or concepts already present in the knowledge base;
- user-specific or SQX Edge Suite project-specific context.

Mandatory lookup order:

1. gbrain search.
2. gbrain query if search is thin, ambiguous, or incomplete.
3. gbrain get_page when a relevant slug/page is identified.
4. External web or APIs only if gbrain does not provide sufficient information.

Behavior rules:

- Prefer brain knowledge over re-deriving known context.
- If gbrain returns enough context, answer from it directly.
- If gbrain returns partial context, use it first and only then supplement from local repo/docs or external sources.
- Do not skip gbrain for entity lookup, project context, previous notes or recurring tasks.
- After the conversation produces durable knowledge, save it to gbrain.
- Treat gbrain as the default memory layer for this workspace.

Write-back rules:

- Save durable facts, decisions, process notes, architecture choices, research summaries and reusable context to gbrain.
- Do not save temporary chatter or low-value intermediate noise.
- When new information materially updates an existing page, update that page instead of duplicating it.

SQX Edge Suite active bootstrap:

- Read `docs/PROJECT_GOVERNANCE.md`, `docs/state_consistency_manifest.json`, `README.md` current state and recent `CHANGELOG.md` anchors before non-trivial work.
- Current host baseline: SQX144 Full is the confirmed primary local host with profile `sqx144_full`.
- SQX142 Codex/QXPRO is preserved as authorized local diagnostic/methodology material, but it is no longer the active fallback for the current project.
- SQX143 has been removed from the local operator install during the 2026-06-06 cleanup; treat SQX143 references as historical unless a tracked doc explicitly reopens that lab.
- Do not delete SQX142 Codex/QXPRO, mutate SQX host projects/databanks, run SQX tasks, copy engine/binarios/internals, handle license material, or automate Migration Tool unless a current gate and explicit operator approval allow it.

Agent and subagent policy:

- Use SQX specialist skills when they materially reduce risk: governance, docs curator, test guardian, SQX142 local intelligence, academic/methodology, and portfolio specialists.
- When the operator explicitly asks for subagents, delegation, G9 or parallel work, load Multi-agent tools with `tool_search` if needed and spawn independent bounded subagents only for genuinely parallel slices.
- Codex remains orchestrator. Subagents may read, inspect, propose and run safe static checks; mutation permission is never automatic.
- If subagent output affects the next action, leave a short sanitized ignored handoff under `.local/agent_handoffs/` with role, scope, result and next action only.
