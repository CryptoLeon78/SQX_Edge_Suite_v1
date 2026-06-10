from __future__ import annotations

import argparse
import hashlib
import json
import math
import sqlite3
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from .blocksettings_ai_generator import _safe_token
from .bsai15_tick_real_diagnostic import BS_AI14_FROZEN_LOT_DECISION, TICK_REAL_TASK_XML
from .bsai_first_start_gate import _load_config, _privacy_guard, _target_project_names
from .bsai_resource_compatibility import DEFAULT_CANDIDATE_ID, DEFAULT_REMAP_SUFFIX, load_candidate_metadata
from .cfx_editor import CfxEditor
from .plan import normalize_direction


BS_AI16_CAPA1_EXPERIMENT_GATE_VERSION = "bs-ai16-capa1-experiment-prereg-gate-v1"
BS_AI16_STATUS = "preregistered_capa1_tick_rule_ready_no_import_no_start"
EVIDENCE_DIR_PARTS = (".local", "blocksettings_ai", "capa1_experiments")

DEFAULT_RETENTION_RATIO = 0.65
DEFAULT_ABSOLUTE_FLOOR = 120
DEFAULT_HOST_PROFILE = "sqx144_full"
TRADE_RULE_FORMULA = "realTickTrades >= max(absoluteFloor, floor(priorValidationTrades * retentionRatio))"
PROTECTED_MAIN_FILTER_COLUMNS = ("ProfitFactor", "WinningPct", "ReturnDDRatio")
SPREAD_TASK_LABELS = {
    "Build-Task1.xml": "BUILD",
    "Retest-Task3.xml": "RETEST 0",
    "Retest-Task1.xml": "retest 1",
    "AutomaticRetest-Task2.xml": "TICK REAL",
    "Retest-Task2.xml": "Forward",
}


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _sha256_short(path: Path, length: int = 12) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:length]


def _retention_pct(retention_ratio: float) -> int:
    return int(round(float(retention_ratio) * 100))


def _validate_rule(retention_ratio: float, absolute_floor: int) -> tuple[float, int]:
    ratio = float(retention_ratio)
    floor_value = int(absolute_floor)
    if ratio < 0.50 or ratio > 0.90:
        raise ValueError("retention_ratio_out_of_guarded_range")
    if floor_value < 50 or floor_value > 250:
        raise ValueError("absolute_floor_out_of_guarded_range")
    return round(ratio, 4), floor_value


def _direction_tag(direction: str) -> str:
    return {"long": "L", "short": "S", "both": "LS"}[normalize_direction(direction)]


def _candidate_recipe(project_root: Path, candidate_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    meta = load_candidate_metadata(project_root, candidate_id)
    recipe = meta.get("recipe") if isinstance(meta.get("recipe"), dict) else {}
    entry = meta.get("entry") if isinstance(meta.get("entry"), dict) else {}
    if not recipe:
        raise ValueError("bsai_candidate_recipe_missing")
    if not entry:
        raise ValueError("bsai_candidate_entry_missing")
    return dict(recipe), dict(entry)


def _experiment_id(recipe: dict[str, Any], retention_ratio: float, absolute_floor: int) -> str:
    asset = _safe_token(str(recipe.get("asset") or "AUDCAD").upper(), "AUDCAD")
    timeframe = _safe_token(str(recipe.get("timeframe") or "H1").upper(), "H1")
    direction = _direction_tag(str(recipe.get("direction") or "long"))
    return _safe_token(
        f"BSAI16_{asset}_{timeframe}_{direction}_TICKR{_retention_pct(retention_ratio)}_F{absolute_floor}_Capa1_v001",
        "BSAI16_Capa1_TICK_RULE_v001",
    )


def _source_project_cfx(config: dict[str, Any], project_name: str) -> Path:
    return Path(str(config.get("sqx_projects_dir") or "")) / project_name / "project.cfx"


def _experiment_dir(project_root: Path, experiment_id: str) -> Path:
    return project_root.joinpath(*EVIDENCE_DIR_PARTS, experiment_id)


def _artifact_name(experiment_id: str) -> str:
    return f"{experiment_id}.cfx"


def _public_zip_summary(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"exists": False, "zipValid": False}
    try:
        with zipfile.ZipFile(path, "r") as archive:
            names = set(archive.namelist())
            return {
                "exists": True,
                "zipValid": True,
                "hasConfigXml": "config.xml" in names,
                "hasTickRealTaskXml": TICK_REAL_TASK_XML in names,
                "memberCount": len(names),
                "sha256Short": _sha256_short(path),
            }
    except Exception as exc:
        return {
            "exists": True,
            "zipValid": False,
            "errorCode": type(exc).__name__,
        }


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _sqlite_ro_uri(db_path: Path) -> str:
    return f"file:{db_path.resolve(strict=False).as_posix()}?mode=ro"


def _catalog_costs(config: dict[str, Any], asset: str) -> dict[str, Any]:
    db_path = Path(str(config.get("sqx_data_db") or ""))
    base = {
        "readMode": "sqlite_uri_mode_ro_query_only",
        "catalogAvailable": False,
        "primaryInstrument": f"{asset}_darwinex",
        "crossBrokerInstrument": f"{asset}_dukascopy",
        "primaryDefaultSpread": None,
        "crossBrokerDefaultSpread": None,
        "instrumentSpreadRows": [],
        "dataRows": [],
    }
    if not db_path.is_file():
        base["status"] = "data_db_unavailable"
        return base
    try:
        conn = sqlite3.connect(_sqlite_ro_uri(db_path), uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only = ON")
        try:
            instrument_rows = [
                dict(row)
                for row in conn.execute(
                    """
                    SELECT INSTRUMENT, BROKER_ID, DEFAULTSPREAD
                    FROM INSTRUMENTS
                    WHERE INSTRUMENT LIKE ?
                    ORDER BY INSTRUMENT, BROKER_ID
                    """,
                    (f"{asset}%",),
                ).fetchall()
            ]
            data_rows = [
                dict(row)
                for row in conn.execute(
                    """
                    SELECT SYMBOL, INSTRUMENT, SOURCE, BROKER_ID, ROWS, USYMBOL
                    FROM DATA
                    WHERE SYMBOL LIKE ? OR USYMBOL = ?
                    ORDER BY SYMBOL
                    """,
                    (f"{asset}%", asset),
                ).fetchall()
            ]
        finally:
            conn.close()
    except Exception as exc:
        base["status"] = f"catalog_read_failed:{type(exc).__name__}"
        return base

    sanitized_rows: list[dict[str, Any]] = []
    primary_default = None
    cross_default = None
    for row in instrument_rows:
        instrument = str(row.get("INSTRUMENT") or "")
        broker_id = None if row.get("BROKER_ID") is None else str(row.get("BROKER_ID"))
        default_spread = _float_or_none(row.get("DEFAULTSPREAD"))
        item = {
            "instrument": instrument,
            "brokerId": broker_id,
            "defaultSpread": default_spread,
        }
        sanitized_rows.append(item)
        if instrument == base["primaryInstrument"] and broker_id == "4":
            primary_default = default_spread
        if instrument == base["crossBrokerInstrument"] and broker_id == "3":
            cross_default = default_spread
    base.update(
        {
            "catalogAvailable": True,
            "status": "ok",
            "primaryDefaultSpread": primary_default,
            "crossBrokerDefaultSpread": cross_default,
            "instrumentSpreadRows": sanitized_rows[:16],
            "dataRows": [
                {
                    "symbol": str(row.get("SYMBOL") or ""),
                    "instrument": str(row.get("INSTRUMENT") or ""),
                    "source": None if row.get("SOURCE") is None else str(row.get("SOURCE")),
                    "brokerId": None if row.get("BROKER_ID") is None else str(row.get("BROKER_ID")),
                    "rowsPositive": bool(int(row.get("ROWS") or 0) > 0),
                    "uSymbol": str(row.get("USYMBOL") or ""),
                }
                for row in data_rows[:16]
            ],
        }
    )
    return base


def _chart_spread_summary(cfx_path: Path) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "sourceCfxPresent": cfx_path.is_file(),
        "taskCharts": [],
        "extractionStatus": "not_available",
    }
    if not cfx_path.is_file():
        return summary
    try:
        with zipfile.ZipFile(cfx_path, "r") as archive:
            names = set(archive.namelist())
            items = []
            for xml_name, label in SPREAD_TASK_LABELS.items():
                if xml_name not in names:
                    continue
                root = ET.fromstring(archive.read(xml_name))
                charts = []
                for chart in root.findall(".//Chart"):
                    symbol = chart.get("symbol")
                    if not symbol:
                        continue
                    charts.append(
                        {
                            "symbol": symbol,
                            "timeframe": chart.get("timeframe"),
                            "spread": _float_or_none(chart.get("spread")),
                        }
                    )
                resource_symbols = []
                for symbol in root.findall(".//Symbol"):
                    name = symbol.get("name")
                    if not name:
                        continue
                    resource_symbols.append(
                        {
                            "name": name,
                            "source": symbol.get("source"),
                            "broker": symbol.get("broker"),
                            "precision": symbol.get("precision"),
                        }
                    )
                items.append(
                    {
                        "task": label,
                        "taskXml": xml_name,
                        "charts": charts[:8],
                        "resourceSymbols": resource_symbols[:4],
                    }
                )
        summary["taskCharts"] = items
        summary["extractionStatus"] = "ok"
        return summary
    except Exception as exc:
        summary["extractionStatus"] = f"read_failed:{type(exc).__name__}"
        return summary


def _spread_cost_sanity(config: dict[str, Any], source_cfx: Path, recipe: dict[str, Any]) -> dict[str, Any]:
    asset = _safe_token(str(recipe.get("asset") or "AUDCAD").upper(), "AUDCAD")
    primary_symbol = f"{asset}_darwinex"
    cross_symbol = f"{asset}_dukascopy"
    catalog = _catalog_costs(config, asset)
    charts = _chart_spread_summary(source_cfx)
    issues: list[dict[str, Any]] = []
    primary_default = _float_or_none(catalog.get("primaryDefaultSpread"))
    cross_default = _float_or_none(catalog.get("crossBrokerDefaultSpread"))
    primary_spreads: list[float] = []
    cross_spreads: list[float] = []
    for task in charts.get("taskCharts") or []:
        for chart in task.get("charts") or []:
            spread = _float_or_none(chart.get("spread"))
            symbol = str(chart.get("symbol") or "")
            if spread is None:
                continue
            if symbol == primary_symbol:
                primary_spreads.append(spread)
                if primary_default is not None and spread + 1e-9 < primary_default:
                    issues.append(
                        {
                            "severity": "fail",
                            "code": "primary_spread_below_host_catalog",
                            "task": task.get("task"),
                            "symbol": symbol,
                            "chartSpread": spread,
                            "catalogSpread": primary_default,
                        }
                    )
            if symbol == cross_symbol:
                cross_spreads.append(spread)
                if cross_default is not None and spread + 1e-9 < cross_default:
                    issues.append(
                        {
                            "severity": "warn",
                            "code": "cross_broker_spread_below_alternate_catalog",
                            "task": task.get("task"),
                            "symbol": symbol,
                            "chartSpread": spread,
                            "catalogSpread": cross_default,
                        }
                    )
    if primary_default is None:
        issues.append({"severity": "warn", "code": "primary_catalog_spread_missing"})
    if charts.get("extractionStatus") != "ok":
        issues.append({"severity": "warn", "code": "chart_spread_extraction_unavailable"})

    fail_count = sum(1 for issue in issues if issue.get("severity") == "fail")
    warn_count = sum(1 for issue in issues if issue.get("severity") == "warn")
    if fail_count:
        verdict = "fail_primary_spread_under_host_catalog"
    elif warn_count:
        verdict = "warn_spread_cost_review_before_run"
    else:
        verdict = "pass_primary_spread_matches_host_catalog"
    return {
        "hypothesis": "too_low_spread_can_inflate_simulated_pf_and_real_tick_can_deflate_pf",
        "verdict": verdict,
        "asset": asset,
        "primarySymbol": primary_symbol,
        "crossBrokerSymbol": cross_symbol,
        "catalog": catalog,
        "chartSpreadSummary": charts,
        "observedPrimaryChartSpreads": sorted(set(primary_spreads)),
        "observedCrossBrokerChartSpreads": sorted(set(cross_spreads)),
        "issues": issues[:16],
        "failCount": fail_count,
        "warnCount": warn_count,
        "policy": {
            "primaryUnderCatalogBlocksPrepare": True,
            "crossBrokerDivergenceIsMethodologyWarning": True,
            "doesNotRescueFrozenLot": True,
        },
    }


def _condition_parts(condition: ET.Element) -> tuple[str | None, list[ET.Element], list[ET.Element]]:
    comparator = condition.find(".//Comparator")
    return (
        comparator.get("value") if comparator is not None else None,
        condition.findall(".//Column-Value"),
        condition.findall(".//Numeric-Value"),
    )


def _tick_filter_summary_from_root(root: ET.Element) -> dict[str, Any]:
    absolute: dict[str, dict[str, Any]] = {}
    relative: list[dict[str, Any]] = []
    for condition in root.findall(".//Condition"):
        if str(condition.get("use", "true")).lower() == "false":
            continue
        comparator, columns, numerics = _condition_parts(condition)
        if len(columns) == 1 and numerics:
            column = str(columns[0].get("column") or "")
            result_type = str(columns[0].get("resultType") or "")
            if result_type == "main" and column not in absolute:
                absolute[column] = {
                    "column": column,
                    "comparator": comparator,
                    "value": numerics[0].get("value"),
                    "resultType": result_type,
                }
        if len(columns) == 2 and str(columns[0].get("resultType") or "") == "RetestWithHigherPrecision":
            relative.append(
                {
                    "column": columns[0].get("column"),
                    "comparator": comparator,
                    "leftResultType": columns[0].get("resultType"),
                    "rightResultType": columns[1].get("resultType"),
                    "rightPctRatio": columns[1].get("pctRatio"),
                }
            )
    ordered = ["NumberOfTrades", "ProfitFactor", "WinningPct", "ReturnDDRatio"]
    return {
        "absoluteMainFilters": [absolute[column] for column in ordered if column in absolute],
        "relativePrecisionFilters": relative[:8],
    }


def _extract_tick_filter_summary_from_cfx(cfx_path: Path) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "task": "TICK REAL",
        "taskXml": TICK_REAL_TASK_XML,
        "projectCfxPresent": cfx_path.is_file(),
        "absoluteMainFilters": [],
        "relativePrecisionFilters": [],
        "extractionStatus": "not_available",
    }
    if not cfx_path.is_file():
        return summary
    try:
        with zipfile.ZipFile(cfx_path, "r") as archive:
            if TICK_REAL_TASK_XML not in archive.namelist():
                summary["extractionStatus"] = "tick_real_task_xml_missing"
                return summary
            root = ET.fromstring(archive.read(TICK_REAL_TASK_XML))
    except Exception as exc:
        summary["extractionStatus"] = f"read_failed:{type(exc).__name__}"
        return summary
    summary.update(_tick_filter_summary_from_root(root))
    summary["extractionStatus"] = "ok"
    return summary


def _main_filter_value(summary: dict[str, Any], column: str) -> str | None:
    for item in summary.get("absoluteMainFilters") or []:
        if item.get("column") == column:
            return item.get("value")
    return None


def _retention_filter_pct(summary: dict[str, Any], column: str = "NumberOfTrades") -> str | None:
    for item in summary.get("relativePrecisionFilters") or []:
        if item.get("column") == column and item.get("rightResultType") == "main":
            return item.get("rightPctRatio")
    return None


def _rule_public(retention_ratio: float, absolute_floor: int) -> dict[str, Any]:
    ratio, floor_value = _validate_rule(retention_ratio, absolute_floor)
    examples = [120, 180, 200, 300, 302, 308, 311]
    return {
        "formula": TRADE_RULE_FORMULA,
        "retentionRatio": ratio,
        "retentionPct": _retention_pct(ratio),
        "absoluteFloor": floor_value,
        "preRegisteredBeforeRun": True,
        "chosenGridPoint": {"retentionRatio": ratio, "absoluteFloor": floor_value},
        "initialGridSource": "BS-AI15 diagnostic grid",
        "effectiveThresholdExamples": [
            {
                "priorValidationTrades": value,
                "requiredRealTickTrades": max(floor_value, math.floor(value * ratio)),
            }
            for value in examples
        ],
        "sqxRepresentation": {
            "absoluteMainFilter": f"NumberOfTrades >= {floor_value}",
            "relativePrecisionFilter": f"RetestWithHigherPrecision.NumberOfTrades >= main.NumberOfTrades * {_retention_pct(ratio)}%",
        },
    }


def _apply_tick_trade_rule(root: ET.Element, retention_ratio: float, absolute_floor: int) -> dict[str, Any]:
    retention_pct = _retention_pct(retention_ratio)
    absolute_patched = 0
    retention_patched = 0
    protected_before: dict[str, str | None] = {}
    protected_after: dict[str, str | None] = {}
    before = _tick_filter_summary_from_root(root)
    for column in PROTECTED_MAIN_FILTER_COLUMNS:
        protected_before[column] = _main_filter_value(before, column)

    for condition in root.findall(".//Condition"):
        if str(condition.get("use", "true")).lower() == "false":
            continue
        _, columns, numerics = _condition_parts(condition)
        if len(columns) == 1 and numerics:
            if columns[0].get("column") == "NumberOfTrades" and columns[0].get("resultType") == "main":
                numerics[0].set("value", str(absolute_floor))
                absolute_patched += 1
                continue
        if len(columns) == 2:
            left = columns[0]
            right = columns[1]
            if (
                left.get("column") == "NumberOfTrades"
                and left.get("resultType") == "RetestWithHigherPrecision"
                and right.get("column") == "NumberOfTrades"
                and right.get("resultType") == "main"
            ):
                right.set("pctRatio", str(retention_pct))
                retention_patched += 1

    after = _tick_filter_summary_from_root(root)
    for column in PROTECTED_MAIN_FILTER_COLUMNS:
        protected_after[column] = _main_filter_value(after, column)
    return {
        "absoluteNumberOfTradesPatched": absolute_patched,
        "relativeNumberOfTradesPatched": retention_patched,
        "protectedFiltersBefore": protected_before,
        "protectedFiltersAfter": protected_after,
        "protectedFiltersUnchanged": protected_before == protected_after,
        "before": {
            "absoluteNumberOfTrades": _main_filter_value(before, "NumberOfTrades"),
            "relativeNumberOfTradesPct": _retention_filter_pct(before),
        },
        "after": {
            "absoluteNumberOfTrades": _main_filter_value(after, "NumberOfTrades"),
            "relativeNumberOfTradesPct": _retention_filter_pct(after),
        },
    }


def _prepare_local_artifact(
    project_root: Path,
    source_cfx: Path,
    experiment_id: str,
    retention_ratio: float,
    absolute_floor: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_dir = _experiment_dir(project_root, experiment_id)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / _artifact_name(experiment_id)
    source_hash_before = _sha256_short(source_cfx) if source_cfx.is_file() else None
    editor = CfxEditor(str(source_cfx))
    if not editor.has("config.xml"):
        raise ValueError("config_xml_missing")
    if not editor.has(TICK_REAL_TASK_XML):
        raise ValueError("tick_real_task_xml_missing")

    config_tree = editor.parse_xml("config.xml")
    config_tree.getroot().set("name", experiment_id)
    editor.update_xml("config.xml", config_tree)

    tick_tree = editor.parse_xml(TICK_REAL_TASK_XML)
    patch_summary = _apply_tick_trade_rule(tick_tree.getroot(), retention_ratio, absolute_floor)
    if patch_summary["absoluteNumberOfTradesPatched"] < 1:
        raise ValueError("absolute_number_of_trades_filter_missing")
    if patch_summary["relativeNumberOfTradesPatched"] < 1:
        raise ValueError("relative_number_of_trades_filter_missing")
    if not patch_summary["protectedFiltersUnchanged"]:
        raise ValueError("protected_filters_changed")
    editor.update_xml(TICK_REAL_TASK_XML, tick_tree)
    editor.save(str(artifact_path), overwrite=True)
    source_hash_after = _sha256_short(source_cfx) if source_cfx.is_file() else None
    artifact_summary = _public_zip_summary(artifact_path)
    artifact_summary.update(
        {
            "written": True,
            "artifactRef": artifact_path.name,
            "projectNameForManualImport": experiment_id,
            "sourceProjectCfxHashUnchanged": source_hash_before == source_hash_after,
        }
    )
    return artifact_summary, patch_summary


def _base_payload(
    action: str,
    project_root: Path,
    candidate_id: str,
    remap_suffix: str,
    retention_ratio: float,
    absolute_floor: int,
) -> tuple[dict[str, Any], Path, str]:
    ratio, floor_value = _validate_rule(retention_ratio, absolute_floor)
    config = _load_config(project_root)
    recipe, entry = _candidate_recipe(project_root, candidate_id)
    source_names = _target_project_names(project_root, candidate_id, remap_suffix)
    source_project = source_names[0]
    source_cfx = _source_project_cfx(config, source_project)
    experiment_id = _experiment_id(recipe, ratio, floor_value)
    source_zip = _public_zip_summary(source_cfx)
    tick_summary = _extract_tick_filter_summary_from_cfx(source_cfx)
    spread_cost = _spread_cost_sanity(config, source_cfx, recipe)
    blockers: list[str] = []
    warnings: list[str] = []
    if not source_zip.get("exists"):
        blockers.append("source_capa1_project_cfx_missing")
    elif not source_zip.get("zipValid"):
        blockers.append("source_capa1_project_cfx_not_valid_zip")
    if tick_summary.get("extractionStatus") != "ok":
        blockers.append("tick_real_task_filter_summary_unavailable")
    current_retention = _retention_filter_pct(tick_summary)
    current_floor = _main_filter_value(tick_summary, "NumberOfTrades")
    if current_floor is None:
        blockers.append("current_absolute_number_of_trades_filter_missing")
    if current_retention is None:
        blockers.append("current_relative_number_of_trades_filter_missing")
    if str(current_floor) == str(floor_value) and str(current_retention) == str(_retention_pct(ratio)):
        warnings.append("source_tick_rule_already_matches_pre_registered_rule")
    if spread_cost.get("failCount"):
        blockers.append("spread_cost_sanity_primary_under_spread")
    if spread_cost.get("warnCount"):
        warnings.append("spread_cost_sanity_warning")

    payload: dict[str, Any] = {
        "ok": not blockers,
        "version": BS_AI16_CAPA1_EXPERIMENT_GATE_VERSION,
        "action": action,
        "status": BS_AI16_STATUS,
        "candidateId": candidate_id,
        "hostProfile": DEFAULT_HOST_PROFILE,
        "remapSuffix": remap_suffix,
        "experiment": {
            "id": experiment_id,
            "type": "new_capa1_experiment",
            "sourceProjectName": source_project,
            "sourceCapa": 1,
            "candidateState": "same_candidate_new_experiment_not_rescue",
            "frozenLotNotReinterpreted": True,
            "frozenLotDecision": BS_AI14_FROZEN_LOT_DECISION,
        },
        "candidateTrace": {
            "asset": _safe_token(str(recipe.get("asset") or "").upper(), "AUDCAD"),
            "timeframe": _safe_token(str(recipe.get("timeframe") or "").upper(), "H1"),
            "direction": normalize_direction(str(recipe.get("direction") or "long")),
            "candidateLayer": int(recipe.get("candidateLayer") or 2),
            "baseCanonicalId": entry.get("baseCanonicalId"),
            "promotionState": entry.get("promotionState"),
        },
        "preRegisteredTradeRule": _rule_public(ratio, floor_value),
        "currentTickRealRule": {
            "taskXml": TICK_REAL_TASK_XML,
            "extractionStatus": tick_summary.get("extractionStatus"),
            "absoluteNumberOfTrades": current_floor,
            "relativeNumberOfTradesPct": current_retention,
            "profitFactor": _main_filter_value(tick_summary, "ProfitFactor"),
            "winningPct": _main_filter_value(tick_summary, "WinningPct"),
            "returnDdRatio": _main_filter_value(tick_summary, "ReturnDDRatio"),
        },
        "spreadCostSanity": spread_cost,
        "patchIntent": {
            "targetTaskXml": TICK_REAL_TASK_XML,
            "newAbsoluteNumberOfTrades": str(floor_value),
            "newRelativeNumberOfTradesPct": str(_retention_pct(ratio)),
            "protectedFilters": list(PROTECTED_MAIN_FILTER_COLUMNS),
            "protectedFiltersPolicy": "preserve_existing_pf_win_return_dd_no_relaxation",
            "onlyLocalArtifactMayBeWritten": action == "prepare",
        },
        "sourceProject": {
            "projectName": source_project,
            "cfxZip": source_zip,
        },
        "artifact": {
            "written": False,
            "artifactRef": None,
            "projectNameForManualImport": experiment_id,
        },
        "nextGate": {
            "recommended": "BS-AI17 controlled Capa1 import/start gate after operator approval",
            "approvalRequiredBeforeImportOrStart": True,
            "capa2StartAllowed": False,
        },
        "blockers": blockers,
        "warnings": warnings,
        "guards": {
            "readOnlyHost": True,
            "writesLocalExperimentArtifact": action == "prepare",
            "writesSqxHost": False,
            "importsProject": False,
            "projectStartRequested": False,
            "projectStopRequested": False,
            "capa2StartAllowed": False,
            "filterRelaxationAllowedForFrozenLot": False,
            "writesDataDb": False,
            "writesUserProjects": False,
            "mutatesDatabanks": False,
            "migrationToolAllowed": False,
            "officialBlocksettingsPromotion": False,
            "sqx144UpdatePromotion": False,
        },
        "privacy": {
            "localPathsReturned": False,
            "rawXmlReturned": False,
            "rawLogReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
        },
    }
    _privacy_guard(payload)
    return payload, source_cfx, experiment_id


def write_evidence_file(project_root: Path, experiment_id: str, action: str, payload: dict[str, Any]) -> str:
    _privacy_guard(payload)
    evidence_dir = _experiment_dir(project_root, experiment_id)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    filename = f"bsai16_capa1_experiment_gate_{action}_{_utc_stamp()}.json"
    (evidence_dir / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return filename


def status_payload(
    project_root: str | Path,
    candidate_id: str = DEFAULT_CANDIDATE_ID,
    *,
    remap_suffix: str = DEFAULT_REMAP_SUFFIX,
    retention_ratio: float = DEFAULT_RETENTION_RATIO,
    absolute_floor: int = DEFAULT_ABSOLUTE_FLOOR,
) -> dict[str, Any]:
    root = _project_root(project_root)
    payload, _, _ = _base_payload("status", root, candidate_id, remap_suffix, retention_ratio, absolute_floor)
    return payload


def plan_payload(
    project_root: str | Path,
    candidate_id: str = DEFAULT_CANDIDATE_ID,
    *,
    remap_suffix: str = DEFAULT_REMAP_SUFFIX,
    retention_ratio: float = DEFAULT_RETENTION_RATIO,
    absolute_floor: int = DEFAULT_ABSOLUTE_FLOOR,
) -> dict[str, Any]:
    root = _project_root(project_root)
    payload, _, _ = _base_payload("plan", root, candidate_id, remap_suffix, retention_ratio, absolute_floor)
    payload["plan"] = {
        "prepareCommand": "tools/sqx144_bsai16_capa1_experiment_gate.ps1 prepare",
        "runPolicy": "prepare local cfx only; import/start requires a later gate",
        "currentLotHandling": "frozen_failed_for_capa2_no_rescue",
    }
    _privacy_guard(payload)
    return payload


def prepare_payload(
    project_root: str | Path,
    candidate_id: str = DEFAULT_CANDIDATE_ID,
    *,
    remap_suffix: str = DEFAULT_REMAP_SUFFIX,
    retention_ratio: float = DEFAULT_RETENTION_RATIO,
    absolute_floor: int = DEFAULT_ABSOLUTE_FLOOR,
    write_evidence: bool = False,
) -> dict[str, Any]:
    root = _project_root(project_root)
    payload, source_cfx, experiment_id = _base_payload("prepare", root, candidate_id, remap_suffix, retention_ratio, absolute_floor)
    if payload["ok"]:
        try:
            artifact, patch_summary = _prepare_local_artifact(root, source_cfx, experiment_id, float(retention_ratio), int(absolute_floor))
            payload["artifact"] = artifact
            payload["appliedLocalPatch"] = patch_summary
            if not artifact.get("sourceProjectCfxHashUnchanged"):
                payload["blockers"].append("source_project_cfx_hash_changed")
        except Exception as exc:
            payload["ok"] = False
            payload["blockers"].append("local_artifact_prepare_failed")
            payload["artifact"] = {
                "written": False,
                "artifactRef": None,
                "projectNameForManualImport": experiment_id,
                "errorCode": type(exc).__name__,
            }
    payload["ok"] = bool(payload["ok"] and not payload["blockers"])
    if write_evidence:
        evidence_ref = write_evidence_file(root, experiment_id, "prepare", payload)
        payload["evidenceWritten"] = True
        payload["evidenceRef"] = evidence_ref
    else:
        payload["evidenceWritten"] = False
    _privacy_guard(payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("status", "plan", "prepare"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--candidate-id", default=DEFAULT_CANDIDATE_ID)
    parser.add_argument("--remap-suffix", default=DEFAULT_REMAP_SUFFIX)
    parser.add_argument("--retention-ratio", type=float, default=DEFAULT_RETENTION_RATIO)
    parser.add_argument("--absolute-floor", type=int, default=DEFAULT_ABSOLUTE_FLOOR)
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)

    if args.action == "prepare":
        payload = prepare_payload(
            args.project_root,
            args.candidate_id,
            remap_suffix=args.remap_suffix,
            retention_ratio=args.retention_ratio,
            absolute_floor=args.absolute_floor,
            write_evidence=args.write_evidence,
        )
    elif args.action == "plan":
        payload = plan_payload(
            args.project_root,
            args.candidate_id,
            remap_suffix=args.remap_suffix,
            retention_ratio=args.retention_ratio,
            absolute_floor=args.absolute_floor,
        )
    else:
        payload = status_payload(
            args.project_root,
            args.candidate_id,
            remap_suffix=args.remap_suffix,
            retention_ratio=args.retention_ratio,
            absolute_floor=args.absolute_floor,
        )

    _privacy_guard(payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
