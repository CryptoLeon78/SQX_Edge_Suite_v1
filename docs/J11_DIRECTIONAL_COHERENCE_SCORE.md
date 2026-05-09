# J11 Directional Coherence and Score Pro

Phase J11 adapts JoseLivan commit `ff73a6682e4927671e02c9af253ddbbfa4deb7fb` into the native SQX Edge architecture.

## Accepted Value

- Direction detection from optional long/short trade splits, optional long/short net-profit splits, strategy-name patterns and a conservative `long_only` fallback.
- Directional coherence from OOS `Net Profit` blocks crossed with first-party regime blocks.
- Compact `Score Pro` evidence that rewards formal pass, OOS stability, Temporal Health, EGT v2 and directional coherence while hard-blocking formal failures, EGT v2 risk, declining health and broken directional coherence.
- Redacted review exports and Strategy Builder handoffs carry only reduced direction, coherence and score evidence.
- Strategy Builder displays the imported CVC evidence in its local review list.

## Explicit Exclusions

- No `Top Picks` tab, block, headline or buyer-facing ranking surface is restored.
- No `Matriz Completa`, matrix tab, heatmap tab or heatmap panel is restored.
- No raw CSV, `metrics_by_block`, regime block arrays, price series, localStorage writes, remote calls, broker calls or automatic StrategyQuant generation are introduced.
- Jose runtime code is not copied. The implementation is native and modular: core parsing, regime evidence, dashboard rendering and Strategy Builder handoff remain separate.

## Runtime Surfaces

- `SQX.championChallengerCore.detectDirection(record)` returns `direction`, `source`, `confidence` and compact split/imbalance evidence.
- `SQX.championChallengerRegime.assessDirectionalCoherence(oosRecord, regimeBlocks, directionEvidence)` returns `OK`, `SUSPICIOUS`, `WEAK`, `BROKEN`, `INSUFFICIENT_DATA` or `UNKNOWN`.
- `SQX.championChallenger` renders `Dir`, `Coherencia` and `Score Pro` chips inside existing rows and adds a `Coherencia OK` filter.
- `sqx-edge.champion-challenger-review` and `sqx-edge.strategy-builder-handoff` now include reduced `direction`, `directional_coherence` and `consolidated_score` fields.

## Verification

- `tests/js/contracts/champion_challenger_core_contracts.mjs`
- `tests/js/contracts/champion_challenger_regime_contracts.mjs`
- `tests/js/contracts/champion_challenger_ui_contracts.mjs`
- `tests/js/contracts/strategy_builder_contracts.mjs`
- `backend/sqx-edge-tool/test_dashboard_static.py`

