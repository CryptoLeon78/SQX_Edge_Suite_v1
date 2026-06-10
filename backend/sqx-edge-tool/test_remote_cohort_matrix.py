import json

from core.remote_cohort_matrix import (
    REMOTE_COHORT_MATRIX_VERSION,
    build_remote_cohort_matrix,
    write_remote_cohort_matrix,
)


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_remote_cohort_matrix_builds_alias_only_status(tmp_path):
    aliases = tmp_path / "user_aliases.local.json"
    entitlements = tmp_path / "remote_entitlements.local.json"
    access_control = tmp_path / "remote_access_control.local.json"
    support_cases = tmp_path / "support_cases.local.jsonl"
    download_smoke = tmp_path / "remote_cohort_download_smoke.local.json"

    _write_json(
        aliases,
        {
            "aliases": [
                {"alias": "CREATOR-IVAN", "role": "creator_operator", "identityHashRef": "aaa111aaa111"},
                {"alias": "TESTER-NEW", "role": "tester_free", "identityHashRef": "bbb222bbb222"},
            ]
        },
    )
    _write_json(
        entitlements,
        {
            "grants": [
                {
                    "emailHash": "aaa111aaa111ffffffffffffffffffffffffffffffffffffffffffffffffffff",
                    "status": "active",
                    "entitlementKind": "tester_free",
                    "featureScope": "full",
                },
                {
                    "emailHash": "bbb222bbb222ffffffffffffffffffffffffffffffffffffffffffffffffffff",
                    "status": "active",
                    "entitlementKind": "tester_free",
                    "featureScope": "full",
                },
            ]
        },
    )
    _write_json(
        access_control,
        {
            "identities": {
                "aaa111aaa111ffffffffffffffffffffffffffffffffffffffffffffffffffff": {
                    "identityHashRef": "aaa111aaa111",
                    "status": "active",
                    "contexts": [{"status": "trusted", "contextRef": "ctxaaa111111"}],
                },
                "bbb222bbb222ffffffffffffffffffffffffffffffffffffffffffffffffffff": {
                    "identityHashRef": "bbb222bbb222",
                    "status": "active",
                    "contexts": [{"status": "pending", "contextRef": "ctxbbb222222"}],
                },
            }
        },
    )
    support_cases.write_text(
        json.dumps(
            {
                "status": "open",
                "remoteIdentityRef": {"emailHashRef": "bbb222bbb222"},
                "summary": "Needs help",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    _write_json(
        download_smoke,
        {
            "cohort": [
                {"alias": "CREATOR-IVAN", "access": "ok", "downloadSmoke": "ok"},
            ]
        },
    )

    result = build_remote_cohort_matrix(
        aliases_path=aliases,
        entitlements_path=entitlements,
        access_control_path=access_control,
        support_cases_path=support_cases,
        download_smoke_path=download_smoke,
    )

    assert result["schemaVersion"] == REMOTE_COHORT_MATRIX_VERSION
    assert result["summary"]["aliasCount"] == 2
    assert result["summary"]["readyCount"] == 1
    assert result["summary"]["needsAttentionCount"] == 1
    assert result["summary"]["openIncidents"] == 1
    creator = result["rows"][0]
    tester = result["rows"][1]
    assert creator["status"] == "ready"
    assert creator["accessOk"] is True
    assert creator["grantOk"] is True
    assert creator["antiSharingOk"] is True
    assert creator["downloadsOk"] is True
    assert tester["status"] == "needs_attention"
    assert "anti_sharing_context_not_ready" in tester["blockers"]
    assert "download_smoke_not_confirmed" in tester["blockers"]
    assert "open_incidents" in tester["blockers"]


def test_remote_cohort_matrix_redacts_private_values_and_writes_local_output(tmp_path):
    aliases = tmp_path / "user_aliases.local.json"
    entitlements = tmp_path / "remote_entitlements.local.json"
    access_control = tmp_path / "remote_access_control.local.json"
    support_cases = tmp_path / "support_cases.local.jsonl"
    download_smoke = tmp_path / "remote_cohort_download_smoke.local.json"
    output = tmp_path / "out" / "remote_cohort_matrix.local.json"

    _write_json(aliases, {"aliases": [{"alias": "TESTER-A", "role": "tester_free", "identityHashRef": "abc123abc123"}]})
    _write_json(
        entitlements,
        {"grants": [{"emailHash": "abc123abc123ffffffffffffffffffffffffffffffffffffffffffffffffffff", "status": "active"}]},
    )
    _write_json(
        access_control,
        {
            "identities": {
                "abc123abc123ffffffffffffffffffffffffffffffffffffffffffffffffffff": {
                    "identityHashRef": "abc123abc123",
                    "contexts": [{"status": "trusted", "contextRef": "ctxabc123123"}],
                }
            }
        },
    )
    support_cases.write_text("", encoding="utf-8")
    _write_json(download_smoke, {"cohort": [{"alias": "TESTER-A", "access": "ok", "downloadSmoke": "ok"}]})

    result = build_remote_cohort_matrix(
        aliases_path=aliases,
        entitlements_path=entitlements,
        access_control_path=access_control,
        support_cases_path=support_cases,
        download_smoke_path=download_smoke,
    )
    written = write_remote_cohort_matrix(result, output)
    serialized = json.dumps(result, sort_keys=True)

    assert written == output
    assert output.is_file()
    assert "@" not in serialized
    assert "https://" not in serialized
    assert ("C:" + "\\BOTS\\") not in serialized
    assert ("__Host-" + "sqx_remote_session") not in serialized
    assert result["privacy"]["rawEmailsReturned"] is False
    assert result["privacy"]["localPathsReturned"] is False


def test_remote_cohort_matrix_separates_standby_aliases_from_active_blockers(tmp_path):
    aliases = tmp_path / "user_aliases.local.json"
    entitlements = tmp_path / "remote_entitlements.local.json"
    access_control = tmp_path / "remote_access_control.local.json"
    support_cases = tmp_path / "support_cases.local.jsonl"
    download_smoke = tmp_path / "remote_cohort_download_smoke.local.json"
    scope = tmp_path / "remote_cohort_scope.local.json"

    _write_json(
        aliases,
        {
            "aliases": [
                {"alias": "TESTER-ACTIVE", "role": "tester_free", "identityHashRef": "aaa111aaa111"},
                {"alias": "TESTER-STANDBY", "role": "tester_free", "identityHashRef": "bbb222bbb222"},
            ]
        },
    )
    _write_json(
        entitlements,
        {
            "grants": [
                {"emailHash": "aaa111aaa111ffffffffffffffffffffffffffffffffffffffffffffffffffff", "status": "active"},
                {"emailHash": "bbb222bbb222ffffffffffffffffffffffffffffffffffffffffffffffffffff", "status": "active"},
            ]
        },
    )
    _write_json(
        access_control,
        {
            "identities": {
                "aaa111aaa111ffffffffffffffffffffffffffffffffffffffffffffffffffff": {
                    "identityHashRef": "aaa111aaa111",
                    "contexts": [{"status": "trusted", "contextRef": "ctxaaa111111"}],
                }
            }
        },
    )
    support_cases.write_text("", encoding="utf-8")
    _write_json(download_smoke, {"cohort": [{"alias": "TESTER-ACTIVE", "access": "ok", "downloadSmoke": "ok"}]})
    _write_json(
        scope,
        {
            "aliases": [
                {"alias": "TESTER-ACTIVE", "monitoringScope": "active", "reason": "in_current_smoke"},
                {"alias": "TESTER-STANDBY", "monitoringScope": "standby", "reason": "future_tester"},
            ]
        },
    )

    result = build_remote_cohort_matrix(
        aliases_path=aliases,
        entitlements_path=entitlements,
        access_control_path=access_control,
        support_cases_path=support_cases,
        download_smoke_path=download_smoke,
        scope_path=scope,
    )

    assert result["summary"]["aliasCount"] == 2
    assert result["summary"]["activeAliasCount"] == 1
    assert result["summary"]["standbyAliasCount"] == 1
    assert result["summary"]["readyCount"] == 1
    assert result["summary"]["needsAttentionCount"] == 0
    assert result["summary"]["activeReadyCount"] == 1
    assert result["summary"]["activeNeedsAttentionCount"] == 0
    standby = next(row for row in result["rows"] if row["alias"] == "TESTER-STANDBY")
    assert standby["status"] == "standby"
    assert standby["monitoringScope"] == "standby"
    assert "standby_not_in_current_monitoring_scope" in standby["blockers"]
