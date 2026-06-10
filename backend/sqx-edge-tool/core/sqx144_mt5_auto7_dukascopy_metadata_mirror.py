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


SQX144_MT5_AUTO7_VERSION = "sqx144-mt5-auto7-dukascopy-metadata-mirror-v1"
SQX144_MT5_AUTO7_PHASE = "SQX144-MT5-AUTO7"
SQX144_MT5_AUTO7_STATUS = "auto7_dukascopy_metadata_mirror_source_ready_no_apply_no_install"
READ_MODE = "sqlite_uri_mode_ro_query_only"
BACKUP_DIR_PARTS = (".local", "sqx144_mt5_auto7_dukascopy_mirror", "backups")
PROCESS_NAMES = {
    "StrategyQuantX",
    "StrategyQuantX_nocheck",
    "StrategyQuantX_ui",
    "CodeEditor",
    "sqcli",
    "SQ.Client.CLI",
}
APPROVED_COLUMNS = (
    "DEFAULTSPREAD",
    "POINTVALUE",
    "TICKSIZE",
    "TICKSTEP",
    "DEFAULTSLIPPAGE",
    "ORDERSIZEMULTIPLIER",
    "ORDERSIZESTEP",
    "COMMISSIONS",
    "SWAP",
)
PRESERVED_AUTHORITIES = {
    "BROKER_ID": "preserve_target_broker_profile",
    "SOURCE": "preserve_sqx_data_source_authority",
    "DATA": "preserve_sqx_history_catalog",
    "ROWS": "preserve_sqx_history_catalog",
    "DATEFROM": "preserve_sqx_history_catalog",
    "DATETO": "preserve_sqx_history_catalog",
    "PROJECTS": "not_touched",
    "databanks": "not_touched",
    "MT5": "not_used_for_dukascopy_mirror",
}


class Auto7Error(RuntimeError):
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
        raise Auto7Error("sqx_edge_config_missing")
    return _read_json(path)


def _sqlite_ro_uri(db_path: Path) -> str:
    return f"file:{quote(db_path.resolve(strict=False).as_posix(), safe=':/')}?mode=ro"


def _connect_readonly(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    if not path.is_file():
        raise Auto7Error("sqx_data_db_missing")
    conn = sqlite3.connect(_sqlite_ro_uri(path), uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn


def _connect_write(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    if not path.is_file():
        raise Auto7Error("sqx_data_db_missing")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _base_payload(action: str, host_profile: str = "sqx144_full") -> dict[str, Any]:
    writes_data_db = action == "apply"
    return {
        "ok": False,
        "version": SQX144_MT5_AUTO7_VERSION,
        "phase": SQX144_MT5_AUTO7_PHASE,
        "statusMarker": SQX144_MT5_AUTO7_STATUS,
        "action": action,
        "host": "sqx144_full",
        "hostProfile": host_profile,
        "readMode": READ_MODE,
        "mirrorPolicy": "dukascopy_copies_darwinex_sibling_metadata",
        "consumesMt5BridgeResponse": False,
        "writesMt5Files": False,
        "writesSqxHost": action in {"backup", "apply", "rollback"},
        "writesDataDb": writes_data_db,
        "writesUserProjects": False,
        "mutatesDatabanks": False,
        "runsSqxTasks": False,
        "launchesMt5": False,
        "runsMt5Ea": False,
        "usesMigrationTool": False,
        "doesNotApplyToSqx": not writes_data_db,
        "doesNotApplyInstrumentConfig": not writes_data_db,
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
        raise Auto7Error("sqx_processes_must_be_zero", details={"processCount": len(processes), "processes": _public_processes(processes)})
    return processes


def _db_path(config: dict[str, Any], db_path: str | Path | None) -> Path:
    return Path(db_path or str(config.get("sqx_data_db") or ""))


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    try:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    except Exception:
        return set()
    return {str(row["name"]) for row in rows}


def _table_count(conn: sqlite3.Connection, table: str) -> int | None:
    try:
        return int(conn.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"])
    except Exception:
        return None


def _quick_check(conn: sqlite3.Connection) -> str:
    return str(conn.execute("PRAGMA quick_check").fetchone()[0])


def _instrument_columns(conn: sqlite3.Connection) -> list[str]:
    columns = _table_columns(conn, "INSTRUMENTS")
    selected = [column for column in ("INSTRUMENT", "BROKER_ID", *APPROVED_COLUMNS) if column in columns]
    if "INSTRUMENT" not in selected:
        raise Auto7Error("instruments_shape_missing_instrument")
    return selected


def _instrument_row(conn: sqlite3.Connection, instrument: str) -> dict[str, Any] | None:
    selected = _instrument_columns(conn)
    quoted = ", ".join(f'"{column}"' for column in selected)
    row = conn.execute(f"SELECT {quoted} FROM INSTRUMENTS WHERE lower(INSTRUMENT) = lower(?)", (instrument,)).fetchone()
    return dict(row) if row else None


def _instrument_row_count(conn: sqlite3.Connection, instrument: str) -> int:
    return int(conn.execute("SELECT COUNT(*) FROM INSTRUMENTS WHERE lower(INSTRUMENT) = lower(?)", (instrument,)).fetchone()[0])


def _data_symbol_instrument_count(conn: sqlite3.Connection, symbol: str, instrument: str) -> int:
    columns = _table_columns(conn, "DATA")
    if "SYMBOL" not in columns or "INSTRUMENT" not in columns:
        return 0
    return int(
        conn.execute(
            "SELECT COUNT(*) FROM DATA WHERE lower(SYMBOL) = lower(?) AND lower(INSTRUMENT) = lower(?)",
            (symbol, instrument),
        ).fetchone()[0]
    )


def _same_value(old_value: Any, new_value: Any) -> bool:
    try:
        old_float = float(old_value)
        new_float = float(new_value)
        if math.isfinite(old_float) and math.isfinite(new_float):
            return math.isclose(old_float, new_float, rel_tol=0.0, abs_tol=1e-9)
    except Exception:
        pass
    return str(old_value or "") == str(new_value or "")


def _normalize_symbol(symbol: str) -> str:
    raw = "".join(str(symbol or "").strip().split())
    if not raw:
        raise Auto7Error("symbol_required")
    if "_" not in raw:
        raise Auto7Error("dukascopy_symbol_required", details={"symbol": raw})
    base, suffix = raw.split("_", 1)
    if suffix.lower() != "dukascopy":
        raise Auto7Error("dukascopy_symbol_required", details={"symbol": raw})
    if not base:
        raise Auto7Error("symbol_required")
    return f"{base.upper()}_dukascopy"


def _normalize_instrument_reference(instrument: str | None) -> str:
    raw = "".join(str(instrument or "").strip().split())
    if not raw:
        return ""
    if "_" not in raw:
        return raw.upper()
    base, suffix = raw.split("_", 1)
    suffix_lower = suffix.lower()
    if suffix_lower in {"darwinex", "dukascopy"}:
        return f"{base.upper()}_{suffix_lower}"
    return f"{base.upper()}_{suffix}"


def _darwinex_sibling(symbol: str) -> str:
    target = _normalize_symbol(symbol)
    return f"{target.split('_', 1)[0]}_darwinex"


def _plan_id(seed: dict[str, Any]) -> str:
    raw = json.dumps(seed, sort_keys=True, ensure_ascii=True, default=str).encode("utf-8")
    return f"auto7_duka_mirror_{hashlib.sha256(raw).hexdigest()[:16]}"


def _approval_phrase(*, target: str, source: str, plan_id: str, backup_id: str, fields: Iterable[str]) -> str:
    return (
        "APRUEBO SQX144 MT5 AUTO7 DUKASCOPY MIRROR APPLY "
        f"host=sqx144_full source={source} target={target} plan={plan_id} backup={backup_id} "
        f"fields={','.join(fields)} no_source_broker_data_history no_projects_no_databanks_no_tasks no_mt5 no_migration_tool"
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


def _build_plan(
    project_root: str | Path,
    *,
    symbol: str,
    db_path: str | Path | None = None,
    backup_id: str | None = None,
    linked_instrument: str | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "")
    target = _normalize_symbol(symbol)
    source = _darwinex_sibling(target)
    linked = _normalize_instrument_reference(linked_instrument)
    resolved_db = _db_path(config, db_path)
    payload = _base_payload("plan", host_profile)
    blockers: list[str] = []
    if host_profile != "sqx144_full":
        blockers.append("host_profile_not_sqx144_full")
    conn = _connect_readonly(resolved_db)
    try:
        quick_check = _quick_check(conn)
        table_counts = {
            "INSTRUMENTS": _table_count(conn, "INSTRUMENTS"),
            "DATA": _table_count(conn, "DATA"),
            "BROKER": _table_count(conn, "BROKER"),
        }
        source_count = _instrument_row_count(conn, source)
        target_count = _instrument_row_count(conn, target)
        linked_count = _instrument_row_count(conn, linked) if linked else 0
        linked_row = _instrument_row(conn, linked) if linked_count == 1 else {}
        linked_data_rows = _data_symbol_instrument_count(conn, target, linked) if linked else 0
        if source_count != 1:
            blockers.append("darwinex_sibling_missing" if source_count == 0 else "darwinex_sibling_ambiguous")
        if target_count != 1:
            blockers.append("dukascopy_target_missing" if target_count == 0 else "dukascopy_target_ambiguous")
        source_row = _instrument_row(conn, source) if source_count == 1 else {}
        target_row = _instrument_row(conn, target) if target_count == 1 else {}
    finally:
        conn.close()
    if (
        host_profile == "sqx144_full"
        and linked
        and linked.lower().endswith("_darwinex")
        and linked.lower() != target.lower()
        and linked_count == 1
        and linked_data_rows > 0
    ):
        noops = {column: linked_row.get(column) for column in APPROVED_COLUMNS if column in linked_row}
        seed = {
            "version": SQX144_MT5_AUTO7_VERSION,
            "mode": "data_symbol_uses_darwinex_instrument",
            "dataSymbol": target,
            "linkedInstrument": linked,
            "noops": noops,
            "linkedBrokerId": linked_row.get("BROKER_ID"),
        }
        plan_id = _plan_id(seed)
        payload.update({
            "ok": True,
            "status": "plan_ready_noop_data_symbol_uses_darwinex_instrument",
            "dataSymbol": target,
            "linkedInstrument": linked,
            "sourceInstrument": linked,
            "targetInstrument": linked,
            "dataSymbolUsesDarwinexInstrument": True,
            "planId": plan_id,
            "backupId": backup_id,
            "changes": {},
            "noops": noops,
            "approvedColumns": list(APPROVED_COLUMNS),
            "preserved": PRESERVED_AUTHORITIES,
            "warnings": ["dukascopy_data_symbol_already_uses_darwinex_instrument"],
            "blockers": [],
            "invariants": {
                "sourceBrokerId": linked_row.get("BROKER_ID"),
                "targetBrokerId": linked_row.get("BROKER_ID"),
                "preserveTargetBrokerId": True,
                "preserveDataRows": True,
                "preserveSourceHistory": True,
                "quickCheck": quick_check,
                "linkedDataRows": linked_data_rows,
            },
            "inverseRollbackData": {
                "targetInstrument": linked,
                "oldValues": {},
            },
            "approvalTemplate": "",
            "futureApplyRequired": False,
            "tableCountsBefore": table_counts,
        })
        return payload
    changes: dict[str, dict[str, Any]] = {}
    noops: dict[str, Any] = {}
    for column in APPROVED_COLUMNS:
        if column not in source_row or column not in target_row:
            continue
        source_value = source_row.get(column)
        target_value = target_row.get(column)
        if _same_value(target_value, source_value):
            noops[column] = target_value
        else:
            changes[column] = {"old": target_value, "new": source_value}
    seed = {
        "version": SQX144_MT5_AUTO7_VERSION,
        "sourceInstrument": source,
        "targetInstrument": target,
        "changes": changes,
        "targetBrokerId": target_row.get("BROKER_ID"),
    }
    plan_id = _plan_id(seed)
    fields = sorted(changes)
    payload.update({
        "ok": not blockers,
        "status": "plan_ready_apply_gated_offline" if not blockers else "plan_blocked",
        "sourceInstrument": source,
        "targetInstrument": target,
        "planId": plan_id,
        "backupId": backup_id,
        "changes": changes,
        "noops": noops,
        "approvedColumns": list(APPROVED_COLUMNS),
        "preserved": PRESERVED_AUTHORITIES,
        "warnings": ["dukascopy_metadata_mirror_requires_separate_exact_gate"],
        "blockers": sorted(set(blockers)),
        "invariants": {
            "sourceBrokerId": source_row.get("BROKER_ID"),
            "targetBrokerId": target_row.get("BROKER_ID"),
            "preserveTargetBrokerId": True,
            "preserveDataRows": True,
            "preserveSourceHistory": True,
            "quickCheck": quick_check,
        },
        "inverseRollbackData": {
            "targetInstrument": target,
            "oldValues": {column: change["old"] for column, change in changes.items()},
        },
        "approvalTemplate": _approval_phrase(
            target=target,
            source=source,
            plan_id=plan_id,
            backup_id=backup_id or "<backupId>",
            fields=fields,
        ),
        "tableCountsBefore": table_counts,
    })
    return payload


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
    blockers: list[str] = []
    if host_profile != "sqx144_full":
        blockers.append("host_profile_not_sqx144_full")
    if not resolved_db.is_file():
        blockers.append("sqx_data_db_missing")
    payload = _base_payload("status", host_profile)
    payload.update({
        "ok": not blockers,
        "status": "status_ready" if not blockers else "status_blocked",
        "db": {"exists": resolved_db.is_file()},
        "actions": ["status", "audit", "plan", "backup", "apply", "verify", "rollback"],
        "processCount": len(processes),
        "processes": _public_processes(processes),
        "approvedColumns": list(APPROVED_COLUMNS),
        "blockers": blockers,
    })
    return payload


def plan_payload(project_root: str | Path, **kwargs: Any) -> dict[str, Any]:
    return _build_plan(project_root, **kwargs)


def audit_payload(project_root: str | Path, **kwargs: Any) -> dict[str, Any]:
    plan = _build_plan(project_root, **kwargs)
    payload = dict(plan)
    payload["action"] = "audit"
    payload["status"] = "audit_diff_ready_readonly" if payload.get("ok") else "audit_blocked"
    payload["auditDiff"] = {
        "sourceInstrument": payload.get("sourceInstrument"),
        "targetInstrument": payload.get("targetInstrument"),
        "changes": payload.get("changes"),
        "noops": payload.get("noops"),
        "preserved": payload.get("preserved"),
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
        raise Auto7Error("sqx_data_db_missing")
    conn = _connect_readonly(source_db)
    try:
        quick_check = _quick_check(conn)
    finally:
        conn.close()
    if quick_check != "ok":
        raise Auto7Error("sqlite_quick_check_failed", details={"quickCheck": quick_check})
    backup_id = f"sqx144_mt5_auto7_duka_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    backup_root = root.joinpath(*BACKUP_DIR_PARTS, backup_id)
    backup_root.mkdir(parents=True, exist_ok=False)
    files: list[dict[str, Any]] = []
    for source in [source_db, source_db.with_name(source_db.name + "-wal"), source_db.with_name(source_db.name + "-shm"), _config_path(root)]:
        if source.is_file():
            dest = backup_root / source.name
            shutil.copy2(source, dest)
            files.append({"name": source.name, "size": dest.stat().st_size, "sha256": _sha256_file(dest)})
    manifest = {
        "version": SQX144_MT5_AUTO7_VERSION,
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
        raise Auto7Error("invalid_backup_id")
    backup_root = project_root.joinpath(*BACKUP_DIR_PARTS, backup_id).resolve(strict=False)
    allowed_root = project_root.joinpath(*BACKUP_DIR_PARTS).resolve(strict=False)
    if allowed_root not in [backup_root, *backup_root.parents]:
        raise Auto7Error("backup_outside_allowed_root")
    manifest_path = backup_root / "manifest.json"
    if not manifest_path.is_file():
        raise Auto7Error("backup_manifest_missing")
    manifest = _read_json(manifest_path)
    if manifest.get("version") != SQX144_MT5_AUTO7_VERSION:
        raise Auto7Error("backup_manifest_version_mismatch")
    if manifest.get("backupId") != backup_id:
        raise Auto7Error("backup_manifest_id_mismatch")
    for item in manifest.get("files", []):
        backup_file = backup_root / str(item.get("name") or "")
        if not backup_file.is_file() or _sha256_file(backup_file) != item.get("sha256"):
            raise Auto7Error("backup_hash_mismatch", details={"file": item.get("name")})
    return backup_root, manifest


def apply_payload(
    project_root: str | Path,
    *,
    symbol: str,
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
        raise Auto7Error("backup_id_required")
    _load_backup_manifest(root, backup_id)
    plan = _build_plan(root, symbol=symbol, db_path=db_path, backup_id=backup_id)
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
            f"UPDATE INSTRUMENTS SET {assignments} WHERE lower(INSTRUMENT) = lower(?) AND BROKER_ID = ?",
            (*values, plan["targetInstrument"], (plan.get("invariants") or {}).get("targetBrokerId")),
        )
        changed_rows = int(conn.execute("SELECT changes()").fetchone()[0])
        if changed_rows != 1:
            raise Auto7Error("apply_update_count_mismatch", details={"changes": changed_rows})
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    payload.update({
        "ok": True,
        "status": "apply_completed_offline_dukascopy_instrument_mirror_only",
        "planId": plan["planId"],
        "sourceInstrument": plan["sourceInstrument"],
        "targetInstrument": plan["targetInstrument"],
        "backupId": backup_id,
        "appliedColumns": columns,
    })
    return payload


def verify_payload(project_root: str | Path, **kwargs: Any) -> dict[str, Any]:
    plan = _build_plan(project_root, **kwargs)
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
    payload["status"] = "verify_passed_dukascopy_matches_darwinex_sibling" if payload["ok"] else "verify_pending_diff_or_blocked"
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
        if name == "config.json":
            continue
        source = backup_root / name
        if name == target_db.name:
            dest = target_db
        elif name == target_db.name + "-wal":
            dest = target_db.with_name(target_db.name + "-wal")
        elif name == target_db.name + "-shm":
            dest = target_db.with_name(target_db.name + "-shm")
        else:
            raise Auto7Error("unexpected_backup_file", details={"file": name})
        shutil.copy2(source, dest)
        if _sha256_file(dest) != item.get("sha256"):
            raise Auto7Error("rollback_hash_mismatch", details={"file": name})
        restored.append(name)
    payload.update({
        "ok": True,
        "status": "rollback_restored_known_auto7_backup",
        "backupId": backup_id,
        "restoredFiles": restored,
        "tableCounts": _table_counts_for_db(target_db),
    })
    return payload


def error_payload(action: str, error: Exception, *, project_root: str | Path = ".") -> dict[str, Any]:
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
    parser = argparse.ArgumentParser(description="SQX144 MT5 AUTO7 Dukascopy metadata mirror gate")
    parser.add_argument("action", choices=("status", "audit", "plan", "backup", "apply", "verify", "rollback"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--symbol", default="EURGBP_dukascopy")
    parser.add_argument("--backup-id", default=None)
    parser.add_argument("--approval", default=None)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "status":
            payload = status_payload(args.project_root, db_path=args.db_path)
        elif args.action == "audit":
            payload = audit_payload(args.project_root, symbol=args.symbol, db_path=args.db_path)
        elif args.action == "plan":
            payload = plan_payload(args.project_root, symbol=args.symbol, db_path=args.db_path, backup_id=args.backup_id)
        elif args.action == "backup":
            payload = backup_payload(args.project_root, db_path=args.db_path)
        elif args.action == "apply":
            payload = apply_payload(
                args.project_root,
                symbol=args.symbol,
                db_path=args.db_path,
                backup_id=args.backup_id,
                approval=args.approval,
                apply=args.apply,
            )
        elif args.action == "verify":
            payload = verify_payload(args.project_root, symbol=args.symbol, db_path=args.db_path)
        else:
            if not args.backup_id:
                raise Auto7Error("backup_id_required")
            payload = rollback_payload(args.project_root, backup_id=args.backup_id, db_path=args.db_path)
    except Auto7Error as exc:
        payload = error_payload(args.action, exc, project_root=args.project_root)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
