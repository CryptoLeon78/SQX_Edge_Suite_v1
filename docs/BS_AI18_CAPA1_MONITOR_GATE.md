# BS-AI18 Capa1 Monitor Gate

Marker: `bs-ai18-capa1-monitor-gate-v1`

Current status: `monitoring_capa1_bsa16_no_capa2`

## Scope

BS-AI18 monitors the BS-AI16 Capa1 experiment after BS-AI17 imported and started it:

`BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001`

This phase is read-only. It observes SQX144 Full state and local sanitized counters without importing, starting, stopping, resolving resources or opening Capa2.

## Initial Readback

The first BS-AI18 status readback after BS-AI17 shows:

- SQX144 Full process still alive.
- Remote access reachable through `taskmanager/listProjects`.
- Target project visible.
- Capa1 reports 65 strategies.
- `tasks=14`.
- `databanks=15`.
- `hasUnresolvedResources=false`.
- Capa1 `project.cfx` hash remains the BS-AI17 hash.
- Local databank folders exist but no `.sqx` files are counted yet in the sanitized snapshot.

Current monitor decision: `continue_monitoring_capa1_active_no_capa2`.

## Monitor Evidence

First monitor run:

- Evidence: `bsai18_capa1_monitor_gate_monitor_20260607_220331.json`.
- Observation window: 75 seconds.
- Samples: 4.
- Capa1 strategies moved from the initial readback of 65 strategies to 75 strategies.
- Last monitored remote state: `tasks=14`, `databanks=15`, `strategies=75`, `hasUnresolvedResources=false`.
- Local databank `.sqx` counts remain `RETEST 0=0`, `retest 1=0`, `TICK=0`, `Forward=0`.
- Clean real TICK/Forward chain ready: `false`.
- Monitor warnings: `latest_log_stale_over_15m`, `tick_databank_empty_or_not_reached_yet`, `forward_databank_empty_or_not_reached_yet`.
- A separate read-only CPU sample showed SQX still actively working: main SQX process CPU delta was about 697 seconds over a 20 second wall-clock sample.
- Current decision remains `continue_monitoring_capa1_active_no_capa2`.

Repeat monitor 2026-06-10:

- Marker: `bs-ai18-repeat-monitor-20260610-v1`.
- Evidence: `bsai18_capa1_monitor_gate_monitor_20260610_192852.json`.
- Observation window: 60 seconds.
- Samples: 5.
- Remote endpoint remains only `taskmanager/listProjects`.
- Remote state: `remote_access_unavailable`.
- Local sanitized databanks show `Results=1321`, `RETEST 0=112`, `retest 1=14`, `TICK=0`, `Forward=0`.
- Capa1 `project.cfx` hash status remains `ok`.
- Latest SQX log is stale over 15 minutes and did not change during the monitor window.
- A separate read-only process check found no SQX/Java/StrategyQuant process; only MT5 was visible.
- Current decision is `monitor_blocked_review_required_no_capa2`.
- Clean real TICK/Forward chain ready: `false`.
- BS-AI19 is now allowed by the idle criterion as the next read-only review gate, but it was not executed in this monitor.

## Guardrails

- No Capa2.
- No Start.
- No Stop.
- No import.
- No `taskmanager/openProject`.
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

The only remote endpoint allowed by this gate is:

- `taskmanager/listProjects`

## Monitor Tool

`tools/sqx144_bsai18_capa1_monitor_gate.ps1` supports:

- `status`
- `monitor`
- `decision-template`

`monitor` writes ignored local evidence under the BS-AI monitor evidence root. Public payloads must not expose local paths, raw XML, raw logs, secrets or license material.

## Decision Policy

BS-AI18 may recommend continued monitoring when Capa1 is active or producing strategies. It may also recommend a later explicit stop/review gate if SQX becomes idle, the log is stale or the remote state becomes unavailable.

BS-AI18 cannot open Capa2. Capa2 remains blocked until there is a clean real TICK/Forward chain with enough evidence to review.

## RetDD Methodology Observation

`bs-ai18-retdd-tick-real-methodology-observation-v1` records a read-only academic/SQX review of `ReturnDDRatio` in TICK REAL.

The exact BS-AI16 artifact does not make RetDD completely final-only: it has an earlier soft main RetDD check at `ReturnDDRatio >= 1.2`, while TICK REAL preserves the hard final `ReturnDDRatio >= 4`. The methodology concern is therefore an asymmetric final quality gate, not a proven failure cause and not a reason to change the active run.

Decision for BS-AI18:

- Do not change the running project.
- Do not remove or relax `ReturnDDRatio >= 4`.
- Do not force pass.
- Do not start Capa2.
- If RetDD becomes the explicit post-run blocker, classify it as `retdd_asymmetric_final_gate_warning_no_capa2` and design a new preregistered experiment.

Expected next movement:

- Continue BS-AI18 monitoring while Capa1 is active.
- If the run becomes idle or stale, open a separate explicit stop/review gate.
- BS-AI19 is reserved for post-run read-only review when Capa1 has stopped or enough databank evidence exists.
