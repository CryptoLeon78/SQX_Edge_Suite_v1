from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
PRODUCT_MANIFEST_PATH = CONFIG_DIR / "product_manifest.json"


def load_product_manifest() -> dict[str, Any]:
    return json.loads(PRODUCT_MANIFEST_PATH.read_text(encoding="utf-8-sig"))


def _license_path(product: dict[str, Any]) -> Path:
    configured = product.get("licensing", {}).get("licenseFile", "config/license.json")
    path = Path(configured)
    if not path.is_absolute():
        path = ROOT / path
    return path


def load_license_payload(product: dict[str, Any] | None = None) -> dict[str, Any] | None:
    manifest = product or load_product_manifest()
    path = _license_path(manifest)
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError:
            return None


def _features_for_level(product: dict[str, Any], level: str) -> list[str]:
    access = product.get("accessLevels", {})
    return list((access.get(level) or {}).get("features") or [])


def _level_label(product: dict[str, Any], level: str, fallback: str) -> str:
    access = product.get("accessLevels", {})
    return str((access.get(level) or {}).get("label") or fallback)


def _feature_catalog(product: dict[str, Any]) -> dict[str, Any]:
    return dict(product.get("features") or {})


def _build_status(product: dict[str, Any], today: date) -> dict[str, Any]:
    build = product.get("build", {})
    channel = build.get("channel", "free")
    if channel == "internal":
        return {
            "ok": True,
            "active": True,
            "state": "internal",
            "plan": "internal",
            "label": _level_label(product, "internal", "SQX Edge Internal"),
            "source": "build_profile",
            "build_channel": channel,
            "features": _features_for_level(product, "internal"),
            "feature_catalog": _feature_catalog(product),
            "expires_at": None,
            "days_remaining": None,
            "message": "Build interno con todas las capacidades habilitadas para desarrollo.",
            "checked_at": today.isoformat(),
        }
    return {
        "ok": True,
        "active": False,
        "state": "free",
        "plan": "free",
        "label": _level_label(product, "free", "SQX Edge Free"),
        "source": "build_profile",
        "build_channel": channel,
        "features": _features_for_level(product, "free"),
        "feature_catalog": _feature_catalog(product),
        "expires_at": None,
        "days_remaining": None,
        "message": "Modo Free. Las funciones Pro requieren licencia.",
        "checked_at": today.isoformat(),
    }


def _license_status(product: dict[str, Any], payload: dict[str, Any], today: date) -> dict[str, Any]:
    plan = str(payload.get("plan") or "free")
    level = "pro" if plan.startswith("pro") else "free"
    expires_at = _parse_date(payload.get("expires_at"))
    grace_days = int(payload.get("grace_days") or product.get("licensing", {}).get("graceDays") or 0)
    signature = str(payload.get("signature") or "").strip()

    if not signature:
        state = "invalid"
        active = False
        message = "Licencia cargada sin firma verificable."
    elif expires_at and today > expires_at + timedelta(days=grace_days):
        state = "expired"
        active = False
        message = "Licencia expirada. Tus datos siguen disponibles en modo Free."
    elif level == "pro":
        state = "pro_pending"
        active = False
        message = "Licencia Pro cargada. Falta implementar verificacion criptografica en una fase posterior."
    else:
        state = "free"
        active = False
        message = "Licencia Free cargada."

    remaining = (expires_at - today).days if expires_at else None
    return {
        "ok": state not in {"invalid"},
        "active": active,
        "state": state,
        "plan": plan,
        "label": _level_label(product, level, "SQX Edge Free"),
        "source": "license_file",
        "build_channel": product.get("build", {}).get("channel", "free"),
        "features": _features_for_level(product, level if active else "free"),
        "feature_catalog": _feature_catalog(product),
        "expires_at": expires_at.isoformat() if expires_at else None,
        "days_remaining": remaining,
        "license_id": payload.get("license_id"),
        "customer": payload.get("customer_name"),
        "message": message,
        "checked_at": today.isoformat(),
    }


def license_status(today: date | None = None) -> dict[str, Any]:
    current = today or date.today()
    product = load_product_manifest()
    build = product.get("build", {})
    if build.get("channel") == "internal":
        return _build_status(product, current)
    payload = load_license_payload(product)
    if payload:
        return _license_status(product, payload, current)
    return _build_status(product, current)


def has_feature(status: dict[str, Any], feature: str) -> bool:
    features = status.get("features") or []
    return "*" in features or feature in features


def check_feature(feature: str, today: date | None = None) -> dict[str, Any]:
    status = license_status(today=today)
    allowed = has_feature(status, feature)
    if allowed:
        return {
            "ok": True,
            "allowed": True,
            "required_feature": feature,
            "license": status,
        }
    product = load_product_manifest()
    response = dict(product.get("lockedResponses", {}).get("proRequired") or {})
    response.update({
        "ok": False,
        "allowed": False,
        "required_feature": feature,
        "license_state": status.get("state"),
        "license_plan": status.get("plan"),
    })
    return response
