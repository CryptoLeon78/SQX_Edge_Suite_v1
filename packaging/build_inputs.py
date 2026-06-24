"""
build_inputs.py — Prepare and harden the buyer manifest for the Nuitka build.

Usage:
    python packaging/build_inputs.py [--staging-dir STAGING_DIR]

Reads backend/sqx-edge-tool/config/product_manifest.json, applies
harden_buyer_manifest() from core.build_hardening, and writes the hardened
copy to STAGING_DIR/product_manifest.json.

Exit codes:
  0  — hardened manifest written successfully
  2  — H2 blocker: placeholder public key detected (BuyerBuildError)
  1  — any other error
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOL_ROOT = PROJECT_ROOT / "backend" / "sqx-edge-tool"

if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.build_hardening import BuyerBuildError, harden_buyer_manifest  # noqa: E402

MANIFEST_SRC = TOOL_ROOT / "config" / "product_manifest.json"


def run(staging_dir: Path) -> int:
    """Harden the manifest and write it to staging_dir. Returns exit code."""
    raw = json.loads(MANIFEST_SRC.read_text(encoding="utf-8"))
    try:
        hardened = harden_buyer_manifest(raw)
    except BuyerBuildError as exc:
        print(f"[H2] Buyer build blocked — {exc}", file=sys.stderr)
        return 2

    staging_dir.mkdir(parents=True, exist_ok=True)
    out = staging_dir / "product_manifest.json"
    out.write_text(json.dumps(hardened, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Hardened manifest written to {out}")
    print(f"  build.channel        = {hardened['build']['channel']!r}")
    print(f"  publicKey.kid        = {hardened['licensing']['publicKey']['kid']!r}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Harden product_manifest.json for buyer builds.")
    parser.add_argument(
        "--staging-dir",
        default=str(PROJECT_ROOT / "dist" / "nuitka_staging"),
        help="Directory to write the hardened manifest (default: dist/nuitka_staging)",
    )
    args = parser.parse_args()
    sys.exit(run(Path(args.staging_dir)))


if __name__ == "__main__":
    main()
