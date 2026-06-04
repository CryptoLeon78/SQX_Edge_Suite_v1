import json
import os
import zipfile
from pathlib import Path
from unittest.mock import patch

from api import server
from core.sqx142_ai_wizard import (
    AI_WIZARD_AI2_VERSION,
    AST_TYPE,
    CATALOG_TYPE,
    XML_ENTRY,
    build_ai_wizard_ast_from_prompt,
    build_ai_wizard_capability_catalog,
    create_ai_wizard_session,
    create_ai_wizard_session_draft,
    get_ai_wizard_session,
    list_ai_wizard_sessions,
    resolve_ai_wizard_draft_download,
)


MINIMAL_XML = """<?xml version="1.0" encoding="UTF-8"?>
<StrategyFile Version="3.9.130">
  <options>
    <StrategyName>New strategy</StrategyName>
    <Date>01/08/2020 08:24</Date>
  </options>
  <Strategy name="" engine="MetaTrader">
    <Description />
  </Strategy>
</StrategyFile>
"""


def _write_fake_sqx_root(tmp_path: Path) -> Path:
    root = tmp_path / "sqx142"
    ctemplate = root / "internal" / "ctemplate"
    examples = root / "internal" / "web" / "AlgoWizard" / "examples"
    blocks = root / "internal" / "extend" / "Code" / "MetaTrader4" / "blocks"
    custom = root / "custom_indicators" / "MetaTrader5" / "Indicators"
    ctemplate.mkdir(parents=True)
    examples.mkdir(parents=True)
    blocks.mkdir(parents=True)
    custom.mkdir(parents=True)
    (ctemplate / "parameterSets.xml").write_text(
        """
        <set name="CCIParamSet1"><paramCategory name="Default"><param key="_PERIOD_" name="Period" type="int" minValue="1" maxValue="10000" defaultValue="14" step="1"/></paramCategory></set>
        <set name="ValuesSet"><paramCategory name="Default"><param key="#Left#" name="Left" type="value"/><param key="#Right#" name="Right" type="value"/></paramCategory></set>
        """,
        encoding="utf-8",
    )
    (ctemplate / "conditions.xml").write_text(
        """
        <conditions>
          <category name="Moving Average" key="IndyComparisons">
            <item key="MARising" name="Moving Average is rising" returnType="boolean" parameterSet="CCIParamSet1" display="_TYPE_ Moving Average(_PERIOD_) is rising"/>
          </category>
          <category name="Comparisons" key="IndyComparisons">
            <item key="IsGreater" name="Is Greater" returnType="boolean" parameterSet="ValuesSet" display="#Left# &gt; #Right#"/>
            <item key="IsLower" name="Is Lower" returnType="boolean" parameterSet="ValuesSet" display="#Left# &lt; #Right#"/>
            <item key="CrossesAbove" name="Crosses Above" returnType="boolean" parameterSet="ValuesSet" display="#Left# crosses above #Right#"/>
            <item key="CrossesBelow" name="Crosses Below" returnType="boolean" parameterSet="ValuesSet" display="#Left# crosses below #Right#"/>
          </category>
        </conditions>
        """,
        encoding="utf-8",
    )
    block_items = "".join(
        f'<Item key="{key}" returnType="number" display="{key}"/>'
        for key in ["EMA", "SMA", "RSI", "BollingerBands", "Stochastic", "MACD", "CCI", "ADX", "High", "Low", "Close", "Number"]
    )
    comparison_items = "".join(
        f'<Item key="{key}" returnType="boolean" display="{key}"/>'
        for key in ["IsGreater", "IsLower", "CrossesAbove", "CrossesBelow"]
    )
    (ctemplate / "wizard.xml").write_text(
        f"""<Wizard><Steps><Step caption="Long entry" type="entry"><Blocks>{block_items}</Blocks><Comparisons>{comparison_items}</Comparisons></Step></Steps></Wizard>""",
        encoding="utf-8",
    )
    for name in ["EMACross.sqx", "breakout.sqx", "RangeBreakout.sqx", "mean_reversion.sqx"]:
        with zipfile.ZipFile(examples / name, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\n")
            archive.writestr(XML_ENTRY, MINIMAL_XML)
    (examples / "examples.json").write_text("[]", encoding="utf-8")
    (blocks / "EMA.tpl").write_text("redacted", encoding="utf-8")
    (custom / "SqRSI.mq5").write_text("redacted", encoding="utf-8")
    return root


def _assert_public_safe(payload: dict) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    assert r"C:\\" not in raw
    assert "Crack" not in raw
    assert "<StrategyFile" not in raw
    assert "EMACross.sqx" not in raw
    assert "OPENAI_API_KEY" not in raw
    assert "token=" not in raw.casefold()
    assert "password=" not in raw.casefold()


def test_ai2_catalog_is_sanitized_and_counts_fake_sources(tmp_path):
    sqx_root = _write_fake_sqx_root(tmp_path)

    report = build_ai_wizard_capability_catalog(tmp_path, sqx_root)

    assert report["ok"] is True
    assert report["version"] == AI_WIZARD_AI2_VERSION
    catalog = report["data"]["catalog"]
    assert catalog["type"] == CATALOG_TYPE
    assert catalog["accessPolicy"] == "read_only_allowlist_sanitized"
    assert catalog["hotSafe"]["userDataPolicy"] == "pending_stable_snapshot"
    assert catalog["counts"]["wizardBlocks"] >= 12
    assert catalog["counts"]["parameterSets"] == 2
    assert catalog["counts"]["examples"] == 4
    assert catalog["examples"]["items"][0]["hasStrategyPortfolioXml"] is True
    assert "name" not in catalog["examples"]["items"][0]
    assert report["privacy"]["raw_xml_returned"] is False
    _assert_public_safe(report)


def test_ai2_ast_validates_common_algowizard_blocks(tmp_path):
    sqx_root = _write_fake_sqx_root(tmp_path)
    with patch.dict(os.environ, {"SQX142_ROOT": str(sqx_root)}):
        report = build_ai_wizard_ast_from_prompt(
            {"prompt": "RSI and Bollinger mean reversion EURUSD H1 with SL/TP"},
            project_root=tmp_path,
        )

    assert report["ok"] is True
    ast = report["data"]["ast"]
    assert ast["type"] == AST_TYPE
    assert "RSI" in ast["catalogRefs"]["blockIds"]
    assert "BollingerBands" in ast["catalogRefs"]["blockIds"]
    assert report["data"]["validation"]["ok"] is True
    assert "blocked_not_draftable_yet" in report["warnings"]
    _assert_public_safe(report)


def test_ai2_sessions_persist_redacted_state_and_block_private_prompt(tmp_path):
    sqx_root = _write_fake_sqx_root(tmp_path)
    db_path = tmp_path / ".local" / "sqx142_ai_wizard" / "ai_wizard.sqlite"

    with patch.dict(os.environ, {"SQX142_ROOT": str(sqx_root)}):
        created = create_ai_wizard_session(
            tmp_path,
            {"prompt": "EMA cross trend-following EURUSD H1 with SL/TP"},
            db_path=db_path,
        )
        private = create_ai_wizard_session(
            tmp_path,
            {"prompt": r"EMA cross from C:\\Users\\Ivan SQX\\secret token=abcdef"},
            db_path=db_path,
        )
        listed = list_ai_wizard_sessions(tmp_path, db_path=db_path)
        loaded = get_ai_wizard_session(tmp_path, created["data"]["session"]["sessionId"], db_path=db_path)

    assert created["ok"] is True
    assert private["ok"] is False
    assert private["error"] == "prompt_not_public_safe"
    assert len(listed["data"]["sessions"]) == 1
    assert loaded["data"]["session"]["promptSummary"]
    assert "ema cross trend-following eurusd h1 with sl/tp" not in json.dumps(loaded["data"], ensure_ascii=False).casefold()
    _assert_public_safe(loaded)


def test_ai2_draft_generation_uses_session_and_downloads_by_draft_id(tmp_path):
    sqx_root = _write_fake_sqx_root(tmp_path)
    db_path = tmp_path / ".local" / "sqx142_ai_wizard" / "ai_wizard.sqlite"

    with patch.dict(os.environ, {"SQX142_ROOT": str(sqx_root)}):
        created = create_ai_wizard_session(
            tmp_path,
            {"prompt": "EMA cross trend-following EURUSD H1 with SL/TP"},
            db_path=db_path,
        )
        session_id = created["data"]["session"]["sessionId"]
        draft = create_ai_wizard_session_draft(tmp_path, session_id, db_path=db_path)
        path = resolve_ai_wizard_draft_download(tmp_path, draft["data"]["draft"]["draftId"], db_path=db_path)

    assert draft["ok"] is True
    assert draft["data"]["draft"]["draftId"].startswith("awd_")
    assert draft["data"]["draft"]["downloadUrl"].startswith("/api/sqx142/ai-wizard/drafts/")
    assert path is not None
    assert path.name == draft["data"]["draft"]["fileName"]
    assert zipfile.is_zipfile(path)
    _assert_public_safe(draft)


def test_ai2_routes_are_local_only_and_block_client_paths(tmp_path):
    client = server.app.test_client()
    safe_catalog = {
        "ok": True,
        "version": AI_WIZARD_AI2_VERSION,
        "data": {"catalog": {"type": CATALOG_TYPE, "counts": {}}},
        "privacy": {"local_paths_returned": False},
    }
    with patch.object(server, "build_ai_wizard_capability_catalog", return_value=safe_catalog):
        response = client.get("/api/sqx142/ai-wizard/catalog")
    assert response.status_code == 200
    assert response.get_json()["version"] == AI_WIZARD_AI2_VERSION

    blocked_remote = client.get(
        "/api/sqx142/ai-wizard/catalog",
        base_url="https://app.sqxedgesuite.org",
        headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert blocked_remote.status_code == 403
    assert blocked_remote.get_json()["error"] == "local_operator_required"

    blocked_path = client.post("/api/sqx142/ai-wizard/sessions", json={"prompt": "EMA cross", "path": "x"})
    assert blocked_path.status_code == 400
    assert blocked_path.get_json()["error"] == "client_path_fields_blocked"

    raw_catalog = client.post("/api/sqx142/ai-wizard/catalog/refresh", json={"includeRawXml": True})
    assert raw_catalog.status_code == 400
    assert raw_catalog.get_json()["error"] == "raw_catalog_request_blocked"
