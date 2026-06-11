# SQX144 CUSTOM RESULTS4 Original Separate Install Correction

Status: `custom_results4_original_separate_plugins_installed_copy_only_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool`

Marker: `sqx144-custom-results4-original-separate-install-correction-v1`

Date: 2026-06-11

## Purpose

CUSTOM-RESULTS4 corrects the previous all-modules bundle install. The operator rejected the aggregated `SQX Edge Custom Results All Modules` tab and required the official StrategyQuant Results Plugin pattern: each downloaded Custom Result is installed unmodified as its own folder under `sqx144_full/user/extend/ResultsPlugins`, producing one Results tab per plugin.

## Applied Correction

SQX was verified closed before apply with `processCount=0`.

Removed from ResultsPlugins and moved to backup:

- `SQX Edge Custom Results All Modules`

Installed original plugin folders unmodified:

- `2-Step Challenge Analyzer`
- `Edge Decay & Max Loss Analyzer`
- `OOSDegradationScorecard`
- `RobustnessScorecard`
- `WinRateEdge`

Each installed folder has `index.html` and source hash equals target hash after copy.

## Non-ResultsPlugin Package

`RandomEntries-1.htm` was not installed into ResultsPlugins. It is a ZIP-like snippet package containing `extend/Code/.../blocks/RandomEntry.tpl` and `extend/Snippets/SQ/Blocks/RandomEntry/RandomEntry.java`, not a Custom Result Results tab.

## Evidence

Ignored local evidence:

- `.local/sqx144_custom_results4/sqx144_custom_results4_apply_20260611_105026.json`

Backup reference:

- `sqx144_full/.local_code_backups/sqx144_custom_results4_original_separate_install_20260611_105026`

## Boundaries

- No SQX runtime launch.
- No `data.db` mutation.
- No `user/projects` mutation.
- No databank mutation.
- No SQX tasks.
- No Migration Tool.
- No source-code access/export.
