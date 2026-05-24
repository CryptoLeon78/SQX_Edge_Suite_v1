from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_SQX_ROOT = Path(r"C:\BOTS\Versiones\SQX_142_Crack")
DEFAULT_DONOR_PROJECT = "Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1"
DEFAULT_BASE_PROJECT = "Capa1_Long_SQX142_Base"
DEFAULT_TEMPLATE = TOOL_ROOT / "templates" / "Capa1_Long.cfx"
BLOCKSETTINGS_MANIFEST_PATH = TOOL_ROOT / "config" / "blocksettings_manifest.json"
BLOCKSETTINGS_RESOURCE_DIR = TOOL_ROOT / "resources" / "blocksettings"
GENERATOR_PROFILES_PATH = TOOL_ROOT / "config" / "generator_profiles.json"
LEDGER_DIRNAME = ".local/sqx142_task_config"
VERSION = "sqx142-task-config-gate-v1"

PHASES = [
    {"id": "phase0", "label": "preflight, snapshots and semantic diff"},
    {"id": "phase1", "label": "selective donor-to-base promotion plan"},
    {"id": "phase2", "label": "Build Capa1 questionnaire"},
    {"id": "phase3", "label": "RETEST 0 questionnaire"},
    {"id": "phase4", "label": "RETEST 1 questionnaire"},
    {"id": "phase5", "label": "TICK REAL questionnaire"},
    {"id": "phase6", "label": "MC questionnaire"},
    {"id": "phase7", "label": "MC 2 questionnaire"},
    {"id": "phase8", "label": "Sequential questionnaire"},
    {"id": "phase9", "label": "Monkey Test questionnaire"},
    {"id": "phase10", "label": "Synthetic questionnaire"},
    {"id": "phase11", "label": "SPP configuration review"},
    {"id": "phase12", "label": "WFM configuration review"},
    {"id": "phase13", "label": "FOWARD configuration review"},
    {"id": "phase14", "label": "Capa1 closeout and methodology sync"},
]

SECTION_ALIASES = {
    "automatic retest": "Options",
    "automatic_retest": "Options",
    "atm": "ATMs",
    "atms": "ATMs",
    "blocks": "Blocks",
    "cross checks": "CrossChecks",
    "cross_checks": "CrossChecks",
    "crosschecks": "CrossChecks",
    "custom data": "CustomData",
    "custom_data": "CustomData",
    "customdata": "CustomData",
    "data": "Data",
    "databanks": "Databanks",
    "money management": "RiskMoneyManagement",
    "money_management": "RiskMoneyManagement",
    "notes": "Notes",
    "optimization": "Optimization",
    "options": "Options",
    "parts to improve": "PartsToImprove",
    "parts_to_improve": "PartsToImprove",
    "rankings": "Rankings",
    "resources": "Resources",
    "risk money management": "RiskMoneyManagement",
    "risk_money_management": "RiskMoneyManagement",
    "trading options": "Options",
    "trading_options": "Options",
    "what to build": "WhatToBuild",
    "what_to_build": "WhatToBuild",
    "whattobuild": "WhatToBuild",
}

SKIP_SUBTREES = {
    "BackupStrategyTemplate",
    "FullStrategyXml",
    "Strategy",
    "StrategyXml",
    "XmlStrategy",
}

VIEW_PROMOTION_TARGETS = {
    "Results": "MINING FAST REVIEW",
    "Initial population": "MINING FAST REVIEW",
    "Last generation": "MINING FAST REVIEW",
    "Strategies to improve": "MINING FAST REVIEW",
    "Strategies to optimize": "MINING FAST REVIEW",
    "RETEST 0": "RETEST QUICK REVIEW",
    "retest 1": "RETEST QUICK REVIEW",
    "TICK": "RETEST ROBUST REVIEW",
    "MC": "RETEST ROBUST REVIEW",
    "MC2": "RETEST ROBUST REVIEW",
    "Sequential": "RETEST ROBUST REVIEW",
    "Monkey Test": "MC MONKEY RETEST",
    "Syntetic": "MC SYNTHETIC RETEST",
    "SPP": "RETEST ROBUST REVIEW",
    "WFM": "RETEST ROBUST REVIEW",
    "Foward": "RETEST QUICK REVIEW",
}

DO_NOT_PROMOTE_FIELDS = {
    "project_name",
    "active_flags",
    "symbol",
    "timeframe",
    "asset_specific_spread",
    "session_results",
}

BUILD_GENETIC_TARGET = {
    "PopulationSize": "20",
    "MaxGenerations": "30",
    "CrossoverProbability": "35",
    "MutationProbability": "35",
    "Islands": "7",
    "MigrationModulo": "5",
    "MigrationRate": "5",
    "ShowLastGenerationDatabank": "false",
    "InitGenerationType": "1",
    "DecimationCoef": "1",
    "FreshBloodReplaceSimilar": "true",
    "FreshBloodReplaceWeakest": "false",
    "FreshBloodWeakestPct": "10",
    "FreshBloodWeakestGenerations": "5",
}

BUILD_GENETIC_ATTR_TARGET = {
    "EvoRestartOnFinish": {"status": "true"},
    "EvoRestartOnStagnation": {"status": "true", "fitnessType": "10", "generations": "10"},
    "EvoInSamplePeriod": {"ratio": "50"},
}

BUILD_INITIAL_CONDITIONS_TARGET = [
    {"column": "ProfitFactor", "comparator": ">=", "value": "1", "format": "Decimal2"},
    {"column": "NumberOfTrades", "comparator": ">=", "value": "100", "format": "Decimal2"},
]

BUILD_MODE_LEGACY_NODES = [
    "FilterInitialPopulation",
    "EvoFitnessRestartType",
    "EvoStagnationRestartGenerations",
]

BUILD_RANKING_TARGET = {
    "MaxStrategies": "2000",
    "StopCondition": {"passedStrategies": "500"},
}

BUILD_ORDER_TYPE_TARGET = {
    "EnterAtMarket": "true",
    "EnterReverseAtMarket": "false",
    "EnterAtStop": "false",
    "EnterAtLimit": "false",
}

BUILD_EXIT_TYPE_ACTIVE_KEY = "ExitAfterBars.ExitAfterBars"
BUILD_EXIT_TYPE_BANNED_TOKENS = ("ExitAfterDays", "ExitAfterTradingDays")
BUILD_EXTERNAL_CUSTOM_DATA_TARGET = {"showAll": "false"}
BUILD_BLOCK_CATEGORY_DISABLE_TARGET = ("signals", "stopLimitBlocks")
BUILD_BLOCK_CATEGORY_PRESERVE_TARGET = ("indicators",)
BUILD_INDICATORS_DEFAULT_BLOCKSETTING = "BS_Volatilidad"
BUILD_INDICATORS_DEFAULT_TIMEFRAME = "H4"
BUILD_DATA_PERIOD_KEY = "BUILD_C1"
BUILD_DATA_TEST_PRECISION = "2"
BUILD_DATA_SESSION = "No Session"
BUILD_RESOURCES_PRECISION = "TICK"
BUILD_RESOURCES_BASE_DATA_TYPE = "3"
BUILD_RESOURCES_BANNED_DONOR_TOKENS = ("USDJPY", "USDJPY_darwinex", "USDJPY_dukascopy")
BUILD_ACTIVE_CROSSCHECK = "SequentialOptimization"
BUILD_CROSSCHECK_PARENT_TARGET = {"use": "true", "evaluateAll": "true"}
BUILD_CROSSCHECK_BANNED_DONOR_TOKENS = ("USDJPY", "USDJPY_darwinex", "USDJPY_dukascopy")
BUILD_STATIC_TABS = (
    "Options",
    "ATMs",
    "PartsToImprove",
    "RiskMoneyManagement",
    "Databanks",
    "Notes",
    "Optimization",
)
BUILD_STATIC_TAB_HASHES = {
    "Options": "BF732DD7B130086DC0EA2E16669A270AC42A5910763B72B9DA001BCE4F22038C",
    "ATMs": "5B18484BDCBB462F169B894A8861C05F7DA323B05EE808FA49BB300442E56C40",
    "PartsToImprove": "14258C2F5FBFB077CE7FC4009F1D89FB32BD7FD2EBD66EAFF5F1ECB33411AC87",
    "RiskMoneyManagement": "CFBC9E6C4D1C30782BAC103AED72CFAF66AAA71BF4B892A4CEDDBA1E6317B76F",
    "Databanks": "31F633435ACD49E3837422C376421A28723FBE7017B4EEBD9EA2F20C29B7BB98",
    "Notes": "7E0C7BB76E5A63E6CD5B9B97F2571F549C95DF5F79CD0C315895ADAF2742E880",
    "Optimization": "63655CE465154201278796A666D9FC0A21B36EAF825B356797927DBC8402E3A8",
}

RETEST1_TASK_TITLE = "RETEST 1"
RETEST1_PERIOD_KEY = "RETEST_1_C1"
RETEST1_PLACEHOLDER_ASSET = "AUDCAD"
RETEST1_PLACEHOLDER_TIMEFRAME = "H1"
RETEST1_BROKER_PROFILE_ID = "dukascopy_oos2"
RETEST1_DATA_TEST_PRECISION = "2"
RETEST1_DATA_SESSION = "No Session"
RETEST1_EXPECTED_SOURCE_ID = "2"
RETEST1_EXPECTED_BROKER_ID = "3"
RETEST1_BANNED_RESOURCE_TOKENS = (
    "USDJPY",
    "USDJPY_darwinex",
    "USDJPY_dukascopy",
    "_darwinex",
    "Darwinex",
)
RETEST1_OPTIONS_PARAMS_TARGET = {
    "Session": "No Session",
    "MarketOpenSession": "No Session",
    "LimitTimeRange": "true",
    "SignalTimeRangeFrom": "7200",
    "SignalTimeRangeTo": "79200",
    "RealisticGapsHandling": "true",
    "StoreChartData": "false",
}
RETEST1_DATABANKS_TARGET = {
    "Input": "RETEST 0",
    "Output": "retest 1",
}
RETEST1_RANKING_TARGET = {
    "MaxStrategies": "10000",
    "ConditionsType": "1",
    "DeleteFailedStrategies": "false",
    "ForceRunCrossChecks": "false",
    "FitPortfolio": {"active": "false", "databank": "Existing portfolio"},
    "CustomAnalysis": {"filter": "false", "inputArgs": "", "method": "none"},
    "AutomaticDismissal": {"warnings": "false"},
    "StopCondition": {
        "type": "databank-full",
        "passedStrategies": "1000",
        "restartCount": "5",
        "days": "0",
        "hours": "0",
        "minutes": "0",
    },
}
RETEST1_RANKING_CONDITIONS_TARGET = [
    {"column": "NumberOfTrades", "comparator": ">=", "value": "100", "format": "Decimal2"},
    {"column": "RExpectancy", "comparator": ">", "value": "0.05", "format": "Decimal2"},
    {"column": "NetProfit", "comparator": ">=", "value": "0", "format": "Decimal2"},
]
RETEST1_PASSIVE_SOURCE_TASK_TITLE = "RETEST 0"
RETEST1_STRATEGY_TYPE_TARGET = {
    "type": "simple",
    "additionalCharts": "2",
    "templateFile": "",
    "improveType": "strategy",
    "strategyFile": "",
    "architecture": "sq4",
    "improveDatabank": "RETEST 0",
}
RETEST1_PASSIVE_BUILDMODE_TEXT_TARGET = {
    "ShowLastGenerationDatabank": "false",
    "FreshBloodReplaceSimilar": "false",
    "FreshBloodReplaceWeakest": "false",
}
RETEST1_PASSIVE_BUILDMODE_ATTR_TARGET = {
    "EvoRestartOnFinish": {"status": "false"},
    "EvoRestartOnStagnation": {"status": "false", "fitnessType": "10", "generations": "30"},
}
RETEST1_STATIC_TABS = ("ATMs", "RiskMoneyManagement", "Notes", "SelectedStrategies")
RETEST1_RISK_MONEY_MANAGEMENT_METHOD_TARGET = {
    "FixedSize": "true",
    "RiskFixedBalancePct": "false",
    "RiskFixedPctOfAccount": "false",
    "FixedAmount": "false",
    "StocksSizeByPrice": "false",
}
RETEST1_ATMS_TARGET = {"enable": "false"}
RETEST1_CROSSCHECKS_TARGET = {"use": "false", "evaluateAll": "false"}

TICK_REAL_TASK_TITLE = "TICK REAL"
TICK_REAL_PERIOD_KEY = "ROBUSTNESS_C1"
TICK_REAL_DATA_TEST_PRECISION = "2"
TICK_REAL_DATA_SESSION = "No Session"
TICK_REAL_DATABANKS_TARGET = {
    "Input": "retest 1",
    "Output": "TICK",
}
TICK_REAL_RESOURCE_PRECISION = "TICK"
TICK_REAL_RESOURCE_TIMEZONE = "EETUS"
TICK_REAL_DEFAULT_SOURCE_ID = "4"
TICK_REAL_DEFAULT_BROKER_ID = "4"
TICK_REAL_BANNED_DONOR_TOKENS = ("USDJPY", "USDJPY_darwinex", "USDJPY_dukascopy")
TICK_REAL_OPTIONS_PARAMS_TARGET = {
    "Session": "No Session",
    "MarketOpenSession": "No Session",
    "LimitTimeRange": "true",
    "SignalTimeRangeFrom": "7200",
    "SignalTimeRangeTo": "79200",
    "RealisticGapsHandling": "true",
    "StoreChartData": "false",
}
TICK_REAL_RANKING_TARGET = {
    "MaxStrategies": "10000",
    "ConditionsType": "1",
    "DeleteFailedStrategies": "false",
    "ForceRunCrossChecks": "false",
    "FitPortfolio": {"active": "false", "databank": "Existing portfolio"},
    "CustomAnalysis": {"filter": "false", "inputArgs": "", "method": "none"},
    "AutomaticDismissal": {"warnings": "false"},
    "StopCondition": {
        "type": "databank-full",
        "passedStrategies": "1000",
        "restartCount": "5",
        "days": "0",
        "hours": "0",
        "minutes": "0",
    },
}
TICK_REAL_RANKING_CONDITIONS_TARGET = [
    {"column": "NumberOfTrades", "comparator": ">=", "value": "200", "format": "Integer", "sampleType": "127"},
    {"column": "ProfitFactor", "comparator": ">=", "value": "1.3", "format": "Decimal2", "sampleType": "127"},
    {"column": "WinningPct", "comparator": ">=", "value": "50", "format": "Decimal2Pct", "sampleType": "127"},
    {"column": "ReturnDDRatio", "comparator": ">=", "value": "4", "format": "Decimal2", "sampleType": "127"},
]
TICK_REAL_PASSIVE_SOURCE_TASK_TITLE = "RETEST 1"
TICK_REAL_STRATEGY_TYPE_TARGET = {
    "type": "simple",
    "additionalCharts": "2",
    "templateFile": "",
    "improveType": "strategy",
    "strategyFile": "",
    "architecture": "sq4",
    "improveDatabank": "retest 1",
}
TICK_REAL_PASSIVE_BUILDMODE_TEXT_TARGET = RETEST1_PASSIVE_BUILDMODE_TEXT_TARGET
TICK_REAL_PASSIVE_BUILDMODE_ATTR_TARGET = RETEST1_PASSIVE_BUILDMODE_ATTR_TARGET
TICK_REAL_STATIC_TABS = ("ATMs", "RiskMoneyManagement", "Notes", "CustomData")

MC_TASK_TITLE = "MC"
MC_PERIOD_KEY = "ROBUSTNESS_C1"
MC_DATA_TEST_PRECISION = "2"
MC_DATA_SESSION = "No Session"
MC_DATABANKS_TARGET = {
    "Input": "TICK",
    "Output": "MC",
}
MC_RESOURCE_PRECISION = "TICK"
MC_RESOURCE_TIMEZONE = "EETUS"
MC_DEFAULT_SOURCE_ID = TICK_REAL_DEFAULT_SOURCE_ID
MC_DEFAULT_BROKER_ID = TICK_REAL_DEFAULT_BROKER_ID
MC_BANNED_DONOR_TOKENS = TICK_REAL_BANNED_DONOR_TOKENS
MC_OPTIONS_PARAMS_TARGET = {
    "Session": "No Session",
    "MarketOpenSession": "No Session",
    "LimitTimeRange": "false",
    "RealisticGapsHandling": "false",
    "StoreChartData": "false",
}
MC_CROSSCHECK_PARENT_TARGET = {"use": "true", "evaluateAll": "true"}
MC_ACTIVE_CROSSCHECK = "MonteCarloManipulation"
MC_INACTIVE_CROSSCHECKS = (
    "RetestOnAdditionalMarkets",
    "WalkForwardOptimization",
    "RetestWithHigherPrecision",
    "MonteCarloRetest",
    "WalkForwardMatrix",
    "OptProfileSysParamPermutation",
    "WhatIf",
    "SequentialOptimization",
)
MC_MANIPULATION_SETTINGS_TARGET = {
    "NumberOfSimulations": "200",
    "MCUseFullSample": "true",
}
MC_MANIPULATION_METHOD_TARGET = {
    "RandomizeTradesOrder": {
        "use": "true",
        "params": {"Method": {"text": "resampling", "type": "String"}},
    },
    "RandomlySkipTrades": {
        "use": "false",
        "params": {"Probability": {"text": "10", "type": "Integer"}},
    },
}
MC_MANIPULATION_CONDITIONS_TARGET = [
    {
        "left": {
            "column": "NetProfit",
            "columnType": "0",
            "name": "Net profit",
            "format": "Decimal2PL",
            "resultType": "MonteCarloManipulation",
            "direction": "0",
            "sampleType": "10",
            "plType": "10",
            "confidenceLevel": "80",
            "market": "1",
            "subresult": "30",
            "pctRatio": "0",
            "class": "NetProfit",
        },
        "comparator": ">=",
        "right": {
            "column": "NetProfit",
            "columnType": "0",
            "format": "Decimal2PL",
            "resultType": "main",
            "direction": "0",
            "sampleType": "127",
            "plType": "10",
            "confidenceLevel": "50",
            "market": "1",
            "subresult": "30",
            "pctRatio": "40",
            "class": "NetProfit",
        },
    },
    {
        "left": {
            "column": "DrawdownPct",
            "columnType": "0",
            "name": "Max DD %",
            "format": "Decimal2Pct",
            "resultType": "MonteCarloManipulation",
            "direction": "0",
            "sampleType": "10",
            "plType": "10",
            "confidenceLevel": "80",
            "market": "1",
            "subresult": "30",
            "pctRatio": "0",
            "class": "DrawdownPct",
        },
        "comparator": "<=",
        "right": {
            "column": "DrawdownPct",
            "columnType": "0",
            "format": "Decimal2Pct",
            "resultType": "main",
            "direction": "0",
            "sampleType": "127",
            "plType": "10",
            "confidenceLevel": "50",
            "market": "1",
            "subresult": "30",
            "pctRatio": "200",
            "class": "DrawdownPct",
        },
    },
]
MC_PASSIVE_SOURCE_TASK_TITLE = "TICK REAL"
MC_STRATEGY_TYPE_TARGET = {
    "type": "simple",
    "additionalCharts": "2",
    "templateFile": "",
    "improveType": "strategy",
    "strategyFile": "",
    "architecture": "sq4",
    "improveDatabank": "TICK",
}
MC_PASSIVE_BUILDMODE_TEXT_TARGET = RETEST1_PASSIVE_BUILDMODE_TEXT_TARGET
MC_PASSIVE_BUILDMODE_ATTR_TARGET = RETEST1_PASSIVE_BUILDMODE_ATTR_TARGET
MC_STATIC_TABS = ("Rankings", "ATMs", "RiskMoneyManagement", "Notes", "SelectedStrategies", "CustomData")
MC_RANKING_TARGET = {
    "MaxStrategies": "10000",
    "ConditionsType": "1",
    "DeleteFailedStrategies": "false",
    "ForceRunCrossChecks": "false",
    "FitPortfolio": {"active": "false", "databank": "Existing portfolio"},
    "CustomAnalysis": {"filter": "false", "inputArgs": "", "method": "none"},
    "AutomaticDismissal": {"warnings": "false"},
    "StopCondition": {
        "type": "databank-full",
        "passedStrategies": "1000",
        "restartCount": "5",
        "days": "0",
        "hours": "0",
        "minutes": "0",
    },
}
MC_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET = {
    "commissions": "true",
    "dates": "false",
    "distance": "true",
    "engine": "true",
    "precision": "false",
    "slippage": "true",
    "spread": "true",
    "subcharts": "false",
    "symbol": "false",
    "timeframe": "true",
}
MC_CUSTOM_DATA_COMMISSION_TARGET = "0.0"
MC2_TASK_TITLE = "MC 2"
MC2_SPREAD_MIN_MULTIPLIER = 2.0
MC2_SPREAD_MAX_MULTIPLIER = 5.0
MC2_ACTIVE_CHECK = "MonteCarloRetest"
MC2_ACTIVE_METHODS = {"RandomizeHistoryData", "RandomizeSpread"}
MC2_NUMBER_OF_SIMULATIONS = "100"
MC2_USE_FULL_SAMPLE = "true"
MC2_PERIOD_KEY = MC_PERIOD_KEY
MC2_DATA_TEST_PRECISION = MC_DATA_TEST_PRECISION
MC2_DATA_SESSION = MC_DATA_SESSION
MC2_DATABANKS_TARGET = {
    "Input": "MC",
    "Output": "MC2",
}
MC2_DEFAULT_CHART_TARGET = {
    "symbol": "AUDCAD_darwinex",
    "timeframe": "H1",
    "spread": "2.0",
}
MC2_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET = {
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
MC2_OPTIONS_PARAMS_TARGET = MC_OPTIONS_PARAMS_TARGET
MC2_PASSIVE_SOURCE_TASK_TITLE = MC_TASK_TITLE
MC2_STRATEGY_TYPE_TARGET = {
    "type": "simple",
    "additionalCharts": "2",
    "templateFile": "",
    "improveType": "strategy",
    "strategyFile": "",
    "architecture": "sq4",
    "improveDatabank": "MC",
}
MC2_PASSIVE_BUILDMODE_TEXT_TARGET = MC_PASSIVE_BUILDMODE_TEXT_TARGET
MC2_PASSIVE_BUILDMODE_ATTR_TARGET = MC_PASSIVE_BUILDMODE_ATTR_TARGET
MC2_STATIC_TABS = MC_STATIC_TABS
MC2_RANKING_TARGET = MC_RANKING_TARGET
SEQUENTIAL_TASK_TITLE = "Sequential"
SEQUENTIAL_TASK_XML = "AutomaticRetest-Task3.xml"
SEQUENTIAL_PERIOD_KEY = MC_PERIOD_KEY
SEQUENTIAL_DATA_TEST_PRECISION = MC_DATA_TEST_PRECISION
SEQUENTIAL_DATA_SESSION = MC_DATA_SESSION
SEQUENTIAL_EXPECTED_DATABANKS = {
    "Input": "MC2",
    "Output": "Sequential",
}
SEQUENTIAL_DEFAULT_CHART_TARGET = MC2_DEFAULT_CHART_TARGET
SEQUENTIAL_DATA_ENGINE = "MetaTrader5 (hedged)"
SEQUENTIAL_CUSTOM_DATA_ENGINE = "MetaTrader4"
SEQUENTIAL_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET = {
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
SEQUENTIAL_OPTIONS_PARAMS_TARGET = MC_OPTIONS_PARAMS_TARGET
SEQUENTIAL_ACTIVE_CROSSCHECK = "SequentialOptimization"
SEQUENTIAL_NEXT_PHASE = "phase8_sequential_data_databanks_resources_options"
SEQUENTIAL_DATA_DATABANKS_RESOURCES_OPTIONS_NEXT = "phase8_sequential_crosschecks"
SEQUENTIAL_CROSSCHECKS_NEXT = "phase8_sequential_passive_generation"
SEQUENTIAL_PASSIVE_GENERATION_NEXT = "phase8_sequential_static_tabs"
SEQUENTIAL_STATIC_TABS_NEXT = "phase8_sequential_closeout"
SEQUENTIAL_CLOSEOUT_NEXT = "phase9_monkey_test_open"
MONKEY_TASK_TITLE = "Monkey Test"
MONKEY_TASK_XML = "AutomaticRetest-Task6.xml"
MONKEY_EXPECTED_DATABANKS = {
    "Input": "Sequential",
    "Output": "Monkey Test",
}
MONKEY_ACTIVE_CROSSCHECK = "MonteCarloRetest"
MONKEY_ACTIVE_METHOD = "RealMonkeyTest"
MONKEY_NUMBER_OF_SIMULATIONS = "200"
MONKEY_USE_FULL_SAMPLE = "true"
MONKEY_METHOD_MAX_CHANGE = "90"
MONKEY_NEXT_PHASE = "phase9_monkey_test_data_databanks_resources_options"
MONKEY_PERIOD_KEY = MC_PERIOD_KEY
MONKEY_DATA_TEST_PRECISION = MC_DATA_TEST_PRECISION
MONKEY_DATA_SESSION = MC_DATA_SESSION
MONKEY_DEFAULT_CHART_TARGET = MC2_DEFAULT_CHART_TARGET
MONKEY_DATA_ENGINE = SEQUENTIAL_DATA_ENGINE
MONKEY_CUSTOM_DATA_ENGINE = SEQUENTIAL_CUSTOM_DATA_ENGINE
MONKEY_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET = SEQUENTIAL_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET
MONKEY_OPTIONS_PARAMS_TARGET = MC_OPTIONS_PARAMS_TARGET
MONKEY_DATA_DATABANKS_RESOURCES_OPTIONS_NEXT = "phase9_monkey_test_crosschecks"
MONKEY_CROSSCHECK_PARENT_TARGET = {"use": "true", "evaluateAll": "true"}
MONKEY_CROSSCHECKS_NEXT = "phase9_monkey_test_passive_generation"
MONKEY_PASSIVE_SOURCE_TASK_TITLE = SEQUENTIAL_TASK_TITLE
MONKEY_STRATEGY_TYPE_TARGET = {
    "type": "simple",
    "additionalCharts": "2",
    "templateFile": "",
    "improveType": "strategy",
    "strategyFile": "",
    "architecture": "sq4",
    "improveDatabank": "Sequential",
}
MONKEY_PASSIVE_BUILDMODE_TEXT_TARGET = MC2_PASSIVE_BUILDMODE_TEXT_TARGET
MONKEY_PASSIVE_BUILDMODE_ATTR_TARGET = MC2_PASSIVE_BUILDMODE_ATTR_TARGET
MONKEY_PASSIVE_GENERATION_NEXT = "phase9_monkey_test_static_tabs"
MONKEY_STATIC_TABS = MC_STATIC_TABS
MONKEY_RANKING_TARGET = MC_RANKING_TARGET
MONKEY_STATIC_TABS_NEXT = "phase9_monkey_test_closeout"
MONKEY_CLOSEOUT_NEXT = "phase10_synthetic_open"
SYNTHETIC_TASK_TITLE = "Syntetic"
SYNTHETIC_DISPLAY_TITLE = "Synthetic / Syntetic"
SYNTHETIC_TASK_XML = "AutomaticRetest-Task5.xml"
SYNTHETIC_EXPECTED_DATABANKS = {
    "Input": "Monkey Test",
    "Output": "Syntetic",
}
SYNTHETIC_ACTIVE_CROSSCHECK = "MonteCarloRetest"
SYNTHETIC_ACTIVE_METHOD = "SyntheticBootstrapV3"
SYNTHETIC_NUMBER_OF_SIMULATIONS = "100"
SYNTHETIC_USE_FULL_SAMPLE = "true"
SYNTHETIC_METHOD_PARAMS_TARGET = {
    "BlockSize": "20",
    "WarmupBars": "200",
    "PreservePct": "85",
}
SYNTHETIC_NEXT_PHASE = "phase10_synthetic_data_databanks_resources_options"
SYNTHETIC_PERIOD_KEY = MC_PERIOD_KEY
SYNTHETIC_DATA_TEST_PRECISION = MC_DATA_TEST_PRECISION
SYNTHETIC_DATA_SESSION = MC_DATA_SESSION
SYNTHETIC_DEFAULT_CHART_TARGET = MC2_DEFAULT_CHART_TARGET
SYNTHETIC_DATA_ENGINE = SEQUENTIAL_DATA_ENGINE
SYNTHETIC_CUSTOM_DATA_ENGINE = SEQUENTIAL_CUSTOM_DATA_ENGINE
SYNTHETIC_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET = SEQUENTIAL_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET
SYNTHETIC_OPTIONS_PARAMS_TARGET = MC_OPTIONS_PARAMS_TARGET
SYNTHETIC_DATA_DATABANKS_RESOURCES_OPTIONS_NEXT = "phase10_synthetic_crosschecks"
SYNTHETIC_CROSSCHECK_PARENT_TARGET = {"use": "true", "evaluateAll": "true"}
SYNTHETIC_MC_BACKTEST_PRECISION = "-1"
SYNTHETIC_CROSSCHECKS_NEXT = "phase10_synthetic_passive_generation"
SYNTHETIC_PASSIVE_SOURCE_TASK_TITLE = MONKEY_TASK_TITLE
SYNTHETIC_STRATEGY_TYPE_TARGET = {
    "type": "simple",
    "additionalCharts": "2",
    "templateFile": "",
    "improveType": "strategy",
    "strategyFile": "",
    "architecture": "sq4",
    "improveDatabank": "Monkey Test",
}
SYNTHETIC_PASSIVE_BUILDMODE_TEXT_TARGET = MC2_PASSIVE_BUILDMODE_TEXT_TARGET
SYNTHETIC_PASSIVE_BUILDMODE_ATTR_TARGET = MC2_PASSIVE_BUILDMODE_ATTR_TARGET
SYNTHETIC_PASSIVE_GENERATION_NEXT = "phase10_synthetic_static_tabs"
SYNTHETIC_ACCEPTANCE_CONDITIONS_TARGET = [
    {
        "left": {
            "column": "NetProfit",
            "columnType": "0",
            "format": "Decimal2PL",
            "resultType": "MonteCarloRetest",
            "direction": "0",
            "sampleType": "10",
            "plType": "10",
            "confidenceLevel": "85",
            "market": "1",
            "subresult": "30",
            "pctRatio": "0",
            "class": "NetProfit",
        },
        "comparator": "<=",
        "right": {
            "column": "NetProfit",
            "columnType": "0",
            "format": "Decimal2PL",
            "resultType": "main",
            "direction": "0",
            "sampleType": "127",
            "plType": "10",
            "confidenceLevel": "90",
            "market": "1",
            "subresult": "30",
            "pctRatio": "0",
            "class": "NetProfit",
        },
    },
]
MONKEY_ACCEPTANCE_CONDITIONS_TARGET = [
    {
        "left": {
            "column": "NetProfit",
            "columnType": "0",
            "name": "Net profit",
            "format": "Decimal2PL",
            "resultType": "MonteCarloRetest",
            "direction": "0",
            "sampleType": "10",
            "plType": "10",
            "confidenceLevel": "80",
            "market": "1",
            "subresult": "30",
            "pctRatio": "0",
            "class": "NetProfit",
        },
        "comparator": ">=",
        "right": {
            "column": "NetProfit",
            "columnType": "0",
            "name": "Net profit",
            "format": "Decimal2PL",
            "resultType": "main",
            "direction": "0",
            "sampleType": "127",
            "plType": "10",
            "confidenceLevel": "90",
            "market": "1",
            "subresult": "30",
            "pctRatio": "50",
            "class": "NetProfit",
        },
    },
    {
        "left": {
            "column": "DrawdownPct",
            "columnType": "0",
            "name": "Max DD %",
            "format": "Decimal2Pct",
            "resultType": "MonteCarloRetest",
            "direction": "0",
            "sampleType": "127",
            "plType": "10",
            "confidenceLevel": "80",
            "market": "1",
            "subresult": "30",
            "pctRatio": "0",
            "class": "DrawdownPct",
        },
        "comparator": "<=",
        "right": {
            "column": "DrawdownPct",
            "columnType": "0",
            "name": "Max DD %",
            "dataType": "Decimal2Pct",
            "direction": "0",
            "sampleType": "127",
            "resultType": "main",
            "pctRatio": "200",
            "confidenceLevel": "90",
            "chartSetup": "10",
            "plType": "10",
            "class": "DrawdownPct",
        },
    },
]
SEQUENTIAL_PASSIVE_SOURCE_TASK_TITLE = MC2_TASK_TITLE
SEQUENTIAL_STRATEGY_TYPE_TARGET = {
    "type": "simple",
    "additionalCharts": "2",
    "templateFile": "",
    "improveType": "strategy",
    "strategyFile": "",
    "architecture": "sq4",
    "improveDatabank": "MC2",
}
SEQUENTIAL_PASSIVE_BUILDMODE_TEXT_TARGET = MC2_PASSIVE_BUILDMODE_TEXT_TARGET
SEQUENTIAL_PASSIVE_BUILDMODE_ATTR_TARGET = MC2_PASSIVE_BUILDMODE_ATTR_TARGET
SEQUENTIAL_STATIC_TABS = MC_STATIC_TABS
SEQUENTIAL_RANKING_TARGET = MC_RANKING_TARGET
SEQUENTIAL_CROSSCHECK_PARENT_TARGET = {"use": "true", "evaluateAll": "true"}
SEQUENTIAL_PARAMETER_SETTINGS_TARGET = {
    "DistributionUp": "130",
    "DistributionDown": "70",
    "Steps": "12",
    "ApplyToStrategy": "false",
}
SEQUENTIAL_WHAT_TO_PARAMETRIZE_ATTR_TARGET = {"type": "1", "symmetricVariables": "false"}
SEQUENTIAL_WHAT_TO_PARAMETRIZE_VALUES_TARGET = {
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
SEQUENTIAL_ACCEPTANCE_SETTINGS_TARGET = {
    "PctToPass": "80",
    "ResultsCount": "5",
    "StabilityRange": "25",
}
SEQUENTIAL_DECISION_PENDING = (
    "StrategyType.improveDatabank",
    "Data_vs_CustomData_carrier",
    "SequentialOptimization_acceptance_settings",
)


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def json_print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def slug(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    safe = safe.strip("._-")
    return safe[:120] or "item"


def question_id(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip()).strip("._-")
    if not safe:
        return "item"
    if len(safe) <= 120:
        return safe
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:10].upper()
    return f"{safe[:109].rstrip('._-')}_{digest}"


def canonical_task_key(value: str) -> str:
    key = re.sub(r"\s+", " ", value.strip().casefold())
    key = key.replace("syntetic", "synthetic")
    key = key.replace("foward", "forward")
    if "build" in key:
        return "build"
    return key


def ledger_root(project_root: Path) -> Path:
    return project_root / LEDGER_DIRNAME


def ensure_ledger(project_root: Path) -> dict[str, str]:
    root = ledger_root(project_root)
    dirs = {
        "root": root,
        "answers": root / "answers" / "capa1",
        "snapshots": root / "snapshots",
        "phase_reports": root / "phase_reports",
        "diffs": root / "diffs",
        "questionnaires": root / "questionnaires" / "capa1",
        "backups": root / "backups",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return {key: str(path) for key, path in dirs.items()}


def write_json(target: Path, payload: dict[str, Any]) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    tmp = target.with_name(f".{target.name}.{os.getpid()}.{time.time_ns()}.tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)
    return target


def safe_zip_text(zf: zipfile.ZipFile, name: str) -> str:
    try:
        return zf.read(name).decode("utf-8")
    except (KeyError, OSError, UnicodeDecodeError, zipfile.BadZipFile):
        return ""


def read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def xml_root_from_zip(zf: zipfile.ZipFile, name: str) -> ET.Element | None:
    try:
        data = zf.read(name)
    except (KeyError, OSError, zipfile.BadZipFile):
        return None
    try:
        return ET.fromstring(data)
    except ET.ParseError:
        return None


def cfx_for_project(root142: Path, project_name: str) -> Path:
    return root142 / "user" / "projects" / project_name / "project.cfx"


def task_title(task: ET.Element) -> str:
    return task.get("title") or task.get("name") or ""


def direct_sections(root: ET.Element | None) -> list[str]:
    if root is None:
        return []
    return [child.tag for child in list(root) if isinstance(child.tag, str)]


def active_cross_checks(root: ET.Element | None) -> list[dict[str, Any]]:
    if root is None:
        return []
    parent = root.find(".//CrossChecks")
    if parent is None:
        return []
    checks: list[dict[str, Any]] = []
    for check in list(parent):
        if check.get("use") != "true":
            continue
        methods = [
            {
                "type": method.get("type", ""),
                "use": method.get("use", ""),
                "settings": {
                    param.get("key", ""): (param.text or "")
                    for param in method.findall(".//Param")
                    if param.get("key")
                },
            }
            for method in check.findall(".//Method")
            if method.get("use") == "true"
        ]
        conditions = [
            dict(condition.attrib)
            for condition in check.findall(".//AcceptanceSettings//Condition")
            if condition.get("use", "true") != "false"
        ]
        checks.append({
            "id": check.tag,
            "use": check.get("use", ""),
            "methods": methods,
            "activeConditionCount": len(conditions),
        })
    return checks


def first_setup_summary(root: ET.Element | None) -> dict[str, Any]:
    if root is None:
        return {}
    setup = root.find(".//Data/Setups/Setup")
    if setup is None:
        return {}
    charts = [dict(chart.attrib) for chart in setup.findall(".//Chart")]
    ranges = [dict(item.attrib) for item in root.findall(".//Data/OutOfSample/Range")]
    return {
        "dateFrom": setup.get("dateFrom", ""),
        "dateTo": setup.get("dateTo", ""),
        "session": setup.get("session", ""),
        "testPrecision": setup.get("testPrecision", ""),
        "charts": charts,
        "outOfSampleRanges": ranges,
    }


def databank_summary(root: ET.Element | None) -> list[dict[str, str]]:
    if root is None:
        return []
    return [dict(item.attrib) for item in root.findall(".//Databanks/Databank")]


def randomize_spread_ranges(root: ET.Element | None) -> list[dict[str, str]]:
    if root is None:
        return []
    ranges: list[dict[str, str]] = []
    for method in root.findall(".//CrossChecks/*/Settings/Methods/Method"):
        if method.get("type") != "RandomizeSpread" or method.get("use") != "true":
            continue
        params = {
            param.get("key", ""): (param.text or "")
            for param in method.findall(".//Param")
            if param.get("key")
        }
        ranges.append({"min": params.get("Min", ""), "max": params.get("Max", "")})
    return ranges


def extract_cfx_snapshot(cfx: Path, label: str, include_hashes: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "label": label,
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": False,
        "sha256": "",
        "config": {},
        "tasks": [],
        "databanks": [],
        "xmlEntries": [],
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload
    payload["isZip"] = True
    payload["sha256"] = file_sha256(cfx)
    with zipfile.ZipFile(cfx) as zf:
        payload["xmlEntries"] = sorted(name for name in zf.namelist() if name.endswith(".xml"))
        if include_hashes:
            hashes: dict[str, str] = {}
            for name in payload["xmlEntries"]:
                hashes[name] = hashlib.sha256(zf.read(name)).hexdigest().upper()
            payload["xmlHashes"] = hashes
        config = xml_root_from_zip(zf, "config.xml")
        if config is None:
            payload["error"] = "config_unreadable"
            return payload
        payload["config"] = {"name": config.get("name", ""), "version": config.get("version", "")}
        payload["databanks"] = [
            {
                "name": databank.get("name", ""),
                "view": databank.get("view", ""),
            }
            for databank in config.findall(".//Databank")
        ]
        for index, task in enumerate(config.findall(".//Task"), start=1):
            file_name = task.get("taskXMLFile", "")
            root = xml_root_from_zip(zf, file_name) if file_name else None
            payload["tasks"].append({
                "position": index,
                "title": task_title(task),
                "name": task.get("name", ""),
                "type": task.get("type", ""),
                "active": task.get("active", ""),
                "taskXml": file_name,
                "sections": direct_sections(root),
                "setup": first_setup_summary(root),
                "databanks": databank_summary(root),
                "activeCrossChecks": active_cross_checks(root),
                "randomizeSpread": randomize_spread_ranges(root),
            })
    return payload


def config_databank_views(cfx: Path) -> dict[str, str]:
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        return {}
    with zipfile.ZipFile(cfx) as zf:
        config = xml_root_from_zip(zf, "config.xml")
        if config is None:
            return {}
        return {
            item.get("name", ""): item.get("view", "")
            for item in config.findall(".//Databank")
            if item.get("name")
        }


def load_task_root(cfx: Path, task_title_wanted: str) -> tuple[str, ET.Element | None]:
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        return "", None
    wanted = task_title_wanted.casefold()
    canonical_wanted = canonical_task_key(task_title_wanted)
    with zipfile.ZipFile(cfx) as zf:
        config = xml_root_from_zip(zf, "config.xml")
        if config is None:
            return "", None
        for task in config.findall(".//Task"):
            title = task_title(task)
            if title.casefold() == wanted or canonical_task_key(title) == canonical_wanted:
                file_name = task.get("taskXMLFile", "")
                return file_name, xml_root_from_zip(zf, file_name)
    return "", None


def find_section(root: ET.Element | None, tab: str) -> ET.Element | None:
    if root is None:
        return None
    key = SECTION_ALIASES.get(tab.strip().casefold(), tab.strip())
    if root.tag == key:
        return root
    direct = root.find(key)
    if direct is not None:
        return direct
    return root.find(f".//{key}")


def node_path(parts: list[str], node: ET.Element) -> str:
    if node.tag == "Param" and node.get("key"):
        return "/".join(parts + [f"Param:{node.get('key')}"])
    if node.tag == "Method" and node.get("type"):
        return "/".join(parts + [f"Method:{node.get('type')}"])
    if node.tag == "Condition" and (node.get("left") or node.get("metric") or node.get("name")):
        ident = node.get("left") or node.get("metric") or node.get("name") or "condition"
        return "/".join(parts + [f"Condition:{ident}"])
    return "/".join(parts + [node.tag])


def value_for_node(node: ET.Element) -> Any:
    value: dict[str, Any] = dict(node.attrib)
    text = (node.text or "").strip()
    if text:
        value["text"] = text
    return value


def collect_section_values(root: ET.Element | None, tab: str, max_values: int) -> dict[str, Any]:
    section = find_section(root, tab)
    if section is None:
        return {"exists": False, "section": SECTION_ALIASES.get(tab.casefold(), tab), "values": []}
    values: list[dict[str, Any]] = []
    limited = max_values > 0
    seen_paths: dict[str, int] = {}

    def unique_xml_path(raw_path: str) -> str:
        seen_paths[raw_path] = seen_paths.get(raw_path, 0) + 1
        return f"{raw_path}#{seen_paths[raw_path]}"

    def walk(node: ET.Element, parts: list[str]) -> None:
        if limited and len(values) >= max_values:
            return
        if node.tag in SKIP_SUBTREES and node is not section:
            return
        interesting = bool(node.attrib) or bool((node.text or "").strip())
        if interesting:
            raw_path = node_path(parts, node)
            values.append({
                "xmlPath": unique_xml_path(raw_path),
                "xmlPathBase": raw_path,
                "tag": node.tag,
                "value": value_for_node(node),
            })
        for child in list(node):
            if not isinstance(child.tag, str):
                continue
            walk(child, parts + [node.tag])

    walk(section, [])
    return {
        "exists": True,
        "section": section.tag,
        "maxValues": max_values if limited else "unlimited",
        "truncated": bool(limited and len(values) >= max_values),
        "values": values,
    }


def normalize_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def build_questionnaire(
    root142: Path,
    project_root: Path,
    task_title_wanted: str,
    tab: str,
    max_values: int,
    write: bool,
) -> dict[str, Any]:
    donor_cfx = cfx_for_project(root142, DEFAULT_DONOR_PROJECT)
    base_cfx = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    donor_file, donor_root = load_task_root(donor_cfx, task_title_wanted)
    base_file, base_root = load_task_root(base_cfx, task_title_wanted)
    donor_values = collect_section_values(donor_root, tab, max_values)
    base_values = collect_section_values(base_root, tab, max_values)
    base_by_path = {item["xmlPath"]: item for item in base_values.get("values", [])}
    donor_by_path = {item["xmlPath"]: item for item in donor_values.get("values", [])}
    all_paths = sorted(set(base_by_path) | set(donor_by_path))
    questions: list[dict[str, Any]] = []
    for path in all_paths:
        base_value = (base_by_path.get(path) or {}).get("value")
        donor_value = (donor_by_path.get(path) or {}).get("value")
        changed = normalize_value(base_value) != normalize_value(donor_value)
        qid = question_id(f"{task_title_wanted}-{tab}-{path}")
        questions.append({
            "id": qid,
            "taskTitle": task_title_wanted,
            "tab": tab,
            "xmlPath": path,
            "baseValue": base_value,
            "donorValue": donor_value,
            "changed": changed,
            "recommendation": "ask_operator" if changed else "keep_base",
            "options": [
                {"id": "keep_base", "label": "Mantener base", "value": base_value},
                {"id": "copy_donor_if_methodological", "label": "Usar valor donor si es metodologico", "value": donor_value},
                {"id": "custom_value", "label": "Valor manual", "value": None},
            ],
            "status": "pending",
        })
    payload = {
        "ok": bool(donor_root is not None or base_root is not None),
        "version": VERSION,
        "createdAt": now_iso(),
        "scope": "capa1",
        "taskTitle": task_title_wanted,
        "tab": tab,
        "donorTaskXml": donor_file,
        "baseTaskXml": base_file,
        "baseSection": base_values,
        "donorSection": donor_values,
        "questionCount": len(questions),
        "changedQuestionCount": sum(1 for item in questions if item["changed"]),
        "questions": questions,
        "discipline": [
            "Ask one task/tab at a time.",
            "Record each answer immediately with record-answer.",
            "Do not apply base changes until the phase is closed.",
        ],
    }
    if write:
        ensure_ledger(project_root)
        target = (
            ledger_root(project_root)
            / "questionnaires"
            / "capa1"
            / slug(task_title_wanted)
            / f"{slug(tab)}_{stamp()}.json"
        )
        write_json(target, payload)
        payload["written"] = str(target)
    return payload


def build_task_questionnaires(
    root142: Path,
    project_root: Path,
    task_title_wanted: str,
    max_values: int,
    write: bool,
) -> dict[str, Any]:
    donor_cfx = cfx_for_project(root142, DEFAULT_DONOR_PROJECT)
    base_cfx = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    donor_file, donor_root = load_task_root(donor_cfx, task_title_wanted)
    base_file, base_root = load_task_root(base_cfx, task_title_wanted)
    tabs = sorted(set(direct_sections(donor_root)) | set(direct_sections(base_root)))
    results = []
    for tab in tabs:
        questionnaire = build_questionnaire(
            root142,
            project_root,
            task_title_wanted=task_title_wanted,
            tab=tab,
            max_values=max_values,
            write=write,
        )
        results.append({
            "tab": tab,
            "ok": questionnaire.get("ok", False),
            "questionCount": questionnaire.get("questionCount", 0),
            "changedQuestionCount": questionnaire.get("changedQuestionCount", 0),
            "baseValueCount": len(((questionnaire.get("baseSection") or {}).get("values") or [])),
            "donorValueCount": len(((questionnaire.get("donorSection") or {}).get("values") or [])),
            "baseTruncated": (questionnaire.get("baseSection") or {}).get("truncated", False),
            "donorTruncated": (questionnaire.get("donorSection") or {}).get("truncated", False),
            "written": questionnaire.get("written", ""),
        })
    payload = {
        "ok": bool(donor_root is not None or base_root is not None),
        "version": VERSION,
        "createdAt": now_iso(),
        "scope": "capa1",
        "taskTitle": task_title_wanted,
        "donorTaskXml": donor_file,
        "baseTaskXml": base_file,
        "tabCount": len(tabs),
        "tabs": results,
        "totalQuestionCount": sum(int(item.get("questionCount") or 0) for item in results),
        "totalChangedQuestionCount": sum(int(item.get("changedQuestionCount") or 0) for item in results),
        "write": write,
        "maxValues": max_values if max_values > 0 else "unlimited",
    }
    if write:
        target = (
            ledger_root(project_root)
            / "questionnaires"
            / "capa1"
            / slug(task_title_wanted)
            / f"_task_summary_{stamp()}.json"
        )
        write_json(target, payload)
        payload["written"] = str(target)
    return payload


def compact_questionnaire_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": payload.get("ok", False),
        "version": payload.get("version", VERSION),
        "createdAt": payload.get("createdAt", ""),
        "scope": payload.get("scope", "capa1"),
        "taskTitle": payload.get("taskTitle", ""),
        "tab": payload.get("tab", ""),
        "donorTaskXml": payload.get("donorTaskXml", ""),
        "baseTaskXml": payload.get("baseTaskXml", ""),
        "questionCount": payload.get("questionCount", 0),
        "changedQuestionCount": payload.get("changedQuestionCount", 0),
        "baseValueCount": len(((payload.get("baseSection") or {}).get("values") or [])),
        "donorValueCount": len(((payload.get("donorSection") or {}).get("values") or [])),
        "baseTruncated": (payload.get("baseSection") or {}).get("truncated", False),
        "donorTruncated": (payload.get("donorSection") or {}).get("truncated", False),
        "written": payload.get("written", ""),
        "output": "summary_only_use_--full-output_to_print_all_questions",
    }


def backup_file(source: Path, backup_root: Path) -> Path:
    backup_root.mkdir(parents=True, exist_ok=True)
    target = backup_root / source.name
    counter = 2
    while target.exists():
        target = backup_root / f"{source.stem}.{counter}{source.suffix}"
        counter += 1
    shutil.copy2(source, target)
    return target


def replace_config_xml_in_cfx(cfx: Path, new_config_text: str) -> None:
    tmp = cfx.with_suffix(cfx.suffix + f".{os.getpid()}.{time.time_ns()}.tmp")
    with zipfile.ZipFile(cfx, "r") as source:
        with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as target:
            for item in source.infolist():
                data = new_config_text.encode("utf-8") if item.filename == "config.xml" else source.read(item.filename)
                target.writestr(item, data)
    tmp.replace(cfx)


def replace_zip_text_entry(cfx: Path, entry_name: str, new_text: str) -> None:
    tmp = cfx.with_suffix(cfx.suffix + f".{os.getpid()}.{time.time_ns()}.tmp")
    with zipfile.ZipFile(cfx, "r") as source:
        with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as target:
            for item in source.infolist():
                data = new_text.encode("utf-8") if item.filename == entry_name else source.read(item.filename)
                target.writestr(item, data)
    tmp.replace(cfx)


def find_build_mode(root: ET.Element | None) -> ET.Element | None:
    if root is None:
        return None
    what_to_build = find_section(root, "WhatToBuild")
    if what_to_build is not None:
        build_mode = what_to_build.find("BuildMode")
        if build_mode is not None:
            return build_mode
    return root.find(".//BuildMode")


def set_text_child(parent: ET.Element, tag: str, value: str, actions: list[dict[str, Any]]) -> None:
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag)
        before = None
    else:
        before = (child.text or "").strip()
    if before != value:
        child.text = value
    actions.append({
        "field": tag,
        "from": before,
        "to": value,
        "changed": before != value,
    })


def set_attr_child(parent: ET.Element, tag: str, attrs: dict[str, str], actions: list[dict[str, Any]]) -> None:
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag)
        before = {}
    else:
        before = dict(child.attrib)
    for key, value in attrs.items():
        child.set(key, value)
    after = dict(child.attrib)
    actions.append({
        "field": tag,
        "from": before,
        "to": after,
        "changed": before != after,
    })


def make_column_condition(
    column: str,
    comparator: str,
    value: str,
    fmt: str,
    sample_type: str = "127",
) -> ET.Element:
    condition = ET.Element("Condition", {"use": "true"})
    condition.text = "\n          "
    left = ET.SubElement(condition, "Left-Side", {"valueType": "column"})
    left.text = "\n            "
    left.tail = "\n          "
    column_value = ET.SubElement(left, "Column-Value", {
        "column": column,
        "columnType": "0",
        "format": fmt,
        "resultType": "main",
        "direction": "0",
        "sampleType": sample_type,
        "plType": "10",
        "confidenceLevel": "50",
        "market": "1",
        "subresult": "30",
        "pctRatio": "0",
        "class": column,
    })
    column_value.tail = "\n          "
    comp = ET.SubElement(condition, "Comparator", {"value": comparator})
    comp.tail = "\n          "
    right = ET.SubElement(condition, "Right-Side", {"valueType": "numeric"})
    right.text = "\n            "
    right.tail = "\n        "
    numeric = ET.SubElement(right, "Numeric-Value", {"value": value})
    numeric.tail = "\n          "
    return condition


def summarize_conditions(parent: ET.Element | None) -> list[dict[str, str]]:
    if parent is None:
        return []
    items: list[dict[str, str]] = []
    for condition in parent.findall("Condition"):
        column_value = condition.find(".//Column-Value")
        comparator = condition.find("Comparator")
        numeric = condition.find(".//Numeric-Value")
        items.append({
            "column": column_value.get("column", "") if column_value is not None else "",
            "comparator": comparator.get("value", "") if comparator is not None else "",
            "value": numeric.get("value", "") if numeric is not None else "",
            "use": condition.get("use", ""),
        })
    return items


def summarize_conditions_detailed(parent: ET.Element | None) -> list[dict[str, str]]:
    if parent is None:
        return []
    items: list[dict[str, str]] = []
    for condition in parent.findall("Condition"):
        column_value = condition.find(".//Column-Value")
        comparator = condition.find("Comparator")
        numeric = condition.find(".//Numeric-Value")
        items.append({
            "column": column_value.get("column", "") if column_value is not None else "",
            "comparator": comparator.get("value", "") if comparator is not None else "",
            "value": numeric.get("value", "") if numeric is not None else "",
            "format": column_value.get("format", "") if column_value is not None else "",
            "sampleType": column_value.get("sampleType", "") if column_value is not None else "",
            "use": condition.get("use", ""),
        })
    return items


def set_ranking_conditions_from_target(
    rankings: ET.Element,
    target: list[dict[str, str]],
    actions: list[dict[str, Any]],
    field: str,
) -> None:
    conditions = rankings.find("Conditions")
    if conditions is None:
        conditions = ET.SubElement(rankings, "Conditions")
        before: list[dict[str, str]] = []
    else:
        before = summarize_conditions_detailed(conditions)
        for child in list(conditions):
            conditions.remove(child)
    conditions.text = "\n      "
    for index, item in enumerate(target):
        condition = make_column_condition(
            column=item["column"],
            comparator=item["comparator"],
            value=item["value"],
            fmt=item["format"],
            sample_type=item.get("sampleType", "127"),
        )
        condition.tail = "\n    " if index == len(target) - 1 else "\n      "
        conditions.append(condition)
    after = summarize_conditions_detailed(conditions)
    actions.append({
        "field": field,
        "from": before,
        "to": after,
        "changed": before != after,
    })


def set_initial_population_conditions(build_mode: ET.Element, actions: list[dict[str, Any]]) -> None:
    conditions = build_mode.find("Conditions")
    if conditions is None:
        conditions = ET.SubElement(build_mode, "Conditions")
        before: list[dict[str, str]] = []
    else:
        before = summarize_conditions(conditions)
        for child in list(conditions):
            conditions.remove(child)
    conditions.text = "\n        "
    for index, target in enumerate(BUILD_INITIAL_CONDITIONS_TARGET):
        condition = make_column_condition(
            column=target["column"],
            comparator=target["comparator"],
            value=target["value"],
            fmt=target["format"],
        )
        condition.tail = "\n      " if index == len(BUILD_INITIAL_CONDITIONS_TARGET) - 1 else "\n        "
        conditions.append(condition)
    after = summarize_conditions(conditions)
    actions.append({
        "field": "InitialPopulationConditions",
        "from": before,
        "to": after,
        "changed": before != after,
    })


def remove_children_by_tag(parent: ET.Element, tags: list[str], actions: list[dict[str, Any]]) -> None:
    for tag in tags:
        removed = []
        for child in list(parent.findall(tag)):
            removed.append(value_for_node(child))
            parent.remove(child)
        actions.append({
            "field": f"RemoveLegacy:{tag}",
            "from": removed,
            "to": [],
            "changed": bool(removed),
        })


def serialize_xml(root: ET.Element) -> str:
    return ET.tostring(root, encoding="unicode", short_empty_elements=True)


def update_build_genetic_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, "Build")
    payload["taskXml"] = task_xml_name
    build_mode = find_build_mode(root)
    if not task_xml_name or root is None or build_mode is None:
        payload["error"] = "build_task_or_build_mode_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    for tag, value in BUILD_GENETIC_TARGET.items():
        set_text_child(build_mode, tag, value, payload["actions"])
    for tag, attrs in BUILD_GENETIC_ATTR_TARGET.items():
        set_attr_child(build_mode, tag, attrs, payload["actions"])
    set_initial_population_conditions(build_mode, payload["actions"])
    remove_children_by_tag(build_mode, BUILD_MODE_LEGACY_NODES, payload["actions"])

    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetRationale"] = {
        "marketSides": "left untouched; generator remains responsible for side selection",
        "trainingValidation": "Build is IS edge mining; external Capa1/Capa2 retests are the validation layers",
        "fitnessType": "10 = In sample (whole)",
        "legacyCleanup": "SQX 142/143 SettingsGeneticOptionsService reads/writes EvoRestartOnStagnation attributes and Conditions, not legacy sibling nodes.",
    }
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_build_genetic_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase2_build_genetic_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_build_genetic_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(item.get("exists") and item.get("isZip") and not item.get("error") for item in results.values()),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_genetic_target",
        "apply": apply,
        "target": target,
        "results": results,
        "targetValues": {
            "text": BUILD_GENETIC_TARGET,
            "attributes": BUILD_GENETIC_ATTR_TARGET,
            "initialConditions": BUILD_INITIAL_CONDITIONS_TARGET,
        },
        "nextPhase": "phase2_build_diff_review" if not apply else "phase2_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_genetic_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def find_rankings(root: ET.Element | None) -> ET.Element | None:
    return find_section(root, "Rankings") if root is not None else None


def update_build_ranking_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, "Build")
    payload["taskXml"] = task_xml_name
    rankings = find_rankings(root)
    if not task_xml_name or root is None or rankings is None:
        payload["error"] = "build_task_or_rankings_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    set_text_child(rankings, "MaxStrategies", BUILD_RANKING_TARGET["MaxStrategies"], payload["actions"])
    stop_condition = rankings.find("StopCondition")
    if stop_condition is None:
        stop_condition = ET.SubElement(rankings, "StopCondition")
        before = {}
    else:
        before = dict(stop_condition.attrib)
    for key, value in BUILD_RANKING_TARGET["StopCondition"].items():
        stop_condition.set(key, value)
    after = dict(stop_condition.attrib)
    payload["actions"].append({
        "field": "StopCondition",
        "from": before,
        "to": after,
        "changed": before != after,
    })

    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetRationale"] = {
        "methodology": "operator accepted the recommendation 2000/500",
        "quality": "keeps ranking logic intact while reducing selection-by-luck surface",
        "scope": "only MaxStrategies and StopCondition.passedStrategies are changed",
    }
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_build_ranking_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase2_build_ranking_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_build_ranking_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(item.get("exists") and item.get("isZip") and not item.get("error") for item in results.values()),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_ranking_target",
        "apply": apply,
        "target": target,
        "results": results,
        "targetValues": BUILD_RANKING_TARGET,
        "nextPhase": "phase2_build_ranking_diff_review" if not apply else "phase2_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_ranking_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def find_blocks(root: ET.Element | None) -> ET.Element | None:
    return find_section(root, "Blocks") if root is not None else None


def block_key_action(block: ET.Element) -> dict[str, Any]:
    return {
        "key": block.get("key", ""),
        "use": block.get("use", ""),
        "probability": block.get("probability", ""),
        "category": block.get("category", ""),
    }


def enforce_order_types(blocks: ET.Element, actions: list[dict[str, Any]]) -> None:
    order_types = blocks.find("OrderTypes")
    if order_types is None:
        actions.append({"field": "OrderTypes", "error": "missing", "changed": False})
        return
    for block in order_types.findall("Block"):
        key = block.get("key", "")
        if key not in BUILD_ORDER_TYPE_TARGET:
            continue
        before = block.get("use", "")
        wanted = BUILD_ORDER_TYPE_TARGET[key]
        block.set("use", wanted)
        actions.append({
            "field": f"OrderTypes:{key}",
            "from": before,
            "to": wanted,
            "changed": before != wanted,
        })


def enforce_exit_types(blocks: ET.Element, actions: list[dict[str, Any]]) -> None:
    exit_types = blocks.find("ExitTypes")
    if exit_types is None:
        actions.append({"field": "ExitTypes", "error": "missing", "changed": False})
        return
    removed = []
    for block in list(exit_types.findall("Block")):
        key = block.get("key", "")
        if any(token in key for token in BUILD_EXIT_TYPE_BANNED_TOKENS):
            removed.append(block_key_action(block))
            exit_types.remove(block)
            continue
        before = block.get("use", "")
        wanted = "true" if key == BUILD_EXIT_TYPE_ACTIVE_KEY else "false"
        block.set("use", wanted)
        if key == BUILD_EXIT_TYPE_ACTIVE_KEY:
            block.set("probability", "100")
            for value in block.findall("Value"):
                if value.get("key") == "undefined":
                    value.set("use", "true")
        actions.append({
            "field": f"ExitTypes:{key}",
            "from": before,
            "to": wanted,
            "changed": before != wanted,
        })
    actions.append({
        "field": "ExitTypes:removeDayBasedExits",
        "from": removed,
        "to": [],
        "changed": bool(removed),
    })


def enforce_external_custom_data(blocks: ET.Element, actions: list[dict[str, Any]]) -> None:
    custom_data = blocks.find("CustomData")
    if custom_data is None:
        custom_data = ET.SubElement(blocks, "CustomData")
        before = {}
    else:
        before = dict(custom_data.attrib)
    for key, value in BUILD_EXTERNAL_CUSTOM_DATA_TARGET.items():
        custom_data.set(key, value)
    removed_children = [child.tag for child in list(custom_data)]
    for child in list(custom_data):
        custom_data.remove(child)
    after = dict(custom_data.attrib)
    actions.append({
        "field": "CustomData",
        "from": {"attributes": before, "children": removed_children},
        "to": {"attributes": after, "children": []},
        "changed": before != after or bool(removed_children),
    })


def enforce_disabled_build_block_categories(blocks: ET.Element, actions: list[dict[str, Any]]) -> None:
    for category in BUILD_BLOCK_CATEGORY_DISABLE_TARGET:
        matching_blocks = [block for block in blocks.findall(".//Block") if block.get("category") == category]
        selected_before = [block_key_action(block) for block in matching_blocks if block.get("use") == "true"]
        for block in matching_blocks:
            block.set("use", "false")
        actions.append({
            "field": f"BuildingBlocks:disableCategory:{category}",
            "from": {
                "selectedCount": len(selected_before),
                "selected": selected_before[:50],
                "truncated": len(selected_before) > 50,
            },
            "to": {"selectedCount": 0},
            "changed": bool(selected_before),
        })


def active_building_block_keys(blocks: ET.Element | None) -> list[str]:
    if blocks is None:
        return []
    building_blocks = blocks.find("BuildingBlocks")
    if building_blocks is None:
        return []
    return [
        block.get("key", "")
        for block in building_blocks.findall("Block")
        if block.get("key")
        and block.get("key") not in {"#Left#", "#Right#"}
        and str(block.get("use", "")).lower() == "true"
    ]


def indicator_family_keys(active_keys: list[str]) -> list[str]:
    return [key for key in active_keys if key.startswith("Indicators.")]


def blocksettings_entries_by_id(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(entry.get("canonicalId")): entry
        for entry in manifest.get("entries", [])
        if entry.get("canonicalId")
    }


def normalize_blocksetting_token(value: str) -> str:
    token = str(value or "").strip()
    if token.lower().endswith(".sqb"):
        token = token[:-4]
    return token


def family_from_blocksetting_manifest(manifest: dict[str, Any], value: str) -> str:
    aliases = manifest.get("aliases") or {}
    token = normalize_blocksetting_token(value)
    resolved = aliases.get(token) or aliases.get(token + ".sqb") or token
    entry = blocksettings_entries_by_id(manifest).get(str(resolved))
    if entry:
        return str(entry.get("family") or "")
    lower = str(resolved).lower()
    if "soporteresistencia" in lower:
        return "sr"
    for family in ("tendencia", "momentum", "volatilidad", "regimen", "volumen", "estadistico", "filtros"):
        if family in lower:
            return family
    return ""


def resolve_capa1_blocksetting_manifest_entry(blocksetting: str, timeframe: str) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = read_json(BLOCKSETTINGS_MANIFEST_PATH, {})
    entries = blocksettings_entries_by_id(manifest)
    aliases = manifest.get("aliases") or {}
    token = normalize_blocksetting_token(blocksetting)
    resolved = str(aliases.get(token) or aliases.get(token + ".sqb") or token)
    family = family_from_blocksetting_manifest(manifest, resolved)
    resolver = manifest.get("capa1Resolver") or {}
    family_rules = (resolver.get("families") or {}).get(family) or {}
    tf = str(timeframe or "").strip().upper()
    intraday_timeframes = set(resolver.get("intradayTimeframes") or [])
    if tf in intraday_timeframes and family_rules.get("intraday"):
        candidate = str(family_rules["intraday"])
    else:
        candidate = str(family_rules.get("default") or resolved)
    entry = entries.get(candidate)
    if not entry:
        raise ValueError(f"BlockSetting not found in manifest: {candidate}")
    return manifest, entry


def read_blocksetting_blocks(entry: dict[str, Any]) -> ET.Element:
    filename = str(entry.get("filename") or "")
    path = BLOCKSETTINGS_RESOURCE_DIR / filename
    if not filename or not path.is_file():
        raise FileNotFoundError(f"BlockSetting .sqb not found: {path}")
    with zipfile.ZipFile(path) as zf:
        return ET.fromstring(zf.read("config.xml"))


def replace_building_blocks_from_source(blocks: ET.Element, source_blocks: ET.Element) -> dict[str, Any]:
    current_building_blocks = blocks.find("BuildingBlocks")
    source_building_blocks = source_blocks.find("BuildingBlocks")
    if source_building_blocks is None:
        return {"field": "BuildingBlocks", "error": "source_missing", "changed": False}
    current_text_raw = serialize_xml(current_building_blocks) if current_building_blocks is not None else ""
    source_text_raw = serialize_xml(source_building_blocks)
    current_text = current_text_raw.strip()
    source_text = source_text_raw.strip()
    source_copy = ET.fromstring(source_text_raw)
    if current_building_blocks is None:
        blocks.insert(0, source_copy)
    else:
        children = list(blocks)
        index = children.index(current_building_blocks)
        blocks.remove(current_building_blocks)
        blocks.insert(index, source_copy)
    return {
        "field": "BuildingBlocks",
        "from": {"sha256": hashlib.sha256(current_text.encode("utf-8")).hexdigest().upper()},
        "to": {"sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest().upper()},
        "changed": current_text != source_text,
    }


def update_build_indicators_target_in_cfx(
    cfx: Path,
    backup_root: Path,
    blocksetting: str,
    timeframe: str,
    apply: bool,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, "Build")
    payload["taskXml"] = task_xml_name
    blocks = find_blocks(root)
    if not task_xml_name or root is None or blocks is None:
        payload["error"] = "build_task_or_blocks_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    _, entry = resolve_capa1_blocksetting_manifest_entry(blocksetting, timeframe)
    source_blocks = read_blocksetting_blocks(entry)
    before_active = active_building_block_keys(blocks)
    expected_active = active_building_block_keys(source_blocks)
    payload["blocksetting"] = {
        "requested": blocksetting,
        "timeframe": timeframe,
        "resolved": entry.get("canonicalId"),
        "filename": entry.get("filename"),
        "sha256": entry.get("sha256"),
        "activeBlocks": len(expected_active),
        "activeIndicators": indicator_family_keys(expected_active),
    }
    payload["actions"].append({
        "field": "BuildingBlocks:activeContract",
        "from": {
            "activeCount": len(before_active),
            "missingExpected": sorted(set(expected_active) - set(before_active)),
            "extraActive": sorted(set(before_active) - set(expected_active)),
        },
        "to": {"activeCount": len(expected_active)},
        "changed": set(before_active) != set(expected_active),
    })
    payload["actions"].append(replace_building_blocks_from_source(blocks, source_blocks))
    enforce_disabled_build_block_categories(blocks, payload["actions"])

    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetRationale"] = {
        "source": "BuildingBlocks is copied from the resolved real .sqb BlockSetting source, not from the donor project.",
        "basePlaceholder": "Capa1 base uses BS_Volatilidad/H4 as placeholder; Project Generator resolves the final BlockSetting by family and timeframe.",
        "fixedLeftSide": "Signals and Stop/Limit entry blocks remain disabled after the source copy.",
    }
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_build_indicators_target(
    root142: Path,
    project_root: Path,
    target: str,
    blocksetting: str,
    timeframe: str,
    apply: bool,
) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase2_build_indicators_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_build_indicators_target_in_cfx(path, backup_root / name, blocksetting, timeframe, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(item.get("exists") and item.get("isZip") and not item.get("error") for item in results.values()),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_indicators_target",
        "apply": apply,
        "target": target,
        "requestedBlocksetting": blocksetting,
        "requestedTimeframe": timeframe,
        "results": results,
        "nextPhase": "phase2_build_indicators_diff_review" if not apply else "phase2_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_indicators_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def generator_period(period_key: str) -> tuple[str, str]:
    profile = read_json(GENERATOR_PROFILES_PATH, {})
    raw_period = (profile.get("retestPeriods") or {}).get(period_key) or []
    if len(raw_period) != 2:
        raise ValueError(f"Missing generator period {period_key}")
    return str(raw_period[0]), str(raw_period[1])


def epoch_ms_for_date(value: str) -> int:
    parsed = datetime.strptime(value, "%Y.%m.%d").replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def bounded_period_ms(period: tuple[str, str], data_from: Any, data_to: Any) -> tuple[str, str]:
    period_from = epoch_ms_for_date(period[0])
    period_to = epoch_ms_for_date(period[1])
    try:
        available_from = int(data_from)
        available_to = int(data_to)
    except (TypeError, ValueError):
        return str(period_from), str(period_to)
    if period_to < available_from or period_from > available_to:
        return str(available_from), str(available_to)
    return str(max(period_from, available_from)), str(min(period_to, available_to))


def _format_decimal(value: Any, default: str = "0.0") -> str:
    if value is None or value == "":
        return default
    try:
        text = f"{float(value):.12g}"
    except (TypeError, ValueError):
        text = str(value)
    if "e" in text:
        text = text.replace("e", "E")
    return text


def _sqlite_row_dict(row: sqlite3.Row | None) -> dict[str, Any]:
    if row is None:
        return {}
    return {key: row[key] for key in row.keys()}


def _retest1_broker_profile() -> dict[str, Any]:
    profile = read_json(GENERATOR_PROFILES_PATH, {})
    return dict(((profile.get("brokerProfiles") or {}).get(RETEST1_BROKER_PROFILE_ID) or {}))


def fallback_retest1_oos2_resource() -> dict[str, Any]:
    profile = _retest1_broker_profile()
    symbol = f"{RETEST1_PLACEHOLDER_ASSET}{profile.get('brokerPostfix') or '_dukascopy'}"
    return {
        "asset": RETEST1_PLACEHOLDER_ASSET,
        "symbol": symbol,
        "instrument": symbol,
        "source_id": str(profile.get("sourceId") or RETEST1_EXPECTED_SOURCE_ID),
        "broker_id": str(profile.get("brokerId") or RETEST1_EXPECTED_BROKER_ID),
        "broker_name": profile.get("brokerName") or "[[Dukascopy]]",
        "broker_description": profile.get("brokerDescription") or "Dukascopy",
        "broker_postfix": profile.get("brokerPostfix") or "_dukascopy",
        "broker_timezone": profile.get("timezone") or "EETUS",
        "precision": profile.get("precision") or "TICK",
        "description": "FX_Forex_Currency",
        "tick_size": "0.0001",
        "tick_step": "0.00001",
        "min_distance": "0.0",
        "spread": "1.9",
        "slippage": "0.0",
        "point_value": "71848.371197",
        "data_type": "3",
        "exchange": "",
        "country": "",
        "sector": "Currency",
        "ordersize_multiplier": "1.0",
        "ordersize_step": "0.01",
        "commissions_xml": '<Method type="SizeBased" use="true"><Params><Param key="Commission" className="SizeBased">0.00</Param></Params></Method>',
        "swap_xml": '<Swap use="true" type="points" long="-2.07" short="-2.36" tripleSwapOn="NEVER" rolloutHour="23:00"/>',
        "swap_attrs": {
            "use": "true",
            "type": "points",
            "long": "-2.07",
            "short": "-2.36",
            "tripleSwapOn": "NEVER",
            "rolloutHour": "23:00",
        },
        "date_from_ms": str(epoch_ms_for_date(generator_period(RETEST1_PERIOD_KEY)[0])),
        "date_to_ms": str(epoch_ms_for_date(generator_period(RETEST1_PERIOD_KEY)[1])),
        "u_symbol": RETEST1_PLACEHOLDER_ASSET,
        "u_symbol_name": RETEST1_PLACEHOLDER_ASSET,
        "source": "fallback_static_dukascopy_oos2",
    }


def retest1_oos2_target_resource(root142: Path | None = None) -> dict[str, Any]:
    """Resolve the protected RETEST 1 placeholder from SQX 142 data.db when possible."""
    target = fallback_retest1_oos2_resource()
    if root142 is None:
        return target
    db_path = root142 / "user" / "data" / "data.db"
    if not db_path.is_file():
        return target

    symbol = target["symbol"]
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            instrument = _sqlite_row_dict(conn.execute(
                "SELECT * FROM INSTRUMENTS WHERE INSTRUMENT = ?",
                (symbol,),
            ).fetchone())
            data = _sqlite_row_dict(conn.execute(
                """
                SELECT SYMBOL,INSTRUMENT,TIMEFRAME,TIMEZONE,DATEFROM,DATETO,ROWS,DATATYPE,USYMBOL,USYMBOLNAME,REMOVE_WEEKENDS,SOURCE
                FROM DATA
                WHERE SYMBOL = ? OR INSTRUMENT = ?
                ORDER BY CASE WHEN TIMEFRAME = 'TICK' THEN 0 ELSE 1 END, ROWS DESC
                LIMIT 1
                """,
                (symbol, symbol),
            ).fetchone())
            broker_id = instrument.get("BROKER_ID") or int(RETEST1_EXPECTED_BROKER_ID)
            broker = _sqlite_row_dict(conn.execute(
                "SELECT * FROM BROKER WHERE ID = ?",
                (broker_id,),
            ).fetchone())
        finally:
            conn.close()
    except sqlite3.Error:
        return target

    if not instrument:
        return target

    target.update({
        "instrument": str(instrument.get("INSTRUMENT") or symbol),
        "description": str(instrument.get("DESCRIPTION") or target["description"]),
        "tick_size": _format_decimal(instrument.get("TICKSIZE"), target["tick_size"]),
        "tick_step": _format_decimal(instrument.get("TICKSTEP"), target["tick_step"]),
        "min_distance": _format_decimal(instrument.get("MIN_DISTANCE"), target["min_distance"]),
        "spread": _format_decimal(instrument.get("DEFAULTSPREAD"), target["spread"]),
        "slippage": _format_decimal(instrument.get("DEFAULTSLIPPAGE"), target["slippage"]),
        "point_value": _format_decimal(instrument.get("POINTVALUE"), target["point_value"]),
        "data_type": str(instrument.get("DATATYPE") or target["data_type"]),
        "exchange": str(instrument.get("EXCHANGE") or ""),
        "country": str(instrument.get("COUNTRY") or ""),
        "sector": str(instrument.get("SECTOR") or target["sector"]),
        "ordersize_multiplier": _format_decimal(instrument.get("ORDERSIZEMULTIPLIER"), target["ordersize_multiplier"]),
        "ordersize_step": _format_decimal(instrument.get("ORDERSIZESTEP"), target["ordersize_step"]),
        "commissions_xml": str(instrument.get("COMMISSIONS") or target["commissions_xml"]),
        "swap_xml": str(instrument.get("SWAP") or target["swap_xml"]),
        "broker_id": str(instrument.get("BROKER_ID") or target["broker_id"]),
        "broker_postfix": str(broker.get("POSTFIX") or target["broker_postfix"]),
        "broker_name": str(broker.get("NAME") or target["broker_name"]),
        "broker_description": str(broker.get("DESC") or target["broker_description"]),
        "broker_timezone": str(broker.get("MT_TIMEZONE") or target["broker_timezone"]),
        "date_from_ms": str(data.get("DATEFROM") or target["date_from_ms"]),
        "date_to_ms": str(data.get("DATETO") or target["date_to_ms"]),
        "u_symbol": str(data.get("USYMBOL") or RETEST1_PLACEHOLDER_ASSET),
        "u_symbol_name": str(data.get("USYMBOLNAME") or RETEST1_PLACEHOLDER_ASSET),
        "source": "sqx142_data_db_instruments",
    })
    # Methodology owns the cross-broker profile even if the DATA row carries a legacy broker id.
    profile = _retest1_broker_profile()
    target["source_id"] = str(profile.get("sourceId") or RETEST1_EXPECTED_SOURCE_ID)
    target["broker_id"] = str(profile.get("brokerId") or RETEST1_EXPECTED_BROKER_ID)
    target["broker_postfix"] = str(profile.get("brokerPostfix") or "_dukascopy")
    target["broker_name"] = str(profile.get("brokerName") or target["broker_name"])
    target["broker_description"] = str(profile.get("brokerDescription") or target["broker_description"])
    target["broker_timezone"] = str(profile.get("timezone") or target["broker_timezone"])
    target["precision"] = str(profile.get("precision") or target["precision"])
    target["swap_attrs"] = swap_attrs_from_xml(target["swap_xml"], target["swap_attrs"])
    return target


def swap_attrs_from_xml(raw: str, fallback: dict[str, str]) -> dict[str, str]:
    try:
        node = ET.fromstring(raw)
    except ET.ParseError:
        return dict(fallback)
    if node.tag != "Swap":
        return dict(fallback)
    attrs = dict(fallback)
    attrs.update({key: str(value) for key, value in node.attrib.items()})
    return attrs


def ensure_sizebased_commission(setup: ET.Element, commission_value: str, actions: list[dict[str, Any]]) -> None:
    commissions = setup.find("Commissions")
    if commissions is None:
        commissions = ET.SubElement(setup, "Commissions")
        before = []
    else:
        before = [
            {
                "type": method.get("type", ""),
                "use": method.get("use", ""),
                "params": {
                    param.get("key", ""): (param.text or "")
                    for param in method.findall("./Params/Param")
                    if param.get("key")
                },
            }
            for method in commissions.findall("Method")
        ]
    for method in commissions.findall("Method"):
        method.set("use", "false")
    size_method = commissions.find("Method[@type='SizeBased']")
    if size_method is None:
        size_method = ET.SubElement(commissions, "Method", {"type": "SizeBased"})
    size_method.set("use", "true")
    params = size_method.find("Params")
    if params is None:
        params = ET.SubElement(size_method, "Params")
    param = params.find("Param[@key='Commission']")
    if param is None:
        param = ET.SubElement(params, "Param", {"key": "Commission", "className": "SizeBased"})
    param.set("className", "SizeBased")
    param.text = commission_value
    after = [
        {
            "type": method.get("type", ""),
            "use": method.get("use", ""),
            "params": {
                param_node.get("key", ""): (param_node.text or "")
                for param_node in method.findall("./Params/Param")
                if param_node.get("key")
            },
        }
        for method in commissions.findall("Method")
    ]
    actions.append({
        "field": "Data/Setup/Commissions",
        "from": before,
        "to": after,
        "changed": before != after,
    })


def ensure_single_child(parent: ET.Element, tag: str, actions: list[dict[str, Any]], field: str) -> ET.Element:
    existing = list(parent.findall(tag))
    if existing:
        node = existing[0]
        removed = [value_for_node(item) for item in existing[1:]]
        for item in existing[1:]:
            parent.remove(item)
    else:
        node = ET.SubElement(parent, tag)
        removed = []
    actions.append({
        "field": f"{field}:dedupe",
        "from": removed,
        "to": [],
        "changed": bool(removed) or not existing,
    })
    return node


def make_retest1_instrument_attrs(resource: dict[str, Any]) -> dict[str, str]:
    return {
        "instrument": str(resource["instrument"]),
        "description": str(resource.get("description") or ""),
        "tickSize": str(resource.get("tick_size") or ""),
        "tickStep": str(resource.get("tick_step") or ""),
        "minDistance": str(resource.get("min_distance") or "0.0"),
        "tickValueInMoney": "0.0",
        "dateFrom": "0",
        "dateTo": "0",
        "rows": "0",
        "totalDays": "0",
        "defaultSpread": str(resource.get("spread") or ""),
        "defaultSlippage": str(resource.get("slippage") or "0.0"),
        "decimals": "5",
        "commissions": str(resource.get("commissions_xml") or ""),
        "pointValue": str(resource.get("point_value") or ""),
        "dataType": str(resource.get("data_type") or "3"),
        "recognizedFromOrders": "false",
        "exchange": str(resource.get("exchange") or ""),
        "country": str(resource.get("country") or ""),
        "sector": str(resource.get("sector") or ""),
        "swap": str(resource.get("swap_xml") or ""),
        "orderSizeMultiplier": str(resource.get("ordersize_multiplier") or "1.0"),
        "orderSizeStep": str(resource.get("ordersize_step") or "0.01"),
        "broker": str(resource.get("broker_id") or RETEST1_EXPECTED_BROKER_ID),
    }


def compact_retest1_resources_summary(root: ET.Element) -> dict[str, Any]:
    resources = root.find(".//Resources")
    if resources is None:
        return {"exists": False}
    summary = build_resources_summary(root)
    summary.update({
        "customIndicators": len(resources.findall("./CustomIndicators/*")),
        "customBlocks": len(resources.findall("./CustomBlocks/*")),
        "childOrder": [child.tag for child in list(resources)],
    })
    return summary


def apply_retest1_data_resources_to_root(root: ET.Element, resource: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    period = generator_period(RETEST1_PERIOD_KEY)
    setup = root.find(".//Data/Setups/Setup")
    data = find_section(root, "Data")
    if setup is None or data is None:
        actions.append({"field": "Data", "error": "missing_setup_or_data", "changed": False})
        return actions

    for setup_index, current_setup in enumerate(root.findall(".//Setup"), start=1):
        setup_label = "Data/Setup" if current_setup is setup else f"Setup#{setup_index}"
        for key, wanted in {
            "dateFrom": period[0],
            "dateTo": period[1],
            "testPrecision": RETEST1_DATA_TEST_PRECISION,
            "session": RETEST1_DATA_SESSION,
        }.items():
            before = current_setup.get(key, "")
            current_setup.set(key, wanted)
            actions.append({"field": f"{setup_label}:{key}", "from": before, "to": wanted, "changed": before != wanted})

        chart = ensure_single_child(current_setup, "Chart", actions, f"{setup_label}/Chart")
        before_chart = dict(chart.attrib)
        chart.attrib.clear()
        chart.attrib.update({
            "symbol": str(resource["symbol"]),
            "timeframe": RETEST1_PLACEHOLDER_TIMEFRAME,
            "spread": str(resource["spread"]),
        })
        actions.append({
            "field": f"{setup_label}/Chart",
            "from": before_chart,
            "to": dict(chart.attrib),
            "changed": before_chart != dict(chart.attrib),
        })

        ensure_sizebased_commission(current_setup, "0.00", actions)

        swap = ensure_single_child(current_setup, "Swap", actions, f"{setup_label}/Swap")
        before_swap = dict(swap.attrib)
        swap.attrib.clear()
        swap.attrib.update({key: str(value) for key, value in resource.get("swap_attrs", {}).items()})
        actions.append({
            "field": f"{setup_label}/Swap",
            "from": before_swap,
            "to": dict(swap.attrib),
            "changed": before_swap != dict(swap.attrib),
        })

    out_of_sample = data.find("OutOfSample")
    if out_of_sample is None:
        out_of_sample = ET.SubElement(data, "OutOfSample", {"showGraph": "false"})
        before_oos_attrs = {}
    else:
        before_oos_attrs = dict(out_of_sample.attrib)
        out_of_sample.set("showGraph", "false")
    removed_ranges = [dict(item.attrib) for item in out_of_sample.findall("Range")]
    for range_node in list(out_of_sample.findall("Range")):
        out_of_sample.remove(range_node)
    actions.append({
        "field": "Data/OutOfSample",
        "from": {"attrs": before_oos_attrs, "ranges": removed_ranges},
        "to": {"attrs": dict(out_of_sample.attrib), "ranges": []},
        "changed": before_oos_attrs != dict(out_of_sample.attrib) or bool(removed_ranges),
    })

    resources = find_section(root, "Resources")
    if resources is None:
        resources = ET.SubElement(root, "Resources")
        before_resources: dict[str, Any] = {"exists": False}
    else:
        before_resources = compact_retest1_resources_summary(root)
        for child in list(resources):
            resources.remove(child)

    date_from, date_to = bounded_period_ms(period, resource.get("date_from_ms"), resource.get("date_to_ms"))
    symbols = ET.SubElement(resources, "Symbols")
    symbol_node = ET.SubElement(symbols, "Symbol", {
        "name": str(resource["symbol"]),
        "source": str(resource["source_id"]),
        "barType": "1",
        "precision": str(resource.get("precision") or "TICK"),
        "timezone": str(resource.get("broker_timezone") or "EETUS"),
        "dateFrom": date_from,
        "dateTo": date_to,
        "uSymbol": str(resource.get("u_symbol") or RETEST1_PLACEHOLDER_ASSET),
        "uSymbolName": str(resource.get("u_symbol_name") or RETEST1_PLACEHOLDER_ASSET),
        "removeWeekends": "false",
        "broker": str(resource["broker_id"]),
    })
    instrument_attrs = make_retest1_instrument_attrs(resource)
    ET.SubElement(symbol_node, "InstrumentInfo", instrument_attrs)

    brokers = ET.SubElement(resources, "Brokers")
    ET.SubElement(brokers, "Broker", {
        "id": str(resource["broker_id"]),
        "name": str(resource.get("broker_name") or "[[Dukascopy]]"),
        "description": str(resource.get("broker_description") or "Dukascopy"),
        "timezone": str(resource.get("broker_timezone") or "EETUS"),
        "postfix": str(resource.get("broker_postfix") or "_dukascopy"),
        "mtUse": "true",
        "spUse": "false",
    })
    instruments = ET.SubElement(resources, "Instruments")
    ET.SubElement(instruments, "InstrumentInfo", instrument_attrs)
    ET.SubElement(resources, "Sessions")
    ET.SubElement(resources, "CustomIndicators")
    ET.SubElement(resources, "CustomBlocks")
    after_resources = compact_retest1_resources_summary(root)
    actions.append({
        "field": "Resources",
        "from": before_resources,
        "to": after_resources,
        "changed": before_resources != after_resources,
    })
    return actions


def enforce_retest1_data_resources_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    period = generator_period(RETEST1_PERIOD_KEY)
    setup = root.find(".//Data/Setups/Setup")
    if setup is None:
        return ["Data/Setup missing"]
    if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
        issues.append("RETEST 1 dates are not protected RETEST_1_C1")
    if setup.get("testPrecision") != RETEST1_DATA_TEST_PRECISION:
        issues.append("RETEST 1 testPrecision is not simulated/tick code 2")
    charts = setup.findall("Chart")
    if len(charts) != 1:
        issues.append(f"RETEST 1 must have exactly one Chart, found {len(charts)}")
    elif charts[0].get("symbol") != f"{RETEST1_PLACEHOLDER_ASSET}_dukascopy":
        issues.append(f"RETEST 1 placeholder chart must be {RETEST1_PLACEHOLDER_ASSET}_dukascopy")
    for chart in root.findall(".//Setup/Chart"):
        if chart.get("symbol") != f"{RETEST1_PLACEHOLDER_ASSET}_dukascopy":
            issues.append(f"Stale RETEST 1 setup chart remains: {chart.get('symbol')}")
    if root.findall(".//Data/OutOfSample/Range"):
        issues.append("RETEST 1 OOS2-only setup should not carry nested OutOfSample ranges")

    resources = root.find(".//Resources")
    if resources is None:
        issues.append("Resources missing")
        return issues
    symbols = resources.findall("./Symbols/Symbol")
    if len(symbols) != 1:
        issues.append(f"RETEST 1 resources must have exactly one Symbol, found {len(symbols)}")
    else:
        symbol = symbols[0]
        if symbol.get("name") != f"{RETEST1_PLACEHOLDER_ASSET}_dukascopy":
            issues.append("RETEST 1 resource symbol is not Dukascopy placeholder")
        if symbol.get("source") != RETEST1_EXPECTED_SOURCE_ID:
            issues.append("RETEST 1 resource source is not Dukascopy source 2")
        if symbol.get("broker") != RETEST1_EXPECTED_BROKER_ID:
            issues.append("RETEST 1 resource broker is not Dukascopy broker 3")
        info = symbol.find("InstrumentInfo")
        if info is None or info.get("broker") != RETEST1_EXPECTED_BROKER_ID:
            issues.append("RETEST 1 nested InstrumentInfo is not broker 3")
    brokers = resources.findall("./Brokers/Broker")
    if [broker.get("id") for broker in brokers] != [RETEST1_EXPECTED_BROKER_ID]:
        issues.append("RETEST 1 Resources/Brokers must contain only broker 3")
    if resources.findall("./Sessions/Session"):
        issues.append("RETEST 1 resources should not keep session entries")
    if resources.findall("./CustomBlocks/*"):
        issues.append("RETEST 1 resources should not keep embedded CustomBlocks")
    data = find_section(root, "Data")
    text = (serialize_xml(data) if data is not None else "") + serialize_xml(resources)
    for token in RETEST1_BANNED_RESOURCE_TOKENS:
        if token in text:
            issues.append(f"Forbidden RETEST 1 donor/base token leaked: {token}")
    if re.search(r"[A-Za-z]:\\", text):
        issues.append("Local absolute path leaked into RETEST 1 XML")
    return issues


def update_retest1_data_resources_target_in_cfx(
    cfx: Path,
    backup_root: Path,
    apply: bool,
    root142: Path,
) -> dict[str, Any]:
    resource = retest1_oos2_target_resource(root142)
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
        "resourceSource": resource.get("source", ""),
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, RETEST1_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "retest1_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["beforeData"] = first_setup_summary(root)
    payload["beforeResources"] = compact_retest1_resources_summary(root)
    payload["actions"] = apply_retest1_data_resources_to_root(root, resource)
    payload["afterData"] = first_setup_summary(root)
    payload["afterResources"] = compact_retest1_resources_summary(root)
    issues = enforce_retest1_data_resources_guard(root)
    after_text = serialize_xml(root)
    payload["issues"] = issues
    payload["guardOk"] = not issues
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["changed"] = before_text != after_text
    payload["targetValues"] = {
        "role": "passive_clone_of_RETEST0_with_protected_OOS2_cross_broker_override",
        "periodKey": RETEST1_PERIOD_KEY,
        "dateFrom": generator_period(RETEST1_PERIOD_KEY)[0],
        "dateTo": generator_period(RETEST1_PERIOD_KEY)[1],
        "symbol": resource["symbol"],
        "timeframe": RETEST1_PLACEHOLDER_TIMEFRAME,
        "spread": resource["spread"],
        "source": RETEST1_EXPECTED_SOURCE_ID,
        "broker": RETEST1_EXPECTED_BROKER_ID,
        "testPrecision": RETEST1_DATA_TEST_PRECISION,
        "outOfSampleRanges": [],
        "customBlocks": 0,
    }
    payload["targetRationale"] = {
        "methodology": "RETEST 1 is the protected OOS2/cross-broker Dukascopy validation fed by RETEST 0.",
        "passiveClone": "Data/Resources receive the protected override; retest generation/improvement choices are handled in later tabs.",
        "generatorOwned": "Project Generator rewrites this same broker/period for the selected asset while preserving the cross-broker rule.",
        "noDonorCopy": "Mining15 resources are not copied literally; target is resolved from generator governance and local SQX data.db when available.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_retest1_data_resources_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase4_retest1_data_resources_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_retest1_data_resources_target_in_cfx(path, backup_root / name, apply=apply, root142=root142)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase4",
        "operation": "retest1_data_resources_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase4_retest1_data_resources_diff_review" if not apply else "phase4_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase4_retest1_data_resources_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def set_param_text(root: ET.Element, key: str, value: str, actions: list[dict[str, Any]], field_prefix: str) -> None:
    nodes = root.findall(f".//BuildTradingOptions/Params/Param[@key='{key}']")
    if not nodes:
        actions.append({"field": f"{field_prefix}:Param:{key}", "from": None, "to": value, "changed": False, "error": "missing_param"})
        return
    for index, node in enumerate(nodes, start=1):
        before = node.text or ""
        node.text = value
        actions.append({
            "field": f"{field_prefix}:Param:{key}#{index}",
            "from": before,
            "to": value,
            "changed": before != value,
        })


def set_or_create_text_child(parent: ET.Element, tag: str, value: str, actions: list[dict[str, Any]], field: str) -> ET.Element:
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag)
        before = None
    else:
        before = (child.text or "")
    child.text = value
    actions.append({"field": field, "from": before, "to": value, "changed": before != value})
    return child


def set_or_create_attrs_child(parent: ET.Element, tag: str, attrs: dict[str, str], actions: list[dict[str, Any]], field: str) -> ET.Element:
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag)
        before = None
    else:
        before = dict(child.attrib)
    child.attrib.clear()
    child.attrib.update(attrs)
    actions.append({"field": field, "from": before, "to": dict(child.attrib), "changed": before != dict(child.attrib)})
    return child


def ranking_conditions_exact(parent: ET.Element | None) -> list[dict[str, str]]:
    items = summarize_conditions(parent)
    return [
        {
            "column": item.get("column", ""),
            "comparator": item.get("comparator", ""),
            "value": item.get("value", ""),
            "use": item.get("use", ""),
        }
        for item in items
    ]


def set_ranking_conditions(rankings: ET.Element, actions: list[dict[str, Any]]) -> None:
    conditions = rankings.find("Conditions")
    if conditions is None:
        conditions = ET.SubElement(rankings, "Conditions")
        before: list[dict[str, str]] = []
    else:
        before = ranking_conditions_exact(conditions)
        for child in list(conditions):
            conditions.remove(child)
    conditions.text = "\n      "
    for index, target in enumerate(RETEST1_RANKING_CONDITIONS_TARGET):
        condition = make_column_condition(
            column=target["column"],
            comparator=target["comparator"],
            value=target["value"],
            fmt=target["format"],
        )
        condition.tail = "\n    " if index == len(RETEST1_RANKING_CONDITIONS_TARGET) - 1 else "\n      "
        conditions.append(condition)
    after = ranking_conditions_exact(conditions)
    actions.append({
        "field": "Rankings/Conditions",
        "from": before,
        "to": after,
        "changed": before != after,
    })


def apply_retest1_options_databanks_rankings_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []

    for key, value in RETEST1_OPTIONS_PARAMS_TARGET.items():
        set_param_text(root, key, value, actions, "Options")

    databanks = find_section(root, "Databanks")
    if databanks is None:
        databanks = ET.SubElement(root, "Databanks")
        actions.append({"field": "Databanks", "from": None, "to": "created", "changed": True})
    existing_by_name = {
        node.get("name", ""): node
        for node in databanks.findall("Databank")
        if node.get("name")
    }
    for name, wanted in RETEST1_DATABANKS_TARGET.items():
        node = existing_by_name.get(name)
        if node is None:
            node = ET.SubElement(databanks, "Databank", {"label": f"{name} databank", "name": name})
            before = None
        else:
            before = dict(node.attrib)
        node.set("name", name)
        node.set("value", wanted)
        if name == "Input":
            node.set("label", "Input databank")
        if name == "Output":
            node.set("label", "Output databank")
        actions.append({
            "field": f"Databanks/{name}",
            "from": before,
            "to": dict(node.attrib),
            "changed": before != dict(node.attrib),
        })

    rankings = find_section(root, "Rankings")
    if rankings is None:
        rankings = ET.SubElement(root, "Rankings", {"type": "never"})
        actions.append({"field": "Rankings", "from": None, "to": dict(rankings.attrib), "changed": True})
    before_rank_attrs = dict(rankings.attrib)
    rankings.set("type", "never")
    actions.append({
        "field": "Rankings:type",
        "from": before_rank_attrs,
        "to": dict(rankings.attrib),
        "changed": before_rank_attrs != dict(rankings.attrib),
    })
    set_or_create_text_child(rankings, "MaxStrategies", RETEST1_RANKING_TARGET["MaxStrategies"], actions, "Rankings/MaxStrategies")
    set_or_create_attrs_child(
        rankings,
        "FitnessCriteria",
        {"method": "ComputeFromStrategyResult", "useFitnessByIndex": "false"},
        actions,
        "Rankings/FitnessCriteria",
    )
    set_or_create_text_child(rankings, "ConditionsType", RETEST1_RANKING_TARGET["ConditionsType"], actions, "Rankings/ConditionsType")
    set_or_create_text_child(rankings, "DeleteFailedStrategies", RETEST1_RANKING_TARGET["DeleteFailedStrategies"], actions, "Rankings/DeleteFailedStrategies")
    set_or_create_text_child(rankings, "ForceRunCrossChecks", RETEST1_RANKING_TARGET["ForceRunCrossChecks"], actions, "Rankings/ForceRunCrossChecks")
    set_or_create_attrs_child(rankings, "AutomaticDismissal", RETEST1_RANKING_TARGET["AutomaticDismissal"], actions, "Rankings/AutomaticDismissal")
    set_or_create_attrs_child(rankings, "StopCondition", RETEST1_RANKING_TARGET["StopCondition"], actions, "Rankings/StopCondition")
    set_or_create_attrs_child(rankings, "FitPortfolio", RETEST1_RANKING_TARGET["FitPortfolio"], actions, "Rankings/FitPortfolio")
    set_or_create_attrs_child(rankings, "CustomAnalysis", RETEST1_RANKING_TARGET["CustomAnalysis"], actions, "Rankings/CustomAnalysis")
    set_ranking_conditions(rankings, actions)
    return actions


def retest1_options_databanks_rankings_summary(root: ET.Element) -> dict[str, Any]:
    params = {
        param.get("key", ""): (param.text or "")
        for param in root.findall(".//BuildTradingOptions/Params/Param")
        if param.get("key") in RETEST1_OPTIONS_PARAMS_TARGET
    }
    databanks = {
        node.get("name", ""): node.get("value", "")
        for node in root.findall(".//Databanks/Databank")
        if node.get("name")
    }
    rankings = find_section(root, "Rankings")
    ranking_data: dict[str, Any] = {}
    if rankings is not None:
        ranking_data = {
            "type": rankings.get("type", ""),
            "MaxStrategies": (rankings.findtext("MaxStrategies") or ""),
            "ConditionsType": (rankings.findtext("ConditionsType") or ""),
            "DeleteFailedStrategies": (rankings.findtext("DeleteFailedStrategies") or ""),
            "ForceRunCrossChecks": (rankings.findtext("ForceRunCrossChecks") or ""),
            "FitPortfolio": dict(rankings.find("FitPortfolio").attrib) if rankings.find("FitPortfolio") is not None else {},
            "StopCondition": dict(rankings.find("StopCondition").attrib) if rankings.find("StopCondition") is not None else {},
            "conditions": ranking_conditions_exact(rankings.find("Conditions")),
        }
    return {"optionsParams": params, "databanks": databanks, "rankings": ranking_data}


def enforce_retest1_options_databanks_rankings_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = retest1_options_databanks_rankings_summary(root)
    params = summary.get("optionsParams") or {}
    for key, wanted in RETEST1_OPTIONS_PARAMS_TARGET.items():
        if params.get(key) != wanted:
            issues.append(f"Options param {key} is {params.get(key)!r}, expected {wanted!r}")
    databanks = summary.get("databanks") or {}
    for key, wanted in RETEST1_DATABANKS_TARGET.items():
        if databanks.get(key) != wanted:
            issues.append(f"Databank {key} is {databanks.get(key)!r}, expected {wanted!r}")
    ranking = summary.get("rankings") or {}
    if ranking.get("DeleteFailedStrategies") != "false":
        issues.append("RETEST 1 must keep failed strategies visible for advisory review")
    if (ranking.get("FitPortfolio") or {}).get("active") != "false":
        issues.append("RETEST 1 must not run portfolio fit selection in Capa1")
    expected_conditions = [
        {"column": item["column"], "comparator": item["comparator"], "value": item["value"], "use": "true"}
        for item in RETEST1_RANKING_CONDITIONS_TARGET
    ]
    if ranking.get("conditions") != expected_conditions:
        issues.append("RETEST 1 ranking conditions do not match tolerant advisory target")
    options_node = find_section(root, "Options")
    databanks_node = find_section(root, "Databanks")
    rankings_node = find_section(root, "Rankings")
    text = (
        serialize_xml(options_node if options_node is not None else root)
        + serialize_xml(databanks_node if databanks_node is not None else root)
        + serialize_xml(rankings_node if rankings_node is not None else root)
    )
    for token in ("USDJPY", "USDJPY_darwinex", "USDJPY_dukascopy"):
        if token in text:
            issues.append(f"Forbidden donor token leaked into Options/Databanks/Rankings: {token}")
    if re.search(r"[A-Za-z]:\\", text):
        issues.append("Local absolute path leaked into Options/Databanks/Rankings")
    return issues


def update_retest1_options_databanks_rankings_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, RETEST1_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "retest1_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = retest1_options_databanks_rankings_summary(root)
    payload["actions"] = apply_retest1_options_databanks_rankings_to_root(root)
    payload["after"] = retest1_options_databanks_rankings_summary(root)
    payload["issues"] = enforce_retest1_options_databanks_rankings_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "options": RETEST1_OPTIONS_PARAMS_TARGET,
        "databanks": RETEST1_DATABANKS_TARGET,
        "rankings": RETEST1_RANKING_TARGET,
        "conditions": RETEST1_RANKING_CONDITIONS_TARGET,
    }
    payload["targetRationale"] = {
        "advisoryNotColadero": "Keep failed rows visible with DeleteFailedStrategies=false, but retain explicit minimum conditions so Result can be failed naturally.",
        "passiveRetest": "Disable FitPortfolio because Capa1 RETEST 1 should validate OOS2/cross-broker behavior, not perform portfolio selection.",
        "realism": "Enable RealisticGapsHandling to avoid a softer cross-broker OOS2 pass than RETEST 0.",
        "generatorOwned": "Time window remains the H1 placeholder in base; Project Generator rewrites it by selected timeframe.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_retest1_options_databanks_rankings_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase4_retest1_options_databanks_rankings_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_retest1_options_databanks_rankings_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase4",
        "operation": "retest1_options_databanks_rankings_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase4_retest1_options_databanks_rankings_diff_review" if not apply else "phase4_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase4_retest1_options_databanks_rankings_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def set_or_update_attrs_child(parent: ET.Element, tag: str, attrs: dict[str, str], actions: list[dict[str, Any]], field: str) -> ET.Element:
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag)
        before = None
    else:
        before = dict(child.attrib)
    for key, value in attrs.items():
        child.set(key, value)
    after = dict(child.attrib)
    actions.append({"field": field, "from": before, "to": after, "changed": before != after})
    return child


def set_improvement_group_passive(parts: ET.Element, group_name: str, actions: list[dict[str, Any]]) -> None:
    group = parts.find(group_name)
    if group is None:
        group = ET.SubElement(parts, group_name)
        actions.append({"field": f"PartsToImprove/{group_name}", "from": None, "to": "created", "changed": True})
    before_group = dict(group.attrib)
    if group_name in {"EntryRules", "ExitRules"}:
        group.set("symmetry", "false")
    actions.append({
        "field": f"PartsToImprove/{group_name}:attrs",
        "from": before_group,
        "to": dict(group.attrib),
        "changed": before_group != dict(group.attrib),
    })
    for side in ("LongImprovement", "ShortImprovement"):
        node = group.find(side)
        if node is None:
            node = ET.SubElement(group, side)
            before = None
        else:
            before = dict(node.attrib)
        node.set("use", "false")
        if "action" in node.attrib or group_name in {"EntryRules", "ExitRules"}:
            node.set("action", "replace")
        actions.append({
            "field": f"PartsToImprove/{group_name}/{side}",
            "from": before,
            "to": dict(node.attrib),
            "changed": before != dict(node.attrib),
        })


def apply_retest1_parts_to_improve_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    parts = find_section(root, "PartsToImprove")
    if parts is None:
        parts = ET.SubElement(root, "PartsToImprove")
        actions.append({"field": "PartsToImprove", "from": None, "to": "created", "changed": True})
    before_attrs = dict(parts.attrib)
    parts.set("improveATM", "false")
    actions.append({
        "field": "PartsToImprove:attrs",
        "from": before_attrs,
        "to": dict(parts.attrib),
        "changed": before_attrs != dict(parts.attrib),
    })
    for group_name in ("EntryRules", "OrderTypes", "ExitRules"):
        set_improvement_group_passive(parts, group_name, actions)


def apply_retest1_what_to_build_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    what_to_build = find_section(root, "WhatToBuild")
    if what_to_build is None:
        what_to_build = ET.SubElement(root, "WhatToBuild")
        actions.append({"field": "WhatToBuild", "from": None, "to": "created", "changed": True})

    set_or_create_attrs_child(
        what_to_build,
        "StrategyType",
        RETEST1_STRATEGY_TYPE_TARGET,
        actions,
        "WhatToBuild/StrategyType",
    )
    build_mode = what_to_build.find("BuildMode")
    if build_mode is None:
        build_mode = ET.SubElement(what_to_build, "BuildMode", {"generationType": "random-generation"})
        actions.append({"field": "WhatToBuild/BuildMode", "from": None, "to": dict(build_mode.attrib), "changed": True})
    else:
        actions.append({
            "field": "WhatToBuild/BuildMode:generationType",
            "from": build_mode.get("generationType", ""),
            "to": build_mode.get("generationType", ""),
            "changed": False,
            "note": "left as SQX-known placeholder; passive behavior is enforced by databanks, no-improve parts and disabled evolution toggles",
        })
    for tag, value in RETEST1_PASSIVE_BUILDMODE_TEXT_TARGET.items():
        set_or_create_text_child(build_mode, tag, value, actions, f"WhatToBuild/BuildMode/{tag}")
    for tag, attrs in RETEST1_PASSIVE_BUILDMODE_ATTR_TARGET.items():
        set_or_update_attrs_child(build_mode, tag, attrs, actions, f"WhatToBuild/BuildMode/{tag}")


def apply_retest1_blocks_to_root(root: ET.Element, source_root: ET.Element | None, actions: list[dict[str, Any]]) -> None:
    blocks = find_blocks(root)
    if blocks is None:
        blocks = ET.SubElement(root, "Blocks", {"type": "simple", "version": "142.2336"})
        actions.append({"field": "Blocks", "from": None, "to": dict(blocks.attrib), "changed": True})

    before_attrs = dict(blocks.attrib)
    blocks.set("type", "simple")
    blocks.set("version", "142.2336")
    actions.append({
        "field": "Blocks:attrs",
        "from": before_attrs,
        "to": dict(blocks.attrib),
        "changed": before_attrs != dict(blocks.attrib),
    })

    source_blocks = find_blocks(source_root)
    if source_blocks is not None:
        actions.append(replace_building_blocks_from_source(blocks, source_blocks))
    else:
        actions.append({"field": "BuildingBlocks", "error": "retest0_source_missing", "changed": False})
    enforce_order_types(blocks, actions)
    enforce_exit_types(blocks, actions)
    enforce_external_custom_data(blocks, actions)
    enforce_disabled_build_block_categories(blocks, actions)


def apply_retest1_passive_generation_to_root(root: ET.Element, source_root: ET.Element | None) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    apply_retest1_parts_to_improve_to_root(root, actions)
    apply_retest1_what_to_build_to_root(root, actions)
    apply_retest1_blocks_to_root(root, source_root, actions)
    return actions


def retest1_passive_generation_summary(root: ET.Element) -> dict[str, Any]:
    parts = find_section(root, "PartsToImprove")
    what_to_build = find_section(root, "WhatToBuild")
    blocks = find_blocks(root)
    strategy_type = what_to_build.find("StrategyType") if what_to_build is not None else None
    build_mode = what_to_build.find("BuildMode") if what_to_build is not None else None
    parts_summary: dict[str, Any] = {}
    if parts is not None:
        for group_name in ("EntryRules", "OrderTypes", "ExitRules"):
            group = parts.find(group_name)
            if group is None:
                parts_summary[group_name] = None
                continue
            parts_summary[group_name] = {
                "attrs": dict(group.attrib),
                "LongImprovement": dict(group.find("LongImprovement").attrib) if group.find("LongImprovement") is not None else {},
                "ShortImprovement": dict(group.find("ShortImprovement").attrib) if group.find("ShortImprovement") is not None else {},
            }
    order_types: dict[str, str] = {}
    exit_types: dict[str, dict[str, str]] = {}
    custom_data: dict[str, Any] = {}
    active_keys = active_building_block_keys(blocks)
    active_building_blocks = []
    if blocks is not None:
        active_building_blocks = [
            block for block in blocks.findall(".//BuildingBlocks/Block")
            if str(block.get("use", "")).lower() == "true"
            and block.get("key") not in {"#Left#", "#Right#"}
        ]
        order_types = {block.get("key", ""): block.get("use", "") for block in blocks.findall("./OrderTypes/Block") if block.get("key")}
        exit_types = {
            block.get("key", ""): {"use": block.get("use", ""), "probability": block.get("probability", "")}
            for block in blocks.findall("./ExitTypes/Block")
            if block.get("key")
        }
        custom = blocks.find("CustomData")
        custom_data = {
            "attrs": dict(custom.attrib) if custom is not None else {},
            "children": len(list(custom)) if custom is not None else 0,
        }
    return {
        "partsToImprove": parts_summary,
        "strategyType": dict(strategy_type.attrib) if strategy_type is not None else {},
        "buildMode": {
            "attrs": dict(build_mode.attrib) if build_mode is not None else {},
            "text": {
                child.tag: (child.text or "")
                for child in list(build_mode) if build_mode is not None and isinstance(child.tag, str) and child.text is not None
            } if build_mode is not None else {},
            "childAttrs": {
                child.tag: dict(child.attrib)
                for child in list(build_mode) if build_mode is not None and isinstance(child.tag, str) and child.attrib
            } if build_mode is not None else {},
        },
        "blocks": {
            "attrs": dict(blocks.attrib) if blocks is not None else {},
            "orderTypes": order_types,
            "exitTypes": exit_types,
            "activeBlockCount": len(active_keys),
            "activeIndicatorCount": len(indicator_family_keys(active_keys)),
            "activeSignalCount": len([block for block in active_building_blocks if block.get("category") == "signals"]),
            "activeStopLimitCount": len([block for block in active_building_blocks if block.get("category") == "stopLimitBlocks"]),
            "customData": custom_data,
        },
    }


def enforce_retest1_passive_generation_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = retest1_passive_generation_summary(root)
    parts = summary.get("partsToImprove") or {}
    for group_name in ("EntryRules", "OrderTypes", "ExitRules"):
        group = parts.get(group_name) or {}
        for side in ("LongImprovement", "ShortImprovement"):
            if (group.get(side) or {}).get("use") != "false":
                issues.append(f"RETEST 1 {group_name}/{side} must be passive use=false")
    if summary.get("strategyType") != RETEST1_STRATEGY_TYPE_TARGET:
        issues.append("RETEST 1 StrategyType does not point passively to RETEST 0 with known SQX attributes")
    build_mode = summary.get("buildMode") or {}
    build_text = build_mode.get("text") or {}
    for tag, value in RETEST1_PASSIVE_BUILDMODE_TEXT_TARGET.items():
        if build_text.get(tag) != value:
            issues.append(f"RETEST 1 BuildMode {tag} is {build_text.get(tag)!r}, expected {value!r}")
    child_attrs = build_mode.get("childAttrs") or {}
    for tag, attrs in RETEST1_PASSIVE_BUILDMODE_ATTR_TARGET.items():
        current = child_attrs.get(tag) or {}
        for key, value in attrs.items():
            if current.get(key) != value:
                issues.append(f"RETEST 1 BuildMode {tag}.{key} is {current.get(key)!r}, expected {value!r}")
    blocks = summary.get("blocks") or {}
    expected_order = BUILD_ORDER_TYPE_TARGET
    actual_order = {key: blocks.get("orderTypes", {}).get(key) for key in expected_order}
    if actual_order != expected_order:
        issues.append(f"RETEST 1 order types are {actual_order!r}, expected {expected_order!r}")
    exits = blocks.get("exitTypes") or {}
    if exits.get(BUILD_EXIT_TYPE_ACTIVE_KEY, {}).get("use") != "true":
        issues.append("RETEST 1 must keep only ExitAfterBars active")
    if exits.get(BUILD_EXIT_TYPE_ACTIVE_KEY, {}).get("probability") != "100":
        issues.append("RETEST 1 ExitAfterBars probability must be 100")
    active_other_exits = [
        key for key, data in exits.items()
        if key != BUILD_EXIT_TYPE_ACTIVE_KEY and (data or {}).get("use") == "true"
    ]
    if active_other_exits:
        issues.append(f"RETEST 1 has non-passive active exit types: {active_other_exits}")
    if any(any(token in key for token in BUILD_EXIT_TYPE_BANNED_TOKENS) for key in exits):
        issues.append("RETEST 1 contains day-based exit types")
    if int(blocks.get("activeSignalCount") or 0) != 0:
        issues.append("RETEST 1 signals must remain disabled in passive retest")
    if int(blocks.get("activeStopLimitCount") or 0) != 0:
        issues.append("RETEST 1 stop/limit entry blocks must remain disabled in passive retest")
    if int(blocks.get("activeIndicatorCount") or 0) <= 0:
        issues.append("RETEST 1 must preserve methodology/BlockSettings indicator blocks")
    custom = blocks.get("customData") or {}
    if (custom.get("attrs") or {}).get("showAll") != "false" or custom.get("children") != 0:
        issues.append("RETEST 1 external CustomData must stay disabled and empty")
    guarded_sections = [
        find_section(root, "PartsToImprove"),
        find_section(root, "WhatToBuild"),
        find_section(root, "Blocks"),
    ]
    guarded_text = "".join(serialize_xml(section if section is not None else root) for section in guarded_sections)
    for token in ("ExitAfterDays", "ExitAfterTradingDays", "USDJPY_darwinex", "USDJPY_dukascopy"):
        if token in guarded_text:
            issues.append(f"Forbidden token leaked into RETEST 1 passive generation tabs: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into RETEST 1 passive generation tabs")
    return issues


def update_retest1_passive_generation_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, RETEST1_TASK_TITLE)
    source_task_xml_name, source_root = load_task_root(cfx, RETEST1_PASSIVE_SOURCE_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    payload["sourceTaskXml"] = source_task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "retest1_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload
    if not source_task_xml_name or source_root is None:
        payload["error"] = "retest0_source_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = retest1_passive_generation_summary(root)
    payload["actions"] = apply_retest1_passive_generation_to_root(root, source_root)
    payload["after"] = retest1_passive_generation_summary(root)
    payload["issues"] = enforce_retest1_passive_generation_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "strategyType": RETEST1_STRATEGY_TYPE_TARGET,
        "buildModeText": RETEST1_PASSIVE_BUILDMODE_TEXT_TARGET,
        "buildModeAttributes": RETEST1_PASSIVE_BUILDMODE_ATTR_TARGET,
        "sourceTask": RETEST1_PASSIVE_SOURCE_TASK_TITLE,
        "orderTypes": BUILD_ORDER_TYPE_TARGET,
        "exitType": BUILD_EXIT_TYPE_ACTIVE_KEY,
        "disabledCategories": BUILD_BLOCK_CATEGORY_DISABLE_TARGET,
    }
    payload["targetRationale"] = {
        "passiveRetest": "RETEST 1 consumes RETEST 0 candidates and must not improve or generate strategies.",
        "noUnknownEnum": "BuildMode.generationType is left as an SQX-known placeholder because no local CFX uses a safe none/passive enum.",
        "blocksSource": "BuildingBlocks are normalized from the already approved RETEST 0 base contract, not from Mining15 donor blocks.",
        "methodology": "Signals and Stop/Limit blocks stay off; indicators remain governed by methodology/BlockSettings; only EnterAtMarket plus ExitAfterBars is allowed.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_retest1_passive_generation_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase4_retest1_passive_generation_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_retest1_passive_generation_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase4",
        "operation": "retest1_passive_generation_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase4_retest1_passive_generation_diff_review" if not apply else "phase4_continue_static_tabs",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase4_retest1_passive_generation_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def apply_retest1_crosschecks_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    parent = find_section(root, "CrossChecks")
    if parent is None:
        parent = ET.SubElement(root, "CrossChecks")
        actions.append({"field": "CrossChecks", "from": None, "to": "created", "changed": True})
    before_attrs = dict(parent.attrib)
    for key, value in RETEST1_CROSSCHECKS_TARGET.items():
        parent.set(key, value)
    actions.append({
        "field": "CrossChecks:attrs",
        "from": before_attrs,
        "to": dict(parent.attrib),
        "changed": before_attrs != dict(parent.attrib),
    })
    for check in list(parent):
        if not isinstance(check.tag, str) or check.get("use") is None:
            continue
        before = check.get("use", "")
        check.set("use", "false")
        actions.append({
            "field": f"CrossChecks/{check.tag}:use",
            "from": before,
            "to": "false",
            "changed": before != "false",
        })
        for method in check.findall("./Settings/Methods/Method"):
            method_type = method.get("type", "")
            method_before = method.get("use", "")
            method.set("use", "false")
            actions.append({
                "field": f"CrossChecks/{check.tag}/Method:{method_type}:use",
                "from": method_before,
                "to": "false",
                "changed": method_before != "false",
            })


def apply_retest1_risk_money_management_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    rmm = find_section(root, "RiskMoneyManagement")
    if rmm is None:
        rmm = ET.SubElement(root, "RiskMoneyManagement", {"customSettings": "false"})
        actions.append({"field": "RiskMoneyManagement", "from": None, "to": dict(rmm.attrib), "changed": True})
    money = rmm.find("MoneyManagement")
    if money is None:
        money = ET.SubElement(rmm, "MoneyManagement")
        actions.append({"field": "RiskMoneyManagement/MoneyManagement", "from": None, "to": "created", "changed": True})

    existing = {method.get("type", ""): method for method in money.findall("Method") if method.get("type")}
    for method_type, wanted in RETEST1_RISK_MONEY_MANAGEMENT_METHOD_TARGET.items():
        method = existing.get(method_type)
        if method is None:
            method = ET.SubElement(money, "Method", {"type": method_type})
            before = None
        else:
            before = dict(method.attrib)
        method.set("type", method_type)
        method.set("use", wanted)
        actions.append({
            "field": f"RiskMoneyManagement/Method:{method_type}",
            "from": before,
            "to": dict(method.attrib),
            "changed": before != dict(method.attrib),
        })


def retest1_static_crosschecks_summary(root: ET.Element) -> dict[str, Any]:
    crosschecks = find_section(root, "CrossChecks")
    direct_checks: list[dict[str, Any]] = []
    if crosschecks is not None:
        for check in list(crosschecks):
            if not isinstance(check.tag, str) or check.get("use") is None:
                continue
            active_methods = [
                method.get("type", "")
                for method in check.findall("./Settings/Methods/Method")
                if method.get("use") == "true"
            ]
            direct_checks.append({
                "id": check.tag,
                "use": check.get("use", ""),
                "configuredMethodCount": len(active_methods),
                "activeMethodCount": len(active_methods) if check.get("use") == "true" else 0,
                "configuredMethods": active_methods,
                "activeMethods": active_methods if check.get("use") == "true" else [],
            })

    rmm = find_section(root, "RiskMoneyManagement")
    money_methods = {
        method.get("type", ""): method.get("use", "")
        for method in (rmm.findall(".//MoneyManagement/Method") if rmm is not None else [])
        if method.get("type")
    }
    atms = find_section(root, "ATMs")
    notes = find_section(root, "Notes")
    selected = find_section(root, "SelectedStrategies")
    return {
        "crossChecks": {
            "exists": crosschecks is not None,
            "attrs": dict(crosschecks.attrib) if crosschecks is not None else {},
            "active": [item["id"] for item in direct_checks if item["use"] == "true"],
            "checks": direct_checks,
            "sha256": section_sha256(root, "CrossChecks"),
        },
        "riskMoneyManagement": {
            "exists": rmm is not None,
            "methods": money_methods,
            "sha256": section_sha256(root, "RiskMoneyManagement"),
        },
        "atms": {
            "exists": atms is not None,
            "attrs": dict(atms.attrib) if atms is not None else {},
            "sha256": section_sha256(root, "ATMs"),
        },
        "notes": {
            "exists": notes is not None,
            "sha256": section_sha256(root, "Notes"),
        },
        "selectedStrategies": {
            "exists": selected is not None,
            "children": len(list(selected)) if selected is not None else 0,
            "text": (selected.text or "").strip() if selected is not None else "",
            "sha256": section_sha256(root, "SelectedStrategies"),
        },
    }


def enforce_retest1_static_crosschecks_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = retest1_static_crosschecks_summary(root)
    crosschecks = summary.get("crossChecks") or {}
    if not crosschecks.get("exists"):
        issues.append("RETEST 1 CrossChecks section missing")
    if crosschecks.get("attrs") != RETEST1_CROSSCHECKS_TARGET:
        issues.append(f"RETEST 1 CrossChecks attrs are {crosschecks.get('attrs')!r}, expected {RETEST1_CROSSCHECKS_TARGET!r}")
    if crosschecks.get("active"):
        issues.append(f"RETEST 1 must not have active internal crosschecks: {crosschecks.get('active')}")
    configured_methods = [
        f"{item.get('id')}:{method}"
        for item in (crosschecks.get("checks") or [])
        for method in (item.get("configuredMethods") or [])
    ]
    if configured_methods:
        issues.append(f"RETEST 1 CrossChecks must not keep enabled Settings/Methods: {configured_methods}")

    rmm = summary.get("riskMoneyManagement") or {}
    methods = rmm.get("methods") or {}
    for method_type, wanted in RETEST1_RISK_MONEY_MANAGEMENT_METHOD_TARGET.items():
        if methods.get(method_type) != wanted:
            issues.append(f"RETEST 1 RiskMoneyManagement {method_type} is {methods.get(method_type)!r}, expected {wanted!r}")

    atms = summary.get("atms") or {}
    for key, wanted in RETEST1_ATMS_TARGET.items():
        if (atms.get("attrs") or {}).get(key) != wanted:
            issues.append(f"RETEST 1 ATMs {key} is {(atms.get('attrs') or {}).get(key)!r}, expected {wanted!r}")

    selected = summary.get("selectedStrategies") or {}
    if selected.get("children") != 0 or selected.get("text"):
        issues.append("RETEST 1 SelectedStrategies must remain empty in the base template")

    rankings = find_section(root, "Rankings")
    if rankings is not None and (rankings.findtext("ForceRunCrossChecks") or "") != "false":
        issues.append("RETEST 1 Rankings/ForceRunCrossChecks must remain false")

    for issue in enforce_retest1_passive_generation_guard(root):
        issues.append(f"Passive generation guard: {issue}")
    return issues


def apply_retest1_static_crosschecks_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    apply_retest1_crosschecks_to_root(root, actions)
    apply_retest1_risk_money_management_to_root(root, actions)
    return actions


def update_retest1_static_crosschecks_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, RETEST1_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "retest1_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = retest1_static_crosschecks_summary(root)
    payload["actions"] = apply_retest1_static_crosschecks_to_root(root)
    payload["after"] = retest1_static_crosschecks_summary(root)
    payload["issues"] = enforce_retest1_static_crosschecks_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "crossChecks": RETEST1_CROSSCHECKS_TARGET,
        "riskMoneyManagementMethods": RETEST1_RISK_MONEY_MANAGEMENT_METHOD_TARGET,
        "staticTabs": RETEST1_STATIC_TABS,
    }
    payload["targetRationale"] = {
        "passiveRetest": "RETEST 1 must remain a pure OOS2 validation task with no internal crosschecks or generation/improvement remnants.",
        "riskMoneyManagement": "Use FixedSize like RETEST 0 and the other Capa1 retests so validation compares strategy behavior without position-sizing noise.",
        "staticTabs": "ATMs, Notes and SelectedStrategies are audited and kept as current values.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_retest1_static_crosschecks_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase4_retest1_static_crosschecks_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_retest1_static_crosschecks_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase4",
        "operation": "retest1_static_crosschecks_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase4_retest1_static_crosschecks_diff_review" if not apply else "phase4_retest1_closeout",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase4_retest1_static_crosschecks_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def _asset_from_tick_real_symbol(symbol: str) -> str:
    return (symbol or "").split("_", 1)[0] or "AUDCAD"


def ensure_resources_container(resources: ET.Element, tag: str) -> ET.Element:
    node = resources.find(tag)
    if node is None:
        node = ET.SubElement(resources, tag)
    return node


def _first_existing_symbol_template(resources: ET.Element) -> tuple[dict[str, str], dict[str, str]]:
    symbol = resources.find("./Symbols/Symbol")
    if symbol is None:
        return {}, {}
    info = symbol.find("InstrumentInfo")
    return dict(symbol.attrib), dict(info.attrib) if info is not None else {}


def _tick_real_resource_summary(root: ET.Element) -> dict[str, Any]:
    summary = build_resources_summary(root)
    resources = root.find(".//Resources")
    summary.update({
        "customIndicators": len(resources.findall("./CustomIndicators/*")) if resources is not None else 0,
        "customBlocks": len(resources.findall("./CustomBlocks/*")) if resources is not None else 0,
        "childOrder": [child.tag for child in list(resources)] if resources is not None else [],
    })
    return summary


def tick_real_data_databanks_resources_summary(root: ET.Element) -> dict[str, Any]:
    databanks = {
        node.get("name", ""): node.get("value", "")
        for node in root.findall(".//Databanks/Databank")
        if node.get("name")
    }
    data = find_section(root, "Data")
    return {
        "data": {
            "setup": first_setup_summary(root),
            "outOfSampleRanges": [dict(node.attrib) for node in root.findall(".//Data/OutOfSample/Range")],
            "outOfSampleAttrs": dict(data.find("OutOfSample").attrib) if data is not None and data.find("OutOfSample") is not None else {},
        },
        "databanks": databanks,
        "resources": _tick_real_resource_summary(root),
    }


def apply_tick_real_data_databanks_resources_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    period = generator_period(TICK_REAL_PERIOD_KEY)
    data = find_section(root, "Data")
    setup = root.find(".//Data/Setups/Setup")
    if data is None or setup is None:
        actions.append({"field": "Data", "error": "missing_data_or_setup", "changed": False})
        return actions

    for key, wanted in {
        "dateFrom": period[0],
        "dateTo": period[1],
        "testPrecision": TICK_REAL_DATA_TEST_PRECISION,
        "session": TICK_REAL_DATA_SESSION,
    }.items():
        before = setup.get(key, "")
        setup.set(key, wanted)
        actions.append({"field": f"Data/Setup:{key}", "from": before, "to": wanted, "changed": before != wanted})

    out_of_sample = data.find("OutOfSample")
    if out_of_sample is None:
        out_of_sample = ET.SubElement(data, "OutOfSample", {"showGraph": "false"})
        before_oos_attrs: dict[str, str] | None = None
    else:
        before_oos_attrs = dict(out_of_sample.attrib)
        out_of_sample.set("showGraph", "false")
    removed_ranges = [dict(node.attrib) for node in out_of_sample.findall("Range")]
    for node in list(out_of_sample.findall("Range")):
        out_of_sample.remove(node)
    actions.append({
        "field": "Data/OutOfSample",
        "from": {"attrs": before_oos_attrs, "ranges": removed_ranges},
        "to": {"attrs": dict(out_of_sample.attrib), "ranges": []},
        "changed": before_oos_attrs != dict(out_of_sample.attrib) or bool(removed_ranges),
    })

    databanks = find_section(root, "Databanks")
    if databanks is None:
        databanks = ET.SubElement(root, "Databanks", {"retestSelected": "false"})
        actions.append({"field": "Databanks", "from": None, "to": dict(databanks.attrib), "changed": True})
    existing_by_name = {
        node.get("name", ""): node
        for node in databanks.findall("Databank")
        if node.get("name")
    }
    for name, wanted in TICK_REAL_DATABANKS_TARGET.items():
        node = existing_by_name.get(name)
        if node is None:
            node = ET.SubElement(databanks, "Databank", {"name": name})
            before = None
        else:
            before = dict(node.attrib)
        node.set("name", name)
        node.set("value", wanted)
        node.set("label", f"{name} databank")
        actions.append({
            "field": f"Databanks/{name}",
            "from": before,
            "to": dict(node.attrib),
            "changed": before != dict(node.attrib),
        })

    resources = find_section(root, "Resources")
    if resources is None:
        resources = ET.SubElement(root, "Resources")
        before_resources: dict[str, Any] = {"resourcesFound": False}
    else:
        before_resources = _tick_real_resource_summary(root)

    charts = setup.findall("Chart")
    if not charts:
        chart = ET.SubElement(setup, "Chart", {"symbol": "AUDCAD_darwinex", "timeframe": "H1", "spread": "2"})
        charts = [chart]
        actions.append({"field": "Data/Setup/Chart", "from": None, "to": dict(chart.attrib), "changed": True})
    chart_by_symbol = {
        chart.get("symbol", ""): chart
        for chart in charts
        if chart.get("symbol")
    }
    symbols_node = ensure_resources_container(resources, "Symbols")
    brokers_node = ensure_resources_container(resources, "Brokers")
    instruments_node = ensure_resources_container(resources, "Instruments")
    sessions_node = ensure_resources_container(resources, "Sessions")
    ensure_resources_container(resources, "CustomIndicators")
    ensure_resources_container(resources, "CustomBlocks")

    template_symbol_attrs, template_info_attrs = _first_existing_symbol_template(resources)
    existing_symbols = {
        symbol.get("name", ""): symbol
        for symbol in symbols_node.findall("Symbol")
        if symbol.get("name")
    }
    before_symbols = [value_for_node(symbol) for symbol in symbols_node.findall("Symbol")]
    for symbol in list(symbols_node.findall("Symbol")):
        symbols_node.remove(symbol)

    referenced_brokers: set[str] = set()
    date_from_default = str(epoch_ms_for_date(period[0]))
    date_to_default = str(epoch_ms_for_date(period[1]))
    for symbol_name, chart in chart_by_symbol.items():
        existing_symbol = existing_symbols.get(symbol_name)
        symbol_attrs = dict(existing_symbol.attrib) if existing_symbol is not None else dict(template_symbol_attrs)
        existing_info = existing_symbol.find("InstrumentInfo") if existing_symbol is not None else None
        info_attrs = dict(existing_info.attrib) if existing_info is not None else dict(template_info_attrs)
        broker_id = symbol_attrs.get("broker") or info_attrs.get("broker") or TICK_REAL_DEFAULT_BROKER_ID
        source_id = symbol_attrs.get("source") or TICK_REAL_DEFAULT_SOURCE_ID
        bounded_from, bounded_to = bounded_period_ms(
            period,
            symbol_attrs.get("dateFrom") or date_from_default,
            symbol_attrs.get("dateTo") or date_to_default,
        )
        asset = _asset_from_tick_real_symbol(symbol_name)
        referenced_brokers.add(broker_id)
        symbol_node = ET.SubElement(symbols_node, "Symbol", {
            "name": symbol_name,
            "source": source_id,
            "barType": symbol_attrs.get("barType", "1"),
            "precision": TICK_REAL_RESOURCE_PRECISION,
            "timezone": symbol_attrs.get("timezone") or TICK_REAL_RESOURCE_TIMEZONE,
            "dateFrom": bounded_from,
            "dateTo": bounded_to,
            "uSymbol": symbol_attrs.get("uSymbol") or asset,
            "uSymbolName": symbol_attrs.get("uSymbolName") or asset,
            "removeWeekends": symbol_attrs.get("removeWeekends", "false"),
            "broker": broker_id,
        })
        info_attrs.update({
            "instrument": symbol_name,
            "defaultSpread": chart.get("spread", info_attrs.get("defaultSpread", "")),
            "dateFrom": "0",
            "dateTo": "0",
            "rows": "0",
            "totalDays": "0",
            "dataType": info_attrs.get("dataType", BUILD_RESOURCES_BASE_DATA_TYPE),
            "broker": broker_id,
        })
        ET.SubElement(symbol_node, "InstrumentInfo", info_attrs)

    after_symbols = [value_for_node(symbol) for symbol in symbols_node.findall("Symbol")]
    actions.append({
        "field": "Resources/Symbols",
        "from": before_symbols,
        "to": after_symbols,
        "changed": before_symbols != after_symbols,
    })

    before_brokers = [value_for_node(broker) for broker in brokers_node.findall("Broker")]
    existing_brokers = {
        broker.get("id", ""): broker
        for broker in brokers_node.findall("Broker")
        if broker.get("id")
    }
    for broker in list(brokers_node.findall("Broker")):
        if broker.get("id") not in referenced_brokers:
            brokers_node.remove(broker)
    for broker_id in sorted(referenced_brokers):
        if broker_id in existing_brokers and existing_brokers[broker_id] in list(brokers_node):
            continue
        ET.SubElement(brokers_node, "Broker", {
            "id": broker_id,
            "name": "[[Darwinex]]" if broker_id == TICK_REAL_DEFAULT_BROKER_ID else f"Broker {broker_id}",
            "description": "Darwinex CFDs" if broker_id == TICK_REAL_DEFAULT_BROKER_ID else "",
            "timezone": TICK_REAL_RESOURCE_TIMEZONE,
            "postfix": "_darwinex" if broker_id == TICK_REAL_DEFAULT_BROKER_ID else "",
            "mtUse": "true",
            "spUse": "false",
        })
    after_brokers = [value_for_node(broker) for broker in brokers_node.findall("Broker")]
    actions.append({
        "field": "Resources/Brokers",
        "from": before_brokers,
        "to": after_brokers,
        "changed": before_brokers != after_brokers,
    })

    before_instruments = [value_for_node(node) for node in instruments_node.findall("InstrumentInfo")]
    for node in list(instruments_node.findall("InstrumentInfo")):
        instruments_node.remove(node)
    for symbol in symbols_node.findall("Symbol"):
        info = symbol.find("InstrumentInfo")
        ET.SubElement(instruments_node, "InstrumentInfo", dict(info.attrib) if info is not None else {})
    after_instruments = [value_for_node(node) for node in instruments_node.findall("InstrumentInfo")]
    actions.append({
        "field": "Resources/Instruments",
        "from": before_instruments,
        "to": after_instruments,
        "changed": before_instruments != after_instruments,
    })

    removed_sessions = [value_for_node(node) for node in sessions_node.findall("Session")]
    for node in list(sessions_node.findall("Session")):
        sessions_node.remove(node)
    actions.append({
        "field": "Resources/Sessions",
        "from": removed_sessions,
        "to": [],
        "changed": bool(removed_sessions),
    })
    actions.append({
        "field": "Resources",
        "from": before_resources,
        "to": _tick_real_resource_summary(root),
        "changed": before_resources != _tick_real_resource_summary(root),
        "note": "CustomIndicators and CustomBlocks are preserved; Project Generator owns final resource rebuild per asset/timeframe.",
    })
    return actions


def enforce_tick_real_data_databanks_resources_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    period = generator_period(TICK_REAL_PERIOD_KEY)
    setup = root.find(".//Data/Setups/Setup")
    if setup is None:
        return ["TICK REAL Data/Setup missing"]
    if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
        issues.append("TICK REAL dates are not ROBUSTNESS_C1")
    if setup.get("testPrecision") != TICK_REAL_DATA_TEST_PRECISION:
        issues.append("TICK REAL testPrecision is not SQX142 tick/simulated code 2")
    if setup.get("session") != TICK_REAL_DATA_SESSION:
        issues.append("TICK REAL session must stay No Session")
    if root.findall(".//Data/OutOfSample/Range"):
        issues.append("TICK REAL must not carry nested OutOfSample ranges")

    databanks = {
        node.get("name", ""): node.get("value", "")
        for node in root.findall(".//Databanks/Databank")
        if node.get("name")
    }
    for name, wanted in TICK_REAL_DATABANKS_TARGET.items():
        if databanks.get(name) != wanted:
            issues.append(f"TICK REAL Databank {name} is {databanks.get(name)!r}, expected {wanted!r}")

    resources = find_section(root, "Resources")
    if resources is None:
        issues.append("TICK REAL Resources missing")
        return issues
    chart_symbols = {
        chart.get("symbol", "")
        for chart in setup.findall("Chart")
        if chart.get("symbol")
    }
    resource_symbols = {
        symbol.get("name", "")
        for symbol in resources.findall("./Symbols/Symbol")
        if symbol.get("name")
    }
    if chart_symbols != resource_symbols:
        issues.append(f"TICK REAL chart/resource mismatch: charts={sorted(chart_symbols)} resources={sorted(resource_symbols)}")
    broker_ids = {
        broker.get("id", "")
        for broker in resources.findall("./Brokers/Broker")
        if broker.get("id")
    }
    for symbol in resources.findall("./Symbols/Symbol"):
        if symbol.get("precision") != TICK_REAL_RESOURCE_PRECISION:
            issues.append(f"TICK REAL resource {symbol.get('name')} precision is not TICK")
        if symbol.get("timezone") != TICK_REAL_RESOURCE_TIMEZONE:
            issues.append(f"TICK REAL resource {symbol.get('name')} timezone is not EETUS")
        if symbol.get("broker") not in broker_ids:
            issues.append(f"TICK REAL resource {symbol.get('name')} references missing broker {symbol.get('broker')}")
        info = symbol.find("InstrumentInfo")
        if info is None:
            issues.append(f"TICK REAL resource {symbol.get('name')} has no nested InstrumentInfo")
        elif info.get("broker") not in broker_ids:
            issues.append(f"TICK REAL nested InstrumentInfo for {symbol.get('name')} references missing broker {info.get('broker')}")
    if resources.findall("./Sessions/Session"):
        issues.append("TICK REAL resources must not keep session entries")

    data_node = find_section(root, "Data")
    databanks_node = find_section(root, "Databanks")
    guarded_text = (
        serialize_xml(data_node if data_node is not None else root)
        + serialize_xml(databanks_node if databanks_node is not None else root)
        + serialize_xml(resources)
    )
    for token in TICK_REAL_BANNED_DONOR_TOKENS:
        if token in guarded_text:
            issues.append(f"Forbidden donor token leaked into TICK REAL Data/Databanks/Resources: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into TICK REAL Data/Databanks/Resources")
    return issues


def update_tick_real_data_databanks_resources_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, TICK_REAL_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "tick_real_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = tick_real_data_databanks_resources_summary(root)
    payload["actions"] = apply_tick_real_data_databanks_resources_to_root(root)
    payload["after"] = tick_real_data_databanks_resources_summary(root)
    payload["issues"] = enforce_tick_real_data_databanks_resources_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "taskTitle": TICK_REAL_TASK_TITLE,
        "periodKey": TICK_REAL_PERIOD_KEY,
        "dateFrom": generator_period(TICK_REAL_PERIOD_KEY)[0],
        "dateTo": generator_period(TICK_REAL_PERIOD_KEY)[1],
        "testPrecision": TICK_REAL_DATA_TEST_PRECISION,
        "databanks": TICK_REAL_DATABANKS_TARGET,
        "resourcePrecision": TICK_REAL_RESOURCE_PRECISION,
        "resourceTimezone": TICK_REAL_RESOURCE_TIMEZONE,
    }
    payload["targetRationale"] = {
        "methodology": "TICK REAL is the precision-data robustness gate after RETEST 1, so it consumes retest 1 and writes TICK.",
        "naturalResults": "The chain preserves natural passed/failed rows; this block does not force Results=passed.",
        "generatorOwned": "Symbol, timeframe, spread, swap and final resources remain owned by Project Generator for each selected asset/timeframe.",
        "noDonorCopy": "Mining15 donor USDJPY/H4 values are not copied; only the confirmed chain and generic compatibility guards are promoted.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_tick_real_data_databanks_resources_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase5_tick_real_data_databanks_resources_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_tick_real_data_databanks_resources_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase5",
        "operation": "tick_real_data_databanks_resources_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase5_tick_real_data_databanks_resources_diff_review" if not apply else "phase5_tick_real_options_rankings_decision",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase5_tick_real_data_databanks_resources_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def apply_tick_real_options_rankings_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []

    for key, value in TICK_REAL_OPTIONS_PARAMS_TARGET.items():
        set_param_text(root, key, value, actions, "Options")

    rankings = find_section(root, "Rankings")
    if rankings is None:
        rankings = ET.SubElement(root, "Rankings", {"type": "never"})
        actions.append({"field": "Rankings", "from": None, "to": dict(rankings.attrib), "changed": True})
    before_rank_attrs = dict(rankings.attrib)
    rankings.set("type", "never")
    actions.append({
        "field": "Rankings:type",
        "from": before_rank_attrs,
        "to": dict(rankings.attrib),
        "changed": before_rank_attrs != dict(rankings.attrib),
    })
    set_or_create_text_child(rankings, "MaxStrategies", TICK_REAL_RANKING_TARGET["MaxStrategies"], actions, "Rankings/MaxStrategies")
    set_or_create_attrs_child(
        rankings,
        "FitnessCriteria",
        {"method": "ComputeFromStrategyResult", "useFitnessByIndex": "false"},
        actions,
        "Rankings/FitnessCriteria",
    )
    set_or_create_text_child(rankings, "ConditionsType", TICK_REAL_RANKING_TARGET["ConditionsType"], actions, "Rankings/ConditionsType")
    set_or_create_text_child(rankings, "DeleteFailedStrategies", TICK_REAL_RANKING_TARGET["DeleteFailedStrategies"], actions, "Rankings/DeleteFailedStrategies")
    set_or_create_text_child(rankings, "ForceRunCrossChecks", TICK_REAL_RANKING_TARGET["ForceRunCrossChecks"], actions, "Rankings/ForceRunCrossChecks")
    set_or_create_attrs_child(rankings, "AutomaticDismissal", TICK_REAL_RANKING_TARGET["AutomaticDismissal"], actions, "Rankings/AutomaticDismissal")
    set_or_create_attrs_child(rankings, "StopCondition", TICK_REAL_RANKING_TARGET["StopCondition"], actions, "Rankings/StopCondition")
    set_or_create_attrs_child(rankings, "FitPortfolio", TICK_REAL_RANKING_TARGET["FitPortfolio"], actions, "Rankings/FitPortfolio")
    set_or_create_attrs_child(rankings, "CustomAnalysis", TICK_REAL_RANKING_TARGET["CustomAnalysis"], actions, "Rankings/CustomAnalysis")
    set_ranking_conditions_from_target(
        rankings,
        TICK_REAL_RANKING_CONDITIONS_TARGET,
        actions,
        "Rankings/Conditions",
    )
    return actions


def tick_real_options_rankings_summary(root: ET.Element) -> dict[str, Any]:
    params = {
        param.get("key", ""): (param.text or "")
        for param in root.findall(".//BuildTradingOptions/Params/Param")
        if param.get("key") in TICK_REAL_OPTIONS_PARAMS_TARGET
    }
    rankings = find_section(root, "Rankings")
    ranking_data: dict[str, Any] = {}
    if rankings is not None:
        ranking_data = {
            "type": rankings.get("type", ""),
            "MaxStrategies": (rankings.findtext("MaxStrategies") or ""),
            "ConditionsType": (rankings.findtext("ConditionsType") or ""),
            "DeleteFailedStrategies": (rankings.findtext("DeleteFailedStrategies") or ""),
            "ForceRunCrossChecks": (rankings.findtext("ForceRunCrossChecks") or ""),
            "FitPortfolio": dict(rankings.find("FitPortfolio").attrib) if rankings.find("FitPortfolio") is not None else {},
            "StopCondition": dict(rankings.find("StopCondition").attrib) if rankings.find("StopCondition") is not None else {},
            "CustomAnalysis": dict(rankings.find("CustomAnalysis").attrib) if rankings.find("CustomAnalysis") is not None else {},
            "conditions": summarize_conditions_detailed(rankings.find("Conditions")),
        }
    return {"optionsParams": params, "rankings": ranking_data}


def enforce_tick_real_options_rankings_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = tick_real_options_rankings_summary(root)
    params = summary.get("optionsParams") or {}
    for key, wanted in TICK_REAL_OPTIONS_PARAMS_TARGET.items():
        if params.get(key) != wanted:
            issues.append(f"TICK REAL Options param {key} is {params.get(key)!r}, expected {wanted!r}")

    if root.findall(".//Data/OutOfSample/Range"):
        issues.append("TICK REAL must not add an internal OOS split; RETEST 0 owns IS/OOS1 validation")

    ranking = summary.get("rankings") or {}
    if ranking.get("DeleteFailedStrategies") != "false":
        issues.append("TICK REAL must keep failed strategies visible for natural passed/failed analysis")
    if ranking.get("ConditionsType") != "1":
        issues.append("TICK REAL ranking conditions must stay active")
    if ranking.get("ForceRunCrossChecks") != "false":
        issues.append("TICK REAL must not force crosschecks from Rankings")
    if (ranking.get("FitPortfolio") or {}).get("active") != "false":
        issues.append("TICK REAL must not run portfolio fit selection")
    if (ranking.get("CustomAnalysis") or {}).get("filter") != "false":
        issues.append("TICK REAL CustomAnalysis filter must remain disabled")
    expected_conditions = [
        {
            "column": item["column"],
            "comparator": item["comparator"],
            "value": item["value"],
            "format": item["format"],
            "sampleType": item.get("sampleType", "127"),
            "use": "true",
        }
        for item in TICK_REAL_RANKING_CONDITIONS_TARGET
    ]
    if ranking.get("conditions") != expected_conditions:
        issues.append("TICK REAL ranking conditions do not match precision-data robustness target")

    options_node = find_section(root, "Options")
    rankings_node = find_section(root, "Rankings")
    guarded_text = (
        serialize_xml(options_node if options_node is not None else root)
        + serialize_xml(rankings_node if rankings_node is not None else root)
    )
    for token in TICK_REAL_BANNED_DONOR_TOKENS:
        if token in guarded_text:
            issues.append(f"Forbidden donor token leaked into TICK REAL Options/Rankings: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into TICK REAL Options/Rankings")
    return issues


def update_tick_real_options_rankings_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, TICK_REAL_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "tick_real_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = tick_real_options_rankings_summary(root)
    payload["actions"] = apply_tick_real_options_rankings_to_root(root)
    payload["after"] = tick_real_options_rankings_summary(root)
    payload["issues"] = enforce_tick_real_options_rankings_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "options": TICK_REAL_OPTIONS_PARAMS_TARGET,
        "rankings": TICK_REAL_RANKING_TARGET,
        "conditions": TICK_REAL_RANKING_CONDITIONS_TARGET,
    }
    payload["targetRationale"] = {
        "academic": "Keep a separate robustness gate without re-optimizing on a repeated OOS split; control selection pressure with explicit total-period tick filters.",
        "naturalResults": "DeleteFailedStrategies=false preserves failed rows, while active conditions let SQX mark natural failed/passed states.",
        "notPortfolio": "FitPortfolio=false keeps this precision-data retest separate from portfolio selection.",
        "generatorOwned": "Base time window is the H1 placeholder; Project Generator rewrites it by selected timeframe.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_tick_real_options_rankings_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase5_tick_real_options_rankings_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_tick_real_options_rankings_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase5",
        "operation": "tick_real_options_rankings_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase5_tick_real_options_rankings_diff_review" if not apply else "phase5_tick_real_passive_generation_decision",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase5_tick_real_options_rankings_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def apply_tick_real_what_to_build_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    what_to_build = find_section(root, "WhatToBuild")
    if what_to_build is None:
        what_to_build = ET.SubElement(root, "WhatToBuild")
        actions.append({"field": "WhatToBuild", "from": None, "to": "created", "changed": True})

    set_or_create_attrs_child(
        what_to_build,
        "StrategyType",
        TICK_REAL_STRATEGY_TYPE_TARGET,
        actions,
        "WhatToBuild/StrategyType",
    )
    build_mode = what_to_build.find("BuildMode")
    if build_mode is None:
        build_mode = ET.SubElement(what_to_build, "BuildMode", {"generationType": "random-generation"})
        actions.append({"field": "WhatToBuild/BuildMode", "from": None, "to": dict(build_mode.attrib), "changed": True})
    else:
        actions.append({
            "field": "WhatToBuild/BuildMode:generationType",
            "from": build_mode.get("generationType", ""),
            "to": build_mode.get("generationType", ""),
            "changed": False,
            "note": "left as SQX-known placeholder; TICK REAL passive behavior is enforced by input databank, disabled improve parts and disabled evolution toggles",
        })
    for tag, value in TICK_REAL_PASSIVE_BUILDMODE_TEXT_TARGET.items():
        set_or_create_text_child(build_mode, tag, value, actions, f"WhatToBuild/BuildMode/{tag}")
    for tag, attrs in TICK_REAL_PASSIVE_BUILDMODE_ATTR_TARGET.items():
        set_or_update_attrs_child(build_mode, tag, attrs, actions, f"WhatToBuild/BuildMode/{tag}")


def apply_tick_real_blocks_to_root(root: ET.Element, source_root: ET.Element | None, actions: list[dict[str, Any]]) -> None:
    blocks = find_blocks(root)
    if blocks is None:
        blocks = ET.SubElement(root, "Blocks", {"type": "simple", "version": "142.2336"})
        actions.append({"field": "Blocks", "from": None, "to": dict(blocks.attrib), "changed": True})

    before_attrs = dict(blocks.attrib)
    blocks.set("type", "simple")
    blocks.set("version", "142.2336")
    actions.append({
        "field": "Blocks:attrs",
        "from": before_attrs,
        "to": dict(blocks.attrib),
        "changed": before_attrs != dict(blocks.attrib),
    })

    source_blocks = find_blocks(source_root)
    if blocks.find("BuildingBlocks") is None and source_blocks is not None:
        actions.append(replace_building_blocks_from_source(blocks, source_blocks))
    else:
        actions.append({
            "field": "BuildingBlocks",
            "changed": False,
            "note": "preserved existing TICK REAL building-block universe; passive gate only enforces no-improve, entry and exit contracts",
        })
    enforce_order_types(blocks, actions)
    enforce_exit_types(blocks, actions)
    enforce_external_custom_data(blocks, actions)
    enforce_disabled_build_block_categories(blocks, actions)


def apply_tick_real_passive_generation_to_root(root: ET.Element, source_root: ET.Element | None) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    apply_retest1_parts_to_improve_to_root(root, actions)
    apply_tick_real_what_to_build_to_root(root, actions)
    apply_tick_real_blocks_to_root(root, source_root, actions)
    return actions


def tick_real_passive_generation_summary(root: ET.Element) -> dict[str, Any]:
    return retest1_passive_generation_summary(root)


def enforce_tick_real_passive_generation_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = tick_real_passive_generation_summary(root)
    parts = summary.get("partsToImprove") or {}
    for group_name in ("EntryRules", "OrderTypes", "ExitRules"):
        group = parts.get(group_name) or {}
        for side in ("LongImprovement", "ShortImprovement"):
            if (group.get(side) or {}).get("use") != "false":
                issues.append(f"TICK REAL {group_name}/{side} must be passive use=false")
    if summary.get("strategyType") != TICK_REAL_STRATEGY_TYPE_TARGET:
        issues.append("TICK REAL StrategyType must point passively to retest 1 with known SQX attributes")
    build_mode = summary.get("buildMode") or {}
    build_text = build_mode.get("text") or {}
    for tag, value in TICK_REAL_PASSIVE_BUILDMODE_TEXT_TARGET.items():
        if build_text.get(tag) != value:
            issues.append(f"TICK REAL BuildMode {tag} is {build_text.get(tag)!r}, expected {value!r}")
    child_attrs = build_mode.get("childAttrs") or {}
    for tag, attrs in TICK_REAL_PASSIVE_BUILDMODE_ATTR_TARGET.items():
        current = child_attrs.get(tag) or {}
        for key, value in attrs.items():
            if current.get(key) != value:
                issues.append(f"TICK REAL BuildMode {tag}.{key} is {current.get(key)!r}, expected {value!r}")
    blocks = summary.get("blocks") or {}
    expected_order = BUILD_ORDER_TYPE_TARGET
    actual_order = {key: blocks.get("orderTypes", {}).get(key) for key in expected_order}
    if actual_order != expected_order:
        issues.append(f"TICK REAL order types are {actual_order!r}, expected {expected_order!r}")
    exits = blocks.get("exitTypes") or {}
    if exits.get(BUILD_EXIT_TYPE_ACTIVE_KEY, {}).get("use") != "true":
        issues.append("TICK REAL must keep only ExitAfterBars active")
    if exits.get(BUILD_EXIT_TYPE_ACTIVE_KEY, {}).get("probability") != "100":
        issues.append("TICK REAL ExitAfterBars probability must be 100")
    active_other_exits = [
        key for key, data in exits.items()
        if key != BUILD_EXIT_TYPE_ACTIVE_KEY and (data or {}).get("use") == "true"
    ]
    if active_other_exits:
        issues.append(f"TICK REAL has non-passive active exit types: {active_other_exits}")
    if any(any(token in key for token in BUILD_EXIT_TYPE_BANNED_TOKENS) for key in exits):
        issues.append("TICK REAL contains day-based exit types")
    if int(blocks.get("activeSignalCount") or 0) != 0:
        issues.append("TICK REAL signals must remain disabled in passive retest")
    if int(blocks.get("activeStopLimitCount") or 0) != 0:
        issues.append("TICK REAL stop/limit entry blocks must remain disabled in passive retest")
    if int(blocks.get("activeIndicatorCount") or 0) <= 0:
        issues.append("TICK REAL must preserve methodology/BlockSettings indicator blocks")
    custom = blocks.get("customData") or {}
    if (custom.get("attrs") or {}).get("showAll") != "false" or custom.get("children") != 0:
        issues.append("TICK REAL external CustomData must stay disabled and empty")
    guarded_sections = [
        find_section(root, "PartsToImprove"),
        find_section(root, "WhatToBuild"),
        find_section(root, "Blocks"),
    ]
    guarded_text = "".join(serialize_xml(section if section is not None else root) for section in guarded_sections)
    for token in ("ExitAfterDays", "ExitAfterTradingDays", "USDJPY_darwinex", "USDJPY_dukascopy"):
        if token in guarded_text:
            issues.append(f"Forbidden token leaked into TICK REAL passive generation tabs: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into TICK REAL passive generation tabs")
    return issues


def update_tick_real_passive_generation_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, TICK_REAL_TASK_TITLE)
    source_task_xml_name, source_root = load_task_root(cfx, TICK_REAL_PASSIVE_SOURCE_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    payload["sourceTaskXml"] = source_task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "tick_real_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload
    if not source_task_xml_name or source_root is None:
        payload["error"] = "tick_real_source_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = tick_real_passive_generation_summary(root)
    payload["actions"] = apply_tick_real_passive_generation_to_root(root, source_root)
    payload["after"] = tick_real_passive_generation_summary(root)
    payload["issues"] = enforce_tick_real_passive_generation_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "strategyType": TICK_REAL_STRATEGY_TYPE_TARGET,
        "buildModeText": TICK_REAL_PASSIVE_BUILDMODE_TEXT_TARGET,
        "buildModeAttributes": TICK_REAL_PASSIVE_BUILDMODE_ATTR_TARGET,
        "sourceTask": TICK_REAL_PASSIVE_SOURCE_TASK_TITLE,
        "orderTypes": BUILD_ORDER_TYPE_TARGET,
        "exitType": BUILD_EXIT_TYPE_ACTIVE_KEY,
        "disabledCategories": BUILD_BLOCK_CATEGORY_DISABLE_TARGET,
    }
    payload["targetRationale"] = {
        "passiveRetest": "TICK REAL consumes retest 1 candidates and must not improve, generate or alter strategy logic.",
        "noUnknownEnum": "BuildMode.generationType is left as an SQX-known placeholder because no local CFX uses a safe none/passive enum.",
        "blocksSource": "Existing TICK REAL BuildingBlocks are preserved to avoid changing strategy logic; RETEST 1 is only a fallback if the section is missing.",
        "methodology": "Signals and Stop/Limit blocks stay off; indicators remain governed by methodology/BlockSettings; only EnterAtMarket plus ExitAfterBars is allowed.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_tick_real_passive_generation_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase5_tick_real_passive_generation_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_tick_real_passive_generation_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase5",
        "operation": "tick_real_passive_generation_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase5_tick_real_passive_generation_diff_review" if not apply else "phase5_tick_real_static_crosschecks_decision",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase5_tick_real_passive_generation_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def tick_real_static_crosschecks_summary(root: ET.Element) -> dict[str, Any]:
    summary = retest1_static_crosschecks_summary(root)
    custom_data = find_section(root, "CustomData")
    setup = custom_data.find(".//Setup") if custom_data is not None else None
    chart = setup.find("Chart") if setup is not None else None
    summary["customData"] = {
        "exists": custom_data is not None,
        "attrs": dict(custom_data.attrib) if custom_data is not None else {},
        "children": len(list(custom_data)) if custom_data is not None else 0,
        "setup": dict(setup.attrib) if setup is not None else {},
        "chart": dict(chart.attrib) if chart is not None else {},
        "sha256": section_sha256(root, "CustomData"),
    }
    return summary


def enforce_tick_real_static_crosschecks_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = tick_real_static_crosschecks_summary(root)
    crosschecks = summary.get("crossChecks") or {}
    if not crosschecks.get("exists"):
        issues.append("TICK REAL CrossChecks section missing")
    if crosschecks.get("attrs") != RETEST1_CROSSCHECKS_TARGET:
        issues.append(f"TICK REAL CrossChecks attrs are {crosschecks.get('attrs')!r}, expected {RETEST1_CROSSCHECKS_TARGET!r}")
    if crosschecks.get("active"):
        issues.append(f"TICK REAL must not have active internal crosschecks: {crosschecks.get('active')}")
    configured_methods = [
        f"{item.get('id')}:{method}"
        for item in (crosschecks.get("checks") or [])
        for method in (item.get("configuredMethods") or [])
    ]
    if configured_methods:
        issues.append(f"TICK REAL CrossChecks must not keep enabled Settings/Methods: {configured_methods}")

    rmm = summary.get("riskMoneyManagement") or {}
    methods = rmm.get("methods") or {}
    for method_type, wanted in RETEST1_RISK_MONEY_MANAGEMENT_METHOD_TARGET.items():
        if methods.get(method_type) != wanted:
            issues.append(f"TICK REAL RiskMoneyManagement {method_type} is {methods.get(method_type)!r}, expected {wanted!r}")

    atms = summary.get("atms") or {}
    for key, wanted in RETEST1_ATMS_TARGET.items():
        if (atms.get("attrs") or {}).get(key) != wanted:
            issues.append(f"TICK REAL ATMs {key} is {(atms.get('attrs') or {}).get(key)!r}, expected {wanted!r}")

    rankings = find_section(root, "Rankings")
    if rankings is not None and (rankings.findtext("ForceRunCrossChecks") or "") != "false":
        issues.append("TICK REAL Rankings/ForceRunCrossChecks must remain false")

    custom = summary.get("customData") or {}
    if not custom.get("exists"):
        issues.append("TICK REAL CustomData section missing")
    else:
        period = generator_period(TICK_REAL_PERIOD_KEY)
        setup = custom.get("setup") or {}
        if setup:
            if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
                issues.append(f"TICK REAL CustomData dates are {(setup.get('dateFrom'), setup.get('dateTo'))!r}, expected {period!r}")
            if setup.get("session") != TICK_REAL_DATA_SESSION:
                issues.append(f"TICK REAL CustomData session is {setup.get('session')!r}, expected {TICK_REAL_DATA_SESSION!r}")
        custom_text = section_text(root, "CustomData")
        for token in TICK_REAL_BANNED_DONOR_TOKENS:
            if token in custom_text:
                issues.append(f"Forbidden donor token leaked into TICK REAL CustomData: {token}")
        if re.search(r"[A-Za-z]:\\", custom_text):
            issues.append("Local absolute path leaked into TICK REAL CustomData")

    for issue in enforce_tick_real_data_databanks_resources_guard(root):
        issues.append(f"Data/Resources guard: {issue}")
    for issue in enforce_tick_real_options_rankings_guard(root):
        issues.append(f"Options/Rankings guard: {issue}")
    for issue in enforce_tick_real_passive_generation_guard(root):
        issues.append(f"Passive generation guard: {issue}")
    return issues


def apply_tick_real_static_crosschecks_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    apply_retest1_crosschecks_to_root(root, actions)
    apply_retest1_risk_money_management_to_root(root, actions)
    return actions


def update_tick_real_static_crosschecks_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, TICK_REAL_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "tick_real_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = tick_real_static_crosschecks_summary(root)
    payload["actions"] = apply_tick_real_static_crosschecks_to_root(root)
    payload["after"] = tick_real_static_crosschecks_summary(root)
    payload["issues"] = enforce_tick_real_static_crosschecks_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "crossChecks": RETEST1_CROSSCHECKS_TARGET,
        "riskMoneyManagementMethods": RETEST1_RISK_MONEY_MANAGEMENT_METHOD_TARGET,
        "staticTabs": TICK_REAL_STATIC_TABS,
    }
    payload["targetRationale"] = {
        "passiveRetest": "TICK REAL must remain a precision-data validation task after RETEST 1, with no internal crosschecks or generation remnants.",
        "riskMoneyManagement": "FixedSize stays active and FixedAmount stays disabled to keep validation comparable with other Capa1 retests.",
        "customData": "CustomData is audited as local-safe and bounded to ROBUSTNESS_C1, but not copied from Mining15 donor.",
        "staticTabs": "ATMs, Notes and CustomData are audited; only executable crosscheck/risk toggles are normalized.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_tick_real_static_crosschecks_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase5_tick_real_static_crosschecks_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_tick_real_static_crosschecks_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase5",
        "operation": "tick_real_static_crosschecks_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase5_tick_real_static_crosschecks_diff_review" if not apply else "phase5_tick_real_closeout",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase5_tick_real_static_crosschecks_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def mc_data_databanks_resources_options_summary(root: ET.Element) -> dict[str, Any]:
    summary = tick_real_data_databanks_resources_summary(root)
    params = {
        param.get("key", ""): (param.text or "")
        for param in root.findall(".//BuildTradingOptions/Params/Param")
        if param.get("key") in MC_OPTIONS_PARAMS_TARGET
    }
    summary["optionsParams"] = params
    return summary


def apply_mc_data_databanks_resources_options_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    period = generator_period(MC_PERIOD_KEY)
    data = find_section(root, "Data")
    setup = root.find(".//Data/Setups/Setup")
    if data is None or setup is None:
        actions.append({"field": "Data", "error": "missing_data_or_setup", "changed": False})
        return actions

    for key, wanted in {
        "dateFrom": period[0],
        "dateTo": period[1],
        "testPrecision": MC_DATA_TEST_PRECISION,
        "session": MC_DATA_SESSION,
    }.items():
        before = setup.get(key, "")
        setup.set(key, wanted)
        actions.append({"field": f"Data/Setup:{key}", "from": before, "to": wanted, "changed": before != wanted})

    out_of_sample = data.find("OutOfSample")
    if out_of_sample is None:
        out_of_sample = ET.SubElement(data, "OutOfSample", {"showGraph": "false"})
        before_oos_attrs: dict[str, str] | None = None
    else:
        before_oos_attrs = dict(out_of_sample.attrib)
        out_of_sample.set("showGraph", "false")
    removed_ranges = [dict(node.attrib) for node in out_of_sample.findall("Range")]
    for node in list(out_of_sample.findall("Range")):
        out_of_sample.remove(node)
    actions.append({
        "field": "Data/OutOfSample",
        "from": {"attrs": before_oos_attrs, "ranges": removed_ranges},
        "to": {"attrs": dict(out_of_sample.attrib), "ranges": []},
        "changed": before_oos_attrs != dict(out_of_sample.attrib) or bool(removed_ranges),
    })

    databanks = find_section(root, "Databanks")
    if databanks is None:
        databanks = ET.SubElement(root, "Databanks", {"retestSelected": "false"})
        actions.append({"field": "Databanks", "from": None, "to": dict(databanks.attrib), "changed": True})
    existing_by_name = {
        node.get("name", ""): node
        for node in databanks.findall("Databank")
        if node.get("name")
    }
    for name, wanted in MC_DATABANKS_TARGET.items():
        node = existing_by_name.get(name)
        if node is None:
            node = ET.SubElement(databanks, "Databank", {"name": name})
            before = None
        else:
            before = dict(node.attrib)
        node.set("name", name)
        node.set("value", wanted)
        node.set("label", f"{name} databank")
        actions.append({
            "field": f"Databanks/{name}",
            "from": before,
            "to": dict(node.attrib),
            "changed": before != dict(node.attrib),
        })

    resources = find_section(root, "Resources")
    if resources is None:
        resources = ET.SubElement(root, "Resources")
        before_resources: dict[str, Any] = {"resourcesFound": False}
    else:
        before_resources = _tick_real_resource_summary(root)

    charts = setup.findall("Chart")
    if not charts:
        chart = ET.SubElement(setup, "Chart", {"symbol": "AUDCAD_darwinex", "timeframe": "H1", "spread": "2"})
        charts = [chart]
        actions.append({"field": "Data/Setup/Chart", "from": None, "to": dict(chart.attrib), "changed": True})
    chart_by_symbol = {
        chart.get("symbol", ""): chart
        for chart in charts
        if chart.get("symbol")
    }
    symbols_node = ensure_resources_container(resources, "Symbols")
    brokers_node = ensure_resources_container(resources, "Brokers")
    instruments_node = ensure_resources_container(resources, "Instruments")
    sessions_node = ensure_resources_container(resources, "Sessions")
    ensure_resources_container(resources, "CustomIndicators")
    ensure_resources_container(resources, "CustomBlocks")

    template_symbol_attrs, template_info_attrs = _first_existing_symbol_template(resources)
    existing_symbols = {
        symbol.get("name", ""): symbol
        for symbol in symbols_node.findall("Symbol")
        if symbol.get("name")
    }
    before_symbols = [value_for_node(symbol) for symbol in symbols_node.findall("Symbol")]
    for symbol in list(symbols_node.findall("Symbol")):
        symbols_node.remove(symbol)

    referenced_brokers: set[str] = set()
    date_from_default = str(epoch_ms_for_date(period[0]))
    date_to_default = str(epoch_ms_for_date(period[1]))
    for symbol_name, chart in chart_by_symbol.items():
        existing_symbol = existing_symbols.get(symbol_name)
        symbol_attrs = dict(existing_symbol.attrib) if existing_symbol is not None else dict(template_symbol_attrs)
        existing_info = existing_symbol.find("InstrumentInfo") if existing_symbol is not None else None
        info_attrs = dict(existing_info.attrib) if existing_info is not None else dict(template_info_attrs)
        broker_id = symbol_attrs.get("broker") or info_attrs.get("broker") or MC_DEFAULT_BROKER_ID
        source_id = symbol_attrs.get("source") or MC_DEFAULT_SOURCE_ID
        bounded_from, bounded_to = bounded_period_ms(
            period,
            symbol_attrs.get("dateFrom") or date_from_default,
            symbol_attrs.get("dateTo") or date_to_default,
        )
        asset = _asset_from_tick_real_symbol(symbol_name)
        referenced_brokers.add(broker_id)
        symbol_node = ET.SubElement(symbols_node, "Symbol", {
            "name": symbol_name,
            "source": source_id,
            "barType": symbol_attrs.get("barType", "1"),
            "precision": MC_RESOURCE_PRECISION,
            "timezone": MC_RESOURCE_TIMEZONE,
            "dateFrom": bounded_from,
            "dateTo": bounded_to,
            "uSymbol": symbol_attrs.get("uSymbol") or asset,
            "uSymbolName": symbol_attrs.get("uSymbolName") or asset,
            "removeWeekends": symbol_attrs.get("removeWeekends", "false"),
            "broker": broker_id,
        })
        info_attrs.update({
            "instrument": symbol_name,
            "defaultSpread": chart.get("spread", info_attrs.get("defaultSpread", "")),
            "dateFrom": "0",
            "dateTo": "0",
            "rows": "0",
            "totalDays": "0",
            "dataType": info_attrs.get("dataType", BUILD_RESOURCES_BASE_DATA_TYPE),
            "broker": broker_id,
        })
        ET.SubElement(symbol_node, "InstrumentInfo", info_attrs)

    after_symbols = [value_for_node(symbol) for symbol in symbols_node.findall("Symbol")]
    actions.append({
        "field": "Resources/Symbols",
        "from": before_symbols,
        "to": after_symbols,
        "changed": before_symbols != after_symbols,
    })

    before_brokers = [value_for_node(broker) for broker in brokers_node.findall("Broker")]
    existing_brokers = {
        broker.get("id", ""): broker
        for broker in brokers_node.findall("Broker")
        if broker.get("id")
    }
    for broker in list(brokers_node.findall("Broker")):
        if broker.get("id") not in referenced_brokers:
            brokers_node.remove(broker)
    for broker_id in sorted(referenced_brokers):
        if broker_id in existing_brokers and existing_brokers[broker_id] in list(brokers_node):
            continue
        ET.SubElement(brokers_node, "Broker", {
            "id": broker_id,
            "name": "[[Darwinex]]" if broker_id == MC_DEFAULT_BROKER_ID else f"Broker {broker_id}",
            "description": "Darwinex CFDs" if broker_id == MC_DEFAULT_BROKER_ID else "",
            "timezone": MC_RESOURCE_TIMEZONE,
            "postfix": "_darwinex" if broker_id == MC_DEFAULT_BROKER_ID else "",
            "mtUse": "true",
            "spUse": "false",
        })
    after_brokers = [value_for_node(broker) for broker in brokers_node.findall("Broker")]
    actions.append({
        "field": "Resources/Brokers",
        "from": before_brokers,
        "to": after_brokers,
        "changed": before_brokers != after_brokers,
    })

    before_instruments = [value_for_node(node) for node in instruments_node.findall("InstrumentInfo")]
    for node in list(instruments_node.findall("InstrumentInfo")):
        instruments_node.remove(node)
    for symbol in symbols_node.findall("Symbol"):
        info = symbol.find("InstrumentInfo")
        ET.SubElement(instruments_node, "InstrumentInfo", dict(info.attrib) if info is not None else {})
    after_instruments = [value_for_node(node) for node in instruments_node.findall("InstrumentInfo")]
    actions.append({
        "field": "Resources/Instruments",
        "from": before_instruments,
        "to": after_instruments,
        "changed": before_instruments != after_instruments,
    })

    removed_sessions = [value_for_node(node) for node in sessions_node.findall("Session")]
    for node in list(sessions_node.findall("Session")):
        sessions_node.remove(node)
    actions.append({
        "field": "Resources/Sessions",
        "from": removed_sessions,
        "to": [],
        "changed": bool(removed_sessions),
    })
    actions.append({
        "field": "Resources",
        "from": before_resources,
        "to": _tick_real_resource_summary(root),
        "changed": before_resources != _tick_real_resource_summary(root),
        "note": "CustomIndicators and CustomBlocks are preserved; Project Generator owns final resource rebuild per asset/timeframe.",
    })

    for key, value in MC_OPTIONS_PARAMS_TARGET.items():
        set_param_text(root, key, value, actions, "Options")
    return actions


def enforce_mc_data_databanks_resources_options_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    period = generator_period(MC_PERIOD_KEY)
    setup = root.find(".//Data/Setups/Setup")
    if setup is None:
        return ["MC Data/Setup missing"]
    if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
        issues.append("MC dates are not ROBUSTNESS_C1")
    if setup.get("testPrecision") != MC_DATA_TEST_PRECISION:
        issues.append("MC testPrecision must stay 2 for fast/simulated Monte Carlo")
    if setup.get("session") != MC_DATA_SESSION:
        issues.append("MC session must stay No Session")
    if root.findall(".//Data/OutOfSample/Range"):
        issues.append("MC must not carry nested OutOfSample ranges")

    databanks = {
        node.get("name", ""): node.get("value", "")
        for node in root.findall(".//Databanks/Databank")
        if node.get("name")
    }
    for name, wanted in MC_DATABANKS_TARGET.items():
        if databanks.get(name) != wanted:
            issues.append(f"MC Databank {name} is {databanks.get(name)!r}, expected {wanted!r}")

    resources = find_section(root, "Resources")
    if resources is None:
        issues.append("MC Resources missing")
        return issues
    chart_symbols = {
        chart.get("symbol", "")
        for chart in setup.findall("Chart")
        if chart.get("symbol")
    }
    resource_symbols = {
        symbol.get("name", "")
        for symbol in resources.findall("./Symbols/Symbol")
        if symbol.get("name")
    }
    if chart_symbols != resource_symbols:
        issues.append(f"MC chart/resource mismatch: charts={sorted(chart_symbols)} resources={sorted(resource_symbols)}")
    broker_ids = {
        broker.get("id", "")
        for broker in resources.findall("./Brokers/Broker")
        if broker.get("id")
    }
    for symbol in resources.findall("./Symbols/Symbol"):
        if symbol.get("precision") != MC_RESOURCE_PRECISION:
            issues.append(f"MC resource {symbol.get('name')} precision is not TICK")
        if symbol.get("timezone") != MC_RESOURCE_TIMEZONE:
            issues.append(f"MC resource {symbol.get('name')} timezone is not EETUS")
        if symbol.get("broker") not in broker_ids:
            issues.append(f"MC resource {symbol.get('name')} references missing broker {symbol.get('broker')}")
        info = symbol.find("InstrumentInfo")
        if info is None:
            issues.append(f"MC resource {symbol.get('name')} has no nested InstrumentInfo")
        elif info.get("broker") not in broker_ids:
            issues.append(f"MC nested InstrumentInfo for {symbol.get('name')} references missing broker {info.get('broker')}")
    if resources.findall("./Sessions/Session"):
        issues.append("MC resources must not keep session entries")

    params = {
        param.get("key", ""): (param.text or "")
        for param in root.findall(".//BuildTradingOptions/Params/Param")
        if param.get("key") in MC_OPTIONS_PARAMS_TARGET
    }
    for key, wanted in MC_OPTIONS_PARAMS_TARGET.items():
        if params.get(key) != wanted:
            issues.append(f"MC Options param {key} is {params.get(key)!r}, expected {wanted!r}")

    data_node = find_section(root, "Data")
    databanks_node = find_section(root, "Databanks")
    options_node = find_section(root, "Options")
    guarded_text = (
        serialize_xml(data_node if data_node is not None else root)
        + serialize_xml(databanks_node if databanks_node is not None else root)
        + serialize_xml(resources)
        + serialize_xml(options_node if options_node is not None else root)
    )
    for token in MC_BANNED_DONOR_TOKENS:
        if token in guarded_text:
            issues.append(f"Forbidden donor token leaked into MC Data/Databanks/Resources/Options: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into MC Data/Databanks/Resources/Options")
    return issues


def update_mc_data_databanks_resources_options_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, MC_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "mc_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = mc_data_databanks_resources_options_summary(root)
    payload["actions"] = apply_mc_data_databanks_resources_options_to_root(root)
    payload["after"] = mc_data_databanks_resources_options_summary(root)
    payload["issues"] = enforce_mc_data_databanks_resources_options_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "taskTitle": MC_TASK_TITLE,
        "periodKey": MC_PERIOD_KEY,
        "dateFrom": generator_period(MC_PERIOD_KEY)[0],
        "dateTo": generator_period(MC_PERIOD_KEY)[1],
        "testPrecision": MC_DATA_TEST_PRECISION,
        "databanks": MC_DATABANKS_TARGET,
        "resourcePrecision": MC_RESOURCE_PRECISION,
        "resourceTimezone": MC_RESOURCE_TIMEZONE,
        "options": MC_OPTIONS_PARAMS_TARGET,
    }
    payload["targetRationale"] = {
        "methodology": "MC is a fast/simulated Monte Carlo robustness perturbation gate after TICK, not an optimizer or another OOS-selection stage.",
        "noInternalOos": "RETEST 0/1 own OOS validation; MC must not add a nested OOS split by default.",
        "naturalResults": "This block preserves natural passed/failed rows and does not force Results=passed.",
        "generatorOwned": "Symbol, timeframe, spread, swap and final resources remain owned by Project Generator for each selected asset/timeframe.",
        "noDonorCopy": "Mining15 donor USDJPY/H4 values and H4 trading window are not copied into the generic Capa1 base.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_mc_data_databanks_resources_options_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase6_mc_data_databanks_resources_options_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_mc_data_databanks_resources_options_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase6",
        "operation": "mc_data_databanks_resources_options_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase6_mc_data_databanks_resources_options_diff_review" if not apply else "phase6_mc_crosschecks_decision",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase6_mc_data_databanks_resources_options_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def ensure_direct_child(parent: ET.Element, tag: str) -> ET.Element:
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag)
    return child


def mc_condition_summary(condition: ET.Element) -> dict[str, Any]:
    left = condition.find("./Left-Side/Column-Value")
    comparator = condition.find("./Comparator")
    right = condition.find("./Right-Side/Column-Value")
    return {
        "use": condition.get("use", ""),
        "left": dict(left.attrib) if left is not None else {},
        "comparator": comparator.get("value", "") if comparator is not None else "",
        "right": dict(right.attrib) if right is not None else {},
    }


def mc_crosschecks_summary(root: ET.Element) -> dict[str, Any]:
    parent = find_section(root, "CrossChecks")
    checks: list[dict[str, Any]] = []
    if parent is not None:
        for check in list(parent):
            if not isinstance(check.tag, str) or check.get("use") is None:
                continue
            methods = []
            for method in check.findall("./Settings/Methods/Method"):
                methods.append({
                    "type": method.get("type", ""),
                    "use": method.get("use", ""),
                    "params": {
                        param.get("key", ""): (param.text or "")
                        for param in method.findall("./Params/Param")
                        if param.get("key")
                    },
                })
            checks.append({
                "id": check.tag,
                "use": check.get("use", ""),
                "methods": methods,
                "numberOfSimulations": check.findtext("./Settings/NumberOfSimulations") or "",
                "mcUseFullSample": check.findtext("./Settings/MCUseFullSample") or "",
                "conditions": [
                    mc_condition_summary(condition)
                    for condition in check.findall("./AcceptanceSettings/Conditions/Condition")
                ],
            })
    rankings = find_section(root, "Rankings")
    return {
        "crossChecks": {
            "exists": parent is not None,
            "attrs": dict(parent.attrib) if parent is not None else {},
            "active": [
                item["id"]
                for item in checks
                if item.get("use") == "true"
            ],
            "checks": checks,
            "sha256": section_sha256(root, "CrossChecks"),
        },
        "rankings": {
            "forceRunCrossChecks": (rankings.findtext("ForceRunCrossChecks") or "") if rankings is not None else "",
        },
    }


def set_method_param(
    method: ET.Element,
    key: str,
    text: str,
    param_type: str,
    actions: list[dict[str, Any]],
    field: str,
) -> None:
    params = method.find("Params")
    if params is None:
        params = ET.SubElement(method, "Params")
        before = None
    else:
        before = [
            {"key": param.get("key", ""), "type": param.get("type", ""), "text": param.text or ""}
            for param in params.findall("Param")
        ]
    target = None
    for param in params.findall("Param"):
        if param.get("key") == key:
            target = param
            break
    if target is None:
        target = ET.SubElement(params, "Param")
    target.set("key", key)
    target.set("type", param_type)
    target.text = text
    after = [
        {"key": param.get("key", ""), "type": param.get("type", ""), "text": param.text or ""}
        for param in params.findall("Param")
    ]
    actions.append({"field": field, "from": before, "to": after, "changed": before != after})


def make_mc_ratio_condition(target: dict[str, Any]) -> ET.Element:
    condition = ET.Element("Condition", {"use": "true"})
    condition.text = "\n            "
    left = ET.SubElement(condition, "Left-Side", {"valueType": "column"})
    left.text = "\n              "
    left.tail = "\n            "
    left_value = ET.SubElement(left, "Column-Value", target["left"])
    left_value.tail = "\n            "
    comparator = ET.SubElement(condition, "Comparator", {"value": target["comparator"]})
    comparator.tail = "\n            "
    right = ET.SubElement(condition, "Right-Side", {"valueType": "column"})
    right.text = "\n              "
    right.tail = "\n          "
    right_value = ET.SubElement(right, "Column-Value", target["right"])
    right_value.tail = "\n            "
    return condition


def set_mc_manipulation_acceptance(check: ET.Element, actions: list[dict[str, Any]]) -> None:
    acceptance = ensure_direct_child(check, "AcceptanceSettings")
    conditions = acceptance.find("Conditions")
    if conditions is None:
        conditions = ET.SubElement(acceptance, "Conditions")
        before: list[dict[str, Any]] = []
    else:
        before = [mc_condition_summary(condition) for condition in conditions.findall("Condition")]
        for child in list(conditions):
            conditions.remove(child)
    conditions.set("CrossCheck", MC_ACTIVE_CROSSCHECK)
    conditions.text = "\n          "
    for index, target in enumerate(MC_MANIPULATION_CONDITIONS_TARGET):
        condition = make_mc_ratio_condition(target)
        condition.tail = "\n        " if index == len(MC_MANIPULATION_CONDITIONS_TARGET) - 1 else "\n          "
        conditions.append(condition)
    after = [mc_condition_summary(condition) for condition in conditions.findall("Condition")]
    actions.append({
        "field": "CrossChecks/MonteCarloManipulation/AcceptanceSettings/Conditions",
        "from": before,
        "to": after,
        "changed": before != after,
    })


def normalize_mc_crosscheck_setups(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    period = generator_period(MC_PERIOD_KEY)
    main_setup = root.find(".//Data/Setups/Setup")
    main_chart = main_setup.find("Chart") if main_setup is not None else None
    target_chart = dict(main_chart.attrib) if main_chart is not None else {}
    before: list[dict[str, Any]] = []
    after: list[dict[str, Any]] = []
    for setup in root.findall(".//CrossChecks/*/Settings/Setups/Setup"):
        setup_before = {
            "attrs": dict(setup.attrib),
            "charts": [dict(chart.attrib) for chart in setup.findall("Chart")],
        }
        before.append(setup_before)
        for key, wanted in {
            "dateFrom": period[0],
            "dateTo": period[1],
            "testPrecision": MC_DATA_TEST_PRECISION,
            "session": MC_DATA_SESSION,
        }.items():
            setup.set(key, wanted)
        if target_chart:
            charts = setup.findall("Chart")
            if not charts:
                charts = [ET.SubElement(setup, "Chart")]
            for chart in charts:
                for key, value in target_chart.items():
                    chart.set(key, value)
        after.append({
            "attrs": dict(setup.attrib),
            "charts": [dict(chart.attrib) for chart in setup.findall("Chart")],
        })
    actions.append({
        "field": "CrossChecks/*/Settings/Setups/Setup",
        "from": before,
        "to": after,
        "changed": before != after,
    })


def apply_mc_crosschecks_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    parent = find_section(root, "CrossChecks")
    if parent is None:
        parent = ET.SubElement(root, "CrossChecks")
        actions.append({"field": "CrossChecks", "from": None, "to": "created", "changed": True})
    before_attrs = dict(parent.attrib)
    for key, value in MC_CROSSCHECK_PARENT_TARGET.items():
        parent.set(key, value)
    actions.append({
        "field": "CrossChecks:attrs",
        "from": before_attrs,
        "to": dict(parent.attrib),
        "changed": before_attrs != dict(parent.attrib),
    })

    active = parent.find(MC_ACTIVE_CROSSCHECK)
    if active is None:
        active = ET.SubElement(parent, MC_ACTIVE_CROSSCHECK)
        actions.append({"field": f"CrossChecks/{MC_ACTIVE_CROSSCHECK}", "from": None, "to": "created", "changed": True})
    for check in list(parent):
        if not isinstance(check.tag, str) or check.get("use") is None:
            continue
        wanted_use = "true" if check.tag == MC_ACTIVE_CROSSCHECK else "false"
        before_use = check.get("use", "")
        check.set("use", wanted_use)
        actions.append({
            "field": f"CrossChecks/{check.tag}:use",
            "from": before_use,
            "to": wanted_use,
            "changed": before_use != wanted_use,
        })

    settings = ensure_direct_child(active, "Settings")
    methods = ensure_direct_child(settings, "Methods")
    existing_methods = {
        method.get("type", ""): method
        for method in methods.findall("Method")
        if method.get("type")
    }
    for method_type, target in MC_MANIPULATION_METHOD_TARGET.items():
        method = existing_methods.get(method_type)
        if method is None:
            method = ET.SubElement(methods, "Method", {"type": method_type})
            before_method = None
        else:
            before_method = value_for_node(method)
        method.set("type", method_type)
        method.set("use", str(target["use"]))
        for param_key, param_target in target["params"].items():
            set_method_param(
                method,
                key=param_key,
                text=str(param_target["text"]),
                param_type=str(param_target["type"]),
                actions=actions,
                field=f"CrossChecks/{MC_ACTIVE_CROSSCHECK}/Method:{method_type}/Param:{param_key}",
            )
        actions.append({
            "field": f"CrossChecks/{MC_ACTIVE_CROSSCHECK}/Method:{method_type}",
            "from": before_method,
            "to": value_for_node(method),
            "changed": before_method != value_for_node(method),
        })
    for method in methods.findall("Method"):
        method_type = method.get("type", "")
        if method_type in MC_MANIPULATION_METHOD_TARGET:
            continue
        before = method.get("use", "")
        method.set("use", "false")
        actions.append({
            "field": f"CrossChecks/{MC_ACTIVE_CROSSCHECK}/Method:{method_type}:use",
            "from": before,
            "to": "false",
            "changed": before != "false",
        })

    for key, value in MC_MANIPULATION_SETTINGS_TARGET.items():
        set_or_create_text_child(settings, key, value, actions, f"CrossChecks/{MC_ACTIVE_CROSSCHECK}/{key}")
    set_mc_manipulation_acceptance(active, actions)

    for check in list(parent):
        if not isinstance(check.tag, str) or check.tag == MC_ACTIVE_CROSSCHECK:
            continue
        for method in check.findall("./Settings/Methods/Method"):
            before = method.get("use", "")
            method.set("use", "false")
            actions.append({
                "field": f"CrossChecks/{check.tag}/Method:{method.get('type', '')}:use",
                "from": before,
                "to": "false",
                "changed": before != "false",
            })
    normalize_mc_crosscheck_setups(root, actions)
    return actions


def enforce_mc_crosschecks_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    parent = find_section(root, "CrossChecks")
    if parent is None:
        return ["MC CrossChecks section missing"]
    if dict(parent.attrib) != MC_CROSSCHECK_PARENT_TARGET:
        issues.append(f"MC CrossChecks attrs are {dict(parent.attrib)!r}, expected {MC_CROSSCHECK_PARENT_TARGET!r}")
    direct_checks = [
        check
        for check in list(parent)
        if isinstance(check.tag, str) and check.get("use") is not None
    ]
    active = [check.tag for check in direct_checks if check.get("use") == "true"]
    if active != [MC_ACTIVE_CROSSCHECK]:
        issues.append(f"MC active crosschecks must be only {MC_ACTIVE_CROSSCHECK}; found {active}")
    manipulation = parent.find(MC_ACTIVE_CROSSCHECK)
    if manipulation is None:
        issues.append("MC MonteCarloManipulation crosscheck missing")
    else:
        settings = manipulation.find("Settings")
        for key, wanted in MC_MANIPULATION_SETTINGS_TARGET.items():
            actual = settings.findtext(key) if settings is not None else ""
            if actual != wanted:
                issues.append(f"MC MonteCarloManipulation {key} is {actual!r}, expected {wanted!r}")
        methods = {
            method.get("type", ""): method
            for method in manipulation.findall("./Settings/Methods/Method")
            if method.get("type")
        }
        for method_type, target in MC_MANIPULATION_METHOD_TARGET.items():
            method = methods.get(method_type)
            if method is None:
                issues.append(f"MC method {method_type} missing")
                continue
            if method.get("use") != target["use"]:
                issues.append(f"MC method {method_type} use is {method.get('use')!r}, expected {target['use']!r}")
            params = {
                param.get("key", ""): (param.text or "")
                for param in method.findall("./Params/Param")
                if param.get("key")
            }
            for param_key, param_target in target["params"].items():
                if params.get(param_key) != param_target["text"]:
                    issues.append(f"MC method {method_type} param {param_key} is {params.get(param_key)!r}, expected {param_target['text']!r}")
        extra_active_methods = [
            method_type
            for method_type, method in methods.items()
            if method_type not in MC_MANIPULATION_METHOD_TARGET and method.get("use") == "true"
        ]
        if extra_active_methods:
            issues.append(f"MC MonteCarloManipulation has unexpected active methods: {extra_active_methods}")
        conditions = [
            mc_condition_summary(condition)
            for condition in manipulation.findall("./AcceptanceSettings/Conditions/Condition")
        ]
        expected_conditions = [
            {"use": "true", "left": item["left"], "comparator": item["comparator"], "right": item["right"]}
            for item in MC_MANIPULATION_CONDITIONS_TARGET
        ]
        if conditions != expected_conditions:
            issues.append(f"MC acceptance conditions drifted: {conditions!r}")

    active_disabled_methods = [
        f"{check.tag}:{method.get('type', '')}"
        for check in direct_checks
        if check.tag != MC_ACTIVE_CROSSCHECK
        for method in check.findall("./Settings/Methods/Method")
        if method.get("use") == "true"
    ]
    if active_disabled_methods:
        issues.append(f"MC disabled crosschecks must not keep enabled methods: {active_disabled_methods}")

    period = generator_period(MC_PERIOD_KEY)
    main_setup = root.find(".//Data/Setups/Setup")
    main_chart = main_setup.find("Chart") if main_setup is not None else None
    target_chart = dict(main_chart.attrib) if main_chart is not None else {}
    for setup in root.findall(".//CrossChecks/*/Settings/Setups/Setup"):
        if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
            issues.append(f"MC nested CrossChecks setup dates drifted: {dict(setup.attrib)!r}")
        if setup.get("testPrecision") != MC_DATA_TEST_PRECISION:
            issues.append(f"MC nested CrossChecks setup precision is {setup.get('testPrecision')!r}, expected {MC_DATA_TEST_PRECISION!r}")
        if setup.get("session") != MC_DATA_SESSION:
            issues.append(f"MC nested CrossChecks setup session is {setup.get('session')!r}, expected {MC_DATA_SESSION!r}")
        for chart in setup.findall("Chart"):
            if target_chart and dict(chart.attrib) != target_chart:
                issues.append(f"MC nested CrossChecks chart drifted: {dict(chart.attrib)!r}, expected {target_chart!r}")

    rankings = find_section(root, "Rankings")
    if rankings is not None and (rankings.findtext("ForceRunCrossChecks") or "") != "false":
        issues.append("MC Rankings/ForceRunCrossChecks must remain false")

    guarded_text = serialize_xml(parent)
    for token in MC_BANNED_DONOR_TOKENS:
        if token in guarded_text:
            issues.append(f"Forbidden donor token leaked into MC CrossChecks: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into MC CrossChecks")
    return issues


def update_mc_crosschecks_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, MC_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "mc_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = mc_crosschecks_summary(root)
    payload["actions"] = apply_mc_crosschecks_to_root(root)
    payload["after"] = mc_crosschecks_summary(root)
    payload["issues"] = enforce_mc_crosschecks_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "parent": MC_CROSSCHECK_PARENT_TARGET,
        "onlyActive": MC_ACTIVE_CROSSCHECK,
        "inactiveCrossChecks": list(MC_INACTIVE_CROSSCHECKS),
        "settings": MC_MANIPULATION_SETTINGS_TARGET,
        "methods": MC_MANIPULATION_METHOD_TARGET,
        "conditions": MC_MANIPULATION_CONDITIONS_TARGET,
        "rankingsForceRunCrossChecks": "false",
    }
    payload["targetRationale"] = {
        "methodology": "MC is the trade-order Monte Carlo manipulation gate after TICK; MC2/Monkey/Synthetic remain separate tasks.",
        "quality": "Use 200 simulations on the full sample, preserve natural passed/failed results, and avoid using MC as a new optimizer.",
        "cleanup": "Disabled crosscheck methods are switched off so stale MonteCarloRetest/WhatIf settings cannot execute accidentally.",
        "generatorOwned": "Nested disabled setups are bounded to ROBUSTNESS_C1 and mirror the base chart seed; Project Generator owns final asset/timeframe rewrites.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_mc_crosschecks_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase6_mc_crosschecks_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_mc_crosschecks_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase6",
        "operation": "mc_crosschecks_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase6_mc_crosschecks_diff_review" if not apply else "phase6_mc_passive_generation_decision",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase6_mc_crosschecks_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def apply_mc_what_to_build_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    what_to_build = find_section(root, "WhatToBuild")
    if what_to_build is None:
        what_to_build = ET.SubElement(root, "WhatToBuild")
        actions.append({"field": "WhatToBuild", "from": None, "to": "created", "changed": True})

    set_or_create_attrs_child(
        what_to_build,
        "StrategyType",
        MC_STRATEGY_TYPE_TARGET,
        actions,
        "WhatToBuild/StrategyType",
    )
    build_mode = what_to_build.find("BuildMode")
    if build_mode is None:
        build_mode = ET.SubElement(what_to_build, "BuildMode", {"generationType": "random-generation"})
        actions.append({"field": "WhatToBuild/BuildMode", "from": None, "to": dict(build_mode.attrib), "changed": True})
    else:
        actions.append({
            "field": "WhatToBuild/BuildMode:generationType",
            "from": build_mode.get("generationType", ""),
            "to": build_mode.get("generationType", ""),
            "changed": False,
            "note": "left as SQX-known placeholder; MC passive behavior is enforced by input databank, disabled improve parts and disabled evolution toggles",
        })
    for tag, value in MC_PASSIVE_BUILDMODE_TEXT_TARGET.items():
        set_or_create_text_child(build_mode, tag, value, actions, f"WhatToBuild/BuildMode/{tag}")
    for tag, attrs in MC_PASSIVE_BUILDMODE_ATTR_TARGET.items():
        set_or_update_attrs_child(build_mode, tag, attrs, actions, f"WhatToBuild/BuildMode/{tag}")


def apply_mc_blocks_to_root(root: ET.Element, source_root: ET.Element | None, actions: list[dict[str, Any]]) -> None:
    blocks = find_blocks(root)
    if blocks is None:
        blocks = ET.SubElement(root, "Blocks", {"type": "simple", "version": "142.2336"})
        actions.append({"field": "Blocks", "from": None, "to": dict(blocks.attrib), "changed": True})

    before_attrs = dict(blocks.attrib)
    blocks.set("type", "simple")
    blocks.set("version", "142.2336")
    actions.append({
        "field": "Blocks:attrs",
        "from": before_attrs,
        "to": dict(blocks.attrib),
        "changed": before_attrs != dict(blocks.attrib),
    })

    source_blocks = find_blocks(source_root)
    if blocks.find("BuildingBlocks") is None and source_blocks is not None:
        actions.append(replace_building_blocks_from_source(blocks, source_blocks))
    else:
        actions.append({
            "field": "BuildingBlocks",
            "changed": False,
            "note": "preserved existing MC building-block universe; passive gate only enforces no-improve, entry and exit contracts",
        })
    enforce_order_types(blocks, actions)
    enforce_exit_types(blocks, actions)
    enforce_external_custom_data(blocks, actions)
    enforce_disabled_build_block_categories(blocks, actions)


def apply_mc_passive_generation_to_root(root: ET.Element, source_root: ET.Element | None) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    apply_retest1_parts_to_improve_to_root(root, actions)
    apply_mc_what_to_build_to_root(root, actions)
    apply_mc_blocks_to_root(root, source_root, actions)
    return actions


def mc_passive_generation_summary(root: ET.Element) -> dict[str, Any]:
    return retest1_passive_generation_summary(root)


def enforce_mc_passive_generation_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = mc_passive_generation_summary(root)
    parts = summary.get("partsToImprove") or {}
    for group_name in ("EntryRules", "OrderTypes", "ExitRules"):
        group = parts.get(group_name) or {}
        for side in ("LongImprovement", "ShortImprovement"):
            if (group.get(side) or {}).get("use") != "false":
                issues.append(f"MC {group_name}/{side} must be passive use=false")
    if summary.get("strategyType") != MC_STRATEGY_TYPE_TARGET:
        issues.append("MC StrategyType must point passively to TICK with known SQX attributes")
    build_mode = summary.get("buildMode") or {}
    build_text = build_mode.get("text") or {}
    for tag, value in MC_PASSIVE_BUILDMODE_TEXT_TARGET.items():
        if build_text.get(tag) != value:
            issues.append(f"MC BuildMode {tag} is {build_text.get(tag)!r}, expected {value!r}")
    child_attrs = build_mode.get("childAttrs") or {}
    for tag, attrs in MC_PASSIVE_BUILDMODE_ATTR_TARGET.items():
        current = child_attrs.get(tag) or {}
        for key, value in attrs.items():
            if current.get(key) != value:
                issues.append(f"MC BuildMode {tag}.{key} is {current.get(key)!r}, expected {value!r}")
    blocks = summary.get("blocks") or {}
    expected_order = BUILD_ORDER_TYPE_TARGET
    actual_order = {key: blocks.get("orderTypes", {}).get(key) for key in expected_order}
    if actual_order != expected_order:
        issues.append(f"MC order types are {actual_order!r}, expected {expected_order!r}")
    exits = blocks.get("exitTypes") or {}
    if exits.get(BUILD_EXIT_TYPE_ACTIVE_KEY, {}).get("use") != "true":
        issues.append("MC must keep only ExitAfterBars active")
    if exits.get(BUILD_EXIT_TYPE_ACTIVE_KEY, {}).get("probability") != "100":
        issues.append("MC ExitAfterBars probability must be 100")
    active_other_exits = [
        key for key, data in exits.items()
        if key != BUILD_EXIT_TYPE_ACTIVE_KEY and (data or {}).get("use") == "true"
    ]
    if active_other_exits:
        issues.append(f"MC has non-passive active exit types: {active_other_exits}")
    if any(any(token in key for token in BUILD_EXIT_TYPE_BANNED_TOKENS) for key in exits):
        issues.append("MC contains day-based exit types")
    if int(blocks.get("activeSignalCount") or 0) != 0:
        issues.append("MC signals must remain disabled in passive retest")
    if int(blocks.get("activeStopLimitCount") or 0) != 0:
        issues.append("MC stop/limit entry blocks must remain disabled in passive retest")
    if int(blocks.get("activeIndicatorCount") or 0) <= 0:
        issues.append("MC must preserve methodology/BlockSettings indicator blocks")
    custom = blocks.get("customData") or {}
    if (custom.get("attrs") or {}).get("showAll") != "false" or custom.get("children") != 0:
        issues.append("MC external CustomData must stay disabled and empty")
    guarded_sections = [
        find_section(root, "PartsToImprove"),
        find_section(root, "WhatToBuild"),
        find_section(root, "Blocks"),
    ]
    guarded_text = "".join(serialize_xml(section if section is not None else root) for section in guarded_sections)
    for token in ("ExitAfterDays", "ExitAfterTradingDays", "USDJPY_darwinex", "USDJPY_dukascopy"):
        if token in guarded_text:
            issues.append(f"Forbidden token leaked into MC passive generation tabs: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into MC passive generation tabs")
    return issues


def update_mc_passive_generation_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, MC_TASK_TITLE)
    source_task_xml_name, source_root = load_task_root(cfx, MC_PASSIVE_SOURCE_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    payload["sourceTaskXml"] = source_task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "mc_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload
    if not source_task_xml_name or source_root is None:
        payload["error"] = "mc_source_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = mc_passive_generation_summary(root)
    payload["actions"] = apply_mc_passive_generation_to_root(root, source_root)
    payload["after"] = mc_passive_generation_summary(root)
    payload["issues"] = enforce_mc_passive_generation_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "strategyType": MC_STRATEGY_TYPE_TARGET,
        "buildModeText": MC_PASSIVE_BUILDMODE_TEXT_TARGET,
        "buildModeAttributes": MC_PASSIVE_BUILDMODE_ATTR_TARGET,
        "sourceTask": MC_PASSIVE_SOURCE_TASK_TITLE,
        "orderTypes": BUILD_ORDER_TYPE_TARGET,
        "exitType": BUILD_EXIT_TYPE_ACTIVE_KEY,
        "disabledCategories": BUILD_BLOCK_CATEGORY_DISABLE_TARGET,
    }
    payload["targetRationale"] = {
        "passiveRetest": "MC consumes TICK candidates and must not improve, generate or alter strategy logic.",
        "noUnknownEnum": "BuildMode.generationType is left as an SQX-known placeholder because no local CFX uses a safe none/passive enum.",
        "blocksSource": "Existing MC BuildingBlocks are preserved to avoid donor universe drift; TICK REAL is only a fallback if the section is missing.",
        "methodology": "Signals and Stop/Limit blocks stay off; indicators remain governed by methodology/BlockSettings; only EnterAtMarket plus ExitAfterBars is allowed.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_mc_passive_generation_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase6_mc_passive_generation_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_mc_passive_generation_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase6",
        "operation": "mc_passive_generation_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase6_mc_passive_generation_diff_review" if not apply else "phase6_mc_static_tabs_decision",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase6_mc_passive_generation_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def set_attrs_on_node(node: ET.Element, attrs: dict[str, str], actions: list[dict[str, Any]], field: str) -> None:
    before = dict(node.attrib)
    for key, value in attrs.items():
        node.set(key, value)
    after = dict(node.attrib)
    actions.append({"field": field, "from": before, "to": after, "changed": before != after})


def clear_ranking_conditions(
    rankings: ET.Element,
    actions: list[dict[str, Any]],
    field: str,
    note: str = "MC pass/fail is owned by CrossChecks acceptance conditions",
) -> None:
    conditions = rankings.find("Conditions")
    if conditions is None:
        actions.append({
            "field": field,
            "from": [],
            "to": [],
            "changed": False,
            "note": note,
        })
        return
    before = summarize_conditions_detailed(conditions)
    for child in list(conditions):
        conditions.remove(child)
    after = summarize_conditions_detailed(conditions)
    actions.append({
        "field": field,
        "from": before,
        "to": after,
        "changed": before != after,
        "note": note,
    })


def main_chart_seed(root: ET.Element) -> dict[str, str]:
    setup = root.find(".//Data/Setups/Setup")
    chart = setup.find("Chart") if setup is not None else None
    if chart is None:
        return {}
    return {
        key: chart.get(key, "")
        for key in ("symbol", "timeframe", "spread")
        if chart.get(key) is not None
    }


def apply_mc_rankings_to_root(
    root: ET.Element,
    actions: list[dict[str, Any]],
    conditions_note: str = "MC pass/fail is owned by CrossChecks acceptance conditions",
) -> None:
    rankings = find_section(root, "Rankings")
    if rankings is None:
        rankings = ET.SubElement(root, "Rankings", {"type": "never"})
        actions.append({"field": "Rankings", "from": None, "to": dict(rankings.attrib), "changed": True})
    before_rank_attrs = dict(rankings.attrib)
    rankings.set("type", "never")
    actions.append({
        "field": "Rankings:type",
        "from": before_rank_attrs,
        "to": dict(rankings.attrib),
        "changed": before_rank_attrs != dict(rankings.attrib),
    })
    set_or_create_text_child(rankings, "MaxStrategies", MC_RANKING_TARGET["MaxStrategies"], actions, "Rankings/MaxStrategies")
    set_or_update_attrs_child(
        rankings,
        "FitnessCriteria",
        {"method": "ComputeFromStrategyResult", "useFitnessByIndex": "false"},
        actions,
        "Rankings/FitnessCriteria",
    )
    set_or_create_text_child(rankings, "ConditionsType", MC_RANKING_TARGET["ConditionsType"], actions, "Rankings/ConditionsType")
    set_or_create_text_child(rankings, "DeleteFailedStrategies", MC_RANKING_TARGET["DeleteFailedStrategies"], actions, "Rankings/DeleteFailedStrategies")
    set_or_create_text_child(rankings, "ForceRunCrossChecks", MC_RANKING_TARGET["ForceRunCrossChecks"], actions, "Rankings/ForceRunCrossChecks")
    set_or_update_attrs_child(rankings, "AutomaticDismissal", MC_RANKING_TARGET["AutomaticDismissal"], actions, "Rankings/AutomaticDismissal")
    set_or_update_attrs_child(rankings, "StopCondition", MC_RANKING_TARGET["StopCondition"], actions, "Rankings/StopCondition")
    set_or_update_attrs_child(rankings, "FitPortfolio", MC_RANKING_TARGET["FitPortfolio"], actions, "Rankings/FitPortfolio")
    set_or_update_attrs_child(rankings, "CustomAnalysis", MC_RANKING_TARGET["CustomAnalysis"], actions, "Rankings/CustomAnalysis")
    clear_ranking_conditions(rankings, actions, "Rankings/Conditions", note=conditions_note)


def apply_sequential_rankings_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    apply_mc_rankings_to_root(
        root,
        actions,
        conditions_note="Sequential pass/fail is owned by SequentialOptimization acceptance settings",
    )


def apply_mc_atms_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    atms = find_section(root, "ATMs")
    if atms is None:
        atms = ET.SubElement(root, "ATMs")
        actions.append({"field": "ATMs", "from": None, "to": dict(atms.attrib), "changed": True})
    set_attrs_on_node(atms, RETEST1_ATMS_TARGET, actions, "ATMs:attrs")


def apply_mc_selected_strategies_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    selected = find_section(root, "SelectedStrategies")
    if selected is None:
        actions.append({
            "field": "SelectedStrategies",
            "from": None,
            "to": None,
            "changed": False,
            "note": "missing is accepted as empty in SQX automatic retests",
        })
        return
    before = {"text": (selected.text or "").strip(), "children": [value_for_node(child) for child in list(selected)]}
    for child in list(selected):
        selected.remove(child)
    selected.text = None
    after = {"text": "", "children": []}
    actions.append({"field": "SelectedStrategies", "from": before, "to": after, "changed": before != after})


def apply_mc_custom_data_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    custom = find_section(root, "CustomData")
    if custom is None:
        custom = ET.SubElement(root, "CustomData")
        actions.append({"field": "CustomData", "from": None, "to": "created", "changed": True})
    setups = ensure_direct_child(custom, "Setups")
    setup = setups.find("Setup")
    if setup is None:
        setup = ET.SubElement(setups, "Setup")
        actions.append({"field": "CustomData/Setup", "from": None, "to": dict(setup.attrib), "changed": True})

    period = generator_period(MC_PERIOD_KEY)
    setup_attrs = {
        "dateFrom": period[0],
        "dateTo": period[1],
        "testPrecision": MC_DATA_TEST_PRECISION,
        "session": MC_DATA_SESSION,
        "slippage": "0",
        "minDist": "0",
    }
    if not setup.get("engine"):
        setup_attrs["engine"] = "MetaTrader4"
    set_attrs_on_node(setup, setup_attrs, actions, "CustomData/Setup:attrs")

    chart = setup.find("Chart")
    if chart is None:
        chart = ET.SubElement(setup, "Chart")
        actions.append({"field": "CustomData/Setup/Chart", "from": None, "to": dict(chart.attrib), "changed": True})
    chart_target = main_chart_seed(root)
    if chart_target:
        set_attrs_on_node(chart, chart_target, actions, "CustomData/Setup/Chart:attrs")

    commissions = ensure_direct_child(setup, "Commissions")
    existing_methods = {
        method.get("type", ""): method
        for method in commissions.findall("Method")
        if method.get("type")
    }
    for method_type, use in {"None": "false", "SizeBased": "true"}.items():
        method = existing_methods.get(method_type)
        if method is None:
            method = ET.SubElement(commissions, "Method", {"type": method_type})
            before = None
        else:
            before = dict(method.attrib)
        method.set("type", method_type)
        method.set("use", use)
        actions.append({
            "field": f"CustomData/Commissions/Method:{method_type}",
            "from": before,
            "to": dict(method.attrib),
            "changed": before != dict(method.attrib),
        })
        if method_type == "SizeBased":
            params = ensure_direct_child(method, "Params")
            param = None
            for candidate in params.findall("Param"):
                if candidate.get("key") == "Commission":
                    param = candidate
                    break
            if param is None:
                param = ET.SubElement(params, "Param", {"key": "Commission", "className": "SizeBased"})
                before_param = None
            else:
                before_param = {**dict(param.attrib), "text": param.text or ""}
            param.set("key", "Commission")
            param.set("className", "SizeBased")
            param.text = MC_CUSTOM_DATA_COMMISSION_TARGET
            after_param = {**dict(param.attrib), "text": param.text or ""}
            actions.append({
                "field": "CustomData/Commissions/Method:SizeBased/Param:Commission",
                "from": before_param,
                "to": after_param,
                "changed": before_param != after_param,
            })

    main_values = setup.find("MainTestValues")
    if main_values is None:
        main_values = ET.SubElement(setup, "MainTestValues")
        actions.append({"field": "CustomData/MainTestValues", "from": None, "to": dict(main_values.attrib), "changed": True})
    set_attrs_on_node(main_values, MC_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET, actions, "CustomData/MainTestValues:attrs")


def apply_mc_static_tabs_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    apply_mc_rankings_to_root(root, actions)
    apply_retest1_risk_money_management_to_root(root, actions)
    apply_mc_atms_to_root(root, actions)
    actions.append({"field": "Notes", "changed": False, "sha256": section_sha256(root, "Notes"), "note": "audited and preserved"})
    apply_mc_selected_strategies_to_root(root, actions)
    apply_mc_custom_data_to_root(root, actions)
    return actions


def mc_static_tabs_summary(root: ET.Element) -> dict[str, Any]:
    summary = tick_real_static_crosschecks_summary(root)
    rankings = find_section(root, "Rankings")
    ranking_data: dict[str, Any] = {}
    if rankings is not None:
        ranking_data = {
            "type": rankings.get("type", ""),
            "MaxStrategies": rankings.findtext("MaxStrategies") or "",
            "ConditionsType": rankings.findtext("ConditionsType") or "",
            "DeleteFailedStrategies": rankings.findtext("DeleteFailedStrategies") or "",
            "ForceRunCrossChecks": rankings.findtext("ForceRunCrossChecks") or "",
            "FitPortfolio": dict(rankings.find("FitPortfolio").attrib) if rankings.find("FitPortfolio") is not None else {},
            "StopCondition": dict(rankings.find("StopCondition").attrib) if rankings.find("StopCondition") is not None else {},
            "CustomAnalysis": dict(rankings.find("CustomAnalysis").attrib) if rankings.find("CustomAnalysis") is not None else {},
            "conditions": summarize_conditions_detailed(rankings.find("Conditions")),
            "sha256": section_sha256(root, "Rankings"),
        }
    summary["rankings"] = ranking_data
    custom = find_section(root, "CustomData")
    setup = custom.find(".//Setup") if custom is not None else None
    size_based = setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']") if setup is not None else None
    main_values = setup.find("MainTestValues") if setup is not None else None
    if "customData" in summary:
        summary["customData"]["commission"] = (size_based.text or "") if size_based is not None else ""
        summary["customData"]["mainTestValues"] = dict(main_values.attrib) if main_values is not None else {}
    return summary


def enforce_mc_static_tabs_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = mc_static_tabs_summary(root)
    ranking = summary.get("rankings") or {}
    if ranking.get("type") != "never":
        issues.append(f"MC Rankings type is {ranking.get('type')!r}, expected 'never'")
    for key in ("MaxStrategies", "ConditionsType", "DeleteFailedStrategies", "ForceRunCrossChecks"):
        if ranking.get(key) != MC_RANKING_TARGET[key]:
            issues.append(f"MC Rankings {key} is {ranking.get(key)!r}, expected {MC_RANKING_TARGET[key]!r}")
    if (ranking.get("FitPortfolio") or {}).get("active") != "false":
        issues.append("MC FitPortfolio must remain disabled; portfolio selection belongs to later portfolio phases")
    if (ranking.get("CustomAnalysis") or {}).get("filter") != "false":
        issues.append("MC CustomAnalysis filter must remain disabled")
    if ranking.get("conditions"):
        issues.append("MC Rankings must not add extra conditions; CrossChecks acceptance owns MC pass/fail")

    rmm = summary.get("riskMoneyManagement") or {}
    methods = rmm.get("methods") or {}
    for method_type, wanted in RETEST1_RISK_MONEY_MANAGEMENT_METHOD_TARGET.items():
        if methods.get(method_type) != wanted:
            issues.append(f"MC RiskMoneyManagement {method_type} is {methods.get(method_type)!r}, expected {wanted!r}")

    atms = summary.get("atms") or {}
    for key, wanted in RETEST1_ATMS_TARGET.items():
        if (atms.get("attrs") or {}).get(key) != wanted:
            issues.append(f"MC ATMs {key} is {(atms.get('attrs') or {}).get(key)!r}, expected {wanted!r}")

    selected = summary.get("selectedStrategies") or {}
    if selected.get("children") != 0 or selected.get("text"):
        issues.append("MC SelectedStrategies must remain empty in the base template")

    custom = summary.get("customData") or {}
    if not custom.get("exists"):
        issues.append("MC CustomData section missing")
    else:
        period = generator_period(MC_PERIOD_KEY)
        setup = custom.get("setup") or {}
        chart = custom.get("chart") or {}
        if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
            issues.append(f"MC CustomData dates are {(setup.get('dateFrom'), setup.get('dateTo'))!r}, expected {period!r}")
        if setup.get("testPrecision") != MC_DATA_TEST_PRECISION:
            issues.append(f"MC CustomData testPrecision is {setup.get('testPrecision')!r}, expected {MC_DATA_TEST_PRECISION!r}")
        if setup.get("session") != MC_DATA_SESSION:
            issues.append(f"MC CustomData session is {setup.get('session')!r}, expected {MC_DATA_SESSION!r}")
        target_chart = main_chart_seed(root)
        if target_chart and {key: chart.get(key, "") for key in target_chart} != target_chart:
            issues.append(f"MC CustomData chart seed is {chart!r}, expected {target_chart!r}")
        if custom.get("commission") != MC_CUSTOM_DATA_COMMISSION_TARGET:
            issues.append(f"MC CustomData commission is {custom.get('commission')!r}, expected {MC_CUSTOM_DATA_COMMISSION_TARGET!r}")
        if custom.get("mainTestValues") != MC_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET:
            issues.append("MC CustomData MainTestValues drifted from methodology target")

    guarded_text = (
        section_text(root, "Rankings")
        + section_text(root, "ATMs")
        + section_text(root, "RiskMoneyManagement")
        + section_text(root, "SelectedStrategies")
        + section_text(root, "CustomData")
    )
    for token in MC_BANNED_DONOR_TOKENS:
        if token in guarded_text:
            issues.append(f"Forbidden donor token leaked into MC static tabs: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into MC static tabs")

    for issue in enforce_mc_data_databanks_resources_options_guard(root):
        issues.append(f"Data/Resources guard: {issue}")
    for issue in enforce_mc_crosschecks_guard(root):
        issues.append(f"CrossChecks guard: {issue}")
    for issue in enforce_mc_passive_generation_guard(root):
        issues.append(f"Passive generation guard: {issue}")
    return issues


def update_mc_static_tabs_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, MC_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "mc_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = mc_static_tabs_summary(root)
    payload["actions"] = apply_mc_static_tabs_to_root(root)
    payload["after"] = mc_static_tabs_summary(root)
    payload["issues"] = enforce_mc_static_tabs_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "rankings": MC_RANKING_TARGET,
        "rankingConditions": [],
        "riskMoneyManagementMethods": RETEST1_RISK_MONEY_MANAGEMENT_METHOD_TARGET,
        "atms": RETEST1_ATMS_TARGET,
        "staticTabs": MC_STATIC_TABS,
        "customDataMainTestValues": MC_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET,
        "customDataCommission": MC_CUSTOM_DATA_COMMISSION_TARGET,
    }
    payload["targetRationale"] = {
        "ranking": "MC pass/fail is owned by MonteCarloManipulation acceptance conditions; Ranking must preserve failed rows and not run portfolio selection.",
        "riskMoneyManagement": "FixedSize keeps Capa1 retests comparable and avoids sizing noise.",
        "customData": "CustomData remains a generic local-safe seed synchronized to the main Data chart, not Mining15 donor values.",
        "staticTabs": "ATMs, Notes and SelectedStrategies stay inert while executable behavior is guarded by previous MC blocks.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_mc_static_tabs_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase6_mc_static_tabs_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_mc_static_tabs_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase6",
        "operation": "mc_static_tabs_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase6_mc_static_tabs_diff_review" if not apply else "phase6_mc_closeout",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase6_mc_static_tabs_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


MC_CLOSEOUT_OPERATIONS = (
    ("dataDatabanksResourcesOptions", "mc-data-databanks-resources-options-target", promote_mc_data_databanks_resources_options_target),
    ("crosschecks", "mc-crosschecks-target", promote_mc_crosschecks_target),
    ("passiveGeneration", "mc-passive-generation-target", promote_mc_passive_generation_target),
    ("staticTabs", "mc-static-tabs-target", promote_mc_static_tabs_target),
)


def mc_closeout_operation_issues(operation: str, payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if payload.get("apply") is not False:
        issues.append(f"{operation}: closeout must run in dry-run mode")
    if not payload.get("ok"):
        issues.append(f"{operation}: operation ok=false")
    results = payload.get("results") or {}
    if not results:
        issues.append(f"{operation}: no target results")
    for target_name, result in results.items():
        prefix = f"{operation}/{target_name}"
        if not result.get("exists"):
            issues.append(f"{prefix}: target file missing")
        if not result.get("isZip"):
            issues.append(f"{prefix}: target is not a .cfx/.zip")
        if result.get("error"):
            issues.append(f"{prefix}: {result.get('error')}")
        if result.get("guardOk") is not True:
            issues.append(f"{prefix}: guardOk is not true")
        if result.get("changed") is not False:
            issues.append(f"{prefix}: dry-run is not idempotent")
        if result.get("changedActionCount") not in {0, "0"}:
            issues.append(f"{prefix}: changedActionCount is {result.get('changedActionCount')!r}, expected 0")
        for issue in result.get("issues") or []:
            issues.append(f"{prefix}: {issue}")
    return issues


def mc_closeout_operation_summary(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": payload.get("ok"),
        "operation": payload.get("operation"),
        "written": payload.get("written", ""),
        "nextPhase": payload.get("nextPhase", ""),
        "targets": {
            target_name: {
                "exists": result.get("exists"),
                "isZip": result.get("isZip"),
                "guardOk": result.get("guardOk"),
                "changed": result.get("changed"),
                "changedActionCount": result.get("changedActionCount"),
                "taskXml": result.get("taskXml", ""),
                "sha256Before": result.get("sha256Before", ""),
                "sha256After": result.get("sha256After", ""),
            }
            for target_name, result in (payload.get("results") or {}).items()
        },
    }


def mc_closeout_report(root142: Path, project_root: Path, target: str, write: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    operations: dict[str, Any] = {}
    issues: list[str] = []
    for key, command, runner in MC_CLOSEOUT_OPERATIONS:
        result = runner(root142, project_root, target=target, apply=False)
        operation_issues = mc_closeout_operation_issues(command, result)
        operations[key] = {
            "command": command,
            "summary": mc_closeout_operation_summary(result),
            "issues": operation_issues,
        }
        issues.extend(operation_issues)

    payload: dict[str, Any] = {
        "ok": not issues,
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase6_mc_closeout",
        "target": target,
        "write": write,
        "operations": operations,
        "issues": issues,
        "processProbe": process_snapshot(),
        "summary": {
            "mcTaskTitle": MC_TASK_TITLE,
            "mcTaskXml": "AutomaticRetest-Task1.xml",
            "chain": "Input=TICK / Output=MC",
            "period": MC_PERIOD_KEY,
            "testPrecision": MC_DATA_TEST_PRECISION,
            "activeCrossCheck": "MonteCarloManipulation",
            "nextPhase": "phase7_mc2_open",
            "closeoutCriterion": "all MC guards must be green and idempotent on local base and repo template",
        },
        "nextPhase": "phase7_mc2_open",
    }
    if write:
        target_path = ledger_root(project_root) / "phase_reports" / f"phase6_mc_closeout_{stamp()}.json"
        write_json(target_path, payload)
        state_path = ledger_root(project_root) / "session_state.json"
        state = read_json(state_path, {})
        state.update({"updatedAt": now_iso(), "currentPhase": "phase6_mc_closeout", "nextPhase": "phase7_mc2_open"})
        write_json(state_path, state)
        payload["written"] = str(target_path)
    return payload


def positive_chart_spreads(root: ET.Element | None) -> list[float]:
    if root is None:
        return []
    spreads: list[float] = []
    for chart in root.findall(".//Chart"):
        try:
            value = float(chart.get("spread", ""))
        except (TypeError, ValueError):
            continue
        if value > 0:
            spreads.append(value)
    return spreads


def mc2_base_spread(root: ET.Element | None) -> float:
    spreads = positive_chart_spreads(root)
    return min(spreads) if spreads else 0.0


def mc2_spread_target(root: ET.Element | None) -> dict[str, Any]:
    base = mc2_base_spread(root)
    spread_min = round(base * MC2_SPREAD_MIN_MULTIPLIER, 2) if base else 0.0
    spread_max = round(base * MC2_SPREAD_MAX_MULTIPLIER, 2) if base else 0.0
    return {
        "baseSpread": base,
        "minMultiplier": MC2_SPREAD_MIN_MULTIPLIER,
        "maxMultiplier": MC2_SPREAD_MAX_MULTIPLIER,
        "min": _format_decimal(spread_min, "0"),
        "max": _format_decimal(spread_max, "0"),
        "ratioMinToBase": round(spread_min / base, 2) if base else None,
        "ratioMaxToBase": round(spread_max / base, 2) if base else None,
    }


def method_params(method: ET.Element | None) -> dict[str, str]:
    if method is None:
        return {}
    return {
        param.get("key", ""): (param.text or "")
        for param in method.findall("./Params/Param")
        if param.get("key")
    }


def mc2_crosschecks_summary(root: ET.Element) -> dict[str, Any]:
    parent = find_section(root, "CrossChecks")
    target = mc2_spread_target(root)
    checks: list[dict[str, Any]] = []
    if parent is not None:
        for check in list(parent):
            if not isinstance(check.tag, str) or check.get("use") is None:
                continue
            methods = []
            for method in check.findall("./Settings/Methods/Method"):
                params = method_params(method)
                row: dict[str, Any] = {
                    "type": method.get("type", ""),
                    "use": method.get("use", ""),
                    "params": params,
                }
                if method.get("type") == "RandomizeSpread":
                    try:
                        spread_min = float(params.get("Min") or 0)
                        spread_max = float(params.get("Max") or 0)
                    except (TypeError, ValueError):
                        spread_min = 0.0
                        spread_max = 0.0
                    base = float(target.get("baseSpread") or 0)
                    row.update({
                        "ratioMinToBase": round(spread_min / base, 2) if base else None,
                        "ratioMaxToBase": round(spread_max / base, 2) if base else None,
                    })
                methods.append(row)
            checks.append({
                "id": check.tag,
                "use": check.get("use", ""),
                "numberOfSimulations": check.findtext("./Settings/NumberOfSimulations") or "",
                "mcUseFullSample": check.findtext("./Settings/MCUseFullSample") or "",
                "methods": methods,
                "activeMethodTypes": [
                    method.get("type", "")
                    for method in check.findall("./Settings/Methods/Method")
                    if method.get("use") == "true"
                ],
                "activeAcceptanceConditionCount": len([
                    condition
                    for condition in check.findall("./AcceptanceSettings/Conditions/Condition")
                    if condition.get("use", "true") != "false"
                ]),
            })
    return {
        "crossChecks": {
            "exists": parent is not None,
            "attrs": dict(parent.attrib) if parent is not None else {},
            "active": [item["id"] for item in checks if item.get("use") == "true"],
            "checks": checks,
            "sha256": section_sha256(root, "CrossChecks"),
        },
        "spreadTarget": target,
        "chartSpreads": positive_chart_spreads(root),
    }


def apply_mc2_crosschecks_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    parent = find_section(root, "CrossChecks")
    if parent is None:
        parent = ET.SubElement(root, "CrossChecks")
        actions.append({"field": "CrossChecks", "from": None, "to": dict(parent.attrib), "changed": True})
    set_attrs_on_node(parent, {"use": "true", "evaluateAll": "true"}, actions, "CrossChecks:attrs")

    target = mc2_spread_target(root)
    active_check = parent.find(MC2_ACTIVE_CHECK)
    if active_check is None:
        active_check = ET.SubElement(parent, MC2_ACTIVE_CHECK, {"use": "true"})
        actions.append({"field": f"CrossChecks/{MC2_ACTIVE_CHECK}", "from": None, "to": dict(active_check.attrib), "changed": True})

    for check in list(parent):
        if not isinstance(check.tag, str) or check.get("use") is None:
            continue
        before_use = check.get("use")
        target_use = "true" if check.tag == MC2_ACTIVE_CHECK else "false"
        check.set("use", target_use)
        actions.append({
            "field": f"CrossChecks/{check.tag}:use",
            "from": before_use,
            "to": target_use,
            "changed": before_use != target_use,
        })
        for method in check.findall("./Settings/Methods/Method"):
            method_type = method.get("type", "")
            wanted = "true" if check.tag == MC2_ACTIVE_CHECK and method_type in MC2_ACTIVE_METHODS else "false"
            before_method = method.get("use")
            method.set("use", wanted)
            actions.append({
                "field": f"CrossChecks/{check.tag}/Method:{method_type}:use",
                "from": before_method,
                "to": wanted,
                "changed": before_method != wanted,
            })

    settings = ensure_direct_child(active_check, "Settings")
    for tag, wanted in (("NumberOfSimulations", MC2_NUMBER_OF_SIMULATIONS), ("MCUseFullSample", MC2_USE_FULL_SAMPLE)):
        node = ensure_direct_child(settings, tag)
        before = node.text or ""
        node.text = wanted
        actions.append({"field": f"CrossChecks/{MC2_ACTIVE_CHECK}/Settings/{tag}", "from": before, "to": wanted, "changed": before != wanted})

    methods = ensure_direct_child(settings, "Methods")
    randomize_spread = None
    for method in methods.findall("Method"):
        if method.get("type") == "RandomizeSpread":
            randomize_spread = method
            break
    if randomize_spread is None:
        randomize_spread = ET.SubElement(methods, "Method", {"type": "RandomizeSpread", "use": "true"})
        actions.append({"field": f"CrossChecks/{MC2_ACTIVE_CHECK}/Method:RandomizeSpread", "from": None, "to": dict(randomize_spread.attrib), "changed": True})
    randomize_spread.set("use", "true")
    set_method_param(randomize_spread, "Min", str(target["min"]), "Double", actions, f"CrossChecks/{MC2_ACTIVE_CHECK}/RandomizeSpread/Min")
    set_method_param(randomize_spread, "Max", str(target["max"]), "Double", actions, f"CrossChecks/{MC2_ACTIVE_CHECK}/RandomizeSpread/Max")
    return actions


def mc2_acceptance_conditions_ok(root: ET.Element) -> bool:
    check = root.find(f".//CrossChecks/{MC2_ACTIVE_CHECK}")
    if check is None:
        return False
    conditions = [
        condition
        for condition in check.findall("./AcceptanceSettings/Conditions/Condition")
        if condition.get("use", "true") != "false"
    ]
    if len(conditions) != 2:
        return False
    numeric = conditions[0].find("./Right-Side/Numeric-Value")
    left0 = conditions[0].find("./Left-Side/Column-Value")
    left1 = conditions[1].find("./Left-Side/Column-Value")
    right1 = conditions[1].find("./Right-Side/Column-Value")
    comp0 = conditions[0].find("./Comparator")
    comp1 = conditions[1].find("./Comparator")
    return bool(
        left0 is not None
        and left0.get("column") == "AnnualPctReturnDDRatio"
        and left0.get("resultType") == "MonteCarloRetest"
        and left0.get("confidenceLevel") == "100"
        and comp0 is not None
        and comp0.get("value") == ">="
        and numeric is not None
        and numeric.get("value") == "0"
        and left1 is not None
        and left1.get("column") == "AnnualPctReturnDDRatio"
        and left1.get("resultType") == "MonteCarloRetest"
        and left1.get("confidenceLevel") == "95"
        and comp1 is not None
        and comp1.get("value") == ">="
        and right1 is not None
        and right1.get("column") == "AnnualPctReturnDDRatio"
        and right1.get("resultType") == "main"
        and right1.get("pctRatio") == "30"
    )


def enforce_mc2_crosschecks_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = mc2_crosschecks_summary(root)
    cross = summary.get("crossChecks") or {}
    attrs = cross.get("attrs") or {}
    if attrs.get("use") != "true" or attrs.get("evaluateAll") != "true":
        issues.append(f"MC2 CrossChecks attrs are {attrs!r}, expected use/evaluateAll true")
    if cross.get("active") != [MC2_ACTIVE_CHECK]:
        issues.append(f"MC2 active crosschecks are {cross.get('active')!r}, expected [{MC2_ACTIVE_CHECK!r}]")
    checks = {item.get("id"): item for item in cross.get("checks") or []}
    active = checks.get(MC2_ACTIVE_CHECK) or {}
    if active.get("numberOfSimulations") != MC2_NUMBER_OF_SIMULATIONS:
        issues.append(f"MC2 NumberOfSimulations is {active.get('numberOfSimulations')!r}, expected {MC2_NUMBER_OF_SIMULATIONS!r}")
    if active.get("mcUseFullSample") != MC2_USE_FULL_SAMPLE:
        issues.append(f"MC2 MCUseFullSample is {active.get('mcUseFullSample')!r}, expected {MC2_USE_FULL_SAMPLE!r}")
    if set(active.get("activeMethodTypes") or []) != MC2_ACTIVE_METHODS:
        issues.append(f"MC2 active methods are {active.get('activeMethodTypes')!r}, expected {sorted(MC2_ACTIVE_METHODS)!r}")
    methods = {item.get("type"): item for item in active.get("methods") or []}
    spread = methods.get("RandomizeSpread") or {}
    params = spread.get("params") or {}
    target = summary.get("spreadTarget") or {}
    if not target.get("baseSpread"):
        issues.append("MC2 base spread could not be resolved from task charts")
    if params.get("Min") != target.get("min") or params.get("Max") != target.get("max"):
        issues.append(f"MC2 RandomizeSpread range is {(params.get('Min'), params.get('Max'))!r}, expected {(target.get('min'), target.get('max'))!r}")
    if spread.get("ratioMinToBase") != target.get("ratioMinToBase") or spread.get("ratioMaxToBase") != target.get("ratioMaxToBase"):
        issues.append("MC2 RandomizeSpread ratios drifted from baseSpread x2-x5")
    if spread.get("ratioMaxToBase") is not None and spread.get("ratioMaxToBase") >= 10:
        issues.append("MC2 RandomizeSpread is extreme versus base spread; expected x2-x5, not >= x10")
    for check in cross.get("checks") or []:
        if check.get("id") == MC2_ACTIVE_CHECK:
            continue
        active_methods = [method for method in check.get("methods") or [] if method.get("use") == "true"]
        if active_methods:
            issues.append(f"Inactive MC2 crosscheck {check.get('id')} still has active methods: {[item.get('type') for item in active_methods]}")
    if not mc2_acceptance_conditions_ok(root):
        issues.append("MC2 acceptance conditions drifted from AnnualPctReturnDDRatio >= 0 and >= 30% main")
    return issues


def update_mc2_crosschecks_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload
    task_xml_name, root = load_task_root(cfx, MC2_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "mc2_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload
    before_text = serialize_xml(root)
    payload["before"] = mc2_crosschecks_summary(root)
    payload["actions"] = apply_mc2_crosschecks_to_root(root)
    payload["after"] = mc2_crosschecks_summary(root)
    payload["issues"] = enforce_mc2_crosschecks_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "activeCheck": MC2_ACTIVE_CHECK,
        "activeMethods": sorted(MC2_ACTIVE_METHODS),
        "numberOfSimulations": MC2_NUMBER_OF_SIMULATIONS,
        "mcUseFullSample": MC2_USE_FULL_SAMPLE,
        "spreadPolicy": "adaptive_base_spread_x2_to_x5",
        "minMultiplier": MC2_SPREAD_MIN_MULTIPLIER,
        "maxMultiplier": MC2_SPREAD_MAX_MULTIPLIER,
    }
    payload["targetRationale"] = {
        "academic": "Transaction costs and bid-ask spread are real frictions; stress testing is useful, but repeated tuning against validation data increases data-snooping/backtest-overfitting risk. x2-x5 is a local, evidence-backed heuristic, not a universal theorem.",
        "localEvidence": "Original 30-50 spread stress was extreme versus the base spread and previously produced 0 passed / 86 failed; x2-x5 restored natural 84 passed / 2 failed without forcing results.",
        "generatorOwned": "Project Generator must recalculate the absolute Min/Max from the selected asset spread.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_mc2_crosschecks_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase7_mc2_crosschecks_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_mc2_crosschecks_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase7",
        "operation": "mc2_crosschecks_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase7_mc2_crosschecks_diff_review" if not apply else "phase7_mc2_next_block",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase7_mc2_crosschecks_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def mc2_custom_data_summary(root: ET.Element) -> dict[str, Any]:
    custom = find_section(root, "CustomData")
    setup = custom.find("./Setups/Setup") if custom is not None else None
    chart = setup.find("Chart") if setup is not None else None
    main_values = setup.find("MainTestValues") if setup is not None else None
    commission = setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']") if setup is not None else None
    return {
        "exists": custom is not None,
        "attrs": dict(custom.attrib) if custom is not None else {},
        "setup": dict(setup.attrib) if setup is not None else {},
        "chart": dict(chart.attrib) if chart is not None else {},
        "mainTestValues": dict(main_values.attrib) if main_values is not None else {},
        "commission": commission.text if commission is not None else "",
        "sha256": section_sha256(root, "CustomData"),
    }


def mc2_data_databanks_resources_options_summary(root: ET.Element) -> dict[str, Any]:
    databanks = {
        node.get("name", ""): node.get("value", "")
        for node in root.findall(".//Databanks/Databank")
        if node.get("name")
    }
    params = {
        param.get("key", ""): (param.text or "")
        for param in root.findall(".//BuildTradingOptions/Params/Param")
        if param.get("key") in MC2_OPTIONS_PARAMS_TARGET
    }
    return {
        "data": {
            "exists": root.find("Data") is not None,
            "outOfSampleRanges": [dict(node.attrib) for node in root.findall(".//Data/OutOfSample/Range")],
        },
        "customData": mc2_custom_data_summary(root),
        "databanks": databanks,
        "resources": _tick_real_resource_summary(root),
        "optionsParams": params,
    }


def apply_mc2_custom_data_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> ET.Element | None:
    data = root.find("Data")
    if data is not None:
        before = {"sha256": section_sha256(data, "Data"), "children": [child.tag for child in list(data)]}
        root.remove(data)
        actions.append({
            "field": "Data",
            "from": before,
            "to": None,
            "changed": True,
            "note": "MC2 uses CustomData as its data carrier; keeping a Data section would create two sources of truth.",
        })
    custom = find_section(root, "CustomData")
    if custom is None:
        custom = ET.SubElement(root, "CustomData")
        actions.append({"field": "CustomData", "from": None, "to": "created", "changed": True})
    setups = ensure_direct_child(custom, "Setups")
    setup = setups.find("Setup")
    if setup is None:
        setup = ET.SubElement(setups, "Setup")
        actions.append({"field": "CustomData/Setup", "from": None, "to": dict(setup.attrib), "changed": True})

    period = generator_period(MC2_PERIOD_KEY)
    set_attrs_on_node(
        setup,
        {
            "dateFrom": period[0],
            "dateTo": period[1],
            "testPrecision": MC2_DATA_TEST_PRECISION,
            "session": MC2_DATA_SESSION,
            "slippage": "0",
            "minDist": "0",
            "engine": "MetaTrader4",
        },
        actions,
        "CustomData/Setup:attrs",
    )

    chart = setup.find("Chart")
    if chart is None:
        chart = ET.SubElement(setup, "Chart")
        actions.append({"field": "CustomData/Setup/Chart", "from": None, "to": dict(chart.attrib), "changed": True})
    set_attrs_on_node(chart, MC2_DEFAULT_CHART_TARGET, actions, "CustomData/Setup/Chart:attrs")

    commissions = ensure_direct_child(setup, "Commissions")
    existing_methods = {
        method.get("type", ""): method
        for method in commissions.findall("Method")
        if method.get("type")
    }
    for method_type, use in {"None": "false", "SizeBased": "true"}.items():
        method = existing_methods.get(method_type)
        if method is None:
            method = ET.SubElement(commissions, "Method", {"type": method_type})
            before = None
        else:
            before = dict(method.attrib)
        method.set("type", method_type)
        method.set("use", use)
        actions.append({
            "field": f"CustomData/Commissions/Method:{method_type}",
            "from": before,
            "to": dict(method.attrib),
            "changed": before != dict(method.attrib),
        })
        if method_type == "SizeBased":
            params = ensure_direct_child(method, "Params")
            param = None
            for candidate in params.findall("Param"):
                if candidate.get("key") == "Commission":
                    param = candidate
                    break
            if param is None:
                param = ET.SubElement(params, "Param", {"key": "Commission", "className": "SizeBased"})
                before_param = None
            else:
                before_param = {**dict(param.attrib), "text": param.text or ""}
            param.set("key", "Commission")
            param.set("className", "SizeBased")
            param.text = MC_CUSTOM_DATA_COMMISSION_TARGET
            after_param = {**dict(param.attrib), "text": param.text or ""}
            actions.append({
                "field": "CustomData/Commissions/Method:SizeBased/Param:Commission",
                "from": before_param,
                "to": after_param,
                "changed": before_param != after_param,
            })

    main_values = setup.find("MainTestValues")
    if main_values is None:
        main_values = ET.SubElement(setup, "MainTestValues")
        actions.append({"field": "CustomData/MainTestValues", "from": None, "to": dict(main_values.attrib), "changed": True})
    set_attrs_on_node(main_values, MC2_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET, actions, "CustomData/MainTestValues:attrs")
    return setup


def apply_mc2_resources_from_custom_data(root: ET.Element, setup: ET.Element | None, actions: list[dict[str, Any]]) -> None:
    resources = find_section(root, "Resources")
    if resources is None:
        resources = ET.SubElement(root, "Resources")
        before_resources: dict[str, Any] = {"resourcesFound": False}
    else:
        before_resources = _tick_real_resource_summary(root)

    if setup is None:
        actions.append({"field": "Resources", "error": "missing_custom_data_setup", "changed": False})
        return

    charts = setup.findall("Chart")
    if not charts:
        chart = ET.SubElement(setup, "Chart", MC2_DEFAULT_CHART_TARGET)
        charts = [chart]
        actions.append({"field": "CustomData/Setup/Chart", "from": None, "to": dict(chart.attrib), "changed": True})
    chart_by_symbol = {
        chart.get("symbol", ""): chart
        for chart in charts
        if chart.get("symbol")
    }
    symbols_node = ensure_resources_container(resources, "Symbols")
    brokers_node = ensure_resources_container(resources, "Brokers")
    instruments_node = ensure_resources_container(resources, "Instruments")
    sessions_node = ensure_resources_container(resources, "Sessions")
    ensure_resources_container(resources, "CustomIndicators")
    ensure_resources_container(resources, "CustomBlocks")

    template_symbol_attrs, template_info_attrs = _first_existing_symbol_template(resources)
    existing_symbols = {
        symbol.get("name", ""): symbol
        for symbol in symbols_node.findall("Symbol")
        if symbol.get("name")
    }
    before_symbols = [value_for_node(symbol) for symbol in symbols_node.findall("Symbol")]
    for symbol in list(symbols_node.findall("Symbol")):
        symbols_node.remove(symbol)

    referenced_brokers: set[str] = set()
    period = generator_period(MC2_PERIOD_KEY)
    date_from_default = str(epoch_ms_for_date(period[0]))
    date_to_default = str(epoch_ms_for_date(period[1]))
    for symbol_name, chart in chart_by_symbol.items():
        existing_symbol = existing_symbols.get(symbol_name)
        symbol_attrs = dict(existing_symbol.attrib) if existing_symbol is not None else dict(template_symbol_attrs)
        existing_info = existing_symbol.find("InstrumentInfo") if existing_symbol is not None else None
        info_attrs = dict(existing_info.attrib) if existing_info is not None else dict(template_info_attrs)
        broker_id = symbol_attrs.get("broker") or info_attrs.get("broker") or MC_DEFAULT_BROKER_ID
        source_id = symbol_attrs.get("source") or MC_DEFAULT_SOURCE_ID
        bounded_from, bounded_to = bounded_period_ms(
            period,
            symbol_attrs.get("dateFrom") or date_from_default,
            symbol_attrs.get("dateTo") or date_to_default,
        )
        asset = _asset_from_tick_real_symbol(symbol_name)
        referenced_brokers.add(broker_id)
        symbol_node = ET.SubElement(symbols_node, "Symbol", {
            "name": symbol_name,
            "source": source_id,
            "barType": symbol_attrs.get("barType", "1"),
            "precision": MC_RESOURCE_PRECISION,
            "timezone": MC_RESOURCE_TIMEZONE,
            "dateFrom": bounded_from,
            "dateTo": bounded_to,
            "uSymbol": symbol_attrs.get("uSymbol") or asset,
            "uSymbolName": symbol_attrs.get("uSymbolName") or asset,
            "removeWeekends": symbol_attrs.get("removeWeekends", "false"),
            "broker": broker_id,
        })
        info_attrs.update({
            "instrument": symbol_name,
            "defaultSpread": chart.get("spread", info_attrs.get("defaultSpread", "")),
            "dateFrom": "0",
            "dateTo": "0",
            "rows": "0",
            "totalDays": "0",
            "dataType": info_attrs.get("dataType", BUILD_RESOURCES_BASE_DATA_TYPE),
            "broker": broker_id,
        })
        ET.SubElement(symbol_node, "InstrumentInfo", info_attrs)

    after_symbols = [value_for_node(symbol) for symbol in symbols_node.findall("Symbol")]
    actions.append({
        "field": "Resources/Symbols",
        "from": before_symbols,
        "to": after_symbols,
        "changed": before_symbols != after_symbols,
    })

    before_brokers = [value_for_node(broker) for broker in brokers_node.findall("Broker")]
    existing_brokers = {
        broker.get("id", ""): broker
        for broker in brokers_node.findall("Broker")
        if broker.get("id")
    }
    for broker in list(brokers_node.findall("Broker")):
        if broker.get("id") not in referenced_brokers:
            brokers_node.remove(broker)
    for broker_id in sorted(referenced_brokers):
        if broker_id in existing_brokers and existing_brokers[broker_id] in list(brokers_node):
            continue
        ET.SubElement(brokers_node, "Broker", {
            "id": broker_id,
            "name": "[[Darwinex]]" if broker_id == MC_DEFAULT_BROKER_ID else f"Broker {broker_id}",
            "description": "Darwinex CFDs" if broker_id == MC_DEFAULT_BROKER_ID else "",
            "timezone": MC_RESOURCE_TIMEZONE,
            "postfix": "_darwinex" if broker_id == MC_DEFAULT_BROKER_ID else "",
            "mtUse": "true",
            "spUse": "false",
        })
    after_brokers = [value_for_node(broker) for broker in brokers_node.findall("Broker")]
    actions.append({
        "field": "Resources/Brokers",
        "from": before_brokers,
        "to": after_brokers,
        "changed": before_brokers != after_brokers,
    })

    before_instruments = [value_for_node(node) for node in instruments_node.findall("InstrumentInfo")]
    for node in list(instruments_node.findall("InstrumentInfo")):
        instruments_node.remove(node)
    for symbol in symbols_node.findall("Symbol"):
        info = symbol.find("InstrumentInfo")
        ET.SubElement(instruments_node, "InstrumentInfo", dict(info.attrib) if info is not None else {})
    after_instruments = [value_for_node(node) for node in instruments_node.findall("InstrumentInfo")]
    actions.append({
        "field": "Resources/Instruments",
        "from": before_instruments,
        "to": after_instruments,
        "changed": before_instruments != after_instruments,
    })

    removed_sessions = [value_for_node(node) for node in sessions_node.findall("Session")]
    for node in list(sessions_node.findall("Session")):
        sessions_node.remove(node)
    actions.append({
        "field": "Resources/Sessions",
        "from": removed_sessions,
        "to": [],
        "changed": bool(removed_sessions),
    })
    actions.append({
        "field": "Resources",
        "from": before_resources,
        "to": _tick_real_resource_summary(root),
        "changed": before_resources != _tick_real_resource_summary(root),
        "note": "CustomIndicators and CustomBlocks are preserved; Project Generator owns final resource rebuild per asset/timeframe.",
    })


def apply_mc2_data_databanks_resources_options_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    setup = apply_mc2_custom_data_to_root(root, actions)

    databanks = find_section(root, "Databanks")
    if databanks is None:
        databanks = ET.SubElement(root, "Databanks", {"retestSelected": "false"})
        actions.append({"field": "Databanks", "from": None, "to": dict(databanks.attrib), "changed": True})
    existing_by_name = {
        node.get("name", ""): node
        for node in databanks.findall("Databank")
        if node.get("name")
    }
    for name, wanted in MC2_DATABANKS_TARGET.items():
        node = existing_by_name.get(name)
        if node is None:
            node = ET.SubElement(databanks, "Databank", {"name": name})
            before = None
        else:
            before = dict(node.attrib)
        node.set("name", name)
        node.set("value", wanted)
        node.set("label", f"{name} databank")
        actions.append({
            "field": f"Databanks/{name}",
            "from": before,
            "to": dict(node.attrib),
            "changed": before != dict(node.attrib),
        })

    apply_mc2_resources_from_custom_data(root, setup, actions)
    for key, value in MC2_OPTIONS_PARAMS_TARGET.items():
        set_param_text(root, key, value, actions, "Options")
    return actions


def enforce_mc2_data_databanks_resources_options_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    period = generator_period(MC2_PERIOD_KEY)
    if root.find("Data") is not None:
        issues.append("MC2 must not carry a Data section; CustomData is the canonical data carrier for this task")

    custom = find_section(root, "CustomData")
    setup = custom.find("./Setups/Setup") if custom is not None else None
    if setup is None:
        issues.append("MC2 CustomData/Setup missing")
    else:
        if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
            issues.append("MC2 CustomData dates are not ROBUSTNESS_C1")
        if setup.get("testPrecision") != MC2_DATA_TEST_PRECISION:
            issues.append("MC2 CustomData testPrecision must stay 2 for fast/simulated Monte Carlo")
        if setup.get("session") != MC2_DATA_SESSION:
            issues.append("MC2 CustomData session must stay No Session")
        chart = setup.find("Chart")
        if chart is None:
            issues.append("MC2 CustomData chart missing")
        main_values = setup.find("MainTestValues")
        main_attrs = dict(main_values.attrib) if main_values is not None else {}
        if main_attrs != MC2_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET:
            issues.append("MC2 CustomData MainTestValues drifted from full-retarget target")
        commission = setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']")
        if (commission.text if commission is not None else "") != MC_CUSTOM_DATA_COMMISSION_TARGET:
            issues.append(f"MC2 CustomData commission is {(commission.text if commission is not None else '')!r}, expected {MC_CUSTOM_DATA_COMMISSION_TARGET!r}")

    databanks = {
        node.get("name", ""): node.get("value", "")
        for node in root.findall(".//Databanks/Databank")
        if node.get("name")
    }
    for name, wanted in MC2_DATABANKS_TARGET.items():
        if databanks.get(name) != wanted:
            issues.append(f"MC2 Databank {name} is {databanks.get(name)!r}, expected {wanted!r}")

    resources = find_section(root, "Resources")
    if resources is None:
        issues.append("MC2 Resources missing")
    else:
        chart_symbols = {
            chart.get("symbol", "")
            for chart in root.findall("./CustomData/Setups/Setup/Chart")
            if chart.get("symbol")
        }
        resource_symbols = {
            symbol.get("name", "")
            for symbol in resources.findall("./Symbols/Symbol")
            if symbol.get("name")
        }
        if chart_symbols != resource_symbols:
            issues.append(f"MC2 custom chart/resource mismatch: charts={sorted(chart_symbols)} resources={sorted(resource_symbols)}")
        broker_ids = {
            broker.get("id", "")
            for broker in resources.findall("./Brokers/Broker")
            if broker.get("id")
        }
        for symbol in resources.findall("./Symbols/Symbol"):
            if symbol.get("precision") != MC_RESOURCE_PRECISION:
                issues.append(f"MC2 resource {symbol.get('name')} precision is not TICK")
            if symbol.get("timezone") != MC_RESOURCE_TIMEZONE:
                issues.append(f"MC2 resource {symbol.get('name')} timezone is not EETUS")
            if symbol.get("broker") not in broker_ids:
                issues.append(f"MC2 resource {symbol.get('name')} references missing broker {symbol.get('broker')}")
            info = symbol.find("InstrumentInfo")
            if info is None:
                issues.append(f"MC2 resource {symbol.get('name')} has no nested InstrumentInfo")
            elif info.get("broker") not in broker_ids:
                issues.append(f"MC2 nested InstrumentInfo for {symbol.get('name')} references missing broker {info.get('broker')}")
        if resources.findall("./Sessions/Session"):
            issues.append("MC2 resources must not keep session entries")

    params = {
        param.get("key", ""): (param.text or "")
        for param in root.findall(".//BuildTradingOptions/Params/Param")
        if param.get("key") in MC2_OPTIONS_PARAMS_TARGET
    }
    for key, wanted in MC2_OPTIONS_PARAMS_TARGET.items():
        if params.get(key) != wanted:
            issues.append(f"MC2 Options param {key} is {params.get(key)!r}, expected {wanted!r}")

    guarded_text = (
        section_text(root, "Data")
        + section_text(root, "CustomData")
        + section_text(root, "Databanks")
        + section_text(root, "Resources")
        + section_text(root, "Options")
    )
    for token in MC_BANNED_DONOR_TOKENS:
        if token in guarded_text:
            issues.append(f"Forbidden donor token leaked into MC2 Data/Databanks/Resources/Options: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into MC2 Data/Databanks/Resources/Options")
    return issues


def update_mc2_data_databanks_resources_options_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload
    task_xml_name, root = load_task_root(cfx, MC2_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "mc2_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = mc2_data_databanks_resources_options_summary(root)
    payload["actions"] = apply_mc2_data_databanks_resources_options_to_root(root)
    payload["after"] = mc2_data_databanks_resources_options_summary(root)
    payload["issues"] = enforce_mc2_data_databanks_resources_options_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["xmlChanged"] = before_text != after_text
    payload["changed"] = payload["changedActionCount"] > 0
    payload["targetValues"] = {
        "taskTitle": MC2_TASK_TITLE,
        "periodKey": MC2_PERIOD_KEY,
        "dateFrom": generator_period(MC2_PERIOD_KEY)[0],
        "dateTo": generator_period(MC2_PERIOD_KEY)[1],
        "dataSection": "absent",
        "customData": {
            "testPrecision": MC2_DATA_TEST_PRECISION,
            "session": MC2_DATA_SESSION,
            "mainTestValues": MC2_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET,
        },
        "databanks": MC2_DATABANKS_TARGET,
        "resourcePrecision": MC_RESOURCE_PRECISION,
        "resourceTimezone": MC_RESOURCE_TIMEZONE,
        "options": MC2_OPTIONS_PARAMS_TARGET,
    }
    payload["targetRationale"] = {
        "methodology": "MC2 is a second Monte Carlo robustness gate after MC; it consumes MC and writes MC2 without adding a new OOS split.",
        "customDataCarrier": "This SQX automatic retest stores its data setup in CustomData, so no parallel Data section is allowed.",
        "generatorOwned": "Symbol, timeframe, spread, swap and final resources remain owned by Project Generator for each selected asset/timeframe.",
        "naturalResults": "This block preserves natural passed/failed rows and does not force Results=passed.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_mc2_data_databanks_resources_options_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase7_mc2_data_databanks_resources_options_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_mc2_data_databanks_resources_options_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase7",
        "operation": "mc2_data_databanks_resources_options_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase7_mc2_data_databanks_resources_options_diff_review" if not apply else "phase7_mc2_passive_or_static_review",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase7_mc2_data_databanks_resources_options_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def apply_mc2_what_to_build_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    what_to_build = find_section(root, "WhatToBuild")
    if what_to_build is None:
        what_to_build = ET.SubElement(root, "WhatToBuild")
        actions.append({"field": "WhatToBuild", "from": None, "to": "created", "changed": True})

    set_or_create_attrs_child(
        what_to_build,
        "StrategyType",
        MC2_STRATEGY_TYPE_TARGET,
        actions,
        "WhatToBuild/StrategyType",
    )
    build_mode = what_to_build.find("BuildMode")
    if build_mode is None:
        build_mode = ET.SubElement(what_to_build, "BuildMode", {"generationType": "random-generation"})
        actions.append({"field": "WhatToBuild/BuildMode", "from": None, "to": dict(build_mode.attrib), "changed": True})
    else:
        actions.append({
            "field": "WhatToBuild/BuildMode:generationType",
            "from": build_mode.get("generationType", ""),
            "to": build_mode.get("generationType", ""),
            "changed": False,
            "note": "left as SQX-known placeholder; MC2 passive behavior is enforced by input databank, disabled improve parts and disabled evolution toggles",
        })
    for tag, value in MC2_PASSIVE_BUILDMODE_TEXT_TARGET.items():
        set_or_create_text_child(build_mode, tag, value, actions, f"WhatToBuild/BuildMode/{tag}")
    for tag, attrs in MC2_PASSIVE_BUILDMODE_ATTR_TARGET.items():
        set_or_update_attrs_child(build_mode, tag, attrs, actions, f"WhatToBuild/BuildMode/{tag}")


def apply_mc2_blocks_to_root(root: ET.Element, source_root: ET.Element | None, actions: list[dict[str, Any]]) -> None:
    blocks = find_blocks(root)
    if blocks is None:
        blocks = ET.SubElement(root, "Blocks", {"type": "simple", "version": "142.2336"})
        actions.append({"field": "Blocks", "from": None, "to": dict(blocks.attrib), "changed": True})

    before_attrs = dict(blocks.attrib)
    blocks.set("type", "simple")
    blocks.set("version", "142.2336")
    actions.append({
        "field": "Blocks:attrs",
        "from": before_attrs,
        "to": dict(blocks.attrib),
        "changed": before_attrs != dict(blocks.attrib),
    })

    source_blocks = find_blocks(source_root)
    if blocks.find("BuildingBlocks") is None and source_blocks is not None:
        actions.append(replace_building_blocks_from_source(blocks, source_blocks))
    else:
        actions.append({
            "field": "BuildingBlocks",
            "changed": False,
            "note": "preserved existing MC2 building-block universe; passive gate only enforces no-improve, entry and exit contracts",
        })
    if source_blocks is not None:
        for child_name in ("OrderTypes", "ExitTypes"):
            if blocks.find(child_name) is None and source_blocks.find(child_name) is not None:
                blocks.append(ET.fromstring(serialize_xml(source_blocks.find(child_name))))
                actions.append({
                    "field": child_name,
                    "from": None,
                    "to": "copied_from_mc_source",
                    "changed": True,
                    "note": "MC2 had no explicit passive block controls; copied the existing MC source controls before enforcing the methodology contract.",
                })
    enforce_order_types(blocks, actions)
    enforce_exit_types(blocks, actions)
    enforce_external_custom_data(blocks, actions)
    enforce_disabled_build_block_categories(blocks, actions)


def apply_mc2_passive_generation_to_root(root: ET.Element, source_root: ET.Element | None) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    apply_retest1_parts_to_improve_to_root(root, actions)
    apply_mc2_what_to_build_to_root(root, actions)
    apply_mc2_blocks_to_root(root, source_root, actions)
    return actions


def mc2_passive_generation_summary(root: ET.Element) -> dict[str, Any]:
    return retest1_passive_generation_summary(root)


def enforce_mc2_passive_generation_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = mc2_passive_generation_summary(root)
    parts = summary.get("partsToImprove") or {}
    for group_name in ("EntryRules", "OrderTypes", "ExitRules"):
        group = parts.get(group_name) or {}
        for side in ("LongImprovement", "ShortImprovement"):
            if (group.get(side) or {}).get("use") != "false":
                issues.append(f"MC2 {group_name}/{side} must be passive use=false")
    if summary.get("strategyType") != MC2_STRATEGY_TYPE_TARGET:
        issues.append("MC2 StrategyType must point passively to MC with known SQX attributes")
    build_mode = summary.get("buildMode") or {}
    build_text = build_mode.get("text") or {}
    for tag, value in MC2_PASSIVE_BUILDMODE_TEXT_TARGET.items():
        if build_text.get(tag) != value:
            issues.append(f"MC2 BuildMode {tag} is {build_text.get(tag)!r}, expected {value!r}")
    child_attrs = build_mode.get("childAttrs") or {}
    for tag, attrs in MC2_PASSIVE_BUILDMODE_ATTR_TARGET.items():
        current = child_attrs.get(tag) or {}
        for key, value in attrs.items():
            if current.get(key) != value:
                issues.append(f"MC2 BuildMode {tag}.{key} is {current.get(key)!r}, expected {value!r}")
    blocks = summary.get("blocks") or {}
    expected_order = BUILD_ORDER_TYPE_TARGET
    actual_order = {key: blocks.get("orderTypes", {}).get(key) for key in expected_order}
    if actual_order != expected_order:
        issues.append(f"MC2 order types are {actual_order!r}, expected {expected_order!r}")
    exits = blocks.get("exitTypes") or {}
    if exits.get(BUILD_EXIT_TYPE_ACTIVE_KEY, {}).get("use") != "true":
        issues.append("MC2 must keep only ExitAfterBars active")
    if exits.get(BUILD_EXIT_TYPE_ACTIVE_KEY, {}).get("probability") != "100":
        issues.append("MC2 ExitAfterBars probability must be 100")
    active_other_exits = [
        key for key, data in exits.items()
        if key != BUILD_EXIT_TYPE_ACTIVE_KEY and (data or {}).get("use") == "true"
    ]
    if active_other_exits:
        issues.append(f"MC2 has non-passive active exit types: {active_other_exits}")
    if any(any(token in key for token in BUILD_EXIT_TYPE_BANNED_TOKENS) for key in exits):
        issues.append("MC2 contains day-based exit types")
    if int(blocks.get("activeSignalCount") or 0) != 0:
        issues.append("MC2 signals must remain disabled in passive retest")
    if int(blocks.get("activeStopLimitCount") or 0) != 0:
        issues.append("MC2 stop/limit entry blocks must remain disabled in passive retest")
    if int(blocks.get("activeIndicatorCount") or 0) <= 0:
        issues.append("MC2 must preserve methodology/BlockSettings indicator blocks")
    custom = blocks.get("customData") or {}
    if (custom.get("attrs") or {}).get("showAll") != "false" or custom.get("children") != 0:
        issues.append("MC2 external CustomData must stay disabled and empty")
    guarded_sections = [
        find_section(root, "PartsToImprove"),
        find_section(root, "WhatToBuild"),
        find_section(root, "Blocks"),
    ]
    guarded_text = "".join(serialize_xml(section if section is not None else root) for section in guarded_sections)
    for token in ("ExitAfterDays", "ExitAfterTradingDays", "USDJPY_darwinex", "USDJPY_dukascopy"):
        if token in guarded_text:
            issues.append(f"Forbidden token leaked into MC2 passive generation tabs: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into MC2 passive generation tabs")
    return issues


def update_mc2_passive_generation_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, MC2_TASK_TITLE)
    source_task_xml_name, source_root = load_task_root(cfx, MC2_PASSIVE_SOURCE_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    payload["sourceTaskXml"] = source_task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "mc2_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload
    if not source_task_xml_name or source_root is None:
        payload["error"] = "mc2_source_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = mc2_passive_generation_summary(root)
    payload["actions"] = apply_mc2_passive_generation_to_root(root, source_root)
    payload["after"] = mc2_passive_generation_summary(root)
    payload["issues"] = enforce_mc2_passive_generation_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "strategyType": MC2_STRATEGY_TYPE_TARGET,
        "buildModeText": MC2_PASSIVE_BUILDMODE_TEXT_TARGET,
        "buildModeAttributes": MC2_PASSIVE_BUILDMODE_ATTR_TARGET,
        "sourceTask": MC2_PASSIVE_SOURCE_TASK_TITLE,
        "orderTypes": BUILD_ORDER_TYPE_TARGET,
        "exitType": BUILD_EXIT_TYPE_ACTIVE_KEY,
        "disabledCategories": BUILD_BLOCK_CATEGORY_DISABLE_TARGET,
    }
    payload["targetRationale"] = {
        "passiveRetest": "MC2 consumes MC survivors and must not improve, generate or alter strategy logic before Sequential.",
        "noUnknownEnum": "BuildMode.generationType is left as an SQX-known placeholder because no local CFX uses a safe none/passive enum.",
        "blocksSource": "Existing MC2 BuildingBlocks are preserved to avoid changing strategy logic; MC is only a fallback if the section is missing.",
        "methodology": "Signals and Stop/Limit blocks stay off; indicators remain governed by methodology/BlockSettings; only EnterAtMarket plus ExitAfterBars is allowed.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_mc2_passive_generation_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase7_mc2_passive_generation_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_mc2_passive_generation_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase7",
        "operation": "mc2_passive_generation_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase7_mc2_passive_generation_diff_review" if not apply else "phase7_mc2_static_tabs_decision",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase7_mc2_passive_generation_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def apply_mc2_static_tabs_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    apply_mc_rankings_to_root(root, actions)
    apply_retest1_risk_money_management_to_root(root, actions)
    apply_mc_atms_to_root(root, actions)
    actions.append({"field": "Notes", "changed": False, "sha256": section_sha256(root, "Notes"), "note": "audited and preserved"})
    apply_mc_selected_strategies_to_root(root, actions)
    apply_mc2_custom_data_to_root(root, actions)
    return actions


def mc2_static_tabs_summary(root: ET.Element) -> dict[str, Any]:
    summary = mc_static_tabs_summary(root)
    custom = find_section(root, "CustomData")
    setup = custom.find(".//Setup") if custom is not None else None
    size_based = setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']") if setup is not None else None
    main_values = setup.find("MainTestValues") if setup is not None else None
    if "customData" in summary:
        summary["customData"]["commission"] = (size_based.text or "") if size_based is not None else ""
        summary["customData"]["mainTestValues"] = dict(main_values.attrib) if main_values is not None else {}
    return summary


def enforce_mc2_static_tabs_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = mc2_static_tabs_summary(root)
    ranking = summary.get("rankings") or {}
    if ranking.get("type") != "never":
        issues.append(f"MC2 Rankings type is {ranking.get('type')!r}, expected 'never'")
    for key in ("MaxStrategies", "ConditionsType", "DeleteFailedStrategies", "ForceRunCrossChecks"):
        if ranking.get(key) != MC2_RANKING_TARGET[key]:
            issues.append(f"MC2 Rankings {key} is {ranking.get(key)!r}, expected {MC2_RANKING_TARGET[key]!r}")
    if (ranking.get("FitPortfolio") or {}).get("active") != "false":
        issues.append("MC2 FitPortfolio must remain disabled; portfolio selection belongs to later portfolio phases")
    if (ranking.get("CustomAnalysis") or {}).get("filter") != "false":
        issues.append("MC2 CustomAnalysis filter must remain disabled")
    if ranking.get("conditions"):
        issues.append("MC2 Rankings must not add extra conditions; CrossChecks acceptance owns MC2 pass/fail")

    rmm = summary.get("riskMoneyManagement") or {}
    methods = rmm.get("methods") or {}
    for method_type, wanted in RETEST1_RISK_MONEY_MANAGEMENT_METHOD_TARGET.items():
        if methods.get(method_type) != wanted:
            issues.append(f"MC2 RiskMoneyManagement {method_type} is {methods.get(method_type)!r}, expected {wanted!r}")

    atms = summary.get("atms") or {}
    for key, wanted in RETEST1_ATMS_TARGET.items():
        if (atms.get("attrs") or {}).get(key) != wanted:
            issues.append(f"MC2 ATMs {key} is {(atms.get('attrs') or {}).get(key)!r}, expected {wanted!r}")

    selected = summary.get("selectedStrategies") or {}
    if selected.get("children") != 0 or selected.get("text"):
        issues.append("MC2 SelectedStrategies must remain empty in the base template")

    custom = summary.get("customData") or {}
    if not custom.get("exists"):
        issues.append("MC2 CustomData section missing")
    else:
        period = generator_period(MC2_PERIOD_KEY)
        setup = custom.get("setup") or {}
        chart = custom.get("chart") or {}
        if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
            issues.append(f"MC2 CustomData dates are {(setup.get('dateFrom'), setup.get('dateTo'))!r}, expected {period!r}")
        if setup.get("testPrecision") != MC2_DATA_TEST_PRECISION:
            issues.append(f"MC2 CustomData testPrecision is {setup.get('testPrecision')!r}, expected {MC2_DATA_TEST_PRECISION!r}")
        if setup.get("session") != MC2_DATA_SESSION:
            issues.append(f"MC2 CustomData session is {setup.get('session')!r}, expected {MC2_DATA_SESSION!r}")
        if chart != MC2_DEFAULT_CHART_TARGET:
            issues.append(f"MC2 CustomData chart seed is {chart!r}, expected {MC2_DEFAULT_CHART_TARGET!r}")
        if custom.get("commission") != MC_CUSTOM_DATA_COMMISSION_TARGET:
            issues.append(f"MC2 CustomData commission is {custom.get('commission')!r}, expected {MC_CUSTOM_DATA_COMMISSION_TARGET!r}")
        if custom.get("mainTestValues") != MC2_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET:
            issues.append("MC2 CustomData MainTestValues drifted from full-retarget target")

    guarded_text = (
        section_text(root, "Rankings")
        + section_text(root, "ATMs")
        + section_text(root, "RiskMoneyManagement")
        + section_text(root, "SelectedStrategies")
        + section_text(root, "CustomData")
    )
    for token in MC_BANNED_DONOR_TOKENS:
        if token in guarded_text:
            issues.append(f"Forbidden donor token leaked into MC2 static tabs: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into MC2 static tabs")

    for issue in enforce_mc2_data_databanks_resources_options_guard(root):
        issues.append(f"Data/Resources guard: {issue}")
    for issue in enforce_mc2_crosschecks_guard(root):
        issues.append(f"CrossChecks guard: {issue}")
    for issue in enforce_mc2_passive_generation_guard(root):
        issues.append(f"Passive generation guard: {issue}")
    return issues


def update_mc2_static_tabs_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, MC2_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "mc2_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = mc2_static_tabs_summary(root)
    payload["actions"] = apply_mc2_static_tabs_to_root(root)
    payload["after"] = mc2_static_tabs_summary(root)
    payload["issues"] = enforce_mc2_static_tabs_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "rankings": MC2_RANKING_TARGET,
        "rankingConditions": [],
        "riskMoneyManagementMethods": RETEST1_RISK_MONEY_MANAGEMENT_METHOD_TARGET,
        "atms": RETEST1_ATMS_TARGET,
        "staticTabs": MC2_STATIC_TABS,
        "customDataMainTestValues": MC2_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET,
        "customDataCommission": MC_CUSTOM_DATA_COMMISSION_TARGET,
    }
    payload["targetRationale"] = {
        "decision": "MC2 gets a static/closeout safety block before Sequential because it is the last robustness gate feeding Sequential.",
        "ranking": "MC2 pass/fail is owned by MonteCarloRetest acceptance conditions; Ranking must preserve failed rows and not run portfolio selection.",
        "riskMoneyManagement": "FixedSize keeps Capa1 retests comparable and avoids sizing noise.",
        "customData": "CustomData remains the canonical MC2 data carrier and a generic local-safe seed, not Mining15 donor values.",
        "staticTabs": "ATMs, Notes and SelectedStrategies stay inert while executable behavior is guarded by previous MC2 blocks.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_mc2_static_tabs_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase7_mc2_static_tabs_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_mc2_static_tabs_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase7",
        "operation": "mc2_static_tabs_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase7_mc2_static_tabs_diff_review" if not apply else "phase7_mc2_closeout",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase7_mc2_static_tabs_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


MC2_CLOSEOUT_OPERATIONS = (
    ("dataDatabanksResourcesOptions", "mc2-data-databanks-resources-options-target", promote_mc2_data_databanks_resources_options_target),
    ("crosschecks", "mc2-crosschecks-target", promote_mc2_crosschecks_target),
    ("passiveGeneration", "mc2-passive-generation-target", promote_mc2_passive_generation_target),
    ("staticTabs", "mc2-static-tabs-target", promote_mc2_static_tabs_target),
)


def mc2_closeout_report(root142: Path, project_root: Path, target: str, write: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    operations: dict[str, Any] = {}
    issues: list[str] = []
    for key, command, runner in MC2_CLOSEOUT_OPERATIONS:
        result = runner(root142, project_root, target=target, apply=False)
        operation_issues = mc_closeout_operation_issues(command, result)
        operations[key] = {
            "command": command,
            "summary": mc_closeout_operation_summary(result),
            "issues": operation_issues,
        }
        issues.extend(operation_issues)

    payload: dict[str, Any] = {
        "ok": not issues,
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase7_mc2_closeout",
        "target": target,
        "write": write,
        "operations": operations,
        "issues": issues,
        "processProbe": process_snapshot(),
        "summary": {
            "decision": "MC2 needs a static/closeout safety block before Sequential, but no extra long questionnaire if all guards are already green and idempotent.",
            "mc2TaskTitle": MC2_TASK_TITLE,
            "mc2TaskXml": "AutomaticRetest-Task8.xml",
            "chain": "Input=MC / Output=MC2",
            "period": MC2_PERIOD_KEY,
            "testPrecision": MC2_DATA_TEST_PRECISION,
            "activeCrossCheck": MC2_ACTIVE_CHECK,
            "activeMethods": sorted(MC2_ACTIVE_METHODS),
            "sequentialInput": "MC2",
            "nextPhase": "phase8_sequential_open",
            "closeoutCriterion": "all MC2 guards must be green and idempotent on local base and repo template before Sequential",
        },
        "nextPhase": "phase8_sequential_open",
    }
    if write:
        target_path = ledger_root(project_root) / "phase_reports" / f"phase7_mc2_closeout_{stamp()}.json"
        write_json(target_path, payload)
        state_path = ledger_root(project_root) / "session_state.json"
        state = read_json(state_path, {})
        state.update({"updatedAt": now_iso(), "currentPhase": "phase7_mc2_closeout", "nextPhase": "phase8_sequential_open"})
        write_json(state_path, state)
        payload["written"] = str(target_path)
    return payload


def sequential_optimization_summary(root: ET.Element | None) -> dict[str, Any]:
    check = root.find(".//CrossChecks/SequentialOptimization") if root is not None else None
    if check is None:
        return {"exists": False}
    parameter_settings = check.find("./Settings/ParameterSettings")
    what_to_parametrize = check.find("./Settings/WhatToParametrize")
    acceptance = check.find("./AcceptanceSettings")
    return {
        "exists": True,
        "use": check.get("use", ""),
        "parameterSettings": {
            child.tag: (child.text or "")
            for child in list(parameter_settings) if isinstance(child.tag, str)
        } if parameter_settings is not None else {},
        "whatToParametrize": {
            "attributes": dict(what_to_parametrize.attrib),
            "values": {
                child.tag: (child.text or "")
                for child in list(what_to_parametrize) if isinstance(child.tag, str)
            },
        } if what_to_parametrize is not None else {},
        "acceptanceSettings": {
            "values": {
                child.tag: (child.text or "")
                for child in list(acceptance)
                if isinstance(child.tag, str) and child.tag != "Conditions"
            },
            "activeConditionCount": len([
                condition
                for condition in check.findall("./AcceptanceSettings/Conditions/Condition")
                if condition.get("use", "true") != "false"
            ]),
        } if acceptance is not None else {},
    }


def _setup_attrs(node: ET.Element | None) -> dict[str, str]:
    return dict(node.attrib) if node is not None else {}


def sequential_open_summary(root: ET.Element | None) -> dict[str, Any]:
    if root is None:
        return {"exists": False}
    databanks = {
        node.get("name", ""): node.get("value", "")
        for node in root.findall(".//Databanks/Databank")
        if node.get("name")
    }
    params = {
        param.get("key", ""): (param.text or "")
        for param in root.findall(".//BuildTradingOptions/Params/Param")
        if param.get("key") in {
            "Session",
            "MarketOpenSession",
            "LimitTimeRange",
            "SignalTimeRangeFrom",
            "SignalTimeRangeTo",
            "RealisticGapsHandling",
            "StoreChartData",
        }
    }
    rankings = find_section(root, "Rankings")
    fit_portfolio = rankings.find("FitPortfolio") if rankings is not None else None
    custom_analysis = rankings.find("CustomAnalysis") if rankings is not None else None
    strategy_type = root.find(".//WhatToBuild/StrategyType")
    crosschecks = root.find(".//CrossChecks")
    active_checks = [
        check.tag
        for check in list(crosschecks) if crosschecks is not None and isinstance(check.tag, str) and check.get("use") == "true"
    ] if crosschecks is not None else []
    return {
        "exists": True,
        "data": {
            "exists": root.find("./Data") is not None,
            "setup": _setup_attrs(root.find("./Data/Setups/Setup")),
            "outOfSampleRanges": [dict(node.attrib) for node in root.findall("./Data/OutOfSample/Range")],
        },
        "customData": {
            "exists": root.find("./CustomData") is not None,
            "setup": _setup_attrs(root.find("./CustomData/Setups/Setup")),
        },
        "databanks": databanks,
        "resources": _tick_real_resource_summary(root),
        "optionsParams": params,
        "strategyType": dict(strategy_type.attrib) if strategy_type is not None else {},
        "passiveGeneration": retest1_passive_generation_summary(root),
        "crossChecks": {
            "exists": crosschecks is not None,
            "attributes": dict(crosschecks.attrib) if crosschecks is not None else {},
            "active": active_checks,
            "sequentialOptimization": sequential_optimization_summary(root),
        },
        "rankings": {
            "type": rankings.get("type", "") if rankings is not None else "",
            "DeleteFailedStrategies": rankings.findtext("DeleteFailedStrategies") if rankings is not None else "",
            "ForceRunCrossChecks": rankings.findtext("ForceRunCrossChecks") if rankings is not None else "",
            "FitPortfolio": dict(fit_portfolio.attrib) if fit_portfolio is not None else {},
            "CustomAnalysis": dict(custom_analysis.attrib) if custom_analysis is not None else {},
            "activeConditionCount": len([
                condition
                for condition in rankings.findall("./Conditions/Condition")
                if condition.get("use", "true") != "false"
            ]) if rankings is not None else 0,
        },
    }


def sequential_open_issues(summary: dict[str, Any]) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    if not summary.get("exists"):
        return ["Sequential task missing"], warnings

    databanks = summary.get("databanks") or {}
    for name, wanted in SEQUENTIAL_EXPECTED_DATABANKS.items():
        if databanks.get(name) != wanted:
            issues.append(f"Sequential Databank {name} is {databanks.get(name)!r}, expected {wanted!r}")

    crosschecks = summary.get("crossChecks") or {}
    if not crosschecks.get("exists"):
        issues.append("Sequential CrossChecks section missing")
    else:
        attrs = crosschecks.get("attributes") or {}
        if attrs.get("use") != "true" or attrs.get("evaluateAll") != "true":
            issues.append("Sequential CrossChecks must stay active/evaluateAll for the SequentialOptimization gate")
        active = crosschecks.get("active") or []
        if active != [SEQUENTIAL_ACTIVE_CROSSCHECK]:
            issues.append(f"Sequential active crosschecks are {active!r}, expected only {SEQUENTIAL_ACTIVE_CROSSCHECK!r}")
        sequential = (crosschecks.get("sequentialOptimization") or {})
        if sequential.get("use") != "true":
            issues.append("SequentialOptimization must be active")
        parameter_settings = sequential.get("parameterSettings") or {}
        if parameter_settings.get("ApplyToStrategy") not in {"false", "False", "0"}:
            issues.append("SequentialOptimization ApplyToStrategy must remain false until explicitly approved")

    strategy_type = summary.get("strategyType") or {}
    improve_databank = strategy_type.get("improveDatabank", "")
    if improve_databank not in {"MC2", "Strategies to improve"}:
        warnings.append(f"Sequential StrategyType.improveDatabank is {improve_databank!r}; next block must decide whether to normalize it to MC2")
    elif improve_databank == "Strategies to improve":
        warnings.append("Sequential StrategyType.improveDatabank is still the SQX placeholder 'Strategies to improve'; next block should decide if it must be normalized to MC2")

    if (summary.get("data") or {}).get("exists") and (summary.get("customData") or {}).get("exists"):
        warnings.append("Sequential currently carries both Data and CustomData; next block must choose the canonical data carrier before mutation")

    return issues, warnings


def sequential_open_target_report(cfx: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256": file_sha256(cfx) if cfx.is_file() else "",
        "taskTitle": SEQUENTIAL_TASK_TITLE,
        "taskXml": "",
        "summary": {},
        "issues": [],
        "warnings": [],
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["issues"].append("missing_or_not_zip")
        payload["ok"] = False
        return payload
    task_xml_name, root = load_task_root(cfx, SEQUENTIAL_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["issues"].append("sequential_task_not_found")
        payload["ok"] = False
        return payload
    payload["summary"] = sequential_open_summary(root)
    issues, warnings = sequential_open_issues(payload["summary"])
    payload["issues"] = issues
    payload["warnings"] = warnings
    payload["ok"] = not issues
    return payload


def sequential_open_report(root142: Path, project_root: Path, target: str, write: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    target_reports = {
        name: sequential_open_target_report(path)
        for name, path in targets.items()
    }
    previous_gate = mc2_closeout_report(root142, project_root, target=target, write=False)
    previous_issues = list(previous_gate.get("issues") or [])
    if previous_gate.get("ok") is not True:
        previous_issues.append("mc2-closeout-report: previous gate ok=false")
    process_probe = process_snapshot()
    process_warnings = []
    if process_probe.get("processes"):
        process_warnings.append("SQX processes are alive; keep phase 8 read-only until SQX is closed")
    payload: dict[str, Any] = {
        "ok": all(item.get("ok") for item in target_reports.values()) and not previous_issues,
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase8_sequential_open",
        "target": target,
        "write": write,
        "previousGate": {
            "phase": previous_gate.get("phase"),
            "ok": previous_gate.get("ok"),
            "issues": previous_issues,
            "nextPhase": previous_gate.get("nextPhase"),
        },
        "targets": target_reports,
        "warnings": process_warnings + [
            warning
            for item in target_reports.values()
            for warning in item.get("warnings", [])
        ],
        "processProbe": process_probe,
        "summary": {
            "decision": "Open Sequential as Phase 8 after MC2 closeout; inspect structure before applying any target values.",
            "taskTitle": SEQUENTIAL_TASK_TITLE,
            "taskXml": SEQUENTIAL_TASK_XML,
            "chain": "Input=MC2 / Output=Sequential",
            "activeCrossCheck": SEQUENTIAL_ACTIVE_CROSSCHECK,
            "batchingDiscipline": "Real smokes stay batched/snapshotted; do not launch all survivors blindly.",
            "noLiveRun": "This gate only reads XML/local state and writes a phase report when requested.",
            "decisionPending": list(SEQUENTIAL_DECISION_PENDING),
        },
        "nextPhase": SEQUENTIAL_NEXT_PHASE,
    }
    if write:
        target_path = ledger_root(project_root) / "phase_reports" / f"phase8_sequential_open_{stamp()}.json"
        write_json(target_path, payload)
        state_path = ledger_root(project_root) / "session_state.json"
        state = read_json(state_path, {})
        state.update({"updatedAt": now_iso(), "currentPhase": "phase8_sequential_open", "nextPhase": SEQUENTIAL_NEXT_PHASE})
        write_json(state_path, state)
        payload["written"] = str(target_path)
    return payload


def sequential_data_databanks_resources_options_summary(root: ET.Element | None) -> dict[str, Any]:
    summary = sequential_open_summary(root)
    if not summary.get("exists"):
        return summary
    setup_pairs = []
    data_setup = root.find("./Data/Setups/Setup") if root is not None else None
    custom_setup = root.find("./CustomData/Setups/Setup") if root is not None else None
    if data_setup is not None and custom_setup is not None:
        setup_pairs.append({
            "field": "Data_vs_CustomData",
            "data": {
                "dateFrom": data_setup.get("dateFrom", ""),
                "dateTo": data_setup.get("dateTo", ""),
                "testPrecision": data_setup.get("testPrecision", ""),
                "session": data_setup.get("session", ""),
                "slippage": data_setup.get("slippage", ""),
                "minDist": data_setup.get("minDist", ""),
                "chart": dict(data_setup.find("Chart").attrib) if data_setup.find("Chart") is not None else {},
            },
            "customData": {
                "dateFrom": custom_setup.get("dateFrom", ""),
                "dateTo": custom_setup.get("dateTo", ""),
                "testPrecision": custom_setup.get("testPrecision", ""),
                "session": custom_setup.get("session", ""),
                "slippage": custom_setup.get("slippage", ""),
                "minDist": custom_setup.get("minDist", ""),
                "chart": dict(custom_setup.find("Chart").attrib) if custom_setup.find("Chart") is not None else {},
            },
        })
    summary["carrierDecision"] = {
        "mode": "dual_synced",
        "reason": "Sequential in SQX142 stores both Data and CustomData; keep both for compatibility but enforce same period, precision, session and chart seed.",
        "pairs": setup_pairs,
    }
    return summary


def ensure_setup_under(parent: ET.Element, actions: list[dict[str, Any]], field_prefix: str) -> ET.Element:
    setups = ensure_direct_child(parent, "Setups")
    setup = setups.find("Setup")
    if setup is None:
        setup = ET.SubElement(setups, "Setup")
        actions.append({"field": f"{field_prefix}/Setups/Setup", "from": None, "to": dict(setup.attrib), "changed": True})
    return setup


def ensure_commission_method(setup: ET.Element, actions: list[dict[str, Any]], field_prefix: str) -> None:
    commissions = ensure_direct_child(setup, "Commissions")
    existing_methods = {
        method.get("type", ""): method
        for method in commissions.findall("Method")
        if method.get("type")
    }
    for method_type, use in {"None": "false", "SizeBased": "true"}.items():
        method = existing_methods.get(method_type)
        before = dict(method.attrib) if method is not None else None
        if method is None:
            method = ET.SubElement(commissions, "Method", {"type": method_type})
        method.set("type", method_type)
        method.set("use", use)
        actions.append({
            "field": f"{field_prefix}/Commissions/Method:{method_type}",
            "from": before,
            "to": dict(method.attrib),
            "changed": before != dict(method.attrib),
        })
        if method_type == "SizeBased":
            params = ensure_direct_child(method, "Params")
            param = params.find("Param[@key='Commission']")
            before_param = {**dict(param.attrib), "text": param.text or ""} if param is not None else None
            if param is None:
                param = ET.SubElement(params, "Param", {"key": "Commission", "className": "SizeBased"})
            param.set("key", "Commission")
            param.set("className", "SizeBased")
            param.text = MC_CUSTOM_DATA_COMMISSION_TARGET
            after_param = {**dict(param.attrib), "text": param.text or ""}
            actions.append({
                "field": f"{field_prefix}/Commissions/Method:SizeBased/Param:Commission",
                "from": before_param,
                "to": after_param,
                "changed": before_param != after_param,
            })


def apply_sequential_setup_to_root(root: ET.Element, section_name: str, engine: str, actions: list[dict[str, Any]]) -> ET.Element:
    section = find_section(root, section_name)
    if section is None:
        section = ET.SubElement(root, section_name)
        actions.append({"field": section_name, "from": None, "to": "created", "changed": True})
    setup = ensure_setup_under(section, actions, section_name)
    period = generator_period(SEQUENTIAL_PERIOD_KEY)
    set_attrs_on_node(
        setup,
        {
            "dateFrom": period[0],
            "dateTo": period[1],
            "testPrecision": SEQUENTIAL_DATA_TEST_PRECISION,
            "session": SEQUENTIAL_DATA_SESSION,
            "slippage": "0",
            "minDist": "0",
            "engine": engine,
        },
        actions,
        f"{section_name}/Setup:attrs",
    )
    chart = setup.find("Chart")
    if chart is None:
        chart = ET.SubElement(setup, "Chart")
        actions.append({"field": f"{section_name}/Setup/Chart", "from": None, "to": dict(chart.attrib), "changed": True})
    set_attrs_on_node(chart, SEQUENTIAL_DEFAULT_CHART_TARGET, actions, f"{section_name}/Setup/Chart:attrs")
    ensure_commission_method(setup, actions, f"{section_name}/Setup")
    if section_name == "CustomData":
        main_values = setup.find("MainTestValues")
        if main_values is None:
            main_values = ET.SubElement(setup, "MainTestValues")
            actions.append({"field": "CustomData/MainTestValues", "from": None, "to": dict(main_values.attrib), "changed": True})
        set_attrs_on_node(
            main_values,
            SEQUENTIAL_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET,
            actions,
            "CustomData/MainTestValues:attrs",
        )
    return setup


def apply_sequential_data_databanks_resources_options_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    data_setup = apply_sequential_setup_to_root(root, "Data", SEQUENTIAL_DATA_ENGINE, actions)
    custom_setup = apply_sequential_setup_to_root(root, "CustomData", SEQUENTIAL_CUSTOM_DATA_ENGINE, actions)

    data = find_section(root, "Data")
    out_of_sample = data.find("OutOfSample") if data is not None else None
    removed_oos = []
    if out_of_sample is not None:
        for range_node in list(out_of_sample.findall("Range")):
            removed_oos.append(dict(range_node.attrib))
            out_of_sample.remove(range_node)
    actions.append({
        "field": "Data/OutOfSample/Range",
        "from": removed_oos,
        "to": [],
        "changed": bool(removed_oos),
        "note": "Sequential robustness gate does not add a nested OOS split.",
    })

    databanks = find_section(root, "Databanks")
    if databanks is None:
        databanks = ET.SubElement(root, "Databanks", {"retestSelected": "false"})
        actions.append({"field": "Databanks", "from": None, "to": dict(databanks.attrib), "changed": True})
    existing_by_name = {
        node.get("name", ""): node
        for node in databanks.findall("Databank")
        if node.get("name")
    }
    for name, wanted in SEQUENTIAL_EXPECTED_DATABANKS.items():
        node = existing_by_name.get(name)
        before = dict(node.attrib) if node is not None else None
        if node is None:
            node = ET.SubElement(databanks, "Databank", {"name": name})
        node.set("name", name)
        node.set("value", wanted)
        node.set("label", f"{name} databank")
        actions.append({
            "field": f"Databanks/{name}",
            "from": before,
            "to": dict(node.attrib),
            "changed": before != dict(node.attrib),
        })

    apply_mc2_resources_from_custom_data(root, custom_setup, actions)
    for key, value in SEQUENTIAL_OPTIONS_PARAMS_TARGET.items():
        set_param_text(root, key, value, actions, "Options")
    actions.append({
        "field": "Sequential/DataCarrier",
        "from": {
            "data": value_for_node(data_setup),
            "customData": value_for_node(custom_setup),
        },
        "to": "dual_synced",
        "changed": False,
        "note": "Kept both Data and CustomData for SQX142 compatibility; enforced matching period, precision, session and chart seed.",
    })
    return actions


def enforce_sequential_data_databanks_resources_options_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    period = generator_period(SEQUENTIAL_PERIOD_KEY)
    data_setup = root.find("./Data/Setups/Setup")
    custom_setup = root.find("./CustomData/Setups/Setup")
    if data_setup is None:
        issues.append("Sequential Data/Setup missing")
    if custom_setup is None:
        issues.append("Sequential CustomData/Setup missing")
    for label, setup in (("Data", data_setup), ("CustomData", custom_setup)):
        if setup is None:
            continue
        if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
            issues.append(f"Sequential {label} dates are not {SEQUENTIAL_PERIOD_KEY}")
        if setup.get("testPrecision") != SEQUENTIAL_DATA_TEST_PRECISION:
            issues.append(f"Sequential {label} testPrecision must stay {SEQUENTIAL_DATA_TEST_PRECISION}")
        if setup.get("session") != SEQUENTIAL_DATA_SESSION:
            issues.append(f"Sequential {label} session must stay {SEQUENTIAL_DATA_SESSION}")
        chart = setup.find("Chart")
        if chart is None:
            issues.append(f"Sequential {label} chart missing")
        else:
            for key, wanted in SEQUENTIAL_DEFAULT_CHART_TARGET.items():
                if chart.get(key) != wanted:
                    issues.append(f"Sequential {label} chart {key} is {chart.get(key)!r}, expected {wanted!r}")
        commission = setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']")
        if (commission.text if commission is not None else "") != MC_CUSTOM_DATA_COMMISSION_TARGET:
            issues.append(f"Sequential {label} commission is {(commission.text if commission is not None else '')!r}, expected {MC_CUSTOM_DATA_COMMISSION_TARGET!r}")
    if data_setup is not None and custom_setup is not None:
        data_chart = data_setup.find("Chart")
        custom_chart = custom_setup.find("Chart")
        for key in ("dateFrom", "dateTo", "testPrecision", "session", "slippage", "minDist"):
            if data_setup.get(key) != custom_setup.get(key):
                issues.append(f"Sequential Data/CustomData setup mismatch for {key}")
        if data_chart is not None and custom_chart is not None:
            for key in ("symbol", "timeframe", "spread"):
                if data_chart.get(key) != custom_chart.get(key):
                    issues.append(f"Sequential Data/CustomData chart mismatch for {key}")
    main_values = root.find("./CustomData/Setups/Setup/MainTestValues")
    if main_values is None or dict(main_values.attrib) != SEQUENTIAL_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET:
        issues.append("Sequential CustomData MainTestValues drifted from dual-synced target")

    databanks = {
        node.get("name", ""): node.get("value", "")
        for node in root.findall(".//Databanks/Databank")
        if node.get("name")
    }
    for name, wanted in SEQUENTIAL_EXPECTED_DATABANKS.items():
        if databanks.get(name) != wanted:
            issues.append(f"Sequential Databank {name} is {databanks.get(name)!r}, expected {wanted!r}")

    resources = find_section(root, "Resources")
    if resources is None:
        issues.append("Sequential Resources missing")
    else:
        chart_symbols = {
            chart.get("symbol", "")
            for chart in root.findall("./CustomData/Setups/Setup/Chart")
            if chart.get("symbol")
        }
        resource_symbols = {
            symbol.get("name", "")
            for symbol in resources.findall("./Symbols/Symbol")
            if symbol.get("name")
        }
        if chart_symbols != resource_symbols:
            issues.append(f"Sequential custom chart/resource mismatch: charts={sorted(chart_symbols)} resources={sorted(resource_symbols)}")
        broker_ids = {
            broker.get("id", "")
            for broker in resources.findall("./Brokers/Broker")
            if broker.get("id")
        }
        for symbol in resources.findall("./Symbols/Symbol"):
            if symbol.get("precision") != MC_RESOURCE_PRECISION:
                issues.append(f"Sequential resource {symbol.get('name')} precision is not TICK")
            if symbol.get("timezone") != MC_RESOURCE_TIMEZONE:
                issues.append(f"Sequential resource {symbol.get('name')} timezone is not EETUS")
            if symbol.get("broker") not in broker_ids:
                issues.append(f"Sequential resource {symbol.get('name')} references missing broker {symbol.get('broker')}")
            info = symbol.find("InstrumentInfo")
            if info is None:
                issues.append(f"Sequential resource {symbol.get('name')} has no nested InstrumentInfo")
            elif info.get("broker") not in broker_ids:
                issues.append(f"Sequential nested InstrumentInfo for {symbol.get('name')} references missing broker {info.get('broker')}")
        if resources.findall("./Sessions/Session"):
            issues.append("Sequential resources must not keep session entries")

    params = {
        param.get("key", ""): (param.text or "")
        for param in root.findall(".//BuildTradingOptions/Params/Param")
        if param.get("key") in SEQUENTIAL_OPTIONS_PARAMS_TARGET
    }
    for key, wanted in SEQUENTIAL_OPTIONS_PARAMS_TARGET.items():
        if params.get(key) != wanted:
            issues.append(f"Sequential Options param {key} is {params.get(key)!r}, expected {wanted!r}")

    if root.findall("./Data/OutOfSample/Range"):
        issues.append("Sequential Data must not contain nested OOS ranges")
    guarded_text = (
        section_text(root, "Data")
        + section_text(root, "CustomData")
        + section_text(root, "Databanks")
        + section_text(root, "Resources")
        + section_text(root, "Options")
    )
    for token in MC_BANNED_DONOR_TOKENS:
        if token in guarded_text:
            issues.append(f"Forbidden donor token leaked into Sequential Data/Databanks/Resources/Options: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into Sequential Data/Databanks/Resources/Options")
    return issues


def update_sequential_data_databanks_resources_options_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload
    task_xml_name, root = load_task_root(cfx, SEQUENTIAL_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "sequential_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = sequential_data_databanks_resources_options_summary(root)
    payload["actions"] = apply_sequential_data_databanks_resources_options_to_root(root)
    payload["after"] = sequential_data_databanks_resources_options_summary(root)
    payload["issues"] = enforce_sequential_data_databanks_resources_options_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["xmlChanged"] = before_text != after_text
    payload["changed"] = payload["changedActionCount"] > 0
    payload["targetValues"] = {
        "taskTitle": SEQUENTIAL_TASK_TITLE,
        "taskXml": SEQUENTIAL_TASK_XML,
        "periodKey": SEQUENTIAL_PERIOD_KEY,
        "dateFrom": generator_period(SEQUENTIAL_PERIOD_KEY)[0],
        "dateTo": generator_period(SEQUENTIAL_PERIOD_KEY)[1],
        "dataCarrier": "dual_synced",
        "dataEngine": SEQUENTIAL_DATA_ENGINE,
        "customDataEngine": SEQUENTIAL_CUSTOM_DATA_ENGINE,
        "customDataMainTestValues": SEQUENTIAL_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET,
        "databanks": SEQUENTIAL_EXPECTED_DATABANKS,
        "resourcePrecision": MC_RESOURCE_PRECISION,
        "resourceTimezone": MC_RESOURCE_TIMEZONE,
        "options": SEQUENTIAL_OPTIONS_PARAMS_TARGET,
    }
    payload["targetRationale"] = {
        "methodology": "Sequential consumes MC2 survivors and probes parameter stability; it is not a new OOS split or live optimizer in Capa1.",
        "carrier": "SQX142 Sequential carries both Data and CustomData in known-good projects; keeping both synced is safer than deleting one without UI evidence.",
        "options": "Trading time ranges are disabled for this robustness gate in the base/template; Project Generator should not inject them for Sequential.",
        "naturalResults": "The block preserves natural passed/failed rows and does not force Results=passed.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_sequential_data_databanks_resources_options_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase8_sequential_data_databanks_resources_options_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_sequential_data_databanks_resources_options_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase8",
        "operation": "sequential_data_databanks_resources_options_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase8_sequential_data_databanks_resources_options_diff_review" if not apply else SEQUENTIAL_DATA_DATABANKS_RESOURCES_OPTIONS_NEXT,
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase8_sequential_data_databanks_resources_options_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def summarize_crosscheck_methods(check: ET.Element) -> list[dict[str, Any]]:
    return [
        {
            "type": method.get("type", ""),
            "use": method.get("use", ""),
            "params": method_params(method),
        }
        for method in check.findall("./Settings/Methods/Method")
    ]


def sequential_crosschecks_summary(root: ET.Element | None) -> dict[str, Any]:
    parent = find_section(root, "CrossChecks") if root is not None else None
    checks: list[dict[str, Any]] = []
    if parent is not None:
        for check in list(parent):
            if not isinstance(check.tag, str) or check.get("use") is None:
                continue
            methods = summarize_crosscheck_methods(check)
            checks.append({
                "id": check.tag,
                "use": check.get("use", ""),
                "methods": methods,
                "activeMethodTypes": [
                    method.get("type", "")
                    for method in methods
                    if method.get("use") == "true"
                ],
                "nestedSetups": [
                    {
                        "attrs": dict(setup.attrib),
                        "charts": [dict(chart.attrib) for chart in setup.findall("Chart")],
                    }
                    for setup in check.findall("./Settings/Setups/Setup")
                ],
            })
    return {
        "crossChecks": {
            "exists": parent is not None,
            "attrs": dict(parent.attrib) if parent is not None else {},
            "active": [item["id"] for item in checks if item.get("use") == "true"],
            "checks": checks,
            "sequentialOptimization": sequential_optimization_summary(root),
            "sha256": section_sha256(root, "CrossChecks") if root is not None else "",
        },
        "dataGate": sequential_data_databanks_resources_options_summary(root),
    }


def clear_conditions_node(conditions: ET.Element, actions: list[dict[str, Any]], field: str) -> None:
    before = {
        "attrs": dict(conditions.attrib),
        "conditions": summarize_conditions_detailed(conditions),
        "childTags": [child.tag for child in list(conditions) if isinstance(child.tag, str)],
    }
    conditions.attrib.clear()
    for child in list(conditions):
        conditions.remove(child)
    conditions.text = None
    after = {
        "attrs": dict(conditions.attrib),
        "conditions": summarize_conditions_detailed(conditions),
        "childTags": [child.tag for child in list(conditions) if isinstance(child.tag, str)],
    }
    actions.append({"field": field, "from": before, "to": after, "changed": before != after})


def remove_unknown_text_children(parent: ET.Element, allowed_tags: set[str], actions: list[dict[str, Any]], field: str) -> None:
    removed = [
        {"tag": child.tag, "text": child.text or "", "attrs": dict(child.attrib)}
        for child in list(parent)
        if isinstance(child.tag, str) and child.tag not in allowed_tags
    ]
    for child in list(parent):
        if isinstance(child.tag, str) and child.tag not in allowed_tags:
            parent.remove(child)
    actions.append({
        "field": field,
        "from": removed,
        "to": [],
        "changed": bool(removed),
    })


def normalize_sequential_crosscheck_setups(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    period = generator_period(SEQUENTIAL_PERIOD_KEY)
    before: list[dict[str, Any]] = []
    after: list[dict[str, Any]] = []
    for setup in root.findall(".//CrossChecks/*/Settings/Setups/Setup"):
        before.append({
            "attrs": dict(setup.attrib),
            "charts": [dict(chart.attrib) for chart in setup.findall("Chart")],
        })
        for key, wanted in {
            "dateFrom": period[0],
            "dateTo": period[1],
            "testPrecision": SEQUENTIAL_DATA_TEST_PRECISION,
            "session": SEQUENTIAL_DATA_SESSION,
            "slippage": "0",
            "minDist": "0",
        }.items():
            setup.set(key, wanted)
        charts = setup.findall("Chart")
        if not charts:
            charts = [ET.SubElement(setup, "Chart")]
        for chart in charts:
            for key, value in SEQUENTIAL_DEFAULT_CHART_TARGET.items():
                chart.set(key, value)
        after.append({
            "attrs": dict(setup.attrib),
            "charts": [dict(chart.attrib) for chart in setup.findall("Chart")],
        })
    actions.append({
        "field": "CrossChecks/*/Settings/Setups/Setup",
        "from": before,
        "to": after,
        "changed": before != after,
        "note": "Inactive nested crosscheck setups are normalized to the same safe seed; SequentialOptimization itself remains the only active gate.",
    })


def apply_sequential_crosschecks_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    parent = find_section(root, "CrossChecks")
    if parent is None:
        parent = ET.SubElement(root, "CrossChecks")
        actions.append({"field": "CrossChecks", "from": None, "to": dict(parent.attrib), "changed": True})
    set_attrs_on_node(parent, SEQUENTIAL_CROSSCHECK_PARENT_TARGET, actions, "CrossChecks:attrs")

    active = parent.find(SEQUENTIAL_ACTIVE_CROSSCHECK)
    if active is None:
        active = ET.SubElement(parent, SEQUENTIAL_ACTIVE_CROSSCHECK, {"use": "true"})
        actions.append({"field": f"CrossChecks/{SEQUENTIAL_ACTIVE_CROSSCHECK}", "from": None, "to": dict(active.attrib), "changed": True})

    for check in list(parent):
        if not isinstance(check.tag, str) or check.get("use") is None:
            continue
        before_use = check.get("use", "")
        wanted_use = "true" if check.tag == SEQUENTIAL_ACTIVE_CROSSCHECK else "false"
        check.set("use", wanted_use)
        actions.append({
            "field": f"CrossChecks/{check.tag}:use",
            "from": before_use,
            "to": wanted_use,
            "changed": before_use != wanted_use,
        })
        if check.tag != SEQUENTIAL_ACTIVE_CROSSCHECK:
            for method in check.findall("./Settings/Methods/Method"):
                before_method = method.get("use", "")
                method.set("use", "false")
                actions.append({
                    "field": f"CrossChecks/{check.tag}/Method:{method.get('type', '')}:use",
                    "from": before_method,
                    "to": "false",
                    "changed": before_method != "false",
                })

    settings = ensure_direct_child(active, "Settings")
    parameter_settings = ensure_direct_child(settings, "ParameterSettings")
    for key, wanted in SEQUENTIAL_PARAMETER_SETTINGS_TARGET.items():
        set_or_create_text_child(
            parameter_settings,
            key,
            wanted,
            actions,
            f"CrossChecks/{SEQUENTIAL_ACTIVE_CROSSCHECK}/ParameterSettings/{key}",
        )
    remove_unknown_text_children(
        parameter_settings,
        set(SEQUENTIAL_PARAMETER_SETTINGS_TARGET),
        actions,
        f"CrossChecks/{SEQUENTIAL_ACTIVE_CROSSCHECK}/ParameterSettings:unknown",
    )

    what_to_parametrize = settings.find("WhatToParametrize")
    if what_to_parametrize is None:
        what_to_parametrize = ET.SubElement(settings, "WhatToParametrize")
        actions.append({
            "field": f"CrossChecks/{SEQUENTIAL_ACTIVE_CROSSCHECK}/WhatToParametrize",
            "from": None,
            "to": dict(what_to_parametrize.attrib),
            "changed": True,
        })
    before_attrs = dict(what_to_parametrize.attrib)
    what_to_parametrize.attrib.clear()
    what_to_parametrize.attrib.update(SEQUENTIAL_WHAT_TO_PARAMETRIZE_ATTR_TARGET)
    actions.append({
        "field": f"CrossChecks/{SEQUENTIAL_ACTIVE_CROSSCHECK}/WhatToParametrize:attrs",
        "from": before_attrs,
        "to": dict(what_to_parametrize.attrib),
        "changed": before_attrs != dict(what_to_parametrize.attrib),
    })
    for key, wanted in SEQUENTIAL_WHAT_TO_PARAMETRIZE_VALUES_TARGET.items():
        set_or_create_text_child(
            what_to_parametrize,
            key,
            wanted,
            actions,
            f"CrossChecks/{SEQUENTIAL_ACTIVE_CROSSCHECK}/WhatToParametrize/{key}",
        )
    remove_unknown_text_children(
        what_to_parametrize,
        set(SEQUENTIAL_WHAT_TO_PARAMETRIZE_VALUES_TARGET),
        actions,
        f"CrossChecks/{SEQUENTIAL_ACTIVE_CROSSCHECK}/WhatToParametrize:unknown",
    )

    acceptance = ensure_direct_child(active, "AcceptanceSettings")
    for key, wanted in SEQUENTIAL_ACCEPTANCE_SETTINGS_TARGET.items():
        set_or_create_text_child(
            acceptance,
            key,
            wanted,
            actions,
            f"CrossChecks/{SEQUENTIAL_ACTIVE_CROSSCHECK}/AcceptanceSettings/{key}",
        )
    remove_unknown_text_children(
        acceptance,
        set(SEQUENTIAL_ACCEPTANCE_SETTINGS_TARGET) | {"Conditions"},
        actions,
        f"CrossChecks/{SEQUENTIAL_ACTIVE_CROSSCHECK}/AcceptanceSettings:unknown",
    )
    conditions = acceptance.find("Conditions")
    if conditions is None:
        conditions = ET.SubElement(acceptance, "Conditions")
        actions.append({
            "field": f"CrossChecks/{SEQUENTIAL_ACTIVE_CROSSCHECK}/AcceptanceSettings/Conditions",
            "from": None,
            "to": "created_empty",
            "changed": True,
        })
    clear_conditions_node(
        conditions,
        actions,
        f"CrossChecks/{SEQUENTIAL_ACTIVE_CROSSCHECK}/AcceptanceSettings/Conditions",
    )
    normalize_sequential_crosscheck_setups(root, actions)
    return actions


def enforce_sequential_crosschecks_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = sequential_crosschecks_summary(root)
    cross = summary.get("crossChecks") or {}
    attrs = cross.get("attrs") or {}
    if attrs != SEQUENTIAL_CROSSCHECK_PARENT_TARGET:
        issues.append(f"Sequential CrossChecks attrs are {attrs!r}, expected {SEQUENTIAL_CROSSCHECK_PARENT_TARGET!r}")
    if cross.get("active") != [SEQUENTIAL_ACTIVE_CROSSCHECK]:
        issues.append(f"Sequential active crosschecks are {cross.get('active')!r}, expected [{SEQUENTIAL_ACTIVE_CROSSCHECK!r}]")

    checks = {item.get("id"): item for item in cross.get("checks") or []}
    sequential = cross.get("sequentialOptimization") or {}
    if sequential.get("exists") is not True or sequential.get("use") != "true":
        issues.append("SequentialOptimization must exist and remain active")
    if (sequential.get("parameterSettings") or {}) != SEQUENTIAL_PARAMETER_SETTINGS_TARGET:
        issues.append(f"SequentialOptimization ParameterSettings drifted: {sequential.get('parameterSettings')!r}")
    what = sequential.get("whatToParametrize") or {}
    if (what.get("attributes") or {}) != SEQUENTIAL_WHAT_TO_PARAMETRIZE_ATTR_TARGET:
        issues.append(f"SequentialOptimization WhatToParametrize attrs drifted: {what.get('attributes')!r}")
    if (what.get("values") or {}) != SEQUENTIAL_WHAT_TO_PARAMETRIZE_VALUES_TARGET:
        issues.append(f"SequentialOptimization WhatToParametrize values drifted: {what.get('values')!r}")
    acceptance = sequential.get("acceptanceSettings") or {}
    if (acceptance.get("values") or {}) != SEQUENTIAL_ACCEPTANCE_SETTINGS_TARGET:
        issues.append(f"SequentialOptimization AcceptanceSettings drifted: {acceptance.get('values')!r}")
    if acceptance.get("activeConditionCount") != 0:
        issues.append("SequentialOptimization AcceptanceSettings must not contain extra filter conditions")

    for check in cross.get("checks") or []:
        if check.get("id") == SEQUENTIAL_ACTIVE_CROSSCHECK:
            continue
        active_methods = [method for method in check.get("methods") or [] if method.get("use") == "true"]
        if active_methods:
            issues.append(f"Inactive Sequential crosscheck {check.get('id')} still has active methods: {[item.get('type') for item in active_methods]}")

    period = generator_period(SEQUENTIAL_PERIOD_KEY)
    for setup in root.findall(".//CrossChecks/*/Settings/Setups/Setup"):
        if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
            issues.append(f"Sequential nested CrossChecks setup dates drifted: {dict(setup.attrib)!r}")
        if setup.get("testPrecision") != SEQUENTIAL_DATA_TEST_PRECISION:
            issues.append(f"Sequential nested CrossChecks setup precision is {setup.get('testPrecision')!r}, expected {SEQUENTIAL_DATA_TEST_PRECISION!r}")
        if setup.get("session") != SEQUENTIAL_DATA_SESSION:
            issues.append(f"Sequential nested CrossChecks setup session is {setup.get('session')!r}, expected {SEQUENTIAL_DATA_SESSION!r}")
        if setup.get("slippage") != "0" or setup.get("minDist") != "0":
            issues.append(f"Sequential nested CrossChecks setup costs drifted: {dict(setup.attrib)!r}")
        for chart in setup.findall("Chart"):
            for key, wanted in SEQUENTIAL_DEFAULT_CHART_TARGET.items():
                if chart.get(key) != wanted:
                    issues.append(f"Sequential nested CrossChecks chart {key} is {chart.get(key)!r}, expected {wanted!r}")

    rankings = find_section(root, "Rankings")
    if rankings is not None and (rankings.findtext("ForceRunCrossChecks") or "") != "false":
        issues.append("Sequential Rankings/ForceRunCrossChecks must remain false")

    for issue in enforce_sequential_data_databanks_resources_options_guard(root):
        issues.append(f"Data/Resources guard: {issue}")

    guarded_text = section_text(root, "CrossChecks")
    for token in MC_BANNED_DONOR_TOKENS:
        if token in guarded_text:
            issues.append(f"Forbidden donor token leaked into Sequential CrossChecks: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into Sequential CrossChecks")
    return issues


def update_sequential_crosschecks_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload
    task_xml_name, root = load_task_root(cfx, SEQUENTIAL_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "sequential_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = sequential_crosschecks_summary(root)
    payload["actions"] = apply_sequential_crosschecks_to_root(root)
    payload["after"] = sequential_crosschecks_summary(root)
    payload["issues"] = enforce_sequential_crosschecks_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "activeCheck": SEQUENTIAL_ACTIVE_CROSSCHECK,
        "parent": SEQUENTIAL_CROSSCHECK_PARENT_TARGET,
        "parameterSettings": SEQUENTIAL_PARAMETER_SETTINGS_TARGET,
        "whatToParametrizeAttrs": SEQUENTIAL_WHAT_TO_PARAMETRIZE_ATTR_TARGET,
        "whatToParametrizeValues": SEQUENTIAL_WHAT_TO_PARAMETRIZE_VALUES_TARGET,
        "acceptanceSettings": SEQUENTIAL_ACCEPTANCE_SETTINGS_TARGET,
        "acceptanceConditions": [],
        "nestedSetupPeriod": SEQUENTIAL_PERIOD_KEY,
        "nestedSetupChartSeed": SEQUENTIAL_DEFAULT_CHART_TARGET,
    }
    payload["targetRationale"] = {
        "methodology": "Sequential is a parameter-stability robustness gate after MC2 survivors, not a second optimizer that rewrites strategies.",
        "academic": "Limiting the parameter search surface and keeping ApplyToStrategy=false reduces repeated fitting pressure on validation evidence.",
        "localEvidence": "Sequential smokes were stable when run in batches after MC2 was unlocked; this target preserves the same gate settings while making inactive checks inert.",
        "naturalResults": "No Results value is forced; passed/failed must remain the natural SQX outcome.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_sequential_crosschecks_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase8_sequential_crosschecks_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_sequential_crosschecks_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase8",
        "operation": "sequential_crosschecks_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase8_sequential_crosschecks_diff_review" if not apply else SEQUENTIAL_CROSSCHECKS_NEXT,
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase8_sequential_crosschecks_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def apply_sequential_what_to_build_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    what_to_build = find_section(root, "WhatToBuild")
    if what_to_build is None:
        what_to_build = ET.SubElement(root, "WhatToBuild")
        actions.append({"field": "WhatToBuild", "from": None, "to": "created", "changed": True})

    set_or_create_attrs_child(
        what_to_build,
        "StrategyType",
        SEQUENTIAL_STRATEGY_TYPE_TARGET,
        actions,
        "WhatToBuild/StrategyType",
    )
    build_mode = what_to_build.find("BuildMode")
    if build_mode is None:
        build_mode = ET.SubElement(what_to_build, "BuildMode", {"generationType": "random-generation"})
        actions.append({"field": "WhatToBuild/BuildMode", "from": None, "to": dict(build_mode.attrib), "changed": True})
    else:
        actions.append({
            "field": "WhatToBuild/BuildMode:generationType",
            "from": build_mode.get("generationType", ""),
            "to": build_mode.get("generationType", ""),
            "changed": False,
            "note": "left as SQX-known placeholder; Sequential passive behavior is enforced by MC2 input, disabled improve parts and disabled evolution toggles",
        })
    for tag, value in SEQUENTIAL_PASSIVE_BUILDMODE_TEXT_TARGET.items():
        set_or_create_text_child(build_mode, tag, value, actions, f"WhatToBuild/BuildMode/{tag}")
    for tag, attrs in SEQUENTIAL_PASSIVE_BUILDMODE_ATTR_TARGET.items():
        set_or_update_attrs_child(build_mode, tag, attrs, actions, f"WhatToBuild/BuildMode/{tag}")


def apply_sequential_blocks_to_root(root: ET.Element, source_root: ET.Element | None, actions: list[dict[str, Any]]) -> None:
    blocks = find_blocks(root)
    if blocks is None:
        blocks = ET.SubElement(root, "Blocks", {"type": "simple", "version": "142.2336"})
        actions.append({"field": "Blocks", "from": None, "to": dict(blocks.attrib), "changed": True})

    before_attrs = dict(blocks.attrib)
    blocks.set("type", "simple")
    blocks.set("version", "142.2336")
    actions.append({
        "field": "Blocks:attrs",
        "from": before_attrs,
        "to": dict(blocks.attrib),
        "changed": before_attrs != dict(blocks.attrib),
    })

    source_blocks = find_blocks(source_root)
    if blocks.find("BuildingBlocks") is None and source_blocks is not None:
        actions.append(replace_building_blocks_from_source(blocks, source_blocks))
    else:
        actions.append({
            "field": "BuildingBlocks",
            "changed": False,
            "note": "preserved existing Sequential building-block universe; passive gate only enforces no-improve, entry and exit contracts",
        })
    if source_blocks is not None:
        for child_name in ("OrderTypes", "ExitTypes"):
            if blocks.find(child_name) is None and source_blocks.find(child_name) is not None:
                blocks.append(ET.fromstring(serialize_xml(source_blocks.find(child_name))))
                actions.append({
                    "field": child_name,
                    "from": None,
                    "to": "copied_from_mc2_source",
                    "changed": True,
                    "note": "Sequential had no explicit passive block controls; copied MC2 controls before enforcing the methodology contract.",
                })
    enforce_order_types(blocks, actions)
    enforce_exit_types(blocks, actions)
    enforce_external_custom_data(blocks, actions)
    enforce_disabled_build_block_categories(blocks, actions)


def apply_sequential_passive_generation_to_root(root: ET.Element, source_root: ET.Element | None) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    apply_retest1_parts_to_improve_to_root(root, actions)
    apply_sequential_what_to_build_to_root(root, actions)
    apply_sequential_blocks_to_root(root, source_root, actions)
    return actions


def sequential_passive_generation_summary(root: ET.Element) -> dict[str, Any]:
    return retest1_passive_generation_summary(root)


def enforce_sequential_passive_generation_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = sequential_passive_generation_summary(root)
    parts = summary.get("partsToImprove") or {}
    for group_name in ("EntryRules", "OrderTypes", "ExitRules"):
        group = parts.get(group_name) or {}
        for side in ("LongImprovement", "ShortImprovement"):
            if (group.get(side) or {}).get("use") != "false":
                issues.append(f"Sequential {group_name}/{side} must be passive use=false")
    if summary.get("strategyType") != SEQUENTIAL_STRATEGY_TYPE_TARGET:
        issues.append("Sequential StrategyType must point passively to MC2 with known SQX attributes")
    build_mode = summary.get("buildMode") or {}
    build_text = build_mode.get("text") or {}
    for tag, value in SEQUENTIAL_PASSIVE_BUILDMODE_TEXT_TARGET.items():
        if build_text.get(tag) != value:
            issues.append(f"Sequential BuildMode {tag} is {build_text.get(tag)!r}, expected {value!r}")
    child_attrs = build_mode.get("childAttrs") or {}
    for tag, attrs in SEQUENTIAL_PASSIVE_BUILDMODE_ATTR_TARGET.items():
        current = child_attrs.get(tag) or {}
        for key, value in attrs.items():
            if current.get(key) != value:
                issues.append(f"Sequential BuildMode {tag}.{key} is {current.get(key)!r}, expected {value!r}")
    blocks = summary.get("blocks") or {}
    expected_order = BUILD_ORDER_TYPE_TARGET
    actual_order = {key: blocks.get("orderTypes", {}).get(key) for key in expected_order}
    if actual_order != expected_order:
        issues.append(f"Sequential order types are {actual_order!r}, expected {expected_order!r}")
    exits = blocks.get("exitTypes") or {}
    if exits.get(BUILD_EXIT_TYPE_ACTIVE_KEY, {}).get("use") != "true":
        issues.append("Sequential must keep only ExitAfterBars active")
    if exits.get(BUILD_EXIT_TYPE_ACTIVE_KEY, {}).get("probability") != "100":
        issues.append("Sequential ExitAfterBars probability must be 100")
    active_other_exits = [
        key for key, data in exits.items()
        if key != BUILD_EXIT_TYPE_ACTIVE_KEY and (data or {}).get("use") == "true"
    ]
    if active_other_exits:
        issues.append(f"Sequential has non-passive active exit types: {active_other_exits}")
    if any(any(token in key for token in BUILD_EXIT_TYPE_BANNED_TOKENS) for key in exits):
        issues.append("Sequential contains day-based exit types")
    if int(blocks.get("activeSignalCount") or 0) != 0:
        issues.append("Sequential signals must remain disabled in passive retest")
    if int(blocks.get("activeStopLimitCount") or 0) != 0:
        issues.append("Sequential stop/limit entry blocks must remain disabled in passive retest")
    if int(blocks.get("activeIndicatorCount") or 0) <= 0:
        issues.append("Sequential must preserve methodology/BlockSettings indicator blocks")
    custom = blocks.get("customData") or {}
    if (custom.get("attrs") or {}).get("showAll") != "false" or custom.get("children") != 0:
        issues.append("Sequential external CustomData must stay disabled and empty")
    for issue in enforce_sequential_data_databanks_resources_options_guard(root):
        issues.append(f"Data/Resources guard: {issue}")
    for issue in enforce_sequential_crosschecks_guard(root):
        issues.append(f"CrossChecks guard: {issue}")
    guarded_sections = [
        find_section(root, "PartsToImprove"),
        find_section(root, "WhatToBuild"),
        find_section(root, "Blocks"),
    ]
    guarded_text = "".join(serialize_xml(section if section is not None else root) for section in guarded_sections)
    for token in ("ExitAfterDays", "ExitAfterTradingDays", "USDJPY_darwinex", "USDJPY_dukascopy", "Strategies to improve"):
        if token in guarded_text:
            issues.append(f"Forbidden token leaked into Sequential passive generation tabs: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into Sequential passive generation tabs")
    return issues


def update_sequential_passive_generation_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, SEQUENTIAL_TASK_TITLE)
    source_task_xml_name, source_root = load_task_root(cfx, SEQUENTIAL_PASSIVE_SOURCE_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    payload["sourceTaskXml"] = source_task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "sequential_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload
    if not source_task_xml_name or source_root is None:
        payload["error"] = "sequential_source_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = sequential_passive_generation_summary(root)
    payload["actions"] = apply_sequential_passive_generation_to_root(root, source_root)
    payload["after"] = sequential_passive_generation_summary(root)
    payload["issues"] = enforce_sequential_passive_generation_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "strategyType": SEQUENTIAL_STRATEGY_TYPE_TARGET,
        "buildModeText": SEQUENTIAL_PASSIVE_BUILDMODE_TEXT_TARGET,
        "buildModeAttributes": SEQUENTIAL_PASSIVE_BUILDMODE_ATTR_TARGET,
        "sourceTask": SEQUENTIAL_PASSIVE_SOURCE_TASK_TITLE,
        "orderTypes": BUILD_ORDER_TYPE_TARGET,
        "exitType": BUILD_EXIT_TYPE_ACTIVE_KEY,
        "disabledCategories": BUILD_BLOCK_CATEGORY_DISABLE_TARGET,
    }
    payload["targetRationale"] = {
        "passiveRetest": "Sequential consumes MC2 survivors and must not improve, generate or alter strategy logic.",
        "noUnknownEnum": "BuildMode.generationType is left as an SQX-known placeholder because no local CFX uses a safe none/passive enum.",
        "placeholderRemoval": "StrategyType.improveDatabank is normalized from 'Strategies to improve' to MC2 so the chain is explicit and auditable.",
        "methodology": "Signals and Stop/Limit blocks stay off; indicators remain governed by methodology/BlockSettings; only EnterAtMarket plus ExitAfterBars is allowed.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_sequential_passive_generation_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase8_sequential_passive_generation_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_sequential_passive_generation_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase8",
        "operation": "sequential_passive_generation_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase8_sequential_passive_generation_diff_review" if not apply else SEQUENTIAL_PASSIVE_GENERATION_NEXT,
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase8_sequential_passive_generation_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def apply_sequential_custom_data_static_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    apply_sequential_setup_to_root(root, "CustomData", SEQUENTIAL_CUSTOM_DATA_ENGINE, actions)


def apply_sequential_static_tabs_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    apply_sequential_rankings_to_root(root, actions)
    apply_retest1_risk_money_management_to_root(root, actions)
    apply_mc_atms_to_root(root, actions)
    actions.append({"field": "Notes", "changed": False, "sha256": section_sha256(root, "Notes"), "note": "audited and preserved"})
    apply_mc_selected_strategies_to_root(root, actions)
    apply_sequential_custom_data_static_to_root(root, actions)
    return actions


def sequential_static_tabs_summary(root: ET.Element) -> dict[str, Any]:
    summary = mc_static_tabs_summary(root)
    custom = find_section(root, "CustomData")
    setup = custom.find(".//Setup") if custom is not None else None
    size_based = setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']") if setup is not None else None
    main_values = setup.find("MainTestValues") if setup is not None else None
    if "customData" in summary:
        summary["customData"]["commission"] = (size_based.text or "") if size_based is not None else ""
        summary["customData"]["mainTestValues"] = dict(main_values.attrib) if main_values is not None else {}
    return summary


def enforce_sequential_static_tabs_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = sequential_static_tabs_summary(root)
    ranking = summary.get("rankings") or {}
    if ranking.get("type") != "never":
        issues.append(f"Sequential Rankings type is {ranking.get('type')!r}, expected 'never'")
    for key in ("MaxStrategies", "ConditionsType", "DeleteFailedStrategies", "ForceRunCrossChecks"):
        if ranking.get(key) != SEQUENTIAL_RANKING_TARGET[key]:
            issues.append(f"Sequential Rankings {key} is {ranking.get(key)!r}, expected {SEQUENTIAL_RANKING_TARGET[key]!r}")
    if (ranking.get("FitPortfolio") or {}).get("active") != "false":
        issues.append("Sequential FitPortfolio must remain disabled; portfolio selection belongs to later portfolio phases")
    if (ranking.get("CustomAnalysis") or {}).get("filter") != "false":
        issues.append("Sequential CustomAnalysis filter must remain disabled")
    if ranking.get("conditions"):
        issues.append("Sequential Rankings must not add extra conditions; SequentialOptimization owns pass/fail")

    rmm = summary.get("riskMoneyManagement") or {}
    methods = rmm.get("methods") or {}
    for method_type, wanted in RETEST1_RISK_MONEY_MANAGEMENT_METHOD_TARGET.items():
        if methods.get(method_type) != wanted:
            issues.append(f"Sequential RiskMoneyManagement {method_type} is {methods.get(method_type)!r}, expected {wanted!r}")

    atms = summary.get("atms") or {}
    for key, wanted in RETEST1_ATMS_TARGET.items():
        if (atms.get("attrs") or {}).get(key) != wanted:
            issues.append(f"Sequential ATMs {key} is {(atms.get('attrs') or {}).get(key)!r}, expected {wanted!r}")

    selected = summary.get("selectedStrategies") or {}
    if selected.get("children") != 0 or selected.get("text"):
        issues.append("Sequential SelectedStrategies must remain empty in the base template")

    custom = summary.get("customData") or {}
    if not custom.get("exists"):
        issues.append("Sequential CustomData section missing")
    else:
        period = generator_period(SEQUENTIAL_PERIOD_KEY)
        setup = custom.get("setup") or {}
        chart = custom.get("chart") or {}
        if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
            issues.append(f"Sequential CustomData dates are {(setup.get('dateFrom'), setup.get('dateTo'))!r}, expected {period!r}")
        if setup.get("testPrecision") != SEQUENTIAL_DATA_TEST_PRECISION:
            issues.append(f"Sequential CustomData testPrecision is {setup.get('testPrecision')!r}, expected {SEQUENTIAL_DATA_TEST_PRECISION!r}")
        if setup.get("session") != SEQUENTIAL_DATA_SESSION:
            issues.append(f"Sequential CustomData session is {setup.get('session')!r}, expected {SEQUENTIAL_DATA_SESSION!r}")
        if chart != SEQUENTIAL_DEFAULT_CHART_TARGET:
            issues.append(f"Sequential CustomData chart seed is {chart!r}, expected {SEQUENTIAL_DEFAULT_CHART_TARGET!r}")
        if custom.get("commission") != MC_CUSTOM_DATA_COMMISSION_TARGET:
            issues.append(f"Sequential CustomData commission is {custom.get('commission')!r}, expected {MC_CUSTOM_DATA_COMMISSION_TARGET!r}")
        if custom.get("mainTestValues") != SEQUENTIAL_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET:
            issues.append("Sequential CustomData MainTestValues drifted from Sequential dual-carrier target")

    guarded_text = (
        section_text(root, "Rankings")
        + section_text(root, "ATMs")
        + section_text(root, "RiskMoneyManagement")
        + section_text(root, "SelectedStrategies")
        + section_text(root, "CustomData")
    )
    for token in MC_BANNED_DONOR_TOKENS:
        if token in guarded_text:
            issues.append(f"Forbidden donor token leaked into Sequential static tabs: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into Sequential static tabs")

    for issue in enforce_sequential_passive_generation_guard(root):
        issues.append(f"Passive generation guard: {issue}")
    return issues


def update_sequential_static_tabs_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, SEQUENTIAL_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "sequential_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = sequential_static_tabs_summary(root)
    payload["actions"] = apply_sequential_static_tabs_to_root(root)
    payload["after"] = sequential_static_tabs_summary(root)
    payload["issues"] = enforce_sequential_static_tabs_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "rankings": SEQUENTIAL_RANKING_TARGET,
        "rankingConditions": [],
        "riskMoneyManagementMethods": RETEST1_RISK_MONEY_MANAGEMENT_METHOD_TARGET,
        "atms": RETEST1_ATMS_TARGET,
        "staticTabs": SEQUENTIAL_STATIC_TABS,
        "customDataMainTestValues": SEQUENTIAL_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET,
        "customDataCommission": MC_CUSTOM_DATA_COMMISSION_TARGET,
        "customDataCarrier": "dual_synced",
    }
    payload["targetRationale"] = {
        "decision": "Sequential static tabs close the last inert surfaces before phase closeout while keeping SequentialOptimization as the only active robustness decision.",
        "ranking": "Sequential pass/fail is owned by SequentialOptimization; Ranking must preserve failed rows and not run portfolio selection.",
        "riskMoneyManagement": "FixedSize keeps Capa1 retests comparable and avoids sizing noise.",
        "customData": "Sequential keeps SQX142-compatible Data+CustomData dual carrier synchronized; this block only hardens the CustomData tab without deleting Data.",
        "staticTabs": "ATMs, Notes and SelectedStrategies stay inert while executable behavior is guarded by previous Sequential blocks.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_sequential_static_tabs_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase8_sequential_static_tabs_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_sequential_static_tabs_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase8",
        "operation": "sequential_static_tabs_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase8_sequential_static_tabs_diff_review" if not apply else SEQUENTIAL_STATIC_TABS_NEXT,
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase8_sequential_static_tabs_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


SEQUENTIAL_CLOSEOUT_OPERATIONS = (
    (
        "dataDatabanksResourcesOptions",
        "sequential-data-databanks-resources-options-target",
        promote_sequential_data_databanks_resources_options_target,
    ),
    ("crosschecks", "sequential-crosschecks-target", promote_sequential_crosschecks_target),
    ("passiveGeneration", "sequential-passive-generation-target", promote_sequential_passive_generation_target),
    ("staticTabs", "sequential-static-tabs-target", promote_sequential_static_tabs_target),
)


def sequential_closeout_report(root142: Path, project_root: Path, target: str, write: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    operations: dict[str, Any] = {}
    issues: list[str] = []
    for key, command, runner in SEQUENTIAL_CLOSEOUT_OPERATIONS:
        result = runner(root142, project_root, target=target, apply=False)
        operation_issues = mc_closeout_operation_issues(command, result)
        operations[key] = {
            "command": command,
            "summary": mc_closeout_operation_summary(result),
            "issues": operation_issues,
        }
        issues.extend(operation_issues)

    previous_gate = mc2_closeout_report(root142, project_root, target=target, write=False)
    previous_issues = list(previous_gate.get("issues") or [])
    if previous_gate.get("ok") is not True:
        previous_issues.append("mc2-closeout-report: previous gate ok=false")
    issues.extend(previous_issues)

    process_probe = process_snapshot()
    process_warnings = []
    if process_probe.get("processes"):
        process_warnings.append("SQX processes are alive; closeout is XML/dry-run only, no SQX runtime mutation was attempted")

    payload: dict[str, Any] = {
        "ok": not issues,
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase8_sequential_closeout",
        "target": target,
        "write": write,
        "previousGate": {
            "phase": previous_gate.get("phase"),
            "ok": previous_gate.get("ok"),
            "issues": previous_issues,
            "nextPhase": previous_gate.get("nextPhase"),
        },
        "operations": operations,
        "issues": issues,
        "warnings": process_warnings,
        "processProbe": process_probe,
        "summary": {
            "decision": "Close Sequential after all Phase 8 guards are green and idempotent on local base and repo template.",
            "taskTitle": SEQUENTIAL_TASK_TITLE,
            "taskXml": SEQUENTIAL_TASK_XML,
            "chain": "Input=MC2 / Output=Sequential",
            "period": SEQUENTIAL_PERIOD_KEY,
            "testPrecision": SEQUENTIAL_DATA_TEST_PRECISION,
            "activeCrossCheck": SEQUENTIAL_ACTIVE_CROSSCHECK,
            "activeCrossCheckSettings": {
                "ApplyToStrategy": SEQUENTIAL_PARAMETER_SETTINGS_TARGET["ApplyToStrategy"],
                "DistributionUp": SEQUENTIAL_PARAMETER_SETTINGS_TARGET["DistributionUp"],
                "DistributionDown": SEQUENTIAL_PARAMETER_SETTINGS_TARGET["DistributionDown"],
                "Steps": SEQUENTIAL_PARAMETER_SETTINGS_TARGET["Steps"],
                "PctToPass": SEQUENTIAL_ACCEPTANCE_SETTINGS_TARGET["PctToPass"],
                "ResultsCount": SEQUENTIAL_ACCEPTANCE_SETTINGS_TARGET["ResultsCount"],
                "StabilityRange": SEQUENTIAL_ACCEPTANCE_SETTINGS_TARGET["StabilityRange"],
            },
            "passiveContract": {
                "improveDatabank": SEQUENTIAL_STRATEGY_TYPE_TARGET["improveDatabank"],
                "signals": 0,
                "stopLimitEntryBlocks": 0,
                "entry": "EnterAtMarket",
                "exit": "ExitAfterBars probability 100",
            },
            "staticContract": {
                "ranking": "inert",
                "deleteFailedStrategies": "false",
                "forceRunCrossChecks": "false",
                "fitPortfolio": "false",
                "customAnalysisFilter": "false",
                "riskMoneyManagement": "FixedSize",
                "atms": "disabled",
                "selectedStrategies": "empty",
                "customDataCarrier": "dual_synced",
            },
            "nextPhase": SEQUENTIAL_CLOSEOUT_NEXT,
            "closeoutCriterion": "all Sequential guards plus MC2 previous gate must be green and idempotent before opening Monkey Test",
            "noLiveRun": "This closeout only reads XML/local state and writes a phase report when requested.",
        },
        "nextPhase": SEQUENTIAL_CLOSEOUT_NEXT,
    }
    if write:
        target_path = ledger_root(project_root) / "phase_reports" / f"phase8_sequential_closeout_{stamp()}.json"
        write_json(target_path, payload)
        state_path = ledger_root(project_root) / "session_state.json"
        state = read_json(state_path, {})
        state.update({"updatedAt": now_iso(), "currentPhase": "phase8_sequential_closeout", "nextPhase": SEQUENTIAL_CLOSEOUT_NEXT})
        write_json(state_path, state)
        payload["written"] = str(target_path)
    return payload


def monkey_crosschecks_summary(root: ET.Element | None) -> dict[str, Any]:
    parent = find_section(root, "CrossChecks") if root is not None else None
    checks: list[dict[str, Any]] = []
    if parent is not None:
        for check in list(parent):
            if not isinstance(check.tag, str) or check.get("use") is None:
                continue
            methods = summarize_crosscheck_methods(check)
            checks.append({
                "id": check.tag,
                "use": check.get("use", ""),
                "numberOfSimulations": check.findtext("./Settings/NumberOfSimulations") or "",
                "mcUseFullSample": check.findtext("./Settings/MCUseFullSample") or "",
                "mcBacktestPrecision": check.findtext("./Settings/MCBacktestPrecision") or "",
                "methods": methods,
                "activeMethodTypes": [
                    method.get("type", "")
                    for method in methods
                    if method.get("use") == "true"
                ],
                "activeAcceptanceConditionCount": len([
                    condition
                    for condition in check.findall("./AcceptanceSettings/Conditions/Condition")
                    if condition.get("use", "true") != "false"
                ]),
                "conditions": [
                    mc_condition_summary(condition)
                    for condition in check.findall("./AcceptanceSettings/Conditions/Condition")
                ],
            })
    return {
        "exists": parent is not None,
        "attributes": dict(parent.attrib) if parent is not None else {},
        "active": [item["id"] for item in checks if item.get("use") == "true"],
        "checks": checks,
        "sha256": section_sha256(root, "CrossChecks") if root is not None else "",
    }


def monkey_open_summary(root: ET.Element | None) -> dict[str, Any]:
    if root is None:
        return {"exists": False}
    databanks = {
        node.get("name", ""): node.get("value", "")
        for node in root.findall(".//Databanks/Databank")
        if node.get("name")
    }
    params = {
        param.get("key", ""): (param.text or "")
        for param in root.findall(".//BuildTradingOptions/Params/Param")
        if param.get("key") in {
            "Session",
            "MarketOpenSession",
            "LimitTimeRange",
            "SignalTimeRangeFrom",
            "SignalTimeRangeTo",
            "RealisticGapsHandling",
            "StoreChartData",
        }
    }
    strategy_type = root.find(".//WhatToBuild/StrategyType")
    crosschecks = monkey_crosschecks_summary(root)
    active_check = next(
        (check for check in crosschecks.get("checks", []) if check.get("id") == MONKEY_ACTIVE_CROSSCHECK),
        {},
    )
    active_methods = [
        method
        for method in active_check.get("methods", [])
        if method.get("use") == "true"
    ]
    return {
        "exists": True,
        "data": {
            "exists": root.find("./Data") is not None,
            "setup": _setup_attrs(root.find("./Data/Setups/Setup")),
            "outOfSampleRanges": [dict(node.attrib) for node in root.findall("./Data/OutOfSample/Range")],
        },
        "customData": {
            "exists": root.find("./CustomData") is not None,
            "setup": _setup_attrs(root.find("./CustomData/Setups/Setup")),
        },
        "databanks": databanks,
        "resources": _tick_real_resource_summary(root),
        "optionsParams": params,
        "strategyType": dict(strategy_type.attrib) if strategy_type is not None else {},
        "passiveGeneration": retest1_passive_generation_summary(root),
        "crossChecks": crosschecks,
        "activeMonkeyMethod": active_methods[0] if active_methods else {},
    }


def monkey_open_issues(summary: dict[str, Any]) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    if not summary.get("exists"):
        return ["Monkey Test task missing"], warnings

    databanks = summary.get("databanks") or {}
    for name, wanted in MONKEY_EXPECTED_DATABANKS.items():
        if databanks.get(name) != wanted:
            issues.append(f"Monkey Test Databank {name} is {databanks.get(name)!r}, expected {wanted!r}")

    crosschecks = summary.get("crossChecks") or {}
    if not crosschecks.get("exists"):
        issues.append("Monkey Test CrossChecks section missing")
    else:
        attrs = crosschecks.get("attributes") or {}
        if attrs.get("use") != "true" or attrs.get("evaluateAll") != "true":
            issues.append("Monkey Test CrossChecks must stay active/evaluateAll for RealMonkeyTest")
        active = crosschecks.get("active") or []
        if active != [MONKEY_ACTIVE_CROSSCHECK]:
            issues.append(f"Monkey Test active crosschecks are {active!r}, expected only {MONKEY_ACTIVE_CROSSCHECK!r}")
        checks = {item.get("id"): item for item in crosschecks.get("checks") or []}
        monte_carlo = checks.get(MONKEY_ACTIVE_CROSSCHECK) or {}
        if monte_carlo.get("numberOfSimulations") != MONKEY_NUMBER_OF_SIMULATIONS:
            issues.append(f"Monkey Test NumberOfSimulations is {monte_carlo.get('numberOfSimulations')!r}, expected {MONKEY_NUMBER_OF_SIMULATIONS!r}")
        if monte_carlo.get("mcUseFullSample") != MONKEY_USE_FULL_SAMPLE:
            issues.append(f"Monkey Test MCUseFullSample is {monte_carlo.get('mcUseFullSample')!r}, expected {MONKEY_USE_FULL_SAMPLE!r}")
        active_methods = monte_carlo.get("activeMethodTypes") or []
        if active_methods != [MONKEY_ACTIVE_METHOD]:
            issues.append(f"Monkey Test active methods are {active_methods!r}, expected only {MONKEY_ACTIVE_METHOD!r}")
        method = summary.get("activeMonkeyMethod") or {}
        params = method.get("params") or {}
        if params.get("MaxChange") != MONKEY_METHOD_MAX_CHANGE:
            issues.append(f"Monkey Test RealMonkeyTest MaxChange is {params.get('MaxChange')!r}, expected {MONKEY_METHOD_MAX_CHANGE!r}")
        if monte_carlo.get("activeAcceptanceConditionCount") == 0:
            warnings.append("Monkey Test acceptance filter conditions are currently inactive; next block must decide whether to keep filters advisory/off or activate them.")
        inactive_with_active_methods = [
            {
                "check": check.get("id"),
                "methods": check.get("activeMethodTypes") or [],
            }
            for check in crosschecks.get("checks") or []
            if check.get("id") != MONKEY_ACTIVE_CROSSCHECK and check.get("use") == "false" and check.get("activeMethodTypes")
        ]
        if inactive_with_active_methods:
            warnings.append(f"Monkey Test inactive crosschecks still carry active methods {inactive_with_active_methods!r}; next CrossChecks block should make them inert if we keep the Sequential discipline.")

    strategy_type = summary.get("strategyType") or {}
    improve_databank = strategy_type.get("improveDatabank", "")
    if improve_databank and improve_databank != "Sequential":
        warnings.append(f"Monkey Test StrategyType.improveDatabank is {improve_databank!r}; next passive-generation block should normalize it to Sequential if needed")

    if (summary.get("data") or {}).get("exists") and (summary.get("customData") or {}).get("exists"):
        warnings.append("Monkey Test currently carries both Data and CustomData; next block must choose the canonical data carrier before mutation")

    return issues, warnings


def monkey_open_target_report(cfx: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256": file_sha256(cfx) if cfx.is_file() else "",
        "taskTitle": MONKEY_TASK_TITLE,
        "taskXml": "",
        "summary": {},
        "issues": [],
        "warnings": [],
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["issues"].append("missing_or_not_zip")
        payload["ok"] = False
        return payload
    task_xml_name, root = load_task_root(cfx, MONKEY_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["issues"].append("monkey_test_task_not_found")
        payload["ok"] = False
        return payload
    if task_xml_name != MONKEY_TASK_XML:
        payload["warnings"].append(f"Monkey Test task XML is {task_xml_name!r}, expected {MONKEY_TASK_XML!r}")
    payload["summary"] = monkey_open_summary(root)
    issues, warnings = monkey_open_issues(payload["summary"])
    payload["issues"] = issues
    payload["warnings"].extend(warnings)
    payload["ok"] = not issues
    return payload


def monkey_open_report(root142: Path, project_root: Path, target: str, write: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    target_reports = {
        name: monkey_open_target_report(path)
        for name, path in targets.items()
    }
    previous_gate = sequential_closeout_report(root142, project_root, target=target, write=False)
    previous_issues = list(previous_gate.get("issues") or [])
    if previous_gate.get("ok") is not True:
        previous_issues.append("sequential-closeout-report: previous gate ok=false")
    process_probe = process_snapshot()
    process_warnings = []
    if process_probe.get("processes"):
        process_warnings.append("SQX processes are alive; keep phase 9 open read-only until SQX is closed")
    payload: dict[str, Any] = {
        "ok": all(item.get("ok") for item in target_reports.values()) and not previous_issues,
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase9_monkey_test_open",
        "target": target,
        "write": write,
        "previousGate": {
            "phase": previous_gate.get("phase"),
            "ok": previous_gate.get("ok"),
            "issues": previous_issues,
            "nextPhase": previous_gate.get("nextPhase"),
        },
        "targets": target_reports,
        "warnings": process_warnings + [
            warning
            for item in target_reports.values()
            for warning in item.get("warnings", [])
        ],
        "processProbe": process_probe,
        "summary": {
            "decision": "Open Monkey Test as Phase 9 after Sequential closeout; inspect structure before applying target values.",
            "taskTitle": MONKEY_TASK_TITLE,
            "taskXml": MONKEY_TASK_XML,
            "chain": "Input=Sequential / Output=Monkey Test",
            "activeCrossCheck": MONKEY_ACTIVE_CROSSCHECK,
            "activeMethod": MONKEY_ACTIVE_METHOD,
            "numberOfSimulations": MONKEY_NUMBER_OF_SIMULATIONS,
            "mcUseFullSample": MONKEY_USE_FULL_SAMPLE,
            "methodMaxChange": MONKEY_METHOD_MAX_CHANGE,
            "naturalResults": "Preserve natural passed/failed outcomes; never force Results=passed.",
            "noLiveRun": "This gate only reads XML/local state and writes a phase report when requested.",
            "decisionPending": [
                "Data/Databanks/Resources/Options must decide the canonical carrier and keep generator-owned asset/timeframe/spread resources.",
                "CrossChecks must decide whether inactive acceptance filters remain advisory/off or become explicit filters.",
                "Passive-generation/static tabs must keep Monkey from generating or altering strategy logic.",
            ],
        },
        "nextPhase": MONKEY_NEXT_PHASE,
    }
    if write:
        target_path = ledger_root(project_root) / "phase_reports" / f"phase9_monkey_test_open_{stamp()}.json"
        write_json(target_path, payload)
        state_path = ledger_root(project_root) / "session_state.json"
        state = read_json(state_path, {})
        state.update({"updatedAt": now_iso(), "currentPhase": "phase9_monkey_test_open", "nextPhase": MONKEY_NEXT_PHASE})
        write_json(state_path, state)
        payload["written"] = str(target_path)
    return payload


def monkey_data_databanks_resources_options_summary(root: ET.Element | None) -> dict[str, Any]:
    summary = monkey_open_summary(root)
    if not summary.get("exists"):
        return summary
    setup_pairs = []
    data_setup = root.find("./Data/Setups/Setup") if root is not None else None
    custom_setup = root.find("./CustomData/Setups/Setup") if root is not None else None
    if data_setup is not None and custom_setup is not None:
        setup_pairs.append({
            "field": "Data_vs_CustomData",
            "data": {
                "dateFrom": data_setup.get("dateFrom", ""),
                "dateTo": data_setup.get("dateTo", ""),
                "testPrecision": data_setup.get("testPrecision", ""),
                "session": data_setup.get("session", ""),
                "slippage": data_setup.get("slippage", ""),
                "minDist": data_setup.get("minDist", ""),
                "chart": dict(data_setup.find("Chart").attrib) if data_setup.find("Chart") is not None else {},
            },
            "customData": {
                "dateFrom": custom_setup.get("dateFrom", ""),
                "dateTo": custom_setup.get("dateTo", ""),
                "testPrecision": custom_setup.get("testPrecision", ""),
                "session": custom_setup.get("session", ""),
                "slippage": custom_setup.get("slippage", ""),
                "minDist": custom_setup.get("minDist", ""),
                "chart": dict(custom_setup.find("Chart").attrib) if custom_setup.find("Chart") is not None else {},
            },
        })
    summary["carrierDecision"] = {
        "mode": "dual_synced",
        "reason": "Monkey Test in SQX142 stores both Data and CustomData; keep both synced for compatibility and leave asset/timeframe/spread to Project Generator in generated customs.",
        "pairs": setup_pairs,
    }
    return summary


def apply_monkey_setup_to_root(root: ET.Element, section_name: str, engine: str, actions: list[dict[str, Any]]) -> ET.Element:
    section = find_section(root, section_name)
    if section is None:
        section = ET.SubElement(root, section_name)
        actions.append({"field": section_name, "from": None, "to": "created", "changed": True})
    setup = ensure_setup_under(section, actions, section_name)
    period = generator_period(MONKEY_PERIOD_KEY)
    set_attrs_on_node(
        setup,
        {
            "dateFrom": period[0],
            "dateTo": period[1],
            "testPrecision": MONKEY_DATA_TEST_PRECISION,
            "session": MONKEY_DATA_SESSION,
            "slippage": "0",
            "minDist": "0",
            "engine": engine,
        },
        actions,
        f"{section_name}/Setup:attrs",
    )
    chart = setup.find("Chart")
    if chart is None:
        chart = ET.SubElement(setup, "Chart")
        actions.append({"field": f"{section_name}/Setup/Chart", "from": None, "to": dict(chart.attrib), "changed": True})
    set_attrs_on_node(chart, MONKEY_DEFAULT_CHART_TARGET, actions, f"{section_name}/Setup/Chart:attrs")
    ensure_commission_method(setup, actions, f"{section_name}/Setup")
    if section_name == "CustomData":
        main_values = setup.find("MainTestValues")
        if main_values is None:
            main_values = ET.SubElement(setup, "MainTestValues")
            actions.append({"field": "CustomData/MainTestValues", "from": None, "to": dict(main_values.attrib), "changed": True})
        set_attrs_on_node(
            main_values,
            MONKEY_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET,
            actions,
            "CustomData/MainTestValues:attrs",
        )
    return setup


def apply_monkey_data_databanks_resources_options_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    data_setup = apply_monkey_setup_to_root(root, "Data", MONKEY_DATA_ENGINE, actions)
    custom_setup = apply_monkey_setup_to_root(root, "CustomData", MONKEY_CUSTOM_DATA_ENGINE, actions)

    data = find_section(root, "Data")
    out_of_sample = data.find("OutOfSample") if data is not None else None
    removed_oos = []
    if out_of_sample is not None:
        for range_node in list(out_of_sample.findall("Range")):
            removed_oos.append(dict(range_node.attrib))
            out_of_sample.remove(range_node)
    actions.append({
        "field": "Data/OutOfSample/Range",
        "from": removed_oos,
        "to": [],
        "changed": bool(removed_oos),
        "note": "Monkey Test is a robustness gate after Sequential survivors and does not add a nested OOS split.",
    })

    databanks = find_section(root, "Databanks")
    if databanks is None:
        databanks = ET.SubElement(root, "Databanks", {"retestSelected": "false"})
        actions.append({"field": "Databanks", "from": None, "to": dict(databanks.attrib), "changed": True})
    existing_by_name = {
        node.get("name", ""): node
        for node in databanks.findall("Databank")
        if node.get("name")
    }
    for name, wanted in MONKEY_EXPECTED_DATABANKS.items():
        node = existing_by_name.get(name)
        before = dict(node.attrib) if node is not None else None
        if node is None:
            node = ET.SubElement(databanks, "Databank", {"name": name})
        node.set("name", name)
        node.set("value", wanted)
        node.set("label", f"{name} databank")
        actions.append({
            "field": f"Databanks/{name}",
            "from": before,
            "to": dict(node.attrib),
            "changed": before != dict(node.attrib),
        })

    apply_mc2_resources_from_custom_data(root, custom_setup, actions)
    for key, value in MONKEY_OPTIONS_PARAMS_TARGET.items():
        set_param_text(root, key, value, actions, "Options")
    actions.append({
        "field": "Monkey/DataCarrier",
        "from": {
            "data": value_for_node(data_setup),
            "customData": value_for_node(custom_setup),
        },
        "to": "dual_synced",
        "changed": False,
        "note": "Kept both Data and CustomData for SQX142 compatibility; enforced matching period, precision, session and chart seed.",
    })
    return actions


def enforce_monkey_data_databanks_resources_options_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    period = generator_period(MONKEY_PERIOD_KEY)
    data_setup = root.find("./Data/Setups/Setup")
    custom_setup = root.find("./CustomData/Setups/Setup")
    if data_setup is None:
        issues.append("Monkey Test Data/Setup missing")
    if custom_setup is None:
        issues.append("Monkey Test CustomData/Setup missing")
    for label, setup in (("Data", data_setup), ("CustomData", custom_setup)):
        if setup is None:
            continue
        if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
            issues.append(f"Monkey Test {label} dates are not {MONKEY_PERIOD_KEY}")
        if setup.get("testPrecision") != MONKEY_DATA_TEST_PRECISION:
            issues.append(f"Monkey Test {label} testPrecision must stay {MONKEY_DATA_TEST_PRECISION}")
        if setup.get("session") != MONKEY_DATA_SESSION:
            issues.append(f"Monkey Test {label} session must stay {MONKEY_DATA_SESSION}")
        chart = setup.find("Chart")
        if chart is None:
            issues.append(f"Monkey Test {label} chart missing")
        else:
            for key, wanted in MONKEY_DEFAULT_CHART_TARGET.items():
                if chart.get(key) != wanted:
                    issues.append(f"Monkey Test {label} chart {key} is {chart.get(key)!r}, expected {wanted!r}")
        commission = setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']")
        if (commission.text if commission is not None else "") != MC_CUSTOM_DATA_COMMISSION_TARGET:
            issues.append(f"Monkey Test {label} commission is {(commission.text if commission is not None else '')!r}, expected {MC_CUSTOM_DATA_COMMISSION_TARGET!r}")
    if data_setup is not None and custom_setup is not None:
        data_chart = data_setup.find("Chart")
        custom_chart = custom_setup.find("Chart")
        for key in ("dateFrom", "dateTo", "testPrecision", "session", "slippage", "minDist"):
            if data_setup.get(key) != custom_setup.get(key):
                issues.append(f"Monkey Test Data/CustomData setup mismatch for {key}")
        if data_chart is not None and custom_chart is not None:
            for key in ("symbol", "timeframe", "spread"):
                if data_chart.get(key) != custom_chart.get(key):
                    issues.append(f"Monkey Test Data/CustomData chart mismatch for {key}")
    main_values = root.find("./CustomData/Setups/Setup/MainTestValues")
    if main_values is None or dict(main_values.attrib) != MONKEY_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET:
        issues.append("Monkey Test CustomData MainTestValues drifted from dual-synced target")

    databanks = {
        node.get("name", ""): node.get("value", "")
        for node in root.findall(".//Databanks/Databank")
        if node.get("name")
    }
    for name, wanted in MONKEY_EXPECTED_DATABANKS.items():
        if databanks.get(name) != wanted:
            issues.append(f"Monkey Test Databank {name} is {databanks.get(name)!r}, expected {wanted!r}")

    resources = find_section(root, "Resources")
    if resources is None:
        issues.append("Monkey Test Resources missing")
    else:
        chart_symbols = {
            chart.get("symbol", "")
            for chart in root.findall("./CustomData/Setups/Setup/Chart")
            if chart.get("symbol")
        }
        resource_symbols = {
            symbol.get("name", "")
            for symbol in resources.findall("./Symbols/Symbol")
            if symbol.get("name")
        }
        if chart_symbols != resource_symbols:
            issues.append(f"Monkey Test custom chart/resource mismatch: charts={sorted(chart_symbols)} resources={sorted(resource_symbols)}")
        broker_ids = {
            broker.get("id", "")
            for broker in resources.findall("./Brokers/Broker")
            if broker.get("id")
        }
        for symbol in resources.findall("./Symbols/Symbol"):
            if symbol.get("precision") != MC_RESOURCE_PRECISION:
                issues.append(f"Monkey Test resource {symbol.get('name')} precision is not TICK")
            if symbol.get("timezone") != MC_RESOURCE_TIMEZONE:
                issues.append(f"Monkey Test resource {symbol.get('name')} timezone is not EETUS")
            if symbol.get("broker") not in broker_ids:
                issues.append(f"Monkey Test resource {symbol.get('name')} references missing broker {symbol.get('broker')}")
            info = symbol.find("InstrumentInfo")
            if info is None:
                issues.append(f"Monkey Test resource {symbol.get('name')} has no nested InstrumentInfo")
            elif info.get("broker") not in broker_ids:
                issues.append(f"Monkey Test nested InstrumentInfo for {symbol.get('name')} references missing broker {info.get('broker')}")
        if resources.findall("./Sessions/Session"):
            issues.append("Monkey Test resources must not keep session entries")

    params = {
        param.get("key", ""): (param.text or "")
        for param in root.findall(".//BuildTradingOptions/Params/Param")
        if param.get("key") in MONKEY_OPTIONS_PARAMS_TARGET
    }
    for key, wanted in MONKEY_OPTIONS_PARAMS_TARGET.items():
        if params.get(key) != wanted:
            issues.append(f"Monkey Test Options param {key} is {params.get(key)!r}, expected {wanted!r}")

    if root.findall("./Data/OutOfSample/Range"):
        issues.append("Monkey Test Data must not contain nested OOS ranges")
    guarded_text = (
        section_text(root, "Data")
        + section_text(root, "CustomData")
        + section_text(root, "Databanks")
        + section_text(root, "Resources")
        + section_text(root, "Options")
    )
    for token in MC_BANNED_DONOR_TOKENS:
        if token in guarded_text:
            issues.append(f"Forbidden donor token leaked into Monkey Test Data/Databanks/Resources/Options: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into Monkey Test Data/Databanks/Resources/Options")
    return issues


def update_monkey_data_databanks_resources_options_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload
    task_xml_name, root = load_task_root(cfx, MONKEY_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "monkey_test_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = monkey_data_databanks_resources_options_summary(root)
    payload["actions"] = apply_monkey_data_databanks_resources_options_to_root(root)
    payload["after"] = monkey_data_databanks_resources_options_summary(root)
    payload["issues"] = enforce_monkey_data_databanks_resources_options_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["xmlChanged"] = before_text != after_text
    payload["changed"] = payload["changedActionCount"] > 0
    payload["targetValues"] = {
        "taskTitle": MONKEY_TASK_TITLE,
        "taskXml": MONKEY_TASK_XML,
        "periodKey": MONKEY_PERIOD_KEY,
        "dateFrom": generator_period(MONKEY_PERIOD_KEY)[0],
        "dateTo": generator_period(MONKEY_PERIOD_KEY)[1],
        "dataCarrier": "dual_synced",
        "dataEngine": MONKEY_DATA_ENGINE,
        "customDataEngine": MONKEY_CUSTOM_DATA_ENGINE,
        "customDataMainTestValues": MONKEY_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET,
        "databanks": MONKEY_EXPECTED_DATABANKS,
        "resourcePrecision": MC_RESOURCE_PRECISION,
        "resourceTimezone": MC_RESOURCE_TIMEZONE,
        "options": MONKEY_OPTIONS_PARAMS_TARGET,
    }
    payload["targetRationale"] = {
        "methodology": "Monkey Test consumes Sequential survivors and performs a robustness perturbation; it is not a new OOS split or optimizer in Capa1.",
        "carrier": "SQX142 Monkey Test carries both Data and CustomData in the working base; keeping both synced is safer than deleting one without UI evidence.",
        "options": "Trading time ranges are disabled for this robustness gate in the base/template; Project Generator should not inject them for Monkey Test.",
        "naturalResults": "The block preserves natural passed/failed rows and does not force Results=passed.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_monkey_data_databanks_resources_options_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase9_monkey_test_data_databanks_resources_options_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_monkey_data_databanks_resources_options_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase9",
        "operation": "monkey_test_data_databanks_resources_options_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase9_monkey_test_data_databanks_resources_options_diff_review" if not apply else MONKEY_DATA_DATABANKS_RESOURCES_OPTIONS_NEXT,
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase9_monkey_test_data_databanks_resources_options_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def set_monkey_acceptance_conditions(check: ET.Element, actions: list[dict[str, Any]]) -> None:
    acceptance = ensure_direct_child(check, "AcceptanceSettings")
    conditions = acceptance.find("Conditions")
    if conditions is None:
        conditions = ET.SubElement(acceptance, "Conditions")
        before: list[dict[str, Any]] = []
    else:
        before = [mc_condition_summary(condition) for condition in conditions.findall("Condition")]
        for child in list(conditions):
            conditions.remove(child)
    conditions.attrib.clear()
    conditions.set("CrossCheck", MONKEY_ACTIVE_CROSSCHECK)
    conditions.text = "\n          "
    for index, target in enumerate(MONKEY_ACCEPTANCE_CONDITIONS_TARGET):
        condition = make_mc_ratio_condition(target)
        condition.tail = "\n        " if index == len(MONKEY_ACCEPTANCE_CONDITIONS_TARGET) - 1 else "\n          "
        conditions.append(condition)
    after = [mc_condition_summary(condition) for condition in conditions.findall("Condition")]
    actions.append({
        "field": "CrossChecks/MonteCarloRetest/AcceptanceSettings/Conditions",
        "from": before,
        "to": after,
        "changed": before != after,
        "note": "Monkey filters are active acceptance filters, not advisory-only rows; they preserve natural passed/failed results.",
    })


def normalize_monkey_crosscheck_setups(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    period = generator_period(MONKEY_PERIOD_KEY)
    before: list[dict[str, Any]] = []
    after: list[dict[str, Any]] = []
    for setup in root.findall(".//CrossChecks/*/Settings/Setups/Setup"):
        before.append({
            "attrs": dict(setup.attrib),
            "charts": [dict(chart.attrib) for chart in setup.findall("Chart")],
        })
        for key, wanted in {
            "dateFrom": period[0],
            "dateTo": period[1],
            "testPrecision": MONKEY_DATA_TEST_PRECISION,
            "session": MONKEY_DATA_SESSION,
            "slippage": "0",
            "minDist": "0",
        }.items():
            setup.set(key, wanted)
        charts = setup.findall("Chart")
        if not charts:
            charts = [ET.SubElement(setup, "Chart")]
        for chart in charts:
            for key, value in MONKEY_DEFAULT_CHART_TARGET.items():
                chart.set(key, value)
        after.append({
            "attrs": dict(setup.attrib),
            "charts": [dict(chart.attrib) for chart in setup.findall("Chart")],
        })
    actions.append({
        "field": "CrossChecks/*/Settings/Setups/Setup",
        "from": before,
        "to": after,
        "changed": before != after,
        "note": "Inactive nested crosscheck setups are normalized to the same safe seed; RealMonkeyTest itself remains the only active Monkey method.",
    })


def apply_monkey_crosschecks_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    parent = find_section(root, "CrossChecks")
    if parent is None:
        parent = ET.SubElement(root, "CrossChecks")
        actions.append({"field": "CrossChecks", "from": None, "to": dict(parent.attrib), "changed": True})
    set_attrs_on_node(parent, MONKEY_CROSSCHECK_PARENT_TARGET, actions, "CrossChecks:attrs")

    active = parent.find(MONKEY_ACTIVE_CROSSCHECK)
    if active is None:
        active = ET.SubElement(parent, MONKEY_ACTIVE_CROSSCHECK, {"use": "true"})
        actions.append({"field": f"CrossChecks/{MONKEY_ACTIVE_CROSSCHECK}", "from": None, "to": dict(active.attrib), "changed": True})

    for check in list(parent):
        if not isinstance(check.tag, str) or check.get("use") is None:
            continue
        before_use = check.get("use", "")
        wanted_use = "true" if check.tag == MONKEY_ACTIVE_CROSSCHECK else "false"
        check.set("use", wanted_use)
        actions.append({
            "field": f"CrossChecks/{check.tag}:use",
            "from": before_use,
            "to": wanted_use,
            "changed": before_use != wanted_use,
        })
        for method in check.findall("./Settings/Methods/Method"):
            method_type = method.get("type", "")
            wanted_method = "true" if check.tag == MONKEY_ACTIVE_CROSSCHECK and method_type == MONKEY_ACTIVE_METHOD else "false"
            before_method = method.get("use", "")
            method.set("use", wanted_method)
            actions.append({
                "field": f"CrossChecks/{check.tag}/Method:{method_type}:use",
                "from": before_method,
                "to": wanted_method,
                "changed": before_method != wanted_method,
            })

    settings = ensure_direct_child(active, "Settings")
    for tag, wanted in (
        ("NumberOfSimulations", MONKEY_NUMBER_OF_SIMULATIONS),
        ("MCUseFullSample", MONKEY_USE_FULL_SAMPLE),
        ("MCBacktestPrecision", "-1"),
    ):
        set_or_create_text_child(settings, tag, wanted, actions, f"CrossChecks/{MONKEY_ACTIVE_CROSSCHECK}/Settings/{tag}")

    methods = ensure_direct_child(settings, "Methods")
    method = None
    for item in methods.findall("Method"):
        if item.get("type") == MONKEY_ACTIVE_METHOD:
            method = item
            break
    if method is None:
        method = ET.SubElement(methods, "Method", {"type": MONKEY_ACTIVE_METHOD, "use": "true"})
        actions.append({"field": f"CrossChecks/{MONKEY_ACTIVE_CROSSCHECK}/Method:{MONKEY_ACTIVE_METHOD}", "from": None, "to": dict(method.attrib), "changed": True})
    before_use = method.get("use", "")
    method.set("use", "true")
    actions.append({
        "field": f"CrossChecks/{MONKEY_ACTIVE_CROSSCHECK}/Method:{MONKEY_ACTIVE_METHOD}:use",
        "from": before_use,
        "to": "true",
        "changed": before_use != "true",
    })
    set_method_param(
        method,
        "MaxChange",
        MONKEY_METHOD_MAX_CHANGE,
        "Integer",
        actions,
        f"CrossChecks/{MONKEY_ACTIVE_CROSSCHECK}/Method:{MONKEY_ACTIVE_METHOD}/Param:MaxChange",
    )
    set_monkey_acceptance_conditions(active, actions)
    normalize_monkey_crosscheck_setups(root, actions)
    return actions


def monkey_acceptance_conditions_ok(root: ET.Element) -> bool:
    check = root.find(f".//CrossChecks/{MONKEY_ACTIVE_CROSSCHECK}")
    if check is None:
        return False
    conditions = [
        mc_condition_summary(condition)
        for condition in check.findall("./AcceptanceSettings/Conditions/Condition")
    ]
    expected = [
        {"use": "true", "left": item["left"], "comparator": item["comparator"], "right": item["right"]}
        for item in MONKEY_ACCEPTANCE_CONDITIONS_TARGET
    ]
    return conditions == expected


def enforce_monkey_crosschecks_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = monkey_crosschecks_summary(root)
    attrs = summary.get("attributes") or {}
    if attrs != MONKEY_CROSSCHECK_PARENT_TARGET:
        issues.append(f"Monkey Test CrossChecks attrs are {attrs!r}, expected {MONKEY_CROSSCHECK_PARENT_TARGET!r}")
    if summary.get("active") != [MONKEY_ACTIVE_CROSSCHECK]:
        issues.append(f"Monkey Test active crosschecks are {summary.get('active')!r}, expected [{MONKEY_ACTIVE_CROSSCHECK!r}]")

    checks = {item.get("id"): item for item in summary.get("checks") or []}
    active = checks.get(MONKEY_ACTIVE_CROSSCHECK) or {}
    if active.get("numberOfSimulations") != MONKEY_NUMBER_OF_SIMULATIONS:
        issues.append(f"Monkey Test NumberOfSimulations is {active.get('numberOfSimulations')!r}, expected {MONKEY_NUMBER_OF_SIMULATIONS!r}")
    if active.get("mcUseFullSample") != MONKEY_USE_FULL_SAMPLE:
        issues.append(f"Monkey Test MCUseFullSample is {active.get('mcUseFullSample')!r}, expected {MONKEY_USE_FULL_SAMPLE!r}")
    if active.get("mcBacktestPrecision") != "-1":
        issues.append(f"Monkey Test MCBacktestPrecision is {active.get('mcBacktestPrecision')!r}, expected '-1'")
    active_methods = active.get("activeMethodTypes") or []
    if active_methods != [MONKEY_ACTIVE_METHOD]:
        issues.append(f"Monkey Test active methods are {active_methods!r}, expected [{MONKEY_ACTIVE_METHOD!r}]")
    method = next((item for item in active.get("methods") or [] if item.get("type") == MONKEY_ACTIVE_METHOD), {})
    if (method.get("params") or {}).get("MaxChange") != MONKEY_METHOD_MAX_CHANGE:
        issues.append(f"Monkey Test RealMonkeyTest MaxChange is {(method.get('params') or {}).get('MaxChange')!r}, expected {MONKEY_METHOD_MAX_CHANGE!r}")
    if not monkey_acceptance_conditions_ok(root):
        issues.append("Monkey Test acceptance conditions must be active NetProfit >= 50% main and Max DD <= 200% main")

    for check in summary.get("checks") or []:
        if check.get("id") == MONKEY_ACTIVE_CROSSCHECK:
            continue
        active_methods_in_disabled = [method for method in check.get("methods") or [] if method.get("use") == "true"]
        if active_methods_in_disabled:
            issues.append(f"Inactive Monkey crosscheck {check.get('id')} still has active methods: {[item.get('type') for item in active_methods_in_disabled]}")

    period = generator_period(MONKEY_PERIOD_KEY)
    for setup in root.findall(".//CrossChecks/*/Settings/Setups/Setup"):
        if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
            issues.append(f"Monkey nested CrossChecks setup dates drifted: {dict(setup.attrib)!r}")
        if setup.get("testPrecision") != MONKEY_DATA_TEST_PRECISION:
            issues.append(f"Monkey nested CrossChecks setup precision is {setup.get('testPrecision')!r}, expected {MONKEY_DATA_TEST_PRECISION!r}")
        if setup.get("session") != MONKEY_DATA_SESSION:
            issues.append(f"Monkey nested CrossChecks setup session is {setup.get('session')!r}, expected {MONKEY_DATA_SESSION!r}")
        if setup.get("slippage") != "0" or setup.get("minDist") != "0":
            issues.append(f"Monkey nested CrossChecks setup costs drifted: {dict(setup.attrib)!r}")
        for chart in setup.findall("Chart"):
            for key, wanted in MONKEY_DEFAULT_CHART_TARGET.items():
                if chart.get(key) != wanted:
                    issues.append(f"Monkey nested CrossChecks chart {key} is {chart.get(key)!r}, expected {wanted!r}")

    rankings = find_section(root, "Rankings")
    if rankings is not None and (rankings.findtext("ForceRunCrossChecks") or "") != "false":
        issues.append("Monkey Test Rankings/ForceRunCrossChecks must remain false")

    for issue in enforce_monkey_data_databanks_resources_options_guard(root):
        issues.append(f"Data/Resources guard: {issue}")

    guarded_text = section_text(root, "CrossChecks")
    for token in MC_BANNED_DONOR_TOKENS:
        if token in guarded_text:
            issues.append(f"Forbidden donor token leaked into Monkey Test CrossChecks: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into Monkey Test CrossChecks")
    return issues


def update_monkey_crosschecks_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload
    task_xml_name, root = load_task_root(cfx, MONKEY_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "monkey_test_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = monkey_crosschecks_summary(root)
    payload["actions"] = apply_monkey_crosschecks_to_root(root)
    payload["after"] = monkey_crosschecks_summary(root)
    payload["issues"] = enforce_monkey_crosschecks_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["xmlChanged"] = before_text != after_text
    payload["changed"] = payload["changedActionCount"] > 0
    payload["targetValues"] = {
        "taskTitle": MONKEY_TASK_TITLE,
        "taskXml": MONKEY_TASK_XML,
        "parent": MONKEY_CROSSCHECK_PARENT_TARGET,
        "onlyActiveCheck": MONKEY_ACTIVE_CROSSCHECK,
        "onlyActiveMethod": MONKEY_ACTIVE_METHOD,
        "numberOfSimulations": MONKEY_NUMBER_OF_SIMULATIONS,
        "mcUseFullSample": MONKEY_USE_FULL_SAMPLE,
        "mcBacktestPrecision": "-1",
        "realMonkeyMaxChange": MONKEY_METHOD_MAX_CHANGE,
        "acceptanceConditions": MONKEY_ACCEPTANCE_CONDITIONS_TARGET,
        "nestedSetupPeriod": MONKEY_PERIOD_KEY,
        "nestedSetupChartSeed": MONKEY_DEFAULT_CHART_TARGET,
    }
    payload["targetRationale"] = {
        "methodology": "Monkey Test is the RealMonkeyTest robustness perturbation after Sequential survivors; SyntheticBootstrap methods stay disabled for the later Synthetic/Syntetic task.",
        "filters": "The two acceptance rows are active filters, not advisory-only rows: MC retest net profit must keep at least 50% of main net profit and MC retest max DD must stay within 200% of main DD.",
        "academic": "A robustness gate should reject fragile candidates but not become a new optimizer; preserving fixed filters and natural failed/passed rows reduces selection drift.",
        "cleanup": "Methods hidden inside inactive crosschecks are switched off so stale MonteCarloManipulation/WhatIf/Synthetic settings cannot execute accidentally.",
        "naturalResults": "No Results value is forced; passed/failed must remain the natural SQX outcome.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_monkey_crosschecks_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase9_monkey_test_crosschecks_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_monkey_crosschecks_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase9",
        "operation": "monkey_test_crosschecks_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase9_monkey_test_crosschecks_diff_review" if not apply else MONKEY_CROSSCHECKS_NEXT,
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase9_monkey_test_crosschecks_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def apply_monkey_what_to_build_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    what_to_build = find_section(root, "WhatToBuild")
    if what_to_build is None:
        what_to_build = ET.SubElement(root, "WhatToBuild")
        actions.append({"field": "WhatToBuild", "from": None, "to": "created", "changed": True})

    set_or_create_attrs_child(
        what_to_build,
        "StrategyType",
        MONKEY_STRATEGY_TYPE_TARGET,
        actions,
        "WhatToBuild/StrategyType",
    )
    build_mode = what_to_build.find("BuildMode")
    if build_mode is None:
        build_mode = ET.SubElement(what_to_build, "BuildMode", {"generationType": "random-generation"})
        actions.append({"field": "WhatToBuild/BuildMode", "from": None, "to": dict(build_mode.attrib), "changed": True})
    else:
        actions.append({
            "field": "WhatToBuild/BuildMode:generationType",
            "from": build_mode.get("generationType", ""),
            "to": build_mode.get("generationType", ""),
            "changed": False,
            "note": "left as SQX-known placeholder; Monkey Test passive behavior is enforced by Sequential input, disabled improve parts and disabled evolution toggles",
        })
    for tag, value in MONKEY_PASSIVE_BUILDMODE_TEXT_TARGET.items():
        set_or_create_text_child(build_mode, tag, value, actions, f"WhatToBuild/BuildMode/{tag}")
    for tag, attrs in MONKEY_PASSIVE_BUILDMODE_ATTR_TARGET.items():
        set_or_update_attrs_child(build_mode, tag, attrs, actions, f"WhatToBuild/BuildMode/{tag}")


def apply_monkey_blocks_to_root(root: ET.Element, source_root: ET.Element | None, actions: list[dict[str, Any]]) -> None:
    blocks = find_blocks(root)
    if blocks is None:
        blocks = ET.SubElement(root, "Blocks", {"type": "simple", "version": "142.2336"})
        actions.append({"field": "Blocks", "from": None, "to": dict(blocks.attrib), "changed": True})

    before_attrs = dict(blocks.attrib)
    blocks.set("type", "simple")
    blocks.set("version", "142.2336")
    actions.append({
        "field": "Blocks:attrs",
        "from": before_attrs,
        "to": dict(blocks.attrib),
        "changed": before_attrs != dict(blocks.attrib),
    })

    source_blocks = find_blocks(source_root)
    if blocks.find("BuildingBlocks") is None and source_blocks is not None:
        actions.append(replace_building_blocks_from_source(blocks, source_blocks))
    else:
        actions.append({
            "field": "BuildingBlocks",
            "changed": False,
            "note": "preserved existing Monkey Test building-block universe; passive gate only enforces no-improve, entry and exit contracts",
        })
    if source_blocks is not None:
        for child_name in ("OrderTypes", "ExitTypes"):
            if blocks.find(child_name) is None and source_blocks.find(child_name) is not None:
                blocks.append(ET.fromstring(serialize_xml(source_blocks.find(child_name))))
                actions.append({
                    "field": child_name,
                    "from": None,
                    "to": "copied_from_sequential_source",
                    "changed": True,
                    "note": "Monkey Test had no explicit passive block controls; copied Sequential controls before enforcing the methodology contract.",
                })
    enforce_order_types(blocks, actions)
    enforce_exit_types(blocks, actions)
    enforce_external_custom_data(blocks, actions)
    enforce_disabled_build_block_categories(blocks, actions)


def apply_monkey_passive_generation_to_root(root: ET.Element, source_root: ET.Element | None) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    apply_retest1_parts_to_improve_to_root(root, actions)
    apply_monkey_what_to_build_to_root(root, actions)
    apply_monkey_blocks_to_root(root, source_root, actions)
    return actions


def monkey_passive_generation_summary(root: ET.Element) -> dict[str, Any]:
    return retest1_passive_generation_summary(root)


def enforce_monkey_passive_generation_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = monkey_passive_generation_summary(root)
    parts = summary.get("partsToImprove") or {}
    for group_name in ("EntryRules", "OrderTypes", "ExitRules"):
        group = parts.get(group_name) or {}
        for side in ("LongImprovement", "ShortImprovement"):
            if (group.get(side) or {}).get("use") != "false":
                issues.append(f"Monkey Test {group_name}/{side} must be passive use=false")
    if summary.get("strategyType") != MONKEY_STRATEGY_TYPE_TARGET:
        issues.append("Monkey Test StrategyType must point passively to Sequential with known SQX attributes")
    build_mode = summary.get("buildMode") or {}
    build_text = build_mode.get("text") or {}
    for tag, value in MONKEY_PASSIVE_BUILDMODE_TEXT_TARGET.items():
        if build_text.get(tag) != value:
            issues.append(f"Monkey Test BuildMode {tag} is {build_text.get(tag)!r}, expected {value!r}")
    child_attrs = build_mode.get("childAttrs") or {}
    for tag, attrs in MONKEY_PASSIVE_BUILDMODE_ATTR_TARGET.items():
        current = child_attrs.get(tag) or {}
        for key, value in attrs.items():
            if current.get(key) != value:
                issues.append(f"Monkey Test BuildMode {tag}.{key} is {current.get(key)!r}, expected {value!r}")
    blocks = summary.get("blocks") or {}
    actual_order = {key: blocks.get("orderTypes", {}).get(key) for key in BUILD_ORDER_TYPE_TARGET}
    if actual_order != BUILD_ORDER_TYPE_TARGET:
        issues.append(f"Monkey Test order types are {actual_order!r}, expected {BUILD_ORDER_TYPE_TARGET!r}")
    exits = blocks.get("exitTypes") or {}
    if exits.get(BUILD_EXIT_TYPE_ACTIVE_KEY, {}).get("use") != "true":
        issues.append("Monkey Test must keep only ExitAfterBars active")
    if exits.get(BUILD_EXIT_TYPE_ACTIVE_KEY, {}).get("probability") != "100":
        issues.append("Monkey Test ExitAfterBars probability must be 100")
    active_other_exits = [
        key for key, data in exits.items()
        if key != BUILD_EXIT_TYPE_ACTIVE_KEY and (data or {}).get("use") == "true"
    ]
    if active_other_exits:
        issues.append(f"Monkey Test has non-passive active exit types: {active_other_exits}")
    if any(any(token in key for token in BUILD_EXIT_TYPE_BANNED_TOKENS) for key in exits):
        issues.append("Monkey Test contains day-based exit types")
    if int(blocks.get("activeSignalCount") or 0) != 0:
        issues.append("Monkey Test signals must remain disabled in passive retest")
    if int(blocks.get("activeStopLimitCount") or 0) != 0:
        issues.append("Monkey Test stop/limit entry blocks must remain disabled in passive retest")
    if int(blocks.get("activeIndicatorCount") or 0) <= 0:
        issues.append("Monkey Test must preserve methodology/BlockSettings indicator blocks")
    custom = blocks.get("customData") or {}
    if (custom.get("attrs") or {}).get("showAll") != "false" or custom.get("children") != 0:
        issues.append("Monkey Test external CustomData must stay disabled and empty")
    for issue in enforce_monkey_data_databanks_resources_options_guard(root):
        issues.append(f"Data/Resources guard: {issue}")
    for issue in enforce_monkey_crosschecks_guard(root):
        issues.append(f"CrossChecks guard: {issue}")
    guarded_sections = [
        find_section(root, "PartsToImprove"),
        find_section(root, "WhatToBuild"),
        find_section(root, "Blocks"),
    ]
    guarded_text = "".join(serialize_xml(section if section is not None else root) for section in guarded_sections)
    for token in ("ExitAfterDays", "ExitAfterTradingDays", "USDJPY_darwinex", "USDJPY_dukascopy", "Strategies to improve"):
        if token in guarded_text:
            issues.append(f"Forbidden token leaked into Monkey Test passive generation tabs: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into Monkey Test passive generation tabs")
    return issues


def update_monkey_passive_generation_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, MONKEY_TASK_TITLE)
    source_task_xml_name, source_root = load_task_root(cfx, MONKEY_PASSIVE_SOURCE_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    payload["sourceTaskXml"] = source_task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "monkey_test_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload
    if not source_task_xml_name or source_root is None:
        payload["error"] = "monkey_source_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = monkey_passive_generation_summary(root)
    payload["actions"] = apply_monkey_passive_generation_to_root(root, source_root)
    payload["after"] = monkey_passive_generation_summary(root)
    payload["issues"] = enforce_monkey_passive_generation_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "strategyType": MONKEY_STRATEGY_TYPE_TARGET,
        "buildModeText": MONKEY_PASSIVE_BUILDMODE_TEXT_TARGET,
        "buildModeAttributes": MONKEY_PASSIVE_BUILDMODE_ATTR_TARGET,
        "sourceTask": MONKEY_PASSIVE_SOURCE_TASK_TITLE,
        "orderTypes": BUILD_ORDER_TYPE_TARGET,
        "exitType": BUILD_EXIT_TYPE_ACTIVE_KEY,
        "disabledCategories": BUILD_BLOCK_CATEGORY_DISABLE_TARGET,
    }
    payload["targetRationale"] = {
        "passiveRetest": "Monkey Test consumes Sequential survivors and must not improve, generate or alter strategy logic.",
        "noUnknownEnum": "BuildMode.generationType is left as an SQX-known placeholder because no local CFX uses a safe none/passive enum.",
        "blocksSource": "Existing Monkey Test BuildingBlocks are preserved to avoid changing strategy logic; Sequential is only a fallback if controls are missing.",
        "methodology": "Signals and Stop/Limit blocks stay off; indicators remain governed by methodology/BlockSettings; only EnterAtMarket plus ExitAfterBars is allowed.",
        "naturalResults": "No Results value is forced; passed/failed must remain the natural SQX outcome after RealMonkeyTest filters.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_monkey_passive_generation_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase9_monkey_test_passive_generation_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_monkey_passive_generation_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase9",
        "operation": "monkey_test_passive_generation_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase9_monkey_test_passive_generation_diff_review" if not apply else MONKEY_PASSIVE_GENERATION_NEXT,
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase9_monkey_test_passive_generation_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def apply_monkey_rankings_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    apply_mc_rankings_to_root(
        root,
        actions,
        conditions_note="Monkey Test pass/fail is owned by MonteCarloRetest/RealMonkeyTest acceptance conditions",
    )


def apply_monkey_custom_data_static_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    apply_monkey_setup_to_root(root, "CustomData", MONKEY_CUSTOM_DATA_ENGINE, actions)


def apply_monkey_static_tabs_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    apply_monkey_rankings_to_root(root, actions)
    apply_retest1_risk_money_management_to_root(root, actions)
    apply_mc_atms_to_root(root, actions)
    actions.append({"field": "Notes", "changed": False, "sha256": section_sha256(root, "Notes"), "note": "audited and preserved"})
    apply_mc_selected_strategies_to_root(root, actions)
    apply_monkey_custom_data_static_to_root(root, actions)
    return actions


def monkey_static_tabs_summary(root: ET.Element) -> dict[str, Any]:
    summary = mc_static_tabs_summary(root)
    custom = find_section(root, "CustomData")
    setup = custom.find(".//Setup") if custom is not None else None
    size_based = setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']") if setup is not None else None
    main_values = setup.find("MainTestValues") if setup is not None else None
    if "customData" in summary:
        summary["customData"]["commission"] = (size_based.text or "") if size_based is not None else ""
        summary["customData"]["mainTestValues"] = dict(main_values.attrib) if main_values is not None else {}
    return summary


def enforce_monkey_static_tabs_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = monkey_static_tabs_summary(root)
    ranking = summary.get("rankings") or {}
    if ranking.get("type") != "never":
        issues.append(f"Monkey Test Rankings type is {ranking.get('type')!r}, expected 'never'")
    for key in ("MaxStrategies", "ConditionsType", "DeleteFailedStrategies", "ForceRunCrossChecks"):
        if ranking.get(key) != MONKEY_RANKING_TARGET[key]:
            issues.append(f"Monkey Test Rankings {key} is {ranking.get(key)!r}, expected {MONKEY_RANKING_TARGET[key]!r}")
    if (ranking.get("FitPortfolio") or {}).get("active") != "false":
        issues.append("Monkey Test FitPortfolio must remain disabled; portfolio selection belongs to later portfolio phases")
    if (ranking.get("CustomAnalysis") or {}).get("filter") != "false":
        issues.append("Monkey Test CustomAnalysis filter must remain disabled")
    if ranking.get("conditions"):
        issues.append("Monkey Test Rankings must not add extra conditions; RealMonkeyTest acceptance owns pass/fail")

    rmm = summary.get("riskMoneyManagement") or {}
    methods = rmm.get("methods") or {}
    for method_type, wanted in RETEST1_RISK_MONEY_MANAGEMENT_METHOD_TARGET.items():
        if methods.get(method_type) != wanted:
            issues.append(f"Monkey Test RiskMoneyManagement {method_type} is {methods.get(method_type)!r}, expected {wanted!r}")

    atms = summary.get("atms") or {}
    for key, wanted in RETEST1_ATMS_TARGET.items():
        if (atms.get("attrs") or {}).get(key) != wanted:
            issues.append(f"Monkey Test ATMs {key} is {(atms.get('attrs') or {}).get(key)!r}, expected {wanted!r}")

    selected = summary.get("selectedStrategies") or {}
    if selected.get("children") != 0 or selected.get("text"):
        issues.append("Monkey Test SelectedStrategies must remain empty in the base template")

    custom = summary.get("customData") or {}
    if not custom.get("exists"):
        issues.append("Monkey Test CustomData section missing")
    else:
        period = generator_period(MONKEY_PERIOD_KEY)
        setup = custom.get("setup") or {}
        chart = custom.get("chart") or {}
        if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
            issues.append(f"Monkey Test CustomData dates are {(setup.get('dateFrom'), setup.get('dateTo'))!r}, expected {period!r}")
        if setup.get("testPrecision") != MONKEY_DATA_TEST_PRECISION:
            issues.append(f"Monkey Test CustomData testPrecision is {setup.get('testPrecision')!r}, expected {MONKEY_DATA_TEST_PRECISION!r}")
        if setup.get("session") != MONKEY_DATA_SESSION:
            issues.append(f"Monkey Test CustomData session is {setup.get('session')!r}, expected {MONKEY_DATA_SESSION!r}")
        target_chart = main_chart_seed(root)
        if target_chart and {key: chart.get(key, "") for key in target_chart} != target_chart:
            issues.append(f"Monkey Test CustomData chart seed is {chart!r}, expected {target_chart!r}")
        if custom.get("commission") != MC_CUSTOM_DATA_COMMISSION_TARGET:
            issues.append(f"Monkey Test CustomData commission is {custom.get('commission')!r}, expected {MC_CUSTOM_DATA_COMMISSION_TARGET!r}")
        if custom.get("mainTestValues") != MONKEY_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET:
            issues.append("Monkey Test CustomData MainTestValues drifted from dual-carrier target")

    guarded_text = (
        section_text(root, "Rankings")
        + section_text(root, "ATMs")
        + section_text(root, "RiskMoneyManagement")
        + section_text(root, "SelectedStrategies")
        + section_text(root, "CustomData")
    )
    for token in MC_BANNED_DONOR_TOKENS:
        if token in guarded_text:
            issues.append(f"Forbidden donor token leaked into Monkey Test static tabs: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into Monkey Test static tabs")

    for issue in enforce_monkey_passive_generation_guard(root):
        issues.append(f"Passive generation guard: {issue}")
    return issues


def update_monkey_static_tabs_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, MONKEY_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "monkey_test_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = monkey_static_tabs_summary(root)
    payload["actions"] = apply_monkey_static_tabs_to_root(root)
    payload["after"] = monkey_static_tabs_summary(root)
    payload["issues"] = enforce_monkey_static_tabs_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "rankings": MONKEY_RANKING_TARGET,
        "rankingConditions": [],
        "riskMoneyManagementMethods": RETEST1_RISK_MONEY_MANAGEMENT_METHOD_TARGET,
        "atms": RETEST1_ATMS_TARGET,
        "staticTabs": MONKEY_STATIC_TABS,
        "customDataMainTestValues": MONKEY_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET,
        "customDataCommission": MC_CUSTOM_DATA_COMMISSION_TARGET,
        "customDataCarrier": "dual_synced",
    }
    payload["targetRationale"] = {
        "decision": "Monkey static tabs close inert surfaces before phase closeout while keeping RealMonkeyTest as the only active robustness decision.",
        "ranking": "Monkey pass/fail is owned by MonteCarloRetest/RealMonkeyTest acceptance filters; Ranking must preserve failed rows and not run portfolio selection.",
        "riskMoneyManagement": "FixedSize keeps Capa1 retests comparable and avoids sizing noise.",
        "customData": "Monkey keeps SQX142-compatible Data+CustomData dual carrier synchronized; this block hardens only the CustomData tab without deleting Data.",
        "staticTabs": "ATMs, Notes and SelectedStrategies stay inert while executable behavior is guarded by previous Monkey blocks.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_monkey_static_tabs_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase9_monkey_test_static_tabs_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_monkey_static_tabs_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase9",
        "operation": "monkey_test_static_tabs_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase9_monkey_test_static_tabs_diff_review" if not apply else MONKEY_STATIC_TABS_NEXT,
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase9_monkey_test_static_tabs_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


MONKEY_CLOSEOUT_OPERATIONS = (
    (
        "dataDatabanksResourcesOptions",
        "monkey-data-databanks-resources-options-target",
        promote_monkey_data_databanks_resources_options_target,
    ),
    ("crosschecks", "monkey-crosschecks-target", promote_monkey_crosschecks_target),
    ("passiveGeneration", "monkey-passive-generation-target", promote_monkey_passive_generation_target),
    ("staticTabs", "monkey-static-tabs-target", promote_monkey_static_tabs_target),
)


def monkey_closeout_report(root142: Path, project_root: Path, target: str, write: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    operations: dict[str, Any] = {}
    issues: list[str] = []
    for key, command, runner in MONKEY_CLOSEOUT_OPERATIONS:
        result = runner(root142, project_root, target=target, apply=False)
        operation_issues = mc_closeout_operation_issues(command, result)
        operations[key] = {
            "command": command,
            "summary": mc_closeout_operation_summary(result),
            "issues": operation_issues,
        }
        issues.extend(operation_issues)

    previous_gate = sequential_closeout_report(root142, project_root, target=target, write=False)
    previous_issues = list(previous_gate.get("issues") or [])
    if previous_gate.get("ok") is not True:
        previous_issues.append("sequential-closeout-report: previous gate ok=false")
    issues.extend(previous_issues)

    process_probe = process_snapshot()
    process_warnings = []
    if process_probe.get("processes"):
        process_warnings.append("SQX processes are alive; closeout is XML/dry-run only, no SQX runtime mutation was attempted")

    payload: dict[str, Any] = {
        "ok": not issues,
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase9_monkey_test_closeout",
        "target": target,
        "write": write,
        "previousGate": {
            "phase": previous_gate.get("phase"),
            "ok": previous_gate.get("ok"),
            "issues": previous_issues,
            "nextPhase": previous_gate.get("nextPhase"),
        },
        "operations": operations,
        "issues": issues,
        "warnings": process_warnings,
        "processProbe": process_probe,
        "summary": {
            "decision": "Close Monkey Test after all Phase 9 guards are green and idempotent on local base and repo template.",
            "taskTitle": MONKEY_TASK_TITLE,
            "taskXml": MONKEY_TASK_XML,
            "chain": "Input=Sequential / Output=Monkey Test",
            "period": MONKEY_PERIOD_KEY,
            "testPrecision": MONKEY_DATA_TEST_PRECISION,
            "activeCrossCheck": MONKEY_ACTIVE_CROSSCHECK,
            "activeMethod": MONKEY_ACTIVE_METHOD,
            "numberOfSimulations": MONKEY_NUMBER_OF_SIMULATIONS,
            "mcUseFullSample": MONKEY_USE_FULL_SAMPLE,
            "realMonkeyMaxChange": MONKEY_METHOD_MAX_CHANGE,
            "acceptanceFilters": [
                "NetProfit >= 50% of main result",
                "Max DD <= 200% of main result",
            ],
            "passiveContract": {
                "improveDatabank": MONKEY_STRATEGY_TYPE_TARGET["improveDatabank"],
                "signals": 0,
                "stopLimitEntryBlocks": 0,
                "entry": "EnterAtMarket",
                "exit": "ExitAfterBars probability 100",
                "dayBasedExits": "forbidden",
            },
            "staticContract": {
                "ranking": "inert",
                "deleteFailedStrategies": "false",
                "forceRunCrossChecks": "false",
                "fitPortfolio": "false",
                "customAnalysisFilter": "false",
                "riskMoneyManagement": "FixedSize",
                "atms": "disabled",
                "selectedStrategies": "empty_or_absent",
                "customDataCarrier": "dual_synced",
            },
            "nextPhase": MONKEY_CLOSEOUT_NEXT,
            "closeoutCriterion": "all Monkey guards plus Sequential previous gate must be green and idempotent before opening Synthetic/Syntetic",
            "naturalResults": "Preserve natural passed/failed outcomes; never force Results=passed.",
            "noLiveRun": "This closeout only reads XML/local state and writes a phase report when requested.",
        },
        "nextPhase": MONKEY_CLOSEOUT_NEXT,
    }
    if write:
        target_path = ledger_root(project_root) / "phase_reports" / f"phase9_monkey_test_closeout_{stamp()}.json"
        write_json(target_path, payload)
        state_path = ledger_root(project_root) / "session_state.json"
        state = read_json(state_path, {})
        state.update({"updatedAt": now_iso(), "currentPhase": "phase9_monkey_test_closeout", "nextPhase": MONKEY_CLOSEOUT_NEXT})
        write_json(state_path, state)
        payload["written"] = str(target_path)
    return payload


def synthetic_open_summary(root: ET.Element | None) -> dict[str, Any]:
    if root is None:
        return {"exists": False}
    summary = monkey_open_summary(root)
    crosschecks = summary.get("crossChecks") or {}
    active_check = next(
        (check for check in crosschecks.get("checks", []) if check.get("id") == SYNTHETIC_ACTIVE_CROSSCHECK),
        {},
    )
    active_methods = [
        method
        for method in active_check.get("methods", [])
        if method.get("use") == "true"
    ]
    summary["activeSyntheticMethod"] = active_methods[0] if active_methods else {}
    summary["alias"] = {
        "canonical": "Synthetic",
        "actual": SYNTHETIC_TASK_TITLE,
        "historical": ["Synthetic", "Syntetic"],
    }
    return summary


def synthetic_open_issues(summary: dict[str, Any]) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    if not summary.get("exists"):
        return ["Synthetic/Syntetic task missing"], warnings

    databanks = summary.get("databanks") or {}
    for name, wanted in SYNTHETIC_EXPECTED_DATABANKS.items():
        if databanks.get(name) != wanted:
            issues.append(f"Synthetic/Syntetic Databank {name} is {databanks.get(name)!r}, expected {wanted!r}")

    crosschecks = summary.get("crossChecks") or {}
    if not crosschecks.get("exists"):
        issues.append("Synthetic/Syntetic CrossChecks section missing")
    else:
        attrs = crosschecks.get("attributes") or {}
        if attrs.get("use") != "true" or attrs.get("evaluateAll") != "true":
            issues.append("Synthetic/Syntetic CrossChecks must stay active/evaluateAll for SyntheticBootstrapV3")
        active = crosschecks.get("active") or []
        if active != [SYNTHETIC_ACTIVE_CROSSCHECK]:
            issues.append(f"Synthetic/Syntetic active crosschecks are {active!r}, expected only {SYNTHETIC_ACTIVE_CROSSCHECK!r}")
        checks = {item.get("id"): item for item in crosschecks.get("checks") or []}
        monte_carlo = checks.get(SYNTHETIC_ACTIVE_CROSSCHECK) or {}
        if monte_carlo.get("numberOfSimulations") != SYNTHETIC_NUMBER_OF_SIMULATIONS:
            issues.append(f"Synthetic/Syntetic NumberOfSimulations is {monte_carlo.get('numberOfSimulations')!r}, expected {SYNTHETIC_NUMBER_OF_SIMULATIONS!r}")
        if monte_carlo.get("mcUseFullSample") != SYNTHETIC_USE_FULL_SAMPLE:
            issues.append(f"Synthetic/Syntetic MCUseFullSample is {monte_carlo.get('mcUseFullSample')!r}, expected {SYNTHETIC_USE_FULL_SAMPLE!r}")
        active_methods = monte_carlo.get("activeMethodTypes") or []
        if active_methods != [SYNTHETIC_ACTIVE_METHOD]:
            issues.append(f"Synthetic/Syntetic active methods are {active_methods!r}, expected only {SYNTHETIC_ACTIVE_METHOD!r}")
        method = summary.get("activeSyntheticMethod") or {}
        params = method.get("params") or {}
        for key, wanted in SYNTHETIC_METHOD_PARAMS_TARGET.items():
            if params.get(key) != wanted:
                issues.append(f"Synthetic/Syntetic {SYNTHETIC_ACTIVE_METHOD} {key} is {params.get(key)!r}, expected {wanted!r}")
        if monte_carlo.get("activeAcceptanceConditionCount") == 0:
            warnings.append("Synthetic/Syntetic acceptance filter conditions are currently inactive; next CrossChecks block must decide final filters.")
        inactive_with_active_methods = [
            {
                "check": check.get("id"),
                "methods": check.get("activeMethodTypes") or [],
            }
            for check in crosschecks.get("checks") or []
            if check.get("id") != SYNTHETIC_ACTIVE_CROSSCHECK and check.get("use") == "false" and check.get("activeMethodTypes")
        ]
        if inactive_with_active_methods:
            warnings.append(f"Synthetic/Syntetic inactive crosschecks still carry active methods {inactive_with_active_methods!r}; next CrossChecks block should make them inert if we keep task separation.")

    strategy_type = summary.get("strategyType") or {}
    improve_databank = strategy_type.get("improveDatabank", "")
    if improve_databank and improve_databank != "Monkey Test":
        warnings.append(f"Synthetic/Syntetic StrategyType.improveDatabank is {improve_databank!r}; passive-generation block should normalize it to Monkey Test if needed")

    if (summary.get("data") or {}).get("exists") and (summary.get("customData") or {}).get("exists"):
        warnings.append("Synthetic/Syntetic currently carries both Data and CustomData; next block must choose the canonical data carrier before mutation")

    return issues, warnings


def synthetic_open_target_report(cfx: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256": file_sha256(cfx) if cfx.is_file() else "",
        "taskTitle": SYNTHETIC_DISPLAY_TITLE,
        "taskXml": "",
        "summary": {},
        "issues": [],
        "warnings": [],
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["issues"].append("missing_or_not_zip")
        payload["ok"] = False
        return payload
    task_xml_name, root = load_task_root(cfx, SYNTHETIC_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["issues"].append("synthetic_task_not_found")
        payload["ok"] = False
        return payload
    if task_xml_name != SYNTHETIC_TASK_XML:
        payload["warnings"].append(f"Synthetic/Syntetic task XML is {task_xml_name!r}, expected {SYNTHETIC_TASK_XML!r}")
    payload["summary"] = synthetic_open_summary(root)
    issues, warnings = synthetic_open_issues(payload["summary"])
    payload["issues"] = issues
    payload["warnings"].extend(warnings)
    payload["ok"] = not issues
    return payload


def synthetic_open_report(root142: Path, project_root: Path, target: str, write: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    target_reports = {
        name: synthetic_open_target_report(path)
        for name, path in targets.items()
    }
    previous_gate = monkey_closeout_report(root142, project_root, target=target, write=False)
    previous_issues = list(previous_gate.get("issues") or [])
    if previous_gate.get("ok") is not True:
        previous_issues.append("monkey-closeout-report: previous gate ok=false")
    process_probe = process_snapshot()
    process_warnings = []
    if process_probe.get("processes"):
        process_warnings.append("SQX processes are alive; keep phase 10 open read-only until SQX is closed")
    payload: dict[str, Any] = {
        "ok": all(item.get("ok") for item in target_reports.values()) and not previous_issues,
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase10_synthetic_open",
        "target": target,
        "write": write,
        "previousGate": {
            "phase": previous_gate.get("phase"),
            "ok": previous_gate.get("ok"),
            "issues": previous_issues,
            "nextPhase": previous_gate.get("nextPhase"),
        },
        "targets": target_reports,
        "warnings": process_warnings + [
            warning
            for item in target_reports.values()
            for warning in item.get("warnings", [])
        ],
        "processProbe": process_probe,
        "summary": {
            "decision": "Open Synthetic/Syntetic as Phase 10 after Monkey Test closeout; inspect structure before applying target values.",
            "taskTitle": SYNTHETIC_DISPLAY_TITLE,
            "actualTaskTitle": SYNTHETIC_TASK_TITLE,
            "taskXml": SYNTHETIC_TASK_XML,
            "chain": "Input=Monkey Test / Output=Syntetic",
            "activeCrossCheck": SYNTHETIC_ACTIVE_CROSSCHECK,
            "activeMethod": SYNTHETIC_ACTIVE_METHOD,
            "numberOfSimulations": SYNTHETIC_NUMBER_OF_SIMULATIONS,
            "mcUseFullSample": SYNTHETIC_USE_FULL_SAMPLE,
            "methodParams": SYNTHETIC_METHOD_PARAMS_TARGET,
            "aliasPolicy": "Synthetic and Syntetic are treated as the same historical task alias; tracked databank output remains Syntetic until a later explicit migration.",
            "naturalResults": "Preserve natural passed/failed outcomes; never force Results=passed.",
            "noLiveRun": "This gate only reads XML/local state and writes a phase report when requested.",
            "decisionPending": [
                "Data/Databanks/Resources/Options must keep generator-owned asset/timeframe/spread resources and avoid copying Monkey-specific columns.",
                "CrossChecks must keep SyntheticBootstrap separated from Monkey RealMonkeyTest and decide acceptance filters explicitly.",
                "Passive-generation/static tabs must keep Synthetic/Syntetic from generating or altering strategy logic.",
            ],
        },
        "nextPhase": SYNTHETIC_NEXT_PHASE,
    }
    if write:
        target_path = ledger_root(project_root) / "phase_reports" / f"phase10_synthetic_open_{stamp()}.json"
        write_json(target_path, payload)
        state_path = ledger_root(project_root) / "session_state.json"
        state = read_json(state_path, {})
        state.update({"updatedAt": now_iso(), "currentPhase": "phase10_synthetic_open", "nextPhase": SYNTHETIC_NEXT_PHASE})
        write_json(state_path, state)
        payload["written"] = str(target_path)
    return payload


def synthetic_data_databanks_resources_options_summary(root: ET.Element | None) -> dict[str, Any]:
    summary = synthetic_open_summary(root)
    if not summary.get("exists"):
        return summary
    setup_pairs = []
    data_setup = root.find("./Data/Setups/Setup") if root is not None else None
    custom_setup = root.find("./CustomData/Setups/Setup") if root is not None else None
    if data_setup is not None and custom_setup is not None:
        setup_pairs.append({
            "field": "Data_vs_CustomData",
            "data": {
                "dateFrom": data_setup.get("dateFrom", ""),
                "dateTo": data_setup.get("dateTo", ""),
                "testPrecision": data_setup.get("testPrecision", ""),
                "session": data_setup.get("session", ""),
                "slippage": data_setup.get("slippage", ""),
                "minDist": data_setup.get("minDist", ""),
                "chart": dict(data_setup.find("Chart").attrib) if data_setup.find("Chart") is not None else {},
            },
            "customData": {
                "dateFrom": custom_setup.get("dateFrom", ""),
                "dateTo": custom_setup.get("dateTo", ""),
                "testPrecision": custom_setup.get("testPrecision", ""),
                "session": custom_setup.get("session", ""),
                "slippage": custom_setup.get("slippage", ""),
                "minDist": custom_setup.get("minDist", ""),
                "chart": dict(custom_setup.find("Chart").attrib) if custom_setup.find("Chart") is not None else {},
            },
        })
    summary["carrierDecision"] = {
        "mode": "dual_synced",
        "reason": "Synthetic/Syntetic in SQX142 stores both Data and CustomData; keep both synced for compatibility and leave asset/timeframe/spread to Project Generator in generated customs.",
        "pairs": setup_pairs,
    }
    return summary


def apply_synthetic_setup_to_root(root: ET.Element, section_name: str, engine: str, actions: list[dict[str, Any]]) -> ET.Element:
    section = find_section(root, section_name)
    if section is None:
        section = ET.SubElement(root, section_name)
        actions.append({"field": section_name, "from": None, "to": "created", "changed": True})
    setup = ensure_setup_under(section, actions, section_name)
    period = generator_period(SYNTHETIC_PERIOD_KEY)
    set_attrs_on_node(
        setup,
        {
            "dateFrom": period[0],
            "dateTo": period[1],
            "testPrecision": SYNTHETIC_DATA_TEST_PRECISION,
            "session": SYNTHETIC_DATA_SESSION,
            "slippage": "0",
            "minDist": "0",
            "engine": engine,
        },
        actions,
        f"{section_name}/Setup:attrs",
    )
    chart = setup.find("Chart")
    if chart is None:
        chart = ET.SubElement(setup, "Chart")
        actions.append({"field": f"{section_name}/Setup/Chart", "from": None, "to": dict(chart.attrib), "changed": True})
    set_attrs_on_node(chart, SYNTHETIC_DEFAULT_CHART_TARGET, actions, f"{section_name}/Setup/Chart:attrs")
    ensure_commission_method(setup, actions, f"{section_name}/Setup")
    if section_name == "CustomData":
        main_values = setup.find("MainTestValues")
        if main_values is None:
            main_values = ET.SubElement(setup, "MainTestValues")
            actions.append({"field": "CustomData/MainTestValues", "from": None, "to": dict(main_values.attrib), "changed": True})
        set_attrs_on_node(
            main_values,
            SYNTHETIC_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET,
            actions,
            "CustomData/MainTestValues:attrs",
        )
    return setup


def apply_synthetic_data_databanks_resources_options_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    data_setup = apply_synthetic_setup_to_root(root, "Data", SYNTHETIC_DATA_ENGINE, actions)
    custom_setup = apply_synthetic_setup_to_root(root, "CustomData", SYNTHETIC_CUSTOM_DATA_ENGINE, actions)

    data = find_section(root, "Data")
    out_of_sample = data.find("OutOfSample") if data is not None else None
    removed_oos = []
    if out_of_sample is not None:
        for range_node in list(out_of_sample.findall("Range")):
            removed_oos.append(dict(range_node.attrib))
            out_of_sample.remove(range_node)
    actions.append({
        "field": "Data/OutOfSample/Range",
        "from": removed_oos,
        "to": [],
        "changed": bool(removed_oos),
        "note": "Synthetic/Syntetic consumes Monkey survivors and does not add a nested OOS split.",
    })

    databanks = find_section(root, "Databanks")
    if databanks is None:
        databanks = ET.SubElement(root, "Databanks", {"retestSelected": "false"})
        actions.append({"field": "Databanks", "from": None, "to": dict(databanks.attrib), "changed": True})
    existing_by_name = {
        node.get("name", ""): node
        for node in databanks.findall("Databank")
        if node.get("name")
    }
    for name, wanted in SYNTHETIC_EXPECTED_DATABANKS.items():
        node = existing_by_name.get(name)
        before = dict(node.attrib) if node is not None else None
        if node is None:
            node = ET.SubElement(databanks, "Databank", {"name": name})
        node.set("name", name)
        node.set("value", wanted)
        node.set("label", f"{name} databank")
        actions.append({
            "field": f"Databanks/{name}",
            "from": before,
            "to": dict(node.attrib),
            "changed": before != dict(node.attrib),
        })

    apply_mc2_resources_from_custom_data(root, custom_setup, actions)
    for key, value in SYNTHETIC_OPTIONS_PARAMS_TARGET.items():
        set_param_text(root, key, value, actions, "Options")
    actions.append({
        "field": "Synthetic/DataCarrier",
        "from": {
            "data": value_for_node(data_setup),
            "customData": value_for_node(custom_setup),
        },
        "to": "dual_synced",
        "changed": False,
        "note": "Kept both Data and CustomData for SQX142 compatibility; enforced matching period, precision, session and chart seed.",
    })
    return actions


def enforce_synthetic_data_databanks_resources_options_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    period = generator_period(SYNTHETIC_PERIOD_KEY)
    data_setup = root.find("./Data/Setups/Setup")
    custom_setup = root.find("./CustomData/Setups/Setup")
    if data_setup is None:
        issues.append("Synthetic/Syntetic Data/Setup missing")
    if custom_setup is None:
        issues.append("Synthetic/Syntetic CustomData/Setup missing")
    for label, setup in (("Data", data_setup), ("CustomData", custom_setup)):
        if setup is None:
            continue
        if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
            issues.append(f"Synthetic/Syntetic {label} dates are not {SYNTHETIC_PERIOD_KEY}")
        if setup.get("testPrecision") != SYNTHETIC_DATA_TEST_PRECISION:
            issues.append(f"Synthetic/Syntetic {label} testPrecision must stay {SYNTHETIC_DATA_TEST_PRECISION}")
        if setup.get("session") != SYNTHETIC_DATA_SESSION:
            issues.append(f"Synthetic/Syntetic {label} session must stay {SYNTHETIC_DATA_SESSION}")
        chart = setup.find("Chart")
        if chart is None:
            issues.append(f"Synthetic/Syntetic {label} chart missing")
        else:
            for key, wanted in SYNTHETIC_DEFAULT_CHART_TARGET.items():
                if chart.get(key) != wanted:
                    issues.append(f"Synthetic/Syntetic {label} chart {key} is {chart.get(key)!r}, expected {wanted!r}")
        commission = setup.find("./Commissions/Method[@type='SizeBased']/Params/Param[@key='Commission']")
        if (commission.text if commission is not None else "") != MC_CUSTOM_DATA_COMMISSION_TARGET:
            issues.append(f"Synthetic/Syntetic {label} commission is {(commission.text if commission is not None else '')!r}, expected {MC_CUSTOM_DATA_COMMISSION_TARGET!r}")
    if data_setup is not None and custom_setup is not None:
        data_chart = data_setup.find("Chart")
        custom_chart = custom_setup.find("Chart")
        for key in ("dateFrom", "dateTo", "testPrecision", "session", "slippage", "minDist"):
            if data_setup.get(key) != custom_setup.get(key):
                issues.append(f"Synthetic/Syntetic Data/CustomData setup mismatch for {key}")
        if data_chart is not None and custom_chart is not None:
            for key in ("symbol", "timeframe", "spread"):
                if data_chart.get(key) != custom_chart.get(key):
                    issues.append(f"Synthetic/Syntetic Data/CustomData chart mismatch for {key}")
    main_values = root.find("./CustomData/Setups/Setup/MainTestValues")
    if main_values is None or dict(main_values.attrib) != SYNTHETIC_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET:
        issues.append("Synthetic/Syntetic CustomData MainTestValues drifted from dual-synced target")

    databanks = {
        node.get("name", ""): node.get("value", "")
        for node in root.findall(".//Databanks/Databank")
        if node.get("name")
    }
    for name, wanted in SYNTHETIC_EXPECTED_DATABANKS.items():
        if databanks.get(name) != wanted:
            issues.append(f"Synthetic/Syntetic Databank {name} is {databanks.get(name)!r}, expected {wanted!r}")

    resources = find_section(root, "Resources")
    if resources is None:
        issues.append("Synthetic/Syntetic Resources missing")
    else:
        chart_symbols = {
            chart.get("symbol", "")
            for chart in root.findall("./CustomData/Setups/Setup/Chart")
            if chart.get("symbol")
        }
        resource_symbols = {
            symbol.get("name", "")
            for symbol in resources.findall("./Symbols/Symbol")
            if symbol.get("name")
        }
        if chart_symbols != resource_symbols:
            issues.append(f"Synthetic/Syntetic custom chart/resource mismatch: charts={sorted(chart_symbols)} resources={sorted(resource_symbols)}")
        broker_ids = {
            broker.get("id", "")
            for broker in resources.findall("./Brokers/Broker")
            if broker.get("id")
        }
        for symbol in resources.findall("./Symbols/Symbol"):
            if symbol.get("precision") != MC_RESOURCE_PRECISION:
                issues.append(f"Synthetic/Syntetic resource {symbol.get('name')} precision is not TICK")
            if symbol.get("timezone") != MC_RESOURCE_TIMEZONE:
                issues.append(f"Synthetic/Syntetic resource {symbol.get('name')} timezone is not EETUS")
            if symbol.get("broker") not in broker_ids:
                issues.append(f"Synthetic/Syntetic resource {symbol.get('name')} references missing broker {symbol.get('broker')}")
            info = symbol.find("InstrumentInfo")
            if info is None:
                issues.append(f"Synthetic/Syntetic resource {symbol.get('name')} has no nested InstrumentInfo")
            elif info.get("broker") not in broker_ids:
                issues.append(f"Synthetic/Syntetic nested InstrumentInfo for {symbol.get('name')} references missing broker {info.get('broker')}")
        if resources.findall("./Sessions/Session"):
            issues.append("Synthetic/Syntetic resources must not keep session entries")

    params = {
        param.get("key", ""): (param.text or "")
        for param in root.findall(".//BuildTradingOptions/Params/Param")
        if param.get("key") in SYNTHETIC_OPTIONS_PARAMS_TARGET
    }
    for key, wanted in SYNTHETIC_OPTIONS_PARAMS_TARGET.items():
        if params.get(key) != wanted:
            issues.append(f"Synthetic/Syntetic Options param {key} is {params.get(key)!r}, expected {wanted!r}")

    if root.findall("./Data/OutOfSample/Range"):
        issues.append("Synthetic/Syntetic Data must not contain nested OOS ranges")
    guarded_text = (
        section_text(root, "Data")
        + section_text(root, "CustomData")
        + section_text(root, "Databanks")
        + section_text(root, "Resources")
        + section_text(root, "Options")
    )
    for token in MC_BANNED_DONOR_TOKENS:
        if token in guarded_text:
            issues.append(f"Forbidden donor token leaked into Synthetic/Syntetic Data/Databanks/Resources/Options: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into Synthetic/Syntetic Data/Databanks/Resources/Options")
    return issues


def update_synthetic_data_databanks_resources_options_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload
    task_xml_name, root = load_task_root(cfx, SYNTHETIC_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "synthetic_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = synthetic_data_databanks_resources_options_summary(root)
    payload["actions"] = apply_synthetic_data_databanks_resources_options_to_root(root)
    payload["after"] = synthetic_data_databanks_resources_options_summary(root)
    payload["issues"] = enforce_synthetic_data_databanks_resources_options_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["xmlChanged"] = before_text != after_text
    payload["changed"] = payload["changedActionCount"] > 0
    payload["targetValues"] = {
        "taskTitle": SYNTHETIC_DISPLAY_TITLE,
        "actualTaskTitle": SYNTHETIC_TASK_TITLE,
        "taskXml": SYNTHETIC_TASK_XML,
        "periodKey": SYNTHETIC_PERIOD_KEY,
        "dateFrom": generator_period(SYNTHETIC_PERIOD_KEY)[0],
        "dateTo": generator_period(SYNTHETIC_PERIOD_KEY)[1],
        "dataCarrier": "dual_synced",
        "dataEngine": SYNTHETIC_DATA_ENGINE,
        "customDataEngine": SYNTHETIC_CUSTOM_DATA_ENGINE,
        "customDataMainTestValues": SYNTHETIC_CUSTOM_DATA_MAIN_TEST_VALUES_TARGET,
        "databanks": SYNTHETIC_EXPECTED_DATABANKS,
        "resourcePrecision": MC_RESOURCE_PRECISION,
        "resourceTimezone": MC_RESOURCE_TIMEZONE,
        "options": SYNTHETIC_OPTIONS_PARAMS_TARGET,
    }
    payload["targetRationale"] = {
        "methodology": "Synthetic/Syntetic consumes Monkey survivors and applies synthetic-sample robustness; it is not a new OOS split or optimizer in Capa1.",
        "carrier": "SQX142 Synthetic carries both Data and CustomData in the working base; keeping both synced is safer than deleting one without UI evidence.",
        "options": "Trading time ranges are disabled for this robustness gate in the base/template; Project Generator should not inject them for Synthetic/Syntetic.",
        "naturalResults": "The block preserves natural passed/failed rows and does not force Results=passed.",
        "separation": "Synthetic/Syntetic keeps its own databank and must not copy Monkey-specific columns or filters.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_synthetic_data_databanks_resources_options_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase10_synthetic_data_databanks_resources_options_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_synthetic_data_databanks_resources_options_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase10",
        "operation": "synthetic_data_databanks_resources_options_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase10_synthetic_data_databanks_resources_options_diff_review" if not apply else SYNTHETIC_DATA_DATABANKS_RESOURCES_OPTIONS_NEXT,
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase10_synthetic_data_databanks_resources_options_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def synthetic_crosschecks_summary(root: ET.Element | None) -> dict[str, Any]:
    return monkey_crosschecks_summary(root)


def set_synthetic_acceptance_conditions(check: ET.Element, actions: list[dict[str, Any]]) -> None:
    acceptance = ensure_direct_child(check, "AcceptanceSettings")
    conditions = acceptance.find("Conditions")
    if conditions is None:
        conditions = ET.SubElement(acceptance, "Conditions")
        before: list[dict[str, Any]] = []
    else:
        before = [mc_condition_summary(condition) for condition in conditions.findall("Condition")]
        for child in list(conditions):
            conditions.remove(child)
    conditions.attrib.clear()
    conditions.set("CrossCheck", SYNTHETIC_ACTIVE_CROSSCHECK)
    conditions.text = "\n          "
    for index, target in enumerate(SYNTHETIC_ACCEPTANCE_CONDITIONS_TARGET):
        condition = make_mc_ratio_condition(target)
        condition.tail = "\n        " if index == len(SYNTHETIC_ACCEPTANCE_CONDITIONS_TARGET) - 1 else "\n          "
        conditions.append(condition)
    after = [mc_condition_summary(condition) for condition in conditions.findall("Condition")]
    actions.append({
        "field": "CrossChecks/MonteCarloRetest/AcceptanceSettings/Conditions",
        "from": before,
        "to": after,
        "changed": before != after,
        "note": "Synthetic/Syntetic keeps its own SyntheticBootstrapV3 acceptance row; it is not copied from Monkey filters.",
    })


def normalize_synthetic_crosscheck_setups(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    period = generator_period(SYNTHETIC_PERIOD_KEY)
    before: list[dict[str, Any]] = []
    after: list[dict[str, Any]] = []
    for setup in root.findall(".//CrossChecks/*/Settings/Setups/Setup"):
        before.append({
            "attrs": dict(setup.attrib),
            "charts": [dict(chart.attrib) for chart in setup.findall("Chart")],
        })
        for key, wanted in {
            "dateFrom": period[0],
            "dateTo": period[1],
            "testPrecision": SYNTHETIC_DATA_TEST_PRECISION,
            "session": SYNTHETIC_DATA_SESSION,
            "slippage": "0",
            "minDist": "0",
        }.items():
            setup.set(key, wanted)
        charts = setup.findall("Chart")
        if not charts:
            charts = [ET.SubElement(setup, "Chart")]
        for chart in charts:
            for key, value in SYNTHETIC_DEFAULT_CHART_TARGET.items():
                chart.set(key, value)
        after.append({
            "attrs": dict(setup.attrib),
            "charts": [dict(chart.attrib) for chart in setup.findall("Chart")],
        })
    actions.append({
        "field": "CrossChecks/*/Settings/Setups/Setup",
        "from": before,
        "to": after,
        "changed": before != after,
        "note": "Nested disabled crosscheck setups are normalized to the same safe seed; SyntheticBootstrapV3 remains the only active Synthetic method.",
    })


def apply_synthetic_crosschecks_to_root(root: ET.Element) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    parent = find_section(root, "CrossChecks")
    if parent is None:
        parent = ET.SubElement(root, "CrossChecks")
        actions.append({"field": "CrossChecks", "from": None, "to": dict(parent.attrib), "changed": True})
    set_attrs_on_node(parent, SYNTHETIC_CROSSCHECK_PARENT_TARGET, actions, "CrossChecks:attrs")

    active = parent.find(SYNTHETIC_ACTIVE_CROSSCHECK)
    if active is None:
        active = ET.SubElement(parent, SYNTHETIC_ACTIVE_CROSSCHECK, {"use": "true"})
        actions.append({"field": f"CrossChecks/{SYNTHETIC_ACTIVE_CROSSCHECK}", "from": None, "to": dict(active.attrib), "changed": True})

    for check in list(parent):
        if not isinstance(check.tag, str) or check.get("use") is None:
            continue
        before_use = check.get("use", "")
        wanted_use = "true" if check.tag == SYNTHETIC_ACTIVE_CROSSCHECK else "false"
        check.set("use", wanted_use)
        actions.append({
            "field": f"CrossChecks/{check.tag}:use",
            "from": before_use,
            "to": wanted_use,
            "changed": before_use != wanted_use,
        })
        for method in check.findall("./Settings/Methods/Method"):
            method_type = method.get("type", "")
            wanted_method = (
                "true"
                if check.tag == SYNTHETIC_ACTIVE_CROSSCHECK and method_type == SYNTHETIC_ACTIVE_METHOD
                else "false"
            )
            before_method = method.get("use", "")
            method.set("use", wanted_method)
            actions.append({
                "field": f"CrossChecks/{check.tag}/Method:{method_type}:use",
                "from": before_method,
                "to": wanted_method,
                "changed": before_method != wanted_method,
            })

    settings = ensure_direct_child(active, "Settings")
    for tag, wanted in (
        ("NumberOfSimulations", SYNTHETIC_NUMBER_OF_SIMULATIONS),
        ("MCUseFullSample", SYNTHETIC_USE_FULL_SAMPLE),
        ("MCBacktestPrecision", SYNTHETIC_MC_BACKTEST_PRECISION),
    ):
        set_or_create_text_child(settings, tag, wanted, actions, f"CrossChecks/{SYNTHETIC_ACTIVE_CROSSCHECK}/Settings/{tag}")

    methods = ensure_direct_child(settings, "Methods")
    method = None
    for item in methods.findall("Method"):
        if item.get("type") == SYNTHETIC_ACTIVE_METHOD:
            method = item
            break
    if method is None:
        method = ET.SubElement(methods, "Method", {"type": SYNTHETIC_ACTIVE_METHOD, "use": "true"})
        actions.append({"field": f"CrossChecks/{SYNTHETIC_ACTIVE_CROSSCHECK}/Method:{SYNTHETIC_ACTIVE_METHOD}", "from": None, "to": dict(method.attrib), "changed": True})
    before_use = method.get("use", "")
    method.set("use", "true")
    actions.append({
        "field": f"CrossChecks/{SYNTHETIC_ACTIVE_CROSSCHECK}/Method:{SYNTHETIC_ACTIVE_METHOD}:use",
        "from": before_use,
        "to": "true",
        "changed": before_use != "true",
    })
    for key, wanted in SYNTHETIC_METHOD_PARAMS_TARGET.items():
        set_method_param(
            method,
            key,
            wanted,
            "Integer",
            actions,
            f"CrossChecks/{SYNTHETIC_ACTIVE_CROSSCHECK}/Method:{SYNTHETIC_ACTIVE_METHOD}/Param:{key}",
        )

    set_synthetic_acceptance_conditions(active, actions)
    normalize_synthetic_crosscheck_setups(root, actions)
    return actions


def synthetic_acceptance_conditions_ok(root: ET.Element) -> bool:
    check = root.find(f".//CrossChecks/{SYNTHETIC_ACTIVE_CROSSCHECK}")
    if check is None:
        return False
    conditions = [
        mc_condition_summary(condition)
        for condition in check.findall("./AcceptanceSettings/Conditions/Condition")
    ]
    expected = [
        {"use": "true", "left": item["left"], "comparator": item["comparator"], "right": item["right"]}
        for item in SYNTHETIC_ACCEPTANCE_CONDITIONS_TARGET
    ]
    return conditions == expected


def enforce_synthetic_crosschecks_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = synthetic_crosschecks_summary(root)
    attrs = summary.get("attributes") or {}
    if attrs != SYNTHETIC_CROSSCHECK_PARENT_TARGET:
        issues.append(f"Synthetic/Syntetic CrossChecks attrs are {attrs!r}, expected {SYNTHETIC_CROSSCHECK_PARENT_TARGET!r}")
    if summary.get("active") != [SYNTHETIC_ACTIVE_CROSSCHECK]:
        issues.append(f"Synthetic/Syntetic active crosschecks are {summary.get('active')!r}, expected [{SYNTHETIC_ACTIVE_CROSSCHECK!r}]")

    checks = {item.get("id"): item for item in summary.get("checks") or []}
    active = checks.get(SYNTHETIC_ACTIVE_CROSSCHECK) or {}
    if active.get("numberOfSimulations") != SYNTHETIC_NUMBER_OF_SIMULATIONS:
        issues.append(f"Synthetic/Syntetic NumberOfSimulations is {active.get('numberOfSimulations')!r}, expected {SYNTHETIC_NUMBER_OF_SIMULATIONS!r}")
    if active.get("mcUseFullSample") != SYNTHETIC_USE_FULL_SAMPLE:
        issues.append(f"Synthetic/Syntetic MCUseFullSample is {active.get('mcUseFullSample')!r}, expected {SYNTHETIC_USE_FULL_SAMPLE!r}")
    if active.get("mcBacktestPrecision") != SYNTHETIC_MC_BACKTEST_PRECISION:
        issues.append(f"Synthetic/Syntetic MCBacktestPrecision is {active.get('mcBacktestPrecision')!r}, expected {SYNTHETIC_MC_BACKTEST_PRECISION!r}")
    active_methods = active.get("activeMethodTypes") or []
    if active_methods != [SYNTHETIC_ACTIVE_METHOD]:
        issues.append(f"Synthetic/Syntetic active methods are {active_methods!r}, expected [{SYNTHETIC_ACTIVE_METHOD!r}]")
    method = next((item for item in active.get("methods") or [] if item.get("type") == SYNTHETIC_ACTIVE_METHOD), {})
    params = method.get("params") or {}
    for key, wanted in SYNTHETIC_METHOD_PARAMS_TARGET.items():
        if params.get(key) != wanted:
            issues.append(f"Synthetic/Syntetic {SYNTHETIC_ACTIVE_METHOD} {key} is {params.get(key)!r}, expected {wanted!r}")
    if not synthetic_acceptance_conditions_ok(root):
        issues.append("Synthetic/Syntetic acceptance conditions must be the dedicated SyntheticBootstrapV3 net-profit confidence row")

    for check in summary.get("checks") or []:
        if check.get("id") == SYNTHETIC_ACTIVE_CROSSCHECK:
            continue
        active_methods_in_disabled = [method for method in check.get("methods") or [] if method.get("use") == "true"]
        if active_methods_in_disabled:
            issues.append(f"Inactive Synthetic/Syntetic crosscheck {check.get('id')} still has active methods: {[item.get('type') for item in active_methods_in_disabled]}")

    period = generator_period(SYNTHETIC_PERIOD_KEY)
    for setup in root.findall(".//CrossChecks/*/Settings/Setups/Setup"):
        if setup.get("dateFrom") != period[0] or setup.get("dateTo") != period[1]:
            issues.append(f"Synthetic/Syntetic nested CrossChecks setup dates drifted: {dict(setup.attrib)!r}")
        if setup.get("testPrecision") != SYNTHETIC_DATA_TEST_PRECISION:
            issues.append(f"Synthetic/Syntetic nested CrossChecks setup precision is {setup.get('testPrecision')!r}, expected {SYNTHETIC_DATA_TEST_PRECISION!r}")
        if setup.get("session") != SYNTHETIC_DATA_SESSION:
            issues.append(f"Synthetic/Syntetic nested CrossChecks setup session is {setup.get('session')!r}, expected {SYNTHETIC_DATA_SESSION!r}")
        if setup.get("slippage") != "0" or setup.get("minDist") != "0":
            issues.append(f"Synthetic/Syntetic nested CrossChecks setup costs drifted: {dict(setup.attrib)!r}")
        for chart in setup.findall("Chart"):
            for key, wanted in SYNTHETIC_DEFAULT_CHART_TARGET.items():
                if chart.get(key) != wanted:
                    issues.append(f"Synthetic/Syntetic nested CrossChecks chart {key} is {chart.get(key)!r}, expected {wanted!r}")

    rankings = find_section(root, "Rankings")
    if rankings is not None and (rankings.findtext("ForceRunCrossChecks") or "") != "false":
        issues.append("Synthetic/Syntetic Rankings/ForceRunCrossChecks must remain false")

    for issue in enforce_synthetic_data_databanks_resources_options_guard(root):
        issues.append(f"Data/Resources guard: {issue}")

    guarded_text = section_text(root, "CrossChecks")
    for token in MC_BANNED_DONOR_TOKENS:
        if token in guarded_text:
            issues.append(f"Forbidden donor token leaked into Synthetic/Syntetic CrossChecks: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into Synthetic/Syntetic CrossChecks")
    return issues


def update_synthetic_crosschecks_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload
    task_xml_name, root = load_task_root(cfx, SYNTHETIC_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "synthetic_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = synthetic_crosschecks_summary(root)
    payload["actions"] = apply_synthetic_crosschecks_to_root(root)
    payload["after"] = synthetic_crosschecks_summary(root)
    payload["issues"] = enforce_synthetic_crosschecks_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["xmlChanged"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["changed"] = payload["changedActionCount"] > 0
    payload["targetValues"] = {
        "taskTitle": SYNTHETIC_DISPLAY_TITLE,
        "taskXml": SYNTHETIC_TASK_XML,
        "parent": SYNTHETIC_CROSSCHECK_PARENT_TARGET,
        "onlyActiveCheck": SYNTHETIC_ACTIVE_CROSSCHECK,
        "onlyActiveMethod": SYNTHETIC_ACTIVE_METHOD,
        "numberOfSimulations": SYNTHETIC_NUMBER_OF_SIMULATIONS,
        "mcUseFullSample": SYNTHETIC_USE_FULL_SAMPLE,
        "mcBacktestPrecision": SYNTHETIC_MC_BACKTEST_PRECISION,
        "methodParams": SYNTHETIC_METHOD_PARAMS_TARGET,
        "acceptanceConditions": SYNTHETIC_ACCEPTANCE_CONDITIONS_TARGET,
        "nestedSetupPeriod": SYNTHETIC_PERIOD_KEY,
        "nestedSetupChartSeed": SYNTHETIC_DEFAULT_CHART_TARGET,
    }
    payload["targetRationale"] = {
        "methodology": "Synthetic/Syntetic consumes Monkey survivors and applies SyntheticBootstrapV3 only; it is not Monkey, MC2 or a new optimizer.",
        "filters": "The existing Synthetic net-profit confidence acceptance row is preserved as the task-specific filter instead of copying Monkey filters.",
        "cleanup": "Methods hidden inside inactive MonteCarloManipulation/WhatIf and other crosschecks are switched off to avoid stale execution paths.",
        "naturalResults": "No Results value is forced; passed/failed must remain the natural SQX outcome.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_synthetic_crosschecks_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase10_synthetic_crosschecks_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_synthetic_crosschecks_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase10",
        "operation": "synthetic_crosschecks_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase10_synthetic_crosschecks_diff_review" if not apply else SYNTHETIC_CROSSCHECKS_NEXT,
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase10_synthetic_crosschecks_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def apply_synthetic_what_to_build_to_root(root: ET.Element, actions: list[dict[str, Any]]) -> None:
    what_to_build = find_section(root, "WhatToBuild")
    if what_to_build is None:
        what_to_build = ET.SubElement(root, "WhatToBuild")
        actions.append({"field": "WhatToBuild", "from": None, "to": "created", "changed": True})

    set_or_create_attrs_child(
        what_to_build,
        "StrategyType",
        SYNTHETIC_STRATEGY_TYPE_TARGET,
        actions,
        "WhatToBuild/StrategyType",
    )
    build_mode = what_to_build.find("BuildMode")
    if build_mode is None:
        build_mode = ET.SubElement(what_to_build, "BuildMode", {"generationType": "random-generation"})
        actions.append({"field": "WhatToBuild/BuildMode", "from": None, "to": dict(build_mode.attrib), "changed": True})
    else:
        actions.append({
            "field": "WhatToBuild/BuildMode:generationType",
            "from": build_mode.get("generationType", ""),
            "to": build_mode.get("generationType", ""),
            "changed": False,
            "note": "left as SQX-known placeholder; Synthetic passive behavior is enforced by Monkey Test input, disabled improve parts and disabled evolution toggles",
        })
    for tag, value in SYNTHETIC_PASSIVE_BUILDMODE_TEXT_TARGET.items():
        set_or_create_text_child(build_mode, tag, value, actions, f"WhatToBuild/BuildMode/{tag}")
    for tag, attrs in SYNTHETIC_PASSIVE_BUILDMODE_ATTR_TARGET.items():
        set_or_update_attrs_child(build_mode, tag, attrs, actions, f"WhatToBuild/BuildMode/{tag}")


def apply_synthetic_blocks_to_root(root: ET.Element, source_root: ET.Element | None, actions: list[dict[str, Any]]) -> None:
    blocks = find_blocks(root)
    if blocks is None:
        blocks = ET.SubElement(root, "Blocks", {"type": "simple", "version": "142.2336"})
        actions.append({"field": "Blocks", "from": None, "to": dict(blocks.attrib), "changed": True})

    before_attrs = dict(blocks.attrib)
    blocks.set("type", "simple")
    blocks.set("version", "142.2336")
    actions.append({
        "field": "Blocks:attrs",
        "from": before_attrs,
        "to": dict(blocks.attrib),
        "changed": before_attrs != dict(blocks.attrib),
    })

    source_blocks = find_blocks(source_root)
    if blocks.find("BuildingBlocks") is None and source_blocks is not None:
        actions.append(replace_building_blocks_from_source(blocks, source_blocks))
    else:
        actions.append({
            "field": "BuildingBlocks",
            "changed": False,
            "note": "preserved existing Synthetic indicator universe; passive gate only enforces no-improve, entry and exit contracts",
        })
    if source_blocks is not None:
        for child_name in ("OrderTypes", "ExitTypes"):
            if blocks.find(child_name) is None and source_blocks.find(child_name) is not None:
                blocks.append(ET.fromstring(serialize_xml(source_blocks.find(child_name))))
                actions.append({
                    "field": child_name,
                    "from": None,
                    "to": "copied_from_monkey_source",
                    "changed": True,
                    "note": "Synthetic had no explicit passive block controls; copied Monkey controls before enforcing the methodology contract.",
                })
    enforce_order_types(blocks, actions)
    enforce_exit_types(blocks, actions)
    enforce_external_custom_data(blocks, actions)
    enforce_disabled_build_block_categories(blocks, actions)


def apply_synthetic_passive_generation_to_root(root: ET.Element, source_root: ET.Element | None) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    apply_retest1_parts_to_improve_to_root(root, actions)
    apply_synthetic_what_to_build_to_root(root, actions)
    apply_synthetic_blocks_to_root(root, source_root, actions)
    return actions


def synthetic_passive_generation_summary(root: ET.Element) -> dict[str, Any]:
    return retest1_passive_generation_summary(root)


def enforce_synthetic_passive_generation_guard(root: ET.Element) -> list[str]:
    issues: list[str] = []
    summary = synthetic_passive_generation_summary(root)
    parts = summary.get("partsToImprove") or {}
    for group_name in ("EntryRules", "OrderTypes", "ExitRules"):
        group = parts.get(group_name) or {}
        for side in ("LongImprovement", "ShortImprovement"):
            if (group.get(side) or {}).get("use") != "false":
                issues.append(f"Synthetic/Syntetic {group_name}/{side} must be passive use=false")
    if summary.get("strategyType") != SYNTHETIC_STRATEGY_TYPE_TARGET:
        issues.append("Synthetic/Syntetic StrategyType must point passively to Monkey Test with known SQX attributes")
    build_mode = summary.get("buildMode") or {}
    build_text = build_mode.get("text") or {}
    for tag, value in SYNTHETIC_PASSIVE_BUILDMODE_TEXT_TARGET.items():
        if build_text.get(tag) != value:
            issues.append(f"Synthetic/Syntetic BuildMode {tag} is {build_text.get(tag)!r}, expected {value!r}")
    child_attrs = build_mode.get("childAttrs") or {}
    for tag, attrs in SYNTHETIC_PASSIVE_BUILDMODE_ATTR_TARGET.items():
        current = child_attrs.get(tag) or {}
        for key, value in attrs.items():
            if current.get(key) != value:
                issues.append(f"Synthetic/Syntetic BuildMode {tag}.{key} is {current.get(key)!r}, expected {value!r}")
    blocks = summary.get("blocks") or {}
    actual_order = {key: blocks.get("orderTypes", {}).get(key) for key in BUILD_ORDER_TYPE_TARGET}
    if actual_order != BUILD_ORDER_TYPE_TARGET:
        issues.append(f"Synthetic/Syntetic order types are {actual_order!r}, expected {BUILD_ORDER_TYPE_TARGET!r}")
    exits = blocks.get("exitTypes") or {}
    if exits.get(BUILD_EXIT_TYPE_ACTIVE_KEY, {}).get("use") != "true":
        issues.append("Synthetic/Syntetic must keep only ExitAfterBars active")
    if exits.get(BUILD_EXIT_TYPE_ACTIVE_KEY, {}).get("probability") != "100":
        issues.append("Synthetic/Syntetic ExitAfterBars probability must be 100")
    active_other_exits = [
        key for key, data in exits.items()
        if key != BUILD_EXIT_TYPE_ACTIVE_KEY and (data or {}).get("use") == "true"
    ]
    if active_other_exits:
        issues.append(f"Synthetic/Syntetic has non-passive active exit types: {active_other_exits}")
    if any(any(token in key for token in BUILD_EXIT_TYPE_BANNED_TOKENS) for key in exits):
        issues.append("Synthetic/Syntetic contains day-based exit types")
    if int(blocks.get("activeSignalCount") or 0) != 0:
        issues.append("Synthetic/Syntetic signals must remain disabled in passive retest")
    if int(blocks.get("activeStopLimitCount") or 0) != 0:
        issues.append("Synthetic/Syntetic stop/limit entry blocks must remain disabled in passive retest")
    if int(blocks.get("activeIndicatorCount") or 0) <= 0:
        issues.append("Synthetic/Syntetic must preserve methodology/BlockSettings indicator blocks")
    custom = blocks.get("customData") or {}
    if (custom.get("attrs") or {}).get("showAll") != "false" or custom.get("children") != 0:
        issues.append("Synthetic/Syntetic external CustomData must stay disabled and empty")
    for issue in enforce_synthetic_data_databanks_resources_options_guard(root):
        issues.append(f"Data/Resources guard: {issue}")
    for issue in enforce_synthetic_crosschecks_guard(root):
        issues.append(f"CrossChecks guard: {issue}")
    guarded_sections = [
        find_section(root, "PartsToImprove"),
        find_section(root, "WhatToBuild"),
        find_section(root, "Blocks"),
    ]
    guarded_text = "".join(serialize_xml(section if section is not None else root) for section in guarded_sections)
    for token in ("ExitAfterDays", "ExitAfterTradingDays", "USDJPY_darwinex", "USDJPY_dukascopy", "Strategies to improve"):
        if token in guarded_text:
            issues.append(f"Forbidden token leaked into Synthetic/Syntetic passive generation tabs: {token}")
    if re.search(r"[A-Za-z]:\\", guarded_text):
        issues.append("Local absolute path leaked into Synthetic/Syntetic passive generation tabs")
    return issues


def update_synthetic_passive_generation_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, SYNTHETIC_TASK_TITLE)
    source_task_xml_name, source_root = load_task_root(cfx, SYNTHETIC_PASSIVE_SOURCE_TASK_TITLE)
    payload["taskXml"] = task_xml_name
    payload["sourceTaskXml"] = source_task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "synthetic_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload
    if not source_task_xml_name or source_root is None:
        payload["error"] = "synthetic_source_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    before_text = serialize_xml(root)
    payload["before"] = synthetic_passive_generation_summary(root)
    payload["actions"] = apply_synthetic_passive_generation_to_root(root, source_root)
    payload["after"] = synthetic_passive_generation_summary(root)
    payload["issues"] = enforce_synthetic_passive_generation_guard(root)
    payload["guardOk"] = not payload["issues"]
    after_text = serialize_xml(root)
    payload["changed"] = before_text != after_text
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "strategyType": SYNTHETIC_STRATEGY_TYPE_TARGET,
        "buildModeText": SYNTHETIC_PASSIVE_BUILDMODE_TEXT_TARGET,
        "buildModeAttributes": SYNTHETIC_PASSIVE_BUILDMODE_ATTR_TARGET,
        "sourceTask": SYNTHETIC_PASSIVE_SOURCE_TASK_TITLE,
        "orderTypes": BUILD_ORDER_TYPE_TARGET,
        "exitType": BUILD_EXIT_TYPE_ACTIVE_KEY,
        "disabledCategories": BUILD_BLOCK_CATEGORY_DISABLE_TARGET,
    }
    payload["targetRationale"] = {
        "passiveRetest": "Synthetic/Syntetic consumes Monkey Test survivors and must not improve, generate or alter strategy logic.",
        "noUnknownEnum": "BuildMode.generationType is left as an SQX-known placeholder because no local CFX uses a safe none/passive enum.",
        "blocksSource": "Existing Synthetic indicator blocks are preserved to avoid changing strategy logic; Monkey Test is only a fallback if controls are missing.",
        "methodology": "Signals and Stop/Limit blocks stay off; indicators remain governed by methodology/BlockSettings; only EnterAtMarket plus ExitAfterBars is allowed.",
        "naturalResults": "No Results value is forced; passed/failed must remain the natural SQX outcome after SyntheticBootstrapV3 filters.",
    }
    if apply and payload["changed"] and payload["guardOk"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_synthetic_passive_generation_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase10_synthetic_passive_generation_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_synthetic_passive_generation_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("guardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase10",
        "operation": "synthetic_passive_generation_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase10_synthetic_passive_generation_diff_review" if not apply else SYNTHETIC_PASSIVE_GENERATION_NEXT,
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase10_synthetic_passive_generation_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def update_build_data_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    date_from, date_to = generator_period(BUILD_DATA_PERIOD_KEY)
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, "Build")
    payload["taskXml"] = task_xml_name
    data = find_section(root, "Data")
    setup = root.find(".//Data/Setups/Setup") if root is not None else None
    if not task_xml_name or root is None or data is None or setup is None:
        payload["error"] = "build_task_or_data_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    target_attrs = {
        "dateFrom": date_from,
        "dateTo": date_to,
        "testPrecision": BUILD_DATA_TEST_PRECISION,
        "session": BUILD_DATA_SESSION,
    }
    for key, wanted in target_attrs.items():
        before = setup.get(key, "")
        setup.set(key, wanted)
        payload["actions"].append({
            "field": f"Data/Setup:{key}",
            "from": before,
            "to": wanted,
            "changed": before != wanted,
        })

    removed_oos = []
    out_of_sample = data.find("OutOfSample")
    if out_of_sample is not None:
        for range_node in list(out_of_sample.findall("Range")):
            removed_oos.append(dict(range_node.attrib))
            out_of_sample.remove(range_node)
    payload["actions"].append({
        "field": "Data/OutOfSample/Range",
        "from": removed_oos,
        "to": [],
        "changed": bool(removed_oos),
    })

    charts = [dict(chart.attrib) for chart in setup.findall("Chart")]
    swaps = [dict(swap.attrib) for swap in setup.findall("Swap")]
    payload["generatorOwned"] = {
        "charts": charts,
        "swaps": swaps,
        "note": "Symbol, timeframe, spread and swaps are preserved in the base/template and rewritten by Project Generator per selected asset/timeframe.",
    }
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "periodKey": BUILD_DATA_PERIOD_KEY,
        "dateFrom": date_from,
        "dateTo": date_to,
        "testPrecision": BUILD_DATA_TEST_PRECISION,
        "precisionMeaning": "simulated / 1 minute data tick simulation in SQX 142 UI",
        "session": BUILD_DATA_SESSION,
        "outOfSampleRanges": [],
    }
    payload["targetRationale"] = {
        "methodology": "Build Capa1 mines only IS; OOS validation is performed by later retest tasks.",
        "precision": "Operator confirmed Build data must remain simulated; SQX 142 maps this to testPrecision=2.",
        "genericBase": "Do not copy donor USDJPY/H4 costs; Project Generator owns charts, spreads and swaps.",
    }
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_build_data_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase2_build_data_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_build_data_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(item.get("exists") and item.get("isZip") and not item.get("error") for item in results.values()),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_data_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase2_build_data_diff_review" if not apply else "phase2_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_data_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def build_resources_summary(root: ET.Element) -> dict[str, Any]:
    resources = root.find(".//Resources")
    chart_symbols = sorted({
        chart.get("symbol", "")
        for chart in root.findall(".//Data/Setups/Setup/Chart")
        if chart.get("symbol")
    })
    if resources is None:
        return {"chartSymbols": chart_symbols, "resourcesFound": False}
    symbols = [dict(symbol.attrib) for symbol in resources.findall("./Symbols/Symbol")]
    brokers = [dict(broker.attrib) for broker in resources.findall("./Brokers/Broker")]
    sessions = [dict(session.attrib) for session in resources.findall("./Sessions/Session")]
    instruments = [dict(instrument.attrib) for instrument in resources.findall("./Instruments/InstrumentInfo")]
    nested_infos = []
    for symbol in resources.findall("./Symbols/Symbol"):
        info = symbol.find("InstrumentInfo")
        nested_infos.append(dict(info.attrib) if info is not None else {})
    return {
        "chartSymbols": chart_symbols,
        "resourcesFound": True,
        "symbols": symbols,
        "brokers": brokers,
        "sessions": sessions,
        "instruments": instruments,
        "nestedInstrumentInfos": nested_infos,
    }


def enforce_build_resources_guard(root: ET.Element, actions: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    resources = root.find(".//Resources")
    if resources is None:
        issues.append("Resources section missing")
        return issues

    chart_symbols = {
        chart.get("symbol", "")
        for chart in root.findall(".//Data/Setups/Setup/Chart")
        if chart.get("symbol")
    }
    symbols = resources.findall("./Symbols/Symbol")
    symbol_names = {symbol.get("name", "") for symbol in symbols if symbol.get("name")}
    if chart_symbols != symbol_names:
        issues.append(f"Chart symbols {sorted(chart_symbols)} do not match resource symbols {sorted(symbol_names)}")

    sessions = resources.find("Sessions")
    removed_sessions = []
    if sessions is not None:
        for session in list(sessions.findall("Session")):
            removed_sessions.append(dict(session.attrib))
            sessions.remove(session)
    actions.append({
        "field": "Resources/Sessions/Session",
        "from": removed_sessions,
        "to": [],
        "changed": bool(removed_sessions),
    })

    broker_ids = {broker.get("id", "") for broker in resources.findall("./Brokers/Broker") if broker.get("id")}
    for symbol in symbols:
        name = symbol.get("name", "")
        before_precision = symbol.get("precision", "")
        symbol.set("precision", BUILD_RESOURCES_PRECISION)
        actions.append({
            "field": f"Resources/Symbols/Symbol:{name}:precision",
            "from": before_precision,
            "to": BUILD_RESOURCES_PRECISION,
            "changed": before_precision != BUILD_RESOURCES_PRECISION,
        })
        broker = symbol.get("broker", "")
        if broker not in {"", "-1"} and broker not in broker_ids:
            issues.append(f"Resource symbol {name} references missing broker {broker}")
        info = symbol.find("InstrumentInfo")
        if info is None:
            issues.append(f"Resource symbol {name} has no nested InstrumentInfo")
            continue
        info_broker = info.get("broker", "")
        if info_broker not in {"", "-1"} and info_broker not in broker_ids:
            issues.append(f"Nested InstrumentInfo for {name} references missing broker {info_broker}")

    for instrument in resources.findall("./Instruments/InstrumentInfo"):
        instrument_name = instrument.get("instrument", "")
        if instrument_name and instrument_name not in symbol_names:
            issues.append(f"Standalone InstrumentInfo {instrument_name} is not represented in Resources/Symbols")

    resource_text = serialize_xml(resources)
    for token in BUILD_RESOURCES_BANNED_DONOR_TOKENS:
        if token in resource_text:
            issues.append(f"Donor token leaked into base resources: {token}")
    if re.search(r"[A-Za-z]:\\", resource_text):
        issues.append("Local absolute path leaked into base resources")
    return issues


def update_build_resources_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, "Build")
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "build_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    payload["before"] = build_resources_summary(root)
    issues = enforce_build_resources_guard(root, payload["actions"])
    payload["after"] = build_resources_summary(root)
    payload["issues"] = issues
    payload["resourceGuardOk"] = not issues
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "precision": BUILD_RESOURCES_PRECISION,
        "baseDataType": BUILD_RESOURCES_BASE_DATA_TYPE,
        "sessions": [],
        "bannedDonorTokens": list(BUILD_RESOURCES_BANNED_DONOR_TOKENS),
    }
    payload["targetRationale"] = {
        "genericBase": "Do not copy donor USDJPY resources; base/template placeholders stay generic.",
        "generatorOwned": "Project Generator rebuilds Symbols, Brokers, Instruments and resource dates for the selected asset/timeframe/target profile.",
        "simulatedData": "Resources precision=TICK describes source data; Build simulated mode remains Data/Setup testPrecision=2.",
    }
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_build_resources_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase2_build_resources_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_build_resources_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("resourceGuardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_resources_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase2_build_resources_diff_review" if not apply else "phase2_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_resources_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def build_crosschecks_summary(root: ET.Element | None) -> dict[str, Any]:
    parent = root.find(".//CrossChecks") if root is not None else None
    if parent is None:
        return {"exists": False, "active": [], "checks": []}
    checks = []
    active = []
    for check in list(parent):
        if not isinstance(check.tag, str) or check.get("use") is None:
            continue
        methods = [
            {
                "type": method.get("type", ""),
                "use": method.get("use", ""),
                "settings": {
                    param.get("key", ""): (param.text or "")
                    for param in method.findall(".//Param")
                    if param.get("key")
                },
            }
            for method in check.findall(".//Method")
            if method.get("use") == "true"
        ]
        conditions = [
            dict(condition.attrib)
            for condition in check.findall(".//AcceptanceSettings//Condition")
            if condition.get("use", "true") != "false"
        ]
        item = {
            "id": check.tag,
            "use": check.get("use", ""),
            "activeMethodCount": len(methods),
            "activeConditionCount": len(conditions),
            "activeMethods": methods,
        }
        checks.append(item)
        if check.get("use") == "true":
            active.append(check.tag)
    return {"exists": True, "attributes": dict(parent.attrib), "active": active, "checks": checks}


def enforce_build_crosschecks_guard(root: ET.Element, actions: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    parent = root.find(".//CrossChecks")
    if parent is None:
        return ["CrossChecks section missing"]

    for key, wanted in BUILD_CROSSCHECK_PARENT_TARGET.items():
        before = parent.get(key, "")
        parent.set(key, wanted)
        actions.append({
            "field": f"CrossChecks:{key}",
            "from": before,
            "to": wanted,
            "changed": before != wanted,
        })

    for check in list(parent):
        if not isinstance(check.tag, str) or check.get("use") is None:
            continue
        wanted = "true" if check.tag == BUILD_ACTIVE_CROSSCHECK else "false"
        before = check.get("use", "")
        check.set("use", wanted)
        actions.append({
            "field": f"CrossChecks/{check.tag}:use",
            "from": before,
            "to": wanted,
            "changed": before != wanted,
        })

    active = [check.tag for check in list(parent) if isinstance(check.tag, str) and check.get("use") == "true"]
    if active != [BUILD_ACTIVE_CROSSCHECK]:
        issues.append(f"Build active crosschecks must be only {BUILD_ACTIVE_CROSSCHECK}; found {active}")

    active_text = "".join(
        serialize_xml(check)
        for check in list(parent)
        if isinstance(check.tag, str) and check.get("use") == "true"
    )
    for token in BUILD_CROSSCHECK_BANNED_DONOR_TOKENS:
        if token in active_text:
            issues.append(f"Donor token leaked into active Build crosscheck: {token}")
    return issues


def update_build_crosschecks_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, "Build")
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["error"] = "build_task_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    payload["before"] = build_crosschecks_summary(root)
    issues = enforce_build_crosschecks_guard(root, payload["actions"])
    payload["after"] = build_crosschecks_summary(root)
    payload["issues"] = issues
    payload["crossChecksGuardOk"] = not issues
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetValues"] = {
        "parent": BUILD_CROSSCHECK_PARENT_TARGET,
        "onlyActive": BUILD_ACTIVE_CROSSCHECK,
        "bannedDonorTokensInActiveChecks": list(BUILD_CROSSCHECK_BANNED_DONOR_TOKENS),
    }
    payload["targetRationale"] = {
        "methodology": "Build mining keeps only the lightweight SequentialOptimization crosscheck active.",
        "noDonorCopy": "Disabled crosscheck internals are not promoted from donor to avoid dragging symbols, dates or heavy robustness settings into mining.",
        "quality": "Heavy robustness checks remain scheduled as dedicated retest tasks outside Build.",
    }
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_build_crosschecks_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase2_build_crosschecks_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_build_crosschecks_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(
            item.get("exists")
            and item.get("isZip")
            and not item.get("error")
            and item.get("crossChecksGuardOk")
            for item in results.values()
        ),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_crosschecks_target",
        "apply": apply,
        "target": target,
        "results": results,
        "nextPhase": "phase2_build_crosschecks_diff_review" if not apply else "phase2_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_crosschecks_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def section_text(root: ET.Element | None, tab: str) -> str:
    node = find_section(root, tab)
    if node is None:
        return ""
    return serialize_xml(node).strip()


def section_sha256(root: ET.Element | None, tab: str) -> str:
    text = section_text(root, tab)
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper() if text else ""


def static_tab_business_checks(root: ET.Element | None) -> list[str]:
    issues: list[str] = []
    if root is None:
        return ["Build task missing"]

    fixed_size = root.find(".//RiskMoneyManagement//Method[@type='FixedSize']")
    fixed_amount = root.find(".//RiskMoneyManagement//Method[@type='FixedAmount']")
    if fixed_size is None or fixed_size.get("use") != "true":
        issues.append("RiskMoneyManagement FixedSize must remain active")
    if fixed_amount is None or fixed_amount.get("use") != "false":
        issues.append("RiskMoneyManagement FixedAmount must remain disabled")

    databanks = {
        databank.get("name", ""): databank.get("value", "")
        for databank in root.findall(".//Databanks/Databank")
        if databank.get("name")
    }
    if databanks.get("Output") != "null":
        issues.append("Build Databanks Output must remain null; Ranking stores filtered strategies into Results")
    if "Input" not in databanks:
        issues.append("Build Databanks Input placeholder missing")

    market_open = root.find(".//BuildTradingOptions/Params/Param[@key='MarketOpenSession']")
    if market_open is not None and (market_open.text or "") != "No Session":
        issues.append("Build Options MarketOpenSession must remain No Session")
    return issues


def static_tabs_report(cfx: Path, baseline_hashes: dict[str, str] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "tabs": {},
        "issues": [],
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["issues"].append("missing_or_not_zip")
        return payload
    task_xml_name, root = load_task_root(cfx, "Build")
    payload["taskXml"] = task_xml_name
    if not task_xml_name or root is None:
        payload["issues"].append("build_task_not_found")
        return payload
    for tab in BUILD_STATIC_TABS:
        digest = section_sha256(root, tab)
        expected = (baseline_hashes or BUILD_STATIC_TAB_HASHES).get(tab, "")
        payload["tabs"][tab] = {
            "exists": bool(digest),
            "sha256": digest,
            "expectedSha256": expected,
            "matchesExpected": bool(digest and expected and digest == expected),
        }
        if not digest:
            payload["issues"].append(f"{tab} section missing")
        elif expected and digest != expected:
            payload["issues"].append(f"{tab} section drift: {digest} != {expected}")
    payload["issues"].extend(static_tab_business_checks(root))
    payload["staticTabsGuardOk"] = not payload["issues"]
    return payload


def promote_build_static_tabs_target(root142: Path, project_root: Path, target: str) -> dict[str, Any]:
    ensure_ledger(project_root)
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {name: static_tabs_report(path) for name, path in targets.items()}
    payload: dict[str, Any] = {
        "ok": all(item.get("exists") and item.get("isZip") and item.get("staticTabsGuardOk") for item in results.values()),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_static_tabs_target",
        "target": target,
        "tabs": list(BUILD_STATIC_TABS),
        "mode": "audit_only_keep_current_values",
        "results": results,
        "targetRationale": {
            "operatorDecision": "Options, ATMs, PartsToImprove, RiskMoneyManagement, Notes and Optimization stay as current values.",
            "databanks": "Build Databanks stay as current placeholder; Ranking filters decide what is saved to Results.",
            "nextStep": "If this audit passes, Build Capa1 Phase 2 can close and move to RETEST 0.",
        },
        "nextPhase": "phase2_closeout_or_phase3_retest0",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_static_tabs_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def update_build_blocks_target_in_cfx(cfx: Path, backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload

    task_xml_name, root = load_task_root(cfx, "Build")
    payload["taskXml"] = task_xml_name
    blocks = find_blocks(root)
    if not task_xml_name or root is None or blocks is None:
        payload["error"] = "build_task_or_blocks_not_found"
        payload["sha256After"] = payload["sha256Before"]
        return payload

    enforce_order_types(blocks, payload["actions"])
    enforce_exit_types(blocks, payload["actions"])
    enforce_external_custom_data(blocks, payload["actions"])
    enforce_disabled_build_block_categories(blocks, payload["actions"])

    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("changed"))
    payload["targetRationale"] = {
        "fixedLeftSide": "Signals and Stop/Limit entry blocks stay disabled in Capa1 base.",
        "preservedLeftSide": "Indicators remain methodology/BlockSettings owned and are not rewritten here.",
        "fixedBlueSide": "Only EnterAtMarket and ExitAfterBars are allowed in Capa1 base; external custom data stays empty.",
        "exitDays": "Day-based exits are removed from the CFX so they cannot be selected by the Builder.",
    }
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_zip_text_entry(cfx, task_xml_name, serialize_xml(root))
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_build_blocks_target(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    backup_root = ledger_root(project_root) / "backups" / f"phase2_build_blocks_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_build_blocks_target_in_cfx(path, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(item.get("exists") and item.get("isZip") and not item.get("error") for item in results.values()),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "build_blocks_target",
        "apply": apply,
        "target": target,
        "results": results,
        "targetValues": {
            "orderTypes": BUILD_ORDER_TYPE_TARGET,
            "activeExitType": BUILD_EXIT_TYPE_ACTIVE_KEY,
            "bannedExitTokens": list(BUILD_EXIT_TYPE_BANNED_TOKENS),
            "customData": BUILD_EXTERNAL_CUSTOM_DATA_TARGET,
            "disabledBlockCategories": list(BUILD_BLOCK_CATEGORY_DISABLE_TARGET),
            "preservedBlockCategories": list(BUILD_BLOCK_CATEGORY_PRESERVE_TARGET),
        },
        "nextPhase": "phase2_build_blocks_diff_review" if not apply else "phase2_continue_questionnaire",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_build_blocks_target_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def exit_day_snippet_candidates(root142: Path) -> list[Path]:
    extend_root = root142 / "user" / "extend"
    if not extend_root.is_dir():
        return []
    tokens = ("ExitAfterDays", "ExitAfterTradingDays")
    suffixes = {".java", ".tpl"}
    return sorted(
        path
        for path in extend_root.rglob("*")
        if path.is_file()
        and path.suffix in suffixes
        and any(token in path.name for token in tokens)
    )


def archive_exit_day_snippets(root142: Path, project_root: Path, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    extend_root = (root142 / "user" / "extend").resolve()
    archive_root = ledger_root(project_root) / "backups" / f"exit_day_snippets_{stamp()}"
    candidates = exit_day_snippet_candidates(root142)
    actions = []
    for source in candidates:
        resolved = source.resolve()
        if not str(resolved).casefold().startswith(str(extend_root).casefold()):
            actions.append({"source": str(source), "error": "outside_user_extend", "willMove": False})
            continue
        relative = resolved.relative_to(extend_root)
        target = archive_root / relative
        actions.append({
            "source": str(resolved),
            "target": str(target),
            "willMove": apply,
        })
        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(resolved), str(target))
    payload = {
        "ok": all(not item.get("error") for item in actions),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase2",
        "operation": "archive_exit_day_snippets",
        "apply": apply,
        "sqxRoot": str(root142),
        "archiveRoot": str(archive_root) if apply else "",
        "candidateCount": len(candidates),
        "actions": actions,
        "rationale": "Capa1 methodology allows ExitAfterBars only; user-level day-based exit snippets are archived reversibly.",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase2_exit_day_snippet_archive_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def update_databank_views_in_cfx(cfx: Path, target_views: dict[str, str], backup_root: Path, apply: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": str(cfx),
        "exists": cfx.is_file(),
        "isZip": bool(cfx.is_file() and zipfile.is_zipfile(cfx)),
        "sha256Before": file_sha256(cfx) if cfx.is_file() else "",
        "actions": [],
        "backup": "",
        "willWrite": apply,
    }
    if not cfx.is_file() or not zipfile.is_zipfile(cfx):
        payload["error"] = "missing_or_not_zip"
        return payload
    with zipfile.ZipFile(cfx, "r") as zf:
        config_text = safe_zip_text(zf, "config.xml")
    if not config_text:
        payload["error"] = "config_unreadable"
        return payload
    updated = config_text
    current_views = config_databank_views(cfx)
    for databank, wanted_view in sorted(target_views.items()):
        current = current_views.get(databank, "")
        if current == wanted_view:
            continue
        pattern = rf'(<Databank\b(?=[^>]*\bname="{re.escape(databank)}")[^>]*\bview=")[^"]*(")'
        updated_candidate, count = re.subn(pattern, rf"\1{wanted_view}\2", updated, count=1)
        payload["actions"].append({
            "databank": databank,
            "from": current,
            "to": wanted_view,
            "matched": count == 1,
            "willWrite": bool(apply and count == 1),
        })
        updated = updated_candidate
    payload["changedActionCount"] = sum(1 for item in payload["actions"] if item.get("matched"))
    if apply and payload["changedActionCount"]:
        backup = backup_file(cfx, backup_root)
        payload["backup"] = str(backup)
        replace_config_xml_in_cfx(cfx, updated)
        payload["sha256After"] = file_sha256(cfx)
    else:
        payload["sha256After"] = payload["sha256Before"]
    return payload


def promote_view_assignments(root142: Path, project_root: Path, target: str, apply: bool) -> dict[str, Any]:
    ensure_ledger(project_root)
    donor_cfx = cfx_for_project(root142, DEFAULT_DONOR_PROJECT)
    donor_views = config_databank_views(donor_cfx)
    target_views = {
        databank: expected
        for databank, expected in VIEW_PROMOTION_TARGETS.items()
        if donor_views.get(databank) == expected
    }
    backup_root = ledger_root(project_root) / "backups" / f"phase1_views_{stamp()}"
    targets: dict[str, Path] = {}
    if target in {"local-base", "both"}:
        targets["localBase"] = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    if target in {"repo-template", "both"}:
        targets["repoTemplate"] = DEFAULT_TEMPLATE
    results = {
        name: update_databank_views_in_cfx(path, target_views, backup_root / name, apply=apply)
        for name, path in targets.items()
    }
    payload: dict[str, Any] = {
        "ok": all(item.get("exists") and item.get("isZip") and not item.get("error") for item in results.values()),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase1",
        "apply": apply,
        "target": target,
        "donorProject": DEFAULT_DONOR_PROJECT,
        "targetViews": target_views,
        "results": results,
        "promotionRule": "Only allowlisted view assignments that already match the donor are promoted.",
        "nextPhase": "phase2",
    }
    evidence_target = ledger_root(project_root) / "diffs" / f"phase1_view_promotion_{stamp()}.json"
    write_json(evidence_target, payload)
    payload["written"] = str(evidence_target)
    return payload


def task_by_title(snapshot: dict[str, Any], title: str) -> dict[str, Any]:
    wanted = title.casefold()
    canonical_wanted = canonical_task_key(title)
    for item in snapshot.get("tasks", []):
        candidate = str(item.get("title", ""))
        if candidate.casefold() == wanted or canonical_task_key(candidate) == canonical_wanted:
            return item
    return {}


def semantic_diff(donor: dict[str, Any], base: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    base_databank_views = {item.get("name", ""): item.get("view", "") for item in base.get("databanks", [])}
    donor_databank_views = {item.get("name", ""): item.get("view", "") for item in donor.get("databanks", [])}
    view_candidates = []
    for name, expected in VIEW_PROMOTION_TARGETS.items():
        donor_view = donor_databank_views.get(name, "")
        base_view = base_databank_views.get(name, "")
        if donor_view == expected and base_view != expected:
            view_candidates.append({
                "databank": name,
                "baseView": base_view,
                "donorView": donor_view,
                "recommended": "promote_view_assignment",
            })

    task_diffs = []
    for donor_task in donor.get("tasks", []):
        title = donor_task.get("title", "")
        base_task = task_by_title(base, title)
        if not base_task:
            # Known base title placeholder for Build is expected.
            if str(donor_task.get("type")) == "Build":
                base_task = next((item for item in base.get("tasks", []) if item.get("type") == "Build"), {})
        if not base_task:
            task_diffs.append({"title": title, "issue": "missing_in_base", "recommendation": "manual_review"})
            continue
        setup_diff = {}
        for key in ("dateFrom", "dateTo", "session", "testPrecision"):
            donor_value = (donor_task.get("setup") or {}).get(key, "")
            base_value = (base_task.get("setup") or {}).get(key, "")
            if donor_value != base_value:
                setup_diff[key] = {"base": base_value, "donor": donor_value}
        donor_checks = [item.get("id") for item in donor_task.get("activeCrossChecks", [])]
        base_checks = [item.get("id") for item in base_task.get("activeCrossChecks", [])]
        if setup_diff or donor_checks != base_checks or donor_task.get("randomizeSpread") != base_task.get("randomizeSpread"):
            task_diffs.append({
                "title": title,
                "taskXml": donor_task.get("taskXml", ""),
                "setupDiff": setup_diff,
                "activeCrossChecks": {"base": base_checks, "donor": donor_checks},
                "randomizeSpread": {
                    "base": base_task.get("randomizeSpread"),
                    "donor": donor_task.get("randomizeSpread"),
                },
                "recommendation": "questionnaire_before_promotion",
            })

    return {
        "version": VERSION,
        "createdAt": now_iso(),
        "source": {
            "donor": donor.get("label"),
            "base": base.get("label"),
            "template": template.get("label"),
        },
        "promotionMode": "selective_normalized",
        "candidatePromotions": {
            "viewAssignments": view_candidates,
            "mc2AdaptiveSpread": [
                item for item in task_diffs
                if str(item.get("title", "")).casefold() == "mc 2"
                and (item.get("randomizeSpread") or {}).get("donor")
            ],
        },
        "requiresQuestionnaire": task_diffs,
        "doNotPromoteDirectly": sorted(DO_NOT_PROMOTE_FIELDS),
        "templateSha256": template.get("sha256", ""),
        "baseSha256": base.get("sha256", ""),
        "donorSha256": donor.get("sha256", ""),
        "nextPhase": "phase1" if view_candidates else "phase2",
    }


def process_snapshot() -> dict[str, Any]:
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-Process | Where-Object { $_.ProcessName -like 'StrategyQuantX*' -or $_.ProcessName -like 'java*' } | Select-Object ProcessName,Id | ConvertTo-Json -Compress",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=8, check=False)
    except (OSError, subprocess.SubprocessError):
        return {"ok": False, "processes": [], "error": "process_probe_failed"}
    raw = (proc.stdout or "").strip()
    if not raw:
        return {"ok": True, "processes": []}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"ok": False, "processes": [], "raw": raw}
    if isinstance(parsed, dict):
        parsed = [parsed]
    return {"ok": True, "processes": parsed}


def preflight(root142: Path, project_root: Path, apply: bool) -> dict[str, Any]:
    dirs = ensure_ledger(project_root) if apply else {key: str(ledger_root(project_root) / key) for key in ("root",)}
    donor_cfx = cfx_for_project(root142, DEFAULT_DONOR_PROJECT)
    base_cfx = cfx_for_project(root142, DEFAULT_BASE_PROJECT)
    template_cfx = DEFAULT_TEMPLATE
    paths = {
        "sqxRoot": str(root142),
        "donorProject": str(donor_cfx),
        "baseProject": str(base_cfx),
        "repoTemplate": str(template_cfx),
    }
    donor = extract_cfx_snapshot(donor_cfx, DEFAULT_DONOR_PROJECT, include_hashes=True)
    base = extract_cfx_snapshot(base_cfx, DEFAULT_BASE_PROJECT, include_hashes=True)
    template = extract_cfx_snapshot(template_cfx, "backend template Capa1_Long.cfx", include_hashes=True)
    diff = semantic_diff(donor, base, template)
    payload = {
        "ok": all(item.get("exists") and item.get("isZip") for item in (donor, base, template)),
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": "phase0",
        "apply": apply,
        "paths": paths,
        "ledger": dirs,
        "processProbe": process_snapshot(),
        "snapshots": {
            "donor": donor,
            "base": base,
            "template": template,
        },
        "semanticDiff": diff,
        "discipline": {
            "sourceOfTruth": DEFAULT_DONOR_PROJECT,
            "promotion": "selective_normalized",
            "answers": "write full local ledger and sanitized docs summary",
            "noDirectPromotion": sorted(DO_NOT_PROMOTE_FIELDS),
        },
    }
    if apply:
        root = ledger_root(project_root)
        donor_path = root / "snapshots" / f"donor_{stamp()}.json"
        base_path = root / "snapshots" / f"base_{stamp()}.json"
        template_path = root / "snapshots" / f"template_{stamp()}.json"
        diff_path = root / "diffs" / f"semantic_diff_{stamp()}.json"
        write_json(donor_path, donor)
        write_json(base_path, base)
        write_json(template_path, template)
        write_json(diff_path, diff)
        next_phase = str(diff.get("nextPhase", "phase1"))
        state = {
            "version": VERSION,
            "updatedAt": now_iso(),
            "currentPhase": "phase1" if next_phase == "phase2" else "phase0",
            "nextPhase": next_phase,
            "scope": "capa1",
            "donorProject": DEFAULT_DONOR_PROJECT,
            "baseProject": DEFAULT_BASE_PROJECT,
            "repoTemplate": str(DEFAULT_TEMPLATE),
            "ledgerPolicy": ".local full answers plus sanitized docs summary",
            "lastPreflight": {
                "donorSnapshot": str(donor_path),
                "baseSnapshot": str(base_path),
                "templateSnapshot": str(template_path),
                "semanticDiff": str(diff_path),
            },
        }
        state_path = root / "session_state.json"
        write_json(state_path, state)
        payload["written"] = {
            "sessionState": str(state_path),
            "donorSnapshot": str(donor_path),
            "baseSnapshot": str(base_path),
            "templateSnapshot": str(template_path),
            "semanticDiff": str(diff_path),
        }
    return payload


def status(project_root: Path) -> dict[str, Any]:
    root = ledger_root(project_root)
    state = read_json(root / "session_state.json", {})
    return {
        "ok": root.is_dir(),
        "version": VERSION,
        "createdAt": now_iso(),
        "ledgerRoot": str(root),
        "sessionState": state,
        "phaseReports": len(list((root / "phase_reports").glob("*.json"))) if (root / "phase_reports").is_dir() else 0,
        "questionnaires": len(list((root / "questionnaires").rglob("*.json"))) if (root / "questionnaires").is_dir() else 0,
        "answerFiles": len(list((root / "answers").rglob("*.json"))) if (root / "answers").is_dir() else 0,
        "processProbe": process_snapshot(),
    }


def record_answer(project_root: Path, task_title_wanted: str, tab: str, question_id: str, answer: str, note: str) -> dict[str, Any]:
    ensure_ledger(project_root)
    target = ledger_root(project_root) / "answers" / "capa1" / slug(task_title_wanted) / f"{slug(tab)}.json"
    payload = read_json(target, {
        "version": VERSION,
        "scope": "capa1",
        "taskTitle": task_title_wanted,
        "tab": tab,
        "answers": {},
        "createdAt": now_iso(),
    })
    payload["updatedAt"] = now_iso()
    payload.setdefault("answers", {})[question_id] = {
        "answer": answer,
        "note": note,
        "answeredAt": now_iso(),
    }
    write_json(target, payload)
    return {"ok": True, "version": VERSION, "written": str(target), "questionId": question_id}


def latest_questionnaire_path(project_root: Path, task_title_wanted: str, tab: str) -> Path | None:
    root = ledger_root(project_root) / "questionnaires" / "capa1" / slug(task_title_wanted)
    if not root.is_dir():
        return None
    candidates = [
        path
        for path in root.glob(f"{slug(tab)}_*.json")
        if path.is_file() and not path.name.startswith("_task_summary_")
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name))


def record_tab_answer(
    project_root: Path,
    task_title_wanted: str,
    tab: str,
    answer: str,
    note: str,
    allow_empty: bool,
) -> dict[str, Any]:
    ensure_ledger(project_root)
    source = latest_questionnaire_path(project_root, task_title_wanted, tab)
    if source is None:
        return {
            "ok": False,
            "version": VERSION,
            "error": "questionnaire_not_found",
            "taskTitle": task_title_wanted,
            "tab": tab,
            "hint": "Run questionnaire --write before recording a tab answer.",
        }

    questionnaire = read_json(source, {})
    questions = questionnaire.get("questions") or []
    if not questions and not allow_empty:
        return {
            "ok": False,
            "version": VERSION,
            "error": "questionnaire_has_no_questions",
            "sourceQuestionnaire": str(source),
            "taskTitle": task_title_wanted,
            "tab": tab,
            "hint": "Use --allow-empty if this tab is intentionally empty.",
        }

    ids = [str(item.get("id", "")).strip() for item in questions if str(item.get("id", "")).strip()]
    id_counts = Counter(ids)
    duplicate_ids = sorted(qid for qid, count in id_counts.items() if count > 1)
    if duplicate_ids:
        return {
            "ok": False,
            "version": VERSION,
            "error": "duplicate_question_ids",
            "sourceQuestionnaire": str(source),
            "taskTitle": task_title_wanted,
            "tab": tab,
            "questionCount": len(questions),
            "uniqueQuestionCount": len(set(ids)),
            "duplicateIdCount": len(duplicate_ids),
            "duplicateIdSample": duplicate_ids[:10],
            "hint": "Regenerate the questionnaire with the current tool before recording bulk answers.",
        }

    if not ids and allow_empty:
        ids = [question_id(f"{task_title_wanted}-{tab}-empty-tab-confirmed")]

    answered_at = now_iso()
    payload = {
        "version": VERSION,
        "scope": "capa1",
        "taskTitle": task_title_wanted,
        "tab": tab,
        "createdAt": answered_at,
        "updatedAt": answered_at,
        "bulkAnswer": True,
        "sourceQuestionnaire": str(source),
        "questionCount": len(questions),
        "uniqueQuestionCount": len(ids),
        "answer": answer,
        "note": note,
        "answers": {
            qid: {
                "answer": answer,
                "note": note,
                "answeredAt": answered_at,
            }
            for qid in ids
        },
    }
    target = ledger_root(project_root) / "answers" / "capa1" / slug(task_title_wanted) / f"{slug(tab)}.json"
    write_json(target, payload)
    return {
        "ok": True,
        "version": VERSION,
        "written": str(target),
        "sourceQuestionnaire": str(source),
        "taskTitle": task_title_wanted,
        "tab": tab,
        "answerCount": len(ids),
        "questionCount": len(questions),
        "bulkAnswer": True,
    }


def phase_report(project_root: Path, phase_id: str, summary: str, next_phase: str, write: bool) -> dict[str, Any]:
    root = ledger_root(project_root)
    payload = {
        "ok": True,
        "version": VERSION,
        "createdAt": now_iso(),
        "phase": phase_id,
        "summary": summary,
        "nextPhase": next_phase,
        "answerFiles": [
            str(path)
            for path in sorted((root / "answers" / "capa1").rglob("*.json"))
        ] if (root / "answers" / "capa1").is_dir() else [],
    }
    if write:
        ensure_ledger(project_root)
        target = root / "phase_reports" / f"{phase_id}_{stamp()}.json"
        write_json(target, payload)
        state_path = root / "session_state.json"
        state = read_json(state_path, {})
        state.update({"updatedAt": now_iso(), "currentPhase": phase_id, "nextPhase": next_phase})
        write_json(state_path, state)
        payload["written"] = str(target)
    return payload


def list_phases() -> dict[str, Any]:
    return {"ok": True, "version": VERSION, "phases": PHASES}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sqx142-task-config-gate")
    parser.add_argument("--sqx-root", type=Path, default=DEFAULT_SQX_ROOT)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status")
    pre = sub.add_parser("preflight")
    pre.add_argument("--apply", action="store_true")
    sub.add_parser("phases")

    promote_views = sub.add_parser("promote-views")
    promote_views.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_views.add_argument("--apply", action="store_true")

    promote_genetic = sub.add_parser("build-genetic-target")
    promote_genetic.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_genetic.add_argument("--apply", action="store_true")

    promote_ranking = sub.add_parser("build-ranking-target")
    promote_ranking.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_ranking.add_argument("--apply", action="store_true")

    promote_blocks = sub.add_parser("build-blocks-target")
    promote_blocks.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_blocks.add_argument("--apply", action="store_true")

    promote_indicators = sub.add_parser("build-indicators-target")
    promote_indicators.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_indicators.add_argument("--blocksetting", default=BUILD_INDICATORS_DEFAULT_BLOCKSETTING)
    promote_indicators.add_argument("--timeframe", default=BUILD_INDICATORS_DEFAULT_TIMEFRAME)
    promote_indicators.add_argument("--apply", action="store_true")

    promote_data = sub.add_parser("build-data-target")
    promote_data.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_data.add_argument("--apply", action="store_true")

    promote_resources = sub.add_parser("build-resources-target")
    promote_resources.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_resources.add_argument("--apply", action="store_true")

    promote_crosschecks = sub.add_parser("build-crosschecks-target")
    promote_crosschecks.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    promote_crosschecks.add_argument("--apply", action="store_true")

    promote_static_tabs = sub.add_parser("build-static-tabs-target")
    promote_static_tabs.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")

    retest1_data_resources = sub.add_parser("retest1-data-resources-target")
    retest1_data_resources.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    retest1_data_resources.add_argument("--apply", action="store_true")

    retest1_odr = sub.add_parser("retest1-options-databanks-rankings-target")
    retest1_odr.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    retest1_odr.add_argument("--apply", action="store_true")

    retest1_passive = sub.add_parser("retest1-passive-generation-target")
    retest1_passive.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    retest1_passive.add_argument("--apply", action="store_true")

    retest1_static = sub.add_parser("retest1-static-crosschecks-target")
    retest1_static.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    retest1_static.add_argument("--apply", action="store_true")

    tick_real_data = sub.add_parser("tick-real-data-databanks-resources-target")
    tick_real_data.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    tick_real_data.add_argument("--apply", action="store_true")

    tick_real_options = sub.add_parser("tick-real-options-rankings-target")
    tick_real_options.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    tick_real_options.add_argument("--apply", action="store_true")

    tick_real_passive = sub.add_parser("tick-real-passive-generation-target")
    tick_real_passive.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    tick_real_passive.add_argument("--apply", action="store_true")

    tick_real_static = sub.add_parser("tick-real-static-crosschecks-target")
    tick_real_static.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    tick_real_static.add_argument("--apply", action="store_true")

    mc_data = sub.add_parser("mc-data-databanks-resources-options-target")
    mc_data.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    mc_data.add_argument("--apply", action="store_true")

    mc_crosschecks = sub.add_parser("mc-crosschecks-target")
    mc_crosschecks.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    mc_crosschecks.add_argument("--apply", action="store_true")

    mc_passive = sub.add_parser("mc-passive-generation-target")
    mc_passive.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    mc_passive.add_argument("--apply", action="store_true")

    mc_static = sub.add_parser("mc-static-tabs-target")
    mc_static.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    mc_static.add_argument("--apply", action="store_true")

    mc_closeout = sub.add_parser("mc-closeout-report")
    mc_closeout.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    mc_closeout.add_argument("--write", action="store_true")

    mc2_data = sub.add_parser("mc2-data-databanks-resources-options-target")
    mc2_data.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    mc2_data.add_argument("--apply", action="store_true")

    mc2_crosschecks = sub.add_parser("mc2-crosschecks-target")
    mc2_crosschecks.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    mc2_crosschecks.add_argument("--apply", action="store_true")

    mc2_passive = sub.add_parser("mc2-passive-generation-target")
    mc2_passive.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    mc2_passive.add_argument("--apply", action="store_true")

    mc2_static = sub.add_parser("mc2-static-tabs-target")
    mc2_static.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    mc2_static.add_argument("--apply", action="store_true")

    mc2_closeout = sub.add_parser("mc2-closeout-report")
    mc2_closeout.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    mc2_closeout.add_argument("--write", action="store_true")

    sequential_open = sub.add_parser("sequential-open-report")
    sequential_open.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    sequential_open.add_argument("--write", action="store_true")

    sequential_data = sub.add_parser("sequential-data-databanks-resources-options-target")
    sequential_data.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    sequential_data.add_argument("--apply", action="store_true")

    sequential_crosschecks = sub.add_parser("sequential-crosschecks-target")
    sequential_crosschecks.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    sequential_crosschecks.add_argument("--apply", action="store_true")

    sequential_passive = sub.add_parser("sequential-passive-generation-target")
    sequential_passive.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    sequential_passive.add_argument("--apply", action="store_true")

    sequential_static = sub.add_parser("sequential-static-tabs-target")
    sequential_static.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    sequential_static.add_argument("--apply", action="store_true")

    sequential_closeout = sub.add_parser("sequential-closeout-report")
    sequential_closeout.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    sequential_closeout.add_argument("--write", action="store_true")

    monkey_open = sub.add_parser("monkey-open-report")
    monkey_open.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    monkey_open.add_argument("--write", action="store_true")

    monkey_data = sub.add_parser("monkey-data-databanks-resources-options-target")
    monkey_data.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    monkey_data.add_argument("--apply", action="store_true")

    monkey_crosschecks = sub.add_parser("monkey-crosschecks-target")
    monkey_crosschecks.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    monkey_crosschecks.add_argument("--apply", action="store_true")

    monkey_passive = sub.add_parser("monkey-passive-generation-target")
    monkey_passive.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    monkey_passive.add_argument("--apply", action="store_true")

    monkey_static = sub.add_parser("monkey-static-tabs-target")
    monkey_static.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    monkey_static.add_argument("--apply", action="store_true")

    monkey_closeout = sub.add_parser("monkey-closeout-report")
    monkey_closeout.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    monkey_closeout.add_argument("--write", action="store_true")

    synthetic_open = sub.add_parser("synthetic-open-report")
    synthetic_open.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    synthetic_open.add_argument("--write", action="store_true")

    synthetic_data = sub.add_parser("synthetic-data-databanks-resources-options-target")
    synthetic_data.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    synthetic_data.add_argument("--apply", action="store_true")

    synthetic_crosschecks = sub.add_parser("synthetic-crosschecks-target")
    synthetic_crosschecks.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    synthetic_crosschecks.add_argument("--apply", action="store_true")

    synthetic_passive = sub.add_parser("synthetic-passive-generation-target")
    synthetic_passive.add_argument("--target", choices=("local-base", "repo-template", "both"), default="both")
    synthetic_passive.add_argument("--apply", action="store_true")

    archive_exit_days = sub.add_parser("archive-exit-day-snippets")
    archive_exit_days.add_argument("--apply", action="store_true")

    questionnaire = sub.add_parser("questionnaire")
    questionnaire.add_argument("--task-title", required=True)
    questionnaire.add_argument("--tab", required=True)
    questionnaire.add_argument("--max-values", type=int, default=0)
    questionnaire.add_argument("--write", action="store_true")
    questionnaire.add_argument("--full-output", action="store_true")

    task_questionnaires = sub.add_parser("task-questionnaires")
    task_questionnaires.add_argument("--task-title", required=True)
    task_questionnaires.add_argument("--max-values", type=int, default=0)
    task_questionnaires.add_argument("--write", action="store_true")

    answer = sub.add_parser("record-answer")
    answer.add_argument("--task-title", required=True)
    answer.add_argument("--tab", required=True)
    answer.add_argument("--question-id", required=True)
    answer.add_argument("--answer", required=True)
    answer.add_argument("--note", default="")

    tab_answer = sub.add_parser("record-tab-answer")
    tab_answer.add_argument("--task-title", required=True)
    tab_answer.add_argument("--tab", required=True)
    tab_answer.add_argument("--answer", required=True)
    tab_answer.add_argument("--note", default="")
    tab_answer.add_argument("--allow-empty", action="store_true")

    report = sub.add_parser("phase-report")
    report.add_argument("--phase", required=True)
    report.add_argument("--summary", required=True)
    report.add_argument("--next-phase", required=True)
    report.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_root = args.project_root.resolve()
    root142 = args.sqx_root
    if args.command == "status":
        json_print(status(project_root))
        return 0
    if args.command == "preflight":
        json_print(preflight(root142, project_root, apply=args.apply))
        return 0
    if args.command == "phases":
        json_print(list_phases())
        return 0
    if args.command == "promote-views":
        json_print(promote_view_assignments(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "build-genetic-target":
        json_print(promote_build_genetic_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "build-ranking-target":
        json_print(promote_build_ranking_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "build-blocks-target":
        json_print(promote_build_blocks_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "build-indicators-target":
        json_print(promote_build_indicators_target(
            root142,
            project_root,
            target=args.target,
            blocksetting=args.blocksetting,
            timeframe=args.timeframe,
            apply=args.apply,
        ))
        return 0
    if args.command == "build-data-target":
        json_print(promote_build_data_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "build-resources-target":
        json_print(promote_build_resources_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "build-crosschecks-target":
        json_print(promote_build_crosschecks_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "build-static-tabs-target":
        json_print(promote_build_static_tabs_target(root142, project_root, target=args.target))
        return 0
    if args.command == "retest1-data-resources-target":
        json_print(promote_retest1_data_resources_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "retest1-options-databanks-rankings-target":
        json_print(promote_retest1_options_databanks_rankings_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "retest1-passive-generation-target":
        json_print(promote_retest1_passive_generation_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "retest1-static-crosschecks-target":
        json_print(promote_retest1_static_crosschecks_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "tick-real-data-databanks-resources-target":
        json_print(promote_tick_real_data_databanks_resources_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "tick-real-options-rankings-target":
        json_print(promote_tick_real_options_rankings_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "tick-real-passive-generation-target":
        json_print(promote_tick_real_passive_generation_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "tick-real-static-crosschecks-target":
        json_print(promote_tick_real_static_crosschecks_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "mc-data-databanks-resources-options-target":
        json_print(promote_mc_data_databanks_resources_options_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "mc-crosschecks-target":
        json_print(promote_mc_crosschecks_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "mc-passive-generation-target":
        json_print(promote_mc_passive_generation_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "mc-static-tabs-target":
        json_print(promote_mc_static_tabs_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "mc-closeout-report":
        json_print(mc_closeout_report(root142, project_root, target=args.target, write=args.write))
        return 0
    if args.command == "mc2-data-databanks-resources-options-target":
        json_print(promote_mc2_data_databanks_resources_options_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "mc2-crosschecks-target":
        json_print(promote_mc2_crosschecks_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "mc2-passive-generation-target":
        json_print(promote_mc2_passive_generation_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "mc2-static-tabs-target":
        json_print(promote_mc2_static_tabs_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "mc2-closeout-report":
        json_print(mc2_closeout_report(root142, project_root, target=args.target, write=args.write))
        return 0
    if args.command == "sequential-open-report":
        json_print(sequential_open_report(root142, project_root, target=args.target, write=args.write))
        return 0
    if args.command == "sequential-data-databanks-resources-options-target":
        json_print(promote_sequential_data_databanks_resources_options_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "sequential-crosschecks-target":
        json_print(promote_sequential_crosschecks_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "sequential-passive-generation-target":
        json_print(promote_sequential_passive_generation_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "sequential-static-tabs-target":
        json_print(promote_sequential_static_tabs_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "sequential-closeout-report":
        json_print(sequential_closeout_report(root142, project_root, target=args.target, write=args.write))
        return 0
    if args.command == "monkey-open-report":
        json_print(monkey_open_report(root142, project_root, target=args.target, write=args.write))
        return 0
    if args.command == "monkey-data-databanks-resources-options-target":
        json_print(promote_monkey_data_databanks_resources_options_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "monkey-crosschecks-target":
        json_print(promote_monkey_crosschecks_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "monkey-passive-generation-target":
        json_print(promote_monkey_passive_generation_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "monkey-static-tabs-target":
        json_print(promote_monkey_static_tabs_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "monkey-closeout-report":
        json_print(monkey_closeout_report(root142, project_root, target=args.target, write=args.write))
        return 0
    if args.command == "synthetic-open-report":
        json_print(synthetic_open_report(root142, project_root, target=args.target, write=args.write))
        return 0
    if args.command == "synthetic-data-databanks-resources-options-target":
        json_print(promote_synthetic_data_databanks_resources_options_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "synthetic-crosschecks-target":
        json_print(promote_synthetic_crosschecks_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "synthetic-passive-generation-target":
        json_print(promote_synthetic_passive_generation_target(root142, project_root, target=args.target, apply=args.apply))
        return 0
    if args.command == "archive-exit-day-snippets":
        json_print(archive_exit_day_snippets(root142, project_root, apply=args.apply))
        return 0
    if args.command == "questionnaire":
        payload = build_questionnaire(
            root142,
            project_root,
            task_title_wanted=args.task_title,
            tab=args.tab,
            max_values=args.max_values,
            write=args.write,
        )
        if args.write and not args.full_output:
            payload = compact_questionnaire_payload(payload)
        json_print(payload)
        return 0
    if args.command == "task-questionnaires":
        json_print(build_task_questionnaires(
            root142,
            project_root,
            task_title_wanted=args.task_title,
            max_values=args.max_values,
            write=args.write,
        ))
        return 0
    if args.command == "record-answer":
        json_print(record_answer(
            project_root,
            task_title_wanted=args.task_title,
            tab=args.tab,
            question_id=args.question_id,
            answer=args.answer,
            note=args.note,
        ))
        return 0
    if args.command == "record-tab-answer":
        json_print(record_tab_answer(
            project_root,
            task_title_wanted=args.task_title,
            tab=args.tab,
            answer=args.answer,
            note=args.note,
            allow_empty=args.allow_empty,
        ))
        return 0
    if args.command == "phase-report":
        json_print(phase_report(
            project_root,
            phase_id=args.phase,
            summary=args.summary,
            next_phase=args.next_phase,
            write=args.write,
        ))
        return 0
    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
