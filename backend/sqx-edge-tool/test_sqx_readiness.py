import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core import sqx_readiness


class SqxReadinessTestCase(unittest.TestCase):
    def test_manifest_loads_required_contract(self):
        manifest = sqx_readiness.load_readiness_manifest()
        self.assertEqual(manifest["schema"], "sqx-edge.sqx-readiness-manifest-v2")
        self.assertIn("darwinex", [item["id"] for item in manifest["brokerProfiles"]])
        self.assertIn("dukascopy_oos", [item["id"] for item in manifest["brokerProfiles"]])
        self.assertIn("sqx_root_selected", sqx_readiness.required_check_ids(manifest))
        self.assertIn("SQXEdgeCorrelationTagger.java", "\n".join(manifest["requiredSnippets"]))
        self.assertFalse(manifest["privacy"]["dataDbCopied"])

    def test_report_evaluation_maps_checker_summary_and_blockers(self):
        report = {
            "source": "portable_checker",
            "checkerVersion": "test",
            "summary": {
                "sqxRootSelected": True,
                "versionCompatible": True,
                "dataDbFound": True,
                "brokersValidated": True,
                "curatedAssetsValidated": True,
                "snippetsReady": True,
                "viewsReady": False,
            },
            "checks": {
                "portable_source_acknowledged": True,
                "sensitive_files_excluded": True,
            },
        }
        status = sqx_readiness.evaluate_readiness_report(report)
        self.assertTrue(status["ok"])
        self.assertFalse(status["complete"])
        self.assertIn("correlation_view_ready", status["missing"])
        self.assertFalse(status["privacy"]["data_db_copied"])

    def test_report_evaluation_accepts_legacy_views_ready_check(self):
        report = {
            "source": "legacy_checker",
            "checks": {
                "sqx_root_selected": True,
                "sqx_version_compatible": True,
                "data_db_found": True,
                "brokers_validated": True,
                "curated_assets_validated": True,
                "snippets_ready": True,
                "views_ready": True,
                "portable_source_acknowledged": True,
                "sensitive_files_excluded": True,
            },
        }
        status = sqx_readiness.evaluate_readiness_report(report)
        self.assertTrue(status["complete"])
        self.assertTrue(status["checks"]["correlation_view_ready"])

    def test_sqlite_probe_reads_fixture_readonly(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir) / "readiness.sqlite"
            connection = sqlite3.connect(tmp)
            try:
                connection.execute("CREATE TABLE BROKER (ID INTEGER, NAME TEXT, POSTFIX TEXT)")
                connection.execute("CREATE TABLE INSTRUMENTS (INSTRUMENT TEXT, TICKSIZE REAL, TICKSTEP REAL, POINTVALUE REAL, DEFAULTSPREAD REAL, DATATYPE INTEGER)")
                connection.execute("CREATE TABLE DATA (INSTRUMENT TEXT, SYMBOL TEXT, TIMEFRAME TEXT, TIMEZONE TEXT, DATATYPE INTEGER, ROWS INTEGER)")
                connection.executemany(
                    "INSERT INTO BROKER VALUES (?, ?, ?)",
                    [(4, "Darwinex", "_darwinex"), (3, "Dukascopy", "_dukascopy")],
                )
                connection.executemany(
                    "INSERT INTO INSTRUMENTS VALUES (?, ?, ?, ?, ?, ?)",
                    [
                        ("EURUSD", 0.0001, 0.00001, 100000, 1.0, 3),
                        ("GBPUSD", 0.0001, 0.00001, 100000, 2.5, 3),
                    ],
                )
                connection.execute("INSERT INTO DATA VALUES (?, ?, ?, ?, ?, ?)", ("EURUSD", "EURUSD_darwinex", "H1", "EETUS", 3, 1000))
                connection.commit()
            finally:
                connection.close()
            manifest = {
                "brokerProfiles": [{"id": "darwinex", "brokerId": 4}, {"id": "dukascopy_oos", "brokerId": 3}],
                "curatedAssets": [{"asset": "EURUSD"}, {"asset": "GBPUSD"}],
            }
            result = sqx_readiness.query_reference_data_db(tmp, manifest)
            self.assertTrue(result["ok"])
            self.assertEqual(result["brokerCount"], 2)
            self.assertEqual(result["curatedCoverage"]["EURUSD"], ["H1"])
            self.assertFalse(result["privacy"]["data_db_copied"])

    def test_local_status_roundtrip_uses_sanitized_path(self):
        tmp = Path(self._testMethodName + ".json")
        try:
            with patch.object(sqx_readiness, "LOCAL_STATUS_PATH", tmp):
                status = sqx_readiness.update_manual_status({
                    check_id: True for check_id in sqx_readiness.required_check_ids()
                })
                self.assertTrue(status["complete"])
                loaded = sqx_readiness.read_readiness_status()
                self.assertTrue(loaded["complete"])
                self.assertFalse(loaded["privacy"]["local_paths_returned"])
                self.assertFalse(loaded["storage"]["local_path_returned"])
        finally:
            tmp.unlink(missing_ok=True)

    def test_packager_declares_blocked_surfaces(self):
        script = Path("tools/sqx_readiness_kit.ps1").read_text(encoding="utf-8")
        for marker in (
            "user[\\\\/]data[\\\\/]data\\.db",
            "user[\\\\/]projects",
            "activation",
            "crack",
            "PrivateOperatorTransfer",
            "SQX_142_Codex_QXPRO",
            "05_SQX_142_Codex_QXPRO_Privado",
            "05_SQX_142_Codex_QXPRO_Privado/SQX_142_Codex_QXPRO",
            "portable_authorization_manifest.json",
            "runtimeAllowlistApplied",
            "bootstrapDataAllowlistApplied",
            "privateBootstrapDataIncluded",
            "historicalDataIncluded",
            "user/data/data.db",
            "user/data/data_futures.h2.db",
            "user/data/History",
            "licenseOrActivationStateIncluded",
            "runtimeActivationLibraryIncluded",
            "internal/libs/activation.jar",
            "license.db",
            "private_operator_only",
            "NO REDISTRIBUIR",
            "Private SQX source root cannot contain Crack",
            "Assert-ZipSourceSafe",
            "Assert-StageSafe",
            "Instalar_snippets_y_View_CORR1.bat",
            "Deshacer_instalacion_snippets_y_View_CORR1.bat",
        ):
            self.assertIn(marker, script)


if __name__ == "__main__":
    unittest.main()
