"""
project_generator.py — Orquestador. Toma un mining + plantilla seed y genera un .cfx
listo para SQX, con todos los XMLs internos parametrizados.

Si data.db de SQX está disponible, los costos (spread/swap/commission) se leen de ahí.
Si no, se usa ASSET_DEFAULTS (aproximaciones de Darwinex).
"""
from __future__ import annotations

import os
import shutil
import copy
from datetime import datetime, timezone
from typing import Optional
from xml.etree import ElementTree as ET

from .cfx_editor import CfxEditor
from .blocksettings import apply_blocksetting_to_xml, blocksetting_trace, resolve_blocksetting_entry
from .config_loader import load_manifest
from .plan import Mining
from .sqx_db import SqxDb
from .xml_patcher import RETEST_PERIODS, apply_mining_to_xml, clean_external_paths, patch_dates


_GENERATOR_PROFILE = load_manifest("generator_profiles.json")
_INSTRUMENTS_PROFILE = load_manifest("instruments.json")
CAPA_TASK_MAPS = {
    int(capa): task_map
    for capa, task_map in (_GENERATOR_PROFILE.get("taskPeriodMaps") or {}).items()
}
TRADING_TIME_RANGES = _GENERATOR_PROFILE.get("tradingTimeRanges") or {}
DISABLE_TRADING_TIME_RANGES = {
    int(capa): set(value or [])
    for capa, value in (_GENERATOR_PROFILE.get("disableTradingTimeRanges") or {}).items()
}
CROSS_BROKER_RETESTS = {
    int(capa): value
    for capa, value in (_GENERATOR_PROFILE.get("crossBrokerRetests") or {}).items()
}
ADAPTIVE_SPREAD_STRESS = {
    int(capa): value
    for capa, value in (_GENERATOR_PROFILE.get("adaptiveSpreadStress") or {}).items()
}
CAPA2_NO_EXIT_AFTER_BARS_TASKS = {
    "Build-Task1.xml",
    "Retest-Task1.xml",
    "AutomaticRetest-Task1.xml",
    "AutomaticRetest-Task8.xml",
    "AutomaticRetest-Task3.xml",
    "AutomaticRetest-Task6.xml",
    "AutomaticRetest-Task5.xml",
    "AutomaticRetest-Task4.xml",
    "Optimize-Task1.xml",
    "AutomaticRetest-Task2.xml",
    "Retest-Task2.xml",
}
CAPA2_FASTEST_PRECISION_TASKS = {
    "AutomaticRetest-Task1.xml",
    "AutomaticRetest-Task8.xml",
    "AutomaticRetest-Task3.xml",
    "AutomaticRetest-Task6.xml",
    "AutomaticRetest-Task5.xml",
    "AutomaticRetest-Task4.xml",
    "Optimize-Task1.xml",
}
CAPA2_TICK_PRECISION_TASKS = {
    "AutomaticRetest-Task2.xml",
    "Retest-Task2.xml",
}
CAPA1_TICK_PRECISION_TASKS = {
    "AutomaticRetest-Task2.xml",
    "Retest-Task2.xml",
}
CAPA1_FASTEST_PRECISION_TASKS = {
    "AutomaticRetest-Task1.xml",
    "AutomaticRetest-Task8.xml",
    "AutomaticRetest-Task3.xml",
    "AutomaticRetest-Task6.xml",
    "AutomaticRetest-Task5.xml",
    "AutomaticRetest-Task7.xml",
    "AutomaticRetest-Task4.xml",
}
BROKER_PROFILES = _GENERATOR_PROFILE.get("brokerProfiles") or {}
TARGET_PROFILES = _GENERATOR_PROFILE.get("targetProfiles") or {}
ASSET_DEFAULTS = _INSTRUMENTS_PROFILE.get("assetDefaults") or {}
DEFAULT_BROKER_POSTFIX = (
    _INSTRUMENTS_PROFILE.get("defaultBrokerPostfix")
    or _GENERATOR_PROFILE.get("defaultBrokerPostfix")
    or "_darwinex"
)
DEFAULT_TARGET_PROFILE_ID = "sq_default_exact"
CAPA1_SYNTHETIC_DATABANK = "Synthetic"
CAPA1_FORWARD_DATABANK = "Forward"
CAPA1_CORR1_STABILITY_DATABANK = "SQX EDGE CORR1 STABILITY"
CAPA1_CORR1_TAGGED_DATABANK = "SQX EDGE CORR1 TAGGED"
CAPA1_CORR1_VIEW = "SQX EDGE CORRELATION REVIEW"
CAPA1_CORR1_STABILITY_TASK_XML = "Retest-Task4.xml"
CAPA1_CORR1_TAG_TASK_XML = "Retest-Task5.xml"
CAPA1_CORR1_STABILITY_TASK_TITLE = "CORR1 STABILITY RETEST"
CAPA1_CORR1_TAG_TASK_TITLE = "CORR1 TAG REVIEW"
CAPA1_CORR1_TAGGER = "SQXEdgeCorrelationTagger"
CAPA2_SYNTHETIC_DATABANK = "Synthetic"
CAPA2_FORWARD_DATABANK = "Forward"
CAPA2_RETEST0_OOS_RANGES = [("2023.01.01", "2025.01.01")]
CAPA2_FORWARD_OOS_RANGES = [("2025.01.01", "2026.01.01"), ("2026.01.01", "2026.04.08")]


def _symbol_for_sqx(asset: str, postfix: str = DEFAULT_BROKER_POSTFIX) -> str:
    """Convierte 'XAUUSD' a 'XAUUSD_darwinex' (o el postfix del broker en uso)."""
    return f"{asset}{postfix}"


def _direction_label(direction: str) -> str:
    return {"long": "LONG", "short": "SHORT", "both": "L+S"}.get(direction, (direction or "").upper())


def _trading_window_for(capa: int, timeframe: str) -> Optional[tuple[str, str]]:
    layer = (TRADING_TIME_RANGES.get(f"capa{capa}") or {})
    value = layer.get((timeframe or "").upper())
    if not value or len(value) != 2:
        return None
    return str(value[0]), str(value[1])


def _trading_window_for_file(capa: int, filename: str, timeframe: str) -> Optional[tuple[str, str]]:
    if filename in (DISABLE_TRADING_TIME_RANGES.get(capa) or set()):
        return None
    return _trading_window_for(capa, timeframe)


def _spread_stress_for(capa: int, filename: str) -> Optional[tuple[float, float]]:
    layer = ADAPTIVE_SPREAD_STRESS.get(capa) or {}
    value = layer.get(filename)
    if not isinstance(value, dict):
        return None
    try:
        min_multiplier = float(value.get("minMultiplier"))
        max_multiplier = float(value.get("maxMultiplier"))
    except (TypeError, ValueError):
        return None
    if min_multiplier <= 0 or max_multiplier <= 0 or min_multiplier > max_multiplier:
        return None
    return min_multiplier, max_multiplier


def _backtest_precision_for_file(capa: int, filename: str) -> str:
    if capa == 1 and filename in CAPA1_FASTEST_PRECISION_TASKS:
        return "1"
    if capa == 1 and filename in CAPA1_TICK_PRECISION_TASKS:
        return "4"
    if capa == 2 and filename in CAPA2_FASTEST_PRECISION_TASKS:
        return "1"
    if capa == 2 and filename in CAPA2_TICK_PRECISION_TASKS:
        return "4"
    return "2"


def _epoch_ms_to_profile_date(value) -> Optional[str]:
    try:
        millis = int(value)
    except (TypeError, ValueError):
        return None
    if millis <= 0:
        return None
    return datetime.fromtimestamp(millis / 1000, tz=timezone.utc).strftime("%Y.%m.%d")


def _profile_date_to_epoch_ms(value: str) -> Optional[int]:
    try:
        dt = datetime.strptime(str(value), "%Y.%m.%d").replace(tzinfo=timezone.utc)
        return int(dt.timestamp() * 1000)
    except Exception:
        return None


def _bound_retest_period_to_available_data(
    period: tuple[str, str],
    resource: dict,
    *,
    min_coverage_days: int = 730,
) -> tuple[str, str]:
    """Clamp a cross-broker retest to real local data when SQX data starts later.

    This is only used when `data.db` evidence is available. It preserves the
    protected historical retest concept, but avoids asking SQX for years of data
    that the local Data Manager does not contain.
    """
    if not resource or resource.get("source") != "db":
        return period
    if resource.get("data_available") is False:
        raise ValueError(f"Cross-broker retest has no loaded data rows for {resource.get('symbol')}")
    data_from = _profile_date_to_epoch_ms(_epoch_ms_to_profile_date(resource.get("date_from_ms")) or "")
    data_to = _profile_date_to_epoch_ms(_epoch_ms_to_profile_date(resource.get("date_to_ms")) or "")
    period_from = _profile_date_to_epoch_ms(period[0])
    period_to = _profile_date_to_epoch_ms(period[1])
    if data_from is None or data_to is None or period_from is None or period_to is None:
        return period
    bounded_from = max(period_from, data_from)
    bounded_to = min(period_to, data_to)
    if bounded_from >= bounded_to:
        raise ValueError(f"Cross-broker retest data range does not overlap requested period for {resource.get('symbol')}")
    coverage_days = (bounded_to - bounded_from) // (24 * 60 * 60 * 1000)
    if coverage_days < min_coverage_days:
        raise ValueError(
            f"Cross-broker retest coverage for {resource.get('symbol')} is {coverage_days} days, "
            f"below minimum {min_coverage_days}"
        )
    return (
        datetime.fromtimestamp(bounded_from / 1000, tz=timezone.utc).strftime("%Y.%m.%d"),
        datetime.fromtimestamp(bounded_to / 1000, tz=timezone.utc).strftime("%Y.%m.%d"),
    )


def _build_task_title(blocksetting_id: str, capa: int, direction: str, timeframe: str) -> str:
    tf = (timeframe or "TF").upper()
    return f"Build {blocksetting_id} · Capa{capa} {_direction_label(direction)} {tf}"


def _disable_exit_after_bars(root) -> int:
    patched = 0
    for block in root.findall(".//ExitTypes/Block[@key='ExitAfterBars.ExitAfterBars']"):
        if block.get("use") != "false":
            block.set("use", "false")
            patched += 1
    return patched


def _set_task_databank(root, label: str, value: str) -> None:
    for databank in root.findall(".//Databank"):
        if databank.get("label") == label:
            databank.set("value", value)
            return
    databanks = root.find(".//Databanks")
    if databanks is None:
        databanks = ET.SubElement(root, "Databanks", {"retestSelected": "false"})
    ET.SubElement(
        databanks,
        "Databank",
        {
            "label": label,
            "name": "Output" if label.startswith("Output") else "Input",
            "value": value,
        },
    )


def _set_strategy_source_databank(root, value: str) -> None:
    strategy_type = root.find(".//WhatToBuild/StrategyType")
    if strategy_type is not None:
        strategy_type.set("improveDatabank", value)


def _set_custom_analysis(root, method: str, *, filter_results: str = "false") -> None:
    rankings = root.find(".//Rankings")
    if rankings is None:
        return
    custom_analysis = rankings.find("CustomAnalysis")
    if custom_analysis is None:
        custom_analysis = ET.SubElement(rankings, "CustomAnalysis")
    custom_analysis.set("method", method)
    custom_analysis.set("filter", filter_results)
    custom_analysis.set("inputArgs", custom_analysis.get("inputArgs") or "")


def _disable_retest_cross_selection(root, *, delete_failed_value: str = "false") -> None:
    rankings = root.find(".//Rankings")
    if rankings is not None:
        delete_failed = rankings.find("DeleteFailedStrategies")
        if delete_failed is not None:
            delete_failed.text = delete_failed_value
        force_cross = rankings.find("ForceRunCrossChecks")
        if force_cross is not None:
            force_cross.text = "false"
        fit_portfolio = rankings.find("FitPortfolio")
        if fit_portfolio is None:
            fit_portfolio = ET.SubElement(rankings, "FitPortfolio")
        fit_portfolio.set("active", "false")
        fit_portfolio.set("databank", fit_portfolio.get("databank") or "Existing portfolio")
    cross_checks = root.find(".//CrossChecks")
    if cross_checks is not None:
        cross_checks.set("use", "false")
        cross_checks.set("evaluateAll", "false")


def _set_oos_ranges(root, ranges: list[tuple[str, str]]) -> None:
    out = root.find(".//OutOfSample")
    if out is None:
        out = ET.SubElement(root, "OutOfSample", {"showGraph": "false"})
    for child in list(out):
        out.remove(child)
    for start, end in ranges:
        ET.SubElement(out, "Range", {"dateFrom": start, "dateTo": end})


def _rename_config_databank(config_root, old: str, new: str) -> None:
    for databank in config_root.findall(".//Databank"):
        if databank.get("name") == old:
            databank.set("name", new)


def _ensure_config_databank(config_root, name: str, view: str) -> None:
    databanks = config_root.find("Databanks")
    if databanks is None:
        databanks = ET.SubElement(config_root, "Databanks")
    existing = {item.get("name"): item for item in databanks.findall("Databank")}
    if name in existing:
        existing[name].set("view", view)
        if not existing[name].get("syncType"):
            existing[name].set("syncType", "Auto-sync never")
        return
    max_position = 0
    for item in databanks.findall("Databank"):
        try:
            max_position = max(max_position, int(item.get("position", "0")))
        except ValueError:
            pass
    ET.SubElement(
        databanks,
        "Databank",
        {
            "name": name,
            "view": view,
            "syncType": "Auto-sync never",
            "position": str(max_position + 100),
        },
    )


def _ensure_config_task(config_root, task_xml: str, title: str, name: str) -> None:
    tasks = config_root.find("Tasks")
    if tasks is None:
        tasks = ET.SubElement(config_root, "Tasks")
    existing = {task.get("taskXMLFile"): task for task in tasks.findall("Task")}
    template = existing.get("Retest-Task2.xml")
    task = existing.get(task_xml)
    if task is None:
        attrs = dict(template.attrib) if template is not None else {
            "type": "Retest",
            "sampleName": "Custom",
            "showSettingsOverview": "false",
        }
        attrs["taskXMLFile"] = task_xml
        task = ET.SubElement(tasks, "Task", attrs)
    task.set("type", "Retest")
    task.set("name", name)
    task.set("title", title)
    task.set("active", "true")
    task.set("sampleName", task.get("sampleName") or "Custom")
    task.set("showSettingsOverview", task.get("showSettingsOverview") or "false")


def _setup_summary_from_task(root) -> dict[str, str]:
    setup = root.find(".//Setup")
    return {
        "dateFrom": setup.get("dateFrom", "") if setup is not None else "",
        "dateTo": setup.get("dateTo", "") if setup is not None else "",
        "testPrecision": setup.get("testPrecision", "") if setup is not None else "",
    }


def _build_corr1_task(forward_tree, *, input_databank: str, output_databank: str, method: str, plan: dict[str, str]):
    root = copy.deepcopy(forward_tree.getroot())
    setup = root.find(".//Setup")
    if setup is not None:
        setup.set("dateFrom", plan["dateFrom"])
        setup.set("dateTo", plan["dateTo"])
        setup.set("testPrecision", "4")
    _set_oos_ranges(root, [(plan["oos3From"], plan["oos3To"])])
    _set_task_databank(root, "Input databank", input_databank)
    _set_task_databank(root, "Output databank", output_databank)
    _set_strategy_source_databank(root, input_databank)
    _set_custom_analysis(root, method)
    _disable_retest_cross_selection(root)
    return ET.ElementTree(root)


def _apply_capa1_registered_pipeline_contract(editor: CfxEditor) -> None:
    """Apply the post-FEATURES5/CORR2 Capa1 chain to generated customs.

    The base SQX template still carries older labels such as Syntetic/Foward.
    Generated Capa1 projects should expose the corrected operator-facing chain:
    Synthetic -> SPP -> WFM -> Forward, then active CORR1 readback tasks.
    """
    task_io = {
        "AutomaticRetest-Task5.xml": ("Monkey Test", CAPA1_SYNTHETIC_DATABANK),
        "AutomaticRetest-Task7.xml": (CAPA1_SYNTHETIC_DATABANK, "SPP"),
        "AutomaticRetest-Task4.xml": ("SPP", "WFM"),
        "Retest-Task2.xml": ("WFM", CAPA1_FORWARD_DATABANK),
    }
    for filename, (input_databank, output_databank) in task_io.items():
        if not editor.has(filename):
            continue
        tree = editor.parse_xml(filename)
        root = tree.getroot()
        _set_task_databank(root, "Input databank", input_databank)
        _set_task_databank(root, "Output databank", output_databank)
        _set_strategy_source_databank(root, input_databank)
        if filename == "Retest-Task2.xml":
            _set_custom_analysis(root, "none")
            _disable_retest_cross_selection(root)
        editor.update_xml(filename, tree)

    if not editor.has("config.xml") or not editor.has("Retest-Task2.xml"):
        return
    forward_tree = editor.parse_xml("Retest-Task2.xml")
    build_summary = _setup_summary_from_task(editor.parse_xml("Build-Task1.xml").getroot()) if editor.has("Build-Task1.xml") else {}
    retest0_summary = _setup_summary_from_task(editor.parse_xml("Retest-Task3.xml").getroot()) if editor.has("Retest-Task3.xml") else {}
    forward_summary = _setup_summary_from_task(forward_tree.getroot())
    plan = {
        "dateFrom": build_summary.get("dateFrom") or retest0_summary.get("dateFrom") or "2017.10.02",
        "dateTo": forward_summary.get("dateTo") or "2026.04.08",
        "oos3From": forward_summary.get("dateFrom") or "2025.01.01",
        "oos3To": forward_summary.get("dateTo") or "2026.04.08",
    }
    editor.update_xml(
        CAPA1_CORR1_STABILITY_TASK_XML,
        _build_corr1_task(
            forward_tree,
            input_databank=CAPA1_FORWARD_DATABANK,
            output_databank=CAPA1_CORR1_STABILITY_DATABANK,
            method="none",
            plan=plan,
        ),
    )
    editor.update_xml(
        CAPA1_CORR1_TAG_TASK_XML,
        _build_corr1_task(
            forward_tree,
            input_databank=CAPA1_CORR1_STABILITY_DATABANK,
            output_databank=CAPA1_CORR1_TAGGED_DATABANK,
            method=CAPA1_CORR1_TAGGER,
            plan=plan,
        ),
    )

    config_tree = editor.parse_xml("config.xml")
    config_root = config_tree.getroot()
    _rename_config_databank(config_root, "Syntetic", CAPA1_SYNTHETIC_DATABANK)
    _rename_config_databank(config_root, "Foward", CAPA1_FORWARD_DATABANK)
    for task in config_root.findall(".//Task"):
        task_xml = task.get("taskXMLFile")
        if task_xml == "AutomaticRetest-Task5.xml":
            task.set("title", "Synthetic")
        elif task_xml == "Retest-Task2.xml":
            task.set("title", "Forward")
    _ensure_config_databank(config_root, CAPA1_CORR1_STABILITY_DATABANK, CAPA1_CORR1_VIEW)
    _ensure_config_databank(config_root, CAPA1_CORR1_TAGGED_DATABANK, CAPA1_CORR1_VIEW)
    _ensure_config_task(
        config_root,
        CAPA1_CORR1_STABILITY_TASK_XML,
        CAPA1_CORR1_STABILITY_TASK_TITLE,
        "SQX Edge CORR1 Stability Retest",
    )
    _ensure_config_task(
        config_root,
        CAPA1_CORR1_TAG_TASK_XML,
        CAPA1_CORR1_TAG_TASK_TITLE,
        "SQX Edge CORR1 Tag Review",
    )
    editor.update_xml("config.xml", config_tree)


def _apply_capa2_registered_pipeline_contract(editor: CfxEditor) -> None:
    """Apply the active Capa2 chain confirmed from the Capa1 success path.

    Capa2 inherits the validated Capa1 temporal partition for Build, Retest 0,
    Retest 1 and Forward. Robustness tasks keep the 2017.10.02-2023.12.31
    robustness window, but the final Forward/OOS ranges must match the Capa1
    winner that generated the Template C2.
    """
    task_io = {
        "AutomaticRetest-Task5.xml": ("Monkey Test", CAPA2_SYNTHETIC_DATABANK),
        "AutomaticRetest-Task4.xml": (CAPA2_SYNTHETIC_DATABANK, "SPP"),
        "Optimize-Task1.xml": ("SPP", "WFM"),
        "Retest-Task2.xml": ("WFM", CAPA2_FORWARD_DATABANK),
    }
    for filename, (input_databank, output_databank) in task_io.items():
        if not editor.has(filename):
            continue
        tree = editor.parse_xml(filename)
        root = tree.getroot()
        _set_task_databank(root, "Input databank", input_databank)
        _set_task_databank(root, "Output databank", output_databank)
        _set_strategy_source_databank(root, input_databank)
        if filename == "Retest-Task2.xml":
            _set_custom_analysis(root, "none")
            _disable_retest_cross_selection(root, delete_failed_value="true")
            _set_oos_ranges(root, CAPA2_FORWARD_OOS_RANGES)
        editor.update_xml(filename, tree)

    if editor.has("Retest-Task1.xml"):
        retest0_tree = editor.parse_xml("Retest-Task1.xml")
        _set_oos_ranges(retest0_tree.getroot(), CAPA2_RETEST0_OOS_RANGES)
        editor.update_xml("Retest-Task1.xml", retest0_tree)

    if not editor.has("config.xml"):
        return
    config_tree = editor.parse_xml("config.xml")
    config_root = config_tree.getroot()
    _rename_config_databank(config_root, "Syntetic", CAPA2_SYNTHETIC_DATABANK)
    _rename_config_databank(config_root, "Foward", CAPA2_FORWARD_DATABANK)
    _ensure_config_databank(config_root, CAPA2_SYNTHETIC_DATABANK, "MC SYNTHETIC RETEST")
    _ensure_config_databank(config_root, CAPA2_FORWARD_DATABANK, "RETEST QUICK REVIEW")
    for task in config_root.findall(".//Task"):
        task_xml = task.get("taskXMLFile")
        if task_xml == "AutomaticRetest-Task5.xml":
            task.set("title", "Synthetic")
        elif task_xml == "Retest-Task2.xml":
            task.set("title", "Forward")
    editor.update_xml("config.xml", config_tree)


def _clean_profile_value(value, default=None):
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _int_profile_value(value, default=None):
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _profile_from_broker(profile_id: str | None) -> dict:
    raw = BROKER_PROFILES.get(profile_id or "") or {}
    return {
        "brokerProfile": raw.get("id") or profile_id or "",
        "brokerPostfix": raw.get("brokerPostfix"),
        "brokerId": raw.get("brokerId"),
        "sourceId": raw.get("sourceId"),
        "inheritInstrumentFromData": raw.get("inheritInstrumentFromData"),
        "brokerName": raw.get("brokerName"),
        "brokerDescription": raw.get("brokerDescription"),
        "timezone": raw.get("timezone"),
        "precision": raw.get("precision") or "TICK",
        "stripCustomBlockResources": raw.get("stripCustomBlockResources"),
        "stripInstrumentResources": raw.get("stripInstrumentResources"),
        "label": raw.get("label") or profile_id or "",
    }


def _format_symbol_template(template: str | None, asset: str) -> str | None:
    if not template:
        return None
    try:
        return str(template).format(asset=asset, assetUpper=(asset or "").upper(), assetLower=(asset or "").lower())
    except Exception:
        return str(template)


def normalize_target_profile(target_profile=None, broker_postfix: str = DEFAULT_BROKER_POSTFIX) -> dict:
    """Resolve a generation target profile into the fields used by XML patching.

    The public UI can send either a profile id or `{id, custom}`. Custom mode is
    intentionally conservative: it remaps symbols only with explicit broker
    fields supplied by the operator/user; otherwise it falls back to the SQX Edge
    Darwinex server profile.
    """
    raw = target_profile or DEFAULT_TARGET_PROFILE_ID
    if isinstance(raw, str):
        profile_id = raw or DEFAULT_TARGET_PROFILE_ID
        custom = {}
    elif isinstance(raw, dict):
        profile_id = str(raw.get("id") or raw.get("profile") or DEFAULT_TARGET_PROFILE_ID)
        custom = raw.get("custom") if isinstance(raw.get("custom"), dict) else raw
        if profile_id not in TARGET_PROFILES and (
            raw.get("brokerProfile") or raw.get("brokerPostfix") or raw.get("brokerId") or raw.get("sourceId")
        ):
            broker_profile_id = str(raw.get("brokerProfile") or raw.get("id") or "")
            direct = _profile_from_broker(broker_profile_id)
            direct.update({
                "id": profile_id,
                "label": raw.get("label") or direct.get("label") or profile_id,
                "mode": raw.get("mode") or "direct_profile",
                "warning": raw.get("warning") or "",
            })
            for key in (
                "brokerPostfix",
                "brokerId",
                "sourceId",
                "brokerName",
                "brokerDescription",
                "timezone",
                "precision",
                "symbol",
                "dataType",
                "stripCustomBlockResources",
                "stripInstrumentResources",
            ):
                if raw.get(key) is not None:
                    direct[key] = raw.get(key)
            if raw.get("brokerName") and not raw.get("brokerDescription"):
                direct["brokerDescription"] = _clean_profile_value(raw.get("brokerName"), "User broker")
            if not direct.get("timezone"):
                direct["timezone"] = "EETUS"
            if not direct.get("precision"):
                direct["precision"] = "TICK"
            return direct
    else:
        profile_id = DEFAULT_TARGET_PROFILE_ID
        custom = {}

    profile = dict(TARGET_PROFILES.get(profile_id) or TARGET_PROFILES.get(DEFAULT_TARGET_PROFILE_ID) or {})
    broker_profile_id = str(profile.get("brokerProfile") or "darwinex")
    resolved = _profile_from_broker(broker_profile_id)
    resolved.update({
        "id": profile.get("id") or profile_id,
        "label": profile.get("label") or resolved.get("label") or profile_id,
        "mode": profile.get("mode") or "server_default",
        "warning": profile.get("warning") or "",
    })
    for key in (
        "brokerPostfix",
        "brokerId",
        "sourceId",
        "brokerName",
        "brokerDescription",
        "timezone",
        "precision",
        "dataType",
        "symbol",
        "symbolTemplate",
        "forceExactSymbol",
        "stripCustomBlockResources",
        "stripInstrumentResources",
    ):
        if profile.get(key) is not None:
            resolved[key] = profile.get(key)

    if resolved["id"] == "custom_user_broker":
        custom_postfix = _clean_profile_value(custom.get("brokerPostfix") or custom.get("postfix"))
        custom_symbol = _clean_profile_value(custom.get("symbol"))
        if custom_postfix is not None:
            resolved["brokerPostfix"] = custom_postfix
        if custom_symbol is not None:
            resolved["symbol"] = custom_symbol
        for key, source_key in (("brokerId", "brokerId"), ("sourceId", "sourceId")):
            value = _int_profile_value(custom.get(source_key))
            if value is not None:
                resolved[key] = value
        for key, source_key in (
            ("brokerName", "brokerName"),
            ("brokerDescription", "brokerDescription"),
            ("timezone", "timezone"),
            ("precision", "precision"),
        ):
            value = _clean_profile_value(custom.get(source_key))
            if value is not None:
                resolved[key] = value
        if custom.get("brokerName") and not custom.get("brokerDescription"):
            resolved["brokerDescription"] = _clean_profile_value(custom.get("brokerName"), "User broker")

    if resolved.get("brokerPostfix") is None:
        resolved["brokerPostfix"] = broker_postfix
    if not resolved.get("brokerPostfix") and not resolved.get("symbol"):
        resolved["brokerPostfix"] = broker_postfix
    if not resolved.get("timezone"):
        resolved["timezone"] = "EETUS"
    if not resolved.get("precision"):
        resolved["precision"] = "TICK"
    return resolved


def public_target_profile(profile: dict) -> dict:
    data = profile or {}
    return {
        "id": data.get("id"),
        "label": data.get("label"),
        "mode": data.get("mode"),
        "brokerPostfix": data.get("brokerPostfix"),
        "brokerId": data.get("brokerId"),
        "sourceId": data.get("sourceId"),
        "symbol": data.get("symbol"),
        "symbolTemplate": data.get("symbolTemplate"),
        "forceExactSymbol": bool(data.get("forceExactSymbol")),
        "stripCustomBlockResources": bool(data.get("stripCustomBlockResources")),
        "stripInstrumentResources": bool(data.get("stripInstrumentResources")),
        "dataType": data.get("dataType"),
        "warning": data.get("warning"),
    }


def _cross_broker_retest(capa: int, filename: str) -> Optional[dict]:
    layer = CROSS_BROKER_RETESTS.get(capa) or {}
    value = layer.get(filename)
    return value if isinstance(value, dict) else None


_EXECUTION_RESOURCE_KEYS = {
    "instrument",
    "spread",
    "slippage",
    "swap_long",
    "swap_short",
    "swap_type",
    "commission_type",
    "commission_value",
    "broker_postfix",
    "broker_id",
    "broker_name",
    "broker_description",
    "broker_timezone",
    "data_type",
    "tick_size",
    "tick_step",
    "point_value",
    "description",
    "min_distance",
    "commissions_xml",
    "swap_xml",
    "exchange",
    "country",
    "sector",
    "ordersize_multiplier",
    "ordersize_step",
}


def _apply_cross_broker_execution_profile(
    cross_costs: dict,
    target_costs: dict,
    cross_retest: dict,
    resolved_target_profile: dict,
) -> dict:
    """Keep cross-broker bars while matching the target execution resource.

    Some SQX 142 installations store Dukascopy OOS bars as
    `SYMBOL={asset}_dukascopy` but keep the executable instrument/broker as the
    Darwinex profile. The generator must preserve the data vendor source while
    avoiding a pure broker-3 resource when the selected target profile is
    Darwinex.
    """
    mapping = cross_retest.get("executionBrokerProfileForTargets")
    if not isinstance(mapping, dict):
        return cross_costs
    target_id = str((resolved_target_profile or {}).get("id") or "")
    expected_profile_id = mapping.get(target_id)
    if not expected_profile_id:
        return cross_costs
    if not target_costs or str(target_costs.get("broker_id")) in ("", "-1", "None"):
        return cross_costs

    patched = dict(cross_costs)
    data_symbol = patched.get("symbol")
    data_source_id = patched.get("source_id")
    data_source_db = patched.get("source")
    coverage = {
        key: patched.get(key)
        for key in ("date_from_ms", "date_to_ms", "rows", "data_available", "data_rows")
    }
    target_profile_public = patched.get("target_profile")

    for key in _EXECUTION_RESOURCE_KEYS:
        value = target_costs.get(key)
        if value is not None:
            patched[key] = value

    if data_symbol:
        patched["symbol"] = data_symbol
    if data_source_id is not None:
        patched["source_id"] = data_source_id
    patched["source"] = data_source_db or patched.get("source")
    for key, value in coverage.items():
        if value is not None:
            patched[key] = value
    if target_profile_public is not None:
        patched["target_profile"] = target_profile_public
    patched["execution_profile"] = expected_profile_id
    return patched


def _fallback_market_shape(asset: str) -> dict:
    token = (asset or "").upper()
    if token.startswith("XAU"):
        return {"tick_size": 0.01, "tick_step": 0.01, "point_value": 100.0, "sector": "Commodities", "data_type": 4}
    if len(token) == 6 and token.isalpha():
        is_jpy = token.endswith("JPY")
        return {
            "tick_size": 0.01 if is_jpy else 0.0001,
            "tick_step": 0.001 if is_jpy else 0.00001,
            "point_value": 1000.0 if is_jpy else 100000.0,
            "sector": "Currency",
            "data_type": 3,
        }
    return {"tick_size": 0.01, "tick_step": 0.01, "point_value": 1.0, "sector": "", "data_type": 3}


def resolve_costs(
    mining: Mining,
    sqx_db_path: Optional[str],
    postfix: str = DEFAULT_BROKER_POSTFIX,
    alias_override: Optional[dict] = None,
    target_profile: Optional[dict] = None,
) -> dict:
    """
    Resuelve costos REALES por mining: lee data.db si está disponible, si no usa
    ASSET_DEFAULTS.

    Args:
        mining: Mining del plan
        sqx_db_path: ruta a data.db (None = usa fallback directo)
        postfix: sufijo de broker para construir el symbol final
        alias_override: dict {asset: instrument} para sobreescribir defaults

    Devuelve dict con: source, spread, swap_long, swap_short, swap_type,
    commission_type, commission_value, instrument, symbol.
    """
    profile = normalize_target_profile(target_profile, postfix) if target_profile else normalize_target_profile(
        DEFAULT_TARGET_PROFILE_ID,
        postfix,
    )
    force_exact_symbol = bool(profile.get("forceExactSymbol"))
    profile_postfix = profile.get("brokerPostfix")
    postfix = "" if force_exact_symbol and profile_postfix == "" else (profile_postfix if profile_postfix is not None else (postfix or ""))
    explicit_symbol = profile.get("symbol") or _format_symbol_template(profile.get("symbolTemplate"), mining.asset)

    # 1) Intentar data.db
    if sqx_db_path and os.path.isfile(sqx_db_path):
        try:
            db = SqxDb(sqx_db_path)
            try:
                info = db.get_symbol_info(
                    mining.asset,
                    alias_override=alias_override,
                    preferred_postfix=postfix,
                    inherit_data_instrument=bool(profile.get("inheritInstrumentFromData")),
                )
                if info.get("source") == "db":
                    inherited_instrument = bool(info.get("data_instrument_inherited"))
                    pf = postfix if force_exact_symbol and not inherited_instrument else (info.get("broker_postfix") or postfix or "")
                    use_profile_broker = force_exact_symbol or (
                        profile.get("id") == "custom_user_broker" and profile.get("brokerId") is not None
                    )
                    broker_id = profile.get("brokerId") if use_profile_broker and not inherited_instrument else info.get("broker_id")
                    source_id = profile.get("sourceId")
                    broker_name = info.get("broker_name") if inherited_instrument else (profile.get("brokerName") or info.get("broker_name"))
                    broker_description = info.get("broker_description") if inherited_instrument else (profile.get("brokerDescription") or info.get("broker_description"))
                    broker_timezone = info.get("broker_timezone") if inherited_instrument else (profile.get("timezone") or info.get("broker_timezone") or "EETUS")
                    resolved_symbol = explicit_symbol or info.get("data_symbol") or (_symbol_for_sqx(info["instrument"], pf) if pf else info["instrument"])
                    resolved_instrument = resolved_symbol if force_exact_symbol else info["instrument"]
                    profile_data_type = profile.get("dataType")
                    return {
                        "source": "db",
                        "instrument": resolved_instrument,
                        "symbol": resolved_symbol,
                        "spread": info.get("spread"),
                        "slippage": info.get("slippage"),
                        "swap_long": info.get("swap_long") if info.get("swap_long") is not None else 0.0,
                        "swap_short": info.get("swap_short") if info.get("swap_short") is not None else 0.0,
                        "swap_type": info.get("swap_type"),
                        "commission_type": info.get("commission_type"),
                        "commission_value": info.get("commission_value"),
                        "broker_postfix": pf,
                        "broker_id": broker_id,
                        "source_id": source_id,
                        "broker_name": broker_name,
                        "broker_description": broker_description,
                        "broker_timezone": broker_timezone,
                        "target_profile": public_target_profile(profile),
                        "data_type": profile_data_type if profile_data_type is not None else info.get("data_type"),
                        "tick_size": info.get("tick_size"),
                        "tick_step": info.get("tick_step"),
                        "point_value": info.get("point_value"),
                        "description": info.get("description"),
                        "min_distance": info.get("min_distance"),
                        "commissions_xml": info.get("commissions_xml"),
                        "swap_xml": info.get("swap_xml"),
                        "date_from_ms": info.get("date_from_ms"),
                        "date_to_ms": info.get("date_to_ms"),
                        "rows": info.get("rows"),
                        "u_symbol": info.get("u_symbol"),
                        "u_symbol_name": info.get("u_symbol_name"),
                        "exchange": info.get("exchange"),
                        "country": info.get("country"),
                        "sector": info.get("sector"),
                        "ordersize_multiplier": info.get("ordersize_multiplier"),
                        "ordersize_step": info.get("ordersize_step"),
                        "data_available": bool(info.get("rows") and int(info.get("rows") or 0) > 0),
                        "data_rows": info.get("rows"),
                    }
            finally:
                db.close()
        except Exception:
            pass  # caer a fallback

    # 2) Fallback a ASSET_DEFAULTS
    d = ASSET_DEFAULTS.get(mining.asset, {"spread": 10, "swap_long": -1.0, "swap_short": -1.0})
    shape = _fallback_market_shape(mining.asset)
    fallback_symbol = explicit_symbol or (_symbol_for_sqx(mining.asset, postfix) if postfix else mining.asset)
    fallback_instrument = fallback_symbol if (force_exact_symbol or postfix) else mining.asset
    return {
        "source": "fallback",
        "instrument": fallback_instrument,
        "symbol": fallback_symbol,
        "spread": d["spread"],
        "slippage": 0,
        "swap_long": d["swap_long"],
        "swap_short": d["swap_short"],
        "swap_type": None,
        "commission_type": d.get("commission_type", "SizeBased") if isinstance(d, dict) else "SizeBased",
        "commission_value": d.get("commission_value", 0.0) if isinstance(d, dict) else 0.0,
        "broker_postfix": postfix,
        "broker_id": profile.get("brokerId"),
        "source_id": profile.get("sourceId"),
        "broker_name": profile.get("brokerName"),
        "broker_description": profile.get("brokerDescription"),
        "broker_timezone": profile.get("timezone"),
        "target_profile": public_target_profile(profile),
        "data_type": profile.get("dataType") if profile.get("dataType") is not None else shape["data_type"],
        "tick_size": shape["tick_size"],
        "tick_step": shape["tick_step"],
        "point_value": shape["point_value"],
        "description": d.get("description") if isinstance(d, dict) and d.get("description") else mining.asset,
        "min_distance": 0,
        "commissions_xml": None,
        "swap_xml": None,
        "date_from_ms": None,
        "date_to_ms": None,
        "rows": None,
        "u_symbol": mining.asset,
        "u_symbol_name": mining.asset,
        "exchange": "",
        "country": "",
        "sector": shape["sector"],
        "ordersize_multiplier": 1.0,
        "ordersize_step": 0.01,
        "data_available": False,
        "data_rows": None,
    }


def generate_project(
    mining: Mining,
    template_path: str,
    output_dir: str,
    capa: int = 1,
    suffix: str = "",
    sqx_data: Optional[dict] = None,
    sqx_db_path: Optional[str] = None,
    broker_postfix: str = DEFAULT_BROKER_POSTFIX,
    alias_override: Optional[dict] = None,
    overwrite: bool = True,
    project_name: Optional[str] = None,
    blocksetting_capa2: Optional[str] = None,
    target_profile: Optional[dict] = None,
) -> str:
    """
    Genera un .cfx para el mining especificado.

    Args:
        mining: instancia Mining del plan
        template_path: path al .cfx seed (Capa1_Long.cfx o Capa2_Base.cfx)
        output_dir: carpeta donde se guarda el .cfx generado
        capa: 1 o 2 — determina el mapping de tasks → períodos
        suffix: sufijo opcional para el nombre (ej. "_v1")
        sqx_data: dict con datos extraídos de data.db (si None, usa ASSET_DEFAULTS)
        overwrite: sobreescribir si existe
        project_name: nombre base opcional para proyectos custom fuera del plan

    Returns:
        Path absoluto al .cfx generado.
    """
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")
    if capa not in CAPA_TASK_MAPS:
        raise ValueError(f"capa must be 1 or 2, got {capa}")
    editor = CfxEditor(template_path)
    task_map = CAPA_TASK_MAPS[capa]
    blocksetting_entry = resolve_blocksetting_entry(
        mining.bs,
        timeframe=mining.tf,
        capa=capa,
        blocksetting_capa2=blocksetting_capa2,
    )
    resolved_bs = str(blocksetting_entry.get("canonicalId") or mining.bs)
    base_project_name = project_name or f"Mining{mining.num:02d}_{mining.asset}_{mining.tf}_{resolved_bs}"
    resolved_target_profile = normalize_target_profile(target_profile, broker_postfix)

    # Resolver costos: data.db → fallback. Override manual con sqx_data si pasa.
    costs = resolve_costs(
        mining,
        sqx_db_path,
        broker_postfix,
        alias_override=alias_override,
        target_profile=resolved_target_profile,
    )
    if sqx_data:
        costs.update(sqx_data)

    # Aplicar patches a todos los XMLs internos del .cfx
    total_stats = {"files_patched": 0, "charts": 0, "swaps": 0, "sides": 0,
                   "dates": 0, "resources": 0, "paths_cleaned": 0, "commissions": 0, "spread_stress": 0,
                   "instrument_resources": 0,
                   "trading_window": 0, "blocksettings": 0, "exit_after_bars_disabled": 0,
                   "costs_source": costs["source"], "symbol": costs["symbol"],
                   "blocksetting": blocksetting_trace(blocksetting_entry)}
    for filename, tree in editor.iter_xml_files():
        if filename == "config.xml":
            continue  # config.xml no contiene Setup nodes
        root = tree.getroot()
        # Determinar el período correcto para este task XML según capa
        period_key = task_map.get(filename, "BUILD")
        period = RETEST_PERIODS[period_key]
        active_costs = costs
        cross_retest = _cross_broker_retest(capa, filename)
        if cross_retest:
            broker_profile_id = str(cross_retest.get("brokerProfile") or "")
            cross_profile = _profile_from_broker(broker_profile_id)
            cross_profile.update({
                "id": broker_profile_id,
                "mode": "methodology_cross_broker",
                "warning": cross_retest.get("label") or "",
            })
            active_costs = resolve_costs(
                mining,
                sqx_db_path,
                str(cross_profile.get("brokerPostfix") or broker_postfix),
                alias_override=alias_override,
                target_profile=cross_profile,
            )
            active_costs = _apply_cross_broker_execution_profile(
                active_costs,
                costs,
                cross_retest,
                resolved_target_profile,
            )
            cross_period_key = str(cross_retest.get("period") or period_key)
            period = RETEST_PERIODS.get(cross_period_key, period)
            if cross_retest.get("boundToAvailableData", True):
                period = _bound_retest_period_to_available_data(
                    period,
                    active_costs,
                    min_coverage_days=int(cross_retest.get("minCoverageDays") or 730),
                )

        stats = apply_mining_to_xml(
            root,
            symbol=active_costs["symbol"],
            timeframe=mining.tf,
            direction=mining.dir,
            swap_long=active_costs["swap_long"],
            swap_short=active_costs["swap_short"],
            spread=active_costs["spread"],
            swap_type=active_costs.get("swap_type"),
            commission_type=active_costs.get("commission_type"),
            commission_value=active_costs.get("commission_value"),
            resource={**active_costs, "asset": mining.asset},
            period=period,
            trading_window=_trading_window_for_file(capa, filename, mining.tf),
            spread_stress_multipliers=_spread_stress_for(capa, filename),
            backtest_precision=_backtest_precision_for_file(capa, filename),
            clean_paths=True,
            strip_custom_block_resources=bool(resolved_target_profile.get("stripCustomBlockResources")),
            strip_instrument_resources=bool(resolved_target_profile.get("stripInstrumentResources")),
        )
        if apply_blocksetting_to_xml(root, blocksetting_entry):
            total_stats["blocksettings"] += 1
        if capa == 2 and filename in CAPA2_NO_EXIT_AFTER_BARS_TASKS:
            total_stats["exit_after_bars_disabled"] += _disable_exit_after_bars(root)
        editor.update_xml(filename, tree)
        total_stats["files_patched"] += 1
        for k in ("charts", "swaps", "sides", "dates", "resources", "paths_cleaned", "commissions", "trading_window", "spread_stress", "instrument_resources"):
            total_stats[k] += stats[k]

    # Renombrar el proyecto en config.xml (incluye capa en el nombre)
    if editor.has("config.xml"):
        config_tree = editor.parse_xml("config.xml")
        config_root = config_tree.getroot()
        config_root.set("name", f"{base_project_name}_Capa{capa}")
        build_title = _build_task_title(resolved_bs, capa, mining.dir, mining.tf)
        for task in config_root.findall(".//Task"):
            if task.get("type") == "Build":
                task.set("title", build_title)
        total_stats["paths_cleaned"] += clean_external_paths(config_root)
        editor.update_xml("config.xml", config_tree)

    if capa == 1:
        _apply_capa1_registered_pipeline_contract(editor)
    elif capa == 2:
        _apply_capa2_registered_pipeline_contract(editor)

    # Guardar el .cfx
    out_name = f"{base_project_name}_Capa{capa}{suffix}.cfx"
    out_path = os.path.abspath(os.path.join(output_dir, out_name))
    if overwrite and os.path.isfile(out_path):
        backup_dir = os.path.join(output_dir, "__cfx_backups")
        os.makedirs(backup_dir, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = os.path.splitext(out_name)[0]
        backup_path = os.path.join(backup_dir, f"{stem}.{stamp}.cfx")
        counter = 2
        while os.path.exists(backup_path):
            backup_path = os.path.join(backup_dir, f"{stem}.{stamp}.{counter}.cfx")
            counter += 1
        shutil.copy2(out_path, backup_path)
    editor.save(out_path, overwrite=overwrite)
    return out_path
