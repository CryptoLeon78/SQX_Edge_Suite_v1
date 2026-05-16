from datetime import date
from unittest.mock import patch

from api import server
from core.remote_access import (
    email_hash,
    evaluate_remote_access,
    find_entitlement_for_email,
    normalize_email,
    redact_email,
)


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
    assert result["entitlement"]["grant_key_required"] is True
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
    with patch.object(server, "evaluate_remote_access_from_headers", return_value=expected) as evaluator:
        response = server.app.test_client().get(
            "/api/remote/access/status",
            headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
        )

    assert response.status_code == 200
    data = response.get_json()
    assert data["access"]["allowed"] is True
    assert data["identity"]["email_ref"] == "te***@example.invalid"
    assert data["privacy"]["raw_email_returned"] is False
    evaluator.assert_called_once()
