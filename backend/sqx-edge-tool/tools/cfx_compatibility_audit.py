from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.cfx_compatibility import audit_many, render_markdown, to_json


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit SQX .cfx host/resource compatibility without mutating files."
    )
    parser.add_argument("paths", nargs="+", help="One or more .cfx files to inspect.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    args = parser.parse_args()

    paths = [Path(path) for path in args.paths]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        print(f"Missing .cfx file(s): {', '.join(missing)}", file=sys.stderr)
        return 2

    report = audit_many(paths)
    print(to_json(report) if args.json else render_markdown(report))
    return 1 if report["failCount"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
