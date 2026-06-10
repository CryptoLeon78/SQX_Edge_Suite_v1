# BS-AI8 First Import Gate

Marker: `bs-ai8-first-import-gate-v1`

Status: `checklist_ready_operator_approval_required_no_import`

Date: 2026-06-06

## Scope

BS-AI8 prepares the first controlled manual import of a BS-AI generated project pair into SQX144 Full, but it does not perform the import.

The phase creates a dry-run gate, validates the selected candidate/project artifacts and defines the exact operator approval phrase required before any SQX import step can begin. This is an authorization boundary between the safe BS-AI7 panel smoke and a future manual import execution gate.

## Selected First Import Candidate

The first controlled import candidate is the H1 explicit-v7 branch proven in BS-AI7:

- candidate: `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005`
- candidate file: `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005.sqb`
- asset: `AUDCAD`
- timeframe: `H1`
- direction: `long`
- base canonical id: `BS_Filtros_v7_H1`
- source version policy: `explicit_base_preserve_official_v6_v7`
- promotion state: `local_candidate`
- active blocks: `21`
- active indicators: `4`
- Capa1: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_Capa1.cfx`
- Capa2: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_Capa2.cfx`

The D1 default branch remains a proven alternate, not the first import target:

- candidate: `BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r005`
- base canonical id: `BS_Filtros_v6_D1`
- visible policy proven in BS-AI7: `D1 default v6_D1`

## Gate Tool

Tool:

`tools\sqx144_bsai_first_import_gate.ps1`

Allowed actions:

- `status`
- `plan`
- `approval-template`

The tool intentionally has no `apply`, `install`, `import`, `copy`, `write` or `launch` action.

Current gate result:

- version: `bs-ai8-first-import-gate-v1`
- status: `approval_required_no_import`
- `ok=true`
- `importAllowed=false`
- `requiresOperatorApproval=true`
- `writesSqxHost=false`
- `writesDataDb=false`
- `writesUserProjects=false`
- `mutatesDatabanks=false`
- `runsSqxTasks=false`
- privacy: `localPathsReturned=false`, `tokensReturned=false`, `licenseMaterialReturned=false`
- host profile: `sqx144_full`
- artifacts: Capa1 and Capa2 are ZIP-valid with `config.xml`
- current warning: `sqx_process_running_no_automation` because SQX is open from the visual smoke; the gate still performs no automation.

## Checklist

Before any future import execution phase:

1. Confirm the active host is SQX144 Full / `sqx144_full`, not the separate 144.2953 candidate.
2. Confirm BS-AI7 remains closed as `operator_panel_hardening_smoke_confirmed_no_import`.
3. Confirm the first import target is exactly `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005`.
4. Confirm Capa1 and Capa2 filenames match the selected candidate exactly.
5. Confirm candidate metadata is local-only: `sourceScope=local_candidate` and `promotionState=local_candidate`.
6. Confirm the candidate does not collide with any official BlockSettings canonical id or filename.
7. Confirm `BS_Filtros_v7_H1` is explicit selection only and no default policy changed.
8. Use only manual SQX file-dialog actions after approval; Codex must not copy files into SQX host folders.
9. Do not save into SQX `user/projects` until a separate post-import review gate permits it.
10. Do not run backtests, retests, optimizations, SQX tasks or `run_project`.
11. Capture only sanitized visual evidence: project name, layer labels, candidate id, visible safe status and no local paths/secrets.
12. Stop immediately if SQX shows unresolved resources, wrong base policy, missing Capa layer, save prompts that imply host mutation, or any import path ambiguity.

## Required Approval Phrase

The next phase must not start unless the operator sends this exact approval phrase:

`APRUEBO BS-AI8 IMPORT MANUAL CONTROLADA candidate=BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005 capa1=BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_Capa1.cfx capa2=BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_Capa2.cfx host=sqx144_full no_auto_import`

Even with that phrase, Codex should treat the next step as `BS-AI9 manual import execution after explicit operator approval`, not as permission to run SQX tasks or mutate databanks.

## Next Gate

Recommended next gate:

`BS-AI9 manual import execution after explicit operator approval`

BS-AI9 should be limited to one manually selected file-dialog import attempt, visual inspection and immediate stop before task execution or saving into host project stores.

## Boundaries

BS-AI8 did not:

- import any `.cfx` into SQX;
- copy artifacts into SQX folders;
- write SQX `data.db`;
- write SQX `user/projects`;
- mutate databanks;
- run SQX tasks;
- launch project execution, backtests, retests or optimizations;
- handle license/activation material;
- use Migration Tool;
- promote SQX144 144.2953;
- promote any BSAI candidate into the official manifest.
