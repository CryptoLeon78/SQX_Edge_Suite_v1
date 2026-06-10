import json

from core.remote_next_controlled_movement_package import (
    REMOTE_NEXT_CONTROLLED_MOVEMENT_PACKAGE_VERSION,
    build_remote8h_movement_package_summary,
    ingest_remote8h_next_controlled_movement_package,
)


def _complete_payload() -> dict:
    return {
        "schemaVersion": REMOTE_NEXT_CONTROLLED_MOVEMENT_PACKAGE_VERSION,
        "packageId": "remote8h-next-movement-001",
        "capturedAt": "2026-05-16T22:00:00+00:00",
        "operatorApproval": True,
        "requestedAction": "prepare_next_controlled_movement_package",
        "sourceGate": {
            "sourceType": "remote8l_post_monitoring_decision_review",
            "remote8lStatus": "GO_REMOTE8L_POST_MONITORING_DECISION_REVIEW_READY",
            "remote8lSelectedDecision": "prepare_next_controlled_movement",
            "remote8lDecisionId": "remote8l-post-monitoring-decision-001",
        },
        "environment": {
            "protectedUrl": "https://private-live.example.invalid/sqx",
            "localPath": "C:/BOTS/private/live",
        },
        "movement": {
            "type": "add_1_2_users",
            "plannedNewUsers": 1,
            "supportWindowHours": 24,
            "maxDurationDays": 7,
        },
        "candidateUsers": [
            {
                "email": "buyer4@example.invalid",
                "kind": "paid_subscription",
                "featureScope": "full",
                "recipientReviewed": True,
                "entitlementKindReviewed": True,
                "supportExpectationReviewed": True,
                "privateHandoffRequired": True,
            },
        ],
        "checks": {
            "sourceDecisionReviewed": True,
            "oneMovementOnly": True,
            "scopeLimited": True,
            "recipientListPrivate": True,
            "entitlementBoundaryDefined": True,
            "supportOwnerAssigned": True,
            "supportWindowReady": True,
            "rollbackPlanReady": True,
            "pauseRuleReady": True,
            "noAutomationConfirmed": True,
            "executionRequiresSeparateApproval": True,
            "privateEvidenceStoredOutsideGit": True,
        },
        "executionMetrics": {
            "newUsersInvited": 0,
            "grantsCreated": 0,
            "checkoutLinksCreated": 0,
            "emailsSent": 0,
            "publicUrlsShared": 0,
            "automationJobsStarted": 0,
            "trafficExpanded": 0,
            "paidCampaignStarted": 0,
        },
    }


def test_remote8h_clean_package_is_redacted_and_requires_execution_approval(tmp_path):
    evidence_path = tmp_path / "remote8h_next_controlled_movement_package.local.json"
    evidence_path.write_text(json.dumps(_complete_payload()), encoding="utf-8")

    result = ingest_remote8h_next_controlled_movement_package(evidence_path=evidence_path, output_root=tmp_path / "out")
    serialized = json.dumps(result, sort_keys=True)

    assert result["ok"] is True
    assert result["version"] == REMOTE_NEXT_CONTROLLED_MOVEMENT_PACKAGE_VERSION
    assert result["status"] == "GO_REMOTE8H_NEXT_CONTROLLED_MOVEMENT_PACKAGE_READY"
    assert result["package"]["movement"]["type"] == "add_1_2_users"
    assert result["package"]["candidateCount"] == 1
    assert result["sourceGate"]["sourceType"] == "remote8l_post_monitoring_decision_review"
    assert result["movementPackage"]["ready"] is True
    assert result["movementPackage"]["allowedNextAction"] == "request_remote8i_execution_approval"
    assert result["movementPackage"]["automationAllowed"] is False
    assert result["movementPackage"]["executionAllowedNow"] is False
    assert result["movementPackage"]["requiresSeparateExecutionApproval"] is True
    assert result["privacy"]["rawEmailsReturned"] is False
    assert result["privacy"]["communicationCopyReturned"] is False
    assert result["package"]["candidates"][0]["emailRef"] == "bu***@example.invalid"
    assert result["nextPhase"] == "REMOTE-8I-next-controlled-movement-execution-approval"

    assert "buyer4@example.invalid" not in serialized
    assert "https://" not in serialized
    assert "C:/BOTS" not in serialized
    assert (tmp_path / "out" / "remote8h_next_controlled_movement_package.public.json").is_file()


def test_remote8h_missing_evidence_returns_no_go(tmp_path):
    result = ingest_remote8h_next_controlled_movement_package(
        evidence_path=tmp_path / "missing.local.json",
        output_root=tmp_path / "out",
    )

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8H_MOVEMENT_PACKAGE_EVIDENCE_MISSING"
    assert result["error"] == "remote8h_movement_package_evidence_missing"
    assert result["movementPackage"]["ready"] is False
    assert result["movementPackage"]["executionAllowedNow"] is False
    assert (tmp_path / "out" / "remote8h_next_controlled_movement_package.public.json").is_file()


def test_remote8h_blockers_prevent_package_ready():
    payload = _complete_payload()
    payload["sourceGate"]["remote8lStatus"] = "NO_GO_REMOTE8L_POST_MONITORING_DECISION_REVIEW_BLOCKED"
    payload["sourceGate"]["remote8lSelectedDecision"] = "continue_monitoring"
    payload["movement"]["plannedNewUsers"] = 3
    payload["movement"]["supportWindowHours"] = 4
    payload["candidateUsers"][0]["privateHandoffRequired"] = False
    payload["checks"]["pauseRuleReady"] = False
    payload["executionMetrics"]["emailsSent"] = 1

    result = build_remote8h_movement_package_summary(payload)

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8H_NEXT_CONTROLLED_MOVEMENT_PACKAGE_BLOCKED"
    assert "remote8l_decision_go_status_missing" in result["blockers"]
    assert "remote8l_selected_decision_not_next_movement" in result["blockers"]
    assert "planned_new_users_exceeds_limit" in result["blockers"]
    assert "candidate_count_must_match_planned_new_users" in result["blockers"]
    assert "support_window_too_short" in result["blockers"]
    assert "required_checks_missing" in result["blockers"]
    assert "execution_metrics_must_remain_zero" in result["blockers"]
    assert "candidate_1_privateHandoffRequired_missing" in result["blockers"]
    assert result["missingChecks"] == ["pauseRuleReady"]
    assert result["executionBlockers"] == ["emailsSent"]
    assert result["movementPackage"]["ready"] is False


def test_remote8h_legacy_remote8g_source_still_supported():
    payload = _complete_payload()
    payload["sourceGate"] = {
        "remote8gStatus": "GO_REMOTE8G_TINY_COHORT_DECISION_REVIEW_READY",
        "remote8gSelectedDecision": "prepare_next_controlled_movement",
        "remote8gDecisionId": "remote8g-tiny-cohort-decision-001",
    }
    payload["checks"].pop("sourceDecisionReviewed")
    payload["checks"]["remote8gDecisionReviewed"] = True

    result = build_remote8h_movement_package_summary(payload)

    assert result["ok"] is True
    assert result["status"] == "GO_REMOTE8H_NEXT_CONTROLLED_MOVEMENT_PACKAGE_READY"
    assert result["sourceGate"]["sourceType"] == "remote8g_tiny_cohort_decision_review"
