import json

from core.remote_tiny_cohort_execution import (
    REMOTE_TINY_COHORT_EXECUTION_VERSION,
    build_remote8e_execution_summary,
    ingest_remote8e_tiny_cohort_execution,
)


def _complete_payload() -> dict:
    return {
        "schemaVersion": REMOTE_TINY_COHORT_EXECUTION_VERSION,
        "executionId": "remote8e-tiny-cohort-execution-001",
        "capturedAt": "2026-05-16T16:00:00+00:00",
        "operatorApproval": True,
        "requestedAction": "record_manual_activation_execution",
        "sourceGate": {
            "remote8dStatus": "GO_REMOTE8D_TINY_COHORT_ACTIVATION_PACKAGE_READY",
            "remote8dPackageId": "remote8d-tiny-cohort-001",
        },
        "environment": {
            "protectedUrl": "https://private-live.example.invalid/sqx",
            "localPath": "C:/BOTS/private/live",
        },
        "activatedUsers": [
            {
                "email": "buyer1@example.invalid",
                "kind": "paid_subscription",
                "featureScope": "full",
                "manualInviteSent": True,
                "manualGrantRecorded": True,
                "privateMessageSent": True,
                "protectedUrlSharedPrivately": True,
                "supportWindowAcknowledged": True,
            },
            {
                "email": "tester2@example.invalid",
                "kind": "tester_free",
                "featureScope": "full",
                "manualInviteSent": True,
                "manualGrantRecorded": True,
                "privateMessageSent": True,
                "protectedUrlSharedPrivately": True,
                "supportWindowAcknowledged": True,
            },
            {
                "email": "buyer3@example.invalid",
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
            "remote8dPackageGoConfirmed": True,
            "operatorFinalApprovalRecorded": True,
            "manualExecutionOnly": True,
            "noAutomationUsed": True,
            "privateMessagesSent": True,
            "entitlementsRecordedPrivately": True,
            "protectedUrlSharedPrivately": True,
            "supportWindowActive": True,
            "rollbackPlanStillReady": True,
            "pauseRuleStillActive": True,
            "monitoringStarted": True,
            "privateEvidenceStoredOutsideGit": True,
        },
        "manualCounts": {
            "invitesSentManually": 3,
            "grantsRecordedManually": 3,
            "privateMessagesSent": 3,
            "protectedUrlsSharedPrivately": 3,
        },
        "automationMetrics": {
            "automationJobsStarted": 0,
            "checkoutLinksCreated": 0,
            "publicUrlsShared": 0,
            "automatedEmailsSent": 0,
            "automatedGrantsCreated": 0,
        },
    }


def test_remote8e_clean_manual_execution_record_is_redacted_and_monitoring_ready(tmp_path):
    evidence_path = tmp_path / "remote8e_tiny_cohort_execution.local.json"
    evidence_path.write_text(json.dumps(_complete_payload()), encoding="utf-8")

    result = ingest_remote8e_tiny_cohort_execution(evidence_path=evidence_path, output_root=tmp_path / "out")
    serialized = json.dumps(result, sort_keys=True)

    assert result["ok"] is True
    assert result["version"] == REMOTE_TINY_COHORT_EXECUTION_VERSION
    assert result["status"] == "GO_REMOTE8E_TINY_COHORT_MANUAL_EXECUTION_RECORDED"
    assert result["execution"]["activatedUserCount"] == 3
    assert result["record"]["ready"] is True
    assert result["record"]["allowedNextAction"] == "start_tiny_cohort_monitoring"
    assert result["record"]["automationAllowed"] is False
    assert result["postExecutionGate"]["furtherExpansionAllowedNow"] is False
    assert result["postExecutionGate"]["monitoringRequired"] is True
    assert result["privacy"]["rawEmailsReturned"] is False
    assert result["privacy"]["protectedUrlReturned"] is False
    assert result["execution"]["users"][0]["emailRef"] == "bu***@example.invalid"
    assert result["nextPhase"] == "REMOTE-8F-tiny-cohort-monitoring"

    assert "buyer1@example.invalid" not in serialized
    assert "tester2@example.invalid" not in serialized
    assert "https://" not in serialized
    assert "C:/BOTS" not in serialized
    assert (tmp_path / "out" / "remote8e_tiny_cohort_execution.public.json").is_file()


def test_remote8e_missing_evidence_returns_no_go(tmp_path):
    result = ingest_remote8e_tiny_cohort_execution(
        evidence_path=tmp_path / "missing.local.json",
        output_root=tmp_path / "out",
    )

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8E_EXECUTION_EVIDENCE_MISSING"
    assert result["error"] == "remote8e_execution_evidence_missing"
    assert result["record"]["ready"] is False
    assert result["record"]["automationAllowed"] is False
    assert (tmp_path / "out" / "remote8e_tiny_cohort_execution.public.json").is_file()


def test_remote8e_blockers_prevent_execution_record():
    payload = _complete_payload()
    payload["sourceGate"]["remote8dStatus"] = "NO_GO_REMOTE8D_TINY_COHORT_ACTIVATION_BLOCKED"
    payload["activatedUsers"] = payload["activatedUsers"][:2]
    payload["checks"]["monitoringStarted"] = False
    payload["manualCounts"] = {
        "invitesSentManually": 3,
        "grantsRecordedManually": 2,
        "privateMessagesSent": 2,
        "protectedUrlsSharedPrivately": 2,
    }
    payload["automationMetrics"]["automatedEmailsSent"] = 1

    result = build_remote8e_execution_summary(payload)

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8E_TINY_COHORT_EXECUTION_BLOCKED"
    assert "remote8d_package_go_status_missing" in result["blockers"]
    assert "activated_user_count_out_of_range" in result["blockers"]
    assert "required_checks_missing" in result["blockers"]
    assert "automation_metrics_must_remain_zero" in result["blockers"]
    assert "manual_execution_counts_mismatch" in result["blockers"]
    assert result["missingChecks"] == ["monitoringStarted"]
    assert result["countBlockers"]["automationMetricsNonzero"] == ["automatedEmailsSent"]
    assert result["countBlockers"]["manualCountsMismatch"] == ["invitesSentManually"]
    assert result["record"]["ready"] is False
