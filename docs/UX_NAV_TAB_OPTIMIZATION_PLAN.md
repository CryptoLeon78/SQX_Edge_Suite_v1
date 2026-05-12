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

`Workflow`

Workflow is the command center and must become the user's guided operating surface before any other tab is optimized.

## Tab Pass Order

This is the working order for individual optimization. It can be adjusted only after the active tab is completed or if the operator explicitly changes priority.

1. `Workflow` - active now.
2. `Mining Control`
3. `Project Generator`
4. `SQX Views`
5. `Strategy Builder`
6. `Champion vs Challenger`
7. `Estrategias`
8. `Por Activo`
9. `Filtros Fase 2`
10. `SQX Priority`
11. `Analyzer C2`
12. `Inicio`
13. Final navigation reordering and complete methodology flow.

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
