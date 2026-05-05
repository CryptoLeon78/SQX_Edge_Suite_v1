import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOL_ROOT = PROJECT_ROOT / "backend" / "sqx-edge-tool"
PACKAGING_ROOT = PROJECT_ROOT / "packaging"


class EmbeddedPackagingTestCase(unittest.TestCase):
    def test_embedded_launchers_and_tools_exist(self):
        expected = [
            PROJECT_ROOT / "START_SQX_EDGE.bat",
            PROJECT_ROOT / "STOP_SQX_EDGE.bat",
            PROJECT_ROOT / "RELEASE_SQX_EDGE.bat",
            PACKAGING_ROOT / "START_SQX_EDGE.bat",
            PACKAGING_ROOT / "STOP_SQX_EDGE.bat",
            TOOL_ROOT / "run-embedded.bat",
            TOOL_ROOT / "run-web-embedded.bat",
            TOOL_ROOT / "tools" / "bootstrap_embedded_python.ps1",
            TOOL_ROOT / "tools" / "package_portable.ps1",
            TOOL_ROOT / "tools" / "release_checklist.ps1",
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
        text = (PROJECT_ROOT / "START_SQX_EDGE.bat").read_text(encoding="utf-8-sig")
        self.assertIn("packaging\\START_SQX_EDGE.bat", text)
        text = (PACKAGING_ROOT / "START_SQX_EDGE.bat").read_text(encoding="utf-8-sig")
        self.assertIn("run-web-embedded.bat", text)
        self.assertIn("app\\SQX_Dashboard_v6.html", text)
        self.assertIn("http://127.0.0.1:5050/api/health", text)

    def test_portable_package_includes_embedded_runtime(self):
        text = (TOOL_ROOT / "tools" / "package_portable.ps1").read_text(encoding="utf-8-sig")
        self.assertIn('"runtime\\python\\python.exe"', text)
        self.assertNotIn('"runtime"', text)
        self.assertIn('"\\\\backend\\\\sqx-edge-tool\\\\runtime\\\\downloads\\\\",', text)
        self.assertIn('"node_modules"', text)
        self.assertIn("RELEASE_SQX_EDGE", text)

    def test_release_checklist_validates_portable_user_flow(self):
        text = (TOOL_ROOT / "tools" / "release_checklist.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("module_contracts.mjs", text)
        self.assertIn("-m pytest", text)
        self.assertIn("package_portable.ps1", text)
        self.assertIn("START_SQX_EDGE.bat", text)
        self.assertIn("project-generator-dom.js", text)
        self.assertIn("RELEASE_SQX_EDGE.bat", text)
        self.assertIn("/api/health", text)
        self.assertIn("runtime\\python\\python.exe", text)
        self.assertIn("RequireCleanGit", text)
        self.assertIn("SQX_release_summary.txt", text)
        self.assertIn("Clean Git working tree", text)

    def test_release_bat_runs_strict_checklist(self):
        text = (PROJECT_ROOT / "RELEASE_SQX_EDGE.bat").read_text(encoding="utf-8-sig")
        self.assertIn("release_checklist.ps1", text)
        self.assertIn("-RequireCleanGit", text)
        self.assertIn("pause", text.lower())

    def test_roadmap_marks_f7_done(self):
        readme = (TOOL_ROOT / "README.md").read_text(encoding="utf-8-sig")
        self.assertIn("[x] **F7**", readme)


if __name__ == "__main__":
    unittest.main()
