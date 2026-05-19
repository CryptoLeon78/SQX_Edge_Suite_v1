from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

from core.cfx_compatibility import audit_cfx_compatibility, audit_many, render_markdown
from core.plan import Mining
from core.project_generator import generate_project


TOOL_ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = TOOL_ROOT / "templates"


def _write_cfx(path: Path, files: dict[str, str]) -> Path:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, text in files.items():
            archive.writestr(name, text)
    return path


def test_generated_cfx_passes_host_compatibility_audit():
    mining = Mining(num=15, phase=1, asset="USDJPY", tf="H4", bs="BS_Volatilidad", dir="both")
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(generate_project(mining, str(TEMPLATE_DIR / "Capa1_Long.cfx"), tmp, capa=1, sqx_db_path=None))
        report = audit_cfx_compatibility(out_path)

    assert report["version"] == "cfx-compatibility-audit-v1"
    assert report["verdict"] == "pass"
    assert report["hostProfile"] == "sqx142_darwinex"
    assert report["failCount"] == 0


def test_external_sq_equity_profile_is_blocked_for_cross_host_delivery(tmp_path):
    cfx = _write_cfx(
        tmp_path / "external_sq_equity.cfx",
        {
            "config.xml": '<Config name="External Sample" />',
            "Build-Task1.xml": """
            <Task>
              <StrategyType templateFile="C:\\Users\\sample\\Desktop\\legacy.cfx" />
              <Data>
                <Setups>
                  <Setup session="No Session">
                    <Chart symbol="[[Dow Jones Industrial Average]]" timeframe="H1" />
                  </Setup>
                </Setups>
              </Data>
              <BuildTradingOptions>
                <Params>
                  <Param key="MarketOpenSession">No Session</Param>
                </Params>
              </BuildTradingOptions>
              <Resources>
                <Symbols>
                  <Symbol name="[[Dow Jones Industrial Average]]" source="5" precision="D1" timezone="Etc/UCT" broker="-1">
                    <InstrumentInfo instrument="[[Dow Jones Industrial Average]]" dataType="1" broker="-1" />
                  </Symbol>
                </Symbols>
                <Brokers />
                <Sessions />
              </Resources>
            </Task>
            """,
        },
    )

    report = audit_cfx_compatibility(cfx)
    codes = {issue["code"] for issue in report["issues"]}

    assert report["verdict"] == "fail"
    assert report["hostProfile"] == "sq_equity_data_subscription_bound"
    assert "placeholder_symbol" in codes
    assert "sq_equity_data_dependency" in codes
    assert "unbound_broker" in codes
    assert "absolute_strategytype_path" in codes


def test_mixed_symbol_and_session_profile_is_failed(tmp_path):
    cfx = _write_cfx(
        tmp_path / "mixed_profile.cfx",
        {
            "config.xml": '<Config name="Mixed Sample" />',
            "Retest-Task1.xml": """
            <Task>
              <Data>
                <Setups>
                  <Setup session="USDJPY_darwinex">
                    <Chart symbol="USDJPY_dukascopy" timeframe="H4" />
                  </Setup>
                </Setups>
              </Data>
              <BuildTradingOptions>
                <Params>
                  <Param key="MarketOpenSession">USDJPY_darwinex</Param>
                </Params>
              </BuildTradingOptions>
              <Resources>
                <Symbols>
                  <Symbol name="USDJPY_darwinex" source="4" precision="TICK" timezone="EETUS" broker="4">
                    <InstrumentInfo instrument="USDJPY_darwinex" dataType="3" broker="4" />
                  </Symbol>
                </Symbols>
                <Brokers><Broker id="4" name="Darwinex" /></Brokers>
                <Sessions><Session name="USDJPY_darwinex" /></Sessions>
              </Resources>
            </Task>
            """,
        },
    )

    report = audit_cfx_compatibility(cfx)
    codes = {issue["code"] for issue in report["issues"]}

    assert report["verdict"] == "fail"
    assert "chart_missing_resource_symbol" in codes
    assert "stale_market_open_session" in codes
    assert "stale_resource_session" in codes


def test_many_audit_and_markdown_summary(tmp_path):
    ok = _write_cfx(
        tmp_path / "ok.cfx",
        {
            "config.xml": '<Config name="OK" />',
            "Build-Task1.xml": """
            <Task>
              <Data><Setups><Setup session="No Session"><Chart symbol="EURUSD_darwinex" timeframe="H1" /></Setup></Setups></Data>
              <Resources>
                <Symbols><Symbol name="EURUSD_darwinex" source="4" precision="TICK" timezone="EETUS" broker="4"><InstrumentInfo instrument="EURUSD" dataType="3" broker="4" /></Symbol></Symbols>
                <Brokers><Broker id="4" name="Darwinex" /></Brokers>
                <Sessions />
              </Resources>
            </Task>
            """,
        },
    )

    report = audit_many([ok])
    markdown = render_markdown(report)

    assert report["passCount"] == 1
    assert "CFX Compatibility Audit" in markdown
    assert "sqx142_darwinex" in markdown
