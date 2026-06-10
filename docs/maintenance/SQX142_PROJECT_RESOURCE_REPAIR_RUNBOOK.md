# SQX142 Project Resource Repair Runbook

## Purpose

This runbook records the 2026-05-27 repair of local SQX 142 custom projects that showed `Project has unresolved resources` while `checkResources` returned an empty resources payload:

`<Resources><Symbols /><Sessions /></Resources>`

It is for local operator maintenance only. It does not change StrategyQuant engine files, jars, licenses, `data.db`, live databanks or project execution state.

## Final Outcome

Validated in SQX 142 through `project/checkResources`:

- `Capa1_Long_SQX142_Base` -> clean.
- `Capa2_Base_SQX142_Base` -> clean.
- `Mining01_USDJPY_H1_BS_Volatilidad_v6_intraday_v6_LS_Capa2` -> clean control donor.
- `IMOX XAU H1 2025(2)` -> clean control.
- `Retester` -> still unresolved and should be treated as a separate case.

Final verification command suite:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe -m pytest backend\sqx-edge-tool\test_sqx142_project_resource_repair.py
```

Expected result:

```text
15 passed
```

## Root Cause

The Capa2 base red state was not fixed by:

- restoring or blanking missing `templateFile` references;
- rebuilding from a clean Capa2 donor alone;
- changing `USDJPY_darwinex` to `AUDCAD_darwinex`;
- preserving per-task data ranges from the donor.

The final blocker was XML numeric formatting inside `InstrumentInfo`:

- Failing generated format: `tickSize="0.0001"` and `tickStep="1e-05"`.
- SQX-compatible format: `tickSize="1.0E-4"` and `tickStep="1.0E-5"`.

SQX 142 accepted the project only after the repair tool emitted Java-like small-double strings through `_java_double_text`.

## Safe Tooling

Primary wrapper:

```powershell
tools\sqx142_project_resource_repair.ps1 -Action plan
tools\sqx142_project_resource_repair.ps1 -Action rebuild-capa1
tools\sqx142_project_resource_repair.ps1 -Action repair-capa2-config
tools\sqx142_project_resource_repair.ps1 -Action rebuild-capa2
tools\sqx142_project_resource_repair.ps1 -Action rollback -BackupId <backup-id>
```

Important behavior:

- `repair`, `rebuild-capa1`, `repair-capa2-config`, `rebuild-capa2` and `rollback` require SQX closed.
- The wrapper checks for `StrategyQuantX*` processes and stops before mutation.
- The script creates a backup under ignored `.local/sqx142_project_resource_repair/backups/`.
- Rollback restores `project.cfx` from the selected backup.
- The script does not use `Stop-Process`.
- The script does not touch jars, engine binaries, license/activation material, `data.db`, live databanks, `run_project` or Migration Tool.

## Known Backups

Key successful repair backups:

- Capa1 donor rebuild: `sqx142-project-resource-repair-v1_clean-donor-rebuild_20260527_062436`.
- Capa2 final donor rebuild: `sqx142-project-resource-repair-v1_capa2-clean-donor-rebuild_20260527_071920`.

Earlier Capa2 attempts are useful evidence but were not final:

- `repair-capa2-config` cleaned missing `templateFile` values but did not remove the red state.
- Capa2 donor rebuilds before `_java_double_text` still left SQX red.

## Capa1 Repair Pattern

Use when `Capa1_Long_SQX142_Base` is red and `Capa1_Long_SQX142_Base(2)` is confirmed clean:

```powershell
tools\sqx142_project_resource_repair.ps1 -Action rebuild-capa1
```

What it does:

- copies the clean donor `project.cfx`;
- rewrites only the root project name to `Capa1_Long_SQX142_Base`;
- keeps backup/rollback available.

## Capa2 Repair Pattern

Use when `Capa2_Base_SQX142_Base` is red with empty resources XML and the clean donor `Mining01_USDJPY_H1_BS_Volatilidad_v6_intraday_v6_LS_Capa2` is available:

```powershell
tools\sqx142_project_resource_repair.ps1 -Action rebuild-capa2
```

What it does:

- copies the clean Capa2 donor `project.cfx`;
- rewrites the root project name to `Capa2_Base_SQX142_Base`;
- rewrites `USDJPY_darwinex` tokens to `AUDCAD_darwinex`;
- reads local SQX 142 `data.db` in read-only mode for resource metadata;
- preserves donor per-task date ranges when they fit local data availability;
- emits SQX-compatible Java-like small-double strings for `tickSize` and `tickStep`;
- keeps backup/rollback available.

## Verification

After repair:

1. Start SQX 142 normally.
2. Wait for `http://localhost:8080/constants/getAll` to respond.
3. Query `project/checkResources`.

Expected clean state:

```text
hasUnresolvedResources: None
resourcesXML: None
```

If a project still returns:

```text
hasUnresolvedResources: True
resourcesXML: <Resources><Symbols /><Sessions /></Resources>
```

do not keep patching blindly. Compare against a confirmed clean donor and inspect:

- root `config.xml` version and task list;
- task XML `Chart` symbols;
- `Resources/Symbols/Symbol`;
- `InstrumentInfo` numeric formatting;
- broker id/postfix/timezone;
- per-task `dateFrom/dateTo`;
- stale temp ZIP files.

## Operational Boundary

This runbook is local-only. It may repair `user/projects/<project>/project.cfx` only through explicit backup/hash/rollback. It must not be used to:

- modify SQX jars, engine binaries or internal plugins;
- bypass license/activation;
- write `data.db`;
- delete live databanks;
- run projects or retests;
- use Migration Tool;
- claim profitability, risk zero or external certification.
