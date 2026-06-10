# SQX142 Project Load Stabilizer Runbook

## Purpose

This runbook records the guarded workaround for SQX 142 custom projects that alternate `Project has unresolved resources` after loading two otherwise clean generated `.cfx` projects.

The observed SQX behavior on 2026-05-27 was:

- Capa1 loaded clean.
- Capa2 loaded clean.
- After both existed in `user/projects`, SQX moved the red unresolved state from one project row to the other when `Load config using these settings` was pressed.
- Local disk inspection showed clean project XML, but SQX logs contained resolver failures and previous `Failed to update zip content` errors while `project.cfx` was locked.

## Tool

```powershell
tools\sqx142_project_load_stabilizer.ps1 -Action status
tools\sqx142_project_load_stabilizer.ps1 -Action plan
tools\sqx142_project_load_stabilizer.ps1 -Action stabilize
tools\sqx142_project_load_stabilizer.ps1 -Action clear-ui-cache
tools\sqx142_project_load_stabilizer.ps1 -Action rollback -BackupId <backup-id>
```

Default projects:

- `Mining15_AUDCAD_H1_BS_Momentum_v6_Capa1`
- `Mining15_AUDCAD_H1_BS_Momentum_v6_Capa2`

Use `-Project <name>` to target a different generated custom project.

## Safety Boundary

`stabilize` and `rollback` require SQX closed. The wrapper checks for `StrategyQuantX*` and `SQX*` processes and aborts if any are running.

The tool may only:

- inspect `user/projects/<project>/project.cfx`;
- move stale `zipfstmp*.tmp` files inside the targeted project folder into backup;
- repack `project.cfx` with identical entry content to clear stale ZIP transaction state;
- move Electron HTTP cache into ignored local backup when stale `/project/checkResources` responses keep the project row red after project files are clean;
- write rollback evidence under ignored `.local/sqx142_project_load_stabilizer/backups/`.

It must not touch jars, plugins, license/activation, `user/data`, `data.db`, live databank contents, `run_project` or Migration Tool.

Use `clear-ui-cache` only after:

1. `plan` reports no project findings or stale ZIP temp files.
2. SQX is closed.
3. The latest SQX log shows no fresh resolver error after restart, but the UI still shows stale red resource state.

## Acceptance

After `stabilize`:

1. Open SQX 142.
2. Confirm both generated projects load without the red unresolved resource alternation.
3. If SQX still alternates red status, do not keep clicking resolver buttons. Capture logs and run `-Action plan` again.
4. If the files are clean and only the browser cache is suspect, close SQX and run `-Action clear-ui-cache`, then reopen SQX to force a fresh resource check.

## Jar Root-Cause Note

The sanitized jar-level fix blueprint is recorded in:

```text
docs/maintenance/SQX142_PROJECT_RESOURCES_JAR_FIX_NOTES.md
```

Short version: `ProjectResources.resolveResources(...)` dereferences a nullable `BrokerDto` when a symbol/instrument broker id is missing from the resolver broker map. SQX should guard that lookup, try a broker-manager fallback by id, and return a controlled unresolved-resource error instead of throwing `NullPointerException`.

Verification:

```powershell
python -m pytest backend\sqx-edge-tool\test_sqx142_project_load_stabilizer.py
```
