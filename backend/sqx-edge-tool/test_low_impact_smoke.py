"""Smoke tests de endpoints de bajo impacto sin cobertura previa (auditoria 2026-06-17).

Cubre:
  - GET  /api/plan               (devuelve el plan.json)
  - GET  /api/templates          (lista de .cfx)
  - GET  /api/output             ({files: [...], output_dir: ...})
  - POST /api/sqx-preview-rename ({ok: True, previews: [...]}; tolerante a paths no permitidos)
  - POST /api/open-folder        (400 si invalido; 403 si el path no esta permitido)

No toca codigo de produccion ni escribe config.json. El unico efecto lateral
posible (abrir el explorador) se neutraliza con un mock de subprocess.Popen.
"""
import tempfile
import unittest
from unittest.mock import patch

import pytest

try:
    from api import server
except ImportError:  # respaldo segun como resuelva sys.path la suite
    import server

pytestmark = pytest.mark.smoke


class LowImpactSmokeTests(unittest.TestCase):
    def setUp(self):
        self.client = server.app.test_client()

    def test_plan_returns_json_dict(self):
        resp = self.client.get("/api/plan")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), dict)

    def test_templates_returns_list(self):
        resp = self.client.get("/api/templates")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)

    def test_output_returns_files_list_with_temp_output_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(server, "load_config", return_value={"output_dir": tmp}):
                resp = self.client.get("/api/output")
                self.assertEqual(resp.status_code, 200)
                body = resp.get_json()
                self.assertIsInstance(body, dict)
                self.assertIsInstance(body["files"], list)

    def test_sqx_preview_rename_tolerates_unallowed_path(self):
        # Un path inexistente / fuera del whitelist no debe reventar: ok + previews vacio.
        resp = self.client.post(
            "/api/sqx-preview-rename",
            json={"files": ["/no/such/strategy.sqx"], "pattern": "{asset}_{tf}_{dir}_{id}"},
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertTrue(body["ok"])
        self.assertIsInstance(body["previews"], list)

    def test_open_folder_invalid_path_returns_400(self):
        with patch.object(server.subprocess, "Popen") as popen:
            resp = self.client.post("/api/open-folder", json={"path": ""})
            self.assertEqual(resp.status_code, 400)
            popen.assert_not_called()

    def test_open_folder_forbidden_path_returns_403_no_side_effect(self):
        # Un path real pero fuera del workspace permitido se rechaza con 403
        # y NO lanza el proceso del explorador.
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(server.subprocess, "Popen") as popen:
                resp = self.client.post("/api/open-folder", json={"path": tmp})
                self.assertEqual(resp.status_code, 403)
                popen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
