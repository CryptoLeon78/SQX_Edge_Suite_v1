from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .bsai_first_start_gate import (
    DEFAULT_REMOTE_BASE_URL,
    _host_snapshot,
    _list_target_projects,
    _load_config,
    _privacy_guard,
    _target_project_names,
)
from .bsai_resource_compatibility import DEFAULT_CANDIDATE_ID, DEFAULT_REMAP_SUFFIX


BS_AI14_CAPA1_MONITOR_GATE_VERSION = "bs-ai14-capa1-monitor-decision-v1"
EVIDENCE_DIR_PARTS = (".local", "blocksettings_ai", "execution_gate")


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _databank_summary(config: dict[str, Any], project_name: str) -> dict[str, Any]:
    project_dir = Path(str(config.get("sqx_projects_dir") or "")) / project_name
    databanks_dir = project_dir / "databanks"
    summaries: list[dict[str, Any]] = []
    if databanks_dir.is_dir():
        for child in sorted((item for item in databanks_dir.iterdir() if item.is_dir()), key=lambda item: item.name.lower()):
            files = [item for item in child.rglob("*") if item.is_file()]
            latest = max((item.stat().st_mtime for item in files), default=None)
            summaries.append({
                "databank": child.name,
                "files": len(files),
                "sqxFiles": sum(1 for item in files if item.suffix.lower() == ".sqx"),
                "latestWriteUtc": datetime.fromtimestamp(latest, timezone.utc).isoformat() if latest else None,
            })
    return {
        "projectName": project_name,
        "databanksDirExists": databanks_dir.is_dir(),
        "items": summaries,
    }


def _latest_log_age(config: dict[str, Any]) -> dict[str, Any]:
    log_root = Path(str(config.get("sqx_path") or "")) / "user" / "log" / "StrategyQuant"
    logs = sorted(log_root.glob("log_*.log"), key=lambda item: item.stat().st_mtime, reverse=True) if log_root.exists() else []
    if not logs:
        return {"exists": False}
    item = logs[0]
    mtime = item.stat().st_mtime
    age_seconds = max(0, int(datetime.now(timezone.utc).timestamp() - mtime))
    return {
        "exists": True,
        "filename": item.name,
        "size": item.stat().st_size,
        "lastWriteTimeUtc": datetime.fromtimestamp(mtime, timezone.utc).isoformat(),
        "ageSeconds": age_seconds,
    }


def _project_match(remote: dict[str, Any], project_name: str) -> dict[str, Any]:
    for item in remote.get("matches") or []:
        if item.get("projectName") == project_name:
            return item
    return {"projectName": project_name, "found": False}


def _recommendation(remote: dict[str, Any], snapshot: dict[str, Any], databanks: dict[str, Any], project_names: list[str]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    capa1 = _project_match(remote, project_names[0])
    capa2 = _project_match(remote, project_names[1])
    latest_log = snapshot.get("latestLog") or {}

    if not remote.get("reachable"):
        blockers.append("remote_access_unavailable")
    if remote.get("matchCount") != 2:
        blockers.append("bsai_projects_not_both_visible")
    if capa1.get("hasUnresolvedResources"):
        blockers.append("capa1_has_unresolved_resources")
    if capa2.get("hasUnresolvedResources"):
        blockers.append("capa2_has_unresolved_resources")
    if int(capa2.get("strategies") or 0) != 0:
        blockers.append("capa2_not_intact_strategies_present")
    if int(((snapshot.get("projectSnapshots") or [{}, {}])[1].get("databanksDir") or {}).get("fileCount") or 0) != 0:
        blockers.append("capa2_not_intact_databank_files_present")

    if int(capa1.get("strategies") or 0) == 0:
        warnings.append("capa1_no_strategies_reported")
    if latest_log.get("ageSeconds") is not None and int(latest_log.get("ageSeconds") or 0) > 600:
        warnings.append("latest_log_stale_over_10m")

    retest0_files = 0
    for item in databanks.get("items") or []:
        if str(item.get("databank") or "").strip().casefold() in {"retest 0", "retest0"}:
            retest0_files += int(item.get("sqxFiles") or item.get("files") or 0)
    if retest0_files > 0 and retest0_files < 5:
        warnings.append("thin_retest0_survivor_count")

    if blockers:
        decision = "blocked_review_required_no_capa2"
    elif "latest_log_stale_over_10m" in warnings:
        decision = "stop_or_review_candidate_no_capa2"
    elif retest0_files > 0:
        decision = "review_retest0_survivors_no_capa2_yet"
    else:
        decision = "continue_monitoring_no_capa2"

    return {
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "capa1Strategies": int(capa1.get("strategies") or 0) if capa1.get("found") else None,
        "capa2Strategies": int(capa2.get("strategies") or 0) if capa2.get("found") else None,
        "retest0SqxFiles": retest0_files,
        "capa2StartAllowed": False,
        "stopAllowedByThisGate": False,
    }


def status_payload(
    project_root: str | Path,
    candidate_id: str,
    *,
    remap_suffix: str = DEFAULT_REMAP_SUFFIX,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    project_names = _target_project_names(root, candidate_id, remap_suffix)
    remote = _list_target_projects(remote_base_url, project_names)
    snapshot = _host_snapshot(config, project_names)
    latest_log = _latest_log_age(config)
    snapshot["latestLog"] = {**(snapshot.get("latestLog") or {}), **latest_log}
    databanks = _databank_summary(config, project_names[0])
    recommendation = _recommendation(remote, snapshot, databanks, project_names)
    payload = {
        "ok": not recommendation["blockers"],
        "version": BS_AI14_CAPA1_MONITOR_GATE_VERSION,
        "action": "status",
        "candidateId": candidate_id,
        "hostProfile": "sqx144_full",
        "remapSuffix": remap_suffix,
        "projectNames": project_names,
        "remote": remote,
        "snapshot": snapshot,
        "databanks": databanks,
        "recommendation": recommendation,
        "guards": {
            "readOnly": True,
            "projectStartRequested": False,
            "projectStopRequested": False,
            "capa2StartAllowed": False,
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
    _privacy_guard(payload)
    return payload


def decision_template_payload(project_root: str | Path, candidate_id: str, *, remap_suffix: str = DEFAULT_REMAP_SUFFIX, remote_base_url: str = DEFAULT_REMOTE_BASE_URL) -> dict[str, Any]:
    payload = status_payload(project_root, candidate_id, remap_suffix=remap_suffix, remote_base_url=remote_base_url)
    payload["action"] = "decision-template"
    payload["operatorChoices"] = [
        "CONTINUAR MONITORIZANDO BS-AI14 SIN CAPA2",
        "APRUEBO STOP BS-AI14 CAPA1 SIN CAPA2",
        "BLOQUEAR CAPA2 Y REVISAR SUPERVIVIENTES RETEST 0",
    ]
    payload["requiredApprovalForStop"] = "APRUEBO STOP BS-AI14 CAPA1 SIN CAPA2"
    return payload


def write_evidence(project_root: str | Path, action: str, payload: dict[str, Any]) -> Path:
    root = _project_root(project_root)
    evidence_dir = root.joinpath(*EVIDENCE_DIR_PARTS)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / f"bsai14_capa1_monitor_{action}_{_utc_stamp()}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("status", "monitor", "decision-template"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--candidate-id", default=DEFAULT_CANDIDATE_ID)
    parser.add_argument("--remap-suffix", default=DEFAULT_REMAP_SUFFIX)
    parser.add_argument("--remote-base-url", default=DEFAULT_REMOTE_BASE_URL)
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)

    if args.action == "decision-template":
        payload = decision_template_payload(
            args.project_root,
            args.candidate_id,
            remap_suffix=args.remap_suffix,
            remote_base_url=args.remote_base_url,
        )
    else:
        payload = status_payload(
            args.project_root,
            args.candidate_id,
            remap_suffix=args.remap_suffix,
            remote_base_url=args.remote_base_url,
        )
        payload["action"] = args.action

    if args.write_evidence:
        path = write_evidence(args.project_root, args.action, payload)
        payload["evidenceWritten"] = True
        payload["evidenceRef"] = path.name
    else:
        payload["evidenceWritten"] = False

    _privacy_guard(payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
