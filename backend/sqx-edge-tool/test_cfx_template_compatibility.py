import hashlib
import sqlite3
import zipfile
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from core.plan import Mining
from core.blocksettings import load_blocksettings_manifest
from core.cfx_compatibility import audit_cfx_compatibility
from core.project_generator import CAPA_TASK_MAPS, _bound_retest_period_to_available_data, generate_project
from core.xml_patcher import (
    RETEST_PERIODS,
    patch_backtest_precision,
    patch_custom_block_resources,
    patch_embedded_strategy_metadata,
    patch_no_session,
    patch_symbol_resources,
)


def _create_hybrid_xau_data_db(path: Path) -> None:
    commission = '<Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">6</Param></Params></Method>'
    swap = '<Swap use="true" type="money" long="-65" short="45" tripleSwapOn="WEDNESDAY" rolloutHour="23:00"/>'
    duk_commission = '<Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">0.00</Param></Params></Method>'
    duk_swap = '<Swap use="true" type="points" long="-460.53" short="247.5" tripleSwapOn="NEVER" rolloutHour="23:00"/>'
    con = sqlite3.connect(path)
    try:
        con.executescript(
            """
            CREATE TABLE BROKER (ID INTEGER PRIMARY KEY, NAME TEXT, SYSTEM BOOLEAN, DESC TEXT, STOCKPICKER_USE INTEGER, MT_USE INTEGER, MT_TIMEZONE TEXT, POSTFIX TEXT);
            CREATE TABLE INSTRUMENTS (
              INSTRUMENT TEXT PRIMARY KEY, DESCRIPTION TEXT, POINTVALUE REAL, TICKSIZE REAL, TICKSTEP REAL,
              DEFAULTSPREAD REAL, COMMISSIONS TEXT, DATATYPE INT, EXCHANGE TEXT, COUNTRY TEXT, SECTOR TEXT,
              DEFAULTSLIPPAGE REAL, SWAP TEXT, ORDERSIZEMULTIPLIER REAL, ORDERSIZESTEP REAL, BROKER_ID INT,
              MIN_DISTANCE REAL
            );
            CREATE TABLE DATA (
              ID INTEGER PRIMARY KEY, SOURCEDATA_ID INTEGER, CONNECTION TEXT, SYMBOL TEXT, INSTRUMENT TEXT,
              TIMEFRAME TEXT, TIMEZONE TEXT, FILENAME TEXT, DATEFROM LONG, DATETO LONG, DATATYPE INT,
              ROWS INT, DECIMALS INT, SOURCE INT, SECONDS_RECORDS LONG, USYMBOL TEXT, USYMBOLNAME TEXT,
              REMOVE_WEEKENDS INT, SHOW INT, BASKET_ID INT, BROKER_ID INT
            );
            """
        )
        con.executemany(
            "INSERT INTO BROKER (ID,NAME,SYSTEM,DESC,MT_TIMEZONE,POSTFIX) VALUES (?,?,?,?,?,?)",
            [
                (3, "[[Dukascopy]]", True, "Dukascopy", "EETUS", "_dukascopy"),
                (4, "[[Darwinex]]", True, "Darwinex CFDs", "EETUS", "_darwinex"),
            ],
        )
        con.executemany(
            """
            INSERT INTO INSTRUMENTS (
              INSTRUMENT,DESCRIPTION,POINTVALUE,TICKSIZE,TICKSTEP,DEFAULTSPREAD,COMMISSIONS,DATATYPE,
              EXCHANGE,COUNTRY,SECTOR,DEFAULTSLIPPAGE,SWAP,ORDERSIZEMULTIPLIER,ORDERSIZESTEP,BROKER_ID,MIN_DISTANCE
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            [
                ("XAUUSD_darwinex", "Futures_Commodities", 100.0, 0.01, 0.01, 30.0, commission, 4, "", "", "Commodities", 0.0, swap, 1.0, 0.01, 4, 0.0),
                ("XAUUSD_dukascopy", "FX_Commodities", 100.0, 0.001, 0.001, 361.0, duk_commission, 4, "", "", "Commodities", 500.0, duk_swap, 1.0, 0.01, 3, 0.0),
            ],
        )
        con.execute(
            """
            INSERT INTO DATA (
              SOURCEDATA_ID,CONNECTION,SYMBOL,INSTRUMENT,TIMEFRAME,TIMEZONE,FILENAME,DATEFROM,DATETO,DATATYPE,
              ROWS,DECIMALS,SOURCE,SECONDS_RECORDS,USYMBOL,USYMBOLNAME,REMOVE_WEEKENDS,SHOW,BASKET_ID,BROKER_ID
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                0,
                "",
                "XAUUSD_dukascopy",
                "XAUUSD_darwinex",
                "TICK",
                "EETUS",
                "",
                1262311321950,
                1776049199924,
                1,
                644187170,
                2,
                2,
                0,
                "XAUUSD",
                "XAUUSD",
                0,
                1,
                -1,
                4,
            ),
        )
        con.commit()
    finally:
        con.close()


TOOL_ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = TOOL_ROOT / "templates"
C1_FASTEST_ROBUSTNESS_TEST_PRECISION = "1"
C1_TICK_TEST_PRECISION = "4"


def _blocksetting_entry(canonical_id: str) -> dict:
    manifest = load_blocksettings_manifest()
    return next(entry for entry in manifest["entries"] if entry["canonicalId"] == canonical_id)


def _active_building_block_keys(blocks: ET.Element) -> list[str]:
    building_blocks = blocks.find("BuildingBlocks")
    assert building_blocks is not None
    return [
        block.get("key")
        for block in building_blocks.findall("Block")
        if block.get("key")
        and block.get("key") not in {"#Left#", "#Right#"}
        and str(block.get("use")).lower() == "true"
    ]


def _assert_retest_passive_generation_contract(
    task: ET.Element,
    expected_improve_databank: str,
    *,
    expected_exit_after_bars: str = "true",
    expected_enabled_exits: set[str] | None = None,
    expected_blocks_version: str | None = "142.2336",
    expect_no_signal_or_stoplimit_blocks: bool = True,
) -> None:
    parts = task.find(".//PartsToImprove")
    assert parts is not None
    for group_name in ("EntryRules", "OrderTypes", "ExitRules"):
        group = parts.find(group_name)
        assert group is not None
        assert group.find("LongImprovement").get("use") == "false"
        assert group.find("ShortImprovement").get("use") == "false"

    strategy_type = task.find(".//WhatToBuild/StrategyType")
    assert strategy_type is not None
    assert strategy_type.get("improveDatabank") == expected_improve_databank
    assert strategy_type.get("improveType") == "strategy"
    assert strategy_type.get("architecture") == "sq4"

    build_mode = task.find(".//WhatToBuild/BuildMode")
    assert build_mode is not None
    assert build_mode.get("generationType") == "random-generation"
    assert build_mode.findtext("ShowLastGenerationDatabank") == "false"
    assert build_mode.findtext("FreshBloodReplaceSimilar") == "false"
    assert build_mode.findtext("FreshBloodReplaceWeakest") == "false"
    assert build_mode.find("EvoRestartOnFinish").get("status") == "false"
    assert build_mode.find("EvoRestartOnStagnation").get("status") == "false"

    blocks = next(
        (candidate for candidate in task.findall(".//Blocks") if candidate.find("OrderTypes") is not None),
        None,
    )
    assert blocks is not None
    if expected_blocks_version is not None:
        assert blocks.get("version") == expected_blocks_version
    order_types = {
        block.get("key"): block.get("use")
        for block in blocks.findall("./OrderTypes/Block")
        if block.get("key")
    }
    assert order_types == {
        "EnterAtMarket": "true",
        "EnterReverseAtMarket": "false",
        "EnterAtStop": "false",
        "EnterAtLimit": "false",
    }
    exit_types = {
        block.get("key"): (block.get("use"), block.get("probability"))
        for block in blocks.findall("./ExitTypes/Block")
        if block.get("key")
    }
    assert exit_types["ExitAfterBars.ExitAfterBars"][0] == expected_exit_after_bars
    enabled_exits = expected_enabled_exits or set()
    for key in enabled_exits:
        assert exit_types[key][0] == "true"
    assert all(
        use == "false"
        for key, (use, _) in exit_types.items()
        if key
        not in {"ExitAfterBars.ExitAfterBars", *enabled_exits}
    )
    assert "ExitAfterDays" not in ET.tostring(blocks, encoding="unicode")
    assert "ExitAfterTradingDays" not in ET.tostring(blocks, encoding="unicode")

    active_blocks = [
        block
        for block in blocks.findall(".//BuildingBlocks/Block")
        if str(block.get("use", "")).lower() == "true"
    ]
    assert active_blocks
    if expect_no_signal_or_stoplimit_blocks:
        assert not [block for block in active_blocks if block.get("category") == "signals"]
        assert not [block for block in active_blocks if block.get("category") == "stopLimitBlocks"]
    assert [block for block in active_blocks if block.get("category") == "indicators"]
    custom_data = blocks.find("CustomData")
    assert custom_data is not None
    assert custom_data.get("showAll") == "false"
    assert list(custom_data) == []


def _assert_retest1_passive_generation_contract(retest1: ET.Element) -> None:
    _assert_retest_passive_generation_contract(retest1, expected_improve_databank="RETEST 0")


def _assert_tick_real_passive_generation_contract(
    tick_real: ET.Element,
    *,
    expected_exit_after_bars: str = "true",
    expected_enabled_exits: set[str] | None = None,
    expected_blocks_version: str | None = "142.2336",
    expect_no_signal_or_stoplimit_blocks: bool = True,
) -> None:
    _assert_retest_passive_generation_contract(
        tick_real,
        expected_improve_databank="retest 1",
        expected_exit_after_bars=expected_exit_after_bars,
        expected_enabled_exits=expected_enabled_exits,
        expected_blocks_version=expected_blocks_version,
        expect_no_signal_or_stoplimit_blocks=expect_no_signal_or_stoplimit_blocks,
    )


def _assert_mc2_passive_generation_contract(mc2: ET.Element) -> None:
    _assert_retest_passive_generation_contract(mc2, expected_improve_databank="MC")


def _assert_sequential_passive_generation_contract(sequential: ET.Element) -> None:
    _assert_retest_passive_generation_contract(sequential, expected_improve_databank="MC2")


def _assert_monkey_passive_generation_contract(monkey: ET.Element) -> None:
    _assert_retest_passive_generation_contract(monkey, expected_improve_databank="Sequential")


def _assert_synthetic_passive_generation_contract(synthetic: ET.Element) -> None:
    _assert_retest_passive_generation_contract(synthetic, expected_improve_databank="Monkey Test")


def _assert_synthetic_static_tabs_contract(synthetic: ET.Element) -> None:
    _assert_monkey_static_tabs_contract(synthetic)


def _assert_monkey_static_tabs_contract(monkey: ET.Element) -> None:
    _assert_mc2_static_tabs_contract(monkey)
    setup = monkey.find("./CustomData/Setups/Setup")
    assert setup is not None
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == C1_FASTEST_ROBUSTNESS_TEST_PRECISION
    assert setup.get("session") == "No Session"
    main_values = setup.find("MainTestValues")
    assert main_values is not None
    assert main_values.get("subcharts") == "false"
    assert main_values.get("symbol") == "true"


def _assert_sequential_static_tabs_contract(sequential: ET.Element) -> None:
    _assert_mc2_static_tabs_contract(sequential)
    setup = sequential.find("./CustomData/Setups/Setup")
    assert setup is not None
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == C1_FASTEST_ROBUSTNESS_TEST_PRECISION
    assert setup.get("session") == "No Session"
    main_values = setup.find("MainTestValues")
    assert main_values is not None
    assert main_values.get("subcharts") == "false"
    assert main_values.get("symbol") == "true"


def _assert_monkey_data_databanks_resources_options_contract(
    monkey: ET.Element,
    expected_symbol: str | None = None,
    expected_timeframe: str | None = None,
    expected_spread: str | None = None,
) -> None:
    databanks = {
        databank.get("name"): databank.get("value")
        for databank in monkey.findall(".//Databanks/Databank")
    }
    assert databanks == {"Output": "Monkey Test", "Input": "Sequential"}
    assert monkey.findall(".//Data/OutOfSample/Range") == []

    data_setup = monkey.find("./Data/Setups/Setup")
    custom_setup = monkey.find("./CustomData/Setups/Setup")
    assert data_setup is not None
    assert custom_setup is not None
    assert data_setup.get("dateFrom") == custom_setup.get("dateFrom") == "2017.10.02"
    assert data_setup.get("dateTo") == custom_setup.get("dateTo") == "2023.12.31"
    assert data_setup.get("testPrecision") == custom_setup.get("testPrecision") == C1_FASTEST_ROBUSTNESS_TEST_PRECISION
    assert data_setup.get("session") == custom_setup.get("session") == "No Session"
    data_chart = data_setup.find("Chart")
    custom_chart = custom_setup.find("Chart")
    assert data_chart is not None
    assert custom_chart is not None
    assert data_chart.attrib == custom_chart.attrib
    if expected_spread is not None:
        assert data_chart.get("spread") == expected_spread
    if expected_symbol is not None:
        assert data_chart.get("symbol") == expected_symbol
    if expected_timeframe is not None:
        assert data_chart.get("timeframe") == expected_timeframe

    main_values = custom_setup.find("MainTestValues")
    assert main_values is not None
    assert main_values.get("subcharts") == "false"
    assert main_values.get("symbol") == "true"

    params = {
        node.get("key"): node.text
        for node in monkey.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"LimitTimeRange", "RealisticGapsHandling", "StoreChartData", "Session", "MarketOpenSession"}
    }
    assert params == {
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
        "Session": "No Session",
        "MarketOpenSession": "No Session",
    }

    resources = monkey.find(".//Resources")
    assert resources is not None
    resource_symbols = {
        symbol.get("name")
        for symbol in resources.findall("./Symbols/Symbol")
        if symbol.get("name")
    }
    assert resource_symbols == {custom_chart.get("symbol")}
    assert resources.findall("./Sessions/Session") == []
    for symbol in resources.findall("./Symbols/Symbol"):
        assert symbol.get("precision") == "TICK"
        assert symbol.get("timezone") == "EETUS"


def _assert_synthetic_data_databanks_resources_options_contract(
    synthetic: ET.Element,
    expected_symbol: str | None = None,
    expected_timeframe: str | None = None,
    expected_spread: str | None = None,
    expected_output_databank: str = "Synthetic",
) -> None:
    databanks = {
        databank.get("name"): databank.get("value")
        for databank in synthetic.findall(".//Databanks/Databank")
    }
    assert databanks == {"Output": expected_output_databank, "Input": "Monkey Test"}
    assert synthetic.findall(".//Data/OutOfSample/Range") == []

    data_setup = synthetic.find("./Data/Setups/Setup")
    custom_setup = synthetic.find("./CustomData/Setups/Setup")
    assert data_setup is not None
    assert custom_setup is not None
    assert data_setup.get("dateFrom") == custom_setup.get("dateFrom") == "2017.10.02"
    assert data_setup.get("dateTo") == custom_setup.get("dateTo") == "2023.12.31"
    assert data_setup.get("testPrecision") == custom_setup.get("testPrecision") == C1_FASTEST_ROBUSTNESS_TEST_PRECISION
    assert data_setup.get("session") == custom_setup.get("session") == "No Session"
    data_chart = data_setup.find("Chart")
    custom_chart = custom_setup.find("Chart")
    assert data_chart is not None
    assert custom_chart is not None
    assert data_chart.attrib == custom_chart.attrib
    if expected_spread is not None:
        assert data_chart.get("spread") == expected_spread
    if expected_symbol is not None:
        assert data_chart.get("symbol") == expected_symbol
    if expected_timeframe is not None:
        assert data_chart.get("timeframe") == expected_timeframe

    main_values = custom_setup.find("MainTestValues")
    assert main_values is not None
    assert main_values.get("subcharts") == "false"
    assert main_values.get("symbol") == "true"

    params = {
        node.get("key"): node.text
        for node in synthetic.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"LimitTimeRange", "RealisticGapsHandling", "StoreChartData", "Session", "MarketOpenSession"}
    }
    assert params == {
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
        "Session": "No Session",
        "MarketOpenSession": "No Session",
    }

    resources = synthetic.find(".//Resources")
    assert resources is not None
    resource_symbols = {
        symbol.get("name")
        for symbol in resources.findall("./Symbols/Symbol")
        if symbol.get("name")
    }
    assert resource_symbols == {custom_chart.get("symbol")}
    assert resources.findall("./Sessions/Session") == []
    for symbol in resources.findall("./Symbols/Symbol"):
        assert symbol.get("precision") == "TICK"
        assert symbol.get("timezone") == "EETUS"


def _assert_monkey_crosschecks_contract(monkey: ET.Element) -> None:
    crosschecks = monkey.find(".//CrossChecks")
    assert crosschecks is not None
    assert crosschecks.get("use") == "true"
    assert crosschecks.get("evaluateAll") == "true"
    active = [
        check.tag
        for check in list(crosschecks)
        if isinstance(check.tag, str) and check.get("use") == "true"
    ]
    assert active == ["MonteCarloRetest"]
    monte_carlo = crosschecks.find("MonteCarloRetest")
    assert monte_carlo is not None
    assert monte_carlo.findtext("./Settings/NumberOfSimulations") == "200"
    assert monte_carlo.findtext("./Settings/MCUseFullSample") == "true"
    assert monte_carlo.findtext("./Settings/MCBacktestPrecision") == "-1"
    methods = {
        method.get("type"): method.get("use")
        for method in monte_carlo.findall("./Settings/Methods/Method")
        if method.get("type")
    }
    assert methods["RealMonkeyTest"] == "true"
    assert all(use == "false" for name, use in methods.items() if name != "RealMonkeyTest")
    real_monkey = monte_carlo.find("./Settings/Methods/Method[@type='RealMonkeyTest']")
    assert real_monkey is not None
    assert real_monkey.find("./Params/Param[@key='MaxChange']").text == "90"

    conditions = monte_carlo.findall("./AcceptanceSettings/Conditions/Condition")
    assert len(conditions) == 2
    assert [condition.get("use") for condition in conditions] == ["true", "true"]
    assert conditions[0].find("./Left-Side/Column-Value").get("column") == "NetProfit"
    assert conditions[0].find("./Comparator").get("value") == ">="
    assert conditions[0].find("./Right-Side/Column-Value").get("pctRatio") == "50"
    assert conditions[1].find("./Left-Side/Column-Value").get("column") == "DrawdownPct"
    assert conditions[1].find("./Comparator").get("value") == "<="
    assert conditions[1].find("./Right-Side/Column-Value").get("pctRatio") == "200"

    inactive_active_methods = [
        (check.tag, method.get("type"))
        for check in list(crosschecks)
        if isinstance(check.tag, str) and check.tag != "MonteCarloRetest"
        for method in check.findall("./Settings/Methods/Method")
        if method.get("use") == "true"
    ]
    assert inactive_active_methods == []


def _assert_synthetic_crosschecks_contract(synthetic: ET.Element) -> None:
    crosschecks = synthetic.find(".//CrossChecks")
    assert crosschecks is not None
    assert crosschecks.get("use") == "true"
    assert crosschecks.get("evaluateAll") == "true"
    active = [
        check.tag
        for check in list(crosschecks)
        if isinstance(check.tag, str) and check.get("use") == "true"
    ]
    assert active == ["MonteCarloRetest"]
    monte_carlo = crosschecks.find("MonteCarloRetest")
    assert monte_carlo is not None
    assert monte_carlo.findtext("./Settings/NumberOfSimulations") == "100"
    assert monte_carlo.findtext("./Settings/MCUseFullSample") == "true"
    assert monte_carlo.findtext("./Settings/MCBacktestPrecision") == "-1"
    methods = {
        method.get("type"): method.get("use")
        for method in monte_carlo.findall("./Settings/Methods/Method")
        if method.get("type")
    }
    assert methods["SyntheticBootstrapV3"] == "true"
    assert all(use == "false" for name, use in methods.items() if name != "SyntheticBootstrapV3")
    bootstrap = monte_carlo.find("./Settings/Methods/Method[@type='SyntheticBootstrapV3']")
    assert bootstrap is not None
    params = {
        param.get("key"): param.text
        for param in bootstrap.findall("./Params/Param")
    }
    assert params["BlockSize"] == "20"
    assert params["WarmupBars"] == "200"
    assert params["PreservePct"] == "85"

    conditions = monte_carlo.findall("./AcceptanceSettings/Conditions/Condition")
    assert len(conditions) == 1
    assert conditions[0].get("use") == "true"
    assert conditions[0].find("./Left-Side/Column-Value").get("column") == "NetProfit"
    assert conditions[0].find("./Left-Side/Column-Value").get("confidenceLevel") == "85"
    assert conditions[0].find("./Comparator").get("value") == "<="
    assert conditions[0].find("./Right-Side/Column-Value").get("resultType") == "main"
    assert conditions[0].find("./Right-Side/Column-Value").get("pctRatio") == "0"

    inactive_active_methods = [
        (check.tag, method.get("type"))
        for check in list(crosschecks)
        if isinstance(check.tag, str) and check.tag != "MonteCarloRetest"
        for method in check.findall("./Settings/Methods/Method")
        if method.get("use") == "true"
    ]
    assert inactive_active_methods == []


def _assert_spp_crosschecks_contract(spp: ET.Element) -> None:
    crosschecks = spp.find(".//CrossChecks")
    assert crosschecks is not None
    assert crosschecks.get("use") == "true"
    assert crosschecks.get("evaluateAll") == "true"
    active = [
        check.tag
        for check in list(crosschecks)
        if isinstance(check.tag, str) and check.get("use") == "true"
    ]
    assert active == ["OptProfileSysParamPermutation"]

    opt_profile = crosschecks.find("OptProfileSysParamPermutation")
    assert opt_profile is not None
    assert opt_profile.findtext("./Settings/MaxTests") == "3000"
    assert opt_profile.findtext("./Settings/DistributionUp") == "20"
    assert opt_profile.findtext("./Settings/DistributionDown") == "20"
    assert opt_profile.findtext("./Settings/Steps") == "25"
    what = opt_profile.find("./Settings/WhatToParametrize")
    assert what is not None
    assert what.get("type") == "1"
    assert what.get("symmetricVariables") == "false"
    flags = {child.tag: child.text for child in list(what) if isinstance(child.tag, str)}
    assert flags == {
        "Recommended": "false",
        "Periods": "true",
        "Shifts": "false",
        "Constants": "true",
        "OtherParams": "false",
        "EntryParams": "true",
        "EntryLogic": "false",
        "ExitParamsUsed": "true",
        "ExitParamsUnused": "false",
        "BooleanParams": "false",
    }

    acceptance = {
        child.tag: child.text
        for child in opt_profile.findall("./AcceptanceSettings/*")
        if isinstance(child.tag, str) and child.tag != "Conditions"
    }
    assert acceptance == {
        "ProfitOptPct": "30",
        "AvgProfit": "0",
        "UniformDistrChanges": "15",
        "StdevAvgProfit": "1",
        "EvalProfitOptCheck": "true",
        "EvalAvgProfitCheck": "true",
        "EvalUniformDistrCheck": "true",
        "EvalTopProfitCheck": "false",
    }

    conditions = opt_profile.findall("./AcceptanceSettings/Conditions/Condition")
    assert len(conditions) == 2
    assert conditions[0].get("use") == "true"
    assert conditions[0].find("./Left-Side/Column-Value").get("column") == "NetProfit"
    assert conditions[0].find("./Left-Side/Column-Value").get("resultType") == "OptProfileSysParamPermutation"
    assert conditions[0].find("./Comparator").get("value") == ">="
    assert conditions[0].find("./Right-Side/Column-Value").get("resultType") == "main"
    assert conditions[0].find("./Right-Side/Column-Value").get("pctRatio") == "50"
    assert conditions[1].get("use") == "true"
    assert conditions[1].find("./Left-Side/Column-Value").get("column") == "DrawdownPct"
    assert conditions[1].find("./Comparator").get("value") == "<="
    assert conditions[1].find("./Right-Side/Column-Value").get("pctRatio") == "200"

    active_methods = [
        (check.tag, method.get("type"))
        for check in list(crosschecks)
        if isinstance(check.tag, str)
        for method in check.findall("./Settings/Methods/Method")
        if method.get("use") == "true"
    ]
    assert active_methods == []


def _assert_spp_static_tabs_contract(spp: ET.Element) -> None:
    _assert_mc2_static_tabs_contract(spp)
    rankings = spp.find(".//Rankings")
    assert rankings is not None
    assert rankings.get("type") == "never"
    assert rankings.findtext("DeleteFailedStrategies") == "true"
    assert rankings.findtext("ForceRunCrossChecks") == "false"
    assert rankings.findall("./Conditions/Condition") == []
    assert rankings.find("FitPortfolio").get("active") == "false"
    assert rankings.find("CustomAnalysis").get("filter") == "false"
    custom = spp.find("./CustomData")
    assert custom is not None
    assert "USDJPY" not in ET.tostring(custom, encoding="unicode")


def _assert_static_crosschecks_contract(task: ET.Element, require_selected_strategies: bool = True) -> None:
    crosschecks = task.find(".//CrossChecks")
    assert crosschecks is not None
    assert crosschecks.get("use") == "false"
    assert crosschecks.get("evaluateAll") == "false"
    for check in list(crosschecks):
        if not isinstance(check.tag, str) or check.get("use") is None:
            continue
        assert check.get("use") == "false"
        for method in check.findall("./Settings/Methods/Method"):
            assert method.get("use") == "false"

    rmm_methods = {
        method.get("type"): method.get("use")
        for method in task.findall(".//RiskMoneyManagement//MoneyManagement/Method")
        if method.get("type")
    }
    assert rmm_methods == {
        "FixedSize": "true",
        "RiskFixedBalancePct": "false",
        "RiskFixedPctOfAccount": "false",
        "FixedAmount": "false",
        "StocksSizeByPrice": "false",
    }
    atms = task.find(".//ATMs")
    assert atms is not None
    assert atms.get("enable") == "false"
    selected = task.find(".//SelectedStrategies")
    if require_selected_strategies:
        assert selected is not None
        assert list(selected) == []
        assert (selected.text or "").strip() == ""


def _assert_retest1_static_crosschecks_contract(retest1: ET.Element) -> None:
    _assert_static_crosschecks_contract(retest1, require_selected_strategies=True)


def _assert_tick_real_static_crosschecks_contract(tick_real: ET.Element) -> None:
    _assert_static_crosschecks_contract(tick_real, require_selected_strategies=False)
    custom = tick_real.find("./CustomData")
    assert custom is not None
    custom_text = ET.tostring(custom, encoding="unicode")
    assert "USDJPY" not in custom_text
    setup = custom.find(".//Setup")
    if setup is not None:
        assert setup.get("dateFrom") == "2017.10.02"
        assert setup.get("dateTo") == "2023.12.31"
        assert setup.get("testPrecision") == C1_TICK_TEST_PRECISION
        assert setup.get("session") == "No Session"
    assert {
        setup.get("testPrecision")
        for setup in tick_real.findall(".//CrossChecks/*/Settings/Setups/Setup")
    } <= {C1_TICK_TEST_PRECISION}


def _assert_capa2_mc_contract(mc: ET.Element, expected_symbol: str, expected_timeframe: str, expected_source: str, expected_broker: str) -> None:
    data_setup = mc.find("./Data/Setups/Setup")
    custom_setup = mc.find("./CustomData/Setups/Setup")
    assert data_setup is not None
    assert custom_setup is not None
    for setup in (data_setup, custom_setup):
        assert setup.get("dateFrom") == "2017.10.02"
        assert setup.get("dateTo") == "2023.12.31"
        assert setup.get("testPrecision") == "1"
        assert setup.get("session") == "No Session"
        chart = setup.find("Chart")
        assert chart is not None
        assert chart.get("symbol") == expected_symbol
        assert chart.get("timeframe") == expected_timeframe
    assert mc.findall("./Data/OutOfSample/Range") == []
    assert {
        databank.get("name"): databank.get("value")
        for databank in mc.findall(".//Databanks/Databank")
    } == {"Output": "MC", "Input": "TICK"}
    symbols = mc.findall(".//Resources/Symbols/Symbol")
    assert {node.get("name") for node in symbols} == {expected_symbol}
    assert {node.get("source") for node in symbols} == {expected_source}
    assert {node.get("broker") for node in symbols} == {expected_broker}
    assert mc.findall(".//Resources/Sessions/Session") == []

    params = {
        node.get("key"): node.text
        for node in mc.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"Session", "MarketOpenSession", "LimitTimeRange", "RealisticGapsHandling", "StoreChartData"}
    }
    assert params == {
        "Session": "No Session",
        "MarketOpenSession": "No Session",
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
    }

    crosschecks = mc.find(".//CrossChecks")
    assert crosschecks is not None
    assert crosschecks.attrib == {"use": "true", "evaluateAll": "true"}
    active = [
        child.tag
        for child in list(crosschecks)
        if isinstance(child.tag, str) and child.get("use") == "true"
    ]
    assert active == ["MonteCarloManipulation"]
    manipulation = crosschecks.find("MonteCarloManipulation")
    assert manipulation is not None
    assert manipulation.findtext("./Settings/NumberOfSimulations") == "200"
    assert manipulation.findtext("./Settings/MCUseFullSample") == "true"
    methods = {
        method.get("type"): method
        for method in manipulation.findall("./Settings/Methods/Method")
        if method.get("type")
    }
    assert methods["RandomizeTradesOrder"].get("use") == "true"
    assert methods["RandomizeTradesOrder"].find("./Params/Param[@key='Method']").text == "resampling"
    assert methods["RandomlySkipTrades"].get("use") == "false"
    for setup in crosschecks.findall(".//Settings/Setups/Setup"):
        assert setup.get("dateFrom") == "2017.10.02"
        assert setup.get("dateTo") == "2023.12.31"
        assert setup.get("testPrecision") == "1"
        assert setup.get("session") == "No Session"
    assert not [
        method
        for check in list(crosschecks)
        if isinstance(check.tag, str) and check.tag != "MonteCarloManipulation"
        for method in check.findall("./Settings/Methods/Method")
        if method.get("use") == "true"
    ]

    rankings = mc.find(".//Rankings")
    assert rankings is not None
    assert rankings.get("type") == "never"
    assert rankings.findtext("DeleteFailedStrategies") == "true"
    assert rankings.findtext("ForceRunCrossChecks") == "false"
    assert rankings.find("FitPortfolio").get("active") == "false"
    assert rankings.find("CustomAnalysis").get("filter") == "false"
    assert rankings.findall("./Conditions/Condition") == []
    assert mc.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "TICK"
    exit_types = {block.get("key"): block.get("use") for block in mc.findall(".//Blocks/ExitTypes/Block")}
    assert exit_types["ExitAfterBars.ExitAfterBars"] == "false"
    assert exit_types["StopLoss.StopLoss"] == "true"
    assert exit_types["ProfitTarget.ProfitTarget"] == "true"
    assert exit_types["TrailingStop.TrailingStop"] == "true"


def _assert_capa2_mc2_contract(
    mc2: ET.Element,
    expected_symbol: str,
    expected_timeframe: str,
    expected_source: str,
    expected_broker: str,
    expected_spread: str,
    expected_spread_min: str,
    expected_spread_max: str,
) -> None:
    assert mc2.find("./Data") is None
    setup = mc2.find("./CustomData/Setups/Setup")
    assert setup is not None
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == "1"
    assert setup.get("session") == "No Session"
    chart = setup.find("Chart")
    assert chart is not None
    assert chart.get("symbol") == expected_symbol
    assert chart.get("timeframe") == expected_timeframe
    assert chart.get("spread") == expected_spread
    assert {
        databank.get("name"): databank.get("value")
        for databank in mc2.findall(".//Databanks/Databank")
    } == {"Output": "MC2", "Input": "MC"}
    symbols = mc2.findall(".//Resources/Symbols/Symbol")
    assert {node.get("name") for node in symbols} == {expected_symbol}
    assert {node.get("source") for node in symbols} == {expected_source}
    assert {node.get("broker") for node in symbols} == {expected_broker}
    assert mc2.findall(".//Resources/Sessions/Session") == []

    params = {
        node.get("key"): node.text
        for node in mc2.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"Session", "MarketOpenSession", "LimitTimeRange", "RealisticGapsHandling", "StoreChartData"}
    }
    assert params == {
        "Session": "No Session",
        "MarketOpenSession": "No Session",
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
    }

    crosschecks = mc2.find(".//CrossChecks")
    assert crosschecks is not None
    assert crosschecks.attrib == {"use": "true", "evaluateAll": "true"}
    active = [
        child.tag
        for child in list(crosschecks)
        if isinstance(child.tag, str) and child.get("use") == "true"
    ]
    assert active == ["MonteCarloRetest"]
    monte_carlo = crosschecks.find("MonteCarloRetest")
    assert monte_carlo is not None
    assert monte_carlo.findtext("./Settings/NumberOfSimulations") == "100"
    assert monte_carlo.findtext("./Settings/MCUseFullSample") == "true"
    methods = {
        method.get("type"): method
        for method in monte_carlo.findall("./Settings/Methods/Method")
        if method.get("type")
    }
    assert methods["RandomizeHistoryData"].get("use") == "true"
    assert methods["RandomizeSpread"].get("use") == "true"
    assert methods["RandomizeSpread"].find("./Params/Param[@key='Min']").text == expected_spread_min
    assert methods["RandomizeSpread"].find("./Params/Param[@key='Max']").text == expected_spread_max
    assert all(use.get("use") == "false" for name, use in methods.items() if name not in {"RandomizeHistoryData", "RandomizeSpread"})
    for nested_setup in crosschecks.findall(".//Settings/Setups/Setup"):
        assert nested_setup.get("dateFrom") == "2017.10.02"
        assert nested_setup.get("dateTo") == "2023.12.31"
        assert nested_setup.get("testPrecision") == "1"
        assert nested_setup.get("session") == "No Session"

    rankings = mc2.find(".//Rankings")
    assert rankings is not None
    assert rankings.get("type") == "never"
    assert rankings.findtext("DeleteFailedStrategies") == "true"
    assert rankings.findtext("ForceRunCrossChecks") == "false"
    assert rankings.find("FitPortfolio").get("active") == "false"
    assert rankings.find("CustomAnalysis").get("filter") == "false"
    assert rankings.findall("./Conditions/Condition") == []
    assert mc2.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "MC"
    exit_types = {block.get("key"): block.get("use") for block in mc2.findall(".//Blocks/ExitTypes/Block")}
    assert exit_types["ExitAfterBars.ExitAfterBars"] == "false"
    assert exit_types["StopLoss.StopLoss"] == "true"
    assert exit_types["ProfitTarget.ProfitTarget"] == "true"
    assert exit_types["TrailingStop.TrailingStop"] == "true"


def _assert_capa2_sequential_contract(
    sequential: ET.Element,
    expected_symbol: str,
    expected_timeframe: str,
    expected_source: str,
    expected_broker: str,
    expected_spread: str,
) -> None:
    for section in ("Data", "CustomData"):
        setup = sequential.find(f"./{section}/Setups/Setup")
        assert setup is not None
        assert setup.get("dateFrom") == "2017.10.02"
        assert setup.get("dateTo") == "2023.12.31"
        assert setup.get("testPrecision") == "1"
        assert setup.get("session") == "No Session"
        chart = setup.find("Chart")
        assert chart is not None
        assert chart.get("symbol") == expected_symbol
        assert chart.get("timeframe") == expected_timeframe
        assert chart.get("spread") == expected_spread
    assert sequential.findall("./Data/OutOfSample/Range") == []
    assert {
        databank.get("name"): databank.get("value")
        for databank in sequential.findall(".//Databanks/Databank")
    } == {"Output": "Sequential", "Input": "MC2"}
    symbols = sequential.findall(".//Resources/Symbols/Symbol")
    assert {node.get("name") for node in symbols} == {expected_symbol}
    assert {node.get("source") for node in symbols} == {expected_source}
    assert {node.get("broker") for node in symbols} == {expected_broker}
    assert sequential.findall(".//Resources/Sessions/Session") == []

    params = {
        node.get("key"): node.text
        for node in sequential.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"Session", "MarketOpenSession", "LimitTimeRange", "RealisticGapsHandling", "StoreChartData"}
    }
    assert params == {
        "Session": "No Session",
        "MarketOpenSession": "No Session",
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
    }

    crosschecks = sequential.find(".//CrossChecks")
    assert crosschecks is not None
    assert crosschecks.attrib == {"use": "true", "evaluateAll": "true"}
    active = [
        child.tag
        for child in list(crosschecks)
        if isinstance(child.tag, str) and child.get("use") == "true"
    ]
    assert active == ["SequentialOptimization"]
    sequential_optimization = crosschecks.find("SequentialOptimization")
    assert sequential_optimization is not None
    assert sequential_optimization.findtext("./Settings/ParameterSettings/DistributionUp") == "130"
    assert sequential_optimization.findtext("./Settings/ParameterSettings/DistributionDown") == "70"
    assert sequential_optimization.findtext("./Settings/ParameterSettings/Steps") == "12"
    assert sequential_optimization.findtext("./Settings/ParameterSettings/ApplyToStrategy") == "false"
    assert sequential_optimization.findtext("./AcceptanceSettings/PctToPass") == "80"
    assert sequential_optimization.findtext("./AcceptanceSettings/ResultsCount") == "5"
    assert sequential_optimization.findtext("./AcceptanceSettings/StabilityRange") == "25"
    assert sequential_optimization.findall("./AcceptanceSettings/Conditions/Condition") == []
    for nested_setup in crosschecks.findall(".//Settings/Setups/Setup"):
        assert nested_setup.get("dateFrom") == "2017.10.02"
        assert nested_setup.get("dateTo") == "2023.12.31"
        assert nested_setup.get("testPrecision") == "1"
        assert nested_setup.get("session") == "No Session"

    rankings = sequential.find(".//Rankings")
    assert rankings is not None
    assert rankings.get("type") == "never"
    assert rankings.findtext("DeleteFailedStrategies") == "true"
    assert rankings.findtext("ForceRunCrossChecks") == "false"
    assert rankings.find("FitPortfolio").get("active") == "false"
    assert rankings.find("CustomAnalysis").get("filter") == "false"
    assert rankings.findall("./Conditions/Condition") == []
    assert sequential.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "MC2"
    exit_types = {block.get("key"): block.get("use") for block in sequential.findall(".//Blocks/ExitTypes/Block")}
    assert exit_types["ExitAfterBars.ExitAfterBars"] == "false"
    assert exit_types["StopLoss.StopLoss"] == "true"
    assert exit_types["ProfitTarget.ProfitTarget"] == "true"
    assert exit_types["TrailingStop.TrailingStop"] == "true"


def _assert_capa2_monkey_contract(
    monkey: ET.Element,
    expected_symbol: str,
    expected_timeframe: str,
    expected_source: str,
    expected_broker: str,
    expected_spread: str,
) -> None:
    for section in ("Data", "CustomData"):
        setup = monkey.find(f"./{section}/Setups/Setup")
        assert setup is not None
        assert setup.get("dateFrom") == "2017.10.02"
        assert setup.get("dateTo") == "2023.12.31"
        assert setup.get("testPrecision") == "1"
        assert setup.get("session") == "No Session"
        chart = setup.find("Chart")
        assert chart is not None
        assert chart.get("symbol") == expected_symbol
        assert chart.get("timeframe") == expected_timeframe
        assert chart.get("spread") == expected_spread
    assert monkey.findall("./Data/OutOfSample/Range") == []
    assert {
        databank.get("name"): databank.get("value")
        for databank in monkey.findall(".//Databanks/Databank")
    } == {"Output": "Monkey Test", "Input": "Sequential"}
    symbols = monkey.findall(".//Resources/Symbols/Symbol")
    assert {node.get("name") for node in symbols} == {expected_symbol}
    assert {node.get("source") for node in symbols} == {expected_source}
    assert {node.get("broker") for node in symbols} == {expected_broker}
    assert monkey.findall(".//Resources/Sessions/Session") == []

    params = {
        node.get("key"): node.text
        for node in monkey.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"Session", "MarketOpenSession", "LimitTimeRange", "RealisticGapsHandling", "StoreChartData"}
    }
    assert params == {
        "Session": "No Session",
        "MarketOpenSession": "No Session",
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
    }

    crosschecks = monkey.find(".//CrossChecks")
    assert crosschecks is not None
    assert crosschecks.attrib == {"use": "true", "evaluateAll": "true"}
    active = [
        child.tag
        for child in list(crosschecks)
        if isinstance(child.tag, str) and child.get("use") == "true"
    ]
    assert active == ["MonteCarloRetest"]
    monte_carlo = crosschecks.find("MonteCarloRetest")
    assert monte_carlo is not None
    assert monte_carlo.findtext("./Settings/NumberOfSimulations") == "200"
    assert monte_carlo.findtext("./Settings/MCUseFullSample") == "true"
    assert monte_carlo.findtext("./Settings/MCBacktestPrecision") == "-1"
    methods = {
        method.get("type"): method
        for method in monte_carlo.findall("./Settings/Methods/Method")
        if method.get("type")
    }
    assert methods["RealMonkeyTest"].get("use") == "true"
    assert methods["RealMonkeyTest"].find("./Params/Param[@key='MaxChange']").text == "90"
    assert all(use.get("use") == "false" for name, use in methods.items() if name != "RealMonkeyTest")
    assert len(monte_carlo.findall("./AcceptanceSettings/Conditions/Condition")) == 2
    for nested_setup in crosschecks.findall(".//Settings/Setups/Setup"):
        assert nested_setup.get("dateFrom") == "2017.10.02"
        assert nested_setup.get("dateTo") == "2023.12.31"
        assert nested_setup.get("testPrecision") == "1"
        assert nested_setup.get("session") == "No Session"

    rankings = monkey.find(".//Rankings")
    assert rankings is not None
    assert rankings.get("type") == "never"
    assert rankings.findtext("DeleteFailedStrategies") == "true"
    assert rankings.findtext("ForceRunCrossChecks") == "false"
    assert rankings.find("FitPortfolio").get("active") == "false"
    assert rankings.find("CustomAnalysis").get("filter") == "false"
    assert rankings.findall("./Conditions/Condition") == []
    assert monkey.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "Sequential"
    exit_types = {block.get("key"): block.get("use") for block in monkey.findall(".//Blocks/ExitTypes/Block")}
    assert exit_types["ExitAfterBars.ExitAfterBars"] == "false"
    assert exit_types["StopLoss.StopLoss"] == "true"
    assert exit_types["ProfitTarget.ProfitTarget"] == "true"
    assert exit_types["TrailingStop.TrailingStop"] == "true"


def _assert_capa2_synthetic_contract(
    synthetic: ET.Element,
    expected_symbol: str,
    expected_timeframe: str,
    expected_source: str,
    expected_broker: str,
    expected_spread: str,
) -> None:
    for section in ("Data", "CustomData"):
        setup = synthetic.find(f"./{section}/Setups/Setup")
        assert setup is not None
        assert setup.get("dateFrom") == "2017.10.02"
        assert setup.get("dateTo") == "2023.12.31"
        assert setup.get("testPrecision") == "1"
        assert setup.get("session") == "No Session"
        chart = setup.find("Chart")
        assert chart is not None
        assert chart.get("symbol") == expected_symbol
        assert chart.get("timeframe") == expected_timeframe
        assert chart.get("spread") == expected_spread
    assert synthetic.findall("./Data/OutOfSample/Range") == []
    assert {
        databank.get("name"): databank.get("value")
        for databank in synthetic.findall(".//Databanks/Databank")
    } == {"Output": "Synthetic", "Input": "Monkey Test"}
    symbols = synthetic.findall(".//Resources/Symbols/Symbol")
    assert {node.get("name") for node in symbols} == {expected_symbol}
    assert {node.get("source") for node in symbols} == {expected_source}
    assert {node.get("broker") for node in symbols} == {expected_broker}
    assert synthetic.findall(".//Resources/Sessions/Session") == []

    params = {
        node.get("key"): node.text
        for node in synthetic.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"Session", "MarketOpenSession", "LimitTimeRange", "RealisticGapsHandling", "StoreChartData"}
    }
    assert params == {
        "Session": "No Session",
        "MarketOpenSession": "No Session",
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
    }

    crosschecks = synthetic.find(".//CrossChecks")
    assert crosschecks is not None
    assert crosschecks.attrib == {"use": "true", "evaluateAll": "true"}
    active = [
        child.tag
        for child in list(crosschecks)
        if isinstance(child.tag, str) and child.get("use") == "true"
    ]
    assert active == ["MonteCarloRetest"]
    monte_carlo = crosschecks.find("MonteCarloRetest")
    assert monte_carlo is not None
    assert monte_carlo.findtext("./Settings/NumberOfSimulations") == "100"
    assert monte_carlo.findtext("./Settings/MCUseFullSample") == "true"
    assert monte_carlo.findtext("./Settings/MCBacktestPrecision") == "-1"
    methods = {
        method.get("type"): method
        for method in monte_carlo.findall("./Settings/Methods/Method")
        if method.get("type")
    }
    assert methods["SyntheticBootstrapV3"].get("use") == "true"
    assert all(use.get("use") == "false" for name, use in methods.items() if name != "SyntheticBootstrapV3")
    params = {
        param.get("key"): param.text
        for param in methods["SyntheticBootstrapV3"].findall("./Params/Param")
    }
    assert params == {"BlockSize": "20", "WarmupBars": "200", "PreservePct": "85"}
    conditions = monte_carlo.findall("./AcceptanceSettings/Conditions/Condition")
    assert len(conditions) == 1
    assert conditions[0].get("use") == "true"
    assert conditions[0].find("./Left-Side/Column-Value").get("column") == "NetProfit"
    assert conditions[0].find("./Left-Side/Column-Value").get("confidenceLevel") == "85"
    assert conditions[0].find("./Comparator").get("value") == "<="
    assert conditions[0].find("./Right-Side/Column-Value").get("pctRatio") == "0"
    for nested_setup in crosschecks.findall(".//Settings/Setups/Setup"):
        assert nested_setup.get("dateFrom") == "2017.10.02"
        assert nested_setup.get("dateTo") == "2023.12.31"
        assert nested_setup.get("testPrecision") == "1"
        assert nested_setup.get("session") == "No Session"

    rankings = synthetic.find(".//Rankings")
    assert rankings is not None
    assert rankings.get("type") == "never"
    assert rankings.findtext("DeleteFailedStrategies") == "true"
    assert rankings.findtext("ForceRunCrossChecks") == "false"
    assert rankings.find("FitPortfolio").get("active") == "false"
    assert rankings.find("CustomAnalysis").get("filter") == "false"
    assert rankings.findall("./Conditions/Condition") == []
    assert synthetic.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "Monkey Test"
    exit_types = {block.get("key"): block.get("use") for block in synthetic.findall(".//Blocks/ExitTypes/Block")}
    assert exit_types["ExitAfterBars.ExitAfterBars"] == "false"
    assert exit_types["StopLoss.StopLoss"] == "true"
    assert exit_types["ProfitTarget.ProfitTarget"] == "true"
    assert exit_types["TrailingStop.TrailingStop"] == "true"


def _assert_capa2_spp_contract(
    spp: ET.Element,
    expected_symbol: str,
    expected_timeframe: str,
    expected_source: str,
    expected_broker: str,
    expected_spread: str,
) -> None:
    databanks = {
        databank.get("name"): databank.get("value")
        for databank in spp.findall(".//Databanks/Databank")
    }
    assert databanks == {"Output": "SPP", "Input": "Synthetic"}
    assert spp.findall("./Data/OutOfSample/Range") == []

    for section in ("Data", "CustomData"):
        setup = spp.find(f"./{section}/Setups/Setup")
        assert setup is not None
        assert setup.get("dateFrom") == "2017.10.02"
        assert setup.get("dateTo") == "2023.12.31"
        assert setup.get("testPrecision") == C1_FASTEST_ROBUSTNESS_TEST_PRECISION
        assert setup.get("session") == "No Session"
        chart = setup.find("Chart")
        assert chart is not None
        assert chart.get("symbol") == expected_symbol
        assert chart.get("timeframe") == expected_timeframe
        assert chart.get("spread") == expected_spread

    resources = spp.find(".//Resources")
    assert resources is not None
    symbols = resources.findall("./Symbols/Symbol")
    assert {node.get("name") for node in symbols} == {expected_symbol}
    assert {node.get("source") for node in symbols} == {expected_source}
    assert {node.get("broker") for node in symbols} == {expected_broker}
    assert {node.get("precision") for node in symbols} == {"TICK"}
    assert {node.get("timezone") for node in symbols} == {"EETUS"}
    assert resources.findall("./Sessions/Session") == []
    assert "dukascopy" not in ET.tostring(resources, encoding="unicode").lower()

    params = {
        node.get("key"): node.text
        for node in spp.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"Session", "MarketOpenSession", "LimitTimeRange", "RealisticGapsHandling", "StoreChartData"}
    }
    assert params == {
        "Session": "No Session",
        "MarketOpenSession": "No Session",
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
    }

    _assert_spp_crosschecks_contract(spp)
    for nested_setup in spp.findall(".//CrossChecks/*/Settings/Setups/Setup"):
        assert nested_setup.get("dateFrom") == "2017.10.02"
        assert nested_setup.get("dateTo") == "2023.12.31"
        assert nested_setup.get("testPrecision") == C1_FASTEST_ROBUSTNESS_TEST_PRECISION
        assert nested_setup.get("session") == "No Session"

    _assert_mc2_static_tabs_contract(spp)
    assert spp.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "Synthetic"
    exit_types = {block.get("key"): block.get("use") for block in spp.findall(".//Blocks/ExitTypes/Block")}
    assert exit_types["ExitAfterBars.ExitAfterBars"] == "false"
    assert exit_types["StopLoss.StopLoss"] == "true"
    assert exit_types["ProfitTarget.ProfitTarget"] == "true"
    assert exit_types["TrailingStop.TrailingStop"] == "true"


def _assert_mc2_static_tabs_contract(mc2: ET.Element) -> None:
    rankings = mc2.find(".//Rankings")
    assert rankings is not None
    assert rankings.get("type") == "never"
    assert rankings.findtext("DeleteFailedStrategies") == "true"
    assert rankings.findtext("ForceRunCrossChecks") == "false"
    assert rankings.find("FitPortfolio").get("active") == "false"
    assert rankings.find("CustomAnalysis").get("filter") == "false"
    assert rankings.findall("./Conditions/Condition") == []

    rmm_methods = {
        method.get("type"): method.get("use")
        for method in mc2.findall(".//RiskMoneyManagement//MoneyManagement/Method")
        if method.get("type")
    }
    assert rmm_methods == {
        "FixedSize": "true",
        "RiskFixedBalancePct": "false",
        "RiskFixedPctOfAccount": "false",
        "FixedAmount": "false",
        "StocksSizeByPrice": "false",
    }
    atms = mc2.find(".//ATMs")
    assert atms is not None
    assert atms.get("enable") == "false"
    selected = mc2.find(".//SelectedStrategies")
    if selected is not None:
        assert list(selected) == []
        assert (selected.text or "").strip() == ""


def _randomize_spread_params(task: ET.Element) -> dict[str, str]:
    method = task.find(".//CrossChecks/MonteCarloRetest/Settings/Methods/Method[@type='RandomizeSpread']")
    assert method is not None
    return {
        param.get("key"): param.text
        for param in method.findall("./Params/Param")
        if param.get("key")
    }


def _assert_mc2_data_databanks_resources_options_contract(mc2: ET.Element, expected_symbol: str | None = None, expected_timeframe: str | None = None) -> None:
    assert mc2.find("./Data") is None
    setup = mc2.find("./CustomData/Setups/Setup")
    assert setup is not None
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == C1_FASTEST_ROBUSTNESS_TEST_PRECISION
    assert setup.get("session") == "No Session"
    assert setup.get("engine") == "MetaTrader4"
    chart = setup.find("Chart")
    assert chart is not None
    if expected_symbol is not None:
        assert chart.get("symbol") == expected_symbol
    if expected_timeframe is not None:
        assert chart.get("timeframe") == expected_timeframe
    assert dict(setup.find("MainTestValues").attrib) == {
        "engine": "true",
        "symbol": "true",
        "timeframe": "true",
        "dates": "true",
        "precision": "true",
        "distance": "true",
        "spread": "true",
        "slippage": "true",
        "commissions": "true",
    }
    assert setup.find("./Commissions/Method[@type='SizeBased']").get("use") == "true"
    assert setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']").text == "0.0"

    databanks = {
        databank.get("name"): databank.get("value")
        for databank in mc2.findall(".//Databanks/Databank")
    }
    assert databanks["Input"] == "MC"
    assert databanks["Output"] == "MC2"

    resources = mc2.find(".//Resources")
    assert resources is not None
    resource_symbols = {
        symbol.get("name")
        for symbol in resources.findall("./Symbols/Symbol")
        if symbol.get("name")
    }
    assert resource_symbols == {chart.get("symbol")}
    assert resources.findall("./Sessions/Session") == []
    assert "USDJPY" not in ET.tostring(resources, encoding="unicode")
    broker_ids = {
        broker.get("id")
        for broker in resources.findall("./Brokers/Broker")
        if broker.get("id")
    }
    for symbol in resources.findall("./Symbols/Symbol"):
        assert symbol.get("precision") == "TICK"
        assert symbol.get("timezone") == "EETUS"
        if broker_ids:
            assert symbol.get("broker") in broker_ids or symbol.get("broker") == "-1"
        else:
            assert symbol.get("broker") in {"-1", None, ""}
        info = symbol.find("InstrumentInfo")
        assert info is not None
        if broker_ids:
            assert info.get("broker") in broker_ids or info.get("broker") == "-1"
        else:
            assert info.get("broker") in {"-1", None, ""}

    params = {
        node.get("key"): node.text
        for node in mc2.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"Session", "MarketOpenSession", "LimitTimeRange", "RealisticGapsHandling", "StoreChartData"}
    }
    assert params == {
        "Session": "No Session",
        "MarketOpenSession": "No Session",
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
    }


def _assert_spp_data_databanks_resources_options_contract(
    spp: ET.Element,
    expected_symbol: str | None = None,
    expected_timeframe: str | None = None,
    expected_spread: str | None = None,
    expected_input_databank: str = "Synthetic",
) -> None:
    assert spp.find("./Data") is None
    setup = spp.find("./CustomData/Setups/Setup")
    assert setup is not None
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == C1_FASTEST_ROBUSTNESS_TEST_PRECISION
    assert setup.get("session") == "No Session"
    assert setup.get("engine") == "MetaTrader4"
    chart = setup.find("Chart")
    assert chart is not None
    if expected_symbol is not None:
        assert chart.get("symbol") == expected_symbol
    if expected_timeframe is not None:
        assert chart.get("timeframe") == expected_timeframe
    if expected_spread is not None:
        assert chart.get("spread") == expected_spread
    assert dict(setup.find("MainTestValues").attrib) == {
        "engine": "true",
        "symbol": "true",
        "timeframe": "true",
        "dates": "true",
        "precision": "true",
        "distance": "true",
        "spread": "true",
        "slippage": "true",
        "commissions": "true",
    }
    assert setup.find("./Commissions/Method[@type='SizeBased']").get("use") == "true"
    assert setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']").text == "0.0"

    databanks = {
        databank.get("name"): databank.get("value")
        for databank in spp.findall(".//Databanks/Databank")
    }
    assert databanks == {"Output": "SPP", "Input": expected_input_databank}

    resources = spp.find(".//Resources")
    assert resources is not None
    resource_symbols = {
        symbol.get("name")
        for symbol in resources.findall("./Symbols/Symbol")
        if symbol.get("name")
    }
    assert resource_symbols == {chart.get("symbol")}
    assert resources.findall("./Sessions/Session") == []
    assert "USDJPY" not in ET.tostring(resources, encoding="unicode")
    for symbol in resources.findall("./Symbols/Symbol"):
        assert symbol.get("precision") == "TICK"
        assert symbol.get("timezone") == "EETUS"

    params = {
        node.get("key"): node.text
        for node in spp.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"Session", "MarketOpenSession", "LimitTimeRange", "RealisticGapsHandling", "StoreChartData"}
    }
    assert params == {
        "Session": "No Session",
        "MarketOpenSession": "No Session",
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
    }


def _assert_wfm_data_databanks_resources_options_contract(
    wfm: ET.Element,
    expected_symbol: str | None = None,
    expected_timeframe: str | None = None,
    expected_spread: str | None = None,
    expected_source: str | None = None,
    expected_broker: str | None = None,
) -> None:
    databanks = {
        databank.get("name"): databank.get("value")
        for databank in wfm.findall(".//Databanks/Databank")
    }
    assert databanks == {"Output": "WFM", "Input": "SPP"}
    assert wfm.findall(".//Data/OutOfSample/Range") == []

    data_setup = wfm.find("./Data/Setups/Setup")
    custom_setup = wfm.find("./CustomData/Setups/Setup")
    assert data_setup is not None
    assert custom_setup is not None
    assert data_setup.get("dateFrom") == custom_setup.get("dateFrom") == "2017.10.02"
    assert data_setup.get("dateTo") == custom_setup.get("dateTo") == "2023.12.31"
    assert data_setup.get("testPrecision") == custom_setup.get("testPrecision") == C1_FASTEST_ROBUSTNESS_TEST_PRECISION
    assert data_setup.get("session") == custom_setup.get("session") == "No Session"
    assert data_setup.get("engine") == "MetaTrader5 (hedged)"
    assert custom_setup.get("engine") == "MetaTrader4"
    data_chart = data_setup.find("Chart")
    custom_chart = custom_setup.find("Chart")
    assert data_chart is not None
    assert custom_chart is not None
    assert data_chart.attrib == custom_chart.attrib
    if expected_spread is not None:
        assert data_chart.get("spread") == expected_spread
    if expected_symbol is not None:
        assert data_chart.get("symbol") == expected_symbol
    if expected_timeframe is not None:
        assert data_chart.get("timeframe") == expected_timeframe

    assert dict(custom_setup.find("MainTestValues").attrib) == {
        "engine": "true",
        "symbol": "true",
        "timeframe": "true",
        "dates": "true",
        "subcharts": "false",
        "precision": "true",
        "distance": "true",
        "spread": "true",
        "slippage": "true",
        "commissions": "true",
    }
    for setup in (data_setup, custom_setup):
        assert setup.find("./Commissions/Method[@type='SizeBased']").get("use") == "true"
        assert setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']").text == "0.0"

    resources = wfm.find(".//Resources")
    assert resources is not None
    resource_symbols = {
        symbol.get("name")
        for symbol in resources.findall("./Symbols/Symbol")
        if symbol.get("name")
    }
    assert resource_symbols == {custom_chart.get("symbol")}
    assert resources.findall("./Sessions/Session") == []
    assert "USDJPY" not in ET.tostring(resources, encoding="unicode")
    for symbol in resources.findall("./Symbols/Symbol"):
        assert symbol.get("precision") == "TICK"
        assert symbol.get("timezone") == "EETUS"
        if expected_source is not None:
            assert symbol.get("source") == expected_source
        if expected_broker is not None:
            assert symbol.get("broker") == expected_broker

    params = {
        node.get("key"): node.text
        for node in wfm.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"Session", "MarketOpenSession", "LimitTimeRange", "RealisticGapsHandling", "StoreChartData"}
    }
    assert params == {
        "Session": "No Session",
        "MarketOpenSession": "No Session",
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
    }


def _assert_wfm_crosschecks_contract(wfm: ET.Element) -> None:
    crosschecks = wfm.find(".//CrossChecks")
    assert crosschecks is not None
    assert crosschecks.get("use") == "true"
    assert crosschecks.get("evaluateAll") == "true"

    active = [
        check.tag
        for check in list(crosschecks)
        if isinstance(check.tag, str) and check.get("use") == "true"
    ]
    assert active == ["WalkForwardMatrix"]

    walk_forward_matrix = crosschecks.find("WalkForwardMatrix")
    assert walk_forward_matrix is not None
    walk_forward = walk_forward_matrix.find("./Settings/WalkForward")
    assert walk_forward is not None
    assert walk_forward.attrib == {
        "type": "2",
        "period": "10",
        "optimization": "15",
        "distributionUp": "20",
        "distributionDown": "20",
        "maxSteps": "8",
    }
    assert walk_forward.find("Param1").attrib == {
        "value": "undefined",
        "start": "20",
        "stop": "36",
        "step": "2",
    }
    assert walk_forward.find("Param2").attrib == {
        "value": "undefined",
        "start": "5",
        "stop": "8",
        "step": "1",
    }
    assert walk_forward_matrix.findtext("./Settings/MaxTests") == "3000"
    what_to_parametrize = walk_forward_matrix.find("./Settings/WhatToParametrize")
    assert what_to_parametrize is not None
    assert what_to_parametrize.attrib == {"type": "1", "symmetricVariables": "false"}
    assert {
        child.tag: child.text
        for child in list(what_to_parametrize)
        if isinstance(child.tag, str)
    } == {
        "Recommended": "false",
        "Periods": "true",
        "Shifts": "false",
        "Constants": "true",
        "OtherParams": "false",
        "EntryParams": "true",
        "EntryLogic": "false",
        "ExitParamsUsed": "true",
        "ExitParamsUnused": "false",
        "BooleanParams": "false",
    }

    active_conditions = [
        (
            condition.find("./Left-Side/Column-Value").get("column"),
            condition.find("./Left-Side/Column-Value").get("resultType"),
            condition.find("./Left-Side/Column-Value").get("sampleType"),
            condition.find("./Left-Side/Column-Value").get("subresult"),
            condition.find("Comparator").get("value"),
            condition.find("./Right-Side/Numeric-Value").get("value"),
        )
        for condition in walk_forward_matrix.findall("./AcceptanceSettings/Conditions/Condition")
        if condition.get("use") == "true"
    ]
    assert active_conditions == [
        ("NetProfit", "WalkForwardMatrix", "20", "30", ">", "0"),
        ("NetProfit", "WalkForwardOptimization", "10", "31", ">", "60"),
        ("WFPctOfProfitableRuns", "WalkForwardOptimization", "10", "33", ">", "70"),
        ("WFMaxProfitByRunInPct", "WalkForwardOptimization", "10", "33", "<", "50"),
        ("WFMinTradesInRun", "WalkForwardOptimization", "10", "33", ">", "20"),
        ("WFMaxPctDDbyRun", "WalkForwardOptimization", "10", "33", "<=", "25"),
    ]

    inactive_methods = [
        method
        for check in list(crosschecks)
        if isinstance(check.tag, str) and check.tag != "WalkForwardMatrix"
        for method in check.findall("./Settings/Methods/Method")
    ]
    assert all(method.get("use") == "false" for method in inactive_methods)

    rankings = wfm.find(".//Rankings")
    if rankings is not None:
        assert rankings.findtext("ForceRunCrossChecks") == "false"


def _assert_wfm_static_tabs_contract(wfm: ET.Element) -> None:
    _assert_mc2_static_tabs_contract(wfm)
    _assert_wfm_custom_data_contract(wfm)


def _assert_capa2_wfm_static_tabs_contract(wfm: ET.Element) -> None:
    rankings = wfm.find(".//Rankings")
    assert rankings is not None
    assert rankings.get("type") == "never"
    assert rankings.findtext("DeleteFailedStrategies") == "true"
    assert rankings.findtext("ForceRunCrossChecks") == "false"
    assert rankings.findtext("./WalkForward/DontSaveOriginalStr") == "true"
    assert rankings.findtext("./WalkForward/DeleteFailedStr") == "true"
    assert rankings.find("FitPortfolio").get("active") == "false"
    assert rankings.find("CustomAnalysis").get("filter") == "false"
    assert rankings.findall("./Conditions/Condition") == []

    rmm_methods = {
        method.get("type"): method.get("use")
        for method in wfm.findall(".//RiskMoneyManagement//MoneyManagement/Method")
        if method.get("type")
    }
    assert rmm_methods == {
        "FixedSize": "false",
        "RiskFixedBalancePct": "false",
        "RiskFixedPctOfAccount": "false",
        "FixedAmount": "true",
        "StocksSizeByPrice": "false",
    }
    atms = wfm.find(".//ATMs")
    assert atms is not None
    assert atms.get("enable") == "false"
    selected = wfm.find(".//SelectedStrategies")
    if selected is not None:
        assert list(selected) == []
        assert (selected.text or "").strip() == ""
    _assert_wfm_custom_data_contract(wfm)


def _assert_wfm_custom_data_contract(wfm: ET.Element) -> None:
    custom = wfm.find("./CustomData")
    assert custom is not None
    assert "USDJPY" not in ET.tostring(custom, encoding="unicode")
    setup = custom.find("./Setups/Setup")
    assert setup is not None
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == C1_FASTEST_ROBUSTNESS_TEST_PRECISION
    assert setup.get("session") == "No Session"
    assert setup.get("engine") == "MetaTrader4"
    assert setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']").text == "0.0"
    assert dict(setup.find("MainTestValues").attrib) == {
        "engine": "true",
        "symbol": "true",
        "timeframe": "true",
        "dates": "true",
        "subcharts": "false",
        "precision": "true",
        "distance": "true",
        "spread": "true",
        "slippage": "true",
        "commissions": "true",
    }


def _assert_capa2_wfm_contract(
    wfm: ET.Element,
    expected_symbol: str,
    expected_timeframe: str,
    expected_source: str,
    expected_broker: str,
    expected_spread: str,
) -> None:
    _assert_wfm_data_databanks_resources_options_contract(
        wfm,
        expected_symbol=expected_symbol,
        expected_timeframe=expected_timeframe,
        expected_spread=expected_spread,
        expected_source=expected_source,
        expected_broker=expected_broker,
    )
    _assert_wfm_crosschecks_contract(wfm)
    _assert_capa2_wfm_static_tabs_contract(wfm)
    optimization = wfm.find("./Optimization")
    assert optimization is not None
    assert optimization.attrib == {"type": "3", "maxOptimizations": "3000"}
    assert optimization.find("Source").attrib == {"type": "2", "relativePath": "false"}
    assert optimization.find("WalkForward").attrib == {
        "type": "2",
        "period": "10",
        "optimization": "15",
        "distributionUp": "20",
        "distributionDown": "20",
        "maxSteps": "8",
    }
    assert optimization.find("./WalkForward/Param1").attrib == {
        "value": "undefined",
        "start": "20",
        "stop": "36",
        "step": "2",
    }
    assert optimization.find("./WalkForward/Param2").attrib == {
        "value": "undefined",
        "start": "5",
        "stop": "8",
        "step": "1",
    }
    assert optimization.find("OptimizationMethod").attrib == {
        "settings": "automatic",
        "method": "brute-force",
        "maxSteps": "20",
        "symmetricVariables": "false",
        "symmetryDisabled": "false",
    }
    assert optimization.find("AutomaticSettings").attrib == {
        "distributionUp": "20",
        "distributionDown": "20",
        "maxSteps": "8",
        "distribution": "20",
    }
    assert wfm.find(".//WhatToBuild/StrategyType").attrib == {
        "type": "simple",
        "architecture": "sq4",
        "improveType": "strategy",
        "improveDatabank": "SPP",
        "templateFile": "",
        "strategyFile": "",
        "additionalCharts": "2",
    }
    exit_types = {block.get("key"): block.get("use") for block in wfm.findall(".//Blocks/ExitTypes/Block")}
    assert exit_types["ExitAfterBars.ExitAfterBars"] == "false"
    assert exit_types["StopLoss.StopLoss"] == "true"
    assert exit_types["ProfitTarget.ProfitTarget"] == "true"
    assert exit_types["TrailingStop.TrailingStop"] == "true"


def _assert_capa2_forward_contract(
    forward: ET.Element,
    expected_symbol: str,
    expected_timeframe: str,
    expected_source: str,
    expected_broker: str,
    expected_spread: str,
    expected_window: tuple[str, str] = ("7200", "79200"),
) -> None:
    setup = forward.find("./Data/Setups/Setup")
    assert setup is not None
    assert setup.get("dateFrom") == "2025.01.01"
    assert setup.get("dateTo") == "2026.04.08"
    assert setup.get("testPrecision") == C1_TICK_TEST_PRECISION
    assert setup.get("session") == "No Session"
    assert setup.get("engine") == "MetaTrader5 (hedged)"
    chart = setup.find("Chart")
    assert chart is not None
    assert chart.attrib == {"symbol": expected_symbol, "timeframe": expected_timeframe, "spread": expected_spread}
    assert setup.find("./Commissions/Method[@type='SizeBased']").get("use") == "true"
    assert setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']").text == "0.0"
    assert [node.attrib for node in forward.findall("./Data/OutOfSample/Range")] == [
        {"dateFrom": "2025.01.01", "dateTo": "2026.01.01"},
        {"dateFrom": "2026.01.01", "dateTo": "2026.04.08"},
    ]
    assert forward.find("./CustomData").attrib == {"showAll": "false"}
    assert list(forward.find("./CustomData")) == []
    databanks = {
        databank.get("name"): databank.get("value")
        for databank in forward.findall(".//Databanks/Databank")
    }
    assert databanks == {"Output": "Forward", "Input": "WFM"}

    resources = forward.find(".//Resources")
    assert resources is not None
    symbols = resources.findall("./Symbols/Symbol")
    assert {symbol.get("name") for symbol in symbols} == {expected_symbol}
    assert {symbol.get("source") for symbol in symbols} == {expected_source}
    assert {symbol.get("broker") for symbol in symbols} == {expected_broker}
    assert {symbol.get("precision") for symbol in symbols} == {"TICK"}
    assert {symbol.get("timezone") for symbol in symbols} == {"EETUS"}
    assert resources.findall("./Sessions/Session") == []
    assert "dukascopy" not in ET.tostring(resources, encoding="unicode").lower()

    options = {
        node.get("key"): node.text
        for node in forward.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"LimitTimeRange", "SignalTimeRangeFrom", "SignalTimeRangeTo", "RealisticGapsHandling", "StoreChartData"}
    }
    assert options == {
        "LimitTimeRange": "true",
        "SignalTimeRangeFrom": expected_window[0],
        "SignalTimeRangeTo": expected_window[1],
        "RealisticGapsHandling": "true",
        "StoreChartData": "false",
    }

    crosschecks = forward.find(".//CrossChecks")
    assert crosschecks is not None
    assert crosschecks.attrib == {"use": "false", "evaluateAll": "false"}
    assert [
        check.tag
        for check in list(crosschecks)
        if isinstance(check.tag, str) and check.get("use") == "true"
    ] == []
    for method in crosschecks.findall(".//Settings/Methods/Method"):
        assert method.get("use") == "false"

    rankings = forward.find(".//Rankings")
    assert rankings is not None
    assert rankings.get("type") == "never"
    assert rankings.findtext("DeleteFailedStrategies") == "true"
    assert rankings.findtext("ForceRunCrossChecks") == "false"
    assert rankings.find("FitPortfolio").get("active") == "false"
    assert rankings.find("CustomAnalysis").get("filter") == "false"
    assert [
        (
            condition.find(".//Column-Value").get("column"),
            condition.find(".//Column-Value").get("sampleType"),
            condition.find(".//Comparator").get("value"),
            condition.find(".//Numeric-Value").get("value"),
        )
        for condition in rankings.findall("./Conditions/Condition")
    ] == [
        ("NumberOfTrades", "20", ">=", "30"),
        ("RExpectancy", "20", ">", "0"),
        ("NetProfit", "20", ">=", "0"),
    ]
    assert forward.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "WFM"
    exit_types = {block.get("key"): block.get("use") for block in forward.findall(".//Blocks/ExitTypes/Block")}
    assert exit_types["ExitAfterBars.ExitAfterBars"] == "false"
    assert exit_types["StopLoss.StopLoss"] == "true"
    assert exit_types["ProfitTarget.ProfitTarget"] == "true"
    assert exit_types["TrailingStop.TrailingStop"] == "true"


def _assert_foward_contract(
    forward: ET.Element,
    expected_symbol: str | None = None,
    expected_timeframe: str | None = None,
    expected_spread: str | None = None,
    expected_window: tuple[str, str] = ("7200", "79200"),
    expected_input_databank: str = "Synthetic",
    expected_output_databank: str = "Forward",
    expected_improve_databank: str = "Synthetic",
    expected_delete_failed: str = "true",
) -> None:
    setup = forward.find(".//Data/Setups/Setup")
    assert setup is not None
    assert setup.get("dateFrom") == "2025.01.01"
    assert setup.get("dateTo") == "2026.04.08"
    assert setup.get("testPrecision") == C1_TICK_TEST_PRECISION
    assert setup.get("session") == "No Session"
    assert setup.get("engine") == "MetaTrader5 (hedged)"
    assert [node.attrib for node in forward.findall(".//Data/OutOfSample/Range")] == [
        {"dateFrom": "2025.01.01", "dateTo": "2026.01.01"},
        {"dateFrom": "2026.01.01", "dateTo": "2026.04.08"},
    ]
    databanks = {
        databank.get("name"): databank.get("value")
        for databank in forward.findall(".//Databanks/Databank")
    }
    assert databanks == {"Output": expected_output_databank, "Input": expected_input_databank}
    charts = setup.findall("Chart")
    if expected_symbol is not None:
        assert {chart.get("symbol") for chart in charts} == {expected_symbol}
    if expected_timeframe is not None:
        assert {chart.get("timeframe") for chart in charts} == {expected_timeframe}
    if expected_spread is not None:
        assert {chart.get("spread") for chart in charts} == {expected_spread}
    resources = forward.find(".//Resources")
    assert resources is not None
    assert resources.findall("./Sessions/Session") == []
    assert {symbol.get("precision") for symbol in resources.findall("./Symbols/Symbol")} == {"TICK"}
    assert {symbol.get("timezone") for symbol in resources.findall("./Symbols/Symbol")} == {"EETUS"}
    if expected_symbol is not None:
        assert {symbol.get("name") for symbol in resources.findall("./Symbols/Symbol")} == {expected_symbol}

    options = {
        node.get("key"): node.text
        for node in forward.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"LimitTimeRange", "SignalTimeRangeFrom", "SignalTimeRangeTo", "RealisticGapsHandling", "StoreChartData"}
    }
    assert options == {
        "LimitTimeRange": "true",
        "SignalTimeRangeFrom": expected_window[0],
        "SignalTimeRangeTo": expected_window[1],
        "RealisticGapsHandling": "true",
        "StoreChartData": "false",
    }
    rankings = forward.find(".//Rankings")
    assert rankings is not None
    assert rankings.get("type") == "never"
    assert rankings.findtext("DeleteFailedStrategies") == expected_delete_failed
    assert rankings.findtext("ForceRunCrossChecks") == "false"
    assert rankings.find("FitPortfolio").get("active") == "false"
    assert rankings.find("CustomAnalysis").get("filter") == "false"
    assert [
        (
            condition.find(".//Column-Value").get("column"),
            condition.find(".//Column-Value").get("sampleType"),
            condition.find(".//Comparator").get("value"),
            condition.find(".//Numeric-Value").get("value"),
        )
        for condition in rankings.findall("./Conditions/Condition")
    ] == [
        ("NumberOfTrades", "20", ">=", "30"),
        ("RExpectancy", "20", ">", "0"),
        ("NetProfit", "20", ">=", "0"),
    ]
    _assert_static_crosschecks_contract(forward, require_selected_strategies=True)
    strategy_type = forward.find(".//WhatToBuild/StrategyType")
    assert strategy_type is not None
    assert strategy_type.get("improveDatabank") == expected_improve_databank
    build_mode = forward.find(".//WhatToBuild/BuildMode")
    assert build_mode.findtext("ShowLastGenerationDatabank") == "false"
    assert build_mode.findtext("FreshBloodReplaceSimilar") == "false"
    assert build_mode.findtext("FreshBloodReplaceWeakest") == "false"
    assert build_mode.find("EvoRestartOnFinish").get("status") == "false"
    assert build_mode.find("EvoRestartOnStagnation").get("status") == "false"
    order_types = {block.get("key"): block.get("use") for block in forward.findall(".//Blocks/OrderTypes/Block")}
    assert order_types == {
        "EnterAtMarket": "true",
        "EnterReverseAtMarket": "false",
        "EnterAtStop": "false",
        "EnterAtLimit": "false",
    }
    exit_types = {block.get("key"): block.get("use") for block in forward.findall(".//Blocks/ExitTypes/Block")}
    assert exit_types["ExitAfterBars.ExitAfterBars"] == "true"
    assert all(value == "false" for key, value in exit_types.items() if key != "ExitAfterBars.ExitAfterBars")
    assert not any("ExitAfterDays" in key or "ExitAfterTradingDays" in key for key in exit_types)


def _assert_tick_real_data_databanks_resources_contract(tick_real: ET.Element, expected_symbol: str | None = None, expected_timeframe: str | None = None) -> None:
    setup = tick_real.find(".//Data/Setups/Setup")
    assert setup is not None
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == C1_TICK_TEST_PRECISION
    assert setup.get("session") == "No Session"
    assert tick_real.findall(".//Data/OutOfSample/Range") == []

    databanks = {
        databank.get("name"): databank.get("value")
        for databank in tick_real.findall(".//Databanks/Databank")
    }
    assert databanks["Input"] == "retest 1"
    assert databanks["Output"] == "TICK"

    chart_symbols = {
        chart.get("symbol")
        for chart in tick_real.findall(".//Data/Setups/Setup/Chart")
        if chart.get("symbol")
    }
    if expected_symbol is not None:
        assert chart_symbols == {expected_symbol}
    if expected_timeframe is not None:
        assert {
            chart.get("timeframe")
            for chart in tick_real.findall(".//Data/Setups/Setup/Chart")
        } == {expected_timeframe}

    resources = tick_real.find(".//Resources")
    assert resources is not None
    resource_symbols = {
        symbol.get("name")
        for symbol in resources.findall("./Symbols/Symbol")
        if symbol.get("name")
    }
    broker_ids = {
        broker.get("id")
        for broker in resources.findall("./Brokers/Broker")
        if broker.get("id")
    }
    assert resource_symbols == chart_symbols
    assert resources.findall("./Sessions/Session") == []
    assert "USDJPY" not in ET.tostring(resources, encoding="unicode")
    for symbol in resources.findall("./Symbols/Symbol"):
        assert symbol.get("precision") == "TICK"
        assert symbol.get("timezone") == "EETUS"
        symbol_broker = symbol.get("broker")
        if broker_ids:
            assert symbol_broker in broker_ids or symbol_broker == "-1"
        else:
            assert symbol_broker in {"-1", None, ""}
        info = symbol.find("InstrumentInfo")
        assert info is not None
        info_broker = info.get("broker")
        if broker_ids:
            assert info_broker in broker_ids or info_broker == "-1"
        else:
            assert info_broker in {"-1", None, ""}


def _assert_tick_real_options_rankings_contract(tick_real: ET.Element, expected_window: tuple[str, str]) -> None:
    params = {
        node.get("key"): node.text
        for node in tick_real.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {
            "Session",
            "MarketOpenSession",
            "LimitTimeRange",
            "SignalTimeRangeFrom",
            "SignalTimeRangeTo",
            "RealisticGapsHandling",
            "StoreChartData",
        }
    }
    assert params == {
        "Session": "No Session",
        "MarketOpenSession": "No Session",
        "LimitTimeRange": "true",
        "SignalTimeRangeFrom": expected_window[0],
        "SignalTimeRangeTo": expected_window[1],
        "RealisticGapsHandling": "true",
        "StoreChartData": "false",
    }

    rankings = tick_real.find(".//Rankings")
    assert rankings is not None
    assert rankings.findtext("ConditionsType") == "1"
    assert rankings.findtext("DeleteFailedStrategies") == "true"
    assert rankings.findtext("ForceRunCrossChecks") == "false"
    assert rankings.find("FitPortfolio").get("active") == "false"
    assert rankings.find("CustomAnalysis").get("filter") == "false"
    conditions = [
        (
            condition.find(".//Column-Value").get("column"),
            condition.find(".//Column-Value").get("sampleType"),
            condition.find(".//Comparator").get("value"),
            condition.find(".//Numeric-Value").get("value"),
        )
        for condition in rankings.findall("./Conditions/Condition")
    ]
    assert conditions == [
        ("NumberOfTrades", "127", ">=", "200"),
        ("ProfitFactor", "127", ">=", "1.3"),
        ("WinningPct", "127", ">=", "50"),
        ("ReturnDDRatio", "127", ">=", "4"),
    ]


def _section_sha256(root: ET.Element, tab: str) -> str:
    node = root.find(tab)
    if node is None:
        node = root.find(f".//{tab}")
    assert node is not None
    text = ET.tostring(node, encoding="unicode", short_empty_elements=True).strip()
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def _xml_roots(cfx_path: Path):
    with zipfile.ZipFile(cfx_path) as archive:
        for name in archive.namelist():
            if name.endswith(".xml"):
                yield name, ET.fromstring(archive.read(name))


def _task_databanks(root: ET.Element) -> dict[str, str | None]:
    return {
        databank.get("name"): databank.get("value")
        for databank in root.findall(".//Databanks/Databank")
    }


CANONICAL_TASK_PERIOD_POLICY = {
    1: {
        "Build-Task1.xml": ("2017.10.02", "2023.01.01"),
        "Retest-Task3.xml": ("2017.10.02", "2025.01.01"),
        "Retest-Task1.xml": ("2010.01.01", "2017.10.02"),
        "AutomaticRetest-Task2.xml": ("2017.10.02", "2023.12.31"),
        "AutomaticRetest-Task1.xml": ("2017.10.02", "2023.12.31"),
        "AutomaticRetest-Task8.xml": ("2017.10.02", "2023.12.31"),
        "AutomaticRetest-Task3.xml": ("2017.10.02", "2023.12.31"),
        "AutomaticRetest-Task6.xml": ("2017.10.02", "2023.12.31"),
        "AutomaticRetest-Task5.xml": ("2017.10.02", "2023.12.31"),
        "AutomaticRetest-Task7.xml": ("2017.10.02", "2023.12.31"),
        "AutomaticRetest-Task4.xml": ("2017.10.02", "2023.12.31"),
        "Retest-Task2.xml": ("2025.01.01", "2026.04.08"),
    },
    2: {
        "Build-Task1.xml": ("2017.10.02", "2023.01.01"),
        "Retest-Task1.xml": ("2017.10.02", "2025.01.01"),
        "AutomaticRetest-Task7.xml": ("2010.01.01", "2017.10.02"),
        "AutomaticRetest-Task2.xml": ("2017.10.02", "2023.12.31"),
        "AutomaticRetest-Task1.xml": ("2017.10.02", "2023.12.31"),
        "AutomaticRetest-Task8.xml": ("2017.10.02", "2023.12.31"),
        "AutomaticRetest-Task3.xml": ("2017.10.02", "2023.12.31"),
        "AutomaticRetest-Task6.xml": ("2017.10.02", "2023.12.31"),
        "AutomaticRetest-Task5.xml": ("2017.10.02", "2023.12.31"),
        "AutomaticRetest-Task4.xml": ("2017.10.02", "2023.12.31"),
        "Optimize-Task1.xml": ("2017.10.02", "2023.12.31"),
        "Retest-Task2.xml": ("2025.01.01", "2026.04.08"),
    },
}

CANONICAL_GENERATED_TASK_PERIODS = {
    1: {
        **{name: {period} for name, period in CANONICAL_TASK_PERIOD_POLICY[1].items()},
        "Retest-Task4.xml": {
            ("2017.10.02", "2026.04.08"),
            ("2025.01.01", "2026.04.08"),
        },
        "Retest-Task5.xml": {
            ("2017.10.02", "2026.04.08"),
            ("2025.01.01", "2026.04.08"),
        },
    },
    2: {
        **{name: {period} for name, period in CANONICAL_TASK_PERIOD_POLICY[2].items()},
        "Retest-Task3.xml": {
            ("2017.10.02", "2026.04.08"),
            ("2025.01.01", "2026.04.08"),
        },
        "Retest-Task4.xml": {
            ("2017.10.02", "2026.04.08"),
            ("2025.01.01", "2026.04.08"),
        },
    },
}

CANONICAL_CORR_REVIEW_TASKS = {
    1: {
        "Retest-Task4.xml": {
            "title": "CORR1 STABILITY RETEST",
            "input": "Forward",
            "output": "SQX EDGE CORR1 STABILITY",
            "method": "none",
            "periods": {
                ("2017.10.02", "2026.04.08"),
                ("2025.01.01", "2026.04.08"),
            },
            "oos": [{"dateFrom": "2025.01.01", "dateTo": "2026.04.08"}],
        },
        "Retest-Task5.xml": {
            "title": "CORR1 TAG REVIEW",
            "input": "SQX EDGE CORR1 STABILITY",
            "output": "SQX EDGE CORR1 TAGGED",
            "method": "SQXEdgeCorrelationTagger",
            "periods": {
                ("2017.10.02", "2026.04.08"),
                ("2025.01.01", "2026.04.08"),
            },
            "oos": [{"dateFrom": "2025.01.01", "dateTo": "2026.04.08"}],
        },
    },
    2: {
        "Retest-Task3.xml": {
            "title": "C2 CORR STABILITY RETEST",
            "input": "Forward",
            "output": "SQX EDGE C2 CORR STABILITY",
            "method": "none",
            "periods": {
                ("2017.10.02", "2026.04.08"),
                ("2025.01.01", "2026.04.08"),
            },
            "oos": [
                {"dateFrom": "2025.01.01", "dateTo": "2026.01.01"},
                {"dateFrom": "2026.01.01", "dateTo": "2026.04.08"},
            ],
        },
        "Retest-Task4.xml": {
            "title": "C2 CORR TAG REVIEW",
            "input": "SQX EDGE C2 CORR STABILITY",
            "output": "SQX EDGE C2 CORR TAGGED",
            "method": "SQXEdgeCorrelationTagger",
            "periods": {
                ("2017.10.02", "2026.04.08"),
                ("2025.01.01", "2026.04.08"),
            },
            "oos": [
                {"dateFrom": "2025.01.01", "dateTo": "2026.01.01"},
                {"dateFrom": "2026.01.01", "dateTo": "2026.04.08"},
            ],
        },
    },
}


def _setup_periods(root: ET.Element) -> set[tuple[str | None, str | None]]:
    return {
        (setup.get("dateFrom"), setup.get("dateTo"))
        for setup in root.findall(".//Setup")
    }


def _assert_generated_task_periods(roots: dict[str, ET.Element], capa: int) -> None:
    for task_xml, expected in CANONICAL_GENERATED_TASK_PERIODS[capa].items():
        assert task_xml in roots
        assert _setup_periods(roots[task_xml]) == expected, task_xml


def _assert_automatic_retests_mark_date_ranges(roots: dict[str, ET.Element]) -> None:
    issues = []
    for task_xml, root in roots.items():
        if not task_xml.startswith("AutomaticRetest-"):
            continue
        values = root.findall(".//MainTestValues")
        if not values:
            issues.append((task_xml, "missing MainTestValues"))
            continue
        for node in values:
            if node.get("dates") != "true":
                issues.append((task_xml, dict(node.attrib)))
    assert issues == []


def _assert_corr_review_task_contracts(roots: dict[str, ET.Element], capa: int) -> None:
    config = roots["config.xml"]
    tasks = {task.get("taskXMLFile"): task for task in config.findall(".//Task")}
    for task_xml, expected in CANONICAL_CORR_REVIEW_TASKS[capa].items():
        assert task_xml in tasks
        assert tasks[task_xml].get("title") == expected["title"]
        root = roots[task_xml]
        assert _setup_periods(root) == expected["periods"]
        assert _task_databanks(root) == {
            "Input": expected["input"],
            "Output": expected["output"],
        }
        assert root.find(".//CustomAnalysis").get("method") == expected["method"]
        assert root.find(".//CustomAnalysis").get("filter") == "false"
        assert root.find(".//DeleteFailedStrategies").text == "false"
        assert root.find(".//CrossChecks").get("use") == "false"
        assert [dict(node.attrib) for node in root.findall(".//Data/OutOfSample/Range")] == expected["oos"]


def test_generator_task_period_policy_is_invariant_across_timeframes_and_directions():
    for capa, expected in CANONICAL_TASK_PERIOD_POLICY.items():
        actual = {
            task_xml: RETEST_PERIODS[period_key]
            for task_xml, period_key in CAPA_TASK_MAPS[capa].items()
        }
        for timeframe in ("M5", "M15", "M30", "H1", "H4"):
            for direction in ("long", "short", "both"):
                assert actual == expected, (capa, timeframe, direction)


def test_generator_date_period_doc_lists_corr_review_tasks_explicitly():
    doc = (TOOL_ROOT.parent.parent / "docs" / "SQX142_PROJECT_GENERATOR_DATE_PERIOD_CONTRACT.md").read_text(encoding="utf-8")
    for capa_tasks in CANONICAL_CORR_REVIEW_TASKS.values():
        for task_xml, expected in capa_tasks.items():
            assert task_xml in doc
            assert expected["title"] in doc
            assert expected["input"] in doc
            assert expected["output"] in doc
            assert expected["method"] in doc


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


def _config_absolute_path_attrs(config_root: ET.Element) -> list[tuple[str, str, str]]:
    refs: list[tuple[str, str, str]] = []
    for node in config_root.iter():
        for key, value in node.attrib.items():
            if ":\\" in value or ":/" in value:
                refs.append((node.tag, key, value))
    return refs


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
    assert build_setup.get("testPrecision") == "2"
    assert build_setup.get("session") == "No Session"
    assert build.findall(".//Data/OutOfSample/Range") == []
    assert build.find(".//RiskMoneyManagement//Method[@type='FixedSize']").get("use") == "true"
    assert build.find(".//RiskMoneyManagement//Method[@type='FixedAmount']").get("use") == "false"

    retest0 = roots["Retest-Task3.xml"]
    retest0_setup = retest0.find(".//Data/Setups/Setup")
    retest0_oos = retest0.find(".//Data/OutOfSample/Range")
    assert retest0_setup.get("dateFrom") == "2017.10.02"
    assert retest0_setup.get("dateTo") == "2025.01.01"
    assert retest0_oos.get("dateFrom") == "2023.01.01"
    assert retest0_oos.get("dateTo") == "2025.01.01"

    tick_real = roots["AutomaticRetest-Task2.xml"]
    _assert_tick_real_data_databanks_resources_contract(tick_real, expected_symbol="AUDCAD_darwinex", expected_timeframe="H1")
    _assert_tick_real_options_rankings_contract(tick_real, expected_window=("7200", "79200"))
    _assert_tick_real_passive_generation_contract(tick_real)
    _assert_tick_real_static_crosschecks_contract(tick_real)

    retest1 = roots["Retest-Task1.xml"]
    retest1_options = {
        node.get("key"): node.text
        for node in retest1.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"RealisticGapsHandling", "MarketOpenSession", "SignalTimeRangeFrom", "SignalTimeRangeTo"}
    }
    assert retest1_options == {
        "RealisticGapsHandling": "true",
        "MarketOpenSession": "No Session",
        "SignalTimeRangeFrom": "7200",
        "SignalTimeRangeTo": "79200",
    }
    retest1_rankings = retest1.find(".//Rankings")
    assert retest1_rankings.findtext("DeleteFailedStrategies") == "true"
    assert retest1_rankings.find("FitPortfolio").get("active") == "false"
    retest1_ranking_conditions = [
        (
            condition.find(".//Column-Value").get("column"),
            condition.find(".//Comparator").get("value"),
            condition.find(".//Numeric-Value").get("value"),
        )
        for condition in retest1_rankings.findall("./Conditions/Condition")
    ]
    assert retest1_ranking_conditions == [
        ("NumberOfTrades", ">=", "100"),
        ("RExpectancy", ">=", "0.05"),
        ("NetProfit", ">=", "0"),
    ]
    retest1_auto_dismissal = {
        problem.get("code"): problem.get("dismiss")
        for problem in retest1_rankings.findall("./AutomaticDismissal/Problem")
    }
    assert retest1_auto_dismissal["2"] == "false"
    _assert_retest1_passive_generation_contract(retest1)
    _assert_retest1_static_crosschecks_contract(retest1)

    forward = roots["Retest-Task2.xml"]
    _assert_foward_contract(
        forward,
        expected_symbol="AUDCAD_darwinex",
        expected_timeframe="H1",
        expected_spread="2.0",
    )


def test_capa2_base_tick_real_matches_phase20_methodology():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa2_Base.cfx"))
    config = roots["config.xml"]
    task = next(task for task in config.findall(".//Task") if task.get("taskXMLFile") == "AutomaticRetest-Task2.xml")
    databanks = {
        databank.get("name"): databank.get("view")
        for databank in config.findall(".//Databank")
    }

    assert task.get("title") == "TICK REAL"
    assert "HBP" not in databanks
    assert databanks["TICK"] == "RETEST ROBUST REVIEW"

    tick_real = roots["AutomaticRetest-Task2.xml"]
    _assert_tick_real_data_databanks_resources_contract(
        tick_real,
        expected_symbol="AUDCAD_darwinex",
        expected_timeframe="H1",
    )
    symbols = tick_real.findall(".//Resources/Symbols/Symbol")
    assert {symbol.get("source") for symbol in symbols} == {"4"}
    assert {symbol.get("broker") for symbol in symbols} == {"4"}
    assert [broker.get("id") for broker in tick_real.findall(".//Resources/Brokers/Broker")] == ["4"]
    _assert_tick_real_options_rankings_contract(tick_real, expected_window=("7200", "79200"))
    _assert_tick_real_passive_generation_contract(
        tick_real,
        expected_exit_after_bars="false",
        expected_enabled_exits={
            "StopLoss.StopLoss",
            "ProfitTarget.ProfitTarget",
            "TrailingStop.TrailingStop",
        },
        expected_blocks_version=None,
        expect_no_signal_or_stoplimit_blocks=False,
    )
    _assert_tick_real_static_crosschecks_contract(tick_real)


def test_capa2_base_mc_matches_phase21_methodology():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa2_Base.cfx"))
    config = roots["config.xml"]
    task = next(task for task in config.findall(".//Task") if task.get("taskXMLFile") == "AutomaticRetest-Task1.xml")
    databanks = {
        databank.get("name"): databank.get("view")
        for databank in config.findall(".//Databank")
    }

    assert task.get("title") == "MC"
    assert databanks["MC"] == "GENERAL"
    _assert_capa2_mc_contract(
        roots["AutomaticRetest-Task1.xml"],
        expected_symbol="AUDCAD_darwinex",
        expected_timeframe="H1",
        expected_source="4",
        expected_broker="4",
    )


def test_capa2_base_mc2_matches_phase22_methodology():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa2_Base.cfx"))
    config = roots["config.xml"]
    task = next(task for task in config.findall(".//Task") if task.get("taskXMLFile") == "AutomaticRetest-Task8.xml")
    databanks = {
        databank.get("name"): databank.get("view")
        for databank in config.findall(".//Databank")
    }

    assert task.get("title") == "MC 2"
    assert databanks["MC2"] == "GENERAL"
    _assert_capa2_mc2_contract(
        roots["AutomaticRetest-Task8.xml"],
        expected_symbol="AUDCAD_darwinex",
        expected_timeframe="H1",
        expected_source="4",
        expected_broker="4",
        expected_spread="2.0",
        expected_spread_min="4",
        expected_spread_max="10",
    )


def test_capa2_base_sequential_matches_phase23_methodology():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa2_Base.cfx"))
    config = roots["config.xml"]
    task = next(task for task in config.findall(".//Task") if task.get("taskXMLFile") == "AutomaticRetest-Task3.xml")
    databanks = {
        databank.get("name"): databank.get("view")
        for databank in config.findall(".//Databank")
    }

    assert task.get("title") == "Sequential"
    assert databanks["Sequential"] == "GENERAL"
    _assert_capa2_sequential_contract(
        roots["AutomaticRetest-Task3.xml"],
        expected_symbol="AUDCAD_darwinex",
        expected_timeframe="H1",
        expected_source="4",
        expected_broker="4",
        expected_spread="2.0",
    )


def test_capa2_base_monkey_matches_phase24_methodology():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa2_Base.cfx"))
    config = roots["config.xml"]
    task = next(task for task in config.findall(".//Task") if task.get("taskXMLFile") == "AutomaticRetest-Task6.xml")
    databanks = {
        databank.get("name"): databank.get("view")
        for databank in config.findall(".//Databank")
    }

    assert task.get("title") == "Monkey Test"
    assert databanks["Monkey Test"] == "MC MONKEY RETEST"
    _assert_capa2_monkey_contract(
        roots["AutomaticRetest-Task6.xml"],
        expected_symbol="AUDCAD_darwinex",
        expected_timeframe="H1",
        expected_source="4",
        expected_broker="4",
        expected_spread="2.0",
    )


def test_capa2_base_synthetic_matches_phase25_methodology():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa2_Base.cfx"))
    config = roots["config.xml"]
    task = next(task for task in config.findall(".//Task") if task.get("taskXMLFile") == "AutomaticRetest-Task5.xml")
    databanks = {
        databank.get("name"): databank.get("view")
        for databank in config.findall(".//Databank")
    }

    assert task.get("title") == "Synthetic"
    assert databanks["Synthetic"] == "MC SYNTHETIC RETEST"
    _assert_capa2_synthetic_contract(
        roots["AutomaticRetest-Task5.xml"],
        expected_symbol="AUDCAD_darwinex",
        expected_timeframe="H1",
        expected_source="4",
        expected_broker="4",
        expected_spread="2.0",
    )


def test_capa2_base_spp_matches_phase26_methodology():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa2_Base.cfx"))
    config = roots["config.xml"]
    task = next(task for task in config.findall(".//Task") if task.get("taskXMLFile") == "AutomaticRetest-Task4.xml")
    databanks = {
        databank.get("name"): databank.get("view")
        for databank in config.findall(".//Databank")
    }

    assert task.get("title") == "SPP"
    assert databanks["SPP"] == "RETEST ROBUST REVIEW"
    _assert_capa2_spp_contract(
        roots["AutomaticRetest-Task4.xml"],
        expected_symbol="AUDCAD_darwinex",
        expected_timeframe="H1",
        expected_source="4",
        expected_broker="4",
        expected_spread="2.0",
    )


def test_capa2_base_wfm_matches_phase27_methodology():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa2_Base.cfx"))
    config = roots["config.xml"]
    task = next(task for task in config.findall(".//Task") if task.get("taskXMLFile") == "Optimize-Task1.xml")
    databanks = {
        databank.get("name"): databank.get("view")
        for databank in config.findall(".//Databank")
    }

    assert task.get("title") == "WFM"
    assert databanks["WFM"] == "RETEST ROBUST REVIEW"
    _assert_capa2_wfm_contract(
        roots["Optimize-Task1.xml"],
        expected_symbol="AUDCAD_darwinex",
        expected_timeframe="H1",
        expected_source="4",
        expected_broker="4",
        expected_spread="2.0",
    )


def test_capa2_base_forward_matches_phase28_methodology():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa2_Base.cfx"))
    config = roots["config.xml"]
    task = next(task for task in config.findall(".//Task") if task.get("taskXMLFile") == "Retest-Task2.xml")
    databanks = {
        databank.get("name"): databank.get("view")
        for databank in config.findall(".//Databank")
    }

    assert task.get("title") == "Forward"
    assert databanks["Forward"] == "RETEST QUICK REVIEW"
    _assert_capa2_forward_contract(
        roots["Retest-Task2.xml"],
        expected_symbol="AUDCAD_darwinex",
        expected_timeframe="H1",
        expected_source="4",
        expected_broker="4",
        expected_spread="2.0",
    )


def test_capa1_build_resources_are_generic_generator_owned_placeholder():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    build = roots["Build-Task1.xml"]
    resources = build.find(".//Resources")
    assert resources is not None

    chart_symbols = {
        chart.get("symbol")
        for chart in build.findall(".//Data/Setups/Setup/Chart")
        if chart.get("symbol")
    }
    symbols = resources.findall("./Symbols/Symbol")
    symbol_names = {symbol.get("name") for symbol in symbols}
    broker_ids = {broker.get("id") for broker in resources.findall("./Brokers/Broker")}

    assert chart_symbols == symbol_names
    assert resources.findall("./Sessions/Session") == []
    assert "USDJPY" not in ET.tostring(resources, encoding="unicode")
    assert {symbol.get("precision") for symbol in symbols} == {"TICK"}
    assert {symbol.find("InstrumentInfo").get("dataType") for symbol in symbols} == {"3"}
    assert all(symbol.get("broker") in broker_ids for symbol in symbols)
    assert all(symbol.find("InstrumentInfo").get("instrument") in symbol_names for symbol in symbols)


def test_capa1_build_crosschecks_only_enable_sequential_optimization():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    build = roots["Build-Task1.xml"]
    crosschecks = build.find(".//CrossChecks")
    assert crosschecks is not None
    assert crosschecks.get("use") == "true"
    assert crosschecks.get("evaluateAll") == "true"

    check_states = {
        check.tag: check.get("use")
        for check in list(crosschecks)
        if isinstance(check.tag, str) and check.get("use") is not None
    }
    assert check_states["SequentialOptimization"] == "true"
    assert [name for name, state in check_states.items() if state == "true"] == ["SequentialOptimization"]
    assert check_states["MonteCarloRetest"] == "false"
    assert check_states["MonteCarloManipulation"] == "false"
    assert check_states["WalkForwardOptimization"] == "false"
    assert check_states["RetestOnAdditionalMarkets"] == "false"


def test_capa1_build_static_tabs_keep_confirmed_current_contract():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    build = roots["Build-Task1.xml"]
    expected = {
        "Options": "BF732DD7B130086DC0EA2E16669A270AC42A5910763B72B9DA001BCE4F22038C",
        "ATMs": "5B18484BDCBB462F169B894A8861C05F7DA323B05EE808FA49BB300442E56C40",
        "PartsToImprove": "14258C2F5FBFB077CE7FC4009F1D89FB32BD7FD2EBD66EAFF5F1ECB33411AC87",
        "RiskMoneyManagement": "CFBC9E6C4D1C30782BAC103AED72CFAF66AAA71BF4B892A4CEDDBA1E6317B76F",
        "Databanks": "50A09F40FAE0412D200151C0C74AA424BE6B19573B3514AA2D5DF6379F47BAB2",
        "Notes": "7E0C7BB76E5A63E6CD5B9B97F2571F549C95DF5F79CD0C315895ADAF2742E880",
        "Optimization": "63655CE465154201278796A666D9FC0A21B36EAF825B356797927DBC8402E3A8",
    }
    for tab, digest in expected.items():
        assert _section_sha256(build, tab) == digest

    databanks = {
        databank.get("name"): databank.get("value")
        for databank in build.findall(".//Databanks/Databank")
    }
    assert databanks == {"Output": "null", "Input": "Synthetic"}
    assert build.find(".//RiskMoneyManagement//Method[@type='FixedSize']").get("use") == "true"
    assert build.find(".//RiskMoneyManagement//Method[@type='FixedAmount']").get("use") == "false"


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
    assert views["Forward"] == "RETEST QUICK REVIEW"
    assert views["TICK"] == "RETEST ROBUST REVIEW"
    assert views["MC"] == "RETEST ROBUST REVIEW"
    assert views["MC2"] == "RETEST ROBUST REVIEW"
    assert views["Sequential"] == "RETEST ROBUST REVIEW"
    assert views["SPP"] == "RETEST ROBUST REVIEW"
    assert views["WFM"] == "RETEST ROBUST REVIEW"
    assert views["Monkey Test"] == "MC MONKEY RETEST"
    assert views["Synthetic"] == "MC SYNTHETIC RETEST"


def test_capa1_mc2_crosschecks_use_adaptive_seed_spread_range():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    mc2 = roots["AutomaticRetest-Task8.xml"]
    _assert_mc2_data_databanks_resources_options_contract(mc2, expected_symbol="AUDCAD_darwinex", expected_timeframe="H1")
    crosschecks = mc2.find(".//CrossChecks")
    assert crosschecks is not None
    assert crosschecks.get("use") == "true"
    assert crosschecks.get("evaluateAll") == "true"

    check_states = {
        check.tag: check.get("use")
        for check in list(crosschecks)
        if isinstance(check.tag, str) and check.get("use") is not None
    }
    assert [name for name, state in check_states.items() if state == "true"] == ["MonteCarloRetest"]

    monte_carlo_retest = crosschecks.find("MonteCarloRetest")
    assert monte_carlo_retest.findtext("./Settings/NumberOfSimulations") == "100"
    assert monte_carlo_retest.findtext("./Settings/MCUseFullSample") == "true"
    method_states = {
        method.get("type"): method.get("use")
        for method in monte_carlo_retest.findall("./Settings/Methods/Method")
        if method.get("type")
    }
    assert {name for name, state in method_states.items() if state == "true"} == {"RandomizeHistoryData", "RandomizeSpread"}
    assert _randomize_spread_params(mc2) == {"Min": "4", "Max": "10"}
    assert {
        setup.get("testPrecision")
        for setup in mc2.findall(".//CrossChecks/*/Settings/Setups/Setup")
    } <= {C1_FASTEST_ROBUSTNESS_TEST_PRECISION}
    _assert_mc2_passive_generation_contract(mc2)
    _assert_mc2_static_tabs_contract(mc2)


def test_capa1_sequential_open_gate_receives_mc2_and_keeps_sequential_optimization():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    sequential = roots["AutomaticRetest-Task3.xml"]
    databanks = {
        databank.get("name"): databank.get("value")
        for databank in sequential.findall(".//Databanks/Databank")
    }
    assert databanks == {"Output": "Sequential", "Input": "MC2"}

    crosschecks = sequential.find(".//CrossChecks")
    assert crosschecks is not None
    assert crosschecks.get("use") == "true"
    assert crosschecks.get("evaluateAll") == "true"
    active = [
        check.tag
        for check in list(crosschecks)
        if isinstance(check.tag, str) and check.get("use") == "true"
    ]
    assert active == ["SequentialOptimization"]
    sequential_optimization = crosschecks.find("SequentialOptimization")
    assert sequential_optimization is not None
    parameter_settings = {
        child.tag: child.text
        for child in sequential_optimization.findall("./Settings/ParameterSettings/*")
    }
    assert parameter_settings == {
        "DistributionUp": "130",
        "DistributionDown": "70",
        "Steps": "12",
        "ApplyToStrategy": "false",
    }
    what_to_parametrize = sequential_optimization.find("./Settings/WhatToParametrize")
    assert what_to_parametrize is not None
    assert what_to_parametrize.attrib == {"type": "1", "symmetricVariables": "false"}
    assert {
        child.tag: child.text
        for child in what_to_parametrize
    } == {
        "Recommended": "false",
        "Periods": "true",
        "Shifts": "false",
        "Constants": "true",
        "OtherParams": "false",
        "EntryParams": "false",
        "EntryLogic": "false",
        "ExitParamsUsed": "true",
        "ExitParamsUnused": "false",
        "BooleanParams": "false",
    }
    assert sequential_optimization.findtext("./Settings/ParameterSettings/ApplyToStrategy") == "false"
    assert sequential_optimization.findtext("./AcceptanceSettings/PctToPass") == "80"
    assert sequential_optimization.findtext("./AcceptanceSettings/ResultsCount") == "5"
    assert sequential_optimization.findtext("./AcceptanceSettings/StabilityRange") == "25"
    assert sequential_optimization.findall("./AcceptanceSettings/Conditions/Condition") == []
    inactive_methods = [
        method
        for check in list(crosschecks)
        if isinstance(check.tag, str) and check.tag != "SequentialOptimization"
        for method in check.findall("./Settings/Methods/Method")
    ]
    assert all(method.get("use") == "false" for method in inactive_methods)

    rankings = sequential.find(".//Rankings")
    assert rankings is not None
    assert rankings.get("type") == "never"
    assert rankings.findtext("DeleteFailedStrategies") == "true"
    assert rankings.findtext("ForceRunCrossChecks") == "false"
    assert rankings.find("CustomAnalysis").get("filter") == "false"
    assert sequential.findall(".//Data/OutOfSample/Range") == []

    data_setup = sequential.find("./Data/Setups/Setup")
    custom_setup = sequential.find("./CustomData/Setups/Setup")
    assert data_setup is not None
    assert custom_setup is not None
    assert data_setup.get("dateFrom") == custom_setup.get("dateFrom") == "2017.10.02"
    assert data_setup.get("dateTo") == custom_setup.get("dateTo") == "2023.12.31"
    assert data_setup.get("testPrecision") == custom_setup.get("testPrecision") == C1_FASTEST_ROBUSTNESS_TEST_PRECISION
    assert data_setup.get("session") == custom_setup.get("session") == "No Session"
    assert data_setup.find("Chart").attrib == custom_setup.find("Chart").attrib == {
        "symbol": "AUDCAD_darwinex",
        "timeframe": "H1",
        "spread": "2.0",
    }
    params = {
        node.get("key"): node.text
        for node in sequential.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"LimitTimeRange", "RealisticGapsHandling", "StoreChartData", "Session", "MarketOpenSession"}
    }
    assert params == {
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
        "Session": "No Session",
        "MarketOpenSession": "No Session",
    }
    _assert_sequential_passive_generation_contract(sequential)
    _assert_sequential_static_tabs_contract(sequential)


def test_capa1_monkey_test_data_gate_receives_sequential_and_keeps_dual_carrier():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    monkey = roots["AutomaticRetest-Task6.xml"]
    _assert_monkey_data_databanks_resources_options_contract(
        monkey,
        expected_symbol="AUDCAD_darwinex",
        expected_timeframe="H1",
        expected_spread="2.0",
    )
    _assert_monkey_crosschecks_contract(monkey)
    _assert_monkey_passive_generation_contract(monkey)
    _assert_monkey_static_tabs_contract(monkey)


def test_capa1_synthetic_data_gate_receives_monkey_and_keeps_dual_carrier():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    synthetic = roots["AutomaticRetest-Task5.xml"]
    _assert_synthetic_data_databanks_resources_options_contract(
        synthetic,
        expected_symbol="AUDCAD_darwinex",
        expected_timeframe="H1",
        expected_spread="2.0",
    )
    _assert_synthetic_crosschecks_contract(synthetic)
    _assert_synthetic_passive_generation_contract(synthetic)
    _assert_synthetic_static_tabs_contract(synthetic)


def test_capa1_spp_data_gate_receives_synthetic_and_keeps_customdata_carrier():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    spp = roots["AutomaticRetest-Task7.xml"]
    _assert_spp_data_databanks_resources_options_contract(
        spp,
        expected_symbol="AUDCAD_darwinex",
        expected_timeframe="H1",
        expected_spread="2.0",
    )
    _assert_spp_crosschecks_contract(spp)
    _assert_spp_static_tabs_contract(spp)


def test_capa1_wfm_data_gate_receives_spp_and_keeps_dual_carrier():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    wfm = roots["AutomaticRetest-Task4.xml"]
    _assert_wfm_data_databanks_resources_options_contract(
        wfm,
        expected_symbol="AUDCAD_darwinex",
        expected_timeframe="H1",
        expected_spread="2.0",
    )
    _assert_wfm_crosschecks_contract(wfm)
    _assert_wfm_static_tabs_contract(wfm)


def test_capa1_base_uses_confirmed_build_ranking_volume():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    build = roots["Build-Task1.xml"]
    ranking = build.find(".//Rankings")
    assert ranking is not None
    assert (ranking.findtext("MaxStrategies") or "").strip() == "2000"
    stop_condition = ranking.find("StopCondition")
    assert stop_condition is not None
    assert stop_condition.get("type") == "databank-full"
    assert stop_condition.get("passedStrategies") == "500"


def test_capa1_build_genetic_options_use_current_sqx142_nodes_only():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    build = roots["Build-Task1.xml"]
    build_mode = build.find(".//WhatToBuild/BuildMode")
    assert build_mode is not None
    assert build_mode.find("FilterInitialPopulation") is None
    assert build_mode.find("EvoFitnessRestartType") is None
    assert build_mode.find("EvoStagnationRestartGenerations") is None
    restart = build_mode.find("EvoRestartOnStagnation")
    assert restart is not None
    assert restart.get("status") == "true"
    assert restart.get("fitnessType") == "10"
    assert restart.get("generations") == "10"


def test_capa1_build_blocks_keep_only_market_entry_and_exit_after_bars():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    build = roots["Build-Task1.xml"]
    blocks = build.find(".//Blocks")
    assert blocks is not None

    order_types = {
        block.get("key"): block.get("use")
        for block in blocks.findall("./OrderTypes/Block")
    }
    assert order_types == {
        "EnterAtMarket": "true",
        "EnterReverseAtMarket": "false",
        "EnterAtStop": "false",
        "EnterAtLimit": "false",
    }

    exit_types = {
        block.get("key"): block.get("use")
        for block in blocks.findall("./ExitTypes/Block")
    }
    assert exit_types["ExitAfterBars.ExitAfterBars"] == "true"
    assert all(value == "false" for key, value in exit_types.items() if key != "ExitAfterBars.ExitAfterBars")
    assert not any("ExitAfterDays" in key or "ExitAfterTradingDays" in key for key in exit_types)

    custom_data = blocks.find("CustomData")
    assert custom_data is not None
    assert custom_data.get("showAll") == "false"
    assert list(custom_data) == []


def test_capa1_build_blocks_disable_signals_and_stop_limit_preserve_indicators():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    build = roots["Build-Task1.xml"]
    blocks = build.find(".//Blocks")
    assert blocks is not None

    signals = [block for block in blocks.findall(".//Block") if block.get("category") == "signals"]
    stop_limit_blocks = [block for block in blocks.findall(".//Block") if block.get("category") == "stopLimitBlocks"]
    indicators = [block for block in blocks.findall(".//Block") if block.get("category") == "indicators"]

    assert signals
    assert stop_limit_blocks
    assert indicators
    assert all(block.get("use") == "false" for block in signals)
    assert all(block.get("use") == "false" for block in stop_limit_blocks)
    assert any(block.get("use") == "true" for block in indicators)


def test_capa1_build_blocks_match_resolved_volatility_h4_blocksetting():
    roots = dict(_xml_roots(TEMPLATE_DIR / "Capa1_Long.cfx"))
    build = roots["Build-Task1.xml"]
    blocks = build.find(".//Blocks")
    assert blocks is not None
    expected = _blocksetting_entry("BS_Volatilidad_v6")

    active_keys = _active_building_block_keys(blocks)
    active_indicator_keys = [key for key in active_keys if key.startswith("Indicators.")]

    assert set(active_keys) == set(expected["activeBlocks"])
    assert set(active_indicator_keys) == set(expected["activeIndicators"])


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

    _assert_generated_task_periods(roots, 1)
    _assert_automatic_retests_mark_date_ranges(roots)
    _assert_corr_review_task_contracts(roots, 1)
    config = roots["config.xml"]
    build_task = next(task for task in config.findall(".//Task") if task.get("type") == "Build")
    assert build_task.get("title") == "Build BS_Volatilidad_v6 · Capa1 L+S H4"
    assert _config_absolute_path_attrs(config) == []

    build = roots["Build-Task1.xml"]
    setup = build.find(".//Data/Setups/Setup")
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.01.01"
    assert setup.get("testPrecision") == "2"
    assert setup.get("session") == "No Session"
    assert build.findall(".//Data/OutOfSample/Range") == []
    charts = build.findall(".//Data/Setups/Setup/Chart")
    assert {chart.get("symbol") for chart in charts} == {"AUDCAD"}
    assert {chart.get("timeframe") for chart in charts} == {"H4"}
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

    retest0 = roots["Retest-Task3.xml"]
    retest0_setup = retest0.find(".//Data/Setups/Setup")
    retest0_oos = retest0.find(".//Data/OutOfSample/Range")
    assert retest0_setup.get("dateFrom") == "2017.10.02"
    assert retest0_setup.get("dateTo") == "2025.01.01"
    assert retest0_oos.get("dateFrom") == "2023.01.01"
    assert retest0_oos.get("dateTo") == "2025.01.01"
    assert {chart.get("symbol") for chart in retest0.findall(".//Data/Setups/Setup/Chart")} == {"AUDCAD"}
    assert {chart.get("timeframe") for chart in retest0.findall(".//Data/Setups/Setup/Chart")} == {"H4"}
    assert {chart.get("spread") for chart in retest0.findall(".//Data/Setups/Setup/Chart")} == {"10"}
    retest0_swap = retest0_setup.find("Swap")
    assert retest0_swap is not None
    assert retest0_swap.get("long") == "-1.0"
    assert retest0_swap.get("short") == "-1.0"
    retest0_commission = retest0_setup.find("Commissions/Method[@type='SizeBased']")
    assert retest0_commission is not None
    assert retest0_commission.get("use") == "true"
    assert retest0_commission.find("Params/Param[@key='Commission']").text == "0.0"
    retest0_resources = retest0.findall(".//Resources/Symbols/Symbol")
    assert {node.get("name") for node in retest0_resources} == {"AUDCAD"}
    assert {node.find("InstrumentInfo").get("defaultSpread") for node in retest0_resources} == {"10"}

    tick_real = roots["AutomaticRetest-Task2.xml"]
    tick_setup = tick_real.find(".//Data/Setups/Setup")
    assert tick_setup.get("dateFrom") == "2017.10.02"
    assert tick_setup.get("dateTo") == "2023.12.31"
    _assert_tick_real_data_databanks_resources_contract(tick_real, expected_symbol="AUDCAD", expected_timeframe="H4")
    _assert_tick_real_options_rankings_contract(tick_real, expected_window=("14400", "72000"))
    _assert_tick_real_passive_generation_contract(tick_real)
    _assert_tick_real_static_crosschecks_contract(tick_real)

    mc = roots["AutomaticRetest-Task1.xml"]
    mc_options = {
        node.get("key"): node.text
        for node in mc.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"LimitTimeRange", "RealisticGapsHandling", "StoreChartData"}
    }
    assert mc_options == {
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
    }

    mc2 = roots["AutomaticRetest-Task8.xml"]
    _assert_mc2_data_databanks_resources_options_contract(mc2, expected_symbol="AUDCAD", expected_timeframe="H4")
    _assert_mc2_passive_generation_contract(mc2)
    _assert_mc2_static_tabs_contract(mc2)
    assert {chart.get("spread") for chart in mc2.findall(".//Chart")} == {"10"}
    assert _randomize_spread_params(mc2) == {"Min": "20", "Max": "50"}

    sequential = roots["AutomaticRetest-Task3.xml"]
    sequential_options = {
        node.get("key"): node.text
        for node in sequential.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"LimitTimeRange", "RealisticGapsHandling", "StoreChartData"}
    }
    assert sequential_options == {
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
    }
    assert {
        databank.get("name"): databank.get("value")
        for databank in sequential.findall(".//Databanks/Databank")
    } == {"Output": "Sequential", "Input": "MC2"}
    assert {chart.get("symbol") for chart in sequential.findall(".//Setup/Chart")} == {"AUDCAD"}
    assert {chart.get("timeframe") for chart in sequential.findall(".//Setup/Chart")} == {"H4"}
    assert {chart.get("spread") for chart in sequential.findall(".//Setup/Chart")} == {"10"}
    sequential_optimization = sequential.find(".//CrossChecks/SequentialOptimization")
    assert sequential_optimization is not None
    assert sequential_optimization.findtext("./Settings/ParameterSettings/ApplyToStrategy") == "false"
    assert sequential_optimization.findtext("./AcceptanceSettings/PctToPass") == "80"
    assert sequential_optimization.findall("./AcceptanceSettings/Conditions/Condition") == []
    _assert_sequential_passive_generation_contract(sequential)
    _assert_sequential_static_tabs_contract(sequential)

    monkey = roots["AutomaticRetest-Task6.xml"]
    _assert_monkey_data_databanks_resources_options_contract(
        monkey,
        expected_symbol="AUDCAD",
        expected_timeframe="H4",
        expected_spread="10",
    )
    assert {chart.get("spread") for chart in monkey.findall(".//Setup/Chart")} == {"10"}
    _assert_monkey_crosschecks_contract(monkey)
    _assert_monkey_passive_generation_contract(monkey)
    _assert_monkey_static_tabs_contract(monkey)

    synthetic = roots["AutomaticRetest-Task5.xml"]
    _assert_synthetic_data_databanks_resources_options_contract(
        synthetic,
        expected_symbol="AUDCAD",
        expected_timeframe="H4",
        expected_spread="10",
        expected_output_databank="Synthetic",
    )
    assert {chart.get("spread") for chart in synthetic.findall(".//Setup/Chart")} == {"10"}
    _assert_synthetic_crosschecks_contract(synthetic)
    _assert_synthetic_passive_generation_contract(synthetic)
    _assert_synthetic_static_tabs_contract(synthetic)

    spp = roots["AutomaticRetest-Task7.xml"]
    _assert_spp_data_databanks_resources_options_contract(
        spp,
        expected_symbol="AUDCAD",
        expected_timeframe="H4",
        expected_spread="10",
        expected_input_databank="Synthetic",
    )
    assert {chart.get("spread") for chart in spp.findall(".//Setup/Chart")} == {"10"}
    _assert_spp_crosschecks_contract(spp)
    _assert_spp_static_tabs_contract(spp)

    wfm = roots["AutomaticRetest-Task4.xml"]
    _assert_wfm_data_databanks_resources_options_contract(
        wfm,
        expected_symbol="AUDCAD",
        expected_timeframe="H4",
        expected_spread="10",
    )
    assert {chart.get("spread") for chart in wfm.findall(".//Setup/Chart")} == {"10"}
    _assert_wfm_crosschecks_contract(wfm)
    _assert_wfm_static_tabs_contract(wfm)

    retest1 = roots["Retest-Task1.xml"]
    retest1_setup = retest1.find(".//Data/Setups/Setup")
    assert retest1_setup.get("dateFrom") == "2010.01.01"
    assert retest1_setup.get("dateTo") == "2017.10.02"
    retest1_options = {
        node.get("key"): node.text
        for node in retest1.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"RealisticGapsHandling", "MarketOpenSession", "SignalTimeRangeFrom", "SignalTimeRangeTo"}
    }
    assert retest1_options == {
        "RealisticGapsHandling": "true",
        "MarketOpenSession": "No Session",
        "SignalTimeRangeFrom": "14400",
        "SignalTimeRangeTo": "72000",
    }
    retest1_rankings = retest1.find(".//Rankings")
    assert retest1_rankings.findtext("DeleteFailedStrategies") == "true"
    assert retest1_rankings.find("FitPortfolio").get("active") == "false"
    retest1_ranking_conditions = [
        (
            condition.find(".//Column-Value").get("column"),
            condition.find(".//Comparator").get("value"),
            condition.find(".//Numeric-Value").get("value"),
        )
        for condition in retest1_rankings.findall("./Conditions/Condition")
    ]
    assert retest1_ranking_conditions == [
        ("NumberOfTrades", ">=", "100"),
        ("RExpectancy", ">=", "0.05"),
        ("NetProfit", ">=", "0"),
    ]
    retest1_auto_dismissal = {
        problem.get("code"): problem.get("dismiss")
        for problem in retest1_rankings.findall("./AutomaticDismissal/Problem")
    }
    assert retest1_auto_dismissal["2"] == "false"
    retest1_symbols = retest1.findall(".//Resources/Symbols/Symbol")
    assert {node.get("name") for node in retest1_symbols} == {"AUDCAD_dukascopy"}
    assert {node.get("source") for node in retest1_symbols} == {"2"}
    assert {node.get("broker") for node in retest1_symbols} == {"3"}
    assert {node.find("InstrumentInfo").get("broker") for node in retest1_symbols} == {"3"}
    assert [broker.get("id") for broker in retest1.findall(".//Resources/Brokers/Broker")] == ["3"]
    _assert_retest1_passive_generation_contract(retest1)
    _assert_retest1_static_crosschecks_contract(retest1)

    forward = roots["Retest-Task2.xml"]
    _assert_foward_contract(
        forward,
        expected_symbol="AUDCAD",
        expected_timeframe="H4",
        expected_spread="10",
        expected_window=("14400", "72000"),
        expected_input_databank="WFM",
        expected_output_databank="Forward",
        expected_improve_databank="WFM",
        expected_delete_failed="false",
    )


def test_generate_capa1_project_applies_registered_forward_corr1_pipeline():
    mining = Mining(num=142, phase=1, asset="USDJPY", tf="H1", bs="BS_Volatilidad", dir="both")
    with tempfile.TemporaryDirectory() as tmp:
        out_path = generate_project(
            mining,
            str(TEMPLATE_DIR / "Capa1_Long.cfx"),
            tmp,
            capa=1,
            sqx_db_path=None,
            target_profile="sqxedge_darwinex",
        )
        roots = dict(_xml_roots(Path(out_path)))

    config = roots["config.xml"]
    tasks = {task.get("taskXMLFile"): task for task in config.findall(".//Task")}
    databanks = {
        databank.get("name"): databank.get("view")
        for databank in config.findall(".//Databank")
    }

    assert tasks["AutomaticRetest-Task5.xml"].get("title") == "Synthetic"
    assert tasks["Retest-Task2.xml"].get("title") == "Forward"
    assert tasks["Retest-Task4.xml"].get("title") == "CORR1 STABILITY RETEST"
    assert tasks["Retest-Task5.xml"].get("title") == "CORR1 TAG REVIEW"
    assert tasks["Retest-Task4.xml"].get("active") == "true"
    assert tasks["Retest-Task5.xml"].get("active") == "true"
    assert [task.get("taskXMLFile") for task in config.findall(".//Task")][-2:] == [
        "Retest-Task4.xml",
        "Retest-Task5.xml",
    ]

    assert "Synthetic" in databanks
    assert "Forward" in databanks
    legacy_databank_names = {"Syntetic", "Foward"}
    assert legacy_databank_names.isdisjoint(databanks)
    assert databanks["SQX EDGE CORR1 STABILITY"] == "SQX EDGE CORRELATION REVIEW"
    assert databanks["SQX EDGE CORR1 TAGGED"] == "SQX EDGE CORRELATION REVIEW"

    assert _task_databanks(roots["AutomaticRetest-Task5.xml"]) == {"Output": "Synthetic", "Input": "Monkey Test"}
    assert _task_databanks(roots["AutomaticRetest-Task7.xml"]) == {"Output": "SPP", "Input": "Synthetic"}
    assert _task_databanks(roots["AutomaticRetest-Task4.xml"]) == {"Output": "WFM", "Input": "SPP"}
    assert _task_databanks(roots["Retest-Task2.xml"]) == {"Output": "Forward", "Input": "WFM"}
    assert roots["Retest-Task2.xml"].find(".//WhatToBuild/StrategyType").get("improveDatabank") == "WFM"
    assert roots["Retest-Task2.xml"].find(".//CustomAnalysis").get("method") == "none"
    assert roots["Retest-Task2.xml"].find(".//DeleteFailedStrategies").text == "false"

    stability = roots["Retest-Task4.xml"]
    assert _task_databanks(stability) == {"Output": "SQX EDGE CORR1 STABILITY", "Input": "Forward"}
    stability_setup = stability.find(".//Data/Setups/Setup")
    assert stability_setup.get("dateFrom") == "2017.10.02"
    assert stability_setup.get("dateTo") == "2026.04.08"
    assert stability_setup.get("testPrecision") == C1_TICK_TEST_PRECISION
    assert [node.attrib for node in stability.findall(".//Data/OutOfSample/Range")] == [
        {"dateFrom": "2025.01.01", "dateTo": "2026.04.08"}
    ]
    assert stability.find(".//CustomAnalysis").get("method") == "none"
    assert stability.find(".//DeleteFailedStrategies").text == "false"
    assert stability.find(".//CrossChecks").get("use") == "false"

    tag_review = roots["Retest-Task5.xml"]
    assert _task_databanks(tag_review) == {
        "Output": "SQX EDGE CORR1 TAGGED",
        "Input": "SQX EDGE CORR1 STABILITY",
    }
    assert tag_review.find(".//Data/Setups/Setup").get("testPrecision") == C1_TICK_TEST_PRECISION
    assert tag_review.find(".//CustomAnalysis").get("method") == "SQXEdgeCorrelationTagger"
    assert tag_review.find(".//CustomAnalysis").get("filter") == "false"
    assert tag_review.find(".//DeleteFailedStrategies").text == "false"
    assert tag_review.find(".//CrossChecks").get("use") == "false"


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


def test_generate_project_preserves_direction_safe_custom_project_identity():
    mining = Mining(num=94, phase=1, asset="AUDCAD", tf="H1", bs="BS_Volatilidad", dir="both")
    project_name = "Project_AUDCAD_H1_BS_Volatilidad_v6_LS"
    with tempfile.TemporaryDirectory() as tmp:
        out_path = generate_project(
            mining,
            str(TEMPLATE_DIR / "Capa1_Long.cfx"),
            tmp,
            capa=1,
            project_name=project_name,
            sqx_db_path=None,
        )
        roots = dict(_xml_roots(Path(out_path)))

    assert Path(out_path).name == f"{project_name}_Capa1.cfx"
    assert roots["config.xml"].get("name") == f"{project_name}_Capa1"


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


def test_generate_capa2_project_applies_layer2_build_window_and_disables_heavy_retest_windows():
    mining = Mining(num=95, phase=2, asset="AUDCAD", tf="H4", bs="BS_Volatilidad", dir="long")
    with tempfile.TemporaryDirectory() as tmp:
        out_path = generate_project(
            mining,
            str(TEMPLATE_DIR / "Capa2_Base.cfx"),
            tmp,
            capa=2,
            sqx_db_path=None,
        )
        roots = dict(_xml_roots(Path(out_path)))

    _assert_generated_task_periods(roots, 2)
    _assert_automatic_retests_mark_date_ranges(roots)
    _assert_corr_review_task_contracts(roots, 2)
    config = roots["config.xml"]
    tick_task = next(task for task in config.findall(".//Task") if task.get("taskXMLFile") == "AutomaticRetest-Task2.xml")
    config_databanks = {databank.get("name") for databank in config.findall(".//Databank")}
    assert tick_task.get("title") == "TICK REAL"
    assert _config_absolute_path_attrs(config) == []
    assert "TICK" in config_databanks
    assert "HBP" not in config_databanks
    task_files = [task.get("taskXMLFile") for task in config.findall(".//Task")]
    assert len(task_files) == 14
    assert task_files[-2:] == ["Retest-Task3.xml", "Retest-Task4.xml"]
    tasks = {task.get("taskXMLFile"): task for task in config.findall(".//Task")}
    assert tasks["Retest-Task3.xml"].get("title") == "C2 CORR STABILITY RETEST"
    assert tasks["Retest-Task4.xml"].get("title") == "C2 CORR TAG REVIEW"
    config_databank_views = {
        databank.get("name"): databank.get("view")
        for databank in config.findall(".//Databank")
    }
    assert config_databank_views["Forward"] == "SQX EDGE C2 CORRELATION REVIEW"
    assert config_databank_views["SQX EDGE C2 CORR STABILITY"] == "SQX EDGE C2 CORRELATION REVIEW"
    assert config_databank_views["SQX EDGE C2 CORR TAGGED"] == "SQX EDGE C2 CORRELATION REVIEW"

    build = roots["Build-Task1.xml"]
    build_params = {
        node.get("key"): node.text
        for node in build.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"LimitTimeRange", "SignalTimeRangeFrom", "SignalTimeRangeTo", "RealisticGapsHandling", "StoreChartData"}
    }
    assert build_params == {
        "LimitTimeRange": "true",
        "SignalTimeRangeFrom": "14400",
        "SignalTimeRangeTo": "72000",
        "RealisticGapsHandling": "true",
        "StoreChartData": "false",
    }
    assert build.find(".//ExitTypes/Block[@key='ExitAfterBars.ExitAfterBars']").get("use") == "false"

    retest0 = roots["Retest-Task1.xml"]
    retest0_setup = retest0.find(".//Data/Setups/Setup")
    assert retest0_setup.get("dateFrom") == "2017.10.02"
    assert retest0_setup.get("dateTo") == "2025.01.01"
    assert [dict(node.attrib) for node in retest0.findall(".//Data/OutOfSample/Range")] == [
        {"dateFrom": "2023.01.01", "dateTo": "2025.01.01"}
    ]
    assert retest0.find(".//CrossChecks").get("use") == "false"
    assert retest0.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "Results"
    assert retest0.find(".//ExitTypes/Block[@key='ExitAfterBars.ExitAfterBars']").get("use") == "false"

    retest1 = roots["AutomaticRetest-Task7.xml"]
    assert retest1.find("./Data") is None
    retest1_setup = retest1.find("./CustomData/Setups/Setup")
    assert retest1_setup is not None
    assert retest1_setup.get("dateFrom") == "2010.01.01"
    assert retest1_setup.get("dateTo") == "2017.10.02"
    assert retest1_setup.find("Chart").get("symbol") == "AUDCAD_dukascopy"
    assert retest1_setup.find("Chart").get("timeframe") == "H4"
    assert retest1.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "RETEST 0"
    assert retest1.find(".//CrossChecks").get("use") == "false"
    retest1_exit_after_bars = retest1.find(".//ExitTypes/Block[@key='ExitAfterBars.ExitAfterBars']")
    assert retest1_exit_after_bars is None or retest1_exit_after_bars.get("use") == "false"
    retest1_symbols = retest1.findall(".//Resources/Symbols/Symbol")
    assert {node.get("name") for node in retest1_symbols} == {"AUDCAD_dukascopy"}
    assert {node.get("source") for node in retest1_symbols} == {"2"}
    assert {node.get("broker") for node in retest1_symbols} == {"3"}
    assert [broker.get("id") for broker in retest1.findall(".//Resources/Brokers/Broker")] == ["3"]
    retest1_params = {
        node.get("key"): node.text
        for node in retest1.findall(".//BuildTradingOptions/Params/Param")
        if node.get("key") in {"LimitTimeRange", "SignalTimeRangeFrom", "SignalTimeRangeTo"}
    }
    assert retest1_params == {
        "LimitTimeRange": "true",
        "SignalTimeRangeFrom": "14400",
        "SignalTimeRangeTo": "72000",
    }

    tick_real = roots["AutomaticRetest-Task2.xml"]
    _assert_tick_real_data_databanks_resources_contract(
        tick_real,
        expected_symbol="AUDCAD",
        expected_timeframe="H4",
    )
    tick_symbols = tick_real.findall(".//Resources/Symbols/Symbol")
    assert {node.get("name") for node in tick_symbols} == {"AUDCAD"}
    assert {node.get("source") for node in tick_symbols} == {"0"}
    assert {node.get("broker") for node in tick_symbols} == {"-1"}
    assert "dukascopy" not in ET.tostring(tick_real, encoding="unicode").lower()
    _assert_tick_real_options_rankings_contract(tick_real, expected_window=("7200", "79200"))
    _assert_tick_real_passive_generation_contract(
        tick_real,
        expected_exit_after_bars="false",
        expected_enabled_exits={
            "StopLoss.StopLoss",
            "ProfitTarget.ProfitTarget",
            "TrailingStop.TrailingStop",
            "TrailingStop.TrailingActivation",
        },
        expected_blocks_version=None,
        expect_no_signal_or_stoplimit_blocks=False,
    )
    _assert_tick_real_static_crosschecks_contract(tick_real)

    mc = roots["AutomaticRetest-Task1.xml"]
    _assert_capa2_mc_contract(
        mc,
        expected_symbol="AUDCAD",
        expected_timeframe="H4",
        expected_source="0",
        expected_broker="-1",
    )
    assert "dukascopy" not in ET.tostring(mc, encoding="unicode").lower()

    mc2 = roots["AutomaticRetest-Task8.xml"]
    _assert_capa2_mc2_contract(
        mc2,
        expected_symbol="AUDCAD",
        expected_timeframe="H4",
        expected_source="0",
        expected_broker="-1",
        expected_spread="10",
        expected_spread_min="20",
        expected_spread_max="50",
    )
    assert "dukascopy" not in ET.tostring(mc2, encoding="unicode").lower()

    sequential = roots["AutomaticRetest-Task3.xml"]
    _assert_capa2_sequential_contract(
        sequential,
        expected_symbol="AUDCAD",
        expected_timeframe="H4",
        expected_source="0",
        expected_broker="-1",
        expected_spread="10",
    )
    assert "dukascopy" not in ET.tostring(sequential, encoding="unicode").lower()

    monkey = roots["AutomaticRetest-Task6.xml"]
    _assert_capa2_monkey_contract(
        monkey,
        expected_symbol="AUDCAD",
        expected_timeframe="H4",
        expected_source="0",
        expected_broker="-1",
        expected_spread="10",
    )
    assert "dukascopy" not in ET.tostring(monkey, encoding="unicode").lower()

    synthetic = roots["AutomaticRetest-Task5.xml"]
    _assert_capa2_synthetic_contract(
        synthetic,
        expected_symbol="AUDCAD",
        expected_timeframe="H4",
        expected_source="0",
        expected_broker="-1",
        expected_spread="10",
    )
    assert "dukascopy" not in ET.tostring(synthetic, encoding="unicode").lower()

    spp = roots["AutomaticRetest-Task4.xml"]
    _assert_capa2_spp_contract(
        spp,
        expected_symbol="AUDCAD",
        expected_timeframe="H4",
        expected_source="0",
        expected_broker="-1",
        expected_spread="10",
    )
    assert "dukascopy" not in ET.tostring(spp, encoding="unicode").lower()

    wfm = roots["Optimize-Task1.xml"]
    _assert_capa2_wfm_contract(
        wfm,
        expected_symbol="AUDCAD",
        expected_timeframe="H4",
        expected_source="0",
        expected_broker="-1",
        expected_spread="10",
    )
    assert "dukascopy" not in ET.tostring(wfm, encoding="unicode").lower()

    forward = roots["Retest-Task2.xml"]
    _assert_capa2_forward_contract(
        forward,
        expected_symbol="AUDCAD",
        expected_timeframe="H4",
        expected_source="0",
        expected_broker="-1",
        expected_spread="10",
        expected_window=("14400", "72000"),
    )
    assert "dukascopy" not in ET.tostring(forward, encoding="unicode").lower()

    corr_stability = roots["Retest-Task3.xml"]
    assert _task_databanks(corr_stability) == {
        "Output": "SQX EDGE C2 CORR STABILITY",
        "Input": "Forward",
    }
    corr_stability_setup = corr_stability.find(".//Data/Setups/Setup")
    assert corr_stability_setup.get("dateFrom") == "2017.10.02"
    assert corr_stability_setup.get("dateTo") == "2026.04.08"
    assert corr_stability_setup.get("testPrecision") == C1_TICK_TEST_PRECISION
    assert [node.attrib for node in corr_stability.findall(".//Data/OutOfSample/Range")] == [
        {"dateFrom": "2025.01.01", "dateTo": "2026.01.01"},
        {"dateFrom": "2026.01.01", "dateTo": "2026.04.08"},
    ]
    assert corr_stability.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "WFM"
    assert corr_stability.find(".//CustomAnalysis").get("method") == "none"
    assert corr_stability.find(".//DeleteFailedStrategies").text == "false"
    assert corr_stability.find(".//CrossChecks").get("use") == "false"

    corr_tag = roots["Retest-Task4.xml"]
    assert _task_databanks(corr_tag) == {
        "Output": "SQX EDGE C2 CORR TAGGED",
        "Input": "SQX EDGE C2 CORR STABILITY",
    }
    assert corr_tag.find(".//Data/Setups/Setup").get("testPrecision") == C1_TICK_TEST_PRECISION
    assert corr_tag.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "WFM"
    assert corr_tag.find(".//CustomAnalysis").get("method") == "SQXEdgeCorrelationTagger"
    assert corr_tag.find(".//CustomAnalysis").get("filter") == "false"
    assert corr_tag.find(".//DeleteFailedStrategies").text == "false"
    assert corr_tag.find(".//CrossChecks").get("use") == "false"


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


def test_sqxedge_darwinex_target_uses_hybrid_oos2_without_local_db():
    mining = Mining(num=97, phase=1, asset="AUDCAD", tf="H1", bs="BS_Tendencia", dir="both")
    with tempfile.TemporaryDirectory() as tmp:
        out_path = generate_project(
            mining,
            str(TEMPLATE_DIR / "Capa1_Long.cfx"),
            tmp,
            capa=1,
            sqx_db_path=None,
            target_profile="sqxedge_darwinex",
        )
        roots = dict(_xml_roots(Path(out_path)))
        report = audit_cfx_compatibility(out_path)

    build = roots["Build-Task1.xml"]
    build_symbol = build.find(".//Resources/Symbols/Symbol")
    assert build_symbol.get("name") == "AUDCAD_darwinex"
    assert build_symbol.get("source") == "4"
    assert build_symbol.get("broker") == "4"
    assert build_symbol.find("InstrumentInfo").get("instrument") == "AUDCAD_darwinex"

    retest1 = roots["Retest-Task1.xml"]
    retest1_chart = retest1.find(".//Data/Setups/Setup/Chart")
    retest1_symbol = retest1.find(".//Resources/Symbols/Symbol")
    retest1_info = retest1_symbol.find("InstrumentInfo")
    assert retest1_chart.get("symbol") == "AUDCAD_dukascopy"
    assert retest1_symbol.get("name") == "AUDCAD_dukascopy"
    assert retest1_symbol.get("source") == "2"
    assert retest1_symbol.get("broker") == "4"
    assert retest1_info.get("instrument") == "AUDCAD_darwinex"
    assert retest1_info.get("broker") == "4"
    assert [broker.get("id") for broker in retest1.findall(".//Resources/Brokers/Broker")] == ["4"]
    assert [broker.get("postfix") for broker in retest1.findall(".//Resources/Brokers/Broker")] == ["_darwinex"]
    assert report["hostProfile"] == "sqx_edge_cross_broker_oos2"
    assert report["failCount"] == 0
    assert all(root.findall(".//Resources/CustomBlocks/*") == [] for root in roots.values())
    assert all(root.findall(".//Resources/Instruments/InstrumentInfo") == [] for root in roots.values())


def test_capa2_sqxedge_darwinex_target_uses_hybrid_oos2_without_local_db():
    mining = Mining(num=98, phase=2, asset="AUDCAD", tf="H4", bs="BS_Tendencia", dir="long")
    with tempfile.TemporaryDirectory() as tmp:
        out_path = generate_project(
            mining,
            str(TEMPLATE_DIR / "Capa2_Base.cfx"),
            tmp,
            capa=2,
            sqx_db_path=None,
            target_profile="sqxedge_darwinex",
        )
        roots = dict(_xml_roots(Path(out_path)))

    retest1 = roots["AutomaticRetest-Task7.xml"]
    retest1_chart = retest1.find(".//CustomData/Setups/Setup/Chart")
    retest1_symbol = retest1.find(".//Resources/Symbols/Symbol")
    retest1_info = retest1_symbol.find("InstrumentInfo")
    assert retest1_chart.get("symbol") == "AUDCAD_dukascopy"
    assert retest1_symbol.get("name") == "AUDCAD_dukascopy"
    assert retest1_symbol.get("source") == "2"
    assert retest1_symbol.get("broker") == "4"
    assert retest1_info.get("instrument") == "AUDCAD_darwinex"
    assert retest1_info.get("broker") == "4"
    assert [broker.get("id") for broker in retest1.findall(".//Resources/Brokers/Broker")] == ["4"]
    assert all(root.findall(".//Resources/CustomBlocks/*") == [] for root in roots.values())
    assert all(root.findall(".//Resources/Instruments/InstrumentInfo") == [] for root in roots.values())


def test_patch_custom_block_resources_strips_packaged_donor_blocks():
    root = ET.fromstring(
        """
        <Task>
          <Resources>
            <CustomBlocks>
              <CustomBlock name="Legacy Block A" />
              <CustomBlock name="Legacy Block B" />
            </CustomBlocks>
          </Resources>
        </Task>
        """
    )

    assert patch_custom_block_resources(root, strip=True) == 2
    custom_blocks = root.find(".//Resources/CustomBlocks")
    assert custom_blocks is not None
    assert list(custom_blocks) == []
    assert custom_blocks.text is None


def test_sq_default_target_keeps_packaged_custom_blocks_for_external_hosts():
    mining = Mining(num=99, phase=1, asset="AUDCAD", tf="H1", bs="BS_Tendencia", dir="both")
    with tempfile.TemporaryDirectory() as tmp:
        out_path = generate_project(
            mining,
            str(TEMPLATE_DIR / "Capa1_Long.cfx"),
            tmp,
            capa=1,
            sqx_db_path=None,
            target_profile="sq_default_exact",
        )
        roots = dict(_xml_roots(Path(out_path)))

    packaged = sum(len(root.findall(".//Resources/CustomBlocks/*")) for root in roots.values())
    assert packaged > 0


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


def test_cross_broker_retest_period_is_bounded_to_available_local_data():
    period = _bound_retest_period_to_available_data(
        ("2010.01.01", "2017.10.02"),
        {
            "source": "db",
            "symbol": "XAUUSD_dukascopy",
            "data_available": True,
            "date_from_ms": "1388624402064",
            "date_to_ms": "1776049199924",
        },
        min_coverage_days=730,
    )

    assert period == ("2014.01.02", "2017.10.02")


def test_capa1_retest1_uses_dukascopy_bars_with_darwinex_execution_contract():
    mining = Mining(num=96, phase=1, asset="XAUUSD", tf="H1", bs="BS_SoporteResistencia", dir="long")
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "data.db"
        _create_hybrid_xau_data_db(db_path)
        out_path = generate_project(
            mining,
            str(TEMPLATE_DIR / "Capa1_Long.cfx"),
            tmp,
            capa=1,
            sqx_db_path=str(db_path),
        )
        roots = dict(_xml_roots(Path(out_path)))

    retest1 = roots["Retest-Task1.xml"]
    setup = retest1.find(".//Data/Setups/Setup")
    assert setup is not None
    assert setup.get("dateFrom") == "2010.01.01"
    assert setup.get("dateTo") == "2017.10.02"
    assert setup.get("testPrecision") == "2"
    chart = setup.find("Chart")
    assert chart is not None
    assert chart.get("symbol") == "XAUUSD_dukascopy"
    assert chart.get("spread") == "30.0"
    assert setup.find("Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']").text == "6.0"
    swap = setup.find("Swap")
    assert swap is not None
    assert swap.get("type") == "money"
    assert swap.get("long") == "-65.0"
    assert swap.get("short") == "45.0"

    symbol = retest1.find(".//Resources/Symbols/Symbol")
    assert symbol is not None
    info = symbol.find("InstrumentInfo")
    assert info is not None
    assert symbol.get("name") == "XAUUSD_dukascopy"
    assert symbol.get("source") == "2"
    assert symbol.get("broker") == "4"
    assert info.get("instrument") == "XAUUSD_darwinex"
    assert info.get("broker") == "4"
    assert info.get("tickSize") == "0.01"
    assert info.get("tickStep") == "0.01"
    assert info.get("defaultSpread") == "30.0"
    assert info.get("defaultSlippage") == "0.0"
    assert info.get("decimals") == "2"
    assert info.get("dataType") == "4"
    broker = retest1.find(".//Resources/Brokers/Broker")
    assert broker is not None
    assert broker.get("id") == "4"
    assert broker.get("postfix") == "_darwinex"


def test_cross_broker_retest_period_rejects_too_short_local_data():
    try:
        _bound_retest_period_to_available_data(
            ("2010.01.01", "2017.10.02"),
            {
                "source": "db",
                "symbol": "XAUUSD_dukascopy",
                "data_available": True,
                "date_from_ms": "1483228800000",
                "date_to_ms": "1506902400000",
            },
            min_coverage_days=730,
        )
    except ValueError as exc:
        assert "below minimum" in str(exc)
    else:
        raise AssertionError("Expected short cross-broker data coverage to be rejected")


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
