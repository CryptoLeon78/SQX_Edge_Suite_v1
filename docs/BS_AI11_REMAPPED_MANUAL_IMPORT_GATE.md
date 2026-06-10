# BS-AI11 Remapped Manual Import Gate

Marker: `bs-ai11-remapped-manual-import-gate-v1`

Status: `remapped_capa1_capa2_imported_visible_no_tasks_started`

Date: 2026-06-06

## Scope

BS-AI11 executes the explicitly approved first controlled import of the BS-AI10 remapped pair into the confirmed `sqx144_full` host.

This phase imports the remapped `.cfx` pair only. It does not press `Start`, does not run SQX tasks, does not mutate databanks, does not use Migration Tool and does not promote any `BSAI_*` candidate into the official BlockSettings manifest.

## Approval And Target

Operator approval was explicit for:

- candidate: `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005`
- Capa1: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa1.cfx`
- Capa2: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa2.cfx`
- host: `sqx144_full`
- mode: controlled local SQX remote access on port `8080`

## Implementation

- Wrapper: `tools/sqx144_bsai11_remapped_import_gate.ps1 status|preflight|snapshot|launch|capture|import-capa1|import-capa2`
- Version: `bs-ai11-remapped-manual-import-gate-v1`
- Import endpoint: `taskmanager/openProject`
- Import request: `loadAsIs=false`
- Escalation blocked: `loadAsIsEscalated=false`
- Task start blocked: `projectStartRequested=false`, `runsSqxTasks=false`, `startButtonAllowed=false`

The first visible remote UI attempt confirmed Custom Projects was reachable. Browser-side screenshot capture of the remote canvas was unstable, so BS-AI11 used the same local SQX endpoint that the UI calls after `Open existing project`, with sanitized evidence and no raw XML storage.

## Import Result

Capa1:

- `status=import_request_accepted_project_visible_no_tasks_started`
- `hasResourcesXML=false`
- `hasConfigXML=false`
- imported project: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa1`
- `.cfx` SHA256: `58F84787605DC107B48FDB635FF8EDC2B76CF9BFCA10DF12107D031BDC175B67`

Capa2:

- `status=import_request_accepted_project_visible_no_tasks_started`
- `hasResourcesXML=false`
- `hasConfigXML=false`
- imported project: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa2`
- `.cfx` SHA256: `EE2827C6C389DA24D4369527B95750BB01690F3837BF465A076E79C69EDBBE8E`

SQX project list after import:

- matching BSAI projects: `2`
- each imported project reports `tasks=14`
- each imported project reports `databanks=15`
- each imported project reports `strategies=0`
- each imported project reports `hasUnresolvedResources=false`

Final snapshot:

- evidence: `.local/blocksettings_ai/import_gate/bsai11_after_api_import_capa2_ui_verified_snapshot_20260606_211130.json`
- `projectsFileCount=2158`
- `projectsMatchCount=2`
- `dataDbHashStatus=unavailable_file_locked_or_unreadable` because SQX was open and owned the file lock

## Evidence

- Pre-remote snapshot: `.local/blocksettings_ai/import_gate/bsai11_pre_remote_import_snapshot_20260606_210034.json`
- Before Capa1 import: `.local/blocksettings_ai/import_gate/bsai11_before_api_import_capa1_snapshot_20260606_210844.json`
- Capa1 import evidence: `.local/blocksettings_ai/import_gate/bsai11_api_open_capa1_20260606_210916.json`
- After Capa1 snapshot: `.local/blocksettings_ai/import_gate/bsai11_after_api_import_capa1_snapshot_20260606_210929.json`
- Capa2 import evidence: `.local/blocksettings_ai/import_gate/bsai11_api_open_capa2_20260606_210941.json`
- Final snapshot: `.local/blocksettings_ai/import_gate/bsai11_after_api_import_capa2_ui_verified_snapshot_20260606_211130.json`

No evidence file stores raw `configXML` or `resourcesXML`; only presence flags and lengths are recorded. Public script output does not return local file paths.

## Boundaries

BS-AI11 allows:

- controlled import through SQX local remote access
- SQX-owned update of its project store caused by `openProject`
- read-only project-list verification after import

BS-AI11 blocks:

- `Load without resolving these issues`
- `Add missing symbols`
- `loadAsIs=true`
- pressing `Start`
- SQX task execution
- direct `data.db` writes by Codex tooling
- direct databank mutation
- Migration Tool
- license, activation or bypass handling
- official BlockSettings overwrite
- `BSAI_*` promotion into the official manifest
- SQX144 144.2953 promotion
- profitability or risk-zero claims

## Next Gate

Recommended next gate:

`BS-AI12 imported project read-only review`

BS-AI12 should inspect the imported Capa1/Capa2 task settings, BlockSettings traces and resource shapes from SQX without pressing `Start`. Any first execution must remain a later explicit operator gate.
