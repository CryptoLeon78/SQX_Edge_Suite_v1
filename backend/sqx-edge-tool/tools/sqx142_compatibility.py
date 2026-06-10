from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.sqx_compatibility import (  # noqa: E402
    SQX142_DEFAULT_ROOT,
    SQX143_DEFAULT_ROOT,
    build_sqx142_status,
)


RUNTIME_CONFIG_FILES = ("StrategyQuantX_nocheck.config", "sqcli.config", "CodeEditor.config")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def json_print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def rel_hashes(base: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    if not base.is_dir():
        return result
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(base)).replace("/", "\\")
        try:
            result[rel] = {"hash": sha256(path), "length": path.stat().st_size}
        except OSError as exc:
            result[rel] = {"hash": "", "length": 0, "error": type(exc).__name__}
    return result


def compare_area(root142: Path, root143: Path, area: str) -> dict[str, Any]:
    base142 = root142 / area
    base143 = root143 / area
    hashes142 = rel_hashes(base142)
    hashes143 = rel_hashes(base143)
    only143 = sorted(set(hashes143) - set(hashes142))
    only142 = sorted(set(hashes142) - set(hashes143))
    changed = sorted(
        rel for rel in set(hashes142).intersection(hashes143)
        if hashes142[rel].get("hash") != hashes143[rel].get("hash")
    )
    return {
        "area": area,
        "files142": len(hashes142),
        "files143": len(hashes143),
        "only143": only143,
        "only142": only142,
        "changed": changed,
        "counts": {"only143": len(only143), "only142": len(only142), "changed": len(changed)},
    }


def close_sqx142_processes(root142: Path, *, apply: bool) -> dict[str, Any]:
    if os.name != "nt":
        return {"attempted": False, "reason": "non_windows"}
    root = str(root142).replace("'", "''")
    script = (
        "$root='" + root + "'; "
        "$procs = Get-CimInstance Win32_Process | Where-Object { "
        "$_.CommandLine -and $_.CommandLine -like ('*' + $root + '*') -and "
        "$_.Name -match 'StrategyQuant|sqcli|CodeEditor|javaw?|electron|SQUANT' }; "
        "$rows = @($procs | Select-Object Name,ProcessId); "
        "if ($env:SQX_COMPAT_APPLY -eq '1') { "
        "$rows | ForEach-Object { Stop-Process -Id $_.ProcessId -ErrorAction SilentlyContinue }; "
        "Start-Sleep -Seconds 2; "
        "$left = @(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -like ('*' + $root + '*') -and $_.Name -match 'StrategyQuant|sqcli|CodeEditor|javaw?|electron|SQUANT' }); "
        "$left | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }; "
        "} "
        "$rows | ConvertTo-Json -Compress"
    )
    env = os.environ.copy()
    env["SQX_COMPAT_APPLY"] = "1" if apply else "0"
    proc = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        env=env,
    )
    raw = (proc.stdout or "").strip()
    try:
        parsed = json.loads(raw) if raw else []
    except json.JSONDecodeError:
        parsed = []
    if isinstance(parsed, dict):
        parsed = [parsed]
    return {
        "attempted": True,
        "apply": apply,
        "matched": parsed,
        "count": len(parsed) if isinstance(parsed, list) else 0,
        "stderr": (proc.stderr or "").strip()[:500],
    }


def copy_file_backup(source: Path, backup_dir: Path, relative_name: str, *, apply: bool) -> dict[str, Any]:
    target = backup_dir / relative_name
    if not source.exists():
        return {"source": relative_name, "copied": False, "reason": "missing"}
    if apply:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return {"source": relative_name, "copied": apply, "bytes": source.stat().st_size}


def runtime_config_text(root143: Path) -> str:
    source = root143 / "StrategyQuantX_nocheck.config"
    if source.is_file():
        text = source.read_text(encoding="utf-8-sig").strip()
    else:
        text = "\n".join([
            "option -Djava.net.useSystemProxies=true",
            "option -Djava.net.preferIPv4Stack=true",
            "option -XX:+UseParallelGC",
            "option -Djdk.tls.trustNameService=true",
            "option --enable-native-access=ALL-UNNAMED",
            "option -Xms4g",
        ])
    return text + "\n"


def apply_runtime_hardening(
    root142: Path,
    root143: Path,
    *,
    apply: bool,
    close_processes: bool,
    copy_runtime: bool,
) -> dict[str, Any]:
    backup_root = root142.parent / "SQX142_ROOT_local_backups" / f"sqx142_compat_before_{stamp()}"
    before = build_sqx142_status(root142, root143, include_paths=True)
    close_result = close_sqx142_processes(root142, apply=apply) if close_processes else {"attempted": False, "reason": "not_requested"}
    after_close = build_sqx142_status(root142, root143, include_paths=True)
    if after_close["processes"]["running"] and apply:
        return {
            "ok": False,
            "dryRun": not apply,
            "error": "sqx_processes_still_running",
            "before": before,
            "close": close_result,
            "afterClose": after_close,
        }

    actions: list[dict[str, Any]] = []
    if apply:
        backup_root.mkdir(parents=True, exist_ok=True)
    for name in RUNTIME_CONFIG_FILES:
        actions.append(copy_file_backup(root142 / name, backup_root, name, apply=apply))

    desired_config = runtime_config_text(root143)
    for name in RUNTIME_CONFIG_FILES:
        target = root142 / name
        actions.append({"action": "write_runtime_config", "target": name, "apply": apply})
        if apply:
            target.write_text(desired_config, encoding="utf-8")

    if copy_runtime:
        source_j64 = root143 / "j64"
        active_j64 = root142 / "j64"
        backup_j64 = backup_root / "j64_before_runtime_backport"
        actions.append({
            "action": "replace_j64_runtime",
            "source": "SQX_143 j64",
            "target": "SQX_142 j64",
            "backup": "j64_before_runtime_backport",
            "apply": apply,
        })
        if apply and source_j64.is_dir():
            if active_j64.exists():
                shutil.move(str(active_j64), str(backup_j64))
            try:
                shutil.copytree(source_j64, active_j64)
            except Exception:
                if not active_j64.exists() and backup_j64.exists():
                    shutil.move(str(backup_j64), str(active_j64))
                raise

    after = build_sqx142_status(root142, root143, include_paths=True)
    return {
        "ok": True,
        "dryRun": not apply,
        "backupRoot": str(backup_root) if apply else str(backup_root) + " (planned)",
        "before": before,
        "close": close_result,
        "actions": actions,
        "after": after,
    }


def write_optional(payload: dict[str, Any], out_file: Path | None) -> None:
    if not out_file:
        return
    out_file.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_file.with_suffix(out_file.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_file)


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX 142/143 compatibility maintenance. Dry-run by default.")
    parser.add_argument("--sqx142-root", type=Path, default=SQX142_DEFAULT_ROOT)
    parser.add_argument("--sqx143-root", type=Path, default=SQX143_DEFAULT_ROOT)
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status")
    status.add_argument("--include-paths", action="store_true")

    compare = sub.add_parser("compare")
    compare.add_argument("--area", action="append", default=["internal\\extend"])
    compare.add_argument("--out", type=Path)

    preflight = sub.add_parser("preflight")
    preflight.add_argument("--apply-close", action="store_true")

    runtime = sub.add_parser("apply-runtime")
    runtime.add_argument("--apply", action="store_true", help="Actually modify SQX 142. Omit for dry-run.")
    runtime.add_argument("--close-processes", action="store_true")
    runtime.add_argument("--skip-runtime-copy", action="store_true")

    args = parser.parse_args()
    root142 = args.sqx142_root
    root143 = args.sqx143_root

    if args.command == "status":
        json_print(build_sqx142_status(root142, root143, include_paths=args.include_paths))
        return 0
    if args.command == "compare":
        payload = {
            "version": "sqx142-143-compare-v1",
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "areas": [compare_area(root142, root143, area) for area in args.area],
        }
        write_optional(payload, args.out)
        json_print(payload)
        return 0
    if args.command == "preflight":
        payload = {
            "version": "sqx142-preflight-v1",
            "status": build_sqx142_status(root142, root143, include_paths=True),
            "close": close_sqx142_processes(root142, apply=args.apply_close),
        }
        payload["statusAfterClose"] = build_sqx142_status(root142, root143, include_paths=True)
        json_print(payload)
        return 0
    if args.command == "apply-runtime":
        payload = apply_runtime_hardening(
            root142,
            root143,
            apply=args.apply,
            close_processes=args.close_processes,
            copy_runtime=not args.skip_runtime_copy,
        )
        json_print(payload)
        return 0 if payload.get("ok") else 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
