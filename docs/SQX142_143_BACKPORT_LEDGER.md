# SQX142-143 Backport Ledger

## Summary

This is the master compatibility ledger for stabilizing local `SQX 142` against the local `SQX 143` reference while keeping StrategyQuant engine binaries, license files and crack/bypass behavior out of scope.

Reference sources:

- Local reference build: `SQX_143\SQX_143` on the operator machine.
- Official Build 143 notes: <https://strategyquant.com/whatsnew/?date=2026-1>.
- Official Build 144 notes: <https://strategyquant.com/whatsnew/?date=2026-5>.
- Public task tracker: <https://roadmap.strategyquant.com/projects/sq4/tasks>.

## Current Findings

| Area | Evidence | Backport Decision | Status |
| --- | --- | --- | --- |
| Java runtime | SQX 142 used Oracle/GraalVM 25; SQX 143 uses Azul Zulu 22. | Align SQX 142 runtime to the 143 `j64` runtime with backup and smoke. | Applied by `tools/sqx142_compatibility.ps1`. |
| Launcher config | SQX 142 forced `-Xmx70g`; SQX 143 uses `-Xms4g` and `--enable-native-access=ALL-UNNAMED`. | Apply the 143 runtime config shape to SQX 142 root configs, not to user settings. | Applied by `tools/sqx142_compatibility.ps1`. |
| MonteCarlo retest snippets | 142 and 143 internal MonteCarlo retest snippets hash-identical. | Do not copy these snippets as a fix; keep the repaired Monkey/Synthetic views and filters. | Documented and preserved. |
| `internal\extend` delta | 548 changed files and 15 files only in 143, mostly blocks/templates/MM/stats/columns. | Candidate pool only; copy single artifacts only after a bug-specific diff and smoke. | Candidate. |
| Plugins/libs/engine | Many plugin/lib differences exist. | No bulk copy and no engine/bin/license patching. | Blocked unless a later bug-specific phase proves safety. |
| SQX process locks | SQX/Electron processes can keep cache files locked. | Preflight must close or block before runtime/cache changes. | Enforced by compatibility tool. |

## Applied Record

- `2026-05-22 16:31` - Runtime/config hardening applied with `tools\sqx142_compatibility.ps1 apply-runtime --apply --close-processes`.
- Backup folder: `SQX_142_Crack_local_backups\sqx142_compat_before_20260522_163115`.
- Result: SQX 142 now reports Zulu 22.32+15, config shape matches SQX 143, `-Xmx70g` is removed, `--enable-native-access=ALL-UNNAMED` is present and process preflight is clear.
- Smoke: `StrategyQuantX_nocheck.exe` starts and writes `Starting StrategyQuant` / `Invoking main class` to the launcher log with the new runtime; controlled close leaves zero SQX 142 processes and no `hs_err_pid*.log` in the SQX root.

## Operator Commands

Dry-run status:

```powershell
tools\sqx142_compatibility.ps1 status
```

Compare extensible files:

```powershell
tools\sqx142_compatibility.ps1 compare
```

Dry-run runtime/config hardening:

```powershell
tools\sqx142_compatibility.ps1 apply-runtime
```

Apply runtime/config hardening with process close and backup:

```powershell
tools\sqx142_compatibility.ps1 apply-runtime --apply --close-processes
```

Rollback is manual from the generated backup folder under `SQX_142_Crack_local_backups`.

## Acceptance

- `/api/sqx142/compat/status` is local-operator-only and returns no local paths.
- `/api/agent/status` includes `sqx142Compat` only for local operator context.
- Remote tester sessions never see the SQX compatibility monitor or local paths.
- The local operator monitor shows Backend, Tunnel, Ollama and SQX 142 compatibility state.
- A future bug-specific backport must cite this ledger row, source evidence, copied files, backup folder and smoke result.
