# SQX142 Template Maker Correlation Review Cert

`SQX EDGE CORRELATION REVIEW` is now the canonical CSV contract for Capa1 -> Template C2 certification.

## Decision

The older `Template Maker Cert` view is obsolete for the current Capa1 correlation workflow. It expected a broad KPI matrix tied to the previous Forward/OOS layout. The active methodology now selects Template C2 candidates through CORR1:

- `IS_CORR` selects or groups Capa1 candidates for Template C2.
- `OOS3_CORR` audits stability and may veto/review drift.
- OOS3 does not select alternates unless a later holdout exists.

Template Maker therefore consumes the same `SQX EDGE CORRELATION REVIEW` export used by CORR1 instead of requiring a second certification view with unavailable or duplicated metrics.

## Required CSV Columns

Canonical required columns:

- `Strategy Name`
- `Symbol`
- `TimeFrame`
- `Fitness`
- `ProfitFactor`
- `ReturnDDRatio`
- `DrawdownPct`
- `NumberOfTrades`
- `SQXEdgeCorrDecision`
- `SQXEdgeCorrStatus`

Accepted aliases remain supported for user-facing columns such as `Profit factor`, `Ret/DD Ratio`, `Max DD %` and `# of trades`.

## Compatibility

Legacy `Template Maker Cert v2` CSV files remain accepted as an import compatibility path. They are no longer the recommended SQX Views output for the buyer/operator workflow.

## Boundaries

This is a UI and contract change only. It does not launch SQX, mutate SQX local projects, write `data.db`, patch jars/plugins/licensing, delete databanks, run projects, call Migration Tool or fabricate missing metrics.
