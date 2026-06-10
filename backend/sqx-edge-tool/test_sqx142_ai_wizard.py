import json
import zipfile
from pathlib import Path
from unittest.mock import patch

from api import server
from core.sqx142_ai_wizard import (
    AI_WIZARD_VERSION,
    SPEC_TYPE,
    SUPPORTED_ARCHETYPES,
    XML_ENTRY,
    build_ai_wizard_spec,
    build_ai_wizard_status,
    generate_draft_sqx,
    resolve_draft_download,
)


MINIMAL_XML = """<?xml version="1.0" encoding="UTF-8"?>
<StrategyFile Version="3.9.130">
  <options>
    <StrategyName>New strategy</StrategyName>
    <Date>01/08/2020 08:24</Date>
  </options>
  <Strategy name="" engine="MetaTrader">
    <Description />
  </Strategy>
</StrategyFile>
"""


def _fake_sqx_root(tmp_path: Path) -> Path:
    root = tmp_path / "sqx142"
    examples = root / "internal" / "web" / "AlgoWizard" / "examples"
    examples.mkdir(parents=True)
    for meta in SUPPORTED_ARCHETYPES.values():
        with zipfile.ZipFile(examples / meta["template"], "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\n")
            archive.writestr(XML_ENTRY, MINIMAL_XML)
    return root


def _assert_public_safe(payload: dict) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    assert r"C:\\" not in raw
    assert "Crack" not in raw
    assert "OPENAI_API_KEY" not in raw
    assert "secret" not in raw.casefold()
    assert "token=" not in raw.casefold()


def test_ai_wizard_spec_accepts_supported_prompt_without_raw_prompt():
    payload = build_ai_wizard_spec({"prompt": "EMA cross trend-following EURUSD H1 with SL/TP"})

    assert payload["ok"] is True
    assert payload["version"] == AI_WIZARD_VERSION
    spec = payload["data"]["spec"]
    assert spec["type"] == SPEC_TYPE
    assert spec["status"] == "ready"
    assert spec["asset"] == "EURUSD"
    assert spec["timeframe"] == "H1"
    assert spec["archetype"] == "ema_cross"
    assert spec["risk"]["manualReviewRequired"] is True
    assert payload["data"]["strategyBuilderPackage"]["type"] == "sqx-edge.strategy-builder-package"
    assert "prompt" not in json.dumps(spec, ensure_ascii=False).casefold()
    _assert_public_safe(payload)


def test_ai_wizard_spec_blocks_empty_unsupported_and_private_text():
    empty = build_ai_wizard_spec({"prompt": ""})
    assert empty["ok"] is False
    assert empty["error"] == "prompt_required"

    unsupported = build_ai_wizard_spec({"prompt": "Use a neural transformer order flow engine"})
    assert unsupported["ok"] is False
    assert unsupported["error"] == "blocked_unsupported_rule"

    private = build_ai_wizard_spec({"prompt": r"EMA cross from C:\Users\Ivan SQX\secret token=abcdef"})
    assert private["ok"] is False
    assert private["error"] == "prompt_not_public_safe"
    _assert_public_safe(private)


def test_ai_wizard_draft_generates_valid_sqx_under_output_only(tmp_path):
    sqx_root = _fake_sqx_root(tmp_path)
    output_dir = tmp_path / "drafts"

    payload = generate_draft_sqx(
        {"prompt": "EMA cross trend-following USDJPY H4 with SL/TP"},
        project_root=tmp_path,
        sqx142_root=sqx_root,
        output_dir=output_dir,
    )

    assert payload["ok"] is True
    draft = payload["data"]["draft"]
    path = output_dir / draft["fileName"]
    assert path.is_file()
    assert zipfile.is_zipfile(path)
    with zipfile.ZipFile(path) as archive:
        xml = archive.read(XML_ENTRY).decode("utf-8")
    assert "SQXEdgeAI_USDJPY_H4" in xml
    assert "SQX Edge AI Wizard draft" in xml
    assert "manual_algowizard_review_required" in payload["data"]["strategyBuilderPackage"]["guardrails"]
    _assert_public_safe(payload)


def test_ai_wizard_status_and_download_resolver_are_safe(tmp_path):
    sqx_root = _fake_sqx_root(tmp_path)
    status = build_ai_wizard_status(tmp_path, sqx_root)
    assert status["ok"] is True
    assert status["data"]["provider"]["id"] == "ollama"
    assert status["data"]["provider"]["openai"]["enabled"] is False
    _assert_public_safe(status)

    output_dir = tmp_path / "out"
    output_dir.mkdir()
    good = output_dir / "draft.sqx"
    good.write_bytes(b"PK\x05\x06" + b"\x00" * 18)
    assert resolve_draft_download(tmp_path, "draft.sqx", output_dir) == good
    assert resolve_draft_download(tmp_path, "../draft.sqx", output_dir) is None
    assert resolve_draft_download(tmp_path, "draft.txt", output_dir) is None
    assert resolve_draft_download(tmp_path, "missing.sqx", output_dir) is None


def test_ai_wizard_routes_are_local_operator_only_and_path_safe(tmp_path):
    client = server.app.test_client()
    safe_status = {
        "ok": True,
        "version": AI_WIZARD_VERSION,
        "data": {"provider": {"id": "ollama"}},
        "privacy": {"local_paths_returned": False},
    }
    with patch.object(server, "build_ai_wizard_status", return_value=safe_status):
        response = client.get("/api/sqx142/ai-wizard/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["version"] == AI_WIZARD_VERSION
    _assert_public_safe(data)

    blocked = client.get(
        "/api/sqx142/ai-wizard/status",
        base_url="https://app.sqxedgesuite.org",
        headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert blocked.status_code == 403
    assert blocked.get_json()["error"] == "local_operator_required"

    plan_ok = client.post("/api/sqx142/ai-wizard/plan", json={"prompt": "EMA cross EURUSD H1"})
    assert plan_ok.status_code == 200
    plan_blocked = client.post("/api/sqx142/ai-wizard/plan", json={"prompt": ""})
    assert plan_blocked.status_code == 400

    draft_file = tmp_path / "draft.sqx"
    draft_file.write_bytes(b"mock")
    with patch.object(server, "resolve_draft_download", return_value=draft_file):
        download = client.get("/api/sqx142/ai-wizard/draft-sqx/download/draft.sqx")
    assert download.status_code == 200

    with patch.object(server, "resolve_draft_download", return_value=None):
        missing = client.get("/api/sqx142/ai-wizard/draft-sqx/download/..%2Fmissing.sqx")
    assert missing.status_code == 404


def test_ai_wizard_draft_route_delegates_status_codes():
    client = server.app.test_client()
    ok_report = {"ok": True, "version": AI_WIZARD_VERSION, "data": {"draft": {"fileName": "x.sqx"}}, "privacy": {"local_paths_returned": False}}
    fail_report = {"ok": False, "version": AI_WIZARD_VERSION, "error": "blocked_unsupported_rule", "privacy": {"local_paths_returned": False}}
    with patch.object(server, "generate_draft_sqx", return_value=ok_report):
        ok = client.post("/api/sqx142/ai-wizard/draft-sqx", json={"prompt": "EMA cross EURUSD H1"})
    with patch.object(server, "generate_draft_sqx", return_value=fail_report):
        fail = client.post("/api/sqx142/ai-wizard/draft-sqx", json={"prompt": "bad"})
    assert ok.status_code == 200
    assert fail.status_code == 400
