from __future__ import annotations

import argparse
import json
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .bsai16_capa1_experiment_gate import (
    BS_AI16_STATUS,
    DEFAULT_ABSOLUTE_FLOOR,
    DEFAULT_RETENTION_RATIO,
    status_payload as bsai16_status_payload,
)
from .bsai_first_start_gate import (
    DEFAULT_REMOTE_BASE_URL,
    _host_snapshot,
    _http_json_get,
    _http_json_post_gzip_form,
    _load_config,
    _privacy_guard,
    _response_summary,
)


BS_AI17_CONTROLLED_IMPORT_START_VERSION = "bs-ai17-controlled-capa1-import-start-gate-v1"
BS_AI17_STATUS = "controlled_capa1_import_start_requested_no_capa2"
EVIDENCE_DIR_PARTS = (".local", "blocksettings_ai", "import_start_gate")
DEFAULT_EXPERIMENT_ID = "BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _artifact_path(project_root: Path, experiment_id: str) -> Path:
    return project_root / ".local" / "blocksettings_ai" / "capa1_experiments" / experiment_id / f"{experiment_id}.cfx"


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
                "hasTickRealTaskXml": "AutomaticRetest-Task2.xml" in names,
                "memberCount": len(names),
            }
    except Exception as exc:
        return {"exists": True, "zipValid": False, "errorCode": type(exc).__name__}


def _remote_project_match(remote_base_url: str, project_name: str) -> dict[str, Any]:
    try:
        data = _http_json_get(remote_base_url, "taskmanager/listProjects", timeout=30)
    except Exception as exc:
        return {
            "endpoint": "taskmanager/listProjects",
            "reachable": False,
            "projectName": project_name,
            "found": False,
            "errorCode": "remote_access_unavailable",
            "exceptionType": type(exc).__name__,
        }
    projects = list(data.get("projects") or [])
    match = next((item for item in projects if str(item.get("projectName") or "") == project_name), None)
    return {
        "endpoint": "taskmanager/listProjects",
        "reachable": True,
        "projectName": project_name,
        "found": match is not None,
        "tasks": int(match.get("tasks") or 0) if match else None,
        "databanks": int(match.get("databanks") or 0) if match else None,
        "strategies": int(match.get("strategies") or 0) if match else None,
        "hasUnresolvedResources": bool(match.get("hasUnresolvedResources")) if match else None,
        "sqxReturnedProjectPath": bool(match and match.get("filePath")),
        "sqxProjectPathStored": False,
        "totalProjectCount": len(projects),
    }


def _write_evidence(project_root: Path, payload: dict[str, Any]) -> str:
    _privacy_guard(payload)
    evidence_dir = project_root.joinpath(*EVIDENCE_DIR_PARTS)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    filename = f"bsai17_controlled_import_start_gate_{payload['action']}_{_utc_stamp()}.json"
    (evidence_dir / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return filename


def _base_payload(
    action: str,
    project_root: Path,
    experiment_id: str,
    *,
    accept_cross_broker_spread_warning: bool,
) -> tuple[dict[str, Any], Path, dict[str, Any], str]:
    config = _load_config(project_root)
    host_profile = str(config.get("sqx_host_profile") or "sqx144_full")
    artifact = _artifact_path(project_root, experiment_id)
    bsai16 = bsai16_status_payload(
        project_root,
        retention_ratio=DEFAULT_RETENTION_RATIO,
        absolute_floor=DEFAULT_ABSOLUTE_FLOOR,
    )
    target_project = str((bsai16.get("experiment") or {}).get("id") or experiment_id)
    spread = bsai16.get("spreadCostSanity") if isinstance(bsai16.get("spreadCostSanity"), dict) else {}
    spread_warn_count = int(spread.get("warnCount") or 0)
    blockers: list[str] = []
    warnings: list[str] = []
    if host_profile != "sqx144_full":
        blockers.append("host_profile_not_sqx144_full")
    if bsai16.get("status") != BS_AI16_STATUS or not bsai16.get("ok"):
        blockers.append("bsai16_prereg_gate_not_ready")
    if spread_warn_count and not accept_cross_broker_spread_warning:
        blockers.append("cross_broker_spread_warning_not_accepted_for_this_trial")
    if spread_warn_count and accept_cross_broker_spread_warning:
        warnings.append("cross_broker_spread_warning_accepted_for_this_trial_only")
    artifact_summary = _public_zip_summary(artifact)
    if not artifact_summary.get("zipValid") or not artifact_summary.get("hasConfigXml"):
        blockers.append("bsai16_local_artifact_invalid")
    payload: dict[str, Any] = {
        "ok": not blockers,
        "version": BS_AI17_CONTROLLED_IMPORT_START_VERSION,
        "action": action,
        "status": "controlled_capa1_import_start_preflight_ready" if not blockers else "controlled_capa1_import_start_preflight_blocked",
        "hostProfile": host_profile,
        "experimentId": experiment_id,
        "targetProject": target_project,
        "artifact": {
            **artifact_summary,
            "artifactRef": artifact.name if artifact.name else None,
        },
        "operatorApproval": {
            "explicitForBSAI17": True,
            "crossBrokerSpreadWarningAccepted": bool(accept_cross_broker_spread_warning),
            "acceptanceScope": "this_trial_only",
            "futureAssetBrokerInstrumentReviewRequired": True,
        },
        "bsai16": {
            "status": bsai16.get("status"),
            "preRegisteredRule": bsai16.get("preRegisteredTradeRule"),
            "spreadCostSanity": {
                "verdict": spread.get("verdict"),
                "failCount": spread.get("failCount"),
                "warnCount": spread.get("warnCount"),
                "policy": spread.get("policy"),
                "observedPrimaryChartSpreads": spread.get("observedPrimaryChartSpreads"),
                "observedCrossBrokerChartSpreads": spread.get("observedCrossBrokerChartSpreads"),
            },
        },
        "blockers": blockers,
        "warnings": warnings,
        "guards": {
            "capa1ImportAllowed": action in ("import-capa1", "start-capa1") and not blockers,
            "projectStartAllowed": action == "start-capa1" and not blockers,
            "capa2StartAllowed": False,
            "loadAsIsAllowed": False,
            "addMissingSymbolsAllowed": False,
            "directDataDbPatch": False,
            "directUserProjectsPatch": False,
            "directDatabankMutation": False,
            "migrationToolAllowed": False,
            "officialBlocksettingsPromotion": False,
            "sqx144UpdatePromotion": False,
            "hostImportMayWriteDataDb": action == "import-capa1",
            "hostImportMayWriteUserProjects": action == "import-capa1",
            "hostRunMayWriteDataDb": action == "start-capa1",
            "hostRunMayWriteUserProjects": action == "start-capa1",
            "hostRunMayMutateTargetDatabanks": action == "start-capa1",
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
    return payload, artifact, config, target_project


def preflight_payload(
    project_root: str | Path,
    *,
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
    accept_cross_broker_spread_warning: bool = False,
    write_evidence: bool = False,
) -> dict[str, Any]:
    root = _project_root(project_root)
    payload, _, config, target_project = _base_payload(
        "preflight",
        root,
        experiment_id,
        accept_cross_broker_spread_warning=accept_cross_broker_spread_warning,
    )
    remote = _remote_project_match(remote_base_url, target_project)
    if remote.get("reachable") is False:
        payload["blockers"].append("remote_access_unavailable")
    if remote.get("found"):
        if int(remote.get("strategies") or 0) > 0:
            payload["blockers"].append("target_project_already_has_strategies")
        elif int(remote.get("tasks") or 0) > 0:
            payload["warnings"].append("target_project_already_imported_clean_start_possible")
    payload["remote"] = remote
    payload["snapshot"] = _host_snapshot(config, [target_project])
    payload["ok"] = not payload["blockers"]
    payload["status"] = "controlled_capa1_import_start_preflight_ready" if payload["ok"] else "controlled_capa1_import_start_preflight_blocked"
    payload["nextAction"] = "start-capa1" if payload["ok"] and remote.get("found") else ("import-capa1" if payload["ok"] else "fix_blockers")
    if write_evidence:
        payload["evidenceFile"] = _write_evidence(root, payload)
    _privacy_guard(payload)
    return payload


def status_payload(
    project_root: str | Path,
    *,
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
    accept_cross_broker_spread_warning: bool = False,
) -> dict[str, Any]:
    root = _project_root(project_root)
    payload = preflight_payload(
        root,
        experiment_id=experiment_id,
        remote_base_url=remote_base_url,
        accept_cross_broker_spread_warning=accept_cross_broker_spread_warning,
        write_evidence=False,
    )
    payload["action"] = "status"
    return payload


def import_capa1_payload(
    project_root: str | Path,
    *,
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
    accept_cross_broker_spread_warning: bool = False,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = _project_root(project_root)
    preflight = preflight_payload(
        root,
        experiment_id=experiment_id,
        remote_base_url=remote_base_url,
        accept_cross_broker_spread_warning=accept_cross_broker_spread_warning,
    )
    payload, artifact, config, target_project = _base_payload(
        "import-capa1",
        root,
        experiment_id,
        accept_cross_broker_spread_warning=accept_cross_broker_spread_warning,
    )
    payload["preflightStatus"] = preflight.get("status")
    payload["preflightBlockers"] = preflight.get("blockers")
    payload["beforeRemote"] = preflight.get("remote")
    payload["beforeSnapshot"] = preflight.get("snapshot")
    if not preflight.get("ok"):
        payload.update({"ok": False, "status": "controlled_capa1_import_blocked_by_preflight"})
        if write_evidence:
            payload["evidenceFile"] = _write_evidence(root, payload)
        _privacy_guard(payload)
        return payload
    if (preflight.get("remote") or {}).get("found"):
        payload.update({"ok": False, "status": "controlled_capa1_import_blocked_project_already_exists"})
        payload["blockers"].append("target_project_already_imported")
        if write_evidence:
            payload["evidenceFile"] = _write_evidence(root, payload)
        _privacy_guard(payload)
        return payload

    try:
        response = _http_json_get(
            remote_base_url,
            "taskmanager/openProject",
            {"file": str(artifact), "loadAsIs": "false"},
            timeout=90,
        )
        exception_type = None
    except Exception as exc:
        response = {}
        exception_type = type(exc).__name__
    has_resources_xml = bool(str(response.get("resourcesXML") or "").strip())
    project_name = str(response.get("projectName") or "") or None
    after_remote = _remote_project_match(remote_base_url, target_project)
    payload.update(
        {
            "ok": bool(response.get("success")) and not response.get("error") and not has_resources_xml and after_remote.get("found"),
            "status": "controlled_capa1_imported_visible_no_start" if bool(response.get("success")) and not response.get("error") and not has_resources_xml else "controlled_capa1_import_failed_or_blocked",
            "remoteEndpoint": "taskmanager/openProject",
            "loadAsIsRequested": False,
            "loadAsIsEscalated": False,
            "projectStartRequested": False,
            "response": {
                **_response_summary(response, exception_type),
                "projectName": project_name,
                "hasResourcesXML": has_resources_xml,
                "hasConfigXML": bool(str(response.get("configXML") or "").strip()),
            },
            "afterRemote": after_remote,
            "afterSnapshot": _host_snapshot(config, [target_project]),
            "nextAction": "start-capa1" if after_remote.get("found") else "fix_import_before_start",
        }
    )
    if has_resources_xml:
        payload["blockers"].append("resource_resolution_required")
    if write_evidence:
        payload["evidenceFile"] = _write_evidence(root, payload)
    _privacy_guard(payload)
    return payload


def start_capa1_payload(
    project_root: str | Path,
    *,
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
    accept_cross_broker_spread_warning: bool = False,
    observe_seconds: int = 90,
    poll_seconds: int = 10,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = _project_root(project_root)
    preflight = preflight_payload(
        root,
        experiment_id=experiment_id,
        remote_base_url=remote_base_url,
        accept_cross_broker_spread_warning=accept_cross_broker_spread_warning,
    )
    payload, _, config, target_project = _base_payload(
        "start-capa1",
        root,
        experiment_id,
        accept_cross_broker_spread_warning=accept_cross_broker_spread_warning,
    )
    remote = preflight.get("remote") or {}
    payload["preflightStatus"] = preflight.get("status")
    payload["preflightBlockers"] = preflight.get("blockers")
    payload["beforeRemote"] = remote
    payload["beforeSnapshot"] = preflight.get("snapshot")
    start_blockers = list(preflight.get("blockers") or [])
    if not remote.get("found"):
        start_blockers.append("target_project_not_imported")
    if remote.get("hasUnresolvedResources"):
        start_blockers.append("target_project_has_unresolved_resources")
    if int(remote.get("strategies") or 0) > 0:
        start_blockers.append("target_project_already_has_strategies")
    if start_blockers:
        payload.update(
            {
                "ok": False,
                "status": "controlled_capa1_start_blocked_by_preflight",
                "preflightBlockers": start_blockers,
                "startResponse": None,
                "observations": [],
            }
        )
        if write_evidence:
            payload["evidenceFile"] = _write_evidence(root, payload)
        _privacy_guard(payload)
        return payload

    started_at = datetime.now(timezone.utc).isoformat()
    try:
        response = _http_json_post_gzip_form(remote_base_url, "project/start", {"projectName": target_project}, timeout=60)
        exception_type = None
    except Exception as exc:
        response = {}
        exception_type = type(exc).__name__

    observations: list[dict[str, Any]] = []
    end_time = time.monotonic() + max(0, int(observe_seconds))
    while time.monotonic() <= end_time:
        current_remote = _remote_project_match(remote_base_url, target_project)
        current_snapshot = _host_snapshot(config, [target_project])
        observations.append(
            {
                "atUtc": datetime.now(timezone.utc).isoformat(),
                "capa1Strategies": current_remote.get("strategies"),
                "capa1Tasks": current_remote.get("tasks"),
                "capa1HasUnresolvedResources": current_remote.get("hasUnresolvedResources"),
                "latestLogSize": (current_snapshot.get("latestLog") or {}).get("size"),
                "targetDatabanksFileCount": ((current_snapshot.get("projectSnapshots") or [{}])[0].get("databanksDir") or {}).get("fileCount"),
            }
        )
        if observe_seconds <= 0:
            break
        time.sleep(max(1, int(poll_seconds)))

    after_snapshot = _host_snapshot(config, [target_project])
    before_log_size = ((preflight.get("snapshot") or {}).get("latestLog") or {}).get("size")
    after_log_size = (after_snapshot.get("latestLog") or {}).get("size")
    payload.update(
        {
            "ok": bool(response.get("success")) and not response.get("error"),
            "status": BS_AI17_STATUS if bool(response.get("success")) and not response.get("error") else "controlled_capa1_start_failed",
            "startedAtUtc": started_at,
            "observeSeconds": observe_seconds,
            "pollSeconds": poll_seconds,
            "remoteEndpoint": "project/start",
            "projectStartRequested": True,
            "startResponse": _response_summary(response, exception_type),
            "afterRemote": _remote_project_match(remote_base_url, target_project),
            "afterSnapshot": after_snapshot,
            "observations": observations,
            "observedEffects": {
                "latestLogChanged": before_log_size != after_log_size,
                "capa2StartRequested": False,
            },
            "nextGate": "BS-AI18 monitor BSAI16 Capa1 run and decide no Capa2 until clean TICK/Forward",
        }
    )
    if write_evidence:
        payload["evidenceFile"] = _write_evidence(root, payload)
    _privacy_guard(payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("status", "preflight", "import-capa1", "start-capa1"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--experiment-id", default=DEFAULT_EXPERIMENT_ID)
    parser.add_argument("--remote-base-url", default=DEFAULT_REMOTE_BASE_URL)
    parser.add_argument("--accept-cross-broker-spread-warning", action="store_true")
    parser.add_argument("--observe-seconds", type=int, default=90)
    parser.add_argument("--poll-seconds", type=int, default=10)
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)

    kwargs = {
        "experiment_id": args.experiment_id,
        "remote_base_url": args.remote_base_url,
        "accept_cross_broker_spread_warning": args.accept_cross_broker_spread_warning,
    }
    if args.action == "status":
        payload = status_payload(args.project_root, **kwargs)
    elif args.action == "preflight":
        payload = preflight_payload(args.project_root, **kwargs, write_evidence=args.write_evidence)
    elif args.action == "import-capa1":
        payload = import_capa1_payload(args.project_root, **kwargs, write_evidence=True)
    else:
        payload = start_capa1_payload(
            args.project_root,
            **kwargs,
            observe_seconds=args.observe_seconds,
            poll_seconds=args.poll_seconds,
            write_evidence=True,
        )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
