from __future__ import annotations

import argparse
import csv
import gzip
import http.cookiejar
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.sqx_compatibility import SQX142_DEFAULT_ROOT, SQX143_DEFAULT_ROOT, build_sqx142_status  # noqa: E402
from core.sqx_performance import (  # noqa: E402
    EVIDENCE_DIRNAME,
    PERFORMANCE_VERSION,
    PROFILE_CONFIGS,
    build_sqx142_performance_status,
    latest_launcher_events,
    performance_view_payloads,
)


RUNTIME_CONFIG_FILES = ("StrategyQuantX_nocheck.config", "sqcli.config", "CodeEditor.config")
DEFAULT_REAL_PROJECT_NAME = "Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1"
MC_DATABANK_VIEW_TARGETS = {
    "Monkey Test": "MC MONKEY RETEST",
    "Syntetic": "MC SYNTHETIC RETEST",
}
PHASE5_DATABANK_VIEW_TARGETS = {
    "Results": "MINING FAST REVIEW",
    "Initial population": "MINING FAST REVIEW",
    "Last generation": "MINING FAST REVIEW",
    "Strategies to improve": "MINING FAST REVIEW",
    "Strategies to optimize": "MINING FAST REVIEW",
    "RETEST 0": "RETEST QUICK REVIEW",
    "retest 1": "RETEST QUICK REVIEW",
    "TICK": "RETEST ROBUST REVIEW",
    "MC": "RETEST ROBUST REVIEW",
    "MC2": "RETEST ROBUST REVIEW",
    "Sequential": "RETEST ROBUST REVIEW",
    "Monkey Test": "MC MONKEY RETEST",
    "Syntetic": "MC SYNTHETIC RETEST",
    "SPP": "RETEST ROBUST REVIEW",
    "WFM": "RETEST ROBUST REVIEW",
    "Foward": "RETEST QUICK REVIEW",
}
PHASE5_ARCHIVE_VIEW_CANDIDATES = {
    "todas las metricas posibles": "oversized_all_metrics_view_replaced_by_review_views",
    "PROPIA": "legacy_heavy_tick_view_replaced_by_retest_robust_review",
    "MONTECARLO RETEST": "legacy_generic_mc_view_replaced_by_dedicated_mc_views",
    "MONTECARLO TRADES": "legacy_generic_mc_view_replaced_by_dedicated_mc_views",
    "ROBUSTEZ": "legacy_generic_robustness_view_replaced_by_retest_robust_review",
}
PHASE5_HEAVY_COLUMN_CLASSES = {"MiniEquityChart", "EntryIndicators", "ExitIndicators", "PriceIndicators"}
OPERATOR_OMITTED_RETEST_TITLES = {"SPP", "FOWARD"}
OPERATOR_OMITTED_DATABANKS = {"SPP", "Foward"}


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def json_print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def evidence_root(project_root: Path) -> Path:
    return project_root / EVIDENCE_DIRNAME


def write_evidence(project_root: Path, filename: str, payload: dict[str, Any]) -> Path:
    root = evidence_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    requested = root / filename
    content = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    for attempt in range(20):
        target = requested if attempt == 0 else requested.with_name(f"{requested.stem}_{attempt}{requested.suffix}")
        tmp = target.with_name(f".{target.name}.{os.getpid()}.{time.time_ns()}.tmp")
        tmp.write_text(content, encoding="utf-8")
        try:
            tmp.replace(target)
            return target
        except PermissionError:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
            time.sleep(0.05)
    raise PermissionError(str(requested))


def config_text_for_profile(profile_id: str) -> str:
    profile = PROFILE_CONFIGS.get(profile_id)
    if not profile:
        raise KeyError(profile_id)
    return "\n".join(profile["lines"]).strip() + "\n"


def atomic_write_text(target: Path, text: str) -> None:
    tmp = target.with_suffix(target.suffix + f".{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(target)


def sqx_processes_running(root142: Path, root143: Path = SQX143_DEFAULT_ROOT) -> bool:
    status = build_sqx142_status(root142, root143, include_paths=False)
    return bool((status.get("processes") or {}).get("running"))


def backup_files(root142: Path, backup_dir: Path, files: list[Path], *, apply: bool) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for source in files:
        try:
            rel = source.relative_to(root142)
        except ValueError:
            rel = Path(source.name)
        target = backup_dir / rel
        item = {"source": str(rel), "exists": source.exists(), "backup": str(target), "copied": False}
        if source.exists() and apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            item["copied"] = True
            item["bytes"] = source.stat().st_size
        actions.append(item)
    return actions


def apply_profile(project_root: Path, root142: Path, root143: Path, profile_id: str, *, apply: bool) -> dict[str, Any]:
    if profile_id not in PROFILE_CONFIGS:
        return {
            "ok": False,
            "version": "sqx142-performance-profile-v1",
            "error": "unknown_profile",
            "availableProfiles": sorted(PROFILE_CONFIGS),
        }
    before = build_sqx142_performance_status(project_root, root142, root143, include_paths=True)
    running = bool(((before.get("compatibility") or {}).get("status") == "blocked") or sqx_processes_running(root142, root143))
    if apply and running:
        return {
            "ok": False,
            "version": "sqx142-performance-profile-v1",
            "dryRun": False,
            "error": "sqx_processes_running",
            "message": "Close SQX 142 before applying JVM profiles.",
            "before": before,
        }

    backup_dir = root142.parent / "SQX_142_Crack_local_backups" / f"sqx142_perf_profile_before_{stamp()}"
    config_files = [root142 / name for name in RUNTIME_CONFIG_FILES]
    backup_actions = backup_files(root142, backup_dir, config_files, apply=apply)
    desired = config_text_for_profile(profile_id)
    writes = []
    if apply:
        backup_dir.mkdir(parents=True, exist_ok=True)
    for target in config_files:
        writes.append({"target": target.name, "apply": apply, "bytes": len(desired.encode("utf-8"))})
        if apply:
            atomic_write_text(target, desired)
    after = build_sqx142_performance_status(project_root, root142, root143, include_paths=True)
    payload = {
        "ok": True,
        "version": "sqx142-performance-profile-v1",
        "dryRun": not apply,
        "profile": profile_id,
        "qualityReductionAllowed": False,
        "backupRoot": str(backup_dir) if apply else str(backup_dir) + " (planned)",
        "backup": backup_actions,
        "writes": writes,
        "before": before,
        "after": after,
    }
    if apply:
        write_evidence(project_root, f"profile_{profile_id}_{stamp()}.json", payload)
    return payload


def create_views(project_root: Path, root142: Path, root143: Path, *, apply: bool, replace: bool) -> dict[str, Any]:
    view_root = root142 / "user" / "settings" / "views" / "databanks"
    view_root.mkdir(parents=True, exist_ok=True) if apply else None
    payloads = performance_view_payloads()
    backup_dir = root142.parent / "SQX_142_Crack_local_backups" / f"sqx142_perf_views_before_{stamp()}"
    actions: list[dict[str, Any]] = []
    existing_to_backup: list[Path] = []
    for name, xml in payloads.items():
        target = view_root / f"{name}.vw"
        exists = target.exists()
        will_write = apply and (replace or not exists)
        if exists and replace:
            existing_to_backup.append(target)
        actions.append({
            "view": name,
            "target": target.name,
            "exists": exists,
            "replace": replace,
            "willWrite": will_write,
            "columns": xml.count("<Column "),
        })
    backups = backup_files(root142, backup_dir, existing_to_backup, apply=apply) if existing_to_backup else []
    if apply:
        if existing_to_backup:
            backup_dir.mkdir(parents=True, exist_ok=True)
        for name, xml in payloads.items():
            target = view_root / f"{name}.vw"
            if target.exists() and not replace:
                continue
            target.write_text(xml, encoding="utf-8")
    after = build_sqx142_performance_status(project_root, root142, root143, include_paths=True)
    payload = {
        "ok": True,
        "version": "sqx142-performance-views-v1",
        "dryRun": not apply,
        "replace": replace,
        "qualityReductionAllowed": False,
        "backupRoot": str(backup_dir) if apply and existing_to_backup else "",
        "backup": backups,
        "actions": actions,
        "after": after,
    }
    if apply:
        write_evidence(project_root, f"views_{stamp()}.json", payload)
    return payload


def cleanup_plan(project_root: Path, root142: Path, root143: Path) -> dict[str, Any]:
    status = build_sqx142_performance_status(project_root, root142, root143, include_paths=True)
    directories = status.get("directories") if isinstance(status.get("directories"), dict) else {}
    candidates = []
    for key in ("logs", "electronCache", "projects"):
        info = directories.get(key) if isinstance(directories.get(key), dict) else {}
        candidates.append({
            "area": key,
            "exists": bool(info.get("exists")),
            "files": info.get("files", 0),
            "human": info.get("human", ""),
            "mode": "archive_or_backup_first",
            "deleteAllowed": False,
        })
    return {
        "ok": True,
        "version": "sqx142-performance-cleanup-plan-v1",
        "dryRun": True,
        "qualityReductionAllowed": False,
        "cleanupIsReversibleOnly": True,
        "candidates": candidates,
        "warnings": status.get("warnings", []),
    }


def _directory_totals(path: Path) -> dict[str, Any]:
    files = 0
    dirs = 0
    total_bytes = 0
    newest = 0.0
    if not path.is_dir():
        return {"files": 0, "dirs": 0, "bytes": 0, "human": "0.0 MB", "newestModified": ""}
    for item in path.rglob("*"):
        try:
            stat = item.stat()
        except OSError:
            continue
        newest = max(newest, stat.st_mtime)
        if item.is_dir():
            dirs += 1
        elif item.is_file():
            files += 1
            total_bytes += stat.st_size
    return {
        "files": files,
        "dirs": dirs,
        "bytes": total_bytes,
        "human": f"{total_bytes / 1024 / 1024:.1f} MB",
        "newestModified": datetime.fromtimestamp(newest).isoformat(timespec="seconds") if newest else "",
    }


def _performance_clone_role(name: str) -> str:
    if "POSTPROMO" in name:
        return "post_promotion_smoke"
    if "SEQBATCH_B" in name:
        return "sequential_full_batch"
    if "SEQDIAG" in name:
        return "sequential_diagnostic"
    if "MC2SPREAD" in name:
        return "mc2_spread_diagnostic"
    if name.startswith("_PERFQ_Mining"):
        return "performance_project_clone"
    return "performance_clone"


def performance_clone_hygiene(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    keep_newest: int,
    apply: bool,
    include_paths: bool,
) -> dict[str, Any]:
    projects_root = root142 / "user" / "projects"
    archive_root = root142.parent / "SQX_142_Crack_local_backups" / "archived_perf_projects" / stamp()
    clones = sorted(
        [path for path in projects_root.glob("_PERFQ_*") if path.is_dir()],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    ) if projects_root.is_dir() else []
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-performance-clone-hygiene-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "cleanupIsReversibleOnly": True,
        "projectsRootExists": projects_root.is_dir(),
        "keepNewest": keep_newest,
        "archiveRoot": str(archive_root) if include_paths or apply else archive_root.name,
        "rules": [
            "Dry-run by default.",
            "Applies by moving old _PERFQ_* projects to SQX_142_Crack_local_backups, never deleting them.",
            "Newest clones are kept active for post-promotion smoke/rollback context.",
            "SQX must be closed before moving project folders.",
        ],
        "clones": [],
        "summary": {},
    }
    keep_newest = max(0, keep_newest)
    archive_candidates: list[Path] = []
    for index, path in enumerate(clones, start=1):
        totals = _directory_totals(path)
        action = "keep_active" if index <= keep_newest else "archive_reversible"
        if action == "archive_reversible":
            archive_candidates.append(path)
        row = {
            "name": path.name,
            "role": _performance_clone_role(path.name),
            "rankNewest": index,
            "action": action,
            **totals,
        }
        if include_paths:
            row["path"] = str(path)
            row["archiveTarget"] = str(archive_root / path.name)
        payload["clones"].append(row)

    payload["summary"] = {
        "totalClones": len(clones),
        "keepActive": min(len(clones), keep_newest),
        "archiveCandidates": len(archive_candidates),
        "activeCloneBytes": sum(int(row.get("bytes") or 0) for row in payload["clones"]),
        "archiveCandidateBytes": sum(
            int(row.get("bytes") or 0)
            for row in payload["clones"]
            if row.get("action") == "archive_reversible"
        ),
    }
    payload["summary"]["activeCloneHuman"] = f"{payload['summary']['activeCloneBytes'] / 1024 / 1024:.1f} MB"
    payload["summary"]["archiveCandidateHuman"] = f"{payload['summary']['archiveCandidateBytes'] / 1024 / 1024:.1f} MB"

    if apply:
        if sqx_processes_running(root142, root143):
            payload["error"] = "sqx_processes_running"
            written = write_evidence(project_root, f"performance_clone_hygiene_blocked_{stamp()}.json", payload)
            payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
            return payload
        projects_root_resolved = projects_root.resolve()
        archive_root.mkdir(parents=True, exist_ok=True)
        archive_root_resolved = archive_root.resolve()
        moved = []
        for source in archive_candidates:
            source_resolved = source.resolve()
            target = archive_root / source.name
            target_resolved = target.resolve(strict=False)
            if projects_root_resolved not in source_resolved.parents:
                moved.append({"name": source.name, "moved": False, "error": "source_outside_projects_root"})
                continue
            if archive_root_resolved != target_resolved.parent:
                moved.append({"name": source.name, "moved": False, "error": "target_outside_archive_root"})
                continue
            shutil.move(str(source), str(target))
            moved.append({"name": source.name, "moved": True, "target": str(target) if include_paths else target.name})
        payload["moved"] = moved
        payload["ok"] = all(item.get("moved") for item in moved) if moved else True
    else:
        payload["ok"] = True
        payload["message"] = "Dry-run only. Re-run with --apply to move archive candidates reversibly."

    written = write_evidence(project_root, f"performance_clone_hygiene_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
    return payload


def _archived_perf_projects_root(root142: Path) -> Path:
    return root142.parent / "SQX_142_Crack_local_backups" / "archived_perf_projects"


def _public_path(path: Path, *, include_paths: bool) -> str:
    return str(path) if include_paths else path.name


def restore_performance_clone(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    clone_name: str,
    archive_stamp: str,
    archive_existing_active: bool,
    apply: bool,
    include_paths: bool,
) -> dict[str, Any]:
    projects_root = root142 / "user" / "projects"
    archive_parent = _archived_perf_projects_root(root142)
    replacement_root = root142.parent / "SQX_142_Crack_local_backups" / "active_perf_project_replaced" / stamp()
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-performance-clone-restore-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "cleanupIsReversibleOnly": True,
        "cloneName": clone_name,
        "archiveStamp": archive_stamp or "",
        "archiveExistingActive": archive_existing_active,
        "projectsRootExists": projects_root.is_dir(),
        "archiveRootExists": archive_parent.is_dir(),
        "rules": [
            "Dry-run by default.",
            "Restores exactly one archived _PERFQ_* project clone back into SQX user/projects.",
            "SQX must be closed before moving project folders.",
            "An existing active clone is never overwritten; with --archive-existing-active it is moved to backup first.",
        ],
        "matches": [],
        "plannedMoves": [],
    }
    if not clone_name.startswith("_PERFQ_"):
        payload["error"] = "invalid_clone_name"
        payload["message"] = "Only archived performance clones whose name starts with _PERFQ_ can be restored."
        written = write_evidence(project_root, f"performance_clone_restore_blocked_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
        return payload

    archive_roots: list[Path] = []
    if archive_stamp:
        archive_roots = [archive_parent / archive_stamp]
    elif archive_parent.is_dir():
        archive_roots = sorted(
            [path for path in archive_parent.iterdir() if path.is_dir()],
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

    matches = []
    for root in archive_roots:
        source = root / clone_name
        if source.is_dir():
            match = {
                "archiveStamp": root.name,
                "name": clone_name,
                "role": _performance_clone_role(clone_name),
                **_directory_totals(source),
            }
            if include_paths:
                match["path"] = str(source)
            matches.append((root, source, match))
            payload["matches"].append(match)

    if not matches:
        payload["error"] = "archived_clone_not_found"
        payload["message"] = "No archived clone with that name was found under archived_perf_projects."
        written = write_evidence(project_root, f"performance_clone_restore_blocked_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
        return payload
    if len(matches) > 1 and not archive_stamp:
        payload["error"] = "ambiguous_archived_clone"
        payload["message"] = "The clone exists in more than one archive stamp. Re-run with --archive-stamp."
        written = write_evidence(project_root, f"performance_clone_restore_blocked_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
        return payload

    archive_root, source, _match = matches[0]
    destination = projects_root / clone_name
    destination_exists = destination.exists()
    source_display = str(source) if include_paths else f"{archive_root.name}/{source.name}"
    destination_display = _public_path(destination, include_paths=include_paths)
    replacement_display = (
        str(replacement_root / clone_name)
        if include_paths
        else f"{replacement_root.name}/{clone_name}"
    )
    payload["selected"] = {
        "archiveStamp": archive_root.name,
        "source": source_display,
        "destination": destination_display,
        "destinationExists": destination_exists,
        "restoreTarget": "user/projects",
    }
    if destination_exists and not archive_existing_active:
        payload["error"] = "active_clone_already_exists"
        payload["message"] = "An active clone with that name already exists. Use --archive-existing-active to move it aside first."
        written = write_evidence(project_root, f"performance_clone_restore_blocked_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
        return payload

    if destination_exists:
        payload["plannedMoves"].append({
            "action": "archive_existing_active",
            "source": destination_display,
            "target": replacement_display,
        })
    payload["plannedMoves"].append({
        "action": "restore_archived_clone",
        "source": source_display,
        "target": destination_display,
    })

    if apply:
        if sqx_processes_running(root142, root143):
            payload["error"] = "sqx_processes_running"
            written = write_evidence(project_root, f"performance_clone_restore_blocked_{stamp()}.json", payload)
            payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
            return payload
        projects_root.mkdir(parents=True, exist_ok=True)
        archive_parent_resolved = archive_parent.resolve()
        projects_root_resolved = projects_root.resolve()
        source_resolved = source.resolve()
        destination_resolved = destination.resolve(strict=False)
        if archive_parent_resolved not in source_resolved.parents:
            payload["error"] = "source_outside_archive_root"
            written = write_evidence(project_root, f"performance_clone_restore_blocked_{stamp()}.json", payload)
            payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
            return payload
        if destination_resolved.parent != projects_root_resolved:
            payload["error"] = "destination_outside_projects_root"
            written = write_evidence(project_root, f"performance_clone_restore_blocked_{stamp()}.json", payload)
            payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
            return payload

        moved = []
        if destination.exists():
            replacement_root.mkdir(parents=True, exist_ok=True)
            replacement_target = replacement_root / clone_name
            shutil.move(str(destination), str(replacement_target))
            moved.append({
                "action": "archive_existing_active",
                "moved": True,
                "target": _public_path(replacement_target, include_paths=include_paths),
            })
        shutil.move(str(source), str(destination))
        moved.append({
            "action": "restore_archived_clone",
            "moved": True,
            "target": _public_path(destination, include_paths=include_paths),
        })
        payload["moved"] = moved
        payload["ok"] = True
    else:
        payload["ok"] = True
        payload["message"] = "Dry-run only. Re-run with --apply to restore the selected archived clone."

    written = write_evidence(project_root, f"performance_clone_restore_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
    return payload


def _latest_evidence_brief(project_root: Path, prefix: str) -> dict[str, Any]:
    selected = _latest_evidence_file(project_root, prefix)
    if not selected or not selected.is_file():
        return {"prefix": prefix, "exists": False}
    result: dict[str, Any] = {
        "prefix": prefix,
        "exists": True,
        "filename": selected.name,
        "modified": datetime.fromtimestamp(selected.stat().st_mtime).isoformat(timespec="seconds"),
    }
    try:
        data = json.loads(selected.read_text(encoding="utf-8"))
        result["ok"] = bool(data.get("ok"))
        result["version"] = data.get("version", "")
        if isinstance(data.get("summary"), dict):
            result["summary"] = data["summary"]
    except (OSError, json.JSONDecodeError):
        result["ok"] = False
        result["error"] = "unreadable_evidence"
    return result


def performance_closeout_report(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    include_paths: bool,
) -> dict[str, Any]:
    status = build_sqx142_performance_status(project_root, root142, root143, include_paths=False)
    projects_root = root142 / "user" / "projects"
    archive_parent = _archived_perf_projects_root(root142)
    active_clones = []
    if projects_root.is_dir():
        for path in sorted(projects_root.glob("_PERFQ_*"), key=lambda item: item.stat().st_mtime, reverse=True):
            row = {
                "name": path.name,
                "role": _performance_clone_role(path.name),
                **_directory_totals(path),
            }
            if include_paths:
                row["path"] = str(path)
            active_clones.append(row)

    archive_batches = []
    if archive_parent.is_dir():
        for archive_root in sorted([path for path in archive_parent.iterdir() if path.is_dir()], key=lambda item: item.stat().st_mtime, reverse=True):
            clones = [path for path in archive_root.glob("_PERFQ_*") if path.is_dir()]
            total_bytes = sum(_directory_totals(path).get("bytes", 0) for path in clones)
            row = {
                "archiveStamp": archive_root.name,
                "cloneCount": len(clones),
                "bytes": total_bytes,
                "human": f"{total_bytes / 1024 / 1024:.1f} MB",
                "cloneNames": [path.name for path in clones],
            }
            if include_paths:
                row["path"] = str(archive_root)
            archive_batches.append(row)

    evidence_prefixes = [
        "mc_project_views",
        "mining_pipeline_advisor",
        "phase5_databank_view_guard",
        "old_log_archive",
        "profile_compare",
        "queue_task_smoke",
        "sequential_final_review",
        "mc2_spread_promotion",
        "performance_clone_hygiene",
        "performance_clone_restore",
        "performance_parallelism_advisor",
        "performance_live_guard",
    ]
    payload: dict[str, Any] = {
        "ok": bool(status.get("ok")),
        "version": "sqx142-performance-closeout-report-v1",
        "dryRun": True,
        "qualityReductionAllowed": False,
        "status": {
            "ok": bool(status.get("ok")),
            "state": status.get("status"),
            "warnings": status.get("warnings", []),
            "activeProfile": (status.get("activeProfile") or {}).get("id"),
            "disk": (status.get("resources") or {}).get("disk", {}),
            "latestEvidence": status.get("latestEvidence", {}),
        },
        "activePerformanceClones": active_clones,
        "archivedPerformanceCloneBatches": archive_batches,
        "keyEvidence": [_latest_evidence_brief(project_root, prefix) for prefix in evidence_prefixes],
        "operatorDecisions": {
            "omittedRetests": sorted(OPERATOR_OMITTED_RETEST_TITLES),
            "mc2SpreadPolicy": "adaptive_base_spread_x2_to_x5",
            "doNotChangeTaskIndividualValuesYet": True,
        },
        "deferredOperatorQuestion": {
            "when": "after_sqx142_performance_optimization_closeout",
            "question": (
                "Que enfoque quieres para configurar los valores individuales de las tareas "
                "de los custom base Capa1 y Capa2?"
            ),
            "rule": "Ask Ivan before editing individual task values in Capa1/Capa2 custom base projects.",
        },
        "nextRecommendedActions": [
            "Mantener SPP/FOWARD fuera de optimizacion salvo decision nueva.",
            "Usar restore-performance-clone solo para inspeccionar lotes archivados.",
            "Cerrar rendimiento cuando status este ok, evidencias clave existan y no haya procesos SQX colgados.",
        ],
        "privacy": {"local_paths_returned": include_paths},
    }
    written = write_evidence(project_root, f"performance_closeout_report_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
    return payload


def performance_next_action(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    include_paths: bool,
) -> dict[str, Any]:
    status = build_sqx142_performance_status(project_root, root142, root143, include_paths=False)
    evidence = {
        prefix: _latest_evidence_brief(project_root, prefix)
        for prefix in (
            "profile_compare",
            "mining_pipeline_advisor",
            "mc_project_views",
            "phase5_databank_view_guard",
            "old_log_archive",
            "sequential_final_review",
            "mc2_spread_promotion",
            "queue_task_smoke",
            "performance_clone_hygiene",
            "performance_parallelism_advisor",
            "performance_live_guard",
            "performance_closeout_report",
        )
    }
    active_profile = str((status.get("activeProfile") or {}).get("id") or "")
    warnings = [str(item) for item in (status.get("warnings") or [])]
    missing_or_bad = [key for key, item in evidence.items() if not (item.get("exists") and item.get("ok"))]

    recommendation = {
        "id": "ready_for_perf1_closeout",
        "label": "PERF1 esta listo para cierre operativo",
        "command": "tools\\sqx142_performance_gate.ps1 performance-closeout-report",
        "reason": "Status ok, evidencias clave presentes y perfil baseline restaurado.",
        "requiresSQXClosed": False,
        "requiresMethodologyDecision": False,
    }
    if warnings:
        recommendation = {
            "id": "fix_status_warnings",
            "label": "Resolver warnings del performance gate",
            "command": "tools\\sqx142_performance_gate.ps1 status --include-paths",
            "reason": "El status no esta limpio; no conviene avanzar con optimizacion hasta corregirlo.",
            "requiresSQXClosed": False,
            "requiresMethodologyDecision": False,
        }
    elif active_profile != "baseline_143_safe":
        recommendation = {
            "id": "restore_baseline_profile",
            "label": "Restaurar perfil baseline_143_safe",
            "command": "tools\\sqx142_performance_gate.ps1 apply-profile baseline_143_safe --apply",
            "reason": "El perfil default debe quedar estable cuando no hay smoke activo.",
            "requiresSQXClosed": True,
            "requiresMethodologyDecision": False,
        }
    elif missing_or_bad:
        first = missing_or_bad[0]
        command_by_prefix = {
            "profile_compare": "tools\\sqx142_performance_gate.ps1 compare-profiles baseline_143_safe diagnostic_low_risk retest_robust mining_fast_safe --apply --wait-seconds 18 --restore-profile baseline_143_safe",
            "mining_pipeline_advisor": "tools\\sqx142_performance_gate.ps1 project-mining-pipeline-advisor",
            "mc_project_views": "tools\\sqx142_performance_gate.ps1 prepare-project-mc-views --apply",
            "phase5_databank_view_guard": "tools\\sqx142_performance_gate.ps1 phase5-databank-view-guard",
            "old_log_archive": "tools\\sqx142_performance_gate.ps1 archive-old-logs --keep-days 2 --apply",
            "sequential_final_review": "tools\\sqx142_performance_gate.ps1 sequential-final-review --latest --write-csv --apply",
            "mc2_spread_promotion": "tools\\sqx142_performance_gate.ps1 promote-mc2-spread-to-base --project-name \"Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1\" --min-multiplier 2 --max-multiplier 5",
            "queue_task_smoke": "tools\\sqx142_performance_gate.ps1 queue-task-smoke \"Sequential\" --project-name \"_PERFQ_SEQBATCH_POSTPROMO8_20260523_080012\" --apply --max-seconds 900",
            "performance_clone_hygiene": "tools\\sqx142_performance_gate.ps1 performance-clone-hygiene --keep-newest 2",
            "performance_parallelism_advisor": "tools\\sqx142_performance_gate.ps1 performance-parallelism-advisor",
            "performance_live_guard": "tools\\sqx142_performance_gate.ps1 live-guard",
            "performance_closeout_report": "tools\\sqx142_performance_gate.ps1 performance-closeout-report",
        }
        recommendation = {
            "id": f"refresh_{first}",
            "label": f"Refrescar evidencia {first}",
            "command": command_by_prefix.get(first, "tools\\sqx142_performance_gate.ps1 performance-closeout-report"),
            "reason": "Falta una evidencia clave o la ultima no esta ok.",
            "requiresSQXClosed": first in {"profile_compare", "mc_project_views", "phase5_databank_view_guard", "old_log_archive", "performance_clone_hygiene", "performance_live_guard"},
            "requiresMethodologyDecision": first == "mc2_spread_promotion",
        }

    complete = (
        not warnings
        and active_profile == "baseline_143_safe"
        and not missing_or_bad
        and bool(status.get("ok"))
    )
    payload: dict[str, Any] = {
        "ok": True,
        "version": "sqx142-performance-next-action-v1",
        "dryRun": True,
        "qualityReductionAllowed": False,
        "completeEnoughForPerf1Closeout": complete,
        "status": {
            "ok": bool(status.get("ok")),
            "state": status.get("status"),
            "warnings": warnings,
            "activeProfile": active_profile,
            "latestEvidence": status.get("latestEvidence", {}),
        },
        "evidence": evidence,
        "missingOrBadEvidence": missing_or_bad,
        "recommendation": recommendation,
        "deferredOperatorQuestion": {
            "active": complete,
            "question": "Que enfoque quieres para configurar los valores individuales de las tareas de los custom base Capa1 y Capa2?",
            "rule": "Do not edit individual Capa1/Capa2 task values before asking Ivan after performance closeout.",
        },
        "privacy": {"local_paths_returned": include_paths},
    }
    if include_paths:
        payload["roots"] = {
            "sqx142Root": str(root142),
            "evidenceRoot": str(evidence_root(project_root)),
        }
    written = write_evidence(project_root, f"performance_next_action_{stamp()}.json", payload)
    payload["reportEvidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
    return payload


def _profile_xmx_gb(profile_id: str) -> int | None:
    profile = PROFILE_CONFIGS.get(profile_id) or {}
    for line in profile.get("lines", []):
        match = re.search(r"-Xmx(\d+)[gG]", str(line))
        if match:
            return int(match.group(1))
    return None


def _sqx_settings_resource_snapshot(root142: Path) -> dict[str, Any]:
    settings = root142 / "user" / "settings" / "settings.xml"
    watched = (
        "memoryCleanup",
        "memoryCleanupInterval",
        "GCType",
        "parallelDownload",
        "cdnParallelDownload",
        "syncDatabanksAfterTaskDone",
        "threadAffinity",
        "memoryProtection",
        "storeChartData",
        "dontStorePendingOrders",
    )
    payload: dict[str, Any] = {"exists": settings.is_file(), "values": {}}
    if not settings.is_file():
        return payload
    try:
        root = ET.parse(settings).getroot()
    except (OSError, ET.ParseError) as exc:
        payload["error"] = type(exc).__name__
        return payload
    for tag in watched:
        value = root.findtext(tag)
        if value is not None:
            payload["values"][tag] = value
    return payload


def _latest_queue_smokes_by_task(project_root: Path) -> dict[str, Any]:
    root = evidence_root(project_root)
    if not root.is_dir():
        return {}
    records: dict[str, Any] = {}
    for path in sorted(root.glob("queue_task_smoke_*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        task = str(data.get("taskTitle") or ((data.get("task") or {}).get("title") if isinstance(data.get("task"), dict) else "") or "")
        if not task or task in records:
            continue
        after_databank = data.get("afterDatabank") if isinstance(data.get("afterDatabank"), dict) else {}
        latest_log = {}
        after_log = data.get("afterLogSummary") if isinstance(data.get("afterLogSummary"), dict) else {}
        by_task = after_log.get("byTask") if isinstance(after_log.get("byTask"), dict) else {}
        task_bucket = by_task.get(task) if isinstance(by_task.get(task), dict) else {}
        if isinstance(task_bucket.get("latest"), dict):
            latest_log = task_bucket["latest"]
        records[task] = {
            "filename": path.name,
            "ok": bool(data.get("ok")),
            "outcome": data.get("outcome", ""),
            "elapsedSeconds": data.get("elapsedSeconds"),
            "afterFiles": after_databank.get("strategyFiles"),
            "passed": latest_log.get("passed"),
            "failed": latest_log.get("failed"),
            "durationText": latest_log.get("durationText", ""),
            "timePerStrategy": latest_log.get("timePerStrategy", ""),
            "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
        }
    return records


def performance_parallelism_advisor(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    include_paths: bool,
) -> dict[str, Any]:
    status = build_sqx142_performance_status(project_root, root142, root143, include_paths=False)
    resources = status.get("resources") if isinstance(status.get("resources"), dict) else {}
    memory = resources.get("memory") if isinstance(resources.get("memory"), dict) else {}
    disk = resources.get("disk") if isinstance(resources.get("disk"), dict) else {}
    cpu = resources.get("cpu") if isinstance(resources.get("cpu"), dict) else {}
    free_memory_gb = round(float(memory.get("freeBytes") or 0) / 1024**3, 1)
    logical = int(cpu.get("logicalPerSocket") or 0)
    free_disk_gb = round(float(disk.get("freeBytes") or 0) / 1024**3, 1)
    settings = _sqx_settings_resource_snapshot(root142)
    smokes = _latest_queue_smokes_by_task(project_root)

    profiles = {
        "ui_diagnostic": {
            "profile": "diagnostic_low_risk",
            "xmxGb": _profile_xmx_gb("diagnostic_low_risk"),
            "maxParallelSQXInstances": 1,
            "maxHeavyRetestsAtOnce": 0,
            "useFor": ["status checks", "UI/API smoke", "short diagnostics"],
            "rules": ["No mining or heavy retests in this profile."],
        },
        "retest_stability": {
            "profile": "retest_robust",
            "xmxGb": _profile_xmx_gb("retest_robust"),
            "maxParallelSQXInstances": 1,
            "maxHeavyRetestsAtOnce": 1,
            "useFor": ["MC", "MC 2", "Monkey Test", "Synthetic", "Sequential batches"],
            "rules": [
                "Run MC/Monkey/Synthetic/Sequential alone until a dedicated parallel smoke proves otherwise.",
                "Snapshot databank before/after and verify natural passed/failed.",
            ],
        },
        "mining_cpu_heavy": {
            "profile": "mining_fast_safe",
            "xmxGb": _profile_xmx_gb("mining_fast_safe"),
            "maxParallelSQXInstances": 1,
            "maxHeavyRetestsAtOnce": 0,
            "useFor": ["short controlled mining smoke", "future mining pipeline tests"],
            "rules": [
                "Prefer one SQX mining project at a time; tune internal project workload only after measuring.",
                "Do not mix mining with MonteCarlo/Synthetic/Sequential on the same host.",
            ],
        },
        "sequential_batch_queue": {
            "profile": "retest_robust",
            "xmxGb": _profile_xmx_gb("retest_robust"),
            "batchSize": "24+24+24+12 validated for 84 MC2 survivors",
            "maxParallelBatches": 1,
            "useFor": ["Sequential Optimization"],
            "rules": ["Sequential writes late; judge by ProgressEngine plus final databank coverage."],
        },
    }

    warnings: list[str] = []
    if status.get("warnings"):
        warnings.append("status_not_clean")
    if free_disk_gb < 100:
        warnings.append("disk_below_parallelism_recommended_floor")
    if free_memory_gb < 64:
        warnings.append("memory_headroom_low_for_heavy_parallelism")

    payload: dict[str, Any] = {
        "ok": not warnings,
        "version": "sqx142-performance-parallelism-advisor-v1",
        "dryRun": True,
        "qualityReductionAllowed": False,
        "status": {
            "ok": bool(status.get("ok")),
            "state": status.get("status"),
            "warnings": status.get("warnings", []),
            "activeProfile": (status.get("activeProfile") or {}).get("id"),
        },
        "resourceSnapshot": {
            "logicalPerSocket": logical,
            "freeMemoryGb": free_memory_gb,
            "freeDiskGb": free_disk_gb,
            "diskState": disk.get("state", ""),
        },
        "settingsSnapshot": settings,
        "validatedSmokesByTask": smokes,
        "parallelismProfiles": profiles,
        "globalPolicy": {
            "defaultMaxConcurrentSQXProjects": 1,
            "allowParallelHeavyRetests": False,
            "allowMiningWhileRetesting": False,
            "reason": "Real evidence favors stability/persistence; no parallel smoke has proven a better crash/time tradeoff yet.",
        },
        "nextSafeExperiment": {
            "id": "mining_short_single_run_baseline",
            "label": "Medir minado corto controlado en single-run antes de tocar paralelismo",
            "profile": "mining_fast_safe",
            "command": "tools\\sqx142_performance_gate.ps1 apply-profile mining_fast_safe --apply",
            "requiresSQXClosed": True,
            "notes": [
                "Create or use a disposable _PERFQ_* mining clone.",
                "Run one short mining task only.",
                "Compare duration, outputs, logs and process cleanup against baseline.",
            ],
        },
        "warnings": warnings,
        "privacy": {"local_paths_returned": include_paths},
    }
    if include_paths:
        payload["roots"] = {"sqx142Root": str(root142), "evidenceRoot": str(evidence_root(project_root))}
    written = write_evidence(project_root, f"performance_parallelism_advisor_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
    return payload


def _old_log_candidates(root142: Path, *, keep_days: int) -> tuple[datetime, list[Path]]:
    cutoff = (datetime.now() - timedelta(days=max(0, keep_days - 1))).replace(hour=0, minute=0, second=0, microsecond=0)
    roots = [
        root142 / "user" / "log",
        root142 / "user" / "projects",
    ]
    candidates: list[Path] = []
    for base in roots:
        if not base.is_dir():
            continue
        for path in base.rglob("*.log"):
            try:
                if datetime.fromtimestamp(path.stat().st_mtime) < cutoff:
                    candidates.append(path)
            except OSError:
                continue
    return cutoff, sorted(set(candidates), key=lambda item: str(item).lower())


def archive_old_logs(project_root: Path, root142: Path, *, keep_days: int, apply: bool) -> dict[str, Any]:
    cutoff, candidates = _old_log_candidates(root142, keep_days=keep_days)
    total_bytes = sum(path.stat().st_size for path in candidates if path.is_file())
    archive_root = root142.parent / "SQX_142_Crack_local_backups" / "archived_logs"
    archive_name = f"sqx142_logs_before_{cutoff.strftime('%Y%m%d')}_{stamp()}.zip"
    archive_path = archive_root / archive_name
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-old-log-archive-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "keepDays": keep_days,
        "cutoffLocal": cutoff.isoformat(timespec="seconds"),
        "candidates": len(candidates),
        "bytes": total_bytes,
        "human": f"{total_bytes / 1024 / 1024:.1f} MB",
        "archive": str(archive_path),
        "deleteAllowed": False,
        "sample": [str(path.relative_to(root142)) for path in candidates[:30]],
    }
    if not candidates:
        payload["ok"] = True
        payload["message"] = "No old .log files found."
        return payload
    if not apply:
        payload["message"] = "Dry-run only. Re-run with --apply to zip old logs and remove originals after archive verification."
        return payload
    if sqx_processes_running(root142):
        payload["error"] = "sqx_processes_running"
        write_evidence(project_root, f"old_log_archive_failed_{stamp()}.json", payload)
        return payload

    archive_root.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for path in candidates:
                if path.is_file():
                    zf.write(path, arcname=str(path.relative_to(root142)))
        with zipfile.ZipFile(archive_path, "r") as zf:
            bad_member = zf.testzip()
        if bad_member is not None:
            payload["error"] = "archive_verification_failed"
            payload["badMember"] = bad_member
            write_evidence(project_root, f"old_log_archive_failed_{stamp()}.json", payload)
            return payload
        removed = []
        for path in candidates:
            try:
                size = path.stat().st_size
                path.unlink()
                removed.append({"file": str(path.relative_to(root142)), "bytes": size})
            except OSError as exc:
                payload.setdefault("removeErrors", []).append({"file": str(path.relative_to(root142)), "error": type(exc).__name__})
        payload["removed"] = len(removed)
        payload["removedBytes"] = sum(item["bytes"] for item in removed)
        payload["archiveBytes"] = archive_path.stat().st_size
        payload["archiveVerified"] = True
        payload["deleteAllowed"] = True
        payload["ok"] = not payload.get("removeErrors")
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        payload["error"] = type(exc).__name__
        payload["ok"] = False
    written = write_evidence(project_root, f"old_log_archive_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def performance_live_guard(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    keep_days: int,
    apply: bool,
) -> dict[str, Any]:
    before = build_sqx142_performance_status(project_root, root142, root143, include_paths=False)
    intelligence = before.get("intelligence") if isinstance(before.get("intelligence"), dict) else {}
    live_guard = intelligence.get("liveGuard") if isinstance(intelligence.get("liveGuard"), dict) else {}
    sqx_running = bool(live_guard.get("sqxProcessDetected"))
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-performance-live-guard-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "mode": "observe_when_open_repair_when_closed",
        "safePolicy": {
            "whileSQXOpen": "observe_only",
            "onOpen": "preflight_warning_only",
            "onClose": "safe_repair_after_processes_are_closed",
            "dryRunByDefault": True,
        },
        "before": {
            "ok": before.get("ok"),
            "status": before.get("status"),
            "warnings": before.get("warnings", []),
            "activeProfile": (before.get("activeProfile") or {}).get("id"),
            "liveGuard": live_guard,
        },
        "plannedActions": live_guard.get("repairPlan", []),
        "appliedActions": [],
        "privacy": {"local_paths_returned": False},
    }
    if apply and sqx_running:
        payload["error"] = "sqx_processes_running"
        payload["message"] = "Live Guard only observes while SQX is open. Close SQX before safe repair."
        written = write_evidence(project_root, f"performance_live_guard_blocked_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
        return payload

    if apply:
        profile_id = str(((before.get("activeProfile") or {}).get("id")) or "")
        config_health = before.get("configHealth") if isinstance(before.get("configHealth"), dict) else {}
        if profile_id != "baseline_143_safe" or config_health.get("corrupt") or config_health.get("mismatched"):
            profile_result = apply_profile(project_root, root142, root143, "baseline_143_safe", apply=True)
            payload["appliedActions"].append({
                "id": "restore_baseline_profile_after_close",
                "ok": bool(profile_result.get("ok")),
                "profile": "baseline_143_safe",
            })
        logs_result = archive_old_logs(project_root, root142, keep_days=keep_days, apply=True)
        payload["appliedActions"].append({
            "id": "archive_old_logs_after_close",
            "ok": bool(logs_result.get("ok")),
            "candidates": logs_result.get("candidates", 0),
            "human": logs_result.get("human", ""),
            "evidence": (logs_result.get("evidence") or {}).get("filename", ""),
        })

    after = build_sqx142_performance_status(project_root, root142, root143, include_paths=False)
    after_live_guard = ((after.get("intelligence") or {}).get("liveGuard") or {}) if isinstance(after.get("intelligence"), dict) else {}
    payload["after"] = {
        "ok": after.get("ok"),
        "status": after.get("status"),
        "warnings": after.get("warnings", []),
        "activeProfile": (after.get("activeProfile") or {}).get("id"),
        "liveGuard": after_live_guard,
    }
    payload["ok"] = bool(after.get("ok")) and not bool(after_live_guard.get("sqxProcessDetected"))
    if after_live_guard.get("alerts"):
        payload["ok"] = False
        payload["message"] = "Live Guard still has alerts; review before closing PERF1."
    elif not apply:
        payload["ok"] = True
        payload["message"] = "Dry-run Live Guard completed. Re-run with --apply after SQX is closed for safe repairs."
    else:
        payload["message"] = "Post-close Live Guard repair completed."
    written = write_evidence(project_root, f"performance_live_guard_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def close_sqx_processes(root142: Path) -> dict[str, Any]:
    if os.name != "nt":
        return {"attempted": False, "reason": "non_windows"}
    root = str(root142).replace("'", "''")
    root_forward = str(root142).replace("\\", "/").replace("'", "''")
    script = (
        "$root='" + root + "'; "
        "$rootForward='" + root_forward + "'; "
        "$procs = @(Get-CimInstance Win32_Process | Where-Object { "
        "$_.CommandLine -and ($_.CommandLine -like ('*' + $root + '*') -or $_.CommandLine -like ('*' + $rootForward + '*')) -and "
        "$_.Name -match 'StrategyQuant|sqcli|CodeEditor|javaw?|electron|SQUANT' }); "
        "$rows = @($procs | Select-Object Name,ProcessId); "
        "$rows | ForEach-Object { Stop-Process -Id $_.ProcessId -ErrorAction SilentlyContinue }; "
        "Start-Sleep -Seconds 4; "
        "$left = @(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and ($_.CommandLine -like ('*' + $root + '*') -or $_.CommandLine -like ('*' + $rootForward + '*')) -and $_.Name -match 'StrategyQuant|sqcli|CodeEditor|javaw?|electron|SQUANT' }); "
        "$left | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }; "
        "Start-Sleep -Seconds 2; "
        "$after = @(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and ($_.CommandLine -like ('*' + $root + '*') -or $_.CommandLine -like ('*' + $rootForward + '*')) -and $_.Name -match 'StrategyQuant|sqcli|CodeEditor|javaw?|electron|SQUANT' }); "
        "[pscustomobject]@{matched=$rows;leftBeforeForce=$left.Count;leftAfterForce=$after.Count} | ConvertTo-Json -Compress"
    )
    proc = subprocess.run(["powershell.exe", "-NoProfile", "-Command", script], capture_output=True, text=True, timeout=20, check=False)
    raw = (proc.stdout or "").strip()
    try:
        parsed = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        parsed = {}
    return {"attempted": True, "result": parsed, "stderr": (proc.stderr or "").strip()[:500]}


def smoke_start(project_root: Path, root142: Path, root143: Path, *, apply: bool, wait_seconds: int) -> dict[str, Any]:
    before = build_sqx142_performance_status(project_root, root142, root143, include_paths=True)
    launcher = root142 / "StrategyQuantX_nocheck.exe"
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-performance-smoke-v1",
        "dryRun": not apply,
        "waitSeconds": wait_seconds,
        "qualityReductionAllowed": False,
        "before": before,
        "launcherExists": launcher.is_file(),
    }
    if not apply:
        payload["message"] = "Dry-run only. Re-run with --apply to launch SQX 142 smoke."
        return payload
    if not launcher.is_file():
        payload["error"] = "launcher_missing"
        write_evidence(project_root, f"smoke_failed_{stamp()}.json", payload)
        return payload
    if sqx_processes_running(root142, root143):
        payload["error"] = "sqx_processes_running"
        write_evidence(project_root, f"smoke_failed_{stamp()}.json", payload)
        return payload

    started_at = time.perf_counter()
    proc = subprocess.Popen([str(launcher)], cwd=str(root142))  # noqa: S603
    time.sleep(max(5, wait_seconds))
    elapsed = round(time.perf_counter() - started_at, 2)
    after_launch = build_sqx142_performance_status(project_root, root142, root143, include_paths=True)
    hs_err = sorted(root142.glob("hs_err_pid*.log"), key=lambda path: path.stat().st_mtime, reverse=True)
    close_result = close_sqx_processes(root142)
    after_close = build_sqx142_performance_status(project_root, root142, root143, include_paths=True)
    payload.update({
        "ok": not bool(hs_err) and not bool(((after_close.get("compatibility") or {}).get("status") == "blocked")),
        "pid": proc.pid,
        "elapsedSeconds": elapsed,
        "afterLaunch": after_launch,
        "launcherEvents": latest_launcher_events(root142, limit=20),
        "hsErrCount": len(hs_err),
        "hsErrLatest": hs_err[0].name if hs_err else "",
        "close": close_result,
        "afterClose": after_close,
    })
    write_evidence(project_root, f"smoke_{stamp()}.json", payload)
    return payload


def compare_profiles(
    project_root: Path,
    root142: Path,
    root143: Path,
    profiles: list[str],
    *,
    apply: bool,
    wait_seconds: int,
    restore_profile: str | None,
) -> dict[str, Any]:
    before = build_sqx142_performance_status(project_root, root142, root143, include_paths=True)
    initial_profile = ((before.get("activeProfile") or {}).get("id") or "").strip()
    restore_target = restore_profile or (initial_profile if initial_profile in PROFILE_CONFIGS else "baseline_143_safe")
    invalid = [profile for profile in profiles if profile not in PROFILE_CONFIGS]
    if invalid:
        return {
            "ok": False,
            "version": "sqx142-performance-profile-comparison-v1",
            "error": "unknown_profile",
            "invalidProfiles": invalid,
            "availableProfiles": sorted(PROFILE_CONFIGS),
        }
    if restore_target not in PROFILE_CONFIGS:
        return {
            "ok": False,
            "version": "sqx142-performance-profile-comparison-v1",
            "error": "unknown_restore_profile",
            "restoreProfile": restore_target,
            "availableProfiles": sorted(PROFILE_CONFIGS),
        }
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-performance-profile-comparison-v1",
        "dryRun": not apply,
        "profiles": profiles,
        "restoreProfile": restore_target,
        "waitSeconds": wait_seconds,
        "qualityReductionAllowed": False,
        "before": before,
        "results": [],
        "restored": None,
    }
    if not apply:
        payload["message"] = "Dry-run only. Re-run with --apply to apply profiles, launch SQX smokes and restore the target profile."
        return payload
    if sqx_processes_running(root142, root143):
        payload["error"] = "sqx_processes_running"
        write_evidence(project_root, f"profile_compare_failed_{stamp()}.json", payload)
        return payload

    try:
        for profile in profiles:
            apply_result = apply_profile(project_root, root142, root143, profile, apply=True)
            smoke_result = smoke_start(project_root, root142, root143, apply=True, wait_seconds=wait_seconds)
            result = {
                "profile": profile,
                "applyOk": bool(apply_result.get("ok")),
                "smokeOk": bool(smoke_result.get("ok")),
                "elapsedSeconds": smoke_result.get("elapsedSeconds"),
                "hsErrCount": smoke_result.get("hsErrCount"),
                "close": smoke_result.get("close"),
                "warningsAfterClose": ((smoke_result.get("afterClose") or {}).get("warnings") or [])[:10],
                "memoryAfterLaunch": (((smoke_result.get("afterLaunch") or {}).get("resources") or {}).get("memory") or {}),
            }
            payload["results"].append(result)
    finally:
        payload["restored"] = apply_profile(project_root, root142, root143, restore_target, apply=True)

    after = build_sqx142_performance_status(project_root, root142, root143, include_paths=True)
    payload["after"] = after
    payload["ok"] = all(item.get("applyOk") and item.get("smokeOk") for item in payload["results"]) and (
        ((after.get("activeProfile") or {}).get("id") == restore_target)
    )
    write_evidence(project_root, f"profile_compare_{stamp()}.json", payload)
    return payload


def resolve_sqx_project(root142: Path, sqx_project: Path | None, project_name: str | None) -> Path:
    if sqx_project:
        return sqx_project
    name = project_name or DEFAULT_REAL_PROJECT_NAME
    return root142 / "user" / "projects" / name


def _safe_zip_text(zip_file: zipfile.ZipFile, name: str) -> str:
    try:
        return zip_file.read(name).decode("utf-8", errors="ignore")
    except (KeyError, OSError, UnicodeDecodeError, zipfile.BadZipFile):
        return ""


def _parse_xml_text(text: str) -> ET.Element | None:
    if not text.strip():
        return None
    try:
        return ET.fromstring(text)
    except ET.ParseError:
        return None


def _classify_filter_result(reason: str) -> str:
    value = reason.strip()
    if not value:
        return "missing"
    if value.lower() == "passed":
        return "passed"
    return "failed"


def _short_reason(reason: str, limit: int = 180) -> str:
    compact = " ".join(reason.split())
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def _read_strategy_mc_summary(path: Path) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "file": path.name,
        "bytes": path.stat().st_size,
        "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
        "ok": False,
        "isZip": False,
    }
    try:
        with zipfile.ZipFile(path) as zf:
            summary["isZip"] = True
            names = set(zf.namelist())
            settings_root = _parse_xml_text(_safe_zip_text(zf, "settings.xml"))
            if settings_root is not None:
                reason = settings_root.findtext(".//FiltersResultFailedReason") or ""
                summary["filterResult"] = _classify_filter_result(reason)
                summary["filterReason"] = _short_reason(reason)
                values = settings_root.find(".//ValuesMap")
                if values is not None:
                    available = [child.tag for child in values if not child.tag.startswith("stats_")]
                    summary["availableResultFields"] = sorted(set(available))[:30]
                    summary["settingsSimulations"] = settings_root.findtext(".//MonteCarloRetest_NumberOfSimulations") or ""
            result_files = [name for name in names if name.endswith("MonteCarloRetest_Results.xml")]
            summary["hasMonteCarloResults"] = bool(result_files)
            if result_files:
                result_root = _parse_xml_text(_safe_zip_text(zf, result_files[0]))
                if result_root is not None:
                    summary["resultXml"] = result_files[0]
                    summary["simulations"] = result_root.findtext("NumberOfSimulations") or ""
                    summary["symbol"] = result_root.findtext("Symbol") or ""
                    summary["timeframe"] = result_root.findtext("TimeFrame") or ""
                    summary["dateRange"] = result_root.findtext("DateRange") or ""
                    summary["methods"] = [
                        " ".join((method.text or "").split())
                        for method in result_root.findall(".//Method")
                        if (method.text or "").strip()
                    ][:10]
            summary["ok"] = True
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        summary["error"] = type(exc).__name__
    return summary


def _counter_dict(items: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return dict(sorted(counts.items(), key=lambda row: (-row[1], row[0])))


def _parse_databank_counts(line: str) -> dict[str, int]:
    _, _, raw = line.partition(":")
    counts: dict[str, int] = {}
    for name, value in re.findall(r"([^,]+?)\s+\((\d+)\)", raw):
        counts[name.strip()] = int(value)
    return counts


def _parse_sqx_datetime(value: str) -> str:
    try:
        return datetime.strptime(value, "%Y.%m.%d %H:%M:%S.%f").isoformat(timespec="milliseconds")
    except ValueError:
        return value


def _duration_to_seconds(value: str) -> int:
    hours = 0
    minutes = 0
    seconds = 0
    hour_match = re.search(r"(\d+)\s+hrs?", value)
    min_match = re.search(r"(\d+)\s+min", value)
    sec_match = re.search(r"(\d+)\s+s", value)
    if hour_match:
        hours = int(hour_match.group(1))
    if min_match:
        minutes = int(min_match.group(1))
    if sec_match:
        seconds = int(sec_match.group(1))
    return hours * 3600 + minutes * 60 + seconds


def _parse_project_log_block(path: Path, text: str, block_index: int) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "file": path.name,
        "blockIndex": block_index,
        "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
        "bytes": path.stat().st_size,
        "ok": False,
    }
    start = re.search(r"TASK STARTED at ([0-9.:\s]+)", text)
    finish = re.search(r"TASK FINISHED at ([0-9.:\s]+) in ([^\r\n]+)", text)
    task = re.search(r"Task:\s*([^,\r\n]+),\s*Type:\s*([^\r\n]+)", text)
    totals = re.search(r"Total:\s*(\d+),\s*Time per strategy:\s*([^,]+),\s*Passed:\s*(\d+),\s*Failed:\s*(\d+)", text)
    if start:
        entry["startedAt"] = _parse_sqx_datetime(start.group(1).strip())
    if finish:
        entry["finishedAt"] = _parse_sqx_datetime(finish.group(1).strip())
        entry["durationText"] = finish.group(2).strip()
        entry["durationSeconds"] = _duration_to_seconds(entry["durationText"])
    if task:
        entry["task"] = task.group(1).strip()
        entry["type"] = task.group(2).strip()
    before = re.search(r"Databanks before start:\s*([^\r\n]+)", text)
    after = re.search(r"Databanks after finish:\s*([^\r\n]+)", text)
    if before:
        entry["databanksBefore"] = _parse_databank_counts(before.group(0))
    if after:
        entry["databanksAfter"] = _parse_databank_counts(after.group(0))
    if totals:
        entry["total"] = int(totals.group(1))
        entry["timePerStrategy"] = totals.group(2).strip()
        entry["passed"] = int(totals.group(3))
        entry["failed"] = int(totals.group(4))
    details = []
    detail_pattern = re.compile(
        r"^([^:\r\n]+): Count: (\d+), Avg\. time: ([0-9.]+) s\., Total time: ([0-9.]+) s\., % of all: ([0-9.]+) %",
        re.MULTILINE,
    )
    for match in detail_pattern.finditer(text):
        details.append({
            "name": match.group(1).strip(),
            "count": int(match.group(2)),
            "avgSeconds": float(match.group(3)),
            "totalSeconds": float(match.group(4)),
            "percent": float(match.group(5)),
        })
    entry["timeDetails"] = details
    issues = []
    if "Exception" in text or "ERROR" in text or "OutOfMemory" in text:
        issues.append("error_marker")
    entry["issues"] = issues
    entry["ok"] = bool(finish and task) and not issues
    return entry


def _parse_project_log_file(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = [block for block in re.split(r"(?=TASK STARTED at )", text) if "TASK STARTED at " in block]
    if not blocks:
        return [{
            "file": path.name,
            "blockIndex": 0,
            "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
            "bytes": path.stat().st_size,
            "ok": False,
            "issues": [],
            "timeDetails": [],
        }]
    return [_parse_project_log_block(path, block, index) for index, block in enumerate(blocks)]


def project_log_summary(
    project_root: Path,
    root142: Path,
    *,
    sqx_project: Path | None,
    project_name: str | None,
    limit: int,
) -> dict[str, Any]:
    target = resolve_sqx_project(root142, sqx_project, project_name)
    log_root = target / "log"
    files = sorted(log_root.glob("global_log_*.log"), key=lambda path: path.stat().st_mtime, reverse=True)[:limit] if log_root.is_dir() else []
    entries: list[dict[str, Any]] = []
    for path in files:
        entries.extend(_parse_project_log_file(path))
    entries.sort(key=lambda item: str(item.get("finishedAt") or item.get("startedAt") or item.get("modified") or ""), reverse=True)
    by_task: dict[str, dict[str, Any]] = {}
    for entry in entries:
        task = str(entry.get("task") or "unknown")
        bucket = by_task.setdefault(task, {"count": 0, "latest": None, "durationSeconds": [], "passed": [], "failed": []})
        bucket["count"] += 1
        if bucket["latest"] is None:
            bucket["latest"] = entry
        if isinstance(entry.get("durationSeconds"), int):
            bucket["durationSeconds"].append(entry["durationSeconds"])
        if isinstance(entry.get("passed"), int):
            bucket["passed"].append(entry["passed"])
        if isinstance(entry.get("failed"), int):
            bucket["failed"].append(entry["failed"])
    for bucket in by_task.values():
        durations = bucket.get("durationSeconds") or []
        bucket["avgDurationSeconds"] = round(sum(durations) / len(durations), 2) if durations else None
        bucket["minDurationSeconds"] = min(durations) if durations else None
        bucket["maxDurationSeconds"] = max(durations) if durations else None
    payload = {
        "ok": True,
        "version": "sqx142-project-log-summary-v1",
        "qualityReductionAllowed": False,
        "project": {"name": target.name, "exists": target.is_dir()},
        "logFilesRead": len(entries),
        "entries": entries,
        "byTask": by_task,
    }
    written = write_evidence(project_root, f"project_log_summary_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def _databank_basic_snapshot(databank: Path, *, sample_limit: int = 12) -> dict[str, Any]:
    files = sorted(databank.glob("*.sqx"), key=lambda path: path.stat().st_mtime, reverse=True) if databank.is_dir() else []
    total_bytes = 0
    for path in files:
        try:
            total_bytes += path.stat().st_size
        except OSError:
            continue
    newest = files[0] if files else None
    return {
        "exists": databank.is_dir(),
        "name": databank.name,
        "strategyFiles": len(files),
        "bytes": total_bytes,
        "human": f"{total_bytes / 1024 / 1024:.1f} MB",
        "newestModified": datetime.fromtimestamp(newest.stat().st_mtime).isoformat(timespec="seconds") if newest else "",
        "newestFile": newest.name if newest else "",
        "sampleNewest": [
            {
                "file": path.name,
                "bytes": path.stat().st_size,
                "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
            }
            for path in files[:sample_limit]
        ],
    }


def _databank_mc_snapshot(databank: Path, *, sample_limit: int) -> dict[str, Any]:
    files = sorted(databank.glob("*.sqx"), key=lambda path: path.name.lower()) if databank.is_dir() else []
    selected = files if sample_limit <= 0 else files[:sample_limit]
    rows = [_read_strategy_mc_summary(path) for path in selected]
    result_classes = [str(row.get("filterResult") or "unreadable") for row in rows]
    methods: list[str] = []
    simulations: list[str] = []
    failed_reasons: list[str] = []
    available_fields: set[str] = set()
    for row in rows:
        methods.extend(str(item) for item in (row.get("methods") or []))
        if row.get("simulations"):
            simulations.append(str(row.get("simulations")))
        if row.get("filterResult") == "failed":
            failed_reasons.append(str(row.get("filterReason") or "failed"))
        available_fields.update(str(item) for item in (row.get("availableResultFields") or []))
    total_bytes = sum(path.stat().st_size for path in files)
    mtimes = [path.stat().st_mtime for path in files]
    return {
        "exists": databank.is_dir(),
        "name": databank.name,
        "strategyFiles": len(files),
        "sampledFiles": len(selected),
        "bytes": total_bytes,
        "human": f"{total_bytes / 1024 / 1024:.1f} MB",
        "oldestModified": datetime.fromtimestamp(min(mtimes)).isoformat(timespec="seconds") if mtimes else "",
        "newestModified": datetime.fromtimestamp(max(mtimes)).isoformat(timespec="seconds") if mtimes else "",
        "resultCounts": _counter_dict(result_classes),
        "simulationCounts": _counter_dict(simulations),
        "methodCounts": _counter_dict(methods),
        "topFailedReasons": _counter_dict(failed_reasons[:200]),
        "availableResultFields": sorted(available_fields),
        "sampleRows": rows[:12],
    }


def _project_config_snapshot(project_cfx: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"exists": project_cfx.is_file(), "databanks": [], "tasks": [], "viewMismatches": []}
    if not project_cfx.is_file() or not zipfile.is_zipfile(project_cfx):
        result["error"] = "project_cfx_missing_or_not_zip"
        return result
    with zipfile.ZipFile(project_cfx) as zf:
        config_root = _parse_xml_text(_safe_zip_text(zf, "config.xml"))
        if config_root is not None:
            for databank in config_root.findall(".//Databank"):
                attrs = dict(databank.attrib)
                result["databanks"].append(attrs)
                expected = MC_DATABANK_VIEW_TARGETS.get(attrs.get("name", ""))
                if expected and attrs.get("view") != expected:
                    result["viewMismatches"].append({
                        "databank": attrs.get("name", ""),
                        "currentView": attrs.get("view", ""),
                        "expectedView": expected,
                    })
            for task in config_root.findall(".//Task"):
                result["tasks"].append(dict(task.attrib))
        task_summaries: dict[str, Any] = {}
        for task_name in ("AutomaticRetest-Task6.xml", "AutomaticRetest-Task5.xml"):
            root = _parse_xml_text(_safe_zip_text(zf, task_name))
            if root is None:
                task_summaries[task_name] = {"exists": False}
                continue
            databanks = [dict(item.attrib) for item in root.findall(".//Databanks/Databank")]
            mc = root.find(".//CrossChecks/MonteCarloRetest")
            methods = []
            if mc is not None:
                for method in mc.findall(".//Methods/Method"):
                    methods.append({"type": method.attrib.get("type", ""), "use": method.attrib.get("use", "")})
            conditions = []
            if mc is not None:
                for condition in mc.findall(".//AcceptanceSettings//Condition"):
                    conditions.append({"use": condition.attrib.get("use", "true")})
            task_summaries[task_name] = {
                "exists": True,
                "databanks": databanks,
                "monteCarloRetestUse": (mc.attrib.get("use", "") if mc is not None else ""),
                "methods": methods,
                "acceptanceConditionCount": len(conditions),
                "activeAcceptanceConditionCount": sum(1 for item in conditions if item.get("use") != "false"),
            }
        result["automaticRetests"] = task_summaries
    return result


def _task_databanks(root: ET.Element | None) -> dict[str, str]:
    if root is None:
        return {}
    databanks: dict[str, str] = {}
    for item in root.findall(".//Databanks/Databank"):
        name = item.attrib.get("name", "")
        if name:
            databanks[name] = item.attrib.get("value", "")
    return databanks


def _task_base_spreads(root: ET.Element | None) -> list[float]:
    if root is None:
        return []
    spreads: list[float] = []
    for chart in root.findall(".//CustomData//Chart"):
        raw = chart.attrib.get("spread", "")
        try:
            spreads.append(float(raw))
        except (TypeError, ValueError):
            pass
    return spreads


def _spread_stress_diagnostics(root: ET.Element | None) -> list[dict[str, Any]]:
    if root is None:
        return []
    base_spreads = _task_base_spreads(root)
    base = min([item for item in base_spreads if item > 0], default=0.0)
    diagnostics: list[dict[str, Any]] = []
    for method in root.findall(".//CrossChecks/*/Settings/Methods/Method"):
        if method.attrib.get("type") != "RandomizeSpread" or method.attrib.get("use") != "true":
            continue
        params = {param.attrib.get("key", ""): (param.text or "") for param in method.findall(".//Param")}
        try:
            min_spread = float(params.get("Min") or 0)
            max_spread = float(params.get("Max") or 0)
        except (TypeError, ValueError):
            min_spread = 0.0
            max_spread = 0.0
        ratio_min = round(min_spread / base, 2) if base > 0 else None
        ratio_max = round(max_spread / base, 2) if base > 0 else None
        issue = ""
        if ratio_max is not None and ratio_max >= 10:
            issue = "spread_stress_extreme_vs_base"
        elif ratio_max is not None and ratio_max >= 5:
            issue = "spread_stress_high_vs_base"
        diagnostics.append({
            "method": "RandomizeSpread",
            "baseSpread": base,
            "minSpread": min_spread,
            "maxSpread": max_spread,
            "ratioMinToBase": ratio_min,
            "ratioMaxToBase": ratio_max,
            "issue": issue,
            "qualityReductionAllowed": False,
        })
    return diagnostics


def _active_cross_checks(root: ET.Element | None) -> list[dict[str, Any]]:
    if root is None:
        return []
    parent = root.find(".//CrossChecks")
    if parent is None:
        return []
    checks: list[dict[str, Any]] = []
    for check in list(parent):
        if check.attrib.get("use") != "true":
            continue
        methods = [
            method.attrib.get("type", "")
            for method in check.findall(".//Methods/Method")
            if method.attrib.get("use") == "true" and method.attrib.get("type")
        ]
        conditions = [
            condition
            for condition in check.findall(".//AcceptanceSettings//Condition")
            if condition.attrib.get("use", "true") != "false"
        ]
        info: dict[str, Any] = {
            "id": check.tag,
            "methods": methods,
            "activeConditionCount": len(conditions),
        }
        simulations = check.findtext(".//NumberOfSimulations")
        if simulations:
            info["simulations"] = simulations
        max_tests = check.findtext(".//MaxTests")
        if max_tests:
            info["maxTests"] = max_tests
        checks.append(info)
    return checks


def _duration_band(seconds: Any, active_checks: list[dict[str, Any]], title: str) -> str:
    title_l = title.lower()
    check_ids = {str(check.get("id", "")).lower() for check in active_checks}
    if isinstance(seconds, (int, float)):
        if seconds >= 1800:
            return "very_heavy"
        if seconds >= 240:
            return "heavy"
        if seconds >= 90:
            return "medium"
    if any(token in title_l for token in ("wfm", "spp", "optprofile")):
        return "very_heavy"
    if any(token in title_l for token in ("monkey", "synthetic", "syntetic", "sequential", "tick")):
        return "heavy"
    if any("montecarlo" in check_id for check_id in check_ids) or "sequentialoptimization" in check_ids:
        return "heavy"
    return "normal"


def _profile_for_task(cost: str, title: str, task_type: str) -> str:
    title_l = title.lower()
    if task_type == "Build" or "build" in title_l:
        return "mining_fast_safe" if cost in {"medium", "heavy", "very_heavy"} else "baseline_143_safe"
    if cost in {"heavy", "very_heavy"}:
        return "retest_robust"
    return "baseline_143_safe"


def _queue_guidance(cost: str, title: str, active_checks: list[dict[str, Any]]) -> list[str]:
    title_l = title.lower()
    checks = {str(item.get("id", "")) for item in active_checks}
    guidance: list[str] = []
    if cost in {"heavy", "very_heavy"}:
        guidance.append("run_alone")
    if any("MonteCarlo" in check for check in checks) or any(token in title_l for token in ("monkey", "synthetic", "syntetic")):
        guidance.append("snapshot_databank_before_after")
        guidance.append("keep_natural_passed_failed")
    if "WalkForwardMatrix" in checks or "WFM" in title or "SPP" in title:
        guidance.append("do_not_parallelize_with_mc_or_wfm")
    if "SequentialOptimization" in checks:
        guidance.append("run_after_mc_survivors_only")
    return guidance


def _latest_metrics_for_task(log_summary: dict[str, Any], title: str) -> dict[str, Any]:
    bucket = ((log_summary.get("byTask") or {}).get(title) or {})
    latest = bucket.get("latest") if isinstance(bucket.get("latest"), dict) else {}
    details = latest.get("timeDetails") if isinstance(latest.get("timeDetails"), list) else []
    top_detail = None
    if details:
        top_detail = sorted(details, key=lambda item: float(item.get("percent") or 0), reverse=True)[0]
    return {
        "logRuns": bucket.get("count", 0),
        "latestDurationSeconds": latest.get("durationSeconds"),
        "latestDurationText": latest.get("durationText", ""),
        "latestPassed": latest.get("passed"),
        "latestFailed": latest.get("failed"),
        "latestFinishedAt": latest.get("finishedAt", ""),
        "topTimeDetail": top_detail,
    }


def _project_task_queue_details(project_cfx: Path, log_summary: dict[str, Any], project_dir: Path | None = None) -> list[dict[str, Any]]:
    if not project_cfx.is_file() or not zipfile.is_zipfile(project_cfx):
        return []
    queue: list[dict[str, Any]] = []
    with zipfile.ZipFile(project_cfx) as zf:
        config_root = _parse_xml_text(_safe_zip_text(zf, "config.xml"))
        if config_root is None:
            return []
        for index, task in enumerate(config_root.findall(".//Task"), start=1):
            task_xml = task.attrib.get("taskXMLFile", "")
            root = _parse_xml_text(_safe_zip_text(zf, task_xml)) if task_xml else None
            databanks = _task_databanks(root)
            spread_diagnostics = _spread_stress_diagnostics(root)
            active_checks = _active_cross_checks(root)
            title = task.attrib.get("title", task.attrib.get("name", ""))
            task_type = task.attrib.get("type", "")
            metrics = _latest_metrics_for_task(log_summary, title)
            cost = _duration_band(metrics.get("latestDurationSeconds"), active_checks, title)
            input_name = databanks.get("Input", "")
            output_name = databanks.get("Output", "")
            input_status: dict[str, Any] = {}
            output_status: dict[str, Any] = {}
            if project_dir is not None and input_name:
                input_snapshot = _databank_mc_snapshot(project_dir / "databanks" / input_name, sample_limit=500)
                input_counts = input_snapshot.get("resultCounts") or {}
                input_status = {
                    "databank": input_name,
                    "exists": input_snapshot.get("exists", False),
                    "strategyFiles": input_snapshot.get("strategyFiles", 0),
                    "sampledFiles": input_snapshot.get("sampledFiles", 0),
                    "passed": int(input_counts.get("passed") or 0),
                    "failed": int(input_counts.get("failed") or 0),
                    "missing": int(input_counts.get("missing") or 0),
                    "unreadable": int(input_counts.get("unreadable") or 0),
                }
            if project_dir is not None and output_name:
                output_snapshot = _databank_mc_snapshot(project_dir / "databanks" / output_name, sample_limit=500)
                output_counts = output_snapshot.get("resultCounts") or {}
                output_status = {
                    "databank": output_name,
                    "exists": output_snapshot.get("exists", False),
                    "strategyFiles": output_snapshot.get("strategyFiles", 0),
                    "sampledFiles": output_snapshot.get("sampledFiles", 0),
                    "passed": int(output_counts.get("passed") or 0),
                    "failed": int(output_counts.get("failed") or 0),
                    "missing": int(output_counts.get("missing") or 0),
                    "unreadable": int(output_counts.get("unreadable") or 0),
                }
            guidance = _queue_guidance(cost, title, active_checks)
            blocked_by_input = (
                any(str(check.get("id", "")) == "SequentialOptimization" for check in active_checks)
                and bool(input_status)
                and int(input_status.get("strategyFiles") or 0) > 0
                and int(input_status.get("passed") or 0) <= 0
            )
            omitted_by_operator = title in OPERATOR_OMITTED_RETEST_TITLES
            blocked_by_omitted_input = input_name in OPERATOR_OMITTED_DATABANKS
            if blocked_by_input:
                guidance.append("blocked_no_passed_input")
            if omitted_by_operator:
                guidance.append("omitted_by_operator_policy")
            if blocked_by_omitted_input:
                guidance.append("blocked_depends_on_omitted_input")
            queue.append({
                "position": index,
                "title": title,
                "name": task.attrib.get("name", ""),
                "type": task_type,
                "taskXml": task_xml,
                "active": task.attrib.get("active") == "true",
                "inputDatabank": input_name,
                "outputDatabank": output_name,
                "inputCandidateStatus": input_status,
                "outputCandidateStatus": output_status,
                "spreadStressDiagnostics": spread_diagnostics,
                "blockedByNoPassedInput": blocked_by_input,
                "omittedByOperator": omitted_by_operator,
                "blockedByOmittedInput": blocked_by_omitted_input,
                "activeCrossChecks": active_checks,
                "cost": cost,
                "runAlone": cost in {"heavy", "very_heavy"},
                "recommendedProfile": _profile_for_task(cost, title, task_type),
                "qualityReductionAllowed": False,
                "guidance": guidance,
                "latestMetrics": metrics,
            })
    return queue


def project_retest_queue_plan(
    project_root: Path,
    root142: Path,
    *,
    sqx_project: Path | None,
    project_name: str | None,
    log_limit: int,
) -> dict[str, Any]:
    target = resolve_sqx_project(root142, sqx_project, project_name)
    is_performance_clone = target.name.startswith("_PERFQ_")
    log_summary = project_log_summary(
        project_root,
        root142,
        sqx_project=sqx_project,
        project_name=project_name,
        limit=log_limit,
    )
    queue = _project_task_queue_details(target / "project.cfx", log_summary, target)
    heavy = [item for item in queue if item.get("cost") in {"heavy", "very_heavy"}]
    payload: dict[str, Any] = {
        "ok": bool(target.is_dir() and queue),
        "version": "sqx142-retest-queue-plan-v1",
        "qualityReductionAllowed": False,
        "project": {"name": target.name, "exists": target.is_dir()},
        "logSummaryEvidence": (log_summary.get("evidence") or {}).get("filename", ""),
        "rules": [
            "Do not lower OOS/Forward ranges, precision, simulations or final filters for speed.",
            "Run heavy retests alone unless a later smoke proves safe parallelism.",
            "Run Monkey, Synthetic, WFM and SPP only after upstream survivor databanks are reasonable.",
            "Snapshot databanks before/after heavy retests and accept natural passed/failed results.",
            "Use a cloned performance project for timing experiments before changing the master project.",
        ],
        "profileUse": {
            "default": "baseline_143_safe",
            "heavyRetest": "retest_robust",
            "miningExperiment": "mining_fast_safe",
        },
        "queue": queue,
        "spreadStressIssues": [
            {
                "title": item.get("title"),
                "inputDatabank": item.get("inputDatabank"),
                "outputDatabank": item.get("outputDatabank"),
                "diagnostic": diagnostic,
            }
            for item in queue
            for diagnostic in (item.get("spreadStressDiagnostics") or [])
            if diagnostic.get("issue")
        ],
        "heavyTasks": [
            {
                "position": item.get("position"),
                "title": item.get("title"),
                "cost": item.get("cost"),
                "recommendedProfile": item.get("recommendedProfile"),
                "latestDurationText": (item.get("latestMetrics") or {}).get("latestDurationText", ""),
            }
            for item in heavy
        ],
        "nextMeasurableExperiment": (
            {
                "step": "run_clone_mc_smoke",
                "command": (
                    "tools\\sqx142_performance_gate.ps1 begin-project-mc-smoke "
                    f"--project-name \"{target.name}\" --apply --launch"
                ),
                "reason": "This is already a performance clone; measure the next heavy retest sequence here.",
            }
            if is_performance_clone
            else {
                "step": "clone_performance_project",
                "command": (
                    "tools\\sqx142_performance_gate.ps1 clone-performance-project "
                    f"--project-name \"{target.name}\" --apply"
                ),
                "reason": "Measure scheduling/profile changes on a clone before touching the source project.",
            }
        ),
        "warnings": [],
    }
    if not target.is_dir():
        payload["warnings"].append("project_missing")
    if not queue:
        payload["warnings"].append("project_queue_unreadable")
    if len(heavy) > 1:
        payload["warnings"].append("multiple_heavy_retests_detected_run_one_at_a_time")
    written = write_evidence(project_root, f"retest_queue_plan_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def _build_task_efficiency_summary(project_cfx: Path, task_xml: str) -> dict[str, Any]:
    payload: dict[str, Any] = {"taskXml": task_xml, "exists": False}
    if not project_cfx.is_file() or not zipfile.is_zipfile(project_cfx) or not task_xml:
        return payload
    try:
        with zipfile.ZipFile(project_cfx) as zf:
            root = _parse_xml_text(_safe_zip_text(zf, task_xml))
    except (OSError, zipfile.BadZipFile):
        return payload
    if root is None:
        return payload
    active_goals = [dict(goal.attrib) for goal in root.findall(".//Ranking/Goal") if goal.attrib.get("use") == "true"]
    condition_groups = []
    total_conditions = 0
    active_conditions = 0
    for conditions in root.findall(".//Conditions"):
        rows = list(conditions.findall("./Condition"))
        if not rows:
            continue
        active = [row for row in rows if row.attrib.get("use", "true") != "false"]
        total_conditions += len(rows)
        active_conditions += len(active)
        condition_groups.append({
            "crossCheck": conditions.attrib.get("CrossCheck", "base"),
            "thresholdPct": conditions.attrib.get("thresholdPct", ""),
            "conditions": len(rows),
            "activeConditions": len(active),
        })
    params = {
        (param.attrib.get("key") or param.attrib.get("name") or ""): (param.text or "").strip()
        for param in root.findall(".//Param")
        if param.attrib.get("key") or param.attrib.get("name")
    }
    databanks = _task_databanks(root)
    max_strategies = root.findtext(".//MaxStrategies") or ""
    max_generations = root.findtext(".//MaxGenerations") or ""
    risks = []
    try:
        if int(max_strategies or 0) >= 5000:
            risks.append("large_max_strategies")
    except ValueError:
        pass
    try:
        if int(max_generations or 0) >= 50:
            risks.append("large_max_generations")
    except ValueError:
        pass
    if databanks.get("Output", "").lower() == "null":
        risks.append("output_databank_null")
    if _active_cross_checks(root):
        risks.append("build_has_active_crosschecks")
    if (params.get("StoreChartData") or "").lower() == "true":
        risks.append("store_chart_data_enabled")
    strategy_type = root.find(".//StrategyType")
    market_sides = root.find(".//MarketSides")
    build_mode = root.find(".//BuildMode")
    payload.update({
        "exists": True,
        "databanks": databanks,
        "buildMode": dict(build_mode.attrib) if build_mode is not None else {},
        "strategyType": dict(strategy_type.attrib) if strategy_type is not None else {},
        "marketSides": dict(market_sides.attrib) if market_sides is not None else {},
        "entrySymmetry": root.findtext(".//EntrySymmetry") or "",
        "exitSymmetry": root.findtext(".//ExitSymmetry") or "",
        "maxStrategies": max_strategies,
        "maxGenerations": max_generations,
        "islands": root.findtext(".//Islands") or "",
        "rankingType": (root.find(".//Ranking").attrib.get("type", "") if root.find(".//Ranking") is not None else ""),
        "activeRankingGoals": active_goals,
        "activeRankingGoalCount": len(active_goals),
        "conditionGroups": condition_groups,
        "conditionTotals": {"total": total_conditions, "active": active_conditions},
        "activeCrossChecks": _active_cross_checks(root),
        "blockCounts": {
            "blocks": len(root.findall(".//Block")),
            "generatedBlocks": len(root.findall(".//Generated")),
            "predefinedBlocks": len(root.findall(".//Predefined")),
        },
        "settings": {
            "StoreChartData": params.get("StoreChartData", ""),
            "DontStorePendingOrders": params.get("DontStorePendingOrders", ""),
            "MaxTradesPerDay": params.get("MaxTradesPerDay", ""),
            "LimitTimeRange": params.get("LimitTimeRange", ""),
        },
        "efficiencyRisks": risks,
    })
    return payload


def project_mining_pipeline_advisor(
    project_root: Path,
    root142: Path,
    *,
    sqx_project: Path | None,
    project_name: str | None,
    log_limit: int,
    include_paths: bool,
) -> dict[str, Any]:
    target = resolve_sqx_project(root142, sqx_project, project_name)
    is_performance_clone = target.name.startswith("_PERFQ_")
    log_summary = project_log_summary(
        project_root,
        root142,
        sqx_project=sqx_project,
        project_name=project_name,
        limit=log_limit,
    )
    project_cfx = target / "project.cfx"
    queue = _project_task_queue_details(project_cfx, log_summary, target)
    build_tasks = [item for item in queue if item.get("type") == "Build" or "build" in str(item.get("title", "")).lower()]
    build_summaries = [
        {"queue": item, "build": _build_task_efficiency_summary(project_cfx, str(item.get("taskXml") or ""))}
        for item in build_tasks
    ]
    databank_names: list[str] = []
    for item in queue:
        for key in ("inputDatabank", "outputDatabank"):
            value = str(item.get(key) or "")
            if value and value.lower() != "null" and value not in databank_names:
                databank_names.append(value)
    for extra in ("Results", "Initial population", "Last generation", "Strategies to optimize", "Strategies to improve"):
        if extra not in databank_names:
            databank_names.append(extra)
    databanks_root = target / "databanks"
    databanks = {}
    for name in databank_names:
        snapshot = _databank_mc_snapshot(databanks_root / name, sample_limit=250)
        databanks[name] = {
            "exists": snapshot.get("exists", False),
            "strategyFiles": snapshot.get("strategyFiles", 0),
            "sampledFiles": snapshot.get("sampledFiles", 0),
            "human": snapshot.get("human", ""),
            "oldestModified": snapshot.get("oldestModified", ""),
            "newestModified": snapshot.get("newestModified", ""),
            "resultCounts": snapshot.get("resultCounts", {}),
            "simulationCounts": snapshot.get("simulationCounts", {}),
            "methodCounts": snapshot.get("methodCounts", {}),
            "topFailedReasons": dict(list((snapshot.get("topFailedReasons", {}) or {}).items())[:8]),
            "availableResultFields": snapshot.get("availableResultFields", [])[:20],
        }
    blockers: list[str] = []
    if not target.is_dir():
        blockers.append("project_missing")
    if not build_tasks:
        blockers.append("build_task_missing")
    first_build = (build_summaries[0].get("build") if build_summaries else {}) or {}
    if "build_has_active_crosschecks" in (first_build.get("efficiencyRisks") or []):
        blockers.append("build_has_active_crosschecks_review_before_long_mining")
    if not is_performance_clone:
        next_experiment = {
            "id": "clone_for_mining_pipeline_smoke",
            "command": f"tools\\sqx142_performance_gate.ps1 clone-performance-project --project-name \"{target.name}\" --apply",
            "reason": "Fase 3 experiments must run on a _PERFQ_* clone before touching the master project.",
            "requiresSQXClosed": False,
        }
    else:
        build_title = str((build_tasks[0] or {}).get("title") or "Build")
        next_experiment = {
            "id": "prepare_build_single_run",
            "command": f"tools\\sqx142_performance_gate.ps1 prepare-queue-step \"{build_title}\" --project-name \"{target.name}\" --apply --launch",
            "reason": "Project is already a performance clone; prepare only Build with mining_fast_safe for a short measured run.",
            "requiresSQXClosed": True,
        }
    payload: dict[str, Any] = {
        "ok": bool(target.is_dir() and build_tasks),
        "version": "sqx142-mining-pipeline-advisor-v1",
        "dryRun": True,
        "qualityReductionAllowed": False,
        "project": {"name": target.name, "exists": target.is_dir(), "isPerformanceClone": is_performance_clone},
        "logSummaryEvidence": (log_summary.get("evidence") or {}).get("filename", ""),
        "buildTasks": build_summaries,
        "databanks": databanks,
        "stagePlan": [
            {
                "stage": "build_short_single_run",
                "purpose": "Measure Build cost with mining_fast_safe without changing methodology.",
                "profile": "mining_fast_safe",
                "maxConcurrentSQXProjects": 1,
                "qualityReductionAllowed": False,
            },
            {
                "stage": "cheap_review",
                "purpose": "Review generated/early databanks with MINING FAST REVIEW before heavy robustness.",
                "view": "MINING FAST REVIEW",
                "qualityReductionAllowed": False,
            },
            {
                "stage": "survivor_handoff",
                "purpose": "Send only reasonable survivors to retest queue; do not run MC/Synthetic during mining.",
                "dependsOn": "Fase 4 retest queue",
                "qualityReductionAllowed": False,
            },
        ],
        "rules": [
            "Do not reduce final quality filters, OOS/Forward ranges, precision or robustness simulations for speed.",
            "Run mining smoke on a _PERFQ_* clone first.",
            "Use mining_fast_safe for Build experiments and restore baseline_143_safe after the smoke.",
            "Do not run MC/Monkey/Synthetic/Sequential in parallel with mining.",
            "Use MINING FAST REVIEW for quick scanning; reserve FINAL DECISION FULL for final/export review.",
        ],
        "blockers": blockers,
        "nextMeasurableExperiment": next_experiment,
        "privacy": {"local_paths_returned": include_paths},
    }
    if include_paths:
        payload["paths"] = {"project": str(target), "projectCfx": str(project_cfx)}
    written = write_evidence(project_root, f"mining_pipeline_advisor_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
    return payload


def _queue_task_blockers(item: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if item.get("omittedByOperator"):
        blockers.append("omitted_by_operator_policy")
    if item.get("blockedByOmittedInput"):
        blockers.append("depends_on_omitted_input")
    if item.get("blockedByNoPassedInput"):
        blockers.append("no_passed_input_candidates")
    input_status = item.get("inputCandidateStatus") if isinstance(item.get("inputCandidateStatus"), dict) else {}
    if input_status:
        if not input_status.get("exists"):
            blockers.append("input_databank_missing")
        elif int(input_status.get("strategyFiles") or 0) <= 0:
            blockers.append("input_databank_empty")
    return blockers


def _queue_task_is_unmeasured(item: dict[str, Any]) -> bool:
    metrics = item.get("latestMetrics") if isinstance(item.get("latestMetrics"), dict) else {}
    if metrics.get("latestDurationSeconds") is not None:
        return False
    output_status = item.get("outputCandidateStatus") if isinstance(item.get("outputCandidateStatus"), dict) else {}
    if int(output_status.get("strategyFiles") or 0) > 0:
        return False
    return True


def project_retest_next_step(
    project_root: Path,
    root142: Path,
    *,
    sqx_project: Path | None,
    project_name: str | None,
    log_limit: int,
) -> dict[str, Any]:
    queue_plan = project_retest_queue_plan(
        project_root,
        root142,
        sqx_project=sqx_project,
        project_name=project_name,
        log_limit=log_limit,
    )
    queue = queue_plan.get("queue") if isinstance(queue_plan.get("queue"), list) else []
    ready: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for item in queue:
        blockers = _queue_task_blockers(item)
        row = {
            "position": item.get("position"),
            "title": item.get("title"),
            "type": item.get("type"),
            "cost": item.get("cost"),
            "inputDatabank": item.get("inputDatabank", ""),
            "outputDatabank": item.get("outputDatabank", ""),
            "recommendedProfile": item.get("recommendedProfile"),
            "latestDurationText": (item.get("latestMetrics") or {}).get("latestDurationText", ""),
            "latestPassed": (item.get("latestMetrics") or {}).get("latestPassed"),
            "latestFailed": (item.get("latestMetrics") or {}).get("latestFailed"),
            "inputCandidateStatus": item.get("inputCandidateStatus") or {},
            "outputCandidateStatus": item.get("outputCandidateStatus") or {},
            "spreadStressDiagnostics": item.get("spreadStressDiagnostics") or [],
            "omittedByOperator": bool(item.get("omittedByOperator")),
            "blockedByOmittedInput": bool(item.get("blockedByOmittedInput")),
            "guidance": item.get("guidance") or [],
            "unmeasured": _queue_task_is_unmeasured(item),
            "blockers": blockers,
        }
        if blockers:
            blocked.append(row)
        else:
            ready.append(row)

    ready_retests = [item for item in ready if item.get("type") != "Build"]
    unmeasured_ready = [item for item in ready if item.get("unmeasured")]
    unmeasured_ready_retests = [item for item in ready_retests if item.get("unmeasured")]
    measured_retest_positions = [
        int(item.get("position") or 0)
        for item in ready + blocked
        if item.get("type") != "Build" and not item.get("unmeasured")
    ]
    last_measured_position = max(measured_retest_positions) if measured_retest_positions else 0
    after_measured = [
        item
        for item in unmeasured_ready_retests
        if int(item.get("position") or 0) > last_measured_position
    ]
    heavy_unmeasured = [item for item in unmeasured_ready_retests if item.get("cost") in {"heavy", "very_heavy"}]
    normal_unmeasured = [item for item in unmeasured_ready_retests if item.get("cost") not in {"heavy", "very_heavy"}]
    heavy_after_measured = [item for item in after_measured if item.get("cost") in {"heavy", "very_heavy"}]
    normal_after_measured = [item for item in after_measured if item.get("cost") not in {"heavy", "very_heavy"}]
    project_order_next = unmeasured_ready_retests[0] if unmeasured_ready_retests else None
    next_after_measured = after_measured[0] if after_measured else project_order_next
    lower_cost_next = normal_after_measured[0] if normal_after_measured else (normal_unmeasured[0] if normal_unmeasured else next_after_measured)
    next_heavy = heavy_after_measured[0] if heavy_after_measured else (heavy_unmeasured[0] if heavy_unmeasured else None)
    primary_blocker = next(
        (
            item
            for item in blocked
            if "no_passed_input_candidates" in (item.get("blockers") or [])
        ),
        blocked[0] if blocked else None,
    )

    target_name = ((queue_plan.get("project") or {}).get("name") or project_name or DEFAULT_REAL_PROJECT_NAME)

    def command_for(item: dict[str, Any] | None) -> str:
        if not item:
            return ""
        return (
            "tools\\sqx142_performance_gate.ps1 prepare-queue-step "
            f"\"{item.get('title')}\" --project-name \"{target_name}\" --apply"
        )

    payload: dict[str, Any] = {
        "ok": bool(queue_plan.get("ok")),
        "version": "sqx142-retest-next-step-v1",
        "qualityReductionAllowed": False,
        "project": queue_plan.get("project") or {},
        "queuePlanEvidence": (queue_plan.get("evidence") or {}).get("filename", ""),
        "rules": [
            "Recommendation only; execution remains dry-run unless the operator applies it.",
            "Blocked tasks are skipped until their input candidate problem is resolved.",
            "Very heavy tasks must run alone and keep existing filters/simulations.",
            "SPP and FOWARD are omitted from tests/optimization by operator decision.",
        ],
        "operatorOmittedTasks": sorted(OPERATOR_OMITTED_RETEST_TITLES),
        "operatorOmittedDatabanks": sorted(OPERATOR_OMITTED_DATABANKS),
        "summary": {
            "readyCount": len(ready),
            "blockedCount": len(blocked),
            "unmeasuredReadyCount": len(unmeasured_ready),
            "unmeasuredReadyRetestCount": len(unmeasured_ready_retests),
            "heavyUnmeasuredCount": len(heavy_unmeasured),
            "lastMeasuredRetestPosition": last_measured_position,
        },
        "blockedTasks": blocked,
        "readyTasks": ready,
        "recommendation": {
            "projectOrderNext": project_order_next,
            "projectOrderCommand": command_for(project_order_next),
            "nextAfterMeasuredChain": next_after_measured,
            "nextAfterMeasuredCommand": command_for(next_after_measured),
            "lowerCostAlternative": lower_cost_next,
            "lowerCostCommand": command_for(lower_cost_next),
            "nextHeavyExperiment": next_heavy,
            "nextHeavyCommand": command_for(next_heavy),
            "primaryBlocker": primary_blocker,
            "spreadStressIssues": queue_plan.get("spreadStressIssues") or [],
        },
    }
    if blocked:
        payload["warnings"] = [f"{item.get('title')}: {','.join(item.get('blockers') or [])}" for item in blocked]
    written = write_evidence(project_root, f"retest_next_step_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def _task_xml_for_title(project_cfx: Path, task_title: str) -> str:
    if not project_cfx.is_file() or not zipfile.is_zipfile(project_cfx):
        return ""
    with zipfile.ZipFile(project_cfx) as zf:
        config_root = _parse_xml_text(_safe_zip_text(zf, "config.xml"))
        if config_root is None:
            return ""
        for task in config_root.findall(".//Task"):
            title = task.attrib.get("title", task.attrib.get("name", ""))
            if title.casefold() == task_title.casefold():
                return task.attrib.get("taskXMLFile", "")
    return ""


def _mc2_spread_current(project_cfx: Path) -> dict[str, Any]:
    task_xml = _task_xml_for_title(project_cfx, "MC 2")
    result: dict[str, Any] = {"taskTitle": "MC 2", "taskXml": task_xml, "exists": False}
    if not task_xml or not project_cfx.is_file() or not zipfile.is_zipfile(project_cfx):
        result["error"] = "mc2_task_missing"
        return result
    with zipfile.ZipFile(project_cfx) as zf:
        root = _parse_xml_text(_safe_zip_text(zf, task_xml))
    if root is None:
        result["error"] = "mc2_xml_unreadable"
        return result
    result["exists"] = True
    result["databanks"] = _task_databanks(root)
    result["baseSpreads"] = _task_base_spreads(root)
    result["spreadDiagnostics"] = _spread_stress_diagnostics(root)
    return result


def mc2_spread_diagnostic(
    project_root: Path,
    root142: Path,
    *,
    sqx_project: Path | None,
    project_name: str | None,
    log_limit: int,
) -> dict[str, Any]:
    target = resolve_sqx_project(root142, sqx_project, project_name)
    current = _mc2_spread_current(target / "project.cfx")
    queue_plan = project_retest_queue_plan(
        project_root,
        root142,
        sqx_project=sqx_project,
        project_name=project_name,
        log_limit=log_limit,
    )
    base = 0.0
    diagnostics = current.get("spreadDiagnostics") if isinstance(current.get("spreadDiagnostics"), list) else []
    if diagnostics:
        base = float((diagnostics[0] or {}).get("baseSpread") or 0)
    candidate_multipliers = [
        {"id": "tight_x1_x3", "minMultiplier": 1.0, "maxMultiplier": 3.0},
        {"id": "conservative_x2_x5", "minMultiplier": 2.0, "maxMultiplier": 5.0},
        {"id": "moderate_x3_x8", "minMultiplier": 3.0, "maxMultiplier": 8.0},
    ]
    candidates = []
    for item in candidate_multipliers:
        candidates.append({
            **item,
            "spreadMin": round(base * float(item["minMultiplier"]), 2) if base else None,
            "spreadMax": round(base * float(item["maxMultiplier"]), 2) if base else None,
            "note": "candidate_only_not_applied",
        })
    payload: dict[str, Any] = {
        "ok": bool(target.is_dir() and current.get("exists")),
        "version": "sqx142-mc2-spread-diagnostic-v1",
        "qualityReductionAllowed": False,
        "project": {"name": target.name, "exists": target.is_dir(), "isPerformanceClone": target.name.startswith("_PERFQ_")},
        "current": current,
        "queuePlanEvidence": (queue_plan.get("evidence") or {}).get("filename", ""),
        "spreadStressIssues": queue_plan.get("spreadStressIssues") or [],
        "candidateRanges": candidates,
        "rules": [
            "This command is diagnostic only and does not modify methodology.",
            "Candidate ranges are base-spread multiples for discussion/smoke design, not automatic recommendations.",
            "Any applied range must be tested on a clone with natural passed/failed results.",
        ],
    }
    written = write_evidence(project_root, f"mc2_spread_diagnostic_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def _patch_mc2_spread(project_cfx: Path, spread_min: float, spread_max: float, backup_dir: Path, *, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": False,
        "dryRun": not apply,
        "taskTitle": "MC 2",
        "spreadMin": spread_min,
        "spreadMax": spread_max,
        "changedParams": [],
    }
    task_xml = _task_xml_for_title(project_cfx, "MC 2")
    payload["taskXml"] = task_xml
    if not task_xml or not project_cfx.is_file() or not zipfile.is_zipfile(project_cfx):
        payload["error"] = "mc2_task_missing"
        return payload
    with zipfile.ZipFile(project_cfx, "r") as source:
        task_text = _safe_zip_text(source, task_xml)
        root = _parse_xml_text(task_text)
        if root is None:
            payload["error"] = "mc2_xml_unreadable"
            return payload
        method = root.find(".//CrossChecks/*/Settings/Methods/Method[@type='RandomizeSpread'][@use='true']")
        if method is None:
            payload["error"] = "active_randomize_spread_missing"
            return payload
        for key, value in (("Min", spread_min), ("Max", spread_max)):
            param = method.find(f".//Param[@key='{key}']")
            if param is None:
                payload["error"] = f"spread_param_{key.lower()}_missing"
                return payload
            old = param.text or ""
            new = f"{value:g}"
            if old != new:
                payload["changedParams"].append({"key": key, "old": old, "new": new})
                param.text = new
        if not apply:
            payload["ok"] = True
            return payload
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / project_cfx.name
        shutil.copy2(project_cfx, backup)
        tmp = project_cfx.with_suffix(project_cfx.suffix + f".{os.getpid()}.tmp")
        updated_task = ET.tostring(root, encoding="utf-8", xml_declaration=False)
        with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as target_zip:
            for item in source.infolist():
                data = updated_task if item.filename == task_xml else source.read(item.filename)
                target_zip.writestr(item, data)
    tmp.replace(project_cfx)
    payload["backup"] = {"copied": True, "path": str(backup)}
    payload["ok"] = True
    return payload


def _archive_variant_databanks(project_dir: Path, databanks: list[str], label: str) -> dict[str, Any]:
    backup_root = project_dir / "diagnostic_backups" / f"{label}_{stamp()}"
    payload: dict[str, Any] = {
        "ok": True,
        "backupRoot": str(backup_root),
        "databanks": [],
        "movedFiles": 0,
    }
    for databank in databanks:
        source = project_dir / "databanks" / databank
        row = {"databank": databank, "exists": source.is_dir(), "movedFiles": 0}
        if not source.is_dir():
            payload["databanks"].append(row)
            continue
        files = [path for path in source.glob("*.sqx") if path.is_file()]
        if files:
            target = backup_root / databank
            target.mkdir(parents=True, exist_ok=True)
            for path in files:
                path.replace(target / path.name)
                row["movedFiles"] += 1
                payload["movedFiles"] += 1
        payload["databanks"].append(row)
    return payload


def create_mc2_spread_variant(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    sqx_project: Path | None,
    project_name: str | None,
    spread_min: float,
    spread_max: float,
    apply: bool,
    allow_source_project: bool,
) -> dict[str, Any]:
    source = resolve_sqx_project(root142, sqx_project, project_name)
    variant_name = f"_PERFQ_MC2SPREAD_{source.name}_{stamp()}"
    target = source.parent / variant_name
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-mc2-spread-variant-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "source": {"name": source.name, "exists": source.is_dir(), "isPerformanceClone": source.name.startswith("_PERFQ_")},
        "target": {"name": target.name, "exists": target.exists()},
        "spreadMin": spread_min,
        "spreadMax": spread_max,
        "rules": [
            "Creates a separate _PERFQ_ diagnostic variant; source project is not modified.",
            "Only MC 2 active RandomizeSpread Min/Max is changed in the variant.",
            "No filters, simulations, OOS/Forward ranges or pass/fail results are forced.",
        ],
    }
    if spread_min <= 0 or spread_max <= 0 or spread_min > spread_max:
        payload["error"] = "invalid_spread_range"
        return payload
    if not source.is_dir() or not (source / "project.cfx").is_file():
        payload["error"] = "source_project_missing"
        return payload
    if not source.name.startswith("_PERFQ_") and not allow_source_project:
        payload["error"] = "source_project_protected"
        payload["message"] = "Use a _PERFQ_ clone or pass --allow-source-project intentionally."
        return payload
    if apply and sqx_processes_running(root142, root143):
        payload["error"] = "sqx_processes_running"
        write_evidence(project_root, f"mc2_spread_variant_failed_{stamp()}.json", payload)
        return payload
    payload["beforeDiagnostic"] = mc2_spread_diagnostic(
        project_root,
        root142,
        sqx_project=sqx_project,
        project_name=project_name,
        log_limit=80,
    )
    if not apply:
        payload["ok"] = True
        payload["message"] = "Dry-run only. Re-run with --apply to copy the project and patch MC 2 in the variant."
    else:
        try:
            shutil.copytree(source, target)
            payload["target"]["exists"] = target.is_dir()
            backup_dir = root142.parent / "SQX_142_Crack_local_backups" / f"sqx142_mc2_spread_variant_before_{stamp()}"
            payload["patch"] = _patch_mc2_spread(target / "project.cfx", spread_min, spread_max, backup_dir, apply=True)
            payload["archivedOldOutputs"] = _archive_variant_databanks(target, ["MC2", "Sequential"], "mc2_spread_variant")
            payload["afterDiagnostic"] = mc2_spread_diagnostic(
                project_root,
                root142,
                sqx_project=target,
                project_name=None,
                log_limit=80,
            )
            payload["ok"] = bool((payload.get("patch") or {}).get("ok"))
        except OSError as exc:
            payload["error"] = type(exc).__name__
    written = write_evidence(project_root, f"mc2_spread_variant_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def _latest_evidence_file(project_root: Path, prefix: str) -> Path | None:
    root = evidence_root(project_root)
    if not root.is_dir():
        return None
    matches = [path for path in root.glob(f"{prefix}_*.json") if path.is_file()]
    if not matches:
        return None
    return max(matches, key=lambda path: path.stat().st_mtime)


def _read_evidence_summary(project_root: Path, filename: str | None) -> dict[str, Any]:
    selected = evidence_root(project_root) / Path(filename).name if filename else _latest_evidence_file(project_root, "sequential_final_review")
    payload: dict[str, Any] = {"requested": filename or "latest:sequential_final_review", "exists": bool(selected and selected.is_file())}
    if not selected or not selected.is_file():
        payload["ok"] = False
        payload["error"] = "evidence_missing"
        return payload
    payload["filename"] = selected.name
    try:
        data = json.loads(selected.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        payload["ok"] = False
        payload["error"] = type(exc).__name__
        return payload
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    sequential_passed = summary.get("sequentialPassed") if isinstance(summary.get("sequentialPassed"), dict) else {}
    payload.update({
        "ok": bool(data.get("ok")),
        "version": data.get("version", ""),
        "filesTotal": summary.get("filesTotal"),
        "readable": summary.get("readable"),
        "filterResults": summary.get("filterResults") or {},
        "sequentialPassed": sequential_passed,
        "stableAreaTotals": summary.get("stableAreaTotals") or {},
        "validForPromotion": bool(
            data.get("ok")
            and summary.get("filesTotal") == 84
            and summary.get("readable") == 84
            and sequential_passed.get("true") == 84
        ),
    })
    return payload


def promote_mc2_spread_to_base(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    sqx_project: Path | None,
    project_name: str | None,
    spread_min: float | None,
    spread_max: float | None,
    min_multiplier: float,
    max_multiplier: float,
    source_evidence: str | None,
    apply: bool,
    allow_master_project: bool,
    accept_methodology_change: bool,
    log_limit: int,
) -> dict[str, Any]:
    target = resolve_sqx_project(root142, sqx_project, project_name)
    backup_dir = root142.parent / "SQX_142_Crack_local_backups" / f"sqx142_mc2_spread_promotion_before_{stamp()}"
    evidence_summary = _read_evidence_summary(project_root, source_evidence)
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-mc2-spread-promotion-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "target": {"name": target.name, "exists": target.is_dir(), "isPerformanceClone": target.name.startswith("_PERFQ_")},
        "requestedSpreadMin": spread_min,
        "requestedSpreadMax": spread_max,
        "multiplierPolicy": {
            "enabledWhenExplicitSpreadMissing": True,
            "minMultiplier": min_multiplier,
            "maxMultiplier": max_multiplier,
        },
        "sourceEvidence": evidence_summary,
        "requiredFlags": {
            "allowMasterProject": allow_master_project,
            "acceptMethodologyChange": accept_methodology_change,
        },
        "backupRoot": str(backup_dir) if apply else str(backup_dir) + " (planned)",
        "rules": [
            "Dry-run by default; the base project is not modified unless --apply is used.",
            "Apply requires --allow-master-project and --accept-methodology-change.",
            "Only MC 2 active RandomizeSpread Min/Max can change.",
            "No filters, simulations, OOS/Forward ranges, databank results or passed/failed values are forced.",
            "Rollback restores project.cfx from the backup recorded in the promotion evidence.",
        ],
    }
    if min_multiplier <= 0 or max_multiplier <= 0 or min_multiplier > max_multiplier:
        payload["error"] = "invalid_multiplier_range"
        return payload
    if not target.is_dir() or not (target / "project.cfx").is_file():
        payload["error"] = "target_project_missing"
        return payload

    payload["beforeDiagnostic"] = mc2_spread_diagnostic(
        project_root,
        root142,
        sqx_project=sqx_project,
        project_name=project_name,
        log_limit=log_limit,
    )
    base_spreads = (((payload.get("beforeDiagnostic") or {}).get("current") or {}).get("baseSpreads") or [])
    base_spread = float(base_spreads[0] or 0) if base_spreads else 0.0
    if spread_min is None:
        spread_min = round(base_spread * min_multiplier, 2) if base_spread else None
    if spread_max is None:
        spread_max = round(base_spread * max_multiplier, 2) if base_spread else None
    payload["baseSpread"] = base_spread
    payload["spreadMin"] = spread_min
    payload["spreadMax"] = spread_max
    payload["derivedFromMultiplierPolicy"] = bool(base_spread and (payload["requestedSpreadMin"] is None or payload["requestedSpreadMax"] is None))
    if spread_min is None or spread_max is None or spread_min <= 0 or spread_max <= 0 or spread_min > spread_max:
        payload["error"] = "invalid_or_unresolved_spread_range"
        return payload
    payload["xmlDiff"] = _patch_mc2_spread(target / "project.cfx", spread_min, spread_max, backup_dir, apply=False)
    payload["readyToApply"] = bool(
        payload["xmlDiff"].get("ok")
        and evidence_summary.get("validForPromotion")
        and target.name == (project_name or DEFAULT_REAL_PROJECT_NAME)
    )
    if not evidence_summary.get("validForPromotion"):
        payload["blocker"] = "source_evidence_not_valid_for_promotion"
    if not apply:
        payload["ok"] = bool(payload["xmlDiff"].get("ok"))
        payload["message"] = "Dry-run only. Re-run with --apply --allow-master-project --accept-methodology-change to promote."
        written = write_evidence(project_root, f"mc2_spread_promotion_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
        return payload

    if not allow_master_project or not accept_methodology_change:
        payload["error"] = "promotion_requires_explicit_flags"
        written = write_evidence(project_root, f"mc2_spread_promotion_blocked_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
        return payload
    if not evidence_summary.get("validForPromotion"):
        payload["error"] = "source_evidence_not_valid_for_promotion"
        written = write_evidence(project_root, f"mc2_spread_promotion_blocked_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
        return payload
    if sqx_processes_running(root142, root143):
        payload["error"] = "sqx_processes_running"
        written = write_evidence(project_root, f"mc2_spread_promotion_blocked_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
        return payload

    payload["patch"] = _patch_mc2_spread(target / "project.cfx", spread_min, spread_max, backup_dir, apply=True)
    payload["afterDiagnostic"] = mc2_spread_diagnostic(
        project_root,
        root142,
        sqx_project=sqx_project,
        project_name=project_name,
        log_limit=log_limit,
    )
    payload["targetProjectPath"] = str(target)
    payload["rollbackCommand"] = "tools\\sqx142_performance_gate.ps1 rollback-mc2-spread-promotion --promotion-evidence <this_evidence_filename> --apply"
    payload["ok"] = bool((payload.get("patch") or {}).get("ok"))
    written = write_evidence(project_root, f"mc2_spread_promotion_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    payload["rollbackCommand"] = f"tools\\sqx142_performance_gate.ps1 rollback-mc2-spread-promotion --promotion-evidence {written.name} --apply"
    return payload


def rollback_mc2_spread_promotion(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    promotion_evidence: str,
    apply: bool,
    log_limit: int,
) -> dict[str, Any]:
    evidence_file = evidence_root(project_root) / Path(promotion_evidence).name
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-mc2-spread-promotion-rollback-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "promotionEvidence": evidence_file.name,
        "promotionEvidenceExists": evidence_file.is_file(),
        "rules": [
            "Dry-run by default; rollback copies the recorded backup project.cfx over the promoted project.cfx only with --apply.",
            "Current project.cfx is backed up before rollback.",
            "SQX must be closed before rollback apply.",
        ],
    }
    if not evidence_file.is_file():
        payload["error"] = "promotion_evidence_missing"
        return payload
    try:
        promotion = json.loads(evidence_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        payload["error"] = type(exc).__name__
        return payload
    backup_raw = str(((promotion.get("patch") or {}).get("backup") or {}).get("path") or "")
    target_raw = str(promotion.get("targetProjectPath") or "")
    backup_path = Path(backup_raw) if backup_raw else None
    target_project = Path(target_raw) if target_raw else None
    target_cfx = (target_project / "project.cfx") if target_project else None
    payload["target"] = {"name": target_project.name if target_project else "", "exists": target_project.is_dir() if target_project else False}
    payload["backup"] = {"exists": backup_path.is_file() if backup_path else False, "filename": backup_path.name if backup_path else ""}
    if not backup_path or not backup_path.is_file():
        payload["error"] = "recorded_backup_missing"
        return payload
    if not target_cfx or not target_cfx.is_file():
        payload["error"] = "target_project_cfx_missing"
        return payload
    payload["beforeRollbackDiagnostic"] = mc2_spread_diagnostic(
        project_root,
        root142,
        sqx_project=target_project,
        project_name=None,
        log_limit=log_limit,
    )
    if not apply:
        payload["ok"] = True
        payload["message"] = "Dry-run only. Re-run with --apply to restore the recorded backup."
        written = write_evidence(project_root, f"mc2_spread_promotion_rollback_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
        return payload
    if sqx_processes_running(root142, root143):
        payload["error"] = "sqx_processes_running"
        written = write_evidence(project_root, f"mc2_spread_promotion_rollback_blocked_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
        return payload
    rollback_backup_dir = root142.parent / "SQX_142_Crack_local_backups" / f"sqx142_mc2_spread_rollback_before_{stamp()}"
    rollback_backup_dir.mkdir(parents=True, exist_ok=True)
    current_backup = rollback_backup_dir / "project.cfx"
    shutil.copy2(target_cfx, current_backup)
    shutil.copy2(backup_path, target_cfx)
    payload["currentBackupBeforeRollback"] = {"copied": True, "filename": current_backup.name}
    payload["afterRollbackDiagnostic"] = mc2_spread_diagnostic(
        project_root,
        root142,
        sqx_project=target_project,
        project_name=None,
        log_limit=log_limit,
    )
    payload["ok"] = True
    written = write_evidence(project_root, f"mc2_spread_promotion_rollback_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def create_sequential_diagnostic_variant(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    sqx_project: Path | None,
    project_name: str | None,
    max_passed: int,
    apply: bool,
    allow_source_project: bool,
    skip_passed: int = 0,
    batch_label: str = "",
) -> dict[str, Any]:
    source = resolve_sqx_project(root142, sqx_project, project_name)
    safe_label = re.sub(r"[^A-Za-z0-9_-]+", "_", batch_label).strip("_")[:32]
    target_prefix = f"_PERFQ_SEQBATCH_{safe_label}_" if safe_label else "_PERFQ_SEQDIAG_"
    target = source.parent / f"{target_prefix}{stamp()}"
    mc2_source = source / "databanks" / "MC2"
    sequential_source = source / "databanks" / "Sequential"
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-sequential-diagnostic-variant-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "source": {"name": source.name, "exists": source.is_dir(), "isPerformanceClone": source.name.startswith("_PERFQ_")},
        "target": {"name": target.name, "exists": target.exists()},
        "maxPassedInput": max_passed,
        "skipPassedInput": skip_passed,
        "batchLabel": batch_label,
        "inputDatabank": _databank_mc_snapshot(mc2_source, sample_limit=500),
        "outputDatabank": _databank_basic_snapshot(sequential_source),
        "rules": [
            "Creates a separate _PERFQ_ diagnostic clone; source project is not modified.",
            "Sequential settings are not weakened; only the diagnostic input sample is reduced.",
            "The subset is for runtime/persistence validation only and must not be promoted as final quality evidence.",
        ],
    }
    if max_passed <= 0:
        payload["error"] = "invalid_max_passed"
        return payload
    if skip_passed < 0:
        payload["error"] = "invalid_skip_passed"
        return payload
    if not source.is_dir() or not (source / "project.cfx").is_file():
        payload["error"] = "source_project_missing"
        return payload
    if not source.name.startswith("_PERFQ_") and not allow_source_project:
        payload["error"] = "source_project_protected"
        payload["message"] = "Use a _PERFQ_ clone or pass --allow-source-project intentionally."
        return payload
    input_counts = (payload.get("inputDatabank") or {}).get("resultCounts") or {}
    if int(input_counts.get("passed") or 0) <= 0:
        payload["error"] = "no_passed_mc2_candidates"
        return payload
    if apply and sqx_processes_running(root142, root143):
        payload["error"] = "sqx_processes_running"
        write_evidence(project_root, f"sequential_diag_variant_failed_{stamp()}.json", payload)
        return payload
    if target.exists():
        payload["error"] = "target_exists"
        return payload
    if not apply:
        payload["ok"] = True
        payload["message"] = "Dry-run only. Re-run with --apply to copy the project and keep a small passed MC2 subset."
        written = write_evidence(project_root, f"sequential_diag_variant_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
        return payload

    try:
        shutil.copytree(source, target)
        payload["target"]["exists"] = target.is_dir()
        backup_root = target / "diagnostic_backups" / f"sequential_input_subset_{stamp()}"
        excluded_root = backup_root / "MC2_excluded"
        excluded_root.mkdir(parents=True, exist_ok=True)
        target_mc2 = target / "databanks" / "MC2"
        files = sorted([path for path in target_mc2.glob("*.sqx") if path.is_file()], key=lambda path: path.name.lower())
        summaries = [(path, _read_strategy_mc_summary(path)) for path in files]
        passed_summaries = [(path, summary) for path, summary in summaries if summary.get("filterResult") == "passed"]
        selected = passed_summaries[skip_passed:skip_passed + max_passed]
        keep: set[Path] = set()
        for path, summary in summaries:
            if any(path == selected_path for selected_path, _selected_summary in selected):
                keep.add(path)
        moved = 0
        for path, _summary in summaries:
            if path not in keep:
                path.replace(excluded_root / path.name)
                moved += 1
        payload["subset"] = {
            "keptFiles": len(keep),
            "movedFiles": moved,
            "backupRoot": str(backup_root),
            "selectedFiles": [path.name for path, _summary in selected],
            "selectedRange": {"startPassedIndex": skip_passed + 1, "endPassedIndex": skip_passed + len(selected)},
            "totalPassedAvailable": len(passed_summaries),
        }
        payload["archivedOldSequentialOutput"] = _archive_variant_databanks(target, ["Sequential"], "sequential_diag_output")
        payload["afterInputDatabank"] = _databank_mc_snapshot(target_mc2, sample_limit=500)
        payload["afterQueuePlan"] = project_retest_queue_plan(
            project_root,
            root142,
            sqx_project=target,
            project_name=None,
            log_limit=80,
        )
        payload["ok"] = len(keep) > 0 and target.is_dir()
    except OSError as exc:
        payload["error"] = type(exc).__name__
    written = write_evidence(project_root, f"sequential_diag_variant_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def _parse_batch_sizes(text: str) -> list[int]:
    sizes: list[int] = []
    for part in re.split(r"[,;+\s]+", text.strip()):
        if not part:
            continue
        sizes.append(int(part))
    return sizes


def _passed_mc2_files(databank: Path) -> list[Path]:
    files = sorted([path for path in databank.glob("*.sqx") if path.is_file()], key=lambda path: path.name.lower()) if databank.is_dir() else []
    passed: list[Path] = []
    for path in files:
        if _read_strategy_mc_summary(path).get("filterResult") == "passed":
            passed.append(path)
    return passed


def create_sequential_batch_plan(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    sqx_project: Path | None,
    project_name: str | None,
    batches: str,
    apply: bool,
    allow_source_project: bool,
) -> dict[str, Any]:
    source = resolve_sqx_project(root142, sqx_project, project_name)
    plan_id = f"SEQBATCH_{stamp()}"
    batch_sizes = _parse_batch_sizes(batches)
    passed_files = _passed_mc2_files(source / "databanks" / "MC2")
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-sequential-batch-plan-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "planId": plan_id,
        "source": {"name": source.name, "exists": source.is_dir(), "isPerformanceClone": source.name.startswith("_PERFQ_")},
        "batchesRequested": batch_sizes,
        "passedAvailable": len(passed_files),
        "coverageRequested": sum(batch_sizes),
        "batches": [],
        "rules": [
            "Creates non-overlapping Sequential input clones from passed MC2 candidates.",
            "Each batch runs as its own _PERFQ_ project and keeps Sequential settings unchanged.",
            "Final merge is review-first; it checks coverage and duplicates before copying outputs.",
        ],
    }
    if not batch_sizes or any(size <= 0 for size in batch_sizes):
        payload["error"] = "invalid_batch_sizes"
        return payload
    if not source.is_dir() or not (source / "project.cfx").is_file():
        payload["error"] = "source_project_missing"
        return payload
    if not source.name.startswith("_PERFQ_") and not allow_source_project:
        payload["error"] = "source_project_protected"
        payload["message"] = "Use a _PERFQ_ clone or pass --allow-source-project intentionally."
        return payload
    if sum(batch_sizes) > len(passed_files):
        payload["error"] = "not_enough_passed_candidates"
        return payload
    if apply and sqx_processes_running(root142, root143):
        payload["error"] = "sqx_processes_running"
        write_evidence(project_root, f"sequential_batch_plan_failed_{stamp()}.json", payload)
        return payload

    offset = 0
    for index, size in enumerate(batch_sizes, start=1):
        selected = passed_files[offset:offset + size]
        label = f"{plan_id}_B{index:02d}_{offset + 1:03d}-{offset + size:03d}"
        batch_info: dict[str, Any] = {
            "index": index,
            "size": size,
            "skipPassed": offset,
            "label": label,
            "selectedFiles": [path.name for path in selected],
            "expectedRange": {"startPassedIndex": offset + 1, "endPassedIndex": offset + size},
            "projectName": "",
            "variantEvidence": "",
            "runCommand": "",
        }
        if apply:
            variant = create_sequential_diagnostic_variant(
                project_root,
                root142,
                root143,
                sqx_project=source,
                project_name=None,
                max_passed=size,
                skip_passed=offset,
                batch_label=f"B{index:02d}_{offset + 1:03d}-{offset + size:03d}",
                apply=True,
                allow_source_project=True,
            )
            batch_info["variantOk"] = bool(variant.get("ok"))
            batch_info["projectName"] = str(((variant.get("target") or {}).get("name")) or "")
            batch_info["variantEvidence"] = str(((variant.get("evidence") or {}).get("filename")) or "")
            batch_info["selectedFiles"] = list(((variant.get("subset") or {}).get("selectedFiles")) or batch_info["selectedFiles"])
            if not variant.get("ok"):
                payload["error"] = "batch_variant_failed"
                payload["failedBatch"] = batch_info
                break
        batch_info["runCommand"] = (
            "tools\\sqx142_performance_gate.ps1 queue-task-smoke \"Sequential\" "
            f"--project-name \"{batch_info['projectName'] or '<batch_project_name>'}\" "
            "--apply --max-seconds 1800 --stall-seconds 360 --poll-seconds 20 "
            "--api-ready-timeout 120 --start-settle-seconds 45"
        )
        payload["batches"].append(batch_info)
        offset += size

    payload["mergeReviewCommand"] = f"tools\\sqx142_performance_gate.ps1 sequential-batch-merge-review --plan-evidence <this_evidence_filename>"
    payload["ok"] = not bool(payload.get("error")) and len(payload["batches"]) == len(batch_sizes)
    written = write_evidence(project_root, f"sequential_batch_plan_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    payload["mergeReviewCommand"] = f"tools\\sqx142_performance_gate.ps1 sequential-batch-merge-review --plan-evidence {written.name}"
    return payload


def sequential_batch_merge_review(
    project_root: Path,
    root142: Path,
    *,
    plan_evidence: str,
    apply: bool,
) -> dict[str, Any]:
    evidence_file = evidence_root(project_root) / Path(plan_evidence).name
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-sequential-batch-merge-review-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "planEvidence": evidence_file.name,
        "planExists": evidence_file.is_file(),
        "batches": [],
        "rules": [
            "Review-only by default; no SQX project is modified.",
            "Merge copies Sequential outputs into .local evidence for inspection, not into the master project.",
            "Coverage must match expected batch inputs and duplicate strategy filenames must be zero.",
        ],
    }
    if not evidence_file.is_file():
        payload["error"] = "plan_evidence_missing"
        return payload
    try:
        plan = json.loads(evidence_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        payload["error"] = type(exc).__name__
        return payload

    expected_all: list[str] = []
    produced_all: list[str] = []
    duplicate_outputs: dict[str, int] = {}
    review_root = evidence_root(project_root) / "sequential_merge_reviews" / f"{Path(evidence_file).stem}_{stamp()}"
    output_root = review_root / "Sequential"
    if apply:
        output_root.mkdir(parents=True, exist_ok=True)

    for batch in plan.get("batches") or []:
        project_name = str(batch.get("projectName") or "")
        expected = [str(name) for name in (batch.get("selectedFiles") or [])]
        batch_project = resolve_sqx_project(root142, None, project_name) if project_name else root142 / "user" / "projects" / "__missing__"
        sequential_dir = batch_project / "databanks" / "Sequential"
        output_files = sorted([path for path in sequential_dir.glob("*.sqx") if path.is_file()], key=lambda path: path.name.lower()) if sequential_dir.is_dir() else []
        produced = [path.name for path in output_files]
        missing = sorted(set(expected) - set(produced))
        unexpected = sorted(set(produced) - set(expected))
        for name in produced:
            duplicate_outputs[name] = duplicate_outputs.get(name, 0) + 1
        if apply:
            batch_root = output_root / f"batch_{int(batch.get('index') or 0):02d}_{project_name}"
            batch_root.mkdir(parents=True, exist_ok=True)
            for path in output_files:
                shutil.copy2(path, batch_root / path.name)
        payload["batches"].append({
            "index": batch.get("index"),
            "projectName": project_name,
            "projectExists": batch_project.is_dir(),
            "expected": len(expected),
            "produced": len(produced),
            "missing": missing,
            "unexpected": unexpected,
            "snapshot": _databank_basic_snapshot(sequential_dir),
        })
        expected_all.extend(expected)
        produced_all.extend(produced)

    duplicate_outputs = {name: count for name, count in duplicate_outputs.items() if count > 1}
    payload["summary"] = {
        "expectedTotal": len(expected_all),
        "expectedUnique": len(set(expected_all)),
        "producedTotal": len(produced_all),
        "producedUnique": len(set(produced_all)),
        "missingTotal": len(set(expected_all) - set(produced_all)),
        "unexpectedTotal": len(set(produced_all) - set(expected_all)),
        "duplicateOutputs": duplicate_outputs,
        "reviewRoot": str(review_root) if apply else "",
    }
    payload["ok"] = (
        payload["summary"]["expectedTotal"] > 0
        and payload["summary"]["missingTotal"] == 0
        and payload["summary"]["unexpectedTotal"] == 0
        and not duplicate_outputs
    )
    written = write_evidence(project_root, f"sequential_batch_merge_review_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def _latest_sequential_merge_root(project_root: Path) -> Path | None:
    reviews_root = evidence_root(project_root) / "sequential_merge_reviews"
    if not reviews_root.is_dir():
        return None
    roots = [path for path in reviews_root.iterdir() if path.is_dir()]
    if not roots:
        return None
    return max(roots, key=lambda path: path.stat().st_mtime)


def _xml_text(root: ET.Element | None, tag: str) -> str:
    if root is None:
        return ""
    value = root.findtext(f".//{tag}") or ""
    return " ".join(value.split())


def _xml_attr(root: ET.Element | None, tag: str, attr: str) -> str:
    if root is None:
        return ""
    node = root.find(f".//{tag}")
    return str(node.attrib.get(attr) or "") if node is not None else ""


def _float_value(value: str) -> float | None:
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def _values_differ(left: str, right: str) -> bool:
    left_value = str(left).strip()
    right_value = str(right).strip()
    if not left_value and not right_value:
        return False
    left_float = _float_value(left_value)
    right_float = _float_value(right_value)
    if left_float is not None and right_float is not None:
        return abs(left_float - right_float) > 1e-9
    return left_value != right_value


def _read_sequential_strategy_summary(path: Path, merge_root: Path) -> dict[str, Any]:
    row: dict[str, Any] = {
        "file": path.name,
        "batch": path.parent.name if path.parent != merge_root else "",
        "relativePath": str(path.relative_to(merge_root)),
        "bytes": path.stat().st_size,
        "ok": False,
        "isZip": False,
        "filterResult": "missing",
        "sequentialPassed": "missing",
        "parameterCount": 0,
        "stableAreaTrue": 0,
        "stableAreaFalse": 0,
        "changedParameterCount": 0,
        "changedParameterIds": [],
        "topParameterIds": [],
    }
    try:
        with zipfile.ZipFile(path) as zf:
            row["isZip"] = True
            names = set(zf.namelist())
            settings_root = _parse_xml_text(_safe_zip_text(zf, "settings.xml"))
            if settings_root is not None:
                reason = _xml_text(settings_root, "FiltersResultFailedReason")
                row["filterResult"] = _classify_filter_result(reason)
                row["filterReason"] = _short_reason(reason, limit=160)
                row["strategyName"] = _xml_text(settings_root, "StrategyName")
                row["symbol"] = _xml_text(settings_root, "Symbol")
                row["timeframe"] = _xml_text(settings_root, "Timeframe")
                row["precision"] = _xml_text(settings_root, "Precision")
                row["trades"] = _xml_attr(settings_root, "Fingerprint", "trades")
                row["netProfit"] = _xml_attr(settings_root, "Fingerprint", "profit")
                row["drawdown"] = _xml_attr(settings_root, "Fingerprint", "drawdown")
                row["strategyProblems"] = _xml_text(settings_root, "StrategyProblems")
                row["ambiguousTrades"] = _xml_text(settings_root, "AmbiguousTrades")

            result_files = sorted(name for name in names if name.endswith("SequentialOptimization_Results.xml"))
            row["resultXml"] = result_files[0] if result_files else ""
            if not result_files:
                row["error"] = "missing_sequential_result_xml"
                return row

            result_root = _parse_xml_text(_safe_zip_text(zf, result_files[0]))
            if result_root is None:
                row["error"] = "invalid_sequential_result_xml"
                return row

            row["sequentialPassed"] = str(result_root.attrib.get("passed", "")).lower() or "missing"
            params = result_root.findall(".//Parameter")
            row["parameterCount"] = len(params)
            stable_true = 0
            stable_false = 0
            changed_ids: list[str] = []
            parameter_ids: list[str] = []
            for param in params:
                original = str(param.attrib.get("originalValue") or "")
                variable = param.find("variable")
                param_id = ""
                current = ""
                if variable is not None:
                    param_id = variable.findtext("id") or variable.findtext("name") or ""
                    current = variable.findtext("value") or ""
                param_id = " ".join(param_id.split())
                if param_id:
                    parameter_ids.append(param_id)
                stable = (param.findtext("Results/StableAreaFound") or "").strip().lower()
                if stable == "true":
                    stable_true += 1
                elif stable == "false":
                    stable_false += 1
                if param_id and _values_differ(original, current):
                    changed_ids.append(param_id)

            row["stableAreaTrue"] = stable_true
            row["stableAreaFalse"] = stable_false
            row["changedParameterCount"] = len(changed_ids)
            row["changedParameterIds"] = sorted(set(changed_ids))
            row["topParameterIds"] = sorted(set(parameter_ids))[:20]
            row["ok"] = True
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        row["error"] = type(exc).__name__
    return row


def sequential_final_review(
    project_root: Path,
    *,
    merge_root: Path | None,
    latest: bool,
    apply: bool,
    write_csv: bool,
    sample_limit: int,
    include_paths: bool,
) -> dict[str, Any]:
    selected_root = merge_root
    if latest:
        selected_root = _latest_sequential_merge_root(project_root)
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-sequential-final-review-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "mergeRootSelected": selected_root.name if selected_root else "",
        "mergeRootExists": bool(selected_root and selected_root.is_dir()),
        "rules": [
            "Review-only; no SQX project or databank is modified.",
            "Reads copied Sequential .sqx outputs from .local merge evidence.",
            "CSV is written only under .local when --write-csv --apply is used.",
        ],
    }
    if not selected_root or not selected_root.is_dir():
        payload["error"] = "merge_root_missing"
        return payload

    sqx_files = sorted(selected_root.rglob("*.sqx"), key=lambda path: str(path.relative_to(selected_root)).lower())
    rows = [_read_sequential_strategy_summary(path, selected_root) for path in sqx_files]
    filter_results = [str(row.get("filterResult") or "missing") for row in rows]
    sequential_results = [str(row.get("sequentialPassed") or "missing") for row in rows]
    stable_totals = {
        "stableAreaTrue": sum(int(row.get("stableAreaTrue") or 0) for row in rows),
        "stableAreaFalse": sum(int(row.get("stableAreaFalse") or 0) for row in rows),
    }
    changed_counts = [str(row.get("changedParameterCount") or 0) for row in rows]
    parameter_counts = [str(row.get("parameterCount") or 0) for row in rows]
    changed_param_ids: list[str] = []
    for row in rows:
        changed_param_ids.extend([str(item) for item in (row.get("changedParameterIds") or [])])
    failed_or_invalid = [
        {
            "file": row.get("file"),
            "batch": row.get("batch"),
            "filterResult": row.get("filterResult"),
            "sequentialPassed": row.get("sequentialPassed"),
            "error": row.get("error", ""),
            "filterReason": row.get("filterReason", ""),
        }
        for row in rows
        if not row.get("ok") or row.get("filterResult") != "passed" or row.get("sequentialPassed") != "true"
    ][:sample_limit]

    samples = []
    for row in rows[:sample_limit]:
        sample = {
            "file": row.get("file"),
            "batch": row.get("batch"),
            "filterResult": row.get("filterResult"),
            "sequentialPassed": row.get("sequentialPassed"),
            "parameterCount": row.get("parameterCount"),
            "stableAreaTrue": row.get("stableAreaTrue"),
            "stableAreaFalse": row.get("stableAreaFalse"),
            "changedParameterCount": row.get("changedParameterCount"),
            "changedParameterIds": row.get("changedParameterIds"),
        }
        if include_paths:
            sample["relativePath"] = row.get("relativePath")
        samples.append(sample)

    payload["summary"] = {
        "filesTotal": len(sqx_files),
        "readable": sum(1 for row in rows if row.get("ok")),
        "unreadable": sum(1 for row in rows if not row.get("ok")),
        "filterResults": _counter_dict(filter_results),
        "sequentialPassed": _counter_dict(sequential_results),
        "parameterCountDistribution": _counter_dict(parameter_counts),
        "changedParameterCountDistribution": _counter_dict(changed_counts),
        "stableAreaTotals": stable_totals,
        "topChangedParameterIds": dict(list(_counter_dict(changed_param_ids).items())[:20]),
        "failedOrInvalidSample": failed_or_invalid,
    }
    payload["samples"] = samples
    if include_paths:
        payload["mergeRoot"] = str(selected_root)

    if write_csv:
        if apply:
            csv_root = evidence_root(project_root) / "sequential_final_reviews"
            csv_root.mkdir(parents=True, exist_ok=True)
            csv_path = csv_root / f"sequential_final_review_{stamp()}.csv"
            fieldnames = [
                "batch",
                "file",
                "ok",
                "filterResult",
                "filterReason",
                "sequentialPassed",
                "parameterCount",
                "stableAreaTrue",
                "stableAreaFalse",
                "changedParameterCount",
                "changedParameterIds",
                "strategyName",
                "symbol",
                "timeframe",
                "precision",
                "trades",
                "netProfit",
                "drawdown",
                "resultXml",
                "relativePath",
            ]
            with csv_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                for row in rows:
                    csv_row = {field: row.get(field, "") for field in fieldnames}
                    csv_row["changedParameterIds"] = ";".join(row.get("changedParameterIds") or [])
                    writer.writerow(csv_row)
            payload["csv"] = {"written": True, "filename": csv_path.name, "localPathReturned": include_paths}
            if include_paths:
                payload["csv"]["path"] = str(csv_path)
        else:
            payload["csv"] = {"written": False, "reason": "requires_apply"}

    payload["ok"] = len(sqx_files) > 0 and payload["summary"]["unreadable"] == 0
    written = write_evidence(project_root, f"sequential_final_review_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
    return payload


def clone_performance_project(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    sqx_project: Path | None,
    project_name: str | None,
    apply: bool,
) -> dict[str, Any]:
    source = resolve_sqx_project(root142, sqx_project, project_name)
    clone_name = f"_PERFQ_{source.name}_{stamp()}"
    target = source.parent / clone_name
    total_bytes = 0
    file_count = 0
    if source.is_dir():
        for path in source.rglob("*"):
            if path.is_file():
                file_count += 1
                try:
                    total_bytes += path.stat().st_size
                except OSError:
                    pass
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-performance-project-clone-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "source": {"name": source.name, "exists": source.is_dir()},
        "target": {"name": target.name, "exists": target.exists()},
        "files": file_count,
        "bytes": total_bytes,
        "human": f"{total_bytes / 1024 / 1024:.1f} MB",
        "message": "Dry-run only. Re-run with --apply to create the clone." if not apply else "",
    }
    if not source.is_dir():
        payload["error"] = "source_project_missing"
        return payload
    if apply and sqx_processes_running(root142, root143):
        payload["error"] = "sqx_processes_running"
        write_evidence(project_root, f"project_clone_failed_{stamp()}.json", payload)
        return payload
    if target.exists():
        payload["error"] = "target_exists"
        return payload
    if apply:
        try:
            shutil.copytree(source, target)
            payload["target"]["exists"] = target.is_dir()
            payload["copied"] = True
            payload["ok"] = target.is_dir()
        except OSError as exc:
            payload["error"] = type(exc).__name__
    else:
        payload["ok"] = True
    written = write_evidence(project_root, f"project_clone_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def _set_project_active_task(project_cfx: Path, task_title: str, backup_dir: Path, *, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": False,
        "dryRun": not apply,
        "taskTitle": task_title,
        "changedTags": 0,
        "matched": False,
    }
    if not project_cfx.is_file() or not zipfile.is_zipfile(project_cfx):
        payload["error"] = "project_cfx_missing_or_not_zip"
        return payload
    tmp: Path | None = None
    with zipfile.ZipFile(project_cfx, "r") as source:
        config_text = _safe_zip_text(source, "config.xml")
        if not config_text:
            payload["error"] = "config_xml_missing"
            return payload

        def update_task_tag(match: re.Match[str]) -> str:
            tag = match.group(0)
            title_match = re.search(r'\btitle="([^"]*)"', tag)
            name_match = re.search(r'\bname="([^"]*)"', tag)
            title = (title_match.group(1) if title_match else (name_match.group(1) if name_match else "")).strip()
            desired_active = title.casefold() == task_title.casefold()
            if desired_active:
                payload["matched"] = True
            desired = "true" if desired_active else "false"
            active_match = re.search(r'\bactive="[^"]*"', tag)
            if active_match:
                updated = re.sub(r'\bactive="[^"]*"', f'active="{desired}"', tag, count=1)
            elif tag.endswith("/>"):
                updated = tag[:-2] + f' active="{desired}" />'
            else:
                updated = tag[:-1] + f' active="{desired}">'
            if updated != tag:
                payload["changedTags"] += 1
            return updated

        updated_config = re.sub(r"<Task\b[^>]*>", update_task_tag, config_text)
        if not payload["matched"]:
            payload["error"] = "task_title_not_found"
            return payload
        if not apply:
            payload["ok"] = True
            return payload
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / project_cfx.name
        shutil.copy2(project_cfx, backup)
        tmp = project_cfx.with_suffix(project_cfx.suffix + f".{os.getpid()}.tmp")
        with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as target_zip:
            for item in source.infolist():
                data = updated_config.encode("utf-8") if item.filename == "config.xml" else source.read(item.filename)
                target_zip.writestr(item, data)
    if tmp is not None:
        tmp.replace(project_cfx)
        payload["backup"] = {"copied": True, "path": str(backup)}
        payload["ok"] = True
        return payload
    payload["error"] = "temp_write_not_created"
    return payload


def _start_project_form_from_cfx(project_dir: Path, task_title: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    form: dict[str, Any] = {"projectName": project_dir.name}
    summary: dict[str, Any] = {
        "projectXMLIncluded": False,
        "taskXMLIncluded": False,
        "taskXMLFile": "",
        "activeTaskTitle": "",
        "activeTaskName": "",
        "matchedRequestedTask": False,
        "source": "project.cfx",
    }
    project_cfx = project_dir / "project.cfx"
    if not project_cfx.is_file() or not zipfile.is_zipfile(project_cfx):
        summary["warning"] = "project_cfx_missing_or_not_zip"
        return form, summary

    with zipfile.ZipFile(project_cfx, "r") as zf:
        config_text = _safe_zip_text(zf, "config.xml")
        config_root = _parse_xml_text(config_text)
        if config_root is None:
            summary["warning"] = "config_xml_missing_or_unreadable"
            return form, summary
        form["projectXML"] = config_text
        summary["projectXMLIncluded"] = True

        tasks = list(config_root.findall(".//Task"))
        selected_task: ET.Element | None = None
        requested = (task_title or "").casefold()
        if requested:
            for task in tasks:
                title = task.attrib.get("title", task.attrib.get("name", ""))
                if title.casefold() == requested:
                    selected_task = task
                    summary["matchedRequestedTask"] = True
                    break
        if selected_task is None:
            selected_task = next((task for task in tasks if task.attrib.get("active") == "true"), None)
        if selected_task is None:
            summary["warning"] = "active_task_not_found"
            return form, summary

        task_xml_file = selected_task.attrib.get("taskXMLFile", "")
        summary["taskXMLFile"] = task_xml_file
        summary["activeTaskTitle"] = selected_task.attrib.get("title", selected_task.attrib.get("name", ""))
        summary["activeTaskName"] = selected_task.attrib.get("name", "")
        if task_xml_file:
            task_xml = _safe_zip_text(zf, task_xml_file)
            if task_xml:
                form["taskXMLFile"] = task_xml_file
                form["taskXML"] = task_xml
                summary["taskXMLIncluded"] = True
            else:
                summary["warning"] = "task_xml_missing_or_unreadable"
    return form, summary


def prepare_queue_step(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    sqx_project: Path | None,
    project_name: str | None,
    task_title: str,
    apply: bool,
    launch: bool,
    allow_source_project: bool,
    log_limit: int,
) -> dict[str, Any]:
    target = resolve_sqx_project(root142, sqx_project, project_name)
    queue_plan = project_retest_queue_plan(
        project_root,
        root142,
        sqx_project=sqx_project,
        project_name=project_name,
        log_limit=log_limit,
    )
    queue = queue_plan.get("queue") if isinstance(queue_plan.get("queue"), list) else []
    selected = next((item for item in queue if str(item.get("title", "")).casefold() == task_title.casefold()), None)
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-queue-step-prepare-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "project": {"name": target.name, "exists": target.is_dir(), "isPerformanceClone": target.name.startswith("_PERFQ_")},
        "taskTitle": task_title,
        "queuePlanEvidence": (queue_plan.get("evidence") or {}).get("filename", ""),
        "selectedTask": selected or {},
        "launch": launch,
        "rules": [
            "Only one task is activated in project.cfx.",
            "Source projects are protected unless --allow-source-project is explicit.",
            "Heavy retests keep their existing simulations and filters.",
        ],
    }
    if not target.is_dir() or not (target / "project.cfx").is_file():
        payload["error"] = "project_missing"
        return payload
    if selected is None:
        payload["error"] = "task_not_found"
        payload["availableTasks"] = [item.get("title") for item in queue]
        return payload
    if selected.get("omittedByOperator"):
        payload["error"] = "task_omitted_by_operator_policy"
        payload["message"] = f"{selected.get('title')} is omitted from tests/optimization by operator decision."
        write_evidence(project_root, f"queue_step_prepare_failed_{stamp()}.json", payload)
        return payload
    if selected.get("blockedByOmittedInput"):
        payload["error"] = "task_depends_on_omitted_input"
        payload["message"] = (
            f"{selected.get('title')} depends on omitted input databank "
            f"'{selected.get('inputDatabank')}'."
        )
        write_evidence(project_root, f"queue_step_prepare_failed_{stamp()}.json", payload)
        return payload
    if not target.name.startswith("_PERFQ_") and not allow_source_project:
        payload["error"] = "source_project_protected"
        payload["message"] = "Use a _PERFQ_ clone or pass --allow-source-project intentionally."
        return payload
    if apply and sqx_processes_running(root142, root143):
        payload["error"] = "sqx_processes_running"
        write_evidence(project_root, f"queue_step_prepare_failed_{stamp()}.json", payload)
        return payload

    backup_dir = root142.parent / "SQX_142_Crack_local_backups" / f"sqx142_queue_step_before_{stamp()}"
    active_result = _set_project_active_task(target / "project.cfx", str(selected.get("title", task_title)), backup_dir, apply=apply)
    payload["activeTaskUpdate"] = active_result
    recommended_profile = str(selected.get("recommendedProfile") or "baseline_143_safe")
    payload["profileApply"] = apply_profile(project_root, root142, root143, recommended_profile, apply=apply)
    payload["beforeSnapshotCommand"] = (
        "tools\\sqx142_performance_gate.ps1 project-mc-snapshot "
        f"--project-name \"{target.name}\" --sample-limit 500"
    )
    payload["afterTaskCommands"] = [
        payload["beforeSnapshotCommand"],
        f"tools\\sqx142_performance_gate.ps1 project-log-summary --project-name \"{target.name}\" --limit {log_limit}",
        "tools\\sqx142_performance_gate.ps1 project-mc-diff",
    ]
    launcher = root142 / "StrategyQuantX_nocheck.exe"
    payload["launcherExists"] = launcher.is_file()
    if launch:
        if not apply:
            payload["message"] = "Dry-run only. Re-run with --apply --launch to launch SQX 142."
        elif launcher.is_file():
            proc = subprocess.Popen([str(launcher)], cwd=str(root142))  # noqa: S603
            payload["launchedPid"] = proc.pid
        else:
            payload["error"] = "launcher_missing"
    payload["ok"] = bool(active_result.get("ok")) and bool((payload["profileApply"] or {}).get("ok")) and not bool(payload.get("error"))
    written = write_evidence(project_root, f"queue_step_prepare_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def _post_sqx_local_api(
    base_url: str,
    endpoint: str,
    form: dict[str, Any],
    timeout: int,
    *,
    token: str | None = None,
    browser_token: str | None = None,
    gzip_body: bool = True,
    opener: urllib.request.OpenerDirector | None = None,
) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/" + endpoint.lstrip("/")
    body = urllib.parse.urlencode({key: str(value) for key, value in form.items()}).encode("utf-8")
    headers = {}
    if gzip_body:
        body = gzip.compress(body)
        headers["Content-Type"] = "application/json; charset=x-user-defined-binary"
        headers["Content-Encoding"] = "gzip"
    else:
        headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    if token:
        headers["sq-auth-token"] = token
    if browser_token:
        headers["browserToken"] = browser_token
    headers.update({
        "Accept": "application/json, text/plain, */*",
        "Origin": base_url.rstrip("/"),
        "Referer": base_url.rstrip("/") + "/",
        "User-Agent": "Mozilla/5.0 SQX142PerformanceGate",
        "X-Requested-With": "XMLHttpRequest",
    })
    request = urllib.request.Request(
        url,
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        open_fn = opener.open if opener else urllib.request.urlopen
        with open_fn(request, timeout=timeout) as response:  # noqa: S310
            text = response.read().decode("utf-8", errors="replace")
            parsed: Any
            try:
                parsed = json.loads(text) if text.strip() else None
            except json.JSONDecodeError:
                parsed = text[:500]
            return {
                "ok": 200 <= response.status < 300,
                "statusCode": response.status,
                "response": parsed,
            }
    except urllib.error.HTTPError as exc:
        try:
            text = exc.read().decode("utf-8", errors="replace")
        except OSError:
            text = ""
        parsed: Any = text[:500]
        try:
            parsed = json.loads(text) if text.strip() else parsed
        except json.JSONDecodeError:
            pass
        return {
            "ok": False,
            "statusCode": exc.code,
            "error": "sqx_local_api_http_error",
            "message": exc.reason,
            "response": parsed,
        }
    except urllib.error.URLError as exc:
        return {
            "ok": False,
            "error": "sqx_local_api_unreachable",
            "message": str(exc.reason if hasattr(exc, "reason") else exc),
        }
    except TimeoutError:
        return {"ok": False, "error": "sqx_local_api_timeout"}


def _read_browser_token(root142: Path) -> str:
    settings = root142 / "user" / "settings" / "settings.xml"
    try:
        tree = ET.parse(settings)
        value = (tree.getroot().findtext("BrowserToken") or "").strip()
        return value
    except (OSError, ET.ParseError):
        return ""


def _login_sqx_local_api(
    base_url: str,
    timeout: int,
    root142: Path,
    opener: urllib.request.OpenerDirector | None = None,
) -> tuple[str | None, dict[str, Any]]:
    browser_token = _read_browser_token(root142)
    _get_sqx_local_api(base_url, timeout, browser_token=browser_token, opener=opener)
    result = _post_sqx_local_api(
        base_url,
        "main/login",
        {"password": ""},
        timeout,
        token=None,
        browser_token=browser_token,
        gzip_body=True,
        opener=opener,
    )
    response = result.get("response") if isinstance(result.get("response"), dict) else {}
    token = str(response.get("token") or "") if isinstance(response, dict) else ""
    public = {
        "ok": bool(result.get("ok")) and bool(response.get("success")) and bool(token),
        "statusCode": result.get("statusCode"),
        "success": bool(response.get("success")) if isinstance(response, dict) else False,
        "tokenReceived": bool(token),
        "method": "empty_password_login",
        "error": result.get("error") or (response.get("error") if isinstance(response, dict) else ""),
    }
    if token:
        return token, public

    if browser_token:
        public.update({
            "ok": True,
            "method": "browser_token_local_session",
            "fallbackUsed": True,
            "tokenReceived": True,
            "loginStatusCode": result.get("statusCode"),
            "error": "",
        })
        return browser_token, public
    return (token or None), public


def _get_sqx_local_api(
    base_url: str,
    timeout: int,
    endpoint: str = "",
    token: str | None = None,
    browser_token: str | None = None,
    opener: urllib.request.OpenerDirector | None = None,
) -> dict[str, Any]:
    try:
        url = base_url.rstrip("/") + "/" + endpoint.lstrip("/")
        headers = {"sq-auth-token": token} if token else {}
        if browser_token:
            headers["browserToken"] = browser_token
        headers.update({
            "Accept": "application/json, text/plain, */*",
            "Referer": base_url.rstrip("/") + "/",
            "User-Agent": "Mozilla/5.0 SQX142PerformanceGate",
            "X-Requested-With": "XMLHttpRequest",
        })
        request = urllib.request.Request(url, headers=headers, method="GET")
        open_fn = opener.open if opener else urllib.request.urlopen
        with open_fn(request, timeout=timeout) as response:  # noqa: S310
            text = response.read(500).decode("utf-8", errors="replace")
            parsed: Any = text
            try:
                parsed = json.loads(text) if text.strip().startswith(("{", "[")) else text
            except json.JSONDecodeError:
                parsed = text
            return {
                "ok": 200 <= response.status < 300,
                "statusCode": response.status,
                "responseSample": text[:500] if isinstance(parsed, str) else "",
                "response": parsed if isinstance(parsed, dict) else None,
            }
    except urllib.error.HTTPError as exc:
        try:
            text = exc.read().decode("utf-8", errors="replace")
        except OSError:
            text = ""
        return {
            "ok": False,
            "statusCode": exc.code,
            "error": "sqx_local_api_http_error",
            "message": exc.reason,
            "responseSample": text[:500],
        }
    except urllib.error.URLError as exc:
        return {
            "ok": False,
            "error": "sqx_local_api_unreachable",
            "message": str(exc.reason if hasattr(exc, "reason") else exc),
        }
    except TimeoutError:
        return {"ok": False, "error": "sqx_local_api_timeout"}


def sqx_local_api(
    project_root: Path,
    root142: Path,
    *,
    action: str,
    project_name: str,
    task_title: str | None,
    active: bool,
    apply: bool,
    allow_source_project: bool,
    base_url: str,
    timeout: int,
) -> dict[str, Any]:
    is_performance_clone = project_name.startswith("_PERFQ_")
    endpoint = ""
    form: dict[str, Any] = {"projectName": project_name}
    selected: dict[str, Any] | None = None

    start_payload_summary: dict[str, Any] = {}
    if action == "start-project":
        endpoint = "project/start"
        project_dir = resolve_sqx_project(root142, None, project_name)
        form, start_payload_summary = _start_project_form_from_cfx(project_dir, task_title)
    elif action == "stop-project":
        endpoint = "project/stop"
    elif action == "check-access":
        endpoint = "main/checkaccess"
    elif action == "activate-task":
        if not task_title:
            return {"ok": False, "version": "sqx142-local-api-v1", "error": "task_title_required"}
        queue_plan = project_retest_queue_plan(
            project_root,
            root142,
            sqx_project=None,
            project_name=project_name,
            log_limit=80,
        )
        queue = queue_plan.get("queue") if isinstance(queue_plan.get("queue"), list) else []
        selected = next((item for item in queue if str(item.get("title", "")).casefold() == task_title.casefold()), None)
        if selected is None:
            return {
                "ok": False,
                "version": "sqx142-local-api-v1",
                "error": "task_not_found",
                "availableTasks": [item.get("title") for item in queue],
            }
        endpoint = "taskmanager/activateTask"
        form.update({
            "taskType": selected.get("type", ""),
            "taskName": selected.get("name") or selected.get("title", ""),
            "active": str(active).lower(),
        })
    elif action == "probe":
        endpoint = ""
        form = {}
    else:
        return {"ok": False, "version": "sqx142-local-api-v1", "error": "unknown_action"}

    mutates_project = action in {"start-project", "activate-task"}
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-local-api-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "baseUrl": base_url,
        "endpoint": endpoint,
        "action": action,
        "project": {"name": project_name, "isPerformanceClone": is_performance_clone},
        "selectedTask": selected or {},
        "startPayload": start_payload_summary,
        "formKeys": sorted(form),
        "rules": [
            "Local SQX API only; never exposed to remote testers.",
            "Dry-run by default.",
            "Mutating project actions require --apply.",
        ],
    }
    if mutates_project and not is_performance_clone and not allow_source_project:
        payload["error"] = "source_project_protected"
        payload["message"] = "Use a _PERFQ_ clone or pass --allow-source-project intentionally."
        return payload
    if not apply:
        payload["ok"] = True
        payload["message"] = "Dry-run only. Re-run with --apply to call SQX local API."
        return payload

    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    token = None
    browser_token = _read_browser_token(root142)
    if action not in {"probe"}:
        token, login_public = _login_sqx_local_api(base_url, timeout, root142, opener=opener)
        payload["login"] = login_public
        browser_token = _read_browser_token(root142) or browser_token
        if not token:
            payload["apiResult"] = {"ok": False, "error": "sqx_local_login_failed"}
            written = write_evidence(project_root, f"sqx_local_api_{action}_{stamp()}.json", payload)
            payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
            return payload

    if action == "probe":
        payload["apiResult"] = _get_sqx_local_api(base_url, timeout, browser_token=browser_token, opener=opener)
    elif action == "check-access":
        payload["apiResult"] = _get_sqx_local_api(
            base_url,
            timeout,
            endpoint,
            token=token,
            browser_token=browser_token,
            opener=opener,
        )
    else:
        payload["apiResult"] = _post_sqx_local_api(
            base_url,
            endpoint,
            form,
            timeout,
            token=token,
            browser_token=browser_token,
            gzip_body=True,
            opener=opener,
        )
    payload["ok"] = bool((payload["apiResult"] or {}).get("ok"))
    written = write_evidence(project_root, f"sqx_local_api_{action}_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def _wait_for_sqx_local_api(base_url: str, *, timeout_seconds: int, poll_seconds: int) -> dict[str, Any]:
    started = time.perf_counter()
    attempts = []
    while (time.perf_counter() - started) <= timeout_seconds:
        result = _get_sqx_local_api(base_url, timeout=5)
        attempts.append({
            "elapsedSeconds": round(time.perf_counter() - started, 2),
            "ok": bool(result.get("ok")),
            "statusCode": result.get("statusCode"),
            "error": result.get("error", ""),
        })
        if result.get("ok"):
            return {
                "ok": True,
                "elapsedSeconds": round(time.perf_counter() - started, 2),
                "attempts": attempts,
            }
        time.sleep(max(1, poll_seconds))
    return {
        "ok": False,
        "elapsedSeconds": round(time.perf_counter() - started, 2),
        "attempts": attempts,
        "error": "sqx_local_api_not_ready",
    }


def _latest_task_entry(log_summary: dict[str, Any], task_title: str) -> dict[str, Any]:
    bucket = (log_summary.get("byTask") or {}).get(task_title) or {}
    latest = bucket.get("latest") if isinstance(bucket.get("latest"), dict) else {}
    return latest


def _is_newer_iso(value: str, marker: datetime) -> bool:
    if not value:
        return False
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return False
    return parsed >= marker.replace(microsecond=0)


def _latest_global_task_activity(root142: Path, task_title: str, marker: datetime, tail_bytes: int = 4 * 1024 * 1024) -> dict[str, Any]:
    logs_dir = root142 / "user" / "log" / "StrategyQuant"
    candidates = sorted(logs_dir.glob("log_*.log"), key=lambda path: path.stat().st_mtime if path.exists() else 0, reverse=True)
    if not candidates:
        return {"active": False}
    path = candidates[0]
    try:
        with path.open("rb") as handle:
            size = handle.seek(0, os.SEEK_END)
            handle.seek(max(0, size - tail_bytes), os.SEEK_SET)
            text = handle.read().decode("utf-8", errors="replace")
    except OSError:
        return {"active": False}

    escaped = re.escape(task_title)
    pattern = re.compile(rf"(?m)^(\d{{2}}:\d{{2}}:\d{{2}}\.\d{{3}}).*?ProgressEngine\s+-\s+{escaped}\s+:\s+(.+)$")
    latest: dict[str, Any] = {"active": False}
    for match in pattern.finditer(text):
        try:
            clock = datetime.strptime(match.group(1), "%H:%M:%S.%f")
        except ValueError:
            continue
        seen_at = marker.replace(hour=clock.hour, minute=clock.minute, second=clock.second, microsecond=clock.microsecond)
        if seen_at < marker:
            continue
        message = " ".join(match.group(2).split())
        latest = {
            "active": True,
            "at": seen_at.isoformat(timespec="milliseconds"),
            "message": _short_reason(message, 220),
            "file": path.name,
        }
    return latest


def queue_task_smoke(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    project_name: str,
    task_title: str,
    apply: bool,
    launch: bool,
    allow_source_project: bool,
    base_url: str,
    max_seconds: int,
    stall_seconds: int,
    poll_seconds: int,
    api_ready_timeout: int,
    start_settle_seconds: int,
    restore_profile: str,
) -> dict[str, Any]:
    target = resolve_sqx_project(root142, None, project_name)
    launcher = root142 / "StrategyQuantX_nocheck.exe"
    safe_project = target.name.startswith("_PERFQ_")
    queue_plan = project_retest_queue_plan(
        project_root,
        root142,
        sqx_project=None,
        project_name=target.name,
        log_limit=80,
    )
    queue = queue_plan.get("queue") if isinstance(queue_plan.get("queue"), list) else []
    selected = next((item for item in queue if str(item.get("title", "")).casefold() == task_title.casefold()), None)
    output_name = str((selected or {}).get("outputDatabank") or task_title)
    output_databank = target / "databanks" / output_name
    expected_output_count = int(((selected or {}).get("inputCandidateStatus") or {}).get("passed") or 0)
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-queue-task-smoke-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "project": {"name": target.name, "exists": target.is_dir(), "isPerformanceClone": safe_project},
        "taskTitle": task_title,
        "selectedTask": selected or {},
        "baseUrl": base_url,
        "expectedOutputCount": expected_output_count,
        "maxSeconds": max_seconds,
        "stallSeconds": stall_seconds,
        "pollSeconds": poll_seconds,
        "startSettleSeconds": start_settle_seconds,
        "restoreProfile": restore_profile,
        "queuePlanEvidence": (queue_plan.get("evidence") or {}).get("filename", ""),
        "beforeDatabank": _databank_basic_snapshot(output_databank),
        "launcherExists": launcher.is_file(),
        "observations": [],
        "rules": [
            "Runs one queue task only on a _PERFQ_ clone unless explicitly allowed.",
            "The smoke measures natural output; it does not lower filters or force pass status.",
            "SQX is stopped, closed and baseline profile restored at the end.",
        ],
    }
    if not target.is_dir() or not (target / "project.cfx").is_file():
        payload["error"] = "project_missing"
        return payload
    if selected is None:
        payload["error"] = "task_not_found"
        payload["availableTasks"] = [item.get("title") for item in queue]
        return payload
    blockers = _queue_task_blockers(selected)
    if blockers:
        payload["error"] = "task_blocked"
        payload["blockers"] = blockers
        write_evidence(project_root, f"queue_task_smoke_blocked_{stamp()}.json", payload)
        return payload
    if not safe_project and not allow_source_project:
        payload["error"] = "source_project_protected"
        payload["message"] = "Use a _PERFQ_ clone or pass --allow-source-project intentionally."
        return payload
    if restore_profile not in PROFILE_CONFIGS:
        payload["error"] = "unknown_restore_profile"
        payload["availableProfiles"] = sorted(PROFILE_CONFIGS)
        return payload
    if not apply:
        payload["ok"] = True
        payload["message"] = "Dry-run only. Re-run with --apply to prepare, launch, run and close."
        payload["plannedCommands"] = [
            f"prepare-queue-step \"{task_title}\" --project-name \"{target.name}\" --apply",
            f"sqx-local-api start-project --project-name \"{target.name}\" --task-title \"{task_title}\" --apply",
        ]
        written = write_evidence(project_root, f"queue_task_smoke_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
        return payload
    if sqx_processes_running(root142, root143):
        payload["error"] = "sqx_processes_running"
        write_evidence(project_root, f"queue_task_smoke_failed_{stamp()}.json", payload)
        return payload
    if not launcher.is_file():
        payload["error"] = "launcher_missing"
        write_evidence(project_root, f"queue_task_smoke_failed_{stamp()}.json", payload)
        return payload
    if int((payload["beforeDatabank"] or {}).get("strategyFiles") or 0) > 0:
        payload["preRunOutputArchive"] = _archive_variant_databanks(target, [output_name], "queue_task_smoke_output")
        payload["beforeDatabank"] = _databank_basic_snapshot(output_databank)

    smoke_started_at = datetime.now()
    started_perf = time.perf_counter()
    last_progress = started_perf
    start_count = int((payload["beforeDatabank"] or {}).get("strategyFiles") or 0)
    start_newest = str((payload["beforeDatabank"] or {}).get("newestModified") or "")
    outcome = "not_started"
    ever_progress = False
    current_log_total = 0
    sqx_started = False
    last_live_activity_at = ""
    try:
        payload["prepare"] = prepare_queue_step(
            project_root,
            root142,
            root143,
            sqx_project=None,
            project_name=target.name,
            task_title=task_title,
            apply=True,
            launch=False,
            allow_source_project=True,
            log_limit=80,
        )
        should_start = True
        if not (payload["prepare"] or {}).get("ok"):
            payload["error"] = "prepare_failed"
            outcome = "prepare_failed"
            should_start = False
        if should_start and launch:
            proc = subprocess.Popen([str(launcher)], cwd=str(root142))  # noqa: S603
            payload["launchedPid"] = proc.pid
        if should_start:
            payload["apiReady"] = _wait_for_sqx_local_api(base_url, timeout_seconds=api_ready_timeout, poll_seconds=5)
            if not (payload["apiReady"] or {}).get("ok"):
                payload["error"] = "api_not_ready"
                outcome = "api_not_ready"
                should_start = False
        if should_start and start_settle_seconds > 0:
            payload["startSettle"] = {
                "seconds": start_settle_seconds,
                "reason": "SQX API can be ready while projects/databanks are still loading; UI Start is effectively later.",
            }
            time.sleep(start_settle_seconds)
        if should_start:
            smoke_started_at = datetime.now()
            payload["startApi"] = sqx_local_api(
                project_root,
                root142,
                action="start-project",
                project_name=target.name,
                task_title=task_title,
                active=True,
                apply=True,
                allow_source_project=True,
                base_url=base_url,
                timeout=20,
            )
            if not (payload["startApi"] or {}).get("ok"):
                payload["error"] = "start_api_failed"
                outcome = "start_api_failed"
                should_start = False
            else:
                sqx_started = True
                last_progress = time.perf_counter()

        if should_start:
            outcome = "running"
        poll_started = should_start
        while should_start and (time.perf_counter() - started_perf) <= max_seconds:
            time.sleep(max(1, poll_seconds))
            elapsed = round(time.perf_counter() - started_perf, 2)
            db_now = _databank_basic_snapshot(output_databank, sample_limit=8)
            count_now = int(db_now.get("strategyFiles") or 0)
            newest_now = str(db_now.get("newestModified") or "")
            progress = count_now > start_count or (newest_now and newest_now != start_newest)
            if progress:
                ever_progress = True
                last_progress = time.perf_counter()
            log_summary = project_log_summary(
                project_root,
                root142,
                sqx_project=None,
                project_name=target.name,
                limit=8,
            )
            latest = _latest_task_entry(log_summary, task_title)
            latest_is_current = _is_newer_iso(str(latest.get("startedAt", "")), smoke_started_at)
            live_activity = _latest_global_task_activity(root142, task_title, smoke_started_at)
            if live_activity.get("active") and live_activity.get("at") != last_live_activity_at:
                last_live_activity_at = str(live_activity.get("at") or "")
                ever_progress = True
                last_progress = time.perf_counter()
            try:
                current_log_total = int(latest.get("total") or 0) if latest_is_current else current_log_total
            except (TypeError, ValueError):
                current_log_total = 0
            payload["observations"].append({
                "elapsedSeconds": elapsed,
                "databank": db_now,
                "progress": progress,
                "secondsSinceProgress": round(time.perf_counter() - last_progress, 2),
                "latestTaskLog": {
                    "ok": latest.get("ok"),
                    "file": latest.get("file", ""),
                    "startedAt": latest.get("startedAt", ""),
                    "finishedAt": latest.get("finishedAt", ""),
                    "durationText": latest.get("durationText", ""),
                    "passed": latest.get("passed"),
                    "failed": latest.get("failed"),
                    "total": latest.get("total"),
                    "isCurrentSmoke": latest_is_current,
                },
                "liveTaskActivity": live_activity,
            })
            if latest.get("ok") and latest_is_current:
                outcome = "completed" if progress or current_log_total > 0 else "completed_without_work"
                break
            if expected_output_count > 0 and count_now >= expected_output_count and progress:
                outcome = "completed"
                payload["databankCoverageCompletion"] = {
                    "reason": "Output databank reached expected input candidate count during polling.",
                    "expectedOutputCount": expected_output_count,
                    "actualOutputCount": count_now,
                }
                break
            if (time.perf_counter() - last_progress) >= stall_seconds:
                outcome = "stalled_after_progress" if progress or count_now > start_count else "stalled_without_progress"
                break
        else:
            if poll_started:
                outcome = "timeout"
    finally:
        if sqx_started:
            payload["stopApi"] = sqx_local_api(
                project_root,
                root142,
                action="stop-project",
                project_name=target.name,
                task_title=None,
                active=True,
                apply=True,
                allow_source_project=True,
                base_url=base_url,
                timeout=10,
            )
        else:
            payload["stopApi"] = {"ok": True, "skipped": True, "reason": outcome}
        time.sleep(5)
        payload["close"] = close_sqx_processes(root142)
        payload["restore"] = apply_profile(project_root, root142, root143, restore_profile, apply=True)

    payload["elapsedSeconds"] = round(time.perf_counter() - started_perf, 2)
    payload["afterDatabank"] = _databank_basic_snapshot(output_databank)
    payload["afterMcSnapshot"] = _databank_mc_snapshot(output_databank, sample_limit=500)
    payload["afterLogSummary"] = project_log_summary(project_root, root142, sqx_project=None, project_name=target.name, limit=12)
    payload["afterStatus"] = build_sqx142_performance_status(project_root, root142, root143, include_paths=False)
    payload["hsErrCount"] = len(list(root142.glob("hs_err_pid*.log")))
    after_count = int((payload["afterDatabank"] or {}).get("strategyFiles") or 0)
    after_newest = str((payload["afterDatabank"] or {}).get("newestModified") or "")
    post_latest = _latest_task_entry(payload["afterLogSummary"], task_title)
    post_latest_is_current = _is_newer_iso(str(post_latest.get("startedAt", "")), smoke_started_at)
    try:
        post_total = int(post_latest.get("total") or 0) if post_latest_is_current else 0
    except (TypeError, ValueError):
        post_total = 0
    if post_latest.get("ok") and post_latest_is_current and (after_count > start_count or post_total > 0):
        if outcome != "completed":
            payload["posthocCompletion"] = {
                "previousOutcome": outcome,
                "reason": "Task completion was visible in final SQX logs after polling stopped.",
            }
        outcome = "completed"
        current_log_total = max(current_log_total, post_total)
    if outcome != "completed" and expected_output_count > 0 and after_count >= expected_output_count and (after_count > start_count or after_newest != start_newest):
        payload["posthocCoverageCompletion"] = {
            "previousOutcome": outcome,
            "reason": "Output databank reached expected input candidate count even though SQX log summary did not expose a final task block.",
            "expectedOutputCount": expected_output_count,
            "actualOutputCount": after_count,
        }
        outcome = "completed"
    payload["postRunLatestTaskLog"] = {
        "ok": post_latest.get("ok"),
        "file": post_latest.get("file", ""),
        "startedAt": post_latest.get("startedAt", ""),
        "finishedAt": post_latest.get("finishedAt", ""),
        "durationText": post_latest.get("durationText", ""),
        "passed": post_latest.get("passed"),
        "failed": post_latest.get("failed"),
        "total": post_latest.get("total"),
        "isCurrentSmoke": post_latest_is_current,
    }
    payload["outcome"] = outcome
    payload["automationOk"] = (
        bool((payload.get("startApi") or {}).get("ok"))
        and bool((payload.get("stopApi") or {}).get("ok"))
        and bool((payload.get("restore") or {}).get("ok"))
        and int(((payload.get("close") or {}).get("result") or {}).get("leftAfterForce") or 0) == 0
        and not ((payload.get("afterStatus") or {}).get("warnings") or [])
        and payload["hsErrCount"] == 0
    )
    payload["methodologicalProgress"] = bool(
        ever_progress
        or after_count > start_count
        or (after_newest and after_newest != start_newest)
        or current_log_total > 0
    )
    payload["ok"] = bool(payload["automationOk"] and payload["methodologicalProgress"] and outcome == "completed")
    written = write_evidence(project_root, f"queue_task_smoke_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def sequential_smoke(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    project_name: str,
    apply: bool,
    launch: bool,
    allow_source_project: bool,
    base_url: str,
    max_seconds: int,
    stall_seconds: int,
    poll_seconds: int,
    api_ready_timeout: int,
    restore_profile: str,
) -> dict[str, Any]:
    target = resolve_sqx_project(root142, None, project_name)
    output_databank = target / "databanks" / "Sequential"
    launcher = root142 / "StrategyQuantX_nocheck.exe"
    safe_project = target.name.startswith("_PERFQ_")
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-sequential-smoke-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "project": {"name": target.name, "exists": target.is_dir(), "isPerformanceClone": safe_project},
        "taskTitle": "Sequential",
        "baseUrl": base_url,
        "maxSeconds": max_seconds,
        "stallSeconds": stall_seconds,
        "pollSeconds": poll_seconds,
        "restoreProfile": restore_profile,
        "rules": [
            "Sequential runs only on a _PERFQ_ clone unless --allow-source-project is explicit.",
            "The smoke measures progress; it does not lower simulations, filters or methodology.",
            "SQX is closed by the process guard at the end of the smoke.",
        ],
        "beforeDatabank": _databank_basic_snapshot(output_databank),
        "launcherExists": launcher.is_file(),
        "observations": [],
    }
    if not target.is_dir() or not (target / "project.cfx").is_file():
        payload["error"] = "project_missing"
        return payload
    if not safe_project and not allow_source_project:
        payload["error"] = "source_project_protected"
        payload["message"] = "Use a _PERFQ_ clone or pass --allow-source-project intentionally."
        return payload
    if restore_profile not in PROFILE_CONFIGS:
        payload["error"] = "unknown_restore_profile"
        payload["availableProfiles"] = sorted(PROFILE_CONFIGS)
        return payload
    if not apply:
        payload["ok"] = True
        payload["message"] = "Dry-run only. Re-run with --apply to prepare, launch and run the Sequential smoke."
        payload["plannedCommands"] = [
            f"prepare-queue-step Sequential --project-name \"{target.name}\" --apply",
            f"sqx-local-api start-project --project-name \"{target.name}\" --apply",
            f"poll Sequential databank for up to {max_seconds}s, stalled after {stall_seconds}s",
        ]
        return payload
    if sqx_processes_running(root142, root143):
        payload["error"] = "sqx_processes_running"
        write_evidence(project_root, f"sequential_smoke_failed_{stamp()}.json", payload)
        return payload
    if not launcher.is_file():
        payload["error"] = "launcher_missing"
        write_evidence(project_root, f"sequential_smoke_failed_{stamp()}.json", payload)
        return payload

    smoke_started_at = datetime.now()
    started_perf = time.perf_counter()
    last_progress = started_perf
    start_count = int((payload["beforeDatabank"] or {}).get("strategyFiles") or 0)
    start_newest = str((payload["beforeDatabank"] or {}).get("newestModified") or "")
    outcome = "not_started"
    ever_progress = False
    current_log_total = 0
    sqx_started = False
    try:
        payload["prepare"] = prepare_queue_step(
            project_root,
            root142,
            root143,
            sqx_project=None,
            project_name=target.name,
            task_title="Sequential",
            apply=True,
            launch=False,
            allow_source_project=True,
            log_limit=80,
        )
        should_start = True
        if not (payload["prepare"] or {}).get("ok"):
            payload["error"] = "prepare_failed"
            outcome = "prepare_failed"
            should_start = False
        if should_start:
            selected_task = (payload.get("prepare") or {}).get("selectedTask") or {}
            input_databank_name = str(selected_task.get("inputDatabank") or "")
            if input_databank_name:
                input_snapshot = _databank_mc_snapshot(target / "databanks" / input_databank_name, sample_limit=500)
                input_counts = input_snapshot.get("resultCounts") or {}
                input_passed = int(input_counts.get("passed") or 0)
                payload["inputDatabank"] = input_snapshot
                payload["inputCandidatePolicy"] = {
                    "requiresPassedInputCandidates": True,
                    "passedInputCandidates": input_passed,
                    "strategyFiles": input_snapshot.get("strategyFiles", 0),
                }
                if input_snapshot.get("strategyFiles", 0) > 0 and input_passed <= 0:
                    payload["error"] = "no_passed_input_candidates"
                    payload["message"] = (
                        f"Sequential input databank '{input_databank_name}' has 0 passed candidates; "
                        "skipping SQX launch to avoid a 0-total run."
                    )
                    outcome = "no_input_candidates"
                    should_start = False
        if should_start and launch:
            proc = subprocess.Popen([str(launcher)], cwd=str(root142))  # noqa: S603
            payload["launchedPid"] = proc.pid
        if should_start:
            payload["apiReady"] = _wait_for_sqx_local_api(base_url, timeout_seconds=api_ready_timeout, poll_seconds=5)
            if not (payload["apiReady"] or {}).get("ok"):
                payload["error"] = "api_not_ready"
                outcome = "api_not_ready"
                should_start = False
        if should_start:
            payload["startApi"] = sqx_local_api(
                project_root,
                root142,
                action="start-project",
                project_name=target.name,
                task_title=None,
                active=True,
                apply=True,
                allow_source_project=True,
                base_url=base_url,
                timeout=20,
            )
            if not (payload["startApi"] or {}).get("ok"):
                payload["error"] = "start_api_failed"
                outcome = "start_api_failed"
                should_start = False
            else:
                sqx_started = True

        if should_start:
            outcome = "running"
        poll_started = should_start
        while should_start and (time.perf_counter() - started_perf) <= max_seconds:
            time.sleep(max(1, poll_seconds))
            elapsed = round(time.perf_counter() - started_perf, 2)
            db_now = _databank_basic_snapshot(output_databank, sample_limit=5)
            count_now = int(db_now.get("strategyFiles") or 0)
            newest_now = str(db_now.get("newestModified") or "")
            progress = count_now > start_count or (newest_now and newest_now != start_newest)
            if progress:
                ever_progress = True
                last_progress = time.perf_counter()
            log_summary = project_log_summary(
                project_root,
                root142,
                sqx_project=None,
                project_name=target.name,
                limit=8,
            )
            latest = _latest_task_entry(log_summary, "Sequential")
            latest_is_current = _is_newer_iso(str(latest.get("startedAt", "")), smoke_started_at)
            try:
                current_log_total = int(latest.get("total") or 0) if latest_is_current else current_log_total
            except (TypeError, ValueError):
                current_log_total = 0
            observation = {
                "elapsedSeconds": elapsed,
                "databank": db_now,
                "progress": progress,
                "secondsSinceProgress": round(time.perf_counter() - last_progress, 2),
                "latestSequentialLog": {
                    "ok": latest.get("ok"),
                    "file": latest.get("file", ""),
                    "startedAt": latest.get("startedAt", ""),
                    "finishedAt": latest.get("finishedAt", ""),
                    "durationText": latest.get("durationText", ""),
                    "passed": latest.get("passed"),
                    "failed": latest.get("failed"),
                    "total": latest.get("total"),
                    "isCurrentSmoke": latest_is_current,
                },
            }
            payload["observations"].append(observation)
            if latest.get("ok") and latest_is_current:
                if progress or current_log_total > 0:
                    outcome = "completed"
                else:
                    outcome = "completed_without_work"
                break
            if (time.perf_counter() - last_progress) >= stall_seconds:
                outcome = "stalled_after_progress" if progress or count_now > start_count else "stalled_without_progress"
                break
        else:
            if not poll_started:
                pass
            else:
                outcome = "timeout"
    finally:
        if sqx_started:
            payload["stopApi"] = sqx_local_api(
                project_root,
                root142,
                action="stop-project",
                project_name=target.name,
                task_title=None,
                active=True,
                apply=True,
                allow_source_project=True,
                base_url=base_url,
                timeout=10,
            )
        else:
            payload["stopApi"] = {"ok": True, "skipped": True, "reason": outcome}
        time.sleep(5)
        payload["close"] = close_sqx_processes(root142)
        payload["restore"] = apply_profile(project_root, root142, root143, restore_profile, apply=True)

    payload["outcome"] = outcome
    payload["elapsedSeconds"] = round(time.perf_counter() - started_perf, 2)
    payload["afterDatabank"] = _databank_basic_snapshot(output_databank)
    payload["afterLogSummary"] = project_log_summary(
        project_root,
        root142,
        sqx_project=None,
        project_name=target.name,
        limit=12,
    )
    payload["afterStatus"] = build_sqx142_performance_status(project_root, root142, root143, include_paths=False)
    payload["hsErrCount"] = len(list(root142.glob("hs_err_pid*.log")))
    after_count = int((payload["afterDatabank"] or {}).get("strategyFiles") or 0)
    after_newest = str((payload["afterDatabank"] or {}).get("newestModified") or "")
    payload["automationOk"] = (
        (outcome == "no_input_candidates" or bool((payload.get("startApi") or {}).get("ok")))
        and (outcome == "no_input_candidates" or bool((payload.get("stopApi") or {}).get("ok")))
        and bool((payload.get("restore") or {}).get("ok"))
        and int(((payload.get("close") or {}).get("result") or {}).get("leftAfterForce") or 0) == 0
        and not ((payload.get("afterStatus") or {}).get("warnings") or [])
        and payload["hsErrCount"] == 0
    )
    payload["methodologicalProgress"] = bool(
        ever_progress
        or after_count > start_count
        or (after_newest and after_newest != start_newest)
        or current_log_total > 0
    )
    if outcome == "completed_without_work":
        payload["warning"] = "Sequential accepted start/stop but produced a current 0-total log and no databank update."
    payload["ok"] = bool(payload["automationOk"] and payload["methodologicalProgress"] and outcome == "completed")
    written = write_evidence(project_root, f"sequential_smoke_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def api_auth_smoke(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    apply: bool,
    base_url: str,
    api_ready_timeout: int,
) -> dict[str, Any]:
    launcher = root142 / "StrategyQuantX_nocheck.exe"
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-api-auth-smoke-v1",
        "dryRun": not apply,
        "baseUrl": base_url,
        "apiReadyTimeout": api_ready_timeout,
        "qualityReductionAllowed": False,
        "launcherExists": launcher.is_file(),
        "beforeStatus": build_sqx142_performance_status(project_root, root142, root143, include_paths=False),
    }
    if not apply:
        payload["message"] = "Dry-run only. Re-run with --apply to launch SQX, check local API auth and close."
        return payload
    if sqx_processes_running(root142, root143):
        payload["error"] = "sqx_processes_running"
        write_evidence(project_root, f"api_auth_smoke_failed_{stamp()}.json", payload)
        return payload
    if not launcher.is_file():
        payload["error"] = "launcher_missing"
        write_evidence(project_root, f"api_auth_smoke_failed_{stamp()}.json", payload)
        return payload

    started = time.perf_counter()
    try:
        proc = subprocess.Popen([str(launcher)], cwd=str(root142))  # noqa: S603
        payload["launchedPid"] = proc.pid
        payload["apiReady"] = _wait_for_sqx_local_api(base_url, timeout_seconds=api_ready_timeout, poll_seconds=5)
        if (payload.get("apiReady") or {}).get("ok"):
            payload["checkAccess"] = sqx_local_api(
                project_root,
                root142,
                action="check-access",
                project_name="_local_api_auth_probe",
                task_title=None,
                active=True,
                apply=True,
                allow_source_project=True,
                base_url=base_url,
                timeout=15,
            )
        else:
            payload["error"] = "api_not_ready"
    finally:
        time.sleep(3)
        payload["close"] = close_sqx_processes(root142)
    payload["elapsedSeconds"] = round(time.perf_counter() - started, 2)
    payload["afterStatus"] = build_sqx142_performance_status(project_root, root142, root143, include_paths=False)
    payload["ok"] = (
        bool((payload.get("checkAccess") or {}).get("ok"))
        and not ((payload.get("afterStatus") or {}).get("warnings") or [])
    )
    written = write_evidence(project_root, f"api_auth_smoke_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def project_mc_snapshot(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    sqx_project: Path | None,
    project_name: str | None,
    sample_limit: int,
    include_paths: bool,
) -> dict[str, Any]:
    target = resolve_sqx_project(root142, sqx_project, project_name)
    databanks_root = target / "databanks"
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-mc-project-snapshot-v1",
        "qualityReductionAllowed": False,
        "project": {
            "name": target.name,
            "exists": target.is_dir(),
            "localPathReturned": include_paths,
        },
        "sampleLimit": sample_limit,
        "status": build_sqx142_performance_status(project_root, root142, root143, include_paths=False),
    }
    if include_paths:
        payload["project"]["path"] = str(target)
    if not target.is_dir():
        payload["error"] = "project_missing"
        return payload
    payload["config"] = _project_config_snapshot(target / "project.cfx")
    payload["databanks"] = {
        name: _databank_mc_snapshot(databanks_root / name, sample_limit=sample_limit)
        for name in MC_DATABANK_VIEW_TARGETS
    }
    issues: list[str] = []
    for name, snapshot in payload["databanks"].items():
        if not snapshot.get("exists"):
            issues.append(f"{name}:missing")
        if not snapshot.get("strategyFiles"):
            issues.append(f"{name}:empty")
        if not snapshot.get("methodCounts"):
            issues.append(f"{name}:missing_mc_results")
        if not snapshot.get("resultCounts", {}).get("failed"):
            issues.append(f"{name}:no_failed_results_in_sample")
    if (payload.get("config") or {}).get("viewMismatches"):
        issues.append("project_view_mismatch")
    payload["issues"] = issues
    payload["ok"] = not any(issue.endswith(":missing") or issue.endswith(":empty") or issue.endswith(":missing_mc_results") for issue in issues)
    written = write_evidence(project_root, f"mc_project_snapshot_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": include_paths}
    return payload


def prepare_project_mc_views(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    sqx_project: Path | None,
    project_name: str | None,
    apply: bool,
) -> dict[str, Any]:
    target = resolve_sqx_project(root142, sqx_project, project_name)
    project_cfx = target / "project.cfx"
    before_config = _project_config_snapshot(project_cfx)
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-mc-project-view-prepare-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "project": {"name": target.name, "exists": target.is_dir()},
        "before": before_config,
        "actions": [],
    }
    if not target.is_dir() or not project_cfx.is_file() or not zipfile.is_zipfile(project_cfx):
        payload["error"] = "project_cfx_missing_or_not_zip"
        return payload
    if apply and sqx_processes_running(root142, root143):
        payload["error"] = "sqx_processes_running"
        write_evidence(project_root, f"mc_project_views_failed_{stamp()}.json", payload)
        return payload
    mismatches = before_config.get("viewMismatches") or []
    if not mismatches:
        payload["ok"] = True
        payload["message"] = "Project already uses the dedicated Monkey/Synthetic MC views."
        return payload
    for item in mismatches:
        payload["actions"].append({
            "databank": item.get("databank"),
            "from": item.get("currentView"),
            "to": item.get("expectedView"),
            "willWrite": apply,
        })
    if not apply:
        payload["message"] = "Dry-run only. Re-run with --apply to update project.cfx config.xml view assignments."
        return payload

    backup_dir = root142.parent / "SQX_142_Crack_local_backups" / f"sqx142_mc_project_views_before_{stamp()}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / project_cfx.name
    shutil.copy2(project_cfx, backup)
    tmp = project_cfx.with_suffix(project_cfx.suffix + f".{os.getpid()}.tmp")
    with zipfile.ZipFile(project_cfx, "r") as source:
        config_text = _safe_zip_text(source, "config.xml")
        for databank, expected_view in MC_DATABANK_VIEW_TARGETS.items():
            pattern = rf'(<Databank\b(?=[^>]*\bname="{re.escape(databank)}")[^>]*\bview=")[^"]*(")'
            config_text = re.sub(pattern, rf"\1{expected_view}\2", config_text, count=1)
        with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as target_zip:
            for item in source.infolist():
                data = config_text.encode("utf-8") if item.filename == "config.xml" else source.read(item.filename)
                target_zip.writestr(item, data)
    tmp.replace(project_cfx)
    after_config = _project_config_snapshot(project_cfx)
    payload["backup"] = {"copied": True, "path": str(backup)}
    payload["after"] = after_config
    payload["ok"] = not bool(after_config.get("viewMismatches"))
    written = write_evidence(project_root, f"mc_project_views_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def _view_file_summary(path: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": path.stem,
        "exists": path.is_file(),
        "columns": 0,
        "heavyColumns": [],
        "columnClasses": [],
        "bytes": path.stat().st_size if path.is_file() else 0,
    }
    if not path.is_file():
        return payload
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        payload["error"] = type(exc).__name__
        return payload
    classes = []
    heavy = []
    for column in root.findall(".//Column"):
        klass = column.attrib.get("class", "")
        if klass:
            classes.append(klass)
        if klass in PHASE5_HEAVY_COLUMN_CLASSES:
            heavy.append({"class": klass, "name": column.attrib.get("name", "")})
    payload["columns"] = len(classes)
    payload["columnClasses"] = classes
    payload["heavyColumns"] = heavy
    return payload


def phase5_databank_view_guard(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    sqx_project: Path | None,
    project_name: str | None,
    apply: bool,
    archive_views: bool,
    include_paths: bool,
) -> dict[str, Any]:
    target = resolve_sqx_project(root142, sqx_project, project_name)
    project_cfx = target / "project.cfx"
    view_root = root142 / "user" / "settings" / "views" / "databanks"
    views = {
        path.stem: _view_file_summary(path)
        for path in sorted(view_root.glob("*.vw"), key=lambda item: item.name.lower())
    } if view_root.is_dir() else {}
    before_config = _project_config_snapshot(project_cfx)
    databanks = before_config.get("databanks") if isinstance(before_config.get("databanks"), list) else []
    referenced_views = {str(item.get("view") or "") for item in databanks if item.get("view")}
    view_actions = []
    for item in databanks:
        name = str(item.get("name") or "")
        expected = PHASE5_DATABANK_VIEW_TARGETS.get(name)
        if not expected:
            continue
        current = str(item.get("view") or "")
        if current != expected:
            view_actions.append({"databank": name, "from": current, "to": expected, "willWrite": apply})
    archive_candidates = []
    for name, reason in PHASE5_ARCHIVE_VIEW_CANDIDATES.items():
        summary = views.get(name)
        if not summary or not summary.get("exists"):
            continue
        archive_candidates.append({
            "view": name,
            "file": f"{name}.vw",
            "reason": reason,
            "currentlyReferenced": name in referenced_views,
            "willArchive": bool(apply and archive_views),
            "columns": summary.get("columns", 0),
            "heavyColumns": summary.get("heavyColumns", []),
        })
    execution_view_issues = []
    for name in ("MINING FAST REVIEW", "RETEST QUICK REVIEW", "RETEST ROBUST REVIEW"):
        summary = views.get(name, {"exists": False})
        if not summary.get("exists"):
            execution_view_issues.append({"view": name, "issue": "missing"})
        elif summary.get("heavyColumns"):
            execution_view_issues.append({"view": name, "issue": "heavy_columns_in_execution_view", "columns": summary.get("heavyColumns")})
    required_missing = [
        name
        for name in sorted(set(PHASE5_DATABANK_VIEW_TARGETS.values()))
        if not (view_root / f"{name}.vw").is_file()
    ]
    blocking = []
    if required_missing:
        blocking.append("required_views_missing")
    if execution_view_issues:
        blocking.append("execution_view_issues")
    if view_actions:
        blocking.append("project_databank_view_mismatch")
    payload: dict[str, Any] = {
        "ok": not blocking,
        "version": "sqx142-phase5-databank-view-guard-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "project": {"name": target.name, "exists": target.is_dir()},
        "requiredMissingViews": required_missing,
        "executionViewIssues": execution_view_issues,
        "projectViewActions": view_actions,
        "archiveCandidates": archive_candidates,
        "blocking": blocking,
        "rules": [
            "Execution views must stay light: no mini charts or indicator/full-audit columns.",
            "Monkey and Synthetic must keep separate dedicated MC views.",
            "Legacy/all-metrics views are archived out of active SQX views, not permanently deleted.",
            "Project databanks are reassigned before archiving referenced legacy views.",
        ],
        "privacy": {"local_paths_returned": include_paths},
    }
    if include_paths:
        payload["paths"] = {"project": str(target), "viewRoot": str(view_root)}
    if not apply:
        payload["message"] = "Dry-run only. Re-run with --apply --archive-views to reassign project views and archive selected legacy views."
        written = write_evidence(project_root, f"phase5_databank_view_guard_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
        return payload
    if sqx_processes_running(root142, root143):
        payload["error"] = "sqx_processes_running"
        written = write_evidence(project_root, f"phase5_databank_view_guard_blocked_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
        return payload
    backup_dir = root142.parent / "SQX_142_Crack_local_backups" / f"sqx142_phase5_views_before_{stamp()}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    if project_cfx.is_file():
        shutil.copy2(project_cfx, backup_dir / "project.cfx")
    for candidate in archive_candidates:
        source = view_root / str(candidate["file"])
        if source.is_file():
            target_backup = backup_dir / "views" / source.name
            target_backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target_backup)
    if view_actions and project_cfx.is_file() and zipfile.is_zipfile(project_cfx):
        tmp = project_cfx.with_suffix(project_cfx.suffix + f".{os.getpid()}.tmp")
        with zipfile.ZipFile(project_cfx, "r") as source:
            config_text = _safe_zip_text(source, "config.xml")
            for databank, expected_view in PHASE5_DATABANK_VIEW_TARGETS.items():
                pattern = rf'(<Databank\b(?=[^>]*\bname="{re.escape(databank)}")[^>]*\bview=")[^"]*(")'
                config_text = re.sub(pattern, rf"\1{expected_view}\2", config_text, count=1)
            with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as target_zip:
                for item in source.infolist():
                    data = config_text.encode("utf-8") if item.filename == "config.xml" else source.read(item.filename)
                    target_zip.writestr(item, data)
        tmp.replace(project_cfx)
    archived = []
    if archive_views:
        archive_root = backup_dir / "archived_active_views"
        archive_root.mkdir(parents=True, exist_ok=True)
        for candidate in archive_candidates:
            source = view_root / str(candidate["file"])
            if not source.is_file():
                continue
            destination = archive_root / source.name
            shutil.move(str(source), str(destination))
            archived.append({"view": candidate["view"], "target": str(destination) if include_paths else destination.name})
    payload["backupRoot"] = str(backup_dir) if include_paths else backup_dir.name
    payload["archived"] = archived
    after = phase5_databank_view_guard(
        project_root,
        root142,
        root143,
        sqx_project=sqx_project,
        project_name=project_name,
        apply=False,
        archive_views=False,
        include_paths=include_paths,
    )
    payload["afterBlocking"] = after.get("blocking", [])
    payload["afterProjectViewActions"] = after.get("projectViewActions", [])
    payload["ok"] = not payload["afterBlocking"]
    written = write_evidence(project_root, f"phase5_databank_view_guard_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(include_paths)}
    return payload


def _evidence_file(project_root: Path, value: str | None) -> Path | None:
    if not value:
        return None
    candidate = Path(value)
    if candidate.is_file():
        return candidate
    candidate = evidence_root(project_root) / value
    return candidate if candidate.is_file() else None


def _latest_mc_snapshots(project_root: Path, limit: int = 2) -> list[Path]:
    root = evidence_root(project_root)
    if not root.is_dir():
        return []
    return sorted(root.glob("mc_project_snapshot_*.json"), key=lambda path: path.stat().st_mtime, reverse=True)[:limit]


def _read_json_file(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _db_compact(snapshot: dict[str, Any], name: str) -> dict[str, Any]:
    databank = ((snapshot.get("databanks") or {}).get(name) or {})
    return {
        "strategyFiles": databank.get("strategyFiles", 0),
        "sampledFiles": databank.get("sampledFiles", 0),
        "bytes": databank.get("bytes", 0),
        "human": databank.get("human", ""),
        "oldestModified": databank.get("oldestModified", ""),
        "newestModified": databank.get("newestModified", ""),
        "resultCounts": databank.get("resultCounts", {}),
        "simulationCounts": databank.get("simulationCounts", {}),
        "methodCounts": databank.get("methodCounts", {}),
    }


def _numeric_delta(before: Any, after: Any) -> int | float | None:
    if isinstance(before, (int, float)) and isinstance(after, (int, float)):
        return after - before
    return None


def _counter_delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    keys = sorted(set(before) | set(after))
    return {
        key: {
            "before": before.get(key, 0),
            "after": after.get(key, 0),
            "delta": (after.get(key, 0) or 0) - (before.get(key, 0) or 0),
        }
        for key in keys
    }


def project_mc_diff(
    project_root: Path,
    *,
    before_snapshot: str | None,
    after_snapshot: str | None,
) -> dict[str, Any]:
    latest = _latest_mc_snapshots(project_root, limit=2)
    before_path = _evidence_file(project_root, before_snapshot)
    after_path = _evidence_file(project_root, after_snapshot)
    if before_path is None and len(latest) >= 2:
        before_path = latest[1]
    if after_path is None and latest:
        after_path = latest[0]
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-mc-project-diff-v1",
        "qualityReductionAllowed": False,
        "before": before_path.name if before_path else "",
        "after": after_path.name if after_path else "",
        "databanks": {},
        "warnings": [],
    }
    if before_path is None or after_path is None:
        payload["error"] = "missing_snapshots"
        return payload
    before = _read_json_file(before_path)
    after = _read_json_file(after_path)
    for name in MC_DATABANK_VIEW_TARGETS:
        left = _db_compact(before, name)
        right = _db_compact(after, name)
        row = {
            "before": left,
            "after": right,
            "deltas": {
                "strategyFiles": _numeric_delta(left.get("strategyFiles"), right.get("strategyFiles")),
                "sampledFiles": _numeric_delta(left.get("sampledFiles"), right.get("sampledFiles")),
                "bytes": _numeric_delta(left.get("bytes"), right.get("bytes")),
                "resultCounts": _counter_delta(left.get("resultCounts") or {}, right.get("resultCounts") or {}),
                "simulationCounts": _counter_delta(left.get("simulationCounts") or {}, right.get("simulationCounts") or {}),
            },
            "methodChanged": left.get("methodCounts") != right.get("methodCounts"),
            "newestModifiedChanged": left.get("newestModified") != right.get("newestModified"),
        }
        payload["databanks"][name] = row
        if right.get("methodCounts") == {}:
            payload["warnings"].append(f"{name}:missing_methods_after")
        if row["methodChanged"]:
            payload["warnings"].append(f"{name}:method_changed")
    payload["ok"] = not any(item.endswith("missing_methods_after") for item in payload["warnings"])
    written = write_evidence(project_root, f"mc_project_diff_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def begin_project_mc_smoke(
    project_root: Path,
    root142: Path,
    root143: Path,
    *,
    sqx_project: Path | None,
    project_name: str | None,
    sample_limit: int,
    profile: str,
    apply: bool,
    launch: bool,
) -> dict[str, Any]:
    launcher = root142 / "StrategyQuantX_nocheck.exe"
    payload: dict[str, Any] = {
        "ok": False,
        "version": "sqx142-mc-smoke-session-v1",
        "dryRun": not apply,
        "qualityReductionAllowed": False,
        "profile": profile,
        "launch": launch,
        "steps": [
            "snapshot_before",
            "ensure_project_mc_views",
            "apply_retest_profile",
            "operator_runs_monkey_and_synthetic",
            "snapshot_after",
            "diff",
        ],
    }
    if profile not in PROFILE_CONFIGS:
        payload["error"] = "unknown_profile"
        payload["availableProfiles"] = sorted(PROFILE_CONFIGS)
        return payload
    if apply and sqx_processes_running(root142, root143):
        payload["error"] = "sqx_processes_running"
        write_evidence(project_root, f"mc_smoke_session_failed_{stamp()}.json", payload)
        return payload
    before = project_mc_snapshot(
        project_root,
        root142,
        root143,
        sqx_project=sqx_project,
        project_name=project_name,
        sample_limit=sample_limit,
        include_paths=False,
    )
    payload["beforeSnapshot"] = (before.get("evidence") or {}).get("filename", "")
    payload["viewPreparation"] = prepare_project_mc_views(
        project_root,
        root142,
        root143,
        sqx_project=sqx_project,
        project_name=project_name,
        apply=apply,
    )
    payload["profileApply"] = apply_profile(project_root, root142, root143, profile, apply=apply)
    if launch:
        payload["launcherExists"] = launcher.is_file()
        if apply and launcher.is_file():
            proc = subprocess.Popen([str(launcher)], cwd=str(root142))  # noqa: S603
            payload["launchedPid"] = proc.pid
        elif apply:
            payload["error"] = "launcher_missing"
    payload["nextCommandAfterRetests"] = (
        "powershell -NoProfile -ExecutionPolicy Bypass -File tools\\sqx142_performance_gate.ps1 "
        f"project-mc-snapshot --sample-limit {sample_limit}"
    )
    payload["diffCommandAfterSecondSnapshot"] = (
        "powershell -NoProfile -ExecutionPolicy Bypass -File tools\\sqx142_performance_gate.ps1 "
        f"project-mc-diff --before {payload['beforeSnapshot']}"
    )
    payload["ok"] = bool(before.get("ok")) and bool(payload["profileApply"].get("ok")) and not bool(payload.get("error"))
    written = write_evidence(project_root, f"mc_smoke_session_{stamp()}.json", payload)
    payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": False}
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX 142 performance gate. Dry-run by default.")
    parser.add_argument("--sqx142-root", type=Path, default=SQX142_DEFAULT_ROOT)
    parser.add_argument("--sqx143-root", type=Path, default=SQX143_DEFAULT_ROOT)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status")
    status.add_argument("--include-paths", action="store_true")

    snapshot = sub.add_parser("snapshot")
    snapshot.add_argument("--include-paths", action="store_true")

    profile = sub.add_parser("apply-profile")
    profile.add_argument("profile", choices=sorted(PROFILE_CONFIGS))
    profile.add_argument("--apply", action="store_true")

    views = sub.add_parser("create-views")
    views.add_argument("--apply", action="store_true")
    views.add_argument("--replace", action="store_true")

    sub.add_parser("cleanup-plan")

    old_logs = sub.add_parser("archive-old-logs")
    old_logs.add_argument("--keep-days", type=int, default=2)
    old_logs.add_argument("--apply", action="store_true")

    clone_hygiene = sub.add_parser("performance-clone-hygiene")
    clone_hygiene.add_argument("--keep-newest", type=int, default=2)
    clone_hygiene.add_argument("--include-paths", action="store_true")
    clone_hygiene.add_argument("--apply", action="store_true")

    clone_restore = sub.add_parser("restore-performance-clone")
    clone_restore.add_argument("--clone-name", required=True)
    clone_restore.add_argument("--archive-stamp", default="")
    clone_restore.add_argument("--archive-existing-active", action="store_true")
    clone_restore.add_argument("--include-paths", action="store_true")
    clone_restore.add_argument("--apply", action="store_true")

    closeout_report = sub.add_parser("performance-closeout-report")
    closeout_report.add_argument("--include-paths", action="store_true")

    next_action = sub.add_parser("performance-next-action")
    next_action.add_argument("--include-paths", action="store_true")

    parallelism = sub.add_parser("performance-parallelism-advisor")
    parallelism.add_argument("--include-paths", action="store_true")

    live_guard = sub.add_parser("live-guard")
    live_guard.add_argument("--keep-days", type=int, default=2)
    live_guard.add_argument("--apply", action="store_true")

    smoke = sub.add_parser("smoke-start")
    smoke.add_argument("--apply", action="store_true")
    smoke.add_argument("--wait-seconds", type=int, default=25)

    compare_profiles_cmd = sub.add_parser("compare-profiles")
    compare_profiles_cmd.add_argument("profiles", nargs="+", choices=sorted(PROFILE_CONFIGS))
    compare_profiles_cmd.add_argument("--apply", action="store_true")
    compare_profiles_cmd.add_argument("--wait-seconds", type=int, default=20)
    compare_profiles_cmd.add_argument("--restore-profile", choices=sorted(PROFILE_CONFIGS))

    mc_snapshot = sub.add_parser("project-mc-snapshot")
    mc_snapshot.add_argument("--sqx-project", type=Path)
    mc_snapshot.add_argument("--project-name", default=DEFAULT_REAL_PROJECT_NAME)
    mc_snapshot.add_argument("--sample-limit", type=int, default=500)
    mc_snapshot.add_argument("--include-paths", action="store_true")

    mc_views = sub.add_parser("prepare-project-mc-views")
    mc_views.add_argument("--sqx-project", type=Path)
    mc_views.add_argument("--project-name", default=DEFAULT_REAL_PROJECT_NAME)
    mc_views.add_argument("--apply", action="store_true")

    phase5_views = sub.add_parser("phase5-databank-view-guard")
    phase5_views.add_argument("--sqx-project", type=Path)
    phase5_views.add_argument("--project-name", default=DEFAULT_REAL_PROJECT_NAME)
    phase5_views.add_argument("--archive-views", action="store_true")
    phase5_views.add_argument("--include-paths", action="store_true")
    phase5_views.add_argument("--apply", action="store_true")

    mc_diff = sub.add_parser("project-mc-diff")
    mc_diff.add_argument("--before")
    mc_diff.add_argument("--after")

    mc_smoke = sub.add_parser("begin-project-mc-smoke")
    mc_smoke.add_argument("--sqx-project", type=Path)
    mc_smoke.add_argument("--project-name", default=DEFAULT_REAL_PROJECT_NAME)
    mc_smoke.add_argument("--sample-limit", type=int, default=500)
    mc_smoke.add_argument("--profile", choices=sorted(PROFILE_CONFIGS), default="retest_robust")
    mc_smoke.add_argument("--apply", action="store_true")
    mc_smoke.add_argument("--launch", action="store_true")

    log_summary = sub.add_parser("project-log-summary")
    log_summary.add_argument("--sqx-project", type=Path)
    log_summary.add_argument("--project-name", default=DEFAULT_REAL_PROJECT_NAME)
    log_summary.add_argument("--limit", type=int, default=40)

    queue_plan = sub.add_parser("project-retest-queue-plan")
    queue_plan.add_argument("--sqx-project", type=Path)
    queue_plan.add_argument("--project-name", default=DEFAULT_REAL_PROJECT_NAME)
    queue_plan.add_argument("--log-limit", type=int, default=80)

    mining_advisor = sub.add_parser("project-mining-pipeline-advisor")
    mining_advisor.add_argument("--sqx-project", type=Path)
    mining_advisor.add_argument("--project-name", default=DEFAULT_REAL_PROJECT_NAME)
    mining_advisor.add_argument("--log-limit", type=int, default=80)
    mining_advisor.add_argument("--include-paths", action="store_true")

    queue_next = sub.add_parser("project-retest-next-step")
    queue_next.add_argument("--sqx-project", type=Path)
    queue_next.add_argument("--project-name", default=DEFAULT_REAL_PROJECT_NAME)
    queue_next.add_argument("--log-limit", type=int, default=80)

    mc2_spread = sub.add_parser("mc2-spread-diagnostic")
    mc2_spread.add_argument("--sqx-project", type=Path)
    mc2_spread.add_argument("--project-name", default=DEFAULT_REAL_PROJECT_NAME)
    mc2_spread.add_argument("--log-limit", type=int, default=80)

    mc2_variant = sub.add_parser("create-mc2-spread-variant")
    mc2_variant.add_argument("--sqx-project", type=Path)
    mc2_variant.add_argument("--project-name", default=DEFAULT_REAL_PROJECT_NAME)
    mc2_variant.add_argument("--spread-min", type=float, required=True)
    mc2_variant.add_argument("--spread-max", type=float, required=True)
    mc2_variant.add_argument("--apply", action="store_true")
    mc2_variant.add_argument("--allow-source-project", action="store_true")

    mc2_promote = sub.add_parser("promote-mc2-spread-to-base")
    mc2_promote.add_argument("--sqx-project", type=Path)
    mc2_promote.add_argument("--project-name", default=DEFAULT_REAL_PROJECT_NAME)
    mc2_promote.add_argument("--spread-min", type=float)
    mc2_promote.add_argument("--spread-max", type=float)
    mc2_promote.add_argument("--min-multiplier", type=float, default=2.0)
    mc2_promote.add_argument("--max-multiplier", type=float, default=5.0)
    mc2_promote.add_argument("--source-evidence")
    mc2_promote.add_argument("--apply", action="store_true")
    mc2_promote.add_argument("--allow-master-project", action="store_true")
    mc2_promote.add_argument("--accept-methodology-change", action="store_true")
    mc2_promote.add_argument("--log-limit", type=int, default=80)

    mc2_rollback = sub.add_parser("rollback-mc2-spread-promotion")
    mc2_rollback.add_argument("--promotion-evidence", required=True)
    mc2_rollback.add_argument("--apply", action="store_true")
    mc2_rollback.add_argument("--log-limit", type=int, default=80)

    sequential_diag_variant = sub.add_parser("create-sequential-diagnostic-variant")
    sequential_diag_variant.add_argument("--sqx-project", type=Path)
    sequential_diag_variant.add_argument("--project-name", default="_PERFQ_MC2SPREAD__PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338_20260522_215125")
    sequential_diag_variant.add_argument("--max-passed", type=int, default=8)
    sequential_diag_variant.add_argument("--skip-passed", type=int, default=0)
    sequential_diag_variant.add_argument("--batch-label", default="")
    sequential_diag_variant.add_argument("--apply", action="store_true")
    sequential_diag_variant.add_argument("--allow-source-project", action="store_true")

    sequential_batch_plan = sub.add_parser("create-sequential-batch-plan")
    sequential_batch_plan.add_argument("--sqx-project", type=Path)
    sequential_batch_plan.add_argument("--project-name", default="_PERFQ_MC2SPREAD__PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338_20260522_215125")
    sequential_batch_plan.add_argument("--batches", default="24,24,24,12")
    sequential_batch_plan.add_argument("--apply", action="store_true")
    sequential_batch_plan.add_argument("--allow-source-project", action="store_true")

    sequential_merge = sub.add_parser("sequential-batch-merge-review")
    sequential_merge.add_argument("--plan-evidence", required=True)
    sequential_merge.add_argument("--apply", action="store_true")

    sequential_review = sub.add_parser("sequential-final-review")
    sequential_review.add_argument("--merge-root", type=Path)
    sequential_review.add_argument("--latest", action="store_true")
    sequential_review.add_argument("--write-csv", action="store_true")
    sequential_review.add_argument("--sample-limit", type=int, default=12)
    sequential_review.add_argument("--include-paths", action="store_true")
    sequential_review.add_argument("--apply", action="store_true")

    clone_project = sub.add_parser("clone-performance-project")
    clone_project.add_argument("--sqx-project", type=Path)
    clone_project.add_argument("--project-name", default=DEFAULT_REAL_PROJECT_NAME)
    clone_project.add_argument("--apply", action="store_true")

    queue_step = sub.add_parser("prepare-queue-step")
    queue_step.add_argument("task_title")
    queue_step.add_argument("--sqx-project", type=Path)
    queue_step.add_argument("--project-name", default=DEFAULT_REAL_PROJECT_NAME)
    queue_step.add_argument("--apply", action="store_true")
    queue_step.add_argument("--launch", action="store_true")
    queue_step.add_argument("--allow-source-project", action="store_true")
    queue_step.add_argument("--log-limit", type=int, default=80)

    task_smoke = sub.add_parser("queue-task-smoke")
    task_smoke.add_argument("task_title")
    task_smoke.add_argument("--project-name", default="_PERFQ_MC2SPREAD__PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338_20260522_215125")
    task_smoke.add_argument("--base-url", default="http://localhost:8080")
    task_smoke.add_argument("--max-seconds", type=int, default=600)
    task_smoke.add_argument("--stall-seconds", type=int, default=180)
    task_smoke.add_argument("--poll-seconds", type=int, default=20)
    task_smoke.add_argument("--api-ready-timeout", type=int, default=120)
    task_smoke.add_argument("--start-settle-seconds", type=int, default=180)
    task_smoke.add_argument("--restore-profile", choices=sorted(PROFILE_CONFIGS), default="baseline_143_safe")
    task_smoke.add_argument("--apply", action="store_true")
    task_smoke.add_argument("--allow-source-project", action="store_true")
    task_smoke.add_argument("--no-launch", dest="launch", action="store_false")
    task_smoke.set_defaults(launch=True)

    local_api = sub.add_parser("sqx-local-api")
    local_api.add_argument("action", choices=("probe", "check-access", "start-project", "stop-project", "activate-task"))
    local_api.add_argument("--project-name", default=DEFAULT_REAL_PROJECT_NAME)
    local_api.add_argument("--task-title")
    local_api.add_argument("--active", choices=("true", "false"), default="true")
    local_api.add_argument("--base-url", default="http://localhost:8080")
    local_api.add_argument("--timeout", type=int, default=15)
    local_api.add_argument("--apply", action="store_true")
    local_api.add_argument("--allow-source-project", action="store_true")

    seq_smoke = sub.add_parser("sequential-smoke")
    seq_smoke.add_argument("--project-name", default="_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338")
    seq_smoke.add_argument("--base-url", default="http://localhost:8080")
    seq_smoke.add_argument("--max-seconds", type=int, default=600)
    seq_smoke.add_argument("--stall-seconds", type=int, default=180)
    seq_smoke.add_argument("--poll-seconds", type=int, default=20)
    seq_smoke.add_argument("--api-ready-timeout", type=int, default=90)
    seq_smoke.add_argument("--restore-profile", choices=sorted(PROFILE_CONFIGS), default="baseline_143_safe")
    seq_smoke.add_argument("--apply", action="store_true")
    seq_smoke.add_argument("--allow-source-project", action="store_true")
    seq_smoke.add_argument("--no-launch", dest="launch", action="store_false")
    seq_smoke.set_defaults(launch=True)

    auth_smoke = sub.add_parser("api-auth-smoke")
    auth_smoke.add_argument("--base-url", default="http://localhost:8080")
    auth_smoke.add_argument("--api-ready-timeout", type=int, default=90)
    auth_smoke.add_argument("--apply", action="store_true")

    args = parser.parse_args()
    project_root = args.project_root
    root142 = args.sqx142_root
    root143 = args.sqx143_root

    if args.command == "status":
        json_print(build_sqx142_performance_status(project_root, root142, root143, include_paths=args.include_paths))
        return 0
    if args.command == "snapshot":
        payload = build_sqx142_performance_status(project_root, root142, root143, include_paths=args.include_paths)
        payload["launcherEvents"] = latest_launcher_events(root142, limit=20)
        written = write_evidence(project_root, f"performance_snapshot_{stamp()}.json", payload)
        payload["evidence"] = {"written": True, "filename": written.name, "localPathReturned": bool(args.include_paths)}
        json_print(payload)
        return 0
    if args.command == "apply-profile":
        json_print(apply_profile(project_root, root142, root143, args.profile, apply=args.apply))
        return 0
    if args.command == "create-views":
        json_print(create_views(project_root, root142, root143, apply=args.apply, replace=args.replace))
        return 0
    if args.command == "cleanup-plan":
        json_print(cleanup_plan(project_root, root142, root143))
        return 0
    if args.command == "archive-old-logs":
        json_print(archive_old_logs(project_root, root142, keep_days=args.keep_days, apply=args.apply))
        return 0
    if args.command == "performance-clone-hygiene":
        json_print(performance_clone_hygiene(
            project_root,
            root142,
            root143,
            keep_newest=args.keep_newest,
            apply=args.apply,
            include_paths=args.include_paths,
        ))
        return 0
    if args.command == "restore-performance-clone":
        json_print(restore_performance_clone(
            project_root,
            root142,
            root143,
            clone_name=args.clone_name,
            archive_stamp=args.archive_stamp,
            archive_existing_active=args.archive_existing_active,
            apply=args.apply,
            include_paths=args.include_paths,
        ))
        return 0
    if args.command == "performance-closeout-report":
        json_print(performance_closeout_report(
            project_root,
            root142,
            root143,
            include_paths=args.include_paths,
        ))
        return 0
    if args.command == "performance-next-action":
        json_print(performance_next_action(
            project_root,
            root142,
            root143,
            include_paths=args.include_paths,
        ))
        return 0
    if args.command == "performance-parallelism-advisor":
        json_print(performance_parallelism_advisor(
            project_root,
            root142,
            root143,
            include_paths=args.include_paths,
        ))
        return 0
    if args.command == "live-guard":
        json_print(performance_live_guard(
            project_root,
            root142,
            root143,
            keep_days=args.keep_days,
            apply=args.apply,
        ))
        return 0
    if args.command == "smoke-start":
        json_print(smoke_start(project_root, root142, root143, apply=args.apply, wait_seconds=args.wait_seconds))
        return 0
    if args.command == "compare-profiles":
        json_print(compare_profiles(
            project_root,
            root142,
            root143,
            args.profiles,
            apply=args.apply,
            wait_seconds=args.wait_seconds,
            restore_profile=args.restore_profile,
        ))
        return 0
    if args.command == "project-mc-snapshot":
        json_print(project_mc_snapshot(
            project_root,
            root142,
            root143,
            sqx_project=args.sqx_project,
            project_name=args.project_name,
            sample_limit=args.sample_limit,
            include_paths=args.include_paths,
        ))
        return 0
    if args.command == "prepare-project-mc-views":
        json_print(prepare_project_mc_views(
            project_root,
            root142,
            root143,
            sqx_project=args.sqx_project,
            project_name=args.project_name,
            apply=args.apply,
        ))
        return 0
    if args.command == "phase5-databank-view-guard":
        json_print(phase5_databank_view_guard(
            project_root,
            root142,
            root143,
            sqx_project=args.sqx_project,
            project_name=args.project_name,
            apply=args.apply,
            archive_views=args.archive_views,
            include_paths=args.include_paths,
        ))
        return 0
    if args.command == "project-mc-diff":
        json_print(project_mc_diff(
            project_root,
            before_snapshot=args.before,
            after_snapshot=args.after,
        ))
        return 0
    if args.command == "begin-project-mc-smoke":
        json_print(begin_project_mc_smoke(
            project_root,
            root142,
            root143,
            sqx_project=args.sqx_project,
            project_name=args.project_name,
            sample_limit=args.sample_limit,
            profile=args.profile,
            apply=args.apply,
            launch=args.launch,
        ))
        return 0
    if args.command == "project-log-summary":
        json_print(project_log_summary(
            project_root,
            root142,
            sqx_project=args.sqx_project,
            project_name=args.project_name,
            limit=args.limit,
        ))
        return 0
    if args.command == "project-retest-queue-plan":
        json_print(project_retest_queue_plan(
            project_root,
            root142,
            sqx_project=args.sqx_project,
            project_name=args.project_name,
            log_limit=args.log_limit,
        ))
        return 0
    if args.command == "project-mining-pipeline-advisor":
        json_print(project_mining_pipeline_advisor(
            project_root,
            root142,
            sqx_project=args.sqx_project,
            project_name=args.project_name,
            log_limit=args.log_limit,
            include_paths=args.include_paths,
        ))
        return 0
    if args.command == "project-retest-next-step":
        json_print(project_retest_next_step(
            project_root,
            root142,
            sqx_project=args.sqx_project,
            project_name=args.project_name,
            log_limit=args.log_limit,
        ))
        return 0
    if args.command == "mc2-spread-diagnostic":
        json_print(mc2_spread_diagnostic(
            project_root,
            root142,
            sqx_project=args.sqx_project,
            project_name=args.project_name,
            log_limit=args.log_limit,
        ))
        return 0
    if args.command == "create-mc2-spread-variant":
        json_print(create_mc2_spread_variant(
            project_root,
            root142,
            root143,
            sqx_project=args.sqx_project,
            project_name=args.project_name,
            spread_min=args.spread_min,
            spread_max=args.spread_max,
            apply=args.apply,
            allow_source_project=args.allow_source_project,
        ))
        return 0
    if args.command == "promote-mc2-spread-to-base":
        json_print(promote_mc2_spread_to_base(
            project_root,
            root142,
            root143,
            sqx_project=args.sqx_project,
            project_name=args.project_name,
            spread_min=args.spread_min,
            spread_max=args.spread_max,
            min_multiplier=args.min_multiplier,
            max_multiplier=args.max_multiplier,
            source_evidence=args.source_evidence,
            apply=args.apply,
            allow_master_project=args.allow_master_project,
            accept_methodology_change=args.accept_methodology_change,
            log_limit=args.log_limit,
        ))
        return 0
    if args.command == "rollback-mc2-spread-promotion":
        json_print(rollback_mc2_spread_promotion(
            project_root,
            root142,
            root143,
            promotion_evidence=args.promotion_evidence,
            apply=args.apply,
            log_limit=args.log_limit,
        ))
        return 0
    if args.command == "create-sequential-diagnostic-variant":
        json_print(create_sequential_diagnostic_variant(
            project_root,
            root142,
            root143,
            sqx_project=args.sqx_project,
            project_name=args.project_name,
            max_passed=args.max_passed,
            apply=args.apply,
            allow_source_project=args.allow_source_project,
            skip_passed=args.skip_passed,
            batch_label=args.batch_label,
        ))
        return 0
    if args.command == "create-sequential-batch-plan":
        json_print(create_sequential_batch_plan(
            project_root,
            root142,
            root143,
            sqx_project=args.sqx_project,
            project_name=args.project_name,
            batches=args.batches,
            apply=args.apply,
            allow_source_project=args.allow_source_project,
        ))
        return 0
    if args.command == "sequential-batch-merge-review":
        json_print(sequential_batch_merge_review(
            project_root,
            root142,
            plan_evidence=args.plan_evidence,
            apply=args.apply,
        ))
        return 0
    if args.command == "sequential-final-review":
        json_print(sequential_final_review(
            project_root,
            merge_root=args.merge_root,
            latest=args.latest or not args.merge_root,
            apply=args.apply,
            write_csv=args.write_csv,
            sample_limit=args.sample_limit,
            include_paths=args.include_paths,
        ))
        return 0
    if args.command == "clone-performance-project":
        json_print(clone_performance_project(
            project_root,
            root142,
            root143,
            sqx_project=args.sqx_project,
            project_name=args.project_name,
            apply=args.apply,
        ))
        return 0
    if args.command == "prepare-queue-step":
        json_print(prepare_queue_step(
            project_root,
            root142,
            root143,
            sqx_project=args.sqx_project,
            project_name=args.project_name,
            task_title=args.task_title,
            apply=args.apply,
            launch=args.launch,
            allow_source_project=args.allow_source_project,
            log_limit=args.log_limit,
        ))
        return 0
    if args.command == "queue-task-smoke":
        json_print(queue_task_smoke(
            project_root,
            root142,
            root143,
            project_name=args.project_name,
            task_title=args.task_title,
            apply=args.apply,
            launch=args.launch,
            allow_source_project=args.allow_source_project,
            base_url=args.base_url,
            max_seconds=args.max_seconds,
            stall_seconds=args.stall_seconds,
            poll_seconds=args.poll_seconds,
            api_ready_timeout=args.api_ready_timeout,
            start_settle_seconds=args.start_settle_seconds,
            restore_profile=args.restore_profile,
        ))
        return 0
    if args.command == "sqx-local-api":
        json_print(sqx_local_api(
            project_root,
            root142,
            action=args.action,
            project_name=args.project_name,
            task_title=args.task_title,
            active=args.active == "true",
            apply=args.apply,
            allow_source_project=args.allow_source_project,
            base_url=args.base_url,
            timeout=args.timeout,
        ))
        return 0
    if args.command == "sequential-smoke":
        json_print(sequential_smoke(
            project_root,
            root142,
            root143,
            project_name=args.project_name,
            apply=args.apply,
            launch=args.launch,
            allow_source_project=args.allow_source_project,
            base_url=args.base_url,
            max_seconds=args.max_seconds,
            stall_seconds=args.stall_seconds,
            poll_seconds=args.poll_seconds,
            api_ready_timeout=args.api_ready_timeout,
            restore_profile=args.restore_profile,
        ))
        return 0
    if args.command == "api-auth-smoke":
        json_print(api_auth_smoke(
            project_root,
            root142,
            root143,
            apply=args.apply,
            base_url=args.base_url,
            api_ready_timeout=args.api_ready_timeout,
        ))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
