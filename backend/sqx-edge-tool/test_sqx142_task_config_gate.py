import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from tools import sqx142_task_config_gate as gate
from tools.sqx142_task_config_gate import (
    apply_mc_data_databanks_resources_options_to_root,
    apply_mc_crosschecks_to_root,
    apply_mc_passive_generation_to_root,
    apply_mc_static_tabs_to_root,
    apply_mc2_data_databanks_resources_options_to_root,
    apply_mc2_crosschecks_to_root,
    apply_mc2_passive_generation_to_root,
    apply_mc2_static_tabs_to_root,
    apply_monkey_crosschecks_to_root,
    apply_monkey_data_databanks_resources_options_to_root,
    apply_monkey_passive_generation_to_root,
    apply_monkey_static_tabs_to_root,
    apply_synthetic_crosschecks_to_root,
    apply_synthetic_data_databanks_resources_options_to_root,
    apply_synthetic_passive_generation_to_root,
    apply_synthetic_static_tabs_to_root,
    apply_spp_data_databanks_resources_options_to_root,
    apply_spp_crosschecks_to_root,
    apply_spp_static_tabs_to_root,
    apply_sequential_data_databanks_resources_options_to_root,
    apply_sequential_crosschecks_to_root,
    apply_sequential_passive_generation_to_root,
    apply_sequential_static_tabs_to_root,
    apply_wfm_data_databanks_resources_options_to_root,
    apply_wfm_crosschecks_to_root,
    apply_wfm_static_tabs_to_root,
    apply_foward_data_databanks_resources_options_to_root,
    apply_foward_crosschecks_to_root,
    apply_foward_static_tabs_to_root,
    apply_retest1_passive_generation_to_root,
    apply_retest1_data_resources_to_root,
    apply_retest1_options_databanks_rankings_to_root,
    apply_retest1_static_crosschecks_to_root,
    apply_tick_real_data_databanks_resources_to_root,
    apply_tick_real_options_rankings_to_root,
    apply_tick_real_passive_generation_to_root,
    apply_tick_real_static_crosschecks_to_root,
    enforce_retest1_data_resources_guard,
    enforce_retest1_options_databanks_rankings_guard,
    enforce_retest1_passive_generation_guard,
    enforce_retest1_static_crosschecks_guard,
    enforce_mc_data_databanks_resources_options_guard,
    enforce_mc_crosschecks_guard,
    enforce_mc_passive_generation_guard,
    enforce_mc_static_tabs_guard,
    enforce_mc2_data_databanks_resources_options_guard,
    enforce_mc2_crosschecks_guard,
    enforce_mc2_passive_generation_guard,
    enforce_mc2_static_tabs_guard,
    enforce_monkey_crosschecks_guard,
    enforce_monkey_data_databanks_resources_options_guard,
    enforce_monkey_passive_generation_guard,
    enforce_monkey_static_tabs_guard,
    enforce_synthetic_crosschecks_guard,
    enforce_synthetic_data_databanks_resources_options_guard,
    enforce_synthetic_passive_generation_guard,
    enforce_synthetic_static_tabs_guard,
    enforce_spp_data_databanks_resources_options_guard,
    enforce_spp_crosschecks_guard,
    enforce_spp_static_tabs_guard,
    enforce_sequential_data_databanks_resources_options_guard,
    enforce_sequential_crosschecks_guard,
    enforce_sequential_passive_generation_guard,
    enforce_sequential_static_tabs_guard,
    enforce_wfm_data_databanks_resources_options_guard,
    enforce_wfm_crosschecks_guard,
    enforce_wfm_static_tabs_guard,
    enforce_foward_data_databanks_resources_options_guard,
    enforce_foward_crosschecks_guard,
    enforce_foward_static_tabs_guard,
    enforce_tick_real_data_databanks_resources_guard,
    enforce_tick_real_options_rankings_guard,
    enforce_tick_real_passive_generation_guard,
    enforce_tick_real_static_crosschecks_guard,
    fallback_retest1_oos2_resource,
    mc_closeout_operation_issues,
    mc_closeout_operation_summary,
    monkey_open_issues,
    monkey_open_summary,
    monkey_crosschecks_summary,
    question_id,
    record_tab_answer,
    sequential_open_issues,
    sequential_open_summary,
    sequential_crosschecks_summary,
)


def test_question_id_keeps_long_repeated_crosscheck_paths_unique():
    prefix = (
        "RETEST 0-CrossChecks-CrossChecks_WalkForwardOptimization_"
        "AcceptanceSettings_Conditions_Condition_Left-Side_Column"
    )
    paths = [f"{prefix}#{index}" for index in range(1, 10)]
    ids = [question_id(path) for path in paths]

    assert len(ids) == len(set(ids))
    assert all(len(item) <= 120 for item in ids)


def test_record_tab_answer_records_all_questions_from_latest_questionnaire(tmp_path):
    questionnaire_dir = (
        tmp_path
        / ".local"
        / "sqx142_task_config"
        / "questionnaires"
        / "capa1"
        / "RETEST_0"
    )
    questionnaire_dir.mkdir(parents=True)
    older = questionnaire_dir / "Blocks_20260101_000000.json"
    latest = questionnaire_dir / "Blocks_20260101_000001.json"
    older.write_text(json.dumps({"questions": [{"id": "old"}]}), encoding="utf-8")
    latest.write_text(
        json.dumps({"questions": [{"id": "q1"}, {"id": "q2"}]}),
        encoding="utf-8",
    )

    result = record_tab_answer(
        tmp_path,
        task_title_wanted="RETEST 0",
        tab="Blocks",
        answer="keep_base",
        note="confirmed",
        allow_empty=False,
    )

    assert result["ok"] is True
    assert result["answerCount"] == 2
    payload = json.loads((tmp_path / ".local" / "sqx142_task_config" / "answers" / "capa1" / "RETEST_0" / "Blocks.json").read_text(encoding="utf-8"))
    assert payload["bulkAnswer"] is True
    assert set(payload["answers"]) == {"q1", "q2"}


def test_record_tab_answer_refuses_duplicate_question_ids(tmp_path):
    questionnaire_dir = (
        tmp_path
        / ".local"
        / "sqx142_task_config"
        / "questionnaires"
        / "capa1"
        / "RETEST_0"
    )
    questionnaire_dir.mkdir(parents=True)
    (questionnaire_dir / "CrossChecks_20260101_000000.json").write_text(
        json.dumps({"questions": [{"id": "same"}, {"id": "same"}]}),
        encoding="utf-8",
    )

    result = record_tab_answer(
        tmp_path,
        task_title_wanted="RETEST 0",
        tab="CrossChecks",
        answer="keep_base",
        note="confirmed",
        allow_empty=False,
    )

    assert result["ok"] is False
    assert result["error"] == "duplicate_question_ids"


def test_retest1_data_resources_target_is_protected_dukascopy_oos2():
    root = ET.fromstring(
        """
        <Task>
          <Data>
            <Setups>
              <Setup dateFrom="2017.10.02" dateTo="2025.01.01" testPrecision="1" session="Old Session" slippage="0" minDist="0" engine="MetaTrader5 (hedged)">
                <Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2" />
                <Commissions>
                  <Method type="PercentageBased" use="true"><Params><Param key="CommissionPct">0.005</Param></Params></Method>
                </Commissions>
                <Swap use="true" type="points" long="-0.5" short="-6.3" tripleSwapOn="WEDNESDAY" rolloutHour="23:00" />
              </Setup>
            </Setups>
            <OutOfSample showGraph="true"><Range dateFrom="2023.01.01" dateTo="2025.01.01" /></OutOfSample>
          </Data>
          <Resources>
            <Symbols><Symbol name="AUDCAD_darwinex" source="4" broker="4" /></Symbols>
            <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
            <Instruments />
            <Sessions><Session name="Old" /></Sessions>
            <CustomIndicators />
            <CustomBlocks><Block name="legacy" /></CustomBlocks>
          </Resources>
        </Task>
        """
    )

    actions = apply_retest1_data_resources_to_root(root, fallback_retest1_oos2_resource())

    assert any(item["field"] == "Resources" and item["changed"] for item in actions)
    assert enforce_retest1_data_resources_guard(root) == []
    setup = root.find(".//Data/Setups/Setup")
    assert setup.get("dateFrom") == "2010.01.01"
    assert setup.get("dateTo") == "2017.10.02"
    assert setup.get("testPrecision") == "2"
    chart = setup.find("Chart")
    assert chart.get("symbol") == "AUDCAD_dukascopy"
    assert chart.get("spread") == "1.9"
    assert root.findall(".//Data/OutOfSample/Range") == []
    symbol = root.find(".//Resources/Symbols/Symbol")
    assert symbol.get("source") == "2"
    assert symbol.get("broker") == "3"
    assert symbol.find("InstrumentInfo").get("broker") == "3"
    assert [broker.get("id") for broker in root.findall(".//Resources/Brokers/Broker")] == ["3"]
    assert root.findall(".//Resources/CustomBlocks/*") == []


def test_retest1_options_databanks_rankings_are_advisory_not_coladero():
    root = ET.fromstring(
        """
        <Task>
          <Options>
            <BuildTradingOptions>
              <Params>
                <Param key="Session">No Session</Param>
                <Param key="MarketOpenSession">USDJPY_darwinex</Param>
                <Param key="LimitTimeRange">false</Param>
                <Param key="SignalTimeRangeFrom">14400</Param>
                <Param key="SignalTimeRangeTo">72000</Param>
                <Param key="RealisticGapsHandling">false</Param>
                <Param key="StoreChartData">true</Param>
              </Params>
            </BuildTradingOptions>
          </Options>
          <Databanks>
            <Databank label="Output databank" name="Output" value="bad" />
            <Databank label="Input databank" name="Input" value="Results" />
          </Databanks>
          <Rankings type="always">
            <MaxStrategies>500</MaxStrategies>
            <ConditionsType>0</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Existing portfolio" />
            <StopCondition type="passed" passedStrategies="10" restartCount="1" days="1" hours="1" minutes="1" />
            <Conditions />
          </Rankings>
        </Task>
        """
    )

    actions = apply_retest1_options_databanks_rankings_to_root(root)

    assert any(item["field"] == "Rankings/DeleteFailedStrategies" and item["changed"] for item in actions)
    assert enforce_retest1_options_databanks_rankings_guard(root) == []
    params = {
        node.get("key"): node.text
        for node in root.findall(".//BuildTradingOptions/Params/Param")
    }
    assert params["MarketOpenSession"] == "No Session"
    assert params["RealisticGapsHandling"] == "true"
    assert params["SignalTimeRangeFrom"] == "7200"
    assert params["SignalTimeRangeTo"] == "79200"
    assert {node.get("name"): node.get("value") for node in root.findall(".//Databanks/Databank")} == {
        "Output": "retest 1",
        "Input": "RETEST 0",
    }
    assert root.find(".//Rankings/DeleteFailedStrategies").text == "false"
    assert root.find(".//Rankings/FitPortfolio").get("active") == "false"
    conditions = root.findall(".//Rankings/Conditions/Condition")
    assert [item.find(".//Column-Value").get("column") for item in conditions] == [
        "NumberOfTrades",
        "RExpectancy",
        "NetProfit",
    ]


def test_retest1_passive_generation_disables_improve_and_generation_remnants():
    root = ET.fromstring(
        """
        <Task>
          <PartsToImprove improveATM="true">
            <EntryRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></EntryRules>
            <OrderTypes><LongImprovement use="true" /><ShortImprovement use="true" /></OrderTypes>
            <ExitRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" stale="true" />
            <MarketSides type="long" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>true</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="true" />
              <EvoRestartOnStagnation status="true" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple">
            <BuildingBlocks>
              <Block key="Signals.ADX" category="signals" use="true" probability="1" />
              <Block key="Indicators.ATR" category="indicators" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="true" probability="1" />
            </BuildingBlocks>
            <OrderTypes>
              <Block key="EnterAtMarket" use="false" probability="1" />
              <Block key="EnterReverseAtMarket" use="true" probability="1" />
              <Block key="EnterAtStop" use="true" probability="1" />
              <Block key="EnterAtLimit" use="true" probability="1" />
            </OrderTypes>
            <ExitTypes>
              <Block key="ExitAfterBars.ExitAfterBars" use="false" probability="50" />
              <Block key="ExitAfterDays.ExitAfterDays" use="true" probability="50" />
              <Block key="StopLoss.StopLoss" use="true" probability="50" />
            </ExitTypes>
            <CustomData showAll="true"><Item key="legacy" /></CustomData>
          </Blocks>
        </Task>
        """
    )
    source_root = ET.fromstring(
        """
        <Task>
          <Blocks type="simple" version="142.2336">
            <BuildingBlocks>
              <Block key="Signals.ADX" category="signals" use="false" probability="1" />
              <Block key="Indicators.ATR" category="indicators" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="false" probability="1" />
            </BuildingBlocks>
            <OrderTypes>
              <Block key="EnterAtMarket" use="true" probability="1" />
              <Block key="EnterReverseAtMarket" use="false" probability="1" />
              <Block key="EnterAtStop" use="false" probability="1" />
              <Block key="EnterAtLimit" use="false" probability="1" />
            </OrderTypes>
            <ExitTypes>
              <Block key="ExitAfterBars.ExitAfterBars" use="true" probability="100" />
              <Block key="StopLoss.StopLoss" use="false" probability="50" />
            </ExitTypes>
            <CustomData showAll="false" />
          </Blocks>
        </Task>
        """
    )

    actions = apply_retest1_passive_generation_to_root(root, source_root)

    assert any(item["field"] == "BuildingBlocks" and item["changed"] for item in actions)
    assert enforce_retest1_passive_generation_guard(root) == []
    assert root.find(".//PartsToImprove/ExitRules/LongImprovement").get("use") == "false"
    assert root.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "RETEST 0"
    assert root.find(".//WhatToBuild/StrategyType").get("stale") is None
    assert root.find(".//BuildMode/ShowLastGenerationDatabank").text == "false"
    assert root.find(".//BuildMode/EvoRestartOnFinish").get("status") == "false"
    assert root.find(".//Blocks").get("version") == "142.2336"
    assert root.findall(".//ExitTypes/Block[@key='ExitAfterDays.ExitAfterDays']") == []
    assert root.find(".//BuildingBlocks/Block[@key='Indicators.ATR']").get("use") == "true"
    assert root.find(".//BuildingBlocks/Block[@key='Signals.ADX']").get("use") == "false"


def test_retest1_static_crosschecks_target_turns_off_checks_and_uses_fixed_size():
    root = ET.fromstring(
        """
        <Task>
          <PartsToImprove improveATM="false">
            <EntryRules symmetry="false"><LongImprovement use="false" action="replace" /><ShortImprovement use="false" action="replace" /></EntryRules>
            <OrderTypes><LongImprovement use="false" /><ShortImprovement use="false" /></OrderTypes>
            <ExitRules symmetry="false"><LongImprovement use="false" action="replace" /><ShortImprovement use="false" action="replace" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="RETEST 0" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>false</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>false</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>false</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="false" />
              <EvoRestartOnStagnation status="false" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple" version="142.2336">
            <BuildingBlocks><Block key="Indicators.ATR" category="indicators" use="true" probability="1" /></BuildingBlocks>
            <OrderTypes>
              <Block key="EnterAtMarket" use="true" probability="1" />
              <Block key="EnterReverseAtMarket" use="false" probability="1" />
              <Block key="EnterAtStop" use="false" probability="1" />
              <Block key="EnterAtLimit" use="false" probability="1" />
            </OrderTypes>
            <ExitTypes>
              <Block key="ExitAfterBars.ExitAfterBars" use="true" probability="100" />
              <Block key="StopLoss.StopLoss" use="false" probability="50" />
            </ExitTypes>
            <CustomData showAll="false" />
          </Blocks>
          <CrossChecks use="true" evaluateAll="true">
            <MonteCarloRetest use="true"><Settings><Methods><Method type="RandomizeSpread" use="true" /></Methods></Settings></MonteCarloRetest>
            <WalkForwardOptimization use="false" />
          </CrossChecks>
          <RiskMoneyManagement customSettings="false">
            <MoneyManagement>
              <Method type="FixedSize" use="false" />
              <Method type="RiskFixedBalancePct" use="false" />
              <Method type="RiskFixedPctOfAccount" use="false" />
              <Method type="FixedAmount" use="true" />
              <Method type="StocksSizeByPrice" use="false" />
            </MoneyManagement>
          </RiskMoneyManagement>
          <ATMs enable="false" />
          <Notes>ok</Notes>
          <SelectedStrategies />
          <Rankings><ForceRunCrossChecks>false</ForceRunCrossChecks></Rankings>
        </Task>
        """
    )

    actions = apply_retest1_static_crosschecks_to_root(root)

    assert any(item["field"] == "CrossChecks:attrs" and item["changed"] for item in actions)
    assert any(item["field"] == "RiskMoneyManagement/Method:FixedSize" and item["changed"] for item in actions)
    assert enforce_retest1_static_crosschecks_guard(root) == []
    assert root.find(".//CrossChecks").get("use") == "false"
    assert root.find(".//CrossChecks/MonteCarloRetest").get("use") == "false"
    assert root.find(".//CrossChecks/MonteCarloRetest/Settings/Methods/Method").get("use") == "false"
    assert root.find(".//RiskMoneyManagement//Method[@type='FixedSize']").get("use") == "true"
    assert root.find(".//RiskMoneyManagement//Method[@type='FixedAmount']").get("use") == "false"


def test_tick_real_data_databanks_resources_chain_after_retest1_preserves_generic_resources():
    root = ET.fromstring(
        """
        <Task>
          <Data>
            <Setups>
              <Setup dateFrom="2010.01.01" dateTo="2026.04.08" testPrecision="1" session="Old Session" slippage="0" minDist="0" engine="MetaTrader5 (hedged)">
                <Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2" />
              </Setup>
            </Setups>
            <OutOfSample showGraph="true"><Range dateFrom="2020.01.01" dateTo="2021.01.01" /></OutOfSample>
          </Data>
          <Databanks retestSelected="false">
            <Databank label="Output databank" name="Output" value="retest 1" />
            <Databank label="Input databank" name="Input" value="RETEST 0" />
          </Databanks>
          <Resources>
            <Symbols>
              <Symbol name="AUDCAD_darwinex" source="4" barType="1" precision="M1" timezone="EETUS" dateFrom="1506902400000" dateTo="1775606400000" uSymbol="AUDCAD" uSymbolName="AUDCAD" removeWeekends="false" broker="4">
                <InstrumentInfo instrument="AUDCAD_darwinex" defaultSpread="1" dataType="3" broker="4" />
              </Symbol>
            </Symbols>
            <Brokers><Broker id="4" name="[[Darwinex]]" description="Darwinex CFDs" timezone="EETUS" postfix="_darwinex" mtUse="true" spUse="false" /></Brokers>
            <Instruments><InstrumentInfo instrument="AUDCAD_darwinex" defaultSpread="1" dataType="3" broker="4" /></Instruments>
            <Sessions><Session name="Old" /></Sessions>
            <CustomIndicators />
            <CustomBlocks><Item key="keep_me" /></CustomBlocks>
          </Resources>
        </Task>
        """
    )

    actions = apply_tick_real_data_databanks_resources_to_root(root)

    assert any(item["field"] == "Databanks/Input" and item["changed"] for item in actions)
    assert enforce_tick_real_data_databanks_resources_guard(root) == []
    setup = root.find(".//Data/Setups/Setup")
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == "2"
    assert root.findall(".//Data/OutOfSample/Range") == []
    assert {node.get("name"): node.get("value") for node in root.findall(".//Databanks/Databank")} == {
        "Output": "TICK",
        "Input": "retest 1",
    }
    symbol = root.find(".//Resources/Symbols/Symbol")
    assert symbol.get("name") == "AUDCAD_darwinex"
    assert symbol.get("precision") == "TICK"
    assert symbol.get("broker") == "4"
    assert symbol.find("InstrumentInfo").get("defaultSpread") == "2"
    assert root.findall(".//Resources/Sessions/Session") == []
    assert len(root.findall(".//Resources/CustomBlocks/Item")) == 1


def test_tick_real_options_rankings_keep_failed_rows_but_not_coladero():
    root = ET.fromstring(
        """
        <Task>
          <Data><OutOfSample showGraph="false" /></Data>
          <Options>
            <BuildTradingOptions><Params>
              <Param key="Session" className="SessionOption">No Session</Param>
              <Param key="MarketOpenSession" className="SessionOption">No Session</Param>
              <Param key="LimitTimeRange" className="LimitTimeRange">false</Param>
              <Param key="SignalTimeRangeFrom" className="LimitTimeRange">28800</Param>
              <Param key="SignalTimeRangeTo" className="LimitTimeRange">57600</Param>
              <Param key="RealisticGapsHandling" className="RealisticGapsHandling">false</Param>
              <Param key="StoreChartData" className="StoreChartData">true</Param>
            </Params></BuildTradingOptions>
          </Options>
          <Rankings type="never">
            <MaxStrategies>10000</MaxStrategies>
            <ConditionsType>1</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Existing portfolio" />
            <CustomAnalysis filter="true" inputArgs="" method="none" />
            <StopCondition type="databank-full" passedStrategies="1000" restartCount="5" days="0" hours="0" minutes="0" />
            <Conditions />
          </Rankings>
        </Task>
        """
    )

    actions = apply_tick_real_options_rankings_to_root(root)

    assert any(item["field"] == "Rankings/DeleteFailedStrategies" and item["changed"] for item in actions)
    assert enforce_tick_real_options_rankings_guard(root) == []
    params = {
        node.get("key"): node.text
        for node in root.findall(".//BuildTradingOptions/Params/Param")
    }
    assert params["LimitTimeRange"] == "true"
    assert params["SignalTimeRangeFrom"] == "7200"
    assert params["SignalTimeRangeTo"] == "79200"
    assert params["RealisticGapsHandling"] == "true"
    rankings = root.find(".//Rankings")
    assert rankings.findtext("DeleteFailedStrategies") == "false"
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


def test_tick_real_options_rankings_guard_rejects_oos_split_and_empty_filters():
    root = ET.fromstring(
        """
        <Task>
          <Data><OutOfSample showGraph="true"><Range dateFrom="2023.01.01" dateTo="2023.12.31" /></OutOfSample></Data>
          <Options><BuildTradingOptions><Params>
            <Param key="Session">No Session</Param>
            <Param key="MarketOpenSession">No Session</Param>
            <Param key="LimitTimeRange">true</Param>
            <Param key="SignalTimeRangeFrom">7200</Param>
            <Param key="SignalTimeRangeTo">79200</Param>
            <Param key="RealisticGapsHandling">true</Param>
            <Param key="StoreChartData">false</Param>
          </Params></BuildTradingOptions></Options>
          <Rankings>
            <ConditionsType>0</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>false</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Existing portfolio" />
            <CustomAnalysis filter="false" inputArgs="" method="none" />
            <Conditions />
          </Rankings>
        </Task>
        """
    )

    issues = enforce_tick_real_options_rankings_guard(root)

    assert any("must not add an internal OOS split" in issue for issue in issues)
    assert any("failed strategies visible" in issue for issue in issues)
    assert any("conditions must stay active" in issue for issue in issues)
    assert any("portfolio fit" in issue for issue in issues)
    assert any("ranking conditions" in issue for issue in issues)


def test_tick_real_passive_generation_disables_improve_and_preserves_entry_exit_logic():
    root = ET.fromstring(
        """
        <Task>
          <PartsToImprove improveATM="true">
            <EntryRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></EntryRules>
            <OrderTypes><LongImprovement use="true" /><ShortImprovement use="true" /></OrderTypes>
            <ExitRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" stale="true" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>true</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="true" />
              <EvoRestartOnStagnation status="true" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple">
            <BuildingBlocks>
              <Block key="Signals.ADX" category="signals" use="true" probability="1" />
              <Block key="Indicators.ATR" category="indicators" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="true" probability="1" />
            </BuildingBlocks>
            <OrderTypes>
              <Block key="EnterAtMarket" use="false" probability="1" />
              <Block key="EnterReverseAtMarket" use="true" probability="1" />
              <Block key="EnterAtStop" use="true" probability="1" />
              <Block key="EnterAtLimit" use="true" probability="1" />
            </OrderTypes>
            <ExitTypes>
              <Block key="ExitAfterBars.ExitAfterBars" use="false" probability="50" />
              <Block key="ExitAfterDays.ExitAfterDays" use="true" probability="50" />
              <Block key="StopLoss.StopLoss" use="true" probability="50" />
            </ExitTypes>
            <CustomData showAll="true"><Item key="legacy" /></CustomData>
          </Blocks>
        </Task>
        """
    )
    source_root = ET.fromstring(
        """
        <Task>
          <Blocks type="simple" version="142.2336">
            <BuildingBlocks>
              <Block key="Signals.ADX" category="signals" use="false" probability="1" />
              <Block key="Indicators.ATR" category="indicators" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="false" probability="1" />
            </BuildingBlocks>
            <OrderTypes>
              <Block key="EnterAtMarket" use="true" probability="1" />
              <Block key="EnterReverseAtMarket" use="false" probability="1" />
              <Block key="EnterAtStop" use="false" probability="1" />
              <Block key="EnterAtLimit" use="false" probability="1" />
            </OrderTypes>
            <ExitTypes>
              <Block key="ExitAfterBars.ExitAfterBars" use="true" probability="100" />
              <Block key="StopLoss.StopLoss" use="false" probability="50" />
            </ExitTypes>
            <CustomData showAll="false" />
          </Blocks>
        </Task>
        """
    )

    actions = apply_tick_real_passive_generation_to_root(root, source_root)

    assert any(item["field"] == "BuildingBlocks:disableCategory:signals" and item["changed"] for item in actions)
    assert enforce_tick_real_passive_generation_guard(root) == []
    assert root.find(".//PartsToImprove/ExitRules/LongImprovement").get("use") == "false"
    assert root.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "retest 1"
    assert root.find(".//WhatToBuild/StrategyType").get("stale") is None
    assert root.find(".//BuildMode/ShowLastGenerationDatabank").text == "false"
    assert root.find(".//BuildMode/FreshBloodReplaceSimilar").text == "false"
    assert root.find(".//BuildMode/EvoRestartOnFinish").get("status") == "false"
    assert root.find(".//Blocks").get("version") == "142.2336"
    assert root.findall(".//ExitTypes/Block[@key='ExitAfterDays.ExitAfterDays']") == []
    assert root.find(".//ExitTypes/Block[@key='ExitAfterBars.ExitAfterBars']").get("probability") == "100"
    assert root.find(".//BuildingBlocks/Block[@key='Indicators.ATR']").get("use") == "true"
    assert root.find(".//BuildingBlocks/Block[@key='Signals.ADX']").get("use") == "false"


def test_tick_real_passive_generation_guard_rejects_active_improvement_and_day_exits():
    root = ET.fromstring(
        """
        <Task>
          <PartsToImprove improveATM="true">
            <EntryRules symmetry="true"><LongImprovement use="false" action="replace" /><ShortImprovement use="false" action="replace" /></EntryRules>
            <OrderTypes><LongImprovement use="false" /><ShortImprovement use="false" /></OrderTypes>
            <ExitRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>false</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="true" />
              <EvoRestartOnStagnation status="true" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple">
            <BuildingBlocks>
              <Block key="Signals.ADX" category="signals" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="true" probability="1" />
            </BuildingBlocks>
            <OrderTypes>
              <Block key="EnterAtMarket" use="false" />
              <Block key="EnterReverseAtMarket" use="true" />
              <Block key="EnterAtStop" use="true" />
              <Block key="EnterAtLimit" use="true" />
            </OrderTypes>
            <ExitTypes><Block key="ExitAfterDays.ExitAfterDays" use="true" probability="50" /></ExitTypes>
            <CustomData showAll="true"><Item /></CustomData>
          </Blocks>
        </Task>
        """
    )

    issues = enforce_tick_real_passive_generation_guard(root)

    assert any("ExitRules/LongImprovement" in issue for issue in issues)
    assert any("StrategyType" in issue for issue in issues)
    assert any("ShowLastGenerationDatabank" in issue for issue in issues)
    assert any("order types" in issue for issue in issues)
    assert any("ExitAfterBars" in issue for issue in issues)
    assert any("day-based exit" in issue for issue in issues)
    assert any("signals must remain disabled" in issue for issue in issues)
    assert any("stop/limit entry blocks" in issue for issue in issues)


def test_tick_real_static_crosschecks_target_turns_off_internal_checks_and_keeps_static_tabs_safe():
    root = ET.fromstring(
        """
        <Task>
          <Data>
            <Setups>
              <Setup dateFrom="2010.01.01" dateTo="2026.04.08" testPrecision="1" session="Old Session" slippage="0" minDist="0" engine="MetaTrader5 (hedged)">
                <Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2" />
              </Setup>
            </Setups>
          </Data>
          <Databanks retestSelected="false">
            <Databank label="Input databank" name="Input" value="RETEST 0" />
            <Databank label="Output databank" name="Output" value="retest 1" />
          </Databanks>
          <Resources>
            <Symbols>
              <Symbol name="AUDCAD_darwinex" source="4" precision="TICK" timezone="EETUS" broker="4">
                <InstrumentInfo instrument="AUDCAD_darwinex" broker="4" />
              </Symbol>
            </Symbols>
            <Brokers><Broker id="4" name="[[Darwinex]]" timezone="EETUS" /></Brokers>
            <Sessions />
            <CustomIndicators />
            <CustomBlocks />
          </Resources>
          <Options>
            <BuildTradingOptions><Params>
              <Param key="Session">Old Session</Param>
              <Param key="MarketOpenSession">Old Session</Param>
              <Param key="LimitTimeRange">false</Param>
              <Param key="SignalTimeRangeFrom">0</Param>
              <Param key="SignalTimeRangeTo">86400</Param>
              <Param key="RealisticGapsHandling">false</Param>
              <Param key="StoreChartData">true</Param>
            </Params></BuildTradingOptions>
          </Options>
          <Rankings>
            <MaxStrategies>100</MaxStrategies>
            <ConditionsType>0</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <Conditions />
            <FitPortfolio active="true" databank="Existing portfolio" />
            <CustomAnalysis filter="true" />
          </Rankings>
          <PartsToImprove improveATM="true">
            <EntryRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></EntryRules>
            <OrderTypes><LongImprovement use="true" /><ShortImprovement use="true" /></OrderTypes>
            <ExitRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>true</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="true" />
              <EvoRestartOnStagnation status="true" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple">
            <BuildingBlocks>
              <Block key="Signals.ADX" category="signals" use="true" probability="1" />
              <Block key="Indicators.ATR" category="indicators" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="true" probability="1" />
            </BuildingBlocks>
            <OrderTypes>
              <Block key="EnterAtMarket" use="false" probability="1" />
              <Block key="EnterReverseAtMarket" use="true" probability="1" />
              <Block key="EnterAtStop" use="true" probability="1" />
              <Block key="EnterAtLimit" use="true" probability="1" />
            </OrderTypes>
            <ExitTypes>
              <Block key="ExitAfterBars.ExitAfterBars" use="false" probability="50" />
              <Block key="StopLoss.StopLoss" use="true" probability="50" />
            </ExitTypes>
            <CustomData showAll="true"><Item key="legacy" /></CustomData>
          </Blocks>
          <CrossChecks use="true" evaluateAll="true">
            <MonteCarloRetest use="true"><Settings><Methods><Method type="RandomizeSpread" use="true" /></Methods></Settings></MonteCarloRetest>
            <WhatIf use="false"><Settings><Methods><Method type="ExcludeTradesWithBiggestPl" use="true" /></Methods></Settings></WhatIf>
          </CrossChecks>
          <RiskMoneyManagement customSettings="false">
            <MoneyManagement>
              <Method type="FixedSize" use="false" />
              <Method type="RiskFixedBalancePct" use="false" />
              <Method type="RiskFixedPctOfAccount" use="false" />
              <Method type="FixedAmount" use="true" />
              <Method type="StocksSizeByPrice" use="false" />
            </MoneyManagement>
          </RiskMoneyManagement>
          <ATMs enable="false" />
          <Notes>ok</Notes>
          <CustomData>
            <Setups>
              <Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="4" session="No Session" slippage="0" minDist="0" engine="MetaTrader4">
                <Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2" />
              </Setup>
            </Setups>
          </CustomData>
        </Task>
        """
    )

    apply_tick_real_data_databanks_resources_to_root(root)
    apply_tick_real_options_rankings_to_root(root)
    apply_tick_real_passive_generation_to_root(root, source_root=root)
    actions = apply_tick_real_static_crosschecks_to_root(root)

    assert any(item["field"] == "CrossChecks:attrs" and item["changed"] for item in actions)
    assert any(item["field"] == "CrossChecks/MonteCarloRetest:use" and item["changed"] for item in actions)
    assert any(item["field"] == "CrossChecks/WhatIf/Method:ExcludeTradesWithBiggestPl:use" and item["changed"] for item in actions)
    assert any(item["field"] == "RiskMoneyManagement/Method:FixedSize" and item["changed"] for item in actions)
    assert enforce_tick_real_static_crosschecks_guard(root) == []
    assert root.find(".//CrossChecks").get("use") == "false"
    assert root.find(".//CrossChecks").get("evaluateAll") == "false"
    assert root.find(".//CrossChecks/MonteCarloRetest").get("use") == "false"
    assert root.find(".//CrossChecks/MonteCarloRetest/Settings/Methods/Method").get("use") == "false"
    assert root.find(".//RiskMoneyManagement//Method[@type='FixedSize']").get("use") == "true"
    assert root.find(".//RiskMoneyManagement//Method[@type='FixedAmount']").get("use") == "false"


def test_tick_real_static_crosschecks_guard_rejects_stale_crosscheck_and_customdata_donor():
    root = ET.fromstring(
        """
        <Task>
          <CrossChecks use="true" evaluateAll="true">
            <MonteCarloRetest use="true"><Settings><Methods><Method type="RandomizeSpread" use="true" /></Methods></Settings></MonteCarloRetest>
          </CrossChecks>
          <RiskMoneyManagement><MoneyManagement><Method type="FixedSize" use="false" /><Method type="FixedAmount" use="true" /></MoneyManagement></RiskMoneyManagement>
          <ATMs enable="true" />
          <Rankings><ForceRunCrossChecks>true</ForceRunCrossChecks></Rankings>
          <CustomData>
            <Setups>
              <Setup dateFrom="2017.10.02" dateTo="2024.12.31" session="Old Session">
                <Chart symbol="USDJPY_darwinex" timeframe="H4" />
              </Setup>
            </Setups>
          </CustomData>
        </Task>
        """
    )

    issues = enforce_tick_real_static_crosschecks_guard(root)

    assert any("active internal crosschecks" in issue for issue in issues)
    assert any("Settings/Methods" in issue for issue in issues)
    assert any("RiskMoneyManagement FixedSize" in issue for issue in issues)
    assert any("ATMs enable" in issue for issue in issues)
    assert any("ForceRunCrossChecks" in issue for issue in issues)
    assert any("CustomData dates" in issue for issue in issues)
    assert any("Forbidden donor token" in issue for issue in issues)


def test_mc_data_databanks_resources_options_target_is_fast_generic_and_post_tick():
    root = ET.fromstring(
        """
        <Task>
          <Data>
            <Setups>
              <Setup dateFrom="2010.01.01" dateTo="2026.04.08" testPrecision="4" session="Old Session" slippage="0" minDist="0" engine="MetaTrader4">
                <Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2" />
              </Setup>
            </Setups>
            <OutOfSample showGraph="true"><Range dateFrom="2023.01.01" dateTo="2024.01.01" /></OutOfSample>
          </Data>
          <Databanks retestSelected="false">
            <Databank label="Input databank" name="Input" value="retest 1" />
            <Databank label="Output databank" name="Output" value="TICK" />
          </Databanks>
          <Resources>
            <Symbols>
              <Symbol name="AUDCAD_darwinex" source="4" precision="M1" timezone="UTC" dateFrom="1262304000000" dateTo="1775606400000" uSymbol="AUDCAD" uSymbolName="AUDCAD" broker="4">
                <InstrumentInfo instrument="AUDCAD_darwinex" defaultSpread="1.7" broker="4" />
              </Symbol>
            </Symbols>
            <Brokers><Broker id="4" name="[[Darwinex]]" timezone="UTC" /></Brokers>
            <Instruments />
            <Sessions><Session name="Old Session" /></Sessions>
            <CustomIndicators />
            <CustomBlocks />
          </Resources>
          <Options>
            <BuildTradingOptions><Params>
              <Param key="Session">Old Session</Param>
              <Param key="MarketOpenSession">Old Session</Param>
              <Param key="LimitTimeRange">true</Param>
              <Param key="RealisticGapsHandling">true</Param>
              <Param key="StoreChartData">true</Param>
            </Params></BuildTradingOptions>
          </Options>
        </Task>
        """
    )

    actions = apply_mc_data_databanks_resources_options_to_root(root)

    assert any(item["field"] == "Data/OutOfSample" and item["changed"] for item in actions)
    assert any(item["field"] == "Databanks/Input" and item["changed"] for item in actions)
    assert enforce_mc_data_databanks_resources_options_guard(root) == []
    setup = root.find(".//Data/Setups/Setup")
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == "2"
    assert setup.get("session") == "No Session"
    assert root.findall(".//Data/OutOfSample/Range") == []
    assert {node.get("name"): node.get("value") for node in root.findall(".//Databanks/Databank")} == {
        "Input": "TICK",
        "Output": "MC",
    }
    symbol = root.find(".//Resources/Symbols/Symbol")
    assert symbol.get("name") == "AUDCAD_darwinex"
    assert symbol.get("precision") == "TICK"
    assert symbol.get("timezone") == "EETUS"
    assert symbol.get("dateTo") == "1703980800000"
    assert root.findall(".//Resources/Sessions/Session") == []
    params = {
        param.get("key"): param.text
        for param in root.findall(".//BuildTradingOptions/Params/Param")
    }
    assert params["Session"] == "No Session"
    assert params["MarketOpenSession"] == "No Session"
    assert params["LimitTimeRange"] == "false"
    assert params["RealisticGapsHandling"] == "false"
    assert params["StoreChartData"] == "false"


def test_mc_data_databanks_resources_options_guard_rejects_donor_oos_and_wrong_options():
    root = ET.fromstring(
        """
        <Task>
          <Data>
            <Setups>
              <Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="4" session="Old Session">
                <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="2" />
              </Setup>
            </Setups>
            <OutOfSample showGraph="true"><Range dateFrom="2020.01.01" dateTo="2021.01.01" /></OutOfSample>
          </Data>
          <Databanks>
            <Databank name="Input" value="RETEST 0" />
            <Databank name="Output" value="TICK" />
          </Databanks>
          <Resources>
            <Symbols>
              <Symbol name="USDJPY_darwinex" source="4" precision="M1" timezone="UTC" broker="9">
                <InstrumentInfo instrument="USDJPY_darwinex" broker="9" />
              </Symbol>
            </Symbols>
            <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
            <Sessions><Session name="Old Session" /></Sessions>
          </Resources>
          <Options>
            <BuildTradingOptions><Params>
              <Param key="Session">Old Session</Param>
              <Param key="MarketOpenSession">Old Session</Param>
              <Param key="LimitTimeRange">true</Param>
              <Param key="RealisticGapsHandling">true</Param>
              <Param key="StoreChartData">true</Param>
            </Params></BuildTradingOptions>
          </Options>
        </Task>
        """
    )

    issues = enforce_mc_data_databanks_resources_options_guard(root)

    assert any("testPrecision" in issue for issue in issues)
    assert any("nested OutOfSample" in issue for issue in issues)
    assert any("Databank Input" in issue for issue in issues)
    assert any("precision is not TICK" in issue for issue in issues)
    assert any("references missing broker" in issue for issue in issues)
    assert any("session entries" in issue for issue in issues)
    assert any("Options param LimitTimeRange" in issue for issue in issues)
    assert any("Forbidden donor token" in issue for issue in issues)


def test_mc_crosschecks_target_runs_only_trade_order_manipulation_and_cleans_disabled_methods():
    root = ET.fromstring(
        """
        <Task>
          <Data>
            <Setups>
              <Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session">
                <Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2" />
              </Setup>
            </Setups>
          </Data>
          <Databanks>
            <Databank name="Input" value="TICK" />
            <Databank name="Output" value="MC" />
          </Databanks>
          <Rankings><ForceRunCrossChecks>false</ForceRunCrossChecks></Rankings>
          <CrossChecks use="false" evaluateAll="false">
            <RetestOnAdditionalMarkets use="true">
              <Settings>
                <Setups>
                  <Setup dateFrom="2017.10.02" dateTo="2026.04.08" testPrecision="1" session="Old Session">
                    <Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2" />
                  </Setup>
                </Setups>
              </Settings>
            </RetestOnAdditionalMarkets>
            <MonteCarloRetest use="true">
              <Settings><Methods><Method type="RandomizeSpread" use="true"><Params><Param key="Min">1.0</Param><Param key="Max">5.0</Param></Params></Method></Methods></Settings>
            </MonteCarloRetest>
            <MonteCarloManipulation use="false">
              <Settings>
                <Methods>
                  <Method type="RandomizeTradesOrder" use="false"><Params><Param key="Method" type="String">permutation</Param></Params></Method>
                  <Method type="RandomlySkipTrades" use="true"><Params><Param key="Probability" type="Integer">25</Param></Params></Method>
                </Methods>
                <NumberOfSimulations>50</NumberOfSimulations>
                <MCUseFullSample>false</MCUseFullSample>
              </Settings>
              <AcceptanceSettings><Conditions CrossCheck="MonteCarloManipulation" /></AcceptanceSettings>
            </MonteCarloManipulation>
            <WhatIf use="false">
              <Settings><Methods><Method type="ExcludeTradesWithBiggestPl" use="true"><Params><Param key="Trades">2</Param></Params></Method></Methods></Settings>
            </WhatIf>
          </CrossChecks>
        </Task>
        """
    )

    actions = apply_mc_crosschecks_to_root(root)

    assert any(item["field"] == "CrossChecks:attrs" and item["changed"] for item in actions)
    assert any(item["field"] == "CrossChecks/MonteCarloRetest/Method:RandomizeSpread:use" and item["changed"] for item in actions)
    assert any(item["field"] == "CrossChecks/*/Settings/Setups/Setup" and item["changed"] for item in actions)
    assert enforce_mc_crosschecks_guard(root) == []
    assert root.find(".//CrossChecks").get("use") == "true"
    assert root.find(".//CrossChecks").get("evaluateAll") == "true"
    assert root.find(".//CrossChecks/MonteCarloRetest").get("use") == "false"
    assert root.find(".//CrossChecks/MonteCarloRetest//Method[@type='RandomizeSpread']").get("use") == "false"
    assert root.find(".//CrossChecks/WhatIf//Method[@type='ExcludeTradesWithBiggestPl']").get("use") == "false"
    manipulation = root.find(".//CrossChecks/MonteCarloManipulation")
    assert manipulation.get("use") == "true"
    assert manipulation.findtext("./Settings/NumberOfSimulations") == "200"
    assert manipulation.findtext("./Settings/MCUseFullSample") == "true"
    assert manipulation.find(".//Method[@type='RandomizeTradesOrder']").get("use") == "true"
    assert manipulation.find(".//Method[@type='RandomizeTradesOrder']/Params/Param[@key='Method']").text == "resampling"
    assert manipulation.find(".//Method[@type='RandomlySkipTrades']").get("use") == "false"
    conditions = manipulation.findall("./AcceptanceSettings/Conditions/Condition")
    assert len(conditions) == 2
    assert conditions[0].find("./Left-Side/Column-Value").get("column") == "NetProfit"
    assert conditions[0].find("./Right-Side/Column-Value").get("pctRatio") == "40"
    assert conditions[1].find("./Left-Side/Column-Value").get("column") == "DrawdownPct"
    assert conditions[1].find("./Right-Side/Column-Value").get("pctRatio") == "200"
    nested_setup = root.find(".//CrossChecks/RetestOnAdditionalMarkets/Settings/Setups/Setup")
    assert nested_setup.get("dateTo") == "2023.12.31"
    assert nested_setup.get("testPrecision") == "2"
    assert nested_setup.get("session") == "No Session"


def test_mc_crosschecks_guard_rejects_wrong_active_check_disabled_methods_and_donor_tokens():
    root = ET.fromstring(
        """
        <Task>
          <Data><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session"><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2" /></Setup></Setups></Data>
          <Rankings><ForceRunCrossChecks>true</ForceRunCrossChecks></Rankings>
          <CrossChecks use="true" evaluateAll="true">
            <MonteCarloRetest use="true">
              <Settings>
                <Setups><Setup dateFrom="2017.10.02" dateTo="2026.05.15" testPrecision="1" session="No Session"><Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" /></Setup></Setups>
                <Methods><Method type="RandomizeSpread" use="true"><Params><Param key="Min">1.0</Param><Param key="Max">5.0</Param></Params></Method></Methods>
              </Settings>
            </MonteCarloRetest>
            <MonteCarloManipulation use="true">
              <Settings>
                <Methods><Method type="RandomizeTradesOrder" use="false"><Params><Param key="Method" type="String">permutation</Param></Params></Method></Methods>
                <NumberOfSimulations>10</NumberOfSimulations>
                <MCUseFullSample>false</MCUseFullSample>
              </Settings>
              <AcceptanceSettings><Conditions CrossCheck="MonteCarloManipulation" /></AcceptanceSettings>
            </MonteCarloManipulation>
          </CrossChecks>
        </Task>
        """
    )

    issues = enforce_mc_crosschecks_guard(root)

    assert any("active crosschecks" in issue for issue in issues)
    assert any("NumberOfSimulations" in issue for issue in issues)
    assert any("RandomizeTradesOrder" in issue for issue in issues)
    assert any("acceptance conditions" in issue for issue in issues)
    assert any("disabled crosschecks" in issue for issue in issues)
    assert any("nested CrossChecks setup dates" in issue for issue in issues)
    assert any("Rankings/ForceRunCrossChecks" in issue for issue in issues)
    assert any("Forbidden donor token" in issue for issue in issues)


def test_mc_passive_generation_disables_generation_and_preserves_mc_indicator_universe():
    root = ET.fromstring(
        """
        <Task>
          <PartsToImprove improveATM="true">
            <EntryRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></EntryRules>
            <OrderTypes><LongImprovement use="true" /><ShortImprovement use="true" /></OrderTypes>
            <ExitRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" stale="true" />
            <MarketSides type="long" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>false</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="true" />
              <EvoRestartOnStagnation status="true" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple">
            <BuildingBlocks>
              <Block key="Signals.ADX" category="signals" use="true" probability="1" />
              <Block key="Indicators.ATR" category="indicators" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="true" probability="1" />
            </BuildingBlocks>
            <OrderTypes>
              <Block key="EnterAtMarket" use="false" probability="1" />
              <Block key="EnterReverseAtMarket" use="true" probability="1" />
              <Block key="EnterAtStop" use="true" probability="1" />
              <Block key="EnterAtLimit" use="true" probability="1" />
            </OrderTypes>
            <ExitTypes>
              <Block key="ExitAfterBars.ExitAfterBars" use="true" probability="50" />
              <Block key="StopLoss.StopLoss" use="true" probability="50" />
            </ExitTypes>
            <CustomData showAll="true"><Item key="legacy" /></CustomData>
          </Blocks>
        </Task>
        """
    )
    source_root = ET.fromstring(
        """
        <Task>
          <Blocks type="simple" version="142.2336">
            <BuildingBlocks>
              <Block key="Indicators.Fallback" category="indicators" use="true" probability="1" />
            </BuildingBlocks>
          </Blocks>
        </Task>
        """
    )

    actions = apply_mc_passive_generation_to_root(root, source_root)

    assert any(item["field"] == "BuildingBlocks:disableCategory:signals" and item["changed"] for item in actions)
    assert enforce_mc_passive_generation_guard(root) == []
    assert root.find(".//PartsToImprove/ExitRules/LongImprovement").get("use") == "false"
    assert root.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "TICK"
    assert root.find(".//WhatToBuild/StrategyType").get("stale") is None
    assert root.find(".//WhatToBuild/MarketSides").get("type") == "long"
    assert root.find(".//BuildMode/ShowLastGenerationDatabank").text == "false"
    assert root.find(".//BuildMode/FreshBloodReplaceSimilar").text == "false"
    assert root.find(".//BuildMode/EvoRestartOnFinish").get("status") == "false"
    assert root.find(".//Blocks").get("version") == "142.2336"
    assert root.find(".//ExitTypes/Block[@key='ExitAfterBars.ExitAfterBars']").get("probability") == "100"
    assert root.find(".//BuildingBlocks/Block[@key='Indicators.ATR']").get("use") == "true"
    assert root.find(".//BuildingBlocks/Block[@key='Indicators.Fallback']") is None
    assert root.find(".//BuildingBlocks/Block[@key='Signals.ADX']").get("use") == "false"
    assert root.find(".//BuildingBlocks/Block[@key='StopLimitBlocks.ATRStop']").get("use") == "false"


def test_mc_passive_generation_guard_rejects_active_generation_and_donor_day_exits():
    root = ET.fromstring(
        """
        <Task>
          <PartsToImprove improveATM="true">
            <EntryRules symmetry="true"><LongImprovement use="false" action="replace" /><ShortImprovement use="false" action="replace" /></EntryRules>
            <OrderTypes><LongImprovement use="false" /><ShortImprovement use="false" /></OrderTypes>
            <ExitRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>false</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="true" />
              <EvoRestartOnStagnation status="true" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple">
            <BuildingBlocks>
              <Block key="Signals.USDJPY_darwinex" category="signals" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="true" probability="1" />
            </BuildingBlocks>
            <OrderTypes>
              <Block key="EnterAtMarket" use="false" />
              <Block key="EnterReverseAtMarket" use="true" />
              <Block key="EnterAtStop" use="true" />
              <Block key="EnterAtLimit" use="true" />
            </OrderTypes>
            <ExitTypes><Block key="ExitAfterDays.ExitAfterDays" use="true" probability="50" /></ExitTypes>
            <CustomData showAll="true"><Item /></CustomData>
          </Blocks>
        </Task>
        """
    )

    issues = enforce_mc_passive_generation_guard(root)

    assert any("ExitRules/LongImprovement" in issue for issue in issues)
    assert any("StrategyType" in issue for issue in issues)
    assert any("ShowLastGenerationDatabank" in issue for issue in issues)
    assert any("order types" in issue for issue in issues)
    assert any("ExitAfterBars" in issue for issue in issues)
    assert any("day-based exit" in issue for issue in issues)
    assert any("signals must remain disabled" in issue for issue in issues)
    assert any("stop/limit entry blocks" in issue for issue in issues)
    assert any("Forbidden token" in issue for issue in issues)


def test_mc_static_tabs_disable_portfolio_fit_and_normalize_custom_data_seed():
    root = ET.fromstring(
        """
        <Task>
          <Data>
            <Setups>
              <Setup dateFrom="2010.01.01" dateTo="2026.04.08" testPrecision="4" session="Old Session" slippage="0" minDist="0" engine="MetaTrader5 (hedged)">
                <Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2" />
              </Setup>
            </Setups>
            <OutOfSample showGraph="true"><Range dateFrom="2020.01.01" dateTo="2021.01.01" /></OutOfSample>
          </Data>
          <Databanks>
            <Databank name="Input" value="retest 1" />
            <Databank name="Output" value="TICK" />
          </Databanks>
          <Resources>
            <Symbols>
              <Symbol name="AUDCAD_darwinex" source="4" precision="M1" timezone="UTC" broker="4">
                <InstrumentInfo instrument="AUDCAD_darwinex" defaultSpread="2" broker="4" />
              </Symbol>
            </Symbols>
            <Brokers><Broker id="4" name="[[Darwinex]]" timezone="UTC" /></Brokers>
            <Instruments />
            <Sessions><Session name="Old Session" /></Sessions>
            <CustomIndicators />
            <CustomBlocks />
          </Resources>
          <Options>
            <BuildTradingOptions><Params>
              <Param key="Session">Old Session</Param>
              <Param key="MarketOpenSession">Old Session</Param>
              <Param key="LimitTimeRange">true</Param>
              <Param key="RealisticGapsHandling">true</Param>
              <Param key="StoreChartData">true</Param>
            </Params></BuildTradingOptions>
          </Options>
          <Rankings type="always">
            <MaxStrategies>500</MaxStrategies>
            <ConditionsType>1</ConditionsType>
            <DeleteFailedStrategies>false</DeleteFailedStrategies>
            <ForceRunCrossChecks>false</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Existing portfolio"><Correlation max="0.3" /></FitPortfolio>
            <CustomAnalysis filter="true" inputArgs="" method="none" />
            <StopCondition type="passed" passedStrategies="10" restartCount="1" days="1" hours="1" minutes="1" />
            <Conditions><Condition use="true"><Left-Side><Column-Value column="NetProfit" format="Decimal2" sampleType="127" /></Left-Side><Comparator value=">=" /><Right-Side><Numeric-Value value="1" /></Right-Side></Condition></Conditions>
          </Rankings>
          <PartsToImprove improveATM="true">
            <EntryRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></EntryRules>
            <OrderTypes><LongImprovement use="true" /><ShortImprovement use="true" /></OrderTypes>
            <ExitRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>true</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="true" />
              <EvoRestartOnStagnation status="true" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple">
            <BuildingBlocks>
              <Block key="Signals.ADX" category="signals" use="true" probability="1" />
              <Block key="Indicators.ATR" category="indicators" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="true" probability="1" />
            </BuildingBlocks>
            <OrderTypes>
              <Block key="EnterAtMarket" use="false" />
              <Block key="EnterReverseAtMarket" use="true" />
              <Block key="EnterAtStop" use="true" />
              <Block key="EnterAtLimit" use="true" />
            </OrderTypes>
            <ExitTypes><Block key="ExitAfterBars.ExitAfterBars" use="false" probability="50" /><Block key="StopLoss.StopLoss" use="true" probability="50" /></ExitTypes>
            <CustomData showAll="true"><Item /></CustomData>
          </Blocks>
          <CrossChecks use="false" evaluateAll="false">
            <MonteCarloRetest use="true"><Settings><Methods><Method type="RandomizeSpread" use="true" /></Methods></Settings></MonteCarloRetest>
            <MonteCarloManipulation use="false">
              <Settings>
                <Methods>
                  <Method type="RandomizeTradesOrder" use="false"><Params><Param key="Method" type="String">permutation</Param></Params></Method>
                  <Method type="RandomlySkipTrades" use="true"><Params><Param key="Probability" type="Integer">25</Param></Params></Method>
                </Methods>
                <NumberOfSimulations>50</NumberOfSimulations>
                <MCUseFullSample>false</MCUseFullSample>
              </Settings>
              <AcceptanceSettings><Conditions CrossCheck="MonteCarloManipulation" /></AcceptanceSettings>
            </MonteCarloManipulation>
          </CrossChecks>
          <RiskMoneyManagement customSettings="false">
            <MoneyManagement>
              <Method type="FixedSize" use="false" />
              <Method type="RiskFixedBalancePct" use="false" />
              <Method type="RiskFixedPctOfAccount" use="false" />
              <Method type="FixedAmount" use="true" />
              <Method type="StocksSizeByPrice" use="false" />
            </MoneyManagement>
          </RiskMoneyManagement>
          <ATMs enable="true" scaleOutType="1" />
          <Notes>ok</Notes>
          <SelectedStrategies><Strategy id="legacy" /></SelectedStrategies>
          <CustomData>
            <Setups>
              <Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="1" session="No Session" slippage="0" minDist="0" engine="MetaTrader4">
                <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
                <Commissions>
                  <Method type="None" use="false" />
                  <Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">0</Param></Params></Method>
                </Commissions>
                <MainTestValues commissions="true" dates="false" distance="true" engine="true" precision="false" slippage="true" spread="true" subcharts="false" symbol="false" timeframe="true" />
              </Setup>
            </Setups>
          </CustomData>
        </Task>
        """
    )

    apply_mc_data_databanks_resources_options_to_root(root)
    apply_mc_crosschecks_to_root(root)
    apply_mc_passive_generation_to_root(root, source_root=root)
    actions = apply_mc_static_tabs_to_root(root)

    assert any(item["field"] == "Rankings/FitPortfolio" and item["changed"] for item in actions)
    assert any(item["field"] == "Rankings/Conditions" and item["changed"] for item in actions)
    assert any(item["field"] == "RiskMoneyManagement/Method:FixedSize" and item["changed"] for item in actions)
    assert any(item["field"] == "ATMs:attrs" and item["changed"] for item in actions)
    assert any(item["field"] == "SelectedStrategies" and item["changed"] for item in actions)
    assert any(item["field"] == "CustomData/Setup:attrs" and item["changed"] for item in actions)
    assert enforce_mc_static_tabs_guard(root) == []
    rankings = root.find(".//Rankings")
    assert rankings.find("FitPortfolio").get("active") == "false"
    assert rankings.find("CustomAnalysis").get("filter") == "false"
    assert rankings.findall("./Conditions/Condition") == []
    assert root.find(".//RiskMoneyManagement//Method[@type='FixedSize']").get("use") == "true"
    assert root.find(".//RiskMoneyManagement//Method[@type='FixedAmount']").get("use") == "false"
    assert root.find(".//ATMs").get("enable") == "false"
    assert root.find(".//SelectedStrategies").text is None
    custom_setup = root.find("./CustomData/Setups/Setup")
    assert custom_setup.get("testPrecision") == "2"
    assert custom_setup.find("Chart").get("symbol") == "AUDCAD_darwinex"
    assert custom_setup.find("Chart").get("timeframe") == "H1"
    assert custom_setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']").text == "0.0"


def test_mc_static_tabs_guard_rejects_portfolio_fit_rank_filters_and_customdata_donor():
    root = ET.fromstring(
        """
        <Task>
          <Data><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session"><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2" /></Setup></Setups></Data>
          <Rankings type="always">
            <MaxStrategies>10000</MaxStrategies>
            <ConditionsType>1</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Existing portfolio" />
            <CustomAnalysis filter="true" inputArgs="" method="none" />
            <Conditions><Condition use="true"><Left-Side><Column-Value column="NetProfit" format="Decimal2" sampleType="127" /></Left-Side><Comparator value=">=" /><Right-Side><Numeric-Value value="1" /></Right-Side></Condition></Conditions>
          </Rankings>
          <ATMs enable="true" />
          <RiskMoneyManagement><MoneyManagement><Method type="FixedSize" use="false" /><Method type="FixedAmount" use="true" /></MoneyManagement></RiskMoneyManagement>
          <SelectedStrategies>legacy</SelectedStrategies>
          <CustomData>
            <Setups>
              <Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="1" session="No Session">
                <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
                <Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission">0</Param></Params></Method></Commissions>
                <MainTestValues commissions="false" />
              </Setup>
            </Setups>
          </CustomData>
        </Task>
        """
    )

    issues = enforce_mc_static_tabs_guard(root)

    assert any("Rankings type" in issue for issue in issues)
    assert any("DeleteFailedStrategies" in issue for issue in issues)
    assert any("ForceRunCrossChecks" in issue for issue in issues)
    assert any("FitPortfolio" in issue for issue in issues)
    assert any("extra conditions" in issue for issue in issues)
    assert any("RiskMoneyManagement FixedSize" in issue for issue in issues)
    assert any("ATMs enable" in issue for issue in issues)
    assert any("SelectedStrategies" in issue for issue in issues)
    assert any("CustomData testPrecision" in issue for issue in issues)
    assert any("Forbidden donor token" in issue for issue in issues)


def test_mc_closeout_operation_issues_require_green_idempotent_dry_run():
    payload = {
        "ok": True,
        "apply": False,
        "operation": "mc_static_tabs_target",
        "nextPhase": "phase6_mc_static_tabs_diff_review",
        "written": "diff.json",
        "results": {
            "localBase": {
                "exists": True,
                "isZip": True,
                "guardOk": True,
                "changed": False,
                "changedActionCount": 0,
                "issues": [],
                "taskXml": "AutomaticRetest-Task1.xml",
            },
            "repoTemplate": {
                "exists": True,
                "isZip": True,
                "guardOk": True,
                "changed": False,
                "changedActionCount": 0,
                "issues": [],
                "taskXml": "AutomaticRetest-Task1.xml",
            },
        },
    }

    assert mc_closeout_operation_issues("mc-static-tabs-target", payload) == []
    summary = mc_closeout_operation_summary(payload)
    assert summary["targets"]["localBase"]["changed"] is False
    assert summary["targets"]["repoTemplate"]["guardOk"] is True

    payload["results"]["repoTemplate"]["changed"] = True
    payload["results"]["repoTemplate"]["changedActionCount"] = 2
    payload["results"]["repoTemplate"]["guardOk"] = False
    payload["results"]["repoTemplate"]["issues"] = ["MC Rankings drifted"]

    issues = mc_closeout_operation_issues("mc-static-tabs-target", payload)

    assert any("guardOk is not true" in issue for issue in issues)
    assert any("dry-run is not idempotent" in issue for issue in issues)
    assert any("changedActionCount" in issue for issue in issues)
    assert any("MC Rankings drifted" in issue for issue in issues)


def test_sequential_closeout_report_requires_green_phase8_dry_runs(monkeypatch, tmp_path):
    calls = []

    def green_payload(command: str) -> dict:
        return {
            "ok": True,
            "apply": False,
            "operation": command.replace("-", "_"),
            "nextPhase": "phase8_sequential_closeout",
            "written": f"{command}.json",
            "results": {
                "localBase": {
                    "exists": True,
                    "isZip": True,
                    "guardOk": True,
                    "changed": False,
                    "changedActionCount": 0,
                    "issues": [],
                    "taskXml": "AutomaticRetest-Task3.xml",
                },
                "repoTemplate": {
                    "exists": True,
                    "isZip": True,
                    "guardOk": True,
                    "changed": False,
                    "changedActionCount": 0,
                    "issues": [],
                    "taskXml": "AutomaticRetest-Task3.xml",
                },
            },
        }

    def runner_factory(command: str):
        def runner(root142, project_root, target, apply):
            calls.append((command, target, apply))
            return green_payload(command)
        return runner

    monkeypatch.setattr(gate, "SEQUENTIAL_CLOSEOUT_OPERATIONS", (
        ("dataDatabanksResourcesOptions", "sequential-data-databanks-resources-options-target", runner_factory("sequential-data-databanks-resources-options-target")),
        ("crosschecks", "sequential-crosschecks-target", runner_factory("sequential-crosschecks-target")),
        ("passiveGeneration", "sequential-passive-generation-target", runner_factory("sequential-passive-generation-target")),
        ("staticTabs", "sequential-static-tabs-target", runner_factory("sequential-static-tabs-target")),
    ))
    monkeypatch.setattr(gate, "mc2_closeout_report", lambda *args, **kwargs: {
        "phase": "phase7_mc2_closeout",
        "ok": True,
        "issues": [],
        "nextPhase": "phase8_sequential_open",
    })
    monkeypatch.setattr(gate, "process_snapshot", lambda: {"processes": []})

    payload = gate.sequential_closeout_report(tmp_path, tmp_path, target="both", write=True)

    assert payload["ok"] is True
    assert payload["phase"] == "phase8_sequential_closeout"
    assert payload["nextPhase"] == "phase9_monkey_test_open"
    assert payload["summary"]["chain"] == "Input=MC2 / Output=Sequential"
    assert {call[0] for call in calls} == {
        "sequential-data-databanks-resources-options-target",
        "sequential-crosschecks-target",
        "sequential-passive-generation-target",
        "sequential-static-tabs-target",
    }
    assert all(call[1] == "both" and call[2] is False for call in calls)
    assert (tmp_path / ".local" / "sqx142_task_config" / "session_state.json").is_file()
    state = json.loads((tmp_path / ".local" / "sqx142_task_config" / "session_state.json").read_text(encoding="utf-8"))
    assert state["currentPhase"] == "phase8_sequential_closeout"
    assert state["nextPhase"] == "phase9_monkey_test_open"


def test_monkey_closeout_report_requires_green_phase9_dry_runs(monkeypatch, tmp_path):
    calls = []

    def green_payload(command: str) -> dict:
        return {
            "ok": True,
            "apply": False,
            "operation": command.replace("-", "_"),
            "nextPhase": "phase9_monkey_test_closeout",
            "written": f"{command}.json",
            "results": {
                "localBase": {
                    "exists": True,
                    "isZip": True,
                    "guardOk": True,
                    "changed": False,
                    "changedActionCount": 0,
                    "issues": [],
                    "taskXml": "AutomaticRetest-Task6.xml",
                },
                "repoTemplate": {
                    "exists": True,
                    "isZip": True,
                    "guardOk": True,
                    "changed": False,
                    "changedActionCount": 0,
                    "issues": [],
                    "taskXml": "AutomaticRetest-Task6.xml",
                },
            },
        }

    def runner_factory(command: str):
        def runner(root142, project_root, target, apply):
            calls.append((command, target, apply))
            return green_payload(command)
        return runner

    monkeypatch.setattr(gate, "MONKEY_CLOSEOUT_OPERATIONS", (
        ("dataDatabanksResourcesOptions", "monkey-data-databanks-resources-options-target", runner_factory("monkey-data-databanks-resources-options-target")),
        ("crosschecks", "monkey-crosschecks-target", runner_factory("monkey-crosschecks-target")),
        ("passiveGeneration", "monkey-passive-generation-target", runner_factory("monkey-passive-generation-target")),
        ("staticTabs", "monkey-static-tabs-target", runner_factory("monkey-static-tabs-target")),
    ))
    monkeypatch.setattr(gate, "sequential_closeout_report", lambda *args, **kwargs: {
        "phase": "phase8_sequential_closeout",
        "ok": True,
        "issues": [],
        "nextPhase": "phase9_monkey_test_open",
    })
    monkeypatch.setattr(gate, "process_snapshot", lambda: {"processes": []})

    payload = gate.monkey_closeout_report(tmp_path, tmp_path, target="both", write=True)

    assert payload["ok"] is True
    assert payload["phase"] == "phase9_monkey_test_closeout"
    assert payload["nextPhase"] == "phase10_synthetic_open"
    assert payload["summary"]["chain"] == "Input=Sequential / Output=Monkey Test"
    assert payload["summary"]["activeMethod"] == "RealMonkeyTest"
    assert {call[0] for call in calls} == {
        "monkey-data-databanks-resources-options-target",
        "monkey-crosschecks-target",
        "monkey-passive-generation-target",
        "monkey-static-tabs-target",
    }
    assert all(call[1] == "both" and call[2] is False for call in calls)
    assert (tmp_path / ".local" / "sqx142_task_config" / "session_state.json").is_file()
    state = json.loads((tmp_path / ".local" / "sqx142_task_config" / "session_state.json").read_text(encoding="utf-8"))
    assert state["currentPhase"] == "phase9_monkey_test_closeout"
    assert state["nextPhase"] == "phase10_synthetic_open"


def test_synthetic_open_summary_accepts_syntetic_alias_and_flags_pending_cleanup():
    root = ET.fromstring(
        """
        <Settings>
          <Data><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0"><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2" /></Setup></Setups></Data>
          <CustomData><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0"><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" /></Setup></Setups></CustomData>
          <Databanks><Databank name="Input" value="Monkey Test" /><Databank name="Output" value="Syntetic" /></Databanks>
          <WhatToBuild><StrategyType improveDatabank="Strategies to improve" /></WhatToBuild>
          <CrossChecks use="true" evaluateAll="true">
            <MonteCarloRetest use="true">
              <Settings>
                <NumberOfSimulations>100</NumberOfSimulations>
                <MCUseFullSample>true</MCUseFullSample>
                <MCBacktestPrecision>-1</MCBacktestPrecision>
                <Methods>
                  <Method type="RealMonkeyTest" use="false"><Params><Param key="MaxChange">90</Param></Params></Method>
                  <Method type="SyntheticBootstrapV3" use="true"><Params><Param key="BlockSize">20</Param><Param key="WarmupBars">200</Param><Param key="PreservePct">85</Param></Params></Method>
                </Methods>
              </Settings>
              <AcceptanceSettings><Conditions CrossCheck="MonteCarloRetest"><Condition use="true" /></Conditions></AcceptanceSettings>
            </MonteCarloRetest>
            <WhatIf use="false"><Settings><Methods><Method type="ExcludeTradesWithBiggestPl" use="true" /></Methods></Settings></WhatIf>
          </CrossChecks>
        </Settings>
        """
    )

    summary = gate.synthetic_open_summary(root)
    issues, warnings = gate.synthetic_open_issues(summary)

    assert issues == []
    assert summary["alias"]["historical"] == ["Synthetic", "Syntetic"]
    assert summary["activeSyntheticMethod"]["type"] == "SyntheticBootstrapV3"
    assert summary["activeSyntheticMethod"]["params"]["PreservePct"] == "85"
    assert any("inactive crosschecks still carry active methods" in warning for warning in warnings)
    assert any("StrategyType.improveDatabank" in warning for warning in warnings)
    assert any("both Data and CustomData" in warning for warning in warnings)


def test_synthetic_open_report_requires_monkey_closeout_and_writes_phase_state(monkeypatch, tmp_path):
    monkeypatch.setattr(gate, "synthetic_open_target_report", lambda path: {
        "ok": True,
        "taskXml": "AutomaticRetest-Task5.xml",
        "issues": [],
        "warnings": ["pending cleanup"],
        "summary": {
            "databanks": {"Input": "Monkey Test", "Output": "Syntetic"},
            "activeSyntheticMethod": {"type": "SyntheticBootstrapV3"},
        },
    })
    monkeypatch.setattr(gate, "monkey_closeout_report", lambda *args, **kwargs: {
        "phase": "phase9_monkey_test_closeout",
        "ok": True,
        "issues": [],
        "nextPhase": "phase10_synthetic_open",
    })
    monkeypatch.setattr(gate, "process_snapshot", lambda: {"processes": []})

    payload = gate.synthetic_open_report(tmp_path, tmp_path, target="both", write=True)

    assert payload["ok"] is True
    assert payload["phase"] == "phase10_synthetic_open"
    assert payload["nextPhase"] == "phase10_synthetic_data_databanks_resources_options"
    assert payload["previousGate"]["phase"] == "phase9_monkey_test_closeout"
    assert payload["summary"]["taskXml"] == "AutomaticRetest-Task5.xml"
    assert payload["summary"]["actualTaskTitle"] == "Syntetic"
    assert "pending cleanup" in payload["warnings"]
    assert (tmp_path / ".local" / "sqx142_task_config" / "session_state.json").is_file()
    state = json.loads((tmp_path / ".local" / "sqx142_task_config" / "session_state.json").read_text(encoding="utf-8"))
    assert state["currentPhase"] == "phase10_synthetic_open"
    assert state["nextPhase"] == "phase10_synthetic_data_databanks_resources_options"


def test_synthetic_data_databanks_resources_options_keeps_dual_carrier_synced_without_monkey_columns():
    root = ET.fromstring(
        """
        <Settings>
          <Data>
            <Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old" slippage="5" minDist="3" engine="Legacy">
              <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
              <Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">9</Param></Params></Method></Commissions>
            </Setup></Setups>
            <OutOfSample><Range dateFrom="2023.01.01" dateTo="2025.01.01" /></OutOfSample>
          </Data>
          <CustomData>
            <Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old" slippage="5" minDist="3" engine="Legacy">
              <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
              <Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">9</Param></Params></Method></Commissions>
              <MainTestValues engine="false" />
            </Setup></Setups>
          </CustomData>
          <Databanks><Databank name="Input" value="Sequential" /><Databank name="Output" value="Monkey Test" /></Databanks>
          <Resources>
            <Symbols><Symbol name="USDJPY_darwinex" precision="M1" timezone="UTC" broker="4"><InstrumentInfo instrument="USDJPY_darwinex" broker="4" /></Symbol></Symbols>
            <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
            <Instruments />
            <Sessions><Session name="Old" /></Sessions>
            <CustomIndicators />
            <CustomBlocks />
          </Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">true</Param><Param key="RealisticGapsHandling">true</Param><Param key="StoreChartData">true</Param><Param key="Session">Old</Param><Param key="MarketOpenSession">Old</Param></Params></BuildTradingOptions></Options>
        </Settings>
        """
    )

    actions = apply_synthetic_data_databanks_resources_options_to_root(root)

    assert any(item["field"] == "Data/Setup/Chart:attrs" and item["changed"] for item in actions)
    assert enforce_synthetic_data_databanks_resources_options_guard(root) == []
    data_setup = root.find("./Data/Setups/Setup")
    custom_setup = root.find("./CustomData/Setups/Setup")
    assert data_setup.get("dateFrom") == custom_setup.get("dateFrom") == "2017.10.02"
    assert data_setup.get("dateTo") == custom_setup.get("dateTo") == "2023.12.31"
    assert data_setup.get("testPrecision") == custom_setup.get("testPrecision") == "2"
    assert data_setup.find("Chart").get("spread") == custom_setup.find("Chart").get("spread") == "2.0"
    assert root.find("./Data/OutOfSample/Range") is None
    assert {
        databank.get("name"): databank.get("value")
        for databank in root.findall(".//Databanks/Databank")
    } == {"Input": "Monkey Test", "Output": "Syntetic"}
    assert root.find(".//BuildTradingOptions/Params/Param[@key='LimitTimeRange']").text == "false"
    assert root.find(".//Resources/Symbols/Symbol").get("precision") == "TICK"
    assert root.findall(".//Resources/Sessions/Session") == []


def test_synthetic_data_databanks_resources_options_guard_rejects_monkey_or_donor_drift():
    root = ET.fromstring(
        """
        <Settings>
          <Data><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0"><Chart symbol="USDJPY_darwinex" timeframe="H1" spread="2.0" /></Setup></Setups></Data>
          <CustomData><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0"><Chart symbol="AUDCAD_darwinex" timeframe="H4" spread="2.0" /><MainTestValues engine="false" /></Setup></Setups></CustomData>
          <Databanks><Databank name="Input" value="Sequential" /><Databank name="Output" value="Monkey Test" /></Databanks>
          <Resources><Symbols /><Brokers /><Sessions /></Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">true</Param></Params></BuildTradingOptions></Options>
        </Settings>
        """
    )

    issues = enforce_synthetic_data_databanks_resources_options_guard(root)

    assert any("Databank Input" in issue for issue in issues)
    assert any("Databank Output" in issue for issue in issues)
    assert any("chart symbol" in issue for issue in issues)
    assert any("chart mismatch for symbol" in issue for issue in issues)
    assert any("Options param" in issue for issue in issues)
    assert any("Forbidden donor token" in issue for issue in issues)


def test_mc2_crosschecks_apply_adaptive_base_spread_x2_x5_and_clean_inactive_methods():
    root = ET.fromstring(
        """
        <Settings>
          <CustomData>
            <Setups>
              <Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session">
                <Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" />
              </Setup>
            </Setups>
          </CustomData>
          <CrossChecks use="true" evaluateAll="true">
            <MonteCarloManipulation use="false">
              <Settings><Methods><Method type="RandomizeTradesOrder" use="true" /><Method type="RandomlySkipTrades" use="true" /></Methods></Settings>
            </MonteCarloManipulation>
            <MonteCarloRetest use="true">
              <Settings>
                <Methods>
                  <Method type="RandomizeHistoryData" use="true" />
                  <Method type="RandomizeHistoryDataFixedRange" use="true" />
                  <Method type="RandomizeSpread" use="true"><Params><Param key="Min" type="Double">30</Param><Param key="Max" type="Double">50</Param></Params></Method>
                  <Method type="RandomizeSlippage" use="true" />
                </Methods>
                <NumberOfSimulations>50</NumberOfSimulations>
                <MCUseFullSample>false</MCUseFullSample>
              </Settings>
              <AcceptanceSettings>
                <Conditions>
                  <Condition use="true"><Left-Side valueType="column"><Column-Value column="AnnualPctReturnDDRatio" resultType="MonteCarloRetest" confidenceLevel="100" /></Left-Side><Comparator value="&gt;=" /><Right-Side valueType="numeric"><Numeric-Value value="0" /></Right-Side></Condition>
                  <Condition use="true"><Left-Side valueType="column"><Column-Value column="AnnualPctReturnDDRatio" resultType="MonteCarloRetest" confidenceLevel="95" /></Left-Side><Comparator value="&gt;=" /><Right-Side valueType="column"><Column-Value column="AnnualPctReturnDDRatio" resultType="main" pctRatio="30" /></Right-Side></Condition>
                </Conditions>
              </AcceptanceSettings>
            </MonteCarloRetest>
          </CrossChecks>
        </Settings>
        """
    )

    actions = apply_mc2_crosschecks_to_root(root)

    assert any(item["field"].endswith("RandomizeSpread/Min") and item["changed"] for item in actions)
    assert enforce_mc2_crosschecks_guard(root) == []
    methods = {
        method.get("type"): method.get("use")
        for method in root.findall(".//CrossChecks/MonteCarloRetest/Settings/Methods/Method")
    }
    assert methods["RandomizeHistoryData"] == "true"
    assert methods["RandomizeSpread"] == "true"
    assert methods["RandomizeHistoryDataFixedRange"] == "false"
    assert methods["RandomizeSlippage"] == "false"
    assert root.find(".//MonteCarloManipulation/Settings/Methods/Method[@type='RandomizeTradesOrder']").get("use") == "false"
    assert root.find(".//MonteCarloRetest/Settings/NumberOfSimulations").text == "100"
    assert root.find(".//MonteCarloRetest/Settings/MCUseFullSample").text == "true"
    params = {
        param.get("key"): param.text
        for param in root.findall(".//MonteCarloRetest/Settings/Methods/Method[@type='RandomizeSpread']/Params/Param")
    }
    assert params == {"Min": "4", "Max": "10"}


def test_mc2_crosschecks_guard_rejects_extreme_spread_stress():
    root = ET.fromstring(
        """
        <Settings>
          <CustomData><Setups><Setup><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" /></Setup></Setups></CustomData>
          <CrossChecks use="true" evaluateAll="true">
            <MonteCarloRetest use="true">
              <Settings>
                <Methods>
                  <Method type="RandomizeHistoryData" use="true" />
                  <Method type="RandomizeSpread" use="true"><Params><Param key="Min" type="Double">30</Param><Param key="Max" type="Double">50</Param></Params></Method>
                </Methods>
                <NumberOfSimulations>100</NumberOfSimulations>
                <MCUseFullSample>true</MCUseFullSample>
              </Settings>
              <AcceptanceSettings>
                <Conditions>
                  <Condition use="true"><Left-Side valueType="column"><Column-Value column="AnnualPctReturnDDRatio" resultType="MonteCarloRetest" confidenceLevel="100" /></Left-Side><Comparator value="&gt;=" /><Right-Side valueType="numeric"><Numeric-Value value="0" /></Right-Side></Condition>
                  <Condition use="true"><Left-Side valueType="column"><Column-Value column="AnnualPctReturnDDRatio" resultType="MonteCarloRetest" confidenceLevel="95" /></Left-Side><Comparator value="&gt;=" /><Right-Side valueType="column"><Column-Value column="AnnualPctReturnDDRatio" resultType="main" pctRatio="30" /></Right-Side></Condition>
                </Conditions>
              </AcceptanceSettings>
            </MonteCarloRetest>
          </CrossChecks>
        </Settings>
        """
    )

    issues = enforce_mc2_crosschecks_guard(root)

    assert any("RandomizeSpread range" in issue for issue in issues)
    assert any("extreme" in issue for issue in issues)


def test_mc2_data_databanks_resources_options_uses_customdata_chain_and_generator_seed():
    root = ET.fromstring(
        """
        <Settings>
          <Data>
            <Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old Session"><Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" /></Setup></Setups>
            <OutOfSample><Range dateFrom="2023.01.01" dateTo="2025.01.01" /></OutOfSample>
          </Data>
          <CustomData>
            <Setups>
              <Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old Session" slippage="5" minDist="3" engine="MetaTrader5">
                <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
                <Commissions><Method type="SizeBased" use="false"><Params><Param key="Commission">9</Param></Params></Method></Commissions>
                <MainTestValues engine="false" symbol="false" timeframe="false" dates="false" precision="false" distance="false" spread="false" slippage="false" commissions="false" />
              </Setup>
            </Setups>
          </CustomData>
          <Databanks>
            <Databank name="Input" value="TICK" />
            <Databank name="Output" value="MC" />
          </Databanks>
          <Resources>
            <Symbols>
              <Symbol name="USDJPY_darwinex" source="4" precision="M1" timezone="UTC" broker="9">
                <InstrumentInfo instrument="USDJPY_darwinex" defaultSpread="1.4" broker="9" />
              </Symbol>
            </Symbols>
            <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
            <Instruments />
            <Sessions><Session name="Old Session" /></Sessions>
            <CustomIndicators />
            <CustomBlocks />
          </Resources>
          <Options>
            <BuildTradingOptions><Params>
              <Param key="Session">Old Session</Param>
              <Param key="MarketOpenSession">Old Session</Param>
              <Param key="LimitTimeRange">true</Param>
              <Param key="RealisticGapsHandling">true</Param>
              <Param key="StoreChartData">true</Param>
            </Params></BuildTradingOptions>
          </Options>
        </Settings>
        """
    )

    actions = apply_mc2_data_databanks_resources_options_to_root(root)

    assert any(item["field"] == "Data" and item["changed"] for item in actions)
    assert enforce_mc2_data_databanks_resources_options_guard(root) == []
    assert root.find("Data") is None
    setup = root.find("./CustomData/Setups/Setup")
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == "2"
    assert setup.get("session") == "No Session"
    assert setup.get("engine") == "MetaTrader4"
    chart = setup.find("Chart")
    assert chart.get("symbol") == "AUDCAD_darwinex"
    assert chart.get("timeframe") == "H1"
    assert chart.get("spread") == "2.0"
    assert setup.find("./Commissions/Method[@type='SizeBased']").get("use") == "true"
    assert setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']").text == "0.0"
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
    databanks = {node.get("name"): node.get("value") for node in root.findall(".//Databanks/Databank")}
    assert databanks == {"Input": "MC", "Output": "MC2"}
    assert {symbol.get("name") for symbol in root.findall(".//Resources/Symbols/Symbol")} == {"AUDCAD_darwinex"}
    assert root.find(".//Resources/Symbols/Symbol").get("precision") == "TICK"
    assert root.find(".//Resources/Sessions/Session") is None
    options = {
        param.get("key"): param.text
        for param in root.findall(".//BuildTradingOptions/Params/Param")
        if param.get("key") in {"Session", "MarketOpenSession", "LimitTimeRange", "RealisticGapsHandling", "StoreChartData"}
    }
    assert options == {
        "Session": "No Session",
        "MarketOpenSession": "No Session",
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
    }


def test_mc2_data_databanks_resources_options_guard_rejects_parallel_data_and_wrong_chain():
    root = ET.fromstring(
        """
        <Settings>
          <Data><Setups><Setup><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" /></Setup></Setups></Data>
          <CustomData>
            <Setups>
              <Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old Session">
                <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
                <MainTestValues engine="false" />
              </Setup>
            </Setups>
          </CustomData>
          <Databanks><Databank name="Input" value="TICK" /><Databank name="Output" value="MC" /></Databanks>
          <Resources>
            <Symbols><Symbol name="USDJPY_darwinex" precision="M1" timezone="UTC" broker="9"><InstrumentInfo broker="9" /></Symbol></Symbols>
            <Brokers><Broker id="4" /></Brokers>
            <Sessions><Session name="Old Session" /></Sessions>
          </Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">true</Param></Params></BuildTradingOptions></Options>
        </Settings>
        """
    )

    issues = enforce_mc2_data_databanks_resources_options_guard(root)

    assert any("Data section" in issue for issue in issues)
    assert any("CustomData dates" in issue for issue in issues)
    assert any("Databank Input" in issue for issue in issues)
    assert any("precision is not TICK" in issue for issue in issues)
    assert any("session entries" in issue for issue in issues)
    assert any("Options param Session" in issue for issue in issues)
    assert any("Forbidden donor token" in issue for issue in issues)


def test_mc2_passive_and_static_tabs_close_before_sequential():
    root = ET.fromstring(
        """
        <Settings>
          <Data><Setups><Setup><Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" /></Setup></Setups></Data>
          <CustomData>
            <Setups>
              <Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old Session" slippage="5" minDist="3" engine="MetaTrader5">
                <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
                <Commissions><Method type="SizeBased" use="false"><Params><Param key="Commission">9</Param></Params></Method></Commissions>
                <MainTestValues engine="false" symbol="false" timeframe="false" dates="false" precision="false" distance="false" spread="false" slippage="false" commissions="false" />
              </Setup>
            </Setups>
          </CustomData>
          <Databanks><Databank name="Input" value="TICK" /><Databank name="Output" value="MC" /></Databanks>
          <Resources>
            <Symbols><Symbol name="USDJPY_darwinex" precision="M1" timezone="UTC" broker="4"><InstrumentInfo instrument="USDJPY_darwinex" broker="4" /></Symbol></Symbols>
            <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
            <Sessions><Session name="Old Session" /></Sessions>
          </Resources>
          <Options><BuildTradingOptions><Params><Param key="Session">Old Session</Param><Param key="MarketOpenSession">Old Session</Param><Param key="LimitTimeRange">true</Param><Param key="RealisticGapsHandling">true</Param><Param key="StoreChartData">true</Param></Params></BuildTradingOptions></Options>
          <CrossChecks use="false" evaluateAll="false">
            <MonteCarloManipulation use="true"><Settings><Methods><Method type="RandomizeTradesOrder" use="true" /></Methods></Settings></MonteCarloManipulation>
            <MonteCarloRetest use="true">
              <Settings>
                <Methods>
                  <Method type="RandomizeHistoryData" use="false" />
                  <Method type="RandomizeSpread" use="true"><Params><Param key="Min" type="Double">30</Param><Param key="Max" type="Double">50</Param></Params></Method>
                </Methods>
                <NumberOfSimulations>50</NumberOfSimulations>
                <MCUseFullSample>false</MCUseFullSample>
              </Settings>
              <AcceptanceSettings>
                <Conditions>
                  <Condition use="true"><Left-Side valueType="column"><Column-Value column="AnnualPctReturnDDRatio" resultType="MonteCarloRetest" confidenceLevel="100" /></Left-Side><Comparator value="&gt;=" /><Right-Side valueType="numeric"><Numeric-Value value="0" /></Right-Side></Condition>
                  <Condition use="true"><Left-Side valueType="column"><Column-Value column="AnnualPctReturnDDRatio" resultType="MonteCarloRetest" confidenceLevel="95" /></Left-Side><Comparator value="&gt;=" /><Right-Side valueType="column"><Column-Value column="AnnualPctReturnDDRatio" resultType="main" pctRatio="30" /></Right-Side></Condition>
                </Conditions>
              </AcceptanceSettings>
            </MonteCarloRetest>
          </CrossChecks>
          <PartsToImprove improveATM="true">
            <EntryRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></EntryRules>
            <OrderTypes><LongImprovement use="true" /><ShortImprovement use="true" /></OrderTypes>
            <ExitRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="TICK" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>true</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="true" />
              <EvoRestartOnStagnation status="true" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple">
            <BuildingBlocks>
              <Block key="Signals.ADX" category="signals" use="true" probability="1" />
              <Block key="Indicators.ATR" category="indicators" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="true" probability="1" />
            </BuildingBlocks>
            <OrderTypes><Block key="EnterAtMarket" use="false" /><Block key="EnterReverseAtMarket" use="true" /><Block key="EnterAtStop" use="true" /><Block key="EnterAtLimit" use="true" /></OrderTypes>
            <ExitTypes><Block key="ExitAfterBars.ExitAfterBars" use="false" probability="50" /><Block key="ExitAfterDays.ExitAfterDays" use="true" probability="50" /></ExitTypes>
            <CustomData showAll="true"><Item /></CustomData>
          </Blocks>
          <Rankings type="always">
            <MaxStrategies>500</MaxStrategies>
            <ConditionsType>1</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Existing portfolio" />
            <CustomAnalysis filter="true" inputArgs="" method="none" />
            <StopCondition type="passed" passedStrategies="10" restartCount="1" days="1" hours="1" minutes="1" />
            <Conditions><Condition use="true"><Left-Side><Column-Value column="NetProfit" format="Decimal2" sampleType="127" /></Left-Side><Comparator value="&gt;=" /><Right-Side><Numeric-Value value="1" /></Right-Side></Condition></Conditions>
          </Rankings>
          <RiskMoneyManagement><MoneyManagement><Method type="FixedSize" use="false" /><Method type="RiskFixedBalancePct" use="false" /><Method type="RiskFixedPctOfAccount" use="false" /><Method type="FixedAmount" use="true" /><Method type="StocksSizeByPrice" use="false" /></MoneyManagement></RiskMoneyManagement>
          <ATMs enable="true" scaleOutType="1" />
          <Notes>ok</Notes>
          <SelectedStrategies><Strategy id="legacy" /></SelectedStrategies>
        </Settings>
        """
    )

    apply_mc2_data_databanks_resources_options_to_root(root)
    apply_mc2_crosschecks_to_root(root)
    passive_actions = apply_mc2_passive_generation_to_root(root, source_root=root)
    static_actions = apply_mc2_static_tabs_to_root(root)

    assert any(item["field"] == "WhatToBuild/StrategyType" and item["changed"] for item in passive_actions)
    assert any(item["field"] == "Rankings/FitPortfolio" and item["changed"] for item in static_actions)
    assert enforce_mc2_passive_generation_guard(root) == []
    assert enforce_mc2_static_tabs_guard(root) == []
    assert root.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "MC"
    assert root.find(".//SelectedStrategies").text is None
    assert root.find("./Data") is None
    assert root.find("./CustomData/Setups/Setup/MainTestValues").get("symbol") == "true"
    assert root.find(".//CrossChecks/MonteCarloRetest").get("use") == "true"
    assert root.find(".//CrossChecks/MonteCarloManipulation").get("use") == "false"


def test_mc2_static_tabs_guard_rejects_portfolio_fit_rank_filters_and_customdata_drift():
    root = ET.fromstring(
        """
        <Settings>
          <CustomData>
            <Setups>
              <Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old Session">
                <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
                <Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission">9</Param></Params></Method></Commissions>
                <MainTestValues engine="false" />
              </Setup>
            </Setups>
          </CustomData>
          <Rankings type="always">
            <MaxStrategies>500</MaxStrategies>
            <ConditionsType>1</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Existing portfolio" />
            <CustomAnalysis filter="true" inputArgs="" method="none" />
            <Conditions><Condition use="true"><Left-Side><Column-Value column="NetProfit" format="Decimal2" sampleType="127" /></Left-Side><Comparator value="&gt;=" /><Right-Side><Numeric-Value value="1" /></Right-Side></Condition></Conditions>
          </Rankings>
          <RiskMoneyManagement><MoneyManagement><Method type="FixedSize" use="false" /><Method type="FixedAmount" use="true" /></MoneyManagement></RiskMoneyManagement>
          <ATMs enable="true" />
          <SelectedStrategies>legacy</SelectedStrategies>
          <PartsToImprove><EntryRules><LongImprovement use="true" /><ShortImprovement use="false" /></EntryRules></PartsToImprove>
        </Settings>
        """
    )

    issues = enforce_mc2_static_tabs_guard(root)

    assert any("Rankings type" in issue for issue in issues)
    assert any("FitPortfolio" in issue for issue in issues)
    assert any("extra conditions" in issue for issue in issues)
    assert any("RiskMoneyManagement FixedSize" in issue for issue in issues)
    assert any("ATMs enable" in issue for issue in issues)
    assert any("SelectedStrategies" in issue for issue in issues)
    assert any("CustomData testPrecision" in issue for issue in issues)
    assert any("Forbidden donor token" in issue for issue in issues)
    assert any("Passive generation guard" in issue for issue in issues)


def test_sequential_open_summary_accepts_mc2_chain_and_active_sequential_optimization():
    root = ET.fromstring(
        """
        <Settings>
          <Data><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" /></Setups></Data>
          <CustomData><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" /></Setups></CustomData>
          <Databanks><Databank name="Input" value="MC2" /><Databank name="Output" value="Sequential" /></Databanks>
          <WhatToBuild><StrategyType improveDatabank="MC2" improveType="strategy" architecture="sq4" /></WhatToBuild>
          <CrossChecks use="true" evaluateAll="true">
            <SequentialOptimization use="true">
              <Settings>
                <ParameterSettings><DistributionUp>130</DistributionUp><DistributionDown>70</DistributionDown><Steps>12</Steps><ApplyToStrategy>false</ApplyToStrategy></ParameterSettings>
                <WhatToParametrize type="1" symmetricVariables="false"><Periods>true</Periods><Constants>true</Constants><ExitParamsUsed>true</ExitParamsUsed></WhatToParametrize>
              </Settings>
              <AcceptanceSettings><PctToPass>80</PctToPass><ResultsCount>5</ResultsCount><StabilityRange>25</StabilityRange><Conditions /></AcceptanceSettings>
            </SequentialOptimization>
          </CrossChecks>
          <Rankings type="never"><DeleteFailedStrategies>false</DeleteFailedStrategies><ForceRunCrossChecks>false</ForceRunCrossChecks><FitPortfolio active="false" /><CustomAnalysis filter="false" /></Rankings>
        </Settings>
        """
    )

    summary = sequential_open_summary(root)
    issues, warnings = sequential_open_issues(summary)

    assert issues == []
    assert summary["databanks"] == {"Input": "MC2", "Output": "Sequential"}
    assert summary["crossChecks"]["active"] == ["SequentialOptimization"]
    assert summary["crossChecks"]["sequentialOptimization"]["parameterSettings"]["ApplyToStrategy"] == "false"
    assert any("Data and CustomData" in warning for warning in warnings)


def test_sequential_open_issues_reject_wrong_chain_and_apply_to_strategy():
    root = ET.fromstring(
        """
        <Settings>
          <Databanks><Databank name="Input" value="MC" /><Databank name="Output" value="MC2" /></Databanks>
          <WhatToBuild><StrategyType improveDatabank="Legacy" /></WhatToBuild>
          <CrossChecks use="false" evaluateAll="false">
            <MonteCarloRetest use="true" />
            <SequentialOptimization use="true">
              <Settings><ParameterSettings><ApplyToStrategy>true</ApplyToStrategy></ParameterSettings></Settings>
              <AcceptanceSettings><Conditions /></AcceptanceSettings>
            </SequentialOptimization>
          </CrossChecks>
        </Settings>
        """
    )

    issues, warnings = sequential_open_issues(sequential_open_summary(root))

    assert any("Databank Input" in issue for issue in issues)
    assert any("Databank Output" in issue for issue in issues)
    assert any("CrossChecks must stay active" in issue for issue in issues)
    assert any("active crosschecks" in issue for issue in issues)
    assert any("ApplyToStrategy" in issue for issue in issues)
    assert any("StrategyType.improveDatabank" in warning for warning in warnings)


def test_monkey_open_summary_accepts_sequential_chain_and_real_monkey_method():
    root = ET.fromstring(
        """
        <Settings>
          <Data><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" /></Setups></Data>
          <CustomData><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" /></Setups></CustomData>
          <Databanks><Databank name="Input" value="Sequential" /><Databank name="Output" value="Monkey Test" /></Databanks>
          <WhatToBuild><StrategyType improveDatabank="Sequential" improveType="strategy" architecture="sq4" /></WhatToBuild>
          <CrossChecks use="true" evaluateAll="true">
            <MonteCarloRetest use="true">
              <Settings>
                <NumberOfSimulations>200</NumberOfSimulations>
                <MCUseFullSample>true</MCUseFullSample>
                <MCBacktestPrecision>-1</MCBacktestPrecision>
                <Methods>
                  <Method type="RealMonkeyTest" use="true"><Params><Param key="MaxChange" type="Integer">90</Param></Params></Method>
                  <Method type="SyntheticBootstrapV3" use="false" />
                </Methods>
              </Settings>
              <AcceptanceSettings><Conditions CrossCheck="MonteCarloRetest"><Condition use="false" /></Conditions></AcceptanceSettings>
            </MonteCarloRetest>
            <SequentialOptimization use="false" />
          </CrossChecks>
        </Settings>
        """
    )

    summary = monkey_open_summary(root)
    issues, warnings = monkey_open_issues(summary)

    assert issues == []
    assert summary["databanks"] == {"Input": "Sequential", "Output": "Monkey Test"}
    assert summary["crossChecks"]["active"] == ["MonteCarloRetest"]
    assert summary["activeMonkeyMethod"]["type"] == "RealMonkeyTest"
    assert summary["activeMonkeyMethod"]["params"]["MaxChange"] == "90"
    assert any("acceptance filter conditions" in warning for warning in warnings)
    assert any("Data and CustomData" in warning for warning in warnings)


def test_monkey_open_issues_reject_wrong_chain_and_wrong_method():
    root = ET.fromstring(
        """
        <Settings>
          <Databanks><Databank name="Input" value="MC2" /><Databank name="Output" value="Sequential" /></Databanks>
          <WhatToBuild><StrategyType improveDatabank="Legacy" /></WhatToBuild>
          <CrossChecks use="false" evaluateAll="false">
            <MonteCarloRetest use="true">
              <Settings>
                <NumberOfSimulations>100</NumberOfSimulations>
                <MCUseFullSample>false</MCUseFullSample>
                <Methods>
                  <Method type="SyntheticBootstrapV3" use="true"><Params><Param key="MaxChange" type="Integer">50</Param></Params></Method>
                </Methods>
              </Settings>
            </MonteCarloRetest>
            <WhatIf use="true" />
          </CrossChecks>
        </Settings>
        """
    )

    issues, warnings = monkey_open_issues(monkey_open_summary(root))

    assert any("Databank Input" in issue for issue in issues)
    assert any("Databank Output" in issue for issue in issues)
    assert any("CrossChecks must stay active" in issue for issue in issues)
    assert any("active crosschecks" in issue for issue in issues)
    assert any("NumberOfSimulations" in issue for issue in issues)
    assert any("MCUseFullSample" in issue for issue in issues)
    assert any("active methods" in issue for issue in issues)
    assert any("MaxChange" in issue for issue in issues)
    assert any("StrategyType.improveDatabank" in warning for warning in warnings)


def test_monkey_data_databanks_resources_options_keeps_dual_carrier_synced():
    root = ET.fromstring(
        """
        <Settings>
          <Data>
            <Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old" slippage="5" minDist="3" engine="Legacy">
              <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
              <Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">9</Param></Params></Method></Commissions>
            </Setup></Setups>
            <OutOfSample><Range dateFrom="2023.01.01" dateTo="2025.01.01" /></OutOfSample>
          </Data>
          <CustomData>
            <Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old" slippage="5" minDist="3" engine="Legacy">
              <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
              <Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">9</Param></Params></Method></Commissions>
              <MainTestValues engine="false" />
            </Setup></Setups>
          </CustomData>
          <Databanks><Databank name="Input" value="MC2" /><Databank name="Output" value="Sequential" /></Databanks>
          <Resources>
            <Symbols><Symbol name="USDJPY_darwinex" precision="M1" timezone="UTC" broker="4"><InstrumentInfo instrument="USDJPY_darwinex" broker="4" /></Symbol></Symbols>
            <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
            <Instruments />
            <Sessions><Session name="Old" /></Sessions>
            <CustomIndicators />
            <CustomBlocks />
          </Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">true</Param><Param key="RealisticGapsHandling">true</Param><Param key="StoreChartData">true</Param><Param key="Session">Old</Param><Param key="MarketOpenSession">Old</Param></Params></BuildTradingOptions></Options>
        </Settings>
        """
    )

    actions = apply_monkey_data_databanks_resources_options_to_root(root)

    assert any(item["field"] == "Data/Setup/Chart:attrs" and item["changed"] for item in actions)
    assert enforce_monkey_data_databanks_resources_options_guard(root) == []
    data_setup = root.find("./Data/Setups/Setup")
    custom_setup = root.find("./CustomData/Setups/Setup")
    assert data_setup.get("dateFrom") == custom_setup.get("dateFrom") == "2017.10.02"
    assert data_setup.find("Chart").get("spread") == custom_setup.find("Chart").get("spread") == "2.0"
    assert root.find("./Data/OutOfSample/Range") is None
    assert {
        databank.get("name"): databank.get("value")
        for databank in root.findall(".//Databanks/Databank")
    } == {"Input": "Sequential", "Output": "Monkey Test"}
    assert root.find(".//BuildTradingOptions/Params/Param[@key='LimitTimeRange']").text == "false"
    assert root.find(".//Resources/Symbols/Symbol").get("precision") == "TICK"
    assert root.findall(".//Resources/Sessions/Session") == []


def test_monkey_data_databanks_resources_options_guard_rejects_divergent_carriers():
    root = ET.fromstring(
        """
        <Settings>
          <Data><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0"><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" /></Setup></Setups></Data>
          <CustomData><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0"><Chart symbol="AUDCAD_darwinex" timeframe="H4" spread="2.0" /><MainTestValues engine="false" /></Setup></Setups></CustomData>
          <Databanks><Databank name="Input" value="MC2" /><Databank name="Output" value="Monkey Test" /></Databanks>
          <Resources><Symbols /><Brokers /><Sessions /></Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">true</Param></Params></BuildTradingOptions></Options>
        </Settings>
        """
    )

    issues = enforce_monkey_data_databanks_resources_options_guard(root)

    assert any("chart mismatch for timeframe" in issue for issue in issues)
    assert any("CustomData MainTestValues" in issue for issue in issues)
    assert any("Databank Input" in issue for issue in issues)
    assert any("Options param" in issue for issue in issues)


def _monkey_data_gate_fixture() -> str:
    return """
      <Data>
        <Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0" engine="MetaTrader5 (hedged)">
          <Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" />
          <Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">0.0</Param></Params></Method></Commissions>
        </Setup></Setups>
      </Data>
      <CustomData>
        <Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0" engine="MetaTrader4">
          <Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" />
          <Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">0.0</Param></Params></Method></Commissions>
          <MainTestValues engine="true" symbol="true" timeframe="true" dates="true" subcharts="false" precision="true" distance="true" spread="true" slippage="true" commissions="true" />
        </Setup></Setups>
      </CustomData>
      <Databanks><Databank name="Input" value="Sequential" /><Databank name="Output" value="Monkey Test" /></Databanks>
      <Resources>
        <Symbols><Symbol name="AUDCAD_darwinex" precision="TICK" timezone="EETUS" broker="4"><InstrumentInfo instrument="AUDCAD_darwinex" broker="4" /></Symbol></Symbols>
        <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
        <Instruments><InstrumentInfo instrument="AUDCAD_darwinex" broker="4" /></Instruments>
        <Sessions />
      </Resources>
      <Options><BuildTradingOptions><Params>
        <Param key="LimitTimeRange">false</Param>
        <Param key="RealisticGapsHandling">false</Param>
        <Param key="StoreChartData">false</Param>
        <Param key="Session">No Session</Param>
        <Param key="MarketOpenSession">No Session</Param>
      </Params></BuildTradingOptions></Options>
    """


def _synthetic_data_gate_fixture() -> str:
    return _monkey_data_gate_fixture().replace(
        '<Databank name="Input" value="Sequential" /><Databank name="Output" value="Monkey Test" />',
        '<Databank name="Input" value="Monkey Test" /><Databank name="Output" value="Syntetic" />',
    )


def test_monkey_crosschecks_activates_real_monkey_filters_and_cleans_synthetic_or_disabled_methods():
    root = ET.fromstring(
        f"""
        <Settings>
          {_monkey_data_gate_fixture()}
          <CrossChecks use="false" evaluateAll="false">
            <RetestOnAdditionalMarkets use="true">
              <Settings><Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old" slippage="5" minDist="2">
                <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
              </Setup></Setups></Settings>
            </RetestOnAdditionalMarkets>
            <MonteCarloRetest use="false">
              <Settings>
                <NumberOfSimulations>50</NumberOfSimulations>
                <MCUseFullSample>false</MCUseFullSample>
                <MCBacktestPrecision>2</MCBacktestPrecision>
                <Methods>
                  <Method type="RealMonkeyTest" use="false"><Params><Param key="MaxChange" type="Integer">50</Param></Params></Method>
                  <Method type="SyntheticBootstrapV3" use="true"><Params><Param key="PreservePct">85</Param></Params></Method>
                  <Method type="RandomizeSpread" use="true"><Params><Param key="Min">1</Param><Param key="Max">5</Param></Params></Method>
                </Methods>
              </Settings>
              <AcceptanceSettings><Conditions CrossCheck="MonteCarloRetest">
                <Condition use="false" />
              </Conditions></AcceptanceSettings>
            </MonteCarloRetest>
            <MonteCarloManipulation use="false">
              <Settings><Methods><Method type="RandomizeTradesOrder" use="true" /><Method type="RandomlySkipTrades" use="true" /></Methods></Settings>
            </MonteCarloManipulation>
            <WhatIf use="false">
              <Settings><Methods><Method type="ExcludeTradesWithBiggestPl" use="true" /></Methods></Settings>
            </WhatIf>
          </CrossChecks>
          <Rankings><ForceRunCrossChecks>false</ForceRunCrossChecks></Rankings>
        </Settings>
        """
    )

    actions = apply_monkey_crosschecks_to_root(root)

    assert any(item["field"] == "CrossChecks:attrs" and item["changed"] for item in actions)
    assert any(item["field"] == "CrossChecks/MonteCarloRetest/Method:SyntheticBootstrapV3:use" and item["changed"] for item in actions)
    assert enforce_monkey_crosschecks_guard(root) == []
    summary = monkey_crosschecks_summary(root)
    assert summary["active"] == ["MonteCarloRetest"]
    monte_carlo = next(item for item in summary["checks"] if item["id"] == "MonteCarloRetest")
    assert monte_carlo["numberOfSimulations"] == "200"
    assert monte_carlo["mcUseFullSample"] == "true"
    assert monte_carlo["mcBacktestPrecision"] == "-1"
    assert monte_carlo["activeMethodTypes"] == ["RealMonkeyTest"]
    methods = {item["type"]: item for item in monte_carlo["methods"]}
    assert methods["RealMonkeyTest"]["params"]["MaxChange"] == "90"
    assert methods["SyntheticBootstrapV3"]["use"] == "false"
    conditions = monte_carlo["conditions"]
    assert [condition["use"] for condition in conditions] == ["true", "true"]
    assert conditions[0]["left"]["column"] == "NetProfit"
    assert conditions[0]["right"]["pctRatio"] == "50"
    assert conditions[1]["left"]["column"] == "DrawdownPct"
    assert conditions[1]["right"]["pctRatio"] == "200"
    inactive_methods = [
        method
        for check in summary["checks"]
        if check["id"] != "MonteCarloRetest"
        for method in check["methods"]
    ]
    assert all(method["use"] == "false" for method in inactive_methods)
    setup = root.find(".//CrossChecks/RetestOnAdditionalMarkets/Settings/Setups/Setup")
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == "2"
    assert setup.find("Chart").attrib == {"symbol": "AUDCAD_darwinex", "timeframe": "H1", "spread": "2.0"}


def test_monkey_crosschecks_guard_rejects_inactive_filters_synthetic_method_and_force_run():
    root = ET.fromstring(
        f"""
        <Settings>
          {_monkey_data_gate_fixture()}
          <CrossChecks use="true" evaluateAll="true">
            <MonteCarloRetest use="true">
              <Settings>
                <NumberOfSimulations>200</NumberOfSimulations>
                <MCUseFullSample>true</MCUseFullSample>
                <MCBacktestPrecision>-1</MCBacktestPrecision>
                <Methods>
                  <Method type="RealMonkeyTest" use="true"><Params><Param key="MaxChange" type="Integer">90</Param></Params></Method>
                  <Method type="SyntheticBootstrapV3" use="true" />
                </Methods>
              </Settings>
              <AcceptanceSettings><Conditions CrossCheck="MonteCarloRetest">
                <Condition use="false" />
              </Conditions></AcceptanceSettings>
            </MonteCarloRetest>
            <MonteCarloManipulation use="false">
              <Settings><Methods><Method type="RandomizeTradesOrder" use="true" /></Methods></Settings>
            </MonteCarloManipulation>
          </CrossChecks>
          <Rankings><ForceRunCrossChecks>true</ForceRunCrossChecks></Rankings>
        </Settings>
        """
    )

    issues = enforce_monkey_crosschecks_guard(root)

    assert any("active methods" in issue for issue in issues)
    assert any("acceptance conditions" in issue for issue in issues)
    assert any("still has active methods" in issue for issue in issues)
    assert any("ForceRunCrossChecks" in issue for issue in issues)


def test_synthetic_crosschecks_activates_bootstrap_filters_and_cleans_monkey_or_disabled_methods():
    root = ET.fromstring(
        f"""
        <Settings>
          {_synthetic_data_gate_fixture()}
          <CrossChecks use="false" evaluateAll="false">
            <RetestOnAdditionalMarkets use="true">
              <Settings><Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old" slippage="5" minDist="2">
                <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
              </Setup></Setups></Settings>
            </RetestOnAdditionalMarkets>
            <MonteCarloRetest use="false">
              <Settings>
                <NumberOfSimulations>50</NumberOfSimulations>
                <MCUseFullSample>false</MCUseFullSample>
                <MCBacktestPrecision>2</MCBacktestPrecision>
                <Methods>
                  <Method type="RealMonkeyTest" use="true"><Params><Param key="MaxChange" type="Integer">90</Param></Params></Method>
                  <Method type="SyntheticBootstrapV3" use="false"><Params><Param key="BlockSize">10</Param><Param key="WarmupBars">50</Param><Param key="PreservePct">60</Param></Params></Method>
                  <Method type="RandomizeSpread" use="true"><Params><Param key="Min">1</Param><Param key="Max">5</Param></Params></Method>
                </Methods>
              </Settings>
              <AcceptanceSettings><Conditions CrossCheck="MonteCarloRetest">
                <Condition use="false" />
              </Conditions></AcceptanceSettings>
            </MonteCarloRetest>
            <MonteCarloManipulation use="false">
              <Settings><Methods><Method type="RandomizeTradesOrder" use="true" /><Method type="RandomlySkipTrades" use="true" /></Methods></Settings>
            </MonteCarloManipulation>
            <WhatIf use="false">
              <Settings><Methods><Method type="ExcludeTradesWithBiggestPl" use="true" /></Methods></Settings>
            </WhatIf>
          </CrossChecks>
          <Rankings><ForceRunCrossChecks>false</ForceRunCrossChecks></Rankings>
        </Settings>
        """
    )

    actions = apply_synthetic_crosschecks_to_root(root)

    assert any(item["field"] == "CrossChecks:attrs" and item["changed"] for item in actions)
    assert any(item["field"] == "CrossChecks/MonteCarloRetest/Method:RealMonkeyTest:use" and item["changed"] for item in actions)
    assert enforce_synthetic_crosschecks_guard(root) == []
    summary = monkey_crosschecks_summary(root)
    assert summary["active"] == ["MonteCarloRetest"]
    monte_carlo = next(item for item in summary["checks"] if item["id"] == "MonteCarloRetest")
    assert monte_carlo["numberOfSimulations"] == "100"
    assert monte_carlo["mcUseFullSample"] == "true"
    assert monte_carlo["mcBacktestPrecision"] == "-1"
    assert monte_carlo["activeMethodTypes"] == ["SyntheticBootstrapV3"]
    methods = {item["type"]: item for item in monte_carlo["methods"]}
    assert methods["RealMonkeyTest"]["use"] == "false"
    assert methods["SyntheticBootstrapV3"]["params"] == {
        "BlockSize": "20",
        "WarmupBars": "200",
        "PreservePct": "85",
    }
    conditions = monte_carlo["conditions"]
    assert len(conditions) == 1
    assert conditions[0]["use"] == "true"
    assert conditions[0]["left"]["column"] == "NetProfit"
    assert conditions[0]["left"]["confidenceLevel"] == "85"
    assert conditions[0]["comparator"] == "<="
    assert conditions[0]["right"]["resultType"] == "main"
    assert conditions[0]["right"]["pctRatio"] == "0"
    inactive_methods = [
        method
        for check in summary["checks"]
        if check["id"] != "MonteCarloRetest"
        for method in check["methods"]
    ]
    assert all(method["use"] == "false" for method in inactive_methods)
    setup = root.find(".//CrossChecks/RetestOnAdditionalMarkets/Settings/Setups/Setup")
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == "2"
    assert setup.find("Chart").attrib == {"symbol": "AUDCAD_darwinex", "timeframe": "H1", "spread": "2.0"}


def test_synthetic_crosschecks_guard_rejects_monkey_method_inactive_filters_and_force_run():
    root = ET.fromstring(
        f"""
        <Settings>
          {_synthetic_data_gate_fixture()}
          <CrossChecks use="true" evaluateAll="true">
            <MonteCarloRetest use="true">
              <Settings>
                <NumberOfSimulations>100</NumberOfSimulations>
                <MCUseFullSample>true</MCUseFullSample>
                <MCBacktestPrecision>-1</MCBacktestPrecision>
                <Methods>
                  <Method type="SyntheticBootstrapV3" use="true"><Params><Param key="BlockSize" type="Integer">20</Param><Param key="WarmupBars" type="Integer">200</Param><Param key="PreservePct" type="Integer">85</Param></Params></Method>
                  <Method type="RealMonkeyTest" use="true" />
                </Methods>
              </Settings>
              <AcceptanceSettings><Conditions CrossCheck="MonteCarloRetest">
                <Condition use="false" />
              </Conditions></AcceptanceSettings>
            </MonteCarloRetest>
            <MonteCarloManipulation use="false">
              <Settings><Methods><Method type="RandomizeTradesOrder" use="true" /></Methods></Settings>
            </MonteCarloManipulation>
          </CrossChecks>
          <Rankings><ForceRunCrossChecks>true</ForceRunCrossChecks></Rankings>
        </Settings>
        """
    )

    issues = enforce_synthetic_crosschecks_guard(root)

    assert any("active methods" in issue for issue in issues)
    assert any("acceptance conditions" in issue for issue in issues)
    assert any("still has active methods" in issue for issue in issues)
    assert any("ForceRunCrossChecks" in issue for issue in issues)


def test_synthetic_passive_generation_points_to_monkey_and_preserves_indicator_universe():
    root = ET.fromstring(
        f"""
        <Settings>
          {_synthetic_data_gate_fixture()}
          <CrossChecks use="true" evaluateAll="true">
            <MonteCarloRetest use="true">
              <Settings>
                <NumberOfSimulations>100</NumberOfSimulations>
                <MCUseFullSample>true</MCUseFullSample>
                <MCBacktestPrecision>-1</MCBacktestPrecision>
                <Methods>
                  <Method type="SyntheticBootstrapV3" use="true"><Params><Param key="BlockSize" type="Integer">20</Param><Param key="WarmupBars" type="Integer">200</Param><Param key="PreservePct" type="Integer">85</Param></Params></Method>
                </Methods>
              </Settings>
              <AcceptanceSettings><Conditions CrossCheck="MonteCarloRetest">
                <Condition use="true"><Left-Side valueType="column"><Column-Value column="NetProfit" columnType="0" format="Decimal2PL" resultType="MonteCarloRetest" direction="0" sampleType="10" plType="10" confidenceLevel="85" market="1" subresult="30" pctRatio="0" class="NetProfit" /></Left-Side><Comparator value="&lt;=" /><Right-Side valueType="column"><Column-Value column="NetProfit" columnType="0" format="Decimal2PL" resultType="main" direction="0" sampleType="127" plType="10" confidenceLevel="90" market="1" subresult="30" pctRatio="0" class="NetProfit" /></Right-Side></Condition>
              </Conditions></AcceptanceSettings>
            </MonteCarloRetest>
          </CrossChecks>
          <Rankings><ForceRunCrossChecks>false</ForceRunCrossChecks></Rankings>
          <PartsToImprove>
            <EntryRules><LongImprovement use="true" /><ShortImprovement use="true" /></EntryRules>
            <OrderTypes><LongImprovement use="true" /><ShortImprovement use="true" /></OrderTypes>
            <ExitRules><LongImprovement use="true" /><ShortImprovement use="true" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>true</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="true" />
              <EvoRestartOnStagnation status="true" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="legacy" version="old">
            <BuildingBlocks>
              <Block key="Signals.CCI" category="signals" use="true" />
              <Block key="Indicators.ATR" category="indicators" use="true" />
              <Block key="StopLimit.ATR" category="stopLimitBlocks" use="true" />
            </BuildingBlocks>
            <OrderTypes>
              <Block key="EnterAtMarket" use="false" />
              <Block key="EnterReverseAtMarket" use="true" />
              <Block key="EnterAtStop" use="true" />
              <Block key="EnterAtLimit" use="true" />
            </OrderTypes>
            <ExitTypes>
              <Block key="ExitAfterBars.ExitAfterBars" use="false" probability="25"><Value key="undefined" use="false" /></Block>
              <Block key="ExitAfterDays.ExitAfterDays" use="true" probability="100" />
              <Block key="StopLoss" use="true" probability="1" />
            </ExitTypes>
            <CustomData showAll="true"><External /></CustomData>
          </Blocks>
        </Settings>
        """
    )

    actions = apply_synthetic_passive_generation_to_root(root, source_root=root)

    assert any(item["field"] == "WhatToBuild/StrategyType" and item["changed"] for item in actions)
    assert enforce_synthetic_passive_generation_guard(root) == []
    strategy_type = root.find("./WhatToBuild/StrategyType")
    assert strategy_type.get("improveDatabank") == "Monkey Test"
    build_mode = root.find("./WhatToBuild/BuildMode")
    assert build_mode.findtext("ShowLastGenerationDatabank") == "false"
    assert build_mode.find("EvoRestartOnFinish").get("status") == "false"
    assert build_mode.find("EvoRestartOnStagnation").get("status") == "false"
    blocks = root.find("./Blocks")
    assert blocks.get("version") == "142.2336"
    assert blocks.find("./BuildingBlocks/Block[@key='Indicators.ATR']").get("use") == "true"
    assert blocks.find("./BuildingBlocks/Block[@key='Signals.CCI']").get("use") == "false"
    assert blocks.find("./BuildingBlocks/Block[@key='StopLimit.ATR']").get("use") == "false"
    assert blocks.find("./OrderTypes/Block[@key='EnterAtMarket']").get("use") == "true"
    assert blocks.find("./ExitTypes/Block[@key='ExitAfterBars.ExitAfterBars']").get("probability") == "100"
    assert "ExitAfterDays" not in ET.tostring(blocks, encoding="unicode")
    assert list(blocks.find("./CustomData")) == []


def test_synthetic_passive_generation_guard_rejects_generation_remnants_and_day_exits():
    root = ET.fromstring(
        f"""
        <Settings>
          {_synthetic_data_gate_fixture()}
          <CrossChecks use="true" evaluateAll="true">
            <MonteCarloRetest use="true">
              <Settings>
                <NumberOfSimulations>100</NumberOfSimulations>
                <MCUseFullSample>true</MCUseFullSample>
                <MCBacktestPrecision>-1</MCBacktestPrecision>
                <Methods>
                  <Method type="SyntheticBootstrapV3" use="true"><Params><Param key="BlockSize" type="Integer">20</Param><Param key="WarmupBars" type="Integer">200</Param><Param key="PreservePct" type="Integer">85</Param></Params></Method>
                </Methods>
              </Settings>
              <AcceptanceSettings><Conditions CrossCheck="MonteCarloRetest">
                <Condition use="true"><Left-Side valueType="column"><Column-Value column="NetProfit" columnType="0" format="Decimal2PL" resultType="MonteCarloRetest" direction="0" sampleType="10" plType="10" confidenceLevel="85" market="1" subresult="30" pctRatio="0" class="NetProfit" /></Left-Side><Comparator value="&lt;=" /><Right-Side valueType="column"><Column-Value column="NetProfit" columnType="0" format="Decimal2PL" resultType="main" direction="0" sampleType="127" plType="10" confidenceLevel="90" market="1" subresult="30" pctRatio="0" class="NetProfit" /></Right-Side></Condition>
              </Conditions></AcceptanceSettings>
            </MonteCarloRetest>
          </CrossChecks>
          <Rankings><ForceRunCrossChecks>false</ForceRunCrossChecks></Rankings>
          <PartsToImprove>
            <EntryRules><LongImprovement use="true" /><ShortImprovement use="false" /></EntryRules>
            <OrderTypes><LongImprovement use="false" /><ShortImprovement use="false" /></OrderTypes>
            <ExitRules><LongImprovement use="false" /><ShortImprovement use="false" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>false</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>false</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="false" />
              <EvoRestartOnStagnation status="false" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple" version="142.2336">
            <BuildingBlocks>
              <Block key="Signals.CCI" category="signals" use="true" />
              <Block key="Indicators.ATR" category="indicators" use="true" />
              <Block key="StopLimit.ATR" category="stopLimitBlocks" use="true" />
            </BuildingBlocks>
            <OrderTypes><Block key="EnterAtMarket" use="false" /><Block key="EnterReverseAtMarket" use="true" /><Block key="EnterAtStop" use="true" /><Block key="EnterAtLimit" use="true" /></OrderTypes>
            <ExitTypes><Block key="ExitAfterBars.ExitAfterBars" use="true" probability="50" /><Block key="ExitAfterDays.ExitAfterDays" use="true" probability="100" /></ExitTypes>
            <CustomData showAll="true"><External /></CustomData>
          </Blocks>
        </Settings>
        """
    )

    issues = enforce_synthetic_passive_generation_guard(root)

    assert any("EntryRules/LongImprovement" in issue for issue in issues)
    assert any("StrategyType" in issue for issue in issues)
    assert any("ShowLastGenerationDatabank" in issue for issue in issues)
    assert any("order types" in issue for issue in issues)
    assert any("ExitAfterBars probability" in issue for issue in issues)
    assert any("day-based" in issue for issue in issues)
    assert any("signals" in issue for issue in issues)
    assert any("stop/limit" in issue for issue in issues)
    assert any("CustomData" in issue for issue in issues)
    assert any("Strategies to improve" in issue for issue in issues)


def test_synthetic_static_tabs_closes_rankings_risk_and_customdata_without_turning_off_bootstrap():
    root = ET.fromstring(
        f"""
        <Settings>
          {_synthetic_data_gate_fixture()}
          <CrossChecks use="false" evaluateAll="false">
            <MonteCarloRetest use="false">
              <Settings>
                <NumberOfSimulations>50</NumberOfSimulations>
                <MCUseFullSample>false</MCUseFullSample>
                <MCBacktestPrecision>2</MCBacktestPrecision>
                <Methods>
                  <Method type="RealMonkeyTest" use="true" />
                  <Method type="SyntheticBootstrapV3" use="false"><Params><Param key="BlockSize">10</Param><Param key="WarmupBars">50</Param><Param key="PreservePct">60</Param></Params></Method>
                </Methods>
              </Settings>
              <AcceptanceSettings><Conditions CrossCheck="MonteCarloRetest"><Condition use="false" /></Conditions></AcceptanceSettings>
            </MonteCarloRetest>
          </CrossChecks>
          <PartsToImprove>
            <EntryRules><LongImprovement use="true" /><ShortImprovement use="true" /></EntryRules>
            <OrderTypes><LongImprovement use="true" /><ShortImprovement use="true" /></OrderTypes>
            <ExitRules><LongImprovement use="true" /><ShortImprovement use="true" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>true</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="true" />
              <EvoRestartOnStagnation status="true" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple">
            <BuildingBlocks>
              <Block key="Signals.ADX" category="signals" use="true" probability="1" />
              <Block key="Indicators.ATR" category="indicators" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="true" probability="1" />
            </BuildingBlocks>
            <OrderTypes><Block key="EnterAtMarket" use="false" /><Block key="EnterReverseAtMarket" use="true" /><Block key="EnterAtStop" use="true" /><Block key="EnterAtLimit" use="true" /></OrderTypes>
            <ExitTypes><Block key="ExitAfterBars.ExitAfterBars" use="false" probability="50" /></ExitTypes>
            <CustomData showAll="true"><Item /></CustomData>
          </Blocks>
          <Rankings type="always">
            <MaxStrategies>500</MaxStrategies>
            <ConditionsType>1</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Existing portfolio" />
            <CustomAnalysis filter="true" inputArgs="" method="SyntheticStressTest" />
            <Conditions><Condition use="true"><Left-Side><Column-Value column="NetProfit" /></Left-Side><Comparator value="&gt;=" /><Right-Side><Numeric-Value value="1" /></Right-Side></Condition></Conditions>
          </Rankings>
          <RiskMoneyManagement><MoneyManagement><Method type="FixedSize" use="false" /><Method type="FixedAmount" use="true" /></MoneyManagement></RiskMoneyManagement>
          <ATMs enable="true" />
          <Notes>ok</Notes>
          <SelectedStrategies><Strategy id="legacy" /></SelectedStrategies>
        </Settings>
        """
    )

    apply_synthetic_crosschecks_to_root(root)
    apply_synthetic_passive_generation_to_root(root, source_root=root)
    actions = apply_synthetic_static_tabs_to_root(root)

    assert any(item["field"] == "Rankings/FitPortfolio" and item["changed"] for item in actions)
    assert enforce_synthetic_static_tabs_guard(root) == []
    assert root.find(".//CrossChecks/MonteCarloRetest").get("use") == "true"
    assert root.find(".//CrossChecks/MonteCarloRetest/Settings/Methods/Method[@type='SyntheticBootstrapV3']").get("use") == "true"
    assert root.find(".//Rankings").get("type") == "never"
    assert root.find(".//Rankings/DeleteFailedStrategies").text == "false"
    assert root.find(".//Rankings/ForceRunCrossChecks").text == "false"
    assert root.find(".//Rankings/FitPortfolio").get("active") == "false"
    assert root.find(".//Rankings/CustomAnalysis").get("filter") == "false"
    assert root.find(".//Rankings/CustomAnalysis").get("method") == "none"
    assert root.find(".//RiskMoneyManagement//Method[@type='FixedSize']").get("use") == "true"
    assert root.find(".//ATMs").get("enable") == "false"
    assert root.find(".//SelectedStrategies").text is None
    assert root.find("./CustomData/Setups/Setup/MainTestValues").get("symbol") == "true"


def test_synthetic_static_tabs_guard_rejects_portfolio_filters_and_customdata_drift():
    root = ET.fromstring(
        f"""
        <Settings>
          {_synthetic_data_gate_fixture()}
          <CrossChecks use="true" evaluateAll="true">
            <MonteCarloRetest use="true">
              <Settings>
                <NumberOfSimulations>100</NumberOfSimulations>
                <MCUseFullSample>true</MCUseFullSample>
                <MCBacktestPrecision>-1</MCBacktestPrecision>
                <Methods><Method type="SyntheticBootstrapV3" use="true"><Params><Param key="BlockSize" type="Integer">20</Param><Param key="WarmupBars" type="Integer">200</Param><Param key="PreservePct" type="Integer">85</Param></Params></Method></Methods>
              </Settings>
              <AcceptanceSettings><Conditions CrossCheck="MonteCarloRetest">
                <Condition use="true"><Left-Side valueType="column"><Column-Value column="NetProfit" columnType="0" format="Decimal2PL" resultType="MonteCarloRetest" direction="0" sampleType="10" plType="10" confidenceLevel="85" market="1" subresult="30" pctRatio="0" class="NetProfit" /></Left-Side><Comparator value="&lt;=" /><Right-Side valueType="column"><Column-Value column="NetProfit" columnType="0" format="Decimal2PL" resultType="main" direction="0" sampleType="127" plType="10" confidenceLevel="90" market="1" subresult="30" pctRatio="0" class="NetProfit" /></Right-Side></Condition>
              </Conditions></AcceptanceSettings>
            </MonteCarloRetest>
          </CrossChecks>
          <PartsToImprove improveATM="false">
            <EntryRules symmetry="false"><LongImprovement use="false" action="replace" /><ShortImprovement use="false" action="replace" /></EntryRules>
            <OrderTypes><LongImprovement use="false" /><ShortImprovement use="false" /></OrderTypes>
            <ExitRules symmetry="false"><LongImprovement use="false" action="replace" /><ShortImprovement use="false" action="replace" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Monkey Test" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>false</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>false</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>false</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="false" />
              <EvoRestartOnStagnation status="false" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple" version="142.2336">
            <BuildingBlocks><Block key="Indicators.ATR" category="indicators" use="true" probability="1" /></BuildingBlocks>
            <OrderTypes><Block key="EnterAtMarket" use="true" /><Block key="EnterReverseAtMarket" use="false" /><Block key="EnterAtStop" use="false" /><Block key="EnterAtLimit" use="false" /></OrderTypes>
            <ExitTypes><Block key="ExitAfterBars.ExitAfterBars" use="true" probability="100" /></ExitTypes>
            <CustomData showAll="false" />
          </Blocks>
          <Rankings type="always">
            <MaxStrategies>500</MaxStrategies>
            <ConditionsType>1</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Existing portfolio" />
            <CustomAnalysis filter="true" inputArgs="" method="SyntheticStressTest" />
            <Conditions><Condition use="true"><Left-Side><Column-Value column="NetProfit" format="Decimal2" sampleType="127" /></Left-Side><Comparator value="&gt;=" /><Right-Side><Numeric-Value value="1" /></Right-Side></Condition></Conditions>
          </Rankings>
          <RiskMoneyManagement><MoneyManagement><Method type="FixedSize" use="false" /><Method type="FixedAmount" use="true" /></MoneyManagement></RiskMoneyManagement>
          <ATMs enable="true" />
          <SelectedStrategies>legacy</SelectedStrategies>
        </Settings>
        """
    )
    setup = root.find("./CustomData/Setups/Setup")
    setup.set("testPrecision", "1")
    setup.find("Chart").set("symbol", "USDJPY_darwinex")
    setup.find("MainTestValues").set("symbol", "false")

    issues = enforce_synthetic_static_tabs_guard(root)

    assert any("Rankings type" in issue for issue in issues)
    assert any("FitPortfolio" in issue for issue in issues)
    assert any("extra conditions" in issue for issue in issues)
    assert any("RiskMoneyManagement FixedSize" in issue for issue in issues)
    assert any("ATMs enable" in issue for issue in issues)
    assert any("SelectedStrategies" in issue for issue in issues)
    assert any("CustomData testPrecision" in issue for issue in issues)
    assert any("CustomData MainTestValues" in issue for issue in issues)
    assert any("Forbidden donor token" in issue for issue in issues)


def _capa2_planning_target_summary(exit_after_bars_build: str = "false") -> dict:
    return {
        "path": "Capa2_Base.cfx",
        "exists": True,
        "isZip": True,
        "sha256": "abc",
        "tasks": {
            "Build": {
                "exists": True,
                "exitTypes": {
                    "StopLoss.StopLoss": "true",
                    "ProfitTarget.ProfitTarget": "true",
                    "TrailingStop.TrailingStop": "true",
                    "ExitAfterBars.ExitAfterBars": exit_after_bars_build,
                },
                "strategyType": {"type": "template", "templateFile": ""},
                "orderTypes": {
                    "EnterAtMarket": "true",
                    "EnterReverseAtMarket": "false",
                    "EnterAtStop": "false",
                    "EnterAtLimit": "false",
                },
            },
            "RETEST 0": {
                "exists": True,
                "exitTypes": {"ExitAfterBars.ExitAfterBars": "true"},
                "strategyType": {},
                "orderTypes": {},
            },
            "MC": {
                "exists": True,
                "exitTypes": {"ExitAfterBars.ExitAfterBars": "true"},
                "strategyType": {},
                "orderTypes": {},
            },
        },
    }


def test_capa2_planning_report_writes_phase15_without_mutating_targets(monkeypatch, tmp_path):
    monkeypatch.setattr(gate, "capa1_closeout_report", lambda *args, **kwargs: {
        "phase": "phase14_capa1_closeout",
        "ok": True,
        "issues": [],
        "nextPhase": "phase15_capa2_planning",
    })
    monkeypatch.setattr(gate, "process_snapshot", lambda: {"processes": []})
    monkeypatch.setattr(gate, "capa2_target_contract_summary", lambda path: _capa2_planning_target_summary())
    monkeypatch.setattr(gate, "capa2_generator_profile_summary", lambda project_root: {
        "path": "generator_profiles.json",
        "exists": True,
        "tradingTimeRangesCapa2": {},
        "disableTradingTimeRangesLayer2": [],
        "taskPeriodMapsLayer2": {
            "Build-Task1.xml": {},
            "Retest-Task1.xml": {},
            "AutomaticRetest-Task7.xml": {},
            "Retest-Task2.xml": {},
        },
        "adaptiveSpreadStressLayer2": {},
        "capa2Profile": {},
    })
    monkeypatch.setattr(gate, "capa2_blocksettings_summary", lambda: {
        "manifest": "blocksettings_manifest.json",
        "mode": "reference_only_traceability",
        "recommendations": {"H1": "BS_Filtros_v6"},
        "inspected": [{
            "canonicalId": "BS_Filtros_v6",
            "filename": "BS_Filtros_v6.sqb",
            "role": "reference_only_traceability_not_active_capa2_layer",
            "exists": True,
            "exitTypes": {"ExitAfterBars.ExitAfterBars": "true", "StopLoss.StopLoss": "true", "ProfitTarget.ProfitTarget": "true"},
        }],
    })

    payload = gate.capa2_planning_report(tmp_path, tmp_path, target="both", write=True)

    assert payload["ok"] is True
    assert payload["phase"] == "phase15_capa2_planning"
    assert payload["nextPhase"] == "phase16_capa2_preflight_snapshot"
    assert payload["previousGate"]["phase"] == "phase14_capa1_closeout"
    assert "Preserve the Capa1 market edge" in payload["summary"]["objective"]
    assert payload["summary"]["buildTarget"]["riskManagement"].startswith("SL, TP and trailing")
    assert any("tradingTimeRanges.capa2 is empty" in warning for warning in payload["warnings"])
    assert any("RETEST 0 still carries ExitAfterBars" in warning for warning in payload["warnings"])
    assert any("adaptiveSpreadStress layer 2" in warning for warning in payload["warnings"])
    assert any("BS_Filtros_v6" in warning and "traceability/reference-only" in warning for warning in payload["warnings"])
    assert any("Reference-only `BS_Filtros_v6*` resources" in item for item in payload["summary"]["blockersBeforeApply"])
    assert any("Template Maker C2 templateFile" in item for item in payload["summary"]["blockersBeforeApply"])
    state = json.loads((tmp_path / ".local" / "sqx142_task_config" / "session_state.json").read_text(encoding="utf-8"))
    assert state["currentPhase"] == "phase15_capa2_planning"
    assert state["nextPhase"] == "phase16_capa2_preflight_snapshot"
    assert state["scope"] == "capa2"
    assert state["baseProject"] == "Capa2_Base_SQX142_Base"


def test_capa2_planning_issues_rejects_build_exit_after_bars():
    summary = {
        "targets": {"repoTemplate": _capa2_planning_target_summary(exit_after_bars_build="true")},
        "generator": {
            "tradingTimeRangesCapa2": {"H1": []},
            "taskPeriodMapsLayer2": {
                "Build-Task1.xml": {},
                "Retest-Task1.xml": {},
                "AutomaticRetest-Task7.xml": {},
                "Retest-Task2.xml": {},
                "AutomaticRetest-Task1.xml": {},
                "AutomaticRetest-Task2.xml": {},
                "AutomaticRetest-Task3.xml": {},
                "AutomaticRetest-Task4.xml": {},
                "AutomaticRetest-Task5.xml": {},
                "AutomaticRetest-Task6.xml": {},
                "AutomaticRetest-Task8.xml": {},
            },
            "adaptiveSpreadStressLayer2": {"default": {"minMultiplier": 2, "maxMultiplier": 5}},
        },
        "blocksettings": {"inspected": []},
    }

    issues, warnings = gate.capa2_planning_issues(summary)

    assert any("Build still allows ExitAfterBars" in issue for issue in issues)
    assert any("RETEST 0 still carries ExitAfterBars" in warning for warning in warnings)


def test_capa2_planning_cli_is_registered():
    args = gate.build_parser().parse_args(["capa2-planning-report", "--target", "repo-template"])

    assert args.command == "capa2-planning-report"
    assert args.target == "repo-template"


def test_capa2_preflight_snapshot_writes_phase16_and_copies_sources(monkeypatch, tmp_path):
    local_cfx = tmp_path / "local_project.cfx"
    repo_cfx = tmp_path / "repo_template.cfx"
    generator_profiles = tmp_path / "generator_profiles.json"
    blocksettings_manifest = tmp_path / "blocksettings_manifest.json"
    reference_bs = tmp_path / "BS_Filtros_v6.sqb"
    for path in (local_cfx, repo_cfx, generator_profiles, blocksettings_manifest, reference_bs):
        path.write_bytes(f"content:{path.name}".encode("utf-8"))

    monkeypatch.setattr(gate, "capa2_planning_report", lambda *args, **kwargs: {
        "phase": "phase15_capa2_planning",
        "ok": True,
        "issues": [],
        "warnings": [],
        "nextPhase": "phase16_capa2_preflight_snapshot",
        "summary": {"blockersBeforeApply": ["reference-only guard"]},
    })
    monkeypatch.setattr(gate, "process_snapshot", lambda: {"processes": []})
    monkeypatch.setattr(gate, "capa2_base_project_path", lambda root142: local_cfx)
    monkeypatch.setattr(gate, "DEFAULT_CAPA2_TEMPLATE", repo_cfx)
    monkeypatch.setattr(gate, "GENERATOR_PROFILES_PATH", generator_profiles)
    monkeypatch.setattr(gate, "BLOCKSETTINGS_MANIFEST_PATH", blocksettings_manifest)
    monkeypatch.setattr(gate, "capa2_blocksettings_summary", lambda: {
        "manifest": str(blocksettings_manifest),
        "mode": "reference_only_traceability",
        "recommendations": {"H1": "BS_Filtros_v6"},
        "inspected": [{
            "canonicalId": "BS_Filtros_v6",
            "path": str(reference_bs),
            "role": "reference_only_traceability_not_active_capa2_layer",
            "exists": True,
        }],
    })

    payload = gate.capa2_preflight_snapshot(tmp_path, tmp_path, target="both", write=True)

    assert payload["ok"] is True
    assert payload["phase"] == "phase16_capa2_preflight_snapshot"
    assert payload["nextPhase"] == "phase17_capa2_build_questionnaire"
    assert "reference-only/traceability" in payload["decisions"]["bsFiltrosRole"]
    assert "Template Maker C2 artifact" in payload["decisions"]["templateFileRole"]
    assert len(payload["copiedFiles"]) == 5
    assert Path(payload["snapshotDir"]).is_dir()
    assert Path(payload["written"]).is_file()
    state = json.loads((tmp_path / ".local" / "sqx142_task_config" / "session_state.json").read_text(encoding="utf-8"))
    assert state["currentPhase"] == "phase16_capa2_preflight_snapshot"
    assert state["nextPhase"] == "phase17_capa2_build_questionnaire"
    assert state["phase16SnapshotDir"] == payload["snapshotDir"]


def test_capa2_preflight_snapshot_cli_is_registered():
    args = gate.build_parser().parse_args(["capa2-preflight-snapshot", "--target", "both"])

    assert args.command == "capa2-preflight-snapshot"
    assert args.target == "both"


def _write_minimal_capa2_build_cfx(
    path: Path,
    template_file: str,
    spread: str = "2.0",
    task_title: str = "Build strategies",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    config_xml = f"""<Project><Tasks><Task title="{task_title}" taskXMLFile="Build-Task1.xml" /></Tasks></Project>"""
    indicator_blocks = "\n".join(
        f'<Block key="{key}" category="indicators" use="true" weight="1" />'
        for key in gate.CAPA2_BUILD_BLOCKS_INDICATOR_TARGET
    )
    task_xml = f"""
    <Task>
      <WhatToBuild><StrategyType type="template" templateFile="{template_file}" improveDatabank="Strategies to improve" /></WhatToBuild>
      <Blocks>
        <BuildingBlocks>
          <Block key="AlwaysTrue" category="signals" use="true" weight="1" />
          <Block key="CCI" category="signals" use="false" weight="1" />
          {indicator_blocks}
          <Block key="Indicators.RSI" category="indicators" use="false" weight="1" />
          <Block key="StopEntry.ATR" category="stopLimitBlocks" use="false" weight="1" />
        </BuildingBlocks>
        <OrderTypes><Block key="EnterAtMarket" use="true" /><Block key="EnterReverseAtMarket" use="false" /><Block key="EnterAtStop" use="false" /><Block key="EnterAtLimit" use="false" /></OrderTypes>
        <ExitTypes>
          <Block key="ExitAfterBars.ExitAfterBars" use="false" probability="50" />
          <Block key="MoveSL2BE.MoveSL2BE" use="false" probability="50" />
          <Block key="MoveSL2BE.SL2BEAddPips" use="false" probability="50" />
          <Block key="StopLoss.StopLoss" use="true" probability="100" />
          <Block key="ProfitTarget.ProfitTarget" use="true" probability="100" />
          <Block key="TrailingStop.TrailingStop" use="true" probability="50" />
          <Block key="TrailingStop.TrailingActivation" use="false" probability="50" />
          <Block key="_ExitRule_" use="false" probability="50" />
        </ExitTypes>
        <CustomData showAll="false" />
      </Blocks>
      <Data><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" session="No Session" testPrecision="2"><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="{spread}" /></Setup></Setups></Data>
      <Resources><Symbols /></Resources>
      <Rankings type="top" />
    </Task>
    """
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("config.xml", config_xml)
        archive.writestr("Build-Task1.xml", task_xml)


def test_capa2_build_questionnaire_writes_phase17_without_mutating_targets(monkeypatch, tmp_path):
    local_cfx = tmp_path / "local" / "project.cfx"
    repo_cfx = tmp_path / "repo" / "Capa2_Base.cfx"
    _write_minimal_capa2_build_cfx(local_cfx, r"C:\Users\Ivan SQX\Downloads\TemplateMaker\c2.sqx", spread="2")
    _write_minimal_capa2_build_cfx(repo_cfx, "", spread="2.0")
    before_local = gate.file_sha256(local_cfx)
    before_repo = gate.file_sha256(repo_cfx)

    monkeypatch.setattr(gate, "capa2_preflight_snapshot", lambda *args, **kwargs: {
        "phase": "phase16_capa2_preflight_snapshot",
        "ok": True,
        "issues": [],
        "warnings": [],
        "nextPhase": "phase17_capa2_build_questionnaire",
        "snapshotDir": str(tmp_path / ".local" / "snapshot"),
    })
    monkeypatch.setattr(gate, "process_snapshot", lambda: {"processes": []})
    monkeypatch.setattr(gate, "capa2_base_project_path", lambda root142: local_cfx)
    monkeypatch.setattr(gate, "DEFAULT_CAPA2_TEMPLATE", repo_cfx)

    payload = gate.capa2_build_questionnaire_report(tmp_path, tmp_path, max_values=0, write=True)

    assert payload["ok"] is True
    assert payload["phase"] == "phase17_capa2_build_questionnaire"
    assert payload["nextPhase"] == "phase17_capa2_build_what_to_build"
    assert payload["questionnaireSummary"]["tabCount"] >= 5
    assert payload["questionnaireSummary"]["totalQuestionCount"] > 0
    assert payload["questionnaireSummary"]["totalChangedQuestionCount"] > 0
    assert "Template Maker C2 templateFile ownership" in payload["summary"]["mustAsk"][0]
    assert Path(payload["written"]["phaseReport"]).is_file()
    assert Path(payload["written"]["taskSummary"]).is_file()
    assert (tmp_path / ".local" / "sqx142_task_config" / "questionnaires" / "capa2" / "Build_strategies").is_dir()
    state = json.loads((tmp_path / ".local" / "sqx142_task_config" / "session_state.json").read_text(encoding="utf-8"))
    assert state["currentPhase"] == "phase17_capa2_build_questionnaire"
    assert state["nextPhase"] == "phase17_capa2_build_what_to_build"
    assert gate.file_sha256(local_cfx) == before_local
    assert gate.file_sha256(repo_cfx) == before_repo


def test_capa2_build_questionnaire_cli_is_registered():
    args = gate.build_parser().parse_args(["capa2-build-questionnaire", "--max-values", "5"])

    assert args.command == "capa2-build-questionnaire"
    assert args.max_values == 5


def test_capa2_build_what_to_build_target_applies_and_is_idempotent(monkeypatch, tmp_path):
    local_cfx = tmp_path / "local" / "project.cfx"
    repo_cfx = tmp_path / "repo" / "Capa2_Base.cfx"
    _write_minimal_capa2_build_cfx(local_cfx, r"C:\Users\Ivan SQX\Downloads\TemplateMaker\c2.sqx", spread="2")
    _write_minimal_capa2_build_cfx(repo_cfx, r"C:\Users\Ivan SQX\Downloads\TemplateMaker\private.sqx", spread="2.0")

    monkeypatch.setattr(gate, "capa2_build_questionnaire_report", lambda *args, **kwargs: {
        "phase": "phase17_capa2_build_questionnaire",
        "ok": True,
        "issues": [],
        "warnings": [],
        "nextPhase": "phase17_capa2_build_what_to_build",
    })
    monkeypatch.setattr(gate, "process_snapshot", lambda: {"processes": []})
    monkeypatch.setattr(gate, "capa2_base_project_path", lambda root142: local_cfx)
    monkeypatch.setattr(gate, "DEFAULT_CAPA2_TEMPLATE", repo_cfx)

    payload = gate.promote_capa2_build_what_to_build_target(tmp_path, tmp_path, target="both", apply=True)

    assert payload["ok"] is True
    assert payload["phase"] == "phase17_capa2_build_what_to_build"
    assert payload["nextPhase"] == "phase17_capa2_build_blocks"
    assert Path(payload["answerRecord"]["written"]).is_file()
    local_root = gate.load_task_root(local_cfx, gate.CAPA2_BUILD_TASK_TITLE)[1]
    repo_root = gate.load_task_root(repo_cfx, gate.CAPA2_BUILD_TASK_TITLE)[1]
    assert gate.enforce_capa2_build_what_to_build_guard(local_root, "localBase") == []
    assert gate.enforce_capa2_build_what_to_build_guard(repo_root, "repoTemplate") == []
    assert local_root.find(".//WhatToBuild/StrategyType").get("templateFile").endswith("c2.sqx")
    assert repo_root.find(".//WhatToBuild/StrategyType").get("templateFile") == ""
    assert local_root.find(".//WhatToBuild/MarketSides").get("type") == "long"
    assert local_root.find(".//WhatToBuild/SLPTOptions/SLATR").text == "true"
    assert local_root.find(".//WhatToBuild/BuildMode/EvoRestartOnStagnation").get("status") == "false"

    dry_run = gate.promote_capa2_build_what_to_build_target(tmp_path, tmp_path, target="both", apply=False)

    assert dry_run["ok"] is True
    assert dry_run["results"]["localBase"]["changed"] is False
    assert dry_run["results"]["repoTemplate"]["changed"] is False
    assert dry_run["results"]["repoTemplate"]["changedActionCount"] == 0


def test_capa2_build_what_to_build_guard_rejects_exit_after_bars_and_day_exits():
    root = ET.fromstring(
        """
        <Settings>
          <WhatToBuild>
            <StrategyType type="template" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" />
            <RulesComplexity useDifferentSettings="false"><Chart name="Main chart" minConditions="0" maxConditions="1" minExitConditions="1" maxExitConditions="1" minExitTypes="1" maxExitTypes="5" minPeriod="5" maxPeriod="200" minShift="1" maxShift="1" /></RulesComplexity>
            <MarketSides type="long"><EntrySymmetry>false</EntrySymmetry><ExitSymmetry>false</ExitSymmetry></MarketSides>
            <SLPTOptions><SLRequired>true</SLRequired><SLFixedPips>false</SLFixedPips><MinSLInPips>30</MinSLInPips><MaxSLInPips>80</MaxSLInPips><MinSLInMoney>30</MinSLInMoney><MaxSLInMoney>80</MaxSLInMoney><SLATR>true</SLATR><MinSLATRMultiple>0.5</MinSLATRMultiple><MaxSLATRMultiple>5</MaxSLATRMultiple><MinSLATRPeriod>5</MinSLATRPeriod><MaxSLATRPeriod>200</MaxSLATRPeriod><PTRequired>true</PTRequired><SeparatedSettings>true</SeparatedSettings><PTFixedPips>false</PTFixedPips><MinPTInPips>60</MinPTInPips><MaxPTInPips>200</MaxPTInPips><MinPTInMoney>60</MinPTInMoney><MaxPTInMoney>200</MaxPTInMoney><PTATR>true</PTATR><MinPTATRMultiple>0.5</MinPTATRMultiple><MaxPTATRMultiple>5</MaxPTATRMultiple><MinPTATRPeriod>5</MinPTATRPeriod><MaxPTATRPeriod>200</MaxPTATRPeriod><LimitSLPTRRR>false</LimitSLPTRRR><LimitSLPTRRRFrom>50</LimitSLPTRRRFrom><LimitSLPTRRRTo>80</LimitSLPTRRRTo><SLValueType>pips</SLValueType><PTValueType>pips</PTValueType><SLIndicatorBased>false</SLIndicatorBased><PTIndicatorBased>false</PTIndicatorBased><SLPercent>false</SLPercent><MinSLInPercent>1</MinSLInPercent><MaxSLInPercent>10</MaxSLInPercent><PTPercent>false</PTPercent><MinPTInPercent>1</MinPTInPercent><MaxPTInPercent>10</MaxPTInPercent></SLPTOptions>
            <BuildMode generationType="random-generation"><PopulationSize>55</PopulationSize><MaxGenerations>100</MaxGenerations><CrossoverProbability>31</CrossoverProbability><MutationProbability>30</MutationProbability><ShowAdvancedGeneticSettings>false</ShowAdvancedGeneticSettings><Islands>7</Islands><MigrationModulo>19</MigrationModulo><MigrationRate>4</MigrationRate><ShowLastGenerationDatabank>true</ShowLastGenerationDatabank><InitGenerationType>1</InitGenerationType><DecimationCoef>1</DecimationCoef><FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar><FreshBloodReplaceWeakest>true</FreshBloodReplaceWeakest><FreshBloodWeakestPct>10</FreshBloodWeakestPct><FreshBloodWeakestGenerations>100</FreshBloodWeakestGenerations><Conditions><Condition use="true"><Left-Side valueType="column"><Column-Value column="ProfitFactor" format="Decimal2" sampleType="127" /></Left-Side><Comparator value="&gt;" /><Right-Side valueType="numeric"><Numeric-Value value="1" /></Right-Side></Condition></Conditions><EvoRestartOnFinish status="true" /><EvoRestartOnStagnation status="false" fitnessType="10" generations="15" /><EvoInSamplePeriod ratio="50" /></BuildMode>
          </WhatToBuild>
          <Blocks>
            <OrderTypes><Block key="EnterAtMarket" use="true" /></OrderTypes>
            <ExitTypes><Block key="ExitAfterBars.ExitAfterBars" use="true" /><Block key="ExitAfterDays.ExitAfterDays" use="true" /><Block key="StopLoss.StopLoss" use="true" /><Block key="ProfitTarget.ProfitTarget" use="true" /><Block key="TrailingStop.TrailingStop" use="true" /></ExitTypes>
          </Blocks>
        </Settings>
        """
    )

    issues = gate.enforce_capa2_build_what_to_build_guard(root, "repoTemplate")

    assert any("ExitAfterBars" in issue for issue in issues)
    assert any("day-based exit" in issue for issue in issues)


def test_capa2_build_what_to_build_cli_is_registered():
    args = gate.build_parser().parse_args(["capa2-build-what-to-build-target", "--target", "both"])

    assert args.command == "capa2-build-what-to-build-target"
    assert args.target == "both"


def test_capa2_build_blocks_target_applies_and_is_idempotent(monkeypatch, tmp_path):
    local_cfx = tmp_path / "local" / "project.cfx"
    repo_cfx = tmp_path / "repo" / "Capa2_Base.cfx"
    _write_minimal_capa2_build_cfx(local_cfx, r"C:\Users\Ivan SQX\Downloads\TemplateMaker\c2.sqx", spread="2")
    _write_minimal_capa2_build_cfx(repo_cfx, "", spread="2.0")
    task_xml, repo_root = gate.load_task_root(repo_cfx, gate.CAPA2_BUILD_TASK_TITLE)
    repo_root.find(".//OrderTypes/Block[@key='EnterAtStop']").set("use", "true")
    repo_root.find(".//ExitTypes/Block[@key='ExitAfterBars.ExitAfterBars']").set("use", "true")
    repo_root.find(".//ExitTypes/Block[@key='TrailingStop.TrailingStop']").set("use", "false")
    repo_root.find(".//BuildingBlocks/Block[@key='StopEntry.ATR']").set("use", "true")
    gate.replace_zip_text_entry(repo_cfx, task_xml, gate.serialize_xml(repo_root))

    monkeypatch.setattr(gate, "promote_capa2_build_what_to_build_target", lambda *args, **kwargs: {
        "phase": "phase17_capa2_build_what_to_build",
        "ok": True,
        "issues": [],
        "warnings": [],
        "nextPhase": "phase17_capa2_build_blocks",
    })
    monkeypatch.setattr(gate, "process_snapshot", lambda: {"processes": []})
    monkeypatch.setattr(gate, "capa2_base_project_path", lambda root142: local_cfx)
    monkeypatch.setattr(gate, "DEFAULT_CAPA2_TEMPLATE", repo_cfx)

    payload = gate.promote_capa2_build_blocks_target(tmp_path, tmp_path, target="both", apply=True)

    assert payload["ok"] is True
    assert payload["phase"] == "phase17_capa2_build_blocks"
    assert payload["nextPhase"] == "phase17_capa2_build_data_databanks_resources_options"
    assert Path(payload["answerRecord"]["written"]).is_file()
    local_root = gate.load_task_root(local_cfx, gate.CAPA2_BUILD_TASK_TITLE)[1]
    repo_root = gate.load_task_root(repo_cfx, gate.CAPA2_BUILD_TASK_TITLE)[1]
    assert gate.enforce_capa2_build_blocks_guard(local_root, "localBase") == []
    assert gate.enforce_capa2_build_blocks_guard(repo_root, "repoTemplate") == []
    assert repo_root.find(".//ExitTypes/Block[@key='ExitAfterBars.ExitAfterBars']").get("use") == "false"
    assert repo_root.find(".//ExitTypes/Block[@key='StopLoss.StopLoss']").get("probability") == "100"
    assert repo_root.find(".//ExitTypes/Block[@key='ProfitTarget.ProfitTarget']").get("probability") == "100"
    assert repo_root.find(".//ExitTypes/Block[@key='TrailingStop.TrailingStop']").get("use") == "true"
    assert gate.active_building_block_keys_by_category(repo_root.find(".//Blocks"), "signals") == ["AlwaysTrue"]
    assert gate.active_building_block_keys_by_category(repo_root.find(".//Blocks"), "stopLimitBlocks") == []

    dry_run = gate.promote_capa2_build_blocks_target(tmp_path, tmp_path, target="both", apply=False)

    assert dry_run["ok"] is True
    assert dry_run["results"]["localBase"]["changed"] is False
    assert dry_run["results"]["repoTemplate"]["changed"] is False
    assert dry_run["results"]["repoTemplate"]["changedActionCount"] == 0


def test_capa2_build_blocks_guard_rejects_drift():
    root = ET.fromstring(
        """
        <Settings>
          <Blocks>
            <BuildingBlocks>
              <Block key="AlwaysTrue" category="signals" use="true" />
              <Block key="CCI" category="signals" use="true" />
              <Block key="StopEntry.ATR" category="stopLimitBlocks" use="true" />
            </BuildingBlocks>
            <OrderTypes><Block key="EnterAtMarket" use="true" /><Block key="EnterAtStop" use="true" /></OrderTypes>
            <ExitTypes>
              <Block key="ExitAfterBars.ExitAfterBars" use="true" probability="50" />
              <Block key="ExitAfterDays.ExitAfterDays" use="true" />
              <Block key="StopLoss.StopLoss" use="true" probability="100" />
              <Block key="ProfitTarget.ProfitTarget" use="true" probability="100" />
              <Block key="TrailingStop.TrailingStop" use="false" probability="50" />
            </ExitTypes>
            <CustomData showAll="true"><Row /></CustomData>
          </Blocks>
        </Settings>
        """
    )

    issues = gate.enforce_capa2_build_blocks_guard(root, "repoTemplate")

    assert any("EnterAtStop" in issue for issue in issues)
    assert any("ExitAfterBars" in issue for issue in issues)
    assert any("TrailingStop" in issue for issue in issues)
    assert any("AlwaysTrue" in issue for issue in issues)
    assert any("stop/limit" in issue for issue in issues)
    assert any("external custom data" in issue for issue in issues)


def test_capa2_build_blocks_cli_is_registered():
    args = gate.build_parser().parse_args(["capa2-build-blocks-target", "--target", "both"])

    assert args.command == "capa2-build-blocks-target"
    assert args.target == "both"


def _write_capa2_generator_profile(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({
            "retestPeriods": {"BUILD": ["2017.10.02", "2023.12.31"]},
            "tradingTimeRanges": {"capa2": gate.CAPA2_TRADING_TIME_RANGES_TARGET},
            "disableTradingTimeRanges": {"2": gate.CAPA2_DISABLE_TRADING_TIME_RANGES_TARGET},
            "taskPeriodMaps": {"2": {"Build-Task1.xml": "BUILD"}},
        }),
        encoding="utf-8",
    )


def test_capa2_build_data_databanks_resources_options_applies_and_is_idempotent(monkeypatch, tmp_path):
    local_cfx = tmp_path / "local" / "project.cfx"
    repo_cfx = tmp_path / "repo" / "Capa2_Base.cfx"
    generator_profile = tmp_path / "generator_profiles.json"
    _write_minimal_capa2_build_cfx(local_cfx, r"C:\Users\Ivan SQX\Downloads\TemplateMaker\c2.sqx", spread="2")
    _write_minimal_capa2_build_cfx(repo_cfx, "", spread="1.4")
    _write_capa2_generator_profile(generator_profile)

    monkeypatch.setattr(gate, "promote_capa2_build_blocks_target", lambda *args, **kwargs: {
        "phase": "phase17_capa2_build_blocks",
        "ok": True,
        "issues": [],
        "warnings": [],
        "nextPhase": "phase17_capa2_build_data_databanks_resources_options",
    })
    monkeypatch.setattr(gate, "process_snapshot", lambda: {"processes": []})
    monkeypatch.setattr(gate, "capa2_base_project_path", lambda root142: local_cfx)
    monkeypatch.setattr(gate, "DEFAULT_CAPA2_TEMPLATE", repo_cfx)
    monkeypatch.setattr(gate, "GENERATOR_PROFILES_PATH", generator_profile)

    payload = gate.promote_capa2_build_data_databanks_resources_options_target(tmp_path, tmp_path, target="both", apply=True)

    assert payload["ok"] is True
    assert payload["phase"] == "phase17_capa2_build_data_databanks_resources_options"
    assert payload["nextPhase"] == "phase17_capa2_build_rankings"
    assert Path(payload["answerRecord"]["written"]["Data"]).is_file()
    local_root = gate.load_task_root(local_cfx, gate.CAPA2_BUILD_TASK_TITLE)[1]
    repo_root = gate.load_task_root(repo_cfx, gate.CAPA2_BUILD_TASK_TITLE)[1]
    assert gate.enforce_capa2_build_data_databanks_resources_options_guard(local_root, "localBase") == []
    assert gate.enforce_capa2_build_data_databanks_resources_options_guard(repo_root, "repoTemplate") == []
    setup = local_root.find("./Data/Setups/Setup")
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == "2"
    assert setup.get("session") == "No Session"
    assert setup.find("Chart").attrib == {"symbol": "AUDCAD_darwinex", "timeframe": "H1", "spread": "2.0"}
    assert local_root.findall("./Data/OutOfSample/Range") == []
    assert {
        databank.get("name"): databank.get("value")
        for databank in local_root.findall("./Databanks/Databank")
    } == {"Input": "Results", "Output": "null"}
    assert local_root.find("./Resources/Symbols/Symbol").get("precision") == "TICK"
    assert local_root.find("./Resources/Symbols/Symbol").get("timezone") == "EETUS"
    assert local_root.findall("./Resources/Sessions/Session") == []
    options = {
        param.get("key"): param.text
        for param in local_root.findall(".//BuildTradingOptions/Params/Param")
        if param.get("key") in gate.CAPA2_BUILD_OPTIONS_PARAMS_TARGET
    }
    assert options == gate.CAPA2_BUILD_OPTIONS_PARAMS_TARGET

    dry_run = gate.promote_capa2_build_data_databanks_resources_options_target(tmp_path, tmp_path, target="both", apply=False)

    assert dry_run["ok"] is True
    assert dry_run["results"]["localBase"]["changed"] is False
    assert dry_run["results"]["repoTemplate"]["changed"] is False
    assert dry_run["results"]["repoTemplate"]["changedActionCount"] == 0


def test_capa2_build_data_databanks_resources_options_guard_rejects_drift():
    root = ET.fromstring(
        """
        <Settings>
          <Data>
            <Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old Session"><Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" /></Setup></Setups>
            <OutOfSample><Range dateFrom="2023.01.01" dateTo="2025.01.01" /></OutOfSample>
          </Data>
          <Databanks><Databank name="Input" value="Monkey Test" /><Databank name="Output" value="Results" /></Databanks>
          <Resources><Symbols><Symbol name="USDJPY_darwinex" precision="M1" timezone="UTC" broker="9"><InstrumentInfo broker="9" /></Symbol></Symbols><Brokers><Broker id="4" /></Brokers><Sessions><Session name="Old" /></Sessions></Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">false</Param><Param key="RealisticGapsHandling">false</Param><Param key="StoreChartData">true</Param><Param key="Session">Old</Param><Param key="MarketOpenSession">Old</Param></Params></BuildTradingOptions></Options>
        </Settings>
        """
    )

    issues = gate.enforce_capa2_build_data_databanks_resources_options_guard(root, "repoTemplate")

    assert any("dateFrom" in issue for issue in issues)
    assert any("testPrecision" in issue for issue in issues)
    assert any("chart symbol" in issue for issue in issues)
    assert any("OutOfSample" in issue for issue in issues)
    assert any("Databank Input" in issue for issue in issues)
    assert any("Resources must keep only seed symbol" in issue for issue in issues)
    assert any("Options param LimitTimeRange" in issue for issue in issues)
    assert any("forbidden donor token" in issue for issue in issues)


def test_capa2_generator_layer2_contract_rejects_missing_windows(monkeypatch, tmp_path):
    generator_profile = tmp_path / "generator_profiles.json"
    generator_profile.write_text(
        json.dumps({"tradingTimeRanges": {"capa2": {}}, "disableTradingTimeRanges": {}, "taskPeriodMaps": {"2": {"Build-Task1.xml": "BUILD"}}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "GENERATOR_PROFILES_PATH", generator_profile)

    issues = gate.enforce_capa2_generator_layer2_contract()

    assert any("tradingTimeRanges.capa2" in issue for issue in issues)
    assert any("disableTradingTimeRanges.2" in issue for issue in issues)


def test_capa2_build_data_databanks_resources_options_cli_is_registered():
    args = gate.build_parser().parse_args(["capa2-build-data-databanks-resources-options-target", "--target", "both"])

    assert args.command == "capa2-build-data-databanks-resources-options-target"
    assert args.target == "both"


def test_capa2_build_task_resolves_by_xml_when_web_title_is_dynamic(tmp_path):
    cfx = tmp_path / "dynamic" / "project.cfx"
    _write_minimal_capa2_build_cfx(
        cfx,
        "",
        task_title="Build EURUSD M15 Long from Edge Factory",
    )

    task_xml, root, display_title = gate.load_capa2_build_task_root(cfx)

    assert task_xml == "Build-Task1.xml"
    assert root is not None
    assert display_title == "Build EURUSD M15 Long from Edge Factory"


def test_capa2_build_rankings_target_applies_and_is_idempotent(monkeypatch, tmp_path):
    local_cfx = tmp_path / "local" / "project.cfx"
    repo_cfx = tmp_path / "repo" / "Capa2_Base.cfx"
    _write_minimal_capa2_build_cfx(
        local_cfx,
        r"C:\Users\Ivan SQX\Downloads\TemplateMaker\c2.sqx",
        spread="2",
        task_title="Build AUDCAD H1 Capa2 generated title",
    )
    _write_minimal_capa2_build_cfx(repo_cfx, "", spread="2.0", task_title="Build Template Capa2")

    monkeypatch.setattr(gate, "promote_capa2_build_data_databanks_resources_options_target", lambda *args, **kwargs: {
        "phase": "phase17_capa2_build_data_databanks_resources_options",
        "ok": True,
        "issues": [],
        "warnings": [],
        "nextPhase": "phase17_capa2_build_rankings",
    })
    monkeypatch.setattr(gate, "process_snapshot", lambda: {"processes": []})
    monkeypatch.setattr(gate, "capa2_base_project_path", lambda root142: local_cfx)
    monkeypatch.setattr(gate, "DEFAULT_CAPA2_TEMPLATE", repo_cfx)

    payload = gate.promote_capa2_build_rankings_target(tmp_path, tmp_path, target="both", apply=True)

    assert payload["ok"] is True
    assert payload["phase"] == "phase17_capa2_build_rankings"
    assert payload["nextPhase"] == "phase17_capa2_build_crosschecks"
    assert Path(payload["answerRecord"]["written"]).is_file()
    local_root = gate.load_capa2_build_task_root(local_cfx)[1]
    repo_root = gate.load_capa2_build_task_root(repo_cfx)[1]
    assert gate.enforce_capa2_build_rankings_guard(local_root, "localBase") == []
    assert gate.enforce_capa2_build_rankings_guard(repo_root, "repoTemplate") == []
    rankings = local_root.find("./Rankings")
    assert rankings.get("type") == "never"
    assert rankings.findtext("MaxStrategies") == "2000"
    assert rankings.findtext("DeleteFailedStrategies") == "false"
    assert rankings.findtext("ForceRunCrossChecks") == "false"
    assert rankings.find("StopCondition").attrib["type"] == "databank-full"
    assert rankings.find("StopCondition").attrib["passedStrategies"] == "500"
    assert rankings.find("FitPortfolio").get("active") == "false"
    assert rankings.find("CustomAnalysis").get("filter") == "false"
    assert gate.summarize_conditions_detailed(rankings.find("Conditions")) == [
        {
            "column": item["column"],
            "comparator": item["comparator"],
            "value": item["value"],
            "format": item["format"],
            "sampleType": item["sampleType"],
            "use": item["use"],
        }
        for item in gate.CAPA2_BUILD_RANKING_CONDITIONS_TARGET
    ]
    assert gate.active_ranking_goal_summary(rankings) == [gate.CAPA2_BUILD_RANKING_ACTIVE_GOAL]

    dry_run = gate.promote_capa2_build_rankings_target(tmp_path, tmp_path, target="both", apply=False)

    assert dry_run["ok"] is True
    assert dry_run["results"]["localBase"]["changed"] is False
    assert dry_run["results"]["repoTemplate"]["changed"] is False
    assert dry_run["results"]["repoTemplate"]["changedActionCount"] == 0


def test_capa2_build_rankings_guard_rejects_drift():
    root = ET.fromstring(
        r"""
        <Settings>
          <Rankings type="top">
            <MaxStrategies>1000</MaxStrategies>
            <ConditionsType>0</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <AutomaticDismissal warnings="true" />
            <StopCondition type="time-limit" passedStrategies="1000" restartCount="5" days="0" hours="6" minutes="0" />
            <FitPortfolio active="true" databank="Existing portfolio" />
            <CustomAnalysis method="python" filter="true" inputArgs="C:\private\USDJPY.csv" />
            <FitnessCriteria method="ComputeFromStrategyResult" useFitnessByIndex="false">
              <Settings><Ranking type="Weighted">
                <Goal type="AnnualPctReturnDDRatio" use="true" weight="1" valueType="1" target="0" />
                <Goal type="ProfitFactor" use="true" weight="1" valueType="1" target="0" />
              </Ranking></Settings>
            </FitnessCriteria>
            <Conditions>
              <Condition use="true"><Left-Side valueType="column"><Column-Value column="NetProfit" format="Decimal2" sampleType="127" /></Left-Side><Comparator value="&gt;" /><Right-Side valueType="numeric"><Numeric-Value value="999999" /></Right-Side></Condition>
            </Conditions>
          </Rankings>
        </Settings>
        """
    )

    issues = gate.enforce_capa2_build_rankings_guard(root, "repoTemplate")

    assert any("type" in issue for issue in issues)
    assert any("MaxStrategies" in issue for issue in issues)
    assert any("StopCondition" in issue for issue in issues)
    assert any("FitPortfolio" in issue for issue in issues)
    assert any("ForceRunCrossChecks" in issue for issue in issues)
    assert any("ranking conditions" in issue for issue in issues)
    assert any("active ranking goals" in issue for issue in issues)
    assert any("forbidden donor token" in issue for issue in issues)
    assert any("local absolute path" in issue for issue in issues)


def test_capa2_build_rankings_cli_is_registered():
    args = gate.build_parser().parse_args(["capa2-build-rankings-target", "--target", "both"])

    assert args.command == "capa2-build-rankings-target"
    assert args.target == "both"


def test_synthetic_closeout_report_requires_green_phase10_dry_runs(monkeypatch, tmp_path):
    calls = []

    def green_payload(command: str) -> dict:
        return {
            "ok": True,
            "apply": False,
            "operation": command.replace("-", "_"),
            "nextPhase": "phase10_synthetic_closeout",
            "written": f"{command}.json",
            "results": {
                "localBase": {
                    "exists": True,
                    "isZip": True,
                    "guardOk": True,
                    "changed": False,
                    "changedActionCount": 0,
                    "issues": [],
                    "taskXml": "AutomaticRetest-Task5.xml",
                },
                "repoTemplate": {
                    "exists": True,
                    "isZip": True,
                    "guardOk": True,
                    "changed": False,
                    "changedActionCount": 0,
                    "issues": [],
                    "taskXml": "AutomaticRetest-Task5.xml",
                },
            },
        }

    def runner_factory(command: str):
        def runner(root142, project_root, target, apply):
            calls.append((command, target, apply))
            return green_payload(command)
        return runner

    monkeypatch.setattr(gate, "SYNTHETIC_CLOSEOUT_OPERATIONS", (
        ("dataDatabanksResourcesOptions", "synthetic-data-databanks-resources-options-target", runner_factory("synthetic-data-databanks-resources-options-target")),
        ("crosschecks", "synthetic-crosschecks-target", runner_factory("synthetic-crosschecks-target")),
        ("passiveGeneration", "synthetic-passive-generation-target", runner_factory("synthetic-passive-generation-target")),
        ("staticTabs", "synthetic-static-tabs-target", runner_factory("synthetic-static-tabs-target")),
    ))
    monkeypatch.setattr(gate, "monkey_closeout_report", lambda *args, **kwargs: {
        "phase": "phase9_monkey_test_closeout",
        "ok": True,
        "issues": [],
        "nextPhase": "phase10_synthetic_open",
    })
    monkeypatch.setattr(gate, "process_snapshot", lambda: {"processes": []})

    payload = gate.synthetic_closeout_report(tmp_path, tmp_path, target="both", write=True)

    assert payload["ok"] is True
    assert payload["phase"] == "phase10_synthetic_closeout"
    assert payload["nextPhase"] == "phase11_spp_open"
    assert payload["summary"]["chain"] == "Input=Monkey Test / Output=Syntetic"
    assert payload["summary"]["activeMethod"] == "SyntheticBootstrapV3"
    assert {call[0] for call in calls} == {
        "synthetic-data-databanks-resources-options-target",
        "synthetic-crosschecks-target",
        "synthetic-passive-generation-target",
        "synthetic-static-tabs-target",
    }
    assert all(call[1] == "both" and call[2] is False for call in calls)
    assert (tmp_path / ".local" / "sqx142_task_config" / "session_state.json").is_file()
    state = json.loads((tmp_path / ".local" / "sqx142_task_config" / "session_state.json").read_text(encoding="utf-8"))
    assert state["currentPhase"] == "phase10_synthetic_closeout"
    assert state["nextPhase"] == "phase11_spp_open"


def test_spp_open_summary_detects_spp_chain_and_execution_policy():
    root = ET.fromstring(
        """
        <Settings>
          <CustomData><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0"><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" /></Setup></Setups></CustomData>
          <Databanks><Databank name="Input" value="Syntetic" /><Databank name="Output" value="SPP" /></Databanks>
          <Resources><Symbols><Symbol name="AUDCAD_darwinex" precision="TICK" timezone="EETUS" broker="4"><InstrumentInfo instrument="AUDCAD_darwinex" broker="4" /></Symbol></Symbols><Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers><Sessions /></Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">false</Param><Param key="RealisticGapsHandling">false</Param><Param key="StoreChartData">false</Param><Param key="Session">No Session</Param><Param key="MarketOpenSession">No Session</Param></Params></BuildTradingOptions></Options>
          <CrossChecks use="true" evaluateAll="true">
            <OptProfileSysParamPermutation use="true">
              <Settings>
                <MaxTests>3000</MaxTests><DistributionUp>20</DistributionUp><DistributionDown>20</DistributionDown><Steps>25</Steps>
                <WhatToParametrize type="1" symmetricVariables="false"><Recommended>false</Recommended><Periods>true</Periods><Constants>true</Constants><EntryParams>true</EntryParams><ExitParamsUsed>true</ExitParamsUsed></WhatToParametrize>
              </Settings>
              <AcceptanceSettings><ProfitOptPct>30</ProfitOptPct><AvgProfit>0</AvgProfit><UniformDistrChanges>15</UniformDistrChanges><StdevAvgProfit>1</StdevAvgProfit><EvalProfitOptCheck>true</EvalProfitOptCheck><EvalAvgProfitCheck>true</EvalAvgProfitCheck><EvalUniformDistrCheck>true</EvalUniformDistrCheck><Conditions><Condition use="true" /><Condition use="true" /></Conditions></AcceptanceSettings>
            </OptProfileSysParamPermutation>
            <MonteCarloRetest use="false"><Settings><Methods><Method type="RandomizeSpread" use="true" /></Methods></Settings></MonteCarloRetest>
          </CrossChecks>
        </Settings>
        """
    )

    summary = gate.spp_open_summary(root)
    issues, warnings = gate.spp_open_issues(summary)

    assert issues == []
    assert summary["databanks"] == {"Input": "Syntetic", "Output": "SPP"}
    assert summary["executionPolicy"] == "configuration_review_only_no_smoke_no_optimization"
    assert summary["crossChecks"]["active"] == ["OptProfileSysParamPermutation"]
    assert summary["activeSPPCheck"]["settings"]["MaxTests"] == "3000"
    assert summary["activeSPPCheck"]["settings"]["ParametrizeFlags"]["Periods"] == "true"
    assert any("inactive crosschecks" in warning for warning in warnings)
    assert any("configuration-review only" in warning for warning in warnings)
    assert any("WFM depends on SPP output" in warning for warning in warnings)


def test_spp_open_report_requires_synthetic_closeout_and_writes_state(monkeypatch, tmp_path):
    monkeypatch.setattr(gate, "spp_open_target_report", lambda path: {
        "ok": True,
        "taskTitle": "SPP",
        "taskXml": "AutomaticRetest-Task7.xml",
        "warnings": ["SPP is explicitly configuration-review only"],
        "issues": [],
        "summary": {
            "databanks": {"Input": "Syntetic", "Output": "SPP"},
            "crossChecks": {"active": ["OptProfileSysParamPermutation"]},
        },
    })
    monkeypatch.setattr(gate, "synthetic_closeout_report", lambda *args, **kwargs: {
        "phase": "phase10_synthetic_closeout",
        "ok": True,
        "issues": [],
        "nextPhase": "phase11_spp_open",
    })
    monkeypatch.setattr(gate, "process_snapshot", lambda: {"processes": []})

    payload = gate.spp_open_report(tmp_path, tmp_path, target="both", write=True)

    assert payload["ok"] is True
    assert payload["phase"] == "phase11_spp_open"
    assert payload["nextPhase"] == "phase11_spp_data_databanks_resources_options"
    assert payload["previousGate"]["phase"] == "phase10_synthetic_closeout"
    assert payload["summary"]["chain"] == "Input=Syntetic / Output=SPP"
    assert payload["summary"]["activeCrossCheck"] == "OptProfileSysParamPermutation"
    assert payload["summary"]["executionPolicy"] == "configuration_review_only_no_smoke_no_optimization"
    state = json.loads((tmp_path / ".local" / "sqx142_task_config" / "session_state.json").read_text(encoding="utf-8"))
    assert state["currentPhase"] == "phase11_spp_open"
    assert state["nextPhase"] == "phase11_spp_data_databanks_resources_options"


def test_spp_closeout_report_consolidates_phase11_guards_without_running_spp(monkeypatch, tmp_path):
    calls = []

    def green_payload(command: str) -> dict:
        return {
            "ok": True,
            "apply": False,
            "operation": command.replace("-", "_"),
            "nextPhase": "phase11_spp_closeout",
            "written": f"{command}.json",
            "results": {
                "localBase": {
                    "exists": True,
                    "isZip": True,
                    "guardOk": True,
                    "changed": False,
                    "changedActionCount": 0,
                    "issues": [],
                    "taskXml": "AutomaticRetest-Task7.xml",
                },
                "repoTemplate": {
                    "exists": True,
                    "isZip": True,
                    "guardOk": True,
                    "changed": False,
                    "changedActionCount": 0,
                    "issues": [],
                    "taskXml": "AutomaticRetest-Task7.xml",
                },
            },
        }

    def runner_factory(command: str):
        def runner(root142, project_root, target, apply):
            calls.append((command, target, apply))
            return green_payload(command)
        return runner

    monkeypatch.setattr(gate, "SPP_CLOSEOUT_OPERATIONS", (
        (
            "dataDatabanksResourcesOptions",
            "spp-data-databanks-resources-options-target",
            runner_factory("spp-data-databanks-resources-options-target"),
        ),
        ("crosschecks", "spp-crosschecks-target", runner_factory("spp-crosschecks-target")),
        ("staticTabs", "spp-static-tabs-target", runner_factory("spp-static-tabs-target")),
    ))
    monkeypatch.setattr(gate, "synthetic_closeout_report", lambda *args, **kwargs: {
        "phase": "phase10_synthetic_closeout",
        "ok": True,
        "issues": [],
        "nextPhase": "phase11_spp_open",
    })
    monkeypatch.setattr(gate, "process_snapshot", lambda: {"processes": []})

    payload = gate.spp_closeout_report(tmp_path, tmp_path, target="both", write=True)

    assert payload["ok"] is True
    assert payload["phase"] == "phase11_spp_closeout"
    assert payload["nextPhase"] == "phase12_wfm_open"
    assert payload["summary"]["chain"] == "Input=Syntetic / Output=SPP"
    assert payload["summary"]["executionPolicy"] == "configuration_review_only_no_smoke_no_optimization"
    assert payload["summary"]["dataContract"]["carrier"] == "CustomData-only"
    assert "review-only/blocked" in payload["summary"]["downstreamDependency"]
    assert {call[0] for call in calls} == {
        "spp-data-databanks-resources-options-target",
        "spp-crosschecks-target",
        "spp-static-tabs-target",
    }
    assert all(call[1] == "both" and call[2] is False for call in calls)
    assert (tmp_path / ".local" / "sqx142_task_config" / "session_state.json").is_file()
    state = json.loads((tmp_path / ".local" / "sqx142_task_config" / "session_state.json").read_text(encoding="utf-8"))
    assert state["currentPhase"] == "phase11_spp_closeout"
    assert state["nextPhase"] == "phase12_wfm_open"


def test_wfm_open_summary_detects_wfm_chain_and_blocked_policy():
    root = ET.fromstring(
        """
        <Settings>
          <Data><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" engine="MetaTrader5 (hedged)"><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2" /></Setup></Setups></Data>
          <CustomData><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" engine="MetaTrader4"><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" /><MainTestValues engine="true" symbol="true" timeframe="true" dates="true" precision="true" spread="true" /></Setup></Setups></CustomData>
          <Databanks><Databank name="Input" value="SPP" /><Databank name="Output" value="WFM" /></Databanks>
          <Resources><Symbols><Symbol name="AUDCAD_darwinex" precision="TICK" timezone="EETUS" broker="4"><InstrumentInfo instrument="AUDCAD_darwinex" broker="4" /></Symbol></Symbols><Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers><Sessions /></Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">false</Param><Param key="RealisticGapsHandling">false</Param><Param key="StoreChartData">false</Param><Param key="Session">No Session</Param><Param key="MarketOpenSession">No Session</Param></Params></BuildTradingOptions></Options>
          <CrossChecks use="true" evaluateAll="true">
            <WalkForwardOptimization use="false"><Settings><WalkForward type="1" period="10" optimization="15" /><MaxTests>100</MaxTests></Settings><AcceptanceSettings><Conditions><Condition use="true" /></Conditions></AcceptanceSettings></WalkForwardOptimization>
            <WalkForwardMatrix use="true">
              <Settings>
                <WalkForward type="2" period="10" optimization="15" distributionUp="20" distributionDown="20" maxSteps="8"><Param1 value="20" /><Param2 value="10" /></WalkForward>
                <MaxTests>3000</MaxTests>
                <WhatToParametrize type="1" symmetricVariables="false"><Recommended>false</Recommended><Periods>true</Periods><Constants>true</Constants><EntryParams>true</EntryParams><ExitParamsUsed>true</ExitParamsUsed></WhatToParametrize>
              </Settings>
              <AcceptanceSettings><Conditions thresholdPct="80"><Condition use="true"><Left-Side valueType="column"><Column-Value column="NetProfit" resultType="WalkForwardMatrix" /></Left-Side><Comparator value="&gt;" /><Right-Side valueType="numeric"><Numeric-Value value="0" /></Right-Side></Condition></Conditions></AcceptanceSettings>
            </WalkForwardMatrix>
          </CrossChecks>
        </Settings>
        """
    )

    summary = gate.wfm_open_summary(root)
    issues, warnings = gate.wfm_open_issues(summary)

    assert issues == []
    assert summary["databanks"] == {"Input": "SPP", "Output": "WFM"}
    assert summary["executionPolicy"] == "configuration_review_only_no_smoke_no_optimization_blocked_by_spp"
    assert summary["crossChecks"]["active"] == ["WalkForwardMatrix"]
    assert summary["activeWFMCheck"]["settings"]["WalkForward"]["type"] == "2"
    assert summary["activeWFMCheck"]["settings"]["MaxTests"] == "3000"
    assert any("Data engine" in warning for warning in warnings)
    assert any("Data spread" in warning for warning in warnings)
    assert any("WFM depends on SPP output" in warning for warning in warnings)


def test_wfm_open_report_requires_spp_closeout_and_writes_state(monkeypatch, tmp_path):
    monkeypatch.setattr(gate, "wfm_open_target_report", lambda path: {
        "ok": True,
        "taskTitle": "WFM",
        "taskXml": "AutomaticRetest-Task4.xml",
        "warnings": ["WFM depends on SPP output"],
        "issues": [],
        "summary": {
            "databanks": {"Input": "SPP", "Output": "WFM"},
            "crossChecks": {"active": ["WalkForwardMatrix"]},
        },
    })
    monkeypatch.setattr(gate, "spp_closeout_report", lambda *args, **kwargs: {
        "phase": "phase11_spp_closeout",
        "ok": True,
        "issues": [],
        "nextPhase": "phase12_wfm_open",
    })
    monkeypatch.setattr(gate, "process_snapshot", lambda: {"processes": []})

    payload = gate.wfm_open_report(tmp_path, tmp_path, target="both", write=True)

    assert payload["ok"] is True
    assert payload["phase"] == "phase12_wfm_open"
    assert payload["nextPhase"] == "phase12_wfm_data_databanks_resources_options"
    assert payload["previousGate"]["phase"] == "phase11_spp_closeout"
    assert payload["summary"]["chain"] == "Input=SPP / Output=WFM"
    assert payload["summary"]["activeCrossCheck"] == "WalkForwardMatrix"
    assert payload["summary"]["executionPolicy"] == "configuration_review_only_no_smoke_no_optimization_blocked_by_spp"
    assert "SPP output" in payload["summary"]["upstreamDependency"]
    state = json.loads((tmp_path / ".local" / "sqx142_task_config" / "session_state.json").read_text(encoding="utf-8"))
    assert state["currentPhase"] == "phase12_wfm_open"
    assert state["nextPhase"] == "phase12_wfm_data_databanks_resources_options"


def test_wfm_data_databanks_resources_options_keeps_dual_carrier_synced():
    root = ET.fromstring(
        """
        <Settings>
          <Data>
            <Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old Session" slippage="5" minDist="3" engine="MetaTrader4"><Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" /></Setup></Setups>
            <OutOfSample><Range dateFrom="2023.01.01" dateTo="2025.01.01" /></OutOfSample>
          </Data>
          <CustomData>
            <Setups>
              <Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old Session" slippage="5" minDist="3" engine="MetaTrader5">
                <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
                <Commissions><Method type="SizeBased" use="false"><Params><Param key="Commission">9</Param></Params></Method></Commissions>
                <MainTestValues engine="false" symbol="false" timeframe="false" dates="false" precision="false" distance="false" spread="false" slippage="false" commissions="false" />
              </Setup>
            </Setups>
          </CustomData>
          <Databanks>
            <Databank name="Input" value="Syntetic" />
            <Databank name="Output" value="SPP" />
          </Databanks>
          <Resources>
            <Symbols>
              <Symbol name="USDJPY_darwinex" source="4" precision="M1" timezone="UTC" broker="9">
                <InstrumentInfo instrument="USDJPY_darwinex" defaultSpread="1.4" broker="9" />
              </Symbol>
            </Symbols>
            <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
            <Instruments />
            <Sessions><Session name="Old Session" /></Sessions>
            <CustomIndicators />
            <CustomBlocks />
          </Resources>
          <Options>
            <BuildTradingOptions><Params>
              <Param key="Session">Old Session</Param>
              <Param key="MarketOpenSession">Old Session</Param>
              <Param key="LimitTimeRange">true</Param>
              <Param key="RealisticGapsHandling">true</Param>
              <Param key="StoreChartData">true</Param>
            </Params></BuildTradingOptions>
          </Options>
        </Settings>
        """
    )

    actions = apply_wfm_data_databanks_resources_options_to_root(root)

    assert any(item["field"] == "Data/OutOfSample/Range" and item["changed"] for item in actions)
    assert enforce_wfm_data_databanks_resources_options_guard(root) == []
    data_setup = root.find("./Data/Setups/Setup")
    custom_setup = root.find("./CustomData/Setups/Setup")
    assert data_setup is not None
    assert custom_setup is not None
    assert data_setup.get("dateFrom") == custom_setup.get("dateFrom") == "2017.10.02"
    assert data_setup.get("dateTo") == custom_setup.get("dateTo") == "2023.12.31"
    assert data_setup.get("testPrecision") == custom_setup.get("testPrecision") == "2"
    assert data_setup.get("session") == custom_setup.get("session") == "No Session"
    assert data_setup.get("engine") == "MetaTrader5 (hedged)"
    assert custom_setup.get("engine") == "MetaTrader4"
    assert data_setup.find("Chart").attrib == custom_setup.find("Chart").attrib == {
        "symbol": "AUDCAD_darwinex",
        "timeframe": "H1",
        "spread": "2.0",
    }
    assert root.findall("./Data/OutOfSample/Range") == []
    assert {
        databank.get("name"): databank.get("value")
        for databank in root.findall(".//Databanks/Databank")
    } == {"Input": "SPP", "Output": "WFM"}
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
    assert {symbol.get("name") for symbol in root.findall(".//Resources/Symbols/Symbol")} == {"AUDCAD_darwinex"}
    assert root.find(".//Resources/Symbols/Symbol").get("precision") == "TICK"
    assert root.find(".//Resources/Symbols/Symbol").get("timezone") == "EETUS"
    assert root.findall(".//Resources/Sessions/Session") == []
    options = {
        param.get("key"): param.text
        for param in root.findall(".//BuildTradingOptions/Params/Param")
        if param.get("key") in {"Session", "MarketOpenSession", "LimitTimeRange", "RealisticGapsHandling", "StoreChartData"}
    }
    assert options == {
        "Session": "No Session",
        "MarketOpenSession": "No Session",
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
    }


def test_wfm_data_databanks_resources_options_guard_rejects_divergent_carriers():
    root = ET.fromstring(
        """
        <Settings>
          <Data><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0" engine="MetaTrader5 (hedged)"><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" /></Setup></Setups></Data>
          <CustomData><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0" engine="MetaTrader4"><Chart symbol="AUDCAD_darwinex" timeframe="H4" spread="2.0" /><MainTestValues engine="false" /></Setup></Setups></CustomData>
          <Databanks><Databank name="Input" value="Syntetic" /><Databank name="Output" value="SPP" /></Databanks>
          <Resources><Symbols /><Brokers /><Sessions><Session name="Old Session" /></Sessions></Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">true</Param></Params></BuildTradingOptions></Options>
        </Settings>
        """
    )

    issues = enforce_wfm_data_databanks_resources_options_guard(root)

    assert any("chart mismatch for timeframe" in issue for issue in issues)
    assert any("CustomData MainTestValues" in issue for issue in issues)
    assert any("Databank Input" in issue for issue in issues)
    assert any("Databank Output" in issue for issue in issues)
    assert any("Resources" in issue or "resource" in issue for issue in issues)
    assert any("Options param" in issue for issue in issues)


def test_wfm_crosschecks_keep_matrix_filters_and_clean_hidden_methods():
    root = ET.fromstring(
        """
        <Settings>
          <Data><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0" engine="MetaTrader5 (hedged)"><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" /><Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission">0.0</Param></Params></Method></Commissions></Setup></Setups></Data>
          <CustomData><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0" engine="MetaTrader4"><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" /><Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission">0.0</Param></Params></Method></Commissions><MainTestValues engine="true" symbol="true" timeframe="true" dates="true" subcharts="false" precision="true" distance="true" spread="true" slippage="true" commissions="true" /></Setup></Setups></CustomData>
          <Databanks><Databank name="Input" value="SPP" /><Databank name="Output" value="WFM" /></Databanks>
          <Resources><Symbols><Symbol name="AUDCAD_darwinex" precision="TICK" timezone="EETUS" broker="4"><InstrumentInfo instrument="AUDCAD_darwinex" broker="4" /></Symbol></Symbols><Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers><Sessions /></Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">false</Param><Param key="RealisticGapsHandling">false</Param><Param key="StoreChartData">false</Param><Param key="Session">No Session</Param><Param key="MarketOpenSession">No Session</Param></Params></BuildTradingOptions></Options>
          <Rankings><ForceRunCrossChecks>true</ForceRunCrossChecks></Rankings>
          <CrossChecks use="true" evaluateAll="true">
            <RetestOnAdditionalMarkets use="false"><Settings><Setups><Setup dateFrom="2010.01.01" dateTo="2017.10.02" testPrecision="1" session="Old" slippage="3" minDist="2"><Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" /></Setup></Setups></Settings></RetestOnAdditionalMarkets>
            <WalkForwardOptimization use="true"><Settings><Methods><Method type="LegacyWFO" use="true" /></Methods></Settings></WalkForwardOptimization>
            <WalkForwardMatrix use="false">
              <Settings>
                <WalkForward type="1" period="5" optimization="10" distributionUp="10" distributionDown="10" maxSteps="4"><Param1 value="bad" /><Param2 value="bad" /></WalkForward>
                <MaxTests>10</MaxTests>
                <WhatToParametrize type="0" symmetricVariables="true"><Recommended>true</Recommended><Shifts>true</Shifts></WhatToParametrize>
              </Settings>
              <AcceptanceSettings><Conditions><Condition use="true"><Left-Side valueType="column"><Column-Value column="WFPctOfProfitableRuns" resultType="WalkForwardOptimization" sampleType="10" subresult="33" /></Left-Side><Comparator value="&gt;" /><Right-Side valueType="numeric"><Numeric-Value value="60" /></Right-Side></Condition></Conditions></AcceptanceSettings>
            </WalkForwardMatrix>
            <MonteCarloRetest use="false"><Settings><Methods><Method type="RandomizeSpread" use="true" /></Methods></Settings></MonteCarloRetest>
            <MonteCarloManipulation use="false"><Settings><Methods><Method type="RandomizeTradesOrder" use="true" /></Methods></Settings></MonteCarloManipulation>
            <WhatIf use="false"><Settings><Methods><Method type="ExcludeTradesWithBiggestPl" use="true" /></Methods></Settings></WhatIf>
          </CrossChecks>
        </Settings>
        """
    )

    actions = apply_wfm_crosschecks_to_root(root)

    assert any("MonteCarloRetest/Method:RandomizeSpread" in item["field"] and item["changed"] for item in actions)
    assert enforce_wfm_crosschecks_guard(root) == []
    summary = gate.wfm_crosschecks_summary(root)
    assert summary["active"] == ["WalkForwardMatrix"]
    wfm = next(item for item in summary["checks"] if item["id"] == "WalkForwardMatrix")
    assert wfm["settings"]["WalkForward"] == {
        "type": "2",
        "period": "10",
        "optimization": "15",
        "distributionUp": "20",
        "distributionDown": "20",
        "maxSteps": "8",
    }
    active_conditions = [
        (
            condition["left"].get("column"),
            condition["comparator"],
            condition["right"]["value"].get("value"),
        )
        for condition in wfm["conditions"]
        if condition["use"] == "true"
    ]
    assert active_conditions == [
        ("NetProfit", ">", "0"),
        ("NetProfit", ">", "60"),
        ("WFPctOfProfitableRuns", ">", "70"),
        ("WFMaxProfitByRunInPct", "<", "50"),
        ("WFMinTradesInRun", ">", "20"),
        ("WFMaxPctDDbyRun", "<=", "25"),
    ]
    inactive_methods = [
        method
        for check in summary["checks"]
        if check["id"] != "WalkForwardMatrix"
        for method in check["methods"]
    ]
    assert all(method["use"] == "false" for method in inactive_methods)
    assert root.findtext("./Rankings/ForceRunCrossChecks") == "false"
    setup = root.find(".//CrossChecks/RetestOnAdditionalMarkets/Settings/Setups/Setup")
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.find("Chart").attrib == {
        "symbol": "AUDCAD_darwinex",
        "timeframe": "H1",
        "spread": "2.0",
    }


def test_wfm_crosschecks_guard_rejects_lax_filters_and_hidden_methods():
    root = ET.fromstring(
        """
        <Settings>
          <Data><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0" engine="MetaTrader5 (hedged)"><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" /><Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission">0.0</Param></Params></Method></Commissions></Setup></Setups></Data>
          <CustomData><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0" engine="MetaTrader4"><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" /><Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission">0.0</Param></Params></Method></Commissions><MainTestValues engine="true" symbol="true" timeframe="true" dates="true" subcharts="false" precision="true" distance="true" spread="true" slippage="true" commissions="true" /></Setup></Setups></CustomData>
          <Databanks><Databank name="Input" value="SPP" /><Databank name="Output" value="WFM" /></Databanks>
          <Resources><Symbols><Symbol name="AUDCAD_darwinex" precision="TICK" timezone="EETUS" broker="4"><InstrumentInfo instrument="AUDCAD_darwinex" broker="4" /></Symbol></Symbols><Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers><Sessions /></Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">false</Param><Param key="RealisticGapsHandling">false</Param><Param key="StoreChartData">false</Param><Param key="Session">No Session</Param><Param key="MarketOpenSession">No Session</Param></Params></BuildTradingOptions></Options>
          <Rankings><ForceRunCrossChecks>true</ForceRunCrossChecks></Rankings>
          <CrossChecks use="true" evaluateAll="true">
            <WalkForwardOptimization use="true" />
            <WalkForwardMatrix use="true">
              <Settings><WalkForward type="2" period="10" optimization="15" distributionUp="20" distributionDown="20" maxSteps="8"><Param1 value="undefined" start="20" stop="36" step="2" /><Param2 value="undefined" start="5" stop="8" step="1" /></WalkForward><MaxTests>3000</MaxTests><WhatToParametrize type="1" symmetricVariables="false"><Recommended>false</Recommended><Periods>true</Periods><Shifts>false</Shifts><Constants>true</Constants><OtherParams>false</OtherParams><EntryParams>true</EntryParams><EntryLogic>false</EntryLogic><ExitParamsUsed>true</ExitParamsUsed><ExitParamsUnused>false</ExitParamsUnused><BooleanParams>false</BooleanParams></WhatToParametrize></Settings>
              <AcceptanceSettings><Conditions><Condition use="true"><Left-Side valueType="column"><Column-Value column="WFPctOfProfitableRuns" resultType="WalkForwardOptimization" sampleType="10" subresult="33" /></Left-Side><Comparator value="&gt;" /><Right-Side valueType="numeric"><Numeric-Value value="60" /></Right-Side></Condition></Conditions></AcceptanceSettings>
            </WalkForwardMatrix>
            <WhatIf use="false"><Settings><Methods><Method type="ExcludeTradesWithBiggestPl" use="true" /></Methods></Settings></WhatIf>
          </CrossChecks>
        </Settings>
        """
    )

    issues = enforce_wfm_crosschecks_guard(root)

    assert any("active crosschecks" in issue for issue in issues)
    assert any("acceptance conditions" in issue for issue in issues)
    assert any("still has active methods" in issue for issue in issues)
    assert any("ForceRunCrossChecks" in issue for issue in issues)


def test_wfm_static_tabs_make_rankings_inert_and_preserve_dual_customdata():
    root = ET.fromstring(
        """
        <Settings>
          <Data>
            <Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old Session" slippage="5" minDist="3" engine="MetaTrader4"><Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" /></Setup></Setups>
            <OutOfSample><Range dateFrom="2023.01.01" dateTo="2025.01.01" /></OutOfSample>
          </Data>
          <CustomData>
            <Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old Session" slippage="5" minDist="3" engine="MetaTrader5"><Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" /></Setup></Setups>
          </CustomData>
          <Databanks><Databank name="Input" value="Syntetic" /><Databank name="Output" value="SPP" /></Databanks>
          <Resources><Symbols><Symbol name="USDJPY_darwinex" source="4" precision="M1" timezone="UTC" broker="9"><InstrumentInfo instrument="USDJPY_darwinex" defaultSpread="1.4" broker="9" /></Symbol></Symbols><Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers><Sessions><Session name="Old Session" /></Sessions></Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">true</Param><Param key="RealisticGapsHandling">true</Param><Param key="StoreChartData">true</Param><Param key="Session">Old Session</Param><Param key="MarketOpenSession">Old Session</Param></Params></BuildTradingOptions></Options>
          <CrossChecks use="false" evaluateAll="false">
            <MonteCarloRetest use="false"><Settings><Methods><Method type="RandomizeSpread" use="true" /></Methods></Settings></MonteCarloRetest>
            <WalkForwardMatrix use="false" />
          </CrossChecks>
          <Rankings type="all">
            <MaxStrategies>5</MaxStrategies>
            <ConditionsType>2</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Old" />
            <CustomAnalysis filter="true" method="old" />
            <Conditions><Condition use="true" /></Conditions>
          </Rankings>
          <RiskMoneyManagement><MoneyManagement><Method type="FixedSize" use="false" /><Method type="FixedAmount" use="true" /></MoneyManagement></RiskMoneyManagement>
          <ATMs enable="true" />
          <Notes>ok</Notes>
          <SelectedStrategies><Strategy id="legacy" /></SelectedStrategies>
        </Settings>
        """
    )

    apply_wfm_data_databanks_resources_options_to_root(root)
    apply_wfm_crosschecks_to_root(root)
    actions = apply_wfm_static_tabs_to_root(root)

    assert any(item["field"] == "Rankings/DeleteFailedStrategies" and item["changed"] for item in actions)
    assert any(item["field"] == "SelectedStrategies" and item["changed"] for item in actions)
    assert enforce_wfm_static_tabs_guard(root) == []
    assert root.find("./Data") is not None
    rankings = root.find("./Rankings")
    assert rankings.get("type") == "never"
    assert rankings.findtext("DeleteFailedStrategies") == "false"
    assert rankings.findtext("ForceRunCrossChecks") == "false"
    assert rankings.findall("./Conditions/Condition") == []
    assert root.find(".//RiskMoneyManagement//Method[@type='FixedSize']").get("use") == "true"
    assert root.find(".//RiskMoneyManagement//Method[@type='FixedAmount']").get("use") == "false"
    assert root.find("./ATMs").get("enable") == "false"
    assert root.find("./SelectedStrategies").text is None
    data_setup = root.find("./Data/Setups/Setup")
    custom_setup = root.find("./CustomData/Setups/Setup")
    assert data_setup.find("Chart").attrib == custom_setup.find("Chart").attrib == {
        "symbol": "AUDCAD_darwinex",
        "timeframe": "H1",
        "spread": "2.0",
    }
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


def test_wfm_static_tabs_guard_rejects_ranking_portfolio_and_customdata_drift():
    root = ET.fromstring(
        """
        <Settings>
          <Data><Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old Session" slippage="5" minDist="3" engine="MetaTrader4"><Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" /></Setup></Setups></Data>
          <CustomData><Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old Session" slippage="5" minDist="3" engine="MetaTrader5"><Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" /></Setup></Setups></CustomData>
          <Databanks><Databank name="Input" value="Syntetic" /><Databank name="Output" value="SPP" /></Databanks>
          <Resources><Symbols><Symbol name="USDJPY_darwinex" source="4" precision="M1" timezone="UTC" broker="9"><InstrumentInfo instrument="USDJPY_darwinex" defaultSpread="1.4" broker="9" /></Symbol></Symbols><Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers><Sessions /></Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">true</Param><Param key="RealisticGapsHandling">true</Param><Param key="StoreChartData">true</Param><Param key="Session">Old Session</Param><Param key="MarketOpenSession">Old Session</Param></Params></BuildTradingOptions></Options>
          <CrossChecks use="false" evaluateAll="false"><WalkForwardMatrix use="false" /></CrossChecks>
          <Rankings type="all">
            <MaxStrategies>1</MaxStrategies>
            <ConditionsType>2</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Existing portfolio" />
            <CustomAnalysis filter="true" method="custom" />
            <Conditions><Condition use="true" /></Conditions>
          </Rankings>
          <RiskMoneyManagement><MoneyManagement><Method type="FixedSize" use="false" /><Method type="FixedAmount" use="true" /></MoneyManagement></RiskMoneyManagement>
          <ATMs enable="true" />
          <SelectedStrategies><Strategy id="legacy" /></SelectedStrategies>
        </Settings>
        """
    )

    apply_wfm_data_databanks_resources_options_to_root(root)
    apply_wfm_crosschecks_to_root(root)
    root.find("./Rankings/ForceRunCrossChecks").text = "true"
    custom_setup = root.find("./CustomData/Setups/Setup")
    custom_setup.set("dateFrom", "2010.01.01")
    custom_setup.find("MainTestValues").set("symbol", "false")

    issues = enforce_wfm_static_tabs_guard(root)

    assert any("Rankings type" in issue for issue in issues)
    assert any("DeleteFailedStrategies" in issue for issue in issues)
    assert any("ForceRunCrossChecks" in issue for issue in issues)
    assert any("FitPortfolio" in issue for issue in issues)
    assert any("CustomAnalysis" in issue for issue in issues)
    assert any("extra conditions" in issue for issue in issues)
    assert any("RiskMoneyManagement FixedSize" in issue for issue in issues)
    assert any("ATMs enable" in issue for issue in issues)
    assert any("SelectedStrategies" in issue for issue in issues)
    assert any("CustomData dates" in issue for issue in issues)
    assert any("CustomData MainTestValues" in issue for issue in issues)
    assert any("Data/Resources guard" in issue for issue in issues)
    assert any("CrossChecks guard" in issue for issue in issues)


def _foward_source_root() -> ET.Element:
    return ET.fromstring(
        """
        <Task>
          <Blocks type="simple" version="142.2336">
            <BuildingBlocks>
              <Block key="Signals.ADX" category="signals" use="false" probability="1" />
              <Block key="Indicators.ATR" category="indicators" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="false" probability="1" />
            </BuildingBlocks>
            <OrderTypes>
              <Block key="EnterAtMarket" use="true" probability="1" />
              <Block key="EnterReverseAtMarket" use="false" probability="1" />
              <Block key="EnterAtStop" use="false" probability="1" />
              <Block key="EnterAtLimit" use="false" probability="1" />
            </OrderTypes>
            <ExitTypes>
              <Block key="ExitAfterBars.ExitAfterBars" use="true" probability="100" />
              <Block key="StopLoss.StopLoss" use="false" probability="50" />
            </ExitTypes>
            <CustomData showAll="false" />
          </Blocks>
        </Task>
        """
    )


def _foward_dirty_root() -> ET.Element:
    return ET.fromstring(
        """
        <Task>
          <Data>
            <Setups><Setup dateFrom="2024.01.01" dateTo="2026.04.30" testPrecision="1" session="Old Session" slippage="5" minDist="3" engine="MetaTrader4"><Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" /></Setup></Setups>
            <OutOfSample showGraph="true"><Range dateFrom="2024.01.01" dateTo="2025.01.01" /></OutOfSample>
          </Data>
          <Databanks><Databank name="Input" value="WFM" /><Databank name="Output" value="old" /></Databanks>
          <Resources><Symbols><Symbol name="USDJPY_darwinex" source="4" precision="M1" timezone="UTC" broker="9"><InstrumentInfo instrument="USDJPY_darwinex" defaultSpread="1.4" broker="9" dataType="3" /></Symbol></Symbols><Brokers><Broker id="9" name="Old" /></Brokers><Instruments /><Sessions><Session name="Old Session" /></Sessions><CustomIndicators /><CustomBlocks /></Resources>
          <Options><BuildTradingOptions><Params>
            <Param key="Session">Old Session</Param>
            <Param key="MarketOpenSession">Old Session</Param>
            <Param key="LimitTimeRange">false</Param>
            <Param key="SignalTimeRangeFrom">28800</Param>
            <Param key="SignalTimeRangeTo">57600</Param>
            <Param key="RealisticGapsHandling">false</Param>
            <Param key="StoreChartData">true</Param>
          </Params></BuildTradingOptions></Options>
          <CrossChecks use="true" evaluateAll="true"><MonteCarloRetest use="false"><Settings><Methods><Method type="RandomizeSpread" use="true" /></Methods></Settings></MonteCarloRetest><WhatIf use="false"><Settings><Methods><Method type="ExcludeTradesWithBiggestPl" use="true" /></Methods></Settings></WhatIf></CrossChecks>
          <Rankings type="all"><MaxStrategies>1</MaxStrategies><ConditionsType>2</ConditionsType><DeleteFailedStrategies>true</DeleteFailedStrategies><ForceRunCrossChecks>true</ForceRunCrossChecks><FitPortfolio active="true" databank="Existing portfolio" /><Conditions /></Rankings>
          <RiskMoneyManagement><MoneyManagement><Method type="FixedSize" use="false" /><Method type="FixedAmount" use="true" /></MoneyManagement></RiskMoneyManagement>
          <ATMs enable="true" />
          <SelectedStrategies><Strategy id="legacy" /></SelectedStrategies>
          <PartsToImprove><EntryRules><LongImprovement use="true" /><ShortImprovement use="true" /></EntryRules><OrderTypes><LongImprovement use="true" /><ShortImprovement use="true" /></OrderTypes><ExitRules><LongImprovement use="true" /><ShortImprovement use="true" /></ExitRules></PartsToImprove>
          <WhatToBuild><StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" /><BuildMode generationType="random-generation"><ShowLastGenerationDatabank>true</ShowLastGenerationDatabank><FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar><FreshBloodReplaceWeakest>true</FreshBloodReplaceWeakest><EvoRestartOnFinish status="true" /><EvoRestartOnStagnation status="true" fitnessType="10" generations="30" /></BuildMode></WhatToBuild>
          <Blocks type="simple"><BuildingBlocks><Block key="Signals.ADX" category="signals" use="true" /><Block key="Indicators.ATR" category="indicators" use="true" /><Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="true" /></BuildingBlocks><OrderTypes><Block key="EnterAtMarket" use="false" /><Block key="EnterReverseAtMarket" use="true" /><Block key="EnterAtStop" use="true" /><Block key="EnterAtLimit" use="true" /></OrderTypes><ExitTypes><Block key="ExitAfterDays.ExitAfterDays" use="true" probability="50" /></ExitTypes><CustomData showAll="true"><Item /></CustomData></Blocks>
        </Task>
        """
    )


def test_foward_data_databanks_resources_options_keeps_forward_oos_blocks():
    root = _foward_dirty_root()

    actions = apply_foward_data_databanks_resources_options_to_root(root)

    assert any(item["field"] == "Data/OutOfSample" and item["changed"] for item in actions)
    assert enforce_foward_data_databanks_resources_options_guard(root) == []
    setup = root.find(".//Data/Setups/Setup")
    assert setup.get("dateFrom") == "2025.01.01"
    assert setup.get("dateTo") == "2026.04.08"
    assert setup.get("testPrecision") == "2"
    assert setup.find("Chart").attrib == {"symbol": "AUDCAD_darwinex", "timeframe": "H1", "spread": "2.0"}
    assert [node.attrib for node in root.findall(".//Data/OutOfSample/Range")] == [
        {"dateFrom": "2025.01.01", "dateTo": "2026.01.01"},
        {"dateFrom": "2026.01.01", "dateTo": "2026.04.08"},
    ]
    assert {node.get("name"): node.get("value") for node in root.findall(".//Databanks/Databank")} == {
        "Input": "Syntetic",
        "Output": "Foward",
    }
    symbol = root.find(".//Resources/Symbols/Symbol")
    assert symbol.get("name") == "AUDCAD_darwinex"
    assert symbol.get("precision") == "TICK"
    assert root.findall(".//Resources/Sessions/Session") == []
    options = {node.get("key"): node.text for node in root.findall(".//BuildTradingOptions/Params/Param")}
    assert options["RealisticGapsHandling"] == "true"
    assert options["StoreChartData"] == "false"


def test_foward_crosschecks_and_static_tabs_make_task_passive():
    root = _foward_dirty_root()
    source_root = _foward_source_root()

    apply_foward_data_databanks_resources_options_to_root(root)
    apply_foward_crosschecks_to_root(root)
    actions = apply_foward_static_tabs_to_root(root, source_root)

    assert any(item["field"] == "Rankings/Conditions" and item["changed"] for item in actions)
    assert enforce_foward_crosschecks_guard(root) == []
    assert enforce_foward_static_tabs_guard(root) == []
    rankings = root.find(".//Rankings")
    assert rankings.findtext("DeleteFailedStrategies") == "false"
    assert rankings.find("FitPortfolio").get("active") == "false"
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
        ("NumberOfTrades", "20", ">=", "30"),
        ("RExpectancy", "20", ">", "0"),
        ("NetProfit", "20", ">=", "0"),
    ]
    assert root.find(".//RiskMoneyManagement//Method[@type='FixedSize']").get("use") == "true"
    assert root.find(".//RiskMoneyManagement//Method[@type='FixedAmount']").get("use") == "false"
    assert root.find("./SelectedStrategies").text is None
    assert root.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "Syntetic"
    assert root.find(".//ExitTypes/Block[@key='ExitAfterBars.ExitAfterBars']").get("probability") == "100"
    assert root.findall(".//ExitTypes/Block[@key='ExitAfterDays.ExitAfterDays']") == []


def test_foward_static_tabs_guard_rejects_generation_and_ranking_drift():
    root = _foward_dirty_root()
    apply_foward_data_databanks_resources_options_to_root(root)
    apply_foward_crosschecks_to_root(root)

    issues = enforce_foward_static_tabs_guard(root)

    assert any("Rankings type" in issue for issue in issues)
    assert any("DeleteFailedStrategies" in issue for issue in issues)
    assert any("FitPortfolio" in issue for issue in issues)
    assert any("ranking conditions" in issue for issue in issues)
    assert any("RiskMoneyManagement FixedSize" in issue for issue in issues)
    assert any("Passive generation guard" in issue for issue in issues)


def test_foward_capa1_closeout_report_writes_final_phase_state(monkeypatch, tmp_path):
    monkeypatch.setattr(gate, "foward_closeout_report", lambda *args, **kwargs: {
        "phase": "phase13_foward_closeout",
        "ok": True,
        "issues": [],
        "nextPhase": "phase14_capa1_closeout",
    })
    monkeypatch.setattr(gate, "process_snapshot", lambda: {"processes": []})

    payload = gate.capa1_closeout_report(tmp_path, tmp_path, target="both", write=True)

    assert payload["ok"] is True
    assert payload["phase"] == "phase14_capa1_closeout"
    assert payload["nextPhase"] == "phase15_capa2_planning"
    assert payload["previousGate"]["phase"] == "phase13_foward_closeout"
    assert "Build -> RETEST 0" in payload["summary"]["finalChain"]
    assert payload["summary"]["agents"]["testRunner"].startswith("SQX Test Guardian")
    state = json.loads((tmp_path / ".local" / "sqx142_task_config" / "session_state.json").read_text(encoding="utf-8"))
    assert state["currentPhase"] == "phase14_capa1_closeout"
    assert state["nextPhase"] == "phase15_capa2_planning"


def test_spp_data_databanks_resources_options_keeps_customdata_only_and_inert_options():
    root = ET.fromstring(
        """
        <Settings>
          <Data>
            <Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old Session"><Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" /></Setup></Setups>
            <OutOfSample><Range dateFrom="2023.01.01" dateTo="2025.01.01" /></OutOfSample>
          </Data>
          <CustomData>
            <Setups>
              <Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old Session" slippage="5" minDist="3" engine="MetaTrader5">
                <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
                <Commissions><Method type="SizeBased" use="false"><Params><Param key="Commission">9</Param></Params></Method></Commissions>
                <MainTestValues engine="false" symbol="false" timeframe="false" dates="false" precision="false" distance="false" spread="false" slippage="false" commissions="false" />
              </Setup>
            </Setups>
          </CustomData>
          <Databanks>
            <Databank name="Input" value="Monkey Test" />
            <Databank name="Output" value="Syntetic" />
          </Databanks>
          <Resources>
            <Symbols>
              <Symbol name="USDJPY_darwinex" source="4" precision="M1" timezone="UTC" broker="9">
                <InstrumentInfo instrument="USDJPY_darwinex" defaultSpread="1.4" broker="9" />
              </Symbol>
            </Symbols>
            <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
            <Instruments />
            <Sessions><Session name="Old Session" /></Sessions>
            <CustomIndicators />
            <CustomBlocks />
          </Resources>
          <Options>
            <BuildTradingOptions><Params>
              <Param key="Session">Old Session</Param>
              <Param key="MarketOpenSession">Old Session</Param>
              <Param key="LimitTimeRange">true</Param>
              <Param key="RealisticGapsHandling">true</Param>
              <Param key="StoreChartData">true</Param>
            </Params></BuildTradingOptions>
          </Options>
        </Settings>
        """
    )

    actions = apply_spp_data_databanks_resources_options_to_root(root)

    assert any(item["field"] == "Data" and item["changed"] for item in actions)
    assert enforce_spp_data_databanks_resources_options_guard(root) == []
    assert root.find("Data") is None
    setup = root.find("./CustomData/Setups/Setup")
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == "2"
    assert setup.get("session") == "No Session"
    assert setup.get("engine") == "MetaTrader4"
    assert setup.find("Chart").attrib == {
        "symbol": "AUDCAD_darwinex",
        "timeframe": "H1",
        "spread": "2.0",
    }
    assert setup.find("./Commissions/Method[@type='SizeBased']").get("use") == "true"
    assert setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']").text == "0.0"
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
    assert {
        databank.get("name"): databank.get("value")
        for databank in root.findall(".//Databanks/Databank")
    } == {"Input": "Syntetic", "Output": "SPP"}
    assert {symbol.get("name") for symbol in root.findall(".//Resources/Symbols/Symbol")} == {"AUDCAD_darwinex"}
    assert root.find(".//Resources/Symbols/Symbol").get("precision") == "TICK"
    assert root.find(".//Resources/Sessions/Session") is None
    options = {
        param.get("key"): param.text
        for param in root.findall(".//BuildTradingOptions/Params/Param")
        if param.get("key") in {"Session", "MarketOpenSession", "LimitTimeRange", "RealisticGapsHandling", "StoreChartData"}
    }
    assert options == {
        "Session": "No Session",
        "MarketOpenSession": "No Session",
        "LimitTimeRange": "false",
        "RealisticGapsHandling": "false",
        "StoreChartData": "false",
    }


def test_spp_data_databanks_resources_options_guard_rejects_data_and_donor_drift():
    root = ET.fromstring(
        """
        <Settings>
          <Data><Setups><Setup><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" /></Setup></Setups></Data>
          <CustomData>
            <Setups>
              <Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old Session" engine="MetaTrader5">
                <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
                <MainTestValues engine="false" />
              </Setup>
            </Setups>
          </CustomData>
          <Databanks><Databank name="Input" value="Monkey Test" /><Databank name="Output" value="Syntetic" /></Databanks>
          <Resources>
            <Symbols><Symbol name="USDJPY_darwinex" precision="M1" timezone="UTC" broker="9"><InstrumentInfo broker="9" /></Symbol></Symbols>
            <Brokers><Broker id="4" /></Brokers>
            <Sessions><Session name="Old Session" /></Sessions>
          </Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">true</Param></Params></BuildTradingOptions></Options>
        </Settings>
        """
    )

    issues = enforce_spp_data_databanks_resources_options_guard(root)

    assert any("Data section" in issue for issue in issues)
    assert any("CustomData dates" in issue for issue in issues)
    assert any("CustomData chart symbol" in issue for issue in issues)
    assert any("Databank Input" in issue for issue in issues)
    assert any("precision is not TICK" in issue for issue in issues)
    assert any("session entries" in issue for issue in issues)
    assert any("Options param Session" in issue for issue in issues)
    assert any("Forbidden donor token" in issue for issue in issues)


def _spp_data_gate_fixture() -> str:
    return """
      <CustomData>
        <Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0" engine="MetaTrader4">
          <Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" />
          <Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">0.0</Param></Params></Method></Commissions>
          <MainTestValues engine="true" symbol="true" timeframe="true" dates="true" precision="true" distance="true" spread="true" slippage="true" commissions="true" />
        </Setup></Setups>
      </CustomData>
      <Databanks><Databank name="Input" value="Syntetic" /><Databank name="Output" value="SPP" /></Databanks>
      <Resources>
        <Symbols><Symbol name="AUDCAD_darwinex" precision="TICK" timezone="EETUS" broker="4"><InstrumentInfo instrument="AUDCAD_darwinex" broker="4" /></Symbol></Symbols>
        <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
        <Instruments><InstrumentInfo instrument="AUDCAD_darwinex" broker="4" /></Instruments>
        <Sessions />
      </Resources>
      <Options><BuildTradingOptions><Params>
        <Param key="LimitTimeRange">false</Param>
        <Param key="RealisticGapsHandling">false</Param>
        <Param key="StoreChartData">false</Param>
        <Param key="Session">No Session</Param>
        <Param key="MarketOpenSession">No Session</Param>
      </Params></BuildTradingOptions></Options>
    """


def test_spp_crosschecks_keeps_optprofile_filters_and_cleans_inactive_methods():
    root = ET.fromstring(
        f"""
        <Settings>
          {_spp_data_gate_fixture()}
          <CrossChecks use="false" evaluateAll="false">
            <RetestOnAdditionalMarkets use="false">
              <Settings><Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old" slippage="5" minDist="2">
                <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
              </Setup></Setups></Settings>
            </RetestOnAdditionalMarkets>
            <MonteCarloManipulation use="false">
              <Settings><Methods><Method type="RandomizeTradesOrder" use="true" /><Method type="RandomlySkipTrades" use="true" /></Methods></Settings>
            </MonteCarloManipulation>
            <MonteCarloRetest use="false">
              <Settings><Methods>
                <Method type="RandomizeHistoryData" use="true" />
                <Method type="RandomizeSpread" use="true"><Params><Param key="Min">1</Param><Param key="Max">5</Param></Params></Method>
              </Methods></Settings>
            </MonteCarloRetest>
            <OptProfileSysParamPermutation use="true">
              <Settings>
                <MaxTests>1000</MaxTests><DistributionUp>50</DistributionUp><DistributionDown>50</DistributionDown><Steps>10</Steps>
                <WhatToParametrize type="2" symmetricVariables="true"><Recommended>true</Recommended><Periods>false</Periods><EntryLogic>true</EntryLogic></WhatToParametrize>
              </Settings>
              <AcceptanceSettings>
                <ProfitOptPct>10</ProfitOptPct><AvgProfit>5</AvgProfit><UniformDistrChanges>99</UniformDistrChanges><StdevAvgProfit>2</StdevAvgProfit>
                <EvalProfitOptCheck>false</EvalProfitOptCheck><EvalAvgProfitCheck>false</EvalAvgProfitCheck><EvalUniformDistrCheck>false</EvalUniformDistrCheck><EvalTopProfitCheck>true</EvalTopProfitCheck>
                <Conditions><Condition use="false" /></Conditions>
              </AcceptanceSettings>
            </OptProfileSysParamPermutation>
          </CrossChecks>
          <Rankings><ForceRunCrossChecks>false</ForceRunCrossChecks></Rankings>
        </Settings>
        """
    )

    actions = apply_spp_crosschecks_to_root(root)

    assert any(item["field"] == "CrossChecks:attrs" and item["changed"] for item in actions)
    assert any(item["field"] == "CrossChecks/MonteCarloRetest/Method:RandomizeSpread:use" and item["changed"] for item in actions)
    assert enforce_spp_crosschecks_guard(root) == []
    summary = gate.spp_crosschecks_summary(root)
    assert summary["active"] == ["OptProfileSysParamPermutation"]
    spp = next(item for item in summary["checks"] if item["id"] == "OptProfileSysParamPermutation")
    assert spp["settings"]["MaxTests"] == "3000"
    assert spp["settings"]["DistributionUp"] == "20"
    assert spp["settings"]["DistributionDown"] == "20"
    assert spp["settings"]["Steps"] == "25"
    assert spp["settings"]["ParametrizeFlags"]["EntryParams"] == "true"
    assert spp["settings"]["ParametrizeFlags"]["EntryLogic"] == "false"
    assert spp["acceptanceSettings"]["ProfitOptPct"] == "30"
    assert spp["acceptanceSettings"]["EvalTopProfitCheck"] == "false"
    assert len(spp["conditions"]) == 2
    assert spp["conditions"][0]["left"]["column"] == "NetProfit"
    assert spp["conditions"][0]["comparator"] == ">="
    assert spp["conditions"][0]["right"]["pctRatio"] == "50"
    assert spp["conditions"][1]["left"]["column"] == "DrawdownPct"
    assert spp["conditions"][1]["comparator"] == "<="
    assert spp["conditions"][1]["right"]["pctRatio"] == "200"
    inactive_methods = [
        method
        for check in summary["checks"]
        for method in check["methods"]
    ]
    assert all(method["use"] == "false" for method in inactive_methods)
    setup = root.find(".//CrossChecks/RetestOnAdditionalMarkets/Settings/Setups/Setup")
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == "2"
    assert setup.find("Chart").attrib == {"symbol": "AUDCAD_darwinex", "timeframe": "H1", "spread": "2.0"}


def test_spp_crosschecks_guard_rejects_active_hidden_methods_bad_filters_and_force_run():
    root = ET.fromstring(
        f"""
        <Settings>
          {_spp_data_gate_fixture()}
          <CrossChecks use="true" evaluateAll="true">
            <MonteCarloRetest use="false"><Settings><Methods><Method type="RandomizeSpread" use="true" /></Methods></Settings></MonteCarloRetest>
            <OptProfileSysParamPermutation use="true">
              <Settings>
                <MaxTests>999</MaxTests><DistributionUp>20</DistributionUp><DistributionDown>20</DistributionDown><Steps>25</Steps>
                <WhatToParametrize type="1" symmetricVariables="false"><Recommended>false</Recommended><Periods>true</Periods><Constants>true</Constants></WhatToParametrize>
              </Settings>
              <AcceptanceSettings><ProfitOptPct>30</ProfitOptPct><Conditions><Condition use="false" /></Conditions></AcceptanceSettings>
            </OptProfileSysParamPermutation>
          </CrossChecks>
          <Rankings><ForceRunCrossChecks>true</ForceRunCrossChecks></Rankings>
        </Settings>
        """
    )

    issues = enforce_spp_crosschecks_guard(root)

    assert any("MaxTests" in issue for issue in issues)
    assert any("ParametrizeFlags" in issue for issue in issues)
    assert any("AcceptanceSettings" in issue for issue in issues)
    assert any("acceptance conditions" in issue for issue in issues)
    assert any("active methods" in issue for issue in issues)
    assert any("ForceRunCrossChecks" in issue for issue in issues)


def test_spp_static_tabs_make_rankings_inert_and_preserve_spp_customdata():
    root = ET.fromstring(
        f"""
        <Settings>
          {_spp_data_gate_fixture()}
          <CrossChecks use="false" evaluateAll="false">
            <MonteCarloRetest use="false"><Settings><Methods><Method type="RandomizeSpread" use="true" /></Methods></Settings></MonteCarloRetest>
            <OptProfileSysParamPermutation use="true">
              <Settings><MaxTests>1000</MaxTests><DistributionUp>50</DistributionUp><DistributionDown>50</DistributionDown><Steps>10</Steps></Settings>
              <AcceptanceSettings><Conditions><Condition use="false" /></Conditions></AcceptanceSettings>
            </OptProfileSysParamPermutation>
          </CrossChecks>
          <Data><Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01"><Chart symbol="USDJPY_darwinex" timeframe="H4" /></Setup></Setups></Data>
          <Rankings type="all">
            <MaxStrategies>5</MaxStrategies>
            <ConditionsType>2</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Old" />
            <CustomAnalysis filter="true" method="old" />
            <Conditions><Condition use="true" /></Conditions>
          </Rankings>
          <RiskMoneyManagement><MoneyManagement><Method type="FixedSize" use="false" /><Method type="FixedAmount" use="true" /></MoneyManagement></RiskMoneyManagement>
          <ATMs enable="true" />
          <Notes>ok</Notes>
          <SelectedStrategies><Strategy id="legacy" /></SelectedStrategies>
        </Settings>
        """
    )

    apply_spp_crosschecks_to_root(root)
    actions = apply_spp_static_tabs_to_root(root)

    assert any(item["field"] == "Rankings/DeleteFailedStrategies" and item["changed"] for item in actions)
    assert any(item["field"] == "SelectedStrategies" and item["changed"] for item in actions)
    assert enforce_spp_static_tabs_guard(root) == []
    assert root.find("./Data") is None
    rankings = root.find("./Rankings")
    assert rankings.get("type") == "never"
    assert rankings.findtext("DeleteFailedStrategies") == "false"
    assert rankings.findtext("ForceRunCrossChecks") == "false"
    assert rankings.findall("./Conditions/Condition") == []
    assert root.find(".//RiskMoneyManagement//Method[@type='FixedSize']").get("use") == "true"
    assert root.find(".//RiskMoneyManagement//Method[@type='FixedAmount']").get("use") == "false"
    assert root.find("./ATMs").get("enable") == "false"
    assert root.find("./SelectedStrategies").text is None
    setup = root.find("./CustomData/Setups/Setup")
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.find("Chart").attrib == {"symbol": "AUDCAD_darwinex", "timeframe": "H1", "spread": "2.0"}


def test_spp_static_tabs_guard_rejects_ranking_portfolio_and_customdata_drift():
    root = ET.fromstring(
        f"""
        <Settings>
          {_spp_data_gate_fixture()}
          <CrossChecks use="true" evaluateAll="true">
            <OptProfileSysParamPermutation use="true">
              <Settings><MaxTests>3000</MaxTests><DistributionUp>20</DistributionUp><DistributionDown>20</DistributionDown><Steps>25</Steps></Settings>
              <AcceptanceSettings><Conditions><Condition use="false" /></Conditions></AcceptanceSettings>
            </OptProfileSysParamPermutation>
          </CrossChecks>
          <Rankings type="all">
            <MaxStrategies>1</MaxStrategies>
            <ConditionsType>2</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Existing portfolio" />
            <CustomAnalysis filter="true" method="custom" />
            <Conditions><Condition use="true" /></Conditions>
          </Rankings>
          <RiskMoneyManagement><MoneyManagement><Method type="FixedSize" use="false" /><Method type="FixedAmount" use="true" /></MoneyManagement></RiskMoneyManagement>
          <ATMs enable="true" />
          <SelectedStrategies><Strategy id="legacy" /></SelectedStrategies>
          <CustomData>
            <Setups><Setup dateFrom="2017.10.02" dateTo="2024.12.31" testPrecision="4" session="Old">
              <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
            </Setup></Setups>
          </CustomData>
        </Settings>
        """
    )

    root.remove(root.findall("./CustomData")[0])
    issues = enforce_spp_static_tabs_guard(root)

    assert any("Rankings type" in issue for issue in issues)
    assert any("DeleteFailedStrategies" in issue for issue in issues)
    assert any("ForceRunCrossChecks" in issue for issue in issues)
    assert any("FitPortfolio" in issue for issue in issues)
    assert any("CustomAnalysis" in issue for issue in issues)
    assert any("extra conditions" in issue for issue in issues)
    assert any("RiskMoneyManagement FixedSize" in issue for issue in issues)
    assert any("ATMs enable" in issue for issue in issues)
    assert any("SelectedStrategies" in issue for issue in issues)
    assert any("CustomData dates" in issue for issue in issues)
    assert any("Forbidden donor token" in issue for issue in issues)
    assert any("CrossChecks guard" in issue for issue in issues)


def test_monkey_passive_generation_points_to_sequential_and_preserves_indicator_universe():
    root = ET.fromstring(
        f"""
        <Settings>
          {_monkey_data_gate_fixture()}
          <PartsToImprove>
            <EntryRules><LongImprovement use="true" /><ShortImprovement use="true" /></EntryRules>
            <OrderTypes><LongImprovement use="true" /><ShortImprovement use="true" /></OrderTypes>
            <ExitRules><LongImprovement use="true" /><ShortImprovement use="true" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>true</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="true" />
              <EvoRestartOnStagnation status="true" fitnessType="10" generations="10" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="legacy" version="old">
            <BuildingBlocks>
              <Block key="Signals.CCI" category="signals" use="true" />
              <Block key="Indicators.ATR" category="indicators" use="true" />
              <Block key="StopLimit.ATR" category="stopLimitBlocks" use="true" />
            </BuildingBlocks>
            <OrderTypes>
              <Block key="EnterAtMarket" use="false" />
              <Block key="EnterReverseAtMarket" use="true" />
              <Block key="EnterAtStop" use="true" />
              <Block key="EnterAtLimit" use="true" />
            </OrderTypes>
            <ExitTypes>
              <Block key="ExitAfterBars.ExitAfterBars" use="false" probability="25"><Value key="undefined" use="false" /></Block>
              <Block key="ExitAfterDays.ExitAfterDays" use="true" probability="100" />
              <Block key="StopLoss" use="true" probability="1" />
            </ExitTypes>
            <CustomData showAll="true"><External /></CustomData>
          </Blocks>
        </Settings>
        """
    )
    apply_monkey_crosschecks_to_root(root)

    actions = apply_monkey_passive_generation_to_root(root, source_root=root)

    assert any(item["field"] == "WhatToBuild/StrategyType" and item["changed"] for item in actions)
    assert enforce_monkey_passive_generation_guard(root) == []
    strategy_type = root.find("./WhatToBuild/StrategyType")
    assert strategy_type.get("improveDatabank") == "Sequential"
    build_mode = root.find("./WhatToBuild/BuildMode")
    assert build_mode.findtext("ShowLastGenerationDatabank") == "false"
    assert build_mode.find("EvoRestartOnFinish").get("status") == "false"
    assert build_mode.find("EvoRestartOnStagnation").get("status") == "false"
    blocks = root.find("./Blocks")
    assert blocks.get("version") == "142.2336"
    assert blocks.find("./BuildingBlocks/Block[@key='Indicators.ATR']").get("use") == "true"
    assert blocks.find("./BuildingBlocks/Block[@key='Signals.CCI']").get("use") == "false"
    assert blocks.find("./BuildingBlocks/Block[@key='StopLimit.ATR']").get("use") == "false"
    assert blocks.find("./OrderTypes/Block[@key='EnterAtMarket']").get("use") == "true"
    assert blocks.find("./ExitTypes/Block[@key='ExitAfterBars.ExitAfterBars']").get("probability") == "100"
    assert "ExitAfterDays" not in ET.tostring(blocks, encoding="unicode")
    assert list(blocks.find("./CustomData")) == []


def test_monkey_passive_generation_guard_rejects_generation_remnants_and_day_exits():
    root = ET.fromstring(
        f"""
        <Settings>
          {_monkey_data_gate_fixture()}
          <PartsToImprove>
            <EntryRules><LongImprovement use="false" /><ShortImprovement use="false" /></EntryRules>
            <OrderTypes><LongImprovement use="false" /><ShortImprovement use="false" /></OrderTypes>
            <ExitRules><LongImprovement use="false" /><ShortImprovement use="false" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Sequential" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>false</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>false</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>false</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="false" />
              <EvoRestartOnStagnation status="false" fitnessType="10" generations="10" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple" version="142.2336">
            <BuildingBlocks>
              <Block key="Signals.CCI" category="signals" use="true" />
              <Block key="Indicators.ATR" category="indicators" use="true" />
              <Block key="StopLimit.ATR" category="stopLimitBlocks" use="true" />
            </BuildingBlocks>
            <OrderTypes>
              <Block key="EnterAtMarket" use="false" />
              <Block key="EnterReverseAtMarket" use="false" />
              <Block key="EnterAtStop" use="false" />
              <Block key="EnterAtLimit" use="false" />
            </OrderTypes>
            <ExitTypes>
              <Block key="ExitAfterBars.ExitAfterBars" use="true" probability="50" />
              <Block key="ExitAfterDays.ExitAfterDays" use="true" probability="100" />
            </ExitTypes>
            <CustomData showAll="true"><External /></CustomData>
          </Blocks>
        </Settings>
        """
    )
    apply_monkey_crosschecks_to_root(root)

    issues = enforce_monkey_passive_generation_guard(root)

    assert any("order types" in issue for issue in issues)
    assert any("ExitAfterBars probability" in issue for issue in issues)
    assert any("day-based" in issue or "ExitAfterDays" in issue for issue in issues)
    assert any("signals" in issue for issue in issues)
    assert any("stop/limit" in issue for issue in issues)
    assert any("CustomData" in issue for issue in issues)


def test_monkey_static_tabs_closes_rankings_risk_and_customdata_without_turning_off_real_monkey():
    root = ET.fromstring(
        f"""
        <Settings>
          {_monkey_data_gate_fixture()}
          <CrossChecks use="false" evaluateAll="false">
            <MonteCarloRetest use="false">
              <Settings>
                <NumberOfSimulations>50</NumberOfSimulations>
                <MCUseFullSample>false</MCUseFullSample>
                <MCBacktestPrecision>2</MCBacktestPrecision>
                <Methods>
                  <Method type="RealMonkeyTest" use="false"><Params><Param key="MaxChange" type="Integer">50</Param></Params></Method>
                  <Method type="SyntheticBootstrapV3" use="true" />
                </Methods>
              </Settings>
              <AcceptanceSettings><Conditions CrossCheck="MonteCarloRetest"><Condition use="false" /></Conditions></AcceptanceSettings>
            </MonteCarloRetest>
          </CrossChecks>
          <PartsToImprove>
            <EntryRules><LongImprovement use="true" /><ShortImprovement use="true" /></EntryRules>
            <OrderTypes><LongImprovement use="true" /><ShortImprovement use="true" /></OrderTypes>
            <ExitRules><LongImprovement use="true" /><ShortImprovement use="true" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>false</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="true" />
              <EvoRestartOnStagnation status="true" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple">
            <BuildingBlocks>
              <Block key="Signals.ADX" category="signals" use="true" probability="1" />
              <Block key="Indicators.ATR" category="indicators" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="true" probability="1" />
            </BuildingBlocks>
            <OrderTypes><Block key="EnterAtMarket" use="false" /><Block key="EnterReverseAtMarket" use="true" /><Block key="EnterAtStop" use="true" /><Block key="EnterAtLimit" use="true" /></OrderTypes>
            <ExitTypes><Block key="ExitAfterBars.ExitAfterBars" use="false" probability="50" /></ExitTypes>
            <CustomData showAll="true"><Item /></CustomData>
          </Blocks>
          <Rankings type="always">
            <MaxStrategies>500</MaxStrategies>
            <ConditionsType>1</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Existing portfolio" />
            <CustomAnalysis filter="true" inputArgs="" method="none" />
            <Conditions><Condition use="true"><Left-Side><Column-Value column="NetProfit" /></Left-Side><Comparator value="&gt;=" /><Right-Side><Numeric-Value value="1" /></Right-Side></Condition></Conditions>
          </Rankings>
          <RiskMoneyManagement><MoneyManagement><Method type="FixedSize" use="false" /><Method type="FixedAmount" use="true" /></MoneyManagement></RiskMoneyManagement>
          <ATMs enable="true" />
          <Notes>ok</Notes>
          <SelectedStrategies><Strategy id="legacy" /></SelectedStrategies>
        </Settings>
        """
    )

    apply_monkey_crosschecks_to_root(root)
    apply_monkey_passive_generation_to_root(root, source_root=root)
    actions = apply_monkey_static_tabs_to_root(root)

    assert any(item["field"] == "Rankings/FitPortfolio" and item["changed"] for item in actions)
    assert enforce_monkey_static_tabs_guard(root) == []
    assert root.find(".//CrossChecks/MonteCarloRetest").get("use") == "true"
    assert root.find(".//CrossChecks/MonteCarloRetest/Settings/Methods/Method[@type='RealMonkeyTest']").get("use") == "true"
    assert root.find(".//Rankings").get("type") == "never"
    assert root.find(".//Rankings/DeleteFailedStrategies").text == "false"
    assert root.find(".//Rankings/ForceRunCrossChecks").text == "false"
    assert root.find(".//RiskMoneyManagement//Method[@type='FixedSize']").get("use") == "true"
    assert root.find(".//ATMs").get("enable") == "false"
    assert root.find(".//SelectedStrategies").text is None
    assert root.find("./Data/Setups/Setup") is not None
    assert root.find("./CustomData/Setups/Setup/MainTestValues").get("symbol") == "true"


def test_monkey_static_tabs_guard_rejects_portfolio_filters_and_customdata_drift():
    root = ET.fromstring(
        f"""
        <Settings>
          {_monkey_data_gate_fixture()}
          <CrossChecks use="true" evaluateAll="true">
            <MonteCarloRetest use="true">
              <Settings>
                <NumberOfSimulations>200</NumberOfSimulations>
                <MCUseFullSample>true</MCUseFullSample>
                <MCBacktestPrecision>-1</MCBacktestPrecision>
                <Methods><Method type="RealMonkeyTest" use="true"><Params><Param key="MaxChange" type="Integer">90</Param></Params></Method></Methods>
              </Settings>
            </MonteCarloRetest>
          </CrossChecks>
          <PartsToImprove improveATM="false">
            <EntryRules symmetry="false"><LongImprovement use="false" action="replace" /><ShortImprovement use="false" action="replace" /></EntryRules>
            <OrderTypes><LongImprovement use="false" /><ShortImprovement use="false" /></OrderTypes>
            <ExitRules symmetry="false"><LongImprovement use="false" action="replace" /><ShortImprovement use="false" action="replace" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Sequential" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>false</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>false</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>false</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="false" />
              <EvoRestartOnStagnation status="false" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple" version="142.2336">
            <BuildingBlocks><Block key="Indicators.ATR" category="indicators" use="true" probability="1" /></BuildingBlocks>
            <OrderTypes><Block key="EnterAtMarket" use="true" /><Block key="EnterReverseAtMarket" use="false" /><Block key="EnterAtStop" use="false" /><Block key="EnterAtLimit" use="false" /></OrderTypes>
            <ExitTypes><Block key="ExitAfterBars.ExitAfterBars" use="true" probability="100" /></ExitTypes>
            <CustomData showAll="false" />
          </Blocks>
          <Rankings type="always">
            <MaxStrategies>500</MaxStrategies>
            <ConditionsType>1</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Existing portfolio" />
            <CustomAnalysis filter="true" inputArgs="" method="none" />
            <Conditions><Condition use="true"><Left-Side><Column-Value column="NetProfit" format="Decimal2" sampleType="127" /></Left-Side><Comparator value="&gt;=" /><Right-Side><Numeric-Value value="1" /></Right-Side></Condition></Conditions>
          </Rankings>
          <RiskMoneyManagement><MoneyManagement><Method type="FixedSize" use="false" /><Method type="FixedAmount" use="true" /></MoneyManagement></RiskMoneyManagement>
          <ATMs enable="true" />
          <SelectedStrategies>legacy</SelectedStrategies>
        </Settings>
        """
    )
    apply_monkey_crosschecks_to_root(root)
    setup = root.find("./CustomData/Setups/Setup")
    setup.set("testPrecision", "1")
    setup.find("Chart").set("symbol", "USDJPY_darwinex")
    setup.find("MainTestValues").set("symbol", "false")

    issues = enforce_monkey_static_tabs_guard(root)

    assert any("Rankings type" in issue for issue in issues)
    assert any("FitPortfolio" in issue for issue in issues)
    assert any("extra conditions" in issue for issue in issues)
    assert any("RiskMoneyManagement FixedSize" in issue for issue in issues)
    assert any("ATMs enable" in issue for issue in issues)
    assert any("SelectedStrategies" in issue for issue in issues)
    assert any("CustomData testPrecision" in issue for issue in issues)
    assert any("CustomData MainTestValues" in issue for issue in issues)
    assert any("Forbidden donor token" in issue for issue in issues)


def test_sequential_data_databanks_resources_options_keeps_dual_carrier_synced():
    root = ET.fromstring(
        """
        <Settings>
          <Data>
            <Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old" slippage="5" minDist="3" engine="Legacy">
              <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
              <Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">9</Param></Params></Method></Commissions>
            </Setup></Setups>
            <OutOfSample><Range dateFrom="2023.01.01" dateTo="2025.01.01" /></OutOfSample>
          </Data>
          <CustomData>
            <Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old" slippage="5" minDist="3" engine="Legacy">
              <Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" />
              <Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">9</Param></Params></Method></Commissions>
              <MainTestValues engine="false" />
            </Setup></Setups>
          </CustomData>
          <Databanks><Databank name="Input" value="MC" /><Databank name="Output" value="MC2" /></Databanks>
          <Resources>
            <Symbols><Symbol name="USDJPY_darwinex" precision="M1" timezone="UTC" broker="4"><InstrumentInfo instrument="USDJPY_darwinex" broker="4" /></Symbol></Symbols>
            <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
            <Instruments />
            <Sessions><Session name="Old" /></Sessions>
            <CustomIndicators />
            <CustomBlocks />
          </Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">true</Param><Param key="RealisticGapsHandling">true</Param><Param key="StoreChartData">true</Param><Param key="Session">Old</Param><Param key="MarketOpenSession">Old</Param></Params></BuildTradingOptions></Options>
        </Settings>
        """
    )

    actions = apply_sequential_data_databanks_resources_options_to_root(root)

    assert any(item["field"] == "Data/Setup/Chart:attrs" and item["changed"] for item in actions)
    assert enforce_sequential_data_databanks_resources_options_guard(root) == []
    data_setup = root.find("./Data/Setups/Setup")
    custom_setup = root.find("./CustomData/Setups/Setup")
    assert data_setup.get("dateFrom") == custom_setup.get("dateFrom") == "2017.10.02"
    assert data_setup.find("Chart").get("spread") == custom_setup.find("Chart").get("spread") == "2.0"
    assert root.find("./Data/OutOfSample/Range") is None
    assert {
        databank.get("name"): databank.get("value")
        for databank in root.findall(".//Databanks/Databank")
    } == {"Input": "MC2", "Output": "Sequential"}
    assert root.find(".//BuildTradingOptions/Params/Param[@key='LimitTimeRange']").text == "false"
    assert root.find(".//Resources/Symbols/Symbol").get("precision") == "TICK"
    assert root.findall(".//Resources/Sessions/Session") == []


def test_sequential_data_databanks_resources_options_guard_rejects_divergent_carriers():
    root = ET.fromstring(
        """
        <Settings>
          <Data><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0"><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" /></Setup></Setups></Data>
          <CustomData><Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0"><Chart symbol="AUDCAD_darwinex" timeframe="H4" spread="2.0" /><MainTestValues engine="false" /></Setup></Setups></CustomData>
          <Databanks><Databank name="Input" value="MC" /><Databank name="Output" value="Sequential" /></Databanks>
          <Resources><Symbols /><Brokers /><Sessions /></Resources>
          <Options><BuildTradingOptions><Params><Param key="LimitTimeRange">true</Param></Params></BuildTradingOptions></Options>
        </Settings>
        """
    )

    issues = enforce_sequential_data_databanks_resources_options_guard(root)

    assert any("chart mismatch for timeframe" in issue for issue in issues)
    assert any("CustomData MainTestValues" in issue for issue in issues)
    assert any("Databank Input" in issue for issue in issues)
    assert any("Options param" in issue for issue in issues)


def _sequential_data_gate_fixture() -> str:
    return """
      <Data>
        <Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0" engine="MetaTrader5 (hedged)">
          <Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" />
          <Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">0.0</Param></Params></Method></Commissions>
        </Setup></Setups>
      </Data>
      <CustomData>
        <Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0" engine="MetaTrader4">
          <Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" />
          <Commissions><Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">0.0</Param></Params></Method></Commissions>
          <MainTestValues engine="true" symbol="true" timeframe="true" dates="true" subcharts="false" precision="true" distance="true" spread="true" slippage="true" commissions="true" />
        </Setup></Setups>
      </CustomData>
      <Databanks><Databank name="Input" value="MC2" /><Databank name="Output" value="Sequential" /></Databanks>
      <Resources>
        <Symbols><Symbol name="AUDCAD_darwinex" precision="TICK" timezone="EETUS" broker="4"><InstrumentInfo instrument="AUDCAD_darwinex" broker="4" /></Symbol></Symbols>
        <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
        <Instruments><InstrumentInfo instrument="AUDCAD_darwinex" broker="4" /></Instruments>
        <Sessions />
      </Resources>
      <Options><BuildTradingOptions><Params>
        <Param key="LimitTimeRange">false</Param>
        <Param key="RealisticGapsHandling">false</Param>
        <Param key="StoreChartData">false</Param>
        <Param key="Session">No Session</Param>
        <Param key="MarketOpenSession">No Session</Param>
      </Params></BuildTradingOptions></Options>
    """


def _sequential_crosschecks_gate_fixture() -> str:
    return """
      <CrossChecks use="true" evaluateAll="true">
        <SequentialOptimization use="true">
          <Settings>
            <ParameterSettings>
              <DistributionUp>130</DistributionUp>
              <DistributionDown>70</DistributionDown>
              <Steps>12</Steps>
              <ApplyToStrategy>false</ApplyToStrategy>
            </ParameterSettings>
            <WhatToParametrize type="1" symmetricVariables="false">
              <Recommended>false</Recommended>
              <Periods>true</Periods>
              <Shifts>false</Shifts>
              <Constants>true</Constants>
              <OtherParams>false</OtherParams>
              <EntryParams>false</EntryParams>
              <EntryLogic>false</EntryLogic>
              <ExitParamsUsed>true</ExitParamsUsed>
              <ExitParamsUnused>false</ExitParamsUnused>
              <BooleanParams>false</BooleanParams>
            </WhatToParametrize>
          </Settings>
          <AcceptanceSettings>
            <PctToPass>80</PctToPass>
            <ResultsCount>5</ResultsCount>
            <StabilityRange>25</StabilityRange>
            <Conditions />
          </AcceptanceSettings>
        </SequentialOptimization>
        <MonteCarloRetest use="false">
          <Settings>
            <Methods><Method type="RandomizeSpread" use="false" /></Methods>
            <Setups><Setup dateFrom="2017.10.02" dateTo="2023.12.31" testPrecision="2" session="No Session" slippage="0" minDist="0">
              <Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="2.0" />
            </Setup></Setups>
          </Settings>
        </MonteCarloRetest>
      </CrossChecks>
      <Rankings><ForceRunCrossChecks>false</ForceRunCrossChecks></Rankings>
    """


def _sequential_crosschecks_only_fixture() -> str:
    return _sequential_crosschecks_gate_fixture().replace(
        '      <Rankings><ForceRunCrossChecks>false</ForceRunCrossChecks></Rankings>',
        "",
    )


def test_sequential_crosschecks_enforces_stability_gate_without_rewriting_strategy():
    root = ET.fromstring(
        f"""
        <Settings>
          {_sequential_data_gate_fixture()}
          <CrossChecks use="false" evaluateAll="false">
            <MonteCarloRetest use="true">
              <Settings>
                <Methods><Method type="RandomizeSpread" use="true"><Params><Param key="Min">30</Param></Params></Method></Methods>
                <Setups><Setup dateFrom="2010.01.01" dateTo="2026.01.01" testPrecision="1" session="Old" slippage="4" minDist="2"><Chart symbol="USDJPY_darwinex" timeframe="H4" spread="1.4" /></Setup></Setups>
              </Settings>
            </MonteCarloRetest>
            <SequentialOptimization use="false">
              <Settings>
                <ParameterSettings><DistributionUp>180</DistributionUp><DistributionDown>30</DistributionDown><Steps>99</Steps><ApplyToStrategy>true</ApplyToStrategy></ParameterSettings>
                <WhatToParametrize type="2" symmetricVariables="true"><Recommended>true</Recommended><Periods>false</Periods><Constants>false</Constants><EntryLogic>true</EntryLogic><ExitParamsUsed>false</ExitParamsUsed></WhatToParametrize>
              </Settings>
              <AcceptanceSettings><PctToPass>10</PctToPass><ResultsCount>1</ResultsCount><StabilityRange>5</StabilityRange><Conditions><Condition use="true" /></Conditions></AcceptanceSettings>
            </SequentialOptimization>
          </CrossChecks>
          <Rankings><ForceRunCrossChecks>false</ForceRunCrossChecks></Rankings>
        </Settings>
        """
    )

    actions = apply_sequential_crosschecks_to_root(root)

    assert any(item["field"] == "CrossChecks:attrs" and item["changed"] for item in actions)
    assert enforce_sequential_crosschecks_guard(root) == []
    summary = sequential_crosschecks_summary(root)["crossChecks"]
    assert summary["active"] == ["SequentialOptimization"]
    assert summary["sequentialOptimization"]["parameterSettings"] == {
        "DistributionUp": "130",
        "DistributionDown": "70",
        "Steps": "12",
        "ApplyToStrategy": "false",
    }
    assert summary["sequentialOptimization"]["acceptanceSettings"]["values"] == {
        "PctToPass": "80",
        "ResultsCount": "5",
        "StabilityRange": "25",
    }
    assert summary["sequentialOptimization"]["acceptanceSettings"]["activeConditionCount"] == 0
    inactive_methods = [
        method
        for check in summary["checks"]
        if check["id"] != "SequentialOptimization"
        for method in check["methods"]
    ]
    assert all(method["use"] == "false" for method in inactive_methods)
    setup = root.find(".//CrossChecks/MonteCarloRetest/Settings/Setups/Setup")
    assert setup.get("dateFrom") == "2017.10.02"
    assert setup.get("dateTo") == "2023.12.31"
    assert setup.get("testPrecision") == "2"
    assert setup.find("Chart").attrib == {"symbol": "AUDCAD_darwinex", "timeframe": "H1", "spread": "2.0"}


def test_sequential_crosschecks_guard_rejects_optimizer_and_extra_conditions():
    root = ET.fromstring(
        f"""
        <Settings>
          {_sequential_data_gate_fixture()}
          <CrossChecks use="true" evaluateAll="true">
            <SequentialOptimization use="true">
              <Settings>
                <ParameterSettings><DistributionUp>130</DistributionUp><DistributionDown>70</DistributionDown><Steps>12</Steps><ApplyToStrategy>true</ApplyToStrategy></ParameterSettings>
                <WhatToParametrize type="1" symmetricVariables="false"><Recommended>false</Recommended><Periods>true</Periods><Shifts>false</Shifts><Constants>true</Constants><OtherParams>false</OtherParams><EntryParams>false</EntryParams><EntryLogic>false</EntryLogic><ExitParamsUsed>true</ExitParamsUsed><ExitParamsUnused>false</ExitParamsUnused><BooleanParams>false</BooleanParams></WhatToParametrize>
              </Settings>
              <AcceptanceSettings><PctToPass>80</PctToPass><ResultsCount>5</ResultsCount><StabilityRange>25</StabilityRange><Conditions><Condition use="true" /></Conditions></AcceptanceSettings>
            </SequentialOptimization>
            <MonteCarloRetest use="false"><Settings><Methods><Method type="RandomizeSpread" use="true" /></Methods></Settings></MonteCarloRetest>
          </CrossChecks>
          <Rankings><ForceRunCrossChecks>true</ForceRunCrossChecks></Rankings>
        </Settings>
        """
    )

    issues = enforce_sequential_crosschecks_guard(root)

    assert any("ParameterSettings" in issue for issue in issues)
    assert any("extra filter conditions" in issue for issue in issues)
    assert any("still has active methods" in issue for issue in issues)
    assert any("ForceRunCrossChecks" in issue for issue in issues)


def test_sequential_passive_generation_points_to_mc2_and_preserves_indicator_universe():
    root = ET.fromstring(
        f"""
        <Settings>
          {_sequential_data_gate_fixture()}
          {_sequential_crosschecks_only_fixture()}
          <PartsToImprove improveATM="true">
            <EntryRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></EntryRules>
            <OrderTypes><LongImprovement use="true" /><ShortImprovement use="true" /></OrderTypes>
            <ExitRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>true</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="true" />
              <EvoRestartOnStagnation status="true" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple">
            <BuildingBlocks>
              <Block key="Signals.ADX" category="signals" use="true" probability="1" />
              <Block key="Indicators.ATR" category="indicators" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="true" probability="1" />
            </BuildingBlocks>
            <OrderTypes><Block key="EnterAtMarket" use="false" /><Block key="EnterReverseAtMarket" use="true" /><Block key="EnterAtStop" use="true" /><Block key="EnterAtLimit" use="true" /></OrderTypes>
            <ExitTypes><Block key="ExitAfterBars.ExitAfterBars" use="false" probability="50" /><Block key="ExitAfterDays.ExitAfterDays" use="true" probability="50" /></ExitTypes>
            <CustomData showAll="true"><Item /></CustomData>
          </Blocks>
        </Settings>
        """
    )

    actions = apply_sequential_passive_generation_to_root(root, source_root=root)

    assert any(item["field"] == "WhatToBuild/StrategyType" and item["changed"] for item in actions)
    assert enforce_sequential_passive_generation_guard(root) == []
    assert root.find(".//WhatToBuild/StrategyType").get("improveDatabank") == "MC2"
    assert root.find(".//WhatToBuild/BuildMode/ShowLastGenerationDatabank").text == "false"
    assert root.find(".//WhatToBuild/BuildMode/EvoRestartOnFinish").get("status") == "false"
    assert root.find(".//BuildingBlocks/Block[@category='indicators']").get("use") == "true"
    assert root.find(".//BuildingBlocks/Block[@category='signals']").get("use") == "false"
    assert root.find(".//BuildingBlocks/Block[@category='stopLimitBlocks']").get("use") == "false"
    assert root.find(".//OrderTypes/Block[@key='EnterAtMarket']").get("use") == "true"
    assert root.find(".//ExitTypes/Block[@key='ExitAfterBars.ExitAfterBars']").get("probability") == "100"
    assert root.find(".//ExitTypes/Block[@key='ExitAfterDays.ExitAfterDays']") is None


def test_sequential_passive_generation_guard_rejects_placeholder_generation_and_day_exits():
    root = ET.fromstring(
        f"""
        <Settings>
          {_sequential_data_gate_fixture()}
          {_sequential_crosschecks_only_fixture()}
          <PartsToImprove improveATM="true">
            <EntryRules><LongImprovement use="true" /><ShortImprovement use="false" /></EntryRules>
            <OrderTypes><LongImprovement use="false" /><ShortImprovement use="false" /></OrderTypes>
            <ExitRules><LongImprovement use="false" /><ShortImprovement use="false" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>false</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>false</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="false" />
              <EvoRestartOnStagnation status="false" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple" version="142.2336">
            <BuildingBlocks>
              <Block key="Signals.ADX" category="signals" use="true" probability="1" />
              <Block key="Indicators.ATR" category="indicators" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="true" probability="1" />
            </BuildingBlocks>
            <OrderTypes><Block key="EnterAtMarket" use="false" /><Block key="EnterReverseAtMarket" use="true" /><Block key="EnterAtStop" use="true" /><Block key="EnterAtLimit" use="true" /></OrderTypes>
            <ExitTypes><Block key="ExitAfterBars.ExitAfterBars" use="false" probability="50" /><Block key="ExitAfterDays.ExitAfterDays" use="true" probability="50" /></ExitTypes>
            <CustomData showAll="true"><Item /></CustomData>
          </Blocks>
        </Settings>
        """
    )

    issues = enforce_sequential_passive_generation_guard(root)

    assert any("EntryRules/LongImprovement" in issue for issue in issues)
    assert any("StrategyType" in issue for issue in issues)
    assert any("BuildMode ShowLastGenerationDatabank" in issue for issue in issues)
    assert any("order types" in issue for issue in issues)
    assert any("ExitAfterBars probability" in issue for issue in issues)
    assert any("day-based" in issue for issue in issues)
    assert any("signals" in issue for issue in issues)
    assert any("stop/limit" in issue for issue in issues)
    assert any("CustomData" in issue for issue in issues)
    assert any("Strategies to improve" in issue for issue in issues)


def test_sequential_static_tabs_closes_rankings_risk_and_customdata_without_turning_off_sequential_optimization():
    root = ET.fromstring(
        f"""
        <Settings>
          {_sequential_data_gate_fixture()}
          {_sequential_crosschecks_only_fixture()}
          <PartsToImprove improveATM="true">
            <EntryRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></EntryRules>
            <OrderTypes><LongImprovement use="true" /><ShortImprovement use="true" /></OrderTypes>
            <ExitRules symmetry="true"><LongImprovement use="true" action="add-or-replace" /><ShortImprovement use="true" action="add-or-replace" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="Strategies to improve" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>true</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>true</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>false</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="true" />
              <EvoRestartOnStagnation status="true" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple">
            <BuildingBlocks>
              <Block key="Signals.ADX" category="signals" use="true" probability="1" />
              <Block key="Indicators.ATR" category="indicators" use="true" probability="1" />
              <Block key="StopLimitBlocks.ATRStop" category="stopLimitBlocks" use="true" probability="1" />
            </BuildingBlocks>
            <OrderTypes><Block key="EnterAtMarket" use="false" /><Block key="EnterReverseAtMarket" use="true" /><Block key="EnterAtStop" use="true" /><Block key="EnterAtLimit" use="true" /></OrderTypes>
            <ExitTypes><Block key="ExitAfterBars.ExitAfterBars" use="false" probability="50" /></ExitTypes>
            <CustomData showAll="true"><Item /></CustomData>
          </Blocks>
          <Rankings type="always">
            <MaxStrategies>500</MaxStrategies>
            <ConditionsType>1</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Existing portfolio" />
            <CustomAnalysis filter="true" inputArgs="" method="none" />
            <Conditions><Condition use="true"><Left-Side><Column-Value column="NetProfit" /></Left-Side><Comparator value="&gt;=" /><Right-Side><Numeric-Value value="1" /></Right-Side></Condition></Conditions>
          </Rankings>
          <RiskMoneyManagement><MoneyManagement><Method type="FixedSize" use="false" /><Method type="FixedAmount" use="true" /></MoneyManagement></RiskMoneyManagement>
          <ATMs enable="true" />
          <Notes>ok</Notes>
          <SelectedStrategies><Strategy id="legacy" /></SelectedStrategies>
        </Settings>
        """
    )

    apply_sequential_passive_generation_to_root(root, source_root=root)
    actions = apply_sequential_static_tabs_to_root(root)

    assert any(item["field"] == "Rankings/FitPortfolio" and item["changed"] for item in actions)
    assert enforce_sequential_static_tabs_guard(root) == []
    assert root.find(".//CrossChecks/SequentialOptimization").get("use") == "true"
    assert root.find(".//Rankings").get("type") == "never"
    assert root.find(".//Rankings/DeleteFailedStrategies").text == "false"
    assert root.find(".//Rankings/ForceRunCrossChecks").text == "false"
    assert root.find(".//RiskMoneyManagement//Method[@type='FixedSize']").get("use") == "true"
    assert root.find(".//ATMs").get("enable") == "false"
    assert root.find(".//SelectedStrategies").text is None
    assert root.find("./Data/Setups/Setup") is not None
    assert root.find("./CustomData/Setups/Setup/MainTestValues").get("subcharts") == "false"


def test_sequential_static_tabs_guard_rejects_portfolio_filters_and_customdata_drift():
    root = ET.fromstring(
        f"""
        <Settings>
          {_sequential_data_gate_fixture()}
          {_sequential_crosschecks_only_fixture()}
          <PartsToImprove improveATM="false">
            <EntryRules symmetry="false"><LongImprovement use="false" action="replace" /><ShortImprovement use="false" action="replace" /></EntryRules>
            <OrderTypes><LongImprovement use="false" /><ShortImprovement use="false" /></OrderTypes>
            <ExitRules symmetry="false"><LongImprovement use="false" action="replace" /><ShortImprovement use="false" action="replace" /></ExitRules>
          </PartsToImprove>
          <WhatToBuild>
            <StrategyType type="simple" additionalCharts="2" templateFile="" improveType="strategy" strategyFile="" architecture="sq4" improveDatabank="MC2" />
            <BuildMode generationType="random-generation">
              <ShowLastGenerationDatabank>false</ShowLastGenerationDatabank>
              <FreshBloodReplaceSimilar>false</FreshBloodReplaceSimilar>
              <FreshBloodReplaceWeakest>false</FreshBloodReplaceWeakest>
              <EvoRestartOnFinish status="false" />
              <EvoRestartOnStagnation status="false" fitnessType="10" generations="30" />
            </BuildMode>
          </WhatToBuild>
          <Blocks type="simple" version="142.2336">
            <BuildingBlocks><Block key="Indicators.ATR" category="indicators" use="true" probability="1" /></BuildingBlocks>
            <OrderTypes><Block key="EnterAtMarket" use="true" /><Block key="EnterReverseAtMarket" use="false" /><Block key="EnterAtStop" use="false" /><Block key="EnterAtLimit" use="false" /></OrderTypes>
            <ExitTypes><Block key="ExitAfterBars.ExitAfterBars" use="true" probability="100" /></ExitTypes>
            <CustomData showAll="false" />
          </Blocks>
          <Rankings type="always">
            <MaxStrategies>500</MaxStrategies>
            <ConditionsType>1</ConditionsType>
            <DeleteFailedStrategies>true</DeleteFailedStrategies>
            <ForceRunCrossChecks>true</ForceRunCrossChecks>
            <FitPortfolio active="true" databank="Existing portfolio" />
            <CustomAnalysis filter="true" inputArgs="" method="none" />
            <Conditions><Condition use="true"><Left-Side><Column-Value column="NetProfit" format="Decimal2" sampleType="127" /></Left-Side><Comparator value="&gt;=" /><Right-Side><Numeric-Value value="1" /></Right-Side></Condition></Conditions>
          </Rankings>
          <RiskMoneyManagement><MoneyManagement><Method type="FixedSize" use="false" /><Method type="FixedAmount" use="true" /></MoneyManagement></RiskMoneyManagement>
          <ATMs enable="true" />
          <SelectedStrategies>legacy</SelectedStrategies>
        </Settings>
        """
    )
    setup = root.find("./CustomData/Setups/Setup")
    setup.set("testPrecision", "1")
    setup.find("Chart").set("symbol", "USDJPY_darwinex")
    setup.find("MainTestValues").set("symbol", "false")

    issues = enforce_sequential_static_tabs_guard(root)

    assert any("Rankings type" in issue for issue in issues)
    assert any("FitPortfolio" in issue for issue in issues)
    assert any("extra conditions" in issue for issue in issues)
    assert any("RiskMoneyManagement FixedSize" in issue for issue in issues)
    assert any("ATMs enable" in issue for issue in issues)
    assert any("SelectedStrategies" in issue for issue in issues)
    assert any("CustomData testPrecision" in issue for issue in issues)
    assert any("CustomData MainTestValues" in issue for issue in issues)
    assert any("Forbidden donor token" in issue for issue in issues)
