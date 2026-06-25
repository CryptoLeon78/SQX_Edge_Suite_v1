from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


from core.app_paths import app_root, user_data_dir

ROOT = app_root()
CONFIG_DIR = ROOT / "config"
PRODUCT_MANIFEST_PATH = CONFIG_DIR / "product_manifest.json"
_USER_DATA = user_data_dir()
DIGESTINFO_SHA256_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")


def load_product_manifest() -> dict[str, Any]:
    return json.loads(PRODUCT_MANIFEST_PATH.read_text(encoding="utf-8-sig"))


def b64url_decode(value: str) -> bytes:
    padded = value + ("=" * (-len(value) % 4))
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def canonical_license_payload(payload: dict[str, Any]) -> bytes:
    unsigned = {key: value for key, value in payload.items() if key != "signature"}
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _license_path(product: dict[str, Any]) -> Path:
    configured = product.get("licensing", {}).get("licenseFile", "config/license.json")
    path = Path(configured)
    if not path.is_absolute():
        path = _USER_DATA / path
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


def _write_license_payload(product: dict[str, Any], payload: dict[str, Any]) -> Path:
    path = _license_path(product)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _clear_license_payload(product: dict[str, Any]) -> bool:
    path = _license_path(product)
    if not path.is_file():
        return False
    path.unlink()
    return True


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


def _rsa_public_key(product: dict[str, Any]) -> dict[str, Any]:
    return dict(product.get("licensing", {}).get("publicKey") or {})


def _rsa_sha256_pkcs1_verify(product: dict[str, Any], payload: dict[str, Any]) -> bool:
    key = _rsa_public_key(product)
    signature = str(payload.get("signature") or "")
    if not signature or key.get("kty") != "RSA":
        return False
    if str(payload.get("signature_algorithm") or key.get("alg") or "") != "RS256":
        return False
    if payload.get("public_key_id") and payload.get("public_key_id") != key.get("kid"):
        return False

    try:
        n = int.from_bytes(b64url_decode(str(key["n"])), "big")
        e = int.from_bytes(b64url_decode(str(key["e"])), "big")
        sig = int.from_bytes(b64url_decode(signature), "big")
    except (KeyError, ValueError, TypeError):
        return False

    key_len = (n.bit_length() + 7) // 8
    digest = hashlib.sha256(canonical_license_payload(payload)).digest()
    digest_info = DIGESTINFO_SHA256_PREFIX + digest
    padding_len = key_len - len(digest_info) - 3
    if padding_len < 8:
        return False
    expected = b"\x00\x01" + (b"\xff" * padding_len) + b"\x00" + digest_info
    try:
        recovered = pow(sig, e, n).to_bytes(key_len, "big")
    except ValueError:
        return False
    return hmac.compare_digest(recovered, expected)


def verify_license_signature(product: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    licensing = product.get("licensing", {})
    expected_version = int(product.get("product", {}).get("licenseVersion") or 1)
    schema_version = int(payload.get("schema_version") or 0)
    if schema_version != expected_version:
        return {"ok": False, "error": "license_schema_mismatch", "signature_valid": False}
    if not payload.get("license_id"):
        return {"ok": False, "error": "missing_license_id", "signature_valid": False}
    if not payload.get("plan"):
        return {"ok": False, "error": "missing_plan", "signature_valid": False}
    mode = str(licensing.get("signatureMode") or "")
    if mode != "rsa_sha256_pkcs1_v1_5":
        return {"ok": False, "error": "unsupported_signature_mode", "signature_valid": False}
    if not _rsa_sha256_pkcs1_verify(product, payload):
        return {"ok": False, "error": "invalid_signature", "signature_valid": False}
    return {"ok": True, "error": "", "signature_valid": True}


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
    signature_result = verify_license_signature(product, payload)

    if not signature_result["signature_valid"]:
        state = "invalid"
        active = False
        message = "Licencia cargada sin firma verificable."
    elif expires_at and today > expires_at + timedelta(days=grace_days):
        state = "expired"
        active = False
        message = "Licencia expirada. Tus datos siguen disponibles en modo Free."
    elif level == "pro":
        state = "pro_active"
        active = True
        message = "Licencia Pro activa y verificada offline."
    else:
        state = "free"
        active = False
        message = "Licencia Free verificada."

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
        "public_key_id": payload.get("public_key_id"),
        "signature_valid": bool(signature_result["signature_valid"]),
        "signature_error": signature_result.get("error") or None,
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


def preview_license_payload(payload: dict[str, Any], today: date | None = None) -> dict[str, Any]:
    return _license_status(load_product_manifest(), payload, today or date.today())


def import_license_payload(payload: dict[str, Any], today: date | None = None) -> dict[str, Any]:
    product = load_product_manifest()
    status = _license_status(product, payload, today or date.today())
    if not status.get("signature_valid"):
        return {
            "ok": False,
            "installed": False,
            "error": status.get("signature_error") or "invalid_signature",
            "status": status,
        }
    path = _write_license_payload(product, payload)
    current = license_status(today=today)
    return {
        "ok": True,
        "installed": True,
        "license_file": str(product.get("licensing", {}).get("licenseFile", "config/license.json")),
        "status": current,
        "import_status": status,
    }


def clear_license_file(today: date | None = None) -> dict[str, Any]:
    product = load_product_manifest()
    removed = _clear_license_payload(product)
    return {
        "ok": True,
        "removed": removed,
        "status": license_status(today=today),
    }


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
