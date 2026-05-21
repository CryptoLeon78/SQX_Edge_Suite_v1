# WFCO - Edge Factory Facelift

## Summary

WFCO converts SQX Edge Suite from a tab-heavy technical dashboard into `Edge Factory`: a desktop-first command surface where the user follows the methodology from hypothesis to portfolio without guessing which tab to open next.

The first implementation is a shell, not a rewrite. Existing engines remain intact: Activos, Mining Control, SQX Views, Project Generator, Template Maker, Strategy Control, Champion vs Challenger and BlockSettings Info are opened from handoffs or `Herramientas avanzadas`.

## Product Direction

Primary user flow:

1. Punto de partida.
2. Elegir edge.
3. Generar Capa 1.
4. Certificar Capa 1.
5. Crear Template C2.
6. Generar Capa 2.
7. Revisar Capa 2.
8. Portfolio.

Default path is guided methodology. `Custom libre avanzado` remains available, but it is secondary and carries a partial-traceability warning.

## Decisions

- Visible primary navigation: `Edge Factory` and `Control Panel`.
- Hidden advanced tools: Activos, Mining Control, SQX Views, Project Generator, Template Maker, Strategy Control, Champion vs Challenger and BlockSettings Info.
- Portfolio Lab is the planned Capa 2 and portfolio analysis surface.
- Template Maker remains focused on Capa 1 certification and Template C2 generation.
- Desktop PC browser is the product target. Mobile only needs to avoid catastrophic breakage.
- Strategy Builder remains retired.

## State Contract

`sqx_edge_factory_state_v1` stores:

- `activeStep`
- `completedSteps`
- `selectedCard`
- `selectedMining`
- `projectPrefill`
- `capa1Outputs`
- `capa1Analysis`
- `c2Template`
- `capa2Outputs`
- `portfolioLab`
- `downloads`

In remote mode this key is persisted through the authenticated workspace state bridge. Browser `localStorage` remains a compatibility cache.

## WFCO-2 Handoff Contract

Edge Factory now receives public-safe handoff context from the existing engines:

- Activos / Mining Control: selected asset, timeframe, direction, BlockSetting real and mining row.
- Project Generator: Capa 1/Capa 2 generation mode, selected minings, result counts and generated output summaries.
- Template Maker: Capa 1 CSV/SQX analysis totals, PASSED count, clusters, winners and generated C2 template trace.
- Portfolio Lab: Capa 2 shortlist totals, diversity status and winners.

The UI shows this as one compact context strip per stage. It is intentionally a summary, not a raw log: no local paths, protected URLs, emails, tokens, Cloudflare identifiers or server internals are allowed in these stage strips.

## WFCO-3 Content Contract

The main shell now uses the headline `Del asset al portfolio, sin perder el hilo` and treats every stage as a compact decision card.

Each stage must answer four questions without forcing the user to know the old tab layout:

- What do I do now?
- What input do I need?
- What output should I get?
- What is still pending?

The visible rhythm is `Haz` plus `Sale`, followed by a short context strip. Advanced tool names may appear in the drawer and buttons, but the primary route is methodology-first and user-action-first.

## WFCO-4 Portfolio Lab Contract

Portfolio Lab is the Capa 2 decision surface. It is intentionally not Template Maker:

- Input: Capa 2 candidate CSV pasted into the Lab or loaded from the browser.
- Supported columns: strategy/name, asset/symbol, timeframe, Profit factor, Ret/DD Ratio or CAGR/Max DD %, Max DD %, # of trades, Stability, Winning Percent, SQN, BlockSetting, Indicator and Cluster when available.
- Decision states: `portfolio`, `similar` and `review`.
- Similarity uses asset, timeframe, BlockSetting, indicator and metric proximity.
- User-tunable defaults: similarity threshold, max winners and max winners per asset.
- Output: browser-downloaded shortlist CSV and public-safe JSON report.

Rows not selected for the portfolio must expose a reason such as similarity, limit, missing metrics, low PF, low trade count or high drawdown.

## WFCO-5 Desktop Polish Contract

Edge Factory now reads as a desktop command surface, not a passive overview.

- The hero includes a compact status stack for mode, output and override state.
- The command strip exposes four live traceability signals: Hipotesis, Capa 1, Template C2 and Portfolio.
- Each signal must summarize public-safe context only: no local paths, protected URLs, raw emails, tokens, Cloudflare identifiers or server internals.
- Stage cards keep one dominant action path and use visual state for current/completed stages without adding decorative noise.
- Browser PC is the product target. Mobile must remain serviceable, but desktop density and traceability remain the priority.

## Phase Status

| Phase | Status | Scope |
| --- | --- | --- |
| WFCO-0 | Completed | Governance, roadmap and contract. |
| WFCO-1 | Completed | Edge Factory shell, advanced drawer and Portfolio Lab MVP surface. |
| WFCO-2 | Completed | Real methodology handoffs from existing engines into Edge Factory state/context strips. |
| WFCO-3 | Completed | Copy/content overhaul across the main experience. |
| WFCO-4 | Completed | Portfolio Lab MVP beyond the shell. |
| WFCO-5 | Completed | Desktop polish, command strip, status stack and visual QA contract. |

## Safety Rules

- No raw local paths, protected URLs, emails, tokens, cookies or Cloudflare identifiers in the user-facing shell.
- No profitability guarantees or fake audit/certification claims.
- No remote tester expansion decisions are coupled to WFCO. REMOTE gates remain independent.
- No new engine format changes in WFCO-1.
