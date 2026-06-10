# BS-AI9 Manual Import Execution

Marker: `bs-ai9-manual-import-execution-v1`

Status: `blocked_resource_resolution_modal_no_import_loaded`

Date: 2026-06-06

## Scope

BS-AI9 executes the first approved, visible SQX144 Full file-dialog attempt from the BS-AI8 gate.

The operator approved the exact BS-AI8 phrase for:

- candidate: `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005`
- Capa1: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_Capa1.cfx`
- Capa2: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_Capa2.cfx`
- host profile: `sqx144_full`
- mode: `no_auto_import`

The execution remained manual and visible: SQX144 Full was opened, Custom Projects was selected, `Open existing project` was pressed, and only the approved Capa1 file was submitted through the SQX file dialog. Capa2 was not attempted.

## Result

The attempt stopped at the SQX resource resolution modal.

SQX displayed `Resolve project resources` with:

- unresolved symbol: `AUDCAD`
- source: `N/A`
- status: `Not found`
- available actions observed: `Load without resolving these issues`, `Add missing symbols`, `Close`
- action taken: `Close`

The import was aborted because the modal offered actions that could either load a project with unresolved resources or create symbols in Data Manager. Under the BS-AI8 checklist, unresolved resources or import-path ambiguity require an immediate stop.

## Snapshot Check

Post-attempt local evidence records:

- `dataDbShaUnchanged=true`
- `dataDbSizeUnchanged=true`
- `projectsFileCountUnchanged=true`
- `noBSAIInHostProjects=true`
- `noAUDCADInHostProjects=true`
- `databanksDirExistsUnchanged=true`
- `tasksDirExistsUnchanged=true`

The post snapshot also records the modal outcome as `blocked_resource_resolution_modal_closed_no_load_no_add_symbol_no_start`.

## Decision

BS-AI9 is closed as blocked by target-host resource compatibility, not by the BS-AI versioning policy.

The BSAI candidate remains local-only:

- base canonical id: `BS_Filtros_v7_H1`
- source version policy: `explicit_base_preserve_official_v6_v7`
- promotion state: `local_candidate`

No official v6/v7 BlockSettings were overwritten or promoted.

## Next Gate

Recommended next gate:

`BS-AI10 target-resource compatibility gate`

BS-AI10 should audit the generated Capa1/Capa2 `.cfx` resources against the active SQX144 Full data catalog before any further import attempt. It should decide one of:

- regenerate the pair with a symbol/source known to exist in `sqx144_full`;
- add an explicit operator-approved Data Manager preparation step;
- or keep the import blocked for this asset.

BS-AI10 must not add symbols, load unresolved projects, run SQX tasks, write databanks, use Migration Tool or promote SQX144 144.2953 unless a new explicit gate allows it.

## Boundaries

BS-AI9 did not:

- load the project after the resource modal;
- accept `Load without resolving these issues`;
- accept `Add missing symbols`;
- attempt the Capa2 import;
- press any `Start` button;
- run SQX tasks, backtests, retests or optimizations;
- write SQX `data.db`;
- add a BSAI or AUDCAD project under SQX `user/projects`;
- mutate databanks;
- handle license/activation material;
- use Migration Tool;
- promote SQX144 144.2953;
- promote any BSAI candidate into the official manifest.
