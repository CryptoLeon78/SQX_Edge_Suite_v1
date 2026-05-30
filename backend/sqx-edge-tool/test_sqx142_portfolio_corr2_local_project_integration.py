from __future__ import annotations

import argparse
import importlib.util
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "backend" / "sqx-edge-tool" / "tools" / "sqx142_portfolio_corr2_local_project_integration.py"
spec = importlib.util.spec_from_file_location("sqx142_portfolio_corr2_local_project_integration", TOOL_PATH)
corr2 = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(corr2)


CONFIG_XML = """<Project name="Project_AUDCAD_H1_Capa1" version="141.2225">
  <Tasks>
    <Task type="Build" name="Build strategies" showSettingsOverview="false" sampleName="Custom" active="true" taskXMLFile="Build-Task1.xml" title="Build BS_Momentum_v6 · Capa1 L+S H1" />
    <Task type="Retest" name="Retest strategies 0" showSettingsOverview="false" sampleName="Custom" active="true" taskXMLFile="Retest-Task3.xml" title="RETEST 0" />
    <Task type="Retest" name="Retest strategies 2" showSettingsOverview="false" sampleName="Custom" active="true" taskXMLFile="Retest-Task2.xml" title="FORWARD" />
  </Tasks>
  <Databanks>
    <Databank name="Results" view="Default - Main data" syncType="Auto-sync" position="0" />
    <Databank name="Forward" view="SQX EDGE CORRELATION REVIEW" syncType="Auto-sync never" position="1700" />
  </Databanks>
</Project>"""


def retest_xml(input_db: str, output_db: str, date_from: str, date_to: str, precision: str = "2") -> str:
    return f"""<Task>
  <TradingOptions><Setup dateFrom="{date_from}" dateTo="{date_to}" testPrecision="{precision}" session="No Session" slippage="0" minDist="0" engine="MetaTrader5 (hedged)" /></TradingOptions>
  <OutOfSample showGraph="false"><Range dateFrom="2025.01.01" dateTo="{date_to}" /></OutOfSample>
  <Rankings type="top"><MaxStrategies>10000</MaxStrategies><DeleteFailedStrategies>true</DeleteFailedStrategies><ForceRunCrossChecks>true</ForceRunCrossChecks><StopCondition type="databank-full" passedStrategies="1000" restartCount="5" days="0" hours="0" minutes="0" /><FitPortfolio active="true" databank="Existing portfolio" /><CustomAnalysis method="old" filter="true" inputArgs="x" /></Rankings>
  <CrossChecks use="true" evaluateAll="true" />
  <Databanks retestSelected="false"><Databank label="Output databank" name="Output" value="{output_db}" /><Databank label="Input databank" name="Input" value="{input_db}" /></Databanks>
</Task>"""


def build_xml() -> str:
    return """<Task>
  <TradingOptions><Setup dateFrom="2017.10.02" dateTo="2023.01.01" testPrecision="2" session="No Session" /></TradingOptions>
  <OutOfSample showGraph="false" />
</Task>"""


def make_project(tmp_path: Path) -> tuple[Path, Path]:
    sqx_root = tmp_path / "SQX"
    project_key = "SQX_EDGE_API_FRESH_AUDCAD_H1_Momentum_20260528_090029_Capa1"
    project = sqx_root / "user" / "projects" / project_key
    (project / "databanks" / "Results").mkdir(parents=True)
    (project / "databanks" / "Forward").mkdir(parents=True)
    for index in range(3):
        (project / "databanks" / "Results" / f"Strategy {index}.sqx").write_bytes(b"fixture")
    with zipfile.ZipFile(project / "project.cfx", "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("config.xml", CONFIG_XML)
        archive.writestr("Build-Task1.xml", build_xml())
        archive.writestr("Retest-Task3.xml", retest_xml("Results", "RETEST 0", "2017.10.02", "2025.01.01"))
        archive.writestr("Retest-Task2.xml", retest_xml("WFM", "Forward", "2025.01.01", "2026.04.08", "4"))
    return sqx_root, project


def args_for(tmp_path: Path, sqx_root: Path, backup_id: str = "") -> argparse.Namespace:
    return argparse.Namespace(
        action="apply",
        sqx_root=str(sqx_root),
        project_key="SQX_EDGE_API_FRESH_AUDCAD_H1_Momentum_20260528_090029_Capa1",
        db=str(tmp_path / "registry.sqlite"),
        backup_id=backup_id,
        skip_process_guard=True,
    )


def test_apply_adds_corr2_tasks_databanks_and_registry_steps(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    sqx_root, project = make_project(tmp_path)

    result = corr2.apply_integration(args_for(tmp_path, sqx_root))

    assert result["ok"] is True
    assert result["status"] == "patched"
    assert result["backupId"].startswith(corr2.VERSION)
    assert result["databanks"][corr2.STABILITY_DATABANK] == 0
    assert (project / "databanks" / corr2.STABILITY_DATABANK).is_dir()
    assert (project / "databanks" / corr2.TAGGED_DATABANK).is_dir()

    with zipfile.ZipFile(project / "project.cfx") as archive:
        names = set(archive.namelist())
        assert corr2.STABILITY_TASK_XML in names
        assert corr2.TAG_TASK_XML in names
        config = ET.fromstring(archive.read("config.xml").decode("utf-8"))
        task_titles = {task.attrib["taskXMLFile"]: task.attrib["title"] for task in config.findall(".//Task")}
        task_active = {task.attrib["taskXMLFile"]: task.attrib["active"] for task in config.findall(".//Task")}
        assert task_titles[corr2.STABILITY_TASK_XML] == corr2.STABILITY_TASK_TITLE
        assert task_titles[corr2.TAG_TASK_XML] == corr2.TAG_TASK_TITLE
        assert task_active[corr2.STABILITY_TASK_XML] == "true"
        assert task_active[corr2.TAG_TASK_XML] == "true"
        databank_names = {item.attrib["name"]: item.attrib.get("view") for item in config.findall(".//Databank")}
        assert databank_names[corr2.STABILITY_DATABANK] == corr2.VIEW_NAME
        stability = ET.fromstring(archive.read(corr2.STABILITY_TASK_XML).decode("utf-8"))
        tag = ET.fromstring(archive.read(corr2.TAG_TASK_XML).decode("utf-8"))

    stability_setup = stability.find(".//Setup")
    assert stability_setup.attrib["dateFrom"] == "2017.10.02"
    assert stability_setup.attrib["dateTo"] == "2026.04.08"
    assert stability_setup.attrib["testPrecision"] == "4"
    assert stability.find(".//CustomAnalysis").attrib["method"] == "none"
    assert stability.find(".//DeleteFailedStrategies").text == "false"
    assert stability.find(".//CrossChecks").attrib["use"] == "false"
    assert corr2.retest_task_databanks(ET.tostring(stability, encoding="unicode"))["input"] == "Forward"
    assert tag.find(".//CustomAnalysis").attrib["method"] == corr2.CUSTOM_ANALYSIS_ID

    status = corr2.build_status(args_for(tmp_path, sqx_root))
    assert status["cfx"]["corr2Integrated"] is True
    assert status["actual"]["sourceDatabank"] == "Forward"
    assert status["databanks"][corr2.STABILITY_DATABANK] == 0


def test_record_manual_status_updates_completed_corr2_registry_steps(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    sqx_root, project = make_project(tmp_path)
    corr2.apply_integration(args_for(tmp_path, sqx_root))
    for index in range(2):
        (project / "databanks" / corr2.STABILITY_DATABANK / f"Stable {index}.sqx").write_bytes(b"fixture")
        (project / "databanks" / corr2.TAGGED_DATABANK / f"Tagged {index}.sqx").write_bytes(b"fixture")

    recorded = corr2.record_manual_status(args_for(tmp_path, sqx_root))

    assert recorded["ok"] is True
    assert recorded["actual"]["sourceDatabank"] == "Forward"
    with corr2.registry_connect(Path(args_for(tmp_path, sqx_root).db)) as con:
        rows = con.execute(
            "SELECT step_key, status, input_databank, output_databank, passed_count FROM custom_project_steps ORDER BY step_order"
        ).fetchall()
    by_key = {row["step_key"]: dict(row) for row in rows}
    assert by_key["corr2_stability_retest"]["status"] == "completed"
    assert by_key["corr2_stability_retest"]["input_databank"] == "Forward"
    assert by_key["corr2_stability_retest"]["passed_count"] == 2
    assert by_key["corr2_tagger_review"]["status"] == "completed"
    assert by_key["corr2_tagger_review"]["passed_count"] == 2


def test_rollback_restores_backed_up_project_cfx(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    sqx_root, project = make_project(tmp_path)
    applied = corr2.apply_integration(args_for(tmp_path, sqx_root))

    rolled = corr2.rollback_integration(args_for(tmp_path, sqx_root, applied["backupId"]))

    assert rolled["ok"] is True
    assert rolled["status"] == "rolled_back"
    with zipfile.ZipFile(project / "project.cfx") as archive:
        names = set(archive.namelist())
    assert corr2.STABILITY_TASK_XML not in names
    assert corr2.TAG_TASK_XML not in names
    assert rolled["databankFoldersLeftInPlace"] is True
