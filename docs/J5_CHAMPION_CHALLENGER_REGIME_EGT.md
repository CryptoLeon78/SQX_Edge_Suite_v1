# J5 Champion vs Challenger Regime/EGT Evidence

Phase J5 adds contextual Regime/EGT evidence to Champion vs Challenger using first-party SQX datasets.

## Scope

- Add `SQX.championChallengerRegime` as a focused adapter in `app/js/modules/champion-challenger-regime.js`.
- Consume `SQX_HISTORICAL_DATA` through `SQX.datasets.historical()`.
- Consume `SQX_SCORES_DATA` through `SQX.datasets.scores()`.
- Resolve imported symbols through a normalized product-universe index.
- Surface the evidence in `tab-cvc` as an EGT metric and summary count.

## Evidence Contract

The adapter computes:

- historical coverage in months
- 12-month and 36-month return
- 36-month max drawdown
- 12-month monthly volatility
- `regimen` objective and composite score from first-party SQX scores

Labels remain contextual evidence, not final truth:

- `COMPLIANT`
- `RISK`
- `FLAT`
- `UNKNOWN`

`UNKNOWN` blocks regime labels when coverage or score evidence is insufficient.

## Explicit Boundaries

- No copied Jose runtime code.
- No remote calls.
- No raw CSV persistence.
- No `Top Picks` tab, block or headline.
- No `Matriz Completa` tab, heatmap tab or heatmap panel.
- No promotion decision is made only from Regime/EGT evidence.

## Verification

- JS contracts: `tests/js/contracts/champion_challenger_regime_contracts.mjs`.
- UI contracts: `tests/js/contracts/champion_challenger_ui_contracts.mjs`.
- Static contracts: `backend/sqx-edge-tool/test_dashboard_static.py`.
- E2E screenshots: `tests/ui_e2e/dashboard_smoke.mjs` verifies desktop and mobile CVC evidence rendering.
