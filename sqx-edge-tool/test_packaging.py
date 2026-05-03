import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TOOL_ROOT = ROOT / "sqx-edge-tool"


class EmbeddedPackagingTestCase(unittest.TestCase):
    def test_embedded_launchers_and_tools_exist(self):
        expected = [
            ROOT / "START_SQX_EDGE.bat",
            ROOT / "STOP_SQX_EDGE.bat",
            TOOL_ROOT / "run-embedded.bat",
            TOOL_ROOT / "run-web-embedded.bat",
            TOOL_ROOT / "tools" / "bootstrap_embedded_python.ps1",
            TOOL_ROOT / "tools" / "package_portable.ps1",
        ]
        for path in expected:
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file(), path)

    def test_launchers_use_project_local_runtime(self):
        for name in ("run-embedded.bat", "run-web-embedded.bat"):
            text = (TOOL_ROOT / name).read_text(encoding="utf-8-sig")
            with self.subTest(name=name):
                self.assertIn("runtime\\python\\python.exe", text)
                self.assertIn("bootstrap_embedded_python.ps1", text)

    def test_one_click_launcher_opens_embedded_stack(self):
        text = (ROOT / "START_SQX_EDGE.bat").read_text(encoding="utf-8-sig")
        self.assertIn("run-web-embedded.bat", text)
        self.assertIn("SQX_Dashboard_v6.html", text)
        self.assertIn("http://127.0.0.1:5050/api/health", text)

    def test_roadmap_marks_f7_done(self):
        readme = (TOOL_ROOT / "README.md").read_text(encoding="utf-8-sig")
        self.assertIn("[x] **F7**", readme)


if __name__ == "__main__":
    unittest.main()
