from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.remote_ops1_laptop_readiness import ingest_remote_ops1_laptop_readiness


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a redacted REMOTE-OPS1 laptop readiness drill.")
    parser.add_argument("--evidence", type=Path, default=None, help="Ignored local REMOTE-OPS1 evidence JSON path.")
    parser.add_argument("--out-dir", type=Path, default=None, help="Output directory for the public-safe summary.")
    args = parser.parse_args()

    result = ingest_remote_ops1_laptop_readiness(evidence_path=args.evidence, output_root=args.out_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
