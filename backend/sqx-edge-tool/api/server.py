"""
api/server.py — REST API local para SQX Edge Tool.

Lanza Flask en localhost:5050 con CORS restringido a uso local.
El dashboard SQX Edge consume estos endpoints desde el navegador.

Endpoints:
  GET  /api/health            -> {ok: true, version, paths, templates, output}
  GET  /api/config            -> config.json actual
  POST /api/config            -> actualiza config.json (path SQX, output_dir, etc.)
  GET  /api/minings           -> lista de los 14 minings del plan
  GET  /api/templates         -> lista de .cfx en templates/
  POST /api/generate          -> body: {mining: int, capa: 1|2, output?: str} -> genera 1 .cfx
  POST /api/generate-custom   -> body: {asset, tf, dir, capa, name?, bs?} -> genera 1 .cfx fuera del plan
  POST /api/generate-all      -> body: {capa: 1|2} -> genera los 14
  GET  /api/output            -> lista de .cfx en output_dir
  POST /api/open-folder       -> body: {path} -> abre carpeta en Explorer
"""
from __future__ import annotations

import json
import os
import re
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Permitir ejecución directa o vía -m
ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ROOT.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, abort, jsonify, make_response, request, send_from_directory  # type: ignore

from core import Mining, all_minings, generate_project, get_mining, normalize_direction
from core.config_loader import load_manifest
from core.license_manager import (
    check_feature,
    clear_license_file,
    import_license_payload,
    license_status,
    load_product_manifest,
)
from core.project_generator import DEFAULT_BROKER_POSTFIX, resolve_costs
from core.blocksettings import (
    blocksetting_trace,
    load_blocksettings_manifest,
    resolve_blocksetting_entry,
)
from core.sqx_db import SqxDb
from core.strategy_cleaner import (
    extract_metadata, list_sqx_directory, clean_exit_after_bars,
    institutional_name, rename_sqx, process_files,
)
from core.mtf_evidence import build_mtf_evidence
from core.remote_access import (
    SESSION_COOKIE_NAME,
    email_hash,
    evaluate_remote_request,
    evaluate_remote_session,
    start_remote_session_from_headers,
    trusted_email_from_headers,
)
from core.remote_access_control import (
    ACCESS_CONTROL_COOKIE_NAME,
    REMOTE_ACCESS_CONTROL_VERSION,
    build_access_context,
    ensure_device_id,
    evaluate_access_context,
    record_session_started,
    summarize_access_control,
)
from core.remote_payments import process_payment_webhook
from core.remote_security import (
    REMOTE_SECURITY_VERSION,
    check_remote_rate_limit,
    is_kill_switch_active,
    load_remote_security_policy,
    public_security_status,
)
from core.remote_workspaces import (
    append_workspace_audit_event,
    derive_remote_workspace,
    public_workspace_context,
    read_recent_workspace_audit_events,
)
from core.remote_workspace_outputs import (
    list_workspace_outputs,
    output_response_fields,
    record_workspace_output_generated,
    workspace_outputs_dir,
)
from core.remote_template_maker_state import (
    REMOTE_TEMPLATE_MAKER_STATE_VERSION,
    read_template_maker_state,
    template_maker_state_public_status,
    write_template_maker_state,
)
from core.remote_workspace_state import (
    REMOTE_WORKSPACE_STATE_VERSION,
    read_workspace_state,
    workspace_state_public_status,
    write_workspace_state,
)
from core.support_diagnostics import build_support_diagnostics
from core.support_incidents import (
    append_support_incident,
    build_support_incident,
    support_incident_public_response,
    validate_support_incident,
)
from core.fulfillment_queue import (
    load_request as load_fulfillment_request,
    process_request as process_fulfillment_request,
    queue_overview as fulfillment_queue_overview,
    store_relay_bundle,
    store_lemon_webhook,
    update_request_status as set_fulfillment_request_status,
)
from core.customer_cockpit import cockpit_overview as customer_cockpit_overview

app = Flask(__name__)

VERSION = "0.2.0"
CONFIG_PATH = ROOT / "config.json"
DASHBOARD_ROOT = PROJECT_ROOT / "app"
STATE_BACKUP_DIR = PROJECT_ROOT / "analysis" / "analysis_output"
STATE_BACKUP_RETENTION = int(os.environ.get("SQX_STATE_BACKUP_RETENTION", "30"))
REMOTE_STATE_BACKUP_VERSION = "remote-state-backup-v1"
REMOTE_STATE_BACKUP_DIRNAME = "state_backups"
STATE_BACKUP_ALLOWED_KEYS = frozenset({
    "sqx_priority_progress_v1",
    "sqx_plan_user_v1",
    "sqx_pipeline_state_v1",
    "sqx_strategies_user_v1",
    "sqx_strategies_deleted_v1",
    "sqx_workflow_checklist_v1",
    "sqx_view_creator_presets_v1",
    "sqx_pg_custom_presets_v1",
    "sqx_home_trace_v1",
    "sqx_pg_api_base_v1",
})
API_PROFILE = (load_manifest("generator_profiles.json").get("api") or {})
DEFAULT_HOST = API_PROFILE.get("defaultHost", "127.0.0.1")
DEFAULT_PORT = int(API_PROFILE.get("defaultPort", 5050))
LOCAL_CORS_ORIGINS = set(API_PROFILE.get("corsOrigins") or ["null"])
LOCAL_HTTP_ORIGIN_RE = re.compile(API_PROFILE.get("localOriginPattern", r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"))
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
LOCAL_REMOTE_ADDRS = {"127.0.0.1", "::1"}
SAFE_PROJECT_TOKEN_RE = re.compile(r"[^A-Za-z0-9._-]+")
REMOTE_WRITE_PILOT_AUDIT_PATH = PROJECT_ROOT / ".local" / "remote_service" / "remote_write_pilot.local.jsonl"


# ── CORS manual local-only (zero deps) ────────────────────────────
def _request_host_name(value: str) -> str:
    host = (value or "").strip().lower()
    if host.startswith("[") and "]" in host:
        return host[1:host.index("]")]
    return host.split(":", 1)[0]


def _is_local_host(value: str) -> bool:
    host = _request_host_name(value)
    return host in LOCAL_HOSTS or host.startswith("127.")


def _is_local_remote(value: str | None) -> bool:
    remote = (value or "").strip().lower()
    return remote in LOCAL_REMOTE_ADDRS or remote.startswith("127.")


def _is_authenticated_access_tunnel_request() -> bool:
    return _is_local_remote(request.remote_addr) and bool(trusted_email_from_headers(request.headers))


def _is_public_link_preview_path(path: str) -> bool:
    public_brand_assets = {
        "/assets/brand/sqx-social-preview.png",
        "/assets/brand/sqx-favicon.png",
        "/assets/brand/sqx-app-icon-256.png",
        "/favicon.ico",
        "/apple-touch-icon.png",
        "/robots.txt",
    }
    return path in {"/", "/link-preview"} or path in public_brand_assets


def _remote_security_action(method: str, path: str) -> str | None:
    if not path.startswith("/api/remote/"):
        return None
    if path == "/api/remote/session/login" and method == "POST":
        return "remote_session_login"
    if path == "/api/remote/session/logout" and method == "POST":
        return "remote_session_logout"
    if path == "/api/remote/payment/webhook" and method == "POST":
        return "remote_payment_webhook"
    if path.startswith("/api/remote/protected/") and method in {"POST", "PUT", "PATCH", "DELETE"}:
        return "remote_protected_write"
    if path.startswith("/api/remote/template-maker/") and method in {"POST", "PUT", "PATCH", "DELETE"}:
        return "remote_protected_write"
    if path.startswith("/api/state/") and method == "POST" and (
        _is_authenticated_access_tunnel_request() or bool(request.cookies.get(SESSION_COOKIE_NAME))
    ):
        return "remote_protected_write"
    return "remote_status"


def _remote_security_subject() -> str:
    session_status = evaluate_remote_session(request.cookies.get(SESSION_COOKIE_NAME))
    session = session_status.get("session") if isinstance(session_status.get("session"), dict) else {}
    if session.get("email_hash"):
        return str(session["email_hash"])
    trusted_email = trusted_email_from_headers(request.headers)
    if trusted_email:
        return email_hash(trusted_email)
    return "local:" + (request.remote_addr or "unknown")


def _remote_device_id() -> tuple[str, bool]:
    return ensure_device_id(request.cookies)


def _set_remote_device_cookie(response, device_id: str):
    if device_id:
        response.set_cookie(
            ACCESS_CONTROL_COOKIE_NAME,
            device_id,
            httponly=True,
            secure=True,
            samesite="Lax",
            path="/",
            max_age=180 * 24 * 60 * 60,
        )
    return response


def _access_control_context(device_id: str | None = None) -> dict:
    return build_access_context(
        request.headers,
        cookies=request.cookies,
        remote_addr=request.remote_addr,
        device_id=device_id,
    )


def _apply_access_control_to_session_status(session_status: dict, context: dict, *, purpose: str = "status") -> dict:
    session = session_status.get("session") if isinstance(session_status.get("session"), dict) else {}
    identity_hash = str(session.get("email_hash") or "").strip()
    if not identity_hash:
        session_status["accessControl"] = {
            "ok": True,
            "schemaVersion": REMOTE_ACCESS_CONTROL_VERSION,
            "accessControl": {"allowed": False, "reason": "identity_missing", "status": "blocked"},
            "privacy": {"raw_email_returned": False, "raw_ip_returned": False, "device_id_returned": False},
        }
        return session_status
    if session.get("active") and not str(session.get("access_context_ref") or "").strip():
        session_status["accessControl"] = {
            "ok": True,
            "schemaVersion": REMOTE_ACCESS_CONTROL_VERSION,
            "accessControl": {
                "allowed": False,
                "reason": "session_context_missing",
                "status": "blocked",
                "mode": "strict",
                "contextRef": context.get("contextRef"),
            },
            "context": {
                "contextRef": context.get("contextRef"),
                "status": "blocked",
                "deviceHashRef": context.get("deviceHashRef"),
                "ipHashRef": context.get("ipHashRef"),
                "userAgentHashRef": context.get("userAgentHashRef"),
                "country": context.get("country"),
            },
            "privacy": {"raw_email_returned": False, "raw_ip_returned": False, "device_id_returned": False},
        }
        session_status["access"] = {
            "allowed": False,
            "reason": "session_context_missing",
            "feature_scope": "none",
            "features": [],
        }
        session_status["session"] = {**session, "active": False, "reason": "session_context_missing"}
        return session_status
    access_control = evaluate_access_context(
        identity_hash,
        context,
        email_ref=session.get("email_ref"),
        entitlement_kind=session.get("entitlement_kind"),
        session_context_ref=session.get("access_context_ref"),
        purpose=purpose,
    )
    session_status["accessControl"] = access_control
    if not access_control.get("accessControl", {}).get("allowed"):
        session_status["access"] = {
            "allowed": False,
            "reason": access_control.get("accessControl", {}).get("reason") or "access_context_blocked",
            "feature_scope": "none",
            "features": [],
        }
        session_status["session"] = {
            **session,
            "active": False,
            "reason": access_control.get("accessControl", {}).get("reason") or "access_context_blocked",
        }
    return session_status


def _remote_session_status_for_request(*, purpose: str = "status", device_id: str | None = None) -> tuple[dict, str]:
    selected_device_id = device_id or _remote_device_id()[0]
    context = _access_control_context(selected_device_id)
    session_status = evaluate_remote_session(request.cookies.get(SESSION_COOKIE_NAME))
    return _apply_access_control_to_session_status(session_status, context, purpose=purpose), selected_device_id


@app.before_request
def enforce_local_api_boundary():
    local_browser_request = _is_local_host(request.host) and _is_local_remote(request.remote_addr)
    access_tunnel_request = _is_authenticated_access_tunnel_request()
    public_preview_request = _is_public_link_preview_path(request.path) and _is_local_remote(request.remote_addr)
    if public_preview_request:
        return None
    if not local_browser_request and not access_tunnel_request:
        return jsonify({
            "ok": False,
            "error": "local_api_only",
            "message": "SQX Edge API only accepts local browser requests.",
        }), 403


@app.before_request
def enforce_remote_security_controls():
    action = _remote_security_action(request.method, request.path)
    if not action:
        return None
    policy = load_remote_security_policy()
    rate = check_remote_rate_limit(_remote_security_subject(), action, policy=policy)
    if not rate.get("allowed"):
        response = jsonify({
            "ok": False,
            "version": REMOTE_SECURITY_VERSION,
            "error": "remote_rate_limited",
            "rateLimit": rate,
            "privacy": {"subject_returned": False, "local_paths_returned": False},
        })
        response.status_code = 429
        response.headers["Retry-After"] = str(rate.get("retryAfterSeconds") or 0)
        return response
    if is_kill_switch_active(policy) and action in {"remote_session_login", "remote_protected_write"}:
        return jsonify({
            "ok": False,
            "version": REMOTE_SECURITY_VERSION,
            "error": "remote_kill_switch_active",
            "killSwitch": policy.get("killSwitch"),
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), 503
    return None


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin in LOCAL_CORS_ORIGINS or (origin and LOCAL_HTTP_ORIGIN_RE.match(origin)):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Vary"] = "Origin"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["X-Content-Type-Options"] = "nosniff"
    if _is_public_link_preview_path(request.path):
        response.headers["Cache-Control"] = "public, max-age=3600, s-maxage=3600"
        response.headers["X-Robots-Tag"] = "index, follow"
    else:
        response.headers["Cache-Control"] = "no-store"
    if request.path.startswith("/api/remote/"):
        response.headers["X-SQX-Remote-Security-Version"] = REMOTE_SECURITY_VERSION
    return response


# Flask responde OPTIONS automáticamente para rutas con GET/POST registrados,
# combinado con el @app.after_request de arriba, eso es suficiente para CORS preflight.

LINK_PREVIEW_TITLE = "SQX Edge Suite | Plataforma Pro para SQX Traders"
LINK_PREVIEW_DESCRIPTION = (
    "Productividad, estructura y trazabilidad para investigar, certificar y "
    "entregar estrategias SQX con menos errores operativos."
)
LINK_PREVIEW_IMAGE_PATH = "/assets/brand/sqx-social-preview.png"


def _public_base_url() -> str:
    scheme = request.headers.get("X-Forwarded-Proto")
    if not scheme:
        try:
            cf_visitor = json.loads(request.headers.get("Cf-Visitor") or "{}")
            scheme = cf_visitor.get("scheme")
        except Exception:
            scheme = None
    scheme = scheme if scheme in {"http", "https"} else request.scheme
    host = request.headers.get("Host") or "127.0.0.1:5050"
    if not re.match(r"^[A-Za-z0-9.\-:\[\]]+$", host):
        host = "127.0.0.1:5050"
    return f"{scheme}://{host}".rstrip("/")


def _absolute_public_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{_public_base_url()}/{path.lstrip('/')}"


def _with_absolute_link_preview_meta(html: str, canonical_path: str = "/") -> str:
    image_url = _absolute_public_url(LINK_PREVIEW_IMAGE_PATH)
    canonical_url = _absolute_public_url(canonical_path)
    return (
        html.replace('content="assets/brand/sqx-social-preview.png"', f'content="{image_url}"')
        .replace('href="/"', f'href="{canonical_url}"')
        .replace('content="/"', f'content="{canonical_url}"')
    )


def _link_preview_html() -> str:
    image_url = _absolute_public_url(LINK_PREVIEW_IMAGE_PATH)
    canonical_url = _absolute_public_url("/")
    dashboard_url = _absolute_public_url("/dashboard")
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{LINK_PREVIEW_TITLE}</title>
<meta name="description" content="{LINK_PREVIEW_DESCRIPTION}">
<link rel="canonical" href="{canonical_url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="SQX Edge Suite">
<meta property="og:locale" content="es_ES">
<meta property="og:title" content="{LINK_PREVIEW_TITLE}">
<meta property="og:description" content="{LINK_PREVIEW_DESCRIPTION}">
<meta property="og:url" content="{canonical_url}">
<meta property="og:image" content="{image_url}">
<meta property="og:image:secure_url" content="{image_url}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="SQX Edge Suite, plataforma Pro para flujo SQX trazable.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{LINK_PREVIEW_TITLE}">
<meta name="twitter:description" content="{LINK_PREVIEW_DESCRIPTION}">
<meta name="twitter:image" content="{image_url}">
<meta name="twitter:image:alt" content="SQX Edge Suite, plataforma Pro para flujo SQX trazable.">
<style>
body{{margin:0;background:#07111f;color:#f8fbff;font-family:Segoe UI,Arial,sans-serif;}}
main{{min-height:100vh;display:grid;place-items:center;padding:32px;}}
.card{{max-width:920px;border:1px solid #24405f;border-radius:18px;background:#101d2d;padding:32px;box-shadow:0 24px 80px rgba(0,0,0,.32);}}
img{{width:100%;border-radius:14px;border:1px solid #2d4a6b;display:block;margin-bottom:24px;}}
.eyebrow{{color:#62a8ff;text-transform:uppercase;font-weight:800;letter-spacing:.08em;font-size:12px;}}
h1{{font-size:42px;margin:10px 0 12px;}}
p{{color:#bdd0e6;font-size:17px;line-height:1.55;}}
a{{display:inline-flex;margin-top:14px;padding:13px 18px;border-radius:10px;background:#2b65f6;color:#fff;text-decoration:none;font-weight:800;}}
small{{display:block;margin-top:18px;color:#8da2ba;}}
</style>
</head>
<body>
<main>
  <section class="card">
    <span class="eyebrow">Acceso web Pro protegido</span>
    <h1>SQX Edge Suite</h1>
    <p>{LINK_PREVIEW_DESCRIPTION}</p>
    <img src="{image_url}" alt="SQX Edge Suite">
    <a href="{dashboard_url}">Acceso DASHBOARD</a>
    <small>No promete rentabilidad ni sustituye la responsabilidad del usuario al validar estrategias.</small>
  </section>
</main>
</body>
</html>"""


@app.get("/")
def serve_public_link_preview_entry():
    response = make_response(_link_preview_html())
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


@app.get("/dashboard")
def serve_dashboard_entry():
    html = (DASHBOARD_ROOT / "SQX_Dashboard_v6.html").read_text(encoding="utf-8-sig")
    response = make_response(_with_absolute_link_preview_meta(html, "/dashboard"))
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


@app.get("/link-preview")
def serve_link_preview():
    response = make_response(_link_preview_html())
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


@app.get("/robots.txt")
def serve_public_robots():
    response = make_response(
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /dashboard\n"
        "Disallow: /api/\n"
        "Disallow: /js/\n"
        "Disallow: /css/\n"
        "Disallow: /vendor/\n"
    )
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    return response


@app.get("/favicon.ico")
def serve_public_favicon():
    return send_from_directory(DASHBOARD_ROOT / "assets" / "brand", "sqx-favicon.png", mimetype="image/png")


@app.get("/apple-touch-icon.png")
def serve_public_touch_icon():
    return send_from_directory(DASHBOARD_ROOT / "assets" / "brand", "sqx-app-icon-256.png", mimetype="image/png")


@app.get("/<path:asset_path>")
def serve_dashboard_asset(asset_path: str):
    first_segment = asset_path.split("/", 1)[0]
    if first_segment not in {"assets", "css", "js", "vendor"}:
        abort(404)
    if ".." in Path(asset_path).parts:
        abort(404)
    return send_from_directory(DASHBOARD_ROOT, asset_path)


# ── Config helpers ────────────────────────────────────────────────
def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_config(cfg: dict) -> None:
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def resolve_template(cfg: dict, capa: int) -> str:
    key = f"template_capa{capa}"
    val = cfg.get(key) or ("templates/Capa1_Long.cfx" if capa == 1 else "templates/Capa2_Base.cfx")
    if not os.path.isabs(val):
        val = str(ROOT / val)
    return val


def looks_like_cfx_template_path(value: str) -> bool:
    raw = str(value or "").strip()
    if not raw:
        return False
    if raw.lower().endswith(".cfx"):
        return True
    if "/" in raw or "\\" in raw:
        return True
    return bool(re.match(r"^[A-Za-z]:", raw))


def resolve_request_template(data: dict, cfg: dict, capa: int) -> str:
    raw = str((data or {}).get("template") or "").strip()
    if not raw or not looks_like_cfx_template_path(raw):
        return resolve_template(cfg, capa)

    template_path = Path(raw)
    if template_path.is_absolute():
        return str(template_path)

    root_candidate = ROOT / template_path
    templates_candidate = ROOT / "templates" / template_path
    if root_candidate.is_file() or template_path.parent != Path("."):
        return str(root_candidate)
    return str(templates_candidate)


def resolve_output_dir(cfg: dict) -> str:
    val = cfg.get("output_dir") or "output"
    if not os.path.isabs(val):
        val = str(ROOT / val)
    os.makedirs(val, exist_ok=True)
    return val


def _active_remote_workspace_for_request(*, purpose: str, create: bool = True) -> tuple[dict | None, tuple | None]:
    """Return the active remote workspace, or a Flask error tuple when remote access lacks app session."""
    session_status, _device_id = _remote_session_status_for_request(purpose=purpose)
    session = session_status.get("session") if isinstance(session_status.get("session"), dict) else {}
    access = session_status.get("access") if isinstance(session_status.get("access"), dict) else {}
    active = bool(session.get("active") and access.get("allowed"))
    if active:
        workspace_context = derive_remote_workspace(session_status, create=create)
        if workspace_context.get("ok"):
            return workspace_context, None
        return None, (jsonify({
            "ok": False,
            "error": workspace_context.get("error") or "remote_workspace_unavailable",
            "workspace": public_workspace_context(workspace_context) if workspace_context.get("workspace") else None,
            "privacy": {"local_paths_returned": False},
        }), int(workspace_context.get("http_status") or 403))
    if _is_authenticated_access_tunnel_request():
        return None, (jsonify({
            "ok": False,
            "error": "remote_session_required",
            "message": "Create a valid SQX Edge Suite app session before using Project Generator remotely.",
            "privacy": {"local_paths_returned": False, "session_token_returned": False},
        }), 403)
    return None, None


def _resolve_generation_output(data: dict, cfg: dict, *, purpose: str) -> tuple[str | None, dict | None, tuple | None]:
    workspace_context, remote_error = _active_remote_workspace_for_request(purpose=purpose, create=True)
    if remote_error:
        return None, None, remote_error
    if workspace_context:
        if data.get("output"):
            return None, workspace_context, (jsonify({
                "ok": False,
                "error": "remote_output_override_blocked",
                "message": "Remote Project Generator always writes to the active user workspace outputs.",
                "output": {
                    "scope": "remote_workspace",
                    "output_dir": "workspace://outputs",
                    "workspace": public_workspace_context(workspace_context),
                },
                "privacy": {"local_paths_returned": False},
            }), 403)
        return str(workspace_outputs_dir(workspace_context)), workspace_context, None
    return data.get("output") or resolve_output_dir(cfg), None, None


def _resolve_path(value: str) -> Path:
    return Path(value).expanduser().resolve(strict=False)


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def allowed_workspace_roots(cfg: dict) -> list[Path]:
    roots = [ROOT, _resolve_path(resolve_output_dir(cfg))]
    for key in ("sqx_projects_dir", "sqx_path"):
        raw = cfg.get(key)
        if not raw:
            continue
        base = _resolve_path(raw)
        if key == "sqx_path":
            roots.extend([base / "user", base / "user" / "projects"])
        else:
            roots.append(base)
    deduped: list[Path] = []
    for root in roots:
        resolved = root.resolve(strict=False)
        if resolved not in deduped:
            deduped.append(resolved)
    return deduped


def is_allowed_workspace_path(value: str, cfg: dict) -> bool:
    if not value:
        return False
    path = _resolve_path(value)
    return any(path == root or _is_within(path, root) for root in allowed_workspace_roots(cfg))


def require_feature(feature: str):
    result = check_feature(feature)
    if result.get("allowed"):
        return None
    return jsonify(result), 402


def safe_project_token(value: str | None, fallback: str) -> str:
    cleaned = SAFE_PROJECT_TOKEN_RE.sub("_", (value or "").strip())
    cleaned = cleaned.strip("._-")
    return cleaned or fallback


def parse_generation_capa(raw) -> int:
    try:
        capa = int(raw or 1)
    except (TypeError, ValueError):
        raise ValueError("capa must be 1 or 2")
    if capa not in (1, 2):
        raise ValueError("capa must be 1 or 2")
    return capa


def build_custom_mining(data: dict) -> tuple[Mining, str]:
    asset = safe_project_token(str(data.get("asset", "")).upper(), "")
    tf = safe_project_token(str(data.get("tf", "")).upper(), "")
    if not asset:
        raise ValueError("missing 'asset'")
    if not tf:
        raise ValueError("missing 'tf'")
    blocksetting = safe_project_token(str(data.get("bs") or data.get("blocksetting") or "BS_Custom"), "BS_Custom")
    direction = normalize_direction(str(data.get("dir") or data.get("direction") or "long"))
    mining = Mining(num=0, phase=0, asset=asset, tf=tf, bs=blocksetting, dir=direction)
    direction_tag = {"long": "L", "short": "S", "both": "LS"}[direction]
    try:
        capa = parse_generation_capa(data.get("capa", 1))
        bs_entry = resolve_blocksetting_entry(
            blocksetting,
            timeframe=tf,
            capa=capa,
            blocksetting_capa2=data.get("blocksetting_capa2") or data.get("capa2_blocksetting"),
        )
        resolved_blocksetting = str(bs_entry.get("canonicalId") or blocksetting)
    except Exception:
        resolved_blocksetting = blocksetting
    default_name = f"Custom_{asset}_{tf}_{resolved_blocksetting}_{direction_tag}"
    project_name = safe_project_token(str(data.get("name") or data.get("project_name") or default_name), default_name)
    return mining, project_name


# ── Endpoints ─────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    cfg = load_config()
    db_path = cfg.get("sqx_data_db", "")
    output_dir = Path(resolve_output_dir(cfg))
    current_license = license_status()
    return jsonify({
        "ok": True,
        "version": VERSION,
        "license": {
            "state": current_license.get("state"),
            "plan": current_license.get("plan"),
            "active": current_license.get("active"),
            "build_channel": current_license.get("build_channel"),
        },
        "config_exists": CONFIG_PATH.is_file(),
        "sqx_path_set": bool(cfg.get("sqx_path")),
        "sqx_path": cfg.get("sqx_path", ""),
        "data_db_set": bool(db_path),
        "data_db_exists": bool(db_path) and os.path.isfile(db_path),
        "output_dir": str(output_dir),
        "output_dir_exists": output_dir.is_dir(),
        "templates_capa1_exists": os.path.isfile(resolve_template(cfg, 1)),
        "templates_capa2_exists": os.path.isfile(resolve_template(cfg, 2)),
    })


@app.get("/api/symbol-info/<asset>")
def symbol_info(asset: str):
    cfg = load_config()
    db_path = cfg.get("sqx_data_db", "")
    if not db_path or not os.path.isfile(db_path):
        return jsonify({"ok": False, "error": "data.db not configured or missing", "asset": asset}), 404
    try:
        db = SqxDb(db_path)
        try:
            info = db.get_symbol_info(asset, alias_override=cfg.get("asset_aliases"))
            return jsonify({"ok": True, "info": info})
        finally:
            db.close()
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.get("/api/suggest-instruments/<asset>")
def suggest_instruments(asset: str):
    cfg = load_config()
    db_path = cfg.get("sqx_data_db", "")
    if not db_path or not os.path.isfile(db_path):
        return jsonify({"ok": False, "error": "data.db not configured", "suggestions": []}), 404
    try:
        db = SqxDb(db_path)
        try:
            suggestions = db.suggest_instruments(asset)
            current = (cfg.get("asset_aliases") or {}).get(asset, "")
            return jsonify({"ok": True, "asset": asset, "current_alias": current, "suggestions": suggestions[:15]})
        finally:
            db.close()
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.get("/api/autodetect-sqx")
def autodetect_sqx():
    """
    Busca instalaciones de StrategyQuant X en ubicaciones típicas.
    Devuelve lista de paths candidatos donde se encontró user/data/data.db.
    """
    candidates = []
    home = Path.home()
    profile = load_manifest("generator_profiles.json").get("autodetect") or {}
    search_roots = []
    for raw in profile.get("roots") or []:
        raw_path = str(raw).replace("~", str(home), 1)
        search_roots.append(Path(raw_path))
    # Custom version folders
    for letter in profile.get("driveLetters") or []:
        for v in profile.get("versionFolders") or []:
            p = Path(f"{letter}:/{v}")
            if p.exists():
                # buscar subcarpetas con SQX
                for sub in p.rglob("StrategyQuantX*.exe"):
                    search_roots.append(sub.parent)
    # Dedupe + buscar data.db
    seen = set()
    for root in search_roots:
        if not root.exists() or str(root).lower() in seen:
            continue
        seen.add(str(root).lower())
        db = root / "user" / "data" / "data.db"
        if db.is_file():
            sqx_exe = root / "StrategyQuantX.exe"
            candidates.append({
                "sqx_path": str(root).replace("\\", "/"),
                "data_db": str(db).replace("\\", "/"),
                "projects_dir": str(root / "user" / "projects").replace("\\", "/"),
                "version": "142" if "142" in str(root) else ("141" if "141" in str(root) else "?"),
                "has_exe": sqx_exe.is_file(),
            })
    return jsonify({"ok": True, "found": len(candidates), "candidates": candidates})


@app.post("/api/validate-sqx-path")
def validate_sqx_path():
    """Verifica que un path SQX dado es válido (tiene data.db y projects/)."""
    data = request.get_json(silent=True) or {}
    path = (data.get("path") or "").strip().rstrip("/\\")
    if not path:
        return jsonify({"ok": False, "error": "missing path"}), 400
    base = Path(path)
    db = base / "user" / "data" / "data.db"
    proj = base / "user" / "projects"
    exe = base / "StrategyQuantX.exe"
    return jsonify({
        "ok": True,
        "valid": db.is_file(),
        "checks": {
            "base_exists": base.is_dir(),
            "data_db_exists": db.is_file(),
            "projects_exists": proj.is_dir(),
            "exe_exists": exe.is_file(),
        },
        "resolved": {
            "sqx_path": str(base).replace("\\", "/") if base.is_dir() else None,
            "data_db": str(db).replace("\\", "/") if db.is_file() else None,
            "projects_dir": str(proj).replace("\\", "/") if proj.is_dir() else None,
        }
    })


@app.get("/api/instruments")
def list_instruments():
    cfg = load_config()
    db_path = cfg.get("sqx_data_db", "")
    if not db_path or not os.path.isfile(db_path):
        return jsonify({"ok": False, "error": "data.db not configured", "instruments": []}), 404
    try:
        db = SqxDb(db_path)
        try:
            instruments = db.list_instruments()
            # Broker info solo está disponible en SQX 142
            try:
                brokers = db.brokers()
            except Exception:
                brokers = []
            return jsonify({"ok": True, "instruments": instruments, "brokers": brokers})
        finally:
            db.close()
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.get("/api/config")
def get_config():
    return jsonify(load_config())


@app.get("/api/manifest")
def manifest():
    return jsonify({
        "ok": True,
        "ui": load_manifest("ui_manifest.json"),
        "product": load_product_manifest(),
        "plan": load_manifest("plan.json"),
        "assets": load_manifest("assets.json"),
        "strategies": load_manifest("strategies.json"),
        "blocksettings": load_manifest("blocksettings_manifest.json"),
    })


@app.get("/api/blocksettings")
def api_blocksettings():
    return jsonify({"ok": True, "blocksettings": load_blocksettings_manifest()})


@app.get("/api/license/status")
def api_license_status():
    return jsonify(license_status())


@app.get("/api/remote/access/status")
def api_remote_access_status():
    """Public-safe remote-service access status derived from trusted edge/app headers."""
    device_id, _created = _remote_device_id()
    status = evaluate_remote_request(request.headers, request.cookies.get(SESSION_COOKIE_NAME))
    identity = status.get("identity") if isinstance(status.get("identity"), dict) else {}
    entitlement = status.get("entitlement") if isinstance(status.get("entitlement"), dict) else {}
    session = status.get("session") if isinstance(status.get("session"), dict) else {}
    identity_hash = str(identity.get("email_hash") or session.get("email_hash") or "").strip()
    if identity_hash:
        context = _access_control_context(device_id)
        access_control = evaluate_access_context(
            identity_hash,
            context,
            email_ref=identity.get("email_ref") or session.get("email_ref"),
            entitlement_kind=entitlement.get("kind") or session.get("entitlement_kind"),
            session_context_ref=session.get("access_context_ref") if session.get("active") else None,
        )
        status["accessControl"] = access_control
        if not access_control.get("accessControl", {}).get("allowed"):
            status["access"] = {
                "allowed": False,
                "reason": access_control.get("accessControl", {}).get("reason") or "access_context_blocked",
                "feature_scope": "none",
                "features": [],
            }
    response = make_response(jsonify(status))
    return _set_remote_device_cookie(response, device_id)


@app.post("/api/remote/session/login")
def api_remote_session_login():
    """Create a signed app session after trusted edge identity and entitlement checks."""
    data = request.get_json(silent=True) or {}
    device_id, _created = _remote_device_id()
    edge_status = evaluate_remote_request(request.headers, request.cookies.get(SESSION_COOKIE_NAME))
    identity = edge_status.get("identity") if isinstance(edge_status.get("identity"), dict) else {}
    entitlement = edge_status.get("entitlement") if isinstance(edge_status.get("entitlement"), dict) else {}
    context = _access_control_context(device_id)
    access_control = evaluate_access_context(
        str(identity.get("email_hash") or ""),
        context,
        email_ref=identity.get("email_ref"),
        entitlement_kind=entitlement.get("kind"),
        purpose="session_login",
    )
    if not access_control.get("accessControl", {}).get("allowed"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_ACCESS_CONTROL_VERSION,
            "error": access_control.get("accessControl", {}).get("reason") or "access_context_blocked",
            "accessControl": access_control,
            "privacy": {"session_token_returned": False, "raw_email_returned": False, "raw_ip_returned": False},
        }), 403)
        return _set_remote_device_cookie(response, device_id)
    result = start_remote_session_from_headers(
        request.headers,
        data,
        access_context_ref=access_control.get("accessControl", {}).get("contextRef"),
    )
    status = int(result.pop("http_status", 200))
    token = result.pop("session_token", None)
    session_id_for_audit = result.pop("_session_id_for_audit", "")
    response = make_response(jsonify(result), status)
    if token and result.get("ok"):
        session = result.get("session") if isinstance(result.get("session"), dict) else {}
        record_session_started(
            str(session.get("email_hash") or ""),
            str(session.get("access_context_ref") or ""),
            str(session_id_for_audit or ""),
        )
        response.set_cookie(
            SESSION_COOKIE_NAME,
            token,
            httponly=True,
            secure=True,
            samesite="Lax",
            path="/",
        )
    return _set_remote_device_cookie(response, device_id)


@app.get("/api/remote/session/status")
def api_remote_session_status():
    """Validate the signed app session cookie without returning the token."""
    session_status, device_id = _remote_session_status_for_request()
    response = make_response(jsonify(session_status))
    return _set_remote_device_cookie(response, device_id)


@app.get("/api/remote/access-control/status")
def api_remote_access_control_status():
    """Report strict anti-sharing context status without returning raw IP/device data."""
    device_id, _created = _remote_device_id()
    edge_status = evaluate_remote_request(request.headers, request.cookies.get(SESSION_COOKIE_NAME))
    identity = edge_status.get("identity") if isinstance(edge_status.get("identity"), dict) else {}
    session = edge_status.get("session") if isinstance(edge_status.get("session"), dict) else {}
    entitlement = edge_status.get("entitlement") if isinstance(edge_status.get("entitlement"), dict) else {}
    context = _access_control_context(device_id)
    access_control = evaluate_access_context(
        str(identity.get("email_hash") or session.get("email_hash") or ""),
        context,
        email_ref=identity.get("email_ref") or session.get("email_ref"),
        entitlement_kind=entitlement.get("kind") or session.get("entitlement_kind"),
        session_context_ref=session.get("access_context_ref") if session.get("active") else None,
    )
    response = make_response(jsonify({
        "ok": True,
        "version": REMOTE_ACCESS_CONTROL_VERSION,
        "accessControl": access_control.get("accessControl"),
        "context": access_control.get("context"),
        "summary": summarize_access_control().get("summary"),
        "privacy": {"raw_email_returned": False, "raw_ip_returned": False, "device_id_returned": False, "store_path_returned": False},
    }))
    return _set_remote_device_cookie(response, device_id)


@app.post("/api/remote/access-control/request-approval")
def api_remote_access_control_request_approval():
    """Create a redacted support case for a blocked/pending access context."""
    data = request.get_json(silent=True) or {}
    device_id, _created = _remote_device_id()
    session_status, _ = _remote_session_status_for_request(device_id=device_id)
    edge_status = evaluate_remote_request(request.headers, request.cookies.get(SESSION_COOKIE_NAME))
    identity = edge_status.get("identity") if isinstance(edge_status.get("identity"), dict) else {}
    session = session_status.get("session") if isinstance(session_status.get("session"), dict) else {}
    entitlement = edge_status.get("entitlement") if isinstance(edge_status.get("entitlement"), dict) else {}
    context = _access_control_context(device_id)
    access_control = evaluate_access_context(
        str(identity.get("email_hash") or session.get("email_hash") or ""),
        context,
        email_ref=identity.get("email_ref") or session.get("email_ref"),
        entitlement_kind=entitlement.get("kind") or session.get("entitlement_kind"),
    )
    workspace_context = derive_remote_workspace(session_status, create=False)
    reason = access_control.get("accessControl", {}).get("reason") or "access_context_review_requested"
    record = build_support_incident(
        {
            "category": "access",
            "severity": str(data.get("severity") or "high"),
            "summary": f"Solicitud de aprobacion de acceso remoto: {reason}",
            "steps": f"Contexto {access_control.get('accessControl', {}).get('contextRef')} pendiente/bloqueado al abrir SQX Edge Suite.",
            "expected": "Aprobar este dispositivo/IP si corresponde al usuario legitimo.",
            "actual": "El control anti-comparticion requiere validacion del operador.",
            "includeDiagnostic": False,
        },
        session_status=session_status,
        workspace_context=workspace_context,
        diagnostic_payload=None,
    )
    blockers = validate_support_incident(record)
    if blockers:
        return jsonify({"ok": False, "error": "support_incident_invalid", "blockers": blockers}), 400
    append_support_incident(record)
    response = make_response(jsonify({
        **support_incident_public_response(record),
        "accessControl": access_control.get("accessControl"),
    }), 201)
    return _set_remote_device_cookie(response, device_id)


@app.get("/api/remote/workspace/status")
def api_remote_workspace_status():
    """Provision and report the server-derived workspace for the active app session."""
    session_status, device_id = _remote_session_status_for_request()
    workspace_context = derive_remote_workspace(session_status, create=True)
    if not workspace_context.get("ok"):
        response = make_response(jsonify({
            "ok": False,
            "error": workspace_context.get("error") or "remote_workspace_unavailable",
            "session": session_status.get("session"),
            "access": session_status.get("access"),
            "accessControl": session_status.get("accessControl"),
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), int(workspace_context.get("http_status") or 403))
        return _set_remote_device_cookie(response, device_id)
    response = make_response(jsonify({
        "ok": True,
        "version": workspace_context.get("version"),
        "workspace": public_workspace_context(workspace_context),
        "access": session_status.get("access"),
        "accessControl": session_status.get("accessControl"),
        "privacy": {"session_token_returned": False, "local_paths_returned": False},
    }))
    return _set_remote_device_cookie(response, device_id)


@app.get("/api/remote/state/bootstrap")
def api_remote_state_bootstrap():
    """Load workspace-scoped dashboard state for the active remote session."""
    session_status, device_id = _remote_session_status_for_request(purpose="remote_state_bootstrap")
    if not session_status.get("access", {}).get("allowed"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_WORKSPACE_STATE_VERSION,
            "error": "remote_session_required",
            "session": session_status.get("session"),
            "access": session_status.get("access"),
            "accessControl": session_status.get("accessControl"),
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), 403)
        return _set_remote_device_cookie(response, device_id)
    workspace_context = derive_remote_workspace(session_status, create=True)
    if not workspace_context.get("ok"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_WORKSPACE_STATE_VERSION,
            "error": workspace_context.get("error") or "remote_workspace_unavailable",
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), int(workspace_context.get("http_status") or 403))
        return _set_remote_device_cookie(response, device_id)
    state = read_workspace_state(workspace_context, audit=True)
    response = make_response(jsonify({
        "ok": True,
        "version": REMOTE_WORKSPACE_STATE_VERSION,
        "workspace": public_workspace_context(workspace_context),
        "state": state,
        "stateKeys": sorted(state.keys()),
        "privacy": {"session_token_returned": False, "local_paths_returned": False, "raw_email_returned": False},
    }))
    return _set_remote_device_cookie(response, device_id)


@app.post("/api/remote/state/save")
def api_remote_state_save():
    """Persist allowed dashboard state keys inside the active remote workspace."""
    session_status, device_id = _remote_session_status_for_request(purpose="remote_state_save")
    if not session_status.get("access", {}).get("allowed"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_WORKSPACE_STATE_VERSION,
            "error": "remote_session_required",
            "session": session_status.get("session"),
            "access": session_status.get("access"),
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), 403)
        return _set_remote_device_cookie(response, device_id)
    workspace_context = derive_remote_workspace(session_status, create=True)
    if not workspace_context.get("ok"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_WORKSPACE_STATE_VERSION,
            "error": workspace_context.get("error") or "remote_workspace_unavailable",
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), int(workspace_context.get("http_status") or 403))
        return _set_remote_device_cookie(response, device_id)
    data = request.get_json(silent=True) or {}
    payload = data.get("state") if isinstance(data.get("state"), dict) else data
    result = write_workspace_state(workspace_context, payload, source=str(data.get("source") or "dashboard"))
    status = 200 if result.get("ok") else 400
    response = make_response(jsonify(result), status)
    return _set_remote_device_cookie(response, device_id)


@app.get("/api/remote/state/status")
def api_remote_state_status():
    """Report public-safe workspace persistence status for the active remote session."""
    session_status, device_id = _remote_session_status_for_request(purpose="remote_state_status")
    if not session_status.get("access", {}).get("allowed"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_WORKSPACE_STATE_VERSION,
            "error": "remote_session_required",
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), 403)
        return _set_remote_device_cookie(response, device_id)
    workspace_context = derive_remote_workspace(session_status, create=True)
    if not workspace_context.get("ok"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_WORKSPACE_STATE_VERSION,
            "error": workspace_context.get("error") or "remote_workspace_unavailable",
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), int(workspace_context.get("http_status") or 403))
        return _set_remote_device_cookie(response, device_id)
    response = make_response(jsonify(workspace_state_public_status(workspace_context)))
    return _set_remote_device_cookie(response, device_id)


@app.get("/api/remote/template-maker/bootstrap")
def api_remote_template_maker_bootstrap():
    """Load workspace-scoped Template Maker snapshot for the active remote session."""
    session_status, device_id = _remote_session_status_for_request(purpose="remote_template_maker_bootstrap")
    if not session_status.get("access", {}).get("allowed"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_TEMPLATE_MAKER_STATE_VERSION,
            "error": "remote_session_required",
            "session": session_status.get("session"),
            "access": session_status.get("access"),
            "accessControl": session_status.get("accessControl"),
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), 403)
        return _set_remote_device_cookie(response, device_id)
    workspace_context = derive_remote_workspace(session_status, create=True)
    if not workspace_context.get("ok"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_TEMPLATE_MAKER_STATE_VERSION,
            "error": workspace_context.get("error") or "remote_workspace_unavailable",
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), int(workspace_context.get("http_status") or 403))
        return _set_remote_device_cookie(response, device_id)
    snapshot = read_template_maker_state(workspace_context, audit=True)
    response = make_response(jsonify({
        "ok": True,
        "version": REMOTE_TEMPLATE_MAKER_STATE_VERSION,
        "workspace": public_workspace_context(workspace_context),
        "state": snapshot,
        "recordCount": len(snapshot.get("strategies") or []),
        "privacy": {"session_token_returned": False, "local_paths_returned": False, "raw_email_returned": False},
    }))
    return _set_remote_device_cookie(response, device_id)


@app.post("/api/remote/template-maker/save")
def api_remote_template_maker_save():
    """Persist Template Maker snapshot inside the active remote workspace."""
    session_status, device_id = _remote_session_status_for_request(purpose="remote_template_maker_save")
    if not session_status.get("access", {}).get("allowed"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_TEMPLATE_MAKER_STATE_VERSION,
            "error": "remote_session_required",
            "session": session_status.get("session"),
            "access": session_status.get("access"),
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), 403)
        return _set_remote_device_cookie(response, device_id)
    workspace_context = derive_remote_workspace(session_status, create=True)
    if not workspace_context.get("ok"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_TEMPLATE_MAKER_STATE_VERSION,
            "error": workspace_context.get("error") or "remote_workspace_unavailable",
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), int(workspace_context.get("http_status") or 403))
        return _set_remote_device_cookie(response, device_id)
    data = request.get_json(silent=True) or {}
    snapshot = data.get("state") if isinstance(data.get("state"), dict) else data
    result = write_template_maker_state(workspace_context, snapshot, source=str(data.get("source") or "dashboard"))
    response = make_response(jsonify(result), 200 if result.get("ok") else 400)
    return _set_remote_device_cookie(response, device_id)


@app.get("/api/remote/template-maker/status")
def api_remote_template_maker_status():
    """Report public-safe Template Maker persistence status for the active remote session."""
    session_status, device_id = _remote_session_status_for_request(purpose="remote_template_maker_status")
    if not session_status.get("access", {}).get("allowed"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_TEMPLATE_MAKER_STATE_VERSION,
            "error": "remote_session_required",
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), 403)
        return _set_remote_device_cookie(response, device_id)
    workspace_context = derive_remote_workspace(session_status, create=True)
    if not workspace_context.get("ok"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_TEMPLATE_MAKER_STATE_VERSION,
            "error": workspace_context.get("error") or "remote_workspace_unavailable",
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), int(workspace_context.get("http_status") or 403))
        return _set_remote_device_cookie(response, device_id)
    response = make_response(jsonify(template_maker_state_public_status(workspace_context)))
    return _set_remote_device_cookie(response, device_id)


@app.get("/api/remote/security/status")
def api_remote_security_status():
    """Public-safe REMOTE-6 security and abuse-control readiness."""
    session_status, device_id = _remote_session_status_for_request()
    workspace_context = derive_remote_workspace(session_status, create=False)
    workspace = public_workspace_context(workspace_context) if workspace_context.get("ok") else {}
    response = make_response(jsonify(public_security_status(
        session_status,
        workspace_id=workspace.get("id"),
    )))
    return _set_remote_device_cookie(response, device_id)


@app.get("/api/remote/security/audit/recent")
def api_remote_security_audit_recent():
    """Return recent redacted workspace audit events for the active remote session."""
    session_status, device_id = _remote_session_status_for_request()
    if not session_status.get("access", {}).get("allowed"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_SECURITY_VERSION,
            "error": "remote_session_required",
            "session": session_status.get("session"),
            "access": session_status.get("access"),
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), 403)
        return _set_remote_device_cookie(response, device_id)
    workspace_context = derive_remote_workspace(session_status, create=True)
    if not workspace_context.get("ok"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_SECURITY_VERSION,
            "error": workspace_context.get("error") or "remote_workspace_unavailable",
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), int(workspace_context.get("http_status") or 403))
        return _set_remote_device_cookie(response, device_id)
    response = make_response(jsonify({
        "ok": True,
        "version": REMOTE_SECURITY_VERSION,
        "workspace": public_workspace_context(workspace_context),
        "events": read_recent_workspace_audit_events(workspace_context, limit=20),
        "privacy": {"raw_email_returned": False, "local_paths_returned": False},
    }))
    return _set_remote_device_cookie(response, device_id)


@app.post("/api/remote/session/logout")
def api_remote_session_logout():
    response = make_response(jsonify({
        "ok": True,
        "session": {"active": False, "reason": "logged_out"},
        "privacy": {"session_token_returned": False},
    }))
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return response


@app.post("/api/remote/payment/webhook")
def api_remote_payment_webhook():
    """Signed REMOTE-3C payment webhook that upserts paid entitlements."""
    signature = (
        request.headers.get("X-SQX-Webhook-Signature")
        or request.headers.get("X-Hub-Signature-256")
        or request.headers.get("X-Signature")
    )
    result = process_payment_webhook(request.get_data(), signature)
    return jsonify(result), int(result.get("http_status") or 200)


def _append_remote_write_pilot_event(payload: dict) -> None:
    REMOTE_WRITE_PILOT_AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REMOTE_WRITE_PILOT_AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


@app.post("/api/remote/protected/write-pilot")
def api_remote_protected_write_pilot():
    """First protected REMOTE-3C write pilot using app-session enforcement."""
    session_status, device_id = _remote_session_status_for_request(purpose="protected_write")
    if not session_status.get("access", {}).get("allowed"):
        response = make_response(jsonify({
            "ok": False,
            "error": "remote_session_required",
            "session": session_status.get("session"),
            "access": session_status.get("access"),
            "privacy": {"session_token_returned": False},
        }), 403)
        return _set_remote_device_cookie(response, device_id)
    workspace_context = derive_remote_workspace(session_status, create=True)
    if not workspace_context.get("ok"):
        response = make_response(jsonify({
            "ok": False,
            "error": workspace_context.get("error") or "remote_workspace_unavailable",
            "session": session_status.get("session"),
            "access": session_status.get("access"),
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), int(workspace_context.get("http_status") or 403))
        return _set_remote_device_cookie(response, device_id)
    data = request.get_json(silent=True) or {}
    action = str(data.get("action") or "remote_write_pilot").strip()[:80]
    event = {
        "type": "remote_write_pilot",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "browserWorkspaceIgnored": bool(data.get("workspace_id") or data.get("workspaceId") or data.get("path")),
        "identityHash": (session_status.get("session") or {}).get("email_hash"),
        "emailRef": (session_status.get("session") or {}).get("email_ref"),
        "entitlementKind": (session_status.get("entitlement") or {}).get("kind"),
        "featureScope": session_status.get("access", {}).get("feature_scope"),
    }
    audit_result = append_workspace_audit_event(workspace_context, event)
    response = make_response(jsonify({
        "ok": True,
        "version": "remote-write-pilot-v1",
        "event": {
            "type": event["type"],
            "action": event["action"],
            "identity_hash": event["identityHash"],
            "email_ref": event["emailRef"],
            "browser_workspace_ignored": event["browserWorkspaceIgnored"],
        },
        "workspace": public_workspace_context(workspace_context),
        "audit": audit_result.get("audit_event"),
        "access": {"allowed": True, "reason": "remote_session_verified"},
        "privacy": {"session_token_returned": False, "raw_email_returned": False, "local_paths_returned": False},
    }))
    return _set_remote_device_cookie(response, device_id)


@app.post("/api/license/check")
def api_license_check():
    data = request.get_json(silent=True) or {}
    feature = (data.get("feature") or "").strip()
    if not feature:
        return jsonify({"ok": False, "error": "missing feature"}), 400
    result = check_feature(feature)
    return jsonify(result), 200 if result.get("allowed") else 402


@app.post("/api/license/import")
def api_license_import():
    data = request.get_json(silent=True) or {}
    payload = data.get("license") if isinstance(data.get("license"), dict) else data
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "license payload must be an object"}), 400
    result = import_license_payload(payload)
    return jsonify(result), 200 if result.get("ok") else 400


@app.post("/api/license/clear")
def api_license_clear():
    return jsonify(clear_license_file())


@app.get("/api/support/diagnostics")
def api_support_diagnostics():
    """Devuelve un diagnostico de soporte sin rutas, licencia ni estrategias."""
    return jsonify(build_support_diagnostics(
        load_config(),
        app_version=VERSION,
        config_exists=CONFIG_PATH.is_file(),
        project_root=PROJECT_ROOT,
    ))


@app.post("/api/support/incidents")
def api_support_incidents():
    """Registra una incidencia local redacted para soporte remoto sin enviarla fuera."""
    data = request.get_json(silent=True) or {}
    session_status, _device_id = _remote_session_status_for_request()
    workspace_context = derive_remote_workspace(session_status, create=False)
    diagnostic_payload = None
    if bool(data.get("includeDiagnostic")):
        diagnostic_payload = build_support_diagnostics(
            load_config(),
            app_version=VERSION,
            config_exists=CONFIG_PATH.is_file(),
            project_root=PROJECT_ROOT,
        )
    record = build_support_incident(
        data,
        session_status=session_status,
        workspace_context=workspace_context,
        diagnostic_payload=diagnostic_payload,
    )
    blockers = validate_support_incident(record)
    if blockers:
        return jsonify({
            "ok": False,
            "error": "support_incident_invalid",
            "blockers": blockers,
            "privacy": {
                "rawEmailReturned": False,
                "protectedUrlReturned": False,
                "localPathsReturned": False,
                "tokensReturned": False,
            },
        }), 400
    append_support_incident(record)
    return jsonify(support_incident_public_response(record)), 201


@app.get("/api/mtf/evidence")
def api_mtf_evidence():
    """Devuelve evidencia A56 MTF resumida, solo lectura y sin rutas completas."""
    return jsonify(build_mtf_evidence())


@app.post("/api/fulfillment/webhook/lemon")
def api_fulfillment_webhook_lemon():
    secret = os.environ.get("SQX_LEMON_WEBHOOK_SECRET", "").strip()
    if not secret:
        return jsonify({
            "ok": False,
            "error": "webhook_secret_missing",
            "message": "Set SQX_LEMON_WEBHOOK_SECRET before enabling the local receiver.",
        }), 503
    signature = request.headers.get("X-Signature", "")
    result = store_lemon_webhook(request.get_data(), signature, secret)
    if not result.get("ok"):
        return jsonify(result), 401
    return jsonify(result)


@app.post("/api/fulfillment/relay-ingest")
def api_fulfillment_relay_ingest():
    secret = os.environ.get("SQX_FULFILLMENT_RELAY_SECRET", "").strip()
    if not secret:
        return jsonify({
            "ok": False,
            "error": "relay_secret_missing",
            "message": "Set SQX_FULFILLMENT_RELAY_SECRET before enabling relay ingest.",
        }), 503
    signature = request.headers.get("X-SQX-Relay-Signature", "")
    result = store_relay_bundle(request.get_data(), signature, secret)
    if not result.get("ok"):
        return jsonify(result), 401
    return jsonify(result)


@app.get("/api/fulfillment/requests")
def api_fulfillment_requests():
    overview = fulfillment_queue_overview()
    return jsonify({
        "ok": True,
        "requests": overview["requests"],
        "processed": overview["processed"],
        "summary": overview["summary"],
        "receiver": {
            "secret_configured": bool(os.environ.get("SQX_LEMON_WEBHOOK_SECRET", "").strip()),
            "relay_secret_configured": bool(os.environ.get("SQX_FULFILLMENT_RELAY_SECRET", "").strip()),
        },
    })


@app.get("/api/fulfillment/requests/<path:filename>")
def api_fulfillment_request_detail(filename: str):
    try:
        payload = load_fulfillment_request(filename)
    except FileNotFoundError:
        return jsonify({"ok": False, "error": "request_not_found"}), 404
    return jsonify({"ok": True, "request": payload})


@app.post("/api/fulfillment/process")
def api_fulfillment_process():
    data = request.get_json(silent=True) or {}
    filename = str(data.get("request_file") or "").strip()
    private_key = str(data.get("private_key") or "").strip()
    zip_path = str(data.get("zip_path") or "").strip()
    support_email = str(data.get("support_email") or "").strip()
    allow_ineligible = bool(data.get("allow_ineligible"))
    if not filename or not private_key or not zip_path:
        return jsonify({"ok": False, "error": "missing request_file/private_key/zip_path"}), 400
    result = process_fulfillment_request(
        filename=filename,
        private_key=private_key,
        zip_path=zip_path,
        support_email=support_email,
        allow_ineligible=allow_ineligible,
    )
    return jsonify(result), 200 if result.get("ok") else 500


@app.post("/api/fulfillment/request-status")
def api_fulfillment_request_status():
    data = request.get_json(silent=True) or {}
    filename = str(data.get("request_file") or "").strip()
    operator_status = str(data.get("operator_status") or "").strip()
    note = str(data.get("note") or "").strip()
    if not filename or not operator_status:
        return jsonify({"ok": False, "error": "missing request_file/operator_status"}), 400
    try:
        result = set_fulfillment_request_status(
            filename=filename,
            operator_status=operator_status,
            note=note,
        )
    except FileNotFoundError:
        return jsonify({"ok": False, "error": "request_not_found"}), 404
    except ValueError as exc:
        return jsonify({"ok": False, "error": "invalid_operator_status", "message": str(exc)}), 400
    return jsonify(result)


@app.get("/api/customer-cockpit")
def api_customer_cockpit():
    """Resumen comercial interno con clientes redactados, renovaciones y soporte."""
    return jsonify(customer_cockpit_overview())


@app.get("/api/plan")
def plan_manifest():
    return jsonify(load_manifest("plan.json"))


@app.post("/api/config")
def update_config():
    data = request.get_json(silent=True) or {}
    cfg = load_config()
    # whitelist de claves editables
    allowed = {"sqx_path", "sqx_data_db", "sqx_projects_dir",
               "template_capa1", "template_capa2", "output_dir", "darwinex_suffix",
               "asset_aliases"}
    changes = {k: v for k, v in data.items() if k in allowed}
    cfg.update(changes)
    save_config(cfg)
    return jsonify({"ok": True, "updated_keys": list(changes.keys()), "config": cfg})


@app.get("/api/minings")
def minings():
    return jsonify([
        {
            "num": m.num, "phase": m.phase, "asset": m.asset, "tf": m.tf,
            "bs": m.bs, "dir": m.dir, "name": m.name,
        }
        for m in all_minings()
    ])


@app.get("/api/templates")
def templates():
    tdir = ROOT / "templates"
    if not tdir.exists():
        return jsonify([])
    items = []
    for f in sorted(tdir.glob("*.cfx")):
        items.append({
            "name": f.name,
            "path": str(f),
            "size_kb": round(f.stat().st_size / 1024, 1),
            "mtime": f.stat().st_mtime,
        })
    return jsonify(items)


@app.get("/api/output")
def list_output():
    cfg = load_config()
    workspace_context, remote_error = _active_remote_workspace_for_request(purpose="project_generator_output_list", create=True)
    if remote_error:
        return remote_error
    if workspace_context:
        return jsonify(list_workspace_outputs(workspace_context, audit=True))
    out_dir = Path(resolve_output_dir(cfg))
    items = []
    for f in sorted(out_dir.glob("*.cfx"), key=lambda p: p.stat().st_mtime, reverse=True):
        items.append({
            "name": f.name,
            "path": str(f),
            "size_kb": round(f.stat().st_size / 1024, 1),
            "mtime": f.stat().st_mtime,
        })
    return jsonify({"output_dir": str(out_dir), "files": items})


@app.post("/api/generate")
def generate_one():
    locked = require_feature("project_generator.generate")
    if locked:
        return locked
    data = request.get_json(silent=True) or {}
    if "mining" not in data:
        return jsonify({"ok": False, "error": "missing 'mining'"}), 400
    capa = int(data.get("capa", 1))
    if capa not in (1, 2):
        return jsonify({"ok": False, "error": "capa must be 1 or 2"}), 400

    cfg = load_config()
    template = resolve_request_template(data, cfg, capa)
    output, workspace_context, remote_error = _resolve_generation_output(data, cfg, purpose="project_generator_generate")
    if remote_error:
        return remote_error
    blocksetting_capa2 = data.get("blocksetting_capa2") or data.get("capa2_blocksetting")

    try:
        mining = get_mining(int(data["mining"]))
    except KeyError as e:
        return jsonify({"ok": False, "error": str(e)}), 404

    if not os.path.isfile(template):
        return jsonify({"ok": False, "error": f"template not found: {template}"}), 404

    db_path = cfg.get("sqx_data_db") or None
    postfix = cfg.get("darwinex_suffix") or DEFAULT_BROKER_POSTFIX
    aliases = cfg.get("asset_aliases") or {}
    try:
        out_path = generate_project(
            mining, template_path=template, output_dir=output, capa=capa,
            sqx_db_path=db_path, broker_postfix=postfix, alias_override=aliases,
            blocksetting_capa2=blocksetting_capa2,
        )
        # Mostrar al cliente qué fuente de costos se usó
        costs = resolve_costs(mining, db_path, postfix, alias_override=aliases)
        bs_entry = resolve_blocksetting_entry(mining.bs, timeframe=mining.tf, capa=capa, blocksetting_capa2=blocksetting_capa2)
        payload = {
            "ok": True, "mining": mining.num, "capa": capa,
            "output_path": out_path, "filename": os.path.basename(out_path),
            "costs_source": costs["source"], "symbol": costs["symbol"],
            "spread": costs["spread"], "swap_long": costs["swap_long"], "swap_short": costs["swap_short"],
            "data_available": costs.get("data_available"), "data_rows": costs.get("data_rows"),
            "blocksetting": blocksetting_trace(bs_entry),
        }
        if workspace_context:
            record_workspace_output_generated(
                workspace_context,
                endpoint="generate",
                filename=os.path.basename(out_path),
                capa=capa,
                mining=mining.num,
            )
            payload.update(output_response_fields(workspace_context, out_path))
        return jsonify(payload)
    except Exception as e:
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 500


@app.post("/api/generate-custom")
def generate_custom():
    locked = require_feature("project_generator.generate")
    if locked:
        return locked
    data = request.get_json(silent=True) or {}
    try:
        capa = parse_generation_capa(data.get("capa", 1))
        mining, project_name = build_custom_mining(data)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    cfg = load_config()
    template = resolve_request_template(data, cfg, capa)
    output, workspace_context, remote_error = _resolve_generation_output(data, cfg, purpose="project_generator_generate_custom")
    if remote_error:
        return remote_error
    blocksetting_capa2 = data.get("blocksetting_capa2") or data.get("capa2_blocksetting")
    if not os.path.isfile(template):
        return jsonify({"ok": False, "error": f"template not found: {template}"}), 404

    db_path = cfg.get("sqx_data_db") or None
    postfix = cfg.get("darwinex_suffix") or DEFAULT_BROKER_POSTFIX
    aliases = cfg.get("asset_aliases") or {}
    try:
        out_path = generate_project(
            mining, template_path=template, output_dir=output, capa=capa,
            sqx_db_path=db_path, broker_postfix=postfix, alias_override=aliases,
            project_name=project_name,
            blocksetting_capa2=blocksetting_capa2,
        )
        costs = resolve_costs(mining, db_path, postfix, alias_override=aliases)
        bs_entry = resolve_blocksetting_entry(mining.bs, timeframe=mining.tf, capa=capa, blocksetting_capa2=blocksetting_capa2)
        payload = {
            "ok": True, "custom": True, "project_name": project_name,
            "asset": mining.asset, "tf": mining.tf, "bs": mining.bs, "dir": mining.dir,
            "capa": capa, "output_path": out_path, "filename": os.path.basename(out_path),
            "costs_source": costs["source"], "symbol": costs["symbol"],
            "spread": costs["spread"], "swap_long": costs["swap_long"], "swap_short": costs["swap_short"],
            "data_available": costs.get("data_available"), "data_rows": costs.get("data_rows"),
            "blocksetting": blocksetting_trace(bs_entry),
        }
        if workspace_context:
            record_workspace_output_generated(
                workspace_context,
                endpoint="generate-custom",
                filename=os.path.basename(out_path),
                capa=capa,
                mining=0,
            )
            payload.update(output_response_fields(workspace_context, out_path))
        return jsonify(payload)
    except Exception as e:
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 500


@app.post("/api/generate-all")
def generate_all():
    locked = require_feature("project_generator.generate")
    if locked:
        return locked
    data = request.get_json(silent=True) or {}
    capa = int(data.get("capa", 1))
    if capa not in (1, 2):
        return jsonify({"ok": False, "error": "capa must be 1 or 2"}), 400

    cfg = load_config()
    template = resolve_request_template(data, cfg, capa)
    output, workspace_context, remote_error = _resolve_generation_output(data, cfg, purpose="project_generator_generate_all")
    if remote_error:
        return remote_error
    blocksetting_capa2 = data.get("blocksetting_capa2") or data.get("capa2_blocksetting")

    if not os.path.isfile(template):
        return jsonify({"ok": False, "error": f"template not found: {template}"}), 404

    db_path = cfg.get("sqx_data_db") or None
    postfix = cfg.get("darwinex_suffix") or DEFAULT_BROKER_POSTFIX
    aliases = cfg.get("asset_aliases") or {}
    results = []
    for m in all_minings():
        try:
            out_path = generate_project(
                m, template_path=template, output_dir=output, capa=capa,
                sqx_db_path=db_path, broker_postfix=postfix, alias_override=aliases,
                blocksetting_capa2=blocksetting_capa2,
            )
            costs = resolve_costs(m, db_path, postfix, alias_override=aliases)
            bs_entry = resolve_blocksetting_entry(m.bs, timeframe=m.tf, capa=capa, blocksetting_capa2=blocksetting_capa2)
            result_item = {
                "mining": m.num, "ok": True,
                "filename": os.path.basename(out_path),
                "costs_source": costs["source"],
                "blocksetting": blocksetting_trace(bs_entry),
            }
            if workspace_context:
                record_workspace_output_generated(
                    workspace_context,
                    endpoint="generate-all",
                    filename=os.path.basename(out_path),
                    capa=capa,
                    mining=m.num,
                )
                result_item.update(output_response_fields(workspace_context, out_path))
            results.append(result_item)
        except Exception as e:
            results.append({"mining": m.num, "ok": False, "error": str(e)})

    ok = sum(1 for r in results if r["ok"])
    return jsonify({"ok": ok == len(results), "ok_count": ok, "fail_count": len(results) - ok, "results": results})


@app.post("/api/sqx-list")
def sqx_list():
    """Lista .sqx en una carpeta con metadata extraída.
    body: {dir: str, recursive: bool=true}
    """
    data = request.get_json(silent=True) or {}
    cfg = load_config()
    directory = (data.get("dir") or "").strip()
    recursive = data.get("recursive", True)
    if not directory or not os.path.isdir(directory):
        return jsonify({"ok": False, "error": "invalid dir", "files": []}), 400
    if not is_allowed_workspace_path(directory, cfg):
        return jsonify({
            "ok": False,
            "error": "dir is outside allowed workspace roots",
            "allowed_roots": [str(p).replace("\\", "/") for p in allowed_workspace_roots(cfg)],
            "files": [],
        }), 403
    files = list_sqx_directory(directory, recursive=recursive)
    return jsonify({"ok": True, "dir": directory, "count": len(files),
                    "files": [f.to_dict() for f in files]})


@app.post("/api/sqx-clean")
def sqx_clean():
    """Procesa selección de .sqx con opciones.
    body: {files: [path,...], options: {remove_exit_bars, rename_institutional, rename_pattern}}
    """
    locked = require_feature("strategy_cleaner.apply")
    if locked:
        return locked
    data = request.get_json(silent=True) or {}
    cfg = load_config()
    files = data.get("files") or []
    options = data.get("options") or {}
    options["backup"] = options.get("backup", True)
    if not files:
        return jsonify({"ok": False, "error": "no files"}), 400
    # Validar paths
    valid = [
        p for p in files
        if isinstance(p, str)
        and os.path.isfile(p)
        and p.lower().endswith(".sqx")
        and is_allowed_workspace_path(p, cfg)
    ]
    if not valid:
        return jsonify({
            "ok": False,
            "error": "no valid .sqx in selection or files outside allowed workspace roots",
            "allowed_roots": [str(p).replace("\\", "/") for p in allowed_workspace_roots(cfg)],
        }), 400
    results = process_files(valid, options)
    ok = sum(1 for r in results if r["ok"])
    return jsonify({"ok": ok == len(results), "ok_count": ok, "fail_count": len(results) - ok,
                    "results": results})


@app.post("/api/sqx-preview-rename")
def sqx_preview_rename():
    """Preview de nombres institucionales para una lista de .sqx.
    body: {files: [path,...], pattern: '{asset}_{tf}_{dir}_{id}'}
    """
    data = request.get_json(silent=True) or {}
    cfg = load_config()
    files = data.get("files") or []
    pattern = data.get("pattern") or "{asset}_{tf}_{dir}_{id}"
    out = []
    for p in files:
        if not (isinstance(p, str) and os.path.isfile(p) and is_allowed_workspace_path(p, cfg)):
            continue
        try:
            m = extract_metadata(p)
            new_name = institutional_name(m, pattern)
            out.append({"path": p, "current": m.name, "new_name": new_name + ".sqx",
                        "asset": m.asset, "tf": m.timeframe, "dir": m.direction})
        except Exception as e:
            out.append({"path": p, "error": str(e)})
    return jsonify({"ok": True, "previews": out})


@app.post("/api/open-folder")
def open_folder():
    """Abre una carpeta en Windows Explorer."""
    data = request.get_json(silent=True) or {}
    cfg = load_config()
    workspace_context, remote_error = _active_remote_workspace_for_request(purpose="project_generator_open_output", create=False)
    if remote_error:
        return remote_error
    if workspace_context:
        return jsonify({
            "ok": False,
            "error": "remote_open_folder_blocked",
            "message": "Remote users cannot open server folders. Use the generated file list/download flow instead.",
            "workspace": public_workspace_context(workspace_context),
            "privacy": {"local_paths_returned": False},
        }), 403
    path = data.get("path", "")
    if not path or not os.path.isdir(path):
        return jsonify({"ok": False, "error": "invalid path"}), 400
    if not is_allowed_workspace_path(path, cfg):
        return jsonify({
            "ok": False,
            "error": "path is outside allowed workspace roots",
            "allowed_roots": [str(p).replace("\\", "/") for p in allowed_workspace_roots(cfg)],
        }), 403
    try:
        subprocess.Popen(["explorer", os.path.abspath(path)])
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── Dashboard state backups ──────────────────────────────────────
# Guarda snapshots JSON del estado del dashboard. En local usa el directorio
# operador historico; en remoto usa el workspace derivado de la sesion.
def _sanitize_state_backup_data(data: dict) -> dict:
    return {key: value for key, value in data.items() if key in STATE_BACKUP_ALLOWED_KEYS}


def _state_backup_scope() -> tuple[dict, object | None]:
    remote_like = _is_authenticated_access_tunnel_request() or bool(request.cookies.get(SESSION_COOKIE_NAME))
    if not remote_like:
        return {
            "ok": True,
            "scope": "local_operator",
            "root": STATE_BACKUP_DIR,
            "workspace": None,
            "version": VERSION,
        }, None
    session_status, device_id = _remote_session_status_for_request(purpose="remote_state_backup")
    if not session_status.get("access", {}).get("allowed"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_STATE_BACKUP_VERSION,
            "error": "remote_session_required",
            "session": session_status.get("session"),
            "access": session_status.get("access"),
            "accessControl": session_status.get("accessControl"),
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), 403)
        return {}, _set_remote_device_cookie(response, device_id)
    workspace_context = derive_remote_workspace(session_status, create=True)
    if not workspace_context.get("ok"):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_STATE_BACKUP_VERSION,
            "error": workspace_context.get("error") or "remote_workspace_unavailable",
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), int(workspace_context.get("http_status") or 403))
        return {}, _set_remote_device_cookie(response, device_id)
    paths = workspace_context.get("_paths") if isinstance(workspace_context.get("_paths"), dict) else {}
    config_dir = paths.get("config")
    if not isinstance(config_dir, Path):
        response = make_response(jsonify({
            "ok": False,
            "version": REMOTE_STATE_BACKUP_VERSION,
            "error": "remote_workspace_config_missing",
            "privacy": {"session_token_returned": False, "local_paths_returned": False},
        }), 500)
        return {}, _set_remote_device_cookie(response, device_id)
    return {
        "ok": True,
        "scope": "remote_workspace",
        "root": config_dir / REMOTE_STATE_BACKUP_DIRNAME,
        "workspace": workspace_context,
        "device_id": device_id,
        "version": REMOTE_STATE_BACKUP_VERSION,
    }, None


def _state_backup_path(filename: str, root: Path) -> Path:
    if not filename.startswith("state_backup_") or not filename.endswith(".json"):
        abort(404)
    path = (root / filename).resolve(strict=False)
    try:
        path.relative_to(root.resolve(strict=False))
    except ValueError:
        abort(403)
    return path


def _list_state_backups(root: Path, scope: str) -> list[dict]:
    if not root.exists():
        return []
    files = sorted(
        root.glob("state_backup_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return [
        {
            "name": p.name,
            "size_kb": round(p.stat().st_size / 1024, 1),
            "mtime": int(p.stat().st_mtime),
            "scope": scope,
            "location": "workspace://state-backups" if scope == "remote_workspace" else "local://analysis_output",
        }
        for p in files
        if p.is_file()
    ]


def _rotate_state_backups(root: Path) -> int:
    files = sorted(
        root.glob("state_backup_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    stale = files[STATE_BACKUP_RETENTION:]
    deleted = 0
    for path in stale:
        try:
            path.unlink()
            deleted += 1
        except OSError:
            pass
    return deleted


@app.post("/api/state/backup")
def api_state_backup():
    """Guarda un backup timestamped del estado del dashboard.
    Body esperado: objeto JSON con claves de localStorage o payload equivalente.
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"ok": False, "error": "body must be a JSON object"}), 400

    scope, blocked = _state_backup_scope()
    if blocked is not None:
        return blocked
    root = scope["root"]
    root.mkdir(parents=True, exist_ok=True)
    clean_data = _sanitize_state_backup_data(data)
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S-%fZ")
    target = root / f"state_backup_{stamp}.json"
    payload = {
        "_meta": {
            "created_at": created_at,
            "version": scope["version"],
            "scope": scope["scope"],
            "keys": sorted(clean_data.keys()),
            "filtered_keys": sorted(set(data.keys()) - set(clean_data.keys())),
            "location": "workspace://state-backups" if scope["scope"] == "remote_workspace" else "local://analysis_output",
        },
        "data": clean_data,
    }
    if scope["scope"] == "remote_workspace":
        payload["_meta"]["workspace"] = public_workspace_context(scope["workspace"])
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    rotated = _rotate_state_backups(root)
    if scope["scope"] == "remote_workspace":
        append_workspace_audit_event(scope["workspace"], {
            "type": "remote_state_backup_created",
            "action": "state_backup",
            "filename": target.name,
            "keys": sorted(clean_data.keys()),
            "version": REMOTE_STATE_BACKUP_VERSION,
        })
    response = make_response(jsonify({
        "ok": True,
        "version": scope["version"],
        "scope": scope["scope"],
        "filename": target.name,
        "size_kb": round(target.stat().st_size / 1024, 1),
        "rotated": rotated,
        "workspace": public_workspace_context(scope["workspace"]) if scope["scope"] == "remote_workspace" else None,
        "privacy": {"local_paths_returned": False, "raw_email_returned": False},
    }))
    if scope["scope"] == "remote_workspace":
        return _set_remote_device_cookie(response, scope.get("device_id", ""))
    return response


@app.get("/api/state/backups")
def api_state_backups():
    """Lista backups disponibles, del mas reciente al mas antiguo."""
    scope, blocked = _state_backup_scope()
    if blocked is not None:
        return blocked
    response = make_response(jsonify({
        "ok": True,
        "version": scope["version"],
        "scope": scope["scope"],
        "backups": _list_state_backups(scope["root"], scope["scope"]),
        "workspace": public_workspace_context(scope["workspace"]) if scope["scope"] == "remote_workspace" else None,
        "privacy": {"local_paths_returned": False, "raw_email_returned": False},
    }))
    if scope["scope"] == "remote_workspace":
        return _set_remote_device_cookie(response, scope.get("device_id", ""))
    return response


@app.get("/api/state/restore/<path:filename>")
def api_state_restore(filename: str):
    """Devuelve el contenido de un backup concreto para restaurarlo en UI."""
    scope, blocked = _state_backup_scope()
    if blocked is not None:
        return blocked
    path = _state_backup_path(filename, scope["root"])
    if not path.is_file():
        abort(404)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if scope["scope"] == "remote_workspace":
        append_workspace_audit_event(scope["workspace"], {
            "type": "remote_state_backup_restored",
            "action": "state_restore",
            "filename": filename,
            "keys": sorted((payload.get("data") or {}).keys()) if isinstance(payload, dict) else [],
            "version": REMOTE_STATE_BACKUP_VERSION,
        })
    response = make_response(jsonify({
        "ok": True,
        "version": scope["version"],
        "scope": scope["scope"],
        "filename": filename,
        "payload": payload,
        "workspace": public_workspace_context(scope["workspace"]) if scope["scope"] == "remote_workspace" else None,
        "privacy": {"local_paths_returned": False, "raw_email_returned": False},
    }))
    if scope["scope"] == "remote_workspace":
        return _set_remote_device_cookie(response, scope.get("device_id", ""))
    return response


# ── Entrypoint ────────────────────────────────────────────────────
def main(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    print(f"\n[SQX Edge Tool] API server starting...")
    print(f"  URL: http://{host}:{port}")
    print(f"  Project root: {ROOT}")
    print(f"  Templates: {ROOT / 'templates'}")
    print(f"  Output: {resolve_output_dir(load_config())}")
    print(f"\n  Health check: http://{host}:{port}/api/health")
    print(f"  Press Ctrl+C to stop\n")
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--host", default=DEFAULT_HOST)
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = p.parse_args()
    main(args.host, args.port)
