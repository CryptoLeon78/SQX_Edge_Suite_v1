from __future__ import annotations

import csv
import hashlib
import io
import math
import re
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping


CORRELATION_FILTER_EXTERNAL_VERSION = "sqx142-correlation-filter-external-v1"

DEFAULT_SETTINGS = {
    "period": "Day",
    "maxCorrelation": 0.50,
    "warnCorrelation": 0.35,
    "minComparablePoints": 12,
    "similarityThreshold": 0.78,
    "maxWinners": 12,
}

_SERIES_ALIASES = {
    "returnSeries": ("returnSeries", "Return Series", "Returns", "returns", "Monthly Returns"),
    "equitySeries": ("equitySeries", "Equity Series", "EquityCurve", "Equity Curve", "Balance Curve"),
}

_PRIVATE_KEY_MARKERS = (
    "token",
    "secret",
    "password",
    "cookie",
    "email",
    "login",
    "account",
    "balance",
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
    text = _text(value).replace("%", "").replace(",", ".")
    try:
        parsed = float(text)
    except ValueError:
        return default
    return parsed if math.isfinite(parsed) else default


def _bool_marker(value: Any) -> bool:
    normalized = _normalize_key(value)
    return normalized in {"1", "true", "yes", "y", "si", "sí", "sample", "demo", "example", "only"}


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


def _parse_series(value: Any) -> list[float]:
    if isinstance(value, (list, tuple)):
        return [_numeric(item, math.nan) for item in value if math.isfinite(_numeric(item, math.nan))]
    text = _text(value)
    if not text:
        return []
    parts = re.split(r"[\s|;]+", text)
    values: list[float] = []
    for part in parts:
        parsed = _numeric(part, math.nan)
        if math.isfinite(parsed):
            values.append(parsed)
    return values


def _return_series(row: Mapping[str, Any]) -> list[float]:
    returns = _parse_series(_value(row, _SERIES_ALIASES["returnSeries"]))
    if len(returns) >= 2:
        return returns
    equity = _parse_series(_value(row, _SERIES_ALIASES["equitySeries"]))
    if len(equity) < 3:
        return []
    series: list[float] = []
    for previous, current in zip(equity, equity[1:]):
        series.append((current - previous) / abs(previous) if previous else current - previous)
    return series


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


def _is_forward_source(value: Any) -> bool:
    normalized = _normalize_key(value)
    return "forward" in normalized or "foward" in normalized


def _is_passed(value: Any) -> bool:
    normalized = _normalize_key(value)
    return normalized in {"passed", "pass", "true", "1", "ok", "accepted", "naturalpassed"}


def _has_forced_pass(row: Mapping[str, Any]) -> bool:
    joined = " ".join(_text(row.get(key)) for key in row)
    normalized = _normalize_key(joined)
    return any(marker in normalized for marker in (
        "forcedpass",
        "forcepass",
        "manualpass",
        "syntheticpass",
        "overridepass",
        "fabricatedpass",
        "simulatedpass",
        "resultspassedfabricado",
    ))


def _forward_contract(row: Mapping[str, Any]) -> dict[str, Any]:
    phase = _value(row, ("sourcePhase", "Source Phase", "phase", "Phase"), "")
    source = _value(row, (
        "forwardSource",
        "Forward Source",
        "Foward Source",
        "sourceDatabank",
        "Source Databank",
        "Databank",
        "Result Databank",
        "Output",
        "Stage",
        "Test",
    ), "")
    status = _value(row, ("forwardStatus", "Forward Status", "Filters result", "status", "Status", "result", "Result", "passed", "Passed"), "")
    sample = any(_bool_marker(_value(row, aliases, "")) for aliases in (
        ("Example Only", "exampleOnly"),
        ("Sample Only", "sampleOnly"),
        ("Demo Only", "demoOnly"),
    ))
    issues: list[str] = []
    if phase and _normalize_key(phase) != "phase28capa2forward":
        issues.append("sourcePhase != phase28_capa2_forward")
    if not _is_forward_source(source):
        issues.append("sourceDatabank != Forward/Foward")
    if not _is_passed(status):
        issues.append("status != PASSED natural")
    if sample:
        issues.append("sample/example row rejected")
    if _has_forced_pass(row):
        issues.append("forced/synthetic pass rejected")
    return {
        "ok": not issues,
        "issues": issues,
        "source": _text(source, "Foward"),
        "status": _text(status),
    }


def _score(row: Mapping[str, Any]) -> float:
    pf = min(2.4, max(0.0, _numeric(_value(row, ("profitFactor", "Profit Factor", "PF"), 0))))
    ret_dd = min(10.0, max(0.0, _numeric(_value(row, ("retDd", "Ret/DD Ratio", "Return / Drawdown ratio"), 0))))
    drawdown = max(0.0, 100.0 - min(100.0, _numeric(_value(row, ("maxDd", "Max DD %", "Max Drawdown %"), 100))))
    trades = min(500.0, max(0.0, _numeric(_value(row, ("trades", "Number of trades", "# of trades"), 0))))
    stability = min(1.0, max(0.0, _numeric(_value(row, ("stability", "Stability"), 0))))
    sqn = min(5.0, max(0.0, _numeric(_value(row, ("SQN", "sqn"), 0))))
    return round((pf * 22) + (ret_dd * 7) + (drawdown * 0.26) + (trades * 0.045) + (stability * 16) + (sqn * 3), 2)


def _similarity(a: Mapping[str, Any], b: Mapping[str, Any]) -> float:
    score = 0.0
    weights = (
        ("asset", 0.28),
        ("timeframe", 0.18),
        ("blockSetting", 0.22),
        ("indicator", 0.20),
        ("cluster", 0.12),
    )
    for key, weight in weights:
        if _normalize_key(a.get(key)) and _normalize_key(a.get(key)) == _normalize_key(b.get(key)):
            score += weight
    pf_gap = abs(float(a.get("profitFactor") or 0) - float(b.get("profitFactor") or 0))
    ret_gap = abs(float(a.get("retDd") or 0) - float(b.get("retDd") or 0))
    dd_gap = abs(float(a.get("maxDd") or 100) - float(b.get("maxDd") or 100))
    if pf_gap < 0.15:
        score += 0.08
    if ret_gap < 0.8:
        score += 0.06
    if dd_gap < 4:
        score += 0.06
    return min(1.0, score)


def _settings(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    result = dict(DEFAULT_SETTINGS)
    for key, value in (raw or {}).items():
        if key not in result:
            continue
        if key == "period":
            result[key] = _text(value, "Day")[:20]
        elif key in {"minComparablePoints", "maxWinners"}:
            result[key] = max(1, int(_numeric(value, result[key])))
        else:
            result[key] = round(max(0.0, min(1.0, _numeric(value, result[key]))), 4)
    return result


def parse_correlation_input(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, str):
        try:
            dialect = csv.Sniffer().sniff(payload[:2048], delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        return list(csv.DictReader(io.StringIO(payload), dialect=dialect))
    if isinstance(payload, Mapping):
        for key in ("rows", "items", "candidates"):
            rows = payload.get(key)
            if isinstance(rows, list):
                return [dict(item) for item in rows if isinstance(item, Mapping)]
        lab = payload.get("portfolioLab")
        if isinstance(lab, Mapping):
            return parse_correlation_input(lab)
        csv_text = payload.get("csv")
        if isinstance(csv_text, str):
            return parse_correlation_input(csv_text)
    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, Mapping)]
    return []


def _candidate(row: Mapping[str, Any], index: int) -> tuple[dict[str, Any], int]:
    clean_row, redactions = _redact_mapping(row)
    identity = _value(row, ("strategy", "name", "Strategy Name", "id"), f"candidate-{index + 1}")
    asset, r_asset = _redact_text(_value(row, ("asset", "symbol", "Symbol", "Market"), "GENERIC"), "GENERIC")
    timeframe, r_tf = _redact_text(_value(row, ("timeframe", "tf", "TimeFrame", "Time frame"), "H1"), "H1")
    block, r_block = _redact_text(_value(row, ("blockSetting", "BlockSetting", "bs", "Block Setting"), "BS_Custom"), "BS_Custom")
    indicator, r_indicator = _redact_text(_value(row, ("indicator", "Indicator", "Indicador", "Base Indicator", "Entry indicators", "Entry Indicators"), "SIN_INDICADOR"), "SIN_INDICADOR")
    cluster, r_cluster = _redact_text(_value(row, ("cluster", "clusterId", "NumCluster", "Cluster"), ""), "")
    redactions += sum(int(flag) for flag in (r_asset, r_tf, r_block, r_indicator, r_cluster))
    contract = _forward_contract(row)
    series = _return_series(row)
    item = {
        "candidateId": _hash_id("candidate", f"{index}|{_text(identity)}|{asset}|{timeframe}|{block}|{indicator}"),
        "sourceIndex": index,
        "strategyRef": _hash_id("strategy", _text(identity, f"candidate-{index + 1}")),
        "score": _score(row),
        "asset": asset.upper() or "GENERIC",
        "timeframe": timeframe.upper() or "H1",
        "blockSetting": block or "BS_Custom",
        "indicator": indicator or "SIN_INDICADOR",
        "cluster": cluster,
        "profitFactor": round(_numeric(_value(row, ("profitFactor", "Profit Factor", "PF"), 0)), 2),
        "retDd": round(_numeric(_value(row, ("retDd", "Ret/DD Ratio"), 0)), 2),
        "maxDd": round(_numeric(_value(row, ("maxDd", "Max DD %"), 100)), 2),
        "trades": int(_numeric(_value(row, ("trades", "Number of trades", "# of trades"), 0))),
        "returnSeries": series[:240],
        "forwardContract": contract,
        "cleanInput": clean_row,
    }
    return item, redactions


def build_correlation_filter_report(payload: Any, settings: Mapping[str, Any] | None = None) -> dict[str, Any]:
    cfg = _settings(settings)
    rows = parse_correlation_input(payload)
    candidates: list[dict[str, Any]] = []
    redactions = 0
    for index, row in enumerate(rows):
        candidate, count = _candidate(row, index)
        candidates.append(candidate)
        redactions += count
    candidates.sort(key=lambda item: (-float(item["score"]), int(item["sourceIndex"])))

    winners: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    comparable_pairs = 0
    portfolio_rank = 0
    for candidate in candidates:
        reasons: list[str] = []
        nearest_winner: dict[str, Any] | None = None
        max_corr: float | None = None
        correlation_status = "similarity_only"
        series = candidate["returnSeries"]
        has_series = len(series) >= int(cfg["minComparablePoints"])

        if not candidate["forwardContract"]["ok"]:
            reasons.extend(candidate["forwardContract"]["issues"])

        best_similarity = 0.0
        for winner in winners:
            sim = _similarity(candidate, winner)
            if sim > best_similarity:
                best_similarity = sim
                nearest_winner = winner
            winner_series = winner["returnSeries"]
            if has_series and len(winner_series) >= int(cfg["minComparablePoints"]):
                if len(series) == len(winner_series):
                    corr = _pearson(series, winner_series)
                    if corr is not None:
                        comparable_pairs += 1
                        correlation_status = "available"
                        if max_corr is None or corr > max_corr:
                            max_corr = corr
                            nearest_winner = winner
                else:
                    correlation_status = "not_comparable"

        if has_series and winners and correlation_status == "similarity_only":
            correlation_status = "not_comparable"
        if not has_series and series:
            correlation_status = "not_comparable"

        if not reasons and max_corr is not None and max_corr >= float(cfg["maxCorrelation"]):
            reasons.append(f"correlation >= {cfg['maxCorrelation']}")
        if not reasons and max_corr is None and nearest_winner and best_similarity >= float(cfg["similarityThreshold"]):
            reasons.append(f"operational similarity >= {cfg['similarityThreshold']}")
        if not reasons and correlation_status == "not_comparable":
            reasons.append("series not comparable")
        if not reasons and len(winners) >= int(cfg["maxWinners"]):
            reasons.append("max winners reached")

        if reasons and not candidate["forwardContract"]["ok"]:
            decision = "review"
        elif reasons and any(reason.startswith(("correlation", "operational similarity", "max winners")) for reason in reasons):
            decision = "similar"
        elif reasons:
            decision = "review"
        else:
            decision = "portfolio"
            winners.append(candidate)
            portfolio_rank += 1

        if decision != "portfolio" and not nearest_winner and winners:
            nearest_winner = winners[0]
        item = {
            "strategyRef": candidate["strategyRef"],
            "candidateId": candidate["candidateId"],
            "decision": decision,
            "c2TemplateDecision": "c2_template_winner" if decision == "portfolio" else ("c2_template_similar" if decision == "similar" else "c2_template_review"),
            "decisionDomain": "capa1_c2_template_selection_alias",
            "reason": " · ".join(reasons) if reasons else "accepted by external correlation filter",
            "score": candidate["score"],
            "maxObservedCorrelation": round(max_corr, 4) if max_corr is not None else None,
            "correlationStatus": correlation_status,
            "nearestWinnerId": nearest_winner["candidateId"] if nearest_winner else "",
            "portfolioRank": portfolio_rank if decision == "portfolio" else None,
            "c2TemplateRank": portfolio_rank if decision == "portfolio" else None,
            "trace": {
                "asset": candidate["asset"],
                "timeframe": candidate["timeframe"],
                "BlockSetting": candidate["blockSetting"],
                "indicator": candidate["indicator"],
                "cluster": candidate["cluster"],
            },
            "forwardContract": {
                "ok": candidate["forwardContract"]["ok"],
                "issues": list(candidate["forwardContract"]["issues"]),
            },
        }
        items.append(item)

    summary = {
        "inputRows": len(rows),
        "eligibleRows": sum(1 for item in items if item["forwardContract"]["ok"]),
        "portfolio": sum(1 for item in items if item["decision"] == "portfolio"),
        "c2TemplateWinners": sum(1 for item in items if item["decision"] == "portfolio"),
        "similar": sum(1 for item in items if item["decision"] == "similar"),
        "review": sum(1 for item in items if item["decision"] == "review"),
        "comparablePairs": comparable_pairs,
        "similarityOnly": sum(1 for item in items if item["correlationStatus"] == "similarity_only"),
        "notComparable": sum(1 for item in items if item["correlationStatus"] == "not_comparable"),
        "redactedFields": redactions,
    }
    return {
        "ok": True,
        "version": CORRELATION_FILTER_EXTERNAL_VERSION,
        "mode": "external_readonly",
        "source": "portfolio_lab_phase29",
        "decisionDomainAliases": ["capa1_c2_template_selection", "capa2_portfolio_selection"],
        "analyzedAt": _now_iso(),
        "settings": cfg,
        "summary": summary,
        "items": items,
        "privacy": {
            "local_paths_returned": False,
            "raw_strategy_names_returned": False,
            "private_fields_returned": False,
            "tokens_returned": False,
        },
        "blockers": [],
    }


def export_correlation_filter_csv(report: Mapping[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "candidateId",
            "decision",
            "reason",
            "maxObservedCorrelation",
            "correlationStatus",
            "nearestWinnerId",
            "asset",
            "timeframe",
            "BlockSetting",
            "indicator",
            "cluster",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    for item in report.get("items", []):
        trace = item.get("trace", {}) if isinstance(item, Mapping) else {}
        writer.writerow({
            "candidateId": item.get("candidateId", ""),
            "decision": item.get("decision", ""),
            "reason": item.get("reason", ""),
            "maxObservedCorrelation": item.get("maxObservedCorrelation", ""),
            "correlationStatus": item.get("correlationStatus", ""),
            "nearestWinnerId": item.get("nearestWinnerId", ""),
            "asset": trace.get("asset", ""),
            "timeframe": trace.get("timeframe", ""),
            "BlockSetting": trace.get("BlockSetting", ""),
            "indicator": trace.get("indicator", ""),
            "cluster": trace.get("cluster", ""),
        })
    return output.getvalue()


def export_correlation_filter_sqx_tag_csv(report: Mapping[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "strategyRef",
            "candidateId",
            "decision",
            "reason",
            "score",
            "maxObservedCorrelation",
            "correlationStatus",
            "nearestWinnerId",
            "portfolioRank",
            "c2TemplateRank",
            "decisionDomain",
            "generatedAt",
            "version",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    generated_at = _text(report.get("analyzedAt"))
    version = _text(report.get("version"), CORRELATION_FILTER_EXTERNAL_VERSION)
    for item in report.get("items", []):
        if not isinstance(item, Mapping):
            continue
        writer.writerow({
            "strategyRef": item.get("strategyRef", ""),
            "candidateId": item.get("candidateId", ""),
            "decision": item.get("decision", ""),
            "reason": item.get("reason", ""),
            "score": item.get("score", ""),
            "maxObservedCorrelation": item.get("maxObservedCorrelation", ""),
            "correlationStatus": item.get("correlationStatus", ""),
            "nearestWinnerId": item.get("nearestWinnerId", ""),
            "portfolioRank": item.get("portfolioRank") or "",
            "c2TemplateRank": item.get("c2TemplateRank") or "",
            "decisionDomain": item.get("decisionDomain", ""),
            "generatedAt": generated_at,
            "version": version,
        })
    return output.getvalue()
