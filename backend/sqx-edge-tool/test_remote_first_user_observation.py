import json

from core.remote_first_user_observation import (
    REMOTE_FIRST_USER_OBSERVATION_VERSION,
    build_remote8c_observation_summary,
    ingest_remote8c_first_user_observation,
)


def _complete_payload() -> dict:
    return {
        "schemaVersion": REMOTE_FIRST_USER_OBSERVATION_VERSION,
        "observationId": "remote8c-first-user-001",
        "capturedAt": "2026-05-16T14:00:00+00:00",
        "operatorApproval": True,
        "requestedDecision": "expand_3_5",
        "observationWindowHours": 36,
        "pilotUser": {
            "kind": "paid_subscription",
            "email": "firstbuyer@example.invalid",
        },
        "previousGate": {
            "remote8bStatus": "GO_REMOTE8B_LIVE_PILOT_EVIDENCE_SAFE_NO_GIT_LEAK",
            "remote8bEvidenceId": "remote8b-private-smoke-001",
        },
        "environment": {
            "provider": "cloudflare_tunnel",
            "protectedUrl": "https://private-live.example.invalid/sqx",
            "localPath": "C:/BOTS/private/live",
        },
        "signals": {
            "remote8bEvidenceGo": True,
            "firstUserCompletedGuidedFlow": True,
            "supportLoopObserved": True,
            "tunnelStable": True,
            "appSessionStable": True,
            "entitlementStable": True,
            "workspaceIsolationClean": True,
            "artifactGenerated": True,
            "exportDownloaded": True,
            "revocationRestoreConfidence": True,
            "noWorkspaceLeakage": True,
            "noSecurityIncidents": True,
            "noUnresolvedSupportBlockers": True,
            "supportEvidenceRedacted": True,
            "privateEvidenceStoredOutsideGit": True,
        },
        "metrics": {
            "openSupportItems": 0,
            "unresolvedBlockers": 0,
            "tunnelDrops": 0,
            "appSessionFailures": 0,
            "workspaceLeakEvents": 0,
            "securityIncidents": 0,
            "generationFailures": 0,
            "entitlementErrors": 0,
            "refundRequests": 0,
            "supportResponseHours": 1.5,
        },
        "artifacts": {
            "workspacePath": "C:/BOTS/private/workspaces/ws",
        },
    }


def test_remote8c_clean_first_user_observation_allows_only_manual_tiny_cohort(tmp_path):
    evidence_path = tmp_path / "remote8c_first_user_observation.local.json"
    evidence_path.write_text(json.dumps(_complete_payload()), encoding="utf-8")

    result = ingest_remote8c_first_user_observation(evidence_path=evidence_path, output_root=tmp_path / "out")
    serialized = json.dumps(result, sort_keys=True)

    assert result["ok"] is True
    assert result["version"] == REMOTE_FIRST_USER_OBSERVATION_VERSION
    assert result["status"] == "GO_REMOTE8C_TINY_COHORT_EXPANSION_READY"
    assert result["observation"]["emailRef"] == "fi***@example.invalid"
    assert result["observation"]["emailHashRef"]
    assert result["expansionGate"]["allowedToExpandToTinyCohort"] is True
    assert result["expansionGate"]["targetTotalUsers"] == "3-5"
    assert result["decision"]["automationAllowed"] is False
    assert result["decision"]["manualOperatorStepRequired"] is True
    assert result["privacy"]["rawEmailReturned"] is False
    assert result["privacy"]["supportLogsReturned"] is False

    assert "firstbuyer@example.invalid" not in serialized
    assert "https://" not in serialized
    assert "C:/BOTS" not in serialized
    assert (tmp_path / "out" / "remote8c_first_user_observation.public.json").is_file()


def test_remote8c_missing_evidence_returns_no_go(tmp_path):
    result = ingest_remote8c_first_user_observation(
        evidence_path=tmp_path / "missing.local.json",
        output_root=tmp_path / "out",
    )

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8C_OBSERVATION_EVIDENCE_MISSING"
    assert result["error"] == "remote8c_observation_evidence_missing"
    assert result["expansionGate"]["allowedToExpandToTinyCohort"] is False
    assert (tmp_path / "out" / "remote8c_first_user_observation.public.json").is_file()


def test_remote8c_blockers_prevent_expansion():
    payload = _complete_payload()
    payload["observationWindowHours"] = 8
    payload["signals"]["tunnelStable"] = False
    payload["metrics"]["generationFailures"] = 1
    payload["requestedDecision"] = "expand_3_5"

    result = build_remote8c_observation_summary(payload)

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8C_FIRST_USER_OBSERVATION_BLOCKED"
    assert "observation_window_too_short" in result["blockers"]
    assert "required_signals_missing" in result["blockers"]
    assert "zero_tolerance_metrics_nonzero" in result["blockers"]
    assert result["missingSignals"] == ["tunnelStable"]
    assert result["metricBlockers"] == ["generationFailures"]
    assert result["expansionGate"]["allowedToExpandToTinyCohort"] is False
