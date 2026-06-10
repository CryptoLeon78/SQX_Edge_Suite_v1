# BS-AI18 RetDD TICK REAL Methodology Observation

Marker: `bs-ai18-retdd-tick-real-methodology-observation-v1`

Current status: `methodology_observation_no_running_project_mutation_no_capa2`

## Scope

This note reviews whether `ReturnDDRatio` / RetDD should be a hard `TICK REAL` metric while the BS-AI18 Capa1 run is active.

It is a read-only methodology observation. It does not change the running SQX project, the imported `.cfx`, any databank, any pass state, any BSAI candidate, any official BlockSettings v6/v7 file or the official manifest.

## Repo Truth

The operator question is valid, but the exact artifact evidence is more nuanced than "RetDD is absent from every previous retest":

- In the current BS-AI16 Capa1 artifact, RetDD appears as a soft earlier main retest filter at `ReturnDDRatio >= 1.2`.
- In `TICK REAL`, RetDD appears as a hard main filter at `ReturnDDRatio >= 4`.
- Several other retest/build stages do not use RetDD as the main pass/fail metric; they mainly use trades, PF, expectancy, RExpectancy, net profit or robustness-specific checks.
- BS-AI16 did not introduce a new RetDD policy. It preserved PF, WinningPct and ReturnDDRatio while changing the TICK REAL trade-count rule from the BS-AI15 warning into the preregistered `120 / 65%` rule.
- Older tracked Capa2 methodology also contains a RetDD ladder: lower RetDD checks before final TICK and a stricter RetDD check in TICK.

Therefore the concern is not "RetDD appears from nowhere"; the concern is asymmetric calibration: a soft/sparse RetDD use before TICK versus a hard final `ReturnDDRatio >= 4` in precision data. This is not a proven failure cause.

## Academic Read

Adding a fresh hard metric only at the final validation stage is poor hygiene unless it was preregistered. It increases researcher degrees of freedom and can turn a validation/holdout step into an additional selection step.

Backtest-overfitting literature supports this caution: Bailey, Borwein, Lopez de Prado and Zhu frame investment backtests as especially prone to overfitting and propose estimating the probability of backtest overfitting; Bailey and Lopez de Prado's Deflated Sharpe Ratio work explicitly addresses selection bias under multiple testing; White's Reality Check warns about repeated use of the same data for model selection; and Magdon-Ismail and Atiya show maximum drawdown is a path-sensitive risk measure used in ratios such as Calmar-like measures.

For SQX Edge, RetDD is useful, but it must be either:

- a preregistered quality gate with a consistent role across the validation chain, or
- a diagnostic/reporting metric in TICK when the earlier chain did not select on it consistently.

## BS-AI18 Decision

For the active BS-AI18 run:

- Do not change the running project.
- Do not remove or relax `ReturnDDRatio >= 4`.
- Do not force pass.
- Do not start Capa2.
- Do not treat RetDD as a proven failure cause unless the post-run evidence explicitly shows it.
- If the run fails at RetDD, classify it as `retdd_asymmetric_final_gate_warning_no_capa2`, not as a reason to rescue the candidate.

Current interpretation:

`ReturnDDRatio >= 4` is a preserved hard final precision-data filter in the BS-AI16 artifact. It is methodologically defensible only if treated as preregistered/preserved, not as a post-hoc response to the BS-AI14/BS-AI15 failure.

## Next Experiment Design Options

Preferred next clean designs:

1. Diagnostic-only RetDD in TICK.
   Use RetDD for reporting in final real tick, but keep pass/fail aligned to the metrics preregistered throughout Capa1.

2. Explicit RetDD ladder.
   Predefine a RetDD progression across Build/retests/TICK, with the final threshold justified as stricter precision-data quality control.

3. Relative RetDD retention.
   Use a rule shaped like `realTickRetDD >= max(absoluteFloor, priorValidationRetDD * retentionRatio)` only if the prior RetDD source is stable and available before TICK.

No option may reinterpret the active BS-AI18 run after the fact. Any RetDD policy change belongs to a future preregistered experiment.

## Guardrails

- No Capa2.
- No Start / Stop action from this note.
- No import.
- No `taskmanager/openProject`.
- No `loadAsIs`.
- No Add missing symbols.
- No resource-resolution bypass.
- No direct `data.db` patch.
- No direct `user/projects` patch.
- No databank mutation.
- No Migration Tool.
- No BSAI promotion.
- No official v6/v7 overwrite.
- No 144.2953 promotion.

## References

- Bailey, Borwein, Lopez de Prado and Zhu, "The Probability of Backtest Overfitting", SSRN: https://ssrn.com/abstract=2326253
- Bailey and Lopez de Prado, "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality", SSRN: https://ssrn.com/abstract=2460551
- White, "A Reality Check for Data Snooping", Econometrica 68(5), 1097-1126: https://doi.org/10.1111/1468-0262.00152
- Magdon-Ismail and Atiya, "Maximum Drawdown", Risk Magazine, October 2004: https://ssrn.com/abstract=874069
