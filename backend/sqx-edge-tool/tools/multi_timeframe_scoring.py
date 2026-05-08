"""
Controlled multi-timeframe scoring for SQX Edge.

This tool turns precomputed asset metric JSON files into dashboard-like scores
per timeframe, then builds a weighted consensus. It deliberately does not
download market data, inject HTML, or require pandas/numpy at runtime.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
CONFIG_DIR = TOOL_ROOT / "config"

DEFAULT_TIMEFRAMES = ("H1", "M30", "M15", "H4")
DEFAULT_WEIGHTS = {"H1": 0.45, "M30": 0.25, "M15": 0.20, "H4": 0.10}


def ou_metric(tf: str) -> str:
    return f"ou_half_life_{normalize_tf(tf).lower()}"


def category_metrics_for(tf: str) -> dict[str, list[tuple[str, bool]]]:
    """Return metric definitions as (metric_name, higher_is_better)."""
    return {
        "tendencia": [
            ("adx_mean", True),
            ("trend_efficiency_200", True),
            ("sma200_persistence_bars", True),
        ],
        "momentum": [("rsi_edge_in_atrs", True)],
        "volatilidad": [
            ("atr_pct_mean", True),
            ("vol_of_vol", True),
        ],
        "regimen": [
            ("sma200_persistence_bars", True),
            ("hurst_dist", True),
        ],
        "estadistico": [
            (ou_metric(tf), False),
            ("kurtosis", True),
        ],
        "volumen": [("vwap_rejection_rate", True)],
        "sr": [("round_bounce_rate", True)],
    }


def normalize_tf(tf: str) -> str:
    value = str(tf or "").strip().upper()
    if not value:
        raise ValueError("timeframe cannot be empty")
    return value


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def metric_file_for(metrics_dir: Path, tf: str) -> Path:
    tf = normalize_tf(tf)
    return metrics_dir / ("asset_metrics.json" if tf == "H1" else f"asset_metrics_{tf}.json")


def load_metrics(metrics_dir: Path, timeframes: list[str]) -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for tf in timeframes:
        norm_tf = normalize_tf(tf)
        path = metric_file_for(metrics_dir, norm_tf)
        if path.exists():
            loaded[norm_tf] = read_json(path)
    return loaded


def safe_number(value: Any) -> float | None:
    try:
        if value is None:
            return None
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number:
        return None
    return number


def enriched_metrics(raw_metrics: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for asset, metrics in raw_metrics.items():
        if not isinstance(metrics, dict):
            continue
        item = dict(metrics)
        hurst = safe_number(item.get("hurst"))
        if hurst is not None:
            item["hurst_dist"] = abs(hurst - 0.5)
        elif safe_number(item.get("hurst_dist")) is None:
            item["hurst_dist"] = None
        out[str(asset)] = item
    return out


def percentile_scores(values: dict[str, float], higher_is_better: bool) -> dict[str, float]:
    """Return percentile scores in [0, 1], with ties sharing average rank."""
    clean = {asset: value for asset, value in values.items() if safe_number(value) is not None}
    if not clean:
        return {}
    ordered = sorted(clean.items(), key=lambda pair: pair[1], reverse=not higher_is_better)
    n = len(ordered)
    if n == 1:
        return {ordered[0][0]: 1.0}
    ranks: dict[str, float] = {}
    index = 0
    while index < n:
        value = ordered[index][1]
        end = index
        while end + 1 < n and ordered[end + 1][1] == value:
            end += 1
        avg_rank = ((index + 1) + (end + 1)) / 2
        percentile = avg_rank / n
        for pos in range(index, end + 1):
            ranks[ordered[pos][0]] = round(percentile, 4)
        index = end + 1
    return ranks


def rating_from_score(score: float | None) -> str | None:
    if score is None:
        return None
    if score >= 0.75:
        return "++"
    if score >= 0.50:
        return "+"
    if score >= 0.25:
        return "~"
    return "-"


def score_timeframe(raw_metrics: dict[str, Any], tf: str) -> dict[str, dict[str, Any]]:
    tf = normalize_tf(tf)
    metrics = enriched_metrics(raw_metrics)
    definitions = category_metrics_for(tf)
    output: dict[str, dict[str, Any]] = {
        asset: {
            "metrics": {},
            "subtype": str(values.get("subtype") or values.get("subtype_group") or "unknown"),
            "type": str(values.get("type") or "unknown"),
        }
        for asset, values in metrics.items()
    }

    for category, metric_defs in definitions.items():
        metric_ranks: list[tuple[str, dict[str, float]]] = []
        for metric_name, higher_is_better in metric_defs:
            values = {
                asset: number
                for asset, item in metrics.items()
                if (number := safe_number(item.get(metric_name))) is not None
            }
            ranks = percentile_scores(values, higher_is_better)
            if ranks:
                metric_ranks.append((metric_name, ranks))
        if not metric_ranks:
            continue
        for asset, item in metrics.items():
            available = [ranks[asset] for _metric_name, ranks in metric_ranks if asset in ranks]
            if not available:
                continue
            composite = round(mean(available), 4)
            output[asset][category] = {
                "objective": rating_from_score(composite),
                "composite_score": composite,
                "metric_count": len(available),
                "scope": "global",
            }
            output[asset]["metrics"][category] = {
                metric_name: item.get(metric_name)
                for metric_name, _ranks in metric_ranks
                if item.get(metric_name) is not None
            }
    return output


def normalize_weights(timeframes: list[str], weights: dict[str, float] | None = None) -> dict[str, float]:
    source = {normalize_tf(k): float(v) for k, v in (weights or DEFAULT_WEIGHTS).items()}
    selected = {tf: source.get(tf, 1.0) for tf in timeframes}
    total = sum(v for v in selected.values() if v > 0)
    if total <= 0:
        raise ValueError("weights must contain at least one positive value")
    return {tf: round(max(weight, 0) / total, 6) for tf, weight in selected.items()}


def consensus_label(values: list[float]) -> str:
    if not values:
        return "missing"
    if len(values) == 1:
        return "single_tf"
    spread = max(values) - min(values)
    if spread <= 0.15:
        return "stable"
    if spread >= 0.35:
        return "divergent"
    return "mixed"


def build_consensus(
    scores_by_tf: dict[str, dict[str, dict[str, Any]]],
    weights: dict[str, float],
) -> dict[str, dict[str, Any]]:
    assets = sorted({asset for scores in scores_by_tf.values() for asset in scores})
    categories = sorted({cat for scores in scores_by_tf.values() for asset in scores.values() for cat in asset if cat not in {"metrics", "subtype", "type"}})
    consensus: dict[str, dict[str, Any]] = {}
    for asset in assets:
        consensus[asset] = {}
        for category in categories:
            per_tf: dict[str, dict[str, Any]] = {}
            weighted_total = 0.0
            weight_used = 0.0
            raw_values: list[float] = []
            for tf, scores in scores_by_tf.items():
                entry = scores.get(asset, {}).get(category)
                if not isinstance(entry, dict):
                    continue
                composite = safe_number(entry.get("composite_score"))
                if composite is None:
                    continue
                per_tf[tf] = {
                    "composite_score": round(composite, 4),
                    "objective": entry.get("objective"),
                }
                raw_values.append(composite)
                weighted_total += composite * weights.get(tf, 0)
                weight_used += weights.get(tf, 0)
            if not per_tf:
                continue
            weighted = weighted_total / weight_used if weight_used else mean(raw_values)
            best_tf = max(per_tf.items(), key=lambda pair: pair[1]["composite_score"])[0]
            consensus[asset][category] = {
                "weighted_composite": round(weighted, 4),
                "objective": rating_from_score(weighted),
                "coverage": len(per_tf),
                "consensus": consensus_label(raw_values),
                "best_tf": best_tf,
                "per_tf": per_tf,
            }
    return consensus


def build_report(
    *,
    metrics_by_tf: dict[str, dict[str, Any]] | None = None,
    metrics_dir: Path | None = None,
    timeframes: list[str] | None = None,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    requested_tfs = [normalize_tf(tf) for tf in (timeframes or list(DEFAULT_TIMEFRAMES))]
    raw_by_tf = metrics_by_tf if metrics_by_tf is not None else load_metrics(metrics_dir or Path("analysis_output"), requested_tfs)
    raw_by_tf = {normalize_tf(tf): data for tf, data in raw_by_tf.items() if normalize_tf(tf) in requested_tfs}
    if not raw_by_tf:
        raise FileNotFoundError("No asset_metrics JSON files found for requested timeframes")
    active_tfs = [tf for tf in requested_tfs if tf in raw_by_tf]
    active_weights = normalize_weights(active_tfs, weights)
    scores_by_tf = {tf: score_timeframe(raw_by_tf[tf], tf) for tf in active_tfs}
    consensus = build_consensus(scores_by_tf, active_weights)
    return {
        "metadata": {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "phase": "A49",
            "sourceImprovement": "Controlled multi-timeframe scoring pattern adapted from compared Jose Livan repository",
            "timeframesRequested": requested_tfs,
            "timeframesLoaded": active_tfs,
            "weights": active_weights,
            "assetCount": len({asset for data in raw_by_tf.values() for asset in data}),
            "categoryModel": sorted(category_metrics_for(active_tfs[0]).keys()),
            "caveat": "Scores depend on supplied metric JSON files; this tool does not download market data or update the dashboard UI.",
        },
        "scoresByTimeframe": scores_by_tf,
        "consensus": consensus,
    }


def render_markdown(report: dict[str, Any], top: int = 8) -> str:
    meta = report["metadata"]
    rows: list[tuple[str, str, dict[str, Any]]] = []
    for asset, categories in report["consensus"].items():
        for category, entry in categories.items():
            rows.append((asset, category, entry))
    rows.sort(key=lambda row: (-row[2]["weighted_composite"], row[0], row[1]))
    lines = [
        "# SQX Multi-Timeframe Scoring",
        "",
        f"- Phase: `{meta['phase']}`",
        f"- Loaded TFs: `{', '.join(meta['timeframesLoaded'])}`",
        f"- Assets: `{meta['assetCount']}`",
        f"- Caveat: {meta['caveat']}",
        "",
        "## Top Consensus",
        "",
        "| Rank | Asset | Category | Weighted | Rating | Coverage | Consensus | Best TF |",
        "| ---: | --- | --- | ---: | --- | ---: | --- | --- |",
    ]
    for rank, (asset, category, entry) in enumerate(rows[:top], 1):
        lines.append(
            f"| {rank} | {asset} | {category} | {entry['weighted_composite']:.3f} | "
            f"{entry['objective']} | {entry['coverage']} | {entry['consensus']} | {entry['best_tf']} |"
        )
    return "\n".join(lines) + "\n"


def parse_weights(raw: str | None) -> dict[str, float] | None:
    if not raw:
        return None
    out: dict[str, float] = {}
    for part in raw.split(","):
        if not part.strip():
            continue
        key, value = part.split("=", 1)
        out[normalize_tf(key)] = float(value)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Score SQX asset metrics across multiple timeframes.")
    parser.add_argument("--metrics-dir", default=str(PROJECT_ROOT / "analysis_output"))
    parser.add_argument("--tf", default=",".join(DEFAULT_TIMEFRAMES), help="Comma-separated TF list.")
    parser.add_argument("--weights", help="Optional weights, e.g. H1=0.5,M30=0.3,M15=0.2")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    parser.add_argument("--out", help="Optional output path.")
    parser.add_argument("--top", type=int, default=8)
    args = parser.parse_args()

    report = build_report(
        metrics_dir=Path(args.metrics_dir),
        timeframes=[normalize_tf(part) for part in args.tf.split(",") if part.strip()],
        weights=parse_weights(args.weights),
    )
    text = json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_markdown(report, top=args.top)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
