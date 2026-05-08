# Jose Livan Repository Comparison

Source reviewed: `https://github.com/jlivanmaseda-maker/sqx-edge-pipeline.git`

Review date: 2026-05-08

## Executive Summary

Jose's repository is a compact earlier SQX Edge implementation with valuable analytical scripts around asset metrics, scoring and plan recommendation. Our application is more advanced in UI structure, modular frontend, portable packaging, backend tests, release discipline, licensing, support, commercial gates and buyer-ready workflows.

The useful extraction is not to copy the legacy dashboard or backend wholesale. The professional integration path is to preserve our architecture and absorb the analytical idea as controlled tooling.

## Valuable Findings

1. `plan_recommender.py` provides a useful data-driven review of the current mining plan against objective dashboard scores.
2. `analyze_assets.py` and `score_assets.py` define a stronger future path for multi-timeframe metrics: ADX, trend efficiency, RSI reversal edge, ATR, volatility of volatility, OU half-life, kurtosis, VWAP rejection and round-number bounce.
3. `download_dukas_bulk.py` shows a possible data acquisition workflow, but it depends on local MetaTrader5 and should remain optional/offline.
4. `stateBackup.js` and backend state backup endpoints are already integrated in our project with stronger tests.
5. Project Generator, Strategy Cleaner and SQX DB ideas are already integrated and extended in our current backend.

## Integration Decision

Phase A47 integrates the highest-value low-risk improvement: a first-party `Plan Quality Advisor`.

Implemented as:

- `backend/sqx-edge-tool/tools/plan_quality_advisor.py`
- `backend/sqx-edge-tool/test_plan_quality_advisor.py`

The advisor reads our current sources of truth:

- `backend/sqx-edge-tool/config/assets.json`
- `backend/sqx-edge-tool/config/ui_manifest.json`
- `backend/sqx-edge-tool/config/plan.json`
- `app/js/scores-data.js`

It produces:

- current plan annotation by objective composite score,
- diversified recommended plan,
- keep/review/add delta, explicitly marked as review guidance rather than automatic replacement,
- Markdown or JSON output for operator review.

## Deferred Improvements

These should be separate phases, not bundled into A47:

1. Multi-timeframe score ingestion: convert Jose's `analyze_assets.py` and `score_assets.py` into dependency-isolated backend tools with fixture tests.
2. Optional market data acquisition: evaluate MT5/Dukascopy data download as an operator-only script, excluded from portable buyer builds unless explicitly needed.
3. UI integration: add a read-only "Plan Advisor" panel in Pipeline State after the backend tool stabilizes.
4. Release packaging: decide whether analytical advisor tools are public buyer tools or internal operator tools before adding packaging assertions.

## Risk Notes

- No legacy HTML tabs were restored.
- No sensitive commercial material was imported.
- No third-party credentials, tokens or account passwords were introduced.
- The current advisor uses the available H1 score baseline; real multi-timeframe scoring remains a future upgrade.
