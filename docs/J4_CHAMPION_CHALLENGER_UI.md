# J4 Champion vs Challenger Dashboard UI

Phase J4 exposes the comparison workflow as native SQX dashboard UI while preserving the J1/J2/J3 safety contract.

## Scope

- Add the `Champion vs Challenger` tab through `ui_manifest.json` and regenerated `app/js/manifest-data.js`.
- Load `app/js/modules/champion-challenger-core.js` before the new `app/js/modules/champion-challenger.js` UI facade.
- Initialize the UI from `app/js/main.js` through `SQX.championChallenger.init()`.
- Add a restrained Inicio shortcut that opens `tab-cvc`.
- Add desktop and mobile E2E coverage with screenshots.

## Runtime Contract

- `SQX.championChallenger` reads CSV textareas only when the user clicks `Evaluar` or `Cargar ejemplo`.
- `tab-cvc` renders a ranking, formal pass/fail checks, key metrics and OOS stability summaries.
- The UI delegates parsing, escaping, numeric normalization, comparison and OOS scoring to `SQX.championChallengerCore`.
- The UI stores no CSV payloads in localStorage.
- Strategy names and symbols are escaped before rendering.

## Explicit Exclusions

- No `Top Picks` tab, block or headline.
- No `Matriz Completa` tab, heatmap tab or heatmap panel.
- No copied Jose runtime code.
- No backend endpoint, external upload, remote request or browser persistence was added in J4.

## Verification

- JS contracts: `tests/js/contracts/champion_challenger_ui_contracts.mjs`.
- Static contracts: `backend/sqx-edge-tool/test_dashboard_static.py`.
- E2E screenshots: `tests/ui_e2e/dashboard_smoke.mjs` covers the new tab on desktop and mobile when `SQX_E2E_SCREENSHOTS=1`.
