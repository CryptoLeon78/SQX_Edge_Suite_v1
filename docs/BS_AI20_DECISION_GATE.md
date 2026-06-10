# BS-AI20 Decision Gate

Marker: `bs-ai20-decision-gate-v1`

Status: `decision_archive_branch_open_asset_broker_instrument_review_no_capa2`

## Scope

BS-AI20 decides the next governed movement after BS-AI19 closed the post-run
read-only review.

Target project:

`BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001`

This phase is a methodology decision only. It does not Start, Stop, import,
move host projects, resolve resources, write `data.db`, write `user/projects`,
mutate databanks, open Capa2 or use Migration Tool.

## Evidence

Decision evidence:

- `bsai20_decision_gate_decide_20260610_201532.json`

The decision consumed the latest BS-AI19 review:

- `bsai19_post_run_readonly_review_review_20260610_194339.json`
- BS-AI19 decision: `post_run_review_no_capa2_tick_forward_empty`
- BS-AI19 clean real TICK/Forward chain: `false`

Sanitized input counts:

- `Results=1321`
- `RETEST 0=112`
- `retest 1=14`
- `TICK=0`
- `Forward=0`

## Decision

Decision:

`archive_branch_and_open_asset_broker_instrument_review_no_capa2`

Selected next gate:

`BS-AI21 asset/broker/instrument configuration review`

Operational meaning:

- Archive the current branch as a failed Capa2 candidate in methodology/docs
  only.
- The archive is `methodology_archive_only_no_host_project_move`.
- The 14 `retest 1` survivors remain learning evidence only.
- A new preregistered Capa1 experiment is deferred until BS-AI21 is complete
  or explicitly waived in a later operator-approved methodology gate.
- No Capa2, No Start, No import, No forced pass and no host project move are
  allowed by BS-AI20.

## Why

The current branch has no clean real TICK/Forward survivor chain. Using the 14
`retest 1` survivors as Capa2 seed would reinterpret post-run evidence after
the failure point.

The next risk to reduce is configuration uncertainty around the traded resource.
BS-AI16 already recorded a spread/cross-broker warning, and later MT5 metadata
observations showed that spread and point value can drift enough to deserve a
dedicated review before another run.

BS-AI20 therefore chooses the asset/broker/instrument review ahead of a new
Capa1 design.

## BS-AI21 Scope

BS-AI21 should audit, read-only unless a later gate approves otherwise:

- `AUDCAD_darwinex` and `AUDCAD_dukascopy`.
- Spread and default spread policy.
- Point value, tick size, tick step, order-size fields, commission and swap.
- Broker/source/data IDs and history coverage.
- Embedded project resources versus the current `sqx144_full` catalog.
- Timing of MT5 metadata observations versus BS-AI16 prepare/import/start.

## Methodology Notes

BS-AI20 keeps two anti-overfit rules:

- Do not use post-run evidence to relax filters or rescue the failed branch.
- Any next thresholds or hypotheses must be preregistered before the next run.

The academic rationale is the same one already used in the project governance:
backtest selection over many candidates can overfit, and holdout evidence should
not be recycled into the same decision chain.

## Tooling

- Core: `backend/sqx-edge-tool/core/bsai20_decision_gate.py`
- Wrapper: `tools/sqx144_bsai20_decision_gate.ps1 status|decide|decision-template`
- Tests: `backend/sqx-edge-tool/test_bsai20_decision_gate.py`
- Contract: `tests/js/contracts/bsai20_decision_gate_contracts.mjs`

`decide` writes ignored local evidence under the BS-AI decision-gate evidence
root. Public payloads must not expose local paths, raw XML, raw logs, secrets or
license material.

## Boundaries

BS-AI20 blocks:

- Capa2 Start.
- New Start or Stop.
- New import.
- Host project move/archive mutation.
- `taskmanager/openProject`.
- `loadAsIs`.
- Resource resolution or Add missing symbols.
- Direct `data.db` patching.
- Direct script-side `user/projects` patching.
- Databank mutation or deletion.
- Migration Tool.
- Filter relaxation for the current lot.
- Forced pass states.
- BSAI promotion.
- Official v6/v7 overwrite.
- SQX144 144.2953 promotion.
- Profitability, pass-rate or risk-zero claims.

## Next Gate

Recommended next gate: `BS-AI21 asset/broker/instrument configuration review`.

No new Capa1 run should be designed from this branch until BS-AI21 is complete
or explicitly waived in a later operator-approved methodology gate.
