from __future__ import annotations

import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[3]
TOOL_ROOT = SCRIPT_PATH.parents[1]
CONFIG_DIR = TOOL_ROOT / "config"
OUT_PATH = PROJECT_ROOT / "app" / "js" / "manifest-data.js"


def read_json(name: str) -> dict:
    return json.loads((CONFIG_DIR / name).read_text(encoding="utf-8-sig"))


def main() -> None:
    manifest = {
        "version": 1,
        "ui": read_json("ui_manifest.json"),
        "product": read_json("product_manifest.json"),
        "plan": read_json("plan.json"),
        "assets": read_json("assets.json"),
        "strategies": read_json("strategies.json"),
        "blocksettings": read_json("blocksettings_manifest.json"),
    }
    OUT_PATH.write_text(
        "window.SQX_MANIFEST = " + json.dumps(manifest, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
