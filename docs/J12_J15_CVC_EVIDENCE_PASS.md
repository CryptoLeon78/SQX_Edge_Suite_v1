# J12-J15 Champion vs Challenger Evidence Pass

Status: implemented as a native SQX Edge integration of JoseLivan commits `7a0b75c`, `333bd60` and `677efd8`.

## Summary

J12-J15 enriches `Champion vs Challenger` without copying Jose's legacy dashboard runtime. The value is now part of the modular CVC stack: real OOS timeline, true `short_only` EGT v2 thresholds, `OK_MEAN_REVERT`, edge archetype detection, volatility coherence and a dedicated SQX Views export contract.

## Integrated Value

- `SQX Views` adds `CVC Decision Cert` as the mandatory CVC export view for Champion, Challengers and OOS evidence.
- `SQX.championChallengerCore` parses `TimeFrame`, `Avg. Bars in Trade` and `Avg. Trades Per Month`, builds OOS block timelines and classifies edge archetype.
- `SQX.championChallengerRegime` supports `short_only` in EGT v2, detects `OK_MEAN_REVERT` and computes volatility coherence from Net Profit by OOS block.
- `SQX.championChallenger` renders compact chips for direction, coherence, archetype, volatility and Score Pro, and includes reduced evidence in safe review exports and internal handoffs.

## Product Boundaries

- No Top Picks, Matriz Completa, heatmap or legacy Jose HTML panel is restored.
- No raw CSV, `metrics_by_block`, historical price series or regime block payload is exported.
- Strategy Builder remains hidden/retired as a visible dashboard surface; existing handoff code is only a tested internal contract.

## Verification

- JS contracts cover `short_only`, `OK_MEAN_REVERT`, arquetype classification, volatility coherence, CVC Decision Cert and redacted exports.
- Full phase verification must also run Python backend tests and E2E screenshots before commit.
