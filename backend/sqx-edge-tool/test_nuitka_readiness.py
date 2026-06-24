"""
test_nuitka_readiness.py — Nuitka packaging readiness tests (ADR-0003, Phase 2).

Tests run on any OS (CI / Linux sandbox); no Nuitka binary required.
"""
from __future__ import annotations

import importlib
import json
import os
import py_compile
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOL_ROOT = PROJECT_ROOT / "backend" / "sqx-edge-tool"
PACKAGING_ROOT = PROJECT_ROOT / "packaging"

# Ensure packaging/ is importable
if str(PACKAGING_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGING_ROOT))

import build_inputs  # noqa: E402  (packaging/build_inputs.py)
from core.app_paths import app_root, project_root  # noqa: E402


class AppPathsRegressionTest(unittest.TestCase):
    """app_root() and project_root() must be bit-for-bit identical to the old
    Path(__file__).resolve().parentsN expressions when SQX_APP_ROOT is absent."""

    def setUp(self):
        self._saved = os.environ.pop("SQX_APP_ROOT", None)
        # Force re-evaluation of module-level cache (functions are not cached,
        # but _HERE is fixed at import time — that's the invariant we test).

    def tearDown(self):
        if self._saved is not None:
            os.environ["SQX_APP_ROOT"] = self._saved
        else:
            os.environ.pop("SQX_APP_ROOT", None)

    def test_app_root_fallback_matches_original_expression(self):
        """Without SQX_APP_ROOT, app_root() == Path(core/app_paths.py).parents[1]."""
        from core import app_paths as _mod
        expected = _mod._HERE.parents[1]
        self.assertEqual(app_root(), expected)
        self.assertTrue(app_root().is_dir(), "app_root() must point to an existing directory")

    def test_project_root_fallback_matches_original_expression(self):
        """Without SQX_APP_ROOT, project_root() == Path(core/app_paths.py).parents[3]."""
        from core import app_paths as _mod
        expected = _mod._HERE.parents[3]
        self.assertEqual(project_root(), expected)
        self.assertTrue(project_root().is_dir(), "project_root() must point to an existing directory")

    def test_app_root_env_override(self):
        """With SQX_APP_ROOT set, app_root() returns that path."""
        os.environ["SQX_APP_ROOT"] = str(TOOL_ROOT)
        self.assertEqual(app_root(), TOOL_ROOT)

    def test_project_root_env_override(self):
        """With SQX_APP_ROOT set, project_root() returns that path."""
        os.environ["SQX_APP_ROOT"] = str(PROJECT_ROOT)
        self.assertEqual(project_root(), PROJECT_ROOT)

    def test_app_root_resolves_to_sqx_edge_tool(self):
        """app_root() must resolve to backend/sqx-edge-tool/ in dev."""
        self.assertEqual(app_root().name, "sqx-edge-tool")

    def test_project_root_contains_packaging_dir(self):
        """project_root() must resolve to the repo root (contains packaging/)."""
        self.assertTrue((project_root() / "packaging").is_dir())


class AppMainSyntaxTest(unittest.TestCase):
    APP_MAIN = PACKAGING_ROOT / "app_main.py"

    def test_app_main_compiles_clean(self):
        py_compile.compile(str(self.APP_MAIN), doraise=True)

    def test_app_main_defines_frozen_guard_and_entry(self):
        source = self.APP_MAIN.read_text(encoding="utf-8")
        self.assertIn("_set_app_root_if_frozen", source)
        self.assertIn("SQX_APP_ROOT", source)
        self.assertIn("__compiled__", source)
        self.assertIn("def main(", source)

    def test_app_main_imports_from_api_server(self):
        source = self.APP_MAIN.read_text(encoding="utf-8")
        self.assertIn("from api.server import", source)

    def test_build_inputs_compiles_clean(self):
        py_compile.compile(str(PACKAGING_ROOT / "build_inputs.py"), doraise=True)

    def test_nuitka_build_ps1_exists(self):
        self.assertTrue((PACKAGING_ROOT / "nuitka_build.ps1").is_file())

    def test_nuitka_build_md_exists(self):
        self.assertTrue((PACKAGING_ROOT / "NUITKA_BUILD.md").is_file())


class BuildInputsTest(unittest.TestCase):
    """Test packaging/build_inputs.run() directly (no subprocess needed)."""

    def _prod_manifest_path(self, tmp_path: Path) -> Path:
        """Write a manifest with a real prod kid to tmp_path; return the path."""
        real = json.loads(build_inputs.MANIFEST_SRC.read_text(encoding="utf-8"))
        real["licensing"]["publicKey"]["kid"] = "sqx-prod-2026-06"
        p = tmp_path / "product_manifest.json"
        p.write_text(json.dumps(real), encoding="utf-8")
        return p

    def test_H2_reports_blocker_for_placeholder_kid(self):
        """run() returns exit code 2 when the current manifest has a placeholder kid."""
        import tempfile, io, contextlib
        with tempfile.TemporaryDirectory() as td:
            staging = Path(td) / "staging"
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                rc = build_inputs.run(staging)
        self.assertEqual(rc, 2)
        self.assertIn("placeholder", buf.getvalue().lower())

    def test_prod_manifest_writes_channel_free(self):
        """run() writes channel=free and returns 0 when kid is not a placeholder."""
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            prod_manifest = self._prod_manifest_path(td_path)
            original_src = build_inputs.MANIFEST_SRC
            try:
                build_inputs.MANIFEST_SRC = prod_manifest
                staging = td_path / "staging"
                rc = build_inputs.run(staging)
                # Read output inside the with block before the temp dir is cleaned up
                out = json.loads((staging / "product_manifest.json").read_text(encoding="utf-8"))
            finally:
                build_inputs.MANIFEST_SRC = original_src

        self.assertEqual(rc, 0)
        self.assertEqual(out["build"]["channel"], "free")
        self.assertNotIn("placeholder", out["licensing"]["publicKey"]["kid"].lower())

    def test_prod_manifest_does_not_mutate_source(self):
        """run() must not modify the on-disk source manifest."""
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            prod_manifest = self._prod_manifest_path(td_path)
            before = json.loads(prod_manifest.read_text(encoding="utf-8"))
            original_src = build_inputs.MANIFEST_SRC
            try:
                build_inputs.MANIFEST_SRC = prod_manifest
                build_inputs.run(td_path / "staging")
            finally:
                build_inputs.MANIFEST_SRC = original_src
            # Read inside with block before temp dir is cleaned up
            after = json.loads(prod_manifest.read_text(encoding="utf-8"))
            self.assertEqual(before, after)


class DataDirsExistTest(unittest.TestCase):
    """The directories that nuitka_build.ps1 bundles must exist."""

    def test_app_dir_exists_at_project_root(self):
        self.assertTrue((PROJECT_ROOT / "app").is_dir())

    def test_templates_dir_exists_at_tool_root(self):
        self.assertTrue((TOOL_ROOT / "templates").is_dir())

    def test_config_dir_exists_at_tool_root(self):
        self.assertTrue((TOOL_ROOT / "config").is_dir())

    def test_product_manifest_is_readable(self):
        manifest_path = TOOL_ROOT / "config" / "product_manifest.json"
        self.assertTrue(manifest_path.is_file())
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertIn("build", data)
        self.assertIn("licensing", data)


class NuikaDevSwitchTest(unittest.TestCase):
    """nuitka_build.ps1 -Dev switch: present in source, release mode still requires harden."""

    PS1 = PACKAGING_ROOT / "nuitka_build.ps1"

    def _source(self) -> str:
        return self.PS1.read_text(encoding="utf-8-sig")

    def test_dev_param_is_declared(self):
        """The script declares a [switch]$Dev parameter."""
        self.assertIn("[switch]$Dev", self._source())

    def test_dev_branch_prints_insecure_warning(self):
        """When -Dev is taken, script prints the INSECURE DEV BUILD string."""
        self.assertIn("INSECURE DEV BUILD", self._source())
        self.assertIn("NO DISTRIBUIR", self._source())

    def test_dev_branch_skips_build_inputs(self):
        """In the -Dev branch, build_inputs.py is NOT called (it's in the else branch)."""
        source = self._source()
        # The actual invocation uses Join-Path + the script path — only in else block.
        # Comments may also contain "build_inputs.py", so we look for the call expression.
        call_marker = '"packaging\\build_inputs.py"'
        else_pos = source.index("} else {")
        call_pos = source.index(call_marker)
        self.assertGreater(call_pos, else_pos,
                           "build_inputs.py invocation must be inside the else (non-Dev) branch")

    def test_release_mode_calls_build_inputs(self):
        """Without -Dev, the script calls build_inputs.py for hardening."""
        self.assertIn("build_inputs.py", self._source())

    def test_release_mode_verifies_channel_free(self):
        """Without -Dev, the script checks channel == 'free' before compiling."""
        self.assertIn("-ne \"free\"", self._source())

    def test_dev_mode_uses_repo_manifest(self):
        """In -Dev mode, the script uses the repo config/product_manifest.json."""
        self.assertIn("config\\product_manifest.json", self._source())

    def test_manifest_to_bundle_variable_used_in_nuitka_call(self):
        """Both modes pass $ManifestToBundle to the Nuitka --include-data-files flag."""
        self.assertIn("$ManifestToBundle=config/product_manifest.json", self._source())

    def test_pythonpath_set_to_tool_root_before_nuitka(self):
        """PYTHONPATH is set to $ToolRoot so Nuitka resolves api/core imports."""
        source = self._source()
        self.assertIn("$env:PYTHONPATH = $ToolRoot", source)
        # Must appear before the Nuitka invocation
        pythonpath_pos = source.index("$env:PYTHONPATH = $ToolRoot")
        nuitka_pos = source.index("python -m nuitka")
        self.assertLess(pythonpath_pos, nuitka_pos,
                        "$env:PYTHONPATH must be set before the Nuitka invocation")

    def test_no_hardcoded_dist_folder_name(self):
        """The .dist folder must be located dynamically, not hardcoded as a PS string."""
        source = self._source()
        # The name may appear in prose comments, but must not appear as a quoted PS string
        # (i.e. "$DistDir = '...exe.dist'" or Join-Path "...exe.dist").
        self.assertNotIn('"SQX_Edge_Tool.exe.dist"', source)
        self.assertNotIn("'SQX_Edge_Tool.exe.dist'", source)
        # The dynamic lookup must use Get-ChildItem with the exe filter
        self.assertIn('Get-ChildItem -Recurse -Filter "SQX_Edge_Tool.exe"', source)
        self.assertIn("$exe.Directory.FullName", source)

    def test_assume_yes_for_downloads_flag_present(self):
        """Nuitka is invoked with --assume-yes-for-downloads to avoid interactive prompts."""
        self.assertIn("--assume-yes-for-downloads", self._source())


class PackagingScriptsAsciiTest(unittest.TestCase):
    """All *.ps1 files under packaging/ must be pure ASCII (every byte < 128).

    PowerShell 5.1 on Windows reads files without BOM as CP1252.  Any byte
    above 127 (em-dash, box-drawing, accented char, etc.) will cause a parse
    error before the script executes.
    """

    def _ps1_files(self):
        return list(PACKAGING_ROOT.glob("*.ps1"))

    def test_at_least_one_ps1_exists(self):
        self.assertGreater(len(self._ps1_files()), 0,
                           "No *.ps1 files found in packaging/ - check PACKAGING_ROOT")

    def test_all_packaging_ps1_are_pure_ascii(self):
        failures = []
        for ps1 in self._ps1_files():
            data = ps1.read_bytes()
            bad = [(i + 1, b) for i, b in enumerate(data) if b > 127]
            if bad:
                sample = bad[:3]
                failures.append(
                    f"{ps1.name}: {len(bad)} non-ASCII byte(s); "
                    f"first offsets: {[(off, hex(b)) for off, b in sample]}"
                )
        self.assertEqual(failures, [],
                         "packaging/ PS1 files with non-ASCII bytes:\n" + "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
