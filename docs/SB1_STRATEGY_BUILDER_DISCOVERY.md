# SB1 Strategy Builder Discovery

Phase SB1 defines the minimum viable Strategy Builder scope for the commercial "only one platform" hook.

This phase is discovery and contract work only. It does not add a live builder UI, generation endpoint, optimizer, trading signal engine or performance claim.

## Product Intent

Strategy Builder should become a guided bridge between SQX Edge evidence and StrategyQuant execution:

1. Read reviewed candidate context from SQX Edge.
2. Convert that context into a structured strategy idea package.
3. Hand the operator toward Project Generator, SQX Views and StrategyQuant validation.
4. Keep every claim, setting and generated artifact reviewable before use.

The buyer-facing promise is not "the app prints profitable strategies". The useful promise is:

- one workflow for asset selection, idea framing, project setup, validation views and candidate review;
- fewer manual copy/paste steps;
- better traceability from evidence to StrategyQuant work;
- safer repetition for paid setup/support services.

## Existing Inputs We Can Reuse

| Source | Existing contract | Value for Strategy Builder |
| --- | --- | --- |
| Champion vs Challenger | `sqx-edge.strategy-builder-handoff` from J6 | Reviewed candidate, normalized metrics, OOS summary and Regime/EGT context. |
| Project Generator | custom projects, starter profiles, buyer profile families and portable preset packs | Builds the StrategyQuant project shell for the selected asset/timeframe/profile. |
| SQX Views | buyer-ready templates, profile packs and validation workflow packs | Creates the validation lens that the strategy idea must survive. |
| Plan Quality / MTF evidence | controlled scoring and GO/NO-GO artifacts | Adds asset/timeframe context without inventing synthetic evidence. |
| Strategy Cleaner | strategy cleanup and deletion workflows | Keeps the result reviewable and prevents noisy candidate piles. |
| Product manifest | asset universe, Pro boundaries and packaging exclusions | Prevents unsupported symbols, private data or internal tools from leaking into buyer flows. |

## Minimum Viable Builder Scope

SB2 should design a controlled flow that produces a local JSON package with:

- `strategy_builder_package_id`
- `source_handoff` summary from J6, if used
- asset, timeframe and market family
- idea archetype, such as trend-following, mean-reversion, breakout, pullback or volatility filter
- entry indicator family candidates
- exit/risk envelope suggestions
- required validation views
- recommended Project Generator preset/profile
- operator checklist before StrategyQuant execution
- traceability notes back to evidence and selected presets

The first implementation should be read-only/package-oriented. It should prepare the operator's work, not silently create a strategy that pretends to be validated.

## Non-Goals

- No auto-trading.
- No live broker or exchange integration.
- No promise of profitability.
- No hidden optimization.
- No bypass of StrategyQuant validation.
- No raw checkout, license, customer or private commercial data.
- No remote AI calls with strategy data.
- No Top Picks or matrix/heatmap restoration.

## Proposed Future Payloads

### `sqx-edge.strategy-builder-scope`

Discovery-level scope document for tests and UI planning:

- `type`
- `version`
- `created_at`
- `allowed_inputs`
- `blocked_inputs`
- `minimum_package_fields`
- `non_goals`

### `sqx-edge.strategy-builder-package`

Operator package produced by a future SB3 prototype:

- `type`
- `version`
- `created_at`
- `source_handoff`
- `asset_profile`
- `idea_archetype`
- `indicator_candidates`
- `risk_envelope`
- `validation_pack`
- `project_generator_profile`
- `operator_checklist`
- `traceability`

## Safe Claims

Allowed:

- "Guided strategy idea packaging."
- "Evidence-linked handoff to StrategyQuant workflows."
- "Reusable validation and project setup flow."
- "Designed to reduce manual setup time."

Blocked:

- "Guaranteed profitable."
- "Fully automated trading system."
- "No validation required."
- "Institutional-grade signal engine."
- "AI-generated strategies without review."

## Recommended SB2 Design

SB2 should design the workflow before UI:

1. Source: start blank, from CVC handoff, from Project Generator preset or from SQX View workflow.
2. Context: asset, timeframe, market family, direction, regime label and available evidence.
3. Idea: choose archetype and indicator families from the existing SQX indicator taxonomy.
4. Package: build a local JSON preview and validation checklist.
5. Handoff: suggest Project Generator profile and SQX Views pack.
6. Review: require operator confirmation before any export/download.

## Acceptance Criteria

- SB1 is documented before runtime changes.
- Governance and roadmap point to SB2 as the next Strategy Builder phase.
- Static tests assert the product intent, non-goals, payload names and safe-claims boundary.
- No frontend, backend or packaging behavior changes in SB1.
