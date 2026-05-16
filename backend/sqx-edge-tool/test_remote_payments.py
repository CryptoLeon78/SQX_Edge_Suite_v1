import json

from api import server
from core.remote_access import (
    ENTITLEMENTS_SCHEMA_VERSION,
    FULL_FEATURE_SCOPE,
    SESSION_COOKIE_NAME,
    create_signed_session,
    email_hash,
    evaluate_remote_access,
)
from core.remote_payments import (
    PAYMENT_WEBHOOK_SECRET_ENV,
    REMOTE_PAYMENT_WEBHOOK_VERSION,
    process_payment_webhook,
    sign_payment_webhook_body,
)


def _body(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _signature(raw: bytes, secret: str) -> str:
    return "sha256=" + sign_payment_webhook_body(raw, secret)


def test_payment_webhook_signature_and_entitlement_activation(tmp_path, monkeypatch):
    secret = "p" * 40
    store_path = tmp_path / "remote_entitlements.local.json"
    audit_path = tmp_path / "payment_events.local.jsonl"
    monkeypatch.setenv(PAYMENT_WEBHOOK_SECRET_ENV, secret)
    raw = _body({
        "eventId": "evt_paid_1",
        "eventType": "subscription_activated",
        "email": "buyer@example.invalid",
        "subscriptionId": "sub_1",
        "customerId": "cus_1",
    })

    result = process_payment_webhook(raw, _signature(raw, secret), store_path=store_path, audit_path=audit_path)

    assert result["ok"] is True
    assert result["version"] == REMOTE_PAYMENT_WEBHOOK_VERSION
    assert result["entitlement"]["kind"] == "paid_subscription"
    assert result["entitlement"]["status"] == "active"
    assert result["privacy"]["raw_email_returned"] is False
    assert result["privacy"]["webhook_secret_returned"] is False
    assert "buyer@example.invalid" not in json.dumps(result)

    store = json.loads(store_path.read_text(encoding="utf-8"))
    assert store["schemaVersion"] == ENTITLEMENTS_SCHEMA_VERSION
    assert "source" not in store
    assert store["grants"][0]["emailHash"] == email_hash("buyer@example.invalid")
    assert store["grants"][0]["entitlementKind"] == "paid_subscription"
    assert store["grants"][0]["status"] == "active"
    assert store["grants"][0]["featureScope"] == FULL_FEATURE_SCOPE
    assert "email" not in store["grants"][0]
    assert store["processedWebhookEvents"][0]["eventId"] == "evt_paid_1"
    assert "buyer@example.invalid" not in store_path.read_text(encoding="utf-8")
    assert audit_path.read_text(encoding="utf-8").count("remote_payment_webhook_processed") == 1


def test_payment_webhook_is_idempotent(tmp_path, monkeypatch):
    secret = "p" * 40
    store_path = tmp_path / "remote_entitlements.local.json"
    monkeypatch.setenv(PAYMENT_WEBHOOK_SECRET_ENV, secret)
    raw = _body({
        "eventId": "evt_once",
        "eventType": "order_paid",
        "email": "buyer@example.invalid",
    })
    signature = _signature(raw, secret)

    first = process_payment_webhook(raw, signature, store_path=store_path, audit_path=tmp_path / "audit.local.jsonl")
    second = process_payment_webhook(raw, signature, store_path=store_path, audit_path=tmp_path / "audit.local.jsonl")

    store = json.loads(store_path.read_text(encoding="utf-8"))
    assert first["idempotent"] is False
    assert second["idempotent"] is True
    assert len(store["grants"]) == 1
    assert len(store["processedWebhookEvents"]) == 1


def test_payment_webhook_cancel_blocks_paid_entitlement(tmp_path, monkeypatch):
    secret = "p" * 40
    store_path = tmp_path / "remote_entitlements.local.json"
    monkeypatch.setenv(PAYMENT_WEBHOOK_SECRET_ENV, secret)
    activate = _body({
        "eventId": "evt_activate",
        "eventType": "subscription_created",
        "email": "buyer@example.invalid",
    })
    cancel = _body({
        "eventId": "evt_cancel",
        "eventType": "subscription_cancelled",
        "email": "buyer@example.invalid",
    })

    process_payment_webhook(activate, _signature(activate, secret), store_path=store_path, audit_path=tmp_path / "audit.local.jsonl")
    cancelled = process_payment_webhook(cancel, _signature(cancel, secret), store_path=store_path, audit_path=tmp_path / "audit.local.jsonl")

    store = json.loads(store_path.read_text(encoding="utf-8"))
    access = evaluate_remote_access("buyer@example.invalid", store=store)
    assert cancelled["entitlement"]["status"] == "cancelled"
    assert store["grants"][0]["status"] == "cancelled"
    assert access["access"]["allowed"] is False
    assert access["access"]["reason"] == "entitlement_cancelled"


def test_payment_webhook_rejects_missing_secret_bad_signature_and_bad_payload(tmp_path, monkeypatch):
    raw = _body({
        "eventId": "evt_bad",
        "eventType": "subscription_activated",
        "email": "buyer@example.invalid",
    })

    monkeypatch.delenv(PAYMENT_WEBHOOK_SECRET_ENV, raising=False)
    missing_secret = process_payment_webhook(raw, "sha256=abc", store_path=tmp_path / "store.local.json")
    assert missing_secret["http_status"] == 503
    assert missing_secret["error"] == "payment_webhook_secret_missing_or_short"

    monkeypatch.setenv(PAYMENT_WEBHOOK_SECRET_ENV, "p" * 40)
    bad_signature = process_payment_webhook(raw, "sha256=abc", store_path=tmp_path / "store.local.json")
    assert bad_signature["http_status"] == 401
    assert bad_signature["error"] == "payment_webhook_signature_invalid"

    malformed = process_payment_webhook(b"{not-json", _signature(b"{not-json", "p" * 40), store_path=tmp_path / "store.local.json")
    assert malformed["http_status"] == 400
    assert malformed["error"] == "payment_webhook_payload_invalid"


def test_payment_webhook_api_route_updates_store_without_returning_raw_identity(tmp_path, monkeypatch):
    secret = "p" * 40
    store_path = tmp_path / "remote_entitlements.local.json"
    monkeypatch.setenv(PAYMENT_WEBHOOK_SECRET_ENV, secret)
    monkeypatch.setenv("SQX_REMOTE_ENTITLEMENTS_PATH", str(store_path))
    raw = _body({
        "eventId": "evt_api",
        "eventType": "subscription_renewed",
        "email": "buyer@example.invalid",
    })

    response = server.app.test_client().post(
        "/api/remote/payment/webhook",
        data=raw,
        content_type="application/json",
        headers={"X-SQX-Webhook-Signature": _signature(raw, secret)},
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["ok"] is True
    assert data["entitlement"]["status"] == "active"
    assert data["privacy"]["raw_email_returned"] is False
    assert "buyer@example.invalid" not in json.dumps(data)
    assert json.loads(store_path.read_text(encoding="utf-8"))["grants"][0]["entitlementKind"] == "paid_subscription"


def test_remote_protected_write_pilot_requires_active_app_session(tmp_path, monkeypatch):
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
    store_path.write_text(json.dumps(store), encoding="utf-8")
    workspaces_root = tmp_path / "workspaces"
    monkeypatch.setenv("SQX_REMOTE_ENTITLEMENTS_PATH", str(store_path))
    monkeypatch.setenv("SQX_REMOTE_SESSION_SECRET", "s" * 40)
    monkeypatch.setenv("SQX_REMOTE_WORKSPACES_ROOT", str(workspaces_root))

    client = server.app.test_client()
    denied = client.post("/api/remote/protected/write-pilot", json={"action": "dry_run"})
    assert denied.status_code == 403
    assert denied.get_json()["error"] == "remote_session_required"

    signed = create_signed_session(
        "buyer@example.invalid",
        {"kind": "paid_subscription", "grant_id": "paid-1", "feature_scope": "full"},
    )
    client.set_cookie(SESSION_COOKIE_NAME, signed["token"])
    allowed = client.post("/api/remote/protected/write-pilot", json={"action": "dry_run"})

    data = allowed.get_json()
    assert allowed.status_code == 200
    assert data["ok"] is True
    assert data["version"] == "remote-write-pilot-v1"
    assert data["access"]["allowed"] is True
    assert data["workspace"]["id"].startswith("ws_")
    assert data["privacy"]["session_token_returned"] is False
    assert data["privacy"]["raw_email_returned"] is False
    assert data["privacy"]["local_paths_returned"] is False
    assert "buyer@example.invalid" not in json.dumps(data)
    audit_path = workspaces_root / data["workspace"]["id"] / "logs" / "audit.local.jsonl"
    assert "remote_write_pilot" in audit_path.read_text(encoding="utf-8")
