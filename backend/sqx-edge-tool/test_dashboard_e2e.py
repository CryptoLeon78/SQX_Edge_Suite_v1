import shutil
import subprocess
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
E2E_SCRIPT = PROJECT_ROOT / "tests" / "ui_e2e" / "dashboard_smoke.mjs"


class DashboardE2ETestCase(unittest.TestCase):
    def test_dashboard_smoke_flow_with_playwright_when_available(self):
        if shutil.which("node") is None:
            self.skipTest("Node.js is not available for optional dashboard E2E tests")
        if not (PROJECT_ROOT / "node_modules" / "playwright").is_dir():
            self.skipTest("Playwright is not installed; run `npm install --no-save --package-lock=false playwright` to enable E2E tests")

        result = subprocess.run(
            ["node", str(E2E_SCRIPT)],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            timeout=45,
        )
        if result.returncode != 0:
            self.fail(result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
