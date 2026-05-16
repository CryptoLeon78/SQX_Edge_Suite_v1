import json

from api import server
from core.remote_access import SESSION_COOKIE_NAME, create_signed_session, email_hash
from core.remote_workspaces import (
    REMOTE_WORKSPACE_VERSION,
    append_workspace_audit_event,
    derive_remote_workspace,
    public_workspace_context,
    workspace_id_from_identity_hash,
)


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


def test_workspace_id_is_deterministic_and_hash_only():
    identity_hash = email_hash("buyer@example.invalid")
    workspace_id = workspace_id_from_identity_hash(identity_hash)

    assert workspace_id == "ws_" + identity_hash[:24]
    assert "buyer" not in workspace_id
    assert "example" not in workspace_id


def test_derive_remote_workspace_creates_layout_without_public_local_paths(tmp_path):
    context = derive_remote_workspace(_session_status(), create=True, root=tmp_path)
    public = public_workspace_context(context)

    assert context["ok"] is True
    assert public["version"] == REMOTE_WORKSPACE_VERSION
    assert public["id"].startswith("ws_")
    assert public["owner_hash"] == email_hash("buyer@example.invalid")
    assert public["owner_ref"] == "bu***@example.invalid"
    assert public["paths"]["mode"] == "server_managed"
    assert public["paths"]["local_paths_returned"] is False
    assert "buyer@example.invalid" not in json.dumps(public)

    workspace_path = context["_path"]
    assert workspace_path.is_dir()
    for subdir in ("config", "uploads", "outputs", "exports", "logs", "tmp"):
        assert (workspace_path / subdir).is_dir()
    manifest = json.loads((workspace_path / "workspace_manifest.local.json").read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == REMOTE_WORKSPACE_VERSION
    assert manifest["privacy"]["raw_email_stored"] is False
    assert "buyer@example.invalid" not in json.dumps(manifest)


def test_workspace_requires_active_remote_session(tmp_path):
    denied = derive_remote_workspace({
        "ok": True,
        "session": {"active": False},
        "access": {"allowed": False, "reason": "session_missing"},
    }, create=True, root=tmp_path)

    assert denied["ok"] is False
    assert denied["error"] == "remote_session_required"
    assert not any(tmp_path.iterdir())


def test_workspace_audit_event_is_written_inside_workspace(tmp_path):
    context = derive_remote_workspace(_session_status(), create=True, root=tmp_path)
    result = append_workspace_audit_event(context, {
        "type": "remote_write_pilot",
        "action": "dry_run",
        "browserWorkspaceIgnored": True,
    })

    audit_path = context["_paths"]["logs"] / "audit.local.jsonl"
    audit_lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert result["audit_event"]["workspace_id"] == context["workspace"]["id"]
    assert len(audit_lines) == 1
    payload = json.loads(audit_lines[0])
    assert payload["workspaceId"] == context["workspace"]["id"]
    assert payload["browserWorkspaceIgnored"] is True


def test_remote_workspace_status_endpoint_requires_session_and_returns_no_paths(tmp_path, monkeypatch):
    store = {
        "schemaVersion": "remote-entitlements-v1",
        "grants": [{
            "emailHash": email_hash("buyer@example.invalid"),
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

    client = server.app.test_client()
    denied = client.get("/api/remote/workspace/status")
    assert denied.status_code == 403
    assert denied.get_json()["privacy"]["local_paths_returned"] is False

    signed = create_signed_session(
        "buyer@example.invalid",
        {"kind": "paid_subscription", "grant_id": "paid-1", "feature_scope": "full"},
    )
    client.set_cookie(SESSION_COOKIE_NAME, signed["token"])
    allowed = client.get("/api/remote/workspace/status")
    data = allowed.get_json()

    assert allowed.status_code == 200
    assert data["ok"] is True
    assert data["workspace"]["id"] == workspace_id_from_identity_hash(email_hash("buyer@example.invalid"))
    assert data["workspace"]["paths"]["local_paths_returned"] is False
    assert data["privacy"]["local_paths_returned"] is False
    assert "buyer@example.invalid" not in json.dumps(data)
    assert (workspaces_root / data["workspace"]["id"] / "workspace_manifest.local.json").is_file()


def test_remote_write_pilot_ignores_browser_workspace_and_writes_workspace_audit(tmp_path, monkeypatch):
    store = {
        "schemaVersion": "remote-entitlements-v1",
        "grants": [{
            "emailHash": email_hash("buyer@example.invalid"),
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

    signed = create_signed_session(
        "buyer@example.invalid",
        {"kind": "paid_subscription", "grant_id": "paid-1", "feature_scope": "full"},
    )
    client = server.app.test_client()
    client.set_cookie(SESSION_COOKIE_NAME, signed["token"])
    response = client.post(
        "/api/remote/protected/write-pilot",
        json={"action": "dry_run", "workspace_id": "../../other-user", "path": "C:/private"},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["workspace"]["id"] == workspace_id_from_identity_hash(email_hash("buyer@example.invalid"))
    assert data["event"]["browser_workspace_ignored"] is True
    assert data["privacy"]["local_paths_returned"] is False
    assert "../../other-user" not in json.dumps(data)
    audit_path = workspaces_root / data["workspace"]["id"] / "logs" / "audit.local.jsonl"
    audit_payload = json.loads(audit_path.read_text(encoding="utf-8").splitlines()[0])
    assert audit_payload["workspaceId"] == data["workspace"]["id"]
    assert audit_payload["browserWorkspaceIgnored"] is True
