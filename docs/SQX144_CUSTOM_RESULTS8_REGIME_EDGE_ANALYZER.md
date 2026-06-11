# SQX144 CUSTOM RESULTS8 Regime Edge Analyzer

Phase: `SQX144-CUSTOM-RESULTS8 - Regime Edge Analyzer`

Marker: `sqx144-custom-results8-regime-edge-analyzer-v1`

Read-only marker: `sqx144-custom-results8-readonly-regime-edge-analyzer-v1`

Source-ready status: `custom_results8_regime_edge_analyzer_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool`

Installed status: `custom_results8_regime_edge_analyzer_installed_copy_only_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool`

Date: 2026-06-11

Install date: 2026-06-12

## Purpose

CUSTOM-RESULTS8 adds the SQX Edge-owned `Regime Edge Analyzer` ResultsPlugin as a separate tab for selected-strategy market regime diagnostics.

It does not replace `SQX Edge Gate`, does not modify the original downloaded Custom Results, and does not enumerate full databanks from the iframe. V1 analyzes the selected strategy only. V2 full-databank analysis remains dependent on a separate governed read-only provider or manual list flow.

## Plugin Source

- Source: `integrations/sqx144/results_plugins/Regime Edge Analyzer`
- Runtime files: `index.html`, `regime-edge.js`, `fixtures/fixtures.js`
- Locales: `locales/en.json`, `locales/es.json`
- Wrapper: `tools/sqx144_custom_results8_regime_edge_analyzer.ps1`
- Core: `backend/sqx-edge-tool/core/sqx144_custom_results8_regime_edge_analyzer.py`
- Tests: `backend/sqx-edge-tool/test_sqx144_custom_results8_regime_edge_analyzer.py`
- JS contract: `tests/js/contracts/sqx144_custom_results8_regime_edge_analyzer_contracts.mjs`
- Render smoke: `tests/js/contracts/sqx144_custom_results8_regime_edge_analyzer_render_smoke.mjs`

## Message Contract

Default messages:

- `STRATEGY_DATA`
- `SET_THEME`
- `SWITCH_THEME`
- `SET_LANGUAGE`
- `GET_STATS`
- `STATS_RESPONSE`

Opt-in messages:

- `GET_ORDERS`
- `ORDERS_RESPONSE`

`GET_ORDERS opt-in` means the plugin sends no order request on load, no order request after `STRATEGY_DATA`, and no order request after `STATS_RESPONSE`. It only sends `GET_ORDERS` after the operator presses `Activar Regime Orders`.

Blocked:

- `GET_SOURCE_CODE`
- remote fetch
- browser persistence
- plugin create/rename/delete endpoints
- file writes from the runtime
- `data.db`
- `user/projects`
- databank mutation
- SQX tasks
- Migration Tool

## Regime Methodology

The tab classifies annual market context as `BULL`, `BEAR`, `SIDEWAYS`, `MIXED` or `UNKNOWN`, then compares selected-strategy orders against detected or overridden direction:

- `long_only`: aligned regime is `BULL`; `BEAR` is adverse.
- `short_only`: aligned regime is `BEAR`; `BULL` is adverse.
- `long_short`: `BULL` and `BEAR` can both be aligned depending on side evidence.
- `mean_reversion`: `SIDEWAYS` is the primary aligned regime.

Decision labels:

- `REGIME_STRONG`
- `REGIME_COMPATIBLE`
- `REGIME_DEFENSIVE`
- `REGIME_MEAN_REVERT`
- `REGIME_MISMATCH_REVIEW`
- `REGIME_ADVERSE_RISK`
- `REGIME_INSUFFICIENT`
- `REGIME_UNKNOWN`

The score combines aligned edge, adverse survival, yearly consistency and data quality. Regime evidence can downgrade confidence or force review, but it never promotes a strategy by itself.

## Market Series Provider

V1 ships with fixtures and embedded/manual fallback for offline smoke and source-ready validation.

The robust path is a future Data Manager read-only provider if OHLC series can be accessed without touching `data.db`, `user/projects`, databanks, tasks or Migration Tool. If that provider requires browser calls, only a future exact gate may allow a localhost-only endpoint. No remote fetch is allowed in this phase.

## Academic Review

CUSTOM-RESULTS8 was planned and implemented with `sqx-academic-lopez` review.

Academic cautions used:

- Bailey, Borwein, Lopez de Prado and Zhu, Probability of Backtest Overfitting: repeated model selection on the same evidence increases overfitting risk.
- Bailey and Lopez de Prado, Deflated Sharpe Ratio: selection bias and non-normality can inflate apparent performance.
- Hamilton 1989 regime switching: regimes are latent/nonstationary states; `BULL/BEAR/SIDEWAYS` diagnostics are useful labels, not proof of causal stable states.

Sources:

- <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253>
- <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551>
- <https://www.jstor.org/stable/1912559>

## Source-Ready Closeout

Source-ready status:

- `installExecuted=false`
- No se instala en SQX144
- No SQX runtime
- no data.db
- no user/projects
- no databank mutation
- no tasks
- no Migration Tool
- no source-code export

Install target:

- `sqx144_full/user/extend/ResultsPlugins/Regime Edge Analyzer`

Install approval phrase applied:

`APRUEBO SQX144 CUSTOM RESULTS8 REGIME EDGE ANALYZER INSTALL host=sqx144_full plugin=sqx_regime_edge_analyzer sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_optin_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_source_code`

## Install Closeout

Installed verification:

- `installExecuted=true`
- `currentlyInstalled=true`
- `copiedFiles=6`
- `targetMatchesSource=true`
- SHA256 `893DE84B706FD208774DF8C74A2A256782159B5DA76E5EEFF04337B6BC8ED8BE`
- `backupCreated=false` because the target did not exist
- preflight `processCount=0`
- blockers `[]`
- warnings `[]`
- evidence `.local/sqx144_custom_results8/sqx144_custom_results8_install_20260611_220624.json`

Install boundary:

- Copied only `Regime Edge Analyzer`.
- Did not launch SQX runtime.
- Did not touch `SQX Edge Gate`.
- Did not touch original downloaded Custom Results tabs.
- Did not touch `data.db`.
- Did not touch `user/projects`.
- Did not mutate databanks.
- Did not run SQX tasks.
- Did not use Migration Tool.
- Did not access/export source code.

## Real Runtime Smoke

Real smoke status 2026-06-12:

- `realSmokeRuntime=true`
- SQX144 Full started manually through `StrategyQuantX.exe` for verification only.
- SQX reported build `144.2938` and loaded the UI through `http://localhost:8080`.
- Runtime endpoint `GET /resultsPlugins/list` returned `Regime Edge Analyzer` as a non-default plugin.
- Runtime URL `http://localhost:8080/plugins/Regime%20Edge%20Analyzer/index.html` returned HTTP `200`.
- Served HTML contains marker `sqx144-custom-results8-regime-edge-analyzer-v1`.
- Served HTML contains debug API `window.__SQX_REGIME_EDGE__`.
- Playwright render smoke of the served plugin returned `ok=true`, `hasTitle=true`, `hasRegimeLabels=true`, `hasDebug=true`, `consoleErrors=[]`.
- Evidence stored locally under `.local/sqx144_custom_results8/` as runtime smoke JSON/PNG artifacts.

Real smoke boundaries:

- No SQX task was started.
- No project/databank action was triggered.
- No order request was triggered.
- No `GET_SOURCE_CODE` was used.
- Runtime startup warnings related to external customization/subscription checks were observed, but no Regime Edge Analyzer load error was found.

## Verification

Required checks:

- `python -B -m pytest -p no:cacheprovider backend\sqx-edge-tool\test_sqx144_custom_results8_regime_edge_analyzer.py -q`
- `node tests\js\contracts\sqx144_custom_results8_regime_edge_analyzer_contracts.mjs`
- `node tests\js\contracts\sqx144_custom_results8_regime_edge_analyzer_render_smoke.mjs`
- `tools\sqx144_custom_results8_regime_edge_analyzer.ps1 status`
- `tools\sqx144_custom_results8_regime_edge_analyzer.ps1 smoke`
- `tools\sqx144_custom_results8_regime_edge_analyzer.ps1 report`
- `python -B -m pytest -p no:cacheprovider backend\sqx-edge-tool\test_docs_state_consistency.py -q`
- `git diff --check`

## Install Boundaries

- No SQX runtime launch during install.
- No `data.db` mutation.
- No `user/projects` mutation.
- No databank mutation.
- No SQX tasks.
- No Migration Tool.
- No source-code access/export.
- No replacement or modification of `SQX Edge Gate`.
- No replacement or modification of original Custom Results tabs.
- No profitability guarantee, no risk-zero claim and no automatic promotion inside SQX.
