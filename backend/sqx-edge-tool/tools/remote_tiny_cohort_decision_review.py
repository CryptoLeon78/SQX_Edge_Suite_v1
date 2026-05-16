from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.remote_tiny_cohort_decision_review import (
    DEFAULT_REMOTE8G_EVIDENCE_PATH,
    DEFAULT_REMOTE8G_OUTPUT_ROOT,
    ingest_remote8g_tiny_cohort_decision_review,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a redacted REMOTE-8G tiny cohort decision review.")
    parser.add_argument(
        "--evidence",
        default=str(DEFAULT_REMOTE8G_EVIDENCE_PATH),
        help="Ignored local REMOTE-8G tiny cohort decision review JSON.",
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_REMOTE8G_OUTPUT_ROOT),
        help="Ignored local output folder for the redacted decision review summary.",
    )
    args = parser.parse_args()

    result = ingest_remote8g_tiny_cohort_decision_review(
        evidence_path=args.evidence,
        output_root=args.out_dir,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
