import json
import os
import zipfile
from pathlib import Path
from unittest.mock import patch

from api import server
from core.sqx142_ai_wizard import (
    AI_WIZARD_AI2_VERSION,
    AI_WIZARD_AI3_CATALOG_VERSION,
    AI_WIZARD_AI3_COMPILER_VERSION,
    AI_WIZARD_AI4_RSI_COMPILER_VERSION,
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

AI3_SIGNAL_XML = """<?xml version="1.0" encoding="UTF-8"?>
<StrategyFile Version="3.9.130">
  <options>
    <StrategyName>New strategy</StrategyName>
    <Date>01/08/2020 08:24</Date>
  </options>
  <Strategy name="" engine="MetaTrader" negateRules="false">
    <Description />
    <Rules>
      <Rule name="Trading signals" type="Signal" everyTick="false">
        <signals>
          <signal variable="33333333-1111-1111-3333-333333333333">
            <Item key="CrossesAbove" name="Crosses Above" display="#Left# crosses above #Right#" mI="Comparisons" returnType="boolean" categoryType="operators" />
          </signal>
          <signal variable="33333333-2222-1111-3333-333333333333">
            <Item key="CrossesBelow" name="Crosses Below" display="#Left# crosses below #Right#" mI="Comparisons" returnType="boolean" categoryType="operators" />
          </signal>
        </signals>
      </Rule>
      <Rule name="Long entry" type="IfThen" everyTick="false">
        <Block />
        <Item key="EnterAtMarket" name="(MKT) Enter at market" display="EnterAtMarket" mI="Open" returnType="order" categoryType="other">
          <Param key="#Direction#" name="Direction" type="int">1</Param>
          <Param key="#ProfitTarget.ProfitTarget#" name="Profit Target" type="double"><Param key="#Value#" name="Value" type="double">70</Param></Param>
          <Param key="#StopLoss.StopLoss#" name="Stop Loss" type="double"><Param key="#Value#" name="Value" type="double">50</Param></Param>
        </Item>
      </Rule>
      <Rule name="Short entry" type="IfThen" everyTick="false">
        <Block />
        <Item key="EnterAtMarket" name="(MKT) Enter at market" display="EnterAtMarket" mI="Open" returnType="order" categoryType="other">
          <Param key="#Direction#" name="Direction" type="int">-1</Param>
          <Param key="#ProfitTarget.ProfitTarget#" name="Profit Target" type="double"><Param key="#Value#" name="Value" type="double">70</Param></Param>
          <Param key="#StopLoss.StopLoss#" name="Stop Loss" type="double"><Param key="#Value#" name="Value" type="double">50</Param></Param>
        </Item>
      </Rule>
    </Rules>
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
          <category name="Keltner Channel" key="IndyComparisons">
            <item key="KCUpperRising" name="Upper band is rising" returnType="boolean" parameterSet="CCIParamSet1" display="Keltner Channel(_MA_PERIOD_, _ATR_PERIOD_, _MULTIPLIER_).Upper is rising"/>
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
        for key in ["EMA", "SMA", "RSI", "BollingerBands", "Stochastic", "MACD", "CCI", "ADX", "ATR", "Open", "High", "Low", "Close", "Number"]
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
            archive.writestr(XML_ENTRY, AI3_SIGNAL_XML if name == "EMACross.sqx" else MINIMAL_XML)
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
    assert catalog["counts"]["semanticItems"] >= catalog["counts"]["wizardBlocks"] + catalog["counts"]["conditionItems"]
    assert catalog["counts"]["semanticFamilies"] >= 3
    assert catalog["semanticCatalog"]["version"] == AI_WIZARD_AI3_CATALOG_VERSION
    assert catalog["semanticCatalog"]["policy"] == "expanded_planning_catalog_not_universal_sqx_generation"
    assert {"id": "rsi_mean_reversion", "label": "RSI mean reversion", "version": AI_WIZARD_AI4_RSI_COMPILER_VERSION} in catalog["semanticCatalog"]["draftableFamilies"]
    assert "rsi_mean_reversion" in catalog["compilerSupport"]["draftablePatterns"]
    assert catalog["compilerSupport"]["phase"] == AI_WIZARD_AI4_RSI_COMPILER_VERSION
    semantic_ids = {item["id"] for item in catalog["semanticCatalog"]["items"]}
    assert {"MARising", "KCUpperRising", "EnterAtMarket"}.issubset(semantic_ids)
    assert any(item["id"] == "RSI" and item["compilerSupport"] == "draftable_rsi_mean_reversion" for item in catalog["semanticCatalog"]["items"])
    assert catalog["examples"]["items"][0]["hasStrategyPortfolioXml"] is True
    assert catalog["examples"]["featureCount"] >= 3
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
    assert "blocked_multi_family_compiler_not_ready" in report["warnings"]
    assert "blocked_not_draftable_yet" in report["warnings"]
    _assert_public_safe(report)


def test_ai4_rsi_mean_reversion_compiles_long_short_and_both(tmp_path):
    sqx_root = _write_fake_sqx_root(tmp_path)
    db_path = tmp_path / ".local" / "sqx142_ai_wizard" / "ai_wizard.sqlite"
    prompts = {
        "long_only": "RSI mean reversion EURUSD H1 long SL 100 TP 200",
        "short_only": "RSI mean reversion EURUSD H1 short SL 100 TP 200",
        "both": "RSI mean reversion EURUSD H1 SL 100 TP 200",
    }

    reports = {}
    drafts = {}
    with patch.dict(os.environ, {"SQX142_ROOT": str(sqx_root)}):
        for expected_direction, prompt in prompts.items():
            report = build_ai_wizard_ast_from_prompt({"prompt": prompt}, project_root=tmp_path)
            created = create_ai_wizard_session(tmp_path, {"prompt": prompt}, db_path=db_path)
            draft = create_ai_wizard_session_draft(tmp_path, created["data"]["session"]["sessionId"], db_path=db_path)
            reports[expected_direction] = report
            drafts[expected_direction] = draft

    for expected_direction, report in reports.items():
        assert report["ok"] is True
        ast = report["data"]["ast"]
        assert ast["direction"] == expected_direction
        assert ast["compiler"]["draftable"] is True
        assert ast["compiler"]["templateClass"] == "rsi_mean_reversion"
        assert ast["compiler"]["version"] == AI_WIZARD_AI4_RSI_COMPILER_VERSION
        assert ast["compiler"]["universalPromptIntake"] is True
        assert ast["compiler"]["universalSqxGeneration"] is False
        assert ast["actions"]["risk"]["manualReviewRequired"] is True
        assert "RSI" in ast["catalogRefs"]["blockIds"]
        _assert_public_safe(report)
        assert drafts[expected_direction]["ok"] is True
        assert drafts[expected_direction]["data"]["draft"]["compilerFamily"] == "rsi_mean_reversion"
        assert drafts[expected_direction]["data"]["draft"]["compilerVersion"] == AI_WIZARD_AI4_RSI_COMPILER_VERSION
        _assert_public_safe(drafts[expected_direction])

    generated = resolve_ai_wizard_draft_download(tmp_path, drafts["both"]["data"]["draft"]["draftId"], db_path=db_path)
    assert generated is not None
    assert zipfile.is_zipfile(generated)
    with zipfile.ZipFile(generated) as archive:
        assert sorted(archive.namelist()) == ["META-INF/MANIFEST.MF", XML_ENTRY]
        xml = archive.read(XML_ENTRY).decode("utf-8")
    assert "SQX Edge AI4 RSI Mean-Reversion Compiler draft" in xml
    assert "SQXEdgeAI2_EURUSD_H1_RSI" in xml
    assert 'Item key="RSI"' in xml
    assert 'Item key="IsLower"' in xml
    assert 'Item key="IsGreater"' in xml
    assert ">30<" in xml
    assert ">70<" in xml
    assert ">100<" in xml
    assert ">200<" in xml


def test_ai3_expanded_catalog_understands_condition_items_without_draft(tmp_path):
    sqx_root = _write_fake_sqx_root(tmp_path)
    db_path = tmp_path / ".local" / "sqx142_ai_wizard" / "ai_wizard.sqlite"
    prompt = "Keltner Channel upper band rising EURUSD H1 with SL/TP"
    with patch.dict(os.environ, {"SQX142_ROOT": str(sqx_root)}):
        report = build_ai_wizard_ast_from_prompt(
            {"prompt": prompt},
            project_root=tmp_path,
        )
        created = create_ai_wizard_session(tmp_path, {"prompt": prompt}, db_path=db_path)
        draft = create_ai_wizard_session_draft(tmp_path, created["data"]["session"]["sessionId"], db_path=db_path)

    assert report["ok"] is True
    ast = report["data"]["ast"]
    assert "KCUpperRising" in ast["catalogRefs"]["semanticIds"]
    assert not any(item in ast["catalogRefs"]["semanticIds"] for item in ("KCLowerFalling", "KCUpperFalling"))
    assert ast["promptUnderstanding"]["recognized"] is True
    assert ast["compiler"]["draftable"] is False
    assert ast["compiler"]["universalPromptIntake"] is True
    assert "blocked_not_draftable_yet" in report["warnings"]
    assert created["ok"] is True
    assert draft["ok"] is False
    assert draft["error"] == "blocked_not_draftable_yet"
    assert "blocked_not_draftable_yet" in draft["blockers"]
    assert "draft" not in draft.get("data", {})
    _assert_public_safe(report)
    _assert_public_safe(draft)


def test_ai4_does_not_turn_keltner_mean_reversion_into_rsi_draft(tmp_path):
    sqx_root = _write_fake_sqx_root(tmp_path)
    db_path = tmp_path / ".local" / "sqx142_ai_wizard" / "ai_wizard.sqlite"
    prompt = "Keltner Channel mean reversion EURUSD H1 SL 100 TP 200"
    with patch.dict(os.environ, {"SQX142_ROOT": str(sqx_root)}):
        report = build_ai_wizard_ast_from_prompt({"prompt": prompt}, project_root=tmp_path)
        created = create_ai_wizard_session(tmp_path, {"prompt": prompt}, db_path=db_path)
        draft = create_ai_wizard_session_draft(tmp_path, created["data"]["session"]["sessionId"], db_path=db_path)

    ast = report["data"]["ast"]
    assert report["ok"] is True
    assert "RSI" not in ast["catalogRefs"]["blockIds"]
    assert "Keltner Channel" in ast["catalogRefs"]["semanticFamilies"]
    assert ast["promptUnderstanding"]["recognized"] is True
    assert ast["compiler"]["draftable"] is False
    assert ast["compiler"]["templateClass"] == ""
    assert "blocked_not_draftable_yet" in report["warnings"]
    assert draft["ok"] is False
    assert draft["error"] == "blocked_not_draftable_yet"
    _assert_public_safe(report)
    _assert_public_safe(draft)


def test_ai3_spanish_candle_prompt_compiles_traceable_draft(tmp_path):
    sqx_root = _write_fake_sqx_root(tmp_path)
    db_path = tmp_path / ".local" / "sqx142_ai_wizard" / "ai_wizard.sqlite"
    prompt = (
        "tres velas rojas y en la siguiente verde una vela martillo entramos a mercado "
        "en la segunda vela verde temporalidad h1 en largo en SP500 con filtro atr. "
        "Stop de 100 pips y tp de 200"
    )

    with patch.dict(os.environ, {"SQX142_ROOT": str(sqx_root)}):
        report = build_ai_wizard_ast_from_prompt({"prompt": prompt}, project_root=tmp_path)
        created = create_ai_wizard_session(tmp_path, {"prompt": prompt}, db_path=db_path)
        draft = create_ai_wizard_session_draft(tmp_path, created["data"]["session"]["sessionId"], db_path=db_path)

    assert report["ok"] is True
    ast = report["data"]["ast"]
    assert ast["asset"] == "US500"
    assert ast["timeframe"] == "H1"
    assert ast["direction"] == "long_only"
    assert ast["actions"]["risk"]["stopLossPips"] == 100
    assert ast["actions"]["risk"]["takeProfitPips"] == 200
    assert ast["recognized"]["pattern"]["type"] == "candlestick_sequence"
    assert ast["recognized"]["pattern"]["redCandles"] == 3
    assert ast["recognized"]["pattern"]["requiresHammer"] is True
    assert ast["recognized"]["pattern"]["entryTiming"] == "market_on_second_green_after_confirmation"
    assert ast["recognized"]["filters"][0]["blockId"] == "ATR"
    assert ast["compiler"]["draftable"] is True
    assert ast["compiler"]["templateClass"] == "candle_atr_sequence"
    assert ast["compiler"]["version"] == AI_WIZARD_AI3_COMPILER_VERSION
    assert ast["compiler"]["universalPromptIntake"] is True
    assert ast["compiler"]["universalSqxGeneration"] is False
    assert ast["interpreter"]["rawPromptPersisted"] is False
    assert "EMA" not in ast["catalogRefs"]["blockIds"]
    assert "BollingerBands" not in ast["catalogRefs"]["blockIds"]
    assert created["ok"] is True
    assert draft["ok"] is True
    generated = resolve_ai_wizard_draft_download(tmp_path, draft["data"]["draft"]["draftId"], db_path=db_path)
    assert generated is not None
    assert zipfile.is_zipfile(generated)
    with zipfile.ZipFile(generated) as archive:
        assert sorted(archive.namelist()) == ["META-INF/MANIFEST.MF", XML_ENTRY]
        xml = archive.read(XML_ENTRY).decode("utf-8")
    assert "SQX Edge AI3 Universal Prompt Compiler draft" in xml
    assert "SQXEdgeAI2_US500_H1_CandlePattern_ATR_Close" in xml
    assert 'Item key="talib_ATR"' in xml
    assert 'Item key="Close"' in xml
    assert 'Item key="Open"' in xml
    assert ">100<" in xml
    assert ">200<" in xml
    _assert_public_safe(report)
    _assert_public_safe(draft)


class _FakeAiWizardModel:
    model = "fake-local-model"

    def status(self, *, auto_start=False):
        return {"available": True, "model": self.model}

    def chat_json(self, *, messages, schema, model=None):
        return {
            "asset": "US500",
            "timeframe": "H1",
            "direction": "long_only",
            "intent": "candlestick_sequence",
            "blocks": ["Open", "Close", "High", "Low"],
            "filters": ["ATR"],
            "risk": {"stopLossPips": 100, "takeProfitPips": 200},
            "candlePattern": {
                "type": "candlestick_sequence",
                "redCandles": 3,
                "requiresHammer": True,
                "entryTiming": "market_on_second_green_after_confirmation",
            },
            "confidence": 0.86,
        }


def test_ai3_local_model_interpreter_feeds_ast_without_persisting_raw(tmp_path):
    sqx_root = _write_fake_sqx_root(tmp_path)
    with patch.dict(os.environ, {"SQX142_ROOT": str(sqx_root)}):
        report = build_ai_wizard_ast_from_prompt(
            {"prompt": "setup de velas para indice americano h1 con filtro atr", "compilerMode": "ollama"},
            project_root=tmp_path,
            llm_client=_FakeAiWizardModel(),
        )

    assert report["ok"] is True
    ast = report["data"]["ast"]
    assert ast["asset"] == "US500"
    assert ast["timeframe"] == "H1"
    assert ast["interpreter"]["source"] == "ollama_ast"
    assert ast["interpreter"]["model"] == "fake-local-model"
    assert ast["interpreter"]["rawPromptPersisted"] is False
    assert ast["interpreter"]["rawResponsePersisted"] is False
    assert ast["compiler"]["templateClass"] == "candle_atr_sequence"
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
            {"prompt": r"EMA cross from C:\\Users\\Operator\\secret token=abcdef"},
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
