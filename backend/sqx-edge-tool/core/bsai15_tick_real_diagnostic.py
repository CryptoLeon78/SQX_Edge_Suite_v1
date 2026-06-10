from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import statistics
import struct
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from .bsai14_capa1_monitor_gate import _databank_summary
from .bsai_first_start_gate import (
    DEFAULT_REMOTE_BASE_URL,
    _host_snapshot,
    _list_target_projects,
    _load_config,
    _privacy_guard,
    _target_project_names,
)
from .bsai_resource_compatibility import DEFAULT_CANDIDATE_ID, DEFAULT_REMAP_SUFFIX


BS_AI15_TICK_REAL_DIAGNOSTIC_VERSION = "bs-ai15-tick-real-diagnostic-v1"
EVIDENCE_DIR_PARTS = (".local", "blocksettings_ai", "tick_real_diagnostic")
BS_AI14_FROZEN_LOT_DECISION = "tick_real_pf_failed_trade_threshold_warning_no_capa2"
BS_AI15_STATUS = "diagnostic_plan_ready_no_capa2_no_filter_relaxation"
TICK_REAL_TASK_XML = "AutomaticRetest-Task2.xml"

TARGET_DATABANKS = ("RETEST 0", "retest 1", "TICK")
TICK_MAIN_FILTER_COLUMNS = ("NumberOfTrades", "ProfitFactor", "WinningPct", "ReturnDDRatio")
SENSITIVE_METRIC_KEYS = {
    "path",
    "localPath",
    "filePath",
    "sqx_path",
    "sqx_data_db",
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


def _round_metric(value: Any) -> float | int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number.is_integer():
        return int(number)
    return round(number, 4)


def _public_strategy_name(path: Path) -> str:
    name = path.stem.strip()
    return name[:80] if name else "strategy"


def _databank_dir(config: dict[str, Any], project_name: str, databank: str) -> Path:
    return Path(str(config.get("sqx_projects_dir") or "")) / project_name / "databanks" / databank


def _sqx_files(config: dict[str, Any], project_name: str, databank: str) -> list[Path]:
    root = _databank_dir(config, project_name, databank)
    if not root.is_dir():
        return []
    return sorted((item for item in root.rglob("*.sqx") if item.is_file()), key=lambda item: item.name.casefold())


def _sqstats_items(data: bytes) -> dict[str, float | int]:
    values: dict[str, float | int] = {}
    for index in range(max(0, len(data) - 7)):
        tag = data[index]
        if tag not in (ord("e"), ord("g")):
            continue
        name_len = int.from_bytes(data[index + 1 : index + 3], "big", signed=False)
        value_start = index + 3 + name_len
        value_end = value_start + 4
        if name_len < 1 or name_len > 100 or value_end > len(data):
            continue
        raw_name = data[index + 3 : value_start]
        if not all(32 <= byte < 127 for byte in raw_name):
            continue
        name = raw_name.decode("ascii", "replace")
        if name in SENSITIVE_METRIC_KEYS:
            continue
        raw_value = data[value_start:value_end]
        if tag == ord("e"):
            values.setdefault(name, int.from_bytes(raw_value, "big", signed=True))
        else:
            values.setdefault(name, struct.unpack(">f", raw_value)[0])
    return values


def _extract_sqstats_values(settings_xml: str) -> dict[str, float | int]:
    values: dict[str, float | int] = {}
    for match in re.finditer(r"<SQStats[^>]*\be=\"b64\"[^>]*>(.*?)</SQStats>", settings_xml, flags=re.DOTALL):
        try:
            data = base64.b64decode(match.group(1), validate=False)
        except Exception:
            continue
        for key, value in _sqstats_items(data).items():
            values.setdefault(key, value)
    return values


def _extract_result_header(settings_xml: str) -> dict[str, Any]:
    result_name = None
    result_key = None
    fitnesses: dict[str, float] = {}
    match = re.search(r"<ResultsGroup\b[^>]*\bResultName=\"([^\"]+)\"", settings_xml)
    if match:
        result_name = match.group(1)[:80]
    match = re.search(r"<Result\b[^>]*\bresultKey=\"([^\"]+)\"", settings_xml)
    if match:
        result_key = match.group(1)[:120]
    match = re.search(r"<Fitnesses\b([^>]*)", settings_xml)
    if match:
        for key, value in re.findall(r"\b([A-Za-z0-9_]+)=\"([-0-9.]+)\"", match.group(1)):
            try:
                fitnesses[key] = float(value)
            except ValueError:
                pass
    return {
        "resultName": result_name,
        "resultKey": result_key,
        "fitnessIS": _round_metric(fitnesses.get("IS")),
        "fitnessFS": _round_metric(fitnesses.get("FS")),
        "fitnessKeysPresent": sorted(fitnesses.keys())[:16],
    }


def _metric_value(stats: dict[str, float | int], *keys: str) -> float | int | None:
    for key in keys:
        if key in stats:
            return stats[key]
    return None


def _survivor_metrics(path: Path, index: int, *, retest0_names: set[str], tick_names: set[str]) -> dict[str, Any]:
    public: dict[str, Any] = {
        "survivorRef": f"retest1_{index:03d}",
        "strategyName": _public_strategy_name(path),
        "sha256Short": _sha256_short(path),
        "zipValid": False,
        "presentInRetest0": path.name in retest0_names,
        "presentInRetest1": True,
        "presentInTick": path.name in tick_names,
    }
    try:
        with zipfile.ZipFile(path, "r") as archive:
            names = set(archive.namelist())
            public["zipValid"] = True
            public["zipMemberSummary"] = {
                "hasSettingsXml": "settings.xml" in names,
                "hasLastSettingsXml": "lastSettings.xml" in names,
                "hasPortfolioXml": "strategy_Portfolio.xml" in names,
                "hasOrdersBin": "orders.bin" in names,
                "hasDailyEquity": any(name.endswith("dailyEquity.bin") for name in names),
                "memberCount": len(names),
            }
            settings_xml = archive.read("settings.xml").decode("utf-8", "replace") if "settings.xml" in names else ""
    except Exception as exc:
        public["metricExtractionStatus"] = "zip_read_failed"
        public["errorCode"] = type(exc).__name__
        return public

    header = _extract_result_header(settings_xml)
    stats = _extract_sqstats_values(settings_xml)
    trade_count = _metric_value(stats, "SampleType_11_Count", "Raw_TotalOrders", "FirstCount")
    public["result"] = header
    public["metricExtractionStatus"] = "partial_sqstats_no_tick_output"
    public["metricAvailability"] = {
        "profitFactorDirect": False,
        "tradeCountObserved": trade_count is not None,
        "netProfitObserved": "NetProfitIS" in stats,
        "drawdownCanonicalObserved": False,
        "drawdownProxyObserved": any(key in stats for key in ("SRS_ddIS", "MaxTSIntradayDrawdown", "AvgDrawdown")),
        "stabilityProxyObserved": any(key in stats for key in ("StagnationTrades", "Max Stagnation Trades", "DDHealthScore")),
        "afterRealTickObserved": False,
    }
    public["preRealTickMetrics"] = {
        "tradeCountObserved": _round_metric(trade_count),
        "tradeCountSource": "SQStats.SampleType_11_Count_or_Raw_TotalOrders",
        "profitFactor": None,
        "profitFactorStatus": "not_embedded_as_direct_retest1_metric",
        "netProfitIS": _round_metric(_metric_value(stats, "NetProfitIS")),
        "drawdownProxySrsDdIS": _round_metric(_metric_value(stats, "SRS_ddIS")),
        "maxTsIntradayDrawdown": _round_metric(_metric_value(stats, "MaxTSIntradayDrawdown")),
        "avgDrawdown": _round_metric(_metric_value(stats, "AvgDrawdown")),
        "returnOpenDdRatio": _round_metric(_metric_value(stats, "ReturnOpenDDRatio")),
        "recoveryFactor": _round_metric(_metric_value(stats, "RecoveryFactor")),
        "stagnationTrades": _round_metric(_metric_value(stats, "StagnationTrades", "Max Stagnation Trades")),
        "ddHealthScore": _round_metric(_metric_value(stats, "DDHealthScore")),
        "winLossProxy": _round_metric(_metric_value(stats, "TSWinLossRatio")),
    }
    public["afterRealTickMetrics"] = {
        "presentInTickDatabank": path.name in tick_names,
        "metricsAvailable": False,
        "reason": "tick_databank_has_zero_sqx" if not tick_names else "no_matching_tick_strategy_file",
    }
    public["tradeCountBeforeAfter"] = {
        "beforeRealTickTradesObserved": public["preRealTickMetrics"]["tradeCountObserved"],
        "afterRealTickTradesObserved": None,
        "retentionRatioObserved": None,
        "comparisonStatus": "after_real_tick_absent",
    }
    return public


def _condition_public(condition: ET.Element) -> dict[str, Any] | None:
    if str(condition.get("use", "true")).lower() == "false":
        return None
    comparator = condition.find(".//Comparator")
    columns = condition.findall(".//Column-Value")
    numerics = condition.findall(".//Numeric-Value")
    if not columns:
        return None
    return {
        "comparator": comparator.get("value") if comparator is not None else None,
        "columns": [
            {
                "column": column.get("column"),
                "name": column.get("name"),
                "resultType": column.get("resultType"),
                "pctRatio": column.get("pctRatio"),
            }
            for column in columns
        ],
        "numericValues": [numeric.get("value") for numeric in numerics],
    }


def _tick_real_filter_summary(config: dict[str, Any], project_name: str) -> dict[str, Any]:
    project_cfx = Path(str(config.get("sqx_projects_dir") or "")) / project_name / "project.cfx"
    summary: dict[str, Any] = {
        "task": "TICK REAL",
        "taskXml": TICK_REAL_TASK_XML,
        "projectCfxPresent": project_cfx.is_file(),
        "absoluteMainFilters": [],
        "relativePrecisionFilters": [],
        "extractionStatus": "not_available",
    }
    if not project_cfx.is_file():
        return summary
    try:
        with zipfile.ZipFile(project_cfx, "r") as archive:
            if TICK_REAL_TASK_XML not in archive.namelist():
                summary["extractionStatus"] = "tick_real_task_xml_missing"
                return summary
            root = ET.fromstring(archive.read(TICK_REAL_TASK_XML))
    except Exception as exc:
        summary["extractionStatus"] = f"read_failed:{type(exc).__name__}"
        return summary

    first_by_column: dict[str, dict[str, Any]] = {}
    relative: list[dict[str, Any]] = []
    for condition in root.findall(".//Condition"):
        item = _condition_public(condition)
        if not item:
            continue
        columns = item["columns"]
        numerics = item["numericValues"]
        if len(columns) == 1 and numerics:
            column = str(columns[0].get("column") or "")
            result_type = str(columns[0].get("resultType") or "")
            if column in TICK_MAIN_FILTER_COLUMNS and result_type == "main" and column not in first_by_column:
                first_by_column[column] = {
                    "column": column,
                    "comparator": item["comparator"],
                    "value": numerics[0],
                    "resultType": result_type,
                }
        if len(columns) == 2 and str(columns[0].get("resultType") or "") == "RetestWithHigherPrecision":
            relative.append({
                "column": columns[0].get("column"),
                "comparator": item["comparator"],
                "leftResultType": columns[0].get("resultType"),
                "rightResultType": columns[1].get("resultType"),
                "rightPctRatio": columns[1].get("pctRatio"),
            })
    summary["absoluteMainFilters"] = [first_by_column[column] for column in TICK_MAIN_FILTER_COLUMNS if column in first_by_column]
    summary["relativePrecisionFilters"] = relative[:8]
    summary["extractionStatus"] = "ok"
    return summary


def _survivor_summary(survivors: list[dict[str, Any]]) -> dict[str, Any]:
    trade_counts = [
        item.get("preRealTickMetrics", {}).get("tradeCountObserved")
        for item in survivors
        if isinstance(item.get("preRealTickMetrics", {}).get("tradeCountObserved"), int)
    ]
    net_profit = [
        item.get("preRealTickMetrics", {}).get("netProfitIS")
        for item in survivors
        if isinstance(item.get("preRealTickMetrics", {}).get("netProfitIS"), (int, float))
    ]
    return {
        "survivorCount": len(survivors),
        "tradeCountObservedCount": len(trade_counts),
        "tradeCountMin": min(trade_counts) if trade_counts else None,
        "tradeCountMax": max(trade_counts) if trade_counts else None,
        "tradeCountMedian": statistics.median(trade_counts) if trade_counts else None,
        "netProfitIsMin": _round_metric(min(net_profit)) if net_profit else None,
        "netProfitIsMax": _round_metric(max(net_profit)) if net_profit else None,
        "allPresentInRetest0ByFilename": all(bool(item.get("presentInRetest0")) for item in survivors) if survivors else False,
        "anyPresentInTickByFilename": any(bool(item.get("presentInTick")) for item in survivors),
        "directProfitFactorAvailable": any(bool(item.get("metricAvailability", {}).get("profitFactorDirect")) for item in survivors),
    }


def _trade_rule_redesign(summary: dict[str, Any], tick_filters: dict[str, Any]) -> dict[str, Any]:
    trade_min = summary.get("tradeCountMin")
    trade_max = summary.get("tradeCountMax")
    current_abs = next((item for item in tick_filters.get("absoluteMainFilters") or [] if item.get("column") == "NumberOfTrades"), None)
    retention = next((item for item in tick_filters.get("relativePrecisionFilters") or [] if item.get("column") == "NumberOfTrades"), None)
    return {
        "currentAbsoluteTradeFilter": current_abs,
        "currentRetentionTradeFilter": retention,
        "diagnosticFinding": (
            "The 5 retest 1 survivors have observed pre-real-tick trade/order counts above 200, "
            "but there is no TICK survivor file, so after-real-tick trade retention cannot be measured from databank output."
        ),
        "recommendedRuleShape": "realTickTrades >= max(absoluteFloor, floor(priorValidationTrades * retentionRatio))",
        "recommendedPolicyForNextExperiment": {
            "preRegisterRuleBeforeRun": True,
            "useCurrentLotToRescue": False,
            "calibrateOnBroaderEvidence": True,
            "initialDiagnosticGrid": [
                {"retentionRatio": 0.60, "absoluteFloor": 120},
                {"retentionRatio": 0.65, "absoluteFloor": 120},
                {"retentionRatio": 0.70, "absoluteFloor": 150},
            ],
            "selectionRule": "choose one grid point before the next run; do not select after seeing TICK survivors",
        },
        "observedPreRealTickTradeRange": {"min": trade_min, "max": trade_max},
        "methodologyWarning": (
            "Because the first logged TICK REAL blocker is Profit Factor, the current lot does not prove whether "
            "absolute or retention trade filters would have passed. Trade-count changes must therefore be redesigned "
            "for the next experiment, not retrofitted into this one."
        ),
    }


def _next_experiment(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "recommendedNextGate": "BS-AI16",
        "recommendedExperiment": "new_capa1_experiment_with_pre_registered_tick_real_trade_rule_no_capa2",
        "why": (
            "The observed blocker is Capa1 TICK REAL Profit Factor before any Capa2 evidence exists. "
            "A Capa2 v6/v7 comparison is premature until a clean Capa1 TICK/Forward chain exists."
        ),
        "preferredOptions": [
            "change Capa1 hypothesis, direction, timeframe or family and run as a new branch",
            "repeat Capa1 only if TICK REAL trade rule is pre-registered as a new experiment",
            "defer v6 default vs v7 explicit Capa2 comparison until Capa1 has natural TICK/Forward survivors",
        ],
        "blockedOptions": [
            "start Capa2 from this lot",
            "relax filters to reinterpret this lot as passed",
            "claim trade-count failure from the log when Profit Factor was the first logged blocker",
        ],
        "capa2StartAllowed": False,
    }


def _audit_payload(
    project_root: str | Path,
    candidate_id: str,
    *,
    remap_suffix: str = DEFAULT_REMAP_SUFFIX,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
    action: str = "audit",
    write_evidence: bool = False,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    project_names = _target_project_names(root, candidate_id, remap_suffix)
    remote = _list_target_projects(remote_base_url, project_names) if remote_base_url else {
        "endpoint": "taskmanager/listProjects",
        "reachable": None,
        "matchCount": 0,
        "matches": [],
        "skipped": True,
    }
    snapshot = _host_snapshot(config, project_names)
    databanks = _databank_summary(config, project_names[0])

    retest0 = _sqx_files(config, project_names[0], "RETEST 0")
    retest1 = _sqx_files(config, project_names[0], "retest 1")
    tick = _sqx_files(config, project_names[0], "TICK")
    retest0_names = {item.name for item in retest0}
    tick_names = {item.name for item in tick}
    survivors = [
        _survivor_metrics(path, index, retest0_names=retest0_names, tick_names=tick_names)
        for index, path in enumerate(retest1, start=1)
    ]
    survivor_summary = _survivor_summary(survivors)
    tick_filters = _tick_real_filter_summary(config, project_names[0])
    trade_rule = _trade_rule_redesign(survivor_summary, tick_filters)
    next_experiment = _next_experiment(survivor_summary)

    blockers: list[str] = []
    warnings: list[str] = []
    if len(retest1) != 5:
        warnings.append("retest1_survivor_count_not_5")
    if len(tick) != 0:
        blockers.append("tick_databank_not_empty_unexpected_for_frozen_lot")
    if int(((snapshot.get("projectSnapshots") or [{}, {}])[1].get("databanksDir") or {}).get("fileCount") or 0) != 0:
        blockers.append("capa2_databanks_not_empty")

    payload: dict[str, Any] = {
        "ok": not blockers,
        "version": BS_AI15_TICK_REAL_DIAGNOSTIC_VERSION,
        "action": action,
        "status": BS_AI15_STATUS,
        "candidateId": candidate_id,
        "hostProfile": "sqx144_full",
        "remapSuffix": remap_suffix,
        "projectNames": project_names,
        "frozenLot": {
            "decision": BS_AI14_FROZEN_LOT_DECISION,
            "candidateState": "failed_for_capa2",
            "capa2StartAllowed": False,
            "rescueByRelaxingFiltersAllowed": False,
            "passStatesChanged": False,
            "firstLoggedTickBlocker": "Profit factor[Main data] >= 1.30",
            "firstLoggedTickBlockerCount": 5,
            "tickRealPassed": 0,
            "methodologyWarning": "trade_threshold_warning_not_proven_failed_by_log",
        },
        "remote": remote,
        "snapshot": snapshot,
        "databanks": databanks,
        "databankCounts": {
            "RETEST 0": len(retest0),
            "retest 1": len(retest1),
            "TICK": len(tick),
        },
        "tickRealFilters": tick_filters,
        "survivorAudit": {
            "summary": survivor_summary,
            "items": survivors,
        },
        "tradeRuleRedesign": trade_rule,
        "nextExperiment": next_experiment,
        "blockers": blockers,
        "warnings": warnings,
        "guards": {
            "readOnly": True,
            "projectStartRequested": False,
            "projectStopRequested": False,
            "capa2StartAllowed": False,
            "filterRelaxationAllowedForCurrentLot": False,
            "writesSqxHost": False,
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
    if write_evidence:
        evidence_ref = write_evidence_file(root, action, payload)
        payload["evidenceWritten"] = True
        payload["evidenceRef"] = evidence_ref
    else:
        payload["evidenceWritten"] = False
    _privacy_guard(payload)
    return payload


def status_payload(
    project_root: str | Path,
    candidate_id: str = DEFAULT_CANDIDATE_ID,
    *,
    remap_suffix: str = DEFAULT_REMAP_SUFFIX,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
) -> dict[str, Any]:
    return _audit_payload(
        project_root,
        candidate_id,
        remap_suffix=remap_suffix,
        remote_base_url=remote_base_url,
        action="status",
        write_evidence=False,
    )


def audit_payload(
    project_root: str | Path,
    candidate_id: str = DEFAULT_CANDIDATE_ID,
    *,
    remap_suffix: str = DEFAULT_REMAP_SUFFIX,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
    write_evidence: bool = False,
) -> dict[str, Any]:
    return _audit_payload(
        project_root,
        candidate_id,
        remap_suffix=remap_suffix,
        remote_base_url=remote_base_url,
        action="audit",
        write_evidence=write_evidence,
    )


def plan_payload(
    project_root: str | Path,
    candidate_id: str = DEFAULT_CANDIDATE_ID,
    *,
    remap_suffix: str = DEFAULT_REMAP_SUFFIX,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
) -> dict[str, Any]:
    payload = _audit_payload(
        project_root,
        candidate_id,
        remap_suffix=remap_suffix,
        remote_base_url=remote_base_url,
        action="plan",
        write_evidence=False,
    )
    payload["operatorDecisionNeededBeforeBSAI16"] = True
    payload["operatorChoices"] = [
        "ABRIR BS-AI16 NUEVO EXPERIMENTO CAPA1 SIN CAPA2",
        "CAMBIAR HIPOTESIS/DIRECCION/TIMEFRAME/FAMILIA ANTES DE BS-AI16",
        "SOLO ARCHIVAR BS-AI15 Y NO EJECUTAR OTRO EXPERIMENTO",
    ]
    return payload


def write_evidence_file(project_root: Path, action: str, payload: dict[str, Any]) -> str:
    _privacy_guard(payload)
    evidence_dir = project_root.joinpath(*EVIDENCE_DIR_PARTS)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    filename = f"bsai15_tick_real_diagnostic_{action}_{_utc_stamp()}.json"
    (evidence_dir / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return filename


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("status", "audit", "plan"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--candidate-id", default=DEFAULT_CANDIDATE_ID)
    parser.add_argument("--remap-suffix", default=DEFAULT_REMAP_SUFFIX)
    parser.add_argument("--remote-base-url", default=DEFAULT_REMOTE_BASE_URL)
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)

    if args.action == "plan":
        payload = plan_payload(
            args.project_root,
            args.candidate_id,
            remap_suffix=args.remap_suffix,
            remote_base_url=args.remote_base_url,
        )
    elif args.action == "audit":
        payload = audit_payload(
            args.project_root,
            args.candidate_id,
            remap_suffix=args.remap_suffix,
            remote_base_url=args.remote_base_url,
            write_evidence=args.write_evidence,
        )
    else:
        payload = status_payload(
            args.project_root,
            args.candidate_id,
            remap_suffix=args.remap_suffix,
            remote_base_url=args.remote_base_url,
        )

    _privacy_guard(payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
