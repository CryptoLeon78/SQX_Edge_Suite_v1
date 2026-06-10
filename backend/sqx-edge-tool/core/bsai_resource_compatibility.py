from __future__ import annotations

import argparse
import json
import sqlite3
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote
from xml.etree import ElementTree as ET

from .blocksettings import blocksetting_trace, resolve_blocksetting_entry
from .blocksettings_ai_generator import _capa1_family_alias, _project_name, _safe_token
from .cfx_compatibility import audit_many
from .plan import Mining, normalize_direction
from .project_generator import DEFAULT_BROKER_POSTFIX, generate_project, resolve_costs


BS_AI10_RESOURCE_COMPATIBILITY_VERSION = "bs-ai10-target-resource-compatibility-gate-v1"
DEFAULT_CANDIDATE_ID = "BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005"
DEFAULT_TARGET_PROFILE_ID = "sqxedge_darwinex"
DEFAULT_REMAP_SUFFIX = "SQX144DARWINEX"
EVIDENCE_DIR_PARTS = (".local", "blocksettings_ai", "resource_compat")


@dataclass(frozen=True)
class CfxResourceUse:
    cfx_file: str
    capa: int | None
    xml_file: str
    symbol: str
    source: str
    broker: str
    instrument: str
    instrument_broker: str
    precision: str
    timezone: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "cfxFile": self.cfx_file,
            "capa": self.capa,
            "xmlFile": self.xml_file,
            "symbol": self.symbol,
            "source": self.source,
            "broker": self.broker,
            "instrument": self.instrument,
            "instrumentBroker": self.instrument_broker,
            "precision": self.precision,
            "timezone": self.timezone,
        }


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _tool_root(project_root: Path) -> Path:
    return project_root / "backend" / "sqx-edge-tool"


def _config_path(project_root: Path) -> Path:
    return _tool_root(project_root) / "config.json"


def _load_config(project_root: Path) -> dict[str, Any]:
    path = _config_path(project_root)
    if not path.is_file():
        raise FileNotFoundError("sqx_edge_config_missing")
    return _read_json(path)


def _candidate_meta_path(project_root: Path, candidate_id: str) -> Path:
    token = _safe_token(candidate_id, "")
    if not token.startswith("BSAI_"):
        raise ValueError("invalid_bsai_candidate_id")
    return project_root / ".local" / "blocksettings_ai" / "candidates" / f"{token}.json"


def load_candidate_metadata(project_root: Path, candidate_id: str) -> dict[str, Any]:
    path = _candidate_meta_path(project_root, candidate_id)
    if not path.is_file():
        raise FileNotFoundError("bsai_candidate_metadata_missing")
    meta = _read_json(path)
    entry = meta.get("entry") if isinstance(meta.get("entry"), dict) else {}
    if str(entry.get("canonicalId") or "") != candidate_id:
        raise ValueError("bsai_candidate_metadata_mismatch")
    return meta


def _recipe_from_candidate(meta: dict[str, Any]) -> dict[str, Any]:
    recipe = meta.get("recipe") if isinstance(meta.get("recipe"), dict) else {}
    if not recipe:
        raise ValueError("bsai_candidate_recipe_missing")
    return recipe


def _entry_from_candidate(meta: dict[str, Any]) -> dict[str, Any]:
    entry = meta.get("entry") if isinstance(meta.get("entry"), dict) else {}
    if not entry:
        raise ValueError("bsai_candidate_entry_missing")
    return dict(entry)


def _direction_tag(direction: str) -> str:
    return {"long": "L", "short": "S", "both": "LS"}[normalize_direction(direction)]


def _candidate_asset_tf_direction(recipe: dict[str, Any]) -> tuple[str, str, str]:
    asset = _safe_token(str(recipe.get("asset") or "EURUSD").upper(), "EURUSD")
    timeframe = _safe_token(str(recipe.get("timeframe") or "H1").upper(), "H1")
    direction = normalize_direction(str(recipe.get("direction") or "both"))
    return asset, timeframe, direction


def _candidate_project_name(recipe: dict[str, Any], candidate_id: str, suffix: str | None = None) -> str:
    name = _project_name(recipe, candidate_id)
    if suffix:
        name = f"{name}_{_safe_token(suffix, DEFAULT_REMAP_SUFFIX)}"
    return name


def candidate_pair_filenames(recipe: dict[str, Any], candidate_id: str, suffix: str | None = None) -> list[str]:
    name = _candidate_project_name(recipe, candidate_id, suffix=suffix)
    return [f"{name}_Capa1.cfx", f"{name}_Capa2.cfx"]


def _output_dir(project_root: Path, config: dict[str, Any]) -> Path:
    raw = str(config.get("output_dir") or "output")
    path = Path(raw)
    if not path.is_absolute():
        path = _tool_root(project_root) / path
    return path.resolve(strict=False)


def candidate_pair_paths(project_root: Path, candidate_id: str, *, suffix: str | None = None) -> list[Path]:
    config = _load_config(project_root)
    meta = load_candidate_metadata(project_root, candidate_id)
    recipe = _recipe_from_candidate(meta)
    root = _output_dir(project_root, config)
    return [root / name for name in candidate_pair_filenames(recipe, candidate_id, suffix=suffix)]


def _sqlite_ro_uri(db_path: Path) -> str:
    return f"file:{quote(db_path.resolve(strict=False).as_posix(), safe=':/')}?mode=ro"


def _connect_readonly(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    if not path.is_file():
        raise FileNotFoundError("sqx_data_db_missing")
    conn = sqlite3.connect(_sqlite_ro_uri(path), uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn


def _table_count(conn: sqlite3.Connection, table: str) -> int | None:
    try:
        return int(conn.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"])
    except Exception:
        return None


def _rows(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def _broker_map(conn: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    brokers: dict[str, dict[str, Any]] = {}
    try:
        for row in conn.execute("SELECT ID, NAME, POSTFIX, DESC FROM BROKER").fetchall():
            brokers[str(row["ID"])] = {
                "id": str(row["ID"]),
                "name": row["NAME"],
                "postfix": row["POSTFIX"],
                "description": row["DESC"],
            }
    except Exception:
        pass
    return brokers


def _catalog_row(row: dict[str, Any], brokers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    broker_id = "" if row.get("BROKER_ID") is None else str(row.get("BROKER_ID"))
    return {
        "symbol": str(row.get("SYMBOL") or ""),
        "instrument": str(row.get("INSTRUMENT") or ""),
        "timeframe": str(row.get("TIMEFRAME") or ""),
        "source": "" if row.get("SOURCE") is None else str(row.get("SOURCE")),
        "brokerId": broker_id,
        "brokerPostfix": (brokers.get(broker_id) or {}).get("postfix"),
        "rowsPositive": bool(int(row.get("ROWS") or 0) > 0),
        "uSymbol": str(row.get("USYMBOL") or ""),
    }


def load_target_catalog(db_path: str | Path, asset: str, *, host_profile: str = "sqx144_full") -> dict[str, Any]:
    asset = _safe_token(str(asset or "").upper(), "EURUSD")
    expected_primary = f"{asset}_darwinex"
    expected_cross = f"{asset}_dukascopy"
    conn = _connect_readonly(db_path)
    try:
        brokers = _broker_map(conn)
        data_rows = _rows(
            conn,
            """
            SELECT SYMBOL, INSTRUMENT, TIMEFRAME, SOURCE, BROKER_ID, ROWS, USYMBOL
            FROM DATA
            WHERE SYMBOL = ? OR SYMBOL = ? OR SYMBOL = ? OR INSTRUMENT LIKE ? OR USYMBOL = ?
            ORDER BY SYMBOL, TIMEFRAME
            """,
            (asset, expected_primary, expected_cross, f"{asset}%", asset),
        )
        instruments = _rows(
            conn,
            """
            SELECT INSTRUMENT, BROKER_ID, DEFAULTSPREAD
            FROM INSTRUMENTS
            WHERE INSTRUMENT = ? OR INSTRUMENT LIKE ?
            ORDER BY INSTRUMENT
            """,
            (asset, f"{asset}%"),
        )
        catalog_rows = [_catalog_row(row, brokers) for row in data_rows]
        instrument_rows = [
            {
                "instrument": str(row.get("INSTRUMENT") or ""),
                "brokerId": "" if row.get("BROKER_ID") is None else str(row.get("BROKER_ID")),
                "brokerPostfix": (brokers.get(str(row.get("BROKER_ID"))) or {}).get("postfix"),
            }
            for row in instruments
        ]
        return {
            "version": BS_AI10_RESOURCE_COMPATIBILITY_VERSION,
            "hostProfile": host_profile,
            "asset": asset,
            "readMode": "sqlite_uri_mode_ro_query_only",
            "tableCounts": {
                "DATA": _table_count(conn, "DATA"),
                "INSTRUMENTS": _table_count(conn, "INSTRUMENTS"),
                "BROKER": _table_count(conn, "BROKER"),
            },
            "expectedPrimarySymbol": expected_primary,
            "expectedCrossBrokerSymbol": expected_cross,
            "exactSymbolPresent": any(row["symbol"] == asset and row["rowsPositive"] for row in catalog_rows),
            "targetSymbolPresent": any(row["symbol"] == expected_primary and row["rowsPositive"] for row in catalog_rows),
            "crossBrokerSymbolPresent": any(row["symbol"] == expected_cross and row["rowsPositive"] for row in catalog_rows),
            "dataSymbols": catalog_rows,
            "instrumentCandidates": instrument_rows[:24],
            "privacy": {
                "localPathsReturned": False,
                "rawXmlReturned": False,
                "sqlReturned": False,
            },
        }
    finally:
        conn.close()


def _infer_capa(cfx_file: str) -> int | None:
    stem = Path(cfx_file).stem
    if stem.endswith("_Capa1") or "_Capa1" in stem:
        return 1
    if stem.endswith("_Capa2") or "_Capa2" in stem:
        return 2
    return None


def _extract_resource_uses(cfx_path: str | Path) -> list[CfxResourceUse]:
    path = Path(cfx_path)
    capa = _infer_capa(path.name)
    uses: list[CfxResourceUse] = []
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.endswith(".xml") or name == "config.xml":
                continue
            root = ET.fromstring(archive.read(name))
            for symbol in root.findall(".//Resources/Symbols/Symbol"):
                info = symbol.find("InstrumentInfo")
                uses.append(
                    CfxResourceUse(
                        cfx_file=path.name,
                        capa=capa,
                        xml_file=name,
                        symbol=str(symbol.get("name") or ""),
                        source=str(symbol.get("source") or ""),
                        broker=str(symbol.get("broker") or ""),
                        instrument=str(info.get("instrument") if info is not None else ""),
                        instrument_broker=str(info.get("broker") if info is not None else ""),
                        precision=str(symbol.get("precision") or ""),
                        timezone=str(symbol.get("timezone") or ""),
                    )
                )
    return uses


def _catalog_match(catalog: dict[str, Any], symbol: str, source: str | None = None, broker: str | None = None) -> dict[str, Any] | None:
    rows = [row for row in catalog.get("dataSymbols") or [] if row.get("symbol") == symbol and row.get("rowsPositive")]
    if source not in (None, ""):
        rows = [row for row in rows if str(row.get("source") or "") == str(source)]
    if broker not in (None, "", "-1"):
        rows = [row for row in rows if str(row.get("brokerId") or "") == str(broker)]
    return rows[0] if rows else None


def _allowed_cross_broker(use: CfxResourceUse) -> bool:
    return (
        use.source == "2"
        and (
            (use.capa == 1 and use.xml_file == "Retest-Task1.xml")
            or (use.capa == 2 and use.xml_file == "AutomaticRetest-Task7.xml")
        )
    )


def _compat_issue(code: str, severity: str, use: CfxResourceUse, detail: str) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "cfxFile": use.cfx_file,
        "xmlFile": use.xml_file,
        "symbol": use.symbol,
        "source": use.source,
        "broker": use.broker,
        "detail": detail,
    }


def _resource_compat_issues(uses: list[CfxResourceUse], catalog: dict[str, Any], target_profile_id: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    asset = str(catalog.get("asset") or "")
    expected_primary = str(catalog.get("expectedPrimarySymbol") or f"{asset}_darwinex")
    expected_cross = str(catalog.get("expectedCrossBrokerSymbol") or f"{asset}_dukascopy")
    for use in uses:
        if not use.symbol:
            continue
        if _allowed_cross_broker(use):
            match = _catalog_match(catalog, use.symbol, use.source, use.broker)
            if use.symbol != expected_cross:
                issues.append(_compat_issue(
                    "methodology_cross_broker_symbol_unexpected",
                    "fail",
                    use,
                    f"expected governed cross-broker symbol {expected_cross}",
                ))
            elif not match:
                issues.append(_compat_issue(
                    "methodology_cross_broker_missing_in_sqx144_catalog",
                    "fail",
                    use,
                    "Dukascopy methodology resource has no loaded target catalog row",
                ))
            else:
                issues.append(_compat_issue(
                    "methodology_cross_broker_catalog_match",
                    "warn",
                    use,
                    "Dukascopy OOS resource exists in target catalog and remains a governed methodology warning",
                ))
            continue

        if target_profile_id == DEFAULT_TARGET_PROFILE_ID:
            source_ok = use.source == "4"
            broker_ok = use.broker == "4"
            symbol_ok = use.symbol == expected_primary
            match = _catalog_match(catalog, use.symbol, use.source, use.broker)
            if not (symbol_ok and source_ok and broker_ok):
                issues.append(_compat_issue(
                    "primary_resource_mismatch_for_sqx144_full",
                    "fail",
                    use,
                    f"expected {expected_primary} with source 4 and broker 4 for sqx144_full",
                ))
            elif not match:
                issues.append(_compat_issue(
                    "target_symbol_missing_in_sqx144_catalog",
                    "fail",
                    use,
                    "primary Darwinex resource has no loaded target catalog row",
                ))
            continue

        match = _catalog_match(catalog, use.symbol, use.source, use.broker)
        if not match:
            issues.append(_compat_issue(
                "target_symbol_missing_in_sqx144_catalog",
                "fail",
                use,
                "resource has no loaded target catalog row",
            ))
    return issues


def audit_target_resource_compatibility(
    cfx_paths: list[str | Path],
    db_path: str | Path,
    *,
    asset: str,
    host_profile: str = "sqx144_full",
    target_profile_id: str = DEFAULT_TARGET_PROFILE_ID,
) -> dict[str, Any]:
    paths = [Path(path) for path in cfx_paths]
    static_report = audit_many(paths)
    catalog = load_target_catalog(db_path, asset, host_profile=host_profile)
    uses = [use for path in paths for use in _extract_resource_uses(path)]
    target_issues = _resource_compat_issues(uses, catalog, target_profile_id)
    fail_count = sum(1 for issue in target_issues if issue["severity"] == "fail")
    warn_count = sum(1 for issue in target_issues if issue["severity"] == "warn")
    target_verdict = "fail" if fail_count else "warn" if warn_count else "pass"
    gate_status = (
        "blocked_target_resource_mismatch"
        if fail_count
        else "ready_for_manual_import_gate_with_methodology_warnings"
        if warn_count or static_report.get("warnCount")
        else "ready_for_manual_import_gate"
    )
    recommendation = (
        "regenerate_with_target_profile_sqxedge_darwinex"
        if fail_count
        else "manual_import_gate_required_before_sqx_file_dialog"
    )
    return {
        "version": BS_AI10_RESOURCE_COMPATIBILITY_VERSION,
        "hostProfile": host_profile,
        "targetProfileId": target_profile_id,
        "asset": catalog["asset"],
        "files": [path.name for path in paths],
        "targetResourceVerdict": target_verdict,
        "gateStatus": gate_status,
        "recommendation": recommendation,
        "targetFailCount": fail_count,
        "targetWarnCount": warn_count,
        "targetIssues": target_issues,
        "resourceUses": [use.as_dict() for use in uses],
        "targetCatalog": catalog,
        "staticAuditSummary": {
            "version": static_report.get("version"),
            "count": static_report.get("count"),
            "passCount": static_report.get("passCount"),
            "warnCount": static_report.get("warnCount"),
            "failCount": static_report.get("failCount"),
            "reports": [
                {
                    "fileName": report.get("fileName"),
                    "hostProfile": report.get("hostProfile"),
                    "verdict": report.get("verdict"),
                    "issueCount": report.get("issueCount"),
                    "failCount": report.get("failCount"),
                    "warnCount": report.get("warnCount"),
                    "issueCodes": sorted({issue.get("code") for issue in report.get("issues") or []}),
                }
                for report in static_report.get("reports") or []
            ],
        },
        "privacy": {
            "localPathsReturned": False,
            "rawXmlReturned": False,
            "secretsReturned": False,
        },
    }


def _template_path(project_root: Path, config: dict[str, Any], key: str) -> Path:
    raw = Path(str(config.get(key) or ""))
    if raw.is_absolute():
        return raw
    return (_tool_root(project_root) / raw).resolve(strict=False)


def generate_remapped_pair(
    project_root: str | Path,
    candidate_id: str = DEFAULT_CANDIDATE_ID,
    *,
    target_profile_id: str = DEFAULT_TARGET_PROFILE_ID,
    project_suffix: str = DEFAULT_REMAP_SUFFIX,
) -> dict[str, Any]:
    project_root = _project_root(project_root)
    config = _load_config(project_root)
    meta = load_candidate_metadata(project_root, candidate_id)
    recipe = _recipe_from_candidate(meta)
    entry = _entry_from_candidate(meta)
    asset, timeframe, direction = _candidate_asset_tf_direction(recipe)
    layer = int(entry.get("layer") or recipe.get("candidateLayer") or 1)
    project_name = _candidate_project_name(recipe, candidate_id, suffix=project_suffix)
    mining = Mining(num=0, phase=0, asset=asset, tf=timeframe, bs=_capa1_family_alias(recipe), dir=direction)
    sqx_db_path = str(config.get("sqx_data_db") or "")
    output_dir = _output_dir(project_root, config)
    output_dir.mkdir(parents=True, exist_ok=True)
    target_profile = {"id": target_profile_id}
    generated: list[dict[str, Any]] = []
    for capa, template_key in ((1, "template_capa1"), (2, "template_capa2")):
        override = entry if layer == capa else None
        out_path = Path(generate_project(
            mining,
            template_path=str(_template_path(project_root, config, template_key)),
            output_dir=str(output_dir),
            capa=capa,
            sqx_db_path=sqx_db_path,
            broker_postfix=str(config.get("darwinex_suffix") or DEFAULT_BROKER_POSTFIX),
            alias_override=config.get("asset_aliases") if isinstance(config.get("asset_aliases"), dict) else None,
            project_name=project_name,
            target_profile=target_profile,
            blocksetting_entry_override=override,
        ))
        costs = resolve_costs(
            mining,
            sqx_db_path,
            str(config.get("darwinex_suffix") or DEFAULT_BROKER_POSTFIX),
            alias_override=config.get("asset_aliases") if isinstance(config.get("asset_aliases"), dict) else None,
            target_profile=target_profile,
        )
        used_entry = override or resolve_blocksetting_entry(mining.bs, timeframe=mining.tf, capa=capa)
        generated.append({
            "capa": capa,
            "filename": out_path.name,
            "downloadUrl": f"/api/output/download/{out_path.name}",
            "symbol": costs.get("symbol"),
            "costsSource": costs.get("source"),
            "blocksetting": blocksetting_trace(used_entry),
        })
    return {
        "version": BS_AI10_RESOURCE_COMPATIBILITY_VERSION,
        "candidateId": candidate_id,
        "projectName": project_name,
        "targetProfileId": target_profile_id,
        "generatedFiles": generated,
        "privacy": {
            "localPathsReturned": False,
            "officialResourcesOverwritten": False,
            "hostStoresWritten": False,
        },
    }


def _write_evidence(project_root: Path, payload: dict[str, Any]) -> str:
    evidence_dir = project_root.joinpath(*EVIDENCE_DIR_PARTS)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / f"bsai10_target_resource_compat_{_utc_stamp()}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path.name


def _base_payload(action: str, candidate_id: str, host_profile: str, target_profile_id: str) -> dict[str, Any]:
    return {
        "ok": False,
        "version": BS_AI10_RESOURCE_COMPATIBILITY_VERSION,
        "action": action,
        "candidateId": candidate_id,
        "hostProfile": host_profile,
        "targetProfileId": target_profile_id,
        "writesSqxHost": False,
        "writesDataDb": False,
        "writesUserProjects": False,
        "mutatesDatabanks": False,
        "runsSqxTasks": False,
        "privacy": {
            "localPathsReturned": False,
            "rawXmlReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
        },
    }


def status_payload(project_root: str | Path, candidate_id: str, *, target_profile_id: str = DEFAULT_TARGET_PROFILE_ID) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "sqx144_full")
    payload = _base_payload("status", candidate_id, host_profile, target_profile_id)
    meta = load_candidate_metadata(root, candidate_id)
    recipe = _recipe_from_candidate(meta)
    asset, timeframe, direction = _candidate_asset_tf_direction(recipe)
    files = [
        {
            "capa": index + 1,
            "filename": path.name,
            "exists": path.is_file(),
        }
        for index, path in enumerate(candidate_pair_paths(root, candidate_id))
    ]
    catalog = load_target_catalog(str(config.get("sqx_data_db") or ""), asset, host_profile=host_profile)
    blockers = []
    if host_profile != "sqx144_full":
        blockers.append("host_profile_not_sqx144_full")
    if not catalog.get("targetSymbolPresent"):
        blockers.append("target_darwinex_symbol_missing")
    if not catalog.get("crossBrokerSymbolPresent"):
        blockers.append("target_dukascopy_symbol_missing")
    if not all(item["exists"] for item in files):
        blockers.append("candidate_project_pair_missing")
    payload.update({
        "ok": not blockers,
        "status": "target_resource_status_ready" if not blockers else "target_resource_status_blocked",
        "asset": asset,
        "timeframe": timeframe,
        "direction": direction,
        "files": files,
        "candidate": {
            "id": candidate_id,
            "baseCanonicalId": (_entry_from_candidate(meta)).get("baseCanonicalId"),
            "sourceVersionPolicy": (_entry_from_candidate(meta)).get("sourceVersionPolicy"),
            "promotionState": (_entry_from_candidate(meta)).get("promotionState"),
        },
        "targetCatalog": {
            "readMode": catalog.get("readMode"),
            "expectedPrimarySymbol": catalog.get("expectedPrimarySymbol"),
            "expectedCrossBrokerSymbol": catalog.get("expectedCrossBrokerSymbol"),
            "exactSymbolPresent": catalog.get("exactSymbolPresent"),
            "targetSymbolPresent": catalog.get("targetSymbolPresent"),
            "crossBrokerSymbolPresent": catalog.get("crossBrokerSymbolPresent"),
            "tableCounts": catalog.get("tableCounts"),
        },
        "blockers": blockers,
    })
    return payload


def audit_payload(
    project_root: str | Path,
    candidate_id: str,
    *,
    target_profile_id: str = DEFAULT_TARGET_PROFILE_ID,
    suffix: str | None = None,
    write_evidence: bool = False,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "sqx144_full")
    meta = load_candidate_metadata(root, candidate_id)
    recipe = _recipe_from_candidate(meta)
    asset, _, _ = _candidate_asset_tf_direction(recipe)
    paths = candidate_pair_paths(root, candidate_id, suffix=suffix)
    report = audit_target_resource_compatibility(
        paths,
        str(config.get("sqx_data_db") or ""),
        asset=asset,
        host_profile=host_profile,
        target_profile_id=target_profile_id,
    )
    payload = _base_payload("audit", candidate_id, host_profile, target_profile_id)
    payload.update({
        "ok": report["targetFailCount"] == 0,
        "status": report["gateStatus"],
        "audit": report,
    })
    if write_evidence:
        payload["evidenceFile"] = _write_evidence(root, payload)
    return payload


def remap_payload(
    project_root: str | Path,
    candidate_id: str,
    *,
    target_profile_id: str = DEFAULT_TARGET_PROFILE_ID,
    project_suffix: str = DEFAULT_REMAP_SUFFIX,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "sqx144_full")
    original = audit_payload(root, candidate_id, target_profile_id=target_profile_id, write_evidence=False)
    remap = generate_remapped_pair(root, candidate_id, target_profile_id=target_profile_id, project_suffix=project_suffix)
    remapped_audit = audit_payload(root, candidate_id, target_profile_id=target_profile_id, suffix=project_suffix, write_evidence=False)
    payload = _base_payload("remap", candidate_id, host_profile, target_profile_id)
    payload.update({
        "ok": bool(remapped_audit.get("ok")),
        "status": "remap_ready_for_manual_import_gate_no_import" if remapped_audit.get("ok") else "remap_generated_but_still_blocked",
        "originalAuditStatus": original.get("status"),
        "remappedAuditStatus": remapped_audit.get("status"),
        "originalAudit": original.get("audit"),
        "remappedProject": remap,
        "remappedAudit": remapped_audit.get("audit"),
        "nextGate": "BS-AI11 remapped manual import gate requires explicit operator approval",
    })
    if write_evidence:
        payload["evidenceFile"] = _write_evidence(root, payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BS-AI10 target-resource compatibility gate")
    parser.add_argument("action", choices=("status", "audit", "remap"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--candidate-id", default=DEFAULT_CANDIDATE_ID)
    parser.add_argument("--target-profile", default=DEFAULT_TARGET_PROFILE_ID)
    parser.add_argument("--remap-suffix", default=DEFAULT_REMAP_SUFFIX)
    parser.add_argument("--suffix", default=None)
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)

    if args.action == "status":
        payload = status_payload(args.project_root, args.candidate_id, target_profile_id=args.target_profile)
    elif args.action == "audit":
        payload = audit_payload(
            args.project_root,
            args.candidate_id,
            target_profile_id=args.target_profile,
            suffix=args.suffix,
            write_evidence=args.write_evidence,
        )
    else:
        payload = remap_payload(
            args.project_root,
            args.candidate_id,
            target_profile_id=args.target_profile,
            project_suffix=args.remap_suffix,
            write_evidence=True,
        )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
