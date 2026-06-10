# BS-AI17 Controlled Import Start Gate

Marker: `bs-ai17-controlled-capa1-import-start-gate-v1`

Current gate status: `controlled_capa1_import_start_requested_no_capa2`

## Scope

BS-AI17 is the first controlled SQX144 Full import/start gate for the BS-AI16 experiment artifact:

`BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001`

The artifact comes from BS-AI16 and keeps the pre-registered TICK REAL rule:

`realTickTrades >= max(absoluteFloor, floor(priorValidationTrades * retentionRatio))`

Configured point:

- `retentionRatio=0.65`
- `absoluteFloor=120`
- SQX representation: `NumberOfTrades >= 120` plus `RetestWithHigherPrecision` `NumberOfTrades >= 65%` of `main`

## Operator Approval

The operator explicitly approved BS-AI17 controlled import/start and accepted the `cross-broker spread warning` for `this trial only`.

This does not close the methodology concern. A `future asset/broker/instrument review` remains required because the operator normally aligns Dukascopy instrument settings to Darwinex for spread, point value, tick size and tick step. The observed cross-broker difference is accepted only as a warning for this one run.

## Allowed Actions

`tools/sqx144_bsai17_controlled_import_start_gate.ps1` supports:

- `status`
- `preflight`
- `launch`
- `import-capa1`
- `start-capa1`

The controlled import path uses SQX local remote access:

- Import endpoint: `taskmanager/openProject`
- Import resource policy: `loadAsIs=false`
- Start endpoint: `project/start`

`launch` may open SQX144 Full visibly and wait for local remote access. It does not import, start, resolve resources or mutate projects by itself.

## Guardrails

- No Capa2.
- No `loadAsIs=true`.
- No Add missing symbols.
- No resource-resolution bypass.
- No direct `data.db` patch.
- No direct script-side `user/projects` patch.
- No direct databank mutation.
- No Migration Tool.
- No official BlockSettings v6/v7 overwrite.
- No BSAI promotion into the official manifest.
- No SQX144 144.2953 promotion.

SQX itself may write natural host state when the approved import/start endpoints are called:

- `taskmanager/openProject` may write the imported target project through SQX.
- `project/start` may write logs, task state and target databanks for the started Capa1 project.

Those host-owned effects are limited to this approved Capa1 experiment.

## Evidence Policy

Evidence is written only under ignored local evidence roots and public payloads must not expose:

- local paths;
- raw XML;
- raw logs;
- secrets;
- license material.

Expected evidence names use:

- `bsai17_controlled_import_start_gate_preflight_*.json`
- `bsai17_controlled_import_start_gate_import-capa1_*.json`
- `bsai17_controlled_import_start_gate_start-capa1_*.json`

## Executed Result

Execution date: 2026-06-07

Observed status: `controlled_capa1_import_start_requested_no_capa2`

Runtime evidence:

- Launch: SQX144 Full was opened and local remote access became reachable.
- Preflight evidence: `bsai17_controlled_import_start_gate_preflight_20260607_204351.json`.
- Import evidence: `bsai17_controlled_import_start_gate_import-capa1_20260607_204409.json`.
- Start evidence: `bsai17_controlled_import_start_gate_start-capa1_20260607_204623.json`.

Import result:

- `taskmanager/openProject` accepted `BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001`.
- `loadAsIs=false`.
- `hasResourcesXML=false`.
- Project visible after import: `tasks=14`, `databanks=15`, `strategies=0`, `hasUnresolvedResources=false`.

Start result:

- `project/start` returned `Project execution started.`
- Capa1 remained visible after Start with `tasks=14`, `databanks=15`, `hasUnresolvedResources=false`.
- Capa1 `project.cfx` hash remained `762197F6A9E764F807C05728F1FC7383DE0C1CEC651A6DC4D26E11B5AEC02642`.
- Latest SQX log changed during observation.
- Capa2 Start requested: `false`.

Post-Start readback:

- A later `status` readback returned `remote_access_unavailable` / `TimeoutError`, consistent with SQX being busy after Start.
- Local sanitized snapshot still showed the target project present, the `project.cfx` hash unchanged and the latest SQX log larger.
- This readback does not open Capa2 or reinterpret Capa1 results.

## Execution Plan

Completed sequence:

1. `launch` SQX144 Full and waited for local remote access.
2. Ran `preflight` with `--accept-cross-broker-spread-warning`.
3. Imported Capa1 with `import-capa1`.
4. Started Capa1 with `start-capa1`.
5. Observed briefly and stopped the gate. Monitoring is deferred to BS-AI18.

## Next Gate

BS-AI18: monitor BSAI16 Capa1 run and decide without opening Capa2 until Capa1 has clean real TICK/Forward survivors.
