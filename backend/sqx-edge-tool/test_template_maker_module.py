import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "app"
TOOL_ROOT = PROJECT_ROOT / "backend" / "sqx-edge-tool"


def read_html():
    return (APP_ROOT / "SQX_Dashboard_v6.html").read_text(encoding="utf-8-sig")


def test_template_maker_files_exist():
    assert (APP_ROOT / "vendor" / "jszip.min.js").is_file()
    assert (APP_ROOT / "js" / "modules" / "template-maker.js").is_file()
    assert (APP_ROOT / "js" / "modules" / "template-maker-ui.js").is_file()
    assert (PROJECT_ROOT / "resources" / "template-maker-tool" / "test_capa1.csv").is_file()


def test_template_maker_scripts_are_ordered_before_home():
    scripts = re.findall(r'<script\s+src="([^"]+)"', read_html())
    assert scripts.index("vendor/jszip.min.js") < scripts.index("js/modules/template-maker.js")
    assert scripts.index("js/modules/template-maker.js") < scripts.index("js/modules/template-maker-ui.js")
    assert scripts.index("js/modules/template-maker-ui.js") < scripts.index("js/modules/home.js")
    assert "js/modules/analyzer.js" not in scripts


def test_template_maker_tab_replaces_active_analyzer_surface():
    html = read_html()
    assert 'id="tab-templatemaker"' in html
    assert 'id="tm-csv-input"' in html
    assert 'id="tm-sqx-input"' in html
    assert 'id="tab-analyzer"' not in html
    assert 'id="analyzer-file-input"' not in html
    assert 'href="css/analyzer.css"' not in html


def test_template_maker_manifest_position():
    manifest = json.loads((TOOL_ROOT / "config" / "ui_manifest.json").read_text(encoding="utf-8-sig"))
    ids = [tab["id"] for tab in manifest["tabs"]]
    assert "templatemaker" in ids
    assert ids.index("templatemaker") == ids.index("estrategias") - 1
