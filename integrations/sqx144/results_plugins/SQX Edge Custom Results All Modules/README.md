# SQX Edge Custom Results All Modules

Marker: `sqx144-custom-results2-all-custom-results-modules-bundle-v1`

Read-only marker: `sqx144-custom-results2-readonly-all-modules-bundle-v1`

Phase: `SQX144-CUSTOM-RESULTS2 - All Custom Results Modules Bundle`

Status: `custom_results2_all_modules_bundle_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool`

This is an SQX Edge-owned repo-side StrategyQuant X 144 Custom Results bundle. It implements all studied module families in one auditable local template without copying downloaded plugin source into SQX144 Full.

Repo source: `integrations/sqx144/results_plugins/SQX Edge Custom Results All Modules`

Governed wrapper: `tools/sqx144_custom_results2_all_modules_bundle.ps1`

Contract test: `tests/js/contracts/sqx144_custom_results2_all_modules_bundle_contracts.mjs`

## Modules

- `RobustnessScorecard`
- `OOSDegradationScorecard`
- `Edge Decay Analyzer`
- `WinRateEdge + RandomEntry`
- `2-Step Challenge Analyzer`

## Contract

- Default messages: `STRATEGY_DATA`, `SET_THEME`, `GET_STATS`, `STATS_RESPONSE`.
- Optional language message: `SET_LANGUAGE`.
- Orders-enabled module messages: `GET_ORDERS`, `ORDERS_RESPONSE`.
- `GET_ORDERS remains privacy/performance-gated`.
- `ORDERS_RESPONSE fixture-only until exact future gate`.
- Blocked: `GET_SOURCE_CODE`, `resultsPlugins/create`, `resultsPlugins/rename`, `resultsPlugins/delete`, MCP calls, SQX runtime launch, data.db writes, user/projects writes, databank mutation and Migration Tool.
- `installExecuted=false`: No se instala en SQX144 in this phase.
- No SQX runtime, no data.db, no user/projects, no databank mutation and no Migration Tool.

## Fixtures

Offline fixtures live in `fixtures/fixtures.js`: `allReady`, `edgeDecay`, `winRateResearch`, `propFirm`, `blockedWeak` and `missingOrders`.

## Install Boundary

Do not copy this folder into SQX144 Full without a future exact gate. A future install must keep SQX closed, make backup/hash/rollback evidence, copy only this folder, and preserve no data.db, no user/projects, no databank mutation, no tasks and no Migration Tool.
