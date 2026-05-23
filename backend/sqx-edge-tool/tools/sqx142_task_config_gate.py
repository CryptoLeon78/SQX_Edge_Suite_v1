from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_SQX_ROOT = Path(r"C:\BOTS\Versiones\SQX_142_Crack")
DEFAULT_DONOR_PROJECT = "Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1"
DEFAULT_BASE_PROJECT = "Capa1_Long_SQX142_Base"
DEFAULT_TEMPLATE = TOOL_ROOT / "templates" / "Capa1_Long.cfx"
LEDGER_DIRNAME = ".local/sqx142_task_config"
VERSION = "sqx142-task-config-gate-v1"

PHASES = [
    {"id": "phase0", "label": "preflight, snapshots and semantic diff"},
    {"id": "phase1", "label": "selective donor-to-base promotion plan"},
    {"id": "phase2", "label": "Build Capa1 questionnaire"},
    {"id": "phase3", "label": "RETEST 0 questionnaire"},
    {"id": "phase4", "label": "RETEST 1 questionnaire"},
    {"id": "phase5", "label": "TICK REAL questionnaire"},
    {"id": "phase6", "label": "MC questionnaire"},
    {"id": "phase7", "label": "MC 2 questionnaire"},
    {"id": "phase8", "label": "Sequential questionnaire"},
    {"id": "phase9", "label": "Monkey Test questionnaire"},
    {"id": "phase10", "label": "Synthetic questionnaire"},
    {"id": "phase11", "label": "SPP configuration review"},
    {"id": "phase12", "label": "WFM configuration review"},
    {"id": "phase13", "label": "FOWARD configuration review"},
    {"id": "phase14", "label": "Capa1 closeout and methodology sync"},
]

SECTION_ALIASES = {
    "automatic retest": "Options",
    "automatic_retest": "Options",
    "atm": "ATMs",
    "atms": "ATMs",
    "blocks": "Blocks",
    "cross checks": "CrossChecks",
    "cross_checks": "CrossChecks",
    "crosschecks": "CrossChecks",
    "custom data": "CustomData",
    "custom_data": "CustomData",
    "customdata": "CustomData",
    "data": "Data",
    "databanks": "Databanks",
    "money management": "RiskMoneyManagement",
    "money_management": "RiskMoneyManagement",
    "notes": "Notes",
    "optimization": "Optimization",
    "options": "Options",
    "parts to improve": "PartsToImprove",
    "parts_to_improve": "PartsToImprove",
    "rankings": "Rankings",
    "resources": "Resources",
    "risk money management": "RiskMoneyManagement",
    "risk_money_management": "RiskMoneyManagement",
    "trading options": "Options",
    "trading_options": "Options",
    "what to build": "WhatToBuild",
    "what_to_build": "WhatToBuild",
    "whattobuild": "WhatToBuild",
}

SKIP_SUBTREES = {
    "BackupStrategyTemplate",
    "FullStrategyXml",
    "Strategy",
    "StrategyXml",
    "XmlStrategy",
}

VIEW_PROMOTION_TARGETS = {
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

DO_NOT_PROMOTE_FIELDS = {
    "project_name",
    "active_flags",
    "symbol",
    "timeframe",
    "asset_specific_spread",
    "session_results",
}

BUILD_GENETIC_TARGET = {
    "PopulationSize": "20",
    "MaxGenerations": "30",
    "CrossoverProbability": "35",
    "MutationProbability": "35",
    "Islands": "7",
    "MigrationModulo": "5",
    "MigrationRate": "5",
    "ShowLastGenerationDatabank": "false",
    "InitGenerationType": "1",
    "DecimationCoef": "1",
    "FreshBloodReplaceSimilar": "true",
    "FreshBloodReplaceWeakest": "false",
    "FreshBloodWeakestPct": "10",
    "FreshBloodWeakestGenerations": "5",
}

BUILD_GENETIC_ATTR_TARGET = {
    "EvoRestartOnFinish": {"status": "true"},
    "EvoRestartOnStagnation": {"status": "true", "fitnessType": "10", "generations": "10"},
    "EvoInSamplePeriod": {"ratio": "50"},
}

BUILD_INITIAL_CONDITIONS_TARGET = [
    {"column": "ProfitFactor", "comparator": ">=", "value": "1", "format": "Decimal2"},
    {"column": "NumberOfTrades", "comparator": ">=", "value": "100", "format": "Decimal2"},
]

BUILD_MODE_LEGACY_NODES = [
    "FilterInitialPopulation",
    "EvoFitnessRestartType",
    "EvoStagnationRestartGenerations",
]

BUILD_RANKING_TARGET = {
    "MaxStrategies": "2000",
    "StopCondition": {"passedStrategies": "500"},
}

BUILD_ORDER_TYPE_TARGET = {
    "EnterAtMarket": "true",
    "EnterReverseAtMarket": "false",
    "EnterAtStop": "false",
    "EnterAtLimit": "false",
}

BUILD_EXIT_TYPE_ACTIVE_KEY = "ExitAfterBars.ExitAfterBars"
BUILD_EXIT_TYPE_BANNED_TOKENS = ("ExitAfterDays", "ExitAfterTradingDays")
BUILD_EXTERNAL_CUSTOM_DATA_TARGET = {"showAll": "false"}


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def json_print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def slug(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    safe = safe.strip("._-")
    return safe[:120] or "item"


def canonical_task_key(value: str) -> str:
    key = re.sub(r"\s+", " ", value.strip().casefold())
    key = key.replace("syntetic", "synthetic")
    key = key.replace("foward", "forward")
    if "build" in key:
        return "build"
    return key


def ledger_root(project_root: Path) -> Path:
    return project_root / LEDGER_DIRNAME


def ensure_ledger(project_root: Path) -> dict[str, str]:
    root = ledger_root(project_root)
    dirs = {
        "root": root,
        "answers": root / "answers" / "capa1",
        "snapshots": root / "snapshots",
        "phase_reports": root / "phase_reports",
        "diffs": root / "diffs",
        "questionnaires": root / "questionnaires" / "capa1",
        "backups": root / "backups",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return {key: str(path) for key, path in dirs.items()}


def write_json(target: Path, payload: dict[str, Any]) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    tmp = target.with_name(f".{target.name}.{os.getpid()}.{time.time_ns()}.tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)
    return target


def safe_zip_text(zf: zipfile.ZipFile, name: str) -> str:
    try:
        return zf.read(name).decode("utf-8")
    except (KeyError, OSError, UnicodeDecodeError, zipfile.BadZipFile):
        return ""


def read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def xml_root_from_zip(zf: zipfile.ZipFile, name: str) -> ET.Element | None:
    try:
        data = zf.read(name)
    except (KeyError, OSError, zipfile.BadZipFile):
        return None
    try:
        return ET.fromstring(data)
    except ET.ParseError:
        return None


def cfx_for_project(root142: Path, project_name: str) -> Path:
    return root142 / "user" / "projects" / project_name / "project.cfx"


def task_title(task: ET.Element) -> str:
    return task.get("title") or task.get("name") or ""


def direct_sections(root: ET.Element | None) -> list[str]:
    if root is None:
        return []
    return [child.tag for child in list(root) if isinstance(child.tag, str)]


def active_cross_checks(root: ET.Element | None) -> list[dict[str, Any]]:
    if root is None:
        return []
    parent = root.find(".//CrossChecks")
    if parent is None:
        return []
    checks: list[dict[str, Any]] = []
    for check in list(parent):
        if check.get("use") != "true":
            continue
        methods = [
            {
                "type": method.get("type", ""),
                "use": method.get("use", ""),
                "settings": {
                    param.get("key", ""): (param.text or "")
                    for param in method.findall(".//Param")
                    if param.get("key")
                },
            }
            for method in check.findall(".//Method")
            if method.get("use") == "true"
        ]
        conditions = [
            dict(condition.attrib)
            for condition in check.findall(".//AcceptanceSettings//Condition")
            if condition.get("use", "true") != "false"
        ]
        checks.append({
            "id": check.tag,
            "use": check.get("use", ""),
            "methods": methods,
            "activeConditionCount": len(conditions),
        })
    return checks


def first_setup_summary(root: ET.Element | None) -> dict[str, Any]:
    if root is None:
        return {}
    setup = root.find(".//Data/Setups/Setup")
    if setup is None:
        return {}
    charts = [dict(chart.attrib) for chart in setup.findall(".//Chart")]
    ranges = [dict(item.attrib) for item in root.findall(".//Data/OutOfSample/Range")]
    return {
        "dateFrom": setup.get("dateFrom", ""),
        "dateTo": setup.get("dateTo", ""),
        "session": setup.get("session", ""),
        "testPrecision": setup.get("testPrecision", ""),
        "charts": charts,
        "outOfSampleRanges": ranges,
    }


def databank_summary(root: ET.Element | None) -> list[dict[str, str]]:
    if root is None:
        return []
    return [dict(item.attrib) for item in root.findall(".//Databanks/Databank")]


def randomize_spread_ranges(root: ET.Element | None) -> list[dict[str, str]]:
    if root is None:
        return []
    ranges: list[dict[str, str]] = []
    for method in root.findall(".//CrossChecks/*/Settings/Methods/Method"):
        if method.get("type") != "RandomizeSpread" or method.get("use") != "true":
            continue
        params = {
            param.get("key", ""): (param.text or "")
            for param in method.findall(".//Param")
            if param.get("key")
        }
        ranges.append({"min": params.get("Min", ""), "max": params.get("Max", "")})
    return ranges


def extract_cfx_snapshot(cfx: Path, label: str, include_hashes: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "label": label,
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": False,
        "sha256": "",
        "config": {},
        "tasks": [],
        "databanks": [],
        "xmlEntries": [],
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload
    payload["isZip"] = True
    payload["sha256"] = file_sha256(cfx)
    with zipfile.ZipFile(cfx) as zf:
        payload["xmlEntries"] = sorted(name for name in zf.namelist() if name.endswith(".xml"))
        if include_hashes:
            hashes: dict[str, str] = {}
            for name in payload["xmlEntries"]:
                hashes[name] = hashlib.sha256(zf.read(name)).hexdigest().upper()
            payload["xmlHashes"] = hashes
        config = xml_root_from_zip(zf, "config.xml")
        if config is None:
            payload["error"] = "config_unreadable"
            return payload
        payload["config"] = {"name": config.get("name", ""), "version": config.get("version", "")}
        payload["databanks"] = [
            {
                "name": databank.get("name", ""),
                "view": databank.get("view", ""),
            }
            for databank in config.findall(".//Databank")
        ]
        for index, task in enumerate(config.findall(".//Task"), start=1):
            file_name = task.get("taskXMLFile", "")
            root = xml_root_from_zip(zf, file_name) if file_name else None
            payload["tasks"].append({
                "position": index,
                "title": task_title(task),
                "name": task.get("name", ""),
                "type": task.get("type", ""),
                "active": task.get("active", ""),
                "taskXml": file_name,
                "sections": direct_sections(root),
                "setup": first_setup_summary(root),
                "databanks": databank_summary(root),
                "activeCrossChecks": active_cross_checks(root),
                "randomizeSpread": randomize_spread_ranges(root),
            })
    return payload


def config_databank_views(cfx: Path) -> dict[str, str]:
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        return {}
    with zipfile.ZipFile(cfx) as zf:
        config = xml_root_from_zip(zf, "config.xml")
        if config is None:
            return {}
        return {
            item.get("name", ""): item.get("view", "")
            for item in config.findall(".//Databank")
            if item.get("name")
        }


def load_task_root(cfx: Path, task_title_wanted: str) -> tuple[str, ET.Element | None]:
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        return "", None
    wanted = task_title_wanted.casefold()
    canonical_wanted = canonical_task_key(task_title_wanted)
    with zipfile.ZipFile(cfx) as zf:
        config = xml_root_from_zip(zf, "config.xml")
        if config is None:
            return "", None
        for task in config.findall(".//Task"):
            title = task_title(task)
            if title.casefold() == wanted or canonical_task_key(title) == canonical_wanted:
                file_name = task.get("taskXMLFile", "")
                return file_name, xml_root_from_zip(zf, file_name)
    return "", None


def find_section(root: ET.Element | None, tab: str) -> ET.Element | None:
    if root is None:
        return None
    key = SECTION_ALIASES.get(tab.strip().casefold(), tab.strip())
    if root.tag == key:
        return root
    direct = root.find(key)
    if direct is not None:
        return direct
    return root.find(f".//{key}")


def node_path(parts: list[str], node: ET.Element) -> str:
    if node.tag == "Param" and node.get("key"):
        return "/".join(parts + [f"Param:{node.get('key')}"])
    if node.tag == "Method" and node.get("type"):
        return "/".join(parts + [f"Method:{node.get('type')}"])
    if node.tag == "Condition" and (node.get("left") or node.get("metric") or node.get("name")):
        ident = node.get("left") or node.get("metric") or node.get("name") or "condition"
        return "/".join(parts + [f"Condition:{ident}"])
    return "/".join(parts + [node.tag])


def value_for_node(node: ET.Element) -> Any:
    value: dict[str, Any] = dict(node.attrib)
    text = (node.text or "").strip()
    if text:
        value["text"] = text
    return value


def collect_section_values(root: ET.Element | None, tab: str, max_values: int) -> dict[str, Any]:
    section = find_section(root, tab)
    if section is None:
        return {"exists": False, "section": SECTION_ALIASES.get(tab.casefold(), tab), "values": []}
    values: list[dict[str, Any]] = []
    limited = max_values > 0
    seen_paths: dict[str, int] = {}

    def unique_xml_path(raw_path: str) -> str:
        seen_paths[raw_path] = seen_paths.get(raw_path, 0) + 1
        return f"{raw_path}#{seen_paths[raw_path]}"

    def walk(node: ET.Element, parts: list[str]) -> None:
        if limited and len(values) >= max_values:
            return
        if node.tag in SKIP_SUBTREES and node is not section:
            return
        interesting = bool(node.attrib) or bool((node.text or "").strip())
        if interesting:
            raw_path = node_path(parts, node)
            values.append({
                "xmlPath": unique_xml_path(raw_path),
                "xmlPathBase": raw_path,
                "tag": node.tag,
                "value": value_for_node(node),
            })
        for child in list(node):
            if not isinstance(child.tag, str):
                continue
            walk(child, parts + [node.tag])

    walk(section, [])
    return {
        "exists": True,
        "section": section.tag,
        "maxValues": max_values if limited else "unlimited",
        "truncated": bool(limited and len(values) >= max_values),
        "values": values,
    }


def normalize_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def build_questionnaire(
    root142: Path,
    project_root: Path,
    task_title_wanted: str,
    tab: str,
    max_values: int,
    write: bool,
) -> dict[str, Any]:
    donor_cfx = cfx_for_project(root142, DEFAULT_DONOR_PROJECT)
    base_cfx = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    donor_file, donor_root = load_task_root(donor_cfx, task_title_wanted)
    base_file, base_root = load_task_root(base_cfx, task_title_wanted)
    donor_values = collect_section_values(donor_root, tab, max_values)
    base_values = collect_section_values(base_root, tab, max_values)
    base_by_path = {item["xmlPath"]: item for item in base_values.get("values", [])}
    donor_by_path = {item["xmlPath"]: item for item in donor_values.get("values", [])}
    all_paths = sorted(set(base_by_path) | set(donor_by_path))
    questions: list[dict[str, Any]] = []
    for path in all_paths:
        base_value = (base_by_path.get(path) or {}).get("value")
        donor_value = (donor_by_path.get(path) or {}).get("value")
        changed = normalize_value(base_value) != normalize_value(donor_value)
        qid = slug(f"{task_title_wanted}-{tab}-{path}")
        questions.append({
            "id": qid,
            "taskTitle": task_title_wanted,
            "tab": tab,
            "xmlPath": path,
            "baseValue": base_value,
            "donorValue": donor_value,
            "changed": changed,
            "recommendation": "ask_operator" if changed else "keep_base",
            "options": [
                {"id": "keep_base", "label": "Mantener base", "value": base_value},
                {"id": "copy_donor_if_methodological", "label": "Usar valor donor si es metodologico", "value": donor_value},
                {"id": "custom_value", "label": "Valor manual", "value": None},
            ],
            "status": "pending",
        })
    payload = {
        "ok": bool(donor_root is not None or base_root is not None),
        "version": VERSION,
        "createdAt": now_iso(),
        "scope": "capa1",
        "taskTitle": task_title_wanted,
        "tab": tab,
        "donorTaskXml": donor_file,
        "baseTaskXml": base_file,
        "baseSection": base_values,
        "donorSection": donor_values,
        "questionCount": len(questions),
        "changedQuestionCount": sum(1 for item in questions if item["changed"]),
        "questions": questions,
        "discipline": [
            "Ask one task/tab at a time.",
            "Record each answer immediately with record-answer.",
            "Do not apply base changes until the phase is closed.",
        ],
    }
    if write:
        ensure_ledger(project_root)
        target = (
            ledger_root(project_root)
            / "questionnaires"
            / "capa1"
            / slug(task_title_wanted)
            / f"{slug(tab)}_{stamp()}.json"
        )
        write_json(target, payload)
        payload["written"] = str(target)
    return payload


def build_task_questionnaires(
    root142: Path,
    project_root: Path,
    task_title_wanted: str,
    max_values: int,
    write: bool,
) -> dict[str, Any]:
    donor_cfx = cfx_for_project(root142, DEFAULT_DONOR_PROJECT)
    base_cfx = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    donor_file, donor_root = load_task_root(donor_cfx, task_title_wanted)
    base_file, base_root = load_task_root(base_cfx, task_title_wanted)
    tabs = sorted(set(direct_sections(donor_root)) | set(direct_sections(base_root)))
    results = []
    for tab in tabs:
        questionnaire = build_questionnaire(
            root142,
            project_root,
            task_title_wanted=task_title_wanted,
            tab=tab,
            max_values=max_values,
            write=write,
        )
        results.append({
            "tab": tab,
            "ok": questionnaire.get("ok", False),
            "questionCount": questionnaire.get("questionCount", 0),
            "changedQuestionCount": questionnaire.get("changedQuestionCount", 0),
            "baseValueCount": len(((questionnaire.get("baseSection") or {}).get("values") or [])),
            "donorValueCount": len(((questionnaire.get("donorSection") or {}).get("values") or [])),
            "baseTruncated": (questionnaire.get("baseSection") or {}).get("truncated", False),
            "donorTruncated": (questionnaire.get("donorSection") or {}).get("truncated", False),
            "written": questionnaire.get("written", ""),
        })
    payload = {
        "ok": bool(donor_root is not None or base_root is not None),
        "version": VERSION,
        "createdAt": now_iso(),
        "scope": "capa1",
        "taskTitle": task_title_wanted,
        "donorTaskXml": donor_file,
        "baseTaskXml": base_file,
        "tabCount": len(tabs),
        "tabs": results,
        "totalQuestionCount": sum(int(item.get("questionCount") or 0) for item in results),
        "totalChangedQuestionCount": sum(int(item.get("changedQuestionCount") or 0) for item in results),
        "write": write,
        "maxValues": max_values if max_values > 0 else "unlimited",
    }
    if write:
        target = (
            ledger_root(project_root)
            / "questionnaires"
            / "capa1"
            / slug(task_title_wanted)
            / f"_task_summary_{stamp()}.json"
        )
        write_json(target, payload)
        payload["written"] = str(target)
    return payload


def compact_questionnaire_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": payload.get("ok", False),
        "version": payload.get("version", VERSION),
        "createdAt": payload.get("createdAt", ""),
        "scope": payload.get("scope", "capa1"),
        "taskTitle": payload.get("taskTitle", ""),
        "tab": payload.get("tab", ""),
        "donorTaskXml": payload.get("donorTaskXml", ""),
        "baseTaskXml": payload.get("baseTaskXml", ""),
        "questionCount": payload.get("questionCount", 0),
        "changedQuestionCount": payload.get("changedQuestionCount", 0),
        "baseValueCount": len(((payload.get("baseSection") or {}).get("values") or [])),
        "donorValueCount": len(((payload.get("donorSection") or {}).get("values") or [])),
        "baseTruncated": (payload.get("baseSection") or {}).get("truncated", False),
        "donorTruncated": (payload.get("donorSection") or {}).get("truncated", False),
        "written": payload.get("written", ""),
        "output": "summary_only_use_--full-output_to_print_all_questions",
    }


def backup_file(source: Path, backup_root: Path) -> Path:
    backup_root.mkdir(parents=True, exist_ok=True)
    target = backup_root / source.name
    counter = 2
    while target.exists():
        target = backup_root / f"{source.stem}.{counter}{source.suffix}"
        counter += 1
    shutil.copy2(source, target)
    return target


def replace_config_xml_in_cfx(cfx: Path, new_config_text: str) -> None:
    tmp = cfx.with_suffix(cfx.suffix + f".{os.getpid()}.{time.time_ns()}.tmp")
    with zipfile.ZipFile(cfx, "r") as source:
        with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as target:
            for item in source.infolist():
                data = new_config_text.encode("utf-8") if item.filename == "config.xml" else source.read(item.filename)
                target.writestr(item, data)
    tmp.replace(cfx)


def replace_zip_text_entry(cfx: Path, entry_name: str, new_text: str) -> None:
    tmp = cfx.with_suffix(cfx.suffix + f".{os.getpid()}.{time.time_ns()}.tmp")
    with zipfile.ZipFile(cfx, "r") as source:
        with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as target:
            for item in source.infolist():
                data = new_text.encode("utf-8") if item.filename == entry_name else source.read(item.filename)
                target.writestr(item, data)
    tmp.replace(cfx)


def find_build_mode(root: ET.Element | None) -> ET.Element | None:
    if root is None:
        return None
    what_to_build = find_section(root, "WhatToBuild")
    if what_to_build is not None:
        build_mode = what_to_build.find("BuildMode")
        if build_mode is not None:
            return build_mode
    return root.find(".//BuildMode")


def set_text_child(parent: ET.Element, tag: str, value: str, actions: list[dict[str, Any]]) -> None:
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag)
        before = None
    else:
        before = (child.text or "").strip()
    if before != value:
        child.text = value
    actions.append({
        "field": tag,
        "from": before,
        "to": value,
        "changed": before != value,
    })


def set_attr_child(parent: ET.Element, tag: str, attrs: dict[str, str], actions: list[dict[str, Any]]) -> None:
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag)
        before = {}
    else:
        before = dict(child.attrib)
    for key, value in attrs.items():
        child.set(key, value)
    after = dict(child.attrib)
    actions.append({
        "field": tag,
        "from": before,
        "to": after,
        "changed": before != after,
    })


def make_column_condition(column: str, comparator: str, value: str, fmt: str) -> ET.Element:
    condition = ET.Element("Condition", {"use": "true"})
    condition.text = "\n          "
    left = ET.SubElement(condition, "Left-Side", {"valueType": "column"})
    left.text = "\n            "
    left.tail = "\n          "
    column_value = ET.SubElement(left, "Column-Value", {
        "column": column,
        "columnType": "0",
        "format": fmt,
        "resultType": "main",
        "direction": "0",
        "sampleType": "127",
        "plType": "10",
        "confidenceLevel": "50",
        "market": "1",
        "subresult": "30",
        "pctRatio": "0",
        "class": column,
    })
    column_value.tail = "\n          "
    comp = ET.SubElement(condition, "Comparator", {"value": comparator})
    comp.tail = "\n          "
    right = ET.SubElement(condition, "Right-Side", {"valueType": "numeric"})
    right.text = "\n            "
    right.tail = "\n        "
    numeric = ET.SubElement(right, "Numeric-Value", {"value": value})
    numeric.tail = "\n          "
    return condition


def summarize_conditions(parent: ET.Element | None) -> list[dict[str, str]]:
    if parent is None:
        return []
    items: list[dict[str, str]] = []
    for condition in parent.findall("Condition"):
        column_value = condition.find(".//Column-Value")
        comparator = condition.find("Comparator")
        numeric = condition.find(".//Numeric-Value")
        items.append({
            "column": column_value.get("column", "") if column_value is not None else "",
            "comparator": comparator.get("value", "") if comparator is not None else "",
            "value": numeric.get("value", "") if numeric is not None else "",
            "use": condition.get("use", ""),
        })
    return items


def set_initial_population_conditions(build_mode: ET.Element, actions: list[dict[str, Any]]) -> None:
    conditions = build_mode.find("Conditions")
    if conditions is None:
        conditions = ET.SubElement(build_mode, "Conditions")
        before: list[dict[str, str]] = []
    else:
        before = summarize_conditions(conditions)
        for child in list(conditions):
            conditions.remove(child)
    conditions.text = "\n        "
    for index, target in enumerate(BUILD_INITIAL_CONDITIONS_TARGET):
        condition = make_column_condition(
            column=target["column"],
            comparator=target["comparator"],
            value=target["value"],
            fmt=target["format"],
        )
        condition.tail = "\n      " if index == len(BUILD_INITIAL_CONDITIONS_TARGET) - 1 else "\n        "
        conditions.append(condition)
    after = summarize_conditions(conditions)
    actions.append({
        "field": "InitialPopulationConditions",
        "from": before,
        "to": after,
        "changed": before != after,
    })


def remove_children_by_tag(parent: ET.Element, tags: list[str], actions: list[dict[str, Any]]) -> None:
    for tag in tags:
        removed = []
        for child in list(parent.findall(tag)):
            removed.append(value_for_node(child))
            parent.remove(child)
        actions.append({
            "field": f"RemoveLegacy:{tag}",
            "from": removed,
            "to": [],
            "changed": bool(removed),
        })


def serialize_xml(root: ET.Element) -> str:
    return ET.tostring(root, encoding="unicode", short_empty_elements=True)


def update_build_genetic_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, "Build")
    payload["taskXml"] = task_xml_name
    build_mode = find_build_mode(root)
    if not task_xml_name or root is None or build_mode is None:
        payload["error"] = "build_task_or_build_mode_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    for tag, value in BUILD_GENETIC_TARGET.items():
        set_text_child(build_mode, tag, value, payload["actions"])
    for tag, attrs in BUILD_GENETIC_ATTR_TARGET.items():
        set_attr_child(build_mode, tag, attrs, payload["actions"])
    set_initial_population_conditions(build_mode, payload["actions"])
    remove_children_by_tag(build_mode, BUILD_MODE_LEGACY_NODES, payload["actions"])

    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetRationale"] = {
        "marketSides": "left untouched; generator remains responsible for side selection",
        "trainingValidation": "Build is IS edge mining; external Capa1/Capa2 retests are the validation layers",
        "fitnessType": "10 = In sample (whole)",
        "legacyCleanup": "SQX 142/143 SettingsGeneticOptionsService reads/writes EvoRestartOnStagnation attributes and Conditions, not legacy sibling nodes.",
    }
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_build_genetic_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase2_build_genetic_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_build_genetic_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(item.get("exists") and item.get("isZip") and not item.get("error") for item in results.values()),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_genetic_target",
        "apply": apply,
        "target": target,
        "results": results,
        "targetValues": {
            "text": BUILD_GENETIC_TARGET,
            "attributes": BUILD_GENETIC_ATTR_TARGET,
            "initialConditions": BUILD_INITIAL_CONDITIONS_TARGET,
        },
        "nextPhase": "phase2_build_diff_review" if not apply else "phase2_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_genetic_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def find_rankings(root: ET.Element | None) -> ET.Element | None:
    return find_section(root, "Rankings") if root is not None else None


def update_build_ranking_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, "Build")
    payload["taskXml"] = task_xml_name
    rankings = find_rankings(root)
    if not task_xml_name or root is None or rankings is None:
        payload["error"] = "build_task_or_rankings_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    set_text_child(rankings, "MaxStrategies", BUILD_RANKING_TARGET["MaxStrategies"], payload["actions"])
    stop_condition = rankings.find("StopCondition")
    if stop_condition is None:
        stop_condition = ET.SubElement(rankings, "StopCondition")
        before = {}
    else:
        before = dict(stop_condition.attrib)
    for key, value in BUILD_RANKING_TARGET["StopCondition"].items():
        stop_condition.set(key, value)
    after = dict(stop_condition.attrib)
    payload["actions"].append({
        "field": "StopCondition",
        "from": before,
        "to": after,
        "changed": before != after,
    })

    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetRationale"] = {
        "methodology": "operator accepted the recommendation 2000/500",
        "quality": "keeps ranking logic intact while reducing selection-by-luck surface",
        "scope": "only MaxStrategies and StopCondition.passedStrategies are changed",
    }
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_build_ranking_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase2_build_ranking_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_build_ranking_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(item.get("exists") and item.get("isZip") and not item.get("error") for item in results.values()),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_ranking_target",
        "apply": apply,
        "target": target,
        "results": results,
        "targetValues": BUILD_RANKING_TARGET,
        "nextPhase": "phase2_build_ranking_diff_review" if not apply else "phase2_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_ranking_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def find_blocks(root: ET.Element | None) -> ET.Element | None:
    return find_section(root, "Blocks") if root is not None else None


def block_key_action(block: ET.Element) -> dict[str, Any]:
    return {
        "key": block.get("key", ""),
        "use": block.get("use", ""),
        "probability": block.get("probability", ""),
        "category": block.get("category", ""),
    }


def enforce_order_types(blocks: ET.Element, actions: list[dict[str, Any]]) -> None:
    order_types = blocks.find("OrderTypes")
    if order_types is None:
        actions.append({"field": "OrderTypes", "error": "missing", "changed": False})
        return
    for block in order_types.findall("Block"):
        key = block.get("key", "")
        if key not in BUILD_ORDER_TYPE_TARGET:
            continue
        before = block.get("use", "")
        wanted = BUILD_ORDER_TYPE_TARGET[key]
        block.set("use", wanted)
        actions.append({
            "field": f"OrderTypes:{key}",
            "from": before,
            "to": wanted,
            "changed": before != wanted,
        })


def enforce_exit_types(blocks: ET.Element, actions: list[dict[str, Any]]) -> None:
    exit_types = blocks.find("ExitTypes")
    if exit_types is None:
        actions.append({"field": "ExitTypes", "error": "missing", "changed": False})
        return
    removed = []
    for block in list(exit_types.findall("Block")):
        key = block.get("key", "")
        if any(token in key for token in BUILD_EXIT_TYPE_BANNED_TOKENS):
            removed.append(block_key_action(block))
            exit_types.remove(block)
            continue
        before = block.get("use", "")
        wanted = "true" if key == BUILD_EXIT_TYPE_ACTIVE_KEY else "false"
        block.set("use", wanted)
        if key == BUILD_EXIT_TYPE_ACTIVE_KEY:
            block.set("probability", "100")
            for value in block.findall("Value"):
                if value.get("key") == "undefined":
                    value.set("use", "true")
        actions.append({
            "field": f"ExitTypes:{key}",
            "from": before,
            "to": wanted,
            "changed": before != wanted,
        })
    actions.append({
        "field": "ExitTypes:removeDayBasedExits",
        "from": removed,
        "to": [],
        "changed": bool(removed),
    })


def enforce_external_custom_data(blocks: ET.Element, actions: list[dict[str, Any]]) -> None:
    custom_data = blocks.find("CustomData")
    if custom_data is None:
        custom_data = ET.SubElement(blocks, "CustomData")
        before = {}
    else:
        before = dict(custom_data.attrib)
    for key, value in BUILD_EXTERNAL_CUSTOM_DATA_TARGET.items():
        custom_data.set(key, value)
    removed_children = [child.tag for child in list(custom_data)]
    for child in list(custom_data):
        custom_data.remove(child)
    after = dict(custom_data.attrib)
    actions.append({
        "field": "CustomData",
        "from": {"attributes": before, "children": removed_children},
        "to": {"attributes": after, "children": []},
        "changed": before != after or bool(removed_children),
    })


def update_build_blocks_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, "Build")
    payload["taskXml"] = task_xml_name
    blocks = find_blocks(root)
    if not task_xml_name or root is None or blocks is None:
        payload["error"] = "build_task_or_blocks_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    enforce_order_types(blocks, payload["actions"])
    enforce_exit_types(blocks, payload["actions"])
    enforce_external_custom_data(blocks, payload["actions"])

    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetRationale"] = {
        "dynamicLeftSide": "Signals/Indicators/Stop-Limit entry blocks remain methodology/generator owned.",
        "fixedBlueSide": "Only EnterAtMarket and ExitAfterBars are allowed in Capa1 base; external custom data stays empty.",
        "exitDays": "Day-based exits are removed from the CFX so they cannot be selected by the Builder.",
    }
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_build_blocks_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase2_build_blocks_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_build_blocks_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(item.get("exists") and item.get("isZip") and not item.get("error") for item in results.values()),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_blocks_target",
        "apply": apply,
        "target": target,
        "results": results,
        "targetValues": {
            "orderTypes": BUILD_ORDER_TYPE_TARGET,
            "activeExitType": BUILD_EXIT_TYPE_ACTIVE_KEY,
            "bannedExitTokens": list(BUILD_EXIT_TYPE_BANNED_TOKENS),
            "customData": BUILD_EXTERNAL_CUSTOM_DATA_TARGET,
        },
        "nextPhase": "phase2_build_blocks_diff_review" if not apply else "phase2_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_blocks_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def exit_day_snippet_candidates(root142: Path) -> list[Path]:
    extend_root = root142 / "user" / "extend"
    if not extend_root.is_dir():
        return []
    tokens = ("ExitAfterDays", "ExitAfterTradingDays")
    suffixes = {".java", ".tpl"}
    return sorted(
        path
        for path in extend_root.rglob("*")
        if path.is_file()
        and path.suffix in suffixes
        and any(token in path.name for token in tokens)
    )


def archive_exit_day_snippets(root142: Path, project_root: Path, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    extend_root = (root142 / "user" / "extend").resolve()
    archive_root = ledger_root(project_root) / "backups" / f"exit_day_snippets_{stamp()}"
    candidates = exit_day_snippet_candidates(root142)
    actions = []
    for source in candidates:
        resolved = source.resolve()
        if not str(resolved).casefold().startswith(str(extend_root).casefold()):
            actions.append({"source": str(source), "error": "outside_user_extend", "willMove": False})
            continue
        relative = resolved.relative_to(extend_root)
        target = archive_root / relative
        actions.append({
            "source": str(resolved),
            "target": str(target),
            "willMove": apply,
        })
        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(resolved), str(target))
    payload = {
        "ok": all(not item.get("error") for item in actions),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "archive_exit_day_snippets",
        "apply": apply,
        "sqxRoot": str(root142),
        "archiveRoot": str(archive_root) if apply else "",
        "candidateCount": len(candidates),
        "actions": actions,
        "rationale": "Capa1 methodology allows ExitAfterBars only; user-level day-based exit snippets are archived reversibly.",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_exit_day_snippet_archive_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def update_databank_views_in_cfx(cfx: Path, target_views: dict[str, str], backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload
    with zipfile.ZipFile(cfx, "r") as zf:
        config_text = safe_zip_text(zf, "config.xml")
    if not config_text:
        payload["error"] = "config_unreadable"
        return payload
    updated = config_text
    current_views = config_databank_views(cfx)
    for databank, wanted_view in sorted(target_views.items()):
        current = current_views.get(databank, "")
        if current == wanted_view:
            continue
        pattern = rf'(<Databank\b(?=[^>]*\bname="{re.escape(databank)}")[^>]*\bview=")[^"]*(")'
        updated_candidate, count = re.subn(pattern, rf"\1{wanted_view}\2", updated, count=1)
        payload["actions"].append({
            "databank": databank,
            "from": current,
            "to": wanted_view,
            "matched": count == 1,
            "willWrite": bool(apply and count == 1),
        })
        updated = updated_candidate
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("matched"))
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_config_xml_in_cfx(cfx, updated)
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_view_assignments(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    donor_cfx = cfx_for_project(root142, DEFAULT_DONOR_PROJECT)
    donor_views = config_databank_views(donor_cfx)
    target_views = {
        databank: expected
        for databank, expected in VIEW_PROMOTION_TARGETS.items()
        if donor_views.get(databank) == expected
    }
    backup_root = ledger_root(project_root) / "backups" / f"phase1_views_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_databank_views_in_cfx(path, target_views, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(item.get("exists") and item.get("isZip") and not item.get("error") for item in results.values()),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase1",
        "apply": apply,
        "target": target,
        "donorProject": DEFAULT_DONOR_PROJECT,
        "targetViews": target_views,
        "results": results,
        "promotionRule": "Only allowlisted view assignments that already match the donor are promoted.",
        "nextPhase": "phase2",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase1_view_promotion_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def task_by_title(snapshot: dict[str, Any], title: str) -> dict[str, Any]:
    wanted = title.casefold()
    canonical_wanted = canonical_task_key(title)
    for item in snapshot.get("tasks", []):
        candidate = str(item.get("title", ""))
        if candidate.casefold() == wanted or canonical_task_key(candidate) == canonical_wanted:
            return item
    return {}


def semantic_diff(donor: dict[str, Any], base: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    base_databank_views = {item.get("name", ""): item.get("view", "") for item in base.get("databanks", [])}
    donor_databank_views = {item.get("name", ""): item.get("view", "") for item in donor.get("databanks", [])}
    view_candidates = []
    for name, expected in VIEW_PROMOTION_TARGETS.items():
        donor_view = donor_databank_views.get(name, "")
        base_view = base_databank_views.get(name, "")
        if donor_view == expected and base_view != expected:
            view_candidates.append({
                "databank": name,
                "baseView": base_view,
                "donorView": donor_view,
                "recommended": "promote_view_assignment",
            })

    task_diffs = []
    for donor_task in donor.get("tasks", []):
        title = donor_task.get("title", "")
        base_task = task_by_title(base, title)
        if not base_task:
            # Known base title placeholder for Build is expected.
            if str(donor_task.get("type")) == "Build":
                base_task = next((item for item in base.get("tasks", []) if item.get("type") == "Build"), {})
        if not base_task:
            task_diffs.append({"title": title, "issue": "missing_in_base", "recommendation": "manual_review"})
            continue
        setup_diff = {}
        for key in ("dateFrom", "dateTo", "session", "testPrecision"):
            donor_value = (donor_task.get("setup") or {}).get(key, "")
            base_value = (base_task.get("setup") or {}).get(key, "")
            if donor_value != base_value:
                setup_diff[key] = {"base": base_value, "donor": donor_value}
        donor_checks = [item.get("id") for item in donor_task.get("activeCrossChecks", [])]
        base_checks = [item.get("id") for item in base_task.get("activeCrossChecks", [])]
        if setup_diff or donor_checks != base_checks or donor_task.get("randomizeSpread") != base_task.get("randomizeSpread"):
            task_diffs.append({
                "title": title,
                "taskXml": donor_task.get("taskXml", ""),
                "setupDiff": setup_diff,
                "activeCrossChecks": {"base": base_checks, "donor": donor_checks},
                "randomizeSpread": {
                    "base": base_task.get("randomizeSpread"),
                    "donor": donor_task.get("randomizeSpread"),
                },
                "recommendation": "questionnaire_before_promotion",
            })

    return {
        "version": VERSION,
        "createdAt": now_iso(),
        "source": {
            "donor": donor.get("label"),
            "base": base.get("label"),
            "template": template.get("label"),
        },
        "promotionMode": "selective_normalized",
        "candidatePromotions": {
            "viewAssignments": view_candidates,
            "mc2AdaptiveSpread": [
                item for item in task_diffs
                if str(item.get("title", "")).casefold() == "mc 2"
                and (item.get("randomizeSpread") or {}).get("donor")
            ],
        },
        "requiresQuestionnaire": task_diffs,
        "doNotPromoteDirectly": sorted(DO_NOT_PROMOTE_FIELDS),
        "templateSha256": template.get("sha256", ""),
        "baseSha256": base.get("sha256", ""),
        "donorSha256": donor.get("sha256", ""),
        "nextPhase": "phase1" if view_candidates else "phase2",
    }


def process_snapshot() -> dict[str, Any]:
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-Process | Where-Object { $_.ProcessName -like 'StrategyQuantX*' -or $_.ProcessName -like 'java*' } | Select-Object ProcessName,Id | ConvertTo-Json -Compress",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=8, check=False)
    except (OSError, subprocess.SubprocessError):
        return {"ok": False, "processes": [], "error": "process_probe_failed"}
    raw = (proc.stdout or "").strip()
    if not raw:
        return {"ok": True, "processes": []}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"ok": False, "processes": [], "raw": raw}
    if isinstance(parsed, dict):
        parsed = [parsed]
    return {"ok": True, "processes": parsed}


def preflight(root142: Path, project_root: Path, apply: bool) -> dict[str, Any]:
    dirs = ensure_ledger(project_root) if apply else {key: str(ledger_root(project_root) / key) for key in ("root",)}
    donor_cfx = cfx_for_project(root142, DEFAULT_DONOR_PROJECT)
    base_cfx = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    template_cfx = DEFAULT_TEMPLATE
    paths = {
        "sqxRoot": str(root142),
        "donorProject": str(donor_cfx),
        "baseProject": str(base_cfx),
        "repoTemplate": str(template_cfx),
    }
    donor = extract_cfx_snapshot(donor_cfx, DEFAULT_DONOR_PROJECT, include_hashes=True)
    base = extract_cfx_snapshot(base_cfx, DEFAULT_BASE_PROJECT, include_hashes=True)
    template = extract_cfx_snapshot(template_cfx, "backend template Capa1_Long.cfx", include_hashes=True)
    diff = semantic_diff(donor, base, template)
    payload = {
        "ok": all(item.get("exists") and item.get("isZip") for item in (donor, base, template)),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase0",
        "apply": apply,
        "paths": paths,
        "ledger": dirs,
        "processProbe": process_snapshot(),
        "snapshots": {
            "donor": donor,
            "base": base,
            "template": template,
        },
        "semanticDiff": diff,
        "discipline": {
            "sourceOfTruth": DEFAULT_DONOR_PROJECT,
            "promotion": "selective_normalized",
            "answers": "write full local ledger and sanitized docs summary",
            "noDirectPromotion": sorted(DO_NOT_PROMOTE_FIELDS),
        },
    }
    if apply:
        root = ledger_root(project_root)
        donor_path = root / "snapshots" / f"donor_{stamp()}.json"
        base_path = root / "snapshots" / f"base_{stamp()}.json"
        template_path = root / "snapshots" / f"template_{stamp()}.json"
        diff_path = root / "diffs" / f"semantic_diff_{stamp()}.json"
        write_json(donor_path, donor)
        write_json(base_path, base)
        write_json(template_path, template)
        write_json(diff_path, diff)
        next_phase = str(diff.get("nextPhase", "phase1"))
        state = {
            "version": VERSION,
            "updatedAt": now_iso(),
            "currentPhase": "phase1" if next_phase == "phase2" else "phase0",
            "nextPhase": next_phase,
            "scope": "capa1",
            "donorProject": DEFAULT_DONOR_PROJECT,
            "baseProject": DEFAULT_BASE_PROJECT,
            "repoTemplate": str(DEFAULT_TEMPLATE),
            "ledgerPolicy": ".local full answers plus sanitized docs summary",
            "lastPreflight": {
                "donorSnapshot": str(donor_path),
                "baseSnapshot": str(base_path),
                "templateSnapshot": str(template_path),
                "semanticDiff": str(diff_path),
            },
        }
        state_path = root / "session_state.json"
        write_json(state_path, state)
        payload["written"] = {
            "sessionState": str(state_path),
            "donorSnapshot": str(donor_path),
            "baseSnapshot": str(base_path),
            "templateSnapshot": str(template_path),
            "semanticDiff": str(diff_path),
        }
    return payload


def status(project_root: Path) -> dict[str, Any]:
    root = ledger_root(project_root)
    state = read_json(root / "session_state.json", {})
    return {
        "ok": root.is_dir(),
        "version": VERSION,
        "createdAt": now_iso(),
        "ledgerRoot": str(root),
        "sessionState": state,
        "phaseReports": len(list((root / "phase_reports").glob("*.json"))) if (root / "phase_reports").is_dir() else 0,
        "questionnaires": len(list((root / "questionnaires").rglob("*.json"))) if (root / "questionnaires").is_dir() else 0,
        "answerFiles": len(list((root / "answers").rglob("*.json"))) if (root / "answers").is_dir() else 0,
        "processProbe": process_snapshot(),
    }


def record_answer(project_root: Path, task_title_wanted: str, tab: str, question_id: str, answer: str, note: str) -> dict[str, Any]:
    ensure_ledger(project_root)
    target = ledger_root(project_root) / "answers" / "capa1" / slug(task_title_wanted) / f"{slug(tab)}.json"
    payload = read_json(target, {
        "version": VERSION,
        "scope": "capa1",
        "taskTitle": task_title_wanted,
        "tab": tab,
        "answers": {},
        "createdAt": now_iso(),
    })
    payload["updatedAt"] = now_iso()
    payload.setdefault("answers", {})[question_id] = {
        "answer": answer,
        "note": note,
        "answeredAt": now_iso(),
    }
    write_json(target, payload)
    return {"ok": True, "version": VERSION, "written": str(target), "questionId": question_id}


def phase_report(project_root: Path, phase_id: str, summary: str, next_phase: str, write: bool) -> dict[str, Any]:
    root = ledger_root(project_root)
    payload = {
        "ok": True,
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": phase_id,
        "summary": summary,
        "nextPhase": next_phase,
        "answerFiles": [
            str(path)
            for path in sorted((root / "answers" / "capa1").rglob("*.json"))
        ] if (root / "answers" / "capa1").is_dir() else [],
    }
    if write:
        ensure_ledger(project_root)
        target = root / "phase_reports" / f"{phase_id}_{stamp()}.json"
        write_json(target, payload)
        state_path = root / "session_state.json"
        state = read_json(state_path, {})
        state.update({"updatedAt": now_iso(), "currentPhase": phase_id, "nextPhase": next_phase})
        write_json(state_path, state)
        payload["written"] = str(target)
    return payload


def list_phases() -> dict[str, Any]:
    return {"ok": True, "version": VERSION, "phases": PHASES}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sqx142-task-config-gate")
    parser.add_argument("--sqx-root", type=Path, default=DEFAULT_SQX_ROOT)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status")
    pre = sub.add_parser("preflight")
    pre.add_argument("--apply", action="store_true")
    sub.add_parser("phases")

    promote_views = sub.add_parser("promote-views")
    promote_views.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_views.add_argument("--apply", action="store_true")

    promote_genetic = sub.add_parser("build-genetic-target")
    promote_genetic.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_genetic.add_argument("--apply", action="store_true")

    promote_ranking = sub.add_parser("build-ranking-target")
    promote_ranking.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_ranking.add_argument("--apply", action="store_true")

    promote_blocks = sub.add_parser("build-blocks-target")
    promote_blocks.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_blocks.add_argument("--apply", action="store_true")

    archive_exit_days = sub.add_parser("archive-exit-day-snippets")
    archive_exit_days.add_argument("--apply", action="store_true")

    questionnaire = sub.add_parser("questionnaire")
    questionnaire.add_argument("--task-title", required=True)
    questionnaire.add_argument("--tab", required=True)
    questionnaire.add_argument("--max-values", type=int, default=0)
    questionnaire.add_argument("--write", action="store_true")
    questionnaire.add_argument("--full-output", action="store_true")

    task_questionnaires = sub.add_parser("task-questionnaires")
    task_questionnaires.add_argument("--task-title", required=True)
    task_questionnaires.add_argument("--max-values", type=int, default=0)
    task_questionnaires.add_argument("--write", action="store_true")

    answer = sub.add_parser("record-answer")
    answer.add_argument("--task-title", required=True)
    answer.add_argument("--tab", required=True)
    answer.add_argument("--question-id", required=True)
    answer.add_argument("--answer", required=True)
    answer.add_argument("--note", default="")

    report = sub.add_parser("phase-report")
    report.add_argument("--phase", required=True)
    report.add_argument("--summary", required=True)
    report.add_argument("--next-phase", required=True)
    report.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_root = args.project_root.resolve()
    root142 = args.sqx_root
    if args.command == "status":
        json_print(status(project_root))
        return 0
    if args.command == "preflight":
        json_print(preflight(root142, project_root, apply=args.apply))
        return 0
    if args.command == "phases":
        json_print(list_phases())
        return 0
    if args.command == "promote-views":
        json_print(promote_view_assignments(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "build-genetic-target":
        json_print(promote_build_genetic_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "build-ranking-target":
        json_print(promote_build_ranking_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "build-blocks-target":
        json_print(promote_build_blocks_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "archive-exit-day-snippets":
        json_print(archive_exit_day_snippets(root142, project_root, apply=args.apply))
        return 0
    if args.command == "questionnaire":
        payload = build_questionnaire(
            root142,
            project_root,
            task_title_wanted=args.task_title,
            tab=args.tab,
            max_values=args.max_values,
            write=args.write,
        )
        if args.write and not args.full_output:
            payload = compact_questionnaire_payload(payload)
        json_print(payload)
        return 0
    if args.command == "task-questionnaires":
        json_print(build_task_questionnaires(
            root142,
            project_root,
            task_title_wanted=args.task_title,
            max_values=args.max_values,
            write=args.write,
        ))
        return 0
    if args.command == "record-answer":
        json_print(record_answer(
            project_root,
            task_title_wanted=args.task_title,
            tab=args.tab,
            question_id=args.question_id,
            answer=args.answer,
            note=args.note,
        ))
        return 0
    if args.command == "phase-report":
        json_print(phase_report(
            project_root,
            phase_id=args.phase,
            summary=args.summary,
            next_phase=args.next_phase,
            write=args.write,
        ))
        return 0
    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
