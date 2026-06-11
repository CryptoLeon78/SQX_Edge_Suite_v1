# SQX144 Custom Results2 All Custom Results Modules Bundle

Phase: `SQX144-CUSTOM-RESULTS2 - All Custom Results Modules Bundle`

Marker: `sqx144-custom-results2-all-custom-results-modules-bundle-v1`

Read-only marker: `sqx144-custom-results2-readonly-all-modules-bundle-v1`

Status: `custom_results2_all_modules_bundle_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool`

Decision: implement all studied Custom Results as an SQX Edge-owned repo-side bundle named `SQX Edge Custom Results All Modules`. `installExecuted=false`. No se instala en SQX144. No SQX runtime, no data.db, no user/projects, no databank mutation, no Migration Tool.

## Scope

`SQX144-CUSTOM-RESULTS2` supersedes the old idea that `CUSTOM-RESULTS2` would be an install gate. Installation is now deferred to `SQX144-CUSTOM-RESULTS3 optional manual install gate`.

This phase builds:

- `integrations/sqx144/results_plugins/SQX Edge Custom Results All Modules/index.html`
- `integrations/sqx144/results_plugins/SQX Edge Custom Results All Modules/fixtures/fixtures.js`
- `integrations/sqx144/results_plugins/SQX Edge Custom Results All Modules/README.md`
- `backend/sqx-edge-tool/core/sqx144_custom_results2_all_modules.py`
- `tools/sqx144_custom_results2_all_modules_bundle.ps1`
- `backend/sqx-edge-tool/test_sqx144_custom_results2_all_modules_bundle.py`
- `tests/js/contracts/sqx144_custom_results2_all_modules_bundle_contracts.mjs`

The bundle does not copy downloaded plugin source into SQX144 Full. It reimplements diagnostic ideas as local SQX Edge code so the behavior is auditable.

## Included Modules

| Module | Implemented | Data | Use |
| --- | --- | --- | --- |
| `RobustnessScorecard` | Yes | Stats | Core scorecard over PF, expectancy, ReturnDDRatio, trades, Stability and SQN. |
| `OOSDegradationScorecard` | Yes | Stats | IS/OOS retention review across PF, ReturnDDRatio and net profit. |
| `Edge Decay Analyzer` | Yes | Stats + orders | Research view for PF decay, worst loss and loss streak. |
| `WinRateEdge + RandomEntry` | Yes | Stats + orders | Research view for win-rate edge versus random baseline. |
| `2-Step Challenge Analyzer` | Yes | Stats + orders | Optional/commercial prop-firm diagnostic. |

## Message Contract

Allowed in the repo/offline bundle:

- `STRATEGY_DATA`
- `SET_THEME`
- `SET_LANGUAGE`
- `GET_STATS`
- `STATS_RESPONSE`
- `GET_ORDERS`
- `ORDERS_RESPONSE`

Orders policy:

- `GET_ORDERS remains privacy/performance-gated`
- `ORDERS_RESPONSE fixture-only until exact future gate`
- Tooling reports `rawOrdersReturned=false` and `rawOrdersReturnedByTooling=false`.
- The browser debug API returns `orderCount`, not raw orders.

Blocked:

- `GET_SOURCE_CODE`
- `resultsPlugins/create`
- `resultsPlugins/rename`
- `resultsPlugins/delete`
- MCP calls
- run_project
- stop_project
- SQX runtime launch
- SQX install
- browser persistence
- file writes
- MT5 import
- Migration Tool

## Why All Modules

The operator asked to implement every Custom Result regardless of whether it was previously gated or commercial. This phase does that at the repo/template level while preserving host safety:

- `RobustnessScorecard` and `OOSDegradationScorecard` remain the best immediate methodology fit.
- `Edge Decay Analyzer` is included because edge half-life and streak decay are useful before promotion.
- `WinRateEdge + RandomEntry` is included as research-only because random baseline validity needs seed/reproducibility policy.
- `2-Step Challenge Analyzer` is included as optional/commercial diagnostic, not as a core pass/fail rule.

## Install Boundary

No downloaded plugin is installed in this phase. No SQX Edge-owned plugin is installed in this phase.

Future install, if approved, must be a new `SQX144-CUSTOM-RESULTS3 optional manual install gate` with:

- SQX144 Full closed.
- Backup/hash/rollback.
- Copy only the selected SQX Edge-owned plugin folder to `<SQX144 Full>/user/extend/ResultsPlugins/<PluginName>/`.
- No data.db.
- No user/projects.
- No databank mutation.
- No tasks.
- No Migration Tool.
- Manual Results tab confirmation.

## Verification

Required checks:

- `python -B -m pytest -p no:cacheprovider backend\sqx-edge-tool\test_sqx144_custom_results2_all_modules_bundle.py -q`
- `node tests\js\contracts\sqx144_custom_results2_all_modules_bundle_contracts.mjs`
- `tools\sqx144_custom_results2_all_modules_bundle.ps1 smoke`
- `tools\sqx144_custom_results2_all_modules_bundle.ps1 report`
- `python -B -m pytest -p no:cacheprovider backend\sqx-edge-tool\test_docs_state_consistency.py -q`
- `git diff --check`

## Sources

- [StrategyQuant Results Plugins docs](https://strategyquant.com/doc/strategyquant/results-plugins/)
- [StrategyQuant Build 144 whatsnew](https://strategyquant.com/whatsnew/)
- [StrategyQuant Result Plugins codebase](https://strategyquant.com/codebase-category/result-plugins/)
- [Edge Decay Analyzer](https://strategyquant.com/codebase/edge-decay-analyzer/)
- [FTMO 2-Step Analyzer](https://strategyquant.com/codebase/the-2-step-challenge-analyzer-for-ftmo-know-if-your-strategy-will-pass-before-you-pay/)
- [WinRateEdge Results Panel](https://strategyquant.com/codebase/strategy-vs-random-edge-testing-winrateedge-results-panel/)
- [IS/OOS Degradation Score](https://strategyquant.com/codebase/is-and-oos-degradation-score/)
- [Robustness Score Card](https://strategyquant.com/codebase/robustness-score-card/)
