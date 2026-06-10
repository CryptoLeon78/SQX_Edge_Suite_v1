# BS-AI15 Tick Real Diagnostic

Marker: `bs-ai15-tick-real-diagnostic-v1`

Status: `diagnostic_plan_ready_no_capa2_no_filter_relaxation`

## Scope

BS-AI15 freezes the BS-AI14 lot
`tick_real_pf_failed_trade_threshold_warning_no_capa2` and audits the 5
`retest 1` survivors in read-only mode.

No Capa2. No filter relaxation. No rescue of the current candidate by changing
pass states after the fact.

## Frozen Lot

- Candidate: `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005`.
- Host profile: `sqx144_full`.
- Capa1 remains the only executed branch.
- Capa2 remains unstarted and empty.
- Final databank counts remain `RETEST 0=37`, `retest 1=5`, `TICK=0`.
- First logged TICK REAL blocker remains
  `Profit factor[Main data] >= 1.30`, Count 5 / 100%.
- SQX does not prove later active filters would have passed once the first
  blocker was logged.

Conclusion: the lot is a failed candidate for Capa2. It is not rescued by
relaxing filters.

## Survivor Audit

BS-AI15 reads the 5 `retest 1` `.sqx` ZIP files and extracts only sanitized
public metrics from `SQStats`. It does not expose local paths, raw XML, raw logs
or secrets.

Evidence ref: `bsai15_tick_real_diagnostic_audit_20260607_191116.json`.

| Ref | Strategy | Trades before real tick | Net profit IS | DD proxy IS | Return/Open DD | Recovery | Stagnation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `retest1_001` | `Strategy 4.14.21` | 302 | 5398.93 | 5722.93 | 0.90 | 1.01 | 218 |
| `retest1_002` | `Strategy 4.16.24` | 302 | 5066.35 | 6063.01 | 0.82 | 0.90 | 239 |
| `retest1_003` | `Strategy 5.10.29` | 308 | 5191.89 | 6258.20 | 0.81 | 0.90 | 229 |
| `retest1_004` | `Strategy 5.15.27` | 300 | 5431.03 | 6379.38 | 0.83 | 0.91 | 235 |
| `retest1_005` | `Strategy 5.5.24` | 311 | 3643.10 | 7578.54 | 0.47 | 0.52 | 240 |

Metric caveat:

- Direct pre-TICK `ProfitFactor` was not embedded as a plain metric in these
  `retest 1` `.sqx` files.
- Canonical `DrawdownPct` was not embedded as a plain metric either; BS-AI15
  records drawdown/stability proxies only.
- There is no after-real-tick metric row because `TICK=0`.

Therefore BS-AI15 can say the 5 survivors had enough observed pre-real-tick
trade count, but it cannot claim their TICK REAL trade count after real-tick
execution because no `TICK` survivor file exists.

## TICK REAL Rule Finding

The TICK REAL task contains the expected absolute main filters:

- `# of trades >= 200` (`NumberOfTrades >= 200`).
- `ProfitFactor >= 1.3`.
- `WinningPct >= 50`.
- `ReturnDDRatio >= 4`.

The task also contains `RetestWithHigherPrecision` retention comparisons
against `main`, including `NumberOfTrades` at `80%`, `NetProfit` at `80%` and
`DrawdownPct` at `130%`.

This matters: the next experiment must explicitly choose the trade-count rule
instead of inheriting an accidental combination of absolute floor plus ratio.
The current log only proves the first observed blocker was Profit Factor, so
the trade rule remains a methodology warning, not a proven failed filter.

## Proposed Trade Rule

For the next experiment, pre-register a tolerant rule before running:

`realTickTrades >= max(absoluteFloor, floor(priorValidationTrades * retentionRatio))`

Initial diagnostic grid to choose from before the run:

- `retentionRatio=0.60`, `absoluteFloor=120`.
- `retentionRatio=0.65`, `absoluteFloor=120`.
- `retentionRatio=0.70`, `absoluteFloor=150`.

The operator must choose one grid point before seeing the next TICK results.
The current lot must not be reinterpreted with the chosen rule.

## Next Experiment

Recommended next gate: `BS-AI16`.

Recommended experiment:
`new_capa1_experiment_with_pre_registered_tick_real_trade_rule_no_capa2`.

Reason: the blocker is Capa1 TICK REAL Profit Factor before any Capa2 evidence
exists. A Capa2 v6 default vs v7 explicit comparison is premature until Capa1
has natural `TICK` and preferably Forward survivors.

Preferred options:

- Change Capa1 hypothesis, direction, timeframe or family and run it as a new
  branch.
- Repeat Capa1 only if the TICK REAL trade rule is pre-registered as a new
  experiment.
- Defer v6 default vs v7 explicit Capa2 comparison until a clean Capa1
  `TICK`/Forward chain exists.

Blocked options:

- Start Capa2 from this lot.
- Relax filters to reinterpret this lot as passed.
- Claim trade-count failure from the log when Profit Factor was the first
  logged blocker.

## Tooling

- Core: `backend/sqx-edge-tool/core/bsai15_tick_real_diagnostic.py`
- Wrapper: `tools/sqx144_bsai15_tick_real_diagnostic.ps1 status|audit|plan`
- Tests: `backend/sqx-edge-tool/test_bsai15_tick_real_diagnostic.py`
- Contract: `tests/js/contracts/bsai15_tick_real_diagnostic_contracts.mjs`

`status` and `plan` print public-safe JSON.

`audit` writes sanitized evidence under ignored local evidence and still does
not mutate SQX host projects, `data.db`, `user/projects` or databanks.

## Boundaries

BS-AI15 blocks:

- Capa2 Start.
- New import.
- `taskmanager/openProject`.
- `loadAsIs`.
- Resource resolution or `Add missing symbols`.
- Direct `data.db` patching.
- Direct script-side `user/projects` patching.
- Databank deletion.
- Migration Tool.
- BSAI promotion.
- Official v6/v7 overwrite.
- 144.2953 promotion.
- Profitability, pass-rate or risk-zero claims.

## Methodology Note

This phase follows the same anti-overfit discipline used elsewhere in SQX Edge:
failed validation results stay failed, and new thresholds must be pre-registered
as a new experiment. Bailey, Borwein, Lopez de Prado and Zhu discuss backtest
overfitting and selection pressure in simulated strategy search; Bailey and
Lopez de Prado's Deflated Sharpe Ratio work also emphasizes multiple-testing
and selection-bias controls. BS-AI15 applies that principle narrowly: do not use
post-hoc filter changes to turn this lot into a pass.

References:

- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659
- https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf
