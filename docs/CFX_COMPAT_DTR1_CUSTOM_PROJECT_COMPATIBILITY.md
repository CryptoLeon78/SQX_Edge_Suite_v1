# CFX-COMPAT-DTR1 - Custom Project Compatibility Review

## Summary

This phase documents the cross-host `.cfx` compatibility issue found while comparing a tester-supplied project with a SQX Edge generated project.

The finding is not that one machine is right and the other is wrong. The real issue is that `.cfx` projects are host-sensitive: symbols, data providers, broker ids, sessions, precision, timezone, available date ranges and even absolute StrategyType paths can bind a project to the SQX installation where it was created.

## Local Diagnostic Inputs

The raw files live only in `material de diagnostico/customs_varios_daniel/` and must not be committed.

Sanitized comparison:

- Tester project profile: `sq_equity_data_subscription_bound`.
- SQX Edge generated sample profile: older generated artifact with Darwinex profile plus a malformed Dukascopy retest resource in one task.
- Fresh SQX Edge generation from current code: `sqx_edge_cross_broker_oos2`, no stale resource sessions, no non-`No Session` `MarketOpenSession`, no mixed chart/resource symbols and no unresolved placeholders.

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

The diagnostic sample in the local folder is not representative of the current generator output. It still showed one task with mixed resource shape: the Retest 1 chart wanted Dukascopy, but resource metadata inherited Darwinex broker/source values.

Freshly generated `.cfx` files now pass without fail-level issues. They intentionally carry a Dukascopy warning because Retest 1/OOS2 is a methodology requirement, not a stale dependency.

## Decision

Add `cfx-compatibility-audit-v1` as a reusable compatibility audit before accepting external `.cfx` evidence or diagnosing user-generated `.cfx` files.

The audit does not mutate files. It classifies:

- unresolved placeholder symbols;
- SQ Equity Data subscription dependencies;
- intended Dukascopy OOS2 dependencies versus unintended legacy source dependencies;
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

For the remote service model, generation continues to target the server SQX host by default, but CFX-TARGET1 introduces an explicit target SQX profile selector for recipients whose local SQX does not use Darwinex-compatible symbols.

For downloaded `.cfx` files opened in a user's own SQX, the target profile must match the recipient's Data Manager where possible. Retest 1/OOS2 still remains Dukascopy 2010.01.01-2017.10.02 by design, because it validates cross-broker survival before IS Mining.

## Next Recommendation

After CFX-TARGET1, the next step is to collect one target profile from a non-Darwinex tester and validate that primary project resources remap while Retest 1/OOS2 remains coherent on Dukascopy.
