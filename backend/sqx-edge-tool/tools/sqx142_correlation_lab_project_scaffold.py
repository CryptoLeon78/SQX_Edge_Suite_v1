from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


VERSION = "sqx142-own-features3b-correlation-lab-project-scaffold-v1"
DEFAULT_DONOR = "Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1"
DEFAULT_TARGET = "SQX_EDGE_CORR_LAB_Mining15_USDJPY_H4_20260527"
VIEW_NAME = "SQX EDGE CORRELATION REVIEW"
TAG_TASK_TITLE = "SQX EDGE CORR TAG"
CUSTOM_ANALYSIS_ID = "SQXEdgeCorrelationTagger"
SOURCE_DATABANK = "Monkey Test"
SECONDARY_DATABANK = "Syntetic"
OUTPUT_DATABANK = "SQX EDGE CORR TAGGED"
RETIRED_STRATEGY_DEPENDENCIES = ("ExitAfterDays", "ExitAfterTradingDays")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _local_root() -> Path:
    return _repo_root() / ".local" / "sqx142_own_features" / "lab_project_scaffold"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _resolve_inside(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    root_resolved = root.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"path escapes root: {resolved} root={root_resolved}") from exc
    return resolved


def _projects_root(sqx_root: Path) -> Path:
    return sqx_root / "user" / "projects"


def _quarantine_root(sqx_root: Path) -> Path:
    return sqx_root / "user" / "projects_quarantine" / "SQXEdge"


def _file_sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _dir_hash(path: Path) -> str | None:
    if not path.is_dir():
        return None
    digest = hashlib.sha256()
    for file_path in sorted(p for p in path.rglob("*") if p.is_file()):
        relative = file_path.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(file_path.stat().st_size).encode("ascii"))
        digest.update(b"\0")
        digest.update((_file_sha256(file_path) or "").encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _databank_counts(project_dir: Path) -> dict[str, int]:
    databanks_root = project_dir / "databanks"
    if not databanks_root.is_dir():
        return {}
    counts: dict[str, int] = {}
    for databank_dir in sorted(p for p in databanks_root.iterdir() if p.is_dir()):
        counts[databank_dir.name] = len(list(databank_dir.glob("*.sqx")))
    return counts


def _iter_strategy_texts(path: Path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path, "r") as archive:
            for entry in archive.infolist():
                if entry.is_dir():
                    continue
                if not entry.filename.lower().endswith((".xml", ".json", ".txt", ".properties")):
                    continue
                yield archive.read(entry).decode("utf-8", errors="ignore")
        return
    yield path.read_text(encoding="utf-8", errors="ignore")


def _scan_databank_retired_dependencies(project_dir: Path, databank_name: str) -> dict[str, object]:
    databank_dir = project_dir / "databanks" / databank_name
    result: dict[str, object] = {
        "databank": databank_name,
        "exists": databank_dir.is_dir(),
        "strategyCount": 0,
        "affectedStrategyCount": 0,
        "tokens": {token: 0 for token in RETIRED_STRATEGY_DEPENDENCIES},
    }
    if not databank_dir.is_dir():
        return result

    for strategy_path in sorted(databank_dir.glob("*.sqx")):
        result["strategyCount"] = int(result["strategyCount"]) + 1
        found: set[str] = set()
        for text in _iter_strategy_texts(strategy_path):
            for token in RETIRED_STRATEGY_DEPENDENCIES:
                if token in text:
                    found.add(token)
        if found:
            result["affectedStrategyCount"] = int(result["affectedStrategyCount"]) + 1
            tokens = result["tokens"]
            assert isinstance(tokens, dict)
            for token in found:
                tokens[token] = int(tokens.get(token, 0)) + 1
    return result


def _retired_dependency_preflight(project_dir: Path) -> dict[str, object]:
    databanks = [
        _scan_databank_retired_dependencies(project_dir, SOURCE_DATABANK),
        _scan_databank_retired_dependencies(project_dir, SECONDARY_DATABANK),
    ]
    affected = sum(int(item.get("affectedStrategyCount") or 0) for item in databanks)
    return {
        "ok": affected == 0,
        "status": "ok" if affected == 0 else "blocked_legacy_retired_snippets",
        "blocked": affected > 0,
        "blockedReason": "" if affected == 0 else "retired_strategy_dependency_detected",
        "tokens": list(RETIRED_STRATEGY_DEPENDENCIES),
        "affectedStrategyCount": affected,
        "databanks": databanks,
        "recommendation": "Use a fresh mining/custom project or a databank that does not reference retired exit snippets.",
    }


def _read_zip_text(entries: dict[str, bytes], name: str) -> str:
    if name not in entries:
        raise ValueError(f"project.cfx missing {name}")
    return entries[name].decode("utf-8")


def _write_project_cfx(entries: dict[str, bytes], cfx_path: Path) -> None:
    tmp_path = cfx_path.with_suffix(".cfx.tmp")
    with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    tmp_path.replace(cfx_path)


def _load_project_cfx(cfx_path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(cfx_path, "r") as archive:
        return {entry.filename: archive.read(entry.filename) for entry in archive.infolist()}


def _patch_config_xml(xml_text: str, target_project: str) -> tuple[str, dict[str, object]]:
    root = ET.fromstring(xml_text)
    previous_name = root.attrib.get("name", "")
    root.set("name", target_project)

    task_updates: list[dict[str, str]] = []
    tasks = root.find("Tasks")
    if tasks is not None:
        for task in tasks.findall("Task"):
            task.set("active", "false")
            if task.attrib.get("taskXMLFile") == "Retest-Task2.xml":
                task.set("title", TAG_TASK_TITLE)
                task.set("name", "SQX Edge Correlation Tag")
                task_updates.append(
                    {
                        "taskXMLFile": "Retest-Task2.xml",
                        "title": TAG_TASK_TITLE,
                        "active": "false",
                    }
                )

    databank_updates: list[dict[str, str]] = []
    databanks = root.find("Databanks")
    existing_names: set[str] = set()
    if databanks is not None:
        max_position = 0
        for databank in databanks.findall("Databank"):
            name = databank.attrib.get("name", "")
            existing_names.add(name)
            try:
                max_position = max(max_position, int(databank.attrib.get("position", "0")))
            except ValueError:
                pass
            if name in {SOURCE_DATABANK, SECONDARY_DATABANK, "Foward"}:
                databank.set("view", VIEW_NAME)
                databank_updates.append({"name": name, "view": VIEW_NAME})
        if OUTPUT_DATABANK not in existing_names:
            ET.SubElement(
                databanks,
                "Databank",
                {
                    "name": OUTPUT_DATABANK,
                    "view": VIEW_NAME,
                    "syncType": "Auto-sync never",
                    "position": str(max_position + 100),
                },
            )
            databank_updates.append({"name": OUTPUT_DATABANK, "view": VIEW_NAME})

    patched = ET.tostring(root, encoding="unicode")
    return patched, {
        "previousProjectName": previous_name,
        "projectName": target_project,
        "taskUpdates": task_updates,
        "databankUpdates": databank_updates,
    }


def _replace_once(text: str, pattern: str, replacement: str, label: str) -> tuple[str, bool]:
    patched, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise ValueError(f"unable to patch {label}")
    return patched, True


def _patch_retest_task_xml(xml_text: str) -> tuple[str, dict[str, object]]:
    patched = xml_text
    changes: list[str] = []
    replacements = [
        (
            r'<Databank label="Output databank" name="Output" value="[^"]*" />',
            f'<Databank label="Output databank" name="Output" value="{OUTPUT_DATABANK}" />',
            "output databank",
        ),
        (
            r'<Databank label="Input databank" name="Input" value="[^"]*" />',
            f'<Databank label="Input databank" name="Input" value="{SOURCE_DATABANK}" />',
            "input databank",
        ),
        (
            r'<CustomAnalysis method="[^"]*" filter="[^"]*" inputArgs="[^"]*" />',
            f'<CustomAnalysis method="{CUSTOM_ANALYSIS_ID}" filter="false" inputArgs="" />',
            "custom analysis",
        ),
        (
            r'<FitPortfolio active="[^"]*" databank="[^"]*">',
            '<FitPortfolio active="false" databank="Existing portfolio">',
            "fit portfolio",
        ),
        (
            r'<CrossChecks use="[^"]*" evaluateAll="[^"]*">',
            '<CrossChecks use="false" evaluateAll="false">',
            "cross checks",
        ),
    ]
    for pattern, replacement, label in replacements:
        patched, _ = _replace_once(patched, pattern, replacement, label)
        changes.append(label)
    return patched, {
        "taskXMLFile": "Retest-Task2.xml",
        "title": TAG_TASK_TITLE,
        "input": SOURCE_DATABANK,
        "output": OUTPUT_DATABANK,
        "customAnalysis": CUSTOM_ANALYSIS_ID,
        "fitPortfolioActive": False,
        "crossChecksUse": False,
        "changed": changes,
    }


def _patch_project_cfx(cfx_path: Path, target_project: str) -> dict[str, object]:
    entries = _load_project_cfx(cfx_path)
    config_text = _read_zip_text(entries, "config.xml")
    retest_text = _read_zip_text(entries, "Retest-Task2.xml")
    patched_config, config_summary = _patch_config_xml(config_text, target_project)
    patched_retest, retest_summary = _patch_retest_task_xml(retest_text)
    entries["config.xml"] = patched_config.encode("utf-8")
    entries["Retest-Task2.xml"] = patched_retest.encode("utf-8")
    _write_project_cfx(entries, cfx_path)
    return {
        "config": config_summary,
        "tagTask": retest_summary,
    }


def _inspect_project_cfx(cfx_path: Path) -> dict[str, object]:
    if not cfx_path.is_file():
        return {"exists": False}
    entries = _load_project_cfx(cfx_path)
    result: dict[str, object] = {"exists": True, "hash": _file_sha256(cfx_path)}
    try:
        root = ET.fromstring(_read_zip_text(entries, "config.xml"))
        databank_views = {}
        databanks = root.find("Databanks")
        if databanks is not None:
            for databank in databanks.findall("Databank"):
                name = databank.attrib.get("name", "")
                if name in {SOURCE_DATABANK, SECONDARY_DATABANK, OUTPUT_DATABANK, "Foward"}:
                    databank_views[name] = databank.attrib.get("view", "")
        task_titles = {}
        tasks = root.find("Tasks")
        if tasks is not None:
            for task in tasks.findall("Task"):
                if task.attrib.get("taskXMLFile") == "Retest-Task2.xml":
                    task_titles["Retest-Task2.xml"] = {
                        "title": task.attrib.get("title", ""),
                        "active": task.attrib.get("active", ""),
                    }
        retest_text = _read_zip_text(entries, "Retest-Task2.xml")
        result.update(
            {
                "projectName": root.attrib.get("name", ""),
                "databankViews": databank_views,
                "tagTask": task_titles.get("Retest-Task2.xml", {}),
                "tagTaskInput": _match_value(retest_text, r'<Databank label="Input databank" name="Input" value="([^"]*)" />'),
                "tagTaskOutput": _match_value(retest_text, r'<Databank label="Output databank" name="Output" value="([^"]*)" />'),
                "customAnalysis": _match_value(retest_text, r'<CustomAnalysis method="([^"]*)" filter="false" inputArgs="" />'),
            }
        )
    except Exception as exc:  # pragma: no cover - surfaced in status JSON
        result["inspectError"] = str(exc)
    return result


def _match_value(text: str, pattern: str) -> str:
    match = re.search(pattern, text)
    return match.group(1) if match else ""


def _copy_lab_project(donor_dir: Path, target_dir: Path) -> dict[str, object]:
    target_dir.mkdir(parents=True)
    shutil.copy2(donor_dir / "project.cfx", target_dir / "project.cfx")
    databanks_root = target_dir / "databanks"
    databanks_root.mkdir()
    copied_counts: dict[str, int] = {}
    for databank_name in (SOURCE_DATABANK, SECONDARY_DATABANK):
        source = donor_dir / "databanks" / databank_name
        if not source.is_dir():
            raise ValueError(f"donor missing databank: {databank_name}")
        destination = databanks_root / databank_name
        shutil.copytree(source, destination)
        copied_counts[databank_name] = len(list(destination.glob("*.sqx")))
    (databanks_root / OUTPUT_DATABANK).mkdir()
    (target_dir / "log").mkdir()
    return {
        "copiedDatabanks": copied_counts,
        "emptyOutputDatabank": OUTPUT_DATABANK,
        "logsCopied": False,
    }


def build_status(args: argparse.Namespace) -> dict[str, object]:
    sqx_root = Path(args.sqx_root)
    projects_root = _projects_root(sqx_root)
    donor_dir = _resolve_inside(projects_root / args.donor_project, projects_root)
    target_dir = _resolve_inside(projects_root / args.target_project, projects_root)
    donor_counts = _databank_counts(donor_dir) if donor_dir.is_dir() else {}
    target_counts = _databank_counts(target_dir) if target_dir.is_dir() else {}
    donor_retired_preflight = _retired_dependency_preflight(donor_dir) if donor_dir.is_dir() else {"ok": False, "status": "donor_missing"}
    target_retired_preflight = _retired_dependency_preflight(target_dir) if target_dir.is_dir() else {"ok": False, "status": "target_missing"}
    return {
        "ok": True,
        "version": VERSION,
        "action": "status",
        "donorProject": args.donor_project,
        "targetProject": args.target_project,
        "donorExists": donor_dir.is_dir(),
        "targetExists": target_dir.is_dir(),
        "donorDatabanks": {
            SOURCE_DATABANK: donor_counts.get(SOURCE_DATABANK, 0),
            SECONDARY_DATABANK: donor_counts.get(SECONDARY_DATABANK, 0),
        },
        "targetDatabanks": {
            SOURCE_DATABANK: target_counts.get(SOURCE_DATABANK, 0),
            SECONDARY_DATABANK: target_counts.get(SECONDARY_DATABANK, 0),
            OUTPUT_DATABANK: target_counts.get(OUTPUT_DATABANK, 0),
        },
        "targetCfx": _inspect_project_cfx(target_dir / "project.cfx"),
        "retiredDependencyPreflight": {
            "donor": donor_retired_preflight,
            "target": target_retired_preflight,
        },
        "expected": {
            "view": VIEW_NAME,
            "customAnalysis": CUSTOM_ANALYSIS_ID,
            "tagTaskTitle": TAG_TASK_TITLE,
            "input": SOURCE_DATABANK,
            "output": OUTPUT_DATABANK,
        },
        "guards": {
            "sqx_runtime_started_by_script": False,
            "data_db_write_allowed": False,
            "jars_write_allowed": False,
            "internal_plugins_write_allowed": False,
            "license_activation_write_allowed": False,
            "databank_delete_allowed": False,
            "run_project_allowed": False,
            "migration_tool_allowed": False,
        },
    }


def build_plan(args: argparse.Namespace) -> dict[str, object]:
    status = build_status(args)
    return {
        "ok": True,
        "version": VERSION,
        "action": "plan",
        "status": status,
        "operations": [
            f"copy donor project {args.donor_project} to {args.target_project}",
            f"copy only databanks {SOURCE_DATABANK} and {SECONDARY_DATABANK}",
            f"create empty output databank {OUTPUT_DATABANK}",
            f"patch project.cfx project name to {args.target_project}",
            f"patch databank views to {VIEW_NAME}",
            f"patch Retest-Task2.xml as {TAG_TASK_TITLE} with {CUSTOM_ANALYSIS_ID}",
            "preflight copied databanks for retired strategy dependencies before any future install",
        ],
        "rollback": "move target lab project to SQXEdge quarantine; no recursive delete",
    }


def install(args: argparse.Namespace) -> dict[str, object]:
    sqx_root = Path(args.sqx_root)
    projects_root = _projects_root(sqx_root)
    if not projects_root.is_dir():
        raise ValueError(f"projects root not found: {projects_root}")
    donor_dir = _resolve_inside(projects_root / args.donor_project, projects_root)
    target_dir = _resolve_inside(projects_root / args.target_project, projects_root)
    if not donor_dir.is_dir():
        raise ValueError(f"donor project not found: {donor_dir}")
    if target_dir.exists():
        raise ValueError(f"target project already exists: {target_dir}")

    donor_counts = _databank_counts(donor_dir)
    if donor_counts.get(SOURCE_DATABANK, 0) <= 0:
        raise ValueError(f"donor databank {SOURCE_DATABANK} is empty or missing")
    if donor_counts.get(SECONDARY_DATABANK, 0) <= 0:
        raise ValueError(f"donor databank {SECONDARY_DATABANK} is empty or missing")
    retired_preflight = _retired_dependency_preflight(donor_dir)
    if retired_preflight.get("blocked"):
        raise ValueError(
            "donor databanks contain retired strategy dependencies "
            + ",".join(RETIRED_STRATEGY_DEPENDENCIES)
            + "; create a fresh mining/custom project or choose a clean donor"
        )

    backup_root = _local_root() / "backups"
    backup_root.mkdir(parents=True, exist_ok=True)
    backup_id = f"{VERSION}_{_utc_stamp()}"
    backup_dir = backup_root / backup_id
    backup_dir.mkdir()

    before_hash = _dir_hash(donor_dir)
    copy_summary = _copy_lab_project(donor_dir, target_dir)
    patch_summary = _patch_project_cfx(target_dir / "project.cfx", args.target_project)
    after_hash = _dir_hash(target_dir)
    status = build_status(args)
    evidence = {
        "ok": True,
        "version": VERSION,
        "action": "install",
        "installedAt": _now_iso(),
        "backupId": backup_id,
        "donorProject": args.donor_project,
        "targetProject": args.target_project,
        "donorDirHash": before_hash,
        "targetDirHash": after_hash,
        "copy": copy_summary,
        "patch": patch_summary,
        "retiredDependencyPreflight": retired_preflight,
        "status": status,
        "blockedSurfaces": [
            "SQX runtime launch",
            "data.db",
            "jars",
            "internal plugins",
            "license/activation",
            "databank deletion",
            "run_project",
            "Migration Tool",
        ],
    }
    (backup_dir / "rollback_manifest.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    (_local_root() / f"{VERSION}_install_{backup_id.rsplit('_', 1)[-1]}.json").write_text(
        json.dumps(evidence, indent=2),
        encoding="utf-8",
    )
    return evidence


def _resolve_backup(args: argparse.Namespace) -> Path:
    backup_root = _local_root() / "backups"
    if args.backup_id:
        candidate = backup_root / args.backup_id
        if candidate.is_dir():
            return candidate
        raise ValueError(f"backup id not found: {args.backup_id}")
    backups = sorted((p for p in backup_root.glob(f"{VERSION}_*") if p.is_dir()), key=lambda p: p.stat().st_mtime, reverse=True)
    if not backups:
        raise ValueError("no lab scaffold backup available")
    return backups[0]


def rollback(args: argparse.Namespace) -> dict[str, object]:
    sqx_root = Path(args.sqx_root)
    projects_root = _projects_root(sqx_root)
    quarantine_root = _quarantine_root(sqx_root)
    backup_dir = _resolve_backup(args)
    manifest = json.loads((backup_dir / "rollback_manifest.json").read_text(encoding="utf-8"))
    target_project = manifest["targetProject"]
    target_dir = _resolve_inside(projects_root / target_project, projects_root)
    quarantine_dir = _resolve_inside(quarantine_root / backup_dir.name / target_project, quarantine_root)
    quarantine_dir.parent.mkdir(parents=True, exist_ok=True)
    if target_dir.exists():
        shutil.move(str(target_dir), str(quarantine_dir))
        result = "moved_to_quarantine"
    else:
        result = "already_absent"
    return {
        "ok": True,
        "version": VERSION,
        "action": "rollback",
        "backupId": backup_dir.name,
        "targetProject": target_project,
        "result": result,
        "quarantineHash": _dir_hash(quarantine_dir),
        "targetExistsAfterRollback": target_dir.exists(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a lab-only SQX142 project for Correlation Pack manual confirmation.")
    parser.add_argument("--action", choices=["status", "plan", "install", "rollback"], default="status")
    parser.add_argument("--sqx-root", default=os.environ.get("SQX142_ROOT", "<LOCAL_SQX142_ROOT>"))
    parser.add_argument("--donor-project", default=DEFAULT_DONOR)
    parser.add_argument("--target-project", default=DEFAULT_TARGET)
    parser.add_argument("--backup-id", default="")
    args = parser.parse_args()

    if args.action == "status":
        result = build_status(args)
    elif args.action == "plan":
        result = build_plan(args)
    elif args.action == "install":
        result = install(args)
    elif args.action == "rollback":
        result = rollback(args)
    else:  # pragma: no cover
        raise ValueError(f"unsupported action: {args.action}")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
