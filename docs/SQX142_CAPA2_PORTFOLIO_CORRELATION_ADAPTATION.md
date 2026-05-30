# SQX142-CAPA2-PORTFOLIO-CORR Adaptation

Status: `implemented_capa2_scope_declared`

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
- Using SQX FitPortfolio as a hidden optimizer.
- Launching SQX, writing `data.db`, mutating SQX projects/databanks, patching jars/internal plugins/license or forcing pass.
