import json
import sqlite3
from pathlib import Path
from unittest.mock import patch

from api import server
from core.sqx142_mcp_like_readonly import (
    MCP_LIKE_VERSION,
    build_mcp_like_data_catalog,
    build_mcp_like_databanks,
    build_mcp_like_projects,
    build_mcp_like_strategies,
)


def _make_fake_sqx142_root(tmp_path: Path) -> Path:
    root = tmp_path / "sqx142"
    projects = root / "user" / "projects"
    project = projects / "Secret Client Project"
    (project / "results" / "Main Databank").mkdir(parents=True)
    (project / "results" / "Main Databank" / "private_strategy.sqx").write_text("mock", encoding="utf-8")
    (project / "config.xml").write_text("<config />", encoding="utf-8")
    data_dir = root / "user" / "data"
    data_dir.mkdir(parents=True)
    con = sqlite3.connect(data_dir / "data.db")
    try:
        con.execute("create table BROKER (ID integer primary key, NAME text)")
        con.execute("create table DATA (SYMBOL text, TIMEFRAME text, DATATYPE integer, DATEFROM text, DATETO text, TIMEZONE text)")
        con.execute("create table INSTRUMENTS (INSTRUMENT text)")
        con.execute("create table SESSIONS (NAME text)")
        con.execute("insert into BROKER (NAME) values ('Private Broker')")
        con.execute(
            "insert into DATA (SYMBOL, TIMEFRAME, DATATYPE, DATEFROM, DATETO, TIMEZONE) values (?, ?, ?, ?, ?, ?)",
            ("PRIVATE_SYMBOL", "H1", 4, "2020.01.01", "2026.01.01", "EETUS"),
        )
        con.commit()
    finally:
        con.close()
    (root / "user" / "extend" / "ResultsPlugins" / "SQX Edge Readiness Panel").mkdir(parents=True)
    return root


def _assert_public_safe(payload: dict) -> None:
    encoded = json.dumps(payload, ensure_ascii=False)
    assert r"C:\\" not in encoded
    assert "SQX_142_Crack" not in encoded
    assert "Secret Client Project" not in encoded
    assert "PRIVATE_SYMBOL" not in encoded
    assert "private_strategy" not in encoded
    assert "Private Broker" not in encoded
    assert "token=" not in encoded.lower()
    assert "secret_token" not in encoded.lower()
    assert "password=" not in encoded.lower()


def test_mcp_like_projects_are_readonly_paginated_and_redacted(tmp_path):
    root = _make_fake_sqx142_root(tmp_path)

    payload = build_mcp_like_projects(root, limit=1)

    assert payload["ok"] is True
    assert payload["version"] == MCP_LIKE_VERSION
    assert payload["mode"] == "read_only"
    assert payload["privacy"]["local_paths_returned"] is False
    assert payload["privacy"]["raw_project_names_returned"] is False
    assert payload["data"]["page"]["limit"] == 1
    assert payload["data"]["items"][0]["projectId"].startswith("project_")
    _assert_public_safe(payload)

    blocked = build_mcp_like_projects(root, include_raw_names=True)
    assert blocked["ok"] is False
    assert blocked["error"] == "raw_project_names_blocked"


def test_mcp_like_data_catalog_reads_sqlite_mode_ro_and_redacts_symbols(tmp_path):
    root = _make_fake_sqx142_root(tmp_path)

    payload = build_mcp_like_data_catalog(root)

    assert payload["ok"] is True
    assert payload["data"]["counts"]["BROKER"] == 1
    assert payload["data"]["counts"]["DATA"] == 1
    assert payload["data"]["samples"]["dataSeries"][0]["seriesId"].startswith("series_")
    assert payload["data"]["samples"]["dataSeries"][0]["fields"]["timeframe"] == "H1"
    _assert_public_safe(payload)


def test_mcp_like_databanks_and_strategies_use_opaque_ids(tmp_path):
    root = _make_fake_sqx142_root(tmp_path)
    project_id = build_mcp_like_projects(root)["data"]["items"][0]["projectId"]

    databanks = build_mcp_like_databanks(root, project_id=project_id)
    strategies = build_mcp_like_strategies(root, project_id=project_id)

    assert databanks["ok"] is True
    assert databanks["data"]["items"][0]["databankId"].startswith("databank_")
    assert strategies["ok"] is True
    assert strategies["data"]["items"][0]["strategyId"].startswith("strategy_")
    assert strategies["data"]["items"][0]["sourceCodeIncluded"] is False
    assert strategies["data"]["items"][0]["ordersIncluded"] is False
    _assert_public_safe(databanks)
    _assert_public_safe(strategies)


def test_mcp_like_routes_are_local_operator_only_path_safe_and_get_only():
    client = server.app.test_client()
    safe_payload = {
        "ok": True,
        "version": MCP_LIKE_VERSION,
        "scope": "local_operator_only",
        "mode": "read_only",
        "data": {"items": [{"projectId": "project_abc", "class": "project"}]},
        "warnings": [],
        "blockers": [],
        "privacy": {
            "local_paths_returned": False,
            "raw_project_names_returned": False,
            "license_material_returned": False,
            "tokens_returned": False,
        },
    }

    with patch.object(server, "build_mcp_like_projects", return_value=safe_payload):
        response = client.get("/api/sqx142/mcp-like/projects")
    assert response.status_code == 200
    data = response.get_json()
    assert data["version"] == MCP_LIKE_VERSION
    assert data["privacy"]["local_paths_returned"] is False
    assert r"C:\\" not in json.dumps(data, ensure_ascii=False)

    blocked = client.get(
        "/api/sqx142/mcp-like/projects",
        base_url="https://app.sqxedgesuite.org",
        headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert blocked.status_code == 403
    assert blocked.get_json()["error"] == "local_operator_required"

    mutating = client.post("/api/sqx142/mcp-like/projects")
    assert mutating.status_code == 405


def test_mcp_like_route_blocks_raw_names_query():
    client = server.app.test_client()

    response = client.get("/api/sqx142/mcp-like/projects?includeRawNames=true")
    data = response.get_json()

    assert response.status_code == 200
    assert data["ok"] is False
    assert data["error"] == "raw_project_names_blocked"
    assert data["privacy"]["raw_project_names_returned"] is False
