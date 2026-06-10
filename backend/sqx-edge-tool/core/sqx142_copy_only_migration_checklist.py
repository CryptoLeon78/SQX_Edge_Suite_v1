from __future__ import annotations

import csv
import hashlib
import io
import re
from datetime import datetime, timezone
from typing import Any, Mapping


COPY_ONLY_MIGRATION_CHECKLIST_VERSION = "sqx142-copy-only-migration-checklist-v1"

DEFAULT_ITEMS = [
    {
        "kind": "results_plugin_owned",
        "label": "SQX Edge-owned Results Plugin payload",
        "relativePath": "user/extend/ResultsPlugins/SQX Edge Readiness Panel",
        "operation": "copy_folder",
    },
    {
        "kind": "project_copy",
        "label": "Operator-selected project copy",
        "relativePath": "user/projects/<selected-project-copy>",
        "operation": "copy_folder_after_backup",
    },
    {
        "kind": "settings_copy",
        "label": "Non-sensitive UI preferences export",
        "relativePath": "user/settings/<ui-preferences>",
        "operation": "copy_file_after_review",
    },
    {
        "kind": "license_material",
        "label": "License or activation material",
        "relativePath": "license/activation",
        "operation": "never_copy",
    },
    {
        "kind": "engine_binary",
        "label": "Engine binaries or internal jars",
        "relativePath": "internal/bin/engine",
        "operation": "never_copy",
    },
]

_PRIVATE_KEY_MARKERS = (
    "token",
    "secret",
    "password",
    "cookie",
    "email",
    "login",
    "account",
    "brokerPrivate",
    "protectedUrl",
    "path",
)

_PRIVATE_VALUE_RE = re.compile(
    r"(?i)([A-Z]:\\|\\\\|https?://\S*(?:token|secret|password|protected)\S*|"
    r"\b[\w.+-]+@[\w.-]+\.[A-Z]{2,}\b|"
    r"\b(?:token|secret|password|api[_-]?key|grant[_-]?key|session)[=:]\s*\S+)"
)

_BLOCK_MARKERS = (
    "license",
    "licence",
    "activation",
    "activacion",
    "crack",
    "bypass",
    "keygen",
    "token",
    "secret",
    "password",
    "cookie",
    "internal",
    "engine",
    "bin",
    "jre",
    "runtime",
    "strategyquantx.exe",
    "servletmcp",
    "migrationtool",
    "migration tool",
    "data.db",
    "user/data",
    "databank",
    "logs",
)

_REVIEW_MARKERS = (
    "user/projects",
    "project",
    ".sqx",
    ".cfx",
    "settings",
    "config",
    "templates",
    "blocksettings",
    "presets",
)

_ALLOW_MARKERS = (
    "user/extend/resultsplugins/sqx edge readiness panel",
    "user/extend/resultsplugins/source code translator",
    "results_plugin_owned",
    "sqx_edge_owned",
    "operator_export",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _hash_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _normalize(value: Any) -> str:
    return re.sub(r"[^a-z0-9./_-]+", "", _text(value).casefold().replace("\\", "/"))


def _redact_text(value: Any, default: str = "") -> tuple[str, bool]:
    text = _text(value, default)
    redacted = _PRIVATE_VALUE_RE.sub("[redacted]", text)
    redacted = re.sub(r"(?i)\bSQX_142_Crack\b", "[redacted]", redacted)
    return redacted[:180], redacted != text


def _redact_mapping(value: Mapping[str, Any]) -> tuple[dict[str, Any], int]:
    clean: dict[str, Any] = {}
    redactions = 0
    for key, raw in value.items():
        key_text, key_redacted = _redact_text(key)
        if key_redacted or any(marker.casefold() in key_text.casefold() for marker in _PRIVATE_KEY_MARKERS):
            clean[key_text] = "[redacted]"
            redactions += 1
            continue
        if isinstance(raw, Mapping):
            nested, nested_redactions = _redact_mapping(raw)
            clean[key_text] = nested
            redactions += nested_redactions
            continue
        text, redacted = _redact_text(raw)
        clean[key_text] = text
        redactions += int(redacted)
    return clean, redactions


def _items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, Mapping):
        for key in ("items", "migrationItems", "copyItems", "checklist"):
            value = payload.get(key)
            if isinstance(value, list):
                return [dict(item) for item in value if isinstance(item, Mapping)]
    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, Mapping)]
    return [dict(item) for item in DEFAULT_ITEMS]


def _decision(kind: str, label: str, relative_path: str, operation: str) -> tuple[str, list[str], list[str]]:
    haystack = _normalize(f"{kind} {label} {relative_path} {operation}")
    blockers = []
    for marker in _BLOCK_MARKERS:
        if marker.replace(" ", "") not in haystack.replace(" ", ""):
            continue
        if marker in {"token", "secret", "password", "cookie"}:
            blockers.append("blocked_marker:sensitive_private_material")
        else:
            blockers.append(f"blocked_marker:{marker}")
    if blockers:
        return "block_copy", blockers, []
    warnings = []
    if any(marker in haystack for marker in _ALLOW_MARKERS):
        return "allow_copy", [], ["copy_requires_manual_backup_and_hash_check"]
    if any(marker in haystack for marker in _REVIEW_MARKERS):
        warnings.append("operator_review_required")
        warnings.append("copy_requires_manual_backup_and_hash_check")
        return "review_copy", [], warnings
    warnings.append("unknown_item_type")
    return "review_copy", [], warnings


def build_copy_only_migration_checklist(payload: Any = None) -> dict[str, Any]:
    rows = _items(payload)
    items: list[dict[str, Any]] = []
    redactions = 0
    for index, row in enumerate(rows):
        _clean, count = _redact_mapping(row)
        redactions += count
        kind = _text(row.get("kind") or row.get("type"), "unknown")
        label = _text(row.get("label") or row.get("name"), f"item-{index + 1}")
        relative_path = _text(row.get("relativePath") or row.get("path") or row.get("target"), "")
        operation = _text(row.get("operation") or row.get("action"), "copy_review")
        decision, blockers, warnings = _decision(kind, label, relative_path, operation)
        path_ref = _hash_id("path", relative_path or label)
        item = {
            "itemId": _hash_id("migration_item", f"{index}|{kind}|{label}|{relative_path}|{operation}"),
            "sourceIndex": index,
            "kind": kind[:80],
            "labelRef": _hash_id("label", label),
            "pathRef": path_ref,
            "operation": operation[:80],
            "decision": decision,
            "blockers": blockers,
            "warnings": warnings,
            "manualSteps": [
                "preflight_process_sweep",
                "backup_destination",
                "copy_only_after_operator_confirmation",
                "hash_verify",
                "manual_open_check",
            ] if decision != "block_copy" else [],
        }
        items.append(item)

    summary = {
        "inputItems": len(rows),
        "allowCopy": sum(1 for item in items if item["decision"] == "allow_copy"),
        "reviewCopy": sum(1 for item in items if item["decision"] == "review_copy"),
        "blockCopy": sum(1 for item in items if item["decision"] == "block_copy"),
        "redactedFields": redactions,
    }
    return {
        "ok": True,
        "version": COPY_ONLY_MIGRATION_CHECKLIST_VERSION,
        "mode": "checklist_only_no_copy",
        "source": "operator_copy_plan",
        "analyzedAt": _now_iso(),
        "summary": summary,
        "items": items,
        "guards": {
            "copy_executed": False,
            "migration_tool_used": False,
            "license_material_allowed": False,
            "activation_material_allowed": False,
            "engine_binary_allowed": False,
            "data_db_write_allowed": False,
            "user_projects_write_allowed": False,
            "sqx_runtime_started": False,
            "remote_tester_access": False,
        },
        "privacy": {
            "local_paths_returned": False,
            "raw_item_names_returned": False,
            "private_fields_returned": False,
            "tokens_returned": False,
        },
        "blockers": [],
    }


def export_copy_only_migration_checklist_csv(report: Mapping[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["itemId", "kind", "pathRef", "operation", "decision", "blockers", "warnings"],
        lineterminator="\n",
    )
    writer.writeheader()
    for item in report.get("items", []):
        if not isinstance(item, Mapping):
            continue
        writer.writerow({
            "itemId": item.get("itemId", ""),
            "kind": item.get("kind", ""),
            "pathRef": item.get("pathRef", ""),
            "operation": item.get("operation", ""),
            "decision": item.get("decision", ""),
            "blockers": "|".join(str(value) for value in item.get("blockers", [])),
            "warnings": "|".join(str(value) for value in item.get("warnings", [])),
        })
    return output.getvalue()
