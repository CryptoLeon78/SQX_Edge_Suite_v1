from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "public_buyer_page_cadence.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "public_buyer_page_cadence"
DEFAULT_CLOSEOUT_DIR = TOOL_ROOT / "data" / "buyer_ready_checkout_closeout"


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def project_path(rel_path: str) -> Path:
    return PROJECT_ROOT / rel_path


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def latest_closeout_file(directory: Path = DEFAULT_CLOSEOUT_DIR) -> Path | None:
    return latest_file(directory, "buyer_ready_checkout_closeout_*.json")


def parse_int(value: str, default: int) -> int:
    if value == "":
        return default
    return int(value)


def validate_required_files(config: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for item in config.get("requiredFiles", []):
        if not project_path(str(item)).is_file():
            findings.append(f"missing_required_file:{item}")
    return findings


def validate_dependency(config: dict[str, Any]) -> list[str]:
    depends_on = config.get("dependsOn") if isinstance(config.get("dependsOn"), dict) else {}
    closeout_config_path = project_path(str(depends_on.get("buyerReadyCloseoutConfig", "")))
    if not closeout_config_path.is_file():
        return ["buyer_ready_checkout_closeout_config_missing"]
    closeout_config = load_json(closeout_config_path)
    if closeout_config.get("state") != depends_on.get("buyerReadyCloseoutState"):
        return ["buyer_ready_checkout_closeout_state_invalid"]
    return []


def validate_closeout(closeout: dict[str, Any] | None, allow_no_go_closeout: bool) -> list[str]:
    if closeout is None:
        return ["buyer_ready_checkout_closeout_evidence_missing"]
    decision = closeout.get("decision", {})
    if not decision.get("go") and not allow_no_go_closeout:
        return ["buyer_ready_checkout_closeout_not_go", *decision.get("blockers", [])]
    return []


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def public_page_checklist() -> list[str]:
    return [
        "Product name, offer and audience are explicit.",
        "Buyer receives ZIP, license, onboarding and support details.",
        "Download, unzip, double click and license import steps are visible.",
        "Pricing, support and refund boundaries are plain.",
        "Responsible notice avoids financial-result promises.",
        "FAQ and support contact are visible before purchase.",
        "First-sale cadence and rollback are known before sharing the page.",
    ]


def decision_from(
    config: dict[str, Any],
    closeout: dict[str, Any] | None,
    public_page_sections: int,
    cadence_steps: int,
    page_status: str,
    support_cadence: str,
    first_sale_owner: str,
    cadence_notes: str,
    decision: str,
    confirmations: dict[str, bool],
    allow_no_go_closeout: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_closeout(closeout, allow_no_go_closeout))

    if public_page_sections < int(config.get("minimumPublicPageSections", 6)):
        blockers.append("public_page_sections_incomplete")
    if cadence_steps < int(config.get("minimumCadenceSteps", 5)):
        blockers.append("first_sale_cadence_incomplete")
    if page_status not in set(config.get("allowedPageStatuses", [])):
        blockers.append("page_status_invalid")
    if decision not in set(config.get("allowedDecisions", [])):
        blockers.append("page_decision_invalid")
    if not is_safe_text(support_cadence):
        blockers.append("support_cadence_missing_or_unsafe")
    if not is_safe_text(first_sale_owner):
        blockers.append("first_sale_owner_missing_or_unsafe")
    if not cadence_notes.strip():
        blockers.append("cadence_notes_missing")

    closeout_decision = closeout.get("closeout_decision", "") if closeout else ""
    if decision == "publish_private_page":
        if page_status not in {"private_link_ready", "published_controlled"}:
            blockers.append("publish_private_page_needs_private_link_ready")
        if closeout_decision not in {"keep_private_pilot", "open_controlled_sales"}:
            blockers.append("publish_private_page_needs_buyer_ready_closeout")
    if decision == "pause_sales":
        warnings.append("operator_decision_pause_sales")
    if decision == "revise_copy":
        warnings.append("operator_decision_revise_copy")
    if decision == "keep_draft":
        warnings.append("operator_decision_keep_draft")

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
        "# Public Buyer Page Cadence Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Page decision: `{report.get('page_decision') or 'missing'}`",
        f"- Page status: `{report.get('page_status') or 'missing'}`",
        f"- Public page sections: `{report.get('public_page_sections')}`",
        f"- Cadence steps: `{report.get('cadence_steps')}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["public_page_checklist"])
    lines.append("")
    lines.append("## Confirmations")
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
    json_path = output_dir / f"public_buyer_page_cadence_{current_stamp}.json"
    md_path = output_dir / f"public_buyer_page_cadence_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_public_page_cadence(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    closeout_file: Path | None = None,
    public_page_sections: int = -1,
    cadence_steps: int = -1,
    page_status: str = "",
    support_cadence: str = "",
    first_sale_owner: str = "",
    cadence_notes: str = "",
    decision: str = "keep_draft",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_closeout: bool = False,
    output_dir: Path = DEFAULT_OUTPUT,
    write: bool = True,
) -> dict[str, Any]:
    config = load_json(config_path)
    load_json(manifest_path)
    closeout = load_json(closeout_file) if closeout_file else None
    final_confirmations = confirmations or {}
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "public_buyer_page_cadence_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "closeout_source": str(closeout_file) if closeout_file else "",
        "closeout_decision": closeout.get("decision") if closeout else None,
        "closeout_page_decision": closeout.get("closeout_decision") if closeout else "",
        "public_page_sections": public_page_sections,
        "cadence_steps": cadence_steps,
        "page_status": page_status.strip(),
        "support_cadence": support_cadence.strip(),
        "first_sale_owner": first_sale_owner.strip(),
        "cadence_notes": cadence_notes.strip(),
        "page_decision": decision,
        "public_page_checklist": public_page_checklist(),
        "confirmations": final_confirmations,
    }
    report["decision"] = decision_from(
        config,
        closeout,
        public_page_sections,
        cadence_steps,
        page_status,
        support_cadence,
        first_sale_owner,
        cadence_notes,
        decision,
        final_confirmations,
        allow_no_go_closeout,
    )
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare public buyer page checklist and first-sale cadence.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--buyer-ready-closeout-file", default="")
    parser.add_argument("--use-latest-buyer-ready-closeout", action="store_true")
    parser.add_argument("--allow-no-go-closeout", action="store_true")
    parser.add_argument("--public-page-sections", default="")
    parser.add_argument("--cadence-steps", default="")
    parser.add_argument("--page-status", default="")
    parser.add_argument("--support-cadence", default="")
    parser.add_argument("--first-sale-owner", default="")
    parser.add_argument("--decision", default="keep_draft")
    parser.add_argument("--cadence-notes", default="")
    parser.add_argument("--confirm-buyer-ready-closeout-go", action="store_true")
    parser.add_argument("--confirm-public-copy-reviewed", action="store_true")
    parser.add_argument("--confirm-price-terms-reviewed", action="store_true")
    parser.add_argument("--confirm-buyer-steps-reviewed", action="store_true")
    parser.add_argument("--confirm-support-cadence-reviewed", action="store_true")
    parser.add_argument("--confirm-first-sale-cadence-reviewed", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-rollback-reviewed", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    closeout_file = Path(args.buyer_ready_closeout_file) if args.buyer_ready_closeout_file else None
    if args.use_latest_buyer_ready_closeout and closeout_file is None:
        closeout_file = latest_closeout_file()
        if closeout_file is None:
            print(json.dumps({"ok": False, "error": "buyer_ready_checkout_closeout_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    confirmations = {
        "buyer_ready_closeout_go": args.confirm_buyer_ready_closeout_go,
        "public_copy_reviewed": args.confirm_public_copy_reviewed,
        "price_terms_reviewed": args.confirm_price_terms_reviewed,
        "buyer_steps_reviewed": args.confirm_buyer_steps_reviewed,
        "support_cadence_reviewed": args.confirm_support_cadence_reviewed,
        "first_sale_cadence_reviewed": args.confirm_first_sale_cadence_reviewed,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "rollback_reviewed": args.confirm_rollback_reviewed,
    }
    report = collect_public_page_cadence(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        closeout_file=closeout_file,
        public_page_sections=parse_int(args.public_page_sections, -1),
        cadence_steps=parse_int(args.cadence_steps, -1),
        page_status=args.page_status,
        support_cadence=args.support_cadence,
        first_sale_owner=args.first_sale_owner,
        cadence_notes=args.cadence_notes,
        decision=args.decision.strip(),
        confirmations=confirmations,
        allow_no_go_closeout=args.allow_no_go_closeout,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
