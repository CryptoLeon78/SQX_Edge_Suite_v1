import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "backend" / "sqx-edge-tool" / "tools" / "sqx142_correlation_data_smoke.py"
spec = importlib.util.spec_from_file_location("sqx142_correlation_data_smoke", TOOL_PATH)
data_smoke = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(data_smoke)


def test_correlation_data_smoke_builds_private_tag_csv(tmp_path):
    input_csv = tmp_path / "rows.csv"
    input_csv.write_text(
        "\n".join([
            "strategy,asset,timeframe,Source Phase,Source Databank,Forward Status,Profit Factor,Ret/DD Ratio,Max DD %,Number of trades,Stability,SQN,BlockSetting,indicator,returnSeries",
            "PRIVATE_A,AUDCAD,H4,phase28_capa2_forward,Foward,PASSED,1.55,4.2,18,140,0.72,2.1,BS_Custom,MACD,0.01|0.02|0.015|0.03|-0.01|0.02|0.01|0.025|0.03|-0.005|0.012|0.02",
            "PRIVATE_B,AUDCAD,H4,phase28_capa2_forward,Foward,PASSED,1.25,3.0,20,120,0.62,1.7,BS_Custom,MACD,0.02|0.04|0.03|0.06|-0.02|0.04|0.02|0.05|0.06|-0.01|0.024|0.04",
        ]),
        encoding="utf-8",
    )

    result = data_smoke.build_smoke_artifacts(input_csv, tmp_path / "out")
    tag_csv = Path(result["outputs"]["tagCsvPath"]).read_text(encoding="utf-8")
    evidence = json.loads(Path(result["outputs"]["evidencePath"]).read_text(encoding="utf-8"))
    rows = list(csv.DictReader(tag_csv.splitlines()))

    assert result["version"] == data_smoke.DATA_SMOKE_VERSION
    assert evidence["privacy"]["raw_strategy_names_returned"] is False
    assert rows
    assert set(rows[0]) == set(data_smoke.TAG_SCHEMA)
    assert all(row["strategyRef"].startswith("strategy_") for row in rows)
    assert "PRIVATE_A" not in tag_csv
    assert "PRIVATE_B" not in tag_csv
    assert evidence["tagCsv"]["rows"] == 2
    assert evidence["guards"]["tag_csv_only"] is True


def test_correlation_data_smoke_accepts_sqx_semicolon_databank_export(tmp_path):
    input_csv = tmp_path / "DatabankExport.csv"
    input_csv.write_text(
        "\n".join([
            '"Strategy Name";"Filters result";"Symbol";"TimeFrame";"# of trades";"Max DD %";"Ret/DD Ratio";"Profit factor";"Sharpe Ratio";"Entry indicators"',
            '"Strategy 1.1.50(1)";"PASSED";"USDJPY_darwinex";"H4";"633";"10.24";"3.75";"1.3";"0.8";"CloseM,Open"',
            '"Strategy 1.10.30(1)";"PASSED";"USDJPY_darwinex";"H4";"459";"11.69";"2.17";"1.21";"0.48";"KeltnerChannel,Open"',
        ]),
        encoding="utf-8",
    )

    result = data_smoke.build_smoke_artifacts(input_csv, tmp_path / "out")
    tag_csv = Path(result["outputs"]["tagCsvPath"]).read_text(encoding="utf-8")
    rows = list(csv.DictReader(tag_csv.splitlines()))

    assert len(rows) == 2
    assert all(row["strategyRef"].startswith("strategy_") for row in rows)
    assert "Strategy 1.1.50" not in tag_csv
    assert result["summary"]["inputRows"] == 2
    assert result["summary"]["eligibleRows"] == 2
    assert result["decisions"]["portfolio"] >= 1
