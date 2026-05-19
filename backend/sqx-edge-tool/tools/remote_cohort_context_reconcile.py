from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.remote_cohort_context_reconcile import (
    build_remote_cohort_context_reconcile,
    write_remote_cohort_context_reconcile,
)


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.parents[1].resolve())).replace("\\", "/")
    except ValueError:
        return ".local/remote_service/remote_cohort_matrix/remote_cohort_context_reconcile.local.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the SQX remote cohort anti-sharing reconciliation plan.")
    parser.add_argument("--aliases", default="", help="Optional local user_aliases.local.json path.")
    parser.add_argument("--entitlements", default="", help="Optional remote_entitlements.local.json path.")
    parser.add_argument("--access-control", default="", help="Optional remote_access_control.local.json path.")
    parser.add_argument("--support-cases", default="", help="Optional support_cases.local.jsonl path.")
    parser.add_argument("--download-smoke", default="", help="Optional cohort download smoke evidence path.")
    parser.add_argument("--scope", default="", help="Optional cohort monitoring scope evidence path.")
    parser.add_argument("--out", default="", help="Optional output path for the local reconciliation JSON.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args()

    payload = build_remote_cohort_context_reconcile(
        aliases_path=args.aliases or None,
        entitlements_path=args.entitlements or None,
        access_control_path=args.access_control or None,
        support_cases_path=args.support_cases or None,
        download_smoke_path=args.download_smoke or None,
        scope_path=args.scope or None,
    )
    output_path = write_remote_cohort_context_reconcile(payload, args.out or None)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    summary = payload["summary"]
    print("SQX Edge Suite REMOTE cohort anti-sharing reconciliation")
    print(f"Schema: {payload['schemaVersion']}")
    print(f"Active aliases: {summary['activeAliasCount']}")
    print(f"Ready aliases: {summary['readyAliasCount']}")
    print(f"Needs action: {summary['needsActionCount']}")
    print(f"Recapture required: {summary['recaptureRequiredCount']}")
    print(f"Operator review required: {summary['operatorReviewRequiredCount']}")
    print(f"Repeat smoke required: {summary['repeatSmokeRequiredCount']}")
    for item in payload["actions"]:
        if item["action"] == "none":
            continue
        print(f"- {item['alias']}: {item['action']} ({item['reason']})")
    print(f"Local reconciliation written: {_display_path(output_path)}")
    print("Privacy: alias-only, no emails/IPs/protected URLs/tokens/local paths.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
