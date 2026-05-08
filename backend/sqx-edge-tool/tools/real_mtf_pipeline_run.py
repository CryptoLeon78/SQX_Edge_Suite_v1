"""
Run the real-data multi-timeframe pipeline end to end.

A56 orchestrates A55 -> A53 -> A54. It can be run against a directory of
operator-exported OHLC CSVs and will only return GO when real metric files and
guarded plan artifacts are produced.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
CONFIG_DIR = TOOL_ROOT / "config"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "real_mtf_pipeline_run.json"
DEFAULT_INPUT_DIR = PROJECT_ROOT / "data" / "ohlc"
DEFAULT_WORK_DIR = PROJECT_ROOT / "analysis_output" / "real_mtf_pipeline_run"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_ohlc_builder():
    return load_module("ohlc_metric_builder", Path(__file__).with_name("ohlc_metric_builder.py"))


def load_plan_artifacts():
    return load_module("multi_timeframe_plan_artifacts", Path(__file__).with_name("multi_timeframe_plan_artifacts.py"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def observed_assets_from_builder(builder_report: dict[str, Any]) -> set[str]:
    return {
        str(item.get("asset", "")).upper()
        for item in builder_report.get("files", [])
        if item.get("status") == "processed" and item.get("asset")
    }


def build_no_go_report(
    *,
    input_dir: Path,
    work_dir: Path,
    failures: list[str],
    builder_report: dict[str, Any] | None = None,
    artifacts_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "metadata": {
            "phase": "A56",
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "inputDir": str(input_dir),
            "workDir": str(work_dir),
            "status": "NO_GO",
            "nextAction": "Place reviewed OHLC CSV files in the input directory, rerun A56, and require A53/A54 GO before UI exposure.",
        },
        "status": "NO_GO",
        "failures": failures,
        "builder": builder_report,
        "artifacts": artifacts_report,
    }


def run_pipeline(
    *,
    input_dir: Path = DEFAULT_INPUT_DIR,
    work_dir: Path = DEFAULT_WORK_DIR,
    expected_assets_mode: str = "manifest",
    include_first_party_h1: bool = True,
) -> dict[str, Any]:
    config = read_json(DEFAULT_CONFIG_PATH)
    if expected_assets_mode not in config["allowedExpectedAssetsModes"]:
        raise ValueError(f"expected_assets_mode must be one of {config['allowedExpectedAssetsModes']}")

    metrics_dir = work_dir / "metrics"
    artifacts_dir = work_dir / "plan_artifacts"
    work_dir.mkdir(parents=True, exist_ok=True)

    if not input_dir.exists():
        report = build_no_go_report(
            input_dir=input_dir,
            work_dir=work_dir,
            failures=[f"input directory does not exist: {input_dir}"],
        )
        persist_report(report, work_dir)
        return report

    builder = load_ohlc_builder()
    builder_report = builder.build_metric_files(input_dir=input_dir, out_dir=metrics_dir)
    if builder_report["status"] != "GO":
        report = build_no_go_report(
            input_dir=input_dir,
            work_dir=work_dir,
            failures=["A55 OHLC metric builder did not return GO", *builder_report.get("failures", [])],
            builder_report=builder_report,
        )
        persist_report(report, work_dir)
        return report

    expected_assets = observed_assets_from_builder(builder_report) if expected_assets_mode == "observed" else None
    artifacts = load_plan_artifacts()
    artifacts_report = artifacts.build_plan_artifacts(
        source_dir=metrics_dir,
        work_dir=artifacts_dir,
        include_first_party_h1=include_first_party_h1,
        expected_assets=expected_assets,
    )
    if artifacts_report["status"] != "GO":
        report = build_no_go_report(
            input_dir=input_dir,
            work_dir=work_dir,
            failures=["A54 guarded plan artifacts did not return GO", *artifacts_report.get("intake", {}).get("failures", [])],
            builder_report=builder_report,
            artifacts_report=artifacts_report,
        )
        persist_report(report, work_dir)
        return report

    report = {
        "metadata": {
            "phase": "A56",
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "inputDir": str(input_dir),
            "workDir": str(work_dir),
            "metricsDir": str(metrics_dir),
            "artifactsDir": str(artifacts_dir),
            "status": "GO",
            "expectedAssetsMode": expected_assets_mode,
            "goPolicy": config["goPolicy"],
            "nextPhase": config["nextPhase"],
        },
        "status": "GO",
        "failures": [],
        "builder": builder_report,
        "artifacts": artifacts_report,
    }
    persist_report(report, work_dir)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    meta = report["metadata"]
    lines = [
        "# SQX Real MTF Pipeline Run",
        "",
        f"- Phase: `{meta['phase']}`",
        f"- Status: `{report['status']}`",
        f"- Input dir: `{meta['inputDir']}`",
        f"- Work dir: `{meta['workDir']}`",
    ]
    builder = report.get("builder") or {}
    if builder:
        lines += [
            f"- Builder status: `{builder.get('status')}`",
            f"- Metric outputs: `{len(builder.get('outputs', {}))}`",
        ]
    artifacts = report.get("artifacts") or {}
    if artifacts:
        lines.append(f"- Plan artifacts status: `{artifacts.get('status')}`")
    if report["status"] == "GO":
        lines += [
            f"- Next phase: {meta['nextPhase']}",
            "",
            "## Outputs",
            "",
        ]
        for tf, path in sorted(builder.get("outputs", {}).items()):
            lines.append(f"- {tf}: `{path}`")
        for name, path in sorted((artifacts.get("artifacts") or {}).items()):
            lines.append(f"- {name}: `{path}`")
    else:
        lines += ["", "## Failures", ""]
        lines.extend(f"- {failure}" for failure in report.get("failures", []))
        lines += ["", "## Next", "", f"- {meta['nextAction']}"]
    return "\n".join(lines) + "\n"


def persist_report(report: dict[str, Any], work_dir: Path) -> None:
    write_json(work_dir / "a56_real_mtf_pipeline_run.json", report)
    write_text(work_dir / "a56_real_mtf_pipeline_run.md", render_markdown(report))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the real-data SQX MTF pipeline: OHLC CSV -> metrics -> intake -> plan artifacts.")
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--work-dir", default=str(DEFAULT_WORK_DIR))
    parser.add_argument("--expected-assets-mode", choices=["manifest", "observed"], default="manifest")
    parser.add_argument("--no-first-party-h1", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = run_pipeline(
        input_dir=Path(args.input_dir),
        work_dir=Path(args.work_dir),
        expected_assets_mode=args.expected_assets_mode,
        include_first_party_h1=not args.no_first_party_h1,
    )
    text = json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_markdown(report)
    print(text)
    return 0 if report["status"] == "GO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
