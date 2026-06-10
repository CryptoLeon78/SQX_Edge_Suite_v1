import json

from api import server
from core.remote_access import SESSION_COOKIE_NAME, create_signed_session, email_hash
from core.remote_template_maker_state import (
    REMOTE_TEMPLATE_MAKER_DB,
    REMOTE_TEMPLATE_MAKER_STATE_VERSION,
    read_template_maker_state,
    write_template_maker_state,
)
from core.remote_workspaces import derive_remote_workspace, workspace_id_from_identity_hash


def _session_status(email: str = "template-maker@example.invalid") -> dict:
    identity_hash = email_hash(email)
    return {
        "ok": True,
        "session": {
            "active": True,
            "email_hash": identity_hash,
            "email_ref": "tm***@example.invalid",
            "entitlement_kind": "paid_subscription",
            "feature_scope": "full",
        },
        "entitlement": {"kind": "paid_subscription", "status": "active"},
        "access": {"allowed": True, "feature_scope": "full"},
        "privacy": {"session_token_returned": False},
    }


def _context_ref_for_test(client, email: str = "template-maker@example.invalid"):
    headers = {"User-Agent": "pytest-template-maker", "Cf-Access-Authenticated-User-Email": email}
    probe = client.get("/api/remote/access-control/status", headers=headers, base_url="https://localhost")
    assert probe.status_code == 200
    return probe.get_json()["accessControl"]["contextRef"], headers


def _authorized_client(tmp_path, monkeypatch, email: str = "template-maker@example.invalid"):
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
    context_ref, headers = _context_ref_for_test(client, email=email)
    signed = create_signed_session(
        email,
        {"kind": "paid_subscription", "grant_id": "paid-1", "feature_scope": "full"},
        access_context_ref=context_ref,
    )
    client.set_cookie(SESSION_COOKIE_NAME, signed["token"])
    return client, headers, workspaces_root


def _snapshot(asset: str = "XAUUSD") -> dict:
    return {
        "templateMakerSchemaVersion": "template-maker-cert-v2",
        "strategies": [{
            "_id": 1,
            "Strategy Name": "Strategy TM.01",
            "Symbol": asset,
            "TimeFrame": "H1",
            "Fitness": "0.9",
            "sources": {"csv": {"fileName": "tm.csv"}},
            "metrics": {"Net profit": 1000},
            "provenance": {"events": [{"type": "imported"}]},
        }],
        "config": {
            "currentCapa": 1,
            "currentPreset": "Commodities",
            "thresholds": {"1": {"Profit factor": {"op": ">=", "val": 1.2}}},
            "diversitySettings": {"structuralThreshold": 0.7},
        },
        "metadata": {"source": "pytest"},
    }


def test_template_maker_state_persists_snapshot_in_workspace_sqlite(tmp_path):
    context = derive_remote_workspace(_session_status(), create=True, root=tmp_path)
    result = write_template_maker_state(context, _snapshot(), source="pytest")
    state = read_template_maker_state(context)

    assert result["ok"] is True
    assert result["version"] == REMOTE_TEMPLATE_MAKER_STATE_VERSION
    assert result["recordCount"] == 1
    assert state["strategies"][0]["Symbol"] == "XAUUSD"
    assert state["config"]["currentPreset"] == "Commodities"
    assert state["metadata"]["recordCount"] == 1
    assert (context["_paths"]["config"] / REMOTE_TEMPLATE_MAKER_DB).is_file()


def test_template_maker_endpoints_require_session_and_return_no_local_paths(tmp_path, monkeypatch):
    client = server.app.test_client()
    denied = client.get("/api/remote/template-maker/bootstrap")
    assert denied.status_code == 403
    assert denied.get_json()["privacy"]["local_paths_returned"] is False

    client, headers, workspaces_root = _authorized_client(tmp_path, monkeypatch)
    saved = client.post(
        "/api/remote/template-maker/save",
        json={"source": "pytest", "state": _snapshot("EURUSD")},
        headers=headers,
        base_url="https://localhost",
    )
    saved_data = saved.get_json()
    assert saved.status_code == 200
    assert saved_data["recordCount"] == 1
    assert saved_data["privacy"]["local_paths_returned"] is False
    assert "template-maker@example.invalid" not in json.dumps(saved_data)

    boot = client.get("/api/remote/template-maker/bootstrap", headers=headers, base_url="https://localhost")
    boot_data = boot.get_json()
    assert boot.status_code == 200
    assert boot_data["version"] == REMOTE_TEMPLATE_MAKER_STATE_VERSION
    assert boot_data["state"]["strategies"][0]["Symbol"] == "EURUSD"
    assert boot_data["privacy"]["local_paths_returned"] is False
    assert "template-maker@example.invalid" not in json.dumps(boot_data)

    status = client.get("/api/remote/template-maker/status", headers=headers, base_url="https://localhost")
    assert status.status_code == 200
    assert status.get_json()["storage"]["dbName"] == REMOTE_TEMPLATE_MAKER_DB
    assert "workspaces" not in json.dumps(status.get_json())

    workspace_id = workspace_id_from_identity_hash(email_hash("template-maker@example.invalid"))
    assert (workspaces_root / workspace_id / "config" / REMOTE_TEMPLATE_MAKER_DB).is_file()


def test_template_maker_state_is_separate_per_identity(tmp_path, monkeypatch):
    first, first_headers, _root = _authorized_client(tmp_path, monkeypatch, "first-tm@example.invalid")
    first.post(
        "/api/remote/template-maker/save",
        json={"state": _snapshot("XAUUSD")},
        headers=first_headers,
        base_url="https://localhost",
    )

    second, second_headers, _root = _authorized_client(tmp_path, monkeypatch, "second-tm@example.invalid")
    second_boot = second.get("/api/remote/template-maker/bootstrap", headers=second_headers, base_url="https://localhost")
    second_data = second_boot.get_json()

    assert second_boot.status_code == 200
    assert second_data["state"]["strategies"] == []
    assert workspace_id_from_identity_hash(email_hash("first-tm@example.invalid")) != workspace_id_from_identity_hash(email_hash("second-tm@example.invalid"))
