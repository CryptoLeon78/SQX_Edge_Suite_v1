import json

from core.remote_live_pilot import (
    REMOTE_LIVE_PILOT_EVIDENCE_VERSION,
    build_remote8b_evidence_summary,
    ingest_remote8b_live_pilot_evidence,
)


def _complete_payload() -> dict:
    return {
        "schemaVersion": REMOTE_LIVE_PILOT_EVIDENCE_VERSION,
        "evidenceId": "remote8b-private-smoke-001",
        "capturedAt": "2026-05-16T13:00:00+00:00",
        "operatorApproval": True,
        "pilotUser": {
            "kind": "paid_subscription",
            "email": "livebuyer@example.invalid",
        },
        "environment": {
            "provider": "cloudflare_tunnel",
            "windowsPilot": True,
            "protectedUrlSharedPrivately": True,
            "protectedUrl": "https://private-live.example.invalid/sqx",
            "localPath": "C:/BOTS/private/live",
        },
        "proofs": {
            "remote8DrillBaselineGo": True,
            "edgeAccessBlockedAnonymous": True,
            "cloudflareAccessPassed": True,
            "appSessionLoginPassed": True,
            "entitlementActive": True,
            "workspaceCreated": True,
            "artifactGenerated": True,
            "exportDownloaded": True,
            "revocationBlockedAccess": True,
            "restoreAllowedAccess": True,
            "secondUserIsolationChecked": True,
            "noWorkspaceLeakage": True,
            "supportEvidenceRedacted": True,
            "privateEvidenceStoredOutsideGit": True,
        },
        "artifacts": {
            "generatedCfxName": "C:/BOTS/private/workspaces/remote8b_live_pilot.cfx",
            "artifactSha256": "a" * 64,
            "workspaceId": "workspace-private-id-123456",
            "workspacePath": "C:/BOTS/private/workspaces/ws",
        },
        "notes": ["Private support notes stay outside git."],
    }


def test_remote8b_live_pilot_evidence_go_redacts_private_values(tmp_path):
    evidence_path = tmp_path / "remote8b_live_pilot_evidence.local.json"
    evidence_path.write_text(json.dumps(_complete_payload()), encoding="utf-8")

    result = ingest_remote8b_live_pilot_evidence(evidence_path=evidence_path, output_root=tmp_path / "out")
    serialized = json.dumps(result, sort_keys=True)

    assert result["ok"] is True
    assert result["version"] == REMOTE_LIVE_PILOT_EVIDENCE_VERSION
    assert result["status"] == "GO_REMOTE8B_LIVE_PILOT_EVIDENCE_SAFE_NO_GIT_LEAK"
    assert result["evidence"]["emailRef"] == "li***@example.invalid"
    assert result["evidence"]["emailHashRef"]
    assert result["artifacts"]["generatedCfxName"] == "remote8b_live_pilot.cfx"
    assert result["artifacts"]["artifactSha256"] == "a" * 64
    assert result["artifacts"]["workspaceIdShort"] == "workspace-pr"
    assert result["privacy"]["rawEmailReturned"] is False
    assert result["privacy"]["protectedUrlReturned"] is False
    assert result["privacy"]["localPathsReturned"] is False
    assert result["expansionGate"]["allowedToExpandBeyondOneUser"] is False

    assert "livebuyer@example.invalid" not in serialized
    assert "https://" not in serialized
    assert "C:/BOTS" not in serialized
    assert "__Host-sqx_remote_session" not in serialized
    assert (tmp_path / "out" / "remote8b_live_pilot_evidence.public.json").is_file()


def test_remote8b_missing_evidence_returns_no_go(tmp_path):
    result = ingest_remote8b_live_pilot_evidence(
        evidence_path=tmp_path / "missing.local.json",
        output_root=tmp_path / "out",
    )

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8B_PRIVATE_EVIDENCE_MISSING"
    assert result["error"] == "remote8b_private_evidence_missing"
    assert result["expansionGate"]["allowedToExpandBeyondOneUser"] is False
    assert (tmp_path / "out" / "remote8b_live_pilot_evidence.public.json").is_file()


def test_remote8b_incomplete_evidence_blocks_expansion():
    payload = _complete_payload()
    payload["operatorApproval"] = False
    payload["proofs"]["noWorkspaceLeakage"] = False
    payload["schemaVersion"] = "old-version"

    result = build_remote8b_evidence_summary(payload)

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8B_LIVE_PILOT_EVIDENCE_BLOCKED"
    assert "operator_approval_missing" in result["blockers"]
    assert "required_proofs_missing" in result["blockers"]
    assert "remote8b_schema_version_mismatch" in result["blockers"]
    assert result["missingProofs"] == ["noWorkspaceLeakage"]
    assert result["expansionGate"]["allowedToExpandBeyondOneUser"] is False
