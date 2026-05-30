import json

from api import server
from core.sqx142_copy_only_migration_checklist import (
    COPY_ONLY_MIGRATION_CHECKLIST_VERSION,
    build_copy_only_migration_checklist,
    export_copy_only_migration_checklist_csv,
)


def _assert_public_safe(payload):
    encoded = json.dumps(payload, ensure_ascii=False)
    assert r"C:\\" not in encoded
    assert "SQX_142_Crack" not in encoded
    assert "ivan@example" not in encoded
    assert "token=" not in encoded.lower()
    assert "secret" not in encoded.lower()
    assert "password=" not in encoded.lower()
    assert "StrategyQuantX.exe" not in encoded


def test_copy_only_checklist_default_matrix_blocks_sensitive_material():
    report = build_copy_only_migration_checklist()

    assert report["ok"] is True
    assert report["version"] == COPY_ONLY_MIGRATION_CHECKLIST_VERSION
    assert report["mode"] == "checklist_only_no_copy"
    assert report["summary"]["inputItems"] >= 5
    assert report["summary"]["allowCopy"] >= 1
    assert report["summary"]["reviewCopy"] >= 1
    assert report["summary"]["blockCopy"] >= 2
    assert report["guards"]["copy_executed"] is False
    assert report["guards"]["migration_tool_used"] is False
    assert report["guards"]["license_material_allowed"] is False
    _assert_public_safe(report)


def test_copy_only_checklist_classifies_allow_review_and_block_items():
    report = build_copy_only_migration_checklist({
        "items": [
            {
                "kind": "results_plugin_owned",
                "label": "SQX Edge Readiness Panel",
                "relativePath": "user/extend/ResultsPlugins/SQX Edge Readiness Panel",
                "operation": "copy_folder",
            },
            {
                "kind": "project_copy",
                "label": "Selected project export",
                "relativePath": "user/projects/OperatorSelectedProject",
                "operation": "copy_folder_after_backup",
            },
            {
                "kind": "license_material",
                "label": "activation file",
                "relativePath": "user/license/license.dat",
                "operation": "copy_file",
            },
        ]
    })

    decisions = [item["decision"] for item in report["items"]]
    assert decisions == ["allow_copy", "review_copy", "block_copy"]
    blocked = report["items"][2]
    assert any("license" in blocker for blocker in blocked["blockers"])
    assert blocked["manualSteps"] == []
    _assert_public_safe(report)


def test_copy_only_checklist_blocks_engine_data_and_migration_tool_items():
    report = build_copy_only_migration_checklist({
        "items": [
            {"kind": "engine_binary", "label": "StrategyQuantX.exe", "relativePath": "StrategyQuantX.exe"},
            {"kind": "data_db", "label": "data db", "relativePath": "user/data/data.db"},
            {"kind": "migration_tool", "label": "Migration Tool export", "relativePath": "internal/MigrationTool"},
        ]
    })

    assert report["summary"]["blockCopy"] == 3
    assert all(item["decision"] == "block_copy" for item in report["items"])
    _assert_public_safe(report)


def test_copy_only_checklist_redacts_private_markers_and_exports_csv():
    report = build_copy_only_migration_checklist({
        "items": [
            {
                "kind": "settings_copy",
                "label": r"C:\\BOTS\\Versiones\\SQX_142_Crack\\settings token=secret",
                "relativePath": r"C:\\private\\settings\\ui.json",
                "operatorEmail": "ivan@example.invalid",
                "brokerPrivate": "password=hidden",
            }
        ]
    })
    csv_export = export_copy_only_migration_checklist_csv(report)

    assert report["summary"]["redactedFields"] >= 3
    assert "itemId,kind,pathRef" in csv_export
    _assert_public_safe(report)
    _assert_public_safe({"csv": csv_export})


def test_copy_only_checklist_route_is_local_operator_only_and_returns_optional_csv():
    client = server.app.test_client()
    response = client.post(
        "/api/sqx142/migration/copy-only-checklist",
        json={"items": [{"kind": "project_copy", "relativePath": "user/projects/OperatorSelectedProject"}], "includeCsvExport": True},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["version"] == COPY_ONLY_MIGRATION_CHECKLIST_VERSION
    assert data["privacy"]["local_paths_returned"] is False
    assert "csvExport" in data
    _assert_public_safe(data)

    blocked = client.post(
        "/api/sqx142/migration/copy-only-checklist",
        json={"items": [{"kind": "project_copy", "relativePath": "user/projects/OperatorSelectedProject"}]},
        base_url="https://app.sqxedgesuite.org",
        headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert blocked.status_code == 403
    assert blocked.get_json()["error"] == "local_operator_required"
