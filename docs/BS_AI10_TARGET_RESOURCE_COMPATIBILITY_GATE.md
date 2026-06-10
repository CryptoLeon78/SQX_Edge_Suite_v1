# BS-AI10 Target Resource Compatibility Gate

Marker: `bs-ai10-target-resource-compatibility-gate-v1`

Status: `remap_ready_for_manual_import_gate_no_import`

Date: 2026-06-06

## Scope

BS-AI10 audits BS-AI generated `.cfx` resources against the real `sqx144_full` local catalog before another manual import attempt.

This phase is a compatibility/remap gate only. It does not open SQX, does not import `.cfx`, does not accept unresolved resources and does not add symbols.

## Implemented Gate

- Core module: `backend/sqx-edge-tool/core/bsai_resource_compatibility.py`
- Wrapper: `tools/sqx144_bsai_resource_compat_gate.ps1 status|audit|remap`
- Contract test: `tests/js/contracts/bsai10_target_resource_compatibility_contracts.mjs`
- Python tests: `backend/sqx-edge-tool/test_bsai_resource_compatibility.py`

The gate reads the target catalog with `sqlite_uri_mode_ro_query_only`, returns only sanitized symbol/source/broker evidence and keeps `localPathsReturned=false` and `rawXmlReturned=false`.

## Target Catalog Result

For `sqx144_full`, candidate `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005` and asset `AUDCAD`, the read-only catalog audit found:

- exact `AUDCAD`: absent for loaded target data
- primary expected symbol: `AUDCAD_darwinex`
- primary expected source/broker: source `4`, broker `4`
- governed cross-broker OOS symbol: `AUDCAD_dukascopy`
- `AUDCAD_darwinex`: present with loaded rows
- `AUDCAD_dukascopy`: present with loaded rows
- table counts observed: `DATA=54`, `INSTRUMENTS=989`, `BROKER=12`

## Original Pair Decision

Original BS-AI9 files:

- Capa1: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_Capa1.cfx`
- Capa2: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_Capa2.cfx`

Audit result:

- `targetResourceVerdict=fail`
- `gateStatus=blocked_target_resource_mismatch`
- `recommendation=regenerate_with_target_profile_sqxedge_darwinex`
- primary mismatch count: `26`
- governed Dukascopy warnings: `2`

Reason: primary tasks still used `AUDCAD` with source `0` and broker `-1`, while `sqx144_full` requires `AUDCAD_darwinex` with source `4` and broker `4`.

## Remapped Pair

BS-AI10 generated a new local-only pair using target profile `sqxedge_darwinex` and suffix `SQX144DARWINEX`:

- Capa1: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa1.cfx`
- Capa2: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa2.cfx`

Audit result:

- `targetResourceVerdict=warn`
- `targetFailCount=0`
- `gateStatus=ready_for_manual_import_gate_with_methodology_warnings`
- static CFX audit: `warn` only for governed `dukascopy_dependency`
- wrapper status: `remap_ready_for_manual_import_gate_no_import`

The remapped pair uses `AUDCAD_darwinex` for primary resources. `AUDCAD_dukascopy` remains only in the governed cross-broker OOS tasks and is recorded as `methodology_cross_broker_catalog_match`.

## Evidence

- Local evidence file: `.local/blocksettings_ai/resource_compat/bsai10_target_resource_compat_20260606_202501.json`
- SQX process count during wrapper execution: `0`
- generated remapped files exist and are ZIP `.cfx` artifacts with `config.xml`

## Boundaries

BS-AI10 preserved:

- `writesSqxHost=false`
- `writesDataDb=false`
- `writesUserProjects=false`
- `mutatesDatabanks=false`
- `runsSqxTasks=false`
- `readOnlyDataDb=true`
- `noAutoImport=true`
- no SQX launch
- no `.cfx` import
- no unresolved resource load
- no symbol creation in Data Manager
- no official v6/v7 BlockSettings overwrite
- no BSAI promotion into the official manifest
- no Migration Tool
- no SQX144 144.2953 promotion

## Next Gate

Recommended next gate:

`BS-AI11 remapped manual import gate`

BS-AI11 should require explicit operator approval before any visible SQX file-dialog attempt with the remapped pair:

- candidate: `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005`
- Capa1: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa1.cfx`
- Capa2: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa2.cfx`
- host: `sqx144_full`
- mode: `no_auto_import`

BS-AI11 is still not permission to run SQX tasks, write databanks, save into host project stores or promote the BSAI candidate.
