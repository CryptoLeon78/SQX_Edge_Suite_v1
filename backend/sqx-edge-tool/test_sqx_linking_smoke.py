"""Smoke tests del flujo de vinculacion SQX: config -> data.db -> symbol-info.

Cubre los huecos detectados en la auditoria de tests 2026-06-17:
  - POST/GET /api/config            (persistir/leer sqx_data_db)   [cobertura cero]
  - GET  /api/symbol-info/<asset>   (404 sin DB; OK con DB)        [hoy se salta en CI]
  - GET  /api/instruments           (lista desde la DB)            [hoy se salta en CI]
  - GET  /api/autodetect-sqx        (descubre sin persistir)       [cobertura cero]
  - POST /api/validate-sqx-path     (valida sin persistir)         [cobertura cero]

No toca codigo de produccion. Aisla server.CONFIG_PATH en un tmp por test y, como
red de seguridad, respalda/restaura el config.json real en setUp/tearDown.
"""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Mismo objeto de modulo que usa la app (asi el patch de CONFIG_PATH aisla de verdad).
try:
    from api import server
except ImportError:  # respaldo segun como resuelva sys.path la suite
    import server


def _build_synthetic_sqx_db(db_path):
    """Crea una data.db SQLite minima con el esquema que espera SqxDb."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("CREATE TABLE BROKER (ID INTEGER, NAME TEXT, POSTFIX TEXT, DESC TEXT)")
        conn.execute(
            "INSERT INTO BROKER (ID, NAME, POSTFIX, DESC) "
            "VALUES (5, '[[Darwinex]]', '_darwinex', 'Darwinex CFDs')"
        )
        conn.execute(
            "CREATE TABLE INSTRUMENTS ("
            "INSTRUMENT TEXT PRIMARY KEY, DESCRIPTION TEXT, POINTVALUE REAL, TICKSIZE REAL, "
            "DEFAULTSPREAD REAL, DEFAULTSLIPPAGE REAL, BROKER_ID INTEGER, COMMISSIONS TEXT, SWAP TEXT)"
        )
        # COMMISSIONS/SWAP a NULL: el parser los trata como ausentes (igual que la fila real de EURUSD).
        conn.execute(
            "INSERT INTO INSTRUMENTS "
            "(INSTRUMENT, DESCRIPTION, POINTVALUE, TICKSIZE, DEFAULTSPREAD, DEFAULTSLIPPAGE, BROKER_ID, COMMISSIONS, SWAP) "
            "VALUES ('EURUSD', 'EURUSD', 100000.0, 0.0001, 2.0, 0.0, 5, NULL, NULL)"
        )
        conn.execute(
            "CREATE TABLE DATA (SYMBOL TEXT, TIMEFRAME TEXT, DATEFROM INTEGER, DATETO INTEGER, ROWS INTEGER)"
        )
        conn.execute(
            "INSERT INTO DATA (SYMBOL, TIMEFRAME, DATEFROM, DATETO, ROWS) "
            "VALUES ('EURUSD', 'M1', 1577836800000, 1735689600000, 100000)"
        )
        conn.commit()
    finally:
        conn.close()


class SqxLinkingSmokeTests(unittest.TestCase):
    def setUp(self):
        self.client = server.app.test_client()
        # Red de seguridad: respaldar el config.json real y restaurarlo en tearDown.
        self._real_config_path = Path(server.CONFIG_PATH)
        self._real_config_backup = (
            self._real_config_path.read_text(encoding="utf-8")
            if self._real_config_path.exists()
            else None
        )

    def tearDown(self):
        if self._real_config_backup is None:
            if self._real_config_path.exists():
                self._real_config_path.unlink()
        else:
            self._real_config_path.write_text(self._real_config_backup, encoding="utf-8")

    # ----- POST/GET /api/config: persistencia de sqx_data_db (raiz del 404) -----
    def test_post_config_persists_sqx_data_db_and_get_reads_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "config.json"
            db_path = Path(tmp) / "data.db"
            with patch.object(server, "CONFIG_PATH", cfg_path):
                resp = self.client.post(
                    "/api/config", json={"sqx_path": tmp, "sqx_data_db": str(db_path)}
                )
                self.assertEqual(resp.status_code, 200)
                body = resp.get_json()
                self.assertTrue(body["ok"])
                self.assertIn("sqx_data_db", body["updated_keys"])
                got = self.client.get("/api/config").get_json()
                self.assertEqual(got["sqx_data_db"], str(db_path))

    def test_post_config_ignores_keys_outside_allowlist(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "config.json"
            with patch.object(server, "CONFIG_PATH", cfg_path):
                resp = self.client.post(
                    "/api/config", json={"evil_key": "x", "sqx_path": tmp}
                )
                self.assertEqual(resp.status_code, 200)
                got = self.client.get("/api/config").get_json()
                self.assertNotIn("evil_key", got)
                self.assertEqual(got.get("sqx_path"), tmp)

    # ----- /api/symbol-info: 404 sin DB, OK con DB sintetica -----
    def test_symbol_info_404_when_db_not_configured(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "config.json"
            cfg_path.write_text(json.dumps({}), encoding="utf-8")  # sin sqx_data_db
            with patch.object(server, "CONFIG_PATH", cfg_path):
                resp = self.client.get("/api/symbol-info/EURUSD")
                self.assertEqual(resp.status_code, 404)
                self.assertFalse(resp.get_json()["ok"])

    def test_symbol_info_ok_with_synthetic_db(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "config.json"
            db_path = Path(tmp) / "data.db"
            _build_synthetic_sqx_db(db_path)
            cfg_path.write_text(json.dumps({"sqx_data_db": str(db_path)}), encoding="utf-8")
            with patch.object(server, "CONFIG_PATH", cfg_path):
                resp = self.client.get("/api/symbol-info/EURUSD")
                self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
                info = resp.get_json()["info"]
                self.assertEqual(info["instrument"], "EURUSD")
                self.assertEqual(info["point_value"], 100000.0)
                self.assertEqual(info["spread"], 2.0)

    def test_instruments_lists_from_synthetic_db(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "config.json"
            db_path = Path(tmp) / "data.db"
            _build_synthetic_sqx_db(db_path)
            cfg_path.write_text(json.dumps({"sqx_data_db": str(db_path)}), encoding="utf-8")
            with patch.object(server, "CONFIG_PATH", cfg_path):
                resp = self.client.get("/api/instruments")
                self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
                body = resp.get_json()
                self.assertTrue(body["ok"])
                self.assertIn("EURUSD", body["instruments"])

    # ----- autodetect / validate: devuelven sin persistir -----
    def test_autodetect_returns_shape_without_persisting(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "config.json"  # no existe -> load_config() == {}
            with patch.object(server, "CONFIG_PATH", cfg_path):
                resp = self.client.get("/api/autodetect-sqx")
                self.assertEqual(resp.status_code, 200)
                body = resp.get_json()
                self.assertTrue(body["ok"])
                self.assertIsInstance(body["candidates"], list)
                self.assertEqual(body["found"], len(body["candidates"]))
                self.assertFalse(cfg_path.exists())  # no ha persistido

    def test_validate_sqx_path_cases_without_persisting(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "config.json"
            with patch.object(server, "CONFIG_PATH", cfg_path):
                # path vacio -> 400
                self.assertEqual(
                    self.client.post("/api/validate-sqx-path", json={"path": ""}).status_code,
                    400,
                )
                # base sin data.db -> valid False
                base_bad = Path(tmp) / "bad"
                base_bad.mkdir()
                r2 = self.client.post("/api/validate-sqx-path", json={"path": str(base_bad)})
                self.assertEqual(r2.status_code, 200)
                self.assertFalse(r2.get_json()["valid"])
                # base con user/data/data.db -> valid True
                base_ok = Path(tmp) / "ok"
                (base_ok / "user" / "data").mkdir(parents=True)
                (base_ok / "user" / "data" / "data.db").write_text("x", encoding="utf-8")
                (base_ok / "user" / "projects").mkdir(parents=True)
                r3 = self.client.post("/api/validate-sqx-path", json={"path": str(base_ok)})
                self.assertEqual(r3.status_code, 200)
                self.assertTrue(r3.get_json()["valid"])
                self.assertFalse(cfg_path.exists())  # no ha persistido


if __name__ == "__main__":
    unittest.main()
