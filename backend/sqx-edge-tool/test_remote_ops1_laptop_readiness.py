import json

from core.remote_ops1_laptop_readiness import (
    REMOTE_OPS1_LAPTOP_READINESS_VERSION,
    build_remote_ops1_laptop_readiness_summary,
    ingest_remote_ops1_laptop_readiness,
)


def _complete_payload() -> dict:
    return {
        "schemaVersion": REMOTE_OPS1_LAPTOP_READINESS_VERSION,
        "drillId": "remote-ops1-laptop-readiness-001",
        "capturedAt": "2026-05-16T20:45:00+02:00",
        "operatorApproval": True,
        "requestedAction": "validate_laptop_production_readiness",
        "environment": {
            "hostClass": "windows_laptop",
            "backendPort": 5050,
            "backendBind": True,
            "cloudflareMode": True,
            "workspaceMode": True,
            "sqxMode": True,
        },
        "privateRefs": {
            "protectedUrl": "https://private.example.invalid",
            "cloudflareAccountId": "private-account-id",
            "cloudflareTunnelId": "private-tunnel-id",
            "cloudflareAccessAppId": "private-access-app-id",
            "localWorkspaceRoot": "C:/BOTS/private/workspaces",
            "sqxPath": "C:/BOTS/Versiones/LOCAL_SQX142_ROOT",
            "sqxDataDb": "C:/BOTS/Versiones/LOCAL_SQX142_ROOT/user/settings/data.db",
            "operatorEmail": "operator@example.invalid",
        },
        "checks": {
            "powerPlanReviewed": True,
            "sleepDisabled": True,
            "rebootRecoveryPlanReady": True,
            "remoteServicePreflightStrictGo": True,
            "watchdogSmokeGo": True,
            "backendLocalHealthGo": True,
            "backendBoundToLocalhostOnly": True,
            "sqxPathsReady": True,
            "sqxDataDbReady": True,
            "templatesReady": True,
            "outputWritable": True,
            "workspaceRootReady": True,
            "cloudflaredInstalled": True,
            "tunnelPreflightGo": True,
            "tunnelStartupPlanReady": True,
            "accessAnonymousBlocked": True,
            "appSessionSmokeReady": True,
            "workspaceSmokeReady": True,
            "artifactGenerationSmokeReady": True,
            "revocationSmokeReady": True,
            "restorePlanReady": True,
            "logsWrittenToIgnoredLocalPath": True,
            "privateEvidenceStoredOutsideGit": True,
            "noSecretsInGitConfirmed": True,
            "noRouterPortsOpened": True,
            "noUsersInvited": True,
        },
        "riskMetrics": {
            "newUsersInvited": 0,
            "paidUsersActivated": 0,
            "testerGrantsChanged": 0,
            "checkoutLinksCreated": 0,
            "emailsSent": 0,
            "publicUrlsShared": 0,
            "routerPortsOpened": 0,
            "automationJobsStarted": 0,
            "unresolvedSupportIssues": 0,
            "workspaceLeakIncidents": 0,
            "securityIncidents": 0,
            "tunnelDropsDuringSmoke": 0,
            "backendHealthFailures": 0,
            "artifactGenerationFailures": 0,
            "revocationFailures": 0,
        },
    }


def test_remote_ops1_clean_readiness_is_redacted_and_non_executing(tmp_path):
    evidence_path = tmp_path / "remote_ops1_laptop_readiness.local.json"
    evidence_path.write_text(json.dumps(_complete_payload()), encoding="utf-8")

    result = ingest_remote_ops1_laptop_readiness(evidence_path=evidence_path, output_root=tmp_path / "out")
    serialized = json.dumps(result, sort_keys=True)

    assert result["ok"] is True
    assert result["status"] == "GO_REMOTE_OPS1_LAPTOP_READY"
    assert result["readiness"]["laptopReady"] is True
    assert result["readiness"]["backendReady"] is True
    assert result["readiness"]["sqxReady"] is True
    assert result["readiness"]["tunnelReady"] is True
    assert result["readiness"]["pilotSmokeReady"] is True
    assert result["readiness"]["executionAllowedNow"] is False
    assert result["readiness"]["userExpansionAllowedNow"] is False
    assert result["nextPhase"] == "REMOTE-8H-private-package-evidence"

    assert "https://" not in serialized
    assert "C:/BOTS" not in serialized
    assert "operator@example.invalid" not in serialized
    assert "private-tunnel-id" not in serialized
    assert (tmp_path / "out" / "remote_ops1_laptop_readiness.public.json").is_file()


def test_remote_ops1_missing_evidence_returns_no_go(tmp_path):
    result = ingest_remote_ops1_laptop_readiness(evidence_path=tmp_path / "missing.local.json", output_root=tmp_path / "out")

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE_OPS1_LAPTOP_READINESS_EVIDENCE_MISSING"
    assert result["readiness"]["laptopReady"] is False
    assert result["readiness"]["executionAllowedNow"] is False
    assert (tmp_path / "out" / "remote_ops1_laptop_readiness.public.json").is_file()


def test_remote_ops1_blockers_prevent_laptop_ready():
    payload = _complete_payload()
    payload["checks"]["sleepDisabled"] = False
    payload["checks"]["tunnelPreflightGo"] = False
    payload["riskMetrics"]["tunnelDropsDuringSmoke"] = 1

    result = build_remote_ops1_laptop_readiness_summary(payload)

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE_OPS1_LAPTOP_READINESS_BLOCKED"
    assert "required_checks_missing" in result["blockers"]
    assert "risk_metrics_must_remain_zero" in result["blockers"]
    assert result["missingChecks"] == ["sleepDisabled", "tunnelPreflightGo"]
    assert result["riskBlockers"] == ["tunnelDropsDuringSmoke"]
    assert result["readiness"]["laptopReady"] is False
