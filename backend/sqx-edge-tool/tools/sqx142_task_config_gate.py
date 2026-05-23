from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_SQX_ROOT = Path(r"C:\BOTS\Versiones\SQX_142_Crack")
DEFAULT_DONOR_PROJECT = "Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1"
DEFAULT_BASE_PROJECT = "Capa1_Long_SQX142_Base"
DEFAULT_TEMPLATE = TOOL_ROOT / "templates" / "Capa1_Long.cfx"
BLOCKSETTINGS_MANIFEST_PATH = TOOL_ROOT / "config" / "blocksettings_manifest.json"
BLOCKSETTINGS_RESOURCE_DIR = TOOL_ROOT / "resources" / "blocksettings"
GENERATOR_PROFILES_PATH = TOOL_ROOT / "config" / "generator_profiles.json"
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
BUILD_BLOCK_CATEGORY_DISABLE_TARGET = ("signals", "stopLimitBlocks")
BUILD_BLOCK_CATEGORY_PRESERVE_TARGET = ("indicators",)
BUILD_INDICATORS_DEFAULT_BLOCKSETTING = "BS_Volatilidad"
BUILD_INDICATORS_DEFAULT_TIMEFRAME = "H4"
BUILD_DATA_PERIOD_KEY = "BUILD_C1"
BUILD_DATA_TEST_PRECISION = "2"
BUILD_DATA_SESSION = "No Session"
BUILD_RESOURCES_PRECISION = "TICK"
BUILD_RESOURCES_BASE_DATA_TYPE = "3"
BUILD_RESOURCES_BANNED_DONOR_TOKENS = ("USDJPY", "USDJPY_darwinex", "USDJPY_dukascopy")
BUILD_ACTIVE_CROSSCHECK = "SequentialOptimization"
BUILD_CROSSCHECK_PARENT_TARGET = {"use": "true", "evaluateAll": "true"}
BUILD_CROSSCHECK_BANNED_DONOR_TOKENS = ("USDJPY", "USDJPY_darwinex", "USDJPY_dukascopy")
BUILD_STATIC_TABS = (
    "Options",
    "ATMs",
    "PartsToImprove",
    "RiskMoneyManagement",
    "Databanks",
    "Notes",
    "Optimization",
)
BUILD_STATIC_TAB_HASHES = {
    "Options": "BF732DD7B130086DC0EA2E16669A270AC42A5910763B72B9DA001BCE4F22038C",
    "ATMs": "5B18484BDCBB462F169B894A8861C05F7DA323B05EE808FA49BB300442E56C40",
    "PartsToImprove": "14258C2F5FBFB077CE7FC4009F1D89FB32BD7FD2EBD66EAFF5F1ECB33411AC87",
    "RiskMoneyManagement": "CFBC9E6C4D1C30782BAC103AED72CFAF66AAA71BF4B892A4CEDDBA1E6317B76F",
    "Databanks": "31F633435ACD49E3837422C376421A28723FBE7017B4EEBD9EA2F20C29B7BB98",
    "Notes": "7E0C7BB76E5A63E6CD5B9B97F2571F549C95DF5F79CD0C315895ADAF2742E880",
    "Optimization": "63655CE465154201278796A666D9FC0A21B36EAF825B356797927DBC8402E3A8",
}

RETEST1_TASK_TITLE = "RETEST 1"
RETEST1_PERIOD_KEY = "RETEST_1_C1"
RETEST1_PLACEHOLDER_ASSET = "AUDCAD"
RETEST1_PLACEHOLDER_TIMEFRAME = "H1"
RETEST1_BROKER_PROFILE_ID = "dukascopy_oos2"
RETEST1_DATA_TEST_PRECISION = "2"
RETEST1_DATA_SESSION = "No Session"
RETEST1_EXPECTED_SOURCE_ID = "2"
RETEST1_EXPECTED_BROKER_ID = "3"
RETEST1_BANNED_RESOURCE_TOKENS = (
    "USDJPY",
    "USDJPY_darwinex",
    "USDJPY_dukascopy",
    "_darwinex",
    "Darwinex",
)


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


def question_id(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip()).strip("._-")
    if not safe:
        return "item"
    if len(safe) <= 120:
        return safe
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:10].upper()
    return f"{safe[:109].rstrip('._-')}_{digest}"


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
        qid = question_id(f"{task_title_wanted}-{tab}-{path}")
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


def enforce_disabled_build_block_categories(blocks: ET.Element, actions: list[dict[str, Any]]) -> None:
    for category in BUILD_BLOCK_CATEGORY_DISABLE_TARGET:
        matching_blocks = [block for block in blocks.findall(".//Block") if block.get("category") == category]
        selected_before = [block_key_action(block) for block in matching_blocks if block.get("use") == "true"]
        for block in matching_blocks:
            block.set("use", "false")
        actions.append({
            "field": f"BuildingBlocks:disableCategory:{category}",
            "from": {
                "selectedCount": len(selected_before),
                "selected": selected_before[:50],
                "truncated": len(selected_before) > 50,
            },
            "to": {"selectedCount": 0},
            "changed": bool(selected_before),
        })


def active_building_block_keys(blocks: ET.Element | None) -> list[str]:
    if blocks is None:
        return []
    building_blocks = blocks.find("BuildingBlocks")
    if building_blocks is None:
        return []
    return [
        block.get("key", "")
        for block in building_blocks.findall("Block")
        if block.get("key")
        and block.get("key") not in {"#Left#", "#Right#"}
        and str(block.get("use", "")).lower() == "true"
    ]


def indicator_family_keys(active_keys: list[str]) -> list[str]:
    return [key for key in active_keys if key.startswith("Indicators.")]


def blocksettings_entries_by_id(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(entry.get("canonicalId")): entry
        for entry in manifest.get("entries", [])
        if entry.get("canonicalId")
    }


def normalize_blocksetting_token(value: str) -> str:
    token = str(value or "").strip()
    if token.lower().endswith(".sqb"):
        token = token[:-4]
    return token


def family_from_blocksetting_manifest(manifest: dict[str, Any], value: str) -> str:
    aliases = manifest.get("aliases") or {}
    token = normalize_blocksetting_token(value)
    resolved = aliases.get(token) or aliases.get(token + ".sqb") or token
    entry = blocksettings_entries_by_id(manifest).get(str(resolved))
    if entry:
        return str(entry.get("family") or "")
    lower = str(resolved).lower()
    if "soporteresistencia" in lower:
        return "sr"
    for family in ("tendencia", "momentum", "volatilidad", "regimen", "volumen", "estadistico", "filtros"):
        if family in lower:
            return family
    return ""


def resolve_capa1_blocksetting_manifest_entry(blocksetting: str, timeframe: str) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = read_json(BLOCKSETTINGS_MANIFEST_PATH, {})
    entries = blocksettings_entries_by_id(manifest)
    aliases = manifest.get("aliases") or {}
    token = normalize_blocksetting_token(blocksetting)
    resolved = str(aliases.get(token) or aliases.get(token + ".sqb") or token)
    family = family_from_blocksetting_manifest(manifest, resolved)
    resolver = manifest.get("capa1Resolver") or {}
    family_rules = (resolver.get("families") or {}).get(family) or {}
    tf = str(timeframe or "").strip().upper()
    intraday_timeframes = set(resolver.get("intradayTimeframes") or [])
    if tf in intraday_timeframes and family_rules.get("intraday"):
        candidate = str(family_rules["intraday"])
    else:
        candidate = str(family_rules.get("default") or resolved)
    entry = entries.get(candidate)
    if not entry:
        raise ValueError(f"BlockSetting not found in manifest: {candidate}")
    return manifest, entry


def read_blocksetting_blocks(entry: dict[str, Any]) -> ET.Element:
    filename = str(entry.get("filename") or "")
    path = BLOCKSETTINGS_RESOURCE_DIR / filename
    if not filename or not path.is_file():
        raise FileNotFoundError(f"BlockSetting .sqb not found: {path}")
    with zipfile.ZipFile(path) as zf:
        return ET.fromstring(zf.read("config.xml"))


def replace_building_blocks_from_source(blocks: ET.Element, source_blocks: ET.Element) -> dict[str, Any]:
    current_building_blocks = blocks.find("BuildingBlocks")
    source_building_blocks = source_blocks.find("BuildingBlocks")
    if source_building_blocks is None:
        return {"field": "BuildingBlocks", "error": "source_missing", "changed": False}
    current_text_raw = serialize_xml(current_building_blocks) if current_building_blocks is not None else ""
    source_text_raw = serialize_xml(source_building_blocks)
    current_text = current_text_raw.strip()
    source_text = source_text_raw.strip()
    source_copy = ET.fromstring(source_text_raw)
    if current_building_blocks is None:
        blocks.insert(0, source_copy)
    else:
        children = list(blocks)
        index = children.index(current_building_blocks)
        blocks.remove(current_building_blocks)
        blocks.insert(index, source_copy)
    return {
        "field": "BuildingBlocks",
        "from": {"sha256": hashlib.sha256(current_text.encode("utf-8")).hexdigest().upper()},
        "to": {"sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest().upper()},
        "changed": current_text != source_text,
    }


def update_build_indicators_target_in_cfx(
    cfx: Path,
    backup_root: Path,
    blocksetting: str,
    timeframe: str,
    apply: bool,
) -> dict[str, Any]:
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

    _, entry = resolve_capa1_blocksetting_manifest_entry(blocksetting, timeframe)
    source_blocks = read_blocksetting_blocks(entry)
    before_active = active_building_block_keys(blocks)
    expected_active = active_building_block_keys(source_blocks)
    payload["blocksetting"] = {
        "requested": blocksetting,
        "timeframe": timeframe,
        "resolved": entry.get("canonicalId"),
        "filename": entry.get("filename"),
        "sha256": entry.get("sha256"),
        "activeBlocks": len(expected_active),
        "activeIndicators": indicator_family_keys(expected_active),
    }
    payload["actions"].append({
        "field": "BuildingBlocks:activeContract",
        "from": {
            "activeCount": len(before_active),
            "missingExpected": sorted(set(expected_active) - set(before_active)),
            "extraActive": sorted(set(before_active) - set(expected_active)),
        },
        "to": {"activeCount": len(expected_active)},
        "changed": set(before_active) != set(expected_active),
    })
    payload["actions"].append(replace_building_blocks_from_source(blocks, source_blocks))
    enforce_disabled_build_block_categories(blocks, payload["actions"])

    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetRationale"] = {
        "source": "BuildingBlocks is copied from the resolved real .sqb BlockSetting source, not from the donor project.",
        "basePlaceholder": "Capa1 base uses BS_Volatilidad/H4 as placeholder; Project Generator resolves the final BlockSetting by family and timeframe.",
        "fixedLeftSide": "Signals and Stop/Limit entry blocks remain disabled after the source copy.",
    }
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_build_indicators_target(
    root142: Path,
    project_root: Path,
    target: str,
    blocksetting: str,
    timeframe: str,
    apply: bool,
) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase2_build_indicators_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_build_indicators_target_in_cfx(path, backup_root / name, blocksetting, timeframe, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(item.get("exists") and item.get("isZip") and not item.get("error") for item in results.values()),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_indicators_target",
        "apply": apply,
        "target": target,
        "requestedBlocksetting": blocksetting,
        "requestedTimeframe": timeframe,
        "results": results,
        "nextPhase": "phase2_build_indicators_diff_review" if not apply else "phase2_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_indicators_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def generator_period(period_key: str) -> tuple[str, str]:
    profile = read_json(GENERATOR_PROFILES_PATH, {})
    raw_period = (profile.get("retestPeriods") or {}).get(period_key) or []
    if len(raw_period) != 2:
        raise ValueError(f"Missing generator period {period_key}")
    return str(raw_period[0]), str(raw_period[1])


def epoch_ms_for_date(value: str) -> int:
    parsed = datetime.strptime(value, "%Y.%m.%d").replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def bounded_period_ms(period: tuple[str, str], data_from: Any, data_to: Any) -> tuple[str, str]:
    period_from = epoch_ms_for_date(period[0])
    period_to = epoch_ms_for_date(period[1])
    try:
        available_from = int(data_from)
        available_to = int(data_to)
    except (TypeError, ValueError):
        return str(period_from), str(period_to)
    if period_to < available_from or period_from > available_to:
        return str(available_from), str(available_to)
    return str(max(period_from, available_from)), str(min(period_to, available_to))


def _format_decimal(value: Any, default: str = "0.0") -> str:
    if value is None or value == "":
        return default
    try:
        text = f"{float(value):.12g}"
    except (TypeError, ValueError):
        text = str(value)
    if "e" in text:
        text = text.replace("e", "E")
    return text


def _sqlite_row_dict(row: sqlite3.Row | None) -> dict[str, Any]:
    if row is None:
        return {}
    return {key: row[key] for key in row.keys()}


def _retest1_broker_profile() -> dict[str, Any]:
    profile = read_json(GENERATOR_PROFILES_PATH, {})
    return dict(((profile.get("brokerProfiles") or {}).get(RETEST1_BROKER_PROFILE_ID) or {}))


def fallback_retest1_oos2_resource() -> dict[str, Any]:
    profile = _retest1_broker_profile()
    symbol = f"{RETEST1_PLACEHOLDER_ASSET}{profile.get('brokerPostfix') or '_dukascopy'}"
    return {
        "asset": RETEST1_PLACEHOLDER_ASSET,
        "symbol": symbol,
        "instrument": symbol,
        "source_id": str(profile.get("sourceId") or RETEST1_EXPECTED_SOURCE_ID),
        "broker_id": str(profile.get("brokerId") or RETEST1_EXPECTED_BROKER_ID),
        "broker_name": profile.get("brokerName") or "[[Dukascopy]]",
        "broker_description": profile.get("brokerDescription") or "Dukascopy",
        "broker_postfix": profile.get("brokerPostfix") or "_dukascopy",
        "broker_timezone": profile.get("timezone") or "EETUS",
        "precision": profile.get("precision") or "TICK",
        "description": "FX_Forex_Currency",
        "tick_size": "0.0001",
        "tick_step": "0.00001",
        "min_distance": "0.0",
        "spread": "1.9",
        "slippage": "0.0",
        "point_value": "71848.371197",
        "data_type": "3",
        "exchange": "",
        "country": "",
        "sector": "Currency",
        "ordersize_multiplier": "1.0",
        "ordersize_step": "0.01",
        "commissions_xml": '<Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">0.00</Param></Params></Method>',
        "swap_xml": '<Swap use="true" type="points" long="-2.07" short="-2.36" tripleSwapOn="NEVER" rolloutHour="23:00"/>',
        "swap_attrs": {
            "use": "true",
            "type": "points",
            "long": "-2.07",
            "short": "-2.36",
            "tripleSwapOn": "NEVER",
            "rolloutHour": "23:00",
        },
        "date_from_ms": str(epoch_ms_for_date(generator_period(RETEST1_PERIOD_KEY)[0])),
        "date_to_ms": str(epoch_ms_for_date(generator_period(RETEST1_PERIOD_KEY)[1])),
        "u_symbol": RETEST1_PLACEHOLDER_ASSET,
        "u_symbol_name": RETEST1_PLACEHOLDER_ASSET,
        "source": "fallback_static_dukascopy_oos2",
    }


def retest1_oos2_target_resource(root142: Path | None = None) -> dict[str, Any]:
    """Resolve the protected RETEST 1 placeholder from SQX 142 data.db when possible."""
    target = fallback_retest1_oos2_resource()
    if root142 is None:
        return target
    db_path = root142 / "user" / "data" / "data.db"
    if not db_path.is_file():
        return target

    symbol = target["symbol"]
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            instrument = _sqlite_row_dict(conn.execute(
                "SELECT * FROM INSTRUMENTS WHERE INSTRUMENT = ?",
                (symbol,),
            ).fetchone())
            data = _sqlite_row_dict(conn.execute(
                """
                SELECT SYMBOL,INSTRUMENT,TIMEFRAME,TIMEZONE,DATEFROM,DATETO,ROWS,DATATYPE,USYMBOL,USYMBOLNAME,REMOVE_WEEKENDS,SOURCE
                FROM DATA
                WHERE SYMBOL = ? OR INSTRUMENT = ?
                ORDER BY CASE WHEN TIMEFRAME = 'TICK' THEN 0 ELSE 1 END, ROWS DESC
                LIMIT 1
                """,
                (symbol, symbol),
            ).fetchone())
            broker_id = instrument.get("BROKER_ID") or int(RETEST1_EXPECTED_BROKER_ID)
            broker = _sqlite_row_dict(conn.execute(
                "SELECT * FROM BROKER WHERE ID = ?",
                (broker_id,),
            ).fetchone())
        finally:
            conn.close()
    except sqlite3.Error:
        return target

    if not instrument:
        return target

    target.update({
        "instrument": str(instrument.get("INSTRUMENT") or symbol),
        "description": str(instrument.get("DESCRIPTION") or target["description"]),
        "tick_size": _format_decimal(instrument.get("TICKSIZE"), target["tick_size"]),
        "tick_step": _format_decimal(instrument.get("TICKSTEP"), target["tick_step"]),
        "min_distance": _format_decimal(instrument.get("MIN_DISTANCE"), target["min_distance"]),
        "spread": _format_decimal(instrument.get("DEFAULTSPREAD"), target["spread"]),
        "slippage": _format_decimal(instrument.get("DEFAULTSLIPPAGE"), target["slippage"]),
        "point_value": _format_decimal(instrument.get("POINTVALUE"), target["point_value"]),
        "data_type": str(instrument.get("DATATYPE") or target["data_type"]),
        "exchange": str(instrument.get("EXCHANGE") or ""),
        "country": str(instrument.get("COUNTRY") or ""),
        "sector": str(instrument.get("SECTOR") or target["sector"]),
        "ordersize_multiplier": _format_decimal(instrument.get("ORDERSIZEMULTIPLIER"), target["ordersize_multiplier"]),
        "ordersize_step": _format_decimal(instrument.get("ORDERSIZESTEP"), target["ordersize_step"]),
        "commissions_xml": str(instrument.get("COMMISSIONS") or target["commissions_xml"]),
        "swap_xml": str(instrument.get("SWAP") or target["swap_xml"]),
        "broker_id": str(instrument.get("BROKER_ID") or target["broker_id"]),
        "broker_postfix": str(broker.get("POSTFIX") or target["broker_postfix"]),
        "broker_name": str(broker.get("NAME") or target["broker_name"]),
        "broker_description": str(broker.get("DESC") or target["broker_description"]),
        "broker_timezone": str(broker.get("MT_TIMEZONE") or target["broker_timezone"]),
        "date_from_ms": str(data.get("DATEFROM") or target["date_from_ms"]),
        "date_to_ms": str(data.get("DATETO") or target["date_to_ms"]),
        "u_symbol": str(data.get("USYMBOL") or RETEST1_PLACEHOLDER_ASSET),
        "u_symbol_name": str(data.get("USYMBOLNAME") or RETEST1_PLACEHOLDER_ASSET),
        "source": "sqx142_data_db_instruments",
    })
    # Methodology owns the cross-broker profile even if the DATA row carries a legacy broker id.
    profile = _retest1_broker_profile()
    target["source_id"] = str(profile.get("sourceId") or RETEST1_EXPECTED_SOURCE_ID)
    target["broker_id"] = str(profile.get("brokerId") or RETEST1_EXPECTED_BROKER_ID)
    target["broker_postfix"] = str(profile.get("brokerPostfix") or "_dukascopy")
    target["broker_name"] = str(profile.get("brokerName") or target["broker_name"])
    target["broker_description"] = str(profile.get("brokerDescription") or target["broker_description"])
    target["broker_timezone"] = str(profile.get("timezone") or target["broker_timezone"])
    target["precision"] = str(profile.get("precision") or target["precision"])
    target["swap_attrs"] = swap_attrs_from_xml(target["swap_xml"], target["swap_attrs"])
    return target


def swap_attrs_from_xml(raw: str, fallback: dict[str, str]) -> dict[str, str]:
    try:
        node = ET.fromstring(raw)
    except ET.ParseError:
        return dict(fallback)
    if node.tag != "Swap":
        return dict(fallback)
    attrs = dict(fallback)
    attrs.update({key: str(value) for key, value in node.attrib.items()})
    return attrs


def ensure_sizebased_commission(setup: ET.Element, commission_value: str, actions: list[dict[str, Any]]) -> None:
    commissions = setup.find("Commissions")
    if commissions is None:
        commissions = ET.SubElement(setup, "Commissions")
        before = []
    else:
        before = [
            {
                "type": method.get("type", ""),
                "use": method.get("use", ""),
                "params": {
                    param.get("key", ""): (param.text or "")
                    for param in method.findall("./Params/Param")
                    if param.get("key")
                },
            }
            for method in commissions.findall("Method")
        ]
    for method in commissions.findall("Method"):
        method.set("use", "false")
    size_method = commissions.find("Method[@type='SizeBased']")
    if size_method is None:
        size_method = ET.SubElement(commissions, "Method", {"type": "SizeBased"})
    size_method.set("use", "true")
    params = size_method.find("Params")
    if params is None:
        params = ET.SubElement(size_method, "Params")
    param = params.find("Param[@key='Commission']")
    if param is None:
        param = ET.SubElement(params, "Param", {"key": "Commission", "className": "SizeBased"})
    param.set("className", "SizeBased")
    param.text = commission_value
    after = [
        {
            "type": method.get("type", ""),
            "use": method.get("use", ""),
            "params": {
                param_node.get("key", ""): (param_node.text or "")
                for param_node in method.findall("./Params/Param")
                if param_node.get("key")
            },
        }
        for method in commissions.findall("Method")
    ]
    actions.append({
        "field": "Data/Setup/Commissions",
        "from": before,
        "to": after,
        "changed": before != after,
    })


def ensure_single_child(parent: ET.Element, tag: str, actions: list[dict[str, Any]], field: str) -> ET.Element:
    existing = list(parent.findall(tag))
    if existing:
        node = existing[0]
        removed = [value_for_node(item) for item in existing[1:]]
        for item in existing[1:]:
            parent.remove(item)
    else:
        node = ET.SubElement(parent, tag)
        removed = []
    actions.append({
        "field": f"{field}:dedupe",
        "from": removed,
        "to": [],
        "changed": bool(removed) or not existing,
    })
    return node


def make_retest1_instrument_attrs(resource: dict[str, Any]) -> dict[str, str]:
    return {
        "instrument": str(resource["instrument"]),
        "description": str(resource.get("description") or ""),
        "tickSize": str(resource.get("tick_size") or ""),
        "tickStep": str(resource.get("tick_step") or ""),
        "minDistance": str(resource.get("min_distance") or "0.0"),
        "tickValueInMoney": "0.0",
        "dateFrom": "0",
        "dateTo": "0",
        "rows": "0",
        "totalDays": "0",
        "defaultSpread": str(resource.get("spread") or ""),
        "defaultSlippage": str(resource.get("slippage") or "0.0"),
        "decimals": "5",
        "commissions": str(resource.get("commissions_xml") or ""),
        "pointValue": str(resource.get("point_value") or ""),
        "dataType": str(resource.get("data_type") or "3"),
        "recognizedFromOrders": "false",
        "exchange": str(resource.get("exchange") or ""),
        "country": str(resource.get("country") or ""),
        "sector": str(resource.get("sector") or ""),
        "swap": str(resource.get("swap_xml") or ""),
        "orderSizeMultiplier": str(resource.get("ordersize_multiplier") or "1.0"),
        "orderSizeStep": str(resource.get("ordersize_step") or "0.01"),
        "broker": str(resource.get("broker_id") or RETEST1_EXPECTED_BROKER_ID),
    }


def compact_retest1_resources_summary(root: ET.Element) -> dict[str, Any]:
    resources = root.find(".//Resources")
    if resources is None:
        return {"exists": False}
    summary = build_resources_summary(root)
    summary.update({
        "customIndicators": len(resources.findall("./CustomIndicators/*")),
        "customBlocks": len(resources.findall("./CustomBlocks/*")),
        "childOrder": [child.tag for child in list(resources)],
    })
    return summary


def apply_retest1_data_resources_to_root(root: ET.Element, resource: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    period = generator_period(RETEST1_PERIOD_KEY)
    setup = root.find(".//Data/Setups/Setup")
    data = find_section(root, "Data")
    if setup is None or data is None:
        actions.append({"field": "Data", "error": "missing_setup_or_data", "changed": False})
        return actions

    for setup_index, current_setup in enumerate(root.findall(".//Setup"), start=1):
        setup_label = "Data/Setup" if current_setup is setup else f"Setup#{setup_index}"
        for key, wanted in {
            "dateFrom": period[0],
            "dateTo": period[1],
            "testPrecision": RETEST1_DATA_TEST_PRECISION,
            "session": RETEST1_DATA_SESSION,
        }.items():
            before = current_setup.get(key, "")
            current_setup.set(key, wanted)
            actions.append({"field": f"{setup_label}:{key}", "from": before, "to": wanted, "changed": before != wanted})

        chart = ensure_single_child(current_setup, "Chart", actions, f"{setup_label}/Chart")
        before_chart = dict(chart.attrib)
        chart.attrib.clear()
        chart.attrib.update({
            "symbol": str(resource["symbol"]),
            "timeframe": RETEST1_PLACEHOLDER_TIMEFRAME,
            "spread": str(resource["spread"]),
        })
        actions.append({
            "field": f"{setup_label}/Chart",
            "from": before_chart,
            "to": dict(chart.attrib),
            "changed": before_chart != dict(chart.attrib),
        })

        ensure_sizebased_commission(current_setup, "0.00", actions)

        swap = ensure_single_child(current_setup, "Swap", actions, f"{setup_label}/Swap")
        before_swap = dict(swap.attrib)
        swap.attrib.clear()
        swap.attrib.update({key: str(value) for key, value in resource.get("swap_attrs", {}).items()})
        actions.append({
            "field": f"{setup_label}/Swap",
            "from": before_swap,
            "to": dict(swap.attrib),
            "changed": before_swap != dict(swap.attrib),
        })

    out_of_sample = data.find("OutOfSample")
    if out_of_sample is None:
        out_of_sample = ET.SubElement(data, "OutOfSample", {"showGraph": "false"})
        before_oos_attrs = {}
    else:
        before_oos_attrs = dict(out_of_sample.attrib)
        out_of_sample.set("showGraph", "false")
    removed_ranges = [dict(item.attrib) for item in out_of_sample.findall("Range")]
    for range_node in list(out_of_sample.findall("Range")):
        out_of_sample.remove(range_node)
    actions.append({
        "field": "Data/OutOfSample",
        "from": {"attrs": before_oos_attrs, "ranges": removed_ranges},
        "to": {"attrs": dict(out_of_sample.attrib), "ranges": []},
        "changed": before_oos_attrs != dict(out_of_sample.attrib) or bool(removed_ranges),
    })

    resources = find_section(root, "Resources")
    if resources is None:
        resources = ET.SubElement(root, "Resources")
        before_resources: dict[str, Any] = {"exists": False}
    else:
        before_resources = compact_retest1_resources_summary(root)
        for child in list(resources):
            resources.remove(child)

    date_from, date_to = bounded_period_ms(period, resource.get("date_from_ms"), resource.get("date_to_ms"))
    symbols = ET.SubElement(resources, "Symbols")
    symbol_node = ET.SubElement(symbols, "Symbol", {
        "name": str(resource["symbol"]),
        "source": str(resource["source_id"]),
        "barType": "1",
        "precision": str(resource.get("precision") or "TICK"),
        "timezone": str(resource.get("broker_timezone") or "EETUS"),
        "dateFrom": date_from,
        "dateTo": date_to,
        "uSymbol": str(resource.get("u_symbol") or RETEST1_PLACEHOLDER_ASSET),
        "uSymbolName": str(resource.get("u_symbol_name") or RETEST1_PLACEHOLDER_ASSET),
        "removeWeekends": "false",
        "broker": str(resource["broker_id"]),
    })
    instrument_attrs = make_retest1_instrument_attrs(resource)
    ET.SubElement(symbol_node, "InstrumentInfo", instrument_attrs)

    brokers = ET.SubElement(resources, "Brokers")
    ET.SubElement(brokers, "Broker", {
        "id": str(resource["broker_id"]),
        "name": str(resource.get("broker_name") or "[[Dukascopy]]"),
        "description": str(resource.get("broker_description") or "Dukascopy"),
        "timezone": str(resource.get("broker_timezone") or "EETUS"),
        "postfix": str(resource.get("broker_postfix") or "_dukascopy"),
        "mtUse": "true",
        "spUse": "false",
    })
    instruments = ET.SubElement(resources, "Instruments")
    ET.SubElement(instruments, "InstrumentInfo", instrument_attrs)
    ET.SubElement(resources, "Sessions")
    ET.SubElement(resources, "CustomIndicators")
    ET.SubElement(resources, "CustomBlocks")
    after_resources = compact_retest1_resources_summary(root)
    actions.append({
        "field": "Resources",
        "from": before_resources,
        "to": after_resources,
        "changed": before_resources != after_resources,
    })
    return actions


def enforce_retest1_data_resources_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    period = generator_period(RETEST1_PERIOD_KEY)
    setup = root.find(".//Data/Setups/Setup")
    if setup is None:
        return ["Data/Setup missing"]
    if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
        issues.append("RETEST 1 dates are not protected RETEST_1_C1")
    if setup.get("testPrecision") != RETEST1_DATA_TEST_PRECISION:
        issues.append("RETEST 1 testPrecision is not simulated/tick code 2")
    charts = setup.findall("Chart")
    if len(charts) != 1:
        issues.append(f"RETEST 1 must have exactly one Chart, found {len(charts)}")
    elif charts[0].get("symbol") != f"{RETEST1_PLACEHOLDER_ASSET}_dukascopy":
        issues.append(f"RETEST 1 placeholder chart must be {RETEST1_PLACEHOLDER_ASSET}_dukascopy")
    for chart in root.findall(".//Setup/Chart"):
        if chart.get("symbol") != f"{RETEST1_PLACEHOLDER_ASSET}_dukascopy":
            issues.append(f"Stale RETEST 1 setup chart remains: {chart.get('symbol')}")
    if root.findall(".//Data/OutOfSample/Range"):
        issues.append("RETEST 1 OOS2-only setup should not carry nested OutOfSample ranges")

    resources = root.find(".//Resources")
    if resources is None:
        issues.append("Resources missing")
        return issues
    symbols = resources.findall("./Symbols/Symbol")
    if len(symbols) != 1:
        issues.append(f"RETEST 1 resources must have exactly one Symbol, found {len(symbols)}")
    else:
        symbol = symbols[0]
        if symbol.get("name") != f"{RETEST1_PLACEHOLDER_ASSET}_dukascopy":
            issues.append("RETEST 1 resource symbol is not Dukascopy placeholder")
        if symbol.get("source") != RETEST1_EXPECTED_SOURCE_ID:
            issues.append("RETEST 1 resource source is not Dukascopy source 2")
        if symbol.get("broker") != RETEST1_EXPECTED_BROKER_ID:
            issues.append("RETEST 1 resource broker is not Dukascopy broker 3")
        info = symbol.find("InstrumentInfo")
        if info is None or info.get("broker") != RETEST1_EXPECTED_BROKER_ID:
            issues.append("RETEST 1 nested InstrumentInfo is not broker 3")
    brokers = resources.findall("./Brokers/Broker")
    if [broker.get("id") for broker in brokers] != [RETEST1_EXPECTED_BROKER_ID]:
        issues.append("RETEST 1 Resources/Brokers must contain only broker 3")
    if resources.findall("./Sessions/Session"):
        issues.append("RETEST 1 resources should not keep session entries")
    if resources.findall("./CustomBlocks/*"):
        issues.append("RETEST 1 resources should not keep embedded CustomBlocks")
    data = find_section(root, "Data")
    text = (serialize_xml(data) if data is not None else "") + serialize_xml(resources)
    for token in RETEST1_BANNED_RESOURCE_TOKENS:
        if token in text:
            issues.append(f"Forbidden RETEST 1 donor/base token leaked: {token}")
    if re.search(r"[A-Za-z]:\\", text):
        issues.append("Local absolute path leaked into RETEST 1 XML")
    return issues


def update_retest1_data_resources_target_in_cfx(
    cfx: Path,
    backup_root: Path,
    apply: bool,
    root142: Path,
) -> dict[str, Any]:
    resource = retest1_oos2_target_resource(root142)
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
        "resourceSource": resource.get("source", ""),
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, RETEST1_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "retest1_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["beforeData"] = first_setup_summary(root)
    payload["beforeResources"] = compact_retest1_resources_summary(root)
    payload["actions"] = apply_retest1_data_resources_to_root(root, resource)
    payload["afterData"] = first_setup_summary(root)
    payload["afterResources"] = compact_retest1_resources_summary(root)
    issues = enforce_retest1_data_resources_guard(root)
    after_text = serialize_xml(root)
    payload["issues"] = issues
    payload["guardOk"] = not issues
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["changed"] = before_text != after_text
    payload["targetValues"] = {
        "role": "passive_clone_of_RETEST0_with_protected_OOS2_cross_broker_override",
        "periodKey": RETEST1_PERIOD_KEY,
        "dateFrom": generator_period(RETEST1_PERIOD_KEY)[0],
        "dateTo": generator_period(RETEST1_PERIOD_KEY)[1],
        "symbol": resource["symbol"],
        "timeframe": RETEST1_PLACEHOLDER_TIMEFRAME,
        "spread": resource["spread"],
        "source": RETEST1_EXPECTED_SOURCE_ID,
        "broker": RETEST1_EXPECTED_BROKER_ID,
        "testPrecision": RETEST1_DATA_TEST_PRECISION,
        "outOfSampleRanges": [],
        "customBlocks": 0,
    }
    payload["targetRationale"] = {
        "methodology": "RETEST 1 is the protected OOS2/cross-broker Dukascopy validation fed by RETEST 0.",
        "passiveClone": "Data/Resources receive the protected override; retest generation/improvement choices are handled in later tabs.",
        "generatorOwned": "Project Generator rewrites this same broker/period for the selected asset while preserving the cross-broker rule.",
        "noDonorCopy": "Mining15 resources are not copied literally; target is resolved from generator governance and local SQX data.db when available.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_retest1_data_resources_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase4_retest1_data_resources_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_retest1_data_resources_target_in_cfx(path, backup_root / name, apply=apply, root142=root142)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase4",
        "operation": "retest1_data_resources_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase4_retest1_data_resources_diff_review" if not apply else "phase4_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase4_retest1_data_resources_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def update_build_data_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    date_from, date_to = generator_period(BUILD_DATA_PERIOD_KEY)
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
    data = find_section(root, "Data")
    setup = root.find(".//Data/Setups/Setup") if root is not None else None
    if not task_xml_name or root is None or data is None or setup is None:
        payload["error"] = "build_task_or_data_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    target_attrs = {
        "dateFrom": date_from,
        "dateTo": date_to,
        "testPrecision": BUILD_DATA_TEST_PRECISION,
        "session": BUILD_DATA_SESSION,
    }
    for key, wanted in target_attrs.items():
        before = setup.get(key, "")
        setup.set(key, wanted)
        payload["actions"].append({
            "field": f"Data/Setup:{key}",
            "from": before,
            "to": wanted,
            "changed": before != wanted,
        })

    removed_oos = []
    out_of_sample = data.find("OutOfSample")
    if out_of_sample is not None:
        for range_node in list(out_of_sample.findall("Range")):
            removed_oos.append(dict(range_node.attrib))
            out_of_sample.remove(range_node)
    payload["actions"].append({
        "field": "Data/OutOfSample/Range",
        "from": removed_oos,
        "to": [],
        "changed": bool(removed_oos),
    })

    charts = [dict(chart.attrib) for chart in setup.findall("Chart")]
    swaps = [dict(swap.attrib) for swap in setup.findall("Swap")]
    payload["generatorOwned"] = {
        "charts": charts,
        "swaps": swaps,
        "note": "Symbol, timeframe, spread and swaps are preserved in the base/template and rewritten by Project Generator per selected asset/timeframe.",
    }
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "periodKey": BUILD_DATA_PERIOD_KEY,
        "dateFrom": date_from,
        "dateTo": date_to,
        "testPrecision": BUILD_DATA_TEST_PRECISION,
        "precisionMeaning": "simulated / 1 minute data tick simulation in SQX 142 UI",
        "session": BUILD_DATA_SESSION,
        "outOfSampleRanges": [],
    }
    payload["targetRationale"] = {
        "methodology": "Build Capa1 mines only IS; OOS validation is performed by later retest tasks.",
        "precision": "Operator confirmed Build data must remain simulated; SQX 142 maps this to testPrecision=2.",
        "genericBase": "Do not copy donor USDJPY/H4 costs; Project Generator owns charts, spreads and swaps.",
    }
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_build_data_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase2_build_data_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_build_data_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(item.get("exists") and item.get("isZip") and not item.get("error") for item in results.values()),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_data_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase2_build_data_diff_review" if not apply else "phase2_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_data_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def build_resources_summary(root: ET.Element) -> dict[str, Any]:
    resources = root.find(".//Resources")
    chart_symbols = sorted({
        chart.get("symbol", "")
        for chart in root.findall(".//Data/Setups/Setup/Chart")
        if chart.get("symbol")
    })
    if resources is None:
        return {"chartSymbols": chart_symbols, "resourcesFound": False}
    symbols = [dict(symbol.attrib) for symbol in resources.findall("./Symbols/Symbol")]
    brokers = [dict(broker.attrib) for broker in resources.findall("./Brokers/Broker")]
    sessions = [dict(session.attrib) for session in resources.findall("./Sessions/Session")]
    instruments = [dict(instrument.attrib) for instrument in resources.findall("./Instruments/InstrumentInfo")]
    nested_infos = []
    for symbol in resources.findall("./Symbols/Symbol"):
        info = symbol.find("InstrumentInfo")
        nested_infos.append(dict(info.attrib) if info is not None else {})
    return {
        "chartSymbols": chart_symbols,
        "resourcesFound": True,
        "symbols": symbols,
        "brokers": brokers,
        "sessions": sessions,
        "instruments": instruments,
        "nestedInstrumentInfos": nested_infos,
    }


def enforce_build_resources_guard(root: ET.Element, actions: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    resources = root.find(".//Resources")
    if resources is None:
        issues.append("Resources section missing")
        return issues

    chart_symbols = {
        chart.get("symbol", "")
        for chart in root.findall(".//Data/Setups/Setup/Chart")
        if chart.get("symbol")
    }
    symbols = resources.findall("./Symbols/Symbol")
    symbol_names = {symbol.get("name", "") for symbol in symbols if symbol.get("name")}
    if chart_symbols != symbol_names:
        issues.append(f"Chart symbols {sorted(chart_symbols)} do not match resource symbols {sorted(symbol_names)}")

    sessions = resources.find("Sessions")
    removed_sessions = []
    if sessions is not None:
        for session in list(sessions.findall("Session")):
            removed_sessions.append(dict(session.attrib))
            sessions.remove(session)
    actions.append({
        "field": "Resources/Sessions/Session",
        "from": removed_sessions,
        "to": [],
        "changed": bool(removed_sessions),
    })

    broker_ids = {broker.get("id", "") for broker in resources.findall("./Brokers/Broker") if broker.get("id")}
    for symbol in symbols:
        name = symbol.get("name", "")
        before_precision = symbol.get("precision", "")
        symbol.set("precision", BUILD_RESOURCES_PRECISION)
        actions.append({
            "field": f"Resources/Symbols/Symbol:{name}:precision",
            "from": before_precision,
            "to": BUILD_RESOURCES_PRECISION,
            "changed": before_precision != BUILD_RESOURCES_PRECISION,
        })
        broker = symbol.get("broker", "")
        if broker not in {"", "-1"} and broker not in broker_ids:
            issues.append(f"Resource symbol {name} references missing broker {broker}")
        info = symbol.find("InstrumentInfo")
        if info is None:
            issues.append(f"Resource symbol {name} has no nested InstrumentInfo")
            continue
        info_broker = info.get("broker", "")
        if info_broker not in {"", "-1"} and info_broker not in broker_ids:
            issues.append(f"Nested InstrumentInfo for {name} references missing broker {info_broker}")

    for instrument in resources.findall("./Instruments/InstrumentInfo"):
        instrument_name = instrument.get("instrument", "")
        if instrument_name and instrument_name not in symbol_names:
            issues.append(f"Standalone InstrumentInfo {instrument_name} is not represented in Resources/Symbols")

    resource_text = serialize_xml(resources)
    for token in BUILD_RESOURCES_BANNED_DONOR_TOKENS:
        if token in resource_text:
            issues.append(f"Donor token leaked into base resources: {token}")
    if re.search(r"[A-Za-z]:\\", resource_text):
        issues.append("Local absolute path leaked into base resources")
    return issues


def update_build_resources_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
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
    if not task_xml_name or root is None:
        payload["error"] = "build_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    payload["before"] = build_resources_summary(root)
    issues = enforce_build_resources_guard(root, payload["actions"])
    payload["after"] = build_resources_summary(root)
    payload["issues"] = issues
    payload["resourceGuardOk"] = not issues
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "precision": BUILD_RESOURCES_PRECISION,
        "baseDataType": BUILD_RESOURCES_BASE_DATA_TYPE,
        "sessions": [],
        "bannedDonorTokens": list(BUILD_RESOURCES_BANNED_DONOR_TOKENS),
    }
    payload["targetRationale"] = {
        "genericBase": "Do not copy donor USDJPY resources; base/template placeholders stay generic.",
        "generatorOwned": "Project Generator rebuilds Symbols, Brokers, Instruments and resource dates for the selected asset/timeframe/target profile.",
        "simulatedData": "Resources precision=TICK describes source data; Build simulated mode remains Data/Setup testPrecision=2.",
    }
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_build_resources_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase2_build_resources_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_build_resources_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("resourceGuardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_resources_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase2_build_resources_diff_review" if not apply else "phase2_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_resources_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def build_crosschecks_summary(root: ET.Element | None) -> dict[str, Any]:
    parent = root.find(".//CrossChecks") if root is not None else None
    if parent is None:
        return {"exists": False, "active": [], "checks": []}
    checks = []
    active = []
    for check in list(parent):
        if not isinstance(check.tag, str) or check.get("use") is None:
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
        item = {
            "id": check.tag,
            "use": check.get("use", ""),
            "activeMethodCount": len(methods),
            "activeConditionCount": len(conditions),
            "activeMethods": methods,
        }
        checks.append(item)
        if check.get("use") == "true":
            active.append(check.tag)
    return {"exists": True, "attributes": dict(parent.attrib), "active": active, "checks": checks}


def enforce_build_crosschecks_guard(root: ET.Element, actions: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    parent = root.find(".//CrossChecks")
    if parent is None:
        return ["CrossChecks section missing"]

    for key, wanted in BUILD_CROSSCHECK_PARENT_TARGET.items():
        before = parent.get(key, "")
        parent.set(key, wanted)
        actions.append({
            "field": f"CrossChecks:{key}",
            "from": before,
            "to": wanted,
            "changed": before != wanted,
        })

    for check in list(parent):
        if not isinstance(check.tag, str) or check.get("use") is None:
            continue
        wanted = "true" if check.tag == BUILD_ACTIVE_CROSSCHECK else "false"
        before = check.get("use", "")
        check.set("use", wanted)
        actions.append({
            "field": f"CrossChecks/{check.tag}:use",
            "from": before,
            "to": wanted,
            "changed": before != wanted,
        })

    active = [check.tag for check in list(parent) if isinstance(check.tag, str) and check.get("use") == "true"]
    if active != [BUILD_ACTIVE_CROSSCHECK]:
        issues.append(f"Build active crosschecks must be only {BUILD_ACTIVE_CROSSCHECK}; found {active}")

    active_text = "".join(
        serialize_xml(check)
        for check in list(parent)
        if isinstance(check.tag, str) and check.get("use") == "true"
    )
    for token in BUILD_CROSSCHECK_BANNED_DONOR_TOKENS:
        if token in active_text:
            issues.append(f"Donor token leaked into active Build crosscheck: {token}")
    return issues


def update_build_crosschecks_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
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
    if not task_xml_name or root is None:
        payload["error"] = "build_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    payload["before"] = build_crosschecks_summary(root)
    issues = enforce_build_crosschecks_guard(root, payload["actions"])
    payload["after"] = build_crosschecks_summary(root)
    payload["issues"] = issues
    payload["crossChecksGuardOk"] = not issues
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "parent": BUILD_CROSSCHECK_PARENT_TARGET,
        "onlyActive": BUILD_ACTIVE_CROSSCHECK,
        "bannedDonorTokensInActiveChecks": list(BUILD_CROSSCHECK_BANNED_DONOR_TOKENS),
    }
    payload["targetRationale"] = {
        "methodology": "Build mining keeps only the lightweight SequentialOptimization crosscheck active.",
        "noDonorCopy": "Disabled crosscheck internals are not promoted from donor to avoid dragging symbols, dates or heavy robustness settings into mining.",
        "quality": "Heavy robustness checks remain scheduled as dedicated retest tasks outside Build.",
    }
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_build_crosschecks_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase2_build_crosschecks_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_build_crosschecks_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("crossChecksGuardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_crosschecks_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase2_build_crosschecks_diff_review" if not apply else "phase2_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_crosschecks_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def section_text(root: ET.Element | None, tab: str) -> str:
    node = find_section(root, tab)
    if node is None:
        return ""
    return serialize_xml(node).strip()


def section_sha256(root: ET.Element | None, tab: str) -> str:
    text = section_text(root, tab)
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper() if text else ""


def static_tab_business_checks(root: ET.Element | None) -> list[str]:
    issues: list[str] = []
    if root is None:
        return ["Build task missing"]

    fixed_size = root.find(".//RiskMoneyManagement//Method[@type='FixedSize']")
    fixed_amount = root.find(".//RiskMoneyManagement//Method[@type='FixedAmount']")
    if fixed_size is None or fixed_size.get("use") != "true":
        issues.append("RiskMoneyManagement FixedSize must remain active")
    if fixed_amount is None or fixed_amount.get("use") != "false":
        issues.append("RiskMoneyManagement FixedAmount must remain disabled")

    databanks = {
        databank.get("name", ""): databank.get("value", "")
        for databank in root.findall(".//Databanks/Databank")
        if databank.get("name")
    }
    if databanks.get("Output") != "null":
        issues.append("Build Databanks Output must remain null; Ranking stores filtered strategies into Results")
    if "Input" not in databanks:
        issues.append("Build Databanks Input placeholder missing")

    market_open = root.find(".//BuildTradingOptions/Params/Param[@key='MarketOpenSession']")
    if market_open is not None and (market_open.text or "") != "No Session":
        issues.append("Build Options MarketOpenSession must remain No Session")
    return issues


def static_tabs_report(cfx: Path, baseline_hashes: dict[str, str] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "tabs": {},
        "issues": [],
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["issues"].append("missing_or_not_zip")
        return payload
    task_xml_name, root = load_task_root(cfx, "Build")
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["issues"].append("build_task_not_found")
        return payload
    for tab in BUILD_STATIC_TABS:
        digest = section_sha256(root, tab)
        expected = (baseline_hashes or BUILD_STATIC_TAB_HASHES).get(tab, "")
        payload["tabs"][tab] = {
            "exists": bool(digest),
            "sha256": digest,
            "expectedSha256": expected,
            "matchesExpected": bool(digest and expected and digest == expected),
        }
        if not digest:
            payload["issues"].append(f"{tab} section missing")
        elif expected and digest != expected:
            payload["issues"].append(f"{tab} section drift: {digest} != {expected}")
    payload["issues"].extend(static_tab_business_checks(root))
    payload["staticTabsGuardOk"] = not payload["issues"]
    return payload


def promote_build_static_tabs_target(root142: Path, project_root: Path, target: str) -> dict[str, Any]:
    ensure_ledger(project_root)
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {name: static_tabs_report(path) for name, path in targets.items()}
    payload: dict[str, Any] = {
        "ok": all(item.get("exists") and item.get("isZip") and item.get("staticTabsGuardOk") for item in results.values()),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_static_tabs_target",
        "target": target,
        "tabs": list(BUILD_STATIC_TABS),
        "mode": "audit_only_keep_current_values",
        "results": results,
        "targetRationale": {
            "operatorDecision": "Options, ATMs, PartsToImprove, RiskMoneyManagement, Notes and Optimization stay as current values.",
            "databanks": "Build Databanks stay as current placeholder; Ranking filters decide what is saved to Results.",
            "nextStep": "If this audit passes, Build Capa1 Phase 2 can close and move to RETEST 0.",
        },
        "nextPhase": "phase2_closeout_or_phase3_retest0",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_static_tabs_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


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
    enforce_disabled_build_block_categories(blocks, payload["actions"])

    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetRationale"] = {
        "fixedLeftSide": "Signals and Stop/Limit entry blocks stay disabled in Capa1 base.",
        "preservedLeftSide": "Indicators remain methodology/BlockSettings owned and are not rewritten here.",
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
            "disabledBlockCategories": list(BUILD_BLOCK_CATEGORY_DISABLE_TARGET),
            "preservedBlockCategories": list(BUILD_BLOCK_CATEGORY_PRESERVE_TARGET),
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


def latest_questionnaire_path(project_root: Path, task_title_wanted: str, tab: str) -> Path | None:
    root = ledger_root(project_root) / "questionnaires" / "capa1" / slug(task_title_wanted)
    if not root.is_dir():
        return None
    candidates = [
        path
        for path in root.glob(f"{slug(tab)}_*.json")
        if path.is_file() and not path.name.startswith("_task_summary_")
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name))


def record_tab_answer(
    project_root: Path,
    task_title_wanted: str,
    tab: str,
    answer: str,
    note: str,
    allow_empty: bool,
) -> dict[str, Any]:
    ensure_ledger(project_root)
    source = latest_questionnaire_path(project_root, task_title_wanted, tab)
    if source is None:
        return {
            "ok": False,
            "version": VERSION,
            "error": "questionnaire_not_found",
            "taskTitle": task_title_wanted,
            "tab": tab,
            "hint": "Run questionnaire --write before recording a tab answer.",
        }

    questionnaire = read_json(source, {})
    questions = questionnaire.get("questions") or []
    if not questions and not allow_empty:
        return {
            "ok": False,
            "version": VERSION,
            "error": "questionnaire_has_no_questions",
            "sourceQuestionnaire": str(source),
            "taskTitle": task_title_wanted,
            "tab": tab,
            "hint": "Use --allow-empty if this tab is intentionally empty.",
        }

    ids = [str(item.get("id", "")).strip() for item in questions if str(item.get("id", "")).strip()]
    id_counts = Counter(ids)
    duplicate_ids = sorted(qid for qid, count in id_counts.items() if count > 1)
    if duplicate_ids:
        return {
            "ok": False,
            "version": VERSION,
            "error": "duplicate_question_ids",
            "sourceQuestionnaire": str(source),
            "taskTitle": task_title_wanted,
            "tab": tab,
            "questionCount": len(questions),
            "uniqueQuestionCount": len(set(ids)),
            "duplicateIdCount": len(duplicate_ids),
            "duplicateIdSample": duplicate_ids[:10],
            "hint": "Regenerate the questionnaire with the current tool before recording bulk answers.",
        }

    if not ids and allow_empty:
        ids = [question_id(f"{task_title_wanted}-{tab}-empty-tab-confirmed")]

    answered_at = now_iso()
    payload = {
        "version": VERSION,
        "scope": "capa1",
        "taskTitle": task_title_wanted,
        "tab": tab,
        "createdAt": answered_at,
        "updatedAt": answered_at,
        "bulkAnswer": True,
        "sourceQuestionnaire": str(source),
        "questionCount": len(questions),
        "uniqueQuestionCount": len(ids),
        "answer": answer,
        "note": note,
        "answers": {
            qid: {
                "answer": answer,
                "note": note,
                "answeredAt": answered_at,
            }
            for qid in ids
        },
    }
    target = ledger_root(project_root) / "answers" / "capa1" / slug(task_title_wanted) / f"{slug(tab)}.json"
    write_json(target, payload)
    return {
        "ok": True,
        "version": VERSION,
        "written": str(target),
        "sourceQuestionnaire": str(source),
        "taskTitle": task_title_wanted,
        "tab": tab,
        "answerCount": len(ids),
        "questionCount": len(questions),
        "bulkAnswer": True,
    }


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

    promote_indicators = sub.add_parser("build-indicators-target")
    promote_indicators.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_indicators.add_argument("--blocksetting", default=BUILD_INDICATORS_DEFAULT_BLOCKSETTING)
    promote_indicators.add_argument("--timeframe", default=BUILD_INDICATORS_DEFAULT_TIMEFRAME)
    promote_indicators.add_argument("--apply", action="store_true")

    promote_data = sub.add_parser("build-data-target")
    promote_data.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_data.add_argument("--apply", action="store_true")

    promote_resources = sub.add_parser("build-resources-target")
    promote_resources.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_resources.add_argument("--apply", action="store_true")

    promote_crosschecks = sub.add_parser("build-crosschecks-target")
    promote_crosschecks.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_crosschecks.add_argument("--apply", action="store_true")

    promote_static_tabs = sub.add_parser("build-static-tabs-target")
    promote_static_tabs.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")

    retest1_data_resources = sub.add_parser("retest1-data-resources-target")
    retest1_data_resources.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    retest1_data_resources.add_argument("--apply", action="store_true")

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

    tab_answer = sub.add_parser("record-tab-answer")
    tab_answer.add_argument("--task-title", required=True)
    tab_answer.add_argument("--tab", required=True)
    tab_answer.add_argument("--answer", required=True)
    tab_answer.add_argument("--note", default="")
    tab_answer.add_argument("--allow-empty", action="store_true")

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
    if args.command == "build-indicators-target":
        json_print(promote_build_indicators_target(
            root142,
            project_root,
            target=args.target,
            blocksetting=args.blocksetting,
            timeframe=args.timeframe,
            apply=args.apply,
        ))
        return 0
    if args.command == "build-data-target":
        json_print(promote_build_data_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "build-resources-target":
        json_print(promote_build_resources_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "build-crosschecks-target":
        json_print(promote_build_crosschecks_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "build-static-tabs-target":
        json_print(promote_build_static_tabs_target(root142, project_root, target=args.target))
        return 0
    if args.command == "retest1-data-resources-target":
        json_print(promote_retest1_data_resources_target(root142, project_root, target=args.target, apply=args.apply))
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
    if args.command == "record-tab-answer":
        json_print(record_tab_answer(
            project_root,
            task_title_wanted=args.task_title,
            tab=args.tab,
            answer=args.answer,
            note=args.note,
            allow_empty=args.allow_empty,
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
