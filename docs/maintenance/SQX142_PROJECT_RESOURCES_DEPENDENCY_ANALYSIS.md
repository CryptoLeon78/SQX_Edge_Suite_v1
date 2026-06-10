# SQX142 ProjectResources Dependency Analysis

## Scope

This note documents the read-only dependency analysis for `ProjectResources.resolveResources(...)`, the SQX 142 resolver path that produced the broker-null `NullPointerException` during generated custom-project loading.

No SQX jar, executable, license, activation file, `data.db` or live project file is modified by this analysis.

## Target Class

```text
Jar:    internal/libs/SQTradingLib.jar
Class:  com.strategyquant.tradinglib.project.ProjectResources
Method: resolveResources(org.jdom2.Element, org.jdom2.Element, java.util.HashMap, org.json.JSONArray)
```

The jar-level fix blueprint is recorded in:

```text
docs/maintenance/SQX142_PROJECT_RESOURCES_JAR_FIX_NOTES.md
```

## Visible Compile-Time Dependencies

These dependencies are present in `internal/libs` and are enough for many referenced classes:

| Dependency | Provides |
| --- | --- |
| `SQTradingLib.jar` | `ProjectResources`, websocket/project/task helper classes, `SQFileManager`, `StrategyTemplateGenerator` |
| `SQDataLib.jar` | `BrokerDto`, `BrokerManager`, `DataManager`, `InstrumentManager`, `InstrumentInfo`, sessions, baskets |
| `SQGridLib2.jar` | `IGridMessageListener` |
| `SQPluginLib.jar` | `IProgram`, `Program` |
| `jdom.jar` | `org.jdom2.Element`, `org.jdom2.Content` |
| `json.jar` | `org.json.JSONArray`, `org.json.JSONObject` |
| `slf4j-api.jar` | `Logger`, `LoggerFactory` |

## Missing Compile-Time Dependency

`ProjectResources.class` references these `com.strategyquant.lib.*` classes, but they are not present in any visible `.jar` under the inspected SQX 142 or SQX 144 folders:

```text
com.strategyquant.lib.L
com.strategyquant.lib.SQTime
com.strategyquant.lib.SQUtils
com.strategyquant.lib.TaskStoppedException
com.strategyquant.lib.XMLUtil
com.strategyquant.lib.app.MainApp
com.strategyquant.lib.constants.SQConst
com.strategyquant.lib.constants.SQPaths
com.strategyquant.lib.utils.IProgressListener
```

Focused checks for these class files returned `NOT_FOUND`:

```text
com/strategyquant/lib/L.class
com/strategyquant/lib/XMLUtil.class
com/strategyquant/lib/SQTime.class
com/strategyquant/lib/SQUtils.class
com/strategyquant/lib/app/MainApp.class
com/strategyquant/lib/constants/SQPaths.class
```

There is no visible `SQLib.jar` in either checked install tree.

## Interpretation

`SQLib.jar` is not a normal visible dependency in these installs. The `com.strategyquant.lib.*` classes are likely:

- embedded in the packaged launcher/runtime;
- loaded through a non-obvious classloader surface;
- omitted from the redistributed visible `internal/libs` folder;
- or otherwise not exposed as a standalone compilation dependency.

That means a clean source-level rebuild of `ProjectResources.class` outside SQX cannot be treated as a normal `javac -cp internal/libs/*` job unless the missing `com.strategyquant.lib.*` dependency is recovered from an authorized source or represented by lab-only stubs.

## Why Stubs Are Not a Production Fix

Minimal stubs for `L`, `XMLUtil`, `SQTime`, `SQUtils`, `MainApp`, `SQConst`, `SQPaths` and related interfaces could help a local laboratory compile experiment. They would not prove runtime compatibility because `ProjectResources` expects SQX's real behavior for:

- XML attribute parsing and defaults;
- localized messages;
- SQX date parsing;
- app paths and data paths;
- stop/pause handling;
- task/websocket progress integration.

Therefore stubs are useful only for static compilation experiments, not for replacing SQX internals.

## Fix Dependency Summary

The bug itself does not need a large dependency change. The logic change is narrow:

- guard nullable broker map lookups;
- validate replacement broker lookups;
- avoid storing null broker DTOs;
- return controlled resource errors instead of servlet `NullPointerException`.

The compilation problem is separate: the class depends on SQX's hidden or non-public `com.strategyquant.lib.*` layer.

## External Guard We Own

Because the jar-level dependency set is not fully visible, our production-safe mitigation remains external:

```powershell
tools\sqx142_project_load_stabilizer.ps1 -Action plan
tools\sqx142_project_load_stabilizer.ps1 -Action stabilize
```

The stabilizer prevents `.cfx` inputs from entering the known null-broker path by checking broker references before SQX resolver execution.
