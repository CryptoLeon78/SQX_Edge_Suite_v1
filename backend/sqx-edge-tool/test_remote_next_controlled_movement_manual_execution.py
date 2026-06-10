import json

from core.remote_next_controlled_movement_manual_execution import (
    REMOTE_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION_VERSION,
    build_remote8j_manual_execution_summary,
    ingest_remote8j_next_controlled_movement_manual_execution,
)


def _complete_payload() -> dict:
    return {
        "schemaVersion": REMOTE_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION_VERSION,
        "executionId": "remote8j-manual-execution-001",
        "capturedAt": "2026-05-17T00:00:00+00:00",
        "operatorApproval": True,
        "requestedAction": "record_next_controlled_movement_manual_execution",
        "sourceGate": {
            "remote8iStatus": "GO_REMOTE8I_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVED",
            "remote8iApprovalId": "remote8i-approval-001",
            "remote8iSelectedDecision": "approve_execution_record",
            "remote8hPackageId": "remote8h-next-movement-001",
            "movementType": "add_1_2_users",
            "plannedNewUsers": 1,
            "candidateCount": 1,
        },
        "environment": {
            "protectedUrl": "https://private-live.example.invalid/sqx",
            "localPath": "C:/BOTS/private/live",
        },
        "privateExecution": {
            "messageBody": "Private handoff copy stays local and ignored.",
        },
        "executedUsers": [
            {
                "email": "buyer4@example.invalid",
                "kind": "paid_subscription",
                "featureScope": "full",
                "manualInviteSent": True,
                "manualGrantRecorded": True,
                "privateMessageSent": True,
                "protectedUrlSharedPrivately": True,
                "supportWindowAcknowledged": True,
            },
        ],
        "checks": {
            "remote8iApprovalConfirmed": True,
            "remote8hPackageStillMatches": True,
            "operatorFinalApprovalRecorded": True,
            "manualExecutionOnly": True,
            "noAutomationUsed": True,
            "manualActionRecorded": True,
            "entitlementsRecordedPrivately": True,
            "protectedUrlSharedPrivately": True,
            "supportWindowActive": True,
            "rollbackPlanStillReady": True,
            "pauseRuleStillActive": True,
            "monitoringStarted": True,
            "privateEvidenceStoredOutsideGit": True,
        },
        "manualCounts": {
            "invitesSentManually": 1,
            "grantsRecordedManually": 1,
            "privateMessagesSent": 1,
            "protectedUrlsSharedPrivately": 1,
        },
        "automationMetrics": {
            "automationJobsStarted": 0,
            "checkoutLinksCreated": 0,
            "publicUrlsShared": 0,
            "automatedEmailsSent": 0,
            "automatedGrantsCreated": 0,
            "trafficExpanded": 0,
            "paidCampaignStarted": 0,
        },
    }


def test_remote8j_clean_manual_execution_record_is_redacted_and_monitoring_ready(tmp_path):
    evidence_path = tmp_path / "remote8j_next_controlled_movement_manual_execution.local.json"
    evidence_path.write_text(json.dumps(_complete_payload()), encoding="utf-8")

    result = ingest_remote8j_next_controlled_movement_manual_execution(
        evidence_path=evidence_path,
        output_root=tmp_path / "out",
    )
    serialized = json.dumps(result, sort_keys=True)

    assert result["ok"] is True
    assert result["version"] == REMOTE_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION_VERSION
    assert result["status"] == "GO_REMOTE8J_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION_RECORDED"
    assert result["execution"]["movementType"] == "add_1_2_users"
    assert result["execution"]["executedUserCount"] == 1
    assert result["record"]["ready"] is True
    assert result["record"]["allowedNextAction"] == "start_remote8k_post_execution_monitoring"
    assert result["record"]["automationAllowed"] is False
    assert result["postExecutionGate"]["furtherExpansionAllowedNow"] is False
    assert result["postExecutionGate"]["monitoringRequired"] is True
    assert result["privacy"]["rawEmailsReturned"] is False
    assert result["privacy"]["messageBodyReturned"] is False
    assert result["execution"]["users"][0]["emailRef"] == "bu***@example.invalid"
    assert result["nextPhase"] == "REMOTE-8K-post-execution-monitoring"

    assert "buyer4@example.invalid" not in serialized
    assert "Private handoff copy" not in serialized
    assert "https://" not in serialized
    assert "C:/BOTS" not in serialized
    assert (tmp_path / "out" / "remote8j_next_controlled_movement_manual_execution.public.json").is_file()


def test_remote8j_missing_evidence_returns_no_go(tmp_path):
    result = ingest_remote8j_next_controlled_movement_manual_execution(
        evidence_path=tmp_path / "missing.local.json",
        output_root=tmp_path / "out",
    )

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8J_MANUAL_EXECUTION_EVIDENCE_MISSING"
    assert result["error"] == "remote8j_manual_execution_evidence_missing"
    assert result["record"]["ready"] is False
    assert result["record"]["automationAllowed"] is False
    assert (tmp_path / "out" / "remote8j_next_controlled_movement_manual_execution.public.json").is_file()


def test_remote8j_blockers_prevent_manual_execution_record():
    payload = _complete_payload()
    payload["sourceGate"]["remote8iStatus"] = "NO_GO_REMOTE8I_EXECUTION_APPROVAL_BLOCKED"
    payload["sourceGate"]["remote8iSelectedDecision"] = "defer_execution"
    payload["sourceGate"]["plannedNewUsers"] = 3
    payload["sourceGate"]["candidateCount"] = 1
    payload["executedUsers"][0]["privateMessageSent"] = False
    payload["checks"]["monitoringStarted"] = False
    payload["manualCounts"]["invitesSentManually"] = 0
    payload["automationMetrics"]["automatedEmailsSent"] = 1

    result = build_remote8j_manual_execution_summary(payload)

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8J_MANUAL_EXECUTION_BLOCKED"
    assert "remote8i_approval_go_status_missing" in result["blockers"]
    assert "remote8i_selected_decision_not_execution_approval" in result["blockers"]
    assert "planned_new_users_exceeds_limit" in result["blockers"]
    assert "candidate_count_must_match_planned_new_users" in result["blockers"]
    assert "executed_user_count_must_match_planned_new_users" in result["blockers"]
    assert "required_checks_missing" in result["blockers"]
    assert "automation_metrics_must_remain_zero" in result["blockers"]
    assert "manual_execution_counts_mismatch" in result["blockers"]
    assert "user_1_privateMessageSent_missing" in result["blockers"]
    assert result["missingChecks"] == ["monitoringStarted"]
    assert result["countBlockers"]["automationMetricsNonzero"] == ["automatedEmailsSent"]
    assert result["countBlockers"]["manualCountsMismatch"] == ["invitesSentManually"]
    assert result["record"]["ready"] is False
