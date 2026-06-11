# SQX Edge Gate

Phase: `SQX144-CUSTOM-RESULTS6 - SQX Edge Gate V2`

Marker: `sqx144-custom-results6-edge-gate-v2`

Status: `custom_results6_edge_gate_v2_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool`

`SQX Edge Gate` is an SQX Edge-owned StrategyQuant X 144 ResultsPlugin. It remains a separate Results tab with a Trading Radar identity and does not replace or modify downloaded Custom Results plugins.

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

## Decision Gate V2

V2 adds stage-aware `Pipeline Context`:

- `Build`
- `Retest 0`
- `Retest 1`
- `Tick Real`
- `Forward`
- `Portfolio Candidate`

The verdict remains `PASS`, `REVIEW` or `BLOCK`, but thresholds now depend on stage. `Gate Score 0-100` is shown for ranking REVIEW candidates only and does not override a hard verdict.

Score weights:

- Evidence 25%
- Profitability 20%
- Risk Efficiency 25%
- Expectancy 15%
- OOS Integrity 15%

Reason chips include a repair action. Examples: low trades means no promotion and universe/TF review; low PF returns to robustness; weak Ret/DD triggers DD cluster review; missing OOS asks for sampleType/OOS confirmation.

`Decision Matrix` renders the stage thresholds, measured detail, score and repair action for every gate axis. It replaces the previous large guardrails/official-tabs panels so the first screen stays focused on operational decision quality.

## Order Radar V2

Order Radar remains opt-in. After orders are requested, V2 computes:

- max loss streak
- average loss vs worst loss
- PnL by thirds
- top 5 trade PnL concentration
- late degradation
- few-order and incomplete timestamp warnings

Order signals can harden a `PASS` to `REVIEW`, but they cannot rescue a candidate into `PASS`.

## Export

`Copy Summary` attempts clipboard copy first and falls back to a selectable textarea. No files are written from the tab.

## Boundaries

- Source-ready only until an exact install approval is supplied.
- No StrategyQuant runtime launch.
- No host data writes.
- No project/databank/task mutation.
- No Migration Tool.
- No pass-state promotion.
- No source-code export.
- No browser persistence.
