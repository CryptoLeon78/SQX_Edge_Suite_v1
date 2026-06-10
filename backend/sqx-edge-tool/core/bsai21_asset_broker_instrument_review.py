from __future__ import annotations

import argparse
import json
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import sqx144_mt5_auto3_broker_catalog as auto3
from .bsai17_controlled_import_start_gate import DEFAULT_EXPERIMENT_ID
from .bsai_first_start_gate import _privacy_guard


BS_AI21_ASSET_REVIEW_VERSION = "bs-ai21-asset-broker-instrument-review-v1"
BS_AI21_STATUS_OK = "asset_broker_instrument_review_completed_new_capa1_allowed_with_controls_no_apply"
BS_AI21_STATUS_REQUIRES_WAIVER = "asset_broker_instrument_review_completed_requires_fix_or_explicit_waiver_no_apply"
BS_AI21_STATUS_BLOCKED = "asset_broker_instrument_review_blocked_no_apply"
EVIDENCE_DIR_PARTS = (".local", "blocksettings_ai", "asset_broker_instrument_review")
PRIMARY_BROKER_KEY = "darwinex"
REFERENCE_BROKER_KEY = "dukascopy"
READ_MODE = auto3.READ_MODE
NUMERIC_TOLERANCE = 1e-6
CONTRACT_FIELDS = (
    "DEFAULTSPREAD",
    "POINTVALUE",
    "TICKSIZE",
    "TICKSTEP",
    "ORDERSIZEMULTIPLIER",
    "ORDERSIZESTEP",
)
INSTRUMENT_FIELDS = (
    "INSTRUMENT",
    "BROKER_ID",
    "DEFAULTSPREAD",
    "POINTVALUE",
    "TICKSIZE",
    "TICKSTEP",
    "DEFAULTSLIPPAGE",
    "ORDERSIZEMULTIPLIER",
    "ORDERSIZESTEP",
    "SWAPLONG",
    "SWAPSHORT",
    "COMMISSION",
)
DATA_FIELDS = (
    "SYMBOL",
    "INSTRUMENT",
    "TIMEFRAME",
    "SOURCE",
    "BROKER_ID",
    "ROWS",
    "DATEFROM",
    "DATETO",
    "USYMBOL",
)
BROKER_FIELDS = ("ID", "NAME", "POSTFIX", "DESC")


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _safe_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except Exception:
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except Exception:
        return None


def _same_number(left: Any, right: Any) -> bool:
    parsed_left = _safe_float(left)
    parsed_right = _safe_float(right)
    if parsed_left is None or parsed_right is None:
        return str(left or "") == str(right or "")
    return math.isclose(parsed_left, parsed_right, rel_tol=0.0, abs_tol=NUMERIC_TOLERANCE)


def _relative_delta_pct(left: Any, right: Any) -> float | None:
    parsed_left = _safe_float(left)
    parsed_right = _safe_float(right)
    if parsed_left is None or parsed_right is None:
        return None
    denominator = abs(parsed_left) if abs(parsed_left) > NUMERIC_TOLERANCE else 1.0
    return abs(parsed_right - parsed_left) / denominator * 100.0


def _casefold(value: Any) -> str:
    return str(value or "").strip().lower()


def _select_rows(conn: sqlite3.Connection, table: str, wanted: tuple[str, ...]) -> list[dict[str, Any]]:
    return auto3._select_table(conn, table, wanted)


def _table_count(conn: sqlite3.Connection, table: str) -> int | None:
    return auto3._table_count(conn, table)


def _quick_check(conn: sqlite3.Connection) -> str | None:
    return auto3._quick_check(conn)


def _load_db_connection(project_root: Path, db_path: str | Path | None = None) -> tuple[sqlite3.Connection | None, dict[str, Any], list[str]]:
    blockers: list[str] = []
    try:
        config = auto3._load_config(project_root)
    except auto3.Auto3Error as exc:
        return None, {"sqxHostProfile": None}, [exc.code]

    if str(config.get("sqx_host_profile") or "") != "sqx144_full":
        blockers.append("host_profile_not_sqx144_full")

    resolved_db = Path(db_path or str(config.get("sqx_data_db") or ""))
    try:
        conn = auto3._connect_readonly(resolved_db)
    except auto3.Auto3Error as exc:
        return None, {"sqxHostProfile": str(config.get("sqx_host_profile") or "")}, blockers + [exc.code]

    return conn, {"sqxHostProfile": str(config.get("sqx_host_profile") or "")}, blockers


def _resolve_broker(project_root: Path, broker_key: str, asset: str) -> dict[str, Any]:
    try:
        profile = auto3._load_profile(project_root, broker_key)
        resolved = auto3.resolve_symbol(profile, asset, aliases={})
        broker = profile.get("sqxBroker") if isinstance(profile.get("sqxBroker"), dict) else {}
        return {
            "brokerKey": broker_key,
            "expectedBrokerId": broker.get("expectedBrokerId"),
            "expectedSourceId": broker.get("expectedSourceId"),
            "targetInstrument": resolved.get("targetInstrument"),
            "dataSymbol": resolved.get("dataSymbol"),
            "postfix": resolved.get("postfix"),
            "profileStatus": "profile_loaded",
        }
    except Exception as exc:
        if broker_key == REFERENCE_BROKER_KEY:
            return {
                "brokerKey": broker_key,
                "expectedBrokerId": 3,
                "expectedSourceId": 2,
                "targetInstrument": f"{asset.upper()}_dukascopy",
                "dataSymbol": f"{asset.upper()}_dukascopy",
                "postfix": "_dukascopy",
                "profileStatus": "profile_missing_using_host_convention",
                "errorCode": type(exc).__name__,
            }
        return {
            "brokerKey": broker_key,
            "errorCode": type(exc).__name__,
            "targetInstrument": None,
            "dataSymbol": None,
            "profileStatus": "profile_missing",
        }


def _public_instrument(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    return {
        "instrument": row.get("INSTRUMENT"),
        "brokerId": row.get("BROKER_ID"),
        "defaultSpread": row.get("DEFAULTSPREAD"),
        "pointValue": row.get("POINTVALUE"),
        "tickSize": row.get("TICKSIZE"),
        "tickStep": row.get("TICKSTEP"),
        "defaultSlippage": row.get("DEFAULTSLIPPAGE"),
        "orderSizeMultiplier": row.get("ORDERSIZEMULTIPLIER"),
        "orderSizeStep": row.get("ORDERSIZESTEP"),
        "swapLongPresent": row.get("SWAPLONG") is not None,
        "swapShortPresent": row.get("SWAPSHORT") is not None,
        "commissionPresent": row.get("COMMISSION") is not None,
    }


def _public_data_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "symbol": row.get("SYMBOL"),
        "instrument": row.get("INSTRUMENT"),
        "timeframe": row.get("TIMEFRAME"),
        "source": row.get("SOURCE"),
        "brokerId": row.get("BROKER_ID"),
        "rows": row.get("ROWS"),
        "dateFrom": row.get("DATEFROM"),
        "dateTo": row.get("DATETO"),
    }


def _public_broker_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    return {"id": row.get("ID"), "name": row.get("NAME"), "postfix": row.get("POSTFIX")}


def _match_instrument(rows: list[dict[str, Any]], target: str | None, expected_broker_id: Any) -> dict[str, Any] | None:
    if not target:
        return None
    matches = [row for row in rows if _casefold(row.get("INSTRUMENT")) == _casefold(target)]
    if expected_broker_id is not None:
        exact = [row for row in matches if str(row.get("BROKER_ID")) == str(expected_broker_id)]
        if exact:
            return exact[0]
    return matches[0] if matches else None


def _match_broker(rows: list[dict[str, Any]], expected_broker_id: Any) -> dict[str, Any] | None:
    for row in rows:
        if expected_broker_id is not None and str(row.get("ID")) == str(expected_broker_id):
            return row
    return None


def _match_data_rows(
    rows: list[dict[str, Any]],
    *,
    target: str | None,
    data_symbol: str | None,
    expected_broker_id: Any,
    expected_source_id: Any,
    timeframe: str,
    strict_broker: bool = True,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    wanted_tf = _casefold(timeframe)
    for row in rows:
        symbol = _casefold(row.get("SYMBOL"))
        instrument = _casefold(row.get("INSTRUMENT"))
        row_tf = _casefold(row.get("TIMEFRAME"))
        if wanted_tf and row_tf and row_tf != wanted_tf:
            continue
        if data_symbol and symbol != _casefold(data_symbol) and target and instrument != _casefold(target):
            continue
        if data_symbol and not target and symbol != _casefold(data_symbol):
            continue
        if target and not data_symbol and instrument != _casefold(target):
            continue
        if strict_broker and expected_broker_id is not None and str(row.get("BROKER_ID")) != str(expected_broker_id):
            continue
        if expected_source_id is not None and str(row.get("SOURCE")) != str(expected_source_id):
            continue
        result.append(row)
    return result


def _history_summary(
    rows: list[dict[str, Any]],
    *,
    requested_timeframe: str,
    effective_timeframe: str,
    direct_requested_rows: int,
    source_only_fallback: bool,
) -> dict[str, Any]:
    positive = [row for row in rows if (_safe_int(row.get("ROWS")) or 0) > 0]
    return {
        "requestedTimeframe": requested_timeframe.upper(),
        "effectiveTimeframe": effective_timeframe.upper(),
        "directRequestedRows": direct_requested_rows,
        "usesTickBackingSource": requested_timeframe.upper() != effective_timeframe.upper(),
        "sourceOnlyFallbackUsed": source_only_fallback,
        "matchingRows": len(rows),
        "positiveHistoryRows": len(positive),
        "rowsTotal": sum((_safe_int(row.get("ROWS")) or 0) for row in positive),
        "dateFromMin": min((str(row.get("DATEFROM")) for row in positive if row.get("DATEFROM") is not None), default=None),
        "dateToMax": max((str(row.get("DATETO")) for row in positive if row.get("DATETO") is not None), default=None),
        "sample": [_public_data_row(row) for row in positive[:6]],
    }


def _select_history_rows(
    rows: list[dict[str, Any]],
    *,
    target: str | None,
    data_symbol: str | None,
    expected_broker_id: Any,
    expected_source_id: Any,
    timeframe: str,
    allow_source_only_fallback: bool,
) -> tuple[list[dict[str, Any]], str, int, bool]:
    direct = _match_data_rows(
        rows,
        target=target,
        data_symbol=data_symbol,
        expected_broker_id=expected_broker_id,
        expected_source_id=expected_source_id,
        timeframe=timeframe,
    )
    if any((_safe_int(row.get("ROWS")) or 0) > 0 for row in direct):
        return direct, timeframe, len(direct), False

    tick = _match_data_rows(
        rows,
        target=target,
        data_symbol=data_symbol,
        expected_broker_id=expected_broker_id,
        expected_source_id=expected_source_id,
        timeframe="TICK",
    )
    if any((_safe_int(row.get("ROWS")) or 0) > 0 for row in tick):
        return tick, "TICK", len(direct), False

    if not allow_source_only_fallback:
        return direct or tick, timeframe if direct else "TICK", len(direct), False

    direct_source = _match_data_rows(
        rows,
        target=target,
        data_symbol=data_symbol,
        expected_broker_id=expected_broker_id,
        expected_source_id=expected_source_id,
        timeframe=timeframe,
        strict_broker=False,
    )
    if any((_safe_int(row.get("ROWS")) or 0) > 0 for row in direct_source):
        return direct_source, timeframe, len(direct), True

    tick_source = _match_data_rows(
        rows,
        target=target,
        data_symbol=data_symbol,
        expected_broker_id=expected_broker_id,
        expected_source_id=expected_source_id,
        timeframe="TICK",
        strict_broker=False,
    )
    if any((_safe_int(row.get("ROWS")) or 0) > 0 for row in tick_source):
        return tick_source, "TICK", len(direct), True

    return direct_source or tick_source or direct or tick, "TICK", len(direct), bool(direct_source or tick_source)


def _effective_instrument_from_history(
    history_rows: list[dict[str, Any]],
    instrument_rows: list[dict[str, Any]],
    fallback: dict[str, Any] | None,
) -> dict[str, Any] | None:
    for row in history_rows:
        if (_safe_int(row.get("ROWS")) or 0) <= 0:
            continue
        instrument_name = row.get("INSTRUMENT")
        match = _match_instrument(instrument_rows, str(instrument_name or ""), row.get("BROKER_ID"))
        if match:
            return match
        match = _match_instrument(instrument_rows, str(instrument_name or ""), None)
        if match:
            return match
    return fallback


def _compare_contract(primary: dict[str, Any] | None, reference: dict[str, Any] | None) -> dict[str, Any]:
    if not primary or not reference:
        return {
            "parityOk": False,
            "mismatches": [],
            "warnings": ["comparison_skipped_missing_instrument"],
        }

    mismatches: list[dict[str, Any]] = []
    warnings: list[str] = []
    for field in CONTRACT_FIELDS:
        if field not in primary or field not in reference:
            continue
        left = primary.get(field)
        right = reference.get(field)
        if _same_number(left, right):
            continue
        delta_pct = _relative_delta_pct(left, right)
        item = {
            "field": field,
            "primaryValue": left,
            "referenceValue": right,
            "relativeDeltaPct": round(delta_pct, 6) if delta_pct is not None else None,
        }
        if field in {"TICKSIZE", "TICKSTEP", "ORDERSIZEMULTIPLIER", "ORDERSIZESTEP"}:
            item["severity"] = "blocker"
        elif field in {"DEFAULTSPREAD", "POINTVALUE"}:
            item["severity"] = "requires_fix_or_explicit_waiver"
        else:
            item["severity"] = "warning"
        mismatches.append(item)

    if any(item["field"] == "DEFAULTSPREAD" for item in mismatches):
        warnings.append("cross_broker_spread_mismatch_can_inflate_simulated_vs_real_tick_drift")
    if any(item["field"] == "POINTVALUE" for item in mismatches):
        warnings.append("point_value_mismatch_can_change_profit_dd_and_retdd_scale")

    return {
        "parityOk": not mismatches,
        "mismatches": mismatches,
        "warnings": warnings,
    }


def _duplicate_summary(instrument_rows: list[dict[str, Any]], data_rows: list[dict[str, Any]], asset: str) -> dict[str, Any]:
    bare_asset = asset.upper()
    bare_instruments = [
        _public_instrument(row)
        for row in instrument_rows
        if _casefold(row.get("INSTRUMENT")) == _casefold(bare_asset)
    ]
    bare_data = [
        _public_data_row(row)
        for row in data_rows
        if _casefold(row.get("SYMBOL")) == _casefold(bare_asset) or _casefold(row.get("INSTRUMENT")) == _casefold(bare_asset)
    ]
    return {
        "bareAssetInstrumentRows": [row for row in bare_instruments if row is not None][:6],
        "bareAssetDataRows": bare_data[:12],
        "legacyBareAssetPresent": bool(bare_instruments or bare_data),
    }


def _review_decision(
    *,
    primary: dict[str, Any],
    reference: dict[str, Any],
    comparison: dict[str, Any],
    catalog_blockers: list[str],
    asset: str,
    timeframe: str,
) -> dict[str, Any]:
    blockers = list(catalog_blockers)
    warnings: list[str] = list(comparison.get("warnings") or [])

    if not primary.get("instrument"):
        blockers.append("primary_darwinex_instrument_missing")
    if not reference.get("effectiveInstrument"):
        blockers.append("reference_dukascopy_effective_instrument_missing")
    if primary.get("history", {}).get("positiveHistoryRows", 0) <= 0:
        blockers.append("primary_darwinex_history_missing_for_timeframe")
    if reference.get("history", {}).get("positiveHistoryRows", 0) <= 0:
        blockers.append("reference_dukascopy_history_missing_for_timeframe")

    mismatches = comparison.get("mismatches") if isinstance(comparison.get("mismatches"), list) else []
    hard_mismatch = any(item.get("severity") == "blocker" for item in mismatches)
    waiver_mismatch = any(item.get("severity") == "requires_fix_or_explicit_waiver" for item in mismatches)
    if hard_mismatch:
        blockers.append("contract_tick_or_order_size_mismatch")
    if waiver_mismatch:
        warnings.append("cost_contract_mismatch_requires_fix_or_explicit_waiver_before_next_capa1")
    if primary.get("history", {}).get("usesTickBackingSource"):
        warnings.append("primary_h1_uses_tick_backing_source_no_direct_h1_data_row")
    if reference.get("history", {}).get("usesTickBackingSource"):
        warnings.append("reference_h1_uses_tick_backing_source_no_direct_h1_data_row")
    if reference.get("history", {}).get("sourceOnlyFallbackUsed"):
        warnings.append("reference_dukascopy_history_source_only_fallback_uses_effective_darwinex_instrument")
    resolution = reference.get("resolution") if isinstance(reference.get("resolution"), dict) else {}
    if resolution.get("profileStatus") == "profile_missing_using_host_convention":
        warnings.append("reference_dukascopy_auto3_profile_missing_using_host_convention")

    requires_fix_or_waiver = bool(blockers or waiver_mismatch)
    if blockers:
        decision = "bsai21_blocked_fix_asset_broker_instrument_config_before_new_capa1"
        status = BS_AI21_STATUS_BLOCKED
    elif waiver_mismatch:
        decision = "bsai21_requires_fix_or_explicit_waiver_before_new_capa1"
        status = BS_AI21_STATUS_REQUIRES_WAIVER
    else:
        decision = "bsai21_review_clean_new_preregistered_capa1_allowed_with_controls"
        status = BS_AI21_STATUS_OK

    return {
        "decision": decision,
        "status": status,
        "asset": asset.upper(),
        "timeframe": timeframe.upper(),
        "newCapa1AllowedAfterReview": not requires_fix_or_waiver,
        "newCapa1AllowedWithExplicitWaiver": not bool(blockers) and requires_fix_or_waiver,
        "requiresFixOrExplicitWaiver": requires_fix_or_waiver,
        "selectedNextGate": (
            "BS-AI22 preregistered Capa1 design after BS-AI21 clean review"
            if not requires_fix_or_waiver
            else "fix or explicitly waive asset/broker/instrument config before BS-AI22"
        ),
        "currentBsAi16BranchRemainsFailedForCapa2": True,
        "capa2StartAllowed": False,
        "projectStartAllowed": False,
        "projectImportAllowed": False,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "methodology": (
            "BS-AI21 is a cost/config gate only. It does not rescue the failed BS-AI16 branch, "
            "does not relax filters and does not reinterpret pass states."
        ),
    }


def _base_payload(action: str, *, asset: str, timeframe: str, direction: str, experiment_id: str) -> dict[str, Any]:
    return {
        "ok": False,
        "version": BS_AI21_ASSET_REVIEW_VERSION,
        "action": action,
        "status": BS_AI21_STATUS_BLOCKED,
        "hostProfile": "sqx144_full",
        "experimentId": experiment_id,
        "asset": asset.upper(),
        "timeframe": timeframe.upper(),
        "direction": direction.upper(),
        "readMode": READ_MODE,
        "scope": {
            "primaryBroker": PRIMARY_BROKER_KEY,
            "referenceBroker": REFERENCE_BROKER_KEY,
            "checks": [
                "instrument rows",
                "broker/source ids",
                "history coverage by timeframe",
                "spread, point value, tick size, tick step",
                "order size multiplier/step",
                "legacy bare asset collisions",
            ],
        },
        "guards": {
            "readOnly": True,
            "writesDataDb": False,
            "writesUserProjects": False,
            "mutatesDatabanks": False,
            "runsSqxTasks": False,
            "projectStartRequested": False,
            "projectStopRequested": False,
            "projectImportRequested": False,
            "capa2StartAllowed": False,
            "taskmanagerOpenProjectAllowed": False,
            "loadAsIsAllowed": False,
            "addMissingSymbolsAllowed": False,
            "migrationToolAllowed": False,
            "officialBlocksettingsPromotion": False,
            "sqx144UpdatePromotion": False,
        },
        "privacy": {
            "localPathsReturned": False,
            "rawXmlReturned": False,
            "rawSqlReturned": False,
            "rawLogReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
        },
    }


def review_payload(
    project_root: str | Path,
    *,
    asset: str = "AUDCAD",
    timeframe: str = "H1",
    direction: str = "L",
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
    db_path: str | Path | None = None,
    write_evidence: bool = False,
) -> dict[str, Any]:
    root = _project_root(project_root)
    payload = _base_payload("review", asset=asset, timeframe=timeframe, direction=direction, experiment_id=experiment_id)
    conn, config_public, blockers = _load_db_connection(root, db_path=db_path)
    payload["config"] = config_public
    if conn is None:
        decision = _review_decision(
            primary={},
            reference={},
            comparison={"parityOk": False, "mismatches": [], "warnings": []},
            catalog_blockers=blockers,
            asset=asset,
            timeframe=timeframe,
        )
        payload.update({
            "status": decision["status"],
            "decision": decision,
            "ok": False,
            "catalog": {"available": False, "tableCounts": {}, "quickCheck": None},
            "evidenceWritten": False,
        })
        _privacy_guard(payload)
        return payload

    try:
        broker_rows = _select_rows(conn, "BROKER", BROKER_FIELDS)
        instrument_rows = _select_rows(conn, "INSTRUMENTS", INSTRUMENT_FIELDS)
        data_rows = _select_rows(conn, "DATA", DATA_FIELDS)
        table_counts = {
            "BROKER": _table_count(conn, "BROKER"),
            "INSTRUMENTS": _table_count(conn, "INSTRUMENTS"),
            "DATA": _table_count(conn, "DATA"),
        }
        quick_check = _quick_check(conn)
    finally:
        conn.close()

    primary_resolved = _resolve_broker(root, PRIMARY_BROKER_KEY, asset)
    reference_resolved = _resolve_broker(root, REFERENCE_BROKER_KEY, asset)
    primary_instrument = _match_instrument(instrument_rows, primary_resolved.get("targetInstrument"), primary_resolved.get("expectedBrokerId"))
    reference_instrument = _match_instrument(instrument_rows, reference_resolved.get("targetInstrument"), reference_resolved.get("expectedBrokerId"))
    primary_data, primary_effective_tf, primary_direct_rows, primary_source_only = _select_history_rows(
        data_rows,
        target=primary_resolved.get("targetInstrument"),
        data_symbol=primary_resolved.get("dataSymbol"),
        expected_broker_id=primary_resolved.get("expectedBrokerId"),
        expected_source_id=primary_resolved.get("expectedSourceId"),
        timeframe=timeframe,
        allow_source_only_fallback=False,
    )
    reference_data, reference_effective_tf, reference_direct_rows, reference_source_only = _select_history_rows(
        data_rows,
        target=reference_resolved.get("targetInstrument"),
        data_symbol=reference_resolved.get("dataSymbol"),
        expected_broker_id=reference_resolved.get("expectedBrokerId"),
        expected_source_id=reference_resolved.get("expectedSourceId"),
        timeframe=timeframe,
        allow_source_only_fallback=True,
    )
    primary_effective_instrument = _effective_instrument_from_history(primary_data, instrument_rows, primary_instrument)
    reference_effective_instrument = _effective_instrument_from_history(reference_data, instrument_rows, reference_instrument)
    comparison = _compare_contract(primary_effective_instrument, reference_effective_instrument)
    standalone_reference_comparison = _compare_contract(primary_instrument, reference_instrument)
    duplicate_summary = _duplicate_summary(instrument_rows, data_rows, asset)
    primary_public = {
        "resolution": primary_resolved,
        "broker": _public_broker_row(_match_broker(broker_rows, primary_resolved.get("expectedBrokerId"))),
        "instrument": _public_instrument(primary_instrument),
        "effectiveInstrument": _public_instrument(primary_effective_instrument),
        "history": _history_summary(
            primary_data,
            requested_timeframe=timeframe,
            effective_timeframe=primary_effective_tf,
            direct_requested_rows=primary_direct_rows,
            source_only_fallback=primary_source_only,
        ),
    }
    reference_public = {
        "resolution": reference_resolved,
        "broker": _public_broker_row(_match_broker(broker_rows, reference_resolved.get("expectedBrokerId"))),
        "instrument": _public_instrument(reference_instrument),
        "effectiveInstrument": _public_instrument(reference_effective_instrument),
        "history": _history_summary(
            reference_data,
            requested_timeframe=timeframe,
            effective_timeframe=reference_effective_tf,
            direct_requested_rows=reference_direct_rows,
            source_only_fallback=reference_source_only,
        ),
    }
    decision = _review_decision(
        primary=primary_public,
        reference=reference_public,
        comparison=comparison,
        catalog_blockers=blockers,
        asset=asset,
        timeframe=timeframe,
    )
    if duplicate_summary["legacyBareAssetPresent"]:
        decision["warnings"] = sorted(set(decision["warnings"] + ["legacy_bare_asset_rows_present_ignore_unless_explicitly_selected"]))
    standalone_mismatch = bool(standalone_reference_comparison.get("mismatches"))
    effective_is_primary = (
        reference_public.get("effectiveInstrument")
        and primary_public.get("effectiveInstrument")
        and reference_public["effectiveInstrument"].get("instrument") == primary_public["effectiveInstrument"].get("instrument")
    )
    if standalone_mismatch and effective_is_primary:
        decision["warnings"] = sorted(set(decision["warnings"] + ["standalone_dukascopy_instrument_differs_but_history_uses_darwinex_effective_instrument"]))

    payload.update({
        "ok": decision["decision"] == "bsai21_review_clean_new_preregistered_capa1_allowed_with_controls",
        "status": decision["status"],
        "catalog": {
            "available": True,
            "tableCounts": table_counts,
            "quickCheck": quick_check,
            "readMode": READ_MODE,
        },
        "primary": primary_public,
        "reference": reference_public,
        "contractComparison": comparison,
        "standaloneReferenceComparison": standalone_reference_comparison,
        "collisionReview": duplicate_summary,
        "decision": decision,
    })
    if write_evidence:
        payload["evidenceWritten"] = True
        payload["evidenceRef"] = write_evidence_file(root, "review", payload)
    else:
        payload["evidenceWritten"] = False
    _privacy_guard(payload)
    return payload


def status_payload(
    project_root: str | Path,
    *,
    asset: str = "AUDCAD",
    timeframe: str = "H1",
    direction: str = "L",
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
) -> dict[str, Any]:
    payload = _base_payload("status", asset=asset, timeframe=timeframe, direction=direction, experiment_id=experiment_id)
    payload.update({
        "ok": True,
        "status": "asset_broker_instrument_review_ready_readonly_no_apply",
        "actions": ["status", "review", "decision-template"],
        "target": {
            "asset": asset.upper(),
            "timeframe": timeframe.upper(),
            "direction": direction.upper(),
            "primaryBroker": PRIMARY_BROKER_KEY,
            "referenceBroker": REFERENCE_BROKER_KEY,
        },
        "nextAction": "run review to inspect current SQX144 Full catalog read-only",
        "evidenceWritten": False,
    })
    _privacy_guard(payload)
    return payload


def decision_template_payload(
    project_root: str | Path,
    *,
    asset: str = "AUDCAD",
    timeframe: str = "H1",
    direction: str = "L",
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
) -> dict[str, Any]:
    payload = status_payload(project_root, asset=asset, timeframe=timeframe, direction=direction, experiment_id=experiment_id)
    payload["action"] = "decision-template"
    payload["selectedDecision"] = "EJECUTAR BS-AI21 REVIEW READ-ONLY ACTIVO/BROKER/INSTRUMENTO"
    payload["approvalNotRequiredBecause"] = "read_only_catalog_review_writes_only_local_evidence"
    payload["blockedDecisions"] = [
        "ARRANCAR CAPA1 O CAPA2",
        "IMPORTAR PROYECTOS",
        "PATCH DIRECTO data.db",
        "MOVER user/projects O databanks",
        "USAR MIGRATION TOOL",
    ]
    _privacy_guard(payload)
    return payload


def write_evidence_file(project_root: Path, action: str, payload: dict[str, Any]) -> str:
    _privacy_guard(payload)
    evidence_dir = project_root.joinpath(*EVIDENCE_DIR_PARTS)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    filename = f"bsai21_asset_broker_instrument_review_{action}_{_utc_stamp()}.json"
    (evidence_dir / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return filename


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("status", "review", "decision-template"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--asset", default="AUDCAD")
    parser.add_argument("--timeframe", default="H1")
    parser.add_argument("--direction", default="L")
    parser.add_argument("--experiment-id", default=DEFAULT_EXPERIMENT_ID)
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)

    if args.action == "review":
        payload = review_payload(
            args.project_root,
            asset=args.asset,
            timeframe=args.timeframe,
            direction=args.direction,
            experiment_id=args.experiment_id,
            db_path=args.db_path,
            write_evidence=args.write_evidence,
        )
    elif args.action == "decision-template":
        payload = decision_template_payload(
            args.project_root,
            asset=args.asset,
            timeframe=args.timeframe,
            direction=args.direction,
            experiment_id=args.experiment_id,
        )
    else:
        payload = status_payload(
            args.project_root,
            asset=args.asset,
            timeframe=args.timeframe,
            direction=args.direction,
            experiment_id=args.experiment_id,
        )

    _privacy_guard(payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
