# Changelog

## 2026-05-24 - C1-CONFIG1 Monkey Test CrossChecks

- Adds `monkey-crosschecks-target` with dry-run-first backup/diff/apply over local base and repo template.
- Keeps `AutomaticRetest-Task6.xml` as a pure Monkey gate: only `MonteCarloRetest` is active, only `RealMonkeyTest` is active, `NumberOfSimulations=200`, `MCUseFullSample=true`, `MCBacktestPrecision=-1` and `MaxChange=90`.
- Activates the two Monkey acceptance filters so the retest is not advisory-only: `NetProfit >= 50%` of main and `Max DD <= 200%` of main, preserving natural passed/failed rows.
- Keeps `SyntheticBootstrapV2` and `SyntheticBootstrapV3` disabled for the later Synthetic/Syntetic task, and clears active methods hidden in inactive `MonteCarloManipulation` and `WhatIf`.
- Records local answers for `Monkey Test > CrossChecks` (`372/372`), report `phase9_monkey_test_crosschecks_20260524_101913.json`, idempotent dry-run (`changed=false`, `changedActionCount=0`, `guardOk=true`) and next exact block `phase9_monkey_test_passive_generation`.

## 2026-05-24 - C1-CONFIG1 Monkey Test Data Databanks Resources Options

- Adds `monkey-data-databanks-resources-options-target` with dry-run-first backup/diff/apply over local base and repo template.
- Keeps Monkey Test's SQX142-compatible dual carrier `Data + CustomData`, synchronizing `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, commissions and chart seed.
- Confirms `Input=Sequential` / `Output=Monkey Test`, no nested OOS split, resources `TICK/EETUS`, no resource sessions and Options inert with `LimitTimeRange=false`, `RealisticGapsHandling=false` and `StoreChartData=false`.
- Updates Project Generator policy so `AutomaticRetest-Task6.xml` does not receive timeframe trading-window injection; generated Capa1 customs still adapt symbol/timeframe/spread/resources by asset and target profile.
- Records local answers for `Monkey Test > Data` (`7/7`), `Databanks` (`2/2`), `Resources` (`1,899/1,899`) and `Options` (`34/34`), plus report `phase9_monkey_test_data_databanks_resources_options_20260524_093446.json`; next exact block is `phase9_monkey_test_crosschecks`.

## 2026-05-24 - C1-CONFIG1 Monkey Test Open

- Adds `monkey-open-report` to open Phase 9 after Sequential closeout without launching SQX or mutating task values.
- Maps `Monkey Test` to `AutomaticRetest-Task6.xml` and verifies the chain `Input=Sequential` / `Output=Monkey Test` on local base and repo template.
- Confirms `MonteCarloRetest` as the only active crosscheck with `RealMonkeyTest`, `NumberOfSimulations=200`, `MCUseFullSample=true` and `MaxChange=90`.
- Records pending decisions before mutation: Data/CustomData carrier, generator-owned resources, inactive acceptance filters, hidden active methods inside inactive checks and passive generation/static tabs.
- Writes local phase report `phase9_monkey_test_open_20260524_091714.json`, generates the full `Monkey Test` questionnaire (`20,036` detected entries, `12,332` donor/base differences) and sets next exact block `phase9_monkey_test_data_databanks_resources_options`.

## 2026-05-24 - C1-CONFIG1 Sequential Closeout

- Adds `sequential-closeout-report` to close Phase 8 only when MC2 previous gate and all Sequential guards are green/idempotent in dry-run mode.
- Verifies `sequential-data-databanks-resources-options-target`, `sequential-crosschecks-target`, `sequential-passive-generation-target` and `sequential-static-tabs-target` over local base and repo template with `changed=false`, `changedActionCount=0` and `guardOk=true`.
- Records `phase8_sequential_closeout_20260524_085653.json` with `issues=[]`, `warnings=[]`, `processes=[]`, chain `Input=MC2 / Output=Sequential`, active `SequentialOptimization` and next exact block `phase9_monkey_test_open`.

## 2026-05-24 - C1-CONFIG1 Sequential Static Tabs

- Adds `sequential-static-tabs-target` with dry-run-first backup/diff/apply over local base and repo template.
- Closes Sequential inert tabs without disabling `SequentialOptimization`: Rankings stay `type=never`, `DeleteFailedStrategies=false`, `ForceRunCrossChecks=false`, `FitPortfolio=false`, `CustomAnalysis.filter=false` and no ranking conditions.
- Keeps `FixedSize` as the active money-management method, ATMs disabled, Notes preserved and SelectedStrategies empty/missing accepted.
- Hardens Sequential `CustomData` as the SQX142 dual carrier partner to Data, preserving `subcharts=false`, `Commission=0.0` and no donor tokens.
- Records local answers for `Sequential > Rankings` (`22/22`), `ATMs` (`9/9`), `RiskMoneyManagement` (`25/25`), `Notes` (`1/1`), `SelectedStrategies` (`0/0`) and `CustomData` (`6/6`), plus report `phase8_sequential_static_tabs_20260524_084121.json`; next exact block is `phase8_sequential_closeout`.

## 2026-05-24 - C1-CONFIG1 Sequential Passive Generation

- Adds `sequential-passive-generation-target` with dry-run-first backup/diff/apply over local base and repo template.
- Normalizes `Sequential` from the SQX placeholder `Strategies to improve` to `StrategyType.improveDatabank=MC2`, making the MC2 -> Sequential chain explicit.
- Leaves Sequential as a passive robustness gate: `PartsToImprove` disabled, evolution restarts off, no Signals, no Stop/Limit entry blocks, indicators preserved, and only `EnterAtMarket` plus `ExitAfterBars` probability `100`.
- Records local answers for `Sequential > PartsToImprove` (`8/8`), `WhatToBuild` (`67/67`) and `Blocks` (`17,583/17,583`), plus report `phase8_sequential_passive_generation_20260524_081943.json`; next exact block is `phase8_sequential_static_tabs`.

## 2026-05-24 - C1-CONFIG1 Sequential CrossChecks

- Adds `sequential-crosschecks-target` with dry-run-first backup/diff/apply over local base and repo template.
- Keeps `SequentialOptimization` as the only active Sequential crosscheck: `ApplyToStrategy=false`, `DistributionUp=130`, `DistributionDown=70`, `Steps=12`, `PctToPass=80`, `ResultsCount=5` and `StabilityRange=25`.
- Limits parametrization to `Periods=true`, `Constants=true` and `ExitParamsUsed=true`; entry logic, entry params, shifts, unused exits, booleans and broad recommended mode stay off.
- Clears extra Sequential acceptance `Conditions`, preserves natural passed/failed outcomes and switches hidden methods inside inactive crosschecks off.
- Records local answers for `Sequential > CrossChecks` (`321/321`) and report `phase8_sequential_crosschecks_20260524_074726.json`; next exact block is `phase8_sequential_passive_generation`.

## 2026-05-24 - C1-CONFIG1 Sequential Data Databanks Resources Options

- Adds `sequential-data-databanks-resources-options-target` with dry-run-first backup/diff/apply over local base and repo template.
- Keeps Sequential's SQX142-compatible dual carrier `Data + CustomData`, but synchronizes period, precision, session, chart seed, spread and commissions instead of deleting one carrier without UI evidence.
- Confirms `Sequential` chain as `Input=MC2` / `Output=Sequential`, `ROBUSTNESS_C1`, `testPrecision=2`, no nested OOS split, resources `TICK/EETUS`, no sessions and options `LimitTimeRange=false`, `RealisticGapsHandling=false`, `StoreChartData=false`.
- Updates Project Generator policy so `AutomaticRetest-Task3.xml` does not receive timeframe trading-window injection; generated Capa1 customs still adapt symbol/timeframe/spread/resources by asset and target profile.
- Records local answers for `Sequential > Data` (`7/7`), `Databanks` (`2/2`), `Resources` (`1,899/1,899`) and `Options` (`34/34`), plus report `phase8_sequential_data_databanks_resources_options_20260524_071310.json`; next exact block is `phase8_sequential_crosschecks`.

## 2026-05-24 - C1-CONFIG1 Sequential Open

- Adds `sequential-open-report` to open Phase 8 after MC2 closeout without launching SQX or mutating task values.
- Maps `Sequential` to `AutomaticRetest-Task3.xml` and verifies the chain `Input=MC2` / `Output=Sequential` on local base and repo template.
- Confirms only `SequentialOptimization` is active, with `ApplyToStrategy=false`, `PctToPass=80`, `ResultsCount=5` and `StabilityRange=25`.
- Records the next decisions before mutation: whether to normalize `StrategyType.improveDatabank` from the SQX placeholder `Strategies to improve` to `MC2`, and whether `Data` or `CustomData` is the canonical carrier.
- Writes local phase report `phase8_sequential_open_20260524_065707.json`; next exact block is `phase8_sequential_data_databanks_resources_options`.

## 2026-05-24 - C1-CONFIG1 MC2 Closeout

- Adds `mc2-passive-generation-target`, `mc2-static-tabs-target` and `mc2-closeout-report` to decide and close `phase7_mc2_static_or_next_block` before opening `Sequential`.
- Applies the MC2 safety closeout on local base and repo template: `StrategyType.improveDatabank=MC`, passive `PartsToImprove`, disabled evolution toggles, no signals, no stop/limit blocks, preserved indicators and only `EnterAtMarket` plus `ExitAfterBars` at `100`.
- Normalizes MC2 static tabs: `DeleteFailedStrategies=false`, `ForceRunCrossChecks=false`, `FitPortfolio=false`, `CustomAnalysis.filter=false`, ATMs disabled, FixedSize active, `SelectedStrategies` empty and `CustomData` still canonical for `ROBUSTNESS_C1`.
- Records the implementation detail that MC2 had no explicit `Blocks`; the guard copies missing passive controls from the `MC` source task before enforcing the contract, avoiding a new block universe before `Sequential`.
- Writes closeout report `phase7_mc2_closeout_20260524_064023.json` with `ok=true`, `issues=0`, `processes=0`; all four MC2 guards are green and idempotent, and the next exact phase is `phase8_sequential_open`.

## 2026-05-23 - C1-CONFIG1 MC2 Data Databanks Resources Options

- Adds `mc2-data-databanks-resources-options-target` to close `MC 2 > Data / Databanks / Resources / Options` with dry-run-first guard over local base and repo template.
- Documents that `MC 2` has no direct `Data` section in this SQX automatic retest shape: `CustomData` is the canonical setup carrier with `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, `MetaTrader4`, full `MainTestValues` and `Commission=0.0`.
- Keeps the chain explicit: `Input=MC`, `Output=MC2`, resources `TICK/EETUS`, no resource sessions, no donor `USDJPY/H4` leakage and no nested OOS split.
- Keeps MC2 options fast and inert: `LimitTimeRange=false`, `RealisticGapsHandling=false`, `StoreChartData=false`; Project Generator now skips trading-window injection for `MC` and `MC 2` while still recalculating MC2 adaptive spread by asset/timeframe.
- Records local answers for `MC 2 > Data` (`0/0` allow-empty), `Databanks` (`2/2`), `Resources` (`4/4`) and `Options` (`34/34`), plus report `phase7_mc2_data_databanks_resources_options_20260523_233831.json`; next exact block is `phase7_mc2_static_or_next_block`.

## 2026-05-23 - C1-CONFIG1 MC2 CrossChecks

- Adds `mc2-crosschecks-target` to close `MC 2 > CrossChecks` with dry-run-first backup/diff/apply and an idempotent guard over local base and repo template.
- Changes `MC 2 / RandomizeSpread` from absolute `30-50` to adaptive `baseSpread x2-x5`; the generic seed `AUDCAD/H1` spread `2.0` becomes `4-10`.
- Adds Project Generator support via `adaptiveSpreadStress`, so generated customs recalculate MC2 spread stress per asset/timeframe; AUDCAD/H4 fallback spread `10` validates as `20-50`.
- Keeps `MonteCarloRetest` as the only active MC2 crosscheck with `100` simulations, `MCUseFullSample=true`, existing `AnnualPctReturnDDRatio` acceptance filters, natural failed/passed rows and no forced pass state.
- Records academic/local rationale: transaction-cost stress is necessary, but x2-x5 is a bounded local heuristic backed by clone smokes, not a universal theorem; repeated tuning against validation data remains a data-snooping risk.
- Records local ledger answer for `MC 2 > CrossChecks` (`133/133`) and report `phase7_mc2_crosschecks_20260523_230735.json`; the following `MC 2 > Data / Databanks / Resources / Options` block is now closed.

## 2026-05-23 - C1-CONFIG1 MC Closeout

- Adds `mc-closeout-report` to consolidate all four Phase 6 MC guards in dry-run mode before moving to MC 2.
- Closes Phase 6 `MC` formally with local report `phase6_mc_closeout_20260523_224903.json`; `mc-data-databanks-resources-options-target`, `mc-crosschecks-target`, `mc-passive-generation-target` and `mc-static-tabs-target` are all idempotent on local base and repo template.
- Keeps the final MC contract intact: `Input=TICK`, `Output=MC`, fast/simulated `testPrecision=2`, only `MonteCarloManipulation` active, no internal OOS split, natural failed/passed rows and no portfolio selection.
- Updates local task-config session state to `currentPhase=phase6_mc_closeout` and `nextPhase=phase7_mc2_open`; next exact work is `MC 2 > CrossChecks`.

## 2026-05-23 - C1-CONFIG1 MC Static Tabs

- Adds `mc-static-tabs-target` to close `MC > Rankings / ATMs / RiskMoneyManagement / Notes / SelectedStrategies / CustomData` with dry-run-first backup/diff/apply and a composed MC guard.
- Disables `FitPortfolio` in `MC > Rankings`; MC pass/fail remains owned by the `MonteCarloManipulation` crosscheck, with no extra Ranking conditions, `DeleteFailedStrategies=false` and `ForceRunCrossChecks=false`.
- Keeps static tabs conservative: `ATMs` disabled, `RiskMoneyManagement` fixed-size, Notes preserved and `SelectedStrategies` empty/absent accepted.
- Normalizes `CustomData` as generic/no-donor seed with `testPrecision=2`, `Commission=0.0`, the main chart seed and no `USDJPY/H4` copy.
- Records local ledger answers for `MC > Rankings` (`22/22`), `MC > ATMs` (`9/9`), `MC > RiskMoneyManagement` (`25/25`), `MC > Notes` (`1/1`), `MC > SelectedStrategies` (`0/0` allow-empty) and `MC > CustomData` (`6/6`), with post-apply dry-run idempotent and `guardOk=true`.

## 2026-05-23 - C1-CONFIG1 MC Passive Generation

- Adds `mc-passive-generation-target` to close `MC > PartsToImprove / WhatToBuild / Blocks` with dry-run-first backup/diff/apply and a guard for passive retest behavior.
- Keeps `MC` as a pure perturbation retest consuming `TICK`: `StrategyType.improveDatabank=TICK`, `improveATM=false`, Entry/Order/Exit improvements off, last-generation/fresh-blood/evolution restart toggles off and no unknown SQX passive enum invented.
- Preserves the existing MC BuildingBlocks universe instead of copying Mining15 donor blocks, while enforcing `signals=0`, `stopLimitBlocks=0`, `activeIndicatorCount=50`, only `EnterAtMarket` and only `ExitAfterBars` at probability `100`.
- Records local ledger answers for `MC > PartsToImprove` (`8/8`), `MC > WhatToBuild` (`67/67`) and `MC > Blocks` (`17,583/17,583`), with post-apply dry-run idempotent and `guardOk=true`.

## 2026-05-23 - C1-CONFIG1 MC CrossChecks

- Adds `mc-crosschecks-target` to close the Phase 6 `MC > CrossChecks` block with dry-run-first backup/diff/apply and guards for the exact active Monte Carlo method.
- Keeps `MC` focused on trade-order robustness only: `CrossChecks use=true/evaluateAll=true`, only `MonteCarloManipulation` active, `RandomizeTradesOrder=resampling`, `RandomlySkipTrades=false`, `NumberOfSimulations=200` and `MCUseFullSample=true`.
- Preserves natural failed/passed outcomes with acceptance checks at confidence `80`: MC net profit must be at least `40%` of main net profit and MC drawdown must stay within `200%` of main drawdown.
- Leaves `MC 2`, `Monkey Test` and `Synthetic` as separate tasks, disables active methods hidden inside inactive crosschecks, bounds nested disabled setups to `ROBUSTNESS_C1`, and records ledger answers for `MC > CrossChecks` (`303/303`) with post-apply dry-run idempotent and `guardOk=true`.

## 2026-05-23 - C1-CONFIG1 MC Data/Databanks/Resources/Options

- Adds `mc-data-databanks-resources-options-target` to close the first Phase 6 `MC` block with dry-run-first backup/diff/apply and guards for no nested OOS, no donor USDJPY/H4 leak and generator-owned resources.
- Keeps MC as a fast/simulated Monte Carlo perturbation gate after TICK: `Input=TICK`, `Output=MC`, `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, `precision=TICK`, `timezone=EETUS`, empty sessions and resource `dateTo=2023.12.31`.
- Keeps MC Options generic and computationally light: `StoreChartData=false`, `RealisticGapsHandling=false`, `LimitTimeRange=false`, without copying the donor H4 trading window.
- Records local ledger answers for `MC > Data` (`7/7`), `MC > Databanks` (`2/2`), `MC > Resources` (`1,899/1,899`) and `MC > Options` (`34/34`), with post-apply dry-run idempotent and `guardOk=true`.

## 2026-05-23 - C1-CONFIG1 TICK REAL Closeout And MC Opened

- Closes Phase 5 `TICK REAL` formally with local report `phase5_tick_real_closeout_20260523_211917.json`; all four TICK guards are idempotent with `changed=false`, `changedActionCount=0` and `guardOk=true`.
- Opens Phase 6 `MC`, mapped to `AutomaticRetest-Task1.xml`, with local questionnaire `13` tabs, `19,966` entries and `12,326` donor/base differences; current chain is `Input=TICK` / `Output=MC`.
- Adds local-only `sqx-academic-lopez` skill/profile/action for source-backed OOS/MC/data-snooping/backtest-overfitting consultation; remote testers do not receive this capability.
- Records the initial MC policy before applying CFX changes: use precision fast/simulated for compute efficiency, avoid internal OOS split by default, keep passed/failed natural and leave asset/timeframe/spread/swap/resources generator-owned.

## 2026-05-23 - C1-CONFIG1 TICK REAL Static/CrossChecks Gate

- Adds `tick-real-static-crosschecks-target` to close the Phase 5 `TICK REAL` static tabs and CrossChecks block with dry-run-first backup/diff/apply and a composed guard over prior TICK decisions.
- Turns off the remaining executable crosscheck leftovers: `CrossChecks use=false/evaluateAll=false`, `0` active crosschecks and `0` active `Settings/Methods/Method` entries after clearing MonteCarloRetest, MonteCarloManipulation and WhatIf remnants.
- Keeps static validation tabs safe: `FixedSize=true`, `FixedAmount=false`, `ATMs enable=false`, Notes unchanged and CustomData audited as `ROBUSTNESS_C1` without Mining15 `USDJPY` donor leakage.
- Records local ledger answers for `TICK REAL > CrossChecks` (`303/303`), `RiskMoneyManagement` (`25/25`), `ATMs` (`9/9`), `CustomData` (`6/6`) and `Notes` (`1/1`), with post-apply dry-run idempotent and `guardOk=true`.

## 2026-05-23 - C1-CONFIG1 TICK REAL Passive Generation Gate

- Adds `tick-real-passive-generation-target` to close the Phase 5 `TICK REAL` PartsToImprove/WhatToBuild/Blocks block with dry-run-first backup/diff/apply and passive-retest guards.
- Keeps TICK REAL as a pure precision-data retest after `RETEST 1`: `StrategyType.improveDatabank=retest 1`, all improvement toggles off, last-generation/fresh-blood/evolution restarts off and no unknown SQX passive enum invented.
- Preserves the existing TICK REAL BuildingBlocks universe to avoid changing strategy logic, while enforcing `signals=0`, `stopLimitBlocks=0`, `activeIndicatorCount=50`, only `EnterAtMarket` and only `ExitAfterBars` at probability `100`.
- Records local ledger answers for `TICK REAL > PartsToImprove` (`9/9`), `TICK REAL > WhatToBuild` (`67/67`) and `TICK REAL > Blocks` (`17,583/17,583`), with post-apply dry-run idempotent and `guardOk=true`.

## 2026-05-23 - C1-CONFIG1 TICK REAL Options/Rankings

- Adds `tick-real-options-rankings-target` to close the Phase 5 `TICK REAL` Options/Rankings block with dry-run-first backup/diff/apply and anti-coladero guards.
- Keeps TICK REAL as a precision-data robustness retest without adding an internal IS/OOS1 split; `RETEST 0` remains the owner of IS/OOS1 validation to reduce repeated-OOS selection pressure.
- Applies realistic passive settings: `RealisticGapsHandling=true`, generator-owned time window, `DeleteFailedStrategies=false`, `ConditionsType=1`, `FitPortfolio=false`, `ForceRunCrossChecks=false` and `CustomAnalysis.filter=false`.
- Keeps active total-tick filters strict enough for this near-realism gate: `NumberOfTrades >= 200`, `ProfitFactor >= 1.3`, `WinningPct >= 50` and `ReturnDDRatio >= 4`, while preserving natural failed rows.
- Records local ledger answers for `TICK REAL > Options` (`34/34`) and `TICK REAL > Rankings` (`46/46`), with post-apply dry-run idempotent and `guardOk=true`.

## 2026-05-23 - C1-CONFIG1 TICK REAL Data/Databanks/Resources

- Adds `tick-real-data-databanks-resources-target` to close the first Phase 5 `TICK REAL` block with dry-run-first backup/diff/apply and a resource guard.
- Applies the precision-data chain to local Capa1 base and `backend/sqx-edge-tool/templates/Capa1_Long.cfx`: `Input=retest 1`, `Output=TICK`, `ROBUSTNESS_C1` (`2017.10.02-2023.12.31`), `testPrecision=2`, `No Session` and no nested OOS ranges.
- Keeps Capa1 base generic: Darwinex placeholder resources stay bounded and SQX-compatible, sessions stay empty, `CustomBlocks` are preserved and no Mining15 `USDJPY/H4` donor resources are copied.
- Records local ledger answers for `TICK REAL > Data` (`7/7`), `TICK REAL > Databanks` (`3/3`) and `TICK REAL > Resources` (`1,899/1,899`), with the post-apply dry-run idempotent and `guardOk=true`.

## 2026-05-23 - C1-CONFIG1 RETEST 1 Closeout And TICK REAL Opened

- Closes Phase 4 `RETEST 1` formally in the local task-config ledger, keeping the protected Dukascopy/OOS2 passive retest with all previously applied guards green.
- Opens Phase 5 `TICK REAL` and maps it to `AutomaticRetest-Task2.xml`, generating the full local questionnaire with `13` tabs, `19,991` entries, `12,334` donor/base differences and `0` duplicate question IDs.
- Documents the first critical Phase 5 decision before applying changes: current base databanks are `Input=RETEST 0` / `Output=retest 1`, while the updated donor/methodology flow points to `Input=retest 1` / `Output=TICK`.
- At opening time, leaves `TICK REAL` base/template untouched until `Data` / `Databanks` / `Resources` are confirmed with the operator.

## 2026-05-23 - C1-CONFIG1 RETEST 1 Static/CrossChecks Gate

- Adds `retest1-static-crosschecks-target` to close Phase 4 static tabs and CrossChecks with dry-run-first backup/diff/apply.
- Keeps `RETEST 1` as pure OOS2 validation: CrossChecks parent is off, every direct crosscheck is off and every internal `Settings/Methods/Method` is off.
- Aligns `RiskMoneyManagement` with `RETEST 0` and the other Capa1 retests by switching to `FixedSize=true` and `FixedAmount=false`, while keeping ATMs disabled, Notes unchanged and SelectedStrategies empty.
- Records local ledger answers for `CrossChecks` (`339/339`), `RiskMoneyManagement` (`25/25`), `ATMs` (`9/9`), `Notes` (`1/1`) and `SelectedStrategies` (`0/0`).

## 2026-05-23 - C1-CONFIG1 RETEST 1 Passive Generation Gate

- Adds `retest1-passive-generation-target` to close Phase 4 `PartsToImprove` / `WhatToBuild` / `Blocks` with dry-run-first backup/diff/apply.
- Turns `RETEST 1` into a passive pure retest: all improvement toggles are off, `StrategyType.improveDatabank=RETEST 0`, evolution/fresh-blood UI toggles are disabled and no unknown SQX enum is invented for `BuildMode.generationType`.
- Normalizes `Blocks` from the approved `RETEST 0` internal contract, not Mining15 donor: Signals and Stop/Limit remain off, methodology indicators stay available, `EnterAtMarket` is the only entry and `ExitAfterBars` is the only active exit at `100`.
- Records local ledger answers for `PartsToImprove` (`9/9`), `WhatToBuild` (`67/67`) and `Blocks` (`17,583/17,583`).

## 2026-05-23 - C1-CONFIG1 RETEST 1 Options/Databanks/Rankings

- Adds `retest1-options-databanks-rankings-target` to close the next Phase 4 block with dry-run-first backup/diff/apply.
- Keeps `RETEST 1` advisory without becoming a pass-through: `DeleteFailedStrategies=false` preserves failed rows for analysis, while active filters remain `NumberOfTrades >= 100`, `RExpectancy > 0.05` and `NetProfit >= 0`.
- Sets `RealisticGapsHandling=true` so protected OOS2/cross-broker validation is not softer than `RETEST 0`, while keeping the time window generator-owned by timeframe.
- Keeps the passive databank chain `Input=RETEST 0` and `Output=retest 1`, and disables `FitPortfolio` because Capa1 RETEST 1 is validation, not portfolio selection.
- Records local ledger answers for `Options` (`34/34`), `Databanks` (`3/3`) and `Rankings` (`40/40`).

## 2026-05-23 - C1-CONFIG1 RETEST 1 Data/Resources

- Converts the operator decision into Phase 4 policy: `RETEST 1` is a passive clone of `RETEST 0` plus a protected Dukascopy/OOS2 override, not a wholesale Mining15 donor copy.
- Adds `retest1-data-resources-target` to the SQX142 task config gate with dry-run-first backup/diff/apply, local `data.db` evidence, compact Dukascopy Resources rebuild and guards against donor/base leakage.
- Applies the target to local Capa1 base and `backend/sqx-edge-tool/templates/Capa1_Long.cfx`: `Retest-Task1.xml` now uses `2010.01.01-2017.10.02`, `AUDCAD_dukascopy`, source `2`, broker `3`, `testPrecision=2`, no nested OOS ranges, no resource sessions and no embedded `CustomBlocks`.
- Normalizes disabled internal crosscheck `Setup/Chart` references in `Retest-Task1.xml` to the same Dukascopy placeholder so SQX142 resource checks do not see stale Darwinex symbols.
- Records full local ledger answers for `RETEST 1 > Data` (`8/8`) and `RETEST 1 > Resources` (`12/12`), then points the next Phase 4 block to `Options` / `Databanks` / `Rankings`.

## 2026-05-23 - C1-CONFIG1 RETEST 1 Opened

- Opens Phase 4 `RETEST 1` and maps it to `Retest-Task1.xml`, generating the local questionnaire with `13` tabs, `20,024` questions, `12,343` donor/base differences and no duplicate question IDs.
- Documents the key structural differences versus `RETEST 0`: no `Optimization` section, protected OOS2/Dukascopy role, heavy `Resources` divergence and `PartsToImprove`/`Blocks` shape that may imply exit improvement rather than passive retest.
- Leaves decisions open for operator debate before recording bulk answers or mutating local base/template files.

## 2026-05-23 - C1-CONFIG1 RETEST 0 Closeout

- Closes `RETEST 0 > Blocks` with the operator-confirmed decision to keep the full base configuration: no new strategy generation, `Signals` and `Stop/Limit` inactive, `Indicators` governed by methodology/BlockSettings, and `EnterAtMarket` plus `ExitAfterBars` only.
- Records `17,583/17,583` `Blocks` answers in the ignored local task-config ledger and creates the Phase 3 local closeout report pointing to Phase 4 `RETEST 1`.
- Documents that no donor `Blocks` are copied because Mining15 carries a volatility-specific universe that does not add value to the first OOS retest gate.

## 2026-05-23 - C1-CONFIG1 Bulk Tab Answer Guard

- Adds `record-tab-answer` to the SQX142 task config gate so very large tabs can be answered atomically from the latest questionnaire instead of spawning thousands of individual calls.
- The command refuses questionnaires with duplicate question IDs and supports intentional empty tabs, protecting `RETEST 0 > Blocks` and later large retest tabs from ledger collapse.
- Regenerates `RETEST 0 > Blocks` with the fixed question ID scheme: `17,583` unique questions, `8,331` differences and no duplicate IDs before the operator's final Blocks decision.

## 2026-05-23 - C1-CONFIG1 RETEST 0 Generator Guard

- Opens `RETEST 0` as the first real Capa1 OOS gate and documents that it runs full IS+OOS1 with OOS1 marked, not OOS-only isolation.
- Makes Project Generator fallback commissions explicit as neutral `SizeBased=0.0` so generated tasks do not inherit accidental donor/base commission state when `data.db` is unavailable.
- Adds template compatibility coverage proving generated `Retest-Task3.xml` keeps `2017.10.02-2025.01.01`, marks OOS1 `2023.01.01-2025.01.01`, and receives generated chart/spread/swap/commission/resources.
- Fixes long questionnaire IDs so repeated CrossChecks conditions keep unique answer keys instead of colliding after slug truncation.

## 2026-05-23 - SQX142-BRANDING1 Etiqueta Visual Local Antes De RETEST 0

- Adds a local-only SQX 142 footer branding patch so SQUANT displays `Build: 142.2336 Codex` while the technical appVersion remains `142.2336`.
- Hides About modal private license/identity lines visually and replaces them with `Optimized and Controlled by Codex 3.0 & QxPro for Edge Suite v1.0`.
- Patches only local web UI/template files, with no binary, engine, license, strategy XML or backend version mutation.
- Records private backup, post-patch hash, cache refresh, footer smoke and About privacy smoke evidence under ignored `.local/sqx142_branding/`.
- Archives only volatile Electron cache folders before the second smoke and confirms SQX closes with no leftover `StrategyQuantX*` processes.

## 2026-05-23 - G8-SQX-AGENT-SKILLS1 Guardianes Antes De RETEST 0

- Updates local Codex skills `sqx-edge-suite-governance` and `sqx142-local-intelligence` with C1-CONFIG1, SQX142-PERF1, Live Guard, handoffs, subagent use and no-mutation limits.
- Adds local skills `sqx-test-guardian` and `sqx-docs-curator` for verification matrix selection, docs consistency, manifest drift and public/private boundary review.
- Adds local AI profiles/actions for `sqx-c1-config`, `sqx-test-guardian`, `sqx-docs-curator` and `sqx-agent-skills`, all read-only and hidden from remote testers.
- Adds `.local/agent_handoffs/` as ignored local handoff root for subagent summaries without prompts, secrets or private evidence.
- Updates governance, the Local AI roadmap, the C1 custom task roadmap and docs consistency manifest so G8 sits between Build closure and `RETEST 0`.
- Adds backend tests proving guardian profiles/capabilities load locally and remain excluded from remote tester capabilities.

## 2026-05-23 - C1-CONFIG1 Capa1 Custom Task Config Gate

- Adds `docs/SQX142_CUSTOM_TASK_CONFIG_ROADMAP.md` as the master roadmap for interactive Capa1 base task configuration.
- Adds `tools/sqx142_task_config_gate.ps1` and `backend/sqx-edge-tool/tools/sqx142_task_config_gate.py` with dry-run-first status, preflight, semantic diff, questionnaire, answer recording and phase-report commands.
- Creates the ignored local ledger shape under `.local/sqx142_task_config/` for full answers, snapshots, diffs, questionnaires and phase reports.
- Records Phase 0 preflight against `Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1`, `Capa1_Long_SQX142_Base` and `backend/sqx-edge-tool/templates/Capa1_Long.cfx` without touching SQX base files.
- Keeps donor promotion selective and normalized: no direct symbol/timeframe/project-name/active-flag/result-state promotion, and `Synthetic`/`Syntetic` is normalized as a historical task alias.
- Updates questionnaires to save every detected tab entry by default; console output is compact when writing, while `--full-output` can print the complete question set.
- Applies Phase 1 view promotion to local `Capa1_Long_SQX142_Base` and repo `Capa1_Long.cfx`, changing only allowlisted databank view assignments and recording local backups/evidence.
- Starts Phase 2 Build Capa1 questionnaires with `task-questionnaires`, preserving duplicate XML paths with stable indexes so repeated entries are not collapsed.
- Adds `build-genetic-target` to apply the confirmed Build Genetic Options target with dry-run, backup and idempotence checks; promotes the values to local Capa1 base and `Capa1_Long.cfx` while leaving `MarketSides` dynamic by generator.
- Adds `build-ranking-target` to apply the accepted Build Ranking recommendation (`MaxStrategies=2000`, `passedStrategies=500`) with dry-run, backup and idempotence checks.
- Adds a Capa1 generator regression guard proving `MarketSides` is patched to `long`, `short` or `both` across every generated task XML instead of inheriting the base template side.
- Cleans legacy BuildMode nodes no longer read by SQX 142/143 genetic options UI, keeping `Conditions` and `EvoRestartOnStagnation` as the source of truth.
- Closes the structural `What to build` block by keeping base `StrategyType`, `RulesComplexity`, SL/PT options and entry/exit symmetry while preserving generator-owned `MarketSides`.
- Adds `build-blocks-target` and `archive-exit-day-snippets` to enforce the Building Blocks rules: market entry only, `ExitAfterBars` only, no day-based exits, no external custom data, `Signals`/`StopLimitBlocks` disabled, and `Indicators` preserved for methodology/BlockSettings; user-level `ExitAfterDays` snippets are archived reversibly.
- Adds `build-indicators-target` so Capa1 base `BuildingBlocks` can be reconciled from the resolved real `.sqb` BlockSetting source (`BS_Volatilidad_v6` for the H4 placeholder) while generated customs keep resolving by user-selected family/timeframe.
- Adds `build-data-target` to guard Build Capa1 Data without donor leakage: `BUILD_C1` dates, `testPrecision=2` simulated data, `No Session`, no Build OOS ranges, and generator-owned charts/spreads/swaps.
- Adds `build-resources-target` to guard Build Capa1 Resources: no donor `USDJPY` leakage, no resource sessions, chart/resource symbol consistency, `precision=TICK` as source-data metadata, and generator-owned broker/symbol rebuilds.
- Adds `build-crosschecks-target` to keep Build Capa1 mining lightweight: only `SequentialOptimization` active, with MonteCarlo/WhatIf/HigherPrecision/additional markets/WFO disabled and no donor crosscheck promotion.
- Adds `build-static-tabs-target` to close the confirmed keep-as-is Build tabs by hash/audit: Options, ATMs, PartsToImprove, RiskMoneyManagement, Databanks, Notes and Optimization.

## 2026-05-22 - SQX142-PERF1 Local Performance Gate

- Adds `docs/SQX142_PERFORMANCE_ROADMAP.md` as the master plan for SQX 142 performance work with `qualityReductionAllowed: false`.
- Adds local measurement and smoke tooling via `/api/sqx142/performance/status`, `backend/sqx-edge-tool/core/sqx_performance.py`, `backend/sqx-edge-tool/tools/sqx142_performance_gate.py` and `tools/sqx142_performance_gate.ps1`.
- Creates lightweight SQX 142 review views for mining/retest/final decision and keeps Monkey/Synthetic MonteCarlo views separated.
- Extends the local-only operator monitor and the local AI agent with SQX 142 performance status while remote tester sessions remain blind to local paths, disk and monitor state.
- Adds JVM profile comparison with automatic restore, atomic config writes and runtime config corruption detection after a power-loss interruption exposed a nulled `CodeEditor.config`.
- Validates `baseline_143_safe`, `diagnostic_low_risk`, `retest_robust` and `mining_fast_safe` with real SQX start/close smokes, no `hs_err_pid*.log` and no leftover processes.
- Adds real-project Monkey/Synthetic databank snapshots from `.sqx` files, validates natural passed/failed filter results and updates the project `.cfx` to use the dedicated MC views with backup.
- Adds a guided MC smoke session and snapshot diff so real Monkey/Synthetic reruns can be compared before/after without touching filters or forcing pass status.
- Records a successful real SQX 142 Monkey/Synthetic smoke: updated databank timestamps, unchanged methods/simulations, stable natural passed/failed counts and no JVM crash log.
- Restores the baseline JVM profile after the smoke, tolerates SQX config line reordering in profile detection and adds project log duration summaries for retest scheduling decisions.
- Adds reversible old-log archiving for SQX 142, keeping today/yesterday logs and zipping verified older logs before removing originals.
- Adds a retest queue planner and dry-run project cloner so MC/Monkey/Synthetic/SPP/WFM scheduling can be measured on controlled `_PERFQ_*` copies before touching the master project.
- Adds `prepare-queue-step` to activate a single queued task, apply the recommended JVM profile and launch SQX for controlled smoke runs; fixes Windows ZIP replacement order for `project.cfx`.
- Records the first controlled `_PERFQ_*` queue smoke: MC completed in `2 min. 31 s.` with `83 passed / 3 failed`, MC 2 completed in `4 min. 17 s.` with `0 passed / 86 failed`, and Sequential is isolated for a dedicated timeout/progress smoke after partial output and an unresponsive local stop.
- Adds `sqx-local-api`, a local-only dry-run wrapper for the SQX Task Manager API (`probe`, `activate-task`, `start-project`, `stop-project`) so future smokes can be driven without Electron clicks.
- Adds `api-auth-smoke` and `sequential-smoke` with full evidence, session cookies, browser-like headers, hidden BrowserToken fallback, baseline restore and process cleanup.
- Resolves the SQX local API `Remote access disabled` blocker by sending the local Chromium-style `browserToken` header without exposing the token; `api_auth_smoke_20260522_205359.json` validates `Access granted` and clean shutdown.
- Hardens `sequential-smoke` so API automation and methodology progress are separate signals; `sequential_smoke_20260522_211255.json` proves `start-project`/`stop-project` now work, while Sequential remains isolated because it completes with `0 total` and no databank update.
- Adds a pre-launch Sequential input guard: when the input databank has zero passed candidates, the smoke skips SQX launch as `no_input_candidates`; `sequential_smoke_20260522_211636.json` documents `MC2` with 86 files and 0 passed.
- Extends the retest queue planner with input candidate diagnostics and `blockedByNoPassedInput`; `retest_queue_plan_20260522_211803.json` marks Sequential as blocked before launch because MC2 has 0 passed / 86 failed.
- Adds `project-retest-next-step`, a dry recommendation layer that separates blocked tasks, measured retests, next heavy experiment and lower-cost alternative; `retest_next_step_20260522_212528.json` points to SPP as next heavy and FOWARD as the cheap smoke option.
- Applies the operator decision to omit SPP and FOWARD from tests/optimization, blocks WFM because it depends on omitted SPP output, and refocuses the next-step recommendation on the MC2/Sequential blocker (`retest_next_step_20260522_213847.json`).
- Adds spread-stress diagnostics for MonteCarlo retests; MC2 is flagged as `spread_stress_extreme_vs_base` because `RandomizeSpread` uses 30-50 against base spread 1.4, matching the likely cause of 0 passed / 86 failed.
- Adds `mc2-spread-diagnostic` and `create-mc2-spread-variant`; creates a clean `_PERFQ_MC2SPREAD_*` clone with MC2 spread changed to 2.8-7.0 and old MC2/Sequential outputs archived for a controlled smoke.
- Hardens `queue-task-smoke` to start like the SQX UI by sending `projectXML`, `taskXMLFile` and `taskXML`, waiting for initial databank load settle, archiving prior output reversibly, and starting the stall timer only after `Project execution started`.
- Records the controlled MC2 spread variant smoke: `queue_task_smoke_20260522_223328.json` generated 86 MC2 outputs in `5 min. 5 s.` with natural `84 passed / 2 failed`, confirming that 2.8-7.0 is a viable diagnostic range versus the original 30-50 stress.
- Adds live `ProgressEngine` activity detection to `queue-task-smoke` after the Sequential diagnostic showed active optimization in SQX logs without databank output; this prevents false "stalled" classification for long-running retests that only write results at completion.
- Adds `create-sequential-diagnostic-variant` and validates Sequential on `_PERFQ_SEQDIAG_20260522_230211`: 8 MC2 passed candidates completed in `4 min. 50 s.`, produced 8 Sequential outputs, `8 passed / 0 failed`, no leftover processes and baseline restore. Sequential is now classified as scale/cost-sensitive, not functionally broken.
- Validates the intermediate Sequential batch `_PERFQ_SEQDIAG_20260522_231548`: 24 MC2 passed candidates completed in `12 min. 57 s.`, produced 24 Sequential outputs, `24 passed / 0 failed`, `28 s.` per strategy, no leftover processes and baseline restore; this supports a 24-candidate batching plan before running all 84 survivors.
- Adds `create-sequential-batch-plan` and `sequential-batch-merge-review`; creates the real 84-candidate Sequential queue as `24+24+24+12` across four non-overlapping `_PERFQ_SEQBATCH_*` clones and validates initial merge coverage with `sequential_batch_merge_review_20260522_234321.json`.
- Runs Sequential batch B01/B02: B01 produced 24 outputs and exposed a smoke classification gap, then `queue-task-smoke` was fixed to complete by output coverage; B02 validates the fix with `queue_task_smoke_20260523_012052.json` (`ok=true`, 24/24 outputs). Merge review now reports `48/84` produced, `36` pending, zero duplicates and zero unexpected outputs.
- Completes Sequential batch B03/B04 and final merge review: B03 produced 24/24, B04 produced 12/12, and `sequential_batch_merge_review_20260523_063406.json` validates `84/84` produced, zero missing, zero unexpected and zero duplicates. Outputs are copied only to `.local/sqx142_performance/sequential_merge_reviews/` for inspection; the master project remains untouched.
- Adds `sequential-final-review` to audit copied Sequential `.sqx` files as ZIPs; `sequential_final_review_20260523_071458.json` confirms 84/84 readable outputs, 84 `SequentialOptimization_Results.xml` passed, zero invalid files, 569 stable areas and writes a local CSV for parameter-level inspection under `.local/sqx142_performance/sequential_final_reviews/`.
- Adds guarded MC2 spread promotion tooling: `promote-mc2-spread-to-base` derives the range from the selected asset spread using the adaptive default `baseSpread x2-x5`, validates the final Sequential evidence, shows the XML diff, requires explicit methodology/apply flags, records a backup and pairs with `rollback-mc2-spread-promotion`. Dry-run `mc2_spread_promotion_20260523_072103.json` resolves USDJPY base spread `1.4` into `2.8-7.0` and plans `Min 30 -> 2.8`, `Max 50 -> 7`.
- Promotes MC2 on the Capa1 base with backup evidence `mc2_spread_promotion_20260523_072626.json`, changing only `RandomizeSpread` from `30-50` to adaptive `baseSpread x2-x5` (`2.8-7.0` for USDJPY/H4). Post-promotion clone smokes validate `MC` 81/5 in `2 min. 17 s.`, `MC 2` 84/2 in `5 min. 46 s.` and Sequential 8/8 in `4 min. 52 s.`; `queue-task-smoke` now defaults to 180 s start settle to avoid starting SQX before large databanks finish loading.
- Adds `performance-clone-hygiene` and archives eight old `_PERFQ_*` projects reversibly to `SQX_142_Crack_local_backups/archived_perf_projects`; only the two post-promotion smoke clones remain active in SQX `user/projects`, reducing active project footprint from about 3.1 GB to 919.5 MB without deleting evidence or backups.
- Adds `restore-performance-clone` for selective, dry-run-first recovery of one archived `_PERFQ_*` clone back to SQX `user/projects`, with SQX-process blocking, duplicate-name protection and optional active-clone archiving before restore.
- Adds `performance-closeout-report`, a local evidence report that summarizes performance status, active/archive clones, key smokes and the deferred operator question required before configuring individual Capa1/Capa2 custom task values.
- Adds `performance-next-action`, a dry recommendation gate that reads status plus key evidence and returns the next PERF1 command instead of relying on memory after long smoke cycles.
- Adds `performance-parallelism-advisor` for PERF1 Phase 7, capturing host resources, relevant SQX settings, validated smoke timings and conservative concurrency profiles before any worker/thread tuning.
- Adds `project-mining-pipeline-advisor` for PERF1 Phase 3, reading Build task structure, databanks, ranking goals, acceptance conditions, block universe and efficiency risks before proposing a clone-only mining smoke.
- Adds and applies `phase5-databank-view-guard` for PERF1 Phase 5, reassigning project databanks to light/specialized views and archiving legacy heavy views (`todas las metricas posibles`, `PROPIA`, `MONTECARLO RETEST`, `MONTECARLO TRADES`, `ROBUSTEZ`) with reversible backup.
- Adds PERF1 Phase 9 local intelligence: `/api/sqx142/performance/status` now returns a redacted `intelligence` block with active profile, view coverage, latest evidence, required evidence health and next recommendation; the operator monitor and local agent display it while remote testers remain blind to local state.
- Adds PERF1-LIVEGUARD1: `live-guard` watches recent SQX logs, JVM crash files, SQX local API responsiveness and running processes without changing anything while SQX is open; `--apply` is post-close only and performs reversible safe repairs such as baseline restore/log archiving.
- Formally closes PERF1 with `performance_closeout_report_20260523_095800.json`, `performance_next_action_20260523_095758.json` and clean Live Guard evidence `performance_live_guard_20260523_095802.json`; the next gated decision is the operator approach for individual Capa1/Capa2 base task values.

## 2026-05-22 - SQX142-143-BACKPORT1 Local Compatibility Gate

- Adds `docs/SQX142_143_BACKPORT_LEDGER.md` as the master ledger for SQX 142/143/144 compatibility, with explicit no-bulk-engine/no-license backport boundaries.
- Adds local compatibility diagnostics and maintenance tooling via `/api/sqx142/compat/status`, `backend/sqx-edge-tool/core/sqx_compatibility.py`, `backend/sqx-edge-tool/tools/sqx142_compatibility.py` and `tools/sqx142_compatibility.ps1`.
- Extends the local-only operator monitor with SQX 142 runtime/process status while keeping remote tester sessions blind to local monitor data and local paths.
- Adds an internal agent capability for explaining SQX 142/143/144 compatibility from the ledger without executing changes.

## 2026-05-22 - SQX142-TRANSLATOR1 Electron Cache Hardening

- Records that SQX 142 does not reliably expose the build 144 Source Code Translator as a standalone `user/extend/ResultsPlugins` Result Plugin; the validated integration point is the native `Source Code` result tab.
- Adds a safe Electron cache refresh runbook/script for the case where `localhost:8080` serves new SQX bundles but the local app still shows stale UI.
- Hardens the local Ollama translator smoke path with a translation-specific model, bounded generation and markdown-fence cleanup so the plugin returns usable code instead of timing out.

## 2026-05-21 - REMOTE-AI-TESTER1 Authenticated Tester AI Pilot

- Enables the Edge Factory AI dock for authenticated remote sessions with active `tester_free`, paid or internal entitlement, using a tester-safe capability subset only.
- Keeps the server monitor local-only for the creator/operator and adds Backend/Tunnel/Ollama readiness: pressing `Arrancar` now triggers `/api/agent/status` so Flask autostarts/checks Ollama before the monitor reports tester-ready.
- Blocks remote access to local inbox, mark-step/write actions, server monitor state, local paths, raw emails, protected URLs, grants, checkout, Cloudflare and commercial automation.

## 2026-05-21 - LOCAL-AI1 Local Operator Agent

- Adds a local AI agent layer backed by Ollama, with Flask-mediated `/api/agent/*` endpoints, structured recommendations, allowlisted execution and confirmation tokens.
- Adds the Edge Factory Agent Dock and Control Panel summary without adding a primary navigation tab.
- Adds `.local/agent_inbox/` as ignored local inbox plus docs/tests for redaction, policy, remote blocking and no prompt/history persistence.
- Adds deterministic capabilities help and best-effort Ollama autostart/status reporting so the operator does not need to manually start the model server first.
- Adds a local SQX 142 Source Code Translator bridge: `/api/agent/translate-source-code` mediates Ollama translation/fix requests, and `tools/build_sqx142_source_translator.py` rebuilds the 144 `.sxp` without external OpenAI calls or API-key storage.

## 2026-05-21 - WFCO-ACCEPT1 Edge Factory Basic/Advanced Polish

- Adds `Modo básico` / `Modo avanzado` to Edge Factory. Basic is now the default buyer/tester route with one primary action per stage; Advanced explicitly unlocks internal tools, manual checks and custom libre.
- Persists the experience mode in `sqx_edge_factory_state_v1` without touching Project Generator, Template Maker, Portfolio Lab, downloads, workspace persistence or remote gates.
- Clarifies the primary shell copy around browser-download `.cfx` files and SQX target profiles (`SQ default / configurable`).

## 2026-05-21 - CFX-RILIS-TARGET1 SQ Default Exact-Symbol Target

- Changes Project Generator's default user-download target profile to `SQ default / símbolo exacto`, generating primary `.cfx` resources as `{asset}` without the Darwinex suffix for testers whose SQX Data Manager uses `Broker profile = SQ default`.
- Keeps `SQX Edge / Darwinex` available as a server/operator profile, and keeps `Broker del usuario` for explicit broker/source remaps when a recipient has a custom local SQX profile.
- Preserves Retest 1/OOS2 on Dukascopy 2010.01.01-2017.10.02 as a methodology rule, separate from the recipient's primary broker profile.
- Aligns `SQ default` with SQX 142's no-broker/default shape (`broker=-1`) instead of a real broker row `0`, avoiding `BrokerDto.getName()` null errors on recipient machines.

## 2026-05-21 - TM-PERF2 Template Maker Worker Ingestion

- Adds a local Template Maker Web Worker path for CSV parsing, `.sqx` ZIP unpacking, SHA-256 hashing, XML extraction and diversity clustering cache warmup, with safe fallback when Worker execution is unavailable.
- Keeps `SQX.templateMaker` as the public API owner for certification, final diversity accessors, C2 generation, Exit Policy, traceability and remote workspace persistence.
- Adds visible per-file progress during Template Maker ingestion so large batches no longer feel frozen while parsing starts.

## 2026-05-21 - WFCO5 Visual Polish And Desktop QA

- Completes WFCO-5: Edge Factory now has a desktop command strip for Hipotesis, Capa 1, Template C2 and Portfolio plus a compact status stack for guided mode, browser downloads and advanced override.
- Tightens the visual hierarchy of the main PC workflow with clearer current/completed stage states and denser public-safe traceability signals.
- Adds the Edge Factory Desktop QA Gate and moves the parallel UX recommendation to a short acceptance pass or CFX-METHOD2 when the Capa 2 base v2 arrives, while REMOTE-RILIS-STANDBY remains independent.

## 2026-05-21 - WFCO4 Portfolio Lab MVP

- Completes WFCO-4: Portfolio Lab now imports/pastes Capa 2 CSV, supports common SQX column aliases and decimal comma/punto, scores candidates and classifies them as `portfolio`, `similar` or `review`.
- Adds tunable similarity, max winners and max-per-asset settings, plus browser downloads for shortlist CSV and full JSON report.
- Adds the Portfolio Lab Decision Gate and moves the next UX recommendation to WFCO-5 Visual Polish And Desktop QA, while REMOTE-RILIS-STANDBY remains independent.

## 2026-05-21 - WFCO3 Content Overhaul

- Completes WFCO-3: Edge Factory copy now guides by action, output and pending state instead of presenting the user with tab-heavy technical wording.
- Updates the main route labels to `Punto de partida`, `Elegir edge`, `Generar Capa 1`, `Certificar Capa 1`, `Crear Template C2`, `Generar Capa 2`, `Revisar Capa 2` and `Portfolio`.
- Adds the Edge Factory Content Gate to governance and moves the parallel UX recommendation to WFCO-4 Portfolio Lab MVP, while REMOTE-RILIS-STANDBY remains the independent remote blocker.

## 2026-05-21 - WFCO2 Methodology Handoffs

- Records WFCO-2 as completed: Edge Factory now receives public-safe handoff context from Activos, Plan Mining, Project Generator, Template Maker and Portfolio Lab.
- Adds stage context strips so the user can see selected card/mining, Capa 1 output, Capa 1 analysis, C2 template, Capa 2 output and portfolio shortlist status from the main pipeline.
- Keeps REMOTE-RILIS-STANDBY as the active remote blocker and moves the parallel UX recommendation to WFCO-3 Content Overhaul.

## 2026-05-20 - Current Docs State Sync

- Synchronizes README, public roadmap, project governance and UX-NAV plan with the current REMOTE-RILIS-STANDBY state.
- Records the Project Generator remote-session redirect fix as applied and keeps TESTER-RILIS retest pending before any REMOTE-8G decision review resumes.
- Aligns UX-NAV docs around no active tab after UX-WF2 acceptance until the operator defines the next scope.
- Adds a persistent state consistency manifest and pytest guard to catch future stale phase, next-action, roadmap-date or UX active-scope drift across docs.

## 2026-05-12 - TL1d Worker Entry Rescue Shell

- Adds a Cloudflare Worker entry wrapper that serves the tester login, portal, logout, health and feature-check flow before the unstable Next/OpenNext runtime path.
- Keeps Cloudflare Access as the external gate and preserves the OpenNext worker fallback for non-rescue routes.
- Keeps tester URL, tester emails, provider IDs, secrets and private evidence outside Git.

## 2026-05-12 - TL1c Cloudflare Middleware Stability Hotfix

- Removes the global Next middleware from the Cloudflare/OpenNext tester portal path after authenticated Access traffic returned a runtime 500.
- Moves browser security headers to `next.config.mjs` and keeps route-level session redirects on `/portal` and `/admin/testers`.
- Keeps Cloudflare Access as the external protected gate and preserves the no-leak tester launch proof boundary.

## 2026-05-12 - TL1b Workers.dev Protected Target Fix

- Enables the committed Cloudflare `workers_dev` target for the protected tester portal after the hotfix deployment exposed a version with no public target.
- Keeps `preview_urls=false`, no custom routes committed and no tester URL, emails, credentials, provider IDs or private evidence in Git.
- Updates the TL1 proof to treat `workers_dev=true` as the protected final tester target instead of the earlier safe default.

## 2026-05-12 - TL1a Tester Portal Runtime Env Hotfix

- Adds a safe runtime env reader for the Cloudflare/OpenNext tester portal.
- Removes direct runtime `process.env` reads from middleware-adjacent auth, entitlement, renewal, admin, cron and security helpers.
- Keeps TL1 proof green and avoids leaking tester URLs, emails, credentials, provider IDs or private evidence.

## 2026-05-11 - TL1 Tester Launch Candidate

- Freezes the tiny T10 tester gates as historical safety work and adds one macro tester launch candidate decision.
- Adds `proof:tester-launch-candidate`, returning `NO_GO_TESTER_LAUNCH_PRIVATE_EVIDENCE_MISSING` until ignored private launch evidence exists.
- Adds `GO_TESTER_LAUNCH_CANDIDATE_READY_NO_GIT_LEAK` as the single launch-readiness result for protected Access, tester auth smoke, blocked states, support, rollback and operator approval.
- Keeps tester URL, tester emails, credentials, provider IDs, screenshots, raw feedback and private notes outside Git.

## 2026-05-11 - T10bc Private Tester Next Iteration Gate

- Adds `proof:tester-next-iteration-gate` with guarded `NO_GO_PRIVATE_TESTER_NEXT_ITERATION_EVIDENCE_MISSING` until ignored local next-iteration evidence exists.
- Adds `GO_PRIVATE_TESTER_NEXT_ITERATION_READY_NO_GIT_LEAK` for a private next-iteration plan: repeat validation, execute fixes, expand micro-cohort, pause tester access, prepare next tester cycle or escalate commercial readiness.
- Documents the private next-iteration boundary after T10bb iteration decision, keeping URLs, emails, credentials, raw feedback, private action details, private execution notes, private result notes, private decision notes, private iteration plans, private support notes, screenshots and provider IDs out of Git.
- Updates governance, roadmap, README and static contracts for the next `T10bd` next-iteration execution gate.

## 2026-05-11 - T10bb Private Tester Iteration Decision Gate

- Adds `proof:tester-iteration-decision-gate` with guarded `NO_GO_PRIVATE_TESTER_ITERATION_DECISION_EVIDENCE_MISSING` until ignored local iteration-decision evidence exists.
- Adds `GO_PRIVATE_TESTER_ITERATION_DECISION_READY_NO_GIT_LEAK` for a private next-move decision: repeat validation, execute fixes, expand micro-cohort, pause tester access, prepare next tester cycle or escalate commercial readiness.
- Documents the private iteration-decision boundary after T10ba result validation, keeping URLs, emails, credentials, raw feedback, private action details, private execution notes, private result notes, private decision notes, screenshots and provider IDs out of Git.
- Updates governance, roadmap, README and static contracts for the next `T10bc` next-iteration gate.

## 2026-05-11 - T10ba Private Tester Result Validation Gate

- Adds `proof:tester-result-validation-gate` with guarded `NO_GO_PRIVATE_TESTER_RESULT_VALIDATION_EVIDENCE_MISSING` until ignored local result-validation evidence exists.
- Adds `GO_PRIVATE_TESTER_RESULT_VALIDATION_READY_NO_GIT_LEAK` for private classification of accepted, repeat, blocked and deferred tester results.
- Documents the private result-validation boundary after T10az action execution, keeping URLs, emails, credentials, raw feedback, private action details, private execution notes, private result notes, screenshots and provider IDs out of Git.
- Updates governance, roadmap, README and static contracts for the next `T10bb` iteration-decision gate.

## 2026-05-11 - T10az Private Tester Action Execution Gate

- Adds `proof:tester-action-execution-gate` with guarded `NO_GO_PRIVATE_TESTER_ACTION_EXECUTION_EVIDENCE_MISSING` until ignored local execution evidence exists.
- Adds `GO_PRIVATE_TESTER_ACTION_EXECUTION_READY_NO_GIT_LEAK` for private action execution evidence with owners, acceptance evidence and rollback-risk review.
- Documents the private execution boundary after T10ay action plan, keeping URLs, emails, credentials, raw feedback, private action details, private execution notes, screenshots and provider IDs out of Git.
- Updates governance, roadmap, README and static contracts for the next `T10ba` result-validation gate.

## 2026-05-11 - T10ay Private Tester Action Plan Gate

- Adds `proof:tester-action-plan-gate` with guarded `NO_GO_PRIVATE_TESTER_ACTION_PLAN_EVIDENCE_MISSING` until ignored local action-plan evidence exists.
- Adds `GO_PRIVATE_TESTER_ACTION_PLAN_READY_NO_GIT_LEAK` for a private prioritized tester action plan with owners, acceptance criteria and release-risk review.
- Documents the private action-plan boundary after T10ax triage, keeping URLs, emails, credentials, raw feedback, private action details, screenshots and provider IDs out of Git.
- Updates governance, roadmap, README and static contracts for the next `T10az` execution gate.

## 2026-05-11 - T10ax Private Tester Feedback Triage Gate

- Adds `proof:tester-feedback-triage-gate` with guarded `NO_GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_EVIDENCE_MISSING` until ignored local triage evidence exists.
- Adds `GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_READY_NO_GIT_LEAK` for private grouping, priority assignment and action-candidate preparation.
- Keeps tester URLs, emails, credentials, provider IDs, screenshots, raw feedback, private bug details and feedback identities outside Git.

## 2026-05-11 - T10aw Private Tester Feedback Intake Gate

- Adds `proof:tester-feedback-intake-gate` with guarded `NO_GO_PRIVATE_TESTER_FEEDBACK_INTAKE_EVIDENCE_MISSING` until ignored local feedback evidence exists.
- Adds `GO_PRIVATE_TESTER_FEEDBACK_INTAKE_READY_NO_GIT_LEAK` for private feedback collection plus public-safe redacted summary boundaries.
- Keeps tester URLs, emails, credentials, provider IDs, screenshots, raw feedback and feedback identities outside Git.

## 2026-05-11 - T10av Private Tester Cohort Expansion Gate

- Adds `proof:tester-cohort-expansion-gate` with guarded `NO_GO_PRIVATE_TESTER_COHORT_EXPANSION_EVIDENCE_MISSING` until ignored local expansion evidence exists.
- Adds `GO_PRIVATE_TESTER_COHORT_EXPANSION_READY_NO_GIT_LEAK` for a controlled 2-10 tester micro-cohort expansion boundary.
- Keeps tester URLs, emails, credentials, provider IDs, screenshots and feedback identities outside Git.

## 2026-05-11 - T10au Private First Tester Smoke Gate

- Adds `proof:tester-first-smoke-gate` with guarded `NO_GO_PRIVATE_FIRST_TESTER_SMOKE_EVIDENCE_MISSING` until ignored local smoke evidence exists.
- Adds `GO_PRIVATE_FIRST_TESTER_SMOKE_PASSED_NO_GIT_LEAK` for a one-tester private smoke result with Access, app login, Pro entitlement, admin-block and logout checks.
- Keeps tester URL, emails, credentials, provider IDs and screenshots outside Git.

## 2026-05-11 - T10at Private Tester URL Share Approval Gate

- Adds `proof:tester-url-share-approval-gate` with guarded `NO_GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_MISSING` until ignored local approval evidence exists.
- Adds `GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_READY_NO_GIT_LEAK` for the private one-to-one URL sharing approval boundary.
- Keeps tester URL publication, automatic emails, credentials and provider IDs outside Git.

## 2026-05-11 - T10as Private Tester Activation Evidence Ingest

- Adds `proof:tester-activation-evidence-ingest` with guarded `NO_GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_MISSING` until ignored local evidence exists.
- Adds `GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_SAFE_NO_GIT_LEAK` for safe private activation evidence without Git URL, email, credential or provider-ID leakage.
- Keeps tester URL sharing blocked for the next private approval gate.

## 2026-05-11 - T10ar Private Tester Account Activation Gate

- Adds `proof:tester-account-activation-gate` with `GO_PRIVATE_TESTER_ACCOUNT_ACTIVATION_GATE_READY_NO_GIT_LEAK`.
- Adds a public-safe activation checklist plus ignored local evidence path for private tester account handling.
- Keeps tester accounts, invites, URL, emails, credentials and provider IDs outside Git until private evidence is ingested.

## 2026-05-11 - T10aq Tester Access Handoff No URL Leak

- Adds `proof:tester-access-handoff` with `GO_TESTER_ACCESS_HANDOFF_READY_NO_PUBLIC_URL_LEAK`.
- Adds a public-safe tester handoff checklist plus ignored local evidence path for operator-only URL handling.
- Keeps tester URL sharing, account creation and tester emails outside Git until a private activation gate.

## 2026-05-11 - T10ap Controlled Workers.dev Publication Result

- Executes the exact approved Cloudflare `workers.dev` publication deploy once.
- Adds `proof:cloudflare-workers-dev-publication-result` with `GO_CONTROLLED_WORKERS_DEV_PUBLICATION_ACCESS_PROTECTED_NO_URL_SHARED`.
- Verifies anonymous Access interception for root, health and portal routes while keeping tester URL sharing and tester account creation blocked.

## 2026-05-11 - T10ao Controlled Workers.dev Publication Preflight

- Adds `proof:cloudflare-controlled-workers-dev-publication-preflight` with `GO_CONTROLLED_WORKERS_DEV_PUBLICATION_PREFLIGHT_READY_EXACT_APPROVAL_REQUIRED`.
- Documents the exact T10ao publication approval phrase, prechecks, one-command deploy boundary, Access smoke and rollback rules.
- Keeps `workers_dev=false`, tester URL sharing and tester account creation blocked until T10ap receives exact approval.

## 2026-05-11 - T10an Protected Tester Publication Target Gate

- Selects protected `workers.dev` plus Cloudflare Access as the first tester publication target.
- Adds `proof:cloudflare-protected-tester-publication-target` with `GO_PROTECTED_TESTER_PUBLICATION_TARGET_SELECTED_EXACT_APPROVAL_REQUIRED`.
- Keeps `workers_dev=false`, tester URL sharing and tester account creation blocked until the next exact-approval gate.

## 2026-05-11 - T10am Controlled Real App Deploy Result

- Executes the exact approved Cloudflare Wrangler deployment attempt for the real OpenNext tester portal.
- Adds `proof:cloudflare-real-app-deploy-result` with `GO_REAL_APP_VERSION_UPLOADED_NO_PUBLIC_TARGET_NO_TESTER_URL`.
- Records that no public target, tester URL, tester accounts or sensitive Cloudflare identifiers were committed.

## 2026-05-10 - T10al Controlled Real App Deploy Gate

- Adds `proof:cloudflare-controlled-real-app-deploy-gate` with `GO_CONTROLLED_REAL_APP_DEPLOY_GATE_READY_EXACT_APPROVAL_REQUIRED`.
- Documents the exact future approval phrase, deploy command, prechecks, post-deploy Access smoke and rollback rules.
- Keeps the real app undeployed and tester URL sharing blocked until a later exact-approval phase.

## 2026-05-10 - T10ak Access Policy Boundary

- Adds `proof:cloudflare-access-policy-boundary` with `GO_ACCESS_APPLICATION_POLICY_BOUNDARY_VERIFIED_NO_APP_DEPLOY`.
- Adds public-safe Access policy boundary evidence template while keeping real boundary data in ignored local evidence only.
- Keeps real app deployment, tester URL sharing and tester account creation blocked until a later controlled deploy gate.

## 2026-05-10 - T10ajo Workers.dev Access Verified

- Verifies that anonymous traffic to the private workers.dev shell is intercepted by Cloudflare Access before the shell body is returned.
- Adds `proof:cloudflare-workers-dev-access` with `GO_ACCESS_PROTECTED_WORKERS_DEV_SHELL_VERIFIED_NO_APP` to require ignored local Access evidence before T10ak can proceed.
- Keeps real app deployment, tester URL sharing and tester account creation blocked while unlocking only the Access app/policy verification gate.

## 2026-05-10 - T10ajn Controlled Workers.dev Shell Deploy

- Deploys only the harmless workers.dev shell target, not the real OpenNext tester portal.
- Adds `proof:cloudflare-workers-dev-shell-deploy` to record shell-created / Access-pending state without committing hostname, account ID, token, tester URL or tester emails.
- Keeps T10ak blocked because Access protection still needs dashboard enablement or an API token with `Access: Apps and Policies Write`.

## 2026-05-10 - T10ajm Workers.dev Shell Gate

- Adds `proof:cloudflare-workers-dev-shell-gate` for the no-domain/no-existing-Worker Cloudflare path.
- Adds a harmless locked shell Worker plus dedicated `wrangler.shell.example.jsonc` so the next approved step can create a target before Access is enabled.
- Keeps the real OpenNext app undeployed, keeps main `wrangler.jsonc` on `workers_dev=false`, and keeps T10ak blocked until shell target and Access protection are verified.

## 2026-05-10 - T10ajl2 Cloudflare Operator Unlock Kit

- Adds `prepare:cloudflare-hostname-zone-selection` to create/review the ignored local evidence file without committing Cloudflare hostname, zone ID, tester URL, tester emails or tokens.
- Hardens `proof:cloudflare-hostname-zone-selection` so local evidence with sensitive keys or values blocks T10ak.
- Adds `docs/T10AJL_OPERATOR_UNLOCK_KIT.md` as the practical operator checklist before Access creation.

## 2026-05-10 - T10ajl Cloudflare Hostname Zone Selection

- Adds the public-safe hostname/zone evidence gate before Cloudflare Access creation.
- Adds `proof:cloudflare-hostname-zone-selection`, which returns `NO_GO_PRIVATE_HOSTNAME_ZONE_EVIDENCE_REQUIRED_T10AK_BLOCKED` until ignored local evidence proves a private hostname/zone or protected workers.dev onboarding.
- Keeps Worker, route, Access, tester URL and tester identities uncreated while documenting the exact evidence needed to unlock T10ak.

## 2026-05-10 - T10ajk Cloudflare Route Access Precreate

- Adds the guarded Cloudflare route/access precreate phase after T10ajj.
- Adds `proof:cloudflare-route-access-precreate` with result `NO_GO_CLOUDFLARE_ROUTE_HOSTNAME_REQUIRED_T10AK_BLOCKED`.
- Records redacted Wrangler authentication plus Worker-not-found checks, keeps `workers_dev=false` and `preview_urls=false`, and blocks Access creation until a private hostname/zone or protected workers.dev onboarding evidence exists.

## 2026-05-10 - T10ajj Cloudflare Route Onboarding Decision

- Adds the no-deploy Cloudflare route/onboarding decision after the first Worker rollback.
- Adds `proof:cloudflare-route-onboarding-decision` with result `GO_CLOUDFLARE_ROUTE_ONBOARDING_DECISION_READY_NO_DEPLOY`.
- Sets `workers_dev=false` and `preview_urls=false` in `wrangler.jsonc` so another deploy cannot accidentally publish a public workers.dev or preview surface before T10ajk chooses and protects the route.

## 2026-05-10 - T10aji Cloudflare First Deploy Rollback

- Executes the first controlled Cloudflare Worker deploy attempt and rolls it back immediately.
- Adds `proof:cloudflare-first-deploy-rollback` with result `NO_GO_FIRST_WORKER_DEPLOY_ROLLED_BACK_WORKERS_DEV_SUBDOMAIN_REQUIRED`.
- Records that Cloudflare requires a workers.dev subdomain or route before publication; no Worker remains, no Access policy was created and no tester URL was shared.

## 2026-05-10 - T10ajh Cloudflare First Deploy Readiness

- Adds a no-deploy readiness phase before the first Cloudflare Worker deploy.
- Adds `proof:cloudflare-first-deploy-readiness` with result `GO_CLOUDFLARE_FIRST_DEPLOY_READY_EXACT_APPROVAL_REQUIRED_NO_PROVIDER_MUTATION`.
- Commits `package-lock.json` for reproducible tester-portal installs, confirms `npm run cf:build`, records read-only Worker-not-found evidence and keeps the first deploy blocked until exact approval.

## 2026-05-10 - T10ajg Cloudflare First Deploy Approval Gate

- Adds the exact approval gate for the first Cloudflare Worker deploy/shell creation.
- Adds `proof:cloudflare-first-deploy-approval-gate` with result `GO_CLOUDFLARE_FIRST_DEPLOY_APPROVAL_GATE_READY_NO_PROVIDER_ACTION`.
- Documents pre-checks, deploy command, post-deploy inspection and cleanup criteria while keeping provider mutation blocked until exact approval.

## 2026-05-10 - T10ajf Cloudflare Shell Creation Decision

- Confirms there is no accepted invisible Cloudflare Worker shell creation path.
- Adds `proof:cloudflare-shell-creation-decision` with result `NO_GO_NO_INVISIBLE_CLOUDFLARE_SHELL_PATH_ACCEPTED`.
- Records the official Cloudflare first-upload constraint: the first Worker creation must use C3 or `wrangler deploy`; `wrangler versions upload` would fail for the first upload.
- Leaves the next phase as an exact approval gate for a first Worker deploy/shell creation, with no tester URL sharing.

## 2026-05-10 - T10aje Cloudflare Read-Only Shell Capture

- Authenticates Wrangler locally and performs read-only checks for `sqx-edge-tester-portal-preview`.
- Adds `proof:cloudflare-readonly-shell-capture` with result `NO_GO_CLOUDFLARE_WORKER_NOT_FOUND_T10AK_BLOCKED`.
- Keeps T10ak blocked because Cloudflare reports the proposed Worker does not exist on the authenticated account.

## 2026-05-10 - T10ajd Cloudflare Shell Evidence Capture Checklist

- Adds the manual/authenticated Cloudflare shell evidence capture checklist before T10ak.
- Adds `proof:cloudflare-shell-evidence-capture` with result `NO_GO_CLOUDFLARE_CAPTURE_PENDING_MANUAL_AUTH_OR_DASHBOARD_EVIDENCE`.
- Keeps Access policy, deployment, tester URL and tester accounts blocked until ignored local evidence passes T10ajc.

## 2026-05-10 - T10ajc Cloudflare Shell Evidence Ingest

- Adds a no-deploy shell evidence ingestion gate for `cloudflare-shell-evidence.local.json`.
- Adds `proof:cloudflare-shell-evidence-ingest` with result `NO_GO_CLOUDFLARE_SHELL_EVIDENCE_MISSING_T10AK_BLOCKED` until real shell evidence exists.
- Keeps T10ak blocked and moves the next action to real manual/authenticated evidence capture.

## 2026-05-10 - T10ajb Cloudflare Auth Handoff

- Adds a safe Cloudflare authentication/manual evidence handoff before any Access policy or deployment.
- Adds `proof:cloudflare-auth-handoff` with result `NO_GO_CLOUDFLARE_AUTH_HANDOFF_PENDING_MANUAL_LOGIN_OR_EVIDENCE`.
- Adds a public-safe `cloudflare-shell-evidence.example.json` and ignores the local evidence file used by T10ajc.

## 2026-05-10 - T10aj Cloudflare Project Shell Gate

- Records Ivan's exact approval to create or verify `sqx-edge-tester-portal-preview` while preserving the no-deploy/no-Access/no-tester boundary.
- Adds `proof:cloudflare-project-shell` with result `NO_GO_CLOUDFLARE_PROJECT_SHELL_NOT_VERIFIED_NO_AUTH_NO_DEPLOY_PATH`.
- Memorizes the remaining T10xx/Txx route: auth/manual shell verification, Access policy, controlled deploy, protected smoke, onboarding packet, tester rollout and monitoring.

## 2026-05-10 - T10ai Cloudflare Provider Project Preflight

- Adds a no-deploy Cloudflare provider-project preflight for the tester portal.
- Adds `proof:cloudflare-provider-project-preflight` with result `GO_CLOUDFLARE_PROVIDER_PROJECT_PREFLIGHT_READY_NO_DEPLOY`.
- Keeps deploy scripts absent and keeps Cloudflare project, Access, Git link, tester URL and tester data as exact-approval-only actions.

## 2026-05-10 - T10ah Next Proxy Migration Gate

- Evaluates the tester portal request gate migration from deprecated `middleware.ts` to `proxy.ts`.
- Blocks the migration because Next.js 16 `proxy.ts` uses Node runtime and OpenNext Cloudflare does not support Node Middleware yet.
- Adds `proof:next-proxy-migration` with result `NO_GO_NEXT_PROXY_MIGRATION_BLOCKED_BY_OPENNEXT_NODE_MIDDLEWARE_UNSUPPORTED`.
- Keeps the Cloudflare route local-only: no provider project, deployment, Access policy, tester URL or tester data.

## 2026-05-10 - T10ag OpenNext Local Smoke

- Runs the OpenNext/Cloudflare local smoke without provider action.
- Confirms native Windows preview starts but returns route 500, while WSL/Linux filesystem smoke returns `/api/health` 200.
- Adds `proof:opennext-local-smoke` with result `GO_OPENNEXT_LOCAL_LINUX_PREVIEW_SMOKE_NO_PROVIDER_ACTION`.

## 2026-05-10 - T10af OpenNext Cloudflare Adapter Package

- Adds the local OpenNext/Cloudflare Workers package shape for the tester portal without provider action.
- Adds `wrangler.jsonc`, `open-next.config.ts`, `.dev.vars.example` and `proof:opennext-cloudflare-adapter`.
- Local proof result: `GO_OPENNEXT_CLOUDFLARE_ADAPTER_LOCAL_PACKAGE_READY_NO_DEPLOY`.
- Keeps Cloudflare deploy absent; next gate is local build/preview smoke only.

## 2026-05-10 - T10ae Cloudflare Runtime Compatibility

- Rejects Cloudflare Pages static export for the current tester portal because middleware and API route handlers are part of the access model.
- Selects the Cloudflare Workers/OpenNext Next.js runtime path for the next local adapter package phase.
- Adds `proof:cloudflare-runtime-compatibility` with result `GO_CLOUDFLARE_WORKERS_OPENNEXT_RUNTIME_SELECTED_NO_PROVIDER_ACTION`.

## 2026-05-10 - T10ad Cloudflare Access Preflight

- Defines the no-deploy Cloudflare Pages plus Access OTP preflight before any provider project, deployment or tester URL.
- Adds a mandatory T10ae runtime compatibility gate because the tester portal uses Next.js route handlers and middleware.
- Adds `proof:cloudflare-access-preflight` with result `GO_CLOUDFLARE_ACCESS_PREFLIGHT_READY_NO_DEPLOY`.

## 2026-05-10 - T10ac Replacement Tester Route Options

- Compares Cloudflare, Netlify, Render, local/private-network and the rejected Vercel route without deployment.
- Selects Cloudflare Pages preview plus Cloudflare Access email OTP as the next protected tester-route candidate.
- Adds `proof:replacement-tester-route-options` with result `GO_CLOUDFLARE_ACCESS_OTP_ROUTE_SELECTED_NO_DEPLOY`.

## 2026-05-10 - T10ab Manual Dashboard Evidence Ingest

- Ingests Ivan's manual Vercel dashboard evidence for `sqx-edge-tester-staging` without deployment or provider mutation.
- Rejects the current Vercel tester route because Git, production branch, auto-alias behavior, correction status and next deployment safety are not visible/proven.
- Adds `proof:manual-dashboard-evidence-ingest` with result `NO_GO_REPLACE_VERCEL_TESTER_ROUTE`.

## 2026-05-10 - T10aa Provider Dashboard Evidence Record

- Records read-only provider/dashboard evidence for `sqx-edge-tester-staging` without deployment or provider mutation.
- Confirms CLI evidence still cannot prove that `tester-preview` cannot map to production target.
- Adds `proof:provider-dashboard-evidence-record` with result `NO_GO_PROVIDER_CANNOT_PROVE_PREVIEW_TARGET`.

## 2026-05-10 - T10z Provider Dashboard Correction Package

- Adds a no-deploy provider/dashboard correction package after T10y paused the Vercel CLI deployment route.
- Defines the manual operator checklist and public-safe evidence format required before another deployment attempt.
- Adds `proof:provider-dashboard-correction-package` with result `GO_PROVIDER_DASHBOARD_CORRECTION_PACKAGE_READY_NO_DEPLOY`.

## 2026-05-10 - T10y No-Deploy Provider Dashboard Decision

- Pauses the Vercel CLI deployment route after default and explicit preview-target attempts both returned production target.
- Selects `provider_dashboard_correction_before_any_deployment` as the next safe route before any new deployment attempt.
- Adds `proof:no-deploy-provider-dashboard-decision` with result `GO_PROVIDER_DASHBOARD_CORRECTION_DECISION_READY_NO_DEPLOY`.

## 2026-05-10 - T10x Explicit Preview Target Rollback

- Executes one explicit `--target=preview` deployment attempt against `sqx-edge-tester-staging`.
- Confirms Vercel still returns `target=production`; the T10b guard blocks the build with exit code 43.
- Removes the failed deployment and adds `proof:explicit-preview-target-rollback` with result `NO_GO_EXPLICIT_PREVIEW_TARGET_RETURNED_PRODUCTION_ROLLBACK_CLEAN`.

## 2026-05-10 - T10w Provider Target Mapping Investigation

- Investigates `sqx-edge-tester-staging` target mapping without another deployment attempt.
- Rejects the default CLI route after T10v returned production target from `tester-preview`.
- Prepares `vercel deploy --target=preview --force --yes --format json` as the only next controlled Vercel route.
- Adds `proof:provider-target-mapping-investigation` with result `NO_GO_DEFAULT_CLI_STAGING_ROUTE_REJECTED_EXPLICIT_PREVIEW_TARGET_PREPARED`.

## 2026-05-10 - T10v Controlled Staging Deploy Rollback

- Executes one controlled staging deployment attempt against `sqx-edge-tester-staging`.
- Confirms Vercel still returns `target=production` from `tester-preview`; the T10b guard blocks the build with exit code 43.
- Removes the failed deployment and adds `proof:controlled-staging-deploy-rollback` with result `NO_GO_STAGING_DEPLOYMENT_TARGET_PRODUCTION_ROLLBACK_CLEAN`.

## 2026-05-10 - T10u Staging Deployment Readiness Gate

- Adds a no-deploy readiness gate before any deployment against `sqx-edge-tester-staging`.
- Confirms branch, local link, protection, zero deployments and zero domains before a controlled deployment attempt.
- Adds `proof:staging-deployment-readiness` with result `GO_STAGING_DEPLOYMENT_READINESS_GATE_NO_DEPLOY`.

## 2026-05-10 - T10t Staging Local Link Configured

- Links the private tester portal working tree to `sqx-edge-tester-staging` through ignored Vercel local metadata only.
- Confirms the staging project still has zero deployments, zero domains and no published tester URL after the local link.
- Adds `proof:staging-local-link` with result `GO_STAGING_LOCAL_LINK_CONFIGURED_NO_DEPLOY`.

## 2026-05-10 - T10s Staging Protection Verified

- Verifies `sqx-edge-tester-staging` has SSO Deployment Protection enabled before any Git link or deployment.
- Confirms Git fork protection is enabled, deployments are zero, domains are empty and no URL is published.
- Adds `proof:staging-protection-verified` with result `GO_STAGING_PROTECTION_VERIFIED_NO_DEPLOY`.

## 2026-05-10 - T10r Fresh Staging Project Created

- Creates and verifies `sqx-edge-tester-staging` as a fresh Vercel project shell without deployment.
- Confirms the new project has no deployments, no domains, no latest deployment and is separate from the rejected route.
- Adds `proof:fresh-staging-project-created` with result `GO_FRESH_STAGING_PROJECT_CREATED_NO_DEPLOY`.

## 2026-05-10 - T10q Fresh Staging Route Access Check

- Records explicit approval for creating or verifying a fresh protected staging route without deployment.
- Verifies read-only Vercel visibility through the connected app and blocks write actions because local CLI/token authentication is unavailable.
- Adds `proof:fresh-staging-route-access-check` with result `NO_GO_FRESH_STAGING_ROUTE_CREATION_BLOCKED_BY_CLI_AUTH`.

## 2026-05-10 - T10p Fresh Staging Route Preflight

- Adds `proof:fresh-staging-route-preflight` as a no-token, no-API, no-project and no-deploy gate for the fresh staging route.
- Documents the exact requirements a future staging route must satisfy before any deployment exists.
- Proof result: `GO_FRESH_STAGING_ROUTE_PREFLIGHT_READY_NO_EXTERNAL_ACTION`.
- Sets T10q as the first exact external-action approval gate for creating or verifying a fresh protected staging route without deployment.

## 2026-05-10 - T10o Replacement Route Contract

- Adds `proof:replacement-route-contract` as a no-token, no-API and no-deploy contract for the replacement route.
- Keeps the current Vercel route rejected for rollout and selects `fresh_staging_route_with_no_deploy_preflight` as the next path.
- Sets T10p as the explicitly approved fresh staging route preflight before any external project creation, deployment or tester URL.

## 2026-05-10 - T10n Vercel Route Decision

- Adds `proof:vercel-route-decision` as a no-deploy decision gate after T10m hardening.
- Records that the current Vercel route remains rejected for rollout because the future deployment target cannot be proven without creating a deployment.
- Sets T10o as replacement route or provider-level proof before any deployment attempt.

## 2026-05-10 - T10m Vercel Config Hardening

- Adds `proof:vercel-config-hardening` with dry-run by default and explicit `T10M_APPLY=1` apply mode.
- Applies only documented Project API settings: `autoAssignCustomDomains = false` and `previewDeploymentsDisabled = false`, without creating a deployment.
- Adds `github.autoAlias = false` to the tester portal Vercel config and sets T10n as the next no-deploy route proof/replacement phase.

## 2026-05-10 - T10l Vercel Route Investigation

- Adds `proof:vercel-route-investigation` as a no-deploy Vercel Project/Environment API investigation.
- Records route-risk signals: missing top-level production branch, empty targets, automatic domain assignment and production fast lane enabled.
- Sets T10m as manual/API correction or alternative no-deploy route proof before any further deployment attempt.

## 2026-05-10 - T10k CLI Default Preview Rollback

- Executes one corrected CLI default preview deployment attempt without `--prod`, `--target` or `--skip-domain`.
- Rolls back immediately because Vercel still returns `target = production`; the T10b guard blocks the build with exit code 43 before publication.
- Adds `proof:vercel-cli-default-preview-rollback` and sets T10l as a no-deploy Vercel route investigation/replacement phase.

## 2026-05-10 - T10j CLI Default Preview Command Rollback

- Executes the single T10i-approved CLI command shape and confirms Vercel rejects `--skip-domain` before creating a preview deployment.
- Adds `proof:vercel-cli-default-preview-command-rollback` to verify the separated project remains deployment-free, domain-free and protected.
- Sets T10k as the corrected inspection phase using `vercel deploy --force --yes --format json` without `--prod`, `--target` or `--skip-domain`.

## 2026-05-10 - T10i CLI Default Preview Route Proof

- Adds `proof:vercel-cli-default-preview-route` as a no-deploy proof for the official CLI default preview route.
- Replaces the failed `--target=preview` route with `vercel deploy --force --yes --format json --skip-domain`, explicitly forbidding `--prod` and `--target`.
- Sets T10j as the single deployment inspection phase: create one preview attempt, inspect `target=preview`, and roll back immediately on mismatch without sharing a URL.

## 2026-05-10 - T10h Protected Preview Deploy Rollback

- Executes one protected preview deployment attempt from the separated project and inspects the target immediately.
- Rolls back immediately because Vercel returns `target = production`; the T10b guard blocks the build with exit code 43 before publication.
- Adds `proof:vercel-protected-preview-rollback` and sets T10i as the required preview-route correction phase before another deployment attempt.

## 2026-05-10 - T10g Linked Preview Project Proof

- Links the private tester portal repository to the separated Vercel preview project without deploying or sharing a URL.
- Adds `proof:vercel-linked-preview-project` to verify Git link, production branch, Deployment Protection, no domains and no latest deployment.
- Sets T10h as the single protected preview deployment inspection phase before any tester URL can be shared.

## 2026-05-10 - T10f Separated Preview Project

- Creates a separated Vercel project for tester preview without deploying, linking Git, adding domains or sharing any URL.
- Adds `proof:vercel-preview-project-separation` to verify the separated project is undeployed, domain-free and different from the legacy unsafe project.
- Sets T10g as the required private Git linking and deployment-protection proof phase before any tester URL can exist.

## 2026-05-10 - T10e Omitted Target Preview Rollback

- Adds `proof:vercel-omitted-target-preview` because Vercel documents omitted `target` as preview behavior.
- Executes one omitted-target API preview attempt and rolls back immediately because Vercel still returns `target = production`.
- Leaves the tester project with no latest deployment, no domains and no shared URL; sets T10f as required project recreation/separation.

## 2026-05-10 - T10d Explicit API Preview Rollback

- Executes one explicit Vercel API preview attempt and inspects the deployment target before any URL is shared.
- Rolls back immediately because Vercel returns `target = production` despite the preview request.
- Leaves the tester project with no latest deployment, no domains and no shared URL; sets T10e as the required project/path correction.

## 2026-05-10 - T10c Explicit API Preview Path

- Adds `proof:vercel-explicit-preview` as a no-deploy proof for a Vercel API request with `target: "preview"`.
- Confirms the project reports `productionBranch = main` while `tester-preview` remains the intended non-production branch.
- Keeps the private tester repo unpushed in T10c to avoid another Git-triggered production-target build and leaves no shared URL.

## 2026-05-10 - T10b Vercel Target Guard

- Adds a `prebuild` target guard that refuses production-target builds from non-production branches.
- Verifies the guard blocks Vercel's unsafe `production` target from `tester-preview` with `NO_GO_PRODUCTION_TARGET_FROM_NON_PRODUCTION_BRANCH`.
- Removes the failed deployment and keeps the tester project with no latest deployment, no domains and no shared URL.

## 2026-05-10 - T10 Internal Preview Target Rollback

- Triggers the first Git-based internal pilot from private `tester-preview`, then blocks it because Vercel reports `target = production`.
- Removes the deployment immediately and verifies no latest deployment, no domains and no shared/committed URL remain.
- Sets T10b as the next required step: fix Vercel preview target mapping before any tester URL is shared.

## 2026-05-09 - T9g Private Git Preview Source

- Creates the private tester portal repository and prepares `main` plus `tester-preview` before Vercel is connected.
- Connects the existing Vercel tester project to the private GitHub repository without running a manual deploy or sharing any URL.
- Updates the preview proof gate to accept Vercel Project API `link` connections and verifies `GO_GIT_PREVIEW_PATH_READY`.

## 2026-05-09 - T9f Preview Path Proof Gate

- Adds `proof:vercel-preview-path` for the tester portal template to verify Deployment Protection, Git integration and non-production preview branch before any URL is shared.
- Documents T9f as a safe proof gate, not a rollout: no deploy, no tester invites, no emails, no production database and no committed URLs.
- Sets T9g as the next safe step: connect a private Git/PR preview source before creating or sharing tester access.

## 2026-05-09 - T9e Protected Preview Deploy Rollback

- Retries deploy after protection gates are green, but rolls back immediately because Vercel reports production target and production alias again.
- Verifies the removed deployment is no longer inspectable, project latest production URL is none and the public alias returns 404.
- Sets T9f as the safer path: Git/PR-based preview or API deployment proof before any URL is shared.

## 2026-05-09 - T9d Vercel Authentication Protection Verified

- Enables Vercel Authentication Standard Protection for `sqx-edge-tester-portal` through the Vercel Project API.
- Verifies `audit:vercel-protection` returns `GO_PROTECTION_VERIFIED` with no active deployment, no domains and no latest production URL.
- Keeps T9d non-rollout: no deploy, no tester invites, no renewal emails, no production database and no committed URLs or raw tester emails.

## 2026-05-09 - T9c Vercel Deployment Protection Gate

- Adds `audit:vercel-protection` to block deploy retry unless Vercel Authentication or Password Protection is verified.
- Records the live project state as no active deployment, no latest deployment and no domains after the T9b rollback.
- Keeps T9c as `NO_GO_PROTECTION_NOT_VERIFIED` until dashboard/API protection can be proven without committing tester emails or URLs.

## 2026-05-09 - T9b Vercel Preview Deploy Rollback

- Authenticates Vercel, links the tester portal project and attempts the approved preview deploy.
- Rolls back immediately because Vercel CLI created production aliases instead of a safe protected preview.
- Verifies the deployment was removed, leaves no active URL, commits no tester emails and sets T9c as Deployment Protection verification before retry.

## 2026-05-09 - T9 Protected Vercel Preview Preflight

- Attempts the approved Vercel preview staging preflight and records the safe auth blocker: local Vercel token is invalid.
- Adds a reproducible `preflight:vercel-preview` script for the tester portal template before retrying deploy.
- Keeps T9 non-invasive after the blocker: no preview URL, no tester accounts, no emails, no production database and no committed secrets.

## 2026-05-09 - T8 Tester Portal Security Hardening

- Adds kill switch, rate-limit contract, visible watermark helper and deployment-protection checklist to the tester portal template.
- Strengthens middleware/security headers and exposes non-sensitive T8 hardening state through `/api/health`.
- Keeps T8 non-external: no Vercel deploy, no tester accounts, no renewal emails, no production database and no published URLs.

## 2026-05-09 - T7 Admin Tester Console

- Adds a protected admin tester console preview with demo lifecycle rows, audit hints and operator actions.
- Adds `/api/admin/testers` with create, renew, deny and block previews guarded by session and disabled-by-default admin flag.
- Keeps T7 non-external: no Vercel deploy, no tester accounts, no renewal emails, no production database and no published URLs.

## 2026-05-09 - T6 15-Day Expiry Renewal Flow

- Adds tester renewal lifecycle helpers for active, pending, expired, denied and blocked states.
- Adds protected `/api/tester/renewal` manual-preview decisions for approve, deny and block without mutating production data.
- Keeps T6 non-external: no Vercel deploy, no tester accounts, no renewal emails, no production database and no published URLs.

## 2026-05-09 - T5 Tester Pro Entitlement Gates

- Adds server-side `tester_pro` entitlement gate helpers and a protected `/api/tester/features` route to the tester portal template.
- Adds read-only Pro feature placeholders for the protected portal while keeping UI visibility separate from access control.
- Keeps T5 non-external: no Vercel deploy, no tester accounts, no real entitlement source, no production database and no published URLs.

## 2026-05-09 - T4 Login Session Prototype

- Adds a disabled-by-default local demo login/session prototype to the tester portal template.
- Adds login/logout route handlers, protected-route middleware redirect, session cookie helper and login form/logout button placeholders.
- Keeps T4 non-external: no Vercel deploy, no tester accounts, no real credentials, no production database, no emails and no published URLs.

## 2026-05-09 - T3 Tester Auth Data Contract

- Defines tester auth records, password hash policy, session cookie contract, renewal token model, audit events and secret boundaries before login implementation.
- Adds a pure `auth-data-contract.ts` template module with Argon2id, `__Host-` cookie, one-use token and audit event contracts.
- Keeps T3 non-external: no Vercel deploy, no tester accounts, no passwords, no emails, no production database and no published URLs.

## 2026-05-09 - T2 Tester Portal Bootstrap

- Adds a public-safe `templates/SQX_Edge_Tester_Portal/` Next.js/Vercel starter for the future private tester portal.
- Adds T2 documentation, roadmap/governance updates and static contracts for no-secret placeholders, protected route skeletons, dry-run cron and security headers.
- Keeps T2 non-external: no private repo creation, no Vercel deploy, no tester accounts, no emails and no published URLs.

## 2026-05-09 - T1 Cloud Tester Architecture Contract

- Defines the future private `SQX_Edge_Tester_Portal` Vercel architecture for 10 controlled Pro testers.
- Adds Access/Security Gatekeeper ownership for tester auth, 15-day renewal, audit, watermark and anti-distribution controls.
- Keeps T1 as contract-only: no deploy, no tester accounts, no emails and no runtime changes.

## 2026-05-09 - PG7 Project Generator buyer .cfx handoff

- Adds a Project Generator handoff card that prepares buyer-specific Markdown notes for `.cfx` deliveries.
- Wires copy/download actions and keeps the flow local, manual and free of backend or remote calls.
- Documents responsible limits: productivity/trazability only, no profitability promise.

## 2026-05-09 - G6 Institutional dashboard quick actions

- Integrates `institutional/feat/dashboard-quick-actions` as native quick actions from asset/category cards to Plan Mining and Project Generator.
- Adds Pipeline State operational health and a graph-style funnel while preserving editable local state.
- Keeps removed Top Picks and Matrix surfaces out of the application.

## 2026-05-09 - G5 Institutional Core sync

- Reconciles `institutional/main` through a non-destructive merge path so Institutional Core can fast-forward without force push.
- Preserves institutional-only assets: CODEOWNERS, institutional workflows, operating discipline doc and Analyzer C2 assets.
- Wires Analyzer C2 into the SQX manifest, dashboard tab, script load order, module registry and initialization contracts.

## 2026-05-09 - G4 Institutional Core repository discipline

- Registers `SQX_Institutional_Core` as a first-class operational repository through local remote `institutional`.
- Adds non-destructive dual-push discipline: fetch/check divergence, report each remote separately and never force-push Institutional Core.
- Sets G5 as the next recommended sync phase because `institutional/main` already contains institutional-only files that must be preserved.

## 2026-05-09 - M99 next commercial movement from M98 decision

- Adds a local M99 decision gate for the next controlled commercial movement from M98 monitor evidence.
- Blocks micro-step movement when observation, positive signal or risk constraints are not clean.
- Extends commercial traceability, packaging exclusions and public redaction pointers without automating traffic, checkout, email or licenses.

## 2026-05-09 - M98 approved M97 execution monitor

- Adds a local M98 monitor for the M97 execution result before any additional commercial movement.
- Blocks next-decision movement when observation time, support, refunds, claims or incidents are not clean.
- Extends commercial traceability, packaging exclusions and public redaction pointers without automating external actions.

## 2026-05-09 - M97 approved M96 commercial movement execution

- Adds a local M97 gate to record only the exact manual movement approved by M96.
- Blocks movement/result mismatches, traffic overflows and missing operator confirmations.
- Extends commercial traceability, packaging exclusions and public redaction pointers without automating checkout, emails or licenses.

## 2026-05-09 - SB17 Strategy Builder evidence handoff index

- Adds a reduced local evidence index for Strategy Builder buyer sessions.
- Tracks required buyer handoff pieces, missing evidence, privacy boundary and manual guardrails.
- Preserves no backend endpoint, no localStorage write, no remote ticket, no raw CSV and no buyer identity.

## 2026-05-09 - J11 Directional Coherence and Score Pro

- Adds native direction detection, directional coherence and compact Score Pro evidence to Champion vs Challenger.
- Carries reduced direction/coherence/score evidence into Strategy Builder handoffs and review UI.
- Preserves no Top Picks, no matrix/heatmap, no raw CSV persistence and no remote calls.

## 2026-05-09 - J10 Temporal Health and EGT v2 handoff

- Extends Champion vs Challenger review exports with reduced `temporal_health` and `egt_v2` evidence fields.
- Carries the same redacted evidence into Strategy Builder handoffs and package `source_summary` context.
- Preserves no raw CSV, no OOS block internals, no remote calls and manual operator review boundaries.

## 2026-05-09 - J9 Temporal Health and EGT v2 UI

- Shows compact Temporal Health and EGT v2 chips inside Champion vs Challenger rankings.
- Adds visual-only `Health OK` and `EGT v2 OK` filters without changing export or Strategy Builder handoff payloads.
- Uses first-party historical series to derive local regime blocks for EGT v2 when candidate/OOS evidence is available.

## 2026-05-09 - J8 Temporal Health and EGT v2 helpers

- Adds pure `computeTemporalHealth` evidence in Champion vs Challenger core for OOS peak, drawdown-at-close and recovery state.
- Adds pure `assessEgtV2` evidence in the regime adapter with `STRONG`, `COMPLIANT`, `DEFENSIVE`, `INSUFFICIENT`, `RISK` and `UNKNOWN` verdicts.
- Extends JS contracts without adding UI rendering, backend endpoints, persistence, remote calls or Top Picks/Matrix surfaces.

## 2026-05-09 - J7 Temporal Health and EGT v2 contract

- Documents JoseLivan commit `06767d8eef597987530f152d54860ab96e590ffa` as a native SQX Edge contract.
- Defines Temporal Health evidence for OOS peak, drawdown-at-close and recovery without a hard stagnation-days promotion filter.
- Defines EGT v2 verdicts and future J8/J9/J10 phases without copying Jose runtime code or restoring Top Picks/Matrix surfaces.

## 2026-05-09 - M96 next controlled commercial movement from M95 decision

- Adds `next_controlled_commercial_movement_from_m95_decision.py` to decide the next controlled movement from M95 evidence.
- Blocks execution, checkout, email, buyer contact and license actions from the decision gate.
- Extends packaging exclusions, public/private commercial traceability, roadmap/governance and tests.

## 2026-05-09 - M95 approved controlled commercial movement from M93 execution monitor

- Adds `approved_controlled_commercial_movement_from_m93_execution_monitor.py` to review M94 execution evidence before any additional movement.
- Tracks redacted observation hours, responses, positive signals, support, refund, claims and incident counts.
- Extends packaging exclusions, public/private commercial traceability, roadmap/governance and tests.

## 2026-05-09 - M94 approved controlled commercial movement from M93 execution

- Adds `approved_controlled_commercial_movement_from_m93_execution.py` to record only the exact M93-approved commercial movement.
- Caps micro-step execution to one private link and three invites, and blocks non-approved deviations.
- Extends packaging exclusions, public/private commercial traceability, roadmap/governance and tests.

## 2026-05-09 - M93 next controlled commercial movement from M92 decision

- Adds `next_controlled_commercial_movement_from_m92_decision.py` to decide the next controlled commercial movement from M92 evidence.
- Blocks execution, checkout, email and license actions from the decision gate.
- Extends packaging exclusions, public/private commercial traceability, roadmap/governance and tests.

## 2026-05-09 - M92 approved controlled commercial movement execution monitor

- Adds `approved_controlled_commercial_movement_execution_monitor.py` to review M91 execution evidence before any additional movement.
- Tracks redacted observation hours, responses, positive signals, support, refund, claims and incident counts.
- Extends packaging exclusions, public/private commercial traceability, roadmap/governance and tests.

## 2026-05-09 - M91 approved controlled commercial movement execution

- Adds `approved_controlled_commercial_movement_execution.py` to record only the exact M90-approved commercial movement.
- Caps micro-step execution to one private link and three invites, and blocks non-approved deviations.
- Extends packaging exclusions, public/private commercial traceability, roadmap/governance and tests.

## 2026-05-09 - M90 next controlled commercial movement decision

- Adds `next_controlled_commercial_movement_decision.py` to decide the next controlled commercial movement from M89 evidence.
- Blocks execution, checkout, email and license actions from the decision gate.
- Extends packaging exclusions, public/private commercial traceability, roadmap/governance and tests.

## 2026-05-09 - M89 controlled commercial next movement execution monitor

- Adds `controlled_commercial_next_movement_execution_monitor.py` to review M88 execution evidence before any broader commercial movement.
- Tracks redacted observation hours, responses, positive signals, support, refund, claims and incident counts.
- Extends packaging exclusions, public/private commercial traceability, roadmap/governance and tests.

## 2026-05-09 - M88 controlled commercial next movement execution

- Adds a guarded internal execution record for the exact manual commercial movement approved by M87.
- Blocks deviations from M87 and keeps micro-step preparation capped at one private link and three invites.
- Extends packaging exclusions, public/private commercial traceability, roadmap/governance and tests.

## 2026-05-09 - M87 controlled commercial next movement

- Adds a guarded internal decision gate for the next controlled commercial movement from M86 evidence.
- Supports observation, next micro-step preparation, private review packet, hold or sales pause without automation.
- Extends packaging exclusions, public/private commercial traceability, roadmap/governance and tests.

## 2026-05-09 - M86 controlled traffic expansion execution monitor

- Adds a guarded internal monitor for the M85 execution result before any further movement.
- Tracks redacted responses, positive signals, support, refunds, claims and incident counts.
- Extends packaging exclusions, public/private commercial traceability, roadmap/governance and tests.

## 2026-05-09 - M85 controlled traffic expansion execution

- Adds a guarded internal execution record for the exact manual action approved by M84.
- Blocks deviations from the M84 decision and keeps repeat traffic capped at one private link and three invites.
- Extends packaging exclusions, public/private commercial traceability, roadmap/governance and tests.

## 2026-05-09 - M84 controlled traffic expansion decision

- Adds a guarded internal decision gate that converts M83 monitor evidence into one manual next action.
- Supports repeat, private review packet, hold, pause or continued observation without automating traffic, checkout or licenses.
- Extends packaging exclusions, public/private commercial traceability, roadmap/governance and tests.

## 2026-05-09 - M83 controlled traffic expansion monitor

- Adds a guarded internal monitor for the M82 tiny traffic step before repeating, pausing or widening again.
- Tracks redacted aggregate responses, positive signals, support, refund, claims and incident counts.
- Extends packaging exclusions, public/private commercial traceability, roadmap/governance and static tests.

## 2026-05-09 - M82 tiny controlled traffic expansion step

- Adds a guarded internal tool and config for one tiny reversible traffic expansion step after M81 approval.
- Keeps evidence redacted: channel, counts, owner and next review only; no buyer identity, checkout payloads or license files.
- Extends portable packaging exclusions, release checklist, public/private commercial traceability and static tests.

## 2026-05-09 - R47 controlled commercial release candidate

- Regenerates the portable ZIP after the Strategy Builder buyer-session support phases.
- Verifies the refreshed package with frontend contracts, full Python suite, `git diff --check`, distribution audit and clean extracted portable API health.
- Records the current candidate as controlled commercial delivery only: demos, assisted early access and manual first-buyer handoff, not mass public launch.
- Publishes local ZIP traceability: `SQX_Edge_Tool_Portable_20260509_102131.zip`, SHA256 `18EC98981D8B52535E1FE26EA47876588FA2EB8321DD2A9706CBD30B6A0B7E5D`.

## 2026-05-08 - R45 controlled publication plan

- Adds a public-safe controlled publication plan for the verified portable ZIP without publishing a GitHub Release.
- Records the release candidate in `product_manifest.json` as `prepared_not_published` with tag draft `v0.2.0-r45`.
- Documents release notes, pre-publication gate command, post-publication record command, rollback steps and no-sensitive-data boundary.
- Adds static coverage for the R45 plan and verified ZIP traceability.

## 2026-05-08 - R44/A63 portable after real MTF GO

- Regenerates the portable ZIP after the real A56 multi-timeframe GO and validates it from a clean extracted folder.
- Adds broad `analysis_output/` exclusion plus explicit `real_mtf_pipeline_run` guards to package, audit, release checklist, product manifest and tests.
- Verifies the release with JS contracts, full Python suite, `git diff --check`, distribution audit and portable API health.
- Publishes local ZIP traceability: `SQX_Edge_Tool_Portable_20260508_201652.zip`, SHA256 `2725D2FC7CB9FD6E05AFDF1C7E20772B629BFBE8BE98532D4F5622A08628116E`.

## 2026-05-08 - A62 recent-bars OHLC download mode

- Adds `--recent-bars` to the MT5/Dukascopy downloader, using `copy_rates_from_pos` for controlled recent OHLC acquisition when fixed historical ranges return no data.
- Aligns the MT5 symbol map with the product manifest universe by using `USDMXN` and `USDZAR` instead of the external-folder draft `AUDCHF` and `NZDCHF`.
- Downloads 33 assets x 4 timeframes from local Dukascopy MT5 and validates the resulting OHLC folder through A56 with GO across A55/A53/A54.

## 2026-05-08 - A61 MT5 IPC diagnostic

- Adds `mt5_ipc_diagnostic.py` as an internal operator diagnostic for MT5 Python IPC readiness before full OHLC download.
- Captures Python/MetaTrader5 versions, terminal process state and configured/active/portable initialization variants into JSON and Markdown evidence.
- Keeps the diagnostic and generated evidence excluded from portable buyer builds, distribution audit and release checklist.
- Records MT5 IPC as GO after active-terminal initialization succeeds; remaining work moves to OHLC retrieval mode and universe alignment.

## 2026-05-08 - A60 MT5 active-terminal retry mode

- Adds `--use-active-terminal` and `--initialize-timeout-ms` to the internal MT5/Dukascopy downloader so the operator can connect to an already-open terminal without forcing the configured executable path.
- Confirms Dukascopy MT5 is open and responsive locally, but records another controlled NO_GO because the Python IPC bridge still returns timeout.
- Adds `docs/A60_MT5_ACTIVE_TERMINAL_MODE.md` with the exact retry command and the remaining manual MT5 checks before full OHLC download.

## 2026-05-08 - A59 local MT5 real-data validation smoke

- Runs the first local A58 smoke against Dukascopy MT5 for `EURUSD/H1`.
- Confirms the terminal path and `MetaTrader5` dependency are present, but records a NO_GO because MT5 returned IPC timeout during initialization.
- Adds `docs/A59_REAL_DATA_VALIDATION.md` with exact rerun, full download and A56 validation commands before any MTF evidence promotion.

## 2026-05-08 - A58 internal MT5/Dukascopy OHLC download gate

- Adds `dukas_mt5_ohlc_download.py` as an operator-only, config-driven downloader for MT5/Dukascopy OHLC CSV files feeding A55/A56 real-data validation.
- Adds coverage JSON/Markdown/CSV output, dry-run support and tests with a fake MT5 module so CI does not require MetaTrader5.
- Excludes the downloader, config and generated OHLC/coverage data from portable buyer packaging, distribution audit, release checklist and product manifest.
- Updates roadmap/governance notes and records Strategy Builder as a future "only one platform" commercial hook, separate from this data-acquisition phase.

## 2026-05-08 - A57 read-only MTF evidence UI

- Anade `core/mtf_evidence.py` y `/api/mtf/evidence` para resumir la salida A56 sin rutas completas ni payloads crudos.
- Incorpora un panel `MTF Evidence` en Inicio y actualiza la franja de `SQX Priority` solo cuando existe evidencia A56 GO.
- Mantiene el dashboard bloqueado/pendiente si A56 devuelve NO_GO, falta el reporte o la API local no esta disponible.

## 2026-05-08 - A56 real MTF pipeline run

- Anade `real_mtf_pipeline_run.py` para orquestar A55 -> A53 -> A54 desde CSV OHLC reales hasta artefactos del Plan Quality Advisor.
- Devuelve GO solo si el builder genera metricas, el intake valida la fuente y los artefactos guardados se crean correctamente.
- Mantiene salida NO_GO trazable cuando faltan CSV o cobertura, sin sintetizar datos ni tocar dashboard.

## 2026-05-08 - A55 OHLC metric builder

- Anade `ohlc_metric_builder.py` para generar `asset_metrics[_TF].json` desde CSV OHLC revisables aportados por el operador.
- Cubre metricas requeridas por el scorer multi-timeframe: ADX, eficiencia, SMA persistence, RSI edge, ATR, vol-of-vol, Hurst distance, OU half-life, kurtosis, VWAP y round bounce.
- Mantiene la regla de no sintetizar timeframes y rechaza archivos con barras insuficientes.

## 2026-05-08 - A54 guarded multi-timeframe plan artifacts

- Anade `multi_timeframe_plan_artifacts.py` para conectar A53 con `Plan Quality Advisor` solo cuando el intake multi-timeframe devuelve GO.
- Genera reportes A53/A54 trazables y bloquea la salida MTF cuando faltan M30/M15/H4 reales.
- Cubre rutas GO/NO-GO con tests sin modificar dashboard ni exponer evidencia parcial en UI.

## 2026-05-08 - A53 multi-timeframe source intake

- Anade `multi_timeframe_source_intake.py` y `multi_timeframe_source_policy.json` para preparar y validar una carpeta real de metricas H1/M30/M15/H4.
- Permite reutilizar el H1 first-party de A52, pero bloquea M15/M30/H4 si faltan archivos reales.
- Deja un flujo GO/NO-GO trazable antes de conectar evidencia multi-timeframe al advisor o a la UI.

## 2026-05-08 - A52 first-party H1 metric source

- Anade `first_party_metric_source.py` para convertir `scores-data.js` en `asset_metrics.json` H1 con manifiesto de procedencia y hashes.
- Ajusta scorer/gate para aceptar `hurst_dist` precomputado del dashboard sin inventar un `hurst` bruto.
- Valida el bundle generado con el gate A51 y deja explicitado que M15/M30/H4 no se sintetizan.

## 2026-05-08 - A51 multi-timeframe metric gate

- Anade `multi_timeframe_metric_gate.py` para validar carpetas `asset_metrics[_TF].json` antes de usarlas como evidencia propia.
- Comprueba archivos por TF, cobertura de activos, completitud de metricas requeridas, activos desconocidos, compatibilidad con el scorer y SHA256.
- Mantiene la disciplina de no descargar datos ni modificar scores del dashboard desde el gate.

## 2026-05-08 - A50 multi-timeframe plan review

- Conecta el consenso multi-timeframe de `multi_timeframe_scoring.py` al `Plan Quality Advisor` como evidencia opcional.
- Mantiene la recomendacion ordenada por baseline H1 para no sustituir automaticamente el plan con metricas no verificadas.
- Anade resumen MTF, cobertura, consenso, mejor TF y assessment por mining cuando existe `asset_metrics[_TF].json`.

## 2026-05-08 - A49 controlled multi-timeframe scoring

- Anade `multi_timeframe_scoring.py` como herramienta backend aislada para convertir `asset_metrics[_TF].json` en scores por timeframe y consenso ponderado.
- Mantiene el flujo seguro: no descarga datos, no inyecta HTML y no cambia UI; solo consume metricas ya preparadas.
- Cubre el contrato con fixtures H1/M15/M30 y salida Markdown/JSON para operador.

## 2026-05-08 - A48 HTML value recovery

- Recupera valor del HTML comparado sin reintroducir los tabs eliminados `Top Picks` ni `Matriz Completa`.
- Anade controles nativos de backup/restauracion de estado local contra los endpoints `/api/state/*`, limitados a claves no sensibles.
- Anade resumen dinamico `Plan v2` en Workflow y una preparacion visual bloqueada para Priority multi-TF, pendiente de motor de scoring dedicado.
- Actualiza arquitectura, contratos JS y tests estaticos para el nuevo modulo `state-backup.js`.

## 2026-05-08 - A47 Jose repo value extraction

- Compara el repo `jlivanmaseda-maker/sqx-edge-pipeline` con nuestra arquitectura actual.
- Integra un `Plan Quality Advisor` propio para revisar el plan de minings contra scores objetivos y proponer alternativas diversificadas.
- Documenta mejoras aprovechables, duplicados ya absorbidos y fases futuras para scoring multi-timeframe.

## 2026-05-08 - R42 portable release candidate refresh

- Regenera el ZIP portable final tras V9 con `SQX_Edge_Tool_Portable_20260508_164956.zip`.
- Verifica contratos frontend, suite Python, `git diff --check`, auditoria de distribucion y arranque del API portable extraido.
- Publica trazabilidad local con SHA256 `92BEF393D5EF4D5B32FB0FBC9A11A04BE30E648B4E0D51E70AA0D5F8A3C73534`.

## 2026-05-08 - V9 SQX Views import preview

- Anade preview visual al importar packs JSON de presets en `SQX Views`.
- Muestra presets entrantes, metricas, columnas estimadas, anos, orden y si reemplaza un preset local.
- Refuerza contratos JS, tests estaticos y E2E para cubrir el preview antes de la fusion local.

## 2026-05-08 - PG6 Project Generator import preview

- Anade preview visual al importar packs JSON de presets custom en `Project Generator`.
- Muestra presets entrantes, asset, timeframe, direccion, capa y si el preset reemplaza uno local.
- Refuerza contratos JS, tests estaticos y E2E para cubrir el preview antes de la fusion local.

## 2026-05-08 - V8 SQX Views asset and validation workflow packs

- Anade packs de `SQX Views` por familia de activo y flujo de validacion.
- Incluye Free Core Validation, Asset Family Review, Validation Screen Flow y Audit Export Flow.
- Permite cargar la primera vista del flujo, guardar el pack completo como presets locales o exportarlo como JSON portable.
- Refuerza contratos JS, tests estaticos y E2E para cubrir los nuevos packs operativos.

## 2026-05-08 - PG5 Project Generator richer custom profile families

- Amplia `Project Generator` con ocho perfiles custom starter y guia de uso por perfil.
- Anade familias por objetivo: comprador inicial, validacion intradia, revision de riesgo y muestra Pro completa.
- Permite cargar el primer perfil de una familia, guardar el pack completo como presets locales o exportarlo como JSON portable.
- Refuerza contratos JS, tests estaticos y E2E para cubrir los nuevos packs de familias.

## 2026-05-08 - V7 SQX Views buyer profile packs

- Anade packs por perfil en `SQX Views`: evaluacion Free, Setup Assist Pro, comprador centrado en riesgo y entrega de auditoria.
- Permite cargar la primera vista del pack, guardar todas sus vistas como presets propios y exportar cada pack como JSON portable.
- Refuerza contratos JS, tests estaticos y E2E para cubrir render, guardado y contrato de exportacion de packs por perfil.

## 2026-05-08 - R41 portable ZIP after PG4

- Regenera el ZIP portable tras los perfiles starter de `Custom libre`.
- Ejecuta release checklist completo: contratos JS, pytest, `git diff --check`, audit distribution y prueba de API desde ZIP extraido.
- Verifica flujo de usuario basico con `START_SQX_EDGE.bat`, `/api/health`, marcador PG4 en dashboard extraido y `STOP_SQX_EDGE.bat`.
- Publica trazabilidad del ZIP `SQX_Edge_Tool_Portable_20260508_075208.zip` con SHA256 `CCB398057E5DEC6AC5AE2993E58E8DCEDBDB0686DD09539E30F9017D54F3A34D`.

## 2026-05-08 - PG4 starter custom preset profiles

- Anade perfiles starter en `Custom libre` para arrancar proyectos Forex, indices y oro sin depender del plan mining.
- Permite cargar cada starter en el formulario, guardarlo como preset local y exportar el pack starter como JSON.
- Refuerza contratos JS, tests estaticos y E2E para cubrir render, eventos y contrato portable del pack starter.

## 2026-05-08 - R40 portable ZIP after V6/PG3

- Regenera el ZIP portable final tras los ejemplos buyer-ready de SQX Views y los packs JSON de `Custom libre`.
- Ejecuta release checklist completo: contratos JS, pytest, `git diff --check`, audit distribution y prueba de API desde ZIP extraido.
- Publica trazabilidad del nuevo ZIP `SQX_Edge_Tool_Portable_20260508_004141.zip` con SHA256 `EB4031FE3A6035DA0F04D569A2963B120CCA6957C5EB4A7F994A078F56556E4C`.

## 2026-05-08 - PG3 Custom libre portable preset packs

- Anade exportacion/importacion JSON para presets de `Custom libre` en Project Generator.
- Fusiona packs importados con presets locales sin duplicar IDs y mantiene validacion de asset/timeframe.
- Refuerza contratos JS, tests estaticos y E2E para cubrir portabilidad de presets custom.

## 2026-05-08 - V6 SQX Views buyer-ready examples

- Anade ejemplos buyer-ready en `SQX Views` para primera revision, robustez, riesgo y auditoria completa.
- Permite cargar cada ejemplo, guardarlo como preset propio y exportar el pack de ejemplos en JSON.
- Activa los contratos JS de SQX Views en la suite principal y refuerza static/E2E para cubrir los ejemplos.

## 2026-05-08 - V5 SQX View Creator integration closeout

- Cierra la integracion del prototipo anual de SQX View Creator dentro del tab nativo `SQX Views`.
- Archiva la carpeta staging `tab a integrar como nueva funcion/` en backup previo y la elimina del workspace local.
- Actualiza trazabilidad de roadmap, gobernanza y arquitectura para dejar el siguiente paso real en V6 o PG3.

## 2026-05-08 - PG2 Custom libre reusable presets

- Anade presets locales para guardar, cargar y eliminar configuraciones de `Custom libre`.
- Mantiene los presets en `localStorage` bajo `sqx_pg_custom_presets_v1` sin tocar backend ni rutas personales.
- Refuerza contratos JS, tests estaticos y E2E para cubrir el flujo de presets custom.

## 2026-05-08 - PG1 Custom libre fuera del plan

- Anade un flujo `Custom libre` en Project Generator para crear `.cfx` sin depender de un mining del plan.
- Expone `/api/generate-custom` con asset, timeframe, direccion, blocksetting, nombre y capa propios.
- Mantiene intacta la generacion masiva por plan y refuerza contratos JS, API y E2E.

## 2026-05-07 - V4 SQX View Creator workflow handoff

- Conecta Workflow y Estrategias con SQX Views mediante handoffs con preset y nombre precargados.
- Mantiene la navegacion y preparacion de vistas dentro de `view-creator.js` para evitar enlaces sueltos.
- Refuerza contratos JS y smoke E2E para cubrir handoff desde ambas zonas operativas.

## 2026-05-07 - V3 SQX View Creator preset packs

- Anade exportacion/importacion JSON para presets propios de SQX Views.
- Valida metricas conocidas al importar y fusiona packs sin duplicar presets existentes.
- Refuerza contratos JS y E2E para cubrir handoff portable entre instalaciones.

## 2026-05-07 - V2 SQX View Creator preset persistence

- Anade presets propios guardados en `localStorage` para SQX Views.
- Permite guardar, cargar y eliminar combinaciones de metricas sin depender de archivos externos.
- Refuerza contratos JS y E2E para cubrir persistencia del View Creator.

## 2026-05-07 - V1 native SQX View Creator

- Integra `SQX Views` como tab nativo para generar vistas `.vw` anuales de StrategyQuant X.
- Migra el prototipo Tkinter a un flujo portable de navegador con preset EGT Core, preview XML y descarga directa.
- Anade contratos JS, cobertura estatica, E2E visual y documentacion de arquitectura.

## 2026-05-07 - M81 controlled traffic expansion review

- Anade gate interno para revisar si procede una ampliacion minima y reversible de trafico.
- Actualiza estado comercial a `controlled_traffic_expansion_review_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M81.

## 2026-05-07 - M80 manual publication monitor

- Anade gate interno para monitorizar la publicacion manual limitada antes de ampliar trafico.
- Actualiza estado comercial a `manual_publication_monitor_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M80.

## 2026-05-07 - M79 manual limited publication record

- Anade gate interno para registrar una publicacion manual limitada despues de M78.
- Actualiza estado comercial a `manual_limited_publication_record_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M79.

## 2026-05-07 - M78 operator publication review

- Anade gate interno para revisar manualmente el borrador limitado antes de cualquier publicacion.
- Actualiza estado comercial a `operator_publication_review_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M78.

## 2026-05-07 - M77 limited publication draft

- Anade gate interno para preparar un borrador de publicacion limitada despues de M76.
- Actualiza estado comercial a `limited_publication_draft_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M77.

## 2026-05-07 - M76 controlled publication gate

- Anade gate interno para preparar publicacion controlada solo despues de la revision privada M75.
- Actualiza estado comercial a `controlled_publication_gate_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M76.

## 2026-05-07 - M75 private asset review

- Anade gate interno para revisar privadamente el asset comprador-facing antes de publicacion o trafico.
- Actualiza estado comercial a `private_asset_review_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M75.

## 2026-05-07 - M74 next buyer-facing asset

- Anade gate interno para preparar un unico asset comprador-facing para review privado tras M73.
- Actualiza estado comercial a `next_buyer_facing_asset_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M74.

## 2026-05-07 - M73 controlled distribution review

- Anade gate interno para revisar evidencia M72 y decidir repetir, corregir, pausar o preparar el siguiente asset buyer-facing.
- Actualiza estado comercial a `controlled_distribution_review_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M73.

## 2026-05-07 - M72 controlled distribution step

- Anade gate interno para ejecutar la decision M71 como paso de distribucion minimo, reversible y sin datos personales.
- Actualiza estado comercial a `controlled_distribution_step_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M72.

## 2026-05-07 - M71 next controlled buyer outcome

- Anade gate interno para registrar el resultado del siguiente comprador controlado sin datos personales, payloads de checkout ni licencias.
- Actualiza estado comercial a `next_controlled_buyer_outcome_ready`.
- Mantiene el documento operativo completo en el repo privado y deja punteros publicos para M71.

## 2026-05-07 - Public commercial redaction

- Redacta roadmap comercial, runbooks de venta y packs Pro buyer/template en el repo publico como punteros de trazabilidad.
- Mantiene la copia completa en `CryptoLeon78/sqx-edge-commercial-private` con commit base `ed79719 Initial private commercial export`.
- Anade `docs/PUBLIC_COMMERCIAL_POINTERS.md` y actualiza gobernanza/manifiesto/tests para la frontera publico/privado.

## 2026-05-07 - Private commercial repository published

- Instala GitHub CLI en modo portable local bajo `private-commercial/tools/gh`.
- Crea el repo privado `CryptoLeon78/sqx-edge-commercial-private`.
- Sube el export comercial privado con commit `ed79719 Initial private commercial export`.
- Verifica con GitHub CLI que el repositorio remoto es privado.

## 2026-05-07 - Local private commercial repository prepared

- Inicializa el export comercial privado como repositorio git local ignorado por el repo publico.
- Anade `.gitignore`, `PUBLISH_TO_GITHUB.md` y `SECURITY.md` dentro del export privado.
- Registra el commit privado local `ed79719 Initial private commercial export` como base para subir al repo privado.
- Mantiene pendiente la creacion del remoto privado y la posterior redaccion de docs publicos sensibles.

## 2026-05-07 - Private commercial docs split prepared

- Anade `private_commercial_split.py` para exportar docs comerciales sensibles a un staging privado ignorado por git.
- Anade plan de split con indice SHA256, destino privado recomendado y regla de no borrar fuentes publicas hasta verificar copia privada.
- Actualiza exclusiones de portable, audit, release checklist y manifest para no enviar la herramienta interna al usuario final.
- Mantiene trazabilidad publica mediante manifiesto y tests sin mover todavia el historial expuesto.

## 2026-05-07 - CI baseline and private commercial docs boundary

- Anade `requirements-dev.txt` para separar runtime de dependencias de test/CI.
- Anade GitHub Actions para compilar Python, ejecutar pytest, contratos JS y `git diff --check`.
- Define la frontera de documentos comerciales privados con manifiesto de migracion y staging local ignorado.
- Mantiene el estado comercial vigente en `next_controlled_buyer_readiness_ready`.

## 2026-05-07 - Next controlled buyer readiness

- Anade M70 con check formal antes de compartir otro enlace privado con un comprador controlado.
- Anade `next_controlled_buyer_readiness.py` para validar slot unico, checkout, licencia, entrega, soporte, follow-up, safe claims y regla de pausa.
- Actualiza estado comercial a `next_controlled_buyer_readiness_ready`.
- Mantiene evidencia de readiness y herramienta interna fuera del ZIP portable.

## 2026-05-07 - Post-sale micro updates

- Anade M69 con micro-mejoras aplicadas a onboarding, activacion, soporte y copy publico.
- Anade `post_sale_micro_updates.py` para validar marcadores buyer-facing y readiness del siguiente comprador controlado.
- Actualiza estado comercial a `post_sale_micro_updates_ready`.
- Mantiene evidencia de readiness y herramienta interna fuera del ZIP portable.

## 2026-05-07 - Post-sale improvement loop

- Anade M68 con bucle de mejora post-venta para onboarding, soporte y copy publico.
- Anade `post_sale_improvement_loop.py` para validar acciones agregadas desde el primer comprador controlado.
- Actualiza estado comercial a `post_sale_improvement_loop_ready`.
- Mantiene evidencia post-venta y herramienta interna fuera del ZIP portable.

## 2026-05-07 - First controlled buyer log

- Anade M67 con registro operativo del primer comprador controlado y revision post-venta ligera.
- Anade `first_controlled_buyer_log.py` para validar compra, entrega, activacion, soporte, feedback y decision.
- Actualiza estado comercial a `first_controlled_buyer_log_ready`.
- Mantiene evidencia de primera venta controlada fuera del ZIP portable.

## 2026-05-07 - Public buyer page cadence

- Anade M66 con checklist de pagina publica de comprador y cadencia de primera venta.
- Anade `public_buyer_page_cadence.py` para validar copy, pasos de comprador, soporte, claims y rollback.
- Actualiza estado comercial a `public_buyer_page_cadence_ready`.
- Mantiene evidencia de pagina/cadencia fuera del ZIP portable.

## 2026-05-07 - Buyer-ready checkout closeout

- Anade M65 con cierre buyer-ready para checkout, release, licencia, soporte y rollback.
- Anade `buyer_ready_checkout_closeout.py` para validar una ruta de comprador basico antes de ventas controladas.
- Actualiza estado comercial a `buyer_ready_checkout_release_closeout_ready`.
- Mantiene evidencia interna y herramientas comerciales fuera del ZIP portable.

## 2026-05-07 - Template Pack 2 feedback cohort

- Anade M64 con revision de cohorte temprana de Template Pack 2.
- Anade `template_pack_2_feedback_cohort.py` para validar feedback agregado, soporte, refunds y decision de roadmap.
- Actualiza estado comercial a `template_pack_2_feedback_cohort_ready`.
- Mantiene evidencia agregada/redactada y fuera del ZIP portable.

## 2026-05-07 - Template Pack 2 sales register

- Anade M63 con registro interno de ventas de Template Pack 2.
- Anade `template_pack_2_sales_register.py` para validar venta, entrega, soporte, refunds, fallos y decision de escala.
- Actualiza estado comercial a `template_pack_2_sales_register_ready`.
- Mantiene evidencia redactada y fuera del ZIP portable.

## 2026-05-07 - Template Pack 2 post-purchase handoff

- Anade M62 con handoff post-compra de Template Pack 2.
- Anade `template_pack_2_handoff.py` para validar entrega, soporte, primer valor y decision de escala/pausa.
- Actualiza estado comercial a `template_pack_2_handoff_ready`.
- Mantiene evidencia redactada y fuera del ZIP portable.

## 2026-05-07 - Template Pack 2 purchase drill

- Anade M61 con compra controlada de Template Pack 2.
- Anade `template_pack_2_purchase_drill.py` para validar pedido, pago, entrega, soporte y refund/pause.
- Actualiza estado comercial a `template_pack_2_purchase_drill_ready`.
- Mantiene evidencia redactada y fuera del ZIP portable.

## 2026-05-07 - Template Pack 2 controlled publication

- Anade M60 con puerta de publicacion controlada para Template Pack 2.
- Anade `template_pack_2_publication.py` para validar checkout URL, variant ID, soporte, rollback y purchase drill.
- Actualiza estado comercial a `template_pack_2_controlled_publication_ready`.
- Mantiene la escritura de valores reales detras de `--apply`.

## 2026-05-07 - Template Pack 2 offer pack

- Anade M59 con oferta controlada para Template Pack 2.
- Anade `template_pack_2_offer_pack.py` para validar copy, FAQ, checkout draft, macros, soporte y safe claims.
- Actualiza estado comercial a `template_pack_2_offer_pack_ready`.
- Mantiene checkout en modo draft hasta completar URL, variant ID y soporte reales.

## 2026-05-07 - Template Pack 2 assets

- Anade M58 con recursos iniciales reales para Template Pack 2.
- Anade `template_pack_2_assets.py` para validar perfiles, presets CSV, soporte, safe claims y empaquetado add-on separado.
- Actualiza estado comercial a `template_pack_2_assets_ready`.
- Mantiene Template Pack 2 fuera del ZIP portable principal y listo como add-on separado.

## 2026-05-07 - Template Pack 2 specs

- Anade M57 con especificacion inicial de Template Pack 2 derivada del action plan M56.
- Anade `template_pack_2_specs.py` para validar alcance, familias de activos, presets, soporte, entrega, claims y siguiente fase.
- Actualiza estado comercial a `template_pack_2_specs_ready`.
- Mantiene Pack 2 como especificacion trazable antes de crear recursos comerciales.

## 2026-05-07 - Template Pack 1 action plan

- Anade M56 con plan accionable para iterar oferta, ampliar trafico, preparar Template Pack 2 o pausar ventas.
- Anade `template_pack_1_action_plan.py` para validar owner, prioridad, acciones, soporte, claims, distribucion y siguiente fase.
- Actualiza estado comercial a `template_pack_1_action_plan_ready`.
- Mantiene el plan como evidencia redactada sin mensajes crudos de comprador ni payloads de proveedor.

## 2026-05-07 - Template Pack 1 feedback cohort

- Anade M55 con revision de cohorte y feedback real para Template Pack 1.
- Anade `template_pack_1_feedback_cohort.py` para validar compradores, feedback, bugs, friccion, soporte, refunds y decision de roadmap.
- Actualiza estado comercial a `template_pack_1_feedback_cohort_ready`.
- Bloquea escalado o Template Pack 2 sin senales positivas, soporte controlado y claims seguros.

## 2026-05-07 - Template Pack 1 sales register

- Anade M54 con registro interno de ventas add-on para Template Pack 1.
- Anade `template_pack_1_sales_register.py` para validar venta, entrega, soporte, refunds, fulfillment y decision de escala.
- Actualiza estado comercial a `template_pack_1_sales_register_ready`.
- Mantiene referencia de comprador redactada, evidencia local fuera del ZIP base y decision responsable antes de abrir mas trafico.

## 2026-05-07 - Template Pack 1 handoff

- Anade M53 con gate de handoff post-compra para Template Pack 1.
- Anade `template_pack_1_handoff.py` para validar entrega, soporte inicial, primer valor y decision de escalar o pausar.
- Actualiza estado comercial a `template_pack_1_handoff_ready`.
- Mantiene datos de comprador redactados y evidencia local fuera del ZIP base.

## 2026-05-07 - Template Pack 1 purchase drill

- Anade M52 con gate de compra controlada para Template Pack 1.
- Anade `template_pack_1_purchase_drill.py` para validar pedido, pago, entrega separada, soporte y rollback.
- Actualiza estado comercial a `template_pack_1_purchase_drill_ready`.
- Mantiene evidencia de comprador redactada y el gate fuera del ZIP base.

## 2026-05-07 - Governance lookup discipline

- Anade G2 como regla operativa: consultar Project Governance o matriz de agentes antes de cada fase/mensaje de trabajo.
- Actualiza Project Governance, roadmap, ADR y README para reflejar ownership activo y checks esperados.
- Refuerza el contrato estatico de gobernanza.

## 2026-05-07 - Template Pack 1 live checkout gate

- Anade M51 con gate de publicacion controlada para Template Pack 1.
- Anade `template_pack_1_publication.py` para validar URL real, provider variant ID, email de soporte y rollback.
- Actualiza estado comercial a `template_pack_1_live_checkout_gate_ready`.
- Mantiene la publicacion bloqueada hasta recibir valores reales del proveedor.

## 2026-05-07 - Template Pack 1 public offer

- Anade M50 con oferta publica draft de Template Pack 1, FAQ, checkout wiring y macros de entrega/soporte.
- Anade `template_pack_1_offer.py` para validar copy, plan, precio, draft de checkout y claims seguros.
- Actualiza estado comercial a `template_pack_1_public_offer_ready`.
- Mantiene el add-on fuera del ZIP base y listo para conectar checkout real.

## 2026-05-07 - Template Pack 1 delivery

- Anade Template Pack 1 como add-on separado con perfiles JSON, CSV resumen, checklist y limites de soporte.
- Anade `template_pack_1_delivery.py` para validar y empaquetar el add-on.
- Actualiza estado comercial a `template_pack_1_delivery_ready`.
- Refuerza empaquetado para excluir el add-on del ZIP base y generar entrega separada.

## 2026-05-07 - Buyer onboarding support gate

- Anade recursos M48 de onboarding para comprador Pro basico.
- Anade `buyer_onboarding_support_gate.py` para validar compra, ZIP, licencia, instrucciones, FAQ, soporte y claims seguros.
- Actualiza estado comercial a `buyer_onboarding_support_gate_ready`.
- Refuerza empaquetado para excluir la herramienta interna y evidencia local.

## 2026-05-07 - Pro buyer data and template pack

- Anade `resources/pro-buyer-pack` con universo de activos, CSV importable y plantillas de activacion, soporte y primer valor.
- Anade `pro_buyer_pack.py` para validar el pack antes de publicar un ZIP comercial.
- Actualiza estado comercial a `pro_buyer_pack_ready`.
- Refuerza empaquetado para excluir la herramienta interna y evidencia local.

## 2026-05-07 - Commercial customer cockpit

- Anade endpoint read-only `GET /api/customer-cockpit`.
- Anade agregador redactado `customer_cockpit.py` para evidencia de customer success.
- Anade panel `Customer Success` en Inicio con clientes, renovaciones, tickets y oportunidades.
- Actualiza estado comercial a `customer_cockpit_ready`.

## 2026-05-07 - Specialist agent governance

- Anade `docs/PROJECT_GOVERNANCE.md` con agentes especializados, ownership, namespaces de fase y criterios de entrada M46.
- Anade ADR-0001 para registrar el modelo de gobernanza por agentes.
- Refuerza `.gitignore` para excluir `config/license.json` local.
- Actualiza roadmap y README con la baseline `G1`.

## 2026-05-07 - Customer success renewal loop

- Anade `customer_success_renewal.py` para revisar onboarding, activacion, soporte, renovacion y expansion responsable.
- Bloquea decisiones sin cliente, owner, activacion confirmada, soporte triado, notas de exito y claims seguros.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/customer_success_renewal`.
- Actualiza manifiesto a `customer_success_renewal_ready`.

## 2026-05-07 - Status and roadmap refresh

- Actualiza el estado visible del proyecto hasta M44 `hotfix_rollback_release_ready`.
- Registra el ultimo ZIP portable verificado y su SHA256 en README y roadmaps.
- Marca M45 como siguiente paso recomendado: customer success y renewal loop.
- Refresca el roadmap publico para reflejar el estado comercial real sin promesas financieras.

## 2026-05-06 - Launch assets kit

- Anade `launch_assets_kit.py` para validar ZIP, SHA256, capturas, copy, README comercial y release draft.
- Bloquea publicacion sin capturas desktop/mobile, support macro o checklist de publicacion.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/launch_assets_kit`.
- Actualiza manifiesto a `launch_assets_kit_ready`.

## 2026-05-06 - Public offer pack

- Anade `public_offer_pack.py` para validar copy, FAQ, release notes, buyer steps y pagina publica.
- Bloquea claims financieros prohibidos y oferta publica incompleta.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/public_offer_pack`.
- Actualiza manifiesto a `public_offer_pack_ready`.

## 2026-05-06 - Commercial feedback loop

- Anade `commercial_feedback_loop.py` para clasificar feedback y decidir version, precio, copy y siguiente accion.
- Bloquea cambios de oferta si falta feedback revisado, roadmap actualizado o owner de release notes.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/commercial_feedback_loop`.
- Actualiza manifiesto a `commercial_feedback_loop_ready`.

## 2026-05-06 - Post launch control

- Anade `post_launch_control.py` para revisar primeras ventas, activaciones, soporte, refunds y fallos.
- Bloquea escalado publico si hay tickets sin resolver, activaciones pendientes o fulfillment fallido.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/post_launch_control`.
- Actualiza manifiesto a `post_launch_control_ready`.

## 2026-05-06 - Limited public launch gate

- Anade `limited_public_launch.py` para validar una venta publica limitada tras el piloto.
- Bloquea `GO` sin piloto valido, checkout HTTPS, variantes reales, soporte, first sale cap y rollback owner.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/limited_public_launch`.
- Actualiza manifiesto a `limited_public_launch_ready`.

## 2026-05-06 - Pilot purchase kit

- Anade `pilot_purchase_kit.py` para preparar compra piloto privada con orden, licencia, entrega e importacion verificada.
- Consume evidencia M34 y bloquea `GO` si falta licencia firmada, manifest de entrega o confirmacion Pro en app.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/pilot_purchase_kit`.
- Actualiza manifiesto a `pilot_purchase_kit_ready`.

## 2026-05-06 - Commercial release candidate

- Anade `commercial_release_candidate.py` para validar ZIP, SHA256, readiness, clave publica y compra piloto.
- Bloquea venta publica si falta evidencia M33 `GO`, compra piloto o clave publica final.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/commercial_release_candidate`.
- Actualiza manifiesto a `commercial_release_candidate_ready`.

## 2026-05-06 - Checkout live readiness

- Anade `checkout_live_readiness.py` para validar URLs Lemon, variantes, soporte y rollback antes de venta publica.
- Bloquea si faltan `providerVariantId`, checkout HTTPS, relay HTTPS o evidencia M32 `GO`.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/checkout_live_readiness`.
- Actualiza manifiesto a `checkout_live_readiness_ready`.

## 2026-05-06 - Render staging purchase drill

- Anade `render_staging_purchase_drill.py` para probar webhook, cola y dispatch en Render staging.
- Exige flags explicitos `--send-webhook` y `--dispatch` para operaciones mutantes.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-relay/data/render_staging_purchase_drill`.
- Actualiza manifiesto a `relay_render_staging_purchase_drill_ready`.

## 2026-05-06 - Render staging apply gate

- Anade `render_staging_apply_gate.py` para validar la aplicacion final de variables en Render.
- Exige handoff M30 `GO`, confirmacion manual y `render_staging_gate.py` remoto `GO`.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-relay/data/render_staging_apply_gate`.
- Actualiza manifiesto a `relay_render_staging_apply_gate_ready`.

## 2026-05-06 - Local ingest Render handoff

- Anade `local_ingest_render_handoff.py` para convertir sesion local GO en variables listas para Render.
- Genera evidencia JSON/Markdown y `.env` local con `SQX_LOCAL_INGEST_URL`.
- Puede consumir la ultima sesion M29 o una URL explicita.
- Actualiza manifiesto a `relay_local_ingest_render_handoff_ready`.

## 2026-05-06 - Local ingest staging session

- Anade `local_ingest_staging_session.py` para orquestar backend local, tunel e ingest check.
- Mantiene arranque de backend/tunel como opt-in con `--start-backend` y `--start-tunnel`.
- Genera evidencia unica para la sesion previa a Render staging.
- Actualiza manifiesto a `relay_local_ingest_staging_session_ready`.

## 2026-05-06 - Local ingest tunnel launcher

- Anade `local_ingest_tunnel_launcher.py` para detectar `cloudflared`, `ngrok` o `localtunnel`.
- Valida el backend local en `/api/health` antes de lanzar tunel.
- Puede arrancar tunel con `--start` y parsear la URL publica de ingest.
- Actualiza manifiesto a `relay_local_ingest_tunnel_launcher_ready`.

## 2026-05-06 - Local ingest tunnel check

- Anade `local_ingest_tunnel_check.py` para validar `SQX_LOCAL_INGEST_URL` antes de configurarlo en Render.
- Comprueba politica HTTPS, `/api/health` y bundle firmado opcional hacia `/api/fulfillment/relay-ingest`.
- Guarda evidencia local en `backend/sqx-edge-relay/data/local_ingest_tunnel_check`.
- Actualiza manifiesto a `relay_local_ingest_tunnel_check_ready`.

## 2026-05-06 - Render staging secrets kit

- Anade `render_staging_secrets_kit.py` para generar secretos fuertes de staging.
- Escribe `.env` local ignorado por git y evidencia redactada.
- Bloquea placeholders, valores cortos y passwords de cuenta Render en entorno.
- Actualiza manifiesto a `relay_render_staging_secrets_kit_ready`.

## 2026-05-06 - Render staging launch pack

- Anade `render_staging_launch_pack.py` para preparar blueprint, SHA256, variables y comandos de staging.
- Integra el estado del Render staging gate en una evidencia unica.
- Guarda evidencia local en `backend/sqx-edge-relay/data/render_staging_launch_pack`.
- Actualiza manifiesto a `relay_render_staging_launch_pack_ready`.

## 2026-05-06 - Render staging gate

- Anade `render_staging_gate.py` como compuerta GO/NO-GO antes del despliegue vivo.
- Exige handshake Render `GO`, URL staging y evidencia remota `GO`.
- Guarda evidencia local en `backend/sqx-edge-relay/data/render_staging_gate`.
- Actualiza manifiesto a `relay_render_staging_gate_ready`.

## 2026-05-06 - Render credential handshake

- Anade `render_credentials_handshake.py` para validar politica de credenciales antes del deploy real.
- Bloquea el uso de password de cuenta Render mediante `RENDER_PASSWORD` o `RENDER_ACCOUNT_PASSWORD`.
- Guarda evidencia local JSON/Markdown ignorada por git.
- Actualiza manifiesto a `relay_render_credentials_handshake_ready`.

## 2026-05-06 - Render API preflight

- Anade `render_api_preflight.py` para validar API key, owner/workspace y blueprint staging.
- Amplia `.env.staging.example` con variables Render API.
- Documenta el flujo seguro sin usar password de cuenta en scripts.
- Actualiza manifiesto a `relay_render_api_preflight_ready`.

## 2026-05-06 - Render staging evidence pack

- Recomienda Render como primer proveedor de staging para el relay.
- Anade `render.staging.yaml.example`.
- Anade `staging_evidence.py` para generar decision GO/NO-GO en JSON y Markdown.
- Actualiza manifiesto a `relay_staging_execution_ready`.

## 2026-05-06 - Relay staging validation kit

- Anade `.env.staging.example` para entorno staging.
- Anade `staging_smoke.py` para validar health, config, observability, snapshot y webhook firmado.
- Anade checklist go/no-go de staging.
- Actualiza manifiesto a `relay_staging_ready`.

## 2026-05-06 - Production relay deployment package

- Anade Dockerfile, `.dockerignore` y plantillas de despliegue para el relay.
- Anade `deployment_check.py` para preflight de produccion.
- Documenta Render, Railway, Fly.io y VPS/systemd en la guia de despliegue.
- Actualiza manifiesto a `relay_production_deploy_ready`.

## 2026-05-06 - Relay observability and simulation

- Anade eventos JSONL y snapshots de cola para el relay remoto.
- Expone `GET /relay/observability` y `POST /relay/observability/snapshot`.
- Anade `simulate_purchase_flow.py` para probar compra -> relay -> dispatch -> snapshot.
- Actualiza manifiesto a `relay_observability_ready`.

## 2026-05-06 - Relay deployment hardening

- Anade `GET /relay/config-check` para validar configuracion sin exponer secretos.
- Protege endpoints operativos con `SQX_RELAY_OPERATOR_TOKEN` cuando esta configurado.
- Anade `.env.example`, `dispatch_worker.py` y `run-worker.bat` para operacion supervisada.
- Actualiza manifiesto, contratos y documentacion a estado `relay_deployment_ready`.

## 2026-05-06 - Deployable remote relay service

- Anade `backend/sqx-edge-relay` como servicio remoto separado del ZIP portable.
- Implementa cola remota con `pending`, `sent`, `failed`, dispatch y requeue.
- Conecta Lemon webhook -> relay bundle -> ingest local firmado.
- Refuerza packaging para excluir el relay del paquete final de cliente.

## 2026-05-06 - Trusted relay ingest

- Anade `POST /api/fulfillment/relay-ingest` para bundles firmados por relay remoto.
- Anade `relay_bundle.py` para preparar bundles de prueba y validar el flujo de relay.
- Refuerza exclusiones del ZIP con `relay_event_*.json` y tooling interno del relay.
- Actualiza la documentacion de M15 y las notas operativas del relay.

## 2026-05-06 - Operator retry cockpit

- Anade estados operativos y contador de intentos persistidos por request de fulfillment.
- Anade `POST /api/fulfillment/request-status` y resumen enriquecido en la cola local.
- Anade panel de fulfillment en Inicio para refrescar, procesar, ignorar y recolar requests.
- Separa la normalizacion compartida en `core/fulfillment_normalizer.py` para mantener el ZIP portable limpio.

## 2026-05-06 - Private receiver and queue

- Anade receiver privado local para webhooks de Lemon Squeezy.
- Persiste `events`, `requests` y `processed` con deduplicacion por `provider_event_id`.
- Expone endpoints locales para listar, inspeccionar y procesar requests.
- Documenta la fase M13 y la operativa del receiver.

## 2026-05-06 - Fulfillment automation bridge

- Anade `fulfillment_request.py` para validar firma y normalizar eventos de Lemon Squeezy.
- Anade `fulfill_from_request.ps1` para convertir una request en licencia firmada y entrega final.
- Refuerza exclusiones del ZIP para requests, eventos y tools internos de automatizacion.
- Documenta la fase M12 y las notas de automatizacion futura.

## 2026-05-06 - Checkout and fulfillment

- Prepara `upgrade.checkout` para Lemon Squeezy con Gumroad como fallback.
- Anade enlace de checkout en el panel Licencia, oculto hasta configurar URL real.
- Anade `prepare_customer_delivery.ps1` para preparar ZIP + licencia + instrucciones por cliente.
- Documenta M11 y runbook de entrega comercial.

## 2026-05-06 - Manual license issuer

- Anade `license_issue.py` para emitir licencias Pro firmadas en un solo comando.
- Permite cliente, email, plan, pedido, fechas, soporte y limite de equipos.
- Refuerza exclusiones de ZIP/auditoria para el issuer y artefactos locales de licencias.
- Documenta la fase M10 para primeras ventas manuales.

## 2026-05-06 - License key management

- Anade `license_keypair.ps1` para generar claves RSA offline compatibles con el firmador interno.
- Documenta M9 con el flujo manual de emision de licencias Pro.
- Refuerza `.gitignore`, empaquetado, auditoria y checklist contra claves privadas/licencias firmadas.
- Actualiza `product_manifest.json` con politica `never_commit_never_ship`.
- Regenera el ZIP portable y valida la API portable con health OK.

## 2026-05-05 - Release polish

- Anade `RELEASE_SQX_EDGE.bat` para ejecutar el checklist de entrega con doble click.
- El checklist puede exigir Git limpio con `-RequireCleanGit`.
- El release genera `dist/SQX_release_summary.txt` con ZIP, fecha, tamano y estado Git.
- El ZIP portable excluye el BAT de release interno para no confundir al usuario final.

## 2026-05-04 - Entrega profesional

Version entregable de SQX Edge Suite v1.

### Incluido

- Diseno `Premium SaaS Dark v2` con fase `Design Pro`.
- Pagina `Inicio` como cockpit operativo por defecto.
- Navegacion visual refinada para desktop y mobile.
- Tab `Estrategias` con eliminacion de cualquier estrategia visible.
- Restauracion de estrategias base eliminadas de la vista.
- Importacion, consolidacion y exportacion de estrategias.
- Project Generator con asistente de arranque y controles visuales refinados.
- Scripts analiticos y endpoints de backup integrados.
- Tests E2E opcionales con Playwright.
- Empaquetado portable con Python embebido.
- Launchers de un click: `START_SQX_EDGE.bat` y `STOP_SQX_EDGE.bat`.

### Verificacion

- Suite normal: `24 passed, 2 skipped`.
- E2E opcional con Playwright: cubre Inicio, Estrategias, eliminar/restaurar y mobile.
- ZIP portable validado en extraccion limpia.
- Runtime portable validado importando `flask` y `api.server`.

### Paquete

El ZIP final se genera en:

```text
dist/SQX_Edge_Tool_Portable_*.zip
```
# 2026-05-07 - Hotfix rollback release kit

- Anade `hotfix_rollback_release.py` para preparar acciones de hotfix, rollback, pausa o cierre.
- Valida owner, incidente, notas, target de rollback, comunicacion a clientes, soporte, verificacion y evidencia de cierre.
- Refuerza empaquetado, auditoria y checklist para excluir la nueva herramienta interna.
- Documenta M44 y el runbook de hotfix/rollback post-release.

# 2026-05-07 - Post release monitor

- Anade `post_release_monitor.py` para decidir mantener, pausar, hotfix, rollback o `scale_public`.
- Valida descargas, ventas, activaciones, tickets, incidencias severas, refunds y fallos de fulfillment.
- Refuerza empaquetado, auditoria y checklist para excluir la nueva herramienta interna.
- Documenta M43 y el runbook de monitorizacion post-release.

# 2026-05-06 - Release publication record

- Anade `release_publication_record.py` para registrar evidencia post-publicacion.
- Valida GitHub Release publicada, tag, ZIP, SHA256 coincidente, descarga probada, soporte y rollback.
- Refuerza empaquetado, auditoria y checklist para excluir la nueva herramienta interna.
- Documenta M42 y el runbook de evidencia de release publicada.

# 2026-05-06 - Public release gate

- Anade `public_release_gate.py` como compuerta final antes de publicar GitHub Release.
- Valida tag, URL HTTPS de release, ZIP adjunto, SHA256 publicado, soporte y rollback.
- Refuerza exclusiones del ZIP portable para la nueva herramienta interna.
- Documenta M41 y el runbook de publicacion controlada.
