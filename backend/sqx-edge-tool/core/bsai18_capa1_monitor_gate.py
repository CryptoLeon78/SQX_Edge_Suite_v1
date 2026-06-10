from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .bsai17_controlled_import_start_gate import DEFAULT_EXPERIMENT_ID, _remote_project_match
from .bsai_first_start_gate import DEFAULT_REMOTE_BASE_URL, _host_snapshot, _load_config, _privacy_guard


BS_AI18_CAPA1_MONITOR_GATE_VERSION = "bs-ai18-capa1-monitor-gate-v1"
BS_AI18_STATUS = "monitoring_capa1_bsa16_no_capa2"
EVIDENCE_DIR_PARTS = (".local", "blocksettings_ai", "monitor_gate")


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _latest_log_age(snapshot: dict[str, Any]) -> dict[str, Any]:
    latest = dict(snapshot.get("latestLog") or {})
    last_write = latest.get("lastWriteTimeUtc")
    if last_write:
        try:
            parsed = datetime.fromisoformat(str(last_write).replace("Z", "+00:00"))
            latest["ageSeconds"] = max(0, int((datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).total_seconds()))
        except ValueError:
            latest["ageSeconds"] = None
    else:
        latest["ageSeconds"] = None
    return latest


def _databank_summary(config: dict[str, Any], project_name: str) -> dict[str, Any]:
    databanks_dir = Path(str(config.get("sqx_projects_dir") or "")) / project_name / "databanks"
    items: list[dict[str, Any]] = []
    if databanks_dir.is_dir():
        for child in sorted((item for item in databanks_dir.iterdir() if item.is_dir()), key=lambda item: item.name.lower()):
            files = [item for item in child.rglob("*") if item.is_file()]
            latest = max((item.stat().st_mtime for item in files), default=None)
            items.append(
                {
                    "databank": child.name,
                    "fileCount": len(files),
                    "sqxFiles": sum(1 for item in files if item.suffix.lower() == ".sqx"),
                    "latestWriteTimeUtc": datetime.fromtimestamp(latest, timezone.utc).isoformat() if latest else None,
                }
            )
    return {
        "exists": databanks_dir.is_dir(),
        "databankCount": len(items),
        "totalFiles": sum(int(item.get("fileCount") or 0) for item in items),
        "totalSqxFiles": sum(int(item.get("sqxFiles") or 0) for item in items),
        "items": items,
    }


def _databank_count(databanks: dict[str, Any], *names: str) -> int:
    wanted = {name.casefold() for name in names}
    return sum(
        int(item.get("sqxFiles") or 0)
        for item in databanks.get("items") or []
        if str(item.get("databank") or "").strip().casefold() in wanted
    )


def _sample_once(config: dict[str, Any], project_name: str, remote_base_url: str) -> dict[str, Any]:
    remote = _remote_project_match(remote_base_url, project_name)
    snapshot = _host_snapshot(config, [project_name])
    latest_log = _latest_log_age(snapshot)
    snapshot["latestLog"] = latest_log
    databanks = _databank_summary(config, project_name)
    project_snapshot = (snapshot.get("projectSnapshots") or [{}])[0]
    return {
        "atUtc": datetime.now(timezone.utc).isoformat(),
        "remote": remote,
        "project": {
            "projectDir": project_snapshot.get("projectDir"),
            "projectCfx": project_snapshot.get("projectCfx"),
            "databanksDir": project_snapshot.get("databanksDir"),
        },
        "latestLog": latest_log,
        "databanks": databanks,
    }


def _decision(samples: list[dict[str, Any]]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if not samples:
        return {
            "decision": "monitor_failed_no_samples_no_capa2",
            "blockers": ["no_samples_collected"],
            "warnings": [],
            "capa2StartAllowed": False,
            "projectStartAllowed": False,
            "projectStopAllowed": False,
        }
    first = samples[0]
    last = samples[-1]
    first_remote = first.get("remote") or {}
    last_remote = last.get("remote") or {}
    last_databanks = last.get("databanks") or {}
    first_log_size = int(((first.get("latestLog") or {}).get("size") or 0))
    last_log_size = int(((last.get("latestLog") or {}).get("size") or 0))
    first_strategies = first_remote.get("strategies")
    last_strategies = last_remote.get("strategies")
    strategy_delta = None
    if first_strategies is not None and last_strategies is not None:
        strategy_delta = int(last_strategies or 0) - int(first_strategies or 0)

    if not last_remote.get("reachable"):
        blockers.append("remote_access_unavailable")
    if last_remote.get("reachable") and not last_remote.get("found"):
        blockers.append("target_project_not_visible")
    if last_remote.get("hasUnresolvedResources"):
        blockers.append("target_project_has_unresolved_resources")

    latest_log_age = (last.get("latestLog") or {}).get("ageSeconds")
    log_changed = last_log_size != first_log_size
    retest0 = _databank_count(last_databanks, "RETEST 0", "retest0")
    retest1 = _databank_count(last_databanks, "retest 1", "RETEST 1", "retest1")
    tick = _databank_count(last_databanks, "TICK", "tick")
    forward = _databank_count(last_databanks, "Forward", "Foward", "forward", "foward")

    if latest_log_age is not None and int(latest_log_age) > 900:
        warnings.append("latest_log_stale_over_15m")
    if int(last_remote.get("strategies") or 0) == 0:
        warnings.append("capa1_no_strategies_reported_yet")
    if retest0 > 0 and tick == 0 and forward == 0:
        warnings.append("retest0_present_but_tick_forward_not_clean_yet")
    if tick == 0:
        warnings.append("tick_databank_empty_or_not_reached_yet")
    if forward == 0:
        warnings.append("forward_databank_empty_or_not_reached_yet")

    if blockers:
        decision = "monitor_blocked_review_required_no_capa2"
    elif log_changed or (strategy_delta is not None and strategy_delta > 0) or int(last_remote.get("strategies") or 0) > 0:
        decision = "continue_monitoring_capa1_active_no_capa2"
    elif "latest_log_stale_over_15m" in warnings:
        decision = "operator_review_or_stop_gate_required_no_capa2"
    else:
        decision = "continue_monitoring_warmup_no_capa2"

    clean_chain_ready = tick > 0 and forward > 0
    return {
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "capa1Strategies": int(last_remote.get("strategies") or 0) if last_remote.get("found") else None,
        "strategyDelta": strategy_delta,
        "latestLogChanged": log_changed,
        "latestLogAgeSeconds": latest_log_age,
        "retest0SqxFiles": retest0,
        "retest1SqxFiles": retest1,
        "tickSqxFiles": tick,
        "forwardSqxFiles": forward,
        "cleanTickForwardChainReady": clean_chain_ready,
        "capa2StartAllowed": False,
        "projectStartAllowed": False,
        "projectStopAllowed": False,
        "nextGate": "BS-AI18 continue monitor or later explicit stop/review gate; no Capa2 until clean real TICK/Forward evidence",
    }


def _base_payload(action: str, config: dict[str, Any], experiment_id: str, samples: list[dict[str, Any]]) -> dict[str, Any]:
    host_profile = str(config.get("sqx_host_profile") or "sqx144_full")
    decision = _decision(samples)
    payload = {
        "ok": not decision["blockers"],
        "version": BS_AI18_CAPA1_MONITOR_GATE_VERSION,
        "action": action,
        "status": BS_AI18_STATUS if not decision["blockers"] else "monitoring_capa1_blocked_review_required_no_capa2",
        "hostProfile": host_profile,
        "experimentId": experiment_id,
        "targetProject": experiment_id,
        "sampleCount": len(samples),
        "samples": samples,
        "decision": decision,
        "guards": {
            "readOnly": True,
            "taskmanagerListProjectsOnly": True,
            "projectStartRequested": False,
            "projectStopRequested": False,
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


def status_payload(
    project_root: str | Path,
    *,
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    sample = _sample_once(config, experiment_id, remote_base_url)
    return _base_payload("status", config, experiment_id, [sample])


def monitor_payload(
    project_root: str | Path,
    *,
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
    observe_seconds: int = 60,
    poll_seconds: int = 15,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    samples: list[dict[str, Any]] = []
    end_time = time.monotonic() + max(0, int(observe_seconds))
    while True:
        samples.append(_sample_once(config, experiment_id, remote_base_url))
        if time.monotonic() >= end_time or int(observe_seconds) <= 0:
            break
        time.sleep(max(1, int(poll_seconds)))
    payload = _base_payload("monitor", config, experiment_id, samples)
    payload["observeSeconds"] = observe_seconds
    payload["pollSeconds"] = poll_seconds
    if write_evidence:
        payload["evidenceFile"] = _write_evidence(root, payload)
    _privacy_guard(payload)
    return payload


def decision_template_payload(
    project_root: str | Path,
    *,
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
) -> dict[str, Any]:
    payload = status_payload(project_root, experiment_id=experiment_id, remote_base_url=remote_base_url)
    payload["action"] = "decision-template"
    payload["operatorChoices"] = [
        "CONTINUAR MONITORIZANDO BS-AI18 SIN CAPA2",
        "BLOQUEAR CAPA2 Y REVISAR SUPERVIVIENTES CUANDO SQX QUEDE IDLE",
        "SOLICITAR GATE EXPLICITO DE STOP BS-AI18 CAPA1 SIN CAPA2",
    ]
    payload["stopRequiresSeparateApproval"] = True
    _privacy_guard(payload)
    return payload


def _write_evidence(project_root: Path, payload: dict[str, Any]) -> str:
    _privacy_guard(payload)
    evidence_dir = project_root.joinpath(*EVIDENCE_DIR_PARTS)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    filename = f"bsai18_capa1_monitor_gate_{payload['action']}_{_utc_stamp()}.json"
    (evidence_dir / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return filename


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("status", "monitor", "decision-template"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--experiment-id", default=DEFAULT_EXPERIMENT_ID)
    parser.add_argument("--remote-base-url", default=DEFAULT_REMOTE_BASE_URL)
    parser.add_argument("--observe-seconds", type=int, default=60)
    parser.add_argument("--poll-seconds", type=int, default=15)
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)

    if args.action == "status":
        payload = status_payload(args.project_root, experiment_id=args.experiment_id, remote_base_url=args.remote_base_url)
    elif args.action == "decision-template":
        payload = decision_template_payload(args.project_root, experiment_id=args.experiment_id, remote_base_url=args.remote_base_url)
    else:
        payload = monitor_payload(
            args.project_root,
            experiment_id=args.experiment_id,
            remote_base_url=args.remote_base_url,
            observe_seconds=args.observe_seconds,
            poll_seconds=args.poll_seconds,
            write_evidence=args.write_evidence,
        )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
