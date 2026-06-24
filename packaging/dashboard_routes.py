"""
dashboard_routes.py -- Flask routes that serve the SQX dashboard from the same
origin as the API.

Registering these routes makes GET / return the dashboard HTML and
GET /<path> serve the static files under app/, so the browser sees a single
origin for both the UI and the API.  This eliminates the file:// quirks and
the CORS cross-origin :5050 requirement.

Flask/Werkzeug gives explicit /api/<endpoint> rules priority over the
/<path:filename> catch-all, so /api/* routes are never shadowed.

The same-origin hint is delivered via a <meta name="sqx-api-base"> tag
injected into the HTML before </head>.  app-config.js:defaultApiBase()
already reads this tag (priority 3 in its resolution chain).  When the file
is opened directly via file://, the tag is absent and the JS falls back to
http://127.0.0.1:5050/api -- the existing dev workflow is unchanged.
"""
from __future__ import annotations

import re
from pathlib import Path

from flask import Flask, Response, send_from_directory

_DASHBOARD_HTML = "SQX_Dashboard_v6.html"
_META_SNIPPET = b'<meta name="sqx-api-base" content="/api">\n'
_HEAD_CLOSE_RE = re.compile(rb"(</head>)", re.IGNORECASE)


def register_dashboard_routes(flask_app: Flask, app_dir: Path) -> None:
    """Register GET / and GET /<path:filename> on flask_app to serve app_dir.

    Call once after creating the Flask app and before app.run().
    """

    @flask_app.get("/")
    def serve_dashboard():
        html = (app_dir / _DASHBOARD_HTML).read_bytes()
        # Inject same-origin apiBase hint so JS calls /api/* regardless of port.
        injected, _ = _HEAD_CLOSE_RE.subn(_META_SNIPPET + rb"\1", html, count=1)
        return Response(injected, mimetype="text/html")

    @flask_app.get("/<path:filename>")
    def serve_app_static(filename: str):
        return send_from_directory(str(app_dir), filename)
