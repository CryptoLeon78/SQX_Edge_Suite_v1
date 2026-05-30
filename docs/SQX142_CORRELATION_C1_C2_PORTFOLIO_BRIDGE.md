# SQX142 Correlation Bridge C1 -> C2 -> Portfolio

Status: `implemented_bridge_contract`

Version: `sqx142-correlation-c1-c2-portfolio-bridge-v1`

## Purpose

The suite now keeps three correlation surfaces separate:

1. Capa1 C2 template selection.
2. Capa2 portfolio selection.
3. The bridge that connects the Capa1 winner into Template Maker, Capa2 generation and later portfolio review.

## Bridge Map

```text
Capa1 custom databanks
  -> SQX EDGE CORR1 STABILITY / SQX EDGE CORR1 TAGGED
  -> c2_template_selection_decision
  -> Template Maker C2 source strategy
  -> Capa2 custom project generation
  -> Capa2 Forward/Foward finalists
  -> Portfolio Lab / Capa2 portfolio correlation
  -> Portfolio Master contract
```

## State Nodes

```text
edgeFactory.capa1Analysis
edgeFactory.c2TemplateSelection
edgeFactory.c2Template
edgeFactory.portfolioLab
edgeFactory.portfolioCorrelationStability
edgeFactory.portfolioMasterContract
```

## Registry Contract

The mining registry is custom-project-centric:

- Every databank snapshot belongs to a custom project.
- Every correlation decision declares `decisionDomain`.
- Capa1 CORR nodes are stored as `capa1_c2_template_selection`.
- Capa2 portfolio nodes are stored as `capa2_portfolio_selection`.
- Legacy portfolio-named Capa1 rows are read as deprecated aliases, not as final portfolio evidence.

## Academic Guard

The guard is conservative and practical:

- Repeated selection on the same holdout creates data-snooping risk.
- OOS/Forward may audit/veto but should not repeatedly select replacements without a fresh later holdout.
- This follows the discipline behind PBO/CSCV, Deflated Sharpe Ratio, White Reality Check and purged/embargoed validation. These sources support the validation discipline; they do not prove profitability or this exact SQX configuration.

## Operational Boundary

The bridge is traceability and decision routing. It does not authorize:

- SQX runtime launch from scripts.
- SQX `data.db` writes.
- Project/databank mutation outside a guarded local-project integrator.
- Jars, engine binaries, internal plugins, license or activation changes.
- Forced pass, sample-as-real, profit guarantee or risk-zero claims.
