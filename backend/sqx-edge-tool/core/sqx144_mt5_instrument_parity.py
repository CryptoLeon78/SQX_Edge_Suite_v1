from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sqlite3
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import quote
from xml.etree import ElementTree as ET


SQX144_MT5_INSTRUMENT_PARITY_VERSION = "sqx144-mt5-instrument-parity-gate-v1"
STATUS_READY = "implemented_apply_gated_db_offline_usdjpy_pilot_ready"
DEFAULT_TARGET_INSTRUMENT = "USDJPY_darwinex"
DEFAULT_MT5_FILES_DIR = Path(
    "C:/Users/Ivan SQX/AppData/Roaming/MetaQuotes/Terminal/"
    "6C3C6A11D1C3791DD4DBF45421BF8028/MQL5/Files"
)
DEFAULT_XML_GLOB = "InstrumentInfo_*.xml"
BACKUP_DIR_PARTS = (".local", "sqx144_mt5_instrument_parity", "backups")
PROCESS_NAMES = {
    "StrategyQuantX",
    "StrategyQuantX_nocheck",
    "StrategyQuantX_ui",
    "CodeEditor",
    "sqcli",
    "SQ.Client.CLI",
}
APPROVED_COLUMN_TO_XML_FIELD = {
    "POINTVALUE": "pointValue",
    "TICKSIZE": "tickSize",
    "TICKSTEP": "tickStep",
    "DEFAULTSPREAD": "defaultSpread",
    "DEFAULTSLIPPAGE": "defaultSlippage",
    "SWAP": "swap",
    "ORDERSIZEMULTIPLIER": "orderSizeMultiplier",
    "ORDERSIZESTEP": "orderSizeStep",
}
COMMISSION_COLUMN = "COMMISSIONS"
READ_MODE = "sqlite_uri_mode_ro_query_only"

INSTRUMENT_INFO_ALLOWED_ATTRS = {
    "instrument",
    "description",
    "tickSize",
    "tickStep",
    "tickValueInMoney",
    "dateFrom",
    "dateTo",
    "rows",
    "totalDays",
    "defaultSpread",
    "defaultSlippage",
    "decimals",
    "commissions",
    "pointValue",
    "dataType",
    "recognizedFromOrders",
    "alias",
    "exchange",
    "country",
    "sector",
    "swap",
    "orderSizeMultiplier",
    "orderSizeStep",
}
INSTRUMENT_INFO_REQUIRED_ATTRS = {
    "instrument",
    "tickSize",
    "tickStep",
    "defaultSpread",
    "defaultSlippage",
    "pointValue",
    "dataType",
    "decimals",
    "commissions",
    "swap",
    "orderSizeMultiplier",
    "orderSizeStep",
}
NON_NEGATIVE_FLOAT_FIELDS = {
    "tickValueInMoney",
    "defaultSpread",
    "defaultSlippage",
}
POSITIVE_FLOAT_FIELDS = {
    "tickSize",
    "tickStep",
    "pointValue",
    "orderSizeMultiplier",
    "orderSizeStep",
}
INTEGER_FIELDS = {"dateFrom", "dateTo", "rows", "totalDays", "decimals", "dataType"}
SWAP_ALLOWED_ATTRS = {"use", "type", "long", "short", "tripleSwapOn", "rolloutHour"}


class GateError(RuntimeError):
    def __init__(self, code: str, *, details: dict[str, Any] | None = None):
        super().__init__(code)
        self.code = code
        self.details = details or {}


@dataclass(frozen=True)
class Mt5InstrumentInfo:
    source_symbol: str
    target_instrument: str
    numeric_fields: dict[str, float]
    integer_fields: dict[str, int]
    swap_xml: str
    commissions_xml: str
    warnings: tuple[str, ...]

    def proposed_values(self) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for column, xml_field in APPROVED_COLUMN_TO_XML_FIELD.items():
            if xml_field == "swap":
                values[column] = self.swap_xml
            else:
                values[column] = self.numeric_fields[xml_field]
        if self.commissions_xml.strip():
            values[COMMISSION_COLUMN] = self.commissions_xml.strip()
        return values

    def as_public_dict(self) -> dict[str, Any]:
        return {
            "sourceSymbol": self.source_symbol,
            "targetInstrument": self.target_instrument,
            "proposedColumns": sorted(self.proposed_values()),
            "warnings": list(self.warnings),
        }


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _tool_root(project_root: Path) -> Path:
    return project_root / "backend" / "sqx-edge-tool"


def _config_path(project_root: Path) -> Path:
    return _tool_root(project_root) / "config.json"


def _load_config(project_root: Path) -> dict[str, Any]:
    path = _config_path(project_root)
    if not path.is_file():
        raise GateError("sqx_edge_config_missing")
    return _read_json(path)


def _sqlite_ro_uri(db_path: Path) -> str:
    return f"file:{quote(db_path.resolve(strict=False).as_posix(), safe=':/')}?mode=ro"


def _connect_readonly(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    if not path.is_file():
        raise GateError("sqx_data_db_missing")
    conn = sqlite3.connect(_sqlite_ro_uri(path), uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn


def _connect_write(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    if not path.is_file():
        raise GateError("sqx_data_db_missing")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _table_count(conn: sqlite3.Connection, table: str) -> int | None:
    try:
        return int(conn.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"])
    except Exception:
        return None


def _quick_check(conn: sqlite3.Connection) -> str:
    return str(conn.execute("PRAGMA quick_check").fetchone()[0])


def _safe_float(text: str, field: str) -> float:
    try:
        value = float(str(text).strip())
    except Exception as exc:
        raise GateError("invalid_numeric", details={"field": field}) from exc
    if not math.isfinite(value):
        raise GateError("invalid_numeric", details={"field": field})
    if field in POSITIVE_FLOAT_FIELDS and value <= 0:
        raise GateError("invalid_numeric", details={"field": field, "rule": "positive"})
    if field in NON_NEGATIVE_FLOAT_FIELDS and value < 0:
        raise GateError("invalid_numeric", details={"field": field, "rule": "non_negative"})
    return value


def _safe_int(text: str, field: str) -> int:
    value_text = str(text).strip()
    try:
        value = int(value_text)
    except Exception as exc:
        raise GateError("invalid_integer", details={"field": field}) from exc
    if value < 0:
        raise GateError("invalid_integer", details={"field": field, "rule": "non_negative"})
    return value


def _reject_xml_entities(raw_text: str) -> None:
    upper = raw_text.upper()
    if "<!DOCTYPE" in upper or "<!ENTITY" in upper:
        raise GateError("xml_external_entities_rejected")


def _canonical_element_xml(element: ET.Element) -> str:
    return ET.tostring(element, encoding="unicode", short_empty_elements=True)


def _validate_inner_xml(value: str, root_tag: str, allowed_attrs: set[str]) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    _reject_xml_entities(text)
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise GateError("malformed_embedded_xml", details={"root": root_tag}) from exc
    if root.tag != root_tag:
        raise GateError("unexpected_embedded_xml_shape", details={"expected": root_tag})
    unknown = sorted(set(root.attrib) - allowed_attrs)
    if unknown:
        raise GateError("unexpected_embedded_xml_attr", details={"root": root_tag, "attrs": unknown})
    if root_tag == "Swap":
        for field in ("long", "short"):
            if field in root.attrib:
                _safe_float_allow_negative(root.attrib[field], f"Swap.{field}")
    return _canonical_element_xml(root)


def _safe_float_allow_negative(text: str, field: str) -> float:
    try:
        value = float(str(text).strip())
    except Exception as exc:
        raise GateError("invalid_numeric", details={"field": field}) from exc
    if not math.isfinite(value):
        raise GateError("invalid_numeric", details={"field": field})
    return value


def normalize_mt5_symbol_to_sqx(symbol: str, *, darwinex_suffix: str = "_darwinex") -> str:
    value = str(symbol or "").strip()
    if not value:
        raise GateError("instrument_symbol_missing")
    suffix_lower = darwinex_suffix.lower()
    if value.lower().endswith(suffix_lower):
        base = value[: -len(darwinex_suffix)]
        return f"{base.upper()}{darwinex_suffix}"
    return value


def parse_mt5_xml(xml_path: str | Path, *, darwinex_suffix: str = "_darwinex") -> dict[str, Any]:
    path = Path(xml_path)
    if not path.is_file():
        raise GateError("mt5_xml_missing")
    raw = path.read_bytes()
    xml_hash = _sha256_bytes(raw)
    try:
        raw_text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise GateError("mt5_xml_not_utf8") from exc
    _reject_xml_entities(raw_text)
    try:
        root = ET.fromstring(raw_text)
    except ET.ParseError as exc:
        raise GateError("malformed_xml") from exc
    if root.tag != "Instruments":
        raise GateError("unknown_required_shape", details={"expectedRoot": "Instruments"})

    instruments: list[Mt5InstrumentInfo] = []
    seen_normalized: set[str] = set()
    for child in list(root):
        if child.tag != "InstrumentInfo":
            raise GateError("unknown_required_shape", details={"unexpectedTag": child.tag})
        unknown = sorted(set(child.attrib) - INSTRUMENT_INFO_ALLOWED_ATTRS)
        if unknown:
            raise GateError("unknown_instrumentinfo_attr", details={"attrs": unknown})
        missing = sorted(INSTRUMENT_INFO_REQUIRED_ATTRS - set(child.attrib))
        if missing:
            raise GateError("missing_instrumentinfo_attr", details={"attrs": missing})

        source_symbol = str(child.attrib["instrument"]).strip()
        target = normalize_mt5_symbol_to_sqx(source_symbol, darwinex_suffix=darwinex_suffix)
        if target.lower() in seen_normalized:
            raise GateError("duplicate_normalized_symbol", details={"instrument": target})
        seen_normalized.add(target.lower())

        numeric_fields: dict[str, float] = {}
        for field in sorted(POSITIVE_FLOAT_FIELDS | NON_NEGATIVE_FLOAT_FIELDS):
            if field in child.attrib:
                numeric_fields[field] = _safe_float(child.attrib[field], field)
        integer_values = {field: _safe_int(child.attrib[field], field) for field in INTEGER_FIELDS if field in child.attrib}
        swap_xml = _validate_inner_xml(child.attrib.get("swap", ""), "Swap", SWAP_ALLOWED_ATTRS)
        commissions_xml = _validate_inner_xml(child.attrib.get("commissions", ""), "Method", {"type"})
        warnings: list[str] = []
        if not commissions_xml.strip():
            warnings.append("empty_mt5_commissions_ignored")
        if swap_xml.strip() and "rolloutHour=" not in swap_xml:
            warnings.append("swap_rollout_hour_missing_in_mt5_xml")
        if integer_values.get("rows", 0) == 0:
            warnings.append("mt5_xml_rows_zero_history_not_proven")
        if integer_values.get("dataType") is not None:
            warnings.append("mt5_datatype_ignored_source_history_authority_preserved")
        instruments.append(Mt5InstrumentInfo(
            source_symbol=source_symbol,
            target_instrument=target,
            numeric_fields=numeric_fields,
            integer_fields=integer_values,
            swap_xml=swap_xml,
            commissions_xml=commissions_xml,
            warnings=tuple(warnings),
        ))
    if not instruments:
        raise GateError("no_instrumentinfo_found")
    return {
        "xmlHash": xml_hash,
        "xmlFileName": path.name,
        "instruments": instruments,
    }


def _instrument_row(conn: sqlite3.Connection, target: str) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT INSTRUMENT, DESCRIPTION, POINTVALUE, TICKSIZE, TICKSTEP, DEFAULTSPREAD,
               COMMISSIONS, DATATYPE, EXCHANGE, COUNTRY, SECTOR, DEFAULTSLIPPAGE, SWAP,
               ORDERSIZEMULTIPLIER, ORDERSIZESTEP, BROKER_ID, MIN_DISTANCE
        FROM INSTRUMENTS
        WHERE INSTRUMENT = ?
        """,
        (target,),
    ).fetchone()
    return dict(row) if row else None


def _resolve_target_instrument(conn: sqlite3.Connection, parsed: Mt5InstrumentInfo) -> tuple[str, list[str]]:
    warnings: list[str] = []
    exact = _instrument_row(conn, parsed.target_instrument)
    if exact:
        return parsed.target_instrument, warnings
    rows = conn.execute(
        "SELECT INSTRUMENT FROM INSTRUMENTS WHERE lower(INSTRUMENT) = lower(?) ORDER BY INSTRUMENT",
        (parsed.target_instrument,),
    ).fetchall()
    if len(rows) == 1:
        target = str(rows[0]["INSTRUMENT"])
        warnings.append("target_instrument_case_resolved_from_sqx")
        return target, warnings
    if len(rows) > 1:
        raise GateError("ambiguous_target_instrument", details={"target": parsed.target_instrument})
    raise GateError("target_instrument_missing_in_sqx", details={"target": parsed.target_instrument})


def _public_old_new(old_value: Any, new_value: Any) -> dict[str, Any]:
    return {"old": old_value, "new": new_value}


def _same_value(old_value: Any, new_value: Any) -> bool:
    if isinstance(new_value, float):
        try:
            return math.isclose(float(old_value), new_value, rel_tol=0.0, abs_tol=1e-9)
        except Exception:
            return False
    return str(old_value or "") == str(new_value or "")


def _plan_id(plan_seed: dict[str, Any]) -> str:
    raw = json.dumps(plan_seed, sort_keys=True, ensure_ascii=True, default=str).encode("utf-8")
    return f"mt5meta_{hashlib.sha256(raw).hexdigest()[:16]}"


def _approval_phrase(host_profile: str, plan_id: str, backup_id: str, xml_hash: str, target: str) -> str:
    return (
        "APRUEBO SQX144 MT5 INSTRUMENT APPLY "
        f"host={host_profile} plan={plan_id} backup={backup_id} xml={xml_hash} "
        f"instrument={target} no_source_broker_history"
    )


def _base_payload(action: str, host_profile: str) -> dict[str, Any]:
    return {
        "ok": False,
        "version": SQX144_MT5_INSTRUMENT_PARITY_VERSION,
        "action": action,
        "hostProfile": host_profile,
        "status": STATUS_READY,
        "readMode": READ_MODE,
        "writesSqxHost": action in {"backup", "apply", "rollback"},
        "writesDataDb": action == "apply",
        "writesUserProjects": False,
        "mutatesDatabanks": False,
        "runsSqxTasks": False,
        "launchesMt5": False,
        "runsMt5Ea": False,
        "usesMigrationTool": False,
        "privacy": {
            "localPathsReturned": False,
            "rawXmlReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
        },
    }


def _find_default_xml(mt5_files_dir: Path = DEFAULT_MT5_FILES_DIR) -> Path:
    matches = sorted(mt5_files_dir.glob(DEFAULT_XML_GLOB), key=lambda item: item.stat().st_mtime, reverse=True)
    if not matches:
        raise GateError("mt5_xml_missing")
    return matches[0]


def _select_parsed_instrument(parsed_payload: dict[str, Any], target_instrument: str | None = None) -> Mt5InstrumentInfo:
    instruments: list[Mt5InstrumentInfo] = parsed_payload["instruments"]
    if target_instrument:
        matches = [item for item in instruments if item.target_instrument.lower() == target_instrument.lower()]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise GateError("duplicate_normalized_symbol", details={"instrument": target_instrument})
        raise GateError("target_instrument_missing_in_xml", details={"target": target_instrument})
    if len(instruments) != 1:
        raise GateError("target_instrument_required_for_multi_xml")
    return instruments[0]


def _load_plan_context(
    project_root: str | Path,
    xml_path: str | Path | None,
    db_path: str | Path | None,
    target_instrument: str | None,
) -> tuple[Path, dict[str, Any], Path, Path, dict[str, Any], Mt5InstrumentInfo, dict[str, Any], str, list[str]]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "")
    resolved_xml = Path(xml_path) if xml_path else _find_default_xml()
    resolved_db = Path(db_path or str(config.get("sqx_data_db") or ""))
    darwinex_suffix = str(config.get("darwinex_suffix") or "_darwinex")
    parsed_payload = parse_mt5_xml(resolved_xml, darwinex_suffix=darwinex_suffix)
    parsed = _select_parsed_instrument(parsed_payload, target_instrument)
    conn = _connect_readonly(resolved_db)
    try:
        resolved_target, target_warnings = _resolve_target_instrument(conn, parsed)
        row = _instrument_row(conn, resolved_target)
        if row is None:
            raise GateError("target_instrument_missing_in_sqx", details={"target": resolved_target})
        table_counts = {
            "INSTRUMENTS": _table_count(conn, "INSTRUMENTS"),
            "DATA": _table_count(conn, "DATA"),
            "BROKER": _table_count(conn, "BROKER"),
        }
    finally:
        conn.close()
    return root, config, resolved_xml, resolved_db, parsed_payload, parsed, row, resolved_target, target_warnings + list(parsed.warnings)


def build_plan(
    project_root: str | Path,
    *,
    xml_path: str | Path | None = None,
    db_path: str | Path | None = None,
    target_instrument: str | None = None,
    backup_id: str | None = None,
) -> dict[str, Any]:
    root, config, resolved_xml, resolved_db, parsed_payload, parsed, row, resolved_target, warnings = _load_plan_context(
        project_root,
        xml_path,
        db_path,
        target_instrument,
    )
    host_profile = str(config.get("sqx_host_profile") or "")
    payload = _base_payload("plan", host_profile)
    changes: dict[str, dict[str, Any]] = {}
    noops: dict[str, Any] = {}
    ignored: dict[str, Any] = {}
    proposed = parsed.proposed_values()
    for column, new_value in proposed.items():
        old_value = row.get(column)
        if _same_value(old_value, new_value):
            noops[column] = old_value
        else:
            changes[column] = _public_old_new(old_value, new_value)
    if not parsed.commissions_xml.strip():
        ignored[COMMISSION_COLUMN] = "empty_mt5_commissions_do_not_change_sqx"
    ignored.update({
        "SOURCE": "preserve_sqx_source_authority",
        "BROKER_ID": "preserve_sqx_broker_authority",
        "DATA": "preserve_history_catalog",
        "ROWS": "mt5_xml_history_fields_ignored",
        "DATEFROM": "mt5_xml_history_fields_ignored",
        "DATETO": "mt5_xml_history_fields_ignored",
        "DATATYPE": "preserve_sqx_datatype",
    })
    blockers: list[str] = []
    if host_profile != "sqx144_full":
        blockers.append("host_profile_not_sqx144_full")
    seed = {
        "version": SQX144_MT5_INSTRUMENT_PARITY_VERSION,
        "xmlHash": parsed_payload["xmlHash"],
        "targetInstrument": resolved_target,
        "changes": changes,
        "ignored": ignored,
    }
    plan_id = _plan_id(seed)
    payload.update({
        "ok": not blockers,
        "status": "plan_ready_apply_gated_offline" if not blockers else "plan_blocked",
        "xml": {
            "fileName": parsed_payload["xmlFileName"],
            "sha256": parsed_payload["xmlHash"],
        },
        "targetInstrument": resolved_target,
        "sourceSymbol": parsed.source_symbol,
        "mt5": parsed.as_public_dict(),
        "planId": plan_id,
        "backupId": backup_id,
        "changes": changes,
        "noops": noops,
        "ignored": ignored,
        "warnings": sorted(set(warnings)),
        "blockers": blockers,
        "inverseRollbackData": {
            "targetInstrument": resolved_target,
            "oldValues": {column: change["old"] for column, change in changes.items()},
        },
        "invariants": {
            "brokerId": row.get("BROKER_ID"),
            "preserveBrokerId": True,
            "preserveDataRows": True,
            "preserveSourceHistory": True,
        },
        "approvalTemplate": _approval_phrase(str(host_profile or "sqx144_full"), plan_id, backup_id or "<backupId>", parsed_payload["xmlHash"], resolved_target),
        "tableCountsBefore": _table_counts_for_db(resolved_db),
    })
    return payload


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
    xml_path: str | Path | None = None,
    db_path: str | Path | None = None,
    target_instrument: str | None = None,
    process_checker: Callable[[], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "")
    payload = _base_payload("status", host_profile)
    processes = (process_checker or detect_sqx_processes)()
    resolved_xml = Path(xml_path) if xml_path else None
    xml_exists = bool(resolved_xml and resolved_xml.is_file())
    if not resolved_xml:
        try:
            resolved_xml = _find_default_xml()
            xml_exists = True
        except GateError:
            xml_exists = False
    resolved_db = Path(db_path or str(config.get("sqx_data_db") or ""))
    blockers = []
    if host_profile != "sqx144_full":
        blockers.append("host_profile_not_sqx144_full")
    if not xml_exists:
        blockers.append("mt5_xml_missing")
    if not resolved_db.is_file():
        blockers.append("sqx_data_db_missing")
    payload.update({
        "ok": not blockers,
        "status": "status_ready" if not blockers else "status_blocked",
        "targetInstrument": target_instrument or DEFAULT_TARGET_INSTRUMENT,
        "xml": {"exists": xml_exists, "fileName": resolved_xml.name if resolved_xml else None},
        "db": {"exists": resolved_db.is_file()},
        "processCount": len(processes),
        "processes": _public_processes(processes),
        "blockers": blockers,
    })
    return payload


def audit_payload(
    project_root: str | Path,
    *,
    xml_path: str | Path | None = None,
    db_path: str | Path | None = None,
    target_instrument: str | None = None,
) -> dict[str, Any]:
    plan = build_plan(project_root, xml_path=xml_path, db_path=db_path, target_instrument=target_instrument)
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
        raise GateError("sqx_processes_must_be_zero", details={"processCount": len(processes), "processes": _public_processes(processes)})
    return processes


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
    source_db = Path(db_path or str(config.get("sqx_data_db") or ""))
    if not source_db.is_file():
        raise GateError("sqx_data_db_missing")
    conn = _connect_readonly(source_db)
    try:
        quick_check = _quick_check(conn)
    finally:
        conn.close()
    if quick_check != "ok":
        raise GateError("sqlite_quick_check_failed", details={"quickCheck": quick_check})
    backup_id = f"sqx144_mt5_instr_{_utc_stamp()}"
    backup_root = root.joinpath(*BACKUP_DIR_PARTS, backup_id)
    backup_root.mkdir(parents=True, exist_ok=False)
    files: list[dict[str, Any]] = []
    for source in [source_db, source_db.with_name(source_db.name + "-wal"), source_db.with_name(source_db.name + "-shm"), _config_path(root)]:
        if source.is_file():
            dest = backup_root / source.name
            shutil.copy2(source, dest)
            files.append({
                "name": source.name,
                "size": dest.stat().st_size,
                "sha256": _sha256_file(dest),
            })
    manifest = {
        "version": SQX144_MT5_INSTRUMENT_PARITY_VERSION,
        "backupId": backup_id,
        "createdUtc": datetime.now(timezone.utc).isoformat(),
        "hostProfile": host_profile,
        "quickCheck": quick_check,
        "tableCounts": _table_counts_for_db(source_db),
        "files": files,
        "privacy": {"localPathsReturned": False},
    }
    manifest_path = backup_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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
        raise GateError("invalid_backup_id")
    backup_root = project_root.joinpath(*BACKUP_DIR_PARTS, backup_id).resolve(strict=False)
    allowed_root = project_root.joinpath(*BACKUP_DIR_PARTS).resolve(strict=False)
    if allowed_root not in [backup_root, *backup_root.parents]:
        raise GateError("backup_outside_allowed_root")
    manifest_path = backup_root / "manifest.json"
    if not manifest_path.is_file():
        raise GateError("backup_manifest_missing")
    manifest = _read_json(manifest_path)
    if manifest.get("version") != SQX144_MT5_INSTRUMENT_PARITY_VERSION:
        raise GateError("backup_manifest_version_mismatch")
    if manifest.get("backupId") != backup_id:
        raise GateError("backup_manifest_id_mismatch")
    for item in manifest.get("files", []):
        backup_file = backup_root / str(item.get("name") or "")
        if not backup_file.is_file() or _sha256_file(backup_file) != item.get("sha256"):
            raise GateError("backup_hash_mismatch", details={"file": item.get("name")})
    return backup_root, manifest


def apply_payload(
    project_root: str | Path,
    *,
    xml_path: str | Path | None = None,
    db_path: str | Path | None = None,
    target_instrument: str | None = None,
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
        raise GateError("backup_id_required")
    _load_backup_manifest(root, backup_id)
    plan = build_plan(root, xml_path=xml_path, db_path=db_path, target_instrument=target_instrument, backup_id=backup_id)
    expected_approval = plan["approvalTemplate"]
    if approval != expected_approval:
        payload.update({
            "status": "apply_blocked_bad_approval",
            "blockers": ["exact_approval_phrase_required"],
            "expectedApproval": expected_approval,
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
    resolved_db = Path(db_path or str(config.get("sqx_data_db") or ""))
    conn = _connect_write(resolved_db)
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            f"UPDATE INSTRUMENTS SET {assignments} WHERE INSTRUMENT = ? AND BROKER_ID = ?",
            (*values, plan["targetInstrument"], (plan.get("invariants") or {}).get("brokerId")),
        )
        changed_rows = int(conn.execute("SELECT changes()").fetchone()[0])
        if changed_rows != 1:
            raise GateError("apply_update_count_mismatch", details={"changes": changed_rows})
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
    })
    return payload


def verify_payload(
    project_root: str | Path,
    *,
    xml_path: str | Path | None = None,
    db_path: str | Path | None = None,
    target_instrument: str | None = None,
) -> dict[str, Any]:
    plan = build_plan(project_root, xml_path=xml_path, db_path=db_path, target_instrument=target_instrument)
    root = _project_root(project_root)
    config = _load_config(root)
    resolved_db = Path(db_path or str(config.get("sqx_data_db") or ""))
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
    target_db = Path(db_path or str(config.get("sqx_data_db") or ""))
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
            raise GateError("unexpected_backup_file", details={"file": name})
        shutil.copy2(source, dest)
        if _sha256_file(dest) != item.get("sha256"):
            raise GateError("rollback_hash_mismatch", details={"file": name})
        restored.append(name)
    payload.update({
        "ok": True,
        "status": "rollback_restored_known_phase_backup",
        "backupId": backup_id,
        "restoredFiles": restored,
        "tableCounts": _table_counts_for_db(target_db),
    })
    return payload


def _handle_gate_error(action: str, project_root: str | Path, error: GateError) -> dict[str, Any]:
    try:
        host_profile = str(_load_config(_project_root(project_root)).get("sqx_host_profile") or "")
    except Exception:
        host_profile = ""
    payload = _base_payload(action, host_profile)
    payload.update({
        "ok": False,
        "status": "blocked",
        "error": error.code,
        "details": error.details,
        "blockers": [error.code],
    })
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SQX144 MT5 InstrumentInfo metadata parity gate")
    parser.add_argument("action", choices=("status", "audit", "plan", "backup", "apply", "verify", "rollback"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--xml-path", default=None)
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--target-instrument", default=None)
    parser.add_argument("--backup-id", default=None)
    parser.add_argument("--approval", default=None)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.action == "status":
            payload = status_payload(args.project_root, xml_path=args.xml_path, db_path=args.db_path, target_instrument=args.target_instrument)
        elif args.action == "audit":
            payload = audit_payload(args.project_root, xml_path=args.xml_path, db_path=args.db_path, target_instrument=args.target_instrument)
        elif args.action == "plan":
            payload = build_plan(args.project_root, xml_path=args.xml_path, db_path=args.db_path, target_instrument=args.target_instrument, backup_id=args.backup_id)
        elif args.action == "backup":
            payload = backup_payload(args.project_root, db_path=args.db_path)
        elif args.action == "apply":
            payload = apply_payload(
                args.project_root,
                xml_path=args.xml_path,
                db_path=args.db_path,
                target_instrument=args.target_instrument,
                backup_id=args.backup_id,
                approval=args.approval,
                apply=args.apply,
            )
        elif args.action == "verify":
            payload = verify_payload(args.project_root, xml_path=args.xml_path, db_path=args.db_path, target_instrument=args.target_instrument)
        else:
            if not args.backup_id:
                raise GateError("backup_id_required")
            payload = rollback_payload(args.project_root, backup_id=args.backup_id, db_path=args.db_path)
    except GateError as exc:
        payload = _handle_gate_error(args.action, args.project_root, exc)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
