# SQX142 Project Generator Date Period Contract

Status: active generator contract.
Date: 2026-06-03.

This document is the base checklist for date periods in generated Capa1 and Capa2 custom projects. It exists to avoid hiding important post-Forward tasks under generic labels such as "Forward" or "CORR".

## Canonical Periods

| Layer | SQX task | XML file | Input -> Output | Period | Internal OOS / review range | Objective |
| --- | --- | --- | --- | --- | --- | --- |
| Capa1 | Build | `Build-Task1.xml` | none -> `Results` | `2017.10.02-2023.01.01` | none | Mine the market edge in IS. |
| Capa1 | Retest 0 / OOS1 | `Retest-Task3.xml` | `Results` -> `RETEST 0` | `2017.10.02-2025.01.01` | `2023.01.01-2025.01.01` | Passive OOS1 validation. |
| Capa1 | Retest 1 / OOS2 | `Retest-Task1.xml` | `RETEST 0` -> `retest 1` | `2010.01.01-2017.10.02` | none | Cross-broker historical Dukascopy validation. |
| Capa1 | TICK REAL, MC, MC2, Sequential, Monkey, Synthetic, SPP, WFM | `AutomaticRetest-Task*.xml` | chained robustness databanks | `2017.10.02-2023.12.31` | none | Robustness and precision gates over the validated IS window. |
| Capa1 | Forward | `Retest-Task2.xml` | `WFM` -> `Forward` | `2025.01.01-2026.04.08` | `2025.01.01-2026.04.08` | Final untouched OOS3 holdout before CORR1. |
| Capa1 | CORR1 STABILITY RETEST | `Retest-Task4.xml` | `Forward` -> `SQX EDGE CORR1 STABILITY` | `2017.10.02-2026.04.08` | `2025.01.01-2026.04.08` | Stability carrier for Template C2 selection. No tagger, no row filtering. |
| Capa1 | CORR1 TAG REVIEW | `Retest-Task5.xml` | `SQX EDGE CORR1 STABILITY` -> `SQX EDGE CORR1 TAGGED` | `2017.10.02-2026.04.08` | `2025.01.01-2026.04.08` | SQXEdgeCorrelationTagger annotation for Template C2 selection. Filtering remains disabled. |
| Capa2 | Build | `Build-Task1.xml` | none -> `Results` | `2017.10.02-2023.01.01` | none | Operable Capa2 build from the fixed Template C2 edge. |
| Capa2 | Retest 0 / OOS1 | `Retest-Task1.xml` | `Results` -> `RETEST 0` | `2017.10.02-2025.01.01` | `2023.01.01-2025.01.01` | Passive OOS1 validation. |
| Capa2 | Retest 1 / OOS2 | `AutomaticRetest-Task7.xml` | `RETEST 0` -> `retest 1` | `2010.01.01-2017.10.02` | none | Cross-broker historical Dukascopy validation. |
| Capa2 | TICK REAL, MC, MC2, Sequential, Monkey, Synthetic, SPP, WFM | `AutomaticRetest-Task*.xml` / `Optimize-Task1.xml` | chained robustness databanks | `2017.10.02-2023.12.31` | none | Capa2 robustness and precision gates. |
| Capa2 | Forward | `Retest-Task2.xml` | `WFM` -> `Forward` | `2025.01.01-2026.04.08` | `2025.01.01-2026.01.01`, `2026.01.01-2026.04.08` | Final Capa2 holdout before portfolio correlation. |
| Capa2 | C2 CORR STABILITY RETEST | `Retest-Task3.xml` | `Forward` -> `SQX EDGE C2 CORR STABILITY` | `2017.10.02-2026.04.08` | `2025.01.01-2026.01.01`, `2026.01.01-2026.04.08` | Portfolio-correlation stability carrier. No tagger, no row filtering. |
| Capa2 | C2 CORR TAG REVIEW | `Retest-Task4.xml` | `SQX EDGE C2 CORR STABILITY` -> `SQX EDGE C2 CORR TAGGED` | `2017.10.02-2026.04.08` | `2025.01.01-2026.01.01`, `2026.01.01-2026.04.08` | SQXEdgeCorrelationTagger annotation for Portfolio Lab review. Filtering remains disabled. |

## Non-Negotiable Rules

- `CORR1 STABILITY RETEST` and `CORR1 TAG REVIEW` must always be listed explicitly in summaries and verification reports.
- They are not equivalent tasks:
  - Stability retest creates a clean carrier databank from Forward survivors.
  - Tag review consumes that carrier and only annotates through `SQXEdgeCorrelationTagger`.
- `Filter by results of custom analysis` stays disabled in tag review.
- `DeleteFailedStrategies=false`, `FitPortfolio=false` and `CrossChecks=false` stay enforced on CORR review tasks.
- Every generated `AutomaticRetest-*.xml` must set all `MainTestValues dates="true"` so SQX marks and honors the explicit date range.
- These rules apply across all generated timeframes (`M5`, `M15`, `M30`, `H1`, `H4`) and directions (`long`, `short`, `both`).
