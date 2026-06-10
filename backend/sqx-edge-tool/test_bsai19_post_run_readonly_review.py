from __future__ import annotations

import base64
import json
import struct
import zipfile
from pathlib import Path

import core.bsai19_post_run_readonly_review as bsai19
from core.bsai19_post_run_readonly_review import (
    BS_AI19_POST_RUN_READONLY_REVIEW_VERSION,
    BS_AI19_STATUS,
    review_payload,
)


EXPERIMENT_ID = "BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_repo_config(root: Path, projects_dir: Path) -> None:
    _write_json(
        root / "backend" / "sqx-edge-tool" / "config.json",
        {
            "sqx_projects_dir": str(projects_dir),
            "sqx_path": str(root / "host"),
            "sqx_host_profile": "sqx144_full",
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
            "SRS_ddIS": 777.5,
            "ReturnOpenDDRatio": 1.42,
            "RecoveryFactor": 1.9,
            "StagnationTrades": 35.0,
        }
    )
    return (
        f'<ResultsGroup ResultName="{name}"><ResultsMap><Results>'
        '<Result resultKey="Main: AUDCAD_darwinex/H1" special="false">'
        '<Fitnesses IS="0.62" FS="0.62" />'
        f'<ValuesMap><stats><SQStats version="2" e="b64">{stats}</SQStats></stats></ValuesMap>'
        "</Result></Results></ResultsMap></ResultsGroup>"
    )


def _write_sqx(path: Path, name: str, trades: int, net_profit: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("settings.xml", _settings_xml(name, trades, net_profit))
        archive.writestr("lastSettings.xml", "<Settings />")
        archive.writestr("strategy_Portfolio.xml", "<Strategy />")
        archive.writestr("orders.bin", b"orders")


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
        + _tick_condition("NumberOfTrades", "120")
        + _tick_condition("ProfitFactor", "1.3")
        + _tick_condition("WinningPct", "50")
        + _tick_condition("ReturnDDRatio", "4")
        + (
            '<Condition use="true"><Left-Side valueType="column">'
            '<Column-Value column="NumberOfTrades" name="# of trades" resultType="RetestWithHigherPrecision" pctRatio="0" />'
            '</Left-Side><Comparator value=">=" /><Right-Side valueType="column">'
            '<Column-Value column="NumberOfTrades" name="# of trades" resultType="main" pctRatio="65" />'
            "</Right-Side></Condition>"
        )
        + "</Conditions></Rankings></Task>"
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("config.xml", "<Project />")
        archive.writestr("AutomaticRetest-Task2.xml", tick_xml)


def _write_bsai18_evidence(root: Path) -> None:
    _write_json(
        root / ".local" / "blocksettings_ai" / "monitor_gate" / "bsai18_capa1_monitor_gate_monitor_20260610_192852.json",
        {
            "version": "bs-ai18-capa1-monitor-gate-v1",
            "status": "monitoring_capa1_blocked_review_required_no_capa2",
            "sampleCount": 1,
            "samples": [
                {
                    "remote": {"reachable": False},
                    "databanks": {
                        "items": [
                            {"databank": "Results", "sqxFiles": 10},
                            {"databank": "RETEST 0", "sqxFiles": 3},
                            {"databank": "retest 1", "sqxFiles": 2},
                            {"databank": "TICK", "sqxFiles": 0},
                            {"databank": "Forward", "sqxFiles": 0},
                        ]
                    },
                }
            ],
            "decision": {
                "decision": "monitor_blocked_review_required_no_capa2",
                "cleanTickForwardChainReady": False,
            },
        },
    )


def _fixture(root: Path, *, tick_count: int = 0, forward_count: int = 0) -> Path:
    projects_dir = root / "host" / "user" / "projects"
    _write_repo_config(root, projects_dir)
    project_dir = projects_dir / EXPERIMENT_ID
    _write_project_cfx(project_dir / "project.cfx")
    for index, trades in enumerate((160, 171, 190), start=1):
        filename = f"Strategy {index}.sqx"
        _write_sqx(project_dir / "databanks" / "RETEST 0" / filename, f"Strategy {index}", trades, 1000 + index)
    for index, trades in enumerate((160, 171), start=1):
        filename = f"Strategy {index}.sqx"
        _write_sqx(project_dir / "databanks" / "retest 1" / filename, f"Strategy {index}", trades, 1000 + index)
    for index in range(tick_count):
        _write_sqx(project_dir / "databanks" / "TICK" / f"Strategy {index + 1}.sqx", f"Strategy {index + 1}", 150, 900)
    for index in range(forward_count):
        _write_sqx(project_dir / "databanks" / "Forward" / f"Strategy {index + 1}.sqx", f"Strategy {index + 1}", 140, 800)
    (project_dir / "databanks" / "Results").mkdir(parents=True, exist_ok=True)
    _write_bsai18_evidence(root)
    return root


def test_bsai19_version_marker():
    assert BS_AI19_POST_RUN_READONLY_REVIEW_VERSION == "bs-ai19-post-run-readonly-review-v1"
    assert BS_AI19_STATUS == "post_run_readonly_review_completed_no_capa2"


def test_review_blocks_capa2_with_empty_tick_forward_and_writes_evidence(tmp_path, monkeypatch):
    monkeypatch.setattr(bsai19, "_process_summary", lambda: {"checked": True, "sqxProcessVisible": False, "javaProcessVisible": False})
    payload = review_payload(_fixture(tmp_path), remote_base_url=None, write_evidence=True)
    blob = json.dumps(payload, ensure_ascii=False)

    assert payload["version"] == BS_AI19_POST_RUN_READONLY_REVIEW_VERSION
    assert payload["status"] == BS_AI19_STATUS
    assert payload["decision"]["decision"] == "post_run_review_no_capa2_tick_forward_empty"
    assert payload["decision"]["capa2StartAllowed"] is False
    assert payload["decision"]["projectStartAllowed"] is False
    assert payload["decision"]["projectStopAllowed"] is False
    assert payload["guards"]["readOnly"] is True
    assert payload["guards"]["projectImportRequested"] is False
    assert payload["guards"]["directDataDbPatch"] is False
    assert payload["guards"]["directUserProjectsPatch"] is False
    assert payload["guards"]["directDatabankMutation"] is False
    assert payload["evidenceRef"].startswith("bsai19_post_run_readonly_review_review_")
    assert str(tmp_path) not in blob
    assert "<Task" not in blob
    assert "<Project" not in blob


def test_review_extracts_preregistered_trade_rule_and_survivor_metrics(tmp_path, monkeypatch):
    monkeypatch.setattr(bsai19, "_process_summary", lambda: {"checked": True, "sqxProcessVisible": False, "javaProcessVisible": False})
    payload = review_payload(_fixture(tmp_path), remote_base_url=None)

    assert payload["databankCounts"] == {"Results": 0, "RETEST 0": 3, "retest 1": 2, "TICK": 0, "Forward": 0}
    assert payload["survivorAudit"]["summary"]["survivorCount"] == 2
    assert payload["survivorAudit"]["summary"]["tradeCountMin"] == 160
    assert payload["survivorAudit"]["summary"]["tradeCountMax"] == 171
    assert payload["survivorAudit"]["items"][0]["preRealTickMetrics"]["netProfitIS"] == 1001
    assert {"column": "NumberOfTrades", "comparator": ">=", "value": "120", "resultType": "main"} in payload["tickRealFilters"]["absoluteMainFilters"]
    assert payload["decision"]["tradeRuleObserved"]["retentionFilter"]["rightPctRatio"] == "65"
    assert payload["methodology"]["retest1SurvivorsCanSeedCapa2"] is False


def test_clean_chain_still_requires_manual_gate_and_never_auto_enables_capa2(tmp_path, monkeypatch):
    monkeypatch.setattr(bsai19, "_process_summary", lambda: {"checked": True, "sqxProcessVisible": False, "javaProcessVisible": False})
    payload = review_payload(_fixture(tmp_path, tick_count=1, forward_count=1), remote_base_url=None)

    assert payload["decision"]["cleanTickForwardChainReady"] is True
    assert payload["decision"]["decision"] == "post_run_review_clean_tick_forward_chain_manual_gate_required_no_auto_capa2"
    assert payload["decision"]["capa2StartAllowed"] is False
    assert payload["guards"]["capa2StartAllowed"] is False
