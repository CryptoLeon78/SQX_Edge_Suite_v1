from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.support_incidents import (
    DEFAULT_SUPPORT_CASES_PATH,
    summarize_support_incidents,
    update_support_incident_status,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize local redacted support incident cases.")
    parser.add_argument(
        "--cases",
        default=str(DEFAULT_SUPPORT_CASES_PATH),
        help="Ignored local support cases JSONL file.",
    )
    parser.add_argument("--set-status-case", default="", help="Case id to update before summarizing.")
    parser.add_argument("--status", default="", help="New status: open, triaged, resolved or dismissed.")
    parser.add_argument("--note", default="", help="Optional redacted operator note for the status update.")
    args = parser.parse_args()
    if args.set_status_case:
        update = update_support_incident_status(
            args.set_status_case.strip(),
            args.status.strip(),
            path=args.cases,
            note=args.note,
        )
        if not update.get("ok"):
            print(json.dumps(update, indent=2, sort_keys=True))
            return 2
    summary = summarize_support_incidents(args.cases)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
