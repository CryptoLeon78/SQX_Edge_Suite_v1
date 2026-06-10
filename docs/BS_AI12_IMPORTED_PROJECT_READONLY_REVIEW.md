# BS-AI12 Imported Project Read-Only Review

Marker: `bs-ai12-imported-project-readonly-review-v1`

Status: `imported_project_readonly_review_passed_with_methodology_warnings_no_start`

## Scope

BS-AI12 reviews the two BS-AI11 imported SQX144 Full Custom Projects in read-only mode:

- `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa1`
- `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa2`

It does not import, start, optimize, retest, save, resolve resources, add symbols, mutate databanks or promote any BSAI candidate.

## Tooling

- Core: `backend/sqx-edge-tool/core/bsai_imported_project_review.py`
- Wrapper: `tools/sqx144_bsai12_imported_project_review.ps1 status|review`
- Python tests: `backend/sqx-edge-tool/test_bsai_imported_project_review.py`
- JS contract: `tests/js/contracts/bsai12_imported_project_readonly_review_contracts.mjs`

The wrapper only calls `taskmanager/listProjects` and reads the already imported `project.cfx` archives as ZIP files. It records sanitized evidence under the local ignored BS-AI import-gate evidence area.

## Review Result

Evidence: `.local/blocksettings_ai/import_gate/bsai12_imported_project_readonly_review_20260606_215157.json`

- `ok=true`
- `status=imported_project_readonly_review_passed_with_methodology_warnings_no_start`
- `tasks=14` for Capa1 and `tasks=14` for Capa2
- `databanks=15` for both imported projects
- `strategies=0` for both imported projects
- `hasUnresolvedResources=false` for both imported projects
- `targetFailCount=0`
- `targetWarnCount=2`
- `readOnlyReview=true`
- `projectStartRequested=false`
- `runsSqxTasks=false`
- `writesDataDb=false`
- `writesUserProjects=false`
- `mutatesDatabanks=false`

## BlockSettings Trace

Candidate reviewed:

- `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005`
- `baseCanonicalId=BS_Filtros_v7_H1`
- `sourceVersionPolicy=explicit_base_preserve_official_v6_v7`
- `promotionState=local_candidate`

Imported project traces:

- Capa1 active build BlockSetting: `BS_Volatilidad_v6_intraday_v6`
- Capa2 active build BlockSetting: `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005`
- Official v6/v7 BlockSettings remain preserved.
- BSAI remains a local candidate and is not added to the official manifest.

## Resource Trace

Target catalog mode: `sqlite_uri_mode_ro_query_only`

- Primary target resource: `AUDCAD_darwinex`
- Governed cross-broker OOS resource: `AUDCAD_dukascopy`
- Capa1 resource groups: 13 primary `AUDCAD_darwinex`, 1 governed `AUDCAD_dukascopy`
- Capa2 resource groups: 13 primary `AUDCAD_darwinex`, 1 governed `AUDCAD_dukascopy`
- Methodology warnings: `methodology_cross_broker_catalog_match` for the expected cross-broker OOS tasks.

These warnings are expected and do not authorize execution by themselves.

## Privacy And Safety

- No host paths are returned in public output.
- No XML content is returned in public output.
- No secrets or license material are returned.
- The SQX path reported by remote access is reduced to a boolean that confirms SQX had a project path internally; the path itself is not stored.

## Boundaries

BS-AI12 permits:

- Read-only remote project listing through `taskmanager/listProjects`.
- Read-only ZIP/config/task/resource inspection of the two imported projects.
- Sanitized local evidence write under ignored BS-AI evidence.

BS-AI12 blocks:

- `Start`
- SQX task execution
- `taskmanager/openProject`
- `loadAsIs`
- resource resolution actions
- symbol creation
- direct `data.db` writes
- direct `user/projects` writes
- databank mutation
- Migration Tool
- BSAI promotion
- official v6/v7 overwrite
- 144.2953 promotion

## Next Gate

`BS-AI13 first manual Start gate requires explicit operator approval`

That gate must be separate, explicit and narrow. It should define exactly which project, which task, what pre-run snapshot, what stop condition and what post-run audit are allowed before pressing `Start`.
