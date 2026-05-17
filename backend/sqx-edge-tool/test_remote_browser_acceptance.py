import json

from core.remote_browser_acceptance import (
    REMOTE_BROWSER_ACCEPTANCE_VERSION,
    build_remote_accept1_browser_acceptance_summary,
    ingest_remote_accept1_browser_acceptance,
)


def _complete_payload() -> dict:
    return {
        "schemaVersion": REMOTE_BROWSER_ACCEPTANCE_VERSION,
        "phase": "REMOTE-ACCEPT1",
        "capturedAt": "2026-05-17T12:00:00+02:00",
        "operatorApproval": True,
        "testerKind": "tester_free",
        "browser": {
            "name": "Chrome",
            "mode": "incognito_or_fresh_session",
            "closedAndReopened": True,
        },
        "checks": {
            "cloudflareAccessPassed": True,
            "welcomeTitleMatches": True,
            "commercialNameIsSqxEdgeSuite": True,
            "identityCopyIsUserFriendly": True,
            "noInternalAppSessionCopy": True,
            "dashboardButtonClickedOnce": True,
            "welcomeDidNotBounceBack": True,
            "dashboardUsableAfterEntry": True,
            "workspaceVisibleWithoutLocalPaths": True,
            "noRawEmailTokenCookieUrlOrCloudflareIdCaptured": True,
            "browserCloseDoesNotKeepAppSessionExpectation": True,
            "privateEvidenceStoredOutsideGit": True,
        },
        "metrics": {
            "dashboardButtonClicksRequired": 1,
            "welcomeBounceBacks": 0,
            "visibleErrorMessages": 0,
            "sessionPersistenceAfterBrowserClose": 0,
            "privateDataLeaksObserved": 0,
        },
        "notes": ["Private notes stay outside git."],
    }


def test_remote_accept1_go_redacts_private_values(tmp_path):
    evidence_path = tmp_path / "remote_accept1_browser_acceptance.local.json"
    evidence_path.write_text(json.dumps(_complete_payload()), encoding="utf-8")

    result = ingest_remote_accept1_browser_acceptance(evidence_path=evidence_path, output_root=tmp_path / "out")
    serialized = json.dumps(result, sort_keys=True)

    assert result["ok"] is True
    assert result["version"] == REMOTE_BROWSER_ACCEPTANCE_VERSION
    assert result["status"] == "GO_REMOTE_ACCEPT1_BROWSER_ACCEPTANCE_CLEAN"
    assert result["metrics"]["dashboardButtonClicksRequired"] == 1
    assert result["metrics"]["welcomeBounceBacks"] == 0
    assert result["privacy"]["rawEmailReturned"] is False
    assert result["expansionGate"]["allowedToExpandBeyondOneUser"] is False
    assert "@" not in serialized
    assert "https://" not in serialized
    assert "C:/BOTS" not in serialized
    assert "__Host-sqx_remote_session" not in serialized
    assert (tmp_path / "out" / "remote_accept1_browser_acceptance.public.json").is_file()


def test_remote_accept1_missing_evidence_returns_no_go(tmp_path):
    result = ingest_remote_accept1_browser_acceptance(
        evidence_path=tmp_path / "missing.local.json",
        output_root=tmp_path / "out",
    )

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE_ACCEPT1_PRIVATE_EVIDENCE_MISSING"
    assert result["error"] == "remote_accept1_private_evidence_missing"
    assert result["expansionGate"]["allowedToExpandBeyondOneUser"] is False
    assert (tmp_path / "out" / "remote_accept1_browser_acceptance.public.json").is_file()


def test_remote_accept1_blocks_on_bounce_or_extra_clicks():
    payload = _complete_payload()
    payload["operatorApproval"] = False
    payload["checks"]["welcomeDidNotBounceBack"] = False
    payload["metrics"]["dashboardButtonClicksRequired"] = 2
    payload["metrics"]["visibleErrorMessages"] = 1

    result = build_remote_accept1_browser_acceptance_summary(payload)

    assert result["ok"] is False
    assert result["status"] == "NO_GO_REMOTE_ACCEPT1_BROWSER_ACCEPTANCE_BLOCKED"
    assert "operator_approval_missing" in result["blockers"]
    assert "required_checks_missing" in result["blockers"]
    assert "acceptance_metrics_not_clean" in result["blockers"]
    assert result["missingChecks"] == ["welcomeDidNotBounceBack"]
    assert "dashboard_button_click_count_not_one" in result["metricBlockers"]
    assert "visibleErrorMessages" in result["metricBlockers"]
