from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .sqx_compatibility import SQX142_DEFAULT_ROOT, SQX143_DEFAULT_ROOT, build_sqx142_status


PERFORMANCE_VERSION = "sqx142-performance-status-v1"
EVIDENCE_DIRNAME = ".local/sqx142_performance"
DISK_RECOMMENDED_FREE_BYTES = 100 * 1024**3
DISK_CRITICAL_FREE_BYTES = 60 * 1024**3
RUNTIME_CONFIG_FILES = ("StrategyQuantX_nocheck.config", "sqcli.config", "CodeEditor.config")

PROFILE_CONFIGS: dict[str, dict[str, Any]] = {
    "baseline_143_safe": {
        "label": "Baseline 143 Safe",
        "description": "Build 143 runtime/config shape. Stable default before performance experiments.",
        "lines": [
            "option -Djava.net.useSystemProxies=true",
            "option -Djava.net.preferIPv4Stack=true",
            "option -XX:+UseParallelGC",
            "option -Djdk.tls.trustNameService=true",
            "option --enable-native-access=ALL-UNNAMED",
            "option -Xms4g",
        ],
    },
    "mining_fast_safe": {
        "label": "Mining Fast Safe",
        "description": "Bounded heap for long mining bursts on the operator workstation; quality rules unchanged.",
        "lines": [
            "option -Djava.net.useSystemProxies=true",
            "option -Djava.net.preferIPv4Stack=true",
            "option -XX:+UseParallelGC",
            "option -Djdk.tls.trustNameService=true",
            "option --enable-native-access=ALL-UNNAMED",
            "option -Xms8g",
            "option -Xmx48g",
        ],
    },
    "retest_robust": {
        "label": "Retest Robust",
        "description": "Conservative bounded heap for MonteCarlo/Synthetic/WFM stability.",
        "lines": [
            "option -Djava.net.useSystemProxies=true",
            "option -Djava.net.preferIPv4Stack=true",
            "option -XX:+UseParallelGC",
            "option -Djdk.tls.trustNameService=true",
            "option --enable-native-access=ALL-UNNAMED",
            "option -Xms4g",
            "option -Xmx32g",
        ],
    },
    "diagnostic_low_risk": {
        "label": "Diagnostic Low Risk",
        "description": "Lower bounded heap for UI diagnostics and smoke runs.",
        "lines": [
            "option -Djava.net.useSystemProxies=true",
            "option -Djava.net.preferIPv4Stack=true",
            "option -XX:+UseParallelGC",
            "option -Djdk.tls.trustNameService=true",
            "option --enable-native-access=ALL-UNNAMED",
            "option -Xms2g",
            "option -Xmx16g",
        ],
    },
}

VIEW_COLUMN_ATTRS = 'sampleType="127" direction="0" plType="10" resultType="main" confidenceLevel="50" market="1" subresult="30" showMainResult="true"'
PERFORMANCE_VIEWS: dict[str, list[tuple[str, str]]] = {
    "MINING FAST REVIEW": [
        ("Symbol", "Symbol"),
        ("TimeFrame", "TimeFrame"),
        ("Fitness", "Fitness"),
        ("NumberOfTrades", "# of trades"),
        ("NetProfit", "Net profit"),
        ("DrawdownPct", "Max DD %"),
        ("ReturnDDRatio", "Ret/DD Ratio"),
        ("ProfitFactor", "Profit factor"),
        ("AvgTradesPerMonth", "Avg. Trades Per Month"),
        ("MaxConsecLosses", "Max Consec. Losses"),
        ("Stagnation", "Stagnation"),
    ],
    "RETEST QUICK REVIEW": [
        ("Symbol", "Symbol"),
        ("TimeFrame", "TimeFrame"),
        ("Fitness", "Fitness"),
        ("NumberOfTrades", "# of trades"),
        ("NetProfit", "Net profit"),
        ("DrawdownPct", "Max DD %"),
        ("Drawdown", "Drawdown"),
        ("ReturnDDRatio", "Ret/DD Ratio"),
        ("ProfitFactor", "Profit factor"),
        ("SharpeRatio", "Sharpe Ratio"),
        ("MaxNewHighDuration", "Max DD Duration"),
    ],
    "RETEST ROBUST REVIEW": [
        ("Symbol", "Symbol"),
        ("TimeFrame", "TimeFrame"),
        ("Fitness", "Fitness"),
        ("SQNScore", "SQN Score"),
        ("SortinoRatio", "Sortino Ratio"),
        ("CVaR_Hobbiecode", "CVaR (95%)"),
        ("NumberOfTrades", "# of trades"),
        ("NetProfit", "Net profit"),
        ("DrawdownPct", "Max DD %"),
        ("Drawdown", "Drawdown"),
        ("ReturnDDRatio", "Ret/DD Ratio"),
        ("ProfitFactor", "Profit factor"),
        ("SharpeRatio", "Sharpe Ratio"),
        ("AnnualPctReturnDDRatio", "CAGR/Max DD %"),
        ("Stagnation", "Stagnation"),
        ("MaxConsecLosses", "Max Consec. Losses"),
    ],
    "FINAL DECISION FULL": [
        ("Symbol", "Symbol"),
        ("TimeFrame", "TimeFrame"),
        ("MiniEquityChart", "Mini equity chart"),
        ("Fitness", "Fitness"),
        ("SQNScore", "SQN Score"),
        ("SortinoRatio", "Sortino Ratio"),
        ("CVaR_Hobbiecode", "CVaR (95%)"),
        ("NumberOfTrades", "# of trades"),
        ("NetProfit", "Net profit"),
        ("DrawdownPct", "Max DD %"),
        ("Drawdown", "Drawdown"),
        ("ReturnDDRatio", "Ret/DD Ratio"),
        ("ProfitFactor", "Profit factor"),
        ("SharpeRatio", "Sharpe Ratio"),
        ("AnnualPctReturnDDRatio", "CAGR/Max DD %"),
        ("AvgTradesPerMonth", "Avg. Trades Per Month"),
        ("Stagnation", "Stagnation"),
        ("MaxConsecLosses", "Max Consec. Losses"),
        ("EntryIndicators", "Entry indicators"),
        ("ExitIndicators", "Exit indicators"),
        ("PriceIndicators", "Price indicators"),
    ],
}

PERFORMANCE_REQUIRED_EVIDENCE_PREFIXES = (
    "profile_compare",
    "mining_pipeline_advisor",
    "mc_project_views",
    "phase5_databank_view_guard",
    "old_log_archive",
    "sequential_final_review",
    "mc2_spread_promotion",
    "queue_task_smoke",
    "performance_clone_hygiene",
    "performance_parallelism_advisor",
    "performance_live_guard",
    "performance_closeout_report",
)

PERFORMANCE_RECOMMENDATION_COMMANDS = {
    "profile_compare": "tools\\sqx142_performance_gate.ps1 compare-profiles baseline_143_safe diagnostic_low_risk retest_robust mining_fast_safe --apply --wait-seconds 18 --restore-profile baseline_143_safe",
    "mining_pipeline_advisor": "tools\\sqx142_performance_gate.ps1 project-mining-pipeline-advisor",
    "mc_project_views": "tools\\sqx142_performance_gate.ps1 prepare-project-mc-views --apply",
    "phase5_databank_view_guard": "tools\\sqx142_performance_gate.ps1 phase5-databank-view-guard",
    "old_log_archive": "tools\\sqx142_performance_gate.ps1 archive-old-logs --keep-days 2 --apply",
    "sequential_final_review": "tools\\sqx142_performance_gate.ps1 sequential-final-review --latest --write-csv --apply",
    "mc2_spread_promotion": "tools\\sqx142_performance_gate.ps1 promote-mc2-spread-to-base --project-name \"Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1\" --min-multiplier 2 --max-multiplier 5",
    "queue_task_smoke": "tools\\sqx142_performance_gate.ps1 queue-task-smoke \"Sequential\" --project-name \"_PERFQ_SEQBATCH_POSTPROMO8_20260523_080012\" --apply --max-seconds 900",
    "performance_clone_hygiene": "tools\\sqx142_performance_gate.ps1 performance-clone-hygiene --keep-newest 2",
    "performance_parallelism_advisor": "tools\\sqx142_performance_gate.ps1 performance-parallelism-advisor",
    "performance_live_guard": "tools\\sqx142_performance_gate.ps1 live-guard",
    "performance_closeout_report": "tools\\sqx142_performance_gate.ps1 performance-closeout-report",
}

LIVE_GUARD_LOG_PATTERNS: dict[str, re.Pattern[str]] = {
    "engine_crash": re.compile(r"crashed unexpectedly|engine crashed|ui will be closed|fatal error", re.IGNORECASE),
    "out_of_memory": re.compile(r"outofmemory|java heap space|gc overhead|unable to create native thread", re.IGNORECASE),
    "exception_or_error": re.compile(r"\b(exception|error|severe|fatal)\b", re.IGNORECASE),
    "api_access_blocked": re.compile(r"remote access disabled|access denied|forbidden", re.IGNORECASE),
}


def _read_text(path: Path, limit: int = 500_000) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")[:limit]
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="replace")[:limit]
    except OSError:
        return ""


def _config_lines(root: Path) -> list[str]:
    return [line.strip() for line in _read_text(root / "StrategyQuantX_nocheck.config").splitlines() if line.strip()]


def _profile_signature(lines: list[str]) -> list[str]:
    return sorted(line.strip() for line in lines if line.strip())


def _same_profile_lines(lines: list[str], profile_lines: list[str]) -> bool:
    return _profile_signature(lines) == _profile_signature(profile_lines)


def _config_file_health(root: Path, profile_lines: list[str]) -> dict[str, Any]:
    files: dict[str, Any] = {}
    corrupt = False
    mismatched = False
    for name in RUNTIME_CONFIG_FILES:
        path = root / name
        row: dict[str, Any] = {
            "exists": path.is_file(),
            "bytes": 0,
            "nulBytes": 0,
            "matchesActiveProfile": False,
            "exactOrderMatch": False,
        }
        try:
            data = path.read_bytes()
            row["bytes"] = len(data)
            row["nulBytes"] = data.count(b"\x00")
            text = data.decode("utf-8-sig", errors="replace")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            row["exactOrderMatch"] = lines == profile_lines
            row["matchesActiveProfile"] = _same_profile_lines(lines, profile_lines)
        except OSError:
            pass
        corrupt = corrupt or bool(row["nulBytes"])
        mismatched = mismatched or (row["exists"] and not row["matchesActiveProfile"])
        files[name] = row
    return {"files": files, "corrupt": corrupt, "mismatched": mismatched}


def active_profile(root: Path) -> dict[str, Any]:
    lines = _config_lines(root)
    normalized = [line.strip() for line in lines]
    for profile_id, profile in PROFILE_CONFIGS.items():
        if _same_profile_lines(normalized, profile["lines"]):
            return {
                "id": profile_id,
                "label": profile["label"],
                "description": profile["description"],
                "custom": False,
                "exactOrderMatch": normalized == profile["lines"],
            }
    xmx = [line for line in lines if "-Xmx" in line]
    xms = [line for line in lines if "-Xms" in line]
    return {
        "id": "custom",
        "label": "Custom",
        "description": "Config differs from the registered safe performance profiles.",
        "custom": True,
        "xmx": xmx,
        "xms": xms,
    }


def _format_bytes(value: int | float | None) -> str:
    if value is None:
        return ""
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} TB"


def _dir_stats(path: Path, *, max_files: int = 25_000) -> dict[str, Any]:
    stats = {"exists": path.exists(), "files": 0, "dirs": 0, "bytes": 0, "truncated": False}
    if not path.exists():
        stats["human"] = "missing"
        return stats
    try:
        for item in path.rglob("*"):
            try:
                if item.is_dir():
                    stats["dirs"] += 1
                    continue
                if item.is_file():
                    stats["files"] += 1
                    stats["bytes"] += item.stat().st_size
                    if stats["files"] >= max_files:
                        stats["truncated"] = True
                        break
            except OSError:
                continue
    except OSError:
        stats["truncated"] = True
    stats["human"] = _format_bytes(stats["bytes"])
    return stats


def _resource_snapshot(root: Path) -> dict[str, Any]:
    memory: dict[str, Any] = {}
    cpu: dict[str, Any] = {}
    if os.name == "nt":
        script = (
            "$os=Get-CimInstance Win32_OperatingSystem; "
            "$cpu=Get-CimInstance Win32_Processor | Select-Object -First 1; "
            "[pscustomobject]@{"
            "totalMem=$os.TotalVisibleMemorySize;freeMem=$os.FreePhysicalMemory;"
            "totalVirtual=$os.TotalVirtualMemorySize;freeVirtual=$os.FreeVirtualMemory;"
            "cpuName=$cpu.Name;cores=$cpu.NumberOfCores;logical=$cpu.NumberOfLogicalProcessors"
            "} | ConvertTo-Json -Compress"
        )
        try:
            proc = subprocess.run(["powershell.exe", "-NoProfile", "-Command", script], capture_output=True, text=True, timeout=5, check=False)
            parsed = json.loads((proc.stdout or "").strip() or "{}")
            memory = {
                "totalBytes": int(parsed.get("totalMem") or 0) * 1024,
                "freeBytes": int(parsed.get("freeMem") or 0) * 1024,
                "totalVirtualBytes": int(parsed.get("totalVirtual") or 0) * 1024,
                "freeVirtualBytes": int(parsed.get("freeVirtual") or 0) * 1024,
            }
            memory["freeHuman"] = _format_bytes(memory["freeBytes"])
            memory["totalHuman"] = _format_bytes(memory["totalBytes"])
            cpu = {
                "name": parsed.get("cpuName") or "",
                "coresPerSocket": parsed.get("cores"),
                "logicalPerSocket": parsed.get("logical"),
            }
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, ValueError):
            pass
    usage = shutil.disk_usage(root.anchor or str(root))
    disk = {
        "totalBytes": usage.total,
        "freeBytes": usage.free,
        "usedBytes": usage.used,
        "freeHuman": _format_bytes(usage.free),
        "totalHuman": _format_bytes(usage.total),
        "recommendedFreeBytes": DISK_RECOMMENDED_FREE_BYTES,
        "criticalFreeBytes": DISK_CRITICAL_FREE_BYTES,
        "state": "critical" if usage.free < DISK_CRITICAL_FREE_BYTES else ("warn" if usage.free < DISK_RECOMMENDED_FREE_BYTES else "ok"),
    }
    return {"cpu": cpu, "memory": memory, "disk": disk}


def _latest_evidence(project_root: Path) -> dict[str, Any]:
    evidence_root = project_root / EVIDENCE_DIRNAME
    if not evidence_root.is_dir():
        return {"exists": False}
    files = sorted(evidence_root.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not files:
        return {"exists": False}
    latest = files[0]
    return {
        "exists": True,
        "filename": latest.name,
        "modified": datetime.fromtimestamp(latest.stat().st_mtime).isoformat(timespec="seconds"),
        "localPathReturned": False,
    }


def _latest_evidence_file(project_root: Path, prefix: str) -> Path | None:
    evidence_root = project_root / EVIDENCE_DIRNAME
    if not evidence_root.is_dir():
        return None
    matches = sorted(evidence_root.glob(f"{prefix}_*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def _latest_evidence_brief(project_root: Path, prefix: str) -> dict[str, Any]:
    selected = _latest_evidence_file(project_root, prefix)
    if not selected or not selected.is_file():
        return {"prefix": prefix, "exists": False}
    result: dict[str, Any] = {
        "prefix": prefix,
        "exists": True,
        "filename": selected.name,
        "modified": datetime.fromtimestamp(selected.stat().st_mtime).isoformat(timespec="seconds"),
        "localPathReturned": False,
    }
    try:
        data = json.loads(selected.read_text(encoding="utf-8"))
        result["ok"] = bool(data.get("ok"))
        result["version"] = data.get("version", "")
        if isinstance(data.get("summary"), dict):
            result["summary"] = data["summary"]
        if isinstance(data.get("recommendation"), dict):
            recommendation = data["recommendation"]
            result["recommendation"] = {
                "id": recommendation.get("id", ""),
                "label": recommendation.get("label", ""),
                "requiresSQXClosed": bool(recommendation.get("requiresSQXClosed")),
            }
        if "completeEnoughForPerf1Closeout" in data:
            result["completeEnoughForPerf1Closeout"] = bool(data.get("completeEnoughForPerf1Closeout"))
        if isinstance(data.get("missingOrBadEvidence"), list):
            result["missingOrBadCount"] = len(data["missingOrBadEvidence"])
    except (OSError, json.JSONDecodeError):
        result["ok"] = False
        result["error"] = "unreadable_evidence"
    return result


def _view_presence(root: Path) -> dict[str, Any]:
    view_root = root / "user" / "settings" / "views" / "databanks"
    return {
        name: (view_root / f"{name}.vw").is_file()
        for name in PERFORMANCE_VIEWS
    }


def _performance_view_summary(views: dict[str, Any]) -> dict[str, Any]:
    performance_views = views.get("performanceViews") if isinstance(views.get("performanceViews"), dict) else {}
    monte_carlo_views = views.get("monteCarloViews") if isinstance(views.get("monteCarloViews"), dict) else {}
    expected: dict[str, bool] = {
        **{str(key): bool(value) for key, value in performance_views.items()},
        **{str(key): bool(value) for key, value in monte_carlo_views.items()},
    }
    missing = sorted(name for name, exists in expected.items() if not exists)
    return {
        "expectedCount": len(expected),
        "presentCount": len(expected) - len(missing),
        "missingCount": len(missing),
        "missing": missing,
        "ok": not missing,
    }


def _performance_recommendation(
    *,
    warnings: list[str],
    active_profile: str,
    missing_or_bad: list[str],
) -> dict[str, Any]:
    if "sqx_processes_running" in warnings:
        return {
            "id": "sqx_running_observe_only",
            "label": "SQX abierto: inteligencia en modo observacion",
            "command": "tools\\sqx142_performance_gate.ps1 status",
            "reason": "El monitor/agente pueden leer estado, pero no conviene tocar perfiles, views o cache mientras SQX este abierto.",
            "requiresSQXClosed": False,
            "requiresMethodologyDecision": False,
        }
    if warnings:
        return {
            "id": "fix_status_warnings",
            "label": "Resolver warnings del performance gate",
            "command": "tools\\sqx142_performance_gate.ps1 status --include-paths",
            "reason": "El status no esta limpio; primero hay que corregir los avisos activos.",
            "requiresSQXClosed": False,
            "requiresMethodologyDecision": False,
        }
    if active_profile != "baseline_143_safe":
        return {
            "id": "restore_baseline_profile",
            "label": "Restaurar perfil baseline_143_safe",
            "command": "tools\\sqx142_performance_gate.ps1 apply-profile baseline_143_safe --apply",
            "reason": "El perfil default debe quedar estable cuando no hay smoke activo.",
            "requiresSQXClosed": True,
            "requiresMethodologyDecision": False,
        }
    if missing_or_bad:
        first = missing_or_bad[0]
        return {
            "id": f"refresh_{first}",
            "label": f"Refrescar evidencia {first}",
            "command": PERFORMANCE_RECOMMENDATION_COMMANDS.get(first, "tools\\sqx142_performance_gate.ps1 performance-closeout-report"),
            "reason": "Falta una evidencia clave o la ultima no esta ok.",
            "requiresSQXClosed": first in {"profile_compare", "mc_project_views", "phase5_databank_view_guard", "old_log_archive", "performance_clone_hygiene"},
            "requiresMethodologyDecision": first == "mc2_spread_promotion",
        }
    return {
        "id": "ready_for_perf1_closeout",
        "label": "PERF1 esta listo para cierre operativo",
        "command": "tools\\sqx142_performance_gate.ps1 performance-closeout-report",
        "reason": "Status ok, evidencias clave presentes y perfil baseline restaurado.",
        "requiresSQXClosed": False,
        "requiresMethodologyDecision": False,
    }


def _read_tail_text(path: Path, limit: int = 400_000) -> str:
    try:
        with path.open("rb") as handle:
            try:
                handle.seek(max(0, path.stat().st_size - limit))
            except OSError:
                handle.seek(0)
            data = handle.read(limit)
        return data.decode("utf-8-sig", errors="replace")
    except OSError:
        return ""


def _sanitize_log_line(value: str) -> str:
    line = re.sub(r"[A-Za-z]:\\[^\s\"']+", "[PATH]", value.strip())
    line = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[EMAIL]", line)
    line = re.sub(r"https?://[^\s\"']+", "[URL]", line)
    return line[:240]


def _recent_log_files(root: Path, *, limit: int = 8) -> list[Path]:
    log_root = root / "user" / "log"
    if not log_root.is_dir():
        return []
    try:
        return sorted(log_root.rglob("*.log"), key=lambda path: path.stat().st_mtime, reverse=True)[:limit]
    except OSError:
        return []


def _scan_live_guard_logs(root: Path) -> dict[str, Any]:
    files = _recent_log_files(root, limit=8)
    marker_counts = {key: 0 for key in LIVE_GUARD_LOG_PATTERNS}
    examples: list[dict[str, str]] = []
    scanned = []
    latest_marker_mtime: float | None = None
    for path in files:
        try:
            stat = path.stat()
        except OSError:
            continue
        scanned.append({
            "name": path.name,
            "bytes": stat.st_size,
            "human": _format_bytes(stat.st_size),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
        })
        text = _read_tail_text(path)
        for line in text.splitlines():
            for marker, pattern in LIVE_GUARD_LOG_PATTERNS.items():
                if pattern.search(line):
                    marker_counts[marker] += 1
                    latest_marker_mtime = max(latest_marker_mtime or 0, stat.st_mtime)
                    if len(examples) < 8:
                        examples.append({"marker": marker, "file": path.name, "line": _sanitize_log_line(line)})
                    break
    active_markers = {key: value for key, value in marker_counts.items() if value > 0}
    marker_age_minutes = None
    latest_marker_modified = ""
    if latest_marker_mtime:
        marker_age_minutes = round(max(0.0, (datetime.now().timestamp() - latest_marker_mtime) / 60), 1)
        latest_marker_modified = datetime.fromtimestamp(latest_marker_mtime).isoformat(timespec="seconds")
    return {
        "filesScanned": len(scanned),
        "files": scanned,
        "markers": active_markers,
        "totalMarkers": sum(active_markers.values()),
        "latestMarkerModified": latest_marker_modified,
        "latestMarkerAgeMinutes": marker_age_minutes,
        "recentMarkerLikelyActive": bool(marker_age_minutes is not None and marker_age_minutes <= 60),
        "examples": examples,
        "ok": not active_markers,
    }


def _hs_err_snapshot(root: Path) -> dict[str, Any]:
    candidates: list[Path] = []
    for base in (root, root / "user" / "log"):
        if not base.exists():
            continue
        try:
            candidates.extend(base.glob("hs_err_pid*.log"))
        except OSError:
            continue
    unique = sorted(set(candidates), key=lambda path: path.stat().st_mtime if path.exists() else 0, reverse=True)
    latest = unique[0] if unique else None
    recent_cutoff = datetime.now() - timedelta(days=7)
    latest_modified = ""
    latest_recent = False
    if latest:
        try:
            modified = datetime.fromtimestamp(latest.stat().st_mtime)
            latest_modified = modified.isoformat(timespec="seconds")
            latest_recent = modified >= recent_cutoff
        except OSError:
            pass
    return {
        "count": len(unique),
        "latestFilename": latest.name if latest else "",
        "latestModified": latest_modified,
        "latestIsRecent": latest_recent,
        "ok": not latest_recent,
        "localPathReturned": False,
    }


def _sqx_local_api_snapshot(sqx_running: bool) -> dict[str, Any]:
    if not sqx_running:
        return {"checked": False, "reachable": False, "reason": "sqx_not_running"}
    request = urllib.request.Request(
        "http://localhost:8080/main/checkaccess",
        headers={"User-Agent": "SQX142-LiveGuard/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=1.5) as response:
            return {"checked": True, "reachable": True, "statusCode": int(response.status)}
    except urllib.error.HTTPError as exc:
        return {"checked": True, "reachable": True, "statusCode": int(exc.code), "httpError": True}
    except (OSError, TimeoutError) as exc:
        return {"checked": True, "reachable": False, "error": type(exc).__name__}


def _old_log_candidate_summary(root: Path, *, keep_days: int = 2) -> dict[str, Any]:
    cutoff = (datetime.now() - timedelta(days=max(0, keep_days - 1))).replace(hour=0, minute=0, second=0, microsecond=0)
    candidates: list[Path] = []
    for base in (root / "user" / "log", root / "user" / "projects"):
        if not base.is_dir():
            continue
        try:
            for path in base.rglob("*.log"):
                try:
                    if datetime.fromtimestamp(path.stat().st_mtime) < cutoff:
                        candidates.append(path)
                except OSError:
                    continue
        except OSError:
            continue
    total = sum(path.stat().st_size for path in candidates if path.is_file())
    return {
        "keepDays": keep_days,
        "cutoffLocal": cutoff.isoformat(timespec="seconds"),
        "count": len(candidates),
        "bytes": total,
        "human": _format_bytes(total),
        "localPathReturned": False,
    }


def _live_guard_repair_plan(
    *,
    status: dict[str, Any],
    active_profile: str,
    sqx_running: bool,
    alerts: list[str],
    old_log_candidates: dict[str, Any],
) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = [
        {
            "id": "capture_live_guard_snapshot",
            "label": "Guardar snapshot Live Guard",
            "command": "tools\\sqx142_performance_gate.ps1 live-guard",
            "safeWhen": "anytime_read_only",
            "automaticWhen": "monitor_or_agent_probe",
        }
    ]
    config_health = status.get("configHealth") if isinstance(status.get("configHealth"), dict) else {}
    if active_profile != "baseline_143_safe" or config_health.get("corrupt") or config_health.get("mismatched"):
        plan.append({
            "id": "restore_baseline_profile_after_close",
            "label": "Restaurar baseline_143_safe tras cerrar SQX",
            "command": "tools\\sqx142_performance_gate.ps1 apply-profile baseline_143_safe --apply",
            "safeWhen": "sqx_closed",
            "automaticWhen": "live_guard_apply_after_close",
        })
    if int(old_log_candidates.get("count") or 0) > 0:
        plan.append({
            "id": "archive_old_logs_after_close",
            "label": "Archivar logs antiguos tras cerrar SQX",
            "command": "tools\\sqx142_performance_gate.ps1 archive-old-logs --keep-days 2 --apply",
            "safeWhen": "sqx_closed",
            "automaticWhen": "live_guard_apply_after_close",
        })
    if "jvm_crash_log_recent" in alerts or "engine_crash_in_recent_logs" in alerts:
        plan.append({
            "id": "manual_crash_review",
            "label": "Revisar crash antes de lanzar nuevos lotes pesados",
            "command": "tools\\sqx142_performance_gate.ps1 snapshot",
            "safeWhen": "read_only",
            "automaticWhen": "never_manual_review",
        })
    cache_dir = ((status.get("directories") or {}).get("electronCache") or {}) if isinstance(status.get("directories"), dict) else {}
    if int(cache_dir.get("bytes") or 0) > 512 * 1024**2 and not sqx_running:
        plan.append({
            "id": "optional_electron_cache_refresh",
            "label": "Refrescar cache Electron si reaparece UI obsoleta",
            "command": "tools\\sqx142_electron_cache_refresh.ps1 -SQXRoot <SQX142_ROOT>",
            "safeWhen": "sqx_closed",
            "automaticWhen": "never_manual_confirmation",
        })
    return plan


def _live_guard_status(project_root: Path, root142: Path, status: dict[str, Any], compat: dict[str, Any]) -> dict[str, Any]:
    sqx_running = bool((compat.get("processes") or {}).get("running"))
    log_scan = _scan_live_guard_logs(root142)
    crash_logs = _hs_err_snapshot(root142)
    api = _sqx_local_api_snapshot(sqx_running)
    old_log_candidates = _old_log_candidate_summary(root142, keep_days=2)
    alerts: list[str] = []
    markers = log_scan.get("markers") if isinstance(log_scan.get("markers"), dict) else {}
    recent_markers = bool(log_scan.get("recentMarkerLikelyActive")) or sqx_running
    if crash_logs.get("latestIsRecent"):
        alerts.append("jvm_crash_log_recent")
    if int(markers.get("engine_crash") or 0) > 0 and recent_markers:
        alerts.append("engine_crash_in_recent_logs")
    if int(markers.get("out_of_memory") or 0) > 0 and recent_markers:
        alerts.append("out_of_memory_in_recent_logs")
    if int(markers.get("exception_or_error") or 0) >= 20 and recent_markers:
        alerts.append("high_error_marker_count")
    if sqx_running and api.get("checked") and not api.get("reachable"):
        alerts.append("sqx_api_unreachable_while_process_running")
    active_profile = str((status.get("activeProfile") or {}).get("id") or "")
    repair_plan = _live_guard_repair_plan(
        status=status,
        active_profile=active_profile,
        sqx_running=sqx_running,
        alerts=alerts,
        old_log_candidates=old_log_candidates,
    )
    repair_candidates = [
        item for item in repair_plan
        if item.get("safeWhen") == "sqx_closed" and item.get("automaticWhen") == "live_guard_apply_after_close"
    ]
    state = "observing_running_sqx" if sqx_running else ("post_close_repair_ready" if alerts or repair_candidates else "clean_idle")
    recommendation = {
        "id": "observe_only_while_running" if sqx_running else ("run_post_close_repair" if repair_candidates else "no_live_guard_repair_needed"),
        "label": (
            "Vigilar sin tocar SQX mientras esta abierto"
            if sqx_running
            else ("Ejecutar reparacion segura post-cierre" if repair_candidates else "Live Guard limpio")
        ),
        "command": (
            "tools\\sqx142_performance_gate.ps1 live-guard"
            if sqx_running
            else ("tools\\sqx142_performance_gate.ps1 live-guard --apply" if repair_candidates else "tools\\sqx142_performance_gate.ps1 live-guard")
        ),
        "requiresSQXClosed": not sqx_running and bool(repair_candidates),
    }
    return {
        "version": "sqx142-live-guard-v1",
        "ok": not alerts,
        "state": state,
        "mode": "observe_when_open_repair_when_closed",
        "sqxProcessDetected": sqx_running,
        "openPreflight": {
            "enabled": True,
            "action": "read_only_warning_before_heavy_work",
            "automaticRepairOnOpen": False,
        },
        "postCloseRepair": {
            "enabled": True,
            "dryRunByDefault": True,
            "applyCommand": "tools\\sqx142_performance_gate.ps1 live-guard --apply",
            "blockedWhileSQXOpen": True,
            "recommended": (not sqx_running and bool(repair_candidates)),
        },
        "logScan": log_scan,
        "oldLogCandidates": old_log_candidates,
        "crashLogs": crash_logs,
        "localApi": api,
        "alerts": alerts,
        "alertCount": len(alerts),
        "repairPlan": repair_plan,
        "recommendation": recommendation,
        "latestEvidence": _latest_evidence_brief(project_root, "performance_live_guard"),
        "privacy": {"local_paths_returned": False},
    }


def _performance_intelligence(project_root: Path, root142: Path, status: dict[str, Any], compat: dict[str, Any]) -> dict[str, Any]:
    evidence = {
        prefix: _latest_evidence_brief(project_root, prefix)
        for prefix in PERFORMANCE_REQUIRED_EVIDENCE_PREFIXES
    }
    missing_or_bad = [key for key, item in evidence.items() if not (item.get("exists") and item.get("ok"))]
    warnings = [str(item) for item in status.get("warnings", [])]
    active_profile = str((status.get("activeProfile") or {}).get("id") or "")
    view_summary = _performance_view_summary(status.get("views") if isinstance(status.get("views"), dict) else {})
    recommendation = _performance_recommendation(
        warnings=warnings,
        active_profile=active_profile,
        missing_or_bad=missing_or_bad,
    )
    sqx_process_running = bool((compat.get("processes") or {}).get("running"))
    live_guard = _live_guard_status(project_root, root142, status, compat)
    complete = (
        not warnings
        and active_profile == "baseline_143_safe"
        and not missing_or_bad
        and bool(status.get("ok"))
        and bool(view_summary.get("ok"))
        and bool(live_guard.get("ok"))
    )
    return {
        "version": "sqx142-performance-intelligence-v1",
        "localOnly": True,
        "visibleToRemote": False,
        "mode": "passive_on_probe",
        "autoStart": {
            "enabled": True,
            "requiresBackgroundDaemon": False,
            "triggers": ["operator_monitor_start", "operator_monitor_refresh", "agent_status", "manual_sqx_process_detected"],
            "sqxProcessDetected": sqx_process_running,
            "state": "observing_running_sqx" if sqx_process_running else "ready_on_monitor_or_agent_probe",
        },
        "activeProfile": status.get("activeProfile", {}),
        "views": view_summary,
        "latestEvidence": status.get("latestEvidence", {}),
        "keyEvidence": evidence,
        "missingOrBadEvidence": missing_or_bad,
        "recommendation": recommendation,
        "liveGuard": live_guard,
        "completeEnoughForPerf1Closeout": complete,
        "agentCapability": "sqx142_performance_help",
        "monitorPanel": "SQX 142 performance status",
        "qualityReductionAllowed": False,
        "privacy": {"local_paths_returned": False},
    }


def _local_access_status(root: Path) -> dict[str, Any]:
    remote_access = root / "user" / "settings" / "remote_access.xml"
    settings = root / "user" / "settings" / "settings.xml"
    result: dict[str, Any] = {
        "remoteAccessFileExists": remote_access.is_file(),
        "enabled": None,
        "requiresPassword": None,
        "passwordLength": None,
        "secureConnection": None,
        "browserTokenPresent": False,
        "unrestrictedOnThisPc": False,
    }
    try:
        tree = ET.parse(remote_access)
        root_el = tree.getroot()
        password_el = root_el.find("Password")
        connection_el = root_el.find("Connection")
        result["enabled"] = str(root_el.get("enabled", "")).lower() == "true"
        result["requiresPassword"] = str((password_el.get("require") if password_el is not None else "") or "").lower() == "true"
        try:
            result["passwordLength"] = int((password_el.get("length") if password_el is not None else "") or 0)
        except ValueError:
            result["passwordLength"] = None
        result["secureConnection"] = str((connection_el.get("secure") if connection_el is not None else "") or "").lower() == "true"
    except (OSError, ET.ParseError):
        pass
    try:
        settings_tree = ET.parse(settings)
        result["browserTokenPresent"] = bool((settings_tree.getroot().findtext("BrowserToken") or "").strip())
    except (OSError, ET.ParseError):
        pass
    result["unrestrictedOnThisPc"] = (
        result.get("enabled") is True
        and result.get("requiresPassword") is False
        and int(result.get("passwordLength") or 0) == 0
    )
    return result


def build_sqx142_performance_status(
    project_root: Path,
    sqx142_root: Path | None = None,
    sqx143_root: Path | None = None,
    *,
    include_paths: bool = False,
) -> dict[str, Any]:
    root142 = Path(sqx142_root or SQX142_DEFAULT_ROOT)
    root143 = Path(sqx143_root or SQX143_DEFAULT_ROOT)
    compat = build_sqx142_status(root142, root143, include_paths=False)
    profile = active_profile(root142)
    profile_lines = PROFILE_CONFIGS.get(str(profile.get("id") or ""), {}).get("lines", _config_lines(root142))
    config_health = _config_file_health(root142, list(profile_lines))
    resources = _resource_snapshot(root142)
    disk_state = (resources.get("disk") or {}).get("state", "unknown")
    directories = {
        "projects": _dir_stats(root142 / "user" / "projects", max_files=12_000),
        "logs": _dir_stats(root142 / "user" / "log", max_files=8_000),
        "views": _dir_stats(root142 / "user" / "settings" / "views" / "databanks", max_files=2_000),
        "electronCache": _dir_stats(root142 / "internal" / "electron" / "resources" / "userData" / "SQUANT", max_files=12_000),
    }
    warnings: list[str] = []
    if disk_state == "critical":
        warnings.append("disk_free_critical")
    elif disk_state == "warn":
        warnings.append("disk_free_below_recommended")
    if config_health.get("corrupt"):
        warnings.append("runtime_config_corrupt")
    if config_health.get("mismatched"):
        warnings.append("runtime_config_mismatch")
    if compat.get("processes", {}).get("running"):
        warnings.append("sqx_processes_running")
    compat_blockers = {str(item) for item in compat.get("blockers", [])}
    registered_perf_profile = bool(profile.get("id") in PROFILE_CONFIGS and not profile.get("custom"))
    perf_profile_only_deviation = (
        not compat.get("ok")
        and registered_perf_profile
        and bool(compat_blockers)
        and compat_blockers.issubset({"legacy_xmx_override_present"})
    )
    if not compat.get("ok") and not perf_profile_only_deviation:
        warnings.append("compatibility_not_ok")
    performance_view_presence = _view_presence(root142)
    monte_carlo_view_presence = {
        "MC MONKEY RETEST": (root142 / "user" / "settings" / "views" / "databanks" / "MC MONKEY RETEST.vw").is_file(),
        "MC SYNTHETIC RETEST": (root142 / "user" / "settings" / "views" / "databanks" / "MC SYNTHETIC RETEST.vw").is_file(),
    }
    views = {
        "performanceViews": performance_view_presence,
        "monteCarloViews": monte_carlo_view_presence,
    }
    missing_views = [
        name
        for name, exists in {
            **performance_view_presence,
            **monte_carlo_view_presence,
        }.items()
        if not exists
    ]
    if missing_views:
        warnings.append("performance_views_missing")
    local_access = _local_access_status(root142)
    if not local_access.get("unrestrictedOnThisPc"):
        warnings.append("local_access_restricted")
    status = "ok" if not warnings else ("warn" if not any(item.endswith("critical") for item in warnings) else "critical")
    result: dict[str, Any] = {
        "version": PERFORMANCE_VERSION,
        "ok": status == "ok",
        "status": status,
        "activeProfile": profile,
        "availableProfiles": [
            {"id": key, "label": value["label"], "description": value["description"]}
            for key, value in PROFILE_CONFIGS.items()
        ],
        "compatibility": {
            "ok": bool(compat.get("ok")),
            "status": compat.get("status"),
            "runtime": ((compat.get("java") or {}).get("active") or {}).get("label"),
            "baseline143Exact": bool(compat.get("ok")),
            "registeredPerformanceProfile": registered_perf_profile,
            "profileOnlyDeviation": perf_profile_only_deviation,
        },
        "configHealth": config_health,
        "resources": resources,
        "directories": directories,
        "views": views,
        "localAccess": local_access,
        "latestEvidence": _latest_evidence(project_root),
        "warnings": warnings,
        "qualityGate": {
            "qualityReductionAllowed": False,
            "requiresEvidenceBeforeMethodologyChange": True,
            "protected": ["OOS/Forward ranges", "validated precision", "MonteCarlo simulations", "final acceptance filters"],
        },
        "privacy": {"local_paths_returned": include_paths},
    }
    result["intelligence"] = _performance_intelligence(project_root, root142, result, compat)
    if include_paths:
        result["roots"] = {"sqx142Root": str(root142), "sqx143Root": str(root143), "evidenceRoot": str(project_root / EVIDENCE_DIRNAME)}
    return result


def render_view_xml(name: str, columns: list[tuple[str, str]]) -> str:
    lines = [f'<View name="{name}" originalName="{name}">', "  <Columns>"]
    for klass, label in columns:
        lines.append(f'    <Column class="{klass}" name="{label}" {VIEW_COLUMN_ATTRS}/>')
    lines.extend(["  </Columns>", "</View>", ""])
    return "\n".join(lines)


def performance_view_payloads() -> dict[str, str]:
    return {name: render_view_xml(name, columns) for name, columns in PERFORMANCE_VIEWS.items()}


def latest_launcher_events(root: Path, limit: int = 20) -> list[str]:
    log_root = root / "user" / "log"
    if not log_root.is_dir():
        return []
    logs = sorted(log_root.glob("launcher_*.log"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not logs:
        return []
    lines = _read_text(logs[0], limit=200_000).splitlines()
    return lines[-limit:]
