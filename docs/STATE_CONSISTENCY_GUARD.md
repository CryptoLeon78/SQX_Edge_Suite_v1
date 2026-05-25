# State Consistency Guard

This repo uses `docs/state_consistency_manifest.json` plus the pytest test
`backend/sqx-edge-tool/test_docs_state_consistency.py` to keep public-safe state
docs aligned.

The guard is intentionally simple:

- `required` markers must appear in the listed files.
- `forbidden` stale markers must not appear in the listed files.
- `coreFiles` must exist, so key status docs cannot silently disappear.

When the project state changes, update the manifest in the same commit as the
affected docs. Do not remove stale phrases only from one document; promote the
new canonical wording into the manifest and let the test prove the full set is
aligned.

Current guarded state:

- Remote gate: REMOTE-RILIS-STANDBY is active.
- Clean anchors: REMOTE-8C and REMOTE-8F-CLOSE, with REMOTE-PG-SESSION-FIX applied.
- Next remote action: wait for TESTER-RILIS retest before reopening REMOTE-8G.
- UX/WFCO: WFCO-5 Visual Polish And Desktop QA is completed; Edge Factory is the active desktop-first experience track with command strip, status stack and Portfolio Lab MVP.
- C1-CONFIG1 Phase29: `phase29_capa2_portfolio` is the governed Forward -> Portfolio handoff. Portfolio Lab owns shortlist/diversity/base-risk export from natural Forward survivors only, with defaults `0.2%` base risk and `8-12` from `30-50`.
- Phase29 forbidden markers block SQX execution claims, forced `Results=passed`, `FitPortfolio=true`, profitability guarantees and risk zero claims.
- C1-CONFIG1 Phase30: `phase30_capa2_portfolio_master_contract` is the Portfolio Master operating contract after the Phase29 governed Lab, registered with local evidence `phase30_capa2_portfolio_master_contract_20260525_152846.json`.
- Phase30 required markers keep actual SQX artifact generation blocked until governed Lab output and operator Forward CSV/equity/account/broker context are present.
- Phase30 forbidden markers block SQX execution, forced pass, FitPortfolio drift, live/broker guarantees, profitability guarantees and risk zero claims.
- C1-CONFIG1 Phase30 inputs pending: `phase30_capa2_portfolio_master_inputs_pending` is registered with local evidence `phase30_capa2_portfolio_master_inputs_pending_20260525_154242.json`, `processes=[]`, `cfxGuard=true`, no Capa2 `.cfx` mutation and Portfolio Master blocked until the five real operator inputs exist.

Run the guard with:

```powershell
python -m pytest backend\sqx-edge-tool\test_docs_state_consistency.py -q
```
