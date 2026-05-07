from __future__ import annotations

import argparse
import csv
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "template_pack_2_assets.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "template_pack_2_assets"
DEFAULT_SPECS_DIR = TOOL_ROOT / "data" / "template_pack_2_specs"


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def project_path(rel_path: str) -> Path:
    return PROJECT_ROOT / rel_path


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def latest_specs_file(directory: Path = DEFAULT_SPECS_DIR) -> Path | None:
    return latest_file(directory, "template_pack_2_specs_*.json")


def forbidden_hits(text: str, forbidden: list[str]) -> list[str]:
    lower = text.lower()
    return [item for item in forbidden if item.lower() in lower]


def csv_headers(path: Path, delimiter: str) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        return next(reader, [])


def csv_rows(path: Path, delimiter: str) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def validate_required_files(config: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    forbidden = config.get("forbiddenClaims") if isinstance(config.get("forbiddenClaims"), list) else []
    for item in config.get("requiredFiles", []):
        path = project_path(str(item))
        if not path.is_file():
            findings.append(f"missing_required_file:{item}")
            continue
        hits = forbidden_hits(read_text(path), forbidden)
        findings.extend(f"forbidden_claim:{item}:{hit}" for hit in hits)
    return findings


def validate_dependency(config: dict[str, Any]) -> list[str]:
    depends_on = config.get("dependsOn") if isinstance(config.get("dependsOn"), dict) else {}
    specs_config_path = project_path(str(depends_on.get("templatePack2SpecsConfig", "")))
    if not specs_config_path.is_file():
        return ["template_pack_2_specs_config_missing"]
    specs_config = load_json(specs_config_path)
    if specs_config.get("state") != depends_on.get("templatePack2SpecsState"):
        return ["template_pack_2_specs_state_invalid"]
    return []


def validate_specs_evidence(specs: dict[str, Any] | None, config: dict[str, Any], allow_no_go_specs: bool) -> list[str]:
    if specs is None:
        return ["template_pack_2_specs_evidence_missing"]
    decision = specs.get("decision", {})
    if not decision.get("go") and not allow_no_go_specs:
        return ["template_pack_2_specs_not_go", *decision.get("blockers", [])]
    depends_on = config.get("dependsOn", {})
    if specs.get("spec_decision") != depends_on.get("requiredSpecDecision"):
        return ["template_pack_2_specs_decision_invalid"]
    if specs.get("next_phase") != depends_on.get("requiredNextPhase"):
        return ["template_pack_2_specs_next_phase_invalid"]
    return []


def validate_profiles(config: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    required_fields = set(config.get("profileRequiredFields", []))
    resource_dir = project_path(str(config["resourceDir"]))
    profile_paths = sorted(resource_dir.glob("profiles/*.json"))
    if len(profile_paths) < int(config.get("minimumProfiles", 3)):
        findings.append("template_pack_2_requires_minimum_profiles")
    for path in profile_paths:
        profile = load_json(path)
        missing = sorted(required_fields - set(profile))
        findings.extend(f"profile_missing_field:{path.name}:{field}" for field in missing)
        for list_field in ("assetClasses", "timeframes", "indicatorFamilies", "riskNotes", "expectedWorkflow"):
            if not isinstance(profile.get(list_field), list) or not profile.get(list_field):
                findings.append(f"profile_field_must_be_non_empty_list:{path.name}:{list_field}")
    return findings


def validate_csv(config: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    delimiter = str(config.get("csvDelimiter", ";"))
    csv_path = project_path("resources/pro-template-pack-2/presets/strategy_import_template_pack_2.csv")
    if not csv_path.is_file():
        return ["template_pack_2_csv_missing"]
    headers = csv_headers(csv_path, delimiter)
    for column in config.get("csvRequiredColumns", []):
        if column not in headers:
            findings.append(f"template_pack_2_csv_missing_column:{column}")
    rows = csv_rows(csv_path, delimiter)
    if len(rows) < int(config.get("minimumPresetRows", 8)):
        findings.append("template_pack_2_csv_needs_eight_rows")
    asset_families = {row.get("Asset Family", "").strip() for row in rows if row.get("Asset Family", "").strip()}
    if len(asset_families) < int(config.get("minimumAssetFamilies", 2)):
        findings.append("template_pack_2_csv_needs_asset_families")
    return findings


def build_package(config: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    package_name = f"{config.get('packageNamePrefix', 'SQX_Template_Pack_2')}_{stamp()}.zip"
    package_path = output_dir / package_name
    resource_dir = project_path(str(config["resourceDir"]))
    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(resource_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(resource_dir.parent))
    return package_path


def decision_from(
    config: dict[str, Any],
    specs: dict[str, Any] | None,
    confirmations: dict[str, bool],
    package_ready: bool,
    allow_no_go_specs: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")
    if not package_ready:
        warnings.append("package_not_generated_in_this_run")
    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_specs_evidence(specs, config, allow_no_go_specs))
    blockers.extend(validate_profiles(config))
    blockers.extend(validate_csv(config))
    if any(item.startswith("forbidden_claim:") for item in blockers):
        blockers.append("forbidden_claims_present")
    deduped_blockers = sorted(set(blockers))
    return {
        "go": not deduped_blockers,
        "label": "GO" if not deduped_blockers else "NO-GO",
        "blockers": deduped_blockers,
        "warnings": sorted(set(warnings)),
    }


def markdown_report(report: dict[str, Any]) -> str:
    decision = report["decision"]
    lines = [
        "# Template Pack 2 Assets Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Resource dir: `{report['resource_dir']}`",
        f"- Package: `{report.get('package_path') or 'not_generated'}`",
        "",
        "## Confirmations",
    ]
    for name, value in report["confirmations"].items():
        lines.append(f"- {name}: `{value}`")
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    return "\n".join(lines) + "\n"


def write_evidence(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"template_pack_2_assets_{current_stamp}.json"
    md_path = output_dir / f"template_pack_2_assets_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_assets(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    specs_file: Path | None = None,
    confirmations: dict[str, bool] | None = None,
    allow_no_go_specs: bool = False,
    output_dir: Path = DEFAULT_OUTPUT,
    create_package: bool = False,
    write: bool = True,
) -> dict[str, Any]:
    config = load_json(config_path)
    load_json(manifest_path)
    specs = load_json(specs_file) if specs_file else None
    package_path = build_package(config, output_dir) if create_package else None
    final_confirmations = confirmations or {}
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "template_pack_2_assets_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "specs_source": str(specs_file) if specs_file else "",
        "specs_decision": specs.get("decision") if specs else None,
        "resource_dir": config.get("resourceDir"),
        "included_in_portable": bool(config.get("includedInPortable")),
        "included_in_addon_delivery": bool(config.get("includedInAddOnDelivery")),
        "package_path": str(package_path) if package_path else "",
        "confirmations": final_confirmations,
    }
    report["decision"] = decision_from(
        config,
        specs,
        final_confirmations,
        package_ready=package_path is not None,
        allow_no_go_specs=allow_no_go_specs,
    )
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and package SQX Template Pack 2 initial assets.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--specs-file", default="")
    parser.add_argument("--use-latest-specs", action="store_true")
    parser.add_argument("--allow-no-go-specs", action="store_true")
    parser.add_argument("--confirm-specs-go", action="store_true")
    parser.add_argument("--confirm-asset-files-present", action="store_true")
    parser.add_argument("--confirm-profile-schema-validated", action="store_true")
    parser.add_argument("--confirm-preset-csv-validated", action="store_true")
    parser.add_argument("--confirm-support-boundaries-included", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-addon-delivery-separate", action="store_true")
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    specs_file = Path(args.specs_file) if args.specs_file else None
    if args.use_latest_specs and specs_file is None:
        specs_file = latest_specs_file()
        if specs_file is None:
            print(json.dumps({"ok": False, "error": "template_pack_2_specs_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    confirmations = {
        "specs_go": args.confirm_specs_go,
        "asset_files_present": args.confirm_asset_files_present,
        "profile_schema_validated": args.confirm_profile_schema_validated,
        "preset_csv_validated": args.confirm_preset_csv_validated,
        "support_boundaries_included": args.confirm_support_boundaries_included,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "addon_delivery_separate": args.confirm_addon_delivery_separate,
    }
    report = collect_assets(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        specs_file=specs_file,
        confirmations=confirmations,
        allow_no_go_specs=args.allow_no_go_specs,
        output_dir=Path(args.output_dir),
        create_package=args.package,
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
