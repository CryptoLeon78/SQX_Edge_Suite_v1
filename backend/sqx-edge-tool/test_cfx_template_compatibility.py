import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from core.xml_patcher import (
    patch_backtest_precision,
    patch_embedded_strategy_metadata,
    patch_no_session,
    patch_symbol_resources,
)


TOOL_ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = TOOL_ROOT / "templates"


def _xml_roots(cfx_path: Path):
    with zipfile.ZipFile(cfx_path) as archive:
        for name in archive.namelist():
            if name.endswith(".xml"):
                yield name, ET.fromstring(archive.read(name))


def _resource_issues(cfx_path: Path) -> list[str]:
    issues: list[str] = []
    for name, root in _xml_roots(cfx_path):
        if name == "config.xml":
            continue
        charts = [chart.get("symbol") for chart in root.findall(".//Setup/Chart") if chart.get("symbol")]
        chart_symbols = set(charts)
        symbol_nodes = root.findall(".//Resources/Symbols/Symbol")
        symbol_names = {node.get("name") for node in symbol_nodes}
        brokers = {broker.get("id") for broker in root.findall(".//Resources/Brokers/Broker")}
        resource_sessions = root.findall(".//Resources/Sessions/Session")
        if resource_sessions:
            names = ", ".join(sorted({session.get("name") or "" for session in resource_sessions}))
            issues.append(f"{name}: stale resource sessions remain: {names}")
        for param in root.findall(".//BuildTradingOptions/Params/Param[@key='MarketOpenSession']"):
            if (param.text or "") != "No Session":
                issues.append(f"{name}: stale MarketOpenSession {param.text!r}")
        for setup in root.findall(".//Setup"):
            if setup.get("testPrecision") != "2":
                issues.append(f"{name}: non-tick testPrecision {setup.get('testPrecision')!r}")
        xml_text = ET.tostring(root, encoding="unicode")
        if "Futures_Commodities1" in xml_text:
            issues.append(f"{name}: unresolved SQX 142 session Futures_Commodities1 remains")
        for node in root.findall(".//BackupStrategyTemplate//symbol"):
            embedded_symbol = node.text or ""
            if embedded_symbol not in chart_symbols:
                issues.append(f"{name}: embedded strategy symbol {embedded_symbol} does not match charts")
        if not brokers:
            issues.append(f"{name}: missing brokers")
        for chart in charts:
            if chart not in symbol_names:
                issues.append(f"{name}: chart {chart} missing from Resources/Symbols")
        for node in symbol_nodes:
            info = node.find("InstrumentInfo")
            if (node.get("name") or "").startswith("[["):
                issues.append(f"{name}: unresolved placeholder symbol {node.get('name')}")
            if node.get("precision") != "TICK":
                issues.append(f"{name}: non-tick symbol precision {node.get('precision')!r} for {node.get('name')}")
            if node.get("timezone") != "EETUS":
                issues.append(f"{name}: non-Darwinex timezone {node.get('timezone')!r} for {node.get('name')}")
            if node.get("broker") not in brokers:
                issues.append(f"{name}: symbol broker {node.get('broker')} missing for {node.get('name')}")
            if info is None:
                issues.append(f"{name}: missing InstrumentInfo for {node.get('name')}")
                continue
            if info.get("broker") not in brokers:
                issues.append(f"{name}: InstrumentInfo broker {info.get('broker')} missing for {node.get('name')}")
        for strategy_type in root.findall(".//StrategyType"):
            for attr in ("templateFile", "strategyFile"):
                value = strategy_type.get(attr) or ""
                if ":\\" in value or ":/" in value:
                    issues.append(f"{name}: absolute {attr} remains in StrategyType")
    return issues


def test_base_cfx_templates_have_sqx142_resolvable_resources():
    for template_name in ("Capa1_Long.cfx", "Capa2_Base.cfx"):
        issues = _resource_issues(TEMPLATE_DIR / template_name)
        assert issues == []


def test_base_cfx_templates_are_labeled_as_sqx142_base():
    expected = {
        "Capa1_Long.cfx": "Capa1_Long_SQX142_Base",
        "Capa2_Base.cfx": "Capa2_Base_SQX142_Base",
    }
    for template_name, project_name in expected.items():
        config = dict(_xml_roots(TEMPLATE_DIR / template_name))["config.xml"]
        assert config.get("name") == project_name


def test_patch_symbol_resources_rebuilds_empty_brokers_for_sqx142():
    root = ET.fromstring(
        """
        <Task>
          <Setup><Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" /></Setup>
          <Resources>
            <Symbols>
              <Symbol name="[[Dow Jones Industrial Average]]" source="5" broker="-1">
                <InstrumentInfo instrument="[[Dow Jones Industrial Average]]" broker="-1" />
              </Symbol>
            </Symbols>
            <Brokers />
            <Sessions>
              <Session name="Futures_Commodities1" />
            </Sessions>
          </Resources>
        </Task>
        """
    )
    patched = patch_symbol_resources(root, {
        "asset": "USDJPY",
        "symbol": "USDJPY_darwinex",
        "instrument": "USDJPY_darwinex",
        "broker_id": 4,
        "broker_name": "[[Darwinex]]",
        "broker_description": "Darwinex CFDs",
        "broker_postfix": "_darwinex",
        "broker_timezone": "EETUS",
        "tick_size": 0.01,
        "tick_step": 0.001,
        "spread": 1.4,
        "slippage": 0.0,
        "point_value": 1000.0,
        "data_type": 3,
        "u_symbol": "USDJPY",
        "u_symbol_name": "USDJPY",
    })

    assert patched == 1
    assert root.find(".//Resources/Brokers/Broker").get("id") == "4"
    assert [broker.get("id") for broker in root.findall(".//Resources/Brokers/Broker")] == ["4"]
    symbol = root.find(".//Resources/Symbols/Symbol")
    info = symbol.find("InstrumentInfo")
    assert symbol.get("name") == "USDJPY_darwinex"
    assert symbol.get("broker") == "4"
    assert symbol.get("precision") == "TICK"
    assert symbol.get("timezone") == "EETUS"
    assert info.get("instrument") == "USDJPY_darwinex"
    assert info.get("broker") == "4"
    assert root.find(".//Resources/Sessions").text is None
    assert root.findall(".//Resources/Sessions/Session") == []


def test_patch_symbol_resources_uses_available_data_range_when_task_is_older_than_sqx_data():
    root = ET.fromstring(
        """
        <Task>
          <Setup dateFrom="2010.01.01" dateTo="2016.12.31">
            <Chart symbol="AUDCAD_darwinex" timeframe="H4" />
          </Setup>
          <Resources><Symbols /><Brokers /><Sessions /></Resources>
        </Task>
        """
    )

    patch_symbol_resources(root, {
        "asset": "AUDCAD",
        "symbol": "AUDCAD_darwinex",
        "instrument": "AUDCAD_darwinex",
        "broker_id": 4,
        "broker_name": "[[Darwinex]]",
        "broker_description": "Darwinex CFDs",
        "broker_timezone": "EETUS",
        "broker_postfix": "_darwinex",
        "tick_size": 0.0001,
        "tick_step": 0.00001,
        "point_value": 72157.360772,
        "data_type": 3,
        "description": "Currency",
        "sector": "Currency",
        "date_from_ms": "1506902400000",
        "date_to_ms": "1775617199907",
        "u_symbol": "AUDCAD",
        "u_symbol_name": "AUDCAD",
    })

    symbol = root.find(".//Resources/Symbols/Symbol")
    assert symbol.get("dateFrom") == "1506902400000"
    assert symbol.get("dateTo") == "1775617199907"


def test_patch_no_session_clears_stale_market_open_session():
    root = ET.fromstring(
        """
        <Task>
          <Setup session="Futures_Commodities1" />
          <Options>
            <BuildTradingOptions>
              <Params>
                <Param key="MarketOpenSession" className="MarketOpenSession">Futures_Commodities1</Param>
              </Params>
            </BuildTradingOptions>
          </Options>
          <Resources>
            <Sessions><Session name="Futures_Commodities1" /></Sessions>
          </Resources>
        </Task>
        """
    )

    patched = patch_no_session(root)

    assert patched == 3
    assert root.find(".//Setup").get("session") == "No Session"
    assert root.find(".//Param[@key='MarketOpenSession']").text == "No Session"
    assert root.findall(".//Resources/Sessions/Session") == []


def test_patch_embedded_strategy_metadata_tracks_generated_symbol():
    root = ET.fromstring(
        """
        <Task>
          <Resources>
            <BackupStrategyTemplate>
              <StrategyFile>
                <Strategy>
                  <StrategyName>Old XAU</StrategyName>
                  <StrategyClassName>Old_XAU</StrategyClassName>
                  <Datas><data><symbol>XAUUSD_darwinex</symbol></data></Datas>
                </Strategy>
              </StrategyFile>
            </BackupStrategyTemplate>
          </Resources>
        </Task>
        """
    )

    patched = patch_embedded_strategy_metadata(root, "USDJPY_darwinex", "H4")

    assert patched == 3
    assert root.find(".//BackupStrategyTemplate//symbol").text == "USDJPY_darwinex"
    assert root.find(".//BackupStrategyTemplate//StrategyName").text == "SQXEDGE_TEMPLATE_USDJPY_H4"
    assert root.find(".//BackupStrategyTemplate//StrategyClassName").text == "SQXEDGE_TEMPLATE_USDJPY_H4"


def test_patch_backtest_precision_sets_tick_precision_for_sqx142():
    root = ET.fromstring(
        """
        <Task>
          <Setup testPrecision="1" />
          <Setup testPrecision="2" />
          <Setup />
        </Task>
        """
    )

    patched = patch_backtest_precision(root)

    assert patched == 2
    assert [setup.get("testPrecision") for setup in root.findall(".//Setup")] == ["2", "2", "2"]
