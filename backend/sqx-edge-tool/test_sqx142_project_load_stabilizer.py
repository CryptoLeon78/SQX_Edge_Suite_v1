import sqlite3
import zipfile
from pathlib import Path

from tools.sqx142_project_load_stabilizer import (
    _sha256,
    clear_ui_cache,
    plan,
    rollback,
    stabilize,
)


def _make_data_db(root: Path) -> None:
    data_dir = root / "user" / "data"
    data_dir.mkdir(parents=True)
    con = sqlite3.connect(data_dir / "data.db")
    try:
        con.executescript(
            """
            create table DATA (SYMBOL text);
            create table INSTRUMENTS (INSTRUMENT text);
            create table BROKER (ID integer);
            insert into DATA values ('AUDCAD_darwinex');
            insert into DATA values ('AUDCAD_dukascopy');
            insert into INSTRUMENTS values ('AUDCAD_darwinex');
            insert into BROKER values (4);
            """
        )
        con.commit()
    finally:
        con.close()


def _make_project(root: Path, name: str, broker: str = "4") -> Path:
    project_dir = root / "user" / "projects" / name
    project_dir.mkdir(parents=True)
    cfx = project_dir / "project.cfx"
    with zipfile.ZipFile(cfx, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "config.xml",
            f'<Project name="{name}" version="142.2336"><Tasks /></Project>',
        )
        archive.writestr(
            "Build-Task1.xml",
            f"""
            <Root>
              <Data><Setups><Setup><Chart symbol="AUDCAD_darwinex" /></Setup></Setups></Data>
              <Resources>
                <Symbols>
                  <Symbol name="AUDCAD_darwinex" broker="{broker}">
                    <InstrumentInfo instrument="AUDCAD_darwinex" broker="{broker}" />
                  </Symbol>
                </Symbols>
                <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
              </Resources>
            </Root>
            """,
        )
    return project_dir


def test_plan_detects_stale_zip_temp_file_and_repack_action(tmp_path: Path) -> None:
    _make_data_db(tmp_path)
    project = _make_project(tmp_path, "Mining15_AUDCAD_H1_BS_Momentum_v6_Capa1")
    (project / "zipfstmp123.tmp").write_text("leftover", encoding="utf-8")

    report = plan(tmp_path, ("Mining15_AUDCAD_H1_BS_Momentum_v6_Capa1",))

    actions = report["projects"][0]["actions"]
    assert {"code": "move_stale_zip_temp_file", "file": "zipfstmp123.tmp"} in actions
    assert {"code": "repack_project_cfx"} in actions
    assert "data.db writes" in report["blockedSurfaces"]


def test_plan_flags_broker_reference_that_would_null_in_sqx_resolver(tmp_path: Path) -> None:
    _make_data_db(tmp_path)
    _make_project(tmp_path, "Mining15_AUDCAD_H1_BS_Momentum_v6_Capa1", broker="99")

    report = plan(tmp_path, ("Mining15_AUDCAD_H1_BS_Momentum_v6_Capa1",))

    codes = {finding["code"] for finding in report["projects"][0]["findings"]}
    assert "resource_broker_not_declared_in_cfx_entry" in codes
    assert "resource_broker_missing_from_data_db" in codes
    assert "instrument_broker_missing_from_data_db" in codes


def test_stabilize_moves_temp_files_repackages_and_rollback_restores(tmp_path: Path) -> None:
    _make_data_db(tmp_path)
    project = _make_project(tmp_path, "Mining15_AUDCAD_H1_BS_Momentum_v6_Capa1")
    cfx = project / "project.cfx"
    before_hash = _sha256(cfx)
    temp = project / "zipfstmp123.tmp"
    temp.write_text("leftover", encoding="utf-8")

    result = stabilize(
        tmp_path,
        tmp_path / "repo",
        ("Mining15_AUDCAD_H1_BS_Momentum_v6_Capa1",),
    )

    assert result["ok"] is True
    assert result["projects"][0]["beforeHash"] == before_hash
    assert not temp.exists()
    assert result["projects"][0]["movedTempFiles"]
    assert zipfile.ZipFile(cfx).testzip() is None

    restored = rollback(tmp_path, tmp_path / "repo", result["backupId"])

    assert restored["ok"] is True
    assert temp.exists()
    assert _sha256(cfx) == before_hash


def test_clear_ui_cache_moves_only_electron_http_cache_to_local_backup(tmp_path: Path) -> None:
    cache_file = (
        tmp_path
        / "sqx"
        / "internal"
        / "electron"
        / "resources"
        / "userData"
        / "SQUANT"
        / "Cache"
        / "Cache_Data"
        / "data_1"
    )
    cache_file.parent.mkdir(parents=True)
    cache_file.write_text(
        "http://localhost:8080/project/checkResources?projectName=Mining15_AUDCAD",
        encoding="utf-8",
    )
    data_db = tmp_path / "sqx" / "user" / "data" / "data.db"
    data_db.parent.mkdir(parents=True)
    data_db.write_text("must stay untouched", encoding="utf-8")

    result = clear_ui_cache(tmp_path / "sqx", tmp_path / "repo")

    assert result["ok"] is True
    assert result["action"] == "clear-ui-cache"
    assert result["movedHttpCache"] is True
    assert not cache_file.exists()
    backup_cache = Path(result["backupCacheDir"])
    assert (backup_cache / "Cache_Data" / "data_1").exists()
    assert data_db.read_text(encoding="utf-8") == "must stay untouched"
    assert "data.db writes" in result["blockedSurfaces"]


def test_wrapper_blocks_mutation_without_stop_process() -> None:
    wrapper = Path("tools/sqx142_project_load_stabilizer.ps1").read_text(encoding="utf-8")
    assert "Stop-Process" not in wrapper
    assert "SQX must be closed before $Action" in wrapper
    assert "jars" not in wrapper.lower()
    assert '"clear-ui-cache"' in wrapper
