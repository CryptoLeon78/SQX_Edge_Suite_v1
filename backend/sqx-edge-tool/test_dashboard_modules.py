import shutil
import subprocess
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_SCRIPT = PROJECT_ROOT / "tests" / "js" / "module_contracts.mjs"


class DashboardModuleContractTestCase(unittest.TestCase):
    def test_dashboard_js_module_contracts_with_node(self):
        if shutil.which("node") is None:
            self.skipTest("Node.js is not available for dashboard module contract tests")

        result = subprocess.run(
            ["node", str(CONTRACT_SCRIPT)],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            timeout=30,
        )
        if result.returncode != 0:
            self.fail(result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
