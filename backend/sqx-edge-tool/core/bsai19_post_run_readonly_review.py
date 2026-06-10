from __future__ import annotations

import argparse
import csv
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .bsai15_tick_real_diagnostic import (
    _sqx_files,
    _survivor_metrics,
    _survivor_summary,
    _tick_real_filter_summary,
)
from .bsai17_controlled_import_start_gate import DEFAULT_EXPERIMENT_ID
from .bsai18_capa1_monitor_gate import _databank_summary
from .bsai_first_start_gate import (
    DEFAULT_REMOTE_BASE_URL,
    _host_snapshot,
    _list_target_projects,
    _load_config,
    _privacy_guard,
)


BS_AI19_POST_RUN_READONLY_REVIEW_VERSION = "bs-ai19-post-run-readonly-review-v1"
BS_AI19_STATUS = "post_run_readonly_review_completed_no_capa2"
EVIDENCE_DIR_PARTS = (".local", "blocksettings_ai", "post_run_review")
BS_AI18_EVIDENCE_PATTERN = "bsai18_capa1_monitor_gate_monitor_*.json"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _databank_counts(config: dict[str, Any], project_name: str) -> dict[str, int]:
    return {
        "Results": len(_sqx_files(config, project_name, "Results")),
        "RETEST 0": len(_sqx_files(config, project_name, "RETEST 0")),
        "retest 1": len(_sqx_files(config, project_name, "retest 1")),
        "TICK": len(_sqx_files(config, project_name, "TICK")),
        "Forward": len(_sqx_files(config, project_name, "Forward")),
    }


def _latest_bsai18_evidence(project_root: Path) -> dict[str, Any]:
    evidence_dir = project_root / ".local" / "blocksettings_ai" / "monitor_gate"
    files = sorted(
        (item for item in evidence_dir.glob(BS_AI18_EVIDENCE_PATTERN) if item.is_file()),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    if not files:
        return {"found": False, "evidenceRef": None}

    latest = files[0]
    try:
        payload = json.loads(latest.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "found": True,
            "evidenceRef": latest.name,
            "readStatus": "failed",
            "errorCode": type(exc).__name__,
        }

    samples = list(payload.get("samples") or [])
    last = samples[-1] if samples else {}
    decision = payload.get("decision") if isinstance(payload.get("decision"), dict) else {}
    last_databanks = last.get("databanks") if isinstance(last.get("databanks"), dict) else {}
    counts: dict[str, int] = {}
    for item in last_databanks.get("items") or []:
        name = str(item.get("databank") or "")
        if name in {"Results", "RETEST 0", "retest 1", "TICK", "Forward"}:
            counts[name] = int(item.get("sqxFiles") or 0)

    return {
        "found": True,
        "evidenceRef": latest.name,
        "readStatus": "ok",
        "version": payload.get("version"),
        "status": payload.get("status"),
        "decision": decision.get("decision"),
        "sampleCount": int(payload.get("sampleCount") or len(samples)),
        "remoteReachable": (last.get("remote") or {}).get("reachable") if last else None,
        "cleanTickForwardChainReady": decision.get("cleanTickForwardChainReady"),
        "databankCounts": counts,
    }


def _process_summary() -> dict[str, Any]:
    try:
        if platform.system().lower() == "windows":
            completed = subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
            rows = csv.reader(completed.stdout.splitlines())
            names = [row[0].strip().lower() for row in rows if row]
        else:
            completed = subprocess.run(
                ["ps", "-eo", "comm="],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
            names = [line.strip().lower() for line in completed.stdout.splitlines() if line.strip()]
    except Exception as exc:
        return {"checked": False, "errorCode": type(exc).__name__}

    matched = sorted(
        {
            name
            for name in names
            if "strategyquant" in name
            or name.startswith("sqx")
            or name in {"java.exe", "javaw.exe", "java"}
            or name.startswith("terminal64")
        }
    )
    return {
        "checked": True,
        "sqxProcessVisible": any(name.startswith("sqx") for name in names),
        "strategyQuantProcessVisible": any("strategyquant" in name for name in names),
        "javaProcessVisible": any(name in {"java.exe", "javaw.exe", "java"} for name in names),
        "mt5TerminalVisible": any(name.startswith("terminal64") for name in names),
        "matchedProcessNames": matched[:16],
    }


def _survivor_audit(config: dict[str, Any], project_name: str) -> dict[str, Any]:
    retest0 = _sqx_files(config, project_name, "RETEST 0")
    retest1 = _sqx_files(config, project_name, "retest 1")
    tick = _sqx_files(config, project_name, "TICK")
    retest0_names = {item.name for item in retest0}
    tick_names = {item.name for item in tick}
    items = [
        _survivor_metrics(path, index, retest0_names=retest0_names, tick_names=tick_names)
        for index, path in enumerate(retest1, start=1)
    ]
    return {
        "summary": _survivor_summary(items),
        "items": items,
        "metricScope": "retest1_pre_real_tick_sanitized_partial_sqstats",
        "afterRealTickMetricsAvailable": bool(tick),
    }


def _decision(
    counts: dict[str, int],
    survivor_audit: dict[str, Any],
    tick_filters: dict[str, Any],
    process_summary: dict[str, Any],
    latest_monitor: dict[str, Any],
) -> dict[str, Any]:
    retest1 = int(counts.get("retest 1") or 0)
    tick = int(counts.get("TICK") or 0)
    forward = int(counts.get("Forward") or 0)
    clean_chain = tick > 0 and forward > 0

    methodology_blockers: list[str] = []
    warnings: list[str] = []
    if retest1 <= 0:
        warnings.append("retest1_empty_no_survivor_metrics")
    if tick <= 0:
        methodology_blockers.append("tick_databank_empty_no_real_tick_survivors")
    if forward <= 0:
        methodology_blockers.append("forward_databank_empty_no_forward_survivors")
    if retest1 > 0 and tick <= 0:
        warnings.append("retest1_survivors_exist_but_none_reached_tick_output")
    if latest_monitor.get("found") and latest_monitor.get("cleanTickForwardChainReady") is False:
        warnings.append("latest_bsai18_monitor_also_reports_no_clean_tick_forward_chain")
    if process_summary.get("checked") and (
        process_summary.get("sqxProcessVisible")
        or process_summary.get("strategyQuantProcessVisible")
        or process_summary.get("javaProcessVisible")
    ):
        warnings.append("sqx_or_java_process_visible_repeat_review_when_idle_before_any_future_gate")
    if not process_summary.get("checked"):
        warnings.append("process_readback_unavailable")

    trade_filters = tick_filters.get("absoluteMainFilters") or []
    trade_filter = next((item for item in trade_filters if item.get("column") == "NumberOfTrades"), None)
    relative_filters = tick_filters.get("relativePrecisionFilters") or []
    trade_retention = next((item for item in relative_filters if item.get("column") == "NumberOfTrades"), None)

    return {
        "decision": (
            "post_run_review_clean_tick_forward_chain_manual_gate_required_no_auto_capa2"
            if clean_chain
            else "post_run_review_no_capa2_tick_forward_empty"
        ),
        "status": "failed_candidate_for_capa2" if not clean_chain else "manual_methodology_review_required_before_capa2",
        "methodologyBlockers": methodology_blockers,
        "warnings": warnings,
        "cleanTickForwardChainReady": clean_chain,
        "retest1SurvivorsForLearningOnly": retest1,
        "tickSurvivors": tick,
        "forwardSurvivors": forward,
        "capa2StartAllowed": False,
        "projectStartAllowed": False,
        "projectStopAllowed": False,
        "filterRelaxationAllowedForCurrentLot": False,
        "passStatesChanged": False,
        "tradeRuleObserved": {
            "preRegisteredShape": "realTickTrades >= max(absoluteFloor, floor(priorValidationTrades * retentionRatio))",
            "absoluteMainFilter": trade_filter,
            "retentionFilter": trade_retention,
            "currentLotMayBeReinterpreted": False,
        },
        "survivorMetricCaveat": {
            "profitFactorDirectAvailable": bool((survivor_audit.get("summary") or {}).get("directProfitFactorAvailable")),
            "afterRealTickMetricsAvailable": bool(survivor_audit.get("afterRealTickMetricsAvailable")),
            "interpretation": "retest1 metrics describe pre-real-tick survivors only; empty TICK/Forward prevents Capa2 eligibility",
        },
        "nextGate": "BS-AI20 choose new preregistered Capa1 experiment or archive this branch; no Capa2 from this lot",
    }


def _base_payload(
    action: str,
    project_root: Path,
    experiment_id: str,
    *,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
) -> dict[str, Any]:
    config = _load_config(project_root)
    host_profile = str(config.get("sqx_host_profile") or "sqx144_full")
    remote = _list_target_projects(remote_base_url, [experiment_id]) if remote_base_url else {
        "endpoint": "taskmanager/listProjects",
        "reachable": None,
        "matchCount": 0,
        "matches": [],
        "skipped": True,
    }
    snapshot = _host_snapshot(config, [experiment_id])
    databanks = _databank_summary(config, experiment_id)
    counts = _databank_counts(config, experiment_id)
    latest_monitor = _latest_bsai18_evidence(project_root)
    processes = _process_summary()
    survivors = _survivor_audit(config, experiment_id)
    tick_filters = _tick_real_filter_summary(config, experiment_id)
    decision = _decision(counts, survivors, tick_filters, processes, latest_monitor)

    payload: dict[str, Any] = {
        "ok": True,
        "version": BS_AI19_POST_RUN_READONLY_REVIEW_VERSION,
        "action": action,
        "status": BS_AI19_STATUS,
        "hostProfile": host_profile,
        "experimentId": experiment_id,
        "targetProject": experiment_id,
        "targetCapa": 1,
        "remote": remote,
        "snapshot": snapshot,
        "latestBsai18Monitor": latest_monitor,
        "processReadback": processes,
        "databanks": databanks,
        "databankCounts": counts,
        "tickRealFilters": tick_filters,
        "survivorAudit": survivors,
        "decision": decision,
        "methodology": {
            "bsai16TradeRuleWasPreRegistered": True,
            "currentLotConclusion": "failed_candidate_for_capa2",
            "retest1SurvivorsCanInformNextExperiment": True,
            "retest1SurvivorsCanSeedCapa2": False,
            "filterRelaxationToRescueCurrentLotAllowed": False,
            "forcedPassAllowed": False,
            "capa2RequiresCleanTickForwardChain": True,
            "futureAssetBrokerInstrumentReviewRequired": True,
        },
        "guards": {
            "readOnly": True,
            "taskmanagerListProjectsOnly": True,
            "projectStartRequested": False,
            "projectStopRequested": False,
            "projectImportRequested": False,
            "capa2StartAllowed": False,
            "taskmanagerOpenProjectAllowed": False,
            "loadAsIsAllowed": False,
            "addMissingSymbolsAllowed": False,
            "directDataDbPatch": False,
            "directUserProjectsPatch": False,
            "directDatabankMutation": False,
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
    return payload


def write_evidence_file(project_root: Path, action: str, payload: dict[str, Any]) -> str:
    _privacy_guard(payload)
    evidence_dir = project_root.joinpath(*EVIDENCE_DIR_PARTS)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    filename = f"bsai19_post_run_readonly_review_{action}_{_utc_stamp()}.json"
    (evidence_dir / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return filename


def status_payload(
    project_root: str | Path,
    *,
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
) -> dict[str, Any]:
    return _base_payload("status", _project_root(project_root), experiment_id, remote_base_url=remote_base_url)


def review_payload(
    project_root: str | Path,
    *,
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
    write_evidence: bool = False,
) -> dict[str, Any]:
    root = _project_root(project_root)
    payload = _base_payload("review", root, experiment_id, remote_base_url=remote_base_url)
    if write_evidence:
        payload["evidenceWritten"] = True
        payload["evidenceRef"] = write_evidence_file(root, "review", payload)
    else:
        payload["evidenceWritten"] = False
    _privacy_guard(payload)
    return payload


def decision_template_payload(
    project_root: str | Path,
    *,
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
) -> dict[str, Any]:
    payload = _base_payload("decision-template", _project_root(project_root), experiment_id, remote_base_url=remote_base_url)
    payload["operatorDecisionNeededBeforeNextRun"] = True
    payload["allowedNextDecisions"] = [
        "ARCHIVAR BS-AI16 COMO FALLIDO PARA CAPA2",
        "ABRIR BS-AI20 NUEVO EXPERIMENTO CAPA1 PREREGISTRADO",
        "REVISAR CONFIGURACION DE ACTIVOS/BROKERS/INSTRUMENTOS ANTES DE OTRO RUN",
    ]
    payload["blockedDecisions"] = [
        "ARRANCAR CAPA2 DESDE ESTE LOTE",
        "RELAJAR FILTROS PARA RESCATAR ESTE LOTE",
        "FORZAR PASS STATES",
    ]
    _privacy_guard(payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("status", "review", "decision-template"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--experiment-id", default=DEFAULT_EXPERIMENT_ID)
    parser.add_argument("--remote-base-url", default=DEFAULT_REMOTE_BASE_URL)
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)

    if args.action == "review":
        payload = review_payload(
            args.project_root,
            experiment_id=args.experiment_id,
            remote_base_url=args.remote_base_url,
            write_evidence=args.write_evidence,
        )
    elif args.action == "decision-template":
        payload = decision_template_payload(
            args.project_root,
            experiment_id=args.experiment_id,
            remote_base_url=args.remote_base_url,
        )
    else:
        payload = status_payload(
            args.project_root,
            experiment_id=args.experiment_id,
            remote_base_url=args.remote_base_url,
        )

    _privacy_guard(payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
