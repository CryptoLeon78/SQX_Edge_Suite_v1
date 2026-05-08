"""
Build the first-party H1 metric source used by the MTF tooling.

A52 deliberately starts with the existing dashboard H1 baseline. It writes a
traceable `asset_metrics.json` plus provenance manifest, and can validate the
bundle with the A51 metric gate. It does not invent lower/higher timeframe
metrics.
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
APP_ROOT = PROJECT_ROOT / "app"
CONFIG_DIR = TOOL_ROOT / "config"
DEFAULT_SCORES_PATH = APP_ROOT / "js" / "scores-data.js"
DEFAULT_ASSETS_PATH = CONFIG_DIR / "assets.json"
DEFAULT_OUT_DIR = PROJECT_ROOT / "analysis_output" / "first_party_metrics"

METRIC_CATEGORY_MAP = {
    "tendencia": ("adx_mean", "trend_efficiency_200", "sma200_persistence_bars"),
    "momentum": ("rsi_edge_in_atrs",),
    "volatilidad": ("atr_pct_mean", "vol_of_vol"),
    "regimen": ("sma200_persistence_bars", "hurst_dist"),
    "estadistico": ("ou_half_life_h1", "kurtosis"),
    "volumen": ("vwap_rejection_rate",),
    "sr": ("round_bounce_rate",),
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


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


def extract_assigned_json(text: str, assignment: str = "window.SQX_SCORES_DATA") -> dict[str, Any]:
    start = text.find(assignment)
    if start < 0:
        raise ValueError(f"{assignment} assignment not found")
    brace_start = text.find("{", start)
    if brace_start < 0:
        raise ValueError("JSON object start not found")

    depth = 0
    in_string = False
    escaped = False
    for index in range(brace_start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[brace_start : index + 1])
    raise ValueError("JSON object end not found")


def load_scores(path: Path = DEFAULT_SCORES_PATH) -> dict[str, Any]:
    return extract_assigned_json(path.read_text(encoding="utf-8-sig"))


def load_asset_manifest(path: Path = DEFAULT_ASSETS_PATH) -> dict[str, dict[str, Any]]:
    data = read_json(path)
    return {str(asset["id"]): asset for asset in data.get("assets", []) if asset.get("id")}


def extract_h1_metrics(scores: dict[str, Any], asset_manifest: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    metrics_by_asset: dict[str, dict[str, Any]] = {}
    for asset, entry in sorted(scores.items()):
        if not isinstance(entry, dict):
            continue
        source_metrics = entry.get("metrics") or {}
        if not isinstance(source_metrics, dict):
            continue
        manifest_entry = asset_manifest.get(asset, {})
        row: dict[str, Any] = {
            "type": manifest_entry.get("type") or entry.get("type") or "unknown",
            "subtype": entry.get("subtype") or manifest_entry.get("sub") or "unknown",
            "source_timeframe": "H1",
            "source": "app/js/scores-data.js",
        }
        for category, metric_names in METRIC_CATEGORY_MAP.items():
            category_values = source_metrics.get(category) or {}
            if not isinstance(category_values, dict):
                continue
            for metric_name in metric_names:
                number = safe_number(category_values.get(metric_name))
                if number is not None:
                    row[metric_name] = number
        metrics_by_asset[asset] = row
    return metrics_by_asset


def build_source_manifest(
    *,
    scores_path: Path,
    assets_path: Path,
    metrics: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    metric_fields = sorted(
        {
            field
            for row in metrics.values()
            for field in row
            if field not in {"type", "subtype", "source_timeframe", "source"}
        }
    )
    return {
        "phase": "A52",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": {
            "scoresData": str(scores_path),
            "scoresDataSha256": sha256(scores_path),
            "assetsManifest": str(assets_path),
            "assetsManifestSha256": sha256(assets_path),
        },
        "timeframesGenerated": ["H1"],
        "assetCount": len(metrics),
        "metricFields": metric_fields,
        "policy": {
            "status": "first_party_h1_baseline_ready",
            "lowerHigherTimeframes": "not_generated_until_real_metric_source_is_selected",
            "noSyntheticTimeframes": True,
            "caveat": "This bundle normalizes existing dashboard H1 metrics only; it does not download market data or invent M15/M30/H4 values.",
        },
    }


def write_bundle(
    *,
    out_dir: Path,
    metrics: dict[str, dict[str, Any]],
    manifest: dict[str, Any],
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = out_dir / "asset_metrics.json"
    manifest_path = out_dir / "metric_source_manifest.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"metrics": metrics_path, "manifest": manifest_path}


def load_metric_gate():
    path = Path(__file__).with_name("multi_timeframe_metric_gate.py")
    spec = importlib.util.spec_from_file_location("multi_timeframe_metric_gate", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_metric_bundle(
    *,
    scores_path: Path = DEFAULT_SCORES_PATH,
    assets_path: Path = DEFAULT_ASSETS_PATH,
    out_dir: Path = DEFAULT_OUT_DIR,
    validate: bool = True,
) -> dict[str, Any]:
    scores = load_scores(scores_path)
    assets = load_asset_manifest(assets_path)
    metrics = extract_h1_metrics(scores, assets)
    manifest = build_source_manifest(scores_path=scores_path, assets_path=assets_path, metrics=metrics)
    paths = write_bundle(out_dir=out_dir, metrics=metrics, manifest=manifest)

    gate_report = None
    if validate:
        gate = load_metric_gate()
        gate_report = gate.build_gate_report(
            metrics_dir=out_dir,
            timeframes=["H1"],
            expected_assets=set(assets),
            min_asset_coverage=0.95,
            min_metric_completeness=0.90,
        )

    return {
        "metadata": {
            "phase": "A52",
            "generatedAt": manifest["generatedAt"],
            "outDir": str(out_dir),
            "assetCount": len(metrics),
            "timeframesGenerated": ["H1"],
            "caveat": manifest["policy"]["caveat"],
        },
        "paths": {name: str(path) for name, path in paths.items()},
        "manifest": manifest,
        "gate": gate_report,
    }


def render_markdown(report: dict[str, Any]) -> str:
    meta = report["metadata"]
    gate = report.get("gate") or {}
    lines = [
        "# SQX First-Party Metric Source",
        "",
        f"- Phase: `{meta['phase']}`",
        f"- Timeframes generated: `{', '.join(meta['timeframesGenerated'])}`",
        f"- Assets: `{meta['assetCount']}`",
        f"- Output dir: `{meta['outDir']}`",
        f"- Caveat: {meta['caveat']}",
        "",
        "## Files",
        "",
        f"- Metrics: `{report['paths']['metrics']}`",
        f"- Manifest: `{report['paths']['manifest']}`",
    ]
    if gate:
        lines += [
            "",
            "## Gate",
            "",
            f"- Status: `{gate['status']}`",
            f"- Failures: `{len(gate['failures'])}`",
        ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build first-party H1 metric files from dashboard scores-data.js.")
    parser.add_argument("--scores", default=str(DEFAULT_SCORES_PATH))
    parser.add_argument("--assets", default=str(DEFAULT_ASSETS_PATH))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--no-validate", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_metric_bundle(
        scores_path=Path(args.scores),
        assets_path=Path(args.assets),
        out_dir=Path(args.out_dir),
        validate=not args.no_validate,
    )
    text = json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_markdown(report)
    print(text)
    gate = report.get("gate")
    return 0 if not gate or gate.get("status") == "GO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
