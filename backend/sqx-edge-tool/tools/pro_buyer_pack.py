from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "pro_buyer_pack.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "pro_buyer_pack"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def rel_path(path: str) -> Path:
    return PROJECT_ROOT / path


def csv_headers(path: Path, delimiter: str) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        return next(reader, [])


def csv_row_count(path: Path, delimiter: str) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        return sum(1 for _row in reader)


def forbidden_hits(text: str, forbidden: list[str]) -> list[str]:
    lower = text.lower()
    return [item for item in forbidden if item.lower() in lower]


def validate_pack(config_path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    config = load_json(config_path)
    findings: list[str] = []
    checked_files: list[str] = []
    required_files = config.get("requiredFiles") if isinstance(config.get("requiredFiles"), list) else []
    forbidden = config.get("forbiddenClaims") if isinstance(config.get("forbiddenClaims"), list) else []

    for item in required_files:
        path = rel_path(str(item))
        if not path.is_file():
            findings.append(f"missing_required_file:{item}")
            continue
        checked_files.append(str(item))
        hits = forbidden_hits(read_text(path), forbidden)
        for hit in hits:
            findings.append(f"forbidden_claim:{item}:{hit}")

    contracts = config.get("csvContracts") if isinstance(config.get("csvContracts"), dict) else {}
    delimiter = contracts.get("strategyImportDelimiter", ";")
    strategy_csv = rel_path("resources/pro-buyer-pack/data/strategy_import_template.csv")
    asset_csv = rel_path("resources/pro-buyer-pack/data/asset_universe_pro.csv")

    if strategy_csv.is_file():
        headers = csv_headers(strategy_csv, delimiter)
        for column in contracts.get("strategyImportRequiredColumns", []):
            if column not in headers:
                findings.append(f"strategy_csv_missing_column:{column}")
        if csv_row_count(strategy_csv, delimiter) < 3:
            findings.append("strategy_csv_needs_three_demo_rows")

    if asset_csv.is_file():
        headers = csv_headers(asset_csv, ",")
        for column in contracts.get("assetUniverseRequiredColumns", []):
            if column not in headers:
                findings.append(f"asset_csv_missing_column:{column}")
        if csv_row_count(asset_csv, ",") != 33:
            findings.append("asset_universe_must_have_33_rows")

    return {
        "ok": not findings,
        "state": config.get("state", "pro_buyer_pack_ready"),
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "resource_dir": config.get("resourceDir"),
        "included_in_portable": bool(config.get("includedInPortable")),
        "checked_files": checked_files,
        "findings": findings,
        "decision": "GO" if not findings else "NO-GO",
    }


def write_evidence(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"pro_buyer_pack_{stamp}.json"
    md_path = output_dir / f"pro_buyer_pack_{stamp}.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    md_lines = [
        "# Pro Buyer Pack Evidence",
        "",
        f"- State: `{result['state']}`",
        f"- Decision: `{result['decision']}`",
        f"- Included in portable: `{result['included_in_portable']}`",
        f"- Files checked: {len(result['checked_files'])}",
        "",
        "## Findings",
        "",
    ]
    if result["findings"]:
        md_lines.extend(f"- {finding}" for finding in result["findings"])
    else:
        md_lines.append("- None.")
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the SQX Edge Pro buyer data/template pack.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    result = validate_pack(Path(args.config))
    if not args.no_write:
        result["evidence"] = write_evidence(result, Path(args.output_dir))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
