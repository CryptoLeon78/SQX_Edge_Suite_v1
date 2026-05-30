import sqlite3
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from tools.sqx142_project_resource_repair import (
    _patch_absolute_strategy_type_paths,
    _patch_base_project_date_caps,
    _patch_base_strategy_type_improve_databank,
    _patch_backup_strategy_symbols_to_chart,
    _patch_config,
    _patch_config_for_clean_load,
    _patch_cross_broker_to_local_loadable,
    _patch_donor_symbol_family,
    _patch_resources_to_data_db,
    _prune_unused_resource_brokers,
    _resource_from_db,
    _java_double_text,
    _rewrite_project_name,
    repair_capa2_clean_config,
    rebuild_capa2_from_clean_donor,
    rebuild_capa1_from_clean_donor,
    rollback,
)


def _make_project_cfx(path: Path, project_name: str, marker: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "config.xml",
            f'<Project name="{project_name}"><Tasks><Task taskXMLFile="Build-Task1.xml" /></Tasks></Project>',
        )
        archive.writestr("Build-Task1.xml", f"<Root><Marker>{marker}</Marker></Root>")


def test_formats_small_floats_like_sqx_java_double_strings() -> None:
    assert _java_double_text(0.0001) == "1.0E-4"
    assert _java_double_text(0.00001) == "1.0E-5"
    assert _java_double_text(2.0) == "2.0"


def _make_sqx_data_db(root: Path) -> None:
    data_dir = root / "user" / "data"
    data_dir.mkdir(parents=True)
    con = sqlite3.connect(data_dir / "data.db")
    try:
        con.executescript(
            """
            create table DATA (
              ID integer, SYMBOL text, INSTRUMENT text, TIMEFRAME text, TIMEZONE text,
              DATEFROM integer, DATETO integer, DATATYPE integer, ROWS integer,
              DECIMALS integer, SOURCE integer, USYMBOL text, USYMBOLNAME text,
              BROKER_ID integer
            );
            create table INSTRUMENTS (
              INSTRUMENT text, DESCRIPTION text, POINTVALUE real, TICKSIZE real,
              TICKSTEP real, DEFAULTSPREAD real, COMMISSIONS text, DATATYPE integer,
              EXCHANGE text, COUNTRY text, SECTOR text, DEFAULTSLIPPAGE real,
              SWAP text, ORDERSIZEMULTIPLIER real, ORDERSIZESTEP real,
              BROKER_ID integer, MIN_DISTANCE real
            );
            create table BROKER (
              ID integer, NAME text, DESC text, MT_TIMEZONE text, POSTFIX text
            );
            """
        )
        con.execute(
            "insert into BROKER values (4, '[[Darwinex]]', 'Darwinex CFDs', 'EETUS', '_darwinex')"
        )
        con.execute(
            """
            insert into DATA values
            (1, 'AUDCAD_dukascopy', 'AUDCAD_darwinex', 'TICK', 'EETUS',
             1262311415817, 1778889597600, 1, 1000, 5, 2, 'AUDCAD', 'AUDCAD', 4)
            """
        )
        con.execute(
            """
            insert into DATA values
            (3, 'AUDCAD_darwinex', 'AUDCAD_darwinex', 'TICK', 'EETUS',
             1506902700032, 1779764398957, 1, 1000, 5, 4, 'AUDCAD', 'AUDCAD', 4)
            """
        )
        con.execute(
            """
            insert into DATA values
            (2, 'USDJPY_darwinex', 'USDJPY_darwinex', 'TICK', 'EETUS',
             1506902700032, 1778885999065, 1, 1000, 3, 4, 'USDJPY', 'USDJPY', 4)
            """
        )
        for instrument, spread, decimals in (
            ("AUDCAD_darwinex", 2.0, 5),
            ("USDJPY_darwinex", 1.4, 3),
        ):
            con.execute(
                """
                insert into INSTRUMENTS values
                (?, 'Currency', 1.0, 0.0001, 0.00001, ?, '<Method/>', 3,
                 '', '', 'Currency', 0.0, '<Swap/>', 1.0, 0.01, 4, 0.0)
                """,
                (instrument, spread),
            )
        con.commit()
    finally:
        con.close()


def test_aligns_cross_broker_symbol_to_data_db_metadata(tmp_path: Path) -> None:
    _make_sqx_data_db(tmp_path)
    xml = """
    <Root>
      <Data><Setups><Setup><Chart symbol="AUDCAD_dukascopy" spread="1.9" /></Setup></Setups></Data>
      <Resources>
        <Symbols>
          <Symbol name="AUDCAD_dukascopy" source="2" broker="3" dateFrom="1262311415817" dateTo="1506902400000">
            <InstrumentInfo instrument="AUDCAD_dukascopy" broker="3" />
          </Symbol>
        </Symbols>
        <Brokers><Broker id="3" name="[[Dukascopy]]" /></Brokers>
      </Resources>
    </Root>
    """

    patched, changes = _patch_resources_to_data_db(xml, tmp_path)

    assert [change["code"] for change in changes] == [
        "align_resource_metadata_to_data_db",
        "align_chart_spread_to_data_db",
    ]
    root = ET.fromstring(patched)
    symbol = root.find(".//Resources/Symbols/Symbol")
    info = symbol.find("InstrumentInfo")
    assert symbol.get("broker") == "4"
    assert symbol.get("source") == "2"
    assert info.get("instrument") == "AUDCAD_darwinex"
    assert info.get("broker") == "4"
    assert root.find(".//Setup/Chart").get("spread") == "2.0"
    assert root.find(".//Resources/Brokers/Broker[@id='4']").get("postfix") == "_darwinex"


def test_bounds_resource_dates_when_requested_period_has_no_local_data(tmp_path: Path) -> None:
    _make_sqx_data_db(tmp_path)
    xml = """
    <Root>
      <Resources>
        <Symbols>
          <Symbol name="USDJPY_darwinex" source="4" broker="4" dateFrom="1262304000000" dateTo="1483142400000">
            <InstrumentInfo instrument="USDJPY_darwinex" broker="4" />
          </Symbol>
        </Symbols>
        <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
      </Resources>
    </Root>
    """

    patched, changes = _patch_resources_to_data_db(xml, tmp_path)

    assert [change["code"] for change in changes] == ["bound_resource_dates_to_data_db"]
    symbol = ET.fromstring(patched).find(".//Resources/Symbols/Symbol")
    assert symbol.get("dateFrom") == "1506902700032"
    assert symbol.get("dateTo") == "1778885999065"


def test_converts_dukascopy_task_to_local_darwinex_loadable(tmp_path: Path) -> None:
    _make_sqx_data_db(tmp_path)
    xml = """
    <Root>
      <Data><Setups><Setup dateFrom="2010.01.01" dateTo="2017.10.02"><Chart symbol="AUDCAD_dukascopy" spread="1.9" /></Setup></Setups></Data>
      <Resources>
        <Symbols>
          <Symbol name="AUDCAD_dukascopy" source="2" broker="3" dateFrom="1262304000000" dateTo="1506902400000">
            <InstrumentInfo instrument="AUDCAD_dukascopy" broker="3" />
          </Symbol>
        </Symbols>
        <Brokers><Broker id="3" name="[[Dukascopy]]" /></Brokers>
      </Resources>
    </Root>
    """

    patched, changes = _patch_cross_broker_to_local_loadable(xml, tmp_path)

    assert "convert_cross_broker_chart_to_local" in {change["code"] for change in changes}
    assert "convert_cross_broker_resource_to_local" in {change["code"] for change in changes}
    assert "bound_setup_dates_to_local_data" in {change["code"] for change in changes}
    root = ET.fromstring(patched)
    setup = root.find(".//Setup")
    chart = setup.find("Chart")
    symbol = root.find(".//Resources/Symbols/Symbol")
    assert setup.get("dateFrom") == "2017.10.02"
    assert chart.get("symbol") == "AUDCAD_darwinex"
    assert symbol.get("name") == "AUDCAD_darwinex"
    assert symbol.get("source") == "4"
    assert symbol.get("broker") == "4"


def test_aligns_backup_strategy_symbol_and_blanks_absolute_strategy_path() -> None:
    xml = """
    <Root>
      <Data><Setups><Setup><Chart symbol="AUDCAD_darwinex" /></Setup></Setups></Data>
      <StrategyType templateFile="C:\\Users\\Ivan SQX\\Downloads\\old.sqx" />
      <BackupStrategyTemplate><symbol>XAUUSD_darwinex</symbol></BackupStrategyTemplate>
    </Root>
    """

    patched, symbol_changes = _patch_backup_strategy_symbols_to_chart(xml)
    patched, path_changes = _patch_absolute_strategy_type_paths(patched)

    root = ET.fromstring(patched)
    assert [change["code"] for change in symbol_changes] == ["align_backup_strategy_symbol_to_chart"]
    assert [change["code"] for change in path_changes] == ["blank_absolute_strategy_type_templateFile"]
    assert root.find(".//BackupStrategyTemplate/symbol").text == "AUDCAD_darwinex"
    assert root.find(".//StrategyType").get("templateFile") == ""


def test_prunes_unused_resource_brokers() -> None:
    xml = """
    <Root>
      <Resources>
        <Symbols>
          <Symbol name="AUDCAD_darwinex" broker="4">
            <InstrumentInfo instrument="AUDCAD_darwinex" broker="4" />
          </Symbol>
        </Symbols>
        <Brokers>
          <Broker id="3" name="[[Dukascopy]]" />
          <Broker id="4" name="[[Darwinex]]" />
        </Brokers>
      </Resources>
    </Root>
    """

    patched, changes = _prune_unused_resource_brokers(xml)

    assert changes == [{"code": "prune_unused_resource_brokers", "removed": "3", "used": "4"}]
    brokers = ET.fromstring(patched).findall(".//Resources/Brokers/Broker")
    assert [broker.get("id") for broker in brokers] == ["4"]


def test_keeps_sanitized_config_template_references_without_blanketing_missing_paths() -> None:
    xml = """
    <Project name="Capa2_Base_SQX142_Base">
      <Tasks>
        <Task type="Build" taskXMLFile="Build-Task1.xml" templateFile="" />
        <Task type="AutomaticRetest" taskXMLFile="AutomaticRetest-Task8.xml" templateFile="" sampleName="" />
        <Task type="Retest" taskXMLFile="Retest-Task1.xml" templateFile="Z:/missing/legacy.cfx" />
      </Tasks>
    </Project>
    """

    patched, changes = _patch_config(xml)

    root = ET.fromstring(patched)
    assert [change["code"] for change in changes] == []
    assert root.find("./Tasks/Task[@taskXMLFile='Build-Task1.xml']").get("templateFile") == ""
    assert root.find("./Tasks/Task[@taskXMLFile='AutomaticRetest-Task8.xml']").get("templateFile") == ""
    assert root.find("./Tasks/Task[@taskXMLFile='Retest-Task1.xml']").get("templateFile") == "Z:/missing/legacy.cfx"


def test_capa2_clean_load_config_blanks_missing_task_templates_and_updates_version() -> None:
    xml = """
    <Project name="Capa2_Base_SQX142_Base" version="141.2225">
      <Tasks>
        <Task taskXMLFile="Build-Task1.xml" templateFile="D:/WuantumBot/Build.cfx" />
        <Task taskXMLFile="AutomaticRetest-Task8.xml" templateFile="C:\\Users\\Administrator\\Desktop\\EDGE\\MC 2 EDGE\\Automatic retest 7.cfx" />
        <Task taskXMLFile="Retest-Task1.xml" templateFile="" />
      </Tasks>
    </Project>
    """

    patched, changes = _patch_config_for_clean_load(xml, "Capa2_Base_SQX142_Base")
    untouched, untouched_changes = _patch_config_for_clean_load(xml, "Other_Project")

    root = ET.fromstring(patched)
    assert root.get("version") == "142.2336"
    assert [change["code"] for change in changes] == [
        "normalize_project_version_to_clean_sqx142",
        "blank_missing_task_templateFile",
        "blank_missing_task_templateFile",
    ]
    assert root.find("./Tasks/Task[@taskXMLFile='Build-Task1.xml']").get("templateFile") == ""
    assert root.find("./Tasks/Task[@taskXMLFile='AutomaticRetest-Task8.xml']").get("templateFile") == ""
    assert untouched == xml
    assert untouched_changes == []


def test_rewrites_clean_donor_symbol_family_to_target_data_db_metadata(tmp_path: Path) -> None:
    _make_sqx_data_db(tmp_path)
    resource = _resource_from_db(tmp_path, "AUDCAD_darwinex")
    xml = """
    <Root>
      <Data><Setups><Setup><Chart symbol="USDJPY_darwinex" spread="1.4" /></Setup></Setups></Data>
      <Resources>
        <Symbols>
          <Symbol name="USDJPY_darwinex" source="4" broker="4" dateFrom="1" dateTo="2">
            <InstrumentInfo instrument="USDJPY_darwinex" broker="4" />
          </Symbol>
        </Symbols>
        <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
      </Resources>
      <BackupStrategyTemplate><symbol>USDJPY_darwinex</symbol></BackupStrategyTemplate>
    </Root>
    """

    patched, changes = _patch_donor_symbol_family(xml, "USDJPY_darwinex", resource)

    root = ET.fromstring(patched)
    assert "USDJPY" not in patched
    assert {change["code"] for change in changes} >= {
        "rewrite_clean_donor_symbol_tokens",
        "align_clean_donor_chart_spread",
        "align_clean_donor_resource_metadata",
    }
    assert root.find(".//Setup/Chart").get("symbol") == "AUDCAD_darwinex"
    assert root.find(".//Setup/Chart").get("spread") == "2.0"
    symbol = root.find(".//Resources/Symbols/Symbol")
    assert symbol.get("name") == "AUDCAD_darwinex"
    assert symbol.get("dateFrom") == "1506902700032"
    info = symbol.find("InstrumentInfo")
    assert info.get("instrument") == "AUDCAD_darwinex"
    assert info.get("tickSize") == "1.0E-4"
    assert info.get("tickStep") == "1.0E-5"
    assert root.find(".//BackupStrategyTemplate/symbol").text == "AUDCAD_darwinex"


def test_neutralizes_only_base_project_improve_databank_chains() -> None:
    xml = """
    <Root>
      <StrategyType improveDatabank="RETEST 0" />
      <StrategyType improveDatabank="Strategies to improve" />
    </Root>
    """

    patched, changes = _patch_base_strategy_type_improve_databank(
        xml, "Capa1_Long_SQX142_Base"
    )
    untouched, untouched_changes = _patch_base_strategy_type_improve_databank(
        xml, "Mining01_USDJPY_H1_BS_Volatilidad_v6_intraday_v6_LS_Capa2"
    )

    assert changes == [
        {
            "code": "neutralize_base_improve_databank",
            "from": "RETEST 0",
            "to": "Strategies to improve",
        }
    ]
    assert [node.get("improveDatabank") for node in ET.fromstring(patched).findall(".//StrategyType")] == [
        "Strategies to improve",
        "Strategies to improve",
    ]
    assert untouched == xml
    assert untouched_changes == []


def test_caps_only_known_base_project_edge_date_ranges() -> None:
    xml = """
    <Root>
      <Resources>
        <Symbols>
          <Symbol name="AUDCAD_darwinex" dateFrom="1506902700032" dateTo="1779764398957" />
        </Symbols>
      </Resources>
      <Data>
        <Setups>
          <Setup dateFrom="2017.10.02" dateTo="2026.05.26"><Chart symbol="AUDCAD_darwinex" /></Setup>
          <Setup dateFrom="2017.10.02" dateTo="2026.05.26"><Chart symbol="AUDCAD_darwinex" /></Setup>
        </Setups>
      </Data>
    </Root>
    """

    patched, changes = _patch_base_project_date_caps(
        xml, "Capa1_Long_SQX142_Base", "Retest-Task1.xml"
    )
    untouched, untouched_changes = _patch_base_project_date_caps(
        xml, "Mining01_USDJPY_H1_BS_Volatilidad_v6_intraday_v6_LS_Capa2", "Retest-Task1.xml"
    )

    root = ET.fromstring(patched)
    symbol = root.find(".//Resources/Symbols/Symbol")
    setups = root.findall(".//Setup")
    assert [change["code"] for change in changes] == [
        "cap_base_resource_date_range",
        "cap_base_setup_date_to",
        "cap_base_setup_date_to",
    ]
    assert symbol.get("dateFrom") == "1506902400000"
    assert symbol.get("dateTo") == "1775606400000"
    assert [setup.get("dateTo") for setup in setups] == ["2026.04.08", "2026.04.08"]
    assert untouched == xml
    assert untouched_changes == []


def test_rewrites_only_project_name_for_clean_donor_config() -> None:
    xml = '<Project name="Capa1_Long_SQX142_Base(2)"><Tasks /></Project>'

    patched, changes = _rewrite_project_name(xml, "Capa1_Long_SQX142_Base")
    unchanged, unchanged_changes = _rewrite_project_name(
        '<Project name="Capa1_Long_SQX142_Base"><Tasks /></Project>',
        "Capa1_Long_SQX142_Base",
    )

    assert ET.fromstring(patched).get("name") == "Capa1_Long_SQX142_Base"
    assert changes == [
        {
            "code": "rewrite_clean_donor_project_name",
            "from": "Capa1_Long_SQX142_Base(2)",
            "to": "Capa1_Long_SQX142_Base",
        }
    ]
    assert unchanged == '<Project name="Capa1_Long_SQX142_Base"><Tasks /></Project>'
    assert unchanged_changes == []


def test_rebuilds_capa1_from_clean_local_donor_with_backup_and_rollback(tmp_path: Path) -> None:
    sqx_root = tmp_path / "sqx"
    repo_root = tmp_path / "repo"
    target_cfx = sqx_root / "user" / "projects" / "Capa1_Long_SQX142_Base" / "project.cfx"
    donor_cfx = sqx_root / "user" / "projects" / "Capa1_Long_SQX142_Base(2)" / "project.cfx"
    _make_project_cfx(target_cfx, "Capa1_Long_SQX142_Base", "old-red-target")
    _make_project_cfx(donor_cfx, "Capa1_Long_SQX142_Base(2)", "clean-donor")

    manifest = rebuild_capa1_from_clean_donor(sqx_root, repo_root)

    assert manifest["ok"] is True
    assert manifest["action"] == "rebuild-capa1"
    result = manifest["projects"][0]
    assert result["project"] == "Capa1_Long_SQX142_Base"
    assert result["donor"] == "Capa1_Long_SQX142_Base(2)"
    assert result["changed"] is True
    assert [change["code"] for change in result["changes"]] == [
        "rewrite_clean_donor_project_name"
    ]
    with zipfile.ZipFile(target_cfx) as archive:
        assert archive.testzip() is None
        assert ET.fromstring(archive.read("config.xml")).get("name") == "Capa1_Long_SQX142_Base"
        assert b"clean-donor" in archive.read("Build-Task1.xml")
    backup_cfx = (
        repo_root
        / ".local"
        / "sqx142_project_resource_repair"
        / "backups"
        / manifest["backupId"]
        / "Capa1_Long_SQX142_Base"
        / "project.cfx"
    )
    with zipfile.ZipFile(backup_cfx) as archive:
        assert b"old-red-target" in archive.read("Build-Task1.xml")

    rollback_payload = rollback(sqx_root, repo_root, manifest["backupId"])

    assert rollback_payload["ok"] is True
    with zipfile.ZipFile(target_cfx) as archive:
        assert b"old-red-target" in archive.read("Build-Task1.xml")


def test_repairs_only_capa2_config_with_backup_and_rollback(tmp_path: Path) -> None:
    sqx_root = tmp_path / "sqx"
    repo_root = tmp_path / "repo"
    cfx = sqx_root / "user" / "projects" / "Capa2_Base_SQX142_Base" / "project.cfx"
    cfx.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(cfx, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "config.xml",
            (
                '<Project name="Capa2_Base_SQX142_Base" version="141.2225"><Tasks>'
                '<Task taskXMLFile="Build-Task1.xml" templateFile="D:/WuantumBot/Build.cfx" />'
                "</Tasks></Project>"
            ),
        )
        archive.writestr("Build-Task1.xml", "<Root><Marker>methodology-kept</Marker></Root>")

    manifest = repair_capa2_clean_config(sqx_root, repo_root)

    assert manifest["ok"] is True
    assert manifest["action"] == "repair-capa2-config"
    assert manifest["projects"][0]["changed"] is True
    with zipfile.ZipFile(cfx) as archive:
        root = ET.fromstring(archive.read("config.xml"))
        assert root.get("version") == "142.2336"
        assert root.find("./Tasks/Task").get("templateFile") == ""
        assert b"methodology-kept" in archive.read("Build-Task1.xml")

    rollback(sqx_root, repo_root, manifest["backupId"])

    with zipfile.ZipFile(cfx) as archive:
        root = ET.fromstring(archive.read("config.xml"))
        assert root.get("version") == "141.2225"
        assert root.find("./Tasks/Task").get("templateFile") == "D:/WuantumBot/Build.cfx"


def test_rebuilds_capa2_from_clean_donor_and_normalizes_symbol(tmp_path: Path) -> None:
    _make_sqx_data_db(tmp_path / "sqx")
    sqx_root = tmp_path / "sqx"
    repo_root = tmp_path / "repo"
    target_cfx = sqx_root / "user" / "projects" / "Capa2_Base_SQX142_Base" / "project.cfx"
    donor_cfx = (
        sqx_root
        / "user"
        / "projects"
        / "Mining01_USDJPY_H1_BS_Volatilidad_v6_intraday_v6_LS_Capa2"
        / "project.cfx"
    )
    _make_project_cfx(target_cfx, "Capa2_Base_SQX142_Base", "old-red-capa2")
    donor_cfx.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(donor_cfx, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "config.xml",
            (
                '<Project name="Mining01_USDJPY_H1_BS_Volatilidad_v6_intraday_v6_LS_Capa2" '
                'version="142.2336"><Tasks><Task taskXMLFile="Build-Task1.xml" /></Tasks></Project>'
            ),
        )
        archive.writestr(
            "Build-Task1.xml",
            """
            <Root>
              <Data><Setups><Setup><Chart symbol="USDJPY_darwinex" spread="1.4" /></Setup></Setups></Data>
              <Resources>
                <Symbols>
                  <Symbol name="USDJPY_darwinex" source="4" broker="4">
                    <InstrumentInfo instrument="USDJPY_darwinex" broker="4" />
                  </Symbol>
                </Symbols>
                <Brokers><Broker id="4" name="[[Darwinex]]" /></Brokers>
              </Resources>
            </Root>
            """,
        )

    manifest = rebuild_capa2_from_clean_donor(sqx_root, repo_root)

    assert manifest["ok"] is True
    assert manifest["action"] == "rebuild-capa2"
    assert manifest["projects"][0]["changed"] is True
    with zipfile.ZipFile(target_cfx) as archive:
        assert archive.testzip() is None
        config = archive.read("config.xml").decode("utf-8")
        task = archive.read("Build-Task1.xml").decode("utf-8")
        assert ET.fromstring(config).get("name") == "Capa2_Base_SQX142_Base"
        assert "USDJPY" not in config + task
        assert "AUDCAD_darwinex" in task

    rollback(sqx_root, repo_root, manifest["backupId"])

    with zipfile.ZipFile(target_cfx) as archive:
        assert b"old-red-capa2" in archive.read("Build-Task1.xml")
