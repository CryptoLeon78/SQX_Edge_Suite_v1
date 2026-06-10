import importlib.util
import json
import zipfile
from argparse import Namespace
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = PROJECT_ROOT / "backend" / "sqx-edge-tool" / "tools" / "sqx142_correlation_lab_project_scaffold.py"

spec = importlib.util.spec_from_file_location("sqx142_correlation_lab_project_scaffold", TOOL_PATH)
lab_scaffold = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab_scaffold)


def _write_project_cfx(project_dir: Path, project_name: str) -> None:
    config_xml = f"""<Project name="{project_name}" version="141.2225">
  <Tasks>
    <Task type="Retest" name="Retest strategies 2" showSettingsOverview="false" sampleName="Custom" active="true" taskXMLFile="Retest-Task2.xml" title="FOWARD" />
  </Tasks>
  <Databanks>
    <Databank name="Monkey Test" view="MC MONKEY RETEST" syncType="Auto-sync every 10 minutes" position="1300" />
    <Databank name="Syntetic" view="MC SYNTHETIC RETEST" syncType="Auto-sync every 10 minutes" position="1400" />
    <Databank name="Foward" view="RETEST QUICK REVIEW" syncType="Auto-sync every 10 minutes" position="1700" />
  </Databanks>
</Project>"""
    retest_xml = """<Settings>
  <Databanks>
    <Databank label="Output databank" name="Output" value="Foward" />
    <Databank label="Input databank" name="Input" value="WFM" />
  </Databanks>
  <Rankings type="never">
    <FitPortfolio active="true" databank="Existing portfolio">
      <Correlation max="0.3" type="ProfitLoss" period="30" allowNegative="true" addEmptyPeriods="true" />
    </FitPortfolio>
    <CustomAnalysis method="none" filter="false" inputArgs="" />
  </Rankings>
  <CrossChecks use="true" evaluateAll="true">
    <RetestOnAdditionalMarkets use="false" />
  </CrossChecks>
</Settings>"""
    with zipfile.ZipFile(project_dir / "project.cfx", "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("config.xml", config_xml)
        archive.writestr("Retest-Task2.xml", retest_xml)


def _make_donor(tmp_path: Path, retired_dependency: bool = False) -> Path:
    donor = tmp_path / "SQX" / "user" / "projects" / "DonorProject"
    (donor / "databanks" / "Monkey Test").mkdir(parents=True)
    (donor / "databanks" / "Syntetic").mkdir(parents=True)
    strategy_text = "mock ExitAfterDays" if retired_dependency else "mock"
    (donor / "databanks" / "Monkey Test" / "Strategy 1.sqx").write_text(strategy_text, encoding="utf-8")
    (donor / "databanks" / "Syntetic" / "Strategy 1(1).sqx").write_text("mock", encoding="utf-8")
    _write_project_cfx(donor, "DonorProject")
    return donor


def test_installs_correlation_lab_project_and_patches_tag_task(tmp_path, monkeypatch):
    _make_donor(tmp_path)
    monkeypatch.setattr(lab_scaffold, "_local_root", lambda: tmp_path / ".local")
    args = Namespace(
        sqx_root=str(tmp_path / "SQX"),
        donor_project="DonorProject",
        target_project="SQX_EDGE_CORR_LAB_TEST",
        backup_id="",
    )

    result = lab_scaffold.install(args)
    target = tmp_path / "SQX" / "user" / "projects" / "SQX_EDGE_CORR_LAB_TEST"

    assert result["ok"] is True
    assert target.is_dir()
    assert (target / "databanks" / "Monkey Test" / "Strategy 1.sqx").is_file()
    assert (target / "databanks" / "Syntetic" / "Strategy 1(1).sqx").is_file()
    assert (target / "databanks" / "SQX EDGE CORR TAGGED").is_dir()

    inspected = lab_scaffold._inspect_project_cfx(target / "project.cfx")
    assert inspected["projectName"] == "SQX_EDGE_CORR_LAB_TEST"
    assert inspected["databankViews"]["Monkey Test"] == "SQX EDGE CORRELATION REVIEW"
    assert inspected["databankViews"]["Syntetic"] == "SQX EDGE CORRELATION REVIEW"
    assert inspected["databankViews"]["SQX EDGE CORR TAGGED"] == "SQX EDGE CORRELATION REVIEW"
    assert inspected["tagTask"]["title"] == "SQX EDGE CORR TAG"
    assert inspected["tagTask"]["active"] == "false"
    assert inspected["tagTaskInput"] == "Monkey Test"
    assert inspected["tagTaskOutput"] == "SQX EDGE CORR TAGGED"
    assert inspected["customAnalysis"] == "SQXEdgeCorrelationTagger"
    assert result["retiredDependencyPreflight"]["ok"] is True


def test_blocks_install_when_donor_databank_uses_retired_exit_snippet(tmp_path, monkeypatch):
    _make_donor(tmp_path, retired_dependency=True)
    monkeypatch.setattr(lab_scaffold, "_local_root", lambda: tmp_path / ".local")
    args = Namespace(
        sqx_root=str(tmp_path / "SQX"),
        donor_project="DonorProject",
        target_project="SQX_EDGE_CORR_LAB_TEST",
        backup_id="",
    )

    status = lab_scaffold.build_status(args)
    preflight = status["retiredDependencyPreflight"]["donor"]
    assert preflight["blocked"] is True
    assert preflight["affectedStrategyCount"] == 1
    assert preflight["databanks"][0]["tokens"]["ExitAfterDays"] == 1

    try:
        lab_scaffold.install(args)
    except ValueError as exc:
        assert "retired strategy dependencies" in str(exc)
    else:
        raise AssertionError("install should block retired strategy dependencies")


def test_rolls_back_lab_project_by_moving_to_quarantine(tmp_path, monkeypatch):
    _make_donor(tmp_path)
    monkeypatch.setattr(lab_scaffold, "_local_root", lambda: tmp_path / ".local")
    args = Namespace(
        sqx_root=str(tmp_path / "SQX"),
        donor_project="DonorProject",
        target_project="SQX_EDGE_CORR_LAB_TEST",
        backup_id="",
    )
    install_result = lab_scaffold.install(args)

    rollback_args = Namespace(
        sqx_root=str(tmp_path / "SQX"),
        donor_project="DonorProject",
        target_project="SQX_EDGE_CORR_LAB_TEST",
        backup_id=install_result["backupId"],
    )
    rollback_result = lab_scaffold.rollback(rollback_args)

    assert rollback_result["result"] == "moved_to_quarantine"
    assert rollback_result["targetExistsAfterRollback"] is False
    quarantine = (
        tmp_path
        / "SQX"
        / "user"
        / "projects_quarantine"
        / "SQXEdge"
        / install_result["backupId"]
        / "SQX_EDGE_CORR_LAB_TEST"
    )
    assert (quarantine / "project.cfx").is_file()
    manifest = tmp_path / ".local" / "backups" / install_result["backupId"] / "rollback_manifest.json"
    assert json.loads(manifest.read_text(encoding="utf-8"))["targetProject"] == "SQX_EDGE_CORR_LAB_TEST"
