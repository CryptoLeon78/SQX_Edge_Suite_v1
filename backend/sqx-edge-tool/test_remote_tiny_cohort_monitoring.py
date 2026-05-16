import json

from core.remote_tiny_cohort_monitoring import (
    REMOTE_TINY_COHORT_MONITORING_VERSION,
    build_remote8f_monitoring_summary,
    ingest_remote8f_tiny_cohort_monitoring,
)


def _complete_payload() -> dict:
    return {
        "schemaVersion": REMOTE_TINY_COHORT_MONITORING_VERSION,
        "monitoringId": "remote8f-tiny-cohort-monitoring-001",
        "capturedAt": "2026-05-16T18:00:00+00:00",
        "operatorReview": True,
        "requestedDecision": "prepare_next_controlled_movement",
        "observationHours": 24,
        "sourceGate": {
            "remote8eStatus": "GO_REMOTE8E_TINY_COHORT_MANUAL_EXECUTION_RECORDED",
            "remote8eExecutionId": "remote8e-tiny-cohort-execution-001",
        },
        "environment": {
            "protectedUrl": "https://private-live.example.invalid/sqx",
            "localPath": "C:/BOTS/private/live",
        },
        "monitoredUsers": [
            {
                "email": "buyer1@example.invalid",
                "kind": "paid_subscription",
                "featureScope": "full",
                "accessVerified": True,
                "entitlementChecked": True,
                "workspaceIsolationChecked": True,
                "supportWindowAcknowledged": True,
                "noCriticalIssue": True,
            },
            {
                "email": "tester2@example.invalid",
                "kind": "tester_free",
                "featureScope": "full",
                "accessVerified": True,
                "entitlementChecked": True,
                "workspaceIsolationChecked": True,
                "supportWindowAcknowledged": True,
                "noCriticalIssue": True,
            },
            {
                "email": "buyer3@example.invalid",
                "kind": "paid_subscription",
                "featureScope": "full",
                "accessVerified": True,
                "entitlementChecked": True,
                "workspaceIsolationChecked": True,
                "supportWindowAcknowledged": True,
                "noCriticalIssue": True,
            },
        ],
        "signals": {
            "remote8eExecutionGoConfirmed": True,
            "cohortAccessStable": True,
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
            "entitlementErrors": 0,
            "refundRequests": 0,
            "crossUserDataFindings": 0,
            "publicUrlLeaks": 0,
            "automationJobsStarted": 0,
        },
    }


def test_remote8f_clean_monitoring_is_redacted_and_allows_decision_review(tmp_path):
    evidence_path = tmp_path / "remote8f_tiny_cohort_monitoring.local.json"
    evidence_path.write_text(json.dumps(_complete_payload()), encoding="utf-8")

    result = ingest_remote8f_tiny_cohort_monitoring(evidence_path=evidence_path, output_root=tmp_path / "out")
    serialized = json.dumps(result, sort_keys=True)

    assert result["ok"] is True
    assert result["version"] == REMOTE_TINY_COHORT_MONITORING_VERSION
    assert result["status"] == "GO_REMOTE8F_TINY_COHORT_MONITORING_CLEAN"
    assert result["monitoring"]["cohortUserCount"] == 3
    assert result["monitoring"]["observationHours"] == 24
    assert result["decision"]["ready"] is True
    assert result["decision"]["allowedNextAction"] == "prepare_remote8g_tiny_cohort_decision_review"
    assert result["decision"]["automationAllowed"] is False
    assert result["decision"]["furtherExpansionAllowedNow"] is False
    assert result["safety"]["rollbackReady"] is True
    assert result["safety"]["pauseRuleReady"] is True
    assert result["privacy"]["rawEmailsReturned"] is False
    assert result["privacy"]["protectedUrlReturned"] is False
    assert result["monitoring"]["users"][0]["emailRef"] == "bu***@example.invalid"
    assert result["nextPhase"] == "REMOTE-8G-tiny-cohort-decision-review"

    assert "buyer1@example.invalid" not in serialized
    assert "tester2@example.invalid" not in serialized
    assert "https://" not in serialized
    assert "C:/BOTS" not in serialized
    assert (tmp_path / "out" / "remote8f_tiny_cohort_monitoring.public.json").is_file()


def test_remote8f_missing_evidence_returns_no_go(tmp_path):
    result = ingest_remote8f_tiny_cohort_monitoring(
        evidence_path=tmp_path / "missing.local.json",
        output_root=tmp_path / "out",
    )

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8F_MONITORING_EVIDENCE_MISSING"
    assert result["error"] == "remote8f_monitoring_evidence_missing"
    assert result["decision"]["ready"] is False
    assert result["decision"]["automationAllowed"] is False
    assert (tmp_path / "out" / "remote8f_tiny_cohort_monitoring.public.json").is_file()


def test_remote8f_blockers_prevent_next_movement():
    payload = _complete_payload()
    payload["sourceGate"]["remote8eStatus"] = "NO_GO_REMOTE8E_TINY_COHORT_EXECUTION_BLOCKED"
    payload["observationHours"] = 8
    payload["monitoredUsers"] = payload["monitoredUsers"][:2]
    payload["monitoredUsers"][0]["workspaceIsolationChecked"] = False
    payload["signals"]["noSecurityIncidents"] = False
    payload["zeroToleranceMetrics"]["securityIncidents"] = 1

    result = build_remote8f_monitoring_summary(payload)

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8F_TINY_COHORT_MONITORING_BLOCKED"
    assert "remote8e_execution_go_status_missing" in result["blockers"]
    assert "minimum_observation_hours_not_met" in result["blockers"]
    assert "monitored_user_count_out_of_range" in result["blockers"]
    assert "required_signals_missing" in result["blockers"]
    assert "zero_tolerance_metrics_nonzero" in result["blockers"]
    assert "user_1_workspaceIsolationChecked_missing" in result["blockers"]
    assert result["missingSignals"] == ["noSecurityIncidents"]
    assert result["metricBlockers"] == ["securityIncidents"]
    assert result["decision"]["ready"] is False
    assert result["decision"]["furtherExpansionAllowedNow"] is False
