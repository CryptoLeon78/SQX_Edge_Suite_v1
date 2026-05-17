import json

from api import server
from core.remote_access import SESSION_COOKIE_NAME, create_signed_session, email_hash
from core.remote_workspaces import workspace_id_from_identity_hash


def _context_ref_for_test(client, email: str):
    headers = {"User-Agent": "pytest-state-backup", "Cf-Access-Authenticated-User-Email": email}
    probe = client.get("/api/remote/access-control/status", headers=headers, base_url="https://localhost")
    assert probe.status_code == 200
    return probe.get_json()["accessControl"]["contextRef"], headers


def _authorized_client(tmp_path, monkeypatch, email: str):
    store = {
        "schemaVersion": "remote-entitlements-v1",
        "grants": [{
            "emailHash": email_hash(email),
            "entitlementKind": "paid_subscription",
            "status": "active",
            "featureScope": "full",
        }],
    }
    store_path = tmp_path / f"{email_hash(email)[:8]}_remote_entitlements.local.json"
    workspaces_root = tmp_path / "workspaces"
    store_path.write_text(json.dumps(store), encoding="utf-8")
    monkeypatch.setenv("SQX_REMOTE_ENTITLEMENTS_PATH", str(store_path))
    monkeypatch.setenv("SQX_REMOTE_SESSION_SECRET", "s" * 40)
    monkeypatch.setenv("SQX_REMOTE_WORKSPACES_ROOT", str(workspaces_root))
    monkeypatch.setenv("SQX_REMOTE_ACCESS_CONTROL_PATH", str(tmp_path / f"{email_hash(email)[:8]}_access_control.local.json"))
    monkeypatch.setenv("SQX_REMOTE_ACCESS_CONTROL_EVENTS_PATH", str(tmp_path / f"{email_hash(email)[:8]}_access_events.local.jsonl"))
    client = server.app.test_client()
    context_ref, headers = _context_ref_for_test(client, email)
    signed = create_signed_session(
        email,
        {"kind": "paid_subscription", "grant_id": "paid-1", "feature_scope": "full"},
        access_context_ref=context_ref,
    )
    client.set_cookie(SESSION_COOKIE_NAME, signed["token"])
    return client, headers, workspaces_root


def test_remote_state_backup_requires_session_for_tunnel_request(tmp_path, monkeypatch):
    client = server.app.test_client()
    headers = {"User-Agent": "pytest-state-backup", "Cf-Access-Authenticated-User-Email": "state-backup@example.invalid"}

    response = client.get("/api/state/backups", headers=headers, base_url="https://localhost")
    data = response.get_json()

    assert response.status_code == 403
    assert data["error"] == "remote_session_required"
    assert data["privacy"]["local_paths_returned"] is False


def test_remote_state_backup_roundtrip_uses_workspace_and_redacts(tmp_path, monkeypatch):
    email = "state-backup@example.invalid"
    client, headers, workspaces_root = _authorized_client(tmp_path, monkeypatch, email)

    response = client.post(
        "/api/state/backup",
        json={
            "sqx_plan_user_v1": {"minings": [{"num": 42, "asset": "XAUUSD"}]},
            "sqx_license_state_v1": {"secret": "must-not-persist"},
        },
        headers=headers,
        base_url="https://localhost",
    )
    created = response.get_json()

    assert response.status_code == 200
    assert created["ok"] is True
    assert created["version"] == "remote-state-backup-v1"
    assert created["scope"] == "remote_workspace"
    assert created["privacy"]["local_paths_returned"] is False
    assert "state-backup@example.invalid" not in json.dumps(created)

    workspace_id = workspace_id_from_identity_hash(email_hash(email))
    backup_path = workspaces_root / workspace_id / "config" / "state_backups" / created["filename"]
    assert backup_path.is_file()

    listed = client.get("/api/state/backups", headers=headers, base_url="https://localhost").get_json()
    assert listed["scope"] == "remote_workspace"
    assert listed["backups"][0]["name"] == created["filename"]
    assert listed["backups"][0]["location"] == "workspace://state-backups"
    assert "workspaces" not in json.dumps(listed)

    restored_response = client.get(
        f"/api/state/restore/{created['filename']}",
        headers=headers,
        base_url="https://localhost",
    )
    restored = restored_response.get_json()
    assert restored_response.status_code == 200
    assert restored["scope"] == "remote_workspace"
    assert restored["payload"]["data"]["sqx_plan_user_v1"]["minings"][0]["asset"] == "XAUUSD"
    assert "sqx_license_state_v1" not in restored["payload"]["data"]
    assert restored["payload"]["_meta"]["filtered_keys"] == ["sqx_license_state_v1"]
    assert "state-backup@example.invalid" not in json.dumps(restored)
    assert "workspaces" not in json.dumps(restored)


def test_remote_state_backups_are_separate_per_identity(tmp_path, monkeypatch):
    first, first_headers, _root = _authorized_client(tmp_path, monkeypatch, "first-state@example.invalid")
    first.post(
        "/api/state/backup",
        json={"sqx_plan_user_v1": {"minings": [{"asset": "EURUSD"}]}},
        headers=first_headers,
        base_url="https://localhost",
    )

    second, second_headers, _root = _authorized_client(tmp_path, monkeypatch, "second-state@example.invalid")
    listed = second.get("/api/state/backups", headers=second_headers, base_url="https://localhost").get_json()

    assert listed["scope"] == "remote_workspace"
    assert listed["backups"] == []
