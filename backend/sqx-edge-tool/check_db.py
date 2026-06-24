from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from core.app_paths import app_root  # noqa: E402

ROOT = app_root()
CONFIG_PATH = ROOT / "config.json"


def configured_db_path() -> Path:
    if not CONFIG_PATH.is_file():
        raise SystemExit(f"No existe {CONFIG_PATH}. Copia config.template.json o configura la ruta desde la UI.")
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
    raw = cfg.get("sqx_data_db")
    if not raw:
        raise SystemExit("sqx_data_db no esta configurado en config.json.")
    return Path(raw)


db_path = configured_db_path()
if not db_path.is_file():
    raise SystemExit(f"data.db no existe: {db_path}")

db = sqlite3.connect(db_path)
try:
    curs = db.execute("SELECT name FROM sqlite_master WHERE type=?", ("table",))
    tables = [r[0] for r in curs.fetchall()]
    print("DB:", db_path)
    print("Tables:", tables)
finally:
    db.close()
