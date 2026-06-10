import json

from core.remote_next_controlled_movement_monitoring import (
    REMOTE_NEXT_CONTROLLED_MOVEMENT_MONITORING_VERSION,
    build_remote8k_monitoring_summary,
    ingest_remote8k_next_controlled_movement_monitoring,
)


def _complete_payload() -> dict:
    return {
        "schemaVersion": REMOTE_NEXT_CONTROLLED_MOVEMENT_MONITORING_VERSION,
        "monitoringId": "remote8k-monitoring-001",
        "capturedAt": "2026-05-17T00:00:00+00:00",
        "operatorReview": True,
        "requestedDecision": "prepare_next_decision_review",
        "observationHours": 24,
        "sourceGate": {
            "remote8jStatus": "GO_REMOTE8J_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION_RECORDED",
            "remote8jExecutionId": "remote8j-manual-execution-001",
            "movementType": "add_1_2_users",
            "executedUserCount": 1,
        },
        "environment": {
            "protectedUrl": "https://private-live.example.invalid/sqx",
            "localPath": "C:/BOTS/private/live",
        },
        "privateMonitoring": {
            "supportNote": "Private support observation stays local and ignored.",
        },
        "monitoredUsers": [
            {
                "email": "buyer4@example.invalid",
                "kind": "paid_subscription",
                "featureScope": "full",
                "accessVerified": True,
                "entitlementChecked": True,
                "workspaceIsolationChecked": True,
                "artifactFlowChecked": True,
                "supportWindowAcknowledged": True,
                "noCriticalIssue": True,
            },
        ],
        "signals": {
            "remote8jExecutionGoConfirmed": True,
            "manualScopeStillMatches": True,
            "accessStable": True,
            "cloudflareAccessStable": True,
            "appSessionStable": True,
            "entitlementStable": True,
            "workspaceIsolationClean": True,
            "artifactGenerationObserved": True,
            "exportsDownloaded": True,
            "supportLoopObserved": True,
            "noWorkspaceLeakage": True,
            "noSecurityIncidents": True,
            "noUnresolvedSupportBlockers": True,
            "rollbackPlanReady": True,
            "pauseRuleReady": True,
            "privateEvidenceStoredOutsideGit": True,
        },
        "zeroToleranceMetrics": {
            "openSupportItems": 0,
            "unresolvedBlockers": 0,
            "tunnelDrops": 0,
            "appSessionFailures": 0,
            "workspaceLeakEvents": 0,
            "securityIncidents": 0,
            "generationFailures": 0,
            "exportFailures": 0,
            "entitlementErrors": 0,
            "refundRequests": 0,
            "crossUserDataFindings": 0,
            "publicUrlLeaks": 0,
            "automationJobsStarted": 0,
            "trafficExpanded": 0,
            "paidCampaignStarted": 0,
            "checkoutLinksCreated": 0,
            "automatedEmailsSent": 0,
            "automatedGrantsCreated": 0,
        },
    }


def test_remote8k_clean_monitoring_is_redacted_and_ready_for_decision_review(tmp_path):
    evidence_path = tmp_path / "remote8k_next_controlled_movement_monitoring.local.json"
    evidence_path.write_text(json.dumps(_complete_payload()), encoding="utf-8")

    result = ingest_remote8k_next_controlled_movement_monitoring(
        evidence_path=evidence_path,
        output_root=tmp_path / "out",
    )
    serialized = json.dumps(result, sort_keys=True)

    assert result["ok"] is True
    assert result["version"] == REMOTE_NEXT_CONTROLLED_MOVEMENT_MONITORING_VERSION
    assert result["status"] == "GO_REMOTE8K_NEXT_CONTROLLED_MOVEMENT_MONITORING_CLEAN"
    assert result["monitoring"]["monitoredUserCount"] == 1
    assert result["monitoring"]["observationHours"] == 24
    assert result["decision"]["ready"] is True
    assert result["decision"]["allowedNextAction"] == "prepare_remote8l_post_monitoring_decision_review"
    assert result["decision"]["automationAllowed"] is False
    assert result["decision"]["furtherExpansionAllowedNow"] is False
    assert result["safety"]["rollbackReady"] is True
    assert result["safety"]["pauseRuleReady"] is True
    assert result["privacy"]["rawEmailsReturned"] is False
    assert result["privacy"]["protectedUrlReturned"] is False
    assert result["monitoring"]["users"][0]["emailRef"] == "bu***@example.invalid"
    assert result["nextPhase"] == "REMOTE-8L-post-monitoring-decision-review"

    assert "buyer4@example.invalid" not in serialized
    assert "Private support observation" not in serialized
    assert "https://" not in serialized
    assert "C:/BOTS" not in serialized
    assert (tmp_path / "out" / "remote8k_next_controlled_movement_monitoring.public.json").is_file()


def test_remote8k_missing_evidence_returns_no_go(tmp_path):
    result = ingest_remote8k_next_controlled_movement_monitoring(
        evidence_path=tmp_path / "missing.local.json",
        output_root=tmp_path / "out",
    )

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8K_MONITORING_EVIDENCE_MISSING"
    assert result["error"] == "remote8k_monitoring_evidence_missing"
    assert result["decision"]["ready"] is False
    assert result["decision"]["automationAllowed"] is False
    assert (tmp_path / "out" / "remote8k_next_controlled_movement_monitoring.public.json").is_file()


def test_remote8k_blockers_prevent_next_decision_review():
    payload = _complete_payload()
    payload["sourceGate"]["remote8jStatus"] = "NO_GO_REMOTE8J_MANUAL_EXECUTION_BLOCKED"
    payload["observationHours"] = 8
    payload["monitoredUsers"][0]["workspaceIsolationChecked"] = False
    payload["signals"]["noSecurityIncidents"] = False
    payload["zeroToleranceMetrics"]["securityIncidents"] = 1
    payload["zeroToleranceMetrics"]["trafficExpanded"] = 1

    result = build_remote8k_monitoring_summary(payload)

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8K_NEXT_CONTROLLED_MOVEMENT_MONITORING_BLOCKED"
    assert "remote8j_manual_execution_go_status_missing" in result["blockers"]
    assert "minimum_observation_hours_not_met" in result["blockers"]
    assert "required_signals_missing" in result["blockers"]
    assert "zero_tolerance_metrics_nonzero" in result["blockers"]
    assert "user_1_workspaceIsolationChecked_missing" in result["blockers"]
    assert result["missingSignals"] == ["noSecurityIncidents"]
    assert result["metricBlockers"] == ["securityIncidents", "trafficExpanded"]
    assert result["decision"]["ready"] is False
    assert result["decision"]["furtherExpansionAllowedNow"] is False
