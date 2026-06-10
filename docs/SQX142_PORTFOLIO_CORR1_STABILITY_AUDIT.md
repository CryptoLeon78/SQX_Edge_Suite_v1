# SQX142-PORTFOLIO-CORR1 Capa2 Correlation Stability Audit

Status: `implemented_capa2_scope_with_capa1_alias_reclassified`

Version: `sqx142-portfolio-corr1-stability-audit-v1`

Registered SQX local reader alias: `sqx142-portfolio-corr1-registered-decision-v1`

Capa1 registered reader: `sqx142-capa1-c2-corr1-registered-decision-v1`

## Decision

Forward/Foward-only correlation is too narrow for portfolio construction. SQX Edge now separates:

- `IS_CORR`: broad in-sample correlation window, intended to cover the mining period plus Retest 0 validation context.
- `OOS3_CORR`: final Forward/Foward correlation window, used only to audit whether the IS diversification survives in the holdout period.

OOS3 must not select alternates. If OOS3 is used to choose replacements, it becomes another validation/selection set and a later untouched holdout is required.

Important 2026-05-30 correction: the first real AUDCAD H1 run is Capa1. Its registered CORR1 result is valid evidence, but its purpose is `capa1_c2_template_selection`, not final portfolio selection. The Capa2 portfolio endpoint remains valid for Portfolio Lab / Capa2 Forward finalists. The Capa1 flow is documented in `docs/SQX142_CAPA1_C2_CORRELATION_TEMPLATE_SELECTION.md`.

## Implementation

Backend contract:

```text
POST /api/sqx142/portfolio-correlation/stability-audit
POST /api/sqx142/capa1-c2-correlation/stability-audit
POST /api/sqx142/capa1-c2-corr1/registered-decision
POST /api/sqx142/portfolio-corr1/registered-decision
```

Core:

```text
backend/sqx-edge-tool/core/sqx142_portfolio_correlation_stability.py
backend/sqx-edge-tool/tools/sqx142_portfolio_corr1_registered_decision.py
tools/sqx142_portfolio_corr1_registered_decision.ps1
```

Frontend:

- Edge Factory / Portfolio Lab panel: `Auditoria Capa2 portfolio IS vs OOS3`.
- Backport Operator Panel operation: `Capa2 Portfolio CORR1 stability audit`.
- Capa1 registered button: `Analizar Capa1 C2 registrado`.

The endpoint accepts:

- candidate CSV or rows;
- optional `isSeriesCsv` with `strategy,isReturnSeries`;
- optional `oos3SeriesCsv` with `strategy,oos3ReturnSeries`;
- settings for IS threshold, OOS3 threshold, warning threshold, drift threshold and minimum comparable points.

The registered SQX local action additionally reads the already registered custom project while SQX is closed:

- input databank: `SQX EDGE CORR1 TAGGED`;
- private source: local SQX142 `.sqx` files, parsed read-only;
- series source: `Results/.../dailyEquity.bin` inside each `.sqx`;
- period split from the custom `project.cfx`: `IS_CORR=2017.10.02..2025.01.01`, `OOS3_CORR=2025.01.01..2026.04.08`;
- legacy registry alias: step `93`, `corr1_registered_stability_decision`, output `portfolio_decision`.
- canonical Capa1 registry node: `capa1_c2_corr1_registered_selection_decision`, output `c2_template_selection_decision`.

The report returns:

- `selectedByIs`: shortlist selected only from `IS_CORR`;
- `selectedPairAudit`: pairwise IS/OOS3 correlations among selected candidates;
- `oos3CorrelationBreaks`: pairs whose OOS3 correlation exceeds the veto threshold;
- `oos3Warnings`: pairs with drift or warning-threshold issues;
- methodology flags proving `oos3MaySelectAlternates=false`.

## Real Registered Result

Custom project: `SQX_EDGE_API_FRESH_AUDCAD_H1_Momentum_20260528_090029_Capa1`

Databank path in the funnel:

```text
Forward -> SQX EDGE CORR1 STABILITY -> SQX EDGE CORR1 TAGGED -> c2_template_selection_decision
```

Result from `tools\sqx142_portfolio_corr1_registered_decision.ps1 -Action analyze`:

- input rows: `23`;
- selected by `IS_CORR`: `1`;
- similar by `IS_CORR`: `22`;
- review: `0`;
- selected pair audit rows: `0`, because only one strategy survived the IS decorrelation gate;
- OOS3 comparable nearest-to-selected checks: `22`;
- OOS3 nearest warnings: `22`;
- status: `pass`.

Decision: the Capa1 Template C2 selection surface has one decorrelated winner from this custom. The 22 non-selected candidates are not valid alternates; their OOS3 correlations to the selected winner remain high, so OOS3 confirms concentration rather than opening replacements. A final portfolio decision must be made later from Capa2 Forward finalists.

## Academic Rationale

This is a methodology guard against data snooping and repeated selection on the same holdout. The implementation follows the conservative inference from:

- Bailey, Borwein, Lopez de Prado and Zhu, [The Probability of Backtest Overfitting](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253): PBO/CSCV and degradation from repeated backtest selection.
- Bailey and Lopez de Prado, [Deflated Sharpe Ratio](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551): selection bias and multiple-testing adjustment.
- White, [White Reality Check](https://www.econometricsociety.org/publications/econometrica/2000/09/01/reality-check-data-snooping): data-snooping risk when selecting among many tested rules.
- Lopez de Prado, *Advances in Financial Machine Learning*: purged/embargoed validation discipline to keep financial time-series validation/test leakage under control.

The sources support the general discipline; they do not prove this exact SQX configuration. The SQX-specific rule is an implementation inference: select on IS, audit on OOS3, and require a fresh holdout if OOS3 becomes a selector.

## Boundaries

Allowed:

- External CSV/series audit in SQX Edge.
- Registered SQX local read-only audit while SQX is closed.
- Sanitized hashed candidate IDs.
- JSON/CSV export of pair audit.
- Capa1 Template Maker using the registered audit as Template C2 selection evidence.
- Capa2 Portfolio Lab using the same audit engine only on Capa2 finalists.

Blocked:

- Launching SQX.
- Running SQX retests from the suite.
- Writing SQX `user/data/data.db`.
- Mutating SQX `user/projects` or databanks.
- Writing to SQX local `.sqx`, `project.cfx`, databanks or `data.db` during registered decision analysis.
- Patching jars, internal plugins, license or activation.
- `run_project`, Migration Tool or `/project/checkResources`.
- Treating OOS3/Forward as an optimizer for replacement candidates.
- Treating a Capa1 CORR1 result as final Portfolio Master evidence.
