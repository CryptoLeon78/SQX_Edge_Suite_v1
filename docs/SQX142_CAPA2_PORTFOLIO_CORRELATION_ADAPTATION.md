# SQX142-CAPA2-PORTFOLIO-CORR Adaptation

Status: `implemented_capa2_scope_declared`

Current extension: `candidate_cohort_parked`

Version: `sqx142-capa2-portfolio-corr1-scope-v1`

## Decision

Portfolio correlation belongs after Capa2 has produced natural Forward/Foward finalists. Capa1 correlation may select C2 templates, but it must not be presented as final portfolio selection.

Capa2 canonical decision domain:

```text
capa2_portfolio_selection
```

Current endpoint kept for Capa2 portfolio:

```text
POST /api/sqx142/portfolio-correlation/stability-audit
```

Current state node kept for Capa2 portfolio:

```text
edgeFactory.portfolioCorrelationStability
```

## Active Rules

- Source candidates must be Capa2 Forward/Foward finalists or an equivalent Portfolio Lab input.
- `IS_CORR` can select/diversify the Capa2 portfolio candidate shortlist.
- `OOS3_CORR` audits or vetoes stability; if it is reused for replacement selection, a later holdout is required.
- Labels `portfolio`, `similar` and `review` are valid only in the Capa2/Portfolio Lab context.
- A single-asset Capa2 result can be parked as an accepted candidate cohort, but it is not Portfolio Master.

## Parked Real Cohort

The USDJPY H1 Volatilidad Capa2 correlation/CVC closeout is parked as accepted evidence:

- Status: `accepted_as_single_asset_capa2_candidate_not_portfolio_master`.
- Primary Champion: `WF Matrix - Strategy 0.13535`.
- Decorrelated co-candidates: `WF Matrix - Strategy 0.6228` and `WF Matrix - Strategy 0.26354`.
- Similar reserves: `5`.
- OOS3 warnings remain visible; hard OOS3 breaks: `0`.
- Portfolio Master status: `deferred_pending_multi_asset_context`.

This cohort may be used later as one candidate sleeve/input when broader multi-asset or multi-cohort context exists. It must not be relabeled as a final portfolio by itself.

## Future Local SQX Integration Names

If a Capa2 local-project CORR flow is added, it must not reuse the Capa1 CORR1 databank names without a domain marker. Reserved names:

```text
sqx142-capa2-portfolio-corr1-registered-decision-v1
sqx142-capa2-portfolio-corr2-local-project-integration-v1
SQX EDGE C2 CORR1 STABILITY
SQX EDGE C2 CORR1 TAGGED
capa2_corr1_registered_stability_decision
```

The current implementation does not mutate Capa2 SQX projects for portfolio correlation. It only exposes the external Capa2 portfolio audit and keeps the shared correlation engine domain-scoped.

## Boundaries

Allowed:

- Use Portfolio Lab / external CSV rows for Capa2 candidates.
- Reuse the shared Pearson IS/OOS3 engine with `decisionDomain=capa2_portfolio_selection`.
- Export sanitized JSON/CSV audit output.

Blocked:

- Feeding Capa1 CORR1 decisions directly into Portfolio Master.
- Promoting one single-asset Capa2 cohort into Portfolio Master without broader portfolio context.
- Using SQX FitPortfolio as a hidden optimizer.
- Launching SQX, writing `data.db`, mutating SQX projects/databanks, patching jars/internal plugins/license or forcing pass.
