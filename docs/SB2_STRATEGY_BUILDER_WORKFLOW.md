# SB2 Strategy Builder Controlled Workflow Design

Phase SB2 designs the controlled Strategy Builder flow that can later become a read-only prototype.

This phase is workflow and contract design only. It does not add dashboard UI, backend endpoints, generation code, trading logic, optimizer logic, remote AI calls or buyer-facing performance claims.

## Goal

Turn the SB1 scope into an operator-safe workflow that creates a reviewable strategy idea package from existing SQX Edge evidence.

The intended buyer value is a guided path from evidence to StrategyQuant preparation:

1. choose a safe source;
2. normalize context;
3. select an idea archetype;
4. attach validation requirements;
5. prepare Project Generator and SQX Views handoffs;
6. export a local package only after explicit review.

## Controlled State Machine

The future Builder must move through these states in order:

1. `source_selected`
2. `context_resolved`
3. `idea_framed`
4. `validation_planned`
5. `handoff_prepared`
6. `operator_reviewed`
7. `package_exportable`

Blocking states:

- `blocked_missing_source`
- `blocked_unsupported_asset`
- `blocked_missing_timeframe`
- `blocked_claims_boundary`
- `blocked_validation_pack_missing`
- `blocked_operator_review`

No package should be exportable unless the state is `package_exportable`.

## Source Modes

| Mode | Input | Required checks |
| --- | --- | --- |
| `blank` | Operator starts from asset/timeframe/profile. | Asset supported, timeframe present, idea archetype selected. |
| `cvc_handoff` | J6 `sqx-edge.strategy-builder-handoff`. | Type/version valid, candidate present, raw CSV absent, symbol supported. |
| `project_generator_profile` | Existing custom starter or buyer profile family. | Profile id present, asset/timeframe resolved, project name safe. |
| `views_workflow` | SQX Views validation workflow pack. | Validation pack id present, minimum validation columns known. |

Every mode must resolve to the same internal context shape.

## Internal Context Shape

The Builder context should contain:

- `asset`
- `timeframe`
- `market_family`
- `direction_bias`
- `source_mode`
- `source_summary`
- `regime_label`
- `oos_summary`
- `mtf_summary`
- `project_profile_id`
- `validation_pack_id`
- `risk_profile`
- `traceability`

Unknown evidence is allowed only when it is explicitly labeled as `unknown` and does not create stronger claims.

## Idea Archetypes

Initial archetypes should stay broad and inspectable:

- `trend_following`
- `mean_reversion`
- `breakout`
- `pullback`
- `volatility_filter`
- `regime_filter`

Each archetype must map to indicator families, not fixed magic settings.

Example mapping:

| Archetype | Indicator family candidates | Validation emphasis |
| --- | --- | --- |
| `trend_following` | EMA, MACD, SuperTrend, SMA persistence | Trend persistence, drawdown, walk-forward. |
| `mean_reversion` | RSI, Stochastic, Bollinger, PercentRank | Recovery profile, adverse excursion, OOS decay. |
| `breakout` | Donchian, Keltner, ATR, volume filters | False breakout rate, volatility expansion, trade count. |
| `pullback` | EMA, RSI, CCI, support/resistance | Entry timing, retracement depth, regime fit. |
| `volatility_filter` | ATR, StdDev, Keltner, Bollinger width | Volatility clustering, risk envelope, stop behavior. |
| `regime_filter` | CSSA/Regime, SMA200 persistence, EGT score | Regime compatibility and blocked market states. |

## Package Contract

Future SB3 packages should use `sqx-edge.strategy-builder-package`.

Required fields:

- `type`
- `version`
- `created_at`
- `workflow_state`
- `source_mode`
- `source_summary`
- `asset_profile`
- `idea_archetype`
- `indicator_family_candidates`
- `risk_envelope`
- `validation_requirements`
- `project_generator_handoff`
- `views_handoff`
- `operator_checklist`
- `traceability`
- `blocked_claims`

The package must not include raw CSV imports, private customer data, checkout data, license payloads, local filesystem secrets or StrategyQuant proprietary result files unless the operator explicitly attaches them in a future local-only tool.

## Handoff Rules

Project Generator handoff:

- Suggest one profile id.
- Suggest project naming only after sanitization.
- Preserve custom project freedom outside plan mining.
- Do not auto-run bulk generation.

SQX Views handoff:

- Suggest one validation workflow pack.
- Include required columns and purpose.
- Keep validation as a review gate, not a marketing proof.

Champion vs Challenger handoff:

- Accept J6 reduced summary only.
- Use the top candidate as a starting point, not a final winner.
- Preserve OOS and Regime/EGT caveats.

## Operator Checklist

The future UI should require the operator to confirm:

- asset and timeframe are correct;
- source evidence has been reviewed;
- idea archetype is appropriate for the asset/regime;
- validation pack is selected;
- StrategyQuant settings will be reviewed manually;
- no profitability claim is inferred from the package;
- export is local and reviewable.

## SB3 Prototype Recommendation

SB3 should add a read-only module and small UI surface:

- `app/js/modules/strategy-builder-core.js` for pure package building.
- `app/js/modules/strategy-builder.js` for the future dashboard facade.
- A compact tab or panel only after contracts pass.
- JS contracts before E2E.
- No backend endpoint unless a later phase needs local file generation.

The first prototype should build and preview a package. It should not generate executable trading logic.

## Acceptance Criteria

- SB2 is documented before runtime changes.
- Governance and roadmap point to SB3 as the next Strategy Builder phase.
- Static tests assert state order, source modes, package fields, handoff rules and blocked claims.
- No frontend, backend or packaging behavior changes in SB2.
