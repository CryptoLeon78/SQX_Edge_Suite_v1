# SQX144 Custom Results1 Read-Only Results Plugin Template

Phase: `SQX144-CUSTOM-RESULTS1 - Read-Only Results Plugin Template`

Marker: `sqx144-custom-results1-results-plugin-template-v1`

Read-only marker: `sqx144-custom-results1-readonly-results-plugin-template-v1`

Status: `custom_results1_template_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool`

Decision: prepare and verify `SQX Edge Custom Results Template` as a repo-side StrategyQuant X 144 Custom Results / Results Plugin template. `installExecuted=false`. No se instala en SQX144 in this phase. No SQX runtime, no data.db, no user/projects, no databank mutation, no Migration Tool.

## Scope

`SQX144-CUSTOM-RESULTS1` studies Build 144 Custom Results as read-only Results Plugins and produces a reusable SQX Edge-owned template under `integrations/sqx144/results_plugins/SQX Edge Custom Results Template`. The template is source-ready only. It is not copied to `<SQX144 Full>/user/extend/ResultsPlugins`.

Main artifacts:

- `integrations/sqx144/results_plugins/SQX Edge Custom Results Template/index.html`
- `integrations/sqx144/results_plugins/SQX Edge Custom Results Template/fixtures/fixtures.js`
- `integrations/sqx144/results_plugins/SQX Edge Custom Results Template/locales/en.json`
- `integrations/sqx144/results_plugins/SQX Edge Custom Results Template/locales/es.json`
- `tools/sqx144_custom_results1_results_plugin_template.ps1`
- `tools/sqx144_custom_results1_study.ps1`
- `backend/sqx-edge-tool/core/sqx144_custom_results1_study.py`
- `backend/sqx-edge-tool/test_sqx144_custom_results1_results_plugin_template.py`
- `tests/js/contracts/sqx144_custom_results1_results_plugin_template_contracts.mjs`

## Entry Workflow After Future Approval

This is the operator workflow only after a later exact install gate:

1. Close SQX144 Full.
2. Backup the target plugin folder if it exists and record hashes.
3. Copy only the complete plugin folder to `<SQX144 Full>/user/extend/ResultsPlugins/<PluginName>/`.
4. Restart SQX144 Full or use the Results tab reload icon.
5. Open a strategy/backtest in a databank.
6. Go to `Results` and select the Custom Results plugin from the Results tab strip.
7. Confirm manually that the panel renders and does not run a project, mutate a databank or change pass states.

Install gate wording must include: `host=sqx144_full`, SQX closed, backup/hash/rollback, no data.db, no user/projects, no databank mutation, no tasks, no Migration Tool. This phase keeps `installExecuted=false`.

## PostMessage Contract

Allowed by default in this template:

- `STRATEGY_DATA`
- `SET_THEME`
- `SET_LANGUAGE`
- `GET_STATS`
- `STATS_RESPONSE`

Optional future modules need a separate gate:

- `GET_LAST_SETTINGS_XML`
- `GET_SYMBOL_INFO`
- `LAST_SETTINGS_XML_RESPONSE`
- `SYMBOL_INFO_RESPONSE`

Research-only and blocked in this phase:

- `GET_ORDERS`

Blocked by default:

- `GET_SOURCE_CODE`
- `resultsPlugins/create`
- `resultsPlugins/rename`
- `resultsPlugins/delete`
- MCP calls
- browser persistence
- file writes
- MT5 import
- SQX install
- SQX runtime
- run_project
- stop_project
- Migration Tool

## Candidate Matrix

| Candidate | Fit | SQX Edge value | Gate notes |
| --- | --- | --- | --- |
| `RobustnessScorecard` | Best immediate fit | Converts existing stats into a readiness scorecard. Good candidate for Capa1/Capa2 review UI because it is mainly `GET_STATS`. | Keep as inspiration; do not install downloaded ZIP in SQX144 Full in this phase. |
| `OOSDegradationScorecard` | Best immediate fit | Directly supports IS/OOS retention and degradation review, useful for our methodology before promoting a strategy. | Main input for the first SQX Edge template logic. |
| `Edge Decay Analyzer` | Strong but gated | Valuable for edge half-life, loss streaks, MFE/MAE and decay diagnostics. | Requires `GET_ORDERS` and likely browser persistence; needs privacy/performance gate. |
| `WinRateEdge + RandomEntry` | Research-only | Useful for checking whether win rate/edge beats random-entry baseline. | Requires full orders plus Random Entry snippet/block workflow and seed policy. |
| `2-Step Challenge Analyzer` | Optional commercial | Useful for FTMO/prop-firm pass probability, drawdown and challenge economics. | Not core SQX Edge methodology; keep optional/commercial. |
| `Robustness Score Card` | Best immediate fit | Reinforces scorecard-style UX for robust filters. | Similar source family to `RobustnessScorecard`; keep local scanner public-safe. |

Recommendation:

- Build first from `RobustnessScorecard` and `OOSDegradationScorecard` ideas.
- Keep `Edge Decay Analyzer` as the first future `GET_ORDERS` research gate.
- Keep `WinRateEdge + RandomEntry` for a separate random-baseline methodology block.
- Keep `2-Step Challenge Analyzer` outside the core pipeline unless a prop-firm product gate is opened.

## Template Design

`SQX Edge Custom Results Template` is a local static template with:

- `index.html` as entry point.
- Local `fixtures/fixtures.js` for offline smoke cases: `ready`, `review`, `blocked`, `noStrategy`, `missingStats`, `largePortfolio`.
- Optional locale payloads `locales/en.json` and `locales/es.json`.
- A compact three-panel layout: context, readiness, guards.
- Exposed debug API `window.__SQX_EDGE_CUSTOM_RESULTS_TEMPLATE__`.
- No remote fetch, no browser persistence, no source code request and no orders request.

The first implementation uses local JS instead of shipping a Vue runtime. A later gate can add a local Vue runtime copied from an approved, auditable source if we decide that component structure is worth the extra dependency.

## Test Plan

Static scanner:

- Scan downloaded candidates from the operator download folder or `SQX_CUSTOM_RESULTS_DOWNLOADS`.
- Detect `GET_SOURCE_CODE`, `GET_ORDERS`, `resultsPlugins/create`, `resultsPlugins/rename`, `resultsPlugins/delete`, local/remote `fetch`, browser persistence and write-like markers.
- Return only public-safe inventory: no raw local paths, no raw strategy names, no orders, no source code, no secrets.

Offline smoke:

- `tools/sqx144_custom_results1_results_plugin_template.ps1 smoke`
- Check required files, markers, locales, fixtures and absence of forbidden markers in `index.html` and fixtures.

Contracts:

- `python -B -m pytest -p no:cacheprovider backend\sqx-edge-tool\test_sqx144_custom_results1_results_plugin_template.py -q`
- `node tests\js\contracts\sqx144_custom_results1_results_plugin_template_contracts.mjs`
- `python -B -m pytest -p no:cacheprovider backend\sqx-edge-tool\test_docs_state_consistency.py -q`

Future install smoke, only after approval:

- Preflight SQX processes.
- Copy only plugin folder.
- Verify hashes.
- Open Results manually.
- Confirm no project run and no databank mutation.

## Sources

- [StrategyQuant Results Plugins docs](https://strategyquant.com/doc/strategyquant/results-plugins/)
- [StrategyQuant Build 144 whatsnew](https://strategyquant.com/whatsnew/)
- [Edge Decay Analyzer](https://strategyquant.com/codebase/edge-decay-analyzer/)
- [FTMO 2-Step Analyzer](https://strategyquant.com/codebase/the-2-step-challenge-analyzer-for-ftmo-know-if-your-strategy-will-pass-before-you-pay/)
- [WinRateEdge Results Panel](https://strategyquant.com/codebase/strategy-vs-random-edge-testing-winrateedge-results-panel/)
- [IS/OOS Degradation Score](https://strategyquant.com/codebase/is-and-oos-degradation-score/)
- [Robustness Score Card](https://strategyquant.com/codebase/robustness-score-card/)

## Next Gate

Recommended next gate is superseded by `SQX144-CUSTOM-RESULTS2 - All Custom Results Modules Bundle` for repo-side implementation of all studied modules. Any manual install is deferred to `SQX144-CUSTOM-RESULTS3 optional manual install gate`, only if the operator wants to copy an SQX Edge-owned plugin into SQX144 Full. Downloaded third-party plugins remain research inputs and are not installed by this phase.
