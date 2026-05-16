import json

from core.remote_post_monitoring_decision_review import (
    REMOTE_POST_MONITORING_DECISION_REVIEW_VERSION,
    build_remote8l_decision_review_summary,
    ingest_remote8l_post_monitoring_decision_review,
)


def _complete_payload() -> dict:
    return {
        "schemaVersion": REMOTE_POST_MONITORING_DECISION_REVIEW_VERSION,
        "decisionId": "remote8l-post-monitoring-decision-001",
        "capturedAt": "2026-05-17T12:00:00+00:00",
        "operatorApproval": True,
        "selectedDecision": "prepare_next_controlled_movement",
        "sourceGate": {
            "remote8kStatus": "GO_REMOTE8K_NEXT_CONTROLLED_MOVEMENT_MONITORING_CLEAN",
            "remote8kMonitoringId": "remote8k-monitoring-001",
            "remote8kRequestedDecision": "prepare_next_decision_review",
            "movementType": "add_1_2_users",
            "monitoredUserCount": 1,
            "observationHours": 24,
            "monitoringBlockerCount": 0,
        },
        "environment": {
            "protectedUrl": "https://private-live.example.invalid/sqx",
            "localPath": "C:/BOTS/private/live",
        },
        "privateDecision": {
            "rationale": "Private operator rationale stays local and ignored.",
        },
        "reviewedUsers": [
            {
                "email": "buyer4@example.invalid",
                "kind": "paid_subscription",
                "featureScope": "full",
                "accessOutcomeReviewed": True,
                "entitlementOutcomeReviewed": True,
                "workspaceOutcomeReviewed": True,
                "artifactOutcomeReviewed": True,
                "supportOutcomeReviewed": True,
                "noNewCriticalIssue": True,
            },
        ],
        "checks": {
            "remote8kMonitoringReviewed": True,
            "operatorDecisionRecorded": True,
            "decisionRationaleRecorded": True,
            "sourceStatusReviewed": True,
            "monitoringWindowReviewed": True,
            "supportOutcomeReviewed": True,
            "workspaceIsolationReviewed": True,
            "securityOutcomeReviewed": True,
            "entitlementOutcomeReviewed": True,
            "generationExportOutcomeReviewed": True,
            "rollbackPlanReady": True,
            "pauseRuleReady": True,
            "noAutomationConfirmed": True,
            "privateEvidenceStoredOutsideGit": True,
        },
        "zeroExecutionMetrics": {
            "newUsersInvited": 0,
            "grantsChanged": 0,
            "checkoutLinksCreated": 0,
            "emailsSent": 0,
            "publicUrlsShared": 0,
            "protectedUrlsShared": 0,
            "automationJobsStarted": 0,
            "trafficExpanded": 0,
            "paidCampaignStarted": 0,
            "automatedEmailsSent": 0,
            "automatedGrantsCreated": 0,
            "entitlementsChanged": 0,
        },
    }


def test_remote8l_clean_decision_review_is_redacted_and_prepares_next_package(tmp_path):
    evidence_path = tmp_path / "remote8l_post_monitoring_decision_review.local.json"
    evidence_path.write_text(json.dumps(_complete_payload()), encoding="utf-8")

    result = ingest_remote8l_post_monitoring_decision_review(evidence_path=evidence_path, output_root=tmp_path / "out")
    serialized = json.dumps(result, sort_keys=True)

    assert result["ok"] is True
    assert result["version"] == REMOTE_POST_MONITORING_DECISION_REVIEW_VERSION
    assert result["status"] == "GO_REMOTE8L_POST_MONITORING_DECISION_REVIEW_READY"
    assert result["decisionReview"]["selectedDecision"] == "prepare_next_controlled_movement"
    assert result["decisionReview"]["reviewedUserCount"] == 1
    assert result["decision"]["ready"] is True
    assert result["decision"]["allowedNextAction"] == "prepare_remote8h_next_controlled_movement_package"
    assert result["decision"]["automationAllowed"] is False
    assert result["decision"]["executionAllowedNow"] is False
    assert result["decision"]["furtherExpansionAllowedNow"] is False
    assert result["safety"]["nextMovementPreparedOnly"] is True
    assert result["privacy"]["decisionRationaleReturned"] is False
    assert result["decisionReview"]["users"][0]["emailRef"] == "bu***@example.invalid"
    assert result["nextPhase"] == "REMOTE-8H-next-controlled-movement-package"

    assert "buyer4@example.invalid" not in serialized
    assert "Private operator rationale" not in serialized
    assert "https://" not in serialized
    assert "C:/BOTS" not in serialized
    assert (tmp_path / "out" / "remote8l_post_monitoring_decision_review.public.json").is_file()


def test_remote8l_missing_evidence_returns_no_go(tmp_path):
    result = ingest_remote8l_post_monitoring_decision_review(
        evidence_path=tmp_path / "missing.local.json",
        output_root=tmp_path / "out",
    )

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8L_DECISION_REVIEW_EVIDENCE_MISSING"
    assert result["error"] == "remote8l_decision_review_evidence_missing"
    assert result["decision"]["ready"] is False
    assert result["decision"]["automationAllowed"] is False
    assert (tmp_path / "out" / "remote8l_post_monitoring_decision_review.public.json").is_file()


def test_remote8l_blockers_prevent_next_movement_package():
    payload = _complete_payload()
    payload["sourceGate"]["remote8kStatus"] = "NO_GO_REMOTE8K_NEXT_CONTROLLED_MOVEMENT_MONITORING_BLOCKED"
    payload["sourceGate"]["remote8kRequestedDecision"] = "continue_monitoring"
    payload["sourceGate"]["observationHours"] = 8
    payload["sourceGate"]["monitoringBlockerCount"] = 2
    payload["reviewedUsers"][0]["workspaceOutcomeReviewed"] = False
    payload["checks"]["pauseRuleReady"] = False
    payload["zeroExecutionMetrics"]["trafficExpanded"] = 1

    result = build_remote8l_decision_review_summary(payload)

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8L_POST_MONITORING_DECISION_REVIEW_BLOCKED"
    assert "prepare_next_movement_requires_clean_monitoring" in result["blockers"]
    assert "prepare_next_movement_requires_remote8k_decision_review_request" in result["blockers"]
    assert "prepare_next_movement_requires_zero_monitoring_blockers" in result["blockers"]
    assert "minimum_observation_hours_not_met" in result["blockers"]
    assert "required_checks_missing" in result["blockers"]
    assert "execution_metrics_must_remain_zero" in result["blockers"]
    assert "user_1_workspaceOutcomeReviewed_missing" in result["blockers"]
    assert result["missingChecks"] == ["pauseRuleReady"]
    assert result["executionBlockers"] == ["trafficExpanded"]
    assert result["decision"]["ready"] is False
    assert result["decision"]["furtherExpansionAllowedNow"] is False
