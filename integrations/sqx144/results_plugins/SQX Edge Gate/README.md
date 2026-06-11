# SQX Edge Gate

Phase: `SQX144-CUSTOM-RESULTS5 - SQX Edge Gate`

Marker: `sqx144-custom-results5-edge-gate-v1`

Status: `custom_results5_edge_gate_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool`

`SQX Edge Gate` is an SQX Edge-owned StrategyQuant X 144 ResultsPlugin. It is a separate Results tab with a Trading Radar identity and does not replace or modify downloaded Custom Results plugins.

## Contract

Default messages:

- `STRATEGY_DATA`
- `SET_THEME` / `SWITCH_THEME`
- `SET_LANGUAGE`
- `GET_STATS`
- `STATS_RESPONSE`

Opt-in messages:

- `GET_ORDERS`
- `ORDERS_RESPONSE`

`GET_ORDERS` is only sent after the operator presses `Activar Order Radar`.

## Decision Gate

PASS requires:

- `NumberOfTrades >= 120`
- `ProfitFactor >= 1.3`
- `ReturnDDRatio >= 4`
- `RExpectancy > 0`
- `NetProfit > 0`

REVIEW covers intermediate stats or missing OOS evidence.

BLOCK covers missing stats, very low evidence, weak profitability/risk, negative expectancy or non-positive net profit.

## Boundaries

- Source-ready only until an exact install approval is supplied.
- No StrategyQuant runtime launch.
- No host data writes.
- No project/databank/task mutation.
- No Migration Tool.
- No pass-state promotion.
- No source-code export.
