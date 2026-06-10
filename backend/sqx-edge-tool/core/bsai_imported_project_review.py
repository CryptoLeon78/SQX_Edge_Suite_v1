from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from .bsai_resource_compatibility import (
    DEFAULT_CANDIDATE_ID,
    DEFAULT_REMAP_SUFFIX,
    DEFAULT_TARGET_PROFILE_ID,
    candidate_pair_filenames,
    load_candidate_metadata,
    load_target_catalog,
)


BS_AI12_IMPORTED_PROJECT_REVIEW_VERSION = "bs-ai12-imported-project-readonly-review-v1"
EXPECTED_IMPORTED_TASKS = 14
EVIDENCE_DIR_PARTS = (".local", "blocksettings_ai", "import_gate")


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _tool_root(project_root: Path) -> Path:
    return project_root / "backend" / "sqx-edge-tool"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_config(project_root: Path) -> dict[str, Any]:
    path = _tool_root(project_root) / "config.json"
    if not path.is_file():
        raise FileNotFoundError("sqx_edge_config_missing")
    return _load_json(path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _candidate_public(project_root: Path, candidate_id: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    meta = load_candidate_metadata(project_root, candidate_id)
    entry = dict(meta.get("entry") if isinstance(meta.get("entry"), dict) else {})
    recipe = dict(meta.get("recipe") if isinstance(meta.get("recipe"), dict) else {})
    public = {
        "id": candidate_id,
        "layer": int(entry.get("layer") or recipe.get("candidateLayer") or 0),
        "baseCanonicalId": entry.get("baseCanonicalId") or recipe.get("baseCanonicalId"),
        "baseVariant": entry.get("baseVariant") or recipe.get("baseVariant"),
        "baseSha256Short": str(entry.get("baseSha256") or recipe.get("baseSha256") or "")[:12],
        "candidateRevision": entry.get("candidateRevision"),
        "sourceVersionPolicy": entry.get("sourceVersionPolicy") or recipe.get("sourceVersionPolicy"),
        "promotionState": entry.get("promotionState"),
        "activeBlocks": len(entry.get("activeBlocks") or []),
        "activeIndicators": len(entry.get("activeIndicators") or []),
        "activeIndicatorNames": list(entry.get("activeIndicators") or [])[:12],
        "asset": recipe.get("asset"),
        "timeframe": recipe.get("timeframe"),
        "direction": recipe.get("direction"),
    }
    return public, entry, recipe


def imported_project_names(project_root: str | Path, candidate_id: str, *, suffix: str = DEFAULT_REMAP_SUFFIX) -> list[str]:
    root = _project_root(project_root)
    return [Path(filename).stem for filename in candidate_pair_filenames(_candidate_recipe(root, candidate_id), candidate_id, suffix=suffix)]


def _candidate_recipe(project_root: Path, candidate_id: str) -> dict[str, Any]:
    meta = load_candidate_metadata(project_root, candidate_id)
    recipe = meta.get("recipe") if isinstance(meta.get("recipe"), dict) else {}
    if not recipe:
        raise ValueError("bsai_candidate_recipe_missing")
    return dict(recipe)


def _host_project_cfx(config: dict[str, Any], project_name: str) -> Path:
    return Path(str(config.get("sqx_projects_dir") or "")) / project_name / "project.cfx"


def _asset_from_candidate(candidate: dict[str, Any]) -> str:
    return str(candidate.get("asset") or "AUDCAD").upper()


def _capa_from_project_name(project_name: str) -> int | None:
    if project_name.endswith("_Capa1") or "_Capa1" in project_name:
        return 1
    if project_name.endswith("_Capa2") or "_Capa2" in project_name:
        return 2
    return None


def _read_remote_projects(remote_base_url: str | None, project_names: list[str]) -> dict[str, Any]:
    if not remote_base_url:
        return {
            "reachable": None,
            "endpoint": "taskmanager/listProjects",
            "matches": [],
            "matchCount": 0,
            "skipped": True,
        }
    url = remote_base_url.rstrip("/") + "/taskmanager/listProjects"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8", "replace"))
    except Exception:
        return {
            "reachable": False,
            "endpoint": "taskmanager/listProjects",
            "matches": [],
            "matchCount": 0,
            "errorCode": "remote_access_unavailable",
        }
    matches = []
    by_name = {str(item.get("projectName") or ""): item for item in data.get("projects") or []}
    for name in project_names:
        item = by_name.get(name)
        matches.append({
            "projectName": name,
            "found": item is not None,
            "tasks": int(item.get("tasks") or 0) if item else None,
            "databanks": int(item.get("databanks") or 0) if item else None,
            "strategies": int(item.get("strategies") or 0) if item else None,
            "hasUnresolvedResources": bool(item.get("hasUnresolvedResources")) if item else None,
            "sqxReturnedProjectPath": bool(item and item.get("filePath")),
            "sqxProjectPathStored": False,
        })
    return {
        "reachable": True,
        "endpoint": "taskmanager/listProjects",
        "successMessagePresent": bool(data.get("success")),
        "matches": matches,
        "matchCount": sum(1 for item in matches if item["found"]),
    }


def _parse_config_tasks(config_xml: bytes) -> tuple[str | None, str | None, list[dict[str, Any]]]:
    root = ET.fromstring(config_xml)
    tasks = []
    for task in root.findall(".//Task"):
        tasks.append({
            "xmlFile": str(task.get("taskXMLFile") or ""),
            "type": str(task.get("type") or ""),
            "name": str(task.get("name") or ""),
            "title": str(task.get("title") or ""),
            "active": str(task.get("active") or "").lower() != "false",
        })
    return root.get("name"), root.get("version"), tasks


def _active_build_blocksetting(tasks: list[dict[str, Any]]) -> str | None:
    build = next((task for task in tasks if task.get("type") == "Build"), None)
    title = str(build.get("title") or "") if build else ""
    match = re.match(r"^Build\s+(.+?)\s+·", title)
    if match:
        return match.group(1)
    return title or None


def _xml_token_summary(archive: zipfile.ZipFile, tokens: list[str]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    files: dict[str, list[str]] = {token: [] for token in tokens}
    for name in archive.namelist():
        if not name.endswith(".xml"):
            continue
        text = archive.read(name).decode("utf-8", "replace")
        for token in tokens:
            count = text.count(token)
            if count:
                counts[token] += count
                files[token].append(name)
    return {
        "counts": dict(counts),
        "files": {token: files[token] for token in tokens if files[token]},
    }


def _resource_uses(project_name: str, archive: zipfile.ZipFile) -> list[dict[str, Any]]:
    capa = _capa_from_project_name(project_name)
    uses = []
    for name in archive.namelist():
        if not name.endswith(".xml") or name == "config.xml":
            continue
        root = ET.fromstring(archive.read(name))
        for symbol in root.findall(".//Resources/Symbols/Symbol"):
            info = symbol.find("InstrumentInfo")
            uses.append({
                "projectName": project_name,
                "capa": capa,
                "xmlFile": name,
                "symbol": str(symbol.get("name") or ""),
                "source": str(symbol.get("source") or ""),
                "broker": str(symbol.get("broker") or ""),
                "instrument": str(info.get("instrument") if info is not None else ""),
                "instrumentBroker": str(info.get("broker") if info is not None else ""),
            })
    return uses


def _catalog_has(catalog: dict[str, Any], symbol: str, source: str, broker: str) -> bool:
    for row in catalog.get("dataSymbols") or []:
        if (
            row.get("symbol") == symbol
            and str(row.get("source") or "") == str(source)
            and str(row.get("brokerId") or "") == str(broker)
            and bool(row.get("rowsPositive"))
        ):
            return True
    return False


def _allowed_cross(use: dict[str, Any]) -> bool:
    return (
        use.get("source") == "2"
        and (
            (use.get("capa") == 1 and use.get("xmlFile") == "Retest-Task1.xml")
            or (use.get("capa") == 2 and use.get("xmlFile") == "AutomaticRetest-Task7.xml")
        )
    )


def _resource_review(uses: list[dict[str, Any]], catalog: dict[str, Any]) -> dict[str, Any]:
    expected_primary = str(catalog.get("expectedPrimarySymbol") or "")
    expected_cross = str(catalog.get("expectedCrossBrokerSymbol") or "")
    issues = []
    for use in uses:
        if _allowed_cross(use):
            if use["symbol"] != expected_cross:
                issues.append({
                    "severity": "fail",
                    "code": "methodology_cross_broker_symbol_unexpected",
                    "projectName": use["projectName"],
                    "xmlFile": use["xmlFile"],
                })
            elif not _catalog_has(catalog, use["symbol"], use["source"], use["broker"]):
                issues.append({
                    "severity": "fail",
                    "code": "methodology_cross_broker_missing_in_sqx144_catalog",
                    "projectName": use["projectName"],
                    "xmlFile": use["xmlFile"],
                })
            else:
                issues.append({
                    "severity": "warn",
                    "code": "methodology_cross_broker_catalog_match",
                    "projectName": use["projectName"],
                    "xmlFile": use["xmlFile"],
                })
            continue
        if use["symbol"] != expected_primary or use["source"] != "4" or use["broker"] != "4":
            issues.append({
                "severity": "fail",
                "code": "primary_resource_mismatch_for_sqx144_full",
                "projectName": use["projectName"],
                "xmlFile": use["xmlFile"],
            })
        elif not _catalog_has(catalog, use["symbol"], use["source"], use["broker"]):
            issues.append({
                "severity": "fail",
                "code": "target_symbol_missing_in_sqx144_catalog",
                "projectName": use["projectName"],
                "xmlFile": use["xmlFile"],
            })
    resource_keys = Counter(f"{use['symbol']}|source:{use['source']}|broker:{use['broker']}" for use in uses)
    fail_count = sum(1 for issue in issues if issue["severity"] == "fail")
    warn_count = sum(1 for issue in issues if issue["severity"] == "warn")
    return {
        "verdict": "fail" if fail_count else "warn" if warn_count else "pass",
        "failCount": fail_count,
        "warnCount": warn_count,
        "issues": issues,
        "resourceUseCount": len(uses),
        "resourceUseGroups": dict(sorted(resource_keys.items())),
        "uses": [
            {
                "projectName": use["projectName"],
                "capa": use["capa"],
                "xmlFile": use["xmlFile"],
                "symbol": use["symbol"],
                "source": use["source"],
                "broker": use["broker"],
                "methodologyRole": "cross_broker_oos" if _allowed_cross(use) else "primary",
            }
            for use in uses
        ],
    }


def _review_cfx_project(
    config: dict[str, Any],
    project_name: str,
    candidate_id: str,
    candidate: dict[str, Any],
    catalog: dict[str, Any],
) -> dict[str, Any]:
    path = _host_project_cfx(config, project_name)
    capa = _capa_from_project_name(project_name)
    result: dict[str, Any] = {
        "projectName": project_name,
        "capa": capa,
        "exists": path.is_file(),
        "pathStored": False,
        "zipWithConfigXml": False,
        "blockers": [],
        "warnings": [],
    }
    if not path.is_file():
        result["blockers"].append("imported_project_cfx_missing")
        return result
    result["size"] = path.stat().st_size
    result["sha256"] = _sha256(path)
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            result["entryCount"] = len(names)
            result["xmlCount"] = sum(1 for name in names if name.endswith(".xml"))
            result["zipWithConfigXml"] = "config.xml" in names
            if "config.xml" not in names:
                result["blockers"].append("config_xml_missing")
                return result
            declared_name, sqx_version, tasks = _parse_config_tasks(archive.read("config.xml"))
            result["declaredProjectNameMatches"] = declared_name == project_name
            result["sqxProjectVersion"] = sqx_version
            result["taskCount"] = len(tasks)
            result["activeTaskCount"] = sum(1 for task in tasks if task["active"])
            result["taskTypeCounts"] = dict(Counter(str(task["type"]) for task in tasks))
            result["tasks"] = tasks
            task_xml_files = {task["xmlFile"] for task in tasks if task["xmlFile"]}
            archive_xml_files = {name for name in names if name.endswith(".xml") and name != "config.xml"}
            result["missingTaskXml"] = sorted(task_xml_files - archive_xml_files)
            result["extraTaskXml"] = sorted(archive_xml_files - task_xml_files)
            result["activeBuildBlockSetting"] = _active_build_blocksetting(tasks)
            tokens = [
                candidate_id,
                str(candidate.get("baseCanonicalId") or ""),
                "BS_Volatilidad_v6_intraday_v6",
                "BS_Volatilidad_v6",
                "BS_Filtros_v6",
                "BS_Filtros_v6_D1",
            ]
            result["blocksettingTokenTrace"] = _xml_token_summary(archive, [token for token in tokens if token])
            uses = _resource_uses(project_name, archive)
            result["resourceReview"] = _resource_review(uses, catalog)
    except zipfile.BadZipFile:
        result["blockers"].append("project_cfx_not_zip")
        return result
    except ET.ParseError:
        result["blockers"].append("project_cfx_xml_parse_failed")
        return result

    if not result["declaredProjectNameMatches"]:
        result["blockers"].append("declared_project_name_mismatch")
    if result["taskCount"] != EXPECTED_IMPORTED_TASKS:
        result["blockers"].append("task_count_not_14")
    if result["activeTaskCount"] != EXPECTED_IMPORTED_TASKS:
        result["blockers"].append("active_task_count_not_14")
    if result["missingTaskXml"]:
        result["blockers"].append("task_xml_missing")
    if result["resourceReview"]["failCount"]:
        result["blockers"].append("target_resource_fail")
    if result["resourceReview"]["warnCount"]:
        result["warnings"].append("methodology_cross_broker_catalog_match")
    active_bs = result.get("activeBuildBlockSetting")
    if capa == 1 and not str(active_bs or "").startswith("BS_Volatilidad_v6"):
        result["blockers"].append("capa1_official_v6_trace_missing")
    if capa == 2 and active_bs != candidate_id:
        result["blockers"].append("capa2_candidate_trace_missing")
    return result


def _base_payload(action: str, candidate_id: str, host_profile: str, remap_suffix: str) -> dict[str, Any]:
    return {
        "ok": False,
        "version": BS_AI12_IMPORTED_PROJECT_REVIEW_VERSION,
        "action": action,
        "candidateId": candidate_id,
        "hostProfile": host_profile,
        "remapSuffix": remap_suffix,
        "readOnlyReview": True,
        "projectStartAllowed": False,
        "projectStartRequested": False,
        "runsSqxTasks": False,
        "writesDataDb": False,
        "writesUserProjects": False,
        "mutatesDatabanks": False,
        "officialBlocksettingsPromotion": False,
        "migrationToolAllowed": False,
        "remoteEndpoint": "taskmanager/listProjects",
        "privacy": {
            "localPathsReturned": False,
            "rawXmlReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
        },
    }


def _privacy_guard(payload: dict[str, Any]) -> None:
    blob = json.dumps(payload, ensure_ascii=False)
    forbidden = [
        r"[A-Za-z]:[\\/]",
        r"<Project\b",
        r"<Task\b",
        r'"filePath"\s*:',
        r'"localPath"\s*:',
        r'"sqx_path"\s*:',
        r'"sqx_data_db"\s*:',
    ]
    for pattern in forbidden:
        if re.search(pattern, blob, flags=re.IGNORECASE):
            raise RuntimeError("bsai12_privacy_guard_failed")


def _write_evidence(project_root: Path, payload: dict[str, Any]) -> str:
    evidence_dir = project_root.joinpath(*EVIDENCE_DIR_PARTS)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    filename = f"bsai12_imported_project_readonly_review_{_utc_stamp()}.json"
    target = evidence_dir / filename
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return filename


def review_payload(
    project_root: str | Path,
    candidate_id: str = DEFAULT_CANDIDATE_ID,
    *,
    remap_suffix: str = DEFAULT_REMAP_SUFFIX,
    remote_base_url: str | None = "http://127.0.0.1:8080",
    write_evidence: bool = False,
    action: str = "review",
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "sqx144_full")
    payload = _base_payload(action, candidate_id, host_profile, remap_suffix)
    candidate, entry, recipe = _candidate_public(root, candidate_id)
    asset = _asset_from_candidate(candidate)
    project_names = [Path(filename).stem for filename in candidate_pair_filenames(recipe, candidate_id, suffix=remap_suffix)]
    catalog = load_target_catalog(str(config.get("sqx_data_db") or ""), asset, host_profile=host_profile)
    remote = _read_remote_projects(remote_base_url, project_names)
    projects = [
        _review_cfx_project(config, name, candidate_id, candidate, catalog)
        for name in project_names
    ]
    blockers = []
    warnings = []
    if host_profile != "sqx144_full":
        blockers.append("host_profile_not_sqx144_full")
    if candidate.get("promotionState") != "local_candidate":
        blockers.append("candidate_not_local_candidate")
    if candidate.get("sourceVersionPolicy") != "explicit_base_preserve_official_v6_v7":
        blockers.append("candidate_source_policy_not_explicit_v6_v7_preserve")
    if remote.get("reachable") is False:
        blockers.append("remote_access_unavailable")
    for match in remote.get("matches") or []:
        if not match["found"]:
            blockers.append(f"remote_project_missing:{match['projectName']}")
        if match.get("tasks") != EXPECTED_IMPORTED_TASKS:
            blockers.append(f"remote_task_count_not_14:{match['projectName']}")
        if match.get("strategies") != 0:
            blockers.append(f"remote_strategies_not_zero:{match['projectName']}")
        if match.get("hasUnresolvedResources"):
            blockers.append(f"remote_project_unresolved_resources:{match['projectName']}")
    for project in projects:
        blockers.extend(f"{project['projectName']}:{code}" for code in project.get("blockers") or [])
        warnings.extend(f"{project['projectName']}:{code}" for code in project.get("warnings") or [])
    target_fail_count = sum(project.get("resourceReview", {}).get("failCount", 0) for project in projects)
    target_warn_count = sum(project.get("resourceReview", {}).get("warnCount", 0) for project in projects)
    status = (
        "imported_project_readonly_review_blocked_no_start"
        if blockers
        else "imported_project_readonly_review_passed_no_start"
        if not warnings
        else "imported_project_readonly_review_passed_with_methodology_warnings_no_start"
    )
    payload.update({
        "status": status,
        "ok": not blockers,
        "candidate": candidate,
        "projectNames": project_names,
        "remote": remote,
        "targetCatalog": {
            "readMode": catalog.get("readMode"),
            "asset": asset,
            "expectedPrimarySymbol": catalog.get("expectedPrimarySymbol"),
            "expectedCrossBrokerSymbol": catalog.get("expectedCrossBrokerSymbol"),
            "targetSymbolPresent": catalog.get("targetSymbolPresent"),
            "crossBrokerSymbolPresent": catalog.get("crossBrokerSymbolPresent"),
            "tableCounts": catalog.get("tableCounts"),
        },
        "summary": {
            "importedProjectCount": len(projects),
            "remoteMatchCount": remote.get("matchCount"),
            "allZipWithConfigXml": all(project.get("zipWithConfigXml") for project in projects),
            "allTaskCounts14": all(project.get("taskCount") == EXPECTED_IMPORTED_TASKS for project in projects),
            "allStrategiesZero": all((match.get("strategies") == 0) for match in remote.get("matches") or []),
            "anyUnresolvedResources": any(bool(match.get("hasUnresolvedResources")) for match in remote.get("matches") or []),
            "targetFailCount": target_fail_count,
            "targetWarnCount": target_warn_count,
            "capa1ActiveBuildBlockSetting": next((project.get("activeBuildBlockSetting") for project in projects if project.get("capa") == 1), None),
            "capa2ActiveBuildBlockSetting": next((project.get("activeBuildBlockSetting") for project in projects if project.get("capa") == 2), None),
        },
        "projects": projects,
        "blockers": blockers,
        "warnings": warnings,
        "nextGate": "BS-AI13 first manual Start gate requires explicit operator approval",
    })
    if write_evidence:
        _privacy_guard(payload)
        payload["evidenceFile"] = _write_evidence(root, payload)
    _privacy_guard(payload)
    return payload


def status_payload(
    project_root: str | Path,
    candidate_id: str = DEFAULT_CANDIDATE_ID,
    *,
    remap_suffix: str = DEFAULT_REMAP_SUFFIX,
    remote_base_url: str | None = "http://127.0.0.1:8080",
) -> dict[str, Any]:
    return review_payload(
        project_root,
        candidate_id,
        remap_suffix=remap_suffix,
        remote_base_url=remote_base_url,
        write_evidence=False,
        action="status",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BS-AI12 imported project read-only review")
    parser.add_argument("action", choices=("status", "review"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--candidate-id", default=DEFAULT_CANDIDATE_ID)
    parser.add_argument("--remap-suffix", default=DEFAULT_REMAP_SUFFIX)
    parser.add_argument("--remote-base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)
    if args.action == "status":
        payload = status_payload(
            args.project_root,
            args.candidate_id,
            remap_suffix=args.remap_suffix,
            remote_base_url=args.remote_base_url,
        )
    else:
        payload = review_payload(
            args.project_root,
            args.candidate_id,
            remap_suffix=args.remap_suffix,
            remote_base_url=args.remote_base_url,
            write_evidence=args.write_evidence,
            action="review",
        )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
