# CFX-COMPAT-DTR1 - Custom Project Compatibility Review

## Summary

This phase documents the cross-host `.cfx` compatibility issue found while comparing a tester-supplied project with a SQX Edge generated project.

The finding is not that one machine is right and the other is wrong. The real issue is that `.cfx` projects are host-sensitive: symbols, data providers, broker ids, sessions, precision, timezone, available date ranges and even absolute StrategyType paths can bind a project to the SQX installation where it was created.

## Local Diagnostic Inputs

The raw files live only in `material de diagnostico/customs_varios_daniel/` and must not be committed.

Sanitized comparison:

- Tester project profile: `sq_equity_data_subscription_bound`.
- SQX Edge generated sample profile: older generated artifact with Darwinex profile plus a stale/mixed retest resource in one task.
- Fresh SQX Edge generation from current code: `sqx142_darwinex`, no stale resource sessions, no non-`No Session` `MarketOpenSession`, no mixed chart/resource symbols and no unresolved placeholders.

## Findings

### Tester-supplied project

The tester project depends on a SQX Equity Data placeholder symbol and an unbound broker profile. On a machine without the same subscription/resources, SQX reports unresolved resources and can block project start.

Sanitized indicators:

- unresolved placeholder symbol;
- SQ Equity Data source profile;
- broker `-1`;
- no active Darwinex broker table for the chart;
- non-SQX Edge precision/timezone profile;
- source-machine paths in StrategyType attributes.

### SQX Edge generated diagnostic sample

The diagnostic sample in the local folder is not representative of the current generator output. It still showed one task with mixed resource shape: chart/source/session state from a different provider while most tasks were Darwinex/TICK/EETUS.

Freshly generated `.cfx` files now pass the full internal compatibility audit.

## Decision

Add `cfx-compatibility-audit-v1` as a reusable compatibility audit before accepting external `.cfx` evidence or diagnosing user-generated `.cfx` files.

The audit does not mutate files. It classifies:

- unresolved placeholder symbols;
- SQ Equity Data subscription dependencies;
- Dukascopy or other legacy source dependencies;
- broker/resource mismatches;
- stale sessions;
- non-`No Session` `MarketOpenSession`;
- chart symbols missing from `Resources/Symbols`;
- embedded strategy symbol mismatches;
- non-TICK precision or non-EETUS timezone;
- source-machine paths in StrategyType attributes.

## Operator Usage

Run locally against diagnostic files:

```powershell
python backend\sqx-edge-tool\tools\cfx_compatibility_audit.py "material de diagnostico\customs_varios_daniel\IMOX XAU H1 2025(2).cfx"
```

JSON mode:

```powershell
python backend\sqx-edge-tool\tools\cfx_compatibility_audit.py --json "<path-to-cfx>"
```

The exit code is `0` when all audited files pass, `1` when at least one file has a fail-level issue and `2` when the input file is missing.

## Product Implication

For the remote service model, generation must continue to target the server SQX host unless a future phase explicitly introduces a user-target compatibility profile.

For downloaded `.cfx` files opened in a user's own SQX, a future phase should collect the target host profile or warn that local symbols/data subscriptions may differ. A single hardcoded `.cfx` cannot be universally loadable across different SQX installations when their Data Manager resources differ.

## Next Recommendation

Implement a future `CFX-TARGET1` phase before broader buyer usage:

- expose an operator-only compatibility profile selector;
- record target source/broker/timezone/precision assumptions;
- run `cfx-compatibility-audit-v1` before download;
- optionally add a repair/remap flow for external `.cfx` imports when the target host profile is known.
