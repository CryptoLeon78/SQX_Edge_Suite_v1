from datetime import date
import json
from unittest.mock import patch

import pytest

from api import server
from core.remote_access import (
    SESSION_COOKIE_NAME,
    create_signed_session,
    email_hash,
    evaluate_remote_access,
    evaluate_remote_session,
    find_entitlement_for_email,
    grant_key_hash,
    normalize_email,
    redact_email,
    start_remote_session_from_headers,
    verify_tester_grant_key,
)
from tools.remote_tester_grant import build_tester_grant, upsert_tester_grant


def test_email_normalization_redaction_and_hash_are_stable():
    assert normalize_email("  TESTER@Example.COM ") == "tester@example.com"
    assert redact_email("tester@example.com") == "te***@example.com"
    assert email_hash("tester@example.com") == email_hash(" TESTER@example.com ")


def test_tester_free_grant_allows_full_access_without_payment():
    store = {
        "schemaVersion": "remote-entitlements-v1",
        "grants": [{
            "emailHash": email_hash("pilot@example.invalid"),
            "entitlementKind": "tester_free",
            "status": "active",
            "featureScope": "full",
            "source": "operator_grant",
            "grantKeyHash": "sha256-redacted",
        }],
    }

    result = evaluate_remote_access("pilot@example.invalid", store=store, today=date(2026, 5, 16))

    assert result["access"]["allowed"] is True
    assert result["access"]["feature_scope"] == "full"
    assert result["entitlement"]["kind"] == "tester_free"
    assert result["entitlement"]["source"] == "operator_grant"
    assert result["entitlement"]["grant_key_configured"] is True
    assert result["entitlement"]["grant_key_required"] is False
    assert result["auth_layers"]["app_session_required"] is True
    assert result["auth_layers"]["grant_key_never_returned"] is True
    assert result["identity"]["email_ref"] == "pi***@example.invalid"
    assert result["privacy"]["raw_email_returned"] is False


def test_paid_subscription_and_internal_operator_are_first_class_entitlements():
    for kind in ("paid_subscription", "internal_operator"):
        store = {
            "schemaVersion": "remote-entitlements-v1",
            "grants": [{
                "email": "buyer@example.invalid",
                "entitlementKind": kind,
                "status": "active",
                "featureScope": "full",
            }],
        }
        result = evaluate_remote_access("buyer@example.invalid", store=store)
        assert result["access"]["allowed"] is True
        assert result["entitlement"]["kind"] == kind
        assert result["access"]["features"] == ["*"]


def test_blocked_missing_and_expired_entitlements_do_not_allow_access():
    store = {
        "schemaVersion": "remote-entitlements-v1",
        "grants": [
            {
                "email": "blocked@example.invalid",
                "entitlementKind": "tester_free",
                "status": "blocked",
                "featureScope": "full",
            },
            {
                "email": "expired@example.invalid",
                "entitlementKind": "paid_subscription",
                "status": "active",
                "featureScope": "full",
                "expiresAt": "2026-01-01",
            },
        ],
    }

    assert evaluate_remote_access(None, store=store)["access"]["reason"] == "identity_missing"
    assert evaluate_remote_access("missing@example.invalid", store=store)["access"]["allowed"] is False
    assert evaluate_remote_access("blocked@example.invalid", store=store)["access"]["reason"] == "entitlement_blocked"
    expired = evaluate_remote_access("expired@example.invalid", store=store, today=date(2026, 5, 16))
    assert expired["entitlement"]["status"] == "expired"
    assert expired["access"]["allowed"] is False


def test_find_entitlement_accepts_hash_or_local_email_without_returning_raw_keys():
    store = {
        "schemaVersion": "remote-entitlements-v1",
        "grants": [
            {"emailHash": email_hash("hashed@example.invalid"), "entitlementKind": "tester_free"},
            {"email": "local@example.invalid", "entitlementKind": "paid_subscription"},
        ],
    }

    assert find_entitlement_for_email("hashed@example.invalid", store)["entitlementKind"] == "tester_free"
    assert find_entitlement_for_email("local@example.invalid", store)["entitlementKind"] == "paid_subscription"


def test_tester_free_session_starts_after_cloudflare_identity_without_default_grant_key(tmp_path, monkeypatch):
    store = {
        "schemaVersion": "remote-entitlements-v1",
        "grants": [{
            "emailHash": email_hash("pilot@example.invalid"),
            "entitlementKind": "tester_free",
            "status": "active",
            "featureScope": "full",
            "grantKeyHash": grant_key_hash("pilot-key"),
            "source": "operator_grant",
        }],
    }
    store_path = tmp_path / "remote_entitlements.local.json"
    store_path.write_text(json.dumps(store), encoding="utf-8")
    monkeypatch.setenv("SQX_REMOTE_ENTITLEMENTS_PATH", str(store_path))
    monkeypatch.setenv("SQX_REMOTE_SESSION_SECRET", "s" * 40)
    monkeypatch.setenv("SQX_REMOTE_ACCESS_CONTROL_PATH", str(tmp_path / "remote_access_control.local.json"))
    monkeypatch.setenv("SQX_REMOTE_ACCESS_CONTROL_EVENTS_PATH", str(tmp_path / "remote_access_events.local.jsonl"))

    created = start_remote_session_from_headers(
        {"Cf-Access-Authenticated-User-Email": "pilot@example.invalid"},
        {},
    )

    assert created["ok"] is True
    assert created["cookie_name"] == SESSION_COOKIE_NAME
    assert created["entitlement"]["kind"] == "tester_free"
    assert created["entitlement"]["grant_key_configured"] is True
    assert created["entitlement"]["grant_key_required"] is False
    assert created["privacy"]["session_token_returned"] is False
    assert created["privacy"]["grant_key_returned"] is False
    assert evaluate_remote_session(created["session_token"])["access"]["allowed"] is True


def test_tester_free_session_can_enforce_legacy_matching_grant_key_and_revalidate_entitlement(tmp_path, monkeypatch):
    store = {
        "schemaVersion": "remote-entitlements-v1",
        "grants": [{
            "emailHash": email_hash("pilot@example.invalid"),
            "entitlementKind": "tester_free",
            "status": "active",
            "featureScope": "full",
            "grantKeyHash": grant_key_hash("pilot-key"),
            "requireGrantKey": True,
            "source": "operator_grant",
        }],
    }
    store_path = tmp_path / "remote_entitlements.local.json"
    store_path.write_text(json.dumps(store), encoding="utf-8")
    monkeypatch.setenv("SQX_REMOTE_ENTITLEMENTS_PATH", str(store_path))
    monkeypatch.setenv("SQX_REMOTE_SESSION_SECRET", "s" * 40)

    missing = start_remote_session_from_headers(
        {"Cf-Access-Authenticated-User-Email": "pilot@example.invalid"},
        {},
    )
    assert missing["http_status"] == 403
    assert missing["error"] == "tester_grant_key_required"

    invalid = start_remote_session_from_headers(
        {"Cf-Access-Authenticated-User-Email": "pilot@example.invalid"},
        {"grant_key": "wrong"},
    )
    assert invalid["http_status"] == 403
    assert invalid["error"] == "tester_grant_key_invalid"

    created = start_remote_session_from_headers(
        {"Cf-Access-Authenticated-User-Email": "pilot@example.invalid"},
        {"grant_key": "pilot-key"},
    )
    assert created["ok"] is True
    assert created["cookie_name"] == SESSION_COOKIE_NAME
    assert "session_token" in created
    assert created["privacy"]["session_token_returned"] is False
    assert created["privacy"]["grant_key_returned"] is False

    session = evaluate_remote_session(created["session_token"])
    assert session["access"]["allowed"] is True
    assert session["session"]["email_ref"] == "pi***@example.invalid"

    store["grants"][0]["status"] = "blocked"
    store_path.write_text(json.dumps(store), encoding="utf-8")
    blocked = evaluate_remote_session(created["session_token"])
    assert blocked["access"]["allowed"] is False
    assert blocked["access"]["reason"] == "entitlement_blocked"


def test_paid_subscription_session_does_not_require_tester_key(tmp_path, monkeypatch):
    store = {
        "schemaVersion": "remote-entitlements-v1",
        "grants": [{
            "emailHash": email_hash("buyer@example.invalid"),
            "entitlementKind": "paid_subscription",
            "status": "active",
            "featureScope": "full",
            "source": "checkout_webhook",
        }],
    }
    store_path = tmp_path / "remote_entitlements.local.json"
    store_path.write_text(json.dumps(store), encoding="utf-8")
    monkeypatch.setenv("SQX_REMOTE_ENTITLEMENTS_PATH", str(store_path))
    monkeypatch.setenv("SQX_REMOTE_SESSION_SECRET", "s" * 40)

    created = start_remote_session_from_headers(
        {"Cf-Access-Authenticated-User-Email": "buyer@example.invalid"},
        {},
    )

    assert created["ok"] is True
    assert created["entitlement"]["kind"] == "paid_subscription"
    assert evaluate_remote_session(created["session_token"])["access"]["allowed"] is True


def test_session_secret_is_required_before_login(monkeypatch):
    monkeypatch.delenv("SQX_REMOTE_SESSION_SECRET", raising=False)
    result = start_remote_session_from_headers(
        {"Cf-Access-Authenticated-User-Email": "buyer@example.invalid"},
        {},
    )
    assert result["http_status"] == 503
    assert result["error"] == "remote_session_secret_missing_or_short"


def test_tester_grant_key_hash_is_constant_time_verifiable():
    grant = {"grantKeyHash": grant_key_hash("secret-key")}
    assert verify_tester_grant_key(grant, "secret-key")["ok"] is True
    assert verify_tester_grant_key(grant, "other")["error"] == "tester_grant_key_invalid"
    assert verify_tester_grant_key({}, "secret-key")["error"] == "tester_grant_key_not_configured"


def test_remote_tester_grant_tool_writes_hashes_without_raw_private_values(tmp_path):
    store_path = tmp_path / "remote_entitlements.local.json"

    result = upsert_tester_grant(store_path, " Pilot@Example.Invalid ", "pilot-key")
    store = json.loads(store_path.read_text(encoding="utf-8"))
    grant = store["grants"][0]
    result_text = json.dumps(result)
    store_text = json.dumps(store)

    assert result["ok"] is True
    assert result["status"] == "created"
    assert result["rawEmailReturned"] is False
    assert result["grantKeyReturned"] is False
    assert result["emailHashRef"] == email_hash("pilot@example.invalid")[:12]
    assert grant["emailHash"] == email_hash("pilot@example.invalid")
    assert grant["grantKeyHash"] == grant_key_hash("pilot-key")
    assert "email" not in grant
    assert "pilot@example.invalid" not in result_text
    assert "pilot@example.invalid" not in store_text
    assert "pilot-key" not in result_text
    assert "pilot-key" not in store_text

    updated = upsert_tester_grant(store_path, "pilot@example.invalid", "new-key")
    store = json.loads(store_path.read_text(encoding="utf-8"))
    assert updated["status"] == "updated"
    assert len(store["grants"]) == 1
    assert store["grants"][0]["grantKeyHash"] == grant_key_hash("new-key")


def test_build_tester_grant_requires_email_and_private_key():
    assert build_tester_grant("tester@example.invalid", "secret")["grantId"].startswith("tester_")
    with pytest.raises(ValueError, match="email_required"):
        build_tester_grant("", "secret")
    with pytest.raises(ValueError, match="grant_key_required"):
        build_tester_grant("tester@example.invalid", "")


def test_remote_access_status_endpoint_uses_trusted_header_and_redacts_identity():
    expected = {
        "ok": True,
        "version": "remote-access-v1",
        "authenticated": True,
        "identity": {"email_ref": "te***@example.invalid"},
        "entitlement": {"kind": "tester_free", "status": "active"},
        "access": {"allowed": True, "feature_scope": "full"},
        "privacy": {"raw_email_returned": False},
    }
    with patch.object(server, "evaluate_remote_request", return_value=expected) as evaluator:
        response = server.app.test_client().get(
            "/api/remote/access/status",
            headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
        )

    assert response.status_code == 200
    data = response.get_json()
    assert data["access"]["allowed"] is True
    assert data["identity"]["email_ref"] == "te***@example.invalid"
    assert data["privacy"]["raw_email_returned"] is False
    assert evaluator.call_count >= 1


def test_remote_session_endpoints_set_and_clear_secure_cookie(tmp_path, monkeypatch):
    store = {
        "schemaVersion": "remote-entitlements-v1",
        "grants": [{
            "emailHash": email_hash("pilot@example.invalid"),
            "entitlementKind": "tester_free",
            "status": "active",
            "featureScope": "full",
            "grantKeyHash": grant_key_hash("pilot-key"),
        }],
    }
    store_path = tmp_path / "remote_entitlements.local.json"
    store_path.write_text(json.dumps(store), encoding="utf-8")
    monkeypatch.setenv("SQX_REMOTE_ENTITLEMENTS_PATH", str(store_path))
    monkeypatch.setenv("SQX_REMOTE_SESSION_SECRET", "s" * 40)
    monkeypatch.setenv("SQX_REMOTE_ACCESS_CONTROL_PATH", str(tmp_path / "remote_access_control.local.json"))
    monkeypatch.setenv("SQX_REMOTE_ACCESS_CONTROL_EVENTS_PATH", str(tmp_path / "remote_access_events.local.jsonl"))

    client = server.app.test_client()
    login = client.post(
        "/api/remote/session/login",
        headers={"Cf-Access-Authenticated-User-Email": "pilot@example.invalid"},
        json={"grant_key": "pilot-key"},
    )

    assert login.status_code == 200
    data = login.get_json()
    assert data["access"]["allowed"] is True
    assert data["privacy"]["session_token_returned"] is False
    assert data["privacy"]["grant_key_returned"] is False
    cookie_header = login.headers.get("Set-Cookie", "")
    assert SESSION_COOKIE_NAME in cookie_header
    assert "HttpOnly" in cookie_header
    assert "Secure" in cookie_header
    assert "SameSite=Lax" in cookie_header
    assert "Max-Age" not in cookie_header
    assert "Expires" not in cookie_header
    assert data["session"]["cookie_persistence"] == "browser_session"

    logout = client.post("/api/remote/session/logout")
    assert logout.status_code == 200
    assert SESSION_COOKIE_NAME in logout.headers.get("Set-Cookie", "")


def test_remote_session_status_endpoint_does_not_return_token(monkeypatch):
    monkeypatch.setenv("SQX_REMOTE_SESSION_SECRET", "s" * 40)
    signed = create_signed_session(
        "buyer@example.invalid",
        {"kind": "paid_subscription", "grant_id": "paid-1", "feature_scope": "full"},
    )
    with patch.object(server, "evaluate_remote_session", return_value={
        "ok": True,
        "session": {"active": True, "email_ref": "bu***@example.invalid"},
        "access": {"allowed": True},
        "privacy": {"session_token_returned": False},
    }) as evaluator:
        response = server.app.test_client().get(
            "/api/remote/session/status",
            headers={"Cookie": f"{SESSION_COOKIE_NAME}={signed['token']}"},
        )
    assert response.status_code == 200
    assert response.get_json()["privacy"]["session_token_returned"] is False
    assert evaluator.call_count >= 1
