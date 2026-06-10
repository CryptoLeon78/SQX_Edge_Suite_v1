import json

from core.remote_next_controlled_movement_execution_approval import (
    REMOTE_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVAL_VERSION,
    build_remote8i_execution_approval_summary,
    ingest_remote8i_next_controlled_movement_execution_approval,
)


def _complete_payload() -> dict:
    return {
        "schemaVersion": REMOTE_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVAL_VERSION,
        "approvalId": "remote8i-approval-001",
        "capturedAt": "2026-05-16T23:00:00+00:00",
        "operatorApproval": True,
        "requestedAction": "approve_or_reject_next_controlled_movement_execution",
        "sourceGate": {
            "remote8hStatus": "GO_REMOTE8H_NEXT_CONTROLLED_MOVEMENT_PACKAGE_READY",
            "remote8hPackageId": "remote8h-next-movement-001",
            "remote8hMovementType": "add_1_2_users",
            "plannedNewUsers": 1,
            "candidateCount": 1,
        },
        "environment": {
            "protectedUrl": "https://private-live.example.invalid/sqx",
            "localPath": "C:/BOTS/private/live",
        },
        "privateReview": {
            "operatorNotes": "private approval notes must never leave ignored evidence",
        },
        "decision": {
            "selectedDecision": "approve_execution_record",
            "rationaleCategory": "tiny_cohort_clean",
            "executionOwner": "operator",
            "supportWindowHours": 24,
            "monitoringWindowHours": 24,
            "maxExecutionDelayHours": 24,
        },
        "candidateUsers": [
            {
                "email": "buyer4@example.invalid",
                "approvedForExecutionRecord": True,
            },
        ],
        "checks": {
            "remote8hPackageReviewed": True,
            "packageMatchesPrivateEvidence": True,
            "operatorDecisionRecorded": True,
            "decisionRationaleRecorded": True,
            "executionScopeUnchanged": True,
            "supportWindowStillReady": True,
            "rollbackStillReady": True,
            "pauseRuleStillReady": True,
            "noAutomationConfirmed": True,
            "executionRecordRequired": True,
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


def test_remote8i_clean_approval_is_redacted_and_requires_manual_execution_record(tmp_path):
    evidence_path = tmp_path / "remote8i_next_controlled_movement_execution_approval.local.json"
    evidence_path.write_text(json.dumps(_complete_payload()), encoding="utf-8")

    result = ingest_remote8i_next_controlled_movement_execution_approval(
        evidence_path=evidence_path,
        output_root=tmp_path / "out",
    )
    serialized = json.dumps(result, sort_keys=True)

    assert result["ok"] is True
    assert result["version"] == REMOTE_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVAL_VERSION
    assert result["status"] == "GO_REMOTE8I_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVED"
    assert result["approval"]["selectedDecision"] == "approve_execution_record"
    assert result["approval"]["approvedForManualExecutionRecord"] is True
    assert result["approval"]["allowedNextAction"] == "create_remote8j_manual_execution_record"
    assert result["approval"]["automationAllowed"] is False
    assert result["approval"]["executionPerformedNow"] is False
    assert result["approval"]["requiresSeparateExecutionRecord"] is True
    assert result["privacy"]["rawEmailsReturned"] is False
    assert result["privacy"]["decisionRationaleReturned"] is False
    assert result["decisionReadiness"]["candidateApprovals"][0]["emailRef"] == "bu***@example.invalid"
    assert result["nextPhase"] == "REMOTE-8J-manual-execution-record"

    assert "buyer4@example.invalid" not in serialized
    assert "private approval notes" not in serialized
    assert "https://" not in serialized
    assert "C:/BOTS" not in serialized
    assert (tmp_path / "out" / "remote8i_next_controlled_movement_execution_approval.public.json").is_file()


def test_remote8i_clean_rejection_is_valid_but_not_executable():
    payload = _complete_payload()
    payload["decision"]["selectedDecision"] = "reject_execution"
    payload["candidateUsers"] = []
    payload["decision"]["executionOwner"] = ""
    payload["decision"]["supportWindowHours"] = 0
    payload["decision"]["monitoringWindowHours"] = 0
    payload["decision"]["maxExecutionDelayHours"] = 0

    result = build_remote8i_execution_approval_summary(payload)

    assert result["ok"] is True
    assert result["status"] == "GO_REMOTE8I_NEXT_CONTROLLED_MOVEMENT_EXECUTION_REJECTED"
    assert result["approval"]["approvedForManualExecutionRecord"] is False
    assert result["approval"]["allowedNextAction"] == "replan_remote8h_or_remote8g"
    assert result["nextPhase"] == "REMOTE-8H-or-8G-replan"


def test_remote8i_missing_evidence_returns_no_go(tmp_path):
    result = ingest_remote8i_next_controlled_movement_execution_approval(
        evidence_path=tmp_path / "missing.local.json",
        output_root=tmp_path / "out",
    )

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8I_EXECUTION_APPROVAL_EVIDENCE_MISSING"
    assert result["error"] == "remote8i_execution_approval_evidence_missing"
    assert result["approval"]["approvedForManualExecutionRecord"] is False
    assert result["approval"]["executionPerformedNow"] is False
    assert (tmp_path / "out" / "remote8i_next_controlled_movement_execution_approval.public.json").is_file()


def test_remote8i_blockers_prevent_execution_approval():
    payload = _complete_payload()
    payload["sourceGate"]["remote8hStatus"] = "NO_GO_REMOTE8H_NEXT_CONTROLLED_MOVEMENT_PACKAGE_BLOCKED"
    payload["sourceGate"]["plannedNewUsers"] = 3
    payload["sourceGate"]["candidateCount"] = 1
    payload["decision"]["selectedDecision"] = "approve_execution_record"
    payload["decision"]["executionOwner"] = ""
    payload["decision"]["supportWindowHours"] = 4
    payload["decision"]["monitoringWindowHours"] = 4
    payload["candidateUsers"][0]["approvedForExecutionRecord"] = False
    payload["checks"]["pauseRuleStillReady"] = False
    payload["executionMetrics"]["emailsSent"] = 1

    result = build_remote8i_execution_approval_summary(payload)

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8I_EXECUTION_APPROVAL_BLOCKED"
    assert "remote8h_package_go_status_missing" in result["blockers"]
    assert "planned_new_users_exceeds_limit" in result["blockers"]
    assert "candidate_count_must_match_planned_new_users" in result["blockers"]
    assert "execution_owner_missing" in result["blockers"]
    assert "support_window_too_short" in result["blockers"]
    assert "monitoring_window_too_short" in result["blockers"]
    assert "candidate_1_approval_missing" in result["blockers"]
    assert "required_checks_missing" in result["blockers"]
    assert "execution_metrics_must_remain_zero" in result["blockers"]
    assert result["missingChecks"] == ["pauseRuleStillReady"]
    assert result["executionBlockers"] == ["emailsSent"]
    assert result["approval"]["approvedForManualExecutionRecord"] is False
