import json
import xml.etree.ElementTree as ET

from tools.sqx142_task_config_gate import (
    apply_retest1_passive_generation_to_root,
    apply_retest1_data_resources_to_root,
    apply_retest1_options_databanks_rankings_to_root,
    apply_retest1_static_crosschecks_to_root,
    apply_tick_real_data_databanks_resources_to_root,
    enforce_retest1_data_resources_guard,
    enforce_retest1_options_databanks_rankings_guard,
    enforce_retest1_passive_generation_guard,
    enforce_retest1_static_crosschecks_guard,
    enforce_tick_real_data_databanks_resources_guard,
    fallback_retest1_oos2_resource,
    question_id,
    record_tab_answer,
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
              <Block key="Indicators.ATR" category="indicators" use="false" probability="1" />
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
