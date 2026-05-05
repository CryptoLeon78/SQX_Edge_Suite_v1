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
from datetime import datetime
from pathlib import Path

# Permitir ejecución directa o vía -m
ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ROOT.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, abort, jsonify, request  # type: ignore

from core import all_minings, generate_project, get_mining
from core.config_loader import load_manifest
from core.license_manager import (
    check_feature,
    clear_license_file,
    import_license_payload,
    license_status,
    load_product_manifest,
)
from core.project_generator import DEFAULT_BROKER_POSTFIX, resolve_costs
from core.sqx_db import SqxDb
from core.strategy_cleaner import (
    extract_metadata, list_sqx_directory, clean_exit_after_bars,
    institutional_name, rename_sqx, process_files,
)
from core.support_diagnostics import build_support_diagnostics

app = Flask(__name__)

VERSION = "0.2.0"
CONFIG_PATH = ROOT / "config.json"
DASHBOARD_ROOT = PROJECT_ROOT / "app"
STATE_BACKUP_DIR = PROJECT_ROOT / "analysis" / "analysis_output"
STATE_BACKUP_RETENTION = int(os.environ.get("SQX_STATE_BACKUP_RETENTION", "30"))
API_PROFILE = (load_manifest("generator_profiles.json").get("api") or {})
DEFAULT_HOST = API_PROFILE.get("defaultHost", "127.0.0.1")
DEFAULT_PORT = int(API_PROFILE.get("defaultPort", 5050))
LOCAL_CORS_ORIGINS = set(API_PROFILE.get("corsOrigins") or ["null"])
LOCAL_HTTP_ORIGIN_RE = re.compile(API_PROFILE.get("localOriginPattern", r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"))
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
LOCAL_REMOTE_ADDRS = {"127.0.0.1", "::1"}


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


@app.before_request
def enforce_local_api_boundary():
    if not _is_local_host(request.host) or not _is_local_remote(request.remote_addr):
        return jsonify({
            "ok": False,
            "error": "local_api_only",
            "message": "SQX Edge API only accepts local browser requests.",
        }), 403


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin in LOCAL_CORS_ORIGINS or (origin and LOCAL_HTTP_ORIGIN_RE.match(origin)):
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Vary"] = "Origin"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    return response


# Flask responde OPTIONS automáticamente para rutas con GET/POST registrados,
# combinado con el @app.after_request de arriba, eso es suficiente para CORS preflight.


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


def resolve_output_dir(cfg: dict) -> str:
    val = cfg.get("output_dir") or "output"
    if not os.path.isabs(val):
        val = str(ROOT / val)
    os.makedirs(val, exist_ok=True)
    return val


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
    })


@app.get("/api/license/status")
def api_license_status():
    return jsonify(license_status())


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
    template = data.get("template") or resolve_template(cfg, capa)
    output = data.get("output") or resolve_output_dir(cfg)

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
        )
        # Mostrar al cliente qué fuente de costos se usó
        costs = resolve_costs(mining, db_path, postfix, alias_override=aliases)
        return jsonify({
            "ok": True, "mining": mining.num, "capa": capa,
            "output_path": out_path, "filename": os.path.basename(out_path),
            "costs_source": costs["source"], "symbol": costs["symbol"],
            "spread": costs["spread"], "swap_long": costs["swap_long"], "swap_short": costs["swap_short"],
        })
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
    template = data.get("template") or resolve_template(cfg, capa)
    output = data.get("output") or resolve_output_dir(cfg)

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
            )
            costs = resolve_costs(m, db_path, postfix, alias_override=aliases)
            results.append({
                "mining": m.num, "ok": True,
                "filename": os.path.basename(out_path),
                "costs_source": costs["source"],
            })
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
# Guarda snapshots JSON del estado local del dashboard sin depender de la
# modularizacion JS. La UI puede consumir estos endpoints ahora o en una fase
# posterior.
def _state_backup_path(filename: str) -> Path:
    if not filename.startswith("state_backup_") or not filename.endswith(".json"):
        abort(404)
    path = (STATE_BACKUP_DIR / filename).resolve(strict=False)
    try:
        path.relative_to(STATE_BACKUP_DIR.resolve(strict=False))
    except ValueError:
        abort(403)
    return path


def _list_state_backups() -> list[dict]:
    if not STATE_BACKUP_DIR.exists():
        return []
    files = sorted(
        STATE_BACKUP_DIR.glob("state_backup_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return [
        {
            "name": p.name,
            "size_kb": round(p.stat().st_size / 1024, 1),
            "mtime": int(p.stat().st_mtime),
        }
        for p in files
        if p.is_file()
    ]


def _rotate_state_backups() -> int:
    files = sorted(
        STATE_BACKUP_DIR.glob("state_backup_*.json"),
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

    STATE_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now().isoformat(timespec="seconds")
    stamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    target = STATE_BACKUP_DIR / f"state_backup_{stamp}.json"
    payload = {
        "_meta": {
            "created_at": created_at,
            "version": VERSION,
            "keys": sorted(data.keys()),
        },
        "data": data,
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    rotated = _rotate_state_backups()
    return jsonify({
        "ok": True,
        "filename": target.name,
        "size_kb": round(target.stat().st_size / 1024, 1),
        "rotated": rotated,
    })


@app.get("/api/state/backups")
def api_state_backups():
    """Lista backups disponibles, del mas reciente al mas antiguo."""
    return jsonify({"ok": True, "backups": _list_state_backups()})


@app.get("/api/state/restore/<path:filename>")
def api_state_restore(filename: str):
    """Devuelve el contenido de un backup concreto para restaurarlo en UI."""
    path = _state_backup_path(filename)
    if not path.is_file():
        abort(404)
    return jsonify({
        "ok": True,
        "filename": filename,
        "payload": json.loads(path.read_text(encoding="utf-8")),
    })


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
