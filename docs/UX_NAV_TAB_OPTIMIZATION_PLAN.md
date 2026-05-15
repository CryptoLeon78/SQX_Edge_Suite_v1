# UX-NAV Tab Optimization Plan

## Operating Rule

UX-NAV now runs as a sequential tab-by-tab optimization track.

- Only one tab can be in active optimization at a time.
- The active tab remains locked until the operator explicitly says: `Adelante con el siguiente tab`.
- Any message during an active tab phase is interpreted as feedback, correction, or extension for that active tab.
- Global tab reordering, final navigation flow and cross-tab reshuffling are postponed until every individual tab pass is complete.
- Do not remove, hide, merge, or repurpose another tab during an active tab pass unless the operator explicitly changes the active scope.
- Each implementation pass still follows the project discipline: backup, focused change, tests, visual E2E when frontend changes, cleanup, single commit and push.

## Current Active Tab

`Mining Control` paused for TM-TRACE1

Project Generator is closed as a guided `.cfx` assistant. Mining Control is reopened as the active pass for a focused operational cleanup.

Temporary repair/enrichment pause: TM-DIV1 adds a hybrid diversity gate to Template Maker after the TM-FIX2 CSV contract repair. This does not advance the UX-NAV tab order and does not reopen Template Maker as a design pass; it prevents redundant C2 templates by clustering similar `.sqx` logic plus CSV metric behavior before Mining Control resumes.

Traceability hardening pause: TM-TRACE1 makes Template Maker C2 generation carry asset, BlockSetting, base indicator, NumCluster, direction, timeframe and source strategy in the generated filename and internal `StrategyName`. This is a product invariant before returning to Mining Control because C2 templates must be traceable from source to output.

Active correction: `Foco operativo` and `Precarga desde Por Activo` are retired completely from the visible UI. `Plan mining` remains the single source of truth, and rows added from asset cards are identified in-table with the source tag `TARJETA`, alongside manual rows tagged as `MANUAL`.

Visual correction: duplicate showcase/preload panels are removed so the tab stays dense, traceable and action-oriented.

Navigation correction: the sidebar labels/icons are standardized for the current methodology: `Activos`, `Mining Control`, `Project Generator`, `Template Maker`, `Strategy Control`, `Champion vs Challenger`, `BlockSettings Info` and `Control Panel`. The navigation rail can be collapsed to icon-only mode to recover workspace width.

BlockSettings Info pass: `Help/Filtros Fase 2` is repurposed as a methodological BlockSettings showcase. It keeps internal tab id `filtros`, but now explains Capa 1 edge-search BlockSettings, Capa 2 `BS_Filtros_v5.sqb`, calibrated market logic and the connection with Activos, Plan Mining and Project Generator.

## Tab Pass Order

This is the working order for individual optimization. It can be adjusted only after the active tab is completed or if the operator explicitly changes priority.

1. `Workflow` - completed as command center.
2. `Mining Control` - active again for focused cleanup of duplicate informational surfaces.
3. `SQX Views` - completed as guided view assistant.
4. `Template Maker` - completed as Capa 1 scoring and C2 generation surface.
5. `Strategy Control` - completed as operational repository.
6. `Champion vs Challenger` - completed as final decision board.
7. `Project Generator` - completed as guided `.cfx` generation assistant.
8. `Activos`
9. `BlockSettings Info` - completed as methodological BlockSettings showcase.
10. `Inicio`
11. Final navigation reordering and complete methodology flow.

## Estrategias Optimization Scope

Goal: make Estrategias a repository, not another scoring engine.

Estrategias should answer:

- Which strategies are visible right now?
- Which are base, imported or hidden?
- Which are candidates, deployed or rejected?
- How do I filter/prioritize without guessing?
- How do I import, add, export, consolidate or clean safely?
- Where do I go next for SQX Views or Champion vs Challenger?

## Champion vs Challenger Optimization Scope

Goal: make Champion vs Challenger a guided final decision board, not a raw CSV console.

Champion vs Challenger should answer:

- When should I compare Champion against Challengers?
- Which CSV blocks do I need and what does each one mean?
- Are the inputs valid enough to evaluate?
- Which candidate survives Health, EGT v2, OOS and coherence filters?
- How do I export a safe review and return to the workflow?

## Project Generator Optimization Scope

Goal: make Project Generator a guided `.cfx` generation assistant, not a mixed technical console.

Project Generator should answer:

- Is the local backend available?
- Are SQX paths, templates, output and aliases ready?
- Should I generate from Plan Mining or use Custom libre?
- Which Plan Mining rows do I want to generate now?
- Which Capa 1/Capa 2 actions are safe to press now?
- Where are the generated `.cfx` files and what did the log report?

Strategy Cleaner remains available in its current position during this pass. Its final location will be reviewed in the global navigation/reflow phase.

## Workflow Optimization Scope

Goal: make Workflow the practical guided methodology screen, not a decorative home page.

Workflow should answer, at every moment:

- What has the user already done?
- What is the next recommended action?
- Which tools are unlocked now?
- Which tools are intentionally locked until prior steps are completed?
- Why does this step matter inside the SQX methodology?
- Where does the user go next without guessing?

### Workflow Pass W1 - Inventory And Contract

- Map current Workflow DOM, JS module, state keys, buttons, cards, handoffs and tests.
- Identify dead, duplicated, unclear or overly decorative elements.
- Define a no-break contract for existing handoffs into SQX Views, Project Generator, Mining Control and Strategy Builder.
- No visual redesign yet except trivial copy fixes if needed.

### Workflow Pass W2 - Guided State Model

- Define explicit workflow stages, completion criteria and unlock rules.
- Keep state local-only unless a later backend contract is explicitly approved.
- Make reset/clear behavior clear and reversible enough for users.
- Preserve tester-safe behavior and avoid claims about trading outcomes.

### Workflow Pass W3 - Command Center Layout

- Reorganize Workflow into a concise operational surface:
  - current progress
  - next action
  - active blockers
  - available tools
  - recent handoffs
- Avoid nested cards and marketing-style hero sections.
- Keep copy brief, practical and action-oriented.

### Workflow Pass W4 - Methodology Guidance

- Add plain explanations for each methodology stage.
- Use progressive disclosure rather than wall-of-text.
- Make locked tools understandable: what unlocks them and why.
- Keep the user guided without making the interface feel patronizing.

### Workflow Pass W5 - Cross-Tab Handoff Hardening

- Verify every Workflow action lands on the correct tab/subtab with the right prefilled context.
- Verify disabled/locked actions cannot create inconsistent state.
- Add/update E2E coverage for the guided route.

### Workflow Pass W6 - Visual Polish And Mobile

- Tune density, contrast, spacing, active states and responsive behavior.
- Verify desktop and mobile screenshots.
- Do not reorder global tabs in this pass.

## Deferred Until Final UX-NAV Pass

- Global tab order.
- Removing additional tabs.
- Merging tabs.
- Renaming tabs beyond the active tab scope.
- Primary navigation hierarchy.
- Final end-to-end methodology flow across all tabs.

## Completion Criteria For Each Tab

A tab is complete only when:

- User-facing objective is clear.
- Dead or confusing UI has been removed or justified.
- State, actions and handoffs are traceable.
- Tests are updated.
- Visual E2E passes if the tab is frontend-visible.
- Temporary Playwright artifacts are cleaned.
- Single commit is created and pushed.
- The operator says `Adelante con el siguiente tab` before work moves to another tab.
