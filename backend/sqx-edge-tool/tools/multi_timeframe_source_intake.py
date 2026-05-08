"""
Controlled intake for real multi-timeframe metric sources.

A53 does not download market data or synthesize missing timeframes. It prepares a
reviewable metrics bundle, optionally adds the first-party H1 baseline from A52,
and then delegates validation to the A51 metric gate.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
CONFIG_DIR = TOOL_ROOT / "config"
DEFAULT_POLICY_PATH = CONFIG_DIR / "multi_timeframe_source_policy.json"
DEFAULT_OUT_DIR = PROJECT_ROOT / "analysis_output" / "mtf_source_intake"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_policy(path: Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    return read_json(path)


def load_metric_gate():
    return load_module("multi_timeframe_metric_gate", Path(__file__).with_name("multi_timeframe_metric_gate.py"))


def load_first_party_source():
    return load_module("first_party_metric_source", Path(__file__).with_name("first_party_metric_source.py"))


def normalize_tf(tf: str) -> str:
    return str(tf or "").strip().upper()


def file_name_for(tf: str, policy: dict[str, Any]) -> str:
    tf = normalize_tf(tf)
    return policy.get("acceptedMetricFiles", {}).get(tf) or ("asset_metrics.json" if tf == "H1" else f"asset_metrics_{tf}.json")


def copy_metric_file(source_dir: Path, out_dir: Path, tf: str, policy: dict[str, Any]) -> dict[str, Any]:
    file_name = file_name_for(tf, policy)
    source_path = source_dir / file_name
    target_path = out_dir / file_name
    if not source_path.exists():
        return {"tf": tf, "file": file_name, "status": "missing", "source": str(source_path)}
    out_dir.mkdir(parents=True, exist_ok=True)
    if source_path.resolve() != target_path.resolve():
        shutil.copy2(source_path, target_path)
    return {"tf": tf, "file": file_name, "status": "copied", "source": str(source_path), "target": str(target_path)}


def prepare_intake_bundle(
    *,
    source_dir: Path,
    out_dir: Path,
    policy: dict[str, Any],
    include_first_party_h1: bool = True,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    required_tfs = [normalize_tf(tf) for tf in policy["requiredTimeframes"]]
    copied: list[dict[str, Any]] = []

    for tf in required_tfs:
        if tf == "H1" and include_first_party_h1 and policy.get("firstPartyH1Allowed", False):
            first_party = load_first_party_source()
            first_party_report = first_party.build_metric_bundle(out_dir=out_dir, validate=False)
            copied.append(
                {
                    "tf": "H1",
                    "file": file_name_for("H1", policy),
                    "status": "generated_first_party_h1",
                    "source": first_party_report["manifest"]["source"]["scoresData"],
                    "target": first_party_report["paths"]["metrics"],
                    "manifest": first_party_report["paths"]["manifest"],
                }
            )
            continue
        copied.append(copy_metric_file(source_dir, out_dir, tf, policy))

    return {"outDir": str(out_dir), "files": copied}


def build_intake_report(
    *,
    source_dir: Path,
    out_dir: Path = DEFAULT_OUT_DIR,
    policy_path: Path = DEFAULT_POLICY_PATH,
    include_first_party_h1: bool = True,
    expected_assets: set[str] | None = None,
) -> dict[str, Any]:
    policy = load_policy(policy_path)
    required_tfs = [normalize_tf(tf) for tf in policy["requiredTimeframes"]]
    bundle = prepare_intake_bundle(
        source_dir=source_dir,
        out_dir=out_dir,
        policy=policy,
        include_first_party_h1=include_first_party_h1,
    )

    missing_real_timeframes = [
        item["tf"]
        for item in bundle["files"]
        if item["status"] == "missing" and item["tf"] != "H1"
    ]
    synthetic_blocked = bool(missing_real_timeframes) and not policy.get("syntheticTimeframesAllowed", False)

    gate = load_metric_gate()
    gate_report = gate.build_gate_report(
        metrics_dir=out_dir,
        timeframes=required_tfs,
        expected_assets=expected_assets,
        min_asset_coverage=float(policy["minimumAssetCoverage"]),
        min_metric_completeness=float(policy["minimumMetricCompleteness"]),
    )

    failures = list(gate_report["failures"])
    if synthetic_blocked:
        failures.append("missing real M15/M30/H4 files cannot be replaced with synthetic metrics")
    status = "GO" if gate_report["status"] == "GO" and not synthetic_blocked else "NO_GO"
    return {
        "metadata": {
            "phase": "A53",
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "sourceDir": str(source_dir),
            "outDir": str(out_dir),
            "requiredTimeframes": required_tfs,
            "includeFirstPartyH1": include_first_party_h1,
            "policyState": policy["state"],
            "goPolicy": policy["goPolicy"],
            "nextPhase": policy["nextPhase"],
        },
        "status": status,
        "failures": failures,
        "missingRealTimeframes": missing_real_timeframes,
        "bundle": bundle,
        "gate": gate_report,
    }


def render_markdown(report: dict[str, Any]) -> str:
    meta = report["metadata"]
    lines = [
        "# SQX Multi-Timeframe Source Intake",
        "",
        f"- Phase: `{meta['phase']}`",
        f"- Status: `{report['status']}`",
        f"- Source dir: `{meta['sourceDir']}`",
        f"- Output dir: `{meta['outDir']}`",
        f"- Required TFs: `{', '.join(meta['requiredTimeframes'])}`",
        f"- Include first-party H1: `{meta['includeFirstPartyH1']}`",
        f"- Policy: {meta['goPolicy']}",
        "",
        "## Bundle Files",
        "",
        "| TF | File | Status |",
        "| --- | --- | --- |",
    ]
    for item in report["bundle"]["files"]:
        lines.append(f"| {item['tf']} | `{item['file']}` | `{item['status']}` |")
    if report["failures"]:
        lines += ["", "## Failures", ""]
        lines.extend(f"- {failure}" for failure in report["failures"])
    lines += ["", "## Next", "", f"- {meta['nextPhase']}"]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare and validate a real SQX multi-timeframe metric source.")
    parser.add_argument("--source-dir", required=True, help="Directory containing real asset_metrics[_TF].json files.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--policy", default=str(DEFAULT_POLICY_PATH))
    parser.add_argument("--no-first-party-h1", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_intake_report(
        source_dir=Path(args.source_dir),
        out_dir=Path(args.out_dir),
        policy_path=Path(args.policy),
        include_first_party_h1=not args.no_first_party_h1,
    )
    text = json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_markdown(report)
    print(text)
    return 0 if report["status"] == "GO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
