"""
Validation gate for first-party multi-timeframe metric files.

A51 keeps multi-timeframe evidence out of the dashboard until the metric JSON
files are traceable, complete enough and scorer-compatible.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
CONFIG_DIR = TOOL_ROOT / "config"

DEFAULT_TIMEFRAMES = ("H1", "M30", "M15", "H4")
DEFAULT_MIN_ASSET_COVERAGE = 0.80
DEFAULT_MIN_METRIC_COMPLETENESS = 0.75


def load_multi_timeframe_scoring():
    path = Path(__file__).with_name("multi_timeframe_scoring.py")
    spec = importlib.util.spec_from_file_location("multi_timeframe_scoring", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def expected_assets_from_manifest(path: Path = CONFIG_DIR / "assets.json") -> set[str]:
    data = read_json(path)
    return {str(asset["id"]) for asset in data.get("assets", []) if asset.get("id")}


def normalize_tf(tf: str) -> str:
    return str(tf or "").strip().upper()


def metric_file_for(metrics_dir: Path, tf: str) -> Path:
    tf = normalize_tf(tf)
    return metrics_dir / ("asset_metrics.json" if tf == "H1" else f"asset_metrics_{tf}.json")


def required_metrics_for_tf(tf: str) -> set[str]:
    scoring = load_multi_timeframe_scoring()
    required: set[str] = set()
    for definitions in scoring.category_metrics_for(tf).values():
        for metric_name, _higher_is_better in definitions:
            required.add("hurst" if metric_name == "hurst_dist" else metric_name)
    return required


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


def validate_payload(
    payload: dict[str, Any],
    *,
    tf: str,
    expected_assets: set[str],
) -> dict[str, Any]:
    required_metrics = required_metrics_for_tf(tf)
    known = sorted(asset for asset in payload if asset in expected_assets)
    unknown = sorted(asset for asset in payload if asset not in expected_assets)
    missing_assets = sorted(expected_assets - set(payload))
    metric_slots = max(1, len(known) * len(required_metrics))
    missing_metric_cells: list[dict[str, str]] = []
    present_metric_cells = 0

    for asset in known:
        values = payload.get(asset) or {}
        for metric in sorted(required_metrics):
            if safe_number(values.get(metric)) is None:
                missing_metric_cells.append({"asset": asset, "metric": metric})
            else:
                present_metric_cells += 1

    asset_coverage = len(known) / max(1, len(expected_assets))
    metric_completeness = present_metric_cells / metric_slots
    return {
        "tf": normalize_tf(tf),
        "assetCount": len(payload),
        "knownAssetCount": len(known),
        "unknownAssetCount": len(unknown),
        "expectedAssetCount": len(expected_assets),
        "assetCoverage": round(asset_coverage, 4),
        "metricCompleteness": round(metric_completeness, 4),
        "requiredMetricCount": len(required_metrics),
        "unknownAssets": unknown,
        "missingAssets": missing_assets,
        "missingMetricCells": missing_metric_cells[:50],
        "missingMetricCellCount": len(missing_metric_cells),
    }


def build_gate_report(
    *,
    metrics_dir: Path,
    timeframes: list[str] | None = None,
    expected_assets: set[str] | None = None,
    min_asset_coverage: float = DEFAULT_MIN_ASSET_COVERAGE,
    min_metric_completeness: float = DEFAULT_MIN_METRIC_COMPLETENESS,
) -> dict[str, Any]:
    tfs = [normalize_tf(tf) for tf in (timeframes or list(DEFAULT_TIMEFRAMES)) if normalize_tf(tf)]
    expected = expected_assets or expected_assets_from_manifest()
    files: list[dict[str, Any]] = []
    failures: list[str] = []
    metrics_by_tf: dict[str, dict[str, Any]] = {}

    for tf in tfs:
        path = metric_file_for(metrics_dir, tf)
        if not path.exists():
            failures.append(f"missing metric file for {tf}: {path.name}")
            files.append({"tf": tf, "path": str(path), "exists": False})
            continue
        payload = read_json(path)
        if not isinstance(payload, dict):
            failures.append(f"invalid JSON shape for {tf}: expected object")
            files.append({"tf": tf, "path": str(path), "exists": True, "sha256": sha256(path), "valid": False})
            continue
        validation = validate_payload(payload, tf=tf, expected_assets=expected)
        if validation["assetCoverage"] < min_asset_coverage:
            failures.append(f"{tf} asset coverage {validation['assetCoverage']:.2%} below {min_asset_coverage:.0%}")
        if validation["metricCompleteness"] < min_metric_completeness:
            failures.append(
                f"{tf} metric completeness {validation['metricCompleteness']:.2%} below {min_metric_completeness:.0%}"
            )
        if validation["unknownAssetCount"]:
            failures.append(f"{tf} has {validation['unknownAssetCount']} unknown assets")
        metrics_by_tf[tf] = payload
        files.append(
            {
                "tf": tf,
                "path": str(path),
                "exists": True,
                "valid": True,
                "sha256": sha256(path),
                "sizeBytes": path.stat().st_size,
                **validation,
            }
        )

    scoring_summary = None
    if metrics_by_tf:
        scoring = load_multi_timeframe_scoring()
        scoring_report = scoring.build_report(metrics_by_tf=metrics_by_tf, timeframes=tfs)
        scoring_summary = {
            "timeframesLoaded": scoring_report["metadata"]["timeframesLoaded"],
            "assetCount": scoring_report["metadata"]["assetCount"],
            "consensusAssetCount": len(scoring_report["consensus"]),
            "categoryModel": scoring_report["metadata"]["categoryModel"],
        }

    status = "GO" if not failures and len(metrics_by_tf) == len(tfs) else "NO_GO"
    return {
        "metadata": {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "phase": "A51",
            "metricsDir": str(metrics_dir),
            "timeframesRequested": tfs,
            "minAssetCoverage": min_asset_coverage,
            "minMetricCompleteness": min_metric_completeness,
            "expectedAssetCount": len(expected),
            "caveat": "This gate validates supplied metric JSON files; it does not download market data or modify dashboard scores.",
        },
        "status": status,
        "failures": failures,
        "files": files,
        "scoringSummary": scoring_summary,
    }


def render_markdown(report: dict[str, Any]) -> str:
    meta = report["metadata"]
    lines = [
        "# SQX Multi-Timeframe Metric Gate",
        "",
        f"- Phase: `{meta['phase']}`",
        f"- Status: `{report['status']}`",
        f"- Metrics dir: `{meta['metricsDir']}`",
        f"- Timeframes: `{', '.join(meta['timeframesRequested'])}`",
        f"- Caveat: {meta['caveat']}",
        "",
        "## Files",
        "",
        "| TF | Exists | Asset Coverage | Metric Completeness | Unknown Assets | SHA256 |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for item in report["files"]:
        lines.append(
            "| {tf} | {exists} | {coverage} | {complete} | {unknown} | {sha} |".format(
                tf=item["tf"],
                exists="yes" if item.get("exists") else "no",
                coverage="-" if not item.get("exists") else f"{item.get('assetCoverage', 0):.1%}",
                complete="-" if not item.get("exists") else f"{item.get('metricCompleteness', 0):.1%}",
                unknown=item.get("unknownAssetCount", "-"),
                sha=(item.get("sha256") or "-")[:16],
            )
        )
    if report["failures"]:
        lines += ["", "## Failures", ""]
        lines.extend(f"- {failure}" for failure in report["failures"])
    if report.get("scoringSummary"):
        summary = report["scoringSummary"]
        lines += [
            "",
            "## Scoring Compatibility",
            "",
            f"- Loaded TFs: `{', '.join(summary['timeframesLoaded'])}`",
            f"- Assets scored: `{summary['assetCount']}`",
            f"- Consensus assets: `{summary['consensusAssetCount']}`",
        ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate first-party multi-timeframe metric JSON files.")
    parser.add_argument("--metrics-dir", required=True)
    parser.add_argument("--tf", default=",".join(DEFAULT_TIMEFRAMES), help="Comma-separated TF list.")
    parser.add_argument("--min-asset-coverage", type=float, default=DEFAULT_MIN_ASSET_COVERAGE)
    parser.add_argument("--min-metric-completeness", type=float, default=DEFAULT_MIN_METRIC_COMPLETENESS)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out", help="Optional output path.")
    args = parser.parse_args()

    report = build_gate_report(
        metrics_dir=Path(args.metrics_dir),
        timeframes=[part for part in args.tf.split(",") if part.strip()],
        min_asset_coverage=args.min_asset_coverage,
        min_metric_completeness=args.min_metric_completeness,
    )
    text = json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_markdown(report)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0 if report["status"] == "GO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
