from __future__ import annotations

import argparse
import json
import os
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SQX144_CUSTOM_RESULTS1_VERSION = "sqx144-custom-results1-results-plugin-template-v1"
SQX144_CUSTOM_RESULTS1_READONLY_MARKER = "sqx144-custom-results1-readonly-results-plugin-template-v1"
SQX144_CUSTOM_RESULTS1_STATUS = "custom_results1_template_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool"
EVIDENCE_DIR_PARTS = (".local", "sqx144_custom_results1")
TEMPLATE_RELATIVE = Path("integrations") / "sqx144" / "results_plugins" / "SQX Edge Custom Results Template"

DEFAULT_DOWNLOAD_ROOT = Path(os.environ.get("SQX_CUSTOM_RESULTS_DOWNLOADS", "")) if os.environ.get("SQX_CUSTOM_RESULTS_DOWNLOADS") else Path.home() / "Downloads" / "CustomResultsSQX"

ALLOWED_DEFAULT_MESSAGES = (
    "STRATEGY_DATA",
    "SET_THEME",
    "SET_LANGUAGE",
    "GET_STATS",
    "STATS_RESPONSE",
)
OPTIONAL_GATED_MESSAGES = (
    "GET_ORDERS",
    "GET_LAST_SETTINGS_XML",
    "GET_SYMBOL_INFO",
    "ORDERS_RESPONSE",
    "LAST_SETTINGS_XML_RESPONSE",
    "SYMBOL_INFO_RESPONSE",
)
BLOCKED_BY_DEFAULT = (
    "GET_SOURCE_CODE",
    "resultsPlugins/create",
    "resultsPlugins/rename",
    "resultsPlugins/delete",
    "localStorage",
    "sessionStorage",
    "indexedDB",
)

PACKAGE_SPECS: tuple[dict[str, Any], ...] = (
    {
        "id": "robustness_scorecard",
        "file": "RobustnessScorecard.zip",
        "kind": "results_plugin",
        "expectedFolder": "RobustnessScorecard",
        "fit": "best_immediate_fit",
        "reason": "GET_STATS-only scorecard style panel that can become a read-only diagnostic template candidate.",
        "metrics": ["ProfitFactor", "RExpectancy", "ReturnDDRatio", "Calmar", "Stability", "SQN", "NumberOfTrades"],
        "sourceUrl": "https://strategyquant.com/codebase/robustness-score-card/",
    },
    {
        "id": "oos_degradation_scorecard",
        "file": "OOSDegradationScorecard.zip",
        "kind": "results_plugin",
        "expectedFolder": "OOSDegradationScorecard",
        "fit": "best_immediate_fit",
        "reason": "IS/OOS retention score from stats; useful as methodology review, not as pass-state promotion.",
        "metrics": ["ProfitFactor", "RExpectancy", "PctDrawdown", "ReturnDDRatio", "SharpeRatio", "WinningPct", "Stability"],
        "sourceUrl": "https://strategyquant.com/codebase/is-and-oos-degradation-score/",
    },
    {
        "id": "edge_decay_analyzer",
        "file": "Edge-Decay-Max-Loss-Analyzer-1.zip",
        "kind": "results_plugin",
        "expectedFolder": "Edge Decay & Max Loss Analyzer",
        "fit": "strong_but_gated",
        "reason": "High methodology value, but uses full orders/trades and browser persistence; needs a privacy/performance gate.",
        "metrics": ["PF decay", "XS", "MFE", "MAE", "concurrency", "streaks", "ReturnDDRatio"],
        "sourceUrl": "https://strategyquant.com/codebase/edge-decay-analyzer/",
    },
    {
        "id": "win_rate_edge",
        "file": "WinRateEdge-1.zip",
        "kind": "results_plugin",
        "expectedFolder": "WinRateEdge",
        "fit": "research_only",
        "reason": "Needs random-entry baseline strategies plus full orders; valuable for research, not direct SQX Edge promotion.",
        "metrics": ["winRateDelta", "zScore", "MFE", "MAE", "MFE/MAE", "randomBaseline"],
        "sourceUrl": "https://strategyquant.com/codebase/strategy-vs-random-edge-testing-winrateedge-results-panel/",
    },
    {
        "id": "two_step_challenge_analyzer",
        "file": "2-Step-Challenge-Analyzer.zip",
        "kind": "results_plugin",
        "expectedFolder": "2-Step Challenge Analyzer",
        "fit": "optional_commercial",
        "reason": "Useful for prop-firm simulation and EV review; not core Capa1/Capa2 methodology.",
        "metrics": ["phasePass", "dailyLoss", "maxLoss", "minTradingDays", "monteCarloPassProbability", "expectedValue"],
        "sourceUrl": "https://strategyquant.com/codebase/the-2-step-challenge-analyzer-for-ftmo-know-if-your-strategy-will-pass-before-you-pay/",
    },
    {
        "id": "random_entries",
        "file": "RandomEntries-1.htm",
        "kind": "snippet_package",
        "expectedFolder": "extend",
        "fit": "research_only",
        "reason": "Random Entry block supports WinRateEdge baselines but requires snippet/template install and seed/reproducibility policy.",
        "metrics": ["randomEntryProbability"],
        "sourceUrl": "operator_downloaded_package",
    },
    {
        "id": "edge_decay_user_guide",
        "file": "Edge_Decay_Analyzer_User_Guide.pdf",
        "kind": "manual",
        "fit": "supporting_reference",
        "reason": "Manual/reference for Edge Decay installation and interpretation.",
        "metrics": [],
        "sourceUrl": "operator_downloaded_manual",
    },
    {
        "id": "parameter_sweeps_multiple_testing",
        "file": "Parameter-Sweeps-and-Multiple-Testing-1.docx",
        "kind": "methodology_guide",
        "fit": "supporting_reference",
        "reason": "Supports false-positive control and coherent sweep-shape interpretation.",
        "metrics": ["zScore", "multipleTesting", "parameterSweepShape"],
        "sourceUrl": "operator_downloaded_guide",
    },
    {
        "id": "win_rate_edge_understanding",
        "file": "Understanding-Win-Rate-Edge-Testing-1.docx",
        "kind": "methodology_guide",
        "fit": "supporting_reference",
        "reason": "Explains win-rate edge interpretation against random baselines.",
        "metrics": ["zScore", "winRateDelta", "randomBaseline"],
        "sourceUrl": "operator_downloaded_guide",
    },
    {
        "id": "win_rate_edge_user_guide",
        "file": "User-Guide-How-the-Test-Was-Performed-for-the-Win-Rate-Edge-Result-Panel-1.docx",
        "kind": "methodology_guide",
        "fit": "supporting_reference",
        "reason": "Practical Random Entry plus WinRateEdge workflow guide.",
        "metrics": ["randomEntryWorkflow", "builderRetesterWorkflow"],
        "sourceUrl": "operator_downloaded_guide",
    },
)


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _safe_read_text_from_zip(zip_path: Path, suffix: str) -> tuple[str | None, str | None]:
    if not zip_path.exists() or not zipfile.is_zipfile(zip_path):
        return None, None
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            normalized = info.filename.replace("\\", "/")
            if normalized.lower().endswith(suffix.lower()):
                with archive.open(info) as handle:
                    return handle.read().decode("utf-8", errors="replace"), normalized
    return None, None


def _zip_entries(zip_path: Path, limit: int = 24) -> list[dict[str, Any]]:
    if not zip_path.exists() or not zipfile.is_zipfile(zip_path):
        return []
    entries: list[dict[str, Any]] = []
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist()[:limit]:
            entries.append({
                "name": info.filename.replace("\\", "/"),
                "size": info.file_size,
                "isDirectory": info.is_dir(),
            })
    return entries


def _scan_text(text: str | None) -> dict[str, Any]:
    source = text or ""
    found_messages = [marker for marker in ALLOWED_DEFAULT_MESSAGES + OPTIONAL_GATED_MESSAGES + ("GET_SOURCE_CODE",) if marker in source]
    blocked_markers = [marker for marker in BLOCKED_BY_DEFAULT if marker in source]
    fetch_calls = re.findall(r"fetch\s*\(([^)]{0,180})\)", source, flags=re.IGNORECASE)
    remote_fetch = [call.strip()[:120] for call in fetch_calls if "http://" in call.lower() or "https://" in call.lower() or "'//" in call or '"//' in call]
    local_fetch = [call.strip()[:120] for call in fetch_calls if call.strip() not in remote_fetch]
    write_like_markers = [
        marker
        for marker in ("localStorage.setItem", "sessionStorage.setItem", "indexedDB", "Blob(", "URL.createObjectURL", "download")
        if marker in source
    ]
    return {
        "messagesDetected": sorted(set(found_messages)),
        "defaultAllowedMessagesDetected": sorted(set(marker for marker in found_messages if marker in ALLOWED_DEFAULT_MESSAGES)),
        "optionalGatedMessagesDetected": sorted(set(marker for marker in found_messages if marker in OPTIONAL_GATED_MESSAGES)),
        "blockedMarkersDetected": sorted(set(blocked_markers)),
        "localFetchCallCount": len(local_fetch),
        "remoteFetchDetected": bool(remote_fetch),
        "remoteFetchCallSamples": remote_fetch[:4],
        "writeLikeMarkersDetected": sorted(set(write_like_markers)),
        "hasPostMessage": "postMessage" in source,
    }


def _scan_random_entries(path: Path) -> dict[str, Any]:
    text, entry = _safe_read_text_from_zip(path, "RandomEntry.java")
    template_entries = []
    if path.exists() and zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            template_entries = [
                info.filename.replace("\\", "/")
                for info in archive.infolist()
                if info.filename.replace("\\", "/").lower().endswith("randomentry.tpl")
            ][:12]
    return {
        "entrypoint": entry,
        "javaClassDetected": bool(text and "class RandomEntry" in text),
        "buildingBlockDetected": bool(text and "@BuildingBlock" in text),
        "mathRandomDetected": bool(text and "Math.random" in text),
        "templateFiles": template_entries,
        "riskNotes": [
            "requires_snippet_template_install_gate",
            "requires_compile_snippets_validation",
            "non_deterministic_without_seed_policy",
        ],
    }


def _scan_artifact(download_root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    artifact = download_root / spec["file"]
    result: dict[str, Any] = {
        "id": spec["id"],
        "file": spec["file"],
        "kind": spec["kind"],
        "present": artifact.exists(),
        "fit": spec["fit"],
        "reason": spec["reason"],
        "metrics": spec.get("metrics", []),
        "sourceUrl": spec.get("sourceUrl"),
        "localPathReturned": False,
    }
    if not artifact.exists():
        result["status"] = "missing"
        return result
    result["sizeBytes"] = artifact.stat().st_size
    if spec["kind"] == "results_plugin":
        index_text, index_entry = _safe_read_text_from_zip(artifact, "index.html")
        readme_text, readme_entry = _safe_read_text_from_zip(artifact, "README.md")
        scan = _scan_text(index_text)
        result.update({
            "status": "scanned",
            "zipEntries": _zip_entries(artifact),
            "entrypoint": index_entry,
            "readme": readme_entry,
            "scan": scan,
            "requiresOrdersGate": "GET_ORDERS" in scan["messagesDetected"],
            "requiresPersistenceWaiver": any(marker in scan["blockedMarkersDetected"] for marker in ("localStorage", "sessionStorage", "indexedDB")),
            "remoteNetworkObserved": scan["remoteFetchDetected"],
            "readmePresent": bool(readme_text),
        })
        return result
    if spec["id"] == "random_entries":
        result.update({
            "status": "scanned" if zipfile.is_zipfile(artifact) else "not_a_zip_package",
            "zipEntries": _zip_entries(artifact),
            "snippet": _scan_random_entries(artifact),
        })
        return result
    result["status"] = "present_reference_only"
    return result


def _base_payload(action: str) -> dict[str, Any]:
    return {
        "ok": False,
        "version": SQX144_CUSTOM_RESULTS1_VERSION,
        "readOnlyMarker": SQX144_CUSTOM_RESULTS1_READONLY_MARKER,
        "action": action,
        "status": SQX144_CUSTOM_RESULTS1_STATUS,
        "hostProfile": "sqx144_full",
        "phase": "SQX144-CUSTOM-RESULTS1",
        "phaseLabel": "SQX144-CUSTOM-RESULTS1 - Read-Only Results Plugin Template",
        "installExecuted": False,
        "guards": {
            "readOnlyStudy": True,
            "readOnlyResultsPluginTemplate": True,
            "installsIntoSqxHost": False,
            "sqxInstallAllowed": False,
            "writesSqxHost": False,
            "writesDataDb": False,
            "writesUserProjects": False,
            "mutatesDatabanks": False,
            "runsSqxTasks": False,
            "launchesSqxRuntime": False,
            "usesMigrationTool": False,
            "usesMcpCalls": False,
            "usesPluginCreateRenameDelete": False,
            "usesGetSourceCode": False,
            "usesGetOrdersByDefault": False,
            "browserPersistenceAllowedByDefault": False,
        },
        "privacy": {
            "localPathsReturned": False,
            "rawStrategyNamesReturned": False,
            "rawOrdersReturned": False,
            "sourceCodeReturned": False,
            "licenseMaterialReturned": False,
            "secretsReturned": False,
        },
    }


def status_payload(project_root: str | Path = ".") -> dict[str, Any]:
    root = _project_root(project_root)
    template_root = root / TEMPLATE_RELATIVE
    payload = _base_payload("status")
    payload.update({
        "ok": True,
        "actions": ["status", "scan-downloads", "template-smoke", "report", "decision-template"],
        "template": {
            "ref": str(TEMPLATE_RELATIVE).replace("\\", "/"),
            "present": template_root.exists(),
            "expectedFiles": ["index.html", "fixtures/fixtures.js", "locales/en.json", "locales/es.json", "README.md"],
        },
        "downloadRootRef": "operator_downloads_custom_results_sqx",
        "downloadRootPresent": DEFAULT_DOWNLOAD_ROOT.exists(),
        "nextAction": "run report to refresh candidate matrix and template smoke",
    })
    return payload


def scan_downloads_payload(download_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(download_root or DEFAULT_DOWNLOAD_ROOT).resolve(strict=False)
    payload = _base_payload("scan-downloads")
    artifacts = [_scan_artifact(root, spec) for spec in PACKAGE_SPECS]
    present = [item for item in artifacts if item.get("present")]
    payload.update({
        "ok": True,
        "status": "custom_results1_download_scan_completed_no_install_no_sqx_runtime_no_db_no_projects_no_databanks_no_migration_tool",
        "downloadRootRef": "operator_downloads_custom_results_sqx",
        "downloadRootPresent": root.exists(),
        "artifactCount": len(artifacts),
        "presentCount": len(present),
        "artifacts": artifacts,
        "comparisonMatrix": [
            {
                "id": item["id"],
                "kind": item["kind"],
                "fit": item["fit"],
                "present": item["present"],
                "messages": item.get("scan", {}).get("messagesDetected", []),
                "requiresOrdersGate": item.get("requiresOrdersGate", False),
                "requiresPersistenceWaiver": item.get("requiresPersistenceWaiver", False),
                "remoteNetworkObserved": item.get("remoteNetworkObserved", False),
                "reason": item["reason"],
            }
            for item in artifacts
        ],
        "recommendation": {
            "firstTemplateInputs": ["robustness_scorecard", "oos_degradation_scorecard"],
            "gatedResearch": ["edge_decay_analyzer", "win_rate_edge", "random_entries"],
            "optionalCommercial": ["two_step_challenge_analyzer"],
        },
    })
    return payload


def template_smoke_payload(project_root: str | Path = ".") -> dict[str, Any]:
    root = _project_root(project_root)
    template_root = root / TEMPLATE_RELATIVE
    expected = [
        "index.html",
        "fixtures/fixtures.js",
        "locales/en.json",
        "locales/es.json",
        "README.md",
    ]
    files = {name: template_root / name for name in expected}
    index_text = files["index.html"].read_text(encoding="utf-8") if files["index.html"].exists() else ""
    fixtures_text = files["fixtures/fixtures.js"].read_text(encoding="utf-8") if files["fixtures/fixtures.js"].exists() else ""
    locale_ok = all(files[name].exists() for name in ("locales/en.json", "locales/es.json"))
    forbidden_in_template = [
        marker
        for marker in ("GET_SOURCE_CODE", "GET_ORDERS", "localStorage", "sessionStorage", "indexedDB", "resultsPlugins/create", "resultsPlugins/rename", "resultsPlugins/delete")
        if marker in index_text or marker in fixtures_text
    ]
    required_markers = [
        "SQX_EDGE_CUSTOM_RESULTS_TEMPLATE_VERSION",
        "STRATEGY_DATA",
        "GET_STATS",
        "STATS_RESPONSE",
        "SET_THEME",
        "SET_LANGUAGE",
        "ready",
        "review",
        "blocked",
        "noStrategy",
        "missingStats",
        "largePortfolio",
    ]
    missing_markers = [marker for marker in required_markers if marker not in index_text and marker not in fixtures_text]
    ok = template_root.exists() and all(path.exists() for path in files.values()) and locale_ok and not forbidden_in_template and not missing_markers
    payload = _base_payload("template-smoke")
    payload.update({
        "ok": ok,
        "status": "custom_results1_readonly_results_plugin_template_smoke_passed_no_install_no_sqx_runtime_no_db_no_projects_no_databanks_no_migration_tool" if ok else "custom_results1_readonly_results_plugin_template_smoke_failed_no_install_no_sqx_runtime_no_db_no_projects_no_databanks_no_migration_tool",
        "templateRef": str(TEMPLATE_RELATIVE).replace("\\", "/"),
        "files": [{"name": name, "present": path.exists()} for name, path in files.items()],
        "localeFilesPresent": locale_ok,
        "forbiddenMarkersInTemplate": forbidden_in_template,
        "missingRequiredMarkers": missing_markers,
        "fixtureNames": ["ready", "review", "blocked", "noStrategy", "missingStats", "largePortfolio"],
    })
    return payload


def report_payload(project_root: str | Path = ".", download_root: str | Path | None = None, write_evidence: bool = False) -> dict[str, Any]:
    payload = _base_payload("report")
    scan = scan_downloads_payload(download_root)
    smoke = template_smoke_payload(project_root)
    ok = scan["ok"] and smoke["ok"]
    payload.update({
        "ok": ok,
        "status": "custom_results1_report_completed_template_ready_no_sqx_runtime_no_host_install" if ok else "custom_results1_report_completed_with_blockers_no_sqx_runtime_no_host_install",
        "scan": scan,
        "templateSmoke": smoke,
        "decision": {
            "templateReady": smoke["ok"],
            "installApproved": False,
            "installRequiresExactGate": "APRUEBO SQX144 CUSTOM RESULTS1 INSTALL TEMPLATE host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_migration_tool",
            "nextRecommendedGate": "SQX144-CUSTOM-RESULTS3 optional manual install gate",
            "downloadedPluginsInstallBlocked": True,
            "methodology": "Custom Results are diagnostic panels only; they do not promote strategies or alter pass states.",
        },
        "evidenceWritten": False,
    })
    if write_evidence:
        payload["evidenceRef"] = write_evidence_file(_project_root(project_root), "report", payload)
        payload["evidenceWritten"] = True
    return payload


def decision_template_payload(project_root: str | Path = ".") -> dict[str, Any]:
    payload = status_payload(project_root)
    payload["action"] = "decision-template"
    payload["selectedDecision"] = "PREPARAR SQX144 CUSTOM RESULTS TEMPLATE READ-ONLY SIN INSTALAR EN SQX"
    payload["approvalNotRequiredBecause"] = "repo_only_template_and_static_scan_no_sqx_runtime_no_host_install"
    payload["blockedDecisions"] = [
        "INSTALAR DESCARGAS EN SQX144 FULL",
        "USAR GET_SOURCE_CODE",
        "USAR GET_ORDERS SIN GATE",
        "CREAR/RENOMBRAR/BORRAR PLUGINS DESDE SQX",
        "ESCRIBIR data.db, user/projects O databanks",
        "USAR MIGRATION TOOL",
    ]
    return payload


def write_evidence_file(project_root: Path, action: str, payload: dict[str, Any]) -> str:
    evidence_dir = project_root.joinpath(*EVIDENCE_DIR_PARTS)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    filename = f"sqx144_custom_results1_{action}_{_utc_stamp()}.json"
    (evidence_dir / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return filename


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("status", "scan-downloads", "template-smoke", "report", "decision-template"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--download-root", default=None)
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)

    if args.action == "scan-downloads":
        payload = scan_downloads_payload(args.download_root)
    elif args.action == "template-smoke":
        payload = template_smoke_payload(args.project_root)
    elif args.action == "report":
        payload = report_payload(args.project_root, args.download_root, write_evidence=args.write_evidence)
    elif args.action == "decision-template":
        payload = decision_template_payload(args.project_root)
    else:
        payload = status_payload(args.project_root)

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
