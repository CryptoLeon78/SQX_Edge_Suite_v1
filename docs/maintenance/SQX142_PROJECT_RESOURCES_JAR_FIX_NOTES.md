# SQX142 ProjectResources Jar Fix Notes

## Scope



Observed log signature:

```text
ProjectResources - Cannot resolve resources
NullPointerException: Cannot invoke "com.strategyquant.datalib.broker.BrokerDto.getName()" because "<local44>" is null
```

The failing class is `SQTradingLib.jar`, method `com.strategyquant.tradinglib.project.ProjectResources.resolveResources(...)`. `BrokerDto` and `BrokerManager` are provided by `SQDataLib.jar`.

The dependency matrix for compiling or auditing this class is recorded in:

```text
docs/maintenance/SQX142_PROJECT_RESOURCES_DEPENDENCY_ANALYSIS.md
```

## Root Cause

`resolveResources(...)` builds an internal map of broker DTOs from the resource payload, keyed by broker id. Later, when processing symbol resources, it reads the symbol `broker` id and follows this logical flow:

```text
projectBroker = brokersById.get(symbolBrokerId)
liveBroker = BrokerManager.getInstance().getBroker(projectBroker.getName())
resolvedBrokerId = liveBroker.getId()
```

There is no null guard between `brokersById.get(symbolBrokerId)` and `projectBroker.getName()`.

If a symbol says `broker="X"` but the resolver payload does not contain a matching `<Broker id="X" ...>` element, `projectBroker` becomes null and SQX throws `NullPointerException` instead of returning a normal unresolved-resource result.

The same risk exists earlier in the instrument path when an `InstrumentInfo.broker` id is missing from the same broker map.

There is also a likely broker-replacement bug in the same method: the `replace` branch resolves the destination broker by name, but the null check appears to validate the source broker DTO rather than the resolved destination broker DTO. If the destination broker lookup returns null, that null can be stored into the broker map and later surface as the `<local44>` `getName()` crash during symbol processing.

## Correct Jar-Level Fix

The robust fix inside `ProjectResources.resolveResources(...)` is to validate every broker DTO before dereferencing it.

For each broker id read from `InstrumentInfo.broker` or `Symbol.broker`:

1. Look up the broker in the project resolver map.
2. If missing, try a safe fallback through the live broker manager by id.
3. If still missing, stop that resource branch with a controlled unresolved-resource message naming the broker id and symbol/instrument.
4. Never call `BrokerDto.getName()` or `BrokerDto.getId()` on a nullable DTO.

For the broker `replace` action specifically:

1. Resolve the requested replacement broker.
2. Check the replacement broker object for null, not only the source broker object.
3. Store only a non-null broker DTO in the broker map.

Conceptual patch shape:

```text
BrokerDto projectBroker = brokersById.get(resourceBrokerId);
if (projectBroker == null) {
    projectBroker = BrokerManager.getInstance().getBroker(resourceBrokerId);
}
if (projectBroker == null) {
    throw controlled resource exception:
      "Broker id <id> used by symbol/instrument <name> is missing from project resources and local broker catalog."
}

BrokerDto liveBroker = BrokerManager.getInstance().getBroker(projectBroker.getName());
if (liveBroker == null) {
    throw controlled resource exception:
      "Broker <name> from project resources is missing from local broker catalog."
}
```

Conceptual `replace` branch guard:

```text
BrokerDto replacementBroker = BrokerManager.getInstance().getBroker(replaceBrokerName);
if (replacementBroker == null) {
    throw controlled resource exception:
      "Replace broker <name> does not exist in local broker catalog."
}
brokersById.put(sourceBroker.getId(), replacementBroker);
```

The resolver should then return a user-actionable unresolved-resource payload instead of crashing the servlet.

## External Preventive Guard

Until SQX itself is fixed, generated `.cfx` projects must obey this invariant:

```text
Every <Symbol broker="X"> and every <InstrumentInfo broker="X"> must have a matching <Resources><Brokers><Broker id="X" .../></Brokers></Resources> entry, and that broker id/name must exist in local SQX data.db.
```

Our guard for this lives in:

```text
tools/sqx142_project_load_stabilizer.ps1 -Action plan
```

It flags:

- `resource_broker_not_declared_in_cfx_entry`
- `resource_broker_missing_from_data_db`
- `instrument_broker_missing_from_data_db`

Those are the external warning signs for the jar-side `ProjectResources.resolveResources` null path.
