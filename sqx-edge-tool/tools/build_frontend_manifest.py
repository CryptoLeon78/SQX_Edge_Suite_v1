from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "sqx-edge-tool" / "config"
OUT_PATH = ROOT / "js" / "manifest-data.js"


def read_json(name: str) -> dict:
    return json.loads((CONFIG_DIR / name).read_text(encoding="utf-8-sig"))


def main() -> None:
    manifest = {
        "version": 1,
        "ui": read_json("ui_manifest.json"),
        "plan": read_json("plan.json"),
        "assets": read_json("assets.json"),
        "strategies": read_json("strategies.json"),
    }
    OUT_PATH.write_text(
        "window.SQX_MANIFEST = " + json.dumps(manifest, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
