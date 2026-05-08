# Jose Livan Repository Comparison

Source reviewed: `https://github.com/jlivanmaseda-maker/sqx-edge-pipeline.git`

Review date: 2026-05-08

## Executive Summary

Jose's repository is a compact earlier SQX Edge implementation with valuable analytical scripts around asset metrics, scoring and plan recommendation. Our application is more advanced in UI structure, modular frontend, portable packaging, backend tests, release discipline, licensing, support, commercial gates and buyer-ready workflows.

The useful extraction is not to copy the legacy dashboard or backend wholesale. The professional integration path is to preserve our architecture and absorb the analytical idea as controlled tooling.

## Valuable Findings

1. `plan_recommender.py` provides a useful data-driven review of the current mining plan against objective dashboard scores.
2. `analyze_assets.py` and `score_assets.py` define a stronger path for multi-timeframe metrics: ADX, trend efficiency, RSI reversal edge, ATR, volatility of volatility, OU half-life, kurtosis, VWAP rejection and round-number bounce.
3. `download_dukas_bulk.py` shows a possible data acquisition workflow, but it depends on local MetaTrader5 and should remain optional/offline.
4. `stateBackup.js` and backend state backup endpoints are now integrated in our project with stronger tests and a native dashboard UI.
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

Phase A49 implements the controlled scoring half of the deferred multi-timeframe idea:

- `backend/sqx-edge-tool/tools/multi_timeframe_scoring.py`
- `backend/sqx-edge-tool/test_multi_timeframe_scoring.py`

It consumes supplied `asset_metrics.json` / `asset_metrics_<TF>.json` files and produces:

- dashboard-like scores per timeframe,
- weighted multi-timeframe consensus per asset/category,
- coverage, stability label and best-TF evidence,
- Markdown or JSON output.

It intentionally does not download market data, alter HTML or update dashboard scores automatically.

Phase A50 connects that consensus to `Plan Quality Advisor` as optional evidence:

- `plan_quality_advisor.py --mtf-metrics-dir <dir>` keeps H1 ordering but enriches each current/recommended mining with MTF weighted score, coverage, consensus state and best timeframe.
- If no metric directory is supplied, the advisor remains fully compatible with the H1-only report.
- The dashboard UI remains unchanged until first-party metric files are generated and validated.

Phase A51 adds a first-party metric validation gate:

- `backend/sqx-edge-tool/tools/multi_timeframe_metric_gate.py`
- `backend/sqx-edge-tool/test_multi_timeframe_metric_gate.py`

The gate validates supplied `asset_metrics[_TF].json` folders before they are accepted as first-party multi-timeframe evidence. It reports GO/NO-GO, missing files, expected asset coverage, metric completeness, unknown assets, scoring compatibility and SHA256 fingerprints. It intentionally does not download market data, change dashboard scores or expose a new UI panel.

## Deferred Improvements

These should be separate phases, not bundled into A47:

1. Multi-timeframe metric generation: A49 added the dependency-isolated scoring tool, A50 connected it to plan review and A51 added the validation gate; remaining work is choosing or generating the first-party metric source and running the gate on real files.
2. Optional market data acquisition: evaluate MT5/Dukascopy data download as an operator-only script, excluded from portable buyer builds unless explicitly needed.
3. UI integration: add a read-only "Plan Advisor" panel in Pipeline State after the backend tool stabilizes.
4. Release packaging: decide whether analytical advisor tools are public buyer tools or internal operator tools before adding packaging assertions.

## A48 HTML Recovery Decision

A48 selectively recovers HTML-side value from the comparison:

- Native backup/restore controls in Pipeline State using the existing local `/api/state/*` endpoints.
- Dynamic Plan v2 summary in Workflow so the methodology page reflects the current plan instead of only static counts.
- Locked Priority multi-timeframe preparation that keeps the current H1 baseline honest until A49 builds real scoring.

Explicitly excluded by product decision:

- No `Top Picks` block or tab.
- No `Matriz Completa`, heatmap tab or matrix panel.

## Risk Notes

- No legacy HTML tabs were restored.
- No sensitive commercial material was imported.
- No third-party credentials, tokens or account passwords were introduced.
- The current advisor uses the available H1 score baseline; A49/A50/A51 now provide a safe backend path for real multi-timeframe metrics once supplied and validated.
