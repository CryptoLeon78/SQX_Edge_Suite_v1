from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.sqx142_mining_registry import (
    DEFAULT_DB as REGISTRY_DEFAULT_DB,
    connect as registry_connect,
    safe_json,
)


VERSION = "sqx142-capa1-c2-corr2-local-project-integration-v1"
DEPRECATED_PORTFOLIO_ALIAS_VERSION = "sqx142-portfolio-corr2-local-custom-project-integration-v1"
DECISION_DOMAIN = "capa1_c2_template_selection"
DEFAULT_SQX_ROOT = Path(os.environ.get("SQX142_ROOT", "<LOCAL_SQX142_ROOT>"))
LOCAL_ROOT = Path(".local") / "sqx142_portfolio_corr2_local_project_integration"

SOURCE_DATABANK = "Forward"
STABILITY_DATABANK = "SQX EDGE CORR1 STABILITY"
TAGGED_DATABANK = "SQX EDGE CORR1 TAGGED"
VIEW_NAME = "SQX EDGE CORRELATION REVIEW"
STABILITY_TASK_XML = "Retest-Task4.xml"
TAG_TASK_XML = "Retest-Task5.xml"
STABILITY_TASK_TITLE = "CORR1 STABILITY RETEST"
TAG_TASK_TITLE = "CORR1 TAG REVIEW"
CUSTOM_ANALYSIS_ID = "SQXEdgeCorrelationTagger"
REAL_TICK_PRECISION = "4"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_inside(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    root_resolved = root.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"path_outside_root: {resolved}") from exc
    return resolved


def projects_root(sqx_root: Path) -> Path:
    return sqx_root / "user" / "projects"


def project_dir(sqx_root: Path, project_key: str) -> Path:
    if not project_key or any(token in project_key for token in ("..", "/", "\\")):
        raise ValueError("project_key_required")
    return resolve_inside(projects_root(sqx_root) / project_key, projects_root(sqx_root))


def databank_counts(project: Path) -> dict[str, int]:
    root = project / "databanks"
    if not root.is_dir():
        return {}
    return {
        item.name: len(list(item.glob("*.sqx")))
        for item in sorted(root.iterdir(), key=lambda p: p.name.lower())
        if item.is_dir()
    }


def load_cfx(cfx_path: Path) -> dict[str, bytes]:
    if not cfx_path.is_file():
        raise ValueError("project_cfx_missing")
    if not zipfile.is_zipfile(cfx_path):
        raise ValueError("project_cfx_not_zip")
    with zipfile.ZipFile(cfx_path, "r") as archive:
        return {entry.filename: archive.read(entry.filename) for entry in archive.infolist()}


def write_cfx(cfx_path: Path, entries: dict[str, bytes]) -> None:
    tmp_path = cfx_path.with_suffix(".cfx.corr2tmp")
    with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    tmp_path.replace(cfx_path)


def text_entry(entries: dict[str, bytes], name: str) -> str:
    if name not in entries:
        raise ValueError(f"cfx_entry_missing:{name}")
    return entries[name].decode("utf-8", errors="replace")


def parse_xml(text: str) -> ET.Element:
    return ET.fromstring(text)


def first_setup(root: ET.Element) -> ET.Element | None:
    return root.find(".//Setup")


def setup_summary(text: str) -> dict[str, str]:
    try:
        setup = first_setup(parse_xml(text))
    except ET.ParseError:
        setup = None
    if setup is None:
        return {"dateFrom": "", "dateTo": "", "testPrecision": ""}
    return {
        "dateFrom": setup.attrib.get("dateFrom", ""),
        "dateTo": setup.attrib.get("dateTo", ""),
        "testPrecision": setup.attrib.get("testPrecision", ""),
    }


def out_of_sample_summary(text: str) -> list[dict[str, str]]:
    try:
        root = parse_xml(text)
    except ET.ParseError:
        return []
    out = root.find(".//OutOfSample")
    if out is None:
        return []
    return [
        {"dateFrom": item.attrib.get("dateFrom", ""), "dateTo": item.attrib.get("dateTo", "")}
        for item in out.findall("Range")
    ]


def period_plan(entries: dict[str, bytes]) -> dict[str, Any]:
    build = setup_summary(text_entry(entries, "Build-Task1.xml")) if "Build-Task1.xml" in entries else {}
    retest0 = setup_summary(text_entry(entries, "Retest-Task3.xml")) if "Retest-Task3.xml" in entries else {}
    forward = setup_summary(text_entry(entries, "Retest-Task2.xml")) if "Retest-Task2.xml" in entries else {}
    forward_oos = out_of_sample_summary(text_entry(entries, "Retest-Task2.xml")) if "Retest-Task2.xml" in entries else []
    start = build.get("dateFrom") or retest0.get("dateFrom") or forward.get("dateFrom") or ""
    is_to = retest0.get("dateTo") or forward.get("dateFrom") or ""
    end = forward.get("dateTo") or is_to
    oos_from = forward.get("dateFrom") or is_to
    oos_to = end
    if forward_oos:
        oos_from = forward_oos[0].get("dateFrom") or oos_from
        oos_to = forward_oos[-1].get("dateTo") or oos_to
    return {
        "source": {
            "build": build,
            "retest0": retest0,
            "forward": forward,
            "forwardOutOfSample": forward_oos,
        },
        "corr1": {
            "dateFrom": start,
            "dateTo": end,
            "isTo": is_to,
            "oos3From": oos_from,
            "oos3To": oos_to,
            "testPrecision": REAL_TICK_PRECISION,
        },
    }


def set_child_text(parent: ET.Element, tag: str, text: str) -> None:
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag)
    child.text = text


def set_or_create_attrs(parent: ET.Element, tag: str, attrs: dict[str, str]) -> ET.Element:
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag)
    for key, value in attrs.items():
        child.set(key, value)
    return child


def set_databank(root: ET.Element, label: str, value: str) -> None:
    for databank in root.findall(".//Databank"):
        if databank.attrib.get("label") == label:
            databank.set("value", value)
            return
    databanks = root.find(".//Databanks")
    if databanks is None:
        databanks = ET.SubElement(root, "Databanks", {"retestSelected": "false"})
    ET.SubElement(databanks, "Databank", {"label": label, "name": "Output" if label.startswith("Output") else "Input", "value": value})


def retest_task_databanks(text: str) -> dict[str, str]:
    try:
        root = parse_xml(text)
    except ET.ParseError:
        return {"input": "", "output": ""}
    result = {"input": "", "output": ""}
    for databank in root.findall(".//Databank"):
        label = (databank.attrib.get("label") or "").strip().lower()
        name = (databank.attrib.get("name") or "").strip().lower()
        value = databank.attrib.get("value", "")
        if label == "input databank" or name == "input":
            result["input"] = value
        elif label == "output databank" or name == "output":
            result["output"] = value
    return result


def patch_retest_task(base_text: str, *, input_databank: str, output_databank: str, custom_analysis: str, plan: dict[str, Any]) -> str:
    root = parse_xml(base_text)
    corr = plan["corr1"]
    setup = first_setup(root)
    if setup is not None:
        setup.set("dateFrom", corr["dateFrom"])
        setup.set("dateTo", corr["dateTo"])
        setup.set("testPrecision", REAL_TICK_PRECISION)
    out = root.find(".//OutOfSample")
    if out is None:
        out = ET.SubElement(root, "OutOfSample", {"showGraph": "false"})
    for item in list(out):
        out.remove(item)
    if corr.get("oos3From") and corr.get("oos3To"):
        ET.SubElement(out, "Range", {"dateFrom": corr["oos3From"], "dateTo": corr["oos3To"]})
    rankings = root.find(".//Rankings")
    if rankings is not None:
        set_child_text(rankings, "DeleteFailedStrategies", "false")
        set_child_text(rankings, "ForceRunCrossChecks", "false")
        stop = rankings.find("StopCondition")
        if stop is not None:
            stop.set("type", "databank-full")
            stop.set("passedStrategies", "10000")
            stop.set("restartCount", "0")
            stop.set("days", "0")
            stop.set("hours", "0")
            stop.set("minutes", "0")
        set_or_create_attrs(rankings, "FitPortfolio", {"active": "false", "databank": "Existing portfolio"})
        set_or_create_attrs(rankings, "CustomAnalysis", {"method": custom_analysis, "filter": "false", "inputArgs": ""})
    cross_checks = root.find(".//CrossChecks")
    if cross_checks is not None:
        cross_checks.set("use", "false")
        cross_checks.set("evaluateAll", "false")
    set_databank(root, "Input databank", input_databank)
    set_databank(root, "Output databank", output_databank)
    return ET.tostring(root, encoding="unicode")


def patch_config(config_text: str) -> tuple[str, dict[str, Any]]:
    root = parse_xml(config_text)
    tasks = root.find("Tasks")
    if tasks is None:
        tasks = ET.SubElement(root, "Tasks")
    existing_task_files = {task.attrib.get("taskXMLFile"): task for task in tasks.findall("Task")}
    template = next((task for task in tasks.findall("Task") if task.attrib.get("taskXMLFile") == "Retest-Task2.xml"), None)
    planned_tasks = [
        (STABILITY_TASK_XML, STABILITY_TASK_TITLE, "SQX Edge CORR1 Stability Retest"),
        (TAG_TASK_XML, TAG_TASK_TITLE, "SQX Edge CORR1 Tag Review"),
    ]
    task_updates: list[dict[str, str]] = []
    for task_xml, title, name in planned_tasks:
        task = existing_task_files.get(task_xml)
        if task is None:
            attrs = dict(template.attrib) if template is not None else {"type": "Retest", "sampleName": "Custom", "showSettingsOverview": "false"}
            attrs.update({"taskXMLFile": task_xml})
            task = ET.SubElement(tasks, "Task", attrs)
        task.set("type", "Retest")
        task.set("name", name)
        task.set("title", title)
        task.set("active", "true")
        task.set("sampleName", task.attrib.get("sampleName") or "Custom")
        task.set("showSettingsOverview", task.attrib.get("showSettingsOverview") or "false")
        task_updates.append({"taskXMLFile": task_xml, "title": title, "active": "true"})

    databanks = root.find("Databanks")
    if databanks is None:
        databanks = ET.SubElement(root, "Databanks")
    existing_databanks = {item.attrib.get("name"): item for item in databanks.findall("Databank")}
    max_position = 0
    for databank in databanks.findall("Databank"):
        try:
            max_position = max(max_position, int(databank.attrib.get("position", "0")))
        except ValueError:
            pass
    databank_updates: list[dict[str, str]] = []
    for name in (STABILITY_DATABANK, TAGGED_DATABANK):
        databank = existing_databanks.get(name)
        if databank is None:
            max_position += 100
            databank = ET.SubElement(databanks, "Databank", {
                "name": name,
                "view": VIEW_NAME,
                "syncType": "Auto-sync never",
                "position": str(max_position),
            })
        databank.set("view", VIEW_NAME)
        if not databank.attrib.get("syncType"):
            databank.set("syncType", "Auto-sync never")
        databank_updates.append({"name": name, "view": VIEW_NAME})
    return ET.tostring(root, encoding="unicode"), {"taskUpdates": task_updates, "databankUpdates": databank_updates}


def inspect_cfx(cfx_path: Path) -> dict[str, Any]:
    if not cfx_path.is_file():
        return {"exists": False}
    result: dict[str, Any] = {"exists": True, "sha256": sha256_file(cfx_path), "byteSize": cfx_path.stat().st_size}
    try:
        entries = load_cfx(cfx_path)
        result["entryCount"] = len(entries)
        config = parse_xml(text_entry(entries, "config.xml"))
        tasks = []
        for task in config.findall(".//Task"):
            tasks.append({
                "title": task.attrib.get("title", ""),
                "taskXMLFile": task.attrib.get("taskXMLFile", ""),
                "active": task.attrib.get("active", ""),
            })
        databanks = []
        for databank in config.findall(".//Databank"):
            databanks.append({
                "name": databank.attrib.get("name", ""),
                "view": databank.attrib.get("view", ""),
                "position": databank.attrib.get("position", ""),
            })
        result.update({
            "projectName": config.attrib.get("name", ""),
            "tasks": tasks,
            "databanks": databanks,
            "periodPlan": period_plan(entries),
            "corr2Integrated": STABILITY_TASK_XML in entries and TAG_TASK_XML in entries,
            "corr2Tasks": [task for task in tasks if task.get("taskXMLFile") in {STABILITY_TASK_XML, TAG_TASK_XML}],
            "corr2TaskDatabanks": {
                name: retest_task_databanks(text_entry(entries, name))
                for name in (STABILITY_TASK_XML, TAG_TASK_XML)
                if name in entries
            },
        })
    except Exception as exc:
        result["inspectError"] = type(exc).__name__
        result["inspectMessage"] = str(exc)[:200]
    return result


def sqx_process_snapshot(sqx_root: Path) -> dict[str, Any]:
    if os.name != "nt":
        return {"ok": True, "running": False, "processes": [], "platform": os.name}
    root_token = str(sqx_root).replace("\\", "\\\\")
    script = (
        "$root = '" + root_token.replace("'", "''") + "'; "
        "$items = Get-CimInstance Win32_Process | Where-Object { "
        "$_.Name -match 'StrategyQuant|sqcli|CodeEditor|electron|javaw?|SQUANT' -and "
        "((($_.CommandLine -as [string]) -match 'StrategyQuant|SQX|SQUANT') -or (($_.CommandLine -as [string]) -like ('*' + $root + '*'))) "
        "} | Select-Object ProcessId,Name,CommandLine; "
        "$items | ConvertTo-Json -Depth 3"
    )
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            check=False,
            capture_output=True,
            text=True,
            timeout=12,
        )
    except Exception as exc:
        return {"ok": False, "running": True, "error": type(exc).__name__, "processes": []}
    output = (completed.stdout or "").strip()
    processes: list[dict[str, Any]] = []
    if output:
        try:
            parsed = json.loads(output)
            if isinstance(parsed, dict):
                parsed = [parsed]
            for item in parsed if isinstance(parsed, list) else []:
                cmd = str(item.get("CommandLine") or "")
                processes.append({"pid": item.get("ProcessId"), "name": item.get("Name"), "commandLineHash": hashlib.sha256(cmd.encode("utf-8", errors="replace")).hexdigest()[:16]})
        except json.JSONDecodeError:
            processes.append({"pid": None, "name": "unknown", "commandLineHash": hashlib.sha256(output.encode("utf-8", errors="replace")).hexdigest()[:16]})
    return {"ok": completed.returncode == 0, "running": bool(processes), "processes": processes, "privacy": {"raw_command_lines_returned": False}}


def require_sqx_closed(sqx_root: Path, skip: bool = False) -> dict[str, Any]:
    snapshot = sqx_process_snapshot(sqx_root)
    if skip:
        snapshot["skipped"] = True
        return snapshot
    if snapshot.get("running"):
        raise RuntimeError("sqx_runtime_open")
    return snapshot


def backup_project(project: Path, project_key: str) -> tuple[str, Path]:
    backup_id = f"{VERSION}_{utc_stamp()}"
    backup_dir = LOCAL_ROOT / "backups" / backup_id / project_key
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(project / "project.cfx", backup_dir / "project.cfx")
    return backup_id, backup_dir


def record_evidence(name: str, payload: dict[str, Any], backup_id: str | None = None) -> None:
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    if backup_id:
        target = LOCAL_ROOT / "backups" / backup_id / f"{name}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    latest = LOCAL_ROOT / f"latest_{name}.json"
    latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def ensure_databank_folders(project: Path) -> dict[str, int]:
    root = project / "databanks"
    root.mkdir(exist_ok=True)
    result = {}
    for name in (STABILITY_DATABANK, TAGGED_DATABANK):
        target = root / name
        target.mkdir(exist_ok=True)
        result[name] = len(list(target.glob("*.sqx")))
    return result


def patch_cfx(cfx_path: Path) -> dict[str, Any]:
    entries = load_cfx(cfx_path)
    plan = period_plan(entries)
    if "Retest-Task2.xml" not in entries:
        raise ValueError("forward_task_missing")
    forward_text = text_entry(entries, "Retest-Task2.xml")
    entries[STABILITY_TASK_XML] = patch_retest_task(
        forward_text,
        input_databank=SOURCE_DATABANK,
        output_databank=STABILITY_DATABANK,
        custom_analysis="none",
        plan=plan,
    ).encode("utf-8")
    entries[TAG_TASK_XML] = patch_retest_task(
        forward_text,
        input_databank=STABILITY_DATABANK,
        output_databank=TAGGED_DATABANK,
        custom_analysis=CUSTOM_ANALYSIS_ID,
        plan=plan,
    ).encode("utf-8")
    patched_config, config_summary = patch_config(text_entry(entries, "config.xml"))
    entries["config.xml"] = patched_config.encode("utf-8")
    write_cfx(cfx_path, entries)
    return {"config": config_summary, "periodPlan": plan}


def infer_trace(project_key: str) -> dict[str, str]:
    match = re.search(r"(?P<asset>[A-Z]{6})_(?P<tf>M\d+|H\d+|D\d+|W\d+).*?(?P<family>BS_[A-Za-z0-9_]+).*?(?P<layer>Capa\d+)", project_key)
    return {
        "asset": match.group("asset") if match else "",
        "symbol": (match.group("asset") + "_darwinex") if match else "",
        "timeframe": match.group("tf") if match else "",
        "layer": match.group("layer") if match else "unknown",
        "blocksettingFamily": match.group("family") if match else "unknown",
        "direction": "L+S",
        "sqxProfile": "SQX Edge / Darwinex",
    }


def registry_record_corr2(db_path: Path, project_key: str, project: Path, status: str, details: dict[str, Any]) -> None:
    now = now_iso()
    counts = databank_counts(project)
    trace = infer_trace(project_key)
    cfx_status = inspect_cfx(project / "project.cfx")
    task_databanks = cfx_status.get("corr2TaskDatabanks", {}) if isinstance(cfx_status, dict) else {}
    stability_io = task_databanks.get(STABILITY_TASK_XML, {}) if isinstance(task_databanks, dict) else {}
    tag_io = task_databanks.get(TAG_TASK_XML, {}) if isinstance(task_databanks, dict) else {}
    source_databank = stability_io.get("input") or SOURCE_DATABANK
    stability_output = stability_io.get("output") or STABILITY_DATABANK
    tag_input = tag_io.get("input") or STABILITY_DATABANK
    tag_output = tag_io.get("output") or TAGGED_DATABANK
    stability_count = counts.get(stability_output, 0)
    tag_count = counts.get(tag_output, 0)
    if source_databank == "Foward":
        source_databank = "Forward"
    details = dict(details)
    details["version"] = VERSION
    details["deprecatedAliases"] = [DEPRECATED_PORTFOLIO_ALIAS_VERSION]
    details["decisionDomain"] = DECISION_DOMAIN
    details["methodologyRole"] = "Capa1 correlation tasks feed Template C2 selection; Capa2 portfolio correlation remains a separate downstream phase."
    details["actualSourceDatabank"] = source_databank
    details["actualCorr2Databanks"] = {
        "stabilityInput": source_databank,
        "stabilityOutput": stability_output,
        "tagInput": tag_input,
        "tagOutput": tag_output,
    }
    with registry_connect(db_path) as con:
        con.execute(
            """
            INSERT OR IGNORE INTO mining_runs(
                run_key, version, source_type, project_name, sqx_project_name,
                asset, symbol, timeframe, layer, blocksetting_family, direction,
                databank, sqx_profile, source_csv_rows, tagger_csv_rows,
                run_flags_json, data_smoke_json, operator_note, created_at, updated_at
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?, ?, ?)
            """,
            (
                project_key,
                VERSION,
                "sqx142_corr2_local_project_integration",
                project_key,
                project_key,
                trace["asset"],
                trace["symbol"],
                trace["timeframe"],
                trace["layer"],
                trace["blocksettingFamily"],
                trace["direction"],
                source_databank,
                trace["sqxProfile"],
                safe_json({"corr2_local_project_integration": True, "sqx_user_projects_mutation": status == "patched"}),
                safe_json({}),
                "CORR2 local custom project integration",
                now,
                now,
            ),
        )
        run_id = int(con.execute("SELECT id FROM mining_runs WHERE run_key = ?", (project_key,)).fetchone()["id"])
        con.execute(
            """
            INSERT INTO custom_projects(
                project_key, run_id, project_name, sqx_project_name, asset, symbol,
                timeframe, layer, blocksetting_family, direction, sqx_profile,
                trace_json, created_at, updated_at
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_key) DO UPDATE SET
                run_id=excluded.run_id,
                trace_json=excluded.trace_json,
                updated_at=excluded.updated_at
            """,
            (
                project_key,
                run_id,
                project_key,
                project_key,
                trace["asset"],
                trace["symbol"],
                trace["timeframe"],
                trace["layer"],
                trace["blocksettingFamily"],
                trace["direction"],
                trace["sqxProfile"],
                safe_json({"version": VERSION, "deprecatedAliases": [DEPRECATED_PORTFOLIO_ALIAS_VERSION], "projectKey": project_key, "corr2": details, "decisionDomain": DECISION_DOMAIN, "source": "capa1_c2_corr2_local_project_integration"}),
                now,
                now,
            ),
        )
        project_id = int(con.execute("SELECT id FROM custom_projects WHERE project_key = ?", (project_key,)).fetchone()["id"])
        stability_status = "completed" if stability_count > 0 else ("pending_run" if status in {"patched", "operator_confirmed"} else status)
        tag_status = "completed" if tag_count > 0 else ("pending_tagger_csv" if status in {"patched", "operator_confirmed"} else status)
        steps = [
            (90, "capa1_c2_corr2_project_patch", "Capa1 C2 CORR2 local project patch", status, "", STABILITY_DATABANK, None, None, None),
            (91, "capa1_c2_corr1_stability_retest", f"Capa1 C2 CORR1 stability retest from {source_databank}", stability_status, source_databank, stability_output, counts.get(source_databank), stability_count, 0),
            (92, "capa1_c2_corr1_tagger_review", "Capa1 C2 CORR1 tag review", tag_status, tag_input, tag_output, counts.get(tag_input), tag_count, 0),
        ]
        for order, key, label, step_status, input_db, output_db, rows, passed, failed in steps:
            con.execute(
                """
                INSERT INTO custom_project_steps(
                    project_id, step_order, step_key, step_label, status,
                    input_databank, output_databank, row_count, passed_count,
                    failed_count, details_json, evidence_note, recorded_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id, step_key) DO UPDATE SET
                    step_label=excluded.step_label,
                    status=excluded.status,
                    input_databank=excluded.input_databank,
                    output_databank=excluded.output_databank,
                    row_count=excluded.row_count,
                    passed_count=excluded.passed_count,
                    failed_count=excluded.failed_count,
                    details_json=excluded.details_json,
                    evidence_note=excluded.evidence_note,
                    recorded_at=excluded.recorded_at
                """,
                (
                    project_id,
                    order,
                    key,
                    label,
                    step_status,
                    input_db,
                    output_db,
                    rows,
                    passed,
                    failed,
                    safe_json(details),
                    "Capa1 CORR2 local project integration for Template C2 selection; SQX execution remains manual.",
                    now,
                ),
            )
        con.commit()


def build_status(args: argparse.Namespace) -> dict[str, Any]:
    sqx_root = Path(args.sqx_root)
    project = project_dir(sqx_root, args.project_key)
    cfx = project / "project.cfx"
    counts = databank_counts(project)
    cfx_status = inspect_cfx(cfx)
    task_databanks = cfx_status.get("corr2TaskDatabanks", {}) if isinstance(cfx_status, dict) else {}
    stability_io = task_databanks.get(STABILITY_TASK_XML, {}) if isinstance(task_databanks, dict) else {}
    tag_io = task_databanks.get(TAG_TASK_XML, {}) if isinstance(task_databanks, dict) else {}
    actual_source = stability_io.get("input") or SOURCE_DATABANK
    if actual_source == "Foward":
        actual_source = "Forward"
    return {
        "ok": True,
        "version": VERSION,
        "deprecatedAliases": [DEPRECATED_PORTFOLIO_ALIAS_VERSION],
        "decisionDomain": DECISION_DOMAIN,
        "methodologyRole": "Capa1 correlation tasks feed Template C2 selection.",
        "action": "status",
        "projectKey": args.project_key,
        "projectExists": project.is_dir(),
        "cfx": cfx_status,
        "databanks": {
            "Results": counts.get("Results", 0),
            SOURCE_DATABANK: counts.get(SOURCE_DATABANK, 0),
            STABILITY_DATABANK: counts.get(STABILITY_DATABANK, 0),
            TAGGED_DATABANK: counts.get(TAGGED_DATABANK, 0),
        },
        "processGuard": sqx_process_snapshot(sqx_root),
        "expected": {
            "sourceDatabank": SOURCE_DATABANK,
            "stabilityDatabank": STABILITY_DATABANK,
            "taggedDatabank": TAGGED_DATABANK,
            "stabilityTask": STABILITY_TASK_XML,
            "tagTask": TAG_TASK_XML,
            "testPrecision": REAL_TICK_PRECISION,
            "customAnalysis": CUSTOM_ANALYSIS_ID,
        },
        "actual": {
            "sourceDatabank": actual_source,
            "stabilityDatabank": stability_io.get("output") or STABILITY_DATABANK,
            "tagInputDatabank": tag_io.get("input") or STABILITY_DATABANK,
            "taggedDatabank": tag_io.get("output") or TAGGED_DATABANK,
        },
        "privacy": {"local_paths_returned": False},
        "guards": guarded_flags(),
    }


def guarded_flags() -> dict[str, bool]:
    return {
        "sqx_runtime_started_by_script": False,
        "sqx_data_db_write_allowed": False,
        "jars_write_allowed": False,
        "internal_plugins_write_allowed": False,
        "license_activation_write_allowed": False,
        "databank_delete_allowed": False,
        "sqx_project_run_allowed": False,
        "migration_tool_allowed": False,
        "check_resources_allowed": False,
    }


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    status = build_status(args)
    return {
        "ok": True,
        "version": VERSION,
        "deprecatedAliases": [DEPRECATED_PORTFOLIO_ALIAS_VERSION],
        "decisionDomain": DECISION_DOMAIN,
        "methodologyRole": "Capa1 correlation tasks feed Template C2 selection; this is not the Capa2 portfolio decision.",
        "action": "plan",
        "status": status,
        "operations": [
            f"backup {args.project_key}/project.cfx into ignored local evidence",
            f"add active task {STABILITY_TASK_XML} '{STABILITY_TASK_TITLE}' input {SOURCE_DATABANK} output {STABILITY_DATABANK}",
            f"add active task {TAG_TASK_XML} '{TAG_TASK_TITLE}' input {STABILITY_DATABANK} output {TAGGED_DATABANK}",
            f"set both CORR1 tasks to testPrecision={REAL_TICK_PRECISION}, DeleteFailedStrategies=false, FitPortfolio=false and CrossChecks=false",
            "register Capa1 C2 CORR2 patch steps in the SQX Edge mining registry",
        ],
        "rollback": "restore backed-up project.cfx only; databank folders are left in place to avoid deleting evidence",
        "privacy": {"local_paths_returned": False},
        "guards": guarded_flags(),
    }


def apply_integration(args: argparse.Namespace) -> dict[str, Any]:
    sqx_root = Path(args.sqx_root)
    process_guard = require_sqx_closed(sqx_root, skip=bool(getattr(args, "skip_process_guard", False)))
    project = project_dir(sqx_root, args.project_key)
    if not project.is_dir():
        raise ValueError("project_missing")
    cfx_path = project / "project.cfx"
    before = inspect_cfx(cfx_path)
    backup_id, backup_dir = backup_project(project, args.project_key)
    patch = patch_cfx(cfx_path)
    created_databanks = ensure_databank_folders(project)
    after = inspect_cfx(cfx_path)
    details = {
        "backupId": backup_id,
        "beforeSha256": before.get("sha256"),
        "afterSha256": after.get("sha256"),
        "patch": patch,
        "databankFolders": created_databanks,
        "processGuard": process_guard,
    }
    registry_record_corr2(Path(args.db), args.project_key, project, "patched", details)
    result = {
        "ok": True,
        "version": VERSION,
        "deprecatedAliases": [DEPRECATED_PORTFOLIO_ALIAS_VERSION],
        "decisionDomain": DECISION_DOMAIN,
        "action": "apply",
        "projectKey": args.project_key,
        "status": "patched",
        "backupId": backup_id,
        "before": before,
        "after": after,
        "databanks": created_databanks,
        "processGuard": process_guard,
        "privacy": {"local_paths_returned": False},
        "guards": guarded_flags(),
    }
    record_evidence("apply", result, backup_id)
    return result


def rollback_integration(args: argparse.Namespace) -> dict[str, Any]:
    if not args.backup_id:
        raise ValueError("backup_id_required")
    sqx_root = Path(args.sqx_root)
    process_guard = require_sqx_closed(sqx_root, skip=bool(getattr(args, "skip_process_guard", False)))
    project = project_dir(sqx_root, args.project_key)
    backup_project_cfx = LOCAL_ROOT / "backups" / args.backup_id / args.project_key / "project.cfx"
    if not backup_project_cfx.is_file():
        raise ValueError("backup_project_cfx_missing")
    cfx_path = project / "project.cfx"
    current_sha = sha256_file(cfx_path) if cfx_path.is_file() else ""
    shutil.copy2(backup_project_cfx, cfx_path)
    after = inspect_cfx(cfx_path)
    details = {"backupId": args.backup_id, "restoredSha256": after.get("sha256"), "previousSha256": current_sha, "processGuard": process_guard}
    registry_record_corr2(Path(args.db), args.project_key, project, "rolled_back", details)
    result = {
        "ok": True,
        "version": VERSION,
        "deprecatedAliases": [DEPRECATED_PORTFOLIO_ALIAS_VERSION],
        "decisionDomain": DECISION_DOMAIN,
        "action": "rollback",
        "projectKey": args.project_key,
        "status": "rolled_back",
        "backupId": args.backup_id,
        "after": after,
        "databankFoldersLeftInPlace": True,
        "processGuard": process_guard,
        "privacy": {"local_paths_returned": False},
        "guards": guarded_flags(),
    }
    record_evidence("rollback", result, args.backup_id)
    return result


def record_manual_status(args: argparse.Namespace) -> dict[str, Any]:
    sqx_root = Path(args.sqx_root)
    process_guard = require_sqx_closed(sqx_root, skip=bool(getattr(args, "skip_process_guard", False)))
    project = project_dir(sqx_root, args.project_key)
    if not project.is_dir():
        raise ValueError("project_missing")
    status_report = build_status(args)
    details = {
        "operatorManualRunConfirmed": True,
        "status": status_report,
        "processGuard": process_guard,
    }
    registry_record_corr2(Path(args.db), args.project_key, project, "operator_confirmed", details)
    result = {
        "ok": True,
        "version": VERSION,
        "deprecatedAliases": [DEPRECATED_PORTFOLIO_ALIAS_VERSION],
        "decisionDomain": DECISION_DOMAIN,
        "action": "record",
        "projectKey": args.project_key,
        "status": "operator_confirmed",
        "cfx": status_report.get("cfx", {}),
        "databanks": status_report.get("databanks", {}),
        "actual": status_report.get("actual", {}),
        "processGuard": process_guard,
        "privacy": {"local_paths_returned": False},
        "guards": guarded_flags(),
    }
    record_evidence("record", result)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SQX142 CORR2 local custom project integration")
    parser.add_argument("--action", choices=["status", "plan", "apply", "rollback", "record"], default="status")
    parser.add_argument("--sqx-root", default=str(DEFAULT_SQX_ROOT))
    parser.add_argument("--project-key", default="SQX_EDGE_API_FRESH_AUDCAD_H1_Momentum_20260528_090029_Capa1")
    parser.add_argument("--db", default=str(REGISTRY_DEFAULT_DB))
    parser.add_argument("--backup-id", default="")
    parser.add_argument("--skip-process-guard", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.action == "plan":
            result = build_plan(args)
        elif args.action == "apply":
            result = apply_integration(args)
        elif args.action == "rollback":
            result = rollback_integration(args)
        elif args.action == "record":
            result = record_manual_status(args)
        else:
            result = build_status(args)
    except Exception as exc:
        result = {
            "ok": False,
            "version": VERSION,
            "action": args.action,
            "error": type(exc).__name__,
            "message": str(exc),
            "privacy": {"local_paths_returned": False},
            "guards": guarded_flags(),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
