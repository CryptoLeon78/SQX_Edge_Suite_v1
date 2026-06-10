from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.remote_pilot import DEFAULT_REMOTE8_ROOT, run_controlled_pilot_drill


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local-only REMOTE-8 controlled pilot drill.")
    parser.add_argument("--base-dir", default=str(DEFAULT_REMOTE8_ROOT), help="Ignored local output root for evidence.")
    parser.add_argument("--run-id", default="", help="Optional deterministic run id for tests or private evidence.")
    parser.add_argument("--pilot-email", default="remote8-buyer@example.invalid", help="Synthetic pilot email for local-only drill.")
    parser.add_argument("--second-email", default="remote8-second@example.invalid", help="Synthetic second email for isolation check.")
    args = parser.parse_args()

    result = run_controlled_pilot_drill(
        base_dir=args.base_dir,
        run_id=args.run_id or None,
        pilot_email=args.pilot_email,
        second_email=args.second_email,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
