from __future__ import annotations

import argparse
import importlib.util
import json
import struct
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "backend" / "sqx-edge-tool" / "tools" / "sqx142_portfolio_corr1_registered_decision.py"
spec = importlib.util.spec_from_file_location("sqx142_portfolio_corr1_registered_decision", TOOL_PATH)
decision = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(decision)


PROJECT_KEY = "SQX_EDGE_API_FRESH_AUDCAD_H1_Momentum_20260528_090029_Capa1"


def java_daily_equity(values: list[tuple[date, float]]) -> bytes:
    payload = bytearray(struct.pack(">i", len(values)))
    for day, value in values:
        timestamp_ms = int(datetime(day.year, day.month, day.day, tzinfo=timezone.utc).timestamp() * 1000)
        payload.extend(struct.pack(">q", timestamp_ms))
        payload.extend(struct.pack(">d", value))
    return b"\xac\xed\x00\x05" + bytes([0x77, len(payload)]) + bytes(payload) if len(payload) < 256 else b"\xac\xed\x00\x05\x7a" + struct.pack(">I", len(payload)) + bytes(payload)


def equity_from_deltas(start: date, deltas: list[float]) -> list[tuple[date, float]]:
    rows = [(start, 0.0)]
    value = 0.0
    ordinal = start.toordinal()
    for index, delta in enumerate(deltas, start=1):
        value += delta
        rows.append((date.fromordinal(ordinal + index), value))
    return rows


def retest_xml(date_from: str, date_to: str, precision: str = "4") -> str:
    return f"""<Task>
  <TradingOptions><Setup dateFrom="{date_from}" dateTo="{date_to}" testPrecision="{precision}" /></TradingOptions>
  <OutOfSample><Range dateFrom="2020.01.16" dateTo="{date_to}" /></OutOfSample>
</Task>"""


def make_project(tmp_path: Path) -> tuple[Path, Path]:
    sqx_root = tmp_path / "SQX"
    project = sqx_root / "user" / "projects" / PROJECT_KEY
    tagged = project / "databanks" / decision.DEFAULT_DATABANK
    tagged.mkdir(parents=True)
    with zipfile.ZipFile(project / "project.cfx", "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("config.xml", f'<Project name="{PROJECT_KEY}"><Tasks /></Project>')
        archive.writestr("Build-Task1.xml", retest_xml("2020.01.01", "2020.01.05", "2"))
        archive.writestr("Retest-Task3.xml", retest_xml("2020.01.01", "2020.01.16", "2"))
        archive.writestr("Retest-Task2.xml", retest_xml("2020.01.16", "2020.01.30", "4"))
    series = {
        "Strategy A": [1, -0.2, 0.8, 0.4, -0.1, 0.9, 0.3, -0.2, 0.7, 0.4, 1, 0.2, -0.1, 0.8, 0.5, 0.2, -0.1, 0.3, 0.4, 0.1],
        "Strategy B": [0.9, -0.1, 0.7, 0.5, -0.1, 0.8, 0.4, -0.1, 0.6, 0.5, 0.9, 0.3, -0.1, 0.7, 0.6, 0.2, -0.1, 0.3, 0.4, 0.1],
        "Strategy C": [-0.2, 0.7, -0.1, 0.6, 0.4, -0.2, 0.7, 0.1, -0.1, 0.6, -0.2, 0.7, 0.1, -0.1, 0.6, 0.3, 0.2, -0.1, 0.2, 0.3],
    }
    for index, (name, deltas) in enumerate(series.items(), start=1):
        with zipfile.ZipFile(tagged / f"{name}.sqx", "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("settings.xml", f'<Root><Fingerprint strategyName="{name}" exact="true" trades="{100 + index}" profit="{1000 + index}" drawdown="100" fitness="{0.5 + index / 10}" tradesHash="h{index}" /></Root>')
            archive.writestr("Results/Main: AUDCAD_darwinex_LOM_H1/dailyEquity.bin", java_daily_equity(equity_from_deltas(date(2020, 1, 1), deltas)))
    return sqx_root, project


def seed_registry(db_path: Path) -> None:
    now = decision.now_iso()
    with decision.registry_connect(db_path) as con:
        con.execute(
            """
            INSERT INTO mining_runs(
                run_key, version, source_type, project_name, sqx_project_name,
                asset, symbol, timeframe, layer, blocksetting_family, direction,
                databank, sqx_profile, source_csv_rows, tagger_csv_rows,
                run_flags_json, data_smoke_json, operator_note, created_at, updated_at
            )
            VALUES(?, ?, 'fixture', ?, ?, 'AUDCAD', 'AUDCAD_darwinex', 'H1', 'Capa1', 'BS_Momentum_v6', 'L+S', ?, 'SQX Edge / Darwinex', 0, 0, '{}', '{}', '', ?, ?)
            """,
            (PROJECT_KEY, decision.VERSION, PROJECT_KEY, PROJECT_KEY, decision.DEFAULT_DATABANK, now, now),
        )
        run_id = int(con.execute("SELECT id FROM mining_runs WHERE run_key = ?", (PROJECT_KEY,)).fetchone()["id"])
        con.execute(
            """
            INSERT INTO custom_projects(
                project_key, run_id, project_name, sqx_project_name, asset, symbol,
                timeframe, layer, blocksetting_family, direction, sqx_profile,
                trace_json, created_at, updated_at
            )
            VALUES(?, ?, ?, ?, 'AUDCAD', 'AUDCAD_darwinex', 'H1', 'Capa1', 'BS_Momentum_v6', 'L+S', 'SQX Edge / Darwinex', ?, ?, ?)
            """,
            (PROJECT_KEY, run_id, PROJECT_KEY, PROJECT_KEY, json.dumps({}), now, now),
        )
        con.commit()


def args_for(tmp_path: Path, sqx_root: Path) -> argparse.Namespace:
    return argparse.Namespace(
        action="analyze",
        sqx_root=str(sqx_root),
        project_key=PROJECT_KEY,
        databank=decision.DEFAULT_DATABANK,
        db=str(tmp_path / "registry.sqlite"),
        max_is_correlation=0.50,
        max_oos3_correlation=0.60,
        warn_oos3_correlation=0.45,
        max_correlation_drift=0.25,
        min_comparable_points=3,
        max_winners=12,
        skip_process_guard=True,
    )


def test_analyze_registered_corr1_decision_records_registry(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    sqx_root, _project = make_project(tmp_path)
    seed_registry(tmp_path / "registry.sqlite")

    result = decision.analyze(args_for(tmp_path, sqx_root))

    assert result["ok"] is True
    assert result["report"]["summary"]["inputRows"] == 3
    assert result["report"]["summary"]["selectedByIs"] >= 1
    assert result["report"]["privacy"]["raw_strategy_names_returned"] is False
    with decision.registry_connect(tmp_path / "registry.sqlite") as con:
        step = con.execute(
            "SELECT status, input_databank, row_count, passed_count FROM custom_project_steps WHERE step_key = 'corr1_registered_stability_decision'"
        ).fetchone()
        snapshot = con.execute(
            "SELECT portfolio_count, similar_count, review_count FROM databank_snapshots WHERE stage_key = 'corr1_registered_decision'"
        ).fetchone()
    assert step["input_databank"] == decision.DEFAULT_DATABANK
    assert step["row_count"] == 3
    assert step["passed_count"] >= 1
    assert snapshot["portfolio_count"] >= 1
