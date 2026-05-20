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
- UX-NAV: no active tab after UX-WF2 until the operator defines the next scope.

Run the guard with:

```powershell
python -m pytest backend\sqx-edge-tool\test_docs_state_consistency.py -q
```
