# BS-AI13 First Manual Start Gate

Marker: `bs-ai13-first-manual-start-gate-v1`

Status: `first_start_requested_observed_no_capa2_start`

## Scope

BS-AI13 executes the first controlled manual `Start` after the BS-AI11 import and BS-AI12 read-only review.

Approved target:

- Candidate: `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005`
- Started project: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa1`
- Not-started project: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa2`

The operator explicitly approved this gate on 2026-06-07 Europe/Madrid. The wrapper pressed `Start` through SQX local remote access only for Capa1.

## Tooling

- Core: `backend/sqx-edge-tool/core/bsai_first_start_gate.py`
- Wrapper: `tools/sqx144_bsai13_first_start_gate.ps1 status|preflight|start-capa1|stop-capa1`
- Python tests: `backend/sqx-edge-tool/test_bsai_first_start_gate.py`
- JS contract: `tests/js/contracts/bsai13_first_manual_start_gate_contracts.mjs`

The wrapper calls `project/start` with the approved Capa1 project name. It records sanitized evidence under the ignored BS-AI execution-gate evidence area.

## Preflight Result

Evidence: `.local/blocksettings_ai/execution_gate/bsai13_first_manual_start_gate_preflight_20260606_221720.json`

- `ok=true`
- `status=first_start_preflight_ready`
- BS-AI12 status remains `imported_project_readonly_review_passed_with_methodology_warnings_no_start`
- `targetFailCount=0`
- `targetWarnCount=2`
- Capa1 remote state: `tasks=14`, `databanks=15`, `strategies=0`, `hasUnresolvedResources=false`
- Capa2 remote state: `tasks=14`, `databanks=15`, `strategies=0`, `hasUnresolvedResources=false`
- `projectStartRequested=false`
- `runsSqxTasks=false`
- `capa2StartAllowed=false`

## Start Result

Evidence: `.local/blocksettings_ai/execution_gate/bsai13_first_manual_start_gate_start-capa1_20260606_221909.json`

- `ok=true`
- `status=first_start_requested_observed_no_capa2_start`
- `projectStartRequested=true`
- `runsSqxTasks=true`
- `hostRunMayWriteDataDb=true`
- `hostRunMayWriteUserProjects=true`
- `hostRunMayMutateTargetDatabanks=true`
- SQX returned `Project execution started.`
- Observation window: 90 seconds, polling every 10 seconds.

Observed effects:

- Capa1 created a small project log and SQX global log changed.
- Sanitized log signals show `Project started` and Capa1 loading backtest data for `AUDCAD_darwinex / H1`.
- Capa1 `project.cfx` hash stayed unchanged.
- Capa1 databank file count remained `0` during the observation window.
- Capa1 still reported `strategies=0` after the observation window.
- Capa2 remained visible with `strategies=0`, no new project files and no Start request.

This is a controlled Start smoke, not a methodology pass and not a production result.

## Post-Outage Readback

After the operator reported a power outage, `status` was run again on 2026-06-07 Europe/Madrid.

- SQX local remote access returned `remote_access_unavailable`.
- No second Start was attempted.
- Local snapshot still shows Capa1 with only `project.cfx` plus the small project log created by BS-AI13.
- Capa1 databank file count remains `0`.
- Capa2 remains unchanged with only its original `project.cfx`.

This does not revise the Start result. It means BS-AI14 must begin with a fresh SQX/remote read-only status audit before any continuation, retry, stop decision or Capa2 authorization.

## BlockSettings Trace

- Capa1 remains official: `BS_Volatilidad_v6_intraday_v6`
- Capa2 candidate remains local and not started: `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005`
- Candidate base remains `BS_Filtros_v7_H1`
- Candidate policy remains `explicit_base_preserve_official_v6_v7`
- Official v6/v7 `.sqb` files remain preserved.
- BSAI remains a local candidate and is not added to the official manifest.

## Privacy And Safety

- No host paths are returned in public output.
- No XML content is returned in public output.
- No raw logs are returned in public output.
- No secrets or license material are returned.
- SQX-returned project paths are reduced to booleans.

## Boundaries

BS-AI13 permits:

- One approved `project/start` request for the Capa1 project.
- SQX-owned writes that naturally happen inside the target project/log/databank area after Start.
- Sanitized local evidence write under ignored BS-AI evidence.

BS-AI13 blocks:

- Capa2 Start
- another `.cfx` import
- `taskmanager/openProject`
- `loadAsIs`
- resource resolution actions
- symbol creation
- direct `data.db` patching
- direct script-side `user/projects` patching
- Migration Tool
- BSAI promotion
- official v6/v7 overwrite
- 144.2953 promotion
- profitability, pass-rate or risk-zero claims

## Next Gate

`BS-AI14 monitor Capa1 run and decide Capa2 start`

The next gate should first restore/read SQX remote status after the outage, then add explicit engine/progress observability, likely through SQX websocket channels, before deciding whether to let Capa1 continue, stop/retry, inspect settings, or later authorize Capa2.
