# SQX144 Custom Results3 Optional Manual Install Gate

Phase: `SQX144-CUSTOM-RESULTS3 - Optional Manual Install Gate`

Marker: `sqx144-custom-results3-optional-manual-install-gate-v1`

Source-ready status: `custom_results3_optional_manual_install_gate_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool`

Installed status: `custom_results3_all_modules_manual_install_completed_copy_only_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool`

Decision: prepare and apply a governed optional manual install gate for the SQX Edge-owned `SQX Edge Custom Results All Modules` Results Plugin. The source-ready step stayed no-install until the exact approval was supplied. After exact approval, `installExecuted=true` and only the repo-owned Results Plugin folder was copied. No SQX runtime, no data.db, no user/projects, no databank mutation, no tasks and no Migration Tool.

## Install Closeout

Applied on 2026-06-11 after exact approval:

`APRUEBO SQX144 CUSTOM RESULTS3 ALL MODULES MANUAL INSTALL host=sqx144_full plugin=sqx_edge_custom_results_all_modules sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_runtime_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_downloaded_plugins no_source_code`

Result:

- `installExecuted=true`
- `copiedFiles=3`
- `targetMatchesSource=true`
- SHA256 `4749A8393AE4418B0121962360C47B637031F171B7078EDFC93FC345B2B5077C`
- `backupCreated=false` because the target plugin folder did not exist before copy.
- Post-install preflight remained clean with `processCount=0`, blockers `[]` and warning `target_plugin_already_matches_source`.
- Evidence ref: `sqx144_custom_results3_install_apply_20260611_091433.json`.

## Scope

`SQX144-CUSTOM-RESULTS3` is the installation gate that follows `SQX144-CUSTOM-RESULTS2 - All Custom Results Modules Bundle`.

This phase adds:

- `backend/sqx-edge-tool/core/sqx144_custom_results3_install_gate.py`
- `tools/sqx144_custom_results3_install_gate.ps1`
- `backend/sqx-edge-tool/test_sqx144_custom_results3_install_gate.py`
- `tests/js/contracts/sqx144_custom_results3_install_gate_contracts.mjs`
- `docs/SQX144_CUSTOM_RESULTS3_OPTIONAL_MANUAL_INSTALL_GATE.md`

The only installable artifact under this gate is:

- Source ref: `integrations/sqx144/results_plugins/SQX Edge Custom Results All Modules`
- Target ref: `sqx144_full/user/extend/ResultsPlugins/SQX Edge Custom Results All Modules`

downloaded third-party plugin ZIPs remain not installed directly. The gate copies only the SQX Edge-owned repo bundle if the operator later provides the exact approval and preflight is clean.

## Actions

The wrapper supports:

- `status`: report source/target state and approval templates.
- `preflight`: verify source files, host root profile, ResultsPlugins root and zero SQX/Java/StrategyQuant processes.
- `plan`: produce a file-name/hash manifest and manual install plan.
- `install`: dry-run by default; copies only with `-Apply` plus exact approval.
- `rollback`: dry-run by default; restores a prior backup only with `-Apply`, backup id and exact rollback approval.
- `approval-template`: prints the exact phrases.
- `report`: combines preflight and plan; optional local ignored evidence.

## Exact Approval

Install approval phrase:

`APRUEBO SQX144 CUSTOM RESULTS3 ALL MODULES MANUAL INSTALL host=sqx144_full plugin=sqx_edge_custom_results_all_modules sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_runtime_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_downloaded_plugins no_source_code`

Rollback approval phrase:

`APRUEBO SQX144 CUSTOM RESULTS3 ALL MODULES MANUAL ROLLBACK host=sqx144_full plugin=sqx_edge_custom_results_all_modules sqx_closed backup_hash_rollback no_db_no_projects_no_databanks_no_tasks no_migration_tool`

No installation is performed unless `install -Apply -Approval "<exact phrase>"` is supplied and preflight is clean.

## Safety Contract

Required before apply:

- SQX144 Full host profile is `sqx144_full`.
- Host root leaf is `SQX_144_Full`, not the 144.2953 UPDATE2 candidate.
- `user/extend/ResultsPlugins` exists.
- SQX/Java/StrategyQuant relevant process count is zero.
- Source plugin has `index.html`, `fixtures/fixtures.js` and `README.md`.
- Target plugin, if present, must carry an SQX Edge marker before overwrite.
- Existing target is backed up before replacement.
- File names, sizes and SHA256 hashes are reported without local Windows paths.

Blocked:

- `GET_SOURCE_CODE`
- plugin create/rename/delete APIs
- downloaded third-party ZIP direct install
- SQX runtime launch
- project/databank/task execution
- `data.db`
- `user/projects`
- databank mutation
- pass-state mutation
- MT5/history import
- Migration Tool
- engine/binarios/internals copy

## Orders Policy

`SQX Edge Custom Results All Modules` includes order-based panels from CUSTOM-RESULTS2:

- `Edge Decay Analyzer`
- `WinRateEdge + RandomEntry`
- `2-Step Challenge Analyzer`

Therefore `GET_ORDERS remains privacy/performance-gated`. The install gate requires `get_orders_runtime_acknowledged` in the exact approval phrase. Repo tooling still reports `rawOrdersReturned=false` and `rawOrdersReturnedByTooling=false`. The only potential `ORDERS_RESPONSE` flow after a future install is inside the manually opened SQX Results panel, not through the gate tooling.

## Post-Install Manual Confirmation

If a future exact approval installs the plugin, the next separate human step is:

1. Restart SQX144 Full or use the Results tab reload icon.
2. Open a strategy/backtest in a databank.
3. Go to `Results`.
4. Select `SQX Edge Custom Results All Modules`.
5. Confirm the panel renders without starting a project, mutating databanks or using Migration Tool.

Suggested later confirmation status:

`custom_results3_all_modules_manual_results_tab_confirmed_no_project_run_no_databank_mutation_no_migration_tool`

## Verification

Required checks:

- `python -B -m pytest -p no:cacheprovider backend\sqx-edge-tool\test_sqx144_custom_results3_install_gate.py -q`
- `node tests\js\contracts\sqx144_custom_results3_install_gate_contracts.mjs`
- `tools\sqx144_custom_results3_install_gate.ps1 status`
- `tools\sqx144_custom_results3_install_gate.ps1 preflight`
- `tools\sqx144_custom_results3_install_gate.ps1 plan`
- `tools\sqx144_custom_results3_install_gate.ps1 approval-template`
- `tools\sqx144_custom_results3_install_gate.ps1 install -Apply -Approval "<exact phrase>"` was executed only after the exact approval above.
- `python -B -m pytest -p no:cacheprovider backend\sqx-edge-tool\test_docs_state_consistency.py -q`
- `git diff --check`

Future rollback apply commands remain blocked unless the exact rollback approval and backup id are supplied.
