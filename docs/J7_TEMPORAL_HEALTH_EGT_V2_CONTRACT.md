# J7 Temporal Health and EGT v2 Contract

Date: 2026-05-09

Status: contract accepted for future implementation. No runtime, UI, backend endpoint or buyer-facing claim is added in J7.

Source reviewed: `https://github.com/jlivanmaseda-maker/sqx-edge-pipeline.git`, commit `06767d8eef597987530f152d54860ab96e590ffa`.

## Objective

J7 converts the latest Jose-derived idea into a native SQX Edge contract before implementation:

- Temporal Health: decide whether OOS stagnation is recent deterioration, an old peak, or a recovered/fresh candidate.
- EGT v2: replace the coarse Regime/EGT label with a richer five-verdict evidence model.

This is a Pro workflow improvement for Champion vs Challenger and future Strategy Builder handoffs. It remains operator evidence, not an automatic trading recommendation.

## Ownership and Risk

- Primary ownership: Architecture/Docs.
- Secondary ownership: Frontend/UI, QA/Release.
- Future implementation ownership: Frontend/UI for rendering, Architecture/Docs for contracts, QA for JS contracts.
- G3 automation risk: level 0 in J7, documentation only.
- Future J8/J9 runtime phases must remain browser-local unless explicitly scoped otherwise.

## Temporal Health Contract

Temporal Health reads the OOS block record already produced by J3. It must not depend on Jose element IDs, inline HTML or global script state.

Preferred source metric order:

1. `Net Profit`
2. `Net profit`
3. `NetProfit`
4. configured primary OOS metric as degraded fallback

Minimum input:

- strategy name
- OOS block count
- ordered numeric block values
- primary metric name
- optional warnings from OOS parsing

Output object:

- `status`: one of `fresh`, `recovered`, `old_peak`, `declining`, `unknown`
- `peak_block`: 1-based OOS block where cumulative equity reaches its max
- `block_count`: number of valid OOS blocks
- `dd_at_close`: drawdown from cumulative peak to final cumulative value, decimal ratio
- `recovery_index`: average of last configured blocks divided by historical block average
- `pass_peak`: boolean
- `pass_drawdown`: boolean
- `pass_recovery`: boolean
- `pass_all`: boolean
- `source_metric`: metric used for the calculation
- `quality`: `full`, `fallback` or `insufficient`
- `warnings`: deterministic warning codes

Default thresholds:

- `min_blocks`: 4
- `recent_peak_window`: 3
- `max_dd_at_close`: 0.15
- `min_recovery_index`: 0.70

Classification policy:

- `fresh`: peak is inside the recent peak window and drawdown is below threshold.
- `recovered`: peak is in the second half, not recent, and drawdown/recovery pass.
- `old_peak`: peak is in the first half while drawdown is not yet severe.
- `declining`: drawdown from peak to close is at or above threshold, or recovery fails.
- `unknown`: evidence is missing, too short or numerically unsafe.

Numerical guardrails:

- If cumulative peak is less than or equal to zero, `dd_at_close` must be `null` and quality must not be `full`.
- If historical average is zero or not finite, `recovery_index` must be `null` and `pass_recovery` must not silently pass unless policy says recovery is optional.
- Fallback to non-profit metrics must emit a warning such as `temporal_health_metric_fallback`.
- Missing or non-numeric blocks must emit warnings and exclude invalid values from calculation.

Stagnation rule:

- Do not use a hard `Stagnation < X days` promotion filter.
- Keep raw stagnation only as secondary context.
- Temporal Health can explain why a strategy with old stagnation may still be recovered, but it cannot promote a candidate by itself.

## EGT v2 Contract

EGT v2 extends the J5 first-party Regime/EGT adapter. It must consume first-party historical data and OOS block evidence through our existing modules.

Inputs:

- candidate OOS record from J3
- regime blocks from `SQX.championChallengerRegime` or a future pure helper
- direction policy: `long_only` or `long_short`
- per-regime thresholds for `BULL`, `BEAR` and `RANGE`
- minimum evaluable blocks per regime
- optional minimum trades per block

Default thresholds:

- `min_blocks_per_regime`: 2

```json
{
  "direction": "long_only",
  "min_blocks_per_regime": 2,
  "long_only": {
    "BULL": { "pass": 1.5, "strong": 2.5 },
    "BEAR": { "pass": 0.0, "strong": 1.0 },
    "RANGE": { "pass": 0.0, "strong": 1.0 }
  },
  "long_short": {
    "BULL": { "pass": 1.0, "strong": 2.0 },
    "BEAR": { "pass": 1.0, "strong": 2.0 },
    "RANGE": { "pass": 0.5, "strong": 1.5 }
  }
}
```

Output object:

- `verdict`: one of `STRONG`, `COMPLIANT`, `DEFENSIVE`, `INSUFFICIENT`, `RISK`, `UNKNOWN`
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

Verdict policy:

- `UNKNOWN`: missing regime blocks, missing OOS blocks or incompatible block counts.
- `INSUFFICIENT`: at least one regime has data but no regime reaches the minimum evaluable block count.
- `RISK`: any evaluated regime fails its `pass` threshold.
- `STRONG`: every evaluated regime passes and the dominant regime reaches `strong`.
- `COMPLIANT`: every evaluated regime passes and at least one non-dominant regime reaches `strong`.
- `DEFENSIVE`: every evaluated regime passes, but no evaluated regime reaches `strong`.

Dominant regime policy:

- Pick the regime with the most evaluated blocks.
- Break ties by higher average.
- Do not use "best average only" as the dominant regime because it overweights one-block outliers.

Backward compatibility:

- Future implementation may expose a legacy label for existing counters:
  - `STRONG` and `COMPLIANT` may count as compliant.
  - `DEFENSIVE`, `INSUFFICIENT` and `UNKNOWN` must not be silently promoted.
  - `RISK` must remain blocking evidence.
- Existing `COMPLIANT`, `RISK`, `FLAT`, `UNKNOWN` J5 labels stay valid until J8/J9 replaces the UI contract.

## UI Contract for Future J9

The future dashboard integration should be compact and native:

- Add Temporal Health as a small evidence chip group inside the current Champion vs Challenger table.
- Add EGT v2 verdict chips inside the existing EGT area.
- Add filters only after the pure core has tests.
- Avoid large explanatory text in the app.
- Use existing dark SaaS visual tokens.
- Do not restore a `Top Picks` tab, Top Picks block, matrix tab, full matrix, heatmap tab or heatmap panel.
- No `Top Picks` tab, Top Picks block, matrix tab, full matrix, heatmap tab or heatmap panel.

## Export and Strategy Builder Handoff

Future J10 should extend the J6 export and handoff contracts with reduced, redacted fields only:

- `temporal_health.status`
- `temporal_health.pass_all`
- `temporal_health.dd_at_close`
- `temporal_health.recovery_index`
- `egt_v2.verdict`
- `egt_v2.dominant_regime`
- `egt_v2.failed_regimes`
- `egt_v2.insufficient_regimes`

Raw CSV rows, raw imported files and localStorage payloads remain excluded.

## Security Boundaries

- No copied Jose runtime code.
- No direct dependency on Jose file structure.
- No remote calls.
- No backend persistence.
- No raw CSV persistence.
- No buyer, checkout, license or customer data.
- No automatic promotion decision.
- No public commercial claim that the app selects profitable strategies automatically.

## Planned Phases

1. `J8` - implement pure Temporal Health and EGT v2 helpers with JS contracts.
2. `J9` - add compact native dashboard rendering and filters, with E2E screenshots.
3. `J10` - extend export and Strategy Builder handoff payloads with reduced evidence.

## Verification Expectations

J7 verification:

- Static docs test asserts the contract, roadmap and governance links.
- `git diff --check`.

Future J8/J9 verification:

- `tests/js/contracts/champion_challenger_core_contracts.mjs`.
- `tests/js/contracts/champion_challenger_regime_contracts.mjs`.
- `tests/js/contracts/champion_challenger_ui_contracts.mjs`.
- `node .\tests\js\module_contracts.mjs`.
- Static dashboard tests.
- E2E screenshots only when UI behavior changes.
