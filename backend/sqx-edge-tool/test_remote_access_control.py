from __future__ import annotations

import json
from datetime import datetime, timezone

from core.remote_access import email_hash
from core.remote_access_control import (
    ACCESS_CONTROL_COOKIE_NAME,
    approve_access_context,
    build_access_context,
    evaluate_access_context,
    load_access_control_store,
    record_session_started,
    revoke_access_context,
    save_access_control_store,
    summarize_access_control,
)


def _context(device: str, ip: str = "203.0.113.10", ua: str = "pytest-browser/1"):
    return build_access_context(
        {
            "CF-Connecting-IP": ip,
            "CF-IPCountry": "ES",
            "User-Agent": ua,
        },
        device_id=device,
    )


def test_first_two_contexts_are_trusted_and_third_is_pending(tmp_path):
    store = tmp_path / "remote_access_control.local.json"
    events = tmp_path / "events.local.jsonl"
    identity = email_hash("pilot@example.invalid")

    first = evaluate_access_context(identity, _context("device-a"), email_ref="pi***@example.invalid", store_path=store, events_path=events)
    second = evaluate_access_context(identity, _context("device-b", ip="203.0.113.11"), store_path=store, events_path=events)
    third = evaluate_access_context(identity, _context("device-c", ip="203.0.113.12"), store_path=store, events_path=events)

    assert first["accessControl"]["allowed"] is True
    assert first["accessControl"]["status"] == "trusted"
    assert second["accessControl"]["allowed"] is True
    assert second["accessControl"]["status"] == "trusted"
    assert third["accessControl"]["allowed"] is False
    assert third["accessControl"]["status"] == "pending"
    assert third["accessControl"]["reason"] == "context_pending"

    summary = summarize_access_control(store)["summary"]
    assert summary["trustedContexts"] == 2
    assert summary["pendingContexts"] == 1
    stored = store.read_text(encoding="utf-8")
    assert "pilot@example.invalid" not in stored
    assert "203.0.113" not in stored
    assert "pytest-browser" not in stored


def test_internal_operator_uses_owner_context_limit_instead_of_tester_limit(tmp_path):
    store = tmp_path / "remote_access_control.local.json"
    events = tmp_path / "events.local.jsonl"
    identity = email_hash("owner@example.invalid")

    results = [
        evaluate_access_context(
            identity,
            _context(f"owner-device-{index}", ip=f"203.0.113.{20 + index}"),
            email_ref="ow***@example.invalid",
            entitlement_kind="internal_operator",
            store_path=store,
            events_path=events,
        )
        for index in range(3)
    ]

    assert all(item["accessControl"]["allowed"] is True for item in results)
    assert results[-1]["accessControl"]["status"] == "trusted"
    assert results[-1]["accessControl"]["maxTrustedContextsPerIdentity"] == 2
    assert results[-1]["accessControl"]["effectiveMaxTrustedContexts"] == 8


def test_revoked_context_and_session_context_mismatch_block_access(tmp_path):
    store = tmp_path / "remote_access_control.local.json"
    events = tmp_path / "events.local.jsonl"
    identity = email_hash("buyer@example.invalid")
    context = _context("device-a")
    trusted = evaluate_access_context(identity, context, store_path=store, events_path=events)
    ref = trusted["accessControl"]["contextRef"]

    assert revoke_access_context(identity[:12], ref, store_path=store)["ok"] is True
    revoked = evaluate_access_context(identity, context, store_path=store, events_path=events)
    assert revoked["accessControl"]["allowed"] is False
    assert revoked["accessControl"]["status"] == "revoked"

    second_context = _context("device-b")
    approved = evaluate_access_context(identity, second_context, store_path=store, events_path=events)
    assert approved["accessControl"]["allowed"] is True
    mismatch = evaluate_access_context(identity, second_context, session_context_ref=ref, store_path=store, events_path=events)
    assert mismatch["accessControl"]["allowed"] is False
    assert mismatch["accessControl"]["reason"] == "session_context_mismatch"


def test_concurrent_context_login_blocks_recent_other_session(tmp_path):
    store = tmp_path / "remote_access_control.local.json"
    events = tmp_path / "events.local.jsonl"
    identity = email_hash("buyer@example.invalid")
    first = evaluate_access_context(identity, _context("device-a"), store_path=store, events_path=events)
    assert record_session_started(identity, first["accessControl"]["contextRef"], "sid-a", store_path=store, events_path=events, now=datetime.now(timezone.utc))["ok"]

    second = evaluate_access_context(identity, _context("device-b", ip="203.0.113.44"), purpose="session_login", store_path=store, events_path=events)
    assert second["accessControl"]["allowed"] is False
    assert second["accessControl"]["reason"] == "concurrent_context_active"


def test_operator_can_approve_pending_context_without_raw_identity(tmp_path):
    store = tmp_path / "remote_access_control.local.json"
    events = tmp_path / "events.local.jsonl"
    identity = email_hash("pilot@example.invalid")
    evaluate_access_context(identity, _context("device-a"), store_path=store, events_path=events)
    evaluate_access_context(identity, _context("device-b", ip="203.0.113.11"), store_path=store, events_path=events)
    pending = evaluate_access_context(identity, _context("device-c", ip="203.0.113.12"), store_path=store, events_path=events)

    result = approve_access_context(identity[:12], pending["accessControl"]["contextRef"], store_path=store)
    assert result["ok"] is True
    store_payload = load_access_control_store(store)
    assert "pilot@example.invalid" not in json.dumps(store_payload)
    assert ACCESS_CONTROL_COOKIE_NAME == "__Host-sqx_device_id"


def test_store_save_merges_identities_from_stale_writers(tmp_path):
    store = tmp_path / "remote_access_control.local.json"
    identity_a = email_hash("first@example.invalid")
    identity_b = email_hash("second@example.invalid")
    context_a = _context("device-a")
    context_b = _context("device-b", ip="203.0.113.22")

    save_access_control_store({
        "policy": {},
        "identities": {
            identity_a: {
                "identityHashRef": identity_a[:12],
                "emailRef": "fi***@example.invalid",
                "status": "active",
                "contexts": [{
                    "contextHash": context_a["contextHash"],
                    "contextRef": context_a["contextRef"],
                    "status": "trusted",
                    "approval": "operator_approved",
                }],
            }
        },
    }, path=store)
    save_access_control_store({
        "policy": {},
        "identities": {
            identity_b: {
                "identityHashRef": identity_b[:12],
                "emailRef": "se***@example.invalid",
                "status": "active",
                "contexts": [{
                    "contextHash": context_b["contextHash"],
                    "contextRef": context_b["contextRef"],
                    "status": "trusted",
                    "approval": "auto_within_limit",
                }],
            }
        },
    }, path=store)

    summary = summarize_access_control(store)["summary"]
    assert summary["identityCount"] == 2
    assert summary["trustedContexts"] == 2


def test_store_save_preserves_operator_approval_when_stale_pending_context_is_saved(tmp_path):
    store = tmp_path / "remote_access_control.local.json"
    identity = email_hash("pilot@example.invalid")
    context = _context("device-a")

    save_access_control_store({
        "policy": {},
        "identities": {
            identity: {
                "identityHashRef": identity[:12],
                "emailRef": "pi***@example.invalid",
                "status": "active",
                "contexts": [{
                    "contextHash": context["contextHash"],
                    "contextRef": context["contextRef"],
                    "status": "trusted",
                    "approval": "operator_approved",
                    "operatorNote": "approved for smoke",
                }],
            }
        },
    }, path=store)
    save_access_control_store({
        "policy": {},
        "identities": {
            identity: {
                "identityHashRef": identity[:12],
                "emailRef": "pi***@example.invalid",
                "status": "active",
                "contexts": [{
                    "contextHash": context["contextHash"],
                    "contextRef": context["contextRef"],
                    "status": "pending",
                    "approval": "operator_required",
                }],
            }
        },
    }, path=store)

    payload = load_access_control_store(store)
    saved_context = payload["identities"][identity]["contexts"][0]
    assert saved_context["status"] == "trusted"
    assert saved_context["approval"] == "operator_approved"


def test_evaluate_backfills_context_hash_for_operator_restored_context_ref(tmp_path):
    store = tmp_path / "remote_access_control.local.json"
    events = tmp_path / "events.local.jsonl"
    identity = email_hash("pilot@example.invalid")
    context = _context("device-a")
    payload = {
        "policy": {},
        "identities": {
            identity: {
                "identityHashRef": identity[:12],
                "emailRef": "pi***@example.invalid",
                "status": "active",
                "contexts": [{
                    "contextRef": context["contextRef"],
                    "status": "trusted",
                    "approval": "operator_approved",
                }],
            }
        },
    }
    save_access_control_store(payload, path=store)

    result = evaluate_access_context(identity, context, store_path=store, events_path=events)
    saved = load_access_control_store(store)
    contexts = saved["identities"][identity]["contexts"]

    assert result["accessControl"]["allowed"] is True
    assert len(contexts) == 1
    assert contexts[0]["contextHash"] == context["contextHash"]
    assert contexts[0]["approval"] == "operator_approved"
