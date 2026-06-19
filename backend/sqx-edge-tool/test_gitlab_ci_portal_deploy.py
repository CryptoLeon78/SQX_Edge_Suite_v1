"""Smoke/regresion del job deploy-portal en .gitlab-ci.yml."""
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
CI = yaml.safe_load((ROOT / ".gitlab-ci.yml").read_text(encoding="utf-8"))
PKG = json.loads((ROOT / "templates/SQX_Edge_Tester_Portal/package.json").read_text(encoding="utf-8"))


def test_deploy_stage_present():
    assert "deploy" in CI.get("stages", [])


def test_deploy_portal_job_shape():
    job = CI.get("deploy-portal")
    assert job, "deploy-portal job missing"
    assert job.get("stage") == "deploy"
    assert str(job.get("image", "")).startswith("node:")
    script = "\n".join(job.get("script", []))
    assert "cf:deploy" in script
    assert "/api/health" in script


def test_deploy_portal_default_branch_only():
    assert "CI_DEFAULT_BRANCH" in str(CI.get("deploy-portal", {}).get("rules", []))


def test_cf_deploy_script_exists():
    assert "cf:deploy" in PKG.get("scripts", {})
