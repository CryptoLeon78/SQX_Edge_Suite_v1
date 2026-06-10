from __future__ import annotations

import argparse
import hashlib
import json
import math
import sqlite3
from pathlib import Path
from typing import Any
from urllib.parse import quote

from . import sqx144_mt5_auto2_datamanager as auto2
from . import sqx144_mt5_bridge as bridge


SQX144_MT5_AUTO3_VERSION = "sqx144-mt5-auto3-broker-catalog-resolver-v1"
SQX144_MT5_AUTO3_PHASE = "SQX144-MT5-AUTO3"
SQX144_MT5_AUTO3_STATUS = "opened_broker_catalog_resolver_readonly_design_no_import_no_apply_no_projects_no_databanks_no_tasks"
READ_MODE = "sqlite_uri_mode_ro_query_only"
DEFAULT_BROKER = "darwinex"
DEFAULT_SPREAD_POLICY = bridge.DEFAULT_SPREAD_POLICY
DECISIONS = (
    "ready_existing",
    "metadata_diff_only",
    "instrument_missing",
    "history_missing",
    "broker_missing",
    "ambiguous_collision",
)
ALLOWED_ACTIONS = (
    "status",
    "catalog-audit",
    "bridge-validate",
    "resolve-plan",
    "import-plan",
    "approval-template",
)
PUBLIC_FLAGS: dict[str, bool] = {
    "readOnlyCatalogResolver": True,
    "importAllowed": False,
    "applyAllowed": False,
    "importExecutionAllowed": False,
    "directDbHistoryInsertAllowed": False,
    "writesSqxHost": False,
    "writesDataDb": False,
    "writesUserProjects": False,
    "mutatesDatabanks": False,
    "runsSqxTasks": False,
    "launchesMt5": False,
    "runsMt5Ea": False,
    "placesOrders": False,
    "usesMigrationTool": False,
    "doesNotApplyToSqx": True,
    "doesNotApplyInstrumentConfig": True,
}
IMPORT_GATE_APPROVAL_SUFFIX = "no_projects_no_databanks_no_tasks"
PREFERRED_NATIVE_IMPORT_ENDPOINT = "dataSourceMt5Api/importData"
FALLBACK_IMPORT_ROUTE = "bridge_csv_file_mass_import"


class Auto3Error(RuntimeError):
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


def _broker_config_dir(project_root: Path) -> Path:
    return _tool_root(project_root) / "config" / "mt5_broker_catalog"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_config(project_root: Path) -> dict[str, Any]:
    path = _config_path(project_root)
    if not path.is_file():
        raise Auto3Error("sqx_edge_config_missing")
    return _read_json(path)


def _sqlite_ro_uri(db_path: Path) -> str:
    return f"file:{quote(db_path.resolve(strict=False).as_posix(), safe=':/')}?mode=ro"


def _connect_readonly(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    if not path.is_file():
        raise Auto3Error("sqx_data_db_missing")
    conn = sqlite3.connect(_sqlite_ro_uri(path), uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn


def _base_payload(action: str) -> dict[str, Any]:
    payload = {
        "ok": False,
        "version": SQX144_MT5_AUTO3_VERSION,
        "phase": SQX144_MT5_AUTO3_PHASE,
        "statusMarker": SQX144_MT5_AUTO3_STATUS,
        "action": action,
        "host": "sqx144_full",
        "hostProfile": "sqx144_full",
        "readMode": READ_MODE,
        "privacy": {
            "localPathsReturned": False,
            "accountReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
            "sqlReturned": False,
            "rawXmlReturned": False,
        },
    }
    payload.update(PUBLIC_FLAGS)
    return payload


def _public_profile(profile: dict[str, Any]) -> dict[str, Any]:
    broker = profile.get("sqxBroker") if isinstance(profile.get("sqxBroker"), dict) else {}
    mapping = profile.get("symbolMapping") if isinstance(profile.get("symbolMapping"), dict) else {}
    routes = profile.get("importRoutes") if isinstance(profile.get("importRoutes"), dict) else {}
    guards = profile.get("guards") if isinstance(profile.get("guards"), dict) else {}
    return {
        "brokerKey": profile.get("brokerKey"),
        "status": profile.get("status"),
        "spreadPolicy": profile.get("spreadPolicy") or DEFAULT_SPREAD_POLICY,
        "expectedBrokerId": broker.get("expectedBrokerId"),
        "expectedSourceId": broker.get("expectedSourceId"),
        "postfix": broker.get("postfix"),
        "requiresDiscovery": bool(guards.get("requiresDiscovery")),
        "mt5SymbolTemplatePresent": bool(mapping.get("mt5SymbolTemplate")),
        "sqxInstrumentTemplatePresent": bool(mapping.get("sqxInstrumentTemplate")),
        "preferredImportRoute": routes.get("preferred"),
        "preferredNativeEndpoint": routes.get("preferredNativeEndpoint"),
        "fallbackImportRoute": routes.get("fallback"),
        "directDbHistoryInsertAllowed": bool(routes.get("directDbHistoryInsertAllowed")),
    }


def load_broker_profiles(project_root: str | Path) -> dict[str, dict[str, Any]]:
    root = _project_root(project_root)
    config_dir = _broker_config_dir(root)
    if not config_dir.is_dir():
        raise Auto3Error("broker_catalog_config_missing")
    profiles: dict[str, dict[str, Any]] = {}
    for path in sorted(config_dir.glob("*.json")):
        payload = _read_json(path)
        if payload.get("version") != SQX144_MT5_AUTO3_VERSION:
            raise Auto3Error("broker_catalog_version_mismatch", details={"fileName": path.name})
        broker_key = str(payload.get("brokerKey") or path.stem).lower()
        profiles[broker_key] = payload
    if not profiles:
        raise Auto3Error("broker_catalog_empty")
    return profiles


def _load_profile(project_root: Path, broker_key: str) -> dict[str, Any]:
    profiles = load_broker_profiles(project_root)
    key = str(broker_key or DEFAULT_BROKER).lower()
    if key not in profiles:
        raise Auto3Error("broker_profile_unknown", details={"broker": broker_key})
    return profiles[key]


def _template(template: Any, *, asset: str) -> str | None:
    if not template:
        return None
    return str(template).replace("{asset}", asset)


def resolve_symbol(profile: dict[str, Any], symbol: str, aliases: dict[str, Any] | None = None) -> dict[str, Any]:
    raw = str(symbol or "").strip()
    if not raw:
        raise Auto3Error("symbol_required")
    value = "".join(raw.split())
    if not value:
        raise Auto3Error("symbol_required")
    base = value.split("_", 1)[0] if "_" in value else value
    asset = base.upper()
    alias_target = ""
    for key, candidate in (aliases or {}).items():
        if str(key).upper() == asset:
            alias_target = str(candidate or "").strip()
            if alias_target:
                asset = alias_target.split("_", 1)[0].upper()
            break
    mapping = profile.get("symbolMapping") if isinstance(profile.get("symbolMapping"), dict) else {}
    broker = profile.get("sqxBroker") if isinstance(profile.get("sqxBroker"), dict) else {}
    mt5_symbol = _template(mapping.get("mt5SymbolTemplate"), asset=asset)
    target_instrument = _template(mapping.get("sqxInstrumentTemplate"), asset=asset)
    data_symbol = _template(mapping.get("sqxDataSymbolTemplate"), asset=asset)
    postfix = broker.get("postfix")
    if postfix and not target_instrument:
        target_instrument = f"{asset}{postfix}"
    if postfix and not data_symbol:
        data_symbol = f"{asset}{postfix}"
    return {
        "inputSymbol": raw,
        "asset": asset,
        "aliasUsed": bool(alias_target),
        "aliasTarget": alias_target or None,
        "brokerKey": profile.get("brokerKey"),
        "mt5BridgeSymbol": mt5_symbol,
        "targetInstrument": target_instrument,
        "dataSymbol": data_symbol,
        "postfix": postfix,
    }


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    try:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    except Exception:
        return set()
    return {str(row["name"]) for row in rows}


def _select_table(conn: sqlite3.Connection, table: str, wanted: tuple[str, ...]) -> list[dict[str, Any]]:
    columns = _table_columns(conn, table)
    if not columns:
        return []
    selected = [column for column in wanted if column in columns]
    if not selected:
        return []
    quoted = ", ".join(f'"{column}"' for column in selected)
    try:
        rows = conn.execute(f"SELECT {quoted} FROM {table}").fetchall()
    except Exception:
        return []
    return [dict(row) for row in rows]


def _table_count(conn: sqlite3.Connection, table: str) -> int | None:
    try:
        return int(conn.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"])
    except Exception:
        return None


def _quick_check(conn: sqlite3.Connection) -> str | None:
    try:
        return str(conn.execute("PRAGMA quick_check").fetchone()[0])
    except Exception:
        return None


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except Exception:
        return None


def _safe_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except Exception:
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _same_value(old_value: Any, new_value: Any) -> bool:
    parsed = _safe_float(new_value)
    if parsed is not None:
        old = _safe_float(old_value)
        return old is not None and math.isclose(old, parsed, rel_tol=0.0, abs_tol=1e-6)
    return str(old_value or "") == str(new_value or "")


def _broker_matches(rows: list[dict[str, Any]], profile: dict[str, Any]) -> list[dict[str, Any]]:
    broker = profile.get("sqxBroker") if isinstance(profile.get("sqxBroker"), dict) else {}
    expected_id = broker.get("expectedBrokerId")
    matchers = {str(item).lower() for item in broker.get("nameMatchers") or [] if str(item).strip()}
    postfix = str(broker.get("postfix") or "").lower()
    matches: list[dict[str, Any]] = []
    for row in rows:
        row_id = row.get("ID")
        row_name = str(row.get("NAME") or row.get("DESC") or "").lower()
        row_desc = str(row.get("DESC") or "").lower()
        row_postfix = str(row.get("POSTFIX") or "").lower()
        if expected_id is not None and str(row_id) == str(expected_id):
            matches.append(row)
            continue
        if postfix and row_postfix == postfix:
            matches.append(row)
            continue
        if matchers and any(matcher in row_name or matcher in row_desc for matcher in matchers):
            matches.append(row)
    return matches


def _instrument_matches(rows: list[dict[str, Any]], target: str | None, expected_broker_id: Any) -> list[dict[str, Any]]:
    if not target:
        return []
    matches = [row for row in rows if str(row.get("INSTRUMENT") or "").lower() == target.lower()]
    if expected_broker_id is None:
        return matches
    return [row for row in matches if str(row.get("BROKER_ID")) == str(expected_broker_id)]


def _data_matches(rows: list[dict[str, Any]], data_symbol: str | None, target: str | None, expected_broker_id: Any, expected_source_id: Any) -> list[dict[str, Any]]:
    if not data_symbol and not target:
        return []
    matched: list[dict[str, Any]] = []
    for row in rows:
        symbol = str(row.get("SYMBOL") or "")
        instrument = str(row.get("INSTRUMENT") or "")
        if data_symbol and symbol.lower() == data_symbol.lower() or target and instrument.lower() == target.lower():
            if expected_broker_id is not None and str(row.get("BROKER_ID")) != str(expected_broker_id):
                continue
            if expected_source_id is not None and str(row.get("SOURCE")) != str(expected_source_id):
                continue
            matched.append(row)
    return matched


def _collision_status(
    instrument_rows: list[dict[str, Any]],
    data_rows: list[dict[str, Any]],
    target: str | None,
    data_symbol: str | None,
) -> tuple[bool, list[str]]:
    collisions: list[str] = []
    if target:
        exact_instruments = [str(row.get("INSTRUMENT") or "") for row in instrument_rows if str(row.get("INSTRUMENT") or "").lower() == target.lower()]
        if len({value for value in exact_instruments}) > 1 or len(exact_instruments) > 1:
            collisions.append("duplicate_case_insensitive_instrument")
    if data_symbol:
        seen_keys: set[tuple[str, str, str, str]] = set()
        for row in data_rows:
            symbol = str(row.get("SYMBOL") or "")
            if symbol.lower() != data_symbol.lower():
                continue
            key = (
                symbol.lower(),
                str(row.get("TIMEFRAME") or ""),
                str(row.get("SOURCE") or ""),
                str(row.get("BROKER_ID") or ""),
            )
            if key in seen_keys:
                collisions.append("duplicate_data_symbol_timeframe_source")
            seen_keys.add(key)
    return bool(collisions), sorted(set(collisions))


def _sanitize_broker_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in rows[:12]:
        result.append({
            "id": row.get("ID"),
            "name": row.get("NAME"),
            "postfix": row.get("POSTFIX"),
        })
    return result


def _sanitize_instrument_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in rows[:24]:
        result.append({
            "instrument": row.get("INSTRUMENT"),
            "brokerId": row.get("BROKER_ID"),
            "defaultSpread": row.get("DEFAULTSPREAD"),
            "pointValue": row.get("POINTVALUE"),
            "tickSize": row.get("TICKSIZE"),
            "tickStep": row.get("TICKSTEP"),
        })
    return result


def _sanitize_data_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in rows[:48]:
        result.append({
            "symbol": row.get("SYMBOL"),
            "instrument": row.get("INSTRUMENT"),
            "timeframe": row.get("TIMEFRAME"),
            "source": row.get("SOURCE"),
            "brokerId": row.get("BROKER_ID"),
            "rows": row.get("ROWS"),
            "dateFrom": row.get("DATEFROM"),
            "dateTo": row.get("DATETO"),
        })
    return result


def _metadata_diff_from_bridge(instrument_row: dict[str, Any] | None, proposed: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if not instrument_row:
        return {}
    mapping = {
        "DEFAULTSPREAD": "DEFAULTSPREAD",
        "POINTVALUE": "POINTVALUE",
        "TICKSIZE": "TICKSIZE",
        "TICKSTEP": "TICKSTEP",
    }
    diff: dict[str, dict[str, Any]] = {}
    for proposed_key, column in mapping.items():
        if proposed_key not in proposed:
            continue
        new_value = proposed.get(proposed_key)
        old_value = instrument_row.get(column)
        if not _same_value(old_value, new_value):
            diff[column] = {"old": old_value, "new": new_value}
    return diff


def _deterministic_plan_id(kind: str, seed: dict[str, Any]) -> str:
    raw = json.dumps(seed, sort_keys=True, ensure_ascii=True, default=str).encode("utf-8")
    return f"auto3_{kind}_{hashlib.sha256(raw).hexdigest()[:16]}"


def _catalog_snapshot(project_root: Path, broker_key: str, symbol: str | None, db_path: str | Path | None = None) -> dict[str, Any]:
    config = _load_config(project_root)
    host_profile = str(config.get("sqx_host_profile") or "")
    if host_profile != "sqx144_full":
        raise Auto3Error("host_profile_not_sqx144_full", details={"host": host_profile})
    profile = _load_profile(project_root, broker_key)
    profile_public = _public_profile(profile)
    broker = profile.get("sqxBroker") if isinstance(profile.get("sqxBroker"), dict) else {}
    expected_broker_id = broker.get("expectedBrokerId")
    expected_source_id = broker.get("expectedSourceId")
    aliases = config.get("asset_aliases") if isinstance(config.get("asset_aliases"), dict) else {}
    resolved = resolve_symbol(profile, symbol, aliases=aliases) if symbol else None
    resolved_db = Path(db_path or str(config.get("sqx_data_db") or ""))
    conn = _connect_readonly(resolved_db)
    try:
        broker_rows = _select_table(conn, "BROKER", ("ID", "NAME", "POSTFIX", "DESC"))
        instrument_rows_all = _select_table(
            conn,
            "INSTRUMENTS",
            ("INSTRUMENT", "BROKER_ID", "DEFAULTSPREAD", "POINTVALUE", "TICKSIZE", "TICKSTEP", "DEFAULTSLIPPAGE", "ORDERSIZEMULTIPLIER", "ORDERSIZESTEP"),
        )
        data_rows_all = _select_table(
            conn,
            "DATA",
            ("SYMBOL", "INSTRUMENT", "TIMEFRAME", "SOURCE", "BROKER_ID", "ROWS", "DATEFROM", "DATETO", "USYMBOL"),
        )
        broker_matches = _broker_matches(broker_rows, profile)
        target = resolved.get("targetInstrument") if resolved else None
        data_symbol = resolved.get("dataSymbol") if resolved else None
        instrument_matches = _instrument_matches(instrument_rows_all, target, expected_broker_id)
        data_matches = _data_matches(data_rows_all, data_symbol, target, expected_broker_id, expected_source_id)
        collision, collision_reasons = _collision_status(instrument_rows_all, data_rows_all, target, data_symbol)
        rows_positive = [row for row in data_matches if (_safe_int(row.get("ROWS")) or 0) > 0]
        if not broker_matches:
            decision = "broker_missing"
        elif collision:
            decision = "ambiguous_collision"
        elif resolved and not target:
            decision = "broker_missing"
        elif resolved and not instrument_matches:
            decision = "instrument_missing"
        elif resolved and not rows_positive:
            decision = "history_missing"
        else:
            decision = "ready_existing"
        return {
            "profile": profile,
            "profilePublic": profile_public,
            "symbolResolution": resolved,
            "decision": decision,
            "tableCounts": {
                "BROKER": _table_count(conn, "BROKER"),
                "INSTRUMENTS": _table_count(conn, "INSTRUMENTS"),
                "DATA": _table_count(conn, "DATA"),
            },
            "quickCheck": _quick_check(conn),
            "brokerRows": broker_rows,
            "brokerMatches": broker_matches,
            "instrumentRowsAll": instrument_rows_all,
            "instrumentMatches": instrument_matches,
            "dataRowsAll": data_rows_all,
            "dataMatches": data_matches,
            "historyRowsPositive": rows_positive,
            "collision": collision,
            "collisionReasons": collision_reasons,
            "readMode": READ_MODE,
        }
    finally:
        conn.close()


def status_payload(project_root: str | Path, *, db_path: str | Path | None = None) -> dict[str, Any]:
    root = _project_root(project_root)
    payload = _base_payload("status")
    config = _load_config(root)
    profiles = load_broker_profiles(root)
    db = Path(db_path or str(config.get("sqx_data_db") or ""))
    table_counts: dict[str, int | None] = {}
    quick_check: str | None = None
    if db.is_file():
        conn = _connect_readonly(db)
        try:
            table_counts = {
                "BROKER": _table_count(conn, "BROKER"),
                "INSTRUMENTS": _table_count(conn, "INSTRUMENTS"),
                "DATA": _table_count(conn, "DATA"),
            }
            quick_check = _quick_check(conn)
        finally:
            conn.close()
    auto2_status = auto2.status_payload(root)
    payload.update({
        "ok": str(config.get("sqx_host_profile") or "") == "sqx144_full",
        "status": SQX144_MT5_AUTO3_STATUS,
        "hostProfile": str(config.get("sqx_host_profile") or ""),
        "actions": list(ALLOWED_ACTIONS),
        "decisions": list(DECISIONS),
        "endpoints": [
            "/api/sqx144/mt5-auto3/status",
            "/api/sqx144/mt5-auto3/catalog-audit",
            "/api/sqx144/mt5-auto3/bridge-validate",
            "/api/sqx144/mt5-auto3/resolve-plan",
            "/api/sqx144/mt5-auto3/import-plan",
        ],
        "brokerProfiles": [_public_profile(item) for item in profiles.values()],
        "sqxCatalog": {
            "dataDbPresent": db.is_file(),
            "tableCounts": table_counts,
            "quickCheck": quick_check,
        },
        "auto2": {
            "version": auto2_status.get("version"),
            "status": auto2_status.get("status"),
            "ok": auto2_status.get("ok"),
            "dataManagerButtonPlanned": auto2_status.get("dataManagerButtonPlanned"),
            "dataManagerButtonInstalled": auto2_status.get("dataManagerButtonInstalled"),
            "doesNotApplyToSqx": auto2_status.get("doesNotApplyToSqx"),
        },
        "importGate": {
            "preferredRoute": "native_datamanager_mt5_import",
            "preferredNativeEndpoint": PREFERRED_NATIVE_IMPORT_ENDPOINT,
            "fallbackRoute": FALLBACK_IMPORT_ROUTE,
            "directDbHistoryInsertAllowed": False,
            "executionAllowedInAuto3": False,
        },
    })
    if not payload["ok"]:
        payload["blockers"] = ["host_profile_not_sqx144_full"]
    else:
        payload["blockers"] = []
    return payload


def catalog_audit_payload(
    project_root: str | Path,
    *,
    broker_key: str = DEFAULT_BROKER,
    symbol: str | None = None,
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    snapshot = _catalog_snapshot(root, broker_key, symbol, db_path=db_path)
    payload = _base_payload("catalog-audit")
    payload.update({
        "ok": True,
        "status": "catalog_audit_ready",
        "brokerKey": str(broker_key or DEFAULT_BROKER).lower(),
        "brokerProfile": snapshot["profilePublic"],
        "symbolResolution": snapshot["symbolResolution"],
        "decision": snapshot["decision"],
        "tableCounts": snapshot["tableCounts"],
        "quickCheck": snapshot["quickCheck"],
        "brokerFound": bool(snapshot["brokerMatches"]),
        "instrumentFound": bool(snapshot["instrumentMatches"]),
        "historyFound": bool(snapshot["historyRowsPositive"]),
        "ambiguousCollision": bool(snapshot["collision"]),
        "collisionReasons": snapshot["collisionReasons"],
        "brokerMatches": _sanitize_broker_rows(snapshot["brokerMatches"]),
        "instrumentRows": _sanitize_instrument_rows(snapshot["instrumentMatches"]),
        "dataRows": _sanitize_data_rows(snapshot["dataMatches"]),
        "historyRowsPositive": len(snapshot["historyRowsPositive"]),
    })
    return payload


def bridge_validate_payload(
    project_root: str | Path,
    *,
    broker_key: str = DEFAULT_BROKER,
    symbol: str,
    spread_policy: str = DEFAULT_SPREAD_POLICY,
    expected_request_id: str | None = None,
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    profile = _load_profile(root, broker_key)
    config = _load_config(root)
    aliases = config.get("asset_aliases") if isinstance(config.get("asset_aliases"), dict) else {}
    resolved = resolve_symbol(profile, symbol, aliases=aliases)
    expected_symbol = resolved.get("mt5BridgeSymbol") or symbol
    payload = _base_payload("bridge-validate")
    validation = auto2.validate_payload(
        project_root=root,
        spread_policy=spread_policy or DEFAULT_SPREAD_POLICY,
        expected_request_id=expected_request_id or None,
        expected_symbol=expected_symbol,
    )
    snapshot = _catalog_snapshot(root, broker_key, symbol, db_path=db_path)
    metadata_diff = _metadata_diff_from_bridge(
        snapshot["instrumentMatches"][0] if snapshot["instrumentMatches"] else None,
        validation.get("proposedSqxFields") if isinstance(validation.get("proposedSqxFields"), dict) else {},
    )
    decision = snapshot["decision"]
    if validation.get("ok") and decision == "ready_existing" and metadata_diff:
        decision = "metadata_diff_only"
    payload.update(validation)
    payload.update(PUBLIC_FLAGS)
    payload.update({
        "ok": bool(validation.get("ok")) and snapshot["decision"] not in {"broker_missing", "ambiguous_collision"},
        "version": SQX144_MT5_AUTO3_VERSION,
        "phase": SQX144_MT5_AUTO3_PHASE,
        "action": "bridge-validate",
        "status": "bridge_validate_ready" if validation.get("ok") else validation.get("status", "bridge_validate_blocked"),
        "brokerKey": str(broker_key or DEFAULT_BROKER).lower(),
        "brokerProfile": snapshot["profilePublic"],
        "symbolResolution": resolved,
        "catalogDecision": snapshot["decision"],
        "decision": decision,
        "metadataDiff": metadata_diff,
        "spreadPolicy": str(spread_policy or DEFAULT_SPREAD_POLICY).lower(),
    })
    return payload


def resolve_plan_payload(
    project_root: str | Path,
    *,
    broker_key: str = DEFAULT_BROKER,
    symbol: str,
    spread_policy: str = DEFAULT_SPREAD_POLICY,
    with_bridge: bool = False,
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    snapshot = _catalog_snapshot(root, broker_key, symbol, db_path=db_path)
    resolved = snapshot["symbolResolution"]
    decision = snapshot["decision"]
    bridge_report: dict[str, Any] | None = None
    metadata_diff: dict[str, dict[str, Any]] = {}
    if with_bridge and decision == "ready_existing":
        bridge_report = bridge_validate_payload(root, broker_key=broker_key, symbol=symbol, spread_policy=spread_policy, db_path=db_path)
        metadata_diff = bridge_report.get("metadataDiff") if isinstance(bridge_report.get("metadataDiff"), dict) else {}
        if metadata_diff:
            decision = "metadata_diff_only"
    plan_seed = {
        "version": SQX144_MT5_AUTO3_VERSION,
        "brokerKey": broker_key,
        "symbolResolution": resolved,
        "decision": decision,
        "tableCounts": snapshot["tableCounts"],
        "metadataDiff": metadata_diff,
    }
    plan_id = _deterministic_plan_id("resolve", plan_seed)
    payload = _base_payload("resolve-plan")
    payload.update({
        "ok": True,
        "status": "resolve_plan_ready",
        "brokerKey": str(broker_key or DEFAULT_BROKER).lower(),
        "brokerProfile": snapshot["profilePublic"],
        "symbolResolution": resolved,
        "decision": decision,
        "planId": plan_id,
        "catalogDecision": snapshot["decision"],
        "metadataDiff": metadata_diff,
        "bridge": bridge_report,
        "nextAction": _next_action_for_decision(decision),
        "requiresFutureExactApproval": decision in {"metadata_diff_only", "instrument_missing", "history_missing", "broker_missing"},
        "approvalTemplates": _approval_templates(str(broker_key or DEFAULT_BROKER).lower(), resolved, plan_id),
        "tableCounts": snapshot["tableCounts"],
        "warnings": _warnings_for_decision(decision, snapshot),
        "blockers": _blockers_for_decision(decision),
    })
    return payload


def import_plan_payload(
    project_root: str | Path,
    *,
    broker_key: str = DEFAULT_BROKER,
    symbol: str,
    timeframe: str = "M1",
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    resolve = resolve_plan_payload(root, broker_key=broker_key, symbol=symbol, db_path=db_path)
    resolved = resolve.get("symbolResolution") if isinstance(resolve.get("symbolResolution"), dict) else {}
    decision = str(resolve.get("decision") or "")
    plan_seed = {
        "version": SQX144_MT5_AUTO3_VERSION,
        "brokerKey": broker_key,
        "symbolResolution": resolved,
        "decision": decision,
        "timeframe": timeframe,
        "route": "native_datamanager_mt5_import",
    }
    plan_id = _deterministic_plan_id("import", plan_seed)
    blocked = decision in {"broker_missing", "ambiguous_collision"} or bool(_load_profile(root, broker_key).get("guards", {}).get("requiresDiscovery"))
    payload = _base_payload("import-plan")
    payload.update({
        "ok": True,
        "status": "import_plan_ready_blocked_until_exact_approval",
        "brokerKey": str(broker_key or DEFAULT_BROKER).lower(),
        "symbolResolution": resolved,
        "decision": decision,
        "planId": plan_id,
        "timeframe": str(timeframe or "M1").upper(),
        "importNeeded": decision in {"instrument_missing", "history_missing"},
        "importBlocked": True,
        "preferredRoute": "native_datamanager_mt5_import",
        "preferredNativeEndpoint": PREFERRED_NATIVE_IMPORT_ENDPOINT,
        "fallbackRoute": FALLBACK_IMPORT_ROUTE,
        "fallbackMode": "bridge_exports_csv_then_data_manager_file_or_mass_import",
        "directDbHistoryInsertAllowed": False,
        "importExecutionAllowed": False,
        "routeContracts": {
            "native": "SQX Data Manager writes its own history format through DataSourceMt5Api/importData in a future approved gate.",
            "fallback": "Bridge CSV plus Data Manager File/Mass import only if native import is not observable or controllable.",
            "forbidden": "direct DB history inserts remain prohibited in AUTO3",
        },
        "futureGateRequired": True,
        "approvalTemplate": _approval_templates(str(broker_key or DEFAULT_BROKER).lower(), resolved, plan_id)["importHistory"],
        "blockers": _blockers_for_decision(decision) + (["future_exact_import_gate_required"] if not blocked else ["broker_discovery_or_collision_blocks_import_plan"]),
    })
    return payload


def approval_template_payload(
    project_root: str | Path,
    *,
    broker_key: str = DEFAULT_BROKER,
    symbol: str | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    profile = _load_profile(root, broker_key)
    config = _load_config(root)
    aliases = config.get("asset_aliases") if isinstance(config.get("asset_aliases"), dict) else {}
    resolved = resolve_symbol(profile, symbol or "AUDCAD", aliases=aliases) if symbol else {
        "asset": "<asset>",
        "targetInstrument": "<instrument>",
        "dataSymbol": "<dataSymbol>",
        "mt5BridgeSymbol": "<mt5Symbol>",
    }
    plan_id = "auto3_<planId>"
    payload = _base_payload("approval-template")
    payload.update({
        "ok": True,
        "status": "approval_templates_ready_for_future_gates",
        "brokerKey": str(broker_key or DEFAULT_BROKER).lower(),
        "symbolResolution": resolved,
        "approvalTemplates": _approval_templates(str(broker_key or DEFAULT_BROKER).lower(), resolved, plan_id),
        "requiredSuffix": IMPORT_GATE_APPROVAL_SUFFIX,
        "futureGateRequired": True,
    })
    return payload


def _next_action_for_decision(decision: str) -> str:
    return {
        "ready_existing": "no_catalog_mutation_needed",
        "metadata_diff_only": "future_metadata_apply_gate_after_backup_and_exact_approval",
        "instrument_missing": "future_create_instrument_gate_then_history_import_gate",
        "history_missing": "future_history_import_gate",
        "broker_missing": "read_only_broker_discovery_required",
        "ambiguous_collision": "manual_catalog_review_required",
    }.get(decision, "manual_review_required")


def _warnings_for_decision(decision: str, snapshot: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    profile_public = snapshot.get("profilePublic") if isinstance(snapshot.get("profilePublic"), dict) else {}
    if profile_public.get("requiresDiscovery"):
        warnings.append("broker_discovery_required_before_axi_create_or_import")
    if decision == "history_missing":
        warnings.append("mt5_metadata_does_not_prove_sqx_history_coverage")
    if decision == "metadata_diff_only":
        warnings.append("instrument_metadata_diff_requires_separate_offline_apply_gate")
    return warnings


def _blockers_for_decision(decision: str) -> list[str]:
    if decision == "ready_existing":
        return []
    return {
        "metadata_diff_only": ["metadata_apply_not_allowed_in_auto3"],
        "instrument_missing": ["instrument_create_not_allowed_in_auto3"],
        "history_missing": ["history_import_not_allowed_in_auto3"],
        "broker_missing": ["broker_missing_discovery_required"],
        "ambiguous_collision": ["ambiguous_collision_manual_review_required"],
    }.get(decision, ["manual_review_required"])


def _approval_templates(broker_key: str, resolved: dict[str, Any] | None, plan_id: str) -> dict[str, str]:
    instrument = str((resolved or {}).get("targetInstrument") or "<instrument>")
    return {
        "metadataApply": (
            "APRUEBO SQX144 MT5 AUTO3 METADATA APPLY "
            f"host=sqx144_full broker={broker_key} instrument={instrument} plan={plan_id} {IMPORT_GATE_APPROVAL_SUFFIX}"
        ),
        "createInstrument": (
            "APRUEBO SQX144 MT5 AUTO3 CREATE INSTRUMENT "
            f"host=sqx144_full broker={broker_key} instrument={instrument} plan={plan_id} {IMPORT_GATE_APPROVAL_SUFFIX}"
        ),
        "importHistory": (
            "APRUEBO SQX144 MT5 AUTO3 IMPORT HISTORY "
            f"host=sqx144_full broker={broker_key} instrument={instrument} plan={plan_id} native_datamanager_only {IMPORT_GATE_APPROVAL_SUFFIX}"
        ),
    }


def error_payload(action: str, error: Auto3Error | bridge.BridgeError) -> dict[str, Any]:
    payload = _base_payload(action)
    code = getattr(error, "code", str(error))
    details = getattr(error, "details", {})
    payload.update({
        "ok": False,
        "status": "blocked",
        "error": code,
        "details": details,
        "blockers": [code],
    })
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SQX144 MT5 AUTO3 broker catalog resolver")
    parser.add_argument("action", choices=ALLOWED_ACTIONS)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--broker", default=DEFAULT_BROKER)
    parser.add_argument("--symbol", default="")
    parser.add_argument("--spread-policy", default=DEFAULT_SPREAD_POLICY)
    parser.add_argument("--expected-request-id", default=None)
    parser.add_argument("--timeframe", default="M1")
    parser.add_argument("--with-bridge", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "status":
            payload = status_payload(args.project_root, db_path=args.db_path)
        elif args.action == "catalog-audit":
            payload = catalog_audit_payload(args.project_root, broker_key=args.broker, symbol=args.symbol or None, db_path=args.db_path)
        elif args.action == "bridge-validate":
            payload = bridge_validate_payload(
                args.project_root,
                broker_key=args.broker,
                symbol=args.symbol,
                spread_policy=args.spread_policy,
                expected_request_id=args.expected_request_id,
                db_path=args.db_path,
            )
        elif args.action == "resolve-plan":
            payload = resolve_plan_payload(
                args.project_root,
                broker_key=args.broker,
                symbol=args.symbol,
                spread_policy=args.spread_policy,
                with_bridge=args.with_bridge,
                db_path=args.db_path,
            )
        elif args.action == "import-plan":
            payload = import_plan_payload(args.project_root, broker_key=args.broker, symbol=args.symbol, timeframe=args.timeframe, db_path=args.db_path)
        else:
            payload = approval_template_payload(args.project_root, broker_key=args.broker, symbol=args.symbol or None)
    except (Auto3Error, bridge.BridgeError) as exc:
        payload = error_payload(args.action, exc)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
