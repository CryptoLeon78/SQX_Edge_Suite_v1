from __future__ import annotations

import csv
import hashlib
import io
import math
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .sqx_compatibility import SQX142_DEFAULT_ROOT


MT5_DATA_INTAKE_PROBE_VERSION = "sqx142-mt5-data-intake-probe-v1"

DEFAULT_SETTINGS = {
    "minBars": 20,
    "maxBars": 2000,
    "minOverlapDays": 1,
}

_PRIVATE_KEY_MARKERS = (
    "token",
    "secret",
    "password",
    "cookie",
    "email",
    "login",
    "account",
    "brokerPrivate",
    "protectedUrl",
    "path",
)

_PRIVATE_VALUE_RE = re.compile(
    r"(?i)([A-Z]:\\|\\\\|https?://\S*(?:token|secret|password|protected)\S*|"
    r"\b[\w.+-]+@[\w.-]+\.[A-Z]{2,}\b|"
    r"\b(?:token|secret|password|api[_-]?key|grant[_-]?key|session)[=:]\s*\S+)"
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _hash_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _normalize_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", _text(value).casefold())


def _numeric(value: Any, default: float = 0.0) -> float:
    if isinstance(value, (int, float)) and math.isfinite(value):
        return float(value)
    text = _text(value).replace(",", ".")
    try:
        parsed = float(text)
    except ValueError:
        return default
    return parsed if math.isfinite(parsed) else default


def _redact_text(value: Any, default: str = "") -> tuple[str, bool]:
    text = _text(value, default)
    redacted = _PRIVATE_VALUE_RE.sub("[redacted]", text)
    return redacted[:160], redacted != text


def _redact_mapping(value: Mapping[str, Any]) -> tuple[dict[str, Any], int]:
    clean: dict[str, Any] = {}
    redactions = 0
    for key, raw in value.items():
        key_text, key_redacted = _redact_text(key)
        if key_redacted or any(marker.casefold() in key_text.casefold() for marker in _PRIVATE_KEY_MARKERS):
            clean[key_text] = "[redacted]"
            redactions += 1
            continue
        if isinstance(raw, Mapping):
            nested, nested_redactions = _redact_mapping(raw)
            clean[key_text] = nested
            redactions += nested_redactions
            continue
        text, redacted = _redact_text(raw)
        clean[key_text] = text
        redactions += int(redacted)
    return clean, redactions


def _value(row: Mapping[str, Any], aliases: Iterable[str], default: Any = "") -> Any:
    for alias in aliases:
        if alias in row and row[alias] not in (None, ""):
            return row[alias]
    normalized = {_normalize_key(key): value for key, value in row.items()}
    for alias in aliases:
        key = _normalize_key(alias)
        if key in normalized and normalized[key] not in (None, ""):
            return normalized[key]
    return default


def _parse_dt(value: Any) -> datetime | None:
    text = _text(value)
    if not text:
        return None
    text = text.replace("Z", "+00:00")
    for candidate in (text, text.replace(".", "-"), text.replace(" ", "T")):
        try:
            parsed = datetime.fromisoformat(candidate)
            return parsed.astimezone(timezone.utc).replace(tzinfo=None) if parsed.tzinfo else parsed
        except ValueError:
            continue
    for fmt in ("%Y.%m.%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y.%m.%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _date_text(value: datetime | None) -> str:
    return value.date().isoformat() if value else ""


def _settings(raw: Mapping[str, Any] | None) -> dict[str, int]:
    result = dict(DEFAULT_SETTINGS)
    for key, value in (raw or {}).items():
        if key not in result:
            continue
        result[key] = max(1, min(100000, int(_numeric(value, result[key]))))
    return result


def _rows_from_csv(text: str) -> list[dict[str, Any]]:
    return [dict(row) for row in csv.DictReader(io.StringIO(text))]


def parse_mt5_ohlc_input(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, str):
        return _rows_from_csv(payload)
    if isinstance(payload, Mapping):
        for key in ("rows", "ohlcRows", "mt5Rows", "items"):
            rows = payload.get(key)
            if isinstance(rows, list):
                return [dict(item) for item in rows if isinstance(item, Mapping)]
        csv_text = payload.get("csv") or payload.get("mt5Csv") or payload.get("ohlcCsv")
        if isinstance(csv_text, str):
            return _rows_from_csv(csv_text)
    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, Mapping)]
    return []


def _normalized_bar(row: Mapping[str, Any], index: int) -> tuple[dict[str, Any] | None, list[str], int]:
    _clean, redactions = _redact_mapping(row)
    time_value = _value(row, ("time", "datetime", "date", "Time", "Date"))
    dt = _parse_dt(time_value)
    open_v = _numeric(_value(row, ("open", "Open"), math.nan), math.nan)
    high_v = _numeric(_value(row, ("high", "High"), math.nan), math.nan)
    low_v = _numeric(_value(row, ("low", "Low"), math.nan), math.nan)
    close_v = _numeric(_value(row, ("close", "Close"), math.nan), math.nan)
    volume_v = _numeric(_value(row, ("volume", "tick_volume", "real_volume", "Volume"), 0.0), 0.0)
    issues: list[str] = []
    if dt is None:
        issues.append("invalid_time")
    if not all(math.isfinite(value) for value in (open_v, high_v, low_v, close_v)):
        issues.append("invalid_ohlc_number")
    elif high_v < max(open_v, close_v, low_v) or low_v > min(open_v, close_v, high_v):
        issues.append("invalid_ohlc_shape")
    if issues or dt is None:
        return None, issues, redactions
    return {
        "index": index,
        "time": dt,
        "open": open_v,
        "high": high_v,
        "low": low_v,
        "close": close_v,
        "volume": max(0.0, volume_v),
    }, issues, redactions


def _normalize_timeframe(value: Any) -> str:
    tf = _text(value).upper().replace(" ", "")
    aliases = {"60": "H1", "240": "H4", "5": "M5", "15": "M15", "30": "M30", "1H": "H1", "4H": "H4"}
    return aliases.get(tf, tf or "UNKNOWN")


def _catalog_rows_from_data_db(
    sqx142_root: Path | None,
    *,
    asset: str,
    timeframe: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    data_db = Path(sqx142_root or SQX142_DEFAULT_ROOT) / "user" / "data" / "data.db"
    if not data_db.is_file():
        return []
    con = sqlite3.connect(f"file:{data_db}?mode=ro", uri=True)
    try:
        columns = {str(row[1]).upper() for row in con.execute('pragma table_info("DATA")').fetchall()}
        wanted = [name for name in ["SYMBOL", "INSTRUMENT", "TIMEFRAME", "TIMEFRAMETYPE", "DATATYPE", "DATEFROM", "DATETO", "TIMEZONE"] if name in columns]
        if not wanted:
            return []
        select = ", ".join(f'"{name}"' for name in wanted)
        clauses: list[str] = []
        params: list[Any] = []
        if asset and "SYMBOL" in columns:
            clauses.append('upper("SYMBOL") like ?')
            params.append(f"%{asset.upper()}%")
        elif asset and "INSTRUMENT" in columns:
            clauses.append('upper("INSTRUMENT") like ?')
            params.append(f"%{asset.upper()}%")
        if timeframe and "TIMEFRAME" in columns:
            clauses.append('upper("TIMEFRAME") = ?')
            params.append(timeframe.upper())
        where = " where " + " and ".join(clauses) if clauses else ""
        rows = con.execute(f'select {select} from "DATA"{where} limit ?', (*params, max(1, min(200, limit)))).fetchall()
        return [dict(zip(wanted, row)) for row in rows]
    except sqlite3.Error:
        return []
    finally:
        con.close()


def _catalog_rows(payload: Mapping[str, Any], sqx142_root: Path | None, asset: str, timeframe: str) -> list[dict[str, Any]]:
    supplied = payload.get("sqxDataRows") or payload.get("dataDbRows") or payload.get("catalogRows")
    if isinstance(supplied, list):
        return [dict(item) for item in supplied if isinstance(item, Mapping)]
    return _catalog_rows_from_data_db(sqx142_root, asset=asset, timeframe=timeframe)


def _catalog_item(row: Mapping[str, Any], index: int) -> dict[str, Any]:
    symbol = _text(_value(row, ("SYMBOL", "symbol", "instrument", "INSTRUMENT"), ""))
    instrument = _text(_value(row, ("INSTRUMENT", "instrument", "symbol", "SYMBOL"), symbol))
    timeframe = _normalize_timeframe(_value(row, ("TIMEFRAME", "timeframe", "tf", "TimeFrame"), ""))
    date_from = _parse_dt(_value(row, ("DATEFROM", "dateFrom", "from", "start"), ""))
    date_to = _parse_dt(_value(row, ("DATETO", "dateTo", "to", "end"), ""))
    return {
        "seriesId": _hash_id("series", f"{index}|{symbol}|{instrument}|{timeframe}|{_date_text(date_from)}|{_date_text(date_to)}"),
        "symbolRef": _hash_id("symbol", symbol or instrument or f"catalog-{index}"),
        "timeframe": timeframe,
        "dateFrom": _date_text(date_from),
        "dateTo": _date_text(date_to),
        "dataType": _text(_value(row, ("DATATYPE", "dataType"), "")),
        "timezone": _text(_value(row, ("TIMEZONE", "timezone"), ""))[:40],
        "_symbolMatchKey": _normalize_key(f"{symbol} {instrument}"),
        "_dateFromRaw": date_from,
        "_dateToRaw": date_to,
    }


def _overlap_days(left_from: datetime | None, left_to: datetime | None, right_from: datetime | None, right_to: datetime | None) -> int:
    if not all((left_from, left_to, right_from, right_to)):
        return 0
    start = max(left_from, right_from)  # type: ignore[arg-type]
    end = min(left_to, right_to)  # type: ignore[arg-type]
    return max(0, (end.date() - start.date()).days + 1)


def build_mt5_data_intake_probe_report(
    payload: Any,
    settings: Mapping[str, Any] | None = None,
    *,
    sqx142_root: Path | None = None,
) -> dict[str, Any]:
    cfg = _settings(settings)
    source_payload = payload if isinstance(payload, Mapping) else {"rows": payload}
    rows = parse_mt5_ohlc_input(source_payload)
    asset_raw = _text(_value(source_payload, ("asset", "symbol", "mt5Symbol"), "UNKNOWN")) if isinstance(source_payload, Mapping) else "UNKNOWN"
    timeframe = _normalize_timeframe(_value(source_payload, ("timeframe", "tf", "TimeFrame"), "UNKNOWN")) if isinstance(source_payload, Mapping) else "UNKNOWN"
    asset, asset_redacted = _redact_text(asset_raw, "UNKNOWN")
    asset_key = _normalize_key(asset)

    bars: list[dict[str, Any]] = []
    invalid_rows = 0
    redactions = int(asset_redacted)
    for index, row in enumerate(rows[: int(cfg["maxBars"])]):
        bar, issues, count = _normalized_bar(row, index)
        redactions += count
        if issues:
            invalid_rows += 1
            continue
        if bar is not None:
            bars.append(bar)
    bars.sort(key=lambda item: item["time"])

    warnings: list[str] = []
    blockers: list[str] = []
    if len(rows) > int(cfg["maxBars"]):
        warnings.append("max_bars_applied")
    if len(bars) < int(cfg["minBars"]):
        blockers.append("not_enough_bars")
    if invalid_rows:
        warnings.append("invalid_rows_ignored")

    duplicate_times = len(bars) - len({bar["time"] for bar in bars})
    if duplicate_times:
        warnings.append("duplicate_times")

    gaps = 0
    if len(bars) >= 2:
        deltas = [(right["time"] - left["time"]).total_seconds() for left, right in zip(bars, bars[1:])]
        positive = [delta for delta in deltas if delta > 0]
        baseline = min(positive) if positive else 0
        gaps = sum(1 for delta in positive if baseline and delta > baseline * 1.5)
        if gaps:
            warnings.append("time_gaps_detected")

    mt5_from = bars[0]["time"] if bars else None
    mt5_to = bars[-1]["time"] if bars else None
    catalog_source = "payload"
    catalog_rows = []
    if isinstance(source_payload, Mapping):
        supplied = source_payload.get("sqxDataRows") or source_payload.get("dataDbRows") or source_payload.get("catalogRows")
        catalog_source = "payload" if isinstance(supplied, list) else "data_db_readonly"
        catalog_rows = _catalog_rows(source_payload, sqx142_root, asset, timeframe)
    catalog = [_catalog_item(row, index) for index, row in enumerate(catalog_rows)]
    matches = [
        item for item in catalog
        if (not asset_key or asset_key in item["_symbolMatchKey"] or item["_symbolMatchKey"] in asset_key)
        and (item["timeframe"] == timeframe or item["timeframe"] == "UNKNOWN" or timeframe == "UNKNOWN")
    ]
    best_match: dict[str, Any] | None = None
    best_overlap = 0
    for item in matches:
        overlap = _overlap_days(mt5_from, mt5_to, item["_dateFromRaw"], item["_dateToRaw"])
        if overlap > best_overlap:
            best_overlap = overlap
            best_match = item
    if not matches:
        warnings.append("sqx_data_catalog_match_missing")
    elif best_overlap < int(cfg["minOverlapDays"]):
        warnings.append("sqx_data_range_overlap_missing")

    if blockers:
        decision = "intake_probe_fail"
    elif not matches or best_overlap < int(cfg["minOverlapDays"]) or warnings:
        decision = "intake_probe_review"
    else:
        decision = "intake_probe_pass"

    sanitized_matches = []
    for item in matches[:5]:
        sanitized_matches.append({
            "seriesId": item["seriesId"],
            "symbolRef": item["symbolRef"],
            "timeframe": item["timeframe"],
            "dateFrom": item["dateFrom"],
            "dateTo": item["dateTo"],
            "dataType": item["dataType"],
            "timezone": item["timezone"],
            "overlapDays": _overlap_days(mt5_from, mt5_to, item["_dateFromRaw"], item["_dateToRaw"]),
        })

    return {
        "ok": True,
        "version": MT5_DATA_INTAKE_PROBE_VERSION,
        "mode": "external_readonly",
        "source": "mt5_csv_copy",
        "analyzedAt": _now_iso(),
        "settings": cfg,
        "decision": decision,
        "summary": {
            "inputRows": len(rows),
            "validBars": len(bars),
            "invalidRows": invalid_rows,
            "duplicateTimes": duplicate_times,
            "timeGaps": gaps,
            "catalogRows": len(catalog),
            "catalogMatches": len(matches),
            "bestOverlapDays": best_overlap,
            "redactedFields": redactions,
        },
        "probe": {
            "assetRef": _hash_id("asset", asset),
            "timeframe": timeframe,
            "dateFrom": _date_text(mt5_from),
            "dateTo": _date_text(mt5_to),
            "barsHash": _hash_id("bars", "|".join(f"{bar['time'].isoformat()}:{bar['open']}:{bar['high']}:{bar['low']}:{bar['close']}" for bar in bars[:500])),
        },
        "sqxCatalog": {
            "source": catalog_source,
            "matched": bool(matches),
            "bestMatchSeriesId": best_match["seriesId"] if best_match else "",
            "matches": sanitized_matches,
        },
        "warnings": warnings,
        "blockers": blockers,
        "privacy": {
            "local_paths_returned": False,
            "raw_mt5_symbol_returned": False,
            "raw_sqx_symbol_returned": False,
            "private_fields_returned": False,
            "tokens_returned": False,
        },
        "guards": {
            "mt5_terminal_started": False,
            "mt5_ipc_called": False,
            "sqx_runtime_started": False,
            "data_db_mode": "ro" if catalog_source == "data_db_readonly" else "payload_fixture",
            "sqx_data_imported": False,
            "generation_enabled": False,
        },
    }


def export_mt5_data_intake_probe_csv(report: Mapping[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "decision",
            "assetRef",
            "timeframe",
            "dateFrom",
            "dateTo",
            "validBars",
            "catalogMatches",
            "bestOverlapDays",
            "warnings",
            "blockers",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    probe = report.get("probe", {}) if isinstance(report.get("probe"), Mapping) else {}
    summary = report.get("summary", {}) if isinstance(report.get("summary"), Mapping) else {}
    writer.writerow({
        "decision": report.get("decision", ""),
        "assetRef": probe.get("assetRef", ""),
        "timeframe": probe.get("timeframe", ""),
        "dateFrom": probe.get("dateFrom", ""),
        "dateTo": probe.get("dateTo", ""),
        "validBars": summary.get("validBars", ""),
        "catalogMatches": summary.get("catalogMatches", ""),
        "bestOverlapDays": summary.get("bestOverlapDays", ""),
        "warnings": "|".join(str(item) for item in report.get("warnings", []) if item),
        "blockers": "|".join(str(item) for item in report.get("blockers", []) if item),
    })
    return output.getvalue()
