from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .bsai_imported_project_review import review_payload
from .bsai_resource_compatibility import DEFAULT_CANDIDATE_ID, DEFAULT_REMAP_SUFFIX, candidate_pair_filenames, load_candidate_metadata


BS_AI13_FIRST_START_GATE_VERSION = "bs-ai13-first-manual-start-gate-v1"
DEFAULT_REMOTE_BASE_URL = "http://127.0.0.1:8080"
EVIDENCE_DIR_PARTS = (".local", "blocksettings_ai", "execution_gate")
SENSITIVE_PUBLIC_PATTERNS = (
    r"[A-Za-z]:[\\/]",
    r"<Project\b",
    r"<Task\b",
    r'"filePath"\s*:',
    r'"localPath"\s*:',
    r'"sqx_path"\s*:',
    r'"sqx_data_db"\s*:',
    r"\bpassword\b",
    r"\btoken\b",
    r"\bsecret\b",
)


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _tool_root(project_root: Path) -> Path:
    return project_root / "backend" / "sqx-edge-tool"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_config(project_root: Path) -> dict[str, Any]:
    path = _tool_root(project_root) / "config.json"
    if not path.is_file():
        raise FileNotFoundError("sqx_edge_config_missing")
    return _load_json(path)


def _candidate_recipe(project_root: Path, candidate_id: str) -> dict[str, Any]:
    meta = load_candidate_metadata(project_root, candidate_id)
    recipe = meta.get("recipe") if isinstance(meta.get("recipe"), dict) else {}
    if not recipe:
        raise ValueError("bsai_candidate_recipe_missing")
    return dict(recipe)


def _target_project_names(project_root: Path, candidate_id: str, remap_suffix: str) -> list[str]:
    recipe = _candidate_recipe(project_root, candidate_id)
    return [Path(name).stem for name in candidate_pair_filenames(recipe, candidate_id, suffix=remap_suffix)]


def _http_json_get(remote_base_url: str, endpoint: str, params: dict[str, Any] | None = None, timeout: int = 30) -> dict[str, Any]:
    base = remote_base_url.rstrip("/")
    query = ""
    if params:
        query = "?" + urllib.parse.urlencode({key: str(value) for key, value in params.items()})
    request = urllib.request.Request(f"{base}/{endpoint.strip('/')}{query}", method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", "replace"))


def _http_json_post_gzip_form(remote_base_url: str, endpoint: str, data: dict[str, Any], timeout: int = 30) -> dict[str, Any]:
    base = remote_base_url.rstrip("/")
    encoded = urllib.parse.urlencode({key: str(value) for key, value in data.items()}).encode("utf-8")
    request = urllib.request.Request(
        f"{base}/{endpoint.strip('/')}",
        data=gzip.compress(encoded),
        method="POST",
        headers={
            "Content-Type": "application/json; charset=x-user-defined-binary",
            "Content-Encoding": "gzip",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", "replace"))


def _sha256(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest().upper()
    except OSError:
        return None


def _file_summary(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"exists": False}
    item = path.stat()
    digest = _sha256(path)
    return {
        "exists": True,
        "size": item.st_size,
        "sha256": digest,
        "hashStatus": "ok" if digest else "unavailable_file_locked_or_unreadable",
        "lastWriteTimeUtc": datetime.fromtimestamp(item.st_mtime, timezone.utc).isoformat(),
    }


def _directory_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    files = [item for item in path.rglob("*") if item.is_file()]
    dirs = [item for item in path.rglob("*") if item.is_dir()]
    digest = hashlib.sha256()
    total_size = 0
    latest_mtime = None
    for item in sorted(files, key=lambda value: str(value.relative_to(path)).lower()):
        stat = item.stat()
        rel = str(item.relative_to(path)).replace("\\", "/")
        total_size += stat.st_size
        latest_mtime = stat.st_mtime if latest_mtime is None else max(latest_mtime, stat.st_mtime)
        digest.update(f"{rel}|{stat.st_size}|{int(stat.st_mtime_ns)}\n".encode("utf-8"))
    return {
        "exists": True,
        "fileCount": len(files),
        "dirCount": len(dirs),
        "totalSize": total_size,
        "latestMtimeUtc": datetime.fromtimestamp(latest_mtime, timezone.utc).isoformat() if latest_mtime else None,
        "digestRelSizeMtime": digest.hexdigest().upper(),
    }


def _project_from_list(projects: list[dict[str, Any]], project_name: str) -> dict[str, Any] | None:
    for item in projects:
        if str(item.get("projectName") or "") == project_name:
            return item
    return None


def _public_project_match(item: dict[str, Any] | None, project_name: str) -> dict[str, Any]:
    return {
        "projectName": project_name,
        "found": item is not None,
        "tasks": int(item.get("tasks") or 0) if item else None,
        "databanks": int(item.get("databanks") or 0) if item else None,
        "strategies": int(item.get("strategies") or 0) if item else None,
        "hasUnresolvedResources": bool(item.get("hasUnresolvedResources")) if item else None,
        "sqxReturnedProjectPath": bool(item and item.get("filePath")),
        "sqxProjectPathStored": False,
    }


def _list_target_projects(remote_base_url: str, project_names: list[str]) -> dict[str, Any]:
    try:
        data = _http_json_get(remote_base_url, "taskmanager/listProjects")
    except Exception as exc:
        return {
            "endpoint": "taskmanager/listProjects",
            "reachable": False,
            "matchCount": 0,
            "matches": [_public_project_match(None, name) for name in project_names],
            "errorCode": "remote_access_unavailable",
            "exceptionType": type(exc).__name__,
        }
    projects = list(data.get("projects") or [])
    matches = [_public_project_match(_project_from_list(projects, name), name) for name in project_names]
    return {
        "endpoint": "taskmanager/listProjects",
        "reachable": True,
        "matchCount": sum(1 for item in matches if item["found"]),
        "matches": matches,
    }


def _host_snapshot(config: dict[str, Any], project_names: list[str]) -> dict[str, Any]:
    projects_root = Path(str(config.get("sqx_projects_dir") or ""))
    log_root = Path(str(config.get("sqx_path") or "")) / "user" / "log" / "StrategyQuant"
    project_items = []
    for name in project_names:
        project_dir = projects_root / name
        project_items.append({
            "projectName": name,
            "projectDir": _directory_summary(project_dir),
            "projectCfx": _file_summary(project_dir / "project.cfx"),
            "databanksDir": _directory_summary(project_dir / "databanks"),
        })
    logs = sorted(log_root.glob("log_*.log"), key=lambda item: item.stat().st_mtime, reverse=True) if log_root.exists() else []
    return {
        "projectSnapshots": project_items,
        "latestLog": {
            "exists": bool(logs),
            "filename": logs[0].name if logs else None,
            "size": logs[0].stat().st_size if logs else None,
            "lastWriteTimeUtc": datetime.fromtimestamp(logs[0].stat().st_mtime, timezone.utc).isoformat() if logs else None,
        },
        "privacy": {
            "localPathsReturned": False,
            "rawLogReturned": False,
            "rawXmlReturned": False,
        },
    }


def _safe_public_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    if len(text) > 180:
        return "redacted_long_remote_text"
    for pattern in SENSITIVE_PUBLIC_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return "redacted_sensitive_remote_text"
    return text


def _response_summary(response: dict[str, Any], exception_type: str | None = None) -> dict[str, Any]:
    error = response.get("error")
    return {
        "success": response.get("success"),
        "errorPresent": bool(error or exception_type),
        "error": _safe_public_text(error),
        "keys": sorted(str(key) for key in response.keys()),
        "exceptionType": _safe_public_text(exception_type),
    }


def _privacy_guard(payload: dict[str, Any]) -> None:
    blob = json.dumps(payload, ensure_ascii=False)
    for pattern in SENSITIVE_PUBLIC_PATTERNS:
        if re.search(pattern, blob, flags=re.IGNORECASE):
            raise RuntimeError("bsai13_privacy_guard_failed")


def _base_payload(action: str, candidate_id: str, host_profile: str, remap_suffix: str, target_project: str | None) -> dict[str, Any]:
    return {
        "ok": False,
        "version": BS_AI13_FIRST_START_GATE_VERSION,
        "action": action,
        "candidateId": candidate_id,
        "hostProfile": host_profile,
        "remapSuffix": remap_suffix,
        "targetCapa": 1,
        "targetProject": target_project,
        "operatorApproval": "explicit",
        "manualStartApproved": True,
        "remoteEndpoint": "project/start",
        "runsSqxTasks": action == "start-capa1",
        "projectStartRequested": action == "start-capa1",
        "capa2StartAllowed": False,
        "officialBlocksettingsPromotion": False,
        "migrationToolAllowed": False,
        "hostRunMayWriteDataDb": action == "start-capa1",
        "hostRunMayWriteUserProjects": action == "start-capa1",
        "hostRunMayMutateTargetDatabanks": action == "start-capa1",
        "privacy": {
            "localPathsReturned": False,
            "rawXmlReturned": False,
            "rawLogReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
        },
    }


def _write_evidence(project_root: Path, payload: dict[str, Any]) -> str:
    _privacy_guard(payload)
    evidence_dir = project_root.joinpath(*EVIDENCE_DIR_PARTS)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    filename = f"bsai13_first_manual_start_gate_{payload['action']}_{_utc_stamp()}.json"
    (evidence_dir / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return filename


def preflight_payload(
    project_root: str | Path,
    candidate_id: str = DEFAULT_CANDIDATE_ID,
    *,
    remap_suffix: str = DEFAULT_REMAP_SUFFIX,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
    write_evidence: bool = False,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "sqx144_full")
    project_names = _target_project_names(root, candidate_id, remap_suffix)
    target_project = project_names[0]
    payload = _base_payload("preflight", candidate_id, host_profile, remap_suffix, target_project)
    bsai12 = review_payload(root, candidate_id, remap_suffix=remap_suffix, remote_base_url=remote_base_url)
    remote = _list_target_projects(remote_base_url, project_names)
    capa1 = next((item for item in remote["matches"] if item["projectName"] == target_project), None)
    capa2 = next((item for item in remote["matches"] if item["projectName"] == project_names[1]), None)
    blockers: list[str] = []
    if host_profile != "sqx144_full":
        blockers.append("host_profile_not_sqx144_full")
    if not bsai12.get("ok"):
        blockers.append("bsai12_review_not_ok")
    if remote.get("reachable") is False:
        blockers.append("remote_access_unavailable")
    if not capa1 or not capa1.get("found"):
        blockers.append("capa1_project_missing")
    if capa1 and capa1.get("tasks") != 14:
        blockers.append("capa1_task_count_not_14")
    if capa1 and capa1.get("strategies") != 0:
        blockers.append("capa1_not_first_start_strategies_already_present")
    if capa1 and capa1.get("hasUnresolvedResources"):
        blockers.append("capa1_has_unresolved_resources")
    if not capa2 or not capa2.get("found"):
        blockers.append("capa2_project_missing")
    if capa2 and capa2.get("strategies") != 0:
        blockers.append("capa2_not_clean")
    if capa2 and capa2.get("hasUnresolvedResources"):
        blockers.append("capa2_has_unresolved_resources")
    payload.update({
        "ok": not blockers,
        "status": "first_start_preflight_ready" if not blockers else "first_start_preflight_blocked",
        "projectNames": project_names,
        "remote": remote,
        "bsai12Status": bsai12.get("status"),
        "bsai12TargetFailCount": (bsai12.get("summary") or {}).get("targetFailCount"),
        "bsai12TargetWarnCount": (bsai12.get("summary") or {}).get("targetWarnCount"),
        "snapshot": _host_snapshot(config, project_names),
        "blockers": blockers,
        "nextAction": "start-capa1" if not blockers else "fix_blockers_before_start",
    })
    if write_evidence:
        payload["evidenceFile"] = _write_evidence(root, payload)
    _privacy_guard(payload)
    return payload


def status_payload(
    project_root: str | Path,
    candidate_id: str = DEFAULT_CANDIDATE_ID,
    *,
    remap_suffix: str = DEFAULT_REMAP_SUFFIX,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "sqx144_full")
    project_names = _target_project_names(root, candidate_id, remap_suffix)
    payload = _base_payload("status", candidate_id, host_profile, remap_suffix, project_names[0])
    remote = _list_target_projects(remote_base_url, project_names)
    payload.update({
        "ok": remote["matchCount"] == 2,
        "status": "first_start_status_ready_or_running" if remote["matchCount"] == 2 else "first_start_status_blocked",
        "projectNames": project_names,
        "remote": remote,
        "snapshot": _host_snapshot(config, project_names),
    })
    _privacy_guard(payload)
    return payload


def start_capa1_payload(
    project_root: str | Path,
    candidate_id: str = DEFAULT_CANDIDATE_ID,
    *,
    remap_suffix: str = DEFAULT_REMAP_SUFFIX,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
    observe_seconds: int = 90,
    poll_seconds: int = 10,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "sqx144_full")
    project_names = _target_project_names(root, candidate_id, remap_suffix)
    target_project = project_names[0]
    preflight = preflight_payload(root, candidate_id, remap_suffix=remap_suffix, remote_base_url=remote_base_url)
    payload = _base_payload("start-capa1", candidate_id, host_profile, remap_suffix, target_project)
    payload["preflightStatus"] = preflight.get("status")
    payload["preflightBlockers"] = preflight.get("blockers")
    payload["projectNames"] = project_names
    payload["beforeSnapshot"] = preflight.get("snapshot")
    if not preflight.get("ok"):
        payload.update({
            "ok": False,
            "status": "first_start_blocked_by_preflight",
            "startResponse": None,
            "observations": [],
        })
        if write_evidence:
            payload["evidenceFile"] = _write_evidence(root, payload)
        _privacy_guard(payload)
        return payload

    started_at = datetime.now(timezone.utc).isoformat()
    try:
        response = _http_json_post_gzip_form(remote_base_url, "project/start", {"projectName": target_project}, timeout=60)
        start_error = None
    except Exception as exc:
        response = {}
        start_error = type(exc).__name__

    observations = []
    end_time = time.monotonic() + max(0, observe_seconds)
    while time.monotonic() <= end_time:
        remote = _list_target_projects(remote_base_url, project_names)
        snapshot = _host_snapshot(config, project_names)
        capa1 = next((item for item in remote["matches"] if item["projectName"] == target_project), {})
        observations.append({
            "atUtc": datetime.now(timezone.utc).isoformat(),
            "capa1Strategies": capa1.get("strategies"),
            "capa1Tasks": capa1.get("tasks"),
            "capa1HasUnresolvedResources": capa1.get("hasUnresolvedResources"),
            "latestLogSize": (snapshot.get("latestLog") or {}).get("size"),
            "targetDatabanksFileCount": ((snapshot.get("projectSnapshots") or [{}])[0].get("databanksDir") or {}).get("fileCount"),
        })
        if observe_seconds <= 0:
            break
        time.sleep(max(1, poll_seconds))

    after_remote = _list_target_projects(remote_base_url, project_names)
    after_snapshot = _host_snapshot(config, project_names)
    response_success = bool(response.get("success"))
    response_error = response.get("error")
    log_changed = (
        (preflight.get("snapshot", {}).get("latestLog") or {}).get("size")
        != (after_snapshot.get("latestLog") or {}).get("size")
    )
    databanks_changed = (
        ((preflight.get("snapshot", {}).get("projectSnapshots") or [{}])[0].get("databanksDir") or {}).get("digestRelSizeMtime")
        != ((after_snapshot.get("projectSnapshots") or [{}])[0].get("databanksDir") or {}).get("digestRelSizeMtime")
    )
    payload.update({
        "ok": response_success and not response_error,
        "status": "first_start_requested_observed_no_capa2_start" if response_success and not response_error else "first_start_request_failed",
        "startedAtUtc": started_at,
        "observeSeconds": observe_seconds,
        "pollSeconds": poll_seconds,
        "startResponse": {
            **_response_summary(response, start_error),
        },
        "afterRemote": after_remote,
        "afterSnapshot": after_snapshot,
        "observations": observations,
        "observedEffects": {
            "latestLogChanged": log_changed,
            "targetDatabanksChanged": databanks_changed,
            "capa2StartRequested": False,
        },
        "nextGate": "BS-AI14 monitor Capa1 run and decide Capa2 start",
    })
    if write_evidence:
        payload["evidenceFile"] = _write_evidence(root, payload)
    _privacy_guard(payload)
    return payload


def stop_capa1_payload(
    project_root: str | Path,
    candidate_id: str = DEFAULT_CANDIDATE_ID,
    *,
    remap_suffix: str = DEFAULT_REMAP_SUFFIX,
    remote_base_url: str = DEFAULT_REMOTE_BASE_URL,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "sqx144_full")
    project_names = _target_project_names(root, candidate_id, remap_suffix)
    target_project = project_names[0]
    payload = _base_payload("stop-capa1", candidate_id, host_profile, remap_suffix, target_project)
    try:
        response = _http_json_get(remote_base_url, "project/stop", {"projectName": target_project}, timeout=30)
        stop_error = None
    except Exception as exc:
        response = {}
        stop_error = type(exc).__name__
    payload.update({
        "ok": bool(response.get("success")) and not response.get("error"),
        "status": "capa1_stop_requested" if response.get("success") and not response.get("error") else "capa1_stop_request_failed",
        "runsSqxTasks": False,
        "projectStartRequested": False,
        "stopResponse": {
            **_response_summary(response, stop_error),
        },
        "afterRemote": _list_target_projects(remote_base_url, project_names),
        "afterSnapshot": _host_snapshot(config, project_names),
    })
    if write_evidence:
        payload["evidenceFile"] = _write_evidence(root, payload)
    _privacy_guard(payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BS-AI13 first manual Start gate")
    parser.add_argument("action", choices=("status", "preflight", "start-capa1", "stop-capa1"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--candidate-id", default=DEFAULT_CANDIDATE_ID)
    parser.add_argument("--remap-suffix", default=DEFAULT_REMAP_SUFFIX)
    parser.add_argument("--remote-base-url", default=DEFAULT_REMOTE_BASE_URL)
    parser.add_argument("--observe-seconds", type=int, default=90)
    parser.add_argument("--poll-seconds", type=int, default=10)
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)

    if args.action == "status":
        payload = status_payload(args.project_root, args.candidate_id, remap_suffix=args.remap_suffix, remote_base_url=args.remote_base_url)
    elif args.action == "preflight":
        payload = preflight_payload(
            args.project_root,
            args.candidate_id,
            remap_suffix=args.remap_suffix,
            remote_base_url=args.remote_base_url,
            write_evidence=args.write_evidence,
        )
    elif args.action == "start-capa1":
        payload = start_capa1_payload(
            args.project_root,
            args.candidate_id,
            remap_suffix=args.remap_suffix,
            remote_base_url=args.remote_base_url,
            observe_seconds=args.observe_seconds,
            poll_seconds=args.poll_seconds,
            write_evidence=True,
        )
    else:
        payload = stop_capa1_payload(
            args.project_root,
            args.candidate_id,
            remap_suffix=args.remap_suffix,
            remote_base_url=args.remote_base_url,
            write_evidence=True,
        )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
