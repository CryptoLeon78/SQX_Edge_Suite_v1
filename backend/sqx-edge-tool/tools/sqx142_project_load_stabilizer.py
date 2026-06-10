from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import time
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


VERSION = "sqx142-project-load-stabilizer-v1"
DEFAULT_SQX_ROOT = Path(os.environ.get("SQX142_ROOT", "<LOCAL_SQX142_ROOT>"))
DEFAULT_PROJECTS = (
    "Mining15_AUDCAD_H1_BS_Momentum_v6_Capa1",
    "Mining15_AUDCAD_H1_BS_Momentum_v6_Capa2",
)
BLOCKED_SURFACES = (
    "jars",
    "plugins",
    "license/activation",
    "data.db writes",
    "user/data",
    "databank deletion",
    "run_project",
    "Migration Tool",
)
ELECTRON_HTTP_CACHE = (
    "internal",
    "electron",
    "resources",
    "userData",
    "SQUANT",
    "Cache",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _assert_in_root(path: Path, root: Path) -> None:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise RuntimeError(f"Path escapes root: path={resolved_path} root={resolved_root}")


def _read_data_db_catalog(sqx_root: Path) -> dict[str, set[str]]:
    db_path = sqx_root / "user" / "data" / "data.db"
    if not db_path.exists():
        return {"symbols": set(), "instruments": set(), "brokers": set()}
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        symbols = {
            str(row[0])
            for row in con.execute("select SYMBOL from DATA where SYMBOL is not null").fetchall()
        }
        instruments = {
            str(row[0])
            for row in con.execute(
                "select INSTRUMENT from INSTRUMENTS where INSTRUMENT is not null"
            ).fetchall()
        }
        brokers = {
            str(row[0])
            for row in con.execute("select ID from BROKER where ID is not null").fetchall()
        }
        return {"symbols": symbols, "instruments": instruments, "brokers": brokers}
    finally:
        con.close()


def _xml_texts(cfx: Path) -> dict[str, str]:
    texts: dict[str, str] = {}
    with zipfile.ZipFile(cfx) as archive:
        bad_entry = archive.testzip()
        if bad_entry:
            raise RuntimeError(f"Invalid zip entry: {bad_entry}")
        for name in archive.namelist():
            if name.endswith(".xml"):
                texts[name] = archive.read(name).decode("utf-8-sig")
    return texts


def _resources_report(entry: str, text: str, catalog: dict[str, set[str]]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return [{"entry": entry, "code": "xml_parse_error", "detail": str(exc)}]

    chart_symbols = {
        chart.get("symbol")
        for chart in root.findall(".//Chart")
        if chart.get("symbol")
    }
    for symbol in sorted(chart_symbols):
        if symbol not in catalog["symbols"]:
            findings.append(
                {
                    "entry": entry,
                    "code": "chart_symbol_missing_from_data_db",
                    "symbol": symbol,
                }
            )

    for resources in root.findall(".//Resources"):
        declared_brokers = {
            broker.get("id")
            for broker in resources.findall("./Brokers/Broker")
            if broker.get("id")
        }
        custom_blocks = resources.find("./CustomBlocks")
        if custom_blocks is not None and len(list(custom_blocks)) > 0:
            findings.append(
                {
                    "entry": entry,
                    "code": "custom_block_resources_present",
                    "count": str(len(list(custom_blocks))),
                }
            )
        for symbol_node in resources.findall("./Symbols/Symbol"):
            symbol_name = symbol_node.get("name") or ""
            broker_id = symbol_node.get("broker") or ""
            if symbol_name and symbol_name not in catalog["symbols"]:
                findings.append(
                    {
                        "entry": entry,
                        "code": "resource_symbol_missing_from_data_db",
                        "symbol": symbol_name,
                    }
                )
            if broker_id:
                if broker_id not in declared_brokers:
                    findings.append(
                        {
                            "entry": entry,
                            "code": "resource_broker_not_declared_in_cfx_entry",
                            "broker": broker_id,
                            "symbol": symbol_name,
                        }
                    )
                if broker_id not in catalog["brokers"]:
                    findings.append(
                        {
                            "entry": entry,
                            "code": "resource_broker_missing_from_data_db",
                            "broker": broker_id,
                            "symbol": symbol_name,
                        }
                    )
            info = symbol_node.find("./InstrumentInfo")
            if info is not None:
                instrument = info.get("instrument") or ""
                info_broker = info.get("broker") or ""
                if instrument and instrument not in catalog["instruments"]:
                    findings.append(
                        {
                            "entry": entry,
                            "code": "instrument_missing_from_data_db",
                            "instrument": instrument,
                            "symbol": symbol_name,
                        }
                    )
                if info_broker and info_broker not in catalog["brokers"]:
                    findings.append(
                        {
                            "entry": entry,
                            "code": "instrument_broker_missing_from_data_db",
                            "broker": info_broker,
                            "instrument": instrument,
                        }
                    )
    return findings


def _project_report(project_dir: Path, sqx_root: Path, catalog: dict[str, set[str]]) -> dict:
    cfx = project_dir / "project.cfx"
    report: dict = {
        "project": project_dir.name,
        "path": str(project_dir),
        "exists": project_dir.exists(),
        "projectCfxExists": cfx.exists(),
        "findings": [],
        "actions": [],
    }
    if not project_dir.exists() or not cfx.exists():
        report["actions"].append({"code": "project_cfx_missing"})
        return report

    report["projectCfxHash"] = _sha256(cfx)
    temp_files = sorted(project_dir.glob("zipfstmp*.tmp"))
    report["staleZipTempFiles"] = [path.name for path in temp_files]
    report["actions"].extend(
        {"code": "move_stale_zip_temp_file", "file": path.name} for path in temp_files
    )

    try:
        texts = _xml_texts(cfx)
    except Exception as exc:
        report["findings"].append({"code": "invalid_project_cfx", "detail": str(exc)})
        report["actions"].append({"code": "repack_project_cfx"})
        return report

    config = texts.get("config.xml", "")
    if config:
        try:
            config_root = ET.fromstring(config)
            config_name = config_root.get("name") or ""
            report["configName"] = config_name
            report["configVersion"] = config_root.get("version") or ""
            if config_name and config_name != project_dir.name:
                report["findings"].append(
                    {
                        "code": "config_name_mismatch",
                        "configName": config_name,
                        "folderName": project_dir.name,
                    }
                )
        except ET.ParseError as exc:
            report["findings"].append({"code": "config_xml_parse_error", "detail": str(exc)})
    else:
        report["findings"].append({"code": "config_xml_missing"})

    xml_entries = 0
    for entry, text in texts.items():
        if entry == "config.xml":
            continue
        xml_entries += 1
        report["findings"].extend(_resources_report(entry, text, catalog))
    report["taskXmlEntries"] = xml_entries
    if report["actions"] or report["findings"]:
        report["actions"].append({"code": "repack_project_cfx"})
    return report


def plan(sqx_root: Path, projects: tuple[str, ...]) -> dict:
    projects_root = sqx_root / "user" / "projects"
    catalog = _read_data_db_catalog(sqx_root)
    reports = [_project_report(projects_root / name, sqx_root, catalog) for name in projects]
    return {
        "ok": True,
        "version": VERSION,
        "action": "plan",
        "sqxRoot": str(sqx_root),
        "projects": reports,
        "blockedSurfaces": BLOCKED_SURFACES,
    }


def _repack_cfx(cfx: Path) -> str:
    before_hash = _sha256(cfx)
    temp = cfx.with_name(f"{cfx.name}.sqxedge_stabilize_tmp")
    with zipfile.ZipFile(cfx, "r") as source, zipfile.ZipFile(
        temp, "w", compression=zipfile.ZIP_DEFLATED
    ) as target:
        for item in source.infolist():
            target.writestr(item, source.read(item.filename))
    with zipfile.ZipFile(temp) as archive:
        bad_entry = archive.testzip()
        if bad_entry:
            raise RuntimeError(f"Repacked CFX failed zip test at {bad_entry}")
    os.replace(temp, cfx)
    return before_hash


def stabilize(sqx_root: Path, repo_root: Path, projects: tuple[str, ...]) -> dict:
    projects_root = sqx_root / "user" / "projects"
    backup_root = (
        repo_root
        / ".local"
        / "sqx142_project_load_stabilizer"
        / "backups"
        / f"{VERSION}_{time.strftime('%Y%m%d_%H%M%S')}"
    )
    backup_root.mkdir(parents=True, exist_ok=True)
    results = []
    for name in projects:
        project_dir = projects_root / name
        _assert_in_root(project_dir, projects_root)
        cfx = project_dir / "project.cfx"
        result: dict = {"project": name, "exists": project_dir.exists(), "changed": False}
        if not project_dir.exists() or not cfx.exists():
            result["projectCfxExists"] = cfx.exists()
            results.append(result)
            continue
        project_backup = backup_root / name
        project_backup.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cfx, project_backup / "project.cfx")
        before_hash = _sha256(cfx)
        moved_temp_files = []
        temp_backup = project_backup / "stale_zip_temp"
        for temp_file in sorted(project_dir.glob("zipfstmp*.tmp")):
            _assert_in_root(temp_file, project_dir)
            temp_backup.mkdir(exist_ok=True)
            destination = temp_backup / temp_file.name
            shutil.move(str(temp_file), str(destination))
            moved_temp_files.append({"from": str(temp_file), "to": str(destination)})
        repack_before_hash = _repack_cfx(cfx)
        after_hash = _sha256(cfx)
        result.update(
            {
                "changed": bool(moved_temp_files or before_hash != after_hash),
                "backupProjectCfx": str(project_backup / "project.cfx"),
                "beforeHash": before_hash,
                "repackBeforeHash": repack_before_hash,
                "afterHash": after_hash,
                "movedTempFiles": moved_temp_files,
            }
        )
        results.append(result)
    manifest = {
        "ok": True,
        "version": VERSION,
        "action": "stabilize",
        "backupId": backup_root.name,
        "backupRoot": str(backup_root),
        "projects": results,
        "blockedSurfaces": BLOCKED_SURFACES,
    }
    (backup_root / "rollback_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest


def clear_ui_cache(sqx_root: Path, repo_root: Path) -> dict:
    cache_dir = sqx_root.joinpath(*ELECTRON_HTTP_CACHE)
    backup_root = (
        repo_root
        / ".local"
        / "sqx142_project_load_stabilizer"
        / "ui_cache_backups"
        / f"sqx142-electron-http-cache_{time.strftime('%Y%m%d_%H%M%S')}"
    )
    backup_parent = backup_root.parent
    backup_root.mkdir(parents=True, exist_ok=True)
    _assert_in_root(backup_root, backup_parent)

    manifest: dict = {
        "ok": True,
        "version": VERSION,
        "action": "clear-ui-cache",
        "sqxRoot": str(sqx_root),
        "cacheDir": str(cache_dir),
        "backupRoot": str(backup_root),
        "movedHttpCache": False,
        "blockedSurfaces": BLOCKED_SURFACES,
    }
    if cache_dir.exists():
        _assert_in_root(cache_dir, sqx_root / "internal" / "electron" / "resources" / "userData")
        files = [
            {
                "path": str(path.relative_to(cache_dir)),
                "length": path.stat().st_size,
                "mtime": int(path.stat().st_mtime),
            }
            for path in sorted(cache_dir.rglob("*"))
            if path.is_file()
        ]
        (backup_root / "cache_manifest_before.json").write_text(
            json.dumps(files, indent=2), encoding="utf-8"
        )
        destination = backup_root / "Cache"
        shutil.move(str(cache_dir), str(destination))
        manifest.update(
            {
                "movedHttpCache": True,
                "backupCacheDir": str(destination),
                "fileCount": len(files),
            }
        )
    (backup_root / "rollback_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest


def _latest_backup(repo_root: Path) -> Path:
    backup_parent = repo_root / ".local" / "sqx142_project_load_stabilizer" / "backups"
    backups = sorted(
        (path for path in backup_parent.glob(f"{VERSION}_*") if path.is_dir()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not backups:
        raise RuntimeError("No sqx142 project load stabilizer backup found.")
    return backups[0]


def rollback(sqx_root: Path, repo_root: Path, backup_id: str) -> dict:
    backup_root = (
        repo_root / ".local" / "sqx142_project_load_stabilizer" / "backups" / backup_id
        if backup_id
        else _latest_backup(repo_root)
    )
    manifest_path = backup_root / "rollback_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    projects_root = sqx_root / "user" / "projects"
    restored = []
    for project in manifest["projects"]:
        if not project.get("exists") or not project.get("backupProjectCfx"):
            continue
        project_dir = projects_root / project["project"]
        _assert_in_root(project_dir, projects_root)
        cfx = project_dir / "project.cfx"
        backup_cfx = Path(project["backupProjectCfx"])
        shutil.copy2(backup_cfx, cfx)
        restored_temps = []
        for moved in project.get("movedTempFiles", []):
            source = Path(moved["to"])
            destination = Path(moved["from"])
            _assert_in_root(destination, project_dir)
            if destination.exists():
                raise RuntimeError(f"Rollback temp destination already exists: {destination}")
            if source.exists():
                shutil.move(str(source), str(destination))
                restored_temps.append(str(destination))
        restored.append(
            {
                "project": project["project"],
                "projectCfxHash": _sha256(cfx),
                "restoredTempFiles": restored_temps,
            }
        )
    return {
        "ok": True,
        "version": VERSION,
        "action": "rollback",
        "backupId": backup_root.name,
        "restored": restored,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action",
        choices=("status", "plan", "stabilize", "rollback", "clear-ui-cache"),
        default="plan",
    )
    parser.add_argument("--sqx-root", default=str(DEFAULT_SQX_ROOT))
    parser.add_argument("--repo-root", default=str(Path.cwd()))
    parser.add_argument("--project", action="append", default=[])
    parser.add_argument("--backup-id", default="")
    args = parser.parse_args()

    sqx_root = Path(args.sqx_root)
    repo_root = Path(args.repo_root)
    projects = tuple(args.project) if args.project else DEFAULT_PROJECTS
    if args.action in {"status", "plan"}:
        result = plan(sqx_root, projects)
        result["action"] = args.action
    elif args.action == "stabilize":
        result = stabilize(sqx_root, repo_root, projects)
    elif args.action == "clear-ui-cache":
        result = clear_ui_cache(sqx_root, repo_root)
    else:
        result = rollback(sqx_root, repo_root, args.backup_id)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
