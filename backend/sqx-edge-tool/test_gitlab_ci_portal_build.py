"""Smoke/regresion del job portal-build en .gitlab-ci.yml (sin deploy)."""
from pathlib import Path
import yaml

CI_PATH = Path(__file__).resolve().parents[2] / ".gitlab-ci.yml"
PORTAL_GLOB = "templates/SQX_Edge_Tester_Portal/**/*"


def _load():
    assert CI_PATH.exists(), f"missing {CI_PATH}"
    return yaml.safe_load(CI_PATH.read_text(encoding="utf-8"))


def test_gitlab_ci_parses():
    assert isinstance(_load(), dict)


def test_portal_stage_present():
    assert "portal" in _load().get("stages", [])


def test_portal_build_job_shape():
    job = _load().get("portal-build")
    assert job, "portal-build job missing"
    assert job.get("stage") == "portal"
    assert str(job.get("image", "")).startswith("node:")
    assert "opennextjs-cloudflare build" in "\n".join(job.get("script", []))


def test_portal_build_scoped_to_portal_changes():
    rules = _load().get("portal-build", {}).get("rules", [])
    changes = [c for r in rules for c in r.get("changes", [])]
    assert PORTAL_GLOB in changes
