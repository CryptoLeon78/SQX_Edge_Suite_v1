from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
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

    def walk(node: ET.Element, parts: list[str]) -> None:
        if len(values) >= max_values:
            return
        if node.tag in SKIP_SUBTREES and node is not section:
            return
        interesting = bool(node.attrib) or bool((node.text or "").strip())
        if interesting:
            values.append({
                "xmlPath": node_path(parts, node),
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
        "truncated": len(values) >= max_values,
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
        "nextPhase": "phase1",
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
        state = {
            "version": VERSION,
            "updatedAt": now_iso(),
            "currentPhase": "phase0",
            "nextPhase": "phase1",
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

    questionnaire = sub.add_parser("questionnaire")
    questionnaire.add_argument("--task-title", required=True)
    questionnaire.add_argument("--tab", required=True)
    questionnaire.add_argument("--max-values", type=int, default=350)
    questionnaire.add_argument("--write", action="store_true")

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
    if args.command == "questionnaire":
        json_print(build_questionnaire(
            root142,
            project_root,
            task_title_wanted=args.task_title,
            tab=args.tab,
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
