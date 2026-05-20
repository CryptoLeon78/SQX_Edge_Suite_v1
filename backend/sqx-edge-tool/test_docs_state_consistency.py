import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PROJECT_ROOT / "docs" / "state_consistency_manifest.json"


class DocsStateConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def _read_repo_file(self, relative_path):
        path = PROJECT_ROOT / relative_path
        self.assertTrue(path.exists(), f"Missing state consistency file: {relative_path}")
        return path.read_text(encoding="utf-8")

    def test_core_state_files_exist(self):
        for relative_path in self.manifest["coreFiles"]:
            with self.subTest(relative_path=relative_path):
                self.assertTrue((PROJECT_ROOT / relative_path).exists())

    def test_required_state_markers_are_present(self):
        for rule in self.manifest["rules"]:
            for relative_path, markers in rule.get("required", {}).items():
                text = self._read_repo_file(relative_path)
                for marker in markers:
                    with self.subTest(rule=rule["id"], relative_path=relative_path, marker=marker):
                        self.assertIn(marker, text)

    def test_forbidden_stale_state_markers_are_absent(self):
        for rule in self.manifest["rules"]:
            for relative_path, markers in rule.get("forbidden", {}).items():
                text = self._read_repo_file(relative_path)
                for marker in markers:
                    with self.subTest(rule=rule["id"], relative_path=relative_path, marker=marker):
                        self.assertNotIn(marker, text)


if __name__ == "__main__":
    unittest.main()
