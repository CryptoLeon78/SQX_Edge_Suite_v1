"""
Generate guarded plan-review artifacts from validated MTF metrics.

A54 connects the A53 intake to Plan Quality Advisor outputs, but only when the
full multi-timeframe source passes GO. Incomplete sources produce a blocked
artifact instead of partial multi-timeframe evidence.
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
DEFAULT_WORK_DIR = PROJECT_ROOT / "analysis_output" / "mtf_plan_artifacts"
DEFAULT_BUNDLE_DIR = DEFAULT_WORK_DIR / "bundle"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_intake():
    return load_module("multi_timeframe_source_intake", Path(__file__).with_name("multi_timeframe_source_intake.py"))


def load_advisor():
    return load_module("plan_quality_advisor", Path(__file__).with_name("plan_quality_advisor.py"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_blocked_report(
    *,
    intake_report: dict[str, Any],
    work_dir: Path,
) -> dict[str, Any]:
    return {
        "metadata": {
            "phase": "A54",
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "workDir": str(work_dir),
            "status": "NO_GO",
            "reason": "A53 intake did not pass GO; plan review MTF artifacts were not generated.",
            "nextAction": "Supply real M30/M15/H4 metric files or a market-data pipeline export, then rerun A53/A54.",
        },
        "status": "NO_GO",
        "intake": intake_report,
        "artifacts": {},
    }


def render_markdown(report: dict[str, Any]) -> str:
    meta = report["metadata"]
    lines = [
        "# SQX Multi-Timeframe Plan Artifacts",
        "",
        f"- Phase: `{meta['phase']}`",
        f"- Status: `{report['status']}`",
        f"- Work dir: `{meta['workDir']}`",
    ]
    if report["status"] != "GO":
        lines += [
            f"- Reason: {meta['reason']}",
            f"- Next action: {meta['nextAction']}",
            "",
            "## Intake Failures",
            "",
        ]
        lines.extend(f"- {failure}" for failure in report["intake"].get("failures", []))
        return "\n".join(lines) + "\n"

    summary = report.get("planSummary") or {}
    lines += [
        f"- Intake status: `{report['intake']['status']}`",
        f"- Current plan MTF covered: `{summary.get('covered', 0)}`",
        f"- Current plan MTF strong: `{summary.get('strong', 0)}`",
        "",
        "## Artifacts",
        "",
    ]
    for name, path in report["artifacts"].items():
        lines.append(f"- {name}: `{path}`")
    return "\n".join(lines) + "\n"


def build_plan_artifacts(
    *,
    source_dir: Path,
    work_dir: Path = DEFAULT_WORK_DIR,
    bundle_dir: Path | None = None,
    include_first_party_h1: bool = True,
    expected_assets: set[str] | None = None,
    limit: int = 14,
    min_composite: float = 60.0,
) -> dict[str, Any]:
    work_dir.mkdir(parents=True, exist_ok=True)
    active_bundle_dir = bundle_dir or (work_dir / "bundle")
    intake = load_intake()
    intake_report = intake.build_intake_report(
        source_dir=source_dir,
        out_dir=active_bundle_dir,
        include_first_party_h1=include_first_party_h1,
        expected_assets=expected_assets,
    )
    intake_json = work_dir / "a53_intake_report.json"
    intake_md = work_dir / "a53_intake_report.md"
    write_json(intake_json, intake_report)
    write_text(intake_md, intake.render_markdown(intake_report))

    if intake_report["status"] != "GO":
        report = build_blocked_report(intake_report=intake_report, work_dir=work_dir)
        report["artifacts"] = {
            "intakeJson": str(intake_json),
            "intakeMarkdown": str(intake_md),
        }
        write_json(work_dir / "a54_plan_artifacts_report.json", report)
        write_text(work_dir / "a54_plan_artifacts_report.md", render_markdown(report))
        return report

    advisor = load_advisor()
    plan_report = advisor.build_report(
        limit=limit,
        min_composite=min_composite,
        mtf_metrics_dir=active_bundle_dir,
        mtf_timeframes=intake_report["metadata"]["requiredTimeframes"],
    )
    plan_json = work_dir / "plan_quality_advisor_mtf.json"
    plan_md = work_dir / "plan_quality_advisor_mtf.md"
    write_json(plan_json, plan_report)
    write_text(plan_md, advisor.render_markdown(plan_report))
    report = {
        "metadata": {
            "phase": "A54",
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "workDir": str(work_dir),
            "status": "GO",
            "sourceDir": str(source_dir),
            "bundleDir": str(active_bundle_dir),
            "caveat": "Artifacts use multi-timeframe evidence only after the A53 intake returns GO.",
        },
        "status": "GO",
        "intake": intake_report,
        "planSummary": plan_report.get("multiTimeframePlanSummary"),
        "artifacts": {
            "intakeJson": str(intake_json),
            "intakeMarkdown": str(intake_md),
            "planJson": str(plan_json),
            "planMarkdown": str(plan_md),
        },
    }
    write_json(work_dir / "a54_plan_artifacts_report.json", report)
    write_text(work_dir / "a54_plan_artifacts_report.md", render_markdown(report))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate guarded Plan Quality Advisor artifacts from validated MTF metrics.")
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--work-dir", default=str(DEFAULT_WORK_DIR))
    parser.add_argument("--bundle-dir")
    parser.add_argument("--no-first-party-h1", action="store_true")
    parser.add_argument("--limit", type=int, default=14)
    parser.add_argument("--min-composite", type=float, default=60.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_plan_artifacts(
        source_dir=Path(args.source_dir),
        work_dir=Path(args.work_dir),
        bundle_dir=Path(args.bundle_dir) if args.bundle_dir else None,
        include_first_party_h1=not args.no_first_party_h1,
        limit=args.limit,
        min_composite=args.min_composite,
    )
    text = json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_markdown(report)
    print(text)
    return 0 if report["status"] == "GO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
