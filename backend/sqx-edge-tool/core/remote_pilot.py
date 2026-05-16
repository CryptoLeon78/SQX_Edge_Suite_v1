from __future__ import annotations

import hashlib
import json
import os
import shutil
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping

from core.remote_access import (
    REMOTE_ACCESS_VERSION,
    REMOTE_SESSION_VERSION,
    email_hash,
    evaluate_remote_session,
    start_remote_session_from_headers,
)
from core.remote_payments import (
    PAYMENT_WEBHOOK_SECRET_ENV,
    REMOTE_PAYMENT_WEBHOOK_VERSION,
    process_payment_webhook,
    sign_payment_webhook_body,
)
from core.remote_security import REMOTE_SECURITY_VERSION
from core.remote_workspaces import (
    REMOTE_WORKSPACE_VERSION,
    append_workspace_audit_event,
    derive_remote_workspace,
    public_workspace_context,
)


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_CONTROLLED_PILOT_VERSION = "remote-controlled-pilot-v1"
DEFAULT_REMOTE8_ROOT = PROJECT_ROOT / ".local" / "remote_service" / "remote8_controlled_pilot"
DEFAULT_PILOT_EMAIL = "remote8-buyer@example.invalid"
DEFAULT_SECOND_EMAIL = "remote8-second@example.invalid"
LOCAL_ONLY_ENV = (
    "SQX_REMOTE_ENTITLEMENTS_PATH",
    "SQX_REMOTE_WORKSPACES_ROOT",
    "SQX_REMOTE_SECURITY_POLICY_PATH",
    "SQX_REMOTE_SESSION_SECRET",
    PAYMENT_WEBHOOK_SECRET_ENV,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_id(now: datetime | None = None) -> str:
    current = now or datetime.now(timezone.utc)
    return current.strftime("run-%Y%m%d-%H%M%S")


def _json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _payment_signature(raw_body: bytes, secret: str) -> str:
    return "sha256=" + sign_payment_webhook_body(raw_body, secret)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_security_policy(path: Path) -> None:
    _write_json(path, {
        "schemaVersion": REMOTE_SECURITY_VERSION,
        "killSwitch": {"active": False, "reason": "remote8_controlled_pilot"},
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
    })


@contextmanager
def _temporary_remote_env(values: Mapping[str, str]) -> Iterator[None]:
    previous = {key: os.environ.get(key) for key in LOCAL_ONLY_ENV}
    try:
        for key, value in values.items():
            os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _activate_paid_entitlement(
    *,
    email: str,
    event_id: str,
    store_path: Path,
    audit_path: Path,
    secret: str,
) -> dict[str, Any]:
    raw = _json_bytes({
        "eventId": event_id,
        "eventType": "subscription_activated",
        "email": email,
        "subscriptionId": f"sub_{event_id}",
        "customerId": f"cus_{event_id}",
        "provider": "remote8_controlled_pilot",
    })
    return process_payment_webhook(
        raw,
        _payment_signature(raw, secret),
        store_path=store_path,
        secret=secret,
        audit_path=audit_path,
    )


def _cancel_paid_entitlement(
    *,
    email: str,
    event_id: str,
    store_path: Path,
    audit_path: Path,
    secret: str,
) -> dict[str, Any]:
    raw = _json_bytes({
        "eventId": event_id,
        "eventType": "subscription_cancelled",
        "email": email,
        "provider": "remote8_controlled_pilot",
    })
    return process_payment_webhook(
        raw,
        _payment_signature(raw, secret),
        store_path=store_path,
        secret=secret,
        audit_path=audit_path,
    )


def _start_session(email: str) -> dict[str, Any]:
    return start_remote_session_from_headers(
        {"Cf-Access-Authenticated-User-Email": email},
        {},
    )


def _write_pilot_artifact(workspace_context: Mapping[str, Any], run_id: str) -> dict[str, Any]:
    paths = workspace_context.get("_paths")
    workspace = workspace_context.get("workspace") if isinstance(workspace_context.get("workspace"), Mapping) else {}
    if not isinstance(paths, Mapping) or not isinstance(paths.get("outputs"), Path) or not isinstance(paths.get("exports"), Path):
        raise ValueError("remote8_workspace_paths_missing")
    filename = f"{run_id}_remote8_controlled_pilot.cfx"
    content = "\n".join([
        "<SQXEdgeRemotePilot>",
        f"  <Version>{REMOTE_CONTROLLED_PILOT_VERSION}</Version>",
        f"  <Workspace>{workspace.get('id')}</Workspace>",
        f"  <GeneratedAt>{_utc_now()}</GeneratedAt>",
        "  <Purpose>Controlled pilot artifact; not a trading promise.</Purpose>",
        "</SQXEdgeRemotePilot>",
        "",
    ]).encode("utf-8")
    output_path = paths["outputs"] / filename
    export_path = paths["exports"] / filename
    output_path.write_bytes(content)
    shutil.copyfile(output_path, export_path)
    digest = _sha256_bytes(content)
    return {
        "filename": filename,
        "sha256": digest,
        "bytes": len(content),
        "_output_path": output_path,
        "_export_path": export_path,
    }


def run_controlled_pilot_drill(
    *,
    base_dir: str | Path | None = None,
    run_id: str | None = None,
    pilot_email: str = DEFAULT_PILOT_EMAIL,
    second_email: str = DEFAULT_SECOND_EMAIL,
    secret: str = "remote8-controlled-pilot-secret-0001",
) -> dict[str, Any]:
    """Run a local-only REMOTE-8 pilot drill and return a public-safe summary."""
    base = Path(base_dir).expanduser().resolve(strict=False) if base_dir else DEFAULT_REMOTE8_ROOT
    active_run_id = run_id or _run_id()
    run_dir = base / active_run_id
    store_path = run_dir / "remote_entitlements.local.json"
    payment_audit_path = run_dir / "remote_payment_webhook_events.local.jsonl"
    security_policy_path = run_dir / "remote_security.local.json"
    workspaces_root = run_dir / "workspaces"
    summary_path = run_dir / "remote8_controlled_pilot.public.json"
    local_manifest_path = run_dir / "remote8_controlled_pilot.local.json"
    restore_snapshot_path = run_dir / "restore_snapshot.local.json"
    run_dir.mkdir(parents=True, exist_ok=True)
    _write_security_policy(security_policy_path)

    env = {
        "SQX_REMOTE_ENTITLEMENTS_PATH": str(store_path),
        "SQX_REMOTE_WORKSPACES_ROOT": str(workspaces_root),
        "SQX_REMOTE_SECURITY_POLICY_PATH": str(security_policy_path),
        "SQX_REMOTE_SESSION_SECRET": secret,
        PAYMENT_WEBHOOK_SECRET_ENV: secret,
    }
    with _temporary_remote_env(env):
        activation = _activate_paid_entitlement(
            email=pilot_email,
            event_id=f"{active_run_id}_activate",
            store_path=store_path,
            audit_path=payment_audit_path,
            secret=secret,
        )
        session = _start_session(pilot_email)
        token = str(session.get("session_token") or "")
        session_status = evaluate_remote_session(token)
        workspace_context = derive_remote_workspace(session_status, create=True, root=workspaces_root)
        artifact = _write_pilot_artifact(workspace_context, active_run_id)
        append_workspace_audit_event(workspace_context, {
            "type": "remote8_artifact_generated",
            "action": "generate_cfx_pilot_artifact",
            "identityHash": (session_status.get("session") or {}).get("email_hash"),
            "emailRef": (session_status.get("session") or {}).get("email_ref"),
            "entitlementKind": (session_status.get("entitlement") or {}).get("kind"),
            "featureScope": session_status.get("access", {}).get("feature_scope"),
            "artifactName": artifact["filename"],
            "artifactSha256": artifact["sha256"],
        })
        exported_bytes = artifact["_export_path"].read_bytes()
        export_verified = _sha256_bytes(exported_bytes) == artifact["sha256"]
        append_workspace_audit_event(workspace_context, {
            "type": "remote8_artifact_exported",
            "action": "export_download_pilot_artifact",
            "identityHash": (session_status.get("session") or {}).get("email_hash"),
            "emailRef": (session_status.get("session") or {}).get("email_ref"),
            "artifactName": artifact["filename"],
            "artifactSha256": artifact["sha256"],
        })

        second_activation = _activate_paid_entitlement(
            email=second_email,
            event_id=f"{active_run_id}_second_activate",
            store_path=store_path,
            audit_path=payment_audit_path,
            secret=secret,
        )
        second_session = _start_session(second_email)
        second_status = evaluate_remote_session(str(second_session.get("session_token") or ""))
        second_workspace_context = derive_remote_workspace(second_status, create=True, root=workspaces_root)
        second_paths = second_workspace_context.get("_paths")
        first_artifact_visible_in_second_workspace = False
        if isinstance(second_paths, Mapping):
            for key in ("outputs", "exports"):
                folder = second_paths.get(key)
                if isinstance(folder, Path) and (folder / artifact["filename"]).exists():
                    first_artifact_visible_in_second_workspace = True

        restore_snapshot_path.write_text(store_path.read_text(encoding="utf-8"), encoding="utf-8")
        cancellation = _cancel_paid_entitlement(
            email=pilot_email,
            event_id=f"{active_run_id}_cancel",
            store_path=store_path,
            audit_path=payment_audit_path,
            secret=secret,
        )
        revoked_status = evaluate_remote_session(token)
        store_path.write_text(restore_snapshot_path.read_text(encoding="utf-8"), encoding="utf-8")
        restored_status = evaluate_remote_session(token)
        append_workspace_audit_event(workspace_context, {
            "type": "remote8_restore_verified",
            "action": "restore_entitlement_snapshot",
            "identityHash": (session_status.get("session") or {}).get("email_hash"),
            "emailRef": (session_status.get("session") or {}).get("email_ref"),
        })

    workspace_public = public_workspace_context(workspace_context)
    second_workspace_public = public_workspace_context(second_workspace_context)
    identity_hash = email_hash(pilot_email)
    public_summary: dict[str, Any] = {
        "ok": True,
        "version": REMOTE_CONTROLLED_PILOT_VERSION,
        "mode": "local_controlled_drill",
        "runId": active_run_id,
        "generatedAt": _utc_now(),
        "versions": {
            "access": REMOTE_ACCESS_VERSION,
            "session": REMOTE_SESSION_VERSION,
            "paymentWebhook": REMOTE_PAYMENT_WEBHOOK_VERSION,
            "workspace": REMOTE_WORKSPACE_VERSION,
            "security": REMOTE_SECURITY_VERSION,
        },
        "identity": {
            "emailRef": (session.get("session") or {}).get("email_ref"),
            "emailHashRef": identity_hash[:12],
        },
        "phases": {
            "paymentWebhook": {
                "ok": bool(activation.get("ok")),
                "entitlementStatus": (activation.get("entitlement") or {}).get("status"),
                "rawEmailReturned": False,
            },
            "login": {
                "ok": bool(session.get("ok")),
                "sessionActive": bool((session.get("session") or {}).get("active")),
                "cookieName": session.get("cookie_name"),
                "sessionTokenReturnedInSummary": False,
            },
            "workspace": {
                "ok": bool(workspace_context.get("ok")),
                "id": workspace_public.get("id"),
                "layout": workspace_public.get("layout"),
                "localPathsReturned": False,
            },
            "artifactGeneration": {
                "ok": True,
                "filename": artifact["filename"],
                "sha256": artifact["sha256"],
                "bytes": artifact["bytes"],
                "localPathReturned": False,
            },
            "exportDownload": {
                "ok": export_verified,
                "filename": artifact["filename"],
                "sha256Matches": export_verified,
                "localPathReturned": False,
            },
            "isolation": {
                "ok": bool(second_activation.get("ok")) and bool(second_workspace_context.get("ok")) and not first_artifact_visible_in_second_workspace,
                "secondWorkspaceId": second_workspace_public.get("id"),
                "sameWorkspace": workspace_public.get("id") == second_workspace_public.get("id"),
                "firstArtifactVisibleInSecondWorkspace": first_artifact_visible_in_second_workspace,
            },
            "revocation": {
                "ok": bool(cancellation.get("ok")) and not bool((revoked_status.get("access") or {}).get("allowed")),
                "entitlementStatus": (cancellation.get("entitlement") or {}).get("status"),
                "accessAllowedAfterCancel": bool((revoked_status.get("access") or {}).get("allowed")),
                "reason": (revoked_status.get("access") or {}).get("reason"),
            },
            "restore": {
                "ok": bool((restored_status.get("access") or {}).get("allowed")),
                "accessAllowedAfterRestore": bool((restored_status.get("access") or {}).get("allowed")),
                "reason": (restored_status.get("access") or {}).get("reason"),
            },
        },
        "privacy": {
            "rawEmailReturned": False,
            "sessionTokenReturned": False,
            "grantKeysReturned": False,
            "localPathsReturned": False,
            "secretsReturned": False,
        },
        "expansionGate": {
            "allowedToExpandBeyondOneUser": False,
            "reason": "requires_private_live_smoke_and_operator_approval",
        },
    }
    public_summary["ok"] = all(bool(phase.get("ok")) for phase in public_summary["phases"].values())

    serialized = json.dumps(public_summary, sort_keys=True)
    if pilot_email in serialized or second_email in serialized:
        raise ValueError("remote8_public_summary_leaked_raw_email")
    _write_json(summary_path, public_summary)
    _write_json(local_manifest_path, {
        "schemaVersion": REMOTE_CONTROLLED_PILOT_VERSION,
        "runId": active_run_id,
        "summaryPath": str(summary_path),
        "localOnlyPaths": {
            "runDir": str(run_dir),
            "entitlementStore": str(store_path),
            "workspaceRoot": str(workspaces_root),
        },
        "privacy": {"committed": False, "localOnly": True},
    })
    return public_summary
