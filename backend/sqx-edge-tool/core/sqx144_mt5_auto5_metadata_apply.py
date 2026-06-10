from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import quote

from . import sqx144_mt5_auto3_broker_catalog as auto3
from . import sqx144_mt5_auto6_metadata_stability as auto6
from . import sqx144_mt5_bridge as bridge


SQX144_MT5_AUTO5_VERSION = "sqx144-mt5-auto5-metadata-apply-gate-v1"
SQX144_MT5_AUTO5_PHASE = "SQX144-MT5-AUTO5"
SQX144_MT5_AUTO5_STATUS = "auto5_metadata_apply_gate_ready_bridge_json_no_apply"
READ_MODE = "sqlite_uri_mode_ro_query_only"
DEFAULT_BROKER = "darwinex"
DEFAULT_SPREAD_POLICY = "p90"
BACKUP_DIR_PARTS = (".local", "sqx144_mt5_auto5_metadata_apply", "backups")
PROCESS_NAMES = {
    "StrategyQuantX",
    "StrategyQuantX_nocheck",
    "StrategyQuantX_ui",
    "CodeEditor",
    "sqcli",
    "SQ.Client.CLI",
}
APPROVED_COLUMNS = ("DEFAULTSPREAD", "POINTVALUE", "TICKSIZE", "TICKSTEP")
IGNORED_AUTHORITIES = {
    "SOURCE": "preserve_sqx_source_authority",
    "BROKER_ID": "preserve_sqx_broker_authority",
    "DATA": "preserve_sqx_history_catalog",
    "ROWS": "preserve_sqx_history_catalog",
    "DATEFROM": "preserve_sqx_history_catalog",
    "DATETO": "preserve_sqx_history_catalog",
    "COMMISSIONS": "bridge_metadata_does_not_change_commission",
    "SWAP": "bridge_metadata_does_not_change_swap",
    "DEFAULTSLIPPAGE": "bridge_metadata_does_not_change_slippage",
}


class Auto5Error(RuntimeError):
    def __init__(self, code: str, *, details: dict[str, Any] | None = None):
        super().__init__(code)
        self.code = code
        self.details = details or {}


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _tool_root(project_root: Path) -> Path:
    return project_root / "backend" / "sqx-edge-tool"


def _config_path(project_root: Path) -> Path:
    return _tool_root(project_root) / "config.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_config(project_root: Path) -> dict[str, Any]:
    path = _config_path(project_root)
    if not path.is_file():
        raise Auto5Error("sqx_edge_config_missing")
    return _read_json(path)


def _sqlite_ro_uri(db_path: Path) -> str:
    return f"file:{quote(db_path.resolve(strict=False).as_posix(), safe=':/')}?mode=ro"


def _connect_readonly(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    if not path.is_file():
        raise Auto5Error("sqx_data_db_missing")
    conn = sqlite3.connect(_sqlite_ro_uri(path), uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn


def _connect_write(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    if not path.is_file():
        raise Auto5Error("sqx_data_db_missing")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _table_count(conn: sqlite3.Connection, table: str) -> int | None:
    try:
        return int(conn.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"])
    except Exception:
        return None


def _quick_check(conn: sqlite3.Connection) -> str:
    return str(conn.execute("PRAGMA quick_check").fetchone()[0])


def _response_path() -> Path:
    return bridge.DEFAULT_MT5_FILES_DIR / bridge.DEFAULT_RESPONSE_FILE


def _response_summary() -> dict[str, Any]:
    path = _response_path()
    if not path.is_file():
        return {"exists": False, "fileName": bridge.DEFAULT_RESPONSE_FILE}
    try:
        payload = _read_json(path)
    except Exception:
        return {"exists": True, "fileName": path.name, "jsonValid": False}
    return {
        "exists": True,
        "jsonValid": True,
        "fileName": path.name,
        "sha256": _sha256_file(path),
        "requestId": payload.get("requestId"),
        "symbol": payload.get("symbol"),
        "status": payload.get("status"),
    }


def _base_payload(action: str, host_profile: str) -> dict[str, Any]:
    return {
        "ok": False,
        "version": SQX144_MT5_AUTO5_VERSION,
        "phase": SQX144_MT5_AUTO5_PHASE,
        "statusMarker": SQX144_MT5_AUTO5_STATUS,
        "action": action,
        "host": "sqx144_full",
        "hostProfile": host_profile,
        "readMode": READ_MODE,
        "writesSqxHost": action in {"backup", "apply", "rollback"},
        "writesDataDb": action == "apply",
        "writesUserProjects": False,
        "mutatesDatabanks": False,
        "runsSqxTasks": False,
        "launchesMt5": False,
        "runsMt5Ea": False,
        "usesMigrationTool": False,
        "doesNotApplyToSqx": action != "apply",
        "doesNotApplyInstrumentConfig": action != "apply",
        "importExecutionAllowed": False,
        "directDbHistoryInsertAllowed": False,
        "privacy": {
            "localPathsReturned": False,
            "accountReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
            "sqlReturned": False,
            "rawBridgeResponseReturned": False,
        },
    }


def detect_sqx_processes() -> list[dict[str, Any]]:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        (
            "Get-Process -ErrorAction SilentlyContinue | "
            "Where-Object { $_.ProcessName -in @('StrategyQuantX','StrategyQuantX_nocheck','StrategyQuantX_ui','CodeEditor','sqcli','SQ.Client.CLI') } | "
            "Select-Object ProcessName,Id | ConvertTo-Json -Compress"
        ),
    ]
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=10)
    except Exception:
        return []
    if completed.returncode != 0 or not completed.stdout.strip():
        return []
    try:
        parsed = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return []
    rows = parsed if isinstance(parsed, list) else [parsed]
    return [
        {"processName": str(row.get("ProcessName") or ""), "pid": int(row.get("Id") or 0)}
        for row in rows
        if isinstance(row, dict) and str(row.get("ProcessName") or "") in PROCESS_NAMES
    ]


def _public_processes(processes: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"processName": str(process.get("processName") or process.get("ProcessName") or ""), "pid": int(process.get("pid") or process.get("Id") or 0)}
        for process in processes
    ]


def _require_zero_processes(process_checker: Callable[[], list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    processes = (process_checker or detect_sqx_processes)()
    if processes:
        raise Auto5Error("sqx_processes_must_be_zero", details={"processCount": len(processes), "processes": _public_processes(processes)})
    return processes


def _db_path(config: dict[str, Any], db_path: str | Path | None) -> Path:
    return Path(db_path or str(config.get("sqx_data_db") or ""))


def _instrument_row(conn: sqlite3.Connection, target: str) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT INSTRUMENT, POINTVALUE, TICKSIZE, TICKSTEP, DEFAULTSPREAD,
               DEFAULTSLIPPAGE, COMMISSIONS, SWAP, BROKER_ID
        FROM INSTRUMENTS
        WHERE INSTRUMENT = ?
        """,
        (target,),
    ).fetchone()
    return dict(row) if row else None


def _same_value(old_value: Any, new_value: Any) -> bool:
    try:
        return math.isclose(float(old_value), float(new_value), rel_tol=0.0, abs_tol=1e-9)
    except Exception:
        return str(old_value or "") == str(new_value or "")


def _plan_id(seed: dict[str, Any]) -> str:
    raw = json.dumps(seed, sort_keys=True, ensure_ascii=True, default=str).encode("utf-8")
    return f"auto5_meta_{hashlib.sha256(raw).hexdigest()[:16]}"


def _approval_phrase(
    *,
    broker_key: str,
    instrument: str,
    plan_id: str,
    backup_id: str,
    request_id: str,
    response_hash: str,
    spread_policy: str,
    fields: Iterable[str],
) -> str:
    field_text = ",".join(fields)
    return (
        "APRUEBO SQX144 MT5 AUTO5 METADATA APPLY "
        f"host=sqx144_full broker={broker_key} instrument={instrument} "
        f"plan={plan_id} backup={backup_id} request={request_id} "
        f"response={response_hash} spreadPolicy={spread_policy} fields={field_text} "
        "no_source_broker_data_history no_projects_no_databanks_no_tasks no_migration_tool"
    )


def _table_counts_for_db(db_path: Path) -> dict[str, int | None]:
    conn = _connect_readonly(db_path)
    try:
        return {
            "INSTRUMENTS": _table_count(conn, "INSTRUMENTS"),
            "DATA": _table_count(conn, "DATA"),
            "BROKER": _table_count(conn, "BROKER"),
        }
    finally:
        conn.close()


def status_payload(
    project_root: str | Path,
    *,
    db_path: str | Path | None = None,
    process_checker: Callable[[], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "")
    resolved_db = _db_path(config, db_path)
    processes = (process_checker or detect_sqx_processes)()
    response = _response_summary()
    blockers: list[str] = []
    if host_profile != "sqx144_full":
        blockers.append("host_profile_not_sqx144_full")
    if not resolved_db.is_file():
        blockers.append("sqx_data_db_missing")
    if not response.get("exists"):
        blockers.append("bridge_response_missing")
    elif response.get("jsonValid") is False:
        blockers.append("bridge_response_json_invalid")
    payload = _base_payload("status", host_profile)
    payload.update({
        "ok": not blockers,
        "status": "status_ready" if not blockers else "status_blocked",
        "response": response,
        "db": {"exists": resolved_db.is_file()},
        "processCount": len(processes),
        "processes": _public_processes(processes),
        "blockers": blockers,
    })
    return payload


def build_plan(
    project_root: str | Path,
    *,
    broker_key: str = DEFAULT_BROKER,
    symbol: str,
    spread_policy: str = DEFAULT_SPREAD_POLICY,
    db_path: str | Path | None = None,
    backup_id: str | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "")
    resolved_db = _db_path(config, db_path)
    payload = _base_payload("plan", host_profile)
    validation = auto3.bridge_validate_payload(root, broker_key=broker_key, symbol=symbol, spread_policy=spread_policy, db_path=resolved_db)
    blockers = list(validation.get("blockers") or [])
    if not validation.get("ok"):
        blockers.append("bridge_validation_not_ready")
    if validation.get("catalogDecision") != "ready_existing":
        blockers.append(f"catalog_not_ready_existing_{validation.get('catalogDecision')}")
    if host_profile != "sqx144_full":
        blockers.append("host_profile_not_sqx144_full")
    resolved = validation.get("symbolResolution") if isinstance(validation.get("symbolResolution"), dict) else {}
    target = str(resolved.get("targetInstrument") or symbol)
    conn = _connect_readonly(resolved_db)
    try:
        row = _instrument_row(conn, target)
        if row is None:
            blockers.append("target_instrument_missing_in_sqx")
            row = {}
        quick_check = _quick_check(conn)
        table_counts = {
            "INSTRUMENTS": _table_count(conn, "INSTRUMENTS"),
            "DATA": _table_count(conn, "DATA"),
            "BROKER": _table_count(conn, "BROKER"),
        }
    finally:
        conn.close()
    proposed = validation.get("proposedSqxFields") if isinstance(validation.get("proposedSqxFields"), dict) else {}
    changes: dict[str, dict[str, Any]] = {}
    noops: dict[str, Any] = {}
    for column in APPROVED_COLUMNS:
        if column not in proposed or proposed.get(column) is None:
            continue
        new_value = proposed[column]
        old_value = row.get(column)
        if _same_value(old_value, new_value):
            noops[column] = old_value
        else:
            changes[column] = {"old": old_value, "new": new_value}
    stability_report: dict[str, Any] | None = None
    if changes:
        try:
            stability_report = auto6.evaluate_payload(
                root,
                broker_key=broker_key,
                symbol=symbol,
                spread_policy=spread_policy,
                db_path=resolved_db,
            )
            if stability_report.get("decision") != auto6.ELIGIBLE_DECISION:
                blockers.append("stability_policy_not_satisfied")
        except Exception as exc:
            stability_report = {
                "ok": False,
                "status": "stability_policy_unavailable",
                "error": getattr(exc, "code", str(exc)),
                "policyId": auto6.POLICY_ID,
            }
            blockers.append("stability_policy_unavailable")
    response = _response_summary()
    request_id = str(validation.get("requestId") or response.get("requestId") or "")
    seed = {
        "version": SQX144_MT5_AUTO5_VERSION,
        "brokerKey": broker_key,
        "targetInstrument": target,
        "requestId": request_id,
        "responseHash": response.get("sha256"),
        "changes": changes,
    }
    plan_id = _plan_id(seed)
    payload.update({
        "ok": not blockers,
        "status": "plan_ready_apply_gated_offline" if not blockers else "plan_blocked",
        "brokerKey": str(broker_key).lower(),
        "targetInstrument": target,
        "sourceSymbol": validation.get("symbol"),
        "requestId": request_id,
        "response": response,
        "spreadPolicy": spread_policy,
        "spreadSamples": proposed.get("spreadSamples"),
        "planId": plan_id,
        "backupId": backup_id,
        "changes": changes,
        "noops": noops,
        "ignored": IGNORED_AUTHORITIES,
        "warnings": sorted(set((validation.get("warnings") or []) + ["metadata_apply_requires_separate_exact_gate"])),
        "blockers": sorted(set(blockers)),
        "stabilityPolicy": {
            "policyId": auto6.POLICY_ID,
            "decision": stability_report.get("decision") if stability_report else "not_required_no_metadata_diff",
            "status": stability_report.get("status") if stability_report else "not_required_no_metadata_diff",
            "futureApplyGateAllowed": bool(stability_report.get("futureApplyGateAllowed")) if stability_report else True,
            "policyReasons": stability_report.get("policyReasons") if stability_report else [],
        },
        "bridgeValidation": {
            "status": validation.get("status"),
            "decision": validation.get("decision"),
            "catalogDecision": validation.get("catalogDecision"),
        },
        "invariants": {
            "brokerId": row.get("BROKER_ID"),
            "preserveBrokerId": True,
            "preserveDataRows": True,
            "preserveSourceHistory": True,
            "quickCheck": quick_check,
        },
        "inverseRollbackData": {
            "targetInstrument": target,
            "oldValues": {column: change["old"] for column, change in changes.items()},
        },
        "approvalTemplate": _approval_phrase(
            broker_key=str(broker_key).lower(),
            instrument=target,
            plan_id=plan_id,
            backup_id=backup_id or "<backupId>",
            request_id=request_id or "<requestId>",
            response_hash=str(response.get("sha256") or "<responseHash>"),
            spread_policy=str(spread_policy),
            fields=sorted(changes),
        ),
        "tableCountsBefore": table_counts,
    })
    return payload


def audit_payload(project_root: str | Path, **kwargs: Any) -> dict[str, Any]:
    plan = build_plan(project_root, **kwargs)
    payload = dict(plan)
    payload["action"] = "audit"
    payload["status"] = "audit_diff_ready_readonly" if payload.get("ok") else "audit_blocked"
    payload["auditDiff"] = {
        "targetInstrument": payload.get("targetInstrument"),
        "changes": payload.get("changes"),
        "noops": payload.get("noops"),
        "ignored": payload.get("ignored"),
        "warnings": payload.get("warnings"),
    }
    return payload


def backup_payload(
    project_root: str | Path,
    *,
    db_path: str | Path | None = None,
    process_checker: Callable[[], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "")
    payload = _base_payload("backup", host_profile)
    if host_profile != "sqx144_full":
        payload.update({"status": "backup_blocked", "blockers": ["host_profile_not_sqx144_full"]})
        return payload
    _require_zero_processes(process_checker)
    source_db = _db_path(config, db_path)
    if not source_db.is_file():
        raise Auto5Error("sqx_data_db_missing")
    conn = _connect_readonly(source_db)
    try:
        quick_check = _quick_check(conn)
    finally:
        conn.close()
    if quick_check != "ok":
        raise Auto5Error("sqlite_quick_check_failed", details={"quickCheck": quick_check})
    backup_id = f"sqx144_mt5_auto5_meta_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    backup_root = root.joinpath(*BACKUP_DIR_PARTS, backup_id)
    backup_root.mkdir(parents=True, exist_ok=False)
    files: list[dict[str, Any]] = []
    for source in [source_db, source_db.with_name(source_db.name + "-wal"), source_db.with_name(source_db.name + "-shm"), _config_path(root), _response_path()]:
        if source.is_file():
            dest = backup_root / source.name
            shutil.copy2(source, dest)
            files.append({"name": source.name, "size": dest.stat().st_size, "sha256": _sha256_file(dest)})
    manifest = {
        "version": SQX144_MT5_AUTO5_VERSION,
        "backupId": backup_id,
        "createdUtc": datetime.now(timezone.utc).isoformat(),
        "hostProfile": host_profile,
        "quickCheck": quick_check,
        "tableCounts": _table_counts_for_db(source_db),
        "files": files,
        "privacy": {"localPathsReturned": False},
    }
    (backup_root / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    payload.update({
        "ok": True,
        "status": "backup_ready_apply_still_requires_exact_approval",
        "backupId": backup_id,
        "quickCheck": quick_check,
        "files": files,
        "tableCounts": manifest["tableCounts"],
    })
    return payload


def _load_backup_manifest(project_root: Path, backup_id: str) -> tuple[Path, dict[str, Any]]:
    if not backup_id or "/" in backup_id or "\\" in backup_id or ".." in backup_id:
        raise Auto5Error("invalid_backup_id")
    backup_root = project_root.joinpath(*BACKUP_DIR_PARTS, backup_id).resolve(strict=False)
    allowed_root = project_root.joinpath(*BACKUP_DIR_PARTS).resolve(strict=False)
    if allowed_root not in [backup_root, *backup_root.parents]:
        raise Auto5Error("backup_outside_allowed_root")
    manifest_path = backup_root / "manifest.json"
    if not manifest_path.is_file():
        raise Auto5Error("backup_manifest_missing")
    manifest = _read_json(manifest_path)
    if manifest.get("version") != SQX144_MT5_AUTO5_VERSION:
        raise Auto5Error("backup_manifest_version_mismatch")
    if manifest.get("backupId") != backup_id:
        raise Auto5Error("backup_manifest_id_mismatch")
    for item in manifest.get("files", []):
        backup_file = backup_root / str(item.get("name") or "")
        if not backup_file.is_file() or _sha256_file(backup_file) != item.get("sha256"):
            raise Auto5Error("backup_hash_mismatch", details={"file": item.get("name")})
    return backup_root, manifest


def apply_payload(
    project_root: str | Path,
    *,
    broker_key: str = DEFAULT_BROKER,
    symbol: str,
    spread_policy: str = DEFAULT_SPREAD_POLICY,
    db_path: str | Path | None = None,
    backup_id: str | None = None,
    approval: str | None = None,
    apply: bool = False,
    process_checker: Callable[[], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "")
    payload = _base_payload("apply", host_profile)
    if not apply:
        payload.update({"status": "apply_blocked_missing_apply_switch", "blockers": ["missing_apply_switch"]})
        return payload
    _require_zero_processes(process_checker)
    if not backup_id:
        raise Auto5Error("backup_id_required")
    _load_backup_manifest(root, backup_id)
    plan = build_plan(root, broker_key=broker_key, symbol=symbol, spread_policy=spread_policy, db_path=db_path, backup_id=backup_id)
    if approval != plan.get("approvalTemplate"):
        payload.update({
            "status": "apply_blocked_bad_approval",
            "blockers": ["exact_approval_phrase_required"],
            "expectedApproval": plan.get("approvalTemplate"),
            "planId": plan.get("planId"),
            "backupId": backup_id,
        })
        return payload
    if plan.get("blockers"):
        payload.update({"status": "apply_blocked", "blockers": plan["blockers"], "planId": plan.get("planId")})
        return payload
    changes = plan.get("changes") or {}
    if not changes:
        payload.update({
            "ok": True,
            "status": "apply_noop_all_fields_already_match",
            "planId": plan["planId"],
            "targetInstrument": plan["targetInstrument"],
            "backupId": backup_id,
        })
        return payload
    columns = sorted(changes)
    assignments = ", ".join(f"{column} = ?" for column in columns)
    values = [changes[column]["new"] for column in columns]
    resolved_db = _db_path(config, db_path)
    conn = _connect_write(resolved_db)
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            f"UPDATE INSTRUMENTS SET {assignments} WHERE INSTRUMENT = ? AND BROKER_ID = ?",
            (*values, plan["targetInstrument"], (plan.get("invariants") or {}).get("brokerId")),
        )
        changed_rows = int(conn.execute("SELECT changes()").fetchone()[0])
        if changed_rows != 1:
            raise Auto5Error("apply_update_count_mismatch", details={"changes": changed_rows})
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    payload.update({
        "ok": True,
        "status": "apply_completed_offline_instruments_only",
        "planId": plan["planId"],
        "targetInstrument": plan["targetInstrument"],
        "backupId": backup_id,
        "appliedColumns": columns,
        "requestId": plan.get("requestId"),
    })
    return payload


def verify_payload(project_root: str | Path, **kwargs: Any) -> dict[str, Any]:
    plan = build_plan(project_root, **kwargs)
    root = _project_root(project_root)
    config = _load_config(root)
    resolved_db = _db_path(config, kwargs.get("db_path"))
    conn = _connect_readonly(resolved_db)
    try:
        quick_check = _quick_check(conn)
    finally:
        conn.close()
    pending = plan.get("changes") or {}
    payload = dict(plan)
    payload["action"] = "verify"
    payload["quickCheck"] = quick_check
    payload["ok"] = not pending and quick_check == "ok" and not plan.get("blockers")
    payload["status"] = "verify_passed_all_approved_fields_match" if payload["ok"] else "verify_pending_diff_or_blocked"
    payload["pendingChanges"] = pending
    return payload


def rollback_payload(
    project_root: str | Path,
    *,
    backup_id: str,
    db_path: str | Path | None = None,
    process_checker: Callable[[], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "")
    payload = _base_payload("rollback", host_profile)
    _require_zero_processes(process_checker)
    backup_root, manifest = _load_backup_manifest(root, backup_id)
    target_db = _db_path(config, db_path)
    restored: list[str] = []
    for item in manifest.get("files", []):
        name = str(item.get("name") or "")
        if name in {"config.json", bridge.DEFAULT_RESPONSE_FILE}:
            continue
        source = backup_root / name
        if name == target_db.name:
            dest = target_db
        elif name == target_db.name + "-wal":
            dest = target_db.with_name(target_db.name + "-wal")
        elif name == target_db.name + "-shm":
            dest = target_db.with_name(target_db.name + "-shm")
        else:
            raise Auto5Error("unexpected_backup_file", details={"file": name})
        shutil.copy2(source, dest)
        if _sha256_file(dest) != item.get("sha256"):
            raise Auto5Error("rollback_hash_mismatch", details={"file": name})
        restored.append(name)
    payload.update({
        "ok": True,
        "status": "rollback_restored_known_auto5_backup",
        "backupId": backup_id,
        "restoredFiles": restored,
        "tableCounts": _table_counts_for_db(target_db),
    })
    return payload


def _handle_error(action: str, project_root: str | Path, error: Auto5Error | auto3.Auto3Error | bridge.BridgeError) -> dict[str, Any]:
    try:
        config = _load_config(_project_root(project_root))
        host_profile = str(config.get("sqx_host_profile") or "")
    except Exception:
        host_profile = ""
    payload = _base_payload(action, host_profile)
    code = getattr(error, "code", str(error))
    payload.update({
        "status": "blocked",
        "error": code,
        "details": getattr(error, "details", {}),
        "blockers": [code],
    })
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SQX144 MT5 AUTO5 metadata apply gate")
    parser.add_argument("action", choices=("status", "audit", "plan", "backup", "apply", "verify", "rollback"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--broker", default=DEFAULT_BROKER)
    parser.add_argument("--symbol", default="")
    parser.add_argument("--spread-policy", default=DEFAULT_SPREAD_POLICY)
    parser.add_argument("--backup-id", default=None)
    parser.add_argument("--approval", default=None)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "status":
            payload = status_payload(args.project_root, db_path=args.db_path)
        elif args.action == "audit":
            payload = audit_payload(args.project_root, broker_key=args.broker, symbol=args.symbol, spread_policy=args.spread_policy, db_path=args.db_path)
        elif args.action == "plan":
            payload = build_plan(args.project_root, broker_key=args.broker, symbol=args.symbol, spread_policy=args.spread_policy, db_path=args.db_path, backup_id=args.backup_id)
        elif args.action == "backup":
            payload = backup_payload(args.project_root, db_path=args.db_path)
        elif args.action == "apply":
            payload = apply_payload(
                args.project_root,
                broker_key=args.broker,
                symbol=args.symbol,
                spread_policy=args.spread_policy,
                db_path=args.db_path,
                backup_id=args.backup_id,
                approval=args.approval,
                apply=args.apply,
            )
        elif args.action == "verify":
            payload = verify_payload(args.project_root, broker_key=args.broker, symbol=args.symbol, spread_policy=args.spread_policy, db_path=args.db_path)
        else:
            if not args.backup_id:
                raise Auto5Error("backup_id_required")
            payload = rollback_payload(args.project_root, backup_id=args.backup_id, db_path=args.db_path)
    except (Auto5Error, auto3.Auto3Error, bridge.BridgeError) as exc:
        payload = _handle_error(args.action, args.project_root, exc)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
