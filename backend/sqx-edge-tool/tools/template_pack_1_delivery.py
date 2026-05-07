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
DEFAULT_CONFIG = TOOL_ROOT / "config" / "template_pack_1.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "template_pack_1_delivery"


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


def forbidden_hits(text: str, forbidden: list[str]) -> list[str]:
    lower = text.lower()
    return [item for item in forbidden if item.lower() in lower]


def csv_headers(path: Path, delimiter: str) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        return next(reader, [])


def csv_row_count(path: Path, delimiter: str) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        return sum(1 for _row in reader)


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
    gate_path = project_path(str(depends_on.get("buyerOnboardingSupportGateConfig", "")))
    expected_state = depends_on.get("buyerOnboardingSupportGateState")
    if not gate_path.is_file():
        return ["buyer_onboarding_support_gate_config_missing"]
    gate = load_json(gate_path)
    if gate.get("state") != expected_state:
        return ["buyer_onboarding_support_gate_state_invalid"]
    return []


def validate_profiles(config: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    required_fields = set(config.get("profileRequiredFields", []))
    profile_paths = sorted(project_path(config["resourceDir"]).glob("profiles/*.json"))
    if len(profile_paths) < 3:
        findings.append("template_pack_1_requires_three_profiles")
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
    csv_path = project_path("resources/pro-template-pack-1/presets/strategy_import_template_pack_1.csv")
    if not csv_path.is_file():
        return ["template_pack_1_csv_missing"]
    headers = csv_headers(csv_path, delimiter)
    for column in config.get("csvRequiredColumns", []):
        if column not in headers:
            findings.append(f"template_pack_1_csv_missing_column:{column}")
    if csv_row_count(csv_path, delimiter) < 3:
        findings.append("template_pack_1_csv_needs_three_rows")
    return findings


def build_package(config: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    package_name = f"{config.get('packageNamePrefix', 'SQX_Template_Pack_1')}_{stamp()}.zip"
    package_path = output_dir / package_name
    resource_dir = project_path(str(config["resourceDir"]))
    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(resource_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(resource_dir.parent))
    return package_path


def decision_from(
    config: dict[str, Any],
    customer_email: str,
    customer_id: str,
    order_id: str,
    buyer_onboarding_gate_go: bool,
    addon_order_confirmed: bool,
    pack_zip_ready: bool,
    readme_included: bool,
    profiles_validated: bool,
    support_boundaries_included: bool,
    safe_claims_reviewed: bool,
    support_scope_needs_setup_assist: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if not customer_email and not customer_id:
        blockers.append("customer_reference_missing")
    if not order_id:
        blockers.append("order_id_missing")
    if not buyer_onboarding_gate_go:
        blockers.append("buyer_onboarding_gate_not_go")
    if not addon_order_confirmed:
        blockers.append("addon_order_not_confirmed")
    if not pack_zip_ready:
        blockers.append("pack_zip_not_ready")
    if not readme_included:
        blockers.append("readme_not_included")
    if not profiles_validated:
        blockers.append("profiles_not_validated")
    if not support_boundaries_included:
        blockers.append("support_boundaries_not_included")
    if not safe_claims_reviewed:
        blockers.append("safe_claims_not_reviewed")
    if support_scope_needs_setup_assist:
        warnings.append("support_scope_needs_setup_assist")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
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
        "# Template Pack 1 Delivery Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Customer: `{report.get('customer_email') or report.get('customer_id') or 'missing'}`",
        f"- Order: `{report.get('order_id') or 'missing'}`",
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
    json_path = output_dir / f"template_pack_1_delivery_{current_stamp}.json"
    md_path = output_dir / f"template_pack_1_delivery_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_delivery(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    customer_email: str = "",
    customer_id: str = "",
    order_id: str = "",
    buyer_onboarding_gate_go: bool = False,
    addon_order_confirmed: bool = False,
    pack_zip_ready: bool = False,
    readme_included: bool = False,
    profiles_validated: bool = False,
    support_boundaries_included: bool = False,
    safe_claims_reviewed: bool = False,
    support_scope_needs_setup_assist: bool = False,
    output_dir: Path = DEFAULT_OUTPUT,
    create_package: bool = False,
    write: bool = True,
) -> dict[str, Any]:
    config = load_json(config_path)
    load_json(manifest_path)
    package_path = build_package(config, output_dir) if create_package else None
    confirmations = {
        "buyer_onboarding_gate_go": buyer_onboarding_gate_go,
        "addon_order_confirmed": addon_order_confirmed,
        "pack_zip_ready": pack_zip_ready or package_path is not None,
        "readme_included": readme_included,
        "profiles_validated": profiles_validated,
        "support_boundaries_included": support_boundaries_included,
        "safe_claims_reviewed": safe_claims_reviewed,
        "support_scope_needs_setup_assist": support_scope_needs_setup_assist,
    }
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "template_pack_1_delivery_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "resource_dir": config.get("resourceDir"),
        "included_in_portable": bool(config.get("includedInPortable")),
        "included_in_addon_delivery": bool(config.get("includedInAddOnDelivery")),
        "customer_email": customer_email,
        "customer_id": customer_id,
        "order_id": order_id,
        "package_path": str(package_path) if package_path else "",
        "confirmations": confirmations,
        "decision": decision_from(
            config,
            customer_email,
            customer_id,
            order_id,
            buyer_onboarding_gate_go,
            addon_order_confirmed,
            confirmations["pack_zip_ready"],
            readme_included,
            profiles_validated,
            support_boundaries_included,
            safe_claims_reviewed,
            support_scope_needs_setup_assist,
        ),
    }
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and package SQX Template Pack 1 delivery.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--customer-email", default="")
    parser.add_argument("--customer-id", default="")
    parser.add_argument("--order-id", default="")
    parser.add_argument("--confirm-buyer-onboarding-gate-go", action="store_true")
    parser.add_argument("--confirm-addon-order-confirmed", action="store_true")
    parser.add_argument("--confirm-pack-zip-ready", action="store_true")
    parser.add_argument("--confirm-readme-included", action="store_true")
    parser.add_argument("--confirm-profiles-validated", action="store_true")
    parser.add_argument("--confirm-support-boundaries-included", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--support-scope-needs-setup-assist", action="store_true")
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    report = collect_delivery(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        customer_email=args.customer_email,
        customer_id=args.customer_id,
        order_id=args.order_id,
        buyer_onboarding_gate_go=args.confirm_buyer_onboarding_gate_go,
        addon_order_confirmed=args.confirm_addon_order_confirmed,
        pack_zip_ready=args.confirm_pack_zip_ready,
        readme_included=args.confirm_readme_included,
        profiles_validated=args.confirm_profiles_validated,
        support_boundaries_included=args.confirm_support_boundaries_included,
        safe_claims_reviewed=args.confirm_safe_claims_reviewed,
        support_scope_needs_setup_assist=args.support_scope_needs_setup_assist,
        output_dir=Path(args.output_dir),
        create_package=args.package,
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
