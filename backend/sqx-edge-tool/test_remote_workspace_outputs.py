import json
from pathlib import Path
from unittest.mock import patch

from api import server
from core.remote_access import SESSION_COOKIE_NAME, create_signed_session, email_hash
from core.remote_workspace_outputs import REMOTE_WORKSPACE_OUTPUT_VERSION
from core.remote_workspaces import workspace_id_from_identity_hash


def _context_ref_for_test(client, email: str) -> tuple[str, dict[str, str]]:
    headers = {"User-Agent": "pytest-remote-output", "Cf-Access-Authenticated-User-Email": email}
    probe = client.get("/api/remote/access-control/status", headers=headers, base_url="https://localhost")
    assert probe.status_code == 200
    return probe.get_json()["accessControl"]["contextRef"], headers


def _authorized_client(tmp_path, monkeypatch, email: str = "remote-output@example.invalid"):
    store = {
        "schemaVersion": "remote-entitlements-v1",
        "grants": [{
            "emailHash": email_hash(email),
            "entitlementKind": "paid_subscription",
            "status": "active",
            "featureScope": "full",
        }],
    }
    store_path = tmp_path / "remote_entitlements.local.json"
    workspaces_root = tmp_path / "workspaces"
    store_path.write_text(json.dumps(store), encoding="utf-8")
    monkeypatch.setenv("SQX_REMOTE_ENTITLEMENTS_PATH", str(store_path))
    monkeypatch.setenv("SQX_REMOTE_SESSION_SECRET", "s" * 40)
    monkeypatch.setenv("SQX_REMOTE_WORKSPACES_ROOT", str(workspaces_root))
    monkeypatch.setenv("SQX_REMOTE_ACCESS_CONTROL_PATH", str(tmp_path / "access_control.local.json"))
    monkeypatch.setenv("SQX_REMOTE_ACCESS_CONTROL_EVENTS_PATH", str(tmp_path / "access_events.local.jsonl"))
    client = server.app.test_client()
    context_ref, headers = _context_ref_for_test(client, email)
    signed = create_signed_session(
        email,
        {"kind": "paid_subscription", "grant_id": "paid-1", "feature_scope": "full"},
        access_context_ref=context_ref,
    )
    client.set_cookie(SESSION_COOKIE_NAME, signed["token"])
    return client, headers, workspaces_root


def _cfg(tmp_path: Path) -> dict:
    template = tmp_path / "template.cfx"
    template.write_text("template", encoding="utf-8")
    global_output = tmp_path / "global-output"
    global_output.mkdir()
    (global_output / "Global_Old.cfx").write_text("old", encoding="utf-8")
    return {
        "template_capa1": str(template),
        "template_capa2": str(template),
        "output_dir": str(global_output),
        "sqx_data_db": "",
        "darwinex_suffix": "_darwinex",
        "asset_aliases": {},
    }


def _costs(asset: str = "EURUSD") -> dict:
    return {
        "source": "fallback",
        "symbol": asset + "_darwinex",
        "spread": 1,
        "swap_long": -1,
        "swap_short": 0,
        "data_available": False,
        "data_rows": 0,
    }


def test_remote_generate_custom_writes_to_workspace_outputs_and_redacts_local_paths(tmp_path, monkeypatch):
    client, headers, workspaces_root = _authorized_client(tmp_path, monkeypatch)
    cfg = _cfg(tmp_path)

    def fake_generate(mining, *, output_dir, **_kwargs):
        target = Path(output_dir) / "Remote_Custom.cfx"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("remote", encoding="utf-8")
        return str(target)

    with patch.object(server, "load_config", return_value=cfg), \
            patch.object(server, "generate_project", side_effect=fake_generate) as gen, \
            patch.object(server, "resolve_costs", return_value=_costs()):
        response = client.post(
            "/api/generate-custom",
            json={"asset": "EURUSD", "tf": "H1", "bs": "BS_Tendencia_v6", "dir": "long", "capa": 1},
            headers=headers,
            base_url="https://localhost",
        )

    data = response.get_json()
    assert response.status_code == 200
    assert data["ok"] is True
    assert data["output"]["version"] == REMOTE_WORKSPACE_OUTPUT_VERSION
    assert data["output"]["scope"] == "remote_workspace"
    assert data["output_path"] == "workspace://outputs/Remote_Custom.cfx"
    assert data["privacy"]["local_paths_returned"] is False
    assert str(cfg["output_dir"]) not in json.dumps(data)
    output_dir = Path(gen.call_args.kwargs["output_dir"])
    output_dir.relative_to(workspaces_root)
    assert output_dir.name == "outputs"
    assert (output_dir / "Remote_Custom.cfx").is_file()


def test_remote_output_lists_workspace_outputs_not_global_output(tmp_path, monkeypatch):
    client, headers, _workspaces_root = _authorized_client(tmp_path, monkeypatch)
    cfg = _cfg(tmp_path)

    def fake_generate(_mining, *, output_dir, **_kwargs):
        target = Path(output_dir) / "Workspace_Only.cfx"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("remote", encoding="utf-8")
        return str(target)

    with patch.object(server, "load_config", return_value=cfg), \
            patch.object(server, "generate_project", side_effect=fake_generate), \
            patch.object(server, "resolve_costs", return_value=_costs()):
        client.post(
            "/api/generate-custom",
            json={"asset": "EURUSD", "tf": "H1", "capa": 1},
            headers=headers,
            base_url="https://localhost",
        )
        listed = client.get("/api/output", headers=headers, base_url="https://localhost")

    data = listed.get_json()
    assert listed.status_code == 200
    assert data["scope"] == "remote_workspace"
    assert data["output_dir"] == "workspace://outputs"
    assert data["privacy"]["local_paths_returned"] is False
    assert [item["name"] for item in data["files"]] == ["Workspace_Only.cfx"]
    assert "Global_Old.cfx" not in json.dumps(data)
    assert str(cfg["output_dir"]) not in json.dumps(data)


def test_remote_output_override_is_blocked(tmp_path, monkeypatch):
    client, headers, _workspaces_root = _authorized_client(tmp_path, monkeypatch)
    cfg = _cfg(tmp_path)

    with patch.object(server, "load_config", return_value=cfg), \
            patch.object(server, "generate_project") as gen:
        response = client.post(
            "/api/generate-custom",
            json={"asset": "EURUSD", "tf": "H1", "capa": 1, "output": cfg["output_dir"]},
            headers=headers,
            base_url="https://localhost",
        )

    data = response.get_json()
    assert response.status_code == 403
    assert data["error"] == "remote_output_override_blocked"
    assert data["privacy"]["local_paths_returned"] is False
    assert str(cfg["output_dir"]) not in json.dumps(data)
    gen.assert_not_called()


def test_remote_project_generator_requires_app_session_before_output_access(tmp_path, monkeypatch):
    store_path = tmp_path / "remote_entitlements.local.json"
    store_path.write_text(json.dumps({"schemaVersion": "remote-entitlements-v1", "grants": []}), encoding="utf-8")
    monkeypatch.setenv("SQX_REMOTE_ENTITLEMENTS_PATH", str(store_path))
    monkeypatch.setenv("SQX_REMOTE_SESSION_SECRET", "s" * 40)
    client = server.app.test_client()
    headers = {"Cf-Access-Authenticated-User-Email": "viewer@example.invalid"}

    output = client.get("/api/output", headers=headers, base_url="https://localhost")
    generate = client.post(
        "/api/generate-custom",
        json={"asset": "EURUSD", "tf": "H1", "capa": 1},
        headers=headers,
        base_url="https://localhost",
    )

    assert output.status_code == 403
    assert output.get_json()["error"] == "remote_session_required"
    assert generate.status_code == 403
    assert generate.get_json()["error"] == "remote_session_required"


def test_remote_workspace_outputs_are_separate_per_identity(tmp_path, monkeypatch):
    first, first_headers, workspaces_root = _authorized_client(tmp_path, monkeypatch, "first-output@example.invalid")
    cfg = _cfg(tmp_path)

    def fake_generate(mining, *, output_dir, **_kwargs):
        name = f"{mining.asset}_{mining.tf}.cfx"
        target = Path(output_dir) / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(name, encoding="utf-8")
        return str(target)

    with patch.object(server, "load_config", return_value=cfg), \
            patch.object(server, "generate_project", side_effect=fake_generate), \
            patch.object(server, "resolve_costs", return_value=_costs()):
        first.post(
            "/api/generate-custom",
            json={"asset": "XAUUSD", "tf": "H1", "capa": 1},
            headers=first_headers,
            base_url="https://localhost",
        )

    second, second_headers, _ = _authorized_client(tmp_path, monkeypatch, "second-output@example.invalid")
    with patch.object(server, "load_config", return_value=cfg):
        second_listed = second.get("/api/output", headers=second_headers, base_url="https://localhost")

    first_workspace = workspaces_root / workspace_id_from_identity_hash(email_hash("first-output@example.invalid"))
    second_workspace = workspaces_root / workspace_id_from_identity_hash(email_hash("second-output@example.invalid"))
    assert (first_workspace / "outputs" / "XAUUSD_H1.cfx").is_file()
    assert second_listed.get_json()["files"] == []
    assert not (second_workspace / "outputs" / "XAUUSD_H1.cfx").exists()
