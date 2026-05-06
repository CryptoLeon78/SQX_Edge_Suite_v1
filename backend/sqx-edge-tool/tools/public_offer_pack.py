from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT_DIR = TOOL_ROOT / "data" / "public_offer_pack"
DEFAULT_FEEDBACK_DIR = TOOL_ROOT / "data" / "commercial_feedback_loop"
DEFAULT_DIST_DIR = PROJECT_ROOT / "dist"
DEFAULT_SCREENSHOT_DIR = PROJECT_ROOT / "output" / "playwright"
FORBIDDEN_CLAIMS = (
    "rentabilidad garantizada",
    "beneficios garantizados",
    "estrategias ganadoras",
    "resultados financieros garantizados",
    "profit guaranteed",
    "guaranteed profits",
)


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def latest_feedback_file(directory: Path = DEFAULT_FEEDBACK_DIR) -> Path | None:
    return latest_file(directory, "commercial_feedback_loop_*.json")


def latest_portable_zip(directory: Path = DEFAULT_DIST_DIR) -> Path | None:
    return latest_file(directory, "SQX_Edge_Tool_Portable_*.zip")


def screenshot_count(directory: Path = DEFAULT_SCREENSHOT_DIR) -> int:
    if not directory.is_dir():
        return 0
    return len(list(directory.glob("*.png")))


def contains_forbidden_claims(*values: str) -> list[str]:
    text = " ".join(values).lower()
    return [claim for claim in FORBIDDEN_CLAIMS if claim in text]


def offer_sections() -> list[str]:
    return [
        "headline",
        "subheadline",
        "audience",
        "included",
        "faq",
        "safe_claims",
        "release_notes",
        "buyer_steps",
        "support",
        "disclaimer",
    ]


def buyer_steps() -> list[str]:
    return [
        "Download the portable ZIP.",
        "Extract the folder.",
        "Double click START_SQX_EDGE.bat.",
        "Open Inicio > Licencia.",
        "Import the signed Pro license JSON.",
        "Generate a support diagnostic if activation fails.",
    ]


def decision_from(
    feedback: dict[str, Any] | None,
    zip_path: Path | None,
    screenshots: int,
    offer_headline: str,
    offer_subheadline: str,
    faq_ready: bool,
    release_notes_ready: bool,
    buyer_steps_ready: bool,
    support_copy_ready: bool,
    safe_claims_reviewed: bool,
    checkout_ready: bool,
    public_page_ready: bool,
    allow_no_go_feedback: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if feedback is None:
        blockers.append("commercial_feedback_loop_missing")
    elif not feedback.get("decision", {}).get("go") and not allow_no_go_feedback:
        blockers.append("commercial_feedback_loop_not_go")
        blockers.extend(feedback.get("decision", {}).get("blockers", []))
    if zip_path is None or not zip_path.is_file():
        blockers.append("portable_zip_missing")
    if screenshots < 3:
        blockers.append("screenshots_missing")
    if not offer_headline.strip():
        blockers.append("offer_headline_missing")
    if not offer_subheadline.strip():
        blockers.append("offer_subheadline_missing")
    forbidden = contains_forbidden_claims(offer_headline, offer_subheadline)
    if forbidden:
        blockers.append("forbidden_claims_present")
        blockers.extend(f"forbidden_claim_{claim.replace(' ', '_')}" for claim in forbidden)
    if not faq_ready:
        blockers.append("faq_not_ready")
    if not release_notes_ready:
        blockers.append("release_notes_not_ready")
    if not buyer_steps_ready:
        blockers.append("buyer_steps_not_ready")
    if not support_copy_ready:
        blockers.append("support_copy_not_ready")
    if not safe_claims_reviewed:
        blockers.append("safe_claims_not_reviewed")
    if not checkout_ready:
        blockers.append("checkout_not_ready")
    if not public_page_ready:
        blockers.append("public_page_not_ready")
    if screenshots < 5:
        warnings.append("screenshot_count_below_recommended_pack")

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
        "# SQX Edge Public Offer Pack",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Feedback source: `{report.get('feedback_source') or 'none'}`",
        f"- ZIP: `{report.get('zip_path') or 'not found'}`",
        f"- Screenshot count: `{report.get('screenshot_count')}`",
        f"- Headline: `{report.get('offer_headline') or 'not configured'}`",
        f"- Subheadline: `{report.get('offer_subheadline') or 'not configured'}`",
        "",
        "## Offer Sections",
    ]
    lines.extend(f"- {item}" for item in report["offer_sections"])
    lines.append("")
    lines.append("## Buyer Steps")
    lines.extend(f"- {item}" for item in report["buyer_steps"])
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    return "\n".join(lines) + "\n"


def write_pack(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"public_offer_pack_{current_stamp}.json"
    md_path = output_dir / f"public_offer_pack_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_pack(
    manifest_path: Path = DEFAULT_MANIFEST,
    feedback_file: Path | None = None,
    zip_path: Path | None = None,
    offer_headline: str = "",
    offer_subheadline: str = "",
    faq_ready: bool = False,
    release_notes_ready: bool = False,
    buyer_steps_ready: bool = False,
    support_copy_ready: bool = False,
    safe_claims_reviewed: bool = False,
    checkout_ready: bool = False,
    public_page_ready: bool = False,
    allow_no_go_feedback: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    feedback = load_json(feedback_file) if feedback_file else None
    final_zip = zip_path or latest_portable_zip()
    screenshots = screenshot_count()
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "feedback_source": str(feedback_file) if feedback_file else "",
        "feedback_decision": feedback.get("decision") if feedback else None,
        "zip_path": str(final_zip) if final_zip else "",
        "screenshot_count": screenshots,
        "offer_headline": offer_headline,
        "offer_subheadline": offer_subheadline,
        "offer_audience": manifest.get("marketing", {}).get("audience", ""),
        "offer_promise": manifest.get("marketing", {}).get("promise", ""),
        "offer_sections": offer_sections(),
        "buyer_steps": buyer_steps(),
        "faq_ready": faq_ready,
        "release_notes_ready": release_notes_ready,
        "buyer_steps_ready": buyer_steps_ready,
        "support_copy_ready": support_copy_ready,
        "safe_claims_reviewed": safe_claims_reviewed,
        "checkout_ready": checkout_ready,
        "public_page_ready": public_page_ready,
        "decision": decision_from(
            feedback,
            final_zip,
            screenshots,
            offer_headline,
            offer_subheadline,
            faq_ready,
            release_notes_ready,
            buyer_steps_ready,
            support_copy_ready,
            safe_claims_reviewed,
            checkout_ready,
            public_page_ready,
            allow_no_go_feedback,
        ),
    }
    if write:
        report["evidence_paths"] = write_pack(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge public offer pack")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--feedback-file", default="")
    parser.add_argument("--use-latest-feedback", action="store_true")
    parser.add_argument("--zip", default="")
    parser.add_argument("--offer-headline", default=env_value("SQX_OFFER_HEADLINE"))
    parser.add_argument("--offer-subheadline", default=env_value("SQX_OFFER_SUBHEADLINE"))
    parser.add_argument("--confirm-faq-ready", action="store_true")
    parser.add_argument("--confirm-release-notes-ready", action="store_true")
    parser.add_argument("--confirm-buyer-steps-ready", action="store_true")
    parser.add_argument("--confirm-support-copy-ready", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-checkout-ready", action="store_true")
    parser.add_argument("--confirm-public-page-ready", action="store_true")
    parser.add_argument("--allow-no-go-feedback", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    feedback_file = Path(args.feedback_file) if args.feedback_file else None
    if args.use_latest_feedback and feedback_file is None:
        feedback_file = latest_feedback_file()
        if feedback_file is None:
            print(json.dumps({"ok": False, "error": "commercial_feedback_loop_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_pack(
        manifest_path=Path(args.manifest),
        feedback_file=feedback_file,
        zip_path=Path(args.zip) if args.zip else None,
        offer_headline=args.offer_headline,
        offer_subheadline=args.offer_subheadline,
        faq_ready=args.confirm_faq_ready,
        release_notes_ready=args.confirm_release_notes_ready,
        buyer_steps_ready=args.confirm_buyer_steps_ready,
        support_copy_ready=args.confirm_support_copy_ready,
        safe_claims_reviewed=args.confirm_safe_claims_reviewed,
        checkout_ready=args.confirm_checkout_ready,
        public_page_ready=args.confirm_public_page_ready,
        allow_no_go_feedback=args.allow_no_go_feedback,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
