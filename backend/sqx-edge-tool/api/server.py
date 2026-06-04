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
  POST /api/generate-pair     -> body: {asset, tf, dir, name?, bs?} -> genera Capa 1 y Capa 2
  POST /api/generate-all      -> body: {capa: 1|2} -> genera los 14
  GET  /api/output            -> lista de .cfx en output_dir
  GET  /api/output/download/* -> descarga .cfx generado
  POST /api/output/delete     -> borra .cfx generados seleccionados
  POST /api/open-folder       -> body: {path} -> abre carpeta en Explorer
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import subprocess
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

# Permitir ejecución directa o vía -m
ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ROOT.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, abort, jsonify, make_response, request, send_file, send_from_directory  # type: ignore

from core import Mining, all_minings, generate_project, get_mining, normalize_direction
from core.config_loader import load_manifest
from core.license_manager import (
    check_feature,
    clear_license_file,
    import_license_payload,
    license_status,
    load_product_manifest,
)
from core.project_generator import (
    DEFAULT_BROKER_POSTFIX,
    normalize_target_profile,
    public_target_profile,
    resolve_costs,
)
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
from core.sqx_readiness import (
    SQX_READINESS_VERSION,
    evaluate_readiness_report,
    gate_disabled_for_local_internal,
    read_readiness_status,
    readiness_gate_response,
    summarize_manifest_for_public,
    update_manual_status,
    write_readiness_status,
)
from core.support_diagnostics import build_support_diagnostics
from core.support_incidents import (
    append_support_incident,
    build_support_incident,
    support_incident_public_response,
    validate_support_incident,
)
from core.sqx_compatibility import SQX142_DEFAULT_ROOT, build_sqx142_status
from core.sqx_performance import build_sqx142_performance_status
from core.sqx142_mcp_like_readonly import (
    MCP_LIKE_VERSION,
    build_mcp_like_data_catalog,
    build_mcp_like_databanks,
    build_mcp_like_projects,
    build_mcp_like_status,
    build_mcp_like_strategies,
    build_results_plugin_readiness,
)
from core.sqx142_correlation_filter_external import (
    CORRELATION_FILTER_EXTERNAL_VERSION,
    build_correlation_filter_report,
    export_correlation_filter_csv,
    export_correlation_filter_sqx_tag_csv,
)
from core.sqx142_portfolio_correlation_stability import (
    CAPA1_C2_CORRELATION_SELECTION_VERSION,
    PORTFOLIO_CORRELATION_STABILITY_VERSION,
    build_capa1_c2_correlation_selection_report,
    build_portfolio_correlation_stability_report,
    export_portfolio_correlation_stability_csv,
)
from core.sqx142_monte_carlo_candidate_benchmarks import (
    MONTE_CARLO_BENCHMARKS_VERSION,
    build_monte_carlo_benchmark_report,
    export_monte_carlo_benchmark_csv,
)
from core.sqx142_mt5_data_intake_probe import (
    MT5_DATA_INTAKE_PROBE_VERSION,
    build_mt5_data_intake_probe_report,
    export_mt5_data_intake_probe_csv,
)
from core.sqx142_copy_only_migration_checklist import (
    COPY_ONLY_MIGRATION_CHECKLIST_VERSION,
    build_copy_only_migration_checklist,
    export_copy_only_migration_checklist_csv,
)
from core.sqx142_ai_wizard import (
    AI_WIZARD_AI2_VERSION,
    AI_WIZARD_VERSION,
    add_ai_wizard_message,
    build_ai_wizard_spec,
    build_ai_wizard_status,
    build_ai_wizard_capability_catalog,
    create_ai_wizard_session,
    create_ai_wizard_session_draft,
    generate_draft_sqx,
    get_ai_wizard_session,
    list_ai_wizard_sessions,
    patch_ai_wizard_session_spec,
    resolve_ai_wizard_draft_download,
    resolve_draft_download,
)
from tools.sqx142_mining_registry import (
    DEFAULT_DB as SQX142_MINING_REGISTRY_DEFAULT_DB,
    VERSION as SQX142_MINING_REGISTRY_VERSION,
    build_funnel_payload as build_sqx142_mining_registry_funnel,
    scan_project_databanks as scan_sqx142_mining_registry_project,
)
from tools.sqx142_portfolio_corr2_local_project_integration import (
    VERSION as SQX142_CAPA1_C2_CORR2_VERSION,
    apply_integration as apply_sqx142_portfolio_corr2_integration,
    build_plan as build_sqx142_portfolio_corr2_plan,
    build_status as build_sqx142_portfolio_corr2_status,
    record_manual_status as record_sqx142_portfolio_corr2_status,
    rollback_integration as rollback_sqx142_portfolio_corr2_integration,
)
from tools.sqx142_portfolio_corr1_registered_decision import (
    VERSION as SQX142_PORTFOLIO_CORR1_REGISTERED_DECISION_VERSION,
    analyze as analyze_sqx142_portfolio_corr1_registered_decision,
    status_for as build_sqx142_portfolio_corr1_registered_decision_status,
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
from core.agent.executor import execute_action
from core.agent.llm_client import OllamaClient, OllamaConfig
from core.agent.policy import consume_confirmation, create_confirmation, is_action_allowed
from core.agent.redaction import redact_data, redact_text, redacted_json
from core.agent.schemas import LOCAL_AI_AGENT_VERSION, PLAN_RESPONSE_SCHEMA, safe_plan_response
from core.agent.tool_catalog import (
    EDGE_STAGE_LABELS,
    build_action_catalog,
    recommended_action_for_stage,
)

app = Flask(__name__)


class DashboardApiAliasMiddleware:
    """Route /dashboard/api/* through the normal /api/* handlers.

    Cloudflare Access deployments can scope the dashboard policy to /dashboard.
    Keeping browser API calls under that path makes the dashboard and API share
    the same Access cookie/policy surface while preserving the existing backend
    route implementations.
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        path_info = environ.get("PATH_INFO") or ""
        if path_info == "/dashboard/api":
            environ["PATH_INFO"] = "/api"
        elif path_info.startswith("/dashboard/api/"):
            environ["PATH_INFO"] = "/api/" + path_info[len("/dashboard/api/"):]
        return self.app(environ, start_response)


app.wsgi_app = DashboardApiAliasMiddleware(app.wsgi_app)

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
    "sqx_readiness_status_v1",
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
PROJECT_DIRECTION_SUFFIX_RE = re.compile(
    r"(?:[._-](?:L|S|LS|LONG|SHORT|BOTH|LONGSHORT|LONG[._-]?SHORT|L[._-]?S))$",
    re.IGNORECASE,
)
REMOTE_WRITE_PILOT_AUDIT_PATH = PROJECT_ROOT / ".local" / "remote_service" / "remote_write_pilot.local.jsonl"
AGENT_AUDIT_PATH = PROJECT_ROOT / ".local" / "agent_inbox" / "agent_actions.local.jsonl"
REMOTE_AI_ALLOWED_ENTITLEMENTS = {"tester_free", "paid_subscription", "internal_operator"}


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
    if path.startswith("/api/agent/") and (
        _is_authenticated_access_tunnel_request() or bool(request.cookies.get(SESSION_COOKIE_NAME))
    ):
        return "remote_ai"
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
    if path.startswith("/api/sqx-readiness/") and method == "POST" and (
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
    if is_kill_switch_active(policy) and action in {"remote_session_login", "remote_protected_write", "remote_ai"}:
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


def _dashboard_asset_version() -> str:
    watched_roots = [DASHBOARD_ROOT / "js", DASHBOARD_ROOT / "css", DASHBOARD_ROOT / "vendor"]
    mtimes: list[float] = []
    for root in watched_roots:
        if root.exists():
            mtimes.extend(path.stat().st_mtime for path in root.rglob("*") if path.is_file())
    return str(int(max(mtimes or [datetime.now(timezone.utc).timestamp()])))


def _with_dashboard_asset_prefix(html: str) -> str:
    """Keep protected dashboard assets under the same /dashboard Access surface."""
    replacements = {
        'href="css/': 'href="/dashboard/css/',
        'href="assets/': 'href="/dashboard/assets/',
        'src="assets/': 'src="/dashboard/assets/',
        'src="js/': 'src="/dashboard/js/',
        'src="vendor/': 'src="/dashboard/vendor/',
    }
    for needle, replacement in replacements.items():
        html = html.replace(needle, replacement)
    version = _dashboard_asset_version()
    html = re.sub(r'(href|src)="(/dashboard/(?:css|js|vendor)/[^"#?]+)"', rf'\1="\2?v={version}"', html)
    return html


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
    html = _with_dashboard_asset_prefix(_with_absolute_link_preview_meta(html, "/dashboard"))
    response = make_response(html)
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


def _send_dashboard_asset(asset_path: str):
    first_segment = asset_path.split("/", 1)[0]
    if first_segment not in {"assets", "css", "js", "vendor"}:
        abort(404)
    if ".." in Path(asset_path).parts:
        abort(404)
    return send_from_directory(DASHBOARD_ROOT, asset_path)


@app.get("/dashboard/<path:asset_path>")
def serve_protected_dashboard_asset(asset_path: str):
    return _send_dashboard_asset(asset_path)


@app.get("/<path:asset_path>")
def serve_dashboard_asset(asset_path: str):
    return _send_dashboard_asset(asset_path)


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


def _target_profile_payload(data: dict, cfg: dict) -> dict:
    """Build the target SQX profile sent to the CFX generator.

    The target profile controls the primary broker/symbol resources used in
    generated projects. Methodological cross-broker retests, such as Retest 1
    OOS2 Dukascopy, are still enforced inside the generator and are not
    overridden by this profile.
    """
    raw = (
        (data or {}).get("target_profile")
        or (data or {}).get("targetProfile")
        or cfg.get("target_profile")
        or "sq_default_exact"
    )
    custom = (
        (data or {}).get("target_profile_custom")
        or (data or {}).get("targetProfileCustom")
        or cfg.get("target_profile_custom")
        or {}
    )
    if isinstance(raw, dict):
        payload = dict(raw)
        if custom and not payload.get("custom"):
            payload["custom"] = custom
        return payload
    profile_id = str(raw or "sq_default_exact")
    payload = {"id": profile_id}
    if profile_id == "custom_user_broker":
        payload["custom"] = custom if isinstance(custom, dict) else {}
    return payload


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


def _is_remote_app_request() -> bool:
    return _is_authenticated_access_tunnel_request() or bool(request.cookies.get(SESSION_COOKIE_NAME))


def _readiness_workspace_for_request(*, purpose: str, create: bool = True) -> tuple[dict | None, tuple | None]:
    if not _is_remote_app_request():
        return None, None
    return _active_remote_workspace_for_request(purpose=purpose, create=create)


def require_sqx_readiness(feature: str):
    current_license = license_status()
    is_remote = _is_remote_app_request()
    if gate_disabled_for_local_internal(is_remote, str(current_license.get("build_channel") or "")):
        return None
    workspace_context, remote_error = _readiness_workspace_for_request(purpose=f"sqx_readiness_gate:{feature}", create=True)
    if remote_error:
        return remote_error
    status = read_readiness_status(workspace_context)
    if status.get("complete"):
        return None
    return jsonify(readiness_gate_response(feature, status)), 428


def safe_project_token(value: str | None, fallback: str) -> str:
    cleaned = SAFE_PROJECT_TOKEN_RE.sub("_", (value or "").strip())
    cleaned = cleaned.strip("._-")
    return cleaned or fallback


def project_direction_tag(direction: str) -> str:
    return {"long": "L", "short": "S", "both": "LS"}[direction]


def ensure_project_direction_suffix(project_name: str, direction: str) -> str:
    tag = project_direction_tag(direction)
    stem = PROJECT_DIRECTION_SUFFIX_RE.sub("", project_name or "").strip("._-")
    return f"{stem}_{tag}" if stem else tag


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
    direction_tag = project_direction_tag(direction)
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
    raw_project_name = str(data.get("name") or data.get("project_name") or default_name)
    project_name = safe_project_token(raw_project_name, default_name)
    project_name = ensure_project_direction_suffix(project_name, direction)
    return mining, project_name


def resolve_pair_request_template(data: dict, cfg: dict, capa: int) -> str:
    pair_data = dict(data or {})
    specific = (
        pair_data.get(f"template_capa{capa}")
        or pair_data.get(f"templateCapa{capa}")
        or pair_data.get(f"template_c{capa}")
    )
    if specific:
        pair_data["template"] = specific
    elif not looks_like_cfx_template_path(str(pair_data.get("template") or "")):
        pair_data.pop("template", None)
    return resolve_request_template(pair_data, cfg, capa)


def _truthy_request_value(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "si", "sí", "on"}
    return False


def _pair_generation_input(data: dict) -> dict:
    pair_data = dict(data or {})
    if not pair_data.get("bs") and not pair_data.get("blocksetting"):
        pair_data["bs"] = (
            pair_data.get("blocksetting_capa1")
            or pair_data.get("capa1_blocksetting")
            or pair_data.get("capa1_bs")
            or pair_data.get("bs_capa1")
            or "BS_Custom"
        )
    pair_data["capa"] = 1
    return pair_data


def _generation_error_message(error: Exception, *, remote: bool) -> str:
    message = f"{type(error).__name__}: {error}"
    return redact_text(message) if remote else message


def _generated_file_entry(result_item: dict) -> dict:
    return {
        "capa": result_item.get("capa"),
        "name": result_item.get("filename"),
        "path": result_item.get("output_path"),
    }


def render_custom_project_visual_guide_pdf(project_name: str, cfx_path: str) -> dict:
    pdf_dir = PROJECT_ROOT / "output" / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_name = f"{safe_project_token(project_name, 'custom_project')}_visual_check_guide.pdf"
    pdf_path = pdf_dir / pdf_name
    relative_path = f"output/pdf/{pdf_name}"
    script = ROOT / "tools" / "render_custom_project_visual_guide.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--output",
            str(pdf_path),
            "--project-name",
            project_name,
            "--cfx-file",
            os.path.basename(cfx_path or ""),
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "visual guide PDF generation failed").strip()
        return {"ok": False, "error": redact_text(message)[:1200]}
    return {
        "ok": True,
        "filename": pdf_name,
        "relative_path": relative_path,
        "output_path": relative_path,
        "strict": False,
        "screenshots_pending": True,
        "privacy": {"local_paths_returned": False},
    }


# ── Endpoints ─────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    cfg = load_config()
    db_path = cfg.get("sqx_data_db", "")
    output_dir = Path(resolve_output_dir(cfg))
    current_license = license_status()
    payload = {
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
    }
    if _is_authenticated_access_tunnel_request():
        payload.pop("sqx_path", None)
        payload.pop("output_dir", None)
        payload["privacy"] = {"local_paths_returned": False}
    return jsonify(payload)


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
        raw_text = str(raw)
        raw_path = raw_text.replace("~", str(home), 1) if raw_text.startswith("~") else raw_text
        search_roots.append(Path(raw_path))
    env_sqx144_root = os.environ.get("SQX144_FULL_ROOT")
    if env_sqx144_root:
        search_roots.append(Path(env_sqx144_root))
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
        if root.is_dir():
            for sub in root.rglob("StrategyQuantX*.exe"):
                parent = sub.parent
                if str(parent).lower() not in seen:
                    search_roots.append(parent)
        db = root / "user" / "data" / "data.db"
        if db.is_file():
            sqx_exe = root / "StrategyQuantX.exe"
            host_profile = _sqx_host_profile_for_path(root)
            candidates.append({
                "sqx_path": str(root).replace("\\", "/"),
                "data_db": str(db).replace("\\", "/"),
                "projects_dir": str(root / "user" / "projects").replace("\\", "/"),
                "version": host_profile.get("version", "?"),
                "sqx_host_profile": host_profile.get("profile", "unknown"),
                "has_exe": sqx_exe.is_file(),
            })
    return jsonify({"ok": True, "found": len(candidates), "candidates": candidates})


def _sqx_host_profile_for_path(path_value):
    normalized = str(path_value).replace("\\", "/").casefold()
    if "sqx_144_full" in normalized:
        return {"profile": "sqx144_full", "version": "144"}
    if "sqx_144" in normalized:
        return {"profile": "sqx144", "version": "144"}
    if "sqx_143" in normalized:
        return {"profile": "sqx143", "version": "143"}
    if "sqx_142" in normalized:
        return {"profile": "sqx142", "version": "142"}
    if "sqx_141" in normalized:
        return {"profile": "sqx141", "version": "141"}
    return {"profile": "unknown", "version": "?"}


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
    host_profile = _sqx_host_profile_for_path(base)
    return jsonify({
        "ok": True,
        "valid": db.is_file(),
        "version": host_profile.get("version", "?"),
        "sqx_host_profile": host_profile.get("profile", "unknown"),
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


def _load_agent_profiles() -> dict:
    profiles = load_manifest("agent_profiles.json")
    return profiles if isinstance(profiles, dict) else {}


def _agent_ollama_config() -> OllamaConfig:
    profiles = _load_agent_profiles()
    provider = profiles.get("provider") if isinstance(profiles.get("provider"), dict) else {}
    return OllamaConfig(
        base_url=str(provider.get("baseUrl") or "http://127.0.0.1:11434"),
        model=str(provider.get("model") or "qwen3.5:latest"),
        fallback_model=str(provider.get("fallbackModel") or "qwen2.5-coder:3b"),
        timeout_seconds=float(provider.get("timeoutSeconds") or 12),
        offline_only=bool(provider.get("offlineOnly", True)),
        auto_start=bool(provider.get("autoStart", True)),
        executable=str(provider.get("executable") or ""),
        startup_wait_seconds=float(provider.get("startupWaitSeconds") or 6),
    )


def _agent_translation_ollama_config(status: dict | None = None) -> tuple[OllamaConfig, str]:
    profiles = _load_agent_profiles()
    provider = profiles.get("provider") if isinstance(profiles.get("provider"), dict) else {}
    base_config = _agent_ollama_config()
    models = status.get("models") if isinstance(status, dict) and isinstance(status.get("models"), list) else []
    installed = {str(model) for model in models}
    candidates = [
        str(provider.get("translationModel") or "").strip(),
        "qwen2.5-coder:1.5b",
        str(provider.get("fallbackModel") or "").strip(),
        "qwen2.5-coder:3b",
        str((status or {}).get("model") or "").strip(),
        base_config.model,
    ]
    selected = ""
    for candidate in candidates:
        if not candidate:
            continue
        if not installed or candidate in installed:
            selected = candidate
            break
    selected = selected or base_config.model
    timeout = float(provider.get("translationTimeoutSeconds") or max(base_config.timeout_seconds, 90))
    return OllamaConfig(
        base_url=base_config.base_url,
        model=selected,
        fallback_model=base_config.fallback_model,
        timeout_seconds=timeout,
        offline_only=base_config.offline_only,
        auto_start=base_config.auto_start,
        executable=base_config.executable,
        startup_wait_seconds=base_config.startup_wait_seconds,
    ), selected


def _agent_access_context() -> tuple[dict | None, tuple | None]:
    """Allow local operator access plus authenticated remote app sessions for the AI pilot."""
    local_operator = _is_local_remote(request.remote_addr) and _is_local_host(request.host) and not trusted_email_from_headers(request.headers)
    if local_operator:
        return {
            "scope": "local_operator",
            "remote": False,
            "entitlementKind": "internal_operator",
            "capabilityMode": "operator_full",
        }, None

    if _is_authenticated_access_tunnel_request() or request.cookies.get(SESSION_COOKIE_NAME):
        session_status, _device_id = _remote_session_status_for_request(purpose="agent_ai")
        session = session_status.get("session") if isinstance(session_status.get("session"), dict) else {}
        access = session_status.get("access") if isinstance(session_status.get("access"), dict) else {}
        entitlement = session_status.get("entitlement") if isinstance(session_status.get("entitlement"), dict) else {}
        entitlement_kind = str(session.get("entitlement_kind") or entitlement.get("kind") or "")
        allowed = bool(session.get("active") and access.get("allowed") and entitlement_kind in REMOTE_AI_ALLOWED_ENTITLEMENTS)
        if allowed:
            return {
                "scope": "remote_user",
                "remote": True,
                "entitlementKind": entitlement_kind,
                "emailRef": session.get("email_ref"),
                "capabilityMode": "tester_safe",
            }, None
        return None, (jsonify({
            "ok": False,
            "version": LOCAL_AI_AGENT_VERSION,
            "error": "remote_ai_session_required",
            "message": "Inicia una sesion remota valida antes de usar el agente IA.",
            "privacy": {
                "local_paths_returned": False,
                "raw_email_returned": False,
                "protected_url_returned": False,
                "prompt_persisted": False,
            },
        }), 403)

    return None, (jsonify({
        "ok": False,
        "version": LOCAL_AI_AGENT_VERSION,
        "error": "local_ai_agent_access_denied",
        "privacy": {
            "local_paths_returned": False,
            "raw_email_returned": False,
            "protected_url_returned": False,
            "prompt_persisted": False,
        },
    }), 403)


LOCAL_OPERATOR_ONLY_AGENT_ACTIONS = {
    "inspect_inbox",
    "sqx142_compat_help",
    "sqx142_performance_help",
    "sqx_c1_config_help",
    "sqx_test_guardian_help",
    "sqx_docs_curator_help",
    "sqx_academic_lopez_help",
    "sqx_agent_skills_help",
}


def _agent_actions_for_context(context: dict | None = None) -> dict:
    actions = build_action_catalog(_load_agent_profiles())
    if not context or not context.get("remote"):
        return actions
    return {
        action_id: action
        for action_id, action in actions.items()
        if action.risk in {"read", "navigate"}
        and action.id not in LOCAL_OPERATOR_ONLY_AGENT_ACTIONS
        and not action.id.startswith("mark_step:")
    }


def _agent_public_status(context: dict | None = None) -> dict:
    profiles = _load_agent_profiles()
    client = OllamaClient(_agent_ollama_config())
    llm_status = client.status()
    profile_map = profiles.get("profiles") if isinstance(profiles.get("profiles"), dict) else {}
    inbox = profiles.get("inbox") if isinstance(profiles.get("inbox"), dict) else {}
    handoffs = profiles.get("handoffs") if isinstance(profiles.get("handoffs"), dict) else {}
    runtime_bootstrap = profiles.get("runtimeBootstrap") if isinstance(profiles.get("runtimeBootstrap"), dict) else {}
    access = context or {"scope": "local_operator", "remote": False, "capabilityMode": "operator_full"}
    return {
        "ok": True,
        "version": LOCAL_AI_AGENT_VERSION,
        "active": bool(llm_status.get("available")),
        "audience": profiles.get("audience") or "local_operator_only",
        "execution": (profiles.get("policy") or {}).get("execution", "guide_then_confirm") if isinstance(profiles.get("policy"), dict) else "guide_then_confirm",
        "provider": {
            "id": (profiles.get("provider") or {}).get("id", "ollama") if isinstance(profiles.get("provider"), dict) else "ollama",
            "available": bool(llm_status.get("available")),
            "model": llm_status.get("model"),
            "configuredModel": llm_status.get("configuredModel"),
            "fallbackModel": llm_status.get("fallbackModel"),
            "error": llm_status.get("error", ""),
            "autoStart": llm_status.get("autoStart") or {},
        },
        "access": {
            "scope": access.get("scope"),
            "remote": bool(access.get("remote")),
            "entitlementKind": access.get("entitlementKind"),
            "capabilityMode": access.get("capabilityMode"),
            "monitorVisible": False if access.get("remote") else True,
        },
        "profiles": [{"id": key, "label": value.get("label", key)} for key, value in sorted(profile_map.items()) if isinstance(value, dict)],
        "inbox": {
            "enabled": not bool(access.get("remote")),
            "root": ".local/agent_inbox",
            "incoming": inbox.get("incoming", ".local/agent_inbox/incoming") if isinstance(inbox, dict) else ".local/agent_inbox/incoming",
            "localPathReturned": False,
        },
        "handoffs": {
            "enabled": not bool(access.get("remote")),
            "root": handoffs.get("root", ".local/agent_handoffs") if isinstance(handoffs, dict) else ".local/agent_handoffs",
            "persistPrompts": bool(handoffs.get("persistPrompts", False)) if isinstance(handoffs, dict) else False,
            "persistPrivateEvidence": bool(handoffs.get("persistPrivateEvidence", False)) if isinstance(handoffs, dict) else False,
            "localPathReturned": False,
        },
        "runtimeBootstrap": {"visible": False} if access.get("remote") else runtime_bootstrap,
        "sqx142Compat": {"visible": False} if access.get("remote") else build_sqx142_status(include_paths=False),
        "sqx142Performance": {"visible": False} if access.get("remote") else build_sqx142_performance_status(PROJECT_ROOT, include_paths=False),
        "privacy": {
            "local_paths_returned": False,
            "raw_email_returned": False,
            "protected_url_returned": False,
            "prompt_persisted": False,
            "conversation_persisted": False,
        },
    }


def _agent_stage_from_payload(data: dict) -> str:
    state = data.get("edgeFactoryState") if isinstance(data.get("edgeFactoryState"), dict) else {}
    context = data.get("context") if isinstance(data.get("context"), dict) else {}
    raw = state.get("activeStep") or context.get("activeStep") or data.get("activeStep") or "session"
    return str(raw) if str(raw) in EDGE_STAGE_LABELS else "session"


def _is_capabilities_question(value: object) -> bool:
    text = str(value or "").lower()
    normalized = (
        text.replace("¿", "")
        .replace("?", "")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    markers = [
        "que eres capaz de hacer",
        "que puedes hacer",
        "que sabes hacer",
        "capabilities",
        "capacidades",
        "ayuda",
        "help",
    ]
    return any(marker in normalized for marker in markers)


def _is_sqx142_compat_question(value: object) -> bool:
    text = str(value or "").lower()
    normalized = (
        text.replace("¿", "")
        .replace("?", "")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    markers = [
        "sqx 142",
        "build 143",
        "build 144",
        "compatibilidad",
        "backport",
        "hotfix",
        "runtime sqx",
    ]
    return any(marker in normalized for marker in markers)


def _is_sqx142_performance_question(value: object) -> bool:
    text = str(value or "").lower()
    normalized = (
        text.replace("¿", "")
        .replace("?", "")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    markers = [
        "rendimiento sqx",
        "performance sqx",
        "optimizar sqx",
        "minados",
        "retests",
        "montecarlo",
        "monte carlo",
        "databanks",
        "perfil jvm",
        "perfil activo",
        "sqx142_performance",
    ]
    return any(marker in normalized for marker in markers)


def _is_sqx_c1_config_question(value: object) -> bool:
    text = str(value or "").lower()
    normalized = (
        text.replace("¿", "")
        .replace("?", "")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    markers = [
        "c1-config1",
        "capa1 config",
        "config capa1",
        "task config",
        "sqx142_task_config",
        "retest 0",
        "mining15",
        "cuestionario",
    ]
    return any(marker in normalized for marker in markers)


def _is_sqx_test_guardian_question(value: object) -> bool:
    text = str(value or "").lower()
    normalized = (
        text.replace("¿", "")
        .replace("?", "")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    markers = [
        "test guardian",
        "checks sqx",
        "matriz de tests",
        "regresion",
        "que tests",
        "verificacion",
    ]
    return any(marker in normalized for marker in markers)


def _is_sqx_docs_curator_question(value: object) -> bool:
    text = str(value or "").lower()
    normalized = (
        text.replace("¿", "")
        .replace("?", "")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    markers = [
        "docs curator",
        "documentacion",
        "manifest",
        "state consistency",
        "governance",
        "gobernanza",
        "changelog",
    ]
    return any(marker in normalized for marker in markers)


def _is_sqx_academic_lopez_question(value: object) -> bool:
    text = str(value or "").lower()
    normalized = (
        text.replace("¿", "")
        .replace("?", "")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    markers = [
        "academic",
        "academico",
        "academica",
        "lopez",
        "lopez de prado",
        "data snooping",
        "backtest overfitting",
        "overfitting",
        "deflated sharpe",
        "probability of backtest overfitting",
        "pbo",
        "purged",
        "embargo",
        "contaminacion",
        "contaminar",
        "mc y oos",
        "monte carlo y oos",
    ]
    return any(marker in normalized for marker in markers)


def _is_sqx_agent_skills_question(value: object) -> bool:
    text = str(value or "").lower()
    normalized = (
        text.replace("¿", "")
        .replace("?", "")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    markers = [
        "agentes",
        "agents",
        "skills",
        "handoff",
        "subagentes",
        "subagents",
        "g8-sqx-agent-skills1",
    ]
    return any(marker in normalized for marker in markers)


def _agent_capabilities_plan(actions: dict | None = None, *, context: dict | None = None) -> dict:
    actions = actions or build_action_catalog(_load_agent_profiles())
    action = actions["capabilities_help"]
    if context and context.get("remote"):
        reply = (
            "Soy el agente IA local de SQX Edge Suite en modo tester seguro. Puedo orientarte por Edge Factory, "
            "explicar el siguiente paso, abrir herramientas internas con tu confirmacion y refrescar el estado visible "
            "de la app. No tengo acceso al monitor local del servidor, a la bandeja local del creador ni a acciones de "
            "escritura como marcar etapas. No ejecuto texto libre ni cambios sin confirmacion, y no puedo tocar emails, "
            "grants, checkout, Cloudflare, permisos, URLs protegidas, borrados, publicaciones ni acciones comerciales externas."
        )
    else:
        reply = (
            "Soy el agente IA local de SQX Edge Suite para operador. Puedo orientarte por Edge Factory, "
            "explicar el siguiente paso, abrir herramientas internas con tu confirmacion, refrescar estado local, "
            "revisar la bandeja local bajo confirmacion, explicar la compatibilidad SQX 142/143/144, analizar rendimiento SQX 142, "
            "explicar C1-CONFIG1 y activar perspectivas internas de Test Guardian, Docs Curator, Academic Lopez y skills cuando reduzcan riesgo. "
            "No ejecuto texto libre ni cambios sin confirmacion, y no puedo tocar emails, grants, checkout, Cloudflare, permisos, URLs protegidas, "
            "borrados, publicaciones ni acciones comerciales externas."
        )
    return safe_plan_response(
        reply=reply,
        profile="orchestrator",
        action=action,
        reason="Pregunta directa sobre capacidades del agente.",
        blockers=[],
        arguments={},
        source="fixed_capabilities",
    )


def _agent_sqx142_compat_plan(actions: dict | None = None) -> dict:
    actions = actions or build_action_catalog(_load_agent_profiles())
    action = actions["sqx142_compat_help"]
    status = build_sqx142_status(include_paths=False)
    java = status.get("java") if isinstance(status.get("java"), dict) else {}
    active = java.get("active") if isinstance(java.get("active"), dict) else {}
    reference = java.get("reference") if isinstance(java.get("reference"), dict) else {}
    blockers = [str(item) for item in status.get("blockers", [])][:8]
    reply = (
        "Compatibilidad SQX 142/143: la build 143 local queda como referencia segura para runtime/config y extensiones. "
        f"Runtime activo: {active.get('label') or 'desconocido'}; referencia 143: {reference.get('label') or 'desconocida'}. "
        f"Estado: {status.get('status')}. {status.get('recommendation')}"
    )
    return safe_plan_response(
        reply=reply,
        profile="sqx142-compat",
        action=action,
        reason="Consulta interna sobre compatibilidad SQX 142/143/144.",
        blockers=blockers,
        arguments={},
        source="fixed_sqx142_compat",
    )


def _agent_sqx142_performance_plan(actions: dict | None = None) -> dict:
    actions = actions or build_action_catalog(_load_agent_profiles())
    action = actions["sqx142_performance_help"]
    status = build_sqx142_performance_status(PROJECT_ROOT, include_paths=False)
    profile = status.get("activeProfile") if isinstance(status.get("activeProfile"), dict) else {}
    resources = status.get("resources") if isinstance(status.get("resources"), dict) else {}
    disk = resources.get("disk") if isinstance(resources.get("disk"), dict) else {}
    compat = status.get("compatibility") if isinstance(status.get("compatibility"), dict) else {}
    intelligence = status.get("intelligence") if isinstance(status.get("intelligence"), dict) else {}
    views = intelligence.get("views") if isinstance(intelligence.get("views"), dict) else {}
    latest_evidence = intelligence.get("latestEvidence") if isinstance(intelligence.get("latestEvidence"), dict) else status.get("latestEvidence", {})
    recommendation = intelligence.get("recommendation") if isinstance(intelligence.get("recommendation"), dict) else {}
    live_guard = intelligence.get("liveGuard") if isinstance(intelligence.get("liveGuard"), dict) else {}
    warnings = [str(item) for item in status.get("warnings", [])][:8]
    view_text = (
        f"{views.get('presentCount')}/{views.get('expectedCount')} views OK"
        if views.get("expectedCount") is not None
        else "views sin resumen"
    )
    evidence_text = latest_evidence.get("filename") if isinstance(latest_evidence, dict) and latest_evidence.get("filename") else "sin evidencia reciente"
    recommendation_text = recommendation.get("label") or "mantener medicion antes de cambiar metodologia"
    live_guard_text = (
        f"Live Guard: {live_guard.get('state') or 'sin estado'}, alertas {live_guard.get('alertCount', 0)}"
        if live_guard
        else "Live Guard: sin resumen"
    )
    reply = (
        "Performance Gate SQX 142: la optimizacion queda controlada por medicion, perfiles reversibles y calidad protegida. "
        f"Perfil activo: {profile.get('id') or 'desconocido'}; disco libre: {disk.get('freeHuman') or 'desconocido'} ({disk.get('state') or 'unknown'}); "
        f"runtime: {compat.get('runtime') or 'desconocido'}; estado: {status.get('status')}; {view_text}; ultima evidencia: {evidence_text}. "
        f"{live_guard_text}. "
        f"Siguiente accion recomendada: {recommendation_text}. "
        "No reduzco OOS/Forward, precision, simulaciones ni filtros finales sin evidencia explicita."
    )
    return safe_plan_response(
        reply=reply,
        profile="sqx142-performance",
        action=action,
        reason="Consulta interna sobre rendimiento SQX 142.",
        blockers=warnings,
        arguments={},
        source="fixed_sqx142_performance",
    )


def _agent_sqx_c1_config_plan(actions: dict | None = None) -> dict:
    actions = actions or build_action_catalog(_load_agent_profiles())
    action = actions["sqx_c1_config_help"]
    reply = (
        "C1-CONFIG1 esta en configuracion interactiva de Capa1 base. Build ya queda cerrado y antes de RETEST 0 "
        "entra G8-SQX-AGENT-SKILLS1 para activar guardianes de tests/docs, handoffs locales y perfiles del agente. "
        "Las respuestas completas viven en .local/sqx142_task_config/; la promocion desde Mining15 sigue siendo selectiva y normalizada. "
        "No toco la base ni ejecuto retests sin fase cerrada, backup, diff y confirmacion."
    )
    return safe_plan_response(
        reply=reply,
        profile="sqx-c1-config",
        action=action,
        reason="Consulta local sobre C1-CONFIG1 y el salto controlado hacia RETEST 0.",
        blockers=[],
        arguments={},
        source="fixed_sqx_c1_config",
    )


def _agent_sqx_test_guardian_plan(actions: dict | None = None) -> dict:
    actions = actions or build_action_catalog(_load_agent_profiles())
    action = actions["sqx_test_guardian_help"]
    reply = (
        "SQX Test Guardian propone la matriz minima para esta fase: compileall backend, "
        "test_local_ai_agent.py, test_docs_state_consistency.py, agent_guide_contracts.mjs y git diff --check. "
        "Si cambia UI o wiring JS, suma contratos JS completos. Solo recomienda/ejecuta checks read-only o dry-run; "
        "no usa --apply, --write, --launch ni arranca SQX real sin aprobacion exacta."
    )
    return safe_plan_response(
        reply=reply,
        profile="sqx-test-guardian",
        action=action,
        reason="Consulta local sobre verificacion y regresion de la fase activa.",
        blockers=[],
        arguments={},
        source="fixed_sqx_test_guardian",
    )


def _agent_sqx_docs_curator_plan(actions: dict | None = None) -> dict:
    actions = actions or build_action_catalog(_load_agent_profiles())
    action = actions["sqx_docs_curator_help"]
    reply = (
        "SQX Docs Curator revisa que README, CHANGELOG, governance, roadmap C1, roadmap del agente y "
        "state_consistency_manifest cuenten la misma historia: G8-SQX-AGENT-SKILLS1 va antes de RETEST 0, "
        "los guardianes son internos/local-only y no hay claims, rutas, emails, tokens ni evidencia privada en docs."
    )
    return safe_plan_response(
        reply=reply,
        profile="sqx-docs-curator",
        action=action,
        reason="Consulta local sobre documentacion y consistencia de estado.",
        blockers=[],
        arguments={},
        source="fixed_sqx_docs_curator",
    )


def _agent_sqx_academic_lopez_plan(actions: dict | None = None) -> dict:
    actions = actions or build_action_catalog(_load_agent_profiles())
    action = actions["sqx_academic_lopez_help"]
    reply = (
        "SQX Academic Lopez recomienda tratar MC como prueba de perturbacion de robustez, no como un nuevo optimizador. "
        "Reusar OOS dentro de cada retest aumenta la presion de seleccion sobre el mismo holdout; por defecto conviene mantener "
        "MC sobre ROBUSTNESS_C1 sin split OOS interno, conservar failed naturales y documentar cualquier cambio de filtros para reducir data snooping. "
        "La precision fast/simulated es defendible en MC por coste si TICK REAL ya cubre precision-data, dejando el endurecimiento "
        "realista para TICK REAL, MC2/Sequential o el cierre Capa1. Para una decision final con claims academicos, se debe citar "
        "White, Bailey/Lopez de Prado y Deflated Sharpe/PBO antes de promocionar metodologia."
    )
    return safe_plan_response(
        reply=reply,
        profile="sqx-academic-lopez",
        action=action,
        reason="Consulta local sobre criterio academico para MC, OOS, data snooping y robustez.",
        blockers=[],
        arguments={},
        source="fixed_sqx_academic_lopez",
    )


def _agent_sqx_agent_skills_plan(actions: dict | None = None) -> dict:
    actions = actions or build_action_catalog(_load_agent_profiles())
    action = actions["sqx_agent_skills_help"]
    reply = (
        "La capa G8-SQX-AGENT-SKILLS1 actualiza skills y perfiles para trabajar con guardianes, y G9R endurece el runtime "
        "para que no dependa solo de memoria conversacional. Si el operador pide G9, subagentes o trabajo en paralelo, hay que "
        "cargar Multi-agent tools con tool_search cuando no esten expuestas, lanzar subagentes independientes en la misma ronda "
        "si las tareas son separables, y dejar handoff breve en .local/agent_handoffs/ cuando afecte al siguiente paso. "
        "Codex sigue como orquestador: la autonomia sube en lectura, planificacion y verificacion; no en mutaciones."
    )
    return safe_plan_response(
        reply=reply,
        profile="sqx-agent-skills",
        action=action,
        reason="Consulta local sobre agentes, skills, handoffs y autonomia permitida.",
        blockers=[],
        arguments={},
        source="fixed_sqx_agent_skills",
    )


def _agent_heuristic_plan(
    data: dict,
    *,
    source: str = "heuristic",
    actions: dict | None = None,
    context: dict | None = None,
) -> dict:
    actions = actions or build_action_catalog(_load_agent_profiles())
    if _is_capabilities_question(data.get("message") or data.get("question")):
        return _agent_capabilities_plan(actions, context=context)
    if not (context and context.get("remote")) and _is_sqx_agent_skills_question(data.get("message") or data.get("question")):
        return _agent_sqx_agent_skills_plan(actions)
    if not (context and context.get("remote")) and _is_sqx_docs_curator_question(data.get("message") or data.get("question")):
        return _agent_sqx_docs_curator_plan(actions)
    if not (context and context.get("remote")) and _is_sqx_academic_lopez_question(data.get("message") or data.get("question")):
        return _agent_sqx_academic_lopez_plan(actions)
    if not (context and context.get("remote")) and _is_sqx_test_guardian_question(data.get("message") or data.get("question")):
        return _agent_sqx_test_guardian_plan(actions)
    if not (context and context.get("remote")) and _is_sqx_c1_config_question(data.get("message") or data.get("question")):
        return _agent_sqx_c1_config_plan(actions)
    if not (context and context.get("remote")) and _is_sqx142_performance_question(data.get("message") or data.get("question")):
        return _agent_sqx142_performance_plan(actions)
    if not (context and context.get("remote")) and _is_sqx142_compat_question(data.get("message") or data.get("question")):
        return _agent_sqx142_compat_plan(actions)
    stage = _agent_stage_from_payload(data)
    action = actions.get(recommended_action_for_stage(stage)) or actions["explain_next"]
    label = EDGE_STAGE_LABELS.get(stage, "Punto de partida")
    message = data.get("message") or data.get("question") or ""
    reply = (
        f"Estoy en {label}. El siguiente movimiento seguro es abrir la herramienta de esa etapa, "
        "revisar el contexto visible y confirmar antes de modificar nada."
    )
    if message:
        reply = f"{reply} He leído tu petición, pero mantengo el flujo con confirmación explícita."
    return safe_plan_response(
        reply=reply,
        profile=stage,
        action=action,
        reason=f"Etapa activa Edge Factory: {label}.",
        blockers=[],
        arguments={"stage": stage, **action.ui_command},
        source=source,
    )


def _agent_plan_with_llm(data: dict, *, actions: dict | None = None, context: dict | None = None) -> dict:
    actions = actions or build_action_catalog(_load_agent_profiles())
    if _is_capabilities_question(data.get("message") or data.get("question")):
        return _agent_capabilities_plan(actions, context=context)
    if not (context and context.get("remote")) and _is_sqx_agent_skills_question(data.get("message") or data.get("question")):
        return _agent_sqx_agent_skills_plan(actions)
    if not (context and context.get("remote")) and _is_sqx_docs_curator_question(data.get("message") or data.get("question")):
        return _agent_sqx_docs_curator_plan(actions)
    if not (context and context.get("remote")) and _is_sqx_academic_lopez_question(data.get("message") or data.get("question")):
        return _agent_sqx_academic_lopez_plan(actions)
    if not (context and context.get("remote")) and _is_sqx_test_guardian_question(data.get("message") or data.get("question")):
        return _agent_sqx_test_guardian_plan(actions)
    if not (context and context.get("remote")) and _is_sqx_c1_config_question(data.get("message") or data.get("question")):
        return _agent_sqx_c1_config_plan(actions)
    if not (context and context.get("remote")) and _is_sqx142_performance_question(data.get("message") or data.get("question")):
        return _agent_sqx142_performance_plan(actions)
    if not (context and context.get("remote")) and _is_sqx142_compat_question(data.get("message") or data.get("question")):
        return _agent_sqx142_compat_plan(actions)
    profiles = _load_agent_profiles()
    client = OllamaClient(_agent_ollama_config())
    status = client.status()
    if not status.get("available"):
        return _agent_heuristic_plan(data, source="heuristic_no_ollama", actions=actions, context=context)
    stage = _agent_stage_from_payload(data)
    safe_context = redact_data({
        "message": data.get("message") or "",
        "edgeFactoryState": data.get("edgeFactoryState") or {},
        "activeStage": stage,
        "capabilities": [action.public() for action in actions.values()],
    })
    messages = [
        {
            "role": "system",
            "content": (
                "Eres el agente local de SQX Edge Suite. Solo puedes recomendar acciones del catalogo. "
                "No inventes herramientas, no pidas datos sensibles y no ejecutes nada. Responde en JSON segun schema."
            ),
        },
        {"role": "user", "content": redacted_json(safe_context)},
    ]
    try:
        raw = client.chat_json(messages=messages, schema=PLAN_RESPONSE_SCHEMA, model=status.get("model"))
        action_id = str((raw.get("recommendedAction") or {}).get("id") or "")
        action = actions.get(action_id) or actions.get(recommended_action_for_stage(stage)) or actions["explain_next"]
        return safe_plan_response(
            reply=str(raw.get("reply") or ""),
            profile=str(raw.get("profile") or stage),
            action=action,
            reason=str((raw.get("recommendedAction") or {}).get("reason") or action.description),
            blockers=[str(item) for item in (raw.get("blockers") or [])][:8],
            arguments=(raw.get("recommendedAction") or {}).get("arguments") if isinstance((raw.get("recommendedAction") or {}).get("arguments"), dict) else {},
            source="ollama",
        )
    except Exception:
        return _agent_heuristic_plan(data, source="heuristic_after_llm_error", actions=actions, context=context)


def _record_agent_action(action_id: str, result: dict) -> None:
    try:
        AGENT_AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "version": "local-ai-agent-audit-v1",
            "at": datetime.now(timezone.utc).isoformat(),
            "actionId": action_id,
            "ok": bool(result.get("ok")),
            "risk": ((result.get("action") or {}).get("risk") or ""),
        }
        with AGENT_AUDIT_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    except OSError:
        return


def _strip_code_fences(value: str) -> str:
    text = str(value or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    if "```" in text:
        text = text.split("```", 1)[0].strip()
    return text


def _agent_translate_source_code(data: dict) -> tuple[dict, int]:
    source_code = str(data.get("sourceCode") or data.get("source") or "").strip()
    target = str(data.get("target") or "MQL5 Expert Advisor").strip()[:120]
    mode = str(data.get("mode") or "translate").strip().lower()
    feedback = str(data.get("feedback") or "").strip()[:8000]
    if not source_code:
        return {"ok": False, "version": LOCAL_AI_AGENT_VERSION, "error": "missing_source_code"}, 400
    if len(source_code) > 120000:
        return {"ok": False, "version": LOCAL_AI_AGENT_VERSION, "error": "source_code_too_large"}, 413

    client = OllamaClient(_agent_ollama_config())
    status = client.status()
    if not status.get("available"):
        return {
            "ok": False,
            "version": LOCAL_AI_AGENT_VERSION,
            "error": "ollama_unavailable",
            "provider": {"model": status.get("model"), "autoStart": status.get("autoStart") or {}},
        }, 503
    translation_config, translation_model = _agent_translation_ollama_config(status)
    translation_client = OllamaClient(translation_config)

    if mode == "fix":
        system_prompt = (
            "You are a local-only trading strategy code fixer. Fix the provided target code while preserving "
            "strategy logic. Output only complete corrected source code, no markdown fences and no explanations."
        )
        user_prompt = (
            f"Target platform/language: {target}\n\n"
            f"User feedback or compiler/runtime error:\n{feedback or 'No extra feedback.'}\n\n"
            f"Code to fix:\n{source_code}"
        )
    else:
        system_prompt = (
            "You are a local-only trading strategy source-code translator. Translate the complete strategy into "
            "the requested target platform/language. Preserve parameters, entry and exit rules, indicators, money "
            "management and order logic. Output only complete source code, no markdown fences and no explanations."
        )
        user_prompt = f"Translate this SQX strategy source code to {target}:\n\n{source_code}"

    try:
        profiles = _load_agent_profiles()
        provider = profiles.get("provider") if isinstance(profiles.get("provider"), dict) else {}
        max_tokens = int(provider.get("translationMaxTokens") or 900)
        output = translation_client.chat_text(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=translation_model,
            temperature=0.1,
            num_predict=max_tokens,
        )
    except Exception as exc:
        return {"ok": False, "version": LOCAL_AI_AGENT_VERSION, "error": type(exc).__name__}, 502

    return {
        "ok": True,
        "version": LOCAL_AI_AGENT_VERSION,
        "mode": "fix" if mode == "fix" else "translate",
        "target": target,
        "model": translation_model,
        "code": _strip_code_fences(output),
        "privacy": {"provider": "ollama_local", "external_api_called": False, "prompt_persisted": False},
    }, 200


def warmup_local_ai_agent() -> dict:
    """Best-effort Ollama warmup for server start; never blocks app startup hard."""
    try:
        return OllamaClient(_agent_ollama_config()).status(auto_start=True)
    except Exception as exc:
        return {"ok": False, "available": False, "error": type(exc).__name__}


@app.get("/api/agent/status")
def api_agent_status():
    context, error = _agent_access_context()
    if error:
        return error
    return jsonify(_agent_public_status(context))


@app.get("/api/sqx142/compat/status")
def api_sqx142_compat_status():
    local_operator = _is_local_remote(request.remote_addr) and _is_local_host(request.host) and not trusted_email_from_headers(request.headers)
    if not local_operator:
        return jsonify({
            "ok": False,
            "version": "sqx142-compat-status-v1",
            "error": "local_operator_required",
            "privacy": {"local_paths_returned": False},
        }), 403
    return jsonify(build_sqx142_status(include_paths=False))


@app.get("/api/sqx142/performance/status")
def api_sqx142_performance_status():
    local_operator = _is_local_remote(request.remote_addr) and _is_local_host(request.host) and not trusted_email_from_headers(request.headers)
    if not local_operator:
        return jsonify({
            "ok": False,
            "version": "sqx142-performance-status-v1",
            "error": "local_operator_required",
            "privacy": {"local_paths_returned": False},
        }), 403
    return jsonify(build_sqx142_performance_status(PROJECT_ROOT, include_paths=False))


def _sqx142_local_operator_error(version: str = MCP_LIKE_VERSION):
    return jsonify({
        "ok": False,
        "version": version,
        "error": "local_operator_required",
        "privacy": {
            "local_paths_returned": False,
            "raw_project_names_returned": False,
            "license_material_returned": False,
            "tokens_returned": False,
        },
    }), 403


def _require_sqx142_local_operator(version: str = MCP_LIKE_VERSION):
    local_operator = _is_local_remote(request.remote_addr) and _is_local_host(request.host) and not trusted_email_from_headers(request.headers)
    if not local_operator:
        return _sqx142_local_operator_error(version)
    return None


@app.get("/api/sqx142/mcp-like/status")
def api_sqx142_mcp_like_status():
    error = _require_sqx142_local_operator()
    if error:
        return error
    return jsonify(build_mcp_like_status(PROJECT_ROOT))


@app.get("/api/sqx142/mcp-like/projects")
def api_sqx142_mcp_like_projects():
    error = _require_sqx142_local_operator()
    if error:
        return error
    include_raw = str(request.args.get("includeRawNames", "")).casefold() == "true"
    return jsonify(build_mcp_like_projects(
        limit=request.args.get("limit"),
        offset=request.args.get("offset"),
        include_raw_names=include_raw,
    ))


@app.get("/api/sqx142/mcp-like/data-catalog")
def api_sqx142_mcp_like_data_catalog():
    error = _require_sqx142_local_operator()
    if error:
        return error
    return jsonify(build_mcp_like_data_catalog(limit=request.args.get("limit")))


@app.get("/api/sqx142/mcp-like/databanks")
def api_sqx142_mcp_like_databanks():
    error = _require_sqx142_local_operator()
    if error:
        return error
    return jsonify(build_mcp_like_databanks(
        project_id=str(request.args.get("projectId") or ""),
        limit=request.args.get("limit"),
    ))


@app.get("/api/sqx142/mcp-like/strategies")
def api_sqx142_mcp_like_strategies():
    error = _require_sqx142_local_operator()
    if error:
        return error
    return jsonify(build_mcp_like_strategies(
        project_id=str(request.args.get("projectId") or ""),
        limit=request.args.get("limit"),
    ))


@app.get("/api/sqx142/mcp-like/results-plugin-readiness")
def api_sqx142_mcp_like_results_plugin_readiness():
    error = _require_sqx142_local_operator()
    if error:
        return error
    return jsonify(build_results_plugin_readiness(PROJECT_ROOT))


@app.get("/api/sqx142/ai-wizard/status")
def api_sqx142_ai_wizard_status():
    error = _require_sqx142_local_operator(AI_WIZARD_VERSION)
    if error:
        return error
    return jsonify(build_ai_wizard_status(PROJECT_ROOT))


@app.post("/api/sqx142/ai-wizard/plan")
def api_sqx142_ai_wizard_plan():
    error = _require_sqx142_local_operator(AI_WIZARD_VERSION)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        payload = {}
    report = build_ai_wizard_spec(payload)
    status_code = 200 if report.get("ok") else 400
    return jsonify(report), status_code


@app.post("/api/sqx142/ai-wizard/draft-sqx")
def api_sqx142_ai_wizard_draft_sqx():
    error = _require_sqx142_local_operator(AI_WIZARD_VERSION)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        payload = {}
    report = generate_draft_sqx(payload, project_root=PROJECT_ROOT)
    status_code = 200 if report.get("ok") else 400
    return jsonify(report), status_code


@app.get("/api/sqx142/ai-wizard/draft-sqx/download/<path:file_name>")
def api_sqx142_ai_wizard_download(file_name: str):
    error = _require_sqx142_local_operator(AI_WIZARD_VERSION)
    if error:
        return error
    path = resolve_draft_download(PROJECT_ROOT, file_name)
    if not path:
        return jsonify({
            "ok": False,
            "version": AI_WIZARD_VERSION,
            "error": "draft_not_found",
            "privacy": {"local_paths_returned": False},
        }), 404
    return send_file(path, as_attachment=True, download_name=path.name, mimetype="application/octet-stream")


@app.get("/api/sqx142/ai-wizard/catalog")
def api_sqx142_ai_wizard_catalog():
    error = _require_sqx142_local_operator(AI_WIZARD_AI2_VERSION)
    if error:
        return error
    return jsonify(build_ai_wizard_capability_catalog(PROJECT_ROOT))


@app.post("/api/sqx142/ai-wizard/catalog/refresh")
def api_sqx142_ai_wizard_catalog_refresh():
    error = _require_sqx142_local_operator(AI_WIZARD_AI2_VERSION)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    if isinstance(payload, dict) and any(payload.get(key) for key in ("includeRawXml", "includeRawLabels", "includeSourceCode", "includeRawPaths")):
        return jsonify({
            "ok": False,
            "version": AI_WIZARD_AI2_VERSION,
            "error": "raw_catalog_request_blocked",
            "blockers": ["raw_catalog_request_blocked"],
            "privacy": {
                "local_paths_returned": False,
                "raw_xml_returned": False,
                "raw_template_names_returned": False,
                "raw_capability_labels_returned": False,
                "tokens_returned": False,
                "license_material_returned": False,
            },
        }), 400
    return jsonify(build_ai_wizard_capability_catalog(PROJECT_ROOT, persist=True))


@app.get("/api/sqx142/ai-wizard/sessions")
def api_sqx142_ai_wizard_sessions_list():
    error = _require_sqx142_local_operator(AI_WIZARD_AI2_VERSION)
    if error:
        return error
    return jsonify(list_ai_wizard_sessions(PROJECT_ROOT, limit=request.args.get("limit") or 20))


@app.post("/api/sqx142/ai-wizard/sessions")
def api_sqx142_ai_wizard_sessions_create():
    error = _require_sqx142_local_operator(AI_WIZARD_AI2_VERSION)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        payload = {}
    if any(key in payload for key in ("path", "output", "dbPath", "sqxRoot", "fileName")):
        return jsonify({
            "ok": False,
            "version": AI_WIZARD_AI2_VERSION,
            "error": "client_path_fields_blocked",
            "blockers": ["client_path_fields_blocked"],
            "privacy": {"local_paths_returned": False, "tokens_returned": False},
        }), 400
    report = create_ai_wizard_session(PROJECT_ROOT, payload)
    return jsonify(report), (201 if report.get("ok") else 400)


@app.get("/api/sqx142/ai-wizard/sessions/<session_id>")
def api_sqx142_ai_wizard_session_get(session_id: str):
    error = _require_sqx142_local_operator(AI_WIZARD_AI2_VERSION)
    if error:
        return error
    report = get_ai_wizard_session(PROJECT_ROOT, session_id)
    return jsonify(report), (200 if report.get("ok") else 404)


@app.post("/api/sqx142/ai-wizard/sessions/<session_id>/messages")
def api_sqx142_ai_wizard_session_messages(session_id: str):
    error = _require_sqx142_local_operator(AI_WIZARD_AI2_VERSION)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        payload = {}
    report = add_ai_wizard_message(PROJECT_ROOT, session_id, payload)
    status_code = 200 if report.get("ok") else (404 if report.get("error") == "session_not_found" else 400)
    return jsonify(report), status_code


@app.patch("/api/sqx142/ai-wizard/sessions/<session_id>/spec")
def api_sqx142_ai_wizard_session_spec(session_id: str):
    error = _require_sqx142_local_operator(AI_WIZARD_AI2_VERSION)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        payload = {}
    report = patch_ai_wizard_session_spec(PROJECT_ROOT, session_id, payload)
    status_code = 200 if report.get("ok") else (404 if report.get("error") == "session_not_found" else 400)
    return jsonify(report), status_code


@app.post("/api/sqx142/ai-wizard/sessions/<session_id>/drafts")
def api_sqx142_ai_wizard_session_drafts(session_id: str):
    error = _require_sqx142_local_operator(AI_WIZARD_AI2_VERSION)
    if error:
        return error
    report = create_ai_wizard_session_draft(PROJECT_ROOT, session_id)
    status_code = 200 if report.get("ok") else (404 if report.get("error") == "session_not_found" else 400)
    return jsonify(report), status_code


@app.get("/api/sqx142/ai-wizard/drafts/<draft_id>/download")
def api_sqx142_ai_wizard_draft_id_download(draft_id: str):
    error = _require_sqx142_local_operator(AI_WIZARD_AI2_VERSION)
    if error:
        return error
    path = resolve_ai_wizard_draft_download(PROJECT_ROOT, draft_id)
    if not path:
        return jsonify({
            "ok": False,
            "version": AI_WIZARD_AI2_VERSION,
            "error": "draft_not_found",
            "privacy": {"local_paths_returned": False, "tokens_returned": False},
        }), 404
    return send_file(path, as_attachment=True, download_name=path.name, mimetype="application/octet-stream")


@app.post("/api/sqx142/correlation-filter/external")
def api_sqx142_correlation_filter_external():
    error = _require_sqx142_local_operator(CORRELATION_FILTER_EXTERNAL_VERSION)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    source_payload = (
        payload.get("rows") or payload.get("portfolioLab") or payload.get("csv") or payload
        if isinstance(payload, dict)
        else payload
    )
    report = build_correlation_filter_report(
        source_payload,
        settings=payload.get("settings") if isinstance(payload, dict) else None,
    )
    if isinstance(payload, dict) and payload.get("includeCsvExport"):
        report["csvExport"] = export_correlation_filter_csv(report)
    if isinstance(payload, dict) and payload.get("includeSqxTagCsv"):
        report["sqxTagCsv"] = export_correlation_filter_sqx_tag_csv(report)
    return jsonify(report)


@app.post("/api/sqx142/portfolio-correlation/stability-audit")
def api_sqx142_portfolio_correlation_stability_audit():
    error = _require_sqx142_local_operator(PORTFOLIO_CORRELATION_STABILITY_VERSION)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        payload = {"csv": payload}
    report = build_portfolio_correlation_stability_report(
        payload,
        payload.get("settings") if isinstance(payload.get("settings"), dict) else None,
        decision_domain="capa2_portfolio_selection",
    )
    if payload.get("includeCsvExport"):
        report["csvExport"] = export_portfolio_correlation_stability_csv(report)
    return jsonify(report)


@app.post("/api/sqx142/capa1-c2-correlation/stability-audit")
def api_sqx142_capa1_c2_correlation_stability_audit():
    error = _require_sqx142_local_operator(CAPA1_C2_CORRELATION_SELECTION_VERSION)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        payload = {"csv": payload}
    report = build_capa1_c2_correlation_selection_report(
        payload,
        payload.get("settings") if isinstance(payload.get("settings"), dict) else None,
    )
    if payload.get("includeCsvExport"):
        report["csvExport"] = export_portfolio_correlation_stability_csv(report)
    return jsonify(report)


@app.post("/api/sqx142/capa1-c2-corr1/registered-decision")
@app.post("/api/sqx142/portfolio-corr1/registered-decision")
def api_sqx142_portfolio_corr1_registered_decision():
    error = _require_sqx142_local_operator(SQX142_PORTFOLIO_CORR1_REGISTERED_DECISION_VERSION)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        payload = {}
    action = str(payload.get("action") or "status").strip().lower()
    if action not in {"status", "analyze"}:
        return jsonify({
            "ok": False,
            "version": SQX142_PORTFOLIO_CORR1_REGISTERED_DECISION_VERSION,
            "error": "invalid_action",
            "privacy": {"local_paths_returned": False},
        }), 400
    project_key = str(payload.get("projectKey") or payload.get("projectName") or "").strip()
    if not project_key or any(part in project_key for part in ("..", "/", "\\")):
        return jsonify({
            "ok": False,
            "version": SQX142_PORTFOLIO_CORR1_REGISTERED_DECISION_VERSION,
            "error": "project_key_required",
            "privacy": {"local_paths_returned": False},
        }), 400
    user_projects = (SQX142_DEFAULT_ROOT / "user" / "projects").resolve()
    sqx_project_dir = (user_projects / project_key).resolve()
    try:
        sqx_project_dir.relative_to(user_projects)
    except ValueError:
        return jsonify({
            "ok": False,
            "version": SQX142_PORTFOLIO_CORR1_REGISTERED_DECISION_VERSION,
            "error": "project_dir_outside_sqx142_user_projects",
            "privacy": {"local_paths_returned": False},
        }), 400
    settings = payload.get("settings") if isinstance(payload.get("settings"), dict) else {}
    def setting_number(key: str, fallback: float) -> float:
        try:
            return float(settings.get(key, fallback))
        except (TypeError, ValueError):
            return fallback
    args = argparse.Namespace(
        action=action,
        sqx_root=str(SQX142_DEFAULT_ROOT),
        project_key=project_key,
        databank=str(payload.get("databank") or "SQX EDGE CORR1 TAGGED"),
        db=str(PROJECT_ROOT / SQX142_MINING_REGISTRY_DEFAULT_DB),
        max_is_correlation=setting_number("maxIsCorrelation", 0.50),
        max_oos3_correlation=setting_number("maxOos3Correlation", 0.60),
        warn_oos3_correlation=setting_number("warnOos3Correlation", 0.45),
        max_correlation_drift=setting_number("maxCorrelationDrift", 0.25),
        min_comparable_points=int(setting_number("minComparablePoints", 12)),
        max_winners=int(setting_number("maxWinners", 12)),
        skip_process_guard=False,
    )
    try:
        if action == "analyze":
            report = analyze_sqx142_portfolio_corr1_registered_decision(args)
        else:
            report = build_sqx142_portfolio_corr1_registered_decision_status(
                sqx_project_dir,
                args.databank,
                PROJECT_ROOT / SQX142_MINING_REGISTRY_DEFAULT_DB,
                project_key,
                SQX142_DEFAULT_ROOT,
            )
    except Exception as exc:
        return jsonify({
            "ok": False,
            "version": SQX142_PORTFOLIO_CORR1_REGISTERED_DECISION_VERSION,
            "action": action,
            "error": type(exc).__name__,
            "message": str(exc)[:240],
            "privacy": {"local_paths_returned": False},
        }), 400
    return jsonify(report)


@app.post("/api/sqx142/monte-carlo/benchmarks")
def api_sqx142_monte_carlo_benchmarks():
    error = _require_sqx142_local_operator(MONTE_CARLO_BENCHMARKS_VERSION)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    report = build_monte_carlo_benchmark_report(
        payload.get("rows") or payload.get("portfolioLab") or payload.get("csv") or payload,
        settings=payload.get("settings") if isinstance(payload, dict) else None,
    )
    if isinstance(payload, dict) and payload.get("includeCsvExport"):
        report["csvExport"] = export_monte_carlo_benchmark_csv(report)
    return jsonify(report)


@app.post("/api/sqx142/mt5-data-intake/probe")
def api_sqx142_mt5_data_intake_probe():
    error = _require_sqx142_local_operator(MT5_DATA_INTAKE_PROBE_VERSION)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    report = build_mt5_data_intake_probe_report(
        payload,
        settings=payload.get("settings") if isinstance(payload, dict) else None,
    )
    if isinstance(payload, dict) and payload.get("includeCsvExport"):
        report["csvExport"] = export_mt5_data_intake_probe_csv(report)
    return jsonify(report)


@app.post("/api/sqx142/migration/copy-only-checklist")
def api_sqx142_copy_only_migration_checklist():
    error = _require_sqx142_local_operator(COPY_ONLY_MIGRATION_CHECKLIST_VERSION)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    report = build_copy_only_migration_checklist(payload)
    if isinstance(payload, dict) and payload.get("includeCsvExport"):
        report["csvExport"] = export_copy_only_migration_checklist_csv(report)
    return jsonify(report)


@app.get("/api/sqx142/mining-registry/funnel")
def api_sqx142_mining_registry_funnel():
    error = _require_sqx142_local_operator(SQX142_MINING_REGISTRY_VERSION)
    if error:
        return error
    db_path = PROJECT_ROOT / SQX142_MINING_REGISTRY_DEFAULT_DB
    project_key = str(request.args.get("projectKey") or "").strip()
    run_key = str(request.args.get("runKey") or "").strip()
    return jsonify(build_sqx142_mining_registry_funnel(db_path, project_key=project_key, run_key=run_key))


@app.post("/api/sqx142/mining-registry/scan-project")
def api_sqx142_mining_registry_scan_project():
    error = _require_sqx142_local_operator(SQX142_MINING_REGISTRY_VERSION)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        payload = {}
    project_key = str(payload.get("projectKey") or payload.get("projectName") or "").strip()
    if not project_key or any(part in project_key for part in ("..", "/", "\\")):
        return jsonify({
            "ok": False,
            "version": SQX142_MINING_REGISTRY_VERSION,
            "error": "project_key_required",
            "privacy": {"local_paths_returned": False},
        }), 400
    user_projects = (SQX142_DEFAULT_ROOT / "user" / "projects").resolve()
    project_dir = (user_projects / project_key).resolve()
    try:
        project_dir.relative_to(user_projects)
    except ValueError:
        return jsonify({
            "ok": False,
            "version": SQX142_MINING_REGISTRY_VERSION,
            "error": "project_dir_outside_sqx142_user_projects",
            "privacy": {"local_paths_returned": False},
        }), 400
    db_path = PROJECT_ROOT / SQX142_MINING_REGISTRY_DEFAULT_DB
    try:
        max_sqx_parse = int(payload.get("maxSqxParse") or 300)
    except (TypeError, ValueError):
        max_sqx_parse = 300
    args = argparse.Namespace(
        action="scan-project",
        db=str(db_path),
        run_key=str(payload.get("runKey") or ""),
        project_key=project_key,
        project_dir=str(project_dir),
        max_sqx_parse=max_sqx_parse,
        source_type="sqx_local_project_scan",
        project_name=str(payload.get("projectName") or project_key),
        sqx_project_name=str(payload.get("sqxProjectName") or project_key),
        asset=str(payload.get("asset") or "unknown"),
        symbol=str(payload.get("symbol") or "unknown"),
        timeframe=str(payload.get("timeframe") or "unknown"),
        layer=str(payload.get("layer") or "unknown"),
        blocksetting_family=str(payload.get("blocksettingFamily") or "unknown"),
        direction=str(payload.get("direction") or "unknown"),
        databank=str(payload.get("databank") or "Foward"),
        sqx_profile=str(payload.get("sqxProfile") or "SQX Edge / Darwinex"),
        operator_note=str(payload.get("operatorNote") or "ui:mining-registry-visual-funnel"),
    )
    try:
        scan_report = scan_sqx142_mining_registry_project(args)
    except SystemExit as exc:
        error_text = str(exc).split(":", 1)[0] or "scan_project_failed"
        return jsonify({
            "ok": False,
            "version": SQX142_MINING_REGISTRY_VERSION,
            "error": error_text,
            "privacy": {"local_paths_returned": False},
            "guards": {
                "read_only_sqx_project": True,
                "sqx_data_db_written": False,
                "sqx_jars_patched": False,
                "sqx_runtime_started": False,
            },
        }), 400
    funnel = build_sqx142_mining_registry_funnel(db_path, project_key=project_key)
    return jsonify({
        "ok": True,
        "version": SQX142_MINING_REGISTRY_VERSION,
        "action": "scan-project-and-funnel",
        "scan": scan_report,
        "funnel": funnel,
        "privacy": {"local_paths_returned": False},
        "guards": scan_report.get("guards", {}),
    })


@app.post("/api/sqx142/capa1-c2-corr2/local-project")
@app.post("/api/sqx142/portfolio-corr2/local-project")
def api_sqx142_portfolio_corr2_local_project():
    error = _require_sqx142_local_operator(SQX142_CAPA1_C2_CORR2_VERSION)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        payload = {}
    action = str(payload.get("action") or "status").strip().lower()
    if action not in {"status", "plan", "apply", "rollback", "record"}:
        return jsonify({
            "ok": False,
            "version": SQX142_CAPA1_C2_CORR2_VERSION,
            "error": "invalid_action",
            "privacy": {"local_paths_returned": False},
        }), 400
    project_key = str(payload.get("projectKey") or payload.get("projectName") or "").strip()
    if not project_key or any(part in project_key for part in ("..", "/", "\\")):
        return jsonify({
            "ok": False,
            "version": SQX142_CAPA1_C2_CORR2_VERSION,
            "error": "project_key_required",
            "privacy": {"local_paths_returned": False},
        }), 400
    args = argparse.Namespace(
        action=action,
        sqx_root=str(SQX142_DEFAULT_ROOT),
        project_key=project_key,
        db=str(PROJECT_ROOT / SQX142_MINING_REGISTRY_DEFAULT_DB),
        backup_id=str(payload.get("backupId") or ""),
        skip_process_guard=False,
    )
    try:
        if action == "plan":
            report = build_sqx142_portfolio_corr2_plan(args)
        elif action == "apply":
            report = apply_sqx142_portfolio_corr2_integration(args)
        elif action == "rollback":
            report = rollback_sqx142_portfolio_corr2_integration(args)
        elif action == "record":
            report = record_sqx142_portfolio_corr2_status(args)
        else:
            report = build_sqx142_portfolio_corr2_status(args)
    except Exception as exc:
        return jsonify({
            "ok": False,
            "version": SQX142_CAPA1_C2_CORR2_VERSION,
            "action": action,
            "error": type(exc).__name__,
            "message": str(exc)[:240],
            "privacy": {"local_paths_returned": False},
        }), 400
    return jsonify(report)


@app.get("/api/agent/capabilities")
def api_agent_capabilities():
    context, error = _agent_access_context()
    if error:
        return error
    actions = _agent_actions_for_context(context)
    return jsonify({
        "ok": True,
        "version": LOCAL_AI_AGENT_VERSION,
        "capabilities": [action.public() for action in actions.values()],
        "access": {
            "scope": context.get("scope"),
            "remote": bool(context.get("remote")),
            "capabilityMode": context.get("capabilityMode"),
        },
        "privacy": {"local_paths_returned": False, "prompt_persisted": False},
    })


@app.post("/api/agent/plan")
def api_agent_plan():
    context, error = _agent_access_context()
    if error:
        return error
    data = request.get_json(silent=True) or {}
    return jsonify(_agent_plan_with_llm(data, actions=_agent_actions_for_context(context), context=context))


@app.post("/api/agent/confirm")
def api_agent_confirm():
    context, error = _agent_access_context()
    if error:
        return error
    data = request.get_json(silent=True) or {}
    actions = _agent_actions_for_context(context)
    action = actions.get(str(data.get("actionId") or ""))
    if not action:
        return jsonify({"ok": False, "version": LOCAL_AI_AGENT_VERSION, "error": "agent_action_unknown"}), 404
    return jsonify(create_confirmation(action, data.get("arguments") if isinstance(data.get("arguments"), dict) else {}))


@app.post("/api/agent/execute")
def api_agent_execute():
    context, error = _agent_access_context()
    if error:
        return error
    data = request.get_json(silent=True) or {}
    actions = _agent_actions_for_context(context)
    action = actions.get(str(data.get("actionId") or ""))
    token = str(data.get("confirmationToken") or "")
    confirmed = False
    if action and action.requires_confirmation:
        confirmed, reason = consume_confirmation(token, action.id)
        if not confirmed:
            return jsonify({"ok": False, "version": LOCAL_AI_AGENT_VERSION, "error": reason}), 403
    allowed, reason = is_action_allowed(action, confirmed=confirmed)
    if not allowed:
        return jsonify({"ok": False, "version": LOCAL_AI_AGENT_VERSION, "error": reason}), 403
    result = execute_action(action, arguments=data.get("arguments") if isinstance(data.get("arguments"), dict) else {}, project_root=PROJECT_ROOT)
    _record_agent_action(action.id, result)
    return jsonify(result)


@app.post("/api/agent/translate-source-code")
def api_agent_translate_source_code():
    _context, error = _agent_access_context()
    if error:
        return error
    data = request.get_json(silent=True) or {}
    result, status = _agent_translate_source_code(data)
    return jsonify(result), status


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


@app.get("/api/sqx-readiness/manifest")
def api_sqx_readiness_manifest():
    """Return the public-safe SQX readiness contract used by the checker and dashboard."""
    return jsonify(summarize_manifest_for_public())


@app.get("/api/sqx-readiness/status")
def api_sqx_readiness_status():
    """Return local or workspace-scoped SQX readiness state without exposing local paths."""
    workspace_context, remote_error = _readiness_workspace_for_request(purpose="sqx_readiness_status", create=True)
    if remote_error:
        return remote_error
    return jsonify(read_readiness_status(workspace_context))


@app.post("/api/sqx-readiness/report")
def api_sqx_readiness_report():
    """Import the JSON report generated by the portable checker."""
    workspace_context, remote_error = _readiness_workspace_for_request(purpose="sqx_readiness_report", create=True)
    if remote_error:
        return remote_error
    data = request.get_json(silent=True) or {}
    report = data.get("report") if isinstance(data.get("report"), dict) else data
    status = evaluate_readiness_report(report)
    saved = write_readiness_status(status, workspace_context, source="checker_report")
    return jsonify(saved), 200 if saved.get("ok") else 400


@app.post("/api/sqx-readiness/status")
def api_sqx_readiness_status_update():
    """Persist manual checklist updates for the current operator or remote workspace."""
    workspace_context, remote_error = _readiness_workspace_for_request(purpose="sqx_readiness_status_update", create=True)
    if remote_error:
        return remote_error
    data = request.get_json(silent=True) or {}
    checks = data.get("checks") if isinstance(data.get("checks"), dict) else data
    status = update_manual_status(checks, workspace_context)
    return jsonify(status), 200 if status.get("ok") else 400


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
               "asset_aliases", "target_profile", "target_profile_custom", "sqx_host_profile"}
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


def _output_dir_for_request(*, purpose: str, create: bool = True) -> tuple[Path | None, dict | None, tuple | None]:
    cfg = load_config()
    workspace_context, remote_error = _active_remote_workspace_for_request(purpose=purpose, create=create)
    if remote_error:
        return None, None, remote_error
    if workspace_context:
        return workspace_outputs_dir(workspace_context), workspace_context, None
    return Path(resolve_output_dir(cfg)), None, None


def _safe_output_filename(raw_name: str) -> str:
    name = Path(str(raw_name or "")).name.strip()
    if not name or name != str(raw_name or "").strip():
        raise ValueError("invalid output filename")
    if not name.lower().endswith(".cfx"):
        raise ValueError("only .cfx output files can be accessed")
    return name


def _output_file_path(output_dir: Path, raw_name: str) -> Path:
    name = _safe_output_filename(raw_name)
    path = (output_dir / name).resolve(strict=False)
    output_root = output_dir.resolve(strict=False)
    try:
        path.relative_to(output_root)
    except ValueError as exc:
        raise ValueError("output file outside output directory") from exc
    return path


@app.get("/api/output/download/<path:filename>")
def download_output_file(filename: str):
    output_dir, workspace_context, remote_error = _output_dir_for_request(
        purpose="project_generator_output_download",
        create=False,
    )
    if remote_error:
        return remote_error
    try:
        path = _output_file_path(output_dir or Path(), filename)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    if not path.is_file():
        return jsonify({"ok": False, "error": "output file not found"}), 404
    if workspace_context:
        append_workspace_audit_event(workspace_context, {
            "type": "remote_workspace_output_downloaded",
            "action": "project_generator_output_download",
            "filename": path.name,
            "version": "remote-workspace-output-download-v1",
        })
    return send_file(path, as_attachment=True, download_name=path.name, mimetype="application/octet-stream")


@app.get("/api/output/download-all")
def download_all_outputs():
    output_dir, workspace_context, remote_error = _output_dir_for_request(
        purpose="project_generator_output_download_all",
        create=False,
    )
    if remote_error:
        return remote_error
    output_dir = output_dir or Path()
    files = sorted(output_dir.glob("*.cfx"), key=lambda item: item.stat().st_mtime, reverse=True)
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, arcname=path.name)
    buffer.seek(0)
    if workspace_context:
        append_workspace_audit_event(workspace_context, {
            "type": "remote_workspace_outputs_downloaded",
            "action": "project_generator_output_download_all",
            "fileCount": len(files),
            "version": "remote-workspace-output-download-v1",
        })
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"sqx-edge-suite-cfx-output-{stamp}.zip",
        mimetype="application/zip",
    )


@app.post("/api/output/download-selected")
def download_selected_outputs():
    data = request.get_json(silent=True) or {}
    raw_files = data.get("files") or []
    if not isinstance(raw_files, list) or not raw_files:
        return jsonify({"ok": False, "error": "no output files selected"}), 400
    output_dir, workspace_context, remote_error = _output_dir_for_request(
        purpose="project_generator_output_download_selected",
        create=False,
    )
    if remote_error:
        return remote_error
    selected_paths: list[Path] = []
    for raw_name in raw_files:
        try:
            path = _output_file_path(output_dir or Path(), str(raw_name))
        except ValueError as exc:
            return jsonify({"ok": False, "error": str(exc), "filename": str(raw_name)}), 400
        if not path.is_file():
            return jsonify({"ok": False, "error": "output file not found", "filename": path.name}), 404
        selected_paths.append(path)
    if len(selected_paths) == 1:
        path = selected_paths[0]
        if workspace_context:
            append_workspace_audit_event(workspace_context, {
                "type": "remote_workspace_output_downloaded",
                "action": "project_generator_output_download_selected",
                "filename": path.name,
                "version": "remote-workspace-output-download-v1",
            })
        return send_file(path, as_attachment=True, download_name=path.name, mimetype="application/octet-stream")
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in selected_paths:
            archive.write(path, arcname=path.name)
    buffer.seek(0)
    if workspace_context:
        append_workspace_audit_event(workspace_context, {
            "type": "remote_workspace_outputs_downloaded",
            "action": "project_generator_output_download_selected",
            "fileCount": len(selected_paths),
            "version": "remote-workspace-output-download-v1",
        })
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"sqx-edge-suite-cfx-selected-{stamp}.zip",
        mimetype="application/zip",
    )


@app.post("/api/output/delete")
def delete_output_files():
    data = request.get_json(silent=True) or {}
    raw_files = data.get("files") or []
    if not isinstance(raw_files, list) or not raw_files:
        return jsonify({"ok": False, "error": "no output files selected"}), 400
    output_dir, workspace_context, remote_error = _output_dir_for_request(
        purpose="project_generator_output_delete",
        create=False,
    )
    if remote_error:
        return remote_error
    deleted: list[str] = []
    missing: list[str] = []
    errors: list[dict[str, str]] = []
    for raw_name in raw_files:
        try:
            path = _output_file_path(output_dir or Path(), str(raw_name))
        except ValueError as exc:
            errors.append({"name": str(raw_name), "error": str(exc)})
            continue
        if not path.is_file():
            missing.append(path.name)
            continue
        try:
            path.unlink()
            deleted.append(path.name)
        except OSError as exc:
            errors.append({"name": path.name, "error": str(exc)})
    if workspace_context:
        append_workspace_audit_event(workspace_context, {
            "type": "remote_workspace_outputs_deleted",
            "action": "project_generator_output_delete",
            "deletedCount": len(deleted),
            "missingCount": len(missing),
            "errorCount": len(errors),
            "filenames": deleted,
            "version": "remote-workspace-output-delete-v1",
        })
    return jsonify({
        "ok": not errors,
        "deleted": deleted,
        "missing": missing,
        "errors": errors,
        "scope": "remote_workspace" if workspace_context else "local_operator",
        "privacy": {"local_paths_returned": False} if workspace_context else {"local_paths_returned": True},
    })


@app.post("/api/generate")
def generate_one():
    locked = require_feature("project_generator.generate")
    if locked:
        return locked
    readiness_locked = require_sqx_readiness("project_generator.generate")
    if readiness_locked:
        return readiness_locked
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
    target_profile = _target_profile_payload(data, cfg)
    resolved_target = normalize_target_profile(target_profile, postfix)
    try:
        out_path = generate_project(
            mining, template_path=template, output_dir=output, capa=capa,
            sqx_db_path=db_path, broker_postfix=postfix, alias_override=aliases,
            blocksetting_capa2=blocksetting_capa2,
            target_profile=target_profile,
        )
        # Mostrar al cliente qué fuente de costos se usó
        costs = resolve_costs(mining, db_path, postfix, alias_override=aliases, target_profile=resolved_target)
        bs_entry = resolve_blocksetting_entry(mining.bs, timeframe=mining.tf, capa=capa, blocksetting_capa2=blocksetting_capa2)
        payload = {
            "ok": True, "mining": mining.num, "capa": capa,
            "output_path": out_path, "filename": os.path.basename(out_path),
            "costs_source": costs["source"], "symbol": costs["symbol"],
            "spread": costs["spread"], "swap_long": costs["swap_long"], "swap_short": costs["swap_short"],
            "data_available": costs.get("data_available"), "data_rows": costs.get("data_rows"),
            "blocksetting": blocksetting_trace(bs_entry),
            "target_profile": public_target_profile(resolved_target),
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


@app.post("/api/generate-pair")
def generate_pair():
    locked = require_feature("project_generator.generate")
    if locked:
        return locked
    readiness_locked = require_sqx_readiness("project_generator.generate")
    if readiness_locked:
        return readiness_locked
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        data = {}
    try:
        mining, project_name = build_custom_mining(_pair_generation_input(data))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    cfg = load_config()
    output, workspace_context, remote_error = _resolve_generation_output(
        data,
        cfg,
        purpose="project_generator_generate_pair",
    )
    if remote_error:
        return remote_error

    db_path = cfg.get("sqx_data_db") or None
    postfix = cfg.get("darwinex_suffix") or DEFAULT_BROKER_POSTFIX
    aliases = cfg.get("asset_aliases") or {}
    target_profile = _target_profile_payload(data, cfg)
    resolved_target = normalize_target_profile(target_profile, postfix)
    blocksetting_capa2 = (
        data.get("blocksetting_capa2")
        or data.get("capa2_blocksetting")
        or data.get("capa2_bs")
        or data.get("bs_capa2")
    )

    results: dict[str, dict] = {}
    files: list[dict] = []
    for capa in (1, 2):
        key = f"capa{capa}"
        template = resolve_pair_request_template(data, cfg, capa)
        try:
            if not os.path.isfile(template):
                raise FileNotFoundError(f"template not found: {template}")
            out_path = generate_project(
                mining,
                template_path=template,
                output_dir=output,
                capa=capa,
                sqx_db_path=db_path,
                broker_postfix=postfix,
                alias_override=aliases,
                project_name=project_name,
                blocksetting_capa2=blocksetting_capa2,
                target_profile=target_profile,
            )
            costs = resolve_costs(mining, db_path, postfix, alias_override=aliases, target_profile=resolved_target)
            bs_entry = resolve_blocksetting_entry(
                mining.bs,
                timeframe=mining.tf,
                capa=capa,
                blocksetting_capa2=blocksetting_capa2,
            )
            result_item = {
                "ok": True,
                "custom": True,
                "project_name": project_name,
                "asset": mining.asset,
                "tf": mining.tf,
                "bs": mining.bs,
                "dir": mining.dir,
                "capa": capa,
                "output_path": out_path,
                "filename": os.path.basename(out_path),
                "costs_source": costs["source"],
                "symbol": costs["symbol"],
                "spread": costs["spread"],
                "swap_long": costs["swap_long"],
                "swap_short": costs["swap_short"],
                "data_available": costs.get("data_available"),
                "data_rows": costs.get("data_rows"),
                "blocksetting": blocksetting_trace(bs_entry),
                "target_profile": public_target_profile(resolved_target),
            }
            if workspace_context:
                record_workspace_output_generated(
                    workspace_context,
                    endpoint="generate-pair",
                    filename=os.path.basename(out_path),
                    capa=capa,
                    mining=0,
                )
                result_item.update(output_response_fields(workspace_context, out_path))
            results[key] = result_item
            files.append(_generated_file_entry(result_item))
        except Exception as e:
            results[key] = {
                "ok": False,
                "custom": True,
                "project_name": project_name,
                "asset": mining.asset,
                "tf": mining.tf,
                "bs": mining.bs,
                "dir": mining.dir,
                "capa": capa,
                "error": _generation_error_message(e, remote=bool(workspace_context)),
                "target_profile": public_target_profile(resolved_target),
            }

    ok_count = sum(1 for item in results.values() if item.get("ok"))
    fail_count = 2 - ok_count
    payload = {
        "ok": fail_count == 0,
        "custom": True,
        "operation": "generate_pair",
        "project_name": project_name,
        "asset": mining.asset,
        "tf": mining.tf,
        "dir": mining.dir,
        "ok_count": ok_count,
        "fail_count": fail_count,
        "target_profile": public_target_profile(resolved_target),
        "results": results,
        "files": files,
    }
    if workspace_context:
        append_workspace_audit_event(workspace_context, {
            "type": "remote_workspace_output_pair_generated",
            "action": "project_generator_generate_pair",
            "asset": mining.asset,
            "timeframe": mining.tf,
            "direction": mining.dir,
            "ok": fail_count == 0,
            "okCount": ok_count,
            "failCount": fail_count,
            "filenames": [item.get("name") for item in files],
            "version": "remote-workspace-output-v1",
        })
        payload["output"] = {
            "version": "remote-workspace-output-v1",
            "scope": "remote_workspace",
            "output_dir": "workspace://outputs",
            "workspace": public_workspace_context(workspace_context),
        }
        payload["privacy"] = {"local_paths_returned": False}
    return jsonify(payload)


@app.post("/api/generate-custom")
def generate_custom():
    locked = require_feature("project_generator.generate")
    if locked:
        return locked
    readiness_locked = require_sqx_readiness("project_generator.generate")
    if readiness_locked:
        return readiness_locked
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
    target_profile = _target_profile_payload(data, cfg)
    resolved_target = normalize_target_profile(target_profile, postfix)
    try:
        out_path = generate_project(
            mining, template_path=template, output_dir=output, capa=capa,
            sqx_db_path=db_path, broker_postfix=postfix, alias_override=aliases,
            project_name=project_name,
            blocksetting_capa2=blocksetting_capa2,
            target_profile=target_profile,
        )
        costs = resolve_costs(mining, db_path, postfix, alias_override=aliases, target_profile=resolved_target)
        bs_entry = resolve_blocksetting_entry(mining.bs, timeframe=mining.tf, capa=capa, blocksetting_capa2=blocksetting_capa2)
        payload = {
            "ok": True, "custom": True, "project_name": project_name,
            "asset": mining.asset, "tf": mining.tf, "bs": mining.bs, "dir": mining.dir,
            "capa": capa, "output_path": out_path, "filename": os.path.basename(out_path),
            "costs_source": costs["source"], "symbol": costs["symbol"],
            "spread": costs["spread"], "swap_long": costs["swap_long"], "swap_short": costs["swap_short"],
            "data_available": costs.get("data_available"), "data_rows": costs.get("data_rows"),
            "blocksetting": blocksetting_trace(bs_entry),
            "target_profile": public_target_profile(resolved_target),
        }
        if _truthy_request_value(data.get("visual_guide_pdf", data.get("visualGuidePdf"))):
            try:
                payload["visual_guide_pdf"] = render_custom_project_visual_guide_pdf(project_name, out_path)
            except Exception as pdf_error:
                payload["visual_guide_pdf"] = {
                    "ok": False,
                    "error": redact_text(f"{type(pdf_error).__name__}: {pdf_error}"),
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
    readiness_locked = require_sqx_readiness("project_generator.generate")
    if readiness_locked:
        return readiness_locked
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
    target_profile = _target_profile_payload(data, cfg)
    resolved_target = normalize_target_profile(target_profile, postfix)
    results = []
    for m in all_minings():
        try:
            out_path = generate_project(
                m, template_path=template, output_dir=output, capa=capa,
                sqx_db_path=db_path, broker_postfix=postfix, alias_override=aliases,
                blocksetting_capa2=blocksetting_capa2,
                target_profile=target_profile,
            )
            costs = resolve_costs(m, db_path, postfix, alias_override=aliases, target_profile=resolved_target)
            bs_entry = resolve_blocksetting_entry(m.bs, timeframe=m.tf, capa=capa, blocksetting_capa2=blocksetting_capa2)
            result_item = {
                "mining": m.num, "ok": True,
                "filename": os.path.basename(out_path),
                "costs_source": costs["source"],
                "blocksetting": blocksetting_trace(bs_entry),
                "target_profile": public_target_profile(resolved_target),
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
    readiness_locked = require_sqx_readiness("strategy_cleaner.apply")
    if readiness_locked:
        return readiness_locked
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
    agent_status = warmup_local_ai_agent()
    agent_auto = agent_status.get("autoStart") if isinstance(agent_status.get("autoStart"), dict) else {}
    print(f"  Local AI: {'available' if agent_status.get('available') else 'pending'} ({agent_status.get('model') or 'ollama'})")
    if agent_auto.get("attempted"):
        print(f"  Local AI autostart: {agent_auto.get('reason') or 'attempted'}")
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
