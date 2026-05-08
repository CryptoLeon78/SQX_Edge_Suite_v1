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
6. The later `Champion vs Challenger` tab is the remaining high-value idea not present in SQX Edge. It should be integrated as a native, tested comparison workflow, not by copying the large global script.

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

Phase A52 creates the first real first-party metric source:

- `backend/sqx-edge-tool/tools/first_party_metric_source.py`
- `backend/sqx-edge-tool/test_first_party_metric_source.py`

The source normalizes our existing dashboard H1 metrics from `app/js/scores-data.js` into `asset_metrics.json`, writes `metric_source_manifest.json` with SHA256 provenance and validates the output through the A51 gate. It explicitly refuses to synthesize M15/M30/H4 values until a real market-derived source is selected.

Phase A53 adds the controlled intake layer for a full multi-timeframe source:

- `backend/sqx-edge-tool/tools/multi_timeframe_source_intake.py`
- `backend/sqx-edge-tool/config/multi_timeframe_source_policy.json`
- `backend/sqx-edge-tool/test_multi_timeframe_source_intake.py`

The intake prepares a reviewable H1/M30/M15/H4 bundle, can generate the A52 H1 baseline, copies only real supplied metric files for M30/M15/H4 and runs the A51 gate. It returns NO_GO when lower/higher timeframe files are missing rather than replacing them with synthetic values.

Phase A54 connects the validated source to review artifacts:

- `backend/sqx-edge-tool/tools/multi_timeframe_plan_artifacts.py`
- `backend/sqx-edge-tool/test_multi_timeframe_plan_artifacts.py`

The artifact generator runs A53 first. When A53 returns GO it writes `Plan Quality Advisor` JSON/Markdown with MTF evidence. When A53 returns NO_GO it writes blocked A53/A54 reports and does not produce plan-review MTF artifacts, avoiding partial or misleading evidence.

Phase A55 adds the real-data bridge needed before A53 can pass with M30/M15/H4:

- `backend/sqx-edge-tool/tools/ohlc_metric_builder.py`
- `backend/sqx-edge-tool/config/ohlc_metric_source_policy.json`
- `backend/sqx-edge-tool/test_ohlc_metric_builder.py`

The builder converts reviewable operator-supplied OHLC CSV files named like `EURUSD_M30.csv` into `asset_metrics[_TF].json`. It computes the metric fields expected by the scoring model and refuses files with insufficient bars. It does not download data or synthesize missing timeframes.

Phase A56 adds the end-to-end real-data run:

- `backend/sqx-edge-tool/tools/real_mtf_pipeline_run.py`
- `backend/sqx-edge-tool/config/real_mtf_pipeline_run.json`
- `backend/sqx-edge-tool/test_real_mtf_pipeline_run.py`

The runner orchestrates A55, A53 and A54. It returns GO only when OHLC CSV metrics are generated, the source intake validates and guarded Plan Quality Advisor artifacts are produced. Empty or incomplete inputs return a traceable NO_GO.

Phase A57 adds the first dashboard exposure, deliberately read-only:

- `backend/sqx-edge-tool/core/mtf_evidence.py`
- `/api/mtf/evidence`
- `app/js/modules/mtf-evidence.js`

The panel appears in Inicio and only shows validated A56 GO summaries. Missing reports, API errors or A56 NO_GO remain blocked/pending, so Priority is not silently promoted to multi-timeframe scoring without real evidence.

Phase A58 adds the internal data-acquisition bridge:

- `backend/sqx-edge-tool/tools/dukas_mt5_ohlc_download.py`
- `backend/sqx-edge-tool/config/dukas_mt5_download.json`

The downloader maps the 33 target assets to MT5/Dukascopy symbols, writes reviewable `ASSET_TF.csv` files into `data/ohlc`, and emits JSON/Markdown/CSV coverage reports. It is intentionally excluded from buyer portable builds because MetaTrader5 and terminal paths are operator dependencies, not basic-user requirements.

Phase A59 performs the first local smoke and records a controlled NO-GO:

- `docs/A59_REAL_DATA_VALIDATION.md`

The machine has the Dukascopy MT5 terminal path and `MetaTrader5` Python package, but the terminal returned IPC timeout during initialization. The next real-data step is operational: open and log into MT5 manually, rerun the smoke, then run the full A58 download and A56 validation.

Phase A60 adds an active-terminal retry mode:

- `docs/A60_MT5_ACTIVE_TERMINAL_MODE.md`

The terminal process is open, responsive and showing `EURUSD,H1`, but the Python IPC bridge still returns timeout. The remaining work is resolving local MT5 session/permission/readiness before any full OHLC download.

Phase A61 adds a repeatable IPC diagnostic:

- `backend/sqx-edge-tool/tools/mt5_ipc_diagnostic.py`
- `docs/A61_MT5_IPC_DIAGNOSTIC.md`

It records Python/MetaTrader5 versions, terminal process state and configured/active/portable initialization variants before any full OHLC download attempt.

Phase A62 completes the real-data bridge:

- `docs/A62_RECENT_BARS_REAL_MTF_GO.md`

The downloader now supports recent-bars acquisition from MT5, aligns the MT5 symbol map with the product manifest universe, downloads 33 assets x 4 timeframes, and A56 returns GO across A55/A53/A54.

Phase J1 starts the selective Champion vs Challenger track:

- `docs/J1_CHAMPION_CHALLENGER_CONTRACT.md`

It defines the safe integration contract for the valuable comparison workflow found in Jose's latest commit. The contract covers accepted CSV/JSON inputs, column aliases, parser rules, scoring rules, OOS block evidence, future regime/EGT context, security boundaries and tests. No Jose runtime code, dashboard UI, Top Picks surface or matrix/heatmap surface is imported in J1.

Phase J2 implements the first native Champion vs Challenger core:

- `app/js/modules/champion-challenger-core.js`
- `tests/js/contracts/champion_challenger_core_contracts.mjs`
- `docs/J2_CHAMPION_CHALLENGER_CORE.md`

It adds pure CSV parsing, alias resolution, numeric normalization, Champion validation, formal comparison and deterministic ranking without dashboard UI, backend endpoints, copied Jose code, Top Picks surfaces or matrix/heatmap surfaces.

Phase J3 adds the OOS stability layer:

- `docs/J3_CHAMPION_CHALLENGER_OOS.md`

It detects columns such as `CAGR/Max DD (OOS1)`, selects a primary OOS metric, computes block count, positive-block ratio, min/max/average/decay, negative streaks and negative Worst Year flags. It still avoids dashboard UI, backend endpoints, copied Jose code, Top Picks surfaces and matrix/heatmap surfaces.

## Deferred Improvements

These should be separate phases, not bundled into A47:

1. Multi-timeframe metric generation: A49 added the dependency-isolated scoring tool, A50 connected it to plan review, A51 added the validation gate, A52 established H1 as a traceable first-party source, A53 added the full-source intake, A54 added guarded plan artifacts, A55 added the OHLC metric builder, A56 added the end-to-end real-data runner, A57 exposed read-only dashboard evidence after GO, A58 added the internal MT5/Dukascopy download gate, A59 recorded the first local MT5 NO-GO smoke, A60 added active-terminal retry mode, A61 added repeatable IPC diagnostics and A62 achieved real A56 GO using recent MT5 bars.
2. Optional market data acquisition: keep MT5/Dukascopy as an operator-only script, excluded from portable buyer builds unless explicitly needed.
3. Champion vs Challenger UI: implement J4 as native dashboard UI after the parser/core/OOS contracts are stable.
4. UI integration: add a read-only "Plan Advisor" panel in Pipeline State after the backend tool stabilizes.
5. Release packaging: decide whether analytical advisor tools are public buyer tools or internal operator tools before adding packaging assertions.

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
- No Champion vs Challenger runtime or UI was imported in J1.
- No sensitive commercial material was imported.
- No third-party credentials, tokens or account passwords were introduced.
- The current advisor uses the available H1 score baseline; A49/A50/A51/A52/A53/A54/A55/A56/A57/A58/A59/A60/A61/A62 now provide a safe backend-to-dashboard path for real multi-timeframe metrics once supplied and validated.
