# J10 Temporal Health and EGT v2 Export Handoff

Date: 2026-05-09

Status: implemented as a redacted Champion vs Challenger export and Strategy Builder handoff extension.

## Scope

J10 carries the J9 evidence beyond the dashboard view:

- `buildReviewExport(model)` includes reduced `temporal_health` and `egt_v2` fields per candidate.
- Review `summary` includes `temporal_health_ok_count` and `egt_v2_ok_count`.
- `buildStrategyBuilderHandoff(reviewOrModel)` forwards the same reduced evidence to `recommended_candidate` and `candidates`.
- Strategy Builder packages preserve this evidence in `source_summary` and `asset_profile.cvc_evidence_summary`.
- `sampleCvcHandoff()` includes safe sample evidence for contracts and demos.

## Redacted Evidence Contract

Candidate `temporal_health` may include:

- `status`
- `pass_all`, `pass_peak`, `pass_drawdown`, `pass_recovery`
- `metric_used`, `metric_quality`
- `peak_block`, `block_count`
- `dd_at_close`, `recovery_index`
- warning codes only

Candidate `egt_v2` may include:

- `verdict`, `label`, `direction`
- `dominant_regime`
- rounded aggregate values such as `dominant_avg`, `worst_regime_avg` and `variance_across_regimes`
- `evaluated_regimes`, `failed_regimes`, `insufficient_regimes`
- `regime_block_counts`
- warning codes only

`evidence_review` is a decision hint only. It includes reduced booleans such as `formal_ok`, `oos_stable`, `temporal_health_ok`, `egt_v2_ok` and `operator_review_required`.

## Boundaries

- No raw CSV payloads.
- No `metrics_by_block` export.
- No historical price series export.
- No regime block payload export.
- No localStorage writes.
- No backend endpoint.
- No remote calls.
- No automatic StrategyQuant generation.
- No buyer, license or customer data.
- No automatic promotion decision.
- No `Top Picks` tab, Top Picks block, matrix tab, full matrix, heatmap tab or heatmap panel.

## Strategy Builder Behavior

Strategy Builder treats J10 evidence as context only:

- It can show and package the reduced evidence inside `source_summary`.
- It keeps `operator_review_required` true.
- It still requires manual operator review before an exportable package.
- It does not infer profitability, live readiness or buyer-facing performance claims.

## Verification

- JS Champion vs Challenger UI contracts assert reduced evidence in review export and handoff.
- JS Strategy Builder contracts assert evidence survives package construction without raw CSV or OOS block internals.
- Static dashboard tests assert the J10 documentation and runtime field names.
- E2E smoke continues to validate desktop/mobile CVC and Strategy Builder handoff flows.

## Next Phase

`SB17` can add a buyer-session evidence handoff index, or `J11` can make Strategy Builder's UI display the imported reduced evidence more explicitly.
