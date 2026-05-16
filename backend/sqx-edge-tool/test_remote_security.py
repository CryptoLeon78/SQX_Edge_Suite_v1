import json

from api import server
from core.remote_access import SESSION_COOKIE_NAME, create_signed_session, email_hash, evaluate_remote_session
from core.remote_security import (
    REMOTE_SECURITY_VERSION,
    check_remote_rate_limit,
    load_remote_security_policy,
    public_security_status,
    reset_remote_rate_limits,
)


def _write_entitlements(path, email="buyer@example.invalid"):
    path.write_text(json.dumps({
        "schemaVersion": "remote-entitlements-v1",
        "grants": [{
            "emailHash": email_hash(email),
            "entitlementKind": "paid_subscription",
            "status": "active",
            "featureScope": "full",
        }],
    }), encoding="utf-8")


def _write_security_policy(path, **overrides):
    payload = {
        "schemaVersion": REMOTE_SECURITY_VERSION,
        "killSwitch": {"active": False, "reason": "test"},
        "blockedIdentityHashes": [],
        "revokedSessionIds": [],
        "rateLimits": {
            "remote_status": {"limit": 180, "windowSeconds": 60},
            "remote_session_login": {"limit": 10, "windowSeconds": 60},
            "remote_session_logout": {"limit": 30, "windowSeconds": 60},
            "remote_payment_webhook": {"limit": 90, "windowSeconds": 60},
            "remote_protected_write": {"limit": 30, "windowSeconds": 60},
        },
        "watermark": {"enabled": True, "label": "SQX REMOTE PRO"},
        "audit": {"recentEventsLimit": 20},
    }
    payload.update(overrides)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def test_default_remote_security_policy_is_public_safe(tmp_path, monkeypatch):
    monkeypatch.setenv("SQX_REMOTE_SECURITY_POLICY_PATH", str(tmp_path / "missing.local.json"))

    policy = load_remote_security_policy()
    status = public_security_status({"session": {"email_ref": "bu***@example.invalid"}, "access": {"allowed": False}}, policy=policy)

    assert policy["schemaVersion"] == REMOTE_SECURITY_VERSION
    assert policy["source"] == "missing_local_policy"
    assert policy["privacy"]["policy_path_returned"] is False
    assert policy["privacy"]["raw_emails_returned"] is False
    assert status["version"] == REMOTE_SECURITY_VERSION
    assert status["privacy"]["local_paths_returned"] is False
    assert "missing.local.json" not in json.dumps(status)


def test_remote_rate_limit_blocks_after_configured_limit():
    reset_remote_rate_limits()
    policy = {
        "schemaVersion": REMOTE_SECURITY_VERSION,
        "rateLimits": {"remote_status": {"limit": 2, "windowSeconds": 60}},
    }

    first = check_remote_rate_limit("subject-hash", "remote_status", policy=policy, now=1000)
    second = check_remote_rate_limit("subject-hash", "remote_status", policy=policy, now=1001)
    third = check_remote_rate_limit("subject-hash", "remote_status", policy=policy, now=1002)

    assert first["allowed"] is True
    assert second["allowed"] is True
    assert third["allowed"] is False
    assert third["retryAfterSeconds"] > 0
    assert third["privacy"]["subject_returned"] is False


def test_session_revocation_and_identity_blocking_are_enforced(tmp_path, monkeypatch):
    store_path = tmp_path / "remote_entitlements.local.json"
    policy_path = tmp_path / "remote_security.local.json"
    _write_entitlements(store_path)
    monkeypatch.setenv("SQX_REMOTE_ENTITLEMENTS_PATH", str(store_path))
    monkeypatch.setenv("SQX_REMOTE_SECURITY_POLICY_PATH", str(policy_path))
    monkeypatch.setenv("SQX_REMOTE_SESSION_SECRET", "s" * 40)

    signed = create_signed_session(
        "buyer@example.invalid",
        {"kind": "paid_subscription", "grant_id": "paid-1", "feature_scope": "full"},
    )
    _write_security_policy(policy_path, revokedSessionIds=[signed["payload"]["sid"]])
    revoked = evaluate_remote_session(signed["token"])
    assert revoked["access"]["allowed"] is False
    assert revoked["access"]["reason"] == "session_revoked"
    assert revoked["security"]["session_revoked"] is True

    _write_security_policy(policy_path, blockedIdentityHashes=[email_hash("buyer@example.invalid")])
    blocked = evaluate_remote_session(signed["token"])
    assert blocked["access"]["allowed"] is False
    assert blocked["access"]["reason"] == "security_identity_blocked"
    assert blocked["security"]["identity_blocked"] is True


def test_remote_security_status_and_recent_audit_are_redacted(tmp_path, monkeypatch):
    reset_remote_rate_limits()
    store_path = tmp_path / "remote_entitlements.local.json"
    policy_path = tmp_path / "remote_security.local.json"
    workspaces_root = tmp_path / "workspaces"
    _write_entitlements(store_path)
    _write_security_policy(policy_path)
    monkeypatch.setenv("SQX_REMOTE_ENTITLEMENTS_PATH", str(store_path))
    monkeypatch.setenv("SQX_REMOTE_SECURITY_POLICY_PATH", str(policy_path))
    monkeypatch.setenv("SQX_REMOTE_WORKSPACES_ROOT", str(workspaces_root))
    monkeypatch.setenv("SQX_REMOTE_SESSION_SECRET", "s" * 40)

    signed = create_signed_session(
        "buyer@example.invalid",
        {"kind": "paid_subscription", "grant_id": "paid-1", "feature_scope": "full"},
    )
    client = server.app.test_client()
    client.set_cookie(SESSION_COOKIE_NAME, signed["token"])

    status = client.get("/api/remote/security/status")
    status_data = status.get_json()
    assert status.status_code == 200
    assert status_data["version"] == REMOTE_SECURITY_VERSION
    assert status_data["watermark"]["enabled"] is True
    assert status_data["privacy"]["local_paths_returned"] is False
    assert "buyer@example.invalid" not in json.dumps(status_data)

    write = client.post("/api/remote/protected/write-pilot", json={
        "action": "dry_run",
        "path": "C:/private/local/path",
    })
    assert write.status_code == 200
    recent = client.get("/api/remote/security/audit/recent")
    recent_data = recent.get_json()
    assert recent.status_code == 200
    assert recent_data["events"][0]["identity_hash_ref"] == email_hash("buyer@example.invalid")[:12]
    assert recent_data["events"][0]["privacy"]["local_paths_returned"] is False
    assert "buyer@example.invalid" not in json.dumps(recent_data)
    assert "C:/private/local/path" not in json.dumps(recent_data)


def test_remote_kill_switch_blocks_login_and_protected_write(tmp_path, monkeypatch):
    reset_remote_rate_limits()
    policy_path = tmp_path / "remote_security.local.json"
    _write_security_policy(policy_path, killSwitch={"active": True, "reason": "incident_response"})
    monkeypatch.setenv("SQX_REMOTE_SECURITY_POLICY_PATH", str(policy_path))
    monkeypatch.setenv("SQX_REMOTE_SESSION_SECRET", "s" * 40)

    client = server.app.test_client()
    login = client.post(
        "/api/remote/session/login",
        headers={"Cf-Access-Authenticated-User-Email": "buyer@example.invalid"},
        json={},
    )
    assert login.status_code == 503
    assert login.get_json()["error"] == "remote_kill_switch_active"

    signed = create_signed_session(
        "buyer@example.invalid",
        {"kind": "paid_subscription", "grant_id": "paid-1", "feature_scope": "full"},
    )
    client.set_cookie(SESSION_COOKIE_NAME, signed["token"])
    protected = client.post("/api/remote/protected/write-pilot", json={"action": "dry_run"})
    assert protected.status_code == 503
    assert protected.get_json()["error"] == "remote_kill_switch_active"
