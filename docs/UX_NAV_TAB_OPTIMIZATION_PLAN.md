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

Active experience track: `WFCO - Edge Factory`.

The operator explicitly opened Website Facelift + Content Overhaul to simplify the full workflow into one main desktop experience. Workflow is being transformed into `Edge Factory`, a methodology-first shell over the existing engines. Project Generator, Template Maker, Strategy Control, CVC, SQX Views, Mining Control, Activos and BlockSettings stay available as advanced/internal tools, not as the primary navigation for the buyer/tester.

Desktop priority: the experience is optimized for PC browser. Mobile should not break catastrophically, but the product will not trade away desktop clarity or column density for phone-first behavior.

Current WFCO status:

- `WFCO-0 · Governance And Contract`: completed.
- `WFCO-1 · Edge Factory Shell`: completed.
- `WFCO-2 · Methodology Handoffs`: completed.
- `WFCO-3 · Content Overhaul`: completed.
- `WFCO-4 · Portfolio Lab MVP`: completed.
- `WFCO-5 · Visual Polish And Desktop QA`: completed.
- `WFCO-ACCEPT1 · Basic/Advanced Acceptance Polish`: completed.
- `WFCO-AI1 · Local/Remote-Safe Agent Dock`: completed.

Historical repair/enrichment pause: TM-DIV1 added a hybrid diversity gate to Template Maker after the TM-FIX2 CSV contract repair. This did not advance the UX-NAV tab order and does not reopen Template Maker as a design pass; it prevents redundant C2 templates by clustering similar `.sqx` logic plus CSV metric behavior.

Historical traceability hardening pause: TM-TRACE1 makes Template Maker C2 generation carry asset, BlockSetting, base indicator, NumCluster, direction, timeframe and source strategy in the generated filename and internal `StrategyName`. This is now a product invariant because C2 templates must be traceable from source to output.

Active correction: `Foco operativo` and `Precarga desde Por Activo` are retired completely from the visible UI. `Plan mining` remains the single source of truth, and rows added from asset cards are identified in-table with the source tag `TARJETA`, alongside manual rows tagged as `MANUAL`.

Visual correction: duplicate showcase/preload panels are removed so the tab stays dense, traceable and action-oriented.

Navigation correction: the sidebar labels/icons are standardized for the current methodology: `Activos`, `Mining Control`, `Project Generator`, `Template Maker`, `Strategy Control`, `Champion vs Challenger`, `BlockSettings Info` and `Control Panel`. The navigation rail can be collapsed to icon-only mode to recover workspace width.

Activos basic/advanced correction: `sqxSelectionPolicy` separates recommended SQX config, selected SQX config and generation permission. Forex is selectable in A/B/C/D; index/gold `Only Short` generation is blocked. In basic mode asset cards use direct Project Generator prefill and hide Plan Mining technical buttons; in advanced mode `+ Plan`, `Gen Project` and Mining Control handoffs remain visible.

Navigation step correction: both basic and advanced users have top and bottom `Anterior` / `Siguiente` controls. Basic navigation follows the methodological route from Edge Factory through Activos, Project Generator, Template Maker, CVC/Portfolio and Control Panel; advanced navigation follows the technical manifest order.

BlockSettings Info pass: `Help/Filtros Fase 2` is repurposed as a methodological BlockSettings showcase. It keeps internal tab id `filtros`, but now explains Capa 1 edge-search BlockSettings from real `_v6`/intraday v6 `.sqb` files, including `BS_Volatilidad_v6` as the general Volatilidad source and `BS_Volatilidad_v6_intraday_v6` for M5/M15/M30/H1, Capa 2 `BS_Filtros_v6`/`BS_Filtros_v6_D1` recommendations, calibrated market logic and the connection with Activos, Plan Mining and Project Generator.

## Tab Pass Order

This historical order remains traceability for completed individual optimizations. WFCO now sits above the tab order as the user-facing shell; technical tabs remain accessible from the advanced drawer.

1. `Workflow` - completed as command center.
2. `Mining Control` - pending only if the operator explicitly reopens it; focused cleanup of duplicate informational surfaces is already complete.
3. `SQX Views` - completed as guided view assistant.
4. `Template Maker` - completed as Capa 1 scoring and C2 generation surface.
5. `Strategy Control` - completed as operational repository.
6. `Champion vs Challenger` - completed as final decision board.
7. `Project Generator` - completed as guided `.cfx` generation assistant.
8. `Activos`
9. `BlockSettings Info` - completed as methodological BlockSettings showcase.
10. `Inicio`
11. Final navigation reordering and complete methodology flow.

## WFCO - Website Facelift + Content Overhaul

Goal: convert the app into `Edge Factory`, a near all-in-one guided methodology that reduces tab-hopping and shows the user only what to do next.

Primary flow:

1. `Punto de partida`: confirm access, workspace, service, downloads and remote readiness.
2. `Elegir edge`: select asset hypothesis, timeframe, direction and real BlockSetting.
3. `Generar Capa 1`: generate the methodological `.cfx`.
4. `Certificar Capa 1`: Template Maker with CSV/SQX contract, clusters and winners.
5. `Crear Template C2`: traceable C2 modal with indicators, cluster and Exit Policy.
6. `Generar Capa 2`: generate `.cfx` Capa 2 from the validated template.
7. `Revisar Capa 2`: Portfolio Lab, not Template Maker.
8. `Portfolio`: shortlist, diversity, export and next action.

Design rules:

- Visible primary navigation: `Edge Factory` and `Control Panel`.
- Existing tools are hidden behind `Herramientas avanzadas` and internal handoffs.
- Custom libre stays advanced and warns about partial traceability.
- Strategy Builder remains retired.
- No routes, server paths, private URLs or raw technical backend details are shown to normal users.
- No profitability claims.
- Operator-only local AI belongs inside Edge Factory as a dock, not as a primary navigation tab.

WFCO-2 applied handoff rule:

- Activos and Mining Control register selected card/mining context in Edge Factory.
- Project Generator registers Capa 1/Capa 2 generation events, selected minings, result counts and output file summaries.
- Template Maker registers Capa 1 analysis state and generated Template C2 trace.
- Portfolio Lab registers shortlist/diversity output.
- Each stage has a compact context strip so the user sees what was selected, generated, analyzed or still missing without reopening every advanced tool.

WFCO-3 applied content rule:

- Edge Factory stages now speak in action/output terms: `Haz`, `Sale`, pending context and one primary action per stage.
- The main shell says `Del asset al portfolio, sin perder el hilo` and removes tab-heavy wording from the primary route.
- Advanced tools remain available in the drawer, but user-facing guidance is methodology-first rather than module-first.

WFCO-4 applied Portfolio Lab rule:

- Capa 2 candidates are analyzed in Portfolio Lab, not Template Maker.
- The Lab accepts pasted CSV or browser file load, supports semicolon/comma CSV and decimal comma/punto, and resolves common SQX columns.
- Output states are `portfolio`, `similar` and `review`; every non-portfolio row must show why it was not selected.
- The shortlist can be exported as browser CSV and the full report as browser JSON.

WFCO-5 applied desktop polish rule:

- Edge Factory uses a live command strip for Hipotesis, Capa 1, Template C2 and Portfolio.
- The hero status stack shows guided mode, browser-download output and advanced override state without exposing internal routes or local paths.
- Stage cards emphasize current/completed state through restrained desktop visuals, keeping the PC browser workflow dense and readable.
- Mobile must remain serviceable, but desktop clarity and traceability are the priority.

WFCO-ACCEPT1 applied mode rule:

- `Modo básico` is the default buyer/tester route: one primary action per stage, context visible, technical drawers and manual checks hidden.
- `Modo avanzado` explicitly unlocks internal tools, manual completion checks and custom libre without changing engines or security gates.
- The primary copy now reinforces `.cfx` browser downloads and SQX target profiles so the user understands that generated files arrive through the browser, not through server folders.

## UX-WF2 - Functional Pipeline KPIs

Goal: make the `Filosofía y flujo completo del pipeline` block behave as a real command map. Static KPIs are not enough at this product stage; each stage must tell the user what it controls, what to verify, where to go next and what traceability must survive.

Design direction: `Pipeline Command Map`.

- Cards stay compact and methodological.
- Only one detail opens at a time, using the existing Workflow detail system.
- Each KPI declares its role: `obligatorio`, `control`, `validación`, `decisión` or `salida`.
- Each KPI answers: what do I do here, what proves I can move on, and which tab/subtab helps me execute it.
- Workflow remains a guide, not an encyclopedia; long operational detail stays in the owning tab.

Functional map:

- Step 0 `Vista SQX obligatoria`: handoff/control to SQX Views; already functional.
- Step 1 `Mining Capa 1`: technical control; already functional.
- Step 2 `Extracción de Templates ganadores`: selection gate with Template Maker and Strategy Control access, requiring `.sqx`, BlockSetting, indicator base and duplicate review.
- Step 3 `Mining 2 / Capa 2`: technical control; already functional.
- Step 4 `Filtros estrictos + Retest C2`: validation gate with C2 semáforo, Risk view handoff and Capa 2 checklist access.
- Step 5 `Robustez supervivientes`: robustness queue for MC, MC2, Sequential, Synthetic, SPP and WFM, with SQX Views Robustez handoff.
- Step 6 `Correlación intra-template`: diversity decision, one winner per template, tied to Template Maker clusters and Strategy Control cleanup.
- Step 7 `Correlación cross-todo`: portfolio gate for cross-template, cross-BlockSetting, cross-timeframe and cross-asset checks before Champion vs Challenger.
- Step 8 `Portfolio Master + MT5`: controlled output stage for demo, gradual real deployment, evidence and support.

Completion criteria for UX-WF2:

- Steps 2, 4, 5, 6, 7 and 8 are expandable and use the same behavior as steps 0, 1 and 3.
- Each new detail has a checklist or decision signal and at least one relevant internal handoff.
- Existing Workflow APIs remain unchanged.
- E2E asserts the new pipeline details and screenshots the updated surface.
- Status: completed, tested, pushed and accepted by operator real-browser visual/manual pass on 2026-05-17.

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
