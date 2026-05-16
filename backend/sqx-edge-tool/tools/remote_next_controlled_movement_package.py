from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.remote_next_controlled_movement_package import (
    DEFAULT_REMOTE8H_EVIDENCE_PATH,
    DEFAULT_REMOTE8H_OUTPUT_ROOT,
    ingest_remote8h_next_controlled_movement_package,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a redacted REMOTE-8H next controlled movement package.")
    parser.add_argument(
        "--evidence",
        default=str(DEFAULT_REMOTE8H_EVIDENCE_PATH),
        help="Ignored local REMOTE-8H next controlled movement package JSON.",
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_REMOTE8H_OUTPUT_ROOT),
        help="Ignored local output folder for the redacted movement package summary.",
    )
    args = parser.parse_args()

    result = ingest_remote8h_next_controlled_movement_package(
        evidence_path=args.evidence,
        output_root=args.out_dir,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
