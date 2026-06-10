import hashlib
import json
import zipfile
from pathlib import Path

from api import server
import pytest

from core.blocksettings import blocksetting_file, load_blocksettings_manifest
from core.blocksettings_ai_generator import (
    BS_AI_VERSION,
    build_bsai_catalog,
    create_bsai_session,
    generate_bsai_project_pair,
    plan_bsai_session,
    resolve_bsai_download,
    save_bsai_candidate,
)
from core.config_loader import ROOT


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _assert_public_safe(payload: dict) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    assert r"C:\\" not in raw
    assert "token=" not in raw.casefold()
    assert "secret" not in raw.casefold()
    assert "localPath" not in raw


def _session_id(payload: dict) -> str:
    assert payload["ok"] is True
    return payload["session"]["sessionId"]


def test_bsai_catalog_reports_safe_version_policy(tmp_path: Path):
    catalog = build_bsai_catalog(tmp_path)

    assert catalog["ok"] is True
    policy = catalog["catalog"]["versionPolicy"]
    assert policy["officialResourcesImmutable"] is True
    assert policy["capa1Default"] == "v6"
    assert policy["capa2Default"] == "BS_Filtros_v6"
    assert policy["capa2D1Default"] == "BS_Filtros_v6_D1"
    assert policy["filtersV7"] == "explicitBaseCanonicalId_only"
    _assert_public_safe(catalog)


def test_bsai_candidate_preserves_official_manifest_hashes_and_writes_local_sqb(tmp_path: Path):
    before = {
        entry["canonicalId"]: _sha256_file(blocksetting_file(entry))
        for entry in load_blocksettings_manifest()["entries"]
    }
    created = create_bsai_session(tmp_path, {"prompt": "filtros H1 con ADX para EURUSD largo"})
    session_id = _session_id(created)

    candidate = save_bsai_candidate(tmp_path, session_id, {})

    after = {
        entry["canonicalId"]: _sha256_file(blocksetting_file(entry))
        for entry in load_blocksettings_manifest()["entries"]
    }
    assert before == after
    assert candidate["ok"] is True
    entry = candidate["candidate"]["entry"]
    assert entry["canonicalId"].startswith("BSAI_Filtros_L2_H1_from_BS_Filtros_v6_r")
    assert entry["baseCanonicalId"] == "BS_Filtros_v6"
    assert entry["promotionState"] == "local_candidate"
    assert entry["sourceVersionPolicy"] == "filters_default_v6_v6_d1_v7_explicit_only"
    assert resolve_bsai_download(tmp_path, candidate["candidate"]["artifactId"]).is_file()
    with zipfile.ZipFile(resolve_bsai_download(tmp_path, candidate["candidate"]["artifactId"])) as archive:
        assert "config.xml" in archive.namelist()
    _assert_public_safe(candidate)


def test_bsai_local_candidate_cannot_impersonate_official_name(tmp_path: Path):
    candidate_dir = tmp_path / ".local" / "blocksettings_ai" / "candidates"
    candidate_dir.mkdir(parents=True)
    fake_official = candidate_dir / "BS_Filtros_v6.sqb"
    fake_official.write_bytes(b"not-a-real-sqb")

    with pytest.raises(ValueError, match="BSAI namespace"):
        blocksetting_file({
            "canonicalId": "BS_Filtros_v6",
            "filename": "BS_Filtros_v6.sqb",
            "sourceScope": "local_candidate",
            "promotionState": "local_candidate",
            "localPath": str(fake_official),
            "candidateRoot": str(candidate_dir),
        })


def test_bsai_filters_v7_requires_explicit_base(tmp_path: Path):
    h1 = create_bsai_session(tmp_path, {"prompt": "filtros H1 con ADX"})
    h1_plan = plan_bsai_session(tmp_path, _session_id(h1), {})
    assert h1_plan["baseBlockSetting"]["canonicalId"] == "BS_Filtros_v6"

    d1 = create_bsai_session(tmp_path, {"prompt": "filtros D1 con ADX"})
    d1_plan = plan_bsai_session(tmp_path, _session_id(d1), {})
    assert d1_plan["baseBlockSetting"]["canonicalId"] == "BS_Filtros_v6_D1"

    blocked = create_bsai_session(tmp_path, {
        "prompt": "filtros H1 con ADX",
        "blocksetting": "BS_Filtros_v7_H1",
    })
    assert blocked["ok"] is False
    assert blocked["error"] == "filters_v7_requires_explicit_base_canonical_id"

    explicit = create_bsai_session(tmp_path, {
        "prompt": "filtros H1 con ADX",
        "explicitBaseCanonicalId": "BS_Filtros_v7_H1",
    })
    explicit_plan = plan_bsai_session(tmp_path, _session_id(explicit), {})
    assert explicit_plan["baseBlockSetting"]["canonicalId"] == "BS_Filtros_v7_H1"
    assert explicit_plan["recipe"]["sourceVersionPolicy"] == "explicit_base_preserve_official_v6_v7"

    mismatched = create_bsai_session(tmp_path, {
        "prompt": "filtros D1 con ADX",
        "explicitBaseCanonicalId": "BS_Filtros_v7_H1",
    })
    mismatched_plan = plan_bsai_session(tmp_path, _session_id(mismatched), {})
    assert mismatched_plan["ok"] is False
    assert mismatched_plan["error"] == "explicit_base_timeframe_mismatch"


def test_bsai_project_pair_injects_candidate_only_on_matching_layer(tmp_path: Path):
    created = create_bsai_session(tmp_path, {"prompt": "volatilidad ATR EURUSD H1 long"})
    session_id = _session_id(created)
    saved = save_bsai_candidate(tmp_path, session_id, {})
    assert saved["ok"] is True
    output_dir = tmp_path / "out"
    output_dir.mkdir()

    result = generate_bsai_project_pair(
        tmp_path,
        session_id,
        template_capa1=str(ROOT / "templates" / "Capa1_Long.cfx"),
        template_capa2=str(ROOT / "templates" / "Capa2_Base.cfx"),
        output_dir=str(output_dir),
        sqx_db_path=None,
    )

    assert result["ok"] is True
    assert result["results"]["capa1"]["blocksetting"]["sourceScope"] == "local_candidate"
    assert result["results"]["capa1"]["blocksetting"]["baseCanonicalId"] == "BS_Volatilidad_v6_intraday_v6"
    assert result["results"]["capa2"]["blocksetting"]["canonicalId"] == "BS_Filtros_v6"
    for item in result["files"]:
        assert (output_dir / item["name"]).is_file()
        assert item["downloadUrl"].startswith("/api/output/download/")
    _assert_public_safe(result)


def test_bsai_routes_are_local_operator_only_and_safe():
    client = server.app.test_client()

    catalog = client.get("/api/blocksettings/ai/catalog")
    assert catalog.status_code == 200
    data = catalog.get_json()
    assert data["version"] == BS_AI_VERSION
    _assert_public_safe(data)

    blocked_remote = client.get(
        "/api/blocksettings/ai/catalog",
        base_url="https://app.sqxedgesuite.org",
        headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert blocked_remote.status_code == 403
    assert blocked_remote.get_json()["error"] == "local_operator_required"

    blocked_private = client.post(
        "/api/blocksettings/ai/sessions",
        json={"prompt": r"usa C:\Users\Operator\secret token=abcdefghi"},
    )
    assert blocked_private.status_code == 400
    assert blocked_private.get_json()["error"] == "prompt_not_public_safe"

    blocked_template = client.post(
        "/api/blocksettings/ai/sessions/bsai_missing/generate-project",
        json={"template_capa1": r"C:\tmp\unsafe.cfx"},
    )
    assert blocked_template.status_code == 400
    assert blocked_template.get_json()["error"] == "client_path_fields_blocked"


def test_bsai_output_guard_blocks_sqx_host_dirs(tmp_path: Path):
    sqx_root = tmp_path / "SQX_144_Full"
    cfg = {
        "sqx_path": str(sqx_root),
        "sqx_data_db": str(sqx_root / "user" / "data" / "data.db"),
        "sqx_projects_dir": str(sqx_root / "user" / "projects"),
        "output_dir": str(sqx_root / "user" / "projects"),
    }
    with pytest.raises(ValueError, match="bsai_output_dir_blocked"):
        server.resolve_bsai_output_dir(cfg)
