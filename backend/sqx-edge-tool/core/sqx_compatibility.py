from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


SQX142_DEFAULT_ROOT = Path(os.environ.get("SQX142_ROOT", r"C:\BOTS\Versiones\SQX_142_Crack"))
SQX143_DEFAULT_ROOT = Path(os.environ.get("SQX143_ROOT", r"C:\BOTS\Versiones\SQX_143\SQX_143"))
PROCESS_NAME_RE = re.compile(r"StrategyQuant|sqcli|CodeEditor|javaw?|electron|SQUANT", re.IGNORECASE)


def _read_text(path: Path, limit: int = 200_000) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")[:limit]
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="replace")[:limit]
    except OSError:
        return ""


def _option_lines(root: Path) -> list[str]:
    config = root / "StrategyQuantX_nocheck.config"
    return [line.strip() for line in _read_text(config).splitlines() if line.strip()]


def _java_identity(root: Path) -> dict[str, Any]:
    java = root / "j64" / "bin" / "java.exe"
    release = root / "j64" / "release"
    readme = root / "j64" / "readme.txt"
    data: dict[str, Any] = {
        "exists": java.is_file(),
        "vendor": "",
        "version": "",
        "runtime": "",
        "label": "missing",
    }
    release_text = _read_text(release)
    if release_text:
        values = {}
        for line in release_text.splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"')
        data["vendor"] = values.get("IMPLEMENTOR", "")
        data["version"] = values.get("JAVA_VERSION", "")
        data["runtime"] = values.get("JAVA_RUNTIME_VERSION", "")
        data["label"] = " ".join(part for part in [data["vendor"], data["version"]] if part).strip() or "java"
        return data
    readme_text = _read_text(readme)
    match = re.search(r"\b(Zulu\s+[\w.+-]+)", readme_text)
    if match:
        label = match.group(1)
        major = re.search(r"Zulu\s+(\d+)", label)
        data["vendor"] = "Azul Zulu"
        data["version"] = major.group(1) if major else ""
        data["runtime"] = label
        data["label"] = label
    return data


def _process_snapshot(include_paths: bool = False) -> list[dict[str, Any]]:
    if os.name != "nt":
        return []
    script = (
        "Get-CimInstance Win32_Process | "
        "Where-Object { $_.Name -match 'StrategyQuant|sqcli|CodeEditor|javaw?|electron|SQUANT' } | "
        "Select-Object Name,ProcessId,CommandLine | ConvertTo-Json -Compress"
    )
    try:
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    raw = (proc.stdout or "").strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    items = parsed if isinstance(parsed, list) else [parsed]
    result = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("Name") or "")
        if not PROCESS_NAME_RE.search(name):
            continue
        row = {"name": name, "pid": item.get("ProcessId")}
        if include_paths:
            row["commandLine"] = str(item.get("CommandLine") or "")
        result.append(row)
    return result


def build_sqx142_status(
    sqx142_root: Path | None = None,
    sqx143_root: Path | None = None,
    *,
    include_paths: bool = False,
) -> dict[str, Any]:
    root142 = Path(sqx142_root or SQX142_DEFAULT_ROOT)
    root143 = Path(sqx143_root or SQX143_DEFAULT_ROOT)
    options142 = _option_lines(root142)
    options143 = _option_lines(root143)
    java142 = _java_identity(root142)
    java143 = _java_identity(root143)
    processes = _process_snapshot(include_paths=include_paths)
    xmx_flags = [line for line in options142 if "-Xmx" in line]
    has_native_access = any("--enable-native-access=ALL-UNNAMED" in line for line in options142)
    java_aligned = bool(java142.get("version") and java142.get("version") == java143.get("version"))
    blockers = []
    if not root142.is_dir():
        blockers.append("sqx142_root_missing")
    if not root143.is_dir():
        blockers.append("sqx143_reference_missing")
    if processes:
        blockers.append("sqx_processes_running")
    if not java_aligned:
        blockers.append("java_runtime_mismatch")
    if xmx_flags:
        blockers.append("legacy_xmx_override_present")
    if not has_native_access:
        blockers.append("native_access_flag_missing")
    status = "ok" if not blockers else ("blocked" if "sqx_processes_running" in blockers else "needs_hardening")
    result: dict[str, Any] = {
        "version": "sqx142-compat-status-v1",
        "ok": status == "ok",
        "status": status,
        "roots": {
            "sqx142Exists": root142.is_dir(),
            "sqx143ReferenceExists": root143.is_dir(),
        },
        "java": {
            "active": java142,
            "reference": java143,
            "alignedWith143": java_aligned,
        },
        "config": {
            "activeOptionCount": len(options142),
            "referenceOptionCount": len(options143),
            "hasNativeAccess": has_native_access,
            "xmxFlags": xmx_flags if include_paths else [flag.replace(str(root142), "[SQX142]") for flag in xmx_flags],
            "uses143OptionShape": options142 == options143,
        },
        "processes": {
            "count": len(processes),
            "running": bool(processes),
            "items": processes[:20],
        },
        "blockers": blockers,
        "recommendation": recommendation_for_status(blockers),
        "privacy": {"local_paths_returned": include_paths},
    }
    if include_paths:
        result["roots"]["sqx142Root"] = str(root142)
        result["roots"]["sqx143Root"] = str(root143)
    return result


def recommendation_for_status(blockers: list[str]) -> str:
    if "sqx_processes_running" in blockers:
        return "Cierra SQX 142 antes de aplicar runtime/config o limpiar cache."
    if "java_runtime_mismatch" in blockers:
        return "Alinear 142 con el runtime Java/Zulu 22 de la build 143 y validar con smoke."
    if "legacy_xmx_override_present" in blockers or "native_access_flag_missing" in blockers:
        return "Aplicar la forma de config de 143 y retirar el override -Xmx legado."
    if blockers:
        return "Completar preflight y revisar el ledger antes de tocar archivos."
    return "SQX 142 esta alineado con la referencia 143 para la capa runtime/config."

