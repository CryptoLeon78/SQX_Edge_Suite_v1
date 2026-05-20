# WFCO - Edge Factory Facelift

## Summary

WFCO converts SQX Edge Suite from a tab-heavy technical dashboard into `Edge Factory`: a desktop-first command surface where the user follows the methodology from hypothesis to portfolio without guessing which tab to open next.

The first implementation is a shell, not a rewrite. Existing engines remain intact: Activos, Mining Control, SQX Views, Project Generator, Template Maker, Strategy Control, Champion vs Challenger and BlockSettings Info are opened from handoffs or `Herramientas avanzadas`.

## Product Direction

Primary user flow:

1. Preparar sesión.
2. Elegir tarjeta.
3. Minar Capa 1.
4. Analizar Capa 1.
5. Generar Template C2.
6. Minar Capa 2.
7. Analizar Capa 2.
8. Portfolio descorrelacionado.

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
- `capa1Outputs`
- `capa1Analysis`
- `c2Template`
- `capa2Outputs`
- `portfolioLab`

In remote mode this key is persisted through the authenticated workspace state bridge. Browser `localStorage` remains a compatibility cache.

## Phase Status

| Phase | Status | Scope |
| --- | --- | --- |
| WFCO-0 | Completed | Governance, roadmap and contract. |
| WFCO-1 | Completed | Edge Factory shell, advanced drawer and Portfolio Lab MVP surface. |
| WFCO-2 | Next | Handoffs from each stage into existing engines. |
| WFCO-3 | Pending | Copy/content overhaul across the main experience. |
| WFCO-4 | Pending | Portfolio Lab MVP beyond the shell. |
| WFCO-5 | Pending | Visual polish and desktop QA. |

## Safety Rules

- No raw local paths, protected URLs, emails, tokens, cookies or Cloudflare identifiers in the user-facing shell.
- No profitability guarantees or fake audit/certification claims.
- No remote tester expansion decisions are coupled to WFCO. REMOTE gates remain independent.
- No new engine format changes in WFCO-1.
