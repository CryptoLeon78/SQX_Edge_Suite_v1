from __future__ import annotations

import base64
import json
import struct
import zipfile
from pathlib import Path

from core.bsai15_tick_real_diagnostic import (
    BS_AI15_STATUS,
    BS_AI15_TICK_REAL_DIAGNOSTIC_VERSION,
    audit_payload,
)


CANDIDATE_ID = "BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005"
PROJECT_ROOT_STEM = f"BSAI_AUDCAD_H1_{CANDIDATE_ID}_L_SQX144DARWINEX"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_repo_config(root: Path, projects_dir: Path) -> None:
    _write_json(
        root / "backend" / "sqx-edge-tool" / "config.json",
        {
            "sqx_projects_dir": str(projects_dir),
            "sqx_host_profile": "sqx144_full",
        },
    )


def _write_candidate(root: Path) -> None:
    _write_json(
        root / ".local" / "blocksettings_ai" / "candidates" / f"{CANDIDATE_ID}.json",
        {
            "entry": {
                "canonicalId": CANDIDATE_ID,
                "baseCanonicalId": "BS_Filtros_v7_H1",
                "promotionState": "local_candidate",
                "localPath": str(root / "must_not_leak.sqb"),
            },
            "recipe": {
                "asset": "AUDCAD",
                "timeframe": "H1",
                "direction": "long",
                "candidateLayer": 2,
                "baseCanonicalId": "BS_Filtros_v7_H1",
            },
        },
    )


def _sqstats_blob(values: dict[str, int | float]) -> str:
    data = bytearray()
    for name, value in values.items():
        raw_name = name.encode("ascii")
        if isinstance(value, int):
            data.append(ord("e"))
            data.extend(len(raw_name).to_bytes(2, "big"))
            data.extend(raw_name)
            data.extend(int(value).to_bytes(4, "big", signed=True))
        else:
            data.append(ord("g"))
            data.extend(len(raw_name).to_bytes(2, "big"))
            data.extend(raw_name)
            data.extend(struct.pack(">f", float(value)))
    return base64.b64encode(bytes(data)).decode("ascii")


def _settings_xml(name: str, trades: int, net_profit: float) -> str:
    stats = _sqstats_blob(
        {
            "SampleType_11_Count": trades,
            "Raw_TotalOrders": trades,
            "NetProfitIS": net_profit,
            "SRS_ddIS": 1200.5,
            "MaxTSIntradayDrawdown": -400.25,
            "AvgDrawdown": 111.25,
            "ReturnOpenDDRatio": 1.25,
            "RecoveryFactor": 1.4,
            "StagnationTrades": 44.0,
            "DDHealthScore": 72.5,
        }
    )
    return (
        f'<ResultsGroup ResultName="{name}"><ResultsMap><Results>'
        '<Result resultKey="Main: AUDCAD_dukascopy/H1" special="false">'
        '<Fitnesses IS="0.52" FS="0.52" />'
        f'<ValuesMap><stats><SQStats version="2" e="b64">{stats}</SQStats></stats></ValuesMap>'
        "</Result></Results></ResultsMap></ResultsGroup>"
    )


def _write_sqx(path: Path, name: str, trades: int, net_profit: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("settings.xml", _settings_xml(name, trades, net_profit))
        archive.writestr("lastSettings.xml", '<Settings><MarketSides type="long" /></Settings>')
        archive.writestr("strategy_Portfolio.xml", "<Strategy />")
        archive.writestr("orders.bin", b"orders")
        archive.writestr("Results/Main: AUDCAD_dukascopy_LOM_H1/dailyEquity.bin", b"equity")


def _tick_condition(column: str, value: str, comparator: str = ">=") -> str:
    return (
        '<Condition use="true"><Left-Side valueType="column">'
        f'<Column-Value column="{column}" resultType="main" pctRatio="0" />'
        f'</Left-Side><Comparator value="{comparator}" />'
        f'<Right-Side valueType="numeric"><Numeric-Value value="{value}" /></Right-Side></Condition>'
    )


def _write_project_cfx(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tick_xml = (
        "<Task><Rankings><Conditions>"
        + _tick_condition("NumberOfTrades", "200")
        + _tick_condition("ProfitFactor", "1.3")
        + _tick_condition("WinningPct", "50")
        + _tick_condition("ReturnDDRatio", "4")
        + (
            '<Condition use="true"><Left-Side valueType="column">'
            '<Column-Value column="NumberOfTrades" name="# of trades" resultType="RetestWithHigherPrecision" pctRatio="0" />'
            '</Left-Side><Comparator value=">=" /><Right-Side valueType="column">'
            '<Column-Value column="NumberOfTrades" name="# of trades" resultType="main" pctRatio="80" />'
            "</Right-Side></Condition>"
        )
        + "</Conditions></Rankings></Task>"
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("config.xml", "<Project />")
        archive.writestr("AutomaticRetest-Task2.xml", tick_xml)


def _fixture(root: Path) -> Path:
    projects_dir = root / "host" / "user" / "projects"
    _write_repo_config(root, projects_dir)
    _write_candidate(root)
    project_name = f"{PROJECT_ROOT_STEM}_Capa1"
    project_dir = projects_dir / project_name
    _write_project_cfx(project_dir / "project.cfx")
    for index, trades in enumerate((300, 302, 311, 305, 301), start=1):
        filename = f"Strategy {index}.sqx"
        _write_sqx(project_dir / "databanks" / "RETEST 0" / filename, f"Strategy {index}", trades, 1000 + index)
        _write_sqx(project_dir / "databanks" / "retest 1" / filename, f"Strategy {index}", trades, 1000 + index)
    (project_dir / "databanks" / "TICK").mkdir(parents=True, exist_ok=True)
    (projects_dir / f"{PROJECT_ROOT_STEM}_Capa2" / "databanks").mkdir(parents=True, exist_ok=True)
    return root


def test_bsai15_version_marker():
    assert BS_AI15_TICK_REAL_DIAGNOSTIC_VERSION == "bs-ai15-tick-real-diagnostic-v1"
    assert BS_AI15_STATUS == "diagnostic_plan_ready_no_capa2_no_filter_relaxation"


def test_audit_extracts_survivor_metrics_without_paths_or_xml(tmp_path):
    payload = audit_payload(_fixture(tmp_path), remote_base_url=None, write_evidence=True)
    blob = json.dumps(payload, ensure_ascii=False)

    assert payload["version"] == BS_AI15_TICK_REAL_DIAGNOSTIC_VERSION
    assert payload["status"] == BS_AI15_STATUS
    assert payload["ok"] is True
    assert payload["databankCounts"] == {"RETEST 0": 5, "retest 1": 5, "TICK": 0}
    assert payload["survivorAudit"]["summary"]["survivorCount"] == 5
    assert payload["survivorAudit"]["summary"]["tradeCountMin"] == 300
    assert payload["survivorAudit"]["summary"]["tradeCountMax"] == 311
    assert payload["survivorAudit"]["items"][0]["preRealTickMetrics"]["tradeCountObserved"] == 300
    assert payload["survivorAudit"]["items"][0]["preRealTickMetrics"]["profitFactor"] is None
    assert payload["survivorAudit"]["items"][0]["afterRealTickMetrics"]["metricsAvailable"] is False
    assert payload["evidenceRef"].startswith("bsai15_tick_real_diagnostic_audit_")
    assert str(tmp_path) not in blob
    assert "<Task" not in blob
    assert "<Project" not in blob
    assert "must_not_leak" not in blob


def test_audit_keeps_current_lot_frozen_and_capa2_blocked(tmp_path):
    payload = audit_payload(_fixture(tmp_path), remote_base_url=None)

    assert payload["frozenLot"]["decision"] == "tick_real_pf_failed_trade_threshold_warning_no_capa2"
    assert payload["frozenLot"]["rescueByRelaxingFiltersAllowed"] is False
    assert payload["guards"]["readOnly"] is True
    assert payload["guards"]["projectStartRequested"] is False
    assert payload["guards"]["projectStopRequested"] is False
    assert payload["guards"]["capa2StartAllowed"] is False
    assert payload["guards"]["filterRelaxationAllowedForCurrentLot"] is False
    assert payload["guards"]["writesDataDb"] is False
    assert payload["guards"]["writesUserProjects"] is False
    assert payload["guards"]["mutatesDatabanks"] is False
    assert payload["nextExperiment"]["capa2StartAllowed"] is False


def test_audit_reports_absolute_and_relative_tick_trade_rules(tmp_path):
    payload = audit_payload(_fixture(tmp_path), remote_base_url=None)

    filters = payload["tickRealFilters"]
    assert filters["extractionStatus"] == "ok"
    assert {"column": "NumberOfTrades", "comparator": ">=", "value": "200", "resultType": "main"} in filters["absoluteMainFilters"]
    assert filters["relativePrecisionFilters"][0]["column"] == "NumberOfTrades"
    assert filters["relativePrecisionFilters"][0]["rightPctRatio"] == "80"
    assert payload["tradeRuleRedesign"]["recommendedRuleShape"] == "realTickTrades >= max(absoluteFloor, floor(priorValidationTrades * retentionRatio))"
    assert payload["tradeRuleRedesign"]["recommendedPolicyForNextExperiment"]["preRegisterRuleBeforeRun"] is True
    assert payload["tradeRuleRedesign"]["recommendedPolicyForNextExperiment"]["useCurrentLotToRescue"] is False
