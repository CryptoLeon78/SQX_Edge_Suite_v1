import json

from core.remote_tiny_cohort_activation import (
    REMOTE_TINY_COHORT_ACTIVATION_VERSION,
    build_remote8d_activation_summary,
    ingest_remote8d_tiny_cohort_activation,
)


def _complete_payload() -> dict:
    return {
        "schemaVersion": REMOTE_TINY_COHORT_ACTIVATION_VERSION,
        "packageId": "remote8d-tiny-cohort-001",
        "capturedAt": "2026-05-16T15:00:00+00:00",
        "operatorApproval": True,
        "requestedAction": "prepare_manual_activation_package",
        "targetCohortSize": 3,
        "sourceGate": {
            "remote8cStatus": "GO_REMOTE8C_TINY_COHORT_EXPANSION_READY",
            "remote8cObservationId": "remote8c-first-user-001",
        },
        "environment": {
            "protectedUrl": "https://private-live.example.invalid/sqx",
            "localPath": "C:/BOTS/private/live",
        },
        "candidates": [
            {"email": "buyer1@example.invalid", "kind": "paid_subscription", "featureScope": "full"},
            {"email": "tester2@example.invalid", "kind": "tester_free", "featureScope": "full"},
            {"email": "buyer3@example.invalid", "kind": "paid_subscription", "featureScope": "full"},
        ],
        "checks": {
            "remote8cGoConfirmed": True,
            "candidateListReviewed": True,
            "cohortSizeWithinLimit": True,
            "entitlementBoundariesDefined": True,
            "supportOwnerAssigned": True,
            "supportWindowReady": True,
            "rollbackPlanReady": True,
            "pauseRuleReady": True,
            "communicationCopyReviewed": True,
            "protectedUrlPrivateOnly": True,
            "workspaceIsolationReminder": True,
            "securityMonitoringReady": True,
            "noAutomationConfirmed": True,
            "privateEvidenceStoredOutsideGit": True,
        },
        "automationMetrics": {
            "invitesSent": 0,
            "grantsCreated": 0,
            "checkoutLinksCreated": 0,
            "emailsSent": 0,
            "publicUrlsShared": 0,
            "automationJobsStarted": 0,
        },
    }


def test_remote8d_clean_package_prepares_manual_only_tiny_cohort(tmp_path):
    evidence_path = tmp_path / "remote8d_tiny_cohort_activation.local.json"
    evidence_path.write_text(json.dumps(_complete_payload()), encoding="utf-8")

    result = ingest_remote8d_tiny_cohort_activation(evidence_path=evidence_path, output_root=tmp_path / "out")
    serialized = json.dumps(result, sort_keys=True)

    assert result["ok"] is True
    assert result["version"] == REMOTE_TINY_COHORT_ACTIVATION_VERSION
    assert result["status"] == "GO_REMOTE8D_TINY_COHORT_ACTIVATION_PACKAGE_READY"
    assert result["package"]["candidateCount"] == 3
    assert result["manualPackage"]["ready"] is True
    assert result["manualPackage"]["mustNotExecuteAutomatically"] is True
    assert result["executionGate"]["invitesAllowedNow"] is False
    assert result["executionGate"]["grantMutationAllowedNow"] is False
    assert result["executionGate"]["emailSendingAllowedNow"] is False
    assert result["privacy"]["rawEmailsReturned"] is False
    assert result["privacy"]["communicationCopyReturned"] is False
    assert result["package"]["candidates"][0]["emailRef"] == "bu***@example.invalid"

    assert "buyer1@example.invalid" not in serialized
    assert "tester2@example.invalid" not in serialized
    assert "https://" not in serialized
    assert "C:/BOTS" not in serialized
    assert (tmp_path / "out" / "remote8d_tiny_cohort_activation.public.json").is_file()


def test_remote8d_missing_evidence_returns_no_go(tmp_path):
    result = ingest_remote8d_tiny_cohort_activation(
        evidence_path=tmp_path / "missing.local.json",
        output_root=tmp_path / "out",
    )

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8D_ACTIVATION_PACKAGE_EVIDENCE_MISSING"
    assert result["error"] == "remote8d_activation_package_evidence_missing"
    assert result["executionGate"]["invitesAllowedNow"] is False
    assert (tmp_path / "out" / "remote8d_tiny_cohort_activation.public.json").is_file()


def test_remote8d_blockers_prevent_package_ready():
    payload = _complete_payload()
    payload["sourceGate"]["remote8cStatus"] = "NO_GO_REMOTE8C_FIRST_USER_OBSERVATION_BLOCKED"
    payload["targetCohortSize"] = 2
    payload["candidates"] = payload["candidates"][:2]
    payload["checks"]["pauseRuleReady"] = False
    payload["automationMetrics"]["emailsSent"] = 1

    result = build_remote8d_activation_summary(payload)

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE8D_TINY_COHORT_ACTIVATION_BLOCKED"
    assert "remote8c_go_status_missing" in result["blockers"]
    assert "target_cohort_size_out_of_range" in result["blockers"]
    assert "candidate_count_out_of_range" in result["blockers"]
    assert "required_checks_missing" in result["blockers"]
    assert "automation_must_remain_zero" in result["blockers"]
    assert result["missingChecks"] == ["pauseRuleReady"]
    assert result["automationBlockers"] == ["emailsSent"]
    assert result["manualPackage"]["ready"] is False
