from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
API_BASE = "https://api.render.com/v1"
DEFAULT_BLUEPRINT = ROOT / "deploy" / "render.staging.yaml.example"


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def api_request(
    path: str,
    api_key: str,
    method: str = "GET",
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    request = urlrequest.Request(
        API_BASE + path,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            **(headers or {}),
        },
    )
    try:
        with urlrequest.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            payload = json.loads(text) if text.strip() else {}
            return {"ok": 200 <= response.status < 300, "status": response.status, "payload": payload}
    except urlerror.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        payload = json.loads(text) if text.strip().startswith("{") else {"error": text}
        return {"ok": False, "status": exc.code, "payload": payload}
    except (urlerror.URLError, TimeoutError) as exc:
        return {"ok": False, "status": 0, "payload": {"error": str(exc)}}


def encode_multipart(owner_id: str, blueprint_path: Path) -> tuple[bytes, str]:
    boundary = "----sqx-render-boundary-" + uuid.uuid4().hex
    file_bytes = blueprint_path.read_bytes()
    chunks = [
        f"--{boundary}\r\n".encode("utf-8"),
        b'Content-Disposition: form-data; name="ownerId"\r\n\r\n',
        owner_id.encode("utf-8"),
        b"\r\n",
        f"--{boundary}\r\n".encode("utf-8"),
        f'Content-Disposition: form-data; name="file"; filename="{blueprint_path.name}"\r\n'.encode("utf-8"),
        b"Content-Type: application/x-yaml\r\n\r\n",
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8"),
    ]
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def list_services(api_key: str) -> dict[str, Any]:
    return api_request("/services", api_key)


def validate_blueprint(api_key: str, owner_id: str, blueprint_path: Path) -> dict[str, Any]:
    body, content_type = encode_multipart(owner_id, blueprint_path)
    return api_request(
        "/blueprints/validate",
        api_key,
        method="POST",
        body=body,
        headers={"Content-Type": content_type},
    )


def run_preflight(api_key: str, owner_id: str, blueprint_path: Path) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if not blueprint_path.is_file():
        blockers.append("blueprint_file_missing")
    if not api_key:
        blockers.append("render_api_key_missing")
    if not owner_id:
        blockers.append("render_owner_id_missing")

    services = None
    blueprint = None
    if api_key:
        services = list_services(api_key)
        if not services.get("ok"):
            blockers.append("render_api_auth_or_services_failed")
    if api_key and owner_id and blueprint_path.is_file():
        blueprint = validate_blueprint(api_key, owner_id, blueprint_path)
        if not blueprint.get("ok"):
            blockers.append("render_blueprint_validation_request_failed")
        elif blueprint.get("payload", {}).get("valid") is False:
            blockers.append("render_blueprint_invalid")
    else:
        warnings.append("blueprint_validation_not_run")

    return {
        "ok": not blockers,
        "blockers": blockers,
        "warnings": warnings,
        "blueprint_path": str(blueprint_path),
        "api_key_configured": bool(api_key),
        "owner_id_configured": bool(owner_id),
        "services": services,
        "blueprint_validation": blueprint,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge Render API staging preflight")
    parser.add_argument("--api-key", default=env_value("RENDER_API_KEY"))
    parser.add_argument("--owner-id", default=env_value("RENDER_OWNER_ID"))
    parser.add_argument("--blueprint", default=env_value("SQX_RENDER_STAGING_BLUEPRINT", str(DEFAULT_BLUEPRINT)))
    args = parser.parse_args()
    report = run_preflight(args.api_key, args.owner_id, Path(args.blueprint))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
