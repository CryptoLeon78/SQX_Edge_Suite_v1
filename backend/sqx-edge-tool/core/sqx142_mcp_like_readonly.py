from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .sqx_compatibility import SQX142_DEFAULT_ROOT, build_sqx142_status
from .sqx_performance import build_sqx142_performance_status


MCP_LIKE_VERSION = "sqx142-mcp-like-readonly-v1"
DEFAULT_LIMIT = 50
MAX_LIMIT = 200


def _privacy() -> dict[str, bool]:
    return {
        "local_paths_returned": False,
        "raw_project_names_returned": False,
        "license_material_returned": False,
        "tokens_returned": False,
    }


def _response(
    data: dict[str, Any] | list[Any] | None = None,
    *,
    ok: bool = True,
    warnings: list[str] | None = None,
    blockers: list[str] | None = None,
    error: str = "",
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": ok,
        "version": MCP_LIKE_VERSION,
        "scope": "local_operator_only",
        "mode": "read_only",
        "data": data if data is not None else {},
        "warnings": warnings or [],
        "blockers": blockers or [],
        "privacy": _privacy(),
    }
    if error:
        payload["error"] = error
    return payload


def _limit(value: Any) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = DEFAULT_LIMIT
    return max(1, min(parsed, MAX_LIMIT))


def _offset(value: Any) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = 0
    return max(0, parsed)


def _hash_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _minute_iso(timestamp: float) -> str:
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(second=0, microsecond=0)
    return dt.isoformat().replace("+00:00", "Z")


def _project_root(sqx142_root: Path | None = None) -> Path:
    return Path(sqx142_root or SQX142_DEFAULT_ROOT) / "user" / "projects"


def _data_db_path(sqx142_root: Path | None = None) -> Path:
    return Path(sqx142_root or SQX142_DEFAULT_ROOT) / "user" / "data" / "data.db"


def _plugins_root(sqx142_root: Path | None = None) -> Path:
    return Path(sqx142_root or SQX142_DEFAULT_ROOT) / "user" / "extend" / "ResultsPlugins"


def _project_class(name: str) -> str:
    lowered = name.casefold()
    if name.startswith("_PERFQ_"):
        return "performance_clone"
    if "mining" in lowered:
        return "mining"
    if "retest" in lowered:
        return "retest"
    if "portfolio" in lowered:
        return "portfolio"
    return "project"


def _project_item(path: Path) -> dict[str, Any]:
    stat = path.stat()
    fingerprint = f"{path.name}|dir|{int(stat.st_mtime)}"
    return {
        "projectId": _hash_id("project", fingerprint),
        "class": _project_class(path.name),
        "modifiedUtc": _minute_iso(stat.st_mtime),
        "createdUtc": _minute_iso(stat.st_ctime),
        "fileCounts": {
            "sqx": _safe_count(path, "*.sqx"),
            "cfx": _safe_count(path, "*.cfx"),
            "xml": _safe_count(path, "*.xml"),
        },
        "flags": {
            "performanceClone": path.name.startswith("_PERFQ_"),
        },
    }


def _safe_count(path: Path, pattern: str) -> int:
    try:
        return sum(1 for _ in path.rglob(pattern))
    except OSError:
        return 0


def _project_items(sqx142_root: Path | None = None) -> list[dict[str, Any]]:
    root = _project_root(sqx142_root)
    if not root.is_dir():
        return []
    items: list[dict[str, Any]] = []
    for child in root.iterdir():
        if not child.is_dir():
            continue
        try:
            items.append(_project_item(child))
        except OSError:
            continue
    items.sort(key=lambda item: item.get("modifiedUtc", ""), reverse=True)
    return items


def build_mcp_like_status(project_root: Path, sqx142_root: Path | None = None) -> dict[str, Any]:
    root = Path(sqx142_root or SQX142_DEFAULT_ROOT)
    plugins = _plugins_root(root)
    projects = _project_root(root)
    data_db = _data_db_path(root)
    compat = build_sqx142_status(root, include_paths=False)
    performance = build_sqx142_performance_status(project_root, root, include_paths=False)
    return _response({
        "compat": compat,
        "performance": performance,
        "availability": {
            "sqx142Exists": root.is_dir(),
            "projectsExists": projects.is_dir(),
            "dataDbExists": data_db.is_file(),
            "resultsPluginsExists": plugins.is_dir(),
            "projectDirCount": len(_project_items(root)),
            "resultsPluginCount": len([p for p in plugins.iterdir() if p.is_dir()]) if plugins.is_dir() else 0,
        },
        "endpoints": [
            "/api/sqx142/mcp-like/status",
            "/api/sqx142/mcp-like/projects",
            "/api/sqx142/mcp-like/data-catalog",
            "/api/sqx142/mcp-like/databanks",
            "/api/sqx142/mcp-like/strategies",
            "/api/sqx142/mcp-like/results-plugin-readiness",
        ],
    })


def build_mcp_like_projects(
    sqx142_root: Path | None = None,
    *,
    limit: Any = DEFAULT_LIMIT,
    offset: Any = 0,
    include_raw_names: bool = False,
) -> dict[str, Any]:
    if include_raw_names:
        return _response(ok=False, error="raw_project_names_blocked", blockers=["includeRawNames"])
    items = _project_items(sqx142_root)
    start = _offset(offset)
    size = _limit(limit)
    return _response({
        "items": items[start:start + size],
        "page": {
            "limit": size,
            "offset": start,
            "returned": len(items[start:start + size]),
            "total": len(items),
        },
    })


def _table_names(con: sqlite3.Connection) -> list[str]:
    rows = con.execute("select name from sqlite_master where type='table' order by name").fetchall()
    return [str(row[0]) for row in rows]


def _table_columns(con: sqlite3.Connection, table: str) -> set[str]:
    rows = con.execute(f'pragma table_info("{table}")').fetchall()
    return {str(row[1]).upper() for row in rows}


def _count_table(con: sqlite3.Connection, table: str) -> int | str:
    try:
        return int(con.execute(f'select count(*) from "{table}"').fetchone()[0])
    except sqlite3.Error as exc:
        return type(exc).__name__


def _sample_data_rows(con: sqlite3.Connection, limit: int) -> list[dict[str, Any]]:
    tables = set(_table_names(con))
    if "DATA" not in tables:
        return []
    columns = _table_columns(con, "DATA")
    wanted = [name for name in ["SYMBOL", "INSTRUMENT", "TIMEFRAME", "TIMEFRAMETYPE", "DATATYPE", "DATEFROM", "DATETO", "TIMEZONE"] if name in columns]
    if not wanted:
        return []
    select = ", ".join(f'"{name}"' for name in wanted)
    rows = con.execute(f'select {select} from "DATA" limit ?', (limit,)).fetchall()
    samples: list[dict[str, Any]] = []
    for row in rows:
        raw = dict(zip(wanted, row))
        symbol_value = str(raw.get("SYMBOL") or raw.get("INSTRUMENT") or "")
        item = {
            "seriesId": _hash_id("series", symbol_value or repr(raw)),
            "fields": {key.lower(): value for key, value in raw.items() if key not in {"SYMBOL", "INSTRUMENT"}},
        }
        if "INSTRUMENT" in raw:
            item["instrumentId"] = _hash_id("instrument", str(raw["INSTRUMENT"]))
        samples.append(item)
    return samples


def build_mcp_like_data_catalog(
    sqx142_root: Path | None = None,
    *,
    limit: Any = DEFAULT_LIMIT,
) -> dict[str, Any]:
    data_db = _data_db_path(sqx142_root)
    if not data_db.is_file():
        return _response(ok=False, error="data_db_missing", blockers=["data_db_missing"])
    size = _limit(limit)
    con = sqlite3.connect(f"file:{data_db}?mode=ro", uri=True)
    try:
        tables = _table_names(con)
        counts = {table: _count_table(con, table) for table in tables}
        samples = _sample_data_rows(con, min(size, 50))
    finally:
        con.close()
    return _response({
        "tables": tables,
        "counts": counts,
        "samples": {
            "dataSeries": samples,
            "limit": min(size, 50),
        },
    })


def _find_project_by_id(project_id: str, sqx142_root: Path | None = None) -> Path | None:
    root = _project_root(sqx142_root)
    if not root.is_dir():
        return None
    for child in root.iterdir():
        if not child.is_dir():
            continue
        try:
            if _project_item(child)["projectId"] == project_id:
                return child
        except OSError:
            continue
    return None


def build_mcp_like_databanks(
    sqx142_root: Path | None = None,
    *,
    project_id: str = "",
    limit: Any = DEFAULT_LIMIT,
) -> dict[str, Any]:
    if not project_id:
        return _response(ok=False, error="projectId_required", blockers=["projectId_required"])
    project = _find_project_by_id(project_id, sqx142_root)
    if project is None:
        return _response(ok=False, error="project_not_found", blockers=["project_not_found"])
    size = _limit(limit)
    candidates = [path for path in project.rglob("*") if path.is_dir() and path.name.casefold() in {"databanks", "results"}]
    items: list[dict[str, Any]] = []
    for container in candidates[:10]:
        for child in container.iterdir():
            if not child.is_dir():
                continue
            stat = child.stat()
            items.append({
                "databankId": _hash_id("databank", f"{project_id}|{child.name}|{int(stat.st_mtime)}"),
                "modifiedUtc": _minute_iso(stat.st_mtime),
                "strategyFileCount": _safe_count(child, "*.sqx"),
                "xmlFileCount": _safe_count(child, "*.xml"),
            })
            if len(items) >= size:
                break
        if len(items) >= size:
            break
    return _response({"projectId": project_id, "items": items, "page": {"limit": size, "returned": len(items)}})


def build_mcp_like_strategies(
    sqx142_root: Path | None = None,
    *,
    project_id: str = "",
    limit: Any = DEFAULT_LIMIT,
) -> dict[str, Any]:
    if not project_id:
        return _response(ok=False, error="projectId_required", blockers=["projectId_required"])
    project = _find_project_by_id(project_id, sqx142_root)
    if project is None:
        return _response(ok=False, error="project_not_found", blockers=["project_not_found"])
    size = _limit(limit)
    items: list[dict[str, Any]] = []
    for path in project.rglob("*.sqx"):
        try:
            stat = path.stat()
        except OSError:
            continue
        items.append({
            "strategyId": _hash_id("strategy", f"{project_id}|{path.name}|{stat.st_size}|{int(stat.st_mtime)}"),
            "sizeBytes": stat.st_size,
            "modifiedUtc": _minute_iso(stat.st_mtime),
            "sourceCodeIncluded": False,
            "ordersIncluded": False,
        })
        if len(items) >= size:
            break
    return _response({"projectId": project_id, "items": items, "page": {"limit": size, "returned": len(items)}})


def build_results_plugin_readiness(project_root: Path, sqx142_root: Path | None = None) -> dict[str, Any]:
    status = build_mcp_like_status(project_root, sqx142_root)
    availability = (status.get("data") or {}).get("availability", {})
    blockers = []
    if not availability.get("sqx142Exists"):
        blockers.append("sqx142_missing")
    if not availability.get("projectsExists"):
        blockers.append("projects_missing")
    state = "blocked" if blockers else "review"
    if availability.get("projectDirCount", 0) and availability.get("dataDbExists"):
        state = "ready"
    return _response({
        "panel": "SQX Edge Readiness Panel",
        "state": state,
        "availability": availability,
        "mcpLikeApi": {
            "available": True,
            "version": MCP_LIKE_VERSION,
            "readOnly": True,
        },
    }, blockers=blockers)
