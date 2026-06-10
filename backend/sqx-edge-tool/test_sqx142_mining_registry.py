import argparse
import zipfile

from tools.sqx142_mining_registry import build_funnel_payload, scan_project_databanks


def _write_sqx(path, name, trades=10, profit=1000, drawdown=250):
    path.parent.mkdir(parents=True, exist_ok=True)
    settings = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<ResultsGroup>'
        '<Fingerprint strategyName="{name}" exact="1" trades="{trades}" '
        'profit="{profit}" drawdown="{drawdown}" fitness="0.1" tradesHash="2" />'
        '</ResultsGroup>'
    ).format(name=name, trades=trades, profit=profit, drawdown=drawdown)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("settings.xml", settings)


def _args(tmp_path, project_dir, db_path):
    return argparse.Namespace(
        action="scan-project",
        db=str(db_path),
        run_key="",
        project_key="Project_AUDCAD_H1_Capa1",
        project_dir=str(project_dir),
        max_sqx_parse=300,
        source_type="sqx_local_project_scan",
        project_name="Project_AUDCAD_H1_Capa1",
        sqx_project_name="Project_AUDCAD_H1_Capa1",
        asset="AUDCAD",
        symbol="AUDCAD_darwinex",
        timeframe="H1",
        layer="Capa1",
        blocksetting_family="BS_Momentum_v6",
        direction="L+S",
        databank="Foward",
        sqx_profile="SQX Edge / Darwinex",
        operator_note="pytest",
    )


def test_scan_project_databanks_records_project_centric_funnel(tmp_path):
    project_dir = tmp_path / "user" / "projects" / "Project_AUDCAD_H1_Capa1"
    for databank, count in {"Results": 3, "SPP": 2, "WFM": 1, "Foward": 1}.items():
        for index in range(count):
            _write_sqx(
                project_dir / "databanks" / databank / f"Strategy {index + 1}.sqx",
                f"Strategy {index + 1}",
                trades=40 + index,
                profit=1000 + index,
                drawdown=200 + index,
            )

    db_path = tmp_path / "registry.sqlite"
    result = scan_project_databanks(_args(tmp_path, project_dir, db_path))
    funnel = build_funnel_payload(db_path, project_key="Project_AUDCAD_H1_Capa1")
    project = funnel["projects"][0]
    databanks = {item["databank"]: item for item in project["databanks"]}

    assert result["ok"] is True
    assert result["guards"]["read_only_sqx_project"] is True
    assert databanks["Results"]["row_count"] == 3
    assert databanks["SPP"]["row_count"] == 2
    assert databanks["WFM"]["row_count"] == 1
    assert databanks["Foward"]["row_count"] == 1
    assert project["edgeFactoryStatePatch"]["capa1Analysis"]["status"] == "recorded"
    assert funnel["privacy"]["local_paths_returned"] is False
