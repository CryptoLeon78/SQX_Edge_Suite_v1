# J8 Temporal Health and EGT v2 Helpers

Date: 2026-05-09

Status: implemented as pure browser-local helpers with JS contracts. No dashboard rendering, backend endpoint, persistence or buyer-facing claim is added in J8.

## Scope

J8 implements the J7 contract as native SQX Edge helpers:

- `SQX.championChallengerCore.computeTemporalHealth(oosRecord, options)`
- `SQX.championChallengerRegime.assessEgtV2(oosRecord, regimeBlocks, options)`

The helpers are intentionally not wired into the dashboard table yet. J9 owns compact UI chips and filters. J10 owns export and Strategy Builder handoff fields.

## Temporal Health Helper

`computeTemporalHealth` consumes a J3 OOS record and returns:

- `status`: `fresh`, `recovered`, `old_peak`, `declining` or `unknown`
- `peak_block`
- `block_count`
- `dd_at_close`
- `recovery_index`
- `pass_peak`
- `pass_drawdown`
- `pass_recovery`
- `pass_all`
- `source_metric`
- `quality`
- `warnings`

It prefers `Net Profit`, `Net profit` or `NetProfit`. If those are unavailable it falls back to the primary OOS metric and emits `temporal_health_metric_fallback`.

Guardrails:

- too few blocks return `unknown`
- non-positive cumulative peak returns guarded evidence
- unavailable recovery emits `temporal_health_recovery_unavailable`
- no hard `Stagnation < X days` promotion filter is introduced

## EGT v2 Helper

`assessEgtV2` consumes a J3 OOS record plus externally supplied regime blocks and returns:

- `verdict`: `STRONG`, `COMPLIANT`, `DEFENSIVE`, `INSUFFICIENT`, `RISK` or `UNKNOWN`
- `label`: legacy-compatible `COMPLIANT`, `FLAT`, `RISK` or `UNKNOWN`
- `direction`
- `dominant_regime`
- `dominant_avg`
- `stats_by_regime`
- `pass_by_regime`
- `strong_by_regime`
- `sufficient_by_regime`
- `failed_regimes`
- `insufficient_regimes`
- `evaluated_regimes`
- `worst_regime_avg`
- `variance_across_regimes`
- `thresholds`
- `warnings`

It supports:

- `long_only` thresholds
- `long_short` thresholds
- `minBlocksPerRegime`
- optional `minTradesPerBlock`
- dominant regime by most evaluated blocks, with average as tiebreaker

## Explicit Non-Scope

- No UI chips or filters.
- No export payload changes.
- No Strategy Builder handoff changes.
- No backend endpoint.
- No remote calls.
- No raw CSV persistence.
- No copied Jose runtime code.
- No automatic promotion decision.
- No `Top Picks` tab, Top Picks block, matrix tab, full matrix, heatmap tab or heatmap panel.

## Verification

- `tests/js/contracts/champion_challenger_core_contracts.mjs` covers Temporal Health.
- `tests/js/contracts/champion_challenger_regime_contracts.mjs` covers EGT v2.
- Static dashboard tests assert helper exports and J8 documentation.
- Full JS module contracts and Python tests remain required before commit.

## Next Phases

1. `J9` - add compact dashboard chips and optional filters using these helpers.
2. `J10` - add reduced Temporal Health and EGT v2 fields to export and Strategy Builder handoff payloads.
