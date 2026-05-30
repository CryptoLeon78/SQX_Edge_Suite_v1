from __future__ import annotations

import csv
import hashlib
import io
import math
import re
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence


MONTE_CARLO_BENCHMARKS_VERSION = "sqx142-monte-carlo-candidate-benchmarks-v1"

DEFAULT_SETTINGS = {
    "simulations": 64,
    "seed": "sqx142-mc-benchmark-v1",
    "minComparablePoints": 12,
    "blockSize": 4,
    "parameterJitterPct": 0.15,
    "executionDegradeBps": 2.0,
    "minSurvivalRate": 0.70,
    "maxMedianDrawdownPct": 35.0,
}

DEFAULT_METHODS = (
    "MACHRBlockRandomization",
    "SimulateParameterJitter",
    "RandomlyDegradeExecution",
)

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
    values: list[float] = []
    for part in re.split(r"[\s|;]+", text):
        if not part:
            continue
        parsed = _numeric(part, math.nan)
        if math.isfinite(parsed):
            values.append(parsed / 100.0 if "%" in part else parsed)
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


def _settings(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    result = dict(DEFAULT_SETTINGS)
    for key, value in (raw or {}).items():
        if key not in result:
            continue
        if key == "seed":
            result[key] = _text(value, str(result[key]))[:80]
        elif key in {"simulations", "minComparablePoints", "blockSize"}:
            upper = 512 if key == "simulations" else 240
            result[key] = max(1, min(upper, int(_numeric(value, result[key]))))
        elif key in {"parameterJitterPct", "minSurvivalRate"}:
            result[key] = round(max(0.0, min(1.0, _numeric(value, result[key]))), 4)
        elif key in {"executionDegradeBps", "maxMedianDrawdownPct"}:
            result[key] = round(max(0.0, min(1000.0, _numeric(value, result[key]))), 4)
    return result


def parse_monte_carlo_input(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, str):
        return list(csv.DictReader(io.StringIO(payload)))
    if isinstance(payload, Mapping):
        for key in ("rows", "items", "candidates"):
            rows = payload.get(key)
            if isinstance(rows, list):
                return [dict(item) for item in rows if isinstance(item, Mapping)]
        lab = payload.get("portfolioLab")
        if isinstance(lab, Mapping):
            return parse_monte_carlo_input(lab)
        csv_text = payload.get("csv")
        if isinstance(csv_text, str):
            return parse_monte_carlo_input(csv_text)
    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, Mapping)]
    return []


def _unit_float(seed: str, method: str, simulation: int, index: int) -> float:
    digest = hashlib.sha256(f"{seed}|{method}|{simulation}|{index}".encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(0xFFFFFFFFFFFF)


def _machr_block_randomization(series: Sequence[float], simulation: int, cfg: Mapping[str, Any]) -> list[float]:
    block_size = max(1, int(cfg["blockSize"]))
    blocks = [list(series[index:index + block_size]) for index in range(0, len(series), block_size)]
    keyed = sorted(
        enumerate(blocks),
        key=lambda item: _unit_float(str(cfg["seed"]), "MACHRBlockRandomization", simulation, item[0]),
    )
    return [value for _index, block in keyed for value in block]


def _simulate_parameter_jitter(series: Sequence[float], simulation: int, cfg: Mapping[str, Any]) -> list[float]:
    jitter = float(cfg["parameterJitterPct"])
    return [
        value * (1.0 + ((_unit_float(str(cfg["seed"]), "SimulateParameterJitter", simulation, index) * 2.0) - 1.0) * jitter)
        for index, value in enumerate(series)
    ]


def _randomly_degrade_execution(series: Sequence[float], simulation: int, cfg: Mapping[str, Any]) -> list[float]:
    base_penalty = float(cfg["executionDegradeBps"]) / 10000.0
    return [
        value - (base_penalty * (0.5 + _unit_float(str(cfg["seed"]), "RandomlyDegradeExecution", simulation, index)))
        for index, value in enumerate(series)
    ]


def _perturb(series: Sequence[float], method: str, simulation: int, cfg: Mapping[str, Any]) -> list[float]:
    if method == "MACHRBlockRandomization":
        return _machr_block_randomization(series, simulation, cfg)
    if method == "SimulateParameterJitter":
        return _simulate_parameter_jitter(series, simulation, cfg)
    if method == "RandomlyDegradeExecution":
        return _randomly_degrade_execution(series, simulation, cfg)
    return list(series)


def _cumulative_return_pct(series: Sequence[float]) -> float:
    equity = 1.0
    for value in series:
        equity *= max(0.0, 1.0 + value)
    return (equity - 1.0) * 100.0


def _max_drawdown_pct(series: Sequence[float]) -> float:
    equity = 1.0
    peak = 1.0
    max_dd = 0.0
    for value in series:
        equity *= max(0.0, 1.0 + value)
        peak = max(peak, equity)
        if peak:
            max_dd = max(max_dd, (peak - equity) / peak)
    return max_dd * 100.0


def _median(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def _percentile(values: Sequence[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(math.floor((len(ordered) - 1) * pct))))
    return ordered[index]


def _method_result(series: Sequence[float], method: str, cfg: Mapping[str, Any]) -> dict[str, Any]:
    returns: list[float] = []
    drawdowns: list[float] = []
    simulations = int(cfg["simulations"])
    for simulation in range(simulations):
        perturbed = _perturb(series, method, simulation, cfg)
        returns.append(_cumulative_return_pct(perturbed))
        drawdowns.append(_max_drawdown_pct(perturbed))
    survival_rate = sum(1 for value in returns if value > 0.0) / simulations if simulations else 0.0
    median_dd = _median(drawdowns)
    p05_return = _percentile(returns, 0.05)
    status = "pass"
    if survival_rate < float(cfg["minSurvivalRate"]) or median_dd > float(cfg["maxMedianDrawdownPct"]):
        status = "fail"
    elif p05_return <= 0.0:
        status = "warn"
    return {
        "method": method,
        "simulations": simulations,
        "medianReturnPct": round(_median(returns), 4),
        "p05ReturnPct": round(p05_return, 4),
        "medianDrawdownPct": round(median_dd, 4),
        "maxDrawdownPct": round(max(drawdowns) if drawdowns else 0.0, 4),
        "survivalRate": round(survival_rate, 4),
        "status": status,
    }


def _has_marker(row: Mapping[str, Any], markers: Iterable[str]) -> bool:
    joined = " ".join(f"{_text(key)} {_text(row.get(key))}" for key in row)
    normalized = _normalize_key(joined)
    return any(marker in normalized for marker in markers)


def _candidate_trace(row: Mapping[str, Any]) -> dict[str, str]:
    asset, _ = _redact_text(_value(row, ("asset", "symbol", "Symbol", "Market"), "GENERIC"), "GENERIC")
    timeframe, _ = _redact_text(_value(row, ("timeframe", "tf", "TimeFrame", "Time frame"), "H1"), "H1")
    block, _ = _redact_text(_value(row, ("blockSetting", "BlockSetting", "bs", "Block Setting"), "BS_Custom"), "BS_Custom")
    return {
        "asset": asset.upper() or "GENERIC",
        "timeframe": timeframe.upper() or "H1",
        "BlockSetting": block or "BS_Custom",
    }


def _methods(raw: Any) -> list[str]:
    if not isinstance(raw, (list, tuple)):
        return list(DEFAULT_METHODS)
    selected = [_text(item) for item in raw]
    allowed = [method for method in DEFAULT_METHODS if method in selected]
    return allowed or list(DEFAULT_METHODS)


def build_monte_carlo_benchmark_report(payload: Any, settings: Mapping[str, Any] | None = None) -> dict[str, Any]:
    cfg = _settings(settings)
    methods = _methods(settings.get("methods") if isinstance(settings, Mapping) else None)
    rows = parse_monte_carlo_input(payload)
    items: list[dict[str, Any]] = []
    redactions = 0
    sample_blocked = 0

    for index, row in enumerate(rows):
        _clean_row, count = _redact_mapping(row)
        redactions += count
        identity = _value(row, ("strategy", "name", "Strategy Name", "id"), f"candidate-{index + 1}")
        trace = _candidate_trace(row)
        series = _return_series(row)[:240]
        blockers: list[str] = []
        warnings: list[str] = []

        if _has_marker(row, ("exampleonly", "sampleonly", "demoonly")):
            blockers.append("sample/example row rejected")
            sample_blocked += 1
        if _has_marker(row, ("forcedpass", "forcepass", "manualpass", "syntheticpass", "overridepass", "fabricatedpass", "simulatedpass")):
            blockers.append("forced/manual/synthetic/fabricated pass rejected")

        if len(series) < int(cfg["minComparablePoints"]):
            warnings.append("not_enough_series")

        base_return = _cumulative_return_pct(series) if series else 0.0
        base_drawdown = _max_drawdown_pct(series) if series else 0.0
        method_results: list[dict[str, Any]] = []
        if not blockers and len(series) >= int(cfg["minComparablePoints"]):
            method_results = [_method_result(series, method, cfg) for method in methods]

        statuses = {result["status"] for result in method_results}
        if blockers:
            decision = "benchmark_review"
        elif not method_results:
            decision = "benchmark_review"
        elif "fail" in statuses:
            decision = "benchmark_fail"
        elif "warn" in statuses:
            decision = "benchmark_review"
        else:
            decision = "benchmark_pass"

        items.append({
            "candidateId": _hash_id("candidate", f"{index}|{_text(identity)}|{trace['asset']}|{trace['timeframe']}|{trace['BlockSetting']}"),
            "sourceIndex": index,
            "strategyRef": _hash_id("strategy", _text(identity, f"candidate-{index + 1}")),
            "decision": decision,
            "reason": " · ".join(blockers + warnings) if blockers or warnings else "accepted by external Monte Carlo candidate benchmarks",
            "base": {
                "points": len(series),
                "cumulativeReturnPct": round(base_return, 4),
                "maxDrawdownPct": round(base_drawdown, 4),
            },
            "benchmarks": method_results,
            "trace": trace,
            "blockers": blockers,
            "warnings": warnings,
        })

    summary = {
        "inputRows": len(rows),
        "evaluatedRows": sum(1 for item in items if item["benchmarks"]),
        "benchmarkPass": sum(1 for item in items if item["decision"] == "benchmark_pass"),
        "benchmarkReview": sum(1 for item in items if item["decision"] == "benchmark_review"),
        "benchmarkFail": sum(1 for item in items if item["decision"] == "benchmark_fail"),
        "sampleBlocked": sample_blocked,
        "redactedFields": redactions,
    }
    return {
        "ok": True,
        "version": MONTE_CARLO_BENCHMARKS_VERSION,
        "mode": "external_readonly",
        "source": "portfolio_lab_phase29",
        "analyzedAt": _now_iso(),
        "settings": {**cfg, "methods": methods},
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


def export_monte_carlo_benchmark_csv(report: Mapping[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "candidateId",
            "decision",
            "reason",
            "points",
            "baseCumulativeReturnPct",
            "baseMaxDrawdownPct",
            "methods",
            "methodStatuses",
            "asset",
            "timeframe",
            "BlockSetting",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    for item in report.get("items", []):
        if not isinstance(item, Mapping):
            continue
        base = item.get("base", {}) if isinstance(item.get("base"), Mapping) else {}
        trace = item.get("trace", {}) if isinstance(item.get("trace"), Mapping) else {}
        benchmarks = item.get("benchmarks", []) if isinstance(item.get("benchmarks"), list) else []
        writer.writerow({
            "candidateId": item.get("candidateId", ""),
            "decision": item.get("decision", ""),
            "reason": item.get("reason", ""),
            "points": base.get("points", ""),
            "baseCumulativeReturnPct": base.get("cumulativeReturnPct", ""),
            "baseMaxDrawdownPct": base.get("maxDrawdownPct", ""),
            "methods": "|".join(str(result.get("method", "")) for result in benchmarks if isinstance(result, Mapping)),
            "methodStatuses": "|".join(str(result.get("status", "")) for result in benchmarks if isinstance(result, Mapping)),
            "asset": trace.get("asset", ""),
            "timeframe": trace.get("timeframe", ""),
            "BlockSetting": trace.get("BlockSetting", ""),
        })
    return output.getvalue()
