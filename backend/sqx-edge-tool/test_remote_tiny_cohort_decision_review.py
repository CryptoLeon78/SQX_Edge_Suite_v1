import json

from core.remote_tiny_cohort_decision_review import (
    REMOTE_TINY_COHORT_DECISION_REVIEW_VERSION,
    build_remote8g_decision_review_summary,
    ingest_remote8g_tiny_cohort_decision_review,
)


def _complete_payload() -> dict:
    return {
        "schemaVersion": REMOTE_TINY_COHORT_DECISION_REVIEW_VERSION,
        "decisionId": "remote8g-tiny-cohort-decision-001",
        "capturedAt": "2026-05-16T20:00:00+00:00",
        "operatorApproval": True,
        "selectedDecision": "prepare_next_controlled_movement",
        "sourceGate": {
            "remote8fStatus": "GO_REMOTE8F_TINY_COHORT_MONITORING_CLEAN",
            "remote8fMonitoringId": "remote8f-tiny-cohort-monitoring-001",
        },
        "environment": {
            "protectedUrl": "https://private-live.example.invalid/sqx",
            "localPath": "C:/BOTS/private/live",
        },
        "monitoringSummary": {
            "observationHours": 24,
            "cohortUserCount": 3,
            "blockerCount": 0,
        },
        "reviewedUsers": [
            {
                "email": "buyer1@example.invalid",
                "kind": "paid_subscription",
                "featureScope": "full",
                "accessOutcomeReviewed": True,
                "supportOutcomeReviewed": True,
                "workspaceOutcomeReviewed": True,
                "entitlementOutcomeReviewed": True,
            },
            {
                "email": "tester2@example.invalid",
                "kind": "tester_free",
                "featureScope": "full",
                "accessOutcomeReviewed": True,
                "supportOutcomeReviewed": True,
                "workspaceOutcomeReviewed": True,
                "entitlementOutcomeReviewed": True,
            },
            {
                "email": "buyer3@example.invalid",
                "kind": "paid_subscription",
                "featureScope": "full",
                "accessOutcomeReviewed": True,
                "supportOutcomeReviewed": True,
                "workspaceOutcomeReviewed": True,
                "entitlementOutcomeReviewed": True,
            },
        ],
        "checks": {
            "remote8fMonitoringReviewed": True,
            "operatorDecisionRecorded": True,
            "decisionRationaleRecorded": True,
            "cohortSizeReviewed": True,
            "supportOwnerConfirmed": True,
            "rollbackPlanReady": True,
            "pauseRuleReady": True,
            "entitlementBoundaryReviewed": True,
            "workspaceIsolationReviewed": True,
            "securityReviewCompleted": True,
            "noAutomationConfirmed": True,
            "privateEvidenceStoredOutsideGit": True,
        },
        "executionMetrics": {
            "newUsersInvited": 0,
            "grantsChanged": 0,
            "checkoutLinksCreated": 0,
            "emailsSent": 0,
            "publicUrlsShared": 0,
            "automationJobsStarted": 0,
            "trafficExpanded": 0,
            "paidCampaignStarted": 0,
        },
    }


def test_remote8g_clean_decision_review_is_redacted_and_prepares_next_package(tmp_path):
    evidence_path = tmp_path / "remote8g_tiny_cohort_decision_review.local.json"
    evidence_path.write_text(json.dumps(_complete_payload()), encoding="utf-8")

    result = ingest_remote8g_tiny_cohort_decision_review(evidence_path=evidence_path, output_root=tmp_path / "out")
    serialized = json.dumps(result, sort_keys=True)

    assert result["ok"] is True
    assert result["version"] == REMOTE_TINY_COHORT_DECISION_REVIEW_VERSION
    assert result["status"] == "GO_REMOTE8G_TINY_COHORT_DECISION_REVIEW_READY"
    assert result["decisionReview"]["selectedDecision"] == "prepare_next_controlled_movement"
    assert result["decisionReview"]["reviewedUserCount"] == 3
    assert result["decision"]["ready"] is True
    assert result["decision"]["allowedNextAction"] == "prepare_remote8h_next_controlled_movement_package"
    assert result["decision"]["automationAllowed"] is False
    assert result["decision"]["executionAllowedNow"] is False
    assert result["safety"]["nextMovementPreparedOnly"] is True
    assert result["privacy"]["decisionRationaleReturned"] is False
    assert result["decisionReview"]["users"][0]["emailRef"] == "bu***@example.invalid"
    assert result["nextPhase"] == "REMOTE-8H-next-controlled-movement-package"

    assert "buyer1@example.invalid" not in serialized
    assert "tester2@example.invalid" not in serialized
    assert "https://" not in serialized
    assert "C:/BOTS" not in serialized
    assert (tmp_path / "out" / "remote8g_tiny_cohort_decision_review.public.json").is_file()


def test_remote8g_missing_evidence_returns_no_go(tmp_path):
    result = ingest_remote8g_tiny_cohort_decision_review(
        evidence_path=tmp_path / "missing.local.json",
        output_root=tmp_path / "out",
    )

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8G_DECISION_REVIEW_EVIDENCE_MISSING"
    assert result["error"] == "remote8g_decision_review_evidence_missing"
    assert result["decision"]["ready"] is False
    assert result["decision"]["automationAllowed"] is False
    assert (tmp_path / "out" / "remote8g_tiny_cohort_decision_review.public.json").is_file()


def test_remote8g_blockers_prevent_next_movement_package():
    payload = _complete_payload()
    payload["sourceGate"]["remote8fStatus"] = "NO_GO_REMOTE8F_TINY_COHORT_MONITORING_BLOCKED"
    payload["monitoringSummary"]["blockerCount"] = 2
    payload["reviewedUsers"] = payload["reviewedUsers"][:2]
    payload["reviewedUsers"][0]["supportOutcomeReviewed"] = False
    payload["checks"]["pauseRuleReady"] = False
    payload["executionMetrics"]["trafficExpanded"] = 1

    result = build_remote8g_decision_review_summary(payload)

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8G_TINY_COHORT_DECISION_REVIEW_BLOCKED"
    assert "prepare_next_movement_requires_clean_monitoring" in result["blockers"]
    assert "prepare_next_movement_requires_zero_monitoring_blockers" in result["blockers"]
    assert "reviewed_user_count_out_of_range" in result["blockers"]
    assert "required_checks_missing" in result["blockers"]
    assert "execution_metrics_must_remain_zero" in result["blockers"]
    assert "user_1_supportOutcomeReviewed_missing" in result["blockers"]
    assert result["missingChecks"] == ["pauseRuleReady"]
    assert result["executionBlockers"] == ["trafficExpanded"]
    assert result["decision"]["ready"] is False
    assert result["decision"]["executionAllowedNow"] is False
