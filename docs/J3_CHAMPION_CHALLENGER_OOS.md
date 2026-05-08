# J3 Champion vs Challenger OOS Stability

Date: 2026-05-08

Status: implemented as pure OOS parsing and stability scoring inside the Champion vs Challenger core. No dashboard UI was added.

## Objective

J3 adds the OOS block evidence layer required before a native Champion vs Challenger dashboard can be useful for real StrategyQuant review work.

The phase extends `SQX.championChallengerCore` with:

- OOS metric-column detection.
- OOS CSV parsing.
- Primary OOS metric selection.
- Stability scoring per strategy row.
- Missing-block warnings.
- Safe strategy/symbol text fields for future rendering.

## Implemented Contract

New exposed functions:

- `extractOosHeader(header)`
- `resolveOosColumns(headers)`
- `choosePrimaryOosMetric(metricColumns, preferredMetrics)`
- `parseOosRecord(row, headers, oosColumns, options)`
- `parseOosCsv(text, options)`
- `normalizeMetricName(value)`

New exposed constants:

- `primaryOosMetrics`
- `defaultMinOosBlocks`

## OOS Column Format

Accepted columns follow this pattern:

```text
<Metric Name> (OOS<n>)
```

Examples:

- `CAGR/Max DD (OOS1)`
- `Profit Factor (OOS2)`
- `Worst Year Profit (OOS3)`

The parser rejects files with no OOS metric columns and warns when a metric has missing block numbers.

## Primary Metric Selection

The default preferred order is:

1. `CAGR/Max DD`
2. `Profit Factor`
3. `Net Profit`

If none of those exists, the first detected OOS metric becomes the primary metric.

## Stability Output

Every parsed OOS row returns:

- `primary_metric`
- `metrics_available`
- `metrics_by_block`
- `block_count`
- `positive_block_count`
- `positive_block_ratio`
- `primary_metric_min`
- `primary_metric_max`
- `primary_metric_avg`
- `primary_metric_decay`
- `max_negative_streak`
- `has_negative_worst_year`
- `stable_enough`
- `warnings`

`stable_enough` requires at least `defaultMinOosBlocks`, currently `3`.

## Security Boundary

J3 keeps the J2 security rules:

- Imported OOS CSV cells are untrusted.
- Strategy names and symbols are escaped for future rendering.
- Raw values remain local to the parsed result.
- No remote calls.
- No persistence.
- No DOM writes.
- No dashboard tab, Top Picks surface or Matrix surface is restored.

## Test Coverage

Contracts cover:

- OOS header extraction.
- OOS metric detection.
- Primary metric selection.
- Semicolon OOS CSV parsing.
- Quoted strategy names.
- XSS-like strategy names escaped as text.
- Positive-block ratio.
- min/max/average/decay.
- negative-streak calculation.
- negative Worst Year detection.
- sparse block warning.
- missing OOS metric-column rejection.

## Deferred To J4/J5

- Native dashboard UI.
- Import file controls.
- E2E screenshot verification.
- User-facing copy and empty/error states.
- Regime/EGT evidence adapter.
- Export and Strategy Builder handoff.
