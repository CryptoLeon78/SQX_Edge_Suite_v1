# SQX Edge Custom Results Template

Marker: `sqx144-custom-results1-results-plugin-template-v1`

Read-only marker: `sqx144-custom-results1-readonly-results-plugin-template-v1`

Phase: `SQX144-CUSTOM-RESULTS1 - Read-Only Results Plugin Template`

Status: `custom_results1_template_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool`

This is an SQX Edge-owned StrategyQuant X 144 Results Plugin template. It is a repo-side template only until a later explicit install gate copies it to a governed SQX144 Full host.

## Default Contract

- Entry point: `index.html`.
- Offline fixtures: `fixtures/fixtures.js`.
- Optional language payloads: `locales/en.json` and `locales/es.json`.
- Repo source: `integrations/sqx144/results_plugins/SQX Edge Custom Results Template`.
- Governed wrapper: `tools/sqx144_custom_results1_results_plugin_template.ps1`.
- Contract test: `tests/js/contracts/sqx144_custom_results1_results_plugin_template_contracts.mjs`.
- Default messages used by the template: `STRATEGY_DATA`, `SET_THEME`, `SET_LANGUAGE`, `GET_STATS`, `STATS_RESPONSE`.
- Optional future modules need a separate gate before using `GET_LAST_SETTINGS_XML`, `GET_SYMBOL_INFO`, `LAST_SETTINGS_XML_RESPONSE` or `SYMBOL_INFO_RESPONSE`.
- `GET_ORDERS` is research-only and blocked in this phase until a privacy/performance gate is opened.
- Blocked by default: `GET_SOURCE_CODE`, `GET_ORDERS`, `resultsPlugins/create`, `resultsPlugins/rename`, `resultsPlugins/delete`, MCP calls, browser persistence, file writes, MT5 import, SQX install and databank mutation.

## Install Boundary

Do not copy this folder into SQX144 Full without an exact operator gate. A future install must keep SQX closed, make a backup, verify hashes and preserve: installExecuted=false for this phase, No se instala en SQX144, No SQX runtime, no data.db, no user/projects, no databank mutation, no tasks and no Migration Tool.
