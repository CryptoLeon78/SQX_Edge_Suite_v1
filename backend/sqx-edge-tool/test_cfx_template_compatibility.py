import zipfile
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from core.plan import Mining
from core.cfx_compatibility import audit_cfx_compatibility
from core.project_generator import generate_project
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
        # The Capa 1 v2 base intentionally keeps a few retest/cross-check
        # precision choices from the operator-edited SQX 142 project. Generated
        # customs are still normalized by xml_patcher before delivery.
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


def test_capa1_base_v2_matches_active_methodology():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    config = roots["config.xml"]
    task_titles = [task.get("title") for task in config.findall(".//Task")]
    databanks = [bank.get("name") for bank in config.findall(".//Databank")]

    assert "TICK REAL" in task_titles
    assert "HBP" not in task_titles
    assert "TICK" in databanks
    assert "HBP" not in databanks

    build = roots["Build-Task1.xml"]
    build_setup = build.find(".//Data/Setups/Setup")
    assert build_setup.get("dateFrom") == "2017.10.02"
    assert build_setup.get("dateTo") == "2023.01.01"
    assert build.find(".//RiskMoneyManagement//Method[@type='FixedSize']").get("use") == "true"
    assert build.find(".//RiskMoneyManagement//Method[@type='FixedAmount']").get("use") == "false"

    retest0 = roots["Retest-Task3.xml"]
    retest0_setup = retest0.find(".//Data/Setups/Setup")
    retest0_oos = retest0.find(".//Data/OutOfSample/Range")
    assert retest0_setup.get("dateFrom") == "2017.10.02"
    assert retest0_setup.get("dateTo") == "2025.01.01"
    assert retest0_oos.get("dateFrom") == "2023.01.01"
    assert retest0_oos.get("dateTo") == "2025.01.01"

    forward = roots["Retest-Task2.xml"]
    forward_setup = forward.find(".//Data/Setups/Setup")
    forward_ranges = forward.findall(".//Data/OutOfSample/Range")
    assert forward_setup.get("dateFrom") == "2025.01.01"
    assert forward_setup.get("dateTo") == "2026.04.08"
    assert len(forward_ranges) == 2
    assert forward_ranges[0].get("dateFrom") == "2025.01.01"
    assert forward_ranges[0].get("dateTo") == "2026.01.01"
    assert forward_ranges[1].get("dateFrom") == "2026.01.01"
    assert forward_ranges[-1].get("dateTo") == "2026.04.08"


def test_capa1_base_uses_phase1_review_views():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    config = roots["config.xml"]
    views = {
        databank.get("name"): databank.get("view")
        for databank in config.findall(".//Databank")
    }
    assert views["Results"] == "MINING FAST REVIEW"
    assert views["Initial population"] == "MINING FAST REVIEW"
    assert views["Last generation"] == "MINING FAST REVIEW"
    assert views["Strategies to improve"] == "MINING FAST REVIEW"
    assert views["Strategies to optimize"] == "MINING FAST REVIEW"
    assert views["RETEST 0"] == "RETEST QUICK REVIEW"
    assert views["retest 1"] == "RETEST QUICK REVIEW"
    assert views["Foward"] == "RETEST QUICK REVIEW"
    assert views["TICK"] == "RETEST ROBUST REVIEW"
    assert views["MC"] == "RETEST ROBUST REVIEW"
    assert views["MC2"] == "RETEST ROBUST REVIEW"
    assert views["Sequential"] == "RETEST ROBUST REVIEW"
    assert views["SPP"] == "RETEST ROBUST REVIEW"
    assert views["WFM"] == "RETEST ROBUST REVIEW"
    assert views["Monkey Test"] == "MC MONKEY RETEST"
    assert views["Syntetic"] == "MC SYNTHETIC RETEST"


def test_generate_project_names_build_task_and_applies_capa1_time_window():
    mining = Mining(num=91, phase=1, asset="AUDCAD", tf="H4", bs="BS_Volatilidad", dir="both")
    with tempfile.TemporaryDirectory() as tmp:
        out_path = generate_project(
            mining,
            str(TEMPLATE_DIR / "Capa1_Long.cfx"),
            tmp,
            capa=1,
            sqx_db_path=None,
        )
        roots = dict(_xml_roots(Path(out_path)))

    config = roots["config.xml"]
    build_task = next(task for task in config.findall(".//Task") if task.get("type") == "Build")
    assert build_task.get("title") == "Build BS_Volatilidad_v6 · Capa1 L+S H4"

    build = roots["Build-Task1.xml"]
    setup = build.find(".//Data/Setups/Setup")
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.01.01"
    params = {
        node.get("key"): node.text
        for node in build.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"LimitTimeRange", "SignalTimeRangeFrom", "SignalTimeRangeTo"}
    }
    assert params == {
        "LimitTimeRange": "true",
        "SignalTimeRangeFrom": "14400",
        "SignalTimeRangeTo": "72000",
    }

    tick_real = roots["AutomaticRetest-Task2.xml"]
    tick_setup = tick_real.find(".//Data/Setups/Setup")
    assert tick_setup.get("dateFrom") == "2017.10.02"
    assert tick_setup.get("dateTo") == "2023.12.31"

    retest1 = roots["Retest-Task1.xml"]
    retest1_setup = retest1.find(".//Data/Setups/Setup")
    assert retest1_setup.get("dateFrom") == "2010.01.01"
    assert retest1_setup.get("dateTo") == "2017.10.02"
    retest1_symbols = retest1.findall(".//Resources/Symbols/Symbol")
    assert {node.get("name") for node in retest1_symbols} == {"AUDCAD_dukascopy"}
    assert {node.get("source") for node in retest1_symbols} == {"2"}
    assert {node.get("broker") for node in retest1_symbols} == {"3"}
    assert {node.find("InstrumentInfo").get("broker") for node in retest1_symbols} == {"3"}
    assert [broker.get("id") for broker in retest1.findall(".//Resources/Brokers/Broker")] == ["3"]


def test_generate_project_applies_selected_market_side_to_all_tasks():
    template = str(TEMPLATE_DIR / "Capa1_Long.cfx")
    expected_titles = {
        "long": "Build BS_Volatilidad_v6 · Capa1 LONG H4",
        "short": "Build BS_Volatilidad_v6 · Capa1 SHORT H4",
        "both": "Build BS_Volatilidad_v6 · Capa1 L+S H4",
    }
    with tempfile.TemporaryDirectory() as tmp:
        for direction, expected_title in expected_titles.items():
            mining = Mining(num=94, phase=1, asset="AUDCAD", tf="H4", bs="BS_Volatilidad", dir=direction)
            out_path = generate_project(
                mining,
                template,
                tmp,
                capa=1,
                suffix=f"_{direction}",
                sqx_db_path=None,
            )
            roots = dict(_xml_roots(Path(out_path)))
            config = roots["config.xml"]
            build_task = next(task for task in config.findall(".//Task") if task.get("type") == "Build")
            assert build_task.get("title") == expected_title

            for name, root in roots.items():
                if name == "config.xml":
                    continue
                market_sides = {
                    node.get("type")
                    for node in root.findall(".//MarketSides")
                    if node.get("type")
                }
                if market_sides:
                    assert market_sides == {direction}, name


def test_generate_project_applies_intraday_time_window():
    mining = Mining(num=92, phase=1, asset="AUDCAD", tf="H1", bs="BS_Volatilidad", dir="long")
    with tempfile.TemporaryDirectory() as tmp:
        out_path = generate_project(
            mining,
            str(TEMPLATE_DIR / "Capa1_Long.cfx"),
            tmp,
            capa=1,
            sqx_db_path=None,
        )
        roots = dict(_xml_roots(Path(out_path)))
    build = roots["Build-Task1.xml"]
    params = {
        node.get("key"): node.text
        for node in build.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"SignalTimeRangeFrom", "SignalTimeRangeTo"}
    }
    assert params == {"SignalTimeRangeFrom": "7200", "SignalTimeRangeTo": "79200"}


def test_generate_project_defaults_to_sq_default_exact_symbol_for_user_downloads():
    mining = Mining(num=93, phase=1, asset="GBPJPY", tf="H1", bs="BS_Tendencia", dir="both")
    with tempfile.TemporaryDirectory() as tmp:
        out_path = generate_project(
            mining,
            str(TEMPLATE_DIR / "Capa1_Long.cfx"),
            tmp,
            capa=1,
            sqx_db_path=None,
        )
        roots = dict(_xml_roots(Path(out_path)))
        report = audit_cfx_compatibility(out_path)

    build = roots["Build-Task1.xml"]
    build_symbols = build.findall(".//Resources/Symbols/Symbol")
    assert {node.get("name") for node in build_symbols} == {"GBPJPY"}
    assert {node.get("source") for node in build_symbols} == {"0"}
    assert {node.get("broker") for node in build_symbols} == {"-1"}
    assert {node.find("InstrumentInfo").get("instrument") for node in build_symbols} == {"GBPJPY"}
    assert {node.find("InstrumentInfo").get("broker") for node in build_symbols} == {"-1"}
    assert {node.find("InstrumentInfo").get("dataType") for node in build_symbols} == {"1"}
    assert build.findall(".//Resources/Brokers/Broker") == []

    retest1 = roots["Retest-Task1.xml"]
    retest1_symbols = retest1.findall(".//Resources/Symbols/Symbol")
    assert {node.get("name") for node in retest1_symbols} == {"GBPJPY_dukascopy"}
    assert {node.get("source") for node in retest1_symbols} == {"2"}
    assert {node.get("broker") for node in retest1_symbols} == {"3"}
    assert report["hostProfile"] == "sq_default_cross_broker_oos2"
    assert report["failCount"] == 0


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


def test_patch_symbol_resources_keeps_source_id_separate_from_broker_id():
    root = ET.fromstring(
        """
        <Task>
          <Setup><Chart symbol="AUDCAD_dukascopy" timeframe="H4" /></Setup>
          <Resources><Symbols /><Brokers /><Sessions /></Resources>
        </Task>
        """
    )
    patch_symbol_resources(root, {
        "asset": "AUDCAD",
        "symbol": "AUDCAD_dukascopy",
        "instrument": "AUDCAD_dukascopy",
        "source_id": 2,
        "broker_id": 3,
        "broker_name": "[[Dukascopy]]",
        "broker_description": "Dukascopy",
        "broker_postfix": "_dukascopy",
        "broker_timezone": "EETUS",
        "tick_size": 0.0001,
        "tick_step": 0.00001,
        "spread": 1.4,
        "slippage": 0.0,
        "point_value": 100000.0,
        "data_type": 3,
        "u_symbol": "AUDCAD",
        "u_symbol_name": "AUDCAD",
    })

    symbol = root.find(".//Resources/Symbols/Symbol")
    info = symbol.find("InstrumentInfo")
    broker = root.find(".//Resources/Brokers/Broker")
    assert symbol.get("name") == "AUDCAD_dukascopy"
    assert symbol.get("source") == "2"
    assert symbol.get("broker") == "3"
    assert info.get("instrument") == "AUDCAD_dukascopy"
    assert info.get("broker") == "3"
    assert broker.get("id") == "3"


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
