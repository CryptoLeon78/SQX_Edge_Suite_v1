# Regime Edge Analyzer

Marker: `sqx144-custom-results8-regime-edge-analyzer-v1`

`Regime Edge Analyzer` is an SQX Edge-owned StrategyQuant X 144 ResultsPlugin for selected-strategy market regime diagnostics.

## Contract

- Default messages: `STRATEGY_DATA`, `SET_THEME`, `SWITCH_THEME`, `SET_LANGUAGE`, `GET_STATS`, `STATS_RESPONSE`.
- Opt-in messages: `GET_ORDERS`, `ORDERS_RESPONSE`, only after pressing `Activar Regime Orders`.
- Future gated provider: Data Manager market series through a localhost-only read-only endpoint if separately approved.
- Blocked: source-code export, runtime writes, browser persistence, plugin management, SQX project/databank/task mutation and Migration Tool usage.

## Methodology

The tab classifies yearly market regimes as `BULL`, `BEAR`, `SIDEWAYS`, `MIXED` or `UNKNOWN`, then compares strategy orders against the detected direction:

- Long-only strategies should show aligned edge in `BULL`.
- Short-only strategies should show aligned edge in `BEAR`.
- Mean-reversion strategies should show evidence in `SIDEWAYS`.
- Adverse regime survival is useful only after aligned-regime edge exists.

Regime evidence is diagnostic only. It can force review or reduce confidence, but it never promotes a strategy by itself.

## Source-Ready Boundary

This phase is source-ready only:

- `installExecuted=false`
- No SQX runtime launch
- No `data.db`
- No `user/projects`
- No databank mutation
- No tasks
- No Migration Tool
- No source-code access/export
