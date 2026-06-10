# SQX144-MT5-AUTO6 - Metadata Stability Policy

Marker: `sqx144-mt5-auto6-metadata-stability-policy-v1`
Policy id: `mt5_metadata_stability_v1`
Status marker: `metadata_stability_observe_no_apply`
Host: `sqx144_full`

## Purpose

AUTO6 defines the stability rule for live MT5 bridge metadata before any future SQX instrument metadata apply can be considered.

The key rule is conservative: the bridge is an observation stream, not direct write authority. `AUTO3 metadata_diff_only` means "a difference was observed"; it does not mean "apply the latest value".

## Policy

AUTO6 does not apply anything to SQX. It evaluates the current `SQXInfoBridge.latest.json`, the matching response history, AUTO3 catalog state and the existing SQX instrument metadata.

Default policy `mt5_metadata_stability_v1`:

- Do not apply the latest value automatically.
- Require `spreadPolicy=p90`.
- Require at least `spreadSamples>=100000`.
- Require at least `yearCount>=2`.
- Block or hold responses with `max_bars_limit_reached`.
- Hold `DEFAULTSPREAD` changes inside `+-0.1` pip.
- Require `DEFAULTSPREAD` material movement of at least `0.2` pip before it can become a future candidate.
- Cost-reducing spread changes need stronger proof: `spreadSamples>=250000`, `yearCount>=3`, and repeated observations.
- Hold `POINTVALUE` changes below `0.25%`.
- Require repeated stable observations for `POINTVALUE` changes from `0.25%` to below `1.0%`.
- Block `POINTVALUE` changes at or above `1.0%` for broker contract review.
- Require `3` matching bridge observations across at least `24` hours before `eligible_metadata_update`.
- Use a `7` day cooldown after an apply/visual closeout unless a separate conservative emergency gate raises costs materially.

AUTO6 decisions:

- `stable_no_change`: bridge and SQX already match.
- `metadata_stability_observe_no_apply`: drift exists but the policy is not satisfied.
- `stability_policy_not_satisfied`: status for observed drift held by thresholds, coverage or repeat-window rules.
- `stability_insufficient_coverage`: reason class for low samples, low years or capped bridge scans.
- `eligible_metadata_update`: stable repeated drift may be considered by a future separate AUTO5-style apply gate.
- `blocked_catalog_not_ready`: broker, instrument, history or collision state is not safe.
- `blocked_bridge_not_ready`: latest bridge response is unsafe, mismatched, missing or not the expected request.

## Current AUDCAD Decision

Baseline visually confirmed in SQX Data Manager after AUTO5:

- `AUDCAD_darwinex`
- `DEFAULTSPREAD=1.3`
- `POINTVALUE=71753.512334`
- `TICKSIZE=0.0001`
- `TICKSTEP=0.00001`

Newer post-visual bridge observation, not applied:

- Request: `sqx_auto2_AUDCAD_Darwinex_20260609_144542`
- Response hash: `3e25c7f7c1a8b5ecc829a2ab77b5eec57d34554402e7f0351aaef5408cb8d865`
- `DEFAULTSPREAD=1.2`
- `POINTVALUE=71659.930633`
- `samples=531264`
- `yearCount=2`

AUTO6 classifies this as `metadata_stability_observe_no_apply` / `stability_policy_not_satisfied`, not as an apply candidate:

- spread moved down only `0.1` pip, inside hysteresis.
- point value moved about `0.1304%`, below the `0.25%` observe threshold.
- cost-reducing spread proof is incomplete because `yearCount=2` is below the stronger `3` year requirement.
- only the latest post-visual observation is known as the new candidate, so the repeated observation window is not satisfied.

Recommended current operational state: keep the visually confirmed SQX baseline `DEFAULTSPREAD=1.3` and `POINTVALUE=71753.512334`.

## Current USDJPY Decision

Post-AUTO11 bridge observation for `USDJPY_Darwinex` is also held by AUTO6 and is not an apply candidate yet.

Observation:

- Request: `sqx_auto2_USDJPY_Darwinex_20260610_184934`
- Target instrument: `USDJPY_darwinex`
- Source symbol: `USDJPY_Darwinex`
- `spreadPolicy=p90`
- `DEFAULTSPREAD=5.0`
- `POINTVALUE=623.15779`
- `spreadSamples=2755271`
- `yearCount=10`

Drift versus current SQX baseline:

- `DEFAULTSPREAD 0.7 -> 5.0`
- `POINTVALUE 624.93 -> 623.15779`

AUTO6 classification:

- `status=stability_policy_not_satisfied`
- `decision=metadata_stability_observe_no_apply`
- `policyReasons=[repeat_observation_window_not_satisfied]`
- `matchingObservationCount=2`
- `matchingObservationWindowHours=0.0`

Recommended current operational state: keep the SQX baseline values for `USDJPY_darwinex` and collect repeated bridge observations before any future apply gate. No metadata update is eligible until AUTO6 can return `eligible_metadata_update`.

Follow-up repeat observation:

- Request: `sqx_auto2_USDJPY_Darwinex_20260610_191729`
- `DEFAULTSPREAD=1.6`
- `POINTVALUE=622.944284`
- `spreadSamples=4234681`
- `yearCount=14`
- Drift versus current SQX baseline: `DEFAULTSPREAD 0.7 -> 1.6`, `POINTVALUE 624.93 -> 622.944284`
- AUTO6 classification remains `stability_policy_not_satisfied` / `metadata_stability_observe_no_apply`
- Policy reason remains `repeat_observation_window_not_satisfied`

This repeat does not confirm the previous `DEFAULTSPREAD=5.0` candidate, so USDJPY remains observe-only.

## Current EURGBP Decision

`EURGBP_Darwinex` was tested as a second governed MT5/SQX pair after AUTO3 resolved it as `ready_existing` with target instrument `EURGBP_darwinex`.

Observation:

- Request: `sqx_auto2_EURGBP_Darwinex_20260610_191736`
- Target instrument: `EURGBP_darwinex`
- Source symbol: `EURGBP_Darwinex`
- `spreadPolicy=p90`
- `DEFAULTSPREAD=0.7`
- `POINTVALUE=133731.0`
- `spreadSamples=902086`
- `yearCount=3`

Drift versus current SQX baseline:

- `DEFAULTSPREAD 0.5 -> 0.7`
- `POINTVALUE 129882.0 -> 133731.0`

AUTO6 classification:

- `status=stability_broker_contract_review_required`
- `decision=blocked_broker_contract_review`
- `policyReasons=[broker_contract_review_required]`
- `relativeDeltaPct=2.963459`
- reason `pointvalue_delta_requires_broker_contract_review`

Recommended current operational state: keep the SQX baseline values for `EURGBP_darwinex`. Repetition alone is not enough for this candidate because AUTO6 requires broker contract review for the point value movement.

## Data Manager Install

Status: `auto6_datamanager_stability_installed_verified_no_db_no_projects_no_databanks_no_tasks`

The Data Manager overlay was installed into `SQX_144_Full` after exact operator approval on 2026-06-09.

Install evidence:

- Approval: `APRUEBO SQX144 MT5 AUTO6 DATAMANAGER STABILITY INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import`
- Backup: `sqx144_mt5_auto2_button_20260609_183452`
- Asset version: `sqx144-mt5-auto6-datamanager-stability-panel-v1`
- `targetHasAuto6=true`
- `includeCount=2`
- `processCount=0`
- Local backend on `127.0.0.1:5050` was restarted after install so the live server exposes `/api/sqx144/mt5-auto6/status` and `/api/sqx144/mt5-auto6/evaluate`.

Installed behavior:

1. AUTO4 still runs catalog triage first.
2. AUTO2 still writes only the MT5 bridge request file.
3. AUTO3 still validates the matching response with `expectedRequestId`.
4. AUTO6 then evaluates stability through `/api/sqx144/mt5-auto6/evaluate`.
5. The panel renders `Stability policy`, `Stability`, `Future gate`, `Coverage` and policy reasons as observation text only.

Local read-only endpoints:

- `/api/sqx144/mt5-auto6/status`
- `/api/sqx144/mt5-auto6/evaluate`

The panel source marker is `AUTO6_STABILITY_VERSION`. It keeps `futureApplyGateAllowed=false` visible as `blocked_by_policy` and never renders an AUTO5 apply approval phrase.

The install wrote only SQX web overlay files through the governed Data Manager overlay installer. It did not apply metadata, import history, write `data.db`, mutate projects/databanks, run SQX tasks, launch MT5 or use Migration Tool.

## Visual Smoke Selection Guard

Marker: `sqx144-mt5-auto6-datamanager-selection-guard-v1`

Status: `auto6_datamanager_selection_guard_installed_verified_no_db_no_projects_no_databanks_no_tasks`

The operator visual smoke after the AUTO6 install showed two useful outcomes:

- `DAX40_darwinex` resolves to instrument `GDAXI_darwinex` and AUTO6 correctly displays `blocked_broker_contract_review` / `blocked_by_policy` with `broker_contract_review_required`.
- With the `EURGBP_darwinex` edit modal visible, the installed overlay could still read a stale grid/context value and display `WARRANTY` plus a stale `DAX40` request. That is a selection-context bug, not a broker/catalog decision.

The selection guard was installed into `SQX_144_Full` after exact operator approval with backup `sqx144_mt5_auto2_button_20260609_191932`.

Installed guard behavior:

- visible `Edit symbol` modal controls are preferred over stale selected grid rows;
- arbitrary uppercase UI words such as `WARRANTY` are no longer accepted as symbols;
- a new request clears `lastRequestId` before catalog triage, so blocked catalog states cannot display a stale request id;
- `bridge-validate` and AUTO6 `evaluate` use the same frozen `{symbol, requestId}` context created by the button click, so later DOM/grid changes cannot redirect the active request;
- `tools\sqx144_mt5_auto2_data_manager_button_bridge.ps1 status` now exposes `sourceHasSelectionGuard=true`, `targetHasSelectionGuard=true`, `processCount=0` and the installed marker above.

The selection guard install wrote only SQX web overlay files through the governed Data Manager overlay installer. It did not apply metadata, import history, write `data.db`, mutate projects/databanks, run SQX tasks, launch MT5 or use Migration Tool.

## Gate Contract

Core:

`backend/sqx-edge-tool/core/sqx144_mt5_auto6_metadata_stability.py`

Wrapper:

`tools/sqx144_mt5_auto6_metadata_stability_policy.ps1 status|evaluate|decision-template`

Overlay install planner:

`tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1 plan`

AUTO6 is read-only:

- `writesDataDb=false`
- `writesUserProjects=false`
- `mutatesDatabanks=false`
- `runsSqxTasks=false`
- `launchesMt5=false`
- `runsMt5Ea=false`
- `usesMigrationTool=false`
- `directDbHistoryInsertAllowed=false`
- `applyAllowed=false`

Future apply gates must require `stabilityPolicy=mt5_metadata_stability_v1` and `stabilityDecision=eligible_metadata_update`, plus separate backup, response hashes, plan id, broker, instrument, observation count/window and `no_source_broker_data_history no_projects_no_databanks_no_tasks no_migration_tool`.

## Verification

Required checks:

- `tools\sqx144_mt5_auto2_data_manager_button_bridge.ps1 status`
- live `GET /api/sqx144/mt5-auto6/status`
- live `POST /api/sqx144/mt5-auto6/evaluate`
- `node --check integrations\sqx144\datamanager_mt5_auto2_overlay\sqx-edge-mt5-auto2.js`
- `node tests\js\contracts\sqx144_mt5_auto6_selection_guard_behavior.mjs`
- `python -m pytest backend\sqx-edge-tool\test_sqx144_mt5_auto6_metadata_stability.py backend\sqx-edge-tool\test_docs_state_consistency.py -q`
- `node tests\js\contracts\sqx144_mt5_auto6_metadata_stability_contracts.mjs`
- `node tests\js\contracts\sqx144_mt5_auto4_datamanager_catalog_triage_contracts.mjs`
- `python -m pytest backend\sqx-edge-tool\test_sqx144_mt5_auto5_metadata_apply.py -q`
- `node tests\js\contracts\sqx144_mt5_auto5_metadata_apply_contracts.mjs`
- `git diff --check`
