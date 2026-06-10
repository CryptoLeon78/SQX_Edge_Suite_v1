# BS-AI16 Capa1 Experiment Pre-Registration Gate

Marker: `bs-ai16-capa1-experiment-prereg-gate-v1`

Status: `preregistered_capa1_tick_rule_ready_no_import_no_start`

## Scope

BS-AI16 prepares a new Capa1 experiment contract after BS-AI15. It does not
reinterpret or rescue the frozen lot
`tick_real_pf_failed_trade_threshold_warning_no_capa2`.

No import. No Start. No Capa2.

The gate can prepare a local `.cfx` artifact under ignored local evidence, but
that artifact still requires a later explicit import/start gate.

## Frozen Lot Boundary

- Frozen decision remains `tick_real_pf_failed_trade_threshold_warning_no_capa2`.
- Previous evidence remains `RETEST 0=37`, `retest 1=5`, `TICK=0`.
- First logged TICK REAL blocker remains `Profit factor[Main data] >= 1.30`.
- The current candidate is failed for Capa2.
- BS-AI16 does not relax filters to change pass states.

## Pre-Registered TICK REAL Trade Rule

BS-AI16 fixes the next experiment rule before seeing new TICK output:

`realTickTrades >= max(absoluteFloor, floor(priorValidationTrades * retentionRatio))`

Default grid point selected for this gate:

- `retentionRatio=0.65`
- `absoluteFloor=120`

SQX representation:

- `NumberOfTrades >= 120`
- `RetestWithHigherPrecision` `NumberOfTrades >= 65%` of `main`

Examples:

| Prior validation trades | Required real-tick trades |
| ---: | ---: |
| 300 | 195 |
| 302 | 196 |
| 308 | 200 |
| 311 | 202 |

This is a new Capa1 experiment rule, not a retrospective scoring rule for the
old lot.

## Spread / Cost Sanity

The operator raised a valid hypothesis: a too-low configured spread can inflate
simulated PF and then collapse at TICK REAL. BS-AI16 therefore adds
`spreadCostSanity` before preparing the next experiment.

Policy:

- If primary Darwinex chart spread in the source `.cfx` is below the host
  catalog spread, preparation is blocked.
- Cross-broker spread divergence is recorded as a methodology warning, not a
  proof of failure.
- Spread/cost diagnostics do not rescue the frozen lot.

Current read-only observation for the imported Capa1:

- Primary `AUDCAD_darwinex` chart spread is `1`.
- Host catalog `AUDCAD_darwinex` default spread is `1.0`.
- Therefore primary spread is not below the `sqx144_full` host catalog.
- Cross-broker `AUDCAD_dukascopy` appears with chart spread `1`, while the
  alternate Dukascopy instrument default spread is `1.9`; this remains a
  `spreadCostSanity` warning to keep visible before the next run.

## Tooling

- Core: `backend/sqx-edge-tool/core/bsai16_capa1_experiment_gate.py`
- Wrapper: `tools/sqx144_bsai16_capa1_experiment_gate.ps1 status|plan|prepare`
- Tests: `backend/sqx-edge-tool/test_bsai16_capa1_experiment_gate.py`
- Contract: `tests/js/contracts/bsai16_capa1_experiment_prereg_contracts.mjs`

`status` and `plan` are read-only.

`prepare` writes only ignored local evidence and a local Capa1 `.cfx` artifact.
It does not import into SQX and does not press Start.

Prepared local artifact:

- Experiment id: `BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001`
- Artifact ref: `BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001.cfx`
- Evidence ref: `bsai16_capa1_experiment_gate_prepare_20260607_195815.json`
- ZIP check: valid `.cfx` with `config.xml` and `AutomaticRetest-Task2.xml`.
- TICK REAL check: `NumberOfTrades >= 120`, `RetestWithHigherPrecision` `NumberOfTrades >= 65%`, `ProfitFactor >= 1.3`, `WinningPct >= 50`, `ReturnDDRatio >= 4`.

## Guards

BS-AI16 blocks:

- SQX import.
- `taskmanager/openProject`.
- `loadAsIs`.
- `project/start`.
- `project/stop`.
- Capa2 Start.
- Direct `data.db` patching.
- Direct script-side `user/projects` patching.
- Databank mutation or deletion.
- Migration Tool.
- BSAI promotion.
- Official v6/v7 overwrite.
- 144.2953 promotion.
- Profitability, pass-rate or risk-zero claims.

## Next Gate

Next recommended gate: `BS-AI17 controlled Capa1 import/start gate after
operator approval`.

BS-AI17 should import/start only if the operator explicitly approves the local
BS-AI16 artifact and accepts the recorded `spreadCostSanity` warning.

## Methodology Note

The academic discipline remains unchanged: failed validation results stay
failed, and new thresholds/cost assumptions are pre-registered as a new
experiment. BS-AI16 follows the same anti-overfit principle recorded in
BS-AI15.

References:

- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659
- https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf
