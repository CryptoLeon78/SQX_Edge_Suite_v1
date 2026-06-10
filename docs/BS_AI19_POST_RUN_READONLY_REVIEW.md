# BS-AI19 Post-Run Read-Only Review

Marker: `bs-ai19-post-run-readonly-review-v1`

Status: `post_run_readonly_review_completed_no_capa2`

## Scope

BS-AI19 reviews the completed/stale BS-AI16 Capa1 experiment after BS-AI18
allowed the idle criterion.

Target project:

`BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001`

This phase is read-only. It does not import, Start, Stop, resolve resources,
write `data.db`, write `user/projects`, mutate databanks or open Capa2.

## Evidence

Review evidence:

- `bsai19_post_run_readonly_review_review_20260610_194339.json`

The review consumed the latest BS-AI18 monitor reference:

- `bsai18_capa1_monitor_gate_monitor_20260610_192852.json`
- BS-AI18 decision: `monitor_blocked_review_required_no_capa2`
- BS-AI18 clean real TICK/Forward chain: `false`

Runtime readback:

- Remote state: `remote_access_unavailable`.
- Process check: no SQX/Java/StrategyQuant process visible.
- MT5 remains visible.

## Databank Review

Sanitized Capa1 counts:

- `Results=1321`
- `RETEST 0=112`
- `retest 1=14`
- `TICK=0`
- `Forward=0`

The 14 `retest 1` `.sqx` files were audited as ZIPs in read-only mode. Public
metric extraction is partial and sanitized:

- Survivor count: `14`.
- Observed pre-real-tick trades: min `265`, median `295`, max `360`.
- Observed `NetProfitIS`: min `3440.5601`, max `6314.8599`.
- All audited `retest 1` files are present in `RETEST 0` by filename.
- No audited file is present in `TICK`.
- Direct `ProfitFactor` is not embedded as a plain survivor metric in the
  audited `.sqx` files.
- After-real-tick metrics are not available because `TICK=0`.

## TICK REAL Rule Check

The BS-AI16 pre-registered trade rule is still visible in the project artifact:

`realTickTrades >= max(absoluteFloor, floor(priorValidationTrades * retentionRatio))`

SQX representation observed by BS-AI19:

- `NumberOfTrades >= 120`
- `RetestWithHigherPrecision` `NumberOfTrades >= 65%` of `main`
- `ProfitFactor >= 1.3`
- `WinningPct >= 50`
- `ReturnDDRatio >= 4`

This confirms BS-AI16 changed the trade-count tolerance as intended. It does not
create a pass state for this lot because TICK and Forward still have zero
survivors.

## Decision

Decision: `post_run_review_no_capa2_tick_forward_empty`

Methodology blockers:

- `tick_databank_empty_no_real_tick_survivors`
- `forward_databank_empty_no_forward_survivors`

Warnings:

- `retest1_survivors_exist_but_none_reached_tick_output`
- `latest_bsai18_monitor_also_reports_no_clean_tick_forward_chain`

Conclusion:

- The BS-AI16 lot is a failed candidate for Capa2.
- The 14 `retest 1` survivors are learning evidence only.
- No filter relaxation is allowed to rescue the current lot.
- No forced pass state is allowed.
- No Capa2 Start is allowed.

## Tooling

- Core: `backend/sqx-edge-tool/core/bsai19_post_run_readonly_review.py`
- Wrapper: `tools/sqx144_bsai19_post_run_readonly_review.ps1 status|review|decision-template`
- Tests: `backend/sqx-edge-tool/test_bsai19_post_run_readonly_review.py`
- Contract: `tests/js/contracts/bsai19_post_run_readonly_review_contracts.mjs`

`review` writes ignored local evidence under the BS-AI post-run review evidence
root. Public payloads must not expose local paths, raw XML, raw logs, secrets or
license material.

## Boundaries

BS-AI19 blocks:

- Capa2 Start.
- New Start or Stop.
- New import.
- `taskmanager/openProject`.
- `loadAsIs`.
- Resource resolution or Add missing symbols.
- Direct `data.db` patching.
- Direct script-side `user/projects` patching.
- Databank mutation or deletion.
- Migration Tool.
- BSAI promotion.
- Official v6/v7 overwrite.
- SQX144 144.2953 promotion.
- Profitability, pass-rate or risk-zero claims.

## Next Gate

Recommended next gate: `BS-AI20`.

BS-AI20 should choose between:

- Archive this branch as failed for Capa2.
- Design a new pre-registered Capa1 experiment.
- Open the dedicated asset/broker/instrument configuration review before
  another run.

No Capa2 can be opened from this lot.
