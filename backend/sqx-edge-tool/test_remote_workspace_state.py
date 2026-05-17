import json

from api import server
from core.remote_access import SESSION_COOKIE_NAME, create_signed_session, email_hash
from core.remote_workspace_state import (
    REMOTE_WORKSPACE_STATE_DB,
    REMOTE_WORKSPACE_STATE_VERSION,
    read_workspace_state,
    write_workspace_state,
)
from core.remote_workspaces import derive_remote_workspace, workspace_id_from_identity_hash


def _session_status(email: str = "buyer@example.invalid") -> dict:
    identity_hash = email_hash(email)
    return {
        "ok": True,
        "session": {
            "active": True,
            "email_hash": identity_hash,
            "email_ref": "bu***@example.invalid",
            "entitlement_kind": "paid_subscription",
            "feature_scope": "full",
        },
        "entitlement": {"kind": "paid_subscription", "status": "active"},
        "access": {"allowed": True, "feature_scope": "full"},
        "privacy": {"session_token_returned": False},
    }


def _context_ref_for_test(client, email: str = "buyer@example.invalid"):
    headers = {"User-Agent": "pytest-remote-state", "Cf-Access-Authenticated-User-Email": email}
    probe = client.get("/api/remote/access-control/status", headers=headers, base_url="https://localhost")
    assert probe.status_code == 200
    return probe.get_json()["accessControl"]["contextRef"], headers


def _authorized_client(tmp_path, monkeypatch, email: str = "buyer@example.invalid"):
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
    monkeypatch.setenv("SQX_REMOTE_ACCESS_CONTROL_PATH", str(tmp_path / f"{email_hash(email)[:8]}_access_control.local.json"))
    monkeypatch.setenv("SQX_REMOTE_ACCESS_CONTROL_EVENTS_PATH", str(tmp_path / f"{email_hash(email)[:8]}_access_events.local.jsonl"))
    client = server.app.test_client()
    context_ref, headers = _context_ref_for_test(client, email=email)
    signed = create_signed_session(
        email,
        {"kind": "paid_subscription", "grant_id": "paid-1", "feature_scope": "full"},
        access_context_ref=context_ref,
    )
    client.set_cookie(SESSION_COOKIE_NAME, signed["token"])
    return client, headers, workspaces_root


def test_workspace_state_persists_allowed_keys_in_workspace_sqlite(tmp_path):
    context = derive_remote_workspace(_session_status(), create=True, root=tmp_path)
    result = write_workspace_state(context, {
        "sqx_plan_user_v1": {"minings": [{"num": 77, "asset": "XAUUSD"}], "phases": {}},
        "sqx_strategies_user_v1": [{"id": "S1"}],
        "sqx_license_state_v1": {"must": "not persist"},
    }, source="pytest")
    state = read_workspace_state(context)

    assert result["ok"] is True
    assert result["version"] == REMOTE_WORKSPACE_STATE_VERSION
    assert result["savedKeys"] == ["sqx_plan_user_v1", "sqx_strategies_user_v1"]
    assert state["sqx_plan_user_v1"]["minings"][0]["num"] == 77
    assert state["sqx_strategies_user_v1"][0]["id"] == "S1"
    assert "sqx_license_state_v1" not in state
    assert (context["_paths"]["config"] / REMOTE_WORKSPACE_STATE_DB).is_file()


def test_remote_state_endpoints_require_session_and_return_no_local_paths(tmp_path, monkeypatch):
    client = server.app.test_client()
    denied = client.get("/api/remote/state/bootstrap")
    assert denied.status_code == 403
    assert denied.get_json()["privacy"]["local_paths_returned"] is False

    client, headers, workspaces_root = _authorized_client(tmp_path, monkeypatch)
    saved = client.post(
        "/api/remote/state/save",
        json={
            "source": "pytest",
            "state": {
                "sqx_plan_user_v1": {"minings": [{"num": 12, "asset": "EURUSD"}], "phases": {"1": {"name": "User"}}},
                "sqx_strategies_deleted_v1": ["base-1"],
                "sqx_license_state_v1": {"must": "not persist"},
            },
        },
        headers=headers,
        base_url="https://localhost",
    )
    saved_data = saved.get_json()
    assert saved.status_code == 200
    assert saved_data["savedKeys"] == ["sqx_plan_user_v1", "sqx_strategies_deleted_v1"]
    assert saved_data["privacy"]["local_paths_returned"] is False
    assert "buyer@example.invalid" not in json.dumps(saved_data)

    boot = client.get("/api/remote/state/bootstrap", headers=headers, base_url="https://localhost")
    boot_data = boot.get_json()
    assert boot.status_code == 200
    assert boot_data["version"] == REMOTE_WORKSPACE_STATE_VERSION
    assert boot_data["state"]["sqx_plan_user_v1"]["minings"][0]["asset"] == "EURUSD"
    assert boot_data["state"]["sqx_strategies_deleted_v1"] == ["base-1"]
    assert "sqx_license_state_v1" not in boot_data["state"]
    assert boot_data["privacy"]["local_paths_returned"] is False
    assert "buyer@example.invalid" not in json.dumps(boot_data)

    workspace_id = workspace_id_from_identity_hash(email_hash("buyer@example.invalid"))
    assert (workspaces_root / workspace_id / "config" / REMOTE_WORKSPACE_STATE_DB).is_file()


def test_remote_state_is_separate_per_identity(tmp_path, monkeypatch):
    first, first_headers, _root = _authorized_client(tmp_path, monkeypatch, "first@example.invalid")
    first.post(
        "/api/remote/state/save",
        json={"state": {"sqx_plan_user_v1": {"minings": [{"asset": "XAUUSD"}], "phases": {}}}},
        headers=first_headers,
        base_url="https://localhost",
    )

    second, second_headers, _root = _authorized_client(tmp_path, monkeypatch, "second@example.invalid")
    second_boot = second.get("/api/remote/state/bootstrap", headers=second_headers, base_url="https://localhost")
    second_data = second_boot.get_json()

    assert second_boot.status_code == 200
    assert second_data["state"] == {}
    assert workspace_id_from_identity_hash(email_hash("first@example.invalid")) != workspace_id_from_identity_hash(email_hash("second@example.invalid"))
