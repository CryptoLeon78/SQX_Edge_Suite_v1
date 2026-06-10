from __future__ import annotations

import csv
import hashlib
import io
import math
import re
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping


PORTFOLIO_CORRELATION_STABILITY_VERSION = "sqx142-portfolio-corr1-stability-audit-v1"
CAPA1_C2_CORRELATION_SELECTION_VERSION = "sqx142-capa1-c2-corr1-template-selection-v1"
CORRELATION_STABILITY_ENGINE_VERSION = "sqx142-correlation-stability-engine-v1"

DECISION_DOMAINS = {
    "capa1_c2_template_selection": {
        "version": CAPA1_C2_CORRELATION_SELECTION_VERSION,
        "source": "capa1_c2_corr1_is_selection_oos3_audit",
        "selectedLabel": "c2_template_winner",
        "similarLabel": "c2_template_similar",
        "reviewLabel": "c2_template_review",
        "selectionSurface": "Template Maker C2",
        "downstreamSurface": "Template C2 generation",
    },
    "capa2_portfolio_selection": {
        "version": PORTFOLIO_CORRELATION_STABILITY_VERSION,
        "source": "capa2_portfolio_corr1_is_selection_oos3_audit",
        "selectedLabel": "portfolio",
        "similarLabel": "similar",
        "reviewLabel": "review",
        "selectionSurface": "Portfolio Lab",
        "downstreamSurface": "Portfolio Master",
    },
}

DEFAULT_SETTINGS = {
    "maxIsCorrelation": 0.50,
    "maxOos3Correlation": 0.60,
    "warnOos3Correlation": 0.45,
    "maxCorrelationDrift": 0.25,
    "minComparablePoints": 12,
    "maxWinners": 12,
}

_PRIVATE_VALUE_RE = re.compile(
    r"(?i)([A-Z]:\\|\\\\|https?://\S*(?:token|secret|password|protected)\S*|"
    r"\b[\w.+-]+@[\w.-]+\.[A-Z]{2,}\b|"
    r"\b(?:token|secret|password|api[_-]?key|grant[_-]?key|session)[=:]\s*\S+)"
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _normalize_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", _text(value).casefold())


def _hash_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _numeric(value: Any, default: float = 0.0) -> float:
    if isinstance(value, (int, float)) and math.isfinite(value):
        return float(value)
    text = _text(value).replace("%", "").replace(",", ".")
    try:
        parsed = float(text)
    except ValueError:
        return default
    return parsed if math.isfinite(parsed) else default


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


def _redact_text(value: Any, default: str = "", limit: int = 160) -> tuple[str, bool]:
    text = _text(value, default)
    redacted = _PRIVATE_VALUE_RE.sub("[redacted]", text)
    return redacted[:limit], redacted != text


def _parse_series(value: Any) -> list[float]:
    if isinstance(value, (list, tuple)):
        return [_numeric(item, math.nan) for item in value if math.isfinite(_numeric(item, math.nan))]
    text = _text(value)
    if not text:
        return []
    values: list[float] = []
    for part in re.split(r"[\s|;]+", text):
        parsed = _numeric(part, math.nan)
        if math.isfinite(parsed):
            values.append(parsed)
    return values


def _return_series_from_equity(value: Any) -> list[float]:
    equity = _parse_series(value)
    if len(equity) < 3:
        return []
    returns: list[float] = []
    for previous, current in zip(equity, equity[1:]):
        returns.append((current - previous) / abs(previous) if previous else current - previous)
    return returns


def _pearson(a: list[float], b: list[float]) -> float | None:
    if len(a) != len(b) or len(a) < 2:
        return None
    mean_a = sum(a) / len(a)
    mean_b = sum(b) / len(b)
    num = 0.0
    den_a = 0.0
    den_b = 0.0
    for left, right in zip(a, b):
        da = left - mean_a
        db = right - mean_b
        num += da * db
        den_a += da * da
        den_b += db * db
    if not den_a or not den_b:
        return None
    return num / math.sqrt(den_a * den_b)


def _settings(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    cfg = dict(DEFAULT_SETTINGS)
    for key, value in (raw or {}).items():
        if key not in cfg:
            continue
        if key in {"minComparablePoints", "maxWinners"}:
            cfg[key] = max(1, int(_numeric(value, cfg[key])))
        else:
            cfg[key] = round(max(0.0, min(1.0, _numeric(value, cfg[key]))), 4)
    return cfg


def _parse_csv_rows(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [dict(item) for item in value if isinstance(item, Mapping)]
    text = _text(value)
    if not text:
        return []
    try:
        dialect = csv.Sniffer().sniff(text[:2048], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    return list(csv.DictReader(io.StringIO(text), dialect=dialect))


def _strategy_key(row: Mapping[str, Any], index: int = 0) -> str:
    identity = _value(row, ("strategy", "Strategy", "Strategy Name", "name", "id", "candidateId"), f"candidate-{index + 1}")
    return _normalize_key(identity)


def _series_row_map(value: Any) -> dict[str, dict[str, Any]]:
    rows = _parse_csv_rows(value)
    return {_strategy_key(row, index): row for index, row in enumerate(rows)}


def _score(row: Mapping[str, Any]) -> float:
    pf = min(2.4, max(0.0, _numeric(_value(row, ("profitFactor", "Profit Factor", "PF"), 0))))
    ret_dd = min(10.0, max(0.0, _numeric(_value(row, ("retDd", "Ret/DD Ratio", "Return / Drawdown ratio"), 0))))
    drawdown = max(0.0, 100.0 - min(100.0, _numeric(_value(row, ("maxDd", "Max DD %", "Max Drawdown %"), 100))))
    trades = min(500.0, max(0.0, _numeric(_value(row, ("trades", "Number of trades", "# of trades"), 0))))
    return round((pf * 22) + (ret_dd * 7) + (drawdown * 0.26) + (trades * 0.045), 2)


def _series_for(row: Mapping[str, Any], period: str) -> list[float]:
    aliases = {
        "is": (
            ("isReturnSeries", "IS Return Series", "Returns IS", "returnSeriesIS", "IS Returns"),
            ("isEquitySeries", "IS Equity Series", "Equity IS", "equitySeriesIS", "IS Equity"),
        ),
        "oos3": (
            ("oos3ReturnSeries", "OOS3 Return Series", "Forward Return Series", "returnSeriesOOS3", "OOS3 Returns"),
            ("oos3EquitySeries", "OOS3 Equity Series", "Forward Equity Series", "equitySeriesOOS3", "OOS3 Equity"),
        ),
    }
    return_aliases, equity_aliases = aliases[period]
    direct = _parse_series(_value(row, return_aliases))
    if len(direct) >= 2:
        return direct
    return _return_series_from_equity(_value(row, equity_aliases))


def _candidate(row: Mapping[str, Any], index: int, is_row: Mapping[str, Any] | None, oos3_row: Mapping[str, Any] | None) -> dict[str, Any]:
    identity = _value(row, ("strategy", "Strategy", "Strategy Name", "name", "id"), f"candidate-{index + 1}")
    strategy_label, redacted = _redact_text(identity)
    merged_is = dict(row)
    if is_row:
        merged_is.update(is_row)
    merged_oos3 = dict(row)
    if oos3_row:
        merged_oos3.update(oos3_row)
    asset, asset_redacted = _redact_text(_value(row, ("asset", "symbol", "Symbol", "Market"), "GENERIC"), "GENERIC", 40)
    timeframe, tf_redacted = _redact_text(_value(row, ("timeframe", "tf", "TimeFrame", "Time frame"), "H1"), "H1", 20)
    block, block_redacted = _redact_text(_value(row, ("blockSetting", "BlockSetting", "bs", "Block Setting"), "BS_Custom"), "BS_Custom", 120)
    return {
        "candidateId": _hash_id("candidate", f"{index}|{strategy_label}|{asset}|{timeframe}|{block}"),
        "strategyRef": _hash_id("strategy", strategy_label),
        "sourceIndex": index,
        "score": _score(row),
        "asset": asset.upper() or "GENERIC",
        "timeframe": timeframe.upper() or "H1",
        "blockSetting": block or "BS_Custom",
        "isSeries": _series_for(merged_is, "is"),
        "oos3Series": _series_for(merged_oos3, "oos3"),
        "redactions": sum(int(flag) for flag in (redacted, asset_redacted, tf_redacted, block_redacted)),
    }


def _best_pair(candidate: Mapping[str, Any], winners: list[Mapping[str, Any]], period: str, min_points: int) -> tuple[float | None, Mapping[str, Any] | None, str]:
    series_key = "isSeries" if period == "is" else "oos3Series"
    series = list(candidate.get(series_key, []))
    best_corr: float | None = None
    best_winner: Mapping[str, Any] | None = None
    status = "not_available"
    for winner in winners:
        winner_series = list(winner.get(series_key, []))
        if len(series) < min_points or len(winner_series) < min_points:
            continue
        if len(series) != len(winner_series):
            status = "not_comparable"
            continue
        corr = _pearson(series, winner_series)
        if corr is None:
            continue
        status = "available"
        if best_corr is None or corr > best_corr:
            best_corr = corr
            best_winner = winner
    return best_corr, best_winner, status


def _audit_selected_pairs(selected: list[Mapping[str, Any]], cfg: Mapping[str, Any]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    min_points = int(cfg["minComparablePoints"])
    for left_index, left in enumerate(selected):
        for right in selected[left_index + 1:]:
            is_corr = None
            oos3_corr = None
            is_status = "not_available"
            oos3_status = "not_available"
            left_is = list(left.get("isSeries", []))
            right_is = list(right.get("isSeries", []))
            left_oos3 = list(left.get("oos3Series", []))
            right_oos3 = list(right.get("oos3Series", []))
            if len(left_is) >= min_points and len(right_is) >= min_points:
                if len(left_is) == len(right_is):
                    is_corr = _pearson(left_is, right_is)
                    is_status = "available" if is_corr is not None else "not_available"
                else:
                    is_status = "not_comparable"
            if len(left_oos3) >= min_points and len(right_oos3) >= min_points:
                if len(left_oos3) == len(right_oos3):
                    oos3_corr = _pearson(left_oos3, right_oos3)
                    oos3_status = "available" if oos3_corr is not None else "not_available"
                else:
                    oos3_status = "not_comparable"
            drift = abs(oos3_corr - is_corr) if is_corr is not None and oos3_corr is not None else None
            flags: list[str] = []
            if oos3_corr is not None and oos3_corr >= float(cfg["maxOos3Correlation"]):
                flags.append("oos3_correlation_break")
            elif oos3_corr is not None and oos3_corr >= float(cfg["warnOos3Correlation"]):
                flags.append("oos3_correlation_warn")
            if drift is not None and drift >= float(cfg["maxCorrelationDrift"]):
                flags.append("correlation_drift_warn")
            pairs.append({
                "leftCandidateId": left["candidateId"],
                "rightCandidateId": right["candidateId"],
                "isCorrelation": round(is_corr, 4) if is_corr is not None else None,
                "oos3Correlation": round(oos3_corr, 4) if oos3_corr is not None else None,
                "correlationDrift": round(drift, 4) if drift is not None else None,
                "isStatus": is_status,
                "oos3Status": oos3_status,
                "flags": flags,
            })
    return pairs


def build_portfolio_correlation_stability_report(
    payload: Mapping[str, Any] | str | list[Any],
    settings: Mapping[str, Any] | None = None,
    *,
    decision_domain: str = "capa2_portfolio_selection",
) -> dict[str, Any]:
    domain_key = decision_domain if decision_domain in DECISION_DOMAINS else "capa2_portfolio_selection"
    domain = DECISION_DOMAINS[domain_key]
    if isinstance(payload, Mapping):
        rows = _parse_csv_rows(payload.get("csv") or payload.get("rows") or payload.get("candidates") or "")
        if not rows and isinstance(payload.get("portfolioLab"), Mapping):
            rows = _parse_csv_rows(payload["portfolioLab"].get("rows", []))
        is_rows = _series_row_map(payload.get("isSeriesCsv") or payload.get("isCsv") or payload.get("isRows") or "")
        oos3_rows = _series_row_map(payload.get("oos3SeriesCsv") or payload.get("oos3Csv") or payload.get("oos3Rows") or "")
        cfg = _settings(settings or payload.get("settings") if isinstance(payload.get("settings"), Mapping) else settings)
    else:
        rows = _parse_csv_rows(payload)
        is_rows = {}
        oos3_rows = {}
        cfg = _settings(settings)

    candidates: list[dict[str, Any]] = []
    redactions = 0
    for index, row in enumerate(rows):
        key = _strategy_key(row, index)
        candidate = _candidate(row, index, is_rows.get(key), oos3_rows.get(key))
        redactions += int(candidate.pop("redactions", 0))
        candidates.append(candidate)
    candidates.sort(key=lambda item: (-float(item["score"]), int(item["sourceIndex"])))

    selected: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    min_points = int(cfg["minComparablePoints"])
    for candidate in candidates:
        is_corr, is_winner, is_status = _best_pair(candidate, selected, "is", min_points)
        oos3_corr, oos3_winner, oos3_status = _best_pair(candidate, selected, "oos3", min_points)
        nearest_drift = abs(oos3_corr - is_corr) if is_corr is not None and oos3_corr is not None else None
        nearest_flags: list[str] = []
        if oos3_corr is not None and oos3_corr >= float(cfg["maxOos3Correlation"]):
            nearest_flags.append("oos3_correlation_break_to_selected")
        elif oos3_corr is not None and oos3_corr >= float(cfg["warnOos3Correlation"]):
            nearest_flags.append("oos3_correlation_warn_to_selected")
        if nearest_drift is not None and nearest_drift >= float(cfg["maxCorrelationDrift"]):
            nearest_flags.append("correlation_drift_warn_to_selected")
        reasons: list[str] = []
        if len(candidate["isSeries"]) < min_points:
            reasons.append("IS series missing or too short")
        if len(candidate["oos3Series"]) < min_points:
            reasons.append("OOS3 series missing or too short")
        if is_corr is not None and is_corr >= float(cfg["maxIsCorrelation"]):
            reasons.append(f"IS correlation >= {cfg['maxIsCorrelation']}")
        if not reasons and len(selected) >= int(cfg["maxWinners"]):
            reasons.append("max winners reached")
        decision = "selected_is" if not reasons else ("similar_is" if any(reason.startswith("IS correlation") for reason in reasons) else "review")
        if decision == "selected_is":
            selected.append(candidate)
        items.append({
            "candidateId": candidate["candidateId"],
            "strategyRef": candidate["strategyRef"],
            "decision": decision,
            "reason": " · ".join(reasons) if reasons else "selected by IS correlation only; OOS3 reserved for stability audit",
            "score": candidate["score"],
            "maxIsCorrelationToSelected": round(is_corr, 4) if is_corr is not None else None,
            "maxOos3CorrelationToSelected": round(oos3_corr, 4) if oos3_corr is not None else None,
            "correlationDriftToSelected": round(nearest_drift, 4) if nearest_drift is not None else None,
            "nearestIsWinnerId": is_winner["candidateId"] if is_winner else "",
            "nearestOos3WinnerId": oos3_winner["candidateId"] if oos3_winner else "",
            "isCorrelationStatus": is_status,
            "oos3CorrelationStatus": oos3_status,
            "nearestOos3AuditFlags": nearest_flags,
            "seriesPoints": {
                "is": len(candidate["isSeries"]),
                "oos3": len(candidate["oos3Series"]),
            },
            "trace": {
                "asset": candidate["asset"],
                "timeframe": candidate["timeframe"],
                "BlockSetting": candidate["blockSetting"],
            },
        })

    selected_pairs = _audit_selected_pairs(selected, cfg)
    pair_flags = [flag for pair in selected_pairs for flag in pair["flags"]]
    oos3_breaks = sum(1 for flag in pair_flags if flag == "oos3_correlation_break")
    oos3_warnings = sum(1 for flag in pair_flags if flag in {"oos3_correlation_warn", "correlation_drift_warn"})
    status = "pass"
    if oos3_breaks:
        status = "blocked_oos3_correlation_break"
    elif oos3_warnings:
        status = "review_oos3_correlation_drift"

    return {
        "ok": True,
        "version": domain["version"],
        "engineVersion": CORRELATION_STABILITY_ENGINE_VERSION,
        "legacyVersion": PORTFOLIO_CORRELATION_STABILITY_VERSION,
        "mode": "external_readonly",
        "source": domain["source"],
        "decisionDomain": domain_key,
        "decisionLabels": {
            "selected": domain["selectedLabel"],
            "similar": domain["similarLabel"],
            "review": domain["reviewLabel"],
        },
        "selectionSurface": domain["selectionSurface"],
        "downstreamSurface": domain["downstreamSurface"],
        "analyzedAt": _now_iso(),
        "settings": cfg,
        "methodology": {
            "selectionBasis": "IS_CORR only",
            "auditBasis": "OOS3_CORR stability confirmation only",
            "oos3MaySelectAlternates": False,
            "requiresFreshHoldoutIfOos3UsedForSelection": True,
            "capa1CorrelationPurpose": "Template C2 selection" if domain_key == "capa1_c2_template_selection" else "",
            "capa2CorrelationPurpose": "Portfolio selection" if domain_key == "capa2_portfolio_selection" else "",
        },
        "summary": {
            "inputRows": len(rows),
            "selectedByIs": sum(1 for item in items if item["decision"] == "selected_is"),
            "c2TemplateSelectedByIs": sum(1 for item in items if item["decision"] == "selected_is") if domain_key == "capa1_c2_template_selection" else 0,
            "portfolioSelectedByIs": sum(1 for item in items if item["decision"] == "selected_is") if domain_key == "capa2_portfolio_selection" else 0,
            "similarByIs": sum(1 for item in items if item["decision"] == "similar_is"),
            "review": sum(1 for item in items if item["decision"] == "review"),
            "selectedPairs": len(selected_pairs),
            "oos3CorrelationBreaks": oos3_breaks,
            "oos3Warnings": oos3_warnings,
            "nearestOos3Comparable": sum(1 for item in items if item.get("maxOos3CorrelationToSelected") is not None),
            "nearestOos3Warnings": sum(1 for item in items if item.get("nearestOos3AuditFlags")),
            "status": status,
            "redactedFields": redactions,
        },
        "items": items,
        "selectedPairAudit": selected_pairs,
        "privacy": {
            "local_paths_returned": False,
            "raw_strategy_names_returned": False,
            "private_fields_returned": False,
            "tokens_returned": False,
        },
        "blockers": ["oos3_stability_break"] if oos3_breaks else [],
        "warnings": ["oos3_used_as_audit_not_selector"] + (["oos3_correlation_drift_review"] if oos3_warnings else []),
    }


def build_capa1_c2_correlation_selection_report(
    payload: Mapping[str, Any] | str | list[Any],
    settings: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return build_portfolio_correlation_stability_report(
        payload,
        settings,
        decision_domain="capa1_c2_template_selection",
    )


def export_portfolio_correlation_stability_csv(report: Mapping[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "leftCandidateId",
            "rightCandidateId",
            "isCorrelation",
            "oos3Correlation",
            "correlationDrift",
            "isStatus",
            "oos3Status",
            "flags",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    for row in report.get("selectedPairAudit", []):
        if not isinstance(row, Mapping):
            continue
        writer.writerow({
            "leftCandidateId": row.get("leftCandidateId", ""),
            "rightCandidateId": row.get("rightCandidateId", ""),
            "isCorrelation": row.get("isCorrelation", ""),
            "oos3Correlation": row.get("oos3Correlation", ""),
            "correlationDrift": row.get("correlationDrift", ""),
            "isStatus": row.get("isStatus", ""),
            "oos3Status": row.get("oos3Status", ""),
            "flags": "|".join(row.get("flags", [])),
        })
    return output.getvalue()
