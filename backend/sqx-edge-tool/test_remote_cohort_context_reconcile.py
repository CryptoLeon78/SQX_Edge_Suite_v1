import json

from core.remote_cohort_context_reconcile import (
    REMOTE_COHORT_CONTEXT_RECONCILE_VERSION,
    build_remote_cohort_context_reconcile,
    write_remote_cohort_context_reconcile,
)


def test_context_reconcile_flags_active_alias_that_needs_recapture(tmp_path):
    payload = {
        "schemaVersion": "remote-cohort-matrix-v1",
        "phase": "REMOTE-COHORT-FIX1",
        "rows": [
            {
                "alias": "TESTER-READY",
                "identityHashRef": "aaa111aaa111",
                "monitoringScope": "active",
                "status": "ready",
                "accessOk": True,
                "grantOk": True,
                "antiSharingOk": True,
                "downloadsOk": True,
                "trustedContexts": 1,
                "pendingContexts": 0,
                "blockedContexts": 0,
                "revokedContexts": 0,
                "contextRefs": ["ctxaaa111111"],
                "openIncidents": 0,
            },
            {
                "alias": "TESTER-RILIS",
                "identityHashRef": "bbb222bbb222",
                "monitoringScope": "active",
                "status": "needs_attention",
                "accessOk": True,
                "grantOk": True,
                "antiSharingOk": False,
                "downloadsOk": True,
                "trustedContexts": 0,
                "pendingContexts": 0,
                "blockedContexts": 0,
                "revokedContexts": 0,
                "contextRefs": [],
                "openIncidents": 0,
            },
            {
                "alias": "TESTER-STANDBY",
                "identityHashRef": "ccc333ccc333",
                "monitoringScope": "standby",
                "status": "standby",
                "accessOk": False,
                "grantOk": True,
                "antiSharingOk": False,
                "downloadsOk": False,
                "trustedContexts": 0,
                "pendingContexts": 0,
                "blockedContexts": 0,
                "revokedContexts": 0,
                "contextRefs": [],
                "openIncidents": 0,
            },
        ],
    }

    result = build_remote_cohort_context_reconcile(matrix_payload=payload)
    actions = {item["alias"]: item for item in result["actions"]}

    assert result["schemaVersion"] == REMOTE_COHORT_CONTEXT_RECONCILE_VERSION
    assert result["summary"]["activeAliasCount"] == 2
    assert result["summary"]["readyAliasCount"] == 1
    assert result["summary"]["needsActionCount"] == 1
    assert result["summary"]["recaptureRequiredCount"] == 1
    assert result["summary"]["canTreatActiveCohortAsClean"] is False
    assert actions["TESTER-RILIS"]["action"] == "recapture_context"
    assert actions["TESTER-RILIS"]["reason"] == "human_smoke_ok_but_anti_sharing_context_missing"
    assert "TESTER-STANDBY" not in actions


def test_context_reconcile_detects_pending_context_operator_review_and_redacts(tmp_path):
    payload = {
        "schemaVersion": "remote-cohort-matrix-v1",
        "phase": "REMOTE-COHORT-FIX1",
        "rows": [
            {
                "alias": "TESTER-PENDING",
                "identityHashRef": "abc123abc123",
                "monitoringScope": "active",
                "status": "needs_attention",
                "accessOk": True,
                "grantOk": True,
                "antiSharingOk": False,
                "downloadsOk": True,
                "trustedContexts": 0,
                "pendingContexts": 1,
                "blockedContexts": 0,
                "revokedContexts": 0,
                "contextRefs": ["ctxabc123123"],
                "openIncidents": 0,
            },
        ],
    }
    output = tmp_path / "remote_cohort_context_reconcile.local.json"

    result = build_remote_cohort_context_reconcile(matrix_payload=payload)
    written = write_remote_cohort_context_reconcile(result, output)
    serialized = json.dumps(result, sort_keys=True)

    assert written == output
    assert result["summary"]["operatorReviewRequiredCount"] == 1
    assert result["actions"][0]["action"] == "operator_review_pending_context"
    assert "@" not in serialized
    assert "https://" not in serialized
    assert ("C:" + "\\BOTS\\") not in serialized
    assert result["privacy"]["rawEmailsReturned"] is False
